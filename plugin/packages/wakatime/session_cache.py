# -*- coding: utf-8 -*-
"""
    wakatime.session_cache
    ~~~~~~~~~~~~~~~~~~~~~~

    Persist requests.Session for multiprocess SSL handshake pooling.

    :copyright: (c) 2015 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""


import logging
import os
import pickle
import sys

try:
    import sqlite3
    HAS_SQL = True
except ImportError:  # pragma: nocover
    HAS_SQL = False

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'packages'))

from .packages import requests


log = logging.getLogger('WakaTime')


class SessionCache(object):
    db_file = '.wakatime.db'
    table_name = 'session'

    def connect(self):
        conn = sqlite3.connect(self._get_db_file(), isolation_level=None)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS {0} (
            value BLOB)
        '''.format(self.table_name))
        return (conn, c)

    def save(self, session):
        """Saves a requests.Session object for the next heartbeat process.
        """

        if not HAS_SQL:  # pragma: nocover
            return
        try:
            conn, c = self.connect()
            c.execute('DELETE FROM {0}'.format(self.table_name))
            values = {
                'value': sqlite3.Binary(pickle.dumps(session, protocol=2)),
            }
            c.execute('INSERT INTO {0} VALUES (:value)'.format(self.table_name), values)
            conn.commit()
            conn.close()
        except:  # pragma: nocover
            log.traceback(logging.DEBUG)

    def get(self):
        """Returns a requests.Session object.

        Gets Session from sqlite3 cache or creates a new Session.
        """

        if not HAS_SQL:  # pragma: nocover
            return requests.session()

        try:
            conn, c = self.connect()
        except:
            log.traceback(logging.DEBUG)
            return requests.session()

        session = None
        try:
            c.execute('BEGIN IMMEDIATE')
            c.execute('SELECT value FROM {0} LIMIT 1'.format(self.table_name))
            row = c.fetchone()
            if row is not None:
                session = pickle.loads(row[0])
        except:  # pragma: nocover
            log.traceback(logging.DEBUG)

        try:
            conn.close()
        except:  # pragma: nocover
            log.traceback(logging.DEBUG)

        return session if session is not None else requests.session()

    def delete(self):
        """Clears all cached Session objects.
        """

        if not HAS_SQL:  # pragma: nocover
            return
        try:
            conn, c = self.connect()
            c.execute('DELETE FROM {0}'.format(self.table_name))
            conn.commit()
            conn.close()
        except:
            log.traceback(logging.DEBUG)

    def _get_db_file(self):
        home = '~'
        if os.environ.get('WAKATIME_HOME'):
            home = os.environ.get('WAKATIME_HOME')
        return os.path.join(os.path.expanduser(home), '.wakatime.db')
