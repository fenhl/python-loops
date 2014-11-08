`loops` is a Python 3 module which provides several utilities for asynchronously controlling loops.

This is `loops` version 1.0.2 ([semver](http://semver.org/)). The versioned API includes the functions `timeout_single` and `timeout_total` and the `Loop` class, as described in their docstrings.

Requirements
============

*   Python 3.2

Usage
=====

*   The `Loop` class is a cubclass of `threading.Thread` which allows looping over an iterable and stopping this loop externally without having to wait for the iterable to generate its next value.
*   The `timeout_total` function is a wrapper around an iterable which stops the iteration early if it takes longer than a given timeout.
*   Similarly, the `timeout_single` function is a wrapper around an iterable which stops the iteration early if any single value takes longer than a given timeout.
