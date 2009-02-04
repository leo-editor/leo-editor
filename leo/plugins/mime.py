#@+leo-ver=4-thin
#@+node:dan.20090203210614.1:@thin mime.py
#@<< docstring >>
#@+node:dan.20090203174248.27:<< docstring >>
'''Open files with their default platform program.

Double-clicking @mime nodes will attempt to open the named file as if opened
from a file manager.  @path parent nodes are used to find the full filename
path.

    @mime foodir/document.pdf

The string setting 'mime_open_cmd' allows specifying a program to handle opening files.

    @settings
        @string mime_open_cmd = see
        .. or ..
        @string mime_open_cmd = see %s

    Where '%s' is replaced with the full pathname.

Note: This plugin terminates handling of the 'icondclick1' event by returning
      True.  If another plugin using this event (e.g. vim.py) is also enabled,
      the order in @enabled-plugins matters.  For example: if vim.py is enabled
      before mime.py, double-clicking on an @mime node will both open the body
      text in [g]vim AND call the mime_open_cmd.

This plugin is complementary to the UNL.py plugin's @url nodes.  Use @url for
opening either URLs or Uniform Node Locators in "*.leo" files and use @mime
nodes for opening files on the local filesystem.
'''
#@-node:dan.20090203174248.27:<< docstring >>
#@nl

#@@language python
#@@tabwidth -4

__name__ = 'mime'
__version__ = '0.1'

#@<< version history >>
#@+node:dan.20090203174248.28:<< version history >>
#@+at
# 
# Contributed by Dan White.
# 
# 0.1 - Initial plugin
#@-at
#@-node:dan.20090203174248.28:<< version history >>
#@nl

#@<< imports >>
#@+node:dan.20090203174248.29:<< imports >>
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

import mailcap
import mimetypes
import os
import sys

subprocess = g.importExtension('subprocess',pluginName=__name__,verbose=True)
#@-node:dan.20090203174248.29:<< imports >>
#@nl

#@<< guess file association handler >>
#@+node:dan.20090203174248.35:<< guess file association handler >>
#@+at 
#@nonl
# Search for the best method of opening files.  If running a desktop manager,
# do the action corresponding to a double-click in the file manager.
#@-at
#@@c

_mime_open_cmd = ''

if sys.platform == 'linux2':
    #detect KDE or Gnome to use their file associations
    if os.environ.get('KDE_FULL_SESSION'):
        _mime_open_cmd = 'kfmclient exec'

    elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
        _mime_open_cmd = 'gnome-open'

#@-node:dan.20090203174248.35:<< guess file association handler >>
#@nl

#@+others
#@+node:dan.20090203174248.30:init
def init ():

    ok = not g.app.unitTesting

    if ok:
        print ('mime.py enabled')

        # Open on double click
        leoPlugins.registerHandler('icondclick1', open_mimetype)

        g.plugin_signon(__name__)

    return ok
#@-node:dan.20090203174248.30:init
#@+node:dan.20090203174248.31:open_mimetype
def open_mimetype(tag, keywords, val=None):
    '''Simulate double-clicking on the filename in a file manager.'''

    c = keywords.get('c')
    p = keywords.get('p')
    if not c or not p:
        return

    if p.h.startswith('@mime'):
        fname = p.h[6:]

        # honor @path
        d = c.scanAllDirectives(p)
        path = d.get('path')
        fpath = g.os_path_finalize_join(path, fname)

        mime_cmd = c.config.getString('mime_open_cmd') or _mime_open_cmd

        if mime_cmd:
            if '%s' not in mime_cmd:
                mime_cmd += ' %s'
            cmd = mime_cmd % fpath
        else:
            #no special handler specified, try mailcap/mimetype entries explicitly
            (ftype, encoding) = mimetypes.guess_type(fname)
            if ftype:
                caps = mailcap.getcaps()
                (cmd, entry) = mailcap.findmatch(caps, ftype,
                                                    filename=fpath,
                                                    key='view')
                if not cmd:
                    g.es('@mime: no entry for %s: %s' % (ftype, fname),
                         color='red')
                    return True #quit while we're ahead

                #g.trace('mailcap command:', cmd)
            else:
                g.es('@mime: unknown file type: %s' % fname, color='red')
                return True #quit while we're ahead


        g.trace('executing:', cmd)
        subprocess.Popen(cmd, shell=True)

        # block execution of e.g. vim plugin
        return True

    return val

#@-node:dan.20090203174248.31:open_mimetype
#@-others
#@-node:dan.20090203210614.1:@thin mime.py
#@-leo
