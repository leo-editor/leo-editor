#@+leo-ver=5-thin
#@+node:ekr.20031218072017.3206: * @file leoImport.py
#@+<< leoImport imports >>
#@+node:ekr.20091224155043.6539: ** << leoImport imports >>
from __future__ import annotations
from collections.abc import Callable
import csv
import io
import os
import re
import textwrap
import time
from typing import Any, Optional, TYPE_CHECKING
import urllib
#
# Third-party imports.
try:
    import docutils
    import docutils.core
    assert docutils
    assert docutils.core
except ImportError:
    # print('leoImport.py: can not import docutils')
    docutils = None  # type:ignore
try:
    import lxml
except ImportError:
    lxml = None

# Leo imports...
from leo.core import leoGlobals as g

# Abbreviation.
StringIO = io.StringIO
#@-<< leoImport imports >>
#@+<< leoImport annotations >>
#@+node:ekr.20220821210220.1: ** << leoImport annotations >>
if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent
    from leo.core.leoNodes import Position
    Value = Any
#@-<< leoImport annotations >>
#@+others
#@+node:ekr.20160503145550.1: ** class FreeMindImporter
class FreeMindImporter:
    """Importer class for FreeMind (.mmap) files."""

    def __init__(self, c: Cmdr) -> None:
        """ctor for FreeMind Importer class."""
        self.c = c
        self.count = 0

    #@+others
    #@+node:ekr.20170222084048.1: *3* freemind.add_children
    def add_children(self, parent: Position, element: Value) -> None:
        """
        parent is the parent position, element is the parent element.
        Recursively add all the child elements as descendants of parent_p.
        """
        p = parent.insertAsLastChild()
        attrib_text = element.attrib.get('text', '').strip()
        tag = element.tag if isinstance(element.tag, str) else ''
        text = element.text or ''
        if not tag:
            text = text.strip()
        p.h = attrib_text or tag or 'Comment'
        p.b = text if text.strip() else ''
        for child in element:
            self.add_children(p, child)
    #@+node:ekr.20160503125844.1: *3* freemind.create_outline
    def create_outline(self, path: str) -> Position:
        """Create a tree of nodes from a FreeMind file."""
        c = self.c
        junk, fileName = g.os_path_split(path)
        undoData = c.undoer.beforeInsertNode(c.p)
        try:
            self.import_file(path)
            c.undoer.afterInsertNode(c.p, 'Import', undoData)
        except Exception:
            g.es_print('Exception importing FreeMind file', g.shortFileName(path))
            g.es_exception()
        return c.p
    #@+node:ekr.20160503191518.4: *3* freemind.import_file
    def import_file(self, path: str) -> None:
        """The main line of the FreeMindImporter class."""
        c = self.c
        sfn = g.shortFileName(path)
        if g.os_path_exists(path):
            htmltree = lxml.html.parse(path)
            root = htmltree.getroot()
            body = root.findall('body')[0]
            if body is None:
                g.error(f"no body in: {sfn}")
            else:
                root_p = c.lastTopLevel().insertAfter()
                root_p.h = g.shortFileName(path)
                for child in body:
                    if child != body:
                        self.add_children(root_p, child)
                c.selectPosition(root_p)
                c.redraw()
        else:
            g.error(f"file not found: {sfn}")
    #@+node:ekr.20160503145113.1: *3* freemind.import_files
    def import_files(self, files: list[str]) -> None:
        """Import a list of FreeMind (.mmap) files."""
        c = self.c
        if files:
            for fileName in files:
                g.setGlobalOpenDir(fileName)
                p = self.create_outline(fileName)
                p.contract()
                p.setDirty()
                c.setChanged()
            c.redraw(p)
    #@+node:ekr.20160504043823.1: *3* freemind.prompt_for_files
    def prompt_for_files(self) -> None:
        """Prompt for a list of FreeMind (.mm.html) files and import them."""
        if not lxml:
            g.trace("FreeMind importer requires lxml")
            return
        c = self.c
        filetypes = [
            ("FreeMind files", "*.mm.html"),
            ("All files", "*"),
        ]
        names = g.app.gui.runOpenFilesDialog(c,
            title="Import FreeMind File", filetypes=filetypes)
        c.bringToFront()
        if names:
            g.chdir(names[0])
            self.import_files(names)
    #@-others
#@+node:ekr.20071127175948: ** class LeoImportCommands
class LeoImportCommands:
    """
    A class implementing all of Leo's import/export code. This class
    uses **importers** in the leo/plugins/importers folder.

    For more information, see leo/plugins/importers/howto.txt.
    """
    #@+others
    #@+node:ekr.20031218072017.3207: *3* ic.__init__& ic.reload_settings
    def __init__(self, c: Cmdr) -> None:
        """ctor for LeoImportCommands class."""
        self.c = c
        self.encoding = 'utf-8'
        self.errors = 0
        self.fileName: str = None  # The original file name, say x.cpp
        self.fileType: str = None  # ".py", ".c", etc.
        self.methodName: str = None  # x, as in < < x methods > > =
        self.output_newline: str = g.getOutputNewline(c=c)  # Value of @bool output_newline
        self.treeType = "@file"  # None or "@file"
        self.verbose = True  # Leo 6.6
        self.webType = "@noweb"  # "cweb" or "noweb"
        self.web_st: list[str] = []  # noweb symbol table.
        self.reload_settings()

    def reload_settings(self) -> None:
        pass

    reloadSettings = reload_settings
    #@+node:ekr.20031218072017.3289: *3* ic.Export
    #@+node:ekr.20031218072017.3290: *4* ic.convertCodePartToWeb & helpers
    def convertCodePartToWeb(self, s: str, i: int, p: Position, result: str) -> tuple[int, str]:
        """
        # Headlines not containing a section reference are ignored in noweb
        and generate index index in cweb.
        """
        ic = self
        nl = ic.output_newline
        head_ref = ic.getHeadRef(p)
        file_name = ic.getFileName(p)
        if g.match_word(s, i, "@root"):
            i = g.skip_line(s, i)
            ic.appendRefToFileName(file_name, result)
        elif g.match_word(s, i, "@c") or g.match_word(s, i, "@code"):
            i = g.skip_line(s, i)
            ic.appendHeadRef(p, file_name, head_ref, result)
        elif g.match_word(p.h, 0, "@file"):
            # Only do this if nothing else matches.
            ic.appendRefToFileName(file_name, result)
            i = g.skip_line(s, i)  # 4/28/02
        else:
            ic.appendHeadRef(p, file_name, head_ref, result)
        i, result = ic.copyPart(s, i, result)
        return i, result.strip() + nl
    #@+node:ekr.20140630085837.16720: *5* ic.appendHeadRef
    def appendHeadRef(self, p: Position, file_name: str, head_ref: str, result: str) -> None:
        ic = self
        nl = ic.output_newline
        if ic.webType == "cweb":
            if head_ref:
                escaped_head_ref = head_ref.replace("@", "@@")
                result += "@<" + escaped_head_ref + "@>=" + nl
            else:
                # Convert the headline to an index entry.
                result += "@^" + p.h.strip() + "@>" + nl
                result += "@c" + nl  # @c denotes a new section.
        else:
            if head_ref:
                pass
            elif p == ic.c.p:
                head_ref = file_name or "*"
            else:
                head_ref = "@others"
            # 2019/09/12
            result += (g.angleBrackets(head_ref) + "=" + nl)
    #@+node:ekr.20140630085837.16719: *5* ic.appendRefToFileName
    def appendRefToFileName(self, file_name: str, result: str) -> None:
        ic = self
        nl = ic.output_newline
        if ic.webType == "cweb":
            if not file_name:
                result += "@<root@>=" + nl
            else:
                result += "@(" + file_name + "@>" + nl  # @(...@> denotes a file.
        else:
            if not file_name:
                file_name = "*"
            # 2019/09/12.
            lt = "<<"
            rt = ">>"
            result += (lt + file_name + rt + "=" + nl)
    #@+node:ekr.20140630085837.16721: *5* ic.getHeadRef
    def getHeadRef(self, p: Position) -> str:
        """
        Look for either noweb or cweb brackets.
        Return everything between those brackets.
        """
        h = p.h.strip()
        if g.match(h, 0, "<<"):
            i = h.find(">>", 2)
        elif g.match(h, 0, "<@"):
            i = h.find("@>", 2)
        else:
            return h
        return h[2:i].strip()
    #@+node:ekr.20031218072017.3292: *5* ic.getFileName
    def getFileName(self, p: Position) -> str:
        """Return the file name from an @file or @root node."""
        h = p.h.strip()
        if g.match(h, 0, "@file") or g.match(h, 0, "@root"):
            line = h[5:].strip()
            # set j & k so line[j:k] is the file name.
            if g.match(line, 0, "<"):
                j, k = 1, line.find(">", 1)
            elif g.match(line, 0, '"'):
                j, k = 1, line.find('"', 1)
            else:
                j, k = 0, line.find(" ", 0)
            if k == -1:
                k = len(line)
            file_name = line[j:k].strip()
        else:
            file_name = ''
        return file_name
    #@+node:ekr.20031218072017.3296: *4* ic.convertDocPartToWeb (handle @ %def)
    def convertDocPartToWeb(self, s: str, i: int, result: str) -> tuple[int, str]:
        nl = self.output_newline
        if g.match_word(s, i, "@doc"):
            i = g.skip_line(s, i)
        elif g.match(s, i, "@ ") or g.match(s, i, "@\t") or g.match(s, i, "@*"):
            i += 2
        elif g.match(s, i, "@\n"):
            i += 1
        i = g.skip_ws_and_nl(s, i)
        i, result2 = self.copyPart(s, i, "")
        if result2:
            # Break lines after periods.
            result2 = result2.replace(".  ", "." + nl)
            result2 = result2.replace(". ", "." + nl)
            result += nl + "@" + nl + result2.strip() + nl + nl
        else:
            # All nodes should start with '@', even if the doc part is empty.
            result += nl + "@ " if self.webType == "cweb" else nl + "@" + nl
        return i, result
    #@+node:ekr.20031218072017.3297: *4* ic.convertVnodeToWeb
    def positionToWeb(self, p: Position) -> str:
        """
        This code converts a VNode to noweb text as follows:

        Convert @doc to @
        Convert @root or @code to < < name > >=, assuming the headline contains < < name > >
        Ignore other directives
        Format doc parts so they fit in pagewidth columns.
        Output code parts as is.
        """
        c = self.c
        if not p or not c:
            return ""
        startInCode = c.config.getBool('at-root-bodies-start-in-doc-mode')
        nl = self.output_newline
        docstart = nl + "@ " if self.webType == "cweb" else nl + "@" + nl
        s = p.b
        lb = "@<" if self.webType == "cweb" else "<<"
        i, result, docSeen = 0, "", False
        while i < len(s):
            progress = i
            i = g.skip_ws_and_nl(s, i)
            if self.isDocStart(s, i) or g.match_word(s, i, "@doc"):
                i, result = self.convertDocPartToWeb(s, i, result)
                docSeen = True
            elif (
                g.match_word(s, i, "@code") or
                g.match_word(s, i, "@root") or
                g.match_word(s, i, "@c") or
                g.match(s, i, lb)
            ):
                if not docSeen:
                    docSeen = True
                    result += docstart
                i, result = self.convertCodePartToWeb(s, i, p, result)
            elif self.treeType == "@file" or startInCode:
                if not docSeen:
                    docSeen = True
                    result += docstart
                i, result = self.convertCodePartToWeb(s, i, p, result)
            else:
                i, result = self.convertDocPartToWeb(s, i, result)
                docSeen = True
            assert progress < i
        result = result.strip()
        if result:
            result += nl
        return result
    #@+node:ekr.20031218072017.3299: *4* ic.copyPart
    # Copies characters to result until the end of the present section is seen.

    def copyPart(self, s: str, i: int, result: str) -> tuple[int, str]:

        lb = "@<" if self.webType == "cweb" else "<<"
        rb = "@>" if self.webType == "cweb" else ">>"
        theType = self.webType
        while i < len(s):
            progress = j = i  # We should be at the start of a line here.
            i = g.skip_nl(s, i)
            i = g.skip_ws(s, i)
            if self.isDocStart(s, i):
                return i, result
            if (g.match_word(s, i, "@doc") or
                g.match_word(s, i, "@c") or
                g.match_word(s, i, "@root") or
                g.match_word(s, i, "@code")  # 2/25/03
            ):
                return i, result
            # 2019/09/12
            lt = "<<"
            rt = ">>="
            if g.match(s, i, lt) and g.find_on_line(s, i, rt) > -1:
                return i, result
            # Copy the entire line, escaping '@' and
            # Converting @others to < < @ others > >
            i = g.skip_line(s, j)
            line = s[j:i]
            if theType == "cweb":
                line = line.replace("@", "@@")
            else:
                j = g.skip_ws(line, 0)
                if g.match(line, j, "@others"):
                    line = line.replace("@others", lb + "@others" + rb)
                elif g.match(line, 0, "@"):
                    # Special case: do not escape @ %defs.
                    k = g.skip_ws(line, 1)
                    if not g.match(line, k, "%defs"):
                        line = "@" + line
            result += line
            assert progress < i
        return i, result.rstrip()
    #@+node:ekr.20031218072017.1462: *4* ic.exportHeadlines
    def exportHeadlines(self, fileName: str) -> None:
        """Export headlines for c.p and its subtree to the file with the given name."""
        c, p = self.c, self.c.p
        nl = self.output_newline
        if not p:
            return
        self.encoding = c.getEncoding(p)
        firstLevel = p.level()
        try:
            with open(fileName, 'w') as theFile:
                for p in p.self_and_subtree(copy=False):
                    head = p.moreHead(firstLevel, useVerticalBar=True)
                    theFile.write(head + nl)
        except IOError:
            g.warning("can not open", fileName)
    #@+node:ekr.20031218072017.1147: *4* ic.flattenOutline
    def flattenOutline(self, fileName: str) -> None:
        """
        A helper for the flatten-outline command.

        Export the selected outline to an external file.
        The outline is represented in MORE format.
        """
        c = self.c
        nl = self.output_newline
        p = c.p
        if not p:
            return
        self.encoding = c.getEncoding(p)
        firstLevel = p.level()
        try:
            theFile = open(fileName, 'wb')  # Fix crasher: open in 'wb' mode.
        except IOError:
            g.warning("can not open", fileName)
            return
        for p in p.self_and_subtree(copy=False):
            s = p.moreHead(firstLevel) + nl
            s = g.toEncodedString(s, encoding=self.encoding, reportErrors=True)
            theFile.write(s)
            s = p.moreBody() + nl  # Inserts escapes.
            if s.strip():
                s = g.toEncodedString(s, self.encoding, reportErrors=True)
                theFile.write(s)
        theFile.close()
    #@+node:ekr.20031218072017.1148: *4* ic.outlineToWeb
    def outlineToWeb(self, fileName: str, webType: str) -> None:
        c = self.c
        nl = self.output_newline
        current = c.p
        if not current:
            return
        self.encoding = c.getEncoding(current)
        self.webType = webType
        try:
            theFile = open(fileName, 'w')
        except IOError:
            g.warning("can not open", fileName)
            return
        self.treeType = "@file"
        # Set self.treeType to @root if p or an ancestor is an @root node.
        for p in current.parents():
            flag, junk = g.is_special(p.b, "@root")
            if flag:
                self.treeType = "@root"
                break
        for p in current.self_and_subtree(copy=False):
            s = self.positionToWeb(p)
            if s:
                theFile.write(s)
                if s[-1] != '\n':
                    theFile.write(nl)
        theFile.close()
    #@+node:ekr.20031218072017.3300: *4* ic.removeSentinelsCommand
    def removeSentinelsCommand(self, paths: list[str], toString: bool = False) -> Optional[str]:
        c = self.c
        self.encoding = c.getEncoding(c.p)
        for fileName in paths:
            g.setGlobalOpenDir(fileName)
            path, self.fileName = g.os_path_split(fileName)
            s, e = g.readFileIntoString(fileName, self.encoding)
            if s is None:
                return None
            if e:
                self.encoding = e
            #@+<< set delims from the header line >>
            #@+node:ekr.20031218072017.3302: *5* << set delims from the header line >>
            # Skip any non @+leo lines.
            i = 0
            while i < len(s) and g.find_on_line(s, i, "@+leo") == -1:
                i = g.skip_line(s, i)
            # Get the comment delims from the @+leo sentinel line.
            at = self.c.atFileCommands
            j = g.skip_line(s, i)
            line = s[i:j]
            valid, junk, start_delim, end_delim, junk = at.parseLeoSentinel(line)
            if not valid:
                if not toString:
                    g.es("invalid @+leo sentinel in", fileName)
                return None
            if end_delim:
                line_delim = None
            else:
                line_delim, start_delim = start_delim, None
            #@-<< set delims from the header line >>
            s = self.removeSentinelLines(s, line_delim, start_delim, end_delim)
            ext = c.config.getString('remove-sentinels-extension')
            if not ext:
                ext = ".txt"
            if ext[0] == '.':
                newFileName = g.finalize_join(path, fileName + ext)  # 1341
            else:
                head, ext2 = g.os_path_splitext(fileName)
                newFileName = g.finalize_join(path, head + ext + ext2)  # 1341
            if toString:
                return s
            #@+<< Write s into newFileName >>
            #@+node:ekr.20031218072017.1149: *5* << Write s into newFileName >> (remove-sentinels)
            # Remove sentinels command.
            try:
                with open(newFileName, 'w') as theFile:
                    theFile.write(s)
                if not g.unitTesting:
                    g.es("created:", newFileName)
            except Exception:
                g.es("exception creating:", newFileName)
                g.print_exception()
            #@-<< Write s into newFileName >>
        return None
    #@+node:ekr.20031218072017.3303: *4* ic.removeSentinelLines
    # This does not handle @nonl properly, but that no longer matters.

    def removeSentinelLines(self, s: str, line_delim: str, start_delim: str, unused_end_delim: str) -> str:
        """Properly remove all sentinel lines in s."""
        delim = (line_delim or start_delim or '') + '@'
        verbatim = delim + 'verbatim'
        verbatimFlag = False
        result = []
        for line in g.splitLines(s):
            i = g.skip_ws(line, 0)
            if not verbatimFlag and g.match(line, i, delim):
                if g.match(line, i, verbatim):
                    # Force the next line to be in the result.
                    verbatimFlag = True
            else:
                result.append(line)
                verbatimFlag = False
        return ''.join(result)
    #@+node:ekr.20031218072017.1464: *4* ic.weave
    def weave(self, filename: str) -> None:
        c, p = self.c, self.c.p
        nl = self.output_newline
        if not p:
            return
        self.encoding = c.getEncoding(p)
        try:
            with open(filename, 'w', encoding=self.encoding) as f:
                for p in p.self_and_subtree():
                    s = p.b
                    s2 = s.strip()
                    if s2:
                        f.write("-" * 60)
                        f.write(nl)
                        #@+<< write the context of p to f >>
                        #@+node:ekr.20031218072017.1465: *5* << write the context of p to f >> (weave)
                        # write the headlines of p, p's parent and p's grandparent.
                        context = []
                        p2 = p.copy()
                        i = 0
                        while i < 3:
                            i += 1
                            if not p2:
                                break
                            context.append(p2.h)
                            p2.moveToParent()
                        context.reverse()
                        indent = ""
                        for line in context:
                            f.write(indent)
                            indent += '\t'
                            f.write(line)
                            f.write(nl)
                        #@-<< write the context of p to f >>
                        f.write("-" * 60)
                        f.write(nl)
                        f.write(s.rstrip() + nl)
        except Exception:
            g.es("exception opening:", filename)
            g.print_exception()
    #@+node:ekr.20031218072017.3209: *3* ic.Import
    #@+node:ekr.20031218072017.3210: *4* ic.createOutline & helpers
    def createOutline(self, parent: Position, ext: str = None, s: str = None) -> Position:
        """
        Create an outline by importing a file, reading the file with the
        given encoding if string s is None.

        ext,        The file extension to be used, or None.
        fileName:   A string or None. The name of the file to be read.
        parent:     The parent position of the created outline.
        s:          A string or None. The file's contents.
        """
        c = self.c
        p = parent.copy()
        self.treeType = '@file'  # Fix #352.
        fileName = c.fullPath(parent)
        if g.is_binary_external_file(fileName):
            return self.import_binary_file(fileName, parent)
        # Init ivars.
        self.encoding = c.getEncoding(parent)
        ext, s = self.init_import(ext, fileName, s)
        if s is None:
            return None

        # Each importer file defines `do_import` at the top level with this signature:
        # def do_import(c: Cmdr, parent: Position, s: str) -> None:

        func = self.dispatch(ext, p)  # The do_import callback.
        # Call the scanning function.
        if g.unitTesting:
            assert func or ext in ('.txt', '.w', '.xxx'), (repr(func), ext, p.h)
        if func and not c.config.getBool('suppress-import-parsing', default=False):
            s = g.toUnicode(s, encoding=self.encoding)
            s = s.replace('\r', '')
            # func is a factory that instantiates the importer class.
            func(c, p, s)
        else:
            # Just copy the file to the parent node.
            s = g.toUnicode(s, encoding=self.encoding)
            s = s.replace('\r', '')
            self.scanUnknownFileType(s, p, ext)
        if g.unitTesting:
            return p

        # #488894: unsettling dialog when saving Leo file
        # #889175: Remember the full fileName.
        c.atFileCommands.rememberReadPath(fileName, p)
        p.contract()
        w = c.frame.body.wrapper
        w.setInsertPoint(0)
        w.seeInsertPoint()
        return p
    #@+node:ekr.20140724064952.18038: *5* ic.dispatch & helpers
    def dispatch(self, ext: str, p: Position) -> Optional[Callable]:
        """Return the correct scanner function for p, an @auto node."""
        # Match the @auto type first, then the file extension.
        return g.app.scanner_for_at_auto(p) or g.app.scanner_for_ext(ext)
    #@+node:ekr.20170405191106.1: *5* ic.import_binary_file
    def import_binary_file(self, fileName: str, parent: Position) -> Position:

        # Fix bug 1185409 importing binary files puts binary content in body editor.
        # Create an @url node.
        c = self.c
        if parent:
            p = parent.insertAsLastChild()
        else:
            p = c.lastTopLevel().insertAfter()
        p.h = f"@url file://{fileName}"
        return p
    #@+node:ekr.20140724175458.18052: *5* ic.init_import
    def init_import(self, ext: str, fileName: str, s: str) -> tuple[str, str]:
        """
        Init ivars imports and read the file into s.
        Return ext, s.
        """
        junk, self.fileName = g.os_path_split(fileName)
        self.methodName, self.fileType = g.os_path_splitext(self.fileName)
        if not ext:
            ext = self.fileType
        ext = ext.lower()
        if not s:
            # Set the kind for error messages in readFileIntoString.
            s, e = g.readFileIntoString(fileName, encoding=self.encoding)
            if s is None:
                return None, None
            if e:
                self.encoding = e
        return ext, s
    #@+node:ekr.20070713075352: *5* ic.scanUnknownFileType & helper
    def scanUnknownFileType(self, s: str, p: Position, ext: str) -> bool:
        """Scan the text of an unknown file type."""
        body = ''
        if ext in ('.html', '.htm'):
            body += '@language html\n'
        elif ext in ('.txt', '.text'):
            body += '@nocolor\n'
        else:
            language = self.languageForExtension(ext)
            if language:
                body += f"@language {language}\n"
        self.setBodyString(p, body + s)
        for p in p.self_and_subtree():
            p.clearDirty()
        return True
    #@+node:ekr.20080811174246.1: *6* ic.languageForExtension
    def languageForExtension(self, ext: str) -> str:
        """Return the language corresponding to the extension ext."""
        unknown = 'unknown_language'
        if ext.startswith('.'):
            ext = ext[1:]
        if ext:
            z = g.app.extra_extension_dict.get(ext)
            if z not in (None, 'none', 'None'):
                language = z
            else:
                language = g.app.extension_dict.get(ext)
            if language in (None, 'none', 'None'):
                language = unknown
        else:
            language = unknown
        # Return the language even if there is no colorizer mode for it.
        return language
    #@+node:ekr.20070806111212: *4* ic.readAtAutoNodes
    def readAtAutoNodes(self) -> None:
        c, p = self.c, self.c.p
        after = p.nodeAfterTree()
        found = False
        while p and p != after:
            if p.isAtAutoNode():
                if p.isAtIgnoreNode():
                    g.warning('ignoring', p.h)
                    p.moveToThreadNext()
                else:
                    c.atFileCommands.readOneAtAutoNode(p)
                    found = True
                    p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
        if not g.unitTesting:
            message = 'finished' if found else 'no @auto nodes in the selected tree'
            g.blue(message)
        c.redraw()
    #@+node:ekr.20031218072017.1810: *4* ic.importDerivedFiles
    def importDerivedFiles(self,
        parent: Position = None,
        paths: list[str] = None,
        command: str = 'Import',
    ) -> Optional[Position]:
        """
        Import one or more external files.
        This is not a command.  It must *not* have an event arg.
        command is None when importing from the command line.
        """
        at, c, u = self.c.atFileCommands, self.c, self.c.undoer
        current = c.p or c.rootPosition()
        if not paths:
            return None
        # Initial open from command line is not undoable.
        if command:
            u.beforeChangeGroup(current, command)
        for fileName in paths:
            fileName = fileName.replace('\\', '/')  # 2011/10/09.
            g.setGlobalOpenDir(fileName)
            isThin = at.scanHeaderForThin(fileName)
            if command:
                undoData = u.beforeInsertNode(parent)
            p = parent.insertAfter()
            if isThin:
                # Create @file node, not a deprecated @thin node.
                p.initHeadString("@file " + fileName)
                at.read(p)
            else:
                p.initHeadString("Imported @file " + fileName)
                at.read(p)
            p.contract()
            p.setDirty()  # 2011/10/09: tell why the file is dirty!
            if command:
                u.afterInsertNode(p, command, undoData)
        current.expand()
        c.setChanged()
        if command:
            u.afterChangeGroup(c.p, command)
        c.redraw(current)
        return p
    #@+node:ekr.20031218072017.3212: *4* ic.importFilesCommand
    def importFilesCommand(
        self,
        files: list[str] = None,
        parent: Position = None,
        shortFn: bool = False,
        treeType: str = None,
        verbose: bool = True,  # Legacy value.
    ) -> None:
        # Not a command.  It must *not* have an event arg.
        c, u = self.c, self.c.undoer
        if not c or not c.p or not files:
            return
        self.treeType = treeType or '@file'
        self.verbose = verbose
        if not parent:
            g.trace('===== no parent', g.callers())
            return
        for fn in files or []:
            # Report exceptions here, not in the caller.
            try:
                g.setGlobalOpenDir(fn)
                # Leo 5.6: Handle undo here, not in createOutline.
                undoData = u.beforeInsertNode(parent)
                p = parent.insertAsLastChild()
                fn = c.relativeDirectory(fn)
                p.h = f"{treeType} {fn}"
                u.afterInsertNode(p, 'Import', undoData)
                p = self.createOutline(parent=p)
                if p:  # createOutline may fail.
                    p.contract()
                    p.setDirty()
                    c.setChanged()
            except Exception:
                g.es_print('Exception importing', fn)
                g.es_exception()
        c.checkOutline()
        parent.expand()
    #@+node:ekr.20160503125237.1: *4* ic.importFreeMind
    def importFreeMind(self, files: list[str]) -> None:
        """
        Import a list of .mm.html files exported from FreeMind:
        http://freemind.sourceforge.net/wiki/index.php/Main_Page
        """
        FreeMindImporter(self.c).import_files(files)
    #@+node:ekr.20241027003435.1: *4* ic.importJupytextFiles
    def importJupytextFiles(self, paths: list[str] = None) -> Optional[Position]:
        """
        Import one or more .ipynb files.
        This is not a command.  It must *not* have an event arg.
        """
        at, c, u = self.c.atFileCommands, self.c, self.c.undoer
        command = 'Import Jupyter Notebook'
        parent = c.p
        if not parent or not paths:
            return None
        u.beforeChangeGroup(parent, command)
        for fileName in paths:
            fileName = fileName.replace('\\', '/')
            g.setGlobalOpenDir(fileName)
            undoData = u.beforeInsertNode(parent)
            p = parent.insertAfter()
            p.initHeadString("@jupytext " + fileName)
            at.readOneAtJupytextNode(p)
            p.contract()
            p.setDirty()
            u.afterInsertNode(p, command, undoData)
        parent.expand()
        c.setChanged()
        u.afterChangeGroup(parent, command)
        c.recolor(parent)
        c.redraw(parent)
        return parent
    #@+node:ekr.20160503125219.1: *4* ic.importMindMap
    def importMindMap(self, files: list[str]) -> None:
        """
        Import a list of .csv files exported from MindJet:
        https://www.mindjet.com/
        """
        MindMapImporter(self.c).import_files(files)
    #@+node:ekr.20031218072017.3224: *4* ic.importWebCommand & helpers
    def importWebCommand(self, files: list[str], webType: str) -> None:
        c, current = self.c, self.c.p
        if current is None:
            return
        if not files:
            return
        self.webType = webType
        for fileName in files:
            g.setGlobalOpenDir(fileName)
            p = self.createOutlineFromWeb(fileName, current)
            p.contract()
            p.setDirty()
            c.setChanged()
        c.redraw(current)
    #@+node:ekr.20031218072017.3225: *5* ic.createOutlineFromWeb
    def createOutlineFromWeb(self, path: str, parent: Position) -> Position:
        c = self.c
        u = c.undoer
        junk, fileName = g.os_path_split(path)
        undoData = u.beforeInsertNode(parent)
        # Create the top-level headline.
        p = parent.insertAfter()
        p.initHeadString(fileName)
        if self.webType == "cweb":
            self.setBodyString(p, "@ignore\n@language cweb")
        # Scan the file, creating one section for each function definition.
        self.scanWebFile(path, p)
        u.afterInsertNode(p, 'Import', undoData)
        return p
    #@+node:ekr.20031218072017.3227: *5* ic.findFunctionDef
    def findFunctionDef(self, s: str, i: int) -> Optional[str]:
        # Look at the next non-blank line for a function name.
        i = g.skip_ws_and_nl(s, i)
        k = g.skip_line(s, i)
        name = None
        while i < k:
            if g.is_c_id(s[i]):
                j = i
                i = g.skip_c_id(s, i)
                name = s[j:i]
            elif s[i] == '(':
                if name:
                    return name
                break
            else:
                i += 1
        return None
    #@+node:ekr.20031218072017.3228: *5* ic.scanBodyForHeadline
    #@+at This method returns the proper headline text.
    # 1. If s contains a section def, return the section ref.
    # 2. cweb only: if s contains @c, return the function name following the @c.
    # 3. cweb only: if s contains @d name, returns @d name.
    # 4. Otherwise, returns "@"
    #@@c

    def scanBodyForHeadline(self, s: str) -> str:
        if self.webType == "cweb":
            #@+<< scan cweb body for headline >>
            #@+node:ekr.20031218072017.3229: *6* << scan cweb body for headline >>
            i = 0
            while i < len(s):
                i = g.skip_ws_and_nl(s, i)
                # Allow constructs such as @ @c, or @ @<.
                if self.isDocStart(s, i):
                    i += 2
                    i = g.skip_ws(s, i)
                if g.match(s, i, "@d") or g.match(s, i, "@f"):
                    # Look for a macro name.
                    directive = s[i : i + 2]
                    i = g.skip_ws(s, i + 2)  # skip the @d or @f
                    if i < len(s) and g.is_c_id(s[i]):
                        j = i
                        i = g.skip_c_id(s, i)
                        return s[j:i]
                    return directive
                if g.match(s, i, "@c") or g.match(s, i, "@p"):
                    # Look for a function def.
                    name = self.findFunctionDef(s, i + 2)
                    return name or "outer function"
                if g.match(s, i, "@<"):
                    # Look for a section def.
                    # A small bug: the section def must end on this line.
                    j = i
                    k = g.find_on_line(s, i, "@>")
                    if k > -1 and (g.match(s, k + 2, "+=") or g.match(s, k + 2, "=")):
                        return s[j : k + 2]  # return the section ref.
                i = g.skip_line(s, i)
            #@-<< scan cweb body for headline >>
        else:
            #@+<< scan noweb body for headline >>
            #@+node:ekr.20031218072017.3230: *6* << scan noweb body for headline >>
            i = 0
            while i < len(s):
                i = g.skip_ws_and_nl(s, i)
                if g.match(s, i, "<<"):
                    k = g.find_on_line(s, i, ">>=")
                    if k > -1:
                        ref = s[i : k + 2]
                        name = s[i + 2 : k].strip()
                        if name != "@others":
                            return ref
                else:
                    name = self.findFunctionDef(s, i)
                    if name:
                        return name
                i = g.skip_line(s, i)
            #@-<< scan noweb body for headline >>
        return "@"  # default.
    #@+node:ekr.20031218072017.3231: *5* ic.scanWebFile (handles limbo)
    def scanWebFile(self, fileName: str, parent: Position) -> None:
        theType = self.webType
        lb = "@<" if theType == "cweb" else "<<"
        rb = "@>" if theType == "cweb" else ">>"
        s, e = g.readFileIntoString(fileName)
        if s is None:
            return
        #@+<< Create a symbol table of all section names >>
        #@+node:ekr.20031218072017.3232: *6* << Create a symbol table of all section names >>
        i = 0
        self.web_st = []
        while i < len(s):
            progress = i
            i = g.skip_ws_and_nl(s, i)
            if self.isDocStart(s, i):
                if theType == "cweb":
                    i += 2
                else:
                    i = g.skip_line(s, i)
            elif theType == "cweb" and g.match(s, i, "@@"):
                i += 2
            elif g.match(s, i, lb):
                i += 2
                j = i
                k = g.find_on_line(s, j, rb)
                if k > -1:
                    self.cstEnter(s[j:k])
            else:
                i += 1
            assert i > progress
        #@-<< Create a symbol table of all section names >>
        #@+<< Create nodes for limbo text and the root section >>
        #@+node:ekr.20031218072017.3233: *6* << Create nodes for limbo text and the root section >>
        i = 0
        while i < len(s):
            progress = i
            i = g.skip_ws_and_nl(s, i)
            if self.isModuleStart(s, i) or g.match(s, i, lb):
                break
            else:
                i = g.skip_line(s, i)
            assert i > progress
        j = g.skip_ws(s, 0)
        if j < i:
            self.createHeadline(parent, "@ " + s[j:i], "Limbo")
        j = i
        if g.match(s, i, lb):
            while i < len(s):
                progress = i
                i = g.skip_ws_and_nl(s, i)
                if self.isModuleStart(s, i):
                    break
                else:
                    i = g.skip_line(s, i)
                assert i > progress
            self.createHeadline(parent, s[j:i], g.angleBrackets(" @ "))

        #@-<< Create nodes for limbo text and the root section >>
        while i < len(s):
            outer_progress = i
            #@+<< Create a node for the next module >>
            #@+node:ekr.20031218072017.3234: *6* << Create a node for the next module >>
            if theType == "cweb":
                assert self.isModuleStart(s, i)
                start = i
                if self.isDocStart(s, i):
                    i += 2
                    while i < len(s):
                        progress = i
                        i = g.skip_ws_and_nl(s, i)
                        if self.isModuleStart(s, i):
                            break
                        else:
                            i = g.skip_line(s, i)
                        assert i > progress
                #@+<< Handle cweb @d, @f, @c and @p directives >>
                #@+node:ekr.20031218072017.3235: *7* << Handle cweb @d, @f, @c and @p directives >>
                if g.match(s, i, "@d") or g.match(s, i, "@f"):
                    i += 2
                    i = g.skip_line(s, i)
                    # Place all @d and @f directives in the same node.
                    while i < len(s):
                        progress = i
                        i = g.skip_ws_and_nl(s, i)
                        if g.match(s, i, "@d") or g.match(s, i, "@f"):
                            i = g.skip_line(s, i)
                        else:
                            break
                        assert i > progress
                    i = g.skip_ws_and_nl(s, i)
                while i < len(s) and not self.isModuleStart(s, i):
                    progress = i
                    i = g.skip_line(s, i)
                    i = g.skip_ws_and_nl(s, i)
                    assert i > progress
                if g.match(s, i, "@c") or g.match(s, i, "@p"):
                    i += 2
                    while i < len(s):
                        progress = i
                        i = g.skip_line(s, i)
                        i = g.skip_ws_and_nl(s, i)
                        if self.isModuleStart(s, i):
                            break
                        assert i > progress
                #@-<< Handle cweb @d, @f, @c and @p directives >>
            else:
                assert self.isDocStart(s, i)
                start = i
                i = g.skip_line(s, i)
                while i < len(s):
                    progress = i
                    i = g.skip_ws_and_nl(s, i)
                    if self.isDocStart(s, i):
                        break
                    else:
                        i = g.skip_line(s, i)
                    assert i > progress
            body = s[start:i]
            body = self.massageWebBody(body)
            headline = self.scanBodyForHeadline(body)
            self.createHeadline(parent, body, headline)
            #@-<< Create a node for the next module >>
            assert i > outer_progress
    #@+node:ekr.20031218072017.3236: *5* ic: Symbol table
    #@+node:ekr.20031218072017.3237: *6* ic.cstCanonicalize
    # We canonicalize strings before looking them up,
    # but strings are entered in the form they are first encountered.

    def cstCanonicalize(self, s: str, lower: bool = True) -> str:
        if lower:
            s = s.lower()
        s = s.replace("\t", " ").replace("\r", "")
        s = s.replace("\n", " ").replace("  ", " ")
        return s.strip()
    #@+node:ekr.20031218072017.3238: *6* ic.cstDump
    def cstDump(self) -> str:
        s = "Web Symbol Table...\n\n"
        for name in sorted(self.web_st):
            s += name + "\n"
        return s
    #@+node:ekr.20031218072017.3239: *6* ic.cstEnter
    # We only enter the section name into the symbol table if the ... convention is not used.

    def cstEnter(self, s: str) -> None:
        # Don't enter names that end in "..."
        s = s.rstrip()
        if s.endswith("..."):
            return
        # Put the section name in the symbol table, retaining capitalization.
        lower = self.cstCanonicalize(s, True)  # do lower
        upper = self.cstCanonicalize(s, False)  # don't lower.
        for name in self.web_st:
            if name.lower() == lower:
                return
        self.web_st.append(upper)
    #@+node:ekr.20031218072017.3240: *6* ic.cstLookup
    # This method returns a string if the indicated string is a prefix of an entry in the web_st.

    def cstLookup(self, target: str) -> str:
        # Do nothing if the ... convention is not used.
        target = target.strip()
        if not target.endswith("..."):
            return target
        # Canonicalize the target name, and remove the trailing "..."
        ctarget = target[:-3]
        ctarget = self.cstCanonicalize(ctarget).strip()
        found = False
        result = target
        for s in self.web_st:
            cs = self.cstCanonicalize(s)
            if cs[: len(ctarget)] == ctarget:
                if found:
                    g.es('', f"****** {target}", 'is also a prefix of', s)
                else:
                    found = True
                    result = s
                    # g.es("replacing",target,"with",s)
        return result
    #@+node:ekr.20140531104908.18833: *3* ic.parse_body
    def parse_body(self, p: Position) -> None:
        """
        Parse p.b as source code, creating a tree of descendant nodes.
        This is essentially an import of p.b.
        """
        c = self.c
        d = g.app.language_extension_dict
        u, undoType = c.undoer, 'parse-body'
        if not p:
            return
        if p.hasChildren():
            g.es_print('can not run parse-body: node has children:', p.h)
            return
        language = c.getLanguage(p)
        self.treeType = '@file'
        ext = '.' + d.get(language)
        parser = g.app.classDispatchDict.get(ext)
        # Fix bug 151: parse-body creates "None declarations"
        if p.isAnyAtFileNode():
            fn = p.anyAtFileNodeName()
            self.methodName, self.fileType = g.os_path_splitext(fn)
        else:
            fileType = d.get(language, 'py')
            self.methodName, self.fileType = p.h, fileType
        if not parser:
            g.es_print(f"parse-body: no parser for @language {language or 'None'}")
            return
        try:
            bunch = u.beforeParseBody(p)
            s = p.b
            p.b = ''
            parser(c, p, s)
            u.afterParseBody(p, undoType, bunch)
            p.expand()
            c.selectPosition(p)
            c.redraw()
        except Exception:
            g.es_exception()
            p.b = s
    #@+node:ekr.20031218072017.3305: *3* ic.Utilities
    #@+node:ekr.20090122201952.4: *4* ic.appendStringToBody & setBodyString (leoImport)
    def appendStringToBody(self, p: Position, s: str) -> None:
        """Similar to c.appendStringToBody,
        but does not recolor the text or redraw the screen."""
        if s:
            p.b = p.b + g.toUnicode(s, self.encoding)

    def setBodyString(self, p: Position, s: str) -> None:
        """
        Similar to c.setBodyString, but does not recolor the text or
        redraw the screen.
        """
        c, v = self.c, p.v
        if not c or not p:
            return
        s = g.toUnicode(s, self.encoding)
        if c.p and p.v == c.p.v:
            w = c.frame.body.wrapper
            i = len(s)
            w.setAllText(s)
            w.setSelectionRange(i, i, insert=i)
        # Keep the body text up-to-date.
        if v.b != s:
            v.setBodyString(s)
            v.setSelection(0, 0)
            p.setDirty()
            if not c.isChanged():
                c.setChanged()
    #@+node:ekr.20031218072017.3306: *4* ic.createHeadline
    def createHeadline(self, parent: Position, body: str, headline: str) -> Position:
        """Create a new VNode as the last child of parent position."""
        p = parent.insertAsLastChild()
        p.initHeadString(headline)
        if body:
            self.setBodyString(p, body)
        return p
    #@+node:ekr.20031218072017.3307: *4* ic.error
    def error(self, s: str) -> None:
        g.es('', s)
    #@+node:ekr.20031218072017.3309: *4* ic.isDocStart & isModuleStart
    # The start of a document part or module in a noweb or cweb file.
    # Exporters may have to test for @doc as well.

    def isDocStart(self, s: str, i: int) -> bool:
        if not g.match(s, i, "@"):
            return False
        j = g.skip_ws(s, i + 1)
        if g.match(s, j, "%defs"):
            return False
        if self.webType == "cweb" and g.match(s, i, "@*"):
            return True
        return g.match(s, i, "@ ") or g.match(s, i, "@\t") or g.match(s, i, "@\n")

    def isModuleStart(self, s: str, i: int) -> bool:
        if self.isDocStart(s, i):
            return True
        return self.webType == "cweb" and (
            g.match(s, i, "@c") or g.match(s, i, "@p") or
            g.match(s, i, "@d") or g.match(s, i, "@f"))
    #@+node:ekr.20031218072017.3312: *4* ic.massageWebBody
    def massageWebBody(self, s: str) -> str:
        theType = self.webType
        lb = "@<" if theType == "cweb" else "<<"
        rb = "@>" if theType == "cweb" else ">>"
        #@+<< Remove most newlines from @space and @* sections >>
        #@+node:ekr.20031218072017.3313: *5* << Remove most newlines from @space and @* sections >>
        i = 0
        while i < len(s):
            progress = i
            i = g.skip_ws_and_nl(s, i)
            if self.isDocStart(s, i):
                # Scan to end of the doc part.
                if g.match(s, i, "@ %def"):
                    # Don't remove the newline following %def
                    i = g.skip_line(s, i)
                    start = end = i
                else:
                    start = end = i
                    i += 2
                while i < len(s):
                    progress2 = i
                    i = g.skip_ws_and_nl(s, i)
                    if self.isModuleStart(s, i) or g.match(s, i, lb):
                        end = i
                        break
                    elif theType == "cweb":
                        i += 1
                    else:
                        i = g.skip_to_end_of_line(s, i)
                    assert i > progress2
                # Remove newlines from start to end.
                doc = s[start:end]
                doc = doc.replace("\n", " ")
                doc = doc.replace("\r", "")
                doc = doc.strip()
                if doc:
                    if doc == "@":
                        doc = "@ " if self.webType == "cweb" else "@\n"
                    else:
                        doc += "\n\n"
                    s = s[:start] + doc + s[end:]
                    i = start + len(doc)
            else:
                i = g.skip_line(s, i)
            assert i > progress
        #@-<< Remove most newlines from @space and @* sections >>
        #@+<< Replace abbreviated names with full names >>
        #@+node:ekr.20031218072017.3314: *5* << Replace abbreviated names with full names >>
        i = 0
        while i < len(s):
            progress = i
            if g.match(s, i, lb):
                i += 2
                j = i
                k = g.find_on_line(s, j, rb)
                if k > -1:
                    name = s[j:k]
                    name2 = self.cstLookup(name)
                    if name != name2:
                        # Replace name by name2 in s.
                        s = s[:j] + name2 + s[k:]
                        i = j + len(name2)
            i = g.skip_line(s, i)
            assert i > progress
        #@-<< Replace abbreviated names with full names >>
        s = s.rstrip()
        return s
    #@+node:ekr.20031218072017.1463: *4* ic.setEncoding (deprecated)
    def setEncoding(self, p: Position = None, default: str = None) -> None:
        g.deprecated()
        c = self.c
        self.encoding = c.getEncoding(p)
    #@-others
#@+node:ekr.20160503144404.1: ** class MindMapImporter
class MindMapImporter:
    """Mind Map Importer class."""

    def __init__(self, c: Cmdr) -> None:
        """ctor for MindMapImporter class."""
        self.c = c
    #@+others
    #@+node:ekr.20160503130209.1: *3* mindmap.create_outline
    def create_outline(self, path: str) -> Position:
        c = self.c
        junk, fileName = g.os_path_split(path)
        undoData = c.undoer.beforeInsertNode(c.p)
        # Create the top-level headline.
        p = c.lastTopLevel().insertAfter()
        fn = g.shortFileName(path).strip()
        if fn.endswith('.csv'):
            fn = fn[:-4]
        p.h = fn
        try:
            f = open(path)
            self.scan(f, p)
            f.close()
            c.redraw()
        except Exception:
            g.es_print('Invalid MindJet file:', fn)
        c.undoer.afterInsertNode(p, 'Import', undoData)
        return p
    #@+node:ekr.20160503144647.1: *3* mindmap.import_files
    def import_files(self, files: list[str]) -> None:
        """Import a list of MindMap (.csv) files."""
        c = self.c
        if files:
            for fileName in files:
                g.setGlobalOpenDir(fileName)
                p = self.create_outline(fileName)
                p.contract()
                p.setDirty()
                c.setChanged()
            c.redraw(p)
    #@+node:ekr.20160504043243.1: *3* mindmap.prompt_for_files
    def prompt_for_files(self) -> None:
        """Prompt for a list of MindJet (.csv) files and import them."""
        c = self.c
        filetypes = [
            ("MindJet files", "*.csv"),
            ("All files", "*"),
        ]
        names = g.app.gui.runOpenFilesDialog(c,
            title="Import MindJet File", filetypes=filetypes)
        c.bringToFront()
        if names:
            g.chdir(names[0])
            self.import_files(names)
    #@+node:ekr.20160503130256.1: *3* mindmap.scan & helpers
    def scan(self, f: io.TextIOBase, target: Position) -> None:
        """Create an outline from a MindMap (.csv) file."""
        reader = csv.reader(f)  # Yields list of lists.
        max_chars_in_header = 80
        n1 = n = target.level()
        p = target.copy()
        for row in list(reader)[1:]:
            # Row is a list of fields.
            new_level = self.csv_level(row) + n1
            self.csv_string(row)
            if new_level > n:
                p = p.insertAsLastChild().copy()
                p.b = self.csv_string(row)
                n = n + 1
            elif new_level == n:
                p = p.insertAfter().copy()
                p.b = self.csv_string(row)
            elif new_level < n:
                for item in p.parents():
                    if item.level() == new_level - 1:
                        p = item.copy()
                        break
                p = p.insertAsLastChild().copy()
                p.b = self.csv_string(row)
                n = p.level()
        for p in target.unique_subtree():
            lines = p.b.splitlines()
            if len(lines) == 1 and len(lines[0]) < max_chars_in_header:
                p.h = lines[0]
                p.b = ""
            else:
                p.h = "@node_with_long_text"
    #@+node:ekr.20160503130810.4: *4* mindmap.csv_level
    def csv_level(self, row: list[str]) -> int:
        """
        Return the level of the given row, a list of fields.
        """
        count = 0
        while count <= len(row):
            if row[count]:
                return count + 1
            count = count + 1
        return -1
    #@+node:ekr.20160503130810.5: *4* mindmap.csv_string
    def csv_string(self, row: list[str]) -> str:
        """Return the string for the given csv row."""
        count = 0
        while count <= len(row):
            if row[count]:
                return row[count]
            count = count + 1
        return None
    #@-others
#@+node:ekr.20161006100941.1: ** class MORE_Importer
class MORE_Importer:
    """Class to import MORE files."""

    def __init__(self, c: Cmdr) -> None:
        """ctor for MORE_Importer class."""
        self.c = c
    #@+others
    #@+node:ekr.20161006101111.1: *3* MORE.prompt_for_files
    def prompt_for_files(self) -> None:
        """Prompt for a list of MORE files and import them."""
        c = self.c
        filetypes = [
            ("All files", "*"),
        ]
        names = g.app.gui.runOpenFilesDialog(c,
            title="Import MORE Files", filetypes=filetypes)
        c.bringToFront()
        if names:
            g.chdir(names[0])
            self.import_files(names)
    #@+node:ekr.20161006101218.1: *3* MORE.import_files
    def import_files(self, files: list[str]) -> None:
        """Import a list of MORE (.csv) files."""
        c = self.c
        if files:
            changed = False
            for fileName in files:
                g.setGlobalOpenDir(fileName)
                p = self.import_file(fileName)
                if p:
                    p.contract()
                    p.setDirty()
                    c.setChanged()
                    changed = True
            if changed:
                c.redraw(p)
    #@+node:ekr.20161006101347.1: *3* MORE.import_file
    def import_file(self, fileName: str) -> Optional[Position]:  # Not a command, so no event arg.
        c = self.c
        u = c.undoer
        ic = c.importCommands
        if not c.p:
            return None
        ic.encoding = c.getEncoding(c.p)
        g.setGlobalOpenDir(fileName)
        s, _e = g.readFileIntoString(fileName)
        if s is None:
            return None
        s = s.replace('\r', '')  # Fixes bug 626101.
        lines = g.splitLines(s)
        # Convert the string to an outline and insert it after the current node.
        if self.check_lines(lines):
            last = c.lastTopLevel()
            undoData = u.beforeInsertNode(c.p)
            root = last.insertAfter()
            root.h = fileName
            p = self.import_lines(lines, root)
            if p:
                c.endEditing()
                c.checkOutline()
                p.setDirty()
                c.setChanged()
                u.afterInsertNode(root, 'Import MORE File', undoData)
                c.selectPosition(root)
                c.redraw()
                return root
        if not g.unitTesting:
            g.es("not a valid MORE file", fileName)
        return None
    #@+node:ekr.20031218072017.3215: *3* MORE.import_lines
    def import_lines(self, strings: list[str], first_p: Position) -> Position:
        c = self.c
        if not strings:
            return None
        if not self.check_lines(strings):
            return None
        firstLevel, junk = self.headlineLevel(strings[0])
        lastLevel = -1
        theRoot = last_p = None
        index = 0
        while index < len(strings):
            progress = index
            s = strings[index]
            level, junk = self.headlineLevel(s)
            level -= firstLevel
            if level >= 0:
                #@+<< Link a new position p into the outline >>
                #@+node:ekr.20031218072017.3216: *4* << Link a new position p into the outline >>
                assert level >= 0
                if not last_p:
                    theRoot = p = first_p.insertAsLastChild()  # 2016/10/06.
                elif level == lastLevel:
                    p = last_p.insertAfter()
                elif level == lastLevel + 1:
                    p = last_p.insertAsNthChild(0)
                else:
                    assert level < lastLevel
                    while level < lastLevel:
                        lastLevel -= 1
                        last_p = last_p.parent()
                        assert last_p
                        assert lastLevel >= 0
                    p = last_p.insertAfter()
                last_p = p
                lastLevel = level
                #@-<< Link a new position p into the outline >>
                #@+<< Set the headline string, skipping over the leader >>
                #@+node:ekr.20031218072017.3217: *4* << Set the headline string, skipping over the leader >>
                j = 0
                while g.match(s, j, '\t') or g.match(s, j, ' '):
                    j += 1
                if g.match(s, j, "+ ") or g.match(s, j, "- "):
                    j += 2
                p.initHeadString(s[j:])
                #@-<< Set the headline string, skipping over the leader >>
                #@+<< Count the number of following body lines >>
                #@+node:ekr.20031218072017.3218: *4* << Count the number of following body lines >>
                bodyLines = 0
                index += 1  # Skip the headline.
                while index < len(strings):
                    s = strings[index]
                    level, junk = self.headlineLevel(s)
                    level -= firstLevel
                    if level >= 0:
                        break
                    # Remove first backslash of the body line.
                    if g.match(s, 0, '\\'):
                        strings[index] = s[1:]
                    bodyLines += 1
                    index += 1
                #@-<< Count the number of following body lines >>
                #@+<< Add the lines to the body text of p >>
                #@+node:ekr.20031218072017.3219: *4* << Add the lines to the body text of p >>
                if bodyLines > 0:
                    body = ""
                    n = index - bodyLines
                    while n < index:
                        body += strings[n].rstrip()
                        if n != index - 1:
                            body += "\n"
                        n += 1
                    p.setBodyString(body)
                #@-<< Add the lines to the body text of p >>
                p.setDirty()
            else:
                index += 1
            assert progress < index
        if theRoot:
            theRoot.setDirty()
            c.setChanged()
        c.redraw()
        return theRoot
    #@+node:ekr.20031218072017.3222: *3* MORE.headlineLevel
    def headlineLevel(self, s: str) -> tuple[int, bool]:
        """return the headline level of s,or -1 if the string is not a MORE headline."""
        level = 0
        i = 0
        while i < len(s) and s[i] in ' \t':  # 2016/10/06: allow blanks or tabs.
            level += 1
            i += 1
        plusFlag = g.match(s, i, "+")
        if g.match(s, i, "+ ") or g.match(s, i, "- "):
            return level, plusFlag
        return -1, plusFlag
    #@+node:ekr.20031218072017.3223: *3* MORE.check & check_lines
    def check(self, s: str) -> bool:
        s = s.replace("\r", "")
        strings = g.splitLines(s)
        return self.check_lines(strings)

    def check_lines(self, strings: list[str]) -> bool:

        if not strings:
            return False
        level1, plusFlag = self.headlineLevel(strings[0])
        if level1 == -1:
            return False
        # Check the level of all headlines.
        lastLevel = level1
        for s in strings:
            level, newFlag = self.headlineLevel(s)
            if level == -1:
                return True  # A body line.
            if level < level1 or level > lastLevel + 1:
                return False  # improper level.
            if level > lastLevel and not plusFlag:
                return False  # parent of this node has no children.
            if level == lastLevel and plusFlag:
                return False  # last node has missing child.
            lastLevel = level
            plusFlag = newFlag
        return True
    #@-others
#@+node:ekr.20130823083943.12596: ** class RecursiveImportController
class RecursiveImportController:
    """Recursively import all python files in a directory and clean the result."""

    # Similar to p.isAnyAtFileNode, but not the same.
    file_pattern = re.compile(r'^(@@|@)(auto|clean|edit|file|nosent)')

    #@+others
    #@+node:ekr.20130823083943.12615: *3*  ric.ctor
    def __init__(self, c: Cmdr,
        *,  # All other args are kwargs.
        dir_: Optional[str],
        ignore_pattern: re.Pattern = None,
        kind: str,
        recursive: bool = True,
        safe_at_file: bool = True,
        theTypes: list[str] = None,
        verbose: bool = True,  # legacy value.
    ) -> None:
        """Ctor for RecursiveImportController class."""
        self.c = c
        self.ignore_pattern = ignore_pattern or re.compile(r'\.git|node_modules')
        self.kind = kind  # in ('@auto', '@clean', '@edit', '@file', '@nosent')
        self.n_files: int = 0
        self.recursive = recursive
        self.root: Position = None
        file_name = c.fileName()
        self.outline_directory: Optional[str] = os.path.dirname(file_name) if file_name else None
        self.safe_at_file = safe_at_file
        self.theTypes = theTypes
        self.verbose = verbose
    #@+node:ekr.20230828090452.1: *3* ric.error
    def error(self, message: str) -> None:
        """Print an error message."""
        g.es_print(message, color='red')
    #@+node:ekr.20130823083943.12597: *3* ric.import_dir
    def import_dir(self, dir_: str, parent: Position) -> None:
        """Import selected files from dir_, a directory."""
        files = []
        if not os.path.exists(dir_):
            self.error(f"Not found: {dir_!r}")
            return
        if g.os_path_isfile(dir_):
            files = [dir_]
        else:
            if self.verbose:
                print(f"importing: {os.path.normpath(dir_)}")
            files = list(sorted(os.listdir(dir_)))

        dirs: list[str] = []
        files2: list[str] = []
        for path in files:
            try:
                # Catch path exceptions: keep going on small errors.
                path = g.os_path_join(dir_, path)
                if g.os_path_isfile(path):
                    name, ext = g.os_path_splitext(path)
                    if ext in self.theTypes:
                        files2.append(path)
                elif self.recursive:
                    if not self.ignore_pattern.search(path):
                        dirs.append(path)
            except OSError:
                self.error(f"Exception computing: {path!r}")
                g.es_exception()
        if files2 or dirs:
            parent = parent.insertAsLastChild()
            parent.v.h = dir_
            if files2:
                for f in files2:
                    if not self.ignore_pattern.search(f):
                        self.import_one_file(f, parent=parent)
            if dirs:
                for dir_ in sorted(dirs):
                    self.import_dir(dir_, parent)
    #@+node:ekr.20170404103953.1: *3* ric.import_one_file
    def import_one_file(self, path: str, parent: Position) -> None:
        """Import one file to the last top-level node."""
        c = self.c
        self.n_files += 1
        if self.kind == '@edit':
            p = parent.insertAsLastChild()
            path = c.relativeDirectory(path)
            p.v.h = '@edit ' + path.replace('\\', '/')
            s, e = g.readFileIntoString(path, kind=self.kind)
            p.v.b = s
            return
        # #1484: Use this for @auto as well.
        c.importCommands.importFilesCommand(
            files=[path],
            parent=parent,
            shortFn=True,
            treeType='@file',  # '@auto','@clean','@nosent' cause problems.
            verbose=self.verbose,  # Leo 6.6.
        )
        p = parent.lastChild()
        p.h = self.kind + p.h[5:]  # Honor the requested kind.
        if self.safe_at_file:
            p.v.h = '@' + p.v.h
    #@+node:ekr.20130823083943.12607: *3* ric.post_process
    def post_process(self, p: Position) -> None:
        """
        Traverse p's tree, replacing all nodes that start with prefix
        by the smallest equivalent @path or @file node.
        """
        assert self.outline_directory
        self.fix_back_slashes(p)
        for p2 in p.subtree():
            self.minimize_headline(p2)
        if self.kind not in ('@auto', '@edit'):
            self.remove_empty_nodes(p)
            self.move_leading_blank_lines(p)
        self.clear_dirty_bits(p)
    #@+node:ekr.20130823083943.12608: *4* ric.clear_dirty_bits
    def clear_dirty_bits(self, p: Position) -> None:
        c = self.c
        c.clearChanged()  # Clears *all* dirty bits.
        for p in p.self_and_subtree(copy=False):
            p.clearDirty()
    #@+node:ekr.20130823083943.12609: *4* ric.dump_headlines
    def dump_headlines(self, p: Position) -> None:
        # show all headlines.
        for p in p.self_and_subtree(copy=False):
            print(p.h)
    #@+node:ekr.20130823083943.12610: *4* ric.fix_back_slashes
    def fix_back_slashes(self, p: Position) -> None:
        """Convert backslash to slash in all headlines."""
        for p in p.self_and_subtree(copy=False):
            s = p.h.replace('\\', '/')
            if s != p.h:
                p.v.h = s
    #@+node:ekr.20130823083943.12611: *4* ric.minimize_headline
    def minimize_headline(self, p: Position) -> None:
        """
        Adjust headlines and add @path directives to headlines or body text.

        Create an @path directive in  @<file> nodes.

        fix_back_slashes has converted backslashes to forward slashes.
        """

        # The outline_directory is the outline's directory.
        assert os.path.isabs(self.outline_directory), repr(self.outline_directory)

        def norm(path: str) -> str:
            """A hack to handle Windows drive names."""
            return path.lower() if g.isWindows else path

        def rel_path(path: str) -> str:
            path = path[len_outline_dir:].strip()
            if path.startswith('/'):
                path = path[1:]
            return path

        # The paths of all @<file> nodes should start with outline_dir.
        p.h = p.h.replace('\\', '/')  # Defensive.
        outline_dir = norm(self.outline_directory.replace('\\', '/'))
        len_outline_dir = len(outline_dir)

        if m := self.file_pattern.match(p.h):
            # p is an @file node of some kind.
            kind = m.group(0)
            path = p.h[len(kind) :].strip()
            if norm(path).startswith(outline_dir):
                file_name = os.path.basename(path)
                dir_name = os.path.dirname(path)
                r_path = rel_path(dir_name)
                p.h = f"{kind} {file_name}"
                if r_path:
                    p.b = f"@path {r_path}\n{p.b}"
            return

        # Handle everything else.
        if norm(p.h).startswith(outline_dir):
            r_path = rel_path(p.h)
            if r_path:
                p.h = f"path: {r_path}"
    #@+node:ekr.20230831011155.1: *4* ric.move_leading_blank_lines
    def move_leading_blank_lines(self, parent: Position) -> None:
        """
        Move leading blank lines from one node to its previous sibling.
        """
        for p in parent.subtree():
            if p.hasBack() and p.b.startswith('\n'):
                back = p.back()
                while p.b.startswith('\n'):
                    p.b = p.b[1:]
                    back.b = back.b + '\n'
    #@+node:ekr.20130823083943.12612: *4* ric.remove_empty_nodes
    def remove_empty_nodes(self, p: Position) -> None:
        """Remove empty nodes. Not called for @auto or @edit trees."""
        c = self.c

        def has_significant_children(p: Position) -> bool:
            """Return True if p has any descendant that is not an @path node."""
            if not p.hasChildren():
                return False
            if not p.h.startswith('path: '):
                return True
            for p2 in p.subtree():
                if has_significant_children(p2):
                    return True
            return False

        # Never remove p itself!
        aList = [
            p2 for p2 in p.subtree()
                if not p2.b.strip() and not has_significant_children(p2)]
        if aList:
            c.deletePositionsInList(aList)  # Don't redraw.
    #@+node:ekr.20230829043849.1: *3* ric_resolve_dir_arg
    def resolve_dir_arg(self, arg: str) -> Optional[str]:
        """
        arg can be None or a path (relative or absolute) to a file or
        directory.

        Return True if the arg can be resolved to a file/directory within
        self.outline_directory.

        Relative paths are considered to be relative to self.outline_directory.
        As a result, there is no need to call os.path.relpath anywhere in this
        class.
        """

        arg1 = arg  # For asserts.
        outline_dir = self.outline_directory

        # Initial sanity checks.
        assert outline_dir, repr(outline_dir)
        assert os.path.isabs(outline_dir), repr(outline_dir)
        assert os.path.exists(outline_dir), repr(outline_dir)
        assert os.path.isdir(outline_dir), repr(outline_dir)

        # Resolve arg relative to the outline's directory.
        if arg is None:
            arg = outline_dir
        elif not os.path.isabs(arg):
            arg = os.path.join(outline_dir, arg)
        if not os.path.exists(arg):
            return None

        # Final sanity checks.
        assert arg, repr(arg1)
        assert os.path.isabs(arg), repr(arg1)
        assert os.path.exists(arg), repr(arg1)
        return arg
    #@+node:ekr.20130823083943.12613: *3* ric.run
    def run(self, dir_: Optional[str]) -> None:
        """
        dir_ can be None, a directory contained in the outline's directory, or a single file.

        Import all files in the dir_ directory, or the outline's directory if dir_ is None.

        Import all files whose extension matches self.theTypes in dir_.
        In fact, dir_ can be a path to a single file.
        """
        if self.kind not in ('@auto', '@clean', '@edit', '@file', '@nosent'):
            self.error(f"bad kind param: {self.kind!r}")
            return
        if not self.outline_directory:
            self.error('The outline has no name. Please save it.')
            return

        # Resolve dir_ to an absolute path.
        dir_1 = dir_
        dir_ = self.resolve_dir_arg(dir_)
        if dir_ is None:
            self.error(f"invalid 'dir_' argument: {dir_1!r}")
            return

        # Import all requested files.
        try:
            c, u = self.c, self.c.undoer
            t1 = time.time()
            g.app.disable_redraw = True
            last = c.lastTopLevel()
            c.selectPosition(last)
            undoData = u.beforeInsertNode(last)
            # Always create a new last top-level node.
            self.root = parent = last.insertAfter()
            parent.v.h = 'imported files'
            # Special case for a single file.
            self.n_files = 0
            if g.os_path_isfile(dir_):
                if self.verbose:
                    # Only print this message if importing a *single* file.
                    print('')
                    print(f"importing file: {os.path.normpath(dir_)}")
                self.import_one_file(dir_, parent)
            else:
                self.import_dir(dir_, parent)
            self.post_process(parent)
            u.afterInsertNode(parent, 'recursive-import', undoData)
        except Exception:
            self.error('Exception in recursive import')
            g.es_exception()
        finally:
            g.app.disable_redraw = False
            for p2 in parent.self_and_subtree(copy=False):
                p2.contract()
            c.redraw(parent)
        if not g.unitTesting:
            t2 = time.time()
            n = len(list(parent.subtree()))
            g.es_print(
                f"imported {n} node{g.plural(n)} "
                f"in {self.n_files} file{g.plural(self.n_files)} "
                f"in {t2 - t1:2.2f} seconds")
    #@-others
#@+node:ekr.20161006071801.1: ** class TabImporter
class TabImporter:
    """
    A class to import a file whose outline levels are indicated by
    leading tabs or blanks (but not both).
    """

    def __init__(self, c: Cmdr, separate: bool = True) -> None:
        """Ctor for the TabImporter class."""
        self.c = c
        self.root: Position = None
        self.separate = separate
        self.stack: list[tuple[int, Position]] = []

    #@+others
    #@+node:ekr.20161006071801.2: *3* tabbed.check
    def check(self, lines: list[str], warn: bool = True) -> bool:
        """Return False and warn if lines contains mixed leading tabs/blanks."""
        blanks, tabs = 0, 0
        for s in lines:
            lws = self.lws(s)
            if '\t' in lws:
                tabs += 1
            if ' ' in lws:
                blanks += 1
        if tabs and blanks:
            if warn:
                g.es_print('intermixed leading blanks and tabs.')
            return False
        return True
    #@+node:ekr.20161006071801.3: *3* tabbed.dump_stack
    def dump_stack(self) -> None:
        """Dump the stack, containing (level, p) tuples."""
        g.trace('==========')
        for i, data in enumerate(self.stack):
            level, p = data
            print(f"{i:2} {level} {p.h!r}")
    #@+node:ekr.20161006073129.1: *3* tabbed.import_files
    def import_files(self, files: list[str]) -> None:
        """Import a list of tab-delimited files."""
        c, u = self.c, self.c.undoer
        if files:
            p = None
            for fn in files:
                try:
                    g.setGlobalOpenDir(fn)
                    s = open(fn).read()
                    s = s.replace('\r', '')
                except Exception:
                    continue
                if s.strip() and self.check(g.splitLines(s)):
                    undoData = u.beforeInsertNode(c.p)
                    last = c.lastTopLevel()
                    self.root = p = last.insertAfter()
                    self.scan(s)
                    p.h = g.shortFileName(fn)
                    p.contract()
                    p.setDirty()
                    u.afterInsertNode(p, 'Import Tabbed File', undoData)
                if p:
                    c.setChanged()
                    c.redraw(p)
    #@+node:ekr.20161006071801.4: *3* tabbed.lws
    def lws(self, s: str) -> str:
        """Return the length of the leading whitespace of s."""
        for i, ch in enumerate(s):
            if ch not in ' \t':
                return s[:i]
        return s
    #@+node:ekr.20161006072958.1: *3* tabbed.prompt_for_files
    def prompt_for_files(self) -> None:
        """Prompt for a list of FreeMind (.mm.html) files and import them."""
        c = self.c
        types = [
            ("All files", "*"),
        ]
        names = g.app.gui.runOpenFilesDialog(c,
            title="Import Tabbed File", filetypes=types)
        c.bringToFront()
        if names:
            g.chdir(names[0])
            self.import_files(names)
    #@+node:ekr.20161006071801.5: *3* tabbed.scan
    def scan(self, s1: str, fn: str = None, root: Position = None) -> Position:
        """Create the outline corresponding to s1."""
        c = self.c
        # self.root can be None if we are called from a script or unit test.
        if not self.root:
            last = root if root else c.lastTopLevel()  # For unit testing.
            self.root = last.insertAfter()
            if fn:
                self.root.h = fn
        lines = g.splitLines(s1)
        self.stack = []
        # Redo the checks in case we are called from a script.
        if s1.strip() and self.check(lines):
            for s in lines:
                if s.strip() or not self.separate:
                    self.scan_helper(s)
        return self.root
    #@+node:ekr.20161006071801.6: *3* tabbed.scan_helper
    def scan_helper(self, s: str) -> int:
        """Update the stack as necessary and return level."""
        root, separate, stack = self.root, self.separate, self.stack
        if stack:
            level, parent = stack[-1]
        else:
            level, parent = 0, None
        lws = len(self.lws(s))
        h = s.strip()
        if lws == level:
            if separate or not parent:
                # Replace the top of the stack with a new entry.
                if stack:
                    stack.pop()
                grand_parent = stack[-1][1] if stack else root
                parent = grand_parent.insertAsLastChild()  # lws == level
                parent.h = h
                stack.append((level, parent),)
            elif not parent.h:
                parent.h = h
        elif lws > level:
            # Create a new parent.
            level = lws
            parent = parent.insertAsLastChild()
            parent.h = h
            stack.append((level, parent),)
        else:
            # Find the previous parent.
            while stack:
                level2, parent2 = stack.pop()
                if level2 == lws:
                    grand_parent = stack[-1][1] if stack else root
                    parent = grand_parent.insertAsLastChild()  # lws < level
                    parent.h = h
                    level = lws
                    stack.append((level, parent),)
                    break
            else:
                level = 0
                parent = root.insertAsLastChild()
                parent.h = h
                stack = [(0, parent),]
        assert parent and parent == stack[-1][1]  # An important invariant.
        assert level == stack[-1][0], (level, stack[-1][0])
        if not separate:
            parent.b = parent.b + self.undent(level, s)
        return level
    #@+node:ekr.20161006071801.7: *3* tabbed.undent
    def undent(self, level: int, s: str) -> str:
        """Unindent all lines of p.b by level."""
        if level <= 0:
            return s
        if s.strip():
            lines = g.splitLines(s)
            ch = lines[0][0]
            assert ch in ' \t', repr(ch)
            # Check that all lines start with the proper lws.
            lws = ch * level
            for s in lines:
                if not s.startswith(lws):
                    g.trace(f"bad indentation: {s!r}")
                    return s
            return ''.join([z[len(lws) :] for z in lines])
        return ''
    #@-others
#@+node:ekr.20200310060123.1: ** class ToDoImporter
class ToDoImporter:

    def __init__(self, c: Cmdr) -> None:
        self.c = c

    #@+others
    #@+node:ekr.20200310103606.1: *3* todo_i.get_tasks_from_file
    def get_tasks_from_file(self, path: str) -> list[ToDoTask]:
        """Return the tasks from the given path."""
        tag = 'import-todo-text-files'
        if not os.path.exists(path):
            print(f"{tag}: file not found: {path}")
            return []
        try:
            with open(path, 'r') as f:
                contents = f.read()
                tasks = self.parse_file_contents(contents)
            return tasks
        except Exception:
            print(f"unexpected exception in {tag}")
            g.es_exception()
            return []
    #@+node:ekr.20200310101028.1: *3* todo_i.import_files
    def import_files(self, files: list[str]) -> dict[str, list[ToDoTask]]:
        """
        Import all todo.txt files in the given list of file names.

        Return a dict: keys are full paths, values are lists of ToDoTasks"
        """
        d, tag = {}, 'import-todo-text-files'
        for path in files:
            try:
                with open(path, 'r') as f:
                    contents = f.read()
                    tasks = self.parse_file_contents(contents)
                    d[path] = tasks
            except Exception:
                print(f"unexpected exception in {tag}")
                g.es_exception()
        return d
    #@+node:ekr.20200310062758.1: *3* todo_i.parse_file_contents
    # Patterns...
    mark_s = r'([x]\ )'
    priority_s = r'(\([A-Z]\)\ )'
    date_s = r'([0-9]{4}-[0-9]{2}-[0-9]{2}\ )'
    task_s = r'\s*(.+)'
    line_s = fr"^{mark_s}?{priority_s}?{date_s}?{date_s}?{task_s}$"
    line_pat = re.compile(line_s)

    def parse_file_contents(self, s: str) -> list[ToDoTask]:
        """
        Parse the contents of a file.
        Return a list of ToDoTask objects.
        """
        trace = False
        tasks = []
        for line in g.splitLines(s):
            if not line.strip():
                continue
            if trace:
                print(f"task: {line.rstrip()!s}")
            m = self.line_pat.match(line)
            if not m:
                print(f"invalid task: {line.rstrip()!s}")
                continue
            # Groups 1, 2 and 5 are context independent.
            completed = m.group(1)
            priority = m.group(2)
            task_s = m.group(5)
            if not task_s:
                print(f"invalid task: {line.rstrip()!s}")
                continue
            # Groups 3 and 4 are context dependent.
            if m.group(3) and m.group(4):
                complete_date = m.group(3)
                start_date = m.group(4)
            elif completed:
                complete_date = m.group(3)
                start_date = ''
            else:
                start_date = m.group(3) or ''
                complete_date = ''
            if completed and not complete_date:
                print(f"no completion date: {line.rstrip()!s}")
            tasks.append(ToDoTask(
                bool(completed), priority, start_date, complete_date, task_s))
        return tasks
    #@+node:ekr.20200310100919.1: *3* todo_i.prompt_for_files
    def prompt_for_files(self) -> dict[str, list[ToDoTask]]:
        """
        Prompt for a list of todo.text files and import them.

        Return a python dict. Keys are full paths; values are lists of ToDoTask objects.
        """
        c = self.c
        types = [
            ("Text files", "*.txt"),
            ("All files", "*"),
        ]
        names = g.app.gui.runOpenFilesDialog(c,
            title="Import todo.txt File", filetypes=types)
        c.bringToFront()
        if not names:
            return {}
        g.chdir(names[0])
        d = self.import_files(names)
        for key in sorted(d):
            tasks = d.get(key)
            print(f"tasks in {g.shortFileName(key)}...\n")
            for task in tasks:
                print(f"    {task}")
        return d
    #@-others
#@+node:ekr.20200310063208.1: ** class ToDoTask
class ToDoTask:
    """A class representing the components of a task line."""

    def __init__(self,
        completed: bool,
        priority: str,
        start_date: str,
        complete_date: str,
        task_s: str,
    ) -> None:
        self.completed = completed
        self.priority = priority and priority[1] or ''
        self.start_date = start_date and start_date.rstrip() or ''
        self.complete_date = complete_date and complete_date.rstrip() or ''
        self.task_s = task_s.strip()
        # Parse tags into separate dictionaries.
        self.projects: list[str] = []
        self.contexts: list[str] = []
        self.key_vals: list[str] = []
        self.parse_task()

    #@+others
    #@+node:ekr.20200310075514.1: *3* task.__repr__ & __str__
    def __repr__(self) -> str:
        start_s = self.start_date if self.start_date else ''
        end_s = self.complete_date if self.complete_date else ''
        mark_s = '[X]' if self.completed else '[ ]'
        result = [
            f"Task: "
            f"{mark_s} "
            f"{self.priority:1} "
            f"start: {start_s:10} "
            f"end: {end_s:10} "
            f"{self.task_s}"
        ]
        for ivar in ('contexts', 'projects', 'key_vals'):
            aList = getattr(self, ivar, None)
            if aList:
                result.append(f"{' '*13}{ivar}: {aList}")
        return '\n'.join(result)

    __str__ = __repr__
    #@+node:ekr.20200310063138.1: *3* task.parse_task
    # Patterns...
    project_pat = re.compile(r'(\+\S+)')
    context_pat = re.compile(r'(@\S+)')
    key_val_pat = re.compile(r'((\S+):(\S+))')  # Might be a false match.

    def parse_task(self) -> None:

        trace = False and not g.unitTesting
        s = self.task_s
        table = (
            ('context', self.context_pat, self.contexts),
            ('project', self.project_pat, self.projects),
            ('key:val', self.key_val_pat, self.key_vals),
        )
        for kind, pat, aList in table:
            for m in re.finditer(pat, s):
                # Check for false key:val match:
                if pat == self.key_val_pat:
                    key, value = m.group(2), m.group(3)
                    if ':' in key or ':' in value:
                        break
                tag = m.group(1)
                # Add the tag.
                if tag in aList:
                    if trace:
                        g.trace('Duplicate tag:', tag)
                else:
                    if trace:
                        g.trace(f"Add {kind} tag: {tag!s}")
                    aList.append(tag)
                # Remove the tag from the task.
                s = re.sub(pat, "", s)
        if s != self.task_s:
            self.task_s = s.strip()
    #@-others
#@+node:ekr.20141210051628.26: ** class ZimImportController
class ZimImportController:
    """
    A class to import Zim folders and files: http://zim-wiki.org/
    First use Zim to export your project to rst files.

    Original script by Davy Cottet.

    User options:
        @int rst_level = 0
        @string rst_type
        @string zim_node_name
        @string path_to_zim

    """
    #@+others
    #@+node:ekr.20141210051628.31: *3* zic.__init__ & zic.reloadSettings
    def __init__(self, c: Cmdr) -> None:
        """Ctor for ZimImportController class."""
        self.c = c
        self.pathToZim = c.config.getString('path-to-zim')
        self.rstLevel = c.config.getInt('zim-rst-level') or 0
        self.rstType = c.config.getString('zim-rst-type') or 'rst'
        self.zimNodeName = c.config.getString('zim-node-name') or 'Imported Zim Tree'
    #@+node:ekr.20141210051628.28: *3* zic.parseZimIndex
    def parseZimIndex(self) -> list[tuple[int, str, list[str]]]:
        """
        Parse Zim wiki index.rst and return a list of tuples (level, name, path) or None.
        """
        # c = self.c
        pathToZim = g.os_path_abspath(self.pathToZim)
        pathToIndex = g.os_path_join(pathToZim, 'index.rst')
        if not g.os_path_exists(pathToIndex):
            g.es(f"not found: {pathToIndex}", color='red')
            return None
        index = open(pathToIndex).read()
        parse = re.findall(r'(\t*)-\s`(.+)\s<(.+)>`_', index)
        if not parse:
            g.es(f"invalid index: {pathToIndex}", color='red')
            return None
        results = []
        for result in parse:
            level = len(result[0])
            name = result[1].decode('utf-8')
            unquote = urllib.parse.unquote
            # mypy: error: "str" has no attribute "decode"; maybe "encode"?  [attr-defined]
            path = [
                g.os_path_abspath(g.os_path_join(pathToZim, unquote(result[2]).decode('utf-8')))
            ]  # type:ignore
            results.append((level, name, path))
        return results
    #@+node:ekr.20141210051628.29: *3* zic.rstToLastChild
    def rstToLastChild(self, p: Position, name: str, rst: list[str]) -> Position:
        """Import an rst file as a last child of pos node with the specified name"""
        c = self.c
        c.importCommands.importFilesCommand(
            files=rst,
            parent=p,
            treeType='@rst',
        )
        rstNode = p.getLastChild()
        rstNode.h = name
        return rstNode
    #@+node:davy.20141212140940.1: *3* zic.clean
    def clean(self, zimNode: Position, rstType: str) -> None:
        """Clean useless nodes"""
        warning = 'Warning: this node is ignored when writing this file'
        for p in zimNode.subtree_iter():
            # looking for useless bodies
            if p.hasFirstChild() and warning in p.b:
                child = p.getFirstChild()
                fmt = "@rst-no-head %s declarations"
                table = (
                    fmt % p.h.replace(' ', '_'),
                    fmt % p.h.replace(rstType, '').strip().replace(' ', '_'),
                )
                # Replace content with @rest-no-head first child (without title head) and delete it
                if child.h in table:
                    p.b = '\n'.join(child.b.split('\n')[3:])
                    child.doDelete()
                    # Replace content of empty body parent node with first child with same name
                elif p.h == child.h or (f"{rstType} {child.h}" == p.h):
                    if not child.hasFirstChild():
                        p.b = child.b
                        child.doDelete()
                    elif not child.hasNext():
                        p.b = child.b
                        child.copyTreeFromSelfTo(p)
                        child.doDelete()
                    else:
                        child.h = 'Introduction'
            elif p.hasFirstChild(
                ) and p.h.startswith("@rst-no-head") and not p.b.strip():
                child = p.getFirstChild()
                p_no_head = p.h.replace("@rst-no-head", "").strip()
                # Replace empty @rst-no-head by its same named children
                if child.h.strip() == p_no_head and not child.hasFirstChild():
                    p.h = p_no_head
                    p.b = child.b
                    child.doDelete()
            elif p.h.startswith("@rst-no-head"):
                lines = p.b.split('\n')
                p.h = lines[1]
                p.b = '\n'.join(lines[3:])
    #@+node:ekr.20141210051628.30: *3* zic.run
    def run(self) -> None:
        """Create the zim node as the last top-level node."""
        c = self.c
        # Make sure a path is given.
        if not self.pathToZim:
            g.es('Missing setting: @string path_to_zim', color='red')
            return
        root = c.rootPosition()
        while root.hasNext():
            root.moveToNext()
        zimNode = root.insertAfter()
        zimNode.h = self.zimNodeName
        # Parse the index file
        files = self.parseZimIndex()
        if files:
            # Do the import
            rstNodes: dict[str, Position] = {'0': zimNode}
            for level, name, rst in files:
                if level == self.rstLevel:
                    name = f"{self.rstType} {name}"
                rstNodes[str(level + 1)] = self.rstToLastChild(rstNodes[str(level)], name, rst)
            # Clean nodes
            g.es('Start cleaning process. Please wait...', color='blue')
            self.clean(zimNode, self.rstType)
            g.es('Done', color='blue')
            # Select zimNode
            c.selectPosition(zimNode)
            c.redraw()
    #@-others
#@+node:ekr.20200424152850.1: ** class LegacyExternalFileImporter
class LegacyExternalFileImporter:
    """
    A class to import external files written by versions of Leo earlier
    than 5.0.
    """
    # Sentinels to ignore, without the leading comment delim.
    ignore = ('@+at', '@-at', '@+leo', '@-leo', '@nonl', '@nl', '@-others')

    def __init__(self, c: Cmdr) -> None:
        self.c = c

    #@+others
    #@+node:ekr.20200424092652.1: *3* legacy.add
    def add(self, line: str, stack: list[LegacyImportNode]) -> None:
        """Add a line to the present node."""
        if stack:
            p = stack[-1]
            p.lines.append(line)
        else:
            print('orphan line: ', repr(line))
    #@+node:ekr.20200424160847.1: *3* legacy.compute_delim1
    def compute_delim1(self, path: str) -> str:
        """Return the opening comment delim for the given file."""
        junk, ext = os.path.splitext(path)
        if not ext:
            return None
        language = g.app.extension_dict.get(ext[1:])
        if not language:
            return None
        delim1, delim2, delim3 = g.set_delims_from_language(language)
        g.trace(language, delim1 or delim2)
        return delim1 or delim2
    #@+node:ekr.20200424153139.1: *3* legacy.import_file
    def import_file(self, path: str) -> None:
        """Import one legacy external file."""
        c = self.c
        root_h = g.shortFileName(path)
        delim1 = self.compute_delim1(path)
        if not delim1:
            g.es_print('unknown file extension:', color='red')
            g.es_print(path)
            return
        # Read the file into s.
        with open(path, 'r') as f:
            s = f.read()
        # Do nothing if the file is a newer external file.
        if delim1 + '@+leo-ver=4' not in s:
            g.es_print('not a legacy external file:', color='red')
            g.es_print(path)
            return
        # Compute the local ignore list for this file.
        ignore = tuple(delim1 + z for z in self.ignore)
        # Handle each line of the file.
        nodes: list[LegacyImportNode] = []  # An list of LegacyImportNode, in file order.
        stack: list[LegacyImportNode] = []  # A stack of LegacyImportNode.
        for line in g.splitLines(s):
            s = line.lstrip()
            lws = line[: len(line) - len(line.lstrip())]
            if s.startswith(delim1 + '@@'):
                self.add(lws + s[2:], stack)
            elif s.startswith(ignore):
                # Ignore these. Use comments instead of @doc bodies.
                pass
            elif (
                s.startswith(delim1 + '@+others') or
                s.startswith(delim1 + '@' + lws + '@+others')
            ):
                self.add(lws + '@others\n', stack)
            elif s.startswith(delim1 + '@<<'):
                n = len(delim1 + '@<<')
                self.add(lws + '<<' + s[n:].rstrip() + '\n', stack)
            elif s.startswith(delim1 + '@+node:'):
                # Compute the headline.
                if stack:
                    h = s[8:]
                    i = h.find(':')
                    h = h[i + 1 :] if ':' in h else h
                else:
                    h = root_h
                # Create a node and push it.
                node = LegacyImportNode(h, len(stack))
                nodes.append(node)
                stack.append(node)
            elif s.startswith(delim1 + '@-node'):
                # End the node.
                stack.pop()
            elif s.startswith(delim1 + '@'):
                print('oops:', repr(s))
            else:
                self.add(line, stack)
        if stack:
            print('Unbalanced node sentinels')
        # Generate nodes.
        last = c.lastTopLevel()
        root = last.insertAfter()
        root.h = f"imported file: {root_h}"
        position_stack: list[Position] = [root]
        for node in nodes:
            b = textwrap.dedent(''.join(node.lines))
            level = node.level
            if level == 0:
                root.h = root_h
                root.b = b
            else:
                parent = position_stack[level - 1]
                p = parent.insertAsLastChild()
                p.b = b
                p.h = node.h
                # Good for debugging.
                # p.h = f"{level} {node.h}"
                position_stack = position_stack[:level] + [p]
        c.selectPosition(root)
        root.expand()  # c.expandAllSubheads()
        c.redraw()
    #@+node:ekr.20200424154553.1: *3* legacy.import_files
    def import_files(self, paths: list[str]) -> None:
        """Import zero or more files."""
        for path in paths:
            if os.path.exists(path):
                self.import_file(path)
            else:
                g.es_print(f"not found: {path!r}")
    #@+node:ekr.20200424154416.1: *3* legacy.prompt_for_files
    def prompt_for_files(self) -> None:
        """Prompt for a list of legacy external .py files and import them."""
        c = self.c
        filetypes = [
            ("Legacy external files", "*.py"),
            ("All files", "*"),
        ]
        paths = g.app.gui.runOpenFilesDialog(c,
            title="Import Legacy External Files", filetypes=filetypes)
        c.bringToFront()
        if paths:
            g.chdir(paths[0])
            self.import_files(paths)
    #@-others
#@+node:ekr.20200424093946.1: ** class LegacyImportNode
class LegacyImportNode:

    def __init__(self, h: str, level: int) -> None:
        """Hold node data."""
        self.h = h.strip()
        self.level = level
        self.lines: list[str] = []
#@+node:ekr.20101103093942.5938: ** Commands (leoImport)
#@+node:ekr.20160504050255.1: *3* @g.command(import-free-mind-files)
@g.command('import-free-mind-files')
def import_free_mind_files(event: LeoKeyEvent) -> None:
    """Prompt for free-mind files and import them."""
    c = event.get('c')
    if c:
        FreeMindImporter(c).prompt_for_files()

#@+node:ekr.20200424154303.1: *3* @g.command(import-legacy-external-file)
@g.command('import-legacy-external-files')
def import_legacy_external_files(event: LeoKeyEvent) -> None:
    """Prompt for legacy external files and import them."""
    c = event.get('c')
    if c:
        LegacyExternalFileImporter(c).prompt_for_files()
#@+node:ekr.20160504050325.1: *3* @g.command(import-mind-map-files
@g.command('import-mind-jet-files')
def import_mind_jet_files(event: LeoKeyEvent) -> None:
    """Prompt for mind-jet files and import them."""
    c = event.get('c')
    if c:
        MindMapImporter(c).prompt_for_files()
#@+node:ekr.20161006100854.1: *3* @g.command(import-MORE-files)
@g.command('import-MORE-files')
def import_MORE_files_command(event: LeoKeyEvent) -> None:
    """Prompt for MORE files and import them."""
    c = event.get('c')
    if c:
        MORE_Importer(c).prompt_for_files()
#@+node:ekr.20161006072227.1: *3* @g.command(import-tabbed-files)
@g.command('import-tabbed-files')
def import_tabbed_files_command(event: LeoKeyEvent) -> None:
    """Prompt for tabbed files and import them."""
    c = event.get('c')
    if c:
        TabImporter(c).prompt_for_files()
#@+node:ekr.20200310095703.1: *3* @g.command(import-todo-text-files)
@g.command('import-todo-text-files')
def import_todo_text_files(event: LeoKeyEvent) -> None:
    """Prompt for free-mind files and import them."""
    c = event.get('c')
    if c:
        ToDoImporter(c).prompt_for_files()
#@+node:ekr.20141210051628.33: *3* @g.command(import-zim-folder)
@g.command('import-zim-folder')
def import_zim_command(event: LeoKeyEvent) -> None:
    """
    Import a zim folder, http://zim-wiki.org/, as the last top-level node of the outline.

    First use Zim to export your project to rst files.

    This command requires the following Leo settings::

        @int rst_level = 0
        @string rst_type
        @string zim_node_name
        @string path_to_zim
    """
    c = event.get('c')
    if c:
        ZimImportController(c).run()
#@+node:ekr.20120429125741.10057: *3* @g.command(parse-body)
@g.command('parse-body')
def parse_body_command(event: LeoKeyEvent) -> None:
    """Parse p.b as source code, creating a tree of descendant nodes."""
    c = event.get('c')
    if c and c.p:
        c.importCommands.parse_body(c.p)
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@@encoding utf-8
#@-leo
