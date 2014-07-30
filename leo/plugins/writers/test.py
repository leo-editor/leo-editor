#@+leo-ver=5-thin
#@+node:ekr.20140729162415.18090: * @file writers/test.py
'''The @auto writer for .xyzzy files and @auto-test nodes.'''
import leo.core.leoGlobals as g
import leo.plugins.writers.basewriter as basewriter
trace = False and not g.unitTesting
tag = '(TestWriter)'
if trace:
    print('%s importing writers/test.py' % ('='*20))
class TestWriter(basewriter.BaseWriter):
    def __init__(self,c):
        g.trace(tag)
        basewriter.BaseWriter.__init__(self,c)
        assert self.c
    def write (self,root):
        g.trace(tag,root.h)
        return True

writer_dict = {
    '@auto': ['@auto-test',],
    'class': TestWriter,
    'extensions': ['.xyzzy',],
}
#@-leo
