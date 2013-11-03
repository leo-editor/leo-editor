# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20031218072017.3093: * @file leoGlobals.py
#@@first

'''Global constants, variables and utility functions used throughout Leo.

Important: This module imports no other Leo module.
'''

#@@language python
#@@tabwidth -4
#@@pagewidth 70

import sys
isPython3 = sys.version_info >= (3,0,0)
#@+<< global switches >>
#@+node:ekr.20120212060348.10374: **  << global switches >>
trace_startup = False
    # These traces use print instead of g.trace so that
    # the traces can add class info the method name.

new_modes = False
    # True: use ModeController and ModeInfo classes.
if new_modes: print('***** new_modes')

new_keys = False
    # This project hardly seems urgent.
    # True: Qt input methods produce a **user setting**, not a stroke.
if new_keys: print('***** new_keys')

# Debugging options...

enableDB = True
    # Don't even think about eliminating this constant:
    # it is needed for debugging.

no_scroll = False
    # True: disable all calls to w.setYScrollPosition.
no_see = False
    # True: disable all calls to w.see and w.seeInsertPoint.

# Tracing options...

trace_scroll = False
    # Trace calls to get/setYScrollPosition
trace_see = False
    # Trace calls to see and setInsertPoint.

# Switches to trace the garbage collector.
trace_gc = False           
trace_gc_calls = False    
trace_gc_calls = False 
trace_gc_verbose = False
trace_gc_inited = False

trace_masterCommand = False
trace_masterKeyHandler = False
trace_masterKeyHandlerGC = False
trace_minibuffer = False
trace_modes = False

# These print statements have been moved to writeWaitingLog.
# This allows for better --silent operation.
if 0:
    print('*** isPython3: %s' % isPython3)
    if not enableDB:
        print('** leoGlobals.py: caching disabled')

#@-<< global switches >>
#@+<< imports >>
#@+node:ekr.20050208101229: ** << imports >> (leoGlobals)
if 0:
    # This is now done in run.
    import leo.core.leoGlobals as g # So code can use g below.

# Don't import this here: it messes up Leo's startup code.
# import leo.core.leoTest as leoTest

import codecs

try:
    import gc
except ImportError:
    gc = None

try:
    import filecmp
except ImportError: # does not exist in jython.
    filecmp = None

try:
    import gettext
except ImportError: # does not exist in jython.
    gettext = None

if isPython3:
    from functools import reduce

if isPython3:
    import io
    StringIO = io.StringIO
else:
    import cStringIO
    StringIO = cStringIO.StringIO

import imp
import inspect
import operator
import os

# Module 'urllib' has no 'parse' member.
import urllib # pylint: disable=E0611

# Do NOT import pdb here!  We shall define pdb as a _function_ below.
# import pdb

import re
import shutil
import string
import subprocess
# import sys
import tempfile
import time
import traceback
import types

if isPython3:
    # E0611: No name 'parse' in urllib.
    import urllib.parse as urlparse # pylint: disable=E0611
else:
    import urlparse

# import zipfile

# These do not exist in IronPython.
# However, it *is* valid for IronPython to use the Python 2.4 libs!
    # import os
    # import string
    # import tempfile
    # import traceback
    # import types
#@-<< imports >>
#@+<< define globalDirectiveList >>
#@+node:EKR.20040610094819: ** << define globalDirectiveList >>
# Visible externally so plugins may add to the list of directives.

globalDirectiveList = [

    # *** Longer prefixes must appear before shorter.
    'all',
    'colorcache', # 2012/10/03.
    'code','color', 'comment','c',
    'delims','doc','encoding','end_raw',
    'first','header','ignore','killcolor',
    'language','last','lineending',
    'markup', # Make this an official directive,
    'nocolor-node','nocolor','noheader','nowrap',
    'others','pagewidth','path','quiet',
    'raw','root-code','root-doc','root','silent',
    'tabwidth', 'terse',
    'unit','verbose', 'wrap',
]
#@-<< define globalDirectiveList >>
#@+<< define the nullObject class >>
#@+node:ekr.20090521175848.5881: ** << define the nullObject class >>
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
#@-<< define the nullObject class >>
tree_popup_handlers = [] # Set later.
user_dict = {}
    # Non-persistent dictionary for free use by scripts and plugins.
# g = None
app = None # The singleton app object. Set by runLeo.py.

# Global status vars.
inScript = False # A synonym for app.inScript
unitTesting = False # A synonym for app.unitTesting.

#@+others
#@+node:ekr.20031218072017.3095: ** Checking Leo Files...
#@+node:ekr.20031218072017.822: *3* createTopologyList
def createTopologyList (c,root=None,useHeadlines=False):

    """Creates a list describing a node and all its descendents"""

    if not root: root = c.rootPosition()
    v = root
    if useHeadlines:
        aList = [(v.numberOfChildren(),v.headString()),]
    else:
        aList = [v.numberOfChildren()]
    child = v.firstChild()
    while child:
        aList.append(g.createTopologyList(c,child,useHeadlines))
        child = child.next()
    return aList
#@+node:ekr.20031218072017.3099: ** Commands & Directives
#@+node:ekr.20031218072017.1380: *3* g.Directive utils...
# New in Leo 4.6:
# g.findAtTabWidthDirectives, g.findLanguageDirectives and
# g.get_directives_dict use re module for faster searching.
#@+node:EKR.20040504150046.4: *4* g.comment_delims_from_extension
def comment_delims_from_extension(filename):

    """
    Return the comment delims corresponding to the filename's extension.

    >>> import leo.core.leoGlobals as g
    >>> g.comment_delims_from_extension(".py")
    ('#', '', '')

    >>> g.comment_delims_from_extension(".c")
    ('//', '/*', '*/')

    >>> g.comment_delims_from_extension(".html")
    ('', '<!--', '-->')

    """

    if filename.startswith('.'):
        # Python 2.6 changes how splitext works.
        root,ext = None,filename
    else:
        root, ext = os.path.splitext(filename)
    if ext == '.tmp':
        root, ext = os.path.splitext(root)

    language = g.app.extension_dict.get(ext[1:])
    if ext:
        return g.set_delims_from_language(language)
    else:
        g.trace("unknown extension: %s, filename: %s, root: %s" % (
            repr(ext),repr(filename),repr(root)))
        return '','',''
#@+node:ekr.20090214075058.8: *4* g.findAtTabWidthDirectives (must be fast)
g_tabwidth_pat = re.compile(r'(^@tabwidth)',re.MULTILINE)

def findTabWidthDirectives(c,p):

    '''Return the language in effect at position p.'''

    if c is None:
        return # c may be None for testing.

    w = None
    # 2009/10/02: no need for copy arg to iter
    for p in p.self_and_parents():
        if w: break
        for s in p.h,p.b:
            if w: break
            anIter = g_tabwidth_pat.finditer(s)
            for m in anIter:
                word = m.group(0)
                i = m.start(0)
                j = g.skip_ws(s,i + len(word))
                junk,w = g.skip_long(s,j)
                if w == 0: w = None
    return w
#@+node:ekr.20090214075058.6: *4* g.findLanguageDirectives (must be fast)
g_language_pat = re.compile(r'(^@language)',re.MULTILINE)

def findLanguageDirectives(c,p):

    '''Return the language in effect at position p.'''

    trace = False and not g.unitTesting

    if c is None:
        return # c may be None for testing. 
    if c.target_language:
        language = c.target_language.lower()
    else:
        language = 'python'
    found = False
    # 2009/10/02: no need for copy arg to iter.
    for p in p.self_and_parents():
        if found: break
        for s in p.h,p.b:
            if found: break
            anIter = g_language_pat.finditer(s)
            for m in anIter:
                word = m.group(0)
                i = m.start(0)
                j = i + len(word)
                k = g.skip_line(s,j)
                language = s[j:k].strip()
                found = True

    if trace: g.trace(language)
    return language
#@+node:ekr.20031218072017.1385: *4* g.findReference
# Called from the syntax coloring method that colorizes section references.
# Also called from write at.putRefAt.

def findReference(c,name,root):

    '''Find the section definition for name.

    If a search of the descendants fails,
    and an ancestor is an @root node,
    search all the descendants of the @root node.
    '''

    for p in root.subtree():
        assert(p!=root)
        if p.matchHeadline(name) and not p.isAtIgnoreNode():
            return p

    # New in Leo 4.7: expand the search for @root trees.
    for p in root.self_and_parents():
        d = g.get_directives_dict(p)
        if 'root' in d:
            for p2 in p.subtree():
                if p2.matchHeadline(name) and not p2.isAtIgnoreNode():
                    return p2

    # g.trace("not found:",name,root)
    return c.nullPosition()
#@+node:ekr.20090214075058.9: *4* g.get_directives_dict (must be fast)
# The caller passes [root_node] or None as the second arg.
# This allows us to distinguish between None and [None].

g_noweb_root = re.compile('<'+'<'+'*'+'>'+'>'+'=',re.MULTILINE)

def get_directives_dict(p,root=None):
    """
    Scan p for @directives found in globalDirectiveList.

    Returns a dict containing the stripped remainder of the line
    following the first occurrence of each recognized directive
    """
    trace = False and not g.unitTesting
    verbose = False
    if trace: g.trace('*'*20,p.h)
    if root: root_node = root[0]
    d = {}
    # Do this every time so plugins can add directives.
    pat = g.compute_directives_re()
    directives_pat = re.compile(pat,re.MULTILINE)
    # The headline has higher precedence because it is more visible.
    for kind,s in (('head',p.h),('body',p.b)):
        anIter = directives_pat.finditer(s)
        for m in anIter:
            word = m.group(0)[1:] # Omit the @
            i = m.start(0)
            if word.strip() not in d:
                j = i + 1 + len(word)
                k = g.skip_line(s,j)
                val = s[j:k].strip()
                if j < len(s) and s[j] not in (' ','\t','\n'):
                    # g.es_print('invalid character after directive',s[max(0,i-1):k-1])
                    # if trace:g.trace(word,repr(val),s[i:i+20])
                    pass # Not a valid directive: just ignore it.
                else:
                    directive_word = word.strip()
                    if directive_word == 'language':
                        d[directive_word] = val
                    else:
                        if directive_word in ('root-doc', 'root-code'):
                            d['root'] = val # in addition to optioned version
                        d[directive_word] = val
                    # g.trace(kind,directive_word,val)
                    if trace: g.trace(word.strip(),kind,repr(val))
                    # A special case for @path in the body text of @<file> nodes.
                    # Don't give an actual warning: just set some flags.
                    if kind == 'body' and word.strip() == 'path' and p.isAnyAtFileNode():
                        g.app.atPathInBodyWarning = p.h
                        d['@path_in_body'] = p.h
                        if trace: g.trace('@path in body',p.h)

    if root:
        anIter = g_noweb_root.finditer(p.b)
        for m in anIter:
            if root_node:
                d["root"]=0 # value not immportant
            else:
                g.es('%s= may only occur in a topmost node (i.e., without a parent)' % (
                    g.angleBrackets('*')))
            break
    if trace and verbose:
        g.trace('%4d' % (len(p.h) + len(p.b)))
    return d
#@+node:ekr.20090214075058.10: *5* compute_directives_re
def compute_directives_re ():

    '''Return an re pattern which will match all Leo directives.'''

    global globalDirectiveList

    aList = ['^@%s' % z for z in globalDirectiveList
                if z != 'others']

    if 0: # 2010/02/01
        # The code never uses this, and this regex is broken
        # because it can confuse g.get_directives_dict.
        # @others can have leading whitespace.
        aList.append(r'^\s@others\s')

    return '|'.join(aList)
#@+node:ekr.20080827175609.1: *4* g.get_directives_dict_list (must be fast)
def get_directives_dict_list(p):

    """Scans p and all its ancestors for directives.

    Returns a list of dicts containing pointers to
    the start of each directive"""

    result = []
    p1 = p.copy()
    for p in p1.self_and_parents():
        root = None if p.hasParent() else [p.copy()]
        result.append(g.get_directives_dict(p,root=root))
    # if trace:
        # n = len(p1.h) + len(p1.b)
        # g.trace('%4d %s' % (n,g.timeSince(time1)))
    return result
#@+node:ekr.20111010082822.15545: *4* g.getLanguageFromAncestorAtFileNode (New)
def getLanguageFromAncestorAtFileNode(p):

    '''Return the language in effect as determined
    by the file extension of the nearest enclosing @<file> node.
    '''

    for p in p.self_and_parents():
        if p.isAnyAtFileNode():
            name = p.anyAtFileNodeName()
            junk,ext = g.os_path_splitext(name)
            ext = ext[1:] # strip the leading .
            language = g.app.extension_dict.get(ext)

            # g.trace('found extension',p.h,ext,language)
            return language

    return None
#@+node:ekr.20031218072017.1386: *4* g.getOutputNewline
def getOutputNewline (c=None,name=None):

    '''Convert the name of a line ending to the line ending itself.

    Priority:
    - Use name if name given
    - Use c.config.output_newline if c given,
    - Otherwise use g.app.config.output_newline.'''

    if name: s = name
    elif c:  s = c.config.output_newline
    else:    s = app.config.output_newline

    if not s: s = ''
    s = s.lower()
    if s in ( "nl","lf"): s = '\n'
    elif s == "cr": s = '\r'
    elif s == "platform": s = os.linesep  # 12/2/03: emakital
    elif s == "crlf": s = "\r\n"
    else: s = '\n' # Default for erroneous values.
    # g.trace(c,name,c.config.output_newline,'returns',repr(s))

    if g.isPython3:
        s = str(s)
    return s
#@+node:ekr.20080827175609.52: *4* g.scanAtCommentAndLanguageDirectives
def scanAtCommentAndAtLanguageDirectives(aList):

    '''Scan aList for @comment and @language directives.

    @comment should follow @language if both appear in the same node.'''

    trace = False and not g.unitTesting
    lang = None

    for d in aList:

        comment = d.get('comment')
        language = d.get('language')

        # Important: assume @comment follows @language.
        if language:
            # if g.unitTesting: g.trace('language',language)
            lang,delim1,delim2,delim3 = g.set_language(language,0)

        if comment:
            # if g.unitTesting: g.trace('comment',comment)
            delim1,delim2,delim3 = g.set_delims_from_string(comment)

        if comment or language:
            delims = delim1,delim2,delim3
            d = {'language':lang,'comment':comment,'delims':delims}
            if trace: g.trace(d)
            return d

    if trace: g.trace(repr(None))
    return None
#@+node:ekr.20080827175609.32: *4* g.scanAtEncodingDirectives
def scanAtEncodingDirectives(aList):

    '''Scan aList for @encoding directives.'''

    for d in aList:
        encoding = d.get('encoding')
        if encoding and g.isValidEncoding(encoding):
            # g.trace(encoding)
            return encoding
        elif encoding and not g.app.unitTesting:
            g.error("invalid @encoding:",encoding)

    return None
#@+node:ekr.20080827175609.53: *4* g.scanAtHeaderDirectives
def scanAtHeaderDirectives(aList):

    '''scan aList for @header and @noheader directives.'''

    for d in aList:
        if d.get('header') and d.get('noheader'):
            g.error("conflicting @header and @noheader directives")
#@+node:ekr.20080827175609.33: *4* g.scanAtLineendingDirectives
def scanAtLineendingDirectives(aList):

    '''Scan aList for @lineending directives.'''

    for d in aList:

        e = d.get('lineending')
        if e in ("cr","crlf","lf","nl","platform"):
            lineending = g.getOutputNewline(name=e)
            return lineending
        # else:
            # g.error("invalid @lineending directive:",e)

    return None
#@+node:ekr.20080827175609.34: *4* g.scanAtPagewidthDirectives
def scanAtPagewidthDirectives(aList,issue_error_flag=False):

    '''Scan aList for @pagewidth directives.'''

    for d in aList:
        s = d.get('pagewidth')
        if s is not None:
            i, val = g.skip_long(s,0)
            if val != None and val > 0:
                # g.trace(val)
                return val
            else:
                if issue_error_flag and not g.app.unitTesting:
                    g.error("ignoring @pagewidth",s)

    return None
#@+node:ekr.20101022172109.6108: *4* g.scanAtPathDirectives scanAllAtPathDirectives
def scanAtPathDirectives(c,aList):

    path = c.scanAtPathDirectives(aList)
    return path

def scanAllAtPathDirectives(c,p):

    aList = g.get_directives_dict_list(p)
    path = c.scanAtPathDirectives(aList)
    return path
#@+node:ekr.20100507084415.5760: *4* g.scanAtRootDirectives
def scanAtRootDirectives(aList):

    '''Scan aList for @root directives.'''

    for d in aList:
        s = d.get('root')
        if s is not None:
            i, mode = g.scanAtRootOptions(s,0)
            g.trace(mode)
            return mode

    return None
#@+node:ekr.20031218072017.3154: *4* g.scanAtRootOptions
def scanAtRootOptions (s,i,err_flag=False):

    # The @root has been eaten when called from tangle.scanAllDirectives.
    if g.match(s,i,"@root"):
        i += len("@root")
        i = g.skip_ws(s,i)

    mode = None 
    while g.match(s,i,'-'):
        #@+<< scan another @root option >>
        #@+node:ekr.20031218072017.3155: *5* << scan another @root option >>
        i += 1 ; err = -1

        if g.match_word(s,i,"code"): # Just match the prefix.
            if not mode: mode = "code"
            elif err_flag: g.es("modes conflict in:",g.get_line(s,i))
        elif g.match(s,i,"doc"): # Just match the prefix.
            if not mode: mode = "doc"
            elif err_flag: g.es("modes conflict in:",g.get_line(s,i))
        else:
            err = i-1

        # Scan to the next minus sign.
        while i < len(s) and s[i] not in (' ','\t','\n','-'):
            i += 1

        if err > -1 and err_flag:
            z_opt = s[err:i]
            z_line = g.get_line(s,i)
            g.es("unknown option:",z_opt,"in",z_line)
        #@-<< scan another @root option >>

    if mode == None:
        doc = app.config.at_root_bodies_start_in_doc_mode
        mode = g.choose(doc,"doc","code")

    # g.trace(mode,g.callers(3))

    return i,mode
#@+node:ekr.20080827175609.37: *4* g.scanAtTabwidthDirectives & scanAllTabWidthDirectives
def scanAtTabwidthDirectives(aList,issue_error_flag=False):

    '''Scan aList for @tabwidth directives.'''

    for d in aList:
        s = d.get('tabwidth')
        if s is not None:
            junk,val = g.skip_long(s,0)
            if val not in (None,0):
                return val
            else:
                if issue_error_flag and not g.app.unitTesting:
                    g.error("ignoring @tabwidth",s)
    return None

def scanAllAtTabWidthDirectives(c,p):

    '''Scan p and all ancestors looking for @tabwidth directives.'''

    if c and p:
        aList = g.get_directives_dict_list(p)
        val = g.scanAtTabwidthDirectives(aList)
        ret = g.choose(val is None,c.tab_width,val)
    else:
        ret = None
    # g.trace(ret,p and p.h,ret)
    return ret
#@+node:ekr.20080831084419.4: *4* g.scanAtWrapDirectives & scanAllAtWrapDirectives
def scanAtWrapDirectives(aList,issue_error_flag=False):

    '''Scan aList for @wrap and @nowrap directives.'''

    for d in aList:
        if d.get('wrap') is not None:
            return True
        elif d.get('nowrap') is not None:
            return False

    return None

def scanAllAtWrapDirectives(c,p):

    '''Scan p and all ancestors looking for @wrap/@nowrap directives.'''

    if c and p:
        default = c and c.config.getBool("body_pane_wraps")
        aList = g.get_directives_dict_list(p)

        val = g.scanAtWrapDirectives(aList)
        ret = g.choose(val is None,default,val)
    else:
        ret = None
    # g.trace(ret,p.h)
    return ret
#@+node:ekr.20080901195858.4: *4* g.scanDirectives  (for compatibility only)
def scanDirectives(c,p=None):

    return c.scanAllDirectives(p)
#@+node:ekr.20040715155607: *4* g.scanForAtIgnore
def scanForAtIgnore(c,p):

    """Scan position p and its ancestors looking for @ignore directives."""

    if g.app.unitTesting:
        return False # For unit tests.

    for p in p.self_and_parents():
        d = g.get_directives_dict(p)
        if 'ignore' in d:
            return True

    return False
#@+node:ekr.20040712084911.1: *4* g.scanForAtLanguage
def scanForAtLanguage(c,p):

    """Scan position p and p's ancestors looking only for @language and @ignore directives.

    Returns the language found, or c.target_language."""

    # Unlike the code in x.scanAllDirectives, this code ignores @comment directives.

    if c and p:
        for p in p.self_and_parents():
            d = g.get_directives_dict(p)
            if 'language' in d:
                z = d["language"]
                language,delim1,delim2,delim3 = g.set_language(z,0)
                return language

    return c.target_language
#@+node:ekr.20041123094807: *4* g.scanForAtSettings
def scanForAtSettings(p):

    """Scan position p and its ancestors looking for @settings nodes."""

    for p in p.self_and_parents():
        h = p.h
        h = g.app.config.canonicalizeSettingName(h)
        if h.startswith("@settings"):
            return True

    return False
#@+node:ekr.20031218072017.1382: *4* g.set_delims_from_language
# Returns a tuple (single,start,end) of comment delims

def set_delims_from_language(language):

    trace = False and not g.unitTesting

    val = g.app.language_delims_dict.get(language)
    # if language.startswith('huh'): g.pdb()

    if val:
        delim1,delim2,delim3 = g.set_delims_from_string(val)
        if trace: g.trace(repr(language),
            repr(delim1),repr(delim2),repr(delim3),g.callers(5))
        if delim2 and not delim3:
            return '',delim1,delim2
        else: # 0,1 or 3 params.
            return delim1,delim2,delim3
    else:
        return '','','' # Indicate that no change should be made
#@+node:ekr.20031218072017.1383: *4* g.set_delims_from_string
def set_delims_from_string(s):

    """Returns (delim1, delim2, delim2), the delims following the @comment directive.

    This code can be called from @language logic, in which case s can point at @comment"""

    # Skip an optional @comment
    tag = "@comment"
    i = 0
    if g.match_word(s,i,tag):
        i += len(tag)

    count = 0 ; delims = ['','','']
    while count < 3 and i < len(s):
        i = j = g.skip_ws(s,i)
        while i < len(s) and not g.is_ws(s[i]) and not g.is_nl(s,i):
            i += 1
        if j == i: break
        delims[count] = s[j:i] or ''
        count += 1

    # 'rr 09/25/02
    if count == 2: # delims[0] is always the single-line delim.
        delims[2] = delims[1]
        delims[1] = delims[0]
        delims[0] = ''

    # 7/8/02: The "REM hack": replace underscores by blanks.
    # 9/25/02: The "perlpod hack": replace double underscores by newlines.
    for i in range(0,3):
        if delims[i]:
            delims[i] = delims[i].replace("__",'\n').replace('_',' ')

    return delims[0], delims[1], delims[2]
#@+node:ekr.20031218072017.1384: *4* g.set_language
def set_language(s,i,issue_errors_flag=False):

    """Scan the @language directive that appears at s[i:].

    The @language may have been stripped away.

    Returns (language, delim1, delim2, delim3)
    """

    tag = "@language"
    # g.trace(g.get_line(s,i))
    assert(i != None)
    # assert(g.match_word(s,i,tag))
    if g.match_word(s,i,tag):
        i += len(tag)
    # Get the argument.
    i = g.skip_ws(s, i)
    j = i ; i = g.skip_c_id(s,i)
    # Allow tcl/tk.
    arg = s[j:i].lower()
    if app.language_delims_dict.get(arg):
        language = arg
        delim1, delim2, delim3 = g.set_delims_from_language(language)
        return language, delim1, delim2, delim3
    if issue_errors_flag:
        g.es("ignoring:",g.get_line(s,i))
    return None, None, None, None,
#@+node:ekr.20081001062423.9: *4* g.setDefaultDirectory & helper
def setDefaultDirectory(c,p,importing=False):

    ''' Return a default directory by scanning @path directives.'''

    name = p.anyAtFileNodeName()
    if name:
        # An absolute path overrides everything.
        d = g.os_path_dirname(name)
        if d and g.os_path_isabs(d):
            return d

    aList = g.get_directives_dict_list(p)
    path = c.scanAtPathDirectives(aList)
        # Returns g.getBaseDirectory(c) by default.
        # However, g.getBaseDirectory can return ''
    if path:
        path = g.os_path_finalize(path)
    else:
        g.checkOpenDirectory(c)
        for d in (c.openDirectory,g.getBaseDirectory(c)):
            # Errors may result in relative or invalid path.
            if d and g.os_path_isabs(d):
                path = d
                break
        else:
            path = ''

    if not importing and not path:
        # This should never happen, but is not serious if it does.
        g.warning("No absolute directory specified anywhere.")

    return path
#@+node:ekr.20101022124309.6132: *5* g.checkOpenDirectory
def checkOpenDirectory (c):

    if c.openDirectory != c.frame.openDirectory:
        g.error(
            'Error: c.openDirectory != c.frame.openDirectory\n'
            'c.openDirectory: %s\n'
            'c.frame.openDirectory: %s' % (
                c.openDirectory,c.frame.openDirectory))

    if not g.os_path_isabs(c.openDirectory):
        g.error ('Error: relative c.openDirectory: %s' % (
            c.openDirectory))
#@+node:ekr.20071109165315: *4* g.stripPathCruft
def stripPathCruft (path):

    '''Strip cruft from a path name.'''

    if not path:
        return path # Retain empty paths for warnings.

    if len(path) > 2 and (
        (path[0]=='<' and path[-1] == '>') or
        (path[0]=='"' and path[-1] == '"') or
        (path[0]=="'" and path[-1] == "'")
    ):
        path = path[1:-1].strip()

    # We want a *relative* path, not an absolute path.
    return path
#@+node:ekr.20031218072017.3104: ** Debugging, Dumping, Timing, Tracing & Sherlock
#@+node:ekr.20051023083258: *3* callers & _callerName
def callers (n=4,count=0,excludeCaller=True,files=False):

    '''Return a list containing the callers of the function that called g.callerList.

    If the excludeCaller keyword is True (the default), g.callers is not on the list.

    If the files keyword argument is True, filenames are included in the list.
    '''

    # sys._getframe throws ValueError in both cpython and jython if there are less than i entries.
    # The jython stack often has less than 8 entries,
    # so we must be careful to call g._callerName with smaller values of i first.
    result = []
    i = 3 if excludeCaller else 2
    while 1:
        s = _callerName(i,files=files)
        # print(i,s)
        if s:
            result.append(s)
        if not s or len(result) >= n: break
        i += 1

    result.reverse()
    if count > 0: result = result[:count]
    sep = '\n' if files else ','
    return sep.join(result)
#@+node:ekr.20031218072017.3107: *4* _callerName
def _callerName (n=1,files=False):

    # print('_callerName: %s %s' % (n,files))

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
        # print('g._callerName: ValueError',n)
        return '' # The stack is not deep enough.
    except Exception:
        es_exception()
        return '' # "<no caller name>"
#@+node:ekr.20121128031949.12605: *3* class SherlockTracer
class SherlockTracer:

    '''A stand-alone tracer class with many of Sherlock's features.

    This class should work in any environment in which it is possible
    to import os and sys.
    
    The arguments in the pattern lists determine which functions get traced or which stats get printed.  Each pattern starts with "+", "-", "+:" or "-:", followed by a regular expression.

    "+x"  Enables tracing (or stats) for all functions/methods whose name
          matches the regular expression x.
    "-x"  Disables tracing for functions/methods.
    "+:x" Enables tracing for all functions in the **file** whose name matches x.
    "-:x" Disables tracing for an entire file.
    
    Enabling and disabling depends on the order of arguments in the pattern
    list. Consider the arguments for the Rope trace::
    
    patterns=['+.*','+:.*',
        '-:.*\\lib\\.*','+:.*rope.*','-:.*leoGlobals.py',
        '-:.*worder.py','-:.*prefs.py','-:.*resources.py',])
    
    This enables tracing for everything, then disables tracing for all
    library modules, except for all rope modules. Finally, it disables the
    tracing for Rope's worder, prefs and resources modules. Btw, this is
    one of the best uses for regular expressions that I know of.
    
    Being able to zero in on the code of interest can be a big help in
    studying other people's code. This is a non-invasive method: no tracing
    code needs to be inserted anywhere.
    '''

    #@+others
    #@+node:ekr.20121128031949.12602: *4* __init__
    def __init__(self,patterns,dots=True,show_args=True,show_return=True,verbose=True):

        import re
        self.bad_patterns = []          # List of bad patterns.
        self.dots = dots                # True: print level dots.
        self.n = 0                      # The frame level on entry to run.
        self.stats = {}                 # Keys are full file names, values are dicts.
        self.patterns = patterns        # A list of regex patterns to match.
        self.re = re                    # Import re only once.
        self.show_args = show_args      # True: show args for each function call.
        self.show_return = show_return  # True: show returns from each function.
        self.verbose = verbose          # True: print filename:func
        try:
            from PyQt4 import QtCore
            QtCore.pyqtRemoveInputHook()
        except Exception:
            pass
    #@+node:ekr.20121128031949.12609: *4* dispatch
    def dispatch(self,frame,event,arg):

        if event == 'call':
            self.do_call(frame,arg)

        elif event == 'return' and self.show_return:
            self.do_return(frame,arg)

        return self.dispatch
    #@+node:ekr.20121128031949.12603: *4* do_call & helper
    def do_call(self,frame,arg): # arg not used.

        import os
        frame1 = frame
        code = frame.f_code
        fn   = code.co_filename
        locals_ = frame.f_locals
        name = code.co_name
        full_name = self.get_full_name(locals_,name)
        if (
            self.is_enabled(fn,name,self.patterns) and
            self.is_enabled(fn,full_name,self.patterns)
        ):
            n = 0
            while frame:
                frame = frame.f_back
                n += 1
            # g_callers = ','.join(self.g.callers(5).split(',')[:-1])
            dots   = '.' * max(0,n-self.n) if self.dots else ''
            path   = '%-20s' % (os.path.basename(fn)) if self.verbose else ''
            leadin = '+' if self.show_return else ''
            args = '(%s)' % self.get_args(frame1) if self.show_args else ''
            print('%s%s%s%s%s' % (path,dots,leadin,full_name,args))

        # Alwas update stats.
        d = self.stats.get(fn,{})
        d[full_name] = 1 + d.get(full_name,0)
        self.stats[fn] = d
    #@+node:ekr.20130111185820.10194: *5* get_args
    def get_args(self,frame):

        def show(item):
            if not item: return ''
            try:
                return item.__class__.__name__
            except Exception:
                return repr(item)
        code = frame.f_code
        locals_ = frame.f_locals
        name = code.co_name
        # fn = code.co_filename
        n = code.co_argcount
        if code.co_flags & 4: n = n+1
        if code.co_flags & 8: n = n+1
        result = []
        for i in range(n):
            name = code.co_varnames[i]
            if name != 'self':
                arg = locals_.get(name,'*undefined*')
                if arg:
                    if isinstance(arg,(list,tuple)):
                        val = '[%s]' % ','.join([show(z) for z in arg if show(z)])
                    else:
                        val = show(arg)
                    if val:
                        result.append('%s=%s' % (name,val))
        return ','.join(result)
    #@+node:ekr.20130109154743.10172: *4* do_return & helper
    def do_return(self,frame,arg): # arg not used.

        import os
        code = frame.f_code
        fn = code.co_filename
        locals_ = frame.f_locals
        name = code.co_name
        full_name = self.get_full_name(locals_,name)
        if (
            self.is_enabled(fn,name,self.patterns) and
            self.is_enabled(fn,full_name,self.patterns)
        ):
            n = 0
            while frame:
                frame = frame.f_back
                n += 1
            dots = '.' * max(0,n-self.n) if self.dots else ''
            path = '%-20s' % (os.path.basename(fn)) if self.verbose else ''
            ret = self.format_ret(arg)
            print('%s%s-%s%s' % (path,dots,full_name,ret))
    #@+node:ekr.20130111120935.10192: *5* format_ret
    def format_ret(self,arg):

        try:
            if isinstance(arg,(tuple,list)):
                try:
                    ret = ' -> [%s]' % ','.join([z.__class__.__name__ for z in arg])
                except Exception:
                    ret = ' -> [%s]' % ','.join([repr(z) for z in arg])
                if len(ret) > 40:
                    try:
                        ret = ' -> [\n%s]' % ('\n,'.join([z.__class__.__name__ for z in arg]))
                    except Exception:
                        ret = ' -> [\n%s]' % ('\n,'.join([repr(z) for z in arg]))
            elif arg:
                try:
                    ret = ' -> %s' % arg.__class__.__name__
                except Exception:
                    ret = ' -> %r' % arg
                if len(ret) > 40:
                    ret = ' ->\n    %r' % arg
            else:
                ret = ''
        except Exception:
            exctype, value = sys.exc_info()[:2]
            s = '<**exception: %s,%s arg: %r**>' % (exctype.__name__, value,arg)
            ret = ' ->\n    %s' % (s) if len(s) > 40 else ' -> %s' % (s)

        return ret
    #@+node:ekr.20121128111829.12185: *4* fn_is_enabled
    def fn_is_enabled (self,fn,patterns):

        '''Return True if tracing for fn is enabled.'''

        try:
            enabled = False
            for pattern in patterns:
                if pattern.startswith('+:'):
                    if self.re.match(pattern[2:],fn): 
                        enabled = True
                elif pattern.startswith('-:'):
                    if self.re.match(pattern[2:],fn):
                        enabled = False
            return enabled
        except Exception:
            return False
    #@+node:ekr.20130112093655.10195: *4* get_full_name
    def get_full_name(self,locals_,name):

        full_name = name
        try:
            user_self = locals_ and locals_.get('self',None)
            if user_self:
                full_name = user_self.__class__.__name__ + '::' + name
        except Exception:
            pass
        return full_name
    #@+node:ekr.20121128111829.12183: *4* is_enabled
    def is_enabled (self,fn,name,patterns):

        '''Return True if tracing for name in fn is enabled.'''

        def oops(pattern):
            if pattern not in self.bad_patterns:
                self.bad_patterns.append(pattern)
                print('ignoring bad pattern: %s' % pattern)

        enabled = False 
        for pattern in patterns:
            try:
                if pattern.startswith('+:'):
                    if self.re.match(pattern[2:],fn): 
                        enabled = True
                elif pattern.startswith('-:'):
                    if self.re.match(pattern[2:],fn):
                        enabled = False
                elif pattern.startswith('+'):
                    if self.re.match(pattern[1:],name):
                        enabled = True
                elif pattern.startswith('-'):
                    if self.re.match(pattern[1:],name):
                        enabled = False
                else: oops(pattern)
            except Exception:
                oops(pattern)

        return enabled

    #@+node:ekr.20121128111829.12182: *4* print_stats
    def print_stats (self,patterns=None):

        print('\nSherlock statistics')
        if not patterns: patterns = ['+.*','+:.*',]
        for fn in sorted(self.stats.keys()):
            d = self.stats.get(fn)
            if self.fn_is_enabled(fn,patterns):
                result = sorted(d.keys())
            else:
                result = [key for key in sorted(d.keys()) if self.is_enabled(fn,key,patterns)]
            if result:
                print('')
                fn = fn.replace('\\','/')
                parts = fn.split('/')
                print('/'.join(parts[-2:]))
                for key in result:
                    print('%4s %s' % (d.get(key),key))
    #@+node:ekr.20121128031949.12614: *4* run
    # Modified from pdb.Pdb.set_trace.

    def run(self,frame=None):

        '''Trace from the given frame or the caller's frame.'''

        import sys

        if frame is None:
            frame = sys._getframe().f_back

        # Compute self.n, the number of frames to ignore.
        self.n = 0
        while frame:
            frame = frame.f_back
            self.n += 1

        sys.settrace(self.dispatch)
    #@+node:ekr.20121128093229.12616: *4* stop
    def stop(self):

        '''Stop all tracing.'''

        import sys
        sys.settrace(None)
    #@-others
#@+node:ekr.20080531075119.1: *3* class Tracer & g.startTracer
class Tracer:

    '''A "debugger" that computes a call graph.

    To trace a function and its callers, put the following at the function's start:

    g.startTracer()
    '''

    #@+others
    #@+node:ekr.20080531075119.2: *4*  __init__ (Tracer)
    def __init__(self,limit=0,trace=False,verbose=False):

        self.callDict = {}
            # Keys are function names.
            # Values are the number of times the function was called by the caller.
        self.calledDict = {}
            # Keys are function names.
            # Values are the total number of times the function was called.

        self.count = 0
        self.inited = False
        self.limit = limit # 0: no limit, otherwise, limit trace to n entries deep.
        self.stack = []
        self.trace = trace
        self.verbose = verbose # True: print returns as well as calls.
    #@+node:ekr.20080531075119.3: *4* computeName
    def computeName (self,frame):

        if not frame: return ''
        code = frame.f_code ; result = []
        module = inspect.getmodule(code)
        if module:
            module_name = module.__name__
            if module_name == 'leo.core.leoGlobals':
                result.append('g')
            else:
                tag = 'leo.core.'
                if module_name.startswith(tag):
                    module_name = module_name[len(tag):]
                result.append(module_name)
        try:
            # This can fail during startup.
            self_obj = frame.f_locals.get('self')
            if self_obj: result.append(self_obj.__class__.__name__)
        except Exception:
            pass
        result.append(code.co_name)
        return '.'.join(result)
    #@+node:ekr.20080531075119.4: *4* report
    def report (self):

        if 0:
            g.pr('\nstack')
            for z in self.stack:
                g.pr(z)

        g.pr('\ncallDict...')

        for key in sorted(self.callDict):

            # Print the calling function.
            g.pr('%d' % (self.calledDict.get(key,0)),key)

            # Print the called functions.
            d = self.callDict.get(key)
            for key2 in sorted(d):
                g.pr('%8d' % (d.get(key2)),key2)
    #@+node:ekr.20080531075119.5: *4* stop
    def stop (self):

        sys.settrace(None)
        self.report()
    #@+node:ekr.20080531075119.6: *4* tracer
    def tracer (self, frame, event, arg):

        '''A function to be passed to sys.settrace.'''

        n = len(self.stack)
        if event == 'return': n = max(0,n-1)
        pad = '.' * n

        if event == 'call':
            if not self.inited:
                # Add an extra stack element for the routine containing the call to startTracer.
                self.inited = True
                name = self.computeName(frame.f_back)
                self.updateStats(name)
                self.stack.append(name)
            name = self.computeName(frame)
            if self.trace and (self.limit == 0 or len(self.stack) < self.limit):
                g.trace('%scall' % (pad),name)
            self.updateStats(name)
            self.stack.append(name)
            return self.tracer
        elif event == 'return':
            if self.stack:
                name = self.stack.pop()
                if self.trace and self.verbose and (self.limit == 0 or len(self.stack) < self.limit):
                    g.trace('%sret ' % (pad),name)
            else:
                g.trace('return underflow')
                self.stop()
                return None
            if self.stack:
                return self.tracer
            else:
                self.stop()
                return None
        else:
            return self.tracer
    #@+node:ekr.20080531075119.7: *4* updateStats
    def updateStats (self,name):

        if not self.stack:
            return

        caller = self.stack[-1]
        d = self.callDict.get(caller,{})
            # d is a dict reprenting the called functions.
            # Keys are called functions, values are counts.
        d[name] = 1 + d.get(name,0)
        self.callDict[caller] = d

        # Update the total counts.
        self.calledDict[name] = 1 + self.calledDict.get(name,0)
    #@-others

def startTracer(limit=0,trace=False,verbose=False):

    import sys
    t = g.Tracer(limit=limit,trace=trace,verbose=verbose)
    sys.settrace(t.tracer)
    return t
#@+node:ekr.20031218072017.3108: *3* Dumps
#@+node:ekr.20031218072017.3109: *4* dump
def dump(s):

    out = ""
    for i in s:
        out += str(ord(i)) + ","
    return out

def oldDump(s):

    out = ""
    for i in s:
        if i=='\n':
            out += "[" ; out += "n" ; out += "]"
        if i=='\t':
            out += "[" ; out += "t" ; out += "]"
        elif i==' ':
            out += "[" ; out += " " ; out += "]"
        else: out += i
    return out
#@+node:ekr.20060917120951: *4* es_dump
def es_dump (s,n = 30,title=None):

    if title:
        g.es_print('',title)

    i = 0
    while i < len(s):
        aList = ''.join(['%2x ' % (ord(ch)) for ch in s[i:i+n]])
        g.es_print('',aList)
        i += n
#@+node:ekr.20031218072017.3110: *4* es_error & es_print_error
def es_error (*args,**keys):

    color = keys.get('color')

    if color is None and g.app.config:
        keys['color'] = g.app.config.getColor("log_error_color") or 'red'

    g.es(*args,**keys)


def es_print_error (*args,**keys):

    color = keys.get('color')

    if color is None and g.app.config:
        keys['color'] = g.app.config.getColor("log_error_color") or 'red'

    g.es_print(*args,**keys)
#@+node:ekr.20031218072017.3111: *4* es_event_exception
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
#@+node:ekr.20031218072017.3112: *4* es_exception
def es_exception (full=True,c=None,color="red"):

    typ,val,tb = sys.exc_info()

    # val is the second argument to the raise statement.

    if full or g.app.debugSwitch > 0:
        lines = traceback.format_exception(typ,val,tb)
    else:
        lines = traceback.format_exception_only(typ,val)

    for line in lines:
        g.es_print_error(line,color=color)

    # if g.app.debugSwitch > 1:
        # import pdb # Be careful: g.pdb may or may not have been defined.
        # pdb.set_trace()

    fileName,n = g.getLastTracebackFileAndLineNumber()

    return fileName,n
#@+node:ekr.20111107181638.9741: *4* es_print_exception
def es_print_exception (full=True,c=None,color="red"):

    typ,val,tb = sys.exc_info()

    # val is the second argument to the raise statement.

    if full or g.app.debugSwitch > 0:
        lines = traceback.format_exception(typ,val,tb)
    else:
        lines = traceback.format_exception_only(typ,val)

    for line in lines:
        print(line)

    fileName,n = g.getLastTracebackFileAndLineNumber()

    return fileName,n
#@+node:ekr.20061015090538: *4* es_exception_type
def es_exception_type (c=None,color="red"):

    # exctype is a Exception class object; value is the error message.
    exctype, value = sys.exc_info()[:2]

    g.es_print('','%s, %s' % (exctype.__name__, value),color=color)
#@+node:ekr.20040731204831: *4* getLastTracebackFileAndLineNumber
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
#@+node:ekr.20031218072017.3113: *4* printBindings
def print_bindings (name,window):

    bindings = window.bind()

    g.pr("\nBindings for", name)
    for b in bindings:
        g.pr(b)
#@+node:ekr.20031218072017.3114: *4* printGlobals
def printGlobals(message=None):

    # Get the list of globals.
    globs = list(globals())
    globs.sort()

    # Print the list.
    if message:
        leader = "-" * 10
        g.pr(leader, ' ', message, ' ', leader)
    for glob in globs:
        g.pr(glob)
#@+node:ekr.20070510074941: *4* g.printEntireTree
def printEntireTree(c,tag=''):

    g.pr('printEntireTree','=' * 50)
    g.pr('printEntireTree',tag,'root',c.rootPosition())
    for p in c.all_positions():
        g.pr('..'*p.level(),p.v)
#@+node:ekr.20031218072017.3115: *4* printLeoModules
def printLeoModules(message=None):

    # Create the list.
    mods = []
    for name in sys.modules:
        if name and name[0:3] == "leo":
            mods.append(name)

    # Print the list.
    if message:
        leader = "-" * 10
        g.pr(leader, ' ', message, ' ', leader)
    mods.sort()
    for m in mods:
        g.pr(m,newline=False)
    g.pr('')
#@+node:ekr.20031218072017.1317: *3* file/module/plugin_date
def module_date (mod,format=None):
    theFile = g.os_path_join(app.loadDir,mod.__file__)
    root,ext = g.os_path_splitext(theFile) 
    return g.file_date(root + ".py",format=format)

def plugin_date (plugin_mod,format=None):
    theFile = g.os_path_join(app.loadDir,"..","plugins",plugin_mod.__file__)
    root,ext = g.os_path_splitext(theFile) 
    return g.file_date(root + ".py",format=format)

def file_date (theFile,format=None):
    if theFile and len(theFile)and g.os_path_exists(theFile):
        try:
            n = g.os_path_getmtime(theFile)
            if format == None:
                format = "%m/%d/%y %H:%M:%S"
            return time.strftime(format,time.gmtime(n))
        except (ImportError,NameError):
            pass # Time module is platform dependent.
    return ""
#@+node:ekr.20031218072017.3105: *3* g.alert
def alert(message,c=None):

    '''Raise an alert.

    This method is deprecated: use c.alert instead.
    '''

    # The unit tests just tests the args.
    if not g.unitTesting:
        g.es(message)
        g.app.gui.alert(c,message)
#@+node:ekr.20031218072017.3127: *3* g.get_line & get_line__after
# Very useful for tracing.

def get_line (s,i):

    nl = ""
    if g.is_nl(s,i):
        i = g.skip_nl(s,i)
        nl = "[nl]"
    j = g.find_line_start(s,i)
    k = g.skip_to_end_of_line(s,i)
    return nl + s[j:k]

# Important: getLine is a completely different function.
# getLine = get_line

def get_line_after (s,i):

    nl = ""
    if g.is_nl(s,i):
        i = g.skip_nl(s,i)
        nl = "[nl]"
    k = g.skip_to_end_of_line(s,i)
    return nl + s[i:k]

getLineAfter = get_line_after
#@+node:ekr.20080729142651.1: *3* g.getIvarsDict and checkUnchangedIvars
def getIvarsDict(obj):

    '''Return a dictionary of ivars:values for non-methods of obj.'''

    d = dict(
        [[key,getattr(obj,key)] for key in dir(obj)
            if type (getattr(obj,key)) != types.MethodType])
    return d

def checkUnchangedIvars(obj,d,exceptions=None):

    if not exceptions: exceptions = []
    ok = True
    for key in d:
        if key not in exceptions:
            if getattr(obj,key) != d.get(key):
                g.trace('changed ivar: %s old: %s new: %s' % (
                    key,repr(d.get(key)),repr(getattr(obj,key))))
                ok = False
    return ok
#@+node:ekr.20041105091148: *3* g.pdb
def pdb (message=''):

    """Fall into pdb."""

    import pdb # Required: we have just defined pdb as a function!

    if app and not app.useIpython:
        try:
            import PyQt4.QtCore as QtCore
            QtCore.pyqtRemoveInputHook()
        except ImportError:
            pass
    if message:
        print(message)
    pdb.set_trace()
#@+node:ekr.20031218072017.3128: *3* pause
def pause (s):

    g.pr(s)

    i = 0 ; n = long(1000) * long(1000)
    while i < n:
        i += 1
#@+node:ekr.20041224080039: *3* print_dict & dictToString
def print_dict(d,tag='',verbose=True,indent=''):

    if not d:
        if tag: g.pr('%s...{}' % tag)
        else:   g.pr('{}')
        return

    n = 6
    for key in sorted(d):
        if type(key) == type(''):
            n = max(n,len(key))
    if tag: g.es('%s...{\n' % tag)
    else:   g.es('{\n')
    for key in sorted(d):
        g.pr("%s%*s: %s" % (indent,n,key,repr(d.get(key)).strip()))
    g.pr('}')

printDict = print_dict

def dictToString(d,tag=None,verbose=True,indent=''):

    if not d:
        if tag: return '%s...{}' % tag
        else:   return '{}'
    n = 6
    for key in sorted(d):
        if g.isString(key):
            n = max(n,len(key))
    lines = ["%s%*s: %s" % (indent,n,key,repr(d.get(key)).strip())
        for key in sorted(d)]
    s = '\n'.join(lines)
    if tag:
        return '%s...{\n%s}\n' % (tag,s)
    else:
        return '{\n%s}\n' % s
#@+node:ekr.20041126060136: *3* print_list & listToString
def print_list(aList,tag=None,sort=False,indent=''):

    if not aList:
        if tag: g.pr('%s...[]' % tag)
        else:   g.pr('[]')
        return
    if sort:
        bList = aList[:] # Sort a copy!
        bList.sort()
    else:
        bList = aList
    if tag: g.pr('%s...[' % tag)
    else:   g.pr('[')
    for e in bList:
        g.pr('%s%s' % (indent,repr(e).strip()))
    g.pr(']')

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
#@+node:ekr.20050819064157: *3* print_obj & toString
def print_obj (obj,tag=None,sort=False,verbose=True,indent=''):

    if type(obj) in (type(()),type([])):
        g.print_list(obj,tag,sort,indent)
    elif type(obj) == type({}):
        g.print_dict(obj,tag,verbose,indent)
    else:
        g.pr('%s%s' % (indent,repr(obj).strip()))

def toString (obj,tag=None,sort=False,verbose=True,indent=''):

    if type(obj) in (type(()),type([])):
        return g.listToString(obj,tag,sort,indent)
    elif type(obj) == type({}):
        return g.dictToString(obj,tag,verbose,indent)
    else:
        return '%s%s' % (indent,repr(obj).strip())
#@+node:ekr.20041122153823: *3* print_stack (printStack)
def print_stack():

    traceback.print_stack()

printStack = print_stack
#@+node:ekr.20031218072017.3121: *3* redirecting stderr and stdout to Leo's log pane
class redirectClass:

    """A class to redirect stdout and stderr to Leo's log pane."""

    #@+<< redirectClass methods >>
    #@+node:ekr.20031218072017.1656: *4* << redirectClass methods >>
    #@+others
    #@+node:ekr.20041012082437: *5* redirectClass.__init__
    def __init__ (self):

        self.old = None
        self.encoding = 'utf-8' # 2019/03/29 For pdb.
    #@+node:ekr.20041012082437.1: *5* isRedirected
    def isRedirected (self):

        return self.old != None
    #@+node:ekr.20041012082437.2: *5* flush
    # For LeoN: just for compatibility.

    def flush(self, *args):
        return
    #@+node:ekr.20041012091252: *5* rawPrint
    def rawPrint (self,s):

        if self.old:
            self.old.write(s+'\n')
        else:
            g.pr(s)
    #@+node:ekr.20041012082437.3: *5* redirect
    def redirect (self,stdout=1):

        if g.app.batchMode:
            # Redirection is futile in batch mode.
            return

        if not self.old:
            if stdout:
                self.old,sys.stdout = sys.stdout,self
            else:
                self.old,sys.stderr = sys.stderr,self
    #@+node:ekr.20041012082437.4: *5* undirect
    def undirect (self,stdout=1):

        if self.old:
            if stdout:
                sys.stdout,self.old = self.old,None
            else:
                sys.stderr,self.old = self.old,None
    #@+node:ekr.20041012082437.5: *5* write
    def write(self,s):

        trace = False

        if self.old:
            if app.log:
                if trace: self.old.write(
                    'redirectClass: to log: %s\n' % repr(s))
                app.log.put(s, from_redirect=True)
            else:
                self.old.write(s +'\n')
        else:
            # Can happen when g.batchMode is True.
            g.pr(s)
    #@-others
    #@-<< redirectClass methods >>

# Create two redirection objects, one for each stream.
redirectStdErrObj = redirectClass()
redirectStdOutObj = redirectClass()

#@+<< define convenience methods for redirecting streams >>
#@+node:ekr.20031218072017.3122: *4* << define convenience methods for redirecting streams >>
#@+others
#@+node:ekr.20041012090942: *5* redirectStderr & redirectStdout
# Redirect streams to the current log window.
def redirectStderr():
    global redirectStdErrObj
    redirectStdErrObj.redirect(stdout=False)

def redirectStdout():
    global redirectStdOutObj
    redirectStdOutObj.redirect()
#@+node:ekr.20041012090942.1: *5* restoreStderr & restoreStdout
# Restore standard streams.
def restoreStderr():
    global redirectStdErrObj
    redirectStdErrObj.undirect(stdout=False)

def restoreStdout():
    global redirectStdOutObj
    redirectStdOutObj.undirect()
#@+node:ekr.20041012090942.2: *5* stdErrIsRedirected & stdOutIsRedirected
def stdErrIsRedirected():
    global redirectStdErrObj
    return redirectStdErrObj.isRedirected()

def stdOutIsRedirected():
    global redirectStdOutObj
    return redirectStdOutObj.isRedirected()
#@+node:ekr.20041012090942.3: *5* rawPrint
# Send output to original stdout.

def rawPrint(s):

    global redirectStdOutObj

    redirectStdOutObj.rawPrint(s)
#@-others
#@-<< define convenience methods for redirecting streams >>
#@+node:ekr.20031218072017.3133: *3* Statistics
#@+node:ekr.20031218072017.3134: *4* clear_stats
def clear_stats():

    g.trace()

    g.app.statsDict = {}

clearStats = clear_stats
#@+node:ekr.20031218072017.3135: *4* print_stats
def print_stats (name=None):

    if name:
        if type(name) != type(""):
            name = repr(name)
    else:
        name = g._callerName(n=2) # Get caller name 2 levels back.

    g.printDict(g.app.statsDict,tag='statistics at %s' % name)

printStats = print_stats
#@+node:ekr.20031218072017.3136: *4* stat
def stat (name=None):

    """Increments the statistic for name in g.app.statsDict
    The caller's name is used by default.
    """

    d = g.app.statsDict

    if name:
        if type(name) != type(""):
            name = repr(name)
    else:
        name = g._callerName(n=2) # Get caller name 2 levels back.

    # g.trace(name)

    d [name] = 1 + d.get(name,0)
#@+node:ekr.20031218072017.3137: *3* Timing
def getTime():
    return time.clock()

def esDiffTime(message, start):
    delta = time.clock()-start
    g.es('',"%s %6.3f sec." % (message,delta))
    return time.clock()

def printDiffTime(message, start):
    delta = time.clock()-start
    g.pr("%s %6.3f sec." % (message,delta))
    return time.clock()

def timeSince(start):
    return "%6.3f sec." % (time.clock()-start)
#@+node:ekr.20031218072017.3116: ** Files & Directories...
#@+node:ekr.20120222084734.10287: *3*  Redirection to LoadManager methods
# For compatibility with old code.
def computeGlobalConfigDir():
    return g.app.loadManager.computeGlobalConfigDir()

def computeHomeDir():
    return g.app.loadManager.computeHomeDir()

def computeLeoDir():
    return g.app.loadManager.computeLeoDir()

def computeLoadDir():
    return g.app.loadManager.computeLoadDir()

def computeMachineName():
    return g.app.loadManager.computeMachineName()

def computeStandardDirectories():
    return g.app.loadManager.computeStandardDirectories()
#@+node:ekr.20080606074139.2: *3* g.chdir
def chdir (path):

    if not g.os_path_isdir(path):
        path = g.os_path_dirname(path)

    if g.os_path_isdir(path) and g.os_path_exists(path):
        os.chdir(path)
#@+node:ekr.20031218072017.3117: *3* g.create_temp_file
def create_temp_file (textMode=False):
    '''Return a tuple (theFile,theFileName)

    theFile: a file object open for writing.
    theFileName: the name of the temporary file.'''

    try:
        # fd is an handle to an open file as would be returned by os.open()
        fd,theFileName = tempfile.mkstemp(text=textMode)
        mode = g.choose(textMode,'w','wb')
        theFile = os.fdopen(fd,mode)
    except Exception:
        g.error('unexpected exception in g.create_temp_file')
        g.es_exception()
        theFile,theFileName = None,''

    return theFile,theFileName
#@+node:ekr.20031218072017.3118: *3* g.ensure_extension
def ensure_extension (name, ext):

    theFile, old_ext = g.os_path_splitext(name)
    if not name:
        return name # don't add to an empty name.
    elif old_ext and old_ext == ext:
        return name
    else:
        return name + ext
#@+node:ekr.20031218072017.1264: *3* g.getBaseDirectory
# Handles the conventions applying to the "relative_path_base_directory" configuration option.

def getBaseDirectory(c):

    '''Convert '!' or '.' to proper directory references.'''

    base = app.config.relative_path_base_directory

    if base and base == "!":
        base = app.loadDir
    elif base and base == ".":
        base = c.openDirectory

    if base and g.os_path_isabs(base):
        # Set c.chdir_to_relative_path as needed.
        if not hasattr(c,'chdir_to_relative_path'):
            c.chdir_to_relative_path = c.config.getBool('chdir_to_relative_path')
        # Call os.chdir if requested.
        if c.chdir_to_relative_path:
            os.chdir(base)
        # g.trace(base)
        return base # base need not exist yet.
    else:
        return "" # No relative base given.
#@+node:ville.20090701144325.14942: *3* g.guessExternalEditor
def guessExternalEditor(c=None):
    """ Return a 'sensible' external editor """

    editor = (
        os.environ.get("LEO_EDITOR") or
        os.environ.get("EDITOR") or
        g.app.db and g.app.db.get("LEO_EDITOR") or
        c and c.config.getString('external_editor'))

    if editor: return editor

    # fallbacks
    platform = sys.platform.lower()
    if platform.startswith('win'):
        return "notepad"
    elif platform.startswith('linux'):
        return 'gedit'
    else:
        g.es('''No editor set.
Please set LEO_EDITOR or EDITOR environment variable,
or do g.app.db['LEO_EDITOR'] = "gvim"''')
        return None
#@+node:ekr.20100329071036.5744: *3* g.is_binary_file/external_file/string
def is_binary_file (f):
    if g.isPython3:
        return f and isinstance(f,io.BufferedIOBase)
    else:
        g.internalError('g.is_binary_file called from Python 2.x code')
        
def is_binary_external_file(fileName):
    try:
        f = open(fileName,'rb')
        s = f.read(1024) # bytes, in Python 3.
        f.close()
        return g.is_binary_string(s)
    except IOError:
        return False
    except Exception:
        g.es_exception()
        return False

def is_binary_string(s):
    # http://stackoverflow.com/questions/898669
    # aList is a list of all non-binary characters.
    aList = [7,8,9,10,12,13,27] + list(range(0x20,0x100))
    if g.isPython3:
        aList = bytes(aList)
    else:
        aList = ''.join([chr(z) for z in aList])
    return bool(s.translate(None,aList))
#@+node:EKR.20040504154039: *3* g.is_sentinel
def is_sentinel (line,delims):

    #@+<< is_sentinel doc tests >>
    #@+node:ekr.20040719161756: *4* << is_sentinel doc tests >>
    """

    Return True if line starts with a sentinel comment.

    >>> import leo.core.leoGlobals as g
    >>> py_delims = g.comment_delims_from_extension('.py')
    >>> g.is_sentinel("#@+node",py_delims)
    True
    >>> g.is_sentinel("#comment",py_delims)
    False

    >>> c_delims = g.comment_delims_from_extension('.c')
    >>> g.is_sentinel("//@+node",c_delims)
    True
    >>> g.is_sentinel("//comment",c_delims)
    False

    >>> html_delims = g.comment_delims_from_extension('.html')
    >>> g.is_sentinel("<!--@+node-->",html_delims)
    True
    >>> g.is_sentinel("<!--comment-->",html_delims)
    False

    """
    #@-<< is_sentinel doc tests >>

    delim1,delim2,delim3 = delims

    line = line.lstrip()

    if delim1:
        return line.startswith(delim1+'@')
    elif delim2 and delim3:
        i = line.find(delim2+'@')
        j = line.find(delim3)
        return 0 == i < j
    else:
        g.error("is_sentinel: can not happen. delims: %s" % repr(delims))
        return False
#@+node:ekr.20031218072017.3119: *3* g.makeAllNonExistentDirectories
# This is a generalization of os.makedir.

def makeAllNonExistentDirectories (theDir,c=None,force=False,verbose=True):

    """Attempt to make all non-existent directories"""

    trace = False and not g.unitTesting
    testing = trace # True: don't actually make the directories.

    if force:
        create = True # Bug fix: g.app.config will not exist during startup.
    elif c:
        create = c.config and c.config.create_nonexistent_directories
    else:
        create = (g.app and g.app.config and
            g.app.config.create_nonexistent_directories)

    if c: theDir = g.os_path_expandExpression(theDir,c=c)

    dir1 = theDir = g.os_path_normpath(theDir)

    ok = g.os_path_isdir(dir1) and g.os_path_exists(dir1)

    if trace: g.trace('ok',ok,'create',create,'force',force,dir1,g.callers())

    if ok:
        return ok
    elif not force and not create:
        if trace:
            g.trace('did not create: force and create are both false')
        return False

    if trace:
        g.trace('\n',theDir,'\n',g.callers(4))
        # g.trace('c exists: %s force: %s create: %s dir: %s' % (
            # c is not None,force,create,theDir))

    # Split theDir into all its component parts.
    paths = []
    while len(theDir) > 0:
        head,tail=g.os_path_split(theDir)
        if len(tail) == 0:
            paths.append(head)
            break
        else:
            paths.append(tail)
            theDir = head
    path = ""
    paths.reverse()
    if trace: g.trace('paths:',paths)
    for s in paths:
        path = g.os_path_finalize_join(path,s)
        if not g.os_path_exists(path):
            try:
                if testing:
                    g.trace('***making',path)
                else:
                    os.mkdir(path)
                if verbose and not testing and not g.app.unitTesting:
                    g.red("created directory:",path)
            except Exception:
                if verbose: g.error("exception creating directory:",path)
                g.es_exception()
                return None
    return dir1 # All have been created.
#@+node:ekr.20071114113736: *3* g.makePathRelativeTo
def makePathRelativeTo (fullPath,basePath):

    if fullPath.startswith(basePath):
        s = fullPath[len(basePath):]
        if s.startswith(os.path.sep):
            s = s[len(os.path.sep):]
        return s
    else:
        return fullPath
#@+node:ekr.20090520055433.5945: *3* g.openWithFileName
def openWithFileName(fileName,old_c=None,gui=None):

    """Create a Leo Frame for the indicated fileName if the file exists.

    returns the commander of the newly-opened outline.
    """

    return g.app.loadManager.loadLocalFile(fileName,gui,old_c)
#@+node:ekr.20100125073206.8710: *3* g.readFileIntoString (Leo 4.7)
def readFileIntoString (fn,
    encoding='utf-8',
    kind=None,
    mode='rb',
    raw=False,
    silent=False,
):

    '''Return the contents of the file whose full path is fn.

    Return (s,e)
    s is the string, converted to unicode, or None if there was an error.
    e the encoding line for Python files: it is usually None.
    '''

    try:
        e = None
        f = open(fn,mode)
        s = f.read()
        f.close()
        if raw or not s:
            return s,e
        # New in Leo 4.11: check for unicode BOM first.
        e,s = g.stripBOM(s)
        if not e:
            # Python's encoding comments override everything else.
            junk,ext = g.os_path_splitext(fn)
            if ext == '.py':
                e = g.getPythonEncodingFromString(s)
        s = g.toUnicode(s,encoding=e or encoding)
        return s,e
    except IOError:
        # Translate 'can not open' and kind, but not fn.
        # g.trace(g.callers(5))
        if not silent:
            if kind:
                g.error('can not open','',kind,fn)
            else:
                g.error('can not open',fn)
    except Exception:
        g.error('readFileIntoString: unexpected exception reading %s' % (fn))
        g.es_exception()
    return None,None
#@+node:ekr.20031218072017.3120: *3* g.readlineForceUnixNewline
#@+at Stephen P. Schaefer 9/7/2002
# 
# The Unix readline() routine delivers "\r\n" line end strings verbatim,
# while the windows versions force the string to use the Unix convention
# of using only "\n". This routine causes the Unix readline to do the
# same.
#@@c

def readlineForceUnixNewline(f,fileName=None):

    try:
        s = f.readline()
        # g.trace(repr(s))
    except UnicodeDecodeError:
        g.trace('UnicodeDecodeError: %s' % (fileName),f,g.callers())
        s = g.u('')

    if len(s) >= 2 and s[-2] == "\r" and s[-1] == "\n":
        s = s[0:-2] + "\n"
    return s
#@+node:tbrown.20110219154422.37469: *3* g.recursiveUNLSearch
def recursiveUNLSearch(unlList, c, depth=0, p=None, maxdepth=0, maxp=None):
    """try and move to unl in the commander c

    NOTE: maxdepth is max depth seen in recursion so far, not a limit on
          how fast we will recurse.  So it should default to 0 (zero).
    """

    if g.unitTesting:
        g.app.unitTestDict['g.recursiveUNLSearch']=True
        return True, maxdepth, maxp

    def moveToP(c, p):
        c.expandAllAncestors(p)
        c.selectPosition(p)
        c.redraw()
        c.frame.bringToFront()

    found, maxdepth, maxp = recursiveUNLFind(unlList, c, depth, p, maxdepth, maxp)

    if maxp:
        moveToP(c, maxp)

    return found, maxdepth, maxp

def recursiveUNLFind(unlList, c, depth=0, p=None, maxdepth=0, maxp=None):
    """Internal part of recursiveUNLSearch which doesn't change the
    selected position or call c.frame.bringToFront()"""

    if depth == 0:
        nds = c.rootPosition().self_and_siblings()
        unlList = [i.replace('--%3E', '-->') for i in unlList if i.strip()]
        # drop empty parts so "-->node name" works
    else:
        nds = p.children()

    for i in nds:

        if unlList[depth] == i.h:

            if depth+1 == len(unlList):  # found it
                #X moveToP(c, i)
                return True, maxdepth, i
            else:
                if maxdepth < depth+1:
                    maxdepth = depth+1
                    maxp = i.copy()
                found, maxdepth, maxp = g.recursiveUNLSearch(unlList, c, depth+1, i, maxdepth, maxp)
                if found:
                    return found, maxdepth, maxp
                # else keep looking through nds

    if depth == 0 and maxp:  # inexact match
        #X moveToP(c, maxp)
        g.es('Partial UNL match')

    return False, maxdepth, maxp
#@+node:ekr.20031218072017.3124: *3* g.sanitize_filename
def sanitize_filename(s):

    """Prepares string s to be a valid file name:

    - substitute '_' whitespace and characters used special path characters.
    - eliminate all other non-alphabetic characters.
    - strip leading and trailing whitespace.
    - return at most 128 characters."""

    result = ""
    for ch in s.strip():
        if ch in string.ascii_letters:
            result += ch
        elif ch in string.whitespace: # Translate whitespace.
            result += '_'
        elif ch in ('.','\\','/',':'): # Translate special path characters.
            result += '_'
    while 1:
        n = len(result)
        result = result.replace('__','_')
        if len(result) == n:
            break
    result = result.strip()
    return result [:128]
#@+node:ekr.20060328150113: *3* g.setGlobalOpenDir
def setGlobalOpenDir (fileName):

    if fileName:
        g.app.globalOpenDir = g.os_path_dirname(fileName)
        # g.es('current directory:',g.app.globalOpenDir)
#@+node:ekr.20031218072017.3125: *3* g.shortFileName & shortFilename
def shortFileName (fileName,n=None):
    
    if n is None or n < 1:
        return g.os_path_basename(fileName)
    else:
        return '\\'.join(fileName.split('\\')[-n:])

shortFilename = shortFileName
#@+node:ekr.20050104135720: *3* Used by tangle code & leoFileCommands
#@+node:ekr.20031218072017.1241: *4* g.update_file_if_changed
# This is part of the tangle code.

def update_file_if_changed(c,file_name,temp_name):

    """Compares two files.

    If they are different, we replace file_name with temp_name.
    Otherwise, we just delete temp_name. Both files should be closed."""

    if g.os_path_exists(file_name):
        if filecmp.cmp(temp_name, file_name):
            kind = 'unchanged'
            ok = g.utils_remove(temp_name)
        else:
            kind = '***updating'
            mode = g.utils_stat(file_name)
            ok = g.utils_rename(c,temp_name,file_name,mode)
    else:
        kind = 'creating'
        # 2010/02/04: g.utils_rename no longer calls
        # makeAllNonExistentDirectories
        head, tail = g.os_path_split(file_name)
        ok = True
        if head:
            ok = g.makeAllNonExistentDirectories(head,c=c)
        if ok:
            ok = g.utils_rename(c,temp_name,file_name)

    if ok:
        g.es('','%12s: %s' % (kind,file_name))
    else:
        g.error("rename failed: no file created!")
        g.es('',file_name," may be read-only or in use")
#@+node:ekr.20050104123726.3: *4* g.utils_remove
def utils_remove (fileName,verbose=True):

    try:
        os.remove(fileName)
        return True
    except Exception:
        if verbose:
            g.es("exception removing:",fileName)
            g.es_exception()
        return False
#@+node:ekr.20031218072017.1263: *4* g.utils_rename
def utils_rename (c,src,dst,verbose=True):

    '''Platform independent rename.'''

    # Don't call g.makeAllNonExistentDirectories.
    # It's not right to do this here!!

    # head, tail = g.os_path_split(dst)
    # if head: g.makeAllNonExistentDirectories(head,c=c)

    try:
        shutil.move(src,dst)
        return True
    except Exception:
        if verbose:
            g.error('exception renaming',src,'to',dst)
            g.es_exception(full=False)
        return False
#@+node:ekr.20050104124903: *4* g.utils_chmod
def utils_chmod (fileName,mode,verbose=True):

    if mode is None:
        return

    try:
        os.chmod(fileName,mode)
    except Exception:
        if verbose:
            g.es("exception in os.chmod",fileName)
            g.es_exception()
#@+node:ekr.20050104123726.4: *4* g.utils_stat
def utils_stat (fileName):

    '''Return the access mode of named file, removing any setuid, setgid, and sticky bits.'''

    try:
        mode = (os.stat(fileName))[0] & (7*8*8 + 7*8 + 7) # 0777
    except Exception:
        mode = None

    return mode
#@+node:ekr.20031218072017.1588: ** Garbage Collection
lastObjectCount = 0
lastObjectsDict = {}
lastTypesDict = {}
lastFunctionsDict = {}

#@+others
#@+node:ekr.20031218072017.1589: *3* clearAllIvars
def clearAllIvars (o):

    """Clear all ivars of o, a member of some class."""

    if o:
        o.__dict__.clear()
#@+node:ekr.20031218072017.1590: *3* collectGarbage
def collectGarbage():

    try:
        if not g.trace_gc_inited:
            g.enable_gc_debug()

        if g.trace_gc_verbose or g.trace_gc_calls:
            g.pr('collectGarbage:')

        gc.collect()
    except Exception:
        pass

    # Only init once, regardless of what happens.
    g.trace_gc_inited = True
#@+node:ekr.20060127162818: *3* enable_gc_debug
no_gc_message = False

def enable_gc_debug(event=None):

    if gc:
        if g.trace_gc_verbose:
            gc.set_debug(
                gc.DEBUG_STATS | # prints statistics.
                gc.DEBUG_LEAK | # Same as all below.
                gc.DEBUG_COLLECTABLE |
                gc.DEBUG_UNCOLLECTABLE |
                gc.DEBUG_INSTANCES |
                gc.DEBUG_OBJECTS |
                gc.DEBUG_SAVEALL
            )
        # else:
            # gc.set_debug(gc.DEBUG_STATS)
    elif not g.no_gc_message:
        g.no_gc_message = True
        g.error('can not import gc module')
#@+node:ekr.20031218072017.1592: *3* printGc
# Formerly called from unit tests.

def printGc(tag=None):

    if not g.trace_gc: return None

    tag = tag or g._callerName(n=2)

    printGcObjects(tag=tag)
    printGcRefs(tag=tag)

    if g.trace_gc_verbose:
        printGcVerbose(tag=tag)
#@+node:ekr.20031218072017.1593: *4* printGcRefs
def printGcRefs (tag=''):

    refs = gc.get_referrers(app.windowList[0])
    g.pr('-' * 30,tag)

    if g.trace_gc_verbose:
        g.pr("refs of", app.windowList[0])
        for ref in refs:
            g.pr(type(ref))
    else:
        g.pr("%d referers" % len(refs))
#@+node:ekr.20060202161935: *3* printGcAll
def printGcAll (tag=''):

    # Suppress warning about keywords arg not supported in sort.

    tag = tag or g._callerName(n=2)
    d = {} ; objects = gc.get_objects()
    if not g.unitTesting:
        g.pr('-' * 30)
        g.pr('%s: %d objects' % (tag,len(objects)))

    for obj in objects:
        t = type(obj)
        if t == 'instance':
            try: t = obj.__class__
            except Exception: pass
        # if type(obj) == type(()):
            # g.pr(id(obj),repr(obj))

        # 2011/02/28: Some types may not be hashable.
        try:
            d[t] = d.get(t,0) + 1
        except TypeError:
            d = {}

    if 1: # Sort by n
        items = list(d.items())
        items.sort(key=lambda x: x[1])
            # key is a function that extracts args.
        if not g.unitTesting:
            for z in items:
                g.pr('%40s %7d' % (z[0],z[1]))
    else: # Sort by type
        for t in sorted(d):
            g.pr('%40s %7d' % (t,d.get(t)))
#@+node:ekr.20060127164729.1: *3* printGcObjects   (printNewObjects=pno)
def printGcObjects(tag=''):

    '''Print newly allocated objects.'''

    tag = tag or g._callerName(n=2)
    global lastObjectCount

    try:
        n = len(gc.garbage)
        n2 = len(gc.get_objects())
        delta = n2-lastObjectCount
        if delta == 0: return
        lastObjectCount = n2

        #@+<< print number of each type of object >>
        #@+node:ekr.20040703054646: *4* << print number of each type of object >>
        global lastTypesDict
        typesDict = {}

        for obj in gc.get_objects():
            t = type(obj)
            if t == 'instance' and t != types.UnicodeType:
                try: t = obj.__class__
                except Exception: pass
            if t != types.FrameType:
                r = repr(t) # was type(obj) instead of repr(t)
                n = typesDict.get(r,0) 
                typesDict[r] = n + 1

        # Create the union of all the keys.
        keys = {}
        for key in lastTypesDict:
            if key not in typesDict:
                keys[key]=None

        empty = True
        for key in keys:
            n3 = lastTypesDict.get(key,0)
            n4 = typesDict.get(key,0)
            delta2 = n4-n3
            if delta2 != 0:
                empty = False
                break

        if not empty:
            g.pr('-' * 30)
            g.pr("%s: garbage: %d, objects: %d, delta: %d" % (tag,n,n2,delta))

            if 0:
                for key in sorted(keys):
                    n1 = lastTypesDict.get(key,0)
                    n2 = typesDict.get(key,0)
                    delta2 = n2-n1
                    if delta2 != 0:
                        g.pr("%+6d =%7d %s" % (delta2,n2,key))

        lastTypesDict = typesDict
        typesDict = {}
        #@-<< print number of each type of object >>
        if 0:
            #@+<< print added functions >>
            #@+node:ekr.20040703065638: *4* << print added functions >>
            global lastFunctionsDict
            funcDict = {}
            n = 0 # Don't print more than 50 objects.
            for obj in gc.get_objects():
                if type(obj) == types.FunctionType:
                    n += 1
            for obj in gc.get_objects():
                if type(obj) == types.FunctionType:
                    key = repr(obj) # Don't create a pointer to the object!
                    funcDict[key]=None 
                    if n < 50 and key not in lastFunctionsDict:
                        g.pr(obj)
                        args, varargs, varkw,defaults  = inspect.getargspec(obj)
                        g.pr("args", args)
                        if varargs: g.pr("varargs",varargs)
                        if varkw: g.pr("varkw",varkw)
                        if defaults:
                            g.pr("defaults...")
                            for s in defaults: g.pr(s)
            lastFunctionsDict = funcDict
            funcDict = {}
            #@-<< print added functions >>

    except Exception:
        traceback.print_exc()

printNewObjects = pno = printGcObjects

#@+node:ekr.20060205043324.1: *3* printGcSummary
def printGcSummary (tag=''):

    tag = tag or g._callerName(n=2)

    g.enable_gc_debug()

    try:
        n = len(gc.garbage)
        n2 = len(gc.get_objects())
        s = '%s: printGCSummary: garbage: %d, objects: %d' % (tag,n,n2)
        g.pr(s)
    except Exception:
        traceback.print_exc()
#@+node:ekr.20060127165509: *3* printGcVerbose
# WARNING: the id trick is not proper because newly allocated objects
#          can have the same address as old objets.

def printGcVerbose(tag=''):

    tag = tag or g._callerName(n=2)
    global lastObjectsDict
    objects = gc.get_objects()
    newObjects = [o for o in objects if id(o) not in lastObjectsDict]
    lastObjectsDict = {}
    for o in objects:
        lastObjectsDict[id(o)]=o

    dicts = 0 ; seqs = 0

    i = 0 ; n = len(newObjects)
    while i < 100 and i < n:
        o = newObjects[i]
        if type(o) == type({}): dicts += 1
        elif type(o) in (type(()),type([])):
            #g.pr(id(o),repr(o))
            seqs += 1
        #else:
        #    g.pr(o)
        i += 1
    g.pr('=' * 40)
    g.pr('dicts: %d, sequences: %d' % (dicts,seqs))
    g.pr("%s: %d new, %d total objects" % (tag,len(newObjects),len(objects)))
    g.pr('-' * 40)
#@-others
#@+node:ekr.20031218072017.3139: ** Hooks & plugins (leoGlobals)
#@+node:ekr.20031218072017.1315: *3* idle time functions (leoGlobals)
#@+node:EKR.20040602125018: *4* enableIdleTimeHook
#@+at Enables the "idle" hook.
# After enableIdleTimeHook is called, Leo will call the "idle" hook
# approximately every g.idleTimeDelay milliseconds.
#@@c

def enableIdleTimeHook(idleTimeDelay=500):

    # g.trace(idleTimeDelay)

    if not g.app.idleTimeHook:
        # g.trace('start idle-time hook: %d msec.' % idleTimeDelay)
        # Start idle-time processing only after the first idle-time event.
        g.app.gui.setIdleTimeHook(g.idleTimeHookHandler)
        g.app.afterHandler = g.idleTimeHookHandler

    # 1/4/05: Always update these.
    g.app.idleTimeHook = True
    g.app.idleTimeDelay = idleTimeDelay # Delay in msec.
#@+node:EKR.20040602125018.1: *4* disableIdleTimeHook
# Disables the "idle" hook.
def disableIdleTimeHook():

    g.app.idleTimeHook = False
#@+node:EKR.20040602125018.2: *4* idleTimeHookHandler
# An internal routine used to dispatch the "idle" hook.
trace_count = 0

def idleTimeHookHandler(*args,**keys):

    trace = False and not g.unitTesting

    if trace: # Do not use g.trace here!
        global trace_count ; trace_count += 1
        if 0:
            g.pr('idleTimeHookHandler',trace_count)
        else:
            if trace_count % 10 == 0:
                for z in g.app.windowList:
                    c = z.c
                    g.pr("idleTimeHookHandler",trace_count,c.shortFileName())

    # New for Python 2.3: may be called during shutdown.
    if g.app.killed: return

    for z in g.app.windowList:
        c = z.c
        # Do NOT compute c.currentPosition.
        # This would be a MAJOR leak of positions.
        g.doHook("idle",c=c)

    # Requeue this routine after g.app.idleTimeDelay msec.
    # (This delay is set by g.enableIdleTimeHook.)
    # Faster requeues overload the system.
    if g.app.idleTimeHook:
        g.app.gui.setIdleTimeHookAfterDelay(g.idleTimeHookHandler)
        g.app.afterHandler = g.idleTimeHookHandler
    else:
        g.app.afterHandler = None
#@+node:ekr.20101028131948.5860: *3* g.act_on_node
def dummy_act_on_node(c,p,event):
    pass

# This dummy definition keeps pylint happy.
# Plugins can change this.
act_on_node = dummy_act_on_node
#@+node:ekr.20031218072017.1596: *3* g.doHook
#@+at This global function calls a hook routine.  Hooks are identified by the tag param.
# Returns the value returned by the hook routine, or None if the there is an exception.
# 
# We look for a hook routine in three places:
# 1. c.hookFunction
# 2. app.hookFunction
# 3. leoPlugins.doPlugins()
# We set app.hookError on all exceptions.  Scripts may reset app.hookError to try again.
#@@c

def doHook(tag,*args,**keywords):

    trace = False ; verbose = False

    if g.app.killed or g.app.hookError: # or (g.app.gui and g.app.gui.isNullGui):
        return None

    if args:
        # A minor error in Leo's core.
        g.pr("***ignoring args param.  tag = %s" % tag)

    if not g.app.config.use_plugins:

        if tag in ('open0','start1'):
            g.warning("Plugins disabled: use_plugins is 0 in a leoSettings.leo file.")
        return None

    # Get the hook handler function.  Usually this is doPlugins.
    c = keywords.get("c")
    f = (c and c.hookFunction) or g.app.hookFunction

    if trace and (verbose or tag != 'idle'):
        g.trace('tag',tag,'f',f and f.__name__)

    if not f:
        g.app.hookFunction = f = g.app.pluginsController.doPlugins

    try:
        # Pass the hook to the hook handler.
        # g.pr('doHook',f.__name__,keywords.get('c'))
        return f(tag,keywords)
    except Exception:
        g.es_exception()
        g.app.hookError = True # Supress this function.
        g.app.idleTimeHook = False # Supress idle-time hook
        return None # No return value
#@+node:ville.20090521164644.5924: *3* g.command (decorator for creating global commands)
class command:
    """ Decorator to create global commands """
    def __init__(self, name, **kwargs):
        """ Registration for command 'name'

        kwargs reserved for future use (shortcut, button, ...?)

        """
        self.name = name
        self.args = kwargs

    def __call__(self,func):
        # register command for all future commanders
        if g and g.app:
            g.app.global_commands_dict[self.name] = func
            # ditto for all current commanders
            for co in g.app.commanders():
                co.k.registerCommand(self.name,shortcut = None, func = func, pane='all',verbose=False)        
        else:
            g.error('@command decorator inside leoGlobals.py')
        return func


#@+node:ville.20120502221057.7500: *3* g.childrenModifiedSet, g.contentModifiedSet
childrenModifiedSet = set()
contentModifiedSet = set()
#@+node:ekr.20100910075900.5950: *3* Wrappers for g.app.pluginController methods
# Important: we can not define g.pc here!

#@+node:ekr.20100910075900.5951: *4* Loading & registration
def loadOnePlugin (pluginName,verbose=False):
    pc = g.app.pluginsController
    return pc.loadOnePlugin(pluginName,verbose=verbose)

def registerExclusiveHandler(tags,fn):
    pc = g.app.pluginsController
    return pc.registerExclusiveHandler(tags,fn)

def registerHandler (tags,fn):
    pc = g.app.pluginsController
    return pc.registerHandler(tags,fn)

def plugin_signon(module_name,verbose=False):
    pc = g.app.pluginsController
    return pc.plugin_signon(module_name,verbose)

def unloadOnePlugin (moduleOrFileName,verbose=False):
    pc = g.app.pluginsController
    return pc.unloadOnePlugin(moduleOrFileName,verbose)

def unregisterHandler (tags,fn):
    pc = g.app.pluginsController
    return pc.unregisterHandler(tags,fn)
#@+node:ekr.20100910075900.5952: *4* Information
def getHandlersForTag(tags):
    pc = g.app.pluginsController
    return pc.getHandlersForTag(tags)

def getLoadedPlugins():
    pc = g.app.pluginsController
    return pc.getLoadedPlugins()

def getPluginModule(moduleName):
    pc = g.app.pluginsController
    return pc.getPluginModule(moduleName)

def pluginIsLoaded(fn):
    pc = g.app.pluginsController
    return pc.isLoaded(fn)

#@+node:ekr.20031218072017.3145: ** Most common functions... (leoGlobals.py)
# These are guaranteed always to exist for scripts.
#@+node:ekr.20120928142052.10116: *3* g.actualColor
def actualColor(color):

    if not g.app.log:
        return color

    c = g.app.log.c
    d = {
        'black':'log_text_foreground_color',
        'blue': 'log_warning_color',
        'red':  'log_error_color',
    }

    setting = d.get(color)

    # Bug fix: 2012/10/17: c.config may not yet exist.
    if c and c.config and setting:
        color2 = c.config.getColor(setting)
    else:
        color2 = color

    # g.trace(color,color2)
    return color2
#@+node:ekr.20031218072017.3147: *3* g.choose (deprecated)
def choose(cond, a, b): # warning: evaluates all arguments

    if cond: return a
    else: return b
#@+node:ekr.20080821073134.2: *3* g.doKeywordArgs
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
#@+node:ekr.20031218072017.1474: *3* g.enl, ecnl & ecnls
def ecnl(tabName='Log'):
    g.ecnls(1,tabName)

def ecnls(n,tabName='Log'):
    log = app.log
    if log and not log.isNull:
        while log.newlines < n:
            g.enl(tabName)

def enl(tabName='Log'):
    log = app.log
    if log and not log.isNull:
        log.newlines += 1
        log.putnl(tabName)
#@+node:ekr.20100914094836.5892: *3* g.error, g.note, g.warning, g.red, g.blue
def blue (*args,**keys):
    g.es_print(color=g.actualColor('blue'),*args,**keys)

def error (*args,**keys):
    g.es_print(color=g.actualColor('red'),*args,**keys)

def note (*args,**keys):
    g.es_print(color=g.actualColor('black'),*args,**keys)

def red (*args,**keys):
    g.es_print(color=g.actualColor('red'),*args,**keys)

def warning (*args,**keys):
    g.es_print(color=g.actualColor('blue'),*args,**keys)
#@+node:ekr.20070626132332: *3* g.es
def es(*args,**keys):

    '''Put all non-keyword args to the log pane.
    The first, third, fifth, etc. arg translated by g.translateString.
    Supports color, comma, newline, spaces and tabName keyword arguments.
    '''

    trace = False

    if not app or app.killed: return
    log = app.log

    if trace: # Effective for debugging.
        print()
        print('***es',args,keys)
        print('***es','logInited',app.logInited,'log',log and id(log))
        print('***es',g.callers())

    # Compute the effective args.
    d = {
        'color':None,
        'commas':False,
        'newline':True,
        'spaces':True,
        'tabName':'Log',
    }
    d = g.doKeywordArgs(keys,d)
    color = d.get('color')
    if color == 'suppress': return # New in 4.3.
    elif log and color is None:
        color = g.actualColor('black')
        
    color = g.actualColor(color)
        
    tabName = d.get('tabName') or 'Log'
    newline = d.get('newline')
    s = g.translateArgs(args,d)

    if app.batchMode:
        if app.log:
            app.log.put(s)
    elif g.unitTesting:
        if log and not log.isNull:
            # This makes the output of unit tests match the output of scripts.
            # s = g.toEncodedString(s,'ascii')
            g.pr(s,newline=newline)
    elif log and app.logInited:
        log.put(s,color=color,tabName=tabName)
        for ch in s:
            if ch == '\n': log.newlines += 1
            else: log.newlines = 0
        if newline:
            g.ecnl(tabName=tabName) # only valid here
    # 2012/05/20: Don't do this.
    # elif app.logInited:
        # print(s.rstrip()) # Happens only rarely.
    elif newline:
        app.logWaiting.append((s+'\n',color),)
    else:
        app.logWaiting.append((s,color),)
#@+node:ekr.20050707064040: *3* g.es_print
# see: http://www.diveintopython.org/xml_processing/unicode.html

def es_print(*args,**keys):

    '''Print all non-keyword args, and put them to the log pane.
    The first, third, fifth, etc. arg translated by g.translateString.
    Supports color, comma, newline, spaces and tabName keyword arguments.
    '''

    g.pr(*args,**keys)

    if not g.app.unitTesting:
        g.es(*args,**keys)
#@+node:ekr.20050707065530: *3* g.es_trace
def es_trace(*args,**keys):

    if args:
        try:
            s = args[0]
            g.trace(g.toEncodedString(s,'ascii'))
        except Exception:
            pass

    g.es(*args,**keys)
#@+node:ekr.20100126062623.6240: *3* g.internalError
def internalError (*args):

    callers = g.callers(5).split(',')
    caller = callers[-1]
    g.error('\nInternal Leo error in',caller)
    g.es_print(*args)
    g.es_print('Called from',','.join(callers[:-1]))
#@+node:ekr.20090128083459.82: *3* g.posList
class posList(list):
    #@+<< docstring for posList >>
    #@+node:ekr.20090130114732.2: *4* << docstring for posList >>
    '''A subclass of list for creating and selecting lists of positions.

        This is deprecated, use leoNodes.poslist instead!

        aList = g.posList(c)
            # Creates a posList containing all positions in c.

        aList = g.posList(c,aList2)
            # Creates a posList from aList2.

        aList2 = aList.select(pattern,regex=False,removeClones=True)
            # Creates a posList containing all positions p in aList
            # such that p.h matches the pattern.
            # The pattern is a regular expression if regex is True.
            # if removeClones is True, all positions p2 are removed
            # if a position p is already in the list and p2.v == p.v.

        aList.dump(sort=False,verbose=False)
            # Prints all positions in aList, sorted if sort is True.
            # Prints p.h, or repr(p) if verbose is True.
    '''
    #@-<< docstring for posList >>
    def __init__ (self,c,aList=None):
        self.c = c
        list.__init__(self) # Init the base class
        if aList is None:
            for p in c.all_positions():
                self.append(p.copy())
        else:
            for p in aList:
                self.append(p.copy())

    def dump (self,sort=False,verbose=False):
        if verbose: return g.listToString(self,sort=sort)
        else: return g.listToString([p.h for p in self],sort=sort)

    def select(self,pat,regex=False,removeClones=True):
        '''Return a new posList containing all positions
        in self that match the given pattern.'''
        c = self.c ; aList = []
        if regex:
            for p in self:
                if re.match(pat,p.h):
                    aList.append(p.copy())
        else:
            for p in self:
                if p.h.find(pat) != -1:
                    aList.append(p.copy())
        if removeClones:
            aList = self.removeClones(aList)
        return posList(c,aList)

    def removeClones(self,aList):
        seen = {} ; aList2 = []
        for p in aList:
            if p.v not in seen:
                seen[p.v] = p.v
                aList2.append(p)
        return aList2
#@+node:ekr.20080710101653.1: *3* g.pr
# see: http://www.diveintopython.org/xml_processing/unicode.html

pr_warning_given = False

def pr(*args,**keys):

    '''Print all non-keyword args, and put them to the log pane.
    The first, third, fifth, etc. arg translated by g.translateString.
    Supports color, comma, newline, spaces and tabName keyword arguments.
    '''

    print_immediately = False or not app # True: good for debugging.

    # Compute the effective args.
    d = {'commas':False,'newline':True,'spaces':True}
    d = doKeywordArgs(keys,d)
    newline = d.get('newline')

    if sys.platform.lower().startswith('win'):
        encoding = 'ascii' # 2011/11/9.
    elif hasattr(sys.stdout,'encoding') and sys.stdout.encoding:
        # sys.stdout is a TextIOWrapper with a particular encoding.
        encoding = sys.stdout.encoding
    else:
        encoding = 'utf-8'

    s = translateArgs(args,d) # Translates everything to unicode.

    # Add a newline unless we are going to queue the message.
    if newline and (print_immediately or app and app.logInited):
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

    if print_immediately:
        # Good for debugging: prints messages immediately.
        sys.stdout.write(s2)
    else:
        assert app
        # Good for production: queues 'reading settings' until after signon.
        if app.logInited and sys.stdout: # Bug fix: 2012/11/13.
            sys.stdout.write(s2)
        else:
            app.printWaiting.append(s2)
#@+node:ekr.20031218072017.2317: *3* g.trace
def trace (*args,**keys):

    # Don't use g here: in standalone mode g is a nullObject!

    # Compute the effective args.
    d = {'align':0,'before':'','newline':True,'caller_level':1}
    d = doKeywordArgs(keys,d)
    newline = d.get('newline')
    align = d.get('align',0)
    caller_level = d.get('caller_level',1)

    # Compute the caller name.
    try: # get the function name from the call stack.
        f1 = sys._getframe(caller_level) # The stack frame, one level up.
        code1 = f1.f_code # The code object
        name = code1.co_name # The code name
    except Exception:
        name = g.shortFileName(__file__)
    if name == '<module>':
        name = g.shortFileName(__file__)
    if name.endswith('.pyc'):
        name = name[:-1]

    # Pad the caller name.
    if align != 0 and len(name) < abs(align):
        pad = ' ' * (abs(align) - len(name))
        if align > 0: name = name + pad
        else:         name = pad + name

    # Munge *args into s.
    # print ('g.trace:args...')
    # for z in args: print (g.isString(z),repr(z))
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

    s = d.get('before')+''.join(result)
    pr(s,newline=newline)
#@+node:ekr.20080220111323: *3* g.translateArgs
console_encoding = None

def translateArgs(args,d):

    '''Return the concatenation of s and all args,

    with odd args translated.'''

    global console_encoding

    if not console_encoding:
        e = sys.getdefaultencoding()
        console_encoding = isValidEncoding(e) and e or 'utf-8'
        # print 'translateArgs',console_encoding

    result = [] ; n = 0 ; spaces = d.get('spaces')
    for arg in args:
        n += 1

        # print('g.translateArgs: arg',arg,type(arg),g.isString(arg),'will trans',(n%2)==1)

        # First, convert to unicode.
        if type(arg) == type('a'):
            arg = toUnicode(arg,console_encoding)

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
#@+node:ekr.20060810095921: *3* g.translateString & tr
def translateString (s):

    '''Return the translated text of s.'''

    if isPython3:
        if not isString(s):
            s = str(s,'utf-8')
        if app and app.translateToUpperCase:
            s = s.upper()
        else:
            s = gettext.gettext(s)
        return s
    else:
        if app and app.translateToUpperCase:
            return s.upper()
        else:
            return gettext.gettext(s)

tr = translateString
#@+node:ekr.20031218072017.3150: *3* g.windows
def windows():
    return app and app.windowList
#@+node:ekr.20031218072017.2145: ** os.path wrappers (leoGlobals.py)
#@+at Note: all these methods return Unicode strings. It is up to the user to
# convert to an encoded string as needed, say when opening a file.
#@+node:ekr.20031218072017.2146: *3* g.os_path_abspath
def os_path_abspath(path):

    """Convert a path to an absolute path."""

    path = g.toUnicodeFileEncoding(path)

    path = os.path.abspath(path)

    path = g.toUnicodeFileEncoding(path)

    return path
#@+node:ekr.20031218072017.2147: *3* g.os_path_basename
def os_path_basename(path):

    """Return the second half of the pair returned by split(path)."""

    path = g.toUnicodeFileEncoding(path)

    path = os.path.basename(path)

    path = g.toUnicodeFileEncoding(path)

    return path
#@+node:ekr.20031218072017.2148: *3* g.os_path_dirname
def os_path_dirname(path):

    """Return the first half of the pair returned by split(path)."""

    path = g.toUnicodeFileEncoding(path)

    path = os.path.dirname(path)

    path = g.toUnicodeFileEncoding(path)

    return path
#@+node:ekr.20031218072017.2149: *3* g.os_path_exists
def os_path_exists(path):

    """Return True if path exists."""

    path = g.toUnicodeFileEncoding(path)

    return os.path.exists(path)
#@+node:ekr.20080922124033.6: *3* g.os_path_expandExpression
def os_path_expandExpression (s,**keys):

    '''Expand {{anExpression}} in c's context.'''

    trace = False
    c = keys.get('c')
    if not c:
        g.trace('can not happen: no c',g.callers())
        return s
    if not s:
        if trace: g.trace('no s')
        return ''
    i = s.find('{{')
    j = s.find('}}')
    if -1 < i < j:
        exp = s[i+2:j].strip()
        if exp:
            try:
                p = c.p
                d = {'c':c,'g':g,'p':p,'os':os,'sys':sys,}
                val = eval(exp,d)
                s = s[:i] + str(val) + s[j+2:]
                if trace: g.trace('returns',s)
            except Exception:
                g.trace(g.callers())
                g.es_exception(full=True, c=c)
    return s
#@+node:ekr.20080921060401.13: *3* g.os_path_expanduser
def os_path_expanduser(path):

    """wrap os.path.expanduser"""

    path = g.toUnicodeFileEncoding(path)

    result = os.path.normpath(os.path.expanduser(path))

    return result
#@+node:ekr.20080921060401.14: *3* g.os_path_finalize & os_path_finalize_join
def os_path_finalize (path,**keys):

    '''
    Expand '~', then return os.path.normpath, os.path.abspath of the path.

    There is no corresponding os.path method'''

    c = keys.get('c')

    if c: path = g.os_path_expandExpression(path,**keys)

    path = g.os_path_expanduser(path)
    path = os.path.abspath(path)
    path = os.path.normpath(path)
    # calling os.path.realpath here would cause problems in some situations.
    return path

def os_path_finalize_join (*args,**keys):

    '''Do os.path.join(*args), then finalize the result.'''

    c = keys.get('c')

    if c:
        args = [g.os_path_expandExpression(z,**keys)
            for z in args if z]

    return os.path.normpath(os.path.abspath(
        g.os_path_join(*args,**keys))) # Handles expanduser
#@+node:ekr.20031218072017.2150: *3* g.os_path_getmtime
def os_path_getmtime(path):

    """Return the modification time of path."""

    path = g.toUnicodeFileEncoding(path)

    return os.path.getmtime(path)
#@+node:ekr.20080729142651.2: *3* g.os_path_getsize
def os_path_getsize (path):

    '''Return the size of path.'''

    path = g.toUnicodeFileEncoding(path)

    return os.path.getsize(path)
#@+node:ekr.20031218072017.2151: *3* g.os_path_isabs
def os_path_isabs(path):

    """Return True if path is an absolute path."""

    path = g.toUnicodeFileEncoding(path)

    return os.path.isabs(path)
#@+node:ekr.20031218072017.2152: *3* g.os_path_isdir
def os_path_isdir(path):

    """Return True if the path is a directory."""

    path = g.toUnicodeFileEncoding(path)

    return os.path.isdir(path)
#@+node:ekr.20031218072017.2153: *3* g.os_path_isfile
def os_path_isfile(path):

    """Return True if path is a file."""

    path = g.toUnicodeFileEncoding(path)

    return os.path.isfile(path)
#@+node:ekr.20031218072017.2154: *3* g.os_path_join
def os_path_join(*args,**keys):

    trace = False and not g.unitTesting
    c = keys.get('c')

    uargs = [g.toUnicodeFileEncoding(arg) for arg in args]

    if trace: g.trace('1',uargs)

    # Note:  This is exactly the same convention as used by getBaseDirectory.
    if uargs and uargs[0] == '!!':
        uargs[0] = g.app.loadDir
    elif uargs and uargs[0] == '.':
        c = keys.get('c')
        if c and c.openDirectory:
            uargs[0] = c.openDirectory
            # g.trace(c.openDirectory)

    uargs = [g.os_path_expanduser(z) for z in uargs if z]

    if trace: g.trace('2',uargs)

    path = os.path.join(*uargs)

    if trace: g.trace('3',path)

    # May not be needed on some Pythons.
    path = g.toUnicodeFileEncoding(path)
    return path
#@+node:ekr.20031218072017.2156: *3* g.os_path_normcase
def os_path_normcase(path):

    """Normalize the path's case."""

    path = g.toUnicodeFileEncoding(path)

    path = os.path.normcase(path)

    path = g.toUnicodeFileEncoding(path)

    return path
#@+node:ekr.20031218072017.2157: *3* g.os_path_normpath
def os_path_normpath(path):

    """Normalize the path."""

    path = g.toUnicodeFileEncoding(path)

    path = os.path.normpath(path)

    path = g.toUnicodeFileEncoding(path)

    return path
#@+node:ekr.20080605064555.2: *3* g.os_path_realpath
def os_path_realpath(path):
    
    '''Return the canonical path of the specified filename, eliminating any
    symbolic links encountered in the path (if they are supported by the
    operating system).
    '''

    path = g.toUnicodeFileEncoding(path)
    path = os.path.realpath(path)
    path = g.toUnicodeFileEncoding(path)
    return path
#@+node:ekr.20031218072017.2158: *3* g.os_path_split
def os_path_split(path):

    path = g.toUnicodeFileEncoding(path)

    head,tail = os.path.split(path)

    head = g.toUnicodeFileEncoding(head)
    tail = g.toUnicodeFileEncoding(tail)

    return head,tail
#@+node:ekr.20031218072017.2159: *3* g.os_path_splitext
def os_path_splitext(path):

    path = g.toUnicodeFileEncoding(path)

    head,tail = os.path.splitext(path)

    head = g.toUnicodeFileEncoding(head)
    tail = g.toUnicodeFileEncoding(tail)

    return head,tail
#@+node:ekr.20090829140232.6036: *3* g.os_startfile
def os_startfile(fname):

    if g.unitTesting:
        g.app.unitTestDict['os_startfile']=fname
        return

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
            # Fix bug 1226358: File URL's are broken on MacOS:
            # use fname, not quoted_fname, as the argument to subprocess.call.
            subprocess.call(['open',fname])
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
#@+node:ekr.20031218072017.2160: *3* g.toUnicodeFileEncoding
def toUnicodeFileEncoding(path):

    if path: path = path.replace('\\', os.sep)

    # Yes, this is correct.  All os_path_x functions return Unicode strings.
    return g.toUnicode(path)
#@+node:ekr.20031218072017.3151: ** Scanning... (leoGlobals.py)
#@+node:ekr.20031218072017.3156: *3* scanError
# It is dubious to bump the Tangle error count here, but it really doesn't hurt.

def scanError(s):

    '''Bump the error count in the tangle command.'''

    # New in Leo 4.4b1: just set this global.
    g.app.scanErrors +=1
    g.es('',s)
#@+node:ekr.20031218072017.3157: *3* scanf
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
    # g.trace("scanf returns:",result)
    return result

if 0: # testing
    g.scanf("1.0","%d.%d",)
#@+node:ekr.20031218072017.3158: *3* Scanners: calling scanError
#@+at These scanners all call g.scanError() directly or indirectly, so they
# will call g.es if they find an error. g.scanError() also bumps
# c.tangleCommands.errors, which is harmless if we aren't tangling, and
# useful if we are.
# 
# These routines are called by the Import routines and the Tangle routines.
#@+node:ekr.20031218072017.3159: *4* skip_block_comment
# Scans past a block comment (an old_style C comment).

def skip_block_comment (s,i):

    assert(g.match(s,i,"/*"))
    j = i ; i += 2 ; n = len(s)

    k = s.find("*/",i)
    if k == -1:
        g.scanError("Run on block comment: " + s[j:i])
        return n
    else: return k + 2
#@+node:ekr.20031218072017.3160: *4* skip_braces
#@+at This code is called only from the import logic, so we are allowed to
# try some tricks. In particular, we assume all braces are matched in
# #if blocks.
#@@c

def skip_braces(s,i):

    '''Skips from the opening to the matching brace.

    If no matching is found i is set to len(s)'''

    # start = g.get_line(s,i)
    assert(g.match(s,i,'{'))
    level = 0 ; n = len(s)
    while i < n:
        c = s[i]
        if c == '{':
            level += 1 ; i += 1
        elif c == '}':
            level -= 1
            if level <= 0: return i
            i += 1
        elif c == '\'' or c == '"': i = g.skip_string(s,i)
        elif g.match(s,i,'//'): i = g.skip_to_end_of_line(s,i)
        elif g.match(s,i,'/*'): i = g.skip_block_comment(s,i)
        # 7/29/02: be more careful handling conditional code.
        elif g.match_word(s,i,"#if") or g.match_word(s,i,"#ifdef") or g.match_word(s,i,"#ifndef"):
            i,delta = g.skip_pp_if(s,i)
            level += delta
        else: i += 1
    return i
#@+node:ekr.20031218072017.3161: *4* skip_php_braces (no longer used)
#@+at 08-SEP-2002 DTHEIN: Added for PHP import support
# Skips from the opening to the matching . If no matching is found i is set to len(s).
# 
# This code is called only from the import logic, and only for PHP imports.
#@@c

def skip_php_braces(s,i):

    # start = g.get_line(s,i)
    assert(g.match(s,i,'{'))
    level = 0 ; n = len(s)
    while i < n:
        c = s[i]
        if c == '{':
            level += 1 ; i += 1
        elif c == '}':
            level -= 1
            if level <= 0: return i + 1
            i += 1
        elif c == '\'' or c == '"': i = g.skip_string(s,i)
        elif g.match(s,i,"<<<"): i = g.skip_heredoc_string(s,i)
        elif g.match(s,i,'//') or g.match(s,i,'#'): i = g.skip_to_end_of_line(s,i)
        elif g.match(s,i,'/*'): i = g.skip_block_comment(s,i)
        else: i += 1
    return i
#@+node:ekr.20031218072017.3162: *4* skip_parens
def skip_parens(s,i):

    '''Skips from the opening ( to the matching ).

    If no matching is found i is set to len(s)'''

    level = 0 ; n = len(s)
    assert(g.match(s,i,'('))
    while i < n:
        c = s[i]
        if c == '(':
            level += 1 ; i += 1
        elif c == ')':
            level -= 1
            if level <= 0:  return i
            i += 1
        elif c == '\'' or c == '"': i = g.skip_string(s,i)
        elif g.match(s,i,"//"): i = g.skip_to_end_of_line(s,i)
        elif g.match(s,i,"/*"): i = g.skip_block_comment(s,i)
        else: i += 1
    return i
#@+node:ekr.20031218072017.3163: *4* skip_pascal_begin_end
def skip_pascal_begin_end(s,i):

    '''Skips from begin to matching end.
    If found, i points to the end. Otherwise, i >= len(s)
    The end keyword matches begin, case, class, record, and try.'''

    assert(g.match_c_word(s,i,"begin"))
    level = 1 ; i = g.skip_c_id(s,i) # Skip the opening begin.
    while i < len(s):
        ch = s[i]
        if ch =='{' : i = g.skip_pascal_braces(s,i)
        elif ch =='"' or ch == '\'': i = g.skip_pascal_string(s,i)
        elif g.match(s,i,"//"): i = g.skip_line(s,i)
        elif g.match(s,i,"(*"): i = g.skip_pascal_block_comment(s,i)
        elif g.match_c_word(s,i,"end"):
            level -= 1
            if level == 0:
                # lines = s[i1:i+3] ; g.trace('\n' + lines + '\n')
                return i
            else: i = g.skip_c_id(s,i)
        elif g.is_c_id(ch):
            j = i ; i = g.skip_c_id(s,i) ; name = s[j:i]
            if name in ["begin", "case", "class", "record", "try"]:
                level += 1
        else: i += 1
    return i
#@+node:ekr.20031218072017.3164: *4* skip_pascal_block_comment
# Scans past a pascal comment delimited by (* and *).

def skip_pascal_block_comment(s,i):

    j = i
    assert(g.match(s,i,"(*"))
    i = s.find("*)",i)
    if i > -1: return i + 2
    else:
        g.scanError("Run on comment" + s[j:i])
        return len(s)
#@+node:ekr.20031218072017.3165: *4* skip_pascal_string : called by tangle
def skip_pascal_string(s,i):

    j = i ; delim = s[i] ; i += 1
    assert(delim == '"' or delim == '\'')

    while i < len(s):
        if s[i] == delim:
            return i + 1
        else: i += 1

    g.scanError("Run on string: " + s[j:i])
    return i
#@+node:ekr.20031218072017.3166: *4* skip_heredoc_string : called by php import (Dave Hein)
#@+at 08-SEP-2002 DTHEIN:  added function skip_heredoc_string
# A heredoc string in PHP looks like:
# 
#   <<<EOS
#   This is my string.
#   It is mine. I own it.
#   No one else has it.
#   EOS
# 
# It begins with <<< plus a token (naming same as PHP variable names).
# It ends with the token on a line by itself (must start in first position.
# 
#@@c
def skip_heredoc_string(s,i):

    j = i
    assert(g.match(s,i,"<<<"))
    m = re.match("\<\<\<([a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*)", s[i:])
    if (None == m):
        i += 3
        return i

    # 14-SEP-2002 DTHEIN: needed to add \n to find word, not just string
    delim = m.group(1) + '\n' 

    i = g.skip_line(s,i) # 14-SEP-2002 DTHEIN: look after \n, not before
    n = len(s)
    while i < n and not g.match(s,i,delim):
        i = g.skip_line(s,i) # 14-SEP-2002 DTHEIN: move past \n

    if i >= n:
        g.scanError("Run on string: " + s[j:i])
    elif g.match(s,i,delim):
        i += len(delim)
    return i
#@+node:ekr.20031218072017.3167: *4* skip_pp_directive
# Now handles continuation lines and block comments.

def skip_pp_directive(s,i):

    while i < len(s):
        if g.is_nl(s,i):
            if g.escaped(s,i): i = g.skip_nl(s,i)
            else: break
        elif g.match(s,i,"//"): i = g.skip_to_end_of_line(s,i)
        elif g.match(s,i,"/*"): i = g.skip_block_comment(s,i)
        else: i += 1
    return i
#@+node:ekr.20031218072017.3168: *4* skip_pp_if
# Skips an entire if or if def statement, including any nested statements.

def skip_pp_if(s,i):

    start_line = g.get_line(s,i) # used for error messages.
    # g.trace(start_line)

    assert(
        g.match_word(s,i,"#if") or
        g.match_word(s,i,"#ifdef") or
        g.match_word(s,i,"#ifndef"))

    i = g.skip_line(s,i)
    i,delta1 = g.skip_pp_part(s,i)
    i = g.skip_ws(s,i)
    if g.match_word(s,i,"#else"):
        i = g.skip_line(s,i)
        i = g.skip_ws(s,i)
        i,delta2 = g.skip_pp_part(s,i)
        if delta1 != delta2:
            g.es("#if and #else parts have different braces:",start_line)
    i = g.skip_ws(s,i)
    if g.match_word(s,i,"#endif"):
        i = g.skip_line(s,i)
    else:
        g.es("no matching #endif:",start_line)

    # g.trace(delta1,start_line)
    return i,delta1
#@+node:ekr.20031218072017.3169: *4* skip_pp_part
# Skip to an #else or #endif.  The caller has eaten the #if, #ifdef, #ifndef or #else

def skip_pp_part(s,i):

    # g.trace(g.get_line(s,i))

    delta = 0
    while i < len(s):
        c = s[i]
        if 0:
            if c == '\n':
                g.trace(delta,g.get_line(s,i))
        if g.match_word(s,i,"#if") or g.match_word(s,i,"#ifdef") or g.match_word(s,i,"#ifndef"):
            i,delta1 = g.skip_pp_if(s,i)
            delta += delta1
        elif g.match_word(s,i,"#else") or g.match_word(s,i,"#endif"):
            return i,delta
        elif c == '\'' or c == '"': i = g.skip_string(s,i)
        elif c == '{':
            delta += 1 ; i += 1
        elif c == '}':
            delta -= 1 ; i += 1
        elif g.match(s,i,"//"): i = g.skip_line(s,i)
        elif g.match(s,i,"/*"): i = g.skip_block_comment(s,i)
        else: i += 1
    return i,delta
#@+node:ekr.20031218072017.3170: *4* skip_python_string
def skip_python_string(s,i,verbose=True):

    if g.match(s,i,"'''") or g.match(s,i,'"""'):
        j = i ; delim = s[i]*3 ; i += 3
        k = s.find(delim,i)
        if k > -1: return k+3
        if verbose:
            g.scanError("Run on triple quoted string: " + s[j:i])
        return len(s)
    else:
        # 2013/09/08: honor the verbose argument.
        return g.skip_string(s,i,verbose=verbose)
#@+node:ekr.20031218072017.2369: *4* skip_string (leoGlobals)
def skip_string(s,i,verbose=True):

    '''Scan forward to the end of a string.
    New in Leo 4.4.2 final: give error only if verbose is True'''

    j = i ; delim = s[i] ; i += 1
    assert(delim == '"' or delim == '\'')

    n = len(s)
    while i < n and s[i] != delim:
        if s[i] == '\\' : i += 2
        else: i += 1

    if i >= n:
        if verbose:
            g.scanError("Run on string: " + s[j:i])
    elif s[i] == delim:
        i += 1

    # g.trace(s[j:i])
    return i
#@+node:ekr.20031218072017.3171: *4* skip_to_semicolon
# Skips to the next semicolon that is not in a comment or a string.

def skip_to_semicolon(s,i):

    n = len(s)
    while i < n:
        c = s[i]
        if c == ';': return i
        elif c == '\'' or c == '"' : i = g.skip_string(s,i)
        elif g.match(s,i,"//"): i = g.skip_to_end_of_line(s,i)
        elif g.match(s,i,"/*"): i = g.skip_block_comment(s,i)
        else: i += 1
    return i
#@+node:ekr.20031218072017.3172: *4* skip_typedef
def skip_typedef(s,i):

    n = len(s)
    while i < n and g.is_c_id(s[i]):
        i = g.skip_c_id(s,i)
        i = g.skip_ws_and_nl(s,i)
    if g.match(s,i,'{'):
        i = g.skip_braces(s,i)
        i = g.skip_to_semicolon(s,i)
    return i
#@+node:ekr.20031218072017.3173: *3* Scanners: no error messages
#@+node:ekr.20031218072017.3174: *4* escaped
# Returns True if s[i] is preceded by an odd number of backslashes.

def escaped(s,i):

    count = 0
    while i-1 >= 0 and s[i-1] == '\\':
        count += 1
        i -= 1
    return (count%2) == 1
#@+node:ekr.20031218072017.3175: *4* find_line_start
def find_line_start(s,i):
    
    '''Return the index in s of the start of the line containing s[i].'''

    if i < 0:
        return 0 # New in Leo 4.4.5: add this defensive code.

    # bug fix: 11/2/02: change i to i+1 in rfind
    i = s.rfind('\n',0,i+1) # Finds the highest index in the range.
    return 0 if i == -1 else i + 1
    # if i == -1: return 0
    # else: return i + 1
#@+node:ekr.20031218072017.3176: *4* find_on_line
def find_on_line(s,i,pattern):

    j = s.find('\n',i)
    if j == -1: j = len(s)
    k = s.find(pattern,i,j)
    return k
#@+node:ekr.20031218072017.3177: *4* is_c_id
def is_c_id(ch):

    return g.isWordChar(ch)

#@+node:ekr.20031218072017.3178: *4* is_nl
def is_nl(s,i):

    return i < len(s) and (s[i] == '\n' or s[i] == '\r')
#@+node:ekr.20031218072017.3179: *4* is_special
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
#@+node:ekr.20031218072017.3180: *4* is_ws & is_ws_or_nl
def is_ws(c):

    return c == '\t' or c == ' '

def is_ws_or_nl(s,i):

    return g.is_nl(s,i) or (i < len(s) and g.is_ws(s[i]))
#@+node:ekr.20031218072017.3181: *4* match
# Warning: this code makes no assumptions about what follows pattern.

def match(s,i,pattern):

    return s and pattern and s.find(pattern,i,i+len(pattern)) == i
#@+node:ekr.20031218072017.3182: *4* match_c_word
def match_c_word (s,i,name):

    if name == None: return False
    n = len(name)
    if n == 0: return False
    return name == s[i:i+n] and (i+n == len(s) or not g.is_c_id(s[i+n]))
#@+node:ekr.20031218072017.3183: *4* match_ignoring_case
def match_ignoring_case(s1,s2):

    if s1 == None or s2 == None: return False

    return s1.lower() == s2.lower()
#@+node:ekr.20031218072017.3184: *4* match_word
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
#@+node:ekr.20031218072017.3185: *4* skip_blank_lines
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
#@+node:ekr.20031218072017.3186: *4* skip_c_id
def skip_c_id(s,i):

    n = len(s)
    while i < n and g.isWordChar(s[i]):
        i += 1
    return i
#@+node:ekr.20040705195048: *4* skip_id
def skip_id(s,i,chars=None):

    chars = chars and g.toUnicode(chars) or ''
    n = len(s)
    while i < n and (g.isWordChar(s[i]) or s[i] in chars):
        i += 1
    return i
#@+node:ekr.20031218072017.3187: *4* skip_line, skip_to_start/end_of_line
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
#@+node:ekr.20031218072017.3188: *4* skip_long
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
#@+node:ekr.20031218072017.3189: *4* skip_matching_python_delims
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
#@+node:ekr.20110916215321.6712: *4* g.skip_matching_c_delims
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
#@+node:ekr.20060627080947: *4* skip_matching_python_parens
def skip_matching_python_parens(s,i):

    '''Skip from the opening ( to the matching ).

    Return the index of the matching ')', or -1'''

    return skip_matching_python_delims(s,i,'(',')')
#@+node:ekr.20031218072017.3190: *4* skip_nl
# We need this function because different systems have different end-of-line conventions.

def skip_nl (s,i):

    '''Skips a single "logical" end-of-line character.'''

    if g.match(s,i,"\r\n"): return i + 2
    elif g.match(s,i,'\n') or g.match(s,i,'\r'): return i + 1
    else: return i
#@+node:ekr.20031218072017.3191: *4* skip_non_ws
def skip_non_ws (s,i):

    n = len(s)
    while i < n and not g.is_ws(s[i]):
        i += 1
    return i
#@+node:ekr.20031218072017.3192: *4* skip_pascal_braces
# Skips from the opening { to the matching }.

def skip_pascal_braces(s,i):

    # No constructs are recognized inside Pascal block comments!
    k = s.find('}',i)
    if i == -1: return len(s)
    else: return k
#@+node:ekr.20031218072017.3193: *4* skip_to_char
def skip_to_char(s,i,ch):

    j = s.find(ch,i)
    if j == -1:
        return len(s),s[i:]
    else:
        return j,s[i:j]
#@+node:ekr.20031218072017.3194: *4* skip_ws, skip_ws_and_nl
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
#@+node:ekr.20031218072017.3195: *3* splitLines & joinLines
def splitLines (s):

    '''Split s into lines, preserving the number of lines and
    the endings of all lines, including the last line.'''

    # g.stat()

    if s:
        return s.splitlines(True) # This is a Python string function!
    else:
        return []

splitlines = splitLines

def joinLines (aList):

    return ''.join(aList)

joinlines = joinLines
#@+node:ekr.20040327103735.2: ** Script Tools (leoGlobals.py)
#@+node:ekr.20050503112513.7: *3* g.executeFile
def executeFile(filename, options= ''):

    if not os.access(filename, os.R_OK): return
    fdir, fname = g.os_path_split(filename)

    # New in Leo 4.10: alway use subprocess.
    def subprocess_wrapper(cmdlst):
        # g.trace(cmdlst, fdir)
        # g.trace(subprocess.list2cmdline([cmdlst]))
        p = subprocess.Popen(cmdlst, cwd=fdir,
            universal_newlines=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdo, stde = p.communicate()
        return p.wait(), stdo, stde
    rc, so, se = subprocess_wrapper('%s %s %s'%(sys.executable, fname, options))
    if rc: g.pr('return code', rc)
    g.pr(so,se)
#@+node:ekr.20131016032805.16721: *3* g.execute_shell_commands
def execute_shell_commands(commands,trace = False):
    '''
    Execute each shell command in a separate process.
    Wait for each command to complete, except those starting with '&'
    '''
    if g.isString(commands): commands = [commands]
    for command in commands:
        wait = not command.startswith('&')
        if command.startswith('&'): command = command[1:].strip()
        if trace: g.trace('wait: %s command: %s' % (wait,command))
        proc = subprocess.Popen(command,shell=True)
        if wait: proc.communicate()
#@+node:ekr.20040321065415: *3* g.findNode... &,findTopLevelNode
def findNodeInChildren(c,p,headline):

    """Search for a node in v's tree matching the given headline."""

    for p in p.children():
        if p.h.strip() == headline.strip():
            return p.copy()
    return c.nullPosition()

def findNodeInTree(c,p,headline):

    """Search for a node in v's tree matching the given headline."""

    for p in p.subtree():
        if p.h.strip() == headline.strip():
            return p.copy()
    return c.nullPosition()

def findNodeAnywhere(c,headline):

    for p in c.all_unique_positions():
        if p.h.strip() == headline.strip():
            return p.copy()
    return c.nullPosition()

def findTopLevelNode(c,headline):

    for p in c.rootPosition().self_and_siblings():
        if p.h.strip() == headline.strip():
            return p.copy()
    return c.nullPosition()
#@+node:EKR.20040614071102.1: *3* g.getScript
def getScript (c,p,useSelectedText=True,forcePythonSentinels=True,useSentinels=True):

    '''Return the expansion of the selected text of node p.
    Return the expansion of all of node p's body text if
    p is not the current node or if there is no text selection.'''

    # New in Leo 4.6 b2: use a pristine atFile handler
    # so there can be no conflict with c.atFileCommands.
    import leo.core.leoAtFile as leoAtFile
    at = leoAtFile.atFile(c)
    w = c.frame.body.bodyCtrl
    p1 = p and p.copy()
    if not p: p = c.p
    try:
        if g.app.inBridge:
            s = p.b
        elif w and p == c.p and useSelectedText and w.hasSelection():
            s = w.getSelectedText()
        else:
            s = p.b
        # Remove extra leading whitespace so the user may execute indented code.
        s = g.removeExtraLws(s,c.tab_width)
        if s.strip():
            g.app.scriptDict["script1"]=s
            # Important: converts unicode to utf-8 encoded strings.
            script = at.writeFromString(p.copy(),s,
                forcePythonSentinels=forcePythonSentinels,
                useSentinels=useSentinels)
            script = script.replace("\r\n","\n") # Use brute force.
            # Important, the script is an **encoded string**, not a unicode string.
            g.app.scriptDict["script2"]=script
        else: script = ''
    except Exception:
        g.es_print("unexpected exception in g.getScript")
        g.es_exception()
        script = ''
    return script
#@+node:ekr.20060624085200: *3* g.handleScriptException
def handleScriptException (c,p,script,script1):

    g.warning("exception executing script")

    full = c.config.getBool('show_full_tracebacks_in_scripts')

    fileName, n = g.es_exception(full=full)

    if p and not script1 and fileName == "<string>":
        c.goToScriptLineNumber(p,script,n)

    #@+<< dump the lines near the error >>
    #@+node:EKR.20040612215018: *4* << dump the lines near the error >>
    if g.os_path_exists(fileName):
        f = open(fileName)
        lines = f.readlines()
        f.close()
    else:
        lines = g.splitLines(script)

    s = '-' * 20
    g.es_print('',s)

    # Print surrounding lines.
    i = max(0,n-2)
    j = min(n+2,len(lines))
    while i < j:
        ch = g.choose(i==n-1,'*',' ')
        s = "%s line %d: %s" % (ch,i+1,lines[i])
        g.es('',s,newline=False)
        i += 1
    #@-<< dump the lines near the error >>
#@+node:ekr.20031218072017.2418: *3* g.initScriptFind (set up dialog)
def initScriptFind(c,findHeadline,changeHeadline=None,firstNode=None,
    script_search=True,script_change=True):

    import leo.core.leoGlobals as g

    # Find the scripts.
    p = c.p
    tm = c.testManager
    find_p = tm.findNodeInTree(p,findHeadline)
    if find_p:
        find_text = find_p.b
    else:
        g.error("no Find script node")
        return
    if changeHeadline:
        change_p = tm.findNodeInTree(p,changeHeadline)
    else:
        change_p = None
    if change_p:
        change_text = change_p.b
    else:
        change_text = ""
    # g.pr(find_p,change_p)

    # Initialize the find panel.
    c.script_search_flag = script_search
    c.script_change_flag = script_change and change_text
    if script_search:
        c.find_text = find_text.strip() + "\n"
    else:
        c.find_text = find_text
    if script_change:
        c.change_text = change_text.strip() + "\n"
    else:
        c.change_text = change_text
    c.frame.findPanel.init(c)
    c.showFindPanel()
#@+node:ekr.20111115155710.9859: ** Tokenizing & parsing
#@+node:ekr.20111115155710.9814: *3* g.python_tokenize
def python_tokenize (s,line_numbers=True):

    '''Tokenize string s and return a list of tokens (kind,value,line_number)

    where kind is in ('comment,'id','nl','other','string','ws').
    '''

    result,i,line_number = [],0,0
    while i < len(s):
        progress = j = i
        ch = s[i]
        if ch == '\n':
            kind,i = 'nl',i+1
        elif ch in ' \t':
            kind = 'ws'
            while i < len(s) and s[i] in ' \t':
                i += 1
        elif ch == '#':
            kind,i = 'comment',g.skip_to_end_of_line(s,i)
        elif ch in '"\'':
            kind,i = 'string',g.skip_python_string(s,i,verbose=False)
        elif ch == '_' or ch.isalpha():
            kind,i = 'id',g.skip_id(s,i)
        else:
            kind,i = 'other',i+1

        assert progress < i and j == progress
        val = s[j:i]
        assert val

        if line_numbers:
            line_number += val.count('\n') # A comment.
            result.append((kind,val,line_number),)
        else:
            result.append((kind,val),)

    return result
#@+node:ekr.20031218072017.1498: ** Unicode utils...
#@+node:ekr.20100125073206.8709: *3* g.getPythonEncodingFromString
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
#@+node:ekr.20080816125725.2: *3* g.isBytes, isCallable, isChar, isString & isUnicode
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
#@+node:ekr.20031218072017.1500: *3* g.isValidEncoding
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
#@+node:ekr.20061006152327: *3* g.isWordChar & g.isWordChar1
def isWordChar (ch):

    '''Return True if ch should be considered a letter.'''

    return ch and (ch.isalnum() or ch == '_')

def isWordChar1 (ch):

    return ch and (ch.isalpha() or ch == '_')
#@+node:ekr.20031218072017.1501: *3* g.reportBadChars
def reportBadChars (s,encoding):

    trace = False and not g.unitTesting
    errors = 0
    if g.isPython3:
        if g.isUnicode(s):
            for ch in s:
                try: ch.encode(encoding,"strict")
                except UnicodeEncodeError:
                    errors += 1
            if errors:
                s2 = "%d errors converting %s to %s" % (
                    errors, s.encode(encoding,'replace'),
                    encoding.encode('ascii','replace'))
                if not g.unitTesting:
                    g.error(s2)
        elif g.isChar(s):
            for ch in s:
                try: unicode(ch,encoding,"strict")
                except Exception: errors += 1
            if errors:
                s2 = "%d errors converting %s (%s encoding) to unicode" % (
                    errors, unicode(s,encoding,'replace'),
                    encoding.encode('ascii','replace'))
                if not g.unitTesting:
                    g.error(s2)
    else:
        if g.isUnicode(s):
            for ch in s:
                try: ch.encode(encoding,"strict")
                except UnicodeEncodeError:
                    errors += 1
            if errors:
                s2 = "%d errors converting %s to %s" % (
                    errors, s.encode(encoding,'replace'),
                    encoding.encode('ascii','replace'))
                if not g.unitTesting:
                    g.error(s2)
        elif g.isChar(s):
            for ch in s:
                try: unicode(ch,encoding,"strict")
                except Exception: errors += 1
            if errors:
                s2 = "%d errors converting %s (%s encoding) to unicode" % (
                    errors, unicode(s,encoding,'replace'),
                    encoding.encode('ascii','replace'))
                if not g.unitTesting:
                    g.error(s2)
    if trace and not errors:
        g.es_exception()
#@+node:ekr.20130910044521.11304: *3* g.stripBOM
def stripBOM(s):
    
    '''
    If there is a BOM, return (e,s2) where e is the encoding
    implied by the BOM and s2 is the s stripped of the BOM.
    
    If there is no BOM, return (None,s)
    
    s must be the contents of a file (a string) read in binary mode.
    '''

    table = (
        # Important: test longer bom's first.
        (4, 'utf-32', codecs.BOM_UTF32_BE),
        (4, 'utf-32', codecs.BOM_UTF32_LE),
        (3, 'utf-8',  codecs.BOM_UTF8),
        (2, 'utf-16', codecs.BOM_UTF16_BE),
        (2, 'utf-16', codecs.BOM_UTF16_LE),
    )
    if s:
        for n,e,bom in table:
            assert len(bom) == n
            if bom == s[:len(bom)]:
                return e,s[len(bom):]
    return None,s
#@+node:ekr.20050208093800: *3* g.toEncodedString
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
#@+node:ekr.20050208093800.1: *3* g.toUnicode
def toUnicode (s,encoding='utf-8',reportErrors=False):

    # The encoding is usually 'utf-8'
    # but it may be different while importing or reading files.
    if not encoding:
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
                g.es_exception()
                s = ''
    else:
        pass
    return s
#@+node:ekr.20091206161352.6232: *3* g.u & g.ue
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
#@+node:ekr.20080919065433.2: *3* toEncodedStringWithErrorCode (for unit testing)
def toEncodedStringWithErrorCode (s,encoding,reportErrors=False):

    ok = True

    if g.isUnicode(s):
        try:
            s = s.encode(encoding,"strict")
        except Exception:
            if reportErrors: g.reportBadChars(s,encoding)
            s = s.encode(encoding,"replace")
            ok = False
    return s, ok
#@+node:ekr.20080919065433.1: *3* toUnicodeWithErrorCode (for unit testing)
def toUnicodeWithErrorCode (s,encoding,reportErrors=False):

    ok = True
    if g.isPython3: f = str
    else: f = unicode
    if s is None:
        s = g.u('')
    if not g.isUnicode(s):
        try:
            s = f(s,encoding,'strict')
        except Exception:
            if reportErrors:
                g.reportBadChars(s,encoding)
            s = f(s,encoding,'replace')
            ok = False
    return s,ok
#@+node:ekr.20070524083513: ** Unit testing (leoGlobals.py)
#@+node:ekr.20070619173330: *3* g.getTestVars
def getTestVars ():

    d = g.app.unitTestDict
    c = d.get('c')
    p = d.get('p')
    # Indicate that getTestVars has run.
    # This is an indirect test that some unit test has run.
    d['getTestVars'] = True
    return c,p and p.copy()
#@+node:ekr.20100812172650.5909: *3* g.findTestScript
def findTestScript(c,h,where=None,warn=True):

    if where:
        p = g.findNodeAnywhere(c,where)
        if p:
            p = g.findNodeInTree(c,p,h)
    else:
        p = g.findNodeAnywhere(c,h)

    if p:
        return g.getScript(c,p)
    else:
        if warn: g.trace('Not found',h)
        return None
#@+node:ekr.20120311151914.9916: ** Urls... (leoGlobals.py)
kinds = '(file|ftp|gopher|http|https|mailto|news|nntp|prospero|telnet|wais)'
url_regex = re.compile(r"""%s://[^\s'"]+[\w=/]""" % (kinds))
#@+node:ekr.20120320053907.9776: *3* g.computeFileUrl
def computeFileUrl(fn,c=None,p=None):

    '''Compute finalized url for filename fn.
    This involves adding url escapes and evaluating Leo expressions.'''

    # Module 'urllib' has no 'parse' member.
    unquote = urllib.parse.unquote if isPython3 else urllib.unquote # pylint: disable=E1101
    # First, replace special characters (especially %20, by their equivalent).
    url = unquote(fn)
    # Finalize the path *before* parsing the url.
    i = url.find('~')
    if i > -1:
        # Expand '~' and handle Leo expressions.
        path = url[i:]
        path = g.os_path_expanduser(path)
        path = g.os_path_expandExpression(path,c=c)
        path = g.os_path_finalize(path)
        url = url[:i] + path
    else:
        # Handle Leo expressions.
        tag = 'file://'
        tag2 = 'file:///'
        if sys.platform.startswith('win') and url.startswith(tag2):
            path = url[len(tag2):].lstrip()
        elif url.startswith(tag):
            path = url[len(tag):].lstrip()
        else:
            path = url
        path = g.os_path_expandExpression(path,c=c)
        # Handle ancestor @path directives.
        if c and c.openDirectory:
            base = c.getNodePath(p)
            path = g.os_path_finalize_join(c.openDirectory,base,path)
        else:
            path = g.os_path_finalize(path)
        url = '%s%s' % (tag,path)
    return url
#@+node:ekr.20120311151914.9917: *3* g.getUrlFromNode
def getUrlFromNode(p):

    '''Get an url from node p:

    1. Use the headline if it contains a valid url.
    2. Otherwise, look *only* at the first line of the body.
    '''

    trace = True and not g.unitTesting
    if not p: return None
    c = p.v.context
    assert c
    table = [p.h,g.splitLines(p.b)[0] if p.b else '']
    table = [s[4:] if g.match_word(s,0,'@url') else s for s in table]
    table = [s.strip() for s in table if s.strip()]
    # First, check for url's with an explicit scheme.
    for s in table:
        if g.isValidUrl(s):
            return s
    # Next check for existing file and add a file:// scheme.
    for s in table:
        tag = 'file://'
        url = computeFileUrl(s,c=c,p=p)
        if url.startswith(tag):
            fn = url[len(tag):].lstrip()
            fn = fn.split('#',1)[0]
            # g.trace('fn',fn)
            if g.os_path_isfile(fn):
                # Return the *original* url, with a file:// scheme.
                # g.handleUrl will call computeFileUrl again.
                return 'file://'+s
    # Finally, check for local url's.
    for s in table:
        if s.startswith("#"):
            return s
    return None
#@+node:tbrown.20090219095555.63: *3* g.handleUrl
#@+at Most browsers should handle the following urls:
#   ftp://ftp.uu.net/public/whatever.
#   http://localhost/MySiteUnderDevelopment/index.html
#   file:///home/me/todolist.html
#@@c

def handleUrl(url,c=None,p=None):

    # E1101: Module 'urllib' has no 'parse' member
    unquote = urllib.parse.unquote if isPython3 else urllib.unquote # pylint: disable=E1101
    trace = False and not g.unitTesting ; verbose = False
    if c and not p:
        p = c.p
    if url.startswith('@url'):
        url = url[4:].lstrip()
    try:
        tag = 'file://'
        if url.startswith(tag) and not url.startswith(tag+'#'):
            # Finalize the path *before* parsing the url.
            url = g.computeFileUrl(url,c=c,p=p)
        parsed   = urlparse.urlparse(url)
        # pylint: disable=E1103
        # E1103: Instance of 'ParseResult' has no 'fragment' member
        # E1103: Instance of 'ParseResult' has no 'netloc' member
        # E1103: Instance of 'ParseResult' has no 'path' member
        # E1103: Instance of 'ParseResult' has no 'scheme' member
        fragment = parsed.fragment 
        netloc   = parsed.netloc
        path     = parsed.path
        scheme   = parsed.scheme
        if netloc:
            leo_path = os.path.join(netloc, path)
            # "readme.txt" gets parsed into .netloc...
        else:
            leo_path = path
        if leo_path.endswith('\\'): leo_path = leo_path[:-1]
        if leo_path.endswith('/'):  leo_path = leo_path[:-1]
        if trace and verbose:
            print()
            g.trace('url          ',url)
            g.trace('c.frame.title',c.frame.title)
            g.trace('leo_path     ',leo_path)
            g.trace('parsed.netloc',netloc)
            g.trace('parsed.path  ',path)
            g.trace('parsed.scheme',scheme)
        if c and scheme in ('', 'file'):
            if not leo_path:
                if '-->' in path:
                    g.recursiveUNLSearch(unquote(path).split("-->"), c)
                    return
                if not path and fragment:
                    g.recursiveUNLSearch(unquote(fragment).split("-->"), c)
                    return
            # .leo file
            if leo_path.lower().endswith('.leo') and os.path.exists(leo_path):
                # Immediately end editing, so that typing in the new window works properly.
                c.endEditing()
                c.redraw_now()
                if g.unitTesting:
                    g.app.unitTestDict['g.openWithFileName']=leo_path
                else:
                    c2 = g.openWithFileName(leo_path,old_c=c)
                    # with UNL after path
                    if c2 and fragment:
                        g.recursiveUNLSearch(fragment.split("-->"),c2)
                    if c2:
                        c2.bringToFront()
                        return
        # isHtml = leo_path.endswith('.html') or leo_path.endswith('.htm')
        # Use g.os_startfile for *all* files.
        if scheme in ('', 'file'):
            if g.os_path_exists(leo_path):
                if trace: g.trace('g.os_startfile(%s)' % (leo_path))
                leo_path = unquote(leo_path)
                g.os_startfile(leo_path)
            else:
                g.es("File '%s' does not exist"%leo_path)
        else:
            import webbrowser

            if trace: g.trace('webbrowser.open(%s)' % (url))
            if g.unitTesting:
                g.app.unitTestDict['browser']=url
            else:
                # Mozilla throws a weird exception, then opens the file!
                try: webbrowser.open(url)
                except: pass
    except:
        g.es("exception opening",leo_path)
        g.es_exception()
#@+node:ekr.20120311151914.9918: *3* g.isValidUrl
def isValidUrl(url):

    '''Return true if url *looks* like a valid url.'''

    table = (
        'file','ftp','gopher','hdl','http','https','imap',
        'mailto','mms','news','nntp','prospero','rsync','rtsp','rtspu',
        'sftp','shttp','sip','sips','snews','svn','svn+ssh','telnet','wais',
    )
    if url.startswith('#-->'):
        # All Leo UNL's.
        return True
    elif url.startswith('@'):
        return False
    else:
        parsed = urlparse.urlparse(url)
        # E1103: Instance of 'ParseResult' has no 'scheme' member.
        scheme = parsed.scheme # pylint: disable=E1103
        for s in table:
            if scheme.startswith(s):
                return True
        return False
#@+node:ekr.20120315062642.9744: *3* g.openUrl
def openUrl(p):

    if p:
        url = g.getUrlFromNode(p)
        if url:
            c = p.v.context
            if not g.doHook("@url1",c=c,p=p,v=p,url=url):
                g.handleUrl(url,c=c,p=p)
            g.doHook("@url2",c=c,p=p,v=p)
#@+node:ekr.20110605121601.18135: *3* g.openUrlOnClick (open-url-under-cursor)
def openUrlOnClick(event):
    '''Open the URL under the cursor.  Return it for unit testing.'''
    c = event.get('c')
    if not c: return None
    w = event.get('w') or c.frame.body.bodyCtrl
    s = w.getAllText()
    ins = w.getInsertPoint()
    i,j = w.getSelectionRange()
    if i != j: return None # So find doesn't open the url.
    row,col = g.convertPythonIndexToRowCol(s,ins)
    i,j = g.getLine(s,ins)
    line = s[i:j]
    for match in g.url_regex.finditer(line):
        if match.start() <= col < match.end(): # Don't open if we click after the url.
            url = match.group()
            if g.isValidUrl(url):
                p = c.p
                if not g.doHook("@url1",c=c,p=p,v=p,url=url):
                    g.handleUrl(url,c=c,p=p)
                g.doHook("@url2",c=c,p=p,v=p)
                return url
    return None
#@+node:EKR.20040612114220: ** Utility classes, functions & objects...
#@+node:ekr.20050315073003: *3*  Index utilities... (leoGlobals)
#@+node:ekr.20050314140957: *4* g.convertPythonIndexToRowCol
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
        # g.trace('prevNL',prevNL,'i',i,g.callers())
        return row,i-prevNL-1
#@+node:ekr.20050315071727: *4* g.convertRowColToPythonIndex
def convertRowColToPythonIndex (s,row,col,lines=None):

    '''Convert zero-based row/col indices into a python index into string s.'''

    if row < 0: return 0

    if lines is None:
        lines = g.splitLines(s)

    if row >= len(lines):
        return len(s)

    col = min(col, len(lines[row]))

    # A big bottleneck
    prev = 0
    for line in lines[:row]:
        prev += len(line)

    return prev + col
#@+node:ekr.20031218072017.3140: *3*  List utilities...
#@+node:ekr.20031218072017.3141: *4* appendToList
def appendToList(out, s):

    for i in s:
        out.append(i)
#@+node:ekr.20031218072017.3142: *4* flattenList
def flattenList (theList):

    result = []
    for item in theList:
        if type(item) == types.ListType:
            result.extend(g.flattenList(item))
        else:
            result.append(item)
    return result
#@+node:ekr.20060221081328: *4* maxStringListLength
def maxStringListLength(aList):

    '''Return the maximum string length in a list of strings.'''

    n = 0
    for z in aList:
        if g.isString():
            n = max(n,len(z))

    return n
#@+node:ekr.20031218072017.3106: *3* angleBrackets & virtual_event_name
# Returns < < s > >

def angleBrackets(s):

    return ( "<<" + s +
        ">>") # must be on a separate line.

virtual_event_name = angleBrackets
#@+node:ekr.20031218072017.3097: *3* CheckVersion
#@+node:ekr.20060921100435: *4* CheckVersion, helper
# Simplified version by EKR: stringCompare not used.

def CheckVersion (s1,s2,condition=">=",stringCompare=None,delimiter='.',trace=False):

    # CheckVersion is called early in the startup process.

    vals1 = [g.CheckVersionToInt(s) for s in s1.split(delimiter)] ; n1 = len(vals1)
    vals2 = [g.CheckVersionToInt(s) for s in s2.split(delimiter)] ; n2 = len(vals2)
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
        # g.pr('%10s' % (repr(vals1)),'%2s' % (condition),'%10s' % (repr(vals2)),result)
        g.pr('%7s' % (s1),'%2s' % (condition),'%7s' % (s2),result)
    return result
#@+node:ekr.20070120123930: *5* CheckVersionToInt
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
#@+node:ekr.20060921100435.1: *4* oldCheckVersion (Dave Hein)
#@+at g.CheckVersion() is a generic version checker.  Assumes a
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
#@+node:ekr.20031218072017.3098: *3* class Bunch (object)
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
#@+node:ekr.20031219074948.1: *3* class nullObject
# From the Python cookbook, recipe 5.23

# This is now defined at the start of this file.
#@+node:ville.20090827174345.9963: *3* g.assertui
class UiTypeException(Exception):
    pass

def assertUi(uitype):
    if not g.app.gui.guiName() == uitype:
        raise UiTypeException
#@+node:ekr.20111103205308.9657: *3* g.cls
def cls(event=None):

    '''Clear the screen.'''

    import os
    import sys

    if sys.platform.lower().startswith('win'):
        os.system('cls')
#@+node:ekr.20031218072017.3103: *3* g.computeWindowTitle
def computeWindowTitle (fileName):

    if fileName == None:
        return "untitled"
    else:
        path,fn = g.os_path_split(fileName)
        if path:
            title = fn + " in " + path
        else:
            title = fn
        # Yet another fix for bug 1194209: regularize slashes.
        if os.sep in '/\\':
            title = title.replace('/',os.sep).replace('\\',os.sep)
        return title
#@+node:ekr.20090516135452.5777: *3* g.ensureLeading/TrailingNewlines
def ensureLeadingNewlines (s,n):

    s = g.removeLeading(s,'\t\n\r ')
    return ('\n' * n) + s

def ensureTrailingNewlines (s,n):

    s = g.removeTrailing(s,'\t\n\r ')
    return s + '\n' * n


#@+node:ekr.20031218072017.3138: *3* g.executeScript
def executeScript (name):

    """Execute a script whose short python file name is given.

    This is called only from the scripts_menu plugin."""

    mod_name,ext = g.os_path_splitext(name)
    theFile = None
    try:
        # This code is in effect an import or a reload.
        # This allows the user to modify scripts without leaving Leo.
        theFile,filename,description = imp.find_module(mod_name)
        imp.load_module(mod_name,theFile,filename,description)
    except Exception:
        g.error("exception executing",name)
        g.es_exception()

    if theFile:
        theFile.close()
#@+node:tbrown.20130411121812.28336: *3* g.expand_css_constants
def expand_css_constants(sheet, font_size_delta=0):
    
    constants = find_constants_defined(sheet)
    
    # adjust @font-size-body by font_size_delta
    # easily extendable to @font-size-*
    if font_size_delta and "@font-size-body" in constants:
        size = constants["@font-size-body"].replace("px", "")
        size = min(250, max(1, int(size) + font_size_delta))
        
        constants["@font-size-body"] = "%spx" % size
    
    for const in constants:
        sheet = re.sub(
            const+"(?![-A-Za-z0-9_])",  
            # don't replace shorter constants occuring in larger
            constants[const],
            sheet
        )
        
    return sheet
#@+node:ekr.20040331083824.1: *3* g.fileLikeObject
# Note: we could use StringIo for this.

class fileLikeObject:

    """Define a file-like object for redirecting writes to a string.

    The caller is responsible for handling newlines correctly."""

    #@+others
    #@+node:ekr.20050404151753: *4*  ctor (g.fileLikeObject)
    def __init__(self,encoding='utf-8',fromString=None):

        # g.trace('g.fileLikeObject:__init__','fromString',fromString)

        # New in 4.2.1: allow the file to be inited from string s.

        self.encoding = encoding or 'utf-8'

        if fromString:
            self.list = g.splitLines(fromString) # Must preserve newlines!
        else:
            self.list = []

        self.ptr = 0

    # In CStringIO the buffer is read-only if the initial value (fromString) is non-empty.
    #@+node:ekr.20050404151753.1: *4* clear
    def clear (self):

        self.list = []
    #@+node:ekr.20050404151753.2: *4* close
    def close (self):

        pass

        # The StringIo version free's the memory buffer.
    #@+node:ekr.20050404151753.3: *4* flush
    def flush (self):

        pass
    #@+node:ekr.20050404151753.4: *4* get & getvalue & read
    def get (self):

        return ''.join(self.list)

    getvalue = get # for compatibility with StringIo
    read = get # for use by sax.
    #@+node:ekr.20050404151753.5: *4* readline
    def readline(self): # New for read-from-string (readOpenFile).

        if self.ptr < len(self.list):
            line = self.list[self.ptr]
            # g.trace(repr(line))
            self.ptr += 1
            return line
        else:
            return ''
    #@+node:ekr.20050404151753.6: *4* write
    def write (self,s):

        if s:
            if g.isBytes(s):
                s = g.toUnicode(s,self.encoding)

            self.list.append(s)
    #@-others
#@+node:tbrown.20130411121812.28335: *3* g.find_constants_defined
def find_constants_defined(text):
    """find_constants - Return a dict of constants defined in the supplied text,
    constants match::
    
        ^\s*(@[A-Za-z_][-A-Za-z0-9_]*)\s*=\s*(.*)$
        i.e.
        @foo_1-5=a
            @foo_1-5 = a more here

    :Parameters:
    - `text`: text to search
    """
    pattern = re.compile(r"^\s*(@[A-Za-z_][-A-Za-z0-9_]*)\s*=\s*(.*)$")
    ans = {}
    text = text.replace('\\\n', '')  # merge lines ending in \
    for line in text.split('\n'):
        test = pattern.match(line)
        if test:
            ans.update([test.groups()])
    # constants may refer to other constants, de-reference here    
    change = True
    level = 0
    while change and level < 10:
        level += 1
        change = False
        for k in ans:
            # pylint: disable=W0108
            #   lambda may not be necessary (it is).
            # process longest first so @solarized-base0 is not replaced
            # when it's part of @solarized-base03
            for o in sorted(ans, key=lambda x:len(x), reverse=True):
                if o in ans[k]:
                    change = True
                    ans[k] = ans[k].replace(o, ans[o])
    if level == 10:
        print("Ten levels of recursion processing styles, abandoned.")
        g.es("Ten levels of recursion processing styles, abandoned.")
    return ans
#@+node:ekr.20031218072017.3126: *3* g.funcToMethod
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
#@+node:ekr.20120123143207.10223: *3* g.GeneralSetting & isGeneralSetting
# Important: The startup code uses this class,
# so it is convenient to define it in leoGlobals.py.
class GeneralSetting:

    '''A class representing any kind of setting except shortcuts.'''

    def __init__ (self,kind,encoding=None,ivar=None,setting=None,val=None,path=None,tag='setting'):

        self.encoding = encoding
        self.ivar = ivar
        self.kind = kind
        self.path = path
        self.setting = setting
        self.val = val
        self.tag = tag

    def __repr__ (self):

        result = ['GeneralSetting kind: %s' % (self.kind)]
        ivars = ('ivar','path','setting','val','tag')
        for ivar in ivars:
            if hasattr(self,ivar):
                val =  getattr(self,ivar)
                if val is not None:
                    result.append('%s: %s' % (ivar,val))
        return ','.join(result)

    dump = __repr__

def isGeneralSetting(obj):
    return isinstance(obj,GeneralSetting)
#@+node:ekr.20111017204736.15898: *3* g.getDocString
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

#@+node:ekr.20111017211256.15905: *3* g.getDocStringForFunction
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
            s = g.getDocString(script)
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
#@+node:ekr.20061031102333.2: *3* g.getWord & getLine
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
#@+node:ekr.20110609125359.16493: *3* g.isMacOS
def isMacOS():

    return sys.platform == 'darwin'
#@+node:ekr.20050920084036.4: *3* g.longestCommonPrefix & g.itemsMatchingPrefixInList
def longestCommonPrefix (s1,s2):

    '''Find the longest prefix common to strings s1 and s2.'''

    prefix = ''
    for ch in s1:
        if s2.startswith(prefix + ch):
            prefix = prefix + ch
        else:
            return prefix
    return prefix

def itemsMatchingPrefixInList (s,aList,matchEmptyPrefix=False):

    '''This method returns a sorted list items of aList whose prefix is s.

    It also returns the longest common prefix of all the matches.'''

    if s:
        pmatches = [a for a in aList if a.startswith(s)]
    elif matchEmptyPrefix:
        pmatches = aList[:]
    else: pmatches = []

    if pmatches:
        pmatches.sort()
        common_prefix = reduce(g.longestCommonPrefix,pmatches)
    else:
        common_prefix = ''

    # g.trace(repr(s),len(pmatches))
    return pmatches,common_prefix
#@+node:ekr.20031218072017.3144: *3* g.makeDict
# From the Python cookbook.

def makeDict(**keys):

    """Returns a Python dictionary from using the optional keyword arguments."""

    return keys
#@+node:ekr.20060221083356: *3* g.prettyPrintType
def prettyPrintType (obj):

    if g.isPython3:
        if type(obj) in (types.MethodType,types.BuiltinMethodType):
            return 'method'
        elif type(obj) in (types.BuiltinFunctionType,types.FunctionType):
            return 'function'
        elif type(obj) == types.ModuleType:
            return 'module'
        elif g.isString(obj):
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
#@+node:ekr.20090516135452.5776: *3* g.removeLeading/Trailing
# Warning: g.removeTrailingWs already exists.
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
#@+node:ekr.20120123115816.10209: *3* g.ShortcutInfo & isShortcutInfo
# bindKey:            ShortcutInfo(kind,commandName,func,pane)
# bindKeyToDict:      ShortcutInfo(kind,commandName,func,pane,stroke)
# createModeBindings: ShortcutInfo(kind,commandName,func,nextMode,stroke)

# Important: The startup code uses this class,
# so it is convenient to define it in leoGlobals.py.
class ShortcutInfo:

    '''A class representing any kind of key binding line.

    This includes other information besides just the KeyStroke.'''

    #@+others
    #@+node:ekr.20120129040823.10254: *4*  ctor (ShortcutInfo)
    def __init__ (self,kind,commandName='',func=None,nextMode=None,pane=None,stroke=None):

        trace = False and commandName=='new' and not g.unitTesting

        if not (stroke is None or g.isStroke(stroke)):
            g.trace('***** (ShortcutInfo) oops',repr(stroke))

        self.kind = kind
        self.commandName = commandName
        self.func = func
        self.nextMode = nextMode
        self.pane = pane
        self.stroke = stroke
            # The *caller* must canonicalize the shortcut.

        if trace: g.trace('(ShortcutInfo)',commandName,stroke,g.callers())
    #@+node:ekr.20120203153754.10031: *4* __hash__ (ShortcutInfo)
    def __hash__ (self):

        return self.stroke.__hash__() if self.stroke else 0
    #@+node:ekr.20120125045244.10188: *4* __repr__ & ___str_& dump (ShortcutInfo)
    def __repr__ (self):

        return self.dump()

    __str__ = __repr__

    def dump (self):
        si = self    
        result = ['ShortcutInfo %17s' % (si.kind)]
        # Print all existing ivars.
        table = ('commandName','func','nextMode','pane','stroke')
        for ivar in table:
            if hasattr(si,ivar):
                val =  getattr(si,ivar)
                if val not in (None,'none','None',''):
                    if ivar == 'func': val = val.__name__
                    s = '%s %s' % (ivar,val)
                    result.append(s)
        return '[%s]' % ' '.join(result).strip()
    #@+node:ekr.20120129040823.10226: *4* isModeBinding
    def isModeBinding (self):

        return self.kind.startswith('*mode')
    #@-others

def isShortcutInfo(obj):
    return isinstance(obj,ShortcutInfo)
#@+node:ekr.20060410112600: *3* g.stripBrackets
def stripBrackets (s):

    '''Same as s.lstrip('<').rstrip('>') except it works for Python 2.2.1.'''

    if s.startswith('<'):
        s = s[1:]
    if s.endswith('>'):
        s = s[:-1]
    return s
#@+node:ekr.20111114151846.9847: *3* g.toPythonIndex
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
            i = g.convertRowColToPythonIndex(s,row-1,col)
            return i
        else:
            g.trace('bad string index: %s' % index)
            return 0

toGuiIndex = toPythonIndex
#@+node:ekr.20120912153732.10597: *3* g.wait
def sleep (n):

    '''Wait about n milliseconds.'''

    from time import sleep
    sleep(n) #sleeps for 5 seconds
#@+node:ekr.20120129181245.10220: *3* g.TypedDict/OfLists & isTypedDict/OfLists
class TypedDict:

    '''A class containing a name and enforcing type checking.'''

    #@+others
    #@+node:ekr.20120205022040.17769: *4* td.ctor
    def __init__(self,name,keyType,valType):

        trace = False and not g.unitTesting and name == 'g.app.config.defaultsDict'
        self.d = {}
        self.isList = False
        self._name = name # name is a method.
        self.keyType = keyType
        self.valType = valType

        if trace:
            print(self)
            # g.trace(self)
    #@+node:ekr.20120205022040.17770: *4* td.__repr__ & __str__
    def __repr__(self):

        return '<TypedDict name:%s keys:%s values:%s len(keys): %s' % (
            self._name,self.keyType.__name__,self.valType.__name__,len(list(self.keys())))

    __str__ = __repr__

    #@+node:ekr.20120206134955.10150: *4* td._checkKey/ValType
    def _checkKeyType(self,key):

        # These fail on Python 2.x for strings.
        if g.isPython3:
            # assert key.__class__ == self.keyType,self._reportTypeError(key,self.keyType)
            if key and key.__class__ != self.keyType:
                self._reportTypeError(key,self.keyType)

    def _checkValType(self,val):

        # This doesn't fail, either on Python 2.x or 3.x.
        assert val.__class__ == self.valType,self._reportTypeError(val,self.valType)

    def _reportTypeError(self,obj,objType):

        print('obj',obj,'obj.__class__',obj.__class__,'objType',objType)

        return 'dict: %s expected %s got %s' % (
            self._name,obj.__class__.__name__,objType.__name__)
    #@+node:ekr.20120205022040.17774: *4* td.add & td.replace
    def add(self,key,val):
        self._checkKeyType(key)
        self._checkValType(val)
        if self.isList:
            aList = self.d.get(key,[])
            if val not in aList:
                aList.append(val)
                self.d[key] = aList
        else:
            self.d[key] = val

    def replace(self,key,val):
        self._checkKeyType(key)
        if self.isList:
            try:
                for z in val:
                    self._checkValType(z)
            except TypeError:
                self._checkValType(val) # val is not iterable.
            self.d[key] = val
        else:
            self._checkValType(val)
            self.d[key] = val

    __setitem__ = replace # allow d[key] = val.
    #@+node:ekr.20120223062418.10422: *4* td.copy
    def copy(self,name=None):

        '''Return a new dict with the same contents.'''

        d = TypedDict(name or self._name,self.keyType,self.valType)
        d.d = dict(self.d)
        return d

    #@+node:ekr.20120206134955.10151: *4* td.dump
    def dump (self):

        result = ['Dump of %s' % (self)]

        for key in sorted(self.d.keys()):
            if self.isList:
                result.append(key)
                aList = self.d.get(key,[])
                for z in aList:
                    result.append('  '+repr(z))
            else:
                result.append(key,self.d.get(key))

        return '\n'.join(result)
    #@+node:ekr.20120205022040.17771: *4* td getters
    def get(self,key,default=None):
        self._checkKeyType(key)
        if default is None and self.isList:
            default = []
        return self.d.get(key,default)

    def keys(self):
        return self.d.keys()

    def name(self):
        return self._name
    #@+node:ekr.20120214165710.10728: *4* td.setName
    def setName (self,name):
        self._name =  name
    #@+node:ekr.20120205022040.17807: *4* td.update
    def update(self,d):

        if isinstance(d,TypedDict):
            self.d.update(d.d)
        else:
            self.d.update(d)
    #@-others

def isTypedDict(obj):
    return isinstance(obj,TypedDict)

class TypedDictOfLists (TypedDict):

    '''A class whose values are lists of typed values.'''

    def __init__(self,name,keyType,valType):
        TypedDict.__init__(self,name,keyType,valType) # Init the base class
        self.isList = True

    def __repr__(self):
        return '<TypedDictOfLists name:%s keys:%s values:%s len(keys): %s' % (
            self._name,self.keyType.__name__,self.valType.__name__,len(list(self.keys())))
    __str__ = __repr__

    def copy(self,name=None):
        d = TypedDictOfLists(name or self._name,self.keyType,self.valType)
        d.d = dict(self.d)
        return d

def isTypedDictOfLists(obj):
    return isinstance(obj,TypedDictOfLists)
#@+node:ekr.20041219095213: *3* import wrappers
#@+node:ekr.20040917061619: *4* g.cantImport
def cantImport (moduleName,pluginName=None,verbose=True):

    """Print a "Can't Import" message and return None."""

    s = "Can not import %s" % moduleName
    if pluginName: s = s + " from plugin %s" % pluginName

    if not g.app or not g.app.gui:
        print (s)
    elif g.unitTesting:
        # print s
        return
    # elif g.app.gui.guiName() == 'tkinter' and moduleName in ('Tkinter','Pmw'):
        # return
    else:
        g.warning('',s)

#@+node:ekr.20041219095213.1: *4* g.importModule
def importModule (moduleName,pluginName=None,verbose=False):

    '''Try to import a module as Python's import command does.

    moduleName is the module's name, without file extension.'''

    # Important: g is Null during startup.
    trace = False and not g.unitTesting
    module = sys.modules.get(moduleName)
    if module:
        return module
    if verbose: g.blue('loading %s' % moduleName)
    exceptions = [] 
    try:
        theFile = None
        try:
            # New in Leo 4.7. We no longer add Leo directories to sys.path,
            # so search extensions and external directories here explicitly.
            for findPath in (None,'extensions','external'):
                if findPath:
                    findPath2 = g.os_path_finalize_join(
                        g.app.loadDir,'..',findPath)
                    findPath = [findPath2]
                if trace: g.trace('findPath',findPath)
                try:
                    data = imp.find_module(moduleName,findPath) # This can open the file.
                    theFile,pathname,description = data
                    if trace: g.trace(theFile,moduleName,pathname)
                    module = imp.load_module(moduleName,theFile,pathname,description)
                    if module: 
                        g.es("%s loaded" % moduleName)
                        break
                except Exception:
                    t, v, tb = sys.exc_info()
                    del tb  # don't need the traceback
                    v = v or str(t) # in case v is empty, we'll at least have the execption type
                    if trace: g.trace(v,moduleName,findPath)
                    if v not in exceptions:
                        exceptions.append(v)
            else:
                #unable to load module, display all exception messages
                if verbose:
                    for e in exceptions:
                        g.warning(e) 
        except Exception: # Importing a module can throw exceptions other than ImportError.
            if verbose:
                t, v, tb = sys.exc_info()
                del tb  # don't need the traceback
                v = v or str(t) # in case v is empty, we'll at least have the execption type
                g.es_exception(v)
    finally:
        if theFile: theFile.close()

    if not module and verbose:
        g.cantImport(moduleName,pluginName=pluginName,verbose=verbose)
    return module
#@+node:ekr.20041219071407: *4* g.importExtension
def importExtension (moduleName,pluginName=None,verbose=False,required=False):

    '''Try to import a module.  If that fails,
    try to import the module from Leo's extensions directory.

    moduleName is the module's name, without file extension.'''

    module = g.importModule(moduleName,pluginName=pluginName,verbose=verbose)
    if not module and verbose:
        g.pr("Warning: '%s' failed to import '%s'" % (
            pluginName,moduleName))
    return module
#@+node:ekr.20031218072017.2278: *4* g.importFromPath
def importFromPath (name,path,pluginName=None,verbose=False):

    trace = False and not g.unitTesting
    fn = g.shortFileName(name)
    moduleName,ext = g.os_path_splitext(fn)
    path = g.os_path_normpath(path)
    if g.isPython3:
        assert g.isString(path)
    else:
        path = g.toEncodedString(path)
    # g.trace(type(path),repr(path))

    if 0: # Bug fix 2011/10/28: Always import the path from the specified path!
        module = sys.modules.get(moduleName)
        if module:
            if trace: g.trace('already loaded',moduleName,module)
            return module

    try:
        module,theFile = None,None
        try:
            data = imp.find_module(moduleName,[path]) # This can open the file.
            theFile,pathname,description = data
            module = imp.load_module(moduleName,theFile,pathname,description)
        except ImportError:
            if trace: # or verbose:
                g.error("exception in g.importFromPath")
                g.es_exception()
        except UiTypeException:
            if not g.unitTesting and not g.app.batchMode:
                g.es_print('Plugin %s does not support %s gui' % (
                    name,g.app.gui.guiName()))          
        except Exception:
            g.error("unexpected exception in g.importFromPath(%s)" %
                (name))
            g.es_exception()
    # Put no return statements before here!
    finally: 
        if theFile: theFile.close()

    if module:
        if trace: g.trace('loaded',moduleName)
    else:
        g.cantImport(moduleName,pluginName=pluginName,verbose=verbose)

    return module
#@+node:ekr.20040629162023: *3* readLines class and generator
#@+node:EKR.20040612114220.3: *4* g.readLinesGenerator
# This has been replaced by readLinesClass because
# yield is not valid in jython.

# def readLinesGenerator(s):

    # for line in g.splitLines(s):
        # # g.trace(repr(line))
        # yield line
    # yield ''
#@+node:EKR.20040612114220.4: *4* class readLinesClass
class readLinesClass:

    """A class whose next method provides a readline method for Python's tokenize module."""

    def __init__ (self,s):
        self.lines = g.splitLines(s)
        self.i = 0

    def next(self):
        if self.i < len(self.lines):
            line = self.lines[self.i]
            self.i += 1
        else:
            line = ''
        # g.trace(repr(line))
        return line

    __next__ = next
#@+node:ekr.20120201164453.10090: *3* g.KeyStroke & isStroke/OrNone
class KeyStroke:

    '''A class that announces that its contents has been canonicalized by k.strokeFromSetting.

    This allows type-checking assertions in the code.'''

    #@+others
    #@+node:ekr.20120204061120.10066: *4*  ks.ctor
    def __init__ (self,s):

        trace = False and not g.unitTesting and s == 'name'
        if trace: g.trace('(KeyStroke)',s,g.callers())

        assert s,repr(s)
        assert g.isString(s)
            # type('s') does not work in Python 3.x.
        self.s = s
    #@+node:ekr.20120204061120.10068: *4*  Special methods
    #@+node:ekr.20120203053243.10118: *5* ks.__hash__
    # Allow KeyStroke objects to be keys in dictionaries.

    def __hash__ (self):

        return self.s.__hash__() if self.s else 0
    #@+node:ekr.20120204061120.10067: *5* ks.__repr___ & __str__
    def __str__ (self):

        return '<KeyStroke: %s>' % (repr(self.s))

    __repr__ = __str__
    #@+node:ekr.20120203053243.10117: *5* ks.rich comparisons
    #@+at All these must be defined in order to say, for example:
    #     for key in sorted(d)
    # where the keys of d are KeyStroke objects.
    #@@c

    def __eq__ (self,other): 
        if not other:               return False
        elif hasattr(other,'s'):    return self.s == other.s
        else:                       return self.s == other

    def __lt__ (self,other):
        if not other:               return False
        elif hasattr(other,'s'):    return self.s < other.s
        else:                       return self.s < other

    def __le__ (self,other): return self.__lt__(other) or self.__eq__(other)    
    def __ne__ (self,other): return not self.__eq__(other)
    def __gt__ (self,other): return not self.__lt__(other) and not self.__eq__(other)  
    def __ge__ (self,other): return not self.__lt__(other)
    #@+node:ekr.20120203053243.10124: *4* ks.find, lower & startswith
    # These may go away later, but for now they make conversion of string strokes easier.

    def find (self,pattern):

        return self.s.find(pattern)

    def lower (self):

        return self.s.lower()

    def startswith(self,s):

        return self.s.startswith(s)
    #@+node:ekr.20120203053243.10121: *4* ks.isFKey
    def isFKey (self):

        s = self.s.lower()

        return s.startswith('f') and len(s) <= 3 and s[1:].isdigit()
    #@+node:ekr.20120203053243.10125: *4* ks.toGuiChar
    def toGuiChar (self):

        '''Replace special chars by the actual gui char.'''

        s = self.s.lower()
        if s in ('\n','return'):        s = '\n'
        elif s in ('\t','tab'):         s = '\t'
        elif s in ('\b','backspace'):   s = '\b'
        elif s in ('.','period'):       s = '.'
        return s
    #@-others

def isStroke(obj):
    return isinstance(obj,KeyStroke)

def isStrokeOrNone(obj):
    return obj is None or isinstance(obj,KeyStroke)
#@+node:ekr.20031218072017.3197: ** Whitespace...
#@+node:ekr.20031218072017.3198: *3* g.computeLeadingWhitespace
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
#@+node:ekr.20120605172139.10263: *3* g.computeLeadingWhitespaceWidth (new)
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
#@+node:ekr.20031218072017.3199: *3* g.computeWidth
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
#@+node:ekr.20051014175117: *3* g.adjustTripleString
def adjustTripleString (s,tab_width):

    '''Remove leading indentation from a triple-quoted string.

    This works around the fact that Leo nodes can't represent underindented strings.
    '''

    # Compute the minimum leading whitespace of all non-blank lines.
    lines = g.splitLines(s)
    first,w = True,0
    for line in lines:
        if line.strip():
            lws = g.get_leading_ws(line)
            # The sign of w2 does not matter.
            w2 = abs(g.computeWidth(lws,tab_width))
            if w2 == 0:
                return s
            elif first or w2 < w:
                w = w2
                first = False

    if w == 0: return s

    # Remove the leading whitespace.
    result = [g.removeLeadingWhitespace(line,w,tab_width) for line in lines]
    result = ''.join(result)
    return result
#@+node:ekr.20050211120242.2: *3* g.removeExtraLws
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
#@+node:ekr.20110727091744.15083: *3* g.wrap_lines (newer)
#@+at
# Important note: this routine need not deal with leading whitespace.
# Instead, the caller should simply reduce pageWidth by the width of
# leading whitespace wanted, then add that whitespace to the lines
# returned here.
# 
# The key to this code is the invarient that line never ends in whitespace.
#@@c

def wrap_lines (lines,pageWidth,firstLineWidth=None):

    """Returns a list of lines, consisting of the input lines wrapped to the given pageWidth."""

    if pageWidth < 10:
        pageWidth = 10

    # First line is special
    if not firstLineWidth:
        firstLineWidth = pageWidth
    if firstLineWidth < 10:
        firstLineWidth = 10
    outputLineWidth = firstLineWidth

    # Sentence spacing
    # This should be determined by some setting, and can only be either 1 or 2
    sentenceSpacingWidth = 1
    assert(0 < sentenceSpacingWidth < 3)

    # g.trace(lines)
    result = [] # The lines of the result.
    line = "" # The line being formed.  It never ends in whitespace.
    for s in lines:
        i = 0
        while i < len(s):
            assert(len(line) <= outputLineWidth) # DTHEIN 18-JAN-2004
            j = g.skip_ws(s,i)   # ;   ws = s[i:j]
            k = g.skip_non_ws(s,j) ; word = s[j:k]
            assert(k>i)
            i = k
            # DTHEIN 18-JAN-2004: wrap at exactly the text width, 
            # not one character less
            # 
            wordLen = len(word)
            if line.endswith('.') or line.endswith('?') or line.endswith('!'):
                space = ' ' * sentenceSpacingWidth
            else:
                space = ' '
            if len(line) > 0 and wordLen > 0: wordLen += len(space)
            if wordLen + len(line) <= outputLineWidth:
                if wordLen > 0:
                    #@+<< place blank and word on the present line >>
                    #@+node:ekr.20110727091744.15084: *4* << place blank and word on the present line >>
                    if len(line) == 0:
                        # Just add the word to the start of the line.
                        line = word
                    else:
                        # Add the word, preceeded by a blank.
                        line = space.join((line,word)) # DTHEIN 18-JAN-2004: better syntax
                    #@-<< place blank and word on the present line >>
                else: pass # discard the trailing whitespace.
            else:
                #@+<< place word on a new line >>
                #@+node:ekr.20110727091744.15085: *4* << place word on a new line >>
                # End the previous line.
                if len(line) > 0:
                    result.append(line)
                    outputLineWidth = pageWidth # DTHEIN 3-NOV-2002: width for remaining lines

                # Discard the whitespace and put the word on a new line.
                line = word

                # Careful: the word may be longer than pageWidth.
                if len(line) > pageWidth: # DTHEIN 18-JAN-2004: line can equal pagewidth
                    result.append(line)
                    outputLineWidth = pageWidth # DTHEIN 3-NOV-2002: width for remaining lines
                    line = ""
                #@-<< place word on a new line >>
    if len(line) > 0:
        result.append(line)
    # g.trace(result)
    return result
#@+node:ekr.20031218072017.3200: *3* g.get_leading_ws
def get_leading_ws(s):

    """Returns the leading whitespace of 's'."""

    i = 0 ; n = len(s)
    while i < n and s[i] in (' ','\t'):
        i += 1
    return s[0:i]
#@+node:ekr.20031218072017.3201: *3* g.optimizeLeadingWhitespace
# Optimize leading whitespace in s with the given tab_width.

def optimizeLeadingWhitespace (line,tab_width):

    i, width = g.skip_leading_ws_with_indent(line,0,tab_width)
    s = g.computeLeadingWhitespace(width,tab_width) + line[i:]
    return s
#@+node:ekr.20040723093558: *3* g.regularizeTrailingNewlines
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
#@+node:ekr.20091229090857.11698: *3* g.removeBlankLines
def removeBlankLines (s):

    lines = g.splitLines(s)
    lines = [z for z in lines if z.strip()]
    return ''.join(lines)
#@+node:ekr.20091229075924.6235: *3* g.removeLeadingBlankLines
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
#@+node:ekr.20031218072017.3202: *3* g.removeLeadingWhitespace
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
#@+node:ekr.20031218072017.3203: *3* g.removeTrailingWs
# Warning: string.rstrip also removes newlines!

def removeTrailingWs(s):

    j = len(s)-1
    while j >= 0 and (s[j] == ' ' or s[j] == '\t'):
        j -= 1
    return s[:j+1]
#@+node:ekr.20031218072017.3204: *3* g.skip_leading_ws
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
#@+node:ekr.20031218072017.3205: *3* g.skip_leading_ws_with_indent
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
#@+node:ekr.20040723093558.1: *3* g.stripBlankLines
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
#@+node:ekr.20060913091602: ** ZODB support
#@+node:ekr.20060913090832.1: *3* g.init_zodb
init_zodb_import_failed = False
init_zodb_failed = {} # Keys are paths, values are True.
init_zodb_db = {} # Keys are paths, values are ZODB.DB instances.

def init_zodb (pathToZodbStorage,verbose=True):

    '''Return an ZODB.DB instance from ZODB.FileStorage.FileStorage(pathToZodbStorage)
    return None on any error.'''

    global init_zodb_db, init_zodb_failed, init_zodb_import_failed

    db = init_zodb_db.get(pathToZodbStorage)
    if db: return db

    if init_zodb_import_failed: return None

    failed = init_zodb_failed.get(pathToZodbStorage)
    if failed: return None

    try:
        import ZODB
    except ImportError:
        if verbose:
            g.es('g.init_zodb: can not import ZODB')
            g.es_exception()
        init_zodb_import_failed = True
        return None

    try:
        storage = ZODB.FileStorage.FileStorage(pathToZodbStorage)
        init_zodb_db [pathToZodbStorage] = db = ZODB.DB(storage)
        return db
    except Exception:
        if verbose:
            g.es('g.init_zodb: exception creating ZODB.DB instance')
            g.es_exception()
        init_zodb_failed [pathToZodbStorage] = True
        return None
#@-others

# set g when the import is about to complete.
g = sys.modules.get('leo.core.leoGlobals')
assert g,sorted(sys.modules.keys())
#@-leo
