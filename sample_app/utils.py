from functools import wraps
from urllib.parse import urlencode

import tornado.web
import ipy_table

from transperth.jp.location import Location
from transperth.exceptions import NotLoggedIn
from transperth_auth import TransperthAuthMixin

from transperth.smart_rider.smart_rider import smartrider_format


class BaseRequestHandler(TransperthAuthMixin, tornado.web.RequestHandler):
    @property
    def args(self):
        args = self.request.arguments

        return {
            k: [sv.decode() for sv in v]
            for k, v in args.items()
        }

    def get_location(self, key):
        return Location.from_location(
            self.get_argument(key)
        )

    def render(self, *args, **kwargs):
        kwargs.update({
            # helper functions
            'is_authenticated': self.is_authenticated,
            'smartrider_format': smartrider_format
        })
        kwargs.setdefault('redirect', None)

        return super().render(*args, **kwargs)

    def redirect(self, url, *args, **kwargs):
        params = kwargs.get('params')
        return super().redirect(
            url + ('?' + urlencode(params) if params else '')
        )


class SmartRiderMixin(tornado.web.RequestHandler):
    def render(self, *args, **kwargs):
        kwargs['smart_riders'] = (
            self.current_user.smart_riders()
        )

        sr_code = self.get_argument('sr_code', None)
        if sr_code:
            for num, meta in kwargs['smart_riders'].items():
                if meta['code'] == sr_code:
                    meta['default'] = True
                else:
                    meta['default'] = False

        return super().render(*args, **kwargs)

    def get_smartrider(self):
        sr_code = self.get_argument('sr_code', None)

        if sr_code is not None:
            return sr_code

        riders = self.current_user.smart_riders()
        for sr_num, sr_meta in riders.items():
            if sr_meta['default']:
                return riders[sr_num]['code']


def fares_to_table(fares):
    keys, values = zip(*fares.items())

    table_rows = [['Fare Type']]
    table_rows[-1].extend(key.title() for key in keys)

    for key in sorted(values[0].keys()):
        table_rows.append([key.title()])

        table_rows[-1].extend(
            '${}'.format(ticket_type[key])
            for ticket_type in values
        )

    table = ipy_table.make_table(table_rows)
    table.apply_theme('basic')

    return table


humanise_flag = {
    "*": 'Estimated time only',
    "Dv": 'Deviating Service',
    "Ls": 'Limited stops service',
    "+": 'indicates the following day',
    "As": 'Accessible service',
    "Ch": 'Service undergoing change'
}.get


def auth_required(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # asserts the user is logged in from our perspective
        if not self.current_user:
            return self.reauth('not_logged_in')

        try:
            return func(self, *args, **kwargs)
        except NotLoggedIn:
            # the user is not logged in from transperths perspective
            # some functions handle the NotLoggedIn error elsewhere
            return self.reauth()

    return wrapper
