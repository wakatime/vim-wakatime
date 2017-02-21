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
import sys

from .__about__ import __version__
from .compat import u


log = logging.getLogger('WakaTime')


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


def get_user_agent(plugin):
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
        filepath = re.sub(r'[/\\]', os.path.sep, filepath)
    except:  # pragma: nocover
        pass
    return filepath
