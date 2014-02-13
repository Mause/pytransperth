import re
from .utils import format_date, clean

STOPNUM_RE = re.compile(r'\d{5}')


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
