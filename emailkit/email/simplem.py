import asyncio
from emailkit.mailaccount import MailAccount
from emailkit.message import MailMessage
from .daemon import MailerDaemon


class SimpleMailer(MailerDaemon):
    def __init__(self, mailaccount_pool: list[MailAccount]):
        super().__init__(mailaccount_pool)
        
    def send_mail(
        self, mailmessage: MailMessage, sender=None, reporting=False
    ):
        # send one mail, or send a bunch of emails
        if mailmessage.use_default_sender_address is True:
            success, default_mail_address, index = self.get_default_email_account()
            if success is True:
                return asyncio.run(self.imailer(mailmessage, default_mail_address))
            else:
                raise Exception
        elif (sender is None) and (mailmessage._random_sender_address is True):
            return asyncio.run(self.imailer(mailmessage, self._mail_account_pool))
        elif isinstance(sender, MailMessage) is True:
            return asyncio.run(self.imailer(mailmessage, sender))
        else:
            raise Exception
        