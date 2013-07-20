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


class BaseProject(object):
    """ Parent project class only
    used when no valid project can
    be found for the current path.
    """

    def __init__(self, path):
        self.path = path

    def type(self):
        """ Returns None if this is the base class.
        Returns the type of project if this is a
        valid project.
        """
        type = self.__class__.__name__.lower()
        if type == 'baseproject':
            type = None
        return type

    def process(self):
        """ Processes self.path into a project and
        returns True if project is valid, otherwise
        returns False.
        """
        return False

    def name(self):
        """ Returns the project's name.
        """
        return None

    def tags(self):
        """ Returns an array of tag strings for the
        path and/or project.
        """
        return []
