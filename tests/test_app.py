#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tests import BaseTestColdCenter
from tests.factories import AgentFactory, ChatFactory, AskerFactory
from listenclosely.models import Agent, Chat, Message, Asker

class TestColdCenter(BaseTestColdCenter):

    def setUp(self):
        super(TestColdCenter, self).setUp()
        self.agent = AgentFactory()
        self.agent.save()
        self.asker = AskerFactory()
        self.asker.save()
        self.question = "question content"
        self.answer = "answer content"
        self.message_id = self._gen_id() 

    def test_attend_pending_one_query_one_free_agent(self):
        self.query = ChatFactory()
        self.query.asker = self.asker
        self.query.save()
        self._register(self.agent)
        self.agent.save()
        self.assertNumberAgentEachState(0, 1, 0)
        self.assertNumberChatEachState(1, 0, 0)
        queries_attended = self.listenclosely_app.attend_pendings()
        self.assertEqual(1, len(queries_attended))
        self.assertEqual(queries_attended[0], Chat.live.all()[0])
        self.assertNumberAgentEachState(0, 0, 1)
        self.assertNumberChatEachState(0, 1, 0)
        self.query = Chat.objects.all()[0]
        self.assertChatState(self.query, Chat.LIVE)
        self.assertEqual(self.agent, self.query.agent)
        self.assertAgentState(self.query.agent, Agent.BUSY)
        
    def test_attend_pending_one_query_no_free_agent(self):
        self.query = ChatFactory()
        self.query.asker = self.asker
        self.query.save()
        self.assertNumberAgentEachState(1, 0, 0)
        self.assertNumberChatEachState(1, 0, 0)
        queries_attended = self.listenclosely_app.attend_pendings()
        self.assertEqual(0, len(queries_attended))
        self.assertNumberAgentEachState(1, 0, 0)
        self.assertNumberChatEachState(1, 0, 0)
        
    def test_attend_pending_no_peding_queries(self):
        self.query = ChatFactory()
        self._register(self.agent)
        self.agent.save()
        self.query.handle_message(self.message_id, self.query.asker.id_service, self.question, self.listenclosely_app)
        self.query.save()
        self.assertNumberAgentEachState(0, 0, 1)
        self.assertNumberChatEachState(0, 1, 0)
        queries_attended = self.listenclosely_app.attend_pendings()
        self.assertEqual(0, len(queries_attended))
        self.assertNumberAgentEachState(0, 0, 1)
        self.assertNumberChatEachState(0, 1, 0)

    def test_terminate_obsolete_one(self):
        self.query = ChatFactory()
        self._register(self.agent)
        self.agent.save()
        self.query.handle_message(self.message_id, self.query.asker.id_service, self.question, self.listenclosely_app)
        self.query.save()
        self.assertNumberAgentEachState(0, 0, 1)
        self.assertNumberChatEachState(0, 1, 0)
        self.listenclosely_app.time_obsolete_offset = -1
        queries_terminated = self.listenclosely_app.terminate_obsolete()
        self.assertEqual(1, len(queries_terminated))
        self.assertEqual(queries_terminated[0], Chat.terminated.all()[0])
        self.assertNumberChatEachState(0, 0, 1)
        self.assertNumberAgentEachState(0, 1, 0)
        
    def test_terminate_obsolete_no_obsolete(self):
        self.query = ChatFactory()
        self._register(self.agent)
        self.agent.save()
        self.query.handle_message(self.message_id, self.query.asker.id_service, self.question, self.listenclosely_app)
        self.query.save()
        self.assertNumberAgentEachState(0, 0, 1)
        self.assertNumberChatEachState(0, 1, 0)
        queries_terminated = self.listenclosely_app.terminate_obsolete()
        self.assertEqual(0, len(queries_terminated))
        self.assertNumberChatEachState(0, 1, 0)
        self.assertNumberAgentEachState(0, 0, 1)
        
    def test_terminate_obsolete_no_live(self):
        self.query = ChatFactory()
        self.assertNumberChatEachState(1, 0, 0)
        self.listenclosely_app.time_obsolete_offset = -1
        queries_terminated = self.listenclosely_app.terminate_obsolete()
        self.assertEqual(0, len(queries_terminated))
        self.assertNumberChatEachState(1, 0, 0)
        
    def test_on_message_asker_new_question_with_free_agent(self):
        self._register(self.agent)
        self.agent.save()
        self.assertNumberAgentEachState(0, 1, 0)
        self.assertNumberChatEachState(0, 0, 0)
        self.listenclosely_app.on_message(self.message_id, self.asker.id_service, self.question)
        self.assertNumberAgentEachState(0, 0, 1)
        self.assertNumberChatEachState(0, 1, 0)
        message = Chat.live.all()[0].messages.all()[0]
        self.assertMessageServiceBackend(message.id_service_out, self.agent.id_service, self.question)
        
    def test_on_message_new_asker_new_question_with_free_agent(self):
        self._register(self.agent)
        self.agent.save()
        self.assertNumberAgentEachState(0, 1, 0)
        self.assertNumberChatEachState(0, 0, 0)
        new_asker_id = "new_asker_id"
        self.listenclosely_app.on_message(self.message_id, new_asker_id, self.question)
        self.assertNumberAgentEachState(0, 0, 1)
        self.assertNumberChatEachState(0, 1, 0)
        asker = Asker.objects.get(id_service=new_asker_id)
        self.assertEqual(asker.id_service, new_asker_id)
        message = Chat.live.all()[0].messages.all()[0]
        self.assertMessageServiceBackend(message.id_service_out, self.agent.id_service, self.question)

    def test_on_message_with_no_free_agent(self):
        self.assertNumberAgentEachState(1, 0, 0)
        self.assertNumberChatEachState(0, 0, 0)
        self.listenclosely_app.on_message(self.message_id, self.asker.id_service, self.question)
        self.assertNumberAgentEachState(1, 0, 0)
        self.assertNumberChatEachState(1, 0, 0)    
        self.query = Chat.pending.all()[0]
        self.assertEqual(1, self.query.messages.count())
        self.assertEqual(None, self.query.messages.all()[0].t_sent)
        
    def test_on_message_from_agent_with_no_query(self):
        self._register(self.agent)
        self.agent.save()
        self.assertNumberAgentEachState(0, 1, 0)
        self.assertNumberChatEachState(0, 0, 0)
        self.listenclosely_app.on_message(self.message_id, self.agent.id_service, self.answer)
        self.assertNumberAgentEachState(0, 1, 0)
        self.assertNumberChatEachState(0, 0, 0)
        self.assertEqual(0, Message.objects.count())
        
    def test_on_message_answer_to_current_query(self):
        self._register(self.agent)
        self.agent.save()
        self.assertNumberAgentEachState(0, 1, 0)
        self.assertNumberChatEachState(0, 0, 0)
        new_asker_id = "new_asker_id"
        self.listenclosely_app.on_message(self.message_id, new_asker_id, self.question)
        self.assertNumberAgentEachState(0, 0, 1)
        self.assertNumberChatEachState(0, 1, 0)
        message = Chat.live.all()[0].messages.all()[0]
        self.assertMessageServiceBackend(message.id_service_out, self.agent.id_service, self.question)
        self.listenclosely_app.on_message(self.message_id + "2", self.agent.id_service, self.answer)
        self.assertNumberAgentEachState(0, 0, 1)
        self.assertNumberChatEachState(0, 1, 0)
        query = Chat.live.get(agent__id_service=self.agent.id_service)
        self.assertEqual(2, query.messages.count())
        message = Chat.live.all()[0].messages.all()[1]
        self.assertMessageServiceBackend(message.id_service_out, new_asker_id, self.answer)

    def test_on_message_question_to_current_attended_query(self):
        self._register(self.agent)
        self.agent.save()
        self.assertNumberAgentEachState(0, 1, 0)
        self.assertNumberChatEachState(0, 0, 0)
        self.listenclosely_app.on_message(self.message_id, self.asker.id_service, self.question)
        self.assertNumberAgentEachState(0, 0, 1)
        self.assertNumberChatEachState(0, 1, 0)
        message = Chat.live.all()[0].messages.all()[0]
        self.assertMessageServiceBackend(message.id_service_out, self.agent.id_service, self.question)
        self.listenclosely_app.on_message(self.message_id + "2", self.asker.id_service, self.question + "2")
        self.assertNumberAgentEachState(0, 0, 1)
        self.assertNumberChatEachState(0, 1, 0)
        message = Chat.live.all()[0].messages.all()[1]
        self.assertMessageServiceBackend(message.id_service_out, self.agent.id_service, self.question + "2")