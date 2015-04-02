#@+leo-ver=5-thin
#@+node:EKR.20040517075715.1: * @file mod_tempfname.py
#@+<< docstring >>
#@+node:ekr.20101112195628.5433: ** << docstring >> (mod_tempfname)
"""
Replaces c.openWithTempFilePath to create alternate temporary
directory paths. Two alternates are supported:

``@bool open_with_clean_filenames = True (default)``
    Creates temporary files with a filename that begins with the headline
    text, and located in a "username_Leo" subdirectory of the temporary
    directory. The "LeoTemp" prefix is omitted.
    
    This option uses ``@bool open_with_uses_derived_file_extensions``.

``@bool open_with_clean_filenames = True``
    Subdirectories mirror the node's hierarchy in Leo.
    
Either method makes it easier to see which temporary file is related to
which outline node.

"""
#@-<< docstring >>

#@@language python
#@@tabwidth -4

import leo.core.leoGlobals as g

import leo.core.leoCommands as leoCommands
import getpass
import os
import tempfile

__version__ = "1.3"

#@+others
#@+node:ekr.20100128091412.5382: ** init
def init():
    '''Return True if the plugin has loaded successfully.'''
    ok = not g.app.unitTesting
        # Not Ok for unit testing: it changes Leo's core.
    if ok:
        # Register the handlers...
        g.registerHandler("start2", onStart)
        g.plugin_signon(__name__)
    return ok
#@+node:EKR.20040517075715.2: ** onStart
def onStart (tag,keywords):
    '''Monkey patch c.openWithTempFilePath.'''
    # g.trace("mod_tempfName: replacing c.openWithTempFilePath")
    g.funcToMethod(openWithTempFilePath,leoCommands.Commands,"openWithTempFilePath")
#@+node:EKR.20040517075715.3: ** openWithTempFilePath
def openWithTempFilePath (self,v,ext):
    """
    Return the path to the temp file corresponding to v and ext.
    Replaces c.openWithTempFilePath.
    """
    c = self
    if c.config.getBool('open_with_clean_filenames'):
        path = cleanFileName(c,v,ext)
    else:
        path = legacyFileName(c,v,ext)
    return path
#@+node:ekr.20150328112036.1: *3* cleanFileName
def cleanFileName(c,v,ext):
    '''Compute the file name when subdirectories mirror the node's hierarchy in Leo.'''
    trace = False and not g.unitTesting
    g.trace(g.callers())
    p = c.p
    use_extentions = c.config.getBool('open_with_uses_derived_file_extensions')
    ancestors,found = [],False
    for p in p.self_and_parents():
        h = p.anyAtFileNodeName()
        if not h:
            h = p.h  # Not an @file node: use the entire header
        elif use_extentions and not found:
            # Found the nearest ancestor @<file> node.
            found = True
            base,ext2 = g.os_path_splitext(h)
            if p == c.p: h = base
            if ext2: ext = ext2
        ancestors.append(g.sanitize_filename(h))

    # The base directory is <tempdir>/Leo<id(v)>.
    ancestors.append("Leo" + str(id(v)))

    # Build temporary directories.
    td = os.path.abspath(tempfile.gettempdir())
    while len(ancestors) > 1:
        td = os.path.join(td, ancestors.pop())
        if not os.path.exists(td):
            # if trace: g.trace('creating',td)
            os.mkdir(td)

    # Compute the full path.
    name = ancestors.pop() + ext
    path = os.path.join(td,name)
    if trace: g.trace('returns',path,g.callers())
    return path
#@+node:ekr.20150328112256.1: *3* legacyFileName
def legacyFileName(c,v,ext):
    '''Compute a legacy file name for unsupported operating systems.'''
    try:
        leoTempDir = getpass.getuser() + "_" + "Leo"
    except Exception:
        leoTempDir = "LeoTemp"
        g.es("Could not retrieve your user name.")
        g.es("Temporary files will be stored in: %s" % leoTempDir)

    td = os.path.join(os.path.abspath(tempfile.gettempdir()),leoTempDir)
    if not os.path.exists(td):
        os.mkdir(td)
    name = g.sanitize_filename(v.h) + '_' + str(id(v)) + ext
    path = os.path.join(td,name)
    return path
#@-others
#@-leo
