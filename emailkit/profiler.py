import time
import logging
import os
import json
import asyncio
from functools import wraps

class Profiler:
    def __init__(self, logger: logging.Logger = logging.Logger(__name__), debug=False):
        self._profiled_data: dict = {}
        self._logger: logging.Logger = logger
        self._debug: bool = debug
    async def __debug(self):
        print(self.__str__())

    def runtime_profiler(self, fn):
        @wraps(fn)
        def profiling_time(*args, **kwargs):
            start_time = time.time()
            ret = fn(*args, **kwargs)
            end_time = time.time()
            elapsed_time = end_time - start_time
            process_pid: int = os.getpid()
            runtime_info: dict = {fn.__name__: {"time_required": elapsed_time, "arguments": args, "time_started": start_time, "time_ended": end_time}}
            if process_pid in self._profiled_data:
                self._profiled_data[process_pid].append(runtime_info)
            else:
                self._profiled_data[process_pid] = [runtime_info]
            if self._debug:
                asyncio.run(self.__debug())
            return ret
        return profiling_time

    def __str__(self):
        return str(self._profiled_data)

    def __json__(self):
        return json.dumps(self._profiled_data)
