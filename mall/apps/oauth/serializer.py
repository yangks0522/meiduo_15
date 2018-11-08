from rest_framework import serializers

from oauth.models import OAuthQQUser
from users.models import User


class OauthQQUserSerializer(serializers.Serializer):
    """
    1.对数据进行校验
    校验openid  和 sms_code
    判断手机号
        如果注册过  判断密码是否正确
        如果没有注册过 需要创建用户
    """
    access_token = serializers.CharField(label='操作凭证')
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')
    password = serializers.CharField(label='密码', max_length=20, min_length=8)
    sms_code = serializers.CharField(label='短信验证码')

    def validate(self, attrs):
        # 1.对数据进行校验
        access_token = attrs['access_token']
        # 校验openid  和 sms_code
        from oauth.utils import check_open_id
        openid = check_open_id(access_token)
        if openid is None:
            raise serializers.ValidationError('access_token错误')
        attrs['openid'] = openid
        sms_code = attrs.get('sms_code')
        # from django_redis import get_redis_connection
        # redis_conn = get_redis_connection('code')
        # redis_code = redis_conn.get('sms_%s' % attrs['moblie'])
        # if redis_code is None:
        #     raise serializers.ValidationError('短信验证码已过期')
        # if redis_code.decode != sms_code:
        #     raise serializers.ValidationError('验证码不一致')
        from users.serializers import validate_note
        validate_note(attrs['mobile'], sms_code)
        # 判断手机号
        mobile = attrs.get('mobile')
        try:
            user = User.objects.get(mobile=mobile)
        except:
            # 如果没有注册过 需要创建用户
            # 创建用户的代码写在这里也行
            pass
        else:
            # 如果注册过  判断密码是否正确
            if not user.check_password(attrs['password']):
                raise serializers.ValidationError('密码不正确')
            attrs['user'] = user

        return attrs

    def create(self, validated_data):
        """
        最终要保存user 和 openid信息
        """
        user = validated_data.get('user')
        openid = validated_data.get('openid')
        if user is None:
            # 创建
            user = User.objects.create(
                username=validated_data.get('mobile'),
                mobile=validated_data.get('mobile'),
                password=validated_data.get('password')
            )
            user.set_password(validated_data.get('password'))
            user.save()
        qquser = OAuthQQUser.objects.create(
            user=user,
            openid=openid
        )
        return qquser
