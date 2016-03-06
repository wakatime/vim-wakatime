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
from .dependencies import DependencyParser

if sys.version_info[0] == 2:  # pragma: nocover
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'packages', 'pygments_py2'))
else:  # pragma: nocover
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'packages', 'pygments_py3'))
from pygments.lexers import get_lexer_by_name, guess_lexer_for_filename
from pygments.modeline import get_filetype_from_buffer
from pygments.util import ClassNotFound


log = logging.getLogger('WakaTime')


def guess_language(file_name):
    """Guess lexer and language for a file.

    Returns (language, lexer) tuple where language is a unicode string.
    """

    language = get_language_from_extension(file_name)
    lexer = smart_guess_lexer(file_name)
    if language is None and lexer is not None:
        language = u(lexer.name)

    return language, lexer


def smart_guess_lexer(file_name):
    """Guess Pygments lexer for a file.

    Looks for a vim modeline in file contents, then compares the accuracy
    of that lexer with a second guess. The second guess looks up all lexers
    matching the file name, then runs a text analysis for the best choice.
    """
    lexer = None

    text = get_file_contents(file_name)

    lexer1, accuracy1 = guess_lexer_using_filename(file_name, text)
    lexer2, accuracy2 = guess_lexer_using_modeline(text)

    if lexer1:
        lexer = lexer1
    if (lexer2 and accuracy2 and
        (not accuracy1 or accuracy2 > accuracy1)):
        lexer = lexer2  # pragma: nocover

    return lexer


def guess_lexer_using_filename(file_name, text):
    """Guess lexer for given text, limited to lexers for this file's extension.

    Returns a tuple of (lexer, accuracy).
    """

    lexer, accuracy = None, None

    try:
        lexer = guess_lexer_for_filename(file_name, text)
    except:  # pragma: nocover
        pass

    if lexer is not None:
        try:
            accuracy = lexer.analyse_text(text)
        except:  # pragma: nocover
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
    except:  # pragma: nocover
        pass

    if file_type is not None:
        try:
            lexer = get_lexer_by_name(file_type)
        except ClassNotFound:  # pragma: nocover
            pass

    if lexer is not None:
        try:
            accuracy = lexer.analyse_text(text)
        except:  # pragma: nocover
            pass

    return lexer, accuracy


def get_language_from_extension(file_name):
    """Returns a matching language for the given file extension.
    """

    filepart, extension = os.path.splitext(file_name)

    if os.path.exists(u('{0}{1}').format(u(filepart), u('.c'))) or os.path.exists(u('{0}{1}').format(u(filepart), u('.C'))):
        return 'C'

    extension = extension.lower()
    if extension == '.h':
        directory = os.path.dirname(file_name)
        available_files = os.listdir(directory)
        available_extensions = list(zip(*map(os.path.splitext, available_files)))[1]
        available_extensions = [ext.lower() for ext in available_extensions]
        if '.cpp' in available_extensions:
            return 'C++'
        if '.c' in available_extensions:
            return 'C'

    return None


def number_lines_in_file(file_name):
    lines = 0
    try:
        with open(file_name, 'r', encoding='utf-8') as fh:
            for line in fh:
                lines += 1
    except:  # pragma: nocover
        try:
            with open(file_name, 'r', encoding=sys.getfilesystemencoding()) as fh:
                for line in fh:
                    lines += 1
        except:
            return None
    return lines


def get_file_stats(file_name, entity_type='file', lineno=None, cursorpos=None):
    if entity_type != 'file':
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
    except:  # pragma: nocover
        try:
            with open(file_name, 'r', encoding=sys.getfilesystemencoding()) as fh:
                text = fh.read(512000)
        except:
            log.traceback('debug')
    return text
