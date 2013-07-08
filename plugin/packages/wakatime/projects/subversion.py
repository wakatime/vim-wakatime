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

from .base import BaseProject


log = logging.getLogger(__name__)


class Subversion(BaseProject):

    def base(self):
        return super(Subversion, self).base()

    def tags(self):
        tags = []
        return tags
