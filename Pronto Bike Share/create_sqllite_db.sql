/*
This script cteates a small-scale SQLLite database for storing data related to the
Seattle Pronto Bike Share program (https://www.prontocycleshare.com)

This was created quickly with little thought, so use at your own risk.
v1.2014-10-18
*/

--Create Station table
DROP INDEX IF EXISTS IDX_Station;
DROP TABLE IF EXISTS Station;
CREATE TABLE Station(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	station_id INTEGER NOT NULL,
	Name VARCHAR(25) NOT NULL,
	Description VARCHAR(25) NOT NULL,
	Latitude REAL NOT NULL,
	Longitude REAL NOT NULL
);
CREATE INDEX IDX_Station_Location ON Station(Name, Latitude, Longitude);

--Create Status table
DROP INDEX IF EXISTS IDX_Status;
DROP TABLE IF EXISTS Status;
CREATE TABLE Status(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	Station INTEGER,
	st INTEGER NOT NULL,
	b INTEGER NOT NULL,
	su INTEGER NOT NULL,
	t INTEGER NOT NULL,
	bk INTEGER NOT NULL,
	bl INTEGER NOT NULL,
	Available_Bikes INT NOT NULL, -- ba
	Unavailable_Bikes INT NOT NULL, -- bk
	Available_Spots INT NOT NULL, -- da
	Unavailable_Spots INT NOT NULL, -- dx
	Updated INT NOT NULL,
	FOREIGN KEY(Station) REFERENCES Station(id));
CREATE INDEX IDX_Status ON Status(Available_Bikes, Unavailable_Bikes);