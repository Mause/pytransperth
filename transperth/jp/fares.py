"""
Provides faculties for determining the price of a route under different
circumstances
"""

from lxml import etree
import requests

from .. import BASE_HTTP
from .utils import clean, itertext
from .routes import determine_routes
from .location import Location, ResolvedLocation
from ..exceptions import NoFareData

FARE_URL = BASE_HTTP + 'DesktopModules/JourneyPlannerResults/GetFares.aspx'


__all__ = ['determine_fare']


def determine_fare(
        from_loco: Location or ResolvedLocation,
        to_loco: Location or ResolvedLocation) -> dict:
    """
    Returns the fare for the recommended route from `from_loco` to
    `to_loco` in the format;

    .. code-block:: python

        {
            '<TICKET-CLASS>': {
                '<TICKET-TYPE>': <COST>
            }
        }
    """
    routes = determine_routes(from_loco, to_loco)

    route = routes[0]

    return fares_for_route(route)


def fares_for_route(route):
    arguments = route['meta']['links'].get('getFares', None)

    if arguments is None:
        raise NoFareData('No fares data seem to have been provided')

    return _get_fare(*arguments)


def _get_fare(journeyCount, journeyDate, *values):
    """
    Used internally to format the request for a fare for a route
    """

    keys = [
        'TripKey0', 'TripStart0', 'TripEnd0', 'TripKey1', 'TripStart1',
        'TripEnd1', 'TripKey2', 'TripStart2', 'TripEnd2', 'TripKey3',
        'TripStart3', 'TripEnd3', 'TripKey4', 'TripStart4', 'TripEnd4',
        'TripKey5', 'TripStart5', 'TripEnd5'
    ]

    params = dict(zip(keys, values))

    # ASP.net wants the date with normal slashes, but requests will encode
    # the slashes, so we have to manually append the damn thing
    url = FARE_URL + '?JDate={}'.format(journeyDate)

    return parse_fares(
        requests.get(
            url, params=params
        ).text
    )


def parse_fares(fares):
    """
    Parses the XML representing the fares
    """

    root = etree.HTML(fares)
    root = root.xpath('//html/body/table/tr')[1:]  # the first is empty

    # determine ticket class'
    keys = root.pop(0).itertext()
    keys = clean(keys)
    keys = [key.lower() for key in keys]

    # remove the 'comments' and 'fare type' column labels
    keys = keys[1:-1]

    fares = dict.fromkeys(keys, {})

    root = map(itertext, root)
    root = map(clean, root)

    for fare_type in root:
        fare_name, *fare_values = fare_type

        for ticket_type, fare in zip(keys, fare_values):
            fares[ticket_type][fare_name] = parse_money(
                fare
            )

    return fares


def parse_money(string):
    """
    Parses a string with a character denoting currency into a float

    Until I can get pymoneyed to play ball, ignored the currency
    """
    return float(string[1:])
