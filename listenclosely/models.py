# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_fsm import FSMField, transition
from django.utils.encoding import python_2_unicode_compatible
from listenclosely import managers
from django.utils.timezone import now
import datetime


class NoAgentFound(Exception):
    """
    Raised when strategy can not find agent to attend chat
    """


class AbstractContact(models.Model):
    id_service = models.CharField(_("Id Service"), unique=True, db_index=True, max_length=128)
    created = models.DateTimeField(_("Date created"), auto_now_add=True)
    
    class Meta:
        abstract = True
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")

@python_2_unicode_compatible
class Asker(AbstractContact):
    """
    Customer, client, ... the who ask a question and starts a chat
    """
    class Meta:
        verbose_name = _("Asker")
        verbose_name_plural = _("Askers")
        
    def __str__(self):
        return _(u"Asker(id_service: %(id_service)s") % {'id_service': self.id_service}

@python_2_unicode_compatible
class Agent(AbstractContact):
    """
    One who answer chat
    """
    OFFLINE, ONLINE, BUSY = "Offline", "Online", "Busy"
    STATE_CHOICES = (
        (OFFLINE, _("Offline")),
        (ONLINE, _("Online")),
        (BUSY, _("Busy")))
    state = FSMField(default=OFFLINE, choices=STATE_CHOICES)
    
    class Meta:
        verbose_name = _("Agent")
        verbose_name_plural = _("Agents")
        
    objects = models.Manager()
    offline = managers.OfflineAgentManager()
    online = managers.OnlineAgentManager()
    busy = managers.BusyAgentManager()
        
    def __str__(self):
        return _(u"Agent(id_service: %(id_service)s, state:%(state)s") % {'id_service': self.id_service,
                                                                          'state': self.state}
    
    @transition(field=state, source=OFFLINE, target=ONLINE)
    def register(self):
        """
        Agent is registered into the system so now is online to answers
        """

    @transition(field=state, source=ONLINE, target=OFFLINE)
    def unregister(self):
        """
        Agent is not online anymore
        """
    
    @transition(field=state, source=ONLINE, target=BUSY)
    def attend(self, chat):
        """
        Agent is assigned to a chat so it is busy answering
        """
        chat.agent = self
        
    @transition(field=state, source=BUSY, target=ONLINE)
    def release(self, chat):
        """
        Agent finishes chat
        """

@python_2_unicode_compatible
class Chat(models.Model):
    asker = models.ForeignKey(Asker, verbose_name=_("Asker"), related_name="chats")
    agent = models.ForeignKey(Agent, null=True, blank=True, verbose_name=_("Agent"), related_name="chats")
    created = models.DateTimeField(_("Date created"), auto_now_add=True)
    last_modified = models.DateTimeField(_("Last modified"), auto_now=True)
    
    PENDING, LIVE, TERMINATED = "Pending", "Live", "Terminated"
    STATE_CHOICES = (
        (PENDING, _("Pending")),
        (LIVE, _("Live")),
        (TERMINATED, _("Terminated")))
    state = FSMField(default=PENDING, choices=STATE_CHOICES)   
    
    class Meta:
        verbose_name = _("Chat")
        verbose_name_plural = _("Chats")
        
    objects = models.Manager()
    pending = managers.PendingChatsManager()
    live = managers.LiveChatsManager()
    terminated = managers.TerminatedChatsManager()
           
    def __str__(self):
        return _(u"Chat(asker: %(asker)s, agent: %(agent)s, state: %(state)s") % {'asker': self.asker,
                                                                                  'agent': self.agent,
                                                                                  'state': self.state}

    @transition(field=state, source=[PENDING, LIVE], target=LIVE)
    def handle_message(self, message_id_service, contact_id_service, content, listenclosely_app):
        message = Message(id_service_in=message_id_service,
                          chat=self,
                          content=content,
                          type=Message.INCOMING if contact_id_service == self.asker.id_service else Message.OUTGOING)
        if not self.agent:
            # get free online agents
            free_agent = listenclosely_app.strategy.free_agent()         
            if free_agent:
                free_agent.attend(self)
                free_agent.save()
            else:
                message.save()
                #  TODO: raise especific exception when no free agent to attend. Send auto message
                raise NoAgentFound("No agent to attend %s created by %s" % (self.id, contact_id_service))

        sent_id = listenclosely_app.service_backend.send_message(message.chat.agent.id_service if message.incoming()
                                                                 else message.chat.asker.id_service,
                                                                 content)
        if sent_id:
            message.id_service_out = sent_id
            message.t_sent = now()
        message.save()
    
    @transition(field=state, source=PENDING, target=LIVE)
    def attend_pending(self, agent, listenclosely_app):
        agent.attend(self)
        agent.save()
        for message in self.messages.all():
            sent = listenclosely_app.service_backend.send_message(message.chat.agent.id_service if message.incoming()
                                                                  else message.chat.asker.id_service,
                                                                  message.content)
            if sent:
                message.t_sent = now()
            message.save()
        
    @transition(field=state, source=LIVE, target=TERMINATED)
    def terminate(self):
        """
        Chat is finished and Agent is free
        """
        self.agent.release(self)
        self.agent.save()
        
    def is_obsolete(self, time_offset):
        """
        Check if chat is obsolete
        """
        return now() > datetime.timedelta(seconds=time_offset) + self.last_modified
        
@python_2_unicode_compatible
class Message(models.Model):
    id_service_in = models.CharField(_("Id Service In"), unique=True, db_index=True, max_length=128)
    id_service_out = models.CharField(_("Id service Out"), null=True, blank=True, max_length=128)
    chat = models.ForeignKey(Chat, verbose_name=_("Chat"), related_name="messages")
    created = models.DateTimeField(_("Date created"), auto_now_add=True)
    t_sent = models.DateTimeField(_("Date sent"), null=True, blank=True)
    content = models.TextField(_("Content"))
    
    INCOMING, OUTGOING = "Incoming", "Outgoing"
    TYPE_CHOICES = ((INCOMING, _("Incoming")),
                    (OUTGOING, _("Outgoing")),
                    )
    type = models.CharField(_("Type"), max_length=128, default=INCOMING, choices=TYPE_CHOICES)
    
    class Meta:
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")
           
    def incoming(self):
        return self.type == self.INCOMING
    
    def outgoing(self):
        return self.type == self.OUTGOING
        
    def __str__(self):
        return _(u"Chat(id_service: %(id_service)s, chat: %(chat)s") % {'id_service': self.id_service_in,
                                                                        'chat': self.chat}