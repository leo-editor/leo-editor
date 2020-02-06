#@+leo-ver=5-thin
#@+node:ekr.20040419105219: * @file lineNumbers.py
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
import leo.core.leoGlobals as g
import leo.core.leoAtFile as leoAtFile

import re
#@-<< imports >>
__version__ = "0.3"
#@+<< version history >>
#@+node:ekr.20050105150253.1: ** << version history >>
#@@killcolor
#@+at
# 
# 0.1 Mark Ng
#     - Original code
# 0.2 EKR:
#     - Convert to new coding conventions.
# 0.3 EKR:
#     - Changed leoAtFile.newDerivedFile to leoAtFile.AtFile when overriding methods.
#       This is required because of changes in 4.3 to Leo's core code.
# 0.4 EKR:
#     - Used named sections to emphasize the dangerous nature of this code.
#@-<< version history >>

linere = re.compile("^#line 1 \".*\"$")

def init():
    '''Return True if the plugin has loaded successfully.'''
    ok = not g.app.unitTesting # Not safe for unit testing.  Changes core class.
    if ok:
        #@+<< override write methods >>
        #@+node:ekr.20040419105219.1: ** << override write methods >>
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
        #@+<< override read methods >>
        #@+node:ekr.20040419105219.2: ** << override read methods >>
        # readNormalLine = leoAtFile.AtFile.readNormalLine

        # def skipLineNumberDirective(self, s, i):

            # if linere.search(s):
                # return  # Skipt the line.
            # else:
                # readNormalLine(self,s,i)

        # g.funcToMethod(skipLineNumberDirective,
            # leoAtFile.AtFile,"readNormalLine")
        #@-<< override read methods >>
        g.plugin_signon(__name__)
    return ok
#@-leo
