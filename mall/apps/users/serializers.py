from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response

from users.models import User, Address
import re
from django_redis import get_redis_connection

from rest_framework_jwt.settings import api_settings


# 生成 jwt  token
def produce_token(user):
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER

    # payload可以装在用户数据
    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)
    return token


# 入库有模型  选择ModelSerializer
class RegisterCreateUserSerializer(serializers.ModelSerializer):
    """
    username, password, password2, mobile, sms_code, allow

    自动写的字段也要添加到列表中
    """

    sms_code = serializers.CharField(label='短信验证码', min_length=6, max_length=6, write_only=True)
    password2 = serializers.CharField(label='确认密码', write_only=True)
    allow = serializers.CharField(label='确认协议', write_only=True)

    token = serializers.CharField(label='token', read_only=True)

    # token = serializers.CharField(label='token', required=False)

    # ModelSerializer自动生成字段的时候 是根据fields 列表生成的
    class Meta:
        model = User

        fields = ['username', 'password', 'mobile', 'sms_code', 'password2', 'allow', 'token']
        extra_kwargs = {
            'id': {'read_only': True},
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    """
    1.校验手机号        单个字段
    2.密码一致          多个字段
    3.短信校验          多个字段
    4.allow是否同意     单个字段
    """

    def validate_mobile(self, value):

        if not re.match('1[345789]\d{9}', value):
            raise serializers.ValidationError('手机号不满足要求')
        # 校验之后要返回回去
        return value

    def validate_allow(self, value):

        if value == False:
            raise serializers.ValidationError('您未同意协议')

    def validate(self, attrs):

        # 密码一致
        password = attrs.get('password')
        password2 = attrs.get('password2')
        mobile = attrs.get('mobile')
        sms_code = attrs.get('sms_code')
        if password != password2:
            raise serializers.ValidationError('密码不一致')

        # 短信
        # validate_note(mobile, sms_code)
        redis_conn = get_redis_connection('code')

        sms_code_redis = redis_conn.get("sms_%s" % mobile)

        if not sms_code_redis:
            raise serializers.ValidationError('验证码已过期')

        if sms_code_redis.decode() != sms_code:
            raise serializers.ValidationError('验证码错误')

        return attrs

    def create(self, validated_data):
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']

        user = User.objects.create(**validated_data)
        # 对密码进行加密
        user.set_password(validated_data['password'])
        user.save()

        # 生成token
        from rest_framework_jwt.settings import api_settings

        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER

        # payload可以装在用户数据
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        user.token = token
        return user


class UserCenterSerializer(serializers.ModelSerializer):
    """
    用户详细信息序列化器
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'email_active')


class UserEmailSerializer(serializers.ModelSerializer):
    """
    邮箱序列化器
    """

    class Meta:
        model = User
        fields = ('email',)


class AddressSerializer(serializers.ModelSerializer):
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')

    class Meta:
        model = Address
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')

    def create(self, validated_data):
        # Address模型类中有user属性,将user对象添加到模型类的创建参数中
        validated_data['user'] = self.context['request'].user
        # page = self.request.user.addresses.count()
        # if page > 20:
        #     return Response({'message': '保存地址数量已经达到上限'}, status=status.HTTP_400_BAD_REQUEST)
        # return Address.objects.create(**validated_data)
        return super().create(validated_data)


class AddressAlterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('title',)


from goods.models import SKU


class UserBrowerHistorySerializer(serializers.ModelSerializer):
    sku_id = serializers.IntegerField(label='商品编号', min_value=1, required=True)

    class Meta:
        model = SKU
        fields = ['sku_id']

# class UserBrowerHistorySerializer(serializers.Serializer):
#     """
#     添加用户浏览记录序列化器
#     """
#     sku_id = serializers.IntegerField(label='商品编号', min_value=1, required=True)
#
#     def validate_sku_id(self, value):
#         """
#         检查商品是否存在
#         """
#         try:
#             SKU.objects.get(pk=value)
#         except SKU.DoesNotExist:
#             raise serializers.ValidationError('商品不存在')
#         return value
#
#     def create(self, validated_data):
#         # 获取用户信息
#         user_id = self.context['request'].user.id
#         # 获取商品id
#         sku_id = validated_data['sku_id']
#         # 连接redis
#         redis_conn = get_redis_connection('history')
#         # 移除已经存在的
#         redis_conn.lrem('history_%s' % user_id, 0, sku_id)
#         # 添加新的记录
#         redis_conn.lpush('history_%s' % user_id, sku_id)
#         # 保存最多5条记录
#         redis_conn.ltrim('history_%s' % user_id, 0, 4)
#         return validated_data
