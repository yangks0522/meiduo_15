from django_redis import get_redis_connection
from rest_framework import serializers

from goods.models import SKU


class CartSKUSerializer(serializers.ModelSerializer):
    """
    购物车商品数据序列化器
    """
    count = serializers.IntegerField(label='数量')

    class Meta:
        model = SKU
        fields = ('id', 'name', 'default_image_url', 'price', 'count')


class OrderPlacesSerialzier(serializers.Serializer):
    freight = serializers.DecimalField(label='运费', max_digits=10, decimal_places=2)
    # CartSKUSerializer(skus,many=True)
    skus = CartSKUSerializer(many=True)


from orders.models import OrderInfo
from .models import OrderGoods
from django.db import transaction


class OrderCommitSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderInfo
        fields = ('order_id', 'address', 'pay_method')
        read_only_fields = ('order_id',)
        extra_kwargs = {
            'address': {
                'write_only': True,
                'required': True,
            },
            'pay_method': {
                'write_only': True,
                'required': True
            }
        }

    def create(self, validated_data):
        """
        生成订单,保存订单商品
        订单商品需要订单ip
        生成订单
        1.获取user信息
        2.获取地址信息
        3.生成订单号
        4.运费 价格 数量
        5.支付方式
        6.状态
        保存订单商品信息
            redis
                hash  sku_id:count
                set     sku_id,sku_id 选中的

        7. 连接redis,获取redis数据
        8. 获取选中商品的信息  {sku_id:count}
        9. 根据id 获取商品的信息  [SKU,SKU,SKu]
        10.我们需要对 商品信息进行遍历
            11. 我们需要修改商品的库存和销量
            12. 我们需要累计 总的商品价格和数量
            13. 保存商品
        """
        # 1.获取user信息
        user = self.context['request'].user
        # 2.获取地址信息
        address = validated_data.get('address')
        # 3.生成订单号
        from django.utils import timezone
        order_id = timezone.now().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)
        # 4.运费 价格 数量
        total_count = 0
        from decimal import Decimal
        total_amount = Decimal('0')
        freight = Decimal('10.00')
        # 5.支付方式
        pay_method = validated_data.get('pay_method')
        # 6.状态 会因为 我们选择的支付方式而不同
        if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']:
            status = OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        else:
            status = OrderInfo.ORDER_STATUS_ENUM['UNPAID']
        # ! 事物 ! ***** 高并发   乐观锁
        with transaction.atomic():

            # 一 创建一个保存点
            point = transaction.savepoint()
            order = OrderInfo.objects.create(
                order_id=order_id,
                user=user,
                address=address,
                total_amount=total_amount,
                total_count=total_count,
                freight=freight,
                pay_method=pay_method,
                status=status
            )
            # 7. 连接redis,获取redis数据
            redis_conn = get_redis_connection('cart')
            sku_id_count = redis_conn.hgetall('cart_%s' % user.id)
            selected_ids = redis_conn.smembers('cart_selected_%s' % user.id)
            # 8. 获取选中商品的信息  {sku_id:count}
            selected_cart = {}
            for sku_id in selected_ids:
                selected_cart[int(sku_id)] = int(sku_id_count[sku_id])
            # 9. 根据id 获取商品的信息  [SKU,SKU,SKu]
            skus = SKU.objects.filter(pk__in=selected_cart.keys())
            # 10.我们需要对 商品信息进行遍历
            for sku in skus:
                # 11. 我们需要修改商品的库存和销量
                count = selected_cart[sku.id]
                # 判断数量和库存
                if count > sku.stock:
                    # 二 出问题的时候 回滚
                    # 回滚到 事务点处
                    transaction.savepoint_rollback(point)
                    raise serializers.ValidationError('库存不足')
                # 12. 我们需要累计 总的商品价格和数量
                # sku.stock -= count
                # sku.sales += count
                # # 13. 保存商品
                # sku.save()
                # 记录库存
                old_stock = sku.stock
                # 更新数据  最新数据
                new_stock = sku.stock - count
                new_sales = sku.sales + count
                # 修改之前在查询一次
                result = SKU.objects.filter(pk=sku.id, stock=old_stock).update(stock=new_stock, sales=new_sales)
                if result == 0:
                    raise serializers.ValidationError('下单失败')
                order.total_count += count
                order.total_amount += (sku.price * count)
                OrderGoods.objects.create(
                    order=order,
                    sku=sku,
                    count=count,
                    price=sku.price
                )
            order.save()
            transaction.savepoint_commit(point)
        return order
