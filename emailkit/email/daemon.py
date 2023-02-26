import sys
import logging
import asyncio
import schedule
import time
import json
from concurrent import futures
from pathlib import PurePath, Path
from threading import Thread
from emailkit import exceptions
from emailkit import message
from emailkit import mailaccount
from emailkit.message import SentMessageReport
from emailkit.event import MessageEvent
from emailkit.tools import Profiler

class MailerDaemon(object):
    _profiler = Profiler(debug=True)

    def __init__(
        self,
        mail_account_pool: list[mailaccount.MailAccount] = None,
        logger=None,
    ) -> None:
        self.host: str = ""
        self.port: int = 0
        self.username: str = ""
        self.password: str = ""
        self.backend: str = ""
        self._scheduler_list: list = []
        self._use_custom_templatedir: bool = False
        self._custom_template_dir: str = ""
        if logger is None:
            logging.basicConfig()
            self._logger = logging.getLogger(__name__)
            self._logger.setLevel(logging.DEBUG)
        else:
            self._logger = logger
        if mail_account_pool is None:
            self._mail_account_pool: list[mailaccount.MailAccount] = []
        else:
            self._mail_account_pool = mail_account_pool
        self._eventstream = MessageEvent()
        self._sent_reports: list[SentMessageReport] = []

    @property
    def custom_template_dir(self) -> str:
        """Property Function for custom_template_dir

        Returns:
            str: Path of custom template directory
        """
        return self._custom_template_dir

    @custom_template_dir.setter
    def custom_template_dir(self, custom_template_dir: str) -> None:
        self._custom_template_dir = custom_template_dir

    @property
    def schedulerlist(self) -> list:
        """Returns the list of scheduler instances

        Returns:
            list: list of scheduler instances
        """
        return self._scheduler_list

    def add_to_accountpool(self, account: mailaccount.MailAccount) -> bool:
        """Add MailAccount to account pool

        Args:
            account (mailaccount.MailAccount): mail account to be added to account pool

        Returns:
            bool: True if add to account pool was successful otherwise False
        """
        if isinstance(account, mailaccount.MailAccount) and (
            account not in self._mail_account_pool
        ):
            self._mail_account_pool.append(account)
            return True
        else:
            return False

    def remove_from_accountpool(self, account: mailaccount.MailAccount) -> bool:
        """Remove MailAccount from mailaccount_pool

        Args:
            account (mailaccount.MailAccount): mailaccount which should be removed from accountpool

        Returns:
            bool: _description_
        """
        if isinstance(account, mailaccount.MailAccount) and (
            account in self._mail_account_pool
        ):
            self._mail_account_pool.remove(account)
            return True
        else:
            return False

    def remove_from_accountpool_byid(self, id: str) -> bool:
        try:
            index = self._mail_account_pool.index(id)

        except IndexError:
            self._logger.warning(
                f"Error removing account from account pool; account with id '{id}' could not be found in pool!"
            )
            return False
        if self.remove_from_accountpool(self._mail_account_pool[index]):
            return True
        else:
            return False
        
    async def _imailer_coroutine_worker(self, message_obj):
        mail_account_index = self._mail_account_pool.index(message_obj._sender_address)
        if isinstance(mail_account_index, int):
            mail_addr = self._mail_account_pool[mail_account_index]
            self.host = mail_addr._smtp_host
            self.port = mail_addr._smtp_port
            self.backend = mail_addr._smtp_interface
            self.username = mail_addr._mail_address
            self.password = mail_addr._mail_password
            try:
                params = [self]
                mailer_backend = getattr(
                    sys.modules["emailkit.mailbackend"], self.backend
                )(*params)
            except AttributeError:
                self._logger.error(
                    f"Server Type {self.backend} is not implemented! Terminating"
                )
                sys.exit(1)
            try:
                await mailer_backend.send_mail(message_obj)
                message_obj.issent = True
            except Exception as ex:
                self._logger.error(f"Service Terminated, reason: {ex}")
                return False
        else:
            raise Exception

    async def _imailer_coroutine_manager(
        self, mail_message: message.MailMessage, sender
    ):
        if (mail_message._random_sender_address is True) and (isinstance(sender, list)):
            message_pool = await mail_message.get_messages(
                eventstream=self._eventstream, random_sender_address=True, sender=sender
            )
        else:
            message_pool = await mail_message.get_messages(
                eventstream=self._eventstream, sender=sender
            )
        for message_obj in message_pool:
            asyncio.gather(self._imailer_coroutine_worker(message_obj))
        for message in message_pool:
            del message
        return True

    def _imailer_eventloop_maanger(self, mail_message: message.MailMessage, sender):
        mail_send_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(mail_send_loop)
        mail_send_loop.run_until_complete(
            self._imailer_coroutine_manager(mail_message, sender)
        )

    @_profiler.runtime_profiler
    async def imailer(self, mail_message: message.MailMessage, sender):
        mailer_thread = Thread(
            target=self._imailer_eventloop_maanger, args=(mail_message, sender)
        )
        mailer_thread.start()

    # @_profiler.runtime_profiler
    def message_from_template(
        self, templatename: str
    ) -> tuple[bool, message.MailMessage]:
        def __load_template(self, templatename: str) -> tuple[bool, str]:
            filepath: PurePath = None
            template: str = ""
            if self._use_custom_templatedir is True:
                filepath = PurePath(self._custom_template_dir, templatename)
            else:
                filepath = PurePath(
                    Path(__file__).parent.resolve(),
                    "message_template",
                    f"{templatename}.json",
                )
            try:
                with open(filepath, "r") as template_reader:
                    template = template_reader.read()
            except FileNotFoundError:
                self._logger.error(f"Template {filepath} could not be loaded!")
                return False, template
            return True, template

        def __parse_template(self, template: str):
            generated_message: object = None
            try:
                _template = json.loads(template)
            except Exception as ex:
                return False, object
            else:
                if "subject" in _template:
                    pass
                elif "sender" in _template:
                    pass

                elif "recipient_address" in _template:
                    pass
                elif "message" in _template:
                    pass
                else:
                    return False, object
                generated_message = message.MailMessage(**_template)
                generated_message.use_default_sender_address = True

                return True, generated_message

        _template_loading_success, _template = __load_template(self, templatename)
        if _template_loading_success is True:
            _success, _generated_message = __parse_template(self, _template)
            if _success:
                return _generated_message
            else:
                raise Exception

    def get_default_email_account(
        self,
    ) -> tuple[bool, list[mailaccount.MailAccount], int]:
        default_email_account = [
            account for account in self._mail_account_pool if account._default is True
        ]
        try:
            index_default_email_count_pool = self._mail_account_pool.index(
                default_email_account.__getitem__(0)
            )
        except IndexError:
            self._logger.debug("No default account found in email account pool!")
        if len(default_email_account) == 0:
            return False, default_email_account, 0
        else:
            return True, default_email_account, index_default_email_count_pool

    # TODO: Implement Custom Excption
    def set_default_email_account(self, value: mailaccount.MailAccount) -> bool:
        success, default_mail_address, index = self.get_default_email_account()
        if success is False:
            try:
                index_selected_account = self._mail_account_pool.index(
                    [
                        account
                        for account in self._mail_account_pool
                        if account._mail_address == value._mail_address
                    ].__getitem__(0)
                )
            except IndexError:
                raise Exception
                sys.exit(0)
            self._mail_account_pool[index_selected_account].default = True
            return True
        else:
            try:
                self._mail_account_pool[index].default = True
            except IndexError:
                raise Exception
                sys.exit(1)
            return True