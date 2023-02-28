import time
import schedule
import asyncio
from concurrent import futures
from pymailkit.mailaccount import MailAccount
from pymailkit.message import MailMessage
from pymailkit.tools import Profiler
from pymailkit import exceptions
from .daemon import MailerDaemon


class ScheduledMailer(MailerDaemon):
    _profiler = Profiler(debug=True)
    def __init__(self, mailaccount_pool):
        super().__init__(mailaccount_pool)

        
        
    @_profiler.runtime_profiler
    def __schedule_worker(
        self,
        mail_message: MailMessage,
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
        
    def scheduled_mailer(
        self,
        mailmessage: MailMessage,
        schedule_every: str,
        schedule_time: str = None,
        sender=None,
    ) -> bool:
        with futures.ThreadPoolExecutor(max_workers=20) as process_executer:
            if mailmessage.use_default_sender_address is True:
                success, default_mail_address, index = self.get_default_email_account()
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
            elif isinstance(sender, MailMessage) is True:
                process_executer.submit(
                    self.__schedule_worker,
                    mailmessage,
                    schedule_every,
                    schedule_time,
                    sender,
                )
            else:
                raise Exception