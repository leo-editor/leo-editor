# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20160306114544.1: * @file leoExternalFiles.py
#@@first
import leo.core.leoGlobals as g
import getpass
import os
import subprocess
import tempfile
import time
#@+others
#@+node:ekr.20160306110233.1: ** class ExternalFile
class ExternalFile:
    '''A class holding all data about an external file.'''

    def __init__(self, c, ext, p, path, time):
        '''Ctor for ExternalFile class.'''
        self.c = c
        self.ext = ext
        self.p = p and p.copy()
            # The nearest @<file> node.
        self.path = path
        self.time = time

    def __repr__(self):
        return f"<ExternalFile: {self.time:20} {g.shortFilename(self.path)}>"

    __str__ = __repr__
    #@+others
    #@+node:ekr.20161011174757.1: *3* ef.shortFileName
    def shortFileName(self):
        return g.shortFilename(self.path)
    #@+node:ekr.20161011174800.1: *3* ef.exists
    def exists(self):
        '''Return True if the external file still exists.'''
        return g.os_path_exists(self.path)
    #@-others
#@+node:ekr.20150405073203.1: ** class ExternalFilesController
class ExternalFilesController:
    '''
    A class tracking changes to external files:

    - temp files created by open-with commands.
    - external files corresponding to @file nodes.

    This class raises a dialog when a file changes outside of Leo.

    **Naming conventions**:

    - d is always a dict created by the @open-with logic.
      This dict describes *only* how to open the file.

    - ef is always an ExternalFiles instance.
    '''
    #@+others
    #@+node:ekr.20150404083533.1: *3* efc.ctor
    def __init__(self, c=None):
        '''Ctor for ExternalFiles class.'''
        self.checksum_d = {}
            # Keys are full paths, values are file checksums.
        self.enabled_d = {}
            # For efc.on_idle.
            # Keys are commanders.
            # Values are cached @bool check-for-changed-external-file settings.
        self.files = []
            # List of ExternalFile instances created by self.open_with.
        self.has_changed_d = {}
            # Keys are commanders. Values are bools.
            # Used only to limit traces.
        self.unchecked_commanders = []
            # Copy of g.app.commanders()
        self.unchecked_files = []
            # Copy of self file. Only one files is checked at idle time.
        self._time_d = {}
            # Keys are full paths, values are modification times.
            # DO NOT alter directly, use set_time(path) and
            # get_time(path), see set_time() for notes.
        self.yesno_all_time = 0  # previous yes/no to all answer, time of answer
        self.yesno_all_answer = None  # answer, 'yes-all', or 'no-all'
        g.app.idleTimeManager.add_callback(self.on_idle)
    #@+node:ekr.20150405105938.1: *3* efc.entries
    #@+node:ekr.20150405194745.1: *4* efc.check_overwrite (called from c.checkTimeStamp)
    def check_overwrite(self, c, path):
        '''
        Implements c.checkTimeStamp.

        Return True if the file given by fn has not been changed
        since Leo read it or if the user agrees to overwrite it.
        '''
        if c.sqlite_connection and c.mFileName == path:
            # sqlite database file is never actually overwriten by Leo
            # so no need to check its timestamp. It is modified through
            # sqlite methods.
            return True
        if self.has_changed(c, path):
            return self.ask(c, path)
        return True
    #@+node:ekr.20031218072017.2613: *4* efc.destroy_frame
    def destroy_frame(self, frame):
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
    def find_path_for_node(self, p):
        '''
        Find the path corresponding to node p.
        called from vim.py.
        '''
        for ef in self.files:
            if ef.p and ef.p.v == p.v:
                path = ef.path
                break
        else:
            path = None
        return path
    #@+node:ekr.20150330033306.1: *4* efc.on_idle & helpers
    on_idle_count = 0

    def on_idle(self):
        '''
        Check for changed open-with files and all external files in commanders
        for which @bool check_for_changed_external_file is True.
        '''
        if not g.app or g.app.killed:
            return
        self.on_idle_count += 1
        # New in Leo 5.7: always handle delayed requests.
        if g.app.windowList:
            c = g.app.log and g.app.log.c
            if c:
                c.outerUpdate()
        if 1:
            # Fix #262: Improve performance when @bool check-for-changed-external-files is True.
            if self.unchecked_files:
                # Check all external files.
                for ef in self.unchecked_files:
                    self.idle_check_open_with_file(ef)
                self.unchecked_files = []
            elif self.unchecked_commanders:
                # Check the next commander for which
                # @bool check_for_changed_external_file is True.
                c = self.unchecked_commanders.pop()
                self.idle_check_commander(c)
            else:
                # Add all commanders for which
                # @bool check_for_changed_external_file is True.
                self.unchecked_commanders = [
                    z for z in g.app.commanders() if self.is_enabled(z)
                ]
                self.unchecked_files = [z for z in self.files if z.exists()]
        else:
            # First, check all existing open-with files.
            for ef in self.files:  # A list of ExternalFile instances.
                if ef.exists():
                    self.idle_check_open_with_file(ef)
            # Next, check all commanders for which
            # @bool check_for_changed_external_file is True.
            for c in g.app.commanders():
                if self.is_enabled(c):
                    self.idle_check_commander(c)
    #@+node:ekr.20150404045115.1: *5* efc.idle_check_commander
    def idle_check_commander(self, c):
        '''
        Check all external files corresponding to @<file> nodes in c for
        changes.
        '''
        # #1100: always scan the entire file for @<file> nodes.
        # #1134: Nested @<file> nodes are no longer valid, but this will do no harm.
        for p in c.all_unique_positions():
            if p.isAnyAtFileNode():
                self.idle_check_at_file_node(c, p)
    #@+node:ekr.20150403044823.1: *5* efc.idle_check_at_file_node
    def idle_check_at_file_node(self, c, p):
        '''Check the @<file> node at p for external changes.'''
        trace = False
            # Matt, set this to True, but only for the file that interests you.\
            # trace = p.h == '@file unregister-leo.leox'
        path = g.fullPath(c, p)
        has_changed = self.has_changed(c, path)
        if trace:
            g.trace('changed', has_changed, p.h)
        if has_changed:
            if p.isAtAsisFileNode() or p.isAtNoSentFileNode():
                # Fix #1081: issue a warning.
                self.warn(c, path, p=p)
            elif self.ask(c, path, p=p):
                c.redraw(p=p)
                c.refreshFromDisk(p)
                c.redraw()
            # Always update the path & time to prevent future warnings.
            self.set_time(path)
            self.checksum_d[path] = self.checksum(path)
    #@+node:ekr.20150407124259.1: *5* efc.idle_check_open_with_file & helper
    def idle_check_open_with_file(self, ef):
        '''Update the open-with node given by ef.'''
        assert isinstance(ef, ExternalFile), ef
        if ef.path and os.path.exists(ef.path):
            time = self.get_mtime(ef.path)
            if time and time != ef.time:
                ef.time = time  # inhibit endless dialog loop.
                self.update_open_with_node(ef)
    #@+node:ekr.20150407205631.1: *6* efc.update_open_with_node
    def update_open_with_node(self, ef):
        '''Update the body text of ef.p to the contents of ef.path.'''
        assert isinstance(ef, ExternalFile), ef
        c, p = ef.c, ef.p.copy()
        # Ask the user how to resolve the conflict.
        if self.ask(c, ef.path, p=p):
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
    def open_with(self, c, d):
        '''
        Called by c.openWith to handle items in the Open With... menu.

        'd' a dict created from an @openwith settings node with these keys:

            'args':     the command-line arguments to be used to open the file.
            'ext':      the file extension.
            'kind':     the method used to open the file, such as subprocess.Popen.
            'name':     menu label (used only by the menu code).
            'p':        the nearest @<file> node, or None.
            'shortcut': menu shortcut (used only by the menu code).
        '''
        try:
            ext = d.get('ext')
            if not g.doHook('openwith1', c=c, p=c.p, v=c.p.v, d=d):
                root = d.get('p')
                if root:
                    # Open the external file itself.
                    directory = g.setDefaultDirectory(c, root)
                    fn = c.expand_path_expression(root.anyAtFileNodeName())  # 1341
                    path = g.os_path_finalize_join(directory, fn)  # 1341
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
    def compute_ext(self, c, p, ext):
        '''Return the file extension to be used in the temp file.'''
        if ext:
            for ch in ("'", '"'):
                if ext.startswith(ch): ext = ext.strip(ch)
        if not ext:
            # if node is part of @<file> tree, get ext from file name
            for p2 in p.self_and_parents(copy=False):
                if p2.isAnyAtFileNode():
                    fn = p2.h.split(None, 1)[1]
                    ext = g.os_path_splitext(fn)[1]
                    break
        if not ext:
            theDict = c.scanAllDirectives()
            language = theDict.get('language')
            ext = g.app.language_extension_dict.get(language)
        if not ext:
            ext = '.txt'
        if ext[0] != '.':
            ext = '.' + ext
        return ext
    #@+node:ekr.20031218072017.2832: *5* efc.compute_temp_file_path & helpers
    def compute_temp_file_path(self, c, p, ext):
        '''Return the path to the temp file for p and ext.'''
        if c.config.getBool('open-with-clean-filenames'):
            path = self.clean_file_name(c, ext, p)
        else:
            path = self.legacy_file_name(c, ext, p)
        if not path:
            g.error('c.temp_file_path failed')
        return path
    #@+node:ekr.20150406055221.2: *6* efc.clean_file_name
    def clean_file_name(self, c, ext, p):
        '''Compute the file name when subdirectories mirror the node's hierarchy in Leo.'''
        use_extentions = c.config.getBool('open-with-uses-derived-file-extensions')
        ancestors, found = [], False
        for p2 in p.self_and_parents(copy=False):
            h = p2.anyAtFileNodeName()
            if not h:
                h = p2.h  # Not an @file node: use the entire header
            elif use_extentions and not found:
                # Found the nearest ancestor @<file> node.
                found = True
                base, ext2 = g.os_path_splitext(h)
                if p2 == p: h = base
                if ext2: ext = ext2
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
    def legacy_file_name(self, c, ext, p):
        '''Compute a legacy file name for unsupported operating systems.'''
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
    def create_temp_file(self, c, ext, p):
        '''
        Create the file used by open-with if necessary.
        Add the corresponding ExternalFile instance to self.files
        '''
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
    def open_file_in_external_editor(self, c, d, fn, testing=False):
        '''
        Open a file fn in an external editor.

        This will be an entire external file, or a temp file for a single node.

        d is a dictionary created from an @openwith settings node.

            'args':     the command-line arguments to be used to open the file.
            'ext':      the file extension.
            'kind':     the method used to open the file, such as subprocess.Popen.
            'name':     menu label (used only by the menu code).
            'p':        the nearest @<file> node, or None.
            'shortcut': menu shortcut (used only by the menu code).
        '''
        testing = testing or g.unitTesting
        arg_tuple = d.get('args', [])
        arg = ' '.join(arg_tuple)
        kind = d.get('kind')
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
                if not testing: os.spawnl(os.P_NOWAIT, arg, filename, fn)
            elif kind == 'os.spawnv':
                filename = os.path.basename(arg_tuple[0])
                vtuple = arg_tuple[1:]
                vtuple.insert(0, filename)
                    # add the name of the program as the first argument.
                    # Change suggested by Jim Sizelove.
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
            elif hasattr(kind, '__call__'):
                # Invoke openWith like this:
                # c.openWith(data=[func,None,None])
                # func will be called with one arg, the filename
                command = f"{kind}({fn})"
                if not testing: kind(fn)
            else:
                command = 'bad command:' + str(kind)
                if not testing: g.trace(command)
            return command  # for unit testing.
        except Exception:
            g.es('exception executing open-with command:', command)
            g.es_exception()
            return f"oops: {command}"
    #@+node:ekr.20190123051253.1: *5* efc.remove_temp_file
    def remove_temp_file(self, p, path):
        '''
        Remove any existing *temp* file for p and path, updating self.files.
        '''
        for ef in self.files:
            if path and path == ef.path and p.v == ef.p.v:
                self.destroy_temp_file(ef)
                self.files = [z for z in self.files if z != ef]
                return
    #@+node:ekr.20150404092538.1: *4* efc.shut_down
    def shut_down(self):
        '''
        Destroy all temporary open-with files.
        This may fail if the files are still open.

        Called by g.app.finishQuit.
        '''
        # Dont call g.es or g.trace! The log stream no longer exists.
        for ef in self.files[:]:
            self.destroy_temp_file(ef)
        self.files = []
    #@+node:ekr.20150405110219.1: *3* efc.utilities
    # pylint: disable=no-value-for-parameter
    #@+node:ekr.20150405200212.1: *4* efc.ask
    def ask(self, c, path, p=None):
        '''
        Ask user whether to overwrite an @<file> tree.
        Return True if the user agrees.
        '''
        if g.unitTesting:
            return False
        if c not in g.app.commanders():
            return False
        if self.yesno_all_time + 3 >= time.time() and self.yesno_all_answer:
            self.yesno_all_time = time.time()  # Still reloading?  Extend time.
            return bool('yes' in self.yesno_all_answer.lower())
        if not p:
            for ef in self.files:
                if ef.path == path:
                    where = ef.p.h
                    break
            else:
                where = 'the outline node'
        else:
            where = p.h
        _is_leo = path.endswith(('.leo', '.db'))
        if _is_leo:
            s = '\n'.join([
                f"{g.splitLongFileName(path)} has changed outside Leo.",
                'Overwrite it?'
            ])
        else:
            s = '\n'.join([
                f"{g.splitLongFileName(path)} has changed outside Leo.",
                f"Reload {where} in Leo?",
            ])
        result = g.app.gui.runAskYesNoDialog(c, 'Overwrite the version in Leo?', s,
            yes_all=not _is_leo, no_all=not _is_leo)
        if result and "-all" in result.lower():
            self.yesno_all_time = time.time()
            self.yesno_all_answer = result.lower()
        return bool(result and 'yes' in result.lower())
            # Careful: may be unit testing.
    #@+node:ekr.20150404052819.1: *4* efc.checksum
    def checksum(self, path):
        '''Return the checksum of the file at the given path.'''
        import hashlib
        # #1454: Explicitly close the file.
        with open(path, 'rb') as f:
            s = f.read()
        return hashlib.md5(s).hexdigest()
    #@+node:ekr.20031218072017.2614: *4* efc.destroy_temp_file
    def destroy_temp_file(self, ef):
        '''Destroy the *temp* file corresponding to ef, an ExternalFile instance.'''
        # Do not use g.trace here.
        if ef.path and g.os_path_exists(ef.path):
            try:
                os.remove(ef.path)
            except Exception:
                pass
    #@+node:ekr.20150407204201.1: *4* efc.get_mtime
    def get_mtime(self, path):
        '''Return the modification time for the path.'''
        return g.os_path_getmtime(g.os_path_realpath(path))
    #@+node:ekr.20150405122428.1: *4* efc.get_time
    def get_time(self, path):
        '''
        return timestamp for path

        see set_time() for notes
        '''
        return self._time_d.get(g.os_path_realpath(path))
    #@+node:ekr.20150403045207.1: *4* efc.has_changed
    def has_changed(self, c, path):
        '''Return True if p's external file has changed outside of Leo.'''
        if not g.os_path_exists(path):
            return False
        if g.os_path_isdir(path):
            return False
        #
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
        #
        # Check the checksums *only* if the mod times don't match.
        old_sum = self.checksum_d.get(path)
        new_sum = self.checksum(path)
        if new_sum == old_sum:
            # The modtime changed, but it's contents didn't.
            # Update the time, so we don't keep checking the checksums.
            # Return False so we don't prompt the user for an update.
            self.set_time(path, new_time)
            return False
        # The file has really changed.
        assert old_time, path
        # #208: external change overwrite protection only works once.
        # If the Leo version is changed (dirtied) again,
        # overwrite will occur without warning.
            # self.set_time(path, new_time)
            # self.checksum_d[path] = new_sum
        return True
    #@+node:ekr.20150405104340.1: *4* efc.is_enabled
    def is_enabled(self, c):
        '''Return the cached @bool check_for_changed_external_file setting.'''
        d = self.enabled_d
        val = d.get(c)
        if val is None:
            val = c.config.getBool('check-for-changed-external-files', default=False)
            d[c] = val
        return val
    #@+node:ekr.20150404083049.1: *4* efc.join
    def join(self, s1, s2):
        '''Return s1 + ' ' + s2'''
        return f"{s1} {s2}"
    #@+node:tbrown.20150904102518.1: *4* efc.set_time
    def set_time(self, path, new_time=None):
        '''
        Implements c.setTimeStamp.

        Update the timestamp for path.

        NOTE: file paths with symbolic links occur with and without those links
        resolved depending on the code call path.  This inconsistency is
        probably not Leo's fault but an underlying Python issue.
        Hence the need to call realpath() here.
        '''
        t = new_time or self.get_mtime(path)
        self._time_d[g.os_path_realpath(path)] = t
    #@+node:ekr.20190218055230.1: *4* efc.warn
    def warn(self, c, path, p):
        '''
        Warn that an @asis or @nosent node has been changed externally.
        
        There is *no way* to update the tree automatically.
        '''
        if g.unitTesting or c not in g.app.commanders():
            return
        if not p:
            g.trace('NO P')
            return
        g.app.gui.runAskOkDialog(
            c=c,
            message='\n'.join([
                f"{g.splitLongFileName(path)} has changed outside Leo.\n",
                'Leo can not update this file automatically.\n',
                f"This file was created from {p.h}.\n",
                'Warning: refresh-from-disk will destroy all children.'
            ]),
            title='External file changed',
        )
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
