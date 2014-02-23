"""
The code in this file was ported from javascript from the transperth website.

As I progress, I will attempt to whittle it down to purely what is absolutely
required.
"""

from collections import defaultdict
from pprint import pprint

# from .. import BASE
BASE = 'https://www.transperth.wa.gov.au/'

_async_post_back_control_client_IDs = set()
_post_back_control_client_IDs = set()
_update_panel_client_IDs = [
    "dnn_ctr2061_SmartRiderTransactions_pnlModuleMessagePanel",
    "dnn_ctr2061_SmartRiderTransactions_pnlSmartRiderBalancePanel",
    "dnn_ctr2061_SmartRiderTransactions_rgTransactionsPanel",
    "dnn_ctr2061_SmartRiderTransactions_rdFromDatePanel",
    "dnn_ctr2061_SmartRiderTransactions_rdToDatePanel",
    "RadAjaxManager1SU"
]
_update_panel_has_children_as_triggers = [True, True, True, True, True, True]
_update_panel_IDs = [
    "dnn$ctr2061$SmartRiderTransactions$pnlModuleMessagePanel",
    "dnn$ctr2061$SmartRiderTransactions$pnlSmartRiderBalancePanel",
    "dnn$ctr2061$SmartRiderTransactions$rgTransactionsPanel",
    "dnn$ctr2061$SmartRiderTransactions$rdFromDatePanel",
    "dnn$ctr2061$SmartRiderTransactions$rdToDatePanel",
    "RadAjaxManager1SU"
]
_create_post_back_settings = lambda c, b, a: {
    'async': c,
    'panelID': b,
    'sourceElement': a
}


_unique_ID_to_client_ID = lambda a: '_'.join(a.split('$'))


def _matches_parent_ID_in_list(c, b):
    for a in b:
        if (c.starts_with(a + "_")):
            return True
    return False


def _find_nearest_element(document, a):
    while a:
        d = _unique_ID_to_client_ID(a)
        c = document.get_element_by_id(d, None)

        if c is not None:
            return c

        if '$' not in a:
            return None

        a = '$'.join(
            a.split('$')[:-1]
        )

    return None


def _get_post_back_settings(document, a, c):
    d = a
    b = None
    while a is not None:
        if a.attrib['id']:
            if not b and a.attrib['id'] in _async_post_back_control_client_IDs:
                b = _create_post_back_settings(
                    True,
                    'ScriptManager|' + c,
                    d
                )
            elif not b and a.attrib['id'] in _post_back_control_client_IDs:
                return _create_post_back_settings(False, None, None)
            else:
                if a.attrib['id'] in _update_panel_client_IDs:
                    e = _update_panel_client_IDs.index(a.attrib['id'])
                else:
                    e = -1

                if e != -1:
                    if (_update_panel_has_children_as_triggers[e]):
                        return _create_post_back_settings(
                            True,
                            _update_panel_IDs[e] + "|" + c,
                            d
                        )
                    else:
                        return _create_post_back_settings(
                            True,
                            'ScriptManager|' + c,
                            d
                        )

            if not b:
                if _matches_parent_ID_in_list(
                        a.attrib['id'],
                        _async_post_back_control_client_IDs):
                    b = _create_post_back_settings(
                        True,
                        'ScriptManager|' + c,
                        d
                    )
                elif _matches_parent_ID_in_list(a.attrib['id'],
                                                _post_back_control_client_IDs):
                    return _create_post_back_settings(False, None, None)

        a = a.getparent()

    if (not b):
        return _create_post_back_settings(False, None, None)
    else:
        return b


def retrieve_postback_settings(document):
    a = (
        "dnn$"
        "ctr2061$"
        "SmartRiderTransactions$"
        "rgTransactions$"
        "ctl00$"
        "ctl02$"
        "ctl00$"
        "ctl00"
    )
    print(a)

    f = _unique_ID_to_client_ID(a)
    d = document.get_element_by_id(f, None)

    if d is None:
        c = _find_nearest_element(document, a)
        if c is not None:
            return _get_post_back_settings(document, c, a)
        else:
            return _create_post_back_settings(
                False, None, None
            )
    else:
        return _get_post_back_settings(document, d, a)


def params_from_form(form):
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


def post_back(session, document, form, code, date_from, date_to):
    params = params_from_form(form)

    _postBackSettings = retrieve_postback_settings(document)
    params["ScriptManager"] = _postBackSettings['panelID']

    # add in date range
    params.update({
        'dnn$ctr2061$SmartRiderTransactions$rdFromDate': (
            date_from.strftime('%Y-%d-%m')
        ),
        'dnn$ctr2061$SmartRiderTransactions$rdFromDate$dateInput': (
            date_from.strftime('%Y-%d-%m-00-00-00')
        ),
        'dnn$ctr2061$SmartRiderTransactions$rdToDate': (
            date_to.strftime('%Y-%d-%m')
        ),
        'dnn$ctr2061$SmartRiderTransactions$rdToDate$dateInput': (
            date_to.strftime('%Y-%d-%m-00-00-00')
        )
    })

    # add in smart rider card selection, for those special few with
    # more than one
    params['dnn$ctr2061$SmartRiderTransactions$ddlSmartCardNumber'] = code

    params.update({
        '__EVENTARGUMENT': (
            'FireCommand:'
            'dnn$ctr2061$SmartRiderTransactions$rgTransactions$ctl00;'
            'PageSize;'
            '50'
        )
    })
    # 'dnn$ctr2061$SmartRiderTransactions$rgTransactions$ctl00$ctl03$ctl01'
    # '$PageSizeComboBox': 50,
    # 'dnn_ctr2061_SmartRiderTransactions_rgTransactions_ctl00_ctl03_ctl01_'
    # 'PageSizeComboBox_ClientState': '',
    # 'dnn_ctr2061_SmartRiderTransactions_rgTransactions_ctl00_ctl03_ctl01_'
    # 'PageSizeComboBox_ClientState': (
    #     '{"logEntries": [],"value": "50","text": "50","enabled": true}'
    # )

    pprint(params)

    r = session.post(
        BASE + "TravelEasy/MySmartRider/tabid/71/Default.aspx",
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

    updates = _parse_delta(r.text)

    if updates['pageRedirect']:
        raise Exception(('Not logged in', updates['pageRedirect']))

    return updates


def _parse_delta(c):
    updates = defaultdict(list)
    c = c.split('|')

    while c:
        if c[0] == '':
            break

        length, frag_type, frag_id, content = (
            c.pop(0), c.pop(0), c.pop(0), c.pop(0)
        )

        updates[frag_type].append({
            'id': frag_id,
            'content': content
        })

    return updates
