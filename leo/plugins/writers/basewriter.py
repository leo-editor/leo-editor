#@+leo-ver=5-thin
#@+node:ekr.20140726091031.18143: * @file writers/basewriter.py
'''A module defining the base class for all writers in leo.plugins.writers.'''
class BaseWriter:
    '''The base writer class for all writers in leo.plugins.writers.'''

    def __init__(self,c):
        '''Ctor for leo.plugins.writers.BaseWriter.'''
        self.c = c
        self.at = c.atFileCommands

    def put(self,s):
        '''Write line s using at.os, taking special care of newlines.'''
        at = self.at
        at.os(s[:-1] if s.endswith('\n') else s)
        at.onl()
#@-leo
