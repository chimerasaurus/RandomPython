# Imports
import requests
import argparse
import datetime

parser = argparse.ArgumentParser(description='Grab historical AirNow data')
parser.add_argument('-d', action="store", default=False, dest="date")
parser.add_argument('-n', action="store", default=False, dest="numdays", type=int)
parser.add_argument('-m', action="store", default=False, dest="distance")
parser.add_argument('-z', action="store", default=False, dest="zip")
parser.add_argument('-a', action="store", default=False, dest="apikey")
results = parser.parse_args()

# Open the out file for writing
with open(results.zip + ".csv", "a") as data_file:
    # Cycle through the days
    start_date = datetime.datetime.strptime(results.date, '%Y-%m-%d')
    for i in range(0, results.numdays+1):
        date_to_grab = start_date + datetime.timedelta(days=i)
        print (date_to_grab)
        
        # Grab the data
        url_to_call = "http://www.airnowapi.org/aq/observation/zipCode/historical/?format=text/csv&zipCode=%s&date=%s&distance=%s&API_KEY=%s" % (results.zip, date_to_grab.strftime("%Y-%m-%dT%H-%M%S" ), results.distance, results.apikey)
        r = requests.get(url_to_call)
        data = r.text.strip().split('\n')
        
        # First loop, keep headers
        if i == 0:
            for line in data:
                data_file.write(line + "\n")
        else:
            for line in data[1:]:
                data_file.write(line + "\n")
