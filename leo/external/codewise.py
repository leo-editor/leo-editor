#!/usr/bin/env python
#@+leo-ver=5-thin
#@+node:ekr.20110310091639.14254: * @file ../external/codewise.py
#@@first
#@+<< docstring >>
#@+node:ekr.20110310091639.14291: ** << docstring >>
r""" CodeWise - global code intelligence database

Why this module
===============

- Exuberant ctags is an excellent code scanner
- Unfortunately, TAGS file lookup sucks for "find methods of this class"
- TAGS files can be all around the hard drive. CodeWise database is
  just one file (by default ~/.codewise.db)
- I wanted to implement modern code completion for Leo editor
- codewise.py is usable as a python module, or a command line tool.

Creating ctags data
===================

1. Make sure you have exuberant ctags (not just regular ctags)
   installed. It's an Ubuntu package, so its easy to install if
   you're using Ubuntu.


2. [Optional] Create a custom ~/.ctags file containing default
    configuration settings for ctags. See:
    http://ctags.sourceforge.net/ctags.html#FILES for more
    details.

    The ``codewise setup`` command (see below), will leave this
    file alone if it exists; otherwise, ``codewise setup`` will
    create a ~/.ctags file containing::

        --exclude=*.html
        --exclude=*.css

3. Create the ctags data in ~/.codewise.db using this module. Execute the
   following from a console window::

        codewise setup
            # Optional: creates ~/.ctags if it does not exist.
            # See http://ctags.sourceforge.net/ctags.html#FILES
        codewise init
            # Optional: deletes ~/.codewise.db if it exists.
        codewise parse <path to directory>
            # Adds ctags data to ~/.codewise.db for <directory>

**Note**: On Windows, use a batch file, say codewise.bat, to execute the
above code. codewise.bat contains::

    python <path to leo>\leo\external\codewise.py %*

Using the autocompleter
=======================

After restarting Leo, type, for example, in the body pane::

    c.op<ctrl-space>

that is, use use the autocomplete-force command,
to find all the c. methods starting with 'op' etc.

Theory of operation
===================

- ~/.codewise.db is an sqlite database with following tables:

CLASS maps class id's to names.

FILE maps file id's to file names

DATASOURCE contains places where data has been parsed from, to enable reparse

FUNCTION, the most important one, contains functions/methods, along with CLASS
 and FILE it was found in. Additionally, it has SEARCHPATTERN field that can be
 used to give calltips, or used as a regexp to find the method from file
 quickly.

You can browse the data by installing sqlitebrovser and doing 'sqlitebrowser
~/codewise.db'

If you know the class name you want to find the methods for,
CodeWise.get_members with a list of classes to match.

If you want to match a function without a class, call CodeWise.get_functions.
This can be much slower if you have a huge database.

"""
#@-<< docstring >>
#@+<< imports >>
#@+node:ekr.20110310091639.14293: ** << imports >>
import os
import sys
import sqlite3
from sqlite3 import ProgrammingError
import traceback
#@-<< imports >>
consoleEncoding = None
#@+<< define usage >>
#@+node:ekr.20110310091639.14292: ** << define usage >>
usage = """
codewise setup
 (Optional - run this first to create template ~/.ctags)

codewise init
 Create/recreate the global database

codewise parse /my/project /other/project
 Parse specified directories (with recursion) and add results to db

codewise m
 List all classes

codewise m MyClass
 Show all methods in MyClass

codewise f PREFIX
 Show all symbols (also nonmember functiosn) starting with PREFIX.
 PREFIX can be omitted to get a list of all symbols

codewise parseall
 Clear database, reparse all paths previously added by 'codewise parse'

codewise sciapi pyqt.api
 Parse an api file (as supported by scintilla, eric4...)

Commands you don't probably need:

codewise tags TAGS
 Dump already-created tagfile TAGS to database

"""
#@-<< define usage >>
#@+<< define DB_SCHEMA >>
#@+node:ekr.20110310091639.14255: ** << define DB_SCHEMA >>
DB_SCHEMA = """
BEGIN TRANSACTION;
CREATE TABLE class (id INTEGER PRIMARY KEY, file INTEGER,  name TEXT, searchpattern TEXT);
CREATE TABLE file (id INTEGER PRIMARY KEY, path TEXT);
CREATE TABLE function (id INTEGER PRIMARY KEY, class INTEGER, file INTEGER, name TEXT, searchpattern TEXT);
CREATE TABLE datasource (type TEXT, src TEXT);

CREATE INDEX idx_class_name ON class(name ASC);
CREATE INDEX idx_function_class ON function(class ASC);

COMMIT;
"""
#@-<< define DB_SCHEMA >>
DEFAULT_DB = os.path.normpath(os.path.expanduser("~/.codewise.db"))
# print('default db: %s' % DEFAULT_DB)
#@+others
#@+node:ekr.20110310091639.14295: ** top level...
#@+node:ekr.20110310091639.14294: *3* codewise cmd wrappers
#@+node:ekr.20110310091639.14289: *4* cmd_functions
def cmd_functions(args):
    cw = CodeWise()
    if args:
        funcs = cw.get_functions(args[0])
    else:
        funcs = cw.get_functions()
    lines = list(set(el[0] + "\t" + el[1] for el in funcs))
    lines.sort()
    return lines  # EKR
#@+node:ekr.20110310091639.14285: *4* cmd_init
def cmd_init(args):
    print("Initializing CodeWise db at: %s" % DEFAULT_DB)
    if os.path.isfile(DEFAULT_DB):
        os.remove(DEFAULT_DB)
    CodeWise()
#@+node:ekr.20110310091639.14288: *4* cmd_members
def cmd_members(args):
    cw = CodeWise()
    if args:
        mems = cw.get_members([args[0]])
        lines = list(set(el + "\t" + pat for el, pat in mems))
    else:
        lines = cw.classcache.keys()  # type:ignore
    lines.sort()
    return lines  # EKR
#@+node:ekr.20110310091639.14283: *4* cmd_parse
def cmd_parse(args):
    assert args
    cw = CodeWise()
    cw.parse(args)
#@+node:ekr.20110310091639.14282: *4* cmd_parseall
def cmd_parseall(args):
    cw = CodeWise()
    cw.parseall()
#@+node:ekr.20110310091639.14281: *4* cmd_scintilla
def cmd_scintilla(args):
    cw = CodeWise()
    for fil in args:
        f = open(fil)
        cw.feed_scintilla(f)
        f.close()
#@+node:ekr.20110310091639.14286: *4* cmd_setup
def cmd_setup(args):

    ctagsfile = os.path.normpath(os.path.expanduser("~/.ctags"))
    if os.path.isfile(ctagsfile):
        print("Using template file: %s" % ctagsfile)
    else:
        print("Creating template: %s" % ctagsfile)
        open(ctagsfile, "w").write("--exclude=*.html\n--exclude=*.css\n")
    # No need for this: the docs say to run "init" after "setup"
        # cmd_init(args)
#@+node:ekr.20110310091639.14284: *4* cmd_tags
def cmd_tags(args):
    cw = CodeWise()
    cw.feed_ctags(open(args[0]))
#@+node:ekr.20110310093050.14234: *3* functions from leoGlobals
#@+node:ekr.20110310093050.14291: *4* Most common functions... (codewise.py)
#@+node:ekr.20110310093050.14296: *5* callers & _callerName (codewise)
def callers(n=4, count=0, excludeCaller=True, files=False):
    '''Return a list containing the callers of the function that called callerList.

    If the excludeCaller keyword is True (the default), callers is not on the list.

    If the files keyword argument is True, filenames are included in the list.
    '''
    # sys._getframe throws ValueError in both cpython and jython if there are less than i entries.
    # The jython stack often has less than 8 entries,
    # so we must be careful to call _callerName with smaller values of i first.
    result = []
    i = 3 if excludeCaller else 2
    while 1:
        s = _callerName(i, files=files)
        if s:
            result.append(s)
        if not s or len(result) >= n: break
        i += 1
    result.reverse()
    if count > 0: result = result[:count]
    sep = '\n' if files else ','
    return sep.join(result)
#@+node:ekr.20110310093050.14297: *6* _callerName
def _callerName(n=1, files=False):
    try:  # get the function name from the call stack.
        f1 = sys._getframe(n)  # The stack frame, n levels up.
        code1 = f1.f_code  # The code object
        name = code1.co_name
        if name == '__init__':
            name = '__init__(%s,line %s)' % (
                shortFileName(code1.co_filename), code1.co_firstlineno)
        return '%s:%s' % (shortFileName(code1.co_filename), name) if files else name
    except ValueError:
        return ''  # The stack is not deep enough.
    except Exception:
        es_exception()
        return ''  # "<no caller name>"
#@+node:ekr.20110310093050.14253: *5* doKeywordArgs (codewise)
def doKeywordArgs(keys, d=None):
    '''Return a result dict that is a copy of the keys dict
    with missing items replaced by defaults in d dict.'''
    if d is None: d = {}
    result = {}
    for key, default_val in d.items():
        isBool = default_val in (True, False)
        val = keys.get(key)
        if isBool and val in (True, 'True', 'true'):
            result[key] = True
        elif isBool and val in (False, 'False', 'false'):
            result[key] = False
        elif val is None:
            result[key] = default_val
        else:
            result[key] = val
    return result
#@+node:ekr.20180311191907.1: *5* error (codewise)
def error(*args, **keys):
    print(args, keys)
#@+node:ekr.20180311192928.1: *5* es_exception (codewise)
def es_exception(full=True, c=None, color="red"):
    typ, val, tb = sys.exc_info()
    # val is the second argument to the raise statement.
    if full:
        lines = traceback.format_exception(typ, val, tb)
    else:
        lines = traceback.format_exception_only(typ, val)
    for line in lines:
        print(line)
    fileName, n = getLastTracebackFileAndLineNumber()
    return fileName, n
#@+node:ekr.20180311193048.1: *5* getLastTracebackFileAndLineNumber (codewise)
def getLastTracebackFileAndLineNumber():
    typ, val, tb = sys.exc_info()
    if typ == SyntaxError:
        # IndentationError is a subclass of SyntaxError.
        # Much easier in Python 2.6 and 3.x.
        return val.filename, val.lineno  # type:ignore
    #
    # Data is a list of tuples, one per stack entry.
    # Tupls have the form (filename,lineNumber,functionName,text).
    data = traceback.extract_tb(tb)
    if data:
        item = data[-1]  # Get the item at the top of the stack.
        filename, n, functionName, text = item
        return filename, n
    #
    # Should never happen.
    return '<string>', 0
#@+node:ekr.20110310093050.14263: *5* pr (codewise)
# see: http://www.diveintopython.org/xml_processing/unicode.html

def pr(*args, **keys):  # (codewise!)
    '''Print all non-keyword args, and put them to the log pane.
    The first, third, fifth, etc. arg translated by translateString.
    Supports color, comma, newline, spaces and tabName keyword arguments.
    '''
    # Compute the effective args.
    d = {'commas': False, 'newline': True, 'spaces': True}
    d = doKeywordArgs(keys, d)
    newline = d.get('newline')
    if getattr(sys.stdout, 'encoding', None):
        # sys.stdout is a TextIOWrapper with a particular encoding.
        encoding = sys.stdout.encoding
    else:
        encoding = 'utf-8'
    # Translates everything to unicode.
    s = translateArgs(args, d)
    s = toUnicode(s, encoding=encoding, reportErrors=False)
    if newline:
        s += u('\n')
    # Python's print statement *can* handle unicode, but
    # sitecustomize.py must have sys.setdefaultencoding('utf-8')
    sys.stdout.write(s)  # Unit tests do not change sys.stdout.
#@+node:ekr.20180311193230.1: *5* shortFileName (codewise)
def shortFileName(fileName, n=None):
    '''Return the base name of a path.'''
    # pylint: disable=invalid-unary-operand-type
    if not fileName:
        return ''
    if n is None or n < 1:
        return os.path.basename(fileName)
    return '/'.join(fileName.replace('\\', '/').split('/')[-n :])
#@+node:ekr.20110310093050.14268: *5* trace (codewise)
# Convert all args to strings.

def trace(*args, **keys):
    # Compute the effective args.
    d = {'align': 0, 'newline': True}
    d = doKeywordArgs(keys, d)
    newline = d.get('newline')
    align = d.get('align')
    if align is None: align = 0
    # Compute the caller name.
    try:  # get the function name from the call stack.
        f1 = sys._getframe(1)  # The stack frame, one level up.
        code1 = f1.f_code  # The code object
        name = code1.co_name  # The code name
    except Exception:
        name = ''
    if name == "?":
        name = "<unknown>"
    # Pad the caller name.
    if align != 0 and len(name) < abs(align):
        pad = ' ' * (abs(align) - len(name))
        if align > 0: name = name + pad
        else: name = pad + name
    # Munge *args into s.
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
    pr(s, newline=newline)
#@+node:ekr.20110310093050.14264: *5* translateArgs (codewise)
def translateArgs(args, d):
    '''Return the concatenation of all args, with odd args translated.'''
    global consoleEncoding
    if not consoleEncoding:
        e = sys.getdefaultencoding()
        consoleEncoding = e if isValidEncoding(e) else 'utf-8'
    result: list[str] = []
    n = 0
    spaces = d.get('spaces')
    for arg in args:
        n += 1
        # print('translateArgs: arg',arg,type(arg),isString(arg),'will trans',(n%2)==1)
        # First, convert to unicode.
        if isString(arg):
            arg = toUnicode(arg, consoleEncoding)
        # Just do this for the stand-alone version.
        if not isString(arg):
            arg = repr(arg)
        if arg:
            if result and spaces: result.append(' ')
            result.append(arg)
    return ''.join(result)
#@+node:ekr.20110310093050.14280: *4* Unicode utils (codewise)...
#@+node:ekr.20110310093050.14282: *5* isBytes, isCallable, isString & isUnicode (codewise)
# The syntax of these functions must be valid on Python2K and Python3K.

# Codewise

def isBytes(s):
    '''Return True if s is Python3k bytes type.'''
    return isinstance(s, bytes)

def isCallable(obj):
    return hasattr(obj, '__call__')

def isString(s):
    '''Return True if s is any string, but not bytes.'''
    return isinstance(s, str)

def isUnicode(s):
    '''Return True if s is a unicode string.'''
    return isinstance(s, str)

#@+node:ekr.20110310093050.14283: *5* isValidEncoding (codewise)
def isValidEncoding(encoding):
    if not encoding:
        return False
    if sys.platform == 'cli':
        return True
    import codecs
    try:
        codecs.lookup(encoding)
        return True
    except LookupError:  # Windows.
        return False
    except AttributeError:  # Linux.
        return False
#@+node:ekr.20110310093050.14286: *5* toEncodedString (codewise)
def toEncodedString(s, encoding='utf-8', reportErrors=False):
    '''Convert unicode string to an encoded string.'''
    if not isUnicode(s):
        return s
    if encoding is None:
        encoding = 'utf-8'
    try:
        s = s.encode(encoding, "strict")
    except UnicodeError:
        s = s.encode(encoding, "replace")
        if reportErrors:
            error("Error converting %s from unicode to %s encoding" % (s, encoding))
    return s
#@+node:ekr.20110310093050.14287: *5* toUnicode (codewise)
def toUnicode(s, encoding='utf-8', reportErrors=False):
    '''Connvert a non-unicode string with the given encoding to unicode.'''
    if isUnicode(s):
        return s
    if not encoding:
        encoding = 'utf-8'
    try:
        s = s.decode(encoding, 'strict')
    except UnicodeError:
        s = s.decode(encoding, 'replace')
        if reportErrors:
            error("Error converting %s from %s encoding to unicode" % (s, encoding))
    return s
#@+node:ekr.20110310093050.14288: *5* u & ue (codewise)
def u(s):
    return s

def ue(s, encoding):
    return s if isUnicode(s) else str(s, encoding)
#@+node:ekr.20110310091639.14290: *3* main
def main():

    if len(sys.argv) < 2:
        print(usage)
        return
    cmd = sys.argv[1]
    args = sys.argv[2:]
    if cmd == 'tags':
        cmd_tags(args)
    elif cmd == 'm':
        printlines(cmd_members(args))
    elif cmd == 'f':
        printlines(cmd_functions(args))
    elif cmd == 'parse':
        cmd_parse(args)
    elif cmd == 'parseall':
        cmd_parseall(args)
    elif cmd == 'sciapi':
        cmd_scintilla(args)
    elif cmd == 'init':
        cmd_init(args)
    elif cmd == 'setup':
        cmd_setup(args)
#@+node:ekr.20110310091639.14287: *3* printlines
def printlines(lines):
    for l in lines:
        try:
            print(l)
        except Exception:  # EKR: UnicodeEncodeError:
            pass
#@+node:ekr.20110310091639.14280: *3* run_ctags
def run_ctags(paths):
    cm = 'ctags -R --sort=no -f - ' + " ".join(paths)
    # print(cm)
    f = os.popen(cm)
    return f
#@+node:ekr.20110310091639.14296: *3* test
def test(self):
    pass
#@+node:ekr.20110310091639.14256: ** class CodeWise
class CodeWise:
    #@+others
    #@+node:ekr.20110310091639.14257: *3* __init__(CodeWise)
    def __init__(self, dbpath=None):
        if dbpath is None:
            # use "current" db from env var
            dbpath = DEFAULT_DB
        # print(dbpath)
        self.reset_caches()
        if not os.path.exists(dbpath):
            self.createdb(dbpath)
        else:
            self.dbconn = sqlite3.connect(dbpath)
            self.create_caches()
    #@+node:ekr.20110310091639.14258: *3* createdb
    def createdb(self, dbpath):
        self.dbconn = c = sqlite3.connect(dbpath)
        # print(self.dbconn)
        c.executescript(DB_SCHEMA)
        c.commit()
        c.close()
    #@+node:ekr.20110310091639.14259: *3* create_caches
    def create_caches(self):
        """ read existing db and create caches """
        c = self.cursor()
        c.execute('select id, name from class')
        for idd, name in c:
            self.classcache[name] = idd
        c.execute('select id, path from file')
        for idd, name in c:
            self.filecache[name] = idd
        c.close()
    #@+node:ekr.20110310091639.14260: *3* reset_caches
    def reset_caches(self):
        self.classcache = {}
        self.filecache = {}
        self.fileids_scanned = set()
    #@+node:ekr.20110310091639.14261: *3* cursor
    def cursor(self):
        if self.dbconn:
            try:
                return self.dbconn.cursor()
            except ProgrammingError:
                print("No cursor for codewise DB, closed database?")
        return None
    #@+node:ekr.20110310091639.14262: *3* class_id
    def class_id(self, classname):
        """ return class id. May create new class """
        if classname is None:
            return 0
        idd = self.classcache.get(classname)
        if idd is None:
            c = self.cursor()
            c.execute('insert into class(name) values (?)', [classname])
            c.close()
            idd = c.lastrowid
            self.classcache[classname] = idd
        return idd
    #@+node:ekr.20110310091639.14263: *3* get_members
    def get_members(self, classnames):
        clset = set(classnames)
        # class_by_id = dict((v, k) for k, v in self.classcache.items())
        # file_by_id = dict((v, k) for k, v in self.filecache.items())
        result = []
        for name, idd in self.classcache.items():
            if name in clset:
                c = self.cursor()
                c.execute(
                    'select name, class, file, searchpattern from function where class = (?)',
                    (idd,))
                for name, klassid, fileid, pat in c:
                    result.append((name, pat))
        return result
    #@+node:ekr.20110310091639.14264: *3* get_functions
    def get_functions(self, prefix=None):
        c = self.cursor()
        if prefix is None:
            c.execute('select name, class, file, searchpattern from function')
        else:
            prefix = str(prefix)
            c.execute(
                'select name, class, file, searchpattern from function where name like (?)', (
                prefix + '%',))
        return [(name, pat, klassid, fileid) for name, klassid, fileid, pat in c]
    #@+node:ekr.20110310091639.14265: *3* file_id
    def file_id(self, fname):
        if fname == '':
            return 0
        idd = self.filecache.get(fname)
        if idd is None:
            c = self.cursor()
            c.execute('insert into file(path) values (?)', [fname])
            idd = c.lastrowid
            self.filecache[fname] = idd
            self.fileids_scanned.add(idd)
        else:
            if idd in self.fileids_scanned:
                return idd
            # we are rescanning a file with old entries - nuke old entries
            c = self.cursor()
            c.execute("delete from function where file = (?)", (idd,))
            #self.dbconn.commit()
            self.fileids_scanned.add(idd)
        return idd
    #@+node:ekr.20110310091639.14266: *3* feed_function
    def feed_function(self, func_name, class_name, file_name, aux):
        """ insert one function

        'aux' can be a search pattern (as with ctags), signature, or description


        """
        clid = self.class_id(class_name)
        fid = self.file_id(file_name)
        c = self.cursor()
        c.execute(
            'insert into function(class, name, searchpattern, file) values (?, ?, ?, ?)',
                  [clid, func_name, aux, fid])
    #@+node:ekr.20110310091639.14267: *3* feed_scintilla
    def feed_scintilla(self, apifile_obj):
        """ handle scintilla api files

        Syntax is like:

        qt.QApplication.style?4() -> QStyle
        """
        for l in apifile_obj:
            parts = l.split('?')
            fullsym = parts[0].rsplit('.', 1)
            klass, func = fullsym
            if len(parts) == 2:
                desc = parts[1]
            else:
                desc = ''
            # now our class is like qt.QApplication. We do the dirty trick and
            # remove all but actual class name
            shortclass = klass.rsplit('.', 1)[-1]
            self.feed_function(func.strip(), shortclass.strip(), '', desc.strip())
        self.dbconn.commit()
    #@+node:ekr.20110310091639.14268: *3* feed_ctags
    def feed_ctags(self, tagsfile_obj):
        for l in tagsfile_obj:
            if l.startswith('!'):
                continue
            fields = l.split('\t')
            m = fields[0]
            fil = fields[1]
            pat = fields[2]
            klass = None
            try:
                ext = fields[4]
                if ext and ext.startswith('class:'):
                    klass = ext.split(':', 1)[1].strip()
                    idd = self.class_id(klass)
            except IndexError:
                ext = None
                idd = 0
            c = self.cursor()
            fid = self.file_id(fil)
            c.execute(
                'insert into function(class, name, searchpattern, file) values (?, ?, ?, ?)',
                      [idd, m, pat, fid])
        self.dbconn.commit()
    #@+node:ekr.20110310091639.14269: *3* add_source
    def add_source(self, type, src):
        c = self.cursor()
        c.execute('insert into datasource(type, src) values (?,?)', (type, src))
        self.dbconn.commit()
    #@+node:ekr.20110310091639.14270: *3* sources
    def sources(self):
        c = self.cursor()
        c.execute('select type, src from datasource')
        return list(c)
    #@+node:ekr.20110310091639.14271: *3* zap_symbols
    def zap_symbols(self):
        c = self.cursor()
        tables = ['class', 'file', 'function']
        for t in tables:
            c.execute('delete from ' + t)
        self.dbconn.commit()
    #@+node:ekr.20110310091639.14272: *3* # high level commands
    # high level commands
    #@+node:ekr.20110310091639.14273: *3* parseall
    def parseall(self):
        sources = self.sources()
        self.reset_caches()
        self.zap_symbols()
        tagdirs = [td for typ, td in sources if typ == 'tagdir']
        self.parse(tagdirs)
        self.dbconn.commit()
    #@+node:ekr.20110310091639.14274: *3* parse
    def parse(self, paths):
        paths = set(os.path.abspath(p) for p in paths)
        f = run_ctags(paths)
        self.feed_ctags(f)
        sources = self.sources()
        for a in paths:
            if ('tagdir', a) not in sources:
                self.add_source('tagdir', a)
    #@-others
#@+node:ekr.20110310091639.14275: ** class ContextSniffer
class ContextSniffer:
    """ Class to analyze surrounding context and guess class

    For simple dynamic code completion engines

    """
    #@+others
    #@+node:ekr.20110310091639.14276: *3* __init__ (ContextSniffer)
    def __init__(self):
        # var name => list of classes
        self.vars = {}
    #@+node:ekr.20110310091639.14277: *3* declare
    def declare(self, var, klass):
        # print("declare",var,klass)
        vars = self.vars.get(var, [])
        if not vars:
            self.vars[var] = vars
        vars.append(klass)
    #@+node:ekr.20110310091639.14278: *3* push_declarations
    def push_declarations(self, body):
        for l in body.splitlines():
            l = l.lstrip()
            if not l.startswith('#'):
                continue
            l = l.lstrip('#')
            parts = l.strip(':')
            if len(parts) != 2:
                continue
            self.declare(parts[0].strip(), parts[1].strip())
    #@+node:ekr.20110310091639.14279: *3* set_small_context
    def set_small_context(self, body):
        """ Set immediate function """
        self.push_declarations(body)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70

if __name__ == "__main__":
    main()
#@-leo
