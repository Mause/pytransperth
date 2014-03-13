import logging
import pickle
from collections import Counter

from auth_base import AuthMixin

logger = logging.getLogger(__name__)


class TransperthAuthMixin(AuthMixin):
    def is_authenticated(self):
        return self.get_secure_cookie('transperth_creds') is not None

    def get_current_user(self):
        if not self.is_authenticated():
            return

        cookie = self.get_secure_cookie('transperth_creds')

        sess = pickle.loads(cookie)
        sess.session.hooks['response'] = self.increm
        return sess

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

    def increm(self, hook_data, **kwargs):
        if not hasattr(self, 'requests'):
            self.requests = [hook_data]
        else:
            self.requests.append(hook_data)

    def on_finish(self):
        if hasattr(self, 'requests'):
            urls = Counter(
                r.url.strip('https://www.transperth.wa.gov.au/')
                for r in self.requests
            )

            urls = ', '.join(
                '{} * {}'.format(url, count)
                for url, count in urls.items()
            )

            logging.info('{} total -> {}'.format(
                len(self.requests), urls
            ))
            self.requests = []
