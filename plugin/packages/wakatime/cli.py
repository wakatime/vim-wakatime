# -*- coding: utf-8 -*-
"""
    wakatime.cli
    ~~~~~~~~~~~~

    Command-line entry point.

    :copyright: (c) 2013 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

import os
import sys


# get path to local wakatime package
package_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# add local wakatime package to sys.path
sys.path.insert(0, package_folder)

# import local wakatime package
try:
    import wakatime
except (TypeError, ImportError):
    # on Windows, non-ASCII characters in import path can be fixed using
    # the script path from sys.argv[0].
    # More info at https://github.com/wakatime/wakatime/issues/32
    package_folder = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
    sys.path.insert(0, package_folder)
    import wakatime


if __name__ == '__main__':
    sys.exit(wakatime.execute(sys.argv[1:]))
