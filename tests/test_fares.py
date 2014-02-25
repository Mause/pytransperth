import os
import sys
import unittest
from unittest.mock import patch

import responses

from constants.fares import (
    FARE_BASIC_XML,
    FARE_OUTPUT,
    FARE_BASIC_ROUTES,
    NO_FARE_DATA
)


MODULE_DIR = os.path.join(os.path.dirname(__file__), '..')
MODULE_DIR = os.path.abspath(MODULE_DIR)
sys.path.insert(0, MODULE_DIR)


class TestFares(unittest.TestCase):
    @patch('transperth.jp.fares.determine_routes', return_value=FARE_BASIC_ROUTES)
    @patch('transperth.jp.fares._get_fare')
    def test_determine_fare(self, _get_fare, determine_routes):
        from transperth.jp.location import Location
        from transperth.jp.fares import determine_fare

        locos = [
            Location.from_location('Esplanade'),
            Location.from_location('Curtin University, Perth')
        ]

        # test the function
        determine_fare(*locos)

        determine_routes.assert_called_with(*locos)
        _get_fare.assert_called_with('fare', 'request', 'args')

    @patch('transperth.jp.fares.determine_routes', return_value=NO_FARE_DATA)
    def test_determine_fare_no_data(self, determine_routes):
        from transperth.jp.location import Location
        from transperth.jp.fares import determine_fare
        from transperth.jp.exceptions import NoFareData

        locos = [
            Location.from_location('Esplanade'),
            Location.from_location('Curtin University, Perth')
        ]

        # test the function
        with self.assertRaises(NoFareData):
            determine_fare(*locos)

    @patch('transperth.jp.fares.parse_fares')
    @responses.activate
    def test__get_fare(self, parse_fares):
        from transperth import BASE
        responses.add(
            responses.GET,
            BASE + 'DesktopModules/JourneyPlannerResults/GetFares.aspx',
            body=FARE_BASIC_XML.encode()
        )

        from transperth.jp.fares import _get_fare

        _get_fare(1, '00/00/0000', *range(18))

        parse_fares.assert_called_with(FARE_BASIC_XML)

    def test_parse_fares(self):
        from transperth.jp.fares import parse_fares

        # test the function
        ret = parse_fares(FARE_BASIC_XML)

        self.assertEqual(ret, FARE_OUTPUT)

    def test_parse_money(self):
        from transperth.jp.fares import parse_money

        # test the function
        ret = parse_money('$111.111')

        self.assertEqual(ret, 111.111)
