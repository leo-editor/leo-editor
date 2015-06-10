#@+leo-ver=5-thin
#@+node:edream.110203113231.919: * @file examples/override_commands.py
"""Override the Equal Sized Pane command"""
#@@language python
#@@tabwidth -4
import leo.core.leoGlobals as g
__version__ = "1.2"
#@+others
#@+node:ekr.20111104210837.9691: ** init
def init():
    '''Return True if the plugin has loaded successfully.'''
    ok = g.app.unitTesting
        # Not for unit testing: overrides core methods.
    if ok:
        # Register the handlers...
        g.registerHandler("command1", onCommand)
        g.plugin_signon(__name__)
    return ok
#@+node:edream.110203113231.920: ** onCommand
def onCommand(tag, keywords):
    if keywords.get("label") == "equalsizedpanes":
        g.es("over-riding Equal Sized Panes")
        return "override" # Anything other than None overrides.
#@-others
#@-leo
