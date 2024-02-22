# Changelog

[Betterproto CHANGELOG](https://github.com/danielgtaylor/python-betterproto/blob/master/CHANGELOG.md)

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

- Versions suffixed with `b*` are in `beta` and can be installed with `pip install --pre bananaproto`.

## [1.3.0] - Feb 23, 2024

- Automatic synchronizer for stubs
- Removed timezone

## [1.2.0] - Oct 4, 2023

- Reorganized tests
- Removed Pydantic
- Pass server python exceptions to client as internal error

## [1.1.0] - Apr 19, 2023

- Service methods get metadata
- Non-string type hinting fr

## [1.0.0] - Apr 6, 2023

- Fixed imports for when non-local (google, custom) types are used only in service method inputs [#472](https://github.com/danielgtaylor/python-betterproto/issues/472) [#426](https://github.com/danielgtaylor/python-betterproto/issues/426)
- Non-string type hinting


[1.3.0]: https://github.com/BananaLoaf/python-bananaproto/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/BananaLoaf/python-bananaproto/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/BananaLoaf/python-bananaproto/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/BananaLoaf/python-bananaproto/releases/tag/v1.0.0
