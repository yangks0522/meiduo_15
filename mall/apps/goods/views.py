from django.shortcuts import render

# Create your views here.
"""
静态化其实就是生成一个html  让用户访问html

首页数据是变化的

1.查询数据
2.将查询的数据渲染到模板中
3.写入到指定的路径
"""
"""
获取商品列表  推荐信息
1.前端应该传递过来一个分类id,我们应该接收这个分类id
2.根据分类id查询商品数据,并对商品数据进行排序,并获取2个
3.需要对数据进行序列化操作   对象 -->　json
4.返回数据

GET         good/categories/cat_id/hotskus/
"""
from rest_framework.views import APIView
from goods.models import SKU
from .serializers import HotSKUSerializer
from rest_framework.response import Response

# class HotSKUView(APIView):
#     def get(self, request, category_id):
#         # 有分类  需要判断是否上架
#         skus = SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[:2]
#         serializer = HotSKUSerializer(skus,many=True)
#         return Response(serializer.data)


from rest_framework.generics import ListAPIView


class HotSKUView(ListAPIView):
    serializer_class = HotSKUSerializer

    def get_queryset(self):
        return SKU.objects.filter(category_id=self.kwargs['category_id'], is_launched=True).order_by('-sales')[:2]


"""
列表页面 数据获取
1.所有返回所有数据
2.分类排序
3.分页查询

GET     categories/(?P<category_id>\d+)/skus/?ordering=-price&page=3&page_size=2
"""
from rest_framework.filters import OrderingFilter
from utils.pagination import StandardResultsSetPagination


class SKUListView(ListAPIView):
    # 排序
    filter_backends = [OrderingFilter]
    # 设置排序字段
    ordering_fields = ['create_time', 'price', 'sales']
    # url ?ordering=字段名

    # 分页类
    pagination_class = StandardResultsSetPagination

    serializer_class = HotSKUSerializer

    def get_queryset(self):
        return SKU.objects.filter(category_id=self.kwargs['category_id'], is_launched=True)
