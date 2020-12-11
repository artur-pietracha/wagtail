from rest_auth.registration.serializers import SocialLoginSerializer


class AppleAuthSerializer(SocialLoginSerializer):
    def validate(self, attrs):
        if attrs.get("code"):
            attrs["access_token"] = attrs.get("code")
        return super().validate(attrs)
