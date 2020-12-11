import json
import re

import pytest
import requests_mock
from google.oauth2 import id_token

from django.contrib.auth.tokens import default_token_generator
from django.contrib.messages import get_messages
from django.test import Client
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode

from rest_framework.exceptions import AuthenticationFailed

from ...applesignin.tests.helpers import mock_apple_verify_oauth2_valid_token
from ...applesignin.views import AppleOAuth2Adapter
from ...user.models import User
from ...user.tests.factories import UserFactory
from .helpers import (
    PasswordResetConfirmClient,
    mock_google_verify_oauth2_invalid_issuer,
    mock_google_verify_oauth2_valid_token,
)


@pytest.mark.django_db
def test_apple_login_valid_access_token(api_client, apple_social_app, monkeypatch):
    monkeypatch.setattr(
        AppleOAuth2Adapter, "get_apple_token_verification", mock_apple_verify_oauth2_valid_token
    )
    response = api_client.post(reverse("apple_login"), data={"code": "valid"})
    assert response.status_code == 200
    assert User.objects.count() == 1

    user = User.objects.first()
    assert user.email == "user@gmail.com"


@pytest.mark.django_db
def test_apple_login_invalid_access_token(api_client, apple_social_app, monkeypatch):
    def raise_authentication_failed(*args, **kwargs):
        raise AuthenticationFailed({"detail": "Invalid token", "code": "invalid_grant"})

    monkeypatch.setattr(
        AppleOAuth2Adapter, "get_apple_token_verification", raise_authentication_failed
    )
    response = api_client.post(reverse("apple_login"), data={"code": "invalid"})

    assert response.status_code == 401
    assert response.data == {"detail": "Invalid token", "code": "invalid_grant"}


@pytest.mark.django_db
def test_google_login_valid_access_token(api_client, google_social_app, monkeypatch):
    monkeypatch.setattr(id_token, "verify_oauth2_token", mock_google_verify_oauth2_valid_token)

    response = api_client.post(reverse("google_login"), data={"access_token": "valid"})

    assert response.status_code == 200
    assert User.objects.count() == 1

    user = User.objects.first()
    assert user.email == "user@example.com"
    assert user.first_name == "User"
    assert user.last_name == "Example"


@pytest.mark.django_db
def test_google_login_valid_access_token_email_already_registered(
    api_client, google_social_app, monkeypatch
):
    monkeypatch.setattr(id_token, "verify_oauth2_token", mock_google_verify_oauth2_valid_token)

    UserFactory(email="user@example.com")

    response = api_client.post(reverse("google_login"), data={"access_token": "valid"})

    assert response.status_code == 400
    assert response.data == {
        "code": "registration_error_email_already_registered",
        "detail": "User with given email already registered",
    }


@pytest.mark.django_db
def test_google_login_invalid_issuer(api_client, google_social_app, monkeypatch):
    monkeypatch.setattr(id_token, "verify_oauth2_token", mock_google_verify_oauth2_invalid_issuer)

    UserFactory(email="user@example.com")

    response = api_client.post(reverse("google_login"), data={"access_token": "invalid_issuer"})

    assert response.status_code == 400
    assert response.data == {
        "code": "complete_login",
        "detail": "{'detail': \"Wrong issuer, got 'https://example.com', expected "
        "['accounts.google.com', 'https://accounts.google.com']\", 'code': 'wrong_issuer'}",
    }


@pytest.mark.django_db
def test_google_login_invalid_access_token(api_client, google_social_app, monkeypatch):
    def raise_value_error(*args, **kwargs):
        raise ValueError("Invalid token")

    monkeypatch.setattr(id_token, "verify_oauth2_token", raise_value_error)

    response = api_client.post(reverse("google_login"), data={"access_token": "ivalid"})

    assert response.status_code == 400
    assert response.data == {"code": "complete_login", "detail": "Invalid token"}
    assert User.objects.count() == 0


@pytest.mark.django_db
def test_facebook_login_valid_access_token(api_client, facebook_social_app):
    access_token = "valid"

    with requests_mock.mock() as mocked_requests:
        # Intercept the call to Facebook API made in the FacebookLogin view
        mocked_requests.get(
            "https://graph.facebook.com/v4.0/me?fields="
            f"id%2Cemail%2Cname%2Cfirst_name%2Clast_name&access_token={access_token}",
            text=json.dumps(
                {
                    "id": "11111111111111111",
                    "name": "User Example",
                    "first_name": "User",
                    "last_name": "Example",
                    "email": "user@example.com",
                }
            ),
            status_code=200,
        )
        response = api_client.post(reverse("facebook_login"), data={"access_token": access_token})

    assert response.status_code == 200
    assert User.objects.count() == 1

    user = User.objects.first()
    assert user.email == "user@example.com"
    assert user.first_name == "User"
    assert user.last_name == "Example"


@pytest.mark.django_db
def test_facebook_login_invalid_access_token(api_client, facebook_social_app):
    access_token = "invalid"

    with requests_mock.mock() as mocked_requests:
        mocked_requests.get(
            "https://graph.facebook.com/v4.0/me?fields="
            f"id%2Cemail%2Cname%2Cfirst_name%2Clast_name&access_token={access_token}",
            text="{}",
            status_code=400,
        )
        response = api_client.post(reverse("facebook_login"), data={"access_token": access_token})

    assert response.status_code == 400
    assert User.objects.count() == 0


@pytest.mark.django_db
def test_email_registration_invalid_data(api_client):
    response = api_client.post(
        reverse("rest_register"),
        data={
            "first_name": "",
            "last_name": "",
            "email": "userexample.com",
            "password1": "1234example1234",
            "password2": "1234example1234",
        },
    )

    assert response.status_code == 400
    assert response.data == {
        "email": ["Enter a valid email address."],
        "first_name": ["This field may not be blank."],
        "last_name": ["This field may not be blank."],
    }


@pytest.mark.django_db
def test_email_registration(api_client):
    response = api_client.post(
        reverse("rest_register"),
        data={
            "first_name": "user first name",
            "last_name": "user last name",
            "email": "user@example.com",
            "password1": "1234example1234",
            "password2": "1234example1234",
        },
    )

    assert response.status_code == 201
    assert "key" in response.data


@pytest.mark.django_db
def test_email_registration_confirm_email(api_client, mailoutbox):
    response = api_client.post(
        reverse("rest_register"),
        data={
            "first_name": "user first name",
            "last_name": "user last name",
            "email": "user@example.com",
            "password1": "1234example1234",
            "password2": "1234example1234",
        },
    )

    assert response.status_code == 201
    assert len(mailoutbox) == 1

    # Find confirmation link in the last email sent by the app
    email_url_match = re.search(r"https?://[^/]*(/.*confirm-email/\S*/)", mailoutbox[0].body)

    assert email_url_match

    response = Client().get(email_url_match.groups()[0], follow=True)

    assert response.status_code == 200

    response = Client().post(email_url_match.groups()[0], follow=True)
    messages = list(get_messages(response.wsgi_request))

    assert response.redirect_chain[0][0] == email_url_match.groups()[0]
    assert "You have confirmed " in str(messages[0])


@pytest.mark.django_db
def test_email_login(api_client):
    user = UserFactory()
    user.set_password("1234example1234")
    user.save()

    response = api_client.post(
        reverse("rest_login"), data={"email": user.email, "password": "1234example1234"}
    )

    assert "key" in response.data
    assert response.status_code == 200


@pytest.mark.django_db
def test_email_login_invalid_password(api_client):
    user = UserFactory()
    user.set_password("1234example1234")
    user.save()

    response = api_client.post(
        reverse("rest_login"), data={"email": user.email, "password": "invalid"}
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_email_password_change(authenticated_api_client):
    new_password = "1234example1234-changed"

    response = authenticated_api_client.post(
        reverse("rest_password_change"),
        data={
            "email": authenticated_api_client.user.email,
            "new_password1": new_password,
            "new_password2": new_password,
        },
    )

    assert response.status_code == 200

    response = authenticated_api_client.post(
        reverse("rest_login"),
        data={"email": authenticated_api_client.user.email, "password": new_password},
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_email_reset_password(api_client, mailoutbox):
    user = UserFactory()
    response = api_client.post(reverse("rest_password_reset"), data={"email": user.email})

    assert response.status_code == 200
    assert len(mailoutbox) == 1

    email_url_match = re.search(r"https?://[^/]*(/.*password-reset/\S*)", mailoutbox[0].body)

    assert email_url_match

    new_password = "1234example1234-new"
    response = PasswordResetConfirmClient().post(
        path=email_url_match.groups()[0],
        data={"new_password1": new_password, "new_password2": new_password},
    )

    assert response.status_code == 302

    response = api_client.post(
        reverse("rest_login"), data={"email": user.email, "password": new_password}
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_email_reset_password_confirm(authenticated_api_client, mailoutbox):
    new_password = "1234example1234-new"

    response = authenticated_api_client.post(
        reverse("rest_password_reset_confirm"),
        data={
            "new_password1": new_password,
            "new_password2": new_password,
            "uid": force_str(urlsafe_base64_encode(force_bytes(authenticated_api_client.user.pk))),
            "token": default_token_generator.make_token(authenticated_api_client.user),
        },
    )

    assert response.status_code == 200

    response = authenticated_api_client.post(
        reverse("rest_login"),
        data={"email": authenticated_api_client.user.email, "password": new_password},
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_user_email_logout(authenticated_api_client):
    response = authenticated_api_client.post(reverse("rest_logout"))

    expected_response = {"detail": "Successfully logged out."}

    assert response.status_code == 200
    assert response.data == expected_response


@pytest.mark.django_db
def test_user_facebook_logout(api_client, facebook_social_app):
    access_token = "valid"

    with requests_mock.mock() as mocked_requests:
        # Intercept the call to Facebook API made in the FacebookLogin view
        mocked_requests.get(
            "https://graph.facebook.com/v4.0/me?fields="
            f"id%2Cemail%2Cname%2Cfirst_name%2Clast_name&access_token={access_token}",
            text=json.dumps(
                {
                    "id": "11111111111111111",
                    "name": "User Example",
                    "first_name": "User",
                    "last_name": "Example",
                    "email": "user@example.com",
                }
            ),
            status_code=200,
        )
        response = api_client.post(reverse("facebook_login"), data={"access_token": access_token})

    assert response.status_code == 200

    token = response.data["key"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    response = api_client.post(reverse("rest_logout"))

    expected_response = {"detail": "Successfully logged out."}

    assert response.status_code == 200
    assert response.data == expected_response


@pytest.mark.django_db
def test_user_google_logout(api_client, google_social_app, monkeypatch):
    access_token = "valid"

    monkeypatch.setattr(id_token, "verify_oauth2_token", mock_google_verify_oauth2_valid_token)

    response = api_client.post(reverse("google_login"), data={"access_token": access_token})

    token = response.data["key"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    response = api_client.post(reverse("rest_logout"))

    expected_response = {"detail": "Successfully logged out."}

    assert response.status_code == 200
    assert response.data == expected_response
