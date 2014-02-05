# -*- coding: utf-8 -*-
"""
    wakatime.projects.mercurial
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Information about the mercurial project for a given file.

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


class Mercurial(BaseProject):

    def process(self):
        self.configDir = self._find_hg_config_dir(self.path)
        return self.configDir is not None

    def name(self):
        if self.configDir:
            return unicode(os.path.basename(os.path.dirname(self.configDir)))
        return None

    def branch(self):
        if self.configDir:
            branch_file = os.path.join(self.configDir, 'branch')
            try:
                with open(branch_file) as fh:
                    return unicode(fh.readline().strip().rsplit('/', 1)[-1])
            except IOError:
                pass
        return unicode('default')

    def _find_hg_config_dir(self, path):
        path = os.path.realpath(path)
        if os.path.isfile(path):
            path = os.path.split(path)[0]
        if os.path.isdir(os.path.join(path, '.hg')):
            return os.path.join(path, '.hg')
        split_path = os.path.split(path)
        if split_path[1] == '':
            return None
        return self._find_hg_config_dir(split_path[0])
