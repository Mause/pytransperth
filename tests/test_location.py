import os
import sys
import unittest
from unittest.mock import patch

import responses

from constants.location import LOCATION_XML

MODULE_DIR = os.path.join(os.path.dirname(__file__), '..')
MODULE_DIR = os.path.abspath(MODULE_DIR)
sys.path.insert(0, MODULE_DIR)


class TestLocationUtils(unittest.TestCase):
    @responses.activate
    @patch('transperth.location.parse_locations')
    def test_determine_location(self, parse_locations):
        responses.add(
            responses.GET,
            'http://www.transperth.wa.gov.au/'
            'DesktopModules/JourneyPlanner/JP.aspx',
            body='TEXT'.encode()
        )

        from transperth.location import determine_location, Location

        determine_location(
            Location.from_location('Curtin University, Perth'),
            Location.from_location('Arena Joondalup')
        )

        parse_locations.assert_called_with('TEXT')

    def test_parse_locations(self):
        from transperth.location import parse_locations, LocationT

        ret = parse_locations(LOCATION_XML)

        self.assertEqual(
            ret,
            {'from': [LocationT('Name', 'Code')]}
        )


class TestLocationClass(unittest.TestCase):
    def test_initialisation(self):
        from transperth.location import Location

        self.assertEqual(
            Location({'hello': 'world'})._data,
            {
                'hello': 'world',
                '': 'Location',
                'street': '',
                'suburb': '',
                'location': '',
                'stop': ''
            }
        )

    def test_from_address(self):
        from transperth.location import Location

        self.assertEqual(
            Location.from_address('STREET', 'SUBURB')._data,
            {
                'street': 'STREET',
                'suburb': 'SUBURB',
                '': 'Point',

                'location': '',
                'stop': '',
            }
        )

    def test_from_stop(self):
        from transperth.location import Location

        self.assertEqual(
            Location.from_stop('11111')._data,
            {
                'stop': '11111',
                '': 'Node',

                'location': '',
                'street': '',
                'suburb': ''
            }
        )

    def test_from_stop_invalid_exception(self):
        from transperth.location import Location
        from transperth.exceptions import InvalidStopNumber

        self.assertRaises(
            InvalidStopNumber,
            Location.from_stop,
            ('1111',)
        )

    def test_from_location(self):
        from transperth.location import Location

        self.assertEqual(
            Location.from_location('LOCATION')._data,
            {
                '': 'Location',
                'location': 'LOCATION',

                'stop': '',
                'street': '',
                'suburb': ''
            }
        )

    def test_as_(self):
        from transperth.location import Location

        self.assertEqual(
            Location.from_location('LOCATION').as_('to'),
            {
                'to': 'Location',
                'toLocation': 'LOCATION',
                'toStop': '',
                'toStreet': '',
                'toSuburb': ''
            }
        )

    def test_as_exception(self):
        from transperth.location import Location
        from transperth.exceptions import InvalidDirection

        self.assertRaises(
            InvalidDirection,
            Location.from_location('LOCATION').as_,
            ('INVALID',)
        )

    def test__hash__(self):
        from transperth.location import Location

        # really we are just ensuring that no exceptions are thrown
        # whether or not it actually operates correctly is ensured in the
        # test for __eq__

        Location({}).__hash__()

    def test__eq__(self):
        from transperth.location import Location

        data = {
            'hello': 'world'
        }

        self.assertEqual(
            Location(data),
            Location(data)
        )


if __name__ == '__main__':
    unittest.main()
