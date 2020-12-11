from .base import *  # noqa
from .base import env
from .constants import *  # noqa


INSTALLED_APPS = ["whitenoise.runserver_nostatic"] + INSTALLED_APPS  # noqa

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

SOCIAL_AUTH_APPLE_KEY_ID = env("SOCIAL_AUTH_APPLE_KEY_ID", default="asdasdasda")  # noqa
SOCIAL_AUTH_APPLE_TEAM_ID = env("SOCIAL_AUTH_APPLE_TEAM_ID", default="asdasdasda")  # noqa
SOCIAL_AUTH_APPLE_PRIVATE_KEY = env(  # noqa
    "SOCIAL_AUTH_APPLE_PRIVATE_KEY",
    default="""-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgevZzL1gdAFr88hb2
OF/2NxApJCzGCEDdfSp6VQO30hyhRANCAAQRWz+jn65BtOMvdyHKcvjBeBSDZH2r
1RTwjmYSi9R/zpBnuQ4EiMnCqfMPWiZqB4QdbAd0E7oH50VpuZ1P087G
-----END PRIVATE KEY-----""",
)
