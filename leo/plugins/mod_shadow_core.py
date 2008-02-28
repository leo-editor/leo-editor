#@+leo-ver=4-thin
#@+node:ekr.20060715100156.8:@thin mod_shadow_core.py
__not_a_plugin__ = True

#@<< imports >>
#@+node:ekr.20060715100156.9:<< imports >>
import difflib
import sys
import os
#@-node:ekr.20060715100156.9:<< imports >>
#@nl
#@<< globals >>
#@+node:ekr.20060715100156.10:<< globals >>
print_copy_operations = False   # True: tell when files are copied.
do_backups = False              # True: always make backups of each file.
print_all = False               # True: print intermediate files.

if 0: # These are now computed as necessary using c.config class.
    prefix = "" # Prefix to be used for shadow files, if any.
    active = True # The plugin can be switched off by this switch
    verbosity = 10

__version__ = "$Rev: 1765 $"
__author__  = "Bernhard Mulder"
__date__    = "$Date: 2007/05/29 13:59:04 $"
__cvsid__   = "$Id: mod_shadow_core.py,v 1.11 2007/05/29 13:59:04 edream Exp $"
#@-node:ekr.20060715100156.10:<< globals >>
#@nl

#@+others
#@+node:ekr.20060715100156.11:plugin core
#@+others
#@+node:ekr.20060715100156.12:auxilary functions
#@+others
#@+node:ekr.20060715100156.13:copy_time
def copy_time (sourcefilename, targetfilename):
   """
   Set the modification time of the targetfile the same
   as the sourcefilename.

   Does not work currently, if we can not read or change
   the modification time.
   """
   st = os.stat(sourcefilename)
   if hasattr(os, 'utime'):
      os.utime(targetfilename, (st.st_atime, st.st_mtime))
   elif hasattr(os, 'mtime'):
      os.mtime(targetfilename, st.st_mtime)
   else:
      assert 0, "Sync operation can't work if no modification time can be set"
#@-node:ekr.20060715100156.13:copy_time
#@+node:ekr.20060715100156.14:default_marker_from_extension
def default_marker_from_extension (filename):
    """
    Tries to guess the sentinel leadin
    comment from the filename extension.

    This function allows testing independent of Leo

    """
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
        assert 0, "extension %s not handled by this plugin" % ext 
    return marker 
#@-node:ekr.20060715100156.14:default_marker_from_extension
#@+node:ekr.20060715100156.15:write_if_changed
def write_if_changed (lines, sourcefilename, targetfilename):
   """

   Checks if 'lines' matches the contents of
   'targetfilename'. Refreshes the targetfile with 'lines' if not.
   'sourcefilename' supplies the modification time to be used for
   'targetfilename'

   Produces a message, if wanted, about the overrite, and optionally
   keeps the overwritten file with a backup name.

   """
   if not os.path.exists(targetfilename):
      copy = True 
   else:
      copy = lines != file(targetfilename).readlines()
   if copy:
      if print_copy_operations:
         print "Copying ", sourcefilename, " to ", targetfilename, " without sentinals"

      if do_backups:
         # Keep the old file around while we are debugging this script
         if os.path.exists(targetfilename):
            count = 0
            backupname = "%s.~%s~"%(targetfilename,count)
            while os.path.exists(backupname):
               count+=1
               backupname = "%s.~%s~"%(targetfilename,count)
            os.rename(targetfilename,backupname)
            if print_copy_operations:
               print "backup file in ", backupname 
      outfile = open(targetfilename, "w")
      for line in lines:
         outfile.write(line)
      outfile.close()
      copy_time(sourcefilename, targetfilename)
   return copy 
#@-node:ekr.20060715100156.15:write_if_changed
#@+node:ekr.20060715100156.16:is_sentinel
def is_sentinel (line, marker):
   """
   Check if line starts with a Leo marker.

   Leo markers are filtered away by this script.

   Leo markers start with a comment character, which dependends
   on the language used. That's why the marker is passed in.
   """
   return line.lstrip().startswith(marker)
#@-node:ekr.20060715100156.16:is_sentinel
#@+node:ekr.20060715100156.17:class sourcereader
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
    #@+node:ekr.20060715100156.18:__init__
    def __init__ (self, lines):
       self.lines = lines 
       self.length = len(self.lines)
       self.i = 0
    #@-node:ekr.20060715100156.18:__init__
    #@+node:ekr.20060715100156.19:index
    def index (self):
       return self.i 
    #@-node:ekr.20060715100156.19:index
    #@+node:ekr.20060715100156.20:get
    def get (self):
       result = self.lines[self.i]
       self.i+=1
       return result 
    #@-node:ekr.20060715100156.20:get
    #@+node:ekr.20060715100156.21:sync
    def sync (self,i):
       self.i = i 
    #@-node:ekr.20060715100156.21:sync
    #@+node:ekr.20060715100156.22:size
    def size (self):
       return self.length 
    #@-node:ekr.20060715100156.22:size
    #@+node:ekr.20060715100156.23:atEnd
    def atEnd (self):
       return self.index>=self.length 
    #@-node:ekr.20060715100156.23:atEnd
    #@+node:ekr.20060715100156.24:clone
    def clone(self):
        sr = sourcereader(self.lines)
        sr.i = self.i
        return sr
    #@nonl
    #@-node:ekr.20060715100156.24:clone
    #@+node:ekr.20060715100156.25:dump
    def dump(self, title):
        """
        Little dump routine for easy debugging
        """
        print title
        print self.i
        for i, line in enumerate(self.lines):
            if i == self.i:
                marker = "===>"
            else:
                marker = ""
            print "%s%s:%s" % (marker, i, line),
    #@nonl
    #@-node:ekr.20060715100156.25:dump
    #@-others
#@-node:ekr.20060715100156.17:class sourcereader
#@+node:ekr.20060715100156.26:class sourcewriter
class sourcewriter:
    """
    Convenience class to capture output to a file.

    Similar to class sourcereader.
    """
    #@	@+others
    #@+node:ekr.20060715100156.27:__init__
    def __init__ (self):
       self.i = 0
       self.lines =[]
    #@-node:ekr.20060715100156.27:__init__
    #@+node:ekr.20060715100156.28:put
    def put(self, line):
       self.lines.append(line)
       self.i+=1
    #@-node:ekr.20060715100156.28:put
    #@+node:ekr.20060715100156.29:index
    def index (self):
       return self.i 
    #@-node:ekr.20060715100156.29:index
    #@+node:ekr.20060715100156.30:getlines
    def getlines (self):
       return self.lines 
    #@-node:ekr.20060715100156.30:getlines
    #@+node:ekr.20060715100156.31:dump
    def dump(self, title):
        """
        Little dump routine for easy debugging
        """
        print title
        for i, line in enumerate(self.lines):
            print "%s:%s" % (i, line),
    #@nonl
    #@-node:ekr.20060715100156.31:dump
    #@-others
#@-node:ekr.20060715100156.26:class sourcewriter
#@+node:ekr.20060715100156.32:copy_file_removing_sentinels
def copy_file_removing_sentinels (sourcefilename, targetfilename, marker_from_extension):
    """
    Filter out Leo comments.

    Writes the lines from sourcefilename without Leo comments
    to targetfilename, if the contents of those lines is different
    from the lines in targetfilename.
    """
    outlines, sentinel_lines = read_file_separating_out_sentinels(sourcefilename, marker_from_extension)
    write_if_changed(outlines, sourcefilename, targetfilename)

#@-node:ekr.20060715100156.32:copy_file_removing_sentinels
#@+node:ekr.20060715100156.33:read_file_separating_out_sentinels
def read_file_separating_out_sentinels (sourcefilename, marker_from_extension):
   """
   Removes sentinels from the lines of 'sourcefilename'.

   Returns (regular_lines, sentinel_lines)
   """

   return separate_regular_lines_from_sentinel_lines(file(sourcefilename).readlines(), marker_from_extension(sourcefilename))
#@-node:ekr.20060715100156.33:read_file_separating_out_sentinels
#@+node:ekr.20060715100156.34:separate_regular_lines_from_sentinel_lines
def separate_regular_lines_from_sentinel_lines (lines, marker):
   """

   Removes sentinels from lines.

   Returns (regular_lines, sentinel_lines)

   """
   result, sentinel_lines =[],[]
   for line in lines:
      if is_sentinel(line,marker):
         sentinel_lines.append(line)
      else:
         result.append(line)
   return result, sentinel_lines 
#@-node:ekr.20060715100156.34:separate_regular_lines_from_sentinel_lines
#@+node:ekr.20060715100156.35:push_filter_mapping
def push_filter_mapping (filelines, marker):
   """
   Given the lines of a file, filter out all
   Leo sentinels, and return a mapping:

      stripped file -> original file

   Filtering should be the same as
   separate_regular_lines_from_sentinel_lines
   """

   mapping =[None]
   for linecount, line in enumerate(filelines):
      if not is_sentinel(line,marker):
         mapping.append(linecount+1)
   return mapping 
#@-node:ekr.20060715100156.35:push_filter_mapping
#@-others
#@nonl
#@-node:ekr.20060715100156.12:auxilary functions
#@+node:ekr.20060715100156.36:class sentinel_squasher
class sentinel_squasher:
    """
    The heart of the script.

    Creates files without sentinels from files with sentinels.

    Propagates changes in the files without sentinels back
    to the files with sentinels.

    """
    #@	@+others
    #@+node:ekr.20060715100156.37:__init__
    def __init__(self, es, nullObject):
        self.es = es
        self.nullObject = nullObject
    #@-node:ekr.20060715100156.37:__init__
    #@+node:ekr.20060715100156.38:check_lines_for_equality
    def check_lines_for_equality (self, lines1, lines2, message, lines1_message, lines2_message, es):
        """
        Little helper function to get nice output if something goes wrong.

        Checks if lines1 == lines2. If not,
            1. Print the two lists line1 and line2
            2. Put the line1 into the file mod_shadow.tmp1 and lines2 into mod_shadow.tmp2.
        """
        if lines1==lines2:
            return 
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
        es("The mod_shadow plugin did not pick up the external changes correctly; please check mod_shadow.tmp1 and mod_shadow.tmp2 for differences")
        assert 0, "Malfunction of mod_shadow plugin"
    #@-node:ekr.20060715100156.38:check_lines_for_equality
    #@+node:ekr.20060715100156.39:create_back_mapping
    def create_back_mapping (self, sourcelines, marker):
       """

       'sourcelines' is a list of lines of a file with sentinels.

       Creates a new list of lines without sentinels, and keeps a
       mapping which maps each source line in the new list back to its
       original line.

       Returns the new list of lines, and the mapping.

       For programming convenience, the mapping is extended by an
       extra element at the end.
       """
       mapping, resultlines =[],[]

       si, l = 0, len(sourcelines)
       while si < l:
          sline = sourcelines[si]
          if not is_sentinel(sline,marker):
             resultlines.append(sline)
             mapping.append(si)
          si+=1

       # for programing convenience, we create an additional mapping entry.
       # This simplifies the programming of the copy_sentinels function below.
       mapping.append(si)
       return resultlines, mapping 
    #@-node:ekr.20060715100156.39:create_back_mapping
    #@+node:ekr.20060715100156.40:check_the_final_output
    def check_the_final_output(self, new_lines_with_sentinels, changed_lines_without_sentinels, sentinel_lines, marker, es):
        """
        Check that we produced a valid output.

        Input:
            new_targetlines:   the lines with sentinels which produce changed_lines_without_sentinels.
            sentinels:         new_targetlines should include all the lines from sentinels.

        checks:
            1. new_targetlines without sentinels must equal changed_lines_without_sentinels.
            2. the sentinel lines of new_targetlines must match 'sentinels'
        """
        new_lines_without_sentinels, new_sentinel_lines,  = separate_regular_lines_from_sentinel_lines (new_lines_with_sentinels, marker)
        self.check_lines_for_equality(
            lines1 = new_lines_without_sentinels,
            lines2 = changed_lines_without_sentinels,
            message = "Checking if all changes have been incorporated",
            lines1_message = "new lines (without sentinels)",
            lines2_message = "new lines as produced by the read algorithm",
            es = es)

        self.check_lines_for_equality(
            lines1 = sentinel_lines,
            lines2 = new_sentinel_lines,
            message = "Checking if all sentinals have been preserved",
            lines1_message = "sentinel lines of the new file",
            lines2_message = "old sentinels",
            es = es)

        # maybe later, we can replace the above two function calls with the two assertions below    
        #  assert new_lines_without_sentinels == changed_lines_without_sentinels, "new_sentinel_lines != changed_lines_without_sentinels"
        # assert new_sentinel_lines == sentinels, "sentinels where changed!"

    #@-node:ekr.20060715100156.40:check_the_final_output
    #@+node:ekr.20060715100156.41:propagate_changes_from_file_without_sentinels_to_file_with_sentinels
    def propagate_changes_from_file_without_sentinels_to_file_with_sentinels (self, with_sentinels, without_sentinels, marker_from_extension):
        """
        Propagate the changes from file 'without_sentinels' to file 'with_sentinels'.

        This is the most complicated part of the plugin.
        """
        # g.trace(without_sentinels, with_sentinels)

        lines_without_sentinels = file(without_sentinels).readlines()
        lines_with_sentinels = file(with_sentinels).readlines()
        marker = marker_from_extension(without_sentinels)

        new_lines_with_sentinels = self.propagate_changes_from_lines_without_sentinels_to_lines_with_sentinels(
            lines_without_sentinels,
            lines_with_sentinels, marker)
        written = write_if_changed(
            new_lines_with_sentinels,
            targetfilename=with_sentinels, sourcefilename=without_sentinels)
        return written
    #@nonl
    #@-node:ekr.20060715100156.41:propagate_changes_from_file_without_sentinels_to_file_with_sentinels
    #@+node:ekr.20060715100156.42:copy_sentinels
    def copy_sentinels(self, reader_lines_with_sentinels, writer_new_sourcelines, marker, upto):
        """
        Copy the sentinels from reader_lines_with_sentinels to writer_new_sourcelines upto,
        but not including, upto.
        """
        while reader_lines_with_sentinels.index() < upto:
            line = reader_lines_with_sentinels.get()
            if is_sentinel(line, marker):
                writer_new_sourcelines.put(line)
    #@-node:ekr.20060715100156.42:copy_sentinels
    #@+node:ekr.20060715100156.43:propagate_changes_from_lines_without_sentinels_to_lines_with_sentinels
    def propagate_changes_from_lines_without_sentinels_to_lines_with_sentinels(self, 
            new_lines_without_sentinels, lines_with_sentinels,
            marker):
        """
        Propagate the changes from lines_without_sentinels to lines_with_sentinels,
        assuming that the sentinel lines start with marker (modulo leading blanks).

        lines_without_sentinels contain changes which should be integrated into lines_with_sentinels.
        """
        #@    <<print_all_func>>
        #@+node:ekr.20060715100156.44:<< print_all_func>>

        def print_all_func(message):
            """
            Print all relevent variables to debug this function
            """
            if not print_all:
                return
            print
            print
            print "============== %s ===================================" % message
            print
            print "tag:", tag, "  i1_old_lines:", i1_old_lines, "  i2_old_lines:", i2_old_lines, "  i1_new_lines:", i1_new_lines, "  i2_new_lines:", i2_new_lines
            print
            print "-----------------------------------"
            reader_lines_with_sentinels.dump('reader_lines_with_sentinels (old)')
            print "-----------------------------------"
            reader_old_lines_without_sentinels.dump('reader_old_lines_without_sentinels')
            print "-----------------------------------"
            reader_new_lines_without_sentinels.dump('reader_new_lines_without_sentinels')
            print "-----------------------------------"
            writer_new_sourcelines.dump('writer_new_sourcelines (new)')
            print "-----------------------------------"

        #@-node:ekr.20060715100156.44:<< print_all_func>>
        #@nl
        old_lines_without_sentinels, mapping = self.create_back_mapping(lines_with_sentinels, marker)

        #@    << init vars >>
        #@+node:ekr.20060715100156.45:<< init vars >>
        writer_new_sourcelines = sourcewriter()
        # collects the contents of the new file.

        reader_new_lines_without_sentinels = sourcereader(new_lines_without_sentinels)
        # reader_new_lines_without_sentinels contains the changed source code.

        reader_old_lines_without_sentinels = sourcereader(old_lines_without_sentinels)
        # this is compared to reader_new_lines_without_sentinels to find out the changes.

        reader_lines_with_sentinels = sourcereader(lines_with_sentinels)
        # This is the file which is currently produced by Leo, with sentinels.

        #@+at 
        #@nonl
        # We compare the 'lines_without_sentinels' with 
        # 'old_lines_without_sentinels' and propagate
        # the changes back into 'write_new_sourcelines' while making sure that
        # all sentinels of 'lines_with_sentinels' are copied as well.
        # 
        # An invariant of the following loop is that all three readers are in 
        # sync.
        # In addition, writer_new_sourcelines has accumulated the new lines, 
        # which
        # is going to replace lines_with_sentinels.
        #@-at
        #@@c

        # Check that all ranges returned by get_opcodes() are contiguous
        old_i2_old_lines, old_i2_modified_lines = -1,-1


        tag = i1_old_lines = i2_old_lines = i1_new_lines = i2_new_lines = None
        #@nonl
        #@-node:ekr.20060715100156.45:<< init vars >>
        #@nl

        sm = difflib.SequenceMatcher(None, old_lines_without_sentinels, new_lines_without_sentinels)

        for tag, i1_old_lines, i2_old_lines, i1_new_lines, i2_new_lines in sm.get_opcodes():
            print_all_func("After a new tag")
            # import pdb; pdb.set_trace()
            if tag == 'insert' and mapping[i1_old_lines] >= len(lines_with_sentinels):
                pass
            else:
                self.copy_sentinels(reader_lines_with_sentinels, writer_new_sourcelines, marker, upto = mapping[i1_old_lines])
            if tag=='equal':
                #@            << handle 'equal' op >>
                #@+node:ekr.20060715100156.46:<< handle 'equal' op >>
                # Copy the lines from the leo file to the new sourcefile.
                # This loop copies both text and sentinels.
                while reader_lines_with_sentinels.index() <= mapping[i2_old_lines-1]:
                   line = reader_lines_with_sentinels.get()
                   writer_new_sourcelines.put(line)

                reader_new_lines_without_sentinels.sync(i2_new_lines)
                #@-node:ekr.20060715100156.46:<< handle 'equal' op >>
                #@nl
            elif tag=='replace':
                #@            << handle 'replace' op >>
                #@+node:ekr.20060715100156.47:<< handle 'replace' op >>
                while reader_new_lines_without_sentinels.index() < i2_new_lines:
                   line = reader_new_lines_without_sentinels.get()
                   writer_new_sourcelines.put(line)
                #@-node:ekr.20060715100156.47:<< handle 'replace' op >>
                #@nl
            elif tag=='delete':
                #@            << handle 'delete' op >>
                #@+node:ekr.20060715100156.48:<< handle 'delete' op >>
                # No copy operation for a deletion!
                pass
                #@-node:ekr.20060715100156.48:<< handle 'delete' op >>
                #@nl
            elif tag=='insert':
                #@            << handle 'insert' op >>
                #@+node:ekr.20060715100156.49:<< handle 'insert' op >>
                while reader_new_lines_without_sentinels.index()<i2_new_lines:
                   line = reader_new_lines_without_sentinels.get()
                   writer_new_sourcelines.put(line)

                #@-node:ekr.20060715100156.49:<< handle 'insert' op >>
                #@nl
            else: assert 0

        print_all_func("Before final copy")
        self.copy_sentinels(reader_lines_with_sentinels, writer_new_sourcelines, marker, upto = reader_lines_with_sentinels.size())
        print_all_func("At the end")
        result = writer_new_sourcelines.getlines()

        #@    << final correctness check>>
        #@+node:ekr.20060715100156.50:<< final correctness check >>
        if 1:
            # Always check the correctnes for now, until we have gained confidence in the plugin.
            t_sourcelines, t_sentinel_lines = separate_regular_lines_from_sentinel_lines(writer_new_sourcelines.lines, marker)
            self.check_the_final_output(
                new_lines_with_sentinels        = result,
                changed_lines_without_sentinels = new_lines_without_sentinels,
                sentinel_lines                  = t_sentinel_lines,
                marker                          = marker,
                es                              = self.es)
        #@-node:ekr.20060715100156.50:<< final correctness check >>
        #@nl
        return result
    #@nonl
    #@-node:ekr.20060715100156.43:propagate_changes_from_lines_without_sentinels_to_lines_with_sentinels
    #@-others
#@-node:ekr.20060715100156.36:class sentinel_squasher
#@-others
#@nonl
#@-node:ekr.20060715100156.11:plugin core
#@+node:ekr.20060715100156.51:propagate_changes_test
def propagate_changes_test (c,
    before_with_sentinels_lines,
    changed_without_sentinels_lines,
    after_with_sentinel_lines, marker, es, nullObject):
    """"
    Check if 'before_with_sentinels_lines' is transformed to 'after_with_sentinel_lines' when picking
    up changes from 'changed_without_sentinels_lines'.
    """
    sq = sentinel_squasher(c, es, nullObject)
    resultlines = sq.propagate_changes_from_lines_without_sentinels_to_lines_with_sentinels(
        new_lines_without_sentinels = changed_without_sentinels_lines, 
        lines_with_sentinels        = before_with_sentinels_lines, 
        marker = marker)
    assert resultlines == after_with_sentinel_lines, "Test failed: changes have not been propagated back properly"

#@-node:ekr.20060715100156.51:propagate_changes_test
#@-others
#@nonl
#@-node:ekr.20060715100156.8:@thin mod_shadow_core.py
#@-leo
