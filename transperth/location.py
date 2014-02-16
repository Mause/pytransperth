import re
from lxml import etree
from collections import namedtuple

import requests

from . import BASE
from .utils import format_date, clean

STOPNUM_RE = re.compile(r'\d{5}')


__all__ = [
    'determine_location',
    'Location',
    'parse_locations',
    'LocationT'
]

LocationT = namedtuple('LocationT', 'name,code')

is_location = lambda arg: isinstance(arg, Location)
are_locations = lambda *args: all(map(is_location, args))


def determine_location(from_d, to_d):
    assert are_locations(from_d, to_d)

    URL = BASE + 'DesktopModules/JourneyPlanner/JP.aspx'

    params = {
        'jpDate': format_date(),
        'jpDirection': 'B',
        # 'jpAMPM': 'AM',
        # 'jpHour': '11',
        # 'jpMinute': '00',
        'fSet': 'False',
        'fGadget': 'False',
        'mode': 't1,b1,f1,s1',
        'jpnMaxJourneys': '5',
        'jpMaxChanges': '-1',
        'jpWalkChange': 'NORMAL',
        'jpWheelchairOnly': '0'
    }

    params.update(from_d.as_('from') or {})
    params.update(to_d.as_('to') or {})

    return parse_locations(
        requests.get(URL, params=params).text
    )


def parse_locations(locations):
    root = etree.XML(locations)

    return {
        element.tag.lower(): [
            LocationT(
                *clean(se.itertext())
            )
            for se in element

        ]
        for element in root
    }


class Location(object):
    def __init__(self, data):
        """
        It is recommend you use one of the specialised methods;
        from_address, from_stop, or from_location
        """
        self._data = {
            '': 'LOCATION',  # this is required
            'street': '',
            'suburb': '',
            'location': '',
            'stop': ''
        }

        self._data.update(data)

    @classmethod
    def from_address(self, street, suburb):
        return Location({
            'street': street,
            'suburb': suburb,
            '': 'POINT'
        })

    @classmethod
    def from_stop(self, stop_number):
        if stop_number and not STOPNUM_RE.match(stop_number):
            raise Exception('Invalid stop number')

        return Location({
            'stop': stop_number,
            '': 'NODE'
        })

    @classmethod
    def from_location(self, location_string):
        return Location({
            'location': location_string,
            '': 'LOCATION'
        })

    def as_(self, direction):
        """
        Returns the input data as a something like the following;

        {
            'to': str,
            'toStreet': str,
            'toSuburb': str,
            'toLocation': str,
            'toStop': str,
        }
        """

        if direction not in {'to', 'from'}:
            raise Exception('tf casn')

        self._data[''] = self._data[''].title()

        return {
            direction + k.title(): v
            for k, v in self._data.items()
        }
