from listenclosely.services.base import BaseMessageServiceBackend
import sys
import threading
import time

class ConsoleMessageService(BaseMessageServiceBackend):
    
    def __init__(self, caller, *args, **kwargs):
        self.stream = kwargs.pop('stream', sys.stdout)
        self._lock = threading.RLock()
        super(ConsoleMessageService, self).__init__(caller, *args, **kwargs)
    
    def write_message(self, message):
        print(message)
    
    def send_message(self, id_service, content):
        """Write all messages to the stream in a thread-safe way."""
        if not content:
            return
        with self._lock:
            try:
                message = "Message: %s to %s" % (content, id_service)
                self.write_message(message)
                self.stream.flush()  # flush after each message
                return "message_id"
            except Exception:
                if not self.fail_silently:
                    raise
                
    def listen(self):
        with self._lock:
            try:
                self.write_message("Listening")
                time.sleep(10)
                self.stream.flush()  # flush after each message
            except Exception:
                if not self.fail_silently:
                    raise
                
    def disconnect(self):
        with self._lock:
            try:
                self.write_message("Disconnecting")
                self.stream.flush()  # flush after each message
            except Exception:
                if not self.fail_silently:
                    raise
        
    def on_message(self, id_service, content):
        self.caller.on_message(id_service, content)
        with self._lock:
            try:
                self.write_message("Message(id: %s, content: %s" % (id_service, content))
                self.stream.flush()  # flush after each message
            except Exception:
                if not self.fail_silently:
                    raise