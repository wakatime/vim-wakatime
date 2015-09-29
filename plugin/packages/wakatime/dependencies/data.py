# -*- coding: utf-8 -*-
"""
    wakatime.languages.data
    ~~~~~~~~~~~~~~~~~~~~~~~

    Parse dependencies from data files.

    :copyright: (c) 2014 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

import os

from . import TokenParser
from ..compat import u


FILES = {
    'bower.json': {'exact': True, 'dependency': 'bower'},
    'component.json': {'exact': True, 'dependency': 'bower'},
    'package.json': {'exact': True, 'dependency': 'npm'},
}


class JsonParser(TokenParser):
    state = None
    level = 0

    def parse(self):
        self._process_file_name(os.path.basename(self.source_file))
        for index, token, content in self.tokens:
            self._process_token(token, content)
        return self.dependencies

    def _process_file_name(self, file_name):
        for key, value in FILES.items():
            found = (key == file_name) if value.get('exact') else (key.lower() in file_name.lower())
            if found:
                self.append(value['dependency'])

    def _process_token(self, token, content):
        if u(token) == 'Token.Name.Tag':
            self._process_tag(token, content)
        elif u(token) == 'Token.Literal.String.Single' or u(token) == 'Token.Literal.String.Double':
            self._process_literal_string(token, content)
        elif u(token) == 'Token.Punctuation':
            self._process_punctuation(token, content)

    def _process_tag(self, token, content):
        if content.strip('"').strip("'") == 'dependencies' or content.strip('"').strip("'") == 'devDependencies':
            self.state = 'dependencies'
        elif self.state == 'dependencies' and self.level == 2:
            self.append(content.strip('"').strip("'"))

    def _process_literal_string(self, token, content):
        pass

    def _process_punctuation(self, token, content):
        if content == '{':
            self.level += 1
        elif content == '}':
            self.level -= 1
            if self.state is not None and self.level <= 1:
                self.state = None
