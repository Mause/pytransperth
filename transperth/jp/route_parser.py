from itertools import chain
from lxml import html, etree
import datetime
import re
import time

from ..exceptions import InvalidStep

DURATION_RE = re.compile(r'(\d+):(\d+) hrs')
FUNCTIONCALL_RE = re.compile(r'(\w+)\(([^\)]*)\)')
ARGUMENT_RE = re.compile(r'''['"]([^"']*)['"]|[-\d]+''')
TIME_RE = re.compile(r'(\d+:\d+ (?:AM|PM))')

__all__ = ['parse_routes']


def parse_routes(text: str) -> list:
    """
    Top level function of this parsing module.

    Because we are parsing complex html intended to be rendered in
    a browser for a user, the parsing code is itself quite complex.

    An attempt at modularisation has been made.

    :param text: Text of XML tree containing routes
    """

    root = html.document_fromstring(text)

    # grab the journey planner results table
    tables = root.xpath("//div[@class='ModJourneyPlannerResultsC']/table")

    assert len(tables) > 0

    # rid ourselves of the query and error tables
    tables = tables[2:]

    routes = []
    for table in tables:
        header, *steps = table.find('tr/td/table')

        header = _parse_header(header)
        steps = _parse_steps(steps)

        routes.append({
            'meta': header,
            'steps': steps
        })

        if header['misc']['number_of_legs'] != len(steps):
            raise Exception(
                'Steps parsed incorrectly: {} != {}'.format(
                    header['misc']['number_of_legs'],
                    len(steps)
                )
            )

    return routes


def _parse_header(header) -> dict:
    """
    Parses the route duration, links (fare and map data), and misc. data

    :param header: Element tree containing the header
    """

    header, misc = header.find('td/table')

    duration, links = header.findall('td')

    return {
        'duration': _parse_duration(duration),
        'links': _parse_links(links),
        'misc': _parse_misc(misc)
    }


def _parse_links(links) -> dict:
    """
    Grabs all img takes within the `links` element tree, and
    passes them through to _parse_img for parsing

    :param links: Element tree containing links
    :returns: a dictionary mapping functions to their arguments
    """

    # TODO: check if these can be melded
    links = links.find('div')
    links = links.xpath('.//img')

    return dict(
        map(_parse_img, links)
    )


def _parse_img(img: '<img/>') -> tuple:
    """
    Grabs the onclick attribute of the given ``<img/>``
    :param img: An image tag with an onclick handler containing a function call
    """

    onclick = img.get('onclick')

    return _parse_function_call(onclick)


def _parse_function_call(call_string: str) -> tuple:
    """
    :returns: a tuple of the function name and function arguments
    """

    name, args = FUNCTIONCALL_RE.match(call_string).groups()

    clean_args = []
    for arg in map(str.strip, args.split(',')):
        if arg[0] == arg[-1] and arg[0] in {'"', "'"}:
            clean_args.append(arg[1:-1])
        else:
            clean_args.append(int(arg))

    return name, clean_args


def _parse_duration(duration) -> datetime.timedelta:
    """
    :returns: a ``datetime.timedelta`` representing the duration provided
    """
    duration = duration.find('span')
    duration = list(duration.itertext())[1]

    hours, minutes = map(int, DURATION_RE.findall(duration)[0])

    return datetime.timedelta(hours=hours, minutes=minutes)


_normalise_key = lambda key: key.replace(' ', '_').lower()


def _parse_misc(misc) -> dict:
    miscs = misc.findall('td')[1:-1]

    miscs = map(etree._Element.itertext, miscs)
    miscs = chain.from_iterable(miscs)

    miscs = [part.strip() for part in miscs]
    miscs = zip(miscs[::2], miscs[1::2])

    misc_data = {}
    for k, v in miscs:
        k = _normalise_key(k[:-1])

        misc_data[k] = v

    return {
        'arrival_time': _parse_time(misc_data['arrival_time']),
        'depart_time': _parse_time(misc_data['depart_time']),
        'number_of_legs': int(misc_data['number_of_legs']),
        'total_walking_distance': int(
            misc_data['total_walking_distance'][:2]
        )
    }


def _parse_steps(steps) -> list:
    """
    :returns: a list of steps
    """
    steps = steps[1].xpath('td/div/table')

    return list(map(_parse_step, steps))


def _parse_step(step: '<table/>') -> dict:
    """
    Extracts the text from the step, and passes it through to the function
    denoted by the alt attribute of the ``<img/>`` tag

    :returns: a dictionary representing a step
    """
    parts = step.xpath('tr/td')

    step_type = parts.pop(0).xpath('img/@alt')[0].lower()

    texts = map(etree._Element.itertext, parts)
    texts = chain.from_iterable(texts)
    texts = map(str.strip, texts)
    texts = filter(bool, texts)

    # islice wont work here because it doesn't know
    # how long the iterator it is consuming is
    texts = list(texts)[:-1]

    if step_type in {'bus', 'train'}:
        route = texts.pop(-1)[8:]
        texts = list(zip(texts[::2], texts[1::2]))

        step = {
            'bus': _parse_bus_step,
            'train': _parse_train_step
        }[step_type](texts)

        step['route'] = _parse_route_text(route)

        return step

    elif step_type == 'walk':
        return _parse_walk_step(texts)
    else:
        raise InvalidStep(step_type)


ROUTE_TEXT_RE = re.compile(
    r'(?:(?P<route_moniker>[\dA-Za-z\s]*) )?(?:\((?P<flags>[A-Za-z|]+)\) )?'
    r'(?P<from>[^(-]*) - (?P<to>.*)'
)


def _parse_route_text(string):
    match = ROUTE_TEXT_RE.match(string)

    if match:
        route_info = match.groupdict()

        if route_info['flags']:
            route_info['flags'] = route_info['flags'].split('|')

        if 'Departs' in route_info['to']:
            route_info['to'], route_info['departs'] = route_info['to'].split(
                ' Departs '
            )

    return route_info if match else {'route_moniker': string}


def _parse_bus_step(texts: str) -> dict:
    dep, arr = {}, {}
    dep['time'], arr['time'] = map(_parse_time, texts.pop(0))

    dep['stop_name'], dep['stop_num'] = texts.pop(0)
    arr['stop_name'], arr['stop_num'] = texts.pop(0)

    dep['stop_num'] = _parse_stop(dep['stop_num'])
    arr['stop_num'] = _parse_stop(arr['stop_num'])

    return {
        'step_type': 'bus',
        'departure': dep,
        'arrival': arr
    }


def _parse_train_step(texts: str) -> dict:
    # train steps are different from bus steps in that they don't have stop
    # numbers, only stop names

    dep, arr = {}, {}
    dep['time'], arr['time'] = map(_parse_time, texts.pop(0))
    dep['stop_name'], arr['stop_name'] = texts.pop(0)

    return {
        'step_type': 'train',
        'departure': dep,
        'arrival': arr
    }


def _parse_walk_step(texts: str) -> dict:
    departure = (
        _parse_time(texts[1]) if len(texts) > 1
        else None
    )

    return {
        'step_type': 'walk',
        'departure': {'time': departure},
        'walking_distance': int(texts[0].split(' ')[0])
    }


def _parse_time(string: str) -> datetime.time:
    """
    :returns: the parsed time
    """
    string = TIME_RE.search(string.strip()).groups()[0]

    t = time.strptime(string, '%I:%M %p')

    return datetime.time(
        hour=t.tm_hour,
        minute=t.tm_min
    )


def _parse_stop(string: str) -> int:
    # Presuming a stop is represented like this;
    # (Stop number: 26679)
    return int(string.split(' ')[2][:-1])
