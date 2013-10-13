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


class Git(BaseProject):

    def process(self):
        self.config = self._find_config(self.path)
        if self.config:
            return True
        return False

    def name(self):
        base = self._project_base()
        if base:
            return os.path.basename(base)
        return None

    def branch(self):
        branch = None
        base = self._project_base()
        if base:
            head = os.path.join(self._project_base(), '.git', 'HEAD')
            try:
                with open(head) as f:
                    branch = f.readline().strip().rsplit('/', 1)[-1]
            except IOError:
                pass
        return branch

    def _project_base(self):
        if self.config:
            return os.path.dirname(os.path.dirname(self.config))
        return None

    def _find_config(self, path):
        path = os.path.realpath(path)
        if os.path.isfile(path):
            path = os.path.split(path)[0]
        if os.path.isfile(os.path.join(path, '.git', 'config')):
            return os.path.join(path, '.git', 'config')
        split_path = os.path.split(path)
        if split_path[1] == '':
            return None
        return self._find_config(split_path[0])

    def _parse_config(self):
        sections = {}
        try:
            f = open(self.config, 'r')
        except IOError as e:
            log.exception("Exception:")
        else:
            with f:
                section = None
                for line in f.readlines():
                    line = line.lstrip()
                    if len(line) > 0 and line[0] == '[':
                        section = line[1:].split(']', 1)[0]
                        temp = section.split(' ', 1)
                        section = temp[0].lower()
                        if len(temp) > 1:
                            section = ' '.join([section, temp[1]])
                        sections[section] = {}
                    else:
                        try:
                            (setting, value) = line.split('=', 1)
                        except ValueError:
                            setting = line.split('#', 1)[0].split(';', 1)[0]
                            value = 'true'
                        setting = setting.strip().lower()
                        value = value.split('#', 1)[0].split(';', 1)[0].strip()
                        sections[section][setting] = value
                f.close()
        return sections
