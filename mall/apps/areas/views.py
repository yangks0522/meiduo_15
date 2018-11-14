from django.shortcuts import render

# Create your views here.


"""

areas/infos/        获取省份信息
areas/infos/pk/     市,区县信息

"""

"""
获取查询结果集
    areas = Areas.objects.filter(parent_id__isnull=True)
将结果给序列化器
返回响应

"""
from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import Area
from .serializers import AreaSerializer, AreaSubSerializer
from rest_framework_extensions.cache.mixins import ListCacheResponseMixin, CacheResponseMixin, \
    RetrieveCacheResponseMixin


class AreaViewSet(CacheResponseMixin, ReadOnlyModelViewSet):
    pagination_class = None

    def get_queryset(self):

        if self.action == 'list':
            return Area.objects.filter(parent_id__isnull=True)
        else:
            return Area.objects.all()

    # serializer_class = AreaSerializer

    def get_serializer_class(self):

        if self.action == 'list':
            return AreaSerializer
        else:
            return AreaSubSerializer
