#@+leo-ver=4-thin
#@+node:ekr.20060715100156.52:@thin mod_shadow.py
# Some unit tests for the core file exist.

#@<<docstring>>
#@+node:ekr.20060715100156.53:<< docstring >>
"""
Use a subfolder for files with Leo comments.

The shadow plugin allows you to use Leo with files which contain no
Leo comments, and still have information flow in both directions:
from the file into Leo, and from Leo into the file.

To use this plugin:

1. Install the shadow script button found in leoPy.leo in the node::

    Code-->Buttons and settings-->@@button shadow

   That is, copy and paste this @button node to your Leo outline, and change @@ to @.

2. Position the cursor somewhere in your tree.

3. Clicking the shadow button will create a shadow file for all @thin nodes
   in the selected outline.

After this initial setup, changes in Leo will be reflected both in the file
in the Leo subfolder, and the file without sentinels.
Conversely, changes in the file without sentinels will flow back to the file
in the leo subfolder, and show up in Leo.
Text insertions within a node will show up as expected. Text insertion
at the end of the node will show up and the end of the node.
Note that the plugin never structures input; this has to be done manually
within Leo.

You can set settings for this plugin in leoSettings.leo at::

    @settings-->Plugins-->shadow plugin.

- @string shadow_subdir (default: LeoFolder): name of the shadow directory.

- @string shadow_prefix (default: x): prefix of shadow files.
  This prefix allows the shadow file and the original file to have different names.
  This is useful for name-based tools like py.test.
"""
#@-node:ekr.20060715100156.53:<< docstring >>
#@nl

# Terminology:
# 'push' create a file without sentinels from a file with sentinels.
# 'pull' propagate changes from a file without sentinels to a file with sentinels.

#@@language python
#@@tabwidth -4

__version__ = "0.10.4"
#@<< version history >>
#@+node:ekr.20060715100156.54:<< version history >>
#@@killcolor 
#@+at
# 
# 0.1: Original code by Bernhard Mulder.
# 
# 0.2: Modifications by EKR.
# 
# - The correct spelling is "Leo", not "LEO".
# - The name of the folder will be "leo-shadow", not "LEO"
#   This should perhaps be a configuration option.
# - Modified code to work with simplified atFile class.
# - Changed the name of the .ini file to mod_shadow.ini.
# - Use import leo.core.leoGlobals as g.
# 
# 0.9 Adapt to cvs post 4.2 by Bernhard Mulder
# - fixed assertion in original_replaceTargetFileIfDifferent
# 
# 0.9.1 Added prefix option.
# 
# 0.9.2 Split up the most complicated functions into two:
#     propagate_changes_from_file_without_sentinels_to_file_with_sentinels
#         operates on files.
#     propagate_changes_from_lines_without_sentinels_to_lines_with_sentinels
#         operates on lines.
#    The latter can be tested without files, and outside Leo.
# 0.9.3 EKR:
# - Changed default shadow directory from 'Leo' to 'LeoShadow'.
# - Added @thin mod_shadow.ini.
# - use g.importFromPath to import mod_shadow_core.
# 0.9.4 EKR:
# - Added guard for self.line_mapping in applyLineNumberMappingIfAny.
# 0.9.5 EKR:
# - Renamed test_propagate_changes_Leo to do_test_propagate_changes_Leo
#   so the unit tests don't try to run this.
# 0.10.1 EKR:
# - Use settings in leoSettings.leo rather than an .ini file.
# - Created init function and removed main function.
# - active global is no longer used.
# 0.10.2 EKR: Removed 'active' and 'testing' globals and the stopTesting 
# function.
# 0.10.4 EKR: Revised docstring.
#@-at
#@nonl
#@-node:ekr.20060715100156.54:<< version history >>
#@nl
#@<< globals >>
#@+node:ekr.20060715100156.55:<< globals >>
__version__ = "$Rev: 3076 $"
__author__  = "Bernhard Mulder"
__date__    = "$Date: 2007/05/29 13:59:04 $"
__cvsid__   = "$Id: mod_shadow.py,v 1.18 2007/05/29 13:59:04 edream Exp $"
#@-node:ekr.20060715100156.55:<< globals >>
#@nl
#@<< Notes >>
#@+node:ekr.20060715100156.56:<< Notes >>
#@+doc
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
#@-doc
#@-node:ekr.20060715100156.56:<< Notes >>
#@nl
#@<< Implementation Notes >>
#@+node:ekr.20060715100156.57:<< Implementation notes >>
#@+doc
# The plugin deals with two set of files:
#     1. The sourcefiles as seen by Leo.
#     2. The sourcefiles as seen by the user.
# The sourcefiles as seen by Leo live in a subdirectory,
# the sourcefiles as seen by the user live in the regular directory.
# 
# When a file is first read by Leo, we have to create a file without
# sentinels in the regular directory.
# 
# That's all fairly easy, once the places within Leo have been identified 
# where
# the changes have to be made.
# 
# The slightly hard thing to do is to pick up changes from the file without
# sentinels, and put them into the file with sentinels.
# 
# We have two invariants:
#     1. We NEVER delete any sentinels.
#     2. As a slighly weaker condition, insertions which could be put either
#        at the end of a node, or the beginning of the next node, should be 
# put
#        at the end of the node.
#        The exception to this rule is the last node. Insertions should 
# *always*
#        be done within sentinels.
# 
#@-doc
#@-node:ekr.20060715100156.57:<< Implementation notes >>
#@nl
#@<< imports >>
#@+node:ekr.20060801095508:<< imports >>
import leo.core.leoGlobals as g 

import leo.core.leoAtFile as leoAtFile
import leo.core.leoCommands as leoCommands
import leo.core.leoImport as leoImport 
# import leo.core.leoPlugins as leoPlugins

import ConfigParser 
import os
# import shutil
# import sys

plugins_path = g.os_path_join(g.app.loadDir,"..","plugins")
mod_shadow_core = g.importFromPath('mod_shadow_core',plugins_path)

shadow_subdir_default = 'LeoFolder'
shadow_prefix_default = ''
#@-node:ekr.20060801095508:<< imports >>
#@nl

#@+others
#@+node:ekr.20060801095508.1:Module level
#@+node:ekr.20060801095508.2:init
def init ():

    ok = mod_shadow_core is not None and not g.app.unitTesting
        # Not safe for unit testing: changes Leo's core.

    if ok:
        putInHooks()
        g.es_print("Shadow plugin enabled!",color="orange")

    return ok
#@nonl
#@-node:ekr.20060801095508.2:init
#@+node:ekr.20060715100156.61:putInHooks
def putInHooks ():
    """Modify methods in Leo's core to support this plugin."""

    # Need to modify Leo's Kernel first
    # Overwrite existing Leo methods.
    g.funcToMethod(replaceTargetFileIfDifferent,leoAtFile.atFile)
    g.funcToMethod(massageComment,leoImport.leoImportCommands)

    # Add new methods used by this plugin to various classes.
    g.funcToMethod(openForRead,leoAtFile.atFile)
    g.funcToMethod(openForWrite,leoAtFile.atFile)
    g.funcToMethod(gotoLineNumberOpen,leoCommands.Commands)
    g.funcToMethod(applyLineNumberMappingIfAny, leoCommands.Commands)
#@-node:ekr.20060715100156.61:putInHooks
#@+node:ekr.20060715100156.62:OLDapplyConfiguration
def applyConfiguration (config=None):

    """Called when the user presses the "Apply" button on the Properties form.

    Not sure yet if we need configuration options for this plugin."""

    if config is None:
        fileName = os.path.join(g.app.loadDir,"..","plugins","mod_shadow.ini")
        if os.path.exists(fileName):
            config = ConfigParser.ConfigParser()
            config.read(fileName)
    if config:
        mod_shadow_core.active = config.getboolean("Main","Active")
        mod_shadow_core.testing = config.getboolean("Main", "testing")
        mod_shadow_core.verbosity = config.getint("Main", "verbosity")
        mod_shadow_core.prefix = config.get("Main", "prefix")
        mod_shadow_core.print_copy_operations = config.get("Main", "print_copy_operations")
        mod_shadow_core.shadow_subdir = config.get("Main", "shadow_subdir")
#@nonl
#@-node:ekr.20060715100156.62:OLDapplyConfiguration
#@+node:ekr.20060715100156.63:check_for_shadow_file (Not used)
def check_for_shadow_file (self,filename):
    """
    Check if there is a shadow file for filename.
    Return:
        - the name of the shadow file,
        - an indicator if the file denoted by 'filename' is
        of zero length.
    """
    dir, simplename = os.path.split(filename)
    rootname, ext = os.path.splitext(simplename)
    if ext=='.tmp':
        shadow_filename = os.path.join(dir, mod_shadow_core.shadow_subdir, mod_shadow_core.prefix + rootname)
        if os.path.exists(shadow_filename):
            resultname = os.path.join(dir, mod_shadow_core.shadow_subdir, mod_shadow_core.prefix + simplename)
            return resultname, False 
        else:
            return '', False 
    else:
        shadow_filename = os.path.join(dir,mod_shadow_core.shadow_subdir,mod_shadow_core.prefix + simplename)
        if os.path.exists(shadow_filename):
            return shadow_filename, os.path.getsize(filename)<= 2
        else:
            return '', False 
#@nonl
#@-node:ekr.20060715100156.63:check_for_shadow_file (Not used)
#@+node:ekr.20060801102118:getVerbosity
def getVerbosity (c):

    verbosity = c.config.getInt('shadow_verbose')
    if verbosity is None: verbosity = 1
    return verbosity
#@nonl
#@-node:ekr.20060801102118:getVerbosity
#@+node:bwmulder.20060806152117:marker_from_extension
def marker_from_extension(filename):
    return g.comment_delims_from_extension(filename)[0] + "@"
#@nonl
#@-node:bwmulder.20060806152117:marker_from_extension
#@-node:ekr.20060801095508.1:Module level
#@+node:ekr.20060715100156.68:Leo overwrites
#@+node:ekr.20060715100156.65:openForRead
def openForRead (self, filename, rb):
    """
    Replaces the standard open for reads.
    Checks and handles shadow files:
        if the length of the real file is zero:
            update the real file from the shadow file.
        else:
            update the shadow file from the real file.
    """
    c = self.c
    shadow_subdir = c.config.getString('shadow_subdir') or shadow_subdir_default
    shadow_prefix = c.config.getString('shadow_prefix') or shadow_prefix_default
    shadow_verbosity = getVerbosity(c)
    try:
        dir, simplename = os.path.split(filename)
        shadow_filename = os.path.join(dir,shadow_subdir,shadow_prefix + simplename)
        if os.path.exists(shadow_filename):
            file_to_read_from = shadow_filename
            newfile = os.path.exists(filename)and os.path.getsize(filename)<=2            
            if newfile:
                if shadow_verbosity >= 2:
                    g.es("Copy %s to %s without sentinels"%(shadow_filename, filename))
                mod_shadow_core.copy_file_removing_sentinels(sourcefilename=shadow_filename,
                                             targetfilename=filename,
                                             marker_from_extension=marker_from_extension)
            else:
                sq = mod_shadow_core.sentinel_squasher(g.es, g.nullObject)
                if shadow_verbosity >= 2:
                    g.es("reading from shadow directory %s"% (
                        shadow_subdir),color="orange")
                written = sq.propagate_changes_from_file_without_sentinels_to_file_with_sentinels(
                                with_sentinels=shadow_filename,
                                without_sentinels=filename,
                                marker_from_extension=marker_from_extension)
                if written:
                    g.es("file %s updated from %s" % (shadow_filename, filename), color="orange")
        else:
            file_to_read_from = filename 
        return open(file_to_read_from,'rb')
    except:
        # Make sure failures to open a file generate clear messages.
        g.es_exception()
        raise 
#@nonl
#@-node:ekr.20060715100156.65:openForRead
#@+node:ekr.20060715100156.66:openForWrite
def openForWrite (self, filename, wb):
    """
    Replaces the standard open for writes:
        - Check if filename designates a file
          which has a shadow file.
          If so, write to the shadow file,
          and update the real file after the close.
    """
    c = self.c
    shadow_subdir = c.config.getString('shadow_subdir') or shadow_subdir_default
    shadow_prefix = c.config.getString('shadow_prefix') or shadow_prefix_default
    shadow_verbosity = getVerbosity(c)
    dir, simplename = os.path.split(filename)
    rootname, ext = os.path.splitext(simplename)
    assert ext=='.tmp'
    shadow_filename = os.path.join(dir,shadow_subdir, shadow_prefix + rootname)
    self.writing_to_shadow_directory = os.path.exists(shadow_filename)
    if self.writing_to_shadow_directory:
        self.shadow_filename = shadow_filename 
        if shadow_verbosity >= 2: 
            g.es("Using shadow file in folder %s" % shadow_subdir,color="orange")
        file_to_use = os.path.join(dir,shadow_subdir,shadow_prefix + simplename)
    else:
        file_to_use = filename 
    return open(file_to_use,'wb')
#@-node:ekr.20060715100156.66:openForWrite
#@+node:ekr.20060715100156.67:gotoLineNumberOpen
def gotoLineNumberOpen (self,filename):
    """
    Open a file for "goto linenumber" command and check if a shadow file exists.
    Construct a line mapping. This line_mapping instance variable is empty if
    no shadow file exist, otherwise it contains a mapping 
    shadow file number -> real file number.
    """
    try:
        shadow_subdir = self.config.getString('shadow_subdir') or shadow_subdir_default
        shadow_prefix = self.config.getString('shadow_prefix') or shadow_prefix_default
        dir, simplename = os.path.split(filename)
        shadow_filename = os.path.join(dir,shadow_subdir,shadow_prefix + simplename)
        if os.path.exists(shadow_filename):
            lines = file(shadow_filename).readlines()
            self.line_mapping = mod_shadow_core.push_filter_mapping(
                lines, marker_from_extension(shadow_filename))
        else:
            self.line_mapping ={}
            lines = file(filename).readlines()
        return lines 
    except:
        # Make sure failures to open a file generate clear messages.
        g.es_exception()
        raise
#@nonl
#@-node:ekr.20060715100156.67:gotoLineNumberOpen
#@+node:ekr.20060715100156.69:gotoLineNumber
#@+node:ekr.20060715100156.70:applyLineNumberMappingIfAny
def applyLineNumberMappingIfAny(self, n):
    """
    Hook for mod_shadow plugin.
    """

    if hasattr(self,'line_mapping') and self.line_mapping:
        return self.line_mapping[n]
    else:
        return n
#@nonl
#@-node:ekr.20060715100156.70:applyLineNumberMappingIfAny
#@-node:ekr.20060715100156.69:gotoLineNumber
#@+node:ekr.20060715100156.71:writing
#@+doc 
# Just like for reading, we redirect the writing to the shadow file, if
# one is there.
# 
# Writing is slightly more complicated by the fact
# that Leo writes the information first to a
# temporary file, before renaming the temporary file
# to the real filename.
# 
# We must therefore patch in two places:
#     -When the temporary file is written(openWriteFile)
#     -When Leo renames the file(replaceTargetFileIfDifferent).
#@-doc
#@nonl
#@+node:ekr.20060715100156.72:atFile.replaceTargetFileIfDifferent
original_replaceTargetFileIfDifferent = leoAtFile.atFile.replaceTargetFileIfDifferent

def replaceTargetFileIfDifferent (self):

    # Check if we are dealing with a shadow file
    try:
        c = self.c
        targetFileName = self.targetFileName 
        outputFileName = self.outputFileName
        shadow_subdir = c.config.getString('shadow_subdir') or shadow_subdir_default
        shadow_verbosity = getVerbosity(c)
        if self.writing_to_shadow_directory:
            self.targetFileName = self.shadow_filename 
            self.outputFileName = self.shadow_filename+'.tmp'
        if original_replaceTargetFileIfDifferent(self):
            # Original_replaceTargetFileIfDifferent should be oblivious
            # to the existance of the shadow directory.
            if self.writing_to_shadow_directory:
                if shadow_verbosity >= 2:
                    g.es("Updating file from shadow folder %s" % shadow_subdir,color='orange')
                mod_shadow_core.copy_file_removing_sentinels(self.shadow_filename,targetFileName, marker_from_extension)

    finally:
        if self.writing_to_shadow_directory:
            assert self.targetFileName == self.shadow_filename 
            assert self.outputFileName == self.shadow_filename+'.tmp'
        else:
            assert self.targetFileName == targetFileName
            assert self.outputFileName == outputFileName
            # We need to check what's going on if the targetFileName or the outputFileName is changed.

        # Not sure if this finally clause is needed or not
        self.targetFileName = targetFileName
        self.outputFileName = outputFileName 
#@-node:ekr.20060715100156.72:atFile.replaceTargetFileIfDifferent
#@-node:ekr.20060715100156.71:writing
#@+node:ekr.20060715100156.73:massageComment
def massageComment (self,s):

    """Leo has no business changing comments!"""

    return s 
#@-node:ekr.20060715100156.73:massageComment
#@-node:ekr.20060715100156.68:Leo overwrites
#@+node:ekr.20060715100156.74:test_support
#@+node:ekr.20060715100156.75:do_test_propagate_changes_Leo
def do_test_propagate_changes_Leo(c):
    """
    Leo version of the test procedure.
    Gets the arguments from Leo nodes.
    """
    from leoTest import testUtils

    def get_node_lines(title):
        unicode_string = u.findNodeInTree(p, title).bodyString()
        return unicode_string.split("\n")
    try:
        p = c.currentPosition()
        u = testUtils(c)

        before_with_sentinels_lines = get_node_lines ("before with sentinels")
        changed_without_sentinels_lines = get_node_lines ("changed without sentinels")
        after_with_sentinel_lines = get_node_lines ("after with sentinels")

        sq = mod_shadow_core.sentinel_squasher(g.es, g.nullObject)
        mod_shadow_core.propagate_changes_test (c,
            before_with_sentinels_lines,
            changed_without_sentinels_lines,
            after_with_sentinel_lines,
            "#@", g.es, g.nullObject)
    finally:
        pass
#@nonl
#@-node:ekr.20060715100156.75:do_test_propagate_changes_Leo
#@-node:ekr.20060715100156.74:test_support
#@-others
#@nonl
#@-node:ekr.20060715100156.52:@thin mod_shadow.py
#@-leo
