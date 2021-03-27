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
import io
import os
import re
import time
import unittest
#
# Third-part imports...
try:
    import docutils
    import docutils.core
    from docutils import parsers
    from docutils.parsers import rst
except Exception:
    docutils = None  # type: ignore
#
# Leo imports.
from leo.core import leoGlobals as g
import leo.core.leoTest2 as leoTest2

#
# Aliases & traces.
StringIO = io.StringIO
if 'plugins' in getattr(g.app, 'debug', []):
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
    A class to convert @rst nodes to rST markup.
    """
    #@+others
    #@+node:ekr.20090502071837.34: *3* rst.Birth
    #@+node:ekr.20090502071837.35: *4* rst.__init__
    def __init__(self, c):
        """Ctor for the RstCommand class."""
        self.c = c
        #
        # Statistics.
        self.n_written = 0  # Number of files written.  Set by write_rst_tree.
        #
        # Http support for HtmlParserClass.  See http_addNodeMarker.
        self.anchor_map = {}  # Keys are anchors. Values are positions
        self.http_map = {}  # Keys are named hyperlink targets.  Value are positions.
        self.nodeNumber = 0  # Unique node number.
        #
        # For writing.
        self.at_auto_underlines = ''  # Full set of underlining characters.
        self.at_auto_write = False  # Flag for underline.
        self.encoding = 'utf-8'  # From any @encoding directive.
        self.path = ''  # The path from any @path directive.
        self.result_list = []  # The intermediate results.
        self.root = None  # The @rst node being processed.
        #
        # Complete the init.
        self.reloadSettings()
    #@+node:ekr.20210326084034.1: *4* rst.reloadSettings (to do)
    def reloadSettings(self):
        """RstCommand.reloadSettings"""
        c = self.c
        ### To do: get the user settings.
        #
        # Reporting options.
        self.silent = False
        #
        # For writeNode and helpers.
        self.generate_rst_header_comment = True
        self.http_server_support = True
        self.node_begin_marker = 'http-node-marker-'
        self.underline_characters = '''#=+*^~"'`-:><_'''
        #
        # For write_docutils_files.
        self.default_path = ''
        self.write_intermediate_extension = '.txt'
        self.write_intermediate_file = True
        #
        # For writeToDocutils & helpers.
        self.publish_argv_for_missing_stylesheets = ''
        self.stylesheet_embed = False
        self.stylesheet_name = 'default.css'
        self.stylesheet_path = ''
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
                self.processTree(p)
        else:
            g.warning('No @rst or @slides nodes in', p.h)
    #@+node:ekr.20090502071837.63: *5* rst.processTree
    def processTree(self, p):
        """
        Process all @rst nodes in a tree.
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
                    self.write_rst_tree(p, fn)
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
    def write_rst_tree(self, p, fn, testing=False):
        """
        Convert p's tree to rst sources.
        Optionally call docutils to convert rst to output.
        Return the sources past to docutils.
        """
        c = self.c
        p = p.copy()  # The loop below modifies p.
        #
        # Init self.root.
        self.root = p.copy()
        #
        # Init encoding and path.
        d = c.scanAllDirectives(p)
        self.encoding = d.get('encoding') or 'utf-8'
        self.path = d.get('path') or ''
        #
        # Write the output to self.result_list.
        self.n_written += 1
        self.result_list = []  # All output goes here.
        if self.generate_rst_header_comment:
            self.result_list.append(f"rst3: filename: {fn}")
        after = p.nodeAfterTree()
        while p and p != after:
            self.writeNode(p)  # Side effect: advances p.
        source = self.compute_result()
        if testing:
            # Don't write either external file.
            html = self.writeToDocutils(p, source, ext='.html')
        else:
            html = self.write_docutils_files(fn, p, source)
        return html, source
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
        """
        Add a node marker for the mod_http plugin (HtmlParserClass class).
        
        The first three elements are a stack of tags, the rest is html code::

            [
                <tag n start>, <tag n end>, <other stack elements>,
                <html line 1>, <html line 2>, ...
            ]

        <other stack elements> has the same structure::

            [<tag n-1 start>, <tag n-1 end>, <other stack elements>]
        """
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
        self.initAtAutoWrite(p)
        self.root = p.copy()
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
    #@+node:ekr.20090502071837.89: *5* rst.computeOutputFileName (to do)
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
        join = g.os_path_finalize_join
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
        stylesheet_path = join(openDirectory, rel_stylesheet_path)
        assert self.stylesheet_name
        path = join(self.stylesheet_path, self.stylesheet_name)
        if not self.stylesheet_embed:
            rel_path = join(rel_stylesheet_path, self.stylesheet_name)
            rel_path = rel_path.replace('\\', '/')
            overrides['stylesheet'] = rel_path
            overrides['stylesheet_path'] = None
            overrides['embed_stylesheet'] = None
        elif os.path.exists(path):
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
            if self.path:
                g.es_print('@path:', self.path)
            g.es_print('open path:', openDirectory)
            if rel_stylesheet_path:
                g.es_print('relative path:', rel_stylesheet_path)
        try:
            result = None
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
        g.pr(f"wrote: {name}")
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
            level = p.level() - self.root.level()
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
        level = max(0, p.level() - self.root.level())
        level = min(level + 1, len(u) - 1)  # Reserve the first character for explicit titles.
        ch = u[level]
        n = max(4, len(encoded_s))
        return f"{s.strip()}\n{ch * n}"
    #@-others
#@+node:ekr.20210327072030.1: ** class TestRst3 (unittest.TestCase)
class TestRst3(unittest.TestCase):  # pragma: no cover
    '''A class to run rst-related unit tests.'''

    #@+others
    #@+node:ekr.20210327072030.3: *3* TestRst3.run
    def run(self, c=None, p=None):  # pylint: disable=arguments-differ
        '''run an rst test.'''
        #
        # Setup.
        if c and p: ### Temp.
            self.c = c
            rc = c.rstCommands
            fn = p.h
            source_p = g.findNodeInTree(c, p, 'source')
            source_s1 = source_p.firstChild().b
            expected_p = g.findNodeInTree(c, p, 'expected')
            expected_s = expected_p.firstChild().b
            root = source_p.firstChild()
            #
            # Compute the result.
            rc.nodeNumber = 0
            html, got_s = rc.write_rst_tree(root, fn, testing=True)
            #
            # Tests...
            # Don't bother testing the html. It will depend on docutils.
            self.assertEqual(expected_s, got_s, msg='expected_s != got_s')
            assert html and html.startswith('<?xml') and html.strip().endswith('</html>')
    #@+node:ekr.20210327090734.1: *3* TestRst3.setUp & tearDown
    def setUp(self):
        """TestRst3.setUp"""
        ### from leo.core import leoRst  # pylint: disable=import-self
        g.unitTesting = True
        self.c = c = leoTest2.create_app()
        c.selectPosition(c.rootPosition())

    def tearDown(self):
        g.unitTesting = False
    #@-others
#@-others
if __name__ == '__main__':
    unittest.main()
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
