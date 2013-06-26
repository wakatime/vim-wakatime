#!/usr/bin/env python

import os
import sys
import argparse
import platform
import urllib2
import json
import base64
import uuid
import time
import re
from collections import OrderedDict
from httplib import BadStatusLine, IncompleteRead
from urllib2 import HTTPError, URLError
import logging as log


# Config
version = '0.1.2'
user_agent = 'vim-wakatime/%s (%s)' % (version, platform.platform())


def project_from_path(path):
    project = git_project(path)
    if project:
        return project
    return None


def tags_from_path(path):
    tags = []
    if os.path.exists(path):
        tags.extend(git_tags(path))
        tags.extend(mercurial_tags(path))
    return list(set(tags))


def git_project(path):
    config_file = find_git_config(path)
    if config_file:
        folder = os.path.split(os.path.split(os.path.split(config_file)[0])[0])[1]
        if folder:
            return folder
    return None


def find_git_config(path):
    path = os.path.realpath(path)
    if os.path.isfile(path):
        path = os.path.split(path)[0]
    if os.path.isfile(os.path.join(path, '.git', 'config')):
        return os.path.join(path, '.git', 'config')
    split_path = os.path.split(path)
    if split_path[1] == '':
        return None
    return find_git_config(split_path[0])


def parse_git_config(config):
    sections = OrderedDict()
    try:
        f = open(config, 'r')
    except IOError as e:
        log.exception("Exception:")
    else:
        with f:
            section = None
            for line in f.readlines():
                line = line.lstrip()
                if len(line) > 0 and line[0] == '[':
                    section = line[1:].split(']', 1)[0]
                    temp = section.split(' ', 1)
                    section = temp[0].lower()
                    if len(temp) > 1:
                        section = ' '.join([section, temp[1]])
                    sections[section] = OrderedDict()
                else:
                    try:
                        (setting, value) = line.split('=', 1)
                    except ValueError:
                        setting = line.split('#', 1)[0].split(';', 1)[0]
                        value = 'true'
                    setting = setting.strip().lower()
                    value = value.split('#', 1)[0].split(';', 1)[0].strip()
                    sections[section][setting] = value
            f.close()
    return sections


def git_tags(path):
    tags = []
    config_file = find_git_config(path)
    if config_file:
        sections = parse_git_config(config_file)
        for section in sections:
            if section.split(' ', 1)[0] == 'remote' and 'url' in sections[section]:
                tags.append(sections[section]['url'])
    return tags


def mercurial_tags(path):
    tags = []
    return tags


def svn_tags(path):
    tags = []
    return tags


def log_action(**kwargs):
    kwargs['User-Agent'] = user_agent
    log.info(json.dumps(kwargs))


def send_action(key, instance, action, task, timestamp, project, tags):
    url = 'https://www.wakati.me/api/v1/actions'
    data = {
        'type': action,
        'task': task,
        'time': time.time(),
        'instance_id': instance,
        'project': project,
        'tags': tags,
    }
    if timestamp:
        data['time'] = timestamp
    request = urllib2.Request(url=url, data=json.dumps(data))
    request.add_header('User-Agent', user_agent)
    request.add_header('Content-Type', 'application/json')
    request.add_header('Authorization', 'Basic %s' % base64.b64encode(key))
    log_action(**data)
    response = None
    try:
        response = urllib2.urlopen(request)
    except HTTPError as ex:
        log.error("%s:\ndata=%s\nresponse=%s" % (ex.getcode(), json.dumps(data), ex.read()))
        if log.getLogger().isEnabledFor(log.DEBUG):
            log.exception("Exception for %s:\n%s" % (data['time'], json.dumps(data)))
    except (URLError, IncompleteRead, BadStatusLine) as ex:
        log.error("%s:\ndata=%s\nmessage=%s" % (ex.__class__.__name__, json.dumps(data), ex))
        if log.getLogger().isEnabledFor(log.DEBUG):
            log.exception("Exception for %s:\n%s" % (data['time'], json.dumps(data)))
    if response:
        log.debug('response_code=%s response_content=%s' % (response.getcode(), response.read()))
    if response and (response.getcode() == 200 or response.getcode() == 201):
        return True
    return False


def parse_args(argv):
    parser = argparse.ArgumentParser(description='Log time to the wakati.me api')
    parser.add_argument('--key', dest='key', required=True,
                        help='your wakati.me api key')
    parser.add_argument('--action', dest='action', required=True,
                        choices=['open_file', 'ping', 'close_file', 'write_file', 'open_editor', 'quit_editor', 'minimize_editor', 'maximize_editor', 'start', 'stop'])
    parser.add_argument('--task', dest='task', required=True,
                        help='path to file or named task')
    parser.add_argument('--instance', dest='instance', required=True,
                        help='the UUID4 representing the current editor')
    parser.add_argument('--time', dest='timestamp', metavar='time', type=float,
                        help='optional floating-point timestamp in seconds')
    parser.add_argument('--verbose', dest='verbose', action='store_true',
                        help='turns on debug messages in logfile')
    parser.add_argument('--version', action='version', version=version)
    return parser.parse_args(argv)


def main(argv):
    args = parse_args(argv)
    level = log.INFO
    if args.verbose:
        level = log.DEBUG
    del args.verbose
    log.basicConfig(filename=os.path.expanduser('~/.wakatime.log'), format='%(asctime)s vim-wakatime/'+version+' %(levelname)s %(message)s', datefmt='%Y-%m-%dT%H:%M:%SZ', level=level)
    tags = tags_from_path(args.task)
    project = project_from_path(args.task)
    send_action(project=project, tags=tags, **vars(args))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
