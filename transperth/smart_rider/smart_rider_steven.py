#!/usr/bin/venv python
import requests
from lxml import html, etree
from itertools import chain
import json

BASE = 'https://www.transperth.wa.gov.au/'

# we actually need a class for the login part of the website,
# as the session has to be stored somewhere


class Transperth(object):
    """

    """


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

    return s


def get_smart_rider(s):
    r = s.get(BASE + "TravelEasy/MySmartRider/tabid/71/Default.aspx")

    assert r.ok, r.status_code
    assert r.headers['Content-Type'].startswith('text/html'), (
        r.headers['Content-Type']
    )

    return _request_from_form(
        r.text
    )


def _request_from_form(document):
    with open('document.html', 'w') as fh:
        fh.write(document)

    document = html.document_fromstring(document)

    from pprint import pprint
    pprint(document.forms[0])

    form = document.forms[0]

    print(form, form.attrib)

    # import IPython
    # IPython.embed()

    _doPostBack(s, document, form)


def _get_smart_rider(root):
    # assert not root.startswith('132')

    print(root)

    with open('test.html', 'w') as fh:
        fh.write(root)

    root = html.document_fromstring(root)

    table = root.xpath("//table[@class='rgMasterTable']")
    assert table, table

    table = table[0]
    print(table)

    rows = table.find('tbody').findall('tr')
    print(rows)
    items = (
        map(etree._Element.itertext, row.findall('td'))
        for row in rows
    )
    items = map(chain.from_iterable, items)
    items = list(map(list, items))

    from pprint import pprint
    pprint(items)

    data = items[0]

    out = {
        'time': data[0] + " +0800",
        'action': data[1],
        'location': (data[2].replace(" a ", " after ")
                     .replace(" b ", " before")),
        'service': data[3],
        'zone': data[4],
        'cost': data[5],
        'balance': data[6],
        'notes': data[7]
    }

    from pprint import pprint
    pprint(out)

    # url = BASE + "DesktopModules/JourneyPlanner/JP.aspx".format(out
        # ["location"])

    # data = requests.get(
    #     ?from=Location&to=Location&fromStreet=&fromSuburb=&fromLocation={}&f
    # romStop=&toStreet=&toSuburb=&toLocation=a&toStop=&jpDate=Tuesday,%2011%2
    # 0February%202014&jpDirection=A&jpAMPM=PM&jpHour=8&jpMinute=30&fSet=False
    # &fGadget=False&mode=t1,b1,f1,s0&jpnMaxJourneys=5&jpMaxChanges=-1&jpWalkCh
    # ange=NORMAL&jpWheelchairOnly=0
    # )

    # data = Soup(requests.get(url).text)


    # if " after " in out["location"] or " before " in out["location"]: # Bus
    #     term = out["location"].split(" ")[-1]
    #     for a in data.findall('fromlocation'):
    #         text = a.find('display').text
    #         if not term in text:
    #             continue
    #         gterm = text.split(" (")[0]
    #     if not gterm:
    #         gterm = "Perth"
    # else: # probably train
    #     gterm = out["location"]
    # out["gterm"] = gterm
    # out["text"] = "Steven was last seen doing a {action} at {location}. He
    # has {balance} left on his SmartRider.".format(**out)
    # with open('/home/blha/sites/blha303.com.au/where/transperthinfo.json'
    #     'w') as f:
    #     f.write(json.dumps(out))


_uniqueIDToClientID = lambda a: '_'.join(a.split('$'))


def _findNearestElement(document, a):
    while a:
        d = _uniqueIDToClientID(a)
        c = document.get_element_by_id(d, None)

        if c is not None:
            return c

        if '$' not in a:
            return None

        a = '$'.join(
            a.split('$')[:-1]
        )

    return None

_asyncPostBackControlClientIDs = set()
_postBackControlClientIDs = set()
_updatePanelClientIDs = [
    "dnn_ctr2061_SmartRiderTransactions_pnlModuleMessagePanel",
    "dnn_ctr2061_SmartRiderTransactions_pnlSmartRiderBalancePanel",
    "dnn_ctr2061_SmartRiderTransactions_rgTransactionsPanel",
    "dnn_ctr2061_SmartRiderTransactions_rdFromDatePanel",
    "dnn_ctr2061_SmartRiderTransactions_rdToDatePanel",
    "RadAjaxManager1SU"
]
_scriptManagerID = 'arbitrary'
_updatePanelHasChildrenAsTriggers = [True, True, True, True, True, True]
_updatePanelIDs = [
    "dnn$ctr2061$SmartRiderTransactions$pnlModuleMessagePanel",
    "dnn$ctr2061$SmartRiderTransactions$pnlSmartRiderBalancePanel",
    "dnn$ctr2061$SmartRiderTransactions$rgTransactionsPanel",
    "dnn$ctr2061$SmartRiderTransactions$rdFromDatePanel",
    "dnn$ctr2061$SmartRiderTransactions$rdToDatePanel",
    "RadAjaxManager1SU"
]


_createPostBackSettings = lambda c, b, a: {
    'async': c,
    'panelID': b,
    'sourceElement': a
}

_matchesParentIDInList = lambda a, b: a in b


def _getPostBackSettings(document, a, c):
    d = a
    b = None
    while a is not None:
        if a.attrib['id']:
            if not b and a.attrib['id'] in _asyncPostBackControlClientIDs:
                b = _createPostBackSettings(
                    True,
                    _scriptManagerID + "|" + c,
                    d
                )
            elif not b and a.attrib['id'] in _postBackControlClientIDs:
                return _createPostBackSettings(False, None, None)
            else:
                if a.attrib['id'] in _updatePanelClientIDs:
                    e = _updatePanelClientIDs.index(a.attrib['id'])
                else:
                    e = -1

                if e != -1:
                    if (_updatePanelHasChildrenAsTriggers[e]):
                        return _createPostBackSettings(
                            True,
                            _updatePanelIDs[e] + "|" + c,
                            d
                        )
                    else:
                        return _createPostBackSettings(
                            True,
                            _scriptManagerID + "|" + c,
                            d
                        )

            if not b:
                if _matchesParentIDInList(a.attrib['id'],
                                          _asyncPostBackControlClientIDs):
                    b = _createPostBackSettings(
                        True,
                        _scriptManagerID + "|" + c,
                        d
                    )
                elif _matchesParentIDInList(a.attrib['id'], _postBackControlClientIDs):
                    return _createPostBackSettings(False, None, None)

        a = a.getparent()

    if (not b):
        return _createPostBackSettings(False, None, None)
    else:
        return b


def _doPostBack(session, document, form):
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
    e = ""

    f = _uniqueIDToClientID(a)
    d = document.get_element_by_id(f, None)

    if not d:
        c = _findNearestElement(document, a)
        if c is not None:
            _postBackSettings = _getPostBackSettings(document, c, a)
        else:
            _postBackSettings = _createPostBackSettings(
                False, None, None
            )
    else:
        _postBackSettings = _getPostBackSettings(document, d, a)

    from pprint import pprint
    pprint(_postBackSettings)

    # b = object()
    # b.__EVENTTARGET.value = a
    # b.__EVENTARGUMENT.value = e
    _onFormSubmit(session, form, _postBackSettings)


def _onFormSubmit(session, form, _postBackSettings):
    params = {}
    params["ScriptManager"] = _postBackSettings['panelID']

    for d in form.xpath('.//input'):
        f = d.name
        if not f or f == "ScriptManager":
            continue

        # m = d.tagName.toUpperCase()
        m = d.tag.upper()

        if m == "INPUT":
            k = d.type
            if (k in {"text", "password", "hidden"} or
                    k in {"checkbox", "radio"} and d.checked):
                params[f] = d.value

        elif m == "SELECT":
            raise NotImplementedError()
            # u = d.options.length
            # for (o = 0; o < u; o++) {
            #     q = d.options[o]
            #     if (q.selected) {
            #         params[f] = q.value
            #     }
            # }
        elif (m == "TEXTAREA"):
            params[f] = d.value
        else:
            raise Exception(m)

    # params['__ASYNCPOST'] = 'true'

    r = session.post(
        BASE + "TravelEasy/MySmartRider/tabid/71/Default.aspx",
        data=params,
        headers={
            "X-MicrosoftAjax": "Delta=true",
            "Cache-Control": "no-cache",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36"
        }
    )

    with open('afterall.html', 'w') as fh:
        fh.write(r.text)

    print(r)

    import IPython
    IPython.embed()

    # i, j = this._get_eventHandlerList().getHandler("initializeRequest")
    # if j:
    #     i = Sys.WebForms.InitializeRequestEventArgs(
    #         c, _postBackSettings.sourceElement
    #     )
    #     j(this, i)
    #     g = not i.get_cancel()

    # this.abortPostBack()
    # j = this._get_eventHandlerList().getHandler("beginRequest")
    # if j:
    #     i = Sys.WebForms.BeginRequestEventArgs(
    #         c, _postBackSettings.sourceElement)
    #     j(this, i)
    # if (this._originalDoCallback):
    #     this._cancelPendingCallbacks()
    # this._request = c
    # this._processingRequest = False
    # c.invoke()
    # if (h):
    #     h.preventDefault()



if __name__ == '__main__':
    import os

    if not os.path.exists('session.json'):
        print('loggging in...')

        s = login(*open('auth').read().split(','))

        with open('session.json', 'w') as fh:
            json.dump(s.cookies.get_dict(), fh, indent=4)
    else:
        s = requests.Session()
        with open('session.json') as fh:
            s.cookies.update(json.load(fh))

    get_smart_rider(s)
