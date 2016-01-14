from listenclosely.strategies.base import BaseAgentStrategy
from listenclosely.models import Agent
class FirstFreeAgentStrategy(BaseAgentStrategy):
    """
    Choose first free agent 
    """
      
    def free_agent(self):
        free_agents = Agent.online.all()
        if free_agents:
            return free_agents[0]
        return None   