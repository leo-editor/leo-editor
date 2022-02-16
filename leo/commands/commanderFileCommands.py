# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20171123095353.1: * @file ../commands/commanderFileCommands.py
#@@first
"""File commands that used to be defined in leoCommands.py"""
import os
import sys
import time
from leo.core import leoGlobals as g
from leo.core import leoImport
#@+others
#@+node:ekr.20170221033738.1: ** c_file.reloadSettings & helper
@g.commander_command('reload-settings')
def reloadSettings(self, event=None):
    """Reload settings in all commanders, or just c."""
    lm = g.app.loadManager
    # Save any changes so they can be seen.
    for c2 in g.app.commanders():
        if c2.isChanged():
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
#@+node:ekr.20170221034501.1: *3* function: reloadSettingsHelper
def reloadSettingsHelper(c):
    """
    Reload settings in all commanders, or just c.

    A helper function for reload-settings and reload-all-settings.
    """
    lm = g.app.loadManager
    # Save any changes so they can be seen.
    for c2 in g.app.commanders():
        if c2.isChanged():
            c2.save()
    lm.readGlobalSettingsFiles()
        # Read leoSettings.leo and myLeoSettings.leo, using a null gui.
    for c in g.app.commanders():
        previousSettings = lm.getPreviousSettings(fn=c.mFileName)
            # Read the local file, using a null gui.
        c.initSettings(previousSettings)
            # Init the config classes.
        c.initConfigSettings()
            # Init the commander config ivars.
        c.reloadConfigurableSettings()
            # Reload settings in all configurable classes
        # c.redraw()
            # Redraw so a pasted temp node isn't visible
#@+node:ekr.20200422075655.1: ** c_file.restartLeo
@g.commander_command('restart-leo')
def restartLeo(self, event=None):
    """Restart Leo, reloading all presently open outlines."""
    c, lm = self, g.app.loadManager
    trace = 'shutdown' in g.app.debug
    # 1. Write .leoRecentFiles.txt.
    g.app.recentFilesManager.writeRecentFilesFile(c)
    # 2. Abort the restart if the user veto's any close.
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
    # 3. Officially begin the restart process. A flag for efc.ask.
    g.app.restarting = True  # #1240.
    # 4. Save session data.
    if g.app.sessionManager:
        g.app.sessionManager.save_snapshot()
    # 5. Close all unsaved outlines.
    g.app.setLog(None)  # Kill the log.
    for c in g.app.commanders():
        frame = c.frame
        # This is similar to g.app.closeLeoWindow.
        g.doHook("close-frame", c=c)
        # Save the window state
        g.app.commander_cacher.commit()  # store cache, but don't close it.
        # This may remove frame from the window list.
        if frame in g.app.windowList:
            g.app.destroyWindow(frame)
            g.app.windowList.remove(frame)
        else:
            # #69.
            g.app.forgetOpenFile(fn=c.fileName())
    # 6. Complete the shutdown.
    g.app.finishQuit()
    # 7. Restart, restoring the original command line.
    args = ['-c'] + [z for z in lm.old_argv]
    if trace:
        g.trace('restarting with args', args)
    sys.stdout.flush()
    sys.stderr.flush()
    os.execv(sys.executable, args)
#@+node:ekr.20031218072017.2820: ** c_file.top level
#@+node:ekr.20031218072017.2833: *3* c_file.close
@g.commander_command('close-window')
def close(self, event=None, new_c=None):
    """Close the Leo window, prompting to save it if it has been changed."""
    g.app.closeLeoWindow(self.frame, new_c=new_c)
#@+node:ekr.20110530124245.18245: *3* c_file.importAnyFile & helper
@g.commander_command('import-file')
def importAnyFile(self, event=None):
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
                treeType='@auto',  # was '@clean'
                    # Experimental: attempt to use permissive section ref logic.
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
def import_txt_file(c, fn):
    """Import the .txt file into a new node."""
    u = c.undoer
    g.setGlobalOpenDir(fn)
    undoData = u.beforeInsertNode(c.p)
    last = c.lastTopLevel()
    p = last.insertAfter()
    p.h = f"@edit {fn}"
    s, e = g.readFileIntoString(fn, kind='@edit')
    p.b = s
    u.afterInsertNode(p, 'Import', undoData)
    c.setChanged()
    c.redraw(p)
#@+node:ekr.20031218072017.1623: *3* c_file.new
@g.commander_command('file-new')
@g.commander_command('new')
def new(self, event=None, gui=None):
    """Create a new Leo window."""
    t1 = time.process_time()
    from leo.core import leoApp
    lm = g.app.loadManager
    old_c = self
    # Clean out the update queue so it won't interfere with the new window.
    self.outerUpdate()
    # Supress redraws until later.
    g.app.disable_redraw = True
    # Send all log messages to the new frame.
    g.app.setLog(None)
    g.app.lockLog()
    # Retain all previous settings. Very important for theme code.
    t2 = time.process_time()
    c = g.app.newCommander(
        fileName=None,
        gui=gui,
        previousSettings=leoApp.PreviousSettings(
            settingsDict=lm.globalSettingsDict,
            shortcutsDict=lm.globalBindingsDict,
        ))
    t3 = time.process_time()
    frame = c.frame
    g.app.unlockLog()
    if not old_c:
        frame.setInitialWindowGeometry()
    # #1643: This doesn't work.
        # g.app.restoreWindowState(c)
    frame.deiconify()
    frame.lift()
    frame.resizePanesToRatio(frame.ratio, frame.secondary_ratio)
        # Resize the _new_ frame.
    c.frame.createFirstTreeNode()
    lm.createMenu(c)
    lm.finishOpen(c)
    g.app.writeWaitingLog(c)
    g.doHook("new", old_c=old_c, c=c, new_c=c)
    c.setLog()
    c.clearChanged()  # Fix #387: Clear all dirty bits.
    g.app.disable_redraw = False
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
@g.commander_command('open-outline')
def open_outline(self, event=None):
    """Open a Leo window containing the contents of a .leo file."""
    c = self
    #@+others
    #@+node:ekr.20190518121302.1: *4* function: open_completer
    def open_completer(c, closeFlag, fileName):

        c.bringToFront()
        c.init_error_dialogs()
        ok = False
        if fileName:
            if g.app.loadManager.isLeoFile(fileName):
                c2 = g.openWithFileName(fileName, old_c=c)
                if c2:
                    c2.k.makeAllBindings()
                        # Fix #579: Key bindings don't take for commands defined in plugins.
                    g.chdir(fileName)
                    g.setGlobalOpenDir(fileName)
                if c2 and closeFlag:
                    g.app.destroyWindow(c.frame)
            elif c.looksLikeDerivedFile(fileName):
                # Create an @file node for files containing Leo sentinels.
                ok = c.importCommands.importDerivedFiles(parent=c.p,
                    paths=[fileName], command='Open')
            else:
                # otherwise, create an @edit node.
                ok = c.createNodeFromExternalFile(fileName)
        c.raise_error_dialogs(kind='write')
        g.app.runAlreadyOpenDialog(c)
        # openWithFileName sets focus if ok.
        if not ok:
            c.initialFocusHelper()
    #@-others
        # Defines open_completer function.

    #
    # Close the window if this command completes successfully?

    closeFlag = (
        c.frame.startupWindow and
            # The window was open on startup
        not c.changed and not c.frame.saved and
            # The window has never been changed
        g.app.numberOfUntitledWindows == 1
            # Only one untitled window has ever been opened
    )
    table = [
        ("Leo files", "*.leo *.db"),
        ("Python files", "*.py"),
        ("All files", "*"),
    ]
    fileName = ''.join(c.k.givenArgs)
    if fileName:
        c.open_completer(c, closeFlag, fileName)
        return
    # Equivalent to legacy code.
    fileName = g.app.gui.runOpenFileDialog(c,
        defaultextension=g.defaultLeoFileExtension(c),
        filetypes=table,
        title="Open",
    )
    open_completer(c, closeFlag, fileName)
#@+node:ekr.20140717074441.17772: *3* c_file.refreshFromDisk
# refresh_pattern = re.compile(r'^(@[\w-]+)')

@g.commander_command('refresh-from-disk')
def refreshFromDisk(self, event=None):
    """Refresh an @<file> node from disk."""
    c, p, u = self, self.p, self.undoer
    c.nodeConflictList = []
    fn = p.anyAtFileNodeName()
    shouldDelete = c.sqlite_connection is None
    if not fn:
        g.warning(f"not an @<file> node: {p.h!r}")
        return
    # #1603.
    if os.path.isdir(fn):
        g.warning(f"not a file: {fn!r}")
        return
    b = u.beforeChangeTree(p)
    redraw_flag = True
    at = c.atFileCommands
    c.recreateGnxDict()
        # Fix bug 1090950 refresh from disk: cut node ressurection.
    i = g.skip_id(p.h, 0, chars='@')
    word = p.h[0:i]
    if word == '@auto':
        # This includes @auto-*
        if shouldDelete:
            p.v._deleteAllChildren()
        # Fix #451: refresh-from-disk selects wrong node.
        p = at.readOneAtAutoNode(p)
    elif word in ('@thin', '@file'):
        if shouldDelete:
            p.v._deleteAllChildren()
        at.read(p)
    elif word == '@clean':
        # Wishlist 148: use @auto parser if the node is empty.
        if p.b.strip() or p.hasChildren():
            at.readOneAtCleanNode(p)
        else:
            # Fix #451: refresh-from-disk selects wrong node.
            p = at.readOneAtAutoNode(p)
    elif word == '@shadow':
        if shouldDelete:
            p.v._deleteAllChildren()
        at.read(p)
    elif word == '@edit':
        at.readOneAtEditNode(fn, p)
            # Always deletes children.
    elif word == '@asis':
        # Fix #1067.
        at.readOneAtAsisNode(fn, p)
            # Always deletes children.
    else:
        g.es_print(f"can not refresh from disk\n{p.h!r}")
        redraw_flag = False
    if redraw_flag:
        # Fix #451: refresh-from-disk selects wrong node.
        c.selectPosition(p)
        u.afterChangeTree(p, command='refresh-from-disk', bunch=b)
        # Create the 'Recovered Nodes' tree.
        c.fileCommands.handleNodeConflicts()
        c.redraw()
#@+node:ekr.20210610083257.1: *3* c_file.pwd
@g.commander_command('pwd')
def pwd_command(self, event=None):
    """Print the current working directory."""
    g.es_print('pwd:', os.getcwd())
#@+node:ekr.20031218072017.2834: *3* c_file.save
@g.commander_command('save')
@g.commander_command('file-save')
@g.commander_command('save-file')
def save(self, event=None, fileName=None):
    """
    Save a Leo outline to a file, using the existing file name unless
    the fileName kwarg is given.

    kwarg: a file name, for use by scripts using Leo's bridge.
    """
    c = self
    p = c.p
    # Do this now: w may go away.
    w = g.app.gui.get_focus(c)
    inBody = g.app.gui.widget_name(w).startswith('body')
    if inBody:
        p.saveCursorAndScroll()
    if g.app.disableSave:
        g.es("save commands disabled", color="purple")
        return
    c.init_error_dialogs()
    # 2013/09/28: use the fileName keyword argument if given.
    # This supports the leoBridge.
    # Make sure we never pass None to the ctor.
    if fileName:
        c.frame.title = g.computeWindowTitle(fileName)
        c.mFileName = fileName
    if not c.mFileName:
        c.frame.title = ""
        c.mFileName = ""
    if c.mFileName:
        # Calls c.clearChanged() if no error.
        g.app.syntax_error_files = []
        c.fileCommands.save(c.mFileName)
        c.syntaxErrorDialog()
    else:
        root = c.rootPosition()
        if not root.next() and root.isAtEditNode():
            # There is only a single @edit node in the outline.
            # A hack to allow "quick edit" of non-Leo files.
            # See https://bugs.launchpad.net/leo-editor/+bug/381527
            fileName = None
            # Write the @edit node if needed.
            if root.isDirty():
                c.atFileCommands.writeOneAtEditNode(root)
            c.clearChanged()  # Clears all dirty bits.
        else:
            fileName = ''.join(c.k.givenArgs)
            if not fileName:
                fileName = g.app.gui.runSaveFileDialog(c,
                    title="Save",
                    filetypes=[("Leo files", "*.leo *.db"),],
                    defaultextension=g.defaultLeoFileExtension(c))
        c.bringToFront()
        if fileName:
            # Don't change mFileName until the dialog has suceeded.
            c.mFileName = g.ensure_extension(fileName, g.defaultLeoFileExtension(c))
            c.frame.title = c.computeWindowTitle(c.mFileName)
            c.frame.setTitle(c.computeWindowTitle(c.mFileName))
                # 2013/08/04: use c.computeWindowTitle.
            c.openDirectory = c.frame.openDirectory = g.os_path_dirname(c.mFileName)
                # Bug fix in 4.4b2.
            if hasattr(c.frame, 'top'):
                c.frame.top.leo_master.setTabName(c, c.mFileName)
            c.fileCommands.save(c.mFileName)
            g.app.recentFilesManager.updateRecentFiles(c.mFileName)
            g.chdir(c.mFileName)
    # Done in FileCommands.save.
    # c.redraw_after_icons_changed()
    c.raise_error_dialogs(kind='write')
    # *Safely* restore focus, without using the old w directly.
    if inBody:
        c.bodyWantsFocus()
        p.restoreCursorAndScroll()
    else:
        c.treeWantsFocus()
#@+node:ekr.20110228162720.13980: *3* c_file.saveAll
@g.commander_command('save-all')
def saveAll(self, event=None):
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
def saveAs(self, event=None, fileName=None):
    """
    Save a Leo outline to a file, prompting for a new filename unless the
    fileName kwarg is given.

    kwarg: a file name, for use by file-save-as-zipped,
    file-save-as-unzipped and scripts using Leo's bridge.
    """
    c, p = self, self.p
    # Do this now: w may go away.
    w = g.app.gui.get_focus(c)
    inBody = g.app.gui.widget_name(w).startswith('body')
    if inBody:
        p.saveCursorAndScroll()
    if g.app.disableSave:
        g.es("save commands disabled", color="purple")
        return
    c.init_error_dialogs()
    # 2013/09/28: add fileName keyword arg for leoBridge scripts.
    if fileName:
        c.frame.title = g.computeWindowTitle(fileName)
        c.mFileName = fileName
    # Make sure we never pass None to the ctor.
    if not c.mFileName:
        c.frame.title = ""
    if not fileName:
        fileName = ''.join(c.k.givenArgs)
    if not fileName:
        fileName = g.app.gui.runSaveFileDialog(c,
            title="Save As",
            filetypes=[("Leo files", "*.leo *.db"),],
            defaultextension=g.defaultLeoFileExtension(c))
    c.bringToFront()
    if fileName:
        # Fix bug 998090: save file as doesn't remove entry from open file list.
        if c.mFileName:
            g.app.forgetOpenFile(c.mFileName)
        # Don't change mFileName until the dialog has suceeded.
        c.mFileName = g.ensure_extension(fileName, g.defaultLeoFileExtension(c))
        # Part of the fix for https://bugs.launchpad.net/leo-editor/+bug/1194209
        c.frame.title = title = c.computeWindowTitle(c.mFileName)
        c.frame.setTitle(title)
            # 2013/08/04: use c.computeWindowTitle.
        c.openDirectory = c.frame.openDirectory = g.os_path_dirname(c.mFileName)
            # Bug fix in 4.4b2.
        # Calls c.clearChanged() if no error.
        if hasattr(c.frame, 'top'):
            c.frame.top.leo_master.setTabName(c, c.mFileName)
        c.fileCommands.saveAs(c.mFileName)
        g.app.recentFilesManager.updateRecentFiles(c.mFileName)
        g.chdir(c.mFileName)
    # Done in FileCommands.saveAs.
    # c.redraw_after_icons_changed()
    c.raise_error_dialogs(kind='write')
    # *Safely* restore focus, without using the old w directly.
    if inBody:
        c.bodyWantsFocus()
        p.restoreCursorAndScroll()
    else:
        c.treeWantsFocus()
#@+node:ekr.20031218072017.2836: *3* c_file.saveTo
@g.commander_command('save-to')
@g.commander_command('file-save-to')
@g.commander_command('save-file-to')
def saveTo(self, event=None, fileName=None, silent=False):
    """
    Save a Leo outline to a file, prompting for a new file name unless the
    fileName kwarg is given. Leave the file name of the Leo outline unchanged.

    kwarg: a file name, for use by scripts using Leo's bridge.
    """
    c, p = self, self.p
    # Do this now: w may go away.
    w = g.app.gui.get_focus(c)
    inBody = g.app.gui.widget_name(w).startswith('body')
    if inBody:
        p.saveCursorAndScroll()
    if g.app.disableSave:
        g.es("save commands disabled", color="purple")
        return
    c.init_error_dialogs()
    # Add fileName keyword arg for leoBridge scripts.
    if not fileName:
        # set local fileName, _not_ c.mFileName
        fileName = ''.join(c.k.givenArgs)
    if not fileName:
        fileName = g.app.gui.runSaveFileDialog(c,
            title="Save To",
            filetypes=[("Leo files", "*.leo *.db"),],
            defaultextension=g.defaultLeoFileExtension(c))
    c.bringToFront()
    if fileName:
        c.fileCommands.saveTo(fileName, silent=silent)
        g.app.recentFilesManager.updateRecentFiles(fileName)
        g.chdir(fileName)
    c.raise_error_dialogs(kind='write')
    # *Safely* restore focus, without using the old w directly.
    if inBody:
        c.bodyWantsFocus()
        p.restoreCursorAndScroll()
    else:
        c.treeWantsFocus()
    c.outerUpdate()
#@+node:ekr.20031218072017.2837: *3* c_file.revert
@g.commander_command('revert')
def revert(self, event=None):
    """Revert the contents of a Leo outline to last saved contents."""
    c = self
    # Make sure the user wants to Revert.
    fn = c.mFileName
    if not fn:
        g.es('can not revert unnamed file.')
    if not g.os_path_exists(fn):
        g.es(f"Can not revert unsaved file: {fn}")
        return
    reply = g.app.gui.runAskYesNoDialog(
        c, 'Revert', f"Revert to previous version of {fn}?")
    c.bringToFront()
    if reply == "yes":
        g.app.loadManager.revertCommander(c)
#@+node:ekr.20210316075815.1: *3* c_file.save-as-leojs
@g.commander_command('file-save-as-leojs')
@g.commander_command('save-file-as-leojs')
def save_as_leojs(self, event=None):
    """
    Save a Leo outline as a JSON (.leojs) file with a new file name.
    """
    c = self
    fileName = g.app.gui.runSaveFileDialog(c,
        title="Save As JSON (.leojs)",
        filetypes=[("Leo files", "*.leojs")],
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
def save_as_zipped(self, event=None):
    """
    Save a Leo outline as a zipped (.db) file with a new file name.
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
def save_as_xml(self, event=None):
    """
    Save a Leo outline as a .leo file with a new file name.
    
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
#@+node:ekr.20031218072017.2849: ** Export
#@+node:ekr.20031218072017.2850: *3* c_file.exportHeadlines
@g.commander_command('export-headlines')
def exportHeadlines(self, event=None):
    """Export all headlines to an external file."""
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
def flattenOutline(self, event=None):
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
def flattenOutlineToNode(self, event=None):
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
def outlineToCWEB(self, event=None):
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
def outlineToNoweb(self, event=None):
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
def removeSentinels(self, event=None):
    """Import one or more files, removing any sentinels."""
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
def weave(self, event=None):
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
def readAtAutoNodes(self, event=None):
    """Read all @auto nodes in the presently selected outline."""
    c, p, u = self, self.p, self.undoer
    c.endEditing()
    c.init_error_dialogs()
    undoData = u.beforeChangeTree(p)
    c.importCommands.readAtAutoNodes()
    u.afterChangeTree(p, 'Read @auto Nodes', undoData)
    c.redraw()
    c.raise_error_dialogs(kind='read')
#@+node:ekr.20031218072017.1839: *3* c_file.readAtFileNodes
@g.commander_command('read-at-file-nodes')
def readAtFileNodes(self, event=None):
    """Read all @file nodes in the presently selected outline."""
    c, p, u = self, self.p, self.undoer
    c.endEditing()
    undoData = u.beforeChangeTree(p)
    c.endEditing()
    c.atFileCommands.readAllSelected(p)
    # Force an update of the body pane.
    c.setBodyString(p, p.b)  # Not a do-nothing!
    u.afterChangeTree(p, 'Read @file Nodes', undoData)
    c.redraw()
#@+node:ekr.20080801071227.4: *3* c_file.readAtShadowNodes
@g.commander_command('read-at-shadow-nodes')
def readAtShadowNodes(self, event=None):
    """Read all @shadow nodes in the presently selected outline."""
    c, p, u = self, self.p, self.undoer
    c.endEditing()
    c.init_error_dialogs()
    undoData = u.beforeChangeTree(p)
    c.atFileCommands.readAtShadowNodes(p)
    u.afterChangeTree(p, 'Read @shadow Nodes', undoData)
    c.redraw()
    c.raise_error_dialogs(kind='read')
#@+node:ekr.20070915134101: *3* c_file.readFileIntoNode
@g.commander_command('read-file-into-node')
def readFileIntoNode(self, event=None):
    """Read a file into a single node."""
    c = self
    undoType = 'Read File Into Node'
    c.endEditing()
    filetypes = [("All files", "*"), ("Python files", "*.py"), ("Leo files", "*.leo"),]
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
    p = c.insertHeadline(op_name=undoType)
    p.setHeadString('@read-file-into-node ' + fileName)
    p.setBodyString(s)
    w.setAllText(s)
    c.redraw(p)
#@+node:ekr.20031218072017.2839: *3* c_file.readOutlineOnly
@g.commander_command('read-outline-only')
def readOutlineOnly(self, event=None):
    """Open a Leo outline from a .leo file, but do not read any derived files."""
    c = self
    c.endEditing()
    fileName = g.app.gui.runOpenFileDialog(c,
        title="Read Outline Only",
        filetypes=[("Leo files", "*.leo"), ("All files", "*")],
        defaultextension=".leo")
    if not fileName:
        return
    try:
        # pylint: disable=assignment-from-no-return
        # Can't use 'with" because readOutlineOnly closes the file.
        theFile = open(fileName, 'r')
        g.chdir(fileName)
        c = g.app.newCommander(fileName)
        frame = c.frame
        frame.deiconify()
        frame.lift()
        c.fileCommands.readOutlineOnly(theFile, fileName)  # closes file.
    except Exception:
        g.es("can not open:", fileName)
#@+node:ekr.20070915142635: *3* c_file.writeFileFromNode
@g.commander_command('write-file-from-node')
def writeFileFromNode(self, event=None):
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
            filetypes=[("All files", "*"), ("Python files", "*.py"), ("Leo files", "*.leo")],
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
def cleanRecentFiles(self, event=None):
    """
    Remove items from the recent files list that no longer exist.

    This almost never does anything because Leo's startup logic removes
    nonexistent files from the recent files list.
    """
    c = self
    g.app.recentFilesManager.cleanRecentFiles(c)
#@+node:ekr.20031218072017.2080: *3* c_file.clearRecentFiles
@g.commander_command('clear-recent-files')
def clearRecentFiles(self, event=None):
    """Clear the recent files list, then add the present file."""
    c = self
    g.app.recentFilesManager.clearRecentFiles(c)
#@+node:vitalije.20170703115710.1: *3* c_file.editRecentFiles
@g.commander_command('edit-recent-files')
def editRecentFiles(self, event=None):
    """Opens recent files list in a new node for editing."""
    c = self
    g.app.recentFilesManager.editRecentFiles(c)
#@+node:ekr.20031218072017.2081: *3* c_file.openRecentFile
@g.commander_command('open-recent-file')
def openRecentFile(self, event=None, fn=None):
    c = self
    # Automatically close the previous window if...
    closeFlag = (
        c.frame.startupWindow and
            # The window was open on startup
        not c.changed and not c.frame.saved and
            # The window has never been changed
        g.app.numberOfUntitledWindows == 1)
            # Only one untitled window has ever been opened.
    if g.doHook("recentfiles1", c=c, p=c.p, v=c.p, fileName=fn, closeFlag=closeFlag):
        return
    c2 = g.openWithFileName(fn, old_c=c)
    if c2:
        g.app.makeAllBindings()
    if closeFlag and c2 and c2 != c:
        g.app.destroyWindow(c.frame)
        c2.setLog()
        g.doHook("recentfiles2",
            c=c2, p=c2.p, v=c2.p, fileName=fn, closeFlag=closeFlag)
#@+node:tbrown.20080509212202.8: *3* c_file.sortRecentFiles
@g.commander_command('sort-recent-files')
def sortRecentFiles(self, event=None):
    """Sort the recent files list."""
    c = self
    g.app.recentFilesManager.sortRecentFiles(c)
#@+node:vitalije.20170703115710.2: *3* c_file.writeEditedRecentFiles
@g.commander_command('write-edited-recent-files')
def writeEditedRecentFiles(self, event=None):
    """
    Write content of "edit_headline" node as recentFiles and recreates
    menues.
    """
    c = self
    g.app.recentFilesManager.writeEditedRecentFiles(c)
#@+node:vitalije.20170831154859.1: ** Reference outline commands
#@+node:vitalije.20170831154830.1: *3* c_file.updateRefLeoFile
@g.commander_command('update-ref-file')
def updateRefLeoFile(self, event=None):
    """
    Saves only the **public part** of this outline to the reference Leo
    file. The public part consists of all nodes above the **special
    separator node**, a top-level node whose headline is
    `---begin-private-area---`.

    Below this special node is **private area** where one can freely make
    changes that should not be copied (published) to the reference Leo file.

    **Note**: Use the set-reference-file command to create the separator node.
    """
    c = self
    c.fileCommands.save_ref()
#@+node:vitalije.20170831154840.1: *3* c_file.readRefLeoFile
@g.commander_command('read-ref-file')
def readRefLeoFile(self, event=None):
    """
    This command *completely replaces* the **public part** of this outline
    with the contents of the reference Leo file. The public part consists
    of all nodes above the top-level node whose headline is
    `---begin-private-area---`.

    Below this special node is **private area** where one can freely make
    changes that should not be copied (published) to the reference Leo file.

    **Note**: Use the set-reference-file command to create the separator node.
    """
    c = self
    c.fileCommands.updateFromRefFile()
#@+node:vitalije.20170831154850.1: *3* c_file.setReferenceFile
@g.commander_command('set-reference-file')
def setReferenceFile(self, event=None):
    """
    Shows a file open dialog allowing you to select a **reference** Leo
    document to which this outline will be connected.

    This command creates a **special separator node**, a top-level node
    whose headline is `---begin-private-area---` and whose body is the path
    to reference Leo file.

    The separator node splits the outline into two parts. The **public
    part** consists of all nodes above the separator node. The **private
    part** consists of all nodes below the separator node.

    The update-ref-file and read-ref-file commands operate on the **public
    part** of the outline. The update-ref-file command saves *only* the
    public part of the outline to reference Leo file. The read-ref-file
    command *completely replaces* the public part of the outline with the
    contents of reference Leo file.
    """
    c = self
    fileName = g.app.gui.runOpenFileDialog(c,
            title="Select reference Leo file",
            filetypes=[("Leo files", "*.leo *.db"),],
            defaultextension=g.defaultLeoFileExtension(c))
    if not fileName:
        return
    c.fileCommands.setReferenceFile(fileName)
#@+node:ekr.20180312043352.1: ** Themes
#@+node:ekr.20180312043352.2: *3* c_file.open_theme_file
@g.commander_command('open-theme-file')
def open_theme_file(self, event):
    """Open a theme file in a new session and apply the theme."""
    c = event and event.get('c')
    if not c:
        return
    # Get the file name.
    themes_dir = g.os_path_finalize_join(g.app.loadDir, '..', 'themes')
    fn = g.app.gui.runOpenFileDialog(c,
        title="Open Theme File",
        filetypes=[
            ("Leo files", "*.leo *.db"),
            ("All files", "*"),
        ],
        defaultextension=g.defaultLeoFileExtension(c),
        startpath=themes_dir,
    )
    if not fn:
        return
    leo_dir = g.os_path_finalize_join(g.app.loadDir, '..', '..')
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
