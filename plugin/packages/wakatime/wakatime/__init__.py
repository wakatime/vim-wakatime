# -*- coding: utf-8 -*-
"""
    wakatime
    ~~~~~~~~

    Action event appender for Wakati.Me, auto time tracking for text editors.

    :copyright: (c) 2013 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import print_function

__title__ = 'wakatime'
__version__ = '0.3.1'
__author__ = 'Alan Hamlett'
__license__ = 'BSD'
__copyright__ = 'Copyright 2013 Alan Hamlett'


import base64
import json
import logging
import os
import platform
import re
import sys
import time
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from .log import setup_logging
from .project import find_project
from .packages import requests
try:
    import argparse
except ImportError:
    from .packages import argparse


log = logging.getLogger(__name__)


class FileAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        values = os.path.realpath(values)
        setattr(namespace, self.dest, values)


def parseArguments(argv):
    try:
        sys.argv
    except AttributeError:
        sys.argv = argv
    parser = argparse.ArgumentParser(
            description='Wakati.Me event api appender')
    parser.add_argument('--file', dest='targetFile', metavar='file',
            action=FileAction, required=True,
            help='absolute path to file for current action')
    parser.add_argument('--time', dest='timestamp', metavar='time',
            type=float,
            help='optional floating-point unix epoch timestamp; '+
                'uses current time by default')
    parser.add_argument('--endtime', dest='endtime',
            help='optional end timestamp turning this action into '+
                'a duration; if a non-duration action occurs within a '+
                'duration, the duration is ignored')
    parser.add_argument('--write', dest='isWrite',
            action='store_true',
            help='note action was triggered from writing to a file')
    parser.add_argument('--plugin', dest='plugin',
            help='optional text editor plugin name and version '+
                'for User-Agent header')
    parser.add_argument('--key', dest='key',
            help='your wakati.me api key; uses api_key from '+
                '~/.wakatime.conf by default')
    parser.add_argument('--logfile', dest='logfile',
            help='defaults to ~/.wakatime.log')
    parser.add_argument('--config', dest='config',
            help='defaults to ~/.wakatime.conf')
    parser.add_argument('--verbose', dest='verbose', action='store_true',
            help='turns on debug messages in log file')
    parser.add_argument('--version', action='version', version=__version__)
    args = parser.parse_args(args=argv[1:])
    if not args.timestamp:
        args.timestamp = time.time()
    if not args.key:
        default_key = get_api_key(args.config)
        if default_key:
            args.key = default_key
        else:
            parser.error('Missing api key')
    return args


def get_api_key(configFile):
    if not configFile:
        configFile = os.path.join(os.path.expanduser('~'), '.wakatime.conf')
    api_key = None
    try:
        cf = open(configFile)
        for line in cf:
            line = line.split('=', 1)
            if line[0] == 'api_key':
                api_key = line[1].strip()
        cf.close()
    except IOError:
        print('Error: Could not read from config file.')
    return api_key


def get_user_agent(plugin):
    ver = sys.version_info
    python_version = '%d.%d.%d.%s.%d' % (ver[0], ver[1], ver[2], ver[3], ver[4])
    user_agent = 'wakatime/%s (%s) Python%s' % (__version__,
        platform.platform(), python_version)
    if plugin:
        user_agent = user_agent+' '+plugin
    return user_agent


def send_action(project=None, tags=None, key=None, targetFile=None,
        timestamp=None, endtime=None, isWrite=None, plugin=None, **kwargs):
    url = 'https://www.wakati.me/api/v1/actions'
    log.debug('Sending action to api at %s' % url)
    data = {
        'time': timestamp,
        'file': targetFile,
    }
    if endtime:
        data['endtime'] = endtime
    if isWrite:
        data['is_write'] = isWrite
    if project:
        data['project'] = project
    if tags:
        data['tags'] = list(set(tags))
    log.debug(data)

    # setup api request headers
    auth = 'Basic %s' % bytes.decode(base64.b64encode(str.encode(key)))
    headers = {
        'User-Agent': get_user_agent(plugin),
        'Content-Type': 'application/json',
        'Authorization': auth,
    }

    # send action to api
    try:
        response = requests.post(url, data=str.encode(json.dumps(data)), headers=headers)
    except requests.exceptions.RequestException as exc:
        exception_data = {
            sys.exc_info()[0].__name__: str(sys.exc_info()[1]),
        }
        if log.isEnabledFor(logging.DEBUG):
            exception_data['traceback'] = traceback.format_exc()
        log.error(exception_data)
    else:
        if response.status_code == requests.codes.created:
            log.debug({
                'response_code': response.status_code,
            })
            return True
        log.error({
            'response_code': response.status_code,
            'response_content': response.text,
        })
    return False


def main(argv=None):
    if not argv:
        argv = sys.argv
    args = parseArguments(argv)
    setup_logging(args, __version__)
    if os.path.isfile(args.targetFile):
        tags = []
        name = None
        project = find_project(args.targetFile)
        if project:
            tags = project.tags()
            name = project.name()
        if send_action(project=name, tags=tags, **vars(args)):
            return 0
        return 102
    else:
        log.debug('File does not exist; ignoring this action.')
    return 101

