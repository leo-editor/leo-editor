# -*- coding: utf-8 -*-
# Copyright (C) 2013 Almar Klein

"""
Define tasks that can be executed by the file browser.
These inherit from proxies.Task and implement that specific interface.
"""

import re

from . import proxies


class SearchTask(proxies.Task):
    __slots__ = []
    
    def process(self, proxy, pattern=None, matchCase=False, regExp=False, **rest):
        
        # Quick test
        if not pattern:
            return
        
        # Get text
        text = self._getText(proxy)
        if not text:
            return
        
        # Get search text. Deal with case sensitivity
        searchText = text
        if not matchCase:
            searchText = searchText.lower()
            pattern = pattern.lower()
        
        # Search indices
        if regExp:
            indices = self._getIndicesRegExp(searchText, pattern)
        else:
            indices = self._getIndicesNormal1(searchText, pattern)
        
        # Return as lines
        if indices:
            return self._indicesToLines(text, indices)
        else:
            return []
    
    
    def _getText(self, proxy):
        
        # Init
        path = proxy.path()
        fsProxy = proxy._fsProxy
       
        # Get file size
        try:
            size = fsProxy.fileSize(path)
        except NotImplementedError:
            pass
        size = size or 0
        
        # Search all Python files. Other files need be < xx bytes
        if path.lower().endswith('.py') or size < 100*1024:
            pass
        else:
            return None
        
        # Get text
        bb = fsProxy.read(path)
        if bb is None:
            return
        try:
            return bb.decode('utf-8')
        except UnicodeDecodeError:
            # todo: right now we only do utf-8
            return None
    
    
    def _getIndicesRegExp(self, text, pattern):
        indices = []
        for match in re.finditer(pattern, text, re.MULTILINE | re.UNICODE):
                indices.append( match.start() )
        return indices
    
    
    def _getIndicesNormal1(self, text, pattern):
        indices = []
        i = -1
        while True:
            i = text.find(pattern,i+1)
            if i>=0:
                indices.append(i)
            else:
                break
        return indices
    
    
    def _getIndicesNormal2(self, text, pattern):
        indices = []
        i = 0
        for line in text.splitlines(True):
            i2 = line.find(pattern)
            if i2>=0:
                indices.append(i+i2)
            i += len(line)
        return indices
    
    
    def _indicesToLines(self, text, indices):
        
        # Determine line endings
        LE = self._determineLineEnding(text)
        
        # Obtain line and line numbers
        lines = []
        for i in indices:
            # Get linenr and index of the line
            linenr = text.count(LE, 0, i) + 1
            i1 = text.rfind(LE, 0, i)
            i2 = text.find(LE, i)
            # Get line and strip
            if i1<0:
                i1 = 0
            line = text[i1:i2].strip()[:80]
            # Store
            lines.append( (linenr, repr(line)) )
        
        # Set result
        return lines
    
    
    def _determineLineEnding(self, text):
        """ function to determine quickly whether LF or CR is used
        as line endings. Windows endings (CRLF) result in LF
        (you can split lines with either char).
        """
        i = 0
        LE = '\n'
        while i < len(text):
            i += 128
            LF = text.count('\n', 0, i)
            CR = text.count('\r', 0, i)
            if LF or CR:
                if CR > LF:
                    LE = '\r'
                break
        return LE



class PeekTask(proxies.Task):
    """ To peek the high level structure of a task.
    """
    __slots__ = []
    
    stringStart = re.compile('("""|\'\'\'|"|\')|#')
    endProgs = {
        "'": re.compile(r"(^|[^\\])(\\\\)*'"),
        '"': re.compile(r'(^|[^\\])(\\\\)*"'),
        "'''": re.compile(r"(^|[^\\])(\\\\)*'''"),
        '"""': re.compile(r'(^|[^\\])(\\\\)*"""')
        }
    
    definition = re.compile(r'^(def|class)\s*(\w*)')
    
    def process(self, proxy):
        path = proxy.path()
        fsProxy = proxy._fsProxy
        
        # Search only Python files
        if not path.lower().endswith('.py'):
            return None
        
        # Get text
        bb = fsProxy.read(path)
        if bb is None:
            return
        try:
            text = bb.decode('utf-8')
            del bb
        except UnicodeDecodeError:
            # todo: right now we only do utf-8
            return
        
        # Parse
        return list(self._parseLines(text.splitlines()))
    
    def _parseLines(self, lines):
        
        stringEndProg = None
        
        linenr = 0
        for line in lines:
            linenr += 1
            
            # If we are in a triple-quoted multi-line string, find the end
            if stringEndProg is None:
                pos = 0
            else:
                endMatch = stringEndProg.search(line)
                if endMatch is None:
                    continue
                else:
                    pos = endMatch.end()
                    stringEndProg = None
            
            # Now process all tokens
            while True:
                match = self.stringStart.search(line, pos)
                
                if pos == 0: # If we are at the start of the line, see if we have a top-level class or method definition
                    end = len(line) if match is None else match.start()
                    definitionMatch = self.definition.search(line[:end])
                    if definitionMatch is not None:
                        if definitionMatch.group(1) == 'def':
                            yield (linenr, 'def ' + definitionMatch.group(2))
                        else:
                            yield (linenr, 'class ' + definitionMatch.group(2))
                    
                if match is None:
                    break # Go to next line
                if match.group()=="#":
                    # comment
                    # yield 'C:'
                    break # Go to next line
                else:
                    endMatch = self.endProgs[match.group()].search(line[match.end():])
                    if endMatch is None:
                        if len(match.group()) == 3 or line.endswith('\\'):
                            # Multi-line string
                            stringEndProg = self.endProgs[match.group()]
                            break
                        else: # incorrect end of single-quoted string
                            break
                        
                    # yield 'S:' + (match.group() + line[match.end():][:endMatch.end()])
                    pos = match.end() + endMatch.end()
        


class DocstringTask(proxies.Task):
    __slots__ = []
    
    def process(self, proxy):
        path = proxy.path()
        fsProxy = proxy._fsProxy
        
        # Search only Python files
        if not path.lower().endswith('.py'):
            return None
        
        # Get text
        bb = fsProxy.read(path)
        if bb is None:
            return
        try:
            text = bb.decode('utf-8')
            del bb
        except UnicodeDecodeError:
            # todo: right now we only do utf-8
            return
        
        # Find docstring
        lines = []
        delim = None # Not started, in progress, done
        count = 0
        for line in text.splitlines():
            count += 1
            if count > 200:
                break
            # Try to find a start
            if not delim:
                if line.startswith('"""'):
                    delim = '"""'
                    line = line.lstrip('"')
                elif line.startswith("'''"):
                    delim = "'''"
                    line = line.lstrip("'")
            # Try to find an end (may be on the same line as the start)
            if delim and delim in line:
                line = line.split(delim, 1)[0]
                count = 999999999  # Stop; we found the end
            # Add this line
            if delim:
                lines.append(line)
        
        # Limit number of lines
        if len(lines) > 16:
            lines = lines[:16] + ['...']
        # Make text and strip
        doc = '\n'.join(lines)
        doc = doc.strip()
        
        return doc



class RenameTask(proxies.Task):
    __slots__ = []
    
    def process(self, proxy, newpath=None, removeold=False):
        path = proxy.path()
        fsProxy = proxy._fsProxy
        
        if not newpath:
            return
        
        if removeold:
            # Works for files and dirs
            fsProxy.rename(path, newpath)
            # The fsProxy will detect that this file is now deleted
        else:
            # Work only for files: duplicate
            # Read bytes
            bb = fsProxy.read(path)
            if bb is None:
                return
            # write back with new name
            fsProxy.write(newpath, bb)


class CreateTask(proxies.Task):
    __slots__ = []
    
    def process(self, proxy, newpath=None, file=True):
        proxy.path()
        fsProxy = proxy._fsProxy
        
        if not newpath:
            return
        
        if file:
            fsProxy.write(newpath, b'')
        else:
            fsProxy.createDir(newpath)


class RemoveTask(proxies.Task):
    __slots__ = []
    
    def process(self, proxy):
        path = proxy.path()
        fsProxy = proxy._fsProxy
        
        # Remove
        fsProxy.remove(path)
        # The fsProxy will detect that this file is now deleted
