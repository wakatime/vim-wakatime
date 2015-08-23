#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
certs.py
~~~~~~~~

This module returns the preferred default CA certificate bundle.

If you are packaging Requests, e.g., for a Linux distribution or a managed
environment, you can change the definition of where() to return a separately
packaged CA bundle.
"""
import sys
import os.path

try:
    from certifi import where
except ImportError:
    def where():
        """Return the preferred certificate bundle."""
        # vendored bundle inside Requests
        is_py3 = (sys.version_info[0] == 3)
        certdir = os.path.dirname(
            __file__
            if is_py3 else
            __file__.decode(sys.getfilesystemencoding())
        )
        return os.path.join(certdir, 'cacert.pem')

if __name__ == '__main__':
    print(where())
