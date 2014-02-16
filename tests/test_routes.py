import unittest
from unittest.mock import patch

from constants.routes import ROUTES


class TestRoutes(unittest.TestCase):
    # for some reason we have to patch this
    @patch('transperth.routes.determine_location', return_value=ROUTES)
    # instead of transperth.location.determine_location
    @patch('transperth.routes._routes')
    def test_determine_routes(self, _routes, determine_location):
        from transperth.location import Location
        from transperth.routes import determine_routes

        determine_routes(
            Location.from_location('LOCATION1'),
            Location.from_location('LOCATION2')
        )

        _routes.assert_called_with(
            ROUTES['from'][0].code,
            ROUTES['to'][0].code
        )

    # kinda pointless testing _routes, considering it only builds a request
    # and sends it
    # @responses.activate
    # def test__routes(self):
    #     pass

if __name__ == '__main__':
    unittest.main()
