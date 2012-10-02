#@+leo-ver=5-thin
#@+node:EKR.20040517075715.10: * @file vim.py
#@+<< docstring >>
#@+node:ekr.20050226184411: ** << docstring >>
''' Enables two-way communication with VIM.

This plugin provides the ``vim-open-node`` command, which opens the
selected node in vim. This *supersedes* the old way of opening nodes by
double-clicking the icon box.

Commands
--------

The **vim-open-node** command opens the selected node in vim. Leo will
update the node in the outline when you save the file in vim.

Installation
------------

Enable this plugin as usual and set the ``vim_cmd`` and ``vim_exe``
settings as shown below. Alternatively, you can ensure that gvim.exe is on
your PATH. gvim is recommended, not the basic console vim.

Settings
--------

**@string vim_cmd** (Important!): The command to execute to start gvim.
Something like::
    
    <path-to-gvim>/gvim --servername LEO

**@string vim_exe** (Important!): The path to the gvim executable.

**vim_plugin_positions_cursor**: Leo will put Vim cursor at same location as
Leo cursor in file.

**vim_plugin_uses_tab_feature**: Leo will put node in a Vim tab card.

'''
#@-<< docstring >>

#@@language python
#@@tabwidth -4

__version__ = "2.0" # EKR
#@+<< version history >>
#@+node:ekr.20050226184411.1: ** << version history >>
#@@killcolor

#@+at
# 
# Contributed by Andrea Galimberti.
# Edited by Felix Breuer.
# 
# 1.5 EKR:
#     - Added new sections.
#     - Move most comments into docstring.
#     - Added useDoubleClick variable.
#     - Added init function.
#     - Init _vim_cmd depending on sys.platform.
# 1.6 EKR:
#     - Use keywords to get c, not g.top().
#     - Don't use during unit testing: prefer xemacs instead.
#     - Added _vim_exe
#     - Use "os.spawnv" instead of os.system.
#     - Simplified the search of g.app.openWithFiles.
#     - Fixed bug in open_in_vim: hanged v.bodyString to v.bodyString()
# 1.7 EKR: Excellent new code by Jim Sizelove solves weird message on first open of vim.
# 1.8 EKR: Set subprocess = None if import fails.
# 1.9 EKR:
#     - Document how install subproces, and use g.importExtension to import subprocess.
#     - Import subprocess with g.importExtension.
# 1.10 EKR:
#     - Support 'vim_cmd' and 'vim_exe' settings.
#     - These override the default _vim_cmd and _vim_exe settings.
# 1.11 EKR: Emergency default for window is now the default location: c:\Program Files\vim\vim63
# 1.12 EKR:
#     - Added emergency default for 'darwin'.
#     - Corrected the call to openWith.  It must now use data=data due to a new event param.
# 1.13 EKR: The docstring now states that the open_with plugin must be enabled for this to work.
# 1.14 EKR: Emphasized that the open_with plugin must be enabled.
# 1.15 EKR: Don't open @url nodes in vim if @bool vim_plugin_opens_url_nodes setting is False.
# 1.16 TL: open_in_vim modifications
#     - support file open in gVim at same line number as Leo cursor location
#     - support file open in a gVim tab (see also mod_tempfname.py)
# 1.17 EKR: Give a location message to help with settings.
# 1.18 VMV:
#     - Use gvim on Linux too, emergency default on Windows doesn't have explicit path
#     - Works when subprocess.Popen(shell=True)
# 2.0 EKR: Use *only* the vim-open-node command.  Do not pollute click handlers.
#@-<< version history >>
#@+<< documentation from Jim Sizelove >>
#@+node:ekr.20050909102921: ** << documentation from Jim Sizelove >>
#@@nocolor

#@+at I was trying to get Leo to work more effectively with Vim, my editor of choice.
# To do so, I made several changes to Leo which (I believe) make it work better.
# 
# After much exploring and trying various things, I made a change to the os.spawnv
# section of the openWith function in leoCommands.py. This added line seems to
# prevent the "weird error message on first open of Vim." (vim.py, line 32) when
# opening Vim with os.spawnv.
# 
# os.spawnv needs the command it is calling as the first argument in the args list
# in addition, so the command actually shows twice in the total args to os.spawnv,
# e.g.::
#     os.spawnv(os.P_NOWAIT, "C:/Program Files/Vim/vim63/gvim.exe",
#         ["gvim.exe", "--servername", "LEO", "--remote", "foo.txt"])
# If the call is made without the command-name as the first item in the list of
# args, like so::
#     os.spawnv(os.P_NOWAIT, "C:/Program Files/Vim/vim63/gvim.exe",
#         ["--servername", "LEO", "--remote", "foo.txt"])
# 
# an error message pops up::
#     E247: no registered server named "GVIM": Send failed.  Trying to execute locally
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
# everything works great, as long as the user doesn't close the gVim window. If
# the user has closed the gVim window, then tries to open a node in Vim, they will
# see this error message::
# 
#     E247: no registered server named "LEO": Send failed.
# 
# Trying to execute locally If you use the "--remote-silent" argument, gVim will
# start the LEO server without the error message.
# 
# One other comment:  you can see which servers gVim has running by typing::
# 
#     vim --serverlist
# 
# at the command prompt.
# 
# The rest of my changes have to do with using the subprocess module instead of
# the os.system, and various os.spawn* calls. I find subprocess easier to
# understand, and it is fairly simple to use for the most common kinds of process
# calls, but is capable of all the variations you may need. It is designed to
# replace all the os.system, os.spawn*, and popen* calls. It is available in
# Python 2.4.
# 
# So I added some lines to use subprocess in the OpenWith plugin and the Vim plugin.
# 
# I also have added a table in the "create_open_with_menu" function that makes use of the various editors I have used at times.  Most of those editors are called with subprocess.Popen.
#@-<< documentation from Jim Sizelove >>
#@+<< imports >>
#@+node:ekr.20050226184411.2: ** << imports >>
import leo.core.leoGlobals as g

import os
import sys
#@-<< imports >>

# This command is used to communicate with the vim server. If you use gvim
# you can leave the command as is, you do not need to change it to "gvim ..."

# New in version 1.10 of these plugin: these are emergency defaults only.
# They are typically overridden by the corresponding 'vim_cmd' and 'vim_exe' settings in
# leoSettings.leo or individual .leo files.

if sys.platform == 'win32':
    # Works on XP if you have gvim on PATH
    _vim_cmd = r"gvim --servername LEO"
    _vim_exe = r"gvim"
elif sys.platform == 'darwin':
    _vim_cmd = "/Applications/gvim.app/Contents/MacOS/gvim --servername LEO"
    _vim_exe = "gvim"
else: 
    _vim_cmd = "gvim --servername LEO"
    _vim_exe = "gvim"

locationMessageGiven = False

#@+others
#@+node:ekr.20050226184624: ** init
def init ():

    ok = not g.app.unitTesting # Don't conflict with xemacs plugin.

    if ok:
        # print ('vim.py enabled')
        # Register the handlers...

        # event = 'open2'
        # g.registerHandler(event,on_open_window)

        # Enable the os.system call if you want to
        # start a (g)vim server when Leo starts.
        if 0:
            os.system(_vim_cmd)

        g.plugin_signon(__name__)

    return ok
#@+node:ekr.20120315101404.9745: ** g.command('vim-open-node')
@g.command('vim-open-node')
def open_in_vim_command(event):

    """ Open current node in (g)vim

        Provied by vim.py plugin
        """
    c = event.get('c')
    if c:
        open_in_vim_helper(c)
#@+node:ekr.20120315101404.9746: *3* open_in_vim_helper
contextmenu_message_given = False

def open_in_vim_helper (c):
    
    p = c.p
    v = p.v

    # Load contextmenu plugin if required.
    contextMenu = g.loadOnePlugin('contextmenu.py',verbose=True)
    if not contextMenu:
        if not contextmenu_message_given:
            contextmenu_message_given = True
            g.trace('can not load contextmenu.py')
        return

    if p.h.find('file-ref') == 1: # Must be at 2nd position
        return

    #URL nodes
    openURLNodes = c.config.getBool('vim_plugin_opens_url_nodes')
    if not openURLNodes and p.h.startswith('@url'):
        return # Avoid conflicts with @url nodes.

    vim_cmd = c.config.getString('vim_cmd') or _vim_cmd
    vim_exe = c.config.getString('vim_exe') or _vim_exe

    global locationMessageGiven

    if not locationMessageGiven:
        locationMessageGiven = True
        print('vim_cmd: %s' % vim_cmd)
        print('vim_exe: %s' % vim_exe)

    #Cursor positioning
    Lnum = ""
    if c.config.getBool('vim_plugin_positions_cursor'):    
        #Line number - start at same line as Leo cursor
        #  get node's body text
        bodyCtrl = c.frame.body.bodyCtrl
        s = bodyCtrl.getAllText()    
        #  Get cursors row & column number
        index = bodyCtrl.getInsertPoint()
        row,col = g.convertPythonIndexToRowCol(s,index)
        #  Build gVim command line parameter for setting cursor row
        Lnum = "+" + str(row + 1)

    #Vim's tab card stack
    useTabs = ""

    if c.config.getBool('vim_plugin_uses_tab_feature'):    
        useTabs = "-tab"

    # Search g.app.openWithFiles for a file corresponding to v.
    for d in g.app.openWithFiles:
        if d.get('v') == id(v):
            path = d.get('path','') ; break
    else: path = ''

    # if the body has changed we need to open a new 
    # temp file containing the new body in vim
    if (
        not g.os_path_exists(path) or 
        not hasattr(v,'OpenWithOldBody') or
        v.b != v.OpenWithOldBody
    ):
        # Open a new temp file.
        if path:
            # Remove the old file and the entry in g.app.openWithFiles.
            os.remove(path)
            g.app.openWithFiles = [d for d in g.app.openWithFiles if d.get('path') != path]
            os.system(vim_cmd+"--remote-send '<C-\\><C-N>:bd "+path+"<CR>'")

        v.OpenWithOldBody=v.b # Remember the previous contents.
    
        # New code by Jim Sizemore. TL: added support for gVim tabs.
        args = [vim_exe,"--servername","LEO","--remote"+useTabs+"-silent",Lnum]
        d = {'kind':'subprocess.Popen','args':args,'ext':None}
        c.openWith(d=d)
    else:
        # Reopen the old temp file.
        os.system(vim_cmd+"--remote-send '<C-\\><C-N>:e "+path+"<CR>'")
#@-others
#@-leo
