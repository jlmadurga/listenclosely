========
Customization
========

Listenclosely is easy to be customized with your own requirements


------
Agent stategy
------

Just extend `strategies.base.BaseAgentStrategy` and define your own `free_agent` function::

	class FirstFreeAgentStrategy(BaseAgentStrategy):
    	"""
    	Choose first free agent 
    	"""
      
    	def free_agent(self):
        	free_agents = Agent.online.all()
        	if free_agents:
            	return free_agents[0]
        	return None
        	
Then configure settings::

	LISTENCLOSELY_AGENT_STRATEGY = 'your_strategy.YourAgentStrategy'
	
-----
Message Service Backend
-----

Extend `services.base.BaseMessageServiceBackend`. You must implement some methods::

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
        
Use other services as example. At the moment:
	* Whatsapp: https://github.com/jlmadurga/listenclosely-whatsapp
	* Telegram: https://github.com/jlmadurga/listenclosely-telegram



