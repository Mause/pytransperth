import requests

from . import BASE
from .location import Location, determine_location
from .route_parser import parse_routes
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

    return _routes(from_string.code, to_string.code)


def _routes(from_code, to_code):
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
