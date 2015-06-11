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
from pygments.lexers import guess_lexer, guess_lexer_for_filename


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
    """Guess lexer and language for a file.

    Returns (language, lexer) tuple where language is a unicode string.
    """

    lexer = smart_guess_lexer(file_name)

    language = None

    # guess language from file extension
    if file_name:
        language = guess_language_from_extension(file_name.rsplit('.', 1)[-1])

    # get language from lexer if we didn't have a hard-coded extension rule
    if language is None and lexer:
        language = translate_language(u(lexer.name))

    return language, lexer


def smart_guess_lexer(file_name):
    """Guess Pygments lexer for a file.

    Looks for a vim modeline in file contents, then compares the accuracy
    of that lexer with a second guess. The second guess looks up all lexers
    matching the file name, then runs a text analysis for the best choice.
    """
    lexer = None

    text = get_file_contents(file_name)

    try:
        guess_1 = guess_lexer(text)
    except:
        guess_1 = None
    try:
        guess_2 = guess_lexer_for_filename(file_name, text)
    except:
        guess_2 = None
    try:
        accuracy_1 = guess_1.analyse_text(text)
    except:
        accuracy_1 = None
    try:
        accuracy_2 = guess_2.analyse_text(text)
    except:
        accuracy_2 = None

    if accuracy_1:
        lexer = guess_1
    if (accuracy_2 and
        (not accuracy_1 or accuracy_2 > accuracy_1)):
        lexer = guess_2

    return lexer


def guess_language_from_extension(extension):
    """Checks hard-coded extension map for a matching language.
    """

    if extension:
        if extension in EXTENSIONS:
            return EXTENSIONS[extension]
        if extension.lower() in EXTENSIONS:
            return EXTENSIONS[extension.lower()]
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
