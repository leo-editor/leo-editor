#@+leo-ver=5-thin
#@+node:ekr.20090701111504.5294: * @file ../plugins/contextmenu.py
#@+<< contextmenu docstring >>
#@+node:ville.20090630210947.5460: ** << contextmenu docstring >>
""" Defines various useful actions for context menus (Qt only).

Examples are:

- Edit in $EDITOR
- Edit @thin node in $EDITOR (remember to do "refresh" after this!)
- Refresh @thin node from disk (e.g. after editing it in external editor)
- Go to clone

A ``context-menu-open`` command is defined to allow opening the
tree context menu from the keyboard.

Here's an example on how to implement your own context menu items
in your plugins::

    def nextclone_rclick(c: Cmdr, p: Position, menu: Wrapper) -> None:
        \""" Go to next clone\"""

        # only show the item if you are on a clone
        # this is what makes this "context sensitive"
        if not p.isCloned():
            return

        def nextclone_rclick_cb() -> None:
            c.goToNextClone()

        # 'menu' is a QMenu instance that was created by Leo
        # in response to right click on tree item

        action = menu.addAction("Go to clone")
        action.connect(action, QtCore.SIGNAL("triggered()"), nextclone_rclick_cb)

And call this in your plugin *once*::

    g.tree_popup_handlers.append(nextclone_rclick)

"""
#@-<< contextmenu docstring >>
# Original version by Ville M. Vainio.
#@+<< contextmenu imports & annotations >>
#@+node:ekr.20220828123814.1: ** << contextmenu imports & annotations >>
from __future__ import annotations
from collections.abc import Callable
import os
from typing import Any, TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.core.leoQt import QtCore
from leo.core.leoGui import LeoKeyEvent

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position
    from leo.plugins.qt_text import QTextEditWrapper as Wrapper

# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.
#@-<< contextmenu imports & annotations >>

# Globals
inited = False

#@+others
#@+node:ekr.20200304124610.1: ** Commands
#@+node:ville.20090701224704.9805: *3* 'cm-external-editor'
# cm is 'contextmenu' prefix
@g.command('cm-external-editor')
def cm_external_editor(event: LeoKeyEvent) -> None:
    """ Open node in external editor

    Set LEO_EDITOR/EDITOR environment variable to get the editor you want.
    """
    c = event['c']

    editor, _ = getEditor(c)

    if not editor.startswith('"'):
        editor = '"' + editor
    if not editor.endswith('"'):
        editor = editor + '"'

    d = {'kind': 'subprocess.Popen', 'args': [editor], 'ext': None}
    c.openWith(d=d)
#@+node:tbrown.20121123075838.19937: *3* 'context_menu_open'
@g.command('context-menu-open')
def context_menu_open(event: LeoKeyEvent) -> None:
    """Provide a command for key binding to open the context menu"""
    event.c.frame.tree.onContextMenu(QtCore.QPoint(0, 0))
#@+node:ekr.20200304124723.1: ** startup
#@+node:ville.20090630210947.5463: *3*  init (contextmenu.py)
def init() -> bool:
    """Return True if the plugin has loaded successfully."""
    global inited
    if g.app.gui.guiName() != "qt":
        return False
    g.plugin_signon(__name__)
    # just run once
    if not inited:
        inited = True
        install_handlers()
    return True
#@+node:ville.20090630210947.10189: *3* install_handlers (contextmenu.py)
def install_handlers() -> None:
    """ Install all the wanted handlers (menu creators) """
    handlers = [
        # Add user-specified items first.
        configuredcommands_rclick,
        # Add the rest...
        openwith_rclick,
        refresh_rclick,
        editnode_rclick,
        nextclone_rclick,
        marknodes_rclick,
        # deletenodes_rclick,
        openurl_rclick,
        pylint_rclick,
    ]
    g.tree_popup_handlers.extend(handlers)
#@+node:tom.20210717164029.1: ** getEditor
def getEditor(c: Cmdr) -> tuple[str, str]:
    """Return system's best guess editor quoted.

    RETURNS
    A tuple (editor_path, editor_name_minus_extension)
    """
    editor = g.guessExternalEditor(c)
    if editor:
        basename = os.path.basename(editor).split('.')[0]
        if not editor.startswith('"'):
            editor = '"' + editor
        if not editor.endswith('"'):
            editor = editor + '"'
        return editor, basename
    return "", ""
#@+node:ekr.20140724211116.19255: ** Handlers
#@+node:ville.20091008192104.7691: *3* configuredcommands_rclick
def configuredcommands_rclick(c: Cmdr, p: Position, menu: Wrapper) -> None:
    """Add all items given by @data contextmenu-commands"""
    config = c.config.getData('contextmenu_commands')
    if not config:
        return
    cmds = [z.split(None, 1) for z in config]
    for data in cmds:
        # Leo 6.2: Allows separator.
        if data == ["-"]:
            menu.addSeparator()
            continue
        # Fix #1084
        try:
            command_name, desc = data
        except ValueError:
            g.es_print(f"Bad @data contextmenu_commands entry: {data!r}")
            continue
        desc = desc.strip()
        action = menu.addAction(desc)

        def create_callback(command_name: Any) -> Callable:
            w = g.app.gui.get_focus(c)
            # #2000: The log pane is a confusing special case.
            wrapper = getattr(w, 'wrapper', None) or getattr(w, 'leo_log_wrapper', None)  # #2000.
            key_event = LeoKeyEvent(c, char=None, event=None, binding=None, w=wrapper)
            return lambda: c.doCommandByName(command_name, event=key_event)

        configcmd_rclick_cb = create_callback(command_name)
        action.triggered.connect(configcmd_rclick_cb)

#@+node:tbrown.20091203121808.15818: *3* deletenodes_rclick
def deletenodes_rclick(c: Cmdr, p: Position, menu: Wrapper) -> None:
    """ Delete selected nodes """

    u = c.undoer
    pl = c.getSelectedPositions()
    undoType = 'Delete Node'
    if len(pl) > 1:
        undoType += 's'
    current = p.copy()
    #@+<< define deletenodes_rclick_cb >>
    #@+node:ekr.20140613141207.17673: *4* << define deletenodes_rclick_cb >>
    def deletenodes_rclick_cb() -> None:

        if len(pl) == 1:
            # sometimes this may leave the selected node in a more
            # convenient place than the generalized case below
            c.deleteOutline()  # handles undo, redraw, etc.
            return
        c.endEditing()
        cull = []
        # try and find the best node to select when this is done
        nextviz = []
        tmp = pl[0].copy().moveToVisBack(c)
        if tmp:
            nextviz.append(tmp.v)
        tmp = pl[-1].copy().moveToVisNext(c)
        if tmp:
            nextviz.append(tmp.v)
        for nd in pl:
            cull.append((nd.v, nd.parent().v or None))
        u.beforeChangeGroup(current, undoType)
        for v, vp in cull:
            for pos in c.vnode2allPositions(v):
                if c.positionExists(pos) and pos.parent().v == vp:
                    bunch = u.beforeDeleteNode(pos)
                    pos.doDelete()
                    u.afterDeleteNode(pos, undoType, bunch)
                    c.setChanged()
                    break
        u.afterChangeGroup(current, undoType)
        # move to a node that still exists
        for v in nextviz:
            pos = c.vnode2position(v)
            if c.positionExists(pos):
                c.selectPosition(pos)
                break
        else:
            # c.selectPosition(c.allNodes_iter().next())
            c.selectPosition(c.rootPosition())
        c.redraw()
    #@-<< define deletenodes_rclick_cb >>
    action = menu.addAction("Delete Node")
    action.triggered.connect(deletenodes_rclick_cb)
#@+node:ville.20090701110830.10215: *3* editnode_rclick
def editnode_rclick(c: Cmdr, p: Position, menu: Wrapper) -> None:
    """Provide "edit in EDITOR" context menu item.

    Opens file or node in external editor."""


    editor, basename = getEditor(c)

    def editnode_rclick_cb() -> None:
        d: dict[str, Any] = {'kind': 'subprocess.Popen', 'args': [editor], 'ext': None}
        c.openWith(d=d)

    action = menu.addAction("Edit with " + basename)
    action.triggered.connect(editnode_rclick_cb)
#@+node:ville.20090719202132.5248: *3* marknodes_rclick
def marknodes_rclick(c: Cmdr, p: Position, menu: Wrapper) -> None:
    """ Mark selected nodes """
    pl = c.getSelectedPositions()
    if any(not p.isMarked() for p in pl):

        def marknodes_rclick_cb() -> None:
            for p in pl:
                p.v.setMarked()
                p.v.setDirty()  # 2020/04/29.

        action = menu.addAction("Mark")
        action.triggered.connect(marknodes_rclick_cb)
    if any(p.isMarked() for p in pl):

        def unmarknodes_rclick_cb() -> None:
            for p in pl:
                p.v.clearMarked()
                p.v.setDirty()  # 2020/04/29.

        action = menu.addAction("Unmark")
        action.triggered.connect(unmarknodes_rclick_cb)
#@+node:ville.20090702171015.5480: *3* nextclone_rclick
def nextclone_rclick(c: Cmdr, p: Position, menu: Wrapper) -> None:
    """ Go to next clone """

    if p.isCloned():

        def nextclone_rclick_cb() -> None:
            c.goToNextClone()

        action = menu.addAction("Go to clone")
        action.triggered.connect(nextclone_rclick_cb)
#@+node:ekr.20120311191905.9900: *3* openurl_rclick
def openurl_rclick(c: Cmdr, p: Position, menu: Wrapper) -> None:
    """ open an url """
    url = g.getUrlFromNode(p)
    if url:

        def openurl_rclick_cb() -> None:
            if not g.doHook("@url1", c=c, p=p, url=url):
                g.handleUrl(url, c=c, p=p)
            g.doHook("@url2", c=c, p=p)

        action = menu.addAction("Open URL")
        action.triggered.connect(openurl_rclick_cb)
#@+node:ville.20090630210947.5465: *3* openwith_rclick & callbacks
def openwith_rclick(c: Cmdr, p: Position, menu: Wrapper) -> None:
    """
    Show "Edit with" in context menu for external file root nodes (@thin, @auto...)

    This looks like "Edit contextmenu.py in scite"

    """
    # define callbacks
    #@+others
    #@+node:ekr.20140613141207.17667: *4* function: openfolder_rclick_cb
    def openfolder_rclick_cb() -> None:

        if g.os_path_exists(path):
            g.os_startfile(path)
        else:
            # #1257:
            g.es_print('file not found:', repr(path))
    #@+node:ekr.20140613141207.17668: *4* function: create_rclick_cb
    def create_rclick_cb() -> None:

        os.makedirs(absp)
        g.es("Created " + absp)
    #@+node:ekr.20140613141207.17669: *4* function: importfiles_rclick_cb
    def importfiles_rclick_cb() -> None:

        def shorten(pth: str, prefix: str) -> str:
            if not pth.startswith(prefix):
                return pth
            return pth[len(prefix) :]

        aList = g.get_directives_dict_list(p)
        path = c.scanAtPathDirectives(aList) + "/"
        table = [
            ("All files", "*"),
            ("Python files", "*.py"),
        ]
        fnames = g.app.gui.runOpenFileDialog(c,
            title="Import files", filetypes=table,
            defaultextension='.notused',
            multiple=True, startpath=path)
        adds = [guess_file_type(pth) + " " + shorten(pth, path) for pth in fnames]
        for a in adds:
            chi = p.insertAsLastChild()
            chi.h = a
        c.readAtFileNodes()
    #@-others

    h = p.h
    parts = h.split(None, 1)
    if len(parts) < 2:
        return
    fname = None
    # argh, we need g.getAbsFileName(c,p)
    head, bname = parts
    fname = p.anyAtFileNodeName()
    if not fname and head != "@path":
        return

    path = g.scanAllAtPathDirectives(c, p)
    absp = g.finalize_join(path, fname)
    exists = os.path.exists(absp)
    if not exists and head == "@path":
        action = menu.addAction("Create dir " + absp + "/")
        action.triggered.connect(create_rclick_cb)
    if exists and head == "@path":
        action = menu.addAction("Import files")
        action.triggered.connect(importfiles_rclick_cb)
    action = menu.addAction("Open " + path)
    action.triggered.connect(openfolder_rclick_cb)
#@+node:ville.20090630221949.5462: *3* refresh_rclick
def refresh_rclick(c: Cmdr, p: Position, menu: Wrapper) -> None:

    def refresh_rclick_cb() -> None:
        c.refreshFromDisk()

    split = p.h.split(None, 1)
    if len(split) >= 2 and p.anyAtFileNodeName():
        action = menu.addAction("Refresh from disk")
        action.triggered.connect(refresh_rclick_cb)
#@+node:ekr.20140724211116.19258: *3* pylint_rclick
def pylint_rclick(c: Cmdr, p: Position, menu: Wrapper) -> None:
    """Run pylint on the selected node."""
    action = menu.addAction("Run Pylint")

    def pylint_rclick_cb(aBool: bool) -> None:
        c.doCommandByName('pylint')

    action.triggered.connect(pylint_rclick_cb)
#@+node:ekr.20140724211116.19256: ** Helpers
#@+node:ville.20110428163751.7685: *3* guess_file_type
def guess_file_type(fname: str) -> str:

    base, ext = os.path.splitext(fname)
    if ext.lower in ['.txt']:
        return "@edit"
    return "@auto"
#@-others
#@-leo
