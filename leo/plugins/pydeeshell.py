#@+leo-ver=4-thin
#@+node:ville.20090801181915.5278:@thin pydeeshell.py
#@<< docstring >>
#@+node:ville.20090801181915.5279:<< docstring >>
''' Launch pydee environment with access to Leo instance

http://code.google.com/p/pydee/

Usage:

Execute alt-x pydee-launch to start pydee

Execute alt-x pydee-update to pass current c,p,g to pydee
interactive session. pydee-update also shows the window
if it was closed before.

'''
#@-node:ville.20090801181915.5279:<< docstring >>
#@nl

__version__ = '0.0'
#@<< version history >>
#@+node:ville.20090801181915.5280:<< version history >>
#@@killcolor
#@+at
# 
# 0.1 VMV First version
#@-at
#@-node:ville.20090801181915.5280:<< version history >>
#@nl

#@<< imports >>
#@+node:ville.20090801181915.5281:<< imports >>
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

# Whatever other imports your plugins uses.
#@nonl
#@-node:ville.20090801181915.5281:<< imports >>
#@nl

#@+others
#@+node:ville.20090801181915.5282:init
def init ():
    ok = g.app.gui.guiName() == 'qt'    
    return ok

#@-node:ville.20090801181915.5282:init
#@+node:ville.20090801181915.5284:Leo commands
@g.command('pydee-launch')
def pydee_launch(event):
    """ Launch pydee """
    # Options
    from pydeelib import pydee
    commands, intitle, message, options = pydee.get_options()

    # Main window
    g.pydee = main = pydee.MainWindow(commands, intitle, message, options)
    main.setup()
    g.pydeens = main.console.shell.interpreter.namespace
    pydee_update(event)
    main.show()

@g.command('pydee-update')
def pydee_update(event):
    """ Reset commander and position to current in pydee session 

    Also shows pydee window if it was closed earlier

    """    

    c = event['c']
    ns = g.pydeens
    ns['c'] = c
    ns['g'] = g
    ns['p'] = c.p
    g.pydee.show()
#@-node:ville.20090801181915.5284:Leo commands
#@-others
#@nonl
#@-node:ville.20090801181915.5278:@thin pydeeshell.py
#@-leo
