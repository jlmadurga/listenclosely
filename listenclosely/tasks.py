from __future__ import absolute_import

from celery import Task, shared_task
from functools import wraps

def listening_required(f):
    @wraps(f)
    def decorated_function(self, *args, **kwargs):
        if not self.facade.listening:
            listen.apply_async(queue=self.request.delivery_info['routing_key'])
            return self.retry()
        else:
            return f(self, *args, **kwargs)
    return decorated_function

   
class ListenCloselyTask(Task):
    abstract = True
    default_retry_delay = 0.5
       
    @property
    def facade(self):
        return self.app.listenclosely_app
    
    
@shared_task(base=ListenCloselyTask, bind=True, ignore_result=True)
def listen(self):
    if not self.facade.listening:
        return self.facade.listen()
    else:
        return "Already listening"

@shared_task(base=ListenCloselyTask, bind=True)
@listening_required
def disconnect(self):
    return self.facade.disconnect()

@shared_task(base=ListenCloselyTask, bind=True)
@listening_required
def send_message(self, number, content):
    self.facade.send_message(number, content)
    return True

@shared_task(base=ListenCloselyTask, bind=True)
@listening_required
def attend_pendings(self):
    self.facade.attend_pendings()    
    
@shared_task(base=ListenCloselyTask, bind=True)
@listening_required
def terminate_obsolete(self):
    self.facade.terminate_obsolete()