import asyncio
import threading
import time

from singleton import Singleton


class EventLoop:
    """Класс для создания одного уникального асинк лупа."""

    def __init__(self):
        self._loop: asyncio.AbstractEventLoop = None
        self._loop_created = threading.Event()
        # Запускаем создатель лупа
        threading.Thread(
            target=self._loop_starter,
            name="Singleton event loop",
            daemon=True,
        ).start()
        self._loop_created.wait()

    def _loop_starter(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop_created.set()
        self._loop.run_forever()

    def get_loop(self):
        """Получить готовый луп."""
        self._loop_created.wait()

        while not self._loop.is_running():
            time.sleep(0.01)

        return self._loop


class SingletonEventLoop(EventLoop, metaclass=Singleton):
    pass
