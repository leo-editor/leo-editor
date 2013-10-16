# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20090502071837.3: * @file leoRst.py
#@@first

#@+<< docstring >>
#@+node:ekr.20090502071837.4: ** << docstring >>
'''Support for restructured text (rST), adapted from rst3 plugin.

For full documentation, see: http://leoeditor.com/rstplugin3.html

To generate documents from rST files, Python's docutils_ module must be
installed. The code will use the SilverCity_ syntax coloring package if is is
available.'''
#@-<< docstring >>

if 0:
    bwm_file = open("bwm_file", "w")

#@+<< imports >>
#@+node:ekr.20100908120927.5971: ** << imports >> (leoRst)
verbose = False
import leo.core.leoGlobals as g

try:
    import docutils
    import docutils.core
except ImportError:
    docutils = None
if docutils:
    try:
        if verbose: print('leoRst.py',docutils)
        from docutils import parsers
        if verbose or not parsers: print('leoRst.py',parsers)
        from docutils.parsers import rst
        if verbose or not rst: print('leoRst.py',rst)
        if not parsers or not rst:
            docutils = None
    except ImportError:
        docutils = None
    except Exception:
        g.es_exception()
        docutils = None
if g.isPython3:
    import html.parser as HTMLParser
else:
    import HTMLParser
try:
    import leo.plugins.mod_http as mod_http
except ImportError:
    mod_http = None
except Exception:
    # Don't let a problem with a plugin crash Leo's core!
    # g.es_print('leoRst: can not import leo.plugins.mod_http')
    # g.es_exception()
    mod_http = None
# import os
import pprint
import re
try:
    import SilverCity
except ImportError:
    SilverCity = None
if g.isPython3:
    import io
    StringIO = io.StringIO
else:
    import StringIO
    StringIO = StringIO.StringIO
# import sys
# import tempfile
#@-<< imports >>

#@+others
#@+node:ekr.20090502071837.12: ** code_block
def code_block (name,arguments,options,
    content,lineno,content_offset,block_text,state,state_machine):

    '''Implement the code-block directive for docutils.'''

    try:
        language = arguments [0]
        # See http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/252170
        module = SilverCity and getattr(SilverCity,language)
        generator = module and getattr(module,language+"HTMLGenerator")
        if generator:
            io = StringIO()
            generator().generate_html(io,'\n'.join(content))
            html = '<div class="code-block">\n%s\n</div>\n' % io.getvalue()
        else:
            html = '<div class="code-block">\n%s\n</div>\n' % '<br>\n'.join(content)
        raw = docutils.nodes.raw('',html,format='html')
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
        docutils.parsers.rst.directives.unchanged # Return the text argument, unchanged.
        ### rst.directives.unchanged # Return the text argument, unchanged.
    }
    code_block.content = 1 # True if content is allowed.

    # Register the directive with docutils.
    docutils.parsers.rst.directives.register_directive('code-block',code_block)
else:
    code_block.options = {}
#@+node:ekr.20090502071837.33: ** class rstCommands
#@+at This plugin optionally stores information for the http plugin. Each node can
# have one additional attribute, with the name rst_http_attributename, which is a
# list. The first three elements are stack of tags, the rest is html code::
# 
#     [<tag n start>, <tag n end>, <other stack elements>, <html line 1>, <html line 2>, ...]
# 
# <other stack elements has the same structure::
# 
#     [<tag n-1 start>, <tag n-1 end>, <other stack elements>]
#@@c

class rstCommands:

    '''A class to write rst markup in Leo outlines.'''

    #@+others
    #@+node:ekr.20090502071837.34: *3*  Birth & init (rstCommands)
    #@+node:ekr.20090502071837.35: *4*  ctor (rstClass)
    def __init__ (self,c):

        global SilverCity

        self.c = c
        #@+<< init ivars >>
        #@+node:ekr.20090502071837.36: *5* << init ivars >> (leoRst)
        self.silverCityWarningGiven = False

        # The options dictionary.
        self.nodeOptionDict = {} # Keys are vnodes, values are optionsDict's.
        self.optionsDict = {}
        self.scriptSettingsDict = {} # 2010/08/12: for format-code command.

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
        self.atAutoWrite = False # True, special cases for writeAtAutoFile.
        self.atAutoWriteUnderlines = '' # Forced underlines for writeAtAutoFile.
        self.leoDirectivesList = g.globalDirectiveList
        self.encoding = 'utf-8'
        self.rst_nodes = [] # The list of positions for all @rst nodes.
        self.outputFile = None # The open file being written.
        self.path = '' # The path from any @path directive.
        self.source = None # The written source as a string.
        self.trialWrite = False # True if doing a trialWrite.
        #@-<< init ivars >>
        self.createDefaultOptionsDict()
        self.initOptionsFromSettings() # Still needed.
        self.initHeadlineCommands() # Only needs to be done once.
        self.initSingleNodeOptions()
    #@+node:ekr.20090502071837.102: *4*  getPublicCommands
    def getPublicCommands (self):        

        return {
            'rst3': self.rst3, # Formerly write-restructured-text.
            'code-to-rst': self.code_to_rst_command,
        }
    #@+node:ekr.20090511055302.5792: *4* finishCreate (rstCommands)
    def finishCreate(self):

        c = self.c
        d = self.getPublicCommands()
        c.commandsDict.update(d)
    #@+node:ekr.20090502071837.38: *4* initHeadlineCommands
    def initHeadlineCommands (self):

        '''Init the list of headline commands used by writeHeadline.'''

        self.headlineCommands = [
            '@rst',
            '@rst-code',
            '@rst-default-path',
            '@rst-doc-only',
            '@rst-head',
            '@rst-ignore-node',
            '@rst-ignore-tree',
            '@rst-no-head',
            '@rst-no-headlines',
            '@rst-option',
            '@rst-options',
        ]
    #@+node:ekr.20090502071837.39: *4* initSingleNodeOptions
    def initSingleNodeOptions (self):

        self.singleNodeOptions = [
            'ignore_this_headline',
            'ignore_this_node',
            'ignore_this_tree',
            'preformat_this_node',
            'show_this_headline',
        ]
    #@+node:ekr.20090502071837.40: *4* munge
    def munge (self,name):

        '''Convert an option name to the equivalent ivar name.'''

        i = g.choose(name.startswith('rst'),3,0)

        while i < len(name) and name[i].isdigit():
            i += 1

        if i < len(name) and name[i] == '_':
            i += 1

        s = name[i:].lower()
        s = s.replace('-','_')

        return s
    #@+node:ekr.20100813041139.5920: *3* Entry points
    #@+node:ekr.20100812082517.5945: *4* code_to_rst_command & helpers
    def code_to_rst_command (self,event=None,p=None,scriptSettingsDict=None,toString=False):

        '''Format the presently selected node as computer code.

        Settings from scriptSettingsDict override normal settings.

        On exit:
            self.source contains rst sources
            self.stringOutput contains docutils output if docutils called.
        '''

        c = self.c
        if p: p = p.copy()
        else: p = c.p
        self.topNode = p.copy()
        self.topLevel = p.level()

        # **Important**: This command works as much like the rst3 command as possible.
        # Difference arise because there is no @rst node to specify a filename.
        # Instead we get the filename from scriptSettingsDict, or use 'code_to_rst.html'

        # Capture the settings, munging all settings.
        self.scriptSettingsDict = {}
        d = scriptSettingsDict
        if d:
            for key in d.keys():
                self.scriptSettingsDict[self.munge(key)] = d.get(key)

        # Init options...
        self.preprocessTree(p)
        self.init_write(p) # scanAllDirectives sets self.path and self.encoding.
        self.scanAllOptions(p) # Settings for p are valid after this call.
        callDocutils = self.getOption('call_docutils')
        writeIntermediateFile = self.getOption('write_intermediate_file')
        # g.trace('writeIntermediateFile',writeIntermediateFile)
        fn = self.getOption('output-file-name') or 'code_to_rst.html'
        junk,ext = g.os_path_splitext(fn)

        # Write the rst sources to self.sources...
        self.outputFile = StringIO()
        self.write_code_tree(p,fn)
        self.source = self.outputFile.getvalue()
        self.outputFile = None

        if callDocutils or writeIntermediateFile:
            self.write_files(ext,fn,callDocutils,toString,writeIntermediateFile)
    #@+node:ekr.20100812082517.5963: *5* write_code_body & helpers
    def write_code_body (self,p):

        trace = False
        self.p = p.copy() # for traces.
        if not p.b.strip():
            return # No need to write any more newlines.

        showDocsAsParagraphs = self.getOption('show_doc_parts_as_paragraphs')
        lines = g.splitLines(p.b)
        parts = self.split_parts(lines,showDocsAsParagraphs)
        result = []
        for kind,lines in parts:
            if trace: g.trace(kind,len(lines),p.h)
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
                    result.extend(self.write_code_block(lines))
            elif kind == 'code':
                result.extend(self.write_code_block(lines))
            else:
                g.trace('Can not happen',kind)

        # Write the lines with exactly two trailing newlines.
        s = ''.join(result).rstrip() + '\n\n'
        self.write(s)
    #@+node:ekr.20100812082517.5964: *6* split_parts
    def split_parts (self,lines,showDocsAsParagraphs):

        '''Split a list of body lines into a list of tuples (kind,lines).'''

        kind,parts,part_lines = 'code',[],[]
        for s in lines:
            if g.match_word(s,0,'@ @rst-markup'):
                if part_lines: parts.append((kind,part_lines[:]),)
                kind = '@rst-markup'
                n = len('@ @rst-markup')
                after = s[n:].strip()
                part_lines = g.choose(after,[after],[])
            elif s.startswith('@ @rst-option'):
                if part_lines: parts.append((kind,part_lines[:]),)
                kind,part_lines = '@rst-option',[s] # part_lines will be ignored.
            elif s.startswith('@ ') or s.startswith('@\n') or s.startswith('@doc'):
                if showDocsAsParagraphs:
                    if part_lines: parts.append((kind,part_lines[:]),)
                    kind = '@doc'
                    # Put only what follows @ or @doc
                    n = g.choose(s.startswith('@doc'),4,1)
                    after = s[n:].lstrip()
                    part_lines = g.choose(after,[after],[])
                else:
                    part_lines.append(s) # still in code mode.
            elif g.match_word(s,0,'@c') and kind != 'code':
                if kind == '@doc' and not showDocsAsParagraphs:
                    part_lines.append(s) # Show the @c as code.
                parts.append((kind,part_lines[:]),)
                kind,part_lines = 'code',[]
            else:
                part_lines.append(s)

        if part_lines:
            parts.append((kind,part_lines[:]),)

        return parts
    #@+node:ekr.20100812082517.5965: *6* write_code_block
    def write_code_block (self,lines):

        result = ['::\n\n'] # ['[**code block**]\n\n']

        if self.getOption('number-code-lines'):
            i = 1
            for s in lines:
                result.append('    %d: %s' % (i,s))
                i += 1
        else:
            result.extend(['    %s' % (z) for z in lines])

        s = ''.join(result).rstrip()+'\n\n'
        return g.splitLines(s)
    #@+node:ekr.20100812082517.5966: *5* write_code_headline & helper
    def write_code_headline (self,p):

        '''Generate an rST section if options permit it.
        Remove headline commands from the headline first,
        and never generate an rST section for @rst-option and @rst-options.'''


        docOnly             = self.getOption('doc_only_mode')
        ignore              = self.getOption('ignore_this_headline')
        showHeadlines       = self.getOption('show_headlines')
        showThisHeadline    = self.getOption('show_this_headline')
        showOrganizers      = self.getOption('show_organizer_nodes')

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
    #@+node:ekr.20100812082517.5967: *6* write_code_headline_helper
    def write_code_headline_helper (self,p):

        h = p.h.strip()

        # Remove any headline command before writing the headline.
        i = g.skip_ws(h,0)
        i = g.skip_id(h,0,chars='@-')
        word = h [:i].strip()
        if word:
            # Never generate a section for @rst-option or @rst-options or @rst-no-head.
            if word in ('@rst-option','@rst-options','@rst-no-head','@rst-no-headlines'):
                return

            for prefix in ('@rst-ignore-node','@rst-ignore-tree','@rst-ignore'):
                if word == prefix:
                    h = h [len(word):].strip()
                    break

        if not h.strip(): return

        if self.getOption('show_sections'):
            self.write(self.underline(h,p))
        else:
            self.write('\n**%s**\n\n' % h.replace('*',''))
    #@+node:ekr.20100812082517.5968: *5* write_code_node
    def write_code_node (self,p):

        '''Format a node according to the options presently in effect.

        Side effect: advance p'''

        h = p.h.strip()
        self.scanAllOptions(p)

        if self.getOption('ignore_this_tree'):
            p.moveToNodeAfterTree()
        elif self.getOption('ignore_this_node'):
            p.moveToThreadNext()
        elif g.match_word(h,0,'@rst-options') and not self.getOption('show_options_nodes'):
            p.moveToThreadNext()
        else:
            self.http_addNodeMarker(p)
            self.write_code_headline(p)
            self.write_code_body(p)
            p.moveToThreadNext()
    #@+node:ekr.20100812082517.5939: *5* write_code_tree
    def write_code_tree (self,p,fn):

        '''Write p's tree as code to self.outputFile.'''

        self.scanAllOptions(p) # So we can get the next option.

        if self.getOption('generate_rst_header_comment'):
            self.write('.. rst3: filename: %s\n\n' % fn)

        # We can't use an iterator because we may skip parts of the tree.
        p = p.copy() # Only one copy is needed for traversal.
        self.topNode = p.copy() # Indicate the top of this tree.
        after = p.nodeAfterTree()
        while p and p != after:
            self.write_code_node(p) # Side effect: advances p.
    #@+node:ekr.20090511055302.5793: *4* rst3 command & helpers
    def rst3 (self,event=None):

        '''Write all @rst nodes.'''

        self.rst_nodes = []
        self.processTopTree(self.c.p)
        return self.rst_nodes # A list of positions.
    #@+node:ekr.20090502071837.62: *5* processTopTree
    def processTopTree (self,p,justOneFile=False):

        current = p.copy()

        # This strange looking code looks up and down the tree for @rst nodes.
        for p in current.self_and_parents():
            h = p.h
            if h.startswith('@rst') and not h.startswith('@rst-'):
                self.processTree(p,ext=None,toString=False,justOneFile=justOneFile)
                break
            elif h.startswith('@slides'):
                self.processTree(p,ext=None,toString=False,justOneFile=False)
                break
        else:
            self.processTree(current,ext=None,toString=False,justOneFile=justOneFile)
        g.blue('done')
    #@+node:ekr.20090502071837.63: *5* processTree
    def processTree(self,p,ext=None,toString=False,justOneFile=False):

        '''Process all @rst nodes in a tree.
        ext is the docutils extention: it's useful for scripts and unit tests.
        '''

        trace = False and not g.unitTesting
        if trace: g.trace(p.h)
        self.preprocessTree(p)
        found = False ; self.stringOutput = ''
        p = p.copy() ; after= p.nodeAfterTree()
        while p and p != after:
            h = p.h.strip()
            if g.match_word(h,0,"@rst"):
                self.rst_nodes.append(p.copy())
                fn = h[4:].strip()
                if ((fn and fn[0] != '-') or (toString and not fn)):
                    if trace: g.trace('found: %s',p.h)
                    found = True
                    self.write_rst_tree(p,ext,fn,toString=toString,justOneFile=justOneFile)
                    self.scanAllOptions(p) # Restore the top-level verbose setting.
                    if toString:
                        return p.copy(),self.stringOutput
                    p.moveToNodeAfterTree()
                else:
                    p.moveToThreadNext()
            elif g.match(h,0,"@slides"):
                self.write_slides(p)
                found = True
                p.moveToNodeAfterTree()
            else: p.moveToThreadNext()
        if not found:
            g.warning('No @rst or @slides nodes in selected tree')
        return None,None
    #@+node:ekr.20090502071837.64: *5* write_rst_tree
    def write_rst_tree (self,p,ext,fn,toString=False,justOneFile=False):

        '''Convert p's tree to rst sources.
        Optionally call docutils to convert rst to output.

        On exit:
            self.source contains rst sources
            self.stringOutput contains docutils output if docutils called.
        '''

        self.topNode = p.copy()
        self.topLevel = p.level()
        if toString:
            ext = ext or '.html' # 2010/08/12: Unit test found this.
        else:
            junk,ext = g.os_path_splitext(fn)
        ext = ext.lower()
        if not ext.startswith('.'): ext = '.' + ext

        # Init options...
        self.init_write(p) # ScanAllDirectives sets self.path and self.encoding.
        self.scanAllOptions(p) # Settings for p are valid after this call.
        callDocutils = self.getOption('call_docutils')
        # g.trace('callDocutils',callDocutils)
        writeIntermediateFile = self.getOption('write_intermediate_file')

        # Write the rst sources to self.source.
        self.outputFile = StringIO()
        self.writeTree(p,fn)
        self.source = self.outputFile.getvalue() # the rST sources.
        self.outputFile = None
        self.stringOutput = None

        if callDocutils or writeIntermediateFile:
            self.write_files(ext,fn,callDocutils,toString,writeIntermediateFile)
    #@+node:ekr.20100822092546.5835: *5* write_slides & helper
    def write_slides (self,p,toString=False):

        '''Convert p's children to slides.'''

        p = p.copy() ; h = p.h
        i = g.skip_id(h,1) # Skip the '@'
        kind,fn = h[:i].strip(),h[i:].strip()
        if not fn: return g.error('%s requires file name' % (kind))
        title = p and p.firstChild().h or '<no slide>'
        title = title.strip().capitalize()
        n_tot = p.numberOfChildren()

        n = 1
        for child in p.children():
            self.init_write(p) # ScanAllDirectives sets self.path and self.encoding.
            self.scanAllOptions(child) # Settings for child are valid after this call.
            # Compute the slide's file name.
            fn2,ext = g.os_path_splitext(fn)
            fn2 = '%s-%03d%s' % (fn2,n,ext) # Use leading zeros for :glob:.
            n += 1
            # Write the rst sources to self.source.
            self.outputFile = StringIO()
            self.writeSlideTitle(title,n-1,n_tot)
            self.writeBody(child)
            self.source = self.outputFile.getvalue() # the rST sources.
            self.outputFile,self.stringOutput = None,None
            self.write_files(ext,fn2,
                callDocutils=self.getOption('call_docutils'),
                toString=toString,
                writeIntermediateFile=self.getOption('write_intermediate_file'))
    #@+node:ekr.20100822174725.5836: *6* writeSlideTitle
    def writeSlideTitle (self,title,n,n_tot):

        '''Write the title, underlined with the '#' character.'''

        if n != 1:
            title = '%s (%s of %s)' % (title,n,n_tot)

        width = max(4,len(g.toEncodedString(title,
            encoding=self.encoding,reportErrors=False)))

        self.write('%s\n%s \n\n' % (title,('#'*width)))
    #@+node:ekr.20090502071837.58: *5* write methods (rst3 command)
    #@+node:ekr.20090502071837.68: *6* getDocPart
    def getDocPart (self,lines,n):

        # g.trace('n',n,repr(''.join(lines)))

        result = []
        #@+<< Append whatever follows @doc or @space to result >>
        #@+node:ekr.20090502071837.69: *7* << Append whatever follows @doc or @space to result >>
        if n > 0:
            line = lines[n-1]
            if line.startswith('@doc'):
                s = line[4:].lstrip()
            elif line.startswith('@'):
                s = line[1:].lstrip()
            else:
                s = ''

            # New in Leo 4.4.4: remove these special tags.
            for tag in ('@rst-options','@rst-option','@rst-markup'):
                if g.match_word(s,0,tag):
                    s = s[len(tag):].strip()

            if s.strip():
                result.append(s)
        #@-<< Append whatever follows @doc or @space to result >>
        while n < len(lines):
            s = lines [n] ; n += 1
            if g.match_word(s,0,'@code') or g.match_word(s,0,'@c'):
                break
            result.append(s)
        return n, result
    #@+node:ekr.20090502071837.81: *6* handleSpecialDocParts
    def handleSpecialDocParts (self,lines,kind,retainContents,asClass=None):

        # g.trace(kind,g.listToString(lines))

        result = [] ; n = 0
        while n < len(lines):
            s = lines [n] ; n += 1
            if s.strip().endswith('::'):
                n, lit = self.skip_literal_block(lines,n-1)
                result.extend(lit)
            elif self.isSpecialDocPart(s,kind):
                n, lines2 = self.getDocPart(lines,n)
                if retainContents:
                    result.extend([''])
                    if asClass:
                        result.extend(['.. container:: '+asClass, ''])
                        if 'literal' in asClass.split():
                            result.extend(['  ::', ''])
                        for l2 in lines2: result.append('    '+l2)
                    else:
                        result.extend(lines2)
                    result.extend([''])
            else:
                result.append(s)

        return result
    #@+node:ekr.20090502071837.77: *6* isAnyDocPart
    def isAnyDocPart (self,s):

        if s.startswith('@doc'):
            return True
        elif not s.startswith('@'):
            return False
        else:
            return len(s) == 1 or s[1].isspace()
    #@+node:ekr.20090502071837.79: *6* isAnySpecialDocPart
    def isAnySpecialDocPart (self,s):

        for kind in (
            '@rst-markup',
            '@rst-option',
            '@rst-options',
        ):
            if self.isSpecialDocPart(s,kind):
                return True

        return False
    #@+node:ekr.20090502071837.78: *6* isSpecialDocPart
    def isSpecialDocPart (self,s,kind):

        '''Return True if s is a special doc part of the indicated kind.

        If kind is None, return True if s is any doc part.'''

        if s.startswith('@') and len(s) > 1 and s[1].isspace():
            if kind:
                i = g.skip_ws(s,1)
                result = g.match_word(s,i,kind)
            else:
                result = True
        elif not kind:
            result = g.match_word(s,0,'@doc') or g.match_word(s,0,'@')
        else:
            result = False

        # g.trace('kind %s, result %s, s %s' % (
            # repr(kind),result,repr(s)))

        return result
    #@+node:ekr.20090502071837.80: *6* removeLeoDirectives
    def removeLeoDirectives (self,lines):

        '''Remove all Leo directives, except within literal blocks.'''

        n = 0 ; result = []
        while n < len(lines):
            s = lines [n] ; n += 1
            if s.strip().endswith('::'):
                n, lit = self.skip_literal_block(lines,n-1)
                result.extend(lit)
            elif s.startswith('@') and not self.isAnySpecialDocPart(s):
                for key in self.leoDirectivesList:
                    if g.match_word(s,1,key):
                        # g.trace('removing %s' % s)
                        break
                else:
                    result.append(s)
            else:
                result.append(s)

        return result
    #@+node:ekr.20090502071837.82: *6* replaceCodeBlockDirectives
    def replaceCodeBlockDirectives (self,lines):

        '''Replace code-block directive, but not in literal blocks.'''

        n = 0 ; result = []
        while n < len(lines):
            s = lines [n] ; n += 1
            if s.strip().endswith('::'):
                n, lit = self.skip_literal_block(lines,n-1)
                result.extend(lit)
            else:
                i = g.skip_ws(s,0)
                if g.match(s,i,'..'):
                    i = g.skip_ws(s,i+2)
                    if g.match_word(s,i,'code-block'):
                        if 1: # Create a literal block to hold the code.
                            result.append('::\n')
                        else: # This 'annotated' literal block is confusing.
                            result.append('%s code::\n' % s[i+len('code-block'):])
                    else:
                        result.append(s)
                else:
                    result.append(s)

        return result
    #@+node:ekr.20090502071837.70: *6* skip_literal_block
    def skip_literal_block (self,lines,n):

        s = lines[n] ; result = [s] ; n += 1
        indent = g.skip_ws(s,0)

        # Skip lines until a non-blank line is found with same or less indent.
        while n < len(lines):
            s = lines[n]
            indent2 = g.skip_ws(s,0)
            if s and not s.isspace() and indent2 <= indent:
                break # We will rescan lines [n]
            n += 1
            result.append(s)

        # g.printList(result,tag='literal block')
        return n, result
    #@+node:ekr.20090502071837.71: *6* writeBody & helpers
    def writeBody (self,p):

        trace = False and not g.unitTesting

        if self.getOption('ignore_noweb_definitions'):
            # 2011/06/10: Ignore section definition nodes.
            name = self.isSectionDef(p)
            if name:
                if trace: g.trace('section def: %s' % (repr(name)))
                return

        # remove trailing cruft and split into lines.
        lines = g.splitLines(p.b)

        if self.getOption('code_mode'):
            # Important: code mode is no longer documented!
            if not self.getOption('show_options_doc_parts'):
                lines = self.handleSpecialDocParts(lines,'@rst-options',
                    retainContents=False)
            if not self.getOption('show_markup_doc_parts'):
                lines = self.handleSpecialDocParts(lines,'@rst-markup',
                    retainContents=False)
            # g.trace(self.getOption('show_leo_directives'))
            if not self.getOption('show_leo_directives'):
                lines = self.removeLeoDirectives(lines)
            lines = self.handleCodeMode(lines)
        elif self.getOption('doc_only_mode'):
            # New in version 1.15
            lines = self.handleDocOnlyMode(p,lines)
        else:
            lines = self.handleSpecialDocParts(lines,'@rst-options',
                retainContents=False)
            lines = self.handleSpecialDocParts(lines,'@rst-markup',
                retainContents=self.getOption('generate_rst'))
            if self.getOption('show_doc_parts_in_rst_mode') is True:
                pass  # original behaviour, treat as plain text
            elif self.getOption('show_doc_parts_in_rst_mode'):
                # use value as class for content
                lines = self.handleSpecialDocParts(lines,None,
                    retainContents=True, asClass=self.getOption('show_doc_parts_in_rst_mode'))
            else:  # option evaluates to false, cut them out
                lines = self.handleSpecialDocParts(lines,None,
                    retainContents=False)
            lines = self.removeLeoDirectives(lines)
            if self.getOption('expand_noweb_references'):
                # 2011/06/10.
                lines = self.expandSectionRefs(lines,p,seen=[])
            if self.getOption('generate_rst') and self.getOption('use_alternate_code_block'):
                lines = self.replaceCodeBlockDirectives(lines)

        # Write the lines.
        s = ''.join(lines)

        # We no longer add newlines to the start of nodes because
        # we write a blank line after all sections.
        # s = g.ensureLeadingNewlines(s,1)
        s = g.ensureTrailingNewlines(s,2)
        self.write(s)
    #@+node:ekr.20110610144305.6749: *7* isSectionDef/Ref
    def isSectionDef (self,p):

        return self.isSectionRef(p.h)

    def isSectionRef (self,s):

        n1 = s.find("<<",0)
        n2 = s.find(">>",0)
        return -1 < n1 < n2 and s[n1+2:n2].strip()
    #@+node:ekr.20110610144305.6750: *7* expandSectionRefs
    def expandSectionRefs (self,lines,p,seen):

        trace = False and not g.unitTesting

        if trace: g.trace(p.h,g.callers())

        result = []
        for s in lines:
            name = self.isSectionRef(s)
            if name:
                p2 = self.findSectionDef(name,p)
                if p2:
                    g.trace('expanding: %s from %s' % (name,p2.h))
                    result.append(s) # Append the section reference line.
                    lines2 = g.splitLines(p2.b)
                    if self.getOption('expand_noweb_recursively'):
                        if name in seen:
                            pass # Prevent unbounded recursion
                        else:
                            seen.append(name)
                            result.extend(self.expandSectionRefs(lines2,p,seen))
                    else:
                        result.extend(lines2)
                else:
                    # Undefined reference.
                    result.append(s)
            else:
                result.append(s)

        return result
    #@+node:ekr.20110610144305.6751: *7* findSectionDef
    def findSectionDef (self,name,p):

        for p2 in p.subtree():
            name2 = self.isSectionDef(p2)
            if name2:
                return p2

        return None
    #@+node:ekr.20090502071837.72: *7* handleCodeMode & helper
    def handleCodeMode (self,lines):

        '''Handle the preprocessed body text in code mode as follows:

        - Blank lines are copied after being cleaned.
        - @ @rst-markup lines get copied as is.
        - Everything else gets put into a code-block directive.'''

        trace = False and not g.unitTesting
        result = [] ; n = 0 ; code = []
        while n < len(lines):
            s = lines [n] ; n += 1
            if (
                self.isSpecialDocPart(s,'@rst-markup') or (
                    self.getOption('show_doc_parts_as_paragraphs') and
                    self.isSpecialDocPart(s,None)
                )
            ):
                if code:
                    self.finishCodePart(result,code)
                    code = []
                result.append('')
                n, lines2 = self.getDocPart(lines,n)
                # A fix, perhaps dubious, to a bug discussed at
                # http://groups.google.com/group/leo-editor/browse_thread/thread/c212814815c92aac
                # lines2 = [z.lstrip() for z in lines2]
                # g.trace('lines2',lines2)
                result.extend(lines2)
            elif not s.strip() and not code:
                pass # Ignore blank lines before the first code block.
            else:
                if not code: # Start the code block.
                    result.append('')
                    result.append(self.code_block_string)

                if trace: g.trace('code line: %s' % repr(s))
                code.append(s)

            # elif not code: # Start the code block.
                # result.append('')
                # result.append(self.code_block_string)
                # if trace: g.trace('code line: %s' % repr(s))
                # code.append(s)
            # else: # Continue the code block.
                # if trace: g.trace('code line: %s' % repr(s))
                # code.append(s)

        if code:
            self.finishCodePart(result,code)
            code = []

        # Munge the result so as to keep docutils happy.
        # Don't use self.rstripList: it's not the same.
        # g.trace(result)
        result2 = []
        for z in result:
            if z == '': result2.append('\n\n')
            # 2010/08/27: Fix bug 618482.
            # elif not z.rstrip(): pass
            elif z.endswith('\n\n'): result2.append(z) # Leave alone.
            else: result2.append('%s\n' % z.rstrip())

        return result2
    #@+node:ekr.20090502071837.73: *8* formatCodeModeLine
    def formatCodeModeLine (self,s,n,numberOption):

        if not s.strip(): s = ''

        if numberOption:
            return '\t%d: %s' % (n,s)
        else:
            return '\t%s' % s
    #@+node:ekr.20090502071837.74: *8* rstripList
    def rstripList (self,theList):

        '''Removed trailing blank lines from theList.'''

        # 2010/08/27: fix bug 618482.
        s = ''.join(theList).rstrip()
        return s.split('\n')
    #@+node:ekr.20090502071837.75: *8* finishCodePart
    def finishCodePart (self,result,code):

        numberOption = self.getOption('number_code_lines')
        code = self.rstripList(code)
        i = 0
        for line in code:
            i += 1
            result.append(self.formatCodeModeLine(line,i,numberOption))
    #@+node:ekr.20090502071837.76: *7* handleDocOnlyMode
    def handleDocOnlyMode (self,p,lines):

        '''Handle the preprocessed body text in doc_only mode as follows:

        - Blank lines are copied after being cleaned.
        - @ @rst-markup lines get copied as is.
        - All doc parts get copied.
        - All code parts are ignored.'''

        # ignore            = self.getOption('ignore_this_headline')
        showHeadlines       = self.getOption('show_headlines')
        showThisHeadline    = self.getOption('show_this_headline')
        showOrganizers      = self.getOption('show_organizer_nodes')
        result = [] ; n = 0
        while n < len(lines):
            s = lines [n] ; n += 1
            if self.isSpecialDocPart(s,'@rst-options'):
                n, lines2 = self.getDocPart(lines,n) # ignore.
            elif self.isAnyDocPart(s):
                # Handle any other doc part, including @rst-markup.
                n, lines2 = self.getDocPart(lines,n)
                if lines2: result.extend(lines2)
        if not result: result = []
        if showHeadlines:
            if result or showThisHeadline or showOrganizers or p == self.topNode:
                # g.trace(len(result),p.h)
                self.writeHeadlineHelper(p)
        return result
    #@+node:ekr.20090502071837.83: *6* writeHeadline & helper
    def writeHeadline (self,p):

        '''Generate an rST section if options permit it.
        Remove headline commands from the headline first,
        and never generate an rST section for @rst-option and @rst-options.'''

        docOnly             = self.getOption('doc_only_mode')
        ignore              = self.getOption('ignore_this_headline')
        ignoreNowebDefs     = self.getOption('ignore_noweb_definitions')
        showHeadlines       = self.getOption('show_headlines')
        showOrganizers      = self.getOption('show_organizer_nodes')
        showThisHeadline    = self.getOption('show_this_headline')

        if (
            p == self.topNode or
            ignore or
            docOnly or # handleDocOnlyMode handles this.
            not showHeadlines and not showThisHeadline or
            # docOnly and not showOrganizers and not thisHeadline or
            not p.h.strip() and not showOrganizers or
            not p.b.strip() and not showOrganizers or
            ignoreNowebDefs and self.isSectionDef(p) # 2011/06/10.
        ):
            return

        self.writeHeadlineHelper(p)
    #@+node:ekr.20090502071837.84: *7* writeHeadlineHelper
    def writeHeadlineHelper (self,p):

        h = p.h
        if not self.atAutoWrite:
            h = h.strip()

        # Remove any headline command before writing the headline.
        i = g.skip_ws(h,0)
        i = g.skip_id(h,0,chars='@-')
        word = h [:i].strip()
        if word:
            # Never generate a section for these...
            if word in (
                '@rst-option','@rst-options',
                '@rst-no-head','@rst-no-headlines'
            ):
                return

            # Remove all other headline commands from the headline.
            for command in self.headlineCommands:
                if word == command:
                    h = h [len(word):].strip()
                    break

            # New in Leo 4.4.4.
            if word.startswith('@'):
                if self.getOption('strip_at_file_prefixes'):
                    for s in ('@auto','@file','@nosent','@thin',):
                        if g.match_word(word,0,s):
                            h = h [len(s):].strip()

        if not h.strip(): return

        if self.getOption('show_sections'):
            if self.getOption('generate_rst'):
                self.write(self.underline(h,p)) # Used by @auto-rst.
            else:
                self.write('\n%s\n\n' % h)
        else:
            self.write('\n**%s**\n\n' % h.replace('*',''))
    #@+node:ekr.20090502071837.85: *6* writeNode (leoRst)
    def writeNode (self,p):

        '''Format a node according to the options presently in effect.'''

        self.initCodeBlockString(p)
        self.scanAllOptions(p)

        if 0:
            g.trace('%24s code_mode %s' % (p.h,self.getOption('code_mode')))

        h = p.h.strip()

        if self.getOption('preformat_this_node'):
            self.http_addNodeMarker(p)
            self.writePreformat(p)
            p.moveToThreadNext()
        elif self.getOption('ignore_this_tree'):
            p.moveToNodeAfterTree()
        elif self.getOption('ignore_this_node'):
            p.moveToThreadNext()
        elif g.match_word(h,0,'@rst-options') and not self.getOption('show_options_nodes'):
            p.moveToThreadNext()
        else:
            self.http_addNodeMarker(p)
            self.writeHeadline(p)
            self.writeBody(p)
            p.moveToThreadNext()
    #@+node:ekr.20090502071837.86: *6* writePreformat
    def writePreformat (self,p):

        '''Write p's body text lines as if preformatted.

         ::

            line 1
            line 2 etc.
        '''

        # g.trace(p.h,g.callers())

        lines = p.b.split('\n')
        lines = [' '*4 + z for z in lines]
        lines.insert(0,'::\n')

        s = '\n'.join(lines)
        if s.strip():
            self.write('%s\n\n' % s)
    #@+node:ekr.20090502071837.87: *6* writeTree
    def writeTree(self,p,fn):

        '''Write p's tree to self.outputFile.'''

        self.scanAllOptions(p)

        if self.getOption('generate_rst'):
            if self.getOption('generate_rst_header_comment'):
                self.write(self.rstComment(
                    'rst3: filename: %s\n\n' % fn))

        # We can't use an iterator because we may skip parts of the tree.
        p = p.copy() # Only one copy is needed for traversal.
        after = p.nodeAfterTree()
        while p and p != after:
            self.writeNode(p) # Side effect: advances p.
    #@+node:ekr.20090502071837.67: *4* writeNodeToString
    def writeNodeToString (self,p=None,ext=None):

        '''Scan p's tree (defaults to presently selected tree) looking for @rst nodes.
        Convert the first node found to an ouput of the type specified by ext.

        The @rst may or may not be followed by a filename; the filename is *ignored*,
        and its type does not affect ext or the output generated in any way.

        ext should start with a period: .html, .tex or None (specifies rst output).

        Returns (p, s), where p is the position of the @rst node and s is the converted text.'''

        c = self.c ; current = p or c.p

        for p in current.self_and_parents():
            if p.h.startswith('@rst'):
                return self.processTree(p,ext=ext,toString=True,justOneFile=True)
        else:
            return self.processTree(current,ext=ext,toString=True,justOneFile=True)
    #@+node:ekr.20090512153903.5803: *4* writeAtAutoFile
    def writeAtAutoFile (self,p,fileName,outputFile,trialWrite=False):

        '''Write an @auto tree containing imported rST code.
        The caller will close the output file.'''

        try:
            self.trialWrite = trialWrite
            self.atAutoWrite = True
            self.initAtAutoWrite(p,fileName,outputFile)
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
    #@+node:ekr.20090513073632.5733: *5* initAtAutoWrite (rstCommands)
    def initAtAutoWrite(self,p,fileName,outputFile):

        # Set up for a standard write.
        self.createDefaultOptionsDict()
        self.nodeOptionDict = {}
        self.scanAllOptions(p)
        self.init_write(p)
        self.preprocessTree(p) # Allow @ @rst-options, for example.
        # Do the overrides.
        self.outputFile = outputFile
        # Set underlining characters.
        # It makes no sense to use user-defined
        # underlining characters in @auto-rst.
        d = p.v.u.get('rst-import',{})
        underlines2 = d.get('underlines2','')
            # Do *not* set a default for overlining characters.
        if len(underlines2) > 1:
            underlines2 = underlines2[0]
            g.warning('too many top-level underlines, using %s' % (underlines2))
        underlines1 = d.get('underlines1','')
        # Bug fix:  2010/05/26: pad underlines with default characters.
        default_underlines = '=+*^~"\'`-:><_'
        if underlines1:
            for ch in default_underlines[1:]:
                if ch not in underlines1:
                    underlines1 = underlines1 + ch
        else:
            underlines1 = default_underlines
        self.atAutoWriteUnderlines   = underlines2 + underlines1
        self.underlines1 = underlines1
        self.underlines2 = underlines2
    #@+node:ekr.20091228080620.6499: *5* isSafeWrite
    def isSafeWrite (self,p):

        '''Return True if node p contributes nothing but
        rst-options to the write.'''

        if self.trialWrite or not p.isAtAutoRstNode():
            return True # Trial writes are always safe.

        lines = g.splitLines(p.b)
        for z in lines:
            if z.strip() and not z.startswith('@') and not z.startswith('.. '):
                # A real line that will not be written.
                g.error('unsafe @auto-rst')
                g.es('body text will be ignored in\n',p.h)
                return False
        else:
            return True
    #@+node:ekr.20090502071837.41: *3* Options
    #@+node:ekr.20090502071837.42: *4* createDefaultOptionsDict
    def createDefaultOptionsDict(self):

        # Important: these must be munged names.
        self.defaultOptionsDict = {
            # Http options...
            'clear_http_attributes':   False,
            'http_server_support':     False,
            'http_attributename':      'rst_http_attribute',
            'node_begin_marker':       'http-node-marker-',
            # Path options...
            'default_path': None, # New in Leo 4.4a4 # Bug fix: must be None, not ''.
            'stylesheet_name': 'default.css',
            'stylesheet_path': None, # Bug fix: must be None, not ''.
            'stylesheet_embed': True,
            'publish_argv_for_missing_stylesheets': None,
            # Global options...
            'call_docutils': True, # 2010/08/05
            'code_block_string': '',
            'number_code_lines': True,
            'underline_characters': '''#=+*^~"'`-:><_''',
            'verbose':True,
            'write_intermediate_file': False, # Used only if generate_rst is True.
            'write_intermediate_extension': '.txt',
            # Mode options...
            'code_mode': False, # True: generate rst markup from @code and @doc parts.
            'doc_only_mode': False, # True: generate only from @doc parts.
            'generate_rst': True, # True: generate rst markup.  False: generate plain text.
            'generate_rst_header_comment': True,
                # True generate header comment (requires generate_rst option)
            # Formatting options that apply to both code and rst modes....
            'expand_noweb_references': False,
            'ignore_noweb_definitions': False,
            'expand_noweb_recursively': True,
            'show_headlines': True,  # Can be set by @rst-no-head headlines.
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
    #@+node:ekr.20090502071837.43: *4* dumpSettings (debugging)
    def dumpSettings (self):

        d = self.optionsDict
        keys = sorted(d)

        g.pr('present settings...')
        for key in keys:
            g.pr('%20s %s' % (key,d.get(key)))
    #@+node:ekr.20090502071837.44: *4* getOption & setOption
    def getOption (self,name):

        # 2010/08/12: munging names here is safe because setOption munges.
        # g.trace(name,self.optionsDict.get(self.munge(name)))
        return self.optionsDict.get(self.munge(name))

    def setOption (self,name,val,tag=None):

        # if self.munge(name) == 'call_docutils':
            # g.trace(name,val,'tag:',tag)
        self.optionsDict [self.munge(name)] = val
    #@+node:ekr.20090502071837.45: *4* initCodeBlockString
    def initCodeBlockString(self,p):

        trace = False and not g.unitTesting
        c = self.c
        # if trace: os.system('cls')
        d = c.scanAllDirectives(p)
        language = d.get('language')
        if language is None: language = 'python'
        else: language = language.lower()
        syntax = SilverCity is not None

        if trace: g.trace('language',language,'language.title()',language.title(),p.h)

        # Note: lines that end with '\n\n' are a signal to handleCodeMode.
        s = self.getOption('code_block_string')
        if s:
            self.code_block_string = s.replace('\\n','\n')
        elif syntax and language in ('python','ruby','perl','c'):
            self.code_block_string = '**code**:\n\n.. code-block:: %s\n\n' % (
                language.title())
        else:
            self.code_block_string = '**code**:\n\n.. class:: code\n..\n\n::\n\n'
    #@+node:ekr.20090502071837.46: *4* preprocessTree & helpers
    def preprocessTree (self,root):

        self.nodeOptionDict = {}

        # Bug fix 12/4/05: must preprocess parents too.
        for p in root.parents():
            self.preprocessNode(p)

        for p in root.self_and_subtree():
            self.preprocessNode(p)

        if 0:
            g.trace(root.h)
            for key in self.nodeOptionDict.keys():
                g.trace(key)
                g.printDict(self.nodeOptionDict.get(key))
    #@+node:ekr.20090502071837.47: *5* preprocessNode
    def preprocessNode (self,p):

        d = self.nodeOptionDict.get(p.v)
        if d is None:
            d = self.scanNodeForOptions(p)
            self.nodeOptionDict [p.v] = d
    #@+node:ekr.20090502071837.48: *5* parseOptionLine
    def parseOptionLine (self,s):

        '''Parse a line containing name=val and return (name,value) or None.

        If no value is found, default to True.'''

        s = s.strip()
        if s.endswith(','): s = s[:-1]
        # Get name.  Names may contain '-' and '_'.
        i = g.skip_id(s,0,chars='-_')
        name = s [:i]
        if not name: return None
        j = g.skip_ws(s,i)
        if g.match(s,j,'='):
            val = s [j+1:].strip()
            # g.trace(val)
            return name,val
        else:
            # g.trace('*True')
            return name,'True'
    #@+node:ekr.20090502071837.49: *5* scanForOptionDocParts
    def scanForOptionDocParts (self,p,s):

        '''Return a dictionary containing all options from @rst-options doc parts in p.
        Multiple @rst-options doc parts are allowed: this code aggregates all options.
        '''

        d = {} ; n = 0 ; lines = g.splitLines(s)
        while n < len(lines):
            line = lines[n] ; n += 1
            if line.startswith('@'):
                i = g.skip_ws(line,1)
                for kind in ('@rst-options','@rst-option'):
                    if g.match_word(line,i,kind):
                        # Allow options on the same line.
                        line = line[i+len(kind):]
                        d.update(self.scanOption(p,line))
                        # Add options until the end of the doc part.
                        while n < len(lines):
                            line = lines[n] ; n += 1 ; found = False
                            for stop in ('@c','@code', '@'):
                                if g.match_word(line,0,stop):
                                    found = True ; break
                            if found:
                                break
                            else:
                                d.update(self.scanOption(p,line))
                        break
        return d
    #@+node:ekr.20090502071837.50: *5* scanHeadlineForOptions
    def scanHeadlineForOptions (self,p):

        '''Return a dictionary containing the options implied by p's headline.'''

        h = p.h.strip()

        if p == self.topNode:
            return {} # Don't mess with the root node.
        elif g.match_word(h,0,'@rst-option'):
            s = h [len('@rst-option'):]
            return self.scanOption(p,s)
        elif g.match_word(h,0,'@rst-options'):
            return self.scanOptions(p,p.b)
        else:
            # Careful: can't use g.match_word because options may have '-' chars.
            i = g.skip_id(h,0,chars='@-')
            word = h[0:i]

            for option,ivar,val in (
                ('@rst',                'code_mode',False),
                ('@rst-code',           'code_mode',True),
                ('@rst-default-path',   'default_prefix',''),
                ('@rst-doc-only',       'doc_only_mode',True),
                ('@rst-head',           'show_this_headline',True),
                # ('@rst-head' ,        'show_headlines',False),
                ('@rst-ignore',         'ignore_this_tree',True),
                ('@rst-ignore-node',    'ignore_this_node',True),
                ('@rst-ignore-tree',    'ignore_this_tree',True),
                ('@rst-no-head',        'ignore_this_headline',True),
                ('@rst-preformat',      'preformat_this_node',True),
            ):
                if word == option:
                    d = { ivar: val }
                    # Special case: code mode and doc-only modes are linked.
                    if ivar == 'code_mode':
                        d ['doc_only_mode'] = False
                    elif ivar == 'doc_only_mode':
                        d ['code_mode'] = False
                    # Special case: Treat a bare @rst like @rst-no-head
                    if h == '@rst':
                        d ['ignore_this_headline'] = True
                    # g.trace(repr(h),d)
                    return d

            if h.startswith('@rst'):
                g.trace('unknown kind of @rst headline',p.h,g.callers(4))

            return {}
    #@+node:ekr.20090502071837.51: *5* scanNodeForOptions
    def scanNodeForOptions (self,p):

        '''Return a dictionary containing all the option-name:value entries in p.

        Such entries may arise from @rst-option or @rst-options in the headline,
        or from @ @rst-options doc parts.'''

        trace = False and not g.unitTesting

        h = p.h

        d = self.scanHeadlineForOptions(p)

        d2 = self.scanForOptionDocParts(p,p.b)

        # A fine point: body options over-ride headline options.
        d.update(d2)

        if trace and d:
            g.trace(h)
            for z in sorted(d):
                print('    %s: %s' % (z,d.get(z)))

        return d
    #@+node:ekr.20090502071837.52: *5* scanOption
    def scanOption (self,p,s):

        '''Return { name:val } if s is a line of the form name=val.
        Otherwise return {}'''

        if not s.strip() or s.strip().startswith('..'): return {}

        data = self.parseOptionLine(s)

        if data:
            name,val = data
            if self.munge(name) in list(self.defaultOptionsDict.keys()):
                if   val.lower() == 'true': val = True
                elif val.lower() == 'false': val = False
                # g.trace('%24s %8s %s' % (self.munge(name),val,p.h))
                return { self.munge(name): val }
            else:
                g.error('ignoring unknown option:',name)
                return {}
        else:
            g.trace(repr(s))
            g.error('bad rst3 option',s,'in',p.h)
            return {}
    #@+node:ekr.20090502071837.53: *5* scanOptions
    def scanOptions (self,p,s):

        '''Return a dictionary containing all the options in s.'''

        d = {}

        for line in g.splitLines(s):
            d2 = self.scanOption(p,line)
            if d2: d.update(d2)

        return d
    #@+node:ekr.20090502071837.54: *4* scanAllOptions & helpers
    # Once an option is seen, no other related options in ancestor nodes have any effect.

    def scanAllOptions(self,p):

        '''Scan position p and p's ancestors looking for options,
        setting corresponding ivars.
        '''

        self.initOptionsFromSettings() # Must be done on every node.
        self.handleSingleNodeOptions(p)
        seen = self.singleNodeOptions[:] # Suppress inheritance of single-node options.

        # g.trace('-'*20)
        for p in p.self_and_parents():
            d = self.nodeOptionDict.get(p.v,{})
            # g.trace(p.h,d)
            for key in d.keys():
                ivar = self.munge(key)
                if not ivar in seen:
                    seen.append(ivar)
                    val = d.get(key)
                    self.setOption(key,val,p.h)

        if self.rst3_all:
            self.setOption("generate_rst", True, "rst3_all")
            self.setOption("generate_rst_header_comment",True, "rst3_all")
            self.setOption("http_server_support", True, "rst3_all")
            self.setOption("write_intermediate_file", True, "rst3_all")
    #@+node:ekr.20090502071837.55: *5* initOptionsFromSettings
    def initOptionsFromSettings (self):

        c = self.c
        d = self.defaultOptionsDict
        keys = sorted(d)
        for key in keys:
            for getter,kind in (
                (c.config.getBool,'@bool'),
                (c.config.getString,'@string'),
                (d.get,'default'),
            ):
                # 2013/10/09: major bug fix: prefix 'rst3_' to c.config names!
                if kind == 'default':
                    val = getter(key)
                else:
                    val = getter('rst3_'+key)
                if kind == 'default' or val is not None:
                    # if key == 'call_docutils':
                        # g.trace(key,val,c,getter)
                        # g.trace(c.config.getBool('rst3_call_docutils'))
                    self.setOption(key,val,'initOptionsFromSettings')
                    break

        # 2010/08/12: Script settings override everything else.
        d2 = self.scriptSettingsDict or {}
        for key in d2.keys():
            val = d2.get(key)
            # g.trace(key,val)
            self.setOption(key,val,'initOptionsFromSettings')

        # Special case.
        if self.getOption('http_server_support') and not mod_http:
            g.error('No http_server_support: can not import mod_http plugin')
            self.setOption('http_server_support',False)
    #@+node:ekr.20090502071837.56: *5* handleSingleNodeOptions
    def handleSingleNodeOptions (self,p):

        '''Init the settings of single-node options from the tnodeOptionsDict.

        All such options default to False.'''

        d = self.nodeOptionDict.get(p.v, {} )

        for ivar in self.singleNodeOptions:
            val = d.get(ivar,False)
            #g.trace('%24s %8s %s' % (ivar,val,p.h))
            self.setOption(ivar,val,p.h)

    #@+node:ekr.20090502071837.59: *3* Shared write code
    #@+node:ekr.20090502071837.96: *4* http_addNodeMarker
    def http_addNodeMarker (self,p):

        if (
            self.getOption('http_server_support') and
            self.getOption('generate_rst')
        ):
            self.nodeNumber += 1
            anchorname = "%s%s" % (self.getOption('node_begin_marker'),self.nodeNumber)
            s = "\n\n.. _%s:\n\n" % anchorname
            self.write(s)
            self.http_map [anchorname] = p.copy()
            # if bwm_file: print >> bwm_file, "addNodeMarker", anchorname, p
    #@+node:ekr.20090502071837.97: *4* http_endTree & helpers
    # Was http_support_main

    def http_endTree (self,filename,p,justOneFile):

        '''Do end-of-tree processing to support the http plugin.'''

        if (
            self.getOption('http_server_support') and
            self.getOption('generate_rst')
        ):
            self.set_initial_http_attributes(filename)
            self.find_anchors(p)
            if justOneFile:
                self.relocate_references(p.self_and_subtree)

            g.blue('html updated for http plugin')

            if self.getOption('clear_http_attributes'):
                g.es_print("http attributes cleared")
    #@+node:ekr.20090502071837.98: *5* set_initial_http_attributes
    def set_initial_http_attributes (self,filename):

        f = open(filename)
        parser = htmlParserClass(self)

        for line in f.readlines():
            parser.feed(line)

        f.close()
    #@+node:ekr.20090502071837.100: *5* relocate_references
    #@+at Relocate references here if we are only running for one file.
    # 
    # Otherwise we must postpone the relocation until we have processed all files.
    #@@c

    def relocate_references (self, iterator_generator):

        for p in iterator_generator():
            attr = mod_http.get_http_attribute(p)
            if not attr:
                continue
            # g.trace('before',p.h,attr)
            # if bwm_file:
                # print >> bwm_file
                # print >> bwm_file, "relocate_references(1): Position, attr:"
                # pprint.pprint((p, attr), bwm_file)
                # http_lines = attr [3:]
            parser = link_htmlparserClass(self,p)
            for line in attr [3:]:
                try:
                    parser.feed(line)
                except:
                    line = ''.join([ch for ch in line if ord(ch) <= 127])
                    parser.feed(line)
            replacements = parser.get_replacements()
            replacements.reverse()
            if not replacements:
                continue
            # if bwm_file:
                # print >> bwm_file, "relocate_references(2): Replacements:"
                # pprint.pprint(replacements, bwm_file)
            for line, column, href, href_file, http_node_ref in replacements:
                # if bwm_file: 
                    # print >> bwm_file, "relocate_references(3): line:", line,
                    # "Column:", column, "href:", href, "href_file:",
                    # href_file, "http_node_ref:", http_node_ref
                marker_parts = href.split("#")
                if len(marker_parts) == 2:
                    marker = marker_parts [1]
                    # replacement = u"%s#%s" % (http_node_ref,marker)
                    replacement = '%s#%s' % (http_node_ref,marker)
                    try:
                        # attr [line + 2] = attr [line + 2].replace(u'href="%s"' % href, u'href="%s"' % replacement)
                        attr [line + 2] = attr [line + 2].replace('href="%s"' % href, 'href="%s"' % replacement)
                    except:
                        g.es("Skipped ", attr[line + 2])
                else:
                    # filename = marker_parts [0]
                    try:
                        attr [line + 2] = attr [line + 2].replace('href="%s"' % href,'href="%s"' % http_node_ref)
                    except:
                        g.es("Skipped", attr[line+2])
        # g.trace('after %s\n\n\n',attr)
    #@+node:ekr.20090502071837.99: *5* find_anchors
    def find_anchors (self, p):

        '''Find the anchors in all the nodes.'''

        for p1, attrs in self.http_attribute_iter(p):
            html = mod_http.reconstruct_html_from_attrs(attrs)
            # g.trace(pprint.pprint(html))
            parser = anchor_htmlParserClass(self, p1)
            for line in html:
                try:
                    parser.feed(line)
                # bwm: changed to unicode(line)
                except:
                    line = ''.join([ch for ch in line if ord(ch) <= 127])
                    # filter out non-ascii characters.
                    # bwm: not quite sure what's going on here.
                    parser.feed(line)        
        # g.trace(g.dictToString(self.anchor_map,tag='anchor_map'))
    #@+node:ekr.20090502071837.101: *5* http_attribute_iter
    def http_attribute_iter (self, p):
        """
        Iterator for all the nodes which have html code.
        Look at the descendents of p.
        Used for relocation.
        """

        for p1 in p.self_and_subtree():
            attr = mod_http.get_http_attribute(p1)
            if attr:
                yield (p1.copy(),attr)
    #@+node:ekr.20090502071837.60: *4* init_write (rstCommands)
    def init_write (self,p):

        self.initOptionsFromSettings() # Still needed.

        # Set the encoding from any parent @encoding directive.
        # This can be overridden by @rst-option encoding=whatever.
        c = self.c

        d = c.scanAllDirectives(p)
        self.encoding = d.get('encoding') or 'utf-8'
        self.path = d.get('path') or ''

        # g.trace('path:',self.path)
    #@+node:ekr.20090502071837.94: *4* write (leoRst)
    def write (self,s,theFile=None):

        if theFile is None:
            theFile = self.outputFile

        if g.isPython3:
            if g.is_binary_file(theFile):
                s = self.encode(s)
        else:
            s = self.encode(s)

        theFile.write(s)
    #@+node:ekr.20100813041139.5919: *4* write_files & helpers
    def write_files (self,ext,fn,callDocutils,toString,writeIntermediateFile):

        isHtml = ext in ('.html','.htm')
        fn = self.computeOutputFileName(fn)
        if not toString:
            if not self.createDirectoryForFile(fn):
                return

        if writeIntermediateFile:
            if not toString:
                self.createIntermediateFile(fn,self.source)

        if callDocutils and ext in ('.htm','.html','.tex','.pdf','.s5','.odt'):
            self.stringOutput = s = self.writeToDocutils(self.source,ext)
            if s and isHtml:
                self.stringOutput = s = self.addTitleToHtml(s)
            if not s: return

            if toString:
                if not g.isUnicode(s):
                    s = g.toUnicode(s,'utf-8')
            else:
                # Fixes bug 923301: Unicode error when executing 'rst3' command
                if g.isPython3:
                    s = g.toEncodedString(s,'utf-8')
                f = open(fn,'wb') # Bug fix: use 'wb'
                f.write(s)
                f.close()
                self.report(fn)
                # self.http_endTree(fn,p,justOneFile=justOneFile)
    #@+node:ekr.20100813041139.5913: *5* addTitleToHtml
    def addTitleToHtml(self,s):

        '''Replace an empty <title> element by the contents of
        the first <h1> element.'''

        i = s.find('<title></title>')
        if i == -1: return s

        m = re.search('<h1>([^<]*)</h1>', s)
        if not m:
            m = re.search('<h1><[^>]+>([^<]*)</a></h1>', s)
        if m:
            s = s.replace('<title></title>',
                '<title>%s</title>' % m.group(1))

        return s
    #@+node:ekr.20100813041139.5914: *5* createDirectoryForFile
    def createDirectoryForFile(self, fn):

        '''Create the directory for fn if
        a) it doesn't exist and
        b) the user options allow it.

        Return True if the directory existed or was made.'''

        c = self.c

        # Create the directory if it doesn't exist.
        theDir, junk = g.os_path_split(fn)
        theDir = c.os_path_finalize(theDir)

        if g.os_path_exists(theDir):
            return True
        else:
            ok = g.makeAllNonExistentDirectories(theDir,c=c,force=False)
            if not ok:
                g.error('did not create:',theDir)
            return ok
    #@+node:ekr.20100813041139.5912: *5* createIntermediateFile (changed)
    def createIntermediateFile(self,fn,s):

        '''Write s to to the file whose name is fn.'''

        ext = self.getOption('write_intermediate_extension')
        ext = ext or '.txt' # .txt by default.
        if not ext.startswith('.'): ext = '.' + ext

        fn = fn + ext

        # g.trace('intermediate file',fn)
        if g.isPython3:
            f = open(fn,'w',encoding=self.encoding)
        else:
            f = open(fn,'w')
        if not g.isPython3: # 2010/08/27
            s = g.toEncodedString(s,encoding=self.encoding,reportErrors=True)
        f.write(s)
        f.close()
        self.report(fn)
    #@+node:ekr.20090502071837.65: *5* writeToDocutils (sets argv) & helper
    def writeToDocutils (self,s,ext):

        '''Send s to docutils using the writer implied by ext and return the result.'''

        trace = False and not g.unitTesting
        if not docutils:
            g.error('writeToDocutils: docutils not present')
            return None
        openDirectory = self.c.frame.openDirectory
        overrides = {'output_encoding': self.encoding }
        # Compute the args list if the stylesheet path does not exist.
        styleSheetArgsDict = self.handleMissingStyleSheetArgs()
        if ext == '.pdf':
            module = g.importFromPath(
                name = 'leo_pdf.py',
                path = g.os_path_finalize_join(g.app.loadDir,'..','plugins'),
                pluginName = 'leo_pdf',
                verbose = False)
            if not module:
                return None
            writer = module.Writer() # Get an instance.
            writer_name = None
        else:
            writer = None
            for ext2,writer_name in (
                ('.html','html'),
                ('.htm','html'),
                ('.tex','latex'),
                ('.pdf','leo.plugins.leo_pdf'), # 2011/11/03
                ('.s5','s5'), # 2011/03/27
                ('.odt','odt'), # 2011/03/27
            ):
                if ext2 == ext: break
            else:
                g.error('unknown docutils extension: %s' % (ext))
                return None
        # SilverCity seems not to be supported, so this warning is strange.
        if False and ext in ('.html','.htm') and not SilverCity:
            if not self.silverCityWarningGiven:
                self.silverCityWarningGiven = True
                if not g.unitTesting:
                    g.es('SilverCity not present so no syntax highlighting')
        # Make the stylesheet path relative to the directory containing the output file.
        rel_stylesheet_path = self.getOption('stylesheet_path') or ''
        # New in Leo 4.5: The rel_stylesheet_path is relative to the open directory.
        stylesheet_path = g.os_path_finalize_join(
            openDirectory,rel_stylesheet_path)
        path = g.os_path_finalize_join(
            stylesheet_path,self.getOption('stylesheet_name'))
        if self.getOption('stylesheet_embed') == False:
            rel_path = g.os_path_join(
                rel_stylesheet_path,self.getOption('stylesheet_name'))
            rel_path = rel_path.replace('\\','/') # 2010/01/28
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
            g.error('stylesheet not found: %s' % (path))
        else:
            g.error('stylesheet not found\n',path)
            if self.path:g.es_print('@path:', self.path)
            g.es_print('open path:',openDirectory)
            if rel_stylesheet_path:
                g.es_print('relative path:', rel_stylesheet_path)
        try:
            # All paths now come through here.
            if trace: g.trace('overrides',overrides)
            result = None # Ensure that result is defined.
            result = docutils.core.publish_string(source=s,
                    reader_name='standalone',
                    parser_name='restructuredtext',
                    writer=writer,
                    writer_name=writer_name,
                    settings_overrides=overrides)
            if g.isBytes(result):
                result = g.toUnicode(result)
        except docutils.ApplicationError as error:
            # g.error('Docutils error (%s):' % (error.__class__.__name__))
            g.error('Docutils error:')
            g.blue(error)
        except Exception:
            g.es_print('Unexpected docutils exception')
            g.es_exception()
        return result
    #@+node:ekr.20090502071837.66: *6* handleMissingStyleSheetArgs
    def handleMissingStyleSheetArgs (self,s=None):

        '''Parse the publish_argv_for_missing_stylesheets option,
        returning a dict containing the parsed args.'''

        force = False
        if force:
            # See http://docutils.sourceforge.net/docs/user/config.html#documentclass
            return {'documentclass':'report', 'documentoptions':'english,12pt,lettersize'}

        if not s:
            s = self.getOption('publish_argv_for_missing_stylesheets')
        if not s: return {}

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
                    key = s[:cm].strip()
                    s = s[cm+1:].strip()
            else: # key = val
                key = s[:eq].strip()
                s = s[eq+1:].strip()
                if s.startswith('['): # [...]
                    rb = s.find(']')
                    if rb == -1: break # Bad argument.
                    val = s[:rb+1]
                    s = s[rb+1:].strip()
                    if s.startswith(','):
                        s = s[1:].strip()
                else: # val[nl] or val,
                    cm = s.find(',')
                    if cm == -1:
                        val = s
                        s = ''
                    else:
                        val = s[:cm].strip()
                        s = s[cm+1:].strip()

            # g.trace('key',repr(key),'val',repr(val),'s',repr(s))
            if not key: break
            if not val.strip(): val = '1'
            d[str(key)] = str(val)

        return d
    #@+node:ekr.20090502071837.88: *3* Utils
    #@+node:ekr.20090502071837.89: *4* computeOutputFileName
    def computeOutputFileName (self,fn):

        openDirectory = self.c.frame.openDirectory
        default_path = self.getOption('default_path')

        if default_path:
            path = g.os_path_finalize_join(self.path,default_path,fn)
        elif self.path:
            path = g.os_path_finalize_join(self.path,fn)
        elif openDirectory:
            path = g.os_path_finalize_join(self.path,openDirectory,fn)
        else:
            path = g.os_path_finalize_join(fn)

        # g.trace('openDirectory %s\ndefault_path %s\npath %s' % (
            # repr(openDirectory),repr(default_path),repr(path)))

        return path
    #@+node:ekr.20090502071837.90: *4* encode
    def encode (self,s):

        # g.trace(self.encoding)

        return g.toEncodedString(s,encoding=self.encoding,reportErrors=True)
    #@+node:ekr.20090502071837.91: *4* report
    def report (self,name):

        if self.getOption('verbose'):

            name = g.os_path_finalize(name)

            g.blue('wrote: %s' % (name))
    #@+node:ekr.20090502071837.92: *4* rstComment
    def rstComment (self,s):

        return '.. %s' % s
    #@+node:ekr.20090502071837.93: *4* underline (leoRst)
    def underline (self,s,p):

        '''Return the underlining string to be used at the given level for string s.
        This includes the headline, and possibly a leading overlining line.
        '''

        trace = False and not g.unitTesting

        if self.atAutoWrite:
            # We *might* generate overlines for top-level sections.
            u = self.atAutoWriteUnderlines
            level = p.level()-self.topLevel

            if trace: g.trace('level: %s under2: %s under1: %s %s' % (
                level,repr(self.underlines2),repr(self.underlines1),p.h))

            # This is tricky. The index n depends on several factors.
            if self.underlines2:
                level -= 1 # There *is* a double-underlined section.
                n = level
            else:
                n = level-1

            if 0 <= n < len(u):
                ch = u[n]
            elif u:
                ch = u[-1]
            else:
                g.trace('can not happen: no u')
                ch = '#'

            # 2010/01/10: write longer underlines for non-ascii characters.
            n = max(4,len(g.toEncodedString(s,encoding=self.encoding,reportErrors=False)))
            if trace: g.trace(self.topLevel,p.level(),level,repr(ch),p.h)
            if level == 0 and self.underlines2:
                return '%s\n%s\n%s\n\n' % (ch*n,p.h,ch*n)
            else:
                return '%s\n%s\n\n' % (p.h,ch*n)
        else:
            # The user is responsible for top-level overlining.
            u = self.getOption('underline_characters') #  '''#=+*^~"'`-:><_'''
            level = max(0,p.level()-self.topLevel)
            level = min(level+1,len(u)-1) # Reserve the first character for explicit titles.
            ch = u [level]
            if trace: g.trace(self.topLevel,p.level(),level,repr(ch),p.h)
            n = max(4,len(g.toEncodedString(s,encoding=self.encoding,reportErrors=False)))
            # return '%s\n%s\n\n' % (p.h.strip(),ch*n)
            return '%s\n%s\n\n' % (s.strip(),ch*n)
                # Fixes bug 618570:
    #@-others
#@+node:ekr.20120219194520.10444: ** html parser classes
#@+at
# Code from rst3.py plugin.
# 
# The parser classes are used to construct the html code for nodes. The algorithm has two phases:
#     1. In the first phase, the html code for each node is identified.
#     2. The second phase identifies all links and checks if these links need to be modified.
# The first phase of scanning is done by the anchor_hmlParserClass. The second phase of this algorithm is
# done with the link_htmlParserClass.
#@@c

#@+<< class linkAnchorParserClass >>
#@+node:ekr.20120219194520.10445: *3*  << class linkAnchorParserClass >>
class linkAnchorParserClass (HTMLParser.HTMLParser):

    '''
    A class to recognize anchors and links in HTML documents.
    A special marker is the "node_marker" which demarkates the border between 
    node and the next.
    '''

    #@+others
    #@+node:ekr.20120219194520.10446: *4* __init__
    def __init__(self,rst):

        HTMLParser.HTMLParser.__init__(self) # Init the base class.

        self.rst = rst

        # Set ivars from options.  This works only if we don't change nodes!
        self.node_begin_marker      = rst.getOption('node_begin_marker')
        self.clear_http_attributes  = rst.getOption('clear_http_attributes')

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
        '''
        Return True if tag, attrs is represents a link.
        '''

        if tag != 'a':
            return False

        result = 'href' in dict(attrs)
        return result
    #@+node:ekr.20120219194520.10449: *4* is_node_marker
    def is_node_marker (self,attrs):
        '''
        Return the name of the anchor, if this is an anchor for the beginning of a node,
        False otherwise.
        '''

        d = dict(attrs)
        result = 'id' in d and d['id'].startswith(self.node_begin_marker)
        if result:
            return d['id']
        return result
    #@-others
#@-<< class linkAnchorParserClass >>
#@+node:ekr.20120219194520.10450: *3* class htmlParserClass (linkAnchorParserClass)
class htmlParserClass (linkAnchorParserClass):

    '''
    The responsibility of the html parser is:
        1. Find out which html code belongs to which node.
        2. Keep a stack of open tags which apply to the current node.
        3. Keep a list of tags which should be included in the nodes, even
           though they might be closed.
           The <style> tag is one example of that.

    Later, we have to relocate inter-file links: if a reference to another location
    is in a file, we must change the link.

    '''

    #@+others
    #@+node:ekr.20120219194520.10451: *4* __init__
    def __init__ (self,rst):

        linkAnchorParserClass.__init__(self,rst) # Init the base class.

        self.stack = None
        # The stack contains lists of the form:
            # [text1, text2, previous].
            # text1 is the opening tag
            # text2 is the closing tag
            # previous points to the previous stack element

        self.node_marker_stack = []
        # self.node_marker_stack.pop() returns True for a closing
        # tag if the opening tag identified an anchor belonging to a vnode.

        self.node_code = []
            # Accumulated html code.
            # Once the hmtl code is assigned a vnode, it is deleted here.

        self.deleted_lines = 0 # Number of lines deleted in self.node_code

        self.endpos_pending = False
        # Do not include self.node_code[0:self.endpos_pending] in the html code.

        self.last_position = None
        # Last position; we must attach html code to this node.

        self.last_marker = None
    #@+node:ekr.20120219194520.10452: *4* handle_starttag
    def handle_starttag (self,tag,attrs):
        '''
        1. Find out if the current tag is an achor.
        2. If it is an anchor, we check if this anchor marks the beginning of a new 
           node
        3. If a new node begins, then we might have to store html code for the previous
           node.
        4. In any case, put the new tag on the stack.
        '''
        is_node_marker = False
        if self.is_anchor(tag,attrs) and self.is_node_marker(attrs):
            is_node_marker = self.is_node_marker(attrs)
            # g.trace(tag,attrs)
            line, column = self.getpos()
            if self.last_position:
                lines = self.node_code [:]
                lines [0] = lines [0] [self.startpos:]
                del lines [line-self.deleted_lines-1:]
                # g.trace('Storing in %s...\n%s' % self.last_position, lines)
                mod_http.get_http_attribute(self.last_position).extend(lines)
                #@+<< trace the unknownAttribute >>
                #@+node:ekr.20120219194520.10453: *5* << trace the unknownAttribute >>
                if 0:
                    g.pr("rst3: unknownAttributes[self.http_attributename]")
                    g.pr("For:", self.last_position)
                    pprint.pprint(mod_http.get_http_attribute(self.last_position))
                #@-<< trace the unknownAttribute >>
            if self.deleted_lines < line-1:
                del self.node_code [: line-1-self.deleted_lines]
                self.deleted_lines = line-1
                self.endpos_pending = True
        # g.trace("rst2: handle_starttag:", tag, attrs, is_node_marker)
        starttag = self.get_starttag_text()
        self.stack = [starttag, None, self.stack]
        self.node_marker_stack.append(is_node_marker)
    #@+node:ekr.20120219194520.10454: *4* handle_endtag
    def handle_endtag(self, tag):
        '''
        1. Set the second element of the current top of stack.
        2. If this is the end tag for an anchor for a node,
           store the current stack for that node.
        '''
        self.stack[1] = "</" + tag + ">"

        # g.trace(tag,g.listToString(self.stack))
        if self.endpos_pending:
            line, column = self.getpos()
            self.startpos = self.node_code[0].find(">", column) + 1
            self.endpos_pending = False

        is_node_marker = self.node_marker_stack.pop()

        if is_node_marker and not self.clear_http_attributes:
            self.last_position = self.rst.http_map[is_node_marker]
            if is_node_marker != self.last_marker:
                if bwm_file: print >> bwm_file, "Handle endtag:", is_node_marker, self.stack
                mod_http.set_http_attribute(self.rst.http_map[is_node_marker], self.stack)
                self.last_marker = is_node_marker
                #bwm: last_marker is not needed?

        self.stack = self.stack[2]
    #@+node:ekr.20120219194520.10455: *4* feed
    def feed(self, line):

        # g.trace(repr(line))

        self.node_code.append(line)

        HTMLParser.HTMLParser.feed(self, line) # Call the base class's feed().
    #@-others
#@+node:ekr.20120219194520.10456: *3* class anchor_htmlParserClass (linkAnchorParserClass)
class anchor_htmlParserClass (linkAnchorParserClass):

    '''
    This htmlparser does the first step of relocating: finding all the anchors within the html nodes.

    Each anchor is mapped to a tuple:
        (current_file, position).

    Filters out markers which mark the beginning of the html code for a node.
    '''

    #@+others
    #@+node:ekr.20120219194520.10457: *4*  __init__
    def __init__ (self,rst,p):

        linkAnchorParserClass.__init__(self,rst)

        self.p = p.copy()
        self.anchor_map = rst.anchor_map
    #@+node:ekr.20120219194520.10458: *4* handle_starttag
    def handle_starttag(self, tag, attrs):
        '''
        1. Find out if the current tag is an achor.
        2. If the current tag is an anchor, update the mapping;
             anchor -> (filename, p)
        '''
        if not self.is_anchor(tag, attrs):
            return

        if self.current_file not in self.anchor_map:
            self.anchor_map[self.current_file] = (self.current_file, self.p)
            simple_name = g.os_path_split(self.current_file)[1]
            self.anchor_map[simple_name] = self.anchor_map[self.current_file]
            if bwm_file: print >> bwm_file, "anchor(1): current_file:", self.current_file, "position:", self.p, "Simple name:", simple_name
            # Not sure what to do here, exactly. Do I need to manipulate
            # the pathname?

        for name, value in attrs:
            if name == 'name' or tag == 'span' and name == 'id':
                if not value.startswith(self.node_begin_marker):
                    if bwm_file: print >> bwm_file, "anchor(2):", value, self.p
                    self.anchor_map[value] = (self.current_file, self.p.copy())
    #@-others
#@+node:ekr.20120219194520.10459: *3* class link_htmlParserClass (linkAnchorParserClass)
class link_htmlparserClass (linkAnchorParserClass):

    '''This html parser does the second step of relocating links:
    1. It scans the html code for links.
    2. If there is a link which links to a previously processed file
       then this link is changed so that it now refers to the node.
    '''

    #@+others
    #@+node:ekr.20120219194520.10460: *4* __init__
    def __init__ (self,rst,p):

        linkAnchorParserClass.__init__(self,rst)

        self.p = p.copy()
        self.anchor_map = rst.anchor_map
        self.replacements = []
    #@+node:ekr.20120219194520.10461: *4* handle_starttag
    def handle_starttag(self, tag, attrs):
        '''
        1. Find out if the current tag is an achor.
        2. If the current tag is an anchor, update the mapping;
             anchor -> p
            Update the list of replacements for the document.
        '''
        if bwm_file: print >> bwm_file, "Is link?", tag, attrs
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
                if bwm_file: print >> bwm_file, "link(1):", name, value, href_a
                if not href_a.startswith(marker):
                    if href_a in self.anchor_map:
                        href_file, href_node = self.anchor_map[href_a]
                        http_node_ref = mod_http.node_reference(href_node)
                        line, column = self.getpos()
                        if bwm_file: print >> bwm_file, "link(2):", line, column, href, href_file, http_node_ref
                        self.replacements.append((line, column, href, href_file, http_node_ref))
    #@+node:ekr.20120219194520.10462: *4* get_replacements
    def get_replacements(self):

        return self.replacements
    #@-others
#@-others
#@-leo
