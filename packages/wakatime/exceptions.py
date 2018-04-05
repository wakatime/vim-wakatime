# -*- coding: utf-8 -*-
"""
    wakatime.exceptions
    ~~~~~~~~~~~~~~~~~~~

    Custom exceptions.

    :copyright: (c) 2015 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""


class NotYetImplemented(Exception):
    """This method needs to be implemented."""


class SkipHeartbeat(Exception):
    """Raised to prevent the current heartbeat from being sent."""
    pass
