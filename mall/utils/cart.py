"""
# 分析具体情况
redis的数据原封不动的保留
cookie数据要合并到 redis的时候,我们就来分析 cookie数据 就三个: sku_id,count,selected
1. cookie中 含有商品id,redis中没有, 这个时候  将cookie的id添加进来,数量以cookie为主
2. cookie中 含有商品id,redis也有, 这个时候  数量怎么办,  以cookie为主

代码是具体化的失误转换为抽象的东西

1.获取cookie数据
2.获取redis数据
3.合并
4.将更新的数据  写入到redis
5.删除cookie
"""
import pickle
import base64
from django_redis import get_redis_connection


def merge_cookie_to_redis(request, user, response):
    cookie_str = request.COOKIES.get('cart')
    if cookie_str is not None:
        cookie_cart = pickle.loads(base64.b64decode(cookie_str))
        redis_conn = get_redis_connection('cart')
        hash_cart = redis_conn.hgetall('cart_%s' % user.id)
        cart = {}
        for sku_id, count in hash_cart.items():
            cart[int(sku_id)] = int(count)
        selected_ids = []
        for sku_id, count_selected_dict in cookie_cart.items():
            cart[sku_id] = count_selected_dict['count']
            if count_selected_dict['selected']:
                selected_ids.append(sku_id)
        redis_conn.hmset('cart_%s' % user.id, cart)
        redis_conn.sadd('cart_selected_%s' % user.id, *selected_ids)
        response.delete_cookie('cart')
        return response
    return response
