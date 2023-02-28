import time
import asyncio
import schedule
from pymailkit.mailaccount import MailAccount
from pymailkit.message import MailMessage, SentMessageReport
from pymailkit.tools import JsonWerkzeug
from pymailkit.tools import Profiler
from .daemon import MailerDaemon


class QueuedMailer(MailerDaemon):
    """QueuedMailer class implements queued mail sending emthods

    Args:
        MailerDaemon (MailerDaemon): MailerDaemon Base class, class inhertiss from QueuedMailer Class
    """

    def __init__(
        self,
        mailaccount_pool: list[MailAccount],
        blobsize: int = 1,
        scheduled_time: str = "15M",
        scheduled: bool = False,
    ):
        super().__init__(mailaccount_pool)
        self._mailpool: list[MailMessage] = []
        self._failed_messages: list[MailMessage] = []
        self._message_blobsize = blobsize
        self._scheduledtime: str = scheduled_time
        self._scheduled: bool = scheduled
        self._queuedm_event_loop = asyncio.new_event_loop()
        
    @property
    def blobsize(self) -> int:
        return self._message_blobsize

    @blobsize.setter
    def blobsize(self, value: bool) -> None:
        self._blobsize = value

    def __iadd__(self, message: MailMessage) -> None:
        self._mailpool.append(message)

    async def __mailing_worker(self) -> None:
        """_summary_

        Returns:
        """
        task_list: list[object] = []
        if len(self._mailpool) >= self._blobsize:
            for mailmessage in self._mailpool:
                if (mailmessage._sender_address is None) and (
                    mailmessage.use_default_sender_address is False
                ):
                    self._failed_messages.append(mailmessage)
                    return False
                else:
                    reciever_per_mailmessage = await mailmessage.get_messages(
                        self._eventstream
                    )
                    for single_mailmessage in reciever_per_mailmessage:
                        task_list.append(
                            (
                                single_mailmessage,
                                await asyncio.gather(
                                    self.imailer(
                                        single_mailmessage, mailmessage._sender_address
                                    )
                                ),
                            )
                        )
                        reciever_per_mailmessage.remove(mailmessage)
                    return True

    async def __run_ququed_mailer(self) -> None:
        """ Run queed mailer worker funkction
        """
        scheduler = schedule.Scheduler()
        if self._scheduled is True:
            if "M" in self._scheduledtime.upper():
                stime: int = int(self._scheduledtime.upper().replace("M", ""))
                scheduler.every(stime).minutes.do(await self.__mailing_worker())

            elif "H" in self._scheduledtime.upper():
                stime: int = int(self._scheduledtime.upper().replace("H", ""))
                scheduler.every(stime).hours.do(await self.__mailing_worker())
            elif "D" in self._scheduledtime.upper():
                stime: int = int(self._scheduledtime.upper().remove("D"))
                scheduler.every(stime).hours.do(await self.__mailing_worker())
        else:
            scheduler.every(1).minutes.do(await self.__mailing_worker())
        while 1:
            scheduler.run_pending()
            time.sleep(1)
            
        
