# -*- coding: utf-8 -*-
"""
    wakatime.configs
    ~~~~~~~~~~~~~~~~

    Config file parser.

    :copyright: (c) 2016 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""


from __future__ import print_function

import os
import sys
import traceback

from .compat import u, open
from .constants import CONFIG_FILE_PARSE_ERROR


try:
    import ConfigParser as configparser
except ImportError:  # pragma: nocover
    import configparser


def parseConfigFile(configFile=None):
    """Returns a configparser.SafeConfigParser instance with configs
    read from the config file. Default location of the config file is
    at ~/.wakatime.cfg.
    """

    # get config file location from ENV
    home = os.environ.get('WAKATIME_HOME')
    if not configFile and home:
        configFile = os.path.join(os.path.expanduser(home), '.wakatime.cfg')

    # use default config file location
    if not configFile:
        configFile = os.path.join(os.path.expanduser('~'), '.wakatime.cfg')

    configs = configparser.SafeConfigParser()
    try:
        with open(configFile, 'r', encoding='utf-8') as fh:
            try:
                configs.readfp(fh)
            except configparser.Error:
                print(traceback.format_exc())
                return None
    except IOError:
        sys.stderr.write(u("Error: Could not read from config file {0}\n").format(u(configFile)))
        raise SystemExit(CONFIG_FILE_PARSE_ERROR)
    return configs
