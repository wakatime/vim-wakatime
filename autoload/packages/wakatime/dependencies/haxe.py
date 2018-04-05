# -*- coding: utf-8 -*-
"""
    wakatime.dependencies.haxe
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Parse dependencies from Haxe code.

    :copyright: (c) 2018 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

from . import TokenParser


class HaxeParser(TokenParser):
    exclude = [
        r'^haxe$',
    ]
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
        else:
            self._process_other(token, content)

    def _process_namespace(self, token, content):
        if self.state == 'import':
            self.append(self._format(content))
            self.state = None
        else:
            self.state = content

    def _process_text(self, token, content):
        pass

    def _process_other(self, token, content):
        self.state = None

    def _format(self, content):
        return content.strip()
