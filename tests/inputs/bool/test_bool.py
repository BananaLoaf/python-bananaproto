import pytest

from tests.inputs.bool.output_bananaproto.bool import Test


def test_value():
    message = Test()
    assert not message.value, "Boolean is False by default"
