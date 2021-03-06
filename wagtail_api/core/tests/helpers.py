import re

from django.test import Client


INTERNAL_RESET_URL_TOKEN = "set-password"
INTERNAL_RESET_SESSION_TOKEN = "_password_reset_token"


def mock_google_verify_oauth2_valid_token(*args, **kwargs):
    return {
        "iss": "https://accounts.google.com",
        "azp": "123123123asdasdasd123123123123123123131231231.apps.googleusercontent.com",
        "aud": "1231231asdase123aweq2ead2a2ea2e12123123123123.apps.googleusercontent.com",
        "sub": "123123123123123423441",
        "hd": "saltandpepper.co",
        "email": "user@example.com",
        "email_verified": True,
        "at_hash": "asd123asd12312312assas",
        "name": "User Example",
        "given_name": "User",
        "family_name": "Example",
        "locale": "en",
        "iat": 1123123123,
        "exp": 1231231231,
    }


def mock_google_verify_oauth2_invalid_issuer(*args, **kwargs):
    response = mock_google_verify_oauth2_valid_token(*args, **kwargs)
    response["iss"] = "https://example.com"

    return response


def extract_token_from_url(url):
    token_search = re.search(r"/password-reset/.*/(.+?)/", url)
    if token_search:
        return token_search.group(1)


class PasswordResetConfirmClient(Client):
    """
    This client eases testing the password reset flow by emulating the
    PasswordResetConfirmView's redirect and saving of the reset token in the
    user's session. This request puts 'my-token' in the session and redirects
    to '/reset/bla/set-password/':
    >>> client = PasswordResetConfirmClient()
    >>> client.get('/reset/bla/my-token/')
    """

    def _get_password_reset_confirm_redirect_url(self, url):
        token = extract_token_from_url(url)
        if not token:
            return url
        # Add the token to the session
        session = self.session
        session[INTERNAL_RESET_SESSION_TOKEN] = token
        session.save()
        return url.replace(token, INTERNAL_RESET_URL_TOKEN)

    def get(self, path, *args, **kwargs):
        redirect_url = self._get_password_reset_confirm_redirect_url(path)
        return super().get(redirect_url, *args, **kwargs)

    def post(self, path, *args, **kwargs):
        redirect_url = self._get_password_reset_confirm_redirect_url(path)
        return super().post(redirect_url, *args, **kwargs)
