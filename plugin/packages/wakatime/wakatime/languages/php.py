# -*- coding: utf-8 -*-
"""
    wakatime.languages.php
    ~~~~~~~~~~~~~~~~~~~~~~

    Parse dependencies from PHP code.

    :copyright: (c) 2014 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

from . import TokenParser
from ..compat import u


class PhpParser(TokenParser):
    state = None
    parens = 0

    def parse(self, tokens=[]):
        if not tokens and not self.tokens:
            self.tokens = self._extract_tokens()
        for index, token, content in self.tokens:
            self._process_token(token, content)
        return self.dependencies

    def _process_token(self, token, content):
        if u(token).split('.')[-1] == 'Keyword':
            self._process_keyword(token, content)
        elif u(token) == 'Token.Literal.String.Single' or u(token) == 'Token.Literal.String.Double':
            self._process_literal_string(token, content)
        elif u(token).split('.')[-1] == 'Punctuation':
            self._process_punctuation(token, content)
        elif u(token).split('.')[-1] == 'Text':
            self._process_text(token, content)
        else:
            self._process_other(token, content)

    def _process_keyword(self, token, content):
        if content == 'include' or content == 'include_once' or content == 'require' or content == 'require_once':
            self.state = 'include'
        else:
            self.state = None

    def _process_literal_string(self, token, content):
        if self.state == 'include':
            if content != '"':
                content = content.strip()
                if u(token) == 'Token.Literal.String.Single':
                    content = content.strip("'")
                self.append(content, truncate=False)
                self.state = None

    def _process_punctuation(self, token, content):
        if content == '(':
            self.parens += 1
        elif content == ')':
            self.parens -= 1
        else:
            self.state = None

    def _process_text(self, token, content):
        pass

    def _process_other(self, token, content):
        self.state = None
