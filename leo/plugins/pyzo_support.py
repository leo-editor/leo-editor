# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20190410171646.1: * @file pyzo_support.py
#@@first
'''
pyzo_support.py:
- Support adding pyzo features within Leo.
- Support embedding Leo into pyzo.
'''
#@+<< copyright >>
#@+node:ekr.20190412042616.1: ** << copyright >>
#@+at
# This file uses code from pyzo. Here is the pyzo copyright notice:
# 
# Copyright (C) 2013-2018, the Pyzo development team
# 
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.
# 
# Yoton is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.
#@-<< copyright >>
import leo.core.leoGlobals as g
import leo.core.leoBridge as leoBridge
#@+others
#@+node:ekr.20190410171905.1: ** init (pyzo_support.py)
def init():
    print('pyzo_support.py is not a real plugin')
    return False
#@+node:ekr.20190418161712.1: ** class GlobalPyzoController
class GlobalPyzoController:
    '''
    A class representing the singleton running instance of pyzo.
    
    Instantiated in the top-level init() function.
    '''

    #@+others
    #@+node:ekr.20190417141817.1: *3* gpc.load_pyzo (to be deleted)
    def load_pyzo(self):
        '''Go through pyzo's *entire* startup logic.
        '''
        import sys
        sys.argv = []
            # Avoid trying to load extra files.
        try:
            import pyzo
        except ImportError:
            g.es_print('can not import pyzo')
        pyzo.start()
        print('\n=====g.app.gui.main_window', g.app.gui.main_window)
    #@+node:ekr.20190803175344.1: *3* gpc.patch_pyzo
    def patch_pyzo(self):
        '''
        Called at the end of pyzo.start to embed Leo into pyzo.
        '''
        import pyzo
        g.trace(pyzo)
    #@-others
#@+node:ekr.20190805081742.1: ** class PyzoInterface
class PyzoInterface:
    '''
    A class representing the singleton running instance of pyzo.
    
    Instantiated in the top-level init() function.
    '''

    #@+others
    #@+node:ekr.20190805081451.1: *3* pyzo_x.patch_pyzo
    def patch_pyzo(self):
        '''
        Called at the end of pyzo.start() to embed Leo into pyzo.
        '''
        import pyzo
        if not pyzo:
            g.es_print('Can not import pyzo')
            return
        g.trace() ; print('')
        bridge = leoBridge.controller(
            gui='nullGui',
            loadPlugins=False, 
                # Essential: some plugins import Qt, which causes this message:
                    # Qt WebEngine seems to be initialized from a plugin.
                    # Please set Qt::AA_ShareOpenGLContexts using QCoreApplication::setAttribute
                    # before constructing QGuiApplication.
            readSettings=True, # Debatable.
            verbose=False,
        )
        if bridge.isOpen():
            self.g = bridge.globals()
            # c = bridge.openLeoFile(path)
    #@-others
#@-others
#@-leo
