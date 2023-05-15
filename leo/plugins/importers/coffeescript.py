#@+leo-ver=5-thin
#@+node:ekr.20160505094722.1: * @file ../plugins/importers/coffeescript.py
"""The @auto importer for coffeescript."""
from __future__ import annotations
import re
from typing import Tuple, TYPE_CHECKING
from leo.plugins.importers.python import Python_Importer
if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position
#@+others
#@+node:ekr.20160505094722.2: ** class Coffeescript_Importer(Python_Importer)
class Coffeescript_Importer(Python_Importer):

    block_patterns: Tuple = (
        ('class', re.compile(r'^\s*class\s+([\w]+)')),
        ('def', re.compile(r'^\s*(.+?):.*?->')),
        ('def', re.compile(r'^\s*(.+?)=.*?->')),
    )

    def __init__(self, c: Cmdr) -> None:
        """Ctor for CoffeeScriptScanner class."""
        super().__init__(c, language='coffeescript')
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for coffeescript."""
    Coffeescript_Importer(c).import_from_string(parent, s)

importer_dict = {
    'extensions': ['.coffee',],
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo
