# -*- coding: utf-8 -*-
"""
    wakatime.projects.mercurial
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Information about the mercurial project for a given file.

    :copyright: (c) 2013 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

import logging
import os

from .base import BaseProject


log = logging.getLogger(__name__)


class Mercurial(BaseProject):

    def process(self):
        return False

    def name(self):
        return None

    def branch(self):
        return None
