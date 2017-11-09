# -*- coding: utf-8 -*-
"""
    wakatime.constants
    ~~~~~~~~~~~~~~~~~~

    Constant variable definitions.

    :copyright: (c) 2016 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

""" Success
Exit code used when a heartbeat was sent successfully.
"""
SUCCESS = 0

""" Api Error
Exit code used when the WakaTime API returned an error.
"""
API_ERROR = 102

""" Config File Parse Error
Exit code used when the ~/.wakatime.cfg config file could not be parsed.
"""
CONFIG_FILE_PARSE_ERROR = 103

""" Auth Error
Exit code used when our api key is invalid.
"""
AUTH_ERROR = 104

""" Unknown Error
Exit code used when there was an unhandled exception.
"""
UNKNOWN_ERROR = 105

""" Connection Error
Exit code used when there was proxy or other problem connecting to the WakaTime
API servers.
"""
CONNECTION_ERROR = 107

""" Max file size supporting line number count stats.
Files larger than this in bytes will not have a line count stat for performance.
Default is 2MB.
"""
MAX_FILE_SIZE_SUPPORTED = 2000000
