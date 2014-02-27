#!/usr/bin/venv python
"""
Based off the code that blha303 (http://github/blha303) provided me with
"""

from dateutil.parser import parse as date_parse
import datetime
from itertools import chain
from pprint import pprint
import logging
import re

from lxml import html, etree
import requests


from .post_back import PageRequestManager
from .. import BASE_HTTPS
from ..exceptions import NotLoggedIn


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TransperthSession(object):
    """
    Provides an interface to the sections on the transperth website
    that require authentication.
    """
    SR_NAME_RE = re.compile(r'(?:\W+([A-Za-z\W]+)\W+)?(\d+)(?:\W+)?')

    def __init__(self, session: requests.Session):
        self.session = session
        self._smart_riders = None
        self._smart_rider_document = None
        self._smart_rider_form = None

        self._request_managers = {}

    def get_rqm(self, url):
        if url not in self._request_managers:

            r = self.session.get(
                BASE_HTTPS + url
            )

            if '?returnurl=' in r.url:
                raise NotLoggedIn('Not logged in')

            self._request_managers[url] = PageRequestManager(
                url,
                html.document_fromstring(r.text)
            )

        return self._request_managers[url]

    def smart_rider_request_manager(self):
        return self.get_rqm(
            # "TravelEasy/MySmartRider/tabid/71/Default.aspx"
            'TravelEasy/MySmartRider.aspx'
        )

    def fire_action(self, action_code: str, extra_params: dict=None) -> dict:
        """
        Fires an `action` into the abyss.
        """
        assert len(self.smart_rider_request_manager().document.forms) > 0, (
            self.smart_rider_request_manager().document.forms
        )

        return self.smart_rider_request_manager().post_back(
            self.session,
            action_code,
            extra_params
        )

    def smart_riders(self) -> dict:
        if not self._smart_riders:
            doc = self.smart_rider_request_manager().document
            select = doc.get_element_by_id(
                'dnn_ctr2061_SmartRiderTransactions_ddlSmartCardNumber'
            )

            self._smart_riders = {}
            for option in select:
                name, number = self.SR_NAME_RE.search(option.text).groups()

                self._smart_riders[number] = {
                    'code': option.get('value'),
                    'name': name
                }

        return self._smart_riders

    def get_actions(self, sr_code: str):
        def action_page(action_code=None):
            updates = self._send_smart_rider_activites_request(
                sr_code,
                date_from,
                date_to,
                action_code=action_code
            )
            return _get_smart_rider_actions(
                updates['updatePanel'][1]['content']
            )

        def pages(remaining_pages):
            for key, action_code in remaining_pages:
                yield action_page(action_code)['actions']

        date_from, date_to = date_parse('01/01/2010'), date_parse('01/01/2015')

        page_one = action_page()

        remaining_pages = sorted(
            page_one['pages'].items(),
            key=lambda x: int(x[0])
        )
        remaining_pages = list(remaining_pages)[1:]

        print('remaining_pages:', remaining_pages)

        for page in chain([page_one['actions']], pages(remaining_pages)):
            for activity in page:
                yield activity

    def _send_smart_rider_activites_request(
            self, code: str, date_from: datetime.datetime,
            date_to: datetime.datetime, action_code: str=None) -> dict:
        # add in date range
        extra_params = {
            'dnn$ctr2061$SmartRiderTransactions$rdFromDate': (
                date_from.strftime('%Y-%m-%d')
            ),
            'dnn$ctr2061$SmartRiderTransactions$rdFromDate$dateInput': (
                date_from.strftime('%Y-%m-%d-00-00-00')
            ),
            'dnn$ctr2061$SmartRiderTransactions$rdToDate': (
                date_to.strftime('%Y-%m-%d')
            ),
            'dnn$ctr2061$SmartRiderTransactions$rdToDate$dateInput': (
                date_to.strftime('%Y-%m-%d-00-00-00')
            ),
            'dnn_ctr2061_SmartRiderTransactions_rdFromDate_calendar_AD': (
                date_from.strftime('[[1980,1,1],[2099,12,30],[%Y,%m,%d]]')
            ),
            'dnn_ctr2061_SmartRiderTransactions_rdToDate_calendar_AD': (
                date_to.strftime('[[1980,1,1],[2099,12,30],[%Y,%m,%d]]')
            ),
        }

        # add in smart rider card selection, for those special few with
        # more than one
        extra_params.update({
            'dnn$ctr2061$SmartRiderTransactions$ddlSmartCardNumber': code
        })

        action_code = action_code or (
            "dnn$"
            "ctr2061$"
            "SmartRiderTransactions$"
            "rgTransactions$"
            "ctl00$"
            "ctl02$"
            "ctl00$"
            "ctl00"
        )

        return self.fire_action(action_code, extra_params)


def login(username: str, password: str) -> TransperthSession:
    logger.info('Authenticating...')

    s = requests.Session()

    r = _login(s, username, password)

    doc = html.document_fromstring(r.text)
    message = doc.xpath("//span[@class='dnn_ctr2099_ctl00_lblMessage']")
    if message:
        print(message[0].text)

    print('Title:', doc.xpath('.//title')[0].text)

    assert r.url.endswith('Home.aspx'), 'Login failed: {}'.format(r.url)

    return TransperthSession(s)


def _login(session: requests.Session, email: str, password: str):
    return session.post(
        "https://www.transperth.wa.gov.au/Default.aspx?tabid=69",
        data={
            "txtUsername_2099": email,
            "txtPassword_2099": password,
            "__EVENTTARGET": "UserLogin",
        }
    )

STOP_RE = re.compile(r'(?<=\W)St (\d+)(?=\W)?')


def mend_location(string: str) -> str:
    """
    For display, the transperth website brutalises the location names somewhat,
    removing entire words or simply shortening them.

    These tend to be uniform, so this function attempts to clean them up.
    """
    string = (
        string
        .title()
        .replace(" A ", " after ")
        .replace(" B ", " before ")
        .replace('nnn', 'annin')
        .replace('NNN', 'ANNIN')
        .replace('Brdge', 'Bridge')
        .replace('Bsprt', 'Esplanade Busport')
    )

    print(STOP_RE.findall(string), string)

    return STOP_RE.sub(
        lambda match: 'Stop {}'.format(match.groups()[0]),
        string
    )


def _get_smart_rider_actions(root: str) -> dict:
    root = html.document_fromstring(root)

    table = root.xpath("//table[@class='rgMasterTable']")[0]

    rows = table.find('tbody').findall('tr')
    items = (
        map(etree._Element.itertext, row.findall('td'))
        for row in rows
    )
    items = map(chain.from_iterable, items)
    items = map(list, items)

    actions = []
    for action in items:
        action = list(map(str.strip, action))

        actions.append({
            'time': date_parse(action[0] + " +0800"),
            'action': action[1],
            'location': mend_location(action[2]),
            'service': action[3],
            'zone': action[4],
            'amount': float(action[5]) if action[5] else 0,
            'balance': float(action[6]),
            'notes': action[7]
        })

    pagination = root.xpath("//div[@class='rgWrap rgInfoPart']")[0]
    items = int(list(pagination.itertext())[1])

    div = root.xpath("//div[@class='rgWrap rgNumPart']")[0]

    pages = {
        anchor[0].text: anchor.attrib['href'].split("'")[1]
        for anchor in div
    }

    return {
        'actions': actions,
        'actions_total': items,
        'pages': pages
    }
