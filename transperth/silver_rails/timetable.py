"""
Contributed by blha303

API key can be retrieved from the android app with Root Browser
(/data/data/au.gov.wa.pta.transperth/com.jeppesen.transperth.xml)

Please don't abuse this service, you'll ruin it for the rest of us.
"""

from lxml.etree import fromstring
import datetime
import dateutil.parser
import logging
import requests

from . import BASE
from .utils import prepare_url

logging.basicConfig(level=logging.DEBUG)


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
    xml = fromstring(xml)

    status = xml.xpath('Status')[0]
    severity = status.xpath("Severity/text()")[0]
    if severity != "Success":

        code = status.xpath("Details/StatusDetail/Code/text()")[0]
        if code == "APIKeyDailyLimitExceeded":
            raise RateLimitExceeded()

        raise Exception("{} fetching {}".format(
            severity,
            stop_num
        ))

    return _parse_timetable_response(xml)


def _parse_timetable_response(xml):
    return [
        (
            b.xpath("Summary/RouteCode/text()")[0],
            dateutil.parser.parse(b.xpath("DepartTime/text()")[0])
        )
        for b in xml.xpath('Trips/StopTimetableTrip')
    ]
