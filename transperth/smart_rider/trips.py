"""
Parses actions into separate trips
"""
from functools import reduce
from operator import add
import datetime

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
        """
        Consumes the provided actions, yielding trips consisting of stepss
        """
        while self.actions:
            current_trip = [self.grab_step()]

            if current_trip[-1]['tagon']['notes'] == TRANSFER:
                current_trip.extend(self.consume_trip())

            sorted_trip = sorted(
                current_trip,
                key=lambda step: step['tagon']['time']
            )
            sorted_trip = list(sorted_trip)

            yield {
                'steps': sorted_trip,
                'meta': self.generate_meta(sorted_trip),
                'path': self.determine_path(sorted_trip)
            }

    def determine_price(self, trip):
        # we negate the price to get a positive number, so the when summed
        # we get a positive price

        return sum(map(
            lambda step: -step['tagoff']['amount'],
            trip
        ))

    def consume_trip(self) -> list:
        """
        Consumes a single trip, bar the first step
        """
        current_trip = [self.grab_step()]
        while self.actions and current_trip[-1]['tagon']['notes'] == TRANSFER:
            current_trip.append(self.grab_step())

        return current_trip

    def grab_step(self) -> dict:
        """
        :returns: a dictionary representing the step
        """
        return {
            'tagoff': self.actions.pop(0),
            'tagon': self.actions.pop(0)
        }

    def determine_path(self, trip: list) -> list:
        path_steps = [None]

        for step in trip:
            if step['tagon'] != path_steps[-1]:
                path_steps.append(step['tagon'])

            if step['tagoff'] != path_steps[-1]:
                path_steps.append(step['tagoff'])

        fmt = '{location} ({service})'.format_map

        return list(map(fmt, path_steps[1:]))

    def generate_meta(self, trip: list) -> dict:
        """
        Computes the following;

         * from location (for the trip)
         * to location (for the trip)
         * trip duration
         * wait time between steps. this is zero on single step trips
         * total price for the trip

        :returns: metadata for a trip
        """
        determine_breadth = lambda iterable: reduce(add, iterable)

        travel_time = determine_breadth(
            step['tagoff']['time'] - step['tagon']['time']
            for step in trip
        )
        travel_time = timedelta_repr(travel_time)

        wait_time = datetime.timedelta()
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
            'wait_time': timedelta_repr(wait_time),
            'price': self.determine_price(trip)
        }


def timedelta_repr(td: datetime.timedelta) -> str:
    """
    :returns: a human readable represation of the provided timedelta object
    """
    assert isinstance(td, datetime.timedelta), type(td)
    ZERO = {'00', '0'}

    td = td.__str__().split(':')

    end = []
    if td[0] not in ZERO:
        end.append('{} hours'.format(td[0]))

    if td[1] not in ZERO:
        end.append('{} minutes'.format(td[1]))

    if td[2] not in ZERO:
        end.append('{} seconds'.format(td[2]))

    if len(end) > 1:
        end.append('and ' + end.pop(-1))

    return ', '.join(
        val.lstrip('0')
        for val in end
    )


def determine_trips(actions):
    return TripTracer(actions).trace()
