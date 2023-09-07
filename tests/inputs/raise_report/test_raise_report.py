from typing import AsyncIterator

import pytest
from grpclib import (
    GRPCError,
    Status,
)
from grpclib.testing import ChannelFor

from bananaproto.grpc.grpclib_client import MetadataLike
from bananaproto.lib.google.protobuf import Empty
from tests.inputs.raise_report.output_bananaproto.raise_report import (
    TestBase,
    TestStub,
)


KEY_NAME = "value"


class MetadataService(TestBase):
    async def raise_unary_unary(
        self,
        msg: Empty,
        metadata: MetadataLike,
    ) -> Empty:
        raise AttributeError("unary_unary")

    async def raise_unary_stream(
        self,
        msg: Empty,
        metadata: MetadataLike,
    ) -> AsyncIterator[Empty]:
        raise KeyError("unary_stream")
        yield Empty()

    async def raise_stream_unary(
        self,
        msg_iter: AsyncIterator[Empty],
        metadata: MetadataLike,
    ) -> Empty:
        raise ValueError("stream_unary")

    async def raise_stream_stream(
        self,
        msg_iter: AsyncIterator[Empty],
        metadata: MetadataLike,
    ) -> AsyncIterator[Empty]:
        raise ZeroDivisionError("stream_stream")
        yield Empty()


@pytest.mark.asyncio
async def test_raise_report():
    async with ChannelFor([MetadataService()]) as channel:
        stub = TestStub(channel)

        # unary unary
        with pytest.raises(GRPCError) as e_info:
            await stub.raise_unary_unary(Empty())
        assert e_info.value.status == Status.INTERNAL
        assert e_info.value.message == "AttributeError: unary_unary"

        # unary stream
        with pytest.raises(GRPCError) as e_info:
            async for _ in stub.raise_unary_stream(Empty()):
                pass
        assert e_info.value.status == Status.INTERNAL
        assert e_info.value.message == "KeyError: unary_stream"

        # stream unary
        async def request_iterator() -> AsyncIterator[Empty]:
            rsp = Empty()
            yield rsp
            yield rsp
            yield rsp

        with pytest.raises(GRPCError) as e_info:
            await stub.raise_stream_unary(request_iterator())
        assert e_info.value.status == Status.INTERNAL
        assert e_info.value.message == "ValueError: stream_unary"

        # stream stream
        with pytest.raises(GRPCError) as e_info:
            async for _ in stub.raise_stream_stream(request_iterator()):
                pass
        assert e_info.value.status == Status.INTERNAL
        assert e_info.value.message == "ZeroDivisionError: stream_stream"
