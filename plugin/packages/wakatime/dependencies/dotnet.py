# -*- coding: utf-8 -*-
"""
    wakatime.languages.dotnet
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Parse dependencies from .NET code.

    :copyright: (c) 2014 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

from . import TokenParser


class CSharpParser(TokenParser):

    def parse(self):
        for index, token, content in self.tokens:
            self._process_token(token, content)
        return self.dependencies

    def _process_token(self, token, content):
        if self.partial(token) == 'Namespace':
            self._process_namespace(token, content)
        else:
            self._process_other(token, content)

    def _process_namespace(self, token, content):
        if content != 'import' and content != 'package' and content != 'namespace':
            self.append(content, truncate=True)

    def _process_other(self, token, content):
        pass
