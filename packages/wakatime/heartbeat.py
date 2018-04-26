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

from .compat import u, json
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
                if not self.entity or not os.path.isfile(self.entity):
                    self.skip = u('File does not exist; ignoring this heartbeat.')
                    return
                if self._excluded_by_missing_project_file():
                    self.skip = u('Skipping because missing .wakatime-project file in parent path.')
                    return

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
                                       language=data.get('language'))
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

        if not self.args.hide_filenames:
            return self

        if self.entity is None:
            return self

        if self.type != 'file':
            return self

        for pattern in self.args.hide_filenames:
            try:
                compiled = re.compile(pattern, re.IGNORECASE)
                if compiled.search(self.entity):

                    sanitized = {}
                    sensitive = ['dependencies', 'lines', 'lineno', 'cursorpos', 'branch']
                    for key, val in self.items():
                        if key in sensitive:
                            sanitized[key] = None
                        else:
                            sanitized[key] = val

                    extension = u(os.path.splitext(self.entity)[1])
                    sanitized['entity'] = u('HIDDEN{0}').format(extension)

                    return self.update(sanitized)

            except re.error as ex:
                log.warning(u('Regex error ({msg}) for include pattern: {pattern}').format(
                    msg=u(ex),
                    pattern=u(pattern),
                ))

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

    def _unicode(self, value):
        if value is None:
            return None
        return u(value)

    def _unicode_list(self, values):
        if values is None:
            return None
        return [self._unicode(value) for value in values]

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

    def __repr__(self):
        return self.json()

    def __bool__(self):
        return not self.skip

    def __nonzero__(self):
        return self.__bool__()

    def __getitem__(self, key):
        return self.dict()[key]
