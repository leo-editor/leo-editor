#@+leo-ver=5-thin
#@+node:edream.110203113231.724: * @thin mod_autosave.py
#@+<< docstring >>
#@+node:ekr.20060108123253: ** << docstring >>
"""Autosave the Leo document every so often.

The time between saves is given in seconds in autosave.ini."""
#@-<< docstring >>

#@@language python
#@@tabwidth -4

#@+<< imports >>
#@+node:ekr.20060108123141: ** << imports >>
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

if g.isPython3:
    import configparser as ConfigParser
else:
    import ConfigParser

import os
import time
#@-<< imports >>
#@+<< version history >>
#@+node:ekr.20060108123141.1: ** << version history >>
#@@nocolor
#@+at
# 
# 0.1, 0.2 By Paul Paterson.
# 0.3 EKR:
# - Removed calls to g.top.
# - Added init function.
# 0.4 EKR: call g.enableIdleTimeHook() in init.
#@-<< version history >>

__version__ = "0.4" # EKR: call g.enableIdleTimeHook()

#@+others
#@+node:ekr.20060108123141.2: ** init
def init ():

    ok = not g.app.unitTesting # Don't want autosave after unit testing.
    if ok:
        # Register the handlers...
        global LAST_AUTOSAVE, ACTIVE, AUTOSAVE_INTERVAL

        AUTOSAVE_INTERVAL = 600
        ACTIVE = "Yes"
        LAST_AUTOSAVE = time.time()
        applyConfiguration()

        # Register the handlers...
        leoPlugins.registerHandler("idle", autosave)
        g.es("auto save enabled",color="orange")
        g.plugin_signon( __name__ )

        # Bug fix: 2009/10/06
        if ACTIVE == "Yes":
            g.enableIdleTimeHook()

    return ok
#@+node:edream.110203113231.725: ** applyConfiguration
def applyConfiguration(config=None):

    """Called when the user presses the "Apply" button on the Properties form"""

    global LAST_AUTOSAVE, ACTIVE, AUTOSAVE_INTERVAL

    if config is None:
        fileName = os.path.join(g.app.loadDir,"../","plugins","mod_autosave.ini")
        config = ConfigParser.ConfigParser()
        config.read(fileName)

    ACTIVE = config.get("Main", "Active")
    AUTOSAVE_INTERVAL = int(config.get("Main", "Interval"))
#@+node:edream.110203113231.726: ** autosave
def autosave(tag, keywords):

    """Save the current document if it has a name"""

    global LAST_AUTOSAVE

    c = keywords.get('c')

    if g.app.killed or not c or not c.exists: return

    ACTIVE = c.config.getBool('mod_autosave_active')
    AUTOSAVE_INTERVAL = c.config.getInt('mod_autosave_interval')
    if ACTIVE:
        if time.time() - LAST_AUTOSAVE > AUTOSAVE_INTERVAL:
            if c.mFileName and c.changed:
                g.es("Autosave: %s" % time.ctime(),color="orange")
                c.fileCommands.save(c.mFileName)
            LAST_AUTOSAVE = time.time()
#@-others
#@-leo
