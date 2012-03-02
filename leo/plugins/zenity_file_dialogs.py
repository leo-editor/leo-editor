#@+leo-ver=5-thin
#@+node:ekr.20101110095202.5882: * @file zenity_file_dialogs.py
#@+<< docstring >>
#@+node:ekr.20101112195628.5435: ** << docstring >>
''' Replaces the tk file dialogs on Linux with external
calls to the zenity gtk dialog package.

This plugin is more a proof of concept demo than
a useful tool.  The dialogs presented do not take
filters and starting folders can not be specified.

Despite this, some Linux users might prefer it to the
tk dialogs.

'''
#@-<< docstring >>

#@@language python
#@@tabwidth -4

__version__ = "0.1"

ok = None

#@+<< imports >>
#@+node:ekr.20101110095557.5884: ** << imports >>
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

import os

trace = False

from subprocess import *
#@-<< imports >>

#@+others
#@+node:ekr.20101110095557.5886: ** testForZenity
def testForZenity():

    command = [ 'which', 'zenity']

    o = Popen(command, stdout=PIPE)
    o.wait()
    filename = o.communicate()[0].rstrip()

    ret = o.returncode

    if trace:
        g.trace('\n\texecutable', repr(filename))
        print('\n\treturncode', ret)

    if trace and ret:
        g.trace('\n\tCan\'t find Zenity!')

    return not ret
#@+node:ekr.20101110095557.5888: ** init
def init ():
    
    if g.unitTesting:
        return False

    ok = testForZenity()
    if ok:
        # g.trace('zenity ok')
        leoPlugins.registerHandler('start2', onStart2)
        g.plugin_signon(__name__)
    else:
        g.trace('failed to load zenity')
    return ok
#@+node:ekr.20101110095557.5890: ** onStart2
def onStart2 (tag, keywords):

    """
    Replace tkfile open/save method with external calls to zenity.
    """
    trace and g.trace('zenity ok')

    g.funcToMethod(runOpenFileDialog,g.app.gui)
    g.funcToMethod(runSaveFileDialog,g.app.gui)
#@+node:ekr.20101110095557.5892: ** callZenity
def callZenity(title, multiple=False, save=False, test=False):

    command = [ 'zenity', '--file-selection', '--title=%s'%title]

    if save:
        command.append('--save')

    if multiple:
        command.append('--multiple')


    o = Popen(command, stdout=PIPE)
    o.wait()
    filename = o.communicate()[0].rstrip()

    ret = o.returncode

    if trace:
        g.trace('\n\tfiles', repr(filename))
        print('\treturncode', ret)

    if ret:
        trace and g.trace(g.choose(save,'save','open'), 'cancelled')
        return ''

    if multiple:
        return filename.split('|')

    return filename
#@+node:ekr.20101110095557.5894: ** runOpenFileDialog
def runOpenFileDialog(title=None,filetypes=None,defaultextension=None,multiple=False):

    """Call zenity's open file(s) dialog."""

    trace and g.trace()

    initialdir = g.app.globalOpenDir or g.os_path_abspath(os.getcwd())

    return callZenity(title, multiple=multiple)
#@+node:ekr.20101110095557.5896: ** runSaveFileDialog
def runSaveFileDialog(initialfile=None,title=None,filetypes=None,defaultextension=None):

    """Call zenity's save file dialog."""

    trace and g.trace()

    initialdir=g.app.globalOpenDir or g.os_path_abspath(os.getcwd())

    return callZenity(title, save=True)
#@-others
#@-leo
