# -*- coding: utf-8 -*-
"""
    wakatime.projects.wakatime_project_file
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Information from a .wakatime-project file about the project for
    a given file. First line of .wakatime-project sets the project
    name. Second line sets the current branch name.

    :copyright: (c) 2013 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

import logging
import os
import sys

from .base import BaseProject
from ..compat import u, open


log = logging.getLogger('WakaTime')


class WakaTimeProjectFile(BaseProject):

    def process(self):
        self.config = self._find_config(self.path)
        self._project_name = None
        self._project_branch = None

        if self.config:

            try:
                with open(self.config, 'r', encoding='utf-8') as fh:
                    self._project_name = u(fh.readline().strip())
                    self._project_branch = u(fh.readline().strip())
            except UnicodeDecodeError:  # pragma: nocover
                try:
                    with open(self.config, 'r', encoding=sys.getfilesystemencoding()) as fh:
                        self._project_name = u(fh.readline().strip())
                        self._project_branch = u(fh.readline().strip())
                except:
                    log.traceback('warn')
            except IOError:  # pragma: nocover
                log.traceback('warn')

            return True
        return False

    def name(self):
        return self._project_name

    def branch(self):
        return self._project_branch

    def _find_config(self, path):
        path = os.path.realpath(path)
        if os.path.isfile(path):
            path = os.path.split(path)[0]
        if os.path.isfile(os.path.join(path, '.wakatime-project')):
            return os.path.join(path, '.wakatime-project')
        split_path = os.path.split(path)
        if split_path[1] == '':
            return None
        return self._find_config(split_path[0])
