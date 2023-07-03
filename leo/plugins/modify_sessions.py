#@+leo-ver=5-thin
#@+node:ekr.20230703052325.1: * @file ../plugins/modify_sessions.py
"""
This plugin changes when Leo writes session data, the list of open outlines.

By default, Leo *always* writes sesion data.

When this plugin is active Leo writes session data only if no files appear on the command line.
"""

from leo.core import leoGlobals as g

def init() -> bool:
    g.app.always_write_session_data = False
    return True
#@-leo
