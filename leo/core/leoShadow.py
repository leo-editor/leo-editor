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
#@<< notes >>
#@+node:ekr.20080708094444.51:<< notes >>
#@+at
# 
# 1. Not sure if I should do something about read-only files. Are they a 
# problem? Should I check for them?
# 
# 2. Introduced openForRead and openForWrite. Both are introduced only as a 
# hook for the mod_shadow plugin, and default to
# the predefined open.
# 
# 3. Changed replaceTargetFileIfDifferent to return True if the file has been 
# replaced (otherwise, it still returns None).
# 
# 4. In gotoLineNumber: encapsulated
#                 theFile=open(fileName)
#                 lines = theFile.readlines()
#                 theFile.close()
# into a new method "gotoLinenumberOpen"
# 
# 5. Introduced a new function "applyLineNumberMappingIfAny" in 
# gotoLineNumber. The default implementation returns the argument.
#@-at
#@-node:ekr.20080708094444.51:<< notes >>
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
import sys

# import shutil
# import sys

# plugins_path = g.os_path_join(g.app.loadDir,"..","plugins")
#@-node:ekr.20080708094444.52:<< imports >>
#@nl

# Terminology:
# 'push' create a file without sentinels from a file with sentinels.
# 'pull' propagate changes from a file without sentinels to a file with sentinels.

#@@language python
#@@tabwidth -4
#@@pagewidth 80

#@+others
#@+node:ekr.20080708094444.80:class pluginController
class shadowController:

   '''A class to manage @shadow files'''

   #@   @+others
   #@+node:ekr.20080708094444.79: ctor (shadowConroller)
   def __init__ (self,c):

       self.c = c

       self.print_copy_operations = False   # True: tell when files are copied.
       self.do_backups = False              # True: always make backups of each file.
       self.print_all = False               # True: print intermediate files.

       # Configuration
       self.shadow_subdir_default = 'LeoFolder'
       self.shadow_prefix_default = ''

   #@-node:ekr.20080708094444.79: ctor (shadowConroller)
   #@+node:ekr.20080708192807.1:Propagation...
   #@+node:ekr.20080708094444.36:propagate_changes 
   def propagate_changes(self, old_private_file, old_public_file, marker_from_extension):

       '''Propagate the changes from the public file (without_sentinels)
       to the private file (with_sentinels)'''

       old_public_lines  = file(old_public_file).readlines()
       old_private_lines = file(old_private_file).readlines()
       marker = marker_from_extension(old_public_file)

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

       if ok: g.trace("success!")
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

       while reader.index() < limit:
           line = reader.get()
           if self.is_sentinel(line, marker):
               writer.put(line)
   #@-node:ekr.20080708094444.37:copy_sentinels
   #@+node:ekr.20080708094444.38:propagate_changed_lines
   def propagate_changed_lines(self,new_public_lines,old_private_lines,marker):

       '''Propagate changes from 'new_public_lines' to 'old_private_lines.

       We compare the old and new public lines, create diffs and
       propagate the diffs to the new private lines, copying sentinels as well.

       We have two invariants:
       1. We *never* delete any sentinels.
       2. Insertions that happen at the boundary between nodes will be put at
          the end of a node.  However, insertions must always be done within sentinels.
       '''

       trace = True ; verbose = True
       # mapping tells which line of old_private_lines each line of old_public_lines comes from.
       old_public_lines, mapping = self.strip_sentinels_with_map(old_private_lines,marker)

       # if trace and verbose:
           # print 'mapping',mapping
           # print 'old_public_lines...'
           # for z in old_public_lines:
               # print z,
           # print '(end)'
           # print 'new_public_lines...'
           # for z in new_public_lines:
               # print z,
           # print '(end)'
       #@    << init vars >>
       #@+node:ekr.20080708094444.40:<< init vars >>
       new_private_lines_wtr = sourcewriter()
       # collects the contents of the new file.

       new_public_lines_rdr = sourcereader(new_public_lines)
           # Contains the changed source code.

       old_public_lines_rdr = sourcereader(old_public_lines)
           # this is compared to new_public_lines_rdr to find out the changes.

       old_private_lines_rdr = sourcereader(old_private_lines) # lines_with_sentinels)
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

           print ; print sep1,message,sep1

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
           # The highlights of the loop:
           # 
           # A. Each time through the loop, we have the following invariants:
           # 
           # - old_i is the index into old_public_lines of the start of the 
           # present SequenceMatcher opcode.
           # 
           # - mapping[old_i] is the index into old_private_lines of the start 
           # of the same opcode.
           # 
           # B. Step 1 effectively skips (deletes) all previously unwritten 
           # non-sentinel
           #    lines in old_private_lines_rdr whose index less than 
           # mapping[old_i].
           # 
           # C. As a result, Step 2 does not need to delete elements from the
           #    old_private_lines_rdr explicitly. This explains why the loop 
           # handles the
           #    'insert' and 'delete' opcodes in the same way.
           #@-at
           #@-node:ekr.20080708192807.2:<< about this loop >>
           #@nl
           #@        << Handle the opcode >>
           #@+node:ekr.20080708192807.5:<< Handle the opcode >>
           # Ignore (delete) all unwritten lines of old_private_lines_rdr up to index mapping[old_i].
           # Because of this, nothing has to be explicitly deleted below.
           self.copy_sentinels(old_private_lines_rdr,new_private_lines_wtr,marker,limit=mapping[old_i])

           if tag == 'equal':
               # Copy all lines (including sentinels) from the old private file to the new private file.
               while old_private_lines_rdr.index() <= mapping[old_j-1]:
                  line = old_private_lines_rdr.get()
                  new_private_lines_wtr.put(line)

               # Ignore all new lines up to new_j: the same lines (with sentinels) have just been written.
               new_public_lines_rdr.sync(new_j)

           elif tag in ('insert','replace'):
               # All unwritten lines from old_private_lines_rdr up to mapping[old_i] have already been ignored.
               # Copy lines from new_public_lines_rdr up to new_j.
               while new_public_lines_rdr.index() < new_j:
                   line = new_public_lines_rdr.get()
                   new_private_lines_wtr.put(line)

           elif tag=='delete':
               # All unwritten lines from old_private_lines_rdr up to mapping[old_i] have already been ignored.
               # Leave new_public_lines_rdr unchanged.
               pass

           else:
               g.trace('can not happen: tag = %s' % repr(tag))

           if trace: print_tags(tag, old_i, old_j, new_i, new_j, "After a new tag")
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
   #@+node:ekr.20080708094444.10:write_if_changed & helpers
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
   #@-node:ekr.20080708094444.10:write_if_changed & helpers
   #@+node:ekr.20080708094444.83:test_propagate_changes
   # This is the heart of @shadow.

   def test_propagate_changes (self,
       old_private_lines,      # with_sentinels
       new_public_lines,       # without sentinels
       expected_private_lines, # with sentinels
       marker):

       '''Check that propagate changed lines changes 'before_private_lines' to
       'expected_private_lines' based on changes to 'changed_public_lines'.'''

       results = self.propagate_changed_lines(
           new_public_lines,   # new_lines_without_sentinels
           old_private_lines,  # lines_with_sentinels, 
           marker = marker)

       assert results == expected_private_lines, 'results: %s\n\nexpected_private_lines: %s' % (
           results,expected_private_lines)
   #@-node:ekr.20080708094444.83:test_propagate_changes
   #@+node:ekr.20080708094444.89:Utils...
   #@+node:ekr.20080708094444.27:copy_file_removing_sentinels (helper for at.replaceTargetFileIfDifferent)
   # Called by updated version of atFile.replaceTargetFileIfDifferent

   def copy_file_removing_sentinels (self,sourcefilename,targetfilename,marker_from_extension):

       '''Copies sourcefilename to targetfilename, removing sentinel lines.'''

       # outlines, sentinel_lines = self.read_file_separating_out_sentinels(sourcefilename, marker_from_extension)

       lines = file(sourcefilename).readlines()
       marker = marker_from_extension(sourcefilename)
       regular_lines, sentinel_lines = self.separate_sentinels(lines,marker)
       self.write_if_changed(regular_lines, sourcefilename, targetfilename)
   #@-node:ekr.20080708094444.27:copy_file_removing_sentinels (helper for at.replaceTargetFileIfDifferent)
   #@+node:ekr.20080708094444.9:default_marker_from_extension
   def default_marker_from_extension (self,filename):

       '''Guess the sentinel delimiter comment from the filename's extension.

       This allows testing independent of Leo.'''

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
   #@-node:ekr.20080708094444.9:default_marker_from_extension
   #@+node:ekr.20080708094444.85:error
   def error (self,s):

       g.es_print(s,color='red')
   #@-node:ekr.20080708094444.85:error
   #@+node:ekr.20080708094444.11:is_sentinel
   def is_sentinel (self, line, marker):

      '''Return true if the line is a sentinel.'''

      return line.lstrip().startswith(marker)
   #@-node:ekr.20080708094444.11:is_sentinel
   #@+node:ekr.20080708094444.30:push_filter_mapping
   def push_filter_mapping (self,filelines, marker):
      """
      Given the lines of a file, filter out all
      Leo sentinels, and return a mapping:

         stripped file -> original file

      Filtering should be the same as
      separate_sentinels
      """

      mapping =[None]

      for linecount, line in enumerate(filelines):
         if not self.is_sentinel(line,marker):
            mapping.append(linecount+1)

      return mapping 
   #@-node:ekr.20080708094444.30:push_filter_mapping
   #@+node:ekr.20080708094444.28:read_file_separating_out_sentinels (not used)
   # def read_file_separating_out_sentinels (sourcefilename, marker_from_extension):
      # """
      # Removes sentinels from the lines of 'sourcefilename'.

      # Returns (regular_lines, sentinel_lines)
      # """

      # return self.separate_sentinels(file(sourcefilename).readlines(), marker_from_extension(sourcefilename))
   #@-node:ekr.20080708094444.28:read_file_separating_out_sentinels (not used)
   #@+node:ekr.20080708094444.29:separate_sentinels
   def separate_sentinels (self, lines, marker):

       '''
       Separates regular lines from sentinel lines.

       Returns (regular_lines, sentinel_lines)
       '''

       regular_lines = [] ; sentinel_lines = []

       for line in lines:
         if self.is_sentinel(line,marker):
            sentinel_lines.append(line)
         else:
            regular_lines.append(line)

       return regular_lines, sentinel_lines 
   #@-node:ekr.20080708094444.29:separate_sentinels
   #@-node:ekr.20080708094444.89:Utils...
   #@-others
#@-node:ekr.20080708094444.80:class pluginController
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
    def __init__ (self, lines):
       self.lines = lines 
       self.length = len(self.lines)
       self.i = 0
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
        """
        Little dump routine for easy debugging
        """
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
    def __init__ (self):

       self.i = 0
       self.lines =[]
    #@-node:ekr.20080708094444.22:__init__
    #@+node:ekr.20080708094444.23:put
    def put(self, line):

       self.lines.append(line)
       self.i+=1
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
