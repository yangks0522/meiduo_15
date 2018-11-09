from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response

"""
获取code
通过code换取token
通过token换取openid
"""

"""
用户点击qq登录按钮的时候  前端应该发送一个ajax请求 来获取要跳转的url
这个url是根据腾讯的文档来生成的
GET			/oauth/qq/statues/
"""

from rest_framework.views import APIView
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings


# from mall import settings

class OauthQQURLView(APIView):
    def get(self, request):
        state = '/'
        # 创建oauth对象
        # client_id=None, client_secret=None, redirect_uri=None, state=None
        oauth = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URI,
            state=state
        )
        login_url = oauth.get_qq_url()
        # 调用方法获取url
        return Response({'login_url': login_url})


"""
接受code:
我们获取到这个code 通过接口来换取token
有了token可以换取openid
跟库openid判断
GET 	oauth/qq/users/?code=xxxx
"""

from rest_framework import status
from .models import OAuthQQUser

from oauth.serializer import OauthQQUserSerializer


class OauthQQUserView(APIView):
    def get(self, request):
        # 接收code
        code = request.query_params.get('code')
        if code is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        oauth = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URI
        )
        # 根据code获取token
        access_token = oauth.get_access_token(code)
        # 根据token 获取openid
        openid = oauth.get_open_id(access_token)
        # 根据openid来判断
        # 如果库中有 openid  表示已经绑定过了  登录
        # 如果库中没有openid  表示没有绑定过
        # 判断手机号是否已经注册  注册判断密码
        # 没有注册绑定
        try:
            qquser = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            from oauth.utils import generate_save_token
            openid = generate_save_token(openid)
            return Response({
                'access_token': openid
            })

            # 没有绑定过
        else:
            from rest_framework_jwt.settings import api_settings

            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(qquser.user)
            token = jwt_encode_handler(payload)

            return Response({
                'user_id': qquser.user.id,
                'username': qquser.user.username,
                'token': token
            })

    def post(self, request):
        # 1.接收数据
        data = request.data
        serializer = OauthQQUserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        qquser = serializer.save()
        from rest_framework_jwt.settings import api_settings

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(qquser.user)
        token = jwt_encode_handler(payload)

        return Response({
            'user_id': qquser.user.id,
            'username': qquser.user.username,
            'token': token
        })


"""
用户点击绑定按钮的时候前端应该将手机号 , 密码, openid, sms_code 发送给后端
1.接收数据
2.对数据进行校验
    校验openid  和 sms_code
3.保存数据
    保存user 和 openid
    判断手机号
        如果注册过  判断密码是否正确
        如果没有注册过 需要创建用户
4.返回响应

POST

"""
