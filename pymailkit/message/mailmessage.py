"""
MailMessage Class.
Class Represents a E-Mail Message to send out.
(C) 2023 Dierk-Bent Piening
E-Mail: dierk-bent.piening@mailbox.org

E-Mail can have an attachment defined.
if at instanciating attachment is not present
"""
import os
import typing
import asyncio
import copy
import asyncio
import random
import logging
import json
import time
from uuid import uuid4
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pymailkit import mailaccount
from pymailkit.tools import JsonWerkzeug


class MailMessage:
    def __init__(
        self,
        recipient_address: list[str],
        subject: str,
        message: str,
        sender: str,
        attachment: list[str] = None,
        bcc: list[str] = None,
        logger: logging.Logger = None,
    ):
        self._id: str = str(uuid4())
        self._recipient_address = recipient_address
        self._subject: str = subject
        self._message: str = message
        self._sender: str = sender
        self._sender_address: str = ""
        self._attachment_list: list[str] = attachment
        self._bcc: list[str] = bcc
        self._logger: logging.Logger = logger
        self._random_sender_address = False
        self._use_default_sender_address = False
        self._sent = False
        self._eventstream = None
        if logger is None:
            self._logger = logging.getLogger(__name__)
        else:
            self._logger = logger

    @property
    def eventstream(self):
        return self._eventstream

    @eventstream.setter
    def eventstream(self, event) -> None:
        self._eventstream = event

    @property
    def issent(self) -> bool:
        return self._sent

    @issent.setter
    def issent(self, value):
        self._sent = value

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

    def _analyze_message(self):
        if "<!DOCTYPE html>" in self._message:
            return "HTML"
        else:
            return "PLAIN"

    def _gen_body(self):
        return MIMEText(self._message, self._analyze_message())

    def _gen_bcc(self):
        try:
            return ", ".join(self._bcc)
        except TypeError:
            return ""

    def _gen_message(self, recipient_address: str):
        message = MIMEMultipart("mixed")
        message["From"] = f"{self._sender} <{self._sender_address._mail_address}>"
        message["To"] = recipient_address
        message["Subject"] = self._subject
        message["Cc"] = self._gen_bcc()
        if self._attachment_list is not None:
            if len(self._attachment_list) > 0:
                for attachment_path in self._attachment_list:
                    try:
                        with open(attachment_path, "rb") as attachment:
                            p = MIMEApplication(attachment.read(), _subtype="text")

                        if os.name == "nt":
                            filename = (attachment_path.split("\\")[-1],)
                        else:
                            filename = (attachment_path.split("/")[-1],)
                        p.add_header(
                            "Content-Disposition", "attachment; filename= %s" % filename
                        )
                        message.attach(p)
                    except FileNotFoundError:
                        self._logger.error(
                            f"Attachment File defined as {attachment_path} could not be found.\nIgnored Attachment."
                        )

        message.attach(self._gen_body())
        return message

    async def _get_cloned_message_obj(
        self, sender_address, eventstream, sender_name=None
    ):
        messages_list: list[MailMessage] = []
        for recipient in self._recipient_address:
            mail_message_object = copy.copy(self)
            mail_message_object._recipient_address = recipient
            mail_message_object._sender_address = sender_address
            mail_message_object.eventstream = eventstream
            if sender_name is None:
                mail_message_object._sender = self._sender
            else:
                mail_message_object._sender = sender_name
            messages_list.append(mail_message_object)
        return messages_list

    def _get_message(self):
        return str(self._gen_message(self._recipient_address))

    async def get_messages(
        self,
        eventstream,
        random_sender_address: bool = False,
        sender=None,
    ) -> list[object]:
        """
        _gen_bcct_message: Function for return MIME Message / MIMEMultipart Message

        """
        messages_list: list[MailMessage] = []
        if isinstance(sender, list) is True:
            if (random_sender_address is True) or (self._random_sender_address is True):
                selected_sender = sender[random.randint(0, len(sender) - 1)]
                messages_list.extend(
                    await self._get_cloned_message_obj(selected_sender, eventstream)
                )
                return messages_list
            else:
                for single_sender in sender:
                    messages_list.extend(
                        await self._get_cloned_message_obj(single_sender, eventstream)
                    )
                return messages_list

        elif isinstance(sender, mailaccount.MailAccount) is True:
            messages_list.extend(
                await self._get_cloned_message_obj(sender, eventstream)
            )
            return messages_list
        else:
            raise Exception

    def _to_json(self) -> bool | str:
        dict_document: dict = {
            "_id": str(self._id),
            "_sender": self._sender,
            "_recipient_address": self._recipient_address,
            "_bcc": self._bcc,
            "_subject": self._subject,
            "_message": self._message,
        }

        isvalid, generatedjson = JsonWerkzeug().dict2json(dict_document)
        if isvalid:
            return generatedjson
        else:
            raise Exception

    def _to_pdf(self):
        pass  # has to be implemented

    def _to_markdown(self):
        pass  # has to be implemented

    def __repr__(self):
        return "MailMessage(recipient='', subject='', message='', sender='')"

    def __str__(self):
        return f"""----\nMessage:\nFrom: <{self._sender_address}>;\nTo: <{self._recipient_address}>;\nSubject: '{self._subject}';\nUse Default Mail Account: {self._use_default_sender_address};\nMessage:\n{self._message}\n----\n"""

    def __del__(self):
        if self.issent:
            if self._eventstream is not None:
                self._eventstream.on_message_sent(self)
            else:
                raise NotImplementedError  # TODO: Implement Custom Exception
