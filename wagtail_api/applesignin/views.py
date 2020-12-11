from datetime import timedelta

import jwt
import requests
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from django.conf import settings
from django.utils import timezone

from rest_framework.exceptions import AuthenticationFailed

from .provider import AppleProvider


class AppleOAuth2Adapter(OAuth2Adapter):
    provider_id = AppleProvider.id

    APPLE_TOKEN_VERIFICATION_URL = "https://appleid.apple.com/auth/token"

    @staticmethod
    def get_apple_token_verification(data):
        response = requests.post(
            AppleOAuth2Adapter.APPLE_TOKEN_VERIFICATION_URL,
            data=data,
            headers={"content-type": "application/x-www-form-urlencoded"},
        ).json()
        if response.get("id_token", None):
            return response
        else:
            raise AuthenticationFailed(
                {"detail": "Invalid token", "code": response.get("error", "invalid_token")}
            )

    @staticmethod
    def create_apple_client_secret():
        client_secret = jwt.encode(
            {
                "iss": settings.SOCIAL_AUTH_APPLE_TEAM_ID,
                "iat": timezone.now(),
                "exp": timezone.now()
                + timedelta(days=settings.SOCIAL_AUTH_APPLE_TOKEN_VALID_DURATION),
                "aud": "https://appleid.apple.com",
                "sub": settings.SOCIAL_AUTH_APPLE_CLIENT_ID,
            },
            settings.SOCIAL_AUTH_APPLE_PRIVATE_KEY,
            algorithm="ES256",
            headers={"kid": settings.SOCIAL_AUTH_APPLE_KEY_ID},
        ).decode("utf-8")
        return client_secret

    def apple_complete_login(self, request, access_token):
        client_secret = AppleOAuth2Adapter.create_apple_client_secret()

        data = {
            "grant_type": "authorization_code",
            "code": access_token,
            "client_id": settings.SOCIAL_AUTH_APPLE_CLIENT_ID,
            "client_secret": client_secret,
        }

        response = AppleOAuth2Adapter.get_apple_token_verification(data)
        id_token = response.get("id_token", None)
        decoded = jwt.decode(id_token, "", verify=False)
        response.update(decoded)
        login = self.get_provider().sociallogin_from_response(request, response)
        return login

    def complete_login(self, request, app, token, **kwargs):
        return self.apple_complete_login(request, token.token)


oauth2_login = OAuth2LoginView.adapter_view(AppleOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(AppleOAuth2Adapter)
