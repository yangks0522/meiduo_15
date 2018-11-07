from rest_framework import serializers
from users.models import User
import re
from django_redis import get_redis_connection


# 入库有模型  选择ModelSerializer
class RegisterCreateUserSerializer(serializers.ModelSerializer):
    """
    username, password, password2, mobile, sms_code, allow

    自动写的字段也要添加到列表中
    """

    sms_code = serializers.CharField(label='短信验证码', min_length=6, max_length=6, write_only=True)
    password2 = serializers.CharField(label='确认密码', write_only=True)
    allow = serializers.CharField(label='确认协议', write_only=True)

    # ModelSerializer自动生成字段的时候 是根据fields 列表生成的
    class Meta:
        model = User

        fields = ['username', 'password', 'mobile', 'sms_code', 'password2', 'allow']

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
        return user
