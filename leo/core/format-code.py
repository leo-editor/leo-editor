#@+leo-ver=5-thin
#@+node:ekr.20100811091636.5997: * @thin format-code.py
#@+others
#@+node:ekr.20100811091636.5838: ** @button format-code
#@+at @rst-markup
# ########################
# Leo's code markup script
# ########################
#@@c
'''A script showing how to convert code in Leo outlines to rST/Sphinx code.

The defaultOptions dict specifies default options.'''

#@+<< imports >>
#@+node:ekr.20100811091636.5919: *3* << imports >>
#@+at Here are the imports.
#@@c
import leo.core.leoGlobals as g

if g.isPython3:
    import io
    StringIO = io.StringIO
else:
    import StringIO
    StringIO = StringIO.StringIO
#@-<< imports >>
if 1: # Format a fixed node.
    h = '@button format-code'
    p = g.findNodeAnywhere(c,h)
#@+<< options >>
#@+node:ekr.20100811091636.5995: *3* << options >>
fn = '%s.rst.txt' % (g.sanitize_filename(p.h))
     # 'format-code.rst.txt'

# g.es('output file',repr(fn))

defaultOptionsDict = {

    # The following options are the most important visually.
    'show_doc_parts_as_paragraphs': True,
    'number-code-lines': False,

    # The following options are definitely used in the script.
    'generate-rst-header-comment': True,
    'output-file-name': fn,
    'show_headlines': True,
    'show_options_nodes': False,
    'show_organizer_nodes': True,
    'show_sections': True,
    'underline_characters': '''#=+*^~"'`-:><_''',
    'verbose': True,

    # The following are not used, but probably should be used.
    'code_block_string': '::',
    'default_path': None, # Must be None, not ''.
    'encoding': 'utf-8',
    'publish_argv_for_missing_stylesheets': None,
    'stylesheet_embed': True,
    'stylesheet_name': 'default.css',
    'stylesheet_path': None, # Must be None, not ''.

    # The following are not used. Their status is unclear.
    'show_leo_directives': False,
}
#@-<< options >>

class formatController:

    '''A class to convert a Leo outline to rst/Sphinx markup.
    The outline is presumed to contain computer source code.'''

    #@+others
    #@+node:ekr.20100811091636.5922: *3*  Birth & init
    #@+node:ekr.20100811091636.5923: *4*  ctor (rstClass)
    def __init__ (self,c,p,defaultOptionsDict):

        self.c = c
        self.p = p.copy()
        self.defaultOptionsDict = defaultOptionsDict

        #@+<< init ivars >>
        #@+node:ekr.20100811091636.5924: *5* << init ivars >>
        # The options dictionary.
        self.optionsDict = {}
        self.vnodeOptionDict = {}

        # Formatting...
        self.code_block_string = ''
        self.node_counter = 0
        self.topLevel = 0
        self.topNode = None

        # For writing.
        self.atAutoWrite = False # True, special cases for writeAtAutoFile.
        self.atAutoWriteUnderlines = '' # Forced underlines for writeAtAutoFile.
        self.leoDirectivesList = g.globalDirectiveList
        self.encoding = 'utf-8'
        self.ext = None # The file extension.
        self.outputFileName = None # The name of the file being written.
        self.outputFile = None # The open file being written.
        self.path = '' # The path from any @path directive.
        self.source = None # The written source as a string.
        self.trialWrite = False # True if doing a trialWrite.
        #@-<< init ivars >>

        self.initOptionsFromSettings() # Still needed.
        self.initSingleNodeOptions()
    #@+node:ekr.20100811091636.5928: *4* initSingleNodeOptions
    def initSingleNodeOptions (self):

        self.singleNodeOptions = [
            'ignore_this_headline',
            'ignore_this_node',
            'ignore_this_tree',
            'preformat_this_node',
            'show_this_headline',
        ]
    #@+node:ekr.20100811091636.5931: *3* Options
    #@+node:ekr.20100811091636.5934: *4* get/SetOption
    def getOption (self,name):

        return self.optionsDict.get(self.munge(name))

    def setOption (self,name,val,tag):

        self.optionsDict [self.munge(name)] = val
    #@+node:ekr.20100811091636.5929: *4* munge
    def munge (self,name):

        '''Convert an option name to the equivalent ivar name.'''

        return name.lower().replace('-','').replace('_','')
    #@+node:ekr.20100811091636.5944: *4* scanAllOptions & helpers
    # Once an option is seen, no other related options in ancestor nodes have any effect.

    def scanAllOptions(self,p):

        '''Scan position p and p's ancestors looking for options,
        setting corresponding ivars.
        '''

        self.initOptionsFromSettings() # Must be done on every node.
        self.preprocessNode(p)
        self.handleSingleNodeOptions(p)
        seen = self.singleNodeOptions[:] # Suppress inheritance of single-node options.

        for p in p.self_and_parents():
            d = self.vnodeOptionDict.get(p.v,{})
            for key in d.keys():
                if not key in seen:
                    seen.append(key)
                    val = d.get(key)
                    self.setOption(key,val,tag=p.h)
    #@+node:ekr.20100811091636.5945: *5* initOptionsFromSettings
    def initOptionsFromSettings (self):

        d = self.defaultOptionsDict

        for key in sorted(d):
            self.setOption(key,d.get(key),'initOptionsFromSettings')
    #@+node:ekr.20100811091636.5946: *5* handleSingleNodeOptions
    def handleSingleNodeOptions (self,p):

        '''Init the settings of single-node options from the vnodeOptionsDict.

        All such options default to False.'''

        d = self.vnodeOptionDict.get(p.v, {} )

        for ivar in self.singleNodeOptions:
            val = d.get(ivar,False)
            #g.trace('%24s %8s %s' % (ivar,val,p.h))
            self.setOption(ivar,val,p.h)

    #@+node:ekr.20100811091636.5937: *5* preprocessNode
    def preprocessNode (self,p):

        d = self.vnodeOptionDict.get(p.v)

        if d is None:
            d = self.scanNodeForOptions(p)
            self.vnodeOptionDict [p.v] = d
    #@+node:ekr.20100811091636.5941: *5* scanNodeForOptions & helpers
    def scanNodeForOptions (self,p):

        '''Return a dictionary containing all the option-name:value entries in p.

        Such entries may arise from @rst-option or @rst-options in the headline,
        or from @ @rst-options doc parts.'''

        d = self.scanHeadlineForOptions(p)
        d2 = self.scanForOptionDocParts(p,p.b)
        d.update(d2)  # Body options over-ride headline options.

        if d: g.trace(p.h,d)

        return d
    #@+node:ekr.20100811091636.5938: *6* parseOptionLine
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
    #@+node:ekr.20100811091636.5939: *6* scanForOptionDocParts
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
    #@+node:ekr.20100811091636.5940: *6* scanHeadlineForOptions
    def scanHeadlineForOptions (self,p):

        '''Return a dictionary containing the options implied by p's headline.'''

        h = p.h.strip()

        if p == self.topNode:
            return {} # Don't mess with the root node.

        if g.match_word(h,0,self.getOption('@rst-options')): 
            return self.scanOptions(p,p.b)
        else:
            # Careful: can't use g.match_word because options may have '-' chars.
            # i = g.skip_id(h,0,chars='@-')
            # word = h[0:i]
            for option,ivar,val in (
                ('@rst-no-head','ignore_this_headline',True),
                ('@rst-head'  ,'show_this_headline',True),
                ('@rst-no-headlines','show_headlines',False),
                ('@rst-ignore','ignore_this_tree',True),
                ('@rst-ignore-node','ignore_this_node',True),
                ('@rst-ignore-tree','ignore_this_tree',True),
                # ('@rst-preformat','preformat_this_node',True),
            ):
                name = self.getOption(option)
                if name:
                    d = { name: val }
                    return d

            return {}
    #@+node:ekr.20100811091636.5942: *6* scanOption
    def scanOption (self,p,s):

        '''Return { name:val } if s is a line of the form name=val.
        Otherwise return {}'''

        if not s.strip() or s.strip().startswith('..'): return {}

        data = self.parseOptionLine(s)

        if data:
            name,val = data
            if name in list(self.defaultOptionsDict.keys()):
                if   val.lower() == 'true': val = True
                elif val.lower() == 'false': val = False
                # g.trace('%24s %8s %s' % (self.munge(name),val,p.h))
                return { self.munge(name): val }
            else:
                g.es_print('ignoring unknown option: %s' % (name),color='red')
                return {}
        else:
            g.trace(repr(s))
            s2 = 'bad rst3 option in %s: %s' % (p.h,s)
            g.es_print(s2,color='red')
            return {}
    #@+node:ekr.20100811091636.5943: *6* scanOptions
    def scanOptions (self,p,s):

        '''Return a dictionary containing all the options in s.'''

        d = {}

        for line in g.splitLines(s):
            d2 = self.scanOption(p,line)
            if d2: d.update(d2)

        return d
    #@+node:ekr.20100811091636.6000: *3* Writing
    #@+node:ekr.20100811091636.5984: *4* encode
    def encode (self,s):

        # g.trace(self.encoding)

        return g.toEncodedString(s,encoding=self.encoding,reportErrors=True)
    #@+node:ekr.20100811091636.5930: *4* run
    def run (self,event=None):

        fn = self.defaultOptionsDict.get('output-file-name','format-code.rst.txt')
        self.outputFileName = g.os_path_finalize_join(g.app.loadDir,fn)
        self.outputFile = StringIO() # Not a binary file.

        print('\n\n\n==========')

        self.writeTree(self.p.copy())
        s = self.outputFile.getvalue()
        self.outputFile = open(self.outputFileName,'w')
        self.outputFile.write(s)
        self.outputFile.close()
        g.es('rst-format: wrote',self.outputFileName)
    #@+node:ekr.20100811091636.5987: *4* underline
    def underline (self,s,p):

        '''Return the underlining string to be used at the given level for string s.'''

        trace = False and not g.unitTesting

        # The user is responsible for top-level overlining.
        u = self.getOption('underline_characters') #  '''#=+*^~"'`-:><_'''
        level = max(0,p.level()-self.topLevel)
        level = min(level+1,len(u)-1) # Reserve the first character for explicit titles.
        ch = u [level]
        if trace: g.trace(self.topLevel,p.level(),level,repr(ch),p.h)
        n = max(4,len(g.toEncodedString(s,encoding=self.encoding,reportErrors=False)))
        return '%s\n%s\n\n' % (p.h.strip(),ch*n)
    #@+node:ekr.20100811091636.5975: *4* write
    def write (self,s):

        # g.trace('%20s %20s %20s %s' % (self.p.h[:20],repr(s)[:20],repr(s)[-20:],g.callers(2)))

        # g.trace('%20s %40s %s' % (self.p.h[:20],repr(s)[:40],g.callers(2)))

        if g.isPython3:
            if g.is_binary_file(self.outputFile):
                s = self.encode(s)
        else:
            s = self.encode(s)

        self.outputFile.write(s)
    #@+node:ekr.20100811091636.5976: *4* writeBody & helpers
    def writeBody (self,p):

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
    #@+node:ekr.20100811091636.6003: *5* split_parts
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
    #@+node:ekr.20100811091636.6004: *5* write_code_block
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
    #@+node:ekr.20100811091636.5977: *4* writeHeadline & helper
    def writeHeadline (self,p):

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

        self.writeHeadlineHelper(p)
    #@+node:ekr.20100811091636.5978: *5* writeHeadlineHelper
    def writeHeadlineHelper (self,p):

        h = p.h.strip()

        # Remove any headline command before writing the headline.
        i = g.skip_ws(h,0)
        i = g.skip_id(h,0,chars='@-')
        word = h [:i].strip()
        if word:
            # Never generate a section for @rst-option or @rst-options or @rst-no-head.
            if word in ('@rst-option','@rst-options','@rst-no-head','@rst-no-leadlines'):
                return

            # Remove all other headline commands from the headline.
            # self.getOption('ignore_node_prefix'),
            # self.getOption('ignore_tree_prefix'),
            # self.getOption('show_headline_prefix'),

            ### for prefix in self.headlineCommands:
            for prefix in ('@rst-ignore-node','@rst-ignore-tree','@rst-ignore'):
                if word == prefix:
                    h = h [len(word):].strip()
                    break

            # New in Leo 4.4.4.
            # if word.startswith('@'):
                # if self.getOption('strip_at_file_prefixes'):
                    # for s in ('@auto','@file','@nosent','@thin',):
                        # if g.match_word(word,0,s):
                            # h = h [len(s):].strip()

        if not h.strip(): return

        if self.getOption('show_sections'):
            self.write(self.underline(h,p))
        else:
            self.write('\n**%s**\n\n' % h.replace('*',''))
    #@+node:ekr.20100811091636.5979: *4* writeNode
    def writeNode (self,p):

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
            self.writeHeadline(p)
            self.writeBody(p)
            p.moveToThreadNext()
    #@+node:ekr.20100811091636.5981: *4* writeTree
    def writeTree(self,p):

        '''Write p's tree to self.outputFile.'''

        self.scanAllOptions(p) # So we can get the next option.

        if self.getOption('generate_rst_header_comment'):
            self.write('.. rst3: filename: %s\n\n' % self.outputFileName)

        # We can't use an iterator because we may skip parts of the tree.
        p = p.copy() # Only one copy is needed for traversal.
        self.topNode = p.copy() # Indicate the top of this tree.
        after = p.nodeAfterTree()
        while p and p != after:
            self.writeNode(p) # Side effect: advances p.
    #@-others

if p:
    fc = formatController(c,p,defaultOptionsDict)
    fc.run()
else:
    print('not found',h)
#@-others
#@-leo
