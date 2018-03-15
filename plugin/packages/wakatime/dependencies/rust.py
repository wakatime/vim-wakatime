# -*- coding: utf-8 -*-
"""
    wakatime.dependencies.rust
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Parse dependencies from Rust code.

    :copyright: (c) 2018 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

from . import TokenParser


class RustParser(TokenParser):
    state = None

    def parse(self):
        for index, token, content in self.tokens:
            self._process_token(token, content)
        return self.dependencies

    def _process_token(self, token, content):
        if self.partial(token) == 'Keyword':
            self._process_keyword(token, content)
        elif self.partial(token) == 'Whitespace':
            self._process_whitespace(token, content)
        elif self.partial(token) == 'Name':
            self._process_name(token, content)
        else:
            self._process_other(token, content)

    def _process_keyword(self, token, content):
        if self.state == 'extern' and content == 'crate':
            self.state = 'extern crate'
        else:
            self.state = content

    def _process_whitespace(self, token, content):
        pass

    def _process_name(self, token, content):
        if self.state == 'extern crate':
            self.append(content)
        self.state = None

    def _process_other(self, token, content):
        self.state = None
