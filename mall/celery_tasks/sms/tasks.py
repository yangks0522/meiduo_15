"""
Celery
1.任务
    任务的文件名必须是 tasks  因为我们的Celery实例对象会自动检测任务,检测任务的文件必须是tasks
    我们的任务必须经过 Celery的实例对象的tasks装饰器 装饰才可以被Celery调用
2.broker
3.worker

"""
from libs.yuntongxun.sms import CCP
from celery_tasks.main import app


@app.task
def send_sms_code(mobile, sms_code):
    CCP().send_template_sms(mobile, [sms_code, 5], 1)
