class AuthMixin(object):
    def authorize_redirect(self, callback_uri=None, extra_params=None,
                           http_client=None, callback=None):
        """Redirects the user to obtain OAuth authorization for this service.

        The ``callback_uri`` may be omitted if you have previously
        registered a callback URI with the third-party service.  For
        some sevices (including Friendfeed), you must use a
        previously-registered callback URI and cannot specify a
        callback via this method.

        This method sets a cookie called ``_oauth_request_token`` which is
        subsequently used (and cleared) in `get_authenticated_user` for
        security purposes.

        Note that this method is asynchronous, although it calls
        `.RequestHandler.finish` for you so it may not be necessary
        to pass a callback or use the `.Future` it returns.  However,
        if this method is called from a function decorated with
        `.gen.coroutine`, you must call it with ``yield`` to keep the
        response from being closed prematurely.

        .. versionchanged:: 3.1
           Now returns a `.Future` and takes an optional callback, for
           compatibility with `.gen.coroutine`.
        """
        raise NotADirectoryError()

    def get_authenticated_user(self, callback, http_client=None):
        """Gets the OAuth authorized user and access token.

        This method should be called from the handler for your
        OAuth callback URL to complete the registration process. We run the
        callback with the authenticated user dictionary.  This dictionary
        will contain an ``access_key`` which can be used to make authorized
        requests to this service on behalf of the user.  The dictionary will
        also contain other fields such as ``name``, depending on the service
        used.
        """
        raise NotImplementedError()
