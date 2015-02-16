"""
This script scrapes data from the Walkscore website. This may be useful since their API has
limits and getting a key can be annoyingly difficult. Please use this responsibly.

This script consumes an input file in CSV format with the following format:

    STATE, City

The STATE code must be the two-letter US code, such as:

    WA, Seattle

@author - James Malone
"""

# Imports for this script
import argparse
import re
import requests
import time

# Constant variables
BASE_URL = 'https://www.walkscore.com/%s/%s'
NULL_SCORE_VALUE = 0
REGEX_FILTERS = {
    'walkscore': '\/\/pp.walk.sc\/badge\/walk\/score\/(\d+)\.svg',
    'transitscore': '\/\/pp.walk.sc\/badge\/transit\/score\/(\d+)\.svg',
    'bikescore': '\/\/pp.walk.sc\/badge\/bike\/score\/(\d+)\.svg'
}
SLEEP_INCREMENT_SECONDS = 1


"""
Parse the score data on the walkscore page.
"""
def parse_score_data(content):
    return_data = [0,0,0]
    score_hash = dict()
    for score_type in REGEX_FILTERS.keys():
        score_data = re.search(REGEX_FILTERS[score_type], content)
        if score_data is not None:
            score_hash[score_type] = score_data.group(1)
        else:
            score_hash[score_type] = NULL_SCORE_VALUE
    return score_hash


"""
Return a well-formatted Walkscore URL
"""
def return_walkscore_url(state, city):
    return BASE_URL % (state, city.replace(' ', '_'))


"""
Main method - executes work for this script.
"""
def main():
    # Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-in", "--city_data", help="CSV city data")
    parser.add_argument("-out", "--output_file", help="Output file")
    args = parser.parse_args()
    
    with open(args.city_data) as city_file:
        with open(args.output_file, "w") as out_file:
            for line in city_file:
                
                # Parse the line and get URL
                parts = line.strip().split(',')
                print("Getting data for %s/%s" % (parts[0], parts[1]))
                city_url = return_walkscore_url(parts[0], parts[1])
                
                # Fetch the data; write to file
                r = requests.get(city_url)
                page_data = str(r.content)
                score_data = parse_score_data(page_data)
                out_file.write("%s,%s,%s,%s,%s\n" % (parts[0], parts[1], score_data['walkscore'], score_data['transitscore'], score_data['bikescore']))
                out_file.flush()
                
                # Sleep to be nice
                time.sleep(SLEEP_INCREMENT_SECONDS)

if __name__ == "__main__":
    main()