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
from pygments.lexers import get_lexer_by_name, guess_lexer_for_filename
from pygments.modeline import get_filetype_from_buffer
from pygments.util import ClassNotFound


log = logging.getLogger('WakaTime')


# extensions taking priority over lexer
EXTENSIONS = {
    'j2': 'HTML',
    'markdown': 'Markdown',
    'md': 'Markdown',
    'mdown': 'Markdown',
    'twig': 'Twig',
}

# lexers to human readable languages
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

# extensions for when no lexer is found
AUXILIARY_EXTENSIONS = {
    'vb': 'VB.net',
}


def guess_language(file_name):
    """Guess lexer and language for a file.

    Returns (language, lexer) tuple where language is a unicode string.
    """

    lexer = smart_guess_lexer(file_name)

    language = None

    # guess language from file extension
    if file_name:
        language = get_language_from_extension(file_name, EXTENSIONS)

    # get language from lexer if we didn't have a hard-coded extension rule
    if language is None and lexer:
        language = u(lexer.name)

    if language is None:
        language = get_language_from_extension(file_name, AUXILIARY_EXTENSIONS)

    if language is not None:
        language = translate_language(language)

    return language, lexer


def smart_guess_lexer(file_name):
    """Guess Pygments lexer for a file.

    Looks for a vim modeline in file contents, then compares the accuracy
    of that lexer with a second guess. The second guess looks up all lexers
    matching the file name, then runs a text analysis for the best choice.
    """
    lexer = None

    text = get_file_contents(file_name)

    lexer_1, accuracy_1 = guess_lexer_using_filename(file_name, text)
    lexer_2, accuracy_2 = guess_lexer_using_modeline(text)

    if lexer_1:
        lexer = lexer_1
    if (lexer_2 and accuracy_2 and
        (not accuracy_1 or accuracy_2 > accuracy_1)):
        lexer = lexer_2

    return lexer


def guess_lexer_using_filename(file_name, text):
    """Guess lexer for given text, limited to lexers for this file's extension.

    Returns a tuple of (lexer, accuracy).
    """

    lexer, accuracy = None, None

    try:
        lexer = guess_lexer_for_filename(file_name, text)
    except:
        pass

    if lexer is not None:
        try:
            accuracy = lexer.analyse_text(text)
        except:
            pass

    return lexer, accuracy


def guess_lexer_using_modeline(text):
    """Guess lexer for given text using Vim modeline.

    Returns a tuple of (lexer, accuracy).
    """

    lexer, accuracy = None, None

    file_type = None
    try:
        file_type = get_filetype_from_buffer(text)
    except:
        pass

    if file_type is not None:
        try:
            lexer = get_lexer_by_name(file_type)
        except ClassNotFound:
            pass

    if lexer is not None:
        try:
            accuracy = lexer.analyse_text(text)
        except:
            pass

    return lexer, accuracy


def get_language_from_extension(file_name, extension_map):
    """Returns a matching language for the given file_name using extension_map.
    """

    extension = file_name.rsplit('.', 1)[-1] if len(file_name.rsplit('.', 1)) > 1 else None

    if extension:
        if extension in extension_map:
            return extension_map[extension]
        if extension.lower() in extension_map:
            return extension_map[extension.lower()]

    return None


def translate_language(language):
    """Turns Pygments lexer class name string into human-readable language.
    """

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


def get_file_contents(file_name):
    """Returns the first 512000 bytes of the file's contents.
    """

    text = None
    try:
        with open(file_name, 'r', encoding='utf-8') as fh:
            text = fh.read(512000)
    except:
        pass
    return text
