# -*- coding: utf-8 -*-
"""
    wakatime.languages.templates
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Parse dependencies from Templates.

    :copyright: (c) 2014 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

from . import TokenParser
from ..compat import u


""" If these keywords are found in the source file, treat them as a dependency.
Must be lower-case strings.
"""
KEYWORDS = [
    '_',
    '$',
    'angular',
    'assert', # probably mocha
    'backbone',
    'batman',
    'c3',
    'can',
    'casper',
    'chai',
    'chaplin',
    'd3',
    'define', # probably require
    'describe', # mocha or jasmine
    'eco',
    'ember',
    'espresso',
    'expect', # probably jasmine
    'exports', # probably npm
    'express',
    'gulp',
    'handlebars',
    'highcharts',
    'jasmine',
    'jquery',
    'jstz',
    'ko', # probably knockout
    'm', # probably mithril
    'marionette',
    'meteor',
    'moment',
    'monitorio',
    'mustache',
    'phantom',
    'pickadate',
    'pikaday',
    'qunit',
    'react',
    'reactive',
    'require', # probably the commonjs spec
    'ripple',
    'rivets',
    'socketio',
    'spine',
    'thorax',
    'underscore',
    'vue',
    'way',
    'zombie',
]


class LassoJavascriptParser(TokenParser):

    def parse(self, tokens=[]):
        if not tokens and not self.tokens:
            self.tokens = self._extract_tokens()
        for index, token, content in self.tokens:
            self._process_token(token, content)
        return self.dependencies

    def _process_token(self, token, content):
        if u(token) == 'Token.Name.Other':
            self._process_name(token, content)
        elif u(token) == 'Token.Literal.String.Single' or u(token) == 'Token.Literal.String.Double':
            self._process_literal_string(token, content)

    def _process_name(self, token, content):
        if content.lower() in KEYWORDS:
            self.append(content.lower())

    def _process_literal_string(self, token, content):
        if 'famous/core/' in content.strip('"').strip("'"):
            self.append('famous')
