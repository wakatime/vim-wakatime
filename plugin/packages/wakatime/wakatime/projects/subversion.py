# -*- coding: utf-8 -*-
"""
    wakatime.projects.subversion
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Information about the svn project for a given file.

    :copyright: (c) 2013 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

import logging
import os
import platform
from subprocess import Popen, PIPE

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


class Subversion(BaseProject):

    def process(self):
        return self._find_project_base(self.path)

    def name(self):
        return unicode(self.info['Repository Root'].split('/')[-1])

    def branch(self):
        if self.base:
            unicode(os.path.basename(self.base))
        return None

    def _get_info(self, path):
        info = OrderedDict()
        stdout = None
        try:
            os.environ['LANG'] = 'en_US'
            stdout, stderr = Popen([
                'svn', 'info', os.path.realpath(path)
            ], stdout=PIPE, stderr=PIPE).communicate()
        except OSError:
            pass
        else:
            if stdout:
                interesting = [
                    'Repository Root',
                    'Repository UUID',
                    'URL',
                ]
                for line in stdout.splitlines():
                    if isinstance(line, bytes):
                        line = bytes.decode(line)
                    line = line.split(': ', 1)
                    if line[0] in interesting:
                        info[line[0]] = line[1]
        return info

    def _find_project_base(self, path, found=False):
        if platform.system() == 'Windows':
            return False
        path = os.path.realpath(path)
        if os.path.isfile(path):
            path = os.path.split(path)[0]
        info = self._get_info(path)
        if len(info) > 0:
            found = True
            self.base = path
            self.info = info
        elif found:
            return True
        split_path = os.path.split(path)
        if split_path[1] == '':
            return found
        return self._find_project_base(split_path[0], found)

