# -*- coding: utf-8 -*-
"""
    wakatime
    ~~~~~~~~

    Common interface to the WakaTime api.
    http://wakatime.com

    :copyright: (c) 2013 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import print_function

__title__ = 'wakatime'
__version__ = '0.5.3'
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
try:
    import ConfigParser as configparser
except ImportError:
    import configparser
try:
    from urllib2 import HTTPError, Request, urlopen
except ImportError:
    from urllib.error import HTTPError
    from urllib.request import Request, urlopen

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'packages'))
from .log import setup_logging
from .project import find_project
from .stats import get_file_stats
from .packages import argparse
from .packages import simplejson as json
from .packages import tzlocal


log = logging.getLogger(__name__)


class FileAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        values = os.path.realpath(values)
        setattr(namespace, self.dest, values)


def upgradeConfigFile(configFile):
    """For backwards-compatibility, upgrade the existing config file
    to work with configparser and rename from .wakatime.conf to .wakatime.cfg.
    """

    if os.path.isfile(configFile):
        # if upgraded cfg file already exists, don't overwrite it
        return

    oldConfig = os.path.join(os.path.expanduser('~'), '.wakatime.conf')
    try:
        configs = {
            'ignore': [],
        }

        with open(oldConfig) as fh:
            for line in fh.readlines():
                line = line.split('=', 1)
                if len(line) == 2 and line[0].strip() and line[1].strip():
                    if line[0].strip() == 'ignore':
                        configs['ignore'].append(line[1].strip())
                    else:
                        configs[line[0].strip()] = line[1].strip()

        with open(configFile, 'w') as fh:
            fh.write("[settings]\n")
            for name, value in configs.items():
                if isinstance(value, list):
                    fh.write("%s=\n" % name)
                    for item in value:
                        fh.write("    %s\n" % item)
                else:
                    fh.write("%s = %s\n" % (name, value))

        os.remove(oldConfig)
    except IOError:
        pass


def parseConfigFile(configFile):
    """Returns a configparser.SafeConfigParser instance with configs
    read from the config file. Default location of the config file is
    at ~/.wakatime.cfg.
    """

    if not configFile:
        configFile = os.path.join(os.path.expanduser('~'), '.wakatime.cfg')

    upgradeConfigFile(configFile)

    configs = configparser.SafeConfigParser()
    try:
        with open(configFile) as fh:
            try:
                configs.readfp(fh)
            except configparser.Error:
                print(traceback.format_exc())
                return None
    except IOError:
        if not os.path.isfile(configFile):
            print('Error: Could not read from config file ~/.wakatime.conf')
    return configs


def parseArguments(argv):
    """Parse command line arguments and configs from ~/.wakatime.cfg.
    Command line arguments take precedence over config file settings.
    Returns instances of ArgumentParser and SafeConfigParser.
    """

    try:
        sys.argv
    except AttributeError:
        sys.argv = argv

    # define supported command line arguments
    parser = argparse.ArgumentParser(
            description='Common interface for the WakaTime api.')
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

    # parse command line arguments
    args = parser.parse_args(args=argv[1:])

    # use current unix epoch timestamp by default
    if not args.timestamp:
        args.timestamp = time.time()

    # parse ~/.wakatime.cfg file
    configs = parseConfigFile(args.config)
    if configs is None:
        return args, configs

    # update args from configs
    if not args.key:
        default_key = None
        if configs.has_option('settings', 'api_key'):
            default_key = configs.get('settings', 'api_key')
        if default_key:
            args.key = default_key
        else:
            parser.error('Missing api key')
    if not args.ignore:
        args.ignore = []
    if configs.has_option('settings', 'ignore'):
        try:
            for pattern in configs.get('settings', 'ignore').split("\n"):
                if pattern.strip() != '':
                    args.ignore.append(pattern)
        except TypeError:
            pass
    if not args.verbose and configs.has_option('settings', 'verbose'):
        args.verbose = configs.getboolean('settings', 'verbose')
    if not args.verbose and configs.has_option('settings', 'debug'):
        args.verbose = configs.getboolean('settings', 'debug')
    if not args.logfile and configs.has_option('settings', 'logfile'):
        args.logfile = configs.get('settings', 'logfile')

    return args, configs


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

    args, configs = parseArguments(argv)
    if configs is None:
        return 103 # config file parsing error

    setup_logging(args, __version__)

    ignore = should_ignore(args.targetFile, args.ignore)
    if ignore is not False:
        log.debug('File ignored because matches pattern: %s' % ignore)
        return 0

    if os.path.isfile(args.targetFile):

        stats = get_file_stats(args.targetFile)

        project = find_project(args.targetFile, configs=configs)
        branch = None
        project_name = None
        if project:
            branch = project.branch()
            project_name = project.name()

        if send_action(
                project=project_name,
                branch=branch,
                stats=stats,
                **vars(args)
            ):
            return 0 # success

        return 102 # api error

    else:
        log.debug('File does not exist; ignoring this action.')
        return 0
