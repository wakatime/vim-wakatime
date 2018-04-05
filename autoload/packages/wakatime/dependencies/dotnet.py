# -*- coding: utf-8 -*-
"""
    wakatime.dependencies.dotnet
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Parse dependencies from .NET code.

    :copyright: (c) 2014 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

from . import TokenParser
from ..compat import u


class CSharpParser(TokenParser):
    exclude = [
        r'^system$',
        r'^microsoft$',
    ]
    state = None
    buffer = u('')

    def parse(self):
        for index, token, content in self.tokens:
            self._process_token(token, content)
        return self.dependencies

    def _process_token(self, token, content):
        if self.partial(token) == 'Keyword':
            self._process_keyword(token, content)
        if self.partial(token) == 'Namespace' or self.partial(token) == 'Name':
            self._process_namespace(token, content)
        elif self.partial(token) == 'Punctuation':
            self._process_punctuation(token, content)
        else:
            self._process_other(token, content)

    def _process_keyword(self, token, content):
        if content == 'using':
            self.state = 'import'
            self.buffer = u('')

    def _process_namespace(self, token, content):
        if self.state == 'import':
            if u(content) != u('import') and u(content) != u('package') and u(content) != u('namespace') and u(content) != u('static'):
                if u(content) == u(';'):  # pragma: nocover
                    self._process_punctuation(token, content)
                else:
                    self.buffer += u(content)

    def _process_punctuation(self, token, content):
        if self.state == 'import':
            if u(content) == u(';'):
                self.append(self.buffer, truncate=True)
                self.buffer = u('')
                self.state = None
            elif u(content) == u('='):
                self.buffer = u('')
            else:
                self.buffer += u(content)

    def _process_other(self, token, content):
        pass
