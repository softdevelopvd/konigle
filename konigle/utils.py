from rest_framework_simplejwt.tokens import AccessToken

from unity.models import User


def is_token_valid(access_token):
    try:
        access_token = AccessToken(access_token)
        User.objects.get(id=access_token["user_id"])
        return True
    except:
        return False


def get_user_token(access_token):
    try:
        access_token = AccessToken(access_token)
        return User.objects.get(id=access_token["user_id"])
    except:
        return False
