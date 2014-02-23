#!/usr/bin/venv python
"""
Based off the code that blha303 (http://github/blha303) provided me with
"""

from dateutil.parser import parse as date_parse
from itertools import chain
from pprint import pprint
import json
import logging
import re

from lxml import html, etree
import requests

from post_back import post_back
# from .. import BASE
BASE = 'https://www.transperth.wa.gov.au/'


# we actually need a class for the login part of the website,
# as the session has to be stored somewhere


logging.basicConfig(level=logging.DEBUG)


class TransperthSession(object):
    SR_NAME_RE = re.compile(r'(?:\W+([A-Za-z\W]+)\W+)?(\d+)(?:\W+)?')

    def __init__(self, session):
        self.session = session
        self._smart_riders = None
        self._smart_rider_document = None
        self._smart_rider_form = None

    def smart_riders(self):
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


def login(username, password):
    params = {
        "txtUsername_2099": username,
        "txtPassword_2099": password,
        "__EVENTTARGET": "UserLogin",
        "__EVENTARGUMENT": "",
        "dnn$dnnSEARCH$Search": "optSite",
        "dnn$dnnSEARCH$txtSearch": "",
        "dnn$dnnRADTABSTRIP$TS": {
            "State": {},
            "TabState": {
                "dnn_dnnRADTABSTRIP_TS_TS_69": {
                    "Selected": True
                }
            }
        },
        "dnn$dnnRADPANELBAR$RadPanel1": "",
        "XsltDbGlobals": "%24tabid=69",
        "mdo-hid-i7-value": "",
        "btnLogin_2099": "Login",
        "dnn$ctr2099$DynamicLogin$objDDL": "False",
        "__dnnVariable": {
            "__scdoff": "1",
            "__dnn_pageload": (
                "__dnn_SetInitialFocus(\u0027txtUsername_2099\u0027);"
            )
        }
    }

    s = requests.Session()

    r = s.post(BASE + "Default.aspx?tabid=69", data=params)

    assert r.url.endswith('Home.aspx'), 'Login failed'

    return TransperthSession(s)


def _get_smart_rider(root):
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
        action[2] = (
            action[2]
            .replace(" a ", " after ")
            .replace(" b ", " before")
            .replace('nnn', 'annin')
        )

        actions.append({
            'time': date_parse(action[0] + " +0800"),
            'action': action[1],
            'location': action[2],
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

if __name__ == '__main__':
    import os

    if not os.path.exists('session.json'):
        print('logging in...')

        s = login(*open('auth').read().split(','))

        print('login succesful')

        with open('session.json', 'w') as fh:
            json.dump(s.session.cookies.get_dict(), fh, indent=4)
    else:
        s = requests.Session()
        with open('session.json') as fh:
            s.cookies.update(json.load(fh))
        s = TransperthSession(s)

    riders = s.smart_riders()

    pprint(riders)

    act = s.get_activities('222664')

    pprint(act)