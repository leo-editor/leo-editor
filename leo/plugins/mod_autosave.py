#@+leo-ver=5-thin
#@+node:edream.110203113231.724: * @file ../plugins/mod_autosave.py
""" Autosaves the Leo outline every so often.

The time between saves is given by the setting, with default as shown::

    @int mod_autosave_interval = 300

This plugin is active only if::

    @bool mod_autosave_active = True

"""

# By Paul Paterson. Rewritten by EKR.
from __future__ import annotations
import time
from typing import Dict, TYPE_CHECKING
from leo.core import leoGlobals as g
# from leo.core.leoQt import QtWidgets
if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr

# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.

# The global settings dict: Keys are commanders. Values are settings dicts.
gDict: Dict[Cmdr, Dict] = {}

#@+others
#@+node:ekr.20060108123141.2: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    ok = not g.unitTesting  # Don't want autosave after unit testing.
    if ok:
        # Register the handlers...
        g.registerHandler('after-create-leo-frame', onCreate)
        g.plugin_signon(__name__)
    return ok
#@+node:edream.110203113231.726: ** onCreate (mod_autosave.py)
def onCreate(tag, keywords):
    """Handle the per-Leo-file settings."""
    global gDict
    c = keywords.get('c')
    if g.unitTesting or g.app.killed or not c or not c.exists:
        return
    # Do nothing here if we already have registered the idle-time hook.
    d = gDict.get(c.hash())
    if not d:
        active = c.config.getBool('mod-autosave-active', default=False)
        interval = c.config.getInt('mod-autosave-interval')
        if active:
            # Create an entry in the global settings dict.
            gDict[c.hash()] = {
                'last': time.time(),
                'interval': interval,
            }
            message = "auto save %s sec. after changes" % (interval)
            g.registerHandler('idle', onIdle)
        else:
            message = "@bool mod_autosave_active=False"
        g.es(message, color='orange')
#@+node:ekr.20100904062957.10654: ** onIdle
def onIdle(tag, keywords):
    """Save the current document if it has a name"""
    global gDict
    if g.app.killed or g.unitTesting:
        return
    # if g.app.gui.guiName() not in ('qt', 'qttabs'):
        # return
    c = keywords.get('c')
    if not c or not c.exists:
        return
    d = gDict.get(c.hash())
    if not d:
        return
    if not c.mFileName:
        return
    # Wait the entire interval after c is first changed or saved.
    # This wait gives the user a chance to revert changes before they are saved.
    if not c.changed:
        d['last'] = time.time()
        gDict[c.hash()] = d
        return
    # Do not save if the user is editing a headline.
    # w = c.get_focus()
    # if isinstance(w, QtWidgets.QLineEdit):
        # # Saving now would destroy the focus.
        # # There is **no way** to recreate outline editing after a redraw.
        # return
    last = d.get('last')
    interval = d.get('interval')
    if time.time() - last >= interval:
        # g.es_print("Autosave: %s" % time.ctime(), color="orange")
        print(f"Autosave: {time.ctime()}")
        # c.fileCommands.save(c.mFileName)
        # c.set_focus(w)
        save(c)
        d['last'] = time.time()
        gDict[c.hash()] = d
    
#@+node:ekr.20230327042532.1: ** save (mode_autosave.py)
def save(c: Cmdr) -> None:
    """Save c's outlines without changing any part of the UI."""
    fc = c.fileCommands
    fileName = c.mFileName
    g.app.commander_cacher.save(c, fileName)
    # ok = c.checkFileTimeStamp(fileName)
    # if not ok:
    #    return
    if c.checkOutline():
        print('mod_autosave: structural errors in outline! outline not saved')
        return
    ###
        # if c.sqlite_connection:
            # c.sqlite_connection.close()
            # c.sqlite_connection = None
    ### ok = fc.write_Leo_file(fileName)
    # g.app.recentFilesManager.writeRecentFilesFile(c)
    fc.writeAllAtFileNodes()  # Ignore any errors.
    fc.writeOutline(fileName)
    # if ok:
        # if not silent:
            # self.putSavedMessage(fileName)
        # c.clearChanged()  # Clears all dirty bits.
        # if c.config.getBool('save-clears-undo-buffer'):
            # g.es("clearing undo")
            # c.undoer.clearUndoState()
#@-others
#@@language python
#@@tabwidth -4
#@-leo
