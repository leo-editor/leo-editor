#@+leo-ver=5-thin
#@+node:ekr.20250901071045.1: * @file ../scripts/leo_pylint_plugin.py
#@@language python

#@+<< leo_pylint_plugin: imports >>
#@+node:ekr.20250902071947.1: ** << leo_pylint_plugin: imports >>
from typing import Optional  # TYPE_CHECKING

from leo.core import leoGlobals as g

from astroid import nodes
from pylint.checkers import BaseChecker
from pylint.lint import PyLinter
#@-<< leo_pylint_plugin: imports >>

class Leo_Checker(BaseChecker):
    name = 'leo-checker'
    #@+<< messages and options >>
    #@+node:ekr.20250902070853.1: ** << messages and options >>
    msgs = {  # Required.
        "W0001": (
            "message",
            "dummy-leo-option",
            "description",
        ),
    }

    # options = ()
    #@-<< messages and options >>

    def get_full_documentation(self, *args, **kwargs) -> str:
        return 'leo-checker: help pylint understand c, g and p'

    def visit_functiondef(self, node: nodes.FunctionDef) -> None:
        print(node)
        g.printObj(node.args.args, tag=node.name)

def register(linter: PyLinter) -> None:
    linter.register_checker(Leo_Checker(linter))
#@-leo
