`loops` is a Python 3 module which provides several utilities for asynchronously controlling loops.

This is `loops` version 1.0.2 ([semver](http://semver.org/)). The versioned API includes the `Loop` class, as described in its docstring.

Requirements
============

*   Python 3.2

Usage
=====

The `Loop` class is a cubclass of `threading.Thread` which allows looping over an iterable and stopping this loop externally without having to wait for the iterable to generate its next value.
