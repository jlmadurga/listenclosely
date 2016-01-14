# -*- coding: utf-8 -*-
from django.test import TestCase
from tests.factories import ListenCloselyAppFactory
from listenclosely.models import Agent, Chat
import time

class BaseTestColdCenter(TestCase):    
    
    def setUp(self):
        self.listenclosely_app = ListenCloselyAppFactory()
    
    def assertAgentState(self, agent, state):
        self.assertEqual(agent.state, state)
        
    def assertChatState(self, chat, state):
        self.assertEqual(chat.state, state)
        
    def assertMessageServiceBackend(self, msg_id, to_id_service, message_content):
        self.assertEqual(1, len(self.listenclosely_app.service_backend.outgoing_messages))
        sent_message = self.listenclosely_app.service_backend.outgoing_messages.pop()
        self.assertEqual(sent_message[0], msg_id)
        self.assertEqual(sent_message[1], to_id_service)
        self.assertEqual(sent_message[2], message_content)
        
    def assertNumberAgentEachState(self, num_offline, num_online, num_busy):
        self.assertEqual(num_offline, Agent.offline.count())
        self.assertEqual(num_online, Agent.online.count())
        self.assertEqual(num_busy, Agent.busy.count())
        
    def assertNumberChatEachState(self, num_pending, num_live, num_terminated):
        self.assertEqual(num_pending, Chat.pending.count())
        self.assertEqual(num_live, Chat.live.count())
        self.assertEqual(num_terminated, Chat.terminated.count())
        
    def _gen_id(self):
        return str(time.time())
        
    def _register(self, agent):
        agent.register()
        self.assertAgentState(agent, Agent.ONLINE)
        
    def _unregister(self, agent):
        agent.unregister()
        self.assertAgentState(agent, Agent.OFFLINE)
        
    def _attend(self, agent, chat):
        agent.attend(chat)
        self.assertAgentState(agent, Agent.BUSY)
        
    def _release(self, agent):
        agent.release(self.chat)
        self.assertAgentState(agent, Agent.ONLINE)