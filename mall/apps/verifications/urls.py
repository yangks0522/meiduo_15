from django.conf.urls import url
from . import views

urlpatterns = [
    #verifications/imagecodes/(?P<image_code_id>.+)/
    url(r'^imagecodes/(?P<image_code_id>.+)/$',views.RegisterImageCodeView.as_view(),name='imagecode'),
    url(r'^sms_codes/(?P<mobile>1[345789]\d{9})/',views.RegisterSmsCodeView.as_view()),
]