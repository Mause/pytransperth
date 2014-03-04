import re
from lxml import etree
from collections import namedtuple

import requests

from .. import BASE_HTTP
from .utils import format_date, clean
from ..exceptions import InvalidStopNumber, InvalidDirection

STOPNUM_RE = re.compile(r'\d{5}')


__all__ = [
    'determine_location',
    'Location',
    'parse_locations',
    'ResolvedLocation'
]


is_location = lambda arg: isinstance(arg, Location)
are_locations = lambda *args: all(map(is_location, args))


# Allows the use of Location in function signatures
class Location():
    pass


def determine_location(from_loco: Location, to_loco: Location) -> dict:
    """
    Takes two location objects, and returns a dict of lists of ResolvedLocation
    mapping possible corresponding real world locations and their codes.

    See :func:`parse_locations` for precise output format.
    """
    assert are_locations(from_loco, to_loco)

    URL = BASE_HTTP + 'DesktopModules/JourneyPlanner/JP.aspx'

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

    params.update(from_loco.as_('from'))
    params.update(to_loco.as_('to'))

    return parse_locations(
        requests.get(URL, params=params).text
    )


def parse_locations(locations: str) -> dict:
    """
    Takes the (pure) XML from the locations request and returns it like so;

    .. code-block:: python

        {
            "from": [
                ResolvedLocation('<NAME>', '<CODE>')
            ]
        }
    """
    root = etree.XML(locations)

    return {
        element.tag.lower(): [
            ResolvedLocation(
                *clean(sub_element.itertext())
            )
            for sub_element in element
        ]
        for element in root
    }


class ResolvedLocation(namedtuple('ResolvedLocation', 'name,code')):
    """
    Represents a location as considered by the transperth api
    """


class Location(object):
    """
    Represents a location that has not been resolved into a (ResolvedLocation)
    location code
    """

    def __init__(self, data: dict):
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
    def from_address(self, street: str, suburb: str) -> Location:
        return Location({
            'street': street,
            'suburb': suburb,
            '': 'Point'
        })

    @classmethod
    def from_stop(self, stop_number: 'str or int') -> Location:
        """
        Creates a Location from a transperth stop number.

        Applies only to bus stops.

        :param stop_number:
        """

        stop_number = str(stop_number)

        if not STOPNUM_RE.match(stop_number):
            raise InvalidStopNumber('Invalid stop number')

        return Location({
            'stop': stop_number,
            '': 'Node'
        })

    @classmethod
    def from_location(self, location: str) -> Location:
        """
        Creates a Location from an arbibrary location, such as;

         * Curtin University, Perth
         * Arena Joondalup

        :param location: arbibrary location
        """
        return Location({
            'location': location,
            '': 'Location'
        })

    def as_(self, direction: str) -> dict:
        """
        Formats the _data attribute so that it can be incorporated into
        a request to transperth's api

        .. code-block:: python

            {
                'to': str,
                'toStreet': str,
                'toSuburb': str,
                'toLocation': str,
                'toStop': str,
            }
        """

        if direction not in {'to', 'from'}:
            raise InvalidDirection('tf casn')

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
        assert isinstance(other, self.__class__)

        return self.__hash__() == other.__hash__()
