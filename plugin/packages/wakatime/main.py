# -*- coding: utf-8 -*-
"""
    wakatime.main
    ~~~~~~~~~~~~~

    Module entry point.

    :copyright: (c) 2013 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import print_function

import base64
import logging
import os
import re
import sys
import traceback
import socket

pwd = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(pwd))
sys.path.insert(0, os.path.join(pwd, 'packages'))

from .__about__ import __version__
from .arguments import parseArguments
from .compat import u, is_py3
from .constants import (
    API_ERROR,
    AUTH_ERROR,
    CONFIG_FILE_PARSE_ERROR,
    SUCCESS,
    UNKNOWN_ERROR,
    MALFORMED_HEARTBEAT_ERROR,
)
from .logger import setup_logging
from .offlinequeue import Queue
from .packages import requests
from .packages.requests.exceptions import RequestException
from .project import get_project_info
from .session_cache import SessionCache
from .stats import get_file_stats
from .utils import get_user_agent, should_exclude, format_file_path
try:
    from .packages import simplejson as json  # pragma: nocover
except (ImportError, SyntaxError):  # pragma: nocover
    import json
from .packages import tzlocal


log = logging.getLogger('WakaTime')


def send_heartbeat(project=None, branch=None, hostname=None, stats={}, key=None,
                   entity=None, timestamp=None, is_write=None, plugin=None,
                   offline=None, entity_type='file', hidefilenames=None,
                   proxy=None, api_url=None, timeout=None, **kwargs):
    """Sends heartbeat as POST request to WakaTime api server.

    Returns `SUCCESS` when heartbeat was sent, otherwise returns an
    error code constant.
    """

    if not api_url:
        api_url = 'https://api.wakatime.com/api/v1/heartbeats'
    if not timeout:
        timeout = 60
    log.debug('Sending heartbeat to api at %s' % api_url)
    data = {
        'time': timestamp,
        'entity': entity,
        'type': entity_type,
    }
    if hidefilenames and entity is not None and entity_type == 'file':
        for pattern in hidefilenames:
            try:
                compiled = re.compile(pattern, re.IGNORECASE)
                if compiled.search(entity):
                    extension = u(os.path.splitext(data['entity'])[1])
                    data['entity'] = u('HIDDEN{0}').format(extension)
                    break
            except re.error as ex:
                log.warning(u('Regex error ({msg}) for include pattern: {pattern}').format(
                    msg=u(ex),
                    pattern=u(pattern),
                ))
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
    if is_write:
        data['is_write'] = is_write
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
    if hostname:
        headers['X-Machine-Name'] = u(hostname).encode('utf-8')

    # add Olson timezone to request
    try:
        tz = tzlocal.get_localzone()
    except:
        tz = None
    if tz:
        headers['TimeZone'] = u(tz.zone).encode('utf-8')

    session_cache = SessionCache()
    session = session_cache.get()

    proxies = {}
    if proxy:
        if '\\' in proxy:
            from .packages.requests_ntlm import HttpNtlmAuth
            username = proxy.rsplit(':', 1)
            password = ''
            if len(username) == 2:
                password = username[1]
            username = username[0]
            session.auth = HttpNtlmAuth(username, password, session)
        else:
            proxies['https'] = proxy

    # log time to api
    response = None
    try:
        response = session.post(api_url, data=request_body, headers=headers,
                                proxies=proxies, timeout=timeout)
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

    except:  # delete cached session when requests raises unknown exception
        exception_data = {
            sys.exc_info()[0].__name__: u(sys.exc_info()[1]),
            'traceback': traceback.format_exc(),
        }
        if offline:
            queue = Queue()
            queue.push(data, json.dumps(stats), plugin)
            log.warn(exception_data)
        session_cache.delete()

    else:
        code = response.status_code if response is not None else None
        content = response.text if response is not None else None
        if code == requests.codes.created or code == requests.codes.accepted:
            log.debug({
                'response_code': code,
            })
            session_cache.save(session)
            return SUCCESS
        if offline:
            if code != 400:
                queue = Queue()
                queue.push(data, json.dumps(stats), plugin)
                if code == 401:
                    log.error({
                        'response_code': code,
                        'response_content': content,
                    })
                    session_cache.delete()
                    return AUTH_ERROR
                elif log.isEnabledFor(logging.DEBUG):
                    log.warn({
                        'response_code': code,
                        'response_content': content,
                    })
            else:
                log.error({
                    'response_code': code,
                    'response_content': content,
                })
        else:
            log.error({
                'response_code': code,
                'response_content': content,
            })
    session_cache.delete()
    return API_ERROR


def sync_offline_heartbeats(args, hostname):
    """Sends all heartbeats which were cached in the offline Queue."""

    queue = Queue()
    while True:
        heartbeat = queue.pop()
        if heartbeat is None:
            break
        status = send_heartbeat(
            project=heartbeat['project'],
            entity=heartbeat['entity'],
            timestamp=heartbeat['time'],
            branch=heartbeat['branch'],
            hostname=hostname,
            stats=json.loads(heartbeat['stats']),
            key=args.key,
            is_write=heartbeat['is_write'],
            plugin=heartbeat['plugin'],
            offline=args.offline,
            hidefilenames=args.hidefilenames,
            entity_type=heartbeat['type'],
            proxy=args.proxy,
            api_url=args.api_url,
            timeout=args.timeout,
        )
        if status != SUCCESS:
            if status == AUTH_ERROR:
                return AUTH_ERROR
            break
    return SUCCESS


def process_heartbeat(args, configs, hostname, heartbeat):
    exclude = should_exclude(heartbeat['entity'], args.include, args.exclude)
    if exclude is not False:
        log.debug(u('Skipping because matches exclude pattern: {pattern}').format(
            pattern=u(exclude),
        ))
        return SUCCESS

    if heartbeat.get('entity_type') not in ['file', 'domain', 'app']:
        heartbeat['entity_type'] = 'file'

    if heartbeat['entity_type'] == 'file':
        heartbeat['entity'] = format_file_path(heartbeat['entity'])

    if heartbeat['entity_type'] != 'file' or os.path.isfile(heartbeat['entity']):

        stats = get_file_stats(heartbeat['entity'],
                                entity_type=heartbeat['entity_type'],
                                lineno=heartbeat.get('lineno'),
                                cursorpos=heartbeat.get('cursorpos'),
                                plugin=args.plugin,
                                language=heartbeat.get('language'))

        project = heartbeat.get('project') or heartbeat.get('alternate_project')
        branch = None
        if heartbeat['entity_type'] == 'file':
            project, branch = get_project_info(configs, heartbeat)

        heartbeat['project'] = project
        heartbeat['branch'] = branch
        heartbeat['stats'] = stats
        heartbeat['hostname'] = hostname
        heartbeat['timeout'] = args.timeout
        heartbeat['key'] = args.key
        heartbeat['plugin'] = args.plugin
        heartbeat['offline'] = args.offline
        heartbeat['hidefilenames'] = args.hidefilenames
        heartbeat['proxy'] = args.proxy
        heartbeat['api_url'] = args.api_url

        return send_heartbeat(**heartbeat)

    else:
        log.debug('File does not exist; ignoring this heartbeat.')
        return SUCCESS


def execute(argv=None):
    if argv:
        sys.argv = ['wakatime'] + argv

    args, configs = parseArguments()
    if configs is None:
        return CONFIG_FILE_PARSE_ERROR

    setup_logging(args, __version__)

    try:

        hostname = args.hostname or socket.gethostname()

        heartbeat = vars(args)
        retval = process_heartbeat(args, configs, hostname, heartbeat)

        if args.extra_heartbeats:
            try:
                for heartbeat in json.loads(sys.stdin.readline()):
                    retval = process_heartbeat(args, configs, hostname, heartbeat)
            except json.JSONDecodeError:
                retval = MALFORMED_HEARTBEAT_ERROR

        if retval == SUCCESS:
            retval = sync_offline_heartbeats(args, hostname)

        return retval

    except:
        log.traceback(logging.ERROR)
        print(traceback.format_exc())
        return UNKNOWN_ERROR
