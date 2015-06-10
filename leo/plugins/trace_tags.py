#@+leo-ver=5-thin
#@+node:edream.110203113231.738: * @file trace_tags.py
''' Trace most common hooks, but not key, drag or idle hooks.'''
import leo.core.leoGlobals as g
tagCount = 0
#@+others
#@+node:ekr.20050303073056.1: ** init
def init():
    '''Return True if the plugin has loaded successfully.'''
    ok = not g.app.unitTesting
    if ok:
        g.registerHandler("all", trace_tags)
        g.plugin_signon(__name__)
    return ok
#@+node:edream.110203113231.739: ** trace_tags (trace_tags.py)
def trace_tags(tag, keywords):
    global tagCount; brief = True
    tagCount += 1 # Always count the hook.
    # List of hooks to suppress.
    if tag in (
        'bodykey1', 'bodykey2', 'dragging1', 'dragging2',
        'headkey1', 'headkey2',
        'idle',
        'after-redraw-outline', 'redraw-entire-outline',
        'draw-outline-text-box', 'draw-outline-icon',
        'draw-outline-node', 'draw-outline-box', 'draw-sub-outline',
    ):
        return
    # Almost all tags have both c and v keys in the keywords dict.
    if tag not in ('start1', 'end1', 'open1', 'open2', 'idle'):
        c = keywords.get('c')
        v = keywords.get('v')
        if not c:
            g.pr(tagCount, tag, 'c = None')
        if not v:
            if tag not in ('select1', 'select2', 'select3', 'unselect1', 'unselect2'):
                g.pr(tagCount, tag, 'v = None')
    # Hook-specific traces...
    if tag in ('command1', 'command2'):
        g.pr(tagCount, tag, keywords.get('label'))
    elif tag in ('open1', 'open2'):
        g.pr(tagCount, tag, keywords.get('fileName'))
    elif brief:
        g.pr(tagCount, tag)
    else: # Verbose
        keys = list(keywords.items())
        keys.sort()
        for key, value in keys:
            g.pr(tagCount, tag, key, value)
        g.pr('')
#@-others
#@@language python
#@@tabwidth -4
#@-leo
