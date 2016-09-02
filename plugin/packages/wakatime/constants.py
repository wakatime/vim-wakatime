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

""" Malformed Heartbeat Error
Exit code used when the JSON input from `--extra-heartbeats` is malformed.
"""
MALFORMED_HEARTBEAT_ERROR = 106
