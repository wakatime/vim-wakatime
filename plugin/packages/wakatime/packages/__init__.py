import os
import sys

from ..compat import is_py2

if is_py2:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'py2'))
else:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'py3'))

import tzlocal
from pygments.lexers import get_lexer_by_name, guess_lexer_for_filename
from pygments.modeline import get_filetype_from_buffer
from pygments.util import ClassNotFound
