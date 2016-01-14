#!/usr/bin/env python
# -*- coding: utf-8 -*-

from listenclosely.models import Agent, Chat, Message, NoAgentFound
from tests.factories import AgentFactory, ChatFactory
from tests import BaseTestColdCenter

class TestAgent(BaseTestColdCenter):
    
    def setUp(self):
        super(TestAgent, self).setUp()
        self.agent = AgentFactory()
        self.chat = ChatFactory()
        
    def test_creation_state(self):
        self.assertAgentState(self.agent, Agent.OFFLINE)
        
    def test_register_state(self):
        self._register(self.agent)
        
    def test_unregister_state(self):
        self._register(self.agent)
        self._unregister(self.agent)

    def test_attend_state(self):
        self._register(self.agent)
        self._attend(self.agent, self.chat)

    def test_release_state(self):
        self._register(self.agent)
        self._attend(self.agent, self.chat)
        self._release(self.agent)
    
class TestChat(BaseTestColdCenter):   

    def setUp(self):
        super(TestChat, self).setUp()
        self.chat = ChatFactory()
        self.agent = AgentFactory()
        self.question = "text question"
        self.answer = "text_answer"
        self.message_id = self._gen_id()
        
    def test_creation_state(self):
        self.assertChatState(self.chat, Chat.PENDING)
        
    def test_handle_message_no_agent_to_assign(self):
        self.assertRaises(NoAgentFound, self.chat.handle_message, self.message_id, self.chat.asker.id_service, 
                          self.question, self.listenclosely_app)   
        
    def test_handle_message_assign_agent(self):
        self._register(self.agent)
        self.agent.save()
        self.chat.handle_message(self.message_id, self.chat.asker.id_service, self.question, self.listenclosely_app)
        self.chat.save()
        self.assertChatState(self.chat, Chat.LIVE)
        self.assertEqual(self.chat.agent, self.agent)
        self.assertAgentState(self.chat.agent, Agent.BUSY)
        self.assertEqual(1, Message.objects.count())
        message = Message.objects.all()[0]
        self.assertEqual(message.id_service_in, self.message_id)
        self.assertEqual(message.content, self.question)
        self.assertEqual(message.type, Message.INCOMING)
        self.assertEqual(message.chat, self.chat)
        self.assertMessageServiceBackend(message.id_service_out, self.chat.agent.id_service, self.question)
        
    def test_handle_message_already_assigned(self):
        self._register(self.agent)
        self.agent.save()
        self._attend(self.agent, self.chat)
        self.agent.save()
        self.assertEqual(self.chat.agent, self.agent)
        self.assertAgentState(self.agent, Agent.BUSY)
        self.chat.handle_message(self.message_id, self.chat.asker.id_service, self.question, self.listenclosely_app)
        self.chat.save()
        self.assertChatState(self.chat, Chat.LIVE)
        self.assertEqual(1, Message.objects.count())
        message = Message.objects.all()[0]
        self.assertEqual(message.id_service_in, self.message_id)
        self.assertEqual(message.content, self.question)
        self.assertEqual(message.type, Message.INCOMING)
        self.assertEqual(message.chat, self.chat)
        self.assertMessageServiceBackend(message.id_service_out, self.chat.agent.id_service, self.question)
        
    def test_handle_message_answer(self):
        self._register(self.agent)
        self.agent.save()
        self._attend(self.agent, self.chat)
        self.agent.save()
        self.assertEqual(self.chat.agent, self.agent)
        self.assertAgentState(self.agent, Agent.BUSY)
        self.chat.handle_message(self.message_id, self.chat.agent.id_service, self.answer, self.listenclosely_app)
        self.chat.save()
        self.assertChatState(self.chat, Chat.LIVE)
        self.assertEqual(1, Message.objects.count())
        message = Message.objects.all()[0]
        self.assertEqual(message.id_service_in, self.message_id)
        self.assertEqual(message.content, self.answer)
        self.assertEqual(message.type, Message.OUTGOING)
        self.assertEqual(message.chat, self.chat)
        self.assertMessageServiceBackend(message.id_service_out, self.chat.asker.id_service, self.answer)
        
    def test_terminate(self):
        self._register(self.agent)
        self.agent.save()
        self.chat.handle_message(self.message_id, self.chat.asker.id_service, self.question, self.listenclosely_app)
        self.chat.save()
        self.assertChatState(self.chat, Chat.LIVE)
        self.assertAgentState(self.chat.agent, Agent.BUSY)
        self.chat.terminate()
        self.assertChatState(self.chat, Chat.TERMINATED)
        self.assertAgentState(self.chat.agent, Agent.ONLINE)        