'''
This script gets all of the locations for the Seattle Pronto bike share
and dumps them out in delimited format.

v1/2014.10.09
'''

# Metadata
__author__ = 'James Malone'

# Imports
import json, requests

# STATIC VARIABLES
PRONTO_LOCATION_JSON_URL = 'http://secure.prontocycleshare.com/data2/stations.json'
DELIMITER = '\t'

# Get the data
http_response = requests.get(url=PRONTO_LOCATION_JSON_URL)
json_location_data = json.loads(http_response.text)

# Output the data
if json_location_data and 'stations' in json_location_data and json_location_data['stations'][0]:
    # Print the headers
    print(DELIMITER.join(map(str, sorted(json_location_data['stations'][0].keys()))))

    # Print the station data
    for station in json_location_data['stations']:
        keys = station.keys()
        keys.sort()
        sorted_station = map(station.get, keys)
        print(DELIMITER.join(map(str, sorted_station)))