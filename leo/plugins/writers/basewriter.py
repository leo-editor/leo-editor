#@+leo-ver=5-thin
#@+node:ekr.20140726091031.18143: * @file writers/basewriter.py
'''A module defining the base class for all writers in leo.plugins.writers.'''

class BaseWriter:
    '''The base writer class for all writers in leo.plugins.writers.'''

    def __init__(self, c):
        '''Ctor for leo.plugins.writers.BaseWriter.'''
        self.c = c
        self.at = c.atFileCommands

    #@+others
    #@+node:ekr.20150626092123.1: ** basewriter.put
    def put(self, s):
        '''Write line s using at.os, taking special care of newlines.'''
        at = self.at
        at.os(s[: -1] if s.endswith('\n') else s)
        at.onl()
    #@+node:ekr.20150626092140.1: ** basewriter.put_node_sentinel
    def put_node_sentinel(self, p, delim, delim2=''):
        '''Put an @+node sentinel for node p.'''
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
    #@+node:ekr.20161125140611.1: ** basewriter.split_lines
    def split_lines(self, s):
        '''Exactly the same as g.splitLines(s).'''
        return s.splitlines(True) if s else []
            # This is a Python string function!
    #@-others

#@@language python
#@@tabwidth -4
#@-leo
