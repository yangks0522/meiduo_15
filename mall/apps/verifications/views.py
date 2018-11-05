from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection

from verifications import constant

"""
一, 写需求
二, 根据需求决定采用那种请求方式
三, 确定视图 进行编码
1.前段需要发送给我一个uuid  , 我们接收到uuid 生成一个图片给前端
2.接收前段提供的uuid
3.生成图片验证码,保存图片验证码的数据
4.返回响应

GET     /verifications/imagecodes/(?P<image_code_id>.+)/
"""
"""
APIView
GenericView
ListAPIView,RetrieveAPIView
"""

class RegisterImageCodeView(APIView):
    def get(self,request,image_code_id):
        # 生成图片验证码
        text ,image = captcha.generate_captcha()
        # 保存图片验证码的数据
        redis_conn = get_redis_connection('code')
        redis_conn.setex('img_%s'%image_code_id,constant.IMAGE_CODE_EXPIRE_TIME,text)
        # 返回响应
        return HttpResponse(image,content_type='image/jpeg')