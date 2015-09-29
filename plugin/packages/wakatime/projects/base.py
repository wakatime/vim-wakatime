# -*- coding: utf-8 -*-
"""
    wakatime.projects.base
    ~~~~~~~~~~~~~~~~~~~~~~

    Base project for use when no other project can be found.

    :copyright: (c) 2013 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

import logging

from ..exceptions import NotYetImplemented


log = logging.getLogger('WakaTime')


class BaseProject(object):
    """ Parent project class only
    used when no valid project can
    be found for the current path.
    """

    def __init__(self, path, configs=None):
        self.path = path
        self._configs = configs

    def process(self):
        """ Processes self.path into a project and
        returns True if project is valid, otherwise
        returns False.
        """
        raise NotYetImplemented()

    def name(self):
        """ Returns the project's name.
        """
        raise NotYetImplemented()

    def branch(self):
        """ Returns the current branch.
        """
        raise NotYetImplemented()
