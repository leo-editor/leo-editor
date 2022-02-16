#@+leo-ver=5-thin
#@+node:ekr.20101110094759.5843: * @file ../plugins/mod_speedups.py
""" Experimental speedups

Various optimizations. Use at your own risk.

If stuff breaks, disable this plugin before reporting bugs.

"""

# By VMV.
import os.path
from leo.core import leoGlobals as g

#@+others
#@+node:ville.20090804155017.7594: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    return True
#@+node:ville.20090804155017.12332: ** os.path shortcuts
g.os_path_basename = os.path.basename
g.os_path_split = os.path.split
g.os_path_splitext = os.path.splitext
#g.os_path_expanduser = os.path.expanduser
g.os_path_abspath = os.path.abspath
#g.os_path_join = os.path.join
g.os_path_normpath = os.path.normpath
g.os_path_exists = os.path.exists
#g.os_path_finalize = os.path.abspath



#@+node:ville.20090804155017.12333: ** os_path_finalize caching
os_path_finalize_orig = g.os_path_finalize
os_path_finalize_join_orig = g.os_path_finalize_join

_finalized_cache = {}
_finalized_join_cache = {}
_expanduser_cache = {}

def os_path_finalize_cached(path, **keys):
    res = _finalized_cache.get(path)
    if res:
        return res
    res = os_path_finalize_orig(path, **keys)
    _finalized_cache[path] = res
    return res

def os_path_finalize_join_cached(*args, **keys):
    res = _finalized_join_cache.get(args)
    if res:
        #print "cache hit", args
        return res

    res = os_path_finalize_join_orig(*args, **keys)
    _finalized_join_cache[args] = res
    return res

def os_path_expanduser_cached(path, encoding=None):
    res = _expanduser_cache.get(path)
    if res:
        #print "cache hit", path
        return res
    res = os.path.expanduser(path)
    _expanduser_cache[path] = res
    return res

def os_path_join_speedup(*args, **kw):
    path = os.path.join(*args)
    return path

g.os_path_finalize = os_path_finalize_cached
g.os_path_finalize_join = os_path_finalize_join_cached
g.os_path_expanduser = os_path_expanduser_cached
#g.os_path_join = os_path_join_speedup

#@-others
#@@language python
#@@tabwidth -4
#@-leo
