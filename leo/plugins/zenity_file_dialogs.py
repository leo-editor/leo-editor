#@+leo-ver=5-thin
#@+node:ekr.20101110095202.5882: * @file ../plugins/zenity_file_dialogs.py
""" Replaces the tk file dialogs on Linux with external
calls to the zenity gtk dialog package.

This plugin is more a proof of concept demo than
a useful tool.  The dialogs presented do not take
filters and starting folders can not be specified.

Despite this, some Linux users might prefer it to the
tk dialogs.

"""
import subprocess
from typing import Optional
from leo.core import leoGlobals as g
from leo.core import leoPlugins
trace = False
#@+others
#@+node:ekr.20101110095557.5886: ** testForZenity
def testForZenity():

    command = ['which', 'zenity']
    o = subprocess.Popen(command, stdout=subprocess.PIPE)
    o.wait()
    o.communicate()[0].rstrip()
    ret = o.returncode
    return not ret
#@+node:ekr.20101110095557.5888: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    if g.unitTesting:
        return False
    ok = testForZenity()
    if ok:
        leoPlugins.registerHandler('start2', onStart2)
        g.plugin_signon(__name__)
    else:
        g.trace('failed to load zenity')
    return ok
#@+node:ekr.20101110095557.5890: ** onStart2
def onStart2(tag, keywords):
    """Replace tkfile open/save method with external calls to zenity."""
    g.funcToMethod(runOpenFileDialog, g.app.gui)
    g.funcToMethod(runSaveFileDialog, g.app.gui)
#@+node:ekr.20101110095557.5892: ** callZenity
def callZenity(title: str, save: bool = False, test: bool = False) -> Optional[bytes]:

    command = ['zenity', '--file-selection', '--title=%s' % title]
    if save:
        command.append('--save')
    # if multiple:
        # command.append('--multiple')
    o = subprocess.Popen(command, stdout=subprocess.PIPE)
    o.wait()
    filename = o.communicate()[0].rstrip()
    ret = o.returncode
    if ret:
        return None
    # if multiple:
        # return filename.split('|')  # type:ignore
    return filename
#@+node:ekr.20101110095557.5894: ** runOpenFileDialog
def runOpenFileDialog(
    title,
    *,
    filetypes: list[tuple[str, str]] = None,
    defaultextension=None,
):
    """Call zenity's open file(s) dialog."""
    # initialdir = g.app.globalOpenDir or g.os_path_abspath(os.getcwd())
    return callZenity(title)
#@+node:ekr.20101110095557.5896: ** runSaveFileDialog
def runSaveFileDialog(
    title=None,
    *,
    filetypes: list[tuple[str, str]] = None,
    defaultextension=None,
) -> bytes:
    """Call zenity's save file dialog."""
    # initialdir=g.app.globalOpenDir or g.os_path_abspath(os.getcwd())
    return callZenity(title, save=True)
#@-others
#@@language python
#@@tabwidth -4
#@-leo
