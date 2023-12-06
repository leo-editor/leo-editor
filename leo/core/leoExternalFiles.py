#@+leo-ver=5-thin
#@+node:ekr.20160306114544.1: * @file leoExternalFiles.py
#@+<< leoExternalFiles imports & annotations >>
#@+node:ekr.20220821202943.1: ** << leoExternalFiles imports & annotations >>
from __future__ import annotations
from collections.abc import Callable
import getpass
import os
import subprocess
import tempfile
from typing import Any, Optional, TYPE_CHECKING
from leo.core import leoGlobals as g

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position
    Widget = Any
#@-<< leoExternalFiles imports & annotations >>

#@+others
#@+node:ekr.20160306110233.1: ** class ExternalFile
class ExternalFile:
    """A class holding all data about an external file."""

    def __init__(self, c: Cmdr, ext: str, p: Position, path: str, time: Any) -> None:
        """Ctor for ExternalFile class."""
        self.c = c
        self.ext = ext
        self.p = p and p.copy()  # The nearest @<file> node.
        self.path = path
        # Inhibit endless dialog loop. See efc.idle_check_open_with_file.
        self.time = time

    def __repr__(self) -> str:
        return f"<ExternalFile: {self.time:20} {g.shortFilename(self.path)}>"

    __str__ = __repr__
    #@+others
    #@+node:ekr.20161011174757.1: *3* ef.shortFileName
    def shortFileName(self) -> str:
        return g.shortFilename(self.path)
    #@+node:ekr.20161011174800.1: *3* ef.exists
    def exists(self) -> bool:
        """Return True if the external file still exists."""
        return g.os_path_exists(self.path)
    #@-others
#@+node:ekr.20150405073203.1: ** class ExternalFilesController
class ExternalFilesController:
    """
    A class tracking changes to external files:

    - temp files created by open-with commands.
    - external files corresponding to @file nodes.

    This class raises a dialog when a file changes outside of Leo.

    **Naming conventions**:

    - d is always a dict created by the @open-with logic.
      This dict describes *only* how to open the file.

    - ef is always an ExternalFiles instance.
    """
    #@+others
    #@+node:ekr.20150404083533.1: *3* efc.ctor
    def __init__(self, c: Cmdr = None) -> None:
        """Ctor for ExternalFiles class."""
        self.checksum_d: dict[str, str] = {}  # Keys are full paths, values are file checksums.
        # For efc.on_idle.
        # Keys are commanders.
        # Values are cached @bool check-for-changed-external-file settings.
        self.enabled_d: dict[Cmdr, bool] = {}
        # List of ExternalFile instances created by self.open_with.
        self.files: list[Any] = []
        # Keys are commanders. Values are bools.
        # Used only to limit traces.
        self.has_changed_d: dict[Cmdr, bool] = {}
        # Copy of g.app.commanders()
        self.unchecked_commanders: list[Cmdr] = []
        # Copy of self file. Only one files is checked at idle time.
        self.unchecked_files: list[Any] = []
        # Keys are full paths, values are modification times.
        # DO NOT alter directly, use set_time(path) and
        # get_time(path), see set_time() for notes.
        self._time_d: dict[str, float] = {}
        self.yesno_all_answer: str = None  # answer, 'yes-all', or 'no-all'
        g.app.idleTimeManager.add_callback(self.on_idle)
    #@+node:ekr.20150405105938.1: *3* efc.entries
    #@+node:ekr.20150405194745.1: *4* efc.check_overwrite (called from c.checkTimeStamp)
    def check_overwrite(self, c: Cmdr, path: str) -> bool:
        """
        Implements c.checkTimeStamp.

        Return True if the file given by fn has not been changed
        since Leo read it or if the user agrees to overwrite it.
        """
        if self.has_changed(path):  # has_changed handles all special cases.
            val = self.ask(c, path)
            return val in ('yes', 'yes-all')
        return True
    #@+node:ekr.20031218072017.2613: *4* efc.destroy_frame
    def destroy_frame(self, frame: Widget) -> None:
        """
        Close all "Open With" files associated with frame.
        Called by g.app.destroyWindow.
        """
        files = [ef for ef in self.files if ef.c.frame == frame]
        paths = [ef.path for ef in files]
        for ef in files:
            self.destroy_temp_file(ef)
        self.files = [z for z in self.files if z.path not in paths]
    #@+node:ekr.20150407141838.1: *4* efc.find_path_for_node (called from vim.py)
    def find_path_for_node(self, p: Position) -> Optional[str]:
        """
        Find the path corresponding to node p.
        called from vim.py.
        """
        for ef in self.files:
            if ef.p and ef.p.v == p.v:
                path = ef.path
                break
        else:
            path = None
        return path
    #@+node:ekr.20150330033306.1: *4* efc.on_idle & helpers
    on_idle_count = 0

    def on_idle(self) -> None:
        """
        Check for changed open-with files and all external files in commanders
        for which @bool check_for_changed_external_file is True.
        """
        #
        # #1240: Note: The "asking" dialog prevents idle time.
        #
        if not g.app or g.app.killed or g.app.restarting:  # #1240.
            return
        self.on_idle_count += 1
        # New in Leo 5.7: always handle delayed requests.
        if g.app.windowList:
            c = g.app.log and g.app.log.c
            if c:
                c.outerUpdate()
        # Fix #262: Improve performance when @bool check-for-changed-external-files is True.
        if self.unchecked_files:
            # Check all external files.
            while self.unchecked_files:
                ef = self.unchecked_files.pop()  # #1959: ensure progress.
                self.idle_check_open_with_file(c, ef)
        elif self.unchecked_commanders:
            # Check the next commander for which
            #@verbatim
            # @bool check_for_changed_external_file is True.
            c = self.unchecked_commanders.pop()
            self.idle_check_commander(c)
        else:
            # Add all commanders for which
            #@verbatim
            # @bool check_for_changed_external_file is True.
            self.unchecked_commanders = [
                z for z in g.app.commanders() if self.is_enabled(z)
            ]
            self.unchecked_files = [z for z in self.files if z.exists()]
    #@+node:ekr.20150404045115.1: *5* efc.idle_check_commander
    def idle_check_commander(self, c: Cmdr) -> None:
        """
        Check all external files corresponding to @<file> nodes in c for
        changes.
        """
        # #1240: Check the .leo file itself.
        self.idle_check_leo_file(c)
        #
        # #1100: always scan the entire file for @<file> nodes.
        # #1134: Nested @<file> nodes are no longer valid, but this will do no harm.
        state = 'no'
        for p in c.all_unique_positions():
            if not p.isAnyAtFileNode():
                continue
            path = c.fullPath(p)
            if not self.has_changed(path):
                continue
            # Prevent further checks for path.
            self.set_time(path)
            self.checksum_d[path] = self.checksum(path)
            # Check file.
            if p.isAtAsisFileNode() or p.isAtNoSentFileNode():
                # #1081: issue a warning.
                self.warn(c, path, p=p)
                continue
            if state in ('yes', 'no'):
                state = self.ask(c, path, p=p)
            if state in ('yes', 'yes-all'):
                old_c = c.p
                c.selectPosition(p)  # Required.
                c.refreshFromDisk()
                c.redraw(old_c)  # #3695: Don't change c.p!
    #@+node:ekr.20201207055713.1: *5* efc.idle_check_leo_file
    def idle_check_leo_file(self, c: Cmdr) -> None:
        """Check c's .leo file for external changes."""
        path = c.fileName()
        if not self.has_changed(path):
            return

        # Always update the path & time to prevent future warnings.
        self.set_time(path)
        self.checksum_d[path] = self.checksum(path)

        # #1888:
        val = self.ask(c, path)
        if val in ('yes', 'yes-all'):
            # Do a complete restart of Leo.
            g.app.loadManager.revertCommander(c)
            g.es_print(f"reloaded {path}")
    #@+node:ekr.20150407124259.1: *5* efc.idle_check_open_with_file & helper
    def idle_check_open_with_file(self, c: Cmdr, ef: Any) -> None:
        """Update the open-with node given by ef."""
        assert isinstance(ef, ExternalFile), ef
        if not ef.path or not os.path.exists(ef.path):
            return
        time = self.get_mtime(ef.path)
        if not time or time == ef.time:
            return
        # Inhibit endless dialog loop.
        ef.time = time
        # #1888: Handle all possible user responses to self.ask.
        val = self.ask(c, ef.path, p=ef.p.copy())
        if val == 'yes-all':
            for ef in self.unchecked_files:
                self.update_open_with_node(ef)
            self.unchecked_files = []
        elif val == 'no-all':
            self.unchecked_files = []
        elif val == 'yes':
            self.update_open_with_node(ef)
        elif val == 'no':
            pass
    #@+node:ekr.20150407205631.1: *6* efc.update_open_with_node
    def update_open_with_node(self, ef: Any) -> None:
        """Update the body text of ef.p to the contents of ef.path."""
        assert isinstance(ef, ExternalFile), ef
        c, p = ef.c, ef.p.copy()
        g.blue(f"updated {p.h}")
        s, e = g.readFileIntoString(ef.path)
        p.b = s
        if c.config.getBool('open-with-goto-node-on-update'):
            c.selectPosition(p)
        if c.config.getBool('open-with-save-on-update'):
            c.save()
        else:
            p.setDirty()
            c.setChanged()
    #@+node:ekr.20150404082344.1: *4* efc.open_with & helpers
    def open_with(self, c: Cmdr, d: dict[str, Any]) -> None:
        """
        Called by c.openWith to handle items in the Open With... menu.

        'd' a dict created from an @openwith settings node with these keys:

            'args':     the command-line arguments to be used to open the file.
            'ext':      the file extension.
            'kind':     the method used to open the file, such as subprocess.Popen.
            'name':     menu label (used only by the menu code).
            'p':        the nearest @<file> node, or None.
            'shortcut': menu shortcut (used only by the menu code).
        """
        try:
            ext = d.get('ext')
            if not g.doHook('openwith1', c=c, p=c.p, v=c.p.v, d=d):
                root: Position = d.get('p')
                if root:
                    # Open the external file itself.
                    path = c.fullPath(root)  # #1914.
                    self.open_file_in_external_editor(c, d, path)
                else:
                    # Open a temp file containing just the node.
                    p = c.p
                    ext = self.compute_ext(c, p, ext)
                    path = self.compute_temp_file_path(c, p, ext)
                    if path:
                        self.remove_temp_file(p, path)
                        self.create_temp_file(c, ext, p)
                        self.open_file_in_external_editor(c, d, path)
            g.doHook('openwith2', c=c, p=c.p, v=c.p.v, d=d)
        except Exception:
            g.es('unexpected exception in c.openWith')
            g.es_exception()
    #@+node:ekr.20031218072017.2824: *5* efc.compute_ext
    def compute_ext(self, c: Cmdr, p: Position, ext: str) -> str:
        """Return the file extension to be used in the temp file."""
        if ext:
            for ch in ("'", '"'):
                if ext.startswith(ch):
                    ext = ext.strip(ch)
        if not ext:
            # if node is part of @<file> tree, get ext from file name
            for p2 in p.self_and_parents(copy=False):
                if p2.isAnyAtFileNode():
                    fn = p2.h.split(None, 1)[1]
                    ext = g.os_path_splitext(fn)[1]
                    break
        if not ext:
            theDict = c.scanAllDirectives(c.p)
            language = theDict.get('language')
            ext = g.app.language_extension_dict.get(language)
        if not ext:
            ext = '.txt'
        if ext[0] != '.':
            ext = '.' + ext
        return ext
    #@+node:ekr.20031218072017.2832: *5* efc.compute_temp_file_path & helpers
    def compute_temp_file_path(self, c: Cmdr, p: Position, ext: str) -> str:
        """Return the path to the temp file for p and ext."""
        if c.config.getBool('open-with-clean-filenames'):
            path = self.clean_file_name(c, ext, p)
        else:
            path = self.legacy_file_name(c, ext, p)
        if not path:
            g.error('c.temp_file_path failed')
        return path
    #@+node:ekr.20150406055221.2: *6* efc.clean_file_name
    def clean_file_name(self, c: Cmdr, ext: str, p: Position) -> str:
        """Compute the file name when subdirectories mirror the node's hierarchy in Leo."""
        use_extensions = c.config.getBool('open-with-uses-derived-file-extensions')
        ancestors, found = [], False
        for p2 in p.self_and_parents(copy=False):
            h = p2.anyAtFileNodeName()
            if not h:
                h = p2.h  # Not an @file node: use the entire header
            elif use_extensions and not found:
                # Found the nearest ancestor @<file> node.
                found = True
                base, ext2 = g.os_path_splitext(h)
                if p2 == p:
                    h = base
                if ext2:
                    ext = ext2
            ancestors.append(g.sanitize_filename(h))
        # The base directory is <tempdir>/Leo<id(v)>.
        ancestors.append("Leo" + str(id(p.v)))
        # Build temporary directories.
        td = os.path.abspath(tempfile.gettempdir())
        while len(ancestors) > 1:
            td = os.path.join(td, ancestors.pop())
            if not os.path.exists(td):
                os.mkdir(td)
        # Compute the full path.
        name = ancestors.pop() + ext
        path = os.path.join(td, name)
        return path
    #@+node:ekr.20150406055221.3: *6* efc.legacy_file_name
    def legacy_file_name(self, c: Cmdr, ext: str, p: Position) -> str:
        """Compute a legacy file name for unsupported operating systems."""
        try:
            leoTempDir = getpass.getuser() + "_" + "Leo"
        except Exception:
            leoTempDir = "LeoTemp"
            g.es("Could not retrieve your user name.")
            g.es(f"Temporary files will be stored in: {leoTempDir}")
        td = os.path.join(os.path.abspath(tempfile.gettempdir()), leoTempDir)
        if not os.path.exists(td):
            os.mkdir(td)
        name = g.sanitize_filename(p.h) + '_' + str(id(p.v)) + ext
        path = os.path.join(td, name)
        return path
    #@+node:ekr.20100203050306.5937: *5* efc.create_temp_file
    def create_temp_file(self, c: Cmdr, ext: str, p: Position) -> str:
        """
        Create the file used by open-with if necessary.
        Add the corresponding ExternalFile instance to self.files
        """
        path = self.compute_temp_file_path(c, p, ext)
        exists = g.os_path_exists(path)
        # Compute encoding and s.
        d2 = c.scanAllDirectives(p)
        encoding = d2.get('encoding', None)
        if encoding is None:
            encoding = c.config.default_derived_file_encoding
        s = g.toEncodedString(p.b, encoding, reportErrors=True)
        # Write the file *only* if it doesn't exist.
        # No need to read the file: recomputing s above suffices.
        if not exists:
            try:
                with open(path, 'wb') as f:
                    f.write(s)
                    f.flush()
            except IOError:
                g.error(f"exception creating temp file: {path}")
                g.es_exception()
                return None
        # Add or update the external file entry.
        time = self.get_mtime(path)
        self.files = [z for z in self.files if z.path != path]
        self.files.append(ExternalFile(c, ext, p, path, time))
        return path
    #@+node:ekr.20031218072017.2829: *5* efc.open_file_in_external_editor
    def open_file_in_external_editor(self, c: Cmdr, d: dict[str, Any], fn: str, testing: bool = False) -> str:
        """
        Open a file fn in an external editor.

        This will be an entire external file, or a temp file for a single node.

        d is a dictionary created from an @openwith settings node.

            'args':     the command-line arguments to be used to open the file.
            'ext':      the file extension.
            'kind':     the method used to open the file, such as subprocess.Popen.
            'name':     menu label (used only by the menu code).
            'p':        the nearest @<file> node, or None.
            'shortcut': menu shortcut (used only by the menu code).
        """
        testing = testing or g.unitTesting
        arg_tuple: list[str] = d.get('args', [])
        arg = ' '.join(arg_tuple)
        kind: Callable = d.get('kind')
        try:
            # All of these must be supported because they
            # could exist in @open-with nodes.
            command = '<no command>'
            if kind in ('os.system', 'os.startfile'):
                # New in Leo 5.7:
                # Use subProcess.Popen(..., shell=True)
                c_arg = self.join(arg, fn)
                if not testing:
                    try:
                        subprocess.Popen(c_arg, shell=True)
                    except OSError:
                        g.es_print('c_arg', repr(c_arg))
                        g.es_exception()
            elif kind == 'exec':
                g.es_print('open-with exec no longer valid.')
            elif kind == 'os.spawnl':
                filename = g.os_path_basename(arg)
                command = f"os.spawnl({arg},{filename},{fn})"
                if not testing:
                    os.spawnl(os.P_NOWAIT, arg, filename, fn)
            elif kind == 'os.spawnv':
                filename = os.path.basename(arg_tuple[0])
                vtuple = arg_tuple[1:]
                # add the name of the program as the first argument.
                # Change suggested by Jim Sizelove.
                vtuple.insert(0, filename)
                vtuple.append(fn)
                command = f"os.spawnv({vtuple})"
                if not testing:
                    os.spawnv(os.P_NOWAIT, arg[0], vtuple)  #???
            elif kind == 'subprocess.Popen':
                c_arg = self.join(arg, fn)
                command = f"subprocess.Popen({c_arg})"
                if not testing:
                    try:
                        subprocess.Popen(c_arg, shell=True)
                    except OSError:
                        g.es_print('c_arg', repr(c_arg))
                        g.es_exception()
            elif callable(kind):
                # Invoke openWith like this:
                # c.openWith(data=[func,None,None])
                # func will be called with one arg, the filename
                command = f"{kind}({fn})"
                if not testing:
                    kind(fn)
            else:
                command = 'bad command:' + str(kind)
                if not testing:
                    g.trace(command)
            return command  # for unit testing.
        except Exception:
            g.es('exception executing open-with command:', command)
            g.es_exception()
            return f"oops: {command}"
    #@+node:ekr.20190123051253.1: *5* efc.remove_temp_file
    def remove_temp_file(self, p: Position, path: str) -> None:
        """
        Remove any existing *temp* file for p and path, updating self.files.
        """
        for ef in self.files:
            if path and path == ef.path and p.v == ef.p.v:
                self.destroy_temp_file(ef)
                self.files = [z for z in self.files if z != ef]
                return
    #@+node:ekr.20150404092538.1: *4* efc.shut_down
    def shut_down(self) -> None:
        """
        Destroy all temporary open-with files.
        This may fail if the files are still open.

        Called by g.app.finishQuit.
        """
        # Dont call g.es or g.trace! The log stream no longer exists.
        for ef in self.files[:]:
            self.destroy_temp_file(ef)
        self.files = []
    #@+node:ekr.20150405110219.1: *3* efc.utilities
    # pylint: disable=no-value-for-parameter
    #@+node:ekr.20150405200212.1: *4* efc.ask
    def ask(self, c: Cmdr, path: str, p: Position = None) -> str:
        """
        Ask user whether to overwrite an @<file> tree.

        Return one of ('yes', 'no', 'yes-all', 'no-all')
        """
        if g.unitTesting:
            return ''
        if c not in g.app.commanders():
            return ''
        is_leo = path.endswith(('.leo', '.db'))
        is_external_file = not is_leo

        # Create the message. Concatenate strings to make finding this message easier.
        message1 = path + '\n' + 'has changed outside Leo.\n\n'
        if is_leo:
            message2 = 'Reload this outline?'
        elif p:
            message2 = f"Reload {p.h}?"
        else:
            for ef in self.files:
                if ef.path == path:
                    message2 = f"Reload {ef.p.h}?"
                    break
            else:
                message2 = f"Reload {path}?"

        # #1240: Note: This dialog prevents idle time.

        result = g.app.gui.runAskYesNoDialog(c,
            message2,
            message1 + message2,
            yes_all=is_external_file,
            no_all=is_external_file,
        )

        # #1961. Re-init the checksum to suppress concurrent dialogs.
        self.checksum_d[path] = self.checksum(path)

        # #1888: return one of ('yes', 'no', 'yes-all', 'no-all')
        return result.lower() if result else 'no'
    #@+node:ekr.20150404052819.1: *4* efc.checksum
    def checksum(self, path: str) -> str:
        """Return the checksum of the file at the given path."""
        import hashlib
        # #1454: Explicitly close the file.
        with open(path, 'rb') as f:
            s = f.read()
        return hashlib.md5(s).hexdigest()
    #@+node:ekr.20031218072017.2614: *4* efc.destroy_temp_file
    def destroy_temp_file(self, ef: Any) -> None:
        """Destroy the *temp* file corresponding to ef, an ExternalFile instance."""
        # Do not use g.trace here.
        if ef.path and g.os_path_exists(ef.path):
            try:
                os.remove(ef.path)
            except Exception:
                pass
    #@+node:ekr.20150407204201.1: *4* efc.get_mtime
    def get_mtime(self, path: str) -> float:
        """Return the modification time for the path."""
        return g.os_path_getmtime(g.os_path_realpath(path))
    #@+node:ekr.20150405122428.1: *4* efc.get_time
    def get_time(self, path: str) -> float:
        """
        return timestamp for path

        see set_time() for notes
        """
        return self._time_d.get(g.os_path_realpath(path))
    #@+node:ekr.20150403045207.1: *4* efc.has_changed
    def has_changed(self, path: str) -> bool:
        """Return True if the file at path has changed outside of Leo."""
        if not path:
            return False
        if not g.os_path_exists(path):
            return False
        if g.os_path_isdir(path):
            return False
        if path.endswith('.db'):
            return False

        # First, check the modification times.
        old_time = self.get_time(path)
        new_time = self.get_mtime(path)
        if not old_time:
            # Initialize.
            self.set_time(path, new_time)
            self.checksum_d[path] = self.checksum(path)
            return False
        if old_time == new_time:
            return False

        # Check the checksums *only* if the mod times don't match.
        old_sum = self.checksum_d.get(path)
        new_sum = self.checksum(path)
        if new_sum == old_sum:
            # The modtime changed, but its contents didn't.
            # Update the time, so we don't keep checking the checksums.
            # Return False so we don't prompt the user for an update.
            self.set_time(path, new_time)
            return False

        # The file has really changed.
        return True
    #@+node:ekr.20150405104340.1: *4* efc.is_enabled
    def is_enabled(self, c: Cmdr) -> bool:
        """Return the cached @bool check_for_changed_external_file setting."""
        d = self.enabled_d
        val = d.get(c)
        if val is None:
            val = c.config.getBool('check-for-changed-external-files', default=False)
            d[c] = val
        return val
    #@+node:ekr.20150404083049.1: *4* efc.join
    def join(self, s1: str, s2: str) -> str:
        """Return s1 + ' ' + s2"""
        return f"{s1} {s2}"
    #@+node:tbrown.20150904102518.1: *4* efc.set_time
    def set_time(self, path: str, new_time: float = None) -> None:
        """
        Implements c.setTimeStamp.

        Update the timestamp for path.

        NOTE: file paths with symbolic links occur with and without those links
        resolved depending on the code call path.  This inconsistency is
        probably not Leo's fault but an underlying Python issue.
        Hence the need to call realpath() here.
        """
        t = new_time or self.get_mtime(path)
        self._time_d[g.os_path_realpath(path)] = t
    #@+node:ekr.20190218055230.1: *4* efc.warn
    def warn(self, c: Cmdr, path: str, p: Position) -> None:
        """
        Warn that an @asis or @nosent node has been changed externally.

        There is *no way* to update the tree automatically.
        """
        if g.unitTesting or c not in g.app.commanders():
            return
        if not p:
            return
        path_name = g.splitLongFileName(path)
        kind = '@asis' if p.h.startswith('@asis') else '@nosent'
        g.app.gui.runAskOkDialog(
            c=c,
            message=(
                f"{path_name} has changed outside Leo.\n\n"
                f"An {kind} node created this file.\n\n"
                'Warning: Leo can not update this node!\n'
                'Neither refresh-from-disk nor restarting Leo will work.\n'
            ),
            title='External file changed',
        )
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
