import pytest
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.facebook.provider import FacebookProvider

from django.conf import settings
from django.contrib.sites.models import Site

from rest_framework.test import APIClient

from .applesignin.provider import AppleProvider
from .core.adapters import GoogleProviderIdToken
from .user.tests.factories import UserFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_api_client():
    class APIClientWithUser(APIClient):
        user = UserFactory()

    client = APIClientWithUser()
    client.force_authenticate(user=client.user)
    return client


def setup_social_app(provider):
    app = SocialApp.objects.create(
        provider=provider.id,
        name=provider.id,
        client_id="app123id",
        key=provider.id,
        secret="dummy",
    )
    app.sites.add(Site.objects.get_current())


@pytest.fixture
def apple_social_app():
    setup_social_app(AppleProvider)


@pytest.fixture
def google_social_app():
    setup_social_app(GoogleProviderIdToken)


@pytest.fixture
def facebook_social_app():
    setup_social_app(FacebookProvider)


@pytest.fixture
def apple_shared_secret(monkeypatch):
    monkeypatch.setattr(settings, "APPLE_SHARED_SECRET", "password")
