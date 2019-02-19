#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import logging

from ifsql import cmd
from ifsql import __version__

__author__ = "Nykakin"
__copyright__ = "Nykakin"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


def parse_args(args):
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(
        description="Analyzing directory structure with sql calls"
    )
    parser.add_argument(
        "directory", nargs="?", default=os.getcwd(), help="directory to analyse"
    )
    parser.add_argument(
        "--version", action="version", version="ifsql {ver}".format(ver=__version__)
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def run():
    """
    Entry point for console_scripts
    """
    args = parse_args(sys.argv[1:])
    setup_logging(args.loglevel)
    if not os.path.isdir(args.directory):
        print("Not a directory")
        sys.exit(1)
    c = cmd.Cmd(args.directory)
    c.run()
