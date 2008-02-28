#@+leo-ver=4
#@+node:@file zenity_file_dialogs.py
#@<< docstring >>
#@+node:<< docstring >>

'''Replace the tk file dialogs on linux with external
calls to the zenity gtk dialog package.

This plugin is more a proof of concopt demo than
a useful tool.  The dialogs presented do not take
filters and starting folders can not be specified.

Despit this, some linux users might prefer it to the
tk dialogs.
'''
#@-node:<< docstring >>
#@nl

#@@language python
#@@tabwidth -4

__version__ = "0.1"
#@<< version history >>
#@+node:<< version history >>
#@@killcolor
#@+at
# 
# 0.1 plumloco: Initial version
#@-at
#@nonl
#@-node:<< version history >>
#@nl
#@<< imports >>
#@+node:<< imports >>
import leoGlobals as g
import leoPlugins

import os

trace = False

try:
    from subprocess import *
    ok = True
except:
    ok = False

if trace:
    if ok:
        print 'subprocess imported ok'
    else:
        g.trace('failed to import subprocess')


#@-node:<< imports >>
#@nl


#@+others
#@+node:testForZenity

def testForZenity():


    command = [ 'which', 'zenity']

    o = Popen(command, stdout=PIPE)
    o.wait()
    filename = o.communicate()[0].rstrip()

    ret = o.returncode

    if trace:
        g.trace('\n\texecutable', repr(filename))
        print '\n\treturncode', ret

    if trace and ret:
        g.trace('\n\tCan\'t find Zenity!')

    return not ret

#@-node:testForZenity
#@+node:init
def init ():
    global ok
	
    if g.unitTesting:
        return False

    if ok:
        ok = ok and testForZenity()
        # trace and g.trace('imported ok')
        trace and g.trace('zenity ok')
        leoPlugins.registerHandler('start2', onStart2)
        g.plugin_signon(__name__)
    else:
        g.trace('failed to load zenity')
    return ok
#@-node:init
#@+node:onStart2
def onStart2 (tag, keywords):

    """
    Replace tkfile open/save method with external calls to zenity.
    """
    trace and g.trace('zenity ok')

    g.funcToMethod(runOpenFileDialog,g.app.gui)
    g.funcToMethod(runSaveFileDialog,g.app.gui)
#@nonl
#@-node:onStart2
#@+node:callZenity
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
        print '\treturncode', ret

    if ret:
        trace and g.trace(g.choose(save,'save','open'), 'cancelled')
        return ''

    if multiple:
        return filename.split('|')

    return filename


#@-node:callZenity
#@+node:runOpenFileDialog
def runOpenFileDialog(title=None,filetypes=None,defaultextension=None,multiple=False):

    """Call zenity's open file(s) dialog."""

    trace and g.trace()

    initialdir = g.app.globalOpenDir or g.os_path_abspath(os.getcwd())

    return callZenity(title, multiple=multiple)

#@-node:runOpenFileDialog
#@+node:runSaveFileDialog
def runSaveFileDialog(initialfile=None,title=None,filetypes=None,defaultextension=None):

    """Call zenity's save file dialog."""

    trace and g.trace()

    initialdir=g.app.globalOpenDir or g.os_path_abspath(os.getcwd())

    return callZenity(title, save=True)


#@-node:runSaveFileDialog
#@-others

#@-node:@file zenity_file_dialogs.py
#@-leo
