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

    def parse(self):
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


class HtmlDjangoParser(TokenParser):
    tags = []
    getting_attrs = False
    current_attr = None
    current_attr_value = None

    def parse(self):
        for index, token, content in self.tokens:
            self._process_token(token, content)
        return self.dependencies

    def _process_token(self, token, content):
        if u(token) == 'Token.Name.Tag':
            self._process_tag(token, content)
        elif u(token) == 'Token.Literal.String':
            self._process_string(token, content)
        elif u(token) == 'Token.Name.Attribute':
            self._process_attribute(token, content)

    @property
    def current_tag(self):
        return None if len(self.tags) == 0 else self.tags[0]

    def _process_tag(self, token, content):
        if content.startswith('</') or content.startswith('/'):
            try:
                self.tags.pop(0)
            except IndexError:
                # ignore errors from malformed markup
                pass
            self.getting_attrs = False
        elif content.startswith('<'):
            self.tags.insert(0, content.replace('<', '', 1).strip().lower())
            self.getting_attrs = True
        elif content.startswith('>'):
            self.getting_attrs = False
        self.current_attr = None

    def _process_attribute(self, token, content):
        if self.getting_attrs:
            self.current_attr = content.lower().strip('=')
        else:
            self.current_attr = None
        self.current_attr_value = None

    def _process_string(self, token, content):
        if self.getting_attrs and self.current_attr is not None:
            if content.endswith('"') or content.endswith("'"):
                if self.current_attr_value is not None:
                    self.current_attr_value += content
                    if self.current_tag == 'script' and self.current_attr == 'src':
                        self.append(self.current_attr_value)
                    self.current_attr = None
                    self.current_attr_value = None
                else:
                    if len(content) == 1:
                        self.current_attr_value = content
                    else:
                        if self.current_tag == 'script' and self.current_attr == 'src':
                            self.append(content)
                        self.current_attr = None
                        self.current_attr_value = None
            elif content.startswith('"') or content.startswith("'"):
                if self.current_attr_value is None:
                    self.current_attr_value = content
                else:
                    self.current_attr_value += content


class VelocityHtmlParser(HtmlDjangoParser):
    pass


class MyghtyHtmlParser(HtmlDjangoParser):
    pass


class MasonParser(HtmlDjangoParser):
    pass


class MakoHtmlParser(HtmlDjangoParser):
    pass


class CheetahHtmlParser(HtmlDjangoParser):
    pass


class HtmlGenshiParser(HtmlDjangoParser):
    pass


class RhtmlParser(HtmlDjangoParser):
    pass


class HtmlPhpParser(HtmlDjangoParser):
    pass


class HtmlSmartyParser(HtmlDjangoParser):
    pass


class EvoqueHtmlParser(HtmlDjangoParser):
    pass


class ColdfusionHtmlParser(HtmlDjangoParser):
    pass


class LassoHtmlParser(HtmlDjangoParser):
    pass


class HandlebarsHtmlParser(HtmlDjangoParser):
    pass


class YamlJinjaParser(HtmlDjangoParser):
    pass


class TwigHtmlParser(HtmlDjangoParser):
    pass
