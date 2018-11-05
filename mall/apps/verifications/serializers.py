from rest_framework import serializers
from django_redis import get_redis_connection

# Serializer , ModelSerializer
# 我们的视图没有模型  选择Serializer
class RegisterSmsCodeSerializer(serializers.Serializer):
    text = serializers.CharField(label='图片验证码', min_length=4, max_length=4, required=True)
    image_code_id = serializers.UUIDField(label='uuid', required=True)
    """
    1.校验
        字段类型
        字段选项
        单个字段
        多个字段
        自定义
        校验图片验证码的时候  需要用到 text 和image_code_id 这两个字段
        选择多个字段进行校验
    """

    def validate(self, attrs):
        # 1.用户提交的图片验证码
        text = attrs.get('text')
        image_code_id = attrs.get('image_code_id')
        # 2.获取redis验证码
        redis_conn = get_redis_connection('code')
        redis_text = redis_conn.get("img_%s"%image_code_id)
        if redis_text is None:
            raise serializers.ValidationError('图片验证码已过期')
        # 3.比对校验
        # 2个注意点: redis_text时=是bytes类型    大小写 lower()
        if text.lower() != redis_text.decode().lower():
            raise serializers.ValidationError('图片验证码不一致')

        # 校验完成  需要返回attrs
        return attrs
