import time
import emailkit.tools.profiler
from emailkit import MailAccount
from emailkit.email import SimpleMailer
from emailkit.message import MailMessage

class TestEmailTemplate:
    def test_init_of_template(self):
        account = [MailAccount("test@test.com", "testpw", "smtp.test.com", 667, "SMTP_TLS")]
        mailer = SimpleMailer(account) 
        message = mailer.message_from_template("example")
        assert isinstance(message, MailMessage) is True, "Check if template get generated correctly from templatefile."
        