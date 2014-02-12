
from pprint import pprint

BASE = 'http://www.transperth.wa.gov.au/'


def main():
    from .location import Location
    from .fares import get_fare

    routes = get_fare(
        Location.from_location('Esplanade'),
        Location.from_location('Curtin University, Perth')
    )

    pprint(routes)


if __name__ == '__main__':
    main()
