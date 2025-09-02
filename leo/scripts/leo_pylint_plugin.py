#@+leo-ver=5-thin
#@+node:ekr.20250901071045.1: * @file ../scripts/leo_pylint_plugin.py
from typing import TYPE_CHECKING
from leo.core import leoGlobals as g

import astroid
from pylint.lint import PyLinter

def register(linter: PyLinter) -> None:
    print('Plugin active!', g.shortFileName(__file__))
#@-leo
