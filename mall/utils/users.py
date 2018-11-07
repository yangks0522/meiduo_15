from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        # jwt 的token
        # user  就是已经认证之后的用户信息
        'token': token,
        'user': user.username,
        'user_id': user.id
    }


from django.contrib.auth.backends import ModelBackend

import re


class MobileUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # username有可能是手机号也有可能是用户名
        # 根据手机号规则，判断时用户名还是手机号
        # 根据username查询用户信息
        try:
            if re.match('^1[345789]\d{9}$', username):
                # 手机号
                user = User.objects.get(mobile=username)
            else:
                # 用户名
                user = User.objects.get(mobile=username)
        except User.DoseNotExist:
            user = None

        # 校验用户的密码
        if user.check_password(password):
            return user


        # user = User.objects.get(mobile)


class SettingsBackend(object):
    """
    Authenticate against the settings ADMIN_LOGIN and ADMIN_PASSWORD.

    Use the login name and a hash of the password. For example:

    ADMIN_LOGIN = 'admin'
    ADMIN_PASSWORD = 'pbkdf2_sha256$30000$Vo0VlMnkR4Bk$qEvtdyZRWTcOsCnI/oQ7fVOu1XAURIZYoOZ3iq8Dr4M='
    """

    def authenticate(self, request, username=None, password=None):
        try:
            if re.match('^1[345789]\d{9}$', username):
                # 手机号
                user = User.objects.get(mobile=username)
            else:
                # 用户名
                user = User.objects.get(mobile=username)
        except User.DoseNotExist:
            user = None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None