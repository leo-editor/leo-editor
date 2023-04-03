#@+leo-ver=5-thin
#@+node:EKR.20040517075715.10: * @file ../plugins/vim.py
#@+<< docstring >>
#@+node:ekr.20050226184411: ** << docstring >>
"""
#@@language rest

Enables two-way communication with gVim (recommended) or Vim.

Commands
--------

``vim-open-file``
    Opens the nearest ancestor @file or @clean node in vim. Leo will update the
    file in the outline when you save the file in vim.

``vim-open-node``
    Opens the selected node in vim. Leo will update the node in the outline when
    you save the file in vim.

Installation
------------

Set the ``vim_cmd`` and ``vim_exe`` settings as shown below.

Alternatively, you can put gvim.exe is on your PATH.

Settings
--------

``@string vim_cmd``
    The command to execute to start gvim. Something like::

        <path-to-gvim>/gvim --servername LEO

``@string vim_exe``
    The path to the gvim executable.

``vim_plugin_uses_tab_feature``
    True: Leo will put the node or file in a Vim tab card.

"""
#@-<< docstring >>

# Contributed by Andrea Galimberti.
# Edited by Felix Breuer, TL, VMV and EKR.

#@+<< documentation from Jim Sizelove >>
#@+node:ekr.20050909102921: ** << documentation from Jim Sizelove >>
#@+at
#@@language rest
#@@wrap
#
# I was trying to get Leo to work more effectively with Vim, my editor of choice.
# To do so, I made several changes to Leo which (I believe) make it work better.
#
# After much exploring and trying various things, I made a change to the os.spawnv
# section of the openWith function in leoCommands.py. This added line seems to
# prevent the "weird error message on first open of Vim." (vim.py, line 32) when
# opening Vim with os.spawnv.
#
# os.spawnv needs the command it is calling as the first argument in the args list
# in addition, so the command actually shows twice in the total args to os.spawnv.
# For example::
#
#     os.spawnv(os.P_NOWAIT, "C:/Program Files/Vim/vim63/gvim.exe",
#         ["gvim.exe", "--servername", "LEO", "--remote", "foo.txt"])
#
# If the call is made without the command-name as the first item in the list of
# args, like so::
#
#     os.spawnv(os.P_NOWAIT, "C:/Program Files/Vim/vim63/gvim.exe",
#         ["--servername", "LEO", "--remote", "foo.txt"])
#
# an error message pops up::
#
#     E247: no registered server named "GVIM": Send failed.  Trying to execute locally
#
# This message means that gVim is not looking for a server named "LEO", which
# presumably the user has already opened with the command "gvim --servername LEO".
# Instead it is looking for a server named "GVIM", and not finding it, opens the
# files "foo.txt" and "LEO" (notice that it didn't catch the "--servername"
# argument and thinks that "LEO" is the name of a new file to create) in two
# buffers in a local copy of gVim. Now, if the command is::
#
#     os.spawnv(
#         os.P_NOWAIT, "C:/Program Files/Vim/vim63/gvim.exe",
#         ["gvim.exe", "--servername", "LEO", "--remote", "foo.txt"])
#
# Everything works great, as long as the user doesn't close the gVim window. If
# the user has closed the gVim window, then tries to open a node in Vim, they will
# see this error message::
#
#     E247: no registered server named "LEO": Send failed.
#
# Trying to execute locally If you use the ``--remote-silent`` argument, gVim will
# start the LEO server without the error message.
#
# You can see which servers gVim has running by typing the following at the
# command prompt::
#
#     vim --serverlist
#
# The rest of my changes have to do with using the subprocess module instead of
# the os.system, and various os.spawn* calls. I find subprocess easier to
# understand, and it is fairly simple to use for the most common kinds of process
# calls, but is capable of all the variations you may need. It is designed to
# replace all the os.system, os.spawn, and popen calls. It is available in Python
# 2.4.
#
# So I added some lines to use subprocess in the OpenWith plugin and the Vim
# plugin.
#
# I also have added a table in the "create_open_with_menu" function that makes use
# of the various editors I have used at times. Most of those editors are called
# with subprocess.Popen.
#@-<< documentation from Jim Sizelove >>
#@+<< imports >>
#@+node:ekr.20050226184411.2: ** << imports >>
import os
import subprocess
import sys
from leo.core import leoGlobals as g
#@-<< imports >>

# This command is used to communicate with the vim server. If you use gvim
# you can leave the command as is, you do not need to change it to "gvim ..."
# New in version 1.10 of this plugin: these are emergency defaults only.
# They are typically overridden by the corresponding 'vim_cmd' and 'vim_exe' settings in
# leoSettings.leo or individual .leo files.
if sys.platform == 'win32':
    # Works on XP if you have gvim on PATH
    _vim_cmd = "gvim --servername LEO"
    _vim_exe = "gvim"
elif sys.platform == 'darwin':
    _vim_cmd = "/Applications/gvim.app/Contents/MacOS/gvim --servername LEO"
    _vim_exe = "gvim"
else:
    _vim_cmd = "gvim --servername LEO"
    _vim_exe = "gvim"
# Global message flags.
contextmenu_message_given = False
locationMessageGiven = False
#@+others
#@+node:ekr.20050226184624: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    ok = not g.unitTesting  # Don't conflict with xemacs plugin.
    if ok:
        # Enable the os.system call if you want to
        # start a (g)vim server when Leo starts.
        if 0:
            os.system(_vim_cmd)
        g.plugin_signon(__name__)
    return ok
#@+node:ekr.20150326150910.1: ** g.command('vim-open-file')
@g.command('vim-open-file')
def vim_open_file_command(event):
    """vim.py: Open the entire file in (g)vim."""
    c = event.get('c')
    if c:
        VimCommander(c, entire_file=True)
#@+node:ekr.20120315101404.9745: ** g.command('vim-open-node')
@g.command('vim-open-node')
def vim_open_node_command(event):
    """vim.py: open the selected node in (g)vim."""
    c = event.get('c')
    if c:
        VimCommander(c, entire_file=False)
#@+node:ekr.20150326153420.1: ** class VimCommander
class VimCommander:
    """A class implementing the vim plugin."""
    #@+others
    #@+node:ekr.20150326155343.1: *3*  vim.ctor
    def __init__(self, c, entire_file):
        """Ctor for the VimCommander class."""
        self.c = c
        self.entire_file = entire_file
        # compute settings.
        getBool, getString = c.config.getBool, c.config.getString
        self.open_url_nodes = getBool('vim-plugin-opens-url-nodes')
        self.trace = False or getBool('vim-plugin-trace')
        self.uses_tab = getBool('vim-plugin-uses-tab-feature')
        self.vim_cmd = getString('vim-cmd') or _vim_cmd
        self.vim_exe = getString('vim-exe') or _vim_exe
        # Give messages.
        global locationMessageGiven
        if self.trace and not locationMessageGiven:
            locationMessageGiven = True
            print('vim_cmd: %s' % self.vim_cmd)
            print('vim_exe: %s' % self.vim_exe)
        self.open_in_vim()
    #@+node:ekr.20150326183310.1: *3* vim.error
    def error(self, s):
        """Report an error."""
        g.es_print(s, color='red')
    #@+node:ekr.20120315101404.9746: *3* vim.open_in_vim & helpers
    def open_in_vim(self):
        """Open p in vim, or the entire enclosing file if entire_file is True."""
        p = self.c.p
        if not self.check_args():
            return
        root = self.find_root(p) if self.entire_file else p
        if not root:
            return
        path = self.find_path_for_node(root)
        if path and self.should_open_old_file(path, root):
            cmd = self.vim_cmd + "--remote-send '<C-\\><C-N>:e " + path + "<CR>'"
            if self.trace:
                g.trace('os.system(%s)' % cmd)
            os.system(cmd)
        else:
            # Open a new temp file.
            if path:
                self.forget_path(path)
            self.open_file(root)
    #@+node:ekr.20150326183613.1: *4* vim.check_args & helper
    def check_args(self):
        """Return True of basic checks pass."""
        p = self.c.p
        contextMenu = self.load_context_menu()
        if not contextMenu:
            return False
        if not self.open_url_nodes and p.h.startswith('@url'):
            return False
        return True
    #@+node:ekr.20150326154203.1: *5* vim.load_context_menu
    def load_context_menu(self):
        """Load the contextmenu plugin."""
        global contextmenu_message_given
        contextMenu = g.loadOnePlugin('contextmenu.py', verbose=True)
        if not contextMenu and not contextmenu_message_given:
            contextmenu_message_given = True
            self.error('can not load contextmenu.py')
        return contextMenu
    #@+node:ekr.20150326180515.1: *4* vim.find_path_for_node
    def find_path_for_node(self, p):
        """Search the open-files list for a file corresponding to p."""
        efc = g.app.externalFilesController
        path = efc.find_path_for_node(p)
        return path
    #@+node:ekr.20150326173414.1: *4* vim.find_root
    def find_root(self, p):
        """Return the nearest ancestor @auto or @clean node."""
        assert self.entire_file
        for p2 in p.self_and_parents():
            if p2.isAnyAtFileNode():
                return p2
        self.error('no parent @auto or @clean node: %s' % p.h)
        return None
    #@+node:ekr.20150326173301.1: *4* vim.forget_path
    def forget_path(self, path):
        """
        Stop handling the path:
        - Remove the path from the list of open-with files.
        - Send a command to vim telling it to close the path.
        """
        assert path
        # Don't do this: it prevents efc from reopening paths.
            # efc = g.app.externalFilesController
            # if efc: efc.forget_path(path)
        if 0:  # Dubious.
            if g.os_path_exists(path):
                os.remove(path)
        cmd = self.vim_cmd + "--remote-send '<C-\\><C-N>:bd " + path + "<CR>'"
        os.system(cmd)
    #@+node:ekr.20150326181247.1: *4* vim.get_cursor_arg
    def get_cursor_arg(self):
        """Compute the cursor argument for vim."""
        wrapper = self.c.frame.body.wrapper
        s = wrapper.getAllText()
        ins = wrapper.getInsertPoint()
        row, col = g.convertPythonIndexToRowCol(s, ins)
        # This is an Ex command, not a normal Vim command.  See:
        # http://vimdoc.sourceforge.net/htmldoc/remote.html
        # and
        # http://pubs.opengroup.org/onlinepubs/9699919799/utilities/ex.html#tag_20_40_13_02
        return "+" + str(row + 1)
    #@+node:ekr.20150326180928.1: *4* vim.open_file
    def open_file(self, root):
        """Open the the file in vim using c.openWith."""
        c = self.c
        efc = g.app.externalFilesController
        # Common arguments.
        tab_arg = "-tab" if self.uses_tab else ""
        remote_arg = "--remote" + tab_arg + "-silent"
        args = [self.vim_exe, "--servername", "LEO", remote_arg]  # No cursor arg.
        if self.entire_file:
            # vim-open-file
            args.append('+0')  # Go to first line of the file. This is an Ex command.
            assert root.isAnyAtFileNode(), root
            # Use os.path.normpath to give system separators.
            fn = os.path.normpath(c.fullPath(root))  # #1914.
        else:
            # vim-open-node
            # Set the cursor position to the current line in the node.
            args.append(self.get_cursor_arg())
            ext = 'txt'
            fn = efc.create_temp_file(c, ext, c.p)
        c_arg = '%s %s' % (' '.join(args), fn)
        command = 'subprocess.Popen(%s,shell=True)' % c_arg
        try:
            subprocess.Popen(c_arg, shell=True)
        except OSError:
            g.es_print(command)
            g.es_exception()
    #@+node:ekr.20150326173000.1: *4* vim.should_open_old_file
    def should_open_old_file(self, path, root):
        """Return True if we should open the old temp file."""
        v = root.v
        return (
            path and g.os_path_exists(path) and
            hasattr(v.b, '_vim_old_body') and v.b == v._vim_old_body
        )
    #@+node:ekr.20150326175258.1: *3* vim.write_root (not used)
    def write_root(self, root):
        """Return the concatenation of all bodies in p's tree."""
        result = []
        for p in root.self_and_subtree():
            s = p.b
            result.append(s if s.endswith('\n') else s.rstrip() + '\n')
        return ''.join(result)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
