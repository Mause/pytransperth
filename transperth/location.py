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
    """
    Takes two location objects, and returns a dict of lists of LocationTs
    mapping possible corresponding locations and their codes
    """
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

    params.update(from_d.as_('from'))
    params.update(to_d.as_('to'))

    return parse_locations(
        requests.get(URL, params=params).text
    )


def parse_locations(locations):
    """
    Takes the (pure) XML from the locations request and returns in the format;

    {
        "from": [
            LocationT('<NAME>', '<CODE>')
        ]
    }
    """
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
    """
    Represents a location that has not been resolved into a (LocationT)
    location code
    """

    def __init__(self, data):
        """
        It is recommend you use one of the specialised methods;
        from_address, from_stop, or from_location
        """
        self._data = {
            '': 'Location',  # this is required
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
            '': 'Point'
        })

    @classmethod
    def from_stop(self, stop_number):
        if not STOPNUM_RE.match(stop_number):
            raise Exception('Invalid stop number')

        return Location({
            'stop': stop_number,
            '': 'Node'
        })

    @classmethod
    def from_location(self, location_string):
        return Location({
            'location': location_string,
            '': 'Location'
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

    def __hash__(self):
        items = sorted(
            self._data.items(),
            key=lambda i: i[0]
        )

        return hash(','.join(map(':'.join, items)))

    def __eq__(self, other):
        assert isinstance(other, Location)

        return self.__hash__() == other.__hash__()
