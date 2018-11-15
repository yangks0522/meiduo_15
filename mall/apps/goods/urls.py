from django.conf.urls import url
from . import views

urlpatterns = [
    # /goods/categories/(?P<category_id>\d+)/hotskus/
    url(r'^categories/(?P<category_id>\d+)/hotskus/$', views.HotSKUView.as_view(), name='hot'),
    url(r'^categories/(?P<category_id>\d+)/skus/$', views.SKUListView.as_view()),

]

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('search', views.SKUSearchViewSet, base_name='skus_search')

urlpatterns += router.urls
