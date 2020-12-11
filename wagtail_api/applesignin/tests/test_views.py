import jwt
import pytest
import requests_mock

from django.conf import settings

from rest_framework.exceptions import AuthenticationFailed

from ..views import AppleOAuth2Adapter
from .helpers import mock_apple_verify_oauth2_invalid_token, mock_apple_verify_oauth2_valid_token


def test_apple_client_secret():
    secret = AppleOAuth2Adapter.create_apple_client_secret()
    decoded = jwt.decode(secret, "", verify=False)
    assert decoded["iss"] == settings.SOCIAL_AUTH_APPLE_TEAM_ID
    assert decoded["aud"] == "https://appleid.apple.com"
    assert decoded["sub"] == settings.SOCIAL_AUTH_APPLE_CLIENT_ID


def test_get_apple_token_verification_token_valid(api_client):
    client_secret = AppleOAuth2Adapter.create_apple_client_secret()

    apple_app_response_json = mock_apple_verify_oauth2_valid_token()

    data = {
        "grant_type": "authorization_code",
        "code": "valid",
        "client_id": settings.SOCIAL_AUTH_APPLE_CLIENT_ID,
        "client_secret": client_secret,
    }
    with requests_mock.mock() as mocked_requests:
        # Intercept the call to Apple API made in the get_apple_token_verification function
        mocked_requests.post(
            AppleOAuth2Adapter.APPLE_TOKEN_VERIFICATION_URL,
            json=apple_app_response_json,
            status_code=200,
        )
        response = AppleOAuth2Adapter.get_apple_token_verification(data)
        assert response == apple_app_response_json


def test_get_apple_token_verification_token_invalid(api_client):
    client_secret = AppleOAuth2Adapter.create_apple_client_secret()

    apple_app_response_json = mock_apple_verify_oauth2_invalid_token()

    data = {
        "grant_type": "authorization_code",
        "code": "invalid",
        "client_id": settings.SOCIAL_AUTH_APPLE_CLIENT_ID,
        "client_secret": client_secret,
    }
    with requests_mock.mock() as mocked_requests:
        # Intercept the call to Apple API made in the get_apple_token_verification function
        mocked_requests.post(
            AppleOAuth2Adapter.APPLE_TOKEN_VERIFICATION_URL,
            json=apple_app_response_json,
            status_code=401,
        )
        with pytest.raises(AuthenticationFailed) as error:
            AppleOAuth2Adapter.get_apple_token_verification(data)
        assert error.value.args[0]["code"] == "invalid_grant"
