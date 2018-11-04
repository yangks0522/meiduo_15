from django.conf.urls import url
from . import views

urlpatterns = [
    # /users/usernames/(?P<username>\w{5,20})/count/
    # url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.RegisterUsernameCountView.as_view(), name='usernamecount'),
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.RegisterUsernameCountView.as_view(), name='usernamecount'),
    # /users/phones/(?P<mobile>1[345789]\d{9})/count/
    url(r'^phones/(?P<mobile>1[345789]\d{9})/count/$', views.ReigsterPhoneCountAPIView.as_view(), name='phonecount'),
]
