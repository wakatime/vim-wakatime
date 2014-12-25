# -*- coding: utf-8 -*-
"""
    wakatime.languages.python
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Parse dependencies from Python code.

    :copyright: (c) 2014 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

from . import TokenParser
from ..compat import u


class PythonParser(TokenParser):
    state = None
    parens = 0
    nonpackage = False

    def parse(self, tokens=[]):
        if not tokens and not self.tokens:
            self.tokens = self._extract_tokens()
        for index, token, content in self.tokens:
            self._process_token(token, content)
        return self.dependencies

    def _process_token(self, token, content):
        if u(token).split('.')[-1] == 'Namespace':
            self._process_namespace(token, content)
        elif u(token).split('.')[-1] == 'Name':
            self._process_name(token, content)
        elif u(token).split('.')[-1] == 'Word':
            self._process_word(token, content)
        elif u(token).split('.')[-1] == 'Operator':
            self._process_operator(token, content)
        elif u(token).split('.')[-1] == 'Punctuation':
            self._process_punctuation(token, content)
        elif u(token).split('.')[-1] == 'Text':
            self._process_text(token, content)
        else:
            self._process_other(token, content)

    def _process_namespace(self, token, content):
        if self.state is None:
            self.state = content
        else:
            if content == 'as':
                self.nonpackage = True
            else:
                self._process_import(token, content)

    def _process_name(self, token, content):
        if self.state is not None:
            if self.nonpackage:
                self.nonpackage = False
            else:
                if self.state == 'from':
                    self.append(content, truncate=True, truncate_to=0)
                if self.state == 'from-2' and content != 'import':
                    self.append(content, truncate=True, truncate_to=0)
                elif self.state == 'import':
                    self.append(content, truncate=True, truncate_to=0)
                elif self.state == 'import-2':
                    self.append(content, truncate=True, truncate_to=0)
                else:
                    self.state = None

    def _process_word(self, token, content):
        if self.state is not None:
            if self.nonpackage:
                self.nonpackage = False
            else:
                if self.state == 'from':
                    self.append(content, truncate=True, truncate_to=0)
                if self.state == 'from-2' and content != 'import':
                    self.append(content, truncate=True, truncate_to=0)
                elif self.state == 'import':
                    self.append(content, truncate=True, truncate_to=0)
                elif self.state == 'import-2':
                    self.append(content, truncate=True, truncate_to=0)
                else:
                    self.state = None

    def _process_operator(self, token, content):
        if self.state is not None:
            if content == '.':
                self.nonpackage = True

    def _process_punctuation(self, token, content):
        if content == '(':
            self.parens += 1
        elif content == ')':
            self.parens -= 1
        self.nonpackage = False

    def _process_text(self, token, content):
        if self.state is not None:
            if content == "\n" and self.parens == 0:
                self.state = None
                self.nonpackage = False

    def _process_other(self, token, content):
        pass

    def _process_import(self, token, content):
        if not self.nonpackage:
            if self.state == 'from':
                self.append(content, truncate=True, truncate_to=0)
                self.state = 'from-2'
            elif self.state == 'from-2' and content != 'import':
                self.append(content, truncate=True, truncate_to=0)
            elif self.state == 'import':
                self.append(content, truncate=True, truncate_to=0)
                self.state = 'import-2'
            elif self.state == 'import-2':
                self.append(content, truncate=True, truncate_to=0)
            else:
                self.state = None
        self.nonpackage = False
