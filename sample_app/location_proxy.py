import logging

from transperth.location import determine_location as _determine_location_raw
from transperth.location import Location

_location_cache = {
    'to': {},
    'from': {}
}


def determine_location(from_loco, to_loco):
    if (from_loco in set(_location_cache['from'].keys()) and
            to_loco in set(_location_cache['to'].keys())):

        logging.info('Cache hit')

        # best to confrom to the current conventions
        return {
            'to': _location_cache['to'][to_loco],
            'from': _location_cache['from'][from_loco]
        }

    logging.info('Cache miss')

    locations = _determine_location_raw(from_loco, to_loco)

    _location_cache['to'][to_loco] = locations['to']
    _location_cache['from'][from_loco] = locations['from']

    assert Location(from_loco._data) == from_loco
    assert Location(from_loco._data) in _location_cache['from']

    return locations
