# -*- coding: utf-8 -*-
#@+leo-ver=4-thin
#@+node:ekr.20071001081358:@thin leoSwingUtils.py
#@@first

'''Utility class and functions for Leo's swing gui.'''

#@@language python
#@@tabwidth -4
#@@pagewidth 80

#@<< imports >>
#@+node:ekr.20071001081358.1:<< imports >>
import leoGlobals as g

# import javax.swing as swing
# import java.awt as awt
import java.lang

# import os
# import string
# import sys
#@-node:ekr.20071001081358.1:<< imports >>
#@nl

#@+others
#@+node:ekr.20070930184746.373:class GCEveryOneMinute
class GCEveryOneMinute(java.lang.Thread):

    def __init__ (self):
        java.lang.Thread.__init__(self)

    def run (self):
        while 1:
            java.lang.System.gc()
            self.sleep(60000)
#@-node:ekr.20070930184746.373:class GCEveryOneMinute
#@-others
#@nonl
#@-node:ekr.20071001081358:@thin leoSwingUtils.py
#@-leo
