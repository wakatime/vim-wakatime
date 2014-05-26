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
import sqlite3
from time import sleep


log = logging.getLogger(__name__)


class Queue(object):
    DB_FILE = os.path.join(os.path.expanduser('~'), '.wakatime.db')

    def connect(self):
        exists = os.path.exists(self.DB_FILE)
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


    def pop(self):
        tries = 3
        wait = 0.1
        action = None
        conn, c = self.connect()
        loop = True
        while loop and tries > -1:
            try:
                c.execute('BEGIN IMMEDIATE')
                c.execute('SELECT * FROM action LIMIT 1')
                row = c.fetchone()
                if row is not None:
                    c.execute('''DELETE FROM action WHERE
                        file=? AND time=? AND project=? AND language=? AND
                        lines=? AND branch=? AND is_write=?''', row[0:7])
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
            except sqlite3.Error, e:
                log.debug(str(e))
                sleep(wait)
                tries -= 1
        conn.close()
        return action
