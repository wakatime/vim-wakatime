# -*- coding: utf-8 -*-
"""
    wakatime.utils
    ~~~~~~~~~~~~~~

    Utility functions.

    :copyright: (c) 2016 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""


import platform
import logging
import os
import re
import socket
import sys

from .__about__ import __version__
from .compat import u


log = logging.getLogger('WakaTime')


BACKSLASH_REPLACE_PATTERN = re.compile(r'[\\/]+')
WINDOWS_DRIVE_PATTERN = re.compile(r'^[a-z]:/')


def should_exclude(entity, include, exclude):
    if entity is not None and entity.strip() != '':
        for pattern in include:
            try:
                compiled = re.compile(pattern, re.IGNORECASE)
                if compiled.search(entity):
                    return False
            except re.error as ex:
                log.warning(u('Regex error ({msg}) for include pattern: {pattern}').format(
                    msg=u(ex),
                    pattern=u(pattern),
                ))
        for pattern in exclude:
            try:
                compiled = re.compile(pattern, re.IGNORECASE)
                if compiled.search(entity):
                    return pattern
            except re.error as ex:
                log.warning(u('Regex error ({msg}) for exclude pattern: {pattern}').format(
                    msg=u(ex),
                    pattern=u(pattern),
                ))
    return False


def get_user_agent(plugin=None):
    ver = sys.version_info
    python_version = '%d.%d.%d.%s.%d' % (ver[0], ver[1], ver[2], ver[3], ver[4])
    user_agent = u('wakatime/{ver} ({platform}) Python{py_ver}').format(
        ver=u(__version__),
        platform=u(platform.platform()),
        py_ver=python_version,
    )
    if plugin:
        user_agent = u('{user_agent} {plugin}').format(
            user_agent=user_agent,
            plugin=u(plugin),
        )
    else:
        user_agent = u('{user_agent} Unknown/0').format(
            user_agent=user_agent,
        )
    return user_agent


def format_file_path(filepath):
    """Formats a path as absolute and with the correct platform separator."""

    try:
        filepath = os.path.realpath(os.path.abspath(filepath))
        filepath = re.sub(BACKSLASH_REPLACE_PATTERN, '/', filepath)
        if WINDOWS_DRIVE_PATTERN.match(filepath):
            filepath = filepath.capitalize()
    except:
        pass
    return filepath


def get_hostname(args):
    return args.hostname or socket.gethostname()


def find_project_file(path):
    path = os.path.realpath(path)
    if os.path.isfile(path):
        path = os.path.split(path)[0]
    if os.path.isfile(os.path.join(path, '.wakatime-project')):
        return os.path.join(path, '.wakatime-project')
    split_path = os.path.split(path)
    if split_path[1] == '':
        return None
    return find_project_file(split_path[0])
