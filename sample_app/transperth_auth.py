import logging
import pickle

from auth_base import AuthMixin

logger = logging.getLogger(__name__)


class TransperthAuthMixin(AuthMixin):
    def is_authenticated(self):
        return self.get_secure_cookie('transperth_creds') is not None

    def get_current_user(self):
        if not self.is_authenticated():
            return

        cookie = self.get_secure_cookie('transperth_creds')

        return pickle.loads(cookie)

    def reauth(self, reason="session_expired"):
        params = {
            "reason": reason,
            "redirect": self.request.uri
        }

        self.clear_cookie('transperth_creds')
        return self.redirect(
            self.get_login_url(),
            params=params
        )
