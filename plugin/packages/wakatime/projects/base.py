# -*- coding: utf-8 -*-
"""
    wakatime.projects.base
    ~~~~~~~~~~~~~~~~~~~~~~

    Base project for use when no other project can be found.

    :copyright: (c) 2013 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

import logging
import os


log = logging.getLogger(__name__)


class BaseProject():

    def __init__(self, path):
        self.path = path
        self.config = self.findConfig(path)

    def name(self):
        base = self.base()
        if base:
            return os.path.basename(base)
        return None

    def type(self):
        type = self.__class__.__name__.lower()
        if type == 'baseproject':
            type = None
        return type

    def base(self):
        if self.config:
            return os.path.dirname(self.config)
        return None

    def tags(self):
        tags = []
        return tags

    def findConfig(self, path):
        return ''
