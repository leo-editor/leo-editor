# -*- coding: utf-8 -*-
#@+leo-ver=4-thin
#@+node:ekr.20080708094444.1:@thin leoShadow.py
#@@first

#@<< docstring >>
#@+node:ekr.20080708094444.78:<< docstring >>
'''
leoShadow.py


This code allows users to use Leo with files which contain no sentinels
and still have information flow in both directions between outlines and
derived files.

Private files contain sentinels: they live in the Leo-shadow subdirectory.
Public files contain no sentinels: they live in the parent (main) directory.

When Leo first reads an @shadow we create a file without sentinels in the regular directory.

The slightly hard thing to do is to pick up changes from the file without
sentinels, and put them into the file with sentinels.



Settings:
- @string shadow_subdir (default: LeoFolder): name of the shadow directory.

- @string shadow_prefix (default: x): prefix of shadow files.
  This prefix allows the shadow file and the original file to have different names.
  This is useful for name-based tools like py.test.
'''
#@-node:ekr.20080708094444.78:<< docstring >>
#@nl
#@<< imports >>
#@+node:ekr.20080708094444.52:<< imports >>
import leo.core.leoGlobals as g

import difflib
import os
import sys
import unittest
#@-node:ekr.20080708094444.52:<< imports >>
#@nl

#@@language python
#@@tabwidth -4
#@@pagewidth 80

#@+others
#@+node:ekr.20080708094444.80:class shadowController
class shadowController:

    '''A class to manage @shadow files'''

    #@    @+others
    #@+node:ekr.20080708094444.79: x.ctor
    def __init__ (self,c,trace=False,trace_writers=False):

        self.c = c

        # Configuration...
        self.shadow_subdir = c.config.getString('shadow_subdir') or 'LeoFolder'
        self.shadow_prefix = c.config.getString('shadow_prefix') or ''

        # Debugging...
        self.trace = trace
        self.trace_writers = trace_writers  # True: enable traces in all sourcewriters.

        # Error handling...
        self.errors = 0
        self.last_error  = '' # The last error message, regardless of whether it was actually shown.

        # Support for goto-line-number.
        self.line_mapping = []
    #@-node:ekr.20080708094444.79: x.ctor
    #@+node:ekr.20080711063656.1:x.File utils
    #@+node:ekr.20080711063656.7:x.baseDirName
    def baseDirName (self):

        x = self ; filename = x.c.fileName()

        if filename:
            return g.os_path_dirname(g.os_path_abspath(filename))
        else:
            self.error('Can not compute shadow path: .leo file has not been saved')
            return None
    #@nonl
    #@-node:ekr.20080711063656.7:x.baseDirName
    #@+node:ekr.20080711063656.4:x.dirName and pathName
    def dirName (self,filename):

        '''Return the directory for filename.'''

        x = self

        return g.os_path_dirname(x.pathName(filename))

    def pathName (self,filename):

        '''Return the full path name of filename.'''

        x = self ; theDir = x.baseDirName()

        return theDir and g.os_path_abspath(g.os_path_join(theDir,filename))
    #@nonl
    #@-node:ekr.20080711063656.4:x.dirName and pathName
    #@+node:ekr.20080712080505.3:x.isSignificantPublicFile
    def isSignificantPublicFile (self,fn):

        '''This tells the atFile.read logic whether to import a public file or use an existing public file.'''

        return g.os_path_exists(fn) and g.os_path_isfile(fn) and g.os_path_getsize(fn) > 10
    #@-node:ekr.20080712080505.3:x.isSignificantPublicFile
    #@+node:ekr.20080710082231.19:x.makeShadowDirectory
    def makeShadowDirectory (self,fn):

        '''Make a shadow directory for the **public** fn.'''

        x = self ; path = x.shadowDirName(fn)

        if not g.os_path_exists(path):

            try:
                # g.trace('making',path)
                os.mkdir(path)
            except Exception:
                x.error('unexpected exception creating %s' % path)
                g.es_exception()
                return False

        return g.os_path_exists(path) and g.os_path_isdir(path)
    #@-node:ekr.20080710082231.19:x.makeShadowDirectory
    #@+node:ekr.20080711063656.2:x.rename
    def rename (self,src,dst,mode=None,silent=False):

        x = self ; c = x.c

        ok = g.utils_rename (c,src,dst,mode=mode,verbose=not silent)
        if not ok:
            x.error('can not rename %s to %s' % (src,dst),silent=silent)

        return ok
    #@-node:ekr.20080711063656.2:x.rename
    #@+node:ekr.20080713091247.1:x.replaceFileWithString
    def replaceFileWithString (self,fn,s):

        '''Replace the file with s if s is different from theFile's contents.

        Return True if theFile was changed.
        '''

        x = self ; testing = g.app.unitTesting

        exists = g.os_path_exists(fn)

        if exists: # Read the file.  Return if it is the same.
            try:
                f = file(fn,'rb')
                s2 = f.read()
                f.close()
            except IOError:
                x.error('unexpected exception creating %s' % fn)
                g.es_exception()
                return False
            if s == s2:
                if not testing: g.es('unchanged:',fn)
                return False

        # Replace the file.
        try:
            f = file(fn,'wb')
            f.write(s)
            f.close()
            if not testing:
                if exists:  g.es('wrote:    ',fn)
                else:       g.es('created:  ',fn)
            return True
        except IOError:
            x.error('unexpected exception writing file: %s' % (fn))
            g.es_exception()
            return False
    #@-node:ekr.20080713091247.1:x.replaceFileWithString
    #@+node:ekr.20080711063656.6:x.shadowDirName and shadowPathName
    def shadowDirName (self,filename):

        '''Return the directory for the shadow file corresponding to filename.'''

        x = self

        return g.os_path_dirname(x.shadowPathName(filename))

    def shadowPathName (self,filename):

        '''Return the full path name of filename, resolved using c.fileName()'''

        x = self ; baseDir = x.baseDirName()
        fileDir = g.os_path_dirname(filename)
        # g.trace(baseDir)
        # g.trace(x.shadow_subdir)
        # g.trace(fileDir)

        return baseDir and g.os_path_abspath(g.os_path_normpath(g.os_path_join(
                baseDir,
                fileDir, # Bug fix: honor any directories specified in filename.
                x.shadow_subdir,
                x.shadow_prefix + g.shortFileName(filename))))
    #@nonl
    #@-node:ekr.20080711063656.6:x.shadowDirName and shadowPathName
    #@+node:ekr.20080711063656.3:x.unlink
    def unlink (self, filename,silent=False):

        '''Unlink filename from the file system.
        Give an error on failure.'''

        x = self

        ok = g.utils_remove(filename, verbose=not silent)
        if not ok:
            x.error('can not delete %s' % (filename),silent=silent)

        return ok
    #@-node:ekr.20080711063656.3:x.unlink
    #@-node:ekr.20080711063656.1:x.File utils
    #@+node:ekr.20080708192807.1:x.Propagation
    #@+node:ekr.20080708094444.35:x.check_the_final_output
    def check_the_final_output(self, new_private_lines, new_public_lines, sentinel_lines, marker):
        """
        Check that we produced a valid output.

        Input:
            new_targetlines:   the lines with sentinels which produce changed_lines_without_sentinels.
            sentinels:         new_targetlines should include all the lines from sentinels.

        checks:
            1. new_targetlines without sentinels must equal changed_lines_without_sentinels.
            2. the sentinel lines of new_targetlines must match 'sentinels'
        """
        new_public_lines2, new_sentinel_lines2 = self.separate_sentinels (new_private_lines, marker)

        ok = True
        if new_public_lines2 != new_public_lines:
            last_line2 = new_public_lines2[-1]
            last_line  = new_public_lines[-1]
            if (
                new_public_lines2[:-1] == new_public_lines[:-1] and
                last_line2 == last_line + '\n'
            ):
                ok = True
            else:
                ok = False
                self.show_error(
                    lines1 = new_public_lines2,
                    lines2 = new_public_lines,
                    message = "Error in updating public file!",
                    lines1_message = "new public lines (derived from new private lines)",
                    lines2_message = "new public lines")
            # g.trace(g.callers())

        if new_sentinel_lines2 != sentinel_lines:
            ok = False
            self.show_error(
                lines1 = sentinel_lines,
                lines2 = new_sentinel_lines2,
                message = "Sentinals not preserved!",
                lines1_message = "old sentinels",
                lines2_message = "new sentinels")

        # if ok: g.trace("success!")
    #@-node:ekr.20080708094444.35:x.check_the_final_output
    #@+node:ekr.20080708094444.37:x.copy_sentinels
    def copy_sentinels(self,reader,writer,marker,limit):

        '''Copy sentinels from reader to writer while reader.index() < limit.'''

        x = self
        start = reader.index()
        while reader.index() < limit:
            line = reader.get()
            if x.is_sentinel(line, marker):
                if x.is_verbatim(line,marker):
                    # # if reader.index() < limit:
                        # # # We are *copying* the @verbatim sentinel.
                        # # line = reader.get()
                        # # writer.put(line,tag='copy sent %s:%s' % (start,limit))
                    # We are *deleting* non-sentinel lines, so we must delete @verbatim sentinels!
                    # We must **extend** the limit to get the next line.
                    if reader.index() < limit + 1:
                        # Skip the next line, whatever it is.
                        # Important: this **deletes** the @verbatim sentinel,
                        # so this is a exception to the rule that sentinels are preserved.
                        line = reader.get()
                    else:
                        x.verbatim_error()
                else:
                    # g.trace('put line',repr(line))
                    writer.put(line,tag='copy sent %s:%s' % (start,limit))
    #@-node:ekr.20080708094444.37:x.copy_sentinels
    #@+node:ekr.20080708094444.38:x.propagate_changed_lines
    def propagate_changed_lines(self,new_public_lines,old_private_lines,marker,p=None):

        '''Propagate changes from 'new_public_lines' to 'old_private_lines.

        We compare the old and new public lines, create diffs and
        propagate the diffs to the new private lines, copying sentinels as well.

        We have two invariants:
        1. We *never* delete any sentinels.
        2. Insertions that happen at the boundary between nodes will be put at
           the end of a node.  However, insertions must always be done within sentinels.
        '''

        x = self ; trace = False ; verbose = True
        # mapping tells which line of old_private_lines each line of old_public_lines comes from.
        old_public_lines, mapping = self.strip_sentinels_with_map(old_private_lines,marker)

        #@    << init vars >>
        #@+node:ekr.20080708094444.40:<< init vars >>
        new_private_lines_wtr = sourcewriter(self)
        # collects the contents of the new file.

        new_public_lines_rdr = sourcereader(self,new_public_lines)
            # Contains the changed source code.

        old_public_lines_rdr = sourcereader(self,old_public_lines)
            # this is compared to new_public_lines_rdr to find out the changes.

        old_private_lines_rdr = sourcereader(self,old_private_lines) # lines_with_sentinels)
            # This is the file which is currently produced by Leo, with sentinels.

        # Check that all ranges returned by get_opcodes() are contiguous
        old_old_j, old_i2_modified_lines = -1,-1

        tag = old_i = old_j = new_i = new_j = None
        #@nonl
        #@-node:ekr.20080708094444.40:<< init vars >>
        #@nl
        #@    << define print_tags >>
        #@+node:ekr.20080708094444.39:<< define print_tags >>
        def print_tags(tag, old_i, old_j, new_i, new_j, message):

            sep1 = '=' * 10 ; sep2 = '-' * 20

            g.pr('\n',sep1,message,sep1,p and p.headString())

            g.pr('\n%s: old[%s:%s] new[%s:%s]' % (tag,old_i,old_j,new_i,new_j))

            g.pr('\n',sep2)

            table = (
                (old_private_lines_rdr,'old private lines'),
                (old_public_lines_rdr,'old public lines'),
                (new_public_lines_rdr,'new public lines'),
                (new_private_lines_wtr,'new private lines'),
            )

            for f,tag in table:
                f.dump(tag)
                g.pr(sep2)


        #@-node:ekr.20080708094444.39:<< define print_tags >>
        #@nl

        sm = difflib.SequenceMatcher(None,old_public_lines,new_public_lines)
        prev_old_j = 0 ; prev_new_j = 0

        for tag,old_i,old_j,new_i,new_j in sm.get_opcodes():

            #@        << About this loop >>
            #@+node:ekr.20080708192807.2:<< about this loop >>
            #@+at
            # 
            # This loop writes all output lines using a single writer: 
            # new_private_lines_wtr.
            # 
            # The output lines come from two, and *only* two readers:
            # 
            # 1. old_private_lines_rdr delivers the complete original sources. 
            # All
            #    sentinels and unchanged regular lines come from this reader.
            # 
            # 2. new_public_lines_rdr delivers the new, changed sources. All 
            # inserted or
            #    replacement text comes from this reader.
            # 
            # Each time through the loop, the following are true:
            # 
            # - old_i is the index into old_public_lines of the start of the 
            # present SequenceMatcher opcode.
            # 
            # - mapping[old_i] is the index into old_private_lines of the 
            # start of the same opcode.
            # 
            # At the start of the loop, the call to copy_sentinels effectively 
            # skips (deletes)
            # all previously unwritten non-sentinel lines in 
            # old_private_lines_rdr whose index
            # less than mapping[old_i].
            # 
            # As a result, the opcode handlers do not need to delete elements 
            # from the
            # old_private_lines_rdr explicitly. This explains why opcode 
            # handlers for the
            # 'insert' and 'delete' opcodes are identical.
            #@-at
            #@-node:ekr.20080708192807.2:<< about this loop >>
            #@nl

            # Verify that SequenceMatcher never leaves gaps.
            if old_i != prev_old_j: # assert old_i == prev_old_j
                x.error('can not happen: gap in old:',old_i,prev_old_j)
            if new_i != prev_new_j: # assert new_i == prev_new_j
                x.error('can not happen: gap in new:',new_i,prev_new_j)

            #@        << Handle the opcode >>
            #@+node:ekr.20080708192807.5:<< Handle the opcode >>
            # Do not copy sentinels if a) we are inserting and b) limit is at the end of the old_private_lines.
            # In this special case, we must do the insert before the sentinels.
            limit=mapping[old_i]

            if trace: g.trace(tag,'old_i',old_i,'limit',limit)

            if tag == 'insert' and limit >= old_private_lines_rdr.size():
                pass
            else:
                # Ignore (delete) all unwritten lines of old_private_lines_rdr up to limit.
                # Because of this, nothing has to be explicitly deleted below.
                self.copy_sentinels(old_private_lines_rdr,new_private_lines_wtr,marker,limit=limit)

            if tag == 'equal':
                # Copy all lines (including sentinels) from the old private file to the new private file.
                start = old_private_lines_rdr.index()
                while old_private_lines_rdr.index() <= mapping[old_j-1]:
                    line = old_private_lines_rdr.get()
                    new_private_lines_wtr.put(line,tag='%s %s:%s' % (tag,start,mapping[old_j-1]))

                # Ignore all new lines up to new_j: the same lines (with sentinels) have just been written.
                new_public_lines_rdr.sync(new_j)

            elif tag in ('insert','replace'):
                # All unwritten lines from old_private_lines_rdr up to mapping[old_i] have already been ignored.
                # Copy lines from new_public_lines_rdr up to new_j.
                start = new_public_lines_rdr.index()
                while new_public_lines_rdr.index() < new_j:
                    line = new_public_lines_rdr.get()
                    if x.is_sentinel(line,marker):
                        new_private_lines_wtr.put('%sverbatim\n' % (marker),tag='%s %s:%s' % ('new sent',start,new_j))
                    new_private_lines_wtr.put(line,tag='%s %s:%s' % (tag,start,new_j))

            elif tag=='delete':
                # All unwritten lines from old_private_lines_rdr up to mapping[old_i] have already been ignored.
                # Leave new_public_lines_rdr unchanged.
                pass

            else: g.trace('can not happen: unknown difflib.SequenceMather tag: %s' % repr(tag))

            if trace and verbose:
                print_tags(tag, old_i, old_j, new_i, new_j, "After tag")
            #@nonl
            #@-node:ekr.20080708192807.5:<< Handle the opcode >>
            #@nl

            # Remember the ends of the previous tag ranges.
            prev_old_j = old_j
            prev_new_j = new_j

        # Copy all unwritten sentinels.
        self.copy_sentinels(
            old_private_lines_rdr,new_private_lines_wtr,
            marker, limit = old_private_lines_rdr.size())

        # Get the result.
        result = new_private_lines_wtr.getlines()
        if 1:
            #@        << do final correctness check>>
            #@+node:ekr.20080708094444.45:<< do final correctness check >>
            t_sourcelines, t_sentinel_lines = self.separate_sentinels(
                new_private_lines_wtr.lines, marker)

            self.check_the_final_output(
                new_private_lines   = result,
                new_public_lines    = new_public_lines,
                sentinel_lines      = t_sentinel_lines,
                marker              = marker)
            #@-node:ekr.20080708094444.45:<< do final correctness check >>
            #@nl
        return result
    #@-node:ekr.20080708094444.38:x.propagate_changed_lines
    #@+node:ekr.20080708094444.36:x.propagate_changes
    def propagate_changes(self, old_public_file, old_private_file):

        '''Propagate the changes from the public file (without_sentinels)
        to the private file (with_sentinels)'''

        x = self

        # g.trace('old_public_file',old_public_file)

        old_public_lines  = file(old_public_file).readlines()
        old_private_lines = file(old_private_file).readlines()
        marker = x.marker_from_extension(old_public_file)
        if not marker:
            return False

        new_private_lines = x.propagate_changed_lines(
            old_public_lines,old_private_lines,marker)

        # Important bug fix: Never create the private file here!
        fn = old_private_file
        copy = os.path.exists(fn) and new_private_lines != old_private_lines

        if copy and x.errors == 0:
            s = ''.join(new_private_lines)
            ok = x.replaceFileWithString(fn,s)
            # g.trace('ok',ok,'writing private file',fn)

        return copy
    #@-node:ekr.20080708094444.36:x.propagate_changes
    #@+node:ekr.20080708094444.34:x.strip_sentinels_with_map
    def strip_sentinels_with_map (self, lines, marker):

        '''Strip sentinels from lines, a list of lines with sentinels.

        Return (results,mapping)

        'lines':     A list of lines containing sentinels.
        'results':   The list of non-sentinel lines.
        'mapping':   A list mapping each line in results to the original list.
                    results[i] comes from line mapping[i] of the original lines.'''

        x = self
        mapping = [] ; results = [] ; i = 0 ; n = len(lines)
        while i < n:
            line = lines[i]
            if x.is_sentinel(line,marker):
                if x.is_verbatim(line,marker):
                    i += 1
                    if i < n:
                        # Not a sentinel, whatever it looks like.
                        line = lines[i]
                        # g.trace('not a sentinel',repr(line))
                        results.append(line)
                        mapping.append(i)
                    else:
                        x.verbatim_error()
            else:
                results.append(line)
                mapping.append(i)
            i += 1

        mapping.append(len(lines)) # To terminate loops.
        return results, mapping 
    #@-node:ekr.20080708094444.34:x.strip_sentinels_with_map
    #@+node:bwmulder.20041231170726:x.updatePublicAndPrivateFiles
    def updatePublicAndPrivateFiles (self,fn,shadow_fn):

        '''handle crucial @shadow read logic.

        This will be called only if the public and private files both exist.'''

        x = self ; trace = False

        if trace and not g.app.unitTesting:
            g.trace('significant',x.isSignificantPublicFile(fn),fn)

        if x.isSignificantPublicFile(fn):
            # Update the private shadow file from the public file.
            written = x.propagate_changes(fn,shadow_fn)
            if written: x.message("updated private %s from public %s" % (shadow_fn, fn))
        else:
            # Don't write *anything*.
            if 0: # This causes considerable problems.
                # Create the public file from the private shadow file.
                x.copy_file_removing_sentinels(shadow_fn,fn)
                x.message("created public %s from private %s " % (fn, shadow_fn))
    #@+node:ekr.20080708094444.27:x.copy_file_removing_sentinels
    def copy_file_removing_sentinels (self,source_fn,target_fn):

        '''Copies sourcefilename to targetfilename, removing sentinel lines.'''

        x = self

        marker = x.marker_from_extension(source_fn)
        if not marker:
            return

        old_lines = file(source_fn).readlines()
        new_lines, junk = x.separate_sentinels(old_lines,marker)

        copy = not os.path.exists(target_fn) or old_lines != new_lines
        if copy:
            s = ''.join(new_lines)
            x.replaceFileWithString(target_fn,s)
    #@-node:ekr.20080708094444.27:x.copy_file_removing_sentinels
    #@-node:bwmulder.20041231170726:x.updatePublicAndPrivateFiles
    #@-node:ekr.20080708192807.1:x.Propagation
    #@+node:ekr.20080708094444.89:x.Utils...
    #@+node:ekr.20080708094444.85:x.error & message & verbatim_error
    def error (self,s,silent=False):

        x = self

        if not silent:
            g.es_print(s,color='red')

        # For unit testing.
        x.last_error = s
        x.errors += 1

    def message (self,s):

        g.es_print(s,color='orange')

    def verbatim_error(self):

        x = self

        x.error('file syntax error: nothing follows verbatim sentinel')
        g.trace(g.callers())
    #@-node:ekr.20080708094444.85:x.error & message & verbatim_error
    #@+node:ekr.20080708094444.11:x.is_sentinel & is_verbatim
    def is_sentinel (self, line, marker):

        '''Return true if the line is a sentinel.'''

        return line.lstrip().startswith(marker)

    def is_verbatim (self,line,marker):

        return line.lstrip().startswith(marker+'verbatim')
    #@-node:ekr.20080708094444.11:x.is_sentinel & is_verbatim
    #@+node:ekr.20080708094444.9:x.marker_from_extension
    def marker_from_extension (self,filename,suppressErrors=False):

        '''Return the sentinel delimiter comment to be used for filename.'''

        x = self
        if not filename: return None
        root,ext = g.os_path_splitext(filename)
        delims = g.comment_delims_from_extension(filename)
        for i in (0,1):
            if delims[i]:
                # g.trace('ext',ext,'delims',repr(delims[i]+'@'))
                return delims[i]+'@'

        if ext=='.tmp':
            root, ext = os.path.splitext(root)
        if ext in('.cfg','.ksh','.txt'):
            marker = '#@'
        elif ext in ('.bat',):
            marker = "REM@"
        else:
            # Yes, we *can* use a special marker for unknown languages,
            # provided we make it impossible to type by mistake,
            # and provided no real language will be the prefix of the comment delim.
            marker = g.app.language_delims_dict.get('unknown_language') + '@'
            # g.trace('unknown language marker',marker)

        return marker
    #@-node:ekr.20080708094444.9:x.marker_from_extension
    #@+node:ekr.20080708094444.30:x.push_filter_mapping
    def push_filter_mapping (self,lines, marker):
        """
        Given the lines of a file, filter out all
        Leo sentinels, and return a mapping:

          stripped file -> original file

        Filtering should be the same as
        separate_sentinels
        """

        x = self ; mapping = [None]

        i = 0 ; n = len(lines)
        while i < n:
            line = lines[i]
            if x.is_sentinel(line,marker):
                if x.is_verbatim(line,marker):
                    i += 1
                    if i < n:
                        mapping.append(i+1)
                    else:
                        x.verbatim_error()
            else:
                mapping.append(i+1)
            i += 1

        # for i, line in enumerate(filelines):
            # if not self.is_sentinel(line,marker):
                # mapping.append(i+1)

        return mapping 
    #@-node:ekr.20080708094444.30:x.push_filter_mapping
    #@+node:ekr.20080708094444.29:x.separate_sentinels
    def separate_sentinels (self, lines, marker):

        '''
        Separates regular lines from sentinel lines.

        Returns (regular_lines, sentinel_lines)
        '''

        x = self ; regular_lines = [] ; sentinel_lines = []

        i = 0 ; n = len(lines)
        while i < len(lines):
            line = lines[i]
            if x.is_sentinel(line,marker):
                sentinel_lines.append(line)
                if x.is_verbatim(line,marker):
                    i += 1
                    if i < len(lines):
                        line = lines[i]
                        regular_lines.append(line)
                    else:
                        x.verbatim_error()
            else:
                regular_lines.append(line)
            i += 1

        return regular_lines, sentinel_lines 
    #@-node:ekr.20080708094444.29:x.separate_sentinels
    #@+node:ekr.20080708094444.33:x.show_error
    def show_error (self, lines1, lines2, message, lines1_message, lines2_message):

        def p(s):
            sys.stdout.write(s)
            f1.write(s)
        g.pr("=================================")
        g.pr(message)
        g.pr("=================================")
        g.pr(lines1_message )
        g.pr("---------------------------------")
        f1 = file("mod_shadow.tmp1", "w")
        for line in lines1:
            p(line)
        f1.close()
        g.pr("\n==================================")
        g.pr(lines2_message )
        g.pr("---------------------------------")
        f1 = file("mod_shadow.tmp2", "w")
        for line in lines2:
            p(line)
        f1.close()
        g.pr('')
        g.es("@shadow did not pick up the external changes correctly; please check shadow.tmp1 and shadow.tmp2 for differences")
        # assert 0, "Malfunction of @shadow"
    #@-node:ekr.20080708094444.33:x.show_error
    #@-node:ekr.20080708094444.89:x.Utils...
    #@+node:ekr.20080709062932.2:atShadowTestCase
    class atShadowTestCase (unittest.TestCase):

        '''Support @shadow-test nodes.

        These nodes should have two descendant nodes: 'before' and 'after'.

        '''

        #@    @+others
        #@+node:ekr.20080709062932.6:__init__
        def __init__ (self,c,p,shadowController,lax,trace=False):

             # Init the base class.
            unittest.TestCase.__init__(self)

            self.c = c
            self.lax = lax
            self.p = p.copy()
            self.shadowController=shadowController

            # Hard value for now.
            self.marker = '#@'

            # For teardown...
            self.ok = True

            # Debugging
            self.trace = trace
        #@-node:ekr.20080709062932.6:__init__
        #@+node:ekr.20080709062932.7: fail
        def fail (self,msg=None):

            """Mark a unit test as having failed."""

            import leo.core.leoGlobals as g

            g.app.unitTestDict["fail"] = g.callers()
        #@-node:ekr.20080709062932.7: fail
        #@+node:ekr.20080709062932.8:setUp & helpers
        def setUp (self):

            c = self.c ; p = self.p ; x = self.shadowController

            old = self.findNode (c,p,'old')
            new = self.findNode (c,p,'new')

            self.old_private_lines = self.makePrivateLines(old)
            self.new_private_lines = self.makePrivateLines(new)

            self.old_public_lines = self.makePublicLines(self.old_private_lines)
            self.new_public_lines = self.makePublicLines(self.new_private_lines)

            # We must change node:new to node:old
            self.expected_private_lines = self.mungePrivateLines(self.new_private_lines,'node:new','node:old')

        #@+node:ekr.20080709062932.19:findNode
        def findNode(self,c,p,headline):
            p = g.findNodeInTree(c,p,headline)
            if not p:
                g.es_print('can not find',headline)
                assert False
            return p
        #@nonl
        #@-node:ekr.20080709062932.19:findNode
        #@+node:ekr.20080709062932.20:createSentinelNode
        def createSentinelNode (self,root,p):

            '''Write p's tree to a string, as if to a file.'''

            h = p.headString()
            p2 = root.insertAsLastChild()
            p2.setHeadString(h + '-sentinels')
            return p2

        #@-node:ekr.20080709062932.20:createSentinelNode
        #@+node:ekr.20080709062932.21:makePrivateLines
        def makePrivateLines (self,p):

            c = self.c ; at = c.atFileCommands

            at.write (p,
                nosentinels = False,
                thinFile = False,  # Debatable.
                scriptWrite = True,
                toString = True,
                write_strips_blank_lines = None,)

            s = at.stringOutput

            # g.trace(p.headString(),'\n',s)

            return g.splitLines(s)
        #@-node:ekr.20080709062932.21:makePrivateLines
        #@+node:ekr.20080709062932.22:makePublicLines
        def makePublicLines (self,lines):

            x = self.shadowController

            lines,mapping = x.strip_sentinels_with_map(lines,self.marker)

            # g.trace(lines)

            return lines
        #@-node:ekr.20080709062932.22:makePublicLines
        #@+node:ekr.20080709062932.23:mungePrivateLines
        def mungePrivateLines (self,lines,find,replace):

            x = self.shadowController ; marker = self.marker

            i = 0 ; n = len(lines) ; results = []
            while i < n:
            # for line in lines:
                line = lines[i]
                if x.is_sentinel(line,self.marker):
                    new_line = line.replace(find,replace)
                    results.append(new_line)
                    if x.is_verbatim(line,marker):
                        i += 1
                        if i < len(lines):
                            line = lines[i]
                            results.append(line)
                        else:
                            x.verbatim_error()

                    # if line != new_line: g.trace(new_line)
                else:
                    results.append(line)
                i += 1

            return results
        #@-node:ekr.20080709062932.23:mungePrivateLines
        #@-node:ekr.20080709062932.8:setUp & helpers
        #@+node:ekr.20080709062932.9:tearDown
        def tearDown (self):

            pass

            # No change is made to the outline.
            # self.c.redraw()
        #@-node:ekr.20080709062932.9:tearDown
        #@+node:ekr.20080709062932.10:runTest (atShadowTestCase)
        def runTest (self,define_g = True):

            x = self.shadowController

            results = x.propagate_changed_lines(
                self.new_public_lines,
                self.old_private_lines,
                marker="#@",
                p = self.p.copy())

            if not self.lax and results != self.expected_private_lines:

                g.pr('%s atShadowTestCase.runTest:failure' % ('*' * 40))
                for aList,tag in ((results,'results'),(self.expected_private_lines,'expected_private_lines')):
                    g.pr('%s...' % tag)
                    for i, line in enumerate(aList):
                        g.pr('%3s %s' % (i,repr(line)))
                    g.pr('-' * 40)

                assert results == self.expected_private_lines

            assert self.ok
            return self.ok
        #@nonl
        #@-node:ekr.20080709062932.10:runTest (atShadowTestCase)
        #@+node:ekr.20080709062932.11:shortDescription
        def shortDescription (self):

            return self.p and self.p.headString() or '@test-shadow: no self.p'
        #@-node:ekr.20080709062932.11:shortDescription
        #@-others

    #@-node:ekr.20080709062932.2:atShadowTestCase
    #@-others
#@-node:ekr.20080708094444.80:class shadowController
#@+node:ekr.20080708094444.12:class sourcereader
class sourcereader:
    """
    A simple class to read lines sequentially.

    The class keeps an internal index, so that each
    call to get returns the next line.

    Index returns the internal index, and sync
    advances the index to the the desired line.

    The index is the *next* line to be returned.

    The line numbering starts from 0.

    The code might be expanded inline once the plugin
    is considered stable
    """
    #@    @+others
    #@+node:ekr.20080708094444.13:__init__
    def __init__ (self,shadowController,lines):
        self.lines = lines 
        self.length = len(self.lines)
        self.i = 0
        self.shadowController=shadowController
    #@-node:ekr.20080708094444.13:__init__
    #@+node:ekr.20080708094444.14:index
    def index (self):
        return self.i
    #@-node:ekr.20080708094444.14:index
    #@+node:ekr.20080708094444.15:get
    def get (self):
        result = self.lines[self.i]
        self.i+=1
        return result 
    #@-node:ekr.20080708094444.15:get
    #@+node:ekr.20080708094444.16:sync
    def sync (self,i):
        self.i = i 
    #@-node:ekr.20080708094444.16:sync
    #@+node:ekr.20080708094444.17:size
    def size (self):
        return self.length 
    #@-node:ekr.20080708094444.17:size
    #@+node:ekr.20080708094444.18:atEnd
    def atEnd (self):
        return self.index>=self.length 
    #@-node:ekr.20080708094444.18:atEnd
    #@+node:ekr.20080708094444.19:clone
    def clone(self):
        sr = sourcereader(self.lines)
        sr.i = self.i
        return sr
    #@nonl
    #@-node:ekr.20080708094444.19:clone
    #@+node:ekr.20080708094444.20:dump
    def dump(self, title):

        g.pr(title)
        # g.pr('self.i',self.i)
        for i, line in enumerate(self.lines):
            marker = g.choose(i==self.i,'**','  ')
            g.pr("%s %3s:%s" % (marker, i, line),)
    #@nonl
    #@-node:ekr.20080708094444.20:dump
    #@-others
#@-node:ekr.20080708094444.12:class sourcereader
#@+node:ekr.20080708094444.21:class sourcewriter
class sourcewriter:
    """
    Convenience class to capture output to a file.

    Similar to class sourcereader.
    """
    #@	@+others
    #@+node:ekr.20080708094444.22:__init__
    def __init__ (self,shadowController):

        self.i = 0
        self.lines =[]
        self.shadowController=shadowController
        self.trace = False or self.shadowController.trace_writers
    #@-node:ekr.20080708094444.22:__init__
    #@+node:ekr.20080708094444.23:put
    def put(self, line, tag=''):

        trace = False or self.trace

        # An important hack.  Make sure *all* lines end with a newline.
        # This will cause a mismatch later in check_the_final_output,
        # and a special case has been inserted to forgive this newline.
        if not line.endswith('\n'):
            if trace: g.trace('adding newline',repr(line))
            line = line + '\n'

        self.lines.append(line)
        self.i+=1

        if trace: g.trace('%16s %s' % (tag,repr(line)))
    #@-node:ekr.20080708094444.23:put
    #@+node:ekr.20080708094444.24:index
    def index (self):

        return self.i 
    #@-node:ekr.20080708094444.24:index
    #@+node:ekr.20080708094444.25:getlines
    def getlines (self):

        return self.lines 
    #@-node:ekr.20080708094444.25:getlines
    #@+node:ekr.20080708094444.26:dump
    def dump(self, title):

        '''Dump lines for debugging.'''

        g.pr(title)
        for i, line in enumerate(self.lines):
            marker = '  '
            g.es("%s %3s:%s" % (marker, i, line),newline=False)
    #@-node:ekr.20080708094444.26:dump
    #@-others
#@-node:ekr.20080708094444.21:class sourcewriter
#@-others
#@-node:ekr.20080708094444.1:@thin leoShadow.py
#@-leo
