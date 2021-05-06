#@+leo-ver=5-thin
#@+node:EKR.20040517075715.12: * @file ../plugins/xemacs.py
#@+<< docstring >>
#@+node:ekr.20101112195628.5434: ** << docstring >> (xemacs.py)
''' Allows you to edit nodes in emacs/xemacs.

Provides the emacs-open-node command which passes the body
text of the node to emacs.

You may edit the node in the emacs buffer and changes will
appear in Leo.

'''
#@-<< docstring >>

# Initial version: http://www.cs.mu.oz.au/~markn/leo/external_editors.leo
# Edited by EKR.

#@+<< imports >>
#@+node:ekr.20050218024153: ** << imports >> (xemacs.py)
import os
import sys
from leo.core import leoGlobals as g
#@-<< imports >>

# Full path of emacsclient executable. We need the full path as spawnlp
# is not yet implemented in leoCommands.py
if sys.platform == "win32":
    # This path must not contain blanks in XP.  Sheesh.
    _emacs_cmd = r"c:\XEmacs\XEmacs-21.4.21\i586-pc-win32\xemacs.exe"
elif sys.platform.startswith("linux"):
    clients = ["gnuclient", "emacsclient", "xemacs"]
    _emacs_cmd = ""
    for client in clients:
        path = "/usr/bin/" + client
        if os.path.exists(path):
            _emacs_cmd = path
            break
    if not _emacs_cmd:
        # print >> sys.stderr, "Unable to locate a usable version of *Emacs"
        print("Unable to locate a usable version of *Emacs")
else:
    _emacs_cmd = "/Applications/Emacs.app/Contents/MacOS/bin/emacsclient"

#@+others
#@+node:ekr.20050218023308: ** xemacs.init
def init():
    '''Return True if the plugin has loaded successfully.'''
    ok = not g.unitTesting
    if ok:
        g.plugin_signon(__name__)
    return ok
#@+node:ekr.20050313071202: ** xemacs.open_in_emacs
contextmenu_message_given = False

def open_in_emacs(tag, keywords):
    c = keywords.get('c')
    p = keywords.get('p')
    if c:
        return open_in_emacs_helper(c, p or c.p)
    return None
#@+node:ekr.20120315101404.9748: ** xemacs.open_in_emacs_helper
def open_in_emacs_helper(c, p):
    global contextmenu_message_given
    v = p.v
    # Load contextmenu plugin if required.
    contextMenu = g.loadOnePlugin('contextmenu.py', verbose=True)
    if not contextMenu:
        if not contextmenu_message_given:
            contextmenu_message_given = True
            g.trace('can not load contextmenu.py')
        return
    # Search the open-files list for a file corresponding to v.
    efc = g.app.externalFilesController
    path = efc and efc.find_path_for_node(p)
    emacs_cmd = c.config.getString('xemacs-exe') or _emacs_cmd
        # 2010/01/18: found by pylint.
    if (
        not path or
        not g.os_path_exists(path) or
        not hasattr(v, 'OpenWithOldBody') or
        v.b != v.OpenWithOldBody
    ):
        # Open a new temp file.
        if path:
            # Don't do this: it prevents efc from reopening paths.
                # efc = g.app.externalFilesController
                # if efc: efc.forget_path(path)
            os.remove(path)
            os.system(emacs_cmd)
        v.OpenWithOldBody = v.b # Remember the old contents
        # open the node in emacs (note the space after _emacs_cmd)
        # data = "os.spawnl", emacs_cmd, None
        d = {'kind': 'os.spawnl', 'args': [emacs_cmd], 'ext': None}
        c.openWith(d=d)
    else:
        # Reopen the old temp file.
        os.system(emacs_cmd)
#@+node:ekr.20120315101404.9747: ** g.command('emacs-open-node')
@g.command('emacs-open-node')
def open_in_emacs_command(event):
    """ Open current node in (x)emacs

    Provied by xemacs.py plugin
    """
    c = event.get('c')
    if c:
        open_in_emacs_helper(c, c.p)
#@-others
#@@language python
#@@tabwidth -4
#@-leo
