import json
import requests
import logging
from auth_base import AuthMixin

from transperth.smart_rider.smart_rider import TransperthSession

logger = logging.getLogger(__name__)


class TransperthAuthMixin(AuthMixin):
    def is_authenticated(self):
        return self.get_secure_cookie('transperth_creds') is not None

    def get_current_user(self):
        if not self.is_authenticated():
            return

        cookie = self.get_secure_cookie('transperth_creds')

        if hasattr(cookie, 'decode'):
            cookie = cookie.decode()

        s = requests.Session()
        s.cookies.update(json.loads(cookie))

        return TransperthSession(s)

    def reauth(self):
        self.clear_cookie('transperth_creds')
        return self.redirect(
            self.get_login_url() + '?reason=session_expired'
        )
