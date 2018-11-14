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
