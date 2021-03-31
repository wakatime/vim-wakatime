# -*- coding: utf-8 -*-
"""
    wakatime.heartbeat
    ~~~~~~~~~~~~~~~~~~
    :copyright: (c) 2017 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""


import os
import logging
import re
from subprocess import PIPE

from .compat import u, json, is_win, Popen
from .exceptions import SkipHeartbeat
from .project import get_project_info
from .stats import get_file_stats
from .utils import get_user_agent, should_exclude, format_file_path, find_project_file


log = logging.getLogger('WakaTime')


class Heartbeat(object):
    """Heartbeat data for sending to API or storing in offline cache."""

    skip = False
    args = None
    configs = None

    time = None
    entity = None
    type = None
    category = None
    is_write = None
    project = None
    branch = None
    language = None
    dependencies = None
    lines = None
    lineno = None
    cursorpos = None
    user_agent = None

    _sensitive_when_hiding_filename = (
        'dependencies',
        'lines',
        'lineno',
        'cursorpos',
    )
    _sensitive_when_hiding_branch = (
        'branch',
    )

    def __init__(self, data, args, configs, _clone=None):
        if not data:
            self.skip = u('Skipping because heartbeat data is missing.')
            return

        self.args = args
        self.configs = configs

        self.entity = data.get('entity')
        self.time = data.get('time', data.get('timestamp'))
        self.is_write = data.get('is_write')
        self.user_agent = data.get('user_agent') or get_user_agent(args.plugin)

        self.type = data.get('type', data.get('entity_type'))
        if self.type not in ['file', 'domain', 'app']:
            self.type = 'file'

        self.category = data.get('category')
        allowed_categories = [
            'coding',
            'building',
            'indexing',
            'debugging',
            'running tests',
            'manual testing',
            'writing tests',
            'browsing',
            'code reviewing',
            'designing',
        ]
        if self.category not in allowed_categories:
            self.category = None

        if not _clone:
            exclude = self._excluded_by_pattern()
            if exclude:
                self.skip = u('Skipping because matches exclude pattern: {pattern}').format(
                    pattern=u(exclude),
                )
                return
            if self.type == 'file':
                self.entity = format_file_path(self.entity)
                self._format_local_file()
                if not self._file_exists():
                    self.skip = u('File does not exist; ignoring this heartbeat.')
                    return
                if self._excluded_by_missing_project_file():
                    self.skip = u('Skipping because missing .wakatime-project file in parent path.')
                    return

            if args.local_file and not os.path.isfile(args.local_file):
                args.local_file = None

            project, branch = get_project_info(configs, self, data)
            self.project = project
            self.branch = branch

            if self._excluded_by_unknown_project():
                self.skip = u('Skipping because project unknown.')
                return

            try:
                stats = get_file_stats(self.entity,
                                       entity_type=self.type,
                                       lineno=data.get('lineno'),
                                       cursorpos=data.get('cursorpos'),
                                       plugin=args.plugin,
                                       language=data.get('language'),
                                       local_file=args.local_file)
            except SkipHeartbeat as ex:
                self.skip = u(ex) or 'Skipping'
                return

        else:
            self.project = data.get('project')
            self.branch = data.get('branch')
            stats = data

        for key in ['language', 'dependencies', 'lines', 'lineno', 'cursorpos']:
            if stats.get(key) is not None:
                setattr(self, key, stats[key])

    def update(self, attrs):
        """Return a copy of the current Heartbeat with updated attributes."""

        data = self.dict()
        data.update(attrs)
        heartbeat = Heartbeat(data, self.args, self.configs, _clone=True)
        return heartbeat

    def sanitize(self):
        """Removes sensitive data including file names and dependencies.

        Returns a Heartbeat.
        """

        if self.entity is None:
            return self

        if self._should_obfuscate_filename():
            self._sanitize_metadata(keys=self._sensitive_when_hiding_filename)
            if self._should_obfuscate_branch(default=True):
                self._sanitize_metadata(keys=self._sensitive_when_hiding_branch)
            extension = u(os.path.splitext(self.entity)[1])
            self.entity = u('HIDDEN{0}').format(extension)
        elif self.should_obfuscate_project():
            self._sanitize_metadata(keys=self._sensitive_when_hiding_filename)
            if self._should_obfuscate_branch(default=True):
                self._sanitize_metadata(keys=self._sensitive_when_hiding_branch)
        elif self._should_obfuscate_branch():
            self._sanitize_metadata(keys=self._sensitive_when_hiding_branch)

        return self

    def json(self):
        return json.dumps(self.dict())

    def dict(self):
        return {
            'time': self.time,
            'entity': self._unicode(self.entity),
            'type': self.type,
            'category': self.category,
            'is_write': self.is_write,
            'project': self._unicode(self.project),
            'branch': self._unicode(self.branch),
            'language': self._unicode(self.language),
            'dependencies': self._unicode_list(self.dependencies),
            'lines': self.lines,
            'lineno': self.lineno,
            'cursorpos': self.cursorpos,
            'user_agent': self._unicode(self.user_agent),
        }

    def items(self):
        return self.dict().items()

    def get_id(self):
        return u('{time}-{type}-{category}-{project}-{branch}-{entity}-{is_write}').format(
            time=self.time,
            type=self.type,
            category=self.category,
            project=self._unicode(self.project),
            branch=self._unicode(self.branch),
            entity=self._unicode(self.entity),
            is_write=self.is_write,
        )

    def should_obfuscate_project(self):
        """Returns True if hide_project_names is true or the entity file path
        matches one in the list of obfuscated project paths."""

        for pattern in self.args.hide_project_names:
            try:
                compiled = re.compile(pattern, re.IGNORECASE)
                if compiled.search(self.entity):
                    return True
            except re.error as ex:
                log.warning(u('Regex error ({msg}) for hide_project_names pattern: {pattern}').format(
                    msg=u(ex),
                    pattern=u(pattern),
                ))

        return False

    def _should_obfuscate_filename(self):
        """Returns True if hide_file_names is true or the entity file path
        matches one in the list of obfuscated file paths."""

        for pattern in self.args.hide_file_names:
            try:
                compiled = re.compile(pattern, re.IGNORECASE)
                if compiled.search(self.entity):
                    return True
            except re.error as ex:
                log.warning(u('Regex error ({msg}) for hide_file_names pattern: {pattern}').format(
                    msg=u(ex),
                    pattern=u(pattern),
                ))

        return False

    def _should_obfuscate_branch(self, default=False):
        """Returns True if hide_file_names is true or the entity file path
        matches one in the list of obfuscated file paths."""

        # when project names or file names are hidden and hide_branch_names is
        # not set, we default to hiding branch names along with file/project.
        if default and self.args.hide_branch_names is None:
            return True

        if not self.branch or not self.args.hide_branch_names:
            return False

        for pattern in self.args.hide_branch_names:
            try:
                compiled = re.compile(pattern, re.IGNORECASE)
                if compiled.search(self.entity) or compiled.search(self.branch):
                    return True
            except re.error as ex:
                log.warning(u('Regex error ({msg}) for hide_branch_names pattern: {pattern}').format(
                    msg=u(ex),
                    pattern=u(pattern),
                ))

        return False

    def _unicode(self, value):
        if value is None:
            return None
        return u(value)

    def _unicode_list(self, values):
        if values is None:
            return None
        return [self._unicode(value) for value in values]

    def _file_exists(self):
        return (self.entity and os.path.isfile(self.entity) or
            self.args.local_file and os.path.isfile(self.args.local_file))

    def _format_local_file(self):
        """When args.local_file empty on Windows, tries to map args.entity to a
        unc path.

        Updates args.local_file in-place without returning anything.
        """

        if self.type != 'file':
            return

        if not self.entity:
            return

        if not is_win:
            return

        if self._file_exists():
            return

        self.args.local_file = self._to_unc_path(self.entity)

    def _to_unc_path(self, filepath):
        drive, rest = self._splitdrive(filepath)
        if not drive:
            return filepath

        stdout = None
        try:
            stdout, stderr = Popen(['net', 'use'], stdout=PIPE, stderr=PIPE).communicate()
        except OSError:
            pass
        else:
            if stdout:
                cols = None
                for line in stdout.strip().splitlines()[1:]:
                    line = u(line)
                    if not line.strip():
                        continue
                    if not cols:
                        cols = self._unc_columns(line)
                        continue
                    start, end = cols.get('local', (0, 0))
                    if not start and not end:
                        break
                    local = line[start:end].strip().split(':')[0].upper()
                    if not local.isalpha():
                        continue
                    if local == drive:
                        start, end = cols.get('remote', (0, 0))
                        if not start and not end:
                            break
                        remote = line[start:end].strip()
                        return remote + rest

        return filepath

    def _unc_columns(self, line):
        cols = {}
        current_col = u('')
        newcol = False
        start, end = 0, 0
        for char in line:
            if char.isalpha():
                if newcol:
                    cols[current_col.strip().lower()] = (start, end)
                    current_col = u('')
                    start = end
                    newcol = False
                current_col += u(char)
            else:
                newcol = True
            end += 1
        if start != end and current_col:
            cols[current_col.strip().lower()] = (start, -1)
        return cols

    def _splitdrive(self, filepath):
        if filepath[1:2] != ':' or not filepath[0].isalpha():
            return None, filepath
        return filepath[0].upper(), filepath[2:]

    def _excluded_by_pattern(self):
        return should_exclude(self.entity, self.args.include, self.args.exclude)

    def _excluded_by_unknown_project(self):
        if self.project:
            return False
        return self.args.exclude_unknown_project

    def _excluded_by_missing_project_file(self):
        if not self.args.include_only_with_project_file:
            return False
        return find_project_file(self.entity) is None

    def _sanitize_metadata(self, keys=[]):
        for key in keys:
            setattr(self, key, None)

    def __repr__(self):
        return self.json()

    def __bool__(self):
        return not self.skip

    def __nonzero__(self):
        return self.__bool__()

    def __getitem__(self, key):
        return self.dict()[key]
