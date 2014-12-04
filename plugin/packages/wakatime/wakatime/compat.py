# -*- coding: utf-8 -*-
"""
    wakatime.compat
    ~~~~~~~~~~~~~~~

    For working with Python2 and Python3.

    :copyright: (c) 2014 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

import codecs
import io
import sys


is_py2 = (sys.version_info[0] == 2)
is_py3 = (sys.version_info[0] == 3)


if is_py2:

    def u(text):
        try:
            return text.decode('utf-8')
        except:
            try:
                return unicode(text)
            except:
                return text
    open = codecs.open
    basestring = basestring


elif is_py3:

    def u(text):
        if isinstance(text, bytes):
            return text.decode('utf-8')
        return str(text)
    open = open
    basestring = (str, bytes)
