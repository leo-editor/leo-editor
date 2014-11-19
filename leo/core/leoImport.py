# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20031218072017.3206: * @file leoImport.py
#@@first
    # Required so non-ascii characters will be valid in unit tests.
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@@encoding utf-8
#@+<< imports >>
#@+node:ekr.20091224155043.6539: ** << imports >> (leoImport)
# Required so the unit test that simulates an @auto leoImport.py will work!
import leo.core.leoGlobals as g
try:
    import docutils
    import docutils.core
    # print('leoImport.py:',docutils)
except ImportError:
    docutils = None
    # print('leoImport.py: can not import docutils')
import glob
import importlib
import os
if g.isPython3:
    import io
    StringIO = io.StringIO
else:
    import StringIO
    StringIO = StringIO.StringIO
import time
#@-<< imports >>
#@+others
#@+node:ekr.20071127175948: ** class LeoImportCommands
class LeoImportCommands:
    '''
    A class implementing all of Leo's import/export code. This class
    uses **importers** in the leo/plugins/importers folder.
    
    For more information, see leo/plugins/importers/howto.txt.
    '''
    #@+others
    #@+node:ekr.20031218072017.3207: *3* ic.__init__ & helpers
    def __init__ (self,c):
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
        self.tab_width = c.tab_width # The tab width in effect in the c.currentPosition.
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
        self.classDispatchDict = {}
        self.atAutoDict = {}
        def report(message,kind,folder,name):
            if trace: g.trace('%7s: %5s %9s %s' % (
                message,kind,folder,name))
        folder = 'importers'
        plugins1 = g.os_path_finalize_join(g.app.homeDir,'.leo','plugins')
        plugins2 = g.os_path_finalize_join(g.app.loadDir,'..','plugins')
        seen = set()
        for kind,plugins in (('home',plugins1),('leo',plugins2)):
            path = g.os_path_finalize_join(plugins,folder)
            if 1: # Old code...
                pattern = g.os_path_finalize_join(g.app.loadDir,'..','plugins','importers','*.py')
                for fn in glob.glob(pattern):
                    sfn = g.shortFileName(fn)
                    if sfn != '__init__.py':
                        try:
                            module_name = sfn[:-3]
                            # Important: use importlib to give imported modules their fully qualified names.
                            m = importlib.import_module('leo.plugins.importers.%s' % module_name)
                            self.parse_importer_dict(sfn,m)
                        except Exception:
                            g.es_exception()
                            g.warning('can not import leo.plugins.importers.%s' % module_name)
            else: # New code: has problems.
                pattern = g.os_path_finalize_join(path,'*.py')
                for fn in glob.glob(pattern):
                    sfn = g.shortFileName(fn)
                    if g.os_path_exists(fn) and sfn != '__init__.py':
                        moduleName = sfn[:-3]
                        if moduleName:
                            data = (folder,sfn)
                            if data in seen:
                                report('seen',kind,folder,sfn)
                            else:
                                m = g.importFromPath(moduleName,path) # Uses imp.
                                if m:
                                    seen.add(data)
                                    self.parse_importer_dict(sfn,m)
                                    report('loaded',kind,folder,m.__name__)
                                else:
                                    report('error',kind,folder,sfn)
                    # else: report('skipped',kind,folder,sfn)
    #@+node:ekr.20140723140445.18076: *5* ic.parse_importer_dict
    def parse_importer_dict(self,sfn,m):
        '''
        Set entries in ic.classDispatchDict, ic.atAutoDict and
        g.app.atAutoNames using entries in m.importer_dict.
        '''
        trace = False and not g.unitTesting
        ic = self
        importer_d = getattr(m,'importer_dict',None)
        if importer_d:
            at_auto       = importer_d.get('@auto',[])
            scanner_class = importer_d.get('class',None)
            extensions    = importer_d.get('extensions',[])
            if at_auto:
                # Make entries for each @auto type.
                d = ic.atAutoDict
                for s in at_auto:
                    aClass = d.get(s)
                    if aClass and aClass != scanner_class:
                        g.trace('%s: duplicate %5s class: %s in %s' % (
                            sfn,s,aClass.__name__,m.__file__))
                    else:
                        d[s] = scanner_class
                        ic.atAutoDict[s] = scanner_class
                        g.app.atAutoNames.add(s)
                        if trace: g.trace(
                            'found scanner for %20s in %s: %s' % (
                                s,sfn,scanner_class))
            if extensions:
                # Make entries for each extension.
                d = ic.classDispatchDict
                for ext in extensions:
                    aClass = d.get(ext)
                    if aClass and aClass != scanner_class:
                        g.trace('%s: duplicate %s class: %s in %s' % (
                            sfn,ext,aClass.__name__,m.__file__))
                    else:
                        d[ext] = scanner_class
        elif sfn not in ('basescanner.py',):
            g.warning('leo/plugins/importers/%s has no importer_dict' % sfn)
    #@+node:ekr.20031218072017.3289: *3* ic.Export
    #@+node:ekr.20031218072017.3290: *4* ic.convertCodePartToWeb & helpers
    def convertCodePartToWeb (self,s,i,p,result):
        '''
        # Headlines not containing a section reference are ignored in noweb 
        and generate index index in cweb.
        '''
        # g.trace(g.get_line(s,i))
        ic = self
        nl = ic.output_newline
        head_ref = ic.getHeadRef(p)
        file_name = ic.getFileName(p)
        if g.match_word(s,i,"@root"):
            i = g.skip_line(s,i)
            ic.appendRefToFileName(file_name,result)
        elif g.match_word(s,i,"@c") or g.match_word(s,i,"@code"):
            i = g.skip_line(s,i)
            ic.appendHeadRef(p,file_name,head_ref,result)
        elif g.match_word(p.h,0,"@file"):
            # Only do this if nothing else matches.
            ic.appendRefToFileName(file_name,result)
            i = g.skip_line(s,i) # 4/28/02
        else:
            ic.appendHeadRef(p,file_name,head_ref,result)
        i,result = ic.copyPart(s,i,result)
        return i, result.strip() + nl

    #@+at %defs a b c
    #@+node:ekr.20140630085837.16720: *5* ic.appendHeadRef
    def appendHeadRef(self,p,file_name,head_ref,result):
        
        ic = self
        nl = ic.output_newline
        if ic.webType == "cweb":
            if head_ref:
                escaped_head_ref = head_ref.replace("@","@@")
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
    def appendRefToFileName(self,file_name,result):
        
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
    def getHeadRef(self,p):
        '''
        Look for either noweb or cweb brackets.
        Return everything between those brackets.
        '''
        h = p.h.strip()
        if g.match(h,0,"<<"):
            i = h.find(">>",2)
        elif g.match(h,0,"<@"):
            i = h.find("@>",2)
        else:
            return h
        return h[2:i].strip()
    #@+node:ekr.20031218072017.3292: *5* ic.getFileName
    def getFileName(self,p):
        '''Return the file name from an @file or @root node.'''
        h = p.h.strip()
        if g.match(h,0,"@file") or g.match(h,0,"@root"):
            line = h[5:].strip()
            # set j & k so line[j:k] is the file name.
            if g.match(line,0,"<"):
                j,k = 1,line.find(">",1)
            elif g.match(line,0,'"'):
                j,k = 1,line.find('"',1)
            else:
                j,k = 0,line.find(" ",0)
            if k == -1:
                k = len(line)
            file_name = line[j:k].strip()
        else:
            file_name = ''
        return file_name
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
            result += nl+"@ " if self.webType=="cweb" else nl+"@"+nl
        return i, result
    #@+node:ekr.20031218072017.3297: *4* ic.convertVnodeToWeb
    def convertVnodeToWeb (self,v):
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
        docstart = nl+"@ " if self.webType=="cweb" else nl+"@"+nl
        s = v.b
        lb = "@<" if self.webType=="cweb" else "<<"
        i,result,docSeen = 0,"",False
        while i < len(s):
            progress = i
            # g.trace(g.get_line(s,i))
            i = g.skip_ws_and_nl(s,i)
            if self.isDocStart(s,i) or g.match_word(s,i,"@doc"):
                i,result = self.convertDocPartToWeb(s,i,result)
                docSeen = True
            elif (g.match_word(s,i,"@code") or g.match_word(s,i,"@root") or
                g.match_word(s,i,"@c") or g.match(s,i,lb)):
                if not docSeen:
                    docSeen = True
                    result += docstart
                i,result = self.convertCodePartToWeb(s,i,v,result)
            elif self.treeType == "@file" or startInCode:
                if not docSeen:
                    docSeen = True
                    result += docstart
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
        lb = "@<" if self.webType=="cweb" else "<<"
        rb = "@>" if self.webType=="cweb" else ">>"
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
        try:
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
    #@+node:ekr.20031218072017.3209: *3* ic.Import
    #@+node:ekr.20031218072017.3210: *4* ic.createOutline & helpers
    def createOutline (self,fileName,parent,
        atAuto=False,atShadow=False,s=None,ext=None
    ):
        '''Create an outline by importing a file or string.'''
        trace = False and not g.unitTesting
        c = self.c
        fileName = self.get_import_filename(fileName,parent)
        if g.is_binary_external_file(fileName):
            # Fix bug 1185409 importing binary files puts binary content in body editor.
            # Create an @url node.
            p = parent.insertAsLastChild()
            p.h = '@url file://%s' % fileName
            if trace: g.trace('binary file:',fileName)
            return
        # Init ivars.
        self.setEncoding(p=parent,atAuto=atAuto)
        atAuto,atAutoKind,ext,s = self.init_import(atAuto,atShadow,ext,fileName,s)
        if s is None:
            if trace: g.trace('read failed',fileName)
            return
        if trace and not s:
            g.trace('empty file: but calling importer',fileName)
        # Create the top-level headline.
        p = self.create_top_node(atAuto,atAutoKind,fileName,parent)
        # Get the scanning function.
        func = self.dispatch(ext,p)
        if trace: g.trace(ext,p.h,func)
        # Call the scanning function.
        if g.unitTesting:
            assert func or ext in ('.w','.xxx'),(ext,p.h)
        if func and not c.config.getBool('suppress_import_parsing',default=False):
            s = s.replace('\r','')
            func(atAuto=atAuto,parent=p,s=s)
        else:
            # Just copy the file to the parent node.
            s = s.replace('\r','')
            self.scanUnknownFileType(s,p,ext,atAuto=atAuto)
        if atAuto:
            # Fix bug 488894: unsettling dialog when saving Leo file
            # Fix bug 889175: Remember the full fileName.
            c.atFileCommands.rememberReadPath(fileName,p)
        p.contract()
        w = c.frame.body.wrapper
        w.setInsertPoint(0)
        w.seeInsertPoint()
        return p
    #@+node:ekr.20140724175458.18053: *5* ic.create_top_node
    def create_top_node(self,atAuto,atAutoKind,fileName,parent):
        '''Create the top node.'''
        u = self.c.undoer
        if atAuto:
            if atAutoKind:
                # We have found a match between ext and an @auto importer.
                undoData = u.beforeInsertNode(parent)
                p = parent.insertAsLastChild()
                p.initHeadString(atAutoKind + ' ' + fileName)
                u.afterInsertNode(p,'Import',undoData)
            else:
                p = parent.copy()
                p.setBodyString('')
        else:
            undoData = u.beforeInsertNode(parent)
            p = parent.insertAsLastChild()
            if self.treeType == "@file":
                p.initHeadString("@file " + fileName)
            elif self.treeType is None:
                # By convention, we use the short file name.
                p.initHeadString(g.shortFileName(fileName))
            else:
                p.initHeadString(fileName)
            u.afterInsertNode(p,'Import',undoData)
        return p
    #@+node:ekr.20140724064952.18038: *5* ic.dispatch & helpers
    def dispatch(self,ext,p):
        '''Return the correct scanner function for p, an @auto node.'''
        # Match the @auto type first, then the file extension.
        return self.scanner_for_at_auto(p) or self.scanner_for_ext(ext)
    #@+node:ekr.20140727180847.17985: *6* ic.scanner_for_at_auto
    def scanner_for_at_auto(self,p):
        '''A factory returning a scanner function for p, an @auto node.'''
        d = self.atAutoDict
        trace = False and not g.unitTesting
        for key in d.keys():
            # pylint: disable=cell-var-from-loop
            aClass = d.get(key)
            # if trace:g.trace(bool(aClass),p.h.startswith(key),g.match_word(p.h,0,key),p.h,key)
            if aClass and g.match_word(p.h,0,key):
                if trace: g.trace('found',aClass.__name__)
                def scanner_for_at_auto_cb(atAuto,parent,s,prepass=False):
                    try:
                        scanner = aClass(importCommands=self,atAuto=atAuto)
                        return scanner.run(s,parent,prepass=prepass)
                    except Exception:
                        g.es_exception()
                        return None
                if trace: g.trace('found',p.h)
                return scanner_for_at_auto_cb
        if trace: g.trace('not found',p.h,sorted(d.keys()))
        return None
    #@+node:ekr.20140130172810.15471: *6* ic.scanner_for_ext
    def scanner_for_ext(self,ext):
        '''A factory returning a scanner function for the given file extension.'''
        aClass = self.classDispatchDict.get(ext)
        if aClass:
            def scanner_for_ext_cb(atAuto,parent,s,prepass=False):
                try:
                    scanner = aClass(importCommands=self,atAuto=atAuto)
                    return scanner.run(s,parent,prepass=prepass)
                except Exception:
                    g.es_exception()
                    return None
            return scanner_for_ext_cb
        else:
            return None
    #@+node:ekr.20140724073946.18050: *5* ic.get_import_filename
    def get_import_filename(self,fileName,parent):
        '''Return the absolute path of the file and set .default_directory.'''
        c = self.c
        self.default_directory = g.setDefaultDirectory(c,parent,importing=False)
        fileName = c.os_path_finalize_join(self.default_directory,fileName)
        fileName = fileName.replace('\\','/') # 2011/11/25
        return fileName
    #@+node:ekr.20140724175458.18052: *5* ic.init_import
    def init_import(self,atAuto,atShadow,ext,fileName,s):
        '''Init ivars & vars for imports.'''
        trace = False and not g.unitTesting
        junk,self.fileName = g.os_path_split(fileName)
        self.methodName,self.fileType = g.os_path_splitext(self.fileName)
        if not ext: ext = self.fileType
        ext = ext.lower()
        kind = None
        if not s:
            if atShadow: kind = '@shadow '
            elif atAuto: kind = '@auto '
            else: kind = ''
            s,e = g.readFileIntoString(fileName,encoding=self.encoding,kind=kind)
                # Kind is used only for messages.
            if s is None:
                return None,None,None,None
            if e: self.encoding = e
        if self.treeType == '@root': # 2010/09/29.
            self.rootLine = "@root-code "+self.fileName+'\n'
        else:
            self.rootLine = ''
        if trace: g.trace('1',atAuto,self.treeType,fileName)
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
        if trace: g.trace('2',atAuto,atAutoKind,ext)
        return atAuto,atAutoKind,ext,s
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
            message = 'finished' if found else 'no @auto nodes in the selected tree'
            g.blue(message)
        c.redraw()

    #@+node:ekr.20031218072017.1810: *4* ic.importDerivedFiles
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
    #@+node:ekr.20031218072017.3212: *4* ic.importFilesCommand & helper
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
                current = p # 2014/08/16
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
    #@+node:ekr.20031218072017.3214: *4* ic.importFlattenedOutline & allies
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
        plusFlag = True if g.match(s,i,"+") else False
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
    #@+node:ekr.20031218072017.3224: *4* ic.importWebCommand & allies
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
                    return name if name else "outer function"
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
        lb = "@<" if theType=="cweb" else "<<"
        rb = "@>" if theType=="cweb" else ">>"

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
    #@+node:ekr.20070713075352: *3* ic.scanUnknownFileType & helper
    def scanUnknownFileType (self,s,p,ext,atAuto=False):
        '''Scan the text of an unknown file type.'''
        c = self.c
        changed = c.isChanged()
        body = '' if atAuto else '@ignore\n'
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
        return True
    #@+node:ekr.20080811174246.1: *4* ic.languageForExtension
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
    #@+node:ekr.20140531104908.18833: *3* ic.parse_body & helper
    def parse_body(self,p):
        '''The parse-body command.'''
        if not p: return
        c,ic = self.c,self
        language = g.scanForAtLanguage(c,p)
        ext = '.' + g.app.language_extension_dict.get(language)
        parser = self.body_parser_for_ext(ext)
        # g.trace(language,ext,parser)
        if parser:
            bunch = c.undoer.beforeChangeTree(p)
            s = p.b
            p.b = ''
            parser(p,s)
            c.undoer.afterChangeTree(p,'parse-body',bunch)
            p.expand()
            c.redraw()
    #@+node:ekr.20140205074001.16365: *4* ic.body_parser_for_ext
    def body_parser_for_ext(self,ext):
        '''A factory returning a body parser function for the given file extension.'''
        aClass = ext and self.classDispatchDict.get(ext)
        def body_parser_for_class(parent,s):
            obj = aClass(importCommands=self,atAuto=True)
            return obj.run(s,parent,parse_body=True)
        return body_parser_for_class if aClass else None
    #@+node:ekr.20070713075450: *3* ic.Unit tests
    # atAuto must be False for unit tests: otherwise the test gets wiped out.

    def cUnitTest(self,p,fileName=None,s=None,showTree=False):
        return self.scannerUnitTest(p,atAuto=False,fileName=fileName,s=s,showTree=showTree,ext='.c')

    def cSharpUnitTest(self,p,fileName=None,s=None,showTree=False):
        return self.scannerUnitTest(p,atAuto=False,fileName=fileName,s=s,showTree=showTree,ext='.c#')

    def elispUnitTest(self,p,fileName=None,s=None,showTree=False):
        return self.scannerUnitTest(p,atAuto=False,fileName=fileName,s=s,showTree=showTree,ext='.el')

    def htmlUnitTest(self,p,fileName=None,s=None,showTree=False):
        return self.scannerUnitTest(p,atAuto=False,fileName=fileName,s=s,showTree=showTree,ext='.htm')

    def iniUnitTest(self,p,fileName=None,s=None,showTree=False):
        return self.scannerUnitTest(p,atAuto=False,fileName=fileName,s=s,showTree=showTree,ext='.ini')

    def javaUnitTest(self,p,fileName=None,s=None,showTree=False):
        return self.scannerUnitTest(p,atAuto=False,fileName=fileName,s=s,showTree=showTree,ext='.java')

    def javaScriptUnitTest(self,p,fileName=None,s=None,showTree=False):
        return self.scannerUnitTest (p,atAuto=False,fileName=fileName,s=s,showTree=showTree,ext='.js')
        
    def markdownUnitTest(self,p,fileName=None,s=None,showTree=False):
        return self.scannerUnitTest(p,atAuto=False,fileName=fileName,s=s,showTree=showTree,ext='.md')

    def pascalUnitTest(self,p,fileName=None,s=None,showTree=False):
        return self.scannerUnitTest (p,atAuto=False,fileName=fileName,s=s,showTree=showTree,ext='.pas')

    def phpUnitTest(self,p,fileName=None,s=None,showTree=False):
        return self.scannerUnitTest (p,atAuto=False,fileName=fileName,s=s,showTree=showTree,ext='.php')

    def pythonUnitTest(self,p,atAuto=False,fileName=None,s=None,showTree=False):
        return self.scannerUnitTest(p,atAuto=atAuto,fileName=fileName,s=s,showTree=showTree,ext='.py')

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
    #@+node:ekr.20070713082220: *4* ic.scannerUnitTest
    def scannerUnitTest (self,p,atAuto=False,ext=None,fileName=None,s=None,showTree=False):
        '''
        Run a unit test of an import scanner,
        i.e., create a tree from string s at location p.
        '''
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
        title = h[5:] if h.startswith('@test') else h
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
                # 'p.h:                  %s' % (p.h),
                'ext:                  %s' % (ext),
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
    #@+node:ekr.20031218072017.3305: *3* ic.Utilities
    #@+node:ekr.20090122201952.4: *4* ic.appendStringToBody & setBodyString (leoImport)
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
            w = c.frame.body.wrapper
            i = w.getInsertPoint()
            w.setSelectionRange(i,i)

        # Keep the body text up-to-date.
        if v.b != s:
            v.setBodyString(s)
            v.setSelection(0,0)
            p.setDirty()
            if not c.isChanged():
                c.setChanged(True)
    #@+node:ekr.20031218072017.3306: *4* ic.createHeadline
    def createHeadline (self,parent,body,headline):
        '''Create a new VNode as the last child of parent position.'''
        p = parent.insertAsLastChild()
        body = g.u(body)
        headline = g.u(headline)
        p.initHeadString(headline)
        if len(body) > 0:
            self.setBodyString(p,body)
        # g.trace(p.v.gnx,p.h)
        return p
    #@+node:ekr.20031218072017.3307: *4* ic.error
    def error (self,s):
        g.es('',s)
    #@+node:ekr.20041126042730: *4* ic.getTabWidth
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
    #@+node:ekr.20031218072017.3309: *4* ic.isDocStart & isModuleStart
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
    #@+node:ekr.20031218072017.3312: *4* ic.massageWebBody
    def massageWebBody (self,s):

        theType = self.webType
        lb = "@<" if theType=="cweb" else "<<"
        rb = "@>" if theType=="cweb" else ">>"
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
                        doc = "@ " if self.webType=="cweb" else "@\n"
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
    #@+node:ekr.20031218072017.1463: *4* ic.setEncoding (leoImport)
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
    #@-others
#@+node:ekr.20130823083943.12596: ** class RecursiveImportController
class RecursiveImportController:
    '''Recursively import all python files in a directory and clean the result.'''
    #@+others
    #@+node:ekr.20130823083943.12615: *3* ctor
    def __init__ (self,c,one_file=False,theTypes=None,safe_at_file=True,use_at_edit=False):
        '''Ctor for RecursiveImportController class.'''
        self.c = c
        self.one_file = one_file
        self.recursive = not one_file
        self.safe_at_file = safe_at_file
        self.theTypes = theTypes
        self.use_at_edit = use_at_edit
    #@+node:ekr.20130823083943.12597: *3* Pass 1: import_dir
    def import_dir(self,root,dir_):
        '''Import selected files from dir_, a directory.'''
        trace = False and not g.unitTesting
        c = self.c
        g.es("dir: " + dir_,color="blue")
        files = os.listdir(dir_)
        if trace: g.trace(sorted(files))
        dirs,files2 = [],[]
        for f in files:
            path = g.os_path_join(dir_,f,expanduser=False)
            if trace: g.trace('is_file',g.os_path_isfile(path),path)
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
        '''Clean all imported nodes.'''
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
        '''
        Traverse p's tree, replacing all nodes that start with prefix
        by the smallest equivalent @path or @file node.
        '''
        root = p.copy()
        self.fix_back_slashes(root.copy())
        prefix = prefix.replace('\\','/')
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
#@+node:ekr.20101103093942.5938: ** Commands (leoImport)
#@+node:ekr.20120429125741.10057: *3* @g.command(parse-body)
@g.command('parse-body')
def parse_body_command(event):
    '''The parse-body command.'''
    c = event.get('c')
    if c and c.p:
        c.importCommands.parse_body(c.p)
#@+node:ekr.20101103093942.5941: *3* @g.command(head-to-prev-node)
@g.command('head-to-prev-node')
def headToPrevNode(event):

    '''Move the code following a def to end of previous node.'''

    c = event.get('c')
    if not c: return
    p = c.p
    try:
        import leo.plugins.importers.python as python
    except ImportError:
        return
    scanner = python.PythonScanner(c.importCommands,atAuto=False)
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
    try:
        import leo.plugins.importers.python as python
    except ImportError:
        return
    scanner = python.PythonScanner(c.importCommands,atAuto=False)
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
