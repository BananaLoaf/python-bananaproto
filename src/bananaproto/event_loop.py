import asyncio
import inspect
import threading
import time
from typing import (
    TypeVar,
    Callable,
    Awaitable,
    AsyncIterator,
    Iterator,
)

from simple_singleton import Singleton


T = TypeVar("T")


class EventLoop:
    def __init__(self):
        self._loop: asyncio.AbstractEventLoop = None
        self._loop_created = threading.Event()
        threading.Thread(
            target=self._loop_starter,
            name="Event loop",
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

    @staticmethod
    async def _wrap_func(obj: Callable[..., T]) -> T:
        return obj()

    @staticmethod
    async def _wrap_iter(obj: Iterator[T]) -> T:
        for elem in obj:
            yield elem

    def _run_coro(self, coro: Awaitable[T]) -> T:
        return asyncio.run_coroutine_threadsafe(coro, loop=self._loop).result()

    def _run_async_iter(self, async_iter: AsyncIterator[T]) -> T:
        while True:
            future = asyncio.run_coroutine_threadsafe(
                anext(async_iter), loop=self._loop
            )
            try:
                yield future.result()
            except StopAsyncIteration:
                break

    def run_in_loop(
        self, obj: Callable[..., T] | Iterator[T] | Awaitable[T] | AsyncIterator[T]
    ) -> T | Iterator[T]:
        # Coro
        if inspect.iscoroutine(obj):
            return self._run_coro(obj)

        # Async generator
        elif inspect.isasyncgen(obj):
            return self._run_async_iter(obj)

        # Generator
        elif inspect.isgenerator(obj):
            obj = self._wrap_iter(obj)
            return self._run_async_iter(obj)

        else:
            obj = self._wrap_func(obj)
            return self._run_coro(obj)


class SingletonEventLoop(EventLoop, metaclass=Singleton):
    pass
