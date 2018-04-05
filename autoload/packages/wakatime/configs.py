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
import traceback

from .compat import open
from .constants import CONFIG_FILE_PARSE_ERROR


try:
    import configparser
except ImportError:  # pragma: nocover
    from .packages import configparser


def getConfigFile():
    """Returns the config file location.

    If $WAKATIME_HOME env varialbe is defined, returns
    $WAKATIME_HOME/.wakatime.cfg, otherwise ~/.wakatime.cfg.
    """

    fileName = '.wakatime.cfg'

    home = os.environ.get('WAKATIME_HOME')
    if home:
        return os.path.join(os.path.expanduser(home), fileName)

    return os.path.join(os.path.expanduser('~'), fileName)


def parseConfigFile(configFile=None):
    """Returns a configparser.SafeConfigParser instance with configs
    read from the config file. Default location of the config file is
    at ~/.wakatime.cfg.
    """

    # get config file location from ENV
    if not configFile:
        configFile = getConfigFile()

    configs = configparser.ConfigParser(delimiters=('='), strict=False)
    try:
        with open(configFile, 'r', encoding='utf-8') as fh:
            try:
                configs.read_file(fh)
            except configparser.Error:
                print(traceback.format_exc())
                raise SystemExit(CONFIG_FILE_PARSE_ERROR)
    except IOError:
        pass
    return configs
