from typing import AsyncIterator

import pytest
from grpclib.testing import ChannelFor

from bananaproto.grpc.grpclib_client import MetadataLike
from tests.inputs.metadata.output_bananaproto.metadata import (
    Payload,
    TestBase,
    TestStub,
)


KEY_NAME = "value"


class MetadataService(TestBase):
    async def echo_metadata_unary_unary(
        self,
        msg: Payload,
        metadata: MetadataLike,
    ) -> Payload:
        return Payload(value=metadata[KEY_NAME])

    async def echo_metadata_unary_stream(
        self,
        msg: Payload,
        metadata: MetadataLike,
    ) -> AsyncIterator[Payload]:
        yield Payload(value=metadata[KEY_NAME])
        yield Payload(value=metadata[KEY_NAME])
        yield Payload(value=metadata[KEY_NAME])

    async def echo_metadata_stream_unary(
        self,
        msg_iter: AsyncIterator[Payload],
        metadata: MetadataLike,
    ) -> Payload:
        async for msg in msg_iter:
            return Payload(value=metadata[KEY_NAME])

    async def echo_metadata_stream_stream(
        self,
        msg_iter: AsyncIterator[Payload],
        metadata: MetadataLike,
    ) -> AsyncIterator[Payload]:
        async for msg in msg_iter:
            yield Payload(value=metadata[KEY_NAME])


@pytest.mark.asyncio
async def test_stub_metadata():
    request = Payload()
    value = "something"
    metadata = {KEY_NAME: value}

    async with ChannelFor([MetadataService()]) as channel:
        stub = TestStub(channel, metadata=metadata)

        # unary unary
        response = await stub.echo_metadata_unary_unary(request)
        assert response.value == value

        # unary stream
        async for response in stub.echo_metadata_unary_stream(request):
            assert response.value == value

        # stream unary
        async def request_iterator():
            yield request
            yield request
            yield request

        response = await stub.echo_metadata_stream_unary(request_iterator())
        assert response.value == value

        # stream stream
        async for response in stub.echo_metadata_stream_stream(request_iterator()):
            assert response.value == value


@pytest.mark.asyncio
async def test_method_metadata():
    request = Payload()

    async with ChannelFor([MetadataService()]) as channel:
        stub = TestStub(channel)

        # unary unary
        response = await stub.echo_metadata_unary_unary(
            request, metadata={KEY_NAME: "unary_unary"}
        )
        assert response.value == "unary_unary"

        # unary stream
        async for response in stub.echo_metadata_unary_stream(
            request, metadata={KEY_NAME: "unary_stream"}
        ):
            assert response.value == "unary_stream"

        # stream unary
        async def request_iterator():
            yield request
            yield request
            yield request

        response = await stub.echo_metadata_stream_unary(
            request_iterator(), metadata={KEY_NAME: "stream_unary"}
        )
        assert response.value == "stream_unary"

        # stream stream
        async for response in stub.echo_metadata_stream_stream(
            request_iterator(), metadata={KEY_NAME: "stream_stream"}
        ):
            assert response.value == "stream_stream"
