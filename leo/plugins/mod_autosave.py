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
from leo.core.leoQt import QtWidgets
if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr

# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.

# The global settings dict: Keys are commanders. Values are settings dicts.
gDict: Dict[Cmdr, Dict] = {}

#@+others
#@+node:ekr.20060108123141.2: ** init (mod_autosave.py)
def init():
    """Return True if the plugin has loaded successfully."""
    if g.unitTesting:
        return False
    # Register the handlers...
    g.registerHandler('after-create-leo-frame', onCreate)
    g.plugin_signon(__name__)
    return True
#@+node:edream.110203113231.726: ** onCreate (mod_autosave.py)
def onCreate(tag, keywords):
    """Handle the per-Leo-file settings."""
    global gDict
    c = keywords.get('c')
    if g.unitTesting or g.app.killed or not c or not c.exists:
        return
    # Do nothing here if we already have registered the idle-time hook.
    d = gDict.get(c.hash())
    if d:
        return
    active = c.config.getBool('mod-autosave-active', default=False)
    interval = c.config.getInt('mod-autosave-interval')
    if active:
        # Create an entry in the global settings dict.
        gDict[c.hash()] = {
            'last': time.time(),
            'interval': interval,
        }
        message = f"auto save {interval} sec. after changes"
        g.registerHandler('idle', onIdle)
    else:
        message = "@bool mod_autosave_active=False"
    print(message)
#@+node:ekr.20100904062957.10654: ** onIdle (mod_autosave.py)
def onIdle(tag, keywords):
    """Save the current document if it has a name"""
    global gDict
    if g.app.killed or g.unitTesting:
        return
    c = keywords.get('c')
    d = gDict.get(c.hash())
    if not c or not c.exists or not d or not c.mFileName:
        return
    # Redraw the screen only if we aren't editing a headline.
    redraw_flag = (
        g.app.gui.guiName() in ('qt', 'qttabs')
        and not isinstance(c.get_focus(), QtWidgets.QLineEdit)
    )
    # Wait the entire interval after c is changed.
    if not c.changed:
        d['last'] = time.time()
        gDict[c.hash()] = d
        return
    last = d.get('last')
    interval = d.get('interval')
    if time.time() - last >= interval:
        save(c)
        print(f"Autosave: {time.ctime()} {c.shortFileName()}")
        if redraw_flag:
            c.redraw()
        c.changed = False  # Clear the flag *without* updating the UI.
        d['last'] = time.time()
        gDict[c.hash()] = d
#@+node:ekr.20230327042532.1: ** save (mode_autosave.py)
def save(c: Cmdr) -> None:
    """Save c's outlines without changing any part of the UI."""
    fc = c.fileCommands
    g.app.commander_cacher.save(c, c.mFileName)
    fc.writeAllAtFileNodes()  # Ignore any errors.
    fc.writeOutline(c.mFileName)
#@-others
#@@language python
#@@tabwidth -4
#@-leo
