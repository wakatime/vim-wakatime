# -*- coding: utf-8 -*-
"""
    wakatime.base
    ~~~~~~~~~~~~~

    wakatime module entry point.

    :copyright: (c) 2013 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import print_function

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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'packages'))

from .__about__ import __version__
from .compat import u, open, is_py3
from .logger import setup_logging
from .offlinequeue import Queue
from .packages import argparse
from .packages import simplejson as json
from .packages.requests.exceptions import RequestException
from .project import find_project
from .session_cache import SessionCache
from .stats import get_file_stats
try:
    from .packages import tzlocal
except:
    from .packages import tzlocal3 as tzlocal


log = logging.getLogger('WakaTime')


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

        with open(oldConfig, 'r', encoding='utf-8') as fh:
            for line in fh.readlines():
                line = line.split('=', 1)
                if len(line) == 2 and line[0].strip() and line[1].strip():
                    if line[0].strip() == 'ignore':
                        configs['ignore'].append(line[1].strip())
                    else:
                        configs[line[0].strip()] = line[1].strip()

        with open(configFile, 'w', encoding='utf-8') as fh:
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


def parseConfigFile(configFile=None):
    """Returns a configparser.SafeConfigParser instance with configs
    read from the config file. Default location of the config file is
    at ~/.wakatime.cfg.
    """

    if not configFile:
        configFile = os.path.join(os.path.expanduser('~'), '.wakatime.cfg')

    upgradeConfigFile(configFile)

    configs = configparser.SafeConfigParser()
    try:
        with open(configFile, 'r', encoding='utf-8') as fh:
            try:
                configs.readfp(fh)
            except configparser.Error:
                print(traceback.format_exc())
                return None
    except IOError:
        print(u('Error: Could not read from config file {0}').format(u(configFile)))
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
            help='absolute path to file for current heartbeat')
    parser.add_argument('--key', dest='key',
            help='your wakatime api key; uses api_key from '+
                '~/.wakatime.conf by default')
    parser.add_argument('--write', dest='isWrite',
            action='store_true',
            help='when set, tells api this heartbeat was triggered from '+
                 'writing to a file')
    parser.add_argument('--plugin', dest='plugin',
            help='optional text editor plugin name and version '+
                 'for User-Agent header')
    parser.add_argument('--time', dest='timestamp', metavar='time',
            type=float,
            help='optional floating-point unix epoch timestamp; '+
                 'uses current time by default')
    parser.add_argument('--lineno', dest='lineno',
            help='optional line number; current line being edited')
    parser.add_argument('--cursorpos', dest='cursorpos',
            help='optional cursor position in the current file')
    parser.add_argument('--notfile', dest='notfile', action='store_true',
            help='when set, will accept any value for the file. for example, '+
                 'a domain name or other item you want to log time towards.')
    parser.add_argument('--proxy', dest='proxy',
                        help='optional https proxy url; for example: '+
                        'https://user:pass@localhost:8080')
    parser.add_argument('--project', dest='project',
            help='optional project name')
    parser.add_argument('--alternate-project', dest='alternate_project',
            help='optional alternate project name; auto-discovered project takes priority')
    parser.add_argument('--disableoffline', dest='offline',
            action='store_false',
            help='disables offline time logging instead of queuing logged time')
    parser.add_argument('--hidefilenames', dest='hidefilenames',
            action='store_true',
            help='obfuscate file names; will not send file names to api')
    parser.add_argument('--exclude', dest='exclude', action='append',
            help='filename patterns to exclude from logging; POSIX regex '+
                 'syntax; can be used more than once')
    parser.add_argument('--include', dest='include', action='append',
            help='filename patterns to log; when used in combination with '+
                 '--exclude, files matching include will still be logged; '+
                 'POSIX regex syntax; can be used more than once')
    parser.add_argument('--ignore', dest='ignore', action='append',
            help=argparse.SUPPRESS)
    parser.add_argument('--logfile', dest='logfile',
            help='defaults to ~/.wakatime.log')
    parser.add_argument('--apiurl', dest='api_url',
            help='heartbeats api url; for debugging with a local server')
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
        elif configs.has_option('settings', 'apikey'):
            default_key = configs.get('settings', 'apikey')
        if default_key:
            args.key = default_key
        else:
            parser.error('Missing api key')
    if not args.exclude:
        args.exclude = []
    if configs.has_option('settings', 'ignore'):
        try:
            for pattern in configs.get('settings', 'ignore').split("\n"):
                if pattern.strip() != '':
                    args.exclude.append(pattern)
        except TypeError:
            pass
    if configs.has_option('settings', 'exclude'):
        try:
            for pattern in configs.get('settings', 'exclude').split("\n"):
                if pattern.strip() != '':
                    args.exclude.append(pattern)
        except TypeError:
            pass
    if not args.include:
        args.include = []
    if configs.has_option('settings', 'include'):
        try:
            for pattern in configs.get('settings', 'include').split("\n"):
                if pattern.strip() != '':
                    args.include.append(pattern)
        except TypeError:
            pass
    if args.offline and configs.has_option('settings', 'offline'):
        args.offline = configs.getboolean('settings', 'offline')
    if not args.hidefilenames and configs.has_option('settings', 'hidefilenames'):
        args.hidefilenames = configs.getboolean('settings', 'hidefilenames')
    if not args.proxy and configs.has_option('settings', 'proxy'):
        args.proxy = configs.get('settings', 'proxy')
    if not args.verbose and configs.has_option('settings', 'verbose'):
        args.verbose = configs.getboolean('settings', 'verbose')
    if not args.verbose and configs.has_option('settings', 'debug'):
        args.verbose = configs.getboolean('settings', 'debug')
    if not args.logfile and configs.has_option('settings', 'logfile'):
        args.logfile = configs.get('settings', 'logfile')
    if not args.api_url and configs.has_option('settings', 'api_url'):
        args.api_url = configs.get('settings', 'api_url')

    return args, configs


def should_exclude(fileName, include, exclude):
    if fileName is not None and fileName.strip() != '':
        try:
            for pattern in include:
                try:
                    compiled = re.compile(pattern, re.IGNORECASE)
                    if compiled.search(fileName):
                        return False
                except re.error as ex:
                    log.warning(u('Regex error ({msg}) for include pattern: {pattern}').format(
                        msg=u(ex),
                        pattern=u(pattern),
                    ))
        except TypeError:
            pass
        try:
            for pattern in exclude:
                try:
                    compiled = re.compile(pattern, re.IGNORECASE)
                    if compiled.search(fileName):
                        return pattern
                except re.error as ex:
                    log.warning(u('Regex error ({msg}) for exclude pattern: {pattern}').format(
                        msg=u(ex),
                        pattern=u(pattern),
                    ))
        except TypeError:
            pass
    return False


def get_user_agent(plugin):
    ver = sys.version_info
    python_version = '%d.%d.%d.%s.%d' % (ver[0], ver[1], ver[2], ver[3], ver[4])
    user_agent = u('wakatime/{ver} ({platform}) Python{py_ver}').format(
        ver=u(__version__),
        platform=u(platform.platform()),
        py_ver=python_version,
    )
    if plugin:
        user_agent = u('{user_agent} {plugin}').format(
            user_agent=user_agent,
            plugin=u(plugin),
        )
    else:
        user_agent = u('{user_agent} Unknown/0').format(
            user_agent=user_agent,
        )
    return user_agent


def send_heartbeat(project=None, branch=None, stats={}, key=None, targetFile=None,
        timestamp=None, isWrite=None, plugin=None, offline=None, notfile=False,
        hidefilenames=None, proxy=None, api_url=None, **kwargs):
    """Sends heartbeat as POST request to WakaTime api server.
    """

    if not api_url:
        api_url = 'https://wakatime.com/api/v1/heartbeats'
    log.debug('Sending heartbeat to api at %s' % api_url)
    data = {
        'time': timestamp,
        'file': targetFile,
    }
    if hidefilenames and targetFile is not None and not notfile:
        data['file'] = data['file'].rsplit('/', 1)[-1].rsplit('\\', 1)[-1]
        if len(data['file'].strip('.').split('.', 1)) > 1:
            data['file'] = u('HIDDEN.{ext}').format(ext=u(data['file'].strip('.').rsplit('.', 1)[-1]))
        else:
            data['file'] = u('HIDDEN')
    if stats.get('lines'):
        data['lines'] = stats['lines']
    if stats.get('language'):
        data['language'] = stats['language']
    if stats.get('dependencies'):
        data['dependencies'] = stats['dependencies']
    if stats.get('lineno'):
        data['lineno'] = stats['lineno']
    if stats.get('cursorpos'):
        data['cursorpos'] = stats['cursorpos']
    if isWrite:
        data['is_write'] = isWrite
    if project:
        data['project'] = project
    if branch:
        data['branch'] = branch
    log.debug(data)

    # setup api request
    request_body = json.dumps(data)
    api_key = u(base64.b64encode(str.encode(key) if is_py3 else key))
    auth = u('Basic {api_key}').format(api_key=api_key)
    headers = {
        'User-Agent': get_user_agent(plugin),
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': auth,
    }
    proxies = {}
    if proxy:
        proxies['https'] = proxy

    # add Olson timezone to request
    try:
        tz = tzlocal.get_localzone()
    except:
        tz = None
    if tz:
        headers['TimeZone'] = u(tz.zone)

    session_cache = SessionCache()
    session = session_cache.get()

    # log time to api
    response = None
    try:
        response = session.post(api_url, data=request_body, headers=headers,
                                 proxies=proxies)
    except RequestException:
        exception_data = {
            sys.exc_info()[0].__name__: u(sys.exc_info()[1]),
        }
        if log.isEnabledFor(logging.DEBUG):
            exception_data['traceback'] = traceback.format_exc()
        if offline:
            queue = Queue()
            queue.push(data, json.dumps(stats), plugin)
            if log.isEnabledFor(logging.DEBUG):
                log.warn(exception_data)
        else:
            log.error(exception_data)
    else:
        response_code = response.status_code if response is not None else None
        response_content = response.text if response is not None else None
        if response_code == 201:
            log.debug({
                'response_code': response_code,
            })
            session_cache.save(session)
            return True
        if offline:
            if response_code != 400:
                queue = Queue()
                queue.push(data, json.dumps(stats), plugin)
                if response_code == 401:
                    log.error({
                        'response_code': response_code,
                        'response_content': response_content,
                    })
                elif log.isEnabledFor(logging.DEBUG):
                    log.warn({
                        'response_code': response_code,
                        'response_content': response_content,
                    })
            else:
                log.error({
                    'response_code': response_code,
                    'response_content': response_content,
                })
        else:
            log.error({
                'response_code': response_code,
                'response_content': response_content,
            })
    session_cache.delete()
    return False


def main(argv=None):
    if not argv:
        argv = sys.argv

    args, configs = parseArguments(argv)
    if configs is None:
        return 103 # config file parsing error

    setup_logging(args, __version__)

    exclude = should_exclude(args.targetFile, args.include, args.exclude)
    if exclude is not False:
        log.debug(u('File not logged because matches exclude pattern: {pattern}').format(
            pattern=u(exclude),
        ))
        return 0

    if os.path.isfile(args.targetFile) or args.notfile:

        stats = get_file_stats(args.targetFile, notfile=args.notfile,
                               lineno=args.lineno, cursorpos=args.cursorpos)

        project = None
        if not args.notfile:
            project = find_project(args.targetFile, configs=configs)
        branch = None
        project_name = args.project
        if project:
            branch = project.branch()
            if not project_name:
                project_name = project.name()
        if not project_name:
            project_name = args.alternate_project

        kwargs = vars(args)
        if 'project' in kwargs:
            del kwargs['project']

        if send_heartbeat(
                project=project_name,
                branch=branch,
                stats=stats,
                **kwargs
            ):
            queue = Queue()
            while True:
                heartbeat = queue.pop()
                if heartbeat is None:
                    break
                sent = send_heartbeat(
                    project=heartbeat['project'],
                    targetFile=heartbeat['file'],
                    timestamp=heartbeat['time'],
                    branch=heartbeat['branch'],
                    stats=json.loads(heartbeat['stats']),
                    key=args.key,
                    isWrite=heartbeat['is_write'],
                    plugin=heartbeat['plugin'],
                    offline=args.offline,
                    hidefilenames=args.hidefilenames,
                    notfile=args.notfile,
                    proxy=args.proxy,
                    api_url=args.api_url,
                )
                if not sent:
                    break
            return 0 # success

        return 102 # api error

    else:
        log.debug('File does not exist; ignoring this heartbeat.')
        return 0
