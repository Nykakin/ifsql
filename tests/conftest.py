#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
