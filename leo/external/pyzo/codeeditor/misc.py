# -*- coding: utf-8 -*-
# Copyright (C) 2013, the codeeditor development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module misc

Defined ustr (Unicode string) class and the option property decorator.

"""

import sys
from .qt import QtGui, QtCore, QtWidgets  # noqa


# Set Python version and get some names
PYTHON_VERSION = sys.version_info[0]
if PYTHON_VERSION < 3:
    ustr = unicode  # noqa
    bstr = str
    from Queue import Queue, Empty
else:
    ustr = str
    bstr = bytes
    from queue import Queue, Empty



DEFAULT_OPTION_NAME = '_ce_default_value'
DEFAULT_OPTION_NONE = '_+_just some absurd value_+_'

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
    

class _CallbackEventHandler(QtCore.QObject):
    """ Helper class to provide the callLater function.
    """
    
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.queue = Queue()

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

    def postEventWithCallback(self, callback, *args):
        self.queue.put((callback, args))
        QtWidgets.qApp.postEvent(self, QtCore.QEvent(QtCore.QEvent.User))


def callLater(callback, *args):
    """ callLater(callback, *args)
    
    Post a callback to be called in the main thread.
    
    """
    _callbackEventHandler.postEventWithCallback(callback, *args)
    
# Create callback event handler instance and insert function in Pyzo namespace
_callbackEventHandler = _CallbackEventHandler()
