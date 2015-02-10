"""
Module to obtain data from the Walkscore website.

In my opinion, the Walkscore API is too limited for educational data gathering and related projects. This module
is designed to make it easier to scrape data from Walkscore.

This module is intended for educational and research purposes only.
"""

__author__ = 'James Malone'
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "James Malone"
__email__ = "jamalone at gmail dot com"
__status__ = "Development"

# Packages needed for this module
import bs4
import json
import re
import requests

class WsLocation:
    def __init__(self,name):
        self.name = name
        self.walk_score = None
        self.transit_score = None
        self.bike_score = None
        self.population = None
        self.restaurants = None
        self.restaurant_average = None

class City(WsLocation):
    """
    Represents a city from the Walkscore website
    """
    def __init__(self, name, state):
        WsLocation.__init__(self, name=name)
        self.state = state
        self.neighborhoods = None

class Neighborhood(WsLocation):
    """
    Represents a neighborhood from the Walkscore website
    """
    def __init__(self, name):
        WsLocation.__init__(self, name=name)


class MovevalueApi:
    """
    Class to interact with the Walkscore website
    """
    base_url = 'https://www.walkscore.com/%s/%s'
    null_score_value = 0
    regex_filters = {
        'int':
            {
                'walk_score': '\/\/pp.walk.sc\/badge\/walk\/score\/(\d+)\.svg',
                'transit_score': '\/\/pp.walk.sc\/badge\/transit\/score\/(\d+)\.svg',
                'bike_score': '\/\/pp.walk.sc\/badge\/bike\/score\/(\d+)\.svg',
                'population': 'with\s+(\S+)\s+residents',
                'restaurants': 'about\s+(\S+)\s+restaurants'
            },
        'float':
            {
                'restaurant_average': 'average\s+of\s+(\S+)\s+restaurants',
            },
    }

    def data_for_city(self, name, state):
        newCity = City(name, str(state).upper())
        city_url = self.walkscore_url(state, name)
        city_data = self.get_page_data(city_url)
        self.parse_data_points(newCity, city_data)

        return newCity

    def parse_data_points(self, city, html):
        for data_type in MovevalueApi.regex_filters.keys():
            if data_type == 'int':
                for data_attribute in MovevalueApi.regex_filters[data_type].keys():
                    value = self.regex_page_data_int(MovevalueApi.regex_filters[data_type][data_attribute], html)
                    setattr(city, data_attribute, value)
            elif data_type == 'float':
                for data_attribute in MovevalueApi.regex_filters[data_type].keys():
                    value = self.regex_page_data_float(MovevalueApi.regex_filters[data_type][data_attribute], html)
                    setattr(city, data_attribute, value)

    def get_page_data(self, url):
        r = requests.get(url)
        page_data = str(r.content)
        return page_data

    def regex_page_data_int(self, pattern, html):
        result = self.regex_page_data(pattern, html)
        if result is not None:
            if ',' in result:
                result = result.replace(',', '')
            result = int(result)
        return result

    def regex_page_data_float(self, pattern, html):
        result = self.regex_page_data(pattern, html)
        if result is not None:
            if ',' in result:
                result = result.replace(',', '')
            result = float(result)
        return result

    def regex_page_data_table(self, pattern, html):
        #todo

    def regex_page_data(self, pattern, html):
        result = re.search(pattern, html)
        if result is not None:
            return result.group(1)
        else:
            return None

    def walkscore_url(self, state, city):
        """
        Return a well-formatted Walkscore URL
        """
        return MovevalueApi.base_url % (state, city.replace(' ', '_'))