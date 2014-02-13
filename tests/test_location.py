import os
import sys
import unittest
import datetime

from constants.location import LOCATION_XML

MODULE_DIR = os.path.join(os.path.dirname(__file__), '..')
MODULE_DIR = os.path.abspath(MODULE_DIR)
sys.path.insert(0, MODULE_DIR)


class TestLocationUtils(unittest.TestCase):
    def test_format_date(self):
        from transperth.location import format_date

        d = datetime.datetime(2014, 2, 13)

        self.assertEqual(
            format_date(d),
            'Thursday, 13 February 2014'
        )

    def test_determine_location(self):
        pass

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
