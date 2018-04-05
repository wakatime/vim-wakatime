# -*- coding: utf-8 -*-
"""
    wakatime.projects.projectfile
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Information from a .wakatime-project file about the project for
    a given file. First line of .wakatime-project sets the project
    name. Second line sets the current branch name.

    :copyright: (c) 2013 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

import logging
import sys

from .base import BaseProject
from ..compat import u, open
from ..utils import find_project_file


log = logging.getLogger('WakaTime')


class ProjectFile(BaseProject):

    def process(self):
        self.config = find_project_file(self.path)
        self._project_name = None
        self._project_branch = None

        if self.config:

            try:
                with open(self.config, 'r', encoding='utf-8') as fh:
                    self._project_name = u(fh.readline().strip()) or None
                    self._project_branch = u(fh.readline().strip()) or None
            except UnicodeDecodeError:  # pragma: nocover
                try:
                    with open(self.config, 'r', encoding=sys.getfilesystemencoding()) as fh:
                        self._project_name = u(fh.readline().strip()) or None
                        self._project_branch = u(fh.readline().strip()) or None
                except:
                    log.traceback(logging.WARNING)
            except IOError:  # pragma: nocover
                log.traceback(logging.WARNING)

            return True
        return False

    def name(self):
        return self._project_name

    def branch(self):
        return self._project_branch
