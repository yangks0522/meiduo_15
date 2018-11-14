from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.utils.deconstruct import deconstructible
from mall import settings


# 您的自定义存储系统必须是以下子类 django.core.files.storage.Storage
@deconstructible
class MyStorage(Storage):
    # Django必须能够在没有任何参数的情况下实例化您的存储系统。    不能传参数
    # 这意味着任何设置都应该来自django.conf.settings
    def __init__(self, conf_path=None, ip=None):
        if not conf_path:
            conf_path = settings.FDFS_CLIENT_CONF
        self.conf_path = conf_path
        if not ip:
            ip = settings.FDFS_URL
        self.ip = ip

    # 打开图片
    # 因为我们通过http方式获取图片,所以不需要在此方法中写任何代码
    def _open(self, name, mode='rb'):
        pass

    def _save(self, name, content, max_length=None):
        # 创建客户端的实例对象
        # client = Fdfs_client('utils/fastdfs/client.conf')
        # client = Fdfs_client(settings.FDFS_CLIENT_CONF)
        client = Fdfs_client(self.conf_path)
        # 上传图片
        # name 只是图片名字不是绝对路径
        # content内容, 图片的内容  我们需要read()方法读取图片的资源
        # read() 读取的图片时二进制
        data = content.read()
        # client.upload_by_filename() 需要知道文件的绝对路径
        # client.append_by_buffer() 上传图片二进制   会返回上传结果
        result = client.append_by_buffer(data)
        # {'Group name': 'group1',
        # 'Status': 'Upload successed.',
        # 'Local file name': '/home/python/Desktop/images/77.png',
        #  'Uploaded size': '56.00KB',
        # 'Remote file_id': 'group1/M00/00/00/wKjHgFvqw02AH5wBAADhzT61YcA573.png',
        #  'Storage IP': '192.168.199.128'}

        # 　判断上传结果,获取file_id
        if result.get('Status') == 'Upload successed':
            # 上传成功
            file_id = result.get('Remote file_id')
            # 需要将file_id 返回给系统. 系统会使用file_id
            return file_id
        else:
            raise Exception('上传失败')

    # exists存在
    # 判断图片是否存在
    # 返回一个false就可以,false可以处理重名请求   不会出现覆盖情况
    def exists(self, name):
        return False

    # 默认url返回name值 name的值其实就是file_id的值
    # 访问图片时真是路径是:http://ip:port/ + file_id
    # 所以返回url时 直接将拼接好的url返回
    def url(self, name):
        # return 'http://192.168.199.128:8888/' + name
        # return settings.FDFS_URL + name
        return self.ip + name
