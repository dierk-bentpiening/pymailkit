import asyncio
from .mailmessage import MailMessage
from .report import SentMessageReport


class DefaultMessageSentCallbacks:
    def default_callback(self, message,) -> tuple[bool, SentMessageReport]:
        return True, SentMessageReport(message)