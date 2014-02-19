from itertools import chain
from lxml import html, etree
import datetime
import re
import time

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
            msg = 'Steps parsed incorrectly: {} != {}'.format(
                header['misc']['number_of_legs'],
                len(steps)
            )
            raise Exception(msg)

    return routes


def _parse_header(header) -> dict:
    """
    Parses the route duration, links (fare and map data), and misc. data
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
    """

    # TODO: check if these can be melded
    links = links.find('div')
    links = links.xpath('.//img')

    return dict(
        map(_parse_img, links)
    )


def _parse_img(img) -> tuple:
    """
    Grabs the onclick attribute of the given `<img/>`
    """
    onclick = img.get('onclick')

    name, args = FUNCTIONCALL_RE.match(onclick).groups()

    clean_args = []
    for arg in map(str.strip, args.split(',')):
        if arg[0] == arg[-1] and arg[0] in {'"', "'"}:
            clean_args.append(arg[1:-1])
        else:
            clean_args.append(int(arg))

    return name, clean_args


def _parse_duration(duration) -> datetime.timedelta:
    duration = duration.find('span')
    duration = list(duration.itertext())[1]

    hours, minutes = map(int, DURATION_RE.findall(duration)[0])

    return datetime.timedelta(hours=hours, minutes=minutes)


_normalise_key = lambda key: key.replace(' ', '_').lower()


def _parse_misc(misc) -> dict:
    miscs = misc.findall('td')[1:-1]

    miscs = map(etree._Element.itertext, miscs)

    misc_data = {}
    for misc in miscs:
        misc = [part.strip() for part in misc]

        misc = zip(misc[::2], misc[1::2])

        for k, v in misc:
            k = _normalise_key(k[:-1])

            misc_data[k] = v

    misc_data.update({
        'arrival_time': _parse_time(misc_data['arrival_time']),
        'depart_time': _parse_time(misc_data['depart_time']),
        'number_of_legs': int(misc_data['number_of_legs']),
        'total_walking_distance': int(
            misc_data['total_walking_distance'][:2]
        )
    })

    return misc_data


def _parse_steps(steps) -> list:
    steps = steps[1].xpath('td/div/table')

    return list(map(_parse_step, steps))


def _parse_step(step) -> dict:
    parts = step.xpath('tr/td')

    step_type = parts.pop(0).xpath('img/@alt')[0].lower()

    texts = map(etree._Element.itertext, parts)
    texts = chain.from_iterable(texts)
    texts = map(str.strip, texts)
    texts = filter(bool, texts)

    # islice wont work here because it doesn't know
    # how long the iterator it is consuming is
    texts = list(texts)[:-1]

    if step_type == 'bus':
        return _parse_bus_step(texts)
    elif step_type == 'walk':
        return _parse_walk_step(texts)
    elif step_type == 'train':
        return _parse_train_step(texts)
    else:
        raise Exception(step_type)


def _parse_bus_step(texts: str) -> dict:
    route = texts.pop(-1)[8:]
    texts = list(zip(texts[::2], texts[1::2]))

    dep, arr = {}, {}
    dep['time'], arr['time'] = map(_parse_time, texts.pop(0))

    dep['stop_name'], dep['stop_num'] = texts.pop(0)
    arr['stop_name'], arr['stop_num'] = texts.pop(0)

    dep['stop_num'] = _parse_stop(dep['stop_num'])
    arr['stop_num'] = _parse_stop(arr['stop_num'])

    return {
        'step_type': 'bus',
        'route': route,
        'departure': dep,
        'arrival': arr
    }


def _parse_train_step(texts: str) -> dict:
    route = texts.pop(-1)[8:]
    texts = list(zip(texts[::2], texts[1::2]))

    # train steps are different from bus steps in that they don't have stop
    # numbers, only stop names

    dep, arr = {}, {}
    dep['time'], arr['time'] = map(_parse_time, texts.pop(0))
    dep['stop_name'], arr['stop_name'] = texts.pop(0)

    return {
        'step_type': 'train',
        'route': route,
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
        'departure': departure,
        'walking_distance': int(texts[0].split(' ')[0])
    }


def _parse_time(string: str) -> datetime.time:
    string = TIME_RE.search(string).groups()[0]

    t = time.strptime(string, '%I:%M %p')

    return datetime.time(
        hour=t.tm_hour,
        minute=t.tm_min
    )


def _parse_stop(string: str) -> int:
    # Presuming a stop is represented like this;
    # (Stop number: 26679)
    return int(string.split(' ')[2][:-1])
