from __future__ import absolute_import
from celery import bootsteps
import logging
from listenclosely.app import ListenCloselyApp
from listenclosely import conf
from django.utils.module_loading import import_string


logger = logging.getLogger(__name__)

class ListenCloselyAppStep(bootsteps.StartStopStep):    
    
    def __init__(self, worker, **kwargs):
        """
        :param worker: celery worker
        """
        worker.app.listenclosely_app = ListenCloselyApp(import_string(conf.LISTENCLOSELY_MESSAGE_SERVICE_BACKEND),
                                                        import_string(conf.LISTENCLOSELY_AGENT_STRATEGY),
                                                        int(conf.LISTENCLOSELY_QUERY_TIME_OBSOLETE))
        logger.info("Listenclosely App initialized")

    def stop(self, worker):     
        logger.info("Stopping Listenclosely App")
        if worker.app.listenclosely_app.listening:
            worker.app.listenclosely_app.disconnect()
            logger.info("Disconnect Listenclosely App")
