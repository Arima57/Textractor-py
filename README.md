# textractor-py

Python wrapper for TextractorCLI.

`textractor-py` provides a simple Python interface for attaching to a running Visual Novel process with TextractorCLI and receiving extracted text directly from Python.

Currently supports Windows only and no future linux build planned for now.

## Features

* Attach to a running process by PID
* Listen for text from specific hooks
* Automatic architecture detection (x86/x64)
* Bundles TextractorCLI binaries
* Simple generator-based API

## Installation

```ps
pip install textractor-py
```

## Quick Start

```python
from textractor_py import Textractor

tex = Textractor()

tex.attach(2764) #PID of a VN process

print("attached, listening...")

for line in tex.listen(
    hook="HW-4*14", #optional
    pid=2764
):
    print(line)
```

Example output:

```python
(2764, "HW-4*14", "こんにちは")
(2764, "HW-4*14", "世界")
```

## API

### Textractor()

Creates a Textractor instance.

```python
tex = Textractor()
```

### attach(pid)

Attach Textractor to a running process.

```python
tex.attach(2764)
```

### detach(pid)

Detach Textractor from a process.

```python
tex.detach(2764)
```

### listen(...)

Listen for extracted text.

Example:

```python
for line in tex.listen(
    hook="HW-4*14",
    pid=2764
):
    print(line)
```

Returns tuples of:

```python
(pid, hook, text)
```

## Requirements

* Windows
* Python 3.10+
* A running target process

## Notes

This package is a Python wrapper around TextractorCLI and is intended primarily for visual novel text extraction, translation tooling, language learning tools, and related automation.

## License

GPL-2.0 License
