#@+leo-ver=5-thin
#@+node:edream.110203113231.919: * @file ../plugins/examples/override_commands.py
"""Override the Equal Sized Pane command"""

from leo.core import leoGlobals as g

#@+others
#@+node:ekr.20111104210837.9691: ** init
def init():
    '''Return True if the plugin has loaded successfully.'''
    ok = not g.app.unitTesting
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
    return None
#@-others
#@@language python
#@@tabwidth -4
#@-leo
