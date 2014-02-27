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
