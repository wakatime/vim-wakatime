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
from .projects.subversion import Subversion


log = logging.getLogger(__name__)

PLUGINS = [
    Git,
    Mercurial,
    Subversion,
]


def find_project(path):
    for plugin in PLUGINS:
        project = plugin(path)
        if project.process():
            return project
    return None
