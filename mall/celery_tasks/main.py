"""
我们的任务 , worker,broker 都需要Celery去协调  所以我们需要创建一个Celery对象


"""

from celery import Celery

# import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mall.settings")

# 进行Celery允许配置
# 为celery使用django配置文件进行设置
import os

if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'mall.settings'

# 以上信息加载到 app创建前面

# selery也是需要使用到django项目中的配置信息的

# 创建celery对象
# 第一步
# 第一个参数,main 一般以celery的文件夹为名字,不要重复
app = Celery(main='celery_tasks')

# 第二步
# app设置broker
# app.config_from_object设置配置文件的路径
app.config_from_object('celery_tasks.config')

# 第三步
# celery可以自动检测任务,检测任务的路径就是任务包的路径
# autodiscover_tasks第一个参数是列表
# 列表中的元素 是任务包的路径
# 路径是从celery_tasks开始就可以
app.autodiscover_tasks(['celery_tasks.sms'])

# worker 是通过指令来执行的
# celery -A celery实例对象的文件路径   worker -l info

# 这个指令需要在虚拟环境中执行
# celery -A celery_tasks worker -l info

# celery -A celery_tasks.main worker -l info
