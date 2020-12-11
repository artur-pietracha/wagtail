from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class AppleAccount(ProviderAccount):
    pass


class AppleProvider(OAuth2Provider):
    id = "apple"
    name = "Apple"

    account_class = AppleAccount

    def extract_uid(self, data):
        return data["sub"]

    def extract_common_fields(self, data):
        return dict(email=data.get("email"))


provider_classes = [AppleProvider]
