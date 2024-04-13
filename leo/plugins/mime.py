#@+leo-ver=5-thin
#@+node:dan.20090217132953.1: * @file ../plugins/mime.py
#@+<< docstring >>
#@+node:dan.20090203174248.27: ** << docstring >> (mime.py)
r""" Opens files with their default platform program.

The double-click-icon-box command on @mime nodes will attempt to open the
named file as if opened from a file manager. \@path parent nodes are used
to find the full filename path. For example::

    @mime foodir/document.pdf

The string setting 'mime_open_cmd' allows specifying a program to handle
opening files::

    @settings
        @string mime_open_cmd = see
        .. or ..
        @string mime_open_cmd = see %s

Where '%s' is replaced with the full pathname.

**Note**: This plugin terminates handling of the 'icondclick1' event by returning
True. If another plugin using this event (e.g. vim.py) is also enabled, the
order in @enabled-plugins matters. For example: if vim.py is enabled before
mime.py, double-clicking on an @mime node will both open the body text in [g]vim
AND call the mime_open_cmd.

Use @url for opening either URLs or Uniform Node Locators in "\*.leo" files and
use @mime nodes for opening files on the local file system. It also replaces the
startfile.py plugin, where here the headline must start with @mime to activate
this plugin.

For other sys.platform's, add an elif case to the section "guess file
association handler" and either define a default _mime_open_cmd string, where
"%s" will be replaced with the filename, or define a function taking the
filename string as its only argument and set as open_func.
"""
#@-<< docstring >>

# By Dan White <etihwnad _at_ gmail _dot_ com>.

import mailcap
import mimetypes
import os
import subprocess
import sys
from leo.core import leoGlobals as g

#@+others
#@+node:dan.20090210183435.1: ** exec_full_cmd
def exec_full_cmd(cmd):
    """Accept a command string including filename and return a function
    which executes the command."""

    def f(fpath):
        return subprocess.Popen(cmd, shell=True)

    return f
#@+node:dan.20090210180636.27: ** exec_string_cmd
def exec_string_cmd(cmd):
    """Accept a command string and return a function which opens executes the command,
    replacing %s with the full file path."""

    if '%s' not in cmd:
        cmd = cmd + ' %s'

    def f(fpath):
        s = cmd % fpath
        return subprocess.Popen(s, shell=True)

    return f
#@+node:dan.20090203174248.30: ** init (mime.py)
def init():
    """Return True if the plugin has loaded successfully."""
    ok = not g.unitTesting
    if ok:
        # Open on double click
        g.registerHandler('icondclick1', open_mimetype)
        g.plugin_signon(__name__)
    return ok
#@+node:dan.20090203174248.31: ** open_mimetype
def open_mimetype(tag, keywords, val=None):
    """Simulate double-clicking on the filename in a file manager.  Order of
    preference is:

        1) @string mime_open_cmd setting
        2) _mime_open_cmd, defined per sys.platform detection
        3) open_func(fpath), defined per sys.platform detection
        4) mailcap file for mimetype handling
    """

    global open_func

    c = keywords.get('c')
    p = keywords.get('p')
    if not c or not p:
        return None

    if p.h.startswith('@mime'):
        fname = p.h[6:]

        # honor @path
        d = c.scanAllDirectives(p)
        path = d.get('path')
        fpath = g.finalize_join(path, fname)

        # stop here if the file doesn't exist
        if not g.os_path_exists(fpath):
            g.error('@mime: file does not exist, %s' % fpath)
            return True

        # user-specified command string, or sys.platform-determined string
        mime_cmd = c.config.getString('mime-open-cmd') or _mime_open_cmd
        if mime_cmd:
            if '%s' not in mime_cmd:
                mime_cmd += ' %s'
            open_func = exec_string_cmd(mime_cmd)

        # no special handler function specified (unknown platform),
        # try mailcap/mimetype entries explicitly
        if open_func is None:
            (ftype, encoding) = mimetypes.guess_type(fname)
            if ftype:
                caps = mailcap.getcaps()
                (fullcmd, entry) = mailcap.findmatch(caps, ftype,
                                                     filename=fpath,
                                                     key='view')
                if fullcmd:
                    # create a function which merely executes the fullcmd in
                    # a shell for e.g. PATH access
                    open_func = exec_full_cmd(fullcmd)
                else:
                    g.error('@mime: no mailcap entry for %s: %s' % (ftype, fname))
                g.trace('mailcap command:', fullcmd)
            else:
                g.error('@mime: unknown file type: %s' % fname)


        # use the custom open_func to open external file viewer
        if open_func:
            open_func(fpath)
        else:
            g.error('@mime: no known way to open %s' % fname)

        # block execution of e.g. vim plugin
        return True

    # not an @mime node
    return val

#@-others
#@@language python
#@@tabwidth -4
#@+<< guess file association handler >>
#@+node:dan.20090203174248.35: ** << guess file association handler >>
#@+at Search for the best method of opening files.  If running a desktop manager,
# do the action corresponding to a double-click in the file manager.
#
# Helper functions return a function f(fpath) which takes the full file path,
# launches the viewer and returns immediately.
#@@c

# open_func is called with the full file path
open_func = None

# no initial system string command
_mime_open_cmd = ''

# default methods of opening files
if sys.platform == 'linux2':
    # detect KDE or Gnome to use their file associations
    if os.environ.get('KDE_FULL_SESSION'):
        # _mime_open_cmd = 'kfmclient exec'
        open_func = exec_string_cmd('kfmclient exec')

    elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
        _mime_open_cmd = 'gnome-open'

    else:
        pass
elif sys.platform == 'win32':
    # Use this directly as 1-arg fn, default action is 'open'
    open_func = os.startfile
#@-<< guess file association handler >>
#@-leo
