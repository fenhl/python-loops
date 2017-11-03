#!/usr/bin/env python

import setuptools

setuptools.setup(
    name='loops',
    description='Convenience classes and functions for looping threads',
    author='Fenhl',
    author_email='fenhl@fenhl.net',
    packages=['loops'],
    use_scm_version={
        'write_to': 'loops/_version.py'
    },
    setup_requires=[
        'setuptools_scm'
    ]
)
