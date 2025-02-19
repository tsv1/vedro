# Vedro

[![Codecov](https://img.shields.io/codecov/c/github/vedro-universe/vedro/main.svg?style=flat-square)](https://codecov.io/gh/vedro-universe/vedro)
[![PyPI](https://img.shields.io/pypi/v/vedro.svg?style=flat-square)](https://pypi.python.org/pypi/vedro/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/vedro?style=flat-square)](https://pypi.python.org/pypi/vedro/)
[![Python Version](https://img.shields.io/pypi/pyversions/vedro.svg?style=flat-square)](https://pypi.python.org/pypi/vedro/)

## Installation

```shell
$ pip3 install vedro
```

## Usage

```python
# ./scenarios/decode_base64_encoded_string.py
import base64
import vedro

class Scenario(vedro.Scenario):
    subject = "decode base64 encoded string"

    def given(self):
        self.encoded = "YmFuYW5h"

    def when(self):
        self.decoded = base64.b64decode(self.encoded)

    def then(self):
        assert self.decoded == b"banana"
```

```shell
$ vedro run
```

## Documentation

🚀 [vedro.io](https://vedro.io/docs/quick-start)
