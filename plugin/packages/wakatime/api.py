# -*- coding: utf-8 -*-
"""
    wakatime.api
    ~~~~~~~~~~~~

    :copyright: (c) 2017 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""


from __future__ import print_function

import base64
import logging
import sys
import traceback

from .compat import u, is_py3, json
from .constants import API_ERROR, AUTH_ERROR, SUCCESS, UNKNOWN_ERROR

from .offlinequeue import Queue
from .packages.requests.exceptions import RequestException
from .session_cache import SessionCache
from .utils import get_hostname, get_user_agent
from .packages import tzlocal


log = logging.getLogger('WakaTime')


try:
    from .packages import requests
except ImportError:  # pragma: nocover
    log.traceback(logging.ERROR)
    print(traceback.format_exc())
    log.error('Please upgrade Python to the latest version.')
    print('Please upgrade Python to the latest version.')
    sys.exit(UNKNOWN_ERROR)


def send_heartbeats(heartbeats, args, configs, use_ntlm_proxy=False):
    """Send heartbeats to WakaTime API.

    Returns `SUCCESS` when heartbeat was sent, otherwise returns an error code.
    """

    if len(heartbeats) == 0:
        return SUCCESS

    api_url = args.api_url
    if not api_url:
        api_url = 'https://api.wakatime.com/api/v1/users/current/heartbeats.bulk'
    log.debug('Sending heartbeats to api at %s' % api_url)
    timeout = args.timeout
    if not timeout:
        timeout = 60

    data = [h.sanitize().dict() for h in heartbeats]
    log.debug(data)

    # setup api request
    request_body = json.dumps(data)
    api_key = u(base64.b64encode(str.encode(args.key) if is_py3 else args.key))
    auth = u('Basic {api_key}').format(api_key=api_key)
    headers = {
        'User-Agent': get_user_agent(args.plugin),
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': auth,
    }

    hostname = get_hostname(args)
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

    should_try_ntlm = False
    proxies = {}
    if args.proxy:
        if use_ntlm_proxy:
            from .packages.requests_ntlm import HttpNtlmAuth
            username = args.proxy.rsplit(':', 1)
            password = ''
            if len(username) == 2:
                password = username[1]
            username = username[0]
            session.auth = HttpNtlmAuth(username, password, session)
        else:
            should_try_ntlm = '\\' in args.proxy
            proxies['https'] = args.proxy

    # send request to api
    response, code = None, None
    try:
        response = session.post(api_url, data=request_body, headers=headers,
                                proxies=proxies, timeout=timeout,
                                verify=not args.nosslverify)
    except RequestException:
        if should_try_ntlm:
            return send_heartbeats(heartbeats, args, configs, use_ntlm_proxy=True)
        else:
            exception_data = {
                sys.exc_info()[0].__name__: u(sys.exc_info()[1]),
            }
            if log.isEnabledFor(logging.DEBUG):
                exception_data['traceback'] = traceback.format_exc()
            if args.offline:
                queue = Queue(args, configs)
                queue.push_many(heartbeats)
                if log.isEnabledFor(logging.DEBUG):
                    log.warn(exception_data)
            else:
                log.error(exception_data)

    except:  # delete cached session when requests raises unknown exception
        if should_try_ntlm:
            return send_heartbeats(heartbeats, args, configs, use_ntlm_proxy=True)
        else:
            exception_data = {
                sys.exc_info()[0].__name__: u(sys.exc_info()[1]),
                'traceback': traceback.format_exc(),
            }
            if args.offline:
                queue = Queue(args, configs)
                queue.push_many(heartbeats)
                log.warn(exception_data)

    else:
        code = response.status_code if response is not None else None
        content = response.text if response is not None else None

        if _success(code):
            results = _get_results(response)
            _process_server_results(heartbeats, code, content, results, args, configs)
            session_cache.save(session)
            return SUCCESS
        else:
            log.debug({
                'response_code': code,
                'response_text': content,
            })

        if should_try_ntlm:
            return send_heartbeats(heartbeats, args, configs, use_ntlm_proxy=True)

        _handle_unsent_heartbeats(heartbeats, code, content, args, configs)

    session_cache.delete()
    return AUTH_ERROR if code == 401 else API_ERROR


def _process_server_results(heartbeats, code, content, results, args, configs):
    log.debug({
        'response_code': code,
        'results': results,
    })

    for i in range(len(results)):
        if len(heartbeats) <= i:
            log.warn('Results from api not matching heartbeats sent.')
            break

        try:
            c = results[i][1]
        except:
            log.traceback(logging.WARNING)
            c = 0
        try:
            text = json.dumps(results[i][0])
        except:
            log.traceback(logging.WARNING)
            text = ''
        if not _success(c):
            _handle_unsent_heartbeats([heartbeats[i]], c, text, args, configs)

    leftover = len(heartbeats) - len(results)
    if leftover > 0:
        log.warn('Missing {0} results from api.'.format(leftover))
        start = len(heartbeats) - leftover
        _handle_unsent_heartbeats(heartbeats[start:], code, content, args, configs)


def _handle_unsent_heartbeats(heartbeats, code, content, args, configs):
    if args.offline:
        if code == 400:
            log.error({
                'response_code': code,
                'response_content': content,
            })
        else:
            if log.isEnabledFor(logging.DEBUG):
                log.warn({
                    'response_code': code,
                    'response_content': content,
                })
            queue = Queue(args, configs)
            queue.push_many(heartbeats)
    else:
        log.error({
            'response_code': code,
            'response_content': content,
        })


def _get_results(response):
    results = []
    if response is not None:
        try:
            results = response.json()['responses']
        except:
            log.traceback(logging.WARNING)
    return results


def _success(code):
    return code == requests.codes.created or code == requests.codes.accepted
