from random import randint

from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.response import Response

from libs.yuntongxun.sms import CCP
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

"""
当用户点击获取短信验证码的时候,前段应该将手机号,图片验证码和uuid(image_code_id) 发送给后端
1.接收前段数据
2.校验数据
3.生成短信验证码
4.发送短信
5.返回响应

APIView
GenericView             配和Mixin使用
ListAPIView,RetrieveAPIView

GET     verifications/sms_codes/mobile/uuid/text/
GET     verifications/sms_codes/?mobile=xxx&uuid=xxx&text=xxx

GET     verifications/sms_codes/(?P<mobile>1[345789]\d{9})/?uuid=xxx&text=xxx

"""
from .serializers import RegisterSmsCodeSerializer


class RegisterSmsCodeView(APIView):
    def get(self,request,mobile):
        # 1.接收前段数据
        params = request.query_params
        # 2.校验数据
        serializer = RegisterSmsCodeSerializer(data=params)
        serializer.is_valid(raise_exception=True)
        # 3.生成短信验证码
        sms_code = '%06d'%randint(0,999999)
        # 4.保存短信,发送短信
        redis_conn = get_redis_connection('code')
        redis_conn.setex('sms_%s'%mobile,constant.MOBILE_CODE_EXPIRE_TIME,sms_code)

        # CCP().send_template_sms(mobile,[sms_code, 5], 1)
        from celery_tasks.sms.tasks import send_sms_code

        # delay的参数 和 send_sms_code任务的参数是对应的
        send_sms_code.delay(mobile,sms_code)

        # 5.返回响应
        return Response({'msg':'ok'})

