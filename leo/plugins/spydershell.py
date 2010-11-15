#@+leo-ver=5-thin
#@+node:ville.20090815203828.5235: * @file spydershell.py
#@+<< docstring >>
#@+node:ville.20090815203828.5236: ** << docstring >>
''' Launches the spyder environment with access to Leo instance.
See http://packages.python.org/spyder/

Execute alt-x spyder-launch to start spyder. Execute alt-x spyder-update to pass
current c,p,g to spyder interactive session. spyder-update also shows the window
if it was closed before.

'''
#@-<< docstring >>

__version__ = '0.0'
#@+<< version history >>
#@+node:ville.20090815203828.5237: ** << version history >>
#@@killcolor
#@+at
# 
# 0.1 VMV First version
# 
# 0.2 VMV name changed to "spyder' (was "pydee")
#@-<< version history >>

#@+<< imports >>
#@+node:ville.20090815203828.5238: ** << imports >>
import sys

import leo.core.leoGlobals as g

g.assertUi('qt')
#@-<< imports >>

#@+others
#@+node:ville.20090815203828.5239: ** init
def init ():
    ok = g.app.gui.guiName() == 'qt'    
    return ok

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
#@-leo
