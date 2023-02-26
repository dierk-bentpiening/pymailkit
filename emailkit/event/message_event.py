import time
import asyncio
import logging
from emailkit.event import Event
from emailkit.message import MailMessage
from emailkit.message import DefaultMessageSentCallbacks


class MessageEvent(Event):
    
    def __init__(self):
        self.eventhandler_instance = Event()
        self.subscriber_list: list[object] = [DefaultMessageSentCallbacks().default_callback]
            
        for subscriber in self.subscriber_list:
            self.eventhandler_instance += subscriber
        
    def _add_message_event_subscriber(self, method):
        if callable(method) is True:
            self.eventhandler_instance += method
        else:
            raise NotImplementedError
        
    def on_message_sent(self, message: MailMessage):
        """

        Args:
            message (MailMessage): Message which has been sent.
        """
        
        if isinstance(message, MailMessage):
            if message.issent is True:
                self.eventhandler_instance(message)
