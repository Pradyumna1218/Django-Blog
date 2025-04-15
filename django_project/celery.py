from __future__ import unicode_literals, absolute_import
import os
from celery import Celery
from django.conf import settings
import django
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')

django.setup()

app = Celery('django_project')

app.conf.enable_utc = False
app.conf.update(timezone= 'Asia/Kathmandu')
app.config_from_object(settings, namespace= 'CELERY')

app.conf.beat_schedule = {
    'soft-delete-after-5pm': {
        'task': 'blog.tasks.soft_delete_post',
        'schedule': crontab(minute=0, hour=17, day_of_week='0'),  
    },
    'testing': {
        'task': 'blog.tasks.soft_delete_post',
        'schedule': crontab(minute=7, hour=12),  
    },
}

app.autodiscover_tasks()

@app.task(bind= True)
def debug_task(self):
    print (f'Request: {self.requst!r}')