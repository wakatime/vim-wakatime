# -*- coding: utf-8 -*-
"""
    wakatime.dependencies.c_cpp
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Parse dependencies from C++ code.

    :copyright: (c) 2014 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

from . import TokenParser


class CParser(TokenParser):
    exclude = [
        r'^stdio\.h$',
        r'^stdlib\.h$',
        r'^string\.h$',
        r'^time\.h$',
    ]
    state = None

    def parse(self):
        for index, token, content in self.tokens:
            self._process_token(token, content)
        return self.dependencies

    def _process_token(self, token, content):
        if self.partial(token) == 'Preproc' or self.partial(token) == 'PreprocFile':
            self._process_preproc(token, content)
        else:
            self._process_other(token, content)

    def _process_preproc(self, token, content):
        if self.state == 'include':
            if content != '\n' and content != '#':
                content = content.strip().strip('"').strip('<').strip('>').strip()
                self.append(content, truncate=True, separator='/')
            self.state = None
        elif content.strip().startswith('include'):
            self.state = 'include'
        else:
            self.state = None

    def _process_other(self, token, content):
        pass


class CppParser(CParser):
    pass
