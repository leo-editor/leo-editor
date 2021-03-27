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
#@+<< imports >>
#@+node:ekr.20100908120927.5971: ** << imports >> (leoRst)
import html.parser as HTMLParser
import io
import pprint
import re
import time
#
# Third-part imports...
try:
    import docutils
    import docutils.core
    from docutils import parsers
    from docutils.parsers import rst
except Exception:
    docutils = None  # type: ignore
    
###
    # try:
        # import SilverCity
    # except ImportError:
        # SilverCity = None  # type: ignore
#
# Leo imports.
from leo.core import leoGlobals as g
from leo.plugins import mod_http
#
# Aliases & traces.
StringIO = io.StringIO
if 'plugins' in g.app.debug:
    print('leoRst.py: docutils:', repr(docutils))
    print('leoRst.py:  parsers:', repr(parsers))
    print('leoRst.py:      rst:', repr(rst))
#@-<< imports >>
#@+others
#@+node:ekr.20150509035745.1: ** cmd (decorator)
def cmd(name):
    """Command decorator for the RstCommands class."""
    return g.new_cmd_decorator(name, ['c', 'rstCommands',])
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
    #@+node:ekr.20090502071837.35: *4* rst.__init__
    def __init__(self, c):
        """Ctor for the RstCommand class."""
        self.c = c
        #
        # Statistics.
        self.n_written = 0  # Number of files written.
        self.node_counter = 0  # Number of nodes written.
        #
        # Http support for HtmlParserClass.
        self.anchor_map = {}  # Maps are anchors. Values are positions
        self.http_map = {}  # Keys are named hyperlink targets.  Value are positions.
        self.nodeNumber = 0  # For unique anchors.
        #
        # For writing.
        self.at_auto_underlines = ''  # Full set of underlining characters.
        self.encoding = 'utf-8'  # From any @encoding directive.
        self.path = ''  # The path from any @path directive.
        self.result_list = []  # The intermediate results.
        self.root = None  # The @rst node being processed.
        self.topLevel = 0  # self.root.level().
        #
        # Complete the init.
        self.reloadSettings()
    #@+node:ekr.20210326084034.1: *4* rst.reloadSettings
    def reloadSettings(self):
        """RstCommand.reloadSettings"""
        c = self.c
        ### To do: get the user settings.
        self.default_path = ''
        self.generate_rst_header_comment = True
        self.http_server_support = True
        self.node_begin_marker = 'http-node-marker-'
        self.publish_argv_for_missing_stylesheets = ''
        self.silent = False
        self.stylesheet_embed = False
        self.stylesheet_name = 'default.css'
        self.stylesheet_path = ''
        self.underline_characters = '''#=+*^~"'`-:><_'''
        self.verbose = False
        self.write_intermediate_extension = '.txt'
        self.write_intermediate_file = True
    #@+node:ekr.20100813041139.5920: *3* rst.Entry points
    #@+node:ekr.20090511055302.5793: *4* rst.rst3 command & helpers
    @cmd('rst3')
    def rst3(self, event=None):
        """Write all @rst nodes."""
        t1 = time.time()
        self.n_written = 0
        self.processTopTree(self.c.p)
        t2 = time.time()
        g.es_print(f"rst3: {self.n_written} files in {t2 - t1:4.2f} sec.")
    #@+node:ekr.20090502071837.62: *5* rst.processTopTree
    def processTopTree(self, p):
        """Find and handle all @rst and @slides node associated with p."""

        def predicate(p):
            h = p.h
            return (
                h.startswith('@rst') and not h.startswith('@rst-') or
                h.startswith('@slides'))

        roots = g.findRootsWithPredicate(self.c, p, predicate=predicate)
        if roots:
            for p in roots:
                self.root = p.copy()
                self.processTree(p)
        else:
            g.warning('No @rst or @slides nodes in', p.h)
    #@+node:ekr.20090502071837.63: *5* rst.processTree
    def processTree(self, p):
        """
        Process all @rst nodes in a tree.
        ext is the docutils extention: it's useful for scripts and unit tests.
        """
        p = p.copy()
        after = p.nodeAfterTree()
        while p and p != after:
            h = p.h.strip()
            if g.match_word(h, 0, '@rst-ignore-tree'):
                p.moveToNodeAfterTree()
            elif (
                g.match_word(h, 0, '@rst-ignore') or
                g.match_word(h, 0, '@rst-ignore-node')
            ):
                p.moveToThreadNext()
            elif g.match_word(h, 0, "@rst") and not g.match(h, 0, "@rst-"):
                fn = h[4:].strip()
                if fn:
                    s = self.write_rst_tree(p, fn)
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
    def write_rst_tree(self, p, fn):
        """
        Convert p's tree to rst sources.
        Optionally call docutils to convert rst to output.
        Return the sources past to docutils.
        """
        c = self.c
        #
        # Init encoding and path.
        d = c.scanAllDirectives(p)
        self.encoding = d.get('encoding') or 'utf-8'
        self.path = d.get('path') or ''
        #
        # Write the output to self.result_list.
        self.n_written += 1
        self.topLevel = p.level()
        p = p.copy()  # The loop below modifies p.
        self.result_list = []  # All output goes here.
        if self.generate_rst_header_comment:
            self.result_list.append(f"rst3: filename: {fn}")
        after = p.nodeAfterTree()
        while p and p != after:
            self.writeNode(p)  # Side effect: advances p.
        source = self.compute_result()
        self.write_docutils_files(fn, p, source)
        return source
    #@+node:ekr.20100822092546.5835: *5* rst.write_slides & helper
    def write_slides(self, p):
        """Convert p's children to slides."""
        c = self.c
        p = p.copy()
        h = p.h
        i = g.skip_id(h, 1)  # Skip the '@'
        kind, fn = h[:i].strip(), h[i:].strip()
        if not fn:
            g.error(f"{kind} requires file name")
            return
        title = p.firstChild().h if p and p.firstChild() else '<no slide>'
        title = title.strip().capitalize()
        n_tot = p.numberOfChildren()
        n = 1
        d = c.scanAllDirectives(p)
        self.encoding = d.get('encoding') or 'utf-8'
        self.path = d.get('path') or ''
        for child in p.children():
            # Compute the slide's file name.
            fn2, ext = g.os_path_splitext(fn)
            fn2 = f"{fn2}-{n:03d}{ext}"  # Use leading zeros for :glob:.
            n += 1
            # Write the rst sources.
            self.result_list = []
            self.writeSlideTitle(title, n - 1, n_tot)
            self.result_list.append(child.b)
            source = self.compute_result()
            self.write_docutils_files(fn2, p, source)
    #@+node:ekr.20100822174725.5836: *6* rst.writeSlideTitle
    def writeSlideTitle(self, title, n, n_tot):
        """Write the title, underlined with the '#' character."""
        if n != 1:
            title = f"{title} ({n} of {n_tot})"
        width = max(4, len(g.toEncodedString(title,
            encoding=self.encoding, reportErrors=False)))
        self.result_list.append(f"{title}\n{'#' * width}")
    #@+node:ekr.20090502071837.85: *5* rst.writeNode & helper
    def writeNode(self, p):
        """Format a node according to the options presently in effect."""
        h = p.h.strip()
        if g.match_word(h, 0, '@rst-ignore-tree'):
            p.moveToNodeAfterTree()
            return
        if g.match_word(h, 0, '@rst-ignore'):
            p.moveToThreadNext()
            return
        if g.match_word(h, 0, '@rst-ignore-head'):
            self.result_list.append(p.b)
            p.moveToThreadNext()
            return
        # Default: write the entire node.
        self.http_addNodeMarker(p)
        self.result_list.append(self.underline(h, p))
        self.result_list.append(p.b)
        p.moveToThreadNext()
    #@+node:ekr.20090502071837.96: *6* rst.http_addNodeMarker
    def http_addNodeMarker(self, p):
        """Add a node marker for the mod_html plugin (HtmlParserClass class)."""
        if self.http_server_support:
            self.nodeNumber += 1
            anchorname = f"{self.node_begin_marker}{self.nodeNumber}"
            self.result_list.append(f".. _{anchorname}:")
            self.http_map[anchorname] = p.copy()
    #@+node:ekr.20090502071837.67: *4* rst.writeNodeToString (New, test)
    def writeNodeToString(self, p):
        """
        rst.writeNodeToString: A utility for scripts. Not used in Leo.
            
        Write p's tree to a string as if it were an @rst node.
        Return the string.
        """
        p = p.copy()
        self.result_list = []
        after = p.nodeAfterTree()
        while p and p != after:
            self.writeNode(p)  # Side effect: advances p.
        return self.compute_result()
    #@+node:ekr.20090512153903.5803: *4* rst.writeAtAutoFile & helpers
    def writeAtAutoFile(self, p, fileName, outputFile):
        """
        at.writeAtAutoContents calls this method to write an @auto tree
        containing imported rST code.
        
        at.writeAtAutoContents will close the output file.
        """
        self.result_list = []
        self.initAtAutoWrite(p) ###, fileName, outputFile)
        self.topLevel = p.level()
        after = p.nodeAfterTree()
        if not self.isSafeWrite(p):
            return False
        try:
            self.at_auto_write = True  # Set the flag for underline.
            p = p.firstChild()  # A hack: ignore the root node.
            while p and p != after:
                self.writeNode(p)  # side effect: advances p
            s = self.compute_result()
            outputFile.write(s)
            ok = True
        except Exception:
            ok = False
        finally:
            self.at_auto_write = False
        return ok
    #@+node:ekr.20090513073632.5733: *5* rst.initAtAutoWrite
    def initAtAutoWrite(self, p):
        """Init underlining for for an @auto write."""
        # User-defined underlining characters make no sense in @auto-rst.
        d = p.v.u.get('rst-import', {})
        underlines2 = d.get('underlines2', '')
        #
        # Do *not* set a default for overlining characters.
        if len(underlines2) > 1:
            underlines2 = underlines2[0]
            g.warning(f"too many top-level underlines, using {underlines2}")
        underlines1 = d.get('underlines1', '')
        #
        # Pad underlines with default characters.
        default_underlines = '=+*^~"\'`-:><_'
        if underlines1:
            for ch in default_underlines[1:]:
                if ch not in underlines1:
                    underlines1 = underlines1 + ch
        else:
            underlines1 = default_underlines
        self.at_auto_underlines = underlines2 + underlines1
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
    #@+node:ekr.20100813041139.5919: *4* rst.write_docutils_files & helpers
    def write_docutils_files(self, fn, p, source):
        """Write source to the intermediate file and write the output from docutils.."""
        #
        # Do nothing if we aren't going to call docutils.
        junk, ext = g.os_path_splitext(fn)
        ext = ext.lower()
        fn = self.computeOutputFileName(fn)
        if ext not in ('.htm', '.html', '.tex', '.pdf', '.s5', '.odt'):
            return
        ok = self.createDirectoryForFile(fn)
        if not ok:
            return
        #
        # Write the intermediate file.
        if self.write_intermediate_file:
            self.createIntermediateFile(fn, p, source)
        #
        # Write the result from docutils.
        s = self.writeToDocutils(p, source, ext)
        if s and ext in ('.html', '.htm'):
            s = self.addTitleToHtml(s)
        if not s:
            return
        s = g.toEncodedString(s, 'utf-8')
        with open(fn, 'wb') as f:
            f.write(s)
        self.report(fn, p)
    #@+node:ekr.20100813041139.5913: *5* rst.addTitleToHtml
    def addTitleToHtml(self, s):
        """
        Replace an empty <title> element by the contents of the first <h1>
        element.
        """
        i = s.find('<title></title>')
        if i == -1: return s
        m = re.search(r'<h1>([^<]*)</h1>', s)
        if not m:
            m = re.search(r'<h1><[^>]+>([^<]*)</a></h1>', s)
        if m:
            s = s.replace('<title></title>',
                f"<title>{m.group(1)}</title>")
        return s
    #@+node:ekr.20090502071837.89: *5* rst.computeOutputFileName
    def computeOutputFileName(self, fn):
        """Return the full path to the output file."""
        c = self.c
        openDirectory = c.frame.openDirectory
        
        ### getOption searched up the tree.
        ### default_path = self.getOption(self.root or c.p, 'default_path')
            # Subtle change, part of #362: scan options starting at self.root, not c.p.
        if self.default_path:
            path = g.os_path_finalize_join(self.path, self.default_path, fn)
        elif self.path:
            path = g.os_path_finalize_join(self.path, fn)
        elif openDirectory:
            path = g.os_path_finalize_join(self.path, openDirectory, fn)
        else:
            path = g.os_path_finalize_join(fn)
        return path
    #@+node:ekr.20100813041139.5914: *5* rst.createDirectoryForFile
    def createDirectoryForFile(self, fn):
        """
        Create the directory for fn if
        a) it doesn't exist and
        b) the user options allow it.

        Return True if the directory existed or was made.
        """
        c, ok = self.c, False  # 1815.
        # Create the directory if it doesn't exist.
        theDir, junk = g.os_path_split(fn)
        theDir = g.os_path_finalize(theDir)  # 1341
        if g.os_path_exists(theDir):
            return True
        if c and c.config and c.config.create_nonexistent_directories:
            theDir = c.expand_path_expression(theDir)
            ok = g.makeAllNonExistentDirectories(theDir)
            if not ok:
                g.error('did not create:', theDir)
        return ok
    #@+node:ekr.20100813041139.5912: *5* rst.createIntermediateFile
    def createIntermediateFile(self, fn, p, s):
        """Write s to to the file whose name is fn."""
        # ext = self.getOption(p, 'write_intermediate_extension')
        ext = self.write_intermediate_extension
        ext = ext or '.txt'  # .txt by default.
        if not ext.startswith('.'): ext = '.' + ext
        fn = fn + ext
        with open(fn, 'w', encoding=self.encoding) as f:
            f.write(s)
        self.report(fn, p)
    #@+node:ekr.20090502071837.65: *5* rst.writeToDocutils & helper
    def writeToDocutils(self, p, s, ext):
        """Send s to docutils using the writer implied by ext and return the result."""
        if not docutils:
            g.error('writeToDocutils: docutils not present')
            return None
        openDirectory = self.c.frame.openDirectory
        overrides = {'output_encoding': self.encoding}
        #
        # Compute the args list if the stylesheet path does not exist.
        styleSheetArgsDict = self.handleMissingStyleSheetArgs(p)
        if ext == '.pdf':
            module = g.import_module('leo.plugins.leo_pdf')
            if not module:
                return None
            writer = module.Writer()  # Get an instance.
            writer_name = None
        else:
            writer = None
            for ext2, writer_name in (
                ('.html', 'html'),
                ('.htm', 'html'),
                ('.tex', 'latex'),
                ('.pdf', 'leo.plugins.leo_pdf'),
                ('.s5', 's5'), 
                ('.odt', 'odt'),
            ):
                if ext2 == ext: break
            else:
                g.error(f"unknown docutils extension: {ext}")
                return None
        #
        # Make the stylesheet path relative to open directory.
        rel_stylesheet_path = self.stylesheet_path or ''
        stylesheet_path = g.os_path_finalize_join(openDirectory, rel_stylesheet_path)
        assert self.stylesheet_name
        path = g.os_path_finalize_join(self.stylesheet_path, self.stylesheet_name)
        if not self.stylesheet_embed:
            rel_path = g.os_path_join(
                rel_stylesheet_path, self.stylesheet_name)
            rel_path = rel_path.replace('\\', '/')
            overrides['stylesheet'] = rel_path
            overrides['stylesheet_path'] = None
            overrides['embed_stylesheet'] = None
        elif g.os_path_exists(path):
            if ext != '.pdf':
                overrides['stylesheet'] = path
                overrides['stylesheet_path'] = None
        elif styleSheetArgsDict:
            g.es_print('using publish_argv_for_missing_stylesheets', styleSheetArgsDict)
            overrides.update(styleSheetArgsDict)  # MWC add args to settings
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
            result = None  # Ensure that result is defined.
            # #1454: This call may print a -Wd warning:
                # site-packages\docutils\io.py:245:
                # DeprecationWarning: 'U' mode is deprecated
                #
                # The actual culprit is 'rU' mode at line 207.
            result = docutils.core.publish_string(source=s,
                    reader_name='standalone',
                    parser_name='restructuredtext',
                    writer=writer,
                    writer_name=writer_name,
                    settings_overrides=overrides)
            if isinstance(result, bytes):
                result = g.toUnicode(result)
        except docutils.ApplicationError as error:
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
        if 0:
            # See http://docutils.sourceforge.net/docs/user/config.html#documentclass
            return {
                'documentclass': 'report',
                'documentoptions': 'english,12pt,lettersize',
            }
        if not s:
            ### To do: getOption searches up p's tree!
                # s = self.getOption(p, 'publish_argv_for_missing_stylesheets')
            s = self.publish_argv_for_missing_stylesheets
        if not s:
            return {}
        #
        # Handle argument lists such as this:
        # --language=en,--documentclass=report,--documentoptions=[english,12pt,lettersize]
        d = {}
        while s:
            s = s.strip()
            if not s.startswith('--'): break
            s = s[2:].strip()
            eq = s.find('=')
            cm = s.find(',')
            if eq == -1 or (-1 < cm < eq):  # key[nl] or key,
                val = ''
                cm = s.find(',')
                if cm == -1:
                    key = s.strip()
                    s = ''
                else:
                    key = s[:cm].strip()
                    s = s[cm + 1 :].strip()
            else:  # key = val
                key = s[:eq].strip()
                s = s[eq + 1 :].strip()
                if s.startswith('['):  # [...]
                    rb = s.find(']')
                    if rb == -1: break  # Bad argument.
                    val = s[: rb + 1]
                    s = s[rb + 1 :].strip()
                    if s.startswith(','):
                        s = s[1:].strip()
                else:  # val[nl] or val,
                    cm = s.find(',')
                    if cm == -1:
                        val = s
                        s = ''
                    else:
                        val = s[:cm].strip()
                        s = s[cm + 1 :].strip()
            if not key:
                break
            if not val.strip():
                val = '1'
            d[str(key)] = str(val)
        return d
    #@+node:ekr.20090502071837.88: *3* rst.Utils
    #@+node:ekr.20210326165315.1: *4* rst.compute_result
    def compute_result(self):
        """Concatenate all strings in self.result, ensuring exactly one blank line between strings."""
        return ''.join(f"{s.rstrip()}\n\n" for s in self.result_list if s.strip())
    #@+node:ekr.20090502071837.43: *4* rst.dumpDict
    def dumpDict(self, d, tag):
        """Dump the given settings dict."""
        g.pr(tag + '...')
        for key in sorted(d):
            g.pr(f"  {key:20} {d.get(key)}")
    #@+node:ekr.20090502071837.90: *4* rst.encode
    def encode(self, s):
        """return s converted to an encoded string."""
        return g.toEncodedString(s, encoding=self.encoding, reportErrors=True)
    #@+node:ekr.20090502071837.91: *4* rst.report
    def report(self, name, p):
        """Issue a report to the log pane."""
        if self.silent:
            return
        name = g.os_path_finalize(name)  # 1341
        f = g.blue if self.verbose else g.pr
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
        encoded_s = g.toEncodedString(s, encoding=self.encoding, reportErrors=False)
        if self.at_auto_write:
            # We *might* generate overlines for top-level sections.
            u = self.at_auto_underlines
            level = p.level() - self.topLevel
            # This is tricky. The index n depends on several factors.
            if self.underlines2:
                level -= 1  # There *is* a double-underlined section.
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
            n = max(4, len(encoded_s))
            if level == 0 and self.underlines2:
                # Generate an overline and an underline.
                return f"{ch * n}\n{p.h}\n{ch * n}"
            # Generate only an underline.
            return f"{p.h}\n{ch * n}"
        #
        # The user is responsible for top-level overlining.
        u = self.underline_characters  #  '''#=+*^~"'`-:><_'''
        level = max(0, p.level() - self.topLevel)
        level = min(level + 1, len(u) - 1)  # Reserve the first character for explicit titles.
        ch = u[level]
        n = max(4, len(encoded_s))
        return f"{s.strip()}\n{ch * n}"
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
        super().__init__()
        self.rst = rst
        self.p = p.copy()
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
    #@+node:ekr.20120219194520.10451: *4* HtmlParserClass.__init__
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
    #@+node:ekr.20120219194520.10452: *4* HtmlParserClass.handle_starttag
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
                del lines[line - self.deleted_lines - 1 :]
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
    #@+node:ekr.20120219194520.10454: *4* HtmlParserClass.handle_endtag
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
                mod_http.set_http_attribute(
                    self.rst.http_map[is_node_marker], self.stack)
                self.last_marker = is_node_marker
                # bwm: last_marker is not needed?
        self.stack = self.stack[2]
    #@+node:ekr.20120219194520.10455: *4* HtmlParserClass.feed
    def feed(self, line):
        # pylint: disable=arguments-differ
        self.node_code.append(line)
        HTMLParser.HTMLParser.feed(self, line)  # Call the base class's feed().
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
        super().__init__(rst, p)
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
                        self.replacements.append(
                            (line, column, href, href_file, http_node_ref))
    #@+node:ekr.20120219194520.10462: *4* get_replacements
    def get_replacements(self):
        return self.replacements
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
