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
    _project_folder = None

    def process(self):
        return self._find_git_config_file(self.path)

    def name(self):
        return u(self._project_name) if self._project_name else None

    def branch(self):
        head = self._head_file
        if head:
            line = self._first_line_of_file(head)
            if line is not None:
                return self._get_branch_from_head_file(line)
        return u('master')

    def folder(self):
        return self._project_folder

    def _find_git_config_file(self, path):
        path = os.path.realpath(path)
        if os.path.isfile(path):
            path = os.path.split(path)[0]
        if os.path.isfile(os.path.join(path, '.git', 'config')):
            self._project_name = os.path.basename(path)
            self._head_file = os.path.join(path, '.git', 'HEAD')
            self._project_folder = path
            return True

        link_path = self._path_from_gitdir_link_file(path)
        if link_path:

            # first check if this is a worktree
            if self._is_worktree(link_path):
                self._project_name = self._project_from_worktree(link_path)
                self._head_file = os.path.join(link_path, 'HEAD')
                self._project_folder = path
                return True

            # next check if this is a submodule
            if self._submodules_supported_for_path(path):
                self._project_name = os.path.basename(path)
                self._head_file = os.path.join(link_path, 'HEAD')
                self._project_folder = path
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

        if not disabled or disabled.strip().lower() == 'false':
            return True
        if disabled.strip().lower() == 'true':
            return False

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

    def _is_worktree(self, link_path):
        return os.path.basename(os.path.dirname(link_path)) == 'worktrees'

    def _path_from_gitdir_link_file(self, path):
        link = os.path.join(path, '.git')
        if not os.path.isfile(link):
            return None

        line = self._first_line_of_file(link)
        if line is not None:
            return self._path_from_gitdir_string(path, line)

        return None

    def _path_from_gitdir_string(self, path, line):
        if line.startswith('gitdir: '):
            subpath = line[len('gitdir: '):].strip()
            if os.path.isfile(os.path.join(path, subpath, 'HEAD')):
                return os.path.realpath(os.path.join(path, subpath))

        return None

    def _project_from_worktree(self, link_path):
        commondir = os.path.join(link_path, 'commondir')
        if os.path.isfile(commondir):
            line = self._first_line_of_file(commondir)
            if line:
                gitdir = os.path.abspath(os.path.join(link_path, line))
                if os.path.basename(gitdir) == '.git':
                    return os.path.basename(os.path.dirname(gitdir))

        return None

    def _first_line_of_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as fh:
                return fh.readline().strip()
        except UnicodeDecodeError:
            pass
        except IOError:
            pass
        try:
            with open(filepath, 'r', encoding=sys.getfilesystemencoding()) as fh:
                return fh.readline().strip()
        except:
            log.traceback(logging.WARNING)

        return None
