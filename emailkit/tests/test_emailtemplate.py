import time
import emailkit.profiler
from emailkit import MailAccount
from emailkit import MailerDaemon
from emailkit.message import MailMessage

class TestEmailTemplate:
    def test_init_of_template(self):
        account = [MailAccount("test@test.com", "testpw", "smtp.test.com", 667, "SMTP_TLS")]
        mailer = MailerDaemon(account)
        message = mailer.message_from_template("example")
        assert isinstance(message, MailMessage) is True, "Check if template get generated correctly from templatefile."
        