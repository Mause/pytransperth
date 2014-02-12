from lxml import etree

import requests

from . import BASE
from .journey_planner import determine_routes

FARE_URL = BASE + 'DesktopModules/JourneyPlannerResults/GetFares.aspx?'


def get_fare(from_loco, to_loco):
    routes = determine_routes(from_loco, to_loco)

    route = routes[0]

    arguments = route['meta']['links'].get('getFares', None)

    if arguments is None:
        raise Exception('No fares data seem to have been provided')

    return _get_fare(*arguments)


def _get_fare(journeyCount, journeyDate, *values):

    keys = [
        'TripKey0', 'TripStart0', 'TripEnd0', 'TripKey1', 'TripStart1',
        'TripEnd1', 'TripKey2', 'TripStart2', 'TripEnd2', 'TripKey3',
        'TripStart3', 'TripEnd3', 'TripKey4', 'TripStart4', 'TripEnd4',
        'TripKey5', 'TripStart5', 'TripEnd5'
    ]

    params = dict(zip(keys, values))

    # requests with encode the slashes, so we have to conform to silly
    # ASP.net standards and manually append the damn thing
    url = FARE_URL + '?JDate={}'.format(journeyDate)

    return parse_fares(
        requests.get(
            url, params=params
        ).text
    )


def parse_fares(fares):
    root = etree.HTML(fares)

    root = root.xpath('//html/body/table/tr')[1:]  # the first is empty

    keys = root.pop(0).itertext()
    keys = [key.lower() for key in keys]
    keys.remove('comments')
    keys.remove('fare type')

    fares = dict.fromkeys(keys, {})

    root = map(etree._Element.itertext, root)
    root = map(list, root)
    for fare_type in root:
        for idx, ticket_type in enumerate(keys):
            fare = fare_type[1 + idx]

            fares[ticket_type][fare_type[0]] = parse_money(fare)

    return fares


def parse_money(string):
    return float(string[1:])