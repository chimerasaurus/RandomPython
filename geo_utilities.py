"""
Geography utilities for Python. Functions designed to carry out specific geography-related tasks.

The following threads helped to build this class:
* http://stackoverflow.com/questions/15736995/
    how-can-i-quickly-estimate-the-distance-between-two-latitude-longitude-points

"""

__author__ = 'James Malone'

# Imports
from math import radians, cos, sin, asin, sqrt

def distance_between_coordinates_km(lon1, lat1, lon2, lat2):
    """
    Calculate the distance (great circle) between two points on the Earth. This calculation uses
    the Haversine formula.
    """

    # Decimal degrees (lat, long) to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Haversine formula
    delta_lon = lon2 - lon1
    delta_lat = lat2 - lat1
    a = sin(delta_lat/2)**2 + cos(lat1) * cos(lat2) * sin(delta_lon/2)**2
    c = 2 * asin(sqrt(a))
    distance_in_km = 6367 * c
    return distance_in_km

def distance_between_coordinates_mi(lon1, lat1, lon2, lat2):
    """
    Calculate the distance between coordinates in miles using the Haversine formula.
    :param lon1: Point A longitude
    :param lat1: Point A latitude
    :param lon2: Point B longitude
    :param lat2: Point A latitude
    :return: Distance between points in miles
    """
    return distance_between_coordinates_km(lon1, lat1, lon2, lat2) * 0.62137