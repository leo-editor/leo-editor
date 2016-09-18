#@+leo-ver=5-thin
#@+node:edream.110203113231.724: * @file mod_autosave.py
""" Autosaves the Leo outline every so often.

The time between saves is given by the setting, with default as shown::

    @int mod_autosave_interval = 300

This plugin is active only if::

    @bool mod_autosave_active = True

"""

# By Paul Paterson. Rewritten by EKR.
import leo.core.leoGlobals as g
import time
# The global settings dict.
gDict = {} # Keys are commanders, values are settings dicts.

#@+others
#@+node:ekr.20060108123141.2: ** init
def init ():
    '''Return True if the plugin has loaded successfully.'''
    ok = not g.app.unitTesting
        # Don't want autosave after unit testing.
    if ok:
        # Register the handlers...
        g.registerHandler('after-create-leo-frame',onCreate)
        g.plugin_signon( __name__ )
    return ok
#@+node:edream.110203113231.726: ** onCreate (mod_autosave.py)
def onCreate(tag, keywords):
    """Handle the per-Leo-file settings."""
    global gDict
    c = keywords.get('c')
    if g.app.unitTesting or g.app.killed or not c or not c.exists:
        return
    # Do nothing here if we already have registered the idle-time hook.
    d = gDict.get(c.hash())
    if not d:
        active = c.config.getBool('mod_autosave_active',default=False)
        interval = c.config.getInt('mod_autosave_interval')
        if active:
            # Create an entry in the global settings dict.
            gDict[c.hash()] = {
                'last':time.clock(),
                'interval':interval,
            }
            message = "auto save %s sec. after changes" % (interval)
            g.registerHandler('idle',onIdle)
        else:
            message = "@bool mod_autosave_active=False"
        g.es(message, color='orange')
#@+node:ekr.20100904062957.10654: ** onIdle
def onIdle (tag,keywords):
    """Save the current document if it has a name"""
    global gDict
    guiName = g.app.gui.guiName()
    if guiName not in ('qt','qttabs'):
        return
    c = keywords.get('c')
    d = gDict.get(c.hash())
    if c and d and c.exists and c.mFileName and not g.app.killed and not g.unitTesting:
        # Wait the entire interval after c is first changed or saved.
        # Imo (EKR) this is the desired behavior.
        # It gives the user a chance to revert changes before they are changed.
        if c.changed:
            last = d.get('last')
            interval = d.get('interval')
            if time.clock()-last >= interval:
                autosave(c, d)
                d['last'] = time.clock()
                gDict[c.hash()] = d
        else:
            d['last'] = time.clock()
            gDict[c.hash()] = d
#@+node:ekr.20160917174238.1: ** autosave
def autosave(c, d):
    '''
    Save the file, retaining focus.
    Note, however, that headline widgets disappear when a redraw happens.
    '''
    w = c.get_focus()
    g.es_print("Autosave: %s" % time.ctime(),color="orange")
    c.fileCommands.save(c.mFileName)
    c.set_focus(w,force=True)
#@-others
#@@language python
#@@tabwidth -4
#@-leo
