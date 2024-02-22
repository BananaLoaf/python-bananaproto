import asyncio
import threading
import time
from threading import Thread
from typing import AsyncIterator

import pytest
from grpclib.client import Channel
from grpclib.server import Server
from grpclib.testing import ChannelFor

from bananaproto.event_loop import EventLoop, SingletonEventLoop
from bananaproto.grpc.grpclib_client import MetadataLike
from tests.inputs.example_service.output_bananaproto.example_service import (
    ExampleRequest,
    ExampleResponse,
    TestBase,
    TestStub,
)


class ExampleService(TestBase):
    async def example_unary_unary(
        self,
        example_request: ExampleRequest,
        metadata: MetadataLike,
    ) -> "ExampleResponse":
        return ExampleResponse(
            example_string=example_request.example_string,
            example_integer=example_request.example_integer,
        )

    async def example_unary_stream(
        self,
        example_request: ExampleRequest,
        metadata: MetadataLike,
    ) -> AsyncIterator["ExampleResponse"]:
        response = ExampleResponse(
            example_string=example_request.example_string,
            example_integer=example_request.example_integer,
        )
        yield response
        yield response
        yield response

    async def example_stream_unary(
        self,
        example_request_iterator: AsyncIterator["ExampleRequest"],
        metadata: MetadataLike,
    ) -> "ExampleResponse":
        async for example_request in example_request_iterator:
            return ExampleResponse(
                example_string=example_request.example_string,
                example_integer=example_request.example_integer,
            )

    async def example_stream_stream(
        self,
        example_request_iterator: AsyncIterator["ExampleRequest"],
        metadata: MetadataLike,
    ) -> AsyncIterator["ExampleResponse"]:
        async for example_request in example_request_iterator:
            yield ExampleResponse(
                example_string=example_request.example_string,
                example_integer=example_request.example_integer,
            )


def start_server(host: str, port: int):
    """Start a proper server."""

    async def main():
        server = Server([ExampleService()])
        await server.start(host, port)
        await server.wait_closed()

    asyncio.run(main())


@pytest.mark.asyncio
async def test_async_calls_with_different_cardinalities():
    example_request = ExampleRequest("test string", 42)

    async with ChannelFor([ExampleService()]) as channel:
        stub = TestStub(channel)

        # unary unary
        response = await stub.example_unary_unary(example_request)
        assert response.example_string == example_request.example_string
        assert response.example_integer == example_request.example_integer

        # unary stream
        async for response in stub.example_unary_stream(example_request):
            assert response.example_string == example_request.example_string
            assert response.example_integer == example_request.example_integer

        # stream unary
        async def request_iterator():
            yield example_request
            yield example_request
            yield example_request

        response = await stub.example_stream_unary(request_iterator())
        assert response.example_string == example_request.example_string
        assert response.example_integer == example_request.example_integer

        # stream stream
        async for response in stub.example_stream_stream(request_iterator()):
            assert response.example_string == example_request.example_string
            assert response.example_integer == example_request.example_integer


@pytest.mark.asyncio
async def test_sync_calls_with_different_cardinalities():
    host = "127.0.0.1"
    port = 50051
    loop = SingletonEventLoop().get_loop()
    example_request = ExampleRequest("test string", 42)

    Thread(target=start_server, args=(host, port), daemon=True).start()

    channel = Channel(host=host, port=port)
    stub = TestStub(channel, synchronization_loop=loop)

    # unary unary
    response = stub.example_unary_unary(example_request)
    assert response.example_string == example_request.example_string
    assert response.example_integer == example_request.example_integer

    # unary stream
    for response in stub.example_unary_stream(example_request):
        assert response.example_string == example_request.example_string
        assert response.example_integer == example_request.example_integer

    # stream unary
    async def request_iterator():
        yield example_request
        yield example_request
        yield example_request

    response = stub.example_stream_unary(request_iterator())
    assert response.example_string == example_request.example_string
    assert response.example_integer == example_request.example_integer

    # stream stream
    for response in stub.example_stream_stream(request_iterator()):
        assert response.example_string == example_request.example_string
        assert response.example_integer == example_request.example_integer

    channel.close()
