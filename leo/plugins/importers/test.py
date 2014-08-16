#@+leo-ver=5-thin
#@+node:ekr.20140729094250.19182: * @file importers/test.py
'''The @auto importer for .xyzzy files and @auto-test nodes.'''
import leo.core.leoGlobals as g
import leo.plugins.importers.basescanner as basescanner
trace = False and not g.unitTesting
tag = '(TestScanner)'
if trace:
    print('%s importing importers/test.py' % ('='*20))
class TestScanner(basescanner.BaseScanner):
    def __init__(self,importCommands,atAuto):
        if trace: g.trace(tag)
        basescanner.BaseScanner.__init__(self,importCommands,atAuto=atAuto,language='test')
    def run(self,s,parent,parse_body=False,prepass=False):
        if trace: g.trace(tag)
        return True
    def scan (self,s,parent,parse_body=False):
        if trace: g.trace(tag)
        return True

importer_dict = {
    '@auto': ['@auto-test',],
    'class': TestScanner,
    'extensions': ['.xyzzy',],
}
#@-leo
