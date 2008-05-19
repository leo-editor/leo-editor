# -*- coding: utf-8 -*-
#@+leo-ver=4-thin
#@+node:ekr.20080112171650:@thin leoGtkKeys.py
#@@first

'''Leo's Gtk Key handling module.'''

#@@language python
#@@tabwidth -4
#@@pagewidth 80

import leoKeys

class gtkKeyHandlerClass (leoKeys.keyHandlerClass):

    '''gtk overrides of base keyHandlerClass.'''

    #@    @+others
    #@+node:ekr.20080112145409.172:ctor
    def __init__(self,c,useGlobalKillbuffer=False,useGlobalRegisters=False):

        # g.trace('gtkKeyHandlerClass',c)

        # Init the base class.
        leoKeys.keyHandlerClass.__init__(self,c,useGlobalKillbuffer,useGlobalRegisters)
    #@-node:ekr.20080112145409.172:ctor
    #@-others
#@-node:ekr.20080112171650:@thin leoGtkKeys.py
#@-leo
