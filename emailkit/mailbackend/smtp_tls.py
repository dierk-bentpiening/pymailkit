import smtplib
import logging
from .smtp import SMTP
from emailkit.email import MailerDaemon
class SMTP_TLS(SMTP):

    def __init__(self, mailer_config: MailerDaemon=None, logger = None):
        self._mailer_config = mailer_config
        if logger == None:
            self._logger = logging.getLogger(__name__)
            self._logger.setLevel(logging.DEBUG)
        else:
            self._logger = logger
        super().__init__(self._mailer_config)

    def connect(self):
        self._logger.debug(f"Try to connect to {self._mailer_config.host}:{self._mailer_config.port}")
        smtp = smtplib.SMTP(self._mailer_config.host, self._mailer_config.port)
        smtp.ehlo()
        smtp.starttls()
        return self._authentificate(smtp)


