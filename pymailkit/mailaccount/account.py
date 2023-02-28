"""
MailAccount Class Represents an MailAccount
(C) 2023 Dierk-Bent Piening
E-Mail: dierk-bent.piening@mailbox.org
"""
import json
import sys
from uuid import uuid4

class MailAccount:
    def __init__(self, mail_address: str, mail_password: str, smtp_host: str, smtp_port: int, smtp_interface: str):
        self._id: str = str(uuid4())
        self._mail_address: str = mail_address
        self._mail_password: str = mail_password
        self._smtp_host: str  = smtp_host
        self._smtp_port: int  = smtp_port
        self._smtp_interface: str = smtp_interface
        self._default: bool = False
        self._imap_host: str = ""
        self._imap_port: int = 0
        self._smtp_account_hash = hash(f"[smtp_account:<{self._mail_address}>@{self._smtp_host}:{self._smtp_port}]")
        self._imap_account_hash = ""

    @property
    def default(self) -> bool:
        return self._default

    @default.setter
    def default(self, value: bool):
        self._default = value

    def __validate_smtp_connection(self):
        params = [self]
        backend_instance = getattr(
            sys.modules["pymailkit.mailbackend"], self._smtp_interface)(*params)
        backend_instance.connect()

    def __str__(self):
        return f"""[E-Mail Account: ['ID': {self._id}, 'sender_address': <{self._mail_address}> on 'server'{self._smtp_host}:{self._smtp_port}, 'isdefault': {self._default}]]"""

    def _to_json(self):
        __dict_document: dict = {"_id": str(self._id), "_mail_address": self._mail_address, "_mail_password": self._mail_password, "_smtp_host": self._smtp_host, "_smtp_port": self._smtp_port, "_smtp_interface": self._smtp_interface}
        return json.dumps(__dict_document)

