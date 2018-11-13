from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response

from users.models import User, Address
from users.serializers import RegisterCreateUserSerializer, AddressAlterSerializer

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


class RegisterPhoneCountAPIView(APIView):
    """
    查询手机号的个数
    GET     /users/phones/(?P<mobile1[345789]\d{9})/count/
    """

    def get(self, request, mobile):
        # 通过模型查询获取手机号个数
        count = User.objects.filter(mobile=mobile).count()
        # 返回数据
        return Response({"count": count})


"""
1.前端应该将6个参数(username,password,password2,mobile,sms_code,allow)  传递给后端

接收前端提交的数据
校验数据
数据入库
返回响应

POST        users/

"""


# APIView
# GenericAPIView
# ListAPIView RetrieveAPIViews


class RegisterCreateUserView(APIView):
    def post(self, request):
        data = request.data
        serializer = RegisterCreateUserSerializer(data=data)
        serializer.is_valid()
        serializer.save()
        return Response(serializer.data)


"""
断点:
    在程序的入口处
    部分代码实现一个功能
    认为哪里有错误
    不知道就(每行都加)

事件的触发点
    很好的确定代码写在哪里

用户注册之后直接跳转到首页,默认表示已经登陆

注册完成应该返回给客户端一个token
如何生成token
在哪里返回token
"""

"""
1.校验 只有当前用户登陆
查询用户信息


GET     /users/infos/
"""

from rest_framework.permissions import IsAuthenticated
from .serializers import UserCenterSerializer

# class UserCenterView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         """
#         获取登陆用户的信息
#         返回数据
#         """
#         # 获取登陆用户的信息
#         user = request.user
#         # 返回数据
#         serializer = UserCenterSerializer(user)
#         return Response(serializer.data)

from rest_framework.generics import RetrieveAPIView


class UserCenterView(RetrieveAPIView):
    # 权限认证
    permission_classes = [IsAuthenticated]

    serializer_class = UserCenterSerializer

    # 重写get_object方法
    def get_object(self):
        # 获取指定某一个对象
        return self.request.user


"""
当用户点击设置的时候,输入邮箱信息   当用户点击保存时需要将邮箱信息发送给后端
这个接口必须登陆才能访问
1.接收邮箱数据
2.校验参数
3.更新数据
4.发送激活邮箱
5.返回响应

PUT     /users/emails/
"""
from rest_framework.permissions import IsAuthenticated
from .serializers import UserEmailSerializer
from mall import settings
from .utils import generic_active_url


class UserEmailView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        # 1.接收邮箱数据
        data = request.data
        user = request.user
        # 2.校验参数
        serializer = UserEmailSerializer(instance=user, data=data)
        serializer.is_valid(raise_exception=True)
        # 3.更新数据
        serializer.save()
        # 4.发送激活邮箱
        from celery_tasks.email.tasks import send_verify_mail
        send_verify_mail(data.get('email'), request.user.id)

        # from django.core.mail import send_mail
        # # subject, message, from_email, recipient_list,
        # subject = '美多商城激活邮件'
        # message = ''
        # from_email = settings.EMAIL_FROM
        # email = data.get('email')
        # recipient_list = [email]
        #
        # verify_url = generic_active_url(user.id, email)
        #
        # html_message = '<p>尊敬的用户您好！</p>' \
        #                '<p>感谢您使用美多商城。</p>' \
        #                '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
        #                '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)
        # send_mail(
        #     subject=subject,
        #     message=message,
        #     from_email=from_email,
        #     recipient_list=recipient_list,
        #     html_message=html_message
        # )

        # 5.返回响应
        return Response(serializer.data)


from rest_framework import status
from .utils import get_active_user


class UserActiveEmailView(APIView):
    def get(self, request):
        """
        当用户点击激活连接的时候,会跳转到一个页面,这个页面中含有 token(含有 用户id和email信息)信息
        前端需要发送一个ajax请求,将 token 发送给后端

        1. 接受token
        2. 对token进行解析
        3. 返回响应

        GET     /users/emails/verification/?token=xxx
        """
        # 1. 接受token
        token = request.query_params.get('token')
        if token is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 2. 对token进行解析
        user = get_active_user(token)
        if user is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user.email_active = True
        user.save()
        # 3. 返回响应
        return Response({'msg': 'ok'})


"""
新增地址功能

前段将用户提交的数据传递给后端
后端接收数据
校验数据
数据入库
返回响应


POST        users/addresses/
"""

from rest_framework.generics import CreateAPIView, ListAPIView, DestroyAPIView, UpdateAPIView
from .serializers import AddressSerializer


class AddressCreateView(ListAPIView, CreateAPIView):
    # 添加地址需要认证权限
    permission_classes = [IsAuthenticated]

    queryset = Address.objects.filter(is_deleted=False)

    serializer_class = AddressSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'addresses': serializer.data,
            'limit': 20,
            'user_id': request.user.id,
            'default_address_id': request.user.default_address_id
        })


class AddressDeleteView(DestroyAPIView, UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Address.objects.filter(is_deleted=False)

    serializer_class = AddressSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdderssAlterView(UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Address.objects.filter(is_deleted=False)

    serializer_class = AddressAlterSerializer


class AddressDefaultView(UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Address.objects.filter(is_deleted=False)

    serializer_class = AddressSerializer

    def update(self, request, *args, **kwargs):
        request.user.default_address = self.get_object()
        request.user.save()
        return Response({'msg': 'ok'})
