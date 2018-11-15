from haystack import indexes

from .models import SKU


# 我们要检索的类
class SKUIndex(indexes.SearchIndex, indexes.Indexable):
    """
    SKU索引数据模型类
    """
    # 每个都SearchIndex需要有一个（也是唯一一个）字段 document=True。这向Haystack和搜索引擎指示哪个字段是在其中搜索的主要字段。
    text = indexes.CharField(document=True, use_template=True)

    id = indexes.IntegerField(model_attr='id')
    name = indexes.CharField(model_attr='name')
    price = indexes.CharField(model_attr='price')
    default_image_url = indexes.CharField(model_attr='default_image_url')
    comments = indexes.IntegerField(model_attr='comments')

    def get_model(self):
        """返回建立索引的模型类"""
        return SKU

    def index_queryset(self, using=None):
        """返回要建立索引的数据查询集"""
        return self.get_model().objects.filter(is_launched=True)