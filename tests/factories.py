# coding=utf-8
from factory.django import DjangoModelFactory
from factory import Sequence, SubFactory, Factory
from factory.fuzzy import FuzzyText
from listenclosely.models import AbstractContact, Asker, Agent, Chat, Message
from listenclosely.app import ListenCloselyApp
from listenclosely.services.dummy import DummyMessageService
from listenclosely.strategies.first_free import FirstFreeAgentStrategy

class AsbtractContactFactory(DjangoModelFactory):
    class Meta:
        model = AbstractContact
        abstract = True
        django_get_or_create = ('id_service',)
    id_service = Sequence(lambda n: 'service_id_%d' % n)

class AskerFactory(AsbtractContactFactory):
    class Meta:
        model = Asker
    id_service = Sequence(lambda n: 'asker_service_id_%d' % n)
    
class AgentFactory(AsbtractContactFactory):
    class Meta:
        model = Agent
    id_service = Sequence(lambda n: 'agent_service_id_%d' % n)
    
class ChatFactory(DjangoModelFactory):
    class Meta:
        model = Chat
    asker = SubFactory(AskerFactory)

class MessageFactory(DjangoModelFactory):
    class Meta:
        model = Message
    chat = SubFactory(ChatFactory)
    content = FuzzyText()
    
class ListenCloselyAppFactory(Factory):
    class Meta:
        model = ListenCloselyApp
    message_service_backend_class = DummyMessageService
    agent_strategy_class = FirstFreeAgentStrategy
    time_obsolete_offset = 60  # seconds
