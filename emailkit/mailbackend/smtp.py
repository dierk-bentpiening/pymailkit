"""
Main SMTP Class.
(C) 2023 Dierk-Bent Piening
E-Mail: dierk-bent.piening@mailbox.org

"""
import smtplib
import os
import time
from concurrent import futures


class SMTP(object):
    from emailkit import MailerDaemon
    from emailkit import MailMessage

    def __init__(self, mailer_config: MailerDaemon=None):
        self._mailer_config = mailer_config

    def connect(self):
        """abstract connection function"""
    def _authentificate(self, smtp):
        self._logger.debug(f"Try to authenticate against {self._mailer_config.host}:{self._mailer_config.port} with user {self._mailer_config.username}")
        smtp.login(self._mailer_config.username, self._mailer_config.password)
        return smtp
    def _thread_sender(self, mailmessage: MailMessage):
        try:
            mailer = self.connect()
            mailer.sendmail(mailmessage._sender_address, mailmessage._recipient_address, str(mailmessage._get_message()))
        except Exception as email_exception:
            self._logger.error(f"Exception occured: {email_exception}")

    def send_mail(self, mailmessage: MailMessage):
        self._logger.debug("Starting MailKit Threaded SMTP Transmission...")
        with futures.ThreadPoolExecutor(max_workers=20) as mailer_thread:
            mailer_thread.submit(self._thread_sender, mailmessage)

