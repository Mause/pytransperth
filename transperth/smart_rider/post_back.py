"""
The code in this file was ported from javascript from the transperth website.

As I progress, I will attempt to whittle it down to purely what is absolutely
required.
"""

from collections import defaultdict

from .. import BASE_HTTPS
from ..jp.utils import clean
from ..jp.route_parser import _parse_function_call, FUNCTIONCALL_RE


def create_post_back_settings(async: str, panel_ID: str, source_element: str):
    return {
        'async': async,
        'panelID': panel_ID,
        'sourceElement': source_element
    }

unique_ID_to_client_ID = lambda a: a.replace('$', '_')


def matches_parent_ID_in_list(c, b):
    for a in b:
        if (c.startswith(a + "_")):
            return True
    return False


def params_from_form(form) -> dict:
    params = {}
    for el in form.xpath('.//input'):
        el_name = el.name
        if not el_name or el_name == "ScriptManager":
            continue

        tag = el.tag.upper()

        if tag == "INPUT":
            el_type = el.type.lower()
            if (el_type in {"text", "password", "hidden"} or
                    el_type in {"checkbox", "radio"} and el.checked):

                params[el_name] = '' if el.value is None else el.value

        elif tag == "SELECT":
            for option in el:
                if option.attrib['selected'] is True:
                    params[el_name] = option.value
            raise Exception()

        elif (tag == "TEXTAREA"):
            params[el_name] = el.value
        else:
            raise Exception(tag)

    return params


def parse_delta(raw_delta: str) -> str:
    """
    Parses the deltas returned by the transperth api to ajax requests.

    They are in the format;

    .. code-block:: none

        content_length|content_type|content_id|content|

    There can be none, one, or many. This function loops until there
    are no more to consume.
    """
    def grab_section(raw_delta, length=None):
        return (
            raw_delta[(length or raw_delta.index('|')) + 1:],
            raw_delta[:(length or raw_delta.index('|'))]
        )

    updates = defaultdict(list)

    while raw_delta:
        raw_delta, length = grab_section(raw_delta)

        raw_delta, frag_type = grab_section(raw_delta)

        raw_delta, frag_id = grab_section(raw_delta)

        raw_delta, content = grab_section(raw_delta, int(length))

        updates[frag_type].append({
            'id': frag_id,
            'content': content
        })

    return updates


class PageRequestManagerOriginal(object):
    def __init__(self, url: str):
        self.url = url
        self.document = None

        self._active_default_button = None
        self._active_default_button_clicked = False
        self._update_panel_IDs = [
            "dnn$ctr2061$SmartRiderTransactions$pnlModuleMessagePanel",
            "dnn$ctr2061$SmartRiderTransactions$pnlSmartRiderBalancePanel",
            "dnn$ctr2061$SmartRiderTransactions$rgTransactionsPanel",
            "dnn$ctr2061$SmartRiderTransactions$rdFromDatePanel",
            "dnn$ctr2061$SmartRiderTransactions$rdToDatePanel",
            "RadAjaxManager1SU"
        ]
        self._update_panel_client_IDs = [
            "dnn_ctr2061_SmartRiderTransactions_pnlModuleMessagePanel",
            "dnn_ctr2061_SmartRiderTransactions_pnlSmartRiderBalancePanel",
            "dnn_ctr2061_SmartRiderTransactions_rgTransactionsPanel",
            "dnn_ctr2061_SmartRiderTransactions_rdFromDatePanel",
            "dnn_ctr2061_SmartRiderTransactions_rdToDatePanel",
            "RadAjaxManager1SU"
        ]
        self._update_panel_has_children_as_triggers = [
            True, True, True, True, True, True
        ]
        self._async_post_back_control_IDs = None
        self._async_post_back_control_client_IDs = [
            "dnn_ctr2061_SmartRiderTransactions_ddlSmartCardNumber",
            "dnn_ctr2061_SmartRiderTransactions_rgTransactions",
            "dnn_ctr2061_SmartRiderTransactions_rdToDate",
            "dnn_ctr2061_SmartRiderTransactions_rdFromDate"
        ]
        self._post_back_control_IDs = None
        self._post_back_control_client_IDs = []
        self._script_manager_ID = None or 'ScriptManager'
        self._page_loaded_handler = None
        self._additional_input = None
        self._onsubmit = None
        self._on_submit_statements = []
        self._original_do_post_back = None
        self._original_do_post_back_with_options = None
        self._original_fire_default_button = None
        self._original_do_callback = None
        self._is_cross_post = False
        self._post_back_settings = None
        self._request = None
        self._on_form_submit_handler = None
        self._on_form_element_click_handler = None
        self._on_window_unload_handler = None
        self._async_post_back_timeout = None
        self._control_ID_to_focus = None
        self._scroll_position = None
        self._processing_request = False
        self._script_disposes = {}
        self._transient_fields = [
            "__VIEWSTATEENCRYPTED",
            "__VIEWSTATEFIELDCOUNT"
        ]

    @property
    def _form(self):
        return self.document.forms[0]

    def load_document(self, document):
        self.document = document
        self.initalise_from_document()

    def find_nearest_element(self, target_id):
        """
        Find the nearest element as consider by the path dictated by
        `target_id`
        """
        while target_id:
            el_id = unique_ID_to_client_ID(target_id)
            el = self.document.get_element_by_id(el_id, None)

            if el is not None:
                return el

            if '$' not in target_id:
                return None

            # remove the latter most section
            target_id = '$'.join(
                target_id.split('$')[:-1]
            )

        return None

    def get_post_back_settings(self, a, c):
        d = a
        b = None
        while a is not None:
            if a.attrib.get('id'):
                if (not b and
                        a.attrib['id'] in self._async_post_back_control_client_IDs):
                    b = create_post_back_settings(
                        True,
                        self._script_manager_ID + '|' + c,
                        d
                    )
                elif (not b and
                        a.attrib['id'] in self._post_back_control_client_IDs):
                    return create_post_back_settings(False, None, None)
                else:
                    if a.attrib['id'] in self._update_panel_client_IDs:
                        e = self._update_panel_client_IDs.index(a.attrib['id'])
                    else:
                        e = -1

                    if e != -1:
                        if (self._update_panel_has_children_as_triggers[e]):
                            return create_post_back_settings(
                                True,
                                self._update_panel_IDs[e] + "|" + c,
                                d
                            )
                        else:
                            return create_post_back_settings(
                                True,
                                self._script_manager_ID + '|' + c,
                                d
                            )

                if not b:
                    if matches_parent_ID_in_list(
                            a.attrib['id'],
                            self._async_post_back_control_client_IDs):
                        b = create_post_back_settings(
                            True,
                            self._script_manager_ID + '|' + c,
                            d
                        )
                    elif matches_parent_ID_in_list(
                            a.attrib['id'],
                            self._post_back_control_client_IDs):
                        return create_post_back_settings(False, None, None)

            a = a.getparent()

        if (not b):
            return create_post_back_settings(False, None, None)
        else:
            return b

    def retrieve_postback_settings(self, action_code):
        el_id = unique_ID_to_client_ID(action_code)
        el = self.document.get_element_by_id(el_id, None)

        if el is None:
            c = self.find_nearest_element(action_code)
            if c is not None:
                return self.get_post_back_settings(c, action_code)
            else:
                return create_post_back_settings(
                    False, None, None
                )
        else:
            return self.get_post_back_settings(el, action_code)

    def post_back(self, session, action_code, extra_params=None):
        params = params_from_form(self._form)

        # load in the extra parameters
        params.update(extra_params or {})

        _postBackSettings = self.retrieve_postback_settings(action_code)
        params[self._script_manager_ID] = _postBackSettings['panelID']
        params['__EVENTTARGET'] = action_code
        params.setdefault('__EVENTARGUMENT', '')

        r = session.post(
            BASE_HTTPS + "TravelEasy/MySmartRider/tabid/71/Default.aspx",
            data=params,
            headers={
                "X-MicrosoftAjax": "Delta=true",
                "Cache-Control": "no-cache",
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 6.1; WOW64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/32.0.1700.107 Safari/537.36)"
                )
            }
        )

        updates = parse_delta(r.text)

        if (updates['pageRedirect'] or
                '/TravelEasy/tabid/69/Default.aspx?returnurl=' in r.url):
            raise Exception('Not logged in: {}'.format(
                updates['pageRedirect'][0]['content']
            ))

        return updates


class PageRequestManagerAugmentations(object):
    def initalise_from_document(self):
        return
        self._form = self.document.forms[0]
        scripts = self.document.xpath(".//script")

        for script in scripts:
            if script.attrib.get('src') is None:
                # try:
                print(script.text[:150])
                # except
                # print(script.text.encode()[:150])
                if 'PageRequestManager._initialize' in script.text:
                    print(script.text)

                    lines = clean(script.text.splitlines())
                    lines = filter(FUNCTIONCALL_RE.search, lines)

                    calls = dict(
                        map(_parse_function_call, lines)
                    )

                    from pprint import pprint
                    pprint(calls)

        # Sys.WebForms.PageRequestManager._initialize(
        #     'ScriptManager',
        #     document.get_element_by_Id('Form')
        # )
        # Sys.WebForms.PageRequestManager.getInstance().
        # _updateControls(
        #     [
        #         'tdnn$ctr2061$SmartRiderTransactions$pnlModuleMessagePanel',
        #         'tdnn$ctr2061$SmartRiderTransactions$pnlSmartRiderBalancePanel',
        #         'tdnn$ctr2061$SmartRiderTransactions$rgTransactionsPanel',
        #         'tdnn$ctr2061$SmartRiderTransactions$rdFromDatePanel',
        #         'tdnn$ctr2061$SmartRiderTransactions$rdToDatePanel',
        #         'tRadAjaxManager1SU'
        #     ],
        #     [
        #         'dnn$ctr2061$SmartRiderTransactions$ddlSmartCardNumber',
        #         'dnn$ctr2061$SmartRiderTransactions$rgTransactions',
        #         'dnn$ctr2061$SmartRiderTransactions$rdToDate',
        #         'dnn$ctr2061$SmartRiderTransactions$rdFromDate'
        #     ],
        #     [],
        #     90
        # );

        print('fin')
        raise Exception()

    def possible_actions(self):
        def args_from_href(href):
            href = href.split('javascript:__doPostBack(')[1][:-1]
            return href.replace("'", '').split(',')

        hrefs = self.document.xpath('//*[@href]')

        hrefs = (
            href
            for href in hrefs
            if '__doPostBack' in href.attrib['href']
        )

        nhrefs = {}
        for href in hrefs:
            if 'id' in href.attrib:
                name = href.attrib.get('id')
            elif 'title' in href.attrib:
                name = href.attrib.get('title')
            else:
                name = href.attrib['class']

            assert name, (href.attrib, href)

            nhrefs[name] = args_from_href(href.attrib['href'])

        return nhrefs


class PageRequestManager(
        PageRequestManagerAugmentations,
        PageRequestManagerOriginal):
    pass
