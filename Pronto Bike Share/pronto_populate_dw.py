'''
This script will populate an SQLLite database with data from the Pronto bike share. This script is an initial hack and
needs some serious modification, DRYing, etc.

BUGS
* If a station is inserted it's update data is ignored until the next execution of the script

v1.2014-10-17
'''

# Metadata
__author__ = 'james'

# Imports
import json
import requests
import sqlite3

# Connect to the DB
conn = sqlite3.connect('pronto_dw.db')
c = conn.cursor()

# Grab the JSON data - this needs to be DRY'd
PRONTO_LOCATION_JSON_URL = 'http://secure.prontocycleshare.com/data2/stations.json'
http_response = requests.get(url=PRONTO_LOCATION_JSON_URL)
json_location_data = json.loads(http_response.text)

# Upsert data
for station in json_location_data['stations']:
    # Find the station in the DB
    c.execute("SELECT EXISTS(SELECT id from Station where Name=?);", (station['n'],))
    data = c.fetchall()
    if data[0][0] == 1:
        # Station exists; handle the update
        c.execute("SELECT id from Station where Name = ?;", (station['n'],))
        station_id = c.fetchone()[0]
        c.execute("SELECT id from Status where Station = ? and Updated = ?;", (station_id,station['lu']))
        row_data = c.fetchall()
        if row_data and row_data[0][0]:
            # Update exists already, ignore the update data
            pass
        else:
            # Update does not exist, insert it
            insert_sql = '''
            INSERT INTO Status VALUES
            (null,?,?,?,?,?,?,?,?,?,?,?)
            '''
            conn.execute(insert_sql, (station_id, station['st'], station['b'], station['su'], station['t'], station['bl'], station['ba'], station['bk'], station['da'], station['dx'], station['lu'],))
    else:
        # Station does not exist; insert it
        station_insert_sql = '''
        INSERT INTO Station VALUES (null,?,?,?,?,?)
        '''
        conn.execute(station_insert_sql, (station['id'],station['n'],station['s'].replace("'", "''"),station['la'],station['lo']))
        
# Commit the changes
conn.commit()

# Close the connection
conn.close()