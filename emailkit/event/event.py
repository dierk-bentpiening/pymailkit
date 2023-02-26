import logging
import asyncio
import threading
from emailkit.message.callbacks import DefaultMessageSentCallbacks


class Event:
    def __init__(
        self,
        eventhandlers: list[object] = None,
        logger: logging.Logger = None,
    ):
        self.returnvalue_pool: list = []
        self.default_returnvalue_pool: list = []
        if logger is None:
            self._logger: logging.Logger = logging.getLogger(__name__)
        else:
            self._logger: logging.Logger = logger

        if eventhandlers is None:
            self.eventhandlers: list[object] = []
        else:
            self.eventhandlers = eventhandlers
            
    @property
    def default_return_value_pool(self):
        """Get Method for return values.

        Returns:
            list: List of return values
        """
        return self.default_returnvalue_pool

    def clear_default_return_value_pool(self):
        self.default_returnvalue_pool = []
        return True

    @property
    def return_value_pool(self):
        """Get Method for return values of non-default return values.

        Returns:
            list: List of return values
        """
        return self.returnvalue_pool

    def clear_return_value_pool(self):
        self.returnvalue_pool = []
        return True

    def __iadd__(self, handler):
        self.eventhandlers.append(handler)
        return self

    def __isub__(self, handler):
        self.eventhandlers.remove(handler)
        return self
    
    async def __run_callback_coroutine(self, callback, isdefault, *args, **kwargs):
        self._logger.debug(f"Running defined sent callback method: '{callback}'; Default callback method: {isdefault}".format(callback.__name__, isdefault))
        return callback(*args, **kwargs)
        
    async def __callback_routine_manager(self, *args, **kwargs):
        for callback in self.eventhandlers:
            if getattr(DefaultMessageSentCallbacks, callback.__name__):
               self.default_return_value_pool.extend(await asyncio.gather(self.__run_callback_coroutine(callback, True ,*args, **kwargs)))
            else:
                self.return_value_pool.extend(await asyncio.gather(self.__run_callback_coroutine(callback, False, *args, **kwargs)))
    
    def __thread_worker(self, *args, **kwargs):
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        new_loop.run_until_complete(self.__callback_routine_manager(*args, **kwargs))
 
    
    def __call__(self, *args, **kwargs):
        callback_thread = threading.Thread(target=self.__thread_worker, args=(*args,))
        callback_thread.start()