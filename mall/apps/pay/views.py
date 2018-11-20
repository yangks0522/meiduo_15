from django.shortcuts import render

# Create your views here.
from pay.models import Payment

"""
1.创建应用(使用沙箱应用)  app_id  网关(api.meiduo.site)
2.设置两对公钥和私钥
    一对是我们的应用的
        公钥  我们需要在支付宝的网站上复制下来  放在一个有公钥开始和结束标识的文件中
        私钥  在支付宝的服务器上生成的
    一对是支付宝的
3.设置环境 app_id  公钥和私钥 sdk
4.按照文档开发

"""

"""
当用户点击支付按钮的时候 我们需要让前端发送一个ajax请求 发送给我们
    必须时登录用户才可以访问此接口
 接收参数 校验参数
 根据订单id查询数据
 创建支付宝对象
 调用支付宝方法生成order_string
 拼接url并且返回

 GET    /pay/orders/(?P<order_id>)\d+/

"""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from orders.models import OrderInfo
from rest_framework import status
from rest_framework.response import Response
from django.conf import settings
# from mall import settings
from alipay import AliPay


class PaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        # 接收参数 校验参数
        # 根据订单id查询数据
        try:
            # 为了查询的更准确 ,需要在添加几个查询条件
            # 查询未支付的订单  这个用户的订单
            order = OrderInfo.objects.get(
                order_id=order_id,
                user=request.user,
                status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']
            )
        except OrderInfo.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 创建支付宝对象
        app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )
        # 调用支付宝方法生成order_string
        subject = "测试订单"

        # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),  # 这个类型我们要由decimal转换为 str
            subject=subject,
            return_url="http://www.meiduo.site:8080/pay_success.html",
            notify_url=None  # 可选, 不填则使用默认notify url
        )
        # 拼接url并且返回
        url = settings.ALIPAY_URL + '?' + order_string
        return Response({'alipay_url': url})


"""
我们通过 git文档中的验证 就可以实现支付结果的查询
我们需要使用支付宝回传的一些字符串  这些字符串需要让前端传递过来

    PUT         /pay/status/?
"""


class PayStatusAPIView(APIView):
    def put(self, request):
        # 创建alipay对象
        app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )
        # 验证
        data = request.query_params.dict()
        # sign 不能参与签名验证
        signature = data.pop("sign")

        # verify
        success = alipay.verify(data, signature)
        if success:
            #　验证成功之后可以从data中获取支付宝的订单id 和我们的订单id
            # 支付宝的交易id
            trade_no = data.get('trade_no')
            # 把支付宝的订单id 和我们的订单id保存起来
            out_trade_no = data.get('out_trade_no')
            Payment.objects.create(
                order_id = out_trade_no,
                trade_id = trade_no,
            )
            # 更新订单状态
            OrderInfo.objects.filter(order_id=out_trade_no).update(status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'])
            # 返回支付宝的订单id
            return Response({'trade_id':trade_no})
