# -*- coding: utf-8 -*-
"""
    wakatime.arguments
    ~~~~~~~~~~~~~~~~~~

    Command-line arguments.

    :copyright: (c) 2016 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""


from __future__ import print_function


import os
import re
import time
import traceback
from .__about__ import __version__
from .configs import parseConfigFile
from .constants import AUTH_ERROR
from .packages import argparse


class FileAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        try:
            if os.path.isfile(values):
                values = os.path.realpath(values)
        except:  # pragma: nocover
            pass
        setattr(namespace, self.dest, values)


def parseArguments():
    """Parse command line arguments and configs from ~/.wakatime.cfg.
    Command line arguments take precedence over config file settings.
    Returns instances of ArgumentParser and SafeConfigParser.
    """

    # define supported command line arguments
    parser = argparse.ArgumentParser(
            description='Common interface for the WakaTime api.')
    parser.add_argument('--entity', dest='entity', metavar='FILE',
            action=FileAction,
            help='absolute path to file for the heartbeat; can also be a '+
                 'url, domain, or app when --entity-type is not file')
    parser.add_argument('--file', dest='file', action=FileAction,
            help=argparse.SUPPRESS)
    parser.add_argument('--key', dest='key',
            help='your wakatime api key; uses api_key from '+
                '~/.wakatime.cfg by default')
    parser.add_argument('--write', dest='is_write',
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
    parser.add_argument('--entity-type', dest='entity_type',
            help='entity type for this heartbeat. can be one of "file", '+
                 '"domain", or "app"; defaults to file.')
    parser.add_argument('--proxy', dest='proxy',
                        help='optional proxy configuration. Supports HTTPS '+
                        'and SOCKS proxies. For example: '+
                        'https://user:pass@host:port or '+
                        'socks5://user:pass@host:port or ' +
                        'domain\\user:pass')
    parser.add_argument('--project', dest='project',
            help='optional project name')
    parser.add_argument('--alternate-project', dest='alternate_project',
            help='optional alternate project name; auto-discovered project '+
                 'takes priority')
    parser.add_argument('--alternate-language',  dest='alternate_language',
            help=argparse.SUPPRESS)
    parser.add_argument('--language', dest='language',
            help='optional language name; if valid, takes priority over '+
                 'auto-detected language')
    parser.add_argument('--hostname', dest='hostname', help='hostname of '+
                        'current machine.')
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
    parser.add_argument('--extra-heartbeats', dest='extra_heartbeats',
            action='store_true',
            help='reads extra heartbeats from STDIN as a JSON array until EOF')
    parser.add_argument('--logfile', dest='logfile',
            help='defaults to ~/.wakatime.log')
    parser.add_argument('--apiurl', dest='api_url',
            help='heartbeats api url; for debugging with a local server')
    parser.add_argument('--timeout', dest='timeout', type=int,
            help='number of seconds to wait when sending heartbeats to api; '+
                 'defaults to 60 seconds')
    parser.add_argument('--config', dest='config',
            help='defaults to ~/.wakatime.cfg')
    parser.add_argument('--verbose', dest='verbose', action='store_true',
            help='turns on debug messages in log file')
    parser.add_argument('--version', action='version', version=__version__)

    # parse command line arguments
    args = parser.parse_args()

    # use current unix epoch timestamp by default
    if not args.timestamp:
        args.timestamp = time.time()

    # parse ~/.wakatime.cfg file
    configs = parseConfigFile(args.config)
    if configs is None:
        return args, configs

    # update args from configs
    if not args.hostname:
        if configs.has_option('settings', 'hostname'):
            args.hostname = configs.get('settings', 'hostname')
    if not args.key:
        default_key = None
        if configs.has_option('settings', 'api_key'):
            default_key = configs.get('settings', 'api_key')
        elif configs.has_option('settings', 'apikey'):
            default_key = configs.get('settings', 'apikey')
        if default_key:
            args.key = default_key
        else:
            try:
                parser.error('Missing api key. Find your api key from wakatime.com/settings.')
            except SystemExit:
                raise SystemExit(AUTH_ERROR)

    is_valid = not not re.match(r'^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$', args.key, re.I)
    if not is_valid:
        try:
            parser.error('Invalid api key. Find your api key from wakatime.com/settings.')
        except SystemExit:
            raise SystemExit(AUTH_ERROR)

    if not args.entity:
        if args.file:
            args.entity = args.file
        else:
            parser.error('argument --entity is required')

    if not args.language and args.alternate_language:
        args.language = args.alternate_language

    if not args.exclude:
        args.exclude = []
    if configs.has_option('settings', 'ignore'):
        try:
            for pattern in configs.get('settings', 'ignore').split("\n"):
                if pattern.strip() != '':
                    args.exclude.append(pattern)
        except TypeError:  # pragma: nocover
            pass
    if configs.has_option('settings', 'exclude'):
        try:
            for pattern in configs.get('settings', 'exclude').split("\n"):
                if pattern.strip() != '':
                    args.exclude.append(pattern)
        except TypeError:  # pragma: nocover
            pass
    if not args.include:
        args.include = []
    if configs.has_option('settings', 'include'):
        try:
            for pattern in configs.get('settings', 'include').split("\n"):
                if pattern.strip() != '':
                    args.include.append(pattern)
        except TypeError:  # pragma: nocover
            pass
    if args.hidefilenames:
        args.hidefilenames = ['.*']
    else:
        args.hidefilenames = []
        if configs.has_option('settings', 'hidefilenames'):
            option = configs.get('settings', 'hidefilenames')
            if option.strip().lower() == 'true':
                args.hidefilenames = ['.*']
            elif option.strip().lower() != 'false':
                for pattern in option.split("\n"):
                    if pattern.strip() != '':
                        args.hidefilenames.append(pattern)
    if args.offline and configs.has_option('settings', 'offline'):
        args.offline = configs.getboolean('settings', 'offline')
    if not args.proxy and configs.has_option('settings', 'proxy'):
        args.proxy = configs.get('settings', 'proxy')
    if args.proxy:
        pattern = r'^((https?|socks5)://)?([^:@]+(:([^:@])+)?@)?[^:]+(:\d+)?$'
        if '\\' in args.proxy:
            pattern = r'^.*\\.+$'
        is_valid = not not re.match(pattern, args.proxy, re.I)
        if not is_valid:
            parser.error('Invalid proxy. Must be in format ' +
                            'https://user:pass@host:port or ' +
                            'socks5://user:pass@host:port or ' +
                            'domain\\user:pass.')
    if not args.verbose and configs.has_option('settings', 'verbose'):
        args.verbose = configs.getboolean('settings', 'verbose')
    if not args.verbose and configs.has_option('settings', 'debug'):
        args.verbose = configs.getboolean('settings', 'debug')
    if not args.logfile and configs.has_option('settings', 'logfile'):
        args.logfile = configs.get('settings', 'logfile')
    if not args.logfile and os.environ.get('WAKATIME_HOME'):
        home = os.environ.get('WAKATIME_HOME')
        args.logfile = os.path.join(os.path.expanduser(home), '.wakatime.log')
    if not args.api_url and configs.has_option('settings', 'api_url'):
        args.api_url = configs.get('settings', 'api_url')
    if not args.timeout and configs.has_option('settings', 'timeout'):
        try:
            args.timeout = int(configs.get('settings', 'timeout'))
        except ValueError:
            print(traceback.format_exc())

    return args, configs
