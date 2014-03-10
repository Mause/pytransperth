"""
Parses actions into separate trips
"""
from functools import reduce
from operator import add, itemgetter


TAG_OFF = 'Normal TAG OFF'
TAG_ON = 'Normal TAG ON'

# synthetic actions are created when the smart rider user forgets to either
# tag on at the start, or tag off at the end of a trip aboard one of the
# transport services
SYNTHETIC_TAG_ON = 'Synthetic TAG ON'
SYNTHETIC_TAG_OFF = 'Synthetic TAG OFF'  # this is only presumed to exist

VALID_TRIP_ACTIONS = [TAG_OFF, TAG_ON, SYNTHETIC_TAG_ON, SYNTHETIC_TAG_OFF]

TRANSFER = 'Transfer'


class TripTracer(object):
    def __init__(self, actions):
        actions = filter(
            lambda action: action['action'] in VALID_TRIP_ACTIONS,
            actions
        )

        self.actions = list(actions)

    def trace(self):
        while self.actions:
            current_trip = [self.grab_step()]

            if current_trip[-1]['tagon']['notes'] == TRANSFER:
                current_trip.extend(self.consume_trip())

            sorted_trip = sorted(
                current_trip,
                key=lambda step: step['tagon']['time']
            )

            current_trip = {
                'steps': list(sorted_trip),
                'meta': self.generate_meta(current_trip),
                'path': self.determine_path(sorted_trip)
            }

            yield current_trip

    def consume_trip(self):
        current_trip = [self.grab_step()]
        while self.actions and current_trip[-1]['tagon']['notes'] == TRANSFER:
            current_trip.append(self.grab_step())

        return current_trip

    def grab_step(self):
        return {
            'tagoff': self.actions.pop(0),
            'tagon': self.actions.pop(0)
        }

    def determine_path(self, trip):
        path_steps = [None]

        for step in trip:
            if step['tagon'] != path_steps[-1]:
                path_steps.append(step['tagon'])

            if step['tagoff'] != path_steps[-1]:
                path_steps.append(step['tagoff'])

        fmt = '{location} ({service})'.format_map

        return list(map(fmt, path_steps[1:]))

    def generate_meta(self, trip):
        def readable(td):
            from itertools import chain
            td = td.__str__().split(':')
            td = zip(td, ['hours,', 'minutes, and', 'seconds'])
            td = chain.from_iterable(td)
            return ' '.join(td)

        determine_breadth = lambda iterable: reduce(add, iterable)

        travel_time = determine_breadth(
            step['tagoff']['time'] - step['tagon']['time']
            for step in trip
        )

        wait_time = 0
        if len(trip) > 1:
            waiting = []
            qtrip = list(trip)

            while len(qtrip) > 1:
                latter = qtrip.pop(0)['tagoff']
                waiting.append(latter['time'] - qtrip[0]['tagon']['time'])
                print(
                    '\t\t\t\t\t',
                    qtrip[0]['tagon']['location'], qtrip[0]['tagon']['time'],
                    '->',
                    latter['location'], latter['time'],
                )

            print('\n')

            wait_time = determine_breadth(waiting)

        return {
            'from': trip[0]['tagon']['location'],
            'to': trip[-1]['tagon']['location'],
            'travel_time': travel_time,
            'wait_time': wait_time
        }


def determine_trips(actions):
    return TripTracer(actions).trace()
