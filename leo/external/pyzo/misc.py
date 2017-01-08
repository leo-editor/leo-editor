#@+leo-ver=5-thin
#@+node:ekr.20170108050440.1: * @file ../external/pyzo/misc.py
# -*- coding: utf-8 -*-
#@+<< pyzo copyright >>
#@+node:ekr.20170108171929.1: ** << pyzo copyright >>
# Copyright (C) 2016, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.
#@-<< pyzo copyright >>
#@+<< misc.py imports >>
#@+node:ekr.20170108050440.2: ** << misc.py imports >>
# import sys
import leo.core.leoGlobals as g
ustr = g.ustr
bstr = bytes if g.isPython3 else str
# from .qt import QtGui, QtCore, QtWidgets
from leo.core.leoQt import QtCore, QtWidgets # QtGui, 
if g.isPython3:
    from queue import Queue, Empty
else:
    from Queue import Queue, Empty
###
# # Set Python version and get some names
# PYTHON_VERSION = sys.version_info[0]
# if PYTHON_VERSION < 3:
    # ustr = unicode
    # bstr = str
    # from Queue import Queue, Empty
# else:
    # ustr = str
    # bstr = bytes
    # from queue import Queue, Empty
#@-<< misc.py imports >>
DEFAULT_OPTION_NAME = '_ce_default_value'
DEFAULT_OPTION_NONE = '_+_just some absurd value_+_'
#@+others
#@+node:ekr.20170108050440.3: ** ce_option
def ce_option(arg1):
    """ Decorator for properties of the code editor. 
    
    It should be used on the setter function, with its default value
    as an argument. The default value is then  stored on the function
    object. 
    
    At the end of the initialization, the base codeeditor class will 
    check all members and (by using the default-value-attribute as a
    flag) select the ones that are options. These are then set to
    their default values.
    
    Similarly this information is used by the setOptions method to
    know which members are "options".
    
    """
    
    # If the decorator is used without arguments, arg1 is the function
    # being decorated. If arguments are used, arg1 is the argument, and
    # we should return a callable that is then used as a decorator.
    
    # Create decorator function.
    def decorator_fun(f):
        f.__dict__[DEFAULT_OPTION_NAME] = default
        return f
    
    # Handle
    default = DEFAULT_OPTION_NONE
    if hasattr(arg1, '__call__'):
        return decorator_fun(arg1)
    else:
        default = arg1
        return decorator_fun
#@+node:ekr.20170108050440.4: ** class _CallbackEventHandler
class _CallbackEventHandler(QtCore.QObject):
    """ Helper class to provide the callLater function. 
    """
    
    #@+others
    #@+node:ekr.20170108050440.5: *3* __init__
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.queue = Queue()
    #@+node:ekr.20170108050440.6: *3* customEvent
    def customEvent(self, event):
        while True:
            try:
                callback, args = self.queue.get_nowait()
            except Empty:
                break
            try:
                callback(*args)
            except Exception as why:
                print('callback failed: {}:\n{}'.format(callback, why))
    #@+node:ekr.20170108050440.7: *3* postEventWithCallback
    def postEventWithCallback(self, callback, *args):
        self.queue.put((callback, args))
        QtWidgets.qApp.postEvent(self, QtCore.QEvent(QtCore.QEvent.User))
    #@-others
#@+node:ekr.20170108050440.8: ** callLater
def callLater(callback, *args):
    """ callLater(callback, *args)
    
    Post a callback to be called in the main thread. 
    
    """
    _callbackEventHandler.postEventWithCallback(callback, *args)
    
# Create callback event handler instance and insert function in Pyzo namespace
_callbackEventHandler = _CallbackEventHandler()   
#@-others
#@@language python
#@@tabwidth -4
#@-leo
