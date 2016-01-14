from django.conf import settings


LISTENCLOSELY_MESSAGE_SERVICE_BACKEND = getattr(settings, 'LISTENCLOSELY_MESSAGE_SERVICE_BACKEND', 
                                                'listenclosely.services.console.ConsoleMessageService')

LISTENCLOSELY_AGENT_STRATEGY = getattr(settings, 'LISTENCLOSELY_AGENT_STRATEGY',
                                       'listenclosely.strategies.first_free.FirstFreeAgentStrategy')

LISTENCLOSELY_QUERY_TIME_OBSOLETE = getattr(settings, 'LISTENCLOSELY_QUERY_TIME_OBSOLETE',
                                            '60')  # in seconds