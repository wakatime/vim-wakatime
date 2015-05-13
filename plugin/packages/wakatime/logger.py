# -*- coding: utf-8 -*-
"""
    wakatime.logger
    ~~~~~~~~~~~~~~~

    Provides the configured logger for writing JSON to the log file.

    :copyright: (c) 2013 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

import logging
import os
import sys

from .packages import simplejson as json
from .compat import u
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
            obj = u(obj)
            encoded = super(CustomEncoder, self).default(obj)
        return encoded


class JsonFormatter(logging.Formatter):

    def setup(self, timestamp, isWrite, targetFile, version, plugin, verbose):
        self.timestamp = timestamp
        self.isWrite = isWrite
        self.targetFile = targetFile
        self.version = version
        self.plugin = plugin
        self.verbose = verbose

    def format(self, record):
        data = OrderedDict([
            ('now', self.formatTime(record, self.datefmt)),
        ])
        data['version'] = self.version
        data['plugin'] = self.plugin
        data['time'] = self.timestamp
        if self.verbose:
            data['caller'] = record.pathname
            data['lineno'] = record.lineno
            data['isWrite'] = self.isWrite
            data['file'] = self.targetFile
            if not self.isWrite:
                del data['isWrite']
        data['level'] = record.levelname
        data['message'] = record.msg
        if not self.plugin:
            del data['plugin']
        return CustomEncoder().encode(data)

    def formatException(self, exc_info):
        return sys.exec_info[2].format_exc()


def set_log_level(logger, args):
    level = logging.WARN
    if args.verbose:
        level = logging.DEBUG
    logger.setLevel(level)


def setup_logging(args, version):
    logging.captureWarnings(True)
    logger = logging.getLogger('WakaTime')
    set_log_level(logger, args)
    if len(logger.handlers) > 0:
        formatter = JsonFormatter(datefmt='%Y/%m/%d %H:%M:%S %z')
        formatter.setup(
            timestamp=args.timestamp,
            isWrite=args.isWrite,
            targetFile=args.targetFile,
            version=version,
            plugin=args.plugin,
            verbose=args.verbose,
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
        verbose=args.verbose,
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logging.getLogger('py.warnings').addHandler(handler)
    return logger
