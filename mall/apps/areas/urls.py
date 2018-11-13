from django.conf.urls import url
from . import views

urlpatterns = [

]

from rest_framework.routers import DefaultRouter

# 创建router
router = DefaultRouter()

# 设置url
router.register(r'infos', views.AreaViewSet, base_name='')

urlpatterns += router.urls
