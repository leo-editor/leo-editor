#@+leo-ver=4-thin
#@+node:ekr.20031218072017.3446:@thin leoTangle.py
#@@language python
#@@tabwidth -4
#@@pagewidth 70

# Tangle and Untangle.
import leo.core.leoGlobals as g
import os
import string

#@<< about Tangle and Untangle >>
#@+node:ekr.20031218072017.2411:<< About Tangle and Untangle >>
#@+at 
#@nonl
# The Tangle command translates the selected @root tree into one or 
# more well-formatted C source files. The outline should contain 
# directives, sections references and section definitions, as 
# described in Chapter 4. The Untangle command is essentially the 
# reverse of the Tangle command. The Tangle command creates a 
# derived file from an @root tree; the Untangle command incorporates 
# changes made to derived files back into the @root tree.
# 
# The Tangle command operates in two passes. The first pass 
# discovers the complete definitions of all sections and places 
# these definitions in a symbol table. The first pass also makes a 
# list of root sections. Definitions can appear in any order, so we 
# must scan the entire input file to know whether any particular 
# definition has been completed.
# 
# Tangle's second pass creates one file for each @root node. Tangle 
# rescans each section in the list of roots, copying the root text 
# to the output and replacing each section reference by the 
# section's definition. This is a recursive process because any 
# definition may contain other references. We can not allow a 
# section to be defined in terms of itself, either directly or 
# indirectly. We check for such illegally recursive definitions in 
# pass 2 using the section stack class.  Tangle indicates where 
# sections begin and end using comment lines called sentinel lines.  
# The this part of the appendix discusses the format of the 
# sentinels output by the Tangle command.
# 
# The key design principle of the Tangle command is this: Tangle 
# must output newlines in a context-free manner. That is, Tangle 
# must never output conditional newlines, either directly or 
# indirectly. Without this rule Untangle could not determine whether 
# to skip or copy newlines.
# 
# The Tangle command increases the indentation level of a section 
# expansion the minimum necessary to align the section expansion 
# with the surrounding code. In essence, this scheme aligns all 
# section expansions with the line of code in which the reference to 
# the section occurs. In some cases, several nested sections 
# expansions will have the same indentation level. This can occur, 
# for example, when a section reference in an outline occurs at the 
# left margin of the outline.
# 
# This scheme is probably better than more obvious schemes that 
# indent more "consistently." Such schemes would produce too much 
# indentation for deeply nested outlines. The present scheme is 
# clear enough and avoids indentation wherever possible, yet indents 
# sections adequately. End sentinel lines make this scheme work by 
# making clear where the expansion of one section ends and the 
# expansion of a containing section resumes.
# 
# Tangle increases indentation if the section reference does not 
# start a line. Untangle is aware of this hack and adjusts 
# accordingly. This extra indentation handles several common code 
# idioms, which otherwise would create under-indented code. In 
# short, Tangle produces highly readable, given the necessity of 
# preserving newlines for Untangle.
# 
# Untangle is inherently complex.  It must do a perfect job of 
# updating the outline, especially whitespace, from expansions of 
# section definitions created by the Tangle command.  Such 
# expansions need not be identical because they may have been 
# generated at different levels of indentation.  The Untangle 
# command can not assume that all expansions of a section will be 
# identical in the derived file; within the derived file, the 
# programmer may have made incompatible changes to two different 
# expansions of the same section. Untangle must check to see that 
# all expansions of a section are "equivalent".  As an added 
# complication, derived files do not contain all the information 
# found in @root trees.  @root trees may contain headlines that 
# generate no code at all.  Also, an outline may define a section in 
# several ways: with an @c or @code directive or with a section 
# definition line.  To be useful, Untangle must handle all these 
# complications flawlessly. The appendix discusses the various 
# conventions used in the sentinels output by the Tangle command.  
# These conventions allow the Untangle command to recreate 
# whitespace correctly.
# 
# Untangle operates in two passes. The first pass finds definitions 
# in the derived file and enters them into the Untangle Symbol 
# Table, or UST.   Definitions often include references to other 
# sections, so definitions often include nested definitions of 
# referenced sections. The first pass of Untangle uses a definition 
# stack to keep track of nested definitions. The top of the stack 
# represents the definition following the latest reference, except 
# for the very first entry pushed on the stack, which represents the 
# code in the outline that contains the @root directive. The stack 
# never becomes empty because of the entry for the @root section. 
# All definitions of a section should match--otherwise there is an 
# inconsistent definition. This pass uses a forgiving compare 
# routine that ignores differences that do not affect the meaning of 
# a program.
# 
# Untangle's second pass enters definitions from the outline into 
# the Tangle Symbol Table, or TST. The second pass simultaneously 
# updates all sections in the outline whose definition in the TST 
# does not match the definition in the UST.  The central coding 
# insight of the Untangle command is that the second pass of 
# Untangle is almost identical to the first pass of Tangle! That is, 
# Tangle and Untangle share key parts of code, namely the 
# skip_body() method and its allies.  Just when skip_body() enters a 
# definition into the symbol table, all the information is present 
# that Untangle needs to update that definition.
#@-at
#@-node:ekr.20031218072017.2411:<< About Tangle and Untangle >>
#@nl
#@<< constants >>
#@+node:ekr.20031218072017.3447:<< constants >>
max_errors = 20

# All these must be defined together, because they form a single enumeration.
# Some of these are used by utility functions.

# Used by token_type().
plain_line = 1 # all other lines
at_at      = 2 # double-at sign.
at_chapter = 3 # @chapter
# at_c     = 4 # @c in noweb mode
at_code    = 5 # @code, or @c or @p in CWEB mode.
at_doc     = 6 # @doc
at_other   = 7 # all other @directives
at_root    = 8 # @root or noweb * sections
at_section = 9 # @section
# at_space = 10 # @space
at_web     = 11 # any CWEB control code, except at_at.

# Returned by self.skip_section_name() and allies and used by token_type.
bad_section_name = 12  # < < with no matching > >
section_ref  = 13  # < < name > >
section_def  = 14  # < < name > > =

# Returned by is_sentinal_line.
non_sentinel_line   = 15
start_sentinel_line = 16
end_sentinel_line   = 17

# Stephen P. Schaefer 9/13/2002
# add support for @first
at_last    = 18
#@-node:ekr.20031218072017.3447:<< constants >>
#@nl

#@+others
#@+node:ekr.20031218072017.3448:node classes
#@+node:ekr.20031218072017.3449:class tst_node
class tst_node:
    #@    @+others
    #@+node:ekr.20031218072017.3450:tst_node.__init__
    def __init__ (self,name,root_flag):

        # g.trace("tst_node.__init__",name)
        self.name = name
        self.is_root = root_flag
        self.referenced = False
        self.parts = []
    #@-node:ekr.20031218072017.3450:tst_node.__init__
    #@+node:ekr.20031218072017.3451:tst_node.__repr__
    def __repr__ (self):

        return "tst_node:" + self.name
    #@-node:ekr.20031218072017.3451:tst_node.__repr__
    #@-others
#@-node:ekr.20031218072017.3449:class tst_node
#@+node:ekr.20031218072017.3452:class part_node
class part_node:
    #@    @+others
    #@+node:ekr.20031218072017.3453:part_node.__init__
    def __init__ (self,name,code,doc,is_root,is_dirty):

        # g.trace("part_node.__init__",name)
        self.name = name # Section or file name.
        self.code = code # The code text.
        self.doc = doc # The doc text.
        self.is_dirty = is_dirty # True: vnode for body text is dirty.
        self.is_root = is_root # True: name is a root name.
    #@-node:ekr.20031218072017.3453:part_node.__init__
    #@+node:ekr.20031218072017.3454:part_node.__repr__
    def __repr__ (self):

        return "part_node:" + self.name
    #@-node:ekr.20031218072017.3454:part_node.__repr__
    #@-others
#@-node:ekr.20031218072017.3452:class part_node
#@+node:ekr.20031218072017.3455:class ust_node
class ust_node:
    #@    @+others
    #@+node:ekr.20031218072017.3456:ust_node.__init__
    #@+at 
    #@nonl
    # The text has been masssaged so that 1) it contains no leading 
    # indentation and 2) all code arising from section references 
    # have been replaced by the reference line itself.  Text for all 
    # copies of the same part can differ only in non-critical white 
    # space.
    #@-at
    #@@c

    def __init__ (self,name,code,part,of,nl_flag,update_flag):

        # g.trace("ust_node.__init__",name,part)
        self.name = name # section name
        self.parts = {} # parts dict
        self.code = code # code text
        self.part = part # n in "(part n of m)" or zero.
        self.of = of  # m in "(part n of m)" or zero.
        self.nl_flag = nl_flag  # True: section starts with a newline.
        self.update_flag = update_flag # True: section corresponds to a section in the outline.
    #@-node:ekr.20031218072017.3456:ust_node.__init__
    #@+node:ekr.20031218072017.3457:ust_node.__repr__
    def __repr__ (self):

        return "ust_node:" + self.name
    #@-node:ekr.20031218072017.3457:ust_node.__repr__
    #@-others
#@-node:ekr.20031218072017.3455:class ust_node
#@+node:ekr.20031218072017.3458:class def_node
class def_node:
    #@    @+others
    #@+node:ekr.20031218072017.3459:def_node.__init__
    #@+at 
    #@nonl
    # The text has been masssaged so that 1) it contains no leading 
    # indentation and 2) all code arising from section references 
    # have been replaced by the reference line itself.  Text for all 
    # copies of the same part can differ only in non-critical white 
    # space.
    #@-at
    #@@c

    def __init__ (self,name,indent,part,of,nl_flag,code):

        if 0:
            g.trace("def_node.__init__:",
                "name:",name," part:",part," of:",of," indent:",indent)
        self.name = name
        self.indent = indent
        self.code = code
        if self.code == None: self.code = ""
        self.part = part
        self.of = of
        self.nl_flag = nl_flag
    #@-node:ekr.20031218072017.3459:def_node.__init__
    #@+node:ekr.20031218072017.3460:def_node.__repr__
    def __repr__ (self):

        return "def_node:" + self.name
    #@-node:ekr.20031218072017.3460:def_node.__repr__
    #@-others
#@-node:ekr.20031218072017.3458:class def_node
#@+node:ekr.20031218072017.3461:class root_attributes (Stephen P. Schaefer)
#@+at 
#@nonl
# Stephen P. Schaefer, 9/2/2002
# Collect the root node specific attributes in an
# easy-to-use container.
#@-at
#@@c

class root_attributes:
    #@    @+others
    #@+node:ekr.20031218072017.3462:root_attributes.__init__
    #@+at 
    #@nonl
    # Stephen P. Schaefer, 9/2/2002
    # Keep track of the attributes of a root node
    #@-at
    #@@c

    def __init__ (self, tangle_state):

        if 0:
            #@        << trace the state >>
            #@+node:ekr.20031218072017.3463:<< trace the state >>
            try:
                if tangle_state.path: pass
            except AttributeError:
                tangle_state.path = None

            g.trace("def_root_attribute.__init__",
                "language:" + tangle_state.language +
                ", single_comment_string: " + tangle_state.single_comment_string +
                ", start_comment_string: " + tangle_state.start_comment_string +
                ", end_comment_string: " + tangle_state.end_comment_string +
                ", use_header_flag: " + repr(tangle_state.use_header_flag) +
                ", print_mode: " + tangle_state.print_mode +
                ", path: " + repr(tangle_state.path) +
                ", page_width: " + repr(tangle_state.page_width) +
                ", tab_width: " + repr(tangle_state.tab_width) +
                # Stephen P. Schaefer 9/13/2002
                ", first_lines: " + tangle_state.first_lines)
            #@-node:ekr.20031218072017.3463:<< trace the state >>
            #@nl
        self.language = tangle_state.language
        self.single_comment_string = tangle_state.single_comment_string
        self.start_comment_string = tangle_state.start_comment_string
        self.end_comment_string = tangle_state.end_comment_string
        self.use_header_flag = tangle_state.use_header_flag
        self.print_mode = tangle_state.print_mode

        # of all the state variables, this one isn't set in tangleCommands.__init__
        # peculiar
        try:
            self.path = tangle_state.path
        except AttributeError:
            self.path = None

        self.page_width = tangle_state.page_width
        self.tab_width = tangle_state.tab_width
        self.first_lines = tangle_state.first_lines # Stephen P. Schaefer 9/13/2002
    #@-node:ekr.20031218072017.3462:root_attributes.__init__
    #@+node:ekr.20031218072017.3464:root_attributes.__repr__
    def __repr__ (self):

        return ("root_attributes: language: " + self.language +
            ", single_comment_string: " + self.single_comment_string +
            ", start_comment_string: " + self.start_comment_string +
            ", end_comment_string: " + self.end_comment_string +
            ", use_header_flag: " + repr(self.use_header_flag) +
            ", print_mode: " + self.print_mode +
            ", path: " + self.path +
            ", page_width: " + repr(self.page_width) +
            ", tab_width: " + repr(self.tab_width) +
            # Stephen P. Schaefer 9/13/2002
            ", first_lines: " + self.first_lines)
    #@-node:ekr.20031218072017.3464:root_attributes.__repr__
    #@-others
#@-node:ekr.20031218072017.3461:class root_attributes (Stephen P. Schaefer)
#@-node:ekr.20031218072017.3448:node classes
#@+node:ekr.20031218072017.3465:class tangleCommands methods
class baseTangleCommands:
    """The base class for Leo's tangle and untangle commands."""
    #@    @+others
    #@+node:ekr.20031218072017.3466:tangle.__init__
    def __init__ (self,c):

        self.c = c
        self.init_ivars()
    #@-node:ekr.20031218072017.3466:tangle.__init__
    #@+node:ekr.20031218072017.1356:tangle.init_ivars & init_directive_ivars
    # Called by __init__

    def init_ivars(self):

        c = self.c
        g.app.scanErrors = 0
        #@    << init tangle ivars >>
        #@+node:ekr.20031218072017.1357:<< init tangle ivars >>
        # Various flags and counts...

        self.errors = 0 # The number of errors seen.
        self.tangling = True # True if tangling, False if untangling.
        self.path_warning_given = False # True: suppress duplicate warnings.
        self.tangle_indent = 0 # Level of indentation during pass 2, in spaces.
        if c.frame:
            self.file_name = c.mFileName # The file name (was a bridge function)
        else:
            self.file_name = "<unknown file name>"
        self.p = None # position being processed.
        self.output_file = None # The file descriptor of the output file.
        self.start_mode = "doc" # "code" or "doc".  Use "doc" for compatibility.
        self.tangle_output = {} # For unit testing.

        #@+at 
        #@nonl
        # Symbol tables: the TST (Tangle Symbol Table) contains all 
        # section names in the outline.
        # The UST (Untangle Symbol Table) contains all sections 
        # defined in the derived file.
        #@-at
        #@@c
        self.tst = {}
        self.ust = {}

        # The section stack for Tangle and the definition stack for Untangle.
        self.section_stack = []
        self.def_stack = []

        #@+at 
        #@nonl
        # The list of all roots. The symbol table routines add roots 
        # to self list during pass 1. Pass 2 uses self list to 
        # generate code for all roots.
        #@-at
        #@@c
        self.root_list = []

        # The delimiters for comments created by the @comment directive.
        self.single_comment_string = "//"  # present comment delimiters.
        self.start_comment_string = "/*"
        self.end_comment_string = "*/"
        self.sentinel = None

        # g.trace(self.single_comment_string)

        # The filename following @root in a headline.
        # The code that checks for < < * > > = uses these globals.
        self.root = None
        self.root_name = None

        # Formerly the "tangle private globals"
        # These save state during tangling and untangling.
        # It is possible that these will be removed...
        if 1:
            self.head_root = None
            self.code = None
            self.doc = None
            self.header_name = None
            self.header = None
            self.section_name = None

        #@+at 
        #@nonl
        # The following records whether we have seen an @code 
        # directive in a body text.
        # If so, an @code represents < < header name > > = and it is 
        # valid to continue a section definition.
        #@-at
        #@@c
        self.code_seen = False # True if @code seen in body text.

        # Support of output_newline option
        self.output_newline = g.getOutputNewline(c=c)
        #@-node:ekr.20031218072017.1357:<< init tangle ivars >>
        #@nl
        #@    << init untangle ivars >>
        #@+node:ekr.20031218072017.1358:<< init untangle ivars >>
        #@+at 
        #@nonl
        # Untangle vars used while comparing.
        #@-at
        #@@c
        self.line_comment = self.comment = self.comment_end = None
        self.comment2 = self.comment2_end = None
        self.string1 = self.string2 = self.verbatim = None
        self.message = None # forgiving compare message.
        #@-node:ekr.20031218072017.1358:<< init untangle ivars >>
        #@nl

    # Called by scanAllDirectives

    def init_directive_ivars (self):

        c = self.c
        #@    << init directive ivars >>
        #@+node:ekr.20031218072017.1359:<< init directive ivars >> (tangle)
        # Global options
        self.page_width = c.page_width
        self.tab_width = c.tab_width

        # New in Leo 4.5: get these from settings.
        self.output_doc_flag = c.config.getBool('output_doc_flag')
        self.tangle_batch_flag = c.config.getBool('tangle_batch_flag')
        self.untangle_batch_flag = c.config.getBool('untangle_batch_flag')
        self.use_header_flag = c.config.getBool('use_header_flag')

        # Default tangle options.
        self.tangle_directory = None # Initialized by scanAllDirectives

        # Default tangle language
        if c.target_language: c.target_language = c.target_language.lower()
        self.language = c.target_language
        delim1,delim2,delim3 = g.set_delims_from_language(self.language)
        # g.trace(delim1,delim2,delim3)

        # 8/1/02: this now works as expected.
        self.single_comment_string = delim1
        self.start_comment_string = delim2
        self.end_comment_string = delim3

        # g.trace(self.single_comment_string)

        # Abbreviations for self.language.
        # Warning: these must also be initialized in tangle.scanAllDirectives.
        if 1: # 10/30/02: Don't change the code, just ignore @language cweb.
            self.use_cweb_flag = False
            self.raw_cweb_flag = self.language == "cweb" # A new ivar.
        else:
            self.use_cweb_flag = self.language == "cweb"
            self.raw_cweb_flag = False # was never used before.

        self.use_noweb_flag = not self.use_cweb_flag

        # Set only from directives.
        self.print_mode = "verbose"

        # Stephen P. Schaefer 9/13/2002
        # support @first directive
        self.first_lines = ""
        self.encoding = c.config.default_derived_file_encoding # 2/21/03
        self.output_newline = g.getOutputNewline(c=c) # 4/24/03: initialize from config settings.
        #@-node:ekr.20031218072017.1359:<< init directive ivars >> (tangle)
        #@nl
    #@-node:ekr.20031218072017.1356:tangle.init_ivars & init_directive_ivars
    #@+node:ekr.20031218072017.3467:top level
    #@+at 
    #@nonl
    # Only top-level drivers initialize ivars.
    #@-at
    #@+node:ekr.20031218072017.3468:cleanup
    # This code is called from tangleTree and untangleTree.

    def cleanup (self):

        c = self.c

        if self.errors + g.app.scanErrors == 0:
            #@        << call tangle_done.run() or untangle_done.run() >>
            #@+node:ekr.20031218072017.3469:<< call tangle_done.run() or untangle_done.run() >>
            # Create a list of root names:
            root_names = []
            theDir = self.tangle_directory # Bug fix: 12/04/02
            if not theDir: theDir = ""
            for section in self.root_list:
                for part in section.parts:
                    if part.is_root:
                        root_names.append(c.os_path_finalize_join(theDir,part.name))

            if self.tangling and self.tangle_batch_flag:
                try:
                    import tangle_done
                    tangle_done.run(root_names)
                except:
                    g.es("can not execute","tangle_done.run()")
                    g.es_exception()
            if not self.tangling and self.untangle_batch_flag:
                try:
                    import untangle_done
                    untangle_done.run(root_names)
                except:
                    g.es("can not execute","tangle_done.run()")
                    g.es_exception()
            #@-node:ekr.20031218072017.3469:<< call tangle_done.run() or untangle_done.run() >>
            #@nl

        # Reinitialize the symbol tables and lists.
        self.tst = {}
        self.ust = {}
        self.root_list = []
        self.def_stack = []
    #@-node:ekr.20031218072017.3468:cleanup
    #@+node:ekr.20031218072017.3470:initTangleCommand
    def initTangleCommand (self):

        c = self.c
        c.endEditing()

        if not g.unitTesting:
            g.es("tangling...")
        self.init_ivars()
        self.tangling = True
    #@-node:ekr.20031218072017.3470:initTangleCommand
    #@+node:ekr.20031218072017.3471:initUntangleCommand
    def initUntangleCommand (self):

        c = self.c
        c.endEditing()

        g.es("untangling...")
        self.init_ivars()
        self.tangling = False
    #@-node:ekr.20031218072017.3471:initUntangleCommand
    #@+node:ekr.20031218072017.3472:tangle
    def tangle(self,event=None,p=None):

        c = self.c
        if not p: p = c.p
        self.initTangleCommand()

        # Paul Paterson's patch.
        if not self.tangleTree(p,report_errors=True):
            g.es("looking for a parent to tangle...")
            while p:
                assert(self.head_root == None)
                d = g.get_directives_dict(p,[self.head_root])
                if 'root' in d:
                    g.es("tangling parent")
                    self.tangleTree(p,report_errors=True)
                    break
                p.moveToParent()

        if not g.unitTesting:
            g.es("tangle complete")
    #@-node:ekr.20031218072017.3472:tangle
    #@+node:ekr.20031218072017.3473:tangleAll
    def tangleAll(self,event=None):

        c = self.c
        self.initTangleCommand()
        has_roots = False

        for p in c.rootPosition().self_and_siblings():
            ok = self.tangleTree(p,report_errors=False)
            if ok: has_roots = True
            if self.path_warning_given:
                break # Fatal error.

        self.errors += g.app.scanErrors

        if not has_roots:
            self.warning("----- the outline contains no roots")
        elif self.errors > 0 and not self.path_warning_given:
            self.warning("----- tangle halted because of errors")
        else:
            if not g.unitTesting:
                g.es("tangle complete")
    #@-node:ekr.20031218072017.3473:tangleAll
    #@+node:ekr.20031218072017.3474:tangleMarked
    def tangleMarked(self,event=None):

        c = self.c ; p = c.rootPosition()
        c.clearAllVisited() # No roots have been tangled yet.
        self.initTangleCommand()
        any_marked = False
        while p:
            is_ignore, i = g.is_special(p.b,0,"@ignore")
            # Only tangle marked and unvisited nodes.
            if is_ignore:
                p.moveToNodeAfterTree()
            elif p.isMarked():
                ok = self.tangleTree(p,report_errors=False)
                if ok: any_marked = True
                if self.path_warning_given:
                    break # Fatal error.
                p.moveToNodeAfterTree()
            else: p.moveToThreadNext()

        self.errors += g.app.scanErrors

        if not any_marked:
            self.warning("----- The outline contains no marked roots")
        elif self.errors > 0 and not self.path_warning_given:
            self.warning("----- Tangle halted because of errors")
        else:
            if not g.unitTesting:
                g.es("tangle complete")
    #@-node:ekr.20031218072017.3474:tangleMarked
    #@+node:ekr.20031218072017.3475:tanglePass1
    # Traverses the tree whose root is given, handling each headline and associated body text.

    def tanglePass1(self,p):

        """The main routine of tangle pass 1"""

        p = p.copy()
        next = p.nodeAfterTree()
        while p and p != next:
            self.p = p
            self.setRootFromHeadline(p)
            assert(self.head_root == None)
            theDict = g.get_directives_dict(p,[self.head_root])
            is_ignore = 'ignore' in theDict
            if is_ignore:
                p.moveToNodeAfterTree()
                continue
            # This must be called after root_name has been set.
            if self.tangling:
                self.scanAllDirectives(p) # calls init_directive_ivars.
            # Scan the headline and body text.
            self.skip_headline(p)
            self.skip_body(p)
            p.moveToThreadNext()
            if self.errors + g.app.scanErrors >= max_errors:
                self.warning("----- Halting Tangle: too many errors")
                break

        if self.tangling:
            self.st_check()
            # g.trace(self.st_dump(verbose_flag=True))
    #@-node:ekr.20031218072017.3475:tanglePass1
    #@+node:ekr.20031218072017.3476:tanglePass2
    # At this point p is the root of the tree that has been tangled.

    def tanglePass2(self):

        self.p = None # self.p is not valid in pass 2.

        self.errors += g.app.scanErrors

        if self.errors > 0:
            self.warning("----- No file written because of errors")
        elif self.root_list == None:
            self.warning("----- The outline contains no roots")
        else:
            self.put_all_roots() # pass 2 top level function.
    #@-node:ekr.20031218072017.3476:tanglePass2
    #@+node:ekr.20031218072017.3477:tangleTree (calls cleanup)
    # This function is called only from the top level, so there is no need to initialize globals.

    def tangleTree(self,p,report_errors):

        """Tangles all nodes in the tree whose root is p.

        Reports on its results if report_errors is True."""

        p = p.copy() # 9/14/04
        assert(p)
        any_root_flag = False
        next = p.nodeAfterTree()
        self.path_warning_given = False

        while p and p != next:
            self.setRootFromHeadline(p)
            assert(self.head_root == None)
            theDict = g.get_directives_dict(p,[self.head_root])
            is_ignore = 'ignore' in theDict
            is_root = 'root' in theDict
            is_unit = 'unit' in theDict
            if is_ignore:
                p.moveToNodeAfterTree()
            elif not is_root and not is_unit:
                p.moveToThreadNext()
            else:
                self.tanglePass1(p) # sets self.p
                if self.root_list and self.tangling:
                    any_root_flag = True
                    self.tanglePass2() # self.p invalid in pass 2.
                self.cleanup()
                p.moveToNodeAfterTree()
                if self.path_warning_given: break # Fatal error.

        if self.tangling and report_errors and not any_root_flag:
            # This is done by Untangle if we are untangling.
            self.warning("----- The outline contains no roots")
        return any_root_flag
    #@-node:ekr.20031218072017.3477:tangleTree (calls cleanup)
    #@+node:ekr.20031218072017.3478:untangle
    def untangle(self,event=None,p=None):

        c = self.c
        if p == None:
            p = c.p
        self.initUntangleCommand()

        #@    << read fake files for unit testing >>
        #@+node:sps.20100608083657.20940:<< read fake files for unit testing >>
        if g.unitTesting:
            p2 = p.copy()
            while (p2.hasNext()):
                p2.moveToNext()
                self.tangle_output[p2.h] = p2.b
        #@-node:sps.20100608083657.20940:<< read fake files for unit testing >>
        #@nl

        self.untangleTree(p,report_errors=True)
        if not g.unitTesting:
            g.es("untangle complete")
        c.redraw()
    #@-node:ekr.20031218072017.3478:untangle
    #@+node:ekr.20031218072017.3479:untangleAll
    def untangleAll(self,event=None):

        c = self.c
        self.initUntangleCommand()
        has_roots = False

        for p in c.rootPosition().self_and_siblings():
            ok = self.untangleTree(p,False)
            if ok: has_roots = True
        c.redraw()

        self.errors += g.app.scanErrors

        if not has_roots:
            self.warning("----- the outline contains no roots")
        elif self.errors > 0:
            self.warning("----- untangle command halted because of errors")
        else:
            if not g.unitTesting:
                g.es("untangle complete")
    #@-node:ekr.20031218072017.3479:untangleAll
    #@+node:ekr.20031218072017.3480:untangleMarked
    def untangleMarked(self,event=None):

        c = self.c ; p = c.rootPosition()
        self.initUntangleCommand()
        marked_flag = False

        while p: # Don't use an iterator.
            if p.isMarked():
                ok = self.untangleTree(p,report_errors=False)
                if ok: marked_flag = True
                if self.errors + g.app.scanErrors > 0: break
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
        c.redraw()

        self.errors += g.app.scanErrors

        if not marked_flag:
            self.warning("----- the outline contains no marked roots")
        elif self.errors > 0:
            self.warning("----- untangle command halted because of errors")
        else:
            if not g.unitTesting:
                g.es("untangle complete")
    #@-node:ekr.20031218072017.3480:untangleMarked
    #@+node:ekr.20031218072017.3481:untangleRoot (calls cleanup)
    #@+at 
    #@nonl
    # This method untangles the derived files in a vnode known to 
    # contain at least one @root directive. The work is done in two 
    # passes. The first pass creates the UST by scanning the derived 
    # file. The second pass updates the outline using the UST and a 
    # TST that is created during the pass.
    # 
    # We assume that all sections from root to end are contained in 
    # the derived file, and we attempt to update all such sections. 
    # The begin/end params indicate the range of nodes to be scanned 
    # when building the TST.
    #@-at
    #@@c

    def untangleRoot(self,root,begin,end):

        # g.trace("root,begin,end:",root,begin,end)
        c = self.c
        #@    << Set path & root_name to the file specified in the @root directive >>
        #@+node:ekr.20031218072017.3483:<< Set path & root_name to the file specified in the @root directive >>
        s = root.b
        i = 0
        while i < len(s):
            code, junk = self.token_type(s,i,report_errors=True)
            if code == at_root:
                # token_type sets root_name unless there is a syntax error.
                if self.root_name: path = self.root_name
                break
            else: i = g.skip_line(s,i)

        if not self.root_name:
            # A bad @root command.  token_type has already given an error.
            self.cleanup()
            return
        #@-node:ekr.20031218072017.3483:<< Set path & root_name to the file specified in the @root directive >>
        #@nl
        #@    << return if @silent or unknown language >>
        #@+node:ekr.20031218072017.3482:<< return if @silent or unknown language >>
        if self.language == "unknown":
            g.es("@comment disables untangle for",path, color="blue")
            return

        if self.print_mode in ("quiet","silent"):
            g.es('','@%s' % (self.print_mode),"inhibits untangle for",path, color="blue")
            return
        #@-node:ekr.20031218072017.3482:<< return if @silent or unknown language >>
        #@nl
        path = c.os_path_finalize_join(self.tangle_directory,path)
        if g.unitTesting:
            #@        << fake the file access >>
            #@+node:sps.20100608083657.20939:<< fake the file access >>
            # complications to handle testing of multiple @root directives together with
            # @path directives
            file_name_path = c.os_path_finalize_join(self.tangle_directory,path)
            if (file_name_path.find(c.openDirectory) == 0):
                relative_path = file_name_path[len(c.openDirectory):]
                # don't confuse /u and /usr as having common prefixes
                if (relative_path[:len(os.sep)] == os.sep):
                    file_name_path = relative_path[len(os.sep):]
            # find the node with the right title, and load self.tangle_output and file_buf

            file_buf = self.tangle_output.get(file_name_path)
            #@-node:sps.20100608083657.20939:<< fake the file access >>
            #@nl
        else:
            file_buf,e = g.readFileIntoString(path)
        if file_buf is None:
            self.cleanup()
            return
        else:
            file_buf = file_buf.replace('\r','')

        g.es('','@root ' + path)
        # Pass 1: Scan the C file, creating the UST
        self.scan_derived_file(file_buf)
        # g.trace(self.ust_dump())
        if self.errors + g.app.scanErrors == 0:
            #@        << Pass 2: Untangle the outline using the UST and a newly-created TST >>
            #@+node:ekr.20031218072017.3485:<< Pass 2:  Untangle the outline using the UST and a newly-created TST >>
            #@+at
            # This code untangles the root and all its siblings. We 
            # don't call tangleTree here
            # because we must handle all siblings. tanglePass1 
            # handles an entire tree. It also
            # handles @ignore.
            #@-at
            #@@c

            p = begin
            while p and p != end: # Don't use iterator.
                self.tanglePass1(p)
                if self.errors + g.app.scanErrors != 0:
                    break
                p.moveToNodeAfterTree()

            self.ust_warn_about_orphans()
            #@-node:ekr.20031218072017.3485:<< Pass 2:  Untangle the outline using the UST and a newly-created TST >>
            #@nl
        self.cleanup()
    #@-node:ekr.20031218072017.3481:untangleRoot (calls cleanup)
    #@+node:ekr.20031218072017.3486:untangleTree
    # This funtion is called when the user selects any "Untangle" command.

    def untangleTree(self,p,report_errors):

        p = p.copy() # 9/14/04
        c = self.c
        any_root_flag = False
        afterEntireTree = p.nodeAfterTree()
        # Initialize these globals here: they can't be cleared later.
        self.head_root = None
        self.errors = 0 ; g.app.scanErrors = 0
        c.clearAllVisited() # Used by untangle code.

        while p and p != afterEntireTree and self.errors + g.app.scanErrors == 0:
            self.setRootFromHeadline(p)
            assert(self.head_root == None)
            theDict = g.get_directives_dict(p,[self.head_root])
            ignore = 'ignore' in theDict
            root = 'root' in theDict
            unit = 'unit' in theDict
            if ignore:
                p.moveToNodeAfterTree()
            elif unit:
                # Expand the context to the @unit directive.
                unitNode = p   # 9/27/99
                afterUnit = p.nodeAfterTree()
                p.moveToThreadNext()
                while p and p != afterUnit and self.errors + g.app.scanErrors== 0:
                    self.setRootFromHeadline(p)
                    assert(self.head_root == None)
                    theDict = g.get_directives_dict(p,[self.head_root])
                    root = 'root' in theDict
                    if root:
                        any_root_flag = True
                        end = None
                        #@                    << set end to the next root in the unit >>
                        #@+node:ekr.20031218072017.3487:<< set end to the next root in the unit >>
                        #@+at 
                        #@nonl
                        # The untangle_root function will untangle 
                        # an entire tree by calling untangleTree, so 
                        # the following code ensures that the next 
                        # @root node will not be an offspring of p.
                        #@-at
                        #@@c

                        end = p.threadNext()
                        while end and end != afterUnit:
                            flag, i = g.is_special(end.b,0,"@root")
                            if flag and not p.isAncestorOf(end):
                                break
                            end.moveToThreadNext()
                        #@-node:ekr.20031218072017.3487:<< set end to the next root in the unit >>
                        #@nl
                        # g.trace("end:",end)
                        self.scanAllDirectives(p)
                        self.untangleRoot(p,unitNode,afterUnit)
                        p = end.copy()
                    else: p.moveToThreadNext()
            elif root:
                # Limit the range of the @root to its own tree.
                afterRoot = p.nodeAfterTree()
                any_root_flag = True
                self.scanAllDirectives(p)
                self.untangleRoot(p,p,afterRoot)
                p = afterRoot.copy()
            else:
                p.moveToThreadNext()

        self.errors += g.app.scanErrors

        if report_errors:
            if not any_root_flag:
                self.warning("----- The outline contains no roots")
            elif self.errors > 0:
                self.warning("----- Untangle command halted because of errors")
        return any_root_flag
    #@-node:ekr.20031218072017.3486:untangleTree
    #@-node:ekr.20031218072017.3467:top level
    #@+node:ekr.20031218072017.3488:tangle
    #@+node:ekr.20031218072017.3489:Pass 1
    #@+node:ekr.20031218072017.3490:handle_newline
    #@+at 
    #@nonl
    # This method handles newline processing while skipping a code 
    # section. It sets 'done' if the line contains an @directive or 
    # section definition that terminates the present code section. 
    # On entry: i should point to the first character of a line.  
    # This routine scans past a line only if it could not contain a 
    # section reference.
    # 
    # Returns (i, done)
    #@-at
    #@@c

    def handle_newline(self,s,i):

        j = i ; done = False
        kind, end = self.token_type(s,i,report_errors=False)
        # token_type will not skip whitespace in noweb mode.
        i = g.skip_ws(s,i)
        # g.trace(kind,g.get_line(s,i))

        if kind == plain_line:
            pass
        elif (kind == at_code or kind == at_doc or
            kind == at_root or kind == section_def):
            i = j ; done = True # Terminate this code section and rescan.
        elif kind == section_ref:
            # Enter the reference.
            ref = s[i:end]
            self.st_enter_section_name(ref,None,None)
        # DTHEIN 13-OCT-2002: @first directives are OK in code sections
        elif (kind == at_other) and g.match_word(s,j,"@first"):
            pass
        elif kind == at_other or kind == at_chapter or kind == at_section:
            # We expect to see only @doc,@c or @root directives
            # while scanning a code section.
            i = g.skip_to_end_of_line(s,i)
            if 0: # 12/03/02: no longer needed
                self.error("directive not valid here: " + s[j:i])
        elif kind == bad_section_name:
            if self.use_cweb_flag:
                i = g.skip_to_end_of_line(s,i)
        elif kind == at_web or kind == at_at:
            i += 2 # Skip a CWEB control code.
        else: assert(False)

        return i, done
    #@-node:ekr.20031218072017.3490:handle_newline
    #@+node:ekr.20031218072017.3491:skip_body
    # This method handles all the body text.

    def skip_body (self,p):

        # g.trace(p)
        c = self.c
        s = p.b
        code_seen = False ; code = doc = None ; i = 0
        anyChanged = False

        if self.start_mode == "code":
            j = g.skip_blank_lines(s,i)
            i,code = self.skip_code(s,j)
            if code:
                #@            << Define a section for a leading code part >>
                #@+node:ekr.20031218072017.3494:<< Define a section for a leading code part >>
                if self.header_name:
                    # Tangle code.
                    part = self.st_enter_section_name(
                        self.header_name,code,doc)
                    # Untangle code.
                    if not self.tangling: 
                        head = s[:j] ; tail = s[i:]
                        s,i,changed = self.update_def(self.header,part,head,code,tail)
                        if changed: anyChanged = True
                    code_seen = True
                    code = doc = None
                #@-node:ekr.20031218072017.3494:<< Define a section for a leading code part >>
                #@nl

        if not code:
            i,doc = self.skip_doc(s,i) # Start in doc section by default.
            if i >= len(s) and doc:
                #@            << Define a section containing only an @doc part >>
                #@+node:ekr.20031218072017.3493:<< Define a section containing only an @doc part >>
                #@+at 
                #@nonl
                # It's valid for an @doc directive to appear under a 
                # headline that does not contain a section name.  In 
                # that case, no section is defined.
                #@-at
                #@@c

                if self.header_name:
                    # Tangle code.
                    part = self.st_enter_section_name(self.header_name,code,doc)
                    # Untangle code.
                    if not self.tangling: 
                        # Untangle no longer updates doc parts.
                        # 12/03/02: Mark the part as having been updated to suppress warning.
                        junk,junk = self.ust_lookup(self.header_name,part,update_flag=True)

                doc = None
                #@-node:ekr.20031218072017.3493:<< Define a section containing only an @doc part >>
                #@nl

        while i < len(s):
            progress = i # progress indicator
            # line = g.get_line(s,i) ; g.trace(line)
            kind, end = self.token_type(s,i,report_errors=True)
            # if g.is_nl(s,i): i = g.skip_nl(s,i)
            i = g.skip_ws(s,i)
            if kind == section_def:
                #@            << Scan and define a section definition >>
                #@+node:ekr.20031218072017.3495:<< Scan and define a section definition >>
                # We enter the code part and any preceding doc part into the symbol table.

                # Skip the section definition line.
                k = i ; i, kind, junk = self.skip_section_name(s,i)
                section_name = s[k:i]
                # g.trace(section_name)
                assert(kind == section_def)
                i = g.skip_to_end_of_line(s,i)

                # Tangle code: enter the section name even if the code part is empty.
                j = g.skip_blank_lines(s,i)
                i, code = self.skip_code(s,j)
                part = self.st_enter_section_name(section_name,code,doc)

                if not self.tangling: # Untangle code.
                    head = s[:j] ; tail = s[i:]
                    s,i,changed = self.update_def(section_name,part,head,code,tail)
                    if changed: anyChanged = True

                code = doc = None
                #@-node:ekr.20031218072017.3495:<< Scan and define a section definition >>
                #@nl
            elif kind == at_code:
                if self.use_cweb_flag:
                    i += 2 # Skip the at-c or at-p
                else:
                    i = g.skip_line(s,i)
                #@            << Scan and define an @code defininition >>
                #@+node:ekr.20031218072017.3496:<< Scan and define an @code defininition >>
                # All @c or @code directives denote < < headline_name > > =
                if self.header_name:

                    # Tangle code.
                    j = g.skip_blank_lines(s,i)
                    i, code = self.skip_code(s,j)
                    part = self.st_enter_section_name(self.header_name,code,doc)
                    # Untangle code.
                    if not self.tangling: 
                        head = s[:j] ; tail = s[i:]
                        s,i,changed = self.update_def(self.header,part,head,code,tail)
                        if changed: anyChanged = True
                else:
                    self.error("@c expects the headline: " + self.header + " to contain a section name")

                code_seen = True
                code = doc = None
                #@-node:ekr.20031218072017.3496:<< Scan and define an @code defininition >>
                #@nl
            elif kind == at_root:
                i = g.skip_line(s,i)
                #@            << Scan and define a root section >>
                #@+node:ekr.20031218072017.3497:<< Scan and define a root section >>
                # We save the file name in case another @root ends the code section.
                old_root_name = self.root_name

                # Tangle code.
                j = g.skip_blank_lines(s,i)
                k, code = self.skip_code(s,j)

                # Stephen Schaefer, 9/2/02, later
                # st_enter_root_name relies on scanAllDirectives to have set
                # the root attributes, such as language, *_comment_string,
                # use_header_flag, etc.
                self.st_enter_root_name(old_root_name,code,doc)

                if not self.tangling: # Untangle code.
                    part = 1 # Use 1 for root part.
                    head = s[:j] ; tail = s[k:]
                    s,i,changed = self.update_def(old_root_name,part,head,code,tail,is_root_flag=True)
                    if changed: anyChanged = True

                code = doc = None
                #@-node:ekr.20031218072017.3497:<< Scan and define a root section >>
                #@nl
            elif kind == at_doc:
                if self.use_cweb_flag:
                    i += 2 # Skip the at-space
                else:
                    i = g.skip_line(s,i)
                i, doc = self.skip_doc(s,i)
            elif kind == at_chapter or kind == at_section:
                i = g.skip_line(s,i)
                i, doc = self.skip_doc(s,i)
            else:
                i = g.skip_line(s,i)
            assert(progress < i) # we must make progress!
        # Only call trimTrailingLines if we have changed its body.
        if anyChanged:
            c.trimTrailingLines(p)
    #@+node:ekr.20031218072017.3492:The interface between tangle and untangle
    #@+at 
    #@nonl
    # The following subsections contain the interface between the 
    # Tangle and Untangle commands.  This interface is an important 
    # hack, and allows Untangle to avoid duplicating the logic in 
    # skip_tree and its allies.
    # 
    # The aha is this: just at the time the Tangle command enters a 
    # definition into the symbol table, all the information is 
    # present that Untangle needs to update that definition.
    # 
    # To get whitespace exactly right we retain the outline's 
    # leading whitespace and remove leading whitespace from the 
    # updated definition.
    #@-at
    #@-node:ekr.20031218072017.3492:The interface between tangle and untangle
    #@-node:ekr.20031218072017.3491:skip_body
    #@+node:ekr.20031218072017.3498:skip_code
    #@+at 
    #@nonl
    # This method skips an entire code section. The caller is 
    # responsible for entering the completed section into the symbol 
    # table. On entry, i points at the line following the @directive 
    # or section definition that starts a code section. We skip code 
    # until we see the end of the body text or the next @ directive 
    # or section defintion that starts a code or doc part.
    #@-at
    #@@c

    def skip_code(self,s,i):

        # g.trace(g.get_line(s,i))
        code1 = i
        nl_i = i # For error messages
        done = False # True when end of code part seen.
        if self.use_noweb_flag:
            #@        << skip a noweb code section >>
            #@+node:ekr.20031218072017.3499:<< skip a noweb code section >>
            #@+at 
            #@nonl
            # This code handles the following escape conventions: 
            # double at-sign at the start of a line and at-<< and 
            # at.>.
            #@-at
            #@@c

            i, done = self.handle_newline(s,i)
            while not done and i < len(s):
                ch = s[i]
                if g.is_nl(s,i):
                    nl_i = i = g.skip_nl(s,i)
                    i, done = self.handle_newline(s,i)
                elif ch == '@' and (g.match(s,i+1,"<<") or # must be on different lines
                    g.match(s,i+1,">>")):
                    i += 3 # skip the noweb escape sequence.
                elif ch == '<':
                    #@        << handle possible noweb section reference >>
                    #@+node:ekr.20031218072017.3500:<< handle possible noweb section reference >>
                    j, kind, end = self.is_section_name(s,i)
                    if kind == section_def:
                        k = g.skip_to_end_of_line(s,i)
                        # We are in the middle of a line.
                        i += 1
                        self.error("chunk definition not valid here\n" + s[nl_i:k])
                    elif kind == bad_section_name:
                        i += 1 # This is not an error.  Just skip the '<'.
                    else:
                        assert(kind == section_ref)
                        # Enter the reference into the symbol table.
                        name = s[i:end]
                        self.st_enter_section_name(name,None,None)
                        i = end
                    #@-node:ekr.20031218072017.3500:<< handle possible noweb section reference >>
                    #@nl
                else: i += 1
            #@-node:ekr.20031218072017.3499:<< skip a noweb code section >>
            #@nl
        else:
            #@        << skip a CWEB code section >>
            #@+node:ekr.20031218072017.3501:<< skip a CWEB code section >>
            # This code is simple because CWEB control codes are valid anywhere.

            while not done and i < len(s):
                if s[i] == '@':
                    #@        << handle CWEB control code >>
                    #@+node:ekr.20031218072017.3502:<< handle CWEB control code >>
                    j, kind, end = self.is_section_name(s,i)

                    if kind == section_def:
                        done = True
                    elif kind == bad_section_name:
                        i += 2 # Any other control code.
                    else:
                        assert(kind == section_ref)
                        # Enter the reference into the symbol table.
                        name = s[i:j]
                        self.st_enter_section_name(name,None,None)
                        i = j
                    #@-node:ekr.20031218072017.3502:<< handle CWEB control code >>
                    #@nl
                else: i += 1
            #@-node:ekr.20031218072017.3501:<< skip a CWEB code section >>
            #@nl
        code = s[code1:i]
        # g.trace("returns:",code)
        return i,code
    #@-node:ekr.20031218072017.3498:skip_code
    #@+node:ekr.20031218072017.3503:skip_doc
    def skip_doc(self,s,i):

        # g.trace(g.get_line(s,i))
        # Skip @space, @*, @doc, @chapter and @section directives.
        doc1 = i
        while i < len(s):
            if g.is_nl(s,i):
                doc1 = i = g.skip_nl(s,i)
            elif g.match(s,i,"@ ") or g.match(s,i,"@\t") or g.match(s,i,"@*"):
                i = g.skip_ws(s,i+2) ; doc1 = i
            elif g.match(s,i,"@\n"):
                i += 1 ; doc1 = i
            elif (g.match_word(s,i,"@doc") or
                  g.match_word(s,i,"@chapter") or
                  g.match_word(s,i,"@section")):
                doc1 = i = g.skip_line(s,i)
            else: break

        while i < len(s):
            kind, end = self.token_type(s,i,report_errors=False)
            if kind == at_code or kind == at_root or kind == section_def:
                break
            i = g.skip_line(s,i)

        doc = s[doc1:i]
        # g.trace(doc)
        return i, doc
    #@-node:ekr.20031218072017.3503:skip_doc
    #@+node:ekr.20031218072017.3504:skip_headline
    #@+at 
    #@nonl
    # This function sets ivars that keep track of the indentation 
    # level. We also remember where the next line starts because it 
    # is assumed to be the first line of a documentation section.
    # 
    # A headline can contain a leading section name.  If it does, we 
    # substitute the section name if we see an @c directive in the 
    # body text.
    #@-at
    #@@c

    def skip_headline(self,p):

        self.header = s = p.h
        # Set self.header_name.
        j = i = g.skip_ws(s,0)
        i, kind, end = self.is_section_name(s,i)
        if kind == bad_section_name:
            self.header_name = None
        else:
            self.header_name = s[j:end]
    #@-node:ekr.20031218072017.3504:skip_headline
    #@-node:ekr.20031218072017.3489:Pass 1
    #@+node:ekr.20031218072017.3505:Pass 2
    #@+node:ekr.20031218072017.1488:oblank, oblanks, os, otab, otabs (Tangle)
    def oblank (self):
        self.oblanks(1)

    def oblanks (self,n):
        if abs(n) > 0:
            s = g.toEncodedString(' ' * abs(n),encoding=self.encoding)
            self.output_file.write(s)

    def onl(self):
        s = self.output_newline
        s = g.toEncodedString(s,self.encoding,reportErrors=True)
        self.output_file.write(s)

    def os (self,s):
        s = s.replace('\r','\n')
        s = g.toEncodedString(s,self.encoding,reportErrors=True)
        self.output_file.write(s)

    def otab (self):
        self.otabs(1)

    def otabs (self,n):
        if abs(n) > 0:
            s = g.toEncodedString('\t' * abs(n),self.encoding,reportErrors=True)
            self.output_file.write(s)
    #@-node:ekr.20031218072017.1488:oblank, oblanks, os, otab, otabs (Tangle)
    #@+node:ekr.20031218072017.1151:tangle.put_all_roots
    #@+at
    # This is the top level method of the second pass. It creates a 
    # separate C file
    # for each @root directive in the outline. The file is actually 
    # written only if
    # the new version of the file is different from the old 
    # version,or if the file did
    # not exist previously. If changed_only_flag FLAG is True only 
    # changed roots are
    # actually written.
    #@-at
    #@@c

    def put_all_roots(self):

        c = self.c ; outline_name = c.mFileName

        for section in self.root_list:

            # g.trace(section.name)
            file_name = c.os_path_finalize_join(self.tangle_directory,section.name)
            mode = c.config.output_newline
            textMode = mode == 'platform'
            if g.unitTesting:
                self.output_file = g.fileLikeObject()
                temp_name = 'temp-file'
            else:
                self.output_file,temp_name = g.create_temp_file(textMode=textMode)
            if not temp_name:
                g.es("can not create temp file")
                break
            #@        <<Get root specific attributes>>
            #@+node:ekr.20031218072017.1152:<<Get root specific attributes>>
            # Stephen Schaefer, 9/2/02
            # Retrieve the full complement of state for the root node
            self.language = section.root_attributes.language
            self.single_comment_string = section.root_attributes.single_comment_string
            self.start_comment_string = section.root_attributes.start_comment_string
            self.end_comment_string = section.root_attributes.end_comment_string
            self.use_header_flag = section.root_attributes.use_header_flag
            self.print_mode = section.root_attributes.print_mode
            self.path = section.root_attributes.path
            self.page_width = section.root_attributes.page_width
            self.tab_width = section.root_attributes.tab_width
            # Stephen P. Schaefer, 9/13/2002
            self.first_lines = section.root_attributes.first_lines

            # g.trace(self.single_comment_string)
            #@-node:ekr.20031218072017.1152:<<Get root specific attributes>>
            #@nl
            #@        <<Put @first lines>>
            #@+node:ekr.20031218072017.1153:<<Put @first lines>>
            # Stephen P. Schaefer 9/13/2002
            if self.first_lines:
                self.os(self.first_lines)
            #@-node:ekr.20031218072017.1153:<<Put @first lines>>
            #@nl
            if self.use_header_flag and self.print_mode == "verbose":
                #@            << Write a banner at the start of the output file >>
                #@+node:ekr.20031218072017.1154:<<Write a banner at the start of the output file>>
                if self.single_comment_string:
                    self.os(self.single_comment_string)
                    self.os(" Created by Leo from: ")
                    self.os(outline_name)
                    self.onl() ; self.onl()
                elif self.start_comment_string and self.end_comment_string:
                    self.os(self.start_comment_string)
                    self.os(" Created by Leo from: ")
                    self.os(outline_name)
                    self.oblank() ; self.os(self.end_comment_string)
                    self.onl() ; self.onl()
                #@-node:ekr.20031218072017.1154:<<Write a banner at the start of the output file>>
                #@nl
            for part in section.parts:
                if part.is_root:
                    self.tangle_indent = 0 # Initialize global.
                    self.put_part_node(part,False) # output first lws
            self.onl() # Make sure the file ends with a cr/lf
            #@        << unit testing fake files>>
            #@+node:sps.20100608083657.20937:<< unit testing fake files>>
            if g.unitTesting:
                # complications to handle testing of multiple @root directives together with
                # @path directives
                file_name_path = file_name
                if (file_name_path.find(c.openDirectory) == 0):
                    relative_path = file_name_path[len(c.openDirectory):]
                    # don't confuse /u and /usr as having common prefixes
                    if (relative_path[:len(os.sep)] == os.sep):
                         file_name_path = relative_path[len(os.sep):]
                self.tangle_output[file_name_path] = self.output_file.get()
            #@nonl
            #@-node:sps.20100608083657.20937:<< unit testing fake files>>
            #@nl
            self.output_file.close()
            self.output_file = None
            #@        << unit testing set result and return >>
            #@+node:sps.20100608083657.20938:<< unit testing set result and return >>
            if g.unitTesting:
                assert self.errors == 0
                g.app.unitTestDict ['tangle'] = True
                g.app.unitTestDict ['tangle_directory'] = self.tangle_directory
                if g.app.unitTestDict.get('tangle_output_fn'):
                    g.app.unitTestDict['tangle_output_fn'] += "\n" + file_name
                else:
                    g.app.unitTestDict ['tangle_output_fn'] = file_name
                continue
            #@-node:sps.20100608083657.20938:<< unit testing set result and return >>
            #@nl
            if self.errors + g.app.scanErrors == 0:
                g.update_file_if_changed(c,file_name,temp_name)
            else:
                g.es("unchanged:",file_name)
                #@            << Erase the temporary file >>
                #@+node:ekr.20031218072017.1155:<< Erase the temporary file >>
                try: # Just delete the temp file.
                    os.remove(temp_name)
                except: pass
                #@-node:ekr.20031218072017.1155:<< Erase the temporary file >>
                #@nl
    #@nonl
    #@-node:ekr.20031218072017.1151:tangle.put_all_roots
    #@+node:ekr.20031218072017.3506:put_code
    #@+at 
    #@nonl
    # This method outputs a code section, expanding section 
    # references by their definition. We should see no @directives 
    # or section definitions that would end the code section.
    # 
    # Most of the differences bewteen noweb mode and CWEB mode are 
    # handled by token_type(called from put_newline). Here, the only 
    # difference is that noweb handles double-@ signs only at the 
    # start of a line.
    #@-at
    #@@c

    def put_code(self,s,no_first_lws_flag):

        # g.trace(g.get_line(s,0))
        i = 0
        if i < len(s):
            i = self.put_newline(s,i,no_first_lws_flag)
            # Double @ is valid in both noweb and CWEB modes here.
            if g.match(s,i,"@@"):
                self.os('@') ; i += 2
        while i < len(s):
            progress = i
            ch = s[i]
            if (g.match(s,i,"<<") and self.use_noweb_flag or
                g.match(s,i,"@<") and self.use_cweb_flag):
                #@            << put possible section reference >>
                #@+node:ekr.20031218072017.3507:<<put possible section reference >>
                j, kind, name_end = self.is_section_name(s,i)
                if kind == section_def:
                    # We are in the middle of a code section
                    self.error(
                        "Should never happen:\n" +
                        "section definition while putting a section reference: " +
                        s[i:j])
                    i += 1
                elif kind == bad_section_name:
                    self.os(s[i]) ; i += 1 # This is not an error.
                else:
                    assert(kind == section_ref)
                    name = s[i:name_end]
                    self.put_section(s,i,name,name_end)
                    i = j
                #@-node:ekr.20031218072017.3507:<<put possible section reference >>
                #@nl
            elif ch == '@': # We are in the middle of a line.
                if self.use_cweb_flag:
                    #@                << handle 2-character CWEB control codes >>
                    #@+node:ekr.20031218072017.3508:<< handle 2-character CWEB control codes >>
                    if g.match(s,i,"@@"):
                        # Handle double @ sign.
                        self.os('@') ; i += 2
                    else:
                        i += 1 # skip the @.
                        if i+1 >= len(s) or g.is_ws_or_nl(s,i):
                            # A control code: at-backslash is not a valid CWEB control code.
                            # We are in CWEB mode, so we can output C block comments.
                            self.os("/*@" + s[i] + "*/") ; i += 1
                        else:
                            self.os("@") # The at sign is not part of a control code.
                    #@-node:ekr.20031218072017.3508:<< handle 2-character CWEB control codes >>
                    #@nl
                else:
                    #@                << handle noweb @ < < convention >>
                    #@+node:ekr.20031218072017.3509:<< handle noweb @ < < convention >>
                    #@+at 
                    #@nonl
                    # The user must ensure that neither @ < < nor @ 
                    # > > occurs in comments or strings. However, it 
                    # is valid for @ < < or @ > > to appear in the 
                    # doc chunk or in a single-line comment.
                    #@-at
                    #@@c

                    if g.match(s,i,"@<<"):
                        self.os("/*@*/<<") ; i += 3

                    elif g.match(s,i,"@>>"):
                        self.os("/*@*/>>") ; i += 3

                    else: self.os("@") ; i += 1
                    #@-node:ekr.20031218072017.3509:<< handle noweb @ < < convention >>
                    #@nl
            elif ch == '\r':
                i += 1
            elif ch == '\n':
                i += 1 ; self.onl()
                i = self.put_newline(s,i,False) # Put full lws
                if self.use_cweb_flag and g.match(s,i,"@@"):
                    self.os('@') ; i += 2
            else: self.os(s[i]) ; i += 1
            assert(progress < i)
    #@-node:ekr.20031218072017.3506:put_code
    #@+node:ekr.20031218072017.3510:put_doc
    # This method outputs a doc section within a block comment.

    def put_doc(self,s):

        # g.trace(g.get_line(s,0))
        width = self.page_width
        words = 0 ; word_width = 0 ; line_width = 0
        # 8/1/02: can't use choose here!
        if self.single_comment_string == None: single_w = 0
        else: single_w = len(self.single_comment_string)
        # Make sure we put at least 20 characters on a line.
        if width - max(0,self.tangle_indent) < 20:
            width = max(0,self.tangle_indent) + 20
        # Skip Initial white space in the doc part.
        i = g.skip_ws_and_nl(s,0)
        if i < len(s) and (self.print_mode == "verbose" or self.print_mode == "quiet"):
            use_block_comment = self.start_comment_string and self.end_comment_string
            use_single_comment = not use_block_comment and self.single_comment_string
            # javadoc_comment = use_block_comment and self.start_comment_string == "/**"
            if use_block_comment or use_single_comment:
                if 0: # The section name ends in an self.onl().
                    self.onl()
                self.put_leading_ws(self.tangle_indent)
                if use_block_comment:
                    self.os(self.start_comment_string)
                #@            << put the doc part >>
                #@+node:ekr.20031218072017.3511:<<put the doc part>>
                #@+at 
                #@nonl
                # This code fills and outputs each line of a doc 
                # part. It keeps track of whether the next word will 
                # fit on a line,and starts a new line if needed.
                #@-at
                #@@c

                if use_single_comment:
                    # New code: 5/31/00
                    self.os(self.single_comment_string) ; self.otab()
                    line_width =(single_w / abs(self.tab_width) + 1) * abs(self.tab_width)
                else:
                    line_width = abs(self.tab_width)
                    self.onl() ; self.otab()
                self.put_leading_ws(self.tangle_indent)
                line_width += max(0,self.tangle_indent)
                words = 0 ; word_width = 0
                while i < len(s):
                    #@    <<output or skip whitespace or newlines>>
                    #@+node:ekr.20031218072017.3512:<<output or skip whitespace or newlines>>
                    #@+at 
                    #@nonl
                    # This outputs whitespace if it fits, and 
                    # ignores it otherwise, and starts a new line if 
                    # a newline is seen. The effect of self code is 
                    # that we never start a line with whitespace 
                    # that was originally at the end of a line.
                    #@-at
                    #@@c

                    while g.is_ws_or_nl(s,i):
                        ch = s[i]
                        if ch == '\t':
                            pad = abs(self.tab_width) - (line_width % abs(self.tab_width))
                            line_width += pad
                            if line_width < width: self.otab()
                            i += 1
                        elif ch == ' ':
                            line_width += 1
                            if line_width < width: self.os(ch)
                            i += 1
                        else:
                            assert(g.is_nl(s,i))
                            self.onl()
                            if use_single_comment:
                                # New code: 5/31/00
                                self.os(self.single_comment_string) ; self.otab()
                                line_width = (single_w / abs(self.tab_width) + 1) * abs(self.tab_width)
                            else:
                                self.otab()
                                line_width = abs(self.tab_width)
                            i = g.skip_nl(s,i)
                            words = 0
                            self.put_leading_ws(self.tangle_indent)
                            # tangle_indent is in spaces.
                            line_width += max(0,self.tangle_indent)
                    #@-node:ekr.20031218072017.3512:<<output or skip whitespace or newlines>>
                    #@nl
                    if i >= len(s):
                        break
                    #@    <<compute the width of the next word>>
                    #@+node:ekr.20031218072017.3513:<<compute the width of the next word>>
                    j = i ; word_width = 0
                    while j < len(s) and not g.is_ws_or_nl(s,j):
                        word_width += 1
                        j += 1
                    #@-node:ekr.20031218072017.3513:<<compute the width of the next word>>
                    #@nl
                    if words == 0 or line_width + word_width < width:
                        words += 1
                        #@        <<output next word>>
                        #@+node:ekr.20031218072017.3514:<<output next word>>
                        while i < len(s) and not g.is_ws_or_nl(s,i):
                            self.os(s[i])
                            i += 1
                        #@-node:ekr.20031218072017.3514:<<output next word>>
                        #@nl
                        line_width += word_width
                    else:
                        # 11-SEP-2002 DTHEIN: Fixed linewrapping bug in
                        # tab-then-comment sequencing
                        self.onl()
                        if use_single_comment:
                            self.os(self.single_comment_string) ; self.otab()
                            line_width = (single_w / abs(self.tab_width) + 1) * abs(self.tab_width)
                        else:
                            self.otab()
                            line_width = abs(self.tab_width)
                        words = 0
                        self.put_leading_ws(self.tangle_indent)
                        # tangle_indent is in spaces.
                        line_width += max(0,self.tangle_indent)
                #@-node:ekr.20031218072017.3511:<<put the doc part>>
                #@nl
                self.onl()
                self.put_leading_ws(self.tangle_indent)
                if use_block_comment:
                    self.os(self.end_comment_string)
                self.onl()
            else: self.onl()
    #@-node:ekr.20031218072017.3510:put_doc
    #@+node:ekr.20031218072017.3515:put_leading_ws
    # Puts tabs and spaces corresponding to n spaces, assuming that we are at the start of a line.

    def put_leading_ws(self,n):

        # g.trace("tab_width,indent:",self.tab_width,indent)
        w = self.tab_width

        if w > 1:
            q,r = divmod(n,w)
            self.otabs(q) 
            self.oblanks(r) 
        else:
            self.oblanks(n)
    #@-node:ekr.20031218072017.3515:put_leading_ws
    #@+node:ekr.20031218072017.3516:put_newline
    #@+at 
    #@nonl
    # This method handles scanning when putting the start of a new 
    # line. Unlike the corresponding method in pass one, this method 
    # doesn't need to set a done flag in the caller because the 
    # caller already knows where the code section ends.
    #@-at
    #@@c

    def put_newline(self,s,i,no_first_lws_flag):

        kind, end = self.token_type(s,i,report_errors=False)
        #@    << Output leading white space except for blank lines >>
        #@+node:ekr.20031218072017.3517:<< Output leading white space except for blank lines >>
        j = i ; i = g.skip_ws(s,i)
        if i < len(s) and not g.is_nl(s,i):
            # Conditionally output the leading previous leading whitespace.
            if not no_first_lws_flag:
                self.put_leading_ws(self.tangle_indent)
            # Always output the leading whitespace of _this_ line.
            k, width = g.skip_leading_ws_with_indent(s,j,self.tab_width)
            self.put_leading_ws(width)
        #@-node:ekr.20031218072017.3517:<< Output leading white space except for blank lines >>
        #@nl
        if i >= len(s):
            return i
        elif kind == at_web or kind == at_at:
            i += 2 # Allow the line to be scanned.
        elif kind == at_doc or kind == at_code:
            if self.use_cweb_flag:
                i += 2
        else:
            # These should have set limit in pass 1.
            assert(kind != section_def and kind != at_chapter and kind != at_section)
        return i
    #@-node:ekr.20031218072017.3516:put_newline
    #@+node:ekr.20031218072017.3518:put_part_node
    # This method outputs one part of a section definition.

    def put_part_node(self,part,no_first_lws_flag):

        if 0:
            if part: name = part.name # can't use choose.
            else: name = "<NULL part>"
            g.trace(name)

        if part.doc and self.output_doc_flag and self.print_mode != "silent":
            self.put_doc(part.doc)

        if part.code:
            self.put_code(part.code,no_first_lws_flag)
    #@-node:ekr.20031218072017.3518:put_part_node
    #@+node:ekr.20031218072017.3519:put_section
    #@+at 
    #@nonl
    # This method outputs the definition of a section and all 
    # sections referenced from the section. name is the section's 
    # name. This code checks for recursive definitions by calling 
    # section_check(). We can not allow section x to expand to code 
    # containing another call to section x, either directly or 
    # indirectly.
    #@-at
    #@@c

    def put_section(self,s,i,name,name_end):

        j = g.skip_line(s,i)
        # g.trace("indent:",self.tangle_indent,s[i:j])
        outer_old_indent = self.tangle_indent
        trailing_ws_indent = 0 # Set below.
        inner_old_indent = 0 # Set below.
        newline_flag = False  # True if the line ends with the reference.
        assert(g.match(name,0,"<<") or g.match(name,0,"@<"))
        #@    << Calculate the new value of tangle_indent >>
        #@+node:ekr.20031218072017.3520:<< Calculate the new value of tangle_indent >>
        # Find the start of the line containing the reference.
        j = i
        while j > 0 and not g.is_nl(s,j):
            j -= 1
        if g.is_nl(s,j):
            j = g.skip_nl(s,j)

        # Bump the indentation
        j, width = g.skip_leading_ws_with_indent(s,j,self.tab_width)
        self.tangle_indent += width
        # g.trace("leading ws,new indent:",width,self.tangle_indent)

        # 4/27/01: Force no trailing whitespace in @silent mode.
        if self.print_mode == "silent":
            trailing_ws_indent = 0
        else:
            trailing_ws_indent = self.tangle_indent

        # Increase the indentation if the section reference does not immediately follow
        # the leading white space.  4/3/01: Make no adjustment in @silent mode.
        if (j < len(s) and self.print_mode != "silent" and
                ((self.use_noweb_flag and s[j] != '<') or
                (self.use_cweb_flag and s[j] != '@'))):
            self.tangle_indent += abs(self.tab_width)
        #@-node:ekr.20031218072017.3520:<< Calculate the new value of tangle_indent >>
        #@nl
        #@    << Set 'newline_flag' if the line ends with the reference >>
        #@+node:ekr.20031218072017.3521:<< Set 'newline_flag' if the line ends with the reference >>
        if self.print_mode != "silent":
            i = name_end
            i = g.skip_ws(s,i)
            newline_flag = (i >= len(s) or g.is_nl(s,i))
        #@-node:ekr.20031218072017.3521:<< Set 'newline_flag' if the line ends with the reference >>
        #@nl
        section = self.st_lookup(name)
        if section and section.parts:
            # Expand the section only if we are not already expanding it.
            if self.section_check(name):
                self.section_stack.append(name)
                #@            << put all parts of the section definition >>
                #@+node:ekr.20031218072017.3522:<<put all parts of the section definition>>
                #@+at 
                #@nonl
                # This section outputs each part of a section 
                # definition. We first count how many parts there 
                # are so that the code can output a comment saying 
                # 'part x of y'.
                #@-at
                #@@c

                # Output each part of the section.
                sections = len(section.parts)
                count = 0
                for part in section.parts:
                    count += 1
                    # In @silent mode, there is no sentinel line to "use up" the previously output
                    # leading whitespace.  We set the flag to tell put_part_node and put_code
                    # not to call put_newline at the start of the first code part of the definition.
                    no_first_leading_ws_flag = (count == 1 and self.print_mode == "silent")
                    inner_old_indent = self.tangle_indent
                    # 4/3/01: @silent inhibits newlines after section expansion.
                    if self.print_mode != "silent":
                        #@        << Put the section name in a comment >>
                        #@+node:ekr.20031218072017.3523:<< Put the section name in a comment >>
                        if count > 1:
                            self.onl()
                            self.put_leading_ws(self.tangle_indent)

                        # Don't print trailing whitespace
                        name = name.rstrip()
                        if self.single_comment_string:
                            self.os(self.single_comment_string) ; self.oblank() ; self.os(name)
                            #@    << put (n of m) >>
                            #@+node:ekr.20031218072017.3524:<< put ( n of m ) >>
                            if sections > 1:
                                self.oblank()
                                self.os("(%d of %d)" % (count,sections))
                            #@-node:ekr.20031218072017.3524:<< put ( n of m ) >>
                            #@nl
                        else:
                            assert(
                                self.start_comment_string and len(self.start_comment_string) > 0 and
                                self.end_comment_string and len(self.end_comment_string)> 0)
                            self.os(self.start_comment_string) ; self.oblank() ; self.os(name)
                            #@    << put (n of m) >>
                            #@+node:ekr.20031218072017.3524:<< put ( n of m ) >>
                            if sections > 1:
                                self.oblank()
                                self.os("(%d of %d)" % (count,sections))
                            #@-node:ekr.20031218072017.3524:<< put ( n of m ) >>
                            #@nl
                            self.oblank() ; self.os(self.end_comment_string)

                        self.onl() # Always output a newline.
                        #@-node:ekr.20031218072017.3523:<< Put the section name in a comment >>
                        #@nl
                    self.put_part_node(part,no_first_leading_ws_flag)
                    # 4/3/01: @silent inhibits newlines after section expansion.
                    if count == sections and (self.print_mode != "silent" and self.print_mode != "quiet"):
                        #@        << Put the ending comment >>
                        #@+node:ekr.20031218072017.3525:<< Put the ending comment >>
                        #@+at 
                        #@nonl
                        # We do not produce an ending comment unless 
                        # we are ending the last part of the 
                        # section,and the comment is clearer if we 
                        # don't say(n of m).
                        #@-at
                        #@@c

                        self.onl() ; self.put_leading_ws(self.tangle_indent)
                        #  Don't print trailing whitespace
                        while name_end > 0 and g.is_ws(s[name_end-1]):
                            name_end -= 1

                        if self.single_comment_string:
                            self.os(self.single_comment_string) ; self.oblank()
                            self.os("-- end -- ") ; self.os(name)
                        else:
                            self.os(self.start_comment_string) ; self.oblank()
                            self.os("-- end -- ") ; self.os(name)
                            self.oblank() ; self.os(self.end_comment_string)

                        #@+at 
                        #@nonl
                        # The following code sets a flag for 
                        # untangle.
                        # 
                        # If something follows the section reference 
                        # we must add a newline, otherwise the 
                        # "something" would become part of the 
                        # comment.  Any whitespace following the 
                        # (!newline) should follow the section 
                        # defintion when Untangled.
                        #@-at
                        #@@c

                        if not newline_flag:
                            self.os(" (!newline)") # LeoCB puts the leading blank, so we must do so too.
                            # Put the whitespace following the reference.
                            while name_end < len(s) and g.is_ws(s[name_end]):
                                self.os(s[name_end])
                                name_end += 1
                            self.onl() # We must supply the newline!
                        #@-node:ekr.20031218072017.3525:<< Put the ending comment >>
                        #@nl
                    # Restore the old indent.
                    self.tangle_indent = inner_old_indent
                #@-node:ekr.20031218072017.3522:<<put all parts of the section definition>>
                #@nl
                self.section_stack.pop()
        else:
            #@        << Put a comment about the undefined section >>
            #@+node:ekr.20031218072017.3526:<<Put a comment about the undefined section>>
            self.onl() ; self.put_leading_ws(self.tangle_indent)

            if self.print_mode != "silent":
                if self.single_comment_string:
                    self.os(self.single_comment_string)
                    self.os(" undefined section: ") ; self.os(name) ; self.onl()
                else:
                    self.os(self.start_comment_string)
                    self.os(" undefined section: ") ; self.os(name)
                    self.oblank() ; self.os(self.end_comment_string) ; self.onl()

            self.error("Undefined section: " + name)
            #@-node:ekr.20031218072017.3526:<<Put a comment about the undefined section>>
            #@nl
        if not newline_flag:
            self.put_leading_ws(trailing_ws_indent)
        self.tangle_indent = outer_old_indent
        return i, name_end
    #@-node:ekr.20031218072017.3519:put_section
    #@+node:ekr.20031218072017.3527:section_check
    #@+at 
    #@nonl
    # We can not allow a section to be defined in terms of itself, 
    # either directly or indirectly.
    # 
    # We push an entry on the section stack whenever beginning to 
    # expand a section and pop the section stack at the end of each 
    # section.  This method checks whether the given name appears in 
    # the stack. If so, the section is defined in terms of itself.
    #@-at
    #@@c

    def section_check (self,name):

        if name in self.section_stack:
            s = "Invalid recursive reference of " + name + "\n"
            for n in self.section_stack:
                s += "called from: " + n + "\n"
            self.error(s)
            return False
        return True
    #@-node:ekr.20031218072017.3527:section_check
    #@-node:ekr.20031218072017.3505:Pass 2
    #@-node:ekr.20031218072017.3488:tangle
    #@+node:ekr.20031218072017.3528:tst
    #@+node:ekr.20031218072017.3529:st_check
    def st_check(self):

        """Checks the given symbol table for defined but never referenced sections."""

        # g.trace(keys)
        for name in sorted(self.tst):
            section = self.tst[name]
            if not section.referenced:
                lp = g.choose(self.use_noweb_flag,"<< ","@< ")
                rp = g.choose(self.use_noweb_flag," >>"," @>")
                g.es('',' ' * 4,'warning:',lp,'',section.name,'',rp,'has been defined but not used.')
    #@-node:ekr.20031218072017.3529:st_check
    #@+node:ekr.20031218072017.3530:st_dump
    # Dumps the given symbol table in a readable format.

    def st_dump(self,verbose_flag=True):

        s = "\ndump of symbol table...\n"

        for name in sorted(self.tst):
            section = self.tst[name]
            if verbose_flag:
                s += self.st_dump_node(section)
            else:
                theType = g.choose(len(section.parts)>0,"  ","un")
                s += ("\n" + theType + "defined:[" + section.name + "]")
        return s
    #@-node:ekr.20031218072017.3530:st_dump
    #@+node:ekr.20031218072017.3531:st_dump_node
    # Dumps each part of a section's definition.

    def st_dump_node(self,section):

        s = ("\nsection: " + section.name +
            ", referenced:" + str(section.referenced) +
            ", is root:" + str(section.is_root))

        if len(section.parts) > 0:
            s += "\n----- parts of " + g.angleBrackets(section.name)
            n = 1 # part list is in numeric order
            for part in section.parts:
                s += "\n----- Part " + str(n)
                n += 1
                s += "\ndoc:  [" + repr(part.doc)  + "]"
                s += "\ncode: [" + repr(part.code) + "]"
            s += "\n----- end of partList\n"
        return s
    #@-node:ekr.20031218072017.3531:st_dump_node
    #@+node:ekr.20031218072017.3532:st_enter
    def st_enter(self,name,code,doc,is_root_flag=False):

        """Enters names and their associated code and doc parts into the given symbol table."""

        section = self.st_lookup(name,is_root_flag)
        assert(section)
        if doc:
            doc = doc.rstrip() # remove trailing lines.
        if code:
            if self.print_mode != "silent": # @silent supresses newline processing.
                i = g.skip_blank_lines(code,0) # remove leading lines.
                if i > 0: code = code[i:] 
                if code and len(code) > 0: code = code.rstrip() # remove trailing lines.
            if len(code) == 0: code = None
        if code:
            #@        << check for duplicate code definitions >>
            #@+node:ekr.20031218072017.3533:<<check for duplicate code definitions >>
            for part in section.parts:

                if self.tangling and code and code == part.code:
                    s = g.angleBrackets(section.name)
                    g.es('warning: possible duplicate definition of:',s)
            #@nonl
            #@-node:ekr.20031218072017.3533:<<check for duplicate code definitions >>
            #@nl
        if code or doc:
            part = part_node(name,code,doc,is_root_flag,is_dirty=False)
            section.parts.append(part)
        else: # A reference
            section.referenced = True
        if is_root_flag:
            self.root_list.append(section)
            section.referenced = True # Mark the root as referenced.
            #@        <<remember root node attributes>>
            #@+node:ekr.20031218072017.3534:<<remember root node attributes>>
            # Stephen Schaefer, 9/2/02
            # remember the language and comment characteristics
            section.root_attributes = root_attributes(self)
            #@-node:ekr.20031218072017.3534:<<remember root node attributes>>
            #@nl
        # Stephen Schaefer, 9/2/02
        return len(section.parts) # part number
    #@-node:ekr.20031218072017.3532:st_enter
    #@+node:ekr.20031218072017.3535:st_enter_root_name
    # Enters a root name into the given symbol table.

    def st_enter_root_name(self,name,code,doc):

        # assert(code)
        if name: # User errors can result in an empty @root name.
            self.st_enter(name,code,doc,is_root_flag=True)
    #@-node:ekr.20031218072017.3535:st_enter_root_name
    #@+node:ekr.20031218072017.3536:st_enter_section_name
    def st_enter_section_name(self,name,code,doc):

        """Enters a section name into the given symbol table.

        The code and doc pointers are None for references."""

        return self.st_enter(name,code,doc)
    #@-node:ekr.20031218072017.3536:st_enter_section_name
    #@+node:ekr.20031218072017.3537:st_lookup
    def st_lookup(self,name,is_root_flag=False):

        """Looks up name in the symbol table and creates a tst_node for it if it does not exist."""

        if is_root_flag:
            key = name
        else:
            key = self.standardize_name(name)

        if key in self.tst:
            section = self.tst[key]
            # g.trace("found:" + key)
            return section
        else:
            # g.trace("not found:" + key)
            section = tst_node(key,is_root_flag)
            self.tst [key] = section
            return section
    #@-node:ekr.20031218072017.3537:st_lookup
    #@-node:ekr.20031218072017.3528:tst
    #@+node:ekr.20031218072017.3538:ust
    #@+node:ekr.20031218072017.3539:ust_dump
    def ust_dump (self):

        s = "\n---------- Untangle Symbol Table ----------"

        for name in sorted(self.ust):
            section = self.ust[name]
            s += "\n\n" + section.name
            for part in section.parts.values():
                assert(part.of == section.of)
                s += "\n----- part %d of %d -----\n" % (part.part,part.of)
                s += repr(g.get_line(part.code,0))

        s += "\n--------------------"

        return s
    #@-node:ekr.20031218072017.3539:ust_dump
    #@+node:ekr.20031218072017.3540:ust_enter
    #@+at 
    #@nonl
    # This routine enters names and their code parts into the given 
    # table. The 'part' and 'of' parameters are taken from the 
    # "(part n of m)" portion of the line that introduces the 
    # section definition in the C code.
    # 
    # If no part numbers are given the caller should set the 'part' 
    # and 'of' parameters to zero.  The caller is reponsible for 
    # checking for duplicate parts.
    # 
    # This function handles names scanned from a source file; the 
    # corresponding st_enter routine handles names scanned from 
    # outlines.
    #@-at
    #@@c

    def ust_enter (self,name,part,of,code,nl_flag,is_root_flag=False):

        if not is_root_flag:
            name = self.standardize_name(name)
        #@    << remove blank lines from the start and end of the text >>
        #@+node:ekr.20031218072017.3541:<< remove blank lines from the start and end of the text >>
        i = g.skip_blank_lines(code,0)
        if i > 0:
            code = code[i:].rstrip()

        #@-node:ekr.20031218072017.3541:<< remove blank lines from the start and end of the text >>
        #@nl
        u = ust_node(name,code,part,of,nl_flag,False) # update_flag
        if name not in self.ust:
            self.ust[name] = u
        section = self.ust[name]
        section.parts[part]=u # Parts may be defined in any order.
        # g.trace("section [%s](part %d of %d)...%s" % (name,part,of,g.get_line(code,0)))
    #@-node:ekr.20031218072017.3540:ust_enter
    #@+node:ekr.20031218072017.3542:ust_lookup
    # Searches the given table for a part matching the name and part number.

    def ust_lookup (self,name,part_number,is_root_flag=False,update_flag=False):

        # g.trace(name,part_number)

        if not is_root_flag:
            name = self.standardize_name(name)

        if part_number == 0: part_number = 1 # A hack: zero indicates the first part.
        if name in self.ust:
            section = self.ust[name]
            if part_number in section.parts:
                part = section.parts[part_number]
                if update_flag: part.update_flag = True
                # g.trace("found: %d (%d)...\n" % (name,part_number,g.get_line(part.code,0)))
                return part, True

        # g.trace("not found: %s(%d)...\n" % (name,part_number))
        return None, False
    #@-node:ekr.20031218072017.3542:ust_lookup
    #@+node:ekr.20031218072017.3543:ust_warn_about_orphans
    def ust_warn_about_orphans (self):

        """Issues a warning about any sections in the derived file for which
        no corresponding section has been seen in the outline."""

        for section in self.ust.values():
            # g.trace(section)
            for part in section.parts.values():
                assert(part.of == section.of)
                if not part.update_flag:
                    lp = g.choose(self.use_noweb_flag,"<< ","@< ")
                    rp = g.choose(self.use_noweb_flag," >>"," @>")
                    g.es("warning:",'%s%s%s' % (lp,part.name,rp),"is not in the outline")
                    break # One warning per section is enough.
    #@-node:ekr.20031218072017.3543:ust_warn_about_orphans
    #@-node:ekr.20031218072017.3538:ust
    #@+node:ekr.20031218072017.3544:untangle
    #@+node:ekr.20031218072017.3545:compare_comments
    #@+at 
    #@nonl
    # This function compares the interior of comments and returns 
    # True if they are identical except for whitespace or newlines. 
    # It is up to the caller to eliminate the opening and closing 
    # delimiters from the text to be compared.
    #@-at
    #@@c

    def compare_comments (self,s1,s2):

        tot_len = 0
        if self.comment: tot_len += len(self.comment)
        if self.comment_end: tot_len += len(self.comment_end)
        CWEB_flag = (self.language == "c" and not self.use_noweb_flag)

        p1, p2 = 0, 0
        while p1 < len(s1) and p2 < len(s2):
            p1 = g.skip_ws_and_nl(s1,p1)
            p2 = g.skip_ws_and_nl(s2,p2)
            if self.comment and self.comment_end:
                #@            << Check both parts for @ comment conventions >>
                #@+node:ekr.20031218072017.3546:<< Check both parts for @ comment conventions >>
                #@+at 
                #@nonl
                # This code is used in forgiving_compare()and in 
                # compare_comments().
                # 
                # In noweb mode we allow / * @ * /  (without the 
                # spaces)to be equal to @.
                # In CWEB mode we allow / * @ ? * / (without the 
                # spaces)to be equal to @?.
                # at-backslash is not a valid CWEB control code, so 
                # we don't have to equate
                # / * @ \\ * / with at-backslash.
                # 
                # We must be careful not to run afoul of this very 
                # convention here!
                #@-at
                #@@c

                if p1 < len(s1) and s1[p1] == '@':
                    if g.match(s2,p2,self.comment + '@' + self.comment_end):
                        p1 += 1
                        p2 += tot_len + 1
                        continue
                    elif (CWEB_flag and s1[p1] == '@' and p1 + 1 < len(s1) and
                        g.match(s2,p2,self.comment + '@' + s1[p1+1])):
                        p1 += 2
                        p2 += tot_len + 2
                        continue
                elif p2 < len(s2) and s2[p2] == '@':
                    if g.match(s1,p1,self.comment + '@' + self.comment_end):
                        p2 += 1
                        p1 += tot_len + 1
                        continue
                    elif (CWEB_flag and s1[p1] == '@' and p1 + 1 < len(s1) and
                        g.match(s1,p1,self.comment + '@' + s2[p2+1])):
                        p2 += 2
                        p1 += tot_len + 2
                        continue
                #@-node:ekr.20031218072017.3546:<< Check both parts for @ comment conventions >>
                #@nl
            if p1 >= len(s1) or p2 >= len(s2):
                break
            if s1[p1] != s2[p2]:
                return False
            p1 += 1 ; p2 += 1
        p1 = g.skip_ws_and_nl(s1,p1)
        p2 = g.skip_ws_and_nl(s2,p2)
        return p1 == len(s1) and p2 == len(s2)
    #@-node:ekr.20031218072017.3545:compare_comments
    #@+node:ekr.20031218072017.3547:massage_block_comment (no longer used)
    #@+at 
    #@nonl
    # This function is called to massage an @doc part in the ust. We 
    # call this routine only after a mismatch in @doc parts is found 
    # between the ust and tst. On entry, the parameters point to the 
    # inside of a block C comment: the opening and closing 
    # delimiters are not part of the text handled by self routine.
    # 
    # This code removes newlines that may have been inserted by the 
    # Tangle command in a block comment. Tangle may break lines 
    # differently in different expansions, but line breaks are 
    # ignored by forgiving_compare() and doc_compare() within block 
    # C comments.
    # 
    # We count the leading whitespace from the first non-blank line 
    # and remove this much whitespace from all lines. We also remove 
    # singleton newlines and replace sequences of two or more 
    # newlines by a single newline.
    #@-at
    #@@c

    def massage_block_comment (self,s):

        c = self.c
        newlines = 0  # Consecutive newlines seen.
        i = g.skip_blank_lines(s,0)
        # Copy the first line and set n
        i, n = g.skip_leading_ws_with_indent(s,i,c.tab_width)
        j = i ; i = g.skip_to_end_of_line(s,i)
        result = s[j:i]
        while i < len(s):
            assert(g.is_nl(s,i))
            newlines += 1
            # Replace the first newline with a blank.
            result += ' ' ; i += 1
            while i < len(s) and g.is_nl(s,i):
                i += 1 # skip the newline.
            j = i ; i = g.skip_ws(s,i)
            if g.is_nl(s,i)and newlines > 1:
                # Skip blank lines.
                while g.is_nl(s,i):
                    i += 1
            else:
                # Skip the leading whitespace.
                i = j # back track
                i = g.skip_leading_ws(s,i,n,c.tab_width)
                newlines = 0
                # Copy the rest of the line.
                j = i ; i = g.skip_to_end_of_line(s,i)
                result += s[j:i]
        return result
    #@-node:ekr.20031218072017.3547:massage_block_comment (no longer used)
    #@+node:ekr.20031218072017.3548:forgiving_compare
    #@+at 
    #@nonl
    # This is the "forgiving compare" function.  It compares two 
    # texts and returns True if they are identical except for 
    # comments or non-critical whitespace.  Whitespace inside 
    # strings or preprocessor directives must match exactly.
    #@-at
    #@@c

    def forgiving_compare (self,name,part,s1,s2):

        if 0:
            g.trace(name,part,
                "\n1:",g.get_line(s1,0),
                "\n2:",g.get_line(s2,0))
        s1 = g.toUnicode(s1,self.encoding)
        s2 = g.toUnicode(s2,self.encoding)
        #@    << Define forgiving_compare vars >>
        #@+node:ekr.20031218072017.3549:<< Define forgiving_compare vars >>
        # scan_derived_file has set the ivars describing comment delims.
        first1 = first2 = 0

        tot_len = 0
        if self.comment: tot_len += len(self.comment)
        if self.comment_end: tot_len += len(self.comment_end)

        CWEB_flag = (self.language == "c" and not self.use_noweb_flag)
        #@-node:ekr.20031218072017.3549:<< Define forgiving_compare vars >>
        #@nl
        p1 = g.skip_ws_and_nl(s1,0) 
        p2 = g.skip_ws_and_nl(s2,0)
        result = True
        while result and p1 < len(s1) and p2 < len(s2):
            first1 = p1 ; first2 = p2
            if self.comment and self.comment_end:
                #@            << Check both parts for @ comment conventions >>
                #@+node:ekr.20031218072017.3546:<< Check both parts for @ comment conventions >>
                #@+at 
                #@nonl
                # This code is used in forgiving_compare()and in 
                # compare_comments().
                # 
                # In noweb mode we allow / * @ * /  (without the 
                # spaces)to be equal to @.
                # In CWEB mode we allow / * @ ? * / (without the 
                # spaces)to be equal to @?.
                # at-backslash is not a valid CWEB control code, so 
                # we don't have to equate
                # / * @ \\ * / with at-backslash.
                # 
                # We must be careful not to run afoul of this very 
                # convention here!
                #@-at
                #@@c

                if p1 < len(s1) and s1[p1] == '@':
                    if g.match(s2,p2,self.comment + '@' + self.comment_end):
                        p1 += 1
                        p2 += tot_len + 1
                        continue
                    elif (CWEB_flag and s1[p1] == '@' and p1 + 1 < len(s1) and
                        g.match(s2,p2,self.comment + '@' + s1[p1+1])):
                        p1 += 2
                        p2 += tot_len + 2
                        continue
                elif p2 < len(s2) and s2[p2] == '@':
                    if g.match(s1,p1,self.comment + '@' + self.comment_end):
                        p2 += 1
                        p1 += tot_len + 1
                        continue
                    elif (CWEB_flag and s1[p1] == '@' and p1 + 1 < len(s1) and
                        g.match(s1,p1,self.comment + '@' + s2[p2+1])):
                        p2 += 2
                        p1 += tot_len + 2
                        continue
                #@-node:ekr.20031218072017.3546:<< Check both parts for @ comment conventions >>
                #@nl
            ch1 = s1[p1]
            if ch1 == '\r' or ch1 == '\n':
                #@            << Compare non-critical newlines >>
                #@+node:ekr.20031218072017.3550:<< Compare non-critical newlines >>
                p1 = g.skip_ws_and_nl(s1,p1)
                p2 = g.skip_ws_and_nl(s2,p2)
                #@-node:ekr.20031218072017.3550:<< Compare non-critical newlines >>
                #@nl
            elif ch1 ==  ' ' or ch1 == '\t':
                #@            << Compare non-critical whitespace >>
                #@+node:ekr.20031218072017.3551:<< Compare non-critical whitespace >>
                p1 = g.skip_ws(s1,p1)
                p2 = g.skip_ws(s2,p2)
                #@-node:ekr.20031218072017.3551:<< Compare non-critical whitespace >>
                #@nl
            elif ch1 == '\'' or ch1 == '"':
                #@            << Compare possible strings >>
                #@+node:ekr.20031218072017.3555:<< Compare possible strings >>
                # This code implicitly assumes that string1_len == string2_len == 1.
                # The match test ensures that the language actually supports strings.

                if (g.match(s1,p1,self.string1) or g.match(s1,p1,self.string2)) and s1[p1] == s2[p2]:

                    if self.language == "pascal":
                        #@        << Compare Pascal strings >>
                        #@+node:ekr.20031218072017.3557:<< Compare Pascal strings >>
                        #@+at 
                        #@nonl
                        # We assume the Pascal string is on a single 
                        # line so the problems with cr/lf do not 
                        # concern us.
                        #@-at
                        #@@c

                        first1 = p1 ; first2 = p2
                        p1 = g.skip_pascal_string(s1,p1)
                        p2 = g.skip_pascal_string(s2,p2)
                        result = s1[first1,p1] == s2[first2,p2]
                        #@-node:ekr.20031218072017.3557:<< Compare Pascal strings >>
                        #@nl
                    else:
                        #@        << Compare C strings >>
                        #@+node:ekr.20031218072017.3556:<< Compare C strings >>
                        delim = s1[p1]
                        result = s1[p1] == s2[p2]
                        p1 += 1 ; p2 += 1

                        while result and p1 < len(s1) and p2 < len(s2):
                            if s1[p1] == delim and self.is_end_of_string(s1,p1,delim):
                                result =(s2[p2] == delim and self.is_end_of_string(s2,p2,delim))
                                p1 += 1 ; p2 += 1
                                break
                            elif g.is_nl(s1,p1) and g.is_nl(s2,p2):
                                p1 = g.skip_nl(s1,p1)
                                p2 = g.skip_nl(s2,p2)
                            else:
                                result = s1[p1] == s2[p2]
                                p1 += 1 ; p2 += 1
                        #@-node:ekr.20031218072017.3556:<< Compare C strings >>
                        #@nl
                    if not result:
                        self.mismatch("Mismatched strings")
                else:
                    #@    << Compare single characters >>
                    #@+node:ekr.20031218072017.3553:<< Compare single characters >>
                    assert(p1 < len(s1) and p2 < len(s2))
                    result = s1[p1] == s2[p2]
                    p1 += 1 ; p2 += 1
                    if not result: self.mismatch("Mismatched single characters")
                    #@-node:ekr.20031218072017.3553:<< Compare single characters >>
                    #@nl
                #@-node:ekr.20031218072017.3555:<< Compare possible strings >>
                #@nl
            elif ch1 == '#':
                #@            << Compare possible preprocessor directives >>
                #@+node:ekr.20031218072017.3552:<< Compare possible preprocessor directives >>
                if self.language == "c":
                    #@    << compare preprocessor directives >>
                    #@+node:ekr.20031218072017.3554:<< Compare preprocessor directives >>
                    # We cannot assume that newlines are single characters.

                    result = s1[p1] == s2[p2]
                    p1 += 1 ; p2 += 1
                    while result and p1 < len(s1) and p2 < len(s2):
                        if g.is_nl(s1,p1):
                            result = g.is_nl(s2,p2)
                            if not result or self.is_end_of_directive(s1,p1):
                                break
                            p1 = g.skip_nl(s1,p1)
                            p2 = g.skip_nl(s2,p2)
                        else:
                            result = s1[p1] == s2[p2]
                            p1 += 1 ; p2 += 1
                    if not result:
                        self.mismatch("Mismatched preprocessor directives")
                    #@-node:ekr.20031218072017.3554:<< Compare preprocessor directives >>
                    #@nl
                else:
                    #@    << compare single characters >>
                    #@+node:ekr.20031218072017.3553:<< Compare single characters >>
                    assert(p1 < len(s1) and p2 < len(s2))
                    result = s1[p1] == s2[p2]
                    p1 += 1 ; p2 += 1
                    if not result: self.mismatch("Mismatched single characters")
                    #@-node:ekr.20031218072017.3553:<< Compare single characters >>
                    #@nl
                #@-node:ekr.20031218072017.3552:<< Compare possible preprocessor directives >>
                #@nl
            elif ch1 == '<' or ch1 == '@':
                #@            << Compare possible section references >>
                #@+node:ekr.20031218072017.3558:<< Compare possible section references >>
                if s1[p1] == '@' and CWEB_flag:  start_ref = "@<"
                elif s1[p1] == '<' and not CWEB_flag:  start_ref = "<<"
                else: start_ref = None

                # Tangling may insert newlines.
                p2 = g.skip_ws_and_nl(s2,p2)

                junk, kind1, junk2 = self.is_section_name(s1,p1)
                junk, kind2, junk2 = self.is_section_name(s2,p2)

                if start_ref and (kind1 != bad_section_name or kind2 != bad_section_name):
                    result = self.compare_section_names(s1[p1:],s2[p2:])
                    if result:
                        p1, junk1, junk2 = self.skip_section_name(s1,p1)
                        p2, junk1, junk2 = self.skip_section_name(s2,p2)
                    else: self.mismatch("Mismatched section names")
                else:
                    # Neither p1 nor p2 points at a section name.
                    result = s1[p1] == s2[p2]
                    p1 += 1 ; p2 += 1
                    if not result:
                        self.mismatch("Mismatch at '@' or '<'")
                #@-node:ekr.20031218072017.3558:<< Compare possible section references >>
                #@nl
            else:
                #@            << Compare comments or single characters >>
                #@+node:ekr.20031218072017.3559:<< Compare comments or single characters >>
                if g.match(s1,p1,self.sentinel) and g.match(s2,p2,self.sentinel):
                    first1 = p1 ; first2 = p2
                    p1 = g.skip_to_end_of_line(s1,p1)
                    p2 = g.skip_to_end_of_line(s2,p2)
                    result = self.compare_comments(s1[first1:p1],s2[first2:p2])
                    if not result:
                        self.mismatch("Mismatched sentinel comments")
                elif g.match(s1,p1,self.line_comment) and g.match(s2,p2,self.line_comment):
                    first1 = p1 ; first2 = p2
                    p1 = g.skip_to_end_of_line(s1,p1)
                    p2 = g.skip_to_end_of_line(s2,p2)
                    result = self.compare_comments(s1[first1:p1],s2[first2:p2])
                    if not result:
                        self.mismatch("Mismatched single-line comments")
                elif g.match(s1,p1,self.comment) and g.match(s2,p2,self.comment):
                    while (p1 < len(s1) and p2 < len(s2) and
                        not g.match(s1,p1,self.comment_end) and not g.match(s2,p2,self.comment_end)):
                        # ws doesn't have to match exactly either!
                        if g.is_nl(s1,p1)or g.is_ws(s1[p1]):
                            p1 = g.skip_ws_and_nl(s1,p1)
                        else: p1 += 1
                        if g.is_nl(s2,p2)or g.is_ws(s2[p2]):
                            p2 = g.skip_ws_and_nl(s2,p2)
                        else: p2 += 1
                    p1 = g.skip_ws_and_nl(s1,p1)
                    p2 = g.skip_ws_and_nl(s2,p2)
                    if g.match(s1,p1,self.comment_end) and g.match(s2,p2,self.comment_end):
                        first1 = p1 ; first2 = p2
                        p1 += len(self.comment_end)
                        p2 += len(self.comment_end)
                        result = self.compare_comments(s1[first1:p1],s2[first2:p2])
                    else: result = False
                    if not result:
                        self.mismatch("Mismatched block comments")
                elif g.match(s1,p1,self.comment2) and g.match(s2,p2,self.comment2):
                    while (p1 < len(s1) and p2 < len(s2) and
                        not g.match(s1,p1,self.comment2_end) and not g.match(s2,p2,self.comment2_end)):
                        # ws doesn't have to match exactly either!
                        if  g.is_nl(s1,p1)or g.is_ws(s1[p1]):
                            p1 = g.skip_ws_and_nl(s1,p1)
                        else: p1 += 1
                        if g.is_nl(s2,p2)or g.is_ws(s2[p2]):
                            p2 = g.skip_ws_and_nl(s2,p2)
                        else: p2 += 1
                    p1 = g.skip_ws_and_nl(s1,p1)
                    p2 = g.skip_ws_and_nl(s2,p2)
                    if g.match(s1,p1,self.comment2_end) and g.match(s2,p2,self.comment2_end):
                        first1 = p1 ; first2 = p2
                        p1 += len(self.comment2_end)
                        p2 += len(self.comment2_end)
                        result = self.compare_comments(s1[first1:p1],s2[first2:p2])
                    else: result = False
                    if not result:
                        self.mismatch("Mismatched alternalte block comments")
                else:
                    #@    << Compare single characters >>
                    #@+node:ekr.20031218072017.3553:<< Compare single characters >>
                    assert(p1 < len(s1) and p2 < len(s2))
                    result = s1[p1] == s2[p2]
                    p1 += 1 ; p2 += 1
                    if not result: self.mismatch("Mismatched single characters")
                    #@-node:ekr.20031218072017.3553:<< Compare single characters >>
                    #@nl
                #@-node:ekr.20031218072017.3559:<< Compare comments or single characters >>
                #@nl
        #@    << Make sure both parts have ended >>
        #@+node:ekr.20031218072017.3560:<< Make sure both parts have ended >>
        if result:
            p1 = g.skip_ws_and_nl(s1,p1)
            p2 = g.skip_ws_and_nl(s2,p2)
            result = p1 >= len(s1) and p2 >= len(s2)
            if not result:
                # Show the ends of both parts.
                p1 = len(s1)
                p2 = len(s2)
                self.mismatch("One part ends before the other.")
        #@-node:ekr.20031218072017.3560:<< Make sure both parts have ended >>
        #@nl
        if not result:
            #@        << trace the mismatch >>
            #@+node:ekr.20031218072017.3561:<< Trace the mismatch >>
            if 0:
                g.trace(self.message +
                    "\nPart ",part," section ",name,
                    "\n1:",g.get_line(s1,p1),
                    "\n2:",g.get_line(s2,p2))
            #@-node:ekr.20031218072017.3561:<< Trace the mismatch >>
            #@nl
        return result
    #@-node:ekr.20031218072017.3548:forgiving_compare
    #@+node:ekr.20031218072017.3562:mismatch
    def mismatch (self,message):

        self.message = message
    #@-node:ekr.20031218072017.3562:mismatch
    #@+node:ekr.20031218072017.3563:scan_derived_file (pass 1)
    #@+at
    # 
    # This function scans an entire derived file in s, discovering 
    # section or part
    # definitions.
    # 
    # This is the easiest place to delete leading whitespace from 
    # each line: we simply
    # don't copy it. We also ignore leading blank lines and trailing 
    # blank lines. The
    # resulting definition must compare equal using the "forgiving" 
    # compare to any
    # other definitions of that section or part.
    # 
    # We use a stack to handle nested expansions. The outermost 
    # level of expansion
    # corresponds to the @root directive that created the file. When 
    # the stack is
    # popped, the indent variable is restored.
    # 
    # self.root_name is the name of the file mentioned in the @root 
    # directive.
    # 
    # The caller has deleted all body_ignored_newlines from the 
    # text.
    #@-at
    #@@c

    def scan_derived_file (self,s):

        c = self.c
        self.def_stack = []
        #@    << set the private global matching vars >>
        #@+node:ekr.20031218072017.2368:<< set the private global matching vars >>
        # Set defaults from the public globals set by the @comment command.
        if self.single_comment_string:
            self.sentinel = self.single_comment_string
            self.sentinel_end = None
        elif self.end_comment_string:
            self.sentinel = self.start_comment_string
            self.sentinel_end = self.end_comment_string
        else:
            self.sentinel = self.sentinel_end = None

        if 0:
            g.trace("single,start,end,sentinel:",
                repr(self.single_comment_string),
                repr(self.start_comment_string),
                repr(self.end_comment_string),
                repr(self.sentinel))

        # Set defaults.  See set_delims_from_langauge.
        self.line_comment = self.single_comment_string
        self.comment = self.start_comment_string
        self.comment_end = self.end_comment_string
        self.comment2 = self.comment2_end = None
        self.string1 = "\""
        self.string2 = "'"
        self.verbatim = None

        # Set special cases.
        if self.language == "plain":
            self.string1 = self.string2 = None # This is debatable.
            self.line_comment = None
        if self.language == "pascal":
            self.comment2 = "(*" ; self.comment2_end = "*)"
        if self.language == "latex": # 3/10/03: Joo-won Jung
            self.string1 = self.string2 = None # This is debatable.
        if self.language == "html":
            self.string1 = '"' ; self.string2 = None # 12/3/03

        if 0:
            g.trace("string1,string2,line_comment:",
                repr(self.string1),
                repr(self.string2),
                repr(self.line_comment))
        #@-node:ekr.20031218072017.2368:<< set the private global matching vars >>
        #@nl
        line_indent = 0  # The indentation to use if we see a section reference.
        # indent is the leading whitespace to be deleted.
        i, indent = g.skip_leading_ws_with_indent(s,0,self.tab_width)
        #@    << Skip the header line output by tangle >>
        #@+node:ekr.20031218072017.3564:<< Skip the header line output by tangle >>
        if self.sentinel or self.comment:
            line = g.choose(self.sentinel,self.sentinel,self.comment) + " Created by Leo from" 
            if g.match(s,i,line):
                # Even a block comment will end on the first line.
                i = g.skip_to_end_of_line(s,i)
        #@-node:ekr.20031218072017.3564:<< Skip the header line output by tangle >>
        #@nl
        # The top level of the stack represents the root.
        self.push_new_def_node(self.root_name,indent,1,1,True)
        while i < len(s):
            ch = s[i]
            if ch == '\r':
                i += 1 # ignore
            elif ch == '\n':
                #@            << handle the start of a new line >>
                #@+node:ekr.20031218072017.3565:<< handle the start of a new line >>
                self.copy(ch) ; i += 1 # This works because we have one-character newlines.

                # Set line_indent, used only if we see a section reference.
                junk, line_indent = g.skip_leading_ws_with_indent(s,i,c.tab_width)
                i = g.skip_leading_ws(s,i,indent,c.tab_width) # skip indent leading white space.
                #@-node:ekr.20031218072017.3565:<< handle the start of a new line >>
                #@nl
            elif g.match(s,i,self.sentinel) and self.is_sentinel_line(s,i):
                #@            << handle a sentinel line  >>
                #@+node:ekr.20031218072017.3566:<< handle a sentinel line >>
                #@+at 
                #@nonl
                # This is the place to eliminate the proper amount 
                # of whitespace from the start of each line. We do 
                # this by setting the 'indent' variable to the 
                # leading whitespace of the first _non-blank_ line 
                # following the opening sentinel.
                # 
                # Tangle increases the indentation by one tab if the 
                # section reference is not the first non-whitespace 
                # item on the line,so self code must do the same.
                #@-at
                #@@c

                # g.trace(g.get_line(s,i))
                result,junk,kind,name,part,of,end,nl_flag = self.is_sentinel_line_with_data(s,i)
                assert(result)
                #@<< terminate the previous part of this section if it exists >>
                #@+node:ekr.20031218072017.3567:<< terminate the previous part of this section if it exists >>
                #@+at 
                #@nonl
                # We have just seen a sentinel line. Any kind of 
                # sentinel line will terminate a previous part of 
                # the present definition. For end sentinel lines, 
                # the present section name must match the name on 
                # the top of the stack.
                #@-at
                #@@c

                if len(self.def_stack) > 0:
                    dn = self.def_stack[-1]
                    if self.compare_section_names(name,dn.name):
                        dn = self.def_stack.pop()
                        if len(dn.code) > 0:
                            thePart, found = self.ust_lookup(name,dn.part,False,False) # not root, not update
                            # Check for incompatible previous definition.
                            if found and not self.forgiving_compare(name,dn.part,dn.code,thePart.code):
                                self.error("Incompatible definitions of " + name)
                            elif not found:
                                self.ust_enter(name,dn.part,dn.of,dn.code,dn.nl_flag,False) # not root
                    elif kind == end_sentinel_line:
                        self.error("Missing sentinel line for: " + name)
                #@-node:ekr.20031218072017.3567:<< terminate the previous part of this section if it exists >>
                #@nl

                if kind == start_sentinel_line:
                    indent = line_indent
                    # Increase line_indent by one tab width if the
                    # the section reference does not start the line.
                    j = i - 1
                    while j >= 0:
                        if g.is_nl(s,j):
                            break
                        elif not g.is_ws(s[j]):
                            indent += abs(self.tab_width) ; break
                        j -= 1
                    # copy the section reference to the _present_ section,
                    # but only if this is the first part of the section.
                    if part < 2: self.copy(name)
                    # Skip to the first character of the new section definition.
                    i = g.skip_to_end_of_line(s,i)
                    # Start the new section.
                    self.push_new_def_node(name,indent,part,of,nl_flag)
                else:
                    assert(kind == end_sentinel_line)
                    # Skip the sentinel line.
                    i = g.skip_to_end_of_line(s,i)
                    # Skip a newline only if it was added after(!newline)
                    if not nl_flag:
                        i = g.skip_ws(s,i)
                        i = g.skip_nl(s,i)
                        i = g.skip_ws(s,i)
                        # Copy any whitespace following the (!newline)
                        while end and g.is_ws(s[end]):
                            self.copy(s[end])
                            end += 1
                    # Restore the old indentation level.
                    if len(self.def_stack) > 0:
                        indent = self.def_stack[-1].indent
                #@-node:ekr.20031218072017.3566:<< handle a sentinel line >>
                #@nl
            elif g.match(s,i,self.line_comment) or g.match(s,i,self.verbatim):
                #@            << copy the entire line >>
                #@+node:ekr.20031218072017.3568:<< copy the entire line >>
                j = i ; i = g.skip_to_end_of_line(s,i)
                self.copy(s[j:i])
                #@-node:ekr.20031218072017.3568:<< copy the entire line >>
                #@nl
            elif g.match(s,i,self.comment):
                #@            << copy a multi-line comment >>
                #@+node:ekr.20031218072017.3570:<< copy a multi-line comment >>
                assert(self.comment_end)

                # Scan for the ending delimiter.
                j = i ; i += len(self.comment)
                while i < len(s) and not g.match(s,i,self.comment_end):
                    i += 1
                if g.match(s,i,self.comment_end):
                    i += len(self.comment_end)
                self.copy(s[j:i])
                #@-node:ekr.20031218072017.3570:<< copy a multi-line comment >>
                #@nl
            elif g.match(s,i,self.comment2):
                #@            << copy an alternate multi-line comment >>
                #@+node:ekr.20031218072017.3571:<< copy an alternate multi-line comment >>
                assert(self.comment2_end)
                j = i
                # Scan for the ending delimiter.
                i += len(self.comment2)
                while i < len(s) and not g.match(s,i,self.comment2_end):
                    i += 1
                if g.match(s,i,self.comment2_end):
                    i += len(self.comment2)
                self.copy(s[j:i])
                #@-node:ekr.20031218072017.3571:<< copy an alternate multi-line comment >>
                #@nl
            elif g.match(s,i,self.string1) or g.match(s,i,self.string2):
                #@            << copy a string >>
                #@+node:ekr.20031218072017.3569:<< copy a string >>
                j = i
                if self.language == "pascal":
                    i = g.skip_pascal_string(s,i)
                else:
                    i = g.skip_string(s,i)
                self.copy(s[j:i])
                #@-node:ekr.20031218072017.3569:<< copy a string >>
                #@nl
            else:
                self.copy(ch) ; i += 1
        #@    << end all open sections >>
        #@+node:ekr.20031218072017.3572:<< end all open sections >>
        dn= None
        while len(self.def_stack) > 0:
            dn = self.def_stack.pop()
            if len(self.def_stack) > 0:
                self.error("Unterminated section: " + dn.name)
        if dn:
            # Terminate the root setcion.
            i = len(s)
            if dn.code and len(dn.code) > 0:
                self.ust_enter(dn.name,dn.part,dn.of,dn.code,dn.nl_flag,is_root_flag=True)
            else:
                self.error("Missing root part")
        else:
            self.error("Missing root section")
        #@-node:ekr.20031218072017.3572:<< end all open sections >>
        #@nl
    #@-node:ekr.20031218072017.3563:scan_derived_file (pass 1)
    #@+node:ekr.20031218072017.3573:update_def (pass 2)
    #@+at
    # This function handles the actual updating of section 
    # definitions in the web.
    # Only code parts are updated, never doc parts.
    # 
    # During pass 2 of Untangle, skip_body() calls this routine when 
    # it discovers the
    # definition of a section in the outline. We look up the name in 
    # the ust. If an
    # entry exists, we compare the code (the code part of an outline 
    # node) with the
    # code part in the ust. We update the code part if necessary.
    # 
    # We use the forgiving_compare() to compare code parts. It's not 
    # possible to
    # change only trivial whitespace using Untangle because 
    # forgiving_compare()
    # ignores trivial whitespace.
    #@-at
    #@@c

    # Major change: 2/23/01: Untangle never updates doc parts.

    def update_def (self,name,part_number,head,code,tail,is_root_flag=False): # Doc parts are never updated!

        # g.trace(name,part_number,code)
        p = self.p ; body = p.b
        if not head: head = ""
        if not tail: tail = ""
        if not code: code = ""
        false_ret = head + code + tail, len(head) + len(code), False
        part, found = self.ust_lookup(name,part_number,is_root_flag,update_flag=True)
        if not found:
            return false_ret  # Not an error.
        ucode = g.toUnicode(part.code,self.encoding)
        #@    << Remove leading blank lines and comments from ucode >>
        #@+node:ekr.20031218072017.3574:<< Remove leading blank lines and comments from ucode >>
        #@+at
        # We formerly assumed that any leading comments came from an 
        # @doc part.
        # That became invalid when we stopped emitting doc parts 
        # into the derived file.
        # Leading comments are now treated as "code"
        #@-at
        #@@c

        i = g.skip_blank_lines(ucode,0)
        #j = g.skip_ws(ucode,i)
        # g.trace("comment,end,single:",self.comment,self.comment_end,self.line_comment)

        #@+at
        # if self.comment and self.comment_end:
        #     if ucode and g.match(ucode,j,self.comment):
        #         # Skip to the end of the block comment.
        #         i = j + len(self.comment)
        #         i = ucode.find(self.comment_end,i)
        #         if i == -1: ucode = None # An unreported problem 
        # in the user code.
        #         else:
        #             i += len(self.comment_end)
        #             i = g.skip_blank_lines(ucode,i)
        # elif self.line_comment:
        #     while ucode and g.match(ucode,j,self.line_comment):
        #         i = g.skip_line(ucode,i)
        #         i = g.skip_blank_lines(ucode,i)
        #         j = g.skip_ws(ucode,i)
        # # Only the value of ucode matters here.
        #@-at
        #@@c
        if ucode: ucode = ucode[i:]
        #@-node:ekr.20031218072017.3574:<< Remove leading blank lines and comments from ucode >>
        #@nl
        # g.trace(ucode)
        if not ucode or len(ucode) == 0:
            return false_ret # Not an error.
        if code and self.forgiving_compare(name,part,code,ucode):
            return false_ret # Not an error.
        # Update the body.
        g.es("***Updating:",p.h)
        i = g.skip_blank_lines(ucode,0)
        ucode = ucode[i:]
        ucode = ucode.rstrip()
        # Add the trailing whitespace of code to ucode.
        code2 = code.rstrip()
        trail_ws = code[len(code2):]
        ucode = ucode + trail_ws
        body = head + ucode + tail
        self.update_current_vnode(body)
        # g.trace("\nhead:",head,"\nucode:"ucode,"\ntail:",tail)
        return body, len(head) + len(ucode),True
    #@-node:ekr.20031218072017.3573:update_def (pass 2)
    #@+node:ekr.20031218072017.3575:update_current_vnode
    def update_current_vnode (self,s):

        """Called from within the Untangle logic to update the body text of self.p."""

        c = self.c ; p = self.p
        assert(self.p)
        c.setBodyString(p,s)

        c.setChanged(True)
        p.setDirty()
        p.setMarked()

        # 2010/02/02: was update_after_icons_changed.
        c.redraw_after_icons_changed()
    #@-node:ekr.20031218072017.3575:update_current_vnode
    #@-node:ekr.20031218072017.3544:untangle
    #@+node:ekr.20031218072017.3576:utility methods
    #@+at 
    #@nonl
    # These utilities deal with tangle ivars, so they should be 
    # methods.
    #@-at
    #@+node:ekr.20031218072017.3577:compare_section_names
    # Compares section names or root names.
    # Arbitrary text may follow the section name on the same line.

    def compare_section_names (self,s1,s2):

        # g.trace(g.get_line(s1,0),':',g.get_line(s2,0))
        if g.match(s1,0,"<<") or g.match(s1,0,"@<"):
            # Use a forgiving compare of the two section names.
            delim = g.choose(self.use_cweb_flag,"@>",">>")
            i1 = i2 = 0
            while i1 < len(s1) and i2 < len(s2):
                ch1 = s1[i1] ; ch2 = s2[i2]
                if g.is_ws(ch1) and g.is_ws(ch2):
                    i1 = g.skip_ws(s1,i1)
                    i2 = g.skip_ws(s2,i2)
                elif g.match(s1,i1,delim) and g.match(s2,i2,delim):
                    return True
                elif ch1.lower() == ch2.lower():
                    i1 += 1 ; i2 += 1
                else: return False
            return False
        else: # A root name.
            return s1 == s2
    #@-node:ekr.20031218072017.3577:compare_section_names
    #@+node:ekr.20031218072017.3578:copy
    def copy (self, s):

        assert(len(self.def_stack) > 0)
        dn = self.def_stack[-1] # Add the code at the top of the stack.
        dn.code += s
    #@-node:ekr.20031218072017.3578:copy
    #@+node:ekr.20031218072017.3579:error, pathError, warning
    def error (self,s):
        self.errors += 1
        g.es_error(g.translateString(s))

    def pathError (self,s):
        if not self.path_warning_given:
            self.path_warning_given = True
            self.error(s)

    def warning (self,s):
        g.es_error(g.translateString(s))
    #@-node:ekr.20031218072017.3579:error, pathError, warning
    #@+node:ekr.20031218072017.3580:is_end_of_directive
    # This function returns True if we are at the end of preprocessor directive.

    def is_end_of_directive (self,s,i):

        return g.is_nl(s,i) and not self.is_escaped(s,i)
    #@-node:ekr.20031218072017.3580:is_end_of_directive
    #@+node:ekr.20031218072017.3581:is_end_of_string
    def is_end_of_string (self,s,i,delim):

        return i < len(s) and s[i] == delim and not self.is_escaped(s,i)
    #@-node:ekr.20031218072017.3581:is_end_of_string
    #@+node:ekr.20031218072017.3582:is_escaped
    # This function returns True if the s[i] is preceded by an odd number of back slashes.

    def is_escaped (self,s,i):

        back_slashes = 0 ; i -= 1
        while i >= 0 and s[i] == '\\':
            back_slashes += 1
            i -= 1
        return (back_slashes & 1) == 1
    #@-node:ekr.20031218072017.3582:is_escaped
    #@+node:ekr.20031218072017.3583:is_section_name
    def is_section_name(self,s,i):

        kind = bad_section_name ; end = -1

        if self.use_cweb_flag :
            if g.match(s,i,"@<"):
                i, kind, end = self.skip_cweb_section_name(s,i)
        elif g.match(s,i,"<<"):
            i, kind, end = self.skip_noweb_section_name(s,i)

        # g.trace(kind,g.get_line(s,end))
        return i, kind, end
    #@-node:ekr.20031218072017.3583:is_section_name
    #@+node:ekr.20031218072017.3584:is_sentinel_line & is_sentinel_line_with_data
    #@+at 
    #@nonl
    # This function returns True if i points to a line a sentinel 
    # line of one of the following forms:
    # 
    # start_sentinel <<section name>> end_sentinel
    # start_sentinel <<section name>> (n of m) end_sentinel
    # start_sentinel -- end -- <<section name>> end_sentinel
    # start_sentinel -- end -- <<section name>> (n of m) 
    # end_sentinel
    # 
    # start_sentinel: the string that signals the start of sentinel 
    # lines\
    # end_sentinel:   the string that signals the endof sentinel 
    # lines.
    # 
    # end_sentinel may be None,indicating that sentinel lines end 
    # with a newline.
    # 
    # Any of these forms may end with (!newline), indicating that 
    # the section reference was not followed by a newline in the 
    # orignal text.  We set nl_flag to False if such a string is 
    # seen. The name argument contains the section name.
    # 
    # The valid values of kind param are:
    # 
    # non_sentinel_line,   # not a sentinel line.
    # start_sentinel_line, #   /// <section name> or /// <section 
    # name>(n of m)
    # end_sentinel_line  //  /// -- end -- <section name> or /// -- 
    # end -- <section name>(n of m).
    #@-at
    #@@c
    def is_sentinel_line (self,s,i):

        result,i,kind,name,part,of,end,nl_flag = self.is_sentinel_line_with_data(s,i)
        return result

    def is_sentinel_line_with_data (self,s,i):

        start_sentinel = self.sentinel
        end_sentinel = self.sentinel_end
        #@    << Initialize the return values >>
        #@+node:ekr.20031218072017.3585:<< Initialize the return values  >>
        name = end = None
        part = of = 1
        kind = non_sentinel_line
        nl_flag = True
        false_data = (False,i,kind,name,part,of,end,nl_flag)
        #@-node:ekr.20031218072017.3585:<< Initialize the return values  >>
        #@nl
        #@    << Make sure the line starts with start_sentinel >>
        #@+node:ekr.20031218072017.3586:<< Make sure the line starts with start_sentinel >>
        if g.is_nl(s,i): i = g.skip_nl(s,i)
        i = g.skip_ws(s,i)

        # 4/18/00: We now require an exact match of the sentinel.
        if g.match(s,i,start_sentinel):
            i += len(start_sentinel)
        else:
            return false_data
        #@-node:ekr.20031218072017.3586:<< Make sure the line starts with start_sentinel >>
        #@nl
        #@    << Set end_flag if we have -- end -- >>
        #@+node:ekr.20031218072017.3587:<< Set end_flag if we have -- end -- >>
        # If i points to "-- end --", this code skips it and sets end_flag.

        end_flag = False
        i = g.skip_ws(s,i)
        if g.match(s,i,"--"):
            while i < len(s) and s[i] == '-':
                i += 1
            i = g.skip_ws(s,i)
            if not g.match(s,i,"end"):
                return false_data # Not a valid sentinel line.
            i += 3 ; i = g.skip_ws(s,i)
            if not g.match(s,i,"--"):
                return false_data # Not a valid sentinel line.
            while i < len(s) and s[i] == '-':
                i += 1
            end_flag = True
        #@-node:ekr.20031218072017.3587:<< Set end_flag if we have -- end -- >>
        #@nl
        #@    << Make sure we have a section reference >>
        #@+node:ekr.20031218072017.3588:<< Make sure we have a section reference >>
        i = g.skip_ws(s,i)

        if (self.use_noweb_flag and g.match(s,i,"<<") or
            self.use_cweb_flag  and g.match(s,i,"@<") ):

            j = i ; i, kind, end = self.skip_section_name(s,i)
            if kind != section_ref:
                return false_data
            name = s[j:i]
        else:
            return false_data
        #@-node:ekr.20031218072017.3588:<< Make sure we have a section reference >>
        #@nl
        #@    << Set part and of if they exist >>
        #@+node:ekr.20031218072017.3589:<< Set part and of if they exist >>
        # This code handles (m of n), if it exists.
        i = g.skip_ws(s,i)
        if g.match(s,i,'('):
            j = i
            i += 1 ; i = g.skip_ws(s,i)
            i, part = self.scan_short_val(s,i)
            if part == -1:
                i = j # back out of the scanning for the number.
                part = 1
            else:
                i = g.skip_ws(s,i)
                if not g.match(s,i,"of"):
                    return false_data
                i += 2 ; i = g.skip_ws(s,i)
                i, of = self.scan_short_val(s,i)
                if of == -1:
                    return false_data
                i = g.skip_ws(s,i)
                if g.match(s,i,')'):
                    i += 1 # Skip the paren and do _not_ return.
                else:
                    return false_data
        #@-node:ekr.20031218072017.3589:<< Set part and of if they exist >>
        #@nl
        #@    << Set nl_flag to False if !newline exists >>
        #@+node:ekr.20031218072017.3590:<< Set nl_flag to false if !newline exists >>
        line = "(!newline)"
        i = g.skip_ws(s,i)
        if g.match(s,i,line):
            i += len(line)
            nl_flag = False
        #@-node:ekr.20031218072017.3590:<< Set nl_flag to false if !newline exists >>
        #@nl
        #@    << Make sure the line ends with end_sentinel >>
        #@+node:ekr.20031218072017.3591:<< Make sure the line ends with end_sentinel >>
        i = g.skip_ws(s,i)
        if end_sentinel:
            # Make sure the line ends with the end sentinel.
            if g.match(s,i,end_sentinel):
                i += len(end_sentinel)
            else:
                return false_data

        end = i # Show the start of the whitespace.
        i = g.skip_ws(s,i)
        if i < len(s) and not g.is_nl(s,i):
            return false_data
        #@-node:ekr.20031218072017.3591:<< Make sure the line ends with end_sentinel >>
        #@nl
        kind = g.choose(end_flag,end_sentinel_line,start_sentinel_line)
        return True,i,kind,name,part,of,end,nl_flag
    #@-node:ekr.20031218072017.3584:is_sentinel_line & is_sentinel_line_with_data
    #@+node:ekr.20031218072017.3592:push_new_def_node
    # This function pushes a new def_node on the top of the section stack.

    def push_new_def_node (self,name,indent,part,of,nl_flag):

        # g.trace(name,part)
        node = def_node(name,indent,part,of,nl_flag,None)
        self.def_stack.append(node)
    #@-node:ekr.20031218072017.3592:push_new_def_node
    #@+node:ekr.20031218072017.3593:scan_short_val
    # This function scans a positive integer.
    # returns (i,val), where val == -1 if there is an error.

    def scan_short_val (self,s,i):


        if i >= len(s) or not s[i].isdigit():
            return i, -1
        j = i
        while i < len(s) and s[i].isdigit():
            i += 1
        val = int(s[j:i])
        # g.trace(s[j:i],val)
        return i, val
    #@nonl
    #@-node:ekr.20031218072017.3593:scan_short_val
    #@+node:ekr.20031218072017.3594:setRootFromHeadline
    def setRootFromHeadline (self,p):

        s = p.h

        if s[0:5] == "@root":
            i,self.start_mode = g.scanAtRootOptions(s,0)
            i = g.skip_ws(s,i)

            if i < len(s): # Non-empty file name.
                # self.root_name must be set later by token_type().
                self.root = s[i:]
                # implement headline @root (but create unit tests first):
                # arguments: name, is_code, is_doc
                # st_enter_root_name(self.root, False, False)
    #@-node:ekr.20031218072017.3594:setRootFromHeadline
    #@+node:ekr.20031218072017.1259:setRootFromText
    #@+at 
    #@nonl
    # This code skips the file name used in @root directives.
    # 
    # File names may be enclosed in < and > characters, or in double 
    # quotes.  If a file name is not enclosed be these delimiters it 
    # continues until the next newline.
    #@-at
    #@@c
    def setRootFromText(self,s,report_errors=True):

        # g.trace(s)
        self.root_name = None
        i,self.start_mode = g.scanAtRootOptions(s,0)
        i = g.skip_ws(s,i)

        if i >= len(s): return i
        # Allow <> or "" as delimiters, or a bare file name.
        if s[i] == '"':
            i += 1 ; delim = '"'
        elif s[i] == '<':
            i += 1 ; delim = '>'
        else: delim = '\n'

        root1 = i # The name does not include the delimiter.
        while i < len(s) and s[i] != delim and not g.is_nl(s,i):
            i += 1
        root2 = i

        if delim != '\n' and not g.match(s,i,delim):
            if report_errors:
                g.scanError("bad filename in @root " + s[:i])
        else:
            self.root_name = s[root1:root2].strip()
        return i
    #@-node:ekr.20031218072017.1259:setRootFromText
    #@+node:ekr.20031218072017.3595:skip_CWEB_section_name
    #@+at 
    #@nonl
    # This function skips past a section name that starts with @< 
    # and ends with @>. This code also skips any = following the 
    # section name.
    # 
    # Returns (i, kind, end), where kind is:
    # 
    #     bad_section_name:  @ < with no matching @ >
    #     section_ref: @ < name @ >
    #     section_def: @ < name @ > =
    # 
    # Unlike noweb, bad section names generate errors.
    #@-at
    #@@c

    def skip_cweb_section_name(self,s,i):

        j = i # Used for error message.
        kind = bad_section_name ; end = -1
        runon = False ; empty_name = True
        assert(s[i:i+2]=="@<")
        i += 2
        while i < len(s):
            if g.match(s,i,"@>="):
                i += 3 ; end = i-1 ; kind = section_def ; break
            elif g.match(s,i,"@>"):
                i += 2 ; end = i ; kind = section_ref ; break
            elif g.match(s,i,"@<"):
                runon = True ; break
            elif g.match(s,i,"@@"): i += 2
            elif g.is_ws_or_nl(s,i): i += 1
            else:
                i += 1 ; empty_name = False

        if empty_name:
            g.scanError("empty CWEB section name: " + s[j:i])
            return i, bad_section_name, -1
        elif i >= len(s) or runon:
            g.scanError("Run on CWEB section name: " + s[j:i])
            return i, bad_section_name, -1
        else:
            return i, kind, end
    #@-node:ekr.20031218072017.3595:skip_CWEB_section_name
    #@+node:ekr.20031218072017.3596:skip_noweb_section_name
    #@+at 
    #@nonl
    # This function skips past a section name that starts with < < 
    # and might end with > > or > > =. The entire section name must 
    # appear on the same line.
    # 
    # Note: this code no longer supports extended noweb mode.
    # 
    # Returns (i, kind, end),
    #     end indicates the end of the section name itself (not 
    # counting the =).
    #     kind is one of:
    #         bad_section_name: "no matching ">>" or ">>"  This is 
    # _not_ a user error!
    #         section_ref: < < name > >
    #         section_def: < < name > > =
    #         at_root:     < < * > > =
    #@-at
    #@@c
    def skip_noweb_section_name(self,s,i):

        assert(g.match(s,i,"<<"))
        i += 2
        j = i # Return this value if no section name found.
        kind = bad_section_name ; end = -1 ; empty_name = True

        # Scan for the end of the section name.
        while i < len(s) and not g.is_nl(s,i):
            if g.match(s,i,">>="):
                i += 3 ; end = i - 1 ; kind = section_def ; break
            elif g.match(s,i,">>"):
                i += 2 ; end = i ; kind = section_ref ; break
            elif g.is_ws_or_nl(s,i):
                i += 1
            elif empty_name and s[i] == '*':
                empty_name = False
                i = g.skip_ws(s,i+1) # skip the '*'
                if g.match(s,i,">>="):
                    i += 3 ; end = i - 1 ; kind = at_root ; break
            else:
                i += 1 ; empty_name = False

        if empty_name:
            kind = bad_section_name
        if kind == bad_section_name:
            i = j
        return i, kind, end
    #@-node:ekr.20031218072017.3596:skip_noweb_section_name
    #@+node:ekr.20031218072017.3597:skip_section_name
    # Returns a tuple (i, kind, end)

    def skip_section_name(self,s,i):

        if self.use_noweb_flag:
            return self.skip_noweb_section_name(s,i)
        else:
            return self.skip_cweb_section_name(s,i)
    #@-node:ekr.20031218072017.3597:skip_section_name
    #@+node:ekr.20031218072017.3598:standardize_name
    def standardize_name (self,name):

        """Removes leading and trailing brackets, converts white space to a single blank and converts to lower case."""

        # Convert to lowercase.
        # Convert whitespace to a single space.
        name = name.lower().replace('\t',' ').replace('  ',' ')

        # Remove leading '<'
        i = 0 ; n = len(name)
        while i < n and name[i] == '<':
            i += 1
        j = i

        # Find the first '>'
        while i < n and name [i] != '>':
            i += 1
        name = name[j:i].strip()

        return name
    #@-node:ekr.20031218072017.3598:standardize_name
    #@+node:ekr.20080923124254.16:tangle.scanAllDirectives
    def scanAllDirectives(self,p):

        """Scan vnode p and p's ancestors looking for directives,
        setting corresponding tangle ivars and globals.
        """

        c = self.c
        self.init_directive_ivars()
        if p:
            s = p.b
            #@        << Collect @first attributes >>
            #@+node:ekr.20080923124254.17:<< Collect @first attributes >>
            #@+at 
            #@nonl
            # Stephen P. Schaefer 9/13/2002: Add support for @first.
            # Unlike other root attributes, does *NOT* inherit from 
            # parent nodes.
            #@-at
            #@@c
            tag = "@first"
            sizeString = len(s) # DTHEIN 13-OCT-2002: use to detect end-of-string
            i = 0
            while 1:
                # DTHEIN 13-OCT-2002: directives must start at beginning of a line
                if not g.match_word(s,i,tag):
                    i = g.skip_line(s,i)
                else:
                    i = i + len(tag)
                    j = i = g.skip_ws(s,i)
                    i = g.skip_to_end_of_line(s,i)
                    if i>j:
                        self.first_lines += s[j:i] + '\n'
                    i = g.skip_nl(s,i)
                if i >= sizeString:  # DTHEIN 13-OCT-2002: get out when end of string reached
                    break
            #@-node:ekr.20080923124254.17:<< Collect @first attributes >>
            #@nl

        # delims = (self.single_comment_string,self.start_comment_string,self.end_comment_string)
        lang_dict = {'language':self.language,'delims':None,} # Delims not used

        table = (
            ('encoding',    self.encoding,  g.scanAtEncodingDirectives),
            ('lang-dict',   lang_dict,      g.scanAtCommentAndAtLanguageDirectives),
            ('lineending',  None,           g.scanAtLineendingDirectives),
            ('pagewidth',   c.page_width,   g.scanAtPagewidthDirectives),
            ('path',        None,           c.scanAtPathDirectives), 
            ('tabwidth',    c.tab_width,    g.scanAtTabwidthDirectives),
        )

        # Set d by scanning all directives.
        aList = g.get_directives_dict_list(p)
        d = {}
        for key,default,func in table:
            val = func(aList)
            d[key] = g.choose(val is None,default,val)

        # Post process.
        lang_dict       = d.get('lang-dict')
        lineending      = d.get('lineending')
        if lineending:
            self.output_newline = lineending
        self.encoding             = d.get('encoding')
        self.language             = lang_dict.get('language')
        self.page_width           = d.get('pagewidth')
        self.tangle_directory     = d.get('path')
        self.tab_width            = d.get('tabwidth')

        # Handle the print-mode directives.
        self.print_mode = None
        for d in aList:
            for key in ('verbose','terse','quiet','silent'):
                if d.get(key) is not None:
                    self.print_mode = key ; break
            if self.print_mode: break
        if not self.print_mode: self.print_mode = 'verbose'

        # 2010/01/27: bug fix: make sure to set the ivars.
        # 2010/06/02: allow @comment (which sets delims) in absence of @language
        if self.language:
            delim1,delim2,delim3 = g.set_delims_from_language(self.language)
        if lang_dict and lang_dict.get('delims'):
            delim1,delim2,delim3 = lang_dict.get('delims')
        self.single_comment_string = delim1
        self.start_comment_string = delim2
        self.end_comment_string = delim3

        # g.trace(self.tangle_directory)

        # For unit testing.
        return {
            "encoding"  : self.encoding,
            "language"  : self.language,
            "lineending": self.output_newline,
            "pagewidth" : self.page_width,
            "path"      : self.tangle_directory,
            "tabwidth"  : self.tab_width,
        }
    #@-node:ekr.20080923124254.16:tangle.scanAllDirectives
    #@+node:ekr.20031218072017.3599:token_type
    def token_type(self,s,i,report_errors=True):

        """This method returns a code indicating the apparent kind of token at the position i.

        The caller must determine whether section definiton tokens are valid.

        returns (kind, end) and sets global root_name using setRootFromText()."""

        kind = plain_line ; end = -1
        if self.use_noweb_flag:
            #@        << set token_type in noweb mode >>
            #@+node:ekr.20031218072017.3600:<< set token_type in noweb mode >>
            if g.match(s,i,"<<"):
                i, kind, end = self.skip_section_name(s,i)
                if kind == bad_section_name:
                    kind = plain_line # not an error.
                elif kind == at_root:
                    assert(self.head_root == None)
                    if self.head_root:
                        self.setRootFromText(self.head_root,report_errors)
                    else:
                        kind = bad_section_name # The warning has been given.
            elif g.match(s,i,"@ ") or g.match(s,i,"@\t") or g.match(s,i,"@\n"):
                # 10/30/02: Only @doc starts a noweb doc part in raw cweb mode.
                kind = g.choose(self.raw_cweb_flag,plain_line,at_doc)
            elif g.match(s,i,"@@"): kind = at_at
            elif i < len(s) and s[i] == '@': kind = at_other
            else: kind = plain_line
            #@-node:ekr.20031218072017.3600:<< set token_type in noweb mode >>
            #@nl
        else:
            #@        << set token_type for CWEB mode >>
            #@+node:ekr.20031218072017.3601:<< set token_type for CWEB mode >>
            i = g.skip_ws(s,i)
            if g.match(s,i,"@*") or g.match(s,i,"@ "): kind = at_doc
            elif g.match(s,i,"@<"): i, kind, end = self.skip_section_name(s,i)
            elif g.match(s,i,"@@"): kind = at_at
            elif g.match_word(s,i,"@c") or g.match_word(s,i,"@p"): kind = at_code
            elif i < len(s) and s[i] == '@':
                if   i + 1 >= len(s): kind = at_doc
                elif i + 1 < len(s) and s[i+1] not in string.ascii_letters:
                    kind = at_web
                else: kind = at_other # Set kind later
            else: kind = plain_line
            #@-node:ekr.20031218072017.3601:<< set token_type for CWEB mode >>
            #@nl
        if kind == at_other :
            #@        << set kind for directive >>
            #@+node:ekr.20031218072017.3602:<< set kind for directive >>
            # This code will return at_other for any directive other than those listed.

            if g.match_word(s,i,"@c"):
                # 10/30/02: Only @code starts a code section in raw cweb mode.
                kind = g.choose(self.raw_cweb_flag,plain_line,at_code)
            else:
                for name, theType in [
                    ("@chapter", at_chapter),
                    ("@code", at_code),
                    ("@doc", at_doc),
                    ("@root", at_root),
                    ("@section", at_section) ]:
                    if g.match_word(s,i,name):
                        kind = theType ; break

            if self.raw_cweb_flag and kind == at_other:
                # 10/30/02: Everything else is plain text in raw cweb mode.
                kind = plain_line

            if kind == at_root:
                end = self.setRootFromText(s[i:],report_errors)
            #@-node:ekr.20031218072017.3602:<< set kind for directive >>
            #@nl
        # g.trace(kind,g.get_line(s,i))
        return kind, end
    #@-node:ekr.20031218072017.3599:token_type
    #@-node:ekr.20031218072017.3576:utility methods
    #@-others

class tangleCommands (baseTangleCommands):
    """A class that implements Leo' tangle and untangle commands."""
    pass
#@-node:ekr.20031218072017.3465:class tangleCommands methods
#@-others
#@-node:ekr.20031218072017.3446:@thin leoTangle.py
#@-leo
