from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response

from users.models import User

"""
用户名
一, 确定需求
二, 确定采用那种请求方式 和 url
三, 实现
1.前段发送一个ajax请求,给后端 用户名

2.后端接收用户名
3.查询校验是或否重复
4.返回响应

GET     /users/usernames/(?P<username>\w{5,20})/count/

"""
# APIView
# GenericAPIView        列表视图和详情视图 通用支持,一般和Mixin配合使用
# ListAPIView,RetrieveAPIView
from rest_framework.views import APIView

"""
1.前段传递过来的数据 已经在url中校验过了
2.我们也不需要 序列化器
"""


class RegisterUsernameCountView(APIView):
    def get(self, request, username):
        """
        1.后端接收用户名
        2.查询校验是或否重复
        3.返回响应
        """
        # 1.后端接收用户名
        # username
        # 2.查询校验是或否重复
        count = User.objects.filter(username=username).count()
        # 3.返回响应
        return Response({'count': count})


"""
手机号
一, 确定需求
二, 确定使用那种请求方式和url
三, 实现代码

1.前段发送一个ajax请求给后端, 手机号
2.后端接收手机号
3.查询校验是否手机号是否已经注册过用户(手机号个数)
4.返回响应
请求方式:       GET     /users/phones/(?P<mobile1[345789]\d{9})/count/
"""


class ReigsterPhoneCountAPIView(APIView):
    """
    查询手机号的个数
    GET     /users/phones/(?P<mobile1[345789]\d{9})/count/
    """
    def get(self,request,mobile):
        # 通过模型查询获取手机号个数
        count = User.objects.filter(mobile=mobile).count()
        # 返回数据
        return Response({"count":count})