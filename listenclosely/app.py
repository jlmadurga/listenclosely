from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
import logging
from listenclosely.models import Chat, Agent, Asker, NoAgentFound
from listenclosely.services.exceptions import AuthenticationError, ConnectionError


logger = logging.getLogger(__name__)

class ListenCloselyApp(object):
    
    def __init__(self, message_service_backend_class, agent_strategy_class, time_obsolete_offset):
        self.service_backend = message_service_backend_class(self)
        self.time_obsolete_offset = time_obsolete_offset
        self.strategy = agent_strategy_class()
        self.listening = False       
    
    def listen(self):
        """
        Listen/Connect to message service loop to start receiving messages.
        Do not include in constructor, in this way it can be included in tasks
        """
        self.listening = True
        try:
            self.service_backend.listen()
        except AuthenticationError:
            self.listening = False
            raise
        else:
            self.listening = False
            
    def disconnect(self):
        """
        Disconnect and not listen anymore
        """
        try:
            self.service_backend.disconnect()
        except ConnectionError:
            raise
        else:
            self.listening = False
        
    def attend_pendings(self):
        """
        Check all chats created with no agent assigned yet.
        Schedule a timer timeout to call it.
        """
        chats_attended = []
        pending_chats = Chat.pending.all()
        for pending_chat in pending_chats:
            free_agent = self.strategy.free_agent() 
            if free_agent:
                pending_chat.attend_pending(free_agent, self)
                pending_chat.save()
                chats_attended.append(pending_chat)
            else:
                break
        return chats_attended

    def terminate_obsolete(self):
        """
        Check chats can be considered as obsolete to terminate them
        """
        chats_terminated = []
        live_chats = Chat.live.all()
        for live_chat in live_chats:
            if live_chat.is_obsolete(self.time_obsolete_offset):
                live_chat.terminate()
                live_chat.save()
                chats_terminated.append(live_chat)
        return chats_terminated
    
    def send_message(self, id_service, content):
        message_id = self.service_backend.send_message(id_service, content)
        return message_id
                  
    def _new_chat_processing(self, message_id_service, contact_id_service, content):
        try:
            Agent.objects.get(id_service=contact_id_service)
        except ObjectDoesNotExist:
            asker, _ = Asker.objects.get_or_create(id_service=contact_id_service)
            chat = Chat(asker=asker)
            chat.save()
            try:
                chat.handle_message(message_id_service, contact_id_service, content, self)
                chat.save()
            except NoAgentFound:
                # No agent to attend chat
                # TODO: automessage to inform asker to wait
                logging.info("Chat %s from %s not attended. No free agents" % (chat.id, asker.id_service))
        else:
            # Agent not attending any chat
            # TODO: automessage to warning agent
            logging.warning("Message %s from %s with no chat ignored" % (message_id_service, 
                                                                         contact_id_service))
   
    def on_message(self, message_id_service, contact_id_service, content):
        """
        To use as callback in message service backend
        """
        try:
            live_chat = Chat.live.get(
                Q(agent__id_service=contact_id_service) | Q(asker__id_service=contact_id_service))            
        except ObjectDoesNotExist:
            self._new_chat_processing(message_id_service, contact_id_service, content)
        else:
            live_chat.handle_message(message_id_service, contact_id_service, content, self)