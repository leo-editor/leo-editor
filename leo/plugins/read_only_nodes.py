#@+leo-ver=5-thin
#@+node:edream.110203113231.876: * @file ../plugins/read_only_nodes.py
#@+<< docstring >>
#@+node:ekr.20050912052854: ** << docstring >>
""" Creates and updates @read-only nodes.

Here's my first attempt at customizing leo. I wanted to have the ability to
import files in "read-only" mode, that is, in a mode where files could only
be read by leo (not tangled), and also kept in sync with the content on the
drive.

The reason for this is for example that I have external programs that generate
resource files. I want these files to be part of a leo outline, but I don't
want leo to tangle or in any way modify them. At the same time, I want them
to be up-to-date in the leo outline.

So I coded the directive plugin. It has the following characteristics:

- It reads the specified file and puts it into the node content.

- If the @read-only directive was in the leo outline already, and the file content
  on disk has changed from what is stored in the outline, it marks the node as
  changed and prints a "changed" message to the log window; if, on the other hand,
  the file content has _not_ changed, the file is simply read and the node is
  not marked as changed.

- When you write a @read-only directive, the file content is added to the node
  immediately, i.e. as soon as you press Enter (no need to call a menu
  entry to import the content).

- If you want to refresh/update the content of the file, just edit the headline
  and press Enter. The file is reloaded, and if in the meantime it has changed,
  a "change" message is sent to the log window.

- The body text of a @read-only file cannot be modified in leo.

The syntax to access files in @read-only via ftp/http is the following::

    @read-only http://www.ietf.org/rfc/rfc0791.txt
    @read-only ftp://ftp.someserver.org/filepath

If FTP authentication (username/password) is required, it can be specified as follows::

    @read-only ftp://username:password@ftp.someserver.org/filepath

For more details, see the doc string for the class FTPurl.

Davide Salomoni
"""
#@-<< docstring >>

# Contributed by Davide Salomoni <dsalomoni@yahoo.com>

# EKR: This plugin does not appear to be ready for Python 3.

# pylint: disable=not-callable,raise-missing-from

#@+<< imports >>
#@+node:ekr.20050311091110.1: ** << imports >>
from formatter import AbstractFormatter, DumbWriter  # pylint: disable=import-error
import ftplib
import html.parser as HTMLParser
import io
import os
import sys
from typing import Any
import urllib.parse as urlparse
from urllib.request import urlopen
from leo.core import leoGlobals as g
# Abbreviation.
StringIO = io.StringIO
#@-<< imports >>
insertOnTime = None
insertOffTime = None
#@+others
#@+node:ekr.20050311092840: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    ok = not g.unitTesting  # Not Ok for unit testing.
    if ok:
        g.registerHandler(('new', 'open2'), on_open)
        g.registerHandler("bodykey1", on_bodykey1)
        g.registerHandler("headkey2", on_headkey2)
        if 0:  # doesn't work: the cursor stops blinking.
            g.registerHandler("select1", on_select1)
            g.registerHandler("select2", on_select2)
        g.plugin_signon(__name__)
    return ok
#@+node:edream.110203113231.879: ** class FTPurl
class FTPurl:
    """An FTP wrapper class to store/retrieve files using an FTP URL.

    To create a connection, call the class with the constructor:

        FTPurl(url[, mode])

    The url should have the following syntax:

        ftp://[username:password@]remotehost/filename

    If username and password are left out, the connection is made using
    username=anonymous and password=realuser@host (for more information,
    see the documentation of module ftplib).

    The mode can be '' (default, for ASCII mode) or 'b' (for binary mode).
    This class raises an IOError exception if something goes wrong.
    """

    #@+others
    #@+node:edream.110203113231.880: *3* __init__
    def __init__(self, ftpURL, mode=''):

        parse = urlparse(ftpURL)  # type:ignore
        if parse[0] != 'ftp':
            raise IOError("error reading %s: malformed ftp URL" % ftpURL)

        # ftp URL; syntax: ftp://[username:password@]hostname/filename
        self.mode = mode
        authIndex = parse[1].find('@')
        if authIndex == -1:
            auth = None
            ftphost = parse[1]
        else:
            auth = parse[1][:authIndex]
            ftphost = parse[1][authIndex + 1 :]
        self.ftp = ftplib.FTP(ftphost)
        if auth is None:
            self.ftp.login()
        else:
            # the URL has username/password
            pwdIndex = auth.find(':')
            if pwdIndex == -1:
                raise IOError("error reading %s: malformed ftp URL" % ftpURL)
            user = auth[:pwdIndex]
            password = auth[pwdIndex + 1 :]
            self.ftp.login(user, password)
        self.path = parse[2][1:]
        self.filename = os.path.basename(self.path)
        self.dirname = os.path.dirname(self.path)
        self.isConnectionOpen = 1
        self.currentLine = 0
    #@+node:edream.110203113231.881: *3* Getters
    #@+node:edream.110203113231.882: *4* read
    def read(self):
        """Read the filename specified in the constructor and return it as a string.
        If the constructor specifies no filename, or if the URL ends with '/',
        return the list of files in the URL directory.
        """
        self.checkParams()
        if self.filename == '' or self.path[-1] == '/':
            return self.dir()

        try:
            if self.mode == '':  # mode='': ASCII mode
                slist: list = []
                self.ftp.retrlines('RETR %s' % self.path, slist.append)  # type:ignore
                s = '\n'.join(slist)
            else:  # mode='b': binary mode
                file = StringIO()
                self.ftp.retrbinary('RETR %s' % self.path, file.write)  # type:ignore
                s = file.getvalue()
                file.close()
            return s
        except Exception:
            exception, msg, tb = sys.exc_info()
            raise IOError(msg)

    #@+node:edream.110203113231.883: *4* readline
    def readline(self):
        """Read one entire line from the remote file."""
        self.lst: list
        try:
            self.lst
        except AttributeError:
            self.lst = self.read().splitlines(1)

        if self.currentLine < len(self.lst):
            s = self.lst[self.currentLine]
            self.currentLine = self.currentLine + 1
            return s
        return ''
    #@+node:edream.110203113231.884: *3* Setters
    #@+node:edream.110203113231.885: *4* write
    def write(self, s):
        """write(s) stores the string s to the filename specified in the
        constructor."""
        self.checkParams()
        if self.filename == '':
            raise IOError('filename not specified')

        try:
            file = StringIO(s)
            if self.mode == '':  # mode='': ASCII mode
                self.ftp.storlines('STOR %s' % self.path, file)  # type:ignore
            else:  # mode='b': binary mode
                self.ftp.storbinary('STOR %s' % self.path, file)  # type:ignore
            file.close()
        except Exception:
            exception, msg, tb = sys.exc_info()
            raise IOError(msg)
    #@+node:edream.110203113231.886: *3* Utilities
    #@+node:edream.110203113231.887: *4* seek
    def seek(self, offset=0):
        self.currentLine = 0  # we don't support fancy seeking via FTP
    #@+node:edream.110203113231.888: *4* flush
    def flush(self):
        pass  # no fancy stuff here.
    #@+node:edream.110203113231.889: *4* dir
    def dir(self, path=None):
        """Issue a LIST command passing the specified argument and return output as a string."""
        s: list = []

        if path is None:
            path = self.dirname
        try:
            listcmd = 'LIST %s' % path
            self.ftp.retrlines(listcmd.rstrip(), s.append)
            return '\n'.join(s)
        except Exception:
            exception, msg, tb = sys.exc_info()
            raise IOError(msg)
    #@+node:edream.110203113231.890: *4* exists
    def exists(self, path=None):
        """
        Return True if the specified path exists.
        If path is omitted, the current file name is tried.
        """
        if path is None:
            path = self.filename
        s = self.dir(path)
        # return s.lower().find('no such file') == -1
        return 'no such file' not in s.lower()
    #@+node:edream.110203113231.891: *4* checkParams
    def checkParams(self):
        if self.mode not in ('', 'b'):
            raise IOError('invalid mode: %s' % self.mode)
        if not self.isConnectionOpen:
            raise IOError('ftp connection closed')
    #@+node:edream.110203113231.892: *3* close
    def close(self):
        """Close an existing FTPurl connection."""
        try:
            self.ftp.quit()
        except Exception:
            self.ftp.close()
        del self.ftp
        self.isConnectionOpen = 0
    #@-others
#@+node:edream.110203113231.893: ** enable/disable_body
# Alas, these do not seem to work on XP:
# disabling the body text _permanently_ stops the cursor from blinking.

def enable_body(body):
    global insertOnTime, insertOffTime
    if body.cget("state") == "disabled":
        try:
            g.es("enable")
            g.pr(insertOffTime, insertOnTime)
            body.configure(state="normal")
            body.configure(insertontime=insertOnTime, insertofftime=insertOffTime)
        except Exception:
            g.es_exception()

def disable_body(body):
    global insertOnTime, insertOffTime
    if body.cget("state") == "normal":
        try:
            g.es("disable")
            insertOnTime = body.cget("insertontime")
            insertOffTime = body.cget("insertofftime")
            g.pr(insertOffTime, insertOnTime)
            body.configure(state="disabled")
        except Exception:
            g.es_exception()
#@+node:edream.110203113231.894: ** insert_read_only_node (FTP version)
# Sets p's body text from the file with the given name.
# Returns True if the body text changed.
def insert_read_only_node(c, p, name):
    if name == "":
        name = g.app.gui.runOpenFileDialog(c,
            title="Open",
            filetypes=[("All files", "*")],
        )
        p.h = "@read-only %s" % name
        c.redraw()
    parse = urlparse(name)  # type:ignore
    f: Any
    try:
        if parse[0] == 'ftp':
            f = FTPurl(name)  # FTP URL
        elif parse[0] == 'http':
            f = urlopen(name)  # HTTP URL
        else:
            f = open(name, "r")  # local file
        g.es("..." + name)
        new = f.read()
        f.close()
    except IOError:  # as msg:
        p.b = ""  # Clear the body text.
        return True  # Mark the node as changed.

    ext = os.path.splitext(parse[2])[1]
    if ext.lower() in ['.htm', '.html']:
        #@+<< convert HTML to text >>
        #@+node:edream.110203113231.895: *3* << convert HTML to text >>
        fh = StringIO()
        fmt = AbstractFormatter(DumbWriter(fh))
        # the parser stores parsed data into fh (file-like handle)
        parser = HTMLParser(fmt)  # type:ignore

        # send the HTML text to the parser
        parser.feed(new)
        parser.close()

        # now replace the old string with the parsed text
        new = fh.getvalue()
        fh.close()

        # finally, get the list of hyperlinks and append to the end of the text
        hyperlinks = parser.anchorlist
        numlinks = len(hyperlinks)
        if numlinks > 0:
            hyperlist = ['\n\n--Hyperlink list follows--']
            for i in range(numlinks):
                hyperlist.append("\n[%d]: %s" % (i + 1, hyperlinks[i]))  # 3/26/03: was i.
            new = new + ''.join(hyperlist)
        #@-<< convert HTML to text >>
    previous = p.b
    p.b = new
    changed = (g.toUnicode(new) != g.toUnicode(previous))
    if changed and previous != "":
        g.es("changed: %s" % name)  # A real change.
    return changed
#@+node:edream.110203113231.896: ** on_open
#  scan the outline and process @read-only nodes.
def on_open(tag, keywords):

    c = keywords.get("c")
    if not c:
        return

    p = c.rootPosition()
    g.blue("scanning for @read-only nodes...")
    while p:
        h = p.h
        if g.match_word(h, 0, "@read-only"):
            changed = insert_read_only_node(c, p, h[11:])
            g.red("changing %s" % p.h)
            if changed:
                if not p.isDirty():
                    p.setDirty()
                if not c.isChanged():
                    c.setChanged()
        p.moveToThreadNext()
    c.redraw()
#@+node:edream.110203113231.897: ** on_bodykey1
# override the body key handler if we are in an @read-only node.

def on_bodykey1(tag, keywords):

    c = keywords.get("c")
    p = keywords.get("p")
    if g.match_word(p.h, 0, "@read-only"):
        # The following code causes problems with scrolling and syntax coloring.
        # Its advantage is that it makes clear that the text can't be changed,
        # but perhaps that is obvious anyway...
        if 0:  # Davide Salomoni requests that this code be eliminated.
            # An @read-only node: do not change its text.
            w = c.frame.body.wrapper
            w.delete(0, w.getLastIndex())
            w.insert(0, p.b)
        return 1  # Override the body key event handler.
    return None
#@+node:edream.110203113231.898: ** on_headkey2
# update the body text when we press enter

def on_headkey2(tag, keywords):

    c = keywords.get("c")
    p = keywords.get("p")
    h = p.h
    ch = keywords.get("ch")
    if ch in ('\n', '\r') and g.match_word(h, 0, "@read-only"):
        # on-the-fly update of @read-only directives
        changed = insert_read_only_node(c, p, h[11:])
        if changed:
            c.setChanged()
        else:
            c.clearChanged()
#@+node:edream.110203113231.899: ** on_select1
def on_select1(tag, keywords):

    # Doesn't work: the cursor doesn't start blinking.
    # Enable the body text so select will work properly.
    c = keywords.get("c")
    enable_body(c.frame.body)
#@+node:edream.110203113231.900: ** on_select2
def on_select2(tag, keywords):

    c = keywords.get("c")

    if g.match_word(c.p.h, 0, "@read-only"):
        disable_body(c.frame.body)
    else:
        enable_body(c.frame.body)
#@-others
#@@language python
#@@tabwidth -4
#@-leo
