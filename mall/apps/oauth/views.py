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
        state = 'test'
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


