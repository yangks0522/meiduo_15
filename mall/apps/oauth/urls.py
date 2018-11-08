from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^qq/statues/$', views.OauthQQURLView.as_view())
]
