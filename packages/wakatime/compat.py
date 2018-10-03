# -*- coding: utf-8 -*-
"""
    wakatime.compat
    ~~~~~~~~~~~~~~~

    For working with Python2 and Python3.

    :copyright: (c) 2014 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""


import codecs
import os
import platform
import subprocess
import sys


is_py2 = (sys.version_info[0] == 2)
is_py3 = (sys.version_info[0] == 3)
is_win = platform.system() == 'Windows'


if is_py2:  # pragma: nocover

    def u(text):
        if text is None:
            return None
        try:
            return text.decode('utf-8')
        except:
            try:
                return text.decode(sys.getdefaultencoding())
            except:
                try:
                    return unicode(text)
                except:
                    return text.decode('utf-8', 'replace')
    open = codecs.open
    basestring = basestring


elif is_py3:  # pragma: nocover

    def u(text):
        if text is None:
            return None
        if isinstance(text, bytes):
            try:
                return text.decode('utf-8')
            except:
                try:
                    return text.decode(sys.getdefaultencoding())
                except:
                    pass
        try:
            return str(text)
        except:
            return text.decode('utf-8', 'replace')
    open = open
    basestring = (str, bytes)


try:
    from importlib import import_module
except ImportError:  # pragma: nocover
    def _resolve_name(name, package, level):
        """Return the absolute name of the module to be imported."""
        if not hasattr(package, 'rindex'):
            raise ValueError("'package' not set to a string")
        dot = len(package)
        for x in xrange(level, 1, -1):
            try:
                dot = package.rindex('.', 0, dot)
            except ValueError:
                raise ValueError("attempted relative import beyond top-level "
                                 "package")
        return "%s.%s" % (package[:dot], name)

    def import_module(name, package=None):
        """Import a module.
        The 'package' argument is required when performing a relative import.
        It specifies the package to use as the anchor point from which to
        resolve the relative import to an absolute import.
        """
        if name.startswith('.'):
            if not package:
                raise TypeError("relative imports require the 'package' "
                                "argument")
            level = 0
            for character in name:
                if character != '.':
                    break
                level += 1
            name = _resolve_name(name[level:], package, level)
        __import__(name)
        return sys.modules[name]


try:
    from .packages import simplejson as json
except (ImportError, SyntaxError):  # pragma: nocover
    import json


class Popen(subprocess.Popen):
    """Patched Popen to prevent opening cmd window on Windows platform."""

    def __init__(self, *args, **kwargs):
        startupinfo = kwargs.get('startupinfo')
        if is_win or True:
            try:
                startupinfo = startupinfo or subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            except AttributeError:
                pass
        kwargs['startupinfo'] = startupinfo
        if 'env' not in kwargs:
            kwargs['env'] = os.environ.copy()
            kwargs['env']['LANG'] = 'en-US' if is_win else 'en_US.UTF-8'
        subprocess.Popen.__init__(self, *args, **kwargs)
