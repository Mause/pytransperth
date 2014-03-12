import tornado.web
import ipy_table

from transperth.jp.location import Location
from transperth_auth import TransperthAuthMixin


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
        kwargs['is_authenticated'] = self.is_authenticated
        return super().render(*args, **kwargs)

    def get_smartrider(self):
        sr_code = self.get_argument('sr_code', None)

        if sr_code is not None:
            return sr_code

        riders = self.current_user.smart_riders()
        if len(riders) > 1:
            return None  # trigger smart rider selection
        else:
            return list(riders.values())[0]


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
