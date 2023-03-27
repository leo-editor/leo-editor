#@+leo-ver=5-thin
#@+node:edream.110203113231.724: * @file ../plugins/mod_autosave.py
""" Autosaves the Leo outline every so often to a .bak file.

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
        message = f"auto save {interval} every sec. {c.shortFileName()}"
        g.registerHandler('idle', onIdle)
    else:
        message = "@bool mod_autosave_active=False"
    print(message)
#@+node:ekr.20100904062957.10654: ** onIdle (mod_autosave.py)
def onIdle(tag, keywords):
    """
    Save the outline to a .bak file every "interval" seconds if it has changed.
    Make *no* changes to the UI and do *not* update c.changed.
    """
    global gDict
    if g.app.killed or g.unitTesting:
        return
    c = keywords.get('c')
    d = gDict.get(c.hash())
    if not d or not c or not c.exists or not c.changed or not c.mFileName:
        return
    # Wait the entire interval.
    if time.time() - d.get('last') < d.get('interval'):
        return
    save(c)
    print(f"Autosave: {time.ctime()} {c.shortFileName()}.bak")
    # Do *not* update the outline's change status.
    # Continue to save the outline to the .bak file
    # until the user explicitly saves the outline.
    gDict[c.hash()]['last'] = time.time()
#@+node:ekr.20230327042532.1: ** save (mode_autosave.py)
def save(c: Cmdr) -> None:
    """Save c's outlines to a .bak file without changing any part of the UI."""
    fc = c.fileCommands
    old_log = g.app.log
    # Make sure nothing goes to the log.
    try:
        # Disable the log so that g.es will append to g.app.logWaiting.
        g.app.log = None
        # The following methods call g.es.
        fc.writeAllAtFileNodes()  # Ignore any errors.
        fc.writeOutline(f"{c.mFileName}.bak")
    finally:
        # Print the queued messages produced by g.es.
        for s, color, newline in g.app.logWaiting:
            print(s.rstrip())
        # Restore the log.
        g.app.logWaiting = []
        g.app.log = old_log
#@-others
#@@language python
#@@tabwidth -4
#@-leo
