"""
MailMessage Class.
Class Represents a E-Mail Message to send out.
(C) 2023 Dierk-Bent Piening
E-Mail: dierk-bent.piening@mailbox.org

E-Mail can have an attachment defined.
if at instanciating attachment is not present
"""
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import asyncio
import copy
import asyncio
import random
import logging
from uuid import uuid4
from . import mail_address

# TODO: Multiple Senders


class MailMessage:
    def __init__(
        self,
        recipient_address: list[str, str],
        subject: str,
        message: str,
        sender: str,
        attachment: list[str, str] = [],
        bcc: list[str, str] = [],
        logger: logging.Logger = logging.Logger(__name__),
    ):
        self._id: uuid4 = uuid4()
        self._recipient_address = recipient_address
        self._subject: str = subject
        self._message: str = message
        self._sender: str = sender
        self._sender_address: str = ""
        self._attachment_list: list[str, str] = attachment
        self._bcc: list[str, str] = bcc
        self._logger: logging.Logger = logger
        self._random_sender_address = False
        self._use_default_sender_address = False

    @property
    def use_default_sender_address(self) -> bool:
        return self._use_default_sender_address

    @use_default_sender_address.setter
    def use_default_sender_address(self, value: bool) -> None:
        self._use_default_sender_address = value

    @property
    def random_sender_address(self) -> bool:
        return self._random_sender_address

    @random_sender_address.setter
    def random_sender_address(self, value: bool) -> None:
        self._random_sender_address = value

    async def _analyze_message(self):
        if "<!DOCTYPE html>" in self._message:
            return "HTML"
        else:
            return "PLAIN"

    async def _gen_body(self):
        return MIMEText(self._message, await self._analyze_message())

    async def _gen_bcc(self):
        return ", ".join(self._bcc)

    async def _gen_message(self, recipient_address: str):
        message = MIMEMultipart("mixed")
        message["From"] = "{sender} <{sender_address}>".format(
            sender_address=self._sender_address, sender=self._sender
        )
        message["To"] = recipient_address
        message["Subject"] = self._subject
        message["Cc"] = await self._gen_bcc()
        if len(self._attachment_list) > 0:
            for attachment_path in self._attachment_list:
                try:
                    with open(attachment_path, "rb") as attachment:
                        p = MIMEApplication(attachment.read(), _subtype="text")
                    p.add_header(
                        "Content-Disposition",
                        "attachment; filename= %s" % attachment_path.split("\\")[-1],
                    )
                    message.attach(p)
                except FileNotFoundError:
                    self._logger.Error(
                        "Attachment File defined as {attachment_path} could not be found.\nIgnored Attachment."
                    )

        message.attach(await self._gen_body())
        return message

    async def _get_cloned_message_obj(
        self, sender_address, sender_name = None
    ):
        messages_list: list[MailMessage, MailMessage] = []
        for recipient in self._recipient_address:
            mail_message_object = copy.copy(self)
            mail_message_object._recipient_address = recipient
            mail_message_object._sender_address = sender_address
            if sender_name is None:
                mail_message_object._sender = self._sender
            else:
                mail_message_object._sender = sender_name
            messages_list.append(mail_message_object)
        return messages_list

    def _get_message(self):
        return asyncio.run(self._gen_message(self._recipient_address))

    async def get_messages(
        self, random_sender_address: bool = False, random_sender_name: bool = False, sender=None
    ):
        """
        _gen_bcct_message: Function for return MIME Message / MIMEMultipart Message

        """
        messages_list: list[MailMessage, MailMessage] = []
        if (type(sender) is list):
            if (random_sender_address is True) or (self._random_sender_address is True):
                selected_sender_address = sender[
                    random.randint(1, len(sender))
                ]
                messages_list.extend(
                   await self._get_cloned_message_obj(selected_sender_address)
                )
                return messages_list
            else:
                for single_sender in sender:
                    messages_list.extend(
                        await self._get_cloned_message_obj(single_sender)
                    )
                return messages_list

        elif type(sender) is mail_address.MailAccount:
            messages_list.extend(
                 await self._get_cloned_message_obj(sender._mail_address)
            )
            return messages_list
        else:
            raise Exception



    def __str__(self):
        return f"""----\nMessage:\nTo: <{self._recipient_address}>\nSubject: '{self._subject}'\nUse Default Mail Account: {self._use_default_sender_address}\nMessage:\n{self._message}\n----\n"""

