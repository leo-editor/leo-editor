#@+leo-ver=4-thin
#@+node:edream.110203113231.738:@thin trace_tags.py
'''Trace most common hooks, but not key, drag or idle hooks.'''

#@@language python
#@@tabwidth -4

import leoGlobals as g
import leoPlugins

__version__ = "1.3" # Set version for the plugin handler.
#@<< version history >>
#@+node:ekr.20050303073056:<< version history >>
#@@killcolor

#@+at
# 
# 1.3 EKR:
#     - Don't trace drawing events.
#     - Added init function.
#@-at
#@nonl
#@-node:ekr.20050303073056:<< version history >>
#@nl

tagCount = 0

#@+others
#@+node:ekr.20050303073056.1:init
def init ():

    ok = not g.app.unitTesting

    if ok:
        leoPlugins.registerHandler("all",trace_tags)
        g.plugin_signon(__name__)

    return ok
#@nonl
#@-node:ekr.20050303073056.1:init
#@+node:edream.110203113231.739:trace_tags
def trace_tags (tag,keywords):

    global tagCount ; brief = True

    tagCount += 1 # Always count the hook.

    # List of hooks to suppress.
    if tag in (
        'bodykey1','bodykey2','dragging1','dragging2',
        'headkey1','headkey2',
        'idle',
        'after-redraw-outline','redraw-entire-outline',
        'draw-outline-text-box','draw-outline-icon',
        'draw-outline-node','draw-outline-box','draw-sub-outline',
    ):
        return

    # Almost all tags have both c and v keys in the keywords dict.
    if tag not in ('start1','end1','open1','open2','idle'):
        c = keywords.get('c')
        v = keywords.get('v')
        if not c:
            print tagCount,tag, 'c = None'
        if not v:
            if tag not in ('select1','select2','select3','unselect1','unselect2'):
                print tagCount,tag, 'v = None'

    # Hook-specific traces...
    if tag in ('command1','command2'):
        print tagCount,tag,keywords.get('label')
    elif tag in ('open1','open2'):
        print tagCount,tag,keywords.get('fileName')
    elif brief:
        print tagCount,tag
    else: # Verbose
        keys = keywords.items()
        keys.sort()
        for key,value in keys:
            print tagCount,tag,key,value
        print
#@nonl
#@-node:edream.110203113231.739:trace_tags
#@-others
#@nonl
#@-node:edream.110203113231.738:@thin trace_tags.py
#@-leo
