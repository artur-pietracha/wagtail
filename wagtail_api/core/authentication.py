from rest_framework.authentication import TokenAuthentication


class Authentication(TokenAuthentication):
    keyword = "Bearer"
