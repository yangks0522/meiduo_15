from rest_framework import serializers
from .models import Area


# 省的序列化器
class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ['id', 'name']


# 市的序列化器
class AreaSubSerializer(serializers.ModelSerializer):
    subs = AreaSerializer(many=True)

    class Meta:
        model = Area
        fields = ['id', 'name', 'subs']
