import json
from itertools import chain
from os.path import join, dirname

import requests
from lxml import etree

from .exceptions import BadStationError

URL = (
    'http://livetimes.transperth.wa.gov.au/LiveTimes.asmx'
    '/GetSercoTimesForStation'
)

ASSETS = join(dirname(__file__), 'assets')
with open(join(ASSETS, 'train_stations.json')) as fh:
    TRAIN_STATIONS = json.load(fh)

TRAIN_STATIONS_SET = (list(station.values())[0] for station in TRAIN_STATIONS)
TRAIN_STATIONS_SET = set(chain.from_iterable(TRAIN_STATIONS_SET))


def times_for_station(station_name):
    """
    Given a station name (from ``TRAIN_STATIONS_SET``) return the associated
    incoming train timings
    """
    if station_name not in TRAIN_STATIONS_SET:
        raise BadStationError()

    r = requests.get(
        URL,
        params={
            'stationname': station_name
        }
    )

    return _parse_trips(r.content)


def _parse_trips(trips):
    root = etree.fromstring(trips)

    root = root.find('{http://services.pta.wa.gov.au/}Trips')
    trips = root.findall('{http://services.pta.wa.gov.au/}SercoTrip')

    trips = [
        {
            etree.QName(el).localname: el.text
            for el in trip
        }
        for trip in trips
    ]

    for trip in trips:
        trip.update({
            'PatternFullDisplay': trip['PatternFullDisplay'].split(', '),
            'Pattern': trip['Pattern'].split(','),
            'Cancelled': trip['Cancelled'] == 'True'
        })

    return trips


def _main():
    from pprint import pprint
    pprint(times_for_station('Perth Underground Stn'))


if __name__ == '__main__':
    _main()
