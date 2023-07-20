#!/usr/bin/env python

import os
import sys
from pathlib import Path

from bananaproto.lib.google.protobuf.compiler import (
    CodeGeneratorRequest,
    CodeGeneratorResponse,
)
from bananaproto.plugin.models import monkey_patch_oneof_index
from bananaproto.plugin.parser import generate_code


def main() -> None:
    """The plugin's main entry point."""

    bin_file = os.getenv("BANANAPROTO_DEBUG")
    # Read request message from file
    if bin_file:
        with Path(bin_file).open("rb") as file:
            data = file.read()
    # Read request message from stdin
    else:
        data = sys.stdin.buffer.read()

    # Apply Work around for proto2/3 difference in protoc messages
    monkey_patch_oneof_index()

    # Parse request
    request = CodeGeneratorRequest()
    request.parse(data)

    dump_dir = os.getenv("BANANAPROTO_DUMP")
    if dump_dir:
        dump_request(Path(dump_dir), request)

    # Generate code
    response = generate_code(request)

    # Serialise response message
    output = response.SerializeToString()

    # Write to stdout
    sys.stdout.buffer.write(output)


def dump_request(dump_dir: Path, request: CodeGeneratorRequest) -> None:
    """
    For developers: Supports running plugin.py standalone so its possible to debug it.
    Run protoc (or generate.py) with BANANAPROTO_DUMP="yourfile.bin" to write the request to a file.
    Then run plugin.py from your IDE in debugging mode, and redirect stdin to the file.
    """
    dump_dir.mkdir(parents=True, exist_ok=True)
    dump_file = dump_dir / "-".join(request.file_to_generate)
    dump_file = dump_file.with_suffix(".bin")

    with dump_file.open("wb") as fh:
        sys.stderr.write(f"\033[31mWriting input from protoc to: {dump_file}\033[0m\n")
        fh.write(request.SerializeToString())


if __name__ == "__main__":
    main()
