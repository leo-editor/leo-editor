#@+leo-ver=5-thin
#@+node:ekr.20130808211520.15893: * @file ../plugins/timestamp.py
"""If this plugin is enabled, the following node attributes will be managed:
    - str_ctime: creation time
    - str_mtime: time node was last modified
    - str_atime: time node contents were last viewed
"""

# By Kent Tenney

import time
from leo.core import leoGlobals as g

#@@language python
#@@tabwidth -4
#@+others
#@+node:ekr.20130808211520.15895: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    g.registerHandler('new', new_hook)
    g.registerHandler('create-node', create_node_hook)
    g.registerHandler('select1', select1_hook)
    g.plugin_signon(__name__)
    return True
#@+node:ekr.20130808211520.15896: ** get_timestamp_now
def get_timestamp_now():
    """Use standard Unix timestamps
    """

    # local time as a time struct
    now = time.localtime()

    # convert time struct to seconds since epoch (timestamp)
    local = time.mktime(now)
    return str(local)

#@+node:ekr.20130808211520.15897: ** new_hook
def new_hook(tag, keywords):
    """Hooked to <new> event, fired when a Leo file is created,
    which the create_node_hook doesn't handle.
    """

    c = keywords['c']
    root = c.rootPosition()
    d = root.v.u
    timestamp = get_timestamp_now()
    d['str_ctime'] = d['str_mtime'] = d['str_atime'] = timestamp

#@+node:ekr.20130808211520.15898: ** create_node_hook
def create_node_hook(tag, keywords):
    """Hooked to <create-node> = set all 3 timestamps to now
    """

    timestamp = get_timestamp_now()
    d = keywords['p'].v.u
    d['str_ctime'] = d['str_mtime'] = d['str_atime'] = timestamp

#@+node:ekr.20130808211520.15899: ** select1_hook
def select1_hook(tag, keywords):
    """Hooked to select1, which fires when focus changes
    Always sets str_atime to now, sets str_mtime if node body has changed
    """

    prev = keywords['old_p'].v
    current = keywords['new_p'].v
    now = get_timestamp_now()
    current.u['str_atime'] = now
    if prev is None:
        return
    if prev.isDirty():
        if hasattr(prev, 'prev_body'):
            if prev.b != prev.prev_body:
                prev.u['str_mtime'] = now
                prev.prev_body = prev.b
        else:
            prev.u['str_mtime'] = now
            prev.prev_body = prev.b

#@-others
#@-leo
