# -*- coding: utf-8 -*-
"""
    wakatime.languages.c_cpp
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Parse dependencies from C++ code.

    :copyright: (c) 2014 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

from . import TokenParser


class CppParser(TokenParser):
    exclude = [
        r'^stdio\.h$',
        r'^stdlib\.h$',
        r'^string\.h$',
        r'^time\.h$',
    ]

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
        if content.strip().startswith('include ') or content.strip().startswith("include\t"):
            content = content.replace('include', '', 1).strip().strip('"').strip('<').strip('>').strip()
            self.append(content)

    def _process_other(self, token, content):
        pass


class CParser(TokenParser):
    exclude = [
        r'^stdio\.h$',
        r'^stdlib\.h$',
        r'^string\.h$',
        r'^time\.h$',
    ]

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
        if content.strip().startswith('include ') or content.strip().startswith("include\t"):
            content = content.replace('include', '', 1).strip().strip('"').strip('<').strip('>').strip()
            self.append(content)

    def _process_other(self, token, content):
        pass
