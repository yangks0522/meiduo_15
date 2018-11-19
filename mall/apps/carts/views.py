from django.shortcuts import render

# Create your views here.

"""
区分登录用户和未登录用户
传jwt登录  没传没登录
    request.user
    判断request.user的状态
登录用户保存到redis中
为登录用户保存到cookie中

保存数据都是三个 : sku_id(商品id), count(商品个数),selected(选中状态)

数据保存到redis中,如何选择数据的结构
    redis是保存在内存中的不能随意浪费
String:     key:value
Hash:       hash_key:   key: value
List:       list_key:   value,value,value
Set:        set_key:    value5,value2,value8
Zset:       zset_key:   value1,value2,value3

cookie的处理
    [
        sku_id:{count:xxx,selected:xxx},
        1:{count:5,selected:True},
        3:{count:2,selected:False
    ]
"""

"""
用户在详情页面中点击添加,前端应该发送一个ajax请求, 将sku_id,count,jwt(可选),selected(可选)
1.接收数据对数据进行校验
2.获取sku_id  count   selected
3.获取用户,根据用户信息,判断登陆状态
4.登录存储redis中
    连接redis
    保存数据到redis中
    返回响应
5.未登录存储cookie中
    先读取cookie信息,判断cookie中是否有cookie信息     str --> base64 --> pickle --> dict
        如果有需要读取
        没有不用管
    更新购物车信息     dict
    对购物车信息进行处理 dict --> pickle --> base64 --> str
    返回响应

POST            /cart/
"""
from rest_framework.views import APIView
from carts.serializers import CartSerializer, CartSKUSerializer
from django_redis import get_redis_connection

from rest_framework.response import Response
from goods.models import SKU
from .serializers import CartDeleteSerializer
import pickle
import base64


class CartView(APIView):
    # 如果传递的token有问题就不能实现购物车功能
    # 不进行验证重写视图perform_authentication方法
    def perform_authentication(self, request):
        pass

    def post(self, request):
        # 1.接收数据对数据进行校验
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 2.获取sku_id  count   selected
        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.data.get('count')
        selected = serializer.data.get('selected')

        # 3.获取用户,根据用户信息,判断登陆状态
        try:
            user = request.user
        except Exception:
            user = None
        # 判断用户登陆状态   request.user.is_authenticated 认证用户为True  匿名为False
        if user is not None and user.is_authenticated:
            # 4.登录存储redis中
            # 连接redis
            redis_conn = get_redis_connection('cart')
            # 保存数据到redis中
            # user = request.user
            # redis_conn.hset("cart_%s" % user.id, sku_id, count)
            pl = redis_conn.pipeline()
            # 记录购物车商品数量,hash
            pl.hincrby('cart_%s' % user.id, sku_id, count)
            # 勾选
            pl.sadd('cart_selected_%s' % user.id, sku_id)
            # 管道执行命令
            pl.execute()
            # 返回响应
            return Response(serializer.data)

        else:
            # 5.未登录存储cookie中    读取request.COOKIES.get()
            #     先读取cookie信息,判断cookie中是否有cookie信息     str --> base64 --> pickle --> dict
            cart_str = request.COOKIES.get('cart')
            if cart_str is not None:
                # 如果有需要读取
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                # 没有不用管
                cart_dict = {}
            # 更新购物车信息     dict
            if sku_id in cart_dict:
                # 存在
                # 获取原来的个数
                orginal_count = cart_dict[sku_id]['count']
                # 累加
                count += orginal_count
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            # 对明文加密
            dumps = pickle.dumps(cart_dict)

            encode = base64.b64encode(dumps)
            # 经过base64编码之后,返回的还是bytes类型, 转换为str类型
            new_cookie = encode.decode()
            response = Response(serializer.data)

            response.set_cookie('cart', new_cookie)
            # 返回响应
            return response

    """
    用户点击购物车列表,应该让前端传递一个 jwt token (前端在headers中填写)

    1. 获取用户信息
    2. 根据用户信息进行判断
    3. 登录用户redis
        连接redis
        获取数据
            hash: sku_id:count
            set:  sku_id
        根据id查询商品的详细信息[SKU,SKU]
        对对象列表进行序列化
        返回响应
    4. 未登录用户获取cookie
        读取cookie数据
        判断是否存在cookie数据  存在转换数据,不存在初始化购物车
            cart = {sku_id:{}}
        获取商品id
        根据id查询商品的详细信息
        对对象列表进行序列化
        返回响应

    GET      /cart/
    """

    def get(self, request):
        try:
            user = request.user
        except Exception:
            user = None

        if user is not None and user.is_authenticated:
            redis_conn = get_redis_connection('cart')
            sku_count = redis_conn.hgetall('cart_%s' % user.id)
            selected_ids = redis_conn.smembers('cart_selected_%s' % user.id)
            # 将redis的数据格式转换为cart样式
            cart = {}
            # 对sku_count 进行遍历
            for sku_id, count in sku_count.items():

                if sku_id in selected_ids:
                    selected = True
                else:
                    selected = False

                cart[int(sku_id)] = {
                    'count': int(count),
                    'selected': selected
                }
        else:
            cookie_str = request.COOKIES.get('cart')
            if cookie_str is not None:
                cart = pickle.loads(base64.b64decode(cookie_str.encode()))
            else:
                cart = {}
        ids = cart.keys()

        skus = SKU.objects.filter(id__in=ids)
        for sku in skus:
            sku.count = cart[sku.id]['count']
            sku.selected = cart[sku.id]['selected']

        serializer = CartSKUSerializer(skus, many=True)
        return Response(serializer.data)

    """
    修改购物车的业务逻辑

    用户在修改数据的时候,前端应该将修改之后的sku_Id ,count ,selected发送给后端
    count 是用户最终的值       幂等
    1. 接收数据,并进行数据的校验
    2. 获取sku_id,count,selected的值
    3. 获取用户信息,并进行判断
    4. 登陆用户redis
        连接redis,
        更新数据
        返回数据(一定要将最终的商品数量返回回去)
    5. 未登录用户 cookie
        读取cookie,并判断数据是否存在
        更新数据dict
        对字典进行处理
        返回响应(一定要将最终的商品数量返回回去)
    """

    def put(self, request):
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.data.get('sku_id')
        count = serializer.data.get('count')
        selected = serializer.data.get('selected')
        try:
            user = request.user
        except Exception:
            user = None
        if user is not None and user.is_authenticated:
            redis_conn = get_redis_connection('cart')
            redis_conn.hset('cart_%s' % user.id, sku_id, count)
            if selected:
                redis_conn.sadd('cart_selected_%s' % user.id, sku_id)
            else:
                redis_conn.srem('cart_selected_%s' % user.id, sku_id)
            return Response(serializer.data)
        else:
            cookie_str = request.COOKIES.get('cart')
            if cookie_str is not None:
                cart = pickle.loads(base64.b64decode(cookie_str))
            else:
                cart = {}
            if sku_id in cart:
                cart[sku_id] = {
                    'count': count,
                    'selected': selected
                }
            new_cookie = base64.b64encode(pickle.dumps(cart)).decode()
            response = Response(serializer.data)
            response.set_cookie('cart', new_cookie)
            return response

    """
    删除功能
    用户点击删除按钮的时候,点短应该发送一个ajax请求,请求中包含 sku_id        jwt
    1. 接收参数,并对参数进行校验
    2. 获取用户信息,并根据用户信息进行判断
    3. 登录用户redis
        3.1 连接redis
        3.2 删除数据 hash,set
        3.3 返回响应
    4. 未登录用户 cookie
        4.1 获取cookie数据并进行判断
        4.2 删除数据
        4.3 dict 对购物车数据进行处理
        4.4 返回响应
    """

    def delete(self, request):
        serializer = CartDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.data.get('sku_id')
        try:
            user = request.user
        except Exception:
            user = None

        if user is not None and user.is_authenticated:
            redis_conn = get_redis_connection('cart')
            redis_conn.hdel('cart_%s' % user.id, sku_id)
            redis_conn.srem('cart_selected_%s' % user.id, sku_id)
            return Response(serializer.data)
        else:
            cookie_str = request.COOKIES.get('cart')
            if cookie_str is not None:
                cart = pickle.loads(base64.b64decode(cookie_str))
            else:
                cart = {}
            if sku_id in cart:
                del cart[sku_id]
            new_cookie = base64.b64encode(pickle.dumps(cart)).decode()
            response = Response(serializer.data)
            response.set_cookie('cart', new_cookie)
            return response
