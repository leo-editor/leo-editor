#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18152: * @file ../plugins/importers/typescript.py
"""The @auto importer for TypeScript."""
from __future__ import annotations
import re
from typing import TYPE_CHECKING
# from leo.plugins.importers.base_importer import Importer
from leo.plugins.importers.javascript import JS_Importer

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position

#@+others
#@+node:ekr.20161118093751.1: ** class TS_Importer(JS_Importer)
class TS_Importer(JS_Importer):

    language = 'typescript'

    #@+<< define non-function patterns >>
    #@+node:ekr.20200817090227.1: *3* << define non-function patterns >>
    non_function_patterns = (
        re.compile(r'catch\s*\(.*\)'),
    )
    #@-<< define non-function patterns >>
    #@+<< define function patterns >>
    #@+node:ekr.20180523172655.1: *3* << define function patterns >>
    kinds = r'(async|public|private|static)'

    # The pattern table. Order matters!
    function_patterns = (
        (1, re.compile(r'(interface\s+\w+)')),  # interface name
        (1, re.compile(r'(class\s+\w+)')),  # class name
        (1, re.compile(r'export\s+(class\s+\w+)')),  # export class name
        (1, re.compile(r'export\s+enum\s+(\w+)')),  # function name
        (1, re.compile(r'export\s+const\s+enum\s+(\w+)')),  # function name
        (1, re.compile(r'export\s+function\s+(\w+)')),  # function name
        (1, re.compile(r'export\s+interface\s+(\w+)')),  # interface name
        (1, re.compile(r'function\s+(\w+)')),  # function name
        (1, re.compile(r'(constructor).*{')),  # constructor ... {
        # kind function name
        (2, re.compile(r'%s\s*function\s+(\w+)' % kinds)),
        # kind kind function name
        (3, re.compile(r'%s\s+%s\s+function\s+(\w+)' % (kinds, kinds))),
        # Bare functions last...
        # kind kind name (...) {
        (3, re.compile(r'%s\s+%s\s+(\w+)\s*\(.*\).*{' % (kinds, kinds))),
        # name (...) {
        (2, re.compile(r'%s\s+(\w+)\s*\(.*\).*{' % kinds)),
        # #1619: Don't allow completely bare functions.
        # (1,  re.compile(r'(\w+)\s*\(.*\).*{')),
            # name (...) {
    )
    #@-<< define function patterns >>
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for typescript."""
    TS_Importer(c).import_from_string(parent, s)

importer_dict = {
    'extensions': ['.ts',],
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo
