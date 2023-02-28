"""
Main SMTP Class.
(C) 2023 Dierk-Bent Piening
E-Mail: dierk-bent.piening@mailbox.org

"""
import smtplib
import os
import time
import asyncio
from concurrent import futures


class SMTP(object):
    from pymailkit.email import MailerDaemon
    from pymailkit.message import MailMessage

    def __init__(self, mailer_config: MailerDaemon = None):
        self._mailer_config = mailer_config
        self._processes: list = []

    def connect(self):
        """abstract connection function"""

    def _authentificate(self, smtp):
        self._logger.debug(
            f"Try to authenticate against {self._mailer_config.host}:{self._mailer_config.port} with user {self._mailer_config.username}")
        smtp.login(self._mailer_config.username, self._mailer_config.password)
        return smtp
        
    async def send_mail(self, mailmessage: MailMessage):
        mailer = self.connect()
        mailer.sendmail(mailmessage._sender_address._mail_address,
                        mailmessage._recipient_address, mailmessage._get_message())