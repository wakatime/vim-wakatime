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

if sys.version_info[0] == 2:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'packages', 'pygments2'))
else:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'packages', 'pygments3'))
from pygments.lexers import guess_lexer_for_filename


log = logging.getLogger(__name__)


# force file name extensions to be recognized as a certain language
EXTENSIONS = {
    'j2': 'HTML',
    'markdown': 'Markdown',
    'md': 'Markdown',
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
    if file_name:
        language = guess_language_from_extension(file_name.rsplit('.', 1)[-1])
        if language:
            return language
    lexer = None
    try:
        with open(file_name) as f:
            lexer = guess_lexer_for_filename(file_name, f.read(512000))
    except:
        pass
    if lexer:
        return translate_language(str(lexer.name))
    else:
        return None


def guess_language_from_extension(extension):
    if extension:
        if extension in EXTENSIONS:
            return EXTENSIONS[extension]
        if extension.lower() in EXTENSIONS:
            return mapping[EXTENSIONS.lower()]
    return None


def translate_language(language):
    if language in TRANSLATIONS:
        language = TRANSLATIONS[language]
    return language


def number_lines_in_file(file_name):
    lines = 0
    try:
        with open(file_name) as f:
            for line in f:
                lines += 1
    except IOError:
        return None
    return lines


def get_file_stats(file_name):
    stats = {
        'language': guess_language(file_name),
        'lines': number_lines_in_file(file_name),
    }
    return stats
