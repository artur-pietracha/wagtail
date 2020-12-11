from allauth.account.views import ConfirmEmailView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_auth.registration.views import RegisterView, SocialLoginView, VerifyEmailView
from rest_auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
)

from django.urls import reverse

from rest_framework.permissions import AllowAny, IsAuthenticated

from ..applesignin.serializer import AppleAuthSerializer
from ..applesignin.views import AppleOAuth2Adapter
from .adapters import FacebookOAuth2AdapterV4, GoogleOAuth2AdapterIdToken
from .serializers import EmailLoginSerializer, EmailRegisterSerializer, SocialAuthSerializer


class FacebookLogin(SocialLoginView):
    serializer_class = SocialAuthSerializer
    adapter_class = FacebookOAuth2AdapterV4


class GoogleLogin(SocialLoginView):
    serializer_class = SocialAuthSerializer
    adapter_class = GoogleOAuth2AdapterIdToken
    client_class = OAuth2Client


class AppleLogin(SocialLoginView):
    serializer_class = AppleAuthSerializer
    adapter_class = AppleOAuth2Adapter
    client_class = OAuth2Client


class EmailRegister(RegisterView):
    permission_classes = (AllowAny,)
    serializer_class = EmailRegisterSerializer


class VerifyEmail(VerifyEmailView):
    permission_classes = (AllowAny,)


class EmailLogin(LoginView):
    permission_classes = (AllowAny,)
    serializer_class = EmailLoginSerializer


class Logout(LogoutView):
    permission_classes = (IsAuthenticated,)


class EmailPasswordChange(PasswordChangeView):
    permission_classes = (IsAuthenticated,)


class EmailPasswordReset(PasswordResetView):
    permission_classes = (AllowAny,)


class EmailPasswordResetConfirm(PasswordResetConfirmView):
    permission_classes = (AllowAny,)


class ConfirmEmail(ConfirmEmailView):
    template_name = "user/email_confirm.html"

    def get_redirect_url(self):
        return reverse("account_confirm_email", kwargs={"key": self.kwargs["key"]})
