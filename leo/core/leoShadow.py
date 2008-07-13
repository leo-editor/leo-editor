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

import leo.core.leoAtFile as leoAtFile
import leo.core.leoCommands as leoCommands
import leo.core.leoImport as leoImport 

import ConfigParser 
import difflib
import os
import shutil
import sys
import unittest
#@nonl
#@-node:ekr.20080708094444.52:<< imports >>
#@nl

#@@language python
#@@tabwidth -4
#@@pagewidth 80

#@+others
#@+node:ekr.20080708094444.80:class shadowController
class shadowController:

   '''A class to manage @shadow files'''

   #@   @+others
   #@+node:ekr.20080708094444.79: x.ctor
   def __init__ (self,c,trace=False,trace_writers=False):

       self.c = c

       self.print_copy_operations = False   # True: tell when files are copied.
       self.do_backups = False              # True: always make backups of each file.

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
   #@+node:ekr.20080708192807.1:Propagation...
   #@+node:ekr.20080708094444.36:propagate_changes
   def propagate_changes(self, old_public, old_private_file):

       '''Propagate the changes from the public file (without_sentinels)
       to the private file (with_sentinels)'''

       old_public_lines  = file(old_public_file).readlines()
       old_private_lines = file(old_private_file).readlines()
       marker = self.marker_from_extension(old_public_file)

       new_private_lines = self.propagate_changed_lines(
           old_public_lines,old_private_lines,marker)

       written = self.write_if_changed(new_private_lines,
           targetfilename=old_private_file,
           sourcefilename=old_public_file)

       return written
   #@nonl
   #@-node:ekr.20080708094444.36:propagate_changes
   #@+node:ekr.20080708094444.35:check_the_final_output & helper
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
           ok = False
           self.show_error(
               lines1 = new_public_lines2,
               lines2 = new_public_lines,
               message = "Not all changes made!",
               lines1_message = "new public lines (derived from new private lines)",
               lines2_message = "new public lines")

       if new_sentinel_lines2 != sentinel_lines:
           ok = False
           self.show_error(
               lines1 = sentinel_lines,
               lines2 = new_sentinel_lines2,
               message = "Sentinals not preserved!",
               lines1_message = "old sentinels",
               lines2_message = "new sentinels")

       # if ok: g.trace("success!")
   #@+node:ekr.20080708094444.33:show_error
   def show_error (self, lines1, lines2, message, lines1_message, lines2_message):

       def p(s):
           sys.stdout.write(s)
           f1.write(s)
       print "================================="
       print message
       print "================================="
       print lines1_message 
       print "---------------------------------"
       f1 = file("mod_shadow.tmp1", "w")
       for line in lines1:
           p(line)
       f1.close()
       print
       print "=================================="
       print lines2_message 
       print "---------------------------------"
       f1 = file("mod_shadow.tmp2", "w")
       for line in lines2:
           p(line)
       f1.close()
       print
       g.es("@shadow did not pick up the external changes correctly; please check shadow.tmp1 and shadow.tmp2 for differences")
       assert 0, "Malfunction of @shadow"
   #@-node:ekr.20080708094444.33:show_error
   #@-node:ekr.20080708094444.35:check_the_final_output & helper
   #@+node:ekr.20080708094444.37:copy_sentinels
   def copy_sentinels(self,reader,writer,marker,limit):

       '''Copy sentinels from reader to writer while reader.index() < limit.'''

       start = reader.index()
       while reader.index() < limit:
           line = reader.get()
           if self.is_sentinel(line, marker):
               writer.put(line,tag='copy sent %s:%s' % (start,limit))
   #@-node:ekr.20080708094444.37:copy_sentinels
   #@+node:ekr.20080708094444.38:propagate_changed_lines
   def propagate_changed_lines(self,new_public_lines,old_private_lines,marker,p=None):

       '''Propagate changes from 'new_public_lines' to 'old_private_lines.

       We compare the old and new public lines, create diffs and
       propagate the diffs to the new private lines, copying sentinels as well.

       We have two invariants:
       1. We *never* delete any sentinels.
       2. Insertions that happen at the boundary between nodes will be put at
          the end of a node.  However, insertions must always be done within sentinels.
       '''

       trace = False ; verbose = False
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

           print ; print sep1,message,sep1,p and p.headString()

           print ; print '%s: old[%s:%s] new[%s:%s]' % (tag,old_i,old_j,new_i,new_j)

           print ; print sep2

           table = (
               (old_private_lines_rdr,'old private lines'),
               (old_public_lines_rdr,'old public lines'),
               (new_public_lines_rdr,'new public lines'),
               (new_private_lines_wtr,'new private lines'),
           )

           for f,tag in table:
               f.dump(tag)
               print sep2


       #@-node:ekr.20080708094444.39:<< define print_tags >>
       #@nl

       sm = difflib.SequenceMatcher(None,old_public_lines,new_public_lines)
       prev_old_j = 0 ; prev_new_j = 0

       for tag,old_i,old_j,new_i,new_j in sm.get_opcodes():

           # Assert that SequenceMatcher never leaves gaps.
           assert old_i == prev_old_j
           assert new_i == prev_new_j
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
           # - mapping[old_i] is the index into old_private_lines of the start 
           # of the same opcode.
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
           #@        << Handle the opcode >>
           #@+node:ekr.20080708192807.5:<< Handle the opcode >>
           if trace: g.trace(tag,'old_i',old_i,'limit',limit)

           # Do not copy sentinels if a) we are inserting and b) limit is at the end of the old_private_lines.
           # In this special case, we must do the insert before the sentinels.
           limit=mapping[old_i]

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
   #@-node:ekr.20080708094444.38:propagate_changed_lines
   #@+node:ekr.20080708094444.34:strip_sentinels_with_map
   def strip_sentinels_with_map (self, lines, marker):

      '''Strip sentinels from lines, a list of lines with sentinels.

      Return (results,mapping)

      'lines':     A list of lines containing sentinels.
      'results':   The list of non-sentinel lines.
      'mapping':   A list mapping each line in results to the original list.
                   results[i] comes from line mapping[i] of the origina lines.'''

      mapping = [] ; results = []
      for i in xrange(len(lines)):
         line = lines[i]
         if not self.is_sentinel(line,marker):
            results.append(line)
            mapping.append(i)

      mapping.append(len(lines)) # To terminate loops.
      return results, mapping 
   #@-node:ekr.20080708094444.34:strip_sentinels_with_map
   #@-node:ekr.20080708192807.1:Propagation...
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
   def isSignificantPublicFile (self,filename):

       '''This tells the atFile.read logic whether to import a public file or use an existing public file.'''

       return (
           g.os_path_exists(filename) and
           g.os_path_isfile(filename) and
           g.os_path_getsize(fn) > 10)
   #@-node:ekr.20080712080505.3:x.isSignificantPublicFile
   #@+node:ekr.20080710082231.19:x.makeShadowDirectory
   def makeShadowDirectory (self,fn):

       x = self ; path = x.shadowDirName(fn)

       if not g.os_path_exists(path):

           try:
               os.mkdir(path)
           except Exception:
               g.es_exception()
               return False

       return g.os_path_exists(path) and g.os_path_isdir(path)
   #@-node:ekr.20080710082231.19:x.makeShadowDirectory
   #@+node:ekr.20080710082231.17:x.makeShadowFile (possibly not used)
   def makeShadowFile (self,fn):

       x = self ; shadow_fn = x.shadowPathName(fn)

       theDir = x.makeShadowDirectory(fn)
       if not theDir:
           x.error('can not create shadow directory: ' % (x.shadowDirName(fn)))
           return False

       if os.path.exists(shadow_fn):
           g.trace('replacing existing shadow file: %s' % (shadow_fn))

       full_fn = x.pathName(fn)
       x.message("creating shadow file: %s" % (shadow_fn))

       # Copy the original file to the shadow file.
       shutil.copy2(full_fn, shadow_fn)

       # Remove the sentinels from the original file.
       x.unlink(full_fn)
       x.copy_file_removing_sentinels(shadow_fn,full_fn)
   #@-node:ekr.20080710082231.17:x.makeShadowFile (possibly not used)
   #@+node:ekr.20080711063656.2:x.rename
   def rename (self,src,dst,mode=None,silent=False):

       x = self ; c = x.c

       ok = g.utils_rename (c,src,dst,mode=mode,verbose=not silent)
       if not ok:
           x.error('can not rename %s to %s' % (src,dst),silent=silent)

       return ok
   #@-node:ekr.20080711063656.2:x.rename
   #@+node:ekr.20080711063656.6:x.shadowDirName and shadowPathName
   def shadowDirName (self,filename):

       '''Return the directory for the shadow file corresponding to filename.'''

       x = self

       return g.os_path_dirname(x.shadowPathName(filename))

   def shadowPathName (self,filename):

       '''Return the full path name of filename, resolved using c.fileName()'''

       x = self ; theDir = x.baseDirName()

       return theDir and g.os_path_abspath(g.os_path_join(
           theDir,x.shadow_subdir,x.shadow_prefix + g.shortFileName(filename)))
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
   #@+node:ekr.20080708094444.89:Utils...
   #@+node:ekr.20080708094444.27:x.copy_file_removing_sentinels (not used: might be used in writeOneAtShadowNode
   # Called by updated version of atFile.replaceTargetFileIfDifferent

   def copy_file_removing_sentinels (self,source,target):

       '''Copies sourcefilename to targetfilename, removing sentinel lines.'''

       x = self ; sourcefilename = source ; targetfilename = target

       lines = file(sourcefilename).readlines()

       marker = x.marker_from_extension(sourcefilename)

       regular_lines, junk = x.separate_sentinels(lines,marker)

       x.write_if_changed(regular_lines, sourcefilename, targetfilename)
   #@-node:ekr.20080708094444.27:x.copy_file_removing_sentinels (not used: might be used in writeOneAtShadowNode
   #@+node:ekr.20080708094444.85:x.error & message
   def error (self,s,silent=False):

       x = self

       if not silent:
           g.es_print(s,color='red')

       # For unit testing.
       x.last_error = s
       x.errors += 1

   def message (self,s):

       g.es_print(s,color='orange')
   #@nonl
   #@-node:ekr.20080708094444.85:x.error & message
   #@+node:ekr.20080708094444.11:x.is_sentinel
   def is_sentinel (self, line, marker):

      '''Return true if the line is a sentinel.'''

      return line.lstrip().startswith(marker)
   #@-node:ekr.20080708094444.11:x.is_sentinel
   #@+node:ekr.20080708094444.9:x.marker_from_extension
   def marker_from_extension (self,filename):

       '''Return the sentinel delimiter comment to be used for filename.'''

       delims = g.comment_delims_from_extension(filename)
       for i in (0,1):
           if delims[i] is not None:
               return delims[i]+'@'

       # Try some other choices.
       root, ext = os.path.splitext(filename)

       if ext=='.tmp':
           root, ext = os.path.splitext(root)

       if ext in('.h', '.c'):
           marker = "//@"
       elif ext in(".py", ".cfg", ".ksh", ".txt"):
           marker = '#@'
       elif ext in (".bat",):
           marker = "REM@"
       else:
           self.error("extension %s not known" % ext)
           marker = '#'

       return marker
   #@-node:ekr.20080708094444.9:x.marker_from_extension
   #@+node:ekr.20080708094444.30:x.push_filter_mapping
   def push_filter_mapping (self,filelines, marker):
      """
      Given the lines of a file, filter out all
      Leo sentinels, and return a mapping:

         stripped file -> original file

      Filtering should be the same as
      separate_sentinels
      """

      mapping =[None]

      for i, line in enumerate(filelines):
         if not self.is_sentinel(line,marker):
            mapping.append(i+1)

      return mapping 
   #@-node:ekr.20080708094444.30:x.push_filter_mapping
   #@+node:ekr.20080708094444.29:x.separate_sentinels
   def separate_sentinels (self, lines, marker):

       '''
       Separates regular lines from sentinel lines.

       Returns (regular_lines, sentinel_lines)
       '''

       x = self ; regular_lines = [] ; sentinel_lines = []

       for line in lines:
         if x.is_sentinel(line,marker):
            sentinel_lines.append(line)
         else:
            regular_lines.append(line)

       return regular_lines, sentinel_lines 
   #@-node:ekr.20080708094444.29:x.separate_sentinels
   #@+node:ekr.20080708094444.10:x.write_if_changed & helpers
   def write_if_changed (self,lines, sourcefilename, targetfilename):

       '''Write lines to targetfilename if targetfilename's contents are not lines.

       Set targetfilename's modification date to that of sourcefilename.

       Produces a message, if wanted, about the overwrite, and optionally
       keeps the overwritten file with a backup name.'''

       if not os.path.exists(targetfilename):
           copy = True 
       else:
           copy = lines != file(targetfilename).readlines()

       if copy:
           if print_copy_operations:
               print "Copying ", sourcefilename, " to ", targetfilename, " without sentinals"
           if self.do_backups and os.path.exists(targetfilename):
               self.make_backup_file(backupname,targetfilename)
           outfile = open(targetfilename, "w")
           for line in lines:
               outfile.write(line)
           outfile.close()
           self.copy_modification_time(sourcefilename, targetfilename)

       return copy 
   #@+node:ekr.20080708094444.8:copy_modification_time
   def copy_modification_time(self,sourcefilename,targetfilename):

       """
       Set the target file's modification time to
       that of the source file.
       """

       st = os.stat(sourcefilename)

       # To avoid pychecker/pylint complaints.
       utime = getattr(os,'utime')
       mtime = getattr(os,'mtime')

       if utime:
           utime(targetfilename, (st.st_atime, st.st_mtime))
       elif mtime:
           mtime(targetfilename, st.st_mtime)
       else:
           self.error("Neither os.utime nor os.mtime exists: can't set modification time.")
   #@-node:ekr.20080708094444.8:copy_modification_time
   #@+node:ekr.20080708094444.84:make_backup_file
   def make_backup_file (self,backupname,targetfilename):

       # Keep the old file around while we are debugging.
       count = 0
       backupname = "%s.~%s~"%(targetfilename,count)

       while os.path.exists(backupname):
          count+=1
          backupname = "%s.~%s~"%(targetfilename,count)

       os.rename(targetfilename,backupname)

       if self.print_copy_operations:
          print "backup file in ", backupname 
   #@-node:ekr.20080708094444.84:make_backup_file
   #@-node:ekr.20080708094444.10:x.write_if_changed & helpers
   #@-node:ekr.20080708094444.89:Utils...
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

           # __pychecker__ = '--no-argsused'
               #  msg needed so signature matches base class.

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

           x = self.shadowController

           results = []
           for line in lines:
               if x.is_sentinel(line,self.marker):
                   new_line = line.replace(find,replace)
                   results.append(new_line)
                   # if line != new_line: g.trace(new_line)
               else:
                   results.append(line)

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

               print '%s atShadowTestCase.runTest:failure' % ('*' * 40)
               for aList,tag in ((results,'results'),(self.expected_private_lines,'expected_private_lines')):
                   print '%s...' % tag
                   for i, line in enumerate(aList):
                       print '%3s %s' % (i,repr(line))
                   print '-' * 40

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
    #@	@+others
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

        print title
        # print 'self.i',self.i
        for i, line in enumerate(self.lines):
            marker = g.choose(i==self.i,'**','  ')
            print "%s %3s:%s" % (marker, i, line),
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
       self.trace = self.shadowController.trace_writers
    #@-node:ekr.20080708094444.22:__init__
    #@+node:ekr.20080708094444.23:put
    def put(self, line, tag=''):

        self.lines.append(line)
        self.i+=1
        if self.trace:
            g.trace('%16s %s' % (tag,repr(line)))
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

        print title
        for i, line in enumerate(self.lines):
            marker = '  '
            print "%s %3s:%s" % (marker, i, line),
    #@-node:ekr.20080708094444.26:dump
    #@-others
#@-node:ekr.20080708094444.21:class sourcewriter
#@-others
#@-node:ekr.20080708094444.1:@thin leoShadow.py
#@-leo
