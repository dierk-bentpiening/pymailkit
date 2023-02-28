"""_
    Test Class for MailAccount modul and units.
"""
import json
from pymailkit.mailaccount import MailAccount
from pymailkit.tools import JsonWerkzeug


class TestMailAccount:

    def test_init_mailaccount(self):
        """Testing of init_mailaccount 
        """
        mailaccount = MailAccount(
            "test@test.com", "testpassword", "smtp.test.com", 449, "SMTP_TLS")
        assert isinstance(
            mailaccount, MailAccount) == True, "Test if created obeject is instance of MailAccount"

    def test_set_as_default_email_account(self):
         mailaccount = MailAccount(
            "test@test.com", "testpassword", "smtp.test.com", 449, "SMTP_TLS")
         mailaccount.default = True
         assert mailaccount.default is True, "Test if mailaccount.default is True after setting it!"
        
        
    def test_account_json_serilization(self):
        mailaccount = MailAccount(
            "test@test.com", "testpassword", "smtp.test.com", 449, "SMTP_TLS")
        assert JsonWerkzeug().validatejson(mailaccount._to_json()) is True, "Test if mailaccount exported json is valid"
        
        
        
         