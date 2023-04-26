from datetime import (
    datetime,
    timedelta,
)

from tests.inputs.repeated_duration_timestamp.output_bananaproto.repeated_duration_timestamp import Test


def test_roundtrip():
    message = Test()
    message.times = [datetime.now(), datetime.now()]
    message.durations = [timedelta(), timedelta()]
