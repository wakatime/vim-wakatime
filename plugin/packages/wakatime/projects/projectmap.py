# -*- coding: utf-8 -*-
"""
    wakatime.projects.projectmap
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Use the ~/.wakatime.cfg file to set custom project names by
    recursively matching folder paths.
    Project maps go under the [projectmap] config section.

    For example:

        [projectmap]
        /home/user/projects/foo = new project name
        /home/user/projects/bar = project2

    Will result in file `/home/user/projects/foo/src/main.c` to have
    project name `new project name`.

    :copyright: (c) 2013 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

import logging
import os

from .base import BaseProject
from ..compat import u


log = logging.getLogger('WakaTime')


class ProjectMap(BaseProject):

    def process(self):
        if not self._configs:
            return False

        self.project = self._find_project(self.path)

        return self.project is not None

    def _find_project(self, path):
        path = os.path.realpath(path)
        if os.path.isfile(path):
            path = os.path.split(path)[0]

        if self._configs.get(path.lower()):
            return self._configs.get(path.lower())
        if self._configs.get('%s/' % path.lower()):  # pragma: nocover
            return self._configs.get('%s/' % path.lower())
        if self._configs.get('%s\\' % path.lower()):  # pragma: nocover
            return self._configs.get('%s\\' % path.lower())

        split_path = os.path.split(path)
        if split_path[1] == '':
            return None  # pragma: nocover
        return self._find_project(split_path[0])

    def branch(self):
        return None

    def name(self):
        if self.project:
            return u(self.project)
        return None  # pragma: nocover
