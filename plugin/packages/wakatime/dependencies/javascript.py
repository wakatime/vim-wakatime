# -*- coding: utf-8 -*-
"""
    wakatime.dependencies.javascript
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Parse dependencies from JavaScript code.

    :copyright: (c) 2018 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

import re

from . import TokenParser


class JavascriptParser(TokenParser):
    state = None
    extension = re.compile(r'\.\w{1,4}$')

    def parse(self):
        for index, token, content in self.tokens:
            self._process_token(token, content)
        return self.dependencies

    def _process_token(self, token, content):
        if self.partial(token) == 'Reserved':
            self._process_reserved(token, content)
        elif self.partial(token) == 'Single':
            self._process_string(token, content)
        elif self.partial(token) == 'Punctuation':
            self._process_punctuation(token, content)
        else:
            self._process_other(token, content)

    def _process_reserved(self, token, content):
        if self.state is None:
            self.state = content

    def _process_string(self, token, content):
        if self.state == 'import':
            self.append(self._format_module(content))
        self.state = None

    def _process_punctuation(self, token, content):
        if content == ';':
            self.state = None

    def _process_other(self, token, content):
        pass

    def _format_module(self, content):
        content = content.strip().strip('"').strip("'").strip()
        content = content.split('/')[-1].split('\\')[-1]
        content = self.extension.sub('', content, count=1)
        return content


class TypeScriptParser(JavascriptParser):
    pass
