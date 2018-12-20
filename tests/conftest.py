#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest


@pytest.fixture
def database():
    import sqlgrep.database

    return sqlgrep.database.Database()


@pytest.fixture
def parser():
    import sqlgrep.parser

    return sqlgrep.parser.Parser()
