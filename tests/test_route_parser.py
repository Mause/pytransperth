import unittest
import datetime
from unittest.mock import patch, ANY, call

from lxml.html import builder as E

from helpers.xml_test_case import XMLTestCase
from helpers.mock_utils_test_case import MockUtilsTestCase
from constants.route_parser import HEADER, STEP_BUS, STEP_WALK


class TestRouteParserInterface(unittest.TestCase):
    """
    Test the route parsers interface; in other words, integration testing
    """

    def test_parse_routes(self):
        NotImplemented


class TestRouteParserInternals(XMLTestCase, MockUtilsTestCase):
    @patch('transperth.route_parser._parse_duration')
    @patch('transperth.route_parser._parse_links')
    @patch('transperth.route_parser._parse_misc')
    def test_parse_header(self, _parse_misc, _parse_links, _parse_duration):
        from transperth.route_parser import _parse_header

        _parse_header(HEADER)

        self.assertEqualXML(
            _parse_misc.call_args[0][0],
            E.TABLE('MISC')
        )

        self.assertEqualXML(
            _parse_links.call_args[0][0],
            E.TD(E.SPAN('LINKS'))
        )

        self.assertEqualXML(
            _parse_duration.call_args[0][0],
            E.TD(E.SPAN('DURATION'))
        )

    def test_parse_links(self):
        pass

    def test_parse_img(self):
        pass

    def test_parse_duration(self):
        pass

    def test_parse_misc(self):
        pass

    def test_parse_steps(self):
        pass

    @patch('transperth.route_parser._parse_bus_step')
    @patch('transperth.route_parser._parse_walk_step')
    def test_parse_step_bus(self, _parse_walk_step, _parse_bus_step):
        from transperth.route_parser import _parse_step

        _parse_step(STEP_BUS)

        self.assertFalse(_parse_walk_step.called)

        _parse_bus_step.assert_called_with([
            'ONE',
            'TWO',
            'THREE'
        ])

    @patch('transperth.route_parser._parse_bus_step')
    @patch('transperth.route_parser._parse_walk_step')
    def test_parse_step_walk(self, _parse_walk_step, _parse_bus_step):
        from transperth.route_parser import _parse_step

        _parse_step(STEP_WALK)

        _parse_walk_step.assert_called_with([
            'ONE',
            'TWO',
            'THREE'
        ])

        self.assertFalse(_parse_bus_step.called)


    @patch('transperth.route_parser._parse_time')
    @patch('transperth.route_parser._parse_stop')
    def test_parse_bus_step(self, _parse_stop, _parse_time):
        from transperth.route_parser import _parse_bus_step

        ret = _parse_bus_step([
            'TIME1',
            'TIME2',
            'DEP_STOP_NAME',
            'DEP_STOP_NUM',
            'ARR_STOP_NAME',
            'ARR_STOP_NUM',
            '12345678REMAINING'
        ])

        assertion = {
            'step_type': 'bus',
            'route': 'REMAINING',
            'departure': {
                'stop_name': 'DEP_STOP_NAME',
                'time': ANY,
                'stop_num': ANY

            },
            'arrival': {
                'stop_name': 'ARR_STOP_NAME',
                'time': ANY,
                'stop_num': ANY
            }
        }

        self.assertEqualMock(ret, assertion)

        self.assertEqual(
            _parse_time.call_args_list,
            [call('TIME1'), call('TIME2')]
        )

        self.assertEqual(
            _parse_stop.call_args_list,
            [call('DEP_STOP_NUM'), call('ARR_STOP_NUM')]
        )

    @patch('transperth.route_parser._parse_time')
    def test_parse_walk_step(self, _parse_time):
        from transperth.route_parser import _parse_walk_step

        ret = _parse_walk_step([
            '111 m',
            'DEPARTURE'
        ])

        self.assertEqualMock(
            ret,
            {
                'step_type': 'walk',
                'walking_distance': 111,
                'departure': ANY
            }
        )

        _parse_time.assert_called_with('DEPARTURE')

    def test_parse_time(self):
        from transperth.route_parser import _parse_time

        ret = _parse_time(
            '\t          10:10 PM \t\t'
        )

        self.assertEqual(
            ret,
            datetime.time(hour=22, minute=10)
        )

    def test_parse_stop(self):
        from transperth.route_parser import _parse_stop

        ret = _parse_stop(
            '(Stop number: 111111)'
        )

        self.assertEqual(ret, 111111)

if __name__ == '__main__':
    unittest.main()
