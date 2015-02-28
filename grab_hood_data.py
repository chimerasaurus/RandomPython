"""
This Python script is designed to take a list of cities, use Walkscore, and perform several calculations with
the ultimate goal of identifying the "most livable" neighborhood. Specifically, this script does the following:

1. Looks up each city individually
2. For each city, looks up every neighborhood
3. For each neighborhood, calculates the number of hoods in the proximity passed to the script
4. Calculates some summary metrics based on the network of neighborhoods

This is a messy work in progress.

This script consumes an input file in CSV format with the following format:

    STATE, City

The STATE code must be the two-letter US code, such as:

    WA, Seattle

"""

# Imports for this script
import argparse
import csv
import sys
import logging
import numpy as np
import time

# Walkscore api imports (github.com/evilsoapbox/WalkscoreApi)
import geo_utilities
import walkscoreapi

# Authorship Information
__author__ = "James Malone"
__copyright__ = "Copyright 2015, James Malone"
__license__ = "MIT"
__version__ = "1"
__maintainer__ = "James Malone
__email__ = "jamalone at gmail dot com"
__status__ = "Production"

# Constants for this script
ELEMENTS_FOR_ANALYSIS = ['bike_score', 'population', 'restaurants', 'transit_score', 'walk_score']
SLEEP_INCREMENT_SECONDS = 0.5 # Sleep between WS lookups not to overload WS


def main():
    """
    Main method for this script.
    :return: Nothing
    """
    # Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-in", "--city_data", help="CSV city data")
    parser.add_argument("-log", "--log_file", help="Log file")
    parser.add_argument("-out", "--output_file", help="Output file")
    parser.add_argument("-rng", "--hood_range", help="Range (mi) between hoods")
    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(format='%(asctime)s-%(levelname)s-%(message)s', level=logging.INFO, filename=args.log_file)
    logger = logging.getLogger('find_best_hood')
    logging.getLogger("requests").setLevel(logging.WARNING)

    # Open the city file and go!
    with open(args.city_data) as city_file:
        for line in city_file:
            # Array to hold rows for this city
            all_rows = []

            # Parse the line and get URL
            parts = line.strip().split(',')
            logger.info("Getting data for %s/%s" % (parts[0], parts[1]))

            # Get the city data
            try:
                city_data = walkscoreapi.data_for_city(parts[1], parts[0])
            except:
                logger.error("Error getting data from Walkscore, skipping")
                continue # Cannot find city data, skip

            # Ignore cities with bad data
            if city_data == None or city_data['neighborhoods'] == None:
                logger.error("City has bad data, skipping it")
                continue

            city_hoods = city_data['neighborhoods']

            # Recurse hoods to get full data
            for i in range(0,len(city_hoods)):
                hood = city_hoods[i]
                logger.info("Getting data for %s\%s\%s (%s\%s)" %
                            (parts[0], parts[1], hood['name'],str(i+1), str(len(city_hoods))))
                hood_data = walkscoreapi.data_for_neighborhood(hood['name'], parts[1], parts[0])

                # Skip hoods with bad data
                if hood_data == None:
                    logger.error("Cannot get NH data from Walkscore")
                    continue

                # Save the NH data and sleep not to overload WS
                city_hoods[i] = hood_data
                time.sleep(SLEEP_INCREMENT_SECONDS)

            # Recurse hoods again to calculate data
            city_hoods = calculate_hood_networks(city_hoods, args.hood_range)

            # Calculate metrics and write them to disk
            for i in range(0,len(city_hoods)):
                hood = city_hoods[i]
                keys_to_add = ['state', 'city', 'name', 'population', 'lng', 'lat', 'in_range', 'walk_score',
                               'transit_score', 'bike_score', 'restaurants']
                master_list = []
                for key in keys_to_add:
                    if key in hood:
                        master_list.append(hood[key])
                    else:
                        logger.info("Missing key '%s' in NH" % key)
                        master_list.append(None)

                master_list = ['None' if v is None else v for v in master_list]
                all_rows.append(master_list)
            write_to_csv(all_rows, args.output_file)


def calculate_hood_networks(hood_array, max_range):
    """
    Calculate "networks" of neighborhoods - find hoods in range of each given hood in a city given a distance.
    :param hood_array: List of neighborhoods
    :param max_range: Max range (miles) before a hood is no longer in the network
    :return: Array of hoods with new element ('in_range')
    """
    for i in range(0,len(hood_array)):
        hood = hood_array[i]
        hoods_in_range = []

        logger = logging.getLogger('find_best_hood')
        logger.info("Calculating data for %s" % (hood['name']))

        for hood_to_check in hood_array:
            if hood['name'] == hood_to_check['name']:
                continue

            try:
                dist = geo_utilities.distance_between_coordinates_mi(hood['lng'], hood['lat'],
                                                                     hood_to_check['lng'],hood_to_check['lat'])
            except:
                logger.error("No geospacial data, skipping")
                continue

            # Check if the NH is in range
            if dist <= float(max_range):
                hoods_in_range.append(hood_to_check['name'])

        hood_array[i]['in_range'] = hoods_in_range

    return hood_array


def calculate_hood_statistics(hood, city_hoods):
    """
    Calculate the statistical results for a given neighborhood (mean, max, min, stdev)
    :param hood: Neighborhood to examine
    :param city_hoods: List of all city neighborhoods and their data
    :return: Array of statistical results
    """
    # Array for results
    statistical_results = []

    # ELEMENTS_FOR_ANALYSIS
    for element in ELEMENTS_FOR_ANALYSIS:
        element_score = [int(hood[element] or 0)]
        for nearby_hood in hood['in_range']:
            related_hood = next((item for item in city_hoods if item["name"] == nearby_hood))
            element_score.append(int(related_hood[element] or 0))
            statistical_results.append(np.mean(element_score))
            statistical_results.append(max(element_score))
            statistical_results.append(min(element_score))
            statistical_results.append(np.std(element_score))

    return statistical_results

def write_to_csv(data_to_write, output_file):
    """
    Write an array of values to a csv file
    :param data_to_write: Data to write into the CSV (in an array)
    :param output_file: Output file to write
    :return: Nothing
    """
    with open(output_file, "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data_to_write)
        f.flush()

if __name__ == "__main__":
    main()