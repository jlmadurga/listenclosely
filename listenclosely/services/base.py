
class BaseMessageServiceBackend(object):
    """
    Abstract Service to send instant messages
    """
    def __init__(self, caller, fail_silently=False, **kwargs):
        self.fail_silently = fail_silently
        self.caller = caller
        
    def listen(self):
        """
        Connect to service and listen for receive messages.
        To implement in concrete services
        """
        raise NotImplementedError('subclasses of BaseMessageServiceBackend must override listen() method')
    
    def send_message(self, id_service, content):
        """
        Send message to a instant messages service
        To implement in concrete services
        :rtype string message_id: identifier for message service
        """
        raise NotImplementedError('subclasses of BaseMessageServiceBackend must override send_message() method')    
    
    def disconnect(self):
        """
        Disconnect to service.
        To implement in concrete services
        """
        raise NotImplementedError('subclasses of BaseMessageServiceBackend must override disconnect() method')