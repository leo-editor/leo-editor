#@+leo-ver=5-thin
#@+node:ekr.20031218072017.3630: * @file leoCompare.py
#@@language python
#@@tabwidth -4
#@@pagewidth 70

"""Leo's base compare class."""

import leo.core.leoGlobals as g
import filecmp
import os
# import string

#@+others
#@+node:ekr.20031218072017.3631: ** choose
def choose(cond, a, b): # warning: evaluates all arguments

    if cond: return a
    else: return b
#@+node:ekr.20031218072017.3632: ** go
def go ():

    compare = leoCompare(
        commands = None,

        appendOutput = True,

        ignoreBlankLines = True,
        ignoreFirstLine1 = False,
        ignoreFirstLine2 = False,
        ignoreInteriorWhitespace = False,
        ignoreLeadingWhitespace = True,
        ignoreSentinelLines = False,

        limitCount = 9, # Zero means don't stop.
        limitToExtension = ".py",  # For directory compares.
        makeWhitespaceVisible = True,

        printBothMatches = False,
        printMatches = False,
        printMismatches = True,
        printTrailingMismatches = False,

        outputFileName = None)

    if 1: # Compare all files in Tangle test directories

        path1 = "c:\\prog\\test\\tangleTest\\"
        path2 = "c:\\prog\\test\\tangleTestCB\\"
        compare.compare_directories(path1,path2)

    else: # Compare two files.

        name1 = "c:\\prog\\test\\compare1.txt"
        name2 = "c:\\prog\\test\\compare2.txt"
        compare.compare_files(name1,name2)
#@+node:ekr.20031218072017.3633: ** class leoCompare
class baseLeoCompare:
    """The base class for Leo's compare code."""
    #@+others
    #@+node:ekr.20031218072017.3634: *3* compare.__init__
    # All these ivars are known to the leoComparePanel class.

    def __init__ (self,

        # Keyword arguments are much convenient and more clear for scripts.
        commands = None,

        appendOutput = False,

        ignoreBlankLines = True,
        ignoreFirstLine1 = False,
        ignoreFirstLine2 = False,
        ignoreInteriorWhitespace = False,
        ignoreLeadingWhitespace = True,
        ignoreSentinelLines = False,

        limitCount = 0, # Zero means don't stop.
        limitToExtension = ".py",  # For directory compares.
        makeWhitespaceVisible = True,

        printBothMatches = False,
        printMatches = False,
        printMismatches = True,
        printTrailingMismatches = False,

        outputFileName = None ):

        # It is more convenient for the leoComparePanel to set these directly.
        self.c = commands

        self.appendOutput = appendOutput

        self.ignoreBlankLines = ignoreBlankLines
        self.ignoreFirstLine1 = ignoreFirstLine1
        self.ignoreFirstLine2 = ignoreFirstLine2
        self.ignoreInteriorWhitespace = ignoreInteriorWhitespace
        self.ignoreLeadingWhitespace = ignoreLeadingWhitespace
        self.ignoreSentinelLines = ignoreSentinelLines

        self.limitCount = limitCount
        self.limitToExtension = limitToExtension

        self.makeWhitespaceVisible = makeWhitespaceVisible

        self.printBothMatches = printBothMatches
        self.printMatches = printMatches
        self.printMismatches = printMismatches
        self.printTrailingMismatches = printTrailingMismatches

        # For communication between methods...
        self.outputFileName = outputFileName
        self.fileName1 = None 
        self.fileName2 = None
        # Open files...
        self.outputFile = None
    #@+node:ekr.20031218072017.3635: *3* compare_directories (entry)
    # We ignore the filename portion of path1 and path2 if it exists.

    def compare_directories (self,path1,path2):

        # Ignore everything except the directory name.
        dir1 = g.os_path_dirname(path1)
        dir2 = g.os_path_dirname(path2)
        dir1 = g.os_path_normpath(dir1)
        dir2 = g.os_path_normpath(dir2)

        if dir1 == dir2:
            return self.show("Please pick distinct directories.")
        try:
            list1 = os.listdir(dir1)
        except:
            return self.show("invalid directory:" + dir1)
        try:
            list2 = os.listdir(dir2)
        except:
            return self.show("invalid directory:" + dir2)

        if self.outputFileName:
            self.openOutputFile()
        ok = self.outputFileName == None or self.outputFile
        if not ok: return None

        # Create files and files2, the lists of files to be compared.
        files1 = []
        files2 = []
        for f in list1:
            junk, ext = g.os_path_splitext(f)
            if self.limitToExtension:
                if ext == self.limitToExtension:
                    files1.append(f)
            else:
                files1.append(f)
        for f in list2:
            junk, ext = g.os_path_splitext(f)
            if self.limitToExtension:
                if ext == self.limitToExtension:
                    files2.append(f)
            else:
                files2.append(f)

        # Compare the files and set the yes, no and missing lists.
        yes = [] ; no = [] ; missing1 = [] ; missing2 = []
        for f1 in files1:
            head,f2 = g.os_path_split(f1)
            if f2 in files2:
                try:
                    name1 = g.os_path_join(dir1,f1)
                    name2 = g.os_path_join(dir2,f2)
                    val = filecmp.cmp(name1,name2,0)
                    if val: yes.append(f1)
                    else:    no.append(f1)
                except:
                    self.show("exception in filecmp.cmp")
                    g.es_exception()
                    missing1.append(f1)
            else:
                missing1.append(f1)
        for f2 in files2:
            head,f1 = g.os_path_split(f2)
            if f1 not in files1:
                missing2.append(f1)

        # Print the results.
        for kind, files in (
            ("----- matches --------",yes),
            ("----- mismatches -----",no),
            ("----- not found 1 ------",missing1),
            ("----- not found 2 ------",missing2),
        ):
            self.show(kind)
            for f in files:
                self.show(f)

        if self.outputFile:
            self.outputFile.close()
            self.outputFile = None

        return None # To keep pychecker happy.
    #@+node:ekr.20031218072017.3636: *3* compare_files (entry)
    def compare_files (self, name1, name2):

        if name1 == name2:
            self.show("File names are identical.\nPlease pick distinct files.")
            return

        f1 = f2 = None
        try:
            f1 = self.doOpen(name1)
            f2 = self.doOpen(name2)
            if self.outputFileName:
                self.openOutputFile()
            ok = self.outputFileName == None or self.outputFile
            ok = g.choose(ok and ok != 0,1,0)
            if f1 and f2 and ok: # Don't compare if there is an error opening the output file.
                self.compare_open_files(f1,f2,name1,name2)
        except:
            self.show("exception comparing files")
            g.es_exception()
        try:
            if f1: f1.close()
            if f2: f2.close()
            if self.outputFile:
                self.outputFile.close() ; self.outputFile = None
        except:
            self.show("exception closing files")
            g.es_exception()
    #@+node:ekr.20031218072017.3637: *3* compare_lines
    def compare_lines (self,s1,s2):

        if self.ignoreLeadingWhitespace:
            s1 = s1.lstrip()
            s2 = s2.lstrip()

        if self.ignoreInteriorWhitespace:
            k1 = g.skip_ws(s1,0)
            k2 = g.skip_ws(s2,0)
            ws1 = s1[:k1]
            ws2 = s2[:k2]
            tail1 = s1[k1:]
            tail2 = s2[k2:]
            tail1 = tail1.replace(" ","").replace("\t","")
            tail2 = tail2.replace(" ","").replace("\t","")
            s1 = ws1 + tail1
            s2 = ws2 + tail2

        return s1 == s2
    #@+node:ekr.20031218072017.3638: *3* compare_open_files
    def compare_open_files (self, f1, f2, name1, name2):

        # self.show("compare_open_files")
        lines1 = 0 ; lines2 = 0 ; mismatches = 0 ; printTrailing = True
        sentinelComment1 = sentinelComment2 = None
        if self.openOutputFile():
            self.show("1: " + name1)
            self.show("2: " + name2)
            self.show("")
        s1 = s2 = None
        #@+<< handle opening lines >>
        #@+node:ekr.20031218072017.3639: *4* << handle opening lines >>
        if self.ignoreSentinelLines:

            s1 = g.readlineForceUnixNewline(f1) ; lines1 += 1
            s2 = g.readlineForceUnixNewline(f2) ; lines2 += 1
            # Note: isLeoHeader may return None.
            sentinelComment1 = self.isLeoHeader(s1)
            sentinelComment2 = self.isLeoHeader(s2)
            if not sentinelComment1: self.show("no @+leo line for " + name1)
            if not sentinelComment2: self.show("no @+leo line for " + name2)

        if self.ignoreFirstLine1:
            if s1 == None:
                g.readlineForceUnixNewline(f1) ; lines1 += 1
            s1 = None

        if self.ignoreFirstLine2:
            if s2 == None:
                g.readlineForceUnixNewline(f2) ; lines2 += 1
            s2 = None
        #@-<< handle opening lines >>
        while 1:
            if s1 == None:
                s1 = g.readlineForceUnixNewline(f1) ; lines1 += 1
            if s2 == None:
                s2 = g.readlineForceUnixNewline(f2) ; lines2 += 1
            #@+<< ignore blank lines and/or sentinels >>
            #@+node:ekr.20031218072017.3640: *4* << ignore blank lines and/or sentinels >>
            # Completely empty strings denotes end-of-file.
            if s1 and len(s1) > 0:
                if self.ignoreBlankLines and len(s1.strip()) == 0:
                    s1 = None ; continue

                if self.ignoreSentinelLines and sentinelComment1 and self.isSentinel(s1,sentinelComment1):
                    s1 = None ; continue

            if s2 and len(s2) > 0:
                if self.ignoreBlankLines and len(s2.strip()) == 0:
                    s2 = None ; continue

                if self.ignoreSentinelLines and sentinelComment2 and self.isSentinel(s2,sentinelComment2):
                    s2 = None ; continue
            #@-<< ignore blank lines and/or sentinels >>
            n1 = len(s1) ; n2 = len(s2)
            if n1==0 and n2 != 0: self.show("1.eof***:")
            if n2==0 and n1 != 0: self.show("2.eof***:")
            if n1==0 or n2==0: break
            match = self.compare_lines(s1,s2)
            if not match: mismatches += 1
            #@+<< print matches and/or mismatches >>
            #@+node:ekr.20031218072017.3641: *4* << print matches and/or mismatches >>
            if self.limitCount == 0 or mismatches <= self.limitCount:

                if match and self.printMatches:

                    if self.printBothMatches:
                        z1 = "1." + str(lines1)
                        z2 = "2." + str(lines2)
                        self.dump(z1.rjust(6) + ' :',s1)
                        self.dump(z2.rjust(6) + ' :',s2)
                    else:
                        self.dump(str(lines1).rjust(6) + ' :',s1)

                if not match and self.printMismatches:
                    z1 = "1." + str(lines1)
                    z2 = "2." + str(lines2)
                    self.dump(z1.rjust(6) + '*:',s1)
                    self.dump(z2.rjust(6) + '*:',s2)
            #@-<< print matches and/or mismatches >>
            #@+<< warn if mismatch limit reached >>
            #@+node:ekr.20031218072017.3642: *4* << warn if mismatch limit reached >>
            if self.limitCount > 0 and mismatches >= self.limitCount:

                if printTrailing:
                    self.show("")
                    self.show("limit count reached")
                    self.show("")
                    printTrailing = False
            #@-<< warn if mismatch limit reached >>
            s1 = s2 = None # force a read of both lines.
        #@+<< handle reporting after at least one eof is seen >>
        #@+node:ekr.20031218072017.3643: *4* << handle reporting after at least one eof is seen >>
        if n1 > 0: 
            lines1 += self.dumpToEndOfFile("1.",f1,s1,lines1,printTrailing)

        if n2 > 0:
            lines2 += self.dumpToEndOfFile("2.",f2,s2,lines2,printTrailing)

        self.show("")
        self.show("lines1:" + str(lines1))
        self.show("lines2:" + str(lines2))
        self.show("mismatches:" + str(mismatches))
        #@-<< handle reporting after at least one eof is seen >>
    #@+node:ekr.20031218072017.3644: *3* filecmp
    def filecmp (self,f1,f2):

        val = filecmp.cmp(f1,f2)
        if 1:
            if val: self.show("equal")
            else:   self.show("*** not equal")
        else:
            self.show("filecmp.cmp returns:")
            if val: self.show(str(val)+ " (equal)")
            else:   self.show(str(val) + " (not equal)")
        return val
    #@+node:ekr.20031218072017.3645: *3* utils...
    #@+node:ekr.20031218072017.3646: *4* doOpen
    def doOpen (self,name):

        try:
            f = open(name,'r')
            return f
        except:
            self.show("can not open:" + '"' + name + '"')
            return None
    #@+node:ekr.20031218072017.3647: *4* dump
    def dump (self,tag,s):

        compare = self ; out = tag

        for ch in s[:-1]: # don't print the newline

            if compare.makeWhitespaceVisible:
                if ch == '\t':
                    out += "[" ; out += "t" ; out += "]"
                elif ch == ' ':
                    out += "[" ; out += " " ; out += "]"
                else: out += ch
            else:
                if 1:
                    out += ch
                else: # I don't know why I thought this was a good idea ;-)
                    if ch == '\t' or ch == ' ':
                        out += ' '
                    else:
                        out += ch

        self.show(out)
    #@+node:ekr.20031218072017.3648: *4* dumpToEndOfFile
    def dumpToEndOfFile (self,tag,f,s,line,printTrailing):

        trailingLines = 0
        while 1:
            if not s:
                s = g.readlineForceUnixNewline(f)
            if len(s) == 0: break
            trailingLines += 1
            if self.printTrailingMismatches and printTrailing:
                z = tag + str(line)
                tag2 = z.rjust(6) + "+:"
                self.dump(tag2,s)
            s = None

        self.show(tag + str(trailingLines) + " trailing lines")
        return trailingLines
    #@+node:ekr.20031218072017.3649: *4* isLeoHeader & isSentinel
    #@+at These methods are based on atFile.scanHeader(). They are simpler
    # because we only care about the starting sentinel comment: any line
    # starting with the starting sentinel comment is presumed to be a
    # sentinel line.
    #@@c

    def isLeoHeader (self,s):

        tag = "@+leo"
        j = s.find(tag)
        if j > 0:
            i = g.skip_ws(s,0)
            if i < j: return s[i:j]
            else: return None
        else: return None

    def isSentinel (self,s,sentinelComment):

        i = g.skip_ws(s,0)
        return g.match(s,i,sentinelComment)
    #@+node:ekr.20031218072017.1144: *4* openOutputFile (compare)
    def openOutputFile (self):

        if self.outputFileName == None:
            return
        theDir,name = g.os_path_split(self.outputFileName)
        if len(theDir) == 0:
            self.show("empty output directory")
            return
        if len(name) == 0:
            self.show("empty output file name")
            return
        if not g.os_path_exists(theDir):
            self.show("output directory not found: " + theDir)
        else:
            try:
                if self.appendOutput:
                    self.show("appending to " + self.outputFileName)
                    self.outputFile = open(self.outputFileName,"ab")
                else:
                    self.show("writing to " + self.outputFileName)
                    self.outputFile = open(self.outputFileName,"wb")
            except:
                self.outputFile = None
                self.show("exception opening output file")
                g.es_exception()
    #@+node:ekr.20031218072017.3650: *4* show (leoCompare) (not changed)
    def show (self,s):

        # g.pr(s)
        if self.outputFile:
            # self.outputFile is opened in 'wb' mode.
            s = g.toEncodedString(s + '\n')
            self.outputFile.write(s)
        elif self.c:
            g.es(s)
        else:
            g.pr(s)
            g.pr('')
    #@+node:ekr.20031218072017.3651: *4* showIvars
    def showIvars (self):

        self.show("fileName1:"        + str(self.fileName1))
        self.show("fileName2:"        + str(self.fileName2))
        self.show("outputFileName:"   + str(self.outputFileName))
        self.show("limitToExtension:" + str(self.limitToExtension))
        self.show("")

        self.show("ignoreBlankLines:"         + str(self.ignoreBlankLines))
        self.show("ignoreFirstLine1:"         + str(self.ignoreFirstLine1))
        self.show("ignoreFirstLine2:"         + str(self.ignoreFirstLine2))
        self.show("ignoreInteriorWhitespace:" + str(self.ignoreInteriorWhitespace))
        self.show("ignoreLeadingWhitespace:"  + str(self.ignoreLeadingWhitespace))
        self.show("ignoreSentinelLines:"      + str(self.ignoreSentinelLines))
        self.show("")

        self.show("limitCount:"              + str(self.limitCount))
        self.show("printMatches:"            + str(self.printMatches))
        self.show("printMismatches:"         + str(self.printMismatches))
        self.show("printTrailingMismatches:" + str(self.printTrailingMismatches))
    #@-others

class leoCompare (baseLeoCompare):
    """A class containing Leo's compare code."""
    pass
#@-others
#@-leo
