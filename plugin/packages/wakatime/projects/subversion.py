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
from ..compat import u, open
try:
    from collections import OrderedDict
except ImportError:  # pragma: nocover
    from ..packages.ordereddict import OrderedDict  # pragma: nocover


log = logging.getLogger('WakaTime')


class Subversion(BaseProject):
    binary_location = None

    def process(self):
        return self._find_project_base(self.path)

    def name(self):
        if 'Repository Root' not in self.info:
            return None  # pragma: nocover
        return u(self.info['Repository Root'].split('/')[-1].split('\\')[-1])

    def branch(self):
        if 'URL' not in self.info:
            return None  # pragma: nocover
        return u(self.info['URL'].split('/')[-1].split('\\')[-1])

    def _find_binary(self):
        if self.binary_location:
            return self.binary_location
        locations = [
            'svn',
            '/usr/bin/svn',
            '/usr/local/bin/svn',
        ]
        for location in locations:
            try:
                with open(os.devnull, 'wb') as DEVNULL:
                    Popen([location, '--version'], stdout=DEVNULL, stderr=DEVNULL)
                    self.binary_location = location
                    return location
            except:
                pass
        self.binary_location = 'svn'
        return 'svn'

    def _get_info(self, path):
        info = OrderedDict()
        if not self._is_mac() or self._has_xcode_tools():
            stdout = None
            try:
                os.environ['LANG'] = 'en_US'
                stdout, stderr = Popen([
                    self._find_binary(), 'info', os.path.realpath(path)
                ], stdout=PIPE, stderr=PIPE).communicate()
            except OSError:
                pass
            else:
                if stdout:
                    for line in stdout.splitlines():
                        line = u(line)
                        line = line.split(': ', 1)
                        if len(line) == 2:
                            info[line[0]] = line[1]
        return info

    def _find_project_base(self, path, found=False):
        if platform.system() == 'Windows':
            return False  # pragma: nocover
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

    def _is_mac(self):
        return platform.system() == 'Darwin'

    def _has_xcode_tools(self):
        try:
            with open(os.devnull, 'wb') as DEVNULL:
                proc = Popen(['/usr/bin/xcode-select', '-p'], stdout=DEVNULL, stderr=DEVNULL)
                proc.communicate()
                retval = proc.wait()
                if retval == 0:
                    return True
        except:
            pass
        return False
