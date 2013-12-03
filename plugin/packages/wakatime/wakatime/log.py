# -*- coding: utf-8 -*-
"""
    wakatime.log
    ~~~~~~~~~~~~

    Provides the configured logger for writing JSON to the log file.

    :copyright: (c) 2013 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

import logging
import os
import sys

from .packages import simplejson as json
try:
    from collections import OrderedDict
except ImportError:
    from .packages.ordereddict import OrderedDict


class CustomEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, bytes):
            obj = bytes.decode(obj)
            return json.dumps(obj)
        try:
            encoded = super(CustomEncoder, self).default(obj)
        except UnicodeDecodeError:
            encoding = sys.getfilesystemencoding()
            obj = obj.decode(encoding, 'ignore').encode('utf-8')
            encoded = super(CustomEncoder, self).default(obj)
        return encoded


class JsonFormatter(logging.Formatter):

    def setup(self, timestamp, isWrite, targetFile, version, plugin):
        self.timestamp = timestamp
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
            ('isWrite', self.isWrite),
            ('file', self.targetFile),
            ('level', record.levelname),
            ('message', record.msg),
        ])
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
        formatter = JsonFormatter(datefmt='%Y/%m/%d %H:%M:%S %z')
        formatter.setup(
            timestamp=args.timestamp,
            isWrite=args.isWrite,
            targetFile=args.targetFile,
            version=version,
            plugin=args.plugin,
        )
        logger.handlers[0].setFormatter(formatter)
        return logger
    logfile = args.logfile
    if not logfile:
        logfile = '~/.wakatime.log'
    handler = logging.FileHandler(os.path.expanduser(logfile))
    formatter = JsonFormatter(datefmt='%Y/%m/%d %H:%M:%S %z')
    formatter.setup(
        timestamp=args.timestamp,
        isWrite=args.isWrite,
        targetFile=args.targetFile,
        version=version,
        plugin=args.plugin,
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
