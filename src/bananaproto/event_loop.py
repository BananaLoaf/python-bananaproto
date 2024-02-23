import asyncio
import threading
import time

from singleton import Singleton


class EventLoop:
    def __init__(self):
        self._loop: asyncio.AbstractEventLoop = None
        self._loop_created = threading.Event()
        threading.Thread(
            target=self._loop_starter,
            name="Singleton event loop",
            daemon=True,
        ).start()

    def _loop_starter(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop_created.set()
        self._loop.run_forever()

    def get_loop(self):
        self._loop_created.wait()

        while not self._loop.is_running():
            time.sleep(0.01)

        return self._loop


class SingletonEventLoop(EventLoop, metaclass=Singleton):
    pass
