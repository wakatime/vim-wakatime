# -*- coding: utf-8 -*-
"""
    wakatime.dependencies.elm
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Parse dependencies from Elm code.

    :copyright: (c) 2018 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

from . import TokenParser


class ElmParser(TokenParser):
    state = None

    def parse(self):
        for index, token, content in self.tokens:
            self._process_token(token, content)
        return self.dependencies

    def _process_token(self, token, content):
        if self.partial(token) == 'Namespace':
            self._process_namespace(token, content)
        elif self.partial(token) == 'Text':
            self._process_text(token, content)
        elif self.partial(token) == 'Class':
            self._process_class(token, content)
        else:
            self._process_other(token, content)

    def _process_namespace(self, token, content):
        self.state = content.strip()

    def _process_class(self, token, content):
        if self.state == 'import':
            self.append(self._format(content))

    def _process_text(self, token, content):
        pass

    def _process_other(self, token, content):
        self.state = None

    def _format(self, content):
        return content.strip().split('.')[0].strip()
