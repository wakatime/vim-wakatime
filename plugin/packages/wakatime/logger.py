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


class CustomEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, bytes):  # pragma: nocover
            obj = u(obj)
            return json.dumps(obj)
        try:  # pragma: nocover
            encoded = super(CustomEncoder, self).default(obj)
        except UnicodeDecodeError:  # pragma: nocover
            obj = u(obj)
            encoded = super(CustomEncoder, self).default(obj)
        return encoded


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
        data['version'] = self.version
        data['plugin'] = self.plugin
        data['time'] = self.timestamp
        if self.verbose:
            data['caller'] = record.pathname
            data['lineno'] = record.lineno
            data['is_write'] = self.is_write
            data['file'] = self.entity
            if not self.is_write:
                del data['is_write']
        data['level'] = record.levelname
        data['message'] = record.getMessage() if self.warnings else record.msg
        if not self.plugin:
            del data['plugin']
        return CustomEncoder().encode(data)


def traceback_formatter(*args, **kwargs):
    if 'level' in kwargs and (kwargs['level'].lower() == 'warn' or kwargs['level'].lower() == 'warning'):
        logging.getLogger('WakaTime').warning(traceback.format_exc())
    elif 'level' in kwargs and kwargs['level'].lower() == 'info':
        logging.getLogger('WakaTime').info(traceback.format_exc())
    elif 'level' in kwargs and kwargs['level'].lower() == 'debug':
        logging.getLogger('WakaTime').debug(traceback.format_exc())
    else:
        logging.getLogger('WakaTime').error(traceback.format_exc())


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
    logfile = args.logfile
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
    logger.traceback = traceback_formatter

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
