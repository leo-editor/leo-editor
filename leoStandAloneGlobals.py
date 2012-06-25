# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20120625092120.12469: * @file leoStandAloneGlobals.py
#@@first

'''Stand-alone version of leoGlobals.py.  This module imports no Leo module. '''

#@@language python
#@@tabwidth -4
#@@pagewidth 70

import sys
isPython3 = sys.version_info >= (3,0,0)

#@+<< imports >>
#@+node:ekr.20120625092120.12840: ** << imports >>
import gettext
import operator
import os

# import pdb
    # Do NOT import pdb here!
    # We shall define pdb as a _function_ below.

import subprocess

# import sys
    # Imported earlier.

import traceback
import types
#@-<< imports >>
#@+<< changes >>
#@+node:ekr.20120625092120.12814: ** << changes >>
#@@nocolor-node
#@+at
# 
# Differences between this file and leoGlobals.c:
#     
# - Removed many seldom-used functions.
# - g defined at end of this file, not by Leo's startup logic.
# - Removed all references to g.app and c in the code.
# - Removed the following:
#     g.globalDirectiveList
#     g.tree_popup_handlers
#     global switches and g.trace_xxx vars.
#@-<< changes >>

# Define these for compatifility...
app = None
enableDB = True
inScript = False
unitTesting = False

#@+others
#@+node:ekr.20120625092120.12831: ** Classes
#@+node:ekr.20120625092120.12734: *3* class Bunch (object)
#@+at From The Python Cookbook: Often we want to just collect a bunch of
# stuff together, naming each item of the bunch; a dictionary's OK for
# that, but a small do-nothing class is even handier, and prettier to
# use.
# 
# Create a Bunch whenever you want to group a few variables:
# 
#     point = Bunch(datum=y, squared=y*y, coord=x)
# 
# You can read/write the named attributes you just created, add others,
# del some of them, etc:
#     if point.squared > threshold:
#         point.isok = True
#@@c

class Bunch (object):

    """A class that represents a colection of things.

    Especially useful for representing a collection of related variables."""

    def __init__(self,**keywords):
        self.__dict__.update (keywords)

    def __repr__(self):
        return self.toString()

    def ivars(self):
        return sorted(self.__dict__)

    def keys(self):
        return sorted(self.__dict__)

    def toString(self):
        tag = self.__dict__.get('tag')
        entries = ["%s: %s" % (key,str(self.__dict__.get(key)))
            for key in self.ivars() if key != 'tag']
        if tag:
            return "Bunch(tag=%s)...\n%s\n" % (tag,'\n'.join(entries))
        else:
            return "Bunch...\n%s\n" % '\n'.join(entries)

    # Used by new undo code.
    def __setitem__ (self,key,value):
        '''Support aBunch[key] = val'''
        return operator.setitem(self.__dict__,key,value)

    def __getitem__ (self,key):
        '''Support aBunch[key]'''
        return operator.getitem(self.__dict__,key)

    def get (self,key,theDefault=None):
        return self.__dict__.get(key,theDefault)

bunch = Bunch
#@+node:ekr.20120625092120.12735: *3* class NullObject
class NullObject:

    """An object that does nothing, and does it very well.
    
    From the Python cookbook, recipe 5.23.
    """

    def __init__   (self,*args,**keys): pass
    def __call__   (self,*args,**keys): return self
    # def __len__    (self): return 0 # Debatable.
    def __repr__   (self): return "NullObject"
    def __str__    (self): return "NullObject"
    if isPython3:
        def __bool__(self): return False
    else:
        def __nonzero__(self): return 0
    def __delattr__(self,attr):     return self
    def __getattr__(self,attr):     return self
    def __setattr__(self,attr,val): return self
    
nullObject = NullObject
#@+node:ekr.20120625092120.12741: *3* class FileLikeObject
# Note: we could use StringIo for this.

class FileLikeObject:

    """Define a file-like object for redirecting writes to a string.

    The caller is responsible for handling newlines correctly."""

    #@+others
    #@+node:ekr.20120625092120.12742: *4*  ctor (FileLikeObject)
    def __init__(self,encoding='utf-8',fromString=None):

        # g.trace('g.FileLikeObject:__init__','fromString',fromString)

        # New in 4.2.1: allow the file to be inited from string s.

        self.encoding = encoding or 'utf-8'

        if fromString:
            self.list = g.splitLines(fromString) # Must preserve newlines!
        else:
            self.list = []

        self.ptr = 0

    # In CStringIO the buffer is read-only if the initial value (fromString) is non-empty.
    #@+node:ekr.20120625092120.12743: *4* clear
    def clear (self):

        self.list = []
    #@+node:ekr.20120625092120.12744: *4* close
    def close (self):

        pass

        # The StringIo version free's the memory buffer.
    #@+node:ekr.20120625092120.12745: *4* flush
    def flush (self):

        pass
    #@+node:ekr.20120625092120.12746: *4* get & getvalue & read
    def get (self):

        return ''.join(self.list)

    getvalue = get # for compatibility with StringIo
    read = get # for use by sax.
    #@+node:ekr.20120625092120.12747: *4* readline
    def readline(self): # New for read-from-string (readOpenFile).

        if self.ptr < len(self.list):
            line = self.list[self.ptr]
            # g.trace(repr(line))
            self.ptr += 1
            return line
        else:
            return ''
    #@+node:ekr.20120625092120.12748: *4* write
    def write (self,s):

        if s:
            if g.isBytes(s):
                s = g.toUnicode(s,self.encoding)

            self.list.append(s)
    #@-others

fileLikeObject = FileLikeObject
#@+node:ekr.20120625092120.12609: ** Common functions
#@+node:ekr.20120625092120.12729: *3* angleBrackets
# Returns < < s > >

def angleBrackets(s):

    return ( "<<" + s +
        ">>") # must be on a separate line.
#@+node:ekr.20120625092120.12510: *3* callers & _callerName
def callers (n=4,count=0,excludeCaller=True,files=False):

    '''Return a list containing the callers of the function that called g.callerList.

    If the excludeCaller keyword is True (the default), g.callers is not on the list.

    If the files keyword argument is True, filenames are included in the list.
    '''

    # sys._getframe throws ValueError in both cpython and jython if there are less than i entries.
    # The jython stack often has less than 8 entries,
    # so we must be careful to call g._callerName with smaller values of i first.
    result = []
    # i = g.choose(excludeCaller,3,2)
    i = 3 if excludeCaller else 2
    while 1:
        s = g._callerName(i,files=files)
        if s:
            result.append(s)
        if not s or len(result) >= n: break
        i += 1

    result.reverse()
    if count > 0: result = result[:count]
    # sep = g.choose(files,'\n',',')
    sep = '\n' if files else ','
    return sep.join(result)
#@+node:ekr.20120625092120.12511: *4* _callerName
def _callerName (n=1,files=False):

    try: # get the function name from the call stack.
        f1 = sys._getframe(n) # The stack frame, n levels up.
        code1 = f1.f_code # The code object
        name = code1.co_name
        if name == '__init__':
            name = '__init__(%s,line %s)' % (
                g.shortFileName(code1.co_filename),code1.co_firstlineno)
        if files:
            return '%s:%s' % (g.shortFilename(code1.co_filename),name)
        else:
            return name # The code name
    except ValueError:
        return '' # The stack is not deep enough.
    except Exception:
        g.es_exception()
        return '' # "<no caller name>"
#@+node:ekr.20120625092120.12737: *3* cls
def cls():
    
    '''Clear the screen.'''
    
    import os
    import sys
    
    if sys.platform.lower().startswith('win'):
        os.system('cls')
#@+node:ekr.20120625092120.12613: *3* error, note & warning
def error (*args,**keys):
    g.es_print('Error:',color='red',*args,**keys)

def note (*args,**keys):
    g.es_print(*args,**keys)

def warning (*args,**keys):
    g.es_print('Warning:',color='blue',*args,**keys)
#@+node:ekr.20120625092120.12749: *3* funcToMethod
#@+at The following is taken from page 188 of the Python Cookbook.
# 
# The following method allows you to add a function as a method of any class. That
# is, it converts the function to a method of the class. The method just added is
# available instantly to all existing instances of the class, and to all instances
# created in the future.
# 
# The function's first argument should be self.
# 
# The newly created method has the same name as the function unless the optional
# name argument is supplied, in which case that name is used as the method name.
#@@c

def funcToMethod(f,theClass,name=None):

    setattr(theClass,name or f.__name__,f)
    # g.trace(name)
#@+node:ekr.20120625092120.12753: *3* getWord & getLine
def getWord (s,i):

    '''Return i,j such that s[i:j] is the word surrounding s[i].'''

    if i >= len(s): i = len(s) - 1
    if i < 0: i = 0
    # Scan backwards.
    while 0 <= i < len(s) and g.isWordChar(s[i]):
        i-= 1
    i += 1
    # Scan forwards.
    j = i
    while 0 <= j < len(s) and g.isWordChar(s[j]):
        j += 1
    return i,j

def getLine (s,i):

    '''Return i,j such that s[i:j] is the line surrounding s[i].
    s[i] is a newline only if the line is empty.
    s[j] is a newline unless there is no trailing newline.
    '''

    if i > len(s): i = len(s) -1 # Bug fix: 10/6/07 (was if i >= len(s))
    if i < 0: i = 0
    j = s.rfind('\n',0,i) # A newline *ends* the line, so look to the left of a newline.
    if j == -1: j = 0
    else:       j += 1
    k = s.find('\n',i)
    if k == -1: k = len(s)
    else:       k = k + 1
    # g.trace('i,j,k',i,j,k,repr(s[j:k]))
    return j,k
#@+node:ekr.20120625092120.12617: *3* internalError
def internalError (*args):

    callers = g.callers(5).split(',')
    caller = callers[-1]
    g.es_print('\nInternal Leo error in',caller,color='red')
    g.es_print(*args)
    g.es_print('Called from',','.join(callers[:-1]))
#@+node:ekr.20120625092120.12756: *3* makeDict
# From the Python cookbook.

def makeDict(**keys):

    """Returns a Python dictionary from using the optional keyword arguments."""

    return keys
#@+node:ekr.20120625092120.12512: *3* pdb
def pdb (message=''):

    """Fall into pdb."""

    import pdb # Required: we have just defined pdb as a function!

    if message:
        print(message)

    pdb.set_trace()
#@+node:ekr.20120625092120.12578: *3* shortFileName & shortFilename
def shortFileName (fileName):

    return g.os_path_basename(fileName)

shortFilename = shortFileName
#@+node:ekr.20120625092120.12690: *3* splitLines & joinLines
def splitLines (s):

    '''Split s into lines, preserving the number of lines and
    the endings of all lines, including the last line.'''

    if s:
        return s.splitlines(True) # This is a Python string function!
    else:
        return []

splitlines = splitLines

def joinLines (aList):

    return ''.join(aList)

joinlines = joinLines
#@+node:ekr.20120625092120.12764: *3* stripBrackets
def stripBrackets (s):

    '''Same as s.lstrip('<').rstrip('>') except it works for Python 2.2.1.'''

    if s.startswith('<'):
        s = s[1:]
    if s.endswith('>'):
        s = s[:-1]
    return s
#@+node:ekr.20120625092120.12621: *3* trace
def trace (*args,**keys):

    # Compute the effective args.
    d = {'align':0,'newline':True}
    d = g.doKeywordArgs(keys,d)
    newline = d.get('newline')
    align = d.get('align',0)

    # Compute the caller name.
    try: # get the function name from the call stack.
        f1 = sys._getframe(1) # The stack frame, one level up.
        code1 = f1.f_code # The code object
        name = code1.co_name # The code name
    except Exception:
        name = '?'
    if name == "?":
        name = "<unknown>"

    # Pad the caller name.
    if align != 0 and len(name) < abs(align):
        pad = ' ' * (abs(align) - len(name))
        if align > 0: name = name + pad
        else:         name = pad + name

    # Munge *args into s.
    result = [name]
    for arg in args:
        if g.isString(arg):
            pass
        elif g.isBytes(arg):
            arg = g.toUnicode(arg)
        else:
            arg = repr(arg)
        if result:
            result.append(" " + arg)
        else:
            result.append(arg)
            
    s = ''.join(result)
    
    # Print the result immediately.
    g.pr(s,newline=newline)
#@+node:ekr.20120625092120.12622: *3* translateArgs
def translateArgs(args,d):

    '''Return the concatenation of s and all args,

    with odd args translated.'''

    if not hasattr(g,'consoleEncoding'):
        e = sys.getdefaultencoding()
        g.consoleEncoding = isValidEncoding(e) and e or 'utf-8'

    result = [] ; n = 0 ; spaces = d.get('spaces')
    for arg in args:
        n += 1
        # First, convert to unicode.
        if type(arg) == type('a'):
            arg = g.toUnicode(arg,g.consoleEncoding)

        # Now translate.
        if not g.isString(arg):
            arg = repr(arg)
        elif (n % 2) == 1:
            arg = g.translateString(arg)
        else:
            pass # The arg is an untranslated string.

        if arg:
            if result and spaces: result.append(' ')
            result.append(arg)

    return ''.join(result)
#@+node:ekr.20120625092120.12623: *3* translateString & tr
def translateString (s):

    '''Return the translated text of s.'''

    if g.isPython3 and not g.isString(s):
        s = str(s,'utf-8')
    
    return gettext.gettext(s)

tr = translateString
#@+node:ekr.20120625092120.12817: ** Printing
#@+node:ekr.20120625092120.12611: *3* doKeywordArgs
def doKeywordArgs (keys,d=None):

    '''Return a result dict that is a copy of the keys dict
    with missing items replaced by defaults in d dict.'''

    if d is None: d = {}

    result = {}
    for key,default_val in d.items():
        isBool = default_val in (True,False)
        val = keys.get(key)
        if isBool and val in (True,'True','true'):
            result[key] = True
        elif isBool and val in (False,'False','false'):
            result[key] = False
        elif val is None:
            result[key] = default_val
        else:
            result[key] = val

    return result 
#@+node:ekr.20120625092120.12516: *3* es_error & es_print_error
def es_error (*args,**keys):

    color = keys.get('color') or 'red'
    g.es(*args,**keys)
    
es_print_error = es_error
#@+node:ekr.20120625092120.12517: *3* es_event_exception
def es_event_exception (eventName,full=False):

    g.es("exception handling ",eventName,"event")
    typ,val,tb = sys.exc_info()

    if full:
        errList = traceback.format_exception(typ,val,tb)
    else:
        errList = traceback.format_exception_only(typ,val)

    for i in errList:
        g.es('',i)

    if not g.stdErrIsRedirected(): # 2/16/04
        traceback.print_exc()
#@+node:ekr.20120625092120.12518: *3* es_exception & es_print_exception
def es_exception (full=True):

    typ,val,tb = sys.exc_info()
         # val is the second argument to the raise statement.

    if full: # or g.app.debugSwitch > 0:
        lines = traceback.format_exception(typ,val,tb)
    else:
        lines = traceback.format_exception_only(typ,val)

    for line in lines:
        g.es_print_error(line,color=color)

    fileName,n = g.getLastTracebackFileAndLineNumber()

    return fileName,n
    
es_print_exception = es_exception
#@+node:ekr.20120625092120.12520: *3* es_exception_type
def es_exception_type():

    # exctype is a Exception class object; value is the error message.
    exctype, value = sys.exc_info()[:2]

    g.es_print('','%s, %s' % (exctype.__name__, value),color=color)
#@+node:ekr.20120625092120.12521: *3* getLastTracebackFileAndLineNumber
def getLastTracebackFileAndLineNumber():

    typ,val,tb = sys.exc_info()

    if typ == SyntaxError:
        # IndentationError is a subclass of SyntaxError.
        # Much easier in Python 2.6 and 3.x.
        return val.filename,val.lineno
    else:
        # Data is a list of tuples, one per stack entry.
        # Tupls have the form (filename,lineNumber,functionName,text).
        data = traceback.extract_tb(tb)
        if data:
            item = data[-1] # Get the item at the top of the stack.
            filename,n,functionName,text = item
            return filename,n
        else:
            # Should never happen.
            return '<string>',0
#@+node:ekr.20120625092120.12620: *3* pr & es and es_print
# see: http://www.diveintopython.org/xml_processing/unicode.html

pr_warning_given = False

def pr(*args,**keys):

    '''Print all non-keyword args.
    The first, third, fifth, etc. arg translated by g.translateString.
    Supports color, comma, newline, spaces and tabName keyword arguments.
    '''
    
    # print_immediately = True # Must always be true for stand-alone operation.

    # Compute the effective args.
    d = {'commas':False,'newline':True,'spaces':True}
    d = g.doKeywordArgs(keys,d)
    newline = d.get('newline')

    if sys.platform.lower().startswith('win'):
        encoding = 'ascii' # 2011/11/9.
    elif hasattr(sys.stdout,'encoding') and sys.stdout.encoding:
        # sys.stdout is a TextIOWrapper with a particular encoding.
        encoding = sys.stdout.encoding
    else:
        encoding = 'utf-8'

    s = g.translateArgs(args,d) # Translates everything to unicode.
    if newline:
        s = s + '\n'

    if g.isPython3:
        if encoding.lower() in ('utf-8','utf-16'):
            s2 = s # There can be no problem.
        else:
            # Carefully convert s to the encoding.
            s3 = g.toEncodedString(s,encoding=encoding,reportErrors=False)
            s2 = g.toUnicode(s3,encoding=encoding,reportErrors=False)
    else:
        s2 = g.toEncodedString(s,encoding,reportErrors=False)
        
    # Don't use print: we might not be writing a newline.
    sys.stdout.write(s2)
         
# Synonyms   
es = pr
es_print = pr
#@+node:ekr.20120625092120.12646: ** Scanning
#@+node:ekr.20120625092120.12836: *3* Character tests
#@+node:ekr.20120625092120.12666: *4* escaped
# Returns True if s[i] is preceded by an odd number of backslashes.

def escaped(s,i):

    count = 0
    while i-1 >= 0 and s[i-1] == '\\':
        count += 1
        i -= 1
    return (count%2) == 1
#@+node:ekr.20120625092120.12669: *4* is_c_id
def is_c_id(ch):

    return g.isWordChar(ch)

#@+node:ekr.20120625092120.12670: *4* is_nl
def is_nl(s,i):

    return i < len(s) and (s[i] == '\n' or s[i] == '\r')
#@+node:ekr.20120625092120.12671: *4* is_special
# We no longer require that the directive appear befor any @c directive or section definition.

def is_special(s,i,directive):

    '''Return True if the body text contains the @ directive.'''

    # j = g.skip_line(s,i) ; g.trace(s[i:j],':',directive)
    assert (directive and directive [0] == '@' )

    # 10/23/02: all directives except @others must start the line.
    skip_flag = directive in ("@others","@all")
    while i < len(s):
        if g.match_word(s,i,directive):
            return True, i
        else:
            i = g.skip_line(s,i)
            if skip_flag:
                i = g.skip_ws(s,i)
    return False, -1
#@+node:ekr.20120625092120.12672: *4* is_ws & is_ws_or_nl
def is_ws(ch):

    return ch == '\t' or ch == ' '

def is_ws_or_nl(s,i):

    return g.is_nl(s,i) or (i < len(s) and g.is_ws(s[i]))
#@+node:ekr.20120625092120.12704: *4* isWordChar & isWordChar1
def isWordChar (ch):

    '''Return True if ch should be considered a letter.'''

    return ch and (ch.isalnum() or ch == '_')

def isWordChar1 (ch):

    return ch and (ch.isalpha() or ch == '_')
#@+node:ekr.20120625092120.12665: *3* Find
#@+node:ekr.20120625092120.12667: *4* find_line_start
def find_line_start(s,i):

    if i < 0:
        return 0 # New in Leo 4.4.5: add this defensive code.

    # bug fix: 11/2/02: change i to i+1 in rfind
    i = s.rfind('\n',0,i+1) # Finds the highest index in the range.
    if i == -1: return 0
    else: return i + 1
#@+node:ekr.20120625092120.12668: *4* find_on_line
def find_on_line(s,i,pattern):

    j = s.find('\n',i)
    if j == -1: j = len(s)
    k = s.find(pattern,i,j)
    return k
#@+node:ekr.20120625092120.12832: *3* Match
#@+node:ekr.20120625092120.12673: *4* match
# Warning: this code makes no assumptions about what follows pattern.

def match(s,i,pattern):

    return s and pattern and s.find(pattern,i,i+len(pattern)) == i
#@+node:ekr.20120625092120.12674: *4* match_c_word
def match_c_word (s,i,name):

    if name == None: return False
    n = len(name)
    if n == 0: return False
    return name == s[i:i+n] and (i+n == len(s) or not g.is_c_id(s[i+n]))
#@+node:ekr.20120625092120.12675: *4* match_ignoring_case
def match_ignoring_case(s1,s2):

    if s1 == None or s2 == None: return False

    return s1.lower() == s2.lower()
#@+node:ekr.20120625092120.12676: *4* match_word
def match_word(s,i,pattern):

    if pattern == None: return False
    j = len(pattern)
    if j == 0: return False
    if s.find(pattern,i,i+j) != i:
        return False
    if i+j >= len(s):
        return True
    ch = s[i+j]
    return not g.isWordChar(ch)
#@+node:ekr.20120625092120.12833: *3* Skipping
#@+node:ekr.20120625092120.12677: *4* skip_blank_lines
# This routine differs from skip_ws_and_nl in that
# it does not advance over whitespace at the start
# of a non-empty or non-nl terminated line
def skip_blank_lines(s,i):

    while i < len(s):
        if g.is_nl(s,i) :
            i = g.skip_nl(s,i)
        elif g.is_ws(s[i]):
            j = g.skip_ws(s,i)
            if g.is_nl(s,j):
                i = j
            else: break
        else: break
    return i
#@+node:ekr.20120625092120.12678: *4* skip_c_id
def skip_c_id(s,i):

    n = len(s)
    while i < n and g.isWordChar(s[i]):
        i += 1
    return i
#@+node:ekr.20120625092120.12679: *4* skip_id
def skip_id(s,i,chars=None):

    chars = chars and g.toUnicode(chars) or ''
    n = len(s)
    while i < n and (g.isWordChar(s[i]) or s[i] in chars):
        i += 1
    return i
#@+node:ekr.20120625092120.12680: *4* skip_line, skip_to_start/end_of_line
#@+at These methods skip to the next newline, regardless of whether the
# newline may be preceeded by a backslash. Consequently, they should be
# used only when we know that we are not in a preprocessor directive or
# string.
#@@c

def skip_line (s,i):

    if i >= len(s): return len(s) # Bug fix: 2007/5/22
    if i < 0: i = 0
    i = s.find('\n',i)
    if i == -1: return len(s)
    else: return i + 1

def skip_to_end_of_line (s,i):

    if i >= len(s): return len(s) # Bug fix: 2007/5/22
    if i < 0: i = 0
    i = s.find('\n',i)
    if i == -1: return len(s)
    else: return i

def skip_to_start_of_line (s,i):

    if i >= len(s): return len(s)
    if i <= 0:      return 0
    i = s.rfind('\n',0,i) # Don't find s[i], so it doesn't matter if s[i] is a newline.
    if i == -1: return 0
    else:       return i + 1
#@+node:ekr.20120625092120.12681: *4* skip_long
def skip_long(s,i):

    '''Scan s[i:] for a valid int.
    Return (i, val) or (i, None) if s[i] does not point at a number.'''

    val = 0
    i = g.skip_ws(s,i)
    n = len(s)
    if i >= n or (not s[i].isdigit() and s[i] not in '+-'):
        return i, None
    j = i
    if s[i] in '+-': # Allow sign before the first digit
        i +=1
    while i < n and s[i].isdigit():
        i += 1
    try: # There may be no digits.
        val = int(s[j:i])
        return i, val
    except Exception:
        return i,None
#@+node:ekr.20120625092120.12682: *4* skip_matching_python_delims
def skip_matching_python_delims(s,i,delim1,delim2,reverse=False):

    '''Skip from the opening delim to the matching delim2.

    Return the index of the matching ')', or -1'''

    level = 0 ; n = len(s)
    # g.trace('delim1/2',repr(delim1),repr(delim2),'i',i,'s[i]',repr(s[i]),'s',repr(s[i-5:i+5]))
    assert(g.match(s,i,delim1))
    if reverse:
        while i >= 0:
            ch = s[i]
            if ch == delim1:
                level += 1 ; i -= 1
            elif ch == delim2:
                level -= 1
                if level <= 0:  return i
                i -= 1
            # Doesn't handle strings and comments properly...
            else: i -= 1
    else:
        while i < n:
            progress = i
            ch = s[i]
            if ch == delim1:
                level += 1 ; i += 1
            elif ch == delim2:
                level -= 1
                if level <= 0:  return i
                i += 1
            elif ch == '\'' or ch == '"': i = g.skip_string(s,i,verbose=False)
            elif g.match(s,i,'#'):  i = g.skip_to_end_of_line(s,i)
            else: i += 1
            if i == progress: return -1
    return -1
#@+node:ekr.20120625092120.12683: *4* skip_matching_c_delims
def skip_matching_c_delims(s,i,delim1,delim2,reverse=False):

    '''Skip from the opening delim to the matching delim2.

    Return the index of the matching ')', or -1'''

    level = 0
    assert(g.match(s,i,delim1))
    if reverse:
        # Reverse scanning is tricky.
        # This doesn't handle single-line comments properly.
        while i >= 0:
            progress = i
            ch = s[i]
            if ch == delim1:
                level += 1 ; i -= 1
            elif ch == delim2:
                level -= 1
                if level <= 0:  return i-1
                i -= 1
            elif ch in ('\'','"'):
                i -= 1
                while i >= 0:
                    if s[i] == ch and not s[i-1] == '\\':
                        i -= 1 ; break
                    else:
                        i -= 1
            elif g.match(s,i,'*/'):
                i += 2
                while i >= 0:
                    if g.match(s,i,'/*'):
                        i -= 2
                        break
                    else:
                        i -= 1
            else: i -= 1
            if i == progress:
                g.trace('oops: reverse')
                return -1
    else:
        while i < len(s):
            progress = i
            ch = s[i]
            # g.trace(i,repr(ch))
            if ch == delim1:
                level += 1 ; i += 1
            elif ch == delim2:
                level -= 1 ; i += 1
                if level <= 0:  return i
            elif ch in ('\'','"'):
                i += 1
                while i < len(s):
                    if s[i] == ch and not s[i-1] == '\\':
                        i += 1 ; break
                    else:
                        i += 1
            elif g.match(s,i,'//'):
                i = g.skip_to_end_of_line(s,i+2)
            elif g.match(s,i,'/*'):
                i += 2
                while i < len(s):
                    if g.match(s,i,'*/'):
                        i += 2
                        break
                    else:
                        i += 1
            else: i += 1
            if i == progress:
                g.trace('oops')
                return -1
    g.trace('not found')
    return -1
#@+node:ekr.20120625092120.12684: *4* skip_matching_python_parens
def skip_matching_python_parens(s,i):

    '''Skip from the opening ( to the matching ).

    Return the index of the matching ')', or -1'''

    return skip_matching_python_delims(s,i,'(',')')
#@+node:ekr.20120625092120.12685: *4* skip_nl
# We need this function because different systems have different end-of-line conventions.

def skip_nl (s,i):

    '''Skips a single "logical" end-of-line character.'''

    if g.match(s,i,"\r\n"): return i + 2
    elif g.match(s,i,'\n') or g.match(s,i,'\r'): return i + 1
    else: return i
#@+node:ekr.20120625092120.12687: *4* skip_pascal_braces
# Skips from the opening { to the matching }.

def skip_pascal_braces(s,i):

    # No constructs are recognized inside Pascal block comments!
    k = s.find('}',i)
    if i == -1: return len(s)
    else: return k
#@+node:ekr.20120625092120.12686: *4* skip_non_ws
def skip_non_ws (s,i):

    n = len(s)
    while i < n and not g.is_ws(s[i]):
        i += 1
    return i
#@+node:ekr.20120625092120.12688: *4* skip_to_char
def skip_to_char(s,i,ch):

    j = s.find(ch,i)
    if j == -1:
        return len(s),s[i:]
    else:
        return j,s[i:j]
#@+node:ekr.20120625092120.12689: *4* skip_ws, skip_ws_and_nl
def skip_ws(s,i):

    n = len(s)
    while i < n and g.is_ws(s[i]):
        i += 1
    return i

def skip_ws_and_nl(s,i):

    n = len(s)
    while i < n and (g.is_ws(s[i]) or g.is_nl(s,i)):
        i += 1
    return i
#@+node:ekr.20120625092120.12700: ** Unicode
#@+node:ekr.20120625092120.12701: *3* getPythonEncodingFromString
def getPythonEncodingFromString(s):

    '''Return the encoding given by Python's encoding line.
    s is the entire file.
    '''

    encoding = None
    tag,tag2 = '# -*- coding:','-*-'
    n1,n2 = len(tag),len(tag2)

    if s:
        # For Python 3.x we must convert to unicode before calling startswith.
        # The encoding doesn't matter: we only look at the first line, and if
        # the first line is an encoding line, it will contain only ascii characters.
        s = g.toUnicode(s,encoding='ascii',reportErrors=False)
        lines = g.splitLines(s)
        line1 = lines[0].strip()
        if line1.startswith(tag) and line1.endswith(tag2):
            e = line1[n1:-n2].strip()
            if e and g.isValidEncoding(e):
                encoding = e
        elif g.match_word(line1,0,'@first'): # 2011/10/21.
            line1 = line1[len('@first'):].strip()
            if line1.startswith(tag) and line1.endswith(tag2):
                e = line1[n1:-n2].strip()
                # g.trace(e,g.isValidEncoding(e),g.callers())
                if e and g.isValidEncoding(e):
                    encoding = e

    return encoding
#@+node:ekr.20120625092120.12702: *3* isBytes, isCallable, isChar, isString & isUnicode
# The syntax of these functions must be valid on Python2K and Python3K.

def isBytes(s):
    '''Return True if s is Python3k bytes type.'''
    if g.isPython3:
        # Generates a pylint warning, but that can't be helped.
        return type(s) == type(bytes('a','utf-8'))
    else:
        return False

def isCallable(obj):
    if g.isPython3:
        return hasattr(obj, '__call__')
    else:
        return callable(obj)

def isChar(s):
    '''Return True if s is a Python2K character type.'''
    if g.isPython3:
        return False
    else:
        return type(s) == types.StringType

def isString(s):
    '''Return True if s is any string, but not bytes.'''
    if g.isPython3:
        return type(s) == type('a')
    else:
        return type(s) in types.StringTypes

def isUnicode(s):
    '''Return True if s is a unicode string.'''
    if g.isPython3:
        return type(s) == type('a')
    else:
        return type(s) == types.UnicodeType
#@+node:ekr.20120625092120.12703: *3* isValidEncoding
def isValidEncoding (encoding):

    if not encoding:
        return False

    if sys.platform == 'cli':
        return True

    import codecs

    try:
        codecs.lookup(encoding)
        return True
    except LookupError: # Windows.
        return False
    except AttributeError: # Linux.
        return False
#@+node:ekr.20120625092120.12705: *3* reportBadChars
def reportBadChars (s,encoding):

    if g.isPython3:
        errors = 0
        if g.isUnicode(s):
            for ch in s:
                try: ch.encode(encoding,"strict")
                except UnicodeEncodeError:
                    errors += 1
            if errors:
                s2 = "%d errors converting %s to %s" % (
                    errors, s.encode(encoding,'replace'),
                    encoding.encode('ascii','replace'))
                # if not g.unitTesting:
                    # g.es(s2,color='red')
                g.es(s2)
        elif g.isChar(s):
            for ch in s:
                try: unicode(ch,encoding,"strict")
                except Exception: errors += 1
            if errors:
                s2 = "%d errors converting %s (%s encoding) to unicode" % (
                    errors, unicode(s,encoding,'replace'),
                    encoding.encode('ascii','replace'))
                # if not g.unitTesting:
                    # g.es(s2,color='red')
                g.es(s2)
    else:
        errors = 0
        if g.isUnicode(s):
            for ch in s:
                try: ch.encode(encoding,"strict")
                except UnicodeEncodeError:
                    errors += 1
            if errors:
                s2 = "%d errors converting %s to %s" % (
                    errors, s.encode(encoding,'replace'),
                    encoding.encode('ascii','replace'))
                # if not g.unitTesting:
                    # g.es(s2,color='red')
                g.es(s2)
        elif g.isChar(s):
            for ch in s:
                try: unicode(ch,encoding,"strict")
                except Exception: errors += 1
            if errors:
                s2 = "%d errors converting %s (%s encoding) to unicode" % (
                    errors, unicode(s,encoding,'replace'),
                    encoding.encode('ascii','replace'))
                # if not g.unitTesting:
                    # g.es(s2,color='red')
                g.es(s2)
#@+node:ekr.20120625092120.12706: *3* toEncodedString
def toEncodedString (s,encoding='utf-8',reportErrors=False):

    if encoding is None:
        encoding = 'utf-8'

    if g.isUnicode(s):
        try:
            s = s.encode(encoding,"strict")
        except UnicodeError:
            if reportErrors: g.reportBadChars(s,encoding)
            s = s.encode(encoding,"replace")
    return s
#@+node:ekr.20120625092120.12707: *3* toUnicode
def toUnicode (s,encoding='utf-8',reportErrors=False):

    # The encoding is usually 'utf-8'
    # but is may be different while importing or reading files.
    if encoding is None:
        encoding = 'utf-8'

    if isPython3:
        f,mustConvert = str,g.isBytes
    else:
        f = unicode
        def mustConvert (s):
            return type(s) != types.UnicodeType

    if not s:
        s = g.u('')
    elif mustConvert(s):
        try:
            s = f(s,encoding,'strict')
        # except (UnicodeError,UnicodeDecodeError,Exception):
        except Exception:
            try:
                s = f(s,encoding,'replace')
                if reportErrors: g.reportBadChars(s,encoding)
            except Exception:
                g.error('can not convert to unicode!',g.callers())
                s = ''
    else:
        pass

    return s
#@+node:ekr.20120625092120.12708: *3* u & ue
if isPython3: # g.not defined yet.
    def u(s):
        return s
    def ue(s,encoding):
        return str(s,encoding)
else:
    def u(s):
        return unicode(s)
    def ue(s,encoding):
        return unicode(s,encoding)
#@+node:ekr.20120625092120.12793: ** Whitespace
#@+node:ekr.20120625092120.12797: *3* adjustTripleString
def adjustTripleString (s,tab_width):

    '''Remove leading indentation from a triple-quoted string.

    This works around the fact that Leo nodes can't represent underindented strings.
    '''

    # Compute the minimum leading whitespace of all non-blank lines.
    lines = g.splitLines(s)
    w = 0 ; val = -1
    for line in lines:
        if line.strip():
            lws = g.get_leading_ws(line)
            w2 = g.computeWidth(lws,tab_width)
            # The sign of w does not matter.
            if w == 0 or abs(w2) < w:
                w = abs(w2)

    if w == 0: return s

    # Remove the leading whitespace.
    result = [g.removeLeadingWhitespace(line,w,tab_width) for line in lines]
    result = ''.join(result)
    return result
#@+node:ekr.20120625092120.12794: *3* computeLeadingWhitespace
# Returns optimized whitespace corresponding to width with the indicated tab_width.

def computeLeadingWhitespace (width, tab_width):

    if width <= 0:
        return ""
    if tab_width > 1:
        tabs   = int(width / tab_width)
        blanks = int(width % tab_width)
        return ('\t' * tabs) + (' ' * blanks)
    else: # 7/3/02: negative tab width always gets converted to blanks.
        return (' ' * width)
#@+node:ekr.20120625092120.12795: *3* computeLeadingWhitespaceWidth
# Returns optimized whitespace corresponding to width with the indicated tab_width.

def computeLeadingWhitespaceWidth (s,tab_width):

    w = 0
    for ch in s:
        if ch == ' ':
            w += 1
        elif ch == '\t':
            w += (abs(tab_width) - (w % abs(tab_width)))
        else:
            break
    return w
#@+node:ekr.20120625092120.12796: *3* computeWidth
# Returns the width of s, assuming s starts a line, with indicated tab_width.

def computeWidth (s, tab_width):

    w = 0
    for ch in s:
        if ch == '\t':
            w += (abs(tab_width) - (w % abs(tab_width)))
        elif ch == '\n': # Bug fix: 2012/06/05.
            break
        else:
            w += 1
    return w
#@+node:ekr.20120625092120.12802: *3* get_leading_ws
def get_leading_ws(s):

    """Returns the leading whitespace of 's'."""

    i = 0 ; n = len(s)
    while i < n and s[i] in (' ','\t'):
        i += 1
    return s[0:i]
#@+node:ekr.20120625092120.12803: *3* optimizeLeadingWhitespace
# Optimize leading whitespace in s with the given tab_width.

def optimizeLeadingWhitespace (line,tab_width):

    i, width = g.skip_leading_ws_with_indent(line,0,tab_width)
    s = g.computeLeadingWhitespace(width,tab_width) + line[i:]
    return s
#@+node:ekr.20120625092120.12804: *3* regularizeTrailingNewlines
#@+at The caller should call g.stripBlankLines before calling this routine
# if desired.
# 
# This routine does _not_ simply call rstrip(): that would delete all
# trailing whitespace-only lines, and in some cases that would change
# the meaning of program or data.
#@@c

def regularizeTrailingNewlines(s,kind):

    """Kind is 'asis', 'zero' or 'one'."""

    pass
#@+node:ekr.20120625092120.12805: *3* removeBlankLines
def removeBlankLines (s):

    lines = g.splitLines(s)
    lines = [z for z in lines if z.strip()]
    return ''.join(lines)
#@+node:ekr.20120625092120.12798: *3* removeExtraLws
def removeExtraLws (s,tab_width):

    '''Remove extra indentation from one or more lines.

    Warning: used by getScript.  This is *not* the same as g.adjustTripleString.'''

    lines = g.splitLines(s)

    # Find the first non-blank line and compute w, the width of its leading whitespace.
    for line in lines:
        if line.strip():
            lws = g.get_leading_ws(line)
            w = g.computeWidth(lws,tab_width)
            break
    else: return s

    # Remove the leading whitespace.
    result = [g.removeLeadingWhitespace(line,w,tab_width) for line in lines]
    result = ''.join(result)

    if 0:
        g.trace('lines...')
        for line in g.splitLines(result):
            g.pr(repr(line))

    return result
#@+node:ekr.20120625092120.12806: *3* removeLeadingBlankLines
def removeLeadingBlankLines (s):

    lines = g.splitLines(s)

    result = [] ; remove = True
    for line in lines:
        if remove and not line.strip():
            pass
        else:
            remove = False
            result.append(line)

    return ''.join(result)
#@+node:ekr.20120625092120.12807: *3* removeLeadingWhitespace
# Remove whitespace up to first_ws wide in s, given tab_width, the width of a tab.

def removeLeadingWhitespace (s,first_ws,tab_width):

    j = 0 ; ws = 0 ; first_ws = abs(first_ws)
    for ch in s:
        if ws >= first_ws:
            break
        elif ch == ' ':
            j += 1 ; ws += 1
        elif ch == '\t':
            j += 1 ; ws += (abs(tab_width) - (ws % abs(tab_width)))
        else: break
    if j > 0:
        s = s[j:]
    return s
#@+node:ekr.20120625092120.12808: *3* removeTrailingWs
# Warning: string.rstrip also removes newlines!

def removeTrailingWs(s):

    j = len(s)-1
    while j >= 0 and (s[j] == ' ' or s[j] == '\t'):
        j -= 1
    return s[:j+1]
#@+node:ekr.20120625092120.12809: *3* skip_leading_ws
# Skips leading up to width leading whitespace.

def skip_leading_ws(s,i,ws,tab_width):

    count = 0
    while count < ws and i < len(s):
        ch = s[i]
        if ch == ' ':
            count += 1
            i += 1
        elif ch == '\t':
            count += (abs(tab_width) - (count % abs(tab_width)))
            i += 1
        else: break

    return i
#@+node:ekr.20120625092120.12810: *3* skip_leading_ws_with_indent
def skip_leading_ws_with_indent(s,i,tab_width):

    """Skips leading whitespace and returns (i, indent), 

    - i points after the whitespace
    - indent is the width of the whitespace, assuming tab_width wide tabs."""

    count = 0 ; n = len(s)
    while i < n:
        ch = s[i]
        if ch == ' ':
            count += 1
            i += 1
        elif ch == '\t':
            count += (abs(tab_width) - (count % abs(tab_width)))
            i += 1
        else: break

    return i, count
#@+node:ekr.20120625092120.12811: *3* stripBlankLines
def stripBlankLines(s):

    lines = g.splitLines(s)

    for i in range(len(lines)):

        line = lines[i]
        j = g.skip_ws(line,0)
        if j >= len(line):
            lines[i] = ''
            # g.trace("%4d %s" % (i,repr(lines[i])))
        elif line[j] == '\n':
            lines[i] = '\n'
            # g.trace("%4d %s" % (i,repr(lines[i])))

    return ''.join(lines)
#@+node:ekr.20120625092120.12625: ** Wrappers for os.path
#@+at Note: all these methods return Unicode strings. It is up to the user to
# convert to an encoded string as needed, say when opening a file.
#@+node:ekr.20120625092120.12626: *3* os_path_abspath
def os_path_abspath(path):

    """Convert a path to an absolute path."""

    path = g.toUnicodeFileEncoding(path)

    path = os.path.abspath(path)

    path = g.toUnicodeFileEncoding(path)

    return path
#@+node:ekr.20120625092120.12627: *3* os_path_basename
def os_path_basename(path):

    """Return the second half of the pair returned by split(path)."""

    path = g.toUnicodeFileEncoding(path)

    path = os.path.basename(path)

    path = g.toUnicodeFileEncoding(path)

    return path
#@+node:ekr.20120625092120.12628: *3* os_path_dirname
def os_path_dirname(path):

    """Return the first half of the pair returned by split(path)."""

    path = g.toUnicodeFileEncoding(path)

    path = os.path.dirname(path)

    path = g.toUnicodeFileEncoding(path)

    return path
#@+node:ekr.20120625092120.12629: *3* os_path_exists
def os_path_exists(path):

    """Return True if path exists."""

    path = g.toUnicodeFileEncoding(path)

    return os.path.exists(path)
#@+node:ekr.20120625092120.12631: *3* os_path_expanduser
def os_path_expanduser(path):

    """wrap os.path.expanduser"""

    path = g.toUnicodeFileEncoding(path)

    result = os.path.normpath(os.path.expanduser(path))

    return result
#@+node:ekr.20120625092120.12632: *3* os_path_finalize & os_path_finalize_join
def os_path_finalize (path,**keys):

    '''
    Expand '~', then return os.path.normpath, os.path.abspath of the path.

    There is no corresponding os.path method'''

    # c = keys.get('c')
    # if c: path = g.os_path_expandExpression(path,**keys)

    path = g.os_path_expanduser(path)
    path = os.path.abspath(path)
    path = os.path.normpath(path)
    return path

def os_path_finalize_join (*args,**keys):

    '''Do os.path.join(*args), then finalize the result.'''

    # c = keys.get('c')
    # if c:
        # args = [g.os_path_expandExpression(z,**keys)
            # for z in args if z]

    return os.path.normpath(os.path.abspath(
        g.os_path_join(*args,**keys))) # Handles expanduser
#@+node:ekr.20120625092120.12633: *3* os_path_getmtime
def os_path_getmtime(path):

    """Return the modification time of path."""

    path = g.toUnicodeFileEncoding(path)

    return os.path.getmtime(path)
#@+node:ekr.20120625092120.12634: *3* os_path_getsize
def os_path_getsize (path):

    '''Return the size of path.'''

    path = g.toUnicodeFileEncoding(path)

    return os.path.getsize(path)
#@+node:ekr.20120625092120.12635: *3* os_path_isabs
def os_path_isabs(path):

    """Return True if path is an absolute path."""

    path = g.toUnicodeFileEncoding(path)

    return os.path.isabs(path)
#@+node:ekr.20120625092120.12636: *3* os_path_isdir
def os_path_isdir(path):

    """Return True if the path is a directory."""

    path = g.toUnicodeFileEncoding(path)

    return os.path.isdir(path)
#@+node:ekr.20120625092120.12637: *3* os_path_isfile
def os_path_isfile(path):

    """Return True if path is a file."""

    path = g.toUnicodeFileEncoding(path)

    return os.path.isfile(path)
#@+node:ekr.20120625092120.12638: *3* os_path_join
def os_path_join(*args,**keys):

    trace = False
    # c = keys.get('c')

    uargs = [g.toUnicodeFileEncoding(arg) for arg in args]

    if trace: g.trace('1',uargs)

    # Note:  This is exactly the same convention as used by getBaseDirectory.
    # if uargs and uargs[0] == '!!':
        # uargs[0] = g.app.loadDir
    # elif uargs and uargs[0] == '.':
        # c = keys.get('c')
        # if c and c.openDirectory:
            # uargs[0] = c.openDirectory
            # # g.trace(c.openDirectory)

    uargs = [g.os_path_expanduser(z) for z in uargs if z]

    if trace: g.trace('2',uargs)

    path = os.path.join(*uargs)

    if trace: g.trace('3',path)

    # May not be needed on some Pythons.
    path = g.toUnicodeFileEncoding(path)
    return path
#@+node:ekr.20120625092120.12639: *3* os_path_normcase
def os_path_normcase(path):

    """Normalize the path's case."""

    path = g.toUnicodeFileEncoding(path)

    path = os.path.normcase(path)

    path = g.toUnicodeFileEncoding(path)

    return path
#@+node:ekr.20120625092120.12640: *3* os_path_normpath
def os_path_normpath(path):

    """Normalize the path."""

    path = g.toUnicodeFileEncoding(path)

    path = os.path.normpath(path)

    path = g.toUnicodeFileEncoding(path)

    return path
#@+node:ekr.20120625092120.12641: *3* os_path_realpath
def os_path_realpath(path):


    path = g.toUnicodeFileEncoding(path)

    path = os.path.realpath(path)

    path = g.toUnicodeFileEncoding(path)

    return path
#@+node:ekr.20120625092120.12642: *3* os_path_split
def os_path_split(path):

    path = g.toUnicodeFileEncoding(path)

    head,tail = os.path.split(path)

    head = g.toUnicodeFileEncoding(head)
    tail = g.toUnicodeFileEncoding(tail)

    return head,tail
#@+node:ekr.20120625092120.12643: *3* os_path_splitext
def os_path_splitext(path):

    path = g.toUnicodeFileEncoding(path)

    head,tail = os.path.splitext(path)

    head = g.toUnicodeFileEncoding(head)
    tail = g.toUnicodeFileEncoding(tail)

    return head,tail
#@+node:ekr.20120625092120.12644: *3* os_startfile
def os_startfile(fname):
    
    # if g.unitTesting:
        # g.app.unitTestDict['os_startfile']=fname
        # return
        
    if fname.find('"') > -1:
        quoted_fname = "'%s'" % fname
    else:
        quoted_fname = '"%s"' % fname

    if sys.platform.startswith('win'):
        os.startfile(quoted_fname)
            # Exists only on Windows.
    elif sys.platform == 'darwin':
        # From Marc-Antoine Parent.
        try:
            subprocess.call(['open', quoted_fname])
        except OSError:
            pass # There may be a spurious "Interrupted system call"
        except ImportError:
            os.system('open %s' % (quoted_fname))
    else:
        # os.system('xdg-open "%s"' % (fname))
        try:
            val = subprocess.call('xdg-open %s' % (quoted_fname),shell=True)
            if val < 0:
                g.es_print('xdg-open %s failed' % (fname))
        except Exception:
            g.es_print('error opening %s' % fname)
            g.es_exception()
#@+node:ekr.20120625092120.12645: *3* toUnicodeFileEncoding
def toUnicodeFileEncoding(path):

    if path: path = path.replace('\\', os.sep)

    # Yes, this is correct.  All os_path_x functions return Unicode strings.
    return g.toUnicode(path)
#@-others

import leoStandAloneGlobals as g # So code in this module can use g
#@-leo
