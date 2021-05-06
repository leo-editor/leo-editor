#@+leo-ver=5-thin
#@+node:ekr.20040419105219: * @file ../plugins/lineNumbers.py
#@+<< docstring >>
#@+node:ekr.20101112180523.5423: ** << docstring >>
''' Adds #line directives in perl and perlpod programs.

Over-rides two methods in leoAtFile.py to write #line directives after node
sentinels. This allows compilers to give locations of errors in relation to the
node name rather than the filename. Currently supports only perl and perlpod.
'''
#@-<< docstring >>

# Use and distribute under the same terms as Leo.
# Original code by Mark Ng <markn@cs.mu.oz.au>

#@+<< imports >>
#@+node:ekr.20050105150253: ** << imports >>
import re
from leo.core import leoGlobals as g
from leo.core import leoAtFile
#@-<< imports >>

linere = re.compile("^#line 1 \".*\"$")

def init():
    '''Return True if the plugin has loaded successfully.'''
    ok = not g.app.unitTesting # Not safe for unit testing.  Changes core class.
    if ok:
        #@+<< override write methods >>
        #@+node:ekr.20040419105219.1: ** << override write methods >> (lineNumbers.py)
        oldOpenNodeSentinel = leoAtFile.AtFile.putOpenNodeSentinel

        def putLineNumberDirective(self,p,inAtAll=False):

            oldOpenNodeSentinel(self,p,inAtAll)

            if self.language in ("perl","perlpod"):
                line = 'line 1 "node:%s (%s)"' % (
                    self.nodeSentinelText(p),self.shortFileName)
                self.putSentinel(line)

        g.funcToMethod(putLineNumberDirective,
            leoAtFile.AtFile,"putOpenNodeSentinel")
        #@-<< override write methods >>
        g.plugin_signon(__name__)
    return ok
#@-leo
