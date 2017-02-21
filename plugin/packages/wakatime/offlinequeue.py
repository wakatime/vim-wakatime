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

try:
    import sqlite3
    HAS_SQL = True
except ImportError:  # pragma: nocover
    HAS_SQL = False

from .compat import u


log = logging.getLogger('WakaTime')


class Queue(object):
    db_file = os.path.join(os.path.expanduser('~'), '.wakatime.db')
    table_name = 'heartbeat_1'

    def get_db_file(self):
        return self.db_file

    def connect(self):
        conn = sqlite3.connect(self.get_db_file(), isolation_level=None)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS {0} (
            entity text,
            type text,
            time real,
            project text,
            branch text,
            is_write integer,
            stats text,
            misc text,
            plugin text)
        '''.format(self.table_name))
        return (conn, c)

    def push(self, data, stats, plugin, misc=None):
        if not HAS_SQL:  # pragma: nocover
            return
        try:
            conn, c = self.connect()
            heartbeat = {
                'entity': u(data.get('entity')),
                'type': u(data.get('type')),
                'time': data.get('time'),
                'project': u(data.get('project')),
                'branch': u(data.get('branch')),
                'is_write': 1 if data.get('is_write') else 0,
                'stats': u(stats),
                'misc': u(misc),
                'plugin': u(plugin),
            }
            c.execute('INSERT INTO {0} VALUES (:entity,:type,:time,:project,:branch,:is_write,:stats,:misc,:plugin)'.format(self.table_name), heartbeat)
            conn.commit()
            conn.close()
        except sqlite3.Error:
            log.traceback()

    def pop(self):
        if not HAS_SQL:  # pragma: nocover
            return None
        tries = 3
        wait = 0.1
        heartbeat = None
        try:
            conn, c = self.connect()
        except sqlite3.Error:
            log.traceback(logging.DEBUG)
            return None
        loop = True
        while loop and tries > -1:
            try:
                c.execute('BEGIN IMMEDIATE')
                c.execute('SELECT * FROM {0} LIMIT 1'.format(self.table_name))
                row = c.fetchone()
                if row is not None:
                    values = []
                    clauses = []
                    index = 0
                    for row_name in ['entity', 'type', 'time', 'project', 'branch', 'is_write']:
                        if row[index] is not None:
                            clauses.append('{0}=?'.format(row_name))
                            values.append(row[index])
                        else:  # pragma: nocover
                            clauses.append('{0} IS NULL'.format(row_name))
                        index += 1
                    if len(values) > 0:
                        c.execute('DELETE FROM {0} WHERE {1}'.format(self.table_name, ' AND '.join(clauses)), values)
                    else:  # pragma: nocover
                        c.execute('DELETE FROM {0} WHERE {1}'.format(self.table_name, ' AND '.join(clauses)))
                conn.commit()
                if row is not None:
                    heartbeat = {
                        'entity': row[0],
                        'type': row[1],
                        'time': row[2],
                        'project': row[3],
                        'branch': row[4],
                        'is_write': True if row[5] is 1 else False,
                        'stats': row[6],
                        'misc': row[7],
                        'plugin': row[8],
                    }
                loop = False
            except sqlite3.Error:  # pragma: nocover
                log.traceback(logging.DEBUG)
                sleep(wait)
                tries -= 1
        try:
            conn.close()
        except sqlite3.Error:  # pragma: nocover
            log.traceback(logging.DEBUG)
        return heartbeat
