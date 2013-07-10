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
from subprocess import Popen, PIPE

from .base import BaseProject
from ..packages.ordereddict import OrderedDict


log = logging.getLogger(__name__)


class Subversion(BaseProject):

    def process(self):
        self.info = self._get_info()
        if 'Repository Root' in self.info:
            return True
        return False

    def name(self):
        return self.info['Repository Root'].split('/')[-1]

    def _get_info(self):
        info = OrderedDict()
        stdout = None
        try:
            stdout, stderr = Popen([
                'svn', 'info', os.path.realpath(self.path)
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
                    line = line.split(': ', 1)
                    if line[0] in interesting:
                        info[line[0]] = line[1]
        return info

    def tags(self):
        tags = []
        for key in self.info:
            if key == 'Repository UUID':
                tags.append(self.info[key])
            if key == 'URL':
                tags.append(os.path.dirname(self.info[key]))
        return tags
