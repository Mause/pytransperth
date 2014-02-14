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
            {
                'from': [
                    LocationT('Name', 'Code')
                ]
            }
        )


# class TestLocationClass(unittest.TestCase):
#     pass

#     __init__
#     from_address
#     from_stop
#     from_location
#     as_

if __name__ == '__main__':
    unittest.main()
