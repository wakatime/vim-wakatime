# -*- coding: utf-8 -*-
"""
    wakatime.dependencies.java
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Parse dependencies from Java code.

    :copyright: (c) 2014 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

from . import TokenParser
from ..compat import u


class JavaParser(TokenParser):
    exclude = [
        r'^java\.',
        r'^javax\.',
        r'^import$',
        r'^package$',
        r'^namespace$',
        r'^static$',
    ]
    state = None
    buffer = u('')

    def parse(self):
        for index, token, content in self.tokens:
            self._process_token(token, content)
        return self.dependencies

    def _process_token(self, token, content):
        if self.partial(token) == 'Namespace':
            self._process_namespace(token, content)
        if self.partial(token) == 'Name':
            self._process_name(token, content)
        elif self.partial(token) == 'Attribute':
            self._process_attribute(token, content)
        elif self.partial(token) == 'Operator':
            self._process_operator(token, content)
        else:
            self._process_other(token, content)

    def _process_namespace(self, token, content):
        if u(content).split() and u(content).split()[0] == u('import'):
            self.state = 'import'

        elif self.state == 'import':
            keywords = [
                u('package'),
                u('namespace'),
                u('static'),
            ]
            if u(content) in keywords:
                return
            self.buffer = u('{0}{1}').format(self.buffer, u(content))

        elif self.state == 'import-finished':
            content = content.split(u('.'))

            if len(content) == 1:
                self.append(content[0])

            elif len(content) > 1:
                if len(content[0]) == 3:
                    content = content[1:]
                if content[-1] == u('*'):
                    content = content[:len(content) - 1]

                if len(content) == 1:
                    self.append(content[0])
                elif len(content) > 1:
                    self.append(u('.').join(content[:2]))

            self.state = None

    def _process_name(self, token, content):
        if self.state == 'import':
            self.buffer = u('{0}{1}').format(self.buffer, u(content))

    def _process_attribute(self, token, content):
        if self.state == 'import':
            self.buffer = u('{0}{1}').format(self.buffer, u(content))

    def _process_operator(self, token, content):
        if u(content) == u(';'):
            self.state = 'import-finished'
            self._process_namespace(token, self.buffer)
            self.state = None
            self.buffer = u('')
        elif self.state == 'import':
            self.buffer = u('{0}{1}').format(self.buffer, u(content))

    def _process_other(self, token, content):
        pass


class KotlinParser(TokenParser):
    state = None
    exclude = [
        r'^java\.',
    ]

    def parse(self):
        for index, token, content in self.tokens:
            self._process_token(token, content)
        return self.dependencies

    def _process_token(self, token, content):
        if self.partial(token) == 'Keyword':
            self._process_keyword(token, content)
        elif self.partial(token) == 'Text':
            self._process_text(token, content)
        elif self.partial(token) == 'Namespace':
            self._process_namespace(token, content)
        else:
            self._process_other(token, content)

    def _process_keyword(self, token, content):
        self.state = content

    def _process_text(self, token, content):
        pass

    def _process_namespace(self, token, content):
        if self.state == 'import':
            self.append(self._format(content))
        self.state = None

    def _process_other(self, token, content):
        self.state = None

    def _format(self, content):
        content = content.split(u('.'))

        if content[-1] == u('*'):
            content = content[:len(content) - 1]

        if len(content) == 0:
            return None

        if len(content) == 1:
            return content[0]

        return u('.').join(content[:2])


class ScalaParser(TokenParser):
    state = None

    def parse(self):
        for index, token, content in self.tokens:
            self._process_token(token, content)
        return self.dependencies

    def _process_token(self, token, content):
        if self.partial(token) == 'Keyword':
            self._process_keyword(token, content)
        elif self.partial(token) == 'Text':
            self._process_text(token, content)
        elif self.partial(token) == 'Namespace':
            self._process_namespace(token, content)
        else:
            self._process_other(token, content)

    def _process_keyword(self, token, content):
        self.state = content

    def _process_text(self, token, content):
        pass

    def _process_namespace(self, token, content):
        if self.state == 'import':
            self.append(self._format(content))
        self.state = None

    def _process_other(self, token, content):
        self.state = None

    def _format(self, content):
        return content.strip().lstrip('__root__').strip('_').strip('.')
