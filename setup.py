#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Setup file for ifsql.

    This file was generated with PyScaffold 2.5.8, a tool that easily
    puts up a scaffold for your new Python project. Learn more under:
    http://pyscaffold.readthedocs.org/
"""

import sys
from setuptools import setup


def setup_package():
    setup(setup_requires=['six', 'pyscaffold>=2.5a0,<2.6a0'], use_pyscaffold=True)


if __name__ == "__main__":
    setup_package()
