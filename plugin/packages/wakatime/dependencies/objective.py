# -*- coding: utf-8 -*-
"""
    wakatime.dependencies.objective
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Parse dependencies from Objective-C and Swift code.

    :copyright: (c) 2018 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

import re

from . import TokenParser


class SwiftParser(TokenParser):
    state = None
    exclude = [
        r'^foundation$',
    ]

    def parse(self):
        for index, token, content in self.tokens:
            self._process_token(token, content)
        return self.dependencies

    def _process_token(self, token, content):
        if self.partial(token) == 'Declaration':
            self._process_declaration(token, content)
        elif self.partial(token) == 'Class':
            self._process_class(token, content)
        else:
            self._process_other(token, content)

    def _process_declaration(self, token, content):
        if self.state is None:
            self.state = content

    def _process_class(self, token, content):
        if self.state == 'import':
            self.append(content)
        self.state = None

    def _process_other(self, token, content):
        pass


class ObjectiveCParser(TokenParser):
    state = None
    extension = re.compile(r'\.[mh]$')

    def parse(self):
        for index, token, content in self.tokens:
            self._process_token(token, content)
        return self.dependencies

    def _process_token(self, token, content):
        if self.partial(token) == 'Preproc':
            self._process_preproc(token, content)
        else:
            self._process_other(token, content)

    def _process_preproc(self, token, content):
        if self.state:
            self._process_import(token, content)

        self.state = content

    def _process_import(self, token, content):
        if self.state == '#' and content.startswith('import '):
            self.append(self._format(content))
        self.state = None

    def _process_other(self, token, content):
        pass

    def _format(self, content):
        content = content.strip().lstrip('import ').strip()
        content = content.strip('"').strip("'").strip()
        content = content.strip('<').strip('>').strip()
        content = content.split('/')[0]
        content = self.extension.sub('', content, count=1)
        return content
