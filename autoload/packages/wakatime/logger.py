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
import traceback

from .compat import u
from .packages.requests.packages import urllib3
try:
    from collections import OrderedDict  # pragma: nocover
except ImportError:  # pragma: nocover
    from .packages.ordereddict import OrderedDict
try:
    from .packages import simplejson as json  # pragma: nocover
except (ImportError, SyntaxError):  # pragma: nocover
    import json


class JsonFormatter(logging.Formatter):

    def setup(self, timestamp, is_write, entity, version, plugin, verbose,
              warnings=False):
        self.timestamp = timestamp
        self.is_write = is_write
        self.entity = entity
        self.version = version
        self.plugin = plugin
        self.verbose = verbose
        self.warnings = warnings

    def format(self, record, *args):
        data = OrderedDict([
            ('now', self.formatTime(record, self.datefmt)),
        ])
        data['version'] = u(self.version)
        if self.plugin:
            data['plugin'] = u(self.plugin)
        data['time'] = self.timestamp
        if self.verbose:
            data['caller'] = u(record.pathname)
            data['lineno'] = record.lineno
            if self.is_write:
                data['is_write'] = self.is_write
            data['file'] = u(self.entity)
        data['level'] = record.levelname
        data['message'] = u(record.getMessage() if self.warnings else record.msg)
        return json.dumps(data)

    def traceback(self, lvl=None):
        logger = logging.getLogger('WakaTime')
        if not lvl:
            lvl = logger.getEffectiveLevel()
        logger.log(lvl, traceback.format_exc())


def set_log_level(logger, args):
    level = logging.WARN
    if args.verbose:
        level = logging.DEBUG
    logger.setLevel(level)


def setup_logging(args, version):
    urllib3.disable_warnings()
    logger = logging.getLogger('WakaTime')
    for handler in logger.handlers:
        logger.removeHandler(handler)
    set_log_level(logger, args)
    logfile = args.log_file
    if not logfile:
        logfile = '~/.wakatime.log'
    handler = logging.FileHandler(os.path.expanduser(logfile))
    formatter = JsonFormatter(datefmt='%Y/%m/%d %H:%M:%S %z')
    formatter.setup(
        timestamp=args.timestamp,
        is_write=args.is_write,
        entity=args.entity,
        version=version,
        plugin=args.plugin,
        verbose=args.verbose,
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # add custom traceback logging method
    logger.traceback = formatter.traceback

    warnings_formatter = JsonFormatter(datefmt='%Y/%m/%d %H:%M:%S %z')
    warnings_formatter.setup(
        timestamp=args.timestamp,
        is_write=args.is_write,
        entity=args.entity,
        version=version,
        plugin=args.plugin,
        verbose=args.verbose,
        warnings=True,
    )
    warnings_handler = logging.FileHandler(os.path.expanduser(logfile))
    warnings_handler.setFormatter(warnings_formatter)
    logging.getLogger('py.warnings').addHandler(warnings_handler)
    try:
        logging.captureWarnings(True)
    except AttributeError:  # pragma: nocover
        pass  # Python >= 2.7 is needed to capture warnings

    return logger
