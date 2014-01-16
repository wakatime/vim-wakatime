# -*- coding: utf-8 -*-
"""
    wakatime.projects.git
    ~~~~~~~~~~~~~~~~~~~~~

    Information about the git project for a given file.

    :copyright: (c) 2013 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

import logging
import os

from .base import BaseProject
try:
    from collections import OrderedDict
except ImportError:
    from ..packages.ordereddict import OrderedDict


log = logging.getLogger(__name__)


# str is unicode in Python3
try:
    unicode
except NameError:
    unicode = str


class Git(BaseProject):

    def process(self):
        self.configFile = self._find_git_config_file(self.path)
        return self.configFile is not None

    def name(self):
        base = self._project_base()
        if base:
            return unicode(os.path.basename(base))
        return None

    def branch(self):
        base = self._project_base()
        if base:
            head = os.path.join(self._project_base(), '.git', 'HEAD')
            try:
                with open(head) as fh:
                    return unicode(fh.readline().strip().rsplit('/', 1)[-1])
            except IOError:
                pass
        return None

    def _project_base(self):
        if self.configFile:
            return os.path.dirname(os.path.dirname(self.configFile))
        return None

    def _find_git_config_file(self, path):
        path = os.path.realpath(path)
        if os.path.isfile(path):
            path = os.path.split(path)[0]
        if os.path.isfile(os.path.join(path, '.git', 'config')):
            return os.path.join(path, '.git', 'config')
        split_path = os.path.split(path)
        if split_path[1] == '':
            return None
        return self._find_git_config_file(split_path[0])
