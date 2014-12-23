# -*- coding: utf-8 -*-
"""
    wakatime.languages
    ~~~~~~~~~~~~~~~~~~

    Parse dependencies from a source code file.

    :copyright: (c) 2014 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

import logging

from ..compat import open, import_module


log = logging.getLogger('WakaTime')


class TokenParser(object):
    """The base class for all dependency parsers. To add support for your
    language, inherit from this class and implement the :meth:`parse` method
    to return a list of dependency strings.
    """
    source_file = None
    lexer = None
    dependencies = []
    tokens = []

    def __init__(self, source_file, lexer=None):
        self.source_file = source_file
        self.lexer = lexer

    def parse(self, tokens=[]):
        """ Should return a list of dependencies.
        """
        if not tokens and not self.tokens:
            self.tokens = self._extract_tokens()
        raise Exception('Not yet implemented.')

    def append(self, dep, truncate=True):
        self._save_dependency(dep, truncate=truncate)

    def _extract_tokens(self):
        with open(self.source_file, 'r', encoding='utf-8') as fh:
            return self.lexer.get_tokens_unprocessed(fh.read(512000))

    def _save_dependency(self, dep, truncate=True):
        dep = dep.strip().split('.')[0].strip() if truncate else dep.strip()
        if dep:
            self.dependencies.append(dep)


class DependencyParser(object):
    source_file = None
    lexer = None
    parser = None

    def __init__(self, source_file, lexer):
        self.source_file = source_file
        self.lexer = lexer

        try:
            module_name = self.lexer.__module__.split('.')[-1]
            class_name = self.lexer.__class__.__name__.replace('Lexer', 'Parser', 1)
            module = import_module('.%s' % module_name, package=__package__)
            self.parser = getattr(module, class_name)
        except ImportError as ex:
            log.debug(ex)

    def parse(self):
        if self.parser:
            plugin = self.parser(self.source_file, lexer=self.lexer)
            dependencies = plugin.parse()
            return list(set(dependencies))
        return []
