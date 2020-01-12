# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20090502071837.3: * @file leoRst.py
#@@first
#@+<< docstring >>
#@+node:ekr.20090502071837.4: ** << docstring >>
"""Support for restructured text (rST), adapted from rst3 plugin.

For full documentation, see: http://leoeditor.com/rstplugin3.html

To generate documents from rST files, Python's docutils_ module must be
installed. The code will use the SilverCity_ syntax coloring package if is is
available."""
#@-<< docstring >>
# pylint: disable=global-variable-not-assigned
# for SilverCity
#@+<< imports >>
#@+node:ekr.20100908120927.5971: ** << imports >> (leoRst)
import leo.core.leoGlobals as g
verbose = 'plugins' in g.app.debug
try:
    import docutils
    import docutils.core
except ImportError:
    docutils = None
if verbose:
    print(f"leoRst3.py: docutils: {docutils}")
if docutils:
    try:
        from docutils import parsers
        if verbose or not parsers: print('leoRst.py', parsers)
        from docutils.parsers import rst
        if verbose or not rst: print('leoRst.py', rst)
        if not parsers or not rst:
            docutils = None
    except ImportError:
        docutils = None
    except Exception:
        g.es_exception()
        docutils = None
import html.parser as HTMLParser
try:
    import leo.plugins.mod_http as mod_http
except ImportError:
    mod_http = None
except Exception:
    # Don't let a problem with a plugin crash Leo's core!
    # g.es_print('leoRst: can not import leo.plugins.mod_http')
    # g.es_exception()
    mod_http = None
import pprint
import re
try:
    import SilverCity
except ImportError:
    SilverCity = None
import io
StringIO = io.StringIO
import time
#@-<< imports >>
#@+others
#@+node:ekr.20090502071837.12: ** code_block
def code_block(name, arguments, options,
    content, lineno, content_offset, block_text, state, state_machine
):
    """Implement the code-block directive for docutils."""
    try:
        language = arguments[0]
        # See http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/252170
        module = SilverCity and getattr(SilverCity, language)
        generator = module and getattr(module, language + "HTMLGenerator")
        if generator:
            io = StringIO()
            generator().generate_html(io, '\n'.join(content))
            html = '<div class="code-block">\n%s\n</div>\n' % io.getvalue()
        else:
            html = '<div class="code-block">\n%s\n</div>\n' % '<br>\n'.join(content)
        raw = docutils.nodes.raw('', html, format='html')
        return [raw]
    except Exception: # Return html as shown.  Lines are separated by <br> elements.
        g.es_trace('exception in rst3:code_block()')
        g.es_exception()
        return [None]
# See http://docutils.sourceforge.net/spec/howto/rst-directives.html

code_block.arguments = (
    1, # Number of required arguments.
    0, # Number of optional arguments.
    0) # True if final argument may contain whitespace.
# A mapping from option name to conversion function.
if docutils:
    code_block.options = {
        'language':
        docutils.parsers.rst.directives.unchanged
            # Return the text argument, unchanged.
    }
    code_block.content = 1 # True if content is allowed.
    # Register the directive with docutils.
    docutils.parsers.rst.directives.register_directive('code-block', code_block)
else:
    code_block.options = {}
#@+node:ekr.20090502071837.33: ** class RstCommands
class RstCommands:
    """
    A class to write rst markup in Leo outlines.

    This class optionally stores information for the http plugin.
    Each node may have an rst_http_attributename attribute, a list.
    The first three elements are a stack of tags, the rest is html code::

        [
            <tag n start>, <tag n end>, <other stack elements>,
            <html line 1>, <html line 2>, ...
        ]

    <other stack elements> has the same structure::

        [<tag n-1 start>, <tag n-1 end>, <other stack elements>]

    """
    #@+others
    #@+node:ekr.20090502071837.34: *3* rst.Birth
    #@+node:ekr.20090502071837.35: *4*  rst.ctor & rst.reloadSettings
    def __init__(self, c):
        """Ctor for the RstCommand class."""
        global SilverCity
        self.c = c
        # Debugging and statistics.
        self.debug = False # Set in reloadSettings.
        self.n_written = 0
            # Number of files written.
        # Warning flags.
        self.silverCityWarningGiven = False
        # Settings.
        self.dd = {}
            # A dict of dict. Keys are vnodes.
            # Values are dicts of settings defined in that vnode *only*.
        self.d0 = self.createD0()
            # Keys are vnodes, values are optionsDict's.
        self.scriptSettingsDict = {}
            # For format-code command.
        self.singleNodeOptions = [
            'ignore_this_headline', 'ignore_this_node', 'ignore_this_tree',
            'preformat_this_node', 'show_this_headline',
        ]
        # Formatting...
        self.code_block_string = ''
        self.node_counter = 0
        self.topLevel = 0
        self.topNode = None
        self.use_alternate_code_block = SilverCity is None
        # Http support...
        self.nodeNumber = 0
            # All nodes are numbered so that unique anchors can be generated.
        self.http_map = {}
            # Keys are named hyperlink targets.  Value are positions.
            # The targets mark the beginning of the html code specific
            # for this position.
        self.anchor_map = {}
            # Maps anchors (generated by this module) to positions
        self.rst3_all = False
            # Set to True by the button which processes all @rst trees.
        # For writing.
        self.atAutoWrite = False
            # True, special cases for writeAtAutoFile.
        self.atAutoWriteUnderlines = ''
            # Forced underlines for writeAtAutoFile.
        self.leoDirectivesList = g.globalDirectiveList
        self.encoding = 'utf-8'
            # The encoding from any @encoding directive. Set by init_write.
        self.rst_nodes = []
            # The list of positions for all @rst nodes.
        self.outputFile = None
            # The open file being written.
        self.path = ''
            # The path from any @path directive. Set by init_write.
            # May be overridden (in computeOutputFileName() by rst3_default_path option.
        self.root = None
            # The @rst node being processed.
        self.source = None
            # The written source as a string.
        # Complete the init.
        self.reloadSettings()
        self.updateD0FromSettings()
        self.initHeadlineCommands()

    def reloadSettings(self):
        """RstCommand.reloadSettings"""
        self.debug = self.c.config.getBool('rst3-debug', default=False)
        
    #@+node:ekr.20150509035745.1: *4* rst.cmd (decorator)
    def cmd(name):
        """Command decorator for the RstCommands class."""
        # pylint: disable=no-self-argument
        return g.new_cmd_decorator(name, ['c', 'rstCommands',])
    #@+node:ekr.20090502071837.42: *4* rst.createD0
    def createD0(self):
        """Create the default options dict."""
        d = {
            # Reporting options...
            'debug': False, # True: enables debug output.
            'silent': False, # True: suppresses report()
            'verbose': True, # True: rst.report() sends to log.
            # Http options...
            'clear_http_attributes': False,
            'http_server_support': False,
            'http_attributename': 'rst_http_attribute',
            'node_begin_marker': 'http-node-marker-',
            # Path options...
            'default_path': None,
                # Must be None, not ''.
                # computeOutputFileName() uses it instead of self.path.
            'stylesheet_name': 'default.css',
            'stylesheet_path': None, # Must be None, not ''.
            'stylesheet_embed': True,
            'publish_argv_for_missing_stylesheets': None,
            # Code generation options...
            'call_docutils': True,
            'code_block_string': '',
            'number_code_lines': True,
            'underline_characters': """#=+*^~"'`-:><_""",
            'write_intermediate_file': False,
                # Used only if generate_rst is True.
            'write_intermediate_extension': '.txt',
            # Mode options...
            'code_mode': False,
                # True: generate rst markup from @code and @doc parts.
            'doc_only_mode': False,
                # True: generate only from @doc parts.
            'generate_rst': True,
                # True: generate rst markup. False: generate plain text.
            'generate_rst_header_comment': True,
                # True generate header comment (requires generate_rst option)
            # Formatting options that apply to both code and rst modes....
            'expand_noweb_references': False,
            'ignore_noweb_definitions': False,
            'expand_noweb_recursively': True,
            'show_headlines': True, # Can be set by @rst-no-head headlines.
            'show_organizer_nodes': True,
            'show_options_nodes': False,
            'show_sections': True,
            'strip_at_file_prefixes': True,
            'show_doc_parts_in_rst_mode': True,
            # Formatting options that apply only to code mode.
            'show_doc_parts_as_paragraphs': False,
            'show_leo_directives': True,
            'show_markup_doc_parts': False,
            'show_options_doc_parts': False,
        }
        # Check that all dictionary keys are already munged.
        for key in sorted(d.keys()):
            assert key == self.munge(key), key
        return d
    #@+node:ekr.20090502071837.38: *4* rst.initHeadlineCommands
    def initHeadlineCommands(self):
        """Init the list of headline commands used by writeHeadline."""
        self.headlineCommands = [
            '@rst',
            '@rst-code',
            '@rst-default-path',
            '@rst-doc-only',
            '@rst-head',
            '@rst-ignore-node',
            '@rst-ignore-tree',
            '@rst-ignore',
            '@rst-no-head',
            '@rst-no-headlines',
            '@rst-table', # New in Leo 5.3.
            '@rst-option',
            '@rst-options',
            '@rst-preformat', # Fix #286.
        ]
    #@+node:ekr.20090502071837.40: *4* rst.munge
    def munge(self, name):
        """Convert an option name to the equivalent ivar name."""
        i = 3 if name.startswith('rst') else 0
        while i < len(name) and name[i].isdigit():
            i += 1
        if i < len(name) and name[i] == '_':
            i += 1
        s = name[i:].lower()
        s = s.replace('-', '_')
        return s
    #@+node:ekr.20150320033317.10: *4* rst.updateD0FromSettings
    def updateD0FromSettings(self):
        """Update entries in self.d0 from user seettings."""
        c, d = self.c, self.d0
        table = (
            ('@bool', c.config.getBool),
            ('@string', c.config.getString),
        )
        for key in sorted(d):
            for kind, f in table:
                val = f('rst3_' + key)
                if val is not None:
                    old = d.get(key)
                    if val != old:
                        d[key] = val
                    break
        # Special warning for mod_http plugin.
        if not mod_http and c.config.getBool('http-server-support'):
            g.error('No http_server_support: can not import mod_http plugin')
            d['http_server_support'] = False
    #@+node:ekr.20100813041139.5920: *3* rst.Entry points
    #@+node:ekr.20100812082517.5945: *4* rst.code_to_rst_command & helpers
    @cmd('code-to-rst')
    def code_to_rst_command(self, event=None, p=None, scriptSettingsDict=None, toString=False):
        """
        Format the presently selected node as computer code.
        Settings from scriptSettingsDict override normal settings.

        On exit:
            self.source contains rst sources
            self.stringOutput contains docutils output if docutils called.

        **Important**: This command works as much like the rst3 command as possible.
        Difference arise because there is no @rst node to specify a filename.
        Instead we get the filename from scriptSettingsDict, or use 'code_to_rst.html'
        """
        c = self.c
        if p: p = p.copy()
        else: p = c.p
        self.topNode = p.copy()
        self.topLevel = p.level()
        self.initSettings(p, script_d=scriptSettingsDict)
        callDocutils = self.getOption(p, 'call_docutils')
        writeIntermediateFile = self.getOption(p, 'write_intermediate_file')
        fn = self.getOption(p, 'output-file-name') or 'code_to_rst.html'
        junk, ext = g.os_path_splitext(fn)
        # Write the rst sources to self.sources...
        self.outputFile = StringIO()
        self.write_code_tree(p, fn)
        self.source = self.outputFile.getvalue()
        self.outputFile = None
        if callDocutils or writeIntermediateFile:
            self.write_files(ext, fn, p,
                callDocutils=callDocutils,
                toString=toString,
                writeIntermediateFile=writeIntermediateFile)
    #@+node:ekr.20100812082517.5963: *5* rst.write_code_body & helpers
    def write_code_body(self, p):

        self.p = p.copy() # for traces.
        if not p.b.strip():
            return # No need to write any more newlines.
        showDocsAsParagraphs = self.getOption(p, 'show_doc_parts_as_paragraphs')
        lines = g.splitLines(p.b)
        parts = self.split_parts(lines, showDocsAsParagraphs)
        result = []
        for kind, lines in parts:
            if kind == '@rst-option': # Also handles '@rst-options'
                pass # The prepass has already handled the options.
            elif kind == '@rst-markup':
                lines.extend('\n')
                result.extend(lines)
            elif kind == '@doc':
                if showDocsAsParagraphs:
                    result.extend(lines)
                    result.append('\n')
                else:
                    result.extend(self.write_code_block(p, lines))
            elif kind == 'code':
                result.extend(self.write_code_block(p, lines))
            else:
                g.trace('Can not happen', kind)
        # Write the lines with exactly two trailing newlines.
        s = ''.join(result).rstrip() + '\n\n'
        self.write(s)
    #@+node:ekr.20100812082517.5964: *6* rst.split_parts
    def split_parts(self, lines, showDocsAsParagraphs):
        """Split a list of body lines into a list of tuples (kind,lines)."""
        kind, parts, part_lines = 'code', [], []
        for s in lines:
            if g.match_word(s, 0, '@ @rst-markup'):
                if part_lines: parts.append((kind, part_lines[:]),)
                kind = '@rst-markup'
                n = len('@ @rst-markup')
                after = s[n:].strip()
                part_lines = [after] if after else []
            elif s.startswith('@ @rst-option'):
                if part_lines: parts.append((kind, part_lines[:]),)
                kind, part_lines = '@rst-option', [s] # part_lines will be ignored.
            elif s.startswith('@ ') or s.startswith('@\n') or s.startswith('@doc'):
                if showDocsAsParagraphs:
                    if part_lines: parts.append((kind, part_lines[:]),)
                    kind = '@doc'
                    # Put only what follows @ or @doc
                    n = 4 if s.startswith('@doc') else 1
                    after = s[n:].lstrip()
                    part_lines = [after] if after else []
                else:
                    part_lines.append(s) # still in code mode.
            elif g.match_word(s, 0, '@c') and kind != 'code':
                if kind == '@doc' and not showDocsAsParagraphs:
                    part_lines.append(s) # Show the @c as code.
                parts.append((kind, part_lines[:]),)
                kind, part_lines = 'code', []
            else:
                part_lines.append(s)
        if part_lines:
            parts.append((kind, part_lines[:]),)
        return parts
    #@+node:ekr.20100812082517.5965: *6* rst.write_code_block
    def write_code_block(self, p, lines):
        """Write a docutils code-block directive."""
        result = ['::\n\n'] # ['[**code block**]\n\n']
        if self.getOption(p, 'number-code-lines'):
            for i, s in enumerate(lines):
                result.append(f"    {i}: {s}")
        else:
            result.extend([f"    {z}" for z in lines])
        s = ''.join(result).rstrip() + '\n\n'
        return g.splitLines(s)
    #@+node:ekr.20100812082517.5966: *5* rst.write_code_headline & helper
    def write_code_headline(self, p):
        """
        Generate an rST section if options permit it.
        Remove headline commands from the headline first,
        and never generate an rST section for @rst-option and @rst-options.
        """
        docOnly = self.getOption(p, 'doc_only_mode')
        ignore = self.getOption(p, 'ignore_this_headline')
        showHeadlines = self.getOption(p, 'show_headlines')
        showThisHeadline = self.getOption(p, 'show_this_headline')
        showOrganizers = self.getOption(p, 'show_organizer_nodes')
        if (
            p == self.topNode or
            ignore or
            docOnly or # handleDocOnlyMode handles this.
            not showHeadlines and not showThisHeadline or
            # docOnly and not showOrganizers and not thisHeadline or
            not p.h.strip() and not showOrganizers or
            not p.b.strip() and not showOrganizers
        ):
            return
        self.write_code_headline_helper(p)
    #@+node:ekr.20100812082517.5967: *6* rst.write_code_headline_helper
    def write_code_headline_helper(self, p):
        """Write a headline in code mode."""
        h = p.h.strip()
        # Remove any headline command before writing the headline.
        i = g.skip_ws(h, 0)
        i = g.skip_id(h, 0, chars='@-')
        word = h[: i].strip()
        if word:
            # Never generate a section for these:
            # @rst-option or @rst-options or @rst-no-head.
            if word in (
                '@rst-option', '@rst-options',
                '@rst-no-head', '@rst-no-headlines',
                '@rst-table', # New in Leo 5.3.
            ):
                return
            for prefix in (
                '@rst-ignore-node',
                '@rst-ignore-tree',
                '@rst-ignore',
            ):
                if word == prefix:
                    h = h[len(word):].strip()
                    break
        if not h.strip():
            pass
        elif self.getOption(p, 'show_sections'):
            self.write(self.underline(h, p))
        else:
            self.write('\n**%s**\n\n' % h.replace('*', ''))
    #@+node:ekr.20100812082517.5968: *5* rst.write_code_node
    def write_code_node(self, p):
        """
        Format a node according to the options presently in effect.
        Side effect: advance p
        """
        h = p.h.strip()
        if self.getOption(p, 'ignore_this_tree'):
            p.moveToNodeAfterTree()
        elif self.getOption(p, 'ignore_this_node'):
            p.moveToThreadNext()
        elif (
            g.match_word(h, 0, '@rst-options') and
            not self.getOption(p, 'show_options_nodes')
        ):
            p.moveToThreadNext()
        else:
            self.http_addNodeMarker(p)
            self.write_code_headline(p)
            self.write_code_body(p)
            p.moveToThreadNext()
    #@+node:ekr.20100812082517.5939: *5* rst.write_code_tree
    def write_code_tree(self, p, fn):
        """Write p's tree as code to self.outputFile."""
        if self.getOption(p, 'generate_rst_header_comment'):
            self.write('.. rst3: filename: %s\n\n' % fn)
        # We can't use an iterator because we may skip parts of the tree.
        p = p.copy()
        self.topNode = p.copy()
        after = p.nodeAfterTree()
        while p and p != after:
            self.write_code_node(p) # Side effect: advances p.
    #@+node:ekr.20090511055302.5793: *4* rst.rst3 command & helpers
    @cmd('rst3')
    def rst3(self, event=None):
        """Write all @rst nodes."""
        t1 = time.time()
        self.rst_nodes = []
        self.n_written = 0
        self.processTopTree(self.c.p)
        t2 = time.time()
        g.es_print('rst3: %s files in %4.2f sec.' % (self.n_written, t2 - t1))
        return self.rst_nodes # A list of positions.
    #@+node:ekr.20090502071837.62: *5* rst.processTopTree
    def processTopTree(self, p, justOneFile=False):
        """Find and handle all @rst and @slides node associated with p."""

        def predicate(p):
            # pylint: disable=consider-using-ternary
            h = p.h if p else ''
            return (
                h.startswith('@rst') and not h.startswith('@rst-') or
                h.startswith('@slides'))

        roots = g.findRootsWithPredicate(self.c, p, predicate=predicate)
        if roots:
            for p in roots:
                self.root = p.copy()
                self.processTree(p, ext=None, toString=False, justOneFile=justOneFile)
        else:
            g.warning('No @rst or @slides nodes in', p.h)
    #@+node:ekr.20090502071837.63: *5* rst.processTree
    def processTree(self, p, ext=None, toString=False, justOneFile=False):
        """
        Process all @rst nodes in a tree.
        ext is the docutils extention: it's useful for scripts and unit tests.
        """
        self.stringOutput = ''
        p = p.copy()
        after = p.nodeAfterTree()
        while p and p != after:
            h = p.h.strip()
            if g.match_word(h, 0, '@rst-ignore-tree'):
                p.moveToNodeAfterTree()
            elif g.match_word(h, 0, '@rst-ignore') or g.match_word(h, 0, '@rst-ignore-node'):
                p.moveToThreadNext()
            elif g.match_word(h, 0, "@rst"):
                self.rst_nodes.append(p.copy())
                fn = h[4:].strip()
                if ((fn and fn[0] != '-') or (toString and not fn)):
                    self.write_rst_tree(p, ext, fn, toString=toString, justOneFile=justOneFile)
                    if toString:
                        return p.copy(), self.stringOutput
                    p.moveToNodeAfterTree()
                else:
                    p.moveToThreadNext()
            elif g.match(h, 0, "@slides"):
                self.write_slides(p)
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
        return None, None
    #@+node:ekr.20090502071837.64: *5* rst.write_rst_tree
    def write_rst_tree(self, p, ext, fn, toString=False, justOneFile=False):
        """
        Convert p's tree to rst sources.
        Optionally call docutils to convert rst to output.

        On exit:
            self.source contains rst sources
            self.stringOutput contains docutils output if docutils called.
        """
        self.n_written += 1
        self.topNode = p.copy()
        self.topLevel = p.level()
        self.initSettings(p.copy()) # 2017/02/19
        if toString:
            ext = ext or '.html' # 2010/08/12: Unit test found this.
        else:
            junk, ext = g.os_path_splitext(fn)
        ext = ext.lower()
        if not ext.startswith('.'): ext = '.' + ext
        self.init_write(p) # sets self.path and self.encoding.
        callDocutils = self.getOption(p, 'call_docutils')
        writeIntermediateFile = self.getOption(p, 'write_intermediate_file')
        # Write the rst sources to self.source.
        self.outputFile = StringIO()
        self.writeTree(p, fn)
        self.source = self.outputFile.getvalue() # the rST sources.
        self.outputFile = None
        self.stringOutput = None
        if callDocutils or writeIntermediateFile:
            self.write_files(ext, fn, p,
                callDocutils=callDocutils,
                toString=toString,
                writeIntermediateFile=writeIntermediateFile)
    #@+node:ekr.20100822092546.5835: *5* rst.write_slides & helper
    def write_slides(self, p, toString=False):
        """Convert p's children to slides."""
        p = p.copy(); h = p.h
        i = g.skip_id(h, 1) # Skip the '@'
        kind, fn = h[: i].strip(), h[i:].strip()
        if not fn:
            g.error(f"{kind} requires file name")
            return
        title = p.firstChild().h if p and p.firstChild() else '<no slide>'
        title = title.strip().capitalize()
        n_tot = p.numberOfChildren()
        n = 1
        for child in p.children():
            self.init_write(p) # sets self.path and self.encoding.
            # Compute the slide's file name.
            fn2, ext = g.os_path_splitext(fn)
            fn2 = '%s-%03d%s' % (fn2, n, ext) # Use leading zeros for :glob:.
            n += 1
            # Write the rst sources to self.source.
            self.outputFile = StringIO()
            self.writeSlideTitle(title, n - 1, n_tot)
            self.writeBody(child)
            self.source = self.outputFile.getvalue() # the rST sources.
            self.outputFile, self.stringOutput = None, None
            self.write_files(ext, fn2, p,
                callDocutils=self.getOption(p, 'call_docutils'),
                toString=toString,
                writeIntermediateFile=self.getOption(p, 'write_intermediate_file'))
    #@+node:ekr.20100822174725.5836: *6* rst.writeSlideTitle
    def writeSlideTitle(self, title, n, n_tot):
        """Write the title, underlined with the '#' character."""
        if n != 1:
            title = f"{title} ({n} of {n_tot})"
        width = max(4, len(g.toEncodedString(title,
            encoding=self.encoding, reportErrors=False)))
        self.write('%s\n%s \n\n' % (title, ('#' * width)))
    #@+node:ekr.20090502071837.58: *5* rst.write methods
    #@+node:ekr.20090502071837.68: *6* rst.getDocPart
    def getDocPart(self, lines, n):

        result = []
        #@+<< Append whatever follows @doc or @space to result >>
        #@+node:ekr.20090502071837.69: *7* << Append whatever follows @doc or @space to result >>
        if n > 0:
            line = lines[n - 1]
            if line.startswith('@doc'):
                s = line[4:].lstrip()
            elif line.startswith('@'):
                s = line[1:].lstrip()
            else:
                s = ''
            # New in Leo 4.4.4: remove these special tags.
            for tag in ('@rst-options', '@rst-option', '@rst-markup'):
                if g.match_word(s, 0, tag):
                    s = s[len(tag):].strip()
            if s.strip():
                result.append(s)
        #@-<< Append whatever follows @doc or @space to result >>
        while n < len(lines):
            s = lines[n]; n += 1
            if g.match_word(s, 0, '@code') or g.match_word(s, 0, '@c'):
                break
            result.append(s)
        return n, result
    #@+node:ekr.20090502071837.81: *6* rst.handleSpecialDocParts
    def handleSpecialDocParts(self, lines, kind, retainContents, asClass=None):

        result = []; n = 0
        while n < len(lines):
            s = lines[n]; n += 1
            if s.strip().endswith('::'):
                n, lit = self.skip_literal_block(lines, n - 1)
                result.extend(lit)
            elif self.isSpecialDocPart(s, kind):
                n, lines2 = self.getDocPart(lines, n)
                if retainContents:
                    result.extend([''])
                    if asClass:
                        result.extend(['.. container:: ' + asClass, ''])
                        if 'literal' in asClass.split():
                            result.extend(['  ::', ''])
                        for l2 in lines2: result.append('    ' + l2)
                    else:
                        result.extend(lines2)
                    result.extend([''])
            else:
                result.append(s)
        return result
    #@+node:ekr.20090502071837.77: *6* rst.isAnyDocPart
    def isAnyDocPart(self, s):
        if s.startswith('@doc'):
            return True
        if not s.startswith('@'):
            return False
        return len(s) == 1 or s[1].isspace()
    #@+node:ekr.20090502071837.79: *6* rst.isAnySpecialDocPart
    def isAnySpecialDocPart(self, s):
        for kind in (
            '@rst-markup',
            '@rst-option',
            '@rst-options',
        ):
            if self.isSpecialDocPart(s, kind):
                return True
        return False
    #@+node:ekr.20090502071837.78: *6* rst.isSpecialDocPart
    def isSpecialDocPart(self, s, kind):
        """
        Return True if s is a special doc part of the indicated kind.

        If kind is None, return True if s is any doc part.
        """
        if s.startswith('@') and len(s) > 1 and s[1].isspace():
            if kind:
                i = g.skip_ws(s, 1)
                result = g.match_word(s, i, kind)
            else:
                result = True
        elif not kind:
            result = g.match_word(s, 0, '@doc') or g.match_word(s, 0, '@')
        else:
            result = False
        return result
    #@+node:ekr.20090502071837.80: *6* rst.removeLeoDirectives
    def removeLeoDirectives(self, lines):
        """Remove all Leo directives, except within literal blocks."""
        n = 0; result = []
        while n < len(lines):
            s = lines[n]; n += 1
            if s.strip().endswith('::'):
                n, lit = self.skip_literal_block(lines, n - 1)
                result.extend(lit)
            elif s.startswith('@') and not self.isAnySpecialDocPart(s):
                for key in self.leoDirectivesList:
                    if g.match_word(s, 1, key):
                        break
                else:
                    result.append(s)
            else:
                result.append(s)
        return result
    #@+node:ekr.20090502071837.82: *6* rst.replaceCodeBlockDirectives
    def replaceCodeBlockDirectives(self, lines):
        """Replace code-block directive, but not in literal blocks."""
        n = 0; result = []
        while n < len(lines):
            s = lines[n]; n += 1
            if s.strip().endswith('::'):
                n, lit = self.skip_literal_block(lines, n - 1)
                result.extend(lit)
            else:
                i = g.skip_ws(s, 0)
                if g.match(s, i, '..'):
                    i = g.skip_ws(s, i + 2)
                    if g.match_word(s, i, 'code-block'):
                        if 1: # Create a literal block to hold the code.
                            result.append('::\n')
                        else: # This 'annotated' literal block is confusing.
                            result.append('%s code::\n' % s[i + len('code-block'):])
                    else:
                        result.append(s)
                else:
                    result.append(s)
        return result
    #@+node:ekr.20090502071837.70: *6* rst.skip_literal_block
    def skip_literal_block(self, lines, n):
        s = lines[n]; result = [s]; n += 1
        indent = g.skip_ws(s, 0)
        # Skip lines until a non-blank line is found with same or less indent.
        while n < len(lines):
            s = lines[n]
            indent2 = g.skip_ws(s, 0)
            if s and not s.isspace() and indent2 <= indent:
                break # We will rescan lines [n]
            n += 1
            result.append(s)
        # g.printList(result,tag='literal block')
        return n, result
    #@+node:ekr.20090502071837.71: *6* rst.writeBody & helpers
    def writeBody(self, p):
        """Write p.b as rST."""
        if self.getOption(p, 'ignore_noweb_definitions'):
            # Ignore section definition nodes.
            name = self.isSectionDef(p)
            if name:
                return
        # remove trailing cruft and split into lines.
        lines = g.splitLines(p.b)
        if self.getOption(p, 'code_mode'):
            # Important: code mode is no longer documented!
            if not self.getOption(p, 'show_options_doc_parts'):
                lines = self.handleSpecialDocParts(lines, '@rst-options',
                    retainContents=False)
            if not self.getOption(p, 'show_markup_doc_parts'):
                lines = self.handleSpecialDocParts(lines, '@rst-markup',
                    retainContents=False)
            if not self.getOption(p, 'show_leo_directives'):
                lines = self.removeLeoDirectives(lines)
            lines = self.handleCodeMode(p, lines)
        elif self.getOption(p, 'doc_only_mode'):
            lines = self.handleDocOnlyMode(p, lines)
        else:
            lines = self.handleSpecialDocParts(lines, '@rst-options',
                retainContents=False)
            lines = self.handleSpecialDocParts(lines, '@rst-markup',
                retainContents=self.getOption(p, 'generate_rst'))
            if self.getOption(p, 'show_doc_parts_in_rst_mode') is True:
                pass # original behaviour, treat as plain text
            elif self.getOption(p, 'show_doc_parts_in_rst_mode'):
                # use value as class for content
                lines = self.handleSpecialDocParts(lines, None,
                    retainContents=True, asClass=self.getOption(p, 'show_doc_parts_in_rst_mode'))
            else: # option evaluates to false, cut them out
                lines = self.handleSpecialDocParts(lines, None,
                    retainContents=False)
            lines = self.removeLeoDirectives(lines)
            if self.getOption(p, 'expand_noweb_references'):
                lines = self.expandSectionRefs(lines, p, seen=[])
            if self.getOption(p, 'generate_rst') and self.getOption(p, 'use_alternate_code_block'):
                lines = self.replaceCodeBlockDirectives(lines)
        # Write the lines.
        s = ''.join(lines)
        if self.getOption(p, 'table'):
            # Support @rst-table: Leo 5.3.
            s = s.rstrip()+'\n'
        else:
            # We no longer add newlines to the start of nodes because
            # we write a blank line after all sections.
            s = g.ensureTrailingNewlines(s, 2)
        self.write(s)
    #@+node:ekr.20110610144305.6749: *7* rst.isSectionDef/Ref
    def isSectionDef(self, p):
        return self.isSectionRef(p.h)

    def isSectionRef(self, s):
        n1 = s.find("<<", 0)
        n2 = s.find(">>", 0)
        return -1 < n1 < n2 and s[n1 + 2: n2].strip()
    #@+node:ekr.20110610144305.6750: *7* rst.expandSectionRefs
    def expandSectionRefs(self, lines, p, seen):
        """Expand section references in lines."""
        result = []
        for s in lines:
            name = self.isSectionRef(s)
            if name:
                p2 = self.findSectionDef(name, p)
                if p2:
                    g.trace(f"expanding: {name} from {p2.h}")
                    result.append(s) # Append the section reference line.
                    lines2 = g.splitLines(p2.b)
                    if self.getOption(p, 'expand_noweb_recursively'):
                        if name in seen:
                            pass # Prevent unbounded recursion
                        else:
                            seen.append(name)
                            result.extend(self.expandSectionRefs(lines2, p, seen))
                    else:
                        result.extend(lines2)
                else:
                    # Undefined reference.
                    result.append(s)
            else:
                result.append(s)
        return result
    #@+node:ekr.20110610144305.6751: *7* rst.findSectionDef
    def findSectionDef(self, name, p):
        for p2 in p.subtree():
            name2 = self.isSectionDef(p2)
            if name2:
                return p2
        return None
    #@+node:ekr.20090502071837.72: *7* rst.handleCodeMode & helper
    def handleCodeMode(self, p, lines):
        """
        Handle the preprocessed body text in code mode as follows:

        - Blank lines are copied after being cleaned.
        - @ @rst-markup lines get copied as is.
        - Everything else gets put into a code-block directive.
        """
        result = []; n = 0; code = []
        while n < len(lines):
            s = lines[n]; n += 1
            if (
                self.isSpecialDocPart(s, '@rst-markup') or (
                    self.getOption(p, 'show_doc_parts_as_paragraphs') and
                    self.isSpecialDocPart(s, None)
                )
            ):
                if code:
                    self.finishCodePart(code, p, result)
                    code = []
                result.append('')
                n, lines2 = self.getDocPart(lines, n)
                # A fix, perhaps dubious, to a bug discussed at
                # http://groups.google.com/group/leo-editor/browse_thread/thread/c212814815c92aac
                result.extend(lines2)
            elif not s.strip() and not code:
                pass # Ignore blank lines before the first code block.
            else:
                if not code: # Start the code block.
                    result.append('')
                    result.append(self.code_block_string)
                code.append(s)
        if code:
            self.finishCodePart(code, p, result)
            code = []
        # Munge the result so as to keep docutils happy.
        # Don't use self.rstripList: it's not the same.
        result2 = []
        for z in result:
            if z == '': result2.append('\n\n')
            # Fix bug 618482.
            elif z.endswith('\n\n'):
                result2.append(z) # Leave alone.
            else:
                result2.append('%s\n' % z.rstrip())
        return result2
    #@+node:ekr.20090502071837.73: *8* rst.formatCodeModeLine
    def formatCodeModeLine(self, s, n, numberOption):
        if not s.strip(): s = ''
        if numberOption:
            return f'\t{n}: {s}'
        return f'\t{s}'
    #@+node:ekr.20090502071837.74: *8* rst.rstripList
    def rstripList(self, theList):
        """Removed trailing blank lines from theList."""
        # 2010/08/27: fix bug 618482.
        s = ''.join(theList).rstrip()
        return s.split('\n')
    #@+node:ekr.20090502071837.75: *8* rst.finishCodePart
    def finishCodePart(self, code, p, result):
        """Finish writing a code part."""
        numberOption = self.getOption(p, 'number_code_lines')
        lines = self.rstripList(code)
        for i, line in enumerate(lines):
            result.append(self.formatCodeModeLine(line, i + 1, numberOption))
    #@+node:ekr.20090502071837.76: *7* rst.handleDocOnlyMode
    def handleDocOnlyMode(self, p, lines):
        """
        Handle the preprocessed body text in doc_only mode as follows:

        - Blank lines are copied after being cleaned.
        - @ @rst-markup lines get copied as is.
        - All doc parts get copied.
        - All code parts are ignored.
        """
        showHeadlines = self.getOption(p, 'show_headlines')
        showThisHeadline = self.getOption(p, 'show_this_headline')
        showOrganizers = self.getOption(p, 'show_organizer_nodes')
        n, result = 0, []
        while n < len(lines):
            s = lines[n]; n += 1
            if self.isSpecialDocPart(s, '@rst-options'):
                n, lines2 = self.getDocPart(lines, n) # ignore.
            elif self.isAnyDocPart(s):
                # Handle any other doc part, including @rst-markup.
                n, lines2 = self.getDocPart(lines, n)
                if lines2: result.extend(lines2)
        if showHeadlines:
            if result or showThisHeadline or showOrganizers or p == self.topNode:
                self.writeHeadlineHelper(p)
        return result
    #@+node:ekr.20090502071837.83: *6* rst.writeHeadline & helper
    def writeHeadline(self, p):
        """
        Generate an rST section if options permit it.
        Remove headline commands from the headline first,
        and never generate an rST section for @rst-option and @rst-options.
        """
        docOnly = self.getOption(p, 'doc_only_mode')
        ignore = self.getOption(p, 'ignore_this_headline')
        ignoreNowebDefs = self.getOption(p, 'ignore_noweb_definitions')
        showHeadlines = self.getOption(p, 'show_headlines')
        showOrganizers = self.getOption(p, 'show_organizer_nodes')
        showThisHeadline = self.getOption(p, 'show_this_headline')
        table = self.getOption(p, 'table') # Leo 5.3.
        if (
            p == self.topNode or
            ignore or
            table or # Leo 5.3
            docOnly or # handleDocOnlyMode handles this.
            not showHeadlines and not showThisHeadline or
            # docOnly and not showOrganizers and not thisHeadline or
            not p.h.strip() and not showOrganizers or
            not p.b.strip() and not showOrganizers or
            ignoreNowebDefs and self.isSectionDef(p) # 2011/06/10.
        ):
            return
        self.writeHeadlineHelper(p)
    #@+node:ekr.20090502071837.84: *7* rst.writeHeadlineHelper
    def writeHeadlineHelper(self, p):
        """Write the headline of p as rST."""
        h = p.h
        if not self.atAutoWrite:
            h = h.strip()
        # Remove any headline command before writing the headline.
        i = g.skip_ws(h, 0)
        i = g.skip_id(h, 0, chars='@-')
        word = h[: i].strip()
        if word:
            # Never generate a section for these...
            if word in (
                '@rst-option', '@rst-options',
                '@rst-no-head', '@rst-no-headlines',
                '@rst-table', # new in Leo 5.3.
                '@rst-preformat', # Fix #286.
            ):
                return
            # Remove all other headline commands from the headline.
            for command in self.headlineCommands:
                if word == command:
                    h = h[len(word):].strip()
                    break
            # New in Leo 4.4.4.
            if word.startswith('@'):
                if self.getOption(p, 'strip_at_file_prefixes'):
                    for s in ('@auto', '@clean', '@file', '@nosent', '@thin',):
                        if g.match_word(word, 0, s):
                            h = h[len(s):].strip()
        if not h.strip():
            pass
        elif self.getOption(p, 'show_sections'):
            if self.getOption(p, 'generate_rst'):
                self.write(self.underline(h, p)) # Used by @auto-rst.
            else:
                self.write('\n%s\n\n' % h)
        else:
            self.write('\n**%s**\n\n' % h.replace('*', ''))
    #@+node:ekr.20090502071837.85: *6* rst.writeNode
    def writeNode(self, p):
        """Format a node according to the options presently in effect."""
        self.initCodeBlockString(p)
        h = p.h.strip()
        if self.getOption(p, 'preformat_this_node'):
            self.http_addNodeMarker(p)
            self.writePreformat(p)
            p.moveToThreadNext()
        elif self.getOption(p, 'ignore_this_tree'):
            p.moveToNodeAfterTree()
        elif self.getOption(p, 'ignore_this_node'):
            p.moveToThreadNext()
        elif(
            g.match_word(h, 0, '@rst-options') and
            not self.getOption(p, 'show_options_nodes')
        ):
            p.moveToThreadNext()
        else:
            self.http_addNodeMarker(p)
            self.writeHeadline(p)
            self.writeBody(p)
            p.moveToThreadNext()
    #@+node:ekr.20090502071837.86: *6* rst.writePreformat
    def writePreformat(self, p):
        """Write p's body text lines as if preformatted.

         ::

            line 1
            line 2 etc.
        """
        lines = p.b.split('\n')
        lines = [' ' * 4 + z for z in lines]
        lines.insert(0, '::\n')
        s = '\n'.join(lines)
        if s.strip():
            self.write('%s\n\n' % s)
    #@+node:ekr.20090502071837.87: *6* rst.writeTree
    def writeTree(self, p, fn):
        """Write p's tree to self.outputFile."""
        if (
            self.getOption(p, 'generate_rst') and
            self.getOption(p, 'generate_rst_header_comment')
        ):
            self.write(self.rstComment('rst3: filename: %s\n\n' % fn))
        # We can't use an iterator because we may skip parts of the tree.
        p = p.copy()
        after = p.nodeAfterTree()
        while p and p != after:
            self.writeNode(p) # Side effect: advances p.
    #@+node:ekr.20090502071837.67: *4* rst.writeNodeToString
    def writeNodeToString(self, p=None, ext=None):
        """
        Scan p's tree (defaults to presently selected tree) looking for @rst nodes.
        Convert the first node found to an ouput of the type specified by ext.

        The @rst may or may not be followed by a filename; the filename is *ignored*,
        and its type does not affect ext or the output generated in any way.

        ext should start with a period: .html, .tex or None (specifies rst output).

        Returns (p, s), where p is the position of the @rst node and s is the converted text.
        """
        c = self.c
        current = p or c.p
        self.initSettings(current)
        for p in current.self_and_parents(copy=False):
            if p.h.startswith('@rst'):
                return self.processTree(p, ext=ext, toString=True, justOneFile=True)
        return self.processTree(current, ext=ext, toString=True, justOneFile=True)
    #@+node:ekr.20090512153903.5803: *4* rst.writeAtAutoFile & helpers
    def writeAtAutoFile(self, p, fileName, outputFile):
        """
        Write an @auto tree containing imported rST code.
        The caller will close the output file.
        """
        self.initSettings(p)
        try:
            self.atAutoWrite = True
            self.initAtAutoWrite(p, fileName, outputFile)
            self.topNode = p.copy() # Indicate the top of this tree.
            self.topLevel = p.level()
            after = p.nodeAfterTree()
            ok = self.isSafeWrite(p)
            if ok:
                p = p.firstChild() # A hack: ignore the root node.
                while p and p != after:
                    self.writeNode(p) # side effect: advances p
        finally:
            self.atAutoWrite = False
        return ok
    #@+node:ekr.20090513073632.5733: *5* rst.initAtAutoWrite
    def initAtAutoWrite(self, p, fileName, outputFile):
        """Init for an @auto write."""
        # Do the overrides.
        self.outputFile = outputFile
        # Set underlining characters.
        # User-defined underlining characters make no sense in @auto-rst.
        d = p.v.u.get('rst-import', {})
        underlines2 = d.get('underlines2', '')
            # Do *not* set a default for overlining characters.
        if len(underlines2) > 1:
            underlines2 = underlines2[0]
            g.warning(f"too many top-level underlines, using {underlines2}")
        underlines1 = d.get('underlines1', '')
        # Bug fix:  2010/05/26: pad underlines with default characters.
        default_underlines = '=+*^~"\'`-:><_'
        if underlines1:
            for ch in default_underlines[1:]:
                if ch not in underlines1:
                    underlines1 = underlines1 + ch
        else:
            underlines1 = default_underlines
        self.atAutoWriteUnderlines = underlines2 + underlines1
        self.underlines1 = underlines1
        self.underlines2 = underlines2
    #@+node:ekr.20091228080620.6499: *5* rst.isSafeWrite
    def isSafeWrite(self, p):
        """
        Return True if node p contributes nothing but
        rst-options to the write.
        """
        lines = g.splitLines(p.b)
        for z in lines:
            if z.strip() and not z.startswith('@') and not z.startswith('.. '):
                # A real line that will not be written.
                g.error('unsafe @auto-rst')
                g.es('body text will be ignored in\n', p.h)
                return False
        return True
    #@+node:ekr.20090502071837.41: *3* rst.Options
    #@+node:ekr.20090502071837.44: *4* rst.getOption
    def getOption(self, p, name):
        """Return the value of the named option at node p."""
        d = self.scriptSettingsDict
        name = self.munge(name)
        assert p, g.callers()
            # We may as well fail here.

        def dump(kind, p, val):
            pass

        # 1. Search scriptSettingsDict.
        val = d.get(name)
        if val is not None:
            dump('script', p, val)
            return val
        # 2. Handle single-node options
        if name in self.singleNodeOptions:
            d = self.dd.get(p.v, {})
            val = d.get(name)
            dump('single', p, val)
            return val
        # 3. Search all parents, using self.dd.
        root = self.root if self.root and p.isAncestorOf(self.root) else p
            # Fix #362.
        for p2 in root.self_and_parents(copy=False):
            d = self.dd.get(p2.v, {})
            val = d.get(name)
            if val is not None:
                dump('node', p2, val)
                return val
        # 4. Search self.d0
        val = self.d0.get(name)
        dump('default', p, val)
        return val # May be None.
    #@+node:ekr.20090502071837.45: *4* rst.initCodeBlockString
    def initCodeBlockString(self, p):
        """Init the string used to write code-block directives."""
        c = self.c
        d = c.scanAllDirectives(p)
        language = d.get('language', 'python').lower()
        syntax = SilverCity is not None
        # Note: lines that end with '\n\n' are a signal to handleCodeMode.
        s = self.getOption(p, 'code_block_string')
        if s:
            self.code_block_string = s.replace('\\n', '\n')
        elif syntax and language in ('python', 'ruby', 'perl', 'c'):
            self.code_block_string = '**code**:\n\n.. code-block:: %s\n\n' % (
                language.title())
        else:
            self.code_block_string = '**code**:\n\n.. class:: code\n..\n\n::\n\n'
    #@+node:ekr.20150319125851.8: *4* rst.initSettings
    def initSettings(self, p, script_d=None):
        """
        Init all settings for a command rooted in p.
        There is no need to create self.d0 again.
        """
        self.scriptSettingsDict = script_d or {}
        self.init_write(p)
        self.preprocessTree(p)
    #@+node:ekr.20090502071837.46: *4* rst.preprocessTree & helpers
    def preprocessTree(self, root):
        """Init settings in root, its subtree and all parents."""
        self.dd = {}
        # Bug fix 12/4/05: must preprocess parents too.
        for p in root.parents():
            self.preprocessNode(p)
        for p in root.self_and_subtree(copy=False):
            self.preprocessNode(p)
    #@+node:ekr.20090502071837.47: *5* rst.preprocessNode & helper
    def preprocessNode(self, p):
        """Set self.dd for p.v."""
        d = self.dd.get(p.v)
        if d is None:
            d = self.scanNodeForOptions(p)
            self.dd[p.v] = d
    #@+node:ekr.20090502071837.51: *6* rst.scanNodeForOptions & helpers
    def scanNodeForOptions(self, p):
        """
        Return a dictionary containing all the option-name:value entries in p.

        Such entries may arise from @rst-option or @rst-options in the headline,
        or from @ @rst-options doc parts.
        """
        # A fine point: body options over-ride headline options.
        d = self.scanHeadlineForOptions(p)
        d2 = self.scanForOptionDocParts(p, p.b)
        d.update(d2)
        return d
    #@+node:ekr.20090502071837.50: *7* rst.scanHeadlineForOptions
    def scanHeadlineForOptions(self, p):
        """Return a dictionary containing the options implied by p's headline."""
        h = p.h.strip()
        if p == self.topNode:
            return {} # Don't mess with the root node.
        if g.match_word(h, 0, '@rst-option'):
            s = h[len('@rst-option'):]
            d = self.scanOption(p, s)
            return d
        if g.match_word(h, 0, '@rst-options'):
            d = self.scanOptions(p, p.b)
            return d
        # Careful: can't use g.match_word because options may have '-' chars.
        i = g.skip_id(h, 0, chars='@-')
        word = h[0: i]
        for option, ivar, val in (
            ('@rst', 'code_mode', False),
            ('@rst-code', 'code_mode', True),
            ('@rst-default-path', 'default_prefix', ''),
            ('@rst-doc-only', 'doc_only_mode', True),
            ('@rst-head', 'show_this_headline', True),
            # ('@rst-head' ,        'show_headlines',False),
            ('@rst-ignore', 'ignore_this_node', True),
            ('@rst-ignore-node', 'ignore_this_node', True),
            ('@rst-ignore-tree', 'ignore_this_tree', True),
            ('@rst-no-head', 'ignore_this_headline', True),
            ('@rst-table', 'table', True), # Leo 5.3.
            ('@rst-preformat', 'preformat_this_node', True),
        ):
            if word == option:
                d = {ivar: val}
                # Special case: code mode and doc-only modes are linked.
                if ivar == 'code_mode':
                    d['doc_only_mode'] = False
                elif ivar == 'doc_only_mode':
                    d['code_mode'] = False
                # Special case: Treat a bare @rst like @rst-no-head
                if h == '@rst':
                    d['ignore_this_headline'] = True
                return d
        if h.startswith('@rst'):
            g.trace('unknown kind of @rst headline', p.h, g.callers(4))
        return {}
    #@+node:ekr.20090502071837.49: *7* rst.scanForOptionDocParts
    def scanForOptionDocParts(self, p, s):
        """
        Return a dictionary containing all options from @rst-options doc parts in p.
        Multiple @rst-options doc parts are allowed: this code aggregates all options.
        """
        d, n = {}, 0
        lines = g.splitLines(s)
        while n < len(lines):
            line = lines[n]; n += 1
            if line.startswith('@'):
                i = g.skip_ws(line, 1)
                for kind in ('@rst-options', '@rst-option'):
                    if g.match_word(line, i, kind):
                        # Allow options on the same line.
                        line = line[i + len(kind):]
                        d.update(self.scanOption(p, line))
                        # Add options until the end of the doc part.
                        while n < len(lines):
                            line = lines[n]; n += 1; found = False
                            for stop in ('@c', '@code', '@'):
                                if g.match_word(line, 0, stop):
                                    found = True; break
                            if found:
                                break
                            else:
                                d.update(self.scanOption(p, line))
                        break
        return d
    #@+node:ekr.20090502071837.53: *5* rst.scanOptions & helper
    def scanOptions(self, p, s):
        """Return a dictionary containing all the options in s."""
        d = {}
        for line in g.splitLines(s):
            d2 = self.scanOption(p, line)
            if d2: d.update(d2)
        return d
    #@+node:ekr.20090502071837.52: *6* rst.scanOption & helper
    def scanOption(self, p, s):
        """
        Return { name:val } if s is a line of the form name=val.
        Otherwise return {}
        """
        if not s.strip() or s.strip().startswith('..'):
            return {}
        data = self.parseOptionLine(s)
        if data:
            name, val = data
            if self.munge(name) in list(self.d0.keys()):
                if val.lower() == 'true': val = True
                elif val.lower() == 'false': val = False
                d = {self.munge(name): val}
                return d
            g.error('ignoring unknown option:', name)
            return {}
        g.trace(repr(s))
        g.error('bad rst3 option', s, 'in', p.h)
        return {}
    #@+node:ekr.20090502071837.48: *7* rst.parseOptionLine
    def parseOptionLine(self, s):
        """
        Parse a line containing name=val and return (name,value) or None.
        If no value is found, default to True.
        """
        s = s.strip()
        if s.endswith(','): s = s[: -1]
        # Get name.  Names may contain '-' and '_'.
        i = g.skip_id(s, 0, chars='-_')
        name = s[: i]
        if not name:
            return None, False
        j = g.skip_ws(s, i)
        if g.match(s, j, '='):
            val = s[j + 1:].strip()
            return name, val
        return name, 'True'
    #@+node:ekr.20090502071837.59: *3* rst.Shared write code
    #@+node:ekr.20090502071837.96: *4* rst.http_addNodeMarker
    def http_addNodeMarker(self, p):
        """Add a node marker for the mod_http plugin."""
        if (
            self.getOption(p, 'http_server_support') and
            self.getOption(p, 'generate_rst')
        ):
            self.nodeNumber += 1
            anchorname = f"{self.getOption(p, 'node_begin_marker')}{self.nodeNumber}"
            s = "\n\n.. _%s:\n\n" % anchorname
            self.write(s)
            self.http_map[anchorname] = p.copy()
    #@+node:ekr.20090502071837.97: *4* rst.http_endTree & helpers
    # Was http_support_main

    def http_endTree(self, filename, p, justOneFile):
        """Do end-of-tree processing to support the http plugin."""
        if (
            self.getOption(p, 'http_server_support') and
            self.getOption(p, 'generate_rst')
        ):
            self.set_initial_http_attributes(filename, p)
            self.find_anchors(p)
            if justOneFile:
                self.relocate_references(p.self_and_subtree)
            g.blue('html updated for http plugin')
            if self.getOption(p, 'clear_http_attributes'):
                g.es_print("http attributes cleared")
    #@+node:ekr.20090502071837.98: *5* rst.set_initial_http_attributes
    def set_initial_http_attributes(self, filename, p):
        f = open(filename)
        parser = HtmlParserClass(self, p)
        for line in f.readlines():
            parser.feed(line)
        f.close()
    #@+node:ekr.20090502071837.100: *5* rst.relocate_references
    def relocate_references(self, iterator_generator):
        """
        Relocate references here if we are only running for one file.

        Otherwise postpone the relocation until we have processed all files.
        """
        for p in iterator_generator():
            attr = mod_http.get_http_attribute(p)
            if not attr:
                continue
            parser = LinkHtmlparserClass(self, p)
            for line in attr[3:]:
                try:
                    parser.feed(line)
                except Exception:
                    line = ''.join([ch for ch in line if ord(ch) <= 127])
                    parser.feed(line)
            replacements = parser.get_replacements()
            replacements.reverse()
            if not replacements:
                continue
            for line, column, href, href_file, http_node_ref in replacements:
                marker_parts = href.split("#")
                if len(marker_parts) == 2:
                    marker = marker_parts[1]
                    replacement = f"{http_node_ref}#{marker}"
                    try:
                        attr[line + 2] = attr[line + 2].replace(
                            f'href="{href}"',
                            f'href="{replacement}"')
                    except Exception:
                        g.es("Skipped ", attr[line + 2])
                else:
                    try:
                        attr[line + 2] = attr[line + 2].replace(
                            f'href="{href}"',
                            f'href="{http_node_ref}"')
                    except Exception:
                        g.es("Skipped", attr[line + 2])
    #@+node:ekr.20090502071837.99: *5* rst.find_anchors
    def find_anchors(self, p):
        """Find the anchors in all the nodes."""
        for p1, attrs in self.http_attribute_iter(p):
            html = mod_http.reconstruct_html_from_attrs(attrs)
            parser = AnchorHtmlParserClass(self, p1)
            for line in html:
                try:
                    parser.feed(line)
                # bwm: changed to unicode(line)
                except Exception:
                    line = ''.join([ch for ch in line if ord(ch) <= 127])
                    # filter out non-ascii characters.
                    # bwm: not quite sure what's going on here.
                    parser.feed(line)
    #@+node:ekr.20090502071837.101: *5* rst.http_attribute_iter
    def http_attribute_iter(self, p):
        """
        Iterator for all the nodes which have html code.
        Look at the descendents of p.
        Used for relocation.
        """
        for p1 in p.self_and_subtree(copy=False):
            attr = mod_http.get_http_attribute(p1)
            if attr:
                yield(p1.copy(), attr)
    #@+node:ekr.20090502071837.60: *4* rst.init_write
    def init_write(self, p):
        """Init self.encoding and self.path ivars."""
        c = self.c
        d = c.scanAllDirectives(p)
        self.encoding = d.get('encoding') or 'utf-8'
        self.path = d.get('path') or ''
    #@+node:ekr.20090502071837.94: *4* rst.write
    def write(self, s, theFile=None):
        """Write s to the given file, or self.outputFile."""
        if theFile is None:
            theFile = self.outputFile
        if g.is_binary_file(theFile):
            s = self.encode(s)
        theFile.write(s)
    #@+node:ekr.20100813041139.5919: *4* rst.write_files & helpers
    def write_files(self, ext, fn, p, callDocutils, toString, writeIntermediateFile):
        """Write a file to the indicated locations."""
        isHtml = ext in ('.html', '.htm')
        fn = self.computeOutputFileName(fn)
        if not toString:
            if not self.createDirectoryForFile(fn):
                return
        if writeIntermediateFile:
            if not toString:
                self.createIntermediateFile(fn, p, self.source)
        if callDocutils and ext in ('.htm', '.html', '.tex', '.pdf', '.s5', '.odt'):
            self.stringOutput = s = self.writeToDocutils(p, self.source, ext)
            if s and isHtml:
                self.stringOutput = s = self.addTitleToHtml(s)
            if not s:
                return
            if toString:
                if not g.isUnicode(s):
                    s = g.toUnicode(s, 'utf-8')
            else:
                # Fixes bug 923301: Unicode error when executing 'rst3' command
                s = g.toEncodedString(s, 'utf-8')
                with open(fn, 'wb') as f:
                    f.write(s)
                self.report(fn, p)
                # self.http_endTree(fn,p,justOneFile=justOneFile)
    #@+node:ekr.20100813041139.5913: *5* rst.addTitleToHtml
    def addTitleToHtml(self, s):
        """Replace an empty <title> element by the contents of
        the first <h1> element."""
        i = s.find('<title></title>')
        if i == -1: return s
        m = re.search('<h1>([^<]*)</h1>', s)
        if not m:
            m = re.search('<h1><[^>]+>([^<]*)</a></h1>', s)
        if m:
            s = s.replace('<title></title>',
                '<title>%s</title>' % m.group(1))
        return s
    #@+node:ekr.20100813041139.5914: *5* rst.createDirectoryForFile
    def createDirectoryForFile(self, fn):
        """
        Create the directory for fn if
        a) it doesn't exist and
        b) the user options allow it.

        Return True if the directory existed or was made.
        """
        c = self.c
        # Create the directory if it doesn't exist.
        theDir, junk = g.os_path_split(fn)
        theDir = g.os_path_finalize(theDir) # 1341
        if g.os_path_exists(theDir):
            return True
        ok = g.makeAllNonExistentDirectories(theDir, c=c, force=False)
        if not ok:
            g.error('did not create:', theDir)
        return ok
    #@+node:ekr.20100813041139.5912: *5* rst.createIntermediateFile
    def createIntermediateFile(self, fn, p, s):
        """Write s to to the file whose name is fn."""
        ext = self.getOption(p, 'write_intermediate_extension')
        ext = ext or '.txt' # .txt by default.
        if not ext.startswith('.'): ext = '.' + ext
        fn = fn + ext
        with open(fn, 'w', encoding=self.encoding) as f:
            f.write(s)
        self.report(fn, p)
    #@+node:ekr.20090502071837.65: *5* rst.writeToDocutils (sets argv) & helper
    def writeToDocutils(self, p, s, ext):
        """Send s to docutils using the writer implied by ext and return the result."""
        if not docutils:
            g.error('writeToDocutils: docutils not present')
            return None
        openDirectory = self.c.frame.openDirectory
        overrides = {'output_encoding': self.encoding}
        # Compute the args list if the stylesheet path does not exist.
        styleSheetArgsDict = self.handleMissingStyleSheetArgs(p)
        if ext == '.pdf':
            module = g.importFromPath(
                moduleName='leo_pdf',
                path=g.os_path_finalize_join(g.app.loadDir, '..', 'plugins'),
                verbose=False)
            if not module:
                return None
            writer = module.Writer() # Get an instance.
            writer_name = None
        else:
            writer = None
            for ext2, writer_name in (
                ('.html', 'html'),
                ('.htm', 'html'),
                ('.tex', 'latex'),
                ('.pdf', 'leo.plugins.leo_pdf'), # 2011/11/03
                ('.s5', 's5'), # 2011/03/27
                ('.odt', 'odt'), # 2011/03/27
            ):
                if ext2 == ext: break
            else:
                g.error(f"unknown docutils extension: {ext}")
                return None
        # SilverCity seems not to be supported, so this warning is strange.
        if False and ext in ('.html', '.htm') and not SilverCity:
            if not self.silverCityWarningGiven:
                self.silverCityWarningGiven = True
                if not g.unitTesting:
                    g.es('SilverCity not present so no syntax highlighting')
        # Make the stylesheet path relative to the directory containing the output file.
        rel_stylesheet_path = self.getOption(p, 'stylesheet_path') or ''
        # New in Leo 4.5: The rel_stylesheet_path is relative to the open directory.
        stylesheet_path = g.os_path_finalize_join(
            openDirectory, rel_stylesheet_path)
        stylesheet_name = self.getOption(p, 'stylesheet_name')
        assert stylesheet_name
        path = g.os_path_finalize_join(stylesheet_path, stylesheet_name)
        if self.getOption(p, 'stylesheet_embed') is False:
            rel_path = g.os_path_join(
                rel_stylesheet_path, self.getOption(p, 'stylesheet_name'))
            rel_path = rel_path.replace('\\', '/') # 2010/01/28
            overrides['stylesheet'] = rel_path
            overrides['stylesheet_path'] = None
            overrides['embed_stylesheet'] = None
        elif g.os_path_exists(path):
            if ext != '.pdf':
                overrides['stylesheet'] = path
                overrides['stylesheet_path'] = None
        elif styleSheetArgsDict:
            g.es_print('using publish_argv_for_missing_stylesheets',
                styleSheetArgsDict)
            overrides.update(styleSheetArgsDict)
                # MWC add args to settings
        elif rel_stylesheet_path == stylesheet_path:
            g.error(f"stylesheet not found: {path}")
        else:
            g.error('stylesheet not found\n', path)
            if self.path: g.es_print('@path:', self.path)
            g.es_print('open path:', openDirectory)
            if rel_stylesheet_path:
                g.es_print('relative path:', rel_stylesheet_path)
        try:
            # All paths now come through here.
            result = None # Ensure that result is defined.
            result = docutils.core.publish_string(source=s,
                    reader_name='standalone',
                    parser_name='restructuredtext',
                    writer=writer,
                    writer_name=writer_name,
                    settings_overrides=overrides)
            if isinstance(result, bytes):
                result = g.toUnicode(result)
        except docutils.ApplicationError as error:
            # g.error('Docutils error (%s):' % (error.__class__.__name__))
            g.error('Docutils error:')
            g.blue(error)
        except Exception:
            g.es_print('Unexpected docutils exception')
            g.es_exception()
        return result
    #@+node:ekr.20090502071837.66: *6* rst.handleMissingStyleSheetArgs
    def handleMissingStyleSheetArgs(self, p, s=None):
        """
        Parse the publish_argv_for_missing_stylesheets option,
        returning a dict containing the parsed args.
        """
        force = False
        if force:
            # See http://docutils.sourceforge.net/docs/user/config.html#documentclass
            return {'documentclass': 'report', 'documentoptions': 'english,12pt,lettersize'}
        if not s:
            s = self.getOption(p, 'publish_argv_for_missing_stylesheets')
        if not s:
            return {}
        # Handle argument lists such as this:
        # --language=en,--documentclass=report,--documentoptions=[english,12pt,lettersize]
        d = {}
        while s:
            s = s.strip()
            if not s.startswith('--'): break
            s = s[2:].strip()
            eq = s.find('=')
            cm = s.find(',')
            if eq == -1 or (-1 < cm < eq): # key[nl] or key,
                val = ''
                cm = s.find(',')
                if cm == -1:
                    key = s.strip()
                    s = ''
                else:
                    key = s[: cm].strip()
                    s = s[cm + 1:].strip()
            else: # key = val
                key = s[: eq].strip()
                s = s[eq + 1:].strip()
                if s.startswith('['): # [...]
                    rb = s.find(']')
                    if rb == -1: break # Bad argument.
                    val = s[: rb + 1]
                    s = s[rb + 1:].strip()
                    if s.startswith(','):
                        s = s[1:].strip()
                else: # val[nl] or val,
                    cm = s.find(',')
                    if cm == -1:
                        val = s
                        s = ''
                    else:
                        val = s[: cm].strip()
                        s = s[cm + 1:].strip()
            if not key:
                break
            if not val.strip(): val = '1'
            d[str(key)] = str(val)
        return d
    #@+node:ekr.20090502071837.88: *3* rst.Utils
    #@+node:ekr.20090502071837.89: *4* rst.computeOutputFileName
    def computeOutputFileName(self, fn):
        """Return the full path to the output file."""
        c = self.c
        openDirectory = c.frame.openDirectory
        default_path = self.getOption(self.root or c.p, 'default_path')
            # Subtle change, part of #362: scan options starting at self.root, not c.p.
        if default_path:
            path = g.os_path_finalize_join(self.path, default_path, fn)
        elif self.path:
            path = g.os_path_finalize_join(self.path, fn)
        elif openDirectory:
            path = g.os_path_finalize_join(self.path, openDirectory, fn)
        else:
            path = g.os_path_finalize_join(fn)
        return path
    #@+node:ekr.20090502071837.43: *4* rst.dumpDict
    def dumpDict(self, d, tag):
        """Dump the given settings dict."""
        g.pr(tag + '...')
        for key in sorted(d):
            g.pr('  %20s %s' % (key, d.get(key)))
    #@+node:ekr.20090502071837.90: *4* rst.encode
    def encode(self, s):
        """return s converted to an encoded string."""
        return g.toEncodedString(s, encoding=self.encoding, reportErrors=True)
    #@+node:ekr.20090502071837.91: *4* rst.report
    def report(self, name, p):
        """Issue a report to the log pane."""
        if self.getOption(p, 'silent'):
            return
        name = g.os_path_finalize(name) # 1341
        f = g.blue if self.getOption(p, 'verbose') else g.pr
        f(f"wrote: {name}")
    #@+node:ekr.20090502071837.92: *4* rst.rstComment
    def rstComment(self, s):
        return f".. {s}"
    #@+node:ekr.20090502071837.93: *4* rst.underline
    def underline(self, s, p):
        """
        Return the underlining string to be used at the given level for string s.
        This includes the headline, and possibly a leading overlining line.
        """
        if self.atAutoWrite:
            # We *might* generate overlines for top-level sections.
            u = self.atAutoWriteUnderlines
            level = p.level() - self.topLevel
            # This is tricky. The index n depends on several factors.
            if self.underlines2:
                level -= 1 # There *is* a double-underlined section.
                n = level
            else:
                n = level - 1
            if 0 <= n < len(u):
                ch = u[n]
            elif u:
                ch = u[-1]
            else:
                g.trace('can not happen: no u')
                ch = '#'
            # Write longer underlines for non-ascii characters.
            n = max(4, len(g.toEncodedString(s, encoding=self.encoding, reportErrors=False)))
            if level == 0 and self.underlines2:
                return '%s\n%s\n%s\n\n' % (ch * n, p.h, ch * n)
            return '%s\n%s\n\n' % (p.h, ch * n)
        # The user is responsible for top-level overlining.
        u = self.getOption(p, 'underline_characters') #  '''#=+*^~"'`-:><_'''
        level = max(0, p.level() - self.topLevel)
        level = min(level + 1, len(u) - 1) # Reserve the first character for explicit titles.
        ch = u[level]
        n = max(4, len(g.toEncodedString(s, encoding=self.encoding, reportErrors=False)))
        return '%s\n%s\n\n' % (s.strip(), ch * n)
            # Fixes bug 618570:
    #@-others
#@+node:ekr.20120219194520.10444: ** html parser classes
# pylint: disable=abstract-method
# The lack of an 'error' method is not serious.
#@+node:ekr.20120219194520.10445: *3*  class LinkAnchorParserClass (HTMLParser)
class LinkAnchorParserClass(HTMLParser.HTMLParser):
    """
    The base class to recognize anchors and links in HTML documents. A
    special marker is the "node_marker" which marks the border between node
    and the next.

    The parser classes are used to construct the html code for nodes.

    The algorithm has two phases:
    - Phase 1 AnchorHtmlParserClass: gets the html code for each node.
    - Phase 2 LinkHtmlParserClass: finds all links and checks whethr
      these links need to be modified.
    """
    #@+others
    #@+node:ekr.20120219194520.10446: *4* __init__
    def __init__(self, rst, p):
        """Ctor for the LinkAnchorParserClass class."""
        super().__init__(p)
        self.rst = rst
        # Set ivars from options.
        # This works only if we don't change nodes!
        self.node_begin_marker = rst.getOption(p, 'node_begin_marker')
        self.clear_http_attributes = rst.getOption(p, 'clear_http_attributes')
        self.current_file = rst.outputFileName
    #@+node:ekr.20120219194520.10447: *4* is_anchor
    def is_anchor(self, tag, attrs):
        """
        Check if the current tag is an anchor.
        Returns *all* anchors.
        Works with docutils 0.4
        """
        if tag == 'a':
            return True
        if self.is_node_marker(attrs):
            return True
        return tag == "span"
    #@+node:ekr.20120219194520.10448: *4* is_link
    def is_link(self, tag, attrs):
        """Return True if tag, attrs is represents a link."""
        if tag == 'a':
            return 'href' in dict(attrs)
        return False
    #@+node:ekr.20120219194520.10449: *4* is_node_marker
    def is_node_marker(self, attrs):
        """
        Return the name of the anchor, if this is an anchor for the beginning of a node,
        False otherwise.
        """
        d = dict(attrs)
        if d.get('id', '').startswith(self.node_begin_marker):
            return d['id']
        return False
    #@-others
#@+node:ekr.20120219194520.10450: *3* class HtmlParserClass (LinkAnchorParserClass)
class HtmlParserClass(LinkAnchorParserClass):
    """
    The responsibility of the html parser is:
        1. Find out which html code belongs to which node.
        2. Keep a stack of open tags which apply to the current node.
        3. Keep a list of tags which should be included in the nodes, even
           though they might be closed.
           The <style> tag is one example of that.

    Later, we have to relocate inter-file links: if a reference to another location
    is in a file, we must change the link.

    """
    #@+others
    #@+node:ekr.20120219194520.10451: *4* __init__
    def __init__(self, rst, p):
        """Ctor for the HtmlParserClass class."""
        super().__init__(rst, p)
        self.stack = None
            # The stack contains lists of the form:
            # [text1, text2, previous].
            # text1 is the opening tag
            # text2 is the closing tag
            # previous points to the previous stack element
        self.node_marker_stack = []
            # self.node_marker_stack.pop() returns True for a closing tag if
            # the opening tag identified an anchor belonging to a VNode.
        self.node_code = []
            # Accumulated html code.
            # Once the hmtl code is assigned a VNode, it is deleted here.
        self.deleted_lines = 0
            # Number of lines deleted in self.node_code
        self.endpos_pending = False
            # Do not include self.node_code[0:self.endpos_pending] in the html code.
        self.last_position = None
            # Last position; we must attach html code to this node.
        self.last_marker = None
    #@+node:ekr.20120219194520.10452: *4* handle_starttag
    def handle_starttag(self, tag, attrs):
        """
        1. Find out if the current tag is an achor.
        2. If it is an anchor, we check if this anchor marks the beginning of a new
           node
        3. If a new node begins, then we might have to store html code for the previous
           node.
        4. In any case, put the new tag on the stack.
        """
        is_node_marker = False
        if self.is_anchor(tag, attrs) and self.is_node_marker(attrs):
            is_node_marker = self.is_node_marker(attrs)
            line, column = self.getpos()
            if self.last_position:
                lines = self.node_code[:]
                lines[0] = lines[0][self.startpos:]
                del lines[line - self.deleted_lines - 1:]
                mod_http.get_http_attribute(self.last_position).extend(lines)
                #@+<< trace the unknownAttribute >>
                #@+node:ekr.20120219194520.10453: *5* << trace the unknownAttribute >>
                if 0:
                    g.pr("rst3: unknownAttributes[self.http_attributename]")
                    g.pr("For:", self.last_position)
                    pprint.pprint(mod_http.get_http_attribute(self.last_position))
                #@-<< trace the unknownAttribute >>
            if self.deleted_lines < line - 1:
                del self.node_code[: line - 1 - self.deleted_lines]
                self.deleted_lines = line - 1
                self.endpos_pending = True
        starttag = self.get_starttag_text()
        self.stack = [starttag, None, self.stack]
        self.node_marker_stack.append(is_node_marker)
    #@+node:ekr.20120219194520.10454: *4* handle_endtag
    def handle_endtag(self, tag):
        """
        1. Set the second element of the current top of stack.
        2. If this is the end tag for an anchor for a node,
           store the current stack for that node.
        """
        self.stack[1] = "</" + tag + ">"
        if self.endpos_pending:
            line, column = self.getpos()
            self.startpos = self.node_code[0].find(">", column) + 1
            self.endpos_pending = False
        is_node_marker = self.node_marker_stack.pop()
        if is_node_marker and not self.clear_http_attributes:
            self.last_position = self.rst.http_map[is_node_marker]
            if is_node_marker != self.last_marker:
                # if bwm_file: print >> bwm_file, "Handle endtag:", is_node_marker, self.stack
                mod_http.set_http_attribute(self.rst.http_map[is_node_marker], self.stack)
                self.last_marker = is_node_marker
                # bwm: last_marker is not needed?
        self.stack = self.stack[2]
    #@+node:ekr.20120219194520.10455: *4* feed
    def feed(self, line):
        # pylint: disable=arguments-differ
        self.node_code.append(line)
        HTMLParser.HTMLParser.feed(self, line) # Call the base class's feed().
    #@-others
#@+node:ekr.20120219194520.10456: *3* class AnchorHtmlParserClass (LinkAnchorParserClass)
class AnchorHtmlParserClass(LinkAnchorParserClass):
    """
    This htmlparser does the first step of relocating: finding all the
    anchors within the html nodes.

    Each anchor is mapped to a tuple: (current_file, position).

    Filters out markers which mark the beginning of the html code for a node.
    """
    #@+others
    #@+node:ekr.20120219194520.10457: *4*  __init__
    def __init__(self, rst, p):
        """Ctor for the AnchorHtmlParserClass class."""
        super().__init__(rst, p)
        self.p = p.copy()
        self.anchor_map = rst.anchor_map
    #@+node:ekr.20120219194520.10458: *4* handle_starttag
    def handle_starttag(self, tag, attrs):
        """
        1. Find out if the current tag is an achor.
        2. If the current tag is an anchor, update the mapping;
             anchor -> (filename, p)
        """
        if not self.is_anchor(tag, attrs):
            return
        if self.current_file not in self.anchor_map:
            self.anchor_map[self.current_file] = (self.current_file, self.p)
            simple_name = g.os_path_split(self.current_file)[1]
            self.anchor_map[simple_name] = self.anchor_map[self.current_file]
            # if bwm_file:
            #   print >> bwm_file, "anchor(1): current_file:",
            #   self.current_file, "position:", self.p, "Simple name:", simple_name
            # Not sure what to do here, exactly. Do I need to manipulate
            # the pathname?
        for name, value in attrs:
            if name == 'name' or tag == 'span' and name == 'id':
                if not value.startswith(self.node_begin_marker):
                    # if bwm_file: print >> bwm_file, "anchor(2):", value, self.p
                    self.anchor_map[value] = (self.current_file, self.p.copy())
    #@-others
#@+node:ekr.20120219194520.10459: *3* class LinkHtmlParserClass (LinkAnchorParserClass)
class LinkHtmlparserClass(LinkAnchorParserClass):
    """This html parser does the second step of relocating links:
    1. It scans the html code for links.
    2. If there is a link which links to a previously processed file
       then this link is changed so that it now refers to the node.
    """
    #@+others
    #@+node:ekr.20120219194520.10460: *4* __init__
    def __init__(self, rst, p):
        """Ctor for the LinkHtmlParserClass class."""
        super().__init__(rst)
        self.p = p.copy()
        self.anchor_map = rst.anchor_map
        self.replacements = []
    #@+node:ekr.20120219194520.10461: *4* handle_starttag
    def handle_starttag(self, tag, attrs):
        """
        1. Find out if the current tag is an achor.
        2. If the current tag is an anchor, update the mapping;
             anchor -> p
            Update the list of replacements for the document.
        """
        if not self.is_link(tag, attrs):
            return
        marker = self.node_begin_marker
        for name, value in attrs:
            if name == 'href':
                href = value
                href_parts = href.split("#")
                if len(href_parts) == 1:
                    href_a = href_parts[0]
                else:
                    href_a = href_parts[1]
                if not href_a.startswith(marker):
                    if href_a in self.anchor_map:
                        href_file, href_node = self.anchor_map[href_a]
                        http_node_ref = mod_http.node_reference(href_node)
                        line, column = self.getpos()
                        self.replacements.append((line, column, href, href_file, http_node_ref))
    #@+node:ekr.20120219194520.10462: *4* get_replacements
    def get_replacements(self):
        return self.replacements
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
