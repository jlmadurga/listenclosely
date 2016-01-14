class BaseAgentStrategy(object):
    
    def free_agent(self):
        raise NotImplementedError('subclasses of BaseAgenStrategy must override free_agent method')
