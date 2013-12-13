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

    def __init__(self, path, configs=None):
        self.path = path
        self._configs = configs

    def project_type(self):
        """ Returns None if this is the base class.
        Returns the type of project if this is a
        valid project.
        """
        project_type = self.__class__.__name__.lower()
        if project_type == 'baseproject':
            project_type = None
        return project_type

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

    def branch(self):
        """ Returns the current branch.
        """
        return None
