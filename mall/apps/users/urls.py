from django.conf.urls import url
from . import views
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    # /users/usernames/(?P<username>\w{5,20})/count/
    # url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.RegisterUsernameCountView.as_view(), name='usernamecount'),
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.RegisterUsernameCountView.as_view(), name='usernamecount'),
    # /users/phones/(?P<mobile>1[345789]\d{9})/count/
    url(r'^phones/(?P<mobile>1[345789]\d{9})/count/$', views.RegisterPhoneCountAPIView.as_view(), name='phonecount'),
    url(r'^$', views.RegisterCreateUserView.as_view()),

    # 定义url
    url(r'^auths/', obtain_jwt_token),
]
"""
header:     eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
payload:    eyJleHAiOjE1NDE1ODA0NDQsInVzZXJfaWQiOjYsInVzZXJuYW1lIjoiaXRjYXN0IiwiZW1haWwiOiIifQ.
signature:  kXos2lYWkEIZPAb5lr7vWO-gqa4tDWbOPc4arQYyedE
"""

"""
我们蚕蛹jwt的认证方式     jwt的认证方式是在 rest_framework 基础上做的   jwt其实就是用的rest_framework认证 ,只不过返回的是token
rest_framework认证 是根据用户名来判断的
我们需要判断用户输入的是手机号还是用户名
"""
