import logging

from transperth.location import determine_location as _determine_location_raw
from transperth.location import Location

_location_cache = {}


def determine_location(from_loco, to_loco):
    cache_from = _location_cache.get(from_loco)
    cache_to = _location_cache.get(to_loco)

    if cache_from and cache_to:

        logging.info('Cache hit')

        # best to conform to the current conventions
        return {
            'to': cache_to,
            'from': cache_from
        }

    logging.info('Cache miss')

    locations = _determine_location_raw(from_loco, to_loco)

    _location_cache[to_loco] = locations['to']
    _location_cache[from_loco] = locations['from']

    assert Location(from_loco._data) == from_loco
    assert Location(from_loco._data) in _location_cache

    return locations
