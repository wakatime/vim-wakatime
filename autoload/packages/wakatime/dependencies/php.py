# -*- coding: utf-8 -*-
"""
    wakatime.dependencies.php
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Parse dependencies from PHP code.

    :copyright: (c) 2014 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

from . import TokenParser
from ..compat import u


class PhpParser(TokenParser):
    state = None
    parens = 0
    exclude = [
        r'^app$',
        r'app\.php$',
    ]

    def parse(self):
        for index, token, content in self.tokens:
            self._process_token(token, content)
        return self.dependencies

    def _process_token(self, token, content):
        if self.partial(token) == 'Keyword':
            self._process_keyword(token, content)
        elif u(token) == 'Token.Literal.String.Single' or u(token) == 'Token.Literal.String.Double':
            self._process_literal_string(token, content)
        elif u(token) == 'Token.Name.Other':
            self._process_name(token, content)
        elif u(token) == 'Token.Name.Function':
            self._process_function(token, content)
        elif self.partial(token) == 'Punctuation':
            self._process_punctuation(token, content)
        elif self.partial(token) == 'Text':
            self._process_text(token, content)
        else:
            self._process_other(token, content)

    def _process_name(self, token, content):
        if self.state == 'use':
            self.append(content, truncate=True, separator=u("\\"))

    def _process_function(self, token, content):
        if self.state == 'use function':
            self.append(content, truncate=True, separator=u("\\"))
            self.state = 'use'

    def _process_keyword(self, token, content):
        if content == 'include' or content == 'include_once' or content == 'require' or content == 'require_once':
            self.state = 'include'
        elif content == 'use':
            self.state = 'use'
        elif content == 'as':
            self.state = 'as'
        elif self.state == 'use' and content == 'function':
            self.state = 'use function'
        else:
            self.state = None

    def _process_literal_string(self, token, content):
        if self.state == 'include':
            if content != '"' and content != "'":
                content = content.strip()
                if u(token) == 'Token.Literal.String.Double':
                    content = u("'{0}'").format(content)
                self.append(content)
                self.state = None

    def _process_punctuation(self, token, content):
        if content == '(':
            self.parens += 1
        elif content == ')':
            self.parens -= 1
        elif (self.state == 'use' or self.state == 'as') and content == ',':
            self.state = 'use'
        else:
            self.state = None

    def _process_text(self, token, content):
        pass

    def _process_other(self, token, content):
        self.state = None
