#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tempfile

import pytest


@pytest.fixture
def database():
    import ifsql.database

    return ifsql.database.Database()


@pytest.fixture
def parser():
    import ifsql.parser

    return ifsql.parser.Parser()


@pytest.fixture
def cmd():
    import ifsql.cmd
    return ifsql.cmd.Cmd()


@pytest.fixture
def fs():
    return MockFilesystem()


class MockFilesystem:
    def __init__(self):
        self.root = tempfile.mkdtemp()

    def add_directory(self, path):
        full_path = os.path.join(self.root, path)
        os.makedirs(full_path)

    def add_file(self, path, size):
        full_path = os.path.join(self.root, path)
    
        with open(full_path, "wb") as f:
            f.write((0).to_bytes(size, "big"))
