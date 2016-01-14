from __future__ import absolute_import

import os

from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "demo_app.settings")

app = Celery('listenclosely')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
import django
django.setup()
from listenclosely.celery import ListenCloselyAppStep

app.steps['worker'].add(ListenCloselyAppStep)
@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
