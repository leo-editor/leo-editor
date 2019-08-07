# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20190410171646.1: * @file pyzo_support.py
#@@first
'''
pyzo_support.py: Will probably be deleted.
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
assert g
#@+others
#@+node:ekr.20190410171905.1: ** init (pyzo_support.py)
def init():
    print('pyzo_support.py is not a real plugin')
    return False
#@+node:ekr.20190418161712.1: ** class PyzoInterface
class PyzoInterface:
    '''
    A class representing the singleton running instance of pyzo.
    
    Instantiated in the top-level init() function.
    '''

    #@+others
    #@+node:ekr.20190803175344.1: *3* pyzo_x.patch_pyzo
    def patch_pyzo(self):
        '''
        Called at the end of pyzo.start to embed Leo into pyzo.
        '''
    #@-others
#@-others
#@-leo
