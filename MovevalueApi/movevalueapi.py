"""
Module to obtain data from the Walkscore website.

In my opinion, the Walkscore API is too limited for educational data gathering and related projects. This module
is designed to make it easier to scrape data from Walkscore.

This module is intended for educational and research purposes only.
"""

__author__ = 'James Malone'
__license__ = "MIT"
__version__ = "0.2"
__maintainer__ = "James Malone"
__email__ = "jamalone at gmail dot com"
__status__ = "Development"

# Packages needed for this module
from bs4 import BeautifulSoup
import re
import requests

class WsLocation:
    def __init__(self, *init_data, **kwargs):
        for dictionary in init_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

class City(WsLocation):
    """
    Represents a city from the Walkscore website
    """
    def __init__(self, *init_data, **kwargs):
        WsLocation.__init__(self, *init_data, **kwargs)

    @property
    def neighborhoods(self):
        nh_list = []
        for nh in self._neighborhoods:
            nh['city'] = self.name
            nh['state'] = self.state
            new_neighborhood = Neighborhood(nh)
            nh_list.append(new_neighborhood)
        return nh_list

    @neighborhoods.setter
    def neighborhoods(self, value):
        self._neighborhoods = value

class Neighborhood(WsLocation):
    """
    Represents a neighborhood from the Walkscore website
    """
    def __init__(self, *init_data, **kwargs):
        WsLocation.__init__(self, *init_data, **kwargs)

    def get_full_data(self):
        # todo fix this error - missing state
        self.__init__(self, MovevalueApi.data_for_neighborhood(self.name, self.city, self.state))


class MovevalueApi:
    """
    Class to interact with the Walkscore website
    """
    base_city_url = 'https://www.walkscore.com/%s/%s'
    base_neighborhood_url = 'https://www.walkscore.com/%s/%s/%s'
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
        'table':
            {
                'neighborhoods': 'id=hoods-list-table',
            },
    }

    def data_for_neighborhood(self, name, city, state):
        nh_url = self.walkscore_neighborhood_url(name, city, state)
        ws_data = self.get_page_data(nh_url)
        nh_data = self.parse_data_points(ws_data)
        nh_data['name'] = name
        nh_data['city'] = city
        nh_data['state'] = state
        new_neighborhood = Neighborhood(nh_data)

        return new_neighborhood

    def data_for_city(self, name, state):
        city_url = self.walkscore_city_url(name, state)
        ws_data = self.get_page_data(city_url)
        city_data = self.parse_data_points(ws_data)
        city_data['name'] = name
        city_data['state'] = state
        newCity = City(city_data)

        return newCity

    def parse_data_points(self, html):
        parsed_data = {}
        for data_type in MovevalueApi.regex_filters.keys():
            if data_type == 'int':
                for data_attribute in MovevalueApi.regex_filters[data_type].keys():
                    value = self.regex_page_data_int(MovevalueApi.regex_filters[data_type][data_attribute], html)
                    parsed_data[data_attribute] = value
            elif data_type == 'float':
                for data_attribute in MovevalueApi.regex_filters[data_type].keys():
                    value = self.regex_page_data_float(MovevalueApi.regex_filters[data_type][data_attribute], html)
                    parsed_data[data_attribute] = value
            elif data_type == 'table':
                for data_attribute in MovevalueApi.regex_filters[data_type].keys():
                    value = self.regex_page_data_table(MovevalueApi.regex_filters[data_type][data_attribute], html)
                    parsed_data[data_attribute] = value
        return parsed_data


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
        soup = BeautifulSoup(html)
        attributes = pattern.split('=')
        table_data = []
        table = soup.find("table", attrs={attributes[0]:attributes[1]})

        if table is not None:
            headings = [th.get_text() for th in table.find("tr").find_all("th")]

            # Format the headings
            for idx, item in enumerate(headings):
                headings[idx] = re.sub('[!@#$]', '', item.lower().replace(' ', '_'))

            # Iterate the table and parse the data
            for row in table.findAll("tr")[1:]:
                cells = row.findAll("td")
                row_data = {}
                for i in range(0, len(cells) -1):
                    row_data[headings[i]] = cells[i].get_text()
                table_data.append(row_data)
            return table_data
        else:
            return None


    def regex_page_data(self, pattern, html):
        result = re.search(pattern, html)
        if result is not None:
            return result.group(1)
        else:
            return None


    def walkscore_city_url(self, city, state):
        """
        Return a well-formatted Walkscore URL
        """
        return MovevalueApi.base_city_url % (state, city.replace(' ', '_'))

    def walkscore_neighborhood_url(self, name, city, state):
        """
        Return a well-formatted Walkscore URL
        """
        return MovevalueApi.base_neighborhood_url % (state, city.replace(' ', '_'), name.replace(' ', '_'))