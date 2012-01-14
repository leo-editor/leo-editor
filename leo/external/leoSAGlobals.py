# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20120114064730.10309: * @file ../external/leoSAGlobals.py
#@@first

"""leoSAGlobals.py: the stand-alone version of leo.core.leoGlobals.py"""

#@@language python
#@@tabwidth -4
#@@pagewidth 70

import sys
isPython3 = sys.version_info >= (3,0,0)

#@+<< imports >>
#@+node:ekr.20120114064730.10310: ** << imports >>
import PyQt4.QtCore as QtCore

try:
    import gettext
except ImportError: # does not exist in jython.
    gettext = None

# Do NOT import pdb here!  We shall define pdb as a _function_ below.
# import pdb

if isPython3:
    import io
    StringIO = io.StringIO
else:
    import cStringIO
    StringIO = cStringIO.StringIO

import inspect
import operator
import re
import shutil
import subprocess
# import sys # Done earlier.
import time
import zipfile

# These do not exist in IronPython.
# However, it *is* valid for IronPython to use the Python 2.4 libs!
import os
import string
import tempfile
import traceback
import types
#@-<< imports >>
#@+<< class nullObject >>
#@+node:ekr.20120114064730.10312: ** << class nullObject >>
# From the Python cookbook, recipe 5.23

class nullObject:

    """An object that does nothing, and does it very well."""

    def __init__   (self,*args,**keys): pass
    def __call__   (self,*args,**keys): return self
    # def __len__    (self): return 0 # Debatable.
    def __repr__   (self): return "nullObject"
    def __str__    (self): return "nullObject"
    if isPython3:
        def __bool__(self): return False
    else:
        def __nonzero__(self): return 0
    def __delattr__(self,attr):     return self
    def __getattr__(self,attr):     return self
    def __setattr__(self,attr,val): return self
#@-<< class nullObject >>
    
#@+others
#@+node:ekr.20120114064730.10355: ** SAG.Debugging
#@+node:ekr.20120114064730.10357: *3* callers & _callerName
def callers (n=4,count=0,excludeCaller=True,files=False):

    '''Return a list containing the callers of the function that called callerList.

    If the excludeCaller keyword is True (the default), callers is not on the list.

    If the files keyword argument is True, filenames are included in the list.
    '''

    # sys._getframe throws ValueError in both cpython and jython if there are less than i entries.
    # The jython stack often has less than 8 entries,
    # so we must be careful to call _callerName with smaller values of i first.
    result = []
    i = choose(excludeCaller,3,2)
    i += 1 ### Not sure why this is needed.
    while 1:
        s = _callerName(i,files=files)
        if s:
            result.append(s)
        if not s or len(result) >= n: break
        i += 1

    result.reverse()
    if count > 0: result = result[:count]
    sep = choose(files,'\n',',')
    return sep.join(result)
#@+node:ekr.20120114064730.10358: *4* _callerName
def _callerName (n=1,files=False):

    try: # get the function name from the call stack.
        f1 = sys._getframe(n) # The stack frame, n levels up.
        code1 = f1.f_code # The code object
        name = code1.co_name
        if name == '__init__':
            name = '__init__(%s,line %s)' % (
                shortFileName(code1.co_filename),code1.co_firstlineno)
        if files:
            return '%s:%s' % (shortFilename(code1.co_filename),name)
        else:
            return name # The code name
    except ValueError:
        return '' # The stack is not deep enough.
    except Exception:
        es_exception()
        return '' # "<no caller name>"
#@+node:ekr.20120114064730.10365: *3* es_exception
def es_exception (full=True,c=None,color="red"):

    typ,val,tb = sys.exc_info()

    # val is the second argument to the raise statement.

    if full: ###  or g.app.debugSwitch > 0:
        lines = traceback.format_exception(typ,val,tb)
    else:
        lines = traceback.format_exception_only(typ,val)

    for line in lines:
        es_error(line,color=color)

    if False: ### g.app.debugSwitch > 1:
        import pdb # Be careful: g.pdb may or may not have been defined.
        pdb.set_trace()

    fileName,n = getLastTracebackFileAndLineNumber()

    return fileName,n
#@+node:ekr.20120114064730.10367: *3* es_exception_type
def es_exception_type (c=None,color="red"):

    # exctype is a Exception class object; value is the error message.
    exctype, value = sys.exc_info()[:2]

    es('','%s, %s' % (exctype.__name__, value),color=color)
#@+node:ekr.20120114064730.10366: *3* es_print_exception
def es_print_exception (full=True,c=None,color="red"):

    typ,val,tb = sys.exc_info()

    # val is the second argument to the raise statement.

    if full: ### or g.app.debugSwitch > 0:
        lines = traceback.format_exception(typ,val,tb)
    else:
        lines = traceback.format_exception_only(typ,val)

    for line in lines:
        print(line)

    fileName,n = getLastTracebackFileAndLineNumber()

    return fileName,n
#@+node:ekr.20120114064730.10390: *3* get_line & get_line__after
# Very useful for tracing.

def get_line (s,i):

    nl = ""
    if is_nl(s,i):
        i = skip_nl(s,i)
        nl = "[nl]"
    j = find_line_start(s,i)
    k = skip_to_end_of_line(s,i)
    return nl + s[j:k]

# Important: getLine is a completely different function.
# getLine = get_line

def get_line_after (s,i):

    nl = ""
    if is_nl(s,i):
        i = skip_nl(s,i)
        nl = "[nl]"
    k = skip_to_end_of_line(s,i)
    return nl + s[i:k]

getLineAfter = get_line_after
#@+node:ekr.20120114064730.10368: *3* getLastTracebackFileAndLineNumber
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
#@+node:ekr.20120114064730.10391: *3* pause
def pause (s):

    pr(s)

    i = 0 ; n = long(1000) * long(1000)
    while i < n:
        i += 1
#@+node:ekr.20120114064730.10359: *3* pdb (changed)
def pdb (message=''):

    """Fall into pdb."""

    import pdb # Required: we have just defined pdb as a function!

    if message:
        print(message)
        
    QtCore.pyqtRemoveInputHook() # In Leo, done in qtPdb.
    pdb.set_trace()
#@+node:ekr.20120114064730.10393: *3* print_dict & dictToString
def print_dict(d,tag='',verbose=True,indent=''):

    if not d:
        if tag: pr('%s...{}' % tag)
        else:   pr('{}')
        return

    n = 6
    for key in sorted(d):
        if type(key) == type(''):
            n = max(n,len(key))
    if tag: es('%s...{\n' % tag)
    else:   es('{\n')
    for key in sorted(d):
        pr("%s%*s: %s" % (indent,n,key,repr(d.get(key)).strip()))
    pr('}')

printDict = print_dict

def dictToString(d,tag=None,verbose=True,indent=''):

    if not d:
        if tag: return '%s...{}' % tag
        else:   return '{}'
    n = 6
    for key in sorted(d):
        if isString(key):
            n = max(n,len(key))
    lines = ["%s%*s: %s" % (indent,n,key,repr(d.get(key)).strip())
        for key in sorted(d)]
    s = '\n'.join(lines)
    if tag:
        return '%s...{\n%s}\n' % (tag,s)
    else:
        return '{\n%s}\n' % s
#@+node:ekr.20120114064730.10394: *3* print_list & listToString
def print_list(aList,tag=None,sort=False,indent=''):

    if not aList:
        if tag: pr('%s...[]' % tag)
        else:   pr('[]')
        return
    if sort:
        bList = aList[:] # Sort a copy!
        bList.sort()
    else:
        bList = aList
    if tag: pr('%s...[' % tag)
    else:   pr('[')
    for e in bList:
        pr('%s%s' % (indent,repr(e).strip()))
    pr(']')

printList = print_list

def listToString(aList,tag=None,sort=False,indent='',toRepr=False):

    if not aList:
        if tag: return '%s...{}' % tag
        else:   return '[]'
    if sort:
        bList = aList[:] # Sort a copy!
        bList.sort()
    else:
        bList = aList
    lines = ["%s%s" % (indent,repr(e).strip()) for e in bList]
    s = '\n'.join(lines)
    if toRepr: s = repr(s)
    if tag:
        return '[%s...\n%s\n]' % (tag,s)
    else:
        return '[%s]' % s
#@+node:ekr.20120114064730.10392: *3* print_obj & toString
def print_obj (obj,tag=None,sort=False,verbose=True,indent=''):

    if type(obj) in (type(()),type([])):
        print_list(obj,tag,sort,indent)
    elif type(obj) == type({}):
        print_dict(obj,tag,verbose,indent)
    else:
        pr('%s%s' % (indent,repr(obj).strip()))

def toString (obj,tag=None,sort=False,verbose=True,indent=''):

    if type(obj) in (type(()),type([])):
        return listToString(obj,tag,sort,indent)
    elif type(obj) == type({}):
        return dictToString(obj,tag,verbose,indent)
    else:
        return '%s%s' % (indent,repr(obj).strip())
#@+node:ekr.20120114064730.10395: *3* print_stack (printStack)
def print_stack():

    traceback.print_stack()

printStack = print_stack
#@+node:ekr.20120114064730.10472: ** SAG.Most common functions...
# These are guaranteed always to exist for scripts.
#@+node:ekr.20120114064730.10473: *3* choose
def choose(cond, a, b): # warning: evaluates all arguments

    if cond: return a
    else: return b
#@+node:ekr.20120114064730.10474: *3* doKeywordArgs
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
#@+node:ekr.20120114064730.10476: *3* error, note & warning
def error (*args,**keys):
    es_print('Error:',color='red',*args,**keys)

def note (*args,**keys):
    es_print(*args,**keys)

def warning (*args,**keys):
    es_print('Warning:',color='blue',*args,**keys)
#@+node:ekr.20120114064730.10479: *3* es_trace
def es_trace(*args,**keys):

    if args:
        try:
            s = args[0]
            trace(toEncodedString(s,'ascii'))
        except Exception:
            pass

    es(*args,**keys)
#@+node:ekr.20120114064730.10483: *3* pr & es & es_print
# see: http://www.diveintopython.org/xml_processing/unicode.html

pr_warning_given = False

def pr(*args,**keys):

    '''Print all non-keyword args, and put them to the log pane.
    The first, third, fifth, etc. arg translated by translateString.
    Supports color, comma, newline, spaces and tabName keyword arguments.
    '''

    # Compute the effective args.
    d = {'commas':False,'newline':True,'spaces':True}
    d = doKeywordArgs(keys,d)
    newline = d.get('newline')
    nl = choose(newline,'\n','')

    if sys.platform.lower().startswith('win'):
        encoding = 'ascii' # 2011/11/9.
    elif hasattr(sys.stdout,'encoding') and sys.stdout.encoding:
        # sys.stdout is a TextIOWrapper with a particular encoding.
        encoding = sys.stdout.encoding
    else:
        encoding = 'utf-8'

    s = translateArgs(args,d) # Translates everything to unicode.
    if True: ### app.logInited:
        s = s + '\n'

    if isPython3:
        if encoding.lower() in ('utf-8','utf-16'):
            s2 = s # There can be no problem.
        else:
            # Carefully convert s to the encoding.
            s3 = toEncodedString(s,encoding=encoding,reportErrors=False)
            s2 = toUnicode(s3,encoding=encoding,reportErrors=False)
    else:
        s2 = toEncodedString(s,encoding,reportErrors=False)

    # Print s2 *without* an additional trailing newline.
    sys.stdout.write(s2)
        
# Synonyms:
es = pr
es_print = pr
es_error = pr
es_print_error = pr
#@+node:ekr.20120114064730.10442: *3* shortFileName & shortFilename
def shortFileName (fileName):

    return os_path_basename(fileName)

shortFilename = shortFileName
#@+node:ekr.20120114064730.10484: *3* trace
# Convert all args to strings.

def trace (*args,**keys):

    # Compute the effective args.
    d = {'align':0,'newline':True}
    d = doKeywordArgs(keys,d)
    newline = d.get('newline',None)
    align = d.get('align',0)
    # if not align: align = 0

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
    # print ('trace:args...')
    # for z in args: print (isString(z),repr(z))
    result = [name]
    for arg in args:
        if isString(arg):
            pass
        elif isBytes(arg):
            arg = toUnicode(arg)
        else:
            arg = repr(arg)
        if result:
            result.append(" " + arg)
        else:
            result.append(arg)
    s = ''.join(result)

    # 'print s,' is not valid syntax in Python 3.x.
    pr(s,newline=newline)
#@+node:ekr.20120114064730.10485: *3* translateArgs
def translateArgs(args,d):

    '''Return the concatenation of s and all args,

    with odd args translated.'''

    if True: ### not hasattr(g,'consoleEncoding'):
        e = sys.getdefaultencoding()
        consoleEncoding = isValidEncoding(e) and e or 'utf-8'

    result = [] ; n = 0 ; spaces = d.get('spaces')
    for arg in args:
        n += 1

        # print('translateArgs: arg',arg,type(arg),isString(arg),'will trans',(n%2)==1)

        # First, convert to unicode.
        if type(arg) == type('a'):
            arg = toUnicode(arg,consoleEncoding)

        # Now translate.
        if not isString(arg):
            arg = repr(arg)
        elif (n % 2) == 1:
            arg = translateString(arg)
        else:
            pass # The arg is an untranslated string.

        if arg:
            if result and spaces: result.append(' ')
            result.append(arg)

    return ''.join(result)
#@+node:ekr.20120114064730.10486: *3* translateString & tr
def translateString (s):

    '''Return the translated text of s.'''

    if isPython3:
        if not isString(s):
            s = str(s,'utf-8')
        if False: ### g.app.translateToUpperCase:
            s = s.upper()
        else:
            s = gettext.gettext(s)
        return s
    else:
        if False: ### g.app.translateToUpperCase:
            return s.upper()
        else:
            return gettext.gettext(s)

tr = translateString
#@+node:ekr.20120114064730.10488: ** SAG.os.path wrappers
#@+at Note: all these methods return Unicode strings. It is up to the user to
# convert to an encoded string as needed, say when opening a file.
#@+node:ekr.20120114064730.10489: *3* os_path_abspath
def os_path_abspath(path):

    """Convert a path to an absolute path."""

    path = toUnicodeFileEncoding(path)

    path = os.path.abspath(path)

    path = toUnicodeFileEncoding(path)

    return path
#@+node:ekr.20120114064730.10490: *3* os_path_basename
def os_path_basename(path):

    """Return the second half of the pair returned by split(path)."""

    path = toUnicodeFileEncoding(path)

    path = os.path.basename(path)

    path = toUnicodeFileEncoding(path)

    return path
#@+node:ekr.20120114064730.10491: *3* os_path_dirname
def os_path_dirname(path):

    """Return the first half of the pair returned by split(path)."""

    path = toUnicodeFileEncoding(path)

    path = os.path.dirname(path)

    path = toUnicodeFileEncoding(path)

    return path
#@+node:ekr.20120114064730.10492: *3* os_path_exists
def os_path_exists(path):

    """Return True if path exists."""

    path = toUnicodeFileEncoding(path)

    return os.path.exists(path)
#@+node:ekr.20120114064730.10493: *3* os_path_expandExpression
def os_path_expandExpression (s,**keys):

    '''Expand {{anExpression}} in c's context.'''

    trace = False
    
    s1 = s
    c = keys.get('c')
    if not c:
        trace('can not happen: no c',callers())
        return s

    if not s:
        if trace: trace('no s')
        return ''

    i = s.find('{{')
    j = s.find('}}')
    if -1 < i < j:
        exp = s[i+2:j].strip()
        if exp:
            try:
                import os
                import sys
                p = c.p
                d = {
                    ### 'c':c,'g':g,'p':p,
                    'os':os,'sys':sys,}
                val = eval(exp,d)
                s = s[:i] + str(val) + s[j+2:]
                if trace: trace(s1,s)
            except Exception:
                trace(callers())
                es_exception(full=True, c=c, color='red')

    return s
#@+node:ekr.20120114064730.10494: *3* os_path_expanduser
def os_path_expanduser(path):

    """wrap os.path.expanduser"""

    path = toUnicodeFileEncoding(path)

    result = os.path.normpath(os.path.expanduser(path))

    return result
#@+node:ekr.20120114064730.10495: *3* os_path_finalize & os_path_finalize_join
def os_path_finalize (path,**keys):

    '''
    Expand '~', then return os.path.normpath, os.path.abspath of the path.

    There is no corresponding os.path method'''

    c = keys.get('c')

    if c: path = os_path_expandExpression(path,**keys)

    path = os_path_expanduser(path)
    path = os.path.abspath(path)
    path = os.path.normpath(path)
    return path

def os_path_finalize_join (*args,**keys):

    '''Do os.path.join(*args), then finalize the result.'''

    c = keys.get('c')

    if c:
        args = [os_path_expandExpression(z,**keys)
            for z in args if z]

    return os.path.normpath(os.path.abspath(
        os_path_join(*args,**keys))) # Handles expanduser
#@+node:ekr.20120114064730.10496: *3* os_path_getmtime
def os_path_getmtime(path):

    """Return the modification time of path."""

    path = toUnicodeFileEncoding(path)

    return os.path.getmtime(path)
#@+node:ekr.20120114064730.10497: *3* os_path_getsize
def os_path_getsize (path):

    '''Return the size of path.'''

    path = toUnicodeFileEncoding(path)

    return os.path.getsize(path)
#@+node:ekr.20120114064730.10498: *3* os_path_isabs
def os_path_isabs(path):

    """Return True if path is an absolute path."""

    path = toUnicodeFileEncoding(path)

    return os.path.isabs(path)
#@+node:ekr.20120114064730.10499: *3* os_path_isdir
def os_path_isdir(path):

    """Return True if the path is a directory."""

    path = toUnicodeFileEncoding(path)

    return os.path.isdir(path)
#@+node:ekr.20120114064730.10500: *3* os_path_isfile
def os_path_isfile(path):

    """Return True if path is a file."""

    path = toUnicodeFileEncoding(path)

    return os.path.isfile(path)
#@+node:ekr.20120114064730.10501: *3* os_path_join
def os_path_join(*args,**keys):

    trace = False
    ### c = keys.get('c')

    uargs = [toUnicodeFileEncoding(arg) for arg in args]

    if trace: trace('1',uargs)

    ### Note:  This is exactly the same convention as used by getBaseDirectory.
    # if uargs and uargs[0] == '!!':
        # uargs[0] = app.loadDir
    # elif uargs and uargs[0] == '.':
        # c = keys.get('c')
        # if c and c.openDirectory:
            # uargs[0] = c.openDirectory
            # # trace(c.openDirectory)

    uargs = [os_path_expanduser(z) for z in uargs if z]

    if trace: trace('2',uargs)

    path = os.path.join(*uargs)

    if trace: trace('3',path)

    # May not be needed on some Pythons.
    path = toUnicodeFileEncoding(path)
    return path
#@+node:ekr.20120114064730.10502: *3* os_path_normcase
def os_path_normcase(path):

    """Normalize the path's case."""

    path = toUnicodeFileEncoding(path)

    path = os.path.normcase(path)

    path = toUnicodeFileEncoding(path)

    return path
#@+node:ekr.20120114064730.10503: *3* os_path_normpath
def os_path_normpath(path):

    """Normalize the path."""

    path = toUnicodeFileEncoding(path)

    path = os.path.normpath(path)

    path = toUnicodeFileEncoding(path)

    return path
#@+node:ekr.20120114064730.10504: *3* os_path_realpath
def os_path_realpath(path):


    path = toUnicodeFileEncoding(path)

    path = os.path.realpath(path)

    path = toUnicodeFileEncoding(path)

    return path
#@+node:ekr.20120114064730.10505: *3* os_path_split
def os_path_split(path):

    path = toUnicodeFileEncoding(path)

    head,tail = os.path.split(path)

    head = toUnicodeFileEncoding(head)
    tail = toUnicodeFileEncoding(tail)

    return head,tail
#@+node:ekr.20120114064730.10506: *3* os_path_splitext
def os_path_splitext(path):

    path = toUnicodeFileEncoding(path)

    head,tail = os.path.splitext(path)

    head = toUnicodeFileEncoding(head)
    tail = toUnicodeFileEncoding(tail)

    return head,tail
#@+node:ekr.20120114064730.10507: *3* os_startfile
def os_startfile(fname):
    if sys.platform.startswith('win'):
        os.startfile(fname)
    elif sys.platform == 'darwin':
        # From Marc-Antoine Parent.
        try:
            subprocess.call(['open', fname])
        except OSError:
            pass # There may be a spurious "Interrupted system call"
        except ImportError:
            os.system("open '%s'" % (fname,))
    else:
        os.system('xdg-open "%s"'%fname)
#@+node:ekr.20120114064730.10508: *3* toUnicodeFileEncoding
def toUnicodeFileEncoding(path):

    if path: path = path.replace('\\', os.sep)

    # Yes, this is correct.  All os_path_x functions return Unicode strings.
    return toUnicode(path)
#@+node:ekr.20120114064730.10509: ** SAG.Scanning
#@+node:ekr.20120114064730.10529: *3* escaped
# Returns True if s[i] is preceded by an odd number of backslashes.

def escaped(s,i):

    count = 0
    while i-1 >= 0 and s[i-1] == '\\':
        count += 1
        i -= 1
    return (count%2) == 1
#@+node:ekr.20120114064730.10530: *3* find_line_start
def find_line_start(s,i):

    if i < 0:
        return 0 # New in Leo 4.4.5: add this defensive code.

    # bug fix: 11/2/02: change i to i+1 in rfind
    i = s.rfind('\n',0,i+1) # Finds the highest index in the range.
    if i == -1: return 0
    else: return i + 1
#@+node:ekr.20120114064730.10531: *3* find_on_line
def find_on_line(s,i,pattern):

    j = s.find('\n',i)
    if j == -1: j = len(s)
    k = s.find(pattern,i,j)
    return k
#@+node:ekr.20120114064730.10532: *3* is_c_id
def is_c_id(ch):

    return isWordChar(ch)

#@+node:ekr.20120114064730.10533: *3* is_nl
def is_nl(s,i):

    return i < len(s) and (s[i] == '\n' or s[i] == '\r')
#@+node:ekr.20120114064730.10534: *3* is_special
# We no longer require that the directive appear befor any @c directive or section definition.

def is_special(s,i,directive):

    '''Return True if the body text contains the @ directive.'''

    # j = skip_line(s,i) ; trace(s[i:j],':',directive)
    assert (directive and directive [0] == '@' )

    # 10/23/02: all directives except @others must start the line.
    skip_flag = directive in ("@others","@all")
    while i < len(s):
        if match_word(s,i,directive):
            return True, i
        else:
            i = skip_line(s,i)
            if skip_flag:
                i = skip_ws(s,i)
    return False, -1
#@+node:ekr.20120114064730.10535: *3* is_ws & is_ws_or_nl
def is_ws(c):

    return c == '\t' or c == ' '

def is_ws_or_nl(s,i):

    return is_nl(s,i) or (i < len(s) and is_ws(s[i]))
#@+node:ekr.20120114064730.10536: *3* match
# Warning: this code makes no assumptions about what follows pattern.

def match(s,i,pattern):

    return s and pattern and s.find(pattern,i,i+len(pattern)) == i
#@+node:ekr.20120114064730.10537: *3* match_c_word
def match_c_word (s,i,name):

    if name == None: return False
    n = len(name)
    if n == 0: return False
    return name == s[i:i+n] and (i+n == len(s) or not is_c_id(s[i+n]))
#@+node:ekr.20120114064730.10538: *3* match_ignoring_case
def match_ignoring_case(s1,s2):

    if s1 == None or s2 == None: return False

    return s1.lower() == s2.lower()
#@+node:ekr.20120114064730.10539: *3* match_word
def match_word(s,i,pattern):

    if pattern == None: return False
    j = len(pattern)
    if j == 0: return False
    if s.find(pattern,i,i+j) != i:
        return False
    if i+j >= len(s):
        return True
    ch = s[i+j]
    return not isWordChar(ch)
#@+node:ekr.20120114064730.10511: *3* scanf
# A quick and dirty sscanf.  Understands only %s and %d.

def scanf (s,pat):
    count = pat.count("%s") + pat.count("%d")
    pat = pat.replace("%s","(\S+)")
    pat = pat.replace("%d","(\d+)")
    parts = re.split(pat,s)
    result = []
    for part in parts:
        if len(part) > 0 and len(result) < count:
            result.append(part)
    # trace("scanf returns:",result)
    return result

if 0: # testing
    scanf("1.0","%d.%d",)
#@+node:ekr.20120114064730.10540: *3* skip_blank_lines
# This routine differs from skip_ws_and_nl in that
# it does not advance over whitespace at the start
# of a non-empty or non-nl terminated line
def skip_blank_lines(s,i):

    while i < len(s):
        if is_nl(s,i) :
            i = skip_nl(s,i)
        elif is_ws(s[i]):
            j = skip_ws(s,i)
            if is_nl(s,j):
                i = j
            else: break
        else: break
    return i
#@+node:ekr.20120114064730.10541: *3* skip_c_id
def skip_c_id(s,i):

    n = len(s)
    while i < n and isWordChar(s[i]):
        i += 1
    return i
#@+node:ekr.20120114064730.10542: *3* skip_id
def skip_id(s,i,chars=None):

    chars = chars and toUnicode(chars) or ''
    n = len(s)
    while i < n and (isWordChar(s[i]) or s[i] in chars):
        i += 1
    return i
#@+node:ekr.20120114064730.10543: *3* skip_line, skip_to_start/end_of_line
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
#@+node:ekr.20120114064730.10544: *3* skip_long
def skip_long(s,i):

    '''Scan s[i:] for a valid int.
    Return (i, val) or (i, None) if s[i] does not point at a number.'''

    val = 0
    i = skip_ws(s,i)
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
#@+node:ekr.20120114064730.10546: *3* skip_matching_c_delims
def skip_matching_c_delims(s,i,delim1,delim2,reverse=False):

    '''Skip from the opening delim to the matching delim2.

    Return the index of the matching ')', or -1'''

    level = 0
    assert(match(s,i,delim1))
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
            elif match(s,i,'*/'):
                i += 2
                while i >= 0:
                    if match(s,i,'/*'):
                        i -= 2
                        break
                    else:
                        i -= 1
            else: i -= 1
            if i == progress:
                trace('oops: reverse')
                return -1
    else:
        while i < len(s):
            progress = i
            ch = s[i]
            # trace(i,repr(ch))
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
            elif match(s,i,'//'):
                i = skip_to_end_of_line(s,i+2)
            elif match(s,i,'/*'):
                i += 2
                while i < len(s):
                    if match(s,i,'*/'):
                        i += 2
                        break
                    else:
                        i += 1
            else: i += 1
            if i == progress:
                trace('oops')
                return -1
    trace('not found')
    return -1
#@+node:ekr.20120114064730.10545: *3* skip_matching_python_delims
def skip_matching_python_delims(s,i,delim1,delim2,reverse=False):

    '''Skip from the opening delim to the matching delim2.

    Return the index of the matching ')', or -1'''

    level = 0 ; n = len(s)
    # trace('delim1/2',repr(delim1),repr(delim2),'i',i,'s[i]',repr(s[i]),'s',repr(s[i-5:i+5]))
    assert(match(s,i,delim1))
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
            elif ch == '\'' or ch == '"': i = skip_string(s,i,verbose=False)
            elif match(s,i,'#'):  i = skip_to_end_of_line(s,i)
            else: i += 1
            if i == progress: return -1
    return -1
#@+node:ekr.20120114064730.10547: *3* skip_matching_python_parens
def skip_matching_python_parens(s,i):

    '''Skip from the opening ( to the matching ).

    Return the index of the matching ')', or -1'''

    return skip_matching_python_delims(s,i,'(',')')
#@+node:ekr.20120114064730.10548: *3* skip_nl
# We need this function because different systems have different end-of-line conventions.

def skip_nl (s,i):

    '''Skips a single "logical" end-of-line character.'''

    if match(s,i,"\r\n"): return i + 2
    elif match(s,i,'\n') or match(s,i,'\r'): return i + 1
    else: return i
#@+node:ekr.20120114064730.10549: *3* skip_non_ws
def skip_non_ws (s,i):

    n = len(s)
    while i < n and not is_ws(s[i]):
        i += 1
    return i
#@+node:ekr.20120114064730.10550: *3* skip_pascal_braces
# Skips from the opening { to the matching }.

def skip_pascal_braces(s,i):

    # No constructs are recognized inside Pascal block comments!
    k = s.find('}',i)
    if i == -1: return len(s)
    else: return k
#@+node:ekr.20120114064730.10551: *3* skip_to_char
def skip_to_char(s,i,ch):

    j = s.find(ch,i)
    if j == -1:
        return len(s),s[i:]
    else:
        return j,s[i:j]
#@+node:ekr.20120114064730.10552: *3* skip_ws, skip_ws_and_nl
def skip_ws(s,i):

    n = len(s)
    while i < n and is_ws(s[i]):
        i += 1
    return i

def skip_ws_and_nl(s,i):

    n = len(s)
    while i < n and (is_ws(s[i]) or is_nl(s,i)):
        i += 1
    return i
#@+node:ekr.20120114064730.10553: *3* splitLines & joinLines
def splitLines (s):

    '''Split s into lines, preserving the number of lines and
    the endings of all lines, including the last line.'''

    # stat()

    if s:
        return s.splitlines(True) # This is a Python string function!
    else:
        return []

splitlines = splitLines

def joinLines (aList):

    return ''.join(aList)

joinlines = joinLines
#@+node:ekr.20120114064730.10564: ** SAG.Unicode utils...
#@+node:ekr.20120114064730.10565: *3* getPythonEncodingFromString
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
        s = toUnicode(s,encoding='ascii',reportErrors=False)
        lines = splitLines(s)
        line1 = lines[0].strip()
        if line1.startswith(tag) and line1.endswith(tag2):
            e = line1[n1:-n2].strip()
            if e and isValidEncoding(e):
                encoding = e
        elif match_word(line1,0,'@first'): # 2011/10/21.
            line1 = line1[len('@first'):].strip()
            if line1.startswith(tag) and line1.endswith(tag2):
                e = line1[n1:-n2].strip()
                # trace(e,isValidEncoding(e),callers())
                if e and isValidEncoding(e):
                    encoding = e

    return encoding
#@+node:ekr.20120114064730.10566: *3* isBytes, isCallable, isChar, isString & isUnicode
# The syntax of these functions must be valid on Python2K and Python3K.

def isBytes(s):
    '''Return True if s is Python3k bytes type.'''
    if isPython3:
        # Generates a pylint warning, but that can't be helped.
        return type(s) == type(bytes('a','utf-8'))
    else:
        return False

def isCallable(obj):
    if isPython3:
        return hasattr(obj, '__call__')
    else:
        return callable(obj)

def isChar(s):
    '''Return True if s is a Python2K character type.'''
    if isPython3:
        return False
    else:
        return type(s) == types.StringType

def isString(s):
    '''Return True if s is any string, but not bytes.'''
    if isPython3:
        return type(s) == type('a')
    else:
        return type(s) in types.StringTypes

def isUnicode(s):
    '''Return True if s is a unicode string.'''
    if isPython3:
        return type(s) == type('a')
    else:
        return type(s) == types.UnicodeType
#@+node:ekr.20120114064730.10567: *3* isValidEncoding
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
#@+node:ekr.20120114064730.10568: *3* isWordChar & isWordChar1
def isWordChar (ch):

    '''Return True if ch should be considered a letter.'''

    return ch and (ch.isalnum() or ch == '_')

def isWordChar1 (ch):

    return ch and (ch.isalpha() or ch == '_')
#@+node:ekr.20120114064730.10569: *3* reportBadChars
def reportBadChars (s,encoding):

    if isPython3:
        errors = 0
        if isUnicode(s):
            for ch in s:
                try: ch.encode(encoding,"strict")
                except UnicodeEncodeError:
                    errors += 1
            if errors:
                s2 = "%d errors converting %s to %s" % (
                    errors, s.encode(encoding,'replace'),
                    encoding.encode('ascii','replace'))
                if not unitTesting:
                    es(s2,color='red')
        elif isChar(s):
            for ch in s:
                try: unicode(ch,encoding,"strict")
                except Exception: errors += 1
            if errors:
                s2 = "%d errors converting %s (%s encoding) to unicode" % (
                    errors, unicode(s,encoding,'replace'),
                    encoding.encode('ascii','replace'))
                if not unitTesting:
                    es(s2,color='red')
    else:
        errors = 0
        if isUnicode(s):
            for ch in s:
                try: ch.encode(encoding,"strict")
                except UnicodeEncodeError:
                    errors += 1
            if errors:
                s2 = "%d errors converting %s to %s" % (
                    errors, s.encode(encoding,'replace'),
                    encoding.encode('ascii','replace'))
                if not unitTesting:
                    es(s2,color='red')
        elif isChar(s):
            for ch in s:
                try: unicode(ch,encoding,"strict")
                except Exception: errors += 1
            if errors:
                s2 = "%d errors converting %s (%s encoding) to unicode" % (
                    errors, unicode(s,encoding,'replace'),
                    encoding.encode('ascii','replace'))
                if not unitTesting:
                    es(s2,color='red')
#@+node:ekr.20120114064730.10570: *3* toEncodedString
def toEncodedString (s,encoding='utf-8',reportErrors=False):

    if encoding is None:
        encoding = 'utf-8'

    if isUnicode(s):
        try:
            s = s.encode(encoding,"strict")
        except UnicodeError:
            if reportErrors: reportBadChars(s,encoding)
            s = s.encode(encoding,"replace")
    return s
#@+node:ekr.20120114064730.10571: *3* toUnicode
def toUnicode (s,encoding='utf-8',reportErrors=False):

    # The encoding is usually 'utf-8'
    # but is may be different while importing or reading files.
    if encoding is None:
        encoding = 'utf-8'

    if isPython3:
        f,mustConvert = str,isBytes
    else:
        f = unicode
        def mustConvert (s):
            return type(s) != types.UnicodeType

    if not s:
        s = u('')
    elif mustConvert(s):
        try:
            s = f(s,encoding,'strict')
        # except (UnicodeError,UnicodeDecodeError,Exception):
        except Exception:
            try:
                s = f(s,encoding,'replace')
                if reportErrors: reportBadChars(s,encoding)
            except Exception:
                error('can not convert to unicode!')
                s = ''
    else:
        pass

    return s
#@+node:ekr.20120114064730.10572: *3* u & ue
if isPython3: # not defined yet.
    def u(s):
        return s
    def ue(s,encoding):
        return str(s,encoding)
else:
    def u(s):
        return unicode(s)
    def ue(s,encoding):
        return unicode(s,encoding)
#@+node:ekr.20120114064730.10574: *3* toUnicodeWithErrorCode (for unit testing)
def toUnicodeWithErrorCode (s,encoding,reportErrors=False):

    ok = True
    if isPython3: f = str
    else: f = unicode
    if s is None:
        s = u('')
    if not isUnicode(s):
        try:
            s = f(s,encoding,'strict')
        except Exception:
            if reportErrors:
                reportBadChars(s,encoding)
            s = f(s,encoding,'replace')
            ok = False
    return s,ok
#@+node:ekr.20120114064730.10578: ** SAG.Utility...
#@+node:ekr.20120114064730.10579: *3*  Index utilities... (leoGlobals)
#@+node:ekr.20120114064730.10580: *4* convertPythonIndexToRowCol
def convertPythonIndexToRowCol (s,i):

    '''Convert index i into string s into zero-based row/col indices.'''

    if not s or i <= 0:
        return 0,0

    i = min(i,len(s))

    # works regardless of what s[i] is
    row = s.count('\n',0,i) # Don't include i
    if row == 0:
        return row,i
    else:
        prevNL = s.rfind('\n',0,i) # Don't include i
        # trace('prevNL',prevNL,'i',i,callers())
        return row,i-prevNL-1
#@+node:ekr.20120114064730.10581: *4* convertRowColToPythonIndex
def convertRowColToPythonIndex (s,row,col,lines=None):

    '''Convert zero-based row/col indices into a python index into string s.'''

    if row < 0: return 0

    if lines is None:
        lines = splitLines(s)

    if row >= len(lines):
        return len(s)

    col = min(col, len(lines[row]))

    # A big bottleneck
    prev = 0
    for line in lines[:row]:
        prev += len(line)

    return prev + col
#@+node:ekr.20120114064730.10582: *3*  List utilities...
#@+node:ekr.20120114064730.10583: *4* appendToList
def appendToList(out, s):

    for i in s:
        out.append(i)
#@+node:ekr.20120114064730.10584: *4* flattenList
def flattenList (theList):

    result = []
    for item in theList:
        if type(item) == types.ListType:
            result.extend(flattenList(item))
        else:
            result.append(item)
    return result
#@+node:ekr.20120114064730.10585: *4* maxStringListLength
def maxStringListLength(aList):

    '''Return the maximum string length in a list of strings.'''

    n = 0
    for z in aList:
        if isString():
            n = max(n,len(z))

    return n
#@+node:ekr.20120114064730.10586: *3* angleBrackets & virtual_event_name
# Returns < < s > >

def angleBrackets(s):

    return ( "<<" + s +
        ">>") # must be on a separate line.

virtual_event_name = angleBrackets
#@+node:ekr.20120114064730.10587: *3* CheckVersion
#@+node:ekr.20120114064730.10588: *4* CheckVersion, helper
# Simplified version by EKR: stringCompare not used.

def CheckVersion (s1,s2,condition=">=",stringCompare=None,delimiter='.',trace=False):

    # CheckVersion is called early in the startup process.

    vals1 = [CheckVersionToInt(s) for s in s1.split(delimiter)] ; n1 = len(vals1)
    vals2 = [CheckVersionToInt(s) for s in s2.split(delimiter)] ; n2 = len(vals2)
    n = max(n1,n2)
    if n1 < n: vals1.extend([0 for i in range(n - n1)])
    if n2 < n: vals2.extend([0 for i in range(n - n2)])
    for cond,val in (
        ('==', vals1 == vals2), ('!=', vals1 != vals2),
        ('<',  vals1 <  vals2), ('<=', vals1 <= vals2),
        ('>',  vals1 >  vals2), ('>=', vals1 >= vals2),
    ):
        if condition == cond:
            result = val ; break
    else:
        raise EnvironmentError("condition must be one of '>=', '>', '==', '!=', '<', or '<='.")

    if trace:
        # pr('%10s' % (repr(vals1)),'%2s' % (condition),'%10s' % (repr(vals2)),result)
        pr('%7s' % (s1),'%2s' % (condition),'%7s' % (s2),result)
    return result
#@+node:ekr.20120114064730.10589: *5* CheckVersionToInt
def CheckVersionToInt (s):

    try:
        return int(s)
    except ValueError:
        aList = []
        for ch in s:
            if ch.isdigit(): aList.append(ch)
            else: break
        if aList:
            s = ''.join(aList)
            return int(s)
        else:
            return 0
#@+node:ekr.20120114064730.10590: *4* oldCheckVersion (Dave Hein)
#@+at CheckVersion() is a generic version checker.  Assumes a
# version string of up to four parts, or tokens, with
# leftmost token being most significant and each token
# becoming less signficant in sequence to the right.
# 
# RETURN VALUE
# 
# 1 if comparison is True
# 0 if comparison is False
# 
# PARAMETERS
# 
# version: the version string to be tested
# againstVersion: the reference version string to be
#               compared against
# condition: can be any of "==", "!=", ">=", "<=", ">", or "<"
# stringCompare: whether to test a token using only the
#              leading integer of the token, or using the
#              entire token string.  For example, a value
#              of "0.0.1.0" means that we use the integer
#              value of the first, second, and fourth
#              tokens, but we use a string compare for the
#              third version token.
# delimiter: the character that separates the tokens in the
#          version strings.
# 
# The comparison uses the precision of the version string
# with the least number of tokens.  For example a test of
# "8.4" against "8.3.3" would just compare the first two
# tokens.
# 
# The version strings are limited to a maximum of 4 tokens.
#@@c

def oldCheckVersion( version, againstVersion, condition=">=", stringCompare="0.0.0.0", delimiter='.' ):

    # tokenize the stringCompare flags
    compareFlag = stringCompare.split('.')

    # tokenize the version strings
    testVersion = version.split(delimiter)
    testAgainst = againstVersion.split(delimiter)

    # find the 'precision' of the comparison
    tokenCount = 4
    if tokenCount > len(testAgainst):
        tokenCount = len(testAgainst)
    if tokenCount > len(testVersion):
        tokenCount = len(testVersion)

    # Apply the stringCompare flags
    justInteger = re.compile("^[0-9]+")
    for i in range(tokenCount):
        if "0" == compareFlag[i]:
            m = justInteger.match( testVersion[i] )
            testVersion[i] = m.group()
            m = justInteger.match( testAgainst[i] )
            testAgainst[i] = m.group()
        elif "1" != compareFlag[i]:
            errMsg = "stringCompare argument must be of " +\
                 "the form \"x.x.x.x\" where each " +\
                 "'x' is either '0' or '1'."
            raise EnvironmentError(errMsg)

    # Compare the versions
    if condition == ">=":
        for i in range(tokenCount):
            if testVersion[i] < testAgainst[i]:
                return 0
            if testVersion[i] > testAgainst[i]:
                return 1 # it was greater than
        return 1 # it was equal
    if condition == ">":
        for i in range(tokenCount):
            if testVersion[i] < testAgainst[i]:
                return 0
            if testVersion[i] > testAgainst[i]:
                return 1 # it was greater than
        return 0 # it was equal
    if condition == "==":
        for i in range(tokenCount):
            if testVersion[i] != testAgainst[i]:
                return 0 # any token was not equal
        return 1 # every token was equal
    if condition == "!=":
        for i in range(tokenCount):
            if testVersion[i] != testAgainst[i]:
                return 1 # any token was not equal
        return 0 # every token was equal
    if condition == "<":
        for i in range(tokenCount):
            if testVersion[i] >= testAgainst[i]:
                return 0
            if testVersion[i] < testAgainst[i]:
                return 1 # it was less than
        return 0 # it was equal
    if condition == "<=":
        for i in range(tokenCount):
            if testVersion[i] > testAgainst[i]:
                return 0
            if testVersion[i] < testAgainst[i]:
                return 1 # it was less than
        return 1 # it was equal

    # didn't find a condition that we expected.
    raise EnvironmentError("condition must be one of '>=', '>', '==', '!=', '<', or '<='.")
#@+node:ekr.20120114064730.10591: *3* class Bunch (object)
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
#@+node:ekr.20120114064730.10592: *3* class nullObject
# From the Python cookbook, recipe 5.23

# This is now defined at the start of this file.
#@+node:ekr.20120114064730.10594: *3* cls
def cls():
    
    '''Clear the screen.'''
    
    import os
    import sys
    
    if sys.platform.lower().startswith('win'):
        os.system('cls')
#@+node:ekr.20120114064730.10595: *3* computeWindowTitle
def computeWindowTitle (fileName):

    if fileName == None:
        return "untitled"
    else:
        path,fn = os_path_split(fileName)
        if path:
            title = fn + " in " + path
        else:
            title = fn
        return title
#@+node:ekr.20120114064730.10596: *3* ensureLeading/TrailingNewlines
def ensureLeadingNewlines (s,n):

    s = removeLeading(s,'\t\n\r ')
    return ('\n' * n) + s

def ensureTrailingNewlines (s,n):

    s = removeTrailing(s,'\t\n\r ')
    return s + '\n' * n


#@+node:ekr.20120114064730.10598: *3* fileLikeObject
# Note: we could use StringIo for this.

class fileLikeObject:

    """Define a file-like object for redirecting writes to a string.

    The caller is responsible for handling newlines correctly."""

    #@+others
    #@+node:ekr.20120114064730.10599: *4*  ctor
    def __init__(self,encoding='utf-8',fromString=None):

        # trace('fileLikeObject:__init__','fromString',fromString)

        # New in 4.2.1: allow the file to be inited from string s.

        self.encoding = encoding or 'utf-8'

        if fromString:
            self.list = splitLines(fromString) # Must preserve newlines!
        else:
            self.list = []

        self.ptr = 0

    # In CStringIO the buffer is read-only if the initial value (fromString) is non-empty.
    #@+node:ekr.20120114064730.10600: *4* clear
    def clear (self):

        self.list = []
    #@+node:ekr.20120114064730.10601: *4* close
    def close (self):

        pass

        # The StringIo version free's the memory buffer.
    #@+node:ekr.20120114064730.10602: *4* flush
    def flush (self):

        pass
    #@+node:ekr.20120114064730.10603: *4* get & getvalue & read
    def get (self):

        return ''.join(self.list)

    getvalue = get # for compatibility with StringIo
    read = get # for use by sax.
    #@+node:ekr.20120114064730.10604: *4* readline
    def readline(self): # New for read-from-string (readOpenFile).

        if self.ptr < len(self.list):
            line = self.list[self.ptr]
            # trace(repr(line))
            self.ptr += 1
            return line
        else:
            return ''
    #@+node:ekr.20120114064730.10605: *4* write
    def write (self,s):

        if s:
            if isBytes(s):
                s = toUnicode(s,self.encoding)

            self.list.append(s)
    #@-others
#@+node:ekr.20120114064730.10606: *3* funcToMethod
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
    # trace(name)
#@+node:ekr.20120114064730.10607: *3* getDocString
def getDocString(s):
    
    '''Return the text of the first docstring found in s.'''

    tags = ('"""',"'''")
    tag1,tag2 = tags
    i1,i2 = s.find(tag1),s.find(tag2)

    if i1 == -1 and i2 == -1:
        return ''
    if i1 > -1 and i2 > -1:
        i = min(i1,i2)
    else:
        i = max(i1,i2)
    tag = s[i:i+3]
    assert tag in tags

    j = s.find(tag,i+3)
    if j > -1:
        return s[i+3:j]
    else:
        return ''

#@+node:ekr.20120114064730.10608: *3* getDocStringForFunction
def getDocStringForFunction (func):
    
    '''Return the docstring for a function that creates a Leo command.'''
    
    def name(func):
        return hasattr(func,'__name__') and func.__name__ or ''
        
    def get_defaults(func,i):
        args, varargs, keywords, defaults = inspect.getargspec(func)
        return defaults[i]
    
    if name(func) == 'minibufferCallback':
        func = get_defaults(func,0)
        if name(func) == 'commonCommandCallback':
            script = get_defaults(func,1)
            s = getDocString(script)
        elif hasattr(func,'docstring'): # atButtonCallback object.
            s = func.docstring()
        elif hasattr(func,'__doc__'):
            s = func.__doc__ or ''
        else:
            print('**oops',func)
            s = ''
    else:
        s = func.__doc__ or ''
        
    return s
#@+node:ekr.20120114064730.10609: *3* getWord & getLine
def getWord (s,i):

    '''Return i,j such that s[i:j] is the word surrounding s[i].'''

    if i >= len(s): i = len(s) - 1
    if i < 0: i = 0
    # Scan backwards.
    while 0 <= i < len(s) and isWordChar(s[i]):
        i-= 1
    i += 1
    # Scan forwards.
    j = i
    while 0 <= j < len(s) and isWordChar(s[j]):
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
    # trace('i,j,k',i,j,k,repr(s[j:k]))
    return j,k
#@+node:ekr.20120114064730.10610: *3* isMacOS
def isMacOS():
    
    return sys.platform == 'darwin'
#@+node:ekr.20120114064730.10612: *3* makeDict
# From the Python cookbook.

def makeDict(**keys):

    """Returns a Python dictionary from using the optional keyword arguments."""

    return keys
#@+node:ekr.20120114064730.10613: *3* prettyPrintType
def prettyPrintType (obj):

    if isPython3:
        if type(obj) in (types.MethodType,types.BuiltinMethodType):
            return 'method'
        elif type(obj) in (types.BuiltinFunctionType,types.FunctionType):
            return 'function'
        elif type(obj) == types.ModuleType:
            return 'module'
        elif isString(obj):
            return 'string'
        else:
            theType = str(type(obj))
            if theType.startswith("<type '"): theType = theType[7:]
            if theType.endswith("'>"): theType = theType[:-2]
            return theType
    else:
        if type(obj) in (
            types.MethodType,types.UnboundMethodType,types.BuiltinMethodType):
            return 'method'
        elif type(obj) in (types.BuiltinFunctionType,types.FunctionType):
            return 'function'
        elif type(obj) == types.ModuleType:
            return 'module'
        elif type(obj) == types.InstanceType:
            return 'object'
        elif type(obj) in (types.UnicodeType,types.StringType):
            return 'string'
        else:
            theType = str(type(obj))
            if theType.startswith("<type '"): theType = theType[7:]
            if theType.endswith("'>"): theType = theType[:-2]
            return theType
#@+node:ekr.20120114064730.10614: *3* removeLeading/Trailing
# Warning: removeTrailingWs already exists.
# Do not change it!

def removeLeading (s,chars):

    '''Remove all characters in chars from the front of s.'''

    i = 0
    while i < len(s) and s[i] in chars:
        i += 1
    return s[i:]

def removeTrailing (s,chars):

    '''Remove all characters in chars from the end of s.'''

    i = len(s)-1
    while i >= 0 and s[i] in chars:
        i -= 1
    i += 1
    return s[:i]
#@+node:ekr.20120114064730.10615: *3* stripBrackets
def stripBrackets (s):

    '''Same as s.lstrip('<').rstrip('>') except it works for Python 2.2.1.'''

    if s.startswith('<'):
        s = s[1:]
    if s.endswith('>'):
        s = s[:-1]
    return s
#@+node:ekr.20120114064730.10616: *3* toPythonIndex
def toPythonIndex (s,index):
    
    '''Convert index to a Python int.
    
    index may be a Tk index (x.y) or 'end'.
    '''
    
    if index is None:
        return 0
    elif type(index) == type(99):
        return index
    elif index == '1.0':
        return 0
    elif index == 'end':
        return len(s)
    else:
        data = index.split('.')
        if len(data) == 2:
            row,col = data
            row,col = int(row),int(col)
            i = convertRowColToPythonIndex(s,row-1,col)
            return i
        else:
            trace('bad string index: %s' % index)
            return 0

toGuiIndex = toPythonIndex
#@+node:ekr.20120114064730.10625: ** SAG.Whitespace...
#@+node:ekr.20120114064730.10626: *3* computeLeadingWhitespace
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
#@+node:ekr.20120114064730.10627: *3* computeWidth
# Returns the width of s, assuming s starts a line, with indicated tab_width.

def computeWidth (s, tab_width):

    w = 0
    for ch in s:
        if ch == '\t':
            w += (abs(tab_width) - (w % abs(tab_width)))
        else:
            w += 1
    return w
#@+node:ekr.20120114064730.10628: *3* adjustTripleString
def adjustTripleString (s,tab_width):

    '''Remove leading indentation from a triple-quoted string.

    This works around the fact that Leo nodes can't represent underindented strings.
    '''

    # Compute the minimum leading whitespace of all non-blank lines.
    lines = splitLines(s)
    w = 0 ; val = -1
    for line in lines:
        if line.strip():
            lws = get_leading_ws(line)
            w2 = computeWidth(lws,tab_width)
            # The sign of w does not matter.
            if w == 0 or abs(w2) < w:
                w = abs(w2)

    if w == 0: return s

    # Remove the leading whitespace.
    result = [removeLeadingWhitespace(line,w,tab_width) for line in lines]
    result = ''.join(result)
    return result
#@+node:ekr.20120114064730.10629: *3* removeExtraLws
def removeExtraLws (s,tab_width):

    '''Remove extra indentation from one or more lines.

    Warning: used by getScript.  This is *not* the same as adjustTripleString.'''

    lines = splitLines(s)

    # Find the first non-blank line and compute w, the width of its leading whitespace.
    for line in lines:
        if line.strip():
            lws = get_leading_ws(line)
            w = computeWidth(lws,tab_width)
            break
    else: return s

    # Remove the leading whitespace.
    result = [removeLeadingWhitespace(line,w,tab_width) for line in lines]
    result = ''.join(result)

    if 0:
        trace('lines...')
        for line in splitLines(result):
            pr(repr(line))

    return result
#@+node:ekr.20120114064730.10633: *3* get_leading_ws
def get_leading_ws(s):

    """Returns the leading whitespace of 's'."""

    i = 0 ; n = len(s)
    while i < n and s[i] in (' ','\t'):
        i += 1
    return s[0:i]
#@+node:ekr.20120114064730.10634: *3* optimizeLeadingWhitespace
# Optimize leading whitespace in s with the given tab_width.

def optimizeLeadingWhitespace (line,tab_width):

    i, width = skip_leading_ws_with_indent(line,0,tab_width)
    s = computeLeadingWhitespace(width,tab_width) + line[i:]
    return s
#@+node:ekr.20120114064730.10636: *3* removeBlankLines
def removeBlankLines (s):

    lines = splitLines(s)
    lines = [z for z in lines if z.strip()]
    return ''.join(lines)
#@+node:ekr.20120114064730.10637: *3* removeLeadingBlankLines
def removeLeadingBlankLines (s):

    lines = splitLines(s)

    result = [] ; remove = True
    for line in lines:
        if remove and not line.strip():
            pass
        else:
            remove = False
            result.append(line)

    return ''.join(result)
#@+node:ekr.20120114064730.10638: *3* removeLeadingWhitespace
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
#@+node:ekr.20120114064730.10639: *3* removeTrailingWs
# Warning: string.rstrip also removes newlines!

def removeTrailingWs(s):

    j = len(s)-1
    while j >= 0 and (s[j] == ' ' or s[j] == '\t'):
        j -= 1
    return s[:j+1]
#@+node:ekr.20120114064730.10640: *3* skip_leading_ws
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
#@+node:ekr.20120114064730.10641: *3* skip_leading_ws_with_indent
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
#@+node:ekr.20120114064730.10642: *3* stripBlankLines
def stripBlankLines(s):

    lines = splitLines(s)

    for i in range(len(lines)):

        line = lines[i]
        j = skip_ws(line,0)
        if j >= len(line):
            lines[i] = ''
            # trace("%4d %s" % (i,repr(lines[i])))
        elif line[j] == '\n':
            lines[i] = '\n'
            # trace("%4d %s" % (i,repr(lines[i])))

    return ''.join(lines)
#@-others

#@-leo
