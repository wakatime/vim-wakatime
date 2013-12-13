# -*- coding: utf-8 -*-
"""
    wakatime.project
    ~~~~~~~~~~~~~~~~

    Returns a project for the given file.

    :copyright: (c) 2013 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

import logging
import os

from .projects.git import Git
from .projects.mercurial import Mercurial
from .projects.projectmap import ProjectMap
from .projects.subversion import Subversion
from .projects.wakatime import WakaTime


log = logging.getLogger(__name__)


# List of plugin classes to find a project for the current file path.
# Project plugins will be processed with priority in the order below.
PLUGINS = [
    WakaTime,
    ProjectMap,
    Git,
    Mercurial,
    Subversion,
]


def find_project(path, configs=None):
    for plugin in PLUGINS:
        plugin_name = plugin.__name__.lower()
        plugin_configs = None
        if configs and configs.has_section(plugin_name):
            plugin_configs = dict(configs.items(plugin_name))
        project = plugin(path, configs=plugin_configs)
        if project.process():
            return project
    return None
