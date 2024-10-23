#@+leo-ver=5-thin
#@+node:ekr.20241022090855.1: * @file leoJupytext.py
"""
Support for pairing .ipynb and .py files with jupytext.

https://github.com/mwouts/jupytext
"""

#@+<< leoJupytext: imports and annotations >>
#@+node:ekr.20241022093347.1: ** << leoJupytext: imports and annotations >>
from __future__ import annotations
import os
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

    #@+others
    #@+node:ekr.20241023152818.1: *3* jtm.full_path (*** test)
    def full_path(self, c: Cmdr, p: Position) -> str:
        """
        Return the full path in effect for the @jupytext node at p,
        converting x.py or x to x.ipynb first.
        """
        if not p.h.startswith('@jupytext'):
            g.trace(f"Can not happen: {p.h!r}")
            return ''
        path = p.h[len('@jupytext') :].strip()
        if path.endswith('.ipynb'):
            return path
        if path.endswith('.py'):
            ipynb_path = path[:-3] + '.ipynb'
            return ipynb_path
        return path + '.ipynb'
    #@+node:ekr.20241023155136.1: *3* jtm.read (*** test)
    def read(self, c: Cmdr, p: Position) -> str:  # pragma: no cover
        """
        Return jupytext's conversion of the .ipynb text given by the @jupytext
        node at p.
        """
        if not has_jupytext:
            self.warn_no_jupytext()
            return  ''
        path = self.full_path(c, p)
        g.trace('jtm.exists', os.path.exists(path), path)  ###
        if not os.path.exists(path):
            g.trace('Not found', p.h, repr(path))
            return ''
        # Use jupytext.reads to convert the .ipynb file to a string
        # representing the jupytext .py file.
        return ''
    #@+node:ekr.20241023073354.1: *3* jtm.update (*** test)
    def update(self, c: Cmdr, p: Position, path: str) -> None:
        """
        Update the @jupytext node at p.
        """
        contents = self.read(c, p)
        if not contents:
            return
        g.printObj(g.splitLines(contents), tag=f"jtm.update: contents of {p.h}")
        # if contents:
            # p.b = contents
    #@+node:ekr.20241023161034.1: *3* jtm.warn_no_jupytext
    warning_given = False

    def warn_no_jupytext(self) -> None:
        """Warn (once) that jupytext is not available"""
        if not self.warning_given:
            self.warning_given = True
            print('')
            g.es_print('can not import `jupytext`', color='red')
            g.es_print('`pip install jupytext`', color='blue')
            print('')
    #@+node:ekr.20241023155519.1: *3* jtm.write (*** test)
    def write(self, c: Cmdr, p: Position) -> None:
        g.trace('not ready:', p.h)  ###
    #@-others
#@-others

#@-leo
