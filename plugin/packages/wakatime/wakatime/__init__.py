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
__version__ = '0.4.9'
__author__ = 'Alan Hamlett'
__license__ = 'BSD'
__copyright__ = 'Copyright 2013 Alan Hamlett'


import base64
import logging
import os
import platform
import re
import sys
import time
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'packages'))
from .log import setup_logging
from .project import find_project
from .stats import get_file_stats
from .packages import argparse
from .packages import simplejson as json
from .packages import tzlocal
try:
    from urllib2 import HTTPError, Request, urlopen
except ImportError:
    from urllib.error import HTTPError
    from urllib.request import Request, urlopen


log = logging.getLogger(__name__)


class FileAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        values = os.path.realpath(values)
        setattr(namespace, self.dest, values)


def parseConfigFile(configFile):
    if not configFile:
        configFile = os.path.join(os.path.expanduser('~'), '.wakatime.conf')

    # define default config values
    configs = {
        'api_key': None,
        'ignore': [],
        'verbose': False,
    }

    try:
        with open(configFile) as fh:
            for line in fh:
                line = line.split('=', 1)
                if len(line) == 2 and line[0].strip() and line[1].strip():
                    line[0] = line[0].strip()
                    line[1] = line[1].strip()
                    if line[0] in configs:
                        if isinstance(configs[line[0]], list):
                            configs[line[0]].append(line[1])
                        elif isinstance(configs[line[0]], bool):
                            configs[line[0]] = True if line[1].lower() == 'true' else False
                        else:
                            configs[line[0]] = line[1]
                    else:
                        configs[line[0]] = line[1]
    except IOError:
        print('Error: Could not read from config file ~/.wakatime.conf')
    return configs


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
    parser.add_argument('--write', dest='isWrite',
            action='store_true',
            help='note action was triggered from writing to a file')
    parser.add_argument('--plugin', dest='plugin',
            help='optional text editor plugin name and version '+
                'for User-Agent header')
    parser.add_argument('--key', dest='key',
            help='your wakati.me api key; uses api_key from '+
                '~/.wakatime.conf by default')
    parser.add_argument('--ignore', dest='ignore', action='append',
            help='filename patterns to ignore; POSIX regex syntax; can be used more than once')
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

    # set arguments from config file
    configs = parseConfigFile(args.config)
    if not args.key:
        default_key = configs.get('api_key')
        if default_key:
            args.key = default_key
        else:
            parser.error('Missing api key')
    for pattern in configs.get('ignore', []):
        if not args.ignore:
            args.ignore = []
        args.ignore.append(pattern)
    if not args.verbose and 'verbose' in configs:
        args.verbose = configs['verbose']
    if not args.logfile and 'logfile' in configs:
        args.logfile = configs['logfile']
    return args


def should_ignore(fileName, patterns):
    try:
        for pattern in patterns:
            try:
                compiled = re.compile(pattern, re.IGNORECASE)
                if compiled.search(fileName):
                    return pattern
            except re.error as ex:
                log.warning('Regex error (%s) for ignore pattern: %s' % (str(ex), pattern))
    except TypeError:
        pass
    return False


def get_user_agent(plugin):
    ver = sys.version_info
    python_version = '%d.%d.%d.%s.%d' % (ver[0], ver[1], ver[2], ver[3], ver[4])
    user_agent = 'wakatime/%s (%s) Python%s' % (__version__,
        platform.platform(), python_version)
    if plugin:
        user_agent = user_agent+' '+plugin
    return user_agent


def send_action(project=None, branch=None, stats={}, key=None, targetFile=None,
        timestamp=None, isWrite=None, plugin=None, **kwargs):
    url = 'https://www.wakati.me/api/v1/actions'
    log.debug('Sending action to api at %s' % url)
    data = {
        'time': timestamp,
        'file': targetFile,
    }
    if stats.get('lines'):
        data['lines'] = stats['lines']
    if stats.get('language'):
        data['language'] = stats['language']
    if isWrite:
        data['is_write'] = isWrite
    if project:
        data['project'] = project
    if branch:
        data['branch'] = branch
    log.debug(data)

    # setup api request
    request = Request(url=url, data=str.encode(json.dumps(data)))
    request.add_header('User-Agent', get_user_agent(plugin))
    request.add_header('Content-Type', 'application/json')
    auth = 'Basic %s' % bytes.decode(base64.b64encode(str.encode(key)))
    request.add_header('Authorization', auth)

    # add Olson timezone to request
    tz = tzlocal.get_localzone()
    if tz:
        request.add_header('TimeZone', str(tz.zone))

    # log time to api
    response = None
    try:
        response = urlopen(request)
    except HTTPError as exc:
        exception_data = {
            'response_code': exc.getcode(),
            sys.exc_info()[0].__name__: str(sys.exc_info()[1]),
        }
        if log.isEnabledFor(logging.DEBUG):
            exception_data['traceback'] = traceback.format_exc()
        log.error(exception_data)
    except:
        exception_data = {
            sys.exc_info()[0].__name__: str(sys.exc_info()[1]),
        }
        if log.isEnabledFor(logging.DEBUG):
            exception_data['traceback'] = traceback.format_exc()
        log.error(exception_data)
    else:
        if response.getcode() == 201:
            log.debug({
                'response_code': response.getcode(),
            })
            return True
        log.error({
            'response_code': response.getcode(),
            'response_content': response.read(),
        })
    return False


def main(argv=None):
    if not argv:
        argv = sys.argv
    args = parseArguments(argv)
    setup_logging(args, __version__)
    ignore = should_ignore(args.targetFile, args.ignore)
    if ignore is not False:
        log.debug('File ignored because matches pattern: %s' % ignore)
        return 0
    if os.path.isfile(args.targetFile):
        branch = None
        name = None
        stats = get_file_stats(args.targetFile)
        project = find_project(args.targetFile)
        if project:
            branch = project.branch()
            name = project.name()
        if send_action(
                project=name,
                branch=branch,
                stats=stats,
                **vars(args)
            ):
            return 0
        return 102
    else:
        log.debug('File does not exist; ignoring this action.')
    return 101
