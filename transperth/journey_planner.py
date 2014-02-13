from collections import namedtuple
from lxml import etree
import datetime

import requests

from .route_parser import parse_routes
from .location import Location
from . import BASE
LocationT = namedtuple('LocationT', 'name,code')
from .utils import format_date


def determine_routes(from_loco, to_loco):
    locations = determine_location(
        Location.from_location('Esplanade'),
        Location.from_location('Curtin University, Perth')
    )

    assert locations['to'], 'No corresponding to locations found'
    assert locations['from'], 'No corresponding from locations found'

    from_string = locations['from'][0]
    to_string = locations['to'][0]

    return routes(from_string.code, to_string.code)


def format_data(date=None):
    """
    Takes a datetime.date object (or defaults to today)
    """
    date = date or datetime.date.today()

    return date.strftime('%A, %d %B %Y')


def determine_location(from_d, to_d):
    URL = BASE + 'DesktopModules/JourneyPlanner/JP.aspx'

    params = {
        'jpDate': format_data(),
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

    params.update(from_d.as_('from') or {})
    params.update(to_d.as_('to') or {})

    return parse_locations(
        requests.get(URL, params=params)
    )


def parse_locations(locations):
    assert locations.text, locations.url
    root = etree.XML(locations.text)

    return {
        element.tag.lower(): [
            LocationT(se[0].text, se[1].text)
            for se in element
        ]
        for element in root
    }


def routes(from_code, to_code):
    params = {
        'LinkMode': 'Walk',
        'StartMode': 'Walk',
        'IsAfter': 'B',
        'Priority': '504',
        'WheelchairOnly': '0',
        'Date': format_date(),
        'SchoolBusVehicleType': 'true',
        'BusVehicleType': 'true',
        'Time': '11%3a00AM',
        'WalkChange': 'NORMAL',
        'FromLoc': from_code,
        'FerryVehicleType': 'true',
        'MaxChanges': '-1',
        'TrainVehicleType': 'true',
        'find+journey.y': '',
        'jpnMaxJourneys': '5',
        'find+journey.x': '',
        'ToLoc': to_code,
        'EndMode': 'Walk'
    }

    return parse_routes(
        requests.get(
            BASE + 'JourneyPlanner/tabid/233/Default.aspx',
            params=params
        ).text
    )
