from users.models import User


# 生成token 抽取代码
def jwt_response_payload_handler(token, user=None, request=None):
    return {
        # jwt 的token
        # user  就是已经认证之后的用户信息
        'token': token,
        'username': user.username,
        'user_id': user.id
    }


from django.contrib.auth.backends import ModelBackend

import re


def get_user(username):
    try:
        if re.match('^1[345789]\d{9}$', username):
            # 手机号
            user = User.objects.get(mobile=username)
        else:
            # 用户名
            user = User.objects.get(username=username)
    except User.DoseNotExist:
        return None
    return user


"""
n行代码实现了一个功能(方法),我们就可以将代码抽取(封装)出去
如果多次出现的代码(只要第二次出现就抽取)
抽取(封装)的思想是:
    将抽取的代码原封不动的放在一个函数,函数暂时不需要参数
    抽取的代码哪里有问题改哪里,其中的变量 变为函数的参数
    用抽取的函数  替换源代码
"""


class MobileUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # username有可能是手机号也有可能是用户名
        # 根据手机号规则，判断时用户名还是手机号
        # 根据username查询用户信息
        # try:
        #     if re.match('^1[345789]\d{9}$', username):
        #         # 手机号
        #         user = User.objects.get(mobile=username)
        #     else:
        #         # 用户名
        #         user = User.objects.get(username=username)
        # except User.DoseNotExist:
        #     user = None

        # 生成token
        user = get_user(username)

        # 校验用户的密码
        if user is not None and user.check_password(password):
            return user

        return None


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
                user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        if user.check_password(password):
            return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
