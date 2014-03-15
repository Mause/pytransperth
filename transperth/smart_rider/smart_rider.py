#!/usr/bin/venv python
"""
Based off the code that blha303 (http://github/blha303) provided me with
"""

from dateutil.parser import parse as date_parse
from itertools import chain
from datetime import datetime
import logging
import re

from lxml import html
import requests

from .. import BASE_HTTPS
from ..exceptions import NotLoggedIn, LoginFailed
from .post_back import PageRequestManager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TransperthSession(object):
    """
    Provides an interface to the sections on the transperth website
    that require authentication.
    """
    SR_NAME_RE = re.compile(r'(?:([A-Za-z\W]+)\W+)?(\d+)?')

    def __init__(self, session: requests.Session):
        self.session = session
        self._smart_riders = None
        self._smart_rider_document = None
        self._smart_rider_form = None

        self.request_managers = {}

    def get_rqm(self, url: str):
        """
        :returns: PageRequestManager instance with a url and the urls \
        content, or a previous version if one had already been requested for \
        that url
        """
        if url not in self.request_managers:

            r = self.session.get(
                BASE_HTTPS + url
            )

            if '?returnurl=' in r.url:
                raise NotLoggedIn('Not logged in')

            self.request_managers[url] = PageRequestManager(url)
            self.request_managers[url].load_document(
                html.document_fromstring(r.text)
            )

        return self.request_managers[url]

    def smart_rider_request_manager(self):
        return self.get_rqm(
            'TravelEasy/MySmartRider.aspx'
        )

    def fire_event(self, event_code: str, extra_params: dict=None) -> dict:
        """
        Fires an event at the ASP.net backend.
        """
        assert len(self.smart_rider_request_manager().document.forms) > 0, (
            self.smart_rider_request_manager().document.forms
        )

        return self.smart_rider_request_manager().post_back(
            self.session,
            event_code,
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
                    'name': name,
                    'default': False
                }

            default = select.xpath('//option[@selected="selected"]')
            if default:
                default = default[0]
                name, number = self.SR_NAME_RE.search(option.text).groups()

                self._smart_riders[number]['default'] = True

        return self._smart_riders

    def get_actions(self, sr_code: str, date_from, date_to):
        """
        :returns: a generator yielding action for the provided smart rider
        """
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

        def yield_pages(remaining_pages):
            for key, action_code in remaining_pages:
                yield action_page(action_code)['actions']

        # we must request the first page, so that we can get the number of
        # pages we can request later
        page_one = action_page()

        remaining_pages = self._sort_pages(page_one['pages'])[1:]

        pages = chain(
            [page_one['actions']],
            yield_pages(remaining_pages)
        )

        return chain.from_iterable(pages)

    def _sort_pages(self, pages):
        remaining_pages = {
            key: value
            for key, value in pages.items()
            if key != '...'
        }

        logging.info('Pages: {}'.format(
            ', '.join(sorted(remaining_pages.keys()))
        ))

        return list(sorted(
            remaining_pages.items(),
            key=lambda x: int(x[0])
        ))

    def _send_smart_rider_activites_request(
            self, code: str, date_from: datetime,
            date_to: datetime, action_code: str=None) -> dict:
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

        return self.fire_event(action_code, extra_params)


def login(username: str, password: str) -> TransperthSession:
    """
    :returns: a session object with login cookies attached
    """
    logger.info('Authenticating...')

    s = requests.Session()

    r = _login(s, username, password)

    doc = html.document_fromstring(r.text)
    message = doc.get_element_by_id("dnn_ctr2099_ctl00_lblMessage", [])
    if message != []:
        raise LoginFailed(message.text)

    elif not r.url.endswith('Home.aspx'):
        raise LoginFailed('Login failed: {}'.format(r.url))

    return TransperthSession(s)


def _login(session: requests.Session, email: str, password: str):
    """
    Performs actual login
    """
    return session.post(
        BASE_HTTPS + "Default.aspx?tabid=69",
        data={
            "txtUsername_2099": email,
            "txtPassword_2099": password,
            "__EVENTTARGET": "UserLogin",
        }
    )

STOP_RE = re.compile(r'(?<=\W)St (\d+)(?=\W)?')

REPLACEMENTS = [
    # generics
    (" A ", " after "),
    (" B ", " before "),
    ('nnn', 'annin'),

    # abbreviations
    ('Brdge', 'Bridge'),
    ('Stn', 'Station'),

    # laziness
    ('Bsprt', 'Esplanade Busport'),
    ('Alxndr', 'Alexander'),
    ('Albny', 'Albany'),
    ('Brrndh', 'Burrendah'),
    ('Pinetreerd', 'Pinetree Rd'),
    ('Sth', 'South'),
    ('Wlnn', 'Walanna'),
    ('Lown', 'Lowan Loop '),
    ('Frmntl', 'Freemantle'),
    ('Ccl', 'Cecil'),
    ('Armdle', 'Armadale'),
    ('Chdwck', 'Chadwick'),
    ('Chrch', 'Church'),
    ('Brslm', 'Burslem'),
    ('Klvn', 'Kelvin'),
    ('Nnth', 'Ninth')
]


def mend_location(string: str) -> str:
    """
    For display, the transperth website brutalises the location names somewhat,
    removing entire words or simply shortening them.

    These tend to be uniform, so this function attempts to clean them up.
    """
    string = string.title()

    for old, new in REPLACEMENTS:
        string = string.replace(old, new)

    return STOP_RE.sub(
        lambda match: 'Stop {}'.format(match.groups()[0]),
        string
    )


def _get_items(doc):
    items = doc.xpath(
        "//table[@class='rgMasterTable']/"  # pull out the table
        "tbody/"                            # grab the body of the table
        "tr/td/"                            # grab the rows
        "text()"                            # grab the text of the rows
    )
    items = list(map(str.strip, items))

    while items:
        yield [items.pop(0) for _ in range(8)]


def _total_actions(doc):
    "pulls out the total number of actions for the date range"
    pagination = doc.xpath("//div[@class='rgWrap rgInfoPart']")[0]
    return int(list(pagination.itertext())[1])


def _pages(doc):
    "pulls out the pages and their action codes"
    div = doc.xpath("//div[@class='rgWrap rgNumPart']")[0]
    return {
        anchor[0].text: anchor.attrib['href'].split("'")[1]
        for anchor in div
    }


def _get_smart_rider_actions(root: str) -> dict:
    root = html.document_fromstring(root)

    actions = []
    for action in _get_items(root):
        actions.append({
            'time': datetime.strptime(action[0].strip(), '%d/%m/%Y %H:%M:%S'),
            'action': action[1],
            'location': mend_location(action[2]),
            'service': action[3],
            'zone': action[4],
            'amount': float(action[5]) if action[5] else 0,
            'balance': float(action[6]),
            'notes': action[7]
        })

    return {
        'actions': actions,
        'actions_total': _total_actions(root),
        'pages': _pages(root)
    }

SR_NUM_RE = re.compile(r'(\d{4})(\d{4})(\d)')


def smartrider_format(string):
    """
    Formats the smart rider number as per transperth convention;

    .. code-block:: text

        SR XXXX XXXX X

    whereby the X's represent the corresponding numbers from the smart rider
    number
    """
    return 'SR {} {} {}'.format(
        *SR_NUM_RE.match(string).groups()
    )
