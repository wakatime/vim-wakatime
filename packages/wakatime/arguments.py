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
from .compat import basestring
from .configs import getConfigFile, parseConfigFile
from .constants import AUTH_ERROR, DEFAULT_SYNC_OFFLINE_ACTIVITY, SUCCESS
from .packages import argparse


class FileAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        if isinstance(values, basestring) and values.startswith('"'):
            values = re.sub(r'\\"', '"', values.strip('"'))
        try:
            if os.path.isfile(values):
                values = os.path.realpath(values)
        except:  # pragma: nocover
            pass
        setattr(namespace, self.dest, values)


class StoreWithoutQuotes(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        if isinstance(values, basestring) and values.startswith('"'):
            values = re.sub(r'\\"', '"', values.strip('"'))
        setattr(namespace, self.dest, values)


def parse_arguments():
    """Parse command line arguments and configs from ~/.wakatime.cfg.
    Command line arguments take precedence over config file settings.
    Returns instances of ArgumentParser and SafeConfigParser.
    """

    # define supported command line arguments
    parser = argparse.ArgumentParser(description='Common interface for the ' +
                                                 'WakaTime api.')
    parser.add_argument('--entity', dest='entity', metavar='FILE',
                        action=FileAction,
                        help='Absolute path to file for the heartbeat. Can ' +
                             'also be a url, domain or app when ' +
                             '--entity-type is not file.')
    parser.add_argument('--file', dest='file', action=FileAction,
                        help=argparse.SUPPRESS)
    parser.add_argument('--key', dest='key', action=StoreWithoutQuotes,
                        metavar='API_KEY',
                        help='Your wakatime api key; uses api_key from ' +
                             '~/.wakatime.cfg by default.')
    parser.add_argument('--write', dest='is_write', action='store_true',
                        help='When set, tells api this heartbeat was ' +
                             'triggered from writing to a file.')
    parser.add_argument('--plugin', dest='plugin', action=StoreWithoutQuotes,
                        help='Optional text editor plugin name and version ' +
                             'for User-Agent header.')
    parser.add_argument('--time', dest='timestamp', metavar='time',
                        type=float, action=StoreWithoutQuotes,
                        help='Optional floating-point unix epoch timestamp. ' +
                             'Uses current time by default.')
    parser.add_argument('--lineno', dest='lineno', action=StoreWithoutQuotes,
                        metavar='INT',
                        help='Optional line number. This is the current ' +
                             'line being edited.')
    parser.add_argument('--cursorpos', dest='cursorpos',
                        metavar='INT', action=StoreWithoutQuotes,
                        help='Optional cursor position in the current file.')
    parser.add_argument('--entity-type', dest='entity_type',
                        action=StoreWithoutQuotes,
                        help='Entity type for this heartbeat. Can be ' +
                             '"file", "domain" or "app". Defaults to "file".')
    parser.add_argument('--category', dest='category',
                        action=StoreWithoutQuotes,
                        help='Category of this heartbeat activity. Can be ' +
                             '"coding", "building", "indexing", ' +
                             '"debugging", "running tests", ' +
                             '"writing tests", "manual testing", ' +
                             '"code reviewing", "browsing", or "designing". ' +
                             'Defaults to "coding".')
    parser.add_argument('--proxy', dest='proxy', action=StoreWithoutQuotes,
                        help='Optional proxy configuration. Supports HTTPS '+
                             'and SOCKS proxies. For example: '+
                             'https://user:pass@host:port or '+
                             'socks5://user:pass@host:port or ' +
                             'domain\\user:pass')
    parser.add_argument('--no-ssl-verify', dest='nosslverify',
                        action='store_true',
                        help='Disables SSL certificate verification for HTTPS '+
                             'requests. By default, SSL certificates are ' +
                             'verified.')
    parser.add_argument('--ssl-certs-file', dest='ssl_certs_file',
                        metavar='FILE', action=StoreWithoutQuotes,
                        help='Override the bundled Python Requests CA certs ' +
                             'file. By default, uses certifi for ca certs.')
    parser.add_argument('--project', dest='project', action=StoreWithoutQuotes,
                        help='Optional project name.')
    parser.add_argument('--alternate-project', dest='alternate_project',
                        metavar='PROJECT', action=StoreWithoutQuotes,
                        help='Optional alternate project name. ' +
                             'Auto-discovered project takes priority.')
    parser.add_argument('--alternate-language', dest='alternate_language',
                        action=StoreWithoutQuotes,
                        help=argparse.SUPPRESS)
    parser.add_argument('--language', dest='language',
                        action=StoreWithoutQuotes,
                        help='Optional language name. If valid, takes ' +
                             'priority over auto-detected language.')
    parser.add_argument('--local-file', dest='local_file', metavar='FILE',
                        action=FileAction,
                        help='Absolute path to local file for the ' +
                             'heartbeat. When --entity is a remote file, ' +
                             'this local file will be used for stats and ' +
                             'just the value of --entity sent with heartbeat.')
    parser.add_argument('--hostname', dest='hostname',
                        action=StoreWithoutQuotes,
                        help='Hostname of current machine.')
    parser.add_argument('--disable-offline', dest='offline',
                        action='store_false',
                        help='Disables offline time logging instead of ' +
                             'queuing logged time.')
    parser.add_argument('--disableoffline', dest='offline_deprecated',
                        action='store_true',
                        help=argparse.SUPPRESS)
    parser.add_argument('--hide-file-names', dest='hide_file_names',
                        action='store_true',
                        help='Obfuscate filenames. Will not send file names ' +
                             'to api.')
    parser.add_argument('--hide-filenames', dest='hide_filenames',
                        action='store_true',
                        help=argparse.SUPPRESS)
    parser.add_argument('--hidefilenames', dest='hidefilenames',
                        action='store_true',
                        help=argparse.SUPPRESS)
    parser.add_argument('--hide-project-names', dest='hide_project_names',
                        action='store_true',
                        help='Obfuscate project names. When a project ' +
                             'folder is detected instead of using the ' +
                             'folder name as the project, a ' +
                             '.wakatime-project file is created with a ' +
                             'random project name.')
    parser.add_argument('--hide-branch-names', dest='hide_branch_names',
                        action='store_true',
                        help='Obfuscate branch names. Will not send revision ' +
                             'control branch names to api.')
    parser.add_argument('--exclude', dest='exclude', action='append',
                        metavar='PATH',
                        help='Filename patterns to exclude from logging. ' +
                             'POSIX regex syntax. Can be used more than once.')
    parser.add_argument('--exclude-unknown-project',
                        dest='exclude_unknown_project', action='store_true',
                        help='When set, any activity where the project ' +
                             'cannot be detected will be ignored.')
    parser.add_argument('--include', dest='include', action='append',
                        metavar='PATH',
                        help='Filename patterns to log. When used in ' +
                             'combination with --exclude, files matching ' +
                             'include will still be logged. POSIX regex ' +
                             'syntax. Can be used more than once.')
    parser.add_argument('--include-only-with-project-file',
                        dest='include_only_with_project_file',
                        action='store_true',
                        help='Disables tracking folders unless they contain ' +
                             'a .wakatime-project file. Defaults to false.')
    parser.add_argument('--ignore', dest='ignore', action='append',
                        help=argparse.SUPPRESS)
    parser.add_argument('--extra-heartbeats', dest='extra_heartbeats',
                        action='store_true',
                        help='Reads extra heartbeats from STDIN as a JSON ' +
                             'array until EOF.')
    parser.add_argument('--log-file', dest='log_file',
                        metavar='FILE', action=StoreWithoutQuotes,
                        help='Defaults to ~/.wakatime.log.')
    parser.add_argument('--logfile', dest='logfile', action=StoreWithoutQuotes,
                        help=argparse.SUPPRESS)
    parser.add_argument('--api-url', dest='api_url', action=StoreWithoutQuotes,
                        metavar='URL',
                        help='Heartbeats api url. For debugging with a ' +
                             'local server.')
    parser.add_argument('--apiurl', dest='apiurl', action=StoreWithoutQuotes,
                        help=argparse.SUPPRESS)
    parser.add_argument('--timeout', dest='timeout', type=int,
                        metavar='SECONDS', action=StoreWithoutQuotes,
                        help='Number of seconds to wait when sending ' +
                             'heartbeats to api. Defaults to 60 seconds.')
    parser.add_argument('--sync-offline-activity', metavar='AMOUNT',
                        dest='sync_offline_activity',
                        action=StoreWithoutQuotes,
                        help='Amount of offline activity to sync from your ' +
                             'local ~/.wakatime.db sqlite3 file to your ' +
                             'WakaTime Dashboard before exiting. Can be ' +
                             '"none" or a positive integer number. Defaults ' +
                             'to 100, meaning for every heartbeat sent ' +
                             'while online, 100 offline heartbeats are ' +
                             'synced. Can be used without --entity to only ' +
                             'sync offline activity without generating new ' +
                             'heartbeats.')
    parser.add_argument('--today', dest='today',
                        action='store_true',
                        help='Prints dashboard time for Today, then exits.')
    parser.add_argument('--config', dest='config', action=StoreWithoutQuotes,
                        metavar='FILE', help='Defaults to ~/.wakatime.cfg.')
    parser.add_argument('--config-section', dest='config_section',
                        metavar='SECTION', action=StoreWithoutQuotes,
                        help='Optional config section when reading or ' +
                             'writing a config key. Defaults to [settings].')
    parser.add_argument('--config-read', dest='config_read',
                        metavar='KEY', action=StoreWithoutQuotes,
                        help='Prints value for the given config key, then ' +
                             'exits.')
    parser.add_argument('--config-write', dest='config_write',
                        nargs=2, metavar=('KEY', 'VALUE'),
                        action=StoreWithoutQuotes,
                        help='Writes value to a config key, then exits. ' +
                             'Expects two arguments, key and value.')
    parser.add_argument('--verbose', dest='verbose', action='store_true',
                        help='Turns on debug messages in log file.')
    parser.add_argument('--version', action='version', version=__version__)

    # parse command line arguments
    args = parser.parse_args()

    # parse ~/.wakatime.cfg file
    configs = parseConfigFile(args.config)

    if args.config_read:
        section = args.config_section or 'settings'
        key = args.config_read
        print(configs.get(section, key))
        raise SystemExit(SUCCESS)

    if args.config_write:
        section = args.config_section or 'settings'
        key = args.config_write[0]
        val = args.config_write[1]
        if not configs.has_section(section):
            configs.add_section(section)
        configs.set(section, key, val)
        with open(args.config or getConfigFile(), 'w', encoding='utf-8') as fh:
            configs.write(fh)
        raise SystemExit(SUCCESS)

    # use current unix epoch timestamp by default
    if not args.timestamp:
        args.timestamp = time.time()

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
                parser.error('Missing api key. Find your api key from wakatime.com/settings/api-key.')
            except SystemExit:
                raise SystemExit(AUTH_ERROR)

    is_valid = not not re.match(r'^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$', args.key, re.I)
    if not is_valid:
        try:
            parser.error('Invalid api key. Find your api key from wakatime.com/settings/api-key.')
        except SystemExit:
            raise SystemExit(AUTH_ERROR)

    if not args.entity:
        if args.file:
            args.entity = args.file
        elif (not args.sync_offline_activity or args.sync_offline_activity == 'none') and not args.today:
            parser.error('argument --entity is required')

    if not args.sync_offline_activity:
        args.sync_offline_activity = DEFAULT_SYNC_OFFLINE_ACTIVITY
    if args.sync_offline_activity == 'none':
        args.sync_offline_activity = 0
    try:
        args.sync_offline_activity = int(args.sync_offline_activity)
        if args.sync_offline_activity < 0:
            raise Exception('Error')
    except:
        parser.error('argument --sync-offline-activity must be "none" or an integer number')

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
    if not args.include_only_with_project_file and configs.has_option('settings', 'include_only_with_project_file'):
        args.include_only_with_project_file = configs.get('settings', 'include_only_with_project_file') == 'true'
    if not args.include:
        args.include = []
    if configs.has_option('settings', 'include'):
        try:
            for pattern in configs.get('settings', 'include').split("\n"):
                if pattern.strip() != '':
                    args.include.append(pattern)
        except TypeError:  # pragma: nocover
            pass
    if not args.exclude_unknown_project and configs.has_option('settings', 'exclude_unknown_project'):
        args.exclude_unknown_project = configs.getboolean('settings', 'exclude_unknown_project')
    _boolean_or_list('hide_file_names', args, configs, alternative_names=['hide_filenames', 'hidefilenames'])
    _boolean_or_list('hide_project_names', args, configs, alternative_names=['hide_projectnames', 'hideprojectnames'])
    _boolean_or_list('hide_branch_names', args, configs, alternative_names=['hide_branchnames', 'hidebranchnames'], default=None)
    if args.offline_deprecated:
        args.offline = False
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
    if configs.has_option('settings', 'no_ssl_verify'):
        args.nosslverify = configs.getboolean('settings', 'no_ssl_verify')
    if configs.has_option('settings', 'ssl_certs_file'):
        args.ssl_certs_file = configs.get('settings', 'ssl_certs_file')
    if not args.verbose and configs.has_option('settings', 'verbose'):
        args.verbose = configs.getboolean('settings', 'verbose')
    if not args.verbose and configs.has_option('settings', 'debug'):
        args.verbose = configs.getboolean('settings', 'debug')
    if not args.log_file and args.logfile:
        args.log_file = args.logfile
    if not args.log_file and configs.has_option('settings', 'log_file'):
        args.log_file = configs.get('settings', 'log_file')
    if not args.log_file and os.environ.get('WAKATIME_HOME'):
        home = os.environ.get('WAKATIME_HOME')
        args.log_file = os.path.join(os.path.expanduser(home), '.wakatime.log')
    if not args.api_url and args.apiurl:
        args.api_url = args.apiurl
    if not args.api_url and configs.has_option('settings', 'api_url'):
        args.api_url = configs.get('settings', 'api_url')
    if not args.timeout and configs.has_option('settings', 'timeout'):
        try:
            args.timeout = int(configs.get('settings', 'timeout'))
        except ValueError:
            print(traceback.format_exc())

    return args, configs


def _boolean_or_list(config_name, args, configs, alternative_names=[], default=[]):
    """Get a boolean or list of regexes from args and configs."""

    # when argument flag present, set to wildcard regex
    for key in alternative_names + [config_name]:
        if hasattr(args, key) and getattr(args, key):
            setattr(args, config_name, ['.*'])
            return

    setattr(args, config_name, default)

    option = None
    alternative_names.insert(0, config_name)
    for key in alternative_names:
        if configs.has_option('settings', key):
            option = configs.get('settings', key)
            break

    if option is not None:
        if option.strip().lower() == 'true':
            setattr(args, config_name, ['.*'])
        elif option.strip().lower() == 'false':
            setattr(args, config_name, [])
        else:
            for pattern in option.split("\n"):
                if pattern.strip() != '':
                    if not getattr(args, config_name):
                        setattr(args, config_name, [])
                    getattr(args, config_name).append(pattern)
