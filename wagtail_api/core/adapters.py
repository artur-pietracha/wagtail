import requests
from allauth.account.models import EmailAddress
from allauth.socialaccount import adapter, providers
from allauth.socialaccount.providers.facebook.provider import FacebookProvider
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.provider import GoogleProvider
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from django.conf import settings

from rest_framework.exceptions import ParseError

from wagtail_api.user.models import User


class SocialAccountAdapter(adapter.DefaultSocialAccountAdapter):
    def is_auto_signup_allowed(self, request, sociallogin):
        if User.objects.filter(email__iexact=sociallogin.user.email).exists():
            raise ParseError(
                {
                    "detail": "User with given email already registered",
                    "code": "registration_error_email_already_registered",
                }
            )
        return super().is_auto_signup_allowed(request, sociallogin)


class GoogleProviderIdToken(GoogleProvider):
    def extract_uid(self, data):
        # "sub" in response is user's unique Google ID
        return data["sub"]

    def extract_email_addresses(self, data):
        email_addresses = []
        email = data.get("email")

        if email and data.get("email_verified"):
            email_addresses.append(EmailAddress(email=email, verified=True, primary=True))
        return email_addresses


class GoogleOAuth2AdapterIdToken(GoogleOAuth2Adapter):
    """
    Google OAuth2 adapter that works with idToken
    https://developers.google.com/identity/sign-in/web/backend-auth
    """

    def get_provider(self):
        return GoogleProviderIdToken(request=self.request)

    @staticmethod
    def get_google_user_data(token):
        user_data = id_token.verify_oauth2_token(
            token, google_requests.Request(), settings.GOOGLE_OAUTH2_CLIENT_ID
        )

        valid_issuers = ["accounts.google.com", "https://accounts.google.com"]
        issuer = user_data["iss"]

        if issuer not in valid_issuers:
            raise ValueError(
                {
                    "detail": f"Wrong issuer, got '{issuer}', expected {valid_issuers}",
                    "code": "wrong_issuer",
                }
            )
        return user_data

    def complete_login(self, request, app, token, **kwargs):
        try:
            user_data = self.get_google_user_data(token.token)
        except Exception as err:
            raise ParseError({"detail": f"{err}", "code": "complete_login"})

        return self.get_provider().sociallogin_from_response(request, user_data)


class FacebookOAuth2AdapterV4(FacebookOAuth2Adapter):
    """
    Facebook OAuth2 adapter for v4 API
    """

    def complete_login(self, request, app, access_token, **kwargs):
        provider = providers.registry.by_id(FacebookProvider.id, request)

        response = requests.get(
            "https://graph.facebook.com/v4.0/me",
            params={
                "fields": "id,email,name,first_name,last_name",
                "access_token": access_token.token,
            },
        )
        response.raise_for_status()
        return provider.sociallogin_from_response(request, response.json())
