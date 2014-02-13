import unittest
from unittest.mock import patch

import responses

from constants.fares import (
    FARE_BASIC_XML,
    FARE_OUTPUT,
    FARE_BASIC_ROUTES
)


class TestFares(unittest.TestCase):
    @patch('transperth.fares.determine_routes', return_value=FARE_BASIC_ROUTES)
    @patch('transperth.fares._get_fare')
    def test_get_fare(self, _get_fare, determine_routes):
        from transperth.location import Location
        from transperth.fares import get_fare

        locos = [
            Location.from_location('Esplanade'),
            Location.from_location('Curtin University, Perth')
        ]

        # test the function
        get_fare(*locos)

        determine_routes.assert_called_with(*locos)
        _get_fare.assert_called_with('fare', 'request', 'args')

    @patch('transperth.fares.parse_fares')
    @responses.activate
    def test__get_fare(self, parse_fares):
        # far better than just mocking out requests
        responses.add(
            responses.GET,
            'http://www.transperth.wa.gov.au/'
            'DesktopModules/JourneyPlannerResults/GetFares.aspx',
            body=FARE_BASIC_XML.encode()
        )

        from transperth.fares import _get_fare

        _get_fare(1, '00/00/0000', *range(18))

        parse_fares.assert_called_with(FARE_BASIC_XML)

    def test_parse_fares(self):
        from transperth.fares import parse_fares

        # test the function
        ret = parse_fares(FARE_BASIC_XML)

        self.assertEqual(ret, FARE_OUTPUT)

    def test_parse_money(self):
        from transperth.fares import parse_money

        # test the function
        ret = parse_money('$111.111')

        self.assertEqual(ret, 111.111)


if __name__ == '__main__':
    unittest.main()
