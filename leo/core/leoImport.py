# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20031218072017.3206: * @file leoImport.py
#@@first
    # Required so non-ascii characters will be valid in unit tests.

#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@@encoding utf-8

#@+<< how to write a new importer >>
#@+node:ekr.20100728074713.5840: ** << how to write a new importer >>
#@@nocolor-node
#@+at
# 
# This discussion is adapted from a thread on the leo-editor group:
# http://groups.google.com/group/leo-editor-users/msg/b148d8fb3338e6a9
# of January 22, 2010.  Feel free to ask more questions there.
# 
# leoImport.py contains a set of "importers" all based on the
# baseScannerClass class. You can define your own importer by creating a
# subclass. With luck, your subclass might be very simple, as with class
# cScanner. In other words, baseScannerClass is supposed to do almost
# all the work.
# 
# **Important**  As I write this, I realize that I remember very little
# about the code, but I do remember its general organization and the
# process of creating a new importer. Here is all I remember, and it
# should be all you need to write any importer.
# 
# This base class has two main parts:
# 
# 1. The "parser" that recognizes where nodes begin and end.
# 
# 2. The "code generator" the actually creates the imported nodes.
# 
# You should never have to change the code generators.  Confine your
# attention to the parser.
# 
# The parser thinks it is looking for classes, and within classes,
# method definitions.  Your job is to tell the parser how to do this.
# Let's look at the ctor for baseScannerClass for clues:
# 
#     # May be overridden in subclasses.
#     self.anonymousClasses = [] # For Delphi Pascal interfaces.
#     self.blockCommentDelim1 = None
#     self.blockCommentDelim2 = None
#     self.blockCommentDelim1_2 = None
#     self.blockCommentDelim2_2 = None
#     self.blockDelim1 = '{'
#     self.blockDelim2 = '}'
#     self.blockDelim2Cruft = [] # Stuff that can follow .blockDelim2.
#     self.classTags = ['class',] # tags that start a tag.
#     self.functionTags = []
#     self.hasClasses = True
#     self.hasFunctions = True
#     self.lineCommentDelim = None
#     self.lineCommentDelim2 = None
#     self.outerBlockDelim1 = None
#     self.outerBlockDelim2 = None
#     self.outerBlockEndsDecls = True
#     self.sigHeadExtraTokens = [] # Extra tokens valid in head of signature.
#     self.sigFailTokens = []
#         # A list of strings that abort a signature when seen in a tail.
#         # For example, ';' and '=' in C.
# 
#     self.strict = False # True if leading whitespace is very significant.
# 
# Yes, this looks like gibberish at first. I do *not* remember what all
# these things do in detail, although obviously the names mean
# something. What I *do* remember is that these ivars control the
# operation of the startsFunction and startsClass methods and their
# helpers (children) *especially startsHelper* and the methods that call
# them, scan and scanHelper. Oh, and one more thing. You may want to set
# hasClasses = False.
# 
# Most of these methods have a trace var that will enable tracing during
# importing. The high-level strategy is simple: study startsHelper in
# detail, set the ivars above to make startsHelper do what you want, and
# trace until things work as you want :-)
# 
# There is one more part of this high-level strategy. Sometimes the
# ivars above are not sufficient to make startsHelper work properly. In
# that case, subclasses will override various methods of the parser, but
# *not* the code generator.
# 
# For example, if indentation affects parsing, you will want to look at
# the Python importer to see how it works--it overrides skipCodeBlock, a
# helper of startsHelper. Others common overrides redefine what a
# comment or string is. For more details, look at the various scanners
# to see the kinds of tricks they use.
# 
# That's it. It would be pointless to give you more details, because
# those details would lead you *away* from the process you need to
# follow.  It's this process/strategy that is important.
#@-<< how to write a new importer >>
#@+<< imports >>
#@+node:ekr.20091224155043.6539: ** << imports >> (leoImport)
# Required so the unit test that simulates an @auto leoImport.py will work!
import leo.core.leoGlobals as g

docutils = g.importExtension('docutils',pluginName='leoImport.py')
import os
import string
if g.isPython3:
    import io
    StringIO = io.StringIO
else:
    import StringIO
    StringIO = StringIO.StringIO
import time
#@-<< imports >>
#@+<< class scanUtility >>
#@+node:sps.20081112093624.1: ** << class scanUtility >>
class scanUtility:

    #@+others
    #@+node:sps.20081111154528.5: *3* escapeFalseSectionReferences
    def escapeFalseSectionReferences(self,s):
        
        '''Probably a bad idea.  Keep the apparent section references.
        The perfect-import write code no longer attempts to expand references
        when the perfectImportFlag is set.
        '''

        return s 

        # result = []
        # for line in g.splitLines(s):
            # r1 = line.find('<<')
            # r2 = line.find('>>')
            # if r1>=0 and r2>=0 and r1<r2:
                # result.append("@verbatim\n")
                # result.append(line)
            # else:
                # result.append(line)
        # return ''.join(result)
    #@-others
#@-<< class scanUtility >>
#@+<< class leoImportCommands >>
#@+node:ekr.20071127175948: ** << class leoImportCommands >>
class leoImportCommands (scanUtility):

    #@+others
    #@+node:ekr.20031218072017.3207: *3* import.__init__ & helper
    def __init__ (self,c):

        self.c = c
        self.default_directory = None # For @path logic.
        self.encoding = 'utf-8'
        self.errors = 0
        self.fileName = None # The original file name, say x.cpp
        self.fileType = None # ".py", ".c", etc.
        self.methodName = None # x, as in < < x methods > > =
        self.output_newline = g.getOutputNewline(c=c) # Value of @bool output_newline
        self.rootLine = "" # Empty or @root + self.fileName
        self.tab_width = c.tab_width # The tab width in effect in the c.currentPosition.
        self.trace = c.config.getBool('trace_import')
        self.treeType = "@file" # None or "@file"
        self.webType = "@noweb" # "cweb" or "noweb"
        self.web_st = [] # noweb symbol table.

        self.createImportDispatchDict()
    #@+node:ekr.20080825131124.3: *4* createImportDispatchDict
    def createImportDispatchDict (self):

        self.importDispatchDict = {
            # Keys are file extensions, values are text scanners.
            # Text scanners must have the signature scanSomeText(self,s,parent,atAuto=False)
            '.c':       self.scanCText,
            '.h':       self.scanCText,
            '.h++':     self.scanCText,
            '.cc':      self.scanCText,
            '.c++':     self.scanCText,
            '.cpp':     self.scanCText,
            '.cxx':     self.scanCText,
            '.cfg':     self.scanIniText,
            '.cs':      self.scanCSharpText,
            '.el':      self.scanElispText,
            '.htm':     self.scanHtmlText,
            '.html':    self.scanHtmlText,
            '.ini':     self.scanIniText,
            '.java':    self.scanJavaText,
            '.js':      self.scanJavaScriptText,
            '.otl':     self.scanVimoutlinterText,
            '.php':     self.scanPHPText,
            '.pas':     self.scanPascalText,
            '.py':      self.scanPythonText,
            '.pyw':     self.scanPythonText,
            # '.txt':     self.scanRstText, # A reasonable default.
            # '.rest':    self.scanRstText,
            # '.rst':     self.scanRstText,
            '.ts':      self.scanTypeScriptText,
            '.xml':     self.scanXmlText,
        }
    #@+node:ekr.20031218072017.3289: *3* Export
    #@+node:ekr.20031218072017.3290: *4* ic.convertCodePartToWeb
    # Headlines not containing a section reference are ignored in noweb and generate index index in cweb.

    def convertCodePartToWeb (self,s,i,v,result):

        # g.trace(g.get_line(s,i))
        c = self.c ; nl = self.output_newline
        lb = g.choose(self.webType=="cweb","@<","<<")
        rb = g.choose(self.webType=="cweb","@>",">>")
        h = v.headString().strip()
        #@+<< put v's headline ref in head_ref >>
        #@+node:ekr.20031218072017.3291: *5* << put v's headline ref in head_ref>>
        #@+at We look for either noweb or cweb brackets. head_ref does not include these brackets.
        #@@c

        head_ref = None
        j = 0
        if g.match(h,j,"<<"):
            k = h.find(">>",j)
        elif g.match(h,j,"<@"):
            k = h.find("@>",j)
        else:
            k = -1

        if k > -1:
            head_ref = h[j+2:k].strip()
            if len(head_ref) == 0:
                head_ref = None
        #@-<< put v's headline ref in head_ref >>
        #@+<< put name following @root or @file in file_name >>
        #@+node:ekr.20031218072017.3292: *5* << put name following @root or @file in file_name >>
        if g.match(h,0,"@file") or g.match(h,0,"@root"):
            line = h[5:].strip()
            #@+<< set file_name >>
            #@+node:ekr.20031218072017.3293: *6* << Set file_name >>
            # set j & k so line[j:k] is the file name.
            # g.trace(line)

            if g.match(line,0,"<"):
                j = 1 ; k = line.find(">",1)
            elif g.match(line,0,'"'):
                j = 1 ; k = line.find('"',1)
            else:
                j = 0 ; k = line.find(" ",0)
            if k == -1:
                k = len(line)

            file_name = line[j:k].strip()
            if file_name and len(file_name) == 0:
                file_name = None
            #@-<< set file_name >>
        else:
            file_name = line = None
        #@-<< put name following @root or @file in file_name >>
        if g.match_word(s,i,"@root"):
            i = g.skip_line(s,i)
            #@+<< append ref to file_name >>
            #@+node:ekr.20031218072017.3294: *5* << append ref to file_name >>
            if self.webType == "cweb":
                if not file_name:
                    result += "@<root@>=" + nl
                else:
                    result += "@(" + file_name + "@>" + nl # @(...@> denotes a file.
            else:
                if not file_name:
                    file_name = "*"
                result += lb + file_name + rb + "=" + nl
            #@-<< append ref to file_name >>
        elif g.match_word(s,i,"@c") or g.match_word(s,i,"@code"):
            i = g.skip_line(s,i)
            #@+<< append head_ref >>
            #@+node:ekr.20031218072017.3295: *5* << append head_ref >>
            if self.webType == "cweb":
                if not head_ref:
                    result += "@^" + h + "@>" + nl # Convert the headline to an index entry.
                    result += "@c" + nl # @c denotes a new section.
                else: 
                    escaped_head_ref = head_ref.replace("@","@@")
                    result += "@<" + escaped_head_ref + "@>=" + nl
            else:
                if not head_ref:
                    if v == c.currentVnode():
                        head_ref = g.choose(file_name,file_name,"*")
                    else:
                        head_ref = "@others"

                result += lb + head_ref + rb + "=" + nl
            #@-<< append head_ref >>
        elif g.match_word(h,0,"@file"):
            # Only do this if nothing else matches.
            #@+<< append ref to file_name >>
            #@+node:ekr.20031218072017.3294: *5* << append ref to file_name >>
            if self.webType == "cweb":
                if not file_name:
                    result += "@<root@>=" + nl
                else:
                    result += "@(" + file_name + "@>" + nl # @(...@> denotes a file.
            else:
                if not file_name:
                    file_name = "*"
                result += lb + file_name + rb + "=" + nl
            #@-<< append ref to file_name >>
            i = g.skip_line(s,i) # 4/28/02
        else:
            #@+<< append head_ref >>
            #@+node:ekr.20031218072017.3295: *5* << append head_ref >>
            if self.webType == "cweb":
                if not head_ref:
                    result += "@^" + h + "@>" + nl # Convert the headline to an index entry.
                    result += "@c" + nl # @c denotes a new section.
                else: 
                    escaped_head_ref = head_ref.replace("@","@@")
                    result += "@<" + escaped_head_ref + "@>=" + nl
            else:
                if not head_ref:
                    if v == c.currentVnode():
                        head_ref = g.choose(file_name,file_name,"*")
                    else:
                        head_ref = "@others"

                result += lb + head_ref + rb + "=" + nl
            #@-<< append head_ref >>
        i,result = self.copyPart(s,i,result)
        return i, result.strip() + nl

    #@+at %defs a b c
    #@+node:ekr.20031218072017.3296: *4* ic.convertDocPartToWeb (handle @ %def)
    def convertDocPartToWeb (self,s,i,result):

        nl = self.output_newline

        # g.trace(g.get_line(s,i))
        if g.match_word(s,i,"@doc"):
            i = g.skip_line(s,i)
        elif g.match(s,i,"@ ") or g.match(s,i,"@\t") or g.match(s,i,"@*"):
            i += 2
        elif g.match(s,i,"@\n"):
            i += 1
        i = g.skip_ws_and_nl(s,i)
        i, result2 = self.copyPart(s,i,"")
        if len(result2) > 0:
            # Break lines after periods.
            result2 = result2.replace(".  ","." + nl)
            result2 = result2.replace(". ","." + nl)
            result += nl+"@"+nl+result2.strip()+nl+nl
        else:
            # All nodes should start with '@', even if the doc part is empty.
            result += g.choose(self.webType=="cweb",nl+"@ ",nl+"@"+nl)
        return i, result
    #@+node:ekr.20031218072017.3297: *4* ic.convertVnodeToWeb
    #@+at This code converts a vnode to noweb text as follows:
    # 
    # Convert @doc to @
    # Convert @root or @code to < < name > >=, assuming the headline contains < < name > >
    # Ignore other directives
    # Format doc parts so they fit in pagewidth columns.
    # Output code parts as is.
    #@@c

    def convertVnodeToWeb (self,v):

        c = self.c
        if not v or not c: return ""
        startInCode = not c.config.at_root_bodies_start_in_doc_mode
        nl = self.output_newline
        s = v.b
        lb = g.choose(self.webType=="cweb","@<","<<")
        i = 0 ; result = "" ; docSeen = False
        while i < len(s):
            progress = i
            # g.trace(g.get_line(s,i))
            i = g.skip_ws_and_nl(s,i)
            if self.isDocStart(s,i) or g.match_word(s,i,"@doc"):
                i,result = self.convertDocPartToWeb(s,i,result)
                docSeen = True
            elif (g.match_word(s,i,"@code") or g.match_word(s,i,"@root") or
                g.match_word(s,i,"@c") or g.match(s,i,lb)):
                #@+<< Supply a missing doc part >>
                #@+node:ekr.20031218072017.3298: *5* << Supply a missing doc part >>
                if not docSeen:
                    docSeen = True
                    result += g.choose(self.webType=="cweb",nl+"@ ",nl+"@"+nl)
                #@-<< Supply a missing doc part >>
                i,result = self.convertCodePartToWeb(s,i,v,result)
            elif self.treeType == "@file" or startInCode:
                #@+<< Supply a missing doc part >>
                #@+node:ekr.20031218072017.3298: *5* << Supply a missing doc part >>
                if not docSeen:
                    docSeen = True
                    result += g.choose(self.webType=="cweb",nl+"@ ",nl+"@"+nl)
                #@-<< Supply a missing doc part >>
                i,result = self.convertCodePartToWeb(s,i,v,result)
            else:
                i,result = self.convertDocPartToWeb(s,i,result)
                docSeen = True
            assert(progress < i)
        result = result.strip()
        if len(result) > 0:
            result += nl
        return result
    #@+node:ekr.20031218072017.3299: *4* ic.copyPart
    # Copies characters to result until the end of the present section is seen.

    def copyPart (self,s,i,result):

        # g.trace(g.get_line(s,i))
        lb = g.choose(self.webType=="cweb","@<","<<")
        rb = g.choose(self.webType=="cweb","@>",">>")
        theType = self.webType
        while i < len(s):
            progress = j = i # We should be at the start of a line here.
            i = g.skip_nl(s,i) ; i = g.skip_ws(s,i)
            if self.isDocStart(s,i):
                return i, result
            if (g.match_word(s,i,"@doc") or
                g.match_word(s,i,"@c") or
                g.match_word(s,i,"@root") or
                g.match_word(s,i,"@code")): # 2/25/03
                return i, result
            elif (g.match(s,i,"<<") and # must be on separate lines.
                g.find_on_line(s,i,">>=") > -1):
                return i, result
            else:
                # Copy the entire line, escaping '@' and
                # Converting @others to < < @ others > >
                i = g.skip_line(s,j) ; line = s[j:i]
                if theType == "cweb":
                    line = line.replace("@","@@")
                else:
                    j = g.skip_ws(line,0)
                    if g.match(line,j,"@others"):
                        line = line.replace("@others",lb + "@others" + rb)
                    elif g.match(line,0,"@"):
                        # Special case: do not escape @ %defs.
                        k = g.skip_ws(line,1)
                        if not g.match(line,k,"%defs"):
                            line = "@" + line
                result += line
            assert(progress < i)
        return i, result.rstrip()
    #@+node:ekr.20031218072017.1462: *4* ic.exportHeadlines
    def exportHeadlines (self,fileName):

        c = self.c ; p = c.p
        nl = g.u(self.output_newline)

        if not p: return
        self.setEncoding()
        firstLevel = p.level()

        try:
            theFile = open(fileName,'w')
        except IOError:
            g.warning("can not open",fileName)
            c.testManager.fail()
            return
        for p in p.self_and_subtree():
            head = p.moreHead(firstLevel,useVerticalBar=True)
            s = head + nl
            if not g.isPython3: # 2010/08/27
                s = g.toEncodedString(s,encoding=self.encoding,reportErrors=True)
            theFile.write(s)
        theFile.close()
    #@+node:ekr.20031218072017.1147: *4* ic.flattenOutline
    def flattenOutline (self,fileName):

        c = self.c ; nl = g.u(self.output_newline)
        p = c.currentVnode()
        if not p: return
        self.setEncoding()
        firstLevel = p.level()

        try:
            theFile = open(fileName,'wb')
                # Fix crasher: open in 'wb' mode.
        except IOError:
            g.warning("can not open",fileName)
            c.testManager.fail()
            return

        for p in p.self_and_subtree():
            head = p.moreHead(firstLevel)
            s = head + nl
            if g.isPython3:
                s = g.toEncodedString(s,encoding=self.encoding,reportErrors=True)
            theFile.write(s)
            body = p.moreBody() # Inserts escapes.
            if len(body) > 0:
                s = g.toEncodedString(body + nl,self.encoding,reportErrors=True)
                theFile.write(s)
        theFile.close()
    #@+node:ekr.20031218072017.1148: *4* ic.outlineToWeb
    def outlineToWeb (self,fileName,webType):

        c = self.c ; nl = self.output_newline
        current = c.p
        if not current: return
        self.setEncoding()
        self.webType = webType
        # 10/14/02: support for output_newline setting.
        # mode = c.config.output_newline
        # mode = g.choose(mode=="platform",'w','wb')
        try:
            # theFile = open(fileName,mode)
            theFile = open(fileName,'w')
        except IOError:
            g.warning("can not open",fileName)
            c.testManager.fail()
            return

        self.treeType = "@file"
        # Set self.treeType to @root if p or an ancestor is an @root node.
        for p in current.parents():
            flag,junk = g.is_special(p.b,0,"@root")
            if flag:
                self.treeType = "@root"
                break
        for p in current.self_and_subtree():
            s = self.convertVnodeToWeb(p)
            if len(s) > 0:
                if not g.isPython3: # 2010/08/27
                    s = g.toEncodedString(s,self.encoding,reportErrors=True)
                theFile.write(s)
                if s[-1] != '\n': theFile.write(nl)
        theFile.close()
    #@+node:ekr.20031218072017.3300: *4* ic.removeSentinelsCommand
    def removeSentinelsCommand (self,paths,toString=False):

        c = self.c

        self.setEncoding()

        for fileName in paths:
            g.setGlobalOpenDir(fileName)
            path, self.fileName = g.os_path_split(fileName)
            s,e = g.readFileIntoString(fileName,self.encoding)
            if s is None: return
            if e: self.encoding = e
            #@+<< set delims from the header line >>
            #@+node:ekr.20031218072017.3302: *5* << set delims from the header line >>
            # Skip any non @+leo lines.
            i = 0
            while i < len(s) and g.find_on_line(s,i,"@+leo") == -1:
                i = g.skip_line(s,i)

            # Get the comment delims from the @+leo sentinel line.
            at = self.c.atFileCommands
            j = g.skip_line(s,i) ; line = s[i:j]

            valid,junk,start_delim,end_delim,junk = at.parseLeoSentinel(line)
            if not valid:
                if not toString: g.es("invalid @+leo sentinel in",fileName)
                return

            if end_delim:
                line_delim = None
            else:
                line_delim,start_delim = start_delim,None
            #@-<< set delims from the header line >>
            # g.trace("line: '%s', start: '%s', end: '%s'" % (line_delim,start_delim,end_delim))
            s = self.removeSentinelLines(s,line_delim,start_delim,end_delim)
            ext = c.config.remove_sentinels_extension
            if not ext:
                ext = ".txt"
            if ext[0] == '.':
                newFileName = c.os_path_finalize_join(path,fileName+ext)
            else:
                head,ext2 = g.os_path_splitext(fileName) 
                newFileName = c.os_path_finalize_join(path,head+ext+ext2)
            if toString:
                return s
            else:
                #@+<< Write s into newFileName >>
                #@+node:ekr.20031218072017.1149: *5* << Write s into newFileName >> (remove-sentinels) (changed)
                # Remove sentinels command.

                try:
                    # mode = c.config.output_newline
                    # mode = g.choose(mode=="platform",'w','wb')
                    # theFile = open(newFileName,mode)
                    theFile = open(newFileName,'w')
                    if not g.isPython3: # 2010/08/27
                        s = g.toEncodedString(s,self.encoding,reportErrors=True)
                    theFile.write(s)
                    theFile.close()
                    if not g.unitTesting:
                        g.es("created:",newFileName)
                except Exception:
                    g.es("exception creating:",newFileName)
                    g.es_print_exception()
                #@-<< Write s into newFileName >>
                return None
    #@+node:ekr.20031218072017.3303: *4* ic.removeSentinelLines
    # This does not handle @nonl properly, but that no longer matters.

    def removeSentinelLines(self,s,line_delim,start_delim,unused_end_delim):

        '''Properly remove all sentinle lines in s.'''

        delim = (line_delim or start_delim or '') + '@'
        verbatim = delim + 'verbatim' ; verbatimFlag = False
        result = [] ; lines = g.splitLines(s)
        for line in lines:
            i = g.skip_ws(line,0)
            if not verbatimFlag and g.match(line,i,delim):
                if g.match(line,i,verbatim):
                    # Force the next line to be in the result.
                    verbatimFlag = True 
            else:
                result.append(line)
                verbatimFlag = False
        result = ''.join(result)
        return result
    #@+node:ekr.20031218072017.1464: *4* ic.weave
    def weave (self,filename):

        c = self.c ; nl = self.output_newline
        p = c.p
        if not p: return
        self.setEncoding()
        #@+<< open filename to f, or return >>
        #@+node:ekr.20031218072017.1150: *5* << open filename to f, or return >> (weave)
        try:
            # 10/14/02: support for output_newline setting.
                # mode = c.config.output_newline
                # mode = g.choose(mode=="platform",'w','wb')
                # f = open(filename,mode)
                # if not f: return

            # 2010/08/27.
            if g.isPython3:
                f = open(filename,'w',encoding=self.encoding)
            else:
                f = open(filename,'w')

        except Exception:
            g.es("exception opening:",filename)
            g.es_print_exception()
            return
        #@-<< open filename to f, or return >>
        for p in p.self_and_subtree():
            s = p.b
            s2 = s.strip()
            if s2 and len(s2) > 0:
                f.write("-" * 60) ; f.write(nl)
                #@+<< write the context of p to f >>
                #@+node:ekr.20031218072017.1465: *5* << write the context of p to f >> (weave)
                # write the headlines of p, p's parent and p's grandparent.
                context = [] ; p2 = p.copy() ; i = 0
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
                        line = g.toEncodedString(line,self.encoding,reportErrors=True)
                    f.write(line)
                    f.write(nl)
                #@-<< write the context of p to f >>
                f.write("-" * 60) ; f.write(nl)
                if not g.isPython3:
                    s = g.toEncodedString(s,self.encoding,reportErrors=True)
                f.write(s.rstrip() + nl)
        f.flush()
        f.close()
    #@+node:ekr.20031218072017.3305: *3* Utilities
    #@+node:ekr.20090122201952.4: *4* appendStringToBody & setBodyString (leoImport)
    def appendStringToBody (self,p,s):

        '''Similar to c.appendStringToBody,
        but does not recolor the text or redraw the screen.'''

        if s:
            body = p.b
            assert(g.isUnicode(body))
            s = g.toUnicode(s,self.encoding)
            self.setBodyString(p,body + s)

    def setBodyString (self,p,s):

        '''Similar to c.setBodyString,
        but does not recolor the text or redraw the screen.'''

        c = self.c ; v = p.v
        if not c or not p: return

        s = g.toUnicode(s,self.encoding)
        current = c.p
        if current and p.v==current.v:
            c.frame.body.setSelectionAreas(s,None,None)
            w = c.frame.body.bodyCtrl
            i = w.getInsertPoint()
            w.setSelectionRange(i,i)

        # Keep the body text up-to-date.
        if v.b != s:
            v.setBodyString(s)
            v.setSelection(0,0)
            p.setDirty()
            if not c.isChanged():
                c.setChanged(True)
    #@+node:ekr.20031218072017.3306: *4* createHeadline (leoImport)
    def createHeadline (self,parent,body,headline):

        # g.trace('*** parent: %s headline: %s' % (parent.h,headline))

        # Create the vnode.
        p = parent.insertAsLastChild()

        body = g.u(body)
        headline = g.u(headline)

        p.initHeadString(headline)
        if len(body) > 0:
            self.setBodyString(p,body)

        return p
    #@+node:ekr.20031218072017.3307: *4* error
    def error (self,s):
        g.es('',s)
    #@+node:ekr.20041126042730: *4* getTabWidth
    def getTabWidth (self,p=None):

        c = self.c
        if 1:
            # Faster, more self-contained.
            val = g.scanAllAtTabWidthDirectives(c,p)
            return val
        else:
            d = c.scanAllDirectives(p)
            w = d.get("tabwidth")
            if w not in (0,None):
                return w
            else:
                return self.c.tab_width
    #@+node:ekr.20031218072017.3309: *4* isDocStart and isModuleStart
    # The start of a document part or module in a noweb or cweb file.
    # Exporters may have to test for @doc as well.

    def isDocStart (self,s,i):

        if not g.match(s,i,"@"):
            return False

        j = g.skip_ws(s,i+1)
        if g.match(s,j,"%defs"):
            return False
        elif self.webType == "cweb" and g.match(s,i,"@*"):
            return True
        else:
            return g.match(s,i,"@ ") or g.match(s,i,"@\t") or g.match(s,i,"@\n")

    def isModuleStart (self,s,i):

        if self.isDocStart(s,i):
            return True
        else:
            return self.webType == "cweb" and (
                g.match(s,i,"@c") or g.match(s,i,"@p") or
                g.match(s,i,"@d") or g.match(s,i,"@f"))
    #@+node:ekr.20031218072017.3312: *4* massageWebBody
    def massageWebBody (self,s):

        theType = self.webType
        lb = g.choose(theType=="cweb","@<","<<")
        rb = g.choose(theType=="cweb","@>",">>")
        #@+<< Remove most newlines from @space and @* sections >>
        #@+node:ekr.20031218072017.3313: *5* << Remove most newlines from @space and @* sections >>
        i = 0
        while i < len(s):
            progress = i
            i = g.skip_ws_and_nl(s,i)
            if self.isDocStart(s,i):
                # Scan to end of the doc part.
                if g.match(s,i,"@ %def"):
                    # Don't remove the newline following %def
                    i = g.skip_line(s,i) ; start = end = i
                else:
                    start = end = i ; i += 2
                while i < len(s):
                    progress2 = i
                    i = g.skip_ws_and_nl(s,i)
                    if self.isModuleStart(s,i) or g.match(s,i,lb):
                        end = i ; break
                    elif theType == "cweb": i += 1
                    else: i = g.skip_to_end_of_line(s,i)
                    assert (i > progress2)
                # Remove newlines from start to end.
                doc = s[start:end]
                doc = doc.replace("\n"," ")
                doc = doc.replace("\r","")
                doc = doc.strip()
                if doc and len(doc) > 0:
                    if doc == "@":
                        doc = g.choose(self.webType=="cweb", "@ ","@\n")
                    else:
                        doc += "\n\n"
                    # g.trace("new doc:",doc)
                    s = s[:start] + doc + s[end:]
                    i = start + len(doc)
            else: i = g.skip_line(s,i)
            assert (i > progress)
        #@-<< Remove most newlines from @space and @* sections >>
        #@+<< Replace abbreviated names with full names >>
        #@+node:ekr.20031218072017.3314: *5* << Replace abbreviated names with full names >>
        i = 0
        while i < len(s):
            progress = i
            # g.trace(g.get_line(s,i))
            if g.match(s,i,lb):
                i += 2 ; j = i ; k = g.find_on_line(s,j,rb)
                if k > -1:
                    name = s[j:k]
                    name2 = self.cstLookup(name)
                    if name != name2:
                        # Replace name by name2 in s.
                        # g.trace("replacing %s by %s" % (name,name2))
                        s = s[:j] + name2 + s[k:]
                        i = j + len(name2)
            i = g.skip_line(s,i)
            assert (i > progress)
        #@-<< Replace abbreviated names with full names >>
        s = s.rstrip()
        return s
    #@+node:ekr.20031218072017.1463: *4* setEncoding (leoImport)
    def setEncoding (self,p=None,atAuto=False):

        # c.scanAllDirectives checks the encoding: may return None.
        c = self.c
        if p is None: p = c.p
        theDict = c.scanAllDirectives(p)
        encoding = theDict.get("encoding")
        if encoding and g.isValidEncoding(encoding):
            self.encoding = encoding
        elif atAuto:
            self.encoding = c.config.default_at_auto_file_encoding
        else:
            self.encoding = 'utf-8'

        # g.trace(self.encoding)
    #@+node:ekr.20031218072017.3209: *3* Import (leoImport)
    #@+node:ekr.20031218072017.3210: *4* ic.createOutline
    def createOutline (self,fileName,parent,
        atAuto=False,atShadow=False,s=None,ext=None
    ):

        c = self.c ; u = c.undoer
        w = c.frame.body
        at = c.atFileCommands
        self.default_directory = g.setDefaultDirectory(c,parent,importing=False)
        fileName = c.os_path_finalize_join(self.default_directory,fileName)
        fileName = fileName.replace('\\','/') # 2011/11/25
        # Fix bug 1185409 importing binary files puts binary content in body editor.
        if g.is_binary_external_file(fileName):
            # Create an @url node.
            p = parent.insertAsLastChild()
            p.h = '@url file://%s' % fileName
            return
        junk,self.fileName = g.os_path_split(fileName)
        self.methodName,self.fileType = g.os_path_splitext(self.fileName)
        self.setEncoding(p=parent,atAuto=atAuto)
        if not ext: ext = self.fileType
        ext = ext.lower()
        if not s:
            if atShadow: kind = '@shadow '
            elif atAuto: kind = '@auto '
            else: kind = ''
            s,e = g.readFileIntoString(fileName,encoding=self.encoding,kind=kind)
            if s is None: return None
            if e: self.encoding = e
        if ext == '.otl':
            self.treeType = '@auto-otl'
            # atAuto = True
            # kind = '@auto-otl'
        # Create the top-level headline.
        if atAuto:
            p = parent.copy()
            p.setBodyString('')
        else:
            undoData = u.beforeInsertNode(parent)
            p = parent.insertAsLastChild()
            if self.treeType == "@file":
                p.initHeadString("@file " + fileName)
            elif self.treeType == "@auto-otl":
                p.initHeadString("@auto-otl " + fileName)
            elif self.treeType is None:
                # 2010/09/29: by convention, we use the short file name.
                p.initHeadString(g.shortFileName(fileName))
            else:
                p.initHeadString(fileName)
            u.afterInsertNode(p,'Import',undoData)
        if self.treeType == '@root': # 2010/09/29.
            self.rootLine = "@root-code "+self.fileName+'\n'
        else:
            self.rootLine = ''
        if p.isAtAutoRstNode(): # @auto-rst is independent of file extension.
            func = self.scanRstText
        elif p.isAtAutoOtlNode():
            func = self.scanVimoutlinterText
        else:
            func = self.importDispatchDict.get(ext)
        if func and not c.config.getBool('suppress_import_parsing',default=False):
            s = s.replace('\r','')
            func(s,p,atAuto=atAuto)
        else:
            # Just copy the file to the parent node.
            s = s.replace('\r','')
            self.scanUnknownFileType(s,p,ext,atAuto=atAuto)
        if atAuto:
            # Fix bug 488894: unsettling dialog when saving Leo file
            # Fix bug 889175: Remember the full fileName.
            at.rememberReadPath(fileName,p)
        p.contract()
        w.setInsertPoint(0)
        w.seeInsertPoint()
        return p
    #@+node:ekr.20070806111212: *4* ic.readAtAutoNodes
    def readAtAutoNodes (self):

        c = self.c
        p = c.p ; after = p.nodeAfterTree()

        found = False
        while p and p != after:
            if p.isAtAutoNode():
                if p.isAtIgnoreNode():
                    g.warning('ignoring',p.h)
                    p.moveToThreadNext()
                else:
                    # self.readOneAtAutoNode(p)
                    fileName=p.atAutoNodeName()
                    c.atFileCommands.readOneAtAutoNode(fileName,p)
                    found = True
                    p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()

        if not g.unitTesting:
            message = g.choose(found,'finished','no @auto nodes in the selected tree')
            g.blue(message)
        c.redraw()

    #@+node:ekr.20031218072017.1810: *4* importDerivedFiles
    def importDerivedFiles (self,parent=None,paths=None,command='Import'):
        # Not a command.  It must *not* have an event arg.
        # command is None when this is called to import a file from the command line.
        c = self.c ; u = c.undoer ; at = c.atFileCommands
        current = c.p or c.rootPosition()
        self.tab_width = self.getTabWidth()
        if not paths:
            return None
        # Initial open from command line is not undoable.
        if command: u.beforeChangeGroup(current,command)
        for fileName in paths:
            fileName = fileName.replace('\\','/') # 2011/10/09.
            g.setGlobalOpenDir(fileName)
            #@+<< set isThin if fileName is a thin derived file >>
            #@+node:ekr.20040930135204: *5* << set isThin if fileName is a thin derived file >>
            # 2011/10/09: g.os.path.normpath converts to *back* slashes!

            # fileName = g.os_path_normpath(fileName)

            # scanHeaderForThin now does all the work.
            isThin = at.scanHeaderForThin(fileName)
            #@-<< set isThin if fileName is a thin derived file >>
            if command: undoData = u.beforeInsertNode(parent)
            p = parent.insertAfter()
            if isThin:
                # 2010/10/09: create @file node, not a deprecated @thin node.
                p.initHeadString("@file " + fileName)
                at.read(p)
            else:
                p.initHeadString("Imported @file " + fileName)
                at.read(p,importFileName=fileName)
            p.contract()
            p.setDirty() # 2011/10/09: tell why the file is dirty!
            if command: u.afterInsertNode(p,command,undoData)
        current.expand()
        c.setChanged(True)
        if command: u.afterChangeGroup(p,command)
        c.redraw(current)
        return p
    #@+node:ekr.20031218072017.3212: *4* importFilesCommand & helper
    def importFilesCommand (self,files=None,treeType=None,redrawFlag=True):
        # Not a command.  It must *not* have an event arg.
        c = self.c ; current = c.p
        if not c or not current or not files: return
        self.tab_width = self.getTabWidth()
        self.treeType = treeType
        if len(files) == 2:
            current = self.createImportParent(current,files)
        for fn in files:
            g.setGlobalOpenDir(fn)
            p = self.createOutline(fn,current)
            if p: # createOutline may fail.
                if not g.unitTesting: g.blue("imported",fn)
                p.contract()
                p.setDirty()
                c.setChanged(True)
        c.validateOutline()
        current.expand()
        if redrawFlag:
            c.redraw(current)
    #@+node:ekr.20031218072017.3213: *5* createImportParent (importCommands)
    def createImportParent (self,current,files):

        '''Create a parent node for nodes with a common prefix: x.h & x.cpp.'''

        name0,name1 = files
        prefix0, junk = g.os_path_splitext(name0)
        prefix1, junk = g.os_path_splitext(name1)

        if prefix0 and prefix0 == prefix1:
            current = current.insertAsLastChild()
            name,junk = g.os_path_splitext(prefix1)
            name = name.replace('\\','/') # 2011/11/25
            current.initHeadString(name)

        return current
    #@+node:ekr.20031218072017.3214: *4* importFlattenedOutline & allies
    #@+node:ekr.20031218072017.3215: *5* convertMoreString/StringsToOutlineAfter
    # Used by paste logic.

    def convertMoreStringToOutlineAfter (self,s,first_p):
        s = s.replace("\r","")
        strings = s.split("\n")
        return self.convertMoreStringsToOutlineAfter(strings,first_p)

    # Almost all the time spent in this command is spent here.

    def convertMoreStringsToOutlineAfter (self,strings,first_p):

        c = self.c
        if len(strings) == 0: return None
        if not self.stringsAreValidMoreFile(strings): return None
        firstLevel, junk = self.moreHeadlineLevel(strings[0])
        lastLevel = -1 ; theRoot = last_p = None
        index = 0
        while index < len(strings):
            progress = index
            s = strings[index]
            level,junk = self.moreHeadlineLevel(s)
            level -= firstLevel
            if level >= 0:
                #@+<< Link a new position p into the outline >>
                #@+node:ekr.20031218072017.3216: *6* << Link a new position p into the outline >>
                assert(level >= 0)
                if not last_p:
                    # g.trace(first_p)
                    theRoot = p = first_p.insertAfter()
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
                #@+node:ekr.20031218072017.3217: *6* << Set the headline string, skipping over the leader >>
                j = 0
                while g.match(s,j,'\t'):
                    j += 1
                if g.match(s,j,"+ ") or g.match(s,j,"- "):
                    j += 2

                p.initHeadString(s[j:])
                #@-<< Set the headline string, skipping over the leader >>
                #@+<< Count the number of following body lines >>
                #@+node:ekr.20031218072017.3218: *6* << Count the number of following body lines >>
                bodyLines = 0
                index += 1 # Skip the headline.
                while index < len(strings):
                    s = strings[index]
                    level, junk = self.moreHeadlineLevel(s)
                    level -= firstLevel
                    if level >= 0:
                        break
                    # Remove first backslash of the body line.
                    if g.match(s,0,'\\'):
                        strings[index] = s[1:]
                    bodyLines += 1
                    index += 1
                #@-<< Count the number of following body lines >>
                #@+<< Add the lines to the body text of p >>
                #@+node:ekr.20031218072017.3219: *6* << Add the lines to the body text of p >>
                if bodyLines > 0:
                    body = ""
                    n = index - bodyLines
                    while n < index:
                        body += strings[n]
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
    #@+node:ekr.20031218072017.3220: *5* importFlattenedOutline
    def importFlattenedOutline (self,files): # Not a command, so no event arg.

        c = self.c ; u = c.undoer ; current = c.p
        if current == None: return
        if len(files) < 1: return

        self.setEncoding()
        fileName = files[0] # files contains at most one file.
        g.setGlobalOpenDir(fileName)
        s,e = g.readFileIntoString(fileName)
        if s is None: return ''
        s = s.replace('\r','') # Fixes bug 626101.
        array = s.split("\n")

        # Convert the string to an outline and insert it after the current node.
        undoData = u.beforeInsertNode(current)
        p = self.convertMoreStringsToOutlineAfter(array,current)
        if p:
            c.endEditing()
            c.validateOutline()
            c.redrawAndEdit(p)
            p.setDirty()
            c.setChanged(True)
            u.afterInsertNode(p,'Import',undoData)
        else:
            if not g.unitTesting:
                g.es("not a valid MORE file",fileName)
    #@+node:ekr.20031218072017.3222: *5* moreHeadlineLevel
    # return the headline level of s,or -1 if the string is not a MORE headline.
    def moreHeadlineLevel (self,s):

        level = 0 ; i = 0
        while g.match(s,i,'\t'):
            level += 1
            i += 1
        plusFlag = g.choose(g.match(s,i,"+"),True,False)
        if g.match(s,i,"+ ") or g.match(s,i,"- "):
            return level, plusFlag
        else:
            return -1, plusFlag
    #@+node:ekr.20031218072017.3223: *5* stringIs/stringsAreValidMoreFile
    # Used by paste logic.

    def stringIsValidMoreFile (self,s):

        s = s.replace("\r","")
        strings = s.split("\n")
        return self.stringsAreValidMoreFile(strings)

    def stringsAreValidMoreFile (self,strings):

        if len(strings) < 1: return False
        level1, plusFlag = self.moreHeadlineLevel(strings[0])
        if level1 == -1: return False
        # Check the level of all headlines.
        i = 0 ; lastLevel = level1
        while i < len(strings):
            s = strings[i] ; i += 1
            level, newFlag = self.moreHeadlineLevel(s)
            if level > 0:
                if level < level1 or level > lastLevel + 1:
                    return False # improper level.
                elif level > lastLevel and not plusFlag:
                    return False # parent of this node has no children.
                elif level == lastLevel and plusFlag:
                    return False # last node has missing child.
                else:
                    lastLevel = level
                    plusFlag = newFlag
        return True
    #@+node:ekr.20031218072017.3224: *4* importWebCommand & allies
    #@+node:ekr.20031218072017.3225: *5* createOutlineFromWeb
    def createOutlineFromWeb (self,path,parent):

        c = self.c ; u = c.undoer
        junk,fileName = g.os_path_split(path)

        undoData = u.beforeInsertNode(parent)

        # Create the top-level headline.
        p = parent.insertAsLastChild()
        p.initHeadString(fileName)
        if self.webType=="cweb":
            self.setBodyString(p,"@ignore\n" + self.rootLine + "@language cweb")

        # Scan the file, creating one section for each function definition.
        self.scanWebFile(path,p)

        u.afterInsertNode(p,'Import',undoData)

        return p
    #@+node:ekr.20031218072017.3226: *5* importWebCommand
    def importWebCommand (self,files,webType):

        c = self.c ; current = c.p
        if current == None: return
        if not files: return
        self.tab_width = self.getTabWidth() # New in 4.3.
        self.webType = webType

        for fileName in files:
            g.setGlobalOpenDir(fileName)
            p = self.createOutlineFromWeb(fileName,current)
            p.contract()
            p.setDirty()
            c.setChanged(True)

        c.redraw(current)
    #@+node:ekr.20031218072017.3227: *5* findFunctionDef
    def findFunctionDef (self,s,i):

        # Look at the next non-blank line for a function name.
        i = g.skip_ws_and_nl(s,i)
        k = g.skip_line(s,i)
        name = None
        while i < k:
            if g.is_c_id(s[i]):
                j = i ; i = g.skip_c_id(s,i) ; name = s[j:i]
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

    def scanBodyForHeadline (self,s):

        if self.webType == "cweb":
            #@+<< scan cweb body for headline >>
            #@+node:ekr.20031218072017.3229: *6* << scan cweb body for headline >>
            i = 0
            while i < len(s):
                i = g.skip_ws_and_nl(s,i)
                # line = g.get_line(s,i) ; g.trace(line)
                # Allow constructs such as @ @c, or @ @<.
                if self.isDocStart(s,i):
                    i += 2 ; i = g.skip_ws(s,i)
                if g.match(s,i,"@d") or g.match(s,i,"@f"):
                    # Look for a macro name.
                    directive = s[i:i+2]
                    i = g.skip_ws(s,i+2) # skip the @d or @f
                    if i < len(s) and g.is_c_id(s[i]):
                        j = i ; g.skip_c_id(s,i) ; return s[j:i]
                    else: return directive
                elif g.match(s,i,"@c") or g.match(s,i,"@p"):
                    # Look for a function def.
                    name = self.findFunctionDef(s,i+2)
                    return g.choose(name,name,"outer function")
                elif g.match(s,i,"@<"):
                    # Look for a section def.
                    # A small bug: the section def must end on this line.
                    j = i ; k = g.find_on_line(s,i,"@>")
                    if k > -1 and (g.match(s,k+2,"+=") or g.match(s,k+2,"=")):
                        return s[j:k+2] # return the section ref.
                i = g.skip_line(s,i)
            #@-<< scan cweb body for headline >>
        else:
            #@+<< scan noweb body for headline >>
            #@+node:ekr.20031218072017.3230: *6* << scan noweb body for headline >>
            i = 0
            while i < len(s):
                i = g.skip_ws_and_nl(s,i)
                # line = g.get_line(s,i) ; g.trace(line)
                if g.match(s,i,"<<"):
                    k = g.find_on_line(s,i,">>=")
                    if k > -1:
                        ref = s[i:k+2]
                        name = s[i+2:k].strip()
                        if name != "@others":
                            return ref
                else:
                    name = self.findFunctionDef(s,i)
                    if name:
                        return name
                i = g.skip_line(s,i)
            #@-<< scan noweb body for headline >>
        return "@" # default.
    #@+node:ekr.20031218072017.3231: *5* scanWebFile (handles limbo)
    def scanWebFile (self,fileName,parent):

        theType = self.webType
        lb = g.choose(theType=="cweb","@<","<<")
        rb = g.choose(theType=="cweb","@>",">>")

        s,e = g.readFileIntoString(fileName)
        if s is None: return

        #@+<< Create a symbol table of all section names >>
        #@+node:ekr.20031218072017.3232: *6* << Create a symbol table of all section names >>
        i = 0 ; self.web_st = []

        while i < len(s):
            progress = i
            i = g.skip_ws_and_nl(s,i)
            # line = g.get_line(s,i) ; g.trace(line)
            if self.isDocStart(s,i):
                if theType == "cweb": i += 2
                else: i = g.skip_line(s,i)
            elif theType == "cweb" and g.match(s,i,"@@"):
                i += 2
            elif g.match(s,i,lb):
                i += 2 ; j = i ; k = g.find_on_line(s,j,rb)
                if k > -1: self.cstEnter(s[j:k])
            else: i += 1
            assert (i > progress)

        # g.trace(self.cstDump())
        #@-<< Create a symbol table of all section names >>
        #@+<< Create nodes for limbo text and the root section >>
        #@+node:ekr.20031218072017.3233: *6* << Create nodes for limbo text and the root section >>
        i = 0
        while i < len(s):
            progress = i
            i = g.skip_ws_and_nl(s,i)
            if self.isModuleStart(s,i) or g.match(s,i,lb):
                break
            else: i = g.skip_line(s,i)
            assert(i > progress)

        j = g.skip_ws(s,0)
        if j < i:
            self.createHeadline(parent,"@ " + s[j:i],"Limbo")

        j = i
        if g.match(s,i,lb):
            while i < len(s):
                progress = i
                i = g.skip_ws_and_nl(s,i)
                if self.isModuleStart(s,i):
                    break
                else: i = g.skip_line(s,i)
                assert(i > progress)
            self.createHeadline(parent,s[j:i],g.angleBrackets(" @ "))

        # g.trace(g.get_line(s,i))
        #@-<< Create nodes for limbo text and the root section >>
        while i < len(s):
            outer_progress = i
            #@+<< Create a node for the next module >>
            #@+node:ekr.20031218072017.3234: *6* << Create a node for the next module >>
            if theType=="cweb":
                assert(self.isModuleStart(s,i))
                start = i
                if self.isDocStart(s,i):
                    i += 2
                    while i < len(s):
                        progress = i
                        i = g.skip_ws_and_nl(s,i)
                        if self.isModuleStart(s,i): break
                        else: i = g.skip_line(s,i)
                        assert (i > progress)
                #@+<< Handle cweb @d, @f, @c and @p directives >>
                #@+node:ekr.20031218072017.3235: *7* << Handle cweb @d, @f, @c and @p directives >>
                if g.match(s,i,"@d") or g.match(s,i,"@f"):
                    i += 2 ; i = g.skip_line(s,i)
                    # Place all @d and @f directives in the same node.
                    while i < len(s):
                        progress = i
                        i = g.skip_ws_and_nl(s,i)
                        if g.match(s,i,"@d") or g.match(s,i,"@f"): i = g.skip_line(s,i)
                        else: break
                        assert (i > progress)
                    i = g.skip_ws_and_nl(s,i)

                while i < len(s) and not self.isModuleStart(s,i):
                    progress = i
                    i = g.skip_line(s,i)
                    i = g.skip_ws_and_nl(s,i)
                    assert (i > progress)

                if g.match(s,i,"@c") or g.match(s,i,"@p"):
                    i += 2
                    while i < len(s):
                        progress = i
                        i = g.skip_line(s,i)
                        i = g.skip_ws_and_nl(s,i)
                        if self.isModuleStart(s,i):
                            break
                        assert (i > progress)
                #@-<< Handle cweb @d, @f, @c and @p directives >>
            else:
                assert(self.isDocStart(s,i)) # isModuleStart == isDocStart for noweb.
                start = i ; i = g.skip_line(s,i)
                while i < len(s):
                    progress = i
                    i = g.skip_ws_and_nl(s,i)
                    if self.isDocStart(s,i): break
                    else: i = g.skip_line(s,i)
                    assert (i > progress)

            body = s[start:i]
            body = self.massageWebBody(body)
            headline = self.scanBodyForHeadline(body)
            self.createHeadline(parent,body,headline)
            #@-<< Create a node for the next module >>
            assert(i > outer_progress)
    #@+node:ekr.20031218072017.3236: *5* Symbol table
    #@+node:ekr.20031218072017.3237: *6* cstCanonicalize
    # We canonicalize strings before looking them up, but strings are entered in the form they are first encountered.

    def cstCanonicalize (self,s,lower=True):

        if lower:
            s = s.lower()

        s = s.replace("\t"," ").replace("\r","")
        s = s.replace("\n"," ").replace("  "," ")

        return s.strip()
    #@+node:ekr.20031218072017.3238: *6* cstDump
    def cstDump (self):

        s = "Web Symbol Table...\n\n"

        for name in sorted(self.web_st):
            s += name + "\n"
        return s
    #@+node:ekr.20031218072017.3239: *6* cstEnter
    # We only enter the section name into the symbol table if the ... convention is not used.

    def cstEnter (self,s):

        # Don't enter names that end in "..."
        s = s.rstrip()
        if s.endswith("..."): return

        # Put the section name in the symbol table, retaining capitalization.
        lower = self.cstCanonicalize(s,True)  # do lower
        upper = self.cstCanonicalize(s,False) # don't lower.
        for name in self.web_st:
            if name.lower() == lower:
                return
        self.web_st.append(upper)
    #@+node:ekr.20031218072017.3240: *6* cstLookup
    # This method returns a string if the indicated string is a prefix of an entry in the web_st.

    def cstLookup (self,target):

        # Do nothing if the ... convention is not used.
        target = target.strip()
        if not target.endswith("..."): return target
        # Canonicalize the target name, and remove the trailing "..."
        ctarget = target[:-3]
        ctarget = self.cstCanonicalize(ctarget).strip()
        found = False ; result = target
        for s in self.web_st:
            cs = self.cstCanonicalize(s)
            if cs[:len(ctarget)] == ctarget:
                if found:
                    g.es('',"****** %s" % (target),"is also a prefix of",s)
                else:
                    found = True ; result = s
                    # g.es("replacing",target,"with",s)
        return result
    #@+node:ekr.20071127175948.1: *3* Import scanners
    #@+node:edreamleo.20070710110153: *4* scanCText
    def scanCText (self,s,parent,atAuto=False):

        scanner = cScanner(importCommands=self,atAuto=atAuto)

        scanner.run(s,parent)
    #@+node:ekr.20071008130845.1: *4* scanCSharpText
    def scanCSharpText (self,s,parent,atAuto=False):

        scanner = cSharpScanner(importCommands=self,atAuto=atAuto)

        scanner.run(s,parent)
    #@+node:ekr.20070711060107.1: *4* scanElispText
    def scanElispText (self,s,parent,atAuto=False):

        scanner = elispScanner(importCommands=self,atAuto=atAuto)

        scanner.run(s,parent)
    #@+node:ekr.20111029055127.16618: *4* scanHtmlText
    def scanHtmlText (self,s,parent,atAuto=False):

        # g.trace(atAuto,parent.h)

        scanner = htmlScanner(importCommands=self,atAuto=atAuto)

        scanner.run(s,parent)
    #@+node:ekr.20100803231223.5808: *4* scanIniText
    def scanIniText (self,s,parent,atAuto=False):

        scanner = iniScanner(importCommands=self,atAuto=atAuto)

        scanner.run(s,parent)
    #@+node:edreamleo.20070710110114.2: *4* scanJavaText
    def scanJavaText (self,s,parent,atAuto=False):

        scanner = javaScanner(importCommands=self,atAuto=atAuto)

        scanner.run(s,parent)
    #@+node:ekr.20071027111225.1: *4* scanJavaScriptText
    def scanJavaScriptText (self,s,parent,atAuto=False):

        scanner = JavaScriptScanner(importCommands=self,atAuto=atAuto)

        scanner.run(s,parent)
    #@+node:ekr.20101027055033.5967: *4* scanNSIText
    def scanNSIText (self,s,p,ext,atAuto=False):

        c = self.c
        changed = c.isChanged()
        # body = g.choose(atAuto,'','@ignore\n')
        # if ext in ('.html','.htm'):   body += '@language html\n'
        # elif ext in ('.txt','.text'): body += '@nocolor\n'
        # else:
            # language = self.languageForExtension(ext)
            # if language: body += '@language %s\n' % language

        assert self.rootLine == ''
        body = '@language ini\n\n'
        self.setBodyString(p,body+s)
        if atAuto:
            p.clearDirty()
            if not changed:
                c.setChanged(False)

        g.app.unitTestDict = {'result':True}
    #@+node:ekr.20070711104241.2: *4* scanPascalText
    def scanPascalText (self,s,parent,atAuto=False):

        scanner = pascalScanner(importCommands=self,atAuto=atAuto)

        scanner.run(s,parent)
    #@+node:ekr.20070711090122: *4* scanPHPText
    def scanPHPText (self,s,parent,atAuto=False):

        scanner = phpScanner(importCommands=self,atAuto=atAuto)
        scanner.run(s,parent)
    #@+node:ekr.20070703122141.99: *4* scanPythonText
    def scanPythonText (self,s,parent,atAuto=False):

        scanner = pythonScanner(importCommands=self,atAuto=atAuto)

        scanner.run(s,parent)
    #@+node:ekr.20090501095634.48: *4* scanRstText
    def scanRstText (self,s,parent,atAuto=False):

        scanner = rstScanner(importCommands=self,atAuto=atAuto)

        scanner.run(s,parent)
    #@+node:ekr.20121011093316.10102: *4* scanTypeScriptText
    def scanTypeScriptText (self,s,parent,atAuto=False):

        scanner = TypeScriptScanner(importCommands=self,atAuto=atAuto)

        scanner.run(s,parent)
    #@+node:ekr.20071214072145: *4* scanXmlText
    def scanXmlText (self,s,parent,atAuto=False):

        # g.trace(atAuto,parent.h)

        scanner = xmlScanner(importCommands=self,atAuto=atAuto)

        scanner.run(s,parent)
    #@+node:ekr.20070713075352: *4* scanUnknownFileType (default scanner) & helper
    def scanUnknownFileType (self,s,p,ext,atAuto=False):

        c = self.c
        changed = c.isChanged()
        body = g.choose(atAuto,'','@ignore\n')
        if ext in ('.html','.htm'):   body += '@language html\n'
        elif ext in ('.txt','.text'): body += '@nocolor\n'
        else:
            language = self.languageForExtension(ext)
            if language: body += '@language %s\n' % language
        self.setBodyString(p,body+self.rootLine+s)
        if atAuto:
            for p in p.self_and_subtree():
                p.clearDirty()
            if not changed:
                c.setChanged(False)
        g.app.unitTestDict = {'result':True}
    #@+node:ekr.20080811174246.1: *5* languageForExtension
    def languageForExtension (self,ext):

        '''Return the language corresponding to the extension ext.'''

        unknown = 'unknown_language'

        if ext.startswith('.'): ext = ext[1:]

        if ext:
            z = g.app.extra_extension_dict.get(ext)
            if z not in (None,'none','None'):
                language = z
            else:
                language = g.app.extension_dict.get(ext)
            if language in (None,'none','None'):
                language = unknown
        else:
            language = unknown

        # g.trace(ext,repr(language))

        # Return the language even if there is no colorizer mode for it.
        return language
    #@+node:ekr.20120517155536.10124: *4* scanVimoutlinterText
    def scanVimoutlinterText(self,s,parent,atAuto=False):

        scanner = vimoutlinerScanner(importCommands=self,atAuto=atAuto)

        scanner.run(s,parent)
    #@+node:ekr.20070713075450: *3* Unit tests (leoImport)
    # atAuto must be False for unit tests: otherwise the test gets wiped out.

    def cUnitTest(self,p,fileName=None,s=None,showTree=False):
        return self.scannerUnitTest(p,atAuto=False,fileName=fileName,s=s,showTree=showTree,ext='.c')

    def cSharpUnitTest(self,p,fileName=None,s=None,showTree=False):
        return self.scannerUnitTest(p,atAuto=False,fileName=fileName,s=s,showTree=showTree,ext='.c#')

    def elispUnitTest(self,p,fileName=None,s=None,showTree=False):
        return self.scannerUnitTest (p,atAuto=False,fileName=fileName,s=s,showTree=showTree,ext='.el')

    def htmlUnitTest(self,p,fileName=None,s=None,showTree=False):
        return self.scannerUnitTest (p,atAuto=False,fileName=fileName,s=s,showTree=showTree,ext='.htm')

    def iniUnitTest(self,p,fileName=None,s=None,showTree=False):
        return self.scannerUnitTest (p,atAuto=False,fileName=fileName,s=s,showTree=showTree,ext='.ini')

    def javaUnitTest(self,p,fileName=None,s=None,showTree=False):
        return self.scannerUnitTest (p,atAuto=False,fileName=fileName,s=s,showTree=showTree,ext='.java')

    def javaScriptUnitTest(self,p,fileName=None,s=None,showTree=False):
        return self.scannerUnitTest (p,atAuto=False,fileName=fileName,s=s,showTree=showTree,ext='.js')

    def pascalUnitTest(self,p,fileName=None,s=None,showTree=False):
        return self.scannerUnitTest (p,atAuto=False,fileName=fileName,s=s,showTree=showTree,ext='.pas')

    def phpUnitTest(self,p,fileName=None,s=None,showTree=False):
        return self.scannerUnitTest (p,atAuto=False,fileName=fileName,s=s,showTree=showTree,ext='.php')

    def pythonUnitTest(self,p,fileName=None,s=None,showTree=False):
        return self.scannerUnitTest (p,atAuto=False,fileName=fileName,s=s,showTree=showTree,ext='.py')

    def rstUnitTest(self,p,fileName=None,s=None,showTree=False):
        if docutils:
            return self.scannerUnitTest(p,atAuto=False,fileName=fileName,s=s,showTree=showTree,ext='.rst')
        else:
            return None

    def textUnitTest(self,p,fileName=None,s=None,showTree=False):
        return self.scannerUnitTest (p,atAuto=False,fileName=fileName,s=s,showTree=showTree,ext='.txt')

    def typeScriptUnitTest(self,p,fileName=None,s=None,showTree=False):
        return self.scannerUnitTest (p,atAuto=False,fileName=fileName,s=s,showTree=showTree,ext='.ts')

    def xmlUnitTest(self,p,fileName=None,s=None,showTree=False):
        return self.scannerUnitTest (p,atAuto=False,fileName=fileName,s=s,showTree=showTree,ext='.xml')

    def defaultImporterUnitTest(self,p,fileName=None,s=None,showTree=False):
        return self.scannerUnitTest (p,atAuto=False,fileName=fileName,s=s,showTree=showTree,ext='.xxx')
    #@+node:ekr.20070713082220: *4* scannerUnitTest
    def scannerUnitTest (self,p,atAuto=False,ext=None,fileName=None,s=None,showTree=False):

        '''Run a unit test of an import scanner,
        i.e., create a tree from string s at location p.'''

        c = self.c ; h = p.h ; old_root = p.copy()
        oldChanged = c.changed
        d = g.app.unitTestDict
        expectedErrors = d.get('expectedErrors')
        expectedErrorMessage = d.get('expectedErrorMessage')
        expectedMismatchLine = d.get('expectedMismatchLine')
        g.app.unitTestDict = {
            'expectedErrors':expectedErrors,
            'expectedErrorMessage':expectedErrorMessage,
            'expectedMismatchLine':expectedMismatchLine,
        }
        if not fileName: fileName = p.h
        if not s: s = self.removeSentinelsCommand([fileName],toString=True)
        title = g.choose(h.startswith('@test'),h[5:],h)

        # Run the actual test.
        self.createOutline(title.strip(),p.copy(),atAuto=atAuto,s=s,ext=ext)

        # Set ok.
        d = g.app.unitTestDict
        ok = ((d.get('result') and expectedErrors in (None,0)) or
            (
                # checkTrialWrite returns *True* if the following match.
                d.get('actualErrors') == d.get('expectedErrors') and
                d.get('actualMismatchLine') == d.get('expectedMismatchLine') and
                (
                    expectedErrorMessage is None or
                    d.get('actualErrorMessage') == d.get('expectedErrorMessage')
                )
            ))

        # Clean up.
        if not showTree:
            while old_root.hasChildren():
                old_root.firstChild().doDelete()
            c.setChanged(oldChanged)

        c.redraw(old_root)

        if g.app.unitTesting:
            # Put all the info in the assertion message.
            table = (
                '',
                'fileName:             %s' % (fileName),
                'result:               %s' % (d.get('result')),
                'actual errors:        %s' % (d.get('actualErrors')),
                'expected errors:      %s' % (d.get('expectedErrors')),
                'actualMismatchLine:   %s' % (repr(d.get('actualMismatchLine'))),
                'expectedMismatchLine: %s' % (repr(d.get('expectedMismatchLine'))),
                'actualErrorMessage:   %s' % (repr(d.get('actualErrorMessage'))),
                'expectedErrorMessage: %s' % (repr(d.get('expectedErrorMessage'))),
            )
            assert ok,'\n'.join(table)

        return ok
    #@-others
#@-<< class leoImportCommands >>
#@+<< class baseScannerClass >>
#@+node:ekr.20070703122141.65: ** << class baseScannerClass >>
class baseScannerClass (scanUtility):

    '''The base class for all import scanner classes.
    This class contains common utility methods.'''

    #@+others
    #@+node:ekr.20070703122141.66: *3*  ctor (baseScannerClass)
    def __init__ (self,importCommands,atAuto,language,alternate_language=None):

        ic = importCommands

        self.atAuto = atAuto
        self.c = c = ic.c

        self.atAutoWarnsAboutLeadingWhitespace = c.config.getBool(
            'at_auto_warns_about_leading_whitespace')
        self.atAutoSeparateNonDefNodes = c.config.getBool(
            'at_auto_separate_non_def_nodes',default=False)
        self.classId = None
            # The identifier containing the class tag:
            # 'class', 'interface', 'namespace', etc.
        self.codeEnd = None
            # The character after the last character of the class, method or function.
            # An error will be given if this is not a newline.
        self.encoding = ic.encoding
        self.errors = 0
        ic.errors = 0
        self.errorLines = []
        self.escapeSectionRefs = True
        self.extraIdChars = ''
        self.fileName = ic.fileName # The original filename.
        self.fileType = ic.fileType # The extension,  '.py', '.c', etc.
        self.file_s = '' # The complete text to be parsed.
        self.fullChecks = c.config.getBool('full_import_checks')
        self.functionSpelling = 'function' # for error message.
        self.importCommands = ic
        self.indentRefFlag = None # None, True or False.
        self.isRst = False
        self.language = language # The language used to set comment delims.
        self.lastParent = None # The last generated parent node (used only by rstScanner).
        self.methodName = ic.methodName # x, as in < < x methods > > =
        self.methodsSeen = False
        self.mismatchWarningGiven = False
        self.output_newline = ic.output_newline
            # = c.config.getBool('output_newline')
        self.output_indent = 0 # The minimum indentation presently in effect.
        self.root = None # The top-level node of the generated tree.
        self.rootLine = ic.rootLine # '' or @root + self.fileName
        self.sigEnd = None # The index of the end of the signature.
        self.sigId = None
            # The identifier contained in the signature,
            # that is, the function or method name.
        self.sigStart = None
            # The start of the line containing the signature.
            # An error will be given if something other than whitespace precedes the signature.
        self.startSigIndent = None
        self.tab_width = None # Set in run: the tab width in effect in the c.currentPosition.
        self.tab_ws = '' # Set in run: the whitespace equivalent to one tab.
        self.trace = False or ic.trace # = c.config.getBool('trace_import')
        self.treeType = ic.treeType # '@root' or '@file'
        self.webType = ic.webType # 'cweb' or 'noweb'

        # Compute language ivars.
        delim1,junk,junk = g.set_delims_from_language(language)
        self.comment_delim = delim1

        # May be overridden in subclasses.
        self.alternate_language = alternate_language # Optional: for @language.
        self.anonymousClasses = [] # For Delphi Pascal interfaces.
        self.blockCommentDelim1 = None
        self.blockCommentDelim2 = None
        self.blockCommentDelim1_2 = None
        self.blockCommentDelim2_2 = None
        self.blockDelim1 = '{'
        self.blockDelim2 = '}'
        self.blockDelim2Cruft = [] # Stuff that can follow .blockDelim2.
        self.caseInsensitive = False
        self.classTags = ['class',] # tags that start a tag.
        self.functionTags = []
        self.hasClasses = True
        self.hasDecls = True
        self.hasFunctions = True
        self.hasNestedClasses = False
        self.ignoreBlankLines = False
        self.ignoreLeadingWs = False
        self.lineCommentDelim = None
        self.lineCommentDelim2 = None
        self.outerBlockDelim1 = None
        self.outerBlockDelim2 = None
        self.outerBlockEndsDecls = True
        self.sigHeadExtraTokens = [] # Extra tokens valid in head of signature.
        self.sigFailTokens = []
            # A list of strings that abort a signature when seen in a tail.
            # For example, ';' and '=' in C.
        self.strict = False # True if leading whitespace is very significant.
        self.warnAboutUnderindentedLines = True
    #@+node:ekr.20070808115837: *3* Checking (baseScannerClass)
    #@+node:ekr.20070703122141.102: *4* check
    def check (self,unused_s,unused_parent):

        '''Make sure the generated nodes are equivalent to the original file.

        1. Regularize and check leading whitespace.
        2. Check that a trial write produces the original file.

        Return True if the nodes are equivalent to the original file.
        '''

        # Note: running full checks on all unit tests is slow.
        if (g.unitTesting or self.fullChecks) and self.treeType in (None,'@file'):
            return self.checkTrialWrite()
        else:
            return True
    #@+node:ekr.20071110144948: *4* checkLeadingWhitespace
    def checkLeadingWhitespace (self,line):

        tab_width = self.tab_width
        lws = line[0:g.skip_ws(line,0)]
        w = g.computeWidth(lws,tab_width)
        ok = (w % abs(tab_width)) == 0

        if not ok:
            self.report('leading whitespace not consistent with @tabwidth %d' % tab_width)
            g.error('line:',repr(line))

        return ok
    #@+node:ekr.20070703122141.104: *4* checkTrialWrite (calls scanAndCompare)
    def checkTrialWrite (self,s1=None,s2=None):

        '''Return True if a trial write produces the original file.'''

        # s1 and s2 are for unit testing.
        trace = False
        c,at=self.c,self.c.atFileCommands
        if s1 is None and s2 is None:
            if self.isRst:
                outputFile = StringIO()
                c.rstCommands.writeAtAutoFile(self.root,self.fileName,outputFile,trialWrite=True)
                s1,s2 = self.file_s,outputFile.getvalue()
            elif self.atAuto: # 2011/12/14: Special case for @auto.
                at.writeOneAtAutoNode(self.root,toString=True,force=True)
                s1,s2 = self.file_s,at.stringOutput
            else:
                # 2011/11/09: We must write sentinels in s2 to handle @others correctly.
                # But we should not handle section references.
                at.write(self.root,
                    nosentinels=False,
                    perfectImportFlag=True,
                    scriptWrite=False,
                    thinFile=True,
                    toString=True,
                )
                s1,s2 = self.file_s, at.stringOutput
                # Now remove sentinels from s2.
                line_delim = self.lineCommentDelim or self.lineCommentDelim2 or ''
                start_delim = self.blockCommentDelim1 or self.blockCommentDelim2 or ''
                # g.trace(self.language,line_delim,start_delim)
                assert line_delim or start_delim
                s2 = self.importCommands.removeSentinelLines(s2,
                    line_delim,start_delim,unused_end_delim=None)
        s1 = g.toUnicode(s1,self.encoding)
        s2 = g.toUnicode(s2,self.encoding)
        # Make sure we have a trailing newline in both strings.
        s1 = s1.replace('\r','')
        s2 = s2.replace('\r','')
        if not s1.endswith('\n'): s1 = s1 + '\n'
        if not s2.endswith('\n'): s2 = s2 + '\n'
        if s1 == s2: return True
        if self.ignoreBlankLines or self.ignoreLeadingWs:
            lines1 = g.splitLines(s1)
            lines2 = g.splitLines(s2)
            lines1 = self.adjustTestLines(lines1)
            lines2 = self.adjustTestLines(lines2)
            s1 = ''.join(lines1)
            s2 = ''.join(lines2)
        if 1: # Token-based comparison.
            bad_i1,bad_i2,ok = self.scanAndCompare(s1,s2)
            if ok: return ok
        else: # Line-based comparison: can not possibly work for html.
            n1,n2 = len(lines1), len(lines2)
            ok = True ; bad_i1,bad_i2 = 0,0
            for i in range(max(n1,n2)):
                ok = self.compareHelper(lines1,lines2,i,self.strict)
                if not ok:
                    bad_1i,bad_i2 = i,i
                    break
        # Unit tests do not generate errors unless the mismatch line does not match.
        if g.app.unitTesting:
            d = g.app.unitTestDict
            ok = d.get('expectedMismatchLine') == bad_i1
                # was d.get('actualMismatchLine')
            if not ok: d['fail'] = g.callers()
        if trace or not ok:
            lines1 = g.splitLines(s1)
            lines2 = g.splitLines(s2)
            self.reportMismatch(lines1,lines2,bad_i1,bad_i2)
        return ok
    #@+node:ekr.20070730093735: *4* compareHelper & helpers (not used when tokenizing)
    def compareHelper (self,lines1,lines2,i,strict):

        '''Compare lines1[i] and lines2[i].
        strict is True if leading whitespace is very significant.'''

        def pr(*args,**keys): #compareHelper
            g.blue(*args,**keys)

        def pr_mismatch(i,line1,line2):
            g.es_print('first mismatched line at line',str(i+1))
            g.es_print('original line: ',line1)
            g.es_print('generated line:',line2)

        d = g.app.unitTestDict
        expectedMismatch = g.app.unitTesting and d.get('expectedMismatchLine')
        enableWarning = not self.mismatchWarningGiven and self.atAutoWarnsAboutLeadingWhitespace
        messageKind = None
        if i >= len(lines1):
            if i != expectedMismatch or not g.unitTesting:
                pr('extra lines')
                for line in lines2[i:]:
                    pr(repr(line))
            d ['actualMismatchLine'] = i
            return False
        if i >= len(lines2):
            if i != expectedMismatch or not g.unitTesting:
                g.es_print('missing lines')
                for line in lines2[i:]:
                    g.es_print('',repr(line))
            d ['actualMismatchLine'] = i
            return False
        line1,line2 = lines1[i],lines2[i]
        if line1 == line2:
            return True # An exact match.
        elif not line1.strip() and not line2.strip():
            return True # Blank lines compare equal.
        elif self.isRst and self.compareRstUnderlines(line1,line2):
            return True
        elif strict:
            s1,s2 = line1.lstrip(),line2.lstrip()
            messageKind = g.choose(
                s1 == s2 and self.startsComment(s1,0) and self.startsComment(s2,0),
                'comment','error')
        else:
            s1,s2 = line1.lstrip(),line2.lstrip()
            messageKind = g.choose(s1==s2,'warning','error')
        if g.unitTesting:
            d ['actualMismatchLine'] = i+1
            ok = i+1 == expectedMismatch
            if not ok:  pr_mismatch(i,line1,line2)
            return ok
        elif strict:
            if enableWarning:
                self.mismatchWarningGiven = True
                if messageKind == 'comment':
                    self.warning('mismatch in leading whitespace before comment')
                else:
                    self.error('mismatch in leading whitespace')
                pr_mismatch(i,line1,line2)
            return messageKind == 'comment' # Only mismatched comment lines are valid.
        else:
            if enableWarning:
                self.mismatchWarningGiven = True
                self.checkLeadingWhitespace(line1)
                self.warning('mismatch in leading whitespace')
                pr_mismatch(i,line1,line2)
            return messageKind in ('comment','warning') # Only errors are invalid.
    #@+node:ekr.20091227115606.6468: *5* adjustTestLines (baseScannerClass)
    def adjustTestLines(self,lines):

        '''Ignore newlines.

        This fudge allows the rst code generators to insert needed newlines freely.'''

        if self.ignoreBlankLines:
            lines = [z for z in lines if z.strip()]

        if self.ignoreLeadingWs:
            lines = [z.lstrip() for z in lines]

        return lines
    #@+node:ekr.20090513073632.5735: *5* compareRstUnderlines
    def compareRstUnderlines(self,s1,s2):

        s1,s2 = s1.rstrip(),s2.rstrip()
        if s1 == s2:
            return True # Don't worry about trailing whitespace.

        n1, n2 = len(s1),len(s2)
        ch1 = n1 and s1[0] or ''
        ch2 = n2 and s2[0] or ''

        val = (
            n1 >= 2 and n2 >= 2 and # Underlinings must be at least 2 long.
            ch1 == ch2 and # The underlining characters must match.
            s1 == ch1 * n1 and # The line must consist only of underlining characters.
            s2 == ch2 * n2)

        return val
    #@+node:ekr.20111109151106.9782: *4* formatTokens (baseScannerClass)
    def formatTokens(self,tokens):

        '''Format tokens for printing or dumping.'''

        i,result = 0,[]
        for kind,val,line_number in tokens:
            s = '%3s %3s %6s %s' % (i,line_number,kind,repr(val))
            result.append(s)
            i += 1

        return '\n'.join(result)
    #@+node:ekr.20070911110507: *4* reportMismatch
    def reportMismatch (self,lines1,lines2,bad_i1,bad_i2):

        # g.trace('**',bad_i1,bad_i2,g.callers())
        trace = False # This causes traces for *non-failing* unit tests.
        kind = g.choose(self.atAuto,'@auto','import command')
        n1,n2 = len(lines1),len(lines2)
        s1 = '%s did not import %s perfectly\n' % (
            kind,self.root.h)
        s2 = 'The clean-all-lines command may help fix whitespace problems\n'
        s3 = 'first mismatched line: %s (original) = %s (imported)' % (
            bad_i1,bad_i2)
        s = s1 + s2 + s3
        if trace: g.trace(s)
        else:     self.error(s)
        aList = []
        aList.append('Original file...\n')
        for i in range(max(0,bad_i1-2),min(bad_i1+3,n1)):
            line = repr(lines1[i])
            aList.append('%4d %s' % (i,line))
        aList.append('\nImported file...\n')
        for i in range(max(0,bad_i2-2),min(bad_i2+3,n2)):
            line = repr(lines2[i])
            aList.append('%4d %s' % (i,line))
        if trace or not g.unitTesting:
            g.blue('\n'.join(aList))
        return False
    #@+node:ekr.20111101052702.16721: *4* scanAndCompare & helpers (calls tokenize)
    def scanAndCompare (self,s1,s2):

        '''Tokenize both s1 and s2, then perform a token-based comparison.

        Blank lines and leading whitespace has already been stripped
        according to the ignoreBlankLines and ignoreLeadingWs ivars.

        Return (n,ok), where n is the first mismatched line in s1.
        '''

        tokens1 = self.tokenize(s1)
        tokens2 = self.tokenize(s2)
        tokens1 = self.filterTokens(tokens1)
        tokens2 = self.filterTokens(tokens2)
        if self.stripTokens(tokens1) == self.stripTokens(tokens2):
            # g.trace('stripped tokens are equal')
            return -1,-1,True
        else:
            n1,n2 = self.compareTokens(tokens1,tokens2)
            return n1,n2,False
    #@+node:ekr.20111101092301.16729: *5* compareTokens
    def compareTokens(self,tokens1,tokens2):

        trace = True and not g.unitTesting
        verbose = False
        i,n1,n2 = 0,len(tokens1),len(tokens2)
        fail_n1,fail_n2 = -1,-1
        while i < max(n1,n2):
            if trace and verbose:
                for n,tokens in ((n1,tokens1),(n2,tokens2),):
                    if i < n: kind,val,line_number = tokens[i]
                    else:     kind,val,line_number = 'eof','',''
                    try:
                        print('%3s %3s %7s' % (i,line_number,kind),repr(val)[:40])
                    except UnicodeEncodeError:
                        print('%3s %3s %7s' % (i,line_number,kind),'unicode error!')
                        # print(val)
            if i < n1: kind1,val1,tok_n1 = tokens1[i]
            else:      kind1,val1,tok_n1 = 'eof','',n1
            if i < n2: kind2,val2,tok_n2 = tokens2[i]
            else:      kind2,val2,tok_n2 = 'eof','',n2
            if fail_n1 == -1 and fail_n2 == -1 and (kind1 != kind2 or val1 != val2):
                if trace: g.trace('fail at lines: %s,%s' % (tok_n1,tok_n2))
                fail_n1,fail_n2 = tok_n1,tok_n2 # Bug fix: 2013/09/08.
                if trace:
                    print('------ Failure ----- i: %s n1: %s n2: %s' % (i,n1,n2))
                    print('tok_n1: %s tok_n2: %s' % (tok_n1,tok_n2))
                    print('kind1: %s kind2: %s\nval1: %s\nval2: %s' % (
                        kind1,kind2,repr(val1),repr(val2)))
                if trace and verbose:
                    n3 = 0
                    i += 1
                    while n3 < 10 and i < max(n1,n2):
                        for n,tokens in ((n1,tokens1),(n2,tokens2),):
                            if i < n: kind,val,junk_n = tokens[i]
                            else:     kind,val = 'eof',''
                            print('%3s %7s %s' % (i,kind,repr(val)))
                        n3 += 1
                        i += 1
                break
            i += 1
        if fail_n1 > -1 or fail_n2 > -1:
            if trace: g.trace('fail',fail_n1,fail_n2)
            return fail_n1,fail_n2
        elif n1 == n2:
            if trace: g.trace('equal')
            return -1,-1
        else:
            n = min(len(tokens1),len(tokens2))
            if trace: g.trace('fail 2 at line: %s' % (n))
            return n,n
    #@+node:ekr.20111101052702.16722: *5* filterTokens & helpers
    def filterTokens (self,tokens):

        '''Filter tokens as needed for correct comparisons.

        May be overridden in subclasses.'''

        return tokens
    #@+node:ekr.20111101092301.16727: *6* removeLeadingWsTokens
    def removeLeadingWsTokens (self,tokens):

        '''Remove tokens representing leading whitespace.'''

        i,last,result = 0,'nl',[]
        while i < len(tokens):
            progress = i
            kind,val,n = tok = tokens[i]
            if kind == 'ws' and last == 'nl':
                pass
            else:
                result.append(tok)
            i += 1
            last = kind
            assert progress + 1 == i

        return result
    #@+node:ekr.20111101092301.16728: *6* removeBlankLinesTokens
    def removeBlankLinesTokens(self,tokens):

        '''Remove all tokens representing blank lines.'''

        trace = False
        if trace: g.trace('\nbefore:',tokens)

        i,last,lws,result = 0,'nl',[],[]
        while i < len(tokens):
            progress = i
            kind,val,n = tok = tokens[i]
            if kind == 'ws':
                if last in ('nl','ws'):
                    # Continue to append leading whitespace.
                    # Wrong, if ws tok ends in newline.
                    lws.append(tok)
                else:
                    # Not leading whitespace: add it.
                    if lws: result.extend(lws)
                    lws = []
                    result.append(tok)
            elif kind == 'nl':
                # Ignore any previous blank line and remember *this* newline.
                lws = [tok]
            else:
                # A non-blank line: append the leading whitespace.
                if lws: result.extend(lws)
                lws = []
                result.append(tok)
            last = kind
            i += 1
            assert i == progress+1
        # Add any remaining ws.
        if lws: result.extend(lws)

        if trace: g.trace('\nafter: ',result)
        return result
    #@+node:ekr.20111109151106.9781: *4* stripTokens (baseScannerClass)
    def stripTokens(self,tokens):

        '''Remove the line_number from all tokens.'''

        return [(kind,val) for (kind,val,line_number) in tokens]
    #@+node:ekr.20070706084535: *3* Code generation
    #@+at None of these methods should ever need to be overridden in subclasses.
    # 
    #@+node:ekr.20090512080015.5800: *4* adjustParent
    def adjustParent (self,parent,headline):

        '''Return the effective parent.

        This is overridden by the rstScanner class.'''

        return parent
    #@+node:ekr.20070707073044.1: *4* addRef
    def addRef (self,parent):

        '''Create an unindented @others or section reference in the parent node.'''

        if self.isRst and not self.atAuto:
            return

        if self.treeType in ('@file',None):
            self.appendStringToBody(parent,'@others\n')

        if self.treeType == '@root' and self.methodsSeen:
            self.appendStringToBody(parent,
                g.angleBrackets(' ' + self.methodName + ' methods ') + '\n\n')
    #@+node:ekr.20090122201952.6: *4* appendStringToBody & setBodyString (baseScannerClass)
    def appendStringToBody (self,p,s):

        '''Similar to c.appendStringToBody,
        but does not recolor the text or redraw the screen.'''

        return self.importCommands.appendStringToBody(p,s)

    def setBodyString (self,p,s):

        '''Similar to c.setBodyString,
        but does not recolor the text or redraw the screen.'''

        return self.importCommands.setBodyString(p,s)
    #@+node:ekr.20090512153903.5806: *4* computeBody (baseScannerClass)
    def computeBody (self,s,start,sigStart,codeEnd):

        trace = False

        body1 = s[start:sigStart]
        # Adjust start backwards to get a better undent.
        if body1.strip():
            while start > 0 and s[start-1] in (' ','\t'):
                start -= 1

        # g.trace(repr(s[sigStart:codeEnd]))

        body1 = self.undentBody(s[start:sigStart],ignoreComments=False)
        body2 = self.undentBody(s[sigStart:codeEnd])
        body = body1 + body2

        if trace: g.trace('body: %s' % repr(body))

        tail = body[len(body.rstrip()):]
        if not '\n' in tail:
            self.warning(
                '%s %s does not end with a newline; one will be added\n%s' % (
                self.functionSpelling,self.sigId,g.get_line(s,codeEnd)))

        return body1,body2
    #@+node:ekr.20090513073632.5737: *4* createDeclsNode
    def createDeclsNode (self,parent,s):

        '''Create a child node of parent containing s.'''

        # Create the node for the decls.
        headline = '%s declarations' % self.methodName
        body = self.undentBody(s)
        self.createHeadline(parent,body,headline)
    #@+node:ekr.20070707085612: *4* createFunctionNode
    def createFunctionNode (self,headline,body,parent):

        # Create the prefix line for @root trees.
        if self.treeType == '@root':
            prefix = g.angleBrackets(' ' + headline + ' methods ') + '=\n\n'
            self.methodsSeen = True
        else:
            prefix = ''

        # Create the node.
        return self.createHeadline(parent,prefix + body,headline)

    #@+node:ekr.20070703122141.77: *4* createHeadline (baseScannerClass)
    def createHeadline (self,parent,body,headline):

        return self.importCommands.createHeadline(parent,body,headline)
    #@+node:ekr.20090502071837.1: *4* endGen
    def endGen (self,s):

        '''Do any language-specific post-processing.'''
        pass
    #@+node:ekr.20070703122141.79: *4* getLeadingIndent
    def getLeadingIndent (self,s,i,ignoreComments=True):

        '''Return the leading whitespace of a line.
        Ignore blank and comment lines if ignoreComments is True'''

        width = 0
        i = g.find_line_start(s,i)
        if ignoreComments:
            while i < len(s):
                # g.trace(g.get_line(s,i))
                j = g.skip_ws(s,i)
                if g.is_nl(s,j) or g.match(s,j,self.comment_delim):
                    i = g.skip_line(s,i) # ignore blank lines and comment lines.
                else:
                    i, width = g.skip_leading_ws_with_indent(s,i,self.tab_width)
                    break      
        else:
            i, width = g.skip_leading_ws_with_indent(s,i,self.tab_width)

        # g.trace('returns:',width)
        return width
    #@+node:ekr.20070709094002: *4* indentBody
    def indentBody (self,s,lws=None):

        '''Add whitespace equivalent to one tab for all non-blank lines of s.'''

        result = []
        if not lws: lws = self.tab_ws

        for line in g.splitLines(s):
            if line.strip():
                result.append(lws + line)
            elif line.endswith('\n'):
                result.append('\n')

        result = ''.join(result)
        return result
    #@+node:ekr.20070705085335: *4* insertIgnoreDirective (leoImport)
    def insertIgnoreDirective (self,parent):

        c = self.c

        self.appendStringToBody(parent,'@ignore')

        if g.unitTesting:
            g.app.unitTestDict['fail'] = g.callers()
        else:
            if parent.isAnyAtFileNode() and not parent.isAtAutoNode():
                g.warning('inserting @ignore')
                c.import_error_nodes.append(parent.h)

    #@+node:ekr.20070707113832.1: *4* putClass & helpers
    def putClass (self,s,i,sigEnd,codeEnd,start,parent):

        '''Creates a child node c of parent for the class,
        and a child of c for each def in the class.'''

        trace = False
        if trace:
            # g.trace('tab_width',self.tab_width)
            g.trace('sig',repr(s[i:sigEnd]))

        # Enter a new class 1: save the old class info.
        oldMethodName = self.methodName
        oldStartSigIndent = self.startSigIndent

        # Enter a new class 2: init the new class info.
        self.indentRefFlag = None

        class_kind = self.classId
        class_name = self.sigId
        headline = '%s %s' % (class_kind,class_name)
        headline = headline.strip()
        self.methodName = headline

        # Compute the starting lines of the class.
        prefix = self.createClassNodePrefix()
        if not self.sigId:
            g.trace('Can not happen: no sigId')
            self.sigId = 'Unknown class name'
        classHead = s[start:sigEnd]
        i = self.extendSignature(s,sigEnd)
        extend = s[sigEnd:i]
        if extend:
            classHead = classHead + extend

        # Create the class node.
        class_node = self.createHeadline(parent,'',headline)

        # Remember the indentation of the class line.
        undentVal = self.getLeadingIndent(classHead,0)

        # Call the helper to parse the inner part of the class.
        putRef,bodyIndent,classDelim,decls,trailing = self.putClassHelper(
            s,i,codeEnd,class_node)
        # g.trace('bodyIndent',bodyIndent,'undentVal',undentVal)

        # Set the body of the class node.
        ref = putRef and self.getClassNodeRef(class_name) or ''

        if trace: g.trace('undentVal',undentVal,'bodyIndent',bodyIndent)

        # Give ref the same indentation as the body of the class.
        if ref:
            bodyWs = g.computeLeadingWhitespace (bodyIndent,self.tab_width)
            ref = '%s%s' % (bodyWs,ref)

        # Remove the leading whitespace.
        result = (
            prefix +
            self.undentBy(classHead,undentVal) +
            self.undentBy(classDelim,undentVal) +
            self.undentBy(decls,undentVal) +
            self.undentBy(ref,undentVal) +
            self.undentBy(trailing,undentVal))

        result = self.adjust_class_ref(result)

        # Append the result to the class node.
        self.appendTextToClassNode(class_node,result)

        # Exit the new class: restore the previous class info.
        self.methodName = oldMethodName
        self.startSigIndent = oldStartSigIndent
    #@+node:ekr.20111029153537.16647: *5* adjust_class_ref
    def adjust_class_ref(self,s):

        '''Over-ridden by xml and html scanners.'''

        return s
    #@+node:ekr.20070707190351: *5* appendTextToClassNode
    def appendTextToClassNode (self,class_node,s):

        self.appendStringToBody(class_node,s) 
    #@+node:ekr.20070703122141.105: *5* createClassNodePrefix
    def createClassNodePrefix (self):

        '''Create the class node prefix.'''

        if  self.treeType == '@root':
            prefix = g.angleBrackets(' ' + self.methodName + ' methods ') + '=\n\n'
            self.methodsSeen = True
        else:
            prefix = ''

        return prefix
    #@+node:ekr.20070703122141.106: *5* getClassNodeRef
    def getClassNodeRef (self,class_name):

        '''Insert the proper body text in the class_vnode.'''

        if self.treeType in ('@file',None):
            s = '@others'
        else:
            s = g.angleBrackets(' class %s methods ' % (class_name))

        return '%s\n' % (s)
    #@+node:ekr.20070707171329: *5* putClassHelper
    def putClassHelper(self,s,i,end,class_node):

        '''s contains the body of a class, not including the signature.

        Parse s for inner methods and classes, and create nodes.'''

        trace = False and not g.unitTesting

        # Increase the output indentation (used only in startsHelper).
        # This allows us to detect over-indented classes and functions.
        old_output_indent = self.output_indent
        self.output_indent += abs(self.tab_width)

        # Parse the decls.
        if self.hasDecls: # 2011/11/11
            j = i ; i = self.skipDecls(s,i,end,inClass=True)
            decls = s[j:i]
        else:
            decls = ''

        # Set the body indent if there are real decls.
        bodyIndent = decls.strip() and self.getIndent(s,i) or None
        if trace: g.trace('bodyIndent',bodyIndent)

        # Parse the rest of the class.
        delim1, delim2 = self.outerBlockDelim1, self.outerBlockDelim2
        if g.match(s,i,delim1):
            # Do *not* use g.skip_ws_and_nl here!
            j = g.skip_ws(s,i + len(delim1))
            if g.is_nl(s,j): j = g.skip_nl(s,j)
            classDelim = s[i:j]
            end2 = self.skipBlock(s,i,delim1=delim1,delim2=delim2)
            start,putRef,bodyIndent2 = self.scanHelper(s,j,end=end2,parent=class_node,kind='class')
        else:
            classDelim = ''
            start,putRef,bodyIndent2 = self.scanHelper(s,i,end=end,parent=class_node,kind='class')

        if bodyIndent is None: bodyIndent = bodyIndent2

        # Restore the output indentation.
        self.output_indent = old_output_indent

        # Return the results.
        trailing = s[start:end]
        return putRef,bodyIndent,classDelim,decls,trailing
    #@+node:ekr.20070707082432: *4* putFunction (baseScannerClass)
    def putFunction (self,s,sigStart,codeEnd,start,parent):

        '''Create a node of parent for a function defintion.'''

        trace = False and not g.unitTesting
        verbose = True

        # if trace: g.trace(start,sigStart,self.sigEnd,codeEnd)

        # Enter a new function: save the old function info.
        oldStartSigIndent = self.startSigIndent

        if self.sigId:
            headline = self.sigId
        else:
            g.trace('Can not happen: no sigId')
            headline = 'unknown function'

        body1,body2 = self.computeBody(s,start,sigStart,codeEnd)
        body = body1 + body2
        parent = self.adjustParent(parent,headline)

        if trace:
            # pylint: disable=E1103
                # Instance of str has no h member.
            g.trace('parent',parent.h) # pylint complains.
            if verbose:
                # g.trace('**body1...\n',body1)
                g.trace('**body2...\n',body2)

        # 2010/11/04: Fix wishlist bug 670744.
        if self.atAutoSeparateNonDefNodes:
            if body1.strip():
                if trace: g.trace('head',body1)
                line1 = g.splitLines(body1.lstrip())[0]
                line1 = line1.strip() or 'non-def code'
                self.createFunctionNode(line1,body1,parent)
                body = body2

        self.lastParent = self.createFunctionNode(headline,body,parent)

        # Exit the function: restore the function info.
        self.startSigIndent = oldStartSigIndent
    #@+node:ekr.20070705094630: *4* putRootText
    def putRootText (self,p):

        self.appendStringToBody(p,'%s@language %s\n@tabwidth %d\n' % (
            self.rootLine,self.alternate_language or self.language,self.tab_width))
    #@+node:ekr.20070703122141.88: *4* undentBody
    def undentBody (self,s,ignoreComments=True):

        '''Remove the first line's leading indentation from all lines of s.'''

        trace = False
        if trace: g.trace('before...\n',g.listToString(g.splitLines(s)))

        if self.isRst:
            return s # Never unindent rst code.

        # Calculate the amount to be removed from each line.
        undentVal = self.getLeadingIndent(s,0,ignoreComments=ignoreComments)
        if undentVal == 0:
            return s
        else:
            result = self.undentBy(s,undentVal)
            if trace: g.trace('after...\n',g.listToString(g.splitLines(result)))
            return result
    #@+node:ekr.20081216090156.1: *4* undentBy
    def undentBy (self,s,undentVal):

        '''Remove leading whitespace equivalent to undentVal from each line.
        For strict languages, add an underindentEscapeString for underindented line.'''

        trace = False and not g.app.unitTesting
        if self.isRst:
            return s # Never unindent rst code.

        tag = self.c.atFileCommands.underindentEscapeString
        result = [] ; tab_width = self.tab_width
        for line in g.splitlines(s):
            lws_s = g.get_leading_ws(line)
            lws = g.computeWidth(lws_s,tab_width)
            s = g.removeLeadingWhitespace(line,undentVal,tab_width)
            # 2011/10/29: Add underindentEscapeString only for strict languages.
            if self.strict and s.strip() and lws < undentVal:
                if trace: g.trace('undentVal: %s, lws: %s, %s' % (
                    undentVal,lws,repr(line)))
                # Bug fix 2012/06/05: end the underindent count with a period,
                # to protect against lines that start with a digit!
                result.append("%s%s.%s" % (tag,undentVal-lws,s.lstrip()))
            else:
                if trace: g.trace(repr(s))
                result.append(s)
        return ''.join(result)
    #@+node:ekr.20070801074524: *4* underindentedComment & underindentedLine
    def underindentedComment (self,line):

        if self.atAutoWarnsAboutLeadingWhitespace:
            self.warning(
                'underindented python comments.\nExtra leading whitespace will be added\n' + line)

    def underindentedLine (self,line):

        if self.warnAboutUnderindentedLines:
            self.error(
                'underindented line.\n' +
                'Extra leading whitespace will be added\n' + line)
    #@+node:ekr.20070703122141.78: *3* error, oops, report and warning
    def error (self,s):
        self.errors += 1
        self.importCommands.errors += 1
        if g.unitTesting:
            if self.errors == 1:
                g.app.unitTestDict ['actualErrorMessage'] = s
            g.app.unitTestDict ['actualErrors'] = self.errors
            if 0: # For debugging unit tests.
                g.trace(g.callers())
                g.error('',s)
        else:
            g.error('Error:',s)

    def oops (self):
        g.pr('baseScannerClass oops: %s must be overridden in subclass' % g.callers())

    def report (self,message):
        if self.strict: self.error(message)
        else:           self.warning(message)

    def warning (self,s):
        if not g.unitTesting:
            g.warning('Warning:',s)
    #@+node:ekr.20070706084535.1: *3* Parsing
    #@+at Scan and skipDecls would typically not be overridden.
    #@+node:ekr.20071201072917: *4* adjustDefStart
    def adjustDefStart (self,unused_s,i):

        '''A hook to allow the Python importer to adjust the 
        start of a class or function to include decorators.'''

        return i
    #@+node:ekr.20070707150022: *4* extendSignature
    def extendSignature(self,unused_s,i):

        '''Extend the signature line if appropriate.
        The text *must* end with a newline.

        For example, the Python scanner appends docstrings if they exist.'''

        return i
    #@+node:ekr.20071017132056: *4* getIndent
    def getIndent (self,s,i):

        j,junk = g.getLine(s,i)
        junk,indent = g.skip_leading_ws_with_indent(s,j,self.tab_width)
        return indent
    #@+node:ekr.20070706101600: *4* scan & scanHelper
    def scan (self,s,parent):

        '''A language independent scanner: it uses language-specific helpers.

        Create a child of self.root for:
        - Leading outer-level declarations.
        - Outer-level classes.
        - Outer-level functions.
        '''

        # Init the parser status ivars.
        self.methodsSeen = False

        # Create the initial body text in the root.
        self.putRootText(parent)

        # Parse the decls.
        if self.hasDecls:
            i = self.skipDecls(s,0,len(s),inClass=False)
            decls = s[:i]
        else:
            i,decls = 0,''

        # Create the decls node.
        if decls: self.createDeclsNode(parent,decls)

        # Scan the rest of the file.
        start,junk,junk = self.scanHelper(s,i,end=len(s),parent=parent,kind='outer')

        # Finish adding to the parent's body text.
        self.addRef(parent)
        if start < len(s):
            self.appendStringToBody(parent,s[start:])

        # Do any language-specific post-processing.
        self.endGen(s)
    #@+node:ekr.20071018084830: *5* scanHelper (baseScannerClass)
    def scanHelper(self,s,i,end,parent,kind):

        '''Common scanning code used by both scan and putClassHelper.'''

        # g.trace(g.callers())
        # g.trace('i',i,g.get_line(s,i))
        assert kind in ('class','outer')
        start = i ; putRef = False ; bodyIndent = None
        # Major change: 2011/11/11: prevent scanners from going beyond end.
        if self.hasNestedClasses and end < len(s):
            s = s[:end] # Potentially expensive, but unavoidable.
        # if g.unitTesting: g.pdb()
        while i < end:
            progress = i
            if s[i] in (' ','\t','\n'):
                i += 1 # Prevent lookahead below, and speed up the scan.
            elif self.startsComment(s,i):
                i = self.skipComment(s,i)
            elif self.startsString(s,i):
                i = self.skipString(s,i)
            elif self.startsClass(s,i):  # Sets sigStart,sigEnd & codeEnd ivars.
                putRef = True
                if bodyIndent is None: bodyIndent = self.getIndent(s,i)
                end2 = self.codeEnd # putClass may change codeEnd ivar.
                self.putClass(s,i,self.sigEnd,self.codeEnd,start,parent)
                i = start = end2
            elif self.startsFunction(s,i): # Sets sigStart,sigEnd & codeEnd ivars.
                putRef = True
                if bodyIndent is None: bodyIndent = self.getIndent(s,i)
                self.putFunction(s,self.sigStart,self.codeEnd,start,parent)
                i = start = self.codeEnd
            elif self.startsId(s,i):
                i = self.skipId(s,i)
            elif kind == 'outer' and g.match(s,i,self.outerBlockDelim1): # Do this after testing for classes.
                # i1 = i # for debugging
                i = self.skipBlock(s,i,delim1=self.outerBlockDelim1,delim2=self.outerBlockDelim2)
                # Bug fix: 2007/11/8: do *not* set start: we are just skipping the block.
            else: i += 1
            if progress >= i:
                # g.pdb()
                i = self.skipBlock(s,i,delim1=self.outerBlockDelim1,delim2=self.outerBlockDelim2)
            assert progress < i,'i: %d, ch: %s' % (i,repr(s[i]))

        return start,putRef,bodyIndent
    #@+node:ekr.20111108111156.9785: *4* Parser skip methods (baseScannerClass)
    #@+node:ekr.20111103073536.16599: *5* isSpace
    def isSpace(self,s,i):

        '''Return true if s[i] is a tokenizer space.'''

        # g.trace(repr(s[i]),i < len(s) and s[i] != '\n' and s[i].isspace())

        return i < len(s) and s[i] != '\n' and s[i].isspace()
    #@+node:ekr.20070712075148: *5* skipArgs
    def skipArgs (self,s,i,kind):

        '''Skip the argument or class list.  Return i, ok

        kind is in ('class','function')'''

        start = i
        i = g.skip_ws_and_nl(s,i)
        if not g.match(s,i,'('):
            return start,kind == 'class'

        i = self.skipParens(s,i)
        # skipParens skips the ')'
        if i >= len(s):
            return start,False
        else:
            return i,True 
    #@+node:ekr.20070707073859: *5* skipBlock (baseScannerClass)
    def skipBlock(self,s,i,delim1=None,delim2=None):

        '''Skip from the opening delim to *past* the matching closing delim.

        If no matching is found i is set to len(s)'''

        trace = False and not g.unitTesting
        verbose = False
        if delim1 is None: delim1 = self.blockDelim1
        if delim2 is None: delim2 = self.blockDelim2
        match1 = g.choose(len(delim1)==1,g.match,g.match_word)
        match2 = g.choose(len(delim2)==1,g.match,g.match_word)
        assert match1(s,i,delim1)
        level,start,startIndent = 0,i,self.startSigIndent
        if trace and verbose:
            g.trace('***','startIndent',startIndent)
        while i < len(s):
            progress = i
            if g.is_nl(s,i):
                backslashNewline = i > 0 and g.match(s,i-1,'\\\n')
                i = g.skip_nl(s,i)
                if not backslashNewline and not g.is_nl(s,i):
                    j, indent = g.skip_leading_ws_with_indent(s,i,self.tab_width)
                    line = g.get_line(s,j)
                    if trace and verbose: g.trace('indent',indent,line)
                    if indent < startIndent and line.strip():
                        # An non-empty underindented line.
                        # Issue an error unless it contains just the closing bracket.
                        if level == 1 and match2(s,j,delim2):
                            pass
                        else:
                            if j not in self.errorLines: # No error yet given.
                                self.errorLines.append(j)
                                self.underindentedLine(line)
            elif s[i] in (' ','\t',):
                i += 1 # speed up the scan.
            elif self.startsComment(s,i):
                i = self.skipComment(s,i)
            elif self.startsString(s,i):
                i = self.skipString(s,i)
            elif match1(s,i,delim1):
                level += 1 ; i += len(delim1)
            elif match2(s,i,delim2):
                level -= 1 ; i += len(delim2)
                # Skip junk following Pascal 'end'
                for z in self.blockDelim2Cruft:
                    i2 = self.skipWs(s,i)
                    if g.match(s,i2,z):
                        i = i2 + len(z)
                        break
                if level <= 0:
                    # 2010/09/20
                    # Skip a single-line comment if it exists.
                    j = self.skipWs(s,i)
                    if (g.match(s,j,self.lineCommentDelim) or
                        g.match(s,j,self.lineCommentDelim2)
                    ):
                        i = g.skip_to_end_of_line(s,i)
                    if trace: g.trace('returns:\n\n%s\n\n' % s[start:i])
                    return i

            else: i += 1
            assert progress < i

        self.error('no block: %s' % self.root.h)
        if 1:
            i,j = g.getLine(s,start)
            g.trace(i,s[i:j])
        else:
            if trace: g.trace('** no block')
        return start+1 # 2012/04/04: Ensure progress in caller.
    #@+node:ekr.20070712091019: *5* skipCodeBlock (baseScannerClass)
    def skipCodeBlock (self,s,i,kind):

        '''Skip the code block in a function or class definition.'''

        trace = False
        start = i
        i = self.skipBlock(s,i,delim1=None,delim2=None)
        if self.sigFailTokens:
            i = self.skipWs(s,i)
            for z in self.sigFailTokens:
                if g.match(s,i,z):
                    if trace: g.trace('failtoken',z)
                    return start,False
        if i > start:
            i = self.skipNewline(s,i,kind)
        if trace:
            # g.trace(g.callers())
            # g.trace('returns...\n',g.listToString(g.splitLines(s[start:i])))
            g.trace('returns:\n\n%s\n\n' % s[start:i])
        return i,True
    #@+node:ekr.20070711104014: *5* skipComment & helper
    def skipComment (self,s,i):

        '''Skip a comment and return the index of the following character.'''

        if g.match(s,i,self.lineCommentDelim) or g.match(s,i,self.lineCommentDelim2):
            return g.skip_to_end_of_line(s,i)
        else:
            return self.skipBlockComment(s,i)
    #@+node:ekr.20070707074541: *6* skipBlockComment
    def skipBlockComment (self,s,i):

        '''Skip past a block comment.'''

        start = i

        # Skip the opening delim.
        if g.match(s,i,self.blockCommentDelim1):
            delim2 = self.blockCommentDelim2
            i += len(self.blockCommentDelim1)
        elif g.match(s,i,self.blockCommentDelim1_2):
            i += len(self.blockCommentDelim1_2)
            delim2 = self.blockCommentDelim2_2
        else:
            assert False

        # Find the closing delim.
        k = s.find(delim2,i)
        if k == -1:
            self.error('Run on block comment: ' + s[start:i])
            return len(s)
        else:
            return k + len(delim2)
    #@+node:ekr.20070707080042: *5* skipDecls (baseScannerClass)
    def skipDecls (self,s,i,end,inClass):

        '''Skip everything until the start of the next class or function.

        The decls *must* end in a newline.'''

        trace = False or self.trace
        start = i ; prefix = None
        classOrFunc = False
        if trace: g.trace(g.callers())
        # Major change: 2011/11/11: prevent scanners from going beyond end.
        if self.hasNestedClasses and end < len(s):
            s = s[:end] # Potentially expensive, but unavoidable.
        while i < end:
            progress = i
            if s[i] in (' ','\t','\n'):
                i += 1 # Prevent lookahead below, and speed up the scan.
            elif self.startsComment(s,i):
                # Add the comment to the decl if it *doesn't* start the line.
                i2,junk = g.getLine(s,i)
                i2 = self.skipWs(s,i2)
                if i2 == i and prefix is None:
                    prefix = i2 # Bug fix: must include leading whitespace in the comment.
                i = self.skipComment(s,i)
            elif self.startsString(s,i):
                i = self.skipString(s,i)
                prefix = None
            elif self.startsClass(s,i):
                # Important: do not include leading ws in the decls.
                classOrFunc = True
                i = g.find_line_start(s,i)
                i = self.adjustDefStart(s,i)
                break
            elif self.startsFunction(s,i):
                # Important: do not include leading ws in the decls.
                classOrFunc = True
                i = g.find_line_start(s,i)
                i = self.adjustDefStart(s,i)
                break
            elif self.startsId(s,i):
                i = self.skipId(s,i)
                prefix = None
            # Don't skip outer blocks: they may contain classes.
            elif g.match(s,i,self.outerBlockDelim1):
                if self.outerBlockEndsDecls:
                    break
                else:
                    i = self.skipBlock(s,i,delim1=self.outerBlockDelim1,delim2=self.outerBlockDelim2)
            else:
                i += 1 ;  prefix = None
            assert(progress < i)

        if prefix is not None:
            i = g.find_line_start(s,prefix) # i = prefix
        decls = s[start:i]
        if inClass and not classOrFunc:
            # Don't return decls if a class contains nothing but decls.
            if trace and decls.strip(): g.trace('**class is all decls...\n',decls)
            return start
        elif decls.strip(): 
            if trace or self.trace: g.trace('\n'+decls)
            return i
        else: # Ignore empty decls.
            return start
    #@+node:ekr.20070707094858.1: *5* skipId
    def skipId (self,s,i):

        return g.skip_id(s,i,chars=self.extraIdChars)
    #@+node:ekr.20070730134936: *5* skipNewline (baseScannerClass)
    def skipNewline(self,s,i,kind):

        '''Skip whitespace and comments up to a newline, then skip the newline.
        Issue an error if no newline is found.'''

        while i < len(s):
            i = self.skipWs(s,i)
            if self.startsComment(s,i):
                i = self.skipComment(s,i)
            else: break

        if i >= len(s):
            return len(s)

        if g.match(s,i,'\n'):
            i += 1
        else:
            self.error(
                '%s %s does not end in a newline; one will be added\n%s' % (
                    kind,self.sigId,g.get_line(s,i)))
        return i
    #@+node:ekr.20070712081451: *5* skipParens
    def skipParens (self,s,i):

        '''Skip a parenthisized list, that might contain strings or comments.'''

        return self.skipBlock(s,i,delim1='(',delim2=')')
    #@+node:ekr.20070707073627.2: *5* skipString (baseScannerClass)
    def skipString (self,s,i):

        # Returns len(s) on unterminated string.
        return g.skip_string(s,i,verbose=False)
    #@+node:ekr.20111101052702.16720: *5* skipWs
    def skipWs (self,s,i):

        return g.skip_ws(s,i)
    #@+node:ekr.20070711132314: *4* startsClass/Function (baseClass) & helpers
    # We don't expect to override this code, but subclasses may override the helpers.

    def startsClass (self,s,i):
        '''Return True if s[i:] starts a class definition.
        Sets sigStart, sigEnd, sigId and codeEnd ivars.'''
        val = self.hasClasses and self.startsHelper(s,i,kind='class',tags=self.classTags)
        return val

    def startsFunction (self,s,i):
        '''Return True if s[i:] starts a function.
        Sets sigStart, sigEnd, sigId and codeEnd ivars.'''
        val = self.hasFunctions and self.startsHelper(s,i,kind='function',tags=self.functionTags)
        return val
    #@+node:ekr.20070711134534: *5* getSigId
    def getSigId (self,ids):

        '''Return the signature's id.

        By default, this is the last id in the ids list.'''

        return ids and ids[-1]
    #@+node:ekr.20070711140703: *5* skipSigStart
    def skipSigStart (self,s,i,kind,tags):

        '''Skip over the start of a function/class signature.

        tags is in (self.classTags,self.functionTags).

        Return (i,ids) where ids is list of all ids found, in order.'''

        trace = False and self.trace # or kind =='function'
        ids = [] ; classId = None
        if trace: g.trace('*entry',kind,i,s[i:i+20])
        start = i
        while i < len(s):
            j = g.skip_ws_and_nl(s,i)
            for z in self.sigFailTokens:
                if g.match(s,j,z):
                    if trace: g.trace('failtoken',z,'ids',ids)
                    return start, [], None
            for z in self.sigHeadExtraTokens:
                if g.match(s,j,z):
                    i += len(z) ; break
            else:
                i = self.skipId(s,j)
                theId = s[j:i]
                if theId and theId in tags: classId = theId
                if theId: ids.append(theId)
                else: break

        if trace: g.trace('*exit ',kind,i,i < len(s) and s[i],ids,classId)
        return i, ids, classId
    #@+node:ekr.20070712082913: *5* skipSigTail
    def skipSigTail(self,s,i,kind):

        '''Skip from the end of the arg list to the start of the block.'''

        trace = False and self.trace
        start = i
        i = self.skipWs(s,i)
        for z in self.sigFailTokens:
            if g.match(s,i,z):
                if trace: g.trace('failToken',z,'line',g.skip_line(s,i))
                return i,False
        while i < len(s):
            if self.startsComment(s,i):
                i = self.skipComment(s,i)
            elif g.match(s,i,self.blockDelim1):
                if trace: g.trace(repr(s[start:i]))
                return i,True
            else:
                i += 1
        if trace: g.trace('no block delim')
        return i,False
    #@+node:ekr.20070712112008: *5* startsHelper (baseScannerClass)
    def startsHelper(self,s,i,kind,tags,tag=None):
        '''
        tags is a list of id's.  tag is a debugging tag.
        return True if s[i:] starts a class or function.
        Sets sigStart, sigEnd, sigId and codeEnd ivars.'''

        trace = False or self.trace
        verbose = False # kind=='function'
        self.codeEnd = self.sigEnd = self.sigId = None
        self.sigStart = i

        # Underindented lines can happen in any language, not just Python.
        # The skipBlock method of the base class checks for such lines.
        self.startSigIndent = self.getLeadingIndent(s,i)

        # Get the tag that starts the class or function.
        j = g.skip_ws_and_nl(s,i)
        i = self.skipId(s,j)
        self.sigId = theId = s[j:i] # Set sigId ivar 'early' for error messages.
        if not theId: return False

        if tags:
            if self.caseInsensitive:
                theId = theId.lower()
            if theId not in tags:
                if trace and verbose:
                    # g.trace('**** %s theId: %s not in tags: %s' % (kind,theId,tags))
                    g.trace('%8s: ignoring %s' % (kind,theId))
                return False

        if trace and verbose: g.trace('kind',kind,'id',theId)

        # Get the class/function id.
        if kind == 'class' and self.sigId in self.anonymousClasses:
            # A hack for Delphi Pascal: interfaces have no id's.
            # g.trace('anonymous',self.sigId)
            classId = theId
            sigId = ''
        else:
            i, ids, classId = self.skipSigStart(s,j,kind,tags) # Rescan the first id.
            sigId = self.getSigId(ids)
            if not sigId:
                if trace and verbose: g.trace('**no sigId',g.get_line(s,i))
                return False

        if self.output_indent < self.startSigIndent:
            if trace: g.trace('**over-indent',sigId)
                #,'output_indent',self.output_indent,'startSigIndent',self.startSigIndent)
            return False

        # Skip the argument list.
        i, ok = self.skipArgs(s,i,kind)
        if not ok:
            if trace and verbose: g.trace('no args',g.get_line(s,i))
            return False
        i = g.skip_ws_and_nl(s,i)

        # Skip the tail of the signature
        i, ok = self.skipSigTail(s,i,kind)
        if not ok:
            if trace and verbose: g.trace('no tail',g.get_line(s,i))
            return False
        sigEnd = i

        # A trick: make sure the signature ends in a newline,
        # even if it overlaps the start of the block.
        if not g.match(s,sigEnd,'\n') and not g.match(s,sigEnd-1,'\n'):
            if trace and verbose: g.trace('extending sigEnd')
            sigEnd = g.skip_line(s,sigEnd)

        if self.blockDelim1:
            i = g.skip_ws_and_nl(s,i)
            if kind == 'class' and self.sigId in self.anonymousClasses:
                pass # Allow weird Pascal unit's.
            elif not g.match(s,i,self.blockDelim1):
                if trace and verbose: g.trace('no block',g.get_line(s,i))
                return False

        i,ok = self.skipCodeBlock(s,i,kind)
        if not ok: return False
            # skipCodeBlock skips the trailing delim.

        # Success: set the ivars.
        self.sigStart = self.adjustDefStart(s,self.sigStart)
        self.codeEnd = i
        self.sigEnd = sigEnd
        self.sigId = sigId
        self.classId = classId

        # Note: backing up here is safe because
        # we won't back up past scan's 'start' point.
        # Thus, characters will never be output twice.
        k = self.sigStart
        if not g.match(s,k,'\n'):
            self.sigStart = g.find_line_start(s,k)

        # Issue this warning only if we have a real class or function.
        if 0: # wrong.
            if s[self.sigStart:k].strip():
                self.error('%s definition does not start a line\n%s' % (
                    kind,g.get_line(s,k)))

        if trace:
            if verbose:
                g.trace(kind,'returns:\n%s' % s[self.sigStart:i])
            else:
                first_line = g.splitLines(s[self.sigStart:i])[0]
                g.trace(kind,first_line.rstrip())
        return True
    #@+node:ekr.20070711104014.1: *4* startsComment
    def startsComment (self,s,i):

        return (
            g.match(s,i,self.lineCommentDelim) or
            g.match(s,i,self.lineCommentDelim2) or
            g.match(s,i,self.blockCommentDelim1) or
            g.match(s,i,self.blockCommentDelim1_2)
        )
    #@+node:ekr.20070707094858.2: *4* startsId
    def startsId(self,s,i):

        return g.is_c_id(s[i:i+1])
    #@+node:ekr.20070707172732.1: *4* startsString
    def startsString(self,s,i):

        return g.match(s,i,'"') or g.match(s,i,"'")
    #@+node:ekr.20111103073536.16583: *3* Tokenizing (baseScannerClass)
    #@+node:ekr.20111103073536.16586: *4* skip...Token (baseScannerClass)
    def skipCommentToken (self,s,i):
        j = self.skipComment(s,i)
        return j,s[i:j]

    def skipIdToken (self,s,i):
        j = self.skipId(s,i)
        return j,s[i:j]

    def skipNewlineToken (self,s,i):
        return i+1,'\n'

    def skipOtherToken (self,s,i):
        return i+1,s[i]

    def skipStringToken(self,s,i):
        j = self.skipString(s,i)
        return j,s[i:j]

    def skipWsToken(self,s,i):
        j = i
        while i < len(s) and s[i] != '\n' and s[i].isspace():
            i += 1
        return i,s[j:i]

    #@+node:ekr.20111030155153.16703: *4* tokenize (baseScannerClass)
    def tokenize (self,s):

        '''Tokenize string s and return a list of tokens (kind,value,line_number)

        where kind is in ('comment,'id','nl','other','string','ws').

        This is used only to verify the imported text.
        '''

        result,i,line_number = [],0,0
        while i < len(s):
            progress = j = i
            ch = s[i]
            if ch == '\n':
                kind = 'nl'
                i,val = self.skipNewlineToken(s,i)
            elif ch in ' \t': # self.isSpace(s,i):
                kind = 'ws'
                i,val = self.skipWsToken(s,i)
            elif self.startsComment(s,i):
                kind = 'comment'
                i,val = self.skipCommentToken(s,i)
            elif self.startsString(s,i):
                kind = 'string'
                i,val = self.skipStringToken(s,i)
            elif self.startsId(s,i):
                kind = 'id'
                i,val = self.skipIdToken(s,i)
            else:
                kind = 'other'
                i,val = self.skipOtherToken(s,i)
            assert progress < i and j == progress
            if val:
                result.append((kind,val,line_number),)
            # Use the raw token, s[j:i] to count newlines, not the munged val.
            line_number += s[j:i].count('\n')
            # g.trace('%3s %7s %s' % (line_number,kind,repr(val[:20])))
        return result
    #@+node:ekr.20070707072749: *3* run (baseScannerClass)
    def run (self,s,parent):

        c = self.c
        self.root = root = parent.copy()
        self.file_s = s
        self.tab_width = self.importCommands.getTabWidth(p=root)
        # g.trace('tab_width',self.tab_width)
        # Create the ws equivalent to one tab.
        if self.tab_width < 0:
            self.tab_ws = ' '*abs(self.tab_width)
        else:
            self.tab_ws = '\t'

        # Init the error/status info.
        self.errors = 0
        self.errorLines = []
        self.mismatchWarningGiven = False
        changed = c.isChanged()

        # Use @verbatim to escape section references.
        # 2011/12/14: @auto never supports section references.
        if self.escapeSectionRefs and not self.atAuto: 
            s = self.escapeFalseSectionReferences(s)

        # Check for intermixed blanks and tabs.
        if self.strict or self.atAutoWarnsAboutLeadingWhitespace:
            if not self.isRst:
                self.checkBlanksAndTabs(s)

        # Regularize leading whitespace for strict languages only.
        if self.strict: s = self.regularizeWhitespace(s) 

        # Generate the nodes, including directive and section references.
        self.scan(s,parent)

        # Check the generated nodes.
        # Return True if the result is equivalent to the original file.
        ok = self.errors == 0 and self.check(s,parent)
        g.app.unitTestDict ['result'] = ok

        # Insert an @ignore directive if there were any serious problems.
        if not ok: self.insertIgnoreDirective(parent)

        if self.atAuto and ok:
            for p in root.self_and_subtree():
                p.clearDirty()
            c.setChanged(changed)
        else:
            root.setDirty(setDescendentsDirty=False)
            c.setChanged(True)
    #@+node:ekr.20071110105107: *4* checkBlanksAndTabs
    def checkBlanksAndTabs(self,s):

        '''Check for intermixed blank & tabs.'''

        # Do a quick check for mixed leading tabs/blanks.
        blanks = tabs = 0

        for line in g.splitLines(s):
            lws = line[0:g.skip_ws(line,0)]
            blanks += lws.count(' ')
            tabs += lws.count('\t')

        ok = blanks == 0 or tabs == 0

        if not ok:
            self.report('intermixed blanks and tabs')

        return ok
    #@+node:ekr.20070808115837.1: *4* regularizeWhitespace
    def regularizeWhitespace (self,s):

        '''Regularize leading whitespace in s:
        Convert tabs to blanks or vice versa depending on the @tabwidth in effect.
        This is only called for strict languages.'''

        changed = False ; lines = g.splitLines(s) ; result = [] ; tab_width = self.tab_width

        if tab_width < 0: # Convert tabs to blanks.
            for line in lines:
                i, w = g.skip_leading_ws_with_indent(line,0,tab_width)
                s = g.computeLeadingWhitespace(w,-abs(tab_width)) + line [i:] # Use negative width.
                if s != line: changed = True
                result.append(s)
        elif tab_width > 0: # Convert blanks to tabs.
            for line in lines:
                s = g.optimizeLeadingWhitespace(line,abs(tab_width)) # Use positive width.
                if s != line: changed = True
                result.append(s)

        if changed:
            action = g.choose(self.tab_width < 0,'tabs converted to blanks','blanks converted to tabs')
            message = 'inconsistent leading whitespace. %s' % action
            self.report(message)

        return ''.join(result)
    #@-others
#@-<< class baseScannerClass >>

#@+others
#@+node:ekr.20130823083943.12596: ** class recursiveImportController
class recursiveImportController():
    
    '''Recursively import all python files in a directory and clean the result.'''
    
    # There is no ctor.

    #@+others
    #@+node:ekr.20130823083943.12615: *3* ctor
    def __init__ (self,c,one_file=False,theTypes=None,safe_at_file=True,use_at_edit=False):
        
        self.c = c
        self.one_file = one_file
        self.recursive = not one_file
        self.safe_at_file = safe_at_file
        self.theTypes = theTypes
        self.use_at_edit = use_at_edit
    #@+node:ekr.20130823083943.12597: *3* Pass 1: import_dir
    def import_dir(self,root,dir_):

        c = self.c
        g.es("dir: " + dir_,color="blue")
        dirs,files,files2 = [],os.listdir(dir_),[]
        for f in files:
            path = g.os_path_join(dir_,f)
            if g.os_path_isfile(path):
                name, ext = g.os_path_splitext(f)
                if ext in self.theTypes:
                    files2.append(path)
            elif self.recursive:
                dirs.append(path)
        if files2 or dirs:
            child = root.insertAsLastChild()
            child.h = dir_
            c.selectPosition(child,enableRedrawFlag=False)
        if files2:
            if self.one_file:
                files2 = [files2[0]]
            if self.use_at_edit:
                for fn in files2:
                    parent = child or root
                    p = parent.insertAsLastChild()
                    p.h = fn.replace('\\','/')
                    s,e = g.readFileIntoString(fn,encoding='utf-8',kind='@edit')
                    p.b = s
            else:
                c.importCommands.importFilesCommand(files2,'@file',redrawFlag=False)
                    # '@auto' causes problems.
        if dirs:
            for dir_ in sorted(dirs):
                prefix = dir_
                self.import_dir(child,dir_)
    #@+node:ekr.20130823083943.12598: *3* Pass 2: clean_all & helpers
    def clean_all (self,p):

        for p in p.self_and_subtree():
            h = p.h
            if h.startswith('@file') or h.startswith('@@file'):
                i = 6 if h[1] == '@' else 5
                path = h[i:].strip()
                junk,ext = g.os_path_splitext(path)
                self.clean(p,ext)
    #@+node:ekr.20130823083943.12599: *4* clean
    def clean(self,p,ext):
        
        '''
        - Move a shebang line from the first child to the root.
        - Move a leading docstring in the first child to the root.
        - Use a section reference for declarations.
        - Remove leading and trailing blank lines from all nodes.
        - Merge a node containing nothing but comments with the next node.
        - Merge a node containing no class or def lines with the previous node.
        '''

        c = self.c
        root = p.copy()
        for tag in ('@@file','@file'):
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
            delim,junk,junk = g.set_delims_from_language(language)
        else:
            delim = None
        # g.trace('ext: %s language: %s delim: %s' % (ext,language,delim))
        if delim:
            # Do general language-dependent cleanups.
            for p in root.subtree():
                self.merge_comment_nodes(p,delim)
        if ext == 'py':
            # Do python only cleanups.
            for p in root.subtree():
                self.merge_extra_nodes(p)
            for p in root.subtree():
                self.move_decorator_lines(p)
    #@+node:ekr.20130823083943.12600: *4* clean_blank_lines
    def clean_blank_lines(self,p):
        
        '''Remove leading and trailing blank lines from all nodes.'''
        
        s = p.b
        if not s.strip():
            return
        result = g.splitLines(s)
        for i in 0,-1:
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
    def merge_comment_nodes(self,p,delim):
        
        '''Merge a node containing nothing but comments with the next node.'''
        
        if not p.hasChildren() and p.hasNext() and p.h.strip().startswith(delim):
            p2 = p.next()
            b = p.b.lstrip()
            b = b + ('\n' if b.endswith('\n') else '\n\n')
            p2.b = b + p2.b
            p.doDelete(p2)
    #@+node:ekr.20130823083943.12602: *4* merge_extra_nodes
    def merge_extra_nodes(self,p):
        
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
            h = p.h
            p.doDelete(p2)
    #@+node:ekr.20130823083943.12603: *4* move_decorator_lines
    def move_decorator_lines (self,p):
        
        '''Move trailing decorator lines to the next node.'''
        
        trace = False and not g.unitTesting
        seen = []
        p2 = p.next()
        if not p2:
            return False
        lines = g.splitLines(p.b)
        n = len(lines) -1
        while n >= 0:
            s = lines[n]
            if s.startswith('@'):
                i = g.skip_id(s,1,chars='-')
                word = s[1:i]
                if word in g.globalDirectiveList:
                    break
                else:
                    n -= 1
            else:
                break
        head = ''.join(lines[:n+1])
        tail = ''.join(lines[n+1:])
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
        p2.b = tail+nl+p2.b
        return True
    #@+node:ekr.20130823083943.12604: *4* move_doc_string
    def move_doc_string(self,root):

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
        i = s.find(delim,i+3)
        if i == -1:
            return
        doc = s[:i+3]
        p.b = s[i+3:].lstrip()
        # Move docstring to front of root.b, but after any shebang line.
        nl = '\n\n' if root.b.strip() else ''
        if root.b.startswith('@first #!'):
            lines = g.splitLines(root.b)
            root.b = lines[0] + '\n' + doc + nl + ''.join(lines[1:])
        else:
            root.b = doc + nl + root.b
    #@+node:ekr.20130823083943.12605: *4* move_shebang_line
    def move_shebang_line (self,root):
        
        '''Move a shebang line from the first child to the root.'''
        
        p = root.firstChild()
        s = p and p.b or ''
        if s.startswith('#!'):
            lines = g.splitLines(s)
            nl = '\n\n' if root.b.strip() else ''
            root.b = '@first ' + lines[0] + nl + root.b
            p.b = ''.join(lines[1:])
    #@+node:ekr.20130823083943.12606: *4* rename_decls
    def rename_decls (self,root):
        
        '''Use a section reference for declarations.'''
        
        p = root.firstChild()
        h = p and p.h or ''
        tag = 'declarations'
        if not h.endswith(tag):
            return
        if not p.b.strip():
            return # The blank node will be deleted.
        name = h[:-len(tag)].strip()
        decls = g.angleBrackets(tag)
        p.h = '%s (%s)' % (decls,name)
        i = root.b.find('@others')
        if i == -1:
            g.trace('can not happen')
        else:
            nl = '' if i == 0 else '\n'
            root.b = root.b[:i] + nl + decls + '\n' + root.b[i:]
    #@+node:ekr.20130823083943.12607: *3* Pass 3: post_process & helpers
    def post_process (self,p,prefix):
        
        '''Traverse p's tree, replacing all nodes that start with prefix
           by the smallest equivalent @path or @file node.
        '''

        root = p.copy()
        self.fix_back_slashes(root.copy())
        prefix = prefix.replace('\\','/')
        
        # self.dump_headlines(root.copy())
        if not self.use_at_edit:
            self.remove_empty_nodes(root.copy())
        self.minimize_headlines(root.copy().firstChild(),prefix)
        self.clear_dirty_bits(root.copy())
    #@+node:ekr.20130823083943.12608: *4* clear_dirty_bits
    def clear_dirty_bits (self,p):

        c = self.c
        c.setChanged(False)
        for p in p.self_and_subtree():
            p.clearDirty()
    #@+node:ekr.20130823083943.12609: *4* dump_headlines
    def dump_headlines (self,p):
        
        # show all headlines.
        for p in p.self_and_subtree():
            print(p.h)
    #@+node:ekr.20130823083943.12610: *4* fix_back_slashes
    def fix_back_slashes (self,p):
        
        '''Convert backslash to slash in all headlines.'''

        for p in p.self_and_subtree():
            s = p.h.replace('\\','/')
            if s != p.h:
                p.h = s
    #@+node:ekr.20130823083943.12611: *4* minimize_headlines
    def minimize_headlines (self,p,prefix):
        
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
                self.minimize_headlines(p,prefix)
        elif h2.find('/') <= 0 and ends_with_ext:
            if h2.startswith('/'): h2 = h2[1:]
            if self.use_at_edit:
                p.h = '@edit %s' % (h2)
            elif self.safe_at_file:
                if trace: g.trace('@@file %s' % (h2))
                p.h = '@@file %s' % (h2)
            else:
                if trace: g.trace('@file %s' % (h2))
                p.h = '@file %s' % (h2)
            # We never scan the children of @file nodes.
        else:
            if h2.startswith('/'): h2 = h2[1:]
            if trace:
                print('')
                g.trace('@path [%s/]%s' % (prefix,h2))
            p.h = '@path %s' % (h2)
            prefix2 = prefix if prefix.endswith('/') else prefix + '/'
            prefix2 = prefix2 + h2
            for p in p.children():
                self.minimize_headlines(p,prefix2)
    #@+node:ekr.20130823083943.12612: *4* remove_empty_nodes
    def remove_empty_nodes (self,p):
        
        c = self.c
        root = p.copy()
        # Restart the scan once a node is deleted.
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
    def run (self,dir_):
        
        '''Import all the .py files in dir_.'''

        try:
            c = self.c
            p = c.p
            p1 = p.copy()
            t1 = time.time()
            n = 0
            g.app.disable_redraw = True
            bunch = c.undoer.beforeChangeTree(p1)
            root = p.insertAfter()
            root.h = 'imported files'
            prefix = dir_
            self.import_dir(root.copy(),dir_)
            for p in root.self_and_subtree():
                n += 1
            if not self.use_at_edit:
                self.clean_all(root.copy())
            self.post_process(root.copy(),dir_)
            c.undoer.afterChangeTree(p1,'recursive-import',bunch)
        except Exception:
            n = 0
            g.es_exception()
        finally:
            g.app.disable_redraw = False
            root.contract()
            c.redraw(root)
        t2 = time.time()
        g.es('imported %s nodes in %2.2f sec' % (n,t2-t1))
    #@-others
#@+node:ekr.20031218072017.3241: ** Scanner classes
# All these classes are subclasses of baseScannerClass.
#@+node:edreamleo.20070710093042: *3* class cScanner
class cScanner (baseScannerClass):

    def __init__ (self,importCommands,atAuto):

        # Init the base class.
        baseScannerClass.__init__(self,importCommands,atAuto=atAuto,language='c')

        # Set the parser delims.
        self.blockCommentDelim1 = '/*'
        self.blockCommentDelim2 = '*/'
        self.blockDelim1 = '{'
        self.blockDelim2 = '}'
        self.classTags = ['class',]
        self.extraIdChars = ':'
        self.functionTags = []
        self.lineCommentDelim = '//'
        self.lineCommentDelim2 = '#' # A hack: treat preprocess directives as comments(!)
        self.outerBlockDelim1 = '{'
        self.outerBlockDelim2 = '}'
        self.outerBlockEndsDecls = False # To handle extern statement.
        self.sigHeadExtraTokens = ['*']
        self.sigFailTokens = [';','=']
#@+node:ekr.20071008130845.2: *3* class cSharpScanner
class cSharpScanner (baseScannerClass):

    def __init__ (self,importCommands,atAuto):

        # Init the base class.
        baseScannerClass.__init__(self,importCommands,atAuto=atAuto,language='c')

        # Set the parser delims.
        self.blockCommentDelim1 = '/*'
        self.blockCommentDelim2 = '*/'
        self.blockDelim1 = '{'
        self.blockDelim2 = '}'
        self.classTags = ['class','interface','namespace',]
        self.extraIdChars = ':'
        self.functionTags = []
        self.lineCommentDelim = '//'
        self.lineCommentDelim2 = None
        self.outerBlockDelim1 = '{'
        self.outerBlockDelim2 = '}'
        self.sigHeadExtraTokens = []
        self.sigFailTokens = [';','='] # Just like C.
#@+node:ekr.20070711060113: *3* class elispScanner
class elispScanner (baseScannerClass):

    #@+others
    #@+node:ekr.20070711060113.1: *4*  __init__ (elispScanner)
    def __init__ (self,importCommands,atAuto):

        # Init the base class.
        baseScannerClass.__init__(self,importCommands,atAuto=atAuto,language='lisp')

        # Set the parser delims.
        self.atAutoWarnsAboutLeadingWhitespace = False # 2010/09/29.
        self.warnAboutUnderindentedLines = False # 2010/09/29.
        self.blockCommentDelim1 = None
        self.blockCommentDelim2 = None
        self.lineCommentDelim = ';'
        self.lineCommentDelim2 = None
        self.blockDelim1 = '('
        self.blockDelim2 = ')'
        self.extraIdChars = '-'
        self.strict=False

    #@+node:ekr.20070711060113.2: *4* Overrides (elispScanner)
    # skipClass/Function/Signature are defined in the base class.
    #@+node:ekr.20070711060113.3: *5* startsClass/Function & skipSignature
    def startsClass (self,unused_s,unused_i):
        '''Return True if s[i:] starts a class definition.
        Sets sigStart, sigEnd, sigId and codeEnd ivars.'''
        return False

    def startsFunction(self,s,i):
        '''Return True if s[i:] starts a function.
        Sets sigStart, sigEnd, sigId and codeEnd ivars.'''

        self.startSigIndent = self.getLeadingIndent(s,i)
        self.sigStart = i
        self.codeEnd = self.sigEnd = self.sigId = None
        if not g.match(s,i,'('): return False

        end = self.skipBlock(s,i)
        # g.trace('%3s %15s block: %s' % (i,repr(s[i:i+10]),repr(s[i:end])))
        if not g.match(s,end-1,')'): return False

        i = g.skip_ws(s,i+1)
        if not g.match_word(s,i,'defun'): return False

        i += len('defun')
        sigEnd = i = g.skip_ws_and_nl(s,i)
        j = self.skipId(s,i) # Bug fix: 2009/09/30
        word = s[i:j]
        if not word: return False

        self.codeEnd = end + 1
        self.sigEnd = sigEnd
        self.sigId = word
        return True
    #@+node:ekr.20070711063339: *5* startsString
    def startsString(self,s,i):

        # Single quotes are not strings.
        # ?\x is the universal character escape.
        return g.match(s,i,'"') or g.match(s,i,'?\\')
    #@+node:ekr.20100929121021.13743: *5* skipBlock
    def skipBlock(self,s,i,delim1=None,delim2=None):

        # Call the base class
        i = baseScannerClass.skipBlock(self,s,i,delim1,delim2)

        # Skip the closing parens of enclosing constructs.
        # This prevents the "does not end in a newline error.
        while i < len(s) and s[i] == ')':
            i += 1

        return i
    #@+node:ekr.20100929121021.13745: *5* skipString
    def skipString (self,s,i):

        # Returns len(s) on unterminated string.
        if s.startswith('?',i):
            return min(len(s),i + 3)
        else:
            return g.skip_string(s,i,verbose=False)
    #@-others
#@+node:ekr.20100803231223.5807: *3* class iniScanner
class iniScanner (baseScannerClass):

    def __init__ (self,importCommands,atAuto):

        # Init the base class.
        baseScannerClass.__init__(self,
            importCommands,atAuto=atAuto,language='ini')

        # Override defaults defined in the base class.
        self.classTags = []
        self.functionTags = []
        self.hasClasses = False
        self.hasFunctions = True
        self.lineCommentDelim = ';'

    def startsString(self,s,i):
        return False

    #@+others
    #@+node:ekr.20100803231223.5810: *4* startsHelper (elispScanner)
    def startsHelper(self,s,i,kind,tags,tag=None):
        '''return True if s[i:] starts section.
        Sets sigStart, sigEnd, sigId and codeEnd ivars.'''

        trace = False
        self.codeEnd = self.sigEnd = self.sigId = None
        self.sigStart = i

        sigStart = i
        ok,sigId,i = self.isSectionLine(s,i)
        if not sigId or not ok:
            # if trace: g.trace('fail',repr(g.getLine(s,i)))
            return False

        i = sigEnd = g.skip_line(s,i)

        # Skip everything until the next section.
        while i < len(s):
            progress = i
            ok,junk,junk = self.isSectionLine(s,i)
            if ok: break # don't change i.
            i = g.skip_line(s,i)
            assert progress < i

        # Success: set the ivars.
        self.sigStart = sigStart
        self.codeEnd = i
        self.sigEnd = sigEnd
        self.sigId = sigId
        self.classId = None

        # Note: backing up here is safe because
        # we won't back up past scan's 'start' point.
        # Thus, characters will never be output twice.
        k = self.sigStart
        if not g.match(s,k,'\n'):
            self.sigStart = g.find_line_start(s,k)

        if trace: g.trace(sigId,'returns\n'+s[self.sigStart:i]+'\nEND')
        return True
    #@+node:ekr.20100803231223.5815: *4* isSectionLine
    def isSectionLine(self,s,i):

        i = g.skip_ws(s,i)
        if not g.match(s,i,'['):
            return False,None,i
        k = s.find('\n',i+1)
        if k == -1: k = len(s)
        j = s.find(']',i+1)
        if -1 < j < k:
            return True,s[i:j+1],i
        else:
            return False,None,i
    #@-others
#@+node:edreamleo.20070710085115: *3* class javaScanner
class javaScanner (baseScannerClass):

    #@+others
    #@+node:ekr.20071019171430: *4* javaScanner.__init__
    def __init__ (self,importCommands,atAuto):

        # Init the base class.
        baseScannerClass.__init__(self,importCommands,atAuto=atAuto,language='java')

        # Set the parser delims.
        self.blockCommentDelim1 = '/*'
        self.blockCommentDelim2 = '*/'
        self.lineCommentDelim = '//'
        self.lineCommentDelim2 = None
        self.outerBlockDelim1 = '{'
        self.classTags = ['class','interface']
        self.functionTags = []
        self.sigFailTokens = [';','='] # Just like c.
    #@+node:ekr.20071019170943: *4* javaScanner.getSigId
    def getSigId (self,ids):

        '''Return the signature's id.

        By default, this is the last id in the ids list.'''

        # Remove 'public' and 'private'
        ids2 = [z for z in ids if z not in ('public','private','final',)]

        # Remove 'extends' and everything after it.
        ids = []
        for z in ids2:
            if z == 'extends': break
            ids.append(z)

        return ids and ids[-1]
    #@-others
#@+node:ekr.20071027111225.2: *3* class JavaScriptScanner
# The syntax for patterns causes all kinds of problems...

class JavaScriptScanner (baseScannerClass):

    #@+others
    #@+node:ekr.20071027111225.3: *4* JavaScriptScanner.__init__
    def __init__ (self,importCommands,atAuto,language='javascript',alternate_language=None):

        # Init the base class.
        baseScannerClass.__init__(self,importCommands,
            atAuto=atAuto,
            language=language,
                # The language is used to set comment delims.
            alternate_language = alternate_language)
                # The language used in the @language directive.
        # Set the parser delims.
        self.blockCommentDelim1 = '/*'
        self.blockCommentDelim2 = '*/'
        self.blockDelim1 = '{'
        self.blockDelim2 = '}'
        self.hasClasses = False
        self.hasFunctions = True
        # self.ignoreBlankLines = True
        self.lineCommentDelim = '//'
        self.lineCommentDelim2 = None
        self.outerBlockDelim1 = None # For now, ignore outer blocks.
        self.outerBlockDelim2 = None
        self.classTags = []
        self.functionTags = ['function',]
        self.sigFailTokens = [';',] # ','=',] # Just like Java.
    #@+node:ekr.20071102150937: *4* startsString
    def startsString(self,s,i):

        if g.match(s,i,'"') or g.match(s,i,"'"):
            # Count the number of preceding backslashes:
            n = 0 ; j = i-1
            while j >= 0 and s[j] == '\\':
                n += 1
                j -= 1
            return (n % 2) == 0
        elif g.match(s,i,'//'):
            # Neither of these are valid in regexp literals.
            return False
        elif g.match(s,i,'/'):
            # could be a division operator or regexp literal.
            while i >= 0 and s[i-1] in ' \t\n':
                i -= 1
            if i == 0: return True
            return s[i-1] in (',([{=')
        else:
            return False
    #@+node:ekr.20071102161115: *4* skipString
    def skipString (self,s,i):

        # Returns len(s) on unterminated string.
        if s[i] in ('"',"'"):
            return g.skip_string(s,i,verbose=False)
        else:
            # Match a regexp pattern.
            delim = '/'
            assert(s[i] == delim)
            i += 1
            n = len(s)
            while i < n:
                if s[i] == delim and s[i-1] != '\\':
                    # This ignores flags, but does that matter?
                    return i + 1
                else:
                    i += 1
            return i
    #@+node:ekr.20130830084323.10544: *4* skipNewline (JavaScriptScanner)
    def skipNewline(self,s,i,kind):

        '''Skip whitespace and comments up to a newline, then skip the newline.
        
        Unlike the base class, we do *not* issue an error if no newline is found.'''

        while i < len(s):
            i = self.skipWs(s,i)
            if self.startsComment(s,i):
                i = self.skipComment(s,i)
            else: break
        if i >= len(s):
            return len(s)
        elif g.match(s,i,'\n'):
            return i+1
        else:
            g.trace(s[i:],g.callers())
            return i
    #@-others
#@+node:ekr.20070711104241.3: *3* class pascalScanner
class pascalScanner (baseScannerClass):

    #@+others
    #@+node:ekr.20080211065754: *4* skipArgs
    def skipArgs (self,s,i,kind):

        '''Skip the argument or class list.  Return i, ok

        kind is in ('class','function')'''

        # Pascal interfaces have no argument list.
        if kind == 'class':
            return i, True

        start = i
        i = g.skip_ws_and_nl(s,i)
        if not g.match(s,i,'('):
            return start,kind == 'class'

        i = self.skipParens(s,i)
        # skipParens skips the ')'
        if i >= len(s):
            return start,False
        else:
            return i,True 
    #@+node:ekr.20080211065906: *4* ctor (pascalScanner)
    def __init__ (self,importCommands,atAuto):

        # Init the base class.
        baseScannerClass.__init__(self,importCommands,atAuto=atAuto,language='pascal')

        # Set the parser overrides.
        self.anonymousClasses = ['interface']
        self.blockCommentDelim1 = '(*'
        self.blockCommentDelim1_2 = '{'
        self.blockCommentDelim2 = '*)'
        self.blockCommentDelim2_2 = '}'
        self.blockDelim1 = 'begin'
        self.blockDelim2 = 'end'
        self.blockDelim2Cruft = [';','.'] # For Delphi.
        self.classTags = ['interface']
        self.functionTags = ['function','procedure','constructor','destructor',]
        self.hasClasses = True
        self.lineCommentDelim = '//'
        self.strict = False
    #@+node:ekr.20080211070816: *4* skipCodeBlock
    def skipCodeBlock (self,s,i,kind):

        '''Skip the code block in a function or class definition.'''

        trace = False
        start = i

        if kind == 'class':
            i = self.skipInterface(s,i)
        else:
            i = self.skipBlock(s,i,delim1=None,delim2=None)

            if self.sigFailTokens:
                i = g.skip_ws(s,i)
                for z in self.sigFailTokens:
                    if g.match(s,i,z):
                        if trace: g.trace('failtoken',z)
                        return start,False

        if i > start:
            i = self.skipNewline(s,i,kind)

        if trace:
            g.trace(g.callers())
            g.trace('returns...\n',g.listToString(g.splitLines(s[start:i])))

        return i,True
    #@+node:ekr.20080211070945: *4* skipInterface
    def skipInterface(self,s,i):

        '''Skip from the opening delim to *past* the matching closing delim.

        If no matching is found i is set to len(s)'''

        trace = False
        start = i
        delim2 = 'end.'
        level = 0 ; start = i
        startIndent = self.startSigIndent
        if trace: g.trace('***','startIndent',startIndent,g.callers())
        while i < len(s):
            progress = i
            if g.is_nl(s,i):
                backslashNewline = i > 0 and g.match(s,i-1,'\\\n')
                i = g.skip_nl(s,i)
                if not backslashNewline and not g.is_nl(s,i):
                    j, indent = g.skip_leading_ws_with_indent(s,i,self.tab_width)
                    line = g.get_line(s,j)
                    if trace: g.trace('indent',indent,line)
                    if indent < startIndent and line.strip():
                        # An non-empty underindented line.
                        # Issue an error unless it contains just the closing bracket.
                        if level == 1 and g.match(s,j,delim2):
                            pass
                        else:
                            if j not in self.errorLines: # No error yet given.
                                self.errorLines.append(j)
                                self.underindentedLine(line)
            elif s[i] in (' ','\t',):
                i += 1 # speed up the scan.
            elif self.startsComment(s,i):
                i = self.skipComment(s,i)
            elif self.startsString(s,i):
                i = self.skipString(s,i)
            elif g.match(s,i,delim2):
                i += len(delim2)
                if trace: g.trace('returns\n',repr(s[start:i]))
                return i

            else: i += 1
            assert progress < i

        self.error('no interface')
        if 1:
            g.pr('** no interface **')
            i,j = g.getLine(s,start)
            g.trace(i,s[i:j])
        else:
            if trace: g.trace('** no interface')
        return start
    #@+node:ekr.20080211070056: *4* skipSigTail
    def skipSigTail(self,s,i,kind):

        '''Skip from the end of the arg list to the start of the block.'''

        trace = False and self.trace

        # Pascal interface has no tail.
        if kind == 'class':
            return i,True

        start = i
        i = g.skip_ws(s,i)
        for z in self.sigFailTokens:
            if g.match(s,i,z):
                if trace: g.trace('failToken',z,'line',g.skip_line(s,i))
                return i,False
        while i < len(s):
            if self.startsComment(s,i):
                i = self.skipComment(s,i)
            elif g.match(s,i,self.blockDelim1):
                if trace: g.trace(repr(s[start:i]))
                return i,True
            else:
                i += 1
        if trace: g.trace('no block delim')
        return i,False
    #@+node:ekr.20080211071959: *4* putClass & helpers
    def putClass (self,s,i,sigEnd,codeEnd,start,parent):

        '''Create a node containing the entire interface.'''

        # Enter a new class 1: save the old class info.
        oldMethodName = self.methodName
        oldStartSigIndent = self.startSigIndent

        # Enter a new class 2: init the new class info.
        self.indentRefFlag = None

        class_kind = self.classId
        class_name = self.sigId
        headline = '%s %s' % (class_kind,class_name)
        headline = headline.strip()
        self.methodName = headline

        # Compute the starting lines of the class.
        # prefix = self.createClassNodePrefix()

        # Create the class node.
        class_node = self.createHeadline(parent,'',headline)

        # Put the entire interface in the body.
        result = s[start:codeEnd]
        self.appendTextToClassNode(class_node,result)

        # Exit the new class: restore the previous class info.
        self.methodName = oldMethodName
        self.startSigIndent = oldStartSigIndent
    #@-others
#@+node:ekr.20100219075946.5742: *3* class phpScanner
class phpScanner (baseScannerClass):

    #@+others
    #@+node:ekr.20100219075946.5743: *4*  __init__(phpScanner)
    def __init__ (self,importCommands,atAuto):

        # Init the base class.
        baseScannerClass.__init__(self,importCommands,atAuto=atAuto,language='php')

        # Set the parser delims.
        self.blockCommentDelim1 = '/*'
        self.blockCommentDelim2 = '*/'
        self.lineCommentDelim = '//'
        self.lineCommentDelim2 = '#'
        self.blockDelim1 = '{'
        self.blockDelim2 = '}'

        self.hasClasses = True # 2010/02/19
        self.hasFunctions = True

        self.functionTags = ['function']

        # The valid characters in an id
        self.chars = list(string.ascii_letters + string.digits)
        extra = [chr(z) for z in range(127,256)]
        self.chars.extend(extra)
    #@+node:ekr.20100219075946.5744: *4* isPurePHP
    def isPurePHP (self,s):

        '''Return True if the file begins with <?php and ends with ?>'''

        s = s.strip()

        return (
            s.startswith('<?') and
            s[2:3] in ('P','p','=','\n','\r',' ','\t') and
            s.endswith('?>'))

    #@+node:ekr.20100219075946.5745: *4* Overrides
    # Does not create @first/@last nodes
    #@+node:ekr.20100219075946.5746: *5* startsString skipString
    def startsString(self,s,i):
        return g.match(s,i,'"') or g.match(s,i,"'") or g.match(s,i,'<<<')

    def skipString (self,s,i):
        if g.match(s,i,'"') or g.match(s,i,"'"):
            return g.skip_string(s,i)
        else:
            return g.skip_heredoc_string(s,i)
    #@+node:ekr.20100219075946.5747: *5* getSigId
    def getSigId (self,ids):

        '''Return the signature's id.

        By default, this is the last id in the ids list.

        For Php, the first id is better.'''

        return ids and ids[1]
    #@-others
#@+node:ekr.20070703122141.100: *3* class pythonScanner
class pythonScanner (baseScannerClass):

    #@+others
    #@+node:ekr.20070703122141.101: *4*  __init__ (pythonScanner)
    def __init__ (self,importCommands,atAuto):

        # Init the base class.
        baseScannerClass.__init__(self,importCommands,atAuto=atAuto,language='python')

        # Set the parser delims.
        self.lineCommentDelim = '#'
        self.classTags = ['class',]
        self.functionTags = ['def',]
        self.ignoreBlankLines = True
        self.blockDelim1 = self.blockDelim2 = None
            # Suppress the check for the block delim.
            # The check is done in skipSigTail.
        self.strict = True
    #@+node:ekr.20071201073102.1: *4* adjustDefStart (pythonScanner)
    def adjustDefStart (self,s,i):
        '''A hook to allow the Python importer to adjust the 
        start of a class or function to include decorators.
        '''
        # Invariant: i does not change.
        # Invariant: start is the present return value.  
        try:
            assert s[i] != '\n'
            start = j = g.find_line_start(s,i) if i > 0 else 0
            # g.trace('entry',j,i,repr(s[j:i+10]))
            assert j == 0 or s[j-1] == '\n'
            while j > 0:
                progress = j
                j1 = j = g.find_line_start(s,j-2)
                # g.trace('line',repr(s[j:progress]))
                j = g.skip_ws(s,j)
                if not g.match(s,j,'@'):
                    break
                k = g.skip_id(s,j+1)
                word = s[j:k]
                # Leo directives halt the scan.
                if word and word in g.globalDirectiveList:
                    break
                # A decorator.
                start = j = j1
                assert j < progress
            # g.trace('**returns %s, %s' % (repr(s[start:i]),repr(s[i:i+20])))
            return start
        except AssertionError:
            g.es_exception()
            return i
    #@+node:ekr.20070707113839: *4* extendSignature
    def extendSignature(self,s,i):

        '''Extend the text to be added to the class node following the signature.

        The text *must* end with a newline.'''

        # Add a docstring to the class node,
        # And everything on the line following it
        j = g.skip_ws_and_nl(s,i)
        if g.match(s,j,'"""') or g.match(s,j,"'''"):
            j = g.skip_python_string(s,j)
            if j < len(s): # No scanning error.
                # Return the docstring only if nothing but whitespace follows.
                j = g.skip_ws(s,j)
                if g.is_nl(s,j):
                    return j + 1

        return i
    #@+node:ekr.20101103093942.5935: *4* findClass (pythonScanner)
    def findClass(self,p):

        '''Return the index end of the class or def in a node, or -1.'''

        s,i = p.b,0
        while i < len(s):
            progress = i
            if s[i] in (' ','\t','\n'):
                i += 1
            elif self.startsComment(s,i):
                i = self.skipComment(s,i)
            elif self.startsString(s,i):
                i = self.skipString(s,i)
            elif self.startsClass(s,i):
                return 'class',self.sigStart,self.codeEnd
            elif self.startsFunction(s,i):
                return 'def',self.sigStart,self.codeEnd
            elif self.startsId(s,i):
                i = self.skipId(s,i)
            else:
                i += 1
            assert progress < i,'i: %d, ch: %s' % (i,repr(s[i]))

        return None,-1,-1
    #@+node:ekr.20070712090019.1: *4* skipCodeBlock (pythonScanner) & helpers
    def skipCodeBlock (self,s,i,kind):

        trace = False ; verbose = True
        # if trace: g.trace('***',g.callers())
        startIndent = self.startSigIndent
        if trace: g.trace('startIndent',startIndent)
        assert startIndent is not None
        i = start = g.skip_ws_and_nl(s,i)
        parenCount = 0
        underIndentedStart = None # The start of trailing underindented blank or comment lines.
        while i < len(s):
            progress = i
            ch = s[i]
            if g.is_nl(s,i):
                if trace and verbose: g.trace(g.get_line(s,i))
                backslashNewline = (i > 0 and g.match(s,i-1,'\\\n'))
                if backslashNewline:
                    # An underindented line, including docstring,
                    # does not end the code block.
                    i += 1 # 2010/11/01
                else:
                    i = g.skip_nl(s,i)
                    j = g.skip_ws(s,i)
                    if g.is_nl(s,j):
                        pass # We have already made progress.
                    else:
                        i,underIndentedStart,breakFlag = self.pythonNewlineHelper(
                            s,i,parenCount,startIndent,underIndentedStart)
                        if breakFlag: break
            elif ch == '#':
                i = g.skip_to_end_of_line(s,i)
            elif ch == '"' or ch == '\'':
                i = g.skip_python_string(s,i)
            elif ch in '[{(':
                i += 1 ; parenCount += 1
                # g.trace('ch',ch,parenCount)
            elif ch in ']})':
                i += 1 ; parenCount -= 1
                # g.trace('ch',ch,parenCount)
            else: i += 1
            assert(progress < i)

        # The actual end of the block.
        if underIndentedStart is not None:
            i = underIndentedStart
            if trace: g.trace('***backtracking to underindent range')
            if trace: g.trace(g.get_line(s,i))

        if 0 < i < len(s) and not g.match(s,i-1,'\n'):
            g.trace('Can not happen: Python block does not end in a newline.')
            g.trace(g.get_line(s,i))
            return i,False

        # 2010/02/19: Include all following material
        # until the next 'def' or 'class'
        i = self.skipToTheNextClassOrFunction(s,i,startIndent)

        if (trace or self.trace) and s[start:i].strip():
            g.trace('%s returns\n' % (kind) + s[start:i])
        return i,True
    #@+node:ekr.20070801080447: *5* pythonNewlineHelper
    def pythonNewlineHelper (self,s,i,parenCount,startIndent,underIndentedStart):

        trace = False
        breakFlag = False
        j, indent = g.skip_leading_ws_with_indent(s,i,self.tab_width)
        if trace: g.trace(
            'startIndent',startIndent,'indent',indent,'parenCount',parenCount,
            'line',repr(g.get_line(s,j)))
        if indent <= startIndent and parenCount == 0:
            # An underindented line: it ends the block *unless*
            # it is a blank or comment line or (2008/9/1) the end of a triple-quoted string.
            if g.match(s,j,'#'):
                if trace: g.trace('underindent: comment')
                if underIndentedStart is None: underIndentedStart = i
                i = j
            elif g.match(s,j,'\n'):
                if trace: g.trace('underindent: blank line')
                # Blank lines never start the range of underindented lines.
                i = j
            else:
                if trace: g.trace('underindent: end of block')
                breakFlag = True # The actual end of the block.
        else:
            if underIndentedStart and g.match(s,j,'\n'):
                # Add the blank line to the underindented range.
                if trace: g.trace('properly indented blank line extends underindent range')
            elif underIndentedStart and g.match(s,j,'#'):
                # Add the (properly indented!) comment line to the underindented range.
                if trace: g.trace('properly indented comment line extends underindent range')
            elif underIndentedStart is None:
                pass
            else:
                # A properly indented non-comment line.
                # Give a message for all underindented comments in underindented range.
                if trace: g.trace('properly indented line generates underindent errors')
                s2 = s[underIndentedStart:i]
                lines = g.splitlines(s2)
                for line in lines:
                    if line.strip():
                        junk, indent = g.skip_leading_ws_with_indent(line,0,self.tab_width)
                        if indent <= startIndent:
                            if j not in self.errorLines: # No error yet given.
                                self.errorLines.append(j)
                                self.underindentedComment(line)
                underIndentedStart = None
        if trace: g.trace('breakFlag',breakFlag,'returns',i,'underIndentedStart',underIndentedStart)
        return i,underIndentedStart,breakFlag
    #@+node:ekr.20100223094350.5834: *5* skipToTheNextClassOrFunction (New in 4.8)
    def skipToTheNextClassOrFunction(self,s,i,lastIndent):

        '''Skip to the next python def or class.
        Return the original i if nothing more is found.
        This allows the "if __name__ == '__main__' hack
        to appear at the top level.'''

        return i # A rewrite is needed.
    #@+node:ekr.20070803101619: *4* skipSigTail
    # This must be overridden in order to handle newlines properly.

    def skipSigTail(self,s,i,kind):

        '''Skip from the end of the arg list to the start of the block.'''

        while i < len(s):
            ch = s[i]
            if ch == '\n':
                break
            elif ch in (' ','\t',):
                i += 1
            elif self.startsComment(s,i):
                i = self.skipComment(s,i)
            else:
                break

        return i,g.match(s,i,':')
    #@+node:ekr.20070707073627.4: *4* skipString
    def skipString (self,s,i):

        # Returns len(s) on unterminated string.
        return g.skip_python_string(s,i,verbose=False)
    #@-others
#@+node:ekr.20090501095634.41: *3* class rstScanner
class rstScanner (baseScannerClass):

    #@+others
    #@+node:ekr.20090501095634.42: *4*  __init__ (rstScanner)
    def __init__ (self,importCommands,atAuto):

        # Init the base class.
        baseScannerClass.__init__(self,importCommands,atAuto=atAuto,language='rest')

        # Scanner overrides
        self.atAutoWarnsAboutLeadingWhitespace = True
        self.blockDelim1 = self.blockDelim2 = None
        self.classTags = []
        self.escapeSectionRefs = False
        self.functionSpelling = 'section'
        self.functionTags = []
        self.hasClasses = False
        self.ignoreBlankLines = True
        self.isRst = True
        self.lineCommentDelim = '..'
        self.outerBlockDelim1 = None
        self.sigFailTokens = []
        self.strict = False # Mismatches in leading whitespace are irrelevant.

        # Ivars unique to rst scanning & code generation.
        self.lastParent = None # The previous parent.
        self.lastSectionLevel = 0 # The section level of previous section.
        self.sectionLevel = 0 # The section level of the just-parsed section.
        self.underlineCh = '' # The underlining character of the last-parsed section.
        self.underlines = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~" # valid rst underlines.
        self.underlines1 = [] # Underlining characters for underlines.
        self.underlines2 = [] # Underlining characters for over/underlines.
    #@+node:ekr.20090512080015.5798: *4* adjustParent
    def adjustParent (self,parent,headline):

        '''Return the proper parent of the new node.'''

        trace = False and not g.unitTesting

        level,lastLevel = self.sectionLevel,self.lastSectionLevel
        lastParent = self.lastParent

        if trace: g.trace('**entry level: %s lastLevel: %s lastParent: %s' % (
            level,lastLevel,lastParent and lastParent.h or '<none>'))

        if self.lastParent:

            if level <= lastLevel:
                parent = lastParent.parent()
                while level < lastLevel:
                    level += 1
                    parent = parent.parent()
            else: # level > lastLevel.
                level -= 1
                parent = lastParent
                while level > lastLevel:
                    level -= 1
                    h2 = '@rst-no-head %s' % headline
                    body = ''
                    parent = self.createFunctionNode(h2,body,parent)

        else:
            assert self.root
            self.lastParent = self.root

        if not parent: parent = self.root

        if trace: g.trace('level %s lastLevel %s %s returns %s' % (
            level,lastLevel,headline,parent.h))

        #self.lastSectionLevel = self.sectionLevel
        self.lastParent = parent.copy()
        return parent.copy()
    #@+node:ekr.20091229090857.11694: *4* computeBody (rstScanner)
    def computeBody (self,s,start,sigStart,codeEnd):

        trace = False and not g.unitTesting

        body1 = s[start:sigStart]
        # Adjust start backwards to get a better undent.
        if body1.strip():
            while start > 0 and s[start-1] in (' ','\t'):
                start -= 1

        # Never indent any text; discard the entire signature.
        body1 = s[start:sigStart]
        body2 = s[self.sigEnd+1:codeEnd]
        body2 = g.removeLeadingBlankLines(body2) # 2009/12/28
        body = body1 + body2

        # Don't warn about missing tail newlines: they will be added.
        if trace: g.trace('body: %s' % repr(body))
        return body1,body2
    #@+node:ekr.20090512080015.5797: *4* computeSectionLevel
    def computeSectionLevel (self,ch,kind):

        '''Return the section level of the underlining character ch.'''

        # Can't use g.choose here.
        if kind == 'over':
            assert ch in self.underlines2
            level = 0
        else:
            level = 1 + self.underlines1.index(ch)

        if False:
            g.trace('level: %s kind: %s ch: %s under2: %s under1: %s' % (
                level,kind,ch,self.underlines2,self.underlines1))

        return level
    #@+node:ekr.20090512153903.5810: *4* createDeclsNode
    def createDeclsNode (self,parent,s):

        '''Create a child node of parent containing s.'''

        # Create the node for the decls.
        headline = '@rst-no-head %s declarations' % self.methodName
        body = self.undentBody(s)
        self.createHeadline(parent,body,headline)
    #@+node:ekr.20090502071837.2: *4* endGen
    def endGen (self,s):

        '''Remember the underlining characters in the root's uA.'''

        trace = False and not g.unitTesting
        p = self.root
        if p:
            tag = 'rst-import'
            d = p.v.u.get(tag,{})
            underlines1 = ''.join([str(z) for z in self.underlines1])
            underlines2 = ''.join([str(z) for z in self.underlines2])
            d ['underlines1'] = underlines1
            d ['underlines2'] = underlines2
            self.underlines1 = underlines1
            self.underlines2 = underlines2
            if trace: g.trace(repr(underlines1),repr(underlines2),g.callers(4))
            p.v.u [tag] = d

        # Append a warning to the root node.
        warningLines = (
            'Warning: this node is ignored when writing this file.',
            'However, @ @rst-options are recognized in this node.',
        )
        lines = ['.. %s' % (z) for z in warningLines]
        warning = '\n%s\n' % '\n'.join(lines)
        self.root.b = self.root.b + warning
    #@+node:ekr.20090501095634.46: *4* isUnderLine
    def isUnderLine(self,s):

        '''Return True if s consists of only the same rST underline character.'''

        if not s: return False
        ch1 = s[0]

        if not ch1 in self.underlines:
            return False

        for ch in s:
            if ch != ch1:
                return False

        return True
    #@+node:ekr.20090501095634.50: *4* startsComment/ID/String
    # These do not affect parsing.

    def startsComment (self,s,i):
        return False

    def startsID (self,s,i):
        return False

    def startsString (self,s,i):
        return False
    #@+node:ekr.20090501095634.45: *4* startsHelper (rstScanner)
    def startsHelper(self,s,i,kind,tags,tag=None):

        '''return True if s[i:] starts an rST section.
        Sets sigStart, sigEnd, sigId and codeEnd ivars.'''

        trace = False and not g.unitTesting
        verbose = True
        kind,name,next,ch = self.startsSection(s,i)
        if kind == 'plain': return False

        self.underlineCh = ch
        self.lastSectionLevel = self.sectionLevel
        self.sectionLevel = self.computeSectionLevel(ch,kind)
        self.sigStart = g.find_line_start(s,i)
        self.sigEnd = next
        self.sigId = name
        i = next + 1

        if trace: g.trace('sigId',self.sigId,'next',next)

        while i < len(s):
            progress = i
            i,j = g.getLine(s,i)
            kind,name,next,ch = self.startsSection(s,i)
            if trace and verbose: g.trace(kind,repr(s[i:j]))
            if kind in ('over','under'):
                break
            else:
                i = j
            assert i > progress

        self.codeEnd = i

        if trace:
            if verbose:
                g.trace('found...\n%s' % s[self.sigStart:self.codeEnd])
            else:
                g.trace('level %s %s' % (self.sectionLevel,self.sigId))
        return True
    #@+node:ekr.20090501095634.47: *4* startsSection & helper
    def startsSection (self,s,i):

        '''Scan a line and possible one or two other lines,
        looking for an underlined or overlined/underlined name.

        Return (kind,name,i):
            kind: in ('under','over','plain')
            name: the name of the underlined or overlined line.
            i: the following character if kind is not 'plain'
            ch: the underlining and possibly overlining character.
        '''

        trace = False and not g.unitTesting
        verbose = False

        # Under/overlines can not begin with whitespace.
        i1,j,nows,line = self.getLine(s,i)
        ch,kind = '','plain' # defaults.

        if nows and self.isUnderLine(line): # an overline.
            name_i = g.skip_line(s,i1)
            name_i,name_j = g.getLine(s,name_i)
            name = s[name_i:name_j].strip()
            next_i = g.skip_line(s,name_i)
            i,j,nows,line2 = self.getLine(s,next_i)
            n1,n2,n3 = len(line),len(name),len(line2)
            ch1,ch3 = line[0],line2 and line2[0]
            ok = (nows and self.isUnderLine(line2) and
                n1 >= n2 and n2 > 0 and n3 >= n2 and ch1 == ch3)
            if ok:
                i += n3
                ch,kind = ch1,'over'
                if ch1 not in self.underlines2:
                    self.underlines2.append(ch1)
                    if trace: g.trace('*** underlines2',self.underlines2,name)
                if trace and verbose:
                    g.trace('\nline  %s\nname  %s\nline2 %s' % (
                        repr(line),repr(name),repr(line2))) #,'\n',g.callers(4))
        else:
            name = line.strip()
            i = g.skip_line(s,i1)
            i,j,nows2,line2 = self.getLine(s,i)
            n1,n2 = len(name),len(line2)
            # look ahead two lines.
            i3,j3 = g.getLine(s,j)
            name2 = s[i3:j3].strip()
            i4,j4,nows4,line4 = self.getLine(s,j3)
            n3,n4 = len(name2),len(line4)
            overline = (
                nows2 and self.isUnderLine(line2) and
                nows4 and self.isUnderLine(line4) and
                n3 > 0 and n2 >= n3 and n4 >= n3)
            ok = (not overline and nows2 and self.isUnderLine(line2) and
                n1 > 0 and n2 >= n1)
            if ok:
                i += n2
                ch,kind = line2[0],'under'
                if ch not in self.underlines1:
                    self.underlines1.append(ch)
                    if trace: g.trace('*** underlines1',self.underlines1,name)
                if trace and verbose: g.trace('\nname  %s\nline2 %s' % (
                    repr(name),repr(line2)))
        return kind,name,i,ch
    #@+node:ekr.20091229075924.6234: *5* getLine
    def getLine (self,s,i):

        i,j = g.getLine(s,i)
        line = s[i:j]
        nows = i == g.skip_ws(s,i)
        line = line.strip()

        return i,j,nows,line
    #@-others
#@+node:ekr.20121011093316.10097: *3* class TypeScriptScanner(JavaScriptScanner)
class TypeScriptScanner (JavaScriptScanner):

    #@+others
    #@+node:ekr.20121011093316.10098: *4* TypeScriptScanner.__init__
    def __init__ (self,importCommands,atAuto):

        # Init the base class.
        JavaScriptScanner.__init__(self,importCommands,
            atAuto=atAuto,language='typescript',
            alternate_language='javascript')

        # Overrides of ivars.
        self.hasClasses = True
        self.classTags = ['module','class','interface',]
        self.functionTags = [
            'constructor','enum','function',
            'public','private','export',]
    #@+node:ekr.20121011093316.10110: *4* getSigId (TypeScriptScanner)
    def getSigId (self,ids):

        '''Return the signature's id.

        This is the last id of the ids list, or the id before extends anotherId.
        '''

        if len(ids) > 2 and ids[-2] == 'extends':
            return ids[-3]
        else:
            return ids and ids[-1]
    #@-others
#@+node:ekr.20120517124200.9983: *3* class vimoutlinerScanner
class vimoutlinerScanner(baseScannerClass):

    def __init__ (self,importCommands,atAuto):

        # Init the base class.
        baseScannerClass.__init__(self,
            importCommands,atAuto=atAuto,language='plain')
                # Use @language plain.

        # Overrides of base-class ivars.
        self.fullChecks = False
        self.hasDecls = False

        # The stack of valid parents at each level.
        self.parents = []

    #@+others
    #@+node:ekr.20120519091649.10016: *4* scanHelper & helpers
    # Override baseScannerClass.scanHelper.

    def scanHelper(self,s,i,end,parent,kind):

        '''Create Leo nodes for all vimoutliner lines.'''

        assert kind == 'outer' and end == len(s)
        while i < len(s):
            # Set k to the end of the line.
            progress = i
            k = g.skip_line(s,i)
            line = s[i:k] # For traces.

            # Skip leading hard tabs, ignore blanks & compute the line's level.
            level = 1 # The root has level 0.
            while i < len(s) and s[i].isspace():
                if s[i] == '\t': level += 1
                i += 1

            if i == k:
                g.trace('ignoring blank line: %s' % (repr(line)))
            elif i < len(s) and s[i] == ':':
                # Append the line to the body.
                i += 1
                if i < len(s) and s[i] == ' ':
                    i += 1
                else:
                    g.trace('missing space after colon: %s' % (repr(line)))
                p = self.findParent(level)
                p.b = p.b + s[i:k]
            else:
                putRef = True

                # Cut back the stack, then allocate a new (placeholder) node.
                self.parents = self.parents[:level]
                p = self.findParent(level)

                # Set the headline of the placeholder node.
                h = s[i:k]
                p.h = h[:-1] if h.endswith('\n') else h

            # Move to the next line.
            i = k
            assert progress < i,'i: %s %s' % (i,repr(line))

        return len(s),putRef,0 # bodyIndent not used.
    #@+node:ekr.20120517155536.10132: *5* findParent
    def findParent(self,level):

        '''Return the parent at the indicated level, allocating
        place-holder nodes as necessary.'''

        trace = False and not g.unitTesting
        assert level >= 0

        if not self.parents:
            self.parents = [self.root]

        if trace: g.trace(level,[z.h for z in self.parents])

        while level >= len(self.parents):
            b = ''
            h = 'placeholder' if level > 1 else 'declarations'
            parent = self.parents[-1]
            p = self.createHeadline(parent,b,h)
            self.parents.append(p)

        return self.parents[level]
    #@+node:ekr.20120517155536.10131: *5* createNode
    def createNode (self,b,h,level):

        parent = self.findParent(level)
        p = self.createHeadline(parent,b,h)
        self.parents = self.parents[:level+1]
        self.parents.append(p)
    #@-others
#@+node:ekr.20071214072145.1: *3* class xmlScanner & htmlScanner(xmlScanner)
#@+<< class xmlScanner (baseScannerClass) >>
#@+node:ekr.20111104032034.9866: *4* << class xmlScanner (baseScannerClass) >>
class xmlScanner (baseScannerClass):

    #@+others
    #@+node:ekr.20071214072451: *5*  ctor_(xmlScanner)
    def __init__ (self,importCommands,atAuto,tags_setting='import_xml_tags'):

        # Init the base class.
        baseScannerClass.__init__(self,importCommands,atAuto=atAuto,language='xml')
            # sets self.c

        # Set the parser delims.
        self.blockCommentDelim1 = '<!--'
        self.blockCommentDelim2 = '-->'
        self.blockDelim1 = None 
        self.blockDelim2 = None
        self.classTags = [] # Inited by import_xml_tags setting.
        self.extraIdChars = None
        self.functionTags = []
        self.lineCommentDelim = None
        self.lineCommentDelim2 = None
        self.outerBlockDelim1 = None
        self.outerBlockDelim2 = None
        self.outerBlockEndsDecls = False
        self.sigHeadExtraTokens = []
        self.sigFailTokens = []

        # Overrides more attributes.
        self.atAutoWarnsAboutLeadingWhitespace = False
        self.caseInsensitive = True
        self.hasClasses = True
        self.hasDecls = False
        self.hasFunctions = False
        self.hasNestedClasses = True
        self.ignoreBlankLines = False # The tokenizer handles this.
        self.ignoreLeadingWs = True # A drastic step, but there seems to be no other way.
        self.strict = False
        self.tags_setting = tags_setting
        self.trace = False

        self.addTags()
    #@+node:ekr.20071214131818: *5* addTags
    def addTags (self):

        '''Add items to self.class/functionTags and from settings.'''

        trace = False # and not g.unitTesting
        c = self.c

        for ivar,setting in (
            ('classTags',self.tags_setting),
        ):
            aList = getattr(self,ivar)
            aList2 = c.config.getData(setting) or []
            aList2 = [z.lower() for z in aList2]
            aList.extend(aList2)
            setattr(self,ivar,aList)
            if trace: g.trace(ivar,aList)
    #@+node:ekr.20111104032034.9868: *5* adjust_class_ref (xmlScanner)
    def adjust_class_ref(self,s):

        '''Ensure that @others appears at the start of a line.'''


        trace = False and not g.unitTesting
        if trace: g.trace('old',repr(s))

        i = s.find('@others')
        if i > -1:
            j = i
            i -= 1
            while i >= 0 and s[i] in '\t ':
                i -= 1
            if i < j:
                # 2011/11/04: Never put lws before @others.
                s = s[:i+1] + s[j:]
            if i > 0 and s[i] != '\n':
                s = s[:i+1] + '\n' + s [i+1:]

        if trace: g.trace('new',repr(s))
        return s
    #@+node:ekr.20111108111156.9922: *5* adjustTestLines (xmlScanner)
    def adjustTestLines(self,lines):

        '''A desparation measure to attempt reasonable comparisons.'''

        # self.ignoreBlankLines:
        lines = [z for z in lines if z.strip()]
        # if self.ignoreLeadingWs:
        lines = [z.lstrip() for z in lines]
        lines = [z.replace('@others','') for z in lines]
        # lines = [z.replace('>\n','>').replace('\n<','<') for z in lines]
        return lines
    #@+node:ekr.20111108111156.9935: *5* filterTokens (xmlScanner)
    def filterTokens (self,tokens):

        '''Filter tokens as needed for correct comparisons.

        For xml, this means:

        1. Removing newlines after opening elements.
        2. Removing newlines before closing elements.
        3. Converting sequences of whitespace to a single blank.
        '''

        trace = False
        if trace: g.trace(tokens)
        if 1: # Permissive code.
            return [(kind,val,line_number) for (kind,val,line_number) in tokens
                if kind not in ('nl','ws')]
        else: # Accurate code.
            # Pass 1. Insert newlines before and after elements.
            i,n,result = 0,len(tokens),[]
            while i < n:
                progress = i
                # Compute lookahead tokens.
                kind1,val1,n1 = tokens[i]
                kind2,val2,n2 = None,None,None
                kind3,val3,n3 = None,None,None
                kind4,val4,n4 = None,None,None
                if i + 1 < n: kind2,val2,n2 = tokens[i+1]
                if i + 2 < n: kind3,val3,n3 = tokens[i+2]
                if i + 3 < n: kind4,val4,n4 = tokens[i+3]
                # Always insert the present token.
                result.append((kind1,val1,n1),)
                i += 1
                if (
                    kind1 == 'other' and val1 == '>' and
                    kind2 != 'nl'
                ):
                    # insert nl after >
                    if trace: g.trace('** insert nl after >')
                    result.append(('nl','\n',n1),)
                elif (
                    kind1 != 'nl'    and
                    kind2 == 'other' and val2 == '<' and
                    kind3 == 'other' and val3 == '/' and
                    kind4 == 'id'
                ):
                    # Insert nl before </id
                    if trace: g.trace('** insert nl before </%s' % (val4))
                    result.append(('nl','\n',n1),)
                else:
                    pass
                assert progress == i-1
            # Pass 2: collapse newlines and whitespace separately.
            tokens = result
            i,n,result = 0,len(tokens),[]
            while i < n:
                progress = i
                kind1,val1,n1 = tokens[i]
                if kind1 == 'nl':
                    while i < n and tokens[i][0] == 'nl':
                        i += 1
                    result.append(('nl','\n',n1),)
                elif kind1 == 'ws':
                    while i < n and tokens[i][0] == 'ws':
                        i += 1
                    result.append(('ws',' ',n1),)
                else:
                    result.append((kind1,val1,n1),)
                    i += 1
                assert progress < i
            return result
    #@+node:ekr.20111103073536.16601: *5* isSpace (xmlScanner) (Use the base class now)
    # def isSpace(self,s,i):

        # '''Return true if s[i] is a tokenizer space.'''

        # # Unlike the base-class method, xml space tokens include newlines.
        # return i < len(s) and s[i].isspace()
    #@+node:ekr.20111103073536.16590: *5* skip...Token (xmlScanner overrides)
    def skipCommentToken(self,s,i):

        '''Return comment lines with all leading/trailing whitespace removed.'''
        j = self.skipComment(s,i)
        lines = g.splitLines(s[i:j])
        lines = [z.strip() for z in lines]
        return j,'\n'.join(lines)

    # skipIdToken: no change.
    # skipNewlineToken: no change.
    # skipOtherToken: no change.
    # skipStringToken: no change.
    # skipWsToken: no change.

    #@+node:ekr.20091230062012.6238: *5* skipId (override base class) & helper
    #@+at  For characters valid in names see:
    #    www.w3.org/TR/2008/REC-xml-20081126/#NT-Name
    #@@c

    def skipId (self,s,i):

        if 1:
            # Fix bug 501636: Leo's import code should support non-ascii xml tags.
            if i < len(s) and self.isWordChar1(s[i]):
                i += 1
            else:
                return i
            while i < len(s) and self.isWordChar2(s[i]):
                i += 1
            return i
        else:
            # Fix bug 497332: @data import_xml_tags does not allow dashes in tag.
            chars = '.-:' # Allow : anywhere.
            while i < len(s) and (self.isWordChar(s[i]) or s[i] in chars):
                i += 1
            return i
    #@+node:ekr.20120306130648.9852: *6* isWordChar (xmlScanner) To be replaced
    def isWordChar (self,ch):

        '''This allows only ascii tags.'''

        # Same as g.isWordChar. This is not correct.
        return ch and (ch.isalnum() or ch == '_')
    #@+node:ekr.20091230062012.6239: *6* isWordChar1 (xmlScanner)
    #@+at From www.w3.org/TR/2008/REC-xml-20081126/#NT-Name
    # 
    # NameStartChar    ::= ":" | [A-Z] | "_" | [a-z] |
    #     [#xC0-#xD6]     | [#xD8-#xF6]     | [#xF8-#x2FF]    |
    #     [#x370-#x37D]   | [#x37F-#x1FFF]  | [#x200C-#x200D] |
    #     [#x2070-#x218F] | [#x2C00-#x2FEF] | [#x3001-#xD7FF] |
    #     [#xF900-#xFDCF] | [#xFDF0-#xFFFD] | [#x10000-#xEFFFF]
    #@@c

    word_char_table1 = (
        (0xC0,  0xD6),    (0xD8,  0xF6),    (0xF8,  0x2FF),
        (0x370, 0x37D),   (0x37F, 0x1FFF),  (0x200C,0x200D),
        (0x2070,0x218F),  (0x2C00,0x2FEF),  (0x3001,0xD7FF),
        (0xF900,0xFDCF),  (0xFDF0,0xFFFD),  (0x10000,0xEFFFF),
    )

    def isWordChar1(self,ch):

        if not ch: return False

        if ch.isalnum() or ch in '_:': return True

        n = ord(ch)
        for n1,n2 in self.word_char_table1:
            if n1 <= n <= n2:
                return True

        return False
    #@+node:ekr.20120306130648.9851: *6* isWordChar2 (xmlScanner)
    #@+at From www.w3.org/TR/2008/REC-xml-20081126/#NT-Name
    # 
    # NameChar    ::= NameStartChar | "-" | "." | [0-9] | #xB7 |
    #     [#x0300-#x036F] | [#x203F-#x2040]
    #@@c

    word_char_table2 = (
        (0xB7,      0xB7),  # Middle dot.
        (0x0300,    0x036F),
        (0x203F,    0x2040),
    )

    def isWordChar2(self,ch):

        if not ch: return False

        if self.isWordChar1(ch) or ch in "-.0123456789":
            return True

        n = ord(ch)
        for n1,n2 in self.word_char_table2:
            if n1 <= n <= n2:
                return True

        return False
    #@+node:ekr.20071214072924.4: *5* startsHelper & helpers (xmlScanner)
    def startsHelper(self,s,i,kind,tags,tag=None):
        '''return True if s[i:] starts a class or function.
        Sets sigStart, sigEnd, sigId and codeEnd ivars.'''

        trace = (False and kind == 'class') # and not g.unitTesting
        verbose = True
        self.codeEnd = self.sigEnd = self.sigId = None

        # Underindented lines can happen in any language, not just Python.
        # The skipBlock method of the base class checks for such lines.
        self.startSigIndent = self.getLeadingIndent(s,i)

        # Get the tag that starts the class or function.
        if not g.match(s,i,'<'): return False
        self.sigStart = i
        i += 1
        sigIdStart = j = g.skip_ws_and_nl(s,i)
        i = self.skipId(s,j)

        # Fix bug 501636: Leo's import code should support non-ascii xml tags.
        # The call to g.toUnicode only needed on Python 2.x.
        self.sigId = theId = g.toUnicode(s[j:i].lower())
            # Set sigId ivar 'early' for error messages.
            # Bug fix: html case does not matter.
        if not theId: return False

        if theId not in tags:
            if trace and verbose:
                g.trace('**** %s theId: %s not in tags: %s' % (
                    kind,theId,tags))
            return False

        if trace and verbose: g.trace(theId)
        classId = '' 
        sigId = theId

        # Complete the opening tag.
        i, ok, complete = self.skipToEndOfTag(s,i,start=sigIdStart)
        if not ok:
            if trace and verbose: g.trace('no tail',g.get_line(s,i))
            return False
        sigEnd = i

        # Bug fix: 2011/11/05.
        # For xml/html, make sure the signature includes any trailing whitespace.
        if not g.match(s,sigEnd,'\n') and not g.match(s,sigEnd-1,'\n'):
            # sigEnd = g.skip_line(s,sigEnd)
            sigEnd = g.skip_ws(s,sigEnd)

        if not complete:
            i,ok = self.skipToMatchingTag(s,i,theId,tags,start=sigIdStart)
            if not ok:
                if trace and verbose: g.trace('no matching tag:',theId)
                return False

        # Success: set the ivars.
        # Not used in xml/html.
        # self.sigStart = self.adjustDefStart(s,self.sigStart)
        self.codeEnd = i
        self.sigEnd = sigEnd
        self.sigId = sigId
        self.classId = classId

        # Scan to the start of the next tag.
        done = False
        while not done and i < len(s):
            progress = i
            if self.startsComment(s,i):
                i = self.skipComment(s,i)
            elif self.startsString(s,i):
                i = self.skipString(s,i)
            elif s[i] == '<':
                start = i
                i += 1
                if i < len(s) and s[i] == '/':
                    i += 1
                j = g.skip_ws_and_nl(s,i)
                if self.startsId(s,j):
                    i = self.skipId(s,j)
                    word = s[j:i].lower()
                    if word in tags:
                        self.codeEnd = start
                        done = True
                        break
                else:
                    i = j
            else:
                i += 1

            assert done or progress < i,'i: %d, ch: %s' % (i,repr(s[i]))

        if trace: g.trace(repr(s[self.sigStart:self.codeEnd]))
        return True
    #@+node:ekr.20071214072924.3: *6* skipToEndOfTag (xmlScanner)
    def skipToEndOfTag(self,s,i,start):

        '''Skip to the end of an open tag.

        return i,ok,complete

        where complete is True if the tag of the form <name/>
        '''

        trace = False
        complete,ok = False,False
        while i < len(s): 
            progress = i
            if i == '"':
                i = self.skipString(s,i)
            elif g.match(s,i,'<!--'):
                i = self.skipComment(s,i)
            elif g.match(s,i,'<'):
                complete,ok = False,False ; break
            elif g.match(s,i,'/>'):
                i = g.skip_ws(s,i+2)
                complete,ok = True,True ; break
            elif g.match(s,i,'>'):
                i += 1
                complete,ok = False,True ; break
            else:
                i += 1
            assert progress < i

        if trace: g.trace('ok',ok,repr(s[start:i]))
        return i,ok,complete
    #@+node:ekr.20071214075117: *6* skipToMatchingTag (xmlScanner)
    def skipToMatchingTag (self,s,i,tag,tags,start):

        '''Skip the entire class definition. Return i,ok.
        '''

        trace = False
        found,level,target_tag = False,1,tag.lower()
        while i < len(s): 
            progress = i
            if s[i] == '"':
                i = self.skipString(s,i)
            elif g.match(s,i,'<!--'):
                i = self.skipComment(s,i)
            elif g.match(s,i,'</'):
                j = i+2
                i = self.skipId(s,j)
                tag2 = s[j:i].lower()
                i,ok,complete = self.skipToEndOfTag(s,i,start=j)
                    # Sets complete if /> terminates the tag.
                if ok and tag2 == target_tag:
                    level -= 1
                    if level == 0:
                        found = True ; break
            elif g.match(s,i,'<'):
                # An open tag.
                j = g.skip_ws_and_nl(s,i+1)
                i = self.skipId(s,j)
                word = s[j:i].lower()
                i,ok,complete = self.skipToEndOfTag(s,i,start=j)
                # **Important**: only bump level for nested *target* tags.
                # This avoids problems when interior tags are not properly nested.
                if ok and word == target_tag and not complete:
                    level += 1
            elif g.match(s,i,'/>'):
                # This is a syntax error.
                # This should have been eaten by skipToEndOfTag.
                i += 2
                g.trace('syntax error: unmatched "/>"')
            else:
                i += 1

            assert progress < i

        if trace: g.trace('%sfound:%s\n%s\n\n*****end %s\n' % (
            g.choose(found,'','not '),target_tag,s[start:i],target_tag))

        return i,found
    #@+node:ekr.20111103073536.16595: *5* startsId (xmlScanner)
    def startsId(self,s,i):

        # Fix bug 501636: Leo's import code should support non-ascii xml tags.
        return i < len(s) and self.isWordChar1(s[i])
    #@+node:ekr.20130918062408.17090: *5* startsString (xmlScanner)
    def startsString(self,s,i):
            
        '''Single quotes do *not* start strings in xml or html.'''
        
        # Fix bug 1208659: leo parsed the wrong line number of html file.
        # Note: the compare failure was caused by using baseScannerClass.startsString.
        # The line number problem is a separate issue.
        return g.match(s,i,'"')
    #@-others
#@-<< class xmlScanner (baseScannerClass) >>

#@+<< class htmlScanner (xmlScanner) >>
#@+node:ekr.20111104032034.9867: *4* << class htmlScanner (xmlScanner) >>
class htmlScanner (xmlScanner):

    def __init__ (self,importCommands,atAuto):

        # Init the base class.
        xmlScanner.__init__(self,importCommands,atAuto,tags_setting='import_html_tags')

    #@+others
    #@-others
#@-<< class htmlScanner (xmlScanner) >>
#@+node:ekr.20101103093942.5938: ** Commands (leoImport)
#@+node:ekr.20120429125741.10057: *3* @g.command(parse-body)
@g.command('parse-body')
def parse_body_command(event):

    c = event.get('c')
    p = c and c.p
    if not c or not p: return
    ic = c.importCommands
    ic.tab_width = ic.getTabWidth()
    language = g.scanForAtLanguage(c,p)
    ext = g.app.language_extension_dict.get(language)
    if ext:
        if not ext.startswith('.'): ext = '.' + ext
        func = ic.importDispatchDict.get(ext)
        if func:
            bunch = c.undoer.beforeChangeTree(p)
            s = p.b
            p.b = ''
            func(s,p,atAuto=False)
            bunch = c.undoer.afterChangeTree(p,'parse-body',bunch)
            c.validateOutline()
            p.expand()
            c.redraw()
            return
    g.es_print('unknown language')
#@+node:ekr.20101103093942.5941: *3* @g.command(head-to-prev-node)
@g.command('head-to-prev-node')
def headToPrevNode(event):

    '''Move the code following a def to end of previous node.'''

    c = event.get('c')
    if not c: return
    p = c.p
    scanner = pythonScanner(c.importCommands,atAuto=False)
    kind,i,junk = scanner.findClass(p)
    p2 = p.back()

    if p2 and kind in ('class','def') and i > 0:
        u = c.undoer ; undoType = 'move-head-to-prev'
        head = p.b[:i].rstrip()
        u.beforeChangeGroup(p,undoType)
        b  = u.beforeChangeNodeContents(p)
        p.b = p.b[i:]
        u.afterChangeNodeContents(p,undoType,b)
        if head:
            b2 = u.beforeChangeNodeContents(p2)
            p2.b = p2.b.rstrip() + '\n\n' + head + '\n'
            u.afterChangeNodeContents(p2,undoType,b2)
        u.afterChangeGroup(p,undoType)
        c.selectPosition(p2)
#@+node:ekr.20101103093942.5943: *3* @g.command(tail-to-next-node)
@g.command('tail-to-next-node')
def tailToNextNode(event=None):

    '''Move the code following a def to end of previous node.'''

    c = event.get('c')
    if not c: return
    p = c.p
    scanner = pythonScanner(c.importCommands,atAuto=False)
    kind,junk,j = scanner.findClass(p)
    p2 = p.next()

    if p2 and kind in ('class','def') and j < len(p.b):
        u = c.undoer ; undoType = 'move-tail-to-next'
        tail = p.b[j:].rstrip()
        u.beforeChangeGroup(p,undoType)
        b  = u.beforeChangeNodeContents(p)
        p.b = p.b[:j]
        u.afterChangeNodeContents(p,undoType,b)
        if tail:
            b2 = u.beforeChangeNodeContents(p2)
            p2.b = tail + '\n\n' + p2.b
            u.afterChangeNodeContents(p2,undoType,b2)
        u.afterChangeGroup(p,undoType)
        c.selectPosition(p2)
#@-others
#@-leo
