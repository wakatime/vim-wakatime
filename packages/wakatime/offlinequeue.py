# -*- coding: utf-8 -*-
"""
    wakatime.offlinequeue
    ~~~~~~~~~~~~~~~~~~~~~

    Queue for saving heartbeats while offline.

    :copyright: (c) 2014 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""


import logging
import os
from time import sleep

from .compat import json
from .constants import DEFAULT_SYNC_OFFLINE_ACTIVITY, HEARTBEATS_PER_REQUEST
from .heartbeat import Heartbeat


try:
    import sqlite3
    HAS_SQL = True
except ImportError:  # pragma: nocover
    HAS_SQL = False


log = logging.getLogger('WakaTime')


class Queue(object):
    db_file = '.wakatime.db'
    table_name = 'heartbeat_2'

    args = None
    configs = None

    def __init__(self, args, configs):
        self.args = args
        self.configs = configs

    def connect(self):
        conn = sqlite3.connect(self._get_db_file(), isolation_level=None)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS {0} (
            id text,
            heartbeat text)
        '''.format(self.table_name))
        return (conn, c)

    def push(self, heartbeat):
        if not HAS_SQL:
            return
        try:
            conn, c = self.connect()
            data = {
                'id': heartbeat.get_id(),
                'heartbeat': heartbeat.json(),
            }
            c.execute('INSERT INTO {0} VALUES (:id,:heartbeat)'.format(self.table_name), data)
            conn.commit()
            conn.close()
        except sqlite3.Error:
            log.traceback()

    def pop(self):
        if not HAS_SQL:
            return None
        tries = 3
        wait = 0.1
        try:
            conn, c = self.connect()
        except sqlite3.Error:
            log.traceback(logging.DEBUG)
            return None

        heartbeat = None

        loop = True
        while loop and tries > -1:
            try:
                c.execute('BEGIN IMMEDIATE')
                c.execute('SELECT * FROM {0} LIMIT 1'.format(self.table_name))
                row = c.fetchone()
                if row is not None:
                    id = row[0]
                    heartbeat = Heartbeat(json.loads(row[1]), self.args, self.configs, _clone=True)
                    c.execute('DELETE FROM {0} WHERE id=?'.format(self.table_name), [id])
                conn.commit()
                loop = False
            except sqlite3.Error:
                log.traceback(logging.DEBUG)
                sleep(wait)
                tries -= 1
        try:
            conn.close()
        except sqlite3.Error:
            log.traceback(logging.DEBUG)
        return heartbeat

    def push_many(self, heartbeats):
        for heartbeat in heartbeats:
            self.push(heartbeat)

    def pop_many(self, limit=None):
        if limit is None:
            limit = DEFAULT_SYNC_OFFLINE_ACTIVITY

        heartbeats = []

        count = 0
        while count < limit:
            heartbeat = self.pop()
            if not heartbeat:
                break
            heartbeats.append(heartbeat)
            count += 1
            if count % HEARTBEATS_PER_REQUEST == 0:
                yield heartbeats
                heartbeats = []

        if heartbeats:
            yield heartbeats

    def _get_db_file(self):
        home = '~'
        if os.environ.get('WAKATIME_HOME'):
            home = os.environ.get('WAKATIME_HOME')
        return os.path.join(os.path.expanduser(home), '.wakatime.db')
