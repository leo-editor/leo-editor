#@+leo-ver=5-thin
#@+node:ekr.20140726091031.18143: * @file ../plugins/writers/basewriter.py
"""A module defining the base class for all writers in leo.plugins.writers."""

from leo.core.leoCommands import Commands as Cmdr
from leo.core.leoNodes import Position

#@+others
#@+node:ekr.20231219152931.1: ** class  BaseWriter
class BaseWriter:
    """The base writer class for all writers in leo.plugins.writers."""

    def __init__(self, c: Cmdr) -> None:
        """Ctor for leo.plugins.writers.BaseWriter."""
        self.c = c
        self.at = c.atFileCommands
        self.at.outputList = []

    #@+others
    #@+node:ekr.20150626092123.1: *3* basewriter.put
    def put(self, s: str) -> None:
        """Write line s using at.os, taking special care of newlines."""
        at = self.at
        at.os(s[:-1] if s.endswith('\n') else s)
        at.onl()
    #@+node:ekr.20150626092140.1: *3* basewriter.put_node_sentinel
    def put_node_sentinel(self, p: Position, delim: str, delim2: str = '') -> None:
        """Put an @+node sentinel for node p."""
        at = self.at
        # Like at.nodeSentinelText.
        gnx = p.v.fileIndex
        level = p.level()
        if level > 2:
            s = "%s: *%s* %s" % (gnx, level, p.h)
        else:
            s = "%s: %s %s" % (gnx, '*' * level, p.h)
        # Like at.putSentinel.
        at.os('%s@+node:%s%s' % (delim, s, delim2))
        at.onl()
    #@+node:ekr.20230913032143.1: *3* basewriter.write
    def write(self, root: Position) -> None:
        raise NotImplementedError('must be overridden in subclasses')
    #@-others
#@-others

#@@language python
#@@tabwidth -4
#@-leo
