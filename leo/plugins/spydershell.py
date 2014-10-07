#@+leo-ver=5-thin
#@+node:ville.20090815203828.5235: * @file spydershell.py
''' Launches the spyder environment with access to Leo instance.
See http://packages.python.org/spyder/

Execute alt-x spyder-launch to start spyder. Execute alt-x spyder-update to pass
current c,p,g to spyder interactive session. spyder-update also shows the window
if it was closed before.

'''
# Written by VMV.
#@+<< imports >>
#@+node:ville.20090815203828.5238: ** << imports >>
import sys

import leo.core.leoGlobals as g

# Fail gracefully if the gui is not qt.
g.assertUi('qt')
#@-<< imports >>
#@+others
#@+node:ville.20090815203828.5239: ** init
def init ():
    '''Return True if the plugin has loaded successfully.'''
    return g.app.gui.guiName() == 'qt'    
#@+node:ville.20090815203828.5240: ** Leo commands
@g.command('spyder-launch')
def spyder_launch(event):
    """ Launch spyder """
    # Options
    from spyderlib import spyder
    data = spyder.get_options()

    # Create the main window
    try:
        # Version 1.x
        commands, intitle, message, options = data
        g.spyder = main = spyder.MainWindow(commands, intitle, message, options)
    except TypeError:
        # Version 2.x
        g.spyder = main = spyder.MainWindow(options=data)

    main.setup()
    g.spyderns = main.console.shell.interpreter.namespace
    spyder_update(event)
    main.show()

@g.command('spyder-light')
def spyder_light(event):
    """ Launch spyder in "light" mode """
    oldarg = sys.argv
    sys.argv = ['spyder', '--light']
    spyder_launch(event)
    sys.argv = oldarg


@g.command('spyder-update')
def spyder_update(event):
    """ Reset commander and position to current in pydee session 

    Also shows pydee window if it was closed earlier

    """    

    c = event['c']
    ns = g.spyderns
    ns['c'] = c
    ns['g'] = g
    ns['p'] = c.p
    g.spyder.show()
#@-others
#@@language python
#@@tabwidth -4
#@-leo
