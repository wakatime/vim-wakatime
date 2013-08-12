# -*- coding: utf-8 -*-
"""
    wakatime.log
    ~~~~~~~~~~~~

    Provides the configured logger for writing JSON to the log file.

    :copyright: (c) 2013 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

import json
import logging
import os

try:
    from collections import OrderedDict
except ImportError:
    from .packages.ordereddict import OrderedDict


class CustomEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, bytes):
            obj = bytes.decode(obj)
            return json.dumps(obj)
        return super(CustomEncoder, self).default(obj)


class JsonFormatter(logging.Formatter):

    def setup(self, timestamp, endtime, isWrite, targetFile, version, plugin):
        self.timestamp = timestamp
        self.endtime = endtime
        self.isWrite = isWrite
        self.targetFile = targetFile
        self.version = version
        self.plugin = plugin

    def format(self, record):
        data = OrderedDict([
            ('now', self.formatTime(record, self.datefmt)),
            ('version', self.version),
            ('plugin', self.plugin),
            ('time', self.timestamp),
            ('endtime', self.endtime),
            ('isWrite', self.isWrite),
            ('file', self.targetFile),
            ('level', record.levelname),
            ('message', record.msg),
        ])
        if not self.endtime:
            del data['endtime']
        if not self.plugin:
            del data['plugin']
        if not self.isWrite:
            del data['isWrite']
        return CustomEncoder().encode(data)

    def formatException(self, exc_info):
        return exec_info[2].format_exc()


def set_log_level(logger, args):
    level = logging.WARN
    if args.verbose:
        level = logging.DEBUG
    logger.setLevel(level)


def setup_logging(args, version):
    logger = logging.getLogger()
    set_log_level(logger, args)
    if len(logger.handlers) > 0:
        return logger
    logfile = args.logfile
    if not logfile:
        logfile = '~/.wakatime.log'
    handler = logging.FileHandler(os.path.expanduser(logfile))
    formatter = JsonFormatter(datefmt='%a %b %d %H:%M:%S %Z %Y')
    formatter.setup(
        timestamp=args.timestamp,
        endtime=args.endtime,
        isWrite=args.isWrite,
        targetFile=args.targetFile,
        version=version,
        plugin=args.plugin,
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
