#@+leo-ver=5-thin
#@+node:edream.110203113231.724: * @file mod_autosave.py
#@+<< docstring >>
#@+node:ekr.20060108123253: ** << docstring >>
""" Autosaves the Leo outline every so often.

The time between saves is given by the setting, with default as shown::

    @int mod_autosave_interval = 300

This plugin is active only if::

    @bool mod_autosave_active = True

 """
#@-<< docstring >>

#@@language python
#@@tabwidth -4

#@+<< imports >>
#@+node:ekr.20060108123141: ** << imports >>
import leo.core.leoGlobals as g

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
# 1.0 EKR: A complete rewrite:
#     - Don't use .ini file.  Use Leo settings, as described in the docstring.
#     - Separate the code into onCreate (handles settings) and onIdle.
#     - Use the global gDict to maintain per-commander values.
#@-<< version history >>

__version__ = "1.0" # EKR: a complete rewrite using only Leo settings.

# The global settings dict.
gDict = {} # Keys are commanders, values are settings dicts.

#@+others
#@+node:ekr.20060108123141.2: ** init
def init ():

    ok = not g.app.unitTesting # Don't want autosave after unit testing.

    if ok:
        # Register the handlers...
        g.registerHandler('after-create-leo-frame',onCreate)
        g.plugin_signon( __name__ )

    return ok
#@+node:edream.110203113231.726: ** onCreate
def onCreate(tag, keywords):

    """Handle the per-Leo-file settings."""

    global gDict

    c = keywords.get('c')
    if g.app.killed or not c or not c.exists: return
    if g.unitTesting: return  # 2011/02/28
    
    # 2011/02/28: do nothing here if we already have registered the idle-time hook.
    d = gDict.get(c.hash())
    if d: return

    active = c.config.getBool('mod_autosave_active',default=False)
    interval = c.config.getInt('mod_autosave_interval')

    if active:
        # Create an entry in the global settings dict.
        d = {
            'last':time.time(),
            'interval':interval,
        }
        gDict[c.hash()] = d
        g.es("auto save enabled every %s sec." % (
            interval),color="orange")
        g.registerHandler('idle',onIdle)
        g.enableIdleTimeHook()
    else:
         g.es("@bool mod_autosave_active=False",color='orange')
#@+node:ekr.20100904062957.10654: ** onIdle
def onIdle (tag,keywords):

    """Save the current document if it has a name"""

    global gDict

    trace = False and not g.unitTesting
    c = keywords.get('c')
    if g.app.killed or not c or not c.exists: return
    if g.unitTesting: return # 2011/02/28
    d = gDict.get(c.hash())
    if not d: return
    last = d.get('last')
    interval = d.get('interval')
    if time.time()-last >= interval:
        # 2010/11/16: disable autosave unless focus is in the body or Tree.
        w = c.get_focus()
        guiName = g.app.gui.guiName()
        if guiName in ('qt','qttabs'):
            bodyWidget = c.frame.body
            treeWidget = c.frame.tree.treeWidget # QtGui.
        ### elif guiName == 'tkinter':
            # treeWidget = c.frame.tree.canvas
            # bodyWidget = c.frame.body.bodyCtrl
        else:
            return # Only Qt and Tk gui's are supported.
        isBody = w == bodyWidget
        isTree = w == treeWidget
        if trace: g.trace(
            'isBody: %s, isTree: %s, w: %s, bodyWidget: %s, treeWidget: %s' % (
                isBody,isTree,w,bodyWidget, treeWidget))
        if c.mFileName and c.changed and (isBody or isTree):
            # g.trace(w)
            s = "Autosave: %s" % time.ctime()
            g.es(s,color="orange")
            if trace: g.trace('message: %s' % (s))
            c.fileCommands.save(c.mFileName)
            c.set_focus(w,force=True) # 2010/11/16: save & restore focus.
        elif trace:
            g.trace('not changed.')
        # Update the global dict.
        d['last'] = time.time()
        gDict[c.hash()] = d
    elif trace:
        g.trace('not time',c.shortFileName())
#@-others
#@-leo
