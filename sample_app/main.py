# standard library
import logging
import os
import sys

here = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(here, '..'))

# third party
import tornado.ioloop
import tornado.log
import tornado.web

# application specific
import transperth.fares
from transperth.smart_rider.smart_rider import login
from transperth.exceptions import NotLoggedIn
from location_proxy import determine_location
from utils import fares_to_table, BaseRequestHandler
from transperth_auth import TransperthAuthMixin

logging.basicConfig(level=logging.DEBUG)
tornado.log.enable_pretty_logging()


class FaresRequestHandler(BaseRequestHandler):
    def get(self):
        self.render('fares.html')

    def post(self):
        from_loco = self.get_location('from')
        to_loco = self.get_location('to')

        locations = determine_location(from_loco, to_loco)

        from_loco = locations['from'][0]
        to_loco = locations['to'][0]

        fares = transperth.fares.determine_fare(
            from_loco,
            to_loco
        )

        table = fares_to_table(fares)

        self.render('fares_display.html', fares_table=table._repr_html_())



REASONS = {
    'session_expired': "Your session has expired. Please login again"
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

        ts = login(usr, pwd)

        creds = json.dumps(ts.session.cookies.get_dict())

        self.set_secure_cookie('transperth_creds', creds)

        self.redirect('/')


class LogoutHandler(BaseRequestHandler):
    def get(self):
        self.clear_cookie('transperth_creds')

        self.redirect('/')


settings = {
    'debug': True,
    'template_path': os.path.join(here, 'templates'),
    'cookie_secret': 'blardyunicurtinblarg',
    'login_url': '/login'
}


application = tornado.web.Application([
    (r"/fares", FaresRequestHandler)

    (r"/login", LoginHandler),
    (r"/logout", LogoutHandler)
], **settings)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
