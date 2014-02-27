#!/usr/bin/venv python
"""
Based off the code that blha303 (http://github/blha303) provided me with
"""

from dateutil.parser import parse as date_parse
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


class TransperthSession(object):
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
            select = self.smart_rider_document().get_element_by_id(
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

    def smart_rider_document(self):
        if self._smart_rider_document is None:
            r = self.session.get(
                BASE + "TravelEasy/MySmartRider/tabid/71/Default.aspx"
            )
            self._smart_rider_document = html.document_fromstring(r.text)

        return self._smart_rider_document

    def smart_rider_form(self):
        if self._smart_rider_form is None:
            self._smart_rider_form = self.smart_rider_document().forms[0]

        return self._smart_rider_form

    def get_activities(self, sr_code):
        date_from, date_to = date_parse('01/01/2010'), date_parse('01/01/2015')

        updates = post_back(
            self.session,
            self.smart_rider_document(),
            self.smart_rider_form(),
            sr_code,
            date_from,
            date_to
        )

        assert self.session
        assert self.smart_rider_document is not None
        assert self.smart_rider_form is not None

        return _get_smart_rider(
            updates['updatePanel'][1]['content']
        )



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

    string = re.sub(
        r'\WSt (\d+)\W',
        lambda match: 'Stop {}'.format(match.groups()[0]),
        string
    )

    string = re.sub(
        r'\WS(\d+)\W',
        lambda match: 'Stop {}'.format(match.groups()[0]),
        string
    )

    return string


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
            'amount': 0 if action[5] == '\xa0' else action[5],
            'balance': float(action[6]),
            'notes': action[7]
        })

    pagination = root.xpath("//div[@class='rgWrap rgInfoPart']")[0]
    items = int(list(pagination.itertext())[1])

    return {
        'actions': actions,
        'actions_total': items
    }
