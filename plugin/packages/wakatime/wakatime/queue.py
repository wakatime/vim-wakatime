# -*- coding: utf-8 -*-
"""
    wakatime.queue
    ~~~~~~~~~~~~~~

    Queue for offline time logging.
    http://wakatime.com

    :copyright: (c) 2014 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""


import logging
import os
import traceback
from time import sleep

from .compat import u

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
        c.execute('''CREATE TABLE IF NOT EXISTS action (
            file text,
            time real,
            project text,
            language text,
            lines integer,
            branch text,
            is_write integer,
            plugin text)
        ''')
        return (conn, c)


    def push(self, data, plugin):
        if not HAS_SQL:
            return
        try:
            conn, c = self.connect()
            action = {
                'file': data.get('file'),
                'time': data.get('time'),
                'project': data.get('project'),
                'language': data.get('language'),
                'lines': data.get('lines'),
                'branch': data.get('branch'),
                'is_write': 1 if data.get('is_write') else 0,
                'plugin': plugin,
            }
            c.execute('INSERT INTO action VALUES (:file,:time,:project,:language,:lines,:branch,:is_write,:plugin)', action)
            conn.commit()
            conn.close()
        except sqlite3.Error:
            log.error(traceback.format_exc())


    def pop(self):
        if not HAS_SQL:
            return None
        tries = 3
        wait = 0.1
        action = None
        try:
            conn, c = self.connect()
        except sqlite3.Error:
            log.debug(traceback.format_exc())
            return None
        loop = True
        while loop and tries > -1:
            try:
                c.execute('BEGIN IMMEDIATE')
                c.execute('SELECT * FROM action LIMIT 1')
                row = c.fetchone()
                if row is not None:
                    values = []
                    clauses = []
                    index = 0
                    for row_name in ['file', 'time', 'project', 'language', 'lines', 'branch', 'is_write']:
                        if row[index] is not None:
                            clauses.append('{0}=?'.format(row_name))
                            values.append(u(row[index]))
                        else:
                            clauses.append('{0} IS NULL'.format(row_name))
                        index += 1
                    if len(values) > 0:
                        c.execute('DELETE FROM action WHERE {0}'.format(' AND '.join(clauses)), values)
                    else:
                        c.execute('DELETE FROM action WHERE {0}'.format(' AND '.join(clauses)))
                conn.commit()
                if row is not None:
                    action = {
                        'file': row[0],
                        'time': row[1],
                        'project': row[2],
                        'language': row[3],
                        'lines': row[4],
                        'branch': row[5],
                        'is_write': True if row[6] is 1 else False,
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
        return action
