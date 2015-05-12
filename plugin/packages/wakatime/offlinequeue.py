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
import traceback
from time import sleep

try:
    import sqlite3
    HAS_SQL = True
except ImportError:
    HAS_SQL = False


log = logging.getLogger('WakaTime')


class Queue(object):
    DB_FILE = os.path.join(os.path.expanduser('~'), '.wakatime.db')

    def connect(self):
        conn = sqlite3.connect(self.DB_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS heartbeat (
            file text,
            time real,
            project text,
            branch text,
            is_write integer,
            stats text,
            misc text,
            plugin text)
        ''')
        return (conn, c)


    def push(self, data, stats, plugin, misc=None):
        if not HAS_SQL:
            return
        try:
            conn, c = self.connect()
            heartbeat = {
                'file': data.get('file'),
                'time': data.get('time'),
                'project': data.get('project'),
                'branch': data.get('branch'),
                'is_write': 1 if data.get('is_write') else 0,
                'stats': stats,
                'misc': misc,
                'plugin': plugin,
            }
            c.execute('INSERT INTO heartbeat VALUES (:file,:time,:project,:branch,:is_write,:stats,:misc,:plugin)', heartbeat)
            conn.commit()
            conn.close()
        except sqlite3.Error:
            log.error(traceback.format_exc())


    def pop(self):
        if not HAS_SQL:
            return None
        tries = 3
        wait = 0.1
        heartbeat = None
        try:
            conn, c = self.connect()
        except sqlite3.Error:
            log.debug(traceback.format_exc())
            return None
        loop = True
        while loop and tries > -1:
            try:
                c.execute('BEGIN IMMEDIATE')
                c.execute('SELECT * FROM heartbeat LIMIT 1')
                row = c.fetchone()
                if row is not None:
                    values = []
                    clauses = []
                    index = 0
                    for row_name in ['file', 'time', 'project', 'branch', 'is_write']:
                        if row[index] is not None:
                            clauses.append('{0}=?'.format(row_name))
                            values.append(row[index])
                        else:
                            clauses.append('{0} IS NULL'.format(row_name))
                        index += 1
                    if len(values) > 0:
                        c.execute('DELETE FROM heartbeat WHERE {0}'.format(' AND '.join(clauses)), values)
                    else:
                        c.execute('DELETE FROM heartbeat WHERE {0}'.format(' AND '.join(clauses)))
                conn.commit()
                if row is not None:
                    heartbeat = {
                        'file': row[0],
                        'time': row[1],
                        'project': row[2],
                        'branch': row[3],
                        'is_write': True if row[4] is 1 else False,
                        'stats': row[5],
                        'misc': row[6],
                        'plugin': row[7],
                    }
                loop = False
            except sqlite3.Error:
                log.debug(traceback.format_exc())
                sleep(wait)
                tries -= 1
        try:
            conn.close()
        except sqlite3.Error:
            log.debug(traceback.format_exc())
        return heartbeat
