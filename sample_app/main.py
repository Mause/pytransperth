# standard library
import logging
import os
import sys
import pickle
from operator import itemgetter

here = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(here, '..'))

# third party
import tornado.ioloop
import tornado.log
import tornado.web

# application specific
from transperth.jp.fares import fares_for_route
from transperth.jp.routes import determine_routes

from transperth.smart_rider.smart_rider import login
from transperth.smart_rider.trips import determine_trips

from transperth.exceptions import LoginFailed

from location_proxy import determine_location
from utils import (
    fares_to_table,
    BaseRequestHandler,
    SmartRiderMixin,
    humanise_flag,
    auth_required
)
from transperth_auth import TransperthAuthMixin

# setup logging
logging.basicConfig(level=logging.DEBUG)
tornado.log.enable_pretty_logging()


class RoutesRequestHandler(BaseRequestHandler):
    def get(self):
        self.render('enter_route.html')

    def resolve_location(self):
        from_loco = self.get_location('from')
        to_loco = self.get_location('to')

        locations = determine_location(from_loco, to_loco)

        return locations['from'][0], locations['to'][0]

    def post(self):
        from_loco, to_loco = self.resolve_location()

        routes = determine_routes(from_loco, to_loco)

        route = routes[0]

        route['meta']['misc'] = {
            key: (
                value.strftime('%I:%M %p') if hasattr(value, 'strftime')
                else value
            )
            for key, value in route['meta']['misc'].items()
        }

        fares = fares_for_route(route)

        self.render(
            'routes.html',
            fares_table=fares_to_table(fares)._repr_html_(),
            route=route,
            humanise_flag=humanise_flag,
            route_path={
                'from': from_loco.name,
                'to': to_loco.name
            }
        )


class ActionsHandler(SmartRiderMixin, BaseRequestHandler):
    @auth_required
    def get(self):
        sr_code = self.get_smartrider()
        if sr_code is None:
            return self.redirect(
                '/select_smartrider',
                params={'redirect': self.request.uri}
            )

        actions = self.current_user.get_actions(sr_code)
        actions = sorted(
            actions,
            key=itemgetter('time'),
            reverse=True
        )

        self.render('actions.html', actions=list(actions))


class TripHandler(SmartRiderMixin, BaseRequestHandler):
    @auth_required
    def get(self):
        sr_code = self.get_smartrider()

        actions = self.current_user.get_actions(sr_code)
        actions = sorted(
            actions,
            key=itemgetter('time'),
            reverse=True
        )
        actions = list(actions)

        trips = determine_trips(actions)

        self.render('trips.html', trips=list(trips))


REASONS = {
    'session_expired': "Your session has expired. Please login again",
    'bad_credentials': 'You supplied incorrect credentials',
    'not_logged_in': 'Please login to access that feature'
}


class LoginHandler(BaseRequestHandler, TransperthAuthMixin):
    def get(self):
        if self.is_authenticated():
            self.redirect('/')

        reason = self.get_argument('reason', None)
        reason = REASONS.get(reason)

        self.render('transperth_login.html', reason=reason)

    def post(self):
        usr, pwd = self.get_argument('username'), self.get_argument('password')

        try:
            ts = login(usr, pwd)
        except LoginFailed:
            return self.reauth('bad_credentials')

        creds = pickle.dumps(ts)

        self.set_secure_cookie('transperth_creds', creds)

        redirect = self.get_argument('redirect', None) or '/'

        self.redirect(redirect)


class LogoutHandler(BaseRequestHandler):
    def get(self):
        self.clear_cookie('transperth_creds')

        self.redirect('/')


class RootHandler(BaseRequestHandler):
    def get(self):
        self.render('root.html')


settings = {
    'debug': True,
    'template_path': os.path.join(here, 'templates'),
    'static_path': os.path.join(here, 'static'),
    'cookie_secret': 'blardyunicurtinblarg',
    'login_url': '/login'
}


application = tornado.web.Application([
    (r"/", RootHandler),
    (r"/routes", RoutesRequestHandler),
    (r"/actions", ActionsHandler),
    (r"/trips", TripHandler),

    (r"/login", LoginHandler),
    (r"/logout", LogoutHandler)
], **settings)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
