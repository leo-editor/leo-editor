# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20031218072017.3206: * @file leoImport.py
#@@first
#@+<< imports >>
#@+node:ekr.20091224155043.6539: ** << imports >> (leoImport)
# Required so the unit test that simulates an @auto leoImport.py will work!
import leo.core.leoGlobals as g
import leo.core.leoNodes as leoNodes
import csv
try:
    import docutils
    import docutils.core
    # print('leoImport.py:',docutils)
except ImportError:
    docutils = None
    # print('leoImport.py: can not import docutils')
import glob
import importlib
import json
try:
    import lxml.html
except ImportError:
    lxml = None
import os
import re
if g.isPython3:
    import io
    StringIO = io.StringIO
else:
    import StringIO
    StringIO = StringIO.StringIO
import time
import urllib
#@-<< imports >>
#@+others
#@+node:ekr.20160503145550.1: ** class FreeMindImporter
class FreeMindImporter(object):
    '''Importer class for FreeMind (.mmap) files.'''

    def __init__(self, c):
        '''ctor for FreeMind Importer class.'''
        self.c = c
        self.count = 0
        self.d = {}

    #@+others
    #@+node:ekr.20170222084048.1: *3* freemind.add_children
    def add_children(self, parent, element):
        '''
        parent is the parent position, element is the parent element.
        Recursively add all the child elements as descendants of parent_p.
        '''
        p = parent.insertAsLastChild()
        attrib_text = element.attrib.get('text','').strip()
        tag = element.tag if g.isString(element.tag) else ''
        text = element.text or ''
        if not tag: text = text.strip()
        # g.trace('tag: %5r text: %10r attrib.text: %r' % (tag, text, attrib_text))
        p.h = attrib_text or tag or 'Comment'
        p.b = text if text.strip() else ''
        for child in element:
            self.add_children(p, child)
    #@+node:ekr.20160503125844.1: *3* freemind.create_outline
    def create_outline(self, path):
        '''Create a tree of nodes from a FreeMind file.'''
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
    def import_file(self, path):
        '''The main line of the FreeMindImporter class.'''
        c = self.c
        sfn = g.shortFileName(path)
        if g.os_path_exists(path):
            htmltree = lxml.html.parse(path)
            root = htmltree.getroot()
            body = root.findall('body')[0]
            if body is None:
                g.error('no body in: %s' % sfn)
            else:
                root_p = c.lastTopLevel().insertAfter()
                root_p.h = g.shortFileName(path)
                for child in body:
                    if child != body:
                        self.add_children(root_p, child)
                c.selectPosition(root_p)
                c.redraw()
        else:
            g.error('file not found: %s' % sfn)
    #@+node:ekr.20160503145113.1: *3* freemind.import_files
    def import_files(self, files):
        '''Import a list of FreeMind (.mmap) files.'''
        c = self.c
        if files:
            self.tab_width = c.getTabWidth(c.p)
            for fileName in files:
                g.setGlobalOpenDir(fileName)
                p = self.create_outline(fileName)
                p.contract()
                p.setDirty()
                c.setChanged(True)
            c.redraw(p)
    #@+node:ekr.20160504043823.1: *3* freemind.prompt_for_files
    def prompt_for_files(self):
        '''Prompt for a list of FreeMind (.mm.html) files and import them.'''
        c = self.c
        types = [
            ("FreeMind files", "*.mm.html"),
            ("All files", "*"),
        ]
        names = g.app.gui.runOpenFileDialog(c,
            title="Import FreeMind File",
            filetypes=types,
            defaultextension=".html",
            multiple=True)
        c.bringToFront()
        if names:
            g.chdir(names[0])
            self.import_files(names)
    #@-others
#@+node:ekr.20160504144241.1: ** class JSON_Import_Helper (To do)
class JSON_Import_Helper(object):
    '''
    A class that helps client scripts import .json files.

    Client scripts supply data describing how to create Leo outlines from
    the .json data.
    '''

    def __init__(self, c):
        '''ctor for the JSON_Import_Helper class.'''
        self.c = c
        self.vnodes_dict = {}

    #@+others
    #@+node:ekr.20160505044925.1: *3*  unused code
    if 0:
        #@+others
        #@+node:ekr.20160505045041.1: *4* unused write code
        #@+node:ekr.20160504144545.1: *5* json.put
        def put(self, s):
            '''Write line s using at.os, taking special care of newlines.'''
            at = self.c.leoAtFile
            at.os(s[: -1] if s.endswith('\n') else s)
            at.onl()
        #@+node:ekr.20160504144241.7: *5* json.vnode_dict
        def vnode_dict(self, v):
            return {
                'gnx': v.gnx,
                'h': v.h, 'b': v.b,
                # 'ua': v.u,
                'children': [z.gnx for z in v.children]
            }
        #@+node:ekr.20160504144455.1: *5* json.write
        def write(self, root, forceSentinels=False):
            """Write all the @auto-json node."""
            nodes = list(set([p.v for p in root.subtree()]))
            nodes = [self.vnode_dict(v) for v in nodes]
            d = {
                'top': self.vnode_dict(root.v),
                'nodes': nodes,
            }
            s = json.dumps(d,
                sort_keys=True,
                indent=2, # Pretty print.
                separators=(',', ': '))
            self.put(s)
            root.setVisited()
            return True
        #@+node:ekr.20160505045049.1: *4* unused read code
        #@+node:ekr.20160504144241.3: *5* json.import_files
        def import_files(self, files):
            '''Import a list of MindMap (.csv) files.'''
            c = self.c
            if files:
                self.tab_width = c.getTabWidth(c.p)
                for fileName in files:
                    g.setGlobalOpenDir(fileName)
                    p = self.create_outline(fileName)
                    p.contract()
                    p.setDirty()
                    c.setChanged(True)
                c.redraw(p)
        #@+node:ekr.20160504144241.4: *5* json.prompt_for_files
        def prompt_for_files(self):
            '''Prompt for a list of MindJet (.csv) files and import them.'''
            c = self.c
            types = [
                ("JSON files", "*.json"),
                ("All files", "*"),
            ]
            names = g.app.gui.runOpenFileDialog(c,
                title="Import MindJet File",
                filetypes=types,
                defaultextension=".csv",
                multiple=True)
            c.bringToFront()
            if names:
                g.chdir(names[0])
                self.import_files(names)
        #@-others
    #@+node:ekr.20160504144353.1: *3* json.create_nodes (generalize)
    def create_nodes(self, parent, parent_d):
        '''Create the tree of nodes rooted in parent.'''
        import pprint
        trace = False and not g.unitTesting
        d = self.gnx_dict
        if trace: g.trace(parent.h, pprint.pprint(parent_d))
        for child_gnx in parent_d.get('children'):
            d2 = d.get(child_gnx)
            if trace:
                g.trace('child', pprint.pprint(d2))
            if child_gnx in self.vnodes_dict:
                # It's a clone.
                v = self.vnodes_dict.get(child_gnx)
                n = parent.numberOfChildren()
                child = leoNodes.Position(v)
                child._linkAsNthChild(parent, n)
                # Don't create children again.
            else:
                child = parent.insertAsLastChild()
                child.h = d2.get('h') or '<**no h**>'
                child.b = d2.get('b') or g.u('')
                if d2.get('gnx'):
                    child.v.findIndex = gnx = d2.get('gnx')
                    self.vnodes_dict[gnx] = child.v
                if d2.get('ua'):
                    child.u = d2.get('ua')
                self.create_nodes(child, d2)
    #@+node:ekr.20160504144241.2: *3* json.create_outline (generalize)
    def create_outline(self, path):
        c = self.c
        junk, fileName = g.os_path_split(path)
        undoData = c.undoer.beforeInsertNode(c.p)
        # Create the top-level headline.
        p = c.lastTopLevel().insertAfter()
        fn = g.shortFileName(path).strip()
        if fn.endswith('.json'):
            fn = fn[:-5]
        p.h = fn
        self.scan(path, p)
        c.undoer.afterInsertNode(p, 'Import', undoData)
        return p
    #@+node:ekr.20160504144314.1: *3* json.scan (generalize)
    def scan(self, s, parent):
        '''Create an outline from a MindMap (.csv) file.'''
        trace = False and not g.unitTesting
        c, d, self.gnx_dict = self.c, json.loads(s), {}
        for d2 in d.get('nodes', []):
            gnx = d2.get('gnx')
            if trace: print('%25s %s' % (d2.get('gnx'), d2.get('h')))
            self.gnx_dict[gnx] = d2
        top_d = d.get('top')
        if top_d:
            # Don't set parent.h or parent.gnx or parent.v.u.
            parent.b = top_d.get('b') or ''
            self.create_nodes(parent, top_d)
            c.redraw()
        return bool(top_d)
    #@-others
#@+node:ekr.20071127175948: ** class LeoImportCommands
class LeoImportCommands(object):
    '''
    A class implementing all of Leo's import/export code. This class
    uses **importers** in the leo/plugins/importers folder.

    For more information, see leo/plugins/importers/howto.txt.
    '''
    #@+others
    #@+node:ekr.20031218072017.3207: *3* ic.__init__ & helpers
    def __init__(self, c):
        '''ctor for LeoImportCommands class.'''
        self.c = c
        self.atAutoDict = {} # Keys are @auto names, values are scanner classes.
        self.classDispatchDict = {}
        self.default_directory = None # For @path logic.
        self.encoding = 'utf-8'
        self.errors = 0
        self.fileName = None # The original file name, say x.cpp
        self.fileType = None # ".py", ".c", etc.
        self.methodName = None # x, as in < < x methods > > =
        self.output_newline = g.getOutputNewline(c=c) # Value of @bool output_newline
        self.rootLine = "" # Empty or @root + self.fileName
        self.tab_width = c.tab_width
        self.trace = c.config.getBool('trace_import')
        self.treeType = "@file" # None or "@file"
        self.webType = "@noweb" # "cweb" or "noweb"
        self.web_st = [] # noweb symbol table.
        self.createImporterData()
            # update g.app.atAutoNames and self.classDispatchDict
    #@+node:ekr.20140724064952.18037: *4* ic.createImporterData & helper
    def createImporterData(self):
        '''Create the data structures describing importer plugins.'''
        trace = False and not g.unitTesting
        trace_exception = False
        self.classDispatchDict = {}
        self.atAutoDict = {}
        # Allow plugins to be defined in ~/.leo/plugins.
        plugins1 = g.os_path_finalize_join(g.app.homeDir, '.leo', 'plugins')
        plugins2 = g.os_path_finalize_join(g.app.loadDir, '..', 'plugins')
        for kind, plugins in (('home', plugins1), ('leo', plugins2)):
            pattern = g.os_path_finalize_join(
                g.app.loadDir, '..', 'plugins', 'importers', '*.py')
            for fn in glob.glob(pattern):
                sfn = g.shortFileName(fn)
                if sfn != '__init__.py':
                    try:
                        module_name = sfn[: -3]
                        # Important: use importlib to give imported modules
                        # their fully qualified names.
                        m = importlib.import_module(
                            'leo.plugins.importers.%s' % module_name)
                        self.parse_importer_dict(sfn, m)
                    except Exception:
                        if trace and trace_exception:
                            g.es_exception()
                        g.warning('can not import leo.plugins.importers.%s' % (
                            module_name))
    #@+node:ekr.20140723140445.18076: *5* ic.parse_importer_dict
    def parse_importer_dict(self, sfn, m):
        '''
        Set entries in ic.classDispatchDict, ic.atAutoDict and
        g.app.atAutoNames using entries in m.importer_dict.
        '''
        trace = False and not g.unitTesting
        ic = self
        importer_d = getattr(m, 'importer_dict', None)
        if importer_d:
            at_auto = importer_d.get('@auto', [])
            scanner_class = importer_d.get('class', None)
            scanner_name = scanner_class.__name__
            extensions = importer_d.get('extensions', [])
            if trace:
                g.trace('===== %s: %s' % (sfn, scanner_name))
                if extensions: g.trace(', '.join(extensions))
            if at_auto:
                # Make entries for each @auto type.
                d = ic.atAutoDict
                for s in at_auto:
                    aClass = d.get(s)
                    if aClass and aClass != scanner_class:
                        g.trace('duplicate %5s class: %s in %s' % (
                            s, aClass.__name__, m.__file__))
                    else:
                        d[s] = scanner_class
                        ic.atAutoDict[s] = scanner_class
                        g.app.atAutoNames.add(s)
                        if trace: g.trace(s)
            if extensions:
                # Make entries for each extension.
                d = ic.classDispatchDict
                for ext in extensions:
                    aClass = d.get(ext)
                    if aClass and aClass != scanner_class:
                        g.trace('duplicate %s class: %s in %s' % (
                           ext, aClass.__name__, m.__file__))
                    else:
                        d[ext] = scanner_class
        elif sfn not in (
            # These are base classes, not real plugins.
            'basescanner.py',
            'linescanner.py',
        ):
            g.warning('leo/plugins/importers/%s has no importer_dict' % sfn)
    #@+node:ekr.20031218072017.3289: *3* ic.Export
    #@+node:ekr.20031218072017.3290: *4* ic.convertCodePartToWeb & helpers
    def convertCodePartToWeb(self, s, i, p, result):
        '''
        # Headlines not containing a section reference are ignored in noweb
        and generate index index in cweb.
        '''
        # g.trace(g.get_line(s,i))
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
            i = g.skip_line(s, i) # 4/28/02
        else:
            ic.appendHeadRef(p, file_name, head_ref, result)
        i, result = ic.copyPart(s, i, result)
        return i, result.strip() + nl
    #@+at %defs a b c
    #@+node:ekr.20140630085837.16720: *5* ic.appendHeadRef
    def appendHeadRef(self, p, file_name, head_ref, result):
        ic = self
        nl = ic.output_newline
        if ic.webType == "cweb":
            if head_ref:
                escaped_head_ref = head_ref.replace("@", "@@")
                result += "@<" + escaped_head_ref + "@>=" + nl
            else:
                result += "@^" + p.h.strip() + "@>" + nl
                    # Convert the headline to an index entry.
                result += "@c" + nl
                    # @c denotes a new section.
        else:
            if head_ref:
                pass
            elif p == ic.c.p:
                head_ref = file_name or "*"
            else:
                head_ref = "@others"
            result += ("<<" + head_ref +
                ">>" + "=" + nl)
                # Must be on separate lines.
    #@+node:ekr.20140630085837.16719: *5* ic.appendRefToFileName
    def appendRefToFileName(self, file_name, result):
        ic = self
        nl = ic.output_newline
        if ic.webType == "cweb":
            if not file_name:
                result += "@<root@>=" + nl
            else:
                result += "@(" + file_name + "@>" + nl
                    # @(...@> denotes a file.
        else:
            if not file_name:
                file_name = "*"
            result += ("<<" + file_name +
                ">>" + "=" + nl)
                # Must be on separate lines.
    #@+node:ekr.20140630085837.16721: *5* ic.getHeadRef
    def getHeadRef(self, p):
        '''
        Look for either noweb or cweb brackets.
        Return everything between those brackets.
        '''
        h = p.h.strip()
        if g.match(h, 0, "<<"):
            i = h.find(">>", 2)
        elif g.match(h, 0, "<@"):
            i = h.find("@>", 2)
        else:
            return h
        return h[2: i].strip()
    #@+node:ekr.20031218072017.3292: *5* ic.getFileName
    def getFileName(self, p):
        '''Return the file name from an @file or @root node.'''
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
            file_name = line[j: k].strip()
        else:
            file_name = ''
        return file_name
    #@+node:ekr.20031218072017.3296: *4* ic.convertDocPartToWeb (handle @ %def)
    def convertDocPartToWeb(self, s, i, result):
        nl = self.output_newline
        # g.trace(g.get_line(s,i))
        if g.match_word(s, i, "@doc"):
            i = g.skip_line(s, i)
        elif g.match(s, i, "@ ") or g.match(s, i, "@\t") or g.match(s, i, "@*"):
            i += 2
        elif g.match(s, i, "@\n"):
            i += 1
        i = g.skip_ws_and_nl(s, i)
        i, result2 = self.copyPart(s, i, "")
        if len(result2) > 0:
            # Break lines after periods.
            result2 = result2.replace(".  ", "." + nl)
            result2 = result2.replace(". ", "." + nl)
            result += nl + "@" + nl + result2.strip() + nl + nl
        else:
            # All nodes should start with '@', even if the doc part is empty.
            result += nl + "@ " if self.webType == "cweb" else nl + "@" + nl
        return i, result
    #@+node:ekr.20031218072017.3297: *4* ic.convertVnodeToWeb
    def convertVnodeToWeb(self, v):
        '''
        This code converts a VNode to noweb text as follows:

        Convert @doc to @
        Convert @root or @code to < < name > >=, assuming the headline contains < < name > >
        Ignore other directives
        Format doc parts so they fit in pagewidth columns.
        Output code parts as is.
        '''
        c = self.c
        if not v or not c: return ""
        startInCode = not c.config.at_root_bodies_start_in_doc_mode
        nl = self.output_newline
        docstart = nl + "@ " if self.webType == "cweb" else nl + "@" + nl
        s = v.b
        lb = "@<" if self.webType == "cweb" else "<<"
        i, result, docSeen = 0, "", False
        while i < len(s):
            progress = i
            # g.trace(g.get_line(s,i))
            i = g.skip_ws_and_nl(s, i)
            if self.isDocStart(s, i) or g.match_word(s, i, "@doc"):
                i, result = self.convertDocPartToWeb(s, i, result)
                docSeen = True
            elif(
                g.match_word(s, i, "@code") or
                g.match_word(s, i, "@root") or
                g.match_word(s, i, "@c") or
                g.match(s, i, lb)
            ):
                if not docSeen:
                    docSeen = True
                    result += docstart
                i, result = self.convertCodePartToWeb(s, i, v, result)
            elif self.treeType == "@file" or startInCode:
                if not docSeen:
                    docSeen = True
                    result += docstart
                i, result = self.convertCodePartToWeb(s, i, v, result)
            else:
                i, result = self.convertDocPartToWeb(s, i, result)
                docSeen = True
            assert(progress < i)
        result = result.strip()
        if len(result) > 0:
            result += nl
        return result
    #@+node:ekr.20031218072017.3299: *4* ic.copyPart
    # Copies characters to result until the end of the present section is seen.

    def copyPart(self, s, i, result):
        # g.trace(g.get_line(s,i))
        lb = "@<" if self.webType == "cweb" else "<<"
        rb = "@>" if self.webType == "cweb" else ">>"
        theType = self.webType
        while i < len(s):
            progress = j = i # We should be at the start of a line here.
            i = g.skip_nl(s, i); i = g.skip_ws(s, i)
            if self.isDocStart(s, i):
                return i, result
            if (g.match_word(s, i, "@doc") or
                g.match_word(s, i, "@c") or
                g.match_word(s, i, "@root") or
                g.match_word(s, i, "@code") # 2/25/03
            ): 
                return i, result
            elif(g.match(s, i, "<<") and # must be on separate lines.
                g.find_on_line(s, i, ">>=") > -1
            ):
                return i, result
            else:
                # Copy the entire line, escaping '@' and
                # Converting @others to < < @ others > >
                i = g.skip_line(s, j); line = s[j: i]
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
            assert(progress < i)
        return i, result.rstrip()
    #@+node:ekr.20031218072017.1462: *4* ic.exportHeadlines
    def exportHeadlines(self, fileName):
        c = self.c; p = c.p
        nl = g.u(self.output_newline)
        if not p: return
        self.setEncoding()
        firstLevel = p.level()
        try:
            theFile = open(fileName, 'w')
        except IOError:
            g.warning("can not open", fileName)
            c.testManager.fail()
            return
        for p in p.self_and_subtree():
            head = p.moreHead(firstLevel, useVerticalBar=True)
            s = head + nl
            if not g.isPython3: # 2010/08/27
                s = g.toEncodedString(s, encoding=self.encoding, reportErrors=True)
            theFile.write(s)
        theFile.close()
    #@+node:ekr.20031218072017.1147: *4* ic.flattenOutline
    def flattenOutline(self, fileName):
        '''
        A helper for the flatten-outline command.

        Export the selected outline to an external file.
        The outline is represented in MORE format.
        '''
        c = self.c
        nl = g.u(self.output_newline)
        p = c.p
        if not p:
            return
        self.setEncoding()
        firstLevel = p.level()
        try:
            theFile = open(fileName, 'wb')
                # Fix crasher: open in 'wb' mode.
        except IOError:
            g.warning("can not open", fileName)
            c.testManager.fail()
            return
        for p in p.self_and_subtree():
            s = p.moreHead(firstLevel) + nl
            s = g.toEncodedString(s, encoding=self.encoding, reportErrors=True)
            theFile.write(s)
            s = p.moreBody() + nl # Inserts escapes.
            if s.strip():
                s = g.toEncodedString(s, self.encoding, reportErrors=True)
                theFile.write(s)
        theFile.close()
    #@+node:ekr.20031218072017.1148: *4* ic.outlineToWeb
    def outlineToWeb(self, fileName, webType):
        c = self.c; nl = self.output_newline
        current = c.p
        if not current: return
        self.setEncoding()
        self.webType = webType
        try:
            theFile = open(fileName, 'w')
        except IOError:
            g.warning("can not open", fileName)
            c.testManager.fail()
            return
        self.treeType = "@file"
        # Set self.treeType to @root if p or an ancestor is an @root node.
        for p in current.parents():
            flag, junk = g.is_special(p.b, 0, "@root")
            if flag:
                self.treeType = "@root"
                break
        for p in current.self_and_subtree():
            s = self.convertVnodeToWeb(p)
            if len(s) > 0:
                if not g.isPython3: # 2010/08/27
                    s = g.toEncodedString(s, self.encoding, reportErrors=True)
                theFile.write(s)
                if s[-1] != '\n': theFile.write(nl)
        theFile.close()
    #@+node:ekr.20031218072017.3300: *4* ic.removeSentinelsCommand
    def removeSentinelsCommand(self, paths, toString=False):
        c = self.c
        self.setEncoding()
        for fileName in paths:
            g.setGlobalOpenDir(fileName)
            path, self.fileName = g.os_path_split(fileName)
            s, e = g.readFileIntoString(fileName, self.encoding)
            if s is None: return
            if e: self.encoding = e
            #@+<< set delims from the header line >>
            #@+node:ekr.20031218072017.3302: *5* << set delims from the header line >>
            # Skip any non @+leo lines.
            i = 0
            while i < len(s) and g.find_on_line(s, i, "@+leo") == -1:
                i = g.skip_line(s, i)
            # Get the comment delims from the @+leo sentinel line.
            at = self.c.atFileCommands
            j = g.skip_line(s, i); line = s[i: j]
            valid, junk, start_delim, end_delim, junk = at.parseLeoSentinel(line)
            if not valid:
                if not toString: g.es("invalid @+leo sentinel in", fileName)
                return
            if end_delim:
                line_delim = None
            else:
                line_delim, start_delim = start_delim, None
            #@-<< set delims from the header line >>
            # g.trace("line: '%s', start: '%s', end: '%s'" % (line_delim,start_delim,end_delim))
            s = self.removeSentinelLines(s, line_delim, start_delim, end_delim)
            ext = c.config.remove_sentinels_extension
            if not ext:
                ext = ".txt"
            if ext[0] == '.':
                newFileName = c.os_path_finalize_join(path, fileName + ext)
            else:
                head, ext2 = g.os_path_splitext(fileName)
                newFileName = c.os_path_finalize_join(path, head + ext + ext2)
            if toString:
                return s
            else:
                #@+<< Write s into newFileName >>
                #@+node:ekr.20031218072017.1149: *5* << Write s into newFileName >> (remove-sentinels) (changed)
                # Remove sentinels command.
                try:
                    theFile = open(newFileName, 'w')
                    if not g.isPython3: # 2010/08/27
                        s = g.toEncodedString(s, self.encoding, reportErrors=True)
                    theFile.write(s)
                    theFile.close()
                    if not g.unitTesting:
                        g.es("created:", newFileName)
                except Exception:
                    g.es("exception creating:", newFileName)
                    g.es_print_exception()
                #@-<< Write s into newFileName >>
                return None
    #@+node:ekr.20031218072017.3303: *4* ic.removeSentinelLines
    # This does not handle @nonl properly, but that no longer matters.

    def removeSentinelLines(self, s, line_delim, start_delim, unused_end_delim):
        '''Properly remove all sentinle lines in s.'''
        delim = (line_delim or start_delim or '') + '@'
        verbatim = delim + 'verbatim'; verbatimFlag = False
        result = []; lines = g.splitLines(s)
        for line in lines:
            i = g.skip_ws(line, 0)
            if not verbatimFlag and g.match(line, i, delim):
                if g.match(line, i, verbatim):
                    # Force the next line to be in the result.
                    verbatimFlag = True
            else:
                result.append(line)
                verbatimFlag = False
        result = ''.join(result)
        return result
    #@+node:ekr.20031218072017.1464: *4* ic.weave
    def weave(self, filename):
        c = self.c; nl = self.output_newline
        p = c.p
        if not p: return
        self.setEncoding()
        #@+<< open filename to f, or return >>
        #@+node:ekr.20031218072017.1150: *5* << open filename to f, or return >> (weave)
        try:
            if g.isPython3:
                f = open(filename, 'w', encoding=self.encoding)
            else:
                f = open(filename, 'w')
        except Exception:
            g.es("exception opening:", filename)
            g.es_print_exception()
            return
        #@-<< open filename to f, or return >>
        for p in p.self_and_subtree():
            s = p.b
            s2 = s.strip()
            if s2 and len(s2) > 0:
                f.write("-" * 60); f.write(nl)
                #@+<< write the context of p to f >>
                #@+node:ekr.20031218072017.1465: *5* << write the context of p to f >> (weave)
                # write the headlines of p, p's parent and p's grandparent.
                context = []; p2 = p.copy(); i = 0
                while i < 3:
                    i += 1
                    if not p2: break
                    context.append(p2.h)
                    p2.moveToParent()
                context.reverse()
                indent = ""
                for line in context:
                    f.write(indent)
                    indent += '\t'
                    if not g.isPython3: # 2010/08/27.
                        line = g.toEncodedString(line, self.encoding, reportErrors=True)
                    f.write(line)
                    f.write(nl)
                #@-<< write the context of p to f >>
                f.write("-" * 60); f.write(nl)
                if not g.isPython3:
                    s = g.toEncodedString(s, self.encoding, reportErrors=True)
                f.write(s.rstrip() + nl)
        f.flush()
        f.close()
    #@+node:ekr.20031218072017.3209: *3* ic.Import
    #@+node:ekr.20031218072017.3210: *4* ic.createOutline & helpers
    def createOutline(self, fileName, parent,
        atAuto=False, atShadow=False, s=None, ext=None
    ):
        '''Create an outline by importing a file or string.'''
        trace = False and not g.unitTesting
        c = self.c
        fileName = self.get_import_filename(fileName, parent)
        if g.is_binary_external_file(fileName):
            # Fix bug 1185409 importing binary files puts binary content in body editor.
            # Create an @url node.
            if parent:
                p = parent.insertAsLastChild()
            else:
                p = c.lastTopLevel().insertAfter()
            p.h = '@url file://%s' % fileName
            if trace: g.trace('binary file:', fileName)
            return
        # Init ivars.
        self.setEncoding(p=parent, atAuto=atAuto)
        atAuto, atAutoKind, ext, s = self.init_import(atAuto, atShadow, ext, fileName, s)
        if s is None:
            if trace: g.trace('read failed', fileName)
            return
        if trace and not s:
            g.trace('empty file: but calling importer', fileName)
        # Create the top-level headline.
        p = self.create_top_node(atAuto, atAutoKind, fileName, parent)
        # Get the scanning function.
        func = self.dispatch(ext, p)
        if trace: g.trace(ext, p.h, func)
        # Call the scanning function.
        if g.unitTesting:
            assert func or ext in ('.w', '.xxx'), (ext, p.h)
        if func and not c.config.getBool('suppress_import_parsing', default=False):
            s = g.toUnicode(s, encoding=self.encoding)
            s = s.replace('\r', '')
            func(atAuto=atAuto, parent=p, s=s)
        else:
            # Just copy the file to the parent node.
            s = g.toUnicode(s, encoding=self.encoding)
            s = s.replace('\r', '')
            self.scanUnknownFileType(s, p, ext, atAuto=atAuto)
        if atAuto:
            # Fix bug 488894: unsettling dialog when saving Leo file
            # Fix bug 889175: Remember the full fileName.
            c.atFileCommands.rememberReadPath(fileName, p)
        p.contract()
        w = c.frame.body.wrapper
        w.setInsertPoint(0)
        w.seeInsertPoint()
        return p
    #@+node:ekr.20140724175458.18053: *5* ic.create_top_node
    def create_top_node(self, atAuto, atAutoKind, fileName, parent):
        '''Create the top node.'''
        c, u = self.c, self.c.undoer
        if atAuto:
            if atAutoKind:
                # We have found a match between ext and an @auto importer.
                undoData = u.beforeInsertNode(parent)
                if parent:
                    p = parent.insertAsLastChild()
                else:
                    p = c.lastTopLevel().insertAfter()
                p.initHeadString(atAutoKind + ' ' + fileName)
                u.afterInsertNode(p, 'Import', undoData)
            else:
                p = parent.copy()
                p.setBodyString('')
        else:
            undoData = u.beforeInsertNode(parent)
            if parent:
                p = parent.insertAsLastChild()
            else:
                p = c.lastTopLevel().insertAfter()
            if self.treeType in ('@clean', '@file', '@nosent'):
                p.initHeadString('%s %s' % (self.treeType, fileName))
            elif self.treeType is None:
                # By convention, we use the short file name.
                p.initHeadString(g.shortFileName(fileName))
            else:
                p.initHeadString(fileName)
            u.afterInsertNode(p, 'Import', undoData)
        return p
    #@+node:ekr.20140724064952.18038: *5* ic.dispatch & helpers
    def dispatch(self, ext, p):
        '''Return the correct scanner function for p, an @auto node.'''
        # Match the @auto type first, then the file extension.
        return self.scanner_for_at_auto(p) or self.scanner_for_ext(ext)
    #@+node:ekr.20140727180847.17985: *6* ic.scanner_for_at_auto
    def scanner_for_at_auto(self, p):
        '''A factory returning a scanner function for p, an @auto node.'''
        trace = False and not g.unitTesting
        d = self.atAutoDict
        if trace: g.trace('\n'.join(sorted(d.keys())))
        for key in d.keys():
            # pylint: disable=cell-var-from-loop
            aClass = d.get(key)
            # if trace:g.trace(bool(aClass),p.h.startswith(key),g.match_word(p.h,0,key),p.h,key)
            if aClass and g.match_word(p.h, 0, key):
                if trace: g.trace('found', aClass.__name__)

                def scanner_for_at_auto_cb(atAuto, parent, s, prepass=False):
                    try:
                        scanner = aClass(importCommands=self, atAuto=atAuto)
                        return scanner.run(s, parent, prepass=prepass)
                    except Exception:
                        g.es_print('Exception running', aClass.__name__)
                        g.es_exception()
                        return None

                if trace: g.trace('found', p.h)
                return scanner_for_at_auto_cb
        if trace: g.trace('not found', p.h, sorted(d.keys()))
        return None
    #@+node:ekr.20140130172810.15471: *6* ic.scanner_for_ext
    def scanner_for_ext(self, ext):
        '''A factory returning a scanner function for the given file extension.'''
        trace = False and not g.unitTesting
        aClass = self.classDispatchDict.get(ext)
        if trace: g.trace(ext, aClass.__name__)
        if aClass:

            def scanner_for_ext_cb(atAuto, parent, s, prepass=False):
                try:
                    scanner = aClass(importCommands=self, atAuto=atAuto)
                    return scanner.run(s, parent, prepass=prepass)
                except Exception:
                    g.es_print('Exception running', aClass.__name__)
                    g.es_exception()
                    return None

            return scanner_for_ext_cb
        else:
            return None
    #@+node:ekr.20140724073946.18050: *5* ic.get_import_filename
    def get_import_filename(self, fileName, parent):
        '''Return the absolute path of the file and set .default_directory.'''
        c = self.c
        self.default_directory = g.setDefaultDirectory(c, parent, importing=False)
        fileName = c.os_path_finalize_join(self.default_directory, fileName)
        fileName = fileName.replace('\\', '/') # 2011/11/25
        return fileName
    #@+node:ekr.20140724175458.18052: *5* ic.init_import
    def init_import(self, atAuto, atShadow, ext, fileName, s):
        '''Init ivars & vars for imports.'''
        trace = False and not g.unitTesting
        junk, self.fileName = g.os_path_split(fileName)
        self.methodName, self.fileType = g.os_path_splitext(self.fileName)
        if not ext: ext = self.fileType
        ext = ext.lower()
        kind = None
        if not s:
            if atShadow: kind = '@shadow '
            elif atAuto: kind = '@auto '
            else: kind = ''
            s, e = g.readFileIntoString(fileName, encoding=self.encoding, kind=kind)
                # Kind is used only for messages.
            if s is None:
                return None, None, None, None
            if e: self.encoding = e
        if self.treeType == '@root': # 2010/09/29.
            self.rootLine = "@root-code " + self.fileName + '\n'
        else:
            self.rootLine = ''
        if trace: g.trace('1', atAuto, self.treeType, fileName)
        atAutoKind = None
        if not atAuto and kind != '@auto':
            # Not yet an @auto node.
            # Set atAutoKind if there is an @auto importer for ext.
            aClass = self.classDispatchDict.get(ext)
            if aClass:
                # Set the atAuto flag if any @auto importers match the extension.
                d2 = self.atAutoDict
                for z in d2:
                    if d2.get(z) == aClass:
                        # g.trace('found',z,'for',ext,aClass.__name__)
                        atAuto = True
                        atAutoKind = z
                        break
        if trace: g.trace('2', atAuto, atAutoKind, ext)
        return atAuto, atAutoKind, ext, s
    #@+node:ekr.20070806111212: *4* ic.readAtAutoNodes
    def readAtAutoNodes(self):
        c = self.c
        p = c.p; after = p.nodeAfterTree()
        found = False
        while p and p != after:
            if p.isAtAutoNode():
                if p.isAtIgnoreNode():
                    g.warning('ignoring', p.h)
                    p.moveToThreadNext()
                else:
                    # self.readOneAtAutoNode(p)
                    fileName = p.atAutoNodeName()
                    c.atFileCommands.readOneAtAutoNode(fileName, p)
                    found = True
                    p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
        if not g.unitTesting:
            message = 'finished' if found else 'no @auto nodes in the selected tree'
            g.blue(message)
        c.redraw()
    #@+node:ekr.20031218072017.1810: *4* ic.importDerivedFiles
    def importDerivedFiles(self, parent=None, paths=None, command='Import'):
        '''
        Import one or more external files.
        This is not a command.  It must *not* have an event arg.
        command is None when importing from the command line.
        '''
        at, c, u = self.c.atFileCommands, self.c, self.c.undoer
        current = c.p or c.rootPosition()
        self.tab_width = c.getTabWidth(current)
        if not paths:
            return None
        # Initial open from command line is not undoable.
        if command: u.beforeChangeGroup(current, command)
        for fileName in paths:
            fileName = fileName.replace('\\', '/') # 2011/10/09.
            g.setGlobalOpenDir(fileName)
            isThin = at.scanHeaderForThin(fileName)
            # g.trace('isThin',isThin,fileName)
            if command: undoData = u.beforeInsertNode(parent)
            p = parent.insertAfter()
            if isThin:
                # Create @file node, not a deprecated @thin node.
                p.initHeadString("@file " + fileName)
                at.read(p, force=True)
            else:
                p.initHeadString("Imported @file " + fileName)
                at.read(p, importFileName=fileName, force=True)
            p.contract()
            p.setDirty() # 2011/10/09: tell why the file is dirty!
            if command: u.afterInsertNode(p, command, undoData)
        current.expand()
        c.setChanged(True)
        if command: u.afterChangeGroup(p, command)
        c.redraw(current)
        return p
    #@+node:ekr.20031218072017.3212: *4* ic.importFilesCommand & helper
    def importFilesCommand(self,
        files=None,
        treeType=None,
        redrawFlag=True,
        shortFn=False,
    ):
        # Not a command.  It must *not* have an event arg.
        c, current = self.c, self.c.p
        if not c or not current or not files:
            return
        self.tab_width = c.getTabWidth(current)
        self.treeType = treeType
        if len(files) == 2:
            current = self.createImportParent(current, files)
        parent = current if len(files) > 1 else None
        for fn in files:
            g.setGlobalOpenDir(fn)
            p = self.createOutline(fn, parent=parent)
            if p: # createOutline may fail.
                if not g.unitTesting:
                    g.blue("imported", g.shortFileName(fn) if shortFn else fn)
                p.contract()
                p.setDirty()
                c.setChanged(True)
        c.validateOutline()
        current.expand()
        if redrawFlag:
            c.redraw(current)
    #@+node:ekr.20031218072017.3213: *5* createImportParent (importCommands)
    def createImportParent(self, current, files):
        '''Create a parent node for nodes with a common prefix: x.h & x.cpp.'''
        name0, name1 = files
        prefix0, junk = g.os_path_splitext(name0)
        prefix1, junk = g.os_path_splitext(name1)
        if prefix0 and prefix0 == prefix1:
            current = current.insertAsLastChild()
            name, junk = g.os_path_splitext(prefix1)
            name = name.replace('\\', '/') # 2011/11/25
            current.initHeadString(name)
        return current
    #@+node:ekr.20031218072017.3220: *4* ic.importFlattenedOutline & helpers
    def importFlattenedOutline(self, files): # Not a command, so no event arg.
        c = self.c; u = c.undoer
        if not c.p: return
        if not files: return
        self.setEncoding()
        fileName = files[0] # files contains at most one file.
        g.setGlobalOpenDir(fileName)
        s, e = g.readFileIntoString(fileName)
        if s is None or not s.strip():
            return ''
        s = s.replace('\r', '') # Fixes bug 626101.
        array = s.split("\n")
        # Convert the string to an outline and insert it after the current node.
        undoData = u.beforeInsertNode(c.p)
        # MORE files are more restrictive than tab-delimited outlines, so try them first.
        p = None
        c.endEditing()
        importer = MORE_Importer(c)
        if importer.check(s):
            p = importer.import_lines(array, c.p)
        if not p:
            # Try to import a tab-delimited outline.
            importer = TabImporter(c)
            if importer.check(s, warn=False):
                p = importer.scan(s, fn=fileName, root=c.p)
        if p:
            c.validateOutline()
            p.setDirty()
            c.setChanged(True)
            u.afterInsertNode(p, 'Import', undoData)
            c.redraw(p)
        # elif not g.unitTesting:
            # g.es_print("not a valid MORE file", fileName)
    #@+node:ekr.20160503125237.1: *4* ic.importFreeMind
    def importFreeMind(self, files):
        '''
        Import a list of .mm.html files exported from FreeMind:
        http://freemind.sourceforge.net/wiki/index.php/Main_Page
        '''
        if lxml:
            FreeMindImporter(self.c).import_files(files)
        else:
            g.es_print('can not import lxml.html')
    #@+node:ekr.20160503125219.1: *4* ic.importMindMap
    def importMindMap(self, files):
        '''
        Import a list of .csv files exported from MindJet:
        https://www.mindjet.com/
        '''
        MindMapImporter(self.c).import_files(files)
    #@+node:ekr.20031218072017.3224: *4* ic.importWebCommand & helpers
    def importWebCommand(self, files, webType):
        c = self.c; current = c.p
        if current is None: return
        if not files: return
        self.tab_width = c.getTabWidth(current) # New in 4.3.
        self.webType = webType
        for fileName in files:
            g.setGlobalOpenDir(fileName)
            p = self.createOutlineFromWeb(fileName, current)
            p.contract()
            p.setDirty()
            c.setChanged(True)
        c.redraw(current)
    #@+node:ekr.20031218072017.3225: *5* createOutlineFromWeb
    def createOutlineFromWeb(self, path, parent):
        c = self.c; u = c.undoer
        junk, fileName = g.os_path_split(path)
        undoData = u.beforeInsertNode(parent)
        # Create the top-level headline.
        p = parent.insertAsLastChild()
        p.initHeadString(fileName)
        if self.webType == "cweb":
            self.setBodyString(p, "@ignore\n" + self.rootLine + "@language cweb")
        # Scan the file, creating one section for each function definition.
        self.scanWebFile(path, p)
        u.afterInsertNode(p, 'Import', undoData)
        return p
    #@+node:ekr.20031218072017.3227: *5* findFunctionDef
    def findFunctionDef(self, s, i):
        # Look at the next non-blank line for a function name.
        i = g.skip_ws_and_nl(s, i)
        k = g.skip_line(s, i)
        name = None
        while i < k:
            if g.is_c_id(s[i]):
                j = i; i = g.skip_c_id(s, i); name = s[j: i]
            elif s[i] == '(':
                if name: return name
                else: break
            else: i += 1
        return None
    #@+node:ekr.20031218072017.3228: *5* scanBodyForHeadline
    #@+at This method returns the proper headline text.
    # 
    # 1. If s contains a section def, return the section ref.
    # 2. cweb only: if s contains @c, return the function name following the @c.
    # 3. cweb only: if s contains @d name, returns @d name.
    # 4. Otherwise, returns "@"
    #@@c

    def scanBodyForHeadline(self, s):
        if self.webType == "cweb":
            #@+<< scan cweb body for headline >>
            #@+node:ekr.20031218072017.3229: *6* << scan cweb body for headline >>
            i = 0
            while i < len(s):
                i = g.skip_ws_and_nl(s, i)
                # line = g.get_line(s,i) ; g.trace(line)
                # Allow constructs such as @ @c, or @ @<.
                if self.isDocStart(s, i):
                    i += 2; i = g.skip_ws(s, i)
                if g.match(s, i, "@d") or g.match(s, i, "@f"):
                    # Look for a macro name.
                    directive = s[i: i + 2]
                    i = g.skip_ws(s, i + 2) # skip the @d or @f
                    if i < len(s) and g.is_c_id(s[i]):
                        j = i; g.skip_c_id(s, i); return s[j: i]
                    else: return directive
                elif g.match(s, i, "@c") or g.match(s, i, "@p"):
                    # Look for a function def.
                    name = self.findFunctionDef(s, i + 2)
                    return name if name else "outer function"
                elif g.match(s, i, "@<"):
                    # Look for a section def.
                    # A small bug: the section def must end on this line.
                    j = i; k = g.find_on_line(s, i, "@>")
                    if k > -1 and (g.match(s, k + 2, "+=") or g.match(s, k + 2, "=")):
                        return s[j: k + 2] # return the section ref.
                i = g.skip_line(s, i)
            #@-<< scan cweb body for headline >>
        else:
            #@+<< scan noweb body for headline >>
            #@+node:ekr.20031218072017.3230: *6* << scan noweb body for headline >>
            i = 0
            while i < len(s):
                i = g.skip_ws_and_nl(s, i)
                # line = g.get_line(s,i) ; g.trace(line)
                if g.match(s, i, "<<"):
                    k = g.find_on_line(s, i, ">>=")
                    if k > -1:
                        ref = s[i: k + 2]
                        name = s[i + 2: k].strip()
                        if name != "@others":
                            return ref
                else:
                    name = self.findFunctionDef(s, i)
                    if name:
                        return name
                i = g.skip_line(s, i)
            #@-<< scan noweb body for headline >>
        return "@" # default.
    #@+node:ekr.20031218072017.3231: *5* scanWebFile (handles limbo)
    def scanWebFile(self, fileName, parent):
        theType = self.webType
        lb = "@<" if theType == "cweb" else "<<"
        rb = "@>" if theType == "cweb" else ">>"
        s, e = g.readFileIntoString(fileName)
        if s is None: return
        #@+<< Create a symbol table of all section names >>
        #@+node:ekr.20031218072017.3232: *6* << Create a symbol table of all section names >>
        i = 0; self.web_st = []
        while i < len(s):
            progress = i
            i = g.skip_ws_and_nl(s, i)
            # line = g.get_line(s,i) ; g.trace(line)
            if self.isDocStart(s, i):
                if theType == "cweb": i += 2
                else: i = g.skip_line(s, i)
            elif theType == "cweb" and g.match(s, i, "@@"):
                i += 2
            elif g.match(s, i, lb):
                i += 2; j = i; k = g.find_on_line(s, j, rb)
                if k > -1: self.cstEnter(s[j: k])
            else: i += 1
            assert(i > progress)
        # g.trace(self.cstDump())
        #@-<< Create a symbol table of all section names >>
        #@+<< Create nodes for limbo text and the root section >>
        #@+node:ekr.20031218072017.3233: *6* << Create nodes for limbo text and the root section >>
        i = 0
        while i < len(s):
            progress = i
            i = g.skip_ws_and_nl(s, i)
            if self.isModuleStart(s, i) or g.match(s, i, lb):
                break
            else: i = g.skip_line(s, i)
            assert(i > progress)
        j = g.skip_ws(s, 0)
        if j < i:
            self.createHeadline(parent, "@ " + s[j: i], "Limbo")
        j = i
        if g.match(s, i, lb):
            while i < len(s):
                progress = i
                i = g.skip_ws_and_nl(s, i)
                if self.isModuleStart(s, i):
                    break
                else: i = g.skip_line(s, i)
                assert(i > progress)
            self.createHeadline(parent, s[j: i], g.angleBrackets(" @ "))
        # g.trace(g.get_line(s,i))
        #@-<< Create nodes for limbo text and the root section >>
        while i < len(s):
            outer_progress = i
            #@+<< Create a node for the next module >>
            #@+node:ekr.20031218072017.3234: *6* << Create a node for the next module >>
            if theType == "cweb":
                assert(self.isModuleStart(s, i))
                start = i
                if self.isDocStart(s, i):
                    i += 2
                    while i < len(s):
                        progress = i
                        i = g.skip_ws_and_nl(s, i)
                        if self.isModuleStart(s, i): break
                        else: i = g.skip_line(s, i)
                        assert(i > progress)
                #@+<< Handle cweb @d, @f, @c and @p directives >>
                #@+node:ekr.20031218072017.3235: *7* << Handle cweb @d, @f, @c and @p directives >>
                if g.match(s, i, "@d") or g.match(s, i, "@f"):
                    i += 2; i = g.skip_line(s, i)
                    # Place all @d and @f directives in the same node.
                    while i < len(s):
                        progress = i
                        i = g.skip_ws_and_nl(s, i)
                        if g.match(s, i, "@d") or g.match(s, i, "@f"): i = g.skip_line(s, i)
                        else: break
                        assert(i > progress)
                    i = g.skip_ws_and_nl(s, i)
                while i < len(s) and not self.isModuleStart(s, i):
                    progress = i
                    i = g.skip_line(s, i)
                    i = g.skip_ws_and_nl(s, i)
                    assert(i > progress)
                if g.match(s, i, "@c") or g.match(s, i, "@p"):
                    i += 2
                    while i < len(s):
                        progress = i
                        i = g.skip_line(s, i)
                        i = g.skip_ws_and_nl(s, i)
                        if self.isModuleStart(s, i):
                            break
                        assert(i > progress)
                #@-<< Handle cweb @d, @f, @c and @p directives >>
            else:
                assert(self.isDocStart(s, i)) # isModuleStart == isDocStart for noweb.
                start = i; i = g.skip_line(s, i)
                while i < len(s):
                    progress = i
                    i = g.skip_ws_and_nl(s, i)
                    if self.isDocStart(s, i): break
                    else: i = g.skip_line(s, i)
                    assert(i > progress)
            body = s[start: i]
            body = self.massageWebBody(body)
            headline = self.scanBodyForHeadline(body)
            self.createHeadline(parent, body, headline)
            #@-<< Create a node for the next module >>
            assert(i > outer_progress)
    #@+node:ekr.20031218072017.3236: *5* Symbol table
    #@+node:ekr.20031218072017.3237: *6* cstCanonicalize
    # We canonicalize strings before looking them up, but strings are entered in the form they are first encountered.

    def cstCanonicalize(self, s, lower=True):
        if lower:
            s = s.lower()
        s = s.replace("\t", " ").replace("\r", "")
        s = s.replace("\n", " ").replace("  ", " ")
        return s.strip()
    #@+node:ekr.20031218072017.3238: *6* cstDump
    def cstDump(self):
        s = "Web Symbol Table...\n\n"
        for name in sorted(self.web_st):
            s += name + "\n"
        return s
    #@+node:ekr.20031218072017.3239: *6* cstEnter
    # We only enter the section name into the symbol table if the ... convention is not used.

    def cstEnter(self, s):
        # Don't enter names that end in "..."
        s = s.rstrip()
        if s.endswith("..."): return
        # Put the section name in the symbol table, retaining capitalization.
        lower = self.cstCanonicalize(s, True) # do lower
        upper = self.cstCanonicalize(s, False) # don't lower.
        for name in self.web_st:
            if name.lower() == lower:
                return
        self.web_st.append(upper)
    #@+node:ekr.20031218072017.3240: *6* cstLookup
    # This method returns a string if the indicated string is a prefix of an entry in the web_st.

    def cstLookup(self, target):
        # Do nothing if the ... convention is not used.
        target = target.strip()
        if not target.endswith("..."): return target
        # Canonicalize the target name, and remove the trailing "..."
        ctarget = target[: -3]
        ctarget = self.cstCanonicalize(ctarget).strip()
        found = False; result = target
        for s in self.web_st:
            cs = self.cstCanonicalize(s)
            if cs[: len(ctarget)] == ctarget:
                if found:
                    g.es('', "****** %s" % (target), "is also a prefix of", s)
                else:
                    found = True; result = s
                    # g.es("replacing",target,"with",s)
        return result
    #@+node:ekr.20070713075352: *3* ic.scanUnknownFileType & helper
    def scanUnknownFileType(self, s, p, ext, atAuto=False):
        '''Scan the text of an unknown file type.'''
        c = self.c
        changed = c.isChanged()
        body = ''
        if ext in ('.html', '.htm'): body += '@language html\n'
        elif ext in ('.txt', '.text'): body += '@nocolor\n'
        else:
            language = self.languageForExtension(ext)
            if language: body += '@language %s\n' % language
        self.setBodyString(p, body + self.rootLine + s)
        if atAuto:
            for p in p.self_and_subtree():
                p.clearDirty()
            if not changed:
                c.setChanged(False)
        g.app.unitTestDict = {'result': True}
        return True
    #@+node:ekr.20080811174246.1: *4* ic.languageForExtension
    def languageForExtension(self, ext):
        '''Return the language corresponding to the extension ext.'''
        unknown = 'unknown_language'
        if ext.startswith('.'): ext = ext[1:]
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
        # g.trace(ext,repr(language))
        # Return the language even if there is no colorizer mode for it.
        return language
    #@+node:ekr.20140531104908.18833: *3* ic.parse_body & helper
    def parse_body(self, p):
        '''
        Parse p.b as source code, creating a tree of descendant nodes.
        This is essentially an import of p.b.
        '''
        if not p: return
        c, ic = self.c, self
        if p.hasChildren():
            g.es_print('can not run parse-body: node has children:', p.h)
            return
        language = g.scanForAtLanguage(c, p)
        self.treeType = '@file'
        ext = '.' + g.app.language_extension_dict.get(language)
        parser = self.body_parser_for_ext(ext)
        # Fix bug 151: parse-body creates "None declarations"
        if p.isAnyAtFileNode():
            fn = p.anyAtFileNodeName()
            ic.methodName, ic.fileType = g.os_path_splitext(fn)
        else:
            d = g.app.language_extension_dict
            fileType = d.get(language, 'py')
            ic.methodName, ic.fileType = p.h, fileType
        # g.trace(language, ext, parser and parser.__name__ or '<NO PARSER>')
        if parser:
            bunch = c.undoer.beforeChangeTree(p)
            s = p.b
            p.b = ''
            try:
                parser(p, s)
                c.undoer.afterChangeTree(p, 'parse-body', bunch)
                p.expand()
                c.selectPosition(p)
                c.redraw()
            except Exception:
                g.es_exception()
                p.b = s
        else:
            g.es_print('parse-body: no parser for @language %s' % (language or 'None'))
    #@+node:ekr.20140205074001.16365: *4* ic.body_parser_for_ext
    def body_parser_for_ext(self, ext):
        '''A factory returning a body parser function for the given file extension.'''
        aClass = ext and self.classDispatchDict.get(ext)

        def body_parser_for_class(parent, s):
            obj = aClass(importCommands=self, atAuto=True)
            return obj.run(s, parent, parse_body=True)

        return body_parser_for_class if aClass else None
    #@+node:ekr.20070713075450: *3* ic.Unit tests

    # atAuto must be False for unit tests: otherwise the test gets wiped out.

    def cUnitTest(self, p, fileName=None, s=None, showTree=False):
        return self.scannerUnitTest(p, atAuto=False, fileName=fileName, s=s, showTree=showTree, ext='.c')

    def cSharpUnitTest(self, p, fileName=None, s=None, showTree=False):
        return self.scannerUnitTest(p, atAuto=False, fileName=fileName, s=s, showTree=showTree, ext='.c#')
        
    def coffeeScriptUnitTest(self, p, fileName=None, s=None, showTree=False):
        return self.scannerUnitTest(p, atAuto=False, fileName=fileName, s=s, showTree=showTree, ext='.coffee')

    def ctextUnitTest(self, p, fileName=None, s=None, showTree=False):
        return self.scannerUnitTest(p, atAuto=False, fileName=fileName, s=s, showTree=showTree, ext='.txt')

    def dartUnitTest(self, p, fileName=None, s=None, showTree=False):
        return self.scannerUnitTest(p, atAuto=False, fileName=fileName, s=s, showTree=showTree, ext='.dart')

    def elispUnitTest(self, p, fileName=None, s=None, showTree=False):
        return self.scannerUnitTest(p, atAuto=False, fileName=fileName, s=s, showTree=showTree, ext='.el')

    def htmlUnitTest(self, p, fileName=None, s=None, showTree=False):
        return self.scannerUnitTest(p, atAuto=False, fileName=fileName, s=s, showTree=showTree, ext='.htm')

    def iniUnitTest(self, p, fileName=None, s=None, showTree=False):
        return self.scannerUnitTest(p, atAuto=False, fileName=fileName, s=s, showTree=showTree, ext='.ini')

    def javaUnitTest(self, p, fileName=None, s=None, showTree=False):
        return self.scannerUnitTest(p, atAuto=False, fileName=fileName, s=s, showTree=showTree, ext='.java')

    def javaScriptUnitTest(self, p, fileName=None, s=None, showTree=False):
        return self.scannerUnitTest(p, atAuto=False, fileName=fileName, s=s, showTree=showTree, ext='.js')

    def markdownUnitTest(self, p, fileName=None, s=None, showTree=False):
        return self.scannerUnitTest(p, atAuto=False, fileName=fileName, s=s, showTree=showTree, ext='.md')

    def orgUnitTest(self, p, fileName=None, s=None, showTree=False):
        return self.scannerUnitTest(p, atAuto=False, fileName=fileName, s=s, showTree=showTree, ext='.org')
        
    def otlUnitTest(self, p, fileName=None, s=None, showTree=False):
        return self.scannerUnitTest(p, atAuto=False, fileName=fileName, s=s, showTree=showTree, ext='.otl')

    def pascalUnitTest(self, p, fileName=None, s=None, showTree=False):
        return self.scannerUnitTest(p, atAuto=False, fileName=fileName, s=s, showTree=showTree, ext='.pas')
        
    def perlUnitTest(self, p, fileName=None, s=None, showTree=False):
        return self.scannerUnitTest(p, atAuto=False, fileName=fileName, s=s, showTree=showTree, ext='.pl')

    def phpUnitTest(self, p, fileName=None, s=None, showTree=False):
        return self.scannerUnitTest(p, atAuto=False, fileName=fileName, s=s, showTree=showTree, ext='.php')

    def pythonUnitTest(self, p, atAuto=False, fileName=None, s=None, showTree=False):
        return self.scannerUnitTest(p, atAuto=atAuto, fileName=fileName, s=s, showTree=showTree, ext='.py')

    def rstUnitTest(self, p, fileName=None, s=None, showTree=False):
        if docutils:
            return self.scannerUnitTest(p, atAuto=False, fileName=fileName, s=s, showTree=showTree, ext='.rst')
        else:
            return None

    def textUnitTest(self, p, fileName=None, s=None, showTree=False):
        return self.scannerUnitTest(p, atAuto=False, fileName=fileName, s=s, showTree=showTree, ext='.txt')

    def typeScriptUnitTest(self, p, fileName=None, s=None, showTree=False):
        return self.scannerUnitTest(p, atAuto=False, fileName=fileName, s=s, showTree=showTree, ext='.ts')

    def xmlUnitTest(self, p, fileName=None, s=None, showTree=False):
        return self.scannerUnitTest(p, atAuto=False, fileName=fileName, s=s, showTree=showTree, ext='.xml')

    def defaultImporterUnitTest(self, p, fileName=None, s=None, showTree=False):
        return self.scannerUnitTest(p, atAuto=False, fileName=fileName, s=s, showTree=showTree, ext='.xxx')
    #@+node:ekr.20070713082220: *4* ic.scannerUnitTest (uses GeneralTestCase)
    def scannerUnitTest(self, p, atAuto=False, ext=None, fileName=None, s=None, showTree=False):
        '''
        Run a unit test of an import scanner,
        i.e., create a tree from string s at location p.
        '''
        trace = False
        c = self.c; h = p.h; old_root = p.copy()
        oldChanged = c.changed
        # A hack.  Let unit tests set the kill-check flag first.
        d = g.app.unitTestDict
        if d.get('kill-check'):
            d = {'kill-check': True}
        else:
            d = {}
        g.app.unitTestDict = d
        if not fileName: fileName = p.h
        if not s: s = self.removeSentinelsCommand([fileName], toString=True)
        title = h[5:] if h.startswith('@test') else h
        # Run the actual test using the **GeneralTestCase** class.
        self.createOutline(title.strip(), p.copy(), atAuto=atAuto, s=s, ext=ext)
        # Set ok.
        d = g.app.unitTestDict
        ok = d.get('result') is True
        if trace:
            g.trace('-'*10, ok, p.h)
            g.printDict(d)
        # Clean up.
        if showTree:
            # 2016/11/17: Make sure saving the outline doesn't create any file.
            for child in old_root.children():
                if child.isAnyAtFileNode():
                    child.h = '@' + child.h
        else:
            while old_root.hasChildren():
                old_root.firstChild().doDelete()
            c.setChanged(oldChanged)
        c.redraw(old_root)
        if g.app.unitTesting:
            d['kill-check'] = False
            if not ok:
                g.app.unitTestDict['fail'] = p.h
            assert ok, p.h
        return ok
    #@+node:ekr.20031218072017.3305: *3* ic.Utilities
    #@+node:ekr.20090122201952.4: *4* ic.appendStringToBody & setBodyString (leoImport)
    def appendStringToBody(self, p, s):
        '''Similar to c.appendStringToBody,
        but does not recolor the text or redraw the screen.'''
        if s:
            body = p.b
            assert(g.isUnicode(body))
            s = g.toUnicode(s, self.encoding)
            self.setBodyString(p, body + s)

    def setBodyString(self, p, s):
        '''Similar to c.setBodyString,
        but does not recolor the text or redraw the screen.'''
        c = self.c; v = p.v
        if not c or not p: return
        s = g.toUnicode(s, self.encoding)
        current = c.p
        if current and p.v == current.v:
            c.frame.body.setSelectionAreas(s, None, None)
            w = c.frame.body.wrapper
            i = w.getInsertPoint()
            w.setSelectionRange(i, i)
        # Keep the body text up-to-date.
        if v.b != s:
            v.setBodyString(s)
            v.setSelection(0, 0)
            p.setDirty()
            if not c.isChanged():
                c.setChanged(True)
    #@+node:ekr.20031218072017.3306: *4* ic.createHeadline
    def createHeadline(self, parent, body, headline):
        '''Create a new VNode as the last child of parent position.'''
        p = parent.insertAsLastChild()
        body = g.u(body)
        headline = g.u(headline)
        p.initHeadString(headline)
        if len(body) > 0:
            self.setBodyString(p, body)
        # g.trace(p.v.gnx,p.h)
        return p
    #@+node:ekr.20031218072017.3307: *4* ic.error
    def error(self, s):
        g.es('', s)
    #@+node:ekr.20031218072017.3309: *4* ic.isDocStart & isModuleStart
    # The start of a document part or module in a noweb or cweb file.
    # Exporters may have to test for @doc as well.

    def isDocStart(self, s, i):
        if not g.match(s, i, "@"):
            return False
        j = g.skip_ws(s, i + 1)
        if g.match(s, j, "%defs"):
            return False
        elif self.webType == "cweb" and g.match(s, i, "@*"):
            return True
        else:
            return g.match(s, i, "@ ") or g.match(s, i, "@\t") or g.match(s, i, "@\n")

    def isModuleStart(self, s, i):
        if self.isDocStart(s, i):
            return True
        else:
            return self.webType == "cweb" and (
                g.match(s, i, "@c") or g.match(s, i, "@p") or
                g.match(s, i, "@d") or g.match(s, i, "@f"))
    #@+node:ekr.20031218072017.3312: *4* ic.massageWebBody
    def massageWebBody(self, s):
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
                    i = g.skip_line(s, i); start = end = i
                else:
                    start = end = i; i += 2
                while i < len(s):
                    progress2 = i
                    i = g.skip_ws_and_nl(s, i)
                    if self.isModuleStart(s, i) or g.match(s, i, lb):
                        end = i; break
                    elif theType == "cweb": i += 1
                    else: i = g.skip_to_end_of_line(s, i)
                    assert(i > progress2)
                # Remove newlines from start to end.
                doc = s[start: end]
                doc = doc.replace("\n", " ")
                doc = doc.replace("\r", "")
                doc = doc.strip()
                if doc and len(doc) > 0:
                    if doc == "@":
                        doc = "@ " if self.webType == "cweb" else "@\n"
                    else:
                        doc += "\n\n"
                    # g.trace("new doc:",doc)
                    s = s[: start] + doc + s[end:]
                    i = start + len(doc)
            else: i = g.skip_line(s, i)
            assert(i > progress)
        #@-<< Remove most newlines from @space and @* sections >>
        #@+<< Replace abbreviated names with full names >>
        #@+node:ekr.20031218072017.3314: *5* << Replace abbreviated names with full names >>
        i = 0
        while i < len(s):
            progress = i
            # g.trace(g.get_line(s,i))
            if g.match(s, i, lb):
                i += 2; j = i; k = g.find_on_line(s, j, rb)
                if k > -1:
                    name = s[j: k]
                    name2 = self.cstLookup(name)
                    if name != name2:
                        # Replace name by name2 in s.
                        # g.trace("replacing %s by %s" % (name,name2))
                        s = s[: j] + name2 + s[k:]
                        i = j + len(name2)
            i = g.skip_line(s, i)
            assert(i > progress)
        #@-<< Replace abbreviated names with full names >>
        s = s.rstrip()
        return s
    #@+node:ekr.20031218072017.1463: *4* ic.setEncoding (leoImport)
    def setEncoding(self, p=None, atAuto=False):
        c = self.c
        encoding = g.getEncodingAt(p or c.p)
        if encoding and g.isValidEncoding(encoding):
            self.encoding = encoding
        elif atAuto:
            self.encoding = c.config.default_at_auto_file_encoding
        else:
            self.encoding = 'utf-8'
    #@-others
#@+node:ekr.20160503144404.1: ** class MindMapImporter
class MindMapImporter(object):
    '''Mind Map Importer class.'''

    def __init__(self, c):
        '''ctor for MindMapImporter class.'''
        self.c = c

    #@+others
    #@+node:ekr.20160503130209.1: *3* mindmap.create_outline
    def create_outline(self, path):
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
            self.scan(path, p)
        except Exception:
            g.es_print('Invalid MindJet file:', fn)
        c.undoer.afterInsertNode(p, 'Import', undoData)
        return p
    #@+node:ekr.20160503144647.1: *3* mindmap.import_files
    def import_files(self, files):
        '''Import a list of MindMap (.csv) files.'''
        c = self.c
        if files:
            self.tab_width = c.getTabWidth(c.p)
            for fileName in files:
                g.setGlobalOpenDir(fileName)
                p = self.create_outline(fileName)
                p.contract()
                p.setDirty()
                c.setChanged(True)
            c.redraw(p)
    #@+node:ekr.20160504043243.1: *3* mindmap.prompt_for_files
    def prompt_for_files(self):
        '''Prompt for a list of MindJet (.csv) files and import them.'''
        c = self.c
        types = [
            ("MindJet files", "*.csv"),
            ("All files", "*"),
        ]
        names = g.app.gui.runOpenFileDialog(c,
            title="Import MindJet File",
            filetypes=types,
            defaultextension=".csv",
            multiple=True)
        c.bringToFront()
        if names:
            g.chdir(names[0])
            self.import_files(names)
    #@+node:ekr.20160503130256.1: *3* mindmap.scan & helpers
    def scan(self, path, target):
        '''Create an outline from a MindMap (.csv) file.'''
        c = self.c
        f = open(path)
        reader = csv.reader(f)
        max_chars_in_header = 80
        n1 = n = target.level()
        p = target.copy()
        for row in list(reader)[1:]:
            new_level = self.csv_level(row) + n1
            self.csv_string(row)
            if new_level > n:
                p = p.insertAsLastChild().copy()
                p.b = self.csv_string(row)
                n = n+1
            elif new_level == n:
                p = p.insertAfter().copy()
                p.b = self.csv_string(row)
            elif new_level < n:
                for item in p.parents():
                    if item.level() == new_level-1:
                        p = item.copy()
                        break
                p = p.insertAsLastChild().copy()
                p.b = self.csv_string(row)
                n = p.level()
        for p in target.unique_subtree():
            if len(p.b.splitlines()) == 1:
                if len(p.b.splitlines()[0]) < max_chars_in_header:
                    p.h = p.b.splitlines()[0]
                    p.b = ""
                else:
                    p.h = "@node_with_long_text"
            else:
                p.h = "@node_with_long_text"
        c.redraw()
        f.close()
    #@+node:ekr.20160503130810.4: *4* mindmap.csv_level
    def csv_level(self, row):
        '''Return the level of the given row.'''
        count = 0
        while count <= len(row):
            if row[count]:
                return count+1
            else:
                count = count+1
        return -1
    #@+node:ekr.20160503130810.5: *4* mindmap.csv_string
    def csv_string(self, row):
        '''Return the string for the given csv row.'''
        count = 0
        while count<=len(row):
            if row[count]:
                return row[count]
            else:
                count = count+1
        return None
    #@-others
#@+node:ekr.20161006100941.1: ** class MORE_Importer
class MORE_Importer(object):
    '''Class to import MORE files.'''

    def __init__(self, c):
        '''ctor for MORE_Importer class.'''
        self.c = c

    #@+others
    #@+node:ekr.20161006101111.1: *3* MORE.prompt_for_files
    def prompt_for_files(self):
        '''Prompt for a list of MORE files and import them.'''
        c = self.c
        types = [
            ("All files", "*"),
        ]
        names = g.app.gui.runOpenFileDialog(c,
            title="Import MORE Files",
            filetypes=types,
            # defaultextension=".txt",
            multiple=True)
        c.bringToFront()
        if names:
            g.chdir(names[0])
            self.import_files(names)
    #@+node:ekr.20161006101218.1: *3* MORE.import_files
    def import_files(self, files):
        '''Import a list of MORE (.csv) files.'''
        c = self.c
        if files:
            changed = False
            self.tab_width = c.getTabWidth(c.p)
            for fileName in files:
                g.setGlobalOpenDir(fileName)
                p = self.import_file(fileName)
                if p:
                    p.contract()
                    p.setDirty()
                    c.setChanged(True)
                    changed = True
            if changed:
                c.redraw(p)
    #@+node:ekr.20161006101347.1: *3* MORE.import_file
    def import_file(self, fileName): # Not a command, so no event arg.
        c = self.c; u = c.undoer
        ic = c.importCommands
        if not c.p: return
        ic.setEncoding()
        g.setGlobalOpenDir(fileName)
        s, e = g.readFileIntoString(fileName)
        if s is None: return None
        s = s.replace('\r', '') # Fixes bug 626101.
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
                c.validateOutline()
                p.setDirty()
                c.setChanged(True)
                u.afterInsertNode(root, 'Import MORE File', undoData)
                c.selectPosition(root)
                c.redraw()
                return root
        if not g.unitTesting:
            g.es("not a valid MORE file", fileName)
        return None
    #@+node:ekr.20031218072017.3215: *3* MORE.import_lines
    def import_lines(self, strings, first_p):
        c = self.c
        if len(strings) == 0: return None
        if not self.check_lines(strings): return None
        firstLevel, junk = self.headlineLevel(strings[0])
        lastLevel = -1; theRoot = last_p = None
        index = 0
        while index < len(strings):
            progress = index
            s = strings[index]
            level, junk = self.headlineLevel(s)
            level -= firstLevel
            if level >= 0:
                #@+<< Link a new position p into the outline >>
                #@+node:ekr.20031218072017.3216: *4* << Link a new position p into the outline >>
                assert(level >= 0)
                if not last_p:
                    theRoot = p = first_p.insertAsLastChild() # 2016/10/06.
                elif level == lastLevel:
                    p = last_p.insertAfter()
                elif level == lastLevel + 1:
                    p = last_p.insertAsNthChild(0)
                else:
                    assert(level < lastLevel)
                    while level < lastLevel:
                        lastLevel -= 1
                        last_p = last_p.parent()
                        assert(last_p)
                        assert(lastLevel >= 0)
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
                index += 1 # Skip the headline.
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
            else: index += 1
            assert progress < index
        if theRoot:
            theRoot.setDirty()
            c.setChanged(True)
        c.redraw()
        return theRoot
    #@+node:ekr.20031218072017.3222: *3* MORE.headlineLevel
    def headlineLevel(self, s):
        '''return the headline level of s,or -1 if the string is not a MORE headline.'''
        level = 0; i = 0
        while i < len(s) and s[i] in ' \t': # 2016/10/06: allow blanks or tabs.
            level += 1
            i += 1
        plusFlag = g.match(s, i, "+")
        if g.match(s, i, "+ ") or g.match(s, i, "- "):
            return level, plusFlag
        else:
            return -1, plusFlag
    #@+node:ekr.20031218072017.3223: *3* MORE.check & check_lines
    def check(self, s):
        s = s.replace("\r", "")
        strings = g.splitLines(s)
        return self.check_lines(strings)

    def check_lines(self, strings):
        trace = False and not g.unitTesting
        if len(strings) < 1: return False
        level1, plusFlag = self.headlineLevel(strings[0])
        if level1 == -1: return False
        # Check the level of all headlines.
        lastLevel = level1
        for s in strings:
            level, newFlag = self.headlineLevel(s)
            if trace: g.trace('level1: %s level: %s lastLevel: %s %s' % (
                level1, level, lastLevel, s.rstrip()))
            if level == -1:
                return True # A body line.
            elif level < level1 or level > lastLevel + 1:
                return False # improper level.
            elif level > lastLevel and not plusFlag:
                return False # parent of this node has no children.
            elif level == lastLevel and plusFlag:
                return False # last node has missing child.
            else:
                lastLevel = level
                plusFlag = newFlag
        return True
    #@-others
#@+node:ekr.20130823083943.12596: ** class RecursiveImportController
class RecursiveImportController(object):
    '''Recursively import all python files in a directory and clean the result.'''
    #@+others
    #@+node:ekr.20130823083943.12615: *3* ctor
    def __init__(self, c, kind, one_file=False, safe_at_file=True, theTypes=None):
        '''Ctor for RecursiveImportController class.'''
        self.c = c
        self.kind = kind
            # in ('@auto', '@clean', '@edit', '@file', '@nosent')
        self.one_file = one_file
        self.recursive = not one_file
        self.safe_at_file = safe_at_file
        self.theTypes = theTypes
    #@+node:ekr.20130823083943.12597: *3* Pass 1: import_dir (RecursiveImportController)
    def import_dir(self, dir_, root):
        '''Import selected files from dir_, a directory.'''
        trace = False and not g.unitTesting
        c = self.c
        g.blue(g.os_path_normpath(dir_))
        files = os.listdir(dir_)
        if trace: g.trace(sorted(files))
        dirs, files2 = [], []
        for f in files:
            path = f
            try: # Fix #408.
                path = g.os_path_join(dir_, f, expanduser=False)
                if trace: g.trace('is_file', g.os_path_isfile(path), path)
                if g.os_path_isfile(path):
                    name, ext = g.os_path_splitext(f)
                    if ext in self.theTypes:
                        files2.append(path)
                elif self.recursive:
                    dirs.append(path)
            except Exception:
                g.es_print('Exception computing', path)
                g.es_exception()
        if files2 or dirs:
            child = root.insertAsLastChild()
            child.h = dir_
            c.selectPosition(child, enableRedrawFlag=False)
        if trace:
            g.trace('files2...\n%s' % '\n'.join(files2))
            g.trace('dirs...\n%s' % '\n'.join(dirs))
        if files2:
            if self.one_file:
                files2 = [files2[0]]
            if self.kind == '@edit':
                for fn in files2:
                    try: # Fix #408
                        parent = child or root
                        p = parent.insertAsLastChild()
                        p.h = fn.replace('\\', '/')
                        s, e = g.readFileIntoString(fn, kind=self.kind)
                        p.b = s
                    except Exception:
                        g.es_print('Exception importing', fn)
                        g.es_exception()
            elif self.kind == '@auto':
                for fn in files2:
                    parent = child or root
                    p = parent.insertAsLastChild()
                    p.h = fn.replace('\\', '/')
                    p.clearDirty()
            else:
                root = c.p
                for fn in files2:
                    c.selectPosition(root)
                    try: # Fix #408.
                        c.importCommands.importFilesCommand(
                            [fn], '@file', redrawFlag=False, shortFn=True)
                            # '@auto','@clean','@nosent' cause problems.
                    except Exception:
                        g.es_print('Exception importing', fn)
                        g.es_exception()
        if dirs:
            for dir_ in sorted(dirs):
                self.import_dir(dir_, child)
    #@+node:ekr.20130823083943.12598: *3* Pass 2: clean_all & helpers
    def clean_all(self, dir_, p):
        '''Clean all imported nodes. This takes a lot of time.'''
        trace = False and not g.unitTesting
        t1 = time.time()
        prev_dir = None
        for p in p.self_and_subtree():
            h = p.h
            for tag in ('@clean', '@file', '@nosent'):
                if h.startswith('@' + tag):
                    i = 1 + len(tag)
                    path = h[i:].strip()
                    dir_, fn = g.os_path_split(path)
                    if prev_dir != dir_:
                        g.blue(g.os_path_normpath(dir_))
                        prev_dir = dir_
                    junk, ext = g.os_path_splitext(path)
                    self.clean(p, ext)
                elif h.startswith(tag):
                    i = len(tag)
                    path = h[i:].strip()
                    dir_, fn = g.os_path_split(path)
                    if prev_dir != dir_:
                        g.blue(g.os_path_normpath(dir_))
                        prev_dir = dir_
                    junk, ext = g.os_path_splitext(path)
                    self.clean(p, ext)
        t2 = time.time()
        if trace: g.trace('%2.2f sec' % (t2-t1))
    #@+node:ekr.20130823083943.12599: *4* clean
    def clean(self, p, ext):
        '''
        - Move a shebang line from the first child to the root.
        - Move a leading docstring in the first child to the root.
        - Use a section reference for declarations.
        - Remove leading and trailing blank lines from all nodes.
        - Merge a node containing nothing but comments with the next node.
        - Merge a node containing no class or def lines with the previous node.
        '''
        g.blue('cleaning', g.shortFileName(p.h))
        root = p.copy()
        for tag in ('@@file', '@file'):
            if p.h.startswith(tag):
                p.h = p.h[len(tag):].strip()
                break
        self.move_shebang_line(root)
        self.move_doc_string(root)
        self.rename_decls(root)
        for p in root.self_and_subtree():
            self.clean_blank_lines(p)
        # Get the single-line comment delim.
        if ext.startswith('.'): ext = ext[1:]
        language = g.app.extension_dict.get(ext)
        if language:
            delim, junk, junk = g.set_delims_from_language(language)
        else:
            delim = None
        # g.trace('ext: %s language: %s delim: %s' % (ext,language,delim))
        if delim:
            # Do general language-dependent cleanups.
            for p in root.subtree():
                self.merge_comment_nodes(p, delim)
        if ext == 'py':
            # Do python only cleanups.
            for p in root.subtree():
                self.merge_extra_nodes(p)
            for p in root.subtree():
                self.move_decorator_lines(p)
    #@+node:ekr.20130823083943.12600: *4* clean_blank_lines
    def clean_blank_lines(self, p):
        '''Remove leading and trailing blank lines from all nodes.'''
        s = p.b
        if not s.strip():
            return
        result = g.splitLines(s)
        for i in 0, -1:
            while result:
                if result[i].strip():
                    break
                else:
                    del result[i]
        s = ''.join(result)
        if not s.endswith('\n'): s = s + '\n'
        if s != p.b:
            p.b = s
    #@+node:ekr.20130823083943.12601: *4* merge_comment_nodes
    def merge_comment_nodes(self, p, delim):
        '''Merge a node containing nothing but comments with the next node.'''
        if not p.hasChildren() and p.hasNext() and p.h.strip().startswith(delim):
            p2 = p.next()
            b = p.b.lstrip()
            b = b + ('\n' if b.endswith('\n') else '\n\n')
            p2.b = b + p2.b
            p.doDelete(p2)
    #@+node:ekr.20130823083943.12602: *4* merge_extra_nodes
    def merge_extra_nodes(self, p):
        '''Merge a node containing no class or def lines with the previous node'''
        s = p.b
        if p.hasChildren() or p.h.strip().startswith('<<') or not s.strip():
            return
        for s2 in g.splitLines(s):
            if s2.strip().startswith('class') or s2.strip().startswith('def'):
                return
        p2 = p.back()
        if p2:
            nl = '\n' if s.endswith('\n') else '\n\n'
            p2.b = p2.b + nl + s
            p.doDelete(p2)
    #@+node:ekr.20130823083943.12603: *4* move_decorator_lines (RecursiveImportController)
    def move_decorator_lines(self, p):
        '''Move trailing decorator lines to the next node.'''
        trace = False and not g.unitTesting
        seen = []
        p2 = p.next()
        if not p2:
            return False
        lines = g.splitLines(p.b)
        n = len(lines) - 1
        while n >= 0:
            s = lines[n]
            if s.startswith('@'):
                i = g.skip_id(s, 1, chars='-')
                word = s[1: i]
                if word in g.globalDirectiveList:
                    break
                else:
                    n -= 1
            else:
                break
        head = ''.join(lines[: n + 1])
        tail = ''.join(lines[n + 1:])
        if not tail:
            return False
        if not head.endswith('\n'):
            head = head + '\n'
        # assert p.b == head+tail
        if trace:
            if tail not in seen:
                seen.append(tail)
                g.trace(tail.strip())
        nl = '' if tail.endswith('\n') else '\n'
        p.b = head
        p2.b = tail + nl + p2.b
        return True
    #@+node:ekr.20130823083943.12604: *4* move_doc_string
    def move_doc_string(self, root):
        '''Move a leading docstring in the first child to the root node.'''
        # To do: copy comments before docstring
        p = root.firstChild()
        s = p and p.b or ''
        if not s:
            return
        result = []
        for s2 in g.splitLines(s):
            delim = None
            s3 = s2.strip()
            if not s3:
                result.append(s2)
            elif s3.startswith('#'):
                result.append(s2)
            elif s3.startswith('"""'):
                delim = '"""'
                break
            elif s3.startswith("'''"):
                delim = "'''"
                break
            else:
                break
        if not delim:
            comments = ''.join(result)
            if comments:
                nl = '\n\n' if root.b.strip() else ''
                if root.b.startswith('@first #!'):
                    lines = g.splitLines(root.b)
                    root.b = lines[0] + '\n' + comments + nl + ''.join(lines[1:])
                else:
                    root.b = comments + nl + root.b
                p.b = s[len(comments):]
            return
        i = s.find(delim)
        assert i > -1
        i = s.find(delim, i + 3)
        if i == -1:
            return
        doc = s[: i + 3]
        p.b = s[i + 3:].lstrip()
        # Move docstring to front of root.b, but after any shebang line.
        nl = '\n\n' if root.b.strip() else ''
        if root.b.startswith('@first #!'):
            lines = g.splitLines(root.b)
            root.b = lines[0] + '\n' + doc + nl + ''.join(lines[1:])
        else:
            root.b = doc + nl + root.b
    #@+node:ekr.20130823083943.12605: *4* move_shebang_line
    def move_shebang_line(self, root):
        '''Move a shebang line from the first child to the root.'''
        p = root.firstChild()
        s = p and p.b or ''
        if s.startswith('#!'):
            lines = g.splitLines(s)
            nl = '\n\n' if root.b.strip() else ''
            root.b = '@first ' + lines[0] + nl + root.b
            p.b = ''.join(lines[1:])
    #@+node:ekr.20130823083943.12606: *4* rename_decls
    def rename_decls(self, root):
        '''Use a section reference for declarations.'''
        p = root.firstChild()
        h = p and p.h or ''
        tag = 'declarations'
        if not h.endswith(tag):
            return
        if not p.b.strip():
            return # The blank node will be deleted.
        name = h[: -len(tag)].strip()
        decls = g.angleBrackets(tag)
        p.h = '%s (%s)' % (decls, name)
        i = root.b.find('@others')
        if i == -1:
            g.trace('can not happen')
        else:
            nl = '' if i == 0 else '\n'
            root.b = root.b[: i] + nl + decls + '\n' + root.b[i:]
    #@+node:ekr.20130823083943.12607: *3* Pass 3: post_process & helpers
    def post_process(self, p, prefix):
        '''
        Traverse p's tree, replacing all nodes that start with prefix
        by the smallest equivalent @path or @file node.
        '''
        trace = False and not g.unitTesting
        if trace: t1 = time.time()
        root = p.copy()
        self.fix_back_slashes(root.copy())
        prefix = prefix.replace('\\', '/')
        if self.kind not in ('@auto', '@edit'):
            self.remove_empty_nodes(root.copy())
        self.minimize_headlines(root.copy().firstChild(), prefix)
        self.clear_dirty_bits(root.copy())
        if trace:
            t2 = time.time()
            g.trace('%2.2f sec' % (t2-t1))
    #@+node:ekr.20130823083943.12608: *4* clear_dirty_bits
    def clear_dirty_bits(self, p):
        c = self.c
        c.setChanged(False)
        for p in p.self_and_subtree():
            p.clearDirty()
    #@+node:ekr.20130823083943.12609: *4* dump_headlines
    def dump_headlines(self, p):
        # show all headlines.
        for p in p.self_and_subtree():
            print(p.h)
    #@+node:ekr.20130823083943.12610: *4* fix_back_slashes
    def fix_back_slashes(self, p):
        '''Convert backslash to slash in all headlines.'''
        for p in p.self_and_subtree():
            s = p.h.replace('\\', '/')
            if s != p.h:
                p.h = s
    #@+node:ekr.20130823083943.12611: *4* minimize_headlines
    def minimize_headlines(self, p, prefix):
        '''Create @path nodes to minimize the paths required in descendant nodes.'''
        trace = False and not g.unitTesting
        # This could only happen during testing.
        if p.h.startswith('@'):
            if trace: g.trace('** skipping: %s' % (p.h))
            return
        h2 = p.h[len(prefix):].strip()
        ends_with_ext = any([h2.endswith(z) for z in self.theTypes])
        if p.h == prefix:
            if trace: g.trace('@path %s' % (p.h))
            p.h = '@path %s' % (p.h)
            for p in p.children():
                self.minimize_headlines(p, prefix)
        elif h2.find('/') <= 0 and ends_with_ext:
            if h2.startswith('/'):
                h2 = h2[1:]
            p.h = '%s %s' % (self.kind, h2)
            if self.safe_at_file:
                p.h = '@' + p.h
            if trace: g.trace(p.h)
            # We never scan the children of @file nodes.
        else:
            if h2.startswith('/'): h2 = h2[1:]
            if trace:
                print('')
                g.trace('@path [%s/]%s' % (prefix, h2))
            p.h = '@path %s' % (h2)
            prefix2 = prefix if prefix.endswith('/') else prefix + '/'
            prefix2 = prefix2 + h2
            for p in p.children():
                self.minimize_headlines(p, prefix2)
    #@+node:ekr.20130823083943.12612: *4* remove_empty_nodes
    def remove_empty_nodes(self, p):
        c = self.c
        root = p.copy()
        # Restart the scan once a node is deleted.
        # This is not a significant performance issue.
        changed = True
        while changed:
            changed = False
            for p in root.self_and_subtree():
                if not p.b and not p.hasChildren():
                    # g.trace('** deleting',p.h)
                    p.doDelete()
                    c.selectPosition(root)
                    changed = True
                    break
    #@+node:ekr.20130823083943.12613: *3* run
    def run(self, dir_):
        '''Import all the .py files in dir_.'''
        if self.kind not in ('@auto', '@clean', '@edit', '@file', '@nosent'):
            g.es('bad kind param', self.kind, color='red')
        try:
            # pylint: disable=used-before-assignment
            # p *is* properly initied.
            c = self.c
            p = c.p
            p1 = p.copy()
            t1 = time.time()
            n = 0
            g.app.disable_redraw = True
            bunch = c.undoer.beforeChangeTree(p1)
            root = p.insertAfter()
            root.h = 'imported files'
            self.import_dir(dir_, root.copy())
            for p in root.self_and_subtree():
                n += 1
            if self.kind not in ('@auto', '@edit'):
                self.clean_all(dir_, root.copy())
            self.post_process(root.copy(), dir_)
            c.undoer.afterChangeTree(p1, 'recursive-import', bunch)
        except Exception:
            n = 0
            g.es_exception()
        finally:
            g.app.disable_redraw = False
            for p in root.self_and_subtree():
                p.contract()
            c.redraw(root)
        t2 = time.time()
        g.es('imported %s nodes in %2.2f sec' % (n, t2 - t1))
    #@-others
#@+node:ekr.20161006071801.1: ** class TabImporter
class TabImporter:
    '''
    A class to import a file whose outline levels are indicated by
    leading tabs or blanks (but not both).
    '''
    
    def __init__(self, c, separate=True):
        '''Ctor for the TabImporter class.'''
        self.c = c
        self.stack = []
        self.root = None
        self.separate = separate
        self.stack = []

    #@+others
    #@+node:ekr.20161006071801.2: *3* tabbed.check
    def check(self, lines, warn=True):
        '''Return False and warn if lines contains mixed leading tabs/blanks.'''
        blanks, tabs = 0, 0
        for s in lines:
            lws = self.lws(s)
            if '\t' in lws: tabs += 1
            if ' ' in lws: blanks += 1
        if tabs and blanks:
            if warn:
                g.es_print('intermixed leading blanks and tabs.')
            return False
        else:
            return True
    #@+node:ekr.20161006071801.3: *3* tabbed.dump_stack
    def dump_stack(self):
        '''Dump the stack, containing (level, p) tuples.'''
        g.trace('==========')
        for i, data in enumerate(self.stack):
            level, p = data
            print('%2s %s %r' % (i, level, p.h))
    #@+node:ekr.20161006073129.1: *3* tabbed.import_files
    def import_files(self, files):
        '''Import a list of tab-delimited files.'''
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
                if s.strip() and self.check(s):
                    undoData = u.beforeInsertNode(c.p)
                    last = c.lastTopLevel()
                    self.root = p = last.insertAfter()
                    self.scan(s)
                    p.h = g.shortFileName(fn)
                    p.contract()
                    p.setDirty()
                    u.afterInsertNode(p, 'Import Tabbed File', undoData)
                if p:
                    c.setChanged(True)
                    c.redraw(p)
    #@+node:ekr.20161006071801.4: *3* tabbed.lws
    def lws(self, s):
        '''Return the length of the leading whitespace of s.'''
        for i, ch in enumerate(s):
            if ch not in ' \t':
                return s[:i]
        return s
        
        
    #@+node:ekr.20161006072958.1: *3* tabbed.prompt_for_files
    def prompt_for_files(self):
        '''Prompt for a list of FreeMind (.mm.html) files and import them.'''
        c = self.c
        types = [
            ("All files", "*"),
        ]
        names = g.app.gui.runOpenFileDialog(c,
            title="Import Tabbed File",
            filetypes=types,
            defaultextension=".html",
            multiple=True)
        c.bringToFront()
        if names:
            g.chdir(names[0])
            self.import_files(names)
    #@+node:ekr.20161006071801.5: *3* tabbed.scan
    def scan(self, s1, fn=None, root=None):
        '''Create the outline corresponding to s1.'''
        trace = False and not g.unitTesting
        c = self.c
        # Self.root can be None if we are called from a script or unit test.
        if not self.root:
            last = root if root else c.lastTopLevel()
                # For unit testing.
            self.root = last.insertAfter()
            if fn: self.root.h = fn
        lines = g.splitLines(s1)
        self.stack = []
        # Redo the checks in case we are called from a script.
        if s1.strip() and self.check(lines):
            if trace: g.trace('importing to %s' % self.root.h)
            for s in lines:
                if s.strip() or not self.separate:
                    self.scan_helper(s)
        return self.root
    #@+node:ekr.20161006071801.6: *3* tabbed.scan_helper
    def scan_helper(self, s):
        '''Update the stack as necessary and return (level, parent, stack).'''
        trace = False and not g.unitTesting
        root, separate, stack = self.root, self.separate, self.stack
        if stack:
            level, parent = stack[-1]
        else:
            level, parent = 0, None
        lws = len(self.lws(s))
        if trace:
            g.trace('----- level: %s lws: %s %s' % (level, lws, s.rstrip()))
        h = s.strip()
        if lws == level:
            if separate or not parent:
                # Replace the top of the stack with a new entry.
                if stack:
                    stack.pop()
                grand_parent = stack[-1][1] if stack else root
                parent = grand_parent.insertAsLastChild() # lws == level
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
            if trace: self.dump_stack()
            while stack:
                level2, parent2 = stack.pop()
                if level2 == lws:
                    grand_parent = stack[-1][1] if stack else root
                    parent = grand_parent.insertAsLastChild() # lws < level
                    parent.h = h
                    level = lws
                    stack.append((level, parent),)
                    break
            else:
                level = 0
                parent = root.insertAsLastChild()
                parent.h = h
                stack = [(0, parent),]
        if trace:
            g.trace('DONE: lws: %s level: %s parent: %s' % (lws, level, parent.h))
            self.dump_stack()
        assert parent and parent == stack[-1][1]
            # An important invariant.
        assert level == stack[-1][0], (level, stack[-1][0])
        if not separate:
            parent.b = parent.b + self.undent(level, s)
        return level
    #@+node:ekr.20161006071801.7: *3* tabbed.undent
    def undent(self, level, s):
        '''Unindent all lines of p.b by level.'''
        # g.trace(level, s.rstrip())
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
                    g.trace('bad indentation: %r' % s)
                    return s
            return ''.join([z[len(lws):] for z in lines])
        else:
            return ''
    #@-others
#@+node:ekr.20141210051628.26: ** class ZimImportController
class ZimImportController(object):
    '''
    A class to import Zim folders and files: http://zim-wiki.org/
    First use Zim to export your project to rst files.

    Original script by Davy Cottet.

    User options:
        @int rst_level = 0
        @string rst_type
        @string zim_node_name
        @string path_to_zim

    '''
    #@+others
    #@+node:ekr.20141210051628.31: *3* zic.__init__
    def __init__(self, c):
        '''Ctor for ZimImportController class.'''
        self.c = c
        # User options.
        self.pathToZim = c.config.getString('path_to_zim')
        self.rstLevel = c.config.getInt('rst_level') or 0
        self.rstType = c.config.getString('rst_type') or 'rst'
        self.zimNodeName = c.config.getString('zim_node_name') or 'Imported Zim Tree'
    #@+node:ekr.20141210051628.28: *3* zic.parseZimIndex
    def parseZimIndex(self):
        """
        Parse Zim wiki index.rst and return a list of tuples (level, name, path)
        """
        # c = self.c
        pathToZim = g.os_path_abspath(self.pathToZim)
        pathToIndex = g.os_path_join(pathToZim, 'index.rst')
        if not g.os_path_exists(pathToIndex):
            g.es('not found: %s' % (pathToIndex), color='red')
            return None
        index = open(pathToIndex).read()
        # pylint: disable=anomalous-backslash-in-string
        parse = re.findall('(\t*)-\s`(.+)\s<(.+)>`_', index)
        if not parse:
            g.es('invalid index: %s' % (pathToIndex), color='red')
            return None
        results = []
        for result in parse:
            level = len(result[0])
            name = result[1].decode('utf-8')
            # pylint: disable=no-member
            unquote = urllib.parse.unquote if g.isPython3 else urllib.unquote
            path = [g.os_path_abspath(g.os_path_join(
                pathToZim, unquote(result[2]).decode('utf-8')))]
            results.append((level, name, path))
        return results
    #@+node:ekr.20141210051628.29: *3* zic.rstToLastChild
    def rstToLastChild(self, pos, name, rst):
        """Import an rst file as a last child of pos node with the specified name"""
        c = self.c
        c.selectPosition(pos, enableRedrawFlag=False)
        c.importCommands.importFilesCommand(rst, '@rst', redrawFlag=False)
        rstNode = pos.getLastChild()
        rstNode.h = name
        return rstNode
    #@+node:davy.20141212140940.1: *3* zic.clean
    def clean(self, zimNode, rstType):
        """Clean useless nodes"""
        warning = 'Warning: this node is ignored when writing this file'
        for p in zimNode.subtree_iter():
            # looking for useless bodies
            if p.hasFirstChild() and warning in p.b:
                child = p.getFirstChild()
                table = (
                    "@rst-no-head %s declarations" % p.h.replace(' ', '_'),
                    "@rst-no-head %s declarations" % p.h.replace(rstType, '').strip().replace(' ', '_'),
                )
                # Replace content with @rest-no-head first child (without title head) and delete it
                if child.h in table:
                    p.b = '\n'.join(child.b.split('\n')[3:])
                    child.doDelete()
                    # Replace content of empty body parent node with first child with same name
                elif p.h == child.h or ("%s %s" % (rstType, child.h) == p.h):
                    if not child.hasFirstChild():
                        p.b = child.b
                        child.doDelete()
                    elif not child.hasNext():
                        p.b = child.b
                        child.copyTreeFromSelfTo(p)
                        child.doDelete()
                    else:
                        child.h = 'Introduction'
            elif p.hasFirstChild() and p.h.startswith("@rst-no-head") and not p.b.strip():
                child = p.getFirstChild()
                p_no_head = p.h.replace("@rst-no-head", "").strip()
                # Replace empty @rst-no-head by its same named chidren
                if child.h.strip() == p_no_head and not child.hasFirstChild():
                    p.h = p_no_head
                    p.b = child.b
                    child.doDelete()
            elif p.h.startswith("@rst-no-head"):
                lines = p.b.split('\n')
                p.h = lines[1]
                p.b = '\n'.join(lines[3:])
    #@+node:ekr.20141210051628.30: *3* zic.run
    def run(self):
        '''Create the zim node as the last top-level node.'''
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
            rstNodes = {'0': zimNode,}
            for level, name, rst in files:
                if level == self.rstLevel:
                    name = "%s %s" % (self.rstType, name)
                rstNodes[str(level + 1)] = self.rstToLastChild(rstNodes[str(level)], name, rst)
            # Clean nodes
            g.es('Start cleaning process. Please wait...', color='blue')
            self.clean(zimNode, self.rstType)
            g.es('Done', color='blue')
            # Select zimNode
            c.selectPosition(zimNode)
            c.redraw()
    #@-others
#@+node:ekr.20101103093942.5938: ** Commands (leoImport)
#@+node:ekr.20101103093942.5941: *3* @g.command(head-to-prev-node)
@g.command('head-to-prev-node')
def headToPrevNode(event):
    '''Move the code preceding a def to end of previous node.'''
    c = event.get('c')
    if not c: return
    p = c.p
    try:
        import leo.plugins.importers.python as python
    except ImportError:
        return
    scanner = python.Py_Importer(c.importCommands, atAuto=False)
    kind, i, junk = scanner.find_class(p)
    p2 = p.back()
    if p2 and kind in ('class', 'def') and i > 0:
        u = c.undoer; undoType = 'move-head-to-prev'
        head = p.b[: i].rstrip()
        u.beforeChangeGroup(p, undoType)
        b = u.beforeChangeNodeContents(p)
        p.b = p.b[i:]
        u.afterChangeNodeContents(p, undoType, b)
        if head:
            b2 = u.beforeChangeNodeContents(p2)
            p2.b = p2.b.rstrip() + '\n\n' + head + '\n'
            u.afterChangeNodeContents(p2, undoType, b2)
        u.afterChangeGroup(p, undoType)
        c.selectPosition(p2)
#@+node:ekr.20160504050255.1: *3* @g.command(import-free-mind-files)
if lxml:

    @g.command('import-free-mind-files')
    def import_free_mind_files(event):
        '''Prompt for free-mind files and import them.'''
        c = event.get('c')
        if c:
            FreeMindImporter(c).prompt_for_files()
#@+node:ekr.20160504050325.1: *3* @g.command(import-mind-map-files
@g.command('import-mind-jet-files')
def import_mind_jet_files(event):
    '''Prompt for mind-jet files and import them.'''
    c = event.get('c')
    if c:
        MindMapImporter(c).prompt_for_files()
#@+node:ekr.20161006100854.1: *3* @g.command(import-MORE-files)
@g.command('import-MORE-files')
def import_MORE_files_command(event):
    '''Prompt for MORE files and import them.'''
    c = event.get('c')
    if c:
        MORE_Importer(c).prompt_for_files()
#@+node:ekr.20161006072227.1: *3* @g.command(import-tabbed-files)
@g.command('import-tabbed-files')
def import_tabbed_files_command(event):
    '''Prompt for tabbed files and import them.'''
    c = event.get('c')
    if c:
        TabImporter(c).prompt_for_files()
#@+node:ekr.20141210051628.33: *3* @g.command(import-zim-folder)
@g.command('import-zim-folder')
def import_zim_command(event):
    '''
    Import a zim folder, http://zim-wiki.org/, as the last top-level node of the outline.
    This command requires the following Leo settings::

        @int rst_level = 0
        @string rst_type
        @string zim_node_name
        @string path_to_zim
    '''
    c = event.get('c')
    if c:
        ZimImportController(c).run()
#@+node:ekr.20120429125741.10057: *3* @g.command(parse-body)
@g.command('parse-body')
def parse_body_command(event):
    '''The parse-body command.'''
    c = event.get('c')
    if c and c.p:
        c.importCommands.parse_body(c.p)
#@+node:ekr.20101103093942.5943: *3* @g.command(tail-to-next-node)
@g.command('tail-to-next-node')
def tailToNextNode(event=None):
    '''Move the code following a def to start of next node.'''
    c = event.get('c')
    if not c: return
    p = c.p
    try:
        import leo.plugins.importers.python as python
    except ImportError:
        return
    scanner = python.Py_Importer(c.importCommands, atAuto=False)
    kind, junk, j = scanner.find_class(p)
    p2 = p.next()
    if p2 and kind in ('class', 'def') and j < len(p.b):
        u = c.undoer; undoType = 'move-tail-to-next'
        tail = p.b[j:].rstrip()
        u.beforeChangeGroup(p, undoType)
        b = u.beforeChangeNodeContents(p)
        p.b = p.b[: j]
        u.afterChangeNodeContents(p, undoType, b)
        if tail:
            b2 = u.beforeChangeNodeContents(p2)
            p2.b = tail + '\n\n' + p2.b
            u.afterChangeNodeContents(p2, undoType, b2)
        u.afterChangeGroup(p, undoType)
        c.selectPosition(p2)
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@@encoding utf-8
#@-leo
