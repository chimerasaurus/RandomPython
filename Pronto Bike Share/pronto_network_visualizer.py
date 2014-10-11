'''
Opens saved network location data for the Seattle Pronto cycle network and
creates a table showing the transit time between each station.

v1.2014-10-10
'''

# Metadata
__author__ = 'james'

# Imports
import pickle

# Open serialized data
file = open('location_data.pkl','rb')
saved_location_data = pickle.load(file)
file.close()

# Create a list with data
location_keys = sorted(map(int, saved_location_data.keys()))
master_data_list = [[''] + location_keys]

for location_1 in location_keys:
    location_row = []
    location_row.append((location_1))
    for location_2 in location_keys:
        outcome = "/"
        if location_1 == location_2:
            pass
        else:
            if str(location_2) in saved_location_data[str(location_1)]['routes_to']:
                map_data = saved_location_data[str(location_1)]['routes_to'][str(location_2)]
                if map_data['status'] != 'OK':
                    outcome = "API FAIL"
                else:
                    duration = (map_data['routes'][0]['legs'][0]['duration']['value'])/60
                    outcome = duration
            elif str(location_1) in saved_location_data[str(location_2)]['routes_to']:
                map_data = saved_location_data[str(location_2)]['routes_to'][str(location_1)]
                if map_data['status'] != 'OK':
                    outcome = "API FAIL"
                else:
                    duration = (map_data['routes'][0]['legs'][0]['duration']['value'])/60
                    outcome = duration
            else:
                outcome = "UNKNOWN FAIL"
        location_row.append(outcome)
    master_data_list.append(location_row)

for row in master_data_list:
    print(','.join(map(str, row)))
