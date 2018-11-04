from django.conf.urls import url
from . import views

urlpatterns = [
    # /users/usernames/(?P<username>\w{5,20})/count/
    # url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.RegisterUsernameCountView.as_view(), name='usernamecount'),
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.RegisterUsernameCountView.as_view(), name='usernamecount'),

]
