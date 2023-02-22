import sys
import logging
import asyncio
import schedule
import time
import json
from concurrent import futures
from pathlib import PurePath, Path

from . import exceptions
from . import message
from . import mail_address
from .profiler import Profiler

# TODO: E-Mail Templates
# TODO: Template parsing from file -> InWork
# TODO: Profiling Extension

class MailerDaemon:
    _profiler = Profiler(debug=True)

    def __init__(self, mail_account_pool: list[mail_address.MailAccount, mail_address.MailAccount] = None, logger=None) -> None:
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
            self._mail_account_pool: list[mail_address.MailAccount, mail_address.MailAccount] = []
        else:
            self._mail_account_pool = mail_account_pool


    @property
    def custom_template_dir(self) -> str:
        return self._custom_template_dir

    @custom_template_dir.setter
    def custom_template_dir(self, custom_template_dir: str) -> None:
        self._custom_template_dir = custom_template_dir

    @property
    def schedulerlist(self) -> list:
        return self._schedulerlist

    def add_to_accountpool(self, account: mail_address.MailAccount) -> bool:
        pass

    def remove_from_accountpool(self, account: mail_address.MailAccount) -> bool:
        pass


    @_profiler.runtime_profiler
    async def __imailer(self, mail_message: message.MailMessage, sender):
        message_pool = await mail_message.get_messages(sender=sender)
        for message_obj in message_pool:
            print(message_obj)
            #mail_addr = [mail_addr for mail_addr in self._mail_account_pool if mail_addr._mail_address == message_obj._sender_address]
            for mail_addr in self._mail_account_pool:
                if mail_addr._mail_address == message_obj._sender_address:

                    if not mail_addr:
                        raise Exception
                    else:
                        self.host = mail_addr._smtp_host
                        self.port = mail_addr._smtp_port
                        self.backend = mail_addr._smtp_interface
                        self.username = mail_addr._mail_address
                        self.password = mail_addr._mail_password
                        try:
                            params = [self]
                            mailer_backend = getattr(sys.modules['emailkit.mailbackend'], self.backend)(*params)
                        except AttributeError:
                            self._logger.error(f"Server Type {self.backend} is not implemented! Terminating")
                            sys.exit(1)
                        try:
                            mailer_backend.send_mail(message_obj)
                        except Exception as ex:
                            self._logger.error(f"Service Terminated, reason: {ex}")
                            return False
                else:
                    print("Not Matching")
        return True

    @_profiler.runtime_profiler
    def generate_from_template(self, templatename: str) -> message.MailMessage:
        def __load_template(self, templatename: str) -> bool:
            filepath: str = ""
            template: str = ""
            if self._use_custom_templatedir is True:
                filepath = PurePath(self._custom_template_dir, templatename)
            else:
                filepath = PurePath(Path(__file__).parent.resolve(),"message_template", templatename + ".msg")
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
                # TODO: Multiple Rbrew install speedtest --forceecipients
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
                return True, generated_message

        _template_loading_success, _template = __load_template(self, templatename)
        if _template_loading_success is True:
            _success, _generated_message = __parse_template(self, _template)
            if _success:
                return _generated_message
            else:
                raise Exception

    @_profiler.runtime_profiler
    def __schedule_worker(self, mail_message: message.MailMessage, schedule_every: str, schedule_time: str = "", sender=None):
        scheduler = schedule.Scheduler()
        self._scheduler_list.append(scheduler)
        match schedule_every.upper():
            case "HOUR":
                if (schedule_time is not None):
                    if(":" in schedule_time):
                        raise exceptions.InvalidTimeStringException(schedule_time, "hour")
                    elif schedule_time.isdigit():
                        scheduler.every(int(schedule_time)).hour.do(self.__imailer(mail_message, sender))
                    else:
                        self._logger.error(f"Not matching scheduling timestring {schedule_time}. Terminating:")
                else:
                    scheduler.every().hour.do(self.__imailer, mail_message)
            case "DAY":
                if (schedule_time is not None):
                    if (":" in schedule_time):
                        scheduler.every().day.at(schedule_time).do(self.__imailer, mail_message, sender)
                    elif schedule_time.isdigit():
                        scheduler.every(int(schedule_time)).day.do(self.__imailer, mail_message, sender)
                    else:
                        self._logger.error(f"Not matching scheduling timestring {schedule_time}. Terminating:")
                else:
                    scheduler.every().day.do(self.__imailer, mail_message)
            case "WEEK":
                if (schedule_time is not None):
                    if (":" in schedule_time) and (";" not in schedule_time):
                        scheduler.every().week.at(schedule_time).do(self.__imailer, mail_message, sender)
                    else:
                        if ";" in schedule_time:
                            schedule_time_pattern = schedule_time.split(";")
                            schedule_time = "12:00"
                            if schedule_time_pattern[1] is not None:
                                schedule_time = schedule_time_pattern[1]
                            match schedule_time_pattern[0].upper():
                                case "MONDAY":
                                    scheduler.every().week.monday.at(schedule_time).do(asyncio.run(self.__imailer, mail_message, sender))
                                case "TUESDAY":
                                    scheduler.every().week.tuesday.at(schedule_time).do(asyncio.run(self.__imailer, mail_message, sender))
                                case "WENDSDAY":
                                    scheduler.every().week.wendsday.at(schedule_time).do(asyncio.run(self.__imailer, mail_message, sender))
                                case "THURSDAY":
                                    scheduler.every().week.thursday.at(schedule_time).do(asyncio.run(self.__imailer, mail_message, sender))
                                case "FRIDAY":
                                    scheduler.every().week.friday.at(schedule_time).do(asyncio.run(self.__imailer, mail_message, sender))
                                case "SATURDAY":
                                    scheduler.every().week.saturday.at(schedule_time).do(asyncio.run(self.__imailer, mail_message, sender))
                                case "SUNDAY":
                                    scheduler.every().week.sunday.at(schedule_time).do(asyncio.run(self.__imailer, mail_message, sender))
            case "WEEKS":
                if schedule_time.isdigit():
                    scheduler.every(int(schedule_time)).weeks.do(self.__imailer, mail_message)
                else:
                    self._logger.error(f"Not matching scheduling timestring {schedule_time}. Terminating:")

            case "MONTH":
                if ":" in schedule_time:
                    scheduler.every(4).weeks.at(schedule_time).do(self.__imailer, mail_message)
                else:
                    self._logger.error(f"Not matching scheduling timestring {schedule_time}. Terminating:")

        while 1:
            scheduler.run_pending()
            time.sleep(1)

    def get_default_email_address(self) -> mail_address.MailAccount:
        default_mail_address = None
        i = 0
        for address in self._mail_account_pool:
            if address.default is True:
                default_mail_address = address
                break
            i += 1
        if default_mail_address is None:
            return False, default_mail_address, None
        else:
            return True, default_mail_address, i

    def set_default_email_address(self, value: mail_address.MailAccount) -> bool:
        success, default_mail_address, index = self.get_default_email_address()
        if success is False:
            if value in self._mail_account_pool:
                i = 0
                for mail_addr in self._mail_account_pool:
                    if mail_addr._mail_address == value._mail_address:
                        break
                    else:
                        i +=1
                self._mail_account_pool[i].default = True
                return True
            else:
                raise Exception
        else:
            if value in self._mail_account_pool:
                 self._mail_account_pool[index].default = False
                 i = 0
                 for mail_addr in self._mail_account_pool:
                     if mail_addr._mail_address == value._mail_address:
                         break
                     else:
                         i += 1

                 self._mail_account_pool[i].default = True
                 return True
            else:
                raise Except

    def simple_mailer(self, mail_message: message.MailMessage, sender=None):
        # send one mail, or send a bunch of emails
        if (mail_message.use_default_sender_address is True):
            success, default_mail_address, index = self.get_default_email_address()
            if success is True:
                return asyncio.run(self.__imailer(mail_message, default_mail_address))
            else:
                raise Exception
        else:
            return asyncio.run(self.__imailer(mail_message, sender))

    def scheduled_mailer(self, mail_message: message.MailMessage, schedule_every: str, schedule_time: str = None, sender = None) -> bool:
        with futures.ThreadPoolExecutor(max_workers=20) as process_executer:
            process_executer.submit(self.__schedule_worker, mail_message, schedule_every, schedule_time, sender)



