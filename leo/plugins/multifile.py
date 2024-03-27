#@+leo-ver=5-thin
#@+node:mork.20041018204908.1: * @file ../plugins/multifile.py
#@+<< docstring >>
#@+node:ekr.20050226114732: ** << docstring >>
#@@language rest
r""" Allows Leo to write a file to multiple locations.

This plugin acts as a post-write mechanism, a file must be written to the
file system for it to work. At this point it is not a replacement for @path or an
absolute path, it works in tandem with them.

To use, place @multipath at the start of a line in the root node or an ancestor
of the node. The format is (On Unix-like systems)::

    (at)multipath /machine/unit/:/machine/robot/:/machine/

New in version 0.6 of this plugin: the separator used above is ';' not ':',
for example::

    (at)multipath c:\prog\test;c:\prog\unittest

It will places copy of the written file in each of these directories.

There is an additional directive that simplifies common paths, it is called
@multiprefix. By typing @multiprefix with a path following it, before a
@multipath directive you set the beginning of the paths in the @multipath
directive. For example::

    (at)multiprefix /leo #@multipath /plugins

or::

    (at)multiprefix /leo/
    (at)multipath plugins: fungus : drain

copies a file to /leo/plugins /leo/fungus /leo/drain.

Note: I put (at) in front of the directives here because I don't want someone
browsing this file to accidentally save multiple copies of this file to their
system :)

The @multiprefix stays in effect for the entire tree until reset with another
@multiprefix directive. @multipath is cumulative, in that for each @multipath in
an ancestor a copy of the file is created. These directives must at the
beginning of the line and by themselves.
"""
#@-<< docstring >>
#@+<< imports >>
#@+node:ekr.20050226114732.1: ** << imports >>
import os.path
import shutil
import weakref
from typing import Any
from leo.core import leoGlobals as g
from leo.core import leoAtFile
#@-<< imports >>
multiprefix = '@multiprefix'
multipath = '@multipath'
haveseen: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()
files: dict[str, Any] = {}  # Values are positions.
original_precheck = None
#@+others
#@+node:ekr.20050226115130.1: ** init & helpers (multifile.py)
def init():
    """Return True if the plugin has loaded successfully."""
    global original_precheck
    #
    # Append to the module list, not to the g.copy.
    g.globalDirectiveList.append('multipath')
    g.globalDirectiveList.append('multiprefix')
    #
    # Override all instances of at.precheck
    at = leoAtFile.AtFile
    original_precheck = at.precheck
    g.funcToMethod(decorated_precheck, at, name='precheck')
    #
    # g.registerHandler('save1',start)
    g.registerHandler('save2', stop)
    g.registerHandler(('new', 'menu2'), addMenu)
    g.plugin_signon(__name__)
    return True  # gui-independent.
#@+node:mork.20041019091317: *3* addMenu
def addMenu(tag, keywords):

    c = keywords.get('c')
    if not c or c in haveseen:
        return
    haveseen[c] = None
    menu = c.frame.menu.getMenu('Edit')
    c.add_command(menu,
        label="Insert Directory String",
        command=lambda c=c: insertDirectoryString(c))
#@+node:mork.20041019091524: *3* insertDirectoryString
def insertDirectoryString(c):

    d = g.app.gui.runOpenDirectoryDialog(
        title='Select a directory',
        startdir=os.curdir)
    if d:
        w = c.frame.body.wrapper
        ins = w.getInsertPoint()
        w.insert(ins, d)
        # w.event_generate('<Key>')
        # w.update_idletasks()
#@+node:mork.20041018204908.3: ** decorated_precheck
def decorated_precheck(self, fileName, root):
    """Call at.precheck, then add fileName to the global files list."""
    #
    # Call the original method.
    global files
    global original_precheck
    val = original_precheck(self, fileName, root)
    #
    # Save a pointer to the root for later.
    if val and root.isDirty():
        files[fileName] = root.copy()
    return val
#@+node:mork.20041018204908.6: ** stop
def stop(tag, keywords):

    c = keywords.get('c')
    if not c:
        g.trace('can not happen')
        return
    multi = scanForMultiPath(c)
    for fileName in multi:
        paths = multi.get(fileName)
        for path in paths:
            try:
                if os.path.isdir(path):
                    shutil.copy2(fileName, path)
                    g.blue("multifile:\nWrote %s to %s" % (fileName, path))
                else:
                    g.error("multifile:\n%s is not a directory, not writing %s" % (path, fileName))
            except Exception:
                g.error("multifile:\nCant write %s to %s" % (fileName, path))
                g.es_exception_type()
    files.clear()
#@+node:mork.20041018204908.5: ** scanForMultiPath
def scanForMultiPath(c):

    """Return a dictionary whose keys are fileNames and whose values are
    lists of paths to which the fileName is to be written.
    New in version 0.6 of this plugin: use ';' to separate paths in @multipath statements."""

    global multiprefix, multipath
    d: dict = {}
    sep = ';'
    for fileName in files:  # Keys are fileNames, values are root positions.
        root = files[fileName]
        default_directory = g.os_path_dirname(fileName)
        fileName = g.os_path_join(default_directory, fileName)
        positions = [p.copy() for p in root.self_and_parents()]
        positions.reverse()
        prefix = ''
        for p in positions:
            lines = p.b.split('\n')
            # Calculate the prefix fisrt.
            for s in lines:
                if s.startswith(multiprefix):
                    prefix = s[len(multiprefix) :].strip()
            # Handle the paths after the prefix is in place.
            for s in lines:
                if s.startswith(multipath):
                    s = s[len(multipath) :].strip()
                    paths = s.split(sep)
                    paths = [z.strip() for z in paths]
                    if prefix:
                        paths = [g.os_path_join(default_directory, prefix, z) for z in paths]
                    else:
                        paths = [g.os_path_join(default_directory, z) for z in paths]
                    aList = d.get(fileName, [])
                    aList.extend(paths)
                    d[fileName] = aList
    return d
#@-others
#@@language python
#@@tabwidth -4
#@-leo
