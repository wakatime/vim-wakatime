# -*- coding: utf-8 -*-
"""
    wakatime.dependencies.python
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Parse dependencies from Python code.

    :copyright: (c) 2014 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

"""
Token.Keyword.Namespace import None
Token.Text   import
Token.Name.Namespace os import
Token.Operator , import-2
Token.Text   import-2
Token.Name.Namespace sys import-2
Token.Text
 import-2
Token.Keyword.Namespace import None
Token.Text   import
Token.Name.Namespace django.forms.monstertruck import
Token.Text
 import-2



Token.Keyword.Namespace import None
Token.Text   import
Token.Name.Namespace os import
Token.Operator , import-2
Token.Text   import-2
Token.Name.Namespace sys import-2
Token.Text
 import-2
Token.Keyword.Namespace import None
Token.Text   import
Token.Name.Namespace django import
Token.Name.Namespace . import-2
Token.Name.Namespace forms import-2
Token.Name.Namespace . import-2
Token.Name.Namespace monstertruck import-2
Token.Text
 import-2



None Token.Keyword.Namespace import
import Token.Text
import Token.Name.Namespace django
import-2 Token.Name.Namespace .
import-2 Token.Name.Namespace forms
import-2 Token.Name.Namespace .
import-2 Token.Name.Namespace monstertruck
import-2 Token.Text

None Token.Keyword.Namespace from
from Token.Text
from Token.Name.Namespace app
from-2 Token.Text
"""

from . import TokenParser


class PythonParser(TokenParser):
    state = None
    parens = 0
    nonpackage = False
    exclude = [
        r'^os$',
        r'^sys$',
        r'^sys\.',
        r'^__future__$',
    ]

    def parse(self):
        for index, token, content in self.tokens:
            self._process_token(token, content)
        return self.dependencies

    def _process_token(self, token, content):
        if self.partial(token) == 'Namespace':
            self._process_namespace(token, content)
        elif self.partial(token) == 'Operator':
            self._process_punctuation(token, content)
        elif self.partial(token) == 'Punctuation':
            self._process_punctuation(token, content)
        elif self.partial(token) == 'Text':
            self._process_text(token, content)
        else:
            self._process_other(token, content)

    def _process_namespace(self, token, content):
        if self.state is None:
            self.state = content
        elif content == 'as':
            self.nonpackage = True
        else:
            self._process_import(token, content)

    def _process_punctuation(self, token, content):
        if content == '(':
            self.parens += 1
            self.nonpackage = False
        elif content == ')':
            self.parens -= 1
            self.nonpackage = False
        elif content == ',' and self.state == 'import-2':
            self.state = 'import'

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
                self.append(content, truncate=True, truncate_to=1)
                self.state = None
            elif self.state == 'import':
                self.append(content, truncate=True, truncate_to=1)
                self.state = 'import-2'
            elif self.state == 'import-2':
                pass
            else:
                self.state = None
        self.nonpackage = False
