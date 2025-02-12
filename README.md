## This is a fork of [betterproto](https://github.com/danielgtaylor/python-betterproto)

- Fixed input types imports missing
- Methods return non-string type hints
- Server methods now receive metadata
- Server-side exceptions get passed to client with original error message
- Removed Pydantic
- Support only `python3.10+`
- Seamless await for coroutines (see below)

# Seamless await for coroutines

Usually you write code like this:

```python
from package import Stub

stub = Stub(channel=channel)

await stub.cool_method()

async for res in stub.cool_stream():
    pass
```

However, due to my personal needs, I added ability to seamlessly de-async coroutines and async generators.

```python
from bananaproto.event_loop import EventLoop, SingletonEventLoop
from package import Stub

# Creates a separate thread with loop running it in
loop = EventLoop().get_loop()

# Creates a single separate thread for the whole program execution with loop running it in
loop = SingletonEventLoop().get_loop()
# Any additional SingletonEventLoop().get_loop() would just return that same event loop

stub = Stub(channel=channel, synchronization_loop=loop)

# They now act as regular methods
stub.cool_method()
for res in stub.cool_stream():
    pass
```

# BANANA Protobuf / gRPC Support for Python

[![Python Version](https://img.shields.io/pypi/pyversions/bananaproto.svg?color=yellow&style=flat-square)](https://www.python.org/downloads/)
[![GitHub Licence](https://img.shields.io/github/license/BananaLoaf/python-bananaproto.svg?color=blue&style=flat-square)](https://github.com/BananaLoaf/python-bananaproto/blob/master/LICENSE)
[![Package Version](https://img.shields.io/pypi/v/bananaproto.svg?color=green&style=flat-square)](https://pypi.org/project/bananaproto/)
[![Tests](https://github.com/BananaLoaf/python-bananaproto/actions/workflows/tests.yaml/badge.svg)](https://github.com/BananaLoaf/python-bananaproto/actions/workflows/tests.yaml)
> :octocat: If you're reading this on github, please be aware that it might mention unreleased features! See the latest released README on [pypi](https://pypi.org/project/bananaproto/).

This project aims to provide an improved experience when using Protobuf / gRPC in a modern Python environment by making use of modern language features and generating readable, understandable, idiomatic Python code. It will not support legacy features or environments (e.g. Protobuf 2). The following are supported:

- Protobuf 3 & gRPC code generation
  - Both binary & JSON serialization is built-in
- Python 3.7+ making use of:
  - Enums
  - Dataclasses
  - `async`/`await`
  - Timezone-aware `datetime` and `timedelta` objects
  - Relative imports
  - Mypy type checking

This project is heavily inspired by, and borrows functionality from:

- https://github.com/protocolbuffers/protobuf/tree/master/python
- https://github.com/eigenein/protobuf/
- https://github.com/vmagamedov/grpclib

## Motivation

This project exists because I am unhappy with the state of the official Google protoc plugin for Python.

- No `async` support (requires additional `grpclib` plugin)
- No typing support or code completion/intelligence (requires additional `mypy` plugin)
- No `__init__.py` module files get generated
- Output is not importable
  - Import paths break in Python 3 unless you mess with `sys.path`
- Bugs when names clash (e.g. `codecs` package)
- Generated code is not idiomatic
  - Completely unreadable runtime code-generation
  - Much code looks like C++ or Java ported 1:1 to Python
  - Capitalized function names like `HasField()` and `SerializeToString()`
  - Uses `SerializeToString()` rather than the built-in `__bytes__()`
  - Special wrapped types don't use Python's `None`
  - Timestamp/duration types don't use Python's built-in `datetime` module


This project is a reimplementation from the ground up focused on idiomatic modern Python to help fix some of the above. While it may not be a 1:1 drop-in replacement due to changed method names and call patterns, the wire format is identical.

## Installation

First, install the package. Note that the `[compiler]` feature flag tells it to install extra dependencies only needed by the `protoc` plugin:

```sh
# Install both the library and compiler
pip install "bananaproto[compiler]"

# Install just the library (to use the generated code output)
pip install bananaproto
```

*Bananaproto* is under active development. To install the latest beta version, use `pip install --pre bananaproto`.

## Getting Started

### Compiling proto files

Given you installed the compiler and have a proto file, e.g `example.proto`:

```protobuf
syntax = "proto3";

package hello;

// Greeting represents a message you can tell a user.
message Greeting {
  string message = 1;
}
```

You can run the following to invoke protoc directly:

```sh
mkdir lib
protoc -I . --python_bananaproto_out=lib example.proto
```

or run the following to invoke protoc via grpcio-tools:

```sh
pip install grpcio-tools
python -m grpc_tools.protoc -I . --python_bananaproto_out=lib example.proto
```

This will generate `lib/hello/__init__.py` which looks like:

```python
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: example.proto
# plugin: python-bananaproto
from dataclasses import dataclass

import bananaproto


@dataclass
class Greeting(bananaproto.Message):
  """Greeting represents a message you can tell a user."""

  message: str = bananaproto.string_field(1)
```

Now you can use it!

```python
>>> from lib.hello import Greeting
>>> test = Greeting()
>>> test
Greeting(message='')

>>> test.message = "Hey!"
>>> test
Greeting(message="Hey!")

>>> serialized = bytes(test)
>>> serialized
b'\n\x04Hey!'

>>> another = Greeting().parse(serialized)
>>> another
Greeting(message="Hey!")

>>> another.to_dict()
{"message": "Hey!"}
>>> another.to_json(indent=2)
'{\n  "message": "Hey!"\n}'
```

### Async gRPC Support

The generated Protobuf `Message` classes are compatible with [grpclib](https://github.com/vmagamedov/grpclib) so you are free to use it if you like. That said, this project also includes support for async gRPC stub generation with better static type checking and code completion support. It is enabled by default.

Given an example service definition:

```protobuf
syntax = "proto3";

package echo;

message EchoRequest {
  string value = 1;
  // Number of extra times to echo
  uint32 extra_times = 2;
}

message EchoResponse {
  repeated string values = 1;
}

message EchoStreamResponse  {
  string value = 1;
}

service Echo {
  rpc Echo(EchoRequest) returns (EchoResponse);
  rpc EchoStream(EchoRequest) returns (stream EchoStreamResponse);
}
```

Generate echo proto file:

```
python -m grpc_tools.protoc -I . --python_bananaproto_out=. echo.proto
```

A client can be implemented as follows:
```python
import asyncio
import echo

from grpclib.client import Channel


async def main():
    channel = Channel(host="127.0.0.1", port=50051)
    service = echo.EchoStub(channel)
    response = await service.echo(echo.EchoRequest(value="hello", extra_times=1))
    print(response)

    async for response in service.echo_stream(echo.EchoRequest(value="hello", extra_times=1)):
        print(response)

    # don't forget to close the channel when done!
    channel.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

```

which would output
```python
EchoResponse(values=['hello', 'hello'])
EchoStreamResponse(value='hello')
EchoStreamResponse(value='hello')
```

This project also produces server-facing stubs that can be used to implement a Python
gRPC server.
To use them, simply subclass the base class in the generated files and override the
service methods:

```python
import asyncio
from echo import EchoBase, EchoRequest, EchoResponse, EchoStreamResponse
from grpclib.server import Server
from typing import AsyncIterator


class EchoService(EchoBase):
    async def echo(self, echo_request: "EchoRequest") -> "EchoResponse":
        return EchoResponse([echo_request.value for _ in range(echo_request.extra_times)])

    async def echo_stream(self, echo_request: "EchoRequest") -> AsyncIterator["EchoStreamResponse"]:
        for _ in range(echo_request.extra_times):
            yield EchoStreamResponse(echo_request.value)


async def main():
    server = Server([EchoService()])
    await server.start("127.0.0.1", 50051)
    await server.wait_closed()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
```

### JSON

Both serializing and parsing are supported to/from JSON and Python dictionaries using the following methods:

- Dicts: `Message().to_dict()`, `Message().from_dict(...)`
- JSON: `Message().to_json()`, `Message().from_json(...)`

For compatibility the default is to convert field names to `camelCase`. You can control this behavior by passing a casing value, e.g:

```python
MyMessage().to_dict(casing=bananaproto.Casing.SNAKE)
```

### Determining if a message was sent

Sometimes it is useful to be able to determine whether a message has been sent on the wire. This is how the Google wrapper types work to let you know whether a value is unset, set as the default (zero value), or set as something else, for example.

Use `bananaproto.serialized_on_wire(message)` to determine if it was sent. This is a little bit different from the official Google generated Python code, and it lives outside the generated `Message` class to prevent name clashes. Note that it **only** supports Proto 3 and thus can **only** be used to check if `Message` fields are set. You cannot check if a scalar was sent on the wire.

```py
# Old way (official Google Protobuf package)
>>> mymessage.HasField('myfield')

# New way (this project)
>>> bananaproto.serialized_on_wire(mymessage.myfield)
```

### One-of Support

Protobuf supports grouping fields in a `oneof` clause. Only one of the fields in the group may be set at a given time. For example, given the proto:

```protobuf
syntax = "proto3";

message Test {
  oneof foo {
    bool on = 1;
    int32 count = 2;
    string name = 3;
  }
}
```

You can use `bananaproto.which_one_of(message, group_name)` to determine which of the fields was set. It returns a tuple of the field name and value, or a blank string and `None` if unset.

```py
>>> test = Test()
>>> bananaproto.which_one_of(test, "foo")
["", None]

>>> test.on = True
>>> bananaproto.which_one_of(test, "foo")
["on", True]

# Setting one member of the group resets the others.
>>> test.count = 57
>>> bananaproto.which_one_of(test, "foo")
["count", 57]
>>> test.on
False

# Default (zero) values also work.
>>> test.name = ""
>>> bananaproto.which_one_of(test, "foo")
["name", ""]
>>> test.count
0
>>> test.on
False
```

Again this is a little different than the official Google code generator:

```py
# Old way (official Google protobuf package)
>>> message.WhichOneof("group")
"foo"

# New way (this project)
>>> bananaproto.which_one_of(message, "group")
["foo", "foo's value"]
```

### Well-Known Google Types

Google provides several well-known message types like a timestamp, duration, and several wrappers used to provide optional zero value support. Each of these has a special JSON representation and is handled a little differently from normal messages. The Python mapping for these is as follows:

| Google Message              | Python Type                              | Default                |
| --------------------------- | ---------------------------------------- | ---------------------- |
| `google.protobuf.duration`  | [`datetime.timedelta`][td]               | `0`                    |
| `google.protobuf.timestamp` | Timezone-aware [`datetime.datetime`][dt] | `1970-01-01T00:00:00Z` |
| `google.protobuf.*Value`    | `Optional[...]`                          | `None`                 |
| `google.protobuf.*`         | `bananaproto.lib.google.protobuf.*`      | `None`                 |

[td]: https://docs.python.org/3/library/datetime.html#timedelta-objects
[dt]: https://docs.python.org/3/library/datetime.html#datetime.datetime

For the wrapper types, the Python type corresponds to the wrapped type, e.g. `google.protobuf.BoolValue` becomes `Optional[bool]` while `google.protobuf.Int32Value` becomes `Optional[int]`. All of the optional values default to `None`, so don't forget to check for that possible state. Given:

```protobuf
syntax = "proto3";

import "google/protobuf/duration.proto";
import "google/protobuf/timestamp.proto";
import "google/protobuf/wrappers.proto";

message Test {
  google.protobuf.BoolValue maybe = 1;
  google.protobuf.Timestamp ts = 2;
  google.protobuf.Duration duration = 3;
}
```

You can do stuff like:

```py
>>> t = Test().from_dict({"maybe": True, "ts": "2019-01-01T12:00:00Z", "duration": "1.200s"})
>>> t
Test(maybe=True, ts=datetime.datetime(2019, 1, 1, 12, 0, tzinfo=datetime.timezone.utc), duration=datetime.timedelta(seconds=1, microseconds=200000))

>>> t.ts - t.duration
datetime.datetime(2019, 1, 1, 11, 59, 58, 800000, tzinfo=datetime.timezone.utc)

>>> t.ts.isoformat()
'2019-01-01T12:00:00+00:00'

>>> t.maybe = None
>>> t.to_dict()
{'ts': '2019-01-01T12:00:00Z', 'duration': '1.200s'}
```


## Development

- _See how you can help &rarr; [Contributing](.github/CONTRIBUTING.md)_

### Requirements

- Python (3.7 or higher)

- [poetry](https://python-poetry.org/docs/#installation)
  *Needed to install dependencies in a virtual environment*

- [poethepoet](https://github.com/nat-n/poethepoet) for running development tasks as defined in pyproject.toml
  - Can be installed to your host environment via `pip install poethepoet` then executed as simple `poe`
  - or run from the poetry venv as `poetry run poe`

### Setup

```sh
# Get set up with the virtual env & dependencies
poetry install -E compiler

# Activate the poetry environment
poetry shell
```

### Code style

This project enforces [black](https://github.com/psf/black) python code formatting.

Before committing changes run:

```sh
poe format
```

To avoid merge conflicts later, non-black formatted python code will fail in CI.

### Tests

There are two types of tests:

1. Standard tests
2. Custom tests

#### Standard tests

Adding a standard test case is easy.

- Create a new directory `bananaproto/tests/inputs/<name>`
  - add `<name>.proto`  with a message called `Test`
  - add `<name>.json` with some test data (optional)

It will be picked up automatically when you run the tests.

- See also: [Standard Tests Development Guide](tests/README.md)

#### Custom tests

Custom tests are found in `tests/test_*.py` and are run with pytest.

#### Running

Here's how to run the tests.

```sh
# Generate assets from sample .proto files required by the tests
poe generate
# Run the tests
poe test
```

To run tests as they are run in CI (with tox) run:

```sh
poe full-test
```

### (Re)compiling Google Well-known Types

Bananaproto includes compiled versions for Google's well-known types at [src/bananaproto/lib/google](src/bananaproto/lib/google).
Be sure to regenerate these files when modifying the plugin output format, and validate by running the tests.

Normally, the plugin does not compile any references to `google.protobuf`, since they are pre-compiled. To force compilation of `google.protobuf`, use the option `--custom_opt=INCLUDE_GOOGLE`.

Assuming your `google.protobuf` source files (included with all releases of `protoc`) are located in `/usr/local/include`, you can regenerate them as follows:

```sh
protoc \
    --plugin=protoc-gen-custom=src/bananaproto/plugin/main.py \
    --custom_opt=INCLUDE_GOOGLE \
    --custom_out=src/bananaproto/lib \
    -I /usr/local/include/ \
    /usr/local/include/google/protobuf/*.proto
```

### TODO

- [x] Fixed length fields
  - [x] Packed fixed-length
- [x] Zig-zag signed fields (sint32, sint64)
- [x] Don't encode zero values for nested types
- [x] Enums
- [x] Repeated message fields
- [x] Maps
  - [x] Maps of message fields
- [x] Support passthrough of unknown fields
- [x] Refs to nested types
- [x] Imports in proto files
- [x] Well-known Google types
  - [ ] Support as request input
  - [ ] Support as response output
    - [ ] Automatically wrap/unwrap responses
- [x] OneOf support
  - [x] Basic support on the wire
  - [x] Check which was set from the group
  - [x] Setting one unsets the others
- [ ] JSON that isn't completely naive.
  - [x] 64-bit ints as strings
  - [x] Maps
  - [x] Lists
  - [x] Bytes as base64
  - [ ] Any support
  - [x] Enum strings
  - [x] Well known types support (timestamp, duration, wrappers)
  - [x] Support different casing (orig vs. camel vs. others?)
- [x] Async service stubs
  - [x] Unary-unary
  - [x] Server streaming response
  - [x] Client streaming request
- [x] Renaming messages and fields to conform to Python name standards
- [x] Renaming clashes with language keywords
- [x] Python package
- [x] Automate running tests
- [ ] Cleanup!

### Banana TODO

- [ ] Add *Reflections* chapter to README
- [ ] Return original folder structure
- [ ] Automatically import *_pb2 for reflections
- [ ] Fix comments in generated code
- [ ] Omit Empty argument from Stub and Service

## License

Copyright © 2019 Daniel G. Taylor

http://dgt.mit-license.org/
