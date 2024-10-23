#@+leo-ver=5-thin
#@+node:ekr.20241022090855.1: * @file leoJupytext.py
"""
Support for pairing .ipynb and .py files with jupytext.

https://github.com/mwouts/jupytext
"""

#@+<< leoJupytext: imports and annotations >>
#@+node:ekr.20241022093347.1: ** << leoJupytext: imports and annotations >>
from __future__ import annotations
from typing import Dict, TYPE_CHECKING

try:
    import jupytext  # pylint: disable=unused-import
    has_jupytext = True
except Exception:
    has_jupytext = False
    print('Can not import jupytext')
    print('pip install jupytext')

from leo.core import leoGlobals as g  # pylint: disable=unused-import

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position
#@-<< leoJupytext: imports and annotations >>

#@+others
#@+node:ekr.20241022093215.1: ** class JupytextManager
class JupytextManager:

    def __init__(self) -> None:

        # Keys are full paths to .ipynb files.
        self.ipynb_dict: Dict[str, str] = {}

    #@+others
    #@+node:ekr.20241023073354.1: *3* jtm.update
    def update(self, c: Cmdr, p: Position, path: str) -> None:
        """
        Update the @jupytext node.
        """
        g.trace(p.h)

        # if path.endswith('.ipynb'):
            # old_c = c.p
            # c.selectPosition(p)
            # c.refreshFromDisk()
            # c.redraw(old_c)
        # elif path.endwith('.py'):
            # g.trace('To do. Update:', repr(path))
        # else:
            # g.trace('Can not happen: wrong file type:', repr(path))
    #@-others
#@-others

#@-leo
