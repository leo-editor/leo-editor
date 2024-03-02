#@+leo-ver=5-thin
#@+node:ekr.20171123095353.1: * @file ../commands/commanderFileCommands.py
"""File commands that used to be defined in leoCommands.py"""
#@+<< commanderFileCommands imports & annotations >>
#@+node:ekr.20220826120852.1: ** << commanderFileCommands imports & annotations >>
from __future__ import annotations
import os
import sys
import time
from typing import TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.core import leoImport

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent as Event
    from leo.core.leoGui import LeoGui
    Self = Cmdr  # For @g.commander_command.
#@-<< commanderFileCommands imports & annotations >>

#@+others
#@+node:ekr.20231008163009.1: **  top-level helper functions
#@+node:ekr.20231008163338.1: *3* function: do_error_dialogs
def do_error_dialogs(c: Cmdr) -> None:
    """
    Raise error dialogs.

    A helper function for c.save, c.saveAs, and c.saveTo.
    """
    c.syntaxErrorDialog()
    c.raise_error_dialogs(kind='write')
#@+node:ekr.20231008163048.1: *3* function: set_name_and_title
def set_name_and_title(c: Cmdr, fileName: str) -> str:
    """
    Compute the finalized name for c.mFileName. Set related ivars.

    A helper function for c.save, c.saveAs, and c.saveTo.

    Return the finalized name.
    """
    # Finalize fileName.
    if fileName.endswith(('.leo', '.db', '.leojs')):
        c.mFileName = fileName
    else:
        c.mFileName = g.ensure_extension(fileName, g.defaultLeoFileExtension(c))

    # Set various ivars.
    title = c.computeWindowTitle()
    c.frame.title = title
    c.frame.setTitle(title)
    try:
        # Does not exist during unit testing. May not exist in all guis.
        c.frame.top.leo_master.setTabName(c, c.mFileName)
    except AttributeError:
        pass
    return c.mFileName
#@+node:ekr.20170221033738.1: ** c_file.reloadSettings
@g.commander_command('reload-settings')
def reloadSettings(self: Self, event: Event = None) -> None:
    """Reload settings in all commanders, saving all existing opened files first"""
    lm = g.app.loadManager
    # Save any changes so they can be seen, for existing files that are not new/untitled.
    for c2 in g.app.commanders():
        if c2.isChanged() and c2.mFileName:
            c2.save()
    # Read leoSettings.leo and myLeoSettings.leo, using a null gui.
    lm.readGlobalSettingsFiles()
    for c in g.app.commanders():
        # Read the local file, using a null gui.
        previousSettings = lm.getPreviousSettings(fn=c.mFileName)
        # Init the config classes.
        c.initSettings(previousSettings)
        # Init the commander config ivars.
        c.initConfigSettings()
        # Reload settings in all configurable classes
        c.reloadConfigurableSettings()
#@+node:ekr.20200422075655.1: ** c_file.restartLeo
@g.commander_command('restart-leo')
def restartLeo(self: Self, event: Event = None) -> None:
    """Restart Leo, reloading all presently open outlines."""
    c, lm = self, g.app.loadManager
    trace = 'shutdown' in g.app.debug
    # Write .leoRecentFiles.txt.
    g.app.recentFilesManager.writeRecentFilesFile(c)
    # Abort the restart if the user veto's any close.
    for c in g.app.commanders():
        if c.changed:
            veto = False
            try:
                c.promptingForClose = True
                veto = c.frame.promptForSave()
            finally:
                c.promptingForClose = False
            if veto:
                g.es_print('Cancelling restart-leo command')
                return
    # Officially begin the restart process. A flag for efc.ask.
    g.app.restarting = True
    # Save session data.
    g.app.saveSession()
    # Close all unsaved outlines.
    g.app.setLog(None)  # Kill the log.
    for c in g.app.commanders():
        frame = c.frame
        # This is similar to g.app.closeLeoWindow.
        g.doHook("close-frame", c=c)
        # Save the window state
        # This may remove frame from the window list.
        if frame in g.app.windowList:
            g.app.destroyWindow(frame)
            g.app.windowList.remove(frame)
        else:
            # #69.
            g.app.forgetOpenFile(fn=c.fileName())
    # Complete the shutdown.
    g.app.finishQuit()
    # Restart, restoring the original command line.
    args = ['-c'] + lm.old_argv
    if trace:
        g.trace('restarting with args', args)
    sys.stdout.flush()
    sys.stderr.flush()
    os.execv(sys.executable, args)
#@+node:ekr.20031218072017.2820: ** c_file.top level
#@+node:ekr.20031218072017.2833: *3* c_file.close
@g.commander_command('close-window')
def close(self: Self, event: Event = None, new_c: Cmdr = None) -> None:
    """Close the Leo window, prompting to save it if it has been changed."""
    g.app.closeLeoWindow(self.frame, new_c=new_c)
#@+node:ekr.20110530124245.18245: *3* c_file.importAnyFile & helper
@g.commander_command('import-any-file')
@g.commander_command('import-file')
def importAnyFile(self: Self, event: Event = None) -> None:
    """Import one or more files."""
    c = self
    ic = c.importCommands
    types = [
        ("All files", "*"),
        ("C/C++ files", "*.c"),
        ("C/C++ files", "*.cpp"),
        ("C/C++ files", "*.h"),
        ("C/C++ files", "*.hpp"),
        ("FreeMind files", "*.mm.html"),
        ("Java files", "*.java"),
        ("JavaScript files", "*.js"),
        # ("JSON files", "*.json"),
        ("Mindjet files", "*.csv"),
        ("MORE files", "*.MORE"),
        ("Lua files", "*.lua"),
        ("Pascal files", "*.pas"),
        ("Python files", "*.py"),
        ("Text files", "*.txt"),
    ]
    names = g.app.gui.runOpenFileDialog(c,
        title="Import File",
        filetypes=types,
        defaultextension=".py",
        multiple=True)
    c.bringToFront()
    if names:
        g.chdir(names[0])
    else:
        names = []
    if not names:
        if g.unitTesting:
            # a kludge for unit testing.
            c.init_error_dialogs()
            c.raise_error_dialogs(kind='read')
        return
    # New in Leo 4.9: choose the type of import based on the extension.
    c.init_error_dialogs()
    derived = [z for z in names if c.looksLikeDerivedFile(z)]
    others = [z for z in names if z not in derived]
    if derived:
        ic.importDerivedFiles(parent=c.p, paths=derived)
    for fn in others:
        junk, ext = g.os_path_splitext(fn)
        ext = ext.lower()  # #1522
        if ext.startswith('.'):
            ext = ext[1:]
        if ext == 'csv':
            ic.importMindMap([fn])
        elif ext in ('cw', 'cweb'):
            ic.importWebCommand([fn], "cweb")
        # Not useful. Use @auto x.json instead.
        # elif ext == 'json':
            # ic.importJSON([fn])
        elif fn.endswith('mm.html'):
            ic.importFreeMind([fn])
        elif ext in ('nw', 'noweb'):
            ic.importWebCommand([fn], "noweb")
        elif ext == 'more':
            leoImport.MORE_Importer(c).import_file(fn)  # #1522.
        elif ext == 'txt':
            # #1522: Create an @edit node.
            import_txt_file(c, fn)
        else:
            # Make *sure* that parent.b is empty.
            last = c.lastTopLevel()
            parent = last.insertAfter()
            parent.v.h = 'Imported Files'
            ic.importFilesCommand(
                files=[fn],
                parent=parent,
                # Experimental: attempt to use permissive section ref logic.
                treeType='@auto',  # was '@clean'
            )
            c.redraw()
    c.raise_error_dialogs(kind='read')

g.command_alias('importAtFile', importAnyFile)
g.command_alias('importAtRoot', importAnyFile)
g.command_alias('importCWEBFiles', importAnyFile)
g.command_alias('importDerivedFile', importAnyFile)
g.command_alias('importFlattenedOutline', importAnyFile)
g.command_alias('importMOREFiles', importAnyFile)
g.command_alias('importNowebFiles', importAnyFile)
g.command_alias('importTabFiles', importAnyFile)
#@+node:ekr.20200306043104.1: *4* function: import_txt_file
def import_txt_file(c: Cmdr, fn: str) -> None:
    """Import the .txt file into a new node."""
    u = c.undoer
    g.setGlobalOpenDir(fn)
    undoData = u.beforeInsertNode(c.p)
    p = c.p.insertAfter()
    p.h = f"@edit {fn}"
    s, e = g.readFileIntoString(fn, kind='@edit')
    p.b = s
    u.afterInsertNode(p, 'Import', undoData)
    c.setChanged()
    c.redraw(p)
#@+node:ekr.20031218072017.1623: *3* c_file.new
@g.commander_command('file-new')
@g.commander_command('new')
def new(self: Self, event: Event = None, gui: LeoGui = None) -> Cmdr:
    """Create a new Leo window."""
    t1 = time.process_time()
    from leo.core import leoApp
    lm = g.app.loadManager
    old_c = self

    # Clean out the update queue so it won't interfere with the new window.
    self.outerUpdate()

    # Suppress redraws until later.
    g.app.disable_redraw = True
    g.app.setLog(None)
    g.app.lockLog()

    t2 = time.process_time()
    g.app.numberOfUntitledWindows += 1

    # Retain all previous settings. Very important for theme code.
    previousSettings = leoApp.PreviousSettings(
        settingsDict=lm.globalSettingsDict,
        shortcutsDict=lm.globalBindingsDict,
    )
    c = g.app.newCommander(
        fileName=None,
        gui=gui,
        previousSettings=previousSettings,
    )

    t3 = time.process_time()
    frame = c.frame
    if not old_c:
        frame.setInitialWindowGeometry()

    # #1643: This doesn't work.
        # g.app.restoreWindowState(c)

    frame.deiconify()
    frame.lift()

    # Resize the _new_ frame.
    frame.resizePanesToRatio(frame.ratio, frame.secondary_ratio)
    c.frame.createFirstTreeNode()

    # Finish.
    lm.finishOpen(c)

    g.doHook("new", old_c=old_c, c=c, new_c=c)
    c.clearChanged()  # Fix #387: Clear all dirty bits.
    c.redraw()

    t4 = time.process_time()
    if 'speed' in g.app.debug:
        g.trace()
        print(
            f"    1: {t2-t1:5.2f}\n"  # 0.00 sec.
            f"    2: {t3-t2:5.2f}\n"  # 0.36 sec: c.__init__
            f"    3: {t4-t3:5.2f}\n"  # 0.17 sec: Everything else.
            f"total: {t4-t1:5.2f}"
        )
    return c  # For unit tests and scripts.
#@+node:ekr.20031218072017.2821: *3* c_file.open_outline
@g.commander_command('open-file')
@g.commander_command('open-outline')
def open_outline(self: Self, event: Event = None) -> None:
    """Open a Leo window containing the contents of a .leo file."""
    c = self
    table = [
        ("Leo files", "*.leo *.leojs *.db"),
        ("Python files", "*.py"),
        ("All files", "*"),
    ]
    fileName = g.app.gui.runOpenFileDialog(c,
        defaultextension=g.defaultLeoFileExtension(c),
        filetypes=table,
        title="Open",
    )
    if fileName:
        g.openWithFileName(fileName, old_c=c)
#@+node:ekr.20140717074441.17772: *3* c_file.refreshFromDisk
@g.commander_command('refresh-from-disk')
def refreshFromDisk(self: Self, event: Event = None) -> None:
    """
    Refresh an @<file> node from disk.

    This command is not undoable.
    """
    c, p = self, self.p
    if not p.isAnyAtFileNode():
        g.warning(f"not an @<file> node: {p.h!r}")
        return
    full_path = c.fullPath(p)
    if os.path.isdir(full_path):
        g.warning(f"not a file: {full_path!r}")
        return
    at = c.atFileCommands
    c.nodeConflictList = []
    c.recreateGnxDict()
    if p.isAtAutoNode() or p.isAtAutoRstNode():
        p.v._deleteAllChildren()
        p = at.readOneAtAutoNode(p)  # Changes p!
    elif p.isAtFileNode():
        p.v._deleteAllChildren()
        at.read(p)
    elif p.isAtCleanNode():
        # Don't delete children!
        at.readOneAtCleanNode(p)
    elif p.isAtShadowFileNode():
        p.v._deleteAllChildren()
        at.read(p)
    elif p.isAtEditNode():
        at.readOneAtEditNode(p)  # Always deletes children.
    elif p.isAtAsisFileNode():
        at.readOneAtAsisNode(p)  # Always deletes children.
    else:
        g.es_print(f"Unknown @<file> node: {p.h!r}")
        return
    c.selectPosition(p)
    # Create the 'Recovered Nodes' tree.
    c.fileCommands.handleNodeConflicts()
    c.redraw()
    c.undoer.clearAndWarn('refresh-from-disk')
#@+node:ekr.20210610083257.1: *3* c_file.pwd
@g.commander_command('pwd')
def pwd_command(self: Self, event: Event = None) -> None:
    """Print the current working directory."""
    g.es_print('pwd:', os.getcwd())
#@+node:ekr.20031218072017.2834: *3* c_file.save
@g.commander_command('save')
@g.commander_command('file-save')
@g.commander_command('save-file')
def save(self: Self, event: Event = None, fileName: str = None) -> None:
    """
    Save a Leo outline to a file, using the existing file name unless
    the fileName kwarg is given.

    kwarg: a file name, for use by scripts using Leo's bridge.
    """
    c = self

    if g.app.disableSave:
        g.es("save commands disabled", color="purple")
        return

    def do_save(c: Cmdr, fileName: str) -> None:
        """Common save code."""
        c.fileCommands.save(fileName)
        g.app.recentFilesManager.updateRecentFiles(fileName)
        g.chdir(fileName)

    try:
        c.init_error_dialogs()

        # Don't prompt if the file name is known.
        given_file_name = fileName or c.mFileName
        if given_file_name:
            final_file_name = set_name_and_title(c, given_file_name)
            do_save(c, final_file_name)
            return

        # The file still has no name.

        root = c.rootPosition()
        if not root.next() and root.isAtEditNode():
            # Write the @edit node if needed.
            if root.isDirty():
                c.atFileCommands.writeOneAtEditNode(root)
            c.clearChanged()  # Clears all dirty bits.
            do_error_dialogs(c)
            return

        # Prompt for fileName.
        new_file_name = g.app.gui.runSaveFileDialog(c,
            title="Save",
            filetypes=[("Leo files", "*.leo *.leojs *.db"),],
            defaultextension=g.defaultLeoFileExtension(c))

        if new_file_name:
            final_file_name = set_name_and_title(c, new_file_name)
            do_save(c, final_file_name)

    finally:
        do_error_dialogs(c)
#@+node:ekr.20110228162720.13980: *3* c_file.saveAll
@g.commander_command('save-all')
def saveAll(self: Self, event: Event = None) -> None:
    """Save all open tabs windows/tabs."""
    c = self
    c.save()  # Force a write of the present window.
    for f in g.app.windowList:
        c2 = f.c
        if c2 != c and c2.isChanged():
            c2.save()
    # Restore the present tab.
    dw = c.frame.top  # A DynamicWindow
    dw.select(c)
#@+node:ekr.20031218072017.2835: *3* c_file.saveAs
@g.commander_command('save-as')
@g.commander_command('file-save-as')
@g.commander_command('save-file-as')
def saveAs(self: Self, event: Event = None, fileName: str = None) -> None:
    """
    Save a Leo outline to a file, prompting for a new filename unless the
    fileName kwarg is given.

    kwarg: a file name, for use by file-save-as-zipped,
    file-save-as-unzipped and scripts using Leo's bridge.
    """
    c = self

    if g.app.disableSave:
        g.es("save commands disabled", color="purple")
        return

    def do_save_as(c: Cmdr, fileName: str) -> str:
        """Common save-as code."""
        # 1. Forget the previous file.
        if c.mFileName:
            g.app.forgetOpenFile(c.mFileName)
        # 2. Finalize fileName and set related ivars.
        new_file_name = set_name_and_title(c, fileName)
        # 3. Do the save and related tasks.
        c.fileCommands.saveAs(new_file_name)
        g.app.recentFilesManager.updateRecentFiles(new_file_name)
        g.chdir(new_file_name)
        return new_file_name

    try:
        c.init_error_dialogs()

        # Handle the kwarg first.
        if fileName:
            do_save_as(c, fileName)
            return

        # Prompt for fileName.
        new_file_name = g.app.gui.runSaveFileDialog(c,
            title="Save As",
            filetypes=[("Leo files", "*.leo *.leojs *.db"),],
            defaultextension=g.defaultLeoFileExtension(c))

        if new_file_name:
            do_save_as(c, new_file_name)

    finally:
        do_error_dialogs(c)
#@+node:ekr.20031218072017.2836: *3* c_file.saveTo
@g.commander_command('save-to')
@g.commander_command('file-save-to')
@g.commander_command('save-file-to')
def saveTo(self: Self, event: Event = None, fileName: str = None, silent: bool = False) -> None:
    """
    Save a copy of the Leo outline to a file, prompting for a new file name.
    Leave the file name of the Leo outline unchanged.

    kwarg: a file name, for use by scripts using Leo's bridge.
    """
    c = self

    if g.app.disableSave:
        g.es("save commands disabled", color="purple")
        return

    def do_save_to(c: Cmdr, fileName: str) -> None:
        """Common save-to code."""
        # *Never* change c.mFileName or c.frame.title.
        c.fileCommands.saveTo(fileName, silent=silent)
        g.app.recentFilesManager.updateRecentFiles(fileName)
        # *Never* call g.chdir!

    try:
        c.init_error_dialogs()

        # Handle the kwarg first.
        if fileName:
            do_save_to(c, fileName)
            return

        new_file_name = g.app.gui.runSaveFileDialog(c,
            title="Save To",
            filetypes=[("Leo files", "*.leo *.leojs *.db"),],
            defaultextension=g.defaultLeoFileExtension(c))

        if new_file_name:
            do_save_to(c, new_file_name)

    finally:
        do_error_dialogs(c)
#@+node:ekr.20031218072017.2837: *3* c_file.revert
@g.commander_command('revert')
def revert(self: Self, event: Event = None) -> None:
    """Revert the contents of a Leo outline to last saved contents."""
    c = self
    u = c.undoer
    # Make sure the user wants to Revert.
    fn = c.mFileName
    if not fn:
        g.es('Can not revert unnamed file.')
        return
    if not g.os_path_exists(fn):
        g.es(f"Can not revert non-existent file: {fn}")
        return
    reply = g.app.gui.runAskYesNoDialog(
        c, 'Revert', f"Revert to previous version of {fn}?")
    c.bringToFront()
    if reply == "yes":
        g.app.loadManager.revertCommander(c)
        u.clearUndoState()
#@+node:ekr.20210316075815.1: *3* c_file.save-as-leojs
@g.commander_command('file-save-as-leojs')
@g.commander_command('save-file-as-leojs')
def save_as_leojs(self: Self, event: Event = None) -> None:
    """
    Save a copy of the Leo outline as a JSON (.leojs) file with a new file name.
    Leave the file name of the Leo outline unchanged.
    """
    c = self
    fileName = g.app.gui.runSaveFileDialog(c,
        title="Save As JSON (.leojs)",
        filetypes=[("Leo JSON files", "*.leojs")],
        defaultextension='.leojs')
    if not fileName:
        return
    if not fileName.endswith('.leojs'):
        fileName = f"{fileName}.leojs"
    # Leo 6.4: Using save-to instead of save-as allows two versions of the file.
    c.saveTo(fileName=fileName)
    c.fileCommands.putSavedMessage(fileName)
#@+node:ekr.20070413045221: *3* c_file.save-as-zipped
@g.commander_command('file-save-as-zipped')
@g.commander_command('save-file-as-zipped')
def save_as_zipped(self: Self, event: Event = None) -> None:
    """
    Save a copy of the Leo outline as a zipped (.db) file with a new file name.
    Leave the file name of the Leo outline unchanged.
    """
    c = self
    fileName = g.app.gui.runSaveFileDialog(c,
        title="Save As Zipped",
        filetypes=[("Leo files", "*.db")],
        defaultextension='.db')
    if not fileName:
        return
    if not fileName.endswith('.db'):
        fileName = f"{fileName}.db"
    # Leo 6.4: Using save-to instead of save-as allows two versions of the file.
    c.saveTo(fileName=fileName)
    c.fileCommands.putSavedMessage(fileName)
#@+node:ekr.20210316075357.1: *3* c_file.save-as-xml
@g.commander_command('file-save-as-xml')
@g.commander_command('save-file-as-xml')
def save_as_xml(self: Self, event: Event = None) -> None:
    """
    Save a copy of the Leo outline as an XML .leo file with a new file name.
    Leave the file name of the Leo outline unchanged.
    Useful for converting a .leo.db file to a .leo file.
    """
    c = self
    fileName = g.app.gui.runSaveFileDialog(c,
        title="Save As XML",
        filetypes=[("Leo files", "*.leo")],
        defaultextension=g.defaultLeoFileExtension(c))
    if not fileName:
        return
    if not fileName.endswith('.leo'):
        fileName = f"{fileName}.leo"
    # Leo 6.4: Using save-to instead of save-as allows two versions of the file.
    c.saveTo(fileName=fileName)
    c.fileCommands.putSavedMessage(fileName)
#@+node:tom.20220310092720.1: *3* c_file.save-node-as-xml
@g.commander_command('save-node-as-xml')
def save_node_as_xml_outline(self: Self, event: Event = None) -> None:
    """
    Save a node with its subtree as an XML .leo outline file.
    Leave the outline and the file name of the Leo outline unchanged.
    """
    c = event.c
    xml = c.fileCommands.outline_to_clipboard_string()

    fileName = g.app.gui.runSaveFileDialog(c,
                title="Save To",
                filetypes=[("Leo files", "*.leo"),],
                defaultextension=g.defaultLeoFileExtension(c))

    if fileName:
        with open(fileName, 'w', encoding='utf-8') as f:
            f.write(xml)
#@+node:ekr.20031218072017.2849: ** Export
#@+node:ekr.20031218072017.2850: *3* c_file.exportHeadlines
@g.commander_command('export-headlines')
def exportHeadlines(self: Self, event: Event = None) -> None:
    """Export headlines for c.p and its subtree to an external file."""
    c = self
    filetypes = [("Text files", "*.txt"), ("All files", "*")]
    fileName = g.app.gui.runSaveFileDialog(c,
        title="Export Headlines",
        filetypes=filetypes,
        defaultextension=".txt")
    c.bringToFront()
    if fileName:
        g.setGlobalOpenDir(fileName)
        g.chdir(fileName)
        c.importCommands.exportHeadlines(fileName)
#@+node:ekr.20031218072017.2851: *3* c_file.flattenOutline
@g.commander_command('flatten-outline')
def flattenOutline(self: Self, event: Event = None) -> None:
    """
    Export the selected outline to an external file.
    The outline is represented in MORE format.
    """
    c = self
    filetypes = [("Text files", "*.txt"), ("All files", "*")]
    fileName = g.app.gui.runSaveFileDialog(c,
        title="Flatten Selected Outline",
        filetypes=filetypes,
        defaultextension=".txt")
    c.bringToFront()
    if fileName:
        g.setGlobalOpenDir(fileName)
        g.chdir(fileName)
        c.importCommands.flattenOutline(fileName)
#@+node:ekr.20141030120755.12: *3* c_file.flattenOutlineToNode
@g.commander_command('flatten-outline-to-node')
def flattenOutlineToNode(self: Self, event: Event = None) -> None:
    """
    Append the body text of all descendants of the selected node to the
    body text of the selected node.
    """
    c, root, u = self, self.p, self.undoer
    if not root.hasChildren():
        return
    language = g.getLanguageAtPosition(c, root)
    if language:
        single, start, end = g.set_delims_from_language(language)
    else:
        single, start, end = '#', None, None
    bunch = u.beforeChangeNodeContents(root)
    aList = []
    for p in root.subtree():
        if single:
            aList.append(f"\n\n===== {single} {p.h}\n\n")
        else:
            aList.append(f"\n\n===== {start} {p.h} {end}\n\n")
        if p.b.strip():
            lines = g.splitLines(p.b)
            aList.extend(lines)
    root.b = root.b.rstrip() + '\n' + ''.join(aList).rstrip() + '\n'
    u.afterChangeNodeContents(root, 'flatten-outline-to-node', bunch)
#@+node:ekr.20031218072017.2857: *3* c_file.outlineToCWEB
@g.commander_command('outline-to-cweb')
def outlineToCWEB(self: Self, event: Event = None) -> None:
    """
    Export the selected outline to an external file.
    The outline is represented in CWEB format.
    """
    c = self
    filetypes = [
        ("CWEB files", "*.w"),
        ("Text files", "*.txt"),
        ("All files", "*")]
    fileName = g.app.gui.runSaveFileDialog(c,
        title="Outline To CWEB",
        filetypes=filetypes,
        defaultextension=".w")
    c.bringToFront()
    if fileName:
        g.setGlobalOpenDir(fileName)
        g.chdir(fileName)
        c.importCommands.outlineToWeb(fileName, "cweb")
#@+node:ekr.20031218072017.2858: *3* c_file.outlineToNoweb
@g.commander_command('outline-to-noweb')
def outlineToNoweb(self: Self, event: Event = None) -> None:
    """
    Export the selected outline to an external file.
    The outline is represented in noweb format.
    """
    c = self
    filetypes = [
        ("Noweb files", "*.nw"),
        ("Text files", "*.txt"),
        ("All files", "*")]
    fileName = g.app.gui.runSaveFileDialog(c,
        title="Outline To Noweb",
        filetypes=filetypes,
        defaultextension=".nw")
    c.bringToFront()
    if fileName:
        g.setGlobalOpenDir(fileName)
        g.chdir(fileName)
        c.importCommands.outlineToWeb(fileName, "noweb")
        c.outlineToNowebDefaultFileName = fileName
#@+node:ekr.20031218072017.2859: *3* c_file.removeSentinels
@g.commander_command('remove-sentinels')
def removeSentinels(self: Self, event: Event = None) -> None:
    """
    Convert one or more files, replacing the original files
    while removing any sentinels they contain.
    """
    c = self
    types = [
        ("All files", "*"),
        ("C/C++ files", "*.c"),
        ("C/C++ files", "*.cpp"),
        ("C/C++ files", "*.h"),
        ("C/C++ files", "*.hpp"),
        ("Java files", "*.java"),
        ("Lua files", "*.lua"),
        ("Pascal files", "*.pas"),
        ("Python files", "*.py")]
    names = g.app.gui.runOpenFileDialog(c,
        title="Remove Sentinels",
        filetypes=types,
        defaultextension=".py",
        multiple=True)
    c.bringToFront()
    if names:
        g.chdir(names[0])
        c.importCommands.removeSentinelsCommand(names)
#@+node:ekr.20031218072017.2860: *3* c_file.weave
@g.commander_command('weave')
def weave(self: Self, event: Event = None) -> None:
    """Simulate a literate-programming weave operation by writing the outline to a text file."""
    c = self
    fileName = g.app.gui.runSaveFileDialog(c,
        title="Weave",
        filetypes=[("Text files", "*.txt"), ("All files", "*")],
        defaultextension=".txt")
    c.bringToFront()
    if fileName:
        g.setGlobalOpenDir(fileName)
        g.chdir(fileName)
        c.importCommands.weave(fileName)
#@+node:ekr.20031218072017.2838: ** Read/Write
#@+node:ekr.20070806105721.1: *3* c_file.readAtAutoNodes
@g.commander_command('read-at-auto-nodes')
def readAtAutoNodes(self: Self, event: Event = None) -> None:
    """
    Read all @auto nodes in the presently selected outline.

    This command is not undoable.
    """
    c = self
    c.endEditing()
    c.init_error_dialogs()
    c.importCommands.readAtAutoNodes()
    c.redraw()
    c.raise_error_dialogs(kind='read')
    c.undoer.clearAndWarn('read-at-auto-nodes')
#@+node:ekr.20031218072017.1839: *3* c_file.readAtFileNodes
@g.commander_command('read-at-file-nodes')
def readAtFileNodes(self: Self, event: Event = None) -> None:
    """
    Read all @file nodes in the presently selected outline.

    This command is not undoable.
    """
    c, p = self, self.p
    c.endEditing()
    c.endEditing()
    c.atFileCommands.readAllSelected(p)

    # Force an update of the body pane.
    c.setBodyString(p, p.b)  # Not a do-nothing!
    c.redraw()
    c.undoer.clearAndWarn('read-at-file-nodes')
#@+node:ekr.20080801071227.4: *3* c_file.readAtShadowNodes
@g.commander_command('read-at-shadow-nodes')
def readAtShadowNodes(self: Self, event: Event = None) -> None:
    """
    Read all @shadow nodes in the presently selected outline.

    This command is not undoable.
    """
    c, p = self, self.p
    c.endEditing()
    c.init_error_dialogs()
    c.atFileCommands.readAtShadowNodes(p)
    c.redraw()
    c.raise_error_dialogs(kind='read')
    c.undoer.clearAndWarn('read-at-shadow-nodes')
#@+node:ekr.20070915134101: *3* c_file.readFileIntoNode
@g.commander_command('read-file-into-node')
def readFileIntoNode(self: Self, event: Event = None) -> None:
    """Read a file into a single node."""
    c = self
    u = c.undoer
    undoType = 'Read File Into Node'
    c.endEditing()
    filetypes = [("All files", "*"), ("Python files", "*.py"), ("Leo files", "*.leo *.leojs"),]
    fileName = g.app.gui.runOpenFileDialog(c,
        title="Read File Into Node",
        filetypes=filetypes,
        defaultextension=None)
    if not fileName:
        return
    s, e = g.readFileIntoString(fileName)
    if s is None:
        return
    g.chdir(fileName)
    s = '@nocolor\n' + s
    w = c.frame.body.wrapper
    undoData = u.beforeInsertNode(c.p)
    p = c.p.insertAfter()
    p.setHeadString('@read-file-into-node ' + fileName)
    p.setBodyString(s)
    u.afterInsertNode(p, undoType, undoData)
    w.setAllText(s)
    c.redraw(p)
#@+node:ekr.20070915142635: *3* c_file.writeFileFromNode
@g.commander_command('write-file-from-node')
def writeFileFromNode(self: Self, event: Event = None) -> None:
    """
    If node starts with @read-file-into-node, use the full path name in the headline.
    Otherwise, prompt for a file name.
    """
    c, p = self, self.p
    c.endEditing()
    h = p.h.rstrip()
    s = p.b
    tag = '@read-file-into-node'
    if h.startswith(tag):
        fileName = h[len(tag) :].strip()
    else:
        fileName = None
    if not fileName:
        fileName = g.app.gui.runSaveFileDialog(c,
            title='Write File From Node',
            filetypes=[("All files", "*"), ("Python files", "*.py"), ("Leo files", "*.leo *.leojs")],
            defaultextension=None)
    if fileName:
        try:
            with open(fileName, 'w') as f:
                g.chdir(fileName)
                if s.startswith('@nocolor\n'):
                    s = s[len('@nocolor\n') :]
                f.write(s)
                f.flush()
                g.blue('wrote:', fileName)
        except IOError:
            g.error('can not write %s', fileName)
#@+node:tom.20230201124905.1: *3* c_file.writeFileFromSubtree
@g.commander_command('write-file-from-subtree')
def writeFileFromSubtree(self: Self, event: Event = None) -> None:
    """Write the entire tree from the selected node as text to a file.

    If node starts with @read-file-into-node, use the full path name in the headline.
    Otherwise, prompt for a file name.
    """
    c, p = self, self.p
    c.endEditing()
    h = p.h.rstrip()
    s = ''
    for p1 in p.self_and_subtree():
        s += p1.b + '\n'
    tag = '@read-file-into-node'
    if h.startswith(tag):
        fileName = h[len(tag) :].strip()
    else:
        fileName = None
    if not fileName:
        fileName = g.app.gui.runSaveFileDialog(c,
            title='Write File From Node',
            filetypes=[("All files", "*"), ("Python files", "*.py"), ("Leo files", "*.leo *.leojs")],
            defaultextension=None)
    if fileName:
        try:
            with open(fileName, 'w') as f:
                g.chdir(fileName)
                if s.startswith('@nocolor\n'):
                    s = s[len('@nocolor\n') :]
                f.write(s)
                f.flush()
                g.blue('wrote:', fileName)
        except IOError:
            g.error('can not write %s', fileName)
#@+node:ekr.20031218072017.2079: ** Recent Files
#@+node:tbrown.20080509212202.6: *3* c_file.cleanRecentFiles
@g.commander_command('clean-recent-files')
def cleanRecentFiles(self: Self, event: Event = None) -> None:
    """
    Remove items from the recent files list that no longer exist.

    This almost never does anything because Leo's startup logic removes
    nonexistent files from the recent files list.
    """
    c = self
    g.app.recentFilesManager.cleanRecentFiles(c)
#@+node:ekr.20031218072017.2080: *3* c_file.clearRecentFiles
@g.commander_command('clear-recent-files')
def clearRecentFiles(self: Self, event: Event = None) -> None:
    """Clear the recent files list, then add the present file."""
    c = self
    g.app.recentFilesManager.clearRecentFiles(c)
#@+node:vitalije.20170703115710.1: *3* c_file.editRecentFiles
@g.commander_command('edit-recent-files')
def editRecentFiles(self: Self, event: Event = None) -> None:
    """Opens recent files list in a new node for editing."""
    c = self
    g.app.recentFilesManager.editRecentFiles(c)
#@+node:tbrown.20080509212202.8: *3* c_file.sortRecentFiles
@g.commander_command('sort-recent-files')
def sortRecentFiles(self: Self, event: Event = None) -> None:
    """Sort the recent files list."""
    c = self
    g.app.recentFilesManager.sortRecentFiles(c)
#@+node:vitalije.20170703115710.2: *3* c_file.writeEditedRecentFiles
@g.commander_command('write-edited-recent-files')
def writeEditedRecentFiles(self: Self, event: Event = None) -> None:
    """
    Write content of "edit_headline" node as recentFiles and recreates
    menus.
    """
    c = self
    g.app.recentFilesManager.writeEditedRecentFiles(c)
#@+node:ekr.20180312043352.1: ** Themes
#@+node:ekr.20180312043352.2: *3* c_file.open_theme_file
@g.commander_command('open-theme-file')
def open_theme_file(self: Self, event: Event) -> None:
    """Open a theme file in a new session and apply the theme."""
    c = event and event.get('c')
    if not c:
        return
    # Get the file name.
    themes_dir = g.finalize_join(g.app.loadDir, '..', 'themes')
    fn = g.app.gui.runOpenFileDialog(c,
        title="Open Theme File",
        filetypes=[
            ("Leo files", "*.leo *.leojs *.db"),
            ("All files", "*"),
        ],
        defaultextension=g.defaultLeoFileExtension(c),
        startpath=themes_dir,
    )
    if not fn:
        return
    leo_dir = g.finalize_join(g.app.loadDir, '..', '..')
    os.chdir(leo_dir)
    #
    # #1425: Open the theme file in a separate process.
    # #1564. Use execute_shell_commands.
    # #1974: allow spaces in path.
    command = f'"{g.sys.executable}" "{g.app.loadDir}/runLeo.py" "{fn}"'
    g.execute_shell_commands(command)
    os.chdir(leo_dir)
#@-others
#@-leo
