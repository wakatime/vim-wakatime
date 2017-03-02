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
import re
import sys

from .compat import u, open
from .dependencies import DependencyParser

from .packages.pygments.lexers import (
    _iter_lexerclasses,
    _fn_matches,
    basename,
    ClassNotFound,
    find_lexer_class,
    get_lexer_by_name,
)
from .packages.pygments.modeline import get_filetype_from_buffer

try:
    from .packages import simplejson as json  # pragma: nocover
except (ImportError, SyntaxError):  # pragma: nocover
    import json


log = logging.getLogger('WakaTime')


def get_file_stats(file_name, entity_type='file', lineno=None, cursorpos=None,
                   plugin=None, language=None):
    if entity_type != 'file':
        stats = {
            'language': None,
            'dependencies': [],
            'lines': None,
            'lineno': lineno,
            'cursorpos': cursorpos,
        }
    else:
        language, lexer = standardize_language(language, plugin)
        if not language:
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


def guess_language(file_name):
    """Guess lexer and language for a file.

    Returns a tuple of (language_str, lexer_obj).
    """

    lexer = None

    language = get_language_from_extension(file_name)
    if language:
        lexer = get_lexer(language)
    else:
        lexer = smart_guess_lexer(file_name)
        if lexer:
            language = u(lexer.name)

    return language, lexer


def smart_guess_lexer(file_name):
    """Guess Pygments lexer for a file.

    Looks for a vim modeline in file contents, then compares the accuracy
    of that lexer with a second guess. The second guess looks up all lexers
    matching the file name, then runs a text analysis for the best choice.
    """
    lexer = None

    text = get_file_head(file_name)

    lexer1, accuracy1 = guess_lexer_using_filename(file_name, text)
    lexer2, accuracy2 = guess_lexer_using_modeline(text)

    if lexer1:
        lexer = lexer1
    if (lexer2 and accuracy2 and
        (not accuracy1 or accuracy2 > accuracy1)):
        lexer = lexer2

    return lexer


def guess_lexer_using_filename(file_name, text):
    """Guess lexer for given text, limited to lexers for this file's extension.

    Returns a tuple of (lexer, accuracy).
    """

    lexer, accuracy = None, None

    try:
        lexer = custom_pygments_guess_lexer_for_filename(file_name, text)
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
    except:  # pragma: nocover
        pass

    if file_type is not None:
        try:
            lexer = get_lexer_by_name(file_type)
        except ClassNotFound:
            pass

    if lexer is not None:
        try:
            accuracy = lexer.analyse_text(text)
        except:  # pragma: nocover
            pass

    return lexer, accuracy


def get_language_from_extension(file_name):
    """Returns a matching language for the given file extension.

    When guessed_language is 'C', does not restrict to known file extensions.
    """

    filepart, extension = os.path.splitext(file_name)

    if re.match(r'\.h.*', extension, re.IGNORECASE) or re.match(r'\.c.*', extension, re.IGNORECASE):

        if os.path.exists(u('{0}{1}').format(u(filepart), u('.c'))) or os.path.exists(u('{0}{1}').format(u(filepart), u('.C'))):
            return 'C'

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


def standardize_language(language, plugin):
    """Maps a string to the equivalent Pygments language.

    Returns a tuple of (language_str, lexer_obj).
    """

    if not language:
        return None, None

    # standardize language for this plugin
    if plugin:
        plugin = plugin.split(' ')[-1].split('/')[0].split('-')[0]
        standardized = get_language_from_json(language, plugin)
        if standardized is not None:
            return standardized, get_lexer(standardized)

    # standardize language against default languages
    standardized = get_language_from_json(language, 'default')
    return standardized, get_lexer(standardized)


def get_lexer(language):
    """Return a Pygments Lexer object for the given language string."""

    if not language:
        return None

    lexer_cls = find_lexer_class(language)
    if lexer_cls:
        return lexer_cls()

    return None


def get_language_from_json(language, key):
    """Finds the given language in a json file."""

    file_name = os.path.join(
        os.path.dirname(__file__),
        'languages',
        '{0}.json').format(key.lower())

    try:
        with open(file_name, 'r', encoding='utf-8') as fh:
            languages = json.loads(fh.read())
            if languages.get(language.lower()):
                return languages[language.lower()]
    except:
        pass

    return None


def get_file_head(file_name):
    """Returns the first 512000 bytes of the file's contents."""

    text = None
    try:
        with open(file_name, 'r', encoding='utf-8') as fh:
            text = fh.read(512000)
    except:
        try:
            with open(file_name, 'r', encoding=sys.getfilesystemencoding()) as fh:
                text = fh.read(512000)  # pragma: nocover
        except:
            log.traceback(logging.DEBUG)
    return text


def custom_pygments_guess_lexer_for_filename(_fn, _text, **options):
    """Overwrite pygments.lexers.guess_lexer_for_filename to customize the
    priority of different lexers based on popularity of languages."""

    fn = basename(_fn)
    primary = {}
    matching_lexers = set()
    for lexer in _iter_lexerclasses():
        for filename in lexer.filenames:
            if _fn_matches(fn, filename):
                matching_lexers.add(lexer)
                primary[lexer] = True
        for filename in lexer.alias_filenames:
            if _fn_matches(fn, filename):
                matching_lexers.add(lexer)
                primary[lexer] = False
    if not matching_lexers:
        raise ClassNotFound('no lexer for filename %r found' % fn)
    if len(matching_lexers) == 1:
        return matching_lexers.pop()(**options)
    result = []
    for lexer in matching_lexers:
        rv = lexer.analyse_text(_text)
        if rv == 1.0:
            return lexer(**options)
        result.append((rv, customize_priority(lexer)))

    def type_sort(t):
        # sort by:
        # - analyse score
        # - is primary filename pattern?
        # - priority
        # - last resort: class name
        return (t[0], primary[t[1]], t[1].priority, t[1].__name__)
    result.sort(key=type_sort)

    return result[-1][1](**options)


CUSTOM_PRIORITIES = {
    'typescript': 0.11,
    'perl': 0.1,
    'perl6': 0.1,
    'f#': 0.1,
}
def customize_priority(lexer):
    """Return an integer priority for the given lexer object."""

    if lexer.name.lower() in CUSTOM_PRIORITIES:
        lexer.priority = CUSTOM_PRIORITIES[lexer.name.lower()]
    return lexer
