from emailkit.message import MailMessage


class TestMailMessage:

    def test_create_mail_message(self):
        mail_message = MailMessage("rectest@test.com", "mail subject", "message body", "John Tester",)
        assert type(mail_message) is MailMessage, "MailMessage Object created"

    def test_set_sender_default_account(self):
        mail_message = MailMessage("rectest@test.com", "mail subject", "message body", "John Tester",)
        mail_message.use_default_sender_address = True
        assert isinstance(mail_message, MailMessage) is True, "Test if MailMessage Object created"
        assert mail_message.use_default_sender_address is True, "Test if mail_message is marked true with use_default_sender_address"


