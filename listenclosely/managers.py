from django.db import models


class StateManager(models.Manager):
    """For searching/creating State Chats only."""

    def get_queryset(self):
        return super(StateManager, self).get_queryset().filter(
            state=self.state_filter)

    def get_or_create(self, **kwargs):
        return self.get_queryset().get_or_create(
            state=self.state_filter, **kwargs)

class PendingChatsManager(StateManager):
    """For searching/creating Pending Chats only."""
    state_filter = "Pending"
    
class LiveChatsManager(StateManager):
    """For searching/creating Live Chats only."""
    state_filter = "Live"
    
class TerminatedChatsManager(StateManager):
    """For searching/creating Terminated Chats only."""
    state_filter = "Terminated"
    
class OfflineAgentManager(StateManager):
    """For searching/creating Offline Agents only."""
    state_filter = "Offline"
    
class OnlineAgentManager(StateManager):
    """For searching/creating Online Agents only."""
    state_filter = "Online"
    
class BusyAgentManager(StateManager):
    """For searching/creating Busy Agents only."""
    state_filter = "Busy"