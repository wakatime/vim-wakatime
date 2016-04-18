# -*- coding: utf-8 -*-
"""
    wakatime.projects.projectmap
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Use the ~/.wakatime.cfg file to set custom project names by matching files
    with regex patterns. Project maps go under the [projectmap] config section.

    For example:

        [projectmap]
        /home/user/projects/foo = new project name
        /home/user/projects/bar(\d+)/ = project{0}

    Will result in file `/home/user/projects/foo/src/main.c` to have
    project name `new project name` and file `/home/user/projects/bar42/main.c`
    to have project name `project42`.

    :copyright: (c) 2013 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

import logging
import os
import re

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

        try:
            for pattern, new_proj_name in self._configs.items():
                try:
                    compiled = re.compile(pattern, re.IGNORECASE)
                    match = compiled.search(path)
                    if match:
                        return new_proj_name.format(*match.groups())
                except re.error as ex:
                    log.warning(u('Regex error ({msg}) for projectmap pattern: {pattern}').format(
                        msg=u(ex),
                        pattern=u(pattern),
                    ))
        except TypeError:  # pragma: nocover
            pass

        return None

    def branch(self):
        return None

    def name(self):
        if self.project:
            return u(self.project)
        return None
