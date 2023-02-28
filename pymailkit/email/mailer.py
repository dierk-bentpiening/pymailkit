import sys
import logging
import asyncio
import schedule
import time
import json
from concurrent import futures
from pathlib import PurePath, Path
from threading import Thread
from pymailkit import exceptions
from pymailkit import message
from pymailkit import mailaccount
from pymailkit.message import SentMessageReport
from pymailkit.event import MessageEvent
from pymailkit.tools import Profiler

# TODO: E-Mail Templates
# TODO: Template parsing from file -> InWork
# TODO: Profiling Extension


class MailerDaemon:
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
                    sys.modules["pymailkit.mailbackend"], self.backend
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

    @_profiler.runtime_profiler
    def __schedule_worker(
        self,
        mail_message: message.MailMessage,
        schedule_every: str,
        schedule_time: str = "",
        sender=None,
    ):
        scheduler = schedule.Scheduler()
        self._scheduler_list.append(scheduler)
        match schedule_every.upper():
            case "HOUR":
                if schedule_time is not None:
                    if ":" in schedule_time:
                        raise exceptions.InvalidTimeStringException(
                            schedule_time, "hour"
                        )
                    elif schedule_time.isdigit():
                        scheduler.every(int(schedule_time)).hour.do(
                            self.imailer(mail_message, sender)
                        )
                    else:
                        self._logger.error(
                            f"Not matching scheduling timestring {schedule_time}. Terminating:"
                        )
                else:
                    scheduler.every().hour.do(self.imailer, mail_message)
            case "DAY":
                if schedule_time is not None:
                    if ":" in schedule_time:
                        scheduler.every().day.at(schedule_time).do(
                            self.imailer, mail_message, sender
                        )
                    elif schedule_time.isdigit():
                        scheduler.every(int(schedule_time)).day.do(
                            self.imailer, mail_message, sender
                        )
                    else:
                        self._logger.error(
                            f"Not matching scheduling timestring {schedule_time}. Terminating:"
                        )
                else:
                    scheduler.every().day.do(self.imailer, mail_message)
            case "WEEK":
                if schedule_time is not None:
                    if (":" in schedule_time) and (";" not in schedule_time):
                        scheduler.every().week.at(schedule_time).do(
                            self.imailer, mail_message, sender
                        )
                    else:
                        if ";" in schedule_time:
                            schedule_time_pattern = schedule_time.split(";")
                            schedule_time = "12:00"
                            if schedule_time_pattern[1] is not None:
                                schedule_time = schedule_time_pattern[1]
                            match schedule_time_pattern[0].upper():
                                case "MONDAY":
                                    scheduler.every().week.monday.at(schedule_time).do(
                                        asyncio.run(
                                            self.imailer(mail_message, sender)
                                        )
                                    )
                                case "TUESDAY":
                                    scheduler.every().week.tuesday.at(schedule_time).do(
                                        asyncio.run(
                                            self.imailer(mail_message, sender)
                                        )
                                    )
                                case "WENDSDAY":
                                    scheduler.every().week.wednesday.at(
                                        schedule_time
                                    ).do(
                                        asyncio.run(
                                            self.imailer(mail_message, sender)
                                        )
                                    )
                                case "THURSDAY":
                                    scheduler.every().week.thursday.at(
                                        schedule_time
                                    ).do(
                                        asyncio.run(
                                            self.imailer(mail_message, sender)
                                        )
                                    )
                                case "FRIDAY":
                                    scheduler.every().week.friday.at(schedule_time).do(
                                        asyncio.run(
                                            self.imailer(mail_message, sender)
                                        )
                                    )
                                case "SATURDAY":
                                    scheduler.every().week.saturday.at(
                                        schedule_time
                                    ).do(
                                        asyncio.run(
                                            self.imailer(mail_message, sender)
                                        )
                                    )
                                case "SUNDAY":
                                    scheduler.every().week.sunday.at(schedule_time).do(
                                        asyncio.run(
                                            self.imailer(mail_message, sender)
                                        )
                                    )
            case "WEEKS":
                if schedule_time.isdigit():
                    scheduler.every(int(schedule_time)).weeks.do(
                        self.imailer, mail_message
                    )
                else:
                    self._logger.error(
                        f"Not matching scheduling timestring {schedule_time}. Terminating:"
                    )

            case "MONTH":
                if ":" in schedule_time:
                    scheduler.every(4).weeks.at(schedule_time).do(
                        self.imailer, mail_message
                    )
                else:
                    self._logger.error(
                        f"Not matching scheduling timestring {schedule_time}. Terminating:"
                    )

        while 1:
            scheduler.run_pending()
            time.sleep(1)

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

    def simple_mailer(
        self, mailmessage: message.MailMessage, sender=None, reporting=False
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
        elif isinstance(sender, message.MailMessage) is True:
            return asyncio.run(self.imailer(mailmessage, sender))
        else:
            raise Exception

    def scheduled_mailer(
        self,
        mailmessage: message.MailMessage,
        schedule_every: str,
        schedule_time: str = None,
        sender=None,
    ) -> bool:
        with futures.ThreadPoolExecutor(max_workers=20) as process_executer:
            if mailmessage.use_default_sender_address is True:
                success, default_mail_address, index = self.get_default_email_address()
                if success is True:
                    process_executer.submit(
                        self.__schedule_worker,
                        mailmessage,
                        schedule_every,
                        schedule_time,
                        default_mail_address,
                    )
                else:
                    raise Exception
            elif (sender is None) and (mailmessage._random_sender_address is True):
                process_executer.submit(
                    self.__schedule_worker,
                    mailmessage,
                    schedule_every,
                    schedule_time,
                    self._mail_account_pool,
                )
            elif isinstance(sender, message.MailMessage) is True:
                process_executer.submit(
                    self.__schedule_worker,
                    mailmessage,
                    schedule_every,
                    schedule_time,
                    sender,
                )
            else:
                raise Exception
