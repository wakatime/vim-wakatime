# -*- coding: utf-8 -*-
"""
    wakatime.languages.unknown
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Parse dependencies from files of unknown language.

    :copyright: (c) 2014 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

import os

from . import TokenParser


FILES = {
    'bower': {'exact': False, 'dependency': 'bower'},
    'grunt': {'exact': False, 'dependency': 'grunt'},
}


class UnknownParser(TokenParser):

    def parse(self):
        self._process_file_name(os.path.basename(self.source_file))
        return self.dependencies

    def _process_file_name(self, file_name):
        for key, value in FILES.items():
            found = (key == file_name) if value.get('exact') else (key.lower() in file_name.lower())
            if found:
                self.append(value['dependency'])
