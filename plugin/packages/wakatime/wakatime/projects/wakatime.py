# -*- coding: utf-8 -*-
"""
    wakatime.projects.wakatime
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Information from a .wakatime-project file about the project for
    a given file. First line of .wakatime-project sets the project
    name. Second line sets the current branch name.

    :copyright: (c) 2013 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

import logging
import os

from .base import BaseProject


log = logging.getLogger(__name__)


# str is unicode in Python3
try:
    unicode
except NameError:
    unicode = str


class WakaTime(BaseProject):

    def process(self):
        self.config = self._find_config(self.path)
        self._project_name = None
        self._project_branch = None

        if self.config:

            try:
                with open(self.config) as fh:
                    self._project_name = unicode(fh.readline().strip())
                    self._project_branch = unicode(fh.readline().strip())
            except IOError as e:
                log.exception("Exception:")

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
