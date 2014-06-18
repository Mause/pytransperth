"""
Contributed by blha303

API key can be retrieved from the android app with Root Browser
(/data/data/au.gov.wa.pta.transperth/com.jeppesen.transperth.xml)

Please don't abuse this service, you'll ruin it for the rest of us.
"""

import datetime
import dateutil.parser
import logging
import requests
import xml.etree.ElementTree as ET

from . import BASE
from .utils import prepare_url

logging.basicConfig(level=logging.DEBUG)


# included here because the pypi installer is broken
class XML2Dict(object):
    def __init__(self, coding='UTF-8'):
        self._coding = coding

    def _parse_node(self, node):
        tree = {}
        # Save childrens
        for child in node.getchildren():
            ctag = child.tag
            cattr = child.attrib
            ctext = (
                child.text.strip()  # .encode(self._coding)
                if child.text is not None else ''
            )
            ctree = self._parse_node(child)
            if not ctree:
                cdict = self._make_dict(ctag, ctext, cattr)
            else:
                cdict = self._make_dict(ctag, ctree, cattr)
            if ctag not in tree:  # First time found
                tree.update(cdict)
                continue
            atag = '@' + ctag
            atree = tree[ctag]
            if not isinstance(atree, list):
                if not isinstance(atree, dict):
                    atree = {}
                if atag in tree:
                    atree['#'+ctag] = tree[atag]
                    del tree[atag]
                tree[ctag] = [atree]  # Multi entries, change to list
            if cattr:
                ctree['#'+ctag] = cattr
            tree[ctag].append(ctree)
        return tree

    def _make_dict(self, tag, value, attr=None):
        ret = {tag: value}
        # Save attributes as @tag value
        if attr:
            atag = '@' + tag
            aattr = {}
            for k, v in attr.items():
                aattr[k] = v
            ret[atag] = aattr
            del atag
            del aattr
        return ret

    def parse(self, xml):
        EL = ET.fromstring(xml)
        return self._make_dict(EL.tag, self._parse_node(EL), EL.attrib)


class RateLimitExceeded(Exception):
    pass


def timetable_for_stop(
        stop_num: int, time: datetime.datetime,
        apikey: str,
        dataset='PerthRestricted'):
    """
    Produces a list of 2 long tuples; (<bus_num>, <time>)
    """

    url = BASE + "/rest/Datasets/:dataset/StopTimetable"
    url = prepare_url(url, {'dataset': dataset})

    req = requests.get(
        url,
        params={
            "stop": stop_num,
            "time": time.strftime('%Y-%m-%dT%H:%M'),
            "ApiKey": apikey,
            "timeband": "1440"
        }
    )

    xml = req.text
    xml = xml.replace('xmlns="http://www.jeppesen.com/journeyplanner" ', "")

    xml = XML2Dict().parse(xml)
    xml = xml["StopTimetableResponse"]

    status = xml['Status']
    if status["Severity"] != "Success":
        details = status["Details"]

        from pprint import pprint
        pprint(details)
        if details["StatusDetail"]["Code"] == "APIKeyDailyLimitExceeded":
            raise RateLimitExceeded()

        raise Exception("{} fetching {}".format(
            xml["Status"]["Severity"],
            stop_num
        ))

    return _parse_timetable_response(xml)


def _parse_timetable_response(xml):
    return [
        (
            b["Summary"]["RouteCode"],
            dateutil.parser.parse(b["DepartTime"])
        )
        for b in xml["Trips"]["StopTimetableTrip"]
    ]
