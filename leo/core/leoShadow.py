# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20080708094444.1: * @file leoShadow.py
#@@first

#@+<< docstring >>
#@+node:ekr.20080708094444.78: ** << docstring >>
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
- @string shadow_subdir (default: .leo_shadow): name of the shadow directory.

- @string shadow_prefix (default: x): prefix of shadow files.
  This prefix allows the shadow file and the original file to have different names.
  This is useful for name-based tools like py.test.
'''
#@-<< docstring >>
#@+<< imports >>
#@+node:ekr.20080708094444.52: ** << imports >> (leoShadow)
import leo.core.leoGlobals as g

import difflib
import os
import pprint
import unittest
#@-<< imports >>
#@+<< define new_shadow >>
#@+node:ekr.20150209090744.4: ** << define new_shadow >>
new_shadow = False # True: use new propagate algorithm
if new_shadow:
    print('**** new_shadow ***')
#@-<< define new_shadow >>

#@@language python
#@@tabwidth -4
#@@pagewidth 70

#@+others
#@+node:ekr.20080708094444.80: ** class ShadowController
class ShadowController:

    '''A class to manage @shadow files'''

    #@+others
    #@+node:ekr.20080708094444.79: *3*  x.ctor
    def __init__ (self,c,trace=False,trace_writers=False):
        '''Ctor for ShadowController class.'''
        self.c = c
        # Opcode dispatch dict.
        self.dispatch_dict = {
            'delete': self.op_delete,
            'equal': self.op_equal,
            'insert': self.op_insert,
            'replace': self.op_replace,
        }
        # File encoding.
        self.encoding = c.config.default_derived_file_encoding
        # Configuration...
        self.shadow_subdir = c.config.getString('shadow_subdir') or '.leo_shadow'
        self.shadow_prefix = c.config.getString('shadow_prefix') or ''
        self.shadow_in_home_dir = c.config.getBool('shadow_in_home_dir',default=False)
        self.shadow_subdir = g.os_path_normpath(self.shadow_subdir)
        # Error handling...
        self.errors = 0
        self.last_error  = '' # The last error message, regardless of whether it was actually shown.
        self.trace = False
        # Support for goto-line.
        self.line_mapping = []
    #@+node:ekr.20080711063656.1: *3* x.File utils
    #@+node:ekr.20080711063656.7: *4* x.baseDirName
    def baseDirName (self):

        x = self ; c = x.c ; filename = c.fileName()

        if filename:
            return g.os_path_dirname(c.os_path_finalize(filename))
        else:
            self.error('Can not compute shadow path: .leo file has not been saved')
            return None
    #@+node:ekr.20080711063656.4: *4* x.dirName and pathName
    def dirName (self,filename):

        '''Return the directory for filename.'''

        x = self

        return g.os_path_dirname(x.pathName(filename))

    def pathName (self,filename):

        '''Return the full path name of filename.'''

        x = self ; c = x.c ; theDir = x.baseDirName()

        return theDir and c.os_path_finalize_join(theDir,filename)
    #@+node:ekr.20080712080505.3: *4* x.isSignificantPublicFile
    def isSignificantPublicFile (self,fn):

        '''This tells the AtFile.read logic whether to import a public file
        or use an existing public file.'''

        return (
            g.os_path_exists(fn) and
            g.os_path_isfile(fn) and
            g.os_path_getsize(fn) > 10
        )
    #@+node:ekr.20080710082231.19: *4* x.makeShadowDirectory
    def makeShadowDirectory (self,fn):

        '''Make a shadow directory for the **public** fn.'''

        x = self ; path = x.shadowDirName(fn)

        if not g.os_path_exists(path):

            # Force the creation of the directories.
            g.makeAllNonExistentDirectories(path,c=None,force=True)

        return g.os_path_exists(path) and g.os_path_isdir(path)
    #@+node:ekr.20080713091247.1: *4* x.replaceFileWithString (@shadow)
    def replaceFileWithString (self,fn,s):

        '''Replace the file with s if s is different from theFile's contents.

        Return True if theFile was changed.
        '''

        trace = False and not g.unitTesting ; verbose = False
        x = self
        exists = g.os_path_exists(fn)

        if exists:
            # Read the file.  Return if it is the same.
            s2,e = g.readFileIntoString(fn)
            if s2 is None:
                return False
            if s == s2:
                if not g.unitTesting: g.es('unchanged:',fn)
                return False

        # Issue warning if directory does not exist.
        theDir = g.os_path_dirname(fn)
        if theDir and not g.os_path_exists(theDir):
            if not g.unitTesting:
                x.error('not written: %s directory not found' % fn)
            return False

        # Replace the file.
        try:
            f = open(fn,'wb')
            # 2011/09/09: Use self.encoding.
            f.write(g.toEncodedString(s,encoding=self.encoding))
            if trace:
                g.trace('encoding',self.encoding)
                if verbose: g.trace('fn',fn,
                    '\nlines...\n%s' %(g.listToString(g.splitLines(s))),
                    '\ncallers',g.callers(4))
            f.close()
            if not g.unitTesting:
                # g.trace('created:',fn,g.callers())
                if exists:  g.es('wrote:',fn)
                else:       g.es('created:',fn)
            return True
        except IOError:
            x.error('unexpected exception writing file: %s' % (fn))
            g.es_exception()
            return False
    #@+node:ekr.20080711063656.6: *4* x.shadowDirName and shadowPathName
    def shadowDirName (self,filename):

        '''Return the directory for the shadow file corresponding to filename.'''

        x = self

        return g.os_path_dirname(x.shadowPathName(filename))

    def shadowPathName (self,filename):

        '''Return the full path name of filename, resolved using c.fileName()'''

        x = self ; c = x.c

        baseDir = x.baseDirName()
        fileDir = g.os_path_dirname(filename)

        # 2011/01/26: bogomil: redirect shadow dir
        if self.shadow_in_home_dir:

            # Each .leo file has a separate shadow_cache in base dir
            fname = "_".join([os.path.splitext(os.path.basename(c.mFileName))[0],"shadow_cache"])

            # On Windows incorporate the drive letter to the private file path
            if os.name == "nt":
                fileDir = fileDir.replace(':','%')

            # build the chache path as a subdir of the base dir            
            fileDir = "/".join([baseDir, fname, fileDir])

        return baseDir and c.os_path_finalize_join(
                baseDir,
                fileDir, # Bug fix: honor any directories specified in filename.
                x.shadow_subdir,
                x.shadow_prefix + g.shortFileName(filename))
    #@+node:ekr.20080711063656.3: *4* x.unlink
    def unlink (self, filename,silent=False):

        '''Unlink filename from the file system.
        Give an error on failure.'''

        x = self

        ok = g.utils_remove(filename,verbose=not silent)
        if not ok:
            x.error('can not delete %s' % (filename),silent=silent)

        return ok
    #@+node:ekr.20080708192807.1: *3* x.Propagation
    #@+node:ekr.20080708094444.35: *4* x.check_output
    def check_output(self):
        '''Check that we produced a valid output.'''
        x = self
        marker = x.marker
        new_private_lines = x.results
        new_public_lines = x.b
        junk, sentinel_lines = x.separate_sentinels(x.old_sent_lines, marker)
        new_public_lines2, new_sentinel_lines2 = self.separate_sentinels(x.results, marker)
        lines1 = new_public_lines
        lines2 = new_public_lines2
        sents1 = sentinel_lines
        sents2 = new_sentinel_lines2
        if 1: # Ignore trailing ws:
            s1 = ''.join(lines1).rstrip()
            s2 = ''.join(lines2).rstrip()
            lines1 = g.splitLines(s1)
            lines2 = g.splitLines(s2)
        if 1: # Ignore trailing ws on every line.
            lines1 = [z.rstrip() for z in lines1]
            lines2 = [z.rstrip() for z in lines2]
            sents1 = [z.rstrip() for z in sents1]
            sents2 = [z.rstrip() for z in sents2]
        lines_ok = lines1 == lines2
        sents_ok = sents1 == sents2
        if g.unitTesting:
            # The unit test will report the error.
            return lines_ok and sents_ok
        if not lines_ok:
            if 1:
                g.trace()
                d = difflib.Differ()
                # g.trace('Different!!',d)
                aList = list(d.compare(new_public_lines2,new_public_lines))
                pprint.pprint(aList)
            else:
                x.show_error(
                    lines1 = new_public_lines2,
                    lines2 = new_public_lines,
                    message = "Error in updating public file!",
                    lines1_message = "new public lines (derived from new private lines)",
                    lines2_message = "new public lines")
        if not sents_ok:
            x.show_error(
                lines1 = sentinel_lines,
                lines2 = new_sentinel_lines2,
                message = "Sentinals not preserved!",
                lines1_message = "old sentinels",
                lines2_message = "new sentinels")
        return lines_ok and sents_ok
    #@+node:ekr.20080708094444.37: *4* x.copy_sentinels
    def copy_sentinels(self,limit):
        '''Copy sentinels from x.sent_rdr to x.results while x.sent_rdr.i < limit.'''
        x = self
        # if x.trace: g.trace(limit)
        marker,sent_rdr = x.marker,x.sent_rdr
        while sent_rdr.i < limit:
            line = sent_rdr.get()
            if marker.isSentinel(line):
                if marker.isVerbatimSentinel(line):
                    # We are *deleting* non-sentinel lines, so we must delete @verbatim sentinels!
                    # We must **extend** the limit to get the next line.
                    if sent_rdr.i < limit + 1:
                        # Skip the next line, whatever it is.
                        # Important: this **deletes** the @verbatim sentinel,
                        # so this is a exception to the rule that sentinels are preserved.
                        line = sent_rdr.get()
                    else:
                        x.verbatim_error()
                else:
                    x.put(line)
        # if x.trace: g.trace('done')
    #@+node:ekr.20080708094444.38: *4* x.propagate_changed_lines (main algorithm) & helpers
    def propagate_changed_lines(self,new_public_lines,old_private_lines,marker,p=None):
        #@+<< docstring >>
        #@+node:ekr.20150207044400.9: *5*  << docstring >>
        '''
        Propagate changes from 'new_public_lines' to 'old_private_lines.

        We compare the old and new public lines, create diffs and
        propagate the diffs to the new private lines, copying sentinels as well.

        Invariants:
        - We never delete sentinels, except for @verbatim sentinels for deleted lines.
        - Insertions that happen at the boundary between nodes will be put at
          the end of a node.  However, insertions must always be done within sentinels.
        - old_public_lines [old_i] is the start of the present opcode.
        - old_private_lines[mapping[old_i]] is the corresponding line.
        '''
        #@-<< docstring >>
        x = self
        trace = (False or x.trace) and g.unitTesting
        x.init_ivars(new_public_lines,old_private_lines,marker)
        sm = difflib.SequenceMatcher(None,x.a,x.b)
        if trace: x.dump_args()
        if new_shadow:
            # A special case to ensure leading sentinels are put first.
            x.put_sentinels(0)
        for opcode in sm.get_opcodes():
            tag,old_i,old_j,new_i,new_j = opcode
            if trace and new_shadow:
                g.trace('%3s %s' % (old_i,tag))
            elif trace:
                g.trace(tag,'old_i:%s limit:%s' % (old_i,x.mapping[old_i]))
            tag,ai,aj,bi,bj = opcode
            f = x.dispatch_dict.get(tag,x.op_bad)
            f(opcode)
        if new_shadow:
            x.results.extend(x.trailing_sentinels)
        else:
            x.copy_sentinels(len(x.sent_rdr.lines))
        if trace: x.dump_lines(x.results,'results')
        # Do the final correctness check.
        x.check_output()
        return x.results
    #@+node:ekr.20150207111757.180: *5* x.dump_args
    def dump_args(self):
        '''Dump the argument lines.'''
        x = self
        if new_shadow:
            table = (
                (x.old_sent_lines,'old private lines'),
                (x.a,'old public lines'),
                (x.b,'new public lines'),
            )
        else:
            table = (
                (x.sent_rdr.lines,'old private lines'),
                (x.a_rdr.lines,'old public lines'),
                (x.b_rdr.lines,'new public lines'),
            )
        for lines,title in table:
            x.dump_lines(lines,title)
        g.pr()
    #@+node:ekr.20150207111757.178: *5* x.dump_lines
    def dump_lines(self,lines,title):
        '''Dump the given lines.'''
        print('\n%s...\n' % title)
        for i,line in enumerate(lines):
            g.pr('%4s %s' % (i,repr(line)))
    #@+node:ekr.20080708094444.40: *5* x.init_ivars & helper
    def init_ivars(self,new_public_lines,old_private_lines,marker):
        '''Init all ivars used by propagate_changed_lines & its helpers.'''
        x = self
        x.delim1,x.delim2 = marker.getDelims()
        x.marker = marker
        x.old_sent_lines = old_private_lines
        x.results = []
        x.verbatim_line = '%s@verbatim%s\n' % (x.delim1,x.delim2)
        # Preprocess both public lines.
        if new_shadow:
            old_public_lines = x.init_data()
        else:
            old_public_lines, x.mapping = x.strip_sentinels_with_map(
                old_private_lines,marker,'old_private_lines')
        x.b = x.preprocess(new_public_lines)
        x.a = x.preprocess(old_public_lines)
        if new_shadow:
            pass
        else:
            # Create reader streams.
            x.b_rdr = x.SourceReader(x,x.b) # new lines, no sentinels.
            x.sent_rdr = x.SourceReader(x,x.old_sent_lines) # old lines, with sentinels.
            x.a_rdr = x.SourceReader(x,x.a) # Dumps only.
    #@+node:ekr.20150209044257.6: *6* x.init_data (test)
    def init_data(self):
        '''
        Init x.sentinels and x.trailing_sentinels arrays.
        Return the list of non-sentinel lines in x.old_sent_lines.
        '''
        x = self
        lines = x.old_sent_lines
        sentinels = []
            # The sentinels preceding each non-sentinel line,
            # not including @verbatim sentinels.
        new_lines = []
            # A list of all non-sentinel lines found.  Should match x.a.
        x.sentinels = []
            # A list of lists of sentinels preceding each line.
        i = 0
        while i < len(lines):
            line = lines[i]
            i += 1
            if x.marker.isVerbatimSentinel(line):
                # Do *not* include the @verbatim sentinel.
                if i < len(lines):
                    line = lines[i]
                    i += 1
                    x.sentinels.append(sentinels)
                    sentinels = []
                    new_lines.append(line)
                else:
                    x.verbatim_error()
            elif x.marker.isSentinel(line):
                sentinels.append(line)
            else:
                x.sentinels.append(sentinels)
                sentinels = []
                new_lines.append(line)
        x.trailing_sentinels = sentinels
        return new_lines
    #@+node:ekr.20150207044400.16: *5* x.op_bad
    def op_bad(self,opcode):
        '''Report an unexpected opcode.'''
        x = self
        tag,old_i,old_j,new_i,new_j = opcode
        x.error('unknown difflib opcode: %s' % repr(tag))
    #@+node:ekr.20150207044400.12: *5* x.op_delete
    def op_delete(self,opcode):
        '''Handle the 'delete' opcode.'''
        x = self
        if new_shadow:
            tag,ai,aj,bi,bj = opcode
            for i in range(ai,aj):
                x.put_sentinels(i)
        else:
            tag,old_i,old_j,new_i,new_j = opcode
            # Copy sentinels up to the limit. Leave b_rdr unchanged.
            x.copy_sentinels(x.mapping[old_i])
    #@+node:ekr.20150207044400.13: *5* x.op_equal
    def op_equal(self,opcode):
        '''Handle the 'equal' opcode.'''
        x = self
        if new_shadow:
            tag,ai,aj,bi,bj = opcode
            assert aj - ai == bj - bi and x.a[ai:aj] == x.b[bi:bj]
            for i in range(ai,aj):
                x.put_sentinels(i)
                x.put_plain_line(x.a[i])
                    # works because x.lines[ai:aj] == x.lines[bi:bj]
        else:
            tag,old_i,old_j,new_i,new_j = opcode
            b_rdr,sent_rdr = x.b_rdr,x.sent_rdr
            # Copy sentinels up to mapping[old_i].
            x.copy_sentinels(x.mapping[old_i])
            # Copy all lines (including sentinels) up to mapping[old_j-1]
            while sent_rdr.i <= x.mapping[old_j-1]:
                line = sent_rdr.get()
                x.put(line)
            # Ignore all new lines up to new_j: these lines (with sentinels) have just been written.
            b_rdr.i = new_j # Sync to new_j.
    #@+node:ekr.20150207044400.14: *5* x.op_insert
    def op_insert(self,opcode):
        '''Handle the 'insert' opcode.'''
        x = self
        if new_shadow:
            tag,ai,aj,bi,bj = opcode
            for i in range(bi,bj):
                x.put_plain_line(x.b[i])
            # Prefer to put sentinels after inserted nodes.
            # Requires a call to x.put_sentinels(0) before the main loop.
            x.put_sentinels(ai)
        else:
            b_rdr,sent_rdr = x.b_rdr,x.sent_rdr
            tag,old_i,old_j,new_i,new_j = opcode
        
            # Do not copy sentinels if we are inserting and limit is at the end of the old_private_lines.
            # In this special case, we must do the insert before the sentinels.
            limit = x.mapping[old_i]
            if limit < len(sent_rdr.lines):
                x.copy_sentinels(limit)
        
            # All unwritten lines from sent_rdr up to mapping[old_i] have already been ignored.
            # Copy lines from b_rdr up to new_j.
            while b_rdr.i < new_j:
                line = b_rdr.get()
                x.put_plain_line(line)
    #@+node:ekr.20150207044400.15: *5* x.op_replace
    def op_replace(self,opcode):
        '''Handle the 'replace' opcode.'''
        x = self
        if new_shadow:
            tag,ai,aj,bi,bj = opcode
            if 1:
                # Intersperse sentinels and lines.
                b_lines = list(reversed(x.b[bi:bj]))
                for i in range(ai,aj):
                    x.put_sentinels(i)
                    if b_lines:
                        x.put_plain_line(b_lines.pop())
                # Put any trailing lines.
                while b_lines:
                    x.put_plain_line(b_lines.pop())  
            else:
                # Feasible, but would change unit tests.
                for i in range(ai,aj):
                    x.put_sentinels(i)
                for i in range(bi,bj):
                    x.put_plain_line(x.b[i])
        else:
            tag,old_i,old_j,new_i,new_j = opcode
            # 2010/01/07: Replacements preserve sentinel locations.
            # Careful: the replacement lines can be shorter.
            while x.sent_rdr.i <= x.mapping[old_j-1] and x.b_rdr.i < new_j:
                old_line = x.sent_rdr.get()
                if x.marker.isSentinel(old_line):
                    # Important: this should work for @verbatim sentinels
                    # because the next line will also be replaced.
                    x.put(old_line)
                else:
                    new_line = x.b_rdr.get()
                    x.put(new_line)
            # Careful: The replacement lines can be longer: same as 'insert' code above.
            while x.b_rdr.i < new_j:
                line = x.b_rdr.get()
                x.put_plain_line(line)
    #@+node:ekr.20150208060128.7: *5* x.preprocess
    def preprocess(self,lines):
        '''
        Preprocess public lines, adding newlines as needed.
        This happens before the diff.
        '''
        x, marker = self,self.marker
        result = []
        for line in lines:
            if not line.endswith('\n'):
                line = line + '\n'
            result.append(line)
        return result
    #@+node:ekr.20150207111757.5: *5* x.put
    def put(self,line):
        '''Put the line to x.results.'''
        x = self
        ### Now done in x.preprocess.
        # if not line.endswith('\n'):
            # if x.trace: g.trace('adding newline',repr(line))
            # line = line + '\n'
        x.results.append(line)
        if x.trace:
            g.trace(repr(line))
    #@+node:ekr.20150208223018.4: *5* x.put_plain_line
    def put_plain_line(self,line):
        '''Put a plain line to x.results, inserting verbatim lines if necessary.'''
        x = self
        # if x.trace: g.trace(repr(line),g.callers(1))
        if x.marker.isSentinel(line):
            x.results.append(x.verbatim_line)
            x.trace_line(x.verbatim_line)
        x.results.append(line)
        x.trace_line(line)
    #@+node:ekr.20150209044257.8: *5* x.put_sentinels
    def put_sentinels(self,i):
        '''Put all the sentinels to the results'''
        x = self
        if 0 <= i < len(x.sentinels):
            sentinels = x.sentinels[i] 
            # if x.trace: g.trace('%3s %s' % (i,sentinels))
            x.results.extend(sentinels)
            # Make sure sentinels are ouput at most once.
            x.sentinels[i] = []
    #@+node:ekr.20150208060128.9: *5* x.trace_line
    def trace_line(self,line):
        '''trace the line.'''
        x = self
        if x.trace:
            print('put %s' % repr(line))
    #@+node:ekr.20080708094444.36: *4* x.propagate_changes
    def propagate_changes(self, old_public_file, old_private_file):
        '''
        Propagate the changes from the public file (without_sentinels)
        to the private file (with_sentinels)
        '''
        trace, verbose = False and not g.unitTesting, False
        import leo.core.leoAtFile as leoAtFile
        x = self ; at = self.c.atFileCommands
        at.errors = 0
        if trace: g.trace('*** header scanned: encoding:',at.encoding)
        self.encoding = at.encoding
        s = at.readFileToUnicode(old_private_file)
            # Sets at.encoding and inits at.readLines.
        old_private_lines = g.splitLines(s)
        s = at.readFileToUnicode(old_public_file)
        if at.encoding != self.encoding:
            g.trace('can not happen: encoding mismatch: %s %s' % (
                at.encoding,self.encoding))
            at.encoding = self.encoding
        old_public_lines = g.splitLines(s)
        if 0:
            g.trace('\nprivate lines...%s' % old_private_file)
            for s in old_private_lines:
                g.trace(type(s),g.isUnicode(s),repr(s))
            g.trace('\npublic lines...%s' % old_public_file)
            for s in old_public_lines:
                g.trace(type(s),g.isUnicode(s),repr(s))
        marker = x.markerFromFileLines(old_private_lines,old_private_file)
        if trace and verbose:
            g.trace(
                'marker',marker,
                '\npublic_file',old_public_file,
                '\npublic lines...\n%s' %(
                    g.listToString(old_public_lines,toRepr=True)),
                '\nprivate_file',old_private_file,
                '\nprivate lines...\n%s\n' %(
                    g.listToString(old_private_lines,toRepr=True)))
        new_private_lines = x.propagate_changed_lines(
            old_public_lines,old_private_lines,marker)
        # Important bug fix: Never create the private file here!
        fn = old_private_file
        exists = g.os_path_exists(fn)
        different = new_private_lines != old_private_lines
        copy = exists and different
        if trace: g.trace('\nexists',exists,fn,'different',different,'errors',x.errors,at.errors)
        # 2010/01/07: check at.errors also.
        if copy and x.errors == 0 and at.errors == 0:
            s = ''.join(new_private_lines)
            ok = x.replaceFileWithString(fn,s)
            if trace: g.trace('ok',ok,'writing private file',fn,g.callers())
        return copy
    #@+node:ekr.20080708094444.34: *4* x.strip_sentinels_with_map
    def strip_sentinels_with_map (self, lines, marker, tag=''):
        '''
        Strip sentinels from lines, a list of lines with sentinels.

        Return (results,mapping)

        'lines':     A list of lines containing sentinels.
        'results':   The list of non-sentinel lines.
        'mapping':   A list mapping each line in results to the original list.
                    results[i] comes from line mapping[i] of the original lines.
        '''
        x = self
        mapping, results = [],[]
        i, n = 0,len(lines)
        while i < n:
            line = lines[i]
            if marker.isSentinel(line):
                if marker.isVerbatimSentinel(line):
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
        if x.trace:
            g.trace('mapping for',tag)
            for i in range(len(results)):
                print('%4s %4s %s' % (i,mapping[i],repr(results[i])))
            i = len(results)
            print('%4s %4s %s' % (i,mapping[i],'None'))
        return results, mapping 
    #@+node:bwmulder.20041231170726: *4* x.updatePublicAndPrivateFiles
    def updatePublicAndPrivateFiles (self,root,fn,shadow_fn):

        '''handle crucial @shadow read logic.

        This will be called only if the public and private files both exist.'''

        trace = False and not g.unitTesting
        x = self

        if x.isSignificantPublicFile(fn):
            # Update the private shadow file from the public file.
            written = x.propagate_changes(fn,shadow_fn)
            if written: x.message("updated private %s from public %s" % (shadow_fn, fn))
            elif trace: g.trace("\nno change to %s = %s" % (shadow_fn,fn))
        else:
            if trace: g.trace('not significant',fn)
            # Don't write *anything*.
            # if 0: # This causes considerable problems.
                # # Create the public file from the private shadow file.
                # x.copy_file_removing_sentinels(shadow_fn,fn)
                # x.message("created public %s from private %s " % (fn, shadow_fn))
    #@+node:ekr.20080708094444.89: *3* x.Utils...
    #@+node:ekr.20080708094444.85: *4* x.error & message & verbatim_error
    def error (self,s,silent=False):

        x = self

        if not silent:
            g.error(s)

        # For unit testing.
        x.last_error = s
        x.errors += 1

    def message (self,s):

        g.es_print(s,color='orange')

    def verbatim_error(self):

        x = self

        x.error('file syntax error: nothing follows verbatim sentinel')
        g.trace(g.callers())
    #@+node:ekr.20090529125512.6122: *4* x.markerFromFileLines & helper
    def markerFromFileLines (self,lines,fn):  # fn used only for traces.

        '''Return the sentinel delimiter comment to be used for filename.'''

        trace = False and not g.unitTesting
        x = self ; at = x.c.atFileCommands

        s = x.findLeoLine(lines)
        ok,junk,start,end,junk = at.parseLeoSentinel(s)
        if end:
            delims = '',start,end
        else:
            delims = start,'',''

        if trace: g.trace('delim1 %s delim2 %s delim3 %s fn %s' % (
            delims[0],delims[1],delims[2], fn))

        marker = x.Marker(delims)
        return marker
    #@+node:ekr.20090529125512.6125: *5* x.findLeoLine
    def findLeoLine (self,lines):
        '''Return the @+leo line, or ''.'''
        for line in lines:
            i = line.find('@+leo')
            if i != -1:
                return line
        return ''
    #@+node:ekr.20080708094444.9: *4* x.markerFromFileName
    def markerFromFileName (self,filename):

        '''Return the sentinel delimiter comment to be used for filename.'''

        x = self
        if not filename: return None
        root,ext = g.os_path_splitext(filename)
        if ext=='.tmp':
            root, ext = os.path.splitext(root)

        delims = g.comment_delims_from_extension(filename)
        marker = x.Marker(delims)
        return marker
    #@+node:ekr.20080708094444.30: *4* x.push_filter_mapping
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
            if marker.isSentinel(line):
                if marker.isVerbatimSentinel(line):
                    i += 1
                    if i < n:
                        mapping.append(i+1)
                    else:
                        x.verbatim_error()
            else:
                mapping.append(i+1)
            i += 1

        return mapping 
    #@+node:ekr.20080708094444.29: *4* x.separate_sentinels
    def separate_sentinels (self, lines, marker):

        '''
        Separates regular lines from sentinel lines.

        Returns (regular_lines, sentinel_lines)
        '''

        x = self
        regular_lines = []
        sentinel_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if marker.isSentinel(line):
                sentinel_lines.append(line)
                if marker.isVerbatimSentinel(line):
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
    #@+node:ekr.20080708094444.33: *4* x.show_error & helper
    def show_error (self, lines1, lines2, message, lines1_message, lines2_message):

        x = self
        banner1 = '=' * 30
        banner2 = '-' * 30
        g.es_print('%s\n%s\n%s\n%s\n%s' % (
            banner1,message,banner1,lines1_message,banner2))

        x.show_error_lines(lines1,'shadow_errors.tmp1')

        g.es_print('\n%s\n%s\n%s' % (
            banner1,lines2_message,banner1))

        x.show_error_lines(lines2,'shadow_errors.tmp2')

        g.es_print('\n@shadow did not pick up the external changes correctly')

        # g.es_print('Please check shadow.tmp1 and shadow.tmp2 for differences')
    #@+node:ekr.20080822065427.4: *5* show_error_lines
    def show_error_lines (self,lines,fileName):

        for i,line in enumerate(lines):
            g.es_print('%3s %s' % (i,repr(line)))

        if False: # Only for major debugging.
            try:
                f1 = open(fileName, "w")
                for s in lines:
                    if not g.isPython3: # 2010/08/27
                        s = g.toEncodedString(s,encoding='utf-8',reportErrors=True)
                    f1.write(repr(s))
                f1.close()
            except IOError:
                g.es_exception()
                g.es_print('can not open',fileName)
    #@+node:ekr.20080709062932.2: *3* AtShadowTestCase
    class AtShadowTestCase (unittest.TestCase):

        '''Support @shadow-test nodes.

        These nodes should have two descendant nodes: 'before' and 'after'.

        '''

        #@+others
        #@+node:ekr.20080709062932.6: *4* __init__ (AtShadowTestCase)
        def __init__ (self,c,p,shadowController,lax,trace=False):
            '''Ctor for AtShadowTestCase class.'''
            unittest.TestCase.__init__(self)
                # Init the base class.
            self.c = c
            self.lax = lax
            self.p = p.copy()
            self.shadowController=shadowController
            self.trace = trace
            # Hard value for now.
            delims = '#','',''
            self.marker = shadowController.Marker(delims)
            # For teardown...
            self.ok = True
        #@+node:ekr.20080709062932.7: *4*  fail (AtShadowTestCase)
        def fail (self,msg=None):

            """Mark a unit test as having failed."""

            import leo.core.leoGlobals as g

            g.app.unitTestDict["fail"] = g.callers()
        #@+node:ekr.20080709062932.8: *4* setUp & helpers
        def setUp (self):

            c = self.c
            p = self.p
            # x = self.shadowController
            old = self.findNode (c,p,'old')
            new = self.findNode (c,p,'new')

            self.old_private_lines = self.makePrivateLines(old)
            self.new_private_lines = self.makePrivateLines(new)

            self.old_public_lines = self.makePublicLines(self.old_private_lines)
            self.new_public_lines = self.makePublicLines(self.new_private_lines)

            # We must change node:new to node:old
            self.expected_private_lines = self.mungePrivateLines(self.new_private_lines,'node:new','node:old')

        #@+node:ekr.20080709062932.19: *5* findNode
        def findNode(self,c,p,headline):
            p = g.findNodeInTree(c,p,headline)
            if not p:
                g.es_print('can not find',headline)
                assert False
            return p
        #@+node:ekr.20080709062932.20: *5* createSentinelNode
        def createSentinelNode (self,root,p):

            '''Write p's tree to a string, as if to a file.'''

            h = p.h
            p2 = root.insertAsLastChild()
            p2.setHeadString(h + '-sentinels')
            return p2

        #@+node:ekr.20080709062932.21: *5* makePrivateLines
        def makePrivateLines (self,p):

            c = self.c ; at = c.atFileCommands

            at.write (p,
                nosentinels = False,
                thinFile = False,  # Debatable.
                scriptWrite = True,
                toString = True)

            s = at.stringOutput
            return g.splitLines(s)
        #@+node:ekr.20080709062932.22: *5* makePublicLines
        def makePublicLines (self,lines):

            x = self.shadowController

            lines,mapping = x.strip_sentinels_with_map(lines,self.marker)

            return lines
        #@+node:ekr.20080709062932.23: *5* mungePrivateLines
        def mungePrivateLines (self,lines,find,replace):

            x = self.shadowController ; marker = self.marker

            i = 0 ; n = len(lines) ; results = []
            while i < n:
                line = lines[i]
                if marker.isSentinel(line):
                    new_line = line.replace(find,replace)
                    results.append(new_line)
                    if marker.isVerbatimSentinel(line):
                        i += 1
                        if i < len(lines):
                            line = lines[i]
                            results.append(line)
                        else:
                            x.verbatim_error()
                else:
                    results.append(line)
                i += 1

            return results
        #@+node:ekr.20080709062932.9: *4* tearDown
        def tearDown (self):

            pass

            # No change is made to the outline.
            # self.c.redraw()
        #@+node:ekr.20080709062932.10: *4* runTest (AtShadowTestCase)
        def runTest (self,define_g = True):

            x = self.shadowController
            x.trace = self.trace
            p = self.p.copy()
            results = x.propagate_changed_lines(
                self.new_public_lines,self.old_private_lines,self.marker,p=p)
            if not self.lax and results != self.expected_private_lines:
                # g.pr('%s\nAtShadowTestCase.runTest:failure\n%s' % ('*' * 40,p.h))
                g.pr(p.h)
                for aList,tag in (
                    (results,'results'),
                    (self.expected_private_lines,'expected_private_lines')
                ):
                    g.pr('%s...' % tag)
                    for i, line in enumerate(aList):
                        g.pr('%3s %s' % (i,repr(line)))
                    g.pr('-' * 40)
                assert results == self.expected_private_lines
            assert self.ok
            return self.ok
        #@+node:ekr.20080709062932.11: *4* shortDescription
        def shortDescription (self):

            return self.p and self.p.h or '@test-shadow: no self.p'
        #@-others

    #@+node:ekr.20090529061522.5727: *3* class Marker
    class Marker:
        '''A class representing comment delims in @shadow files.'''
        #@+others
        #@+node:ekr.20090529061522.6257: *4* ctor & repr
        def __init__(self,delims):
            '''Ctor for Marker class.'''
            delim1,delim2,delim3 = delims
            self.delim1 = delim1 # Single-line comment delim.
            self.delim2 = delim2 # Block comment starting delim.
            self.delim3 = delim3 # Block comment ending delim.
            if not delim1 and not delim2:
                self.delim1 = g.app.language_delims_dict.get('unknown_language')

        def __repr__ (self):
            if self.delim1:
                delims = self.delim1
            else:
                delims = '%s %s' % (self.delim2,self.delim2)
            return '<Marker: delims: %s>' % repr(delims)
        #@+node:ekr.20090529061522.6258: *4* getDelims
        def getDelims(self):
            '''Return the pair of delims to be used in sentinel lines.'''
            if self.delim1:
                return self.delim1,''
            else:
                return self.delim2,self.delim3
        #@+node:ekr.20090529061522.6259: *4* isSentinel
        def isSentinel(self,s,suffix=''):
            '''Return True is line s contains a valid sentinel comment.'''
            s = s.strip()
            if self.delim1 and s.startswith(self.delim1):
                return s.startswith(self.delim1+'@'+suffix)
            elif self.delim2:
                return s.startswith(self.delim2+'@'+suffix) and s.endswith(self.delim3)
            else:
                return False
        #@+node:ekr.20090529061522.6260: *4* isVerbatimSentinel
        def isVerbatimSentinel(self,s):
            '''Return True if s is an @verbatim sentinel.'''
            return self.isSentinel(s,suffix='verbatim')
        #@-others

    #@+node:ekr.20080708094444.12: *3* class SourceReader
    class SourceReader:
        '''
        A class to read lines sequentially.
        A thin wrapper around a list of lines and a pointer.
        '''
        #@+others
        #@+node:ekr.20080708094444.13: *4* sr.__init
        def __init__ (self,ShadowController,lines):
            '''Ctor for SourceReader class.'''
            self.i = 0
            self.lines = lines 
            self.x = ShadowController
                # To allow access to the x.trace var.
        #@+node:ekr.20080708094444.15: *4* sr.get
        def get (self):
            '''Return the next line, always incrementing self.i'''
            line = self.lines[self.i] if self.i < len(self.lines) else ''
            self.i += 1
                # Defensive code: make sure loops on self.i terminate.
            if self.x.trace:
                g.trace(repr(line))
            return line 
        #@-others
    Sourcereader = SourceReader
        # Compatibility.
    #@-others
#@-others
#@-leo
