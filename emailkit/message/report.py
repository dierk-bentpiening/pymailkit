import time
import datetime
from uuid import uuid4
from emailkit.tools import JsonWerkzeug
from emailkit.mailaccount import MailAccount
from .mailmessage import MailMessage
class SentMessageReport:
    def __init__(self, mailmessage: MailMessage):
        self.id: str = f"{uuid4()}"
        self._mailmessage: MailMessage = mailmessage
        self.time_sended = datetime.datetime.now().strftime("HH:mm:ss")
        self.date_sended = datetime.datetime.now().strftime("YYYY-MM-DD")
        self.sender_name = self._mailmessage._sender
        self.sender_account_address = self._mailmessage._sender_address._mail_address
        self.sender_account_smtp_server: str = self._mailmessage._sender_address._smtp_host
        self.sender_account_smtp_port: int = self._mailmessage._sender_address._smtp_port
        self.smtp_server: str = f"smtp://{self.sender_account_smtp_server}:{self.sender_account_smtp_port}"
        self.subject: str = self._mailmessage._subject
        self.message: str = self._mailmessage._message
        
        

    @property
    def sended (self) -> bool:
        """sended attribute get method (sended attribute: getter/setter)

        Returns:
            bool: returns true if the mailmessage was sent successfully.
        """
        return self._issended
    
    @sended.setter
    def sended (self, value: bool) -> None:
        """sended attribute setter metthod (sended attribute: getter/setter)

        Args:
            value (bool): True = message was sent successfully, False = sent failed or message was not sent.
        """
        self._issended = value
        
    def __to_json(self):
        report_dict = {
            "id": self.id,
            "date": self.date_sended,
            "time": self.time_sended,
            "account": self._mailmessage._sender,
            "message": self.message,
        }
        
        success ,generatedjson = JsonWerkzeug().dict2json(report_dict)
        
        
    def __str__(self) -> str:
        return f"----\nMailMessage:\nFrom: {self.sender_name} <{self.sender_account_address}>\nSubject: {self.subject}\nMessage: {self.message}\nTime: {self.date_sended} {self.time_sended}\n----\n"
