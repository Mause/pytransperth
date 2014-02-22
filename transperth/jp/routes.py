import requests

from .. import BASE
from .location import determine_location, are_locations
from .route_parser import parse_routes
from .utils import format_date


__all__ = ['determine_routes']


def determine_routes(from_loco, to_loco):
    """
    Determine possible routes between the two provided locations
    """

    if are_locations(from_loco, to_loco):
        locations = determine_location(from_loco, to_loco)

        assert locations['to'], 'No corresponding to locations found'
        assert locations['from'], 'No corresponding from locations found'

        from_loco = locations['from'][0]
        to_loco = locations['to'][0]

    return _routes(from_loco.code, to_loco.code)


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
