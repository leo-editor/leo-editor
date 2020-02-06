#@+leo-ver=5-thin
#@+node:ekr.20031218072017.3446: * @file leoTangle.py
'''
Support for @root and Leo's tangle and untangle commands.

Everything in this file is deprecated, but will remain "forever".
'''
import leo.core.leoGlobals as g
import os
#@+<< about Tangle and Untangle >>
#@+node:ekr.20031218072017.2411: ** << About Tangle and Untangle >>
#@@root directive. The stack never becomes empty because of the entry
#@+at
# The Tangle command translates the selected @root tree into one or more
# well-formatted source files. The outline should contain directives,
# sections references and section definitions, as described in Chapter
# 4. The Untangle command is essentially the reverse of the Tangle
# command. The Tangle command creates a derived file from an @root tree;
# the Untangle command incorporates changes made to derived files back
# into the @root tree.
# 
# The Tangle command operates in two passes. The first pass discovers
# the complete definitions of all sections and places these definitions
# in a Tangle Symbol Table. The first pass also makes a list of root
# sections. Definitions can appear in any order, so we must scan the
# entire input file to know whether any particular definition has been
# completed.
# 
# Tangle's second pass creates one file for each @root node. Tangle
# rescans each section in the list of roots, copying the root text to
# the output and replacing each section reference by the section's
# definition. This is a recursive process because any definition may
# contain other references. We can not allow a section to be defined in
# terms of itself, either directly or indirectly. We check for such
# illegally recursive definitions in pass 2 using the section stack
# class. Tangle indicates where sections begin and end using comment
# lines called sentinel lines. The sentinels used predate the formats
# described in the "Format of external files" appendix.
# 
# The key design principle of the Tangle command is this: Tangle must
# output newlines in a context-free manner. That is, Tangle must never
# output conditional newlines, either directly or indirectly. Without
# this rule Untangle could not determine whether to skip or copy
# newlines.
# 
# The Tangle command increases the indentation level of a section
# expansion the minimum necessary to align the section expansion with
# the surrounding code. In essence, this scheme aligns all section
# expansions with the line of code in which the reference to the section
# occurs. In some cases, several nested sections expansions will have
# the same indentation level. This can occur, for example, when a
# section reference in an outline occurs at the left margin of the
# outline.
# 
# This scheme is probably better than more obvious schemes that indent
# more "consistently." Such schemes would produce too much indentation
# for deeply nested outlines. The present scheme is clear enough and
# avoids indentation wherever possible, yet indents sections adequately.
# End sentinel lines make this scheme work by making clear where the
# expansion of one section ends and the expansion of a containing
# section resumes.
# 
# Tangle increases indentation if the section reference does not start a
# line. Untangle is aware of this hack and adjusts accordingly. This
# extra indentation handles several common code idioms, which otherwise
# would create under-indented code. In short, Tangle produces highly
# readable, given the necessity of preserving newlines for Untangle.
# 
# Untangle is inherently complex. It must do a perfect job of updating
# the outline, especially whitespace, from expansions of section
# definitions created by the Tangle command. Such expansions need not be
# identical because they may have been generated at different levels of
# indentation. The Untangle command can not assume that all expansions
# of a section will be identical in the derived file; within the derived
# file, the programmer may have made incompatible changes to two
# different expansions of the same section. Untangle must check to see
# that all expansions of a section are "equivalent". As an added
# complication, derived files do not contain all the information found
# in @root trees. @root trees may contain headlines that generate no
# code at all. Also, an outline may define a section in several ways:
# with an @c or @code directive or with a section definition line. To be
# useful, Untangle must handle all these complications flawlessly.
# 
# Untangle operates in three passes. The first pass builds a symbol
# table in the same way that Tangle does. The key information there
# informs how the second pass finds definitions in the derived file: to
# support multi-language files (e.g., javascript embedded in html) the
# second pass needs to know what comment delimiters to look for as it
# discovers sentinels in the derived file. Using comment delimiters as
# suggested by the first pass, it uses the sentinels to find section
# parts and enters them into the Untangle Symbol Table, or UST.
# Definitions often include references to other sections, so definitions
# often include nested definitions of referenced sections. The second
# pass of Untangle uses a definition stack to keep track of nested
# definitions. The top of the stack represents the definition following
# the latest reference, except for the very first entry pushed on the
# stack, which represents the code in the outline that contains the
# for the @root section. All definitions of a section should
# match--otherwise there is an inconsistent definition. This pass uses a
# forgiving compare routine that ignores differences that do not affect
# the meaning of a program.
# 
# Untangle's third pass enters definitions from the outline into a
# second Tangle Symbol Table, or TST. The third pass simultaneously
# updates all sections in the outline whose definition in the new TST
# does not match the definition in the UST. The central coding insight
# of the Untangle command is that the second pass of Untangle is almost
# identical to the first pass of Tangle! That is, Tangle and Untangle
# share key parts of code, namely the skip_body() method and its allies.
# Just when skip_body() enters a definition into the symbol table, all
# the information is present that Untangle needs to update that
# definition.
#@-<< about Tangle and Untangle >>
#@+<< constants >>
#@+node:ekr.20031218072017.3447: ** << constants >>
max_errors = 20
# All these must be defined together, because they form a single enumeration.
# Some of these are used by utility functions.
# Used by token_type().
plain_line = 1 # all other lines
at_at = 2 # double-at sign.
at_chapter = 3 # @chapter
# at_c     = 4 # @c in noweb mode
at_code = 5 # @code, or @c or @p in CWEB mode.
at_doc = 6 # @doc
at_other = 7 # all other @directives
at_root = 8 # @root or noweb * sections
at_section = 9 # @section
# at_space = 10 # @space
at_web = 11 # any CWEB control code, except at_at.
# Returned by self.skip_section_name() and allies and used by token_type.
bad_section_name = 12 # < < with no matching > >
section_ref = 13 # < < name > >
section_def = 14 # < < name > > =
# Returned by is_sentinal_line.
non_sentinel_line = 15
start_sentinel_line = 16
end_sentinel_line = 17
# Stephen P. Schaefer 9/13/2002
# add support for @first
at_last = 18
#@-<< constants >>
#@+others
#@+node:ekr.20031218072017.3448: ** node classes
#@+node:ekr.20031218072017.3449: *3* class TstNode
class TstNode:
    #@+others
    #@+node:ekr.20031218072017.3450: *4* TstNode.__init__
    def __init__(self, name, root_flag):

        self.name = name
        self.is_root = root_flag
        self.referenced = False
        self.parts = []
        self.delims = None
    #@+node:ekr.20031218072017.3451: *4* TstNode.__repr__
    def __repr__(self):
        return "TstNode:" + self.name
    #@+node:sps.20100624231018.12083: *4* TstNode.dump
    def dump(self):
        s = ("\nsection: " + self.name +
            ", referenced:" + str(self.referenced) +
            ", is root:" + str(self.is_root))
        if self.parts:
            s += "\n----- parts of " + g.angleBrackets(self.name)
            n = 1 # part list is in numeric order
            for part in self.parts:
                s += "\n----- Part " + str(n)
                n += 1
                s += "\ndoc:  [" + repr(part.doc) + "]"
                s += "\ncode: [" + repr(part.code) + "]"
                s += "\ndelims: <%s><%s><%s>" % part.delims
                for ref in part.reflist():
                    s += "\n    ref: [" + repr(ref.name) + "]"
            s += "\n----- end of partList\n"
        return s
    #@-others
#@+node:ekr.20031218072017.3452: *3* class PartNode
class PartNode:
    #@+others
    #@+node:ekr.20031218072017.3453: *4* PartNode.__init__
    def __init__(self, name, code, doc, is_root, is_dirty, delims):

        self.name = name # Section or file name.
        self.code = code # The code text.
        self.doc = doc # The doc text.
        self.is_dirty = is_dirty # True: VNode for body text is dirty.
        self.is_root = is_root # True: name is a root name.
        self.delims = delims
        self.refs = []
    #@+node:ekr.20031218072017.3454: *4* PartNode.__repr__
    def __repr__(self):
        return "PartNode:" + self.name
    #@+node:sps.20100622084732.16656: *4* PartNode.reflist
    def reflist(self, refs=False):
        if refs:
            self.refs = refs
        return self.refs
    #@-others
#@+node:ekr.20031218072017.3455: *3* class UstNode
class UstNode:
    #@+others
    #@+node:ekr.20031218072017.3456: *4* UstNode.__init__
    #@+at
    # The text has been masssaged so that 1) it contains no leading
    # indentation and 2) all code arising from section references have been
    # replaced by the reference line itself. Text for all copies of the same
    # part can differ only in non-critical white space.
    #@@c

    def __init__(self, name, code, part, of, nl_flag, update_flag):

        self.name = name # section name
        self.parts = {} # parts dict
        self.code = code # code text
        self.part = part # n in "(part n of m)" or zero.
        self.of = of # m in "(part n of m)" or zero.
        self.nl_flag = nl_flag # True: section starts with a newline.
        self.update_flag = update_flag # True: section corresponds to a section in the outline.
    #@+node:ekr.20031218072017.3457: *4* UstNode.__repr__
    def __repr__(self):
        return "UstNode:" + self.name
    #@+node:sps.20100624231018.12084: *4* UstNode.dump
    def dump(self):
        s = "name: %s" % repr(self.name)
        for part in self.parts.values():
            s += "\n----- part %s of %s -----\n" % (repr(part.part), repr(part.of))
            s += repr(g.get_line(part.code, 0))
            s += "\nupdate_flag: %s" % repr(part.update_flag)
        return s
    #@-others
#@+node:ekr.20031218072017.3458: *3* class DefNode
class DefNode:
    #@+others
    #@+node:ekr.20031218072017.3459: *4* DefNode.__init__
    #@+at
    # The text has been masssaged so that 1) it contains no leading
    # indentation and 2) all code arising from section references have been
    # replaced by the reference line itself. Text for all copies of the same
    # part can differ only in non-critical white space.
    #@@c

    def __init__(self, name, indent, part, of, nl_flag, code):

        self.name = name
        self.indent = indent
        self.code = code
        if self.code is None: self.code = ""
        self.part = part
        self.of = of
        self.nl_flag = nl_flag
    #@+node:ekr.20031218072017.3460: *4* DefNode.__repr__
    def __repr__(self):
        return "DefNode:" + self.name
    #@-others
#@+node:ekr.20031218072017.3461: *3* class RootAttributes (Stephen P. Schaefer)
#@+at Stephen P. Schaefer, 9/2/2002
# Collect the root node specific attributes in an
# easy-to-use container.
#@@c

class RootAttributes:
    #@+others
    #@+node:ekr.20031218072017.3462: *4* RootAttributes.__init__
    #@+at Stephen P. Schaefer, 9/2/2002
    # Keep track of the attributes of a root node
    #@@c

    def __init__(self, tangle_state):

        self.language = tangle_state.language
        self.use_header_flag = tangle_state.use_header_flag
        self.print_mode = tangle_state.print_mode
        # of all the state variables, this one isn't set in TangleCommands.__init__
        # peculiar
        try:
            self.path = tangle_state.path
        except AttributeError:
            self.path = None
        self.page_width = tangle_state.page_width
        self.tab_width = tangle_state.tab_width
        self.first_lines = tangle_state.first_lines # Stephen P. Schaefer 9/13/2002
    #@+node:ekr.20031218072017.3464: *4* RootAttributes.__repr__
    def __repr__(self):
        return ("RootAttributes: language: " + self.language +
            ", use_header_flag: " + repr(self.use_header_flag) +
            ", print_mode: " + self.print_mode +
            ", path: " + self.path +
            ", page_width: " + repr(self.page_width) +
            ", tab_width: " + repr(self.tab_width) +
            # Stephen P. Schaefer 9/13/2002
            ", first_lines: " + self.first_lines)
    #@-others
#@+node:ekr.20031218072017.3465: ** class TangleCommands
class BaseTangleCommands:
    """The base class for Leo's tangle and untangle commands."""
    #@+others
    #@+node:sps.20100629094515.20943: *3* class RegexpForLanguageOrComment
    class RegexpForLanguageOrComment:
        import re
        regex = re.compile(r'''
            ^(
                (?P<language>
                    @language\s[^\n]*
                ) |
                (?P<comment>
                    @comment\s[^\n]*
                ) |
                (
                    [^\n]*\n
                )
            )*'''         , re.VERBOSE)
    #@+node:ekr.20031218072017.1356: *3* tangle.Birth
    def __init__(self, c):
        self.c = c
        self.init_ivars()

    def init_ivars(self):
        c = self.c
        g.app.scanErrors = 0
        #@+<< init tangle ivars >>
        #@+node:ekr.20031218072017.1357: *4* << init tangle ivars >>
        # Various flags and counts...
        self.errors = 0 # The number of errors seen.
        # self.tangling = True # True if tangling, False if untangling.
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
        #@+at Symbol tables: the TST (Tangle Symbol Table) contains all section names in the outline.
        # The UST (Untangle Symbol Table) contains all sections defined in the derived file.
        #@@c
        self.tst = {}
        self.ust = {}
        # The section stack for Tangle and the definition stack for Untangle.
        self.section_stack = []
        self.def_stack = []
        #@+at
        # The list of all roots. The symbol table routines add roots to self
        # list during pass 1. Pass 2 uses self list to generate code for all
        # roots.
        #@@c
        self.root_list = []
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
        # The following records whether we have seen an @code directive in a
        # body text. If so, an @code represents < < header name > > = and it is
        # valid to continue a section definition.
        #@@c
        self.code_seen = False # True if @code seen in body text.
        # Support of output_newline option
        self.output_newline = g.getOutputNewline(c=c)
        #@-<< init tangle ivars >>
        #@+<< init untangle ivars >>
        #@+node:ekr.20031218072017.1358: *4* << init untangle ivars >>
        #@+at Untangle vars used while comparing.
        #@@c
        self.line_comment = self.comment = self.comment_end = None
        self.comment2 = self.comment2_end = None
        self.string1 = self.string2 = self.verbatim = None
        self.message = None # forgiving compare message.
        #@-<< init untangle ivars >>

    # Called by scanAllDirectives

    def init_directive_ivars(self):
        c = self.c
        #@+<< init directive ivars >>
        #@+node:ekr.20031218072017.1359: *4* << init directive ivars >> (tangle)
        # Global options
        self.page_width = c.page_width
        self.tab_width = c.tab_width
        # Get settings from reload_settings.
        self.output_doc_flag = False
        self.tangle_batch_flag = False
        self.untangle_batch_flag = False
        self.use_header_flag = False
        # Default tangle options.
        self.tangle_directory = None # Initialized by scanAllDirectives
        # Default tangle language
        if c.target_language: c.target_language = c.target_language.lower()
        self.language = c.target_language
        if 0: # debug
            import sys
            g.es(f"TangleCommands.languague: {self.language} at header {self.p!r}")
            f = sys._getframe(1)
            g.es("caller: " + f.f_code.co_name)
            f = sys._getframe(2)
            g.es("caller's caller: " + f.f_code.co_name)
        # Abbreviations for self.language.
        # Warning: these must also be initialized in tangle.scanAllDirectives.
        self.raw_cweb_flag = (self.language == "cweb") # A new ivar.
        # Set only from directives.
        self.print_mode = "verbose"
        self.first_lines = ""
        self.encoding = c.config.default_derived_file_encoding # 2/21/03
        self.output_newline = g.getOutputNewline(c=c) # 4/24/03: initialize from config settings.
        #@-<< init directive ivars >>
        
    def reload_settings(self):
        c = self.c
        self.output_doc_flag = c.config.getBool('output-doc-flag')
        self.tangle_batch_flag = c.config.getBool('tangle-batch-flag')
        self.untangle_batch_flag = c.config.getBool('untangle-batch-flag')
        self.use_header_flag = c.config.getBool('use-header-flag')
        
    reloadSettings = reload_settings
    #@+node:ekr.20031218072017.3467: *3* top level
    #@+at Only top-level drivers initialize ivars.
    #@+node:ekr.20031218072017.3468: *4* cleanup
    # This code is called from tangleTree and untangleTree.

    def cleanup(self):
        # Reinitialize the symbol tables and lists.
        self.tst = {}
        self.ust = {}
        self.root_list = []
        self.def_stack = []
    #@+node:ekr.20031218072017.3470: *4* initTangleCommand
    def initTangleCommand(self):
        c = self.c
        c.endEditing()
        if not g.unitTesting:
            g.es("tangling...")
        self.init_ivars()
        self.tangling = True
    #@+node:ekr.20031218072017.3471: *4* initUntangleCommand
    def initUntangleCommand(self):
        c = self.c
        c.endEditing()
        if not g.unitTesting:
            g.es("untangling...")
        self.init_ivars()
    #@+node:ekr.20031218072017.3472: *4* tangle
    def tangle(self, event=None, p=None):
        c = self.c
        if not p: p = c.p
        self.initTangleCommand()
        # Paul Paterson's patch.
        if not self.tangleTree(p, report_errors=True):
            g.es("looking for a parent to tangle...")
            while p:
                assert(self.head_root is None)
                d = g.get_directives_dict(p, [self.head_root])
                if 'root' in d:
                    g.es("tangling parent")
                    self.tangleTree(p, report_errors=True)
                    break
                p.moveToParent()
        if not g.unitTesting:
            g.es("tangle complete")
    #@+node:ekr.20031218072017.3473: *4* tangleAll
    def tangleAll(self, event=None):
        c = self.c
        self.initTangleCommand()
        has_roots = False
        for p in c.rootPosition().self_and_siblings():
            ok = self.tangleTree(p, report_errors=False)
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
    #@+node:ekr.20031218072017.3474: *4* tangleMarked
    def tangleMarked(self, event=None):
        c = self.c; p = c.rootPosition()
        c.clearAllVisited() # No roots have been tangled yet.
        self.initTangleCommand()
        any_marked = False
        while p:
            is_ignore, i = g.is_special(p.b, "@ignore")
            # Only tangle marked and unvisited nodes.
            if is_ignore:
                p.moveToNodeAfterTree()
            elif p.isMarked():
                ok = self.tangleTree(p, report_errors=False)
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
    #@+node:sps.20100618004337.20865: *4* tanglePass1
    # Traverses the tree whose root is given, handling each headline and associated body text.

    def tanglePass1(self, p_in, delims):
        """The main routine of tangle pass 1"""
        p = self.p = p_in.copy() # self.p used by update_def in untangle
        self.setRootFromHeadline(p)
        theDict = g.get_directives_dict(p, [self.head_root])
        if ('ignore' in theDict):
            return
        self.scanAllDirectives(p) # calls init_directive_ivars.
        # Scan the headline and body text.
        # @language and @comment are not recognized in headlines
        self.skip_headline(p)
        delims = self.skip_body(p, delims)
        if self.errors + g.app.scanErrors >= max_errors:
            self.warning("----- Halting Tangle: too many errors")
        elif p.hasChildren():
            p.moveToFirstChild()
            self.tanglePass1(p, delims)
            while p.hasNext() and (self.errors + g.app.scanErrors < max_errors):
                p.moveToNext()
                self.tanglePass1(p, delims)
    #@+node:ekr.20031218072017.3476: *4* tanglePass2
    # At this point p is the root of the tree that has been tangled.

    def tanglePass2(self):
        self.p = None # self.p is not valid in pass 2.
        self.errors += g.app.scanErrors
        if self.errors > 0:
            self.warning("----- No file written because of errors")
        elif self.root_list is None:
            self.warning("----- The outline contains no roots")
        else:
            self.put_all_roots() # pass 2 top level function.
    #@+node:ekr.20031218072017.3477: *4* tangleTree (calls cleanup)
    # This function is called only from the top level,
    # so there is no need to initialize globals.

    def tangleTree(self, p, report_errors):
        """Tangles all nodes in the tree whose root is p.

        Reports on its results if report_errors is True."""
        p = p.copy() # 9/14/04
        assert(p)
        any_root_flag = False
        next = p.nodeAfterTree()
        self.path_warning_given = False
        self.tangling = True
        while p and p != next:
            self.setRootFromHeadline(p)
            assert self.head_root is None
            theDict = g.get_directives_dict(p, [self.head_root])
            is_ignore = 'ignore' in theDict
            is_root = 'root' in theDict
            is_unit = 'unit' in theDict
            if is_ignore:
                p.moveToNodeAfterTree()
            elif not is_root and not is_unit:
                p.moveToThreadNext()
            else:
                self.scanAllDirectives(p) # sets self.init_delims
                self.tanglePass1(p, self.init_delims) # sets self.p
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
    #@+node:ekr.20031218072017.3478: *4* untangle
    def untangle(self, event=None, p=None):
        c = self.c
        if not p:
            p = c.p
        self.initUntangleCommand()
        # must be done at this point, since initUntangleCommand blows away tangle_output
        #@+<< read fake files for unit testing >>
        #@+node:sps.20100618004337.16262: *5* << read fake files for unit testing >>
        if g.unitTesting:
            p2 = p.copy()
            while(p2.hasNext()):
                p2.moveToNext()
                self.tangle_output[p2.h] = p2.b
        #@-<< read fake files for unit testing >>
        self.untangleTree(p, report_errors=True)
        if not g.unitTesting:
            g.es("untangle complete")
        c.redraw()
    #@+node:ekr.20031218072017.3479: *4* untangleAll
    def untangleAll(self, event=None):
        c = self.c
        self.initUntangleCommand()
        has_roots = False
        for p in c.rootPosition().self_and_siblings():
            ok = self.untangleTree(p, False)
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
    #@+node:ekr.20031218072017.3480: *4* untangleMarked
    def untangleMarked(self, event=None):
        c = self.c; p = c.rootPosition()
        self.initUntangleCommand()
        marked_flag = False
        while p: # Don't use an iterator.
            if p.isMarked():
                ok = self.untangleTree(p, report_errors=False)
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
    #@+node:ekr.20031218072017.3481: *4* untangleRoot (calls cleanup)
    #@+at
    # This method untangles the derived files in a VNode known to contain at
    # least one @root directive. The work is done in three passes. The first
    # pass creates a TST from the Leo tree so that the next pass will know
    # what comment conventions to use; that pass is performed in
    # untangleTree. The second pass creates the UST by scanning the derived
    # file. The third pass updates the outline using the UST and a new TST
    # that is created during the pass.
    # 
    # We assume that all sections from root to end are contained in the
    # derived file, and we attempt to update all such sections. The
    # begin/end params indicate the range of nodes to be scanned when
    # building the TST.
    #@@c

    def untangleRoot(self, root, begin, end):

        c = self.c
        #@+<< return if @silent >>
        #@+node:ekr.20031218072017.3482: *5* << return if @silent >>
        if self.print_mode in ("quiet", "silent"):
            g.warning(f"@{self.print_mode} inhibits untangle for {root.h}")
            return
        #@-<< return if @silent >>
        s = root.b
        i = 0
        while i < len(s):
            #@+<< Set path & root_name to the file specified in the @root directive >>
            #@+node:ekr.20031218072017.3483: *5* << Set path & root_name to the file specified in the @root directive >>
            self.root_name = None
            while i < len(s):
                code, junk = self.token_type(s, i, report_errors=True)
                i = g.skip_line(s, i)
                if code == at_root:
                    # token_type sets root_name unless there is a syntax error.
                    if self.root_name: path = self.root_name
                    break
            if not self.root_name:
                # A bad @root command.  token_type has already given an error.
                self.cleanup()
                return
            #@-<< Set path & root_name to the file specified in the @root directive >>
            path = c.os_path_finalize_join(self.tangle_directory, path)
            if g.unitTesting:
                #@+<< fake the file access >>
                #@+node:sps.20100608083657.20939: *5* << fake the file access >>
                # complications to handle testing of multiple @root directives together with
                # @path directives
                file_name_path = c.os_path_finalize_join(self.tangle_directory, path)
                if (file_name_path.find(c.openDirectory) == 0):
                    relative_path = file_name_path[len(c.openDirectory):]
                    # don't confuse /u and /usr as having common prefixes
                    if (relative_path[: len(os.sep)] == os.sep):
                        file_name_path = relative_path[len(os.sep):]
                # find the node with the right title, and load self.tangle_output and file_buf
                file_buf = self.tangle_output.get(file_name_path)
                #@-<< fake the file access >>
            else:
                file_buf, e = g.readFileIntoString(path)
            if file_buf is not None:
                file_buf = file_buf.replace('\r', '')
                if not g.unitTesting:
                    g.es('', '@root ' + path)
                if 0: # debug
                    g.es(self.st_dump())
                    g.es("path: " + path)
                section = self.tst[self.root_name]
                assert section
                # Pass 2: Scan the derived files, creating the UST
                self.scan_derived_file(file_buf)
                if self.errors + g.app.scanErrors == 0:
                    # Untangle the outline using the UST and a newly-created TST
                    #@+<< Pass 3 >>
                    #@+node:ekr.20031218072017.3485: *5* << Pass 3  >>
                    # This code untangles the root and all its siblings.
                    # We don't call tangleTree here because we must handle all siblings.
                    # tanglePass1 handles an entire tree. It also handles @ignore.
                    self.tangling = False
                    p = begin
                    while p and p != end: # Don't use iterator.
                        self.scanAllDirectives(p) # sets self.init_delims
                        self.tst = {}
                        self.untangle_stage1 = False
                        self.tanglePass1(p, self.init_delims)
                        if self.errors + g.app.scanErrors != 0:
                            break
                        p.moveToNodeAfterTree()
                    self.ust_warn_about_orphans()
                    #@-<< Pass 3 >>
        self.cleanup()
    #@+node:ekr.20031218072017.3486: *4* untangleTree
    # This funtion is called when the user selects any "Untangle" command.

    def untangleTree(self, p, report_errors):
        p = p.copy() # 9/14/04
        c = self.c
        any_root_flag = False
        afterEntireTree = p.nodeAfterTree()
        # Initialize these globals here: they can't be cleared later.
        self.head_root = None
        self.errors = 0; g.app.scanErrors = 0
        c.clearAllVisited() # Used by untangle code.
        self.tangling = False
        self.delims_table = False
        while p and p != afterEntireTree and self.errors + g.app.scanErrors == 0:
            self.setRootFromHeadline(p)
            assert(self.head_root is None)
            theDict = g.get_directives_dict(p, [self.head_root])
            ignore = 'ignore' in theDict
            root = 'root' in theDict
            unit = 'unit' in theDict
            if ignore:
                p.moveToNodeAfterTree()
            elif unit:
                # Expand the context to the @unit directive.
                unitNode = p # 9/27/99
                afterUnit = p.nodeAfterTree()
                self.scanAllDirectives(p) # sets self.init_delims
                p.moveToThreadNext()
                while p and p != afterUnit and self.errors + g.app.scanErrors == 0:
                    self.setRootFromHeadline(p)
                    assert(self.head_root is None)
                    theDict = g.get_directives_dict(p, [self.head_root])
                    root = 'root' in theDict
                    if root:
                        any_root_flag = True
                        end = None
                        #@+<< set end to the next root in the unit >>
                        #@+node:ekr.20031218072017.3487: *5* << set end to the next root in the unit >>
                        #@+at
                        # The untangle_root function will untangle an entire tree by calling
                        # untangleTree, so the following code ensures that the next @root node
                        # will not be an offspring of p.
                        #@@c
                        end = p.threadNext()
                        while end and end != afterUnit:
                            flag, i = g.is_special(end.b, "@root")
                            if flag and not p.isAncestorOf(end):
                                break
                            end.moveToThreadNext()
                        #@-<< set end to the next root in the unit >>
                        self.scanAllDirectives(p)
                        self.tanglePass1(p, self.init_delims)
                        self.untangleRoot(p, unitNode, afterUnit)
                        p = end.copy()
                    else: p.moveToThreadNext()
            elif root:
                # Limit the range of the @root to its own tree.
                afterRoot = p.nodeAfterTree()
                any_root_flag = True
                self.scanAllDirectives(p)
                # get the delims table
                self.untangle_stage1 = True
                self.tanglePass1(p, self.init_delims)
                self.untangleRoot(p, p, afterRoot)
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
    #@+node:ekr.20031218072017.3488: *3* tangle
    #@+node:ekr.20031218072017.3489: *4* Pass 1
    #@+node:sps.20100618004337.20969: *5* handle_newline
    #@+at
    # This method handles newline processing while skipping a code section.
    # It sets 'done' if the line contains an @directive or section
    # definition that terminates the present code section. On entry: i
    # should point to the first character of a line. This routine scans past
    # a line only if it could not contain a section reference.
    # 
    # Returns (i, done)
    #@@c

    def handle_newline(self, s, i, delims):
        assert(delims)
        j = i; done = False
        kind, end = self.token_type(s, i, report_errors=False)
        # token_type will not skip whitespace in noweb mode.
        i = g.skip_ws(s, i)
        if kind == plain_line:
            pass
        elif(
            kind == at_code or
            kind == at_doc or
            kind == at_root or
            kind == section_def
        ):
            i = j; done = True # Terminate this code section and rescan.
        elif kind == section_ref:
            # Enter the reference.
            ref = s[i: end]
            self.st_enter_section_name(ref, None, None, None, None)
        elif kind == at_other:
            k = g.skip_to_end_of_line(s, i)
            if g.match_word(s, j, "@language"):
                lang, d1, d2, d3 = g.set_language(s, j)
                delims = (d1, d2, d3)
            elif g.match_word(s, j, "@comment"):
                delims = g.set_delims_from_string(s[j: k])
            i = k
        elif kind == at_chapter or kind == at_section:
            # We don't process chapter or section here
            i = g.skip_to_end_of_line(s, i)
        elif kind == bad_section_name:
            pass
        elif kind == at_web or kind == at_at:
            i += 2 # Skip a CWEB control code.
        else: assert(False)
        return i, done, delims
    #@+node:sps.20100618004337.20951: *5* skip_body
    # This method handles all the body text.

    def skip_body(self, p, delims):
        #@+<< skip_body docstring >>
        #@+node:sps.20100618004337.20957: *6* << skip_body docstring >>
        '''
        The following subsections contain the interface between the Tangle and
        Untangle commands. This interface is an important hack, and allows
        Untangle to avoid duplicating the logic in skip_tree and its allies.

        The aha is this: just at the time the Tangle command enters a
        definition into the symbol table, all the information is present that
        Untangle needs to update that definition.

        To get whitespace exactly right we retain the outline's leading
        whitespace and remove leading whitespace from the updated definition.
        '''
        #@-<< skip_body docstring >>
        c = self.c
        s = p.b
        code = doc = None; i = 0
        anyChanged = False
        if self.start_mode == "code":
            j = g.skip_blank_lines(s, i)
            i, code, new_delims, reflist = self.skip_code(s, j, delims)
            if code:
                #@+<< Define a section for a leading code part >>
                #@+node:sps.20100618004337.20952: *6* << Define a section for a leading code part >>
                if self.header_name:
                    # Tangle code.
                    part = self.st_enter_section_name(
                        self.header_name, code, doc, delims, new_delims)
                    if not self.tangling:
                        # Untangle code.
                        if self.untangle_stage1:
                            section = self.st_lookup(self.header_name)
                            section.parts[part - 1].reflist(refs=reflist)
                        else:
                            head = s[: j]; tail = s[i:]
                            s, i, changed = self.update_def(self.header, part, head, code, tail)
                            if changed: anyChanged = True
                    code = doc = None
                # leading code without a header name gets silently dropped
                #@-<< Define a section for a leading code part >>
            delims = new_delims
        if not code:
            i, doc, delims = self.skip_doc(s, i, delims) # Start in doc section by default.
            if i >= len(s) and doc:
                #@+<< Define a section containing only an @doc part >>
                #@+node:sps.20100618004337.20953: *6* << Define a section containing only an @doc part >>
                #@+at
                # It's valid for an @doc directive to appear under a headline that does
                # not contain a section name. In that case, no section is defined.
                #@@c
                if self.header_name:
                    # Tangle code.
                    part = self.st_enter_section_name(self.header_name, code, doc, delims, delims)
                    # Untangle code.
                    if not self.tangling:
                        # Untangle no longer updates doc parts.
                        # 12/03/02: Mark the part as having been updated to suppress warning.
                        junk, junk = self.ust_lookup(self.header_name, part, update_flag=True)
                doc = None
                #@-<< Define a section containing only an @doc part >>
        while i < len(s):
            progress = i # progress indicator
            kind, end = self.token_type(s, i, report_errors=True)
            # if g.is_nl(s,i): i = g.skip_nl(s,i)
            i = g.skip_ws(s, i)
            if kind == section_def:
                #@+<< Scan and define a section definition >>
                #@+node:sps.20100618004337.20954: *6* << Scan and define a section definition >>
                # We enter the code part and any preceding doc part into the symbol table.
                # Skip the section definition line.
                k = i; i, kind, junk = self.skip_section_name(s, i)
                section_name = s[k: i]
                assert(kind == section_def)
                i = g.skip_to_end_of_line(s, i)
                # Tangle code: enter the section name even if the code part is empty.
                #@+<<process normal section>>
                #@+node:sps.20100716120121.12132: *7* <<process normal section>>
                # Tangle code.
                j = g.skip_blank_lines(s, i)
                i, code, new_delims, reflist = self.skip_code(s, j, delims)
                part = self.st_enter_section_name(section_name, code, doc, delims, new_delims)
                delims = new_delims
                # Untangle code
                if not self.tangling:
                    # part may be zero if there was an empty code section (doc part only)
                    # In untangle stage1 such code produces no reference list,
                    #    thus nothing to do.
                    # In untangle stage2, such code cannot be updated because it
                    # was either not emitted to the external file or emitted as a doc part only
                    #     in either case, there is no code section to update, and we don't
                    #     update doc parts.
                    if part > 0:
                        if self.untangle_stage1:
                            section = self.st_lookup(section_name)
                            section.parts[part - 1].reflist(refs=reflist)
                        else:
                            head = s[: j]; tail = s[i:]
                            s, i, changed = self.update_def(section_name, part, head, code, tail)
                            if changed: anyChanged = True
                #@-<<process normal section>>
                code = None
                doc = ''
                #@-<< Scan and define a section definition >>
            elif kind == at_code:
                i = g.skip_line(s, i)
                #@+<< Scan and define an @code defininition >>
                #@+node:sps.20100618004337.20955: *6* << Scan and define an @code defininition >>
                # All @c or @code directives denote < < headline_name > > =
                if self.header_name:
                    section_name = self.header_name
                    #@+<<process normal section>>
                    #@+node:ekr.20140630110633.16726: *7* <<process normal section>>
                    # Tangle code.
                    j = g.skip_blank_lines(s, i)
                    i, code, new_delims, reflist = self.skip_code(s, j, delims)
                    part = self.st_enter_section_name(section_name, code, doc, delims, new_delims)
                    delims = new_delims
                    # Untangle code
                    if not self.tangling:
                        # part may be zero if there was an empty code section (doc part only)
                        # In untangle stage1 such code produces no reference list,
                        #    thus nothing to do.
                        # In untangle stage2, such code cannot be updated because it
                        # was either not emitted to the external file or emitted as a doc part only
                        #     in either case, there is no code section to update, and we don't
                        #     update doc parts.
                        if part > 0:
                            if self.untangle_stage1:
                                section = self.st_lookup(section_name)
                                section.parts[part - 1].reflist(refs=reflist)
                            else:
                                head = s[: j]; tail = s[i:]
                                s, i, changed = self.update_def(section_name, part, head, code, tail)
                                if changed: anyChanged = True
                    #@-<<process normal section>>
                else:
                    self.error("@c expects the headline: " + self.header + " to contain a section name")
                code = None
                doc = ''
                #@-<< Scan and define an @code defininition >>
            elif kind == at_root:
                i = g.skip_line(s, i)
                #@+<< Scan and define a root section >>
                #@+node:sps.20100618004337.20956: *6* << Scan and define a root section >>
                # We save the file name in case another @root ends the code section.
                old_root_name = self.root_name
                #
                # Tangle code.
                j = g.skip_blank_lines(s, i)
                k, code, new_delims, reflist = self.skip_code(s, j, delims)
                self.st_enter_root_name(old_root_name, code, doc, delims, new_delims)
                delims = new_delims
                if not self.tangling:
                    # Untangle code.
                    if self.untangle_stage1:
                        root_section = self.st_lookup(old_root_name)
                        assert(root_section)
                        root_first_part = root_section.parts[0]
                        assert(root_first_part)
                        root_first_part.reflist(refs=reflist)
                    else:
                        part = 1 # Use 1 for root part.
                        head = s[: j]; tail = s[k:]
                        s, i, changed = self.update_def(old_root_name, part, head, code, tail, is_root_flag=True)
                        if changed: anyChanged = True
                code = None
                doc = ''
                #@-<< Scan and define a root section >>
            elif kind in (at_doc, at_chapter, at_section):
                i = g.skip_line(s, i)
                i, more_doc, delims = self.skip_doc(s, i, delims)
                doc = doc + more_doc
            else:
                i = g.skip_line(s, i)
            assert(progress < i) # we must make progress!
        # Only call trimTrailingLines if we have changed its body.
        if anyChanged:
            c.trimTrailingLines(p)
        return delims
    #@+node:sps.20100618004337.20965: *5* skip_code
    #@+at
    # This method skips an entire code section. The caller is responsible
    # for entering the completed section into the symbol table. On entry, i
    # points at the line following the @directive or section definition that
    # starts a code section. We skip code until we see the end of the body
    # text or the next @ directive or section defintion that starts a code
    # or doc part.
    #@@c

    def skip_code(self, s, i, delims):
        reflist = []
        code1 = i
        nl_i = i # For error messages
        done = False # True when end of code part seen.
        #@+<< skip a noweb code section >>
        #@+node:sps.20100618004337.20966: *6* << skip a noweb code section >>
        #@+at
        # This code handles the following escape conventions: double at-sign at
        # the start of a line and at-<< and at.>.
        #@@c
        i, done, delims = self.handle_newline(s, i, delims)
        while not done and i < len(s):
            ch = s[i]
            if g.is_nl(s, i):
                nl_i = i = g.skip_nl(s, i)
                i, done, delims = self.handle_newline(s, i, delims)
            elif ch == '@' and (
                g.match(s, i + 1, "<<") or # must be on different lines
                g.match(s, i + 1, ">>")
            ):
                i += 3 # skip the noweb escape sequence.
            elif ch == '<':
                #@+<< handle possible noweb section reference >>
                #@+node:sps.20100618004337.20967: *7* << handle possible noweb section reference >>
                j, kind, end = self.is_section_name(s, i)
                if kind == section_def:
                    k = g.skip_to_end_of_line(s, i)
                    # We are in the middle of a line.
                    i += 1
                    self.error("chunk definition not valid here\n" + s[nl_i: k])
                elif kind == bad_section_name:
                    i += 1 # This is not an error.  Just skip the '<'.
                else:
                    assert(kind == section_ref)
                    # Enter the reference into the symbol table.
                    # Appropriate comment delimiters get specified
                    # at the time the section gets defined.
                    name = s[i: end]
                    self.st_enter_section_name(name, None, None, None, None)
                    reflist.append(self.st_lookup(name))
                    i = end
                #@-<< handle possible noweb section reference >>
            else: i += 1
        #@-<< skip a noweb code section >>
        code = s[code1: i]
        return i, code, delims, reflist
    #@+node:ekr.20031218072017.3503: *5* skip_doc
    def skip_doc(self, s, i, delims):
        # Skip @space, @*, @doc, @chapter and @section directives.
        doc1 = i
        while i < len(s):
            if g.is_nl(s, i):
                doc1 = i = g.skip_nl(s, i)
            elif g.match(s, i, "@ ") or g.match(s, i, "@\t") or g.match(s, i, "@*"):
                i = g.skip_ws(s, i + 2); doc1 = i
            elif g.match(s, i, "@\n"):
                i += 1; doc1 = i
            elif(g.match_word(s, i, "@doc") or
                  g.match_word(s, i, "@chapter") or
                  g.match_word(s, i, "@section")):
                doc1 = i = g.skip_line(s, i)
            else: break
        while i < len(s):
            kind, junk = self.token_type(s, i, report_errors=False)
            if kind == at_code or kind == at_root or kind == section_def:
                break
            # @language and @comment are honored within document parts
            k = g.skip_line(s, i)
            if kind == at_other:
                if g.match_word(s, i, "@language"):
                    lang, d1, d2, d3 = g.set_language(s, i)
                    delims = (d1, d2, d3)
                elif g.match_word(s, i, "@comment"):
                    delims = g.set_delims_from_string(s[i: k])
            i = k
        doc = s[doc1: i]
        return i, doc, delims
    #@+node:ekr.20031218072017.3504: *5* skip_headline
    #@+at
    # This function sets ivars that keep track of the indentation level. We
    # also remember where the next line starts because it is assumed to be
    # the first line of a documentation section.
    # 
    # A headline can contain a leading section name. If it does, we
    # substitute the section name if we see an @c directive in the body
    # text.
    #@@c

    def skip_headline(self, p):
        self.header = s = p.h
        # Set self.header_name.
        j = i = g.skip_ws(s, 0)
        i, kind, end = self.is_section_name(s, i)
        if kind == bad_section_name:
            self.header_name = None
        else:
            self.header_name = s[j: end]
    #@+node:ekr.20031218072017.3505: *4* Pass 2
    #@+node:ekr.20031218072017.1488: *5* oblank, oblanks, os, otab, otabs (Tangle)
    def oblank(self):
        self.oblanks(1)

    def oblanks(self, n):
        if abs(n) > 0:
            s = g.toEncodedString(' ' * abs(n), encoding=self.encoding)
            self.output_file.write(s)

    def onl(self):
        s = self.output_newline
        s = g.toEncodedString(s, self.encoding, reportErrors=True)
        self.output_file.write(s)

    def os(self, s):
        s = s.replace('\r', '\n')
        s = g.toEncodedString(s, self.encoding, reportErrors=True)
        self.output_file.write(s)

    def otab(self):
        self.otabs(1)

    def otabs(self, n):
        if abs(n) > 0:
            s = g.toEncodedString('\t' * abs(n), self.encoding, reportErrors=True)
            self.output_file.write(s)
    #@+node:ekr.20031218072017.1151: *5* tangle.put_all_roots
    #@+at
    # This is the top level method of the second pass. It creates a separate derived file
    # for each @root directive in the outline. The file is actually written only if
    # the new version of the file is different from the old version,or if the file did
    # not exist previously. If changed_only_flag FLAG is True only changed roots are
    # actually written.
    #@@c

    def put_all_roots(self):
        c = self.c; outline_name = c.mFileName
        for section in self.root_list:
            file_name = c.os_path_finalize_join(self.tangle_directory, section.name)
            mode = c.config.output_newline
            textMode = mode == 'platform'
            if g.unitTesting:
                self.output_file = g.FileLikeObject()
                temp_name = 'temp-file'
            else:
                self.output_file, temp_name = g.create_temp_file(textMode=textMode)
            if not temp_name:
                g.es("can not create temp file")
                break
            #@+<<Get root specific attributes>>
            #@+node:ekr.20031218072017.1152: *6* <<Get root specific attributes>> (Tangle)
            # Stephen Schaefer, 9/2/02
            # Retrieve the full complement of state for the root node
            self.language = section.RootAttributes.language
            self.use_header_flag = section.RootAttributes.use_header_flag
            self.print_mode = section.RootAttributes.print_mode
            self.path = section.RootAttributes.path
            self.page_width = section.RootAttributes.page_width
            self.tab_width = section.RootAttributes.tab_width
            # Stephen P. Schaefer, 9/13/2002
            self.first_lines = section.RootAttributes.first_lines
            #@-<<Get root specific attributes>>
            #@+<<Put @first lines>>
            #@+node:ekr.20031218072017.1153: *6* <<Put @first lines>>
            # Stephen P. Schaefer 9/13/2002
            if self.first_lines:
                self.os(self.first_lines)
            #@-<<Put @first lines>>
            if self.use_header_flag and self.print_mode == "verbose":
                #@+<< Write a banner at the start of the output file >>
                #@+node:ekr.20031218072017.1154: *6* <<Write a banner at the start of the output file>>
                # a root section must have at least one part
                assert section.parts
                delims = section.parts[0].delims
                if delims[0]:
                    self.os(delims[0])
                    self.os(" Created by Leo from: ")
                    self.os(outline_name)
                    self.onl(); self.onl()
                elif delims[1] and delims[2]:
                    self.os(delims[1])
                    self.os(" Created by Leo from: ")
                    self.os(outline_name)
                    self.oblank(); self.os(delims[2])
                    self.onl(); self.onl()
                #@-<< Write a banner at the start of the output file >>
            for part in section.parts:
                if part.is_root:
                    self.tangle_indent = 0 # Initialize global.
                    self.put_PartNode(part, False) # output first lws
            self.onl() # Make sure the file ends with a cr/lf
            #@+<< unit testing fake files>>
            #@+node:sps.20100608083657.20937: *6* << unit testing fake files>>
            if g.unitTesting:
                # complications to handle testing of multiple @root directives together with
                # @path directives
                file_name_path = file_name
                if (file_name_path.find(c.openDirectory) == 0):
                    relative_path = file_name_path[len(c.openDirectory):]
                    # don't confuse /u and /usr as having common prefixes
                    if (relative_path[: len(os.sep)] == os.sep):
                        file_name_path = relative_path[len(os.sep):]
                self.tangle_output[file_name_path] = self.output_file.get()
            #@-<< unit testing fake files>>
            self.output_file.close()
            self.output_file = None
            #@+<< unit testing set result and continue >>
            #@+node:sps.20100608083657.20938: *6* << unit testing set result and continue >>
            if g.unitTesting:
                assert self.errors == 0
                g.app.unitTestDict['tangle'] = True
                g.app.unitTestDict['tangle_directory'] = self.tangle_directory
                if g.app.unitTestDict.get('tangle_output_fn'):
                    g.app.unitTestDict['tangle_output_fn'] += "\n" + file_name
                else:
                    g.app.unitTestDict['tangle_output_fn'] = file_name
                continue
            #@-<< unit testing set result and continue >>
            if self.errors + g.app.scanErrors == 0:
                self.update_file_if_changed(c, file_name, temp_name)
            else:
                g.es("unchanged:", file_name)
                #@+<< Erase the temporary file >>
                #@+node:ekr.20031218072017.1155: *6* << Erase the temporary file >>
                try: # Just delete the temp file.
                    os.remove(temp_name)
                except Exception:
                    pass
                #@-<< Erase the temporary file >>
    #@+node:ekr.20031218072017.3506: *5* put_code
    #@+at
    # This method outputs a code section, expanding section references by
    # their definition. We should see no @directives or section definitions
    # that would end the code section.
    # 
    # Most of the differences bewteen noweb mode and CWEB mode are handled
    # by token_type(called from put_newline). Here, the only difference is
    # that noweb handles double-@ signs only at the start of a line.
    #@@c

    def put_code(self, s, no_first_lws_flag, delims):

        i = 0
        if i < len(s):
            i = self.put_newline(s, i, no_first_lws_flag)
            # Double @ is valid in both noweb and CWEB modes here.
            if g.match(s, i, "@@"):
                self.os('@'); i += 2
        while i < len(s):
            progress = i
            ch = s[i]
            if g.match(s, i, "<<"):
                #@+<< put possible section reference >>
                #@+node:ekr.20031218072017.3507: *6* <<put possible section reference >>
                j, kind, name_end = self.is_section_name(s, i)
                if kind == section_def:
                    # We are in the middle of a code section
                    self.error(
                        "Should never happen:\n" +
                        "section definition while putting a section reference: " +
                        s[i: j])
                    i += 1
                elif kind == bad_section_name:
                    self.os(s[i]); i += 1 # This is not an error.
                else:
                    assert(kind == section_ref)
                    name = s[i: name_end]
                    self.put_section(s, i, name, name_end, delims)
                    i = j
                #@-<< put possible section reference >>
            elif ch == '@': # We are in the middle of a line.
                #@+<< handle noweb @ < < convention >>
                #@+node:ekr.20031218072017.3509: *6* << handle noweb @ < < convention >>
                #@+at
                # The user must ensure that neither @ < < nor @ > > occurs in comments
                # or strings. However, it is valid for @ < < or @ > > to appear in the
                # doc chunk or in a single-line comment.
                #@@c
                if g.match(s, i, "@<<"):
                    self.os("/*@*/<<"); i += 3
                elif g.match(s, i, "@>>"):
                    self.os("/*@*/>>"); i += 3
                else: self.os("@"); i += 1
                #@-<< handle noweb @ < < convention >>
            elif ch == '\r':
                i += 1
            elif ch == '\n':
                i += 1; self.onl()
                #@+<< elide @comment or @language >>
                #@+node:sps.20100624113712.16401: *6* << elide @comment or @language >>
                while g.match_word(s, i, "@comment") or g.match_word(s, i, "@language"):
                    i = g.skip_line(s, i)
                #@-<< elide @comment or @language >>
                i = self.put_newline(s, i, False) # Put full lws
            else: self.os(s[i]); i += 1
            assert(progress < i)
    #@+node:ekr.20031218072017.3510: *5* put_doc
    # This method outputs a doc section within a block comment.

    def put_doc(self, s, delims):

        width = self.page_width
        words = 0; word_width = 0; line_width = 0
        # 8/1/02: can't use choose here!
        if delims[0] is None: single_w = 0
        else: single_w = len(delims[0])
        # Make sure we put at least 20 characters on a line.
        if width - max(0, self.tangle_indent) < 20:
            width = max(0, self.tangle_indent) + 20
        # Skip Initial white space in the doc part.
        i = g.skip_ws_and_nl(s, 0)
        if i < len(s) and (self.print_mode == "verbose" or self.print_mode == "quiet"):
            use_block_comment = delims[1] and delims[2]
            use_single_comment = not use_block_comment and delims[0]
            # javadoc_comment = use_block_comment and delims[1] == "/**"
            if use_block_comment or use_single_comment:
                self.put_leading_ws(self.tangle_indent)
                if use_block_comment:
                    self.os(delims[1])
                #@+<< put the doc part >>
                #@+node:ekr.20031218072017.3511: *6* <<put the doc part>>
                #@+at
                # This code fills and outputs each line of a doc part. It keeps track of
                # whether the next word will fit on a line,and starts a new line if
                # needed.
                #@@c
                if use_single_comment:
                    self.os(delims[0]); self.otab()
                    line_width = (single_w / abs(self.tab_width) + 1) * abs(self.tab_width)
                else:
                    line_width = abs(self.tab_width)
                    self.onl(); self.otab()
                self.put_leading_ws(self.tangle_indent)
                line_width += max(0, self.tangle_indent)
                words = 0; word_width = 0
                while i < len(s):
                    #@+<<output or skip whitespace or newlines>>
                    #@+node:ekr.20031218072017.3512: *7* <<output or skip whitespace or newlines>>
                    #@+at
                    # This outputs whitespace if it fits, and ignores it otherwise, and
                    # starts a new line if a newline is seen. The effect of self code is
                    # that we never start a line with whitespace that was originally at the
                    # end of a line.
                    #@@c
                    while g.is_ws_or_nl(s, i):
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
                            assert(g.is_nl(s, i))
                            self.onl()
                            if use_single_comment:
                                # New code: 5/31/00
                                self.os(delims[0]); self.otab()
                                line_width = (single_w / abs(self.tab_width) + 1) * abs(self.tab_width)
                            else:
                                self.otab()
                                line_width = abs(self.tab_width)
                            i = g.skip_nl(s, i)
                            words = 0
                            self.put_leading_ws(self.tangle_indent)
                            # tangle_indent is in spaces.
                            line_width += max(0, self.tangle_indent)
                    #@-<<output or skip whitespace or newlines>>
                    if i >= len(s):
                        break
                    j = i; word_width = 0
                    while j < len(s) and not g.is_ws_or_nl(s, j):
                        word_width += 1
                        j += 1
                    if words == 0 or line_width + word_width < width:
                        words += 1
                        self.os(s[i: j])
                        i = j
                        line_width += word_width
                    else:
                        # 11-SEP-2002 DTHEIN: Fixed linewrapping bug in
                        # tab-then-comment sequencing
                        self.onl()
                        if use_single_comment:
                            self.os(delims[0]); self.otab()
                            line_width = (single_w / abs(self.tab_width) + 1) * abs(self.tab_width)
                        else:
                            self.otab()
                            line_width = abs(self.tab_width)
                        words = 0
                        self.put_leading_ws(self.tangle_indent)
                        # tangle_indent is in spaces.
                        line_width += max(0, self.tangle_indent)
                #@-<< put the doc part >>
                self.onl()
                self.put_leading_ws(self.tangle_indent)
                if use_block_comment:
                    self.os(delims[2])
                self.onl()
            else: self.onl()
    #@+node:ekr.20031218072017.3515: *5* put_leading_ws
    # Puts tabs and spaces corresponding to n spaces, assuming that we are at the start of a line.

    def put_leading_ws(self, n):

        w = self.tab_width
        if w > 1:
            q, r = divmod(n, w)
            self.otabs(q)
            self.oblanks(r)
        else:
            self.oblanks(n)
    #@+node:ekr.20031218072017.3516: *5* put_newline
    #@+at
    # This method handles scanning when putting the start of a new line.
    # Unlike the corresponding method in pass one, this method doesn't need
    # to set a done flag in the caller because the caller already knows
    # where the code section ends.
    #@@c

    def put_newline(self, s, i, no_first_lws_flag):
        kind, junk = self.token_type(s, i, report_errors=False)
        #@+<< Output leading white space except for blank lines >>
        #@+node:ekr.20031218072017.3517: *6* << Output leading white space except for blank lines >>
        j = i; i = g.skip_ws(s, i)
        if i < len(s) and not g.is_nl(s, i):
            # Conditionally output the leading previous leading whitespace.
            if not no_first_lws_flag:
                self.put_leading_ws(self.tangle_indent)
            # Always output the leading whitespace of _this_ line.
            k, width = g.skip_leading_ws_with_indent(s, j, self.tab_width)
            self.put_leading_ws(width)
        #@-<< Output leading white space except for blank lines >>
        if i >= len(s):
            return i
        if kind == at_web or kind == at_at:
            i += 2 # Allow the line to be scanned.
        elif kind == at_doc or kind == at_code:
            pass
        else:
            # These should have set limit in pass 1.
            assert(kind != section_def and kind != at_chapter and kind != at_section)
        return i
    #@+node:ekr.20031218072017.3518: *5* put_PartNode
    # This method outputs one part of a section definition.

    def put_PartNode(self, part, no_first_lws_flag):

        if part.doc and self.output_doc_flag and self.print_mode != "silent":
            self.put_doc(part.doc, part.delims)
        if part.code:
            # comment convention cannot change in the middle of a doc part
            self.put_code(part.code, no_first_lws_flag, part.delims)
    #@+node:ekr.20031218072017.3519: *5* put_section
    #@+at
    # This method outputs the definition of a section and all sections
    # referenced from the section. name is the section's name. This code
    # checks for recursive definitions by calling section_check(). We can
    # not allow section x to expand to code containing another call to
    # section x, either directly or indirectly.
    #@@c

    def put_section(self, s, i, name, name_end, delims):
        
        j = g.skip_line(s, i)
        outer_old_indent = self.tangle_indent
        trailing_ws_indent = 0 # Set below.
        inner_old_indent = 0 # Set below.
        newline_flag = False # True if the line ends with the reference.
        assert(g.match(name, 0, "<<") or g.match(name, 0, "@<"))
        #@+<< Calculate the new value of tangle_indent >>
        #@+node:ekr.20031218072017.3520: *6* << Calculate the new value of tangle_indent >>
        # Find the start of the line containing the reference.
        j = i
        while j > 0 and not g.is_nl(s, j):
            j -= 1
        if g.is_nl(s, j):
            j = g.skip_nl(s, j)
        # Bump the indentation
        j, width = g.skip_leading_ws_with_indent(s, j, self.tab_width)
        self.tangle_indent += width
        #
        # Force no trailing whitespace in @silent mode.
        if self.print_mode == "silent":
            trailing_ws_indent = 0
        else:
            trailing_ws_indent = self.tangle_indent
        # Increase the indentation if the section reference does not immediately follow
        # the leading white space.  4/3/01: Make no adjustment in @silent mode.
        if (j < len(s) and self.print_mode != "silent" and s[j] != '<'):
            self.tangle_indent += abs(self.tab_width)
        #@-<< Calculate the new value of tangle_indent >>
        #@+<< Set 'newline_flag' if the line ends with the reference >>
        #@+node:ekr.20031218072017.3521: *6* << Set 'newline_flag' if the line ends with the reference >>
        if self.print_mode != "silent":
            i = name_end
            i = g.skip_ws(s, i)
            newline_flag = (i >= len(s) or g.is_nl(s, i))
        #@-<< Set 'newline_flag' if the line ends with the reference >>
        section = self.st_lookup(name)
        if section and section.parts:
            # Expand the section only if we are not already expanding it.
            if self.section_check(name):
                self.section_stack.append(name)
                #@+<< put all parts of the section definition >>
                #@+node:ekr.20031218072017.3522: *6* <<put all parts of the section definition>>
                #@+at
                # This section outputs each part of a section definition. We first count
                # how many parts there are so that the code can output a comment saying
                # 'part x of y'.
                #@@c
                # Output each part of the section.
                sections = len(section.parts)
                count = 0
                for part in section.parts:
                    count += 1
                    # In @silent mode, there is no sentinel line to "use up" the previously output
                    # leading whitespace.  We set the flag to tell put_PartNode and put_code
                    # not to call put_newline at the start of the first code part of the definition.
                    no_first_leading_ws_flag = (count == 1 and self.print_mode == "silent")
                    inner_old_indent = self.tangle_indent
                    # 4/3/01: @silent inhibits newlines after section expansion.
                    if self.print_mode != "silent":
                        #@+<< Put the section name in a comment >>
                        #@+node:ekr.20031218072017.3523: *7* << Put the section name in a comment >>
                        if count > 1:
                            self.onl()
                            self.put_leading_ws(self.tangle_indent)
                        # Don't print trailing whitespace
                        name = name.rstrip()
                        if part.delims[0]:
                            self.os(part.delims[0]); self.oblank(); self.os(name)
                            # put (n of m)
                            if sections > 1:
                                self.oblank()
                                self.os(f"{count} of {sections}")
                        else:
                            assert part.delims[1] and part.delims[2]
                            self.os(part.delims[1]); self.oblank(); self.os(name)
                            # put (n of m)
                            if sections > 1:
                                self.oblank()
                                self.os(f"{count} of {sections}")
                            self.oblank(); self.os(part.delims[2])
                        self.onl() # Always output a newline.
                        #@-<< Put the section name in a comment >>
                    self.put_PartNode(part, no_first_leading_ws_flag)
                    # 4/3/01: @silent inhibits newlines after section expansion.
                    if count == sections and (self.print_mode != "silent" and self.print_mode != "quiet"):
                        #@+<< Put the ending comment >>
                        #@+node:ekr.20031218072017.3525: *7* << Put the ending comment >>
                        #@+at
                        # We do not produce an ending comment unless we are ending the last part
                        # of the section,and the comment is clearer if we don't say(n of m).
                        #@@c
                        self.onl(); self.put_leading_ws(self.tangle_indent)
                        #  Don't print trailing whitespace
                        while name_end > 0 and g.is_ws(s[name_end - 1]):
                            name_end -= 1
                        if section.delims[0]:
                            self.os(section.delims[0]); self.oblank()
                            self.os("-- end -- "); self.os(name)
                        else:
                            self.os(section.delims[1]); self.oblank()
                            self.os("-- end -- "); self.os(name)
                            self.oblank(); self.os(section.delims[2])
                        #@+at The following code sets a flag for untangle.
                        # 
                        # If something follows the section reference we must add a newline,
                        # otherwise the "something" would become part of the comment. Any
                        # whitespace following the (!newline) should follow the section
                        # defintion when Untangled.
                        #@@c
                        if not newline_flag:
                            self.os(" (!newline)") # LeoCB puts the leading blank, so we must do so too.
                            # Put the whitespace following the reference.
                            while name_end < len(s) and g.is_ws(s[name_end]):
                                self.os(s[name_end])
                                name_end += 1
                            self.onl() # We must supply the newline!
                        #@-<< Put the ending comment >>
                    # Restore the old indent.
                    self.tangle_indent = inner_old_indent
                #@-<< put all parts of the section definition >>
                self.section_stack.pop()
        else:
            #@+<< Put a comment about the undefined section >>
            #@+node:sps.20100621105534.16896: *6* <<Put a comment about the undefined section>>
            self.onl(); self.put_leading_ws(self.tangle_indent)
            if self.print_mode != "silent":
                if delims[0]:
                    self.os(delims[0])
                    self.os(" undefined section: "); self.os(name); self.onl()
                else:
                    self.os(delims[1])
                    self.os(" undefined section: "); self.os(name)
                    self.oblank(); self.os(delims[2]); self.onl()
            self.error("Undefined section: " + name)
            #@-<< Put a comment about the undefined section >>
        if not newline_flag:
            self.put_leading_ws(trailing_ws_indent)
        self.tangle_indent = outer_old_indent
        return i, name_end
    #@+node:ekr.20031218072017.3527: *5* section_check
    #@+at
    # We can not allow a section to be defined in terms of itself, either
    # directly or indirectly.
    # 
    # We push an entry on the section stack whenever beginning to expand a
    # section and pop the section stack at the end of each section. This
    # method checks whether the given name appears in the stack. If so, the
    # section is defined in terms of itself.
    #@@c

    def section_check(self, name):
        if name in self.section_stack:
            s = "Invalid recursive reference of " + name + "\n"
            for n in self.section_stack:
                s += "called from: " + n + "\n"
            self.error(s)
            return False
        return True
    #@+node:ekr.20031218072017.3528: *3* tst
    #@+node:ekr.20031218072017.3529: *4* st_check
    def st_check(self):
        """Checks the given symbol table for defined but never referenced sections."""
        for name in sorted(self.tst):
            section = self.tst[name]
            if not section.referenced:
                lp = "<< "
                rp = " >>"
                g.es('', ' ' * 4, 'warning:', lp, section.name, rp, 'has been defined but not used.')
    #@+node:ekr.20031218072017.3530: *4* st_dump
    # Dumps the given symbol table in a readable format.

    def st_dump(self, verbose_flag=True):
        s = "\ndump of symbol table...\n"
        for name in sorted(self.tst):
            section = self.tst[name]
            if verbose_flag:
                s += self.st_dump_node(section)
            else:
                theType = "  " if section.parts else "un"
                s += ("\n" + theType + "defined:[" + section.name + "]")
            s += "\nsection delims: " + repr(section.delims)
        return s
    #@+node:ekr.20031218072017.3531: *4* st_dump_node
    # Dumps each part of a section's definition.

    def st_dump_node(self, section):
        return section.dump()
    #@+node:ekr.20031218072017.3532: *4* st_enter
    # The comment delimiters for the start sentinel are kept in the part;
    # for the end sentinel, in the section

    def st_enter(self, name, code, doc, delims_begin, delims_end, is_root_flag=False):
        """Enters names and their associated code and doc parts into the given symbol table."""
        section = self.st_lookup(name, is_root_flag)
        assert(section)
        if doc:
            doc = doc.rstrip() # remove trailing lines.
        if code:
            if self.print_mode != "silent": # @silent supresses newline processing.
                i = g.skip_blank_lines(code, 0) # remove leading lines.
                if i > 0: code = code[i:]
                if code: code = code.rstrip() # remove trailing lines.
            if not code: code = None
        if self.tangling and code:
            #@+<< check for duplicate code definitions >>
            #@+node:ekr.20031218072017.3533: *5* <<check for duplicate code definitions >>
            for part in section.parts:
                if code == part.code:
                    s = g.angleBrackets(section.name)
                    g.es('warning: possible duplicate definition of:', s)
            #@-<< check for duplicate code definitions >>
        if code or doc:
            part = PartNode(name, code, doc, is_root_flag, False, delims_begin)
            section.parts.append(part)
            section.delims = delims_end
        else: # A reference
            section.referenced = True
        if is_root_flag:
            self.root_list.append(section)
            section.referenced = True # Mark the root as referenced.
            #@+<<remember root node attributes>>
            #@+node:ekr.20031218072017.3534: *5* <<remember root node attributes>>
            # Stephen Schaefer, 9/2/02
            # remember the language and comment characteristics
            section.RootAttributes = RootAttributes(self)
            #@-<<remember root node attributes>>
        return len(section.parts) # part number
    #@+node:ekr.20031218072017.3535: *4* st_enter_root_name
    # Enters a root name into the given symbol table.

    def st_enter_root_name(self, name, code, doc, delims_begin, delims_end):

        if name: # User errors can result in an empty @root name.
            self.st_enter(name, code, doc, delims_begin, delims_end, is_root_flag=True)
    #@+node:ekr.20031218072017.3536: *4* st_enter_section_name
    def st_enter_section_name(self, name, code, doc, delims_begin, delims_end):
        """Enters a section name into the given symbol table.

        The code and doc pointers are None for references."""
        return self.st_enter(name, code, doc, delims_begin, delims_end)
    #@+node:ekr.20031218072017.3537: *4* st_lookup
    def st_lookup(self, name, is_root_flag=False):
        """Looks up name in the symbol table and creates a TstNode for it if it does not exist."""
        if is_root_flag:
            key = name
        else:
            key = self.standardize_name(name)
        if key in self.tst:
            section = self.tst[key]
            return section
        section = TstNode(key, is_root_flag)
        self.tst[key] = section
        return section
    #@+node:ekr.20031218072017.3538: *3* ust
    #@+node:ekr.20031218072017.3539: *4* ust_dump
    def ust_dump(self):
        s = "\n---------- Untangle Symbol Table ----------"
        for name in sorted(self.ust):
            section = self.ust[name]
            s += "\n\n" + section.dump()
        s += "\n--------------------"
        return s
    #@+node:ekr.20031218072017.3540: *4* ust_enter
    def ust_enter(self, name, part, of, code, nl_flag, is_root_flag=False):
        #@+<< ust_enter docstring >>
        #@+node:ekr.20140630111044.16914: *5* << ust_enter docstring >>
        '''
        This routine enters names and their code parts into the given table.
        The 'part' and 'of' parameters are taken from the "(part n of m)"
        portion of the line that introduces the section definition in the C
        code.

        If no part numbers are given the caller should set the 'part' and 'of'
        parameters to zero. The caller is reponsible for checking for
        duplicate parts.

        This function handles names scanned from a source file; the
        corresponding st_enter routine handles names scanned from outlines.
        '''
        #@-<< ust_enter docstring >>
        if not is_root_flag:
            name = self.standardize_name(name)
        #@+<< remove blank lines from the start and end of the text >>
        #@+node:ekr.20031218072017.3541: *5* << remove blank lines from the start and end of the text >>
        i = g.skip_blank_lines(code, 0)
        if i > 0:
            code = code[i:].rstrip()
        #@-<< remove blank lines from the start and end of the text >>
        u = UstNode(name, code, part, of, nl_flag, False) # update_flag
        if name not in self.ust:
            self.ust[name] = u
        section = self.ust[name]
        section.parts[part] = u # Parts may be defined in any order.
    #@+node:ekr.20031218072017.3542: *4* ust_lookup
    def ust_lookup(self, name, part_number, is_root_flag=False, update_flag=False):
        '''
        Search the given table for a part matching the name and part number.
        '''
        if not is_root_flag:
            name = self.standardize_name(name)
        if part_number == 0: part_number = 1 # A hack: zero indicates the first part.
        if name in self.ust:
            section = self.ust[name]
            if part_number in section.parts:
                part = section.parts[part_number]
                if update_flag: part.update_flag = True
                return part, True
        return None, False
    #@+node:ekr.20031218072017.3543: *4* ust_warn_about_orphans
    def ust_warn_about_orphans(self):
        """Issues a warning about any sections in the derived file for which
        no corresponding section has been seen in the outline."""
        for section in self.ust.values():
            for part in section.parts.values():
                assert(part.of == section.of)
                if not part.update_flag:
                    # lp = "<< "
                    # rp = " >>"
                    # g.es("warning:",'%s%s(%s)%s' % (lp,part.name,part.part,rp),
                      # "is not in the outline")
                    break # One warning per section is enough.
    #@+node:ekr.20031218072017.3544: *3* untangle
    #@+node:ekr.20031218072017.3545: *4* compare_comments
    #@+at
    # This function compares the interior of comments and returns True if
    # they are identical except for whitespace or newlines. It is up to the
    # caller to eliminate the opening and closing delimiters from the text
    # to be compared.
    #@@c

    def compare_comments(self, s1, s2):
        tot_len = 0
        if self.comment: tot_len += len(self.comment)
        if self.comment_end: tot_len += len(self.comment_end)
        p1, p2 = 0, 0
        while p1 < len(s1) and p2 < len(s2):
            p1 = g.skip_ws_and_nl(s1, p1)
            p2 = g.skip_ws_and_nl(s2, p2)
            if self.comment and self.comment_end:
                #@+<< Check both parts for @ comment conventions >>
                #@+node:ekr.20031218072017.3546: *5* << Check both parts for @ comment conventions >>
                #@+at
                # This code is used in forgiving_compare()and in compare_comments().
                # 
                # In noweb mode we allow / * @ * /  (without the spaces)to be equal to @.
                # We must be careful not to run afoul of this very convention here!
                #@@c
                if p1 < len(s1) and s1[p1] == '@':
                    if g.match(s2, p2, self.comment + '@' + self.comment_end):
                        p1 += 1
                        p2 += tot_len + 1
                        continue
                elif p2 < len(s2) and s2[p2] == '@':
                    if g.match(s1, p1, self.comment + '@' + self.comment_end):
                        p2 += 1
                        p1 += tot_len + 1
                        continue
                #@-<< Check both parts for @ comment conventions >>
            if p1 >= len(s1) or p2 >= len(s2):
                break
            if s1[p1] != s2[p2]:
                return False
            p1 += 1; p2 += 1
        p1 = g.skip_ws_and_nl(s1, p1)
        p2 = g.skip_ws_and_nl(s2, p2)
        return p1 == len(s1) and p2 == len(s2)
    #@+node:ekr.20031218072017.3548: *4* forgiving_compare (tangle)
    #@+at
    # This is the "forgiving compare" function. It compares two texts and
    # returns True if they are identical except for comments or non-critical
    # whitespace. Whitespace inside strings or preprocessor directives must
    # match exactly. @language and @comment in the outline version are
    # ignored. s1 is the outline version, s2 is the external file version.
    #@@c

    def forgiving_compare(self, name, part, s1, s2):

        s1 = g.toUnicode(s1, self.encoding)
        s2 = g.toUnicode(s2, self.encoding)
        #@+<< Define forgiving_compare vars >>
        #@+node:ekr.20031218072017.3549: *5* << Define forgiving_compare vars >>
        # scan_derived_file has set the ivars describing comment delims.
        first1 = first2 = 0
        tot_len = 0
        if self.comment: tot_len += len(self.comment)
        if self.comment_end: tot_len += len(self.comment_end)
        #@-<< Define forgiving_compare vars >>
        p1 = g.skip_ws_and_nl(s1, 0)
        p2 = g.skip_ws_and_nl(s2, 0)
        result = True
        while result and p1 < len(s1) and p2 < len(s2):
            first1 = p1; first2 = p2
            if self.comment and self.comment_end:
                #@+<< Check both parts for @ comment conventions >>
                #@+node:ekr.20140630110727.16727: *5* << Check both parts for @ comment conventions >>
                #@+at
                # This code is used in forgiving_compare()and in compare_comments().
                # 
                # In noweb mode we allow / * @ * /  (without the spaces)to be equal to @.
                # We must be careful not to run afoul of this very convention here!
                #@@c
                if p1 < len(s1) and s1[p1] == '@':
                    if g.match(s2, p2, self.comment + '@' + self.comment_end):
                        p1 += 1
                        p2 += tot_len + 1
                        continue
                elif p2 < len(s2) and s2[p2] == '@':
                    if g.match(s1, p1, self.comment + '@' + self.comment_end):
                        p2 += 1
                        p1 += tot_len + 1
                        continue
                #@-<< Check both parts for @ comment conventions >>
            ch1 = s1[p1]
            if ch1 == '\r' or ch1 == '\n':
                #@+<< Compare non-critical newlines >>
                #@+node:ekr.20031218072017.3550: *5* << Compare non-critical newlines >>
                p1 = g.skip_ws_and_nl(s1, p1)
                p2 = g.skip_ws_and_nl(s2, p2)
                #@-<< Compare non-critical newlines >>
            elif ch1 == ' ' or ch1 == '\t':
                #@+<< Compare non-critical whitespace >>
                #@+node:ekr.20031218072017.3551: *5* << Compare non-critical whitespace >>
                p1 = g.skip_ws(s1, p1)
                p2 = g.skip_ws(s2, p2)
                #@-<< Compare non-critical whitespace >>
            elif ch1 == '\'' or ch1 == '"':
                #@+<< Compare possible strings >>
                #@+node:ekr.20031218072017.3555: *5* << Compare possible strings >>
                # This code implicitly assumes that string1_len == string2_len == 1.
                # The match test ensures that the language actually supports strings.
                if (g.match(s1, p1, self.string1) or g.match(s1, p1, self.string2)) and s1[p1] == s2[p2]:
                    if self.language == "pascal":
                        #@+<< Compare Pascal strings >>
                        #@+node:ekr.20031218072017.3557: *6* << Compare Pascal strings >>
                        #@+at
                        # We assume the Pascal string is on a single line so the problems with
                        # cr/lf do not concern us.
                        #@@c
                        first1 = p1; first2 = p2
                        p1 = g.skip_pascal_string(s1, p1)
                        p2 = g.skip_pascal_string(s2, p2)
                        result = s1[first1, p1] == s2[first2, p2]
                        #@-<< Compare Pascal strings >>
                    else:
                        #@+<< Compare C strings >>
                        #@+node:ekr.20031218072017.3556: *6* << Compare C strings >>
                        delim = s1[p1]
                        result = s1[p1] == s2[p2]
                        p1 += 1; p2 += 1
                        while result and p1 < len(s1) and p2 < len(s2):
                            if s1[p1] == delim and self.is_end_of_string(s1, p1, delim):
                                result = (s2[p2] == delim and self.is_end_of_string(s2, p2, delim))
                                p1 += 1; p2 += 1
                                break
                            elif g.is_nl(s1, p1) and g.is_nl(s2, p2):
                                p1 = g.skip_nl(s1, p1)
                                p2 = g.skip_nl(s2, p2)
                            else:
                                result = s1[p1] == s2[p2]
                                p1 += 1; p2 += 1
                        #@-<< Compare C strings >>
                    if not result:
                        self.mismatch("Mismatched strings")
                else:
                    #@+<< Compare single characters >>
                    #@+node:ekr.20031218072017.3553: *6* << Compare single characters >>
                    assert(p1 < len(s1) and p2 < len(s2))
                    result = s1[p1] == s2[p2]
                    p1 += 1; p2 += 1
                    if not result: self.mismatch("Mismatched single characters")
                    #@-<< Compare single characters >>
                #@-<< Compare possible strings >>
            elif ch1 == '#':
                #@+<< Compare possible preprocessor directives >>
                #@+node:ekr.20031218072017.3552: *5* << Compare possible preprocessor directives >>
                if self.language == "c":
                    #@+<< compare preprocessor directives >>
                    #@+node:ekr.20031218072017.3554: *6* << Compare preprocessor directives >>
                    # We cannot assume that newlines are single characters.
                    result = s1[p1] == s2[p2]
                    p1 += 1; p2 += 1
                    while result and p1 < len(s1) and p2 < len(s2):
                        if g.is_nl(s1, p1):
                            result = g.is_nl(s2, p2)
                            if not result or self.is_end_of_directive(s1, p1):
                                break
                            p1 = g.skip_nl(s1, p1)
                            p2 = g.skip_nl(s2, p2)
                        else:
                            result = s1[p1] == s2[p2]
                            p1 += 1; p2 += 1
                    if not result:
                        self.mismatch("Mismatched preprocessor directives")
                    #@-<< compare preprocessor directives >>
                else:
                    #@+<< compare single characters >>
                    #@+node:ekr.20140630110727.16729: *6* << Compare single characters >>
                    assert(p1 < len(s1) and p2 < len(s2))
                    result = s1[p1] == s2[p2]
                    p1 += 1; p2 += 1
                    if not result: self.mismatch("Mismatched single characters")
                    #@-<< compare single characters >>
                #@-<< Compare possible preprocessor directives >>
            elif ch1 == '<':
                # NB: support for derived noweb or CWEB file
                #@+<< Compare possible section references >>
                #@+node:ekr.20031218072017.3558: *5* << Compare possible section references >>
                if s1[p1] == '<': start_ref = "<<"
                else: start_ref = None
                # Tangling may insert newlines.
                p2 = g.skip_ws_and_nl(s2, p2)
                junk, kind1, junk2 = self.is_section_name(s1, p1)
                junk, kind2, junk2 = self.is_section_name(s2, p2)
                if start_ref and (kind1 != bad_section_name or kind2 != bad_section_name):
                    result = self.compare_section_names(s1[p1:], s2[p2:])
                    if result:
                        p1, junk1, junk2 = self.skip_section_name(s1, p1)
                        p2, junk1, junk2 = self.skip_section_name(s2, p2)
                    else: self.mismatch("Mismatched section names")
                else:
                    # Neither p1 nor p2 points at a section name.
                    result = s1[p1] == s2[p2]
                    p1 += 1; p2 += 1
                    if not result:
                        self.mismatch("Mismatch at '@' or '<'")
                #@-<< Compare possible section references >>
            elif ch1 == '@':
                #@+<< Skip @language or @comment in outline >>
                #@+node:sps.20100629094515.16518: *5* << Skip @language or @comment in outline >>
                if g.match_word(s1, p1 + 1, "language") or g.match_word(s1, p1 + 1, "comment"):
                    p1 = g.skip_line(s1, p1 + 7)
                else:
                    #@+<< Compare single characters >>
                    #@+node:ekr.20140630110727.16731: *6* << Compare single characters >>
                    assert(p1 < len(s1) and p2 < len(s2))
                    result = s1[p1] == s2[p2]
                    p1 += 1; p2 += 1
                    if not result: self.mismatch("Mismatched single characters")
                    #@-<< Compare single characters >>
                #@-<< Skip @language or @comment in outline >>
            else:
                #@+<< Compare comments or single characters >>
                #@+node:ekr.20031218072017.3559: *5* << Compare comments or single characters >>
                if g.match(s1, p1, self.sentinel) and g.match(s2, p2, self.sentinel):
                    first1 = p1; first2 = p2
                    p1 = g.skip_to_end_of_line(s1, p1)
                    p2 = g.skip_to_end_of_line(s2, p2)
                    result = self.compare_comments(s1[first1: p1], s2[first2: p2])
                    if not result:
                        self.mismatch("Mismatched sentinel comments")
                elif g.match(s1, p1, self.line_comment) and g.match(s2, p2, self.line_comment):
                    first1 = p1; first2 = p2
                    p1 = g.skip_to_end_of_line(s1, p1)
                    p2 = g.skip_to_end_of_line(s2, p2)
                    result = self.compare_comments(s1[first1: p1], s2[first2: p2])
                    if not result:
                        self.mismatch("Mismatched single-line comments")
                elif g.match(s1, p1, self.comment) and g.match(s2, p2, self.comment):
                    while(
                        p1 < len(s1) and p2 < len(s2) and
                        not g.match(s1, p1, self.comment_end) and
                        not g.match(s2, p2, self.comment_end)
                    ):
                        # ws doesn't have to match exactly either!
                        if g.is_nl(s1, p1) or g.is_ws(s1[p1]):
                            p1 = g.skip_ws_and_nl(s1, p1)
                        else: p1 += 1
                        if g.is_nl(s2, p2) or g.is_ws(s2[p2]):
                            p2 = g.skip_ws_and_nl(s2, p2)
                        else: p2 += 1
                    p1 = g.skip_ws_and_nl(s1, p1)
                    p2 = g.skip_ws_and_nl(s2, p2)
                    if g.match(s1, p1, self.comment_end) and g.match(s2, p2, self.comment_end):
                        first1 = p1; first2 = p2
                        p1 += len(self.comment_end)
                        p2 += len(self.comment_end)
                        result = self.compare_comments(s1[first1: p1], s2[first2: p2])
                    else: result = False
                    if not result:
                        self.mismatch("Mismatched block comments")
                elif g.match(s1, p1, self.comment2) and g.match(s2, p2, self.comment2):
                    while(
                        p1 < len(s1) and p2 < len(s2) and
                        not g.match(s1, p1, self.comment2_end) and
                        not g.match(s2, p2, self.comment2_end)
                    ):
                        # ws doesn't have to match exactly either!
                        if g.is_nl(s1, p1) or g.is_ws(s1[p1]):
                            p1 = g.skip_ws_and_nl(s1, p1)
                        else: p1 += 1
                        if g.is_nl(s2, p2) or g.is_ws(s2[p2]):
                            p2 = g.skip_ws_and_nl(s2, p2)
                        else: p2 += 1
                    p1 = g.skip_ws_and_nl(s1, p1)
                    p2 = g.skip_ws_and_nl(s2, p2)
                    if g.match(s1, p1, self.comment2_end) and g.match(s2, p2, self.comment2_end):
                        first1 = p1; first2 = p2
                        p1 += len(self.comment2_end)
                        p2 += len(self.comment2_end)
                        result = self.compare_comments(s1[first1: p1], s2[first2: p2])
                    else: result = False
                    if not result:
                        self.mismatch("Mismatched alternate block comments")
                else:
                    #@+<< Compare single characters >>
                    #@+node:ekr.20140630110727.16733: *6* << Compare single characters >>
                    assert(p1 < len(s1) and p2 < len(s2))
                    result = s1[p1] == s2[p2]
                    p1 += 1; p2 += 1
                    if not result: self.mismatch("Mismatched single characters")
                    #@-<< Compare single characters >>
                #@-<< Compare comments or single characters >>
        #@+<< Make sure both parts have ended >>
        #@+node:ekr.20031218072017.3560: *5* << Make sure both parts have ended >>
        if result:
            p1 = g.skip_ws_and_nl(s1, p1)
            p2 = g.skip_ws_and_nl(s2, p2)
            result = p1 >= len(s1) and p2 >= len(s2)
            if not result:
                # Show the ends of both parts.
                p1 = len(s1)
                p2 = len(s2)
                self.mismatch("One part ends before the other.")
        #@-<< Make sure both parts have ended >>
        return result
    #@+node:ekr.20031218072017.3562: *4* mismatch
    def mismatch(self, message):
        self.message = message
    #@+node:ekr.20031218072017.3563: *4* scan_derived_file (pass 2)
    #@+at
    # 
    # This function scans an entire derived file in s, discovering section or part
    # definitions.
    # 
    # This is the easiest place to delete leading whitespace from each line: we simply
    # don't copy it. We also ignore leading blank lines and trailing blank lines. The
    # resulting definition must compare equal using the "forgiving" compare to any
    # other definitions of that section or part.
    # 
    # We use a stack to handle nested expansions. The outermost level of expansion
    # corresponds to the @root directive that created the file. When the stack is
    # popped, the indent variable is restored.
    # 
    # self.root_name is the name of the file mentioned in the @root directive.
    # 
    # The caller has deleted all body_ignored_newlines from the text.
    #@@c

    def scan_derived_file(self, s):

        c = self.c
        self.def_stack = []
        #@+<< set the private global matching vars >>
        #@+node:ekr.20031218072017.2368: *5* << set the private global matching vars >>
        # Set defaults.
        self.string1 = "\""
        self.string2 = "'"
        self.verbatim = None
        # Set special cases.
        if self.language == "plain":
            self.string1 = self.string2 = None # This is debatable.
        # if you're not going to use { } for pascal comments, use
        # @comment (* *)
        # to specify the alternative
        #if self.language == "pascal":
        #    self.comment2 = "(*" ; self.comment2_end = "*)"
        self.refpart_stack = []
        self.select_next_sentinel()
        if self.language == "latex": # 3/10/03: Joo-won Jung
            self.string1 = self.string2 = None # This is debatable.
        if self.language == "html":
            self.string1 = '"'; self.string2 = None # 12/3/03

        #@-<< set the private global matching vars >>
        line_indent = 0 # The indentation to use if we see a section reference.
        # indent is the leading whitespace to be deleted.
        i, indent = g.skip_leading_ws_with_indent(s, 0, self.tab_width)
        #@+<< Skip the header line output by tangle >>
        #@+node:sps.20100622084732.12299: *5* << Skip the header line output by tangle >>
        if self.line_comment or self.comment:
            line = self.line_comment if self.line_comment else self.comment + " Created by Leo from"
            if g.match(s, i, line):
                # Even a block comment will end on the first line.
                i = g.skip_to_end_of_line(s, i)
        #@-<< Skip the header line output by tangle >>
        # The top level of the stack represents the root.
        self.push_new_DefNode(self.root_name, indent, 1, 1, True)
        while i < len(s):
            ch = s[i]
            if ch == '\r':
                i += 1 # ignore
            elif ch == '\n':
                #@+<< handle the start of a new line >>
                #@+node:ekr.20031218072017.3565: *5* << handle the start of a new line >> (Untangle)
                self.copy(ch); i += 1
                    # This works because we have one-character newlines.
                #
                # Set line_indent, used only if we see a section reference.
                junk, line_indent = g.skip_leading_ws_with_indent(s, i, c.tab_width)
                i = g.skip_leading_ws(s, i, indent, c.tab_width)
                    # skip indent leading white space.
                #@-<< handle the start of a new line >>
            elif g.match(s, i, self.sentinel) and self.is_sentinel_line(s, i):
                #@+<< handle a sentinel line  >>
                #@+node:ekr.20031218072017.3566: *5* << handle a sentinel line >>
                #@+at
                # This is the place to eliminate the proper amount of whitespace from
                # the start of each line. We do this by setting the 'indent' variable to
                # the leading whitespace of the first _non-blank_ line following the
                # opening sentinel.
                # 
                # Tangle increases the indentation by one tab if the section reference
                # is not the first non-whitespace item on the line,so self code must do
                # the same.
                #@@c

                result, junk, kind, name, part, of, end, nl_flag = self.is_sentinel_line_with_data(s, i)
                assert(result)
                #@+<< terminate the previous part of this section if it exists >>
                #@+node:ekr.20031218072017.3567: *6* << terminate the previous part of this section if it exists >>
                #@+at
                # We have just seen a sentinel line. Any kind of sentinel line will
                # terminate a previous part of the present definition. For end sentinel
                # lines, the present section name must match the name on the top of the
                # stack.
                #@@c
                if self.def_stack:
                    dn = self.def_stack[-1]
                    if self.compare_section_names(name, dn.name):
                        dn = self.def_stack.pop()
                        if dn.code:
                            thePart, found = self.ust_lookup(name, dn.part, False, False) # not root, not update
                            # Check for incompatible previous definition.
                            if found and not self.forgiving_compare(name, dn.part, dn.code, thePart.code):
                                self.error("Incompatible definitions of " + name)
                            elif not found:
                                self.ust_enter(name, dn.part, dn.of, dn.code, dn.nl_flag, False) # not root
                    elif kind == end_sentinel_line:
                        self.error(f"Missing sentinel line for {name}. found end {dn.name} instead")
                #@-<< terminate the previous part of this section if it exists >>
                if kind == start_sentinel_line:
                    indent = line_indent
                    # Increase line_indent by one tab width if the
                    # the section reference does not start the line.
                    j = i - 1
                    while j >= 0:
                        if g.is_nl(s, j):
                            break
                        elif not g.is_ws(s[j]):
                            indent += abs(self.tab_width); break
                        j -= 1
                    # copy the section reference to the _present_ section,
                    # but only if this is the first part of the section.
                    if part < 2: self.copy(name)
                    # Skip to the first character of the new section definition.
                    i = g.skip_to_end_of_line(s, i)
                    # Start the new section.
                    self.push_new_DefNode(name, indent, part, of, nl_flag)
                    self.select_next_sentinel()
                else:
                    assert(kind == end_sentinel_line)
                    # Skip the sentinel line.
                    i = g.skip_to_end_of_line(s, i)
                    # Skip a newline only if it was added after(!newline)
                    if not nl_flag:
                        i = g.skip_ws(s, i)
                        i = g.skip_nl(s, i)
                        i = g.skip_ws(s, i)
                        # Copy any whitespace following the (!newline)
                        while end and g.is_ws(s[end]):
                            self.copy(s[end])
                            end += 1
                    # Restore the old indentation level.
                    if self.def_stack:
                        indent = self.def_stack[-1].indent
                    self.select_next_sentinel(part_start_flag=False)
                #@-<< handle a sentinel line  >>
            elif g.match(s, i, self.line_comment) or g.match(s, i, self.verbatim):
                #@+<< copy the entire line >>
                #@+node:ekr.20031218072017.3568: *5* << copy the entire line >>
                j = i; i = g.skip_to_end_of_line(s, i)
                self.copy(s[j: i])
                #@-<< copy the entire line >>
            elif g.match(s, i, self.comment):
                #@+<< copy a multi-line comment >>
                #@+node:sps.20100622084732.12308: *5* << copy a multi-line comment >>
                assert(self.comment_end)
                j = i
                i += len(self.comment)
                if self.sentinel == self.comment:
                    # Scan for the ending delimiter.
                    while i < len(s) and not g.match(s, i, self.comment_end):
                        i += 1
                    if g.match(s, i, self.comment_end):
                        i += len(self.comment_end)
                    self.copy(s[j: i])
                else:
                    # Copy line by line, looking for a sentinel within the
                    # comment
                    while i < len(s):
                        if g.match(s, i, self.comment_end):
                            i += len(self.comment_end)
                            break
                        elif g.is_nl(s, i):
                            k = g.skip_nl(s, i)
                            k = g.skip_ws(s, k)
                            if self.is_sentinel_line(s, k):
                                break
                            else:
                                i = k + 1 if k + 1 <= len(s) else len(s)
                        else:
                            i += 1
                self.copy(s[j: i])
                #@-<< copy a multi-line comment >>
            elif g.match(s, i, self.string1) or g.match(s, i, self.string2):
                #@+<< copy a string >>
                #@+node:ekr.20031218072017.3569: *5* << copy a string >>
                j = i
                if self.language == "pascal":
                    i = g.skip_pascal_string(s, i)
                else:
                    i = g.skip_string(s, i)
                self.copy(s[j: i])
                #@-<< copy a string >>
            else:
                self.copy(ch); i += 1
        #@+<< end all open sections >>
        #@+node:ekr.20031218072017.3572: *5* << end all open sections >>
        dn = None
        while self.def_stack:
            dn = self.def_stack.pop()
            if self.def_stack:
                self.error("Unterminated section: " + dn.name)
        if dn:
            # Terminate the root setcion.
            i = len(s)
            if dn.code:
                self.ust_enter(dn.name, dn.part, dn.of, dn.code, dn.nl_flag, is_root_flag=True)
            else:
                self.error("Missing root part")
        else:
            self.error("Missing root section")
        #@-<< end all open sections >>
    #@+node:sps.20100623125751.16367: *4* select_next_sentinel & helper
    def select_next_sentinel(self, part_start_flag=True):
        '''
        The next sentinel will be either
        (a) a section part reference, using the "before" comment style for that part
        - when there are section references yet to interpolate for this part
        - when we're followed by another part for this section
        (b) an end sentinel using the "after" comment style for the current part
        - when we've exhausted the parts for this section
        or (c) end of file for the root section
        The above requires that the parts in the tst be aware of the section
        interpolations each part will make
        '''
        # keep a "private" copy of the tst table so that it doesn't get
        # corrupted by a subsequent tanglePass1 run
        if not self.delims_table:
            self.delims_table = self.tst
            restore_tst = self.tst
        else:
            restore_tst = self.tst
            self.tst = self.delims_table
        if self.refpart_stack == []:
            # beginning a new file
            section = self.st_lookup(self.root_name)
            assert section.__class__ == TstNode
            assert len(section.parts) == 1
            # references to sections within the part were noted by tanglePass1
            root_part = section.parts[0]
            assert root_part.__class__ == PartNode
            self.push_parts(root_part.reflist())
            # set the delimiters for the root section
            delims = section.parts[0].delims
        else:
            # we've just matched a sentinel
            if part_start_flag:
                part = self.refpart_stack.pop()
                assert part.__class__ == PartNode, (
                    "expected type PartNode, got %s" % repr(part.__class__))
                self.push_parts(part.reflist())
            else:
                s = self.refpart_stack.pop()
                assert s.__class__ == TstNode
            if self.refpart_stack:
                delims = self.refpart_stack[-1].delims
            else:
                section = self.st_lookup(self.root_name)
                delims = section.delims
        if delims[0]:
            self.line_comment = delims[0]
            self.sentinel = delims[0]
            self.sentinel_end = False
        else:
            self.line_comment = None
            self.sentinel = delims[1]
            self.sentinel_end = delims[2]
        # don't change multiline comment until after a comment convention transition is finished
        if len(self.refpart_stack) < 2 or (
            self.refpart_stack[-2].delims[1] == self.refpart_stack[-1].delims[1] and
            self.refpart_stack[-2].delims[1] == self.refpart_stack[-1].delims[2]
        ):
            self.comment = delims[1]
            self.comment_end = delims[2]
        self.tst = restore_tst
    #@+node:ekr.20140630111044.16913: *5* push_parts
    def push_parts(self, reflist):
        if not reflist:
            return
        for i in range(-1, -(len(reflist) + 1), -1):
            # push each part start delims for each reference expected
            r = reflist[i]
            # cope with undefined sections
            count = len(r.parts)
            if count > 0:
                # push the section for the end sentinel
                self.refpart_stack.append(r)
                for j in range(-1, -(count + 1), -1):
                    self.refpart_stack.append(r.parts[j])
    #@+node:ekr.20031218072017.3573: *4* update_def (untangle: pass 2)
    #@+at
    # This function handles the actual updating of section definitions in the web.
    # Only code parts are updated, never doc parts.
    # 
    # During pass 2 of Untangle, skip_body() calls this routine when it discovers the
    # definition of a section in the outline. We look up the name in the ust. If an
    # entry exists, we compare the code (the code part of an outline node) with the
    # code part in the ust. We update the code part if necessary.
    # 
    # We use the forgiving_compare() to compare code parts. It's not possible to
    # change only trivial whitespace using Untangle because forgiving_compare()
    # ignores trivial whitespace.
    #@@c
    # Major change: 2/23/01: Untangle never updates doc parts.

    def update_def(self, name, part_number, head, code, tail, is_root_flag=False):
        # Doc parts are never updated!
        p = self.p; body = p.b
        if not head: head = ""
        if not tail: tail = ""
        if not code: code = ""
        false_ret = head + code + tail, len(head) + len(code), False
        part, found = self.ust_lookup(name, part_number, is_root_flag, update_flag=True)
        if not found:
            return false_ret # Not an error.
        ucode = g.toUnicode(part.code, self.encoding)
        #@+<< Remove leading blank lines and comments from ucode >>
        #@+node:ekr.20031218072017.3574: *5* << Remove leading blank lines and comments from ucode >>
        #@+at
        # We formerly assumed that any leading comments came from an @doc part, which might
        # be the case if self.output_doc_flag were true.  For now, we treat leading comments
        # as "code".
        # 
        # Elsewhere in the code is a comment that "we never update doc parts" when untangling.
        # 
        # Needs to be dealt with.
        #@@c
        i = g.skip_blank_lines(ucode, 0)
        #@+at
        # if self.comment and self.comment_end:
        #     if ucode and g.match(ucode,j,self.comment):
        #         # Skip to the end of the block comment.
        #         i = j + len(self.comment)
        #         i = ucode.find(self.comment_end,i)
        #         if i == -1: ucode = None # An unreported problem in the user code.
        #         else:
        #             i += len(self.comment_end)
        #             i = g.skip_blank_lines(ucode,i)
        # elif self.line_comment:
        #     while ucode and g.match(ucode,j,self.line_comment):
        #         i = g.skip_line(ucode,i)
        #         i = g.skip_blank_lines(ucode,i)
        #         j = g.skip_ws(ucode,i)
        #  Only the value of ucode matters here.
        #@@c
        if ucode: ucode = ucode[i:]
        #@-<< Remove leading blank lines and comments from ucode >>
        if not ucode:
            return false_ret # Not an error.
        if code and self.forgiving_compare(name, part, code, ucode):
            return false_ret # Not an error.
        # Update the body.
        if not g.unitTesting:
            g.es("***Updating:", p.h)
        ucode = ucode.strip()
        #@+<< Add the trailing whitespace of code to ucode. >>
        #@+node:sps.20100629094515.20939: *5* << Add the trailing whitespace of code to ucode. >>
        code2 = code.rstrip()
        trail_ws = code[len(code2):]
        ucode = ucode + trail_ws
        #@-<< Add the trailing whitespace of code to ucode. >>
        #@+<< Move any @language or @comment from code to ucode >>
        #@+node:sps.20100629094515.20940: *5* << Move any @language or @comment from code to ucode >>
        # split the code into lines, collecting the @language and @comment lines specially
        # if @language or @comment are present, they get added at the end
        if code[-1] == '\n':
            leading_newline = ''
            trailing_newline = '\n'
        else:
            leading_newline = '\n'
            trailing_newline = ''
        m = self.RegexpForLanguageOrComment.regex.match(code)
        if m.group('language'):
            ucode = ucode + leading_newline
            if m.group('comment') and (m.start('language') < m.start('comment')):
                ucode = ucode + m.group('language') + "\n" + m.group('comment')
            else:
                ucode = ucode + m.group('language')
            ucode = ucode + trailing_newline
        else:
            if m.group('comment'):
                ucode = ucode + leading_newline + m.group('comment') + trailing_newline
        #@-<< Move any @language or @comment from code to ucode >>
        body = head + ucode + tail
        self.update_current_vnode(body)
        return body, len(head) + len(ucode), True
    #@+node:ekr.20031218072017.3575: *4* update_current_vnode
    def update_current_vnode(self, s):
        """Called from within the Untangle logic to update the body text of self.p."""
        c = self.c; p = self.p
        assert(self.p)
        c.setBodyString(p, s)
        c.setChanged()
        p.setDirty()
        p.setMarked()
        # 2010/02/02: was update_after_icons_changed.
        c.redraw_after_icons_changed()
    #@+node:ekr.20031218072017.3576: *3* utility methods
    #@+at These utilities deal with tangle ivars, so they should be methods.
    #@+node:ekr.20031218072017.3577: *4* compare_section_names
    # Compares section names or root names.
    # Arbitrary text may follow the section name on the same line.

    def compare_section_names(self, s1, s2):

        if g.match(s1, 0, "<<") or g.match(s1, 0, "@<"):
            # Use a forgiving compare of the two section names.
            delim = ">>"
            i1 = i2 = 0
            while i1 < len(s1) and i2 < len(s2):
                ch1 = s1[i1]; ch2 = s2[i2]
                if g.is_ws(ch1) and g.is_ws(ch2):
                    i1 = g.skip_ws(s1, i1)
                    i2 = g.skip_ws(s2, i2)
                elif g.match(s1, i1, delim) and g.match(s2, i2, delim):
                    return True
                elif ch1.lower() == ch2.lower():
                    i1 += 1; i2 += 1
                else: return False
            return False
        # A root name.
        return s1 == s2
    #@+node:ekr.20031218072017.3578: *4* copy
    def copy(self, s):
        assert self.def_stack
        # dn = self.def_stack[-1] # Add the code at the top of the stack.
        # dn.code += s
        self.def_stack[-1].code += s
            # Add the code at the top of the stack.
            # pyflakes has trouble with the commented-out code.
    #@+node:ekr.20031218072017.3579: *4* error, pathError, warning
    def error(self, s):
        self.errors += 1
        g.es_error(g.translateString(s))

    def pathError(self, s):
        if not self.path_warning_given:
            self.path_warning_given = True
            self.error(s)

    def warning(self, s):
        g.es_error(g.translateString(s))
    #@+node:ekr.20031218072017.3580: *4* is_end_of_directive
    # This function returns True if we are at the end of preprocessor directive.

    def is_end_of_directive(self, s, i):
        return g.is_nl(s, i) and not self.is_escaped(s, i)
    #@+node:ekr.20031218072017.3581: *4* is_end_of_string
    def is_end_of_string(self, s, i, delim):
        return i < len(s) and s[i] == delim and not self.is_escaped(s, i)
    #@+node:ekr.20031218072017.3582: *4* is_escaped
    # This function returns True if the s[i] is preceded by an odd number of back slashes.

    def is_escaped(self, s, i):
        back_slashes = 0; i -= 1
        while i >= 0 and s[i] == '\\':
            back_slashes += 1
            i -= 1
        return (back_slashes & 1) == 1
    #@+node:ekr.20031218072017.3583: *4* is_section_name
    def is_section_name(self, s, i):
        kind = bad_section_name; end = -1
        if g.match(s, i, "<<"):
            i, kind, end = self.skip_section_name(s, i)
        return i, kind, end
    #@+node:ekr.20031218072017.3584: *4* is_sentinel_line & is_sentinel_line_with_data
    #@+at
    # This function returns True if i points to a line a sentinel line of
    # one of the following forms:
    # 
    # start_sentinel <<section name>> end_sentinel
    # start_sentinel <<section name>> (n of m) end_sentinel
    # start_sentinel -- end -- <<section name>> end_sentinel
    # start_sentinel -- end -- <<section name>> (n of m) end_sentinel
    # 
    # start_sentinel: the string that signals the start of sentinel lines\
    # end_sentinel:   the string that signals the endof sentinel lines.
    # 
    # end_sentinel may be None,indicating that sentinel lines end with a newline.
    # 
    # Any of these forms may end with (!newline), indicating that the
    # section reference was not followed by a newline in the orignal text.
    # We set nl_flag to False if such a string is seen. The name argument
    # contains the section name.
    # 
    # The valid values of kind param are:
    # 
    # non_sentinel_line,   # not a sentinel line.
    # start_sentinel_line, #   /// <section name> or /// <section name>(n of m)
    # end_sentinel_line  //  /// -- end -- <section name> or /// -- end -- <section name>(n of m).
    #@@c

    def is_sentinel_line(self, s, i):
        result, i, kind, name, part, of, end, nl_flag = self.is_sentinel_line_with_data(s, i)
        return result

    def is_sentinel_line_with_data(self, s, i):
        start_sentinel = self.sentinel
        end_sentinel = self.sentinel_end
        #@+<< Initialize the return values >>
        #@+node:ekr.20031218072017.3585: *5* << Initialize the return values  >>
        name = end = None
        part = of = 1
        kind = non_sentinel_line
        nl_flag = True
        false_data = (False, i, kind, name, part, of, end, nl_flag)
        #@-<< Initialize the return values >>
        #@+<< Make sure the line starts with start_sentinel >>
        #@+node:ekr.20031218072017.3586: *5* << Make sure the line starts with start_sentinel >>
        if g.is_nl(s, i): i = g.skip_nl(s, i)
        i = g.skip_ws(s, i)
        # 4/18/00: We now require an exact match of the sentinel.
        if g.match(s, i, start_sentinel):
            i += len(start_sentinel)
        else:
            return false_data
        #@-<< Make sure the line starts with start_sentinel >>
        #@+<< Set end_flag if we have -- end -- >>
        #@+node:ekr.20031218072017.3587: *5* << Set end_flag if we have -- end -- >>
        # If i points to "-- end --", this code skips it and sets end_flag.
        end_flag = False
        i = g.skip_ws(s, i)
        if g.match(s, i, "--"):
            while i < len(s) and s[i] == '-':
                i += 1
            i = g.skip_ws(s, i)
            if not g.match(s, i, "end"):
                return false_data # Not a valid sentinel line.
            i += 3; i = g.skip_ws(s, i)
            if not g.match(s, i, "--"):
                return false_data # Not a valid sentinel line.
            while i < len(s) and s[i] == '-':
                i += 1
            end_flag = True
        #@-<< Set end_flag if we have -- end -- >>
        #@+<< Make sure we have a section reference >>
        #@+node:ekr.20031218072017.3588: *5* << Make sure we have a section reference >>
        i = g.skip_ws(s, i)
        if g.match(s, i, "<<"):
            j = i; i, kind, end = self.skip_section_name(s, i)
            if kind != section_ref:
                return false_data
            name = s[j: i]
        else:
            return false_data
        #@-<< Make sure we have a section reference >>
        #@+<< Set part and of if they exist >>
        #@+node:ekr.20031218072017.3589: *5* << Set part and of if they exist >>
        # This code handles (m of n), if it exists.
        i = g.skip_ws(s, i)
        if g.match(s, i, '('):
            j = i
            i += 1; i = g.skip_ws(s, i)
            i, part = self.scan_short_val(s, i)
            if part == -1:
                i = j # back out of the scanning for the number.
                part = 1
            else:
                i = g.skip_ws(s, i)
                if not g.match(s, i, "of"):
                    return false_data
                i += 2; i = g.skip_ws(s, i)
                i, of = self.scan_short_val(s, i)
                if of == -1:
                    return false_data
                i = g.skip_ws(s, i)
                if g.match(s, i, ')'):
                    i += 1 # Skip the paren and do _not_ return.
                else:
                    return false_data
        #@-<< Set part and of if they exist >>
        #@+<< Set nl_flag to False if !newline exists >>
        #@+node:ekr.20031218072017.3590: *5* << Set nl_flag to false if !newline exists >>
        line = "(!newline)"
        i = g.skip_ws(s, i)
        if g.match(s, i, line):
            i += len(line)
            nl_flag = False
        #@-<< Set nl_flag to False if !newline exists >>
        #@+<< Make sure the line ends with end_sentinel >>
        #@+node:ekr.20031218072017.3591: *5* << Make sure the line ends with end_sentinel >>
        i = g.skip_ws(s, i)
        if end_sentinel:
            # Make sure the line ends with the end sentinel.
            if g.match(s, i, end_sentinel):
                i += len(end_sentinel)
            else:
                return false_data
        end = i # Show the start of the whitespace.
        i = g.skip_ws(s, i)
        if i < len(s) and not g.is_nl(s, i):
            return false_data
        #@-<< Make sure the line ends with end_sentinel >>
        kind = end_sentinel_line if end_flag else start_sentinel_line
        return True, i, kind, name, part, of, end, nl_flag
    #@+node:sps.20100625103124.16437: *4* parent_language_comment_settings
    # side effect: sets the values within lang_dict
    # *might* lower case c.target_language

    def parent_language_comment_settings(self, p, lang_dict):
        c = self.c
        if p.hasParent():
            p1 = p.parent()
            for s in (p1.b, p1.h):
                m = self.RegexpForLanguageOrComment.regex.match(s)
                if not lang_dict['delims']:
                    if m.group('language'):
                        lang, d1, d2, d3 = g.set_language(m.group('language'), 0)
                        lang_dict['language'] = lang
                        lang_dict['delims'] = (d1, d2, d3)
                        if m.group('comment') and (m.start('comment') > m.start('language')):
                            lang_dict['delims'] = g.set_delims_from_string(m.group('comment'))
                        break
                    if m.group('comment'):
                        lang_dict['delims'] = g.set_delims_from_string(m.group('comment'))
                elif not lang_dict['language']:
                    # delims are already set, only set language
                    if m.group('language'):
                        lang, d1, d2, d3 = g.set_language(m.group('language'), 0)
                        lang.dict['language'] = lang
                        break
            if not lang_dict['language']:
                self.parent_language_comment_settings(p1, lang_dict)
        else:
            if not lang_dict['language']:
                if c.target_language:
                    c.target_language = c.target_language.lower()
                    lang, d1, d2, d3 = g.set_language(c.target_language, 0)
                    lang_dict['language'] = lang
                    if not lang_dict['delims']:
                        lang_dict['delims'] = (d1, d2, d3)
    #@+node:ekr.20031218072017.3592: *4* push_new_DefNode
    # This function pushes a new DefNode on the top of the section stack.

    def push_new_DefNode(self, name, indent, part, of, nl_flag):

        node = DefNode(name, indent, part, of, nl_flag, None)
        self.def_stack.append(node)
    #@+node:sps.20100623164631.12028: *4* refpart_stack_dump
    def refpart_stack_dump(self):
        s = "top of stack:"
        for i in range(-1, -(len(self.refpart_stack) + 1), -1):
            if self.refpart_stack[i].__class__ == PartNode:
                s += ("\nnode: " + self.refpart_stack[i].name +
                      " delims: " + repr(self.refpart_stack[i].delims))
            elif self.refpart_stack[i].__class__ == TstNode:
                s += ("\nsection: " + self.refpart_stack[i].name +
                " delims: " + repr(self.refpart_stack[i].delims))
            else:
                s += "\nINVALID ENTRY of type " + repr(self.refpart_stack[i].__class__)
        s += "\nbottom of stack.\n"
        return s
    #@+node:ekr.20031218072017.3593: *4* scan_short_val
    # This function scans a positive integer.
    # returns (i,val), where val == -1 if there is an error.

    def scan_short_val(self, s, i):
        if i >= len(s) or not s[i].isdigit():
            return i, -1
        j = i
        while i < len(s) and s[i].isdigit():
            i += 1
        val = int(s[j: i])
        return i, val
    #@+node:ekr.20031218072017.3594: *4* setRootFromHeadline
    def setRootFromHeadline(self, p):
        s = p.h
        if s[0: 5] == "@root":
            i, self.start_mode = g.scanAtRootOptions(s, 0)
            i = g.skip_ws(s, i)
            if i < len(s): # Non-empty file name.
                # self.root_name must be set later by token_type().
                self.root = s[i:]
                # implement headline @root (but create unit tests first):
                # arguments: name, is_code, is_doc
                # st_enter_root_name(self.root, False, False)
    #@+node:ekr.20031218072017.1259: *4* setRootFromText
    #@+at This code skips the file name used in @root directives.
    # 
    # File names may be enclosed in < and > characters, or in double quotes.
    # If a file name is not enclosed be these delimiters it continues until
    # the next newline.
    #@@c

    def setRootFromText(self, s, report_errors=True):

        self.root_name = None
        i, self.start_mode = g.scanAtRootOptions(s, 0)
        i = g.skip_ws(s, i)
        if i >= len(s): return i
        # Allow <> or "" as delimiters, or a bare file name.
        if s[i] == '"':
            i += 1; delim = '"'
        elif s[i] == '<':
            i += 1; delim = '>'
        else: delim = '\n'
        root1 = i # The name does not include the delimiter.
        while i < len(s) and s[i] != delim and not g.is_nl(s, i):
            i += 1
        root2 = i
        if delim != '\n' and not g.match(s, i, delim):
            if report_errors:
                g.scanError("bad filename in @root " + s[: i])
        else:
            self.root_name = s[root1: root2].strip()
        return i
    #@+node:ekr.20031218072017.3596: *4* skip_section_name
    #@+at
    # This function skips past a section name that starts with < < and might
    # end with > > or > > =. The entire section name must appear on the same
    # line.
    # 
    # Note: this code no longer supports extended noweb mode.
    # 
    # Returns (i, kind, end),
    #     end indicates the end of the section name itself (not counting the =).
    #     kind is one of:
    #         bad_section_name: "no matching ">>" or ">>"  This is _not_ a user error!
    #         section_ref: < < name > >
    #         section_def: < < name > > =
    #         at_root:     < < * > > =
    #@@c

    def skip_section_name(self, s, i):
        assert(g.match(s, i, "<<"))
        i += 2
        j = i # Return this value if no section name found.
        kind = bad_section_name; end = -1; empty_name = True
        # Scan for the end of the section name.
        while i < len(s) and not g.is_nl(s, i):
            if g.match(s, i, ">>="):
                i += 3; end = i - 1; kind = section_def; break
            elif g.match(s, i, ">>"):
                i += 2; end = i; kind = section_ref; break
            elif g.is_ws_or_nl(s, i):
                i += 1
            elif empty_name and s[i] == '*':
                empty_name = False
                i = g.skip_ws(s, i + 1) # skip the '*'
                if g.match(s, i, ">>="):
                    i += 3; end = i - 1; kind = at_root; break
            else:
                i += 1; empty_name = False
        if empty_name:
            kind = bad_section_name
        if kind == bad_section_name:
            i = j
        return i, kind, end
    #@+node:ekr.20031218072017.3598: *4* standardize_name
    def standardize_name(self, name):
        """
        Removes leading and trailing brackets,
        converts white space to a single blank and
        converts to lower case.
        """
        # Convert to lowercase.
        # Convert whitespace to a single space.
        name = name.lower().replace('\t', ' ').replace('  ', ' ')
        # Remove leading '<'
        i = 0; n = len(name)
        while i < n and name[i] == '<':
            i += 1
        j = i
        # Find the first '>'
        while i < n and name[i] != '>':
            i += 1
        name = name[j: i].strip()
        return name
    #@+node:ekr.20080923124254.16: *4* tangle.scanAllDirectives
    def scanAllDirectives(self, p):
        """Scan VNode p and p's ancestors looking for directives,
        setting corresponding tangle ivars and globals.
        """
        c = self.c
        self.init_directive_ivars()
        if not p:
            p = c.p
        if p:
            s = p.b
            #@+<< Collect @first attributes >>
            #@+node:ekr.20080923124254.17: *5* << Collect @first attributes >>
            #@+at
            # Stephen P. Schaefer 9/13/2002: Add support for @first. Unlike other
            # root attributes, does *NOT* inherit from parent nodes.
            #@@c
            tag = "@first"
            sizeString = len(s) # DTHEIN 13-OCT-2002: use to detect end-of-string
            i = 0
            while 1:
                # DTHEIN 13-OCT-2002: directives must start at beginning of a line
                if not g.match_word(s, i, tag):
                    i = g.skip_line(s, i)
                else:
                    i = i + len(tag)
                    j = i = g.skip_ws(s, i)
                    i = g.skip_to_end_of_line(s, i)
                    if i > j:
                        self.first_lines += s[j: i] + '\n'
                    i = g.skip_nl(s, i)
                if i >= sizeString: # DTHEIN 13-OCT-2002: get out when end of string reached
                    break
            #@-<< Collect @first attributes >>
        table = (
            ('encoding', self.encoding, g.scanAtEncodingDirectives),
            ('lineending', None, g.scanAtLineendingDirectives),
            ('pagewidth', c.page_width, g.scanAtPagewidthDirectives),
            ('path', None, c.scanAtPathDirectives),
            ('tabwidth', c.tab_width, g.scanAtTabwidthDirectives),
        )
        # Set d by scanning all directives.
        aList = g.get_directives_dict_list(p)
        d = {}
        for key, default, func in table:
            val = func(aList)
            d[key] = default if val is None else val
        lang_dict = {'language': None, 'delims': None}
        self.parent_language_comment_settings(p, lang_dict)
        # Post process.
        lineending = d.get('lineending')
        if lineending:
            self.output_newline = lineending
        self.encoding = d.get('encoding')
        self.language = lang_dict.get('language')
        self.init_delims = lang_dict.get('delims')
        self.page_width = d.get('pagewidth')
        self.tangle_directory = d.get('path')
        self.tab_width = d.get('tabwidth')
        # Handle the print-mode directives.
        self.print_mode = None
        for d in aList:
            for key in ('verbose', 'terse', 'quiet', 'silent'):
                if d.get(key) is not None:
                    self.print_mode = key; break
            if self.print_mode: break
        if not self.print_mode: self.print_mode = 'verbose'
        # For unit testing.
        return {
            "encoding": self.encoding,
            "language": self.language,
            "lineending": self.output_newline,
            "pagewidth": self.page_width,
            "path": self.tangle_directory,
            "tabwidth": self.tab_width,
        }
    #@+node:ekr.20031218072017.1241: *4* tangle.update_file_if_changed
    def update_file_if_changed(self, c, file_name, temp_name):
        """
        A helper for compares two files.

        If they are different, we replace file_name with temp_name.
        Otherwise, we just delete temp_name. Both files should be closed.
        """
        import filecmp
        if g.os_path_exists(file_name):
            if filecmp.cmp(temp_name, file_name):
                kind = 'unchanged'
                ok = g.utils_remove(temp_name)
            else:
                kind = '***updating'
                mode = g.utils_stat(file_name)
                ok = g.utils_rename(c, temp_name, file_name, mode)
        else:
            kind = 'creating'
            head, tail = g.os_path_split(file_name)
            ok = True
            if (
                head and c and c.config and
                c.config.create_nonexistent_directories
            ):
                theDir = c.expand_path_expression(head)
                if theDir:
                    ok = g.makeAllNonExistentDirectories(theDir)
            if ok:
                ok = g.utils_rename(c, temp_name, file_name)
        if ok:
            g.es('', f'{kind:12}: {file_name}')
        else:
            g.error("rename failed: no file created!")
            g.es('', file_name, " may be read-only or in use")
    #@+node:ekr.20031218072017.3599: *4* token_type
    def token_type(self, s, i, report_errors=True):
        """This method returns a code indicating the apparent kind of token at the position i.

        The caller must determine whether section definiton tokens are valid.

        returns (kind, end) and sets global root_name using setRootFromText().
        end is only valid for kind in (section_ref, section_def, at_root)."""
        kind = plain_line; end = -1
        #@+<< set token_type in noweb mode >>
        #@+node:ekr.20031218072017.3600: *5* << set token_type in noweb mode >>
        if g.match(s, i, "<<"):
            i, kind, end = self.skip_section_name(s, i)
            if kind == bad_section_name:
                kind = plain_line # not an error.
            elif kind == at_root:
                assert(self.head_root is None)
                if self.head_root:
                    self.setRootFromText(self.head_root, report_errors)
                else:
                    kind = bad_section_name # The warning has been given.
        elif g.match(s, i, "@ ") or g.match(s, i, "@\t") or g.match(s, i, "@\n"):
            # 10/30/02: Only @doc starts a noweb doc part in raw cweb mode.
            kind = plain_line if self.raw_cweb_flag else at_doc
        elif g.match(s, i, "@@"): kind = at_at
        elif i < len(s) and s[i] == '@': kind = at_other
        else: kind = plain_line
        #@-<< set token_type in noweb mode >>
        if kind == at_other:
            #@+<< set kind for directive >>
            #@+node:ekr.20031218072017.3602: *5* << set kind for directive >>
            # This code will return at_other for any directive other than those listed.
            if g.match_word(s, i, "@c"):
                # 10/30/02: Only @code starts a code section in raw cweb mode.
                kind = plain_line if self.raw_cweb_flag else at_code
            else:
                for name, theType in [
                    ("@chapter", at_chapter),
                    ("@code", at_code),
                    ("@doc", at_doc),
                    ("@root", at_root),
                    ("@section", at_section)
                ]:
                    if g.match_word(s, i, name):
                        kind = theType; break
            if self.raw_cweb_flag and kind == at_other:
                # 10/30/02: Everything else is plain text in raw cweb mode.
                kind = plain_line
            if kind == at_root:
                end = self.setRootFromText(s[i:], report_errors)
            #@-<< set kind for directive >>
        return kind, end
    #@-others

class TangleCommands(BaseTangleCommands):
    """A class that implements Leo' tangle and untangle commands."""
    pass
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
