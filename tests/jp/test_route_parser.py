import unittest
import datetime
from unittest.mock import patch, ANY, call

from lxml.html import builder as E

from ..helpers.xml_test_case import XMLTestCase
from ..helpers.mock_utils_test_case import MockUtilsTestCase
from ..constants.route_parser import (
    HEADER,
    STEP_BUS,
    STEP_TRAIN,
    STEP_WALK,
    STEP_INVALID,
    STEPS,
    MISC,
    IMG,
    LINKS,
    DURATION,
    ROUTES
)


class TestRouteParserInterface(unittest.TestCase):
    """
    Test the route parsers interface; in other words, integration testing
    """

    def test_parse_routes(self):
        from transperth.jp.route_parser import parse_routes

        parse_routes(ROUTES)


class TestRouteParserInternals(XMLTestCase, MockUtilsTestCase):
    @patch('transperth.jp.route_parser._parse_duration')
    @patch('transperth.jp.route_parser._parse_links')
    @patch('transperth.jp.route_parser._parse_misc')
    def test_parse_header(self, _parse_misc, _parse_links, _parse_duration):
        from transperth.jp.route_parser import _parse_header

        _parse_header(HEADER)

        self.assertEqual(
            _parse_misc.call_args[0][0].text,
            'MISC'
        )

        self.assertEqual(
            _parse_links.call_args[0][0].text,
            'LINKS'
        )

        self.assertEqual(
            _parse_duration.call_args[0][0].text,
            'DURATION'
        )

    @patch('transperth.jp.route_parser._parse_img')
    def test_parse_links(self, _parse_img):
        _parse_img.return_value = ('key', 'value')

        from transperth.jp.route_parser import _parse_links

        ret = _parse_links(LINKS)

        self.assertEqualMock(
            ret,
            {
                'key': 'value'
            }
        )

        self.assertEqualXML(
            _parse_img.call_args_list[0][0][0],
            E.IMG('ONE')
        )

        self.assertEqualXML(
            _parse_img.call_args_list[1][0][0],
            E.IMG('TWO')
        )

    def test_parse_img(self):
        from transperth.jp.route_parser import _parse_img

        ret = _parse_img(IMG)

        self.assertEqual(
            ret,
            (
                'getFares',
                ['11/11/1111', 1111]
            )
        )

    def test_parse_duration(self):
        from transperth.jp.route_parser import _parse_duration

        self.assertEqual(
            _parse_duration(DURATION),
            datetime.timedelta(hours=11, minutes=11)
        )

    def test_parse_misc(self):
        from transperth.jp.route_parser import _parse_misc

        ret = _parse_misc(MISC)

        self.assertEqual(
            ret,
            {
                'arrival_time': datetime.time(11, 0),
                'depart_time': datetime.time(10, 30),
                'number_of_legs': 1,
                'total_walking_distance': 0
            }
        )

    @patch('transperth.jp.route_parser._parse_step')
    def test_parse_steps(self, _parse_step):
        from transperth.jp.route_parser import _parse_steps

        _parse_steps(['IGNORED', STEPS])

        self.assertEqualXML(
            _parse_step.call_args_list[0][0][0],
            E.TABLE('STEP1')
        )

        self.assertEqualXML(
            _parse_step.call_args_list[1][0][0],
            E.TABLE('STEP2')
        )

    @patch('transperth.jp.route_parser._parse_bus_step')
    def test_parse_step_bus(self, _parse_bus_step):
        from transperth.jp.route_parser import _parse_step

        _parse_step(STEP_BUS)

        _parse_bus_step.assert_called_with([
            ('ONE', 'TWO')
        ])

    @patch('transperth.jp.route_parser._parse_train_step')
    def test_parse_step_train(self, _parse_train_step):
        from transperth.jp.route_parser import _parse_step

        _parse_step(STEP_TRAIN)

        _parse_train_step.assert_called_with([
            ('ONE', 'TWO')
        ])

    @patch('transperth.jp.route_parser._parse_walk_step')
    def test_parse_step_walk(self, _parse_walk_step):
        from transperth.jp.route_parser import _parse_step

        _parse_step(STEP_WALK)

        _parse_walk_step.assert_called_with([
            'ONE',
            'TWO',
            'THREE'
        ])

    def test_parse_step_invalid(self):
        from transperth.jp.route_parser import _parse_step
        from transperth.exceptions import InvalidStep

        with self.assertRaises(InvalidStep):
            _parse_step(STEP_INVALID)

    @patch('transperth.jp.route_parser._parse_time')
    @patch('transperth.jp.route_parser._parse_stop')
    def test_parse_bus_step(self, _parse_stop, _parse_time):
        from transperth.jp.route_parser import _parse_bus_step

        ret = _parse_bus_step([
            ('TIME1', 'TIME2'),
            ('DEP_STOP_NAME', 'DEP_STOP_NUM'),
            ('ARR_STOP_NAME', 'ARR_STOP_NUM'),
            '12345678ROUTE'
        ])

        assertion = {
            'step_type': 'bus',
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

    @patch('transperth.jp.route_parser._parse_time')
    @patch('transperth.jp.route_parser._parse_stop')
    def test_parse_train_step(self, _parse_stop, _parse_time):
        from transperth.jp.route_parser import _parse_train_step

        ret = _parse_train_step([
            ('TIME1', 'TIME2'),
            ('DEP_STOP_NAME', 'ARR_STOP_NAME'),
            '12345678ROUTE'
        ])

        assertion = {
            'step_type': 'train',
            'departure': {
                'stop_name': 'DEP_STOP_NAME',
                'time': ANY

            },
            'arrival': {
                'stop_name': 'ARR_STOP_NAME',
                'time': ANY
            }
        }

        self.assertEqualMock(ret, assertion)

        self.assertEqual(
            _parse_time.call_args_list,
            [call('TIME1'), call('TIME2')]
        )

    @patch('transperth.jp.route_parser._parse_time')
    def test_parse_walk_step(self, _parse_time):
        from transperth.jp.route_parser import _parse_walk_step

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
        from transperth.jp.route_parser import _parse_time

        ret = _parse_time(
            '\t          10:10 PM \t\t'
        )

        self.assertEqual(
            ret,
            datetime.time(hour=22, minute=10)
        )

    def test_parse_stop(self):
        from transperth.jp.route_parser import _parse_stop

        ret = _parse_stop(
            '(Stop number: 111111)'
        )

        self.assertEqual(ret, 111111)

    def test_parse_route_text(self):
        from transperth.jp.route_parser import _parse_route_text

        self.assertDictEqual(
            _parse_route_text(
                '100 (As) Curtin University Bus Stn - '
                'Canning Bridge Stn'
            ),
            {
                'flags': ['As'],
                'route_moniker': '100',
                'from': 'Curtin University Bus Stn',
                'to': 'Canning Bridge Stn'
            }
        )

        self.assertDictEqual(
            _parse_route_text(
                'Mandurah Line (As) Mandurah Stn - '
                'Perth Underground Stn All Stops Mandurah to Esplanade Stn'
            ),
            {
                'flags': ['As'],
                'route_moniker': 'Mandurah Line',
                'from': 'Mandurah Stn',
                'to': (
                    'Perth Underground Stn All Stops Mandurah to Esplanade Stn'
                )
            }
        )

        self.assertDictEqual(
            _parse_route_text(
                'Thornlie Line (As) Perth Stn - Thornlie Stn T '
                'Pattern to Thornlie. Departs Platform 4 At Perth, '
                'Platform 2 At Mciver And Claisebrook.'
            ),
            {
                'flags': ['As'],
                'route_moniker': 'Thornlie Line',
                'from': 'Perth Stn',
                'to': 'Thornlie Stn T Pattern to Thornlie.',
                'departs': (
                    'Platform 4 At Perth, '
                    'Platform 2 At Mciver And Claisebrook.'
                )
            }
        )

        self.assertDictEqual(
            # i don't understand the route, but i took it directly from
            # the transperth website, so meh
            _parse_route_text('98 (Ls|As) Fremantle Stn - Fremantle Stn'),
            {
                'flags': ['Ls', 'As'],
                'from': 'Fremantle Stn',
                'to': 'Fremantle Stn',
                'route_moniker': '98'
            }
        )


if __name__ == '__main__':
    unittest.main()
