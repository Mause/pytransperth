TAG_OFF = 'Normal TAG OFF'
TAG_ON = 'Normal TAG ON'
TRANSFER = 'Transfer'


class TripTracer(object):
    def __init__(self, actions):
        actions = filter(
            lambda action: action['action'] in [TAG_OFF, TAG_ON],
            actions
        )

        self.actions = list(actions)

    def trace(self):
        while self.actions:
            current_trip = [self.grab_step()]

            if current_trip[-1]['tagon']['notes'] == TRANSFER:
                current_trip.extend(self.consume_trip())

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


def determine_trips(actions):
    return TripTracer(actions).trace()
