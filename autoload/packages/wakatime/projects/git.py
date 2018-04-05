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
import re
import sys

from .base import BaseProject
from ..compat import u, open


log = logging.getLogger('WakaTime')


class Git(BaseProject):
    _submodule = None
    _project_name = None
    _head_file = None

    def process(self):
        return self._find_git_config_file(self.path)

    def name(self):
        return u(self._project_name) if self._project_name else None

    def branch(self):
        head = self._head_file
        if head:
            try:
                with open(head, 'r', encoding='utf-8') as fh:
                    return self._get_branch_from_head_file(fh.readline())
            except UnicodeDecodeError:  # pragma: nocover
                try:
                    with open(head, 'r', encoding=sys.getfilesystemencoding()) as fh:
                        return self._get_branch_from_head_file(fh.readline())
                except:
                    log.traceback(logging.WARNING)
            except IOError:  # pragma: nocover
                log.traceback(logging.WARNING)
        return u('master')

    def _find_git_config_file(self, path):
        path = os.path.realpath(path)
        if os.path.isfile(path):
            path = os.path.split(path)[0]
        if os.path.isfile(os.path.join(path, '.git', 'config')):
            self._project_name = os.path.basename(path)
            self._head_file = os.path.join(path, '.git', 'HEAD')
            return True
        if self._submodules_supported_for_path(path):
            submodule_path = self._find_path_from_submodule(path)
            if submodule_path:
                self._project_name = os.path.basename(path)
                self._head_file = os.path.join(submodule_path, 'HEAD')
                return True
        split_path = os.path.split(path)
        if split_path[1] == '':
            return False
        return self._find_git_config_file(split_path[0])

    def _get_branch_from_head_file(self, line):
        if u(line.strip()).startswith('ref: '):
            return u(line.strip().rsplit('/', 1)[-1])
        return None

    def _submodules_supported_for_path(self, path):
        if not self._configs:
            return True

        disabled = self._configs.get('submodules_disabled')
        if not disabled:
            return True

        if disabled.strip().lower() == 'true':
            return False
        if disabled.strip().lower() == 'false':
            return True

        for pattern in disabled.split("\n"):
            if pattern.strip():
                try:
                    compiled = re.compile(pattern, re.IGNORECASE)
                    if compiled.search(path):
                        return False
                except re.error as ex:
                    log.warning(u('Regex error ({msg}) for disable git submodules pattern: {pattern}').format(
                        msg=u(ex),
                        pattern=u(pattern),
                    ))

        return True

    def _find_path_from_submodule(self, path):
        link = os.path.join(path, '.git')
        if not os.path.isfile(link):
            return None

        try:
            with open(link, 'r', encoding='utf-8') as fh:
                return self._get_path_from_submodule_link(path, fh.readline())
        except UnicodeDecodeError:
            try:
                with open(link, 'r', encoding=sys.getfilesystemencoding()) as fh:
                    return self._get_path_from_submodule_link(path, fh.readline())
            except:
                log.traceback(logging.WARNING)
        except IOError:
            log.traceback(logging.WARNING)

        return None

    def _get_path_from_submodule_link(self, path, line):
        if line.startswith('gitdir: '):
            subpath = line[len('gitdir: '):].strip()
            if os.path.isfile(os.path.join(path, subpath, 'config')) and \
                    os.path.isfile(os.path.join(path, subpath, 'HEAD')):
                return os.path.realpath(os.path.join(path, subpath))

        return None
