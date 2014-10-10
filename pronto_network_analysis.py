'''
This script completes an analysis of the Seattle Pronto cycling network.
Specifically, it will compare all stations in the network to examine their distance
from one another to calculate cost, usage, distance, and other metrics.

v1.2014-10-09
'''

# Metadata
__author__ = 'james'

# Imports
import json
import pickle
import requests
import subprocess
import time

# Static variables
DATAFILE_DELIMITER = '\t'
GOOGLE_MAPS_DIRECTIONS_API_KEY = ''
MAPS_LOOKUP_DELAY = 2 # sec

# Get location data
location_dict = {}
process = subprocess.Popen(['python', 'pronto_location_grab.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
location_data = process.communicate()[0].split('\n')
location_data.pop(0)
for location in location_data:
    location_items = location.split(DATAFILE_DELIMITER)
    if len(location_items) > 1 and location_items[8] != "0.0":
        location_dict[location_items[7]] = {'name': location_items[11], 'lat': location_items[8], 'long':
            location_items[9], 'routes_to': {}}

# Determine number of possible routes
stations = location_dict.keys()
for station_1 in stations:
    for station_2 in stations:
        # Ignore same station routing
        if station_1 == station_2:
            pass
        elif location_dict[station_1]['routes_to'].has_key(station_2) or \
                location_dict[station_2]['routes_to'].has_key(station_1):
            pass
        else:
            location_dict[station_1]['routes_to'][station_2] = "true"
            print("Getting directions from %s to %s" % (station_1, station_2))
            origin = location_dict[station_1]['lat'] + ',' + location_dict[station_1]['long']
            destination = location_dict[station_2]['lat'] + ',' + location_dict[station_2]['long']
            url_to_call = "https://maps.googleapis.com/maps/api/directions/json?origin=" + origin + "&destination=" + destination + "&key=" + GOOGLE_MAPS_DIRECTIONS_API_KEY + "&departure_time=" + str(int(time.time())) + "&mode=bicycling&avoid=highways"
            http_response = requests.get(url=url_to_call)
            json_route_data = json.loads(http_response.text)
            location_dict[station_1]['routes_to'][station_2] = json_route_data
            #print(json.dumps(location_dict))
            time.sleep(MAPS_LOOKUP_DELAY)

# Write the dictionary to disk
output = open('location_data.pkl', 'wb')
pickle.dump(location_dict, output)
output.close()