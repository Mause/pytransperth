from dateutil.parser import parse as date_parse
from itertools import chain
from lxml import html, etree
import datetime
import re
import time

DURATION_RE = re.compile(r'(\d+):(\d+) hrs')
FUNCTIONCALL_RE = re.compile(r'(\w+)\(([^\)]*)\)')
ARGUMENT_RE = re.compile(r'''(['"][^'"]*['"]|[-\d]+)''')
TIME_RE = re.compile(r'(\d+:\d+ (?:AM|PM))')


def parse_routes(text):
    """
    Top level function of this parsing module.

    Because we are parsing complex html intended to be rendered in
    a browser for a user, the parsing code is itself quite complex.

    An attempt at modularisation has been made.
    """

    root = html.document_fromstring(text)

    # grab the journey planner results table
    tables = root.xpath("//div[@class='ModJourneyPlannerResultsC']/table")

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

    return routes


def _parse_header(header):
    header, misc = header.find('td/table')

    duration, links = header.findall('td')

    return {
        'duration': _parse_duration(duration),
        'links': _parse_links(links),
        'misc': _parse_misc(misc)
    }


def _parse_links(links):
    links = links.find('div')
    links = links.xpath('.//img')

    return dict(
        map(_parse_img, links)
    )


def _parse_img(img):
    onclick = img.get('onclick')

    name, args = FUNCTIONCALL_RE.match(onclick).groups()

    args = ARGUMENT_RE.findall(args)

    return name, args


def _parse_duration(duration):
    duration = duration.find('span')
    duration = list(duration.itertext())[1]

    hours, minutes = map(int, DURATION_RE.findall(duration)[0])

    return datetime.timedelta(hours=hours, minutes=minutes)


def _parse_misc(misc):
    miscs = misc.findall('td')

    misc_data = {}

    for misc in miscs[1:-1]:
        texts = misc.itertext()
        texts = list(map(str.strip, texts))

        texts = zip(texts[::2], texts[1::2])

        for k, v in texts:
            k = k[:-1].replace(' ', '_').lower()

            misc_data[k] = v

    misc_data['arrival_time'] = date_parse(misc_data['arrival_time'])
    misc_data['depart_time'] = date_parse(misc_data['depart_time'])
    misc_data['number_of_legs'] = int(misc_data['number_of_legs'])
    misc_data['total_walking_distance'] = int(
        misc_data['total_walking_distance'][:2]
    )

    return misc_data


def _parse_steps(steps):
    steps = steps[1].xpath('td/div/table')

    return list(map(_parse_step, steps[:1]))


def _parse_step(step):
    parts = step.find('tr').findall('td')

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


def _parse_bus_step(texts):
    step = {
        'step_type': 'bus',
        'route': texts.pop(-1)[8:]
    }

    texts = list(zip(texts[::2], texts[1::2]))

    dep, arr = {}, {}

    dep['time'], arr['time'] = map(_parse_time, texts.pop(0))

    dep['stop_name'], dep['stop_num'] = texts.pop(0)
    arr['stop_name'], arr['stop_num'] = texts.pop(0)

    dep['stop_num'] = _parse_stop(dep['stop_num'])
    arr['stop_num'] = _parse_stop(arr['stop_num'])

    step.update({
        'departure': dep,
        'arrival': arr
    })

    return step


def _parse_walk_step(texts):
    return {
        'step_type': 'walk',
        'departure': _parse_time(texts[1]),
        'walking_distance': int(texts[0].split(' ')[0])
    }


def _parse_time(string):
    string = TIME_RE.search(string).groups()[0]

    t = time.strptime(string, '%I:%M %p')

    return datetime.time(
        hour=t.tm_hour,
        minute=t.tm_min
    )


def _parse_stop(string):
    return int(string.split(' ')[2][:-1])
