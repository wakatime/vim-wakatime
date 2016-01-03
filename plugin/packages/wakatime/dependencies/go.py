# -*- coding: utf-8 -*-
"""
    wakatime.languages.go
    ~~~~~~~~~~~~~~~~~~~~~

    Parse dependencies from Go code.

    :copyright: (c) 2016 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

from . import TokenParser


class GoParser(TokenParser):
    state = None
    parens = 0
    aliases = 0
    exclude = [
        r'^"fmt"$',
    ]

    def parse(self):
        for index, token, content in self.tokens:
            self._process_token(token, content)
        return self.dependencies

    def _process_token(self, token, content):
        if self.partial(token) == 'Namespace':
            self._process_namespace(token, content)
        elif self.partial(token) == 'Punctuation':
            self._process_punctuation(token, content)
        elif self.partial(token) == 'String':
            self._process_string(token, content)
        elif self.partial(token) == 'Text':
            self._process_text(token, content)
        elif self.partial(token) == 'Other':
            self._process_other(token, content)
        else:
            self._process_misc(token, content)

    def _process_namespace(self, token, content):
        self.state = content
        self.parens = 0
        self.aliases = 0

    def _process_string(self, token, content):
        if self.state == 'import':
            self.append(content, truncate=False)

    def _process_punctuation(self, token, content):
        if content == '(':
            self.parens += 1
        elif content == ')':
            self.parens -= 1
        elif content == '.':
            self.aliases += 1
        else:
            self.state = None

    def _process_text(self, token, content):
        if self.state == 'import':
            if content == "\n" and self.parens <= 0:
                self.state = None
                self.parens = 0
                self.aliases = 0
        else:
            self.state = None

    def _process_other(self, token, content):
        if self.state == 'import':
            self.aliases += 1
        else:
            self.state = None

    def _process_misc(self, token, content):
        self.state = None
