# -*- coding: utf-8 -*-
"""
    wakatime.stats
    ~~~~~~~~~~~~~~

    Stats about files

    :copyright: (c) 2013 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""

import logging
import os
import sys

from .compat import u, open
from .languages import DependencyParser

if sys.version_info[0] == 2:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'packages', 'pygments_py2'))
else:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'packages', 'pygments_py3'))
from pygments.lexers import guess_lexer_for_filename


log = logging.getLogger('WakaTime')


# force file name extensions to be recognized as a certain language
EXTENSIONS = {
    'j2': 'HTML',
    'markdown': 'Markdown',
    'md': 'Markdown',
    'mdown': 'Markdown',
    'twig': 'Twig',
}
TRANSLATIONS = {
    'CSS+Genshi Text': 'CSS',
    'CSS+Lasso': 'CSS',
    'HTML+Django/Jinja': 'HTML',
    'HTML+Lasso': 'HTML',
    'JavaScript+Genshi Text': 'JavaScript',
    'JavaScript+Lasso': 'JavaScript',
    'Perl6': 'Perl',
    'RHTML': 'HTML',
}


def guess_language(file_name):
    language, lexer = None, None
    try:
        with open(file_name, 'r', encoding='utf-8') as fh:
            lexer = guess_lexer_for_filename(file_name, fh.read(512000))
    except:
        pass
    if file_name:
        language = guess_language_from_extension(file_name.rsplit('.', 1)[-1])
    if lexer and language is None:
        language = translate_language(u(lexer.name))
    return language, lexer


def guess_language_from_extension(extension):
    if extension:
        if extension in EXTENSIONS:
            return EXTENSIONS[extension]
        if extension.lower() in EXTENSIONS:
            return EXTENSIONS[extension.lower()]
    return None


def translate_language(language):
    if language in TRANSLATIONS:
        language = TRANSLATIONS[language]
    return language


def number_lines_in_file(file_name):
    lines = 0
    try:
        with open(file_name, 'r', encoding='utf-8') as fh:
            for line in fh:
                lines += 1
    except:
        return None
    return lines


def get_file_stats(file_name, notfile=False, lineno=None, cursorpos=None):
    if notfile:
        stats = {
            'language': None,
            'dependencies': [],
            'lines': None,
            'lineno': lineno,
            'cursorpos': cursorpos,
        }
    else:
        language, lexer = guess_language(file_name)
        parser = DependencyParser(file_name, lexer)
        dependencies = parser.parse()
        stats = {
            'language': language,
            'dependencies': dependencies,
            'lines': number_lines_in_file(file_name),
            'lineno': lineno,
            'cursorpos': cursorpos,
        }
    return stats
