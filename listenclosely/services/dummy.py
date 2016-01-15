from listenclosely.services.base import BaseMessageServiceBackend
import random
import string


class DummyMessageService(BaseMessageServiceBackend):
    
    def __init__(self, caller, *args, **kwargs):
        super(DummyMessageService, self).__init__(caller, *args, **kwargs)
        self.incoming_messages = []
        self.outgoing_messages = []
    
    def listen(self):
        pass
    
    def _message_id(self):
        return ''.join(random.choice(string.ascii_lowercase) for i in range(10))

    def send_message(self, id_service, content):
        msg_id = self._message_id()  
        self.outgoing_messages.append((msg_id, id_service, content))
        return msg_id
    
    def on_message(self, id_service, content):
        self.caller.on_message(id_service, content)
        self.incoming_messages.append((id_service, content))
        
    def disconnect(self):
        pass