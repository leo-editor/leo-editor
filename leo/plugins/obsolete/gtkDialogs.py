#@+leo-ver=4-thin
#@+node:bob.20080109185406.1:@thin gtkDialogs.py
#@@language python
#@@tabwidth -4
#@<< docstring >>
#@+node:bob.20071220105852:<< docstring >>
"""Replace Tk dialogs with Gtk dialogs.

At the moment this plugin only replaces Tk's file dialogs, but
other dialogs may be replaced in future.

This plugin consists of two files, this one and runGtkDialogs.py.txt,
and obviously requires gtk2 to be availiable on your system.

runGtkDialogs.py.txt has a .txt extension so it can live
in the plugins folder without being mistaken for a plugin.
This python script is called to show the gtk dialogs.

@settings
=========

This plugin assumes that the command to invoke python is 'python'
but this may be changed by placing:

  @string gtkdialogs_pythoncommand = your_python_command

in the @settings tree of myLeoSettings.leo.


"""

#@-node:bob.20071220105852:<< docstring >>
#@nl
#@<< version history >>
#@+node:bob.20071220123624:<< version history >>
#@@killcolor
#@+at
# 
# 1.1 plumloco: Initial version
# 1.2 plumloco: Changed root node to fit in leoPlugins
# 1.3 plumloco: check for c is None in hook handler
#@-at
#@nonl
#@-node:bob.20071220123624:<< version history >>
#@nl

#@<<imports>>
#@+node:bob.20071220110146:<< imports >>
import leoGlobals as g
import leoPlugins

import os
import pickle

try:
    from subprocess import *

    ok = True
except:
    ok = False

import re



#@-node:bob.20071220110146:<< imports >>
#@nl

__revision__ = re.sub(r'^\D+([\d\.]+)\D+$', r'\1', "$Revision: 1.3 $")

__version__ = '0.%s'% __revision__

__plugin_name__ = "GTK Dialogs"

__author__ = "plumloco@hcoop.net"




#@+others
#@+node:bob.20071220111856:init
def init ():

    if g.unitTesting:
        return False

    if ok:
        leoPlugins.registerHandler('start2', onStart2)
        g.plugin_signon(__name__)


    return ok
#@-node:bob.20071220111856:init
#@+node:bob.20071220110328:onStart2
def onStart2 (tag, keywords):

    """
    Replace tkfile open/save method with external calls to runGtkDialogs.
    """

    global oldopen, oldsave



    c = keywords.get('c')
    if not c:
        return

    global pythoncommand


    oldopen = g.app.gui.runOpenFileDialog
    oldsave = g.app.gui.runSaveFileDialog

    g.funcToMethod(runOpenFileDialog,g.app.gui)
    g.funcToMethod(runSaveFileDialog,g.app.gui)

    pythoncommand = c.config.getString('gtkdialogs_pythoncommand') 

#@-node:bob.20071220110328:onStart2
#@+node:bob.20071220094231.10:callGtkDialogs
def callGtkDialogs(data, path='runGtkDialogs.py.txt'):


    data = pickle.dumps(data)

    path = g.os_path_abspath(g.os_path_join(g.app.loadDir, '..', 'plugins', path))

    command = [ pythoncommand or 'python', path, data ] 


    try:
        o = Popen(command, stdout=PIPE)

        o.wait()
        ok = True
    except:

        ok = False

    if not ok:
        g.es('error running gtk file chooser\nreverting to tk dialogs', color='red')
        return False, None

    data = o.communicate()[0].rstrip()

    ret = o.returncode


    if  ret or not data:
        return True, None

    return True, pickle.loads(data)



#@-node:bob.20071220094231.10:callGtkDialogs
#@+node:bob.20071220100337:runOpenFileDialog
def runOpenFileDialog(title=None,filetypes=None,defaultextension=None,multiple=False):

    """Call runGtkDialogs open file(s) dialog."""


    initialdir = g.app.globalOpenDir or g.os_path_abspath(os.getcwd())

    data = {
        'dialog': 'filechooser',
        'title': title,
        'initialdir': initialdir,
        'filetypes': filetypes,
        'defaultextension': defaultextension,
        'multiple': multiple,
        'action': 'open',
    }


    ok, data = callGtkDialogs(data)

    if not ok:
        return oldopen(title=title,filetypes=filetypes,defaultextension=defaultextension,multiple=multiple)


    if data is None:
        return ''
    return data['result']

#@-node:bob.20071220100337:runOpenFileDialog
#@+node:bob.20071220100831:runSaveFileDialog
def runSaveFileDialog(initialfile=None,title=None,filetypes=None,defaultextension=None):

    """Call runGtkDialogs save file dialog."""


    initialdir=g.app.globalOpenDir or g.os_path_abspath(os.getcwd())


    data = {
        'dialog': 'filechooser',
        'title': title,
        'initialdir': initialdir,
        'filetypes': filetypes,
        'defaultextension': defaultextension,
        'action': 'save'
    }

    ok, data = callGtkDialogs(data)
    if not ok:
        return oldsave(initialfile=initialfile,title=title,filetypes=none,defaultextension=none)


    if data is None:
        return ''

    return data['result']





#@-node:bob.20071220100831:runSaveFileDialog
#@-others
#@nonl
#@-node:bob.20080109185406.1:@thin gtkDialogs.py
#@-leo
