# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20160306114544.1: * @file leoExternalFiles.py
#@@first
import leo.core.leoGlobals as g
import getpass
import os
import subprocess
import tempfile
#@+others
#@+node:ekr.20160306110233.1: ** class ExternalFile
class ExternalFile:
    '''A class holding all data about an external file.'''
    
    def __init__(self, body, c, encoding, ext, p, path, time):
        '''Ctor for ExternalFile class.'''
        self.body = body
        self.c = c
        self.encoding = encoding
        self.ext = ext
        self.p = p.copy()
        self.path = path
        self.time = time
        # self.v = p.v
        
    def __repr__(self):
        return '<ExternalFile: %20s %s>' % (self.time, g.shortFilename(self.path))
        
    __str__ = __repr__
#@+node:ekr.20150405073203.1: ** class ExternalFilesController
class ExternalFilesController:
    '''
    A class tracking changes to external files:
        
    - temp files created by open-with commands.
    - external files corresponding to @file nodes.
    
    This class raises a dialog when a file changes outside of Leo.
    
    **Convention**:
    
    - d is always a dict created by the @open-with logic.
      It would be difficult and pointless to change d.
    
    - ef is always an ExternalFiles instance.
    '''
    #@+others
    #@+node:ekr.20150404083533.1: *3* efc.ctor
    def __init__(self, c=None):
        '''Ctor for ExternalFiles class.'''
        self.checksum_d = {}
            # Keys are full paths, values are file checksums.
        self.enabled_d = {}
            # Keys are commanders.
            # Values are cached check_for_changed_external_file settings.
        self.files = []
            # List of ExternalFile instances created by self.open_with.
        self.has_changed_d = {}
            # Keys are commanders. Values are bools.
        self._time_d = {}
            # Keys are full paths, values are modification times.
            # DO NOT alter directly, use set_time(path) and
            # get_time(path), see set_time() for notes.
    #@+node:ekr.20150405105938.1: *3* efc.entries & helpers
    #@+node:ekr.20150405194745.1: *4* efc.check_overwrite (called from c.checkTimeStamp)
    def check_overwrite(self, c, path):
        '''
        Implements c.checkTimeStamp.

        Return True if the file given by fn has not been changed
        since Leo read it or if the user agrees to overwrite it.
        '''
        if self.has_changed(c, path):
            return self.ask_overwrite(c, path)
        else:
            return True
    #@+node:ekr.20031218072017.2613: *4* efc.destroy_frame & helper
    def destroy_frame(self, frame):
        """
        Close all "Open With" files associated with frame
        Called by g.app.destroyWindow.
        """
        trace = False and not g.unitTesting
        if trace: g.trace(frame.c.shortFileName())
        files = [ef for ef in self.files if ef.c.frame == frame]
        paths = [ef.path for ef in files]
        for ef in files:
            self.destroy_external_file(ef)
        self.files = [z for z in self.files if z.path not in paths]

    #@+node:ekr.20031218072017.2614: *5* efc.destroy_external_file
    def destroy_external_file(self, ef):
        '''Destroy the file corresponding to the given ExternalFile instance.'''
        trace = False and not g.unitTesting
        # Do not use g.trace here.
        if ef.path and g.os_path_exists(ef.path):
            try:
                os.remove(ef.path)
                if trace:
                    print("deleting temp file: %s" % g.shortFileName(ef.path))
            except Exception:
                if trace:
                    print("can not delete temp file: %s" % ef.path)
    #@+node:ekr.20150407141838.1: *4* efc.find_path_for_node (called from vim.py)
    def find_path_for_node(self, p):
        '''
        Find the path corresponding to node p.
        called from vim.py.
        '''
        trace = False and not g.unitTesting
        for ef in self.files:
            if ef.p and ef.p.v == p.v:
                path = ef.path
                break
        else:
            path = None
        if trace: g.trace(p.h, path)
        return path
    #@+node:ekr.20150330033306.1: *4* efc.on_idle & helpers
    def on_idle(self, timer):
        '''Check for changed files in all commanders.'''
        trace = False and not g.unitTesting
        if trace:
            import time
            t1 = time.time()
        if g.app and not g.app.killed:
            # First, check the open-with files.
            for ef in self.files:
                self.idle_check_open_with_file(ef)
            # Next, check, all @<file> nodes in all commanders.
            for c in g.app.commanders():
                self.idle_check_commander(c)
        if trace:
            t2 = time.time()
            n = len(list(g.app.commanders()))
            g.trace('%s files %4.2f sec.' % (n, t2 - t1))
    #@+node:ekr.20150404045115.1: *5* efc.idle_check_commander
    def idle_check_commander(self, c):
        '''
        Check all external files corresponding to @<file> nodes in c for
        changes.
        '''
        trace = False and not g.unitTesting
        if not self.is_enabled(c) or g.unitTesting:
            return
        # g.trace('checking',c.shortFileName())
        p = c.rootPosition()
        seen = set()
        while p:
            if p.v in seen:
                p.moveToNodeAfterTree()
            elif p.isAnyAtFileNode():
                seen.add(p.v)
                self.idle_check_node(c, p)
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
    #@+node:ekr.20150403044823.1: *5* efc.idle_check_node
    def idle_check_node(self, c, p):
        '''Check the @<file> node at p for external changes.'''
        path = g.fullPath(c, p)
        if self.has_changed(c, path):
            ok = self.ask_update(c, path)
            if ok:
                c.redraw_now(p=p)
                c.refreshFromDisk(p)
            # Always update the path & time to prevent future warnings.
            self.set_time(path)
            self.checksum_d[path] = self.checksum(path)
    #@+node:ekr.20150407124259.1: *5* efc.idle_check_open_with_file & helper
    def idle_check_open_with_file(self, ef):
        '''Update the open-with node given by d.'''
        trace = False and not g.unitTesting
        if ef.path and os.path.exists(ef.path):
            time = self.get_mtime(ef.path)
            if time and time != ef.time:
                ef.time = time # inhibit endless dialog loop.
                self.update_open_with_node(ef)
    #@+node:ekr.20150407205631.1: *6* efc.update_open_with_node & helper
    def update_open_with_node(self, ef):
        '''Update the body text of ef.p to the contents of ef.path.'''
        trace = False and not g.unitTesting
        assert isinstance(ef, ExternalFile)
        if trace: g.trace(repr(ef))
        c, p = ef.c, ef.p.copy()
        old_body = ef.body
        body = p.b
        body = g.toEncodedString(body, ef.encoding, reportErrors=True)
        s = g.readFileIntoEncodedString(ef.path)
        s = g.toEncodedString(s, ef.encoding, reportErrors=True)
        conflict = body not in (old_body, s)
        update = s != body
        if conflict:
            # Ask the user how to resolve the conflict.
            result = self.ask_conflict(c, ef.path)
            assert result in ('cancel', 'file', 'outline'), result
            if result == 'file':
                g.blue('updated %s' % p.h)
                ef.body = s
                p.b = g.toUnicode(s, encoding=ef.encoding)
                self.finish_open_with_update(c, p)
            elif result == 'outline':
                g.blue('retaining %s' % p.h)
                ef.body = body
            else:
                g.blue('ignoring conflict in %s' % p.h)
        elif update:
            g.blue('updated %s' % p.h)
            ef.body = s
            p.b = g.toUnicode(s, encoding=ef.encoding)
            self.finish_open_with_update(c, p)
    #@+node:ekr.20150407211506.1: *7* efc.finish_open_with_update
    def finish_open_with_update(self, c, p):
        '''Complete updating p.b from s.'''
        if c.config.getBool('open_with_goto_node_on_update'):
            c.selectPosition(p)
        if c.config.getBool('open_with_save_on_update'):
            c.save()
    #@+node:ekr.20150404082344.1: *4* efc.open_with & helpers (called from c.openWith)
    def open_with(self, c, d):
        '''
        Called by c.openWith to handle items in the Open With... menu.
        
        d is a dictionary created from an @openwith settings node.

        'args':     the command-line arguments to be used to open the file.
        'ext':      the file extension.
        'kind':     the method used to open the file, such as subprocess.Popen.
        'name':     menu label (used only by the menu code).
        'shortcut': menu shortcut (used only by the menu code).
        '''
        trace = False and not g.unitTesting
        if trace: self.dump_d(d, 'open_with')
        try:
            ext = d.get('ext')
            p = d.get('p') or c.p
            if not g.doHook('openwith1', c=c, p=p, v=p.v, d=d):
                d['ext'] = self.get_ext(c, p, ext)
                fn = self.open_with_helper(c, d, p)
                if fn:
                    self.open_temp_file(c, d, fn)
            g.doHook('openwith2', c=c, p=p, v=p.v, d=d)
        except Exception:
            g.es('unexpected exception in c.openWith')
            g.es_exception()
    #@+node:ekr.20031218072017.2829: *5* efc.open_temp_file
    def open_temp_file(self, c, d, fn, testing=False):
        '''
        Open the closed mkstemp file fn in an external editor.
        
        d is a dictionary created from an @openwith settings node.

        'args':     the command-line arguments to be used to open the file.
        'ext':      the file extension.
        'kind':     the method used to open the file, such as subprocess.Popen.
        'name':     menu label (used only by the menu code).
        'shortcut': menu shortcut (used only by the menu code).
        '''
        trace = False and not g.unitTesting
        testing = testing or g.unitTesting
        arg_tuple = d.get('args', [])
        arg = ' '.join(arg_tuple)
        kind = d.get('kind')
        try:
            # All of these must be supported because they
            # could exist in @open-with nodes.
            command = '<no command>'
            if kind == 'os.startfile':
                command = 'os.startfile(%s)' % self.join(arg, fn)
                if trace: g.trace(command)
                # pylint: disable=no-member
                # trust the user not to use this option on Linux.
                if not testing: os.startfile(self.join(arg, fn))
            elif kind == 'exec':
                g.es_print('open-with exec no longer valid.')
                # command = 'exec(%s)' % self.join(arg,fn)
                # if trace: g.trace(command)
                # if not testing:
                    # exec(self.join(arg,fn),{},{})
            elif kind == 'os.spawnl':
                filename = g.os_path_basename(arg)
                command = 'os.spawnl(%s,%s,%s)' % (arg, filename, fn)
                if trace: g.trace(command)
                if not testing: os.spawnl(os.P_NOWAIT, arg, filename, fn)
            elif kind == 'os.spawnv':
                filename = os.path.basename(arg_tuple[0])
                vtuple = arg_tuple[1:]
                vtuple.insert(0, filename)
                    # add the name of the program as the first argument.
                    # Change suggested by Jim Sizelove.
                vtuple.append(fn)
                command = 'os.spawnv(%s)' % (vtuple)
                if trace: g.trace(command)
                if not testing:
                    os.spawnv(os.P_NOWAIT, arg[0], vtuple) #???
            elif kind == 'subprocess.Popen':
                use_shell = True
                c_arg = self.join(arg, fn)
                command = 'subprocess.Popen(%s)' % c_arg
                if trace: g.trace(command)
                if not testing:
                    try:
                        subprocess.Popen(c_arg, shell=use_shell)
                    except OSError:
                        g.es_print('c_arg', repr(c_arg))
                        g.es_exception()
            elif g.isCallable(kind):
                # Invoke openWith like this:
                # c.openWith(data=[func,None,None])
                # func will be called with one arg, the filename
                if trace: g.trace('%s(%s)' % (kind, fn))
                command = '%s(%s)' % (kind, fn)
                if not testing: kind(fn)
            else:
                command = 'bad command:' + str(kind)
                if not testing: g.trace(command)
            return command # for unit testing.
        except Exception:
            g.es('exception executing open-with command:', command)
            g.es_exception()
            return 'oops: %s' % command
    #@+node:ekr.20100203050306.5797: *5* efc.open_with_helper & helpers
    def open_with_helper(self, c, d, p):
        '''
        Reopen a temp file for p if it exists in self.files.
        Otherwise, open a new temp file.
        '''
        trace = False and not g.unitTesting
        assert isinstance(d, dict), d
        # May be over-ridden by mod_tempfname plugin.
        path = self.temp_file_path(c, p, d.get('ext'))
        if not path:
            # Check the mod_tempfname plugin.
            return g.error('c.temp_file_path failed')
        # Return a path if a temp file already refers to p.v
        for ef in self.files:
            if path == ef.path and p.v == ef.p.v:
                if trace: g.trace('found!', path)
                return self.reopen_open_with_node(c, ef)
                    # May be None
        # Not found: create the temp file.
        if trace: g.trace('not found', path)
        return self.create_temp_file(c, d, p)
            # May be None.
    #@+node:ekr.20100203050306.5937: *6* efc.create_temp_file
    def create_temp_file(self, c, d, p):
        '''
        Create the temp file used by open-with if necessary.
        Add the corresponding ExternalFile instance to self.files
        
        d is a dictionary created from an @openwith settings node.

        'args':     the command-line arguments to be used to open the file.
        'ext':      the file extension.
        'kind':     the method used to open the file, such as subprocess.Popen.
        'name':     menu label (used only by the menu code).
        'shortcut': menu shortcut (used only by the menu code).
        '''
        trace = False and not g.unitTesting
        assert isinstance(d, dict), d
        body = d.get('body') if d and 'body' in d else c.p.b
        ext = d.get('ext')
        path = self.temp_file_path(c, p, ext)
        exists = g.os_path_exists(path)
        if trace:
            kind = 'recreating:' if exists else 'creating: '
            g.trace(kind, path)
        # Compute encoding and s.
        d = c.scanAllDirectives(p)
        encoding = d.get('encoding', None)
        if encoding is None:
            encoding = c.config.default_derived_file_encoding
        if not g.isPython3:
            body = g.toEncodedString(body, encoding, reportErrors=True)
        # Write the file *only* if it doesn't exist.
        # No need to read the file: recomputing s above suffices.
        if not exists:
            try:
                f = open(path, 'w')
                f.write(body)
                f.flush()
                f.close()
            except IOError:
                g.error('exception creating temp file: %s' % path)
                g.es_exception()
                return None
        # Add or update the external file entry.
        ef = ExternalFile(body=body,
                         c=c,
                         encoding=encoding,
                         ext=ext,
                         p=p,
                         path=path,
                         time = self.get_mtime(path))
        self.files = [z for z in self.files if z.path != path]
        self.files.append(f)
        return path
    #@+node:ekr.20031218072017.2827: *6* efc.reopen_open_with_node
    def reopen_open_with_node(self, c, d):
        '''
        Test for changes in both p and the temp file:

        - If only p's body text has changed, we recreate the temp file.
        - If only the temp file has changed, do nothing here.
        - If both have changed we must prompt the user to see which code to use.

        Return the file name.
        '''
        trace = False and not g.unitTesting
        p = d.get('p')
        ext = d.get('ext')
        ext = self.get_ext(c, p, ext)
        path = d.get('path')
        # Get the old & new body text and modification times.
        encoding = d.get('encoding')
        old_body = d.get('body')
        old_body = g.toEncodedString(old_body, encoding, reportErrors=True)
        new_body = d.get('body') if 'body' in d else p.b
        old_time = d.get('time')
        try:
            new_time = self.get_mtime(path)
        except Exception:
            new_time = None
        body_changed = old_body != new_body
        time_changed = old_time != new_time
        if body_changed and time_changed:
            # g.error('Conflict in temp file for',p.h)
            result = self.ask_conflict(c, p.h)
            d['time'] = new_time
            d['body'] = new_body
            if result is None or result.lower() == 'cancel':
                return None
            rewrite = result.lower() == 'yes'
        else:
            rewrite = body_changed
        if rewrite:
            # May be overridden by the mod_tempfname plugin.
            path = self.create_temp_file(c, d, p)
        else:
            g.trace('reopening:', path)
        return path
    #@+node:ekr.20150404092538.1: *4* efc.shut_down
    def shut_down(self):
        '''
        Destroy all temporary open-with files.
        This may fail if the files are still open.

        Called by g.app.finishQuit.
        '''
        trace = False and not g.unitTesting
        if trace: print('efc.shut_down')
        # Dont call g.es or g.trace! The log stream no longer exists.
        for ef in self.files[:]:
            self.destroy_external_file(ef)
        self.files = []
    #@+node:ekr.20150427144312.1: *3* efc.ask...
    #@+node:ekr.20150405223300.1: *4* efc.ask_conflict
    def ask_conflict(self, c, path):
        '''Ask the user how to resolve an open-with update conflict.'''
        s = '\n'.join([
            'Conflicting changes in outline and temp file.',
            'What data do you want to use?',
            '',
            'Outline: use the data in the outline.',
            'File: use the data in the temp file.',
            'Cancel: do nothing.',
        ])
        result = g.app.gui.runAskYesNoCancelDialog(c, "Conflict!", s,
            yesMessage='Outline',
            noMessage='File',
            defaultButton='Cancel')
        if result == 'yes': return 'outline'
        elif result == 'no': return 'file'
        else: return 'cancel'
    #@+node:ekr.20150405200212.1: *4* efc.ask_overwrite
    def ask_overwrite(self, c, path):
        '''
        Ask user whether to overwrite an @<file> tree.
        Return True if the user agrees.
        '''
        s = '\n'.join([
            '%s has been modified outside Leo.' % (g.splitLongFileName(path)),
            'Overwrite this file?'
        ])
        result = g.app.gui.runAskYesNoCancelDialog(c, 'Overwrite modified file?', s)
        return result.lower() == 'yes'
    #@+node:ekr.20150405200752.1: *4* efc.ask_update
    def ask_update(self, c, path):
        '''
        Ask user whether to update an @<file> tree.
        Update the file if the user agrees.
        Return True if the user agrees.
        '''
        s = '\n'.join([
            '%s has changed outside Leo.' % (g.splitLongFileName(path)),
            'Update the outline from the external file?'
        ])
        result = g.app.gui.runAskYesNoCancelDialog(c, 'Update Outline?', s)
        return result.lower() == 'yes'
    #@+node:ekr.20150405110219.1: *3* efc.utilities
    # pylint: disable=no-value-for-parameter
    #@+node:ekr.20150404052819.1: *4* efc.checksum
    def checksum(self, path):
        '''Return the checksum of the file at the given path.'''
        import hashlib
        return hashlib.md5(open(path, 'rb').read()).hexdigest()
    #@+node:ekr.20150427145447.1: *4* efc.dump_d
    def dump_d(self, d, tag):
        '''Print dictionary d.  Similar to g.printDict.'''
        if d:
            indent = ''
            n = 6
            for key in sorted(d):
                if g.isString(key):
                    n = max(n, len(key))
            g.pr('%s...{' % (tag) if tag else '{')
            for key in sorted(d):
                val = d.get(key)
                if key == 'body':
                    val = 'len(body) = %s' % (len(val))
                else:
                    val = repr(val).strip()
                # g.pr("%s%*s: %s" % (indent,n,key,repr(d.get(key)).strip()))
                g.pr("%s%*s: %s" % (indent, n, key, val))
            g.pr('}')
        else:
            g.pr('%s...{}' % (tag) if tag else '{}')
    #@+node:ekr.20031218072017.2824: *4* efc.get_ext
    def get_ext(self, c, p, ext):
        '''Return the file extension to be used in the temp file.'''
        trace = False and not g.unitTesting
        if trace: g.trace(ext)
        if ext:
            for ch in ("'", '"'):
                if ext.startswith(ch): ext = ext.strip(ch)
        if not ext:
            # if node is part of @<file> tree, get ext from file name
            for p2 in p.self_and_parents():
                if p2.isAnyAtFileNode():
                    fn = p2.h.split(None, 1)[1]
                    ext = g.os_path_splitext(fn)[1]
                    if trace: g.trace('found node:', ext, p2.h)
                    break
        if not ext:
            theDict = c.scanAllDirectives()
            language = theDict.get('language')
            ext = g.app.language_extension_dict.get(language)
            if trace: g.trace('found directive', language, ext)
        if not ext:
            ext = '.txt'
            if trace: g.trace('use default (.txt)')
        if ext[0] != '.':
            ext = '.' + ext
        if trace: g.trace(ext)
        return ext
    #@+node:ekr.20150407204201.1: *4* efc.get_mtime
    def get_mtime(self, path):
        '''Return the modification time for the path.'''
        return g.os_path_getmtime(path)
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
        trace = False and not g.unitTesting
        verbose_init = False
        tag = 'efc.has_changed'
        if not g.os_path_exists(path):
            if trace: print('%s:does not exist %s' % (tag, path))
            return False
        if g.os_path_isdir(path):
            if trace: print('%s: %s is a directory' % (tag, path))
            return False
        fn = g.shortFileName(path)
        # First, check the modification times.
        old_time = self.get_time(path)
        new_time = self.get_mtime(path)
        if not old_time:
            # Initialize.
            self.set_time(path, new_time)
            self.checksum_d[path] = checksum = self.checksum(path)
            if trace and verbose_init:
                print('%s:init %s %s %s' % (tag, checksum, c.shortFileName(), path))
            elif trace:
                # Only print one message per commander.
                d = self.has_changed_d
                val = d.get(c)
                if not val:
                    d[c] = True
                    print('%s:init %s' % (tag, c.shortFileName()))
            return False
        if old_time == new_time:
            # print('%s:times match %s %s' % (tag,c.shortFileName(),path))
            return False
        # Check the checksums *only* if the mod times don't match.
        old_sum = self.checksum_d.get(path)
        new_sum = self.checksum(path)
        if new_sum == old_sum:
            # The modtime changed, but it's contents didn't.
            # Update the time, so we don't keep checking the checksums.
            # Return False so we don't prompt the user for an update.
            if trace: print('%s:unchanged %s %s' % (tag, old_time, new_time))
            self.set_time(path, new_time)
            return False
        else:
            # The file has really changed.
            if trace: print('%s:changed %s %s %s' % (tag, old_sum, new_sum, fn))
            assert old_time, path
            if 0: # Fix bug 208: external change overwrite protection only works once
                # https://github.com/leo-editor/leo-editor/issues/208
                # These next two lines mean that if the Leo version
                # is changed (dirtied) again, overwrite will occur without warning.
                self.set_time(path, new_time)
                self.checksum_d[path] = new_sum
            return True
    #@+node:ekr.20150405104340.1: *4* efc.is_enabled
    def is_enabled(self, c):
        '''return cached @bool check_for_changed_external_file setting.'''
        trace = False and not g.unitTesting
        d = self.enabled_d
        val = d.get(c)
        if val is None:
            val = c.config.getBool('check_for_changed_external_files', default=False)
            d[c] = val
        if trace: g.trace(val, c.shortFileName())
        return val
    #@+node:ekr.20150404083049.1: *4* efc.join
    def join(self, s1, s2):
        '''Return s1 + ' ' + s2'''
        return '%s %s' % (s1, s2)
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
        trace = False and not g.unitTesting
        t = new_time or self.get_mtime(path)
        if trace: g.trace(t, path)
        self._time_d[g.os_path_realpath(path)] = t 
    #@+node:ekr.20031218072017.2832: *4* efc.temp_file_path
    def temp_file_path(self, c, p, ext):
        '''Return the path to the temp file for p and ext.'''
        trace = False and not g.unitTesting
        if c.config.getBool('open_with_clean_filenames'):
            path = self.clean_file_name(c, p, ext)
        else:
            path = self.legacy_file_name(c, p, ext)
        if trace: g.trace(p.h, path)
        return path
    #@+node:ekr.20150406055221.2: *5* efc.clean_file_name
    def clean_file_name(self, c, p, ext):
        '''Compute the file name when subdirectories mirror the node's hierarchy in Leo.'''
        trace = False and not g.unitTesting
        use_extentions = c.config.getBool('open_with_uses_derived_file_extensions')
        ancestors, found = [], False
        for p2 in p.self_and_parents():
            h = p.anyAtFileNodeName()
            if not h:
                h = p2.h # Not an @file node: use the entire header
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
                # if trace: g.trace('creating',td)
                os.mkdir(td)
        # Compute the full path.
        name = ancestors.pop() + ext
        path = os.path.join(td, name)
        if trace: g.trace(path)
        return path
    #@+node:ekr.20150406055221.3: *5* efc.legacy_file_name
    def legacy_file_name(self, c, p, ext):
        '''Compute a legacy file name for unsupported operating systems.'''
        try:
            leoTempDir = getpass.getuser() + "_" + "Leo"
        except Exception:
            leoTempDir = "LeoTemp"
            g.es("Could not retrieve your user name.")
            g.es("Temporary files will be stored in: %s" % leoTempDir)
        td = os.path.join(os.path.abspath(tempfile.gettempdir()), leoTempDir)
        if not os.path.exists(td):
            os.mkdir(td)
        name = g.sanitize_filename(p.h) + '_' + str(id(p.v)) + ext
        path = os.path.join(td, name)
        return path
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
