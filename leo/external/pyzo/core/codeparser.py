# -*- coding: utf-8 -*-
# Copyright (C) 2016, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module codeparser

Analyses the source code to get the structure of a module/script.
This can be used for fictive introspection, and to display the
structure of a source file in for example a tree widget.

"""

#TODO: replace this module, get data from the syntax highlighter in the code editor

import time, threading, re
import pyzo


# Define regular expression patterns
classPattern  = r'^\s*' # Optional whitespace
classPattern += r'(cp?def\s+)?' # Cython preamble + whitespace
classPattern += r'class\s+'  # The class keyword + whitespace
classPattern += r'([a-zA-Z_][a-zA-Z_0-9]*)\s*' # The NAME + optional whitespace
classPattern += r'(\(.*?\))?' # The superclass(es)
classPattern += r'\s*:' # Optional whitespace and the colon
#
defPattern  = r'^\s*' # Optional whitespace
defPattern += r'(async )?' # Optional async keyword
defPattern += r'(cp?)?def\s+' # The Cython preamble, def keyword and whitespace
defPattern += r'([a-zA-Z_][\*a-zA-Z_0-9]*\s+)?' # Optional Cython return type
defPattern += r'([a-zA-Z_][a-zA-Z_0-9]*)\s*' # The NAME + optional whitespace
defPattern += r'\((.*?)\)' # The SIGNATURE
#defPattern += r'\s*:' # Optional whitespace and the colon
# Leave the colon, easier for cython

class Job:
    """ Simple class to represent a job. """
    def __init__(self, text, editorId):
        self.text = text
        self.editorId = editorId


class Result:
    """ Simple class to represent a parser result. """
    def __init__(self, rootItem, importList, editorId):
        self.rootItem = rootItem
        self.importList = importList
        self.editorId = editorId
    
    def isMatch(self, editorId):
        """ isMatch(editorId):
        Returns whether the result matches with the given editorId.
        The editorId can also be an editor instance. """
        if isinstance(editorId, int):
            return self.editorId == editorId
        else:
            return self.editorId == id(editorId)


class Parser(threading.Thread):
    """ Parser
    Parsing sourcecode in a separate thread, this class obtains
    introspection informarion. This class is also the interface
    to the parsed information; it has methods that can be used
    to extract information from the result.
    """
    
    def __init__(self):
        threading.Thread.__init__(self)
        
        # Reference current job
        self._job = None
        
        # Reference to last result
        self._result = None
        
        # Lock to enable save threading
        self._lock = threading.RLock()
        
        # Set deamon
        self.daemon = True
        self._exit = False
    
    
    def stop(self, timeout=1.0):
        self._exit = True
        self.join(timeout)
    
    
    def parseThis(self, editor):
        """ parseThis(editor)
        Give the parser new text to parse.
        If the parser is busy parsing text, it will stop doing that
        and start anew with the most recent version of the text.
        """
        
        # Get text
        text = editor.toPlainText()
        
        # Make job
        self._lock.acquire()
        self._job = Job(text, id(editor))
        self._lock.release()
    
    
    def getFictiveNameSpace(self, editor):
        """ getFictiveNameSpace(editor)
        Produce the fictive namespace, based on the current position.
        A list of names is returned.
        """
        
        # Obtain result
        result = self._getResult()
        if result is None or not result.isMatch(editor):
            return []
        
        # Get linenr and indent. These are used to establish the namespace
        # based on indentation.
        cursor = editor.textCursor()
        linenr = cursor.blockNumber()
        index = cursor.positionInBlock()
        
        # init empty namespace and item list
        namespace = []
        items = result.rootItem.children
        curIsClass = False  # to not add methods (of classes)
        
        while items:
            curitem = None
            for item in items:
                # append name
                if not curIsClass and item.type in ['class', 'def']:
                    namespace.append( item.name )
                # check if this is the one only last one remains
                if (item.type in ['class', 'def'] and item.linenr <= linenr and item.linenr2 > linenr):
                    curitem = item
            # prepare for next round
            if curitem and curitem.indent < index:
                items = curitem.children
                if curitem.type=='class':
                    curIsClass = True
                else:
                    curIsClass = False
            else:
                items = []
                
        return namespace
    
    
    def getFictiveClass(self, name, editor, handleSelf=False):
        """ getFictiveClass(name, editor, handleSelf=False)
        Return the fictive class object of the given name, or None
        if it does not exist. If handleSelf is True, automatically
        handles "self." names.
        """
        return self._getFictiveItem(name, 'class', editor, handleSelf)
    
    
    def getFictiveSignature(self, name, editor, handleSelf=False):
        """ getFictiveSignature(name, editor, handleSelf=False)
        Get the signature of the fictive function or method of the
        given name. Returns None if the given name is not a known
        function or method. If handleSelf is True, automatically
        handles "self." names.
        """
        # Get item being a function
        item = self._getFictiveItem(name, 'def', editor, handleSelf)
        
        # Get item being a class
        if not item:
            item = self._getFictiveItem(name, 'class', editor, handleSelf)
            if item:
                for subItem in item.children:
                    if subItem.name == '__init__' and subItem.type == 'def':
                        item = subItem
                        break
                else:
                    item = None
        
        # Process or return None if there was no item
        if item:
            nameParts = name.split('.')
            return '{}({})'.format(nameParts[-1], item.sig)
        else:
            return None
    
    
    def getFictiveImports(self, editor):
        """ getFictiveImports(editor)
        Get the fictive imports of this source file.
        tuple:
        - list of names that are imported,
        - a dict with the line to import each name
        """
        
        # Obtain result
        result = self._getResult()
        if result is None or not result.isMatch(editor):
            return [], []
        
        # Extract list of names and dict of lines
        imports = []
        importlines = {}
        for item in result.importList:
            imports.append(item.name)
            importlines[item.name] = item.text
        return imports, importlines
    
    
    def _getResult(self):
        """ getResult()
        Savely Obtain result.
        """
        self._lock.acquire()
        result = self._result
        self._lock.release()
        return result
    
    
    def _getFictiveItem(self, name, type, editor, handleSelf=False):
        """ _getFictiveItem(name, type, editor, handleSelf=False)
        Obtain the fictive item of the given name and type.
        If handleSelf is True, will handle "self." correctly.
        Intended for internal use.
        """
        
        # Obtain result
        result = self._getResult()
        if result is None or not result.isMatch(editor):
            return None
        
        # Split name in parts
        nameParts = name.split('.')
        
        # Try if the first part represents a class instance
        if handleSelf:
            item = self._getFictiveCurrentClass(editor, nameParts[0])
            if item:
                nameParts[0] = item.name
        
        # Init
        name = nameParts.pop(0)
        items = result.rootItem.children
        theItem = None
        
        # Search for name
        while items:
            for item in items:
                if item.name == name:
                    # Found it
                    if nameParts:
                        # Go down one level
                        name = nameParts.pop(0)
                        items = item.children
                        break
                    else:
                        # This is it, is it what we wanted?
                        if item.type == type:
                            theItem = item
                            items = []
                            break
            else:
                # Did not find it
                items = []
        
        return theItem
    
    
    def _getFictiveCurrentClass(self, editor, selfname):
        """ _getFictiveCurrentClass(editor, selfname)
        Get the fictive object for the class referenced
        using selfname (usually 'self').
        Intendef for internal use.
        """
        
        # Obtain result
        result = self._getResult()
        if result is None:
            return None
        
        # Get linenr and indent
        cursor = editor.textCursor()
        linenr = cursor.blockNumber()
        index = cursor.positionInBlock()
        
        
        # Init
        items = result.rootItem.children
        theclass = None
        
        while items:
            curitem = None
            for item in items:
                # check if this is the one only last one remains
                if item.linenr <= linenr:
                    if not item.linenr2 > linenr:
                        continue
                    curitem = item
                    if item.type == 'def' and item.selfname==selfname:
                        theclass = item.parent
                else:
                    break
            
            # prepare for next round
            if curitem and curitem.indent < index:
                items = curitem.children
            else:
                items = []
        
        # return
        return theclass
    
    
    def run(self):
        """ run()
        This is the main loop.
        """
        
        time.sleep(0.5)
        try:
            while True:
                time.sleep(0.1)
                
                if self._exit:
                    return
                
                if self._job:
                    
                    # Savely obtain job
                    self._lock.acquire()
                    job = self._job
                    self._job = None
                    self._lock.release()
                    
                    # Analyse job
                    result = self._analyze(job)
                    
                    # Savely store result
                    self._lock.acquire()
                    self._result = result
                    self._lock.release()
                    
                    # Notify
                    if pyzo.editors is not None:
                        pyzo.editors.parserDone.emit()
            
        except AttributeError:
            pass # when python exits, time can be None...
    
    
    def _analyze(self, job):
        """ The core function.
        Analyses the source code.
        Produces:
        - a tree of FictiveObject objects.
        - a (flat) list of the same object
        - a list of imports
        """
        
        # Remove multiline strings
        text = washMultilineStrings(job.text)
        
        # Split text in lines
        lines = text.splitlines()
        lines.insert(0,"") # so the lines start at 1
        
        # The structure object. It will first only consist of class and defs
        # the rest will be inserted afterwards.
        root = FictiveObject("root", 0, -1, 'root')
        
        # Also keep a flat list (while running this function)
        flatList = []
        
        # Cells and imports are inserted in the structure afterwards
        leafs = []
        
        # Keep a list of imports
        importList = []
        
        # To know when to make something new when for instance a class is defined
        # in an if statement, we keep track of the last valid node/object:
        # Put inside a list, so we can set it from inside a subfuncion
        lastObject = [root]
        
        # Define funcion to put an item in the structure in the right parent
        def appendToStructure(object):
            # find position in structure to insert
            node = lastObject[0]
            while ( (object.indent <= node.indent) and (node is not root) ):
                node = node.parent
            # insert object
            flatList.append(object)
            node.children.append(object)
            object.parent = node
            lastObject[0] = object
        
        # Find objects!
        # type can be: cell, class, def, import, var
        for i in range( len(lines) ):
            
            # Obtain line
            line = lines[i]
            
            # Should we stop?
            if self._job or self._exit:
                break
            
            # Remove indentation
            tmp = line.lstrip()
            indent = len(line) - len(tmp)
            line = tmp.rstrip()
            
            # Detect cells
            if line.startswith('##') or line.startswith('#%%') or line.startswith('# %%'):
                if line.startswith('##'):
                    name = line[2:].lstrip()
                elif line.startswith('#%%'):
                    name = line[3:].lstrip()
                else:
                    name = line[4:].lstrip()
                item = FictiveObject('cell', i, indent, name)
                leafs.append(item)
                # Next! (we have to put this before the elif stuff below
                # because it looks like a comment!)
                continue
                
            # Split in line and comment
            line, tmp, cmnt = line.partition('#')
            line, cmnt = line.rstrip(), cmnt.lower().strip()
            
            # Detect todos
            if cmnt and (cmnt.startswith('todo:') or cmnt.startswith('2do:') ):
                item = FictiveObject('todo', i, indent, cmnt)
                item.linenr2 = i+1 # a todo is active at one line only
                leafs.append(item)
            
            # Continue of no line left
            if not line:
                continue
            
            # Find last valid node. As the indent of the root is set to -1,
            # this will always stop at the root
            while indent <= lastObject[0].indent:
                lastObject[0].linenr2 = i # close object
                lastObject[0] = lastObject[0].parent
            
            # Make a lowercase version of the line
            foundSomething = False
            
            # Detect classes
            if not foundSomething:
                classResult = re.search(classPattern, line)
                
                if classResult:
                    foundSomething = True
                    # Get name
                    name = classResult.group(2)
                    item = FictiveObject('class', i, indent, name)
                    appendToStructure(item)
                    item.supers = []
                    item.members = []
                    # Get inheritance
                    supers = classResult.group(3)
                    if supers:
                        supers = supers[1:-1].split(',')
                        supers = [tmp.strip() for tmp in supers]
                        item.supers = [tmp for tmp in supers if tmp]
            
            # Detect functions and methods (also multiline)
            if (not foundSomething) and line.count('def '):
                # Get a multiline version (for long defs)
                multiLine = line
                for ii in range(1,5):
                    if i+ii<len(lines): multiLine += ' '+lines[i+ii].strip()
                # Get result
                defResult = re.search(defPattern, multiLine)
                if defResult:
                    # Get name
                    name = defResult.group(4)
                    item = FictiveObject('def', i, indent, name)
                    appendToStructure(item)
                    item.selfname = None # will be filled in if a valid method
                    item.sig = defResult.group(5)
                    # is it a method? -> add method to attr and find selfname
                    if item.parent.type == 'class':
                        item.parent.members.append(name)
                        
                        # Find what is used as "self"
                        i2 = line.find('(')
                        i4 = line.find(",",i2)
                        if i4 < 0:
                            i4 = line.find(")",i2)
                        if i4 < 0:
                            i4 = i2
                        selfname = line[i2+1:i4].strip()
                        if selfname:
                            item.selfname = selfname
            
            elif line.count('import '):
                if line.startswith("import "):
                    for name in ParseImport(line[7:]):
                        item = FictiveObject('import', i, indent, name)
                        item.text = line
                        item.linenr2 = i+1 # an import is active at one line only
                        leafs.append(item)
                        importList.append(item)
                    
                elif line.startswith("from "):
                    i1 = line.find(" import ")
                    for name in ParseImport(line[i1+8:]):
                        if not IsValidName(name):
                            continue # we cannot do that!
                        item = FictiveObject('import', i, indent, name)
                        item.text = line
                        item.linenr2 = i+1 # an import is active at one line only
                        leafs.append(item)
                        importList.append(item)
            
            elif not indent and line.startswith('if __name__ ==') and '__main__' in line:
                item = FictiveObject('nameismain', i, indent, '__main__')
                item.text = line
                appendToStructure(item)
            
            elif line.count('='):
                if lastObject[0].type=='def' and lastObject[0].selfname:
                    selfname = lastObject[0].selfname + "."
                    line = line.partition("=")[0]
                    if line.count(selfname):
                        # A lot of ifs here. If we got here, the line is part of
                        # a valid method and contains the selfname before the =.
                        # Now we need to establish whether there is a valid
                        # assignment done here...
                        parts = line.split(",") # handle tuples
                        for part in parts:
                            part = part.strip()
                            part2 = part[len(selfname):]
                            if part.startswith(selfname) and IsValidName(part2):
                                # add to the list if not already present
                                defItem = lastObject[0]
                                classItem = lastObject[0].parent
                                #
                                item = FictiveObject('attribute', i, indent, part2)
                                item.parent = defItem
                                defItem.children.append(item)
                                if part2 not in classItem.members:
                                    classItem.members.append(part2)
        
     
        ## Post processing
        
        def getTwoItems(series, linenr):
            """ Return the two items just above and below the
            given linenr. The object always is a class or def.
            """
            # find object after linenr
            object1, object2 = None, None # if no items at all
            i = -1
            for i in range(len(series)):
                object = series[i]
                if object.type not in ['class','def']:
                    continue
                if object.linenr > linenr:
                    object2 = object
                    break
            # find object just before linenr
            for ii in range(i,-1,-1):
                object = series[ii]
                if object.type not in ['class','def']:
                    continue
                if object.linenr < linenr:
                    object1 = object
                    break
            # return result
            return object1, object2
                
        # insert the leafs (backwards as the last inserted is at the top)
        for leaf in reversed(leafs):
            ob1, ob2 = getTwoItems(flatList, leaf.linenr)
            if ob1 is None: # also if ob2 is None
                # insert in root
                root.children.insert(0,leaf)
                leaf.parent = root
                continue
            if ob2 is None:
                ob2parent = root
            else:
                ob2parent = ob2.parent
                
            
            # get the object IN which to insert it: ob1
            sibling = None
            while 1:
                canGoDeeper = ob1 is not ob2parent
                canGoDeeper = canGoDeeper and ob1 is not root
                shouldGoDeeper = ob1.indent >= leaf.indent
                shouldGoDeeper = shouldGoDeeper or ob1.linenr2 < leaf.linenr
                if canGoDeeper and shouldGoDeeper:
                    sibling = ob1
                    ob1 = ob1.parent
                else:
                    break
            
            # insert into ob1, after sibling (if available)
            L = ob1.children
            if sibling:
                i = L.index(sibling)
                L.insert(i+1,leaf)
            else:
                L.insert(0,leaf)
        
        # Return result
        return Result(root, importList, job.editorId)



## Helper classes and functions


class FictiveObject:
    """ An un-instantiated object.
    type can be class, def, import, cell, todo
    extra stuff:
    class   - supers, members
    def     - selfname
    imports - text
    cell    -
    todo    -
    attribute -
    """
    def __init__(self, type, linenr, indent, name):
        self.children = []
        self.type = type
        self.linenr = linenr # at which line this object starts
        self.linenr2 = 9999999 # at which line it ends
        self.indent = indent
        self.name = name
        self.sig = ''  # for functions and methods
    

namechars = 'abcdefghijklmnopqrstuvwxyz_0123456789'
def IsValidName(name):
    """ Given a string, checks whether it is a
    valid name (dots are not valid!)
    """
    if not name:
        return False
    name = name.lower()
    if name[0] not in namechars[0:-10]:
        return False
    tmp = map(lambda x: x not in namechars, name[2:])
    return sum(tmp)==0
    
    
def ParseImport(names):
    for part in names.split(","):
        i1 = part.find(' as ')
        if i1>0:
            name = part[i1+3:].strip()
        else:
            name = part.strip()
        yield name


def findString(text, s, i):
    """ findString(text, s)
    Find s in text, but only if s is not in a string or commented
    Helper function for washMultilineStrings """
    
    while True:
        i = _findString(text, s, i)
        if i<-1:
            i = -i+1
        else:
            break
    return i


def _findString(text, s, i):
    """ Helper function of findString, which is called recursively
    until a match is found, or it is clear there is no match. """
    
    # Find occurrence
    i2 = text.find(s, i)
    if i2<0:
        return -1
    
    # Find newline  (if none, we're done)
    i1 = text.rfind('\n', 0, i2)
    if i1<0:
        return i2
    
    # Extract the part on the line up to the match
    line = text[i1:i2]
    
    # Count quotes, we're done if we found none
    if not line.count('"') and not line.count("'") and not line.count('#'):
        return i2
    
    # So we found quotes, now really count them ...
    prev = ''
    inString = '' # this is a boolean combined with a flag which quote was used
    isComment = False
    for c in line:
        if c == '#':
            if not inString:
                isComment = True
                break
        elif c in "\"\'":
            if not inString:
                inString = c
            elif prev != '\\':
                if inString == c:
                    inString = '' # exit string
                else:
                    pass # the other quote can savely be used inside this string
        prev = c
    
    # If we are in a string, this match is false ...
    if inString or isComment:
        return -i2 # indicate failure and where to continue
    else:
        return i2 # all's right
    

def washMultilineStrings(text):
    """ washMultilineStrings(text)
    Replace all text within multiline strings with dummy chars
    so that it is not parsed.
    """
    i=0
    s1 = "'''"
    s2 = '"""'
    while i<len(text):
        # Detect start of a multiline comment (there are two versions)
        i1 = findString(text, s1, i)
        i2 = findString(text, s2, i)
        # Stop if nothing found ...
        if i1 == -1 and i2 == -1:
            break
        else:
            # Make no result be very large
            if i1==-1:
                i1 = 2**60
            if i2==-1:
                i2 = 2**60
            # Find end of the multiline comment
            if i1 < i2:
                i3 = i1+3
                i4 = text.find(s1, i3)
            else:
                i3 = i2+3
                i4 = text.find(s2, i3)
            # No end found -> take all text, unclosed string!
            if i4==-1:
                i4 = 2**32
            # Leave only the first two quotes of the start of the comment
            i3 -= 1
            i4 += 3
            # Replace all non-newline chars
            tmp = re.sub(r'\S', ' ', text[i3:i4])
            text = text[:i3] + tmp + text[i3+len(tmp):]
            # Prepare for next round
            i = i4+1
    return text

"""
## testing skipping of multiline strings
def ThisShouldNotBeVisible():
  pass
class ThisShouldNotBeVisibleEither():
  pass
"""
