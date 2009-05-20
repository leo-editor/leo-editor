# -*- coding: utf-8 -*-
#@+leo-ver=4-thin
#@+node:ekr.20031218072017.3093:@thin leoGlobals.py
#@@first

"""Global constants, variables and utility functions used throughout Leo."""

#@@language python
#@@tabwidth -4
#@@pagewidth 80

#@<< imports >>
#@+node:ekr.20050208101229:<< imports >>
if 0:
    # This is now done in run.
    import leoGlobals as g # So code can use g below.

# Don't import this here: it messes up Leo's startup code.
# import leo.core.leoTest as leoTest

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

# Do NOT import pdb here!  We shall define pdb as a _function_ below.
# import pdb

try:
    # No such module in Python 3.x.
    import exceptions
except ImportError:
    pass

import operator
import re
import sys
import time
import zipfile

# These do not exist in IronPython.
# However, it *is* valid for IronPython to use the Python 2.4 libs!
import os
import string
import tempfile
import traceback
import types

# g.pr('(types.FrameType)',repr(types.FrameType))
# g.pr('(types.StringTypes)',repr(types.StringTypes))
#@-node:ekr.20050208101229:<< imports >>
#@nl
#@<< define general constants >>
#@+node:ekr.20031218072017.3094:<< define general constants >>
body_newline = '\n'
body_ignored_newline = '\r'
#@-node:ekr.20031218072017.3094:<< define general constants >>
#@nl
#@<< define global data structures >>
#@+node:EKR.20040610094819:<< define global data structures >>
# Visible externally so plugins may add to the list of directives.

globalDirectiveList = [

    # Longer prefixes must appear before shorter.
    'all',
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
#@nonl
#@-node:EKR.20040610094819:<< define global data structures >>
#@nl

# Give g a temporary value so tests for g.unitTesting will work in this file.
class gClass:
    def __init__(self):
        self.unitTesting = False

g = gClass() # Set later by startup logic to this module.
app = None # The singleton app object.
unitTesting = False # A synonym for app.unitTesting.
isPython3 = sys.version_info >= (3,0,0)

# "compile-time" constants.
# It makes absolutely no sense to change these after Leo loads.
unified_nodes = False
    # True: (Not recommended) unify vnodes and tnodes into a single vnode.

#@+others
#@+node:ekr.20050328133058:g.createStandAloneTkApp
# This must be defined in leoGlobals: g.app.gui doesn't exist yet.

def createStandAloneTkApp(pluginName=''):

    '''Create a Tk version of the g.app object for 'stand-alone' plugins.'''

    if not g.app:
        # Important: these references do not make Leo's core gui-dependent.
        # In other words, this function is called only when Tkinter should be the gui.
        import Tkinter as Tk
        Pmw = g.importExtension('Pmw',pluginName=pluginName,verbose=True)
        if Tk and Pmw:
            import leo.core.leoApp as leoApp, leoGui
            g.app = leoApp.LeoApp()
            g.app.root = Tk.Tk()
            Pmw.initialise(g.app.root)
            g.app.gui = leoGui.nullGui('<stand-alone app gui>')
            g.computeStandardDirectories()
    return g.app
#@-node:ekr.20050328133058:g.createStandAloneTkApp
#@+node:ekr.20031218072017.3095:Checking Leo Files...
#@+node:ekr.20031218072017.822:createTopologyList
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
#@-node:ekr.20031218072017.822:createTopologyList
#@-node:ekr.20031218072017.3095:Checking Leo Files...
#@+node:ekr.20031218072017.3099:Commands & Directives
#@+node:ekr.20050304072744:Compute directories... (leoGlobals)
#@+node:ekr.20041117155521:computeGlobalConfigDir
def computeGlobalConfigDir():

    import leo.core.leoGlobals as g

    encoding = g.startupEncoding()

    # To avoid pylint complaints that sys.leo_config_directory does not exist.
    leo_config_dir = (
        hasattr(sys,'leo_config_directory') and
        getattr(sys,'leo_config_directory'))

    if leo_config_dir:
        theDir = leo_config_dir
    else:
        theDir = g.os_path_join(g.app.loadDir,"..","config")

    if theDir:
        theDir = g.os_path_finalize(theDir)

    if (
        not theDir or
        not g.os_path_exists(theDir,encoding) or
        not g.os_path_isdir(theDir,encoding)
    ):
        theDir = None

    return theDir
#@-node:ekr.20041117155521:computeGlobalConfigDir
#@+node:ekr.20041117151301:computeHomeDir
def computeHomeDir():

    """Returns the user's home directory."""

    import leo.core.leoGlobals as g

    encoding = g.startupEncoding()
    # dotDir = g.os_path_finalize('./',encoding=encoding)
    # home = os.getenv('HOME',default=None)
    home = os.path.expanduser("~")
        # Windows searches the HOME, HOMEPATH and HOMEDRIVE environment vars, then gives up.

    # g.pr('computeHomeDir: %s' % repr(home))
    # g.pr("computeHomeDir: os.path.expanduser('~'): %s" % os.path.expanduser('~'))

    if home and len(home) > 1 and home[0]=='%' and home[-1]=='%':
        # Get the indirect reference to the true home.
        home = os.getenv(home[1:-1],default=None)

    if home:
        # N.B. This returns the _working_ directory if home is None!
        # This was the source of the 4.3 .leoID.txt problems.
        home = g.os_path_finalize(home,encoding=encoding)
        if (
            not g.os_path_exists(home,encoding) or
            not g.os_path_isdir(home,encoding)
        ):
            home = None

    # g.trace(home)
    return home
#@-node:ekr.20041117151301:computeHomeDir
#@+node:ekr.20060416113431:computeLeoDir
def computeLeoDir ():

    loadDir = g.app.loadDir
    theDir = g.os_path_dirname(loadDir)

    if theDir not in sys.path:
        sys.path.append(theDir)

    if 0: # This is required so we can do import leo.core.leo as leo (as a package)
        theParentDir = g.os_path_dirname(theDir)
        if theParentDir not in sys.path:
            sys.path.append(theParentDir)

    return theDir
#@-node:ekr.20060416113431:computeLeoDir
#@+node:ekr.20031218072017.1937:computeLoadDir
def computeLoadDir():

    """Returns the directory containing leo.py."""

    import leo.core.leoGlobals as g
    import sys

    try:
        # Fix a hangnail: on Windows the drive letter returned by
        # __file__ is randomly upper or lower case!
        # The made for an ugly recent files list.
        path = g.__file__ # was leo.__file__
        if sys.platform=='win32':
            if len(path) > 2 and path[1]==':':
                # Convert the drive name to upper case.
                path = path[0].upper() + path[1:]
        encoding = g.startupEncoding()
        path = g.os_path_finalize(path,encoding=encoding)
        if path:
            loadDir = g.os_path_dirname(path,encoding)
        else: loadDir = None

        if (
            not loadDir or
            not g.os_path_exists(loadDir,encoding) or
            not g.os_path_isdir(loadDir,encoding)
        ):
            loadDir = os.getcwd()
            g.pr("Exception getting load directory")
        loadDir = g.os_path_finalize(loadDir,encoding=encoding)
        # g.es("load dir:",loadDir,color="blue")
        return loadDir
    except:
        g.pr("Exception getting load directory")
        raise
        #import traceback ; traceback.print_exc()
        #return None
#@-node:ekr.20031218072017.1937:computeLoadDir
#@+node:dan.20080410121257.1:computeMachineName
def computeMachineName():
    """Returns the name of the current machine, i.e, HOSTNAME"""
    try:
        import os
        name = os.getenv('HOSTNAME')
        if not name:
            name = os.getenv('COMPUTERNAME')
        if not name:
            import socket
            name = socket.gethostname()
    except Exception:
        name = ''

    # g.trace(name)

    return name
#@-node:dan.20080410121257.1:computeMachineName
#@+node:ekr.20050328133444:computeStandardDirectories
def computeStandardDirectories():

    '''Set g.app.loadDir, g.app.homeDir, g.app.homeLeoDir and g.app.globalConfigDir.'''

    if 0:
        import sys
        for s in sys.path: g.trace(s)

    g.app.loadDir = g.computeLoadDir()
        # Depends on g.app.tkEncoding: uses utf-8 for now.

    g.app.leoDir = g.computeLeoDir()

    g.app.homeDir = g.computeHomeDir()

    # New in Leo 4.5 b4: create homeLeoDir if needed.
    g.app.homeLeoDir = homeLeoDir = g.os_path_finalize(
        g.os_path_join(g.app.homeDir,'.leo'))

    if not g.os_path_exists(homeLeoDir):
        g.makeAllNonExistentDirectories(homeLeoDir,force=True)

    g.app.extensionsDir = g.os_path_finalize(
        g.os_path_join(g.app.loadDir,'..','extensions'))

    g.app.globalConfigDir = g.computeGlobalConfigDir()

    g.app.testDir = g.os_path_finalize(
        g.os_path_join(g.app.loadDir,'..','test'))

    g.app.user_xresources_path = g.os_path_join(g.app.homeDir,'.leo_xresources')
#@-node:ekr.20050328133444:computeStandardDirectories
#@+node:ekr.20041117151301.1:startupEncoding
def startupEncoding ():

    import leo.core.leoGlobals as g
    import sys

    if sys.platform=="win32": # "mbcs" exists only on Windows.
        encoding = "mbcs"
    elif sys.platform=="dawwin":
        encoding = "utf-8"
    else:
        encoding = g.app.tkEncoding

    return encoding
#@-node:ekr.20041117151301.1:startupEncoding
#@-node:ekr.20050304072744:Compute directories... (leoGlobals)
#@+node:ekr.20031218072017.1380:g.Directive utils...
# New in Leo 4.6:
# g.findAtTabWidthDirectives, g.findLanguageDirectives and
# g.get_directives_dict use re module for faster searching.
#@nonl
#@+node:EKR.20040504150046.4:g.comment_delims_from_extension
def comment_delims_from_extension(filename):

    """
    Return the comment delims corresponding to the filename's extension.

    >>> import leo.core.leoGlobals as g
    >>> g.comment_delims_from_extension(".py")
    ('#', None, None)

    >>> g.comment_delims_from_extension(".c")
    ('//', '/*', '*/')

    >>> g.comment_delims_from_extension(".html")
    (None, '<!--', '-->')

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
        return None,None,None
#@-node:EKR.20040504150046.4:g.comment_delims_from_extension
#@+node:ekr.20071109165315:g.computeRelativePath
def computeRelativePath (path):

    if len(path) > 2 and (
        (path[0]=='<' and path[-1] == '>') or
        (path[0]=='"' and path[-1] == '"') or
        (path[0]=="'" and path[-1] == "'")
    ):
        path = path[1:-1].strip()

    # We want a *relative* path, not an absolute path.
    return path
#@-node:ekr.20071109165315:g.computeRelativePath
#@+node:ekr.20090214075058.8:g.findAtTabWidthDirectives (must be fast)
g_tabwidth_pat = re.compile(r'(^@tabwidth)',re.MULTILINE)

def findTabWidthDirectives(c,p):

    '''Return the language in effect at position p.'''

    if c is None:
        return # c may be None for testing.

    w = None
    for p in p.self_and_parents_iter(copy=True):
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
#@-node:ekr.20090214075058.8:g.findAtTabWidthDirectives (must be fast)
#@+node:ekr.20090214075058.6:g.findLanguageDirectives (must be fast)
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
    for p in p.self_and_parents_iter(copy=True):
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
#@-node:ekr.20090214075058.6:g.findLanguageDirectives (must be fast)
#@+node:ekr.20031218072017.1385:g.findReference
#@+at 
#@nonl
# We search the descendents of v looking for the definition node matching 
# name.
# There should be exactly one such node (descendents of other definition nodes 
# are not searched).
#@-at
#@@c

def findReference(c,name,root):

    for p in root.subtree_iter():
        assert(p!=root)
        if p.matchHeadline(name) and not p.isAtIgnoreNode():
            return p

    # g.trace("not found:",name,root)
    return c.nullPosition()
#@-node:ekr.20031218072017.1385:g.findReference
#@+node:ekr.20090214075058.9:g.get_directives_dict (must be fast)
# The caller passes [root_node] or None as the second arg.
# This allows us to distinguish between None and [None].

g_noweb_root = re.compile('<'+'<'+'*'+'>'+'>'+'=',re.MULTILINE)

def get_directives_dict(p,root=None):

    """Scan p for @directives found in globalDirectiveList.

    Returns a dict containing pointers to the start of each directive"""

    trace = False and not g.unitTesting

    if root: root_node = root[0]
    d = {}

    # Do this every time so plugins can add directives.
    pat = g.compute_directives_re()
    directives_pat = re.compile(pat,re.MULTILINE)

    # The headline has higher precedence because it is more visible.
    for kind,s in (('body',p.h),('head',p.b)):
        anIter = directives_pat.finditer(s)
        for m in anIter:
            word = m.group(0)[1:] # Omit the @
            i = m.start(0)
            if word.strip() not in d:
                j = i + 1 + len(word)
                k = g.skip_line(s,j)
                val = s[j:k].strip()
                if trace: g.trace(word,repr(val))
                d[word.strip()] = val

    if root:
        anIter = g_noweb_root.finditer(p.b)
        for m in anIter:
            if root_node:
                d["root"]=0 # value not immportant
            else:
                g.es('%s= requires @root in the headline' % (
                    g.angleBrackets('*')))
            break

    if trace: g.trace('%4d' % (len(p.h) + len(p.b)),g.callers(5))
    return d
#@+node:ekr.20090214075058.10:compute_directives_re
def compute_directives_re ():

    '''Return an re pattern which will match all Leo directives.'''

    global globalDirectiveList

    aList = ['^@%s' % z for z in globalDirectiveList
                if z != 'others']

    # @others can have leading whitespace.
    aList.append(r'^\s@others')

    return '|'.join(aList)
#@-node:ekr.20090214075058.10:compute_directives_re
#@-node:ekr.20090214075058.9:g.get_directives_dict (must be fast)
#@+node:ekr.20080827175609.1:g.get_directives_dict_list (must be fast)
def get_directives_dict_list(p1):

    """Scans p and all its ancestors for directives.

    Returns a list of dicts containing pointers to
    the start of each directive"""

    trace = False and not g.unitTesting

    if trace: time1 = g.getTime()

    result = [] ; p1 = p1.copy()

    for p in p1.self_and_parents_iter():
        if p.hasParent(): root = None
        else:             root = [p.copy()]
        result.append(g.get_directives_dict(p,root=root))

    if trace:
        n = len(p1.h) + len(p1.b)
        g.trace('%4d %s' % (n,g.timeSince(time1)))

    return result
#@-node:ekr.20080827175609.1:g.get_directives_dict_list (must be fast)
#@+node:ekr.20031218072017.1386:g.getOutputNewline
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
    return s
#@-node:ekr.20031218072017.1386:g.getOutputNewline
#@+node:ekr.20080827175609.52:g.scanAtCommentAndLanguageDirectives
def scanAtCommentAndAtLanguageDirectives(aList):

    '''Scan aList for @comment and @language directives.

    @comment should follow @language if both appear in the same node.'''

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
            return {'language':lang,'comment':comment,'delims':delims}

    return None
#@-node:ekr.20080827175609.52:g.scanAtCommentAndLanguageDirectives
#@+node:ekr.20080827175609.32:g.scanAtEncodingDirectives
def scanAtEncodingDirectives(aList):

    '''Scan aList for @encoding directives.'''

    for d in aList:
        encoding = d.get('encoding')
        if encoding and g.isValidEncoding(encoding):
            # g.trace(encoding)
            return encoding
        elif encoding and not g.app.unitTesting:
            g.es("invalid @encoding:",encoding,color="red")

    return None
#@-node:ekr.20080827175609.32:g.scanAtEncodingDirectives
#@+node:ekr.20080827175609.53:g.scanAtHeaderDirectives
def scanAtHeaderDirectives(aList):

    '''scan aList for @header and @noheader directives.'''

    for d in aList:
        if d.get('header') and d.get('noheader'):
            g.es_print("conflicting @header and @noheader directives",color='red')
#@nonl
#@-node:ekr.20080827175609.53:g.scanAtHeaderDirectives
#@+node:ekr.20080827175609.33:g.scanAtLineendingDirectives
def scanAtLineendingDirectives(aList):

    '''Scan aList for @lineending directives.'''

    for d in aList:

        e = d.get('lineending')
        if e in ("cr","crlf","lf","nl","platform"):
            lineending = g.getOutputNewline(name=e)
            return lineending
        # else:
            # g.es("invalid @lineending directive:",e,color="red")

    return None
#@-node:ekr.20080827175609.33:g.scanAtLineendingDirectives
#@+node:ekr.20080827175609.34:g.scanAtPagewidthDirectives
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
                    g.es("ignoring @pagewidth",s,color="red")

    return None
#@-node:ekr.20080827175609.34:g.scanAtPagewidthDirectives
#@+node:ekr.20031218072017.3154:g.scanAtRootOptions
def scanAtRootOptions (s,i,err_flag=False):

    # The @root has been eaten when called from tangle.scanAllDirectives.
    if g.match(s,i,"@root"):
        i += len("@root")
        i = g.skip_ws(s,i)

    mode = None 
    while g.match(s,i,'-'):
        #@        << scan another @root option >>
        #@+node:ekr.20031218072017.3155:<< scan another @root option >>
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
        while i < len(s) and s[i] not in (' ','\t','-'):
            i += 1

        if err > -1 and err_flag:
            z_opt = s[err:i]
            z_line = g.get_line(s,i)
            g.es("unknown option:",z_opt,"in",z_line)
        #@-node:ekr.20031218072017.3155:<< scan another @root option >>
        #@nl

    if mode == None:
        doc = app.config.at_root_bodies_start_in_doc_mode
        mode = g.choose(doc,"doc","code")

    return i,mode
#@-node:ekr.20031218072017.3154:g.scanAtRootOptions
#@+node:ekr.20080827175609.37:g.scanAtTabwidthDirectives
def scanAtTabwidthDirectives(aList,issue_error_flag=False):

    '''Scan aList for @tabwidth directives.'''

    for d in aList:
        s = d.get('tabwidth')
        if s is not None:
            junk,val = g.skip_long(s,0)

            if val not in (None,0):
                # g.trace(val)
                return val
            else:
                if issue_error_flag and not g.app.unitTesting:
                    g.es("ignoring @tabwidth",s,color="red")

    return None
#@-node:ekr.20080827175609.37:g.scanAtTabwidthDirectives
#@+node:ekr.20080831084419.4:g.scanAtWrapDirectives
def scanAtWrapDirectives(aList,issue_error_flag=False):

    '''Scan aList for @wrap and @nowrap directives.'''

    for d in aList:
        if d.get('wrap') is not None:
            return True
        elif d.get('nowrap') is not None:
            return False

    return None
#@nonl
#@-node:ekr.20080831084419.4:g.scanAtWrapDirectives
#@+node:ekr.20080901195858.4:g.scanDirectives  (for compatibility only)
def scanDirectives(c,p=None):

    return c.scanAllDirectives(p)
#@nonl
#@-node:ekr.20080901195858.4:g.scanDirectives  (for compatibility only)
#@+node:ekr.20040715155607:g.scanForAtIgnore
def scanForAtIgnore(c,p):

    """Scan position p and its ancestors looking for @ignore directives."""

    if g.app.unitTesting:
        return False # For unit tests.

    for p in p.self_and_parents_iter():
        d = g.get_directives_dict(p)
        if 'ignore' in d:
            return True

    return False
#@-node:ekr.20040715155607:g.scanForAtIgnore
#@+node:ekr.20040712084911.1:g.scanForAtLanguage
def scanForAtLanguage(c,p):

    """Scan position p and p's ancestors looking only for @language and @ignore directives.

    Returns the language found, or c.target_language."""

    # Unlike the code in x.scanAllDirectives, this code ignores @comment directives.

    if c and p:
        for p in p.self_and_parents_iter():
            d = g.get_directives_dict(p)
            if 'language' in d:
                z = d["language"]
                language,delim1,delim2,delim3 = g.set_language(z,0)
                return language

    return c.target_language
#@-node:ekr.20040712084911.1:g.scanForAtLanguage
#@+node:ekr.20041123094807:g.scanForAtSettings
def scanForAtSettings(p):

    """Scan position p and its ancestors looking for @settings nodes."""

    for p in p.self_and_parents_iter():
        h = p.h
        h = g.app.config.canonicalizeSettingName(h)
        if h.startswith("@settings"):
            return True

    return False
#@-node:ekr.20041123094807:g.scanForAtSettings
#@+node:ekr.20031218072017.1382:g.set_delims_from_language
# Returns a tuple (single,start,end) of comment delims

def set_delims_from_language(language):

    # g.trace(g.callers())

    val = g.app.language_delims_dict.get(language)
    # if language.startswith('huh'): g.pdb()

    if val:
        delim1,delim2,delim3 = g.set_delims_from_string(val)
        if delim2 and not delim3:
            return None,delim1,delim2
        else: # 0,1 or 3 params.
            return delim1,delim2,delim3
    else:
        return None, None, None # Indicate that no change should be made
#@-node:ekr.20031218072017.1382:g.set_delims_from_language
#@+node:ekr.20031218072017.1383:g.set_delims_from_string
def set_delims_from_string(s):

    """Returns (delim1, delim2, delim2), the delims following the @comment directive.

    This code can be called from @language logic, in which case s can point at @comment"""

    # Skip an optional @comment
    tag = "@comment"
    i = 0
    if g.match_word(s,i,tag):
        i += len(tag)

    count = 0 ; delims = [None, None, None]
    while count < 3 and i < len(s):
        i = j = g.skip_ws(s,i)
        while i < len(s) and not g.is_ws(s[i]) and not g.is_nl(s,i):
            i += 1
        if j == i: break
        delims[count] = s[j:i]
        count += 1

    # 'rr 09/25/02
    if count == 2: # delims[0] is always the single-line delim.
        delims[2] = delims[1]
        delims[1] = delims[0]
        delims[0] = None

    # 7/8/02: The "REM hack": replace underscores by blanks.
    # 9/25/02: The "perlpod hack": replace double underscores by newlines.
    for i in range(0,3):
        if delims[i]:
            delims[i] = delims[i].replace("__",'\n').replace('_',' ')

    return delims[0], delims[1], delims[2]
#@-node:ekr.20031218072017.1383:g.set_delims_from_string
#@+node:ekr.20031218072017.1384:g.set_language
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
#@-node:ekr.20031218072017.1384:g.set_language
#@+node:ekr.20081001062423.9:g.setDefaultDirectory
# This is a refactoring, used by leoImport.scanDefaultDirectory and
# atFile.scanDefault directory

def setDefaultDirectory(c,p,importing=False):

    '''Set default_directory by scanning @path directives.
    Return (default_directory,error_message).'''

    default_directory = '' ; error = ''
    if not p: return default_directory,error

    #@    << Set path from @file node >>
    #@+node:ekr.20081001062423.10:<< Set path from @file node >>
    # An absolute path in an @file node over-rides everything else.
    # A relative path gets appended to the relative path by the open logic.

    name = p.anyAtFileNodeName()
    theDir = g.choose(name,g.os_path_dirname(name),None)

    if theDir and g.os_path_isabs(theDir):
        if g.os_path_exists(theDir):
            default_directory = theDir
        else:
            default_directory = g.makeAllNonExistentDirectories(theDir,c=c)
            if not default_directory:
                error = "Directory \"%s\" does not exist" % theDir
    #@-node:ekr.20081001062423.10:<< Set path from @file node >>
    #@nl

    if not default_directory:
        # Scan for @path directives.
        aList = g.get_directives_dict_list(p)
        path = c.scanAtPathDirectives(aList)
        if path:
            #@            << handle @path >>
            #@+node:ekr.20081001062423.11:<< handle @path >>
            path = g.computeRelativePath (path)

            if path:
                base = g.getBaseDirectory(c) # returns "" on error.
                path = c.os_path_finalize_join(base,path)

                if g.os_path_isabs(path):
                    if g.os_path_exists(path):
                        default_directory = path
                    else:
                        default_directory = g.makeAllNonExistentDirectories(path,c=c)
                        if not default_directory:
                            error = "invalid @path: %s" % path
                        else:
                            error = "ignoring bad @path: %s" % path
            else:
                error = "ignoring empty @path"
            #@-node:ekr.20081001062423.11:<< handle @path >>
            #@nl

    if not default_directory:
        #@        << Set current directory >>
        #@+node:ekr.20081001062423.12:<< Set current directory >>
        # This code is executed if no valid absolute path was specified in the @file node or in an @path directive.

        assert(not default_directory)

        if c.frame:
            base = g.getBaseDirectory(c) # returns "" on error.
            for theDir in (c.tangle_directory,c.frame.openDirectory,c.openDirectory):
                if theDir and len(theDir) > 0:
                    theDir = c.os_path_finalize_join(base,theDir) # Bug fix: 2008/9/23
                    if g.os_path_isabs(theDir): # Errors may result in relative or invalid path.
                        if g.os_path_exists(theDir):
                            default_directory = theDir ; break
                        else:
                            default_directory = g.makeAllNonExistentDirectories(theDir,c=c)
        #@-node:ekr.20081001062423.12:<< Set current directory >>
        #@nl

    if not default_directory and not importing:
        # This should never happen: c.openDirectory should be a good last resort.
        error = "No absolute directory specified anywhere."

    # g.trace('returns',default_directory)
    return default_directory, error
#@-node:ekr.20081001062423.9:g.setDefaultDirectory
#@-node:ekr.20031218072017.1380:g.Directive utils...
#@+node:ekr.20031218072017.3100:wrap_lines
#@+at 
#@nonl
# Important note: this routine need not deal with leading whitespace.  
# Instead, the caller should simply reduce pageWidth by the width of leading 
# whitespace wanted, then add that whitespace to the lines returned here.
# 
# The key to this code is the invarient that line never ends in whitespace.
#@-at
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
            if len(line) > 0 and wordLen > 0: wordLen += len(" ")
            if wordLen + len(line) <= outputLineWidth:
                if wordLen > 0:
                    #@                    << place blank and word on the present line >>
                    #@+node:ekr.20031218072017.3101:<< place blank and word on the present line >>
                    if len(line) == 0:
                        # Just add the word to the start of the line.
                        line = word
                    else:
                        # Add the word, preceeded by a blank.
                        line = " ".join([line,word]) # DTHEIN 18-JAN-2004: better syntax
                    #@-node:ekr.20031218072017.3101:<< place blank and word on the present line >>
                    #@nl
                else: pass # discard the trailing whitespace.
            else:
                #@                << place word on a new line >>
                #@+node:ekr.20031218072017.3102:<< place word on a new line >>
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
                #@-node:ekr.20031218072017.3102:<< place word on a new line >>
                #@nl
    if len(line) > 0:
        result.append(line)
    # g.trace(result)
    return result
#@-node:ekr.20031218072017.3100:wrap_lines
#@+node:ekr.20090517020744.5889:unit tests for new directives
if g.unitTesting:

    #@    @+others
    #@+node:ekr.20090517020744.5890:@test c.scanAllDirectives
    #@@language python
    #@@comment a b c
        # @comment must follow @language
    #@@tabwidth -4
    #@@pagewidth 72
    #@@encoding utf-8
    #@@lineending crlf

    d = c.scanAllDirectives(p)
    # print g.dictToString(d)

    table = (
        ('delims', ('a','b','c'),),
        ('encoding','utf-8'),
        ('language','python'),
        ('lineending','\r\n'),
        ('pagewidth',72),
        ('tabwidth',-4),
    )

    for kind,expected in table:
        got = d.get(kind)
        assert got == expected, 'kind: %s, expected %s, got %s' % (
            kind,repr(expected),repr(got))
    #@-node:ekr.20090517020744.5890:@test c.scanAllDirectives
    #@+node:ekr.20090517020744.5891:@test c.scanAtRootDirectives root-code
    #@@root-code

    aList = g.get_directives_dict_list(p)
    s = c.scanAtRootDirectives(aList)

    assert s == 'code',repr(s)
    #@nonl
    #@-node:ekr.20090517020744.5891:@test c.scanAtRootDirectives root-code
    #@+node:ekr.20090517020744.5892:@test c.scanAtRootDirectives root-doc
    #@@root-doc

    aList = g.get_directives_dict_list(p)
    s = c.scanAtRootDirectives(aList)

    assert s == 'doc',repr(s)
    #@nonl
    #@-node:ekr.20090517020744.5892:@test c.scanAtRootDirectives root-doc
    #@+node:ekr.20090517020744.5893:@test g.get_directives_dict
    #@@language python
    #@@comment a b c
        # @comment must follow @language.
    #@@tabwidth -8
    #@@pagewidth 72
    #@@encoding utf-8

    # @path xyzzy # Creates folder called xyzzy: interferes with other unit tests.

    d = g.get_directives_dict(p)

    # assert d.get('_p') == p # Never used, and a bad idea.
    assert d.get('language') == 'python'
    assert d.get('tabwidth') == '-8'
    assert d.get('pagewidth') == '72'
    assert d.get('encoding') == 'utf-8'
    assert d.get('comment') == 'a b c'
    # assert d.get('path').endswith('xyzzy')
    #@-node:ekr.20090517020744.5893:@test g.get_directives_dict
    #@+node:ekr.20090517020744.5894:@test g.scanAtHeaderDirectives header
    #@@header

    aList = g.get_directives_dict_list(p)
    g.scanAtHeaderDirectives(aList)
    #@-node:ekr.20090517020744.5894:@test g.scanAtHeaderDirectives header
    #@+node:ekr.20090517020744.5895:@test g.scanAtHeaderDirectives noheader
    #@@noheader

    aList = g.get_directives_dict_list(p)
    g.scanAtHeaderDirectives(aList)
    #@-node:ekr.20090517020744.5895:@test g.scanAtHeaderDirectives noheader
    #@+node:ekr.20090517020744.5896:@test g.scanAtLineendingDirectives cr
    #@@lineending cr

    aList = g.get_directives_dict_list(p)
    s = g.scanAtLineendingDirectives(aList)

    assert s == '\r'
    #@-node:ekr.20090517020744.5896:@test g.scanAtLineendingDirectives cr
    #@+node:ekr.20090517020744.5897:@test g.scanAtLineendingDirectives crlf
    #@@lineending crlf

    aList = g.get_directives_dict_list(p)
    s = g.scanAtLineendingDirectives(aList)
    # print ('@lineending: %s'%repr(s))

    assert s == '\r\n'
    #@-node:ekr.20090517020744.5897:@test g.scanAtLineendingDirectives crlf
    #@+node:ekr.20090517020744.5898:@test g.scanAtLineendingDirectives lf
    #@@lineending lf

    aList = g.get_directives_dict_list(p)
    s = g.scanAtLineendingDirectives(aList)

    assert s == '\n'
    #@-node:ekr.20090517020744.5898:@test g.scanAtLineendingDirectives lf
    #@+node:ekr.20090517020744.5899:@test g.scanAtLineendingDirectives nl
    #@@lineending nl

    aList = g.get_directives_dict_list(p)
    s = g.scanAtLineendingDirectives(aList)

    assert s == '\n'
    #@-node:ekr.20090517020744.5899:@test g.scanAtLineendingDirectives nl
    #@+node:ekr.20090517020744.5900:@test g.scanAtLineendingDirectives platform
    #@@lineending platform

    import sys

    aList = g.get_directives_dict_list(p)
    s = g.scanAtLineendingDirectives(aList)

    if sys.platform.startswith('win'):
        assert s == '\r\n'
    else:
        assert s == '\n'
    #@-node:ekr.20090517020744.5900:@test g.scanAtLineendingDirectives platform
    #@+node:ekr.20090517020744.5901:@test g.scanAtPagewidthDirectives -40
    #@@pagewidth -40

    aList = g.get_directives_dict_list(p)
    n = g.scanAtPagewidthDirectives(aList)

    assert n is None
    #@nonl
    #@-node:ekr.20090517020744.5901:@test g.scanAtPagewidthDirectives -40
    #@+node:ekr.20090517020744.5902:@test g.scanAtPagewidthDirectives 40
    #@@pagewidth 40

    aList = g.get_directives_dict_list(p)
    n = g.scanAtPagewidthDirectives(aList)

    assert n == 40
    #@nonl
    #@-node:ekr.20090517020744.5902:@test g.scanAtPagewidthDirectives 40
    #@+node:ekr.20090517020744.5912:@test g.scanAtTabwidthDirectives +6
    #@@tabwidth 6

    aList = g.get_directives_dict_list(p)
    n = g.scanAtTabwidthDirectives(aList)

    assert n == 6,repr(n)
    #@nonl
    #@-node:ekr.20090517020744.5912:@test g.scanAtTabwidthDirectives +6
    #@+node:ekr.20090517020744.5913:@test g.scanAtTabwidthDirectives -6
    #@@tabwidth -6

    aList = g.get_directives_dict_list(p)
    n = g.scanAtTabwidthDirectives(aList)

    assert n == -6
    #@nonl
    #@-node:ekr.20090517020744.5913:@test g.scanAtTabwidthDirectives -6
    #@+node:ekr.20090517020744.5914:@test g.scanAtWrapDirectives nowrap
    #@@nowrap

    aList = g.get_directives_dict_list(p)
    s = g.scanAtWrapDirectives(aList)

    assert s is False,repr(s)
    #@nonl
    #@-node:ekr.20090517020744.5914:@test g.scanAtWrapDirectives nowrap
    #@+node:ekr.20090517020744.5915:@test g.scanAtWrapDirectives wrap
    #@@wrap

    aList = g.get_directives_dict_list(p)
    s = g.scanAtWrapDirectives(aList)

    assert s is True,repr(s)
    #@nonl
    #@-node:ekr.20090517020744.5915:@test g.scanAtWrapDirectives wrap
    #@+node:ekr.20090517020744.5916:@test g.scanAtWrapDirectives wrap
    aList = g.get_directives_dict_list(p)
    s = g.scanAtWrapDirectives(aList)

    assert s is None,repr(s)
    #@nonl
    #@-node:ekr.20090517020744.5916:@test g.scanAtWrapDirectives wrap
    #@-others
#@-node:ekr.20090517020744.5889:unit tests for new directives
#@-node:ekr.20031218072017.3099:Commands & Directives
#@+node:ekr.20031218072017.3104:Debugging, Dumping, Timing, Tracing & Sherlock
#@+node:ekr.20031218072017.3105:alert
def alert(message):

    g.es(message)
    g.app.gui.alert(message)
#@-node:ekr.20031218072017.3105:alert
#@+node:ekr.20051023083258:callers & _callerName
def callers (n=8,excludeCaller=True,files=False):

    '''Return a list containing the callers of the function that called g.callerList.

    If the excludeCaller keyword is True (the default), g.callers is not on the list.

    If the files keyword argument is True, filenames are included in the list.
    '''

    # sys._getframe throws ValueError in both cpython and jython if there are less than i entries.
    # The jython stack often has less than 8 entries,
    # so we must be careful to call g._callerName with smaller values of i first.
    result = []
    i = g.choose(excludeCaller,3,2)
    while 1:
        s = g._callerName(i,files=files)
        if s:
            result.append(s)
        if not s or len(result) >= n: break
        i += 1

    result.reverse()
    sep = g.choose(files,'\n',',')
    return sep.join(result)
#@+node:ekr.20031218072017.3107:_callerName
def _callerName (n=1,files=False):

    try: # get the function name from the call stack.
        f1 = sys._getframe(n) # The stack frame, n levels up.
        code1 = f1.f_code # The code object
        if files:
            return '%s:%s' % (g.shortFilename(code1.co_filename),code1.co_name)
        else:
            return code1.co_name # The code name
    except ValueError:
        return '' # The stack is not deep enough.
    except Exception:
        g.es_exception()
        return '' # "<no caller name>"
#@-node:ekr.20031218072017.3107:_callerName
#@-node:ekr.20051023083258:callers & _callerName
#@+node:ekr.20041105091148:g.pdb & test
def pdb (message=''):

    """Fall into pdb."""

    import pdb # Required: we have just defined pdb as a function!

    if message:
        print message
    pdb.set_trace()
#@+node:ekr.20090517020744.5880:@test g.pdb
if g.unitTesting:

    import sys

    # Not a good unit test; it probably will never fail.
    def aFunction(): pass
    assert type(g.pdb)==type(aFunction), 'wrong type for g.pdb: %s' % type(g.pdb)

    class myStdout:
        def write(self,s):
            pass # g.es('From pdb:',s)

    class myStdin:
        def readline (self):
            return 'c' # Return 'c' (continue) for all requests for input.

    def restore():
        sys.stdout,sys.stdin = sys.__stdout__,sys.__stdin__

    try:
        sys.stdin = myStdin() # Essential
        sys.stdout=myStdout() # Optional
        g.pdb()
        restore()
        # assert False,'test of reraising'
    except Exception:
        restore()
        raise
#@-node:ekr.20090517020744.5880:@test g.pdb
#@-node:ekr.20041105091148:g.pdb & test
#@+node:ekr.20031218072017.3108:Dumps
#@+node:ekr.20031218072017.3109:dump
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
#@-node:ekr.20031218072017.3109:dump
#@+node:ekr.20060917120951:es_dump
def es_dump (s,n = 30,title=None):

    if title:
        g.es_print('',title)

    i = 0
    while i < len(s):
        aList = ''.join(['%2x ' % (ord(ch)) for ch in s[i:i+n]])
        g.es_print('',aList)
        i += n
#@nonl
#@-node:ekr.20060917120951:es_dump
#@+node:ekr.20031218072017.3110:es_error & es_print_error
def es_error (*args,**keys):

    color = keys.get('color')

    if color is None and g.app.config:
        keys['color'] = g.app.config.getColor(None,"log_error_color") or 'red'

    g.es(*args,**keys)


def es_print_error (*args,**keys):

    color = keys.get('color')

    if color is None and g.app.config:
        keys['color'] = g.app.config.getColor(None,"log_error_color") or 'red'

    g.es_print(*args,**keys)
#@-node:ekr.20031218072017.3110:es_error & es_print_error
#@+node:ekr.20031218072017.3111:es_event_exception
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
#@-node:ekr.20031218072017.3111:es_event_exception
#@+node:ekr.20031218072017.3112:es_exception & test
def es_exception (full=True,c=None,color="red"):

    typ,val,tb = sys.exc_info()

    fileName,n = g.getLastTracebackFileAndLineNumber()

    if full or g.app.debugSwitch > 0:
        lines = traceback.format_exception(typ,val,tb)
    else:
        lines = traceback.format_exception_only(typ,val)
        if 0: # We might as well print the entire SyntaxError message.
            lines = lines[-1:] # Usually only one line, but more for Syntax errors!

    for line in lines:
        g.es_error(line,color=color)
        if not g.stdErrIsRedirected():
            try:
                g.pr(line)
            except Exception:
                g.pr(g.toEncodedString(line,'ascii'))

    if g.app.debugSwitch > 1:
        import pdb # Be careful: g.pdb may or may not have been defined.
        pdb.set_trace()

    return fileName,n
#@+node:ekr.20090517020744.5874:@test g.es_exception
if g.unitTesting:

    if c.config.redirect_execute_script_output_to_log_pane:
        pass # Test doesn't work when redirection is on.
    else:
        try:
            import sys
            # Catch the output of g.es_exception.
            # We catch the AssertionError, so nothing gets written to stderr.
            sys.stdout = fo = g.fileLikeObject()
            try: # Create an exception to catch.
                assert False, 'Assert False in test_g_es_exception'
            except AssertionError:
                g.es_exception(color='suppress')
                result = fo.get()
                s1 = 'Traceback (most recent call last):'
                s2 = 'AssertionError: Assert False in test_g_es_exception'
                assert result.find(s1) > -1, 'No traceback line: %s' % repr(result)
                assert result.find(s2) > -1, 'No AssertionError line: %s' % repr(result)
        finally:
            # Not needed unless we execute this script as selected text.
            sys.stdout = sys.__stdout__
#@-node:ekr.20090517020744.5874:@test g.es_exception
#@-node:ekr.20031218072017.3112:es_exception & test
#@+node:ekr.20061015090538:es_exception_type
def es_exception_type (c=None,color="red"):

    # exctype is a Exception class object; value is the error message.
    exctype, value = sys.exc_info()[:2]

    g.es_print('','%s, %s' % (exctype.__name__, value),color=color)
#@-node:ekr.20061015090538:es_exception_type
#@+node:ekr.20040731204831:getLastTracebackFileAndLineNumber
def getLastTracebackFileAndLineNumber():

    typ,val,tb = sys.exc_info()

    if g.isPython3:
        if typ in (SyntaxError,IndentationError):
            # Syntax and indentation errors are a special case.
            # extract_tb does _not_ return the proper line number!
            # This code is similar to the code in format_exception_only(!!)
            try:
                # g.es_print('',repr(val))
                msg,(filename, lineno, offset, line) = val
                return filename,lineno
            except Exception:
                g.trace("bad line number")
                return None,0

        else:
            # The proper line number is the second element in the last tuple.
            data = traceback.extract_tb(tb)
            if data:
                # g.es_print('',repr(data))
                item = data[-1]
                filename = item[0]
                n = item[1]
                return filename,n
            else:
                return None,0


    else:

        if typ in (exceptions.SyntaxError,exceptions.IndentationError):
            # Syntax and indentation errors are a special case.
            # extract_tb does _not_ return the proper line number!
            # This code is similar to the code in format_exception_only(!!)
            try:
                # g.es_print('',repr(val))
                msg,(filename, lineno, offset, line) = val
                return filename,lineno
            except Exception:
                g.trace("bad line number")
                return None,0

        else:
            # The proper line number is the second element in the last tuple.
            data = traceback.extract_tb(tb)
            if data:
                # g.es_print('',repr(data))
                item = data[-1]
                filename = item[0]
                n = item[1]
                return filename,n
            else:
                return None,0
#@-node:ekr.20040731204831:getLastTracebackFileAndLineNumber
#@+node:ekr.20031218072017.3113:printBindings
def print_bindings (name,window):

    bindings = window.bind()

    g.pr("\nBindings for", name)
    for b in bindings:
        g.pr(b)
#@-node:ekr.20031218072017.3113:printBindings
#@+node:ekr.20031218072017.3114:printGlobals
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
#@-node:ekr.20031218072017.3114:printGlobals
#@+node:ekr.20070510074941:g.printEntireTree
def printEntireTree(c,tag=''):

    g.pr('printEntireTree','=' * 50)
    g.pr('printEntireTree',tag,'root',c.rootPosition())
    for p in c.allNodes_iter():
        g.pr('..'*p.level(),p.v)
#@nonl
#@-node:ekr.20070510074941:g.printEntireTree
#@+node:ekr.20031218072017.3115:printLeoModules
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
#@-node:ekr.20031218072017.3115:printLeoModules
#@-node:ekr.20031218072017.3108:Dumps
#@+node:ekr.20031218072017.1317:file/module/plugin_date
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
#@-node:ekr.20031218072017.1317:file/module/plugin_date
#@+node:ekr.20031218072017.3121:redirecting stderr and stdout to Leo's log pane
class redirectClass:

    """A class to redirect stdout and stderr to Leo's log pane."""

    #@    << redirectClass methods >>
    #@+node:ekr.20031218072017.1656:<< redirectClass methods >>
    #@+others
    #@+node:ekr.20041012082437:redirectClass.__init__
    def __init__ (self):

        self.old = None
    #@-node:ekr.20041012082437:redirectClass.__init__
    #@+node:ekr.20041012082437.1:isRedirected
    def isRedirected (self):

        return self.old != None
    #@-node:ekr.20041012082437.1:isRedirected
    #@+node:ekr.20041012082437.2:flush
    # For LeoN: just for compatibility.

    def flush(self, *args):
        return
    #@-node:ekr.20041012082437.2:flush
    #@+node:ekr.20041012091252:rawPrint
    def rawPrint (self,s):

        if self.old:
            self.old.write(s+'\n')
        else:
            g.pr(s)
    #@-node:ekr.20041012091252:rawPrint
    #@+node:ekr.20041012082437.3:redirect
    def redirect (self,stdout=1):

        if g.app.batchMode:
            # Redirection is futile in batch mode.
            return

        if not self.old:
            if stdout:
                self.old,sys.stdout = sys.stdout,self
            else:
                self.old,sys.stderr = sys.stderr,self
    #@-node:ekr.20041012082437.3:redirect
    #@+node:ekr.20041012082437.4:undirect
    def undirect (self,stdout=1):

        if self.old:
            if stdout:
                sys.stdout,self.old = self.old,None
            else:
                sys.stderr,self.old = self.old,None
    #@-node:ekr.20041012082437.4:undirect
    #@+node:ekr.20041012082437.5:write
    def write(self,s):

        if self.old:
            if app.log:
                app.log.put(s)
            else:
                self.old.write(s+'\n')
        else:
            # Can happen when g.batchMode is True.
            g.pr(s)
    #@-node:ekr.20041012082437.5:write
    #@-others
    #@-node:ekr.20031218072017.1656:<< redirectClass methods >>
    #@nl

# Create two redirection objects, one for each stream.
redirectStdErrObj = redirectClass()
redirectStdOutObj = redirectClass()

#@<< define convenience methods for redirecting streams >>
#@+node:ekr.20031218072017.3122:<< define convenience methods for redirecting streams >>
#@+others
#@+node:ekr.20041012090942:redirectStderr & redirectStdout
# Redirect streams to the current log window.
def redirectStderr():
    global redirectStdErrObj
    redirectStdErrObj.redirect(stdout=False)

def redirectStdout():
    global redirectStdOutObj
    redirectStdOutObj.redirect()
#@-node:ekr.20041012090942:redirectStderr & redirectStdout
#@+node:ekr.20041012090942.1:restoreStderr & restoreStdout
# Restore standard streams.
def restoreStderr():
    global redirectStdErrObj
    redirectStdErrObj.undirect(stdout=False)

def restoreStdout():
    global redirectStdOutObj
    redirectStdOutObj.undirect()
#@-node:ekr.20041012090942.1:restoreStderr & restoreStdout
#@+node:ekr.20041012090942.2:stdErrIsRedirected & stdOutIsRedirected
def stdErrIsRedirected():
    global redirectStdErrObj
    return redirectStdErrObj.isRedirected()

def stdOutIsRedirected():
    global redirectStdOutObj
    return redirectStdOutObj.isRedirected()
#@-node:ekr.20041012090942.2:stdErrIsRedirected & stdOutIsRedirected
#@+node:ekr.20041012090942.3:rawPrint
# Send output to original stdout.

def rawPrint(s):

    global redirectStdOutObj

    redirectStdOutObj.rawPrint(s)
#@-node:ekr.20041012090942.3:rawPrint
#@-others
#@-node:ekr.20031218072017.3122:<< define convenience methods for redirecting streams >>
#@nl

if 0: # Test code: may be executed in the child node.
    #@    << test code >>
    #@+node:ekr.20031218072017.3123:<< test code >>
    import leo.core.leoGlobals as g ; import sys
    print >> sys.stdout, "stdout isRedirected:", g.stdOutIsRedirected()
    print >> sys.stderr, "stderr isRedirected:", g.stdErrIsRedirected()

    # stderr
    import leo.core.leoGlobals as g ; import sys
    g.redirectStderr()
    print >> sys.stdout, "stdout isRedirected:", g.stdOutIsRedirected()
    print >> sys.stderr, "stderr isRedirected:", g.stdErrIsRedirected()

    import leo.core.leoGlobals as g ; import sys
    g.restoreStderr()
    print >> sys.stdout, "stdout isRedirected:", g.stdOutIsRedirected()
    print >> sys.stderr, "stderr isRedirected:", g.stdErrIsRedirected()

    # stdout
    import leo.core.leoGlobals as g ; import sys
    g.restoreStdout()
    print >> sys.stdout, "stdout isRedirected:", g.stdOutIsRedirected()
    print >> sys.stderr, "stderr isRedirected:", g.stdErrIsRedirected()

    import leo.core.leoGlobals as g ; import sys
    g.redirectStdout()
    print >> sys.stdout, "stdout isRedirected:", g.stdOutIsRedirected()
    print >> sys.stderr, "stderr isRedirected:", g.stdErrIsRedirected()
    #@-node:ekr.20031218072017.3123:<< test code >>
    #@nl
#@-node:ekr.20031218072017.3121:redirecting stderr and stdout to Leo's log pane
#@+node:ekr.20080729142651.1:g.getIvarsDict and checkUnchangedIvars
def getIvarsDict(obj):

    '''Return a dictionary of ivars:values for non-methods of obj.'''

    import types

    d = dict(
        [[key,getattr(obj,key)] for key in dir(obj)
            if type (getattr(obj,key)) != types.MethodType])

    # g.pr(g.listToString(sorted(d)))
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
#@-node:ekr.20080729142651.1:g.getIvarsDict and checkUnchangedIvars
#@+node:ekr.20031218072017.3127:g.get_line & get_line__after
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
#@nonl
#@-node:ekr.20031218072017.3127:g.get_line & get_line__after
#@+node:ekr.20031218072017.3128:pause
def pause (s):

    g.pr(s)

    i = 0 ; n = long(1000) * long(1000)
    while i < n:
        i += 1
#@-node:ekr.20031218072017.3128:pause
#@+node:ekr.20050819064157:print_obj & toString
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
#@-node:ekr.20050819064157:print_obj & toString
#@+node:ekr.20041224080039:print_dict & dictToString
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
#@-node:ekr.20041224080039:print_dict & dictToString
#@+node:ekr.20041126060136:print_list & listToString
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

def listToString(aList,tag=None,sort=False,indent=''):

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
    if tag:
        return '[%s...\n%s\n]' % (tag,s)
    else:
        return '[%s]' % s
#@-node:ekr.20041126060136:print_list & listToString
#@+node:ekr.20041122153823:print_stack (printStack)
def print_stack():

    traceback.print_stack()

printStack = print_stack
#@-node:ekr.20041122153823:print_stack (printStack)
#@+node:ekr.20031218072017.3129:Sherlock... (trace)
#@+at 
#@nonl
# Starting with this release, you will see trace statements throughout the 
# code.  The trace function is defined in leoGlobals.py; trace implements much 
# of the functionality of my Sherlock tracing package.  Traces are more 
# convenient than print statements for two reasons: 1) you don't need explicit 
# trace names and 2) you can disable them without recompiling.
# 
# In the following examples, suppose that the call to trace appears in 
# function f.
# 
# g.trace(string) prints string if tracing for f has been enabled.  For 
# example, the following statment prints from s[i] to the end of the line if 
# tracing for f has been enabled.
# 
#   j = g.skip_line(s,i) ; g.trace(s[i:j])
# 
# g.trace(function) exectutes the function if tracing for f has been enabled.  
# For example,
# 
#   g.trace(self.f2)
# 
# You enable and disable tracing by calling g.init_trace(args).  Examples:
# 
#   g.init_trace("+*")         # enable all traces
#   g.init_trace("+a","+b")    # enable traces for a and b
#   g.init_trace(("+a","+b"))  # enable traces for a and b
#   g.init_trace("-a")         # disable tracing for a
#   traces = g.init_trace("?") # return the list of enabled traces
# 
# If two arguments are supplied to trace, the first argument is the 
# "tracepoint name" and the second argument is the "tracepoint action" as 
# shown in the examples above.  If tracing for the tracepoint name is enabled, 
# the tracepoint action is printed (if it is a string) or exectuted (if it is 
# a function name).
# 
# "*" will not match an explicit tracepoint name that starts with a minus 
# sign.  For example,
# 
#   g.trace_tag("-nocolor", self.disable_color)
#@-at
#@+node:ekr.20031218072017.3130:init_sherlock
# Called by startup code.
# Args are all the arguments on the command line.

def init_sherlock (args):

    g.init_trace(args,echo=0)
    # g.trace("sys.argv:",sys.argv)
#@-node:ekr.20031218072017.3130:init_sherlock
#@+node:ekr.20031218072017.3131:get_Sherlock_args
#@+at 
#@nonl
# It no args are given we attempt to get them from the "SherlockArgs" file.  
# If there are still no arguments we trace everything.  This default makes 
# tracing much more useful in Python.
#@-at
#@@c

def get_Sherlock_args (args):

    if not args or len(args)==0:
        try:
            fn = g.os_path_join(app.loadDir,"SherlockArgs")
            f = open(fn)
            args = f.readlines()
            f.close()
        except Exception: pass
    elif type(args[0]) == type(("1","2")):
        args = args[0] # strip away the outer tuple.

    # No args means trace everything.
    if not args or len(args)==0: args = ["+*"] 
    # g.pr("get_Sherlock_args:", args)
    return args
#@-node:ekr.20031218072017.3131:get_Sherlock_args
#@+node:ekr.20031218072017.3132:init_trace
def init_trace(args,echo=1):

    t = app.trace_list
    args = g.get_Sherlock_args(args)

    for arg in args:
        if arg[0] in string.ascii_letters: prefix = '+'
        else: prefix = arg[0] ; arg = arg[1:]

        if prefix == '?':
            g.pr("trace list:", t)
        elif prefix == '+' and not arg in t:
            t.append(arg.lower())
            if echo:
                g.pr("enabling:", arg)
        elif prefix == '-' and arg in t:
            t.remove(arg.lower())
            if echo:
                g.pr("disabling:", arg)
        else:
            g.pr("ignoring:", prefix + arg)
#@-node:ekr.20031218072017.3132:init_trace
#@+node:ekr.20031218072017.2317:g.trace
# Convert all args to strings.

def trace (*args,**keys):

    # Compute the effective args.
    d = {'align':0,'newline':True}
    d = g.doKeywordArgs(keys,d)
    newline = d.get('newline')
    align = d.get('align')
    if align is None: align = 0

    # Compute the caller name.
    try: # get the function name from the call stack.
        f1 = sys._getframe(1) # The stack frame, one level up.
        code1 = f1.f_code # The code object
        name = code1.co_name # The code name
    except Exception: name = ''
    if name == "?":
        name = "<unknown>"

    # Pad the caller name.
    if align != 0 and len(name) < abs(align):
        pad = ' ' * (abs(align) - len(name))
        if align > 0: name = name + pad
        else:         name = pad + name

    # Munge *args into s.
    # print ('g.trace:args...')
    # for z in args: print (g.isString(z),repr(z))
    result = []
    for arg in args:
        if g.isString(arg):
            pass
        elif g.isBytes(arg):
            arg = g.toUnicode(arg,'utf-8')
        else:
            arg = repr(arg)
        if result:
            result.append(" " + arg)
        else:
            result.append(arg)
    s = ''.join(result)
    try:
        g.pr('%s: %s' % (name,s),newline=newline)
    except Exception:
        s = g.toEncodedString(s,'ascii')
        g.pr('%s: %s' % (name,s),newline=newline)

#@-node:ekr.20031218072017.2317:g.trace
#@+node:ekr.20031218072017.2318:trace_tag
# Convert all args to strings.
# Print if tracing for name has been enabled.

def trace_tag (name, *args):

    s = ""
    for arg in args:
        if type(arg) != type(""):
            arg = repr(arg)
        if len(s) > 0:
            s = s + ", " + arg
        else:
            s = arg
    message = s

    t = app.trace_list
    # tracepoint names starting with '-' must match exactly.
    minus = len(name) > 0 and name[0] == '-'
    if minus: name = name[1:]
    if (not minus and '*' in t) or name.lower() in t:
        s = name + ": " + message
        g.es(s) # Traces _always_ get printed.
#@-node:ekr.20031218072017.2318:trace_tag
#@-node:ekr.20031218072017.3129:Sherlock... (trace)
#@+node:ekr.20031218072017.3133:Statistics
#@+node:ekr.20031218072017.3134:clear_stats
def clear_stats():

    g.trace()

    g.app.statsDict = {}

clearStats = clear_stats
#@-node:ekr.20031218072017.3134:clear_stats
#@+node:ekr.20031218072017.3135:print_stats
def print_stats (name=None):

    if name:
        if type(name) != type(""):
            name = repr(name)
    else:
        name = g._callerName(n=2) # Get caller name 2 levels back.

    g.printDict(g.app.statsDict,tag='statistics at %s' % name)

printStats = print_stats
#@-node:ekr.20031218072017.3135:print_stats
#@+node:ekr.20031218072017.3136:stat
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
#@-node:ekr.20031218072017.3136:stat
#@-node:ekr.20031218072017.3133:Statistics
#@+node:ekr.20031218072017.3137:Timing
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
#@-node:ekr.20031218072017.3137:Timing
#@+node:ekr.20080531075119.1:class Tracer & g.startTracer
class Tracer:

    '''A "debugger" that computes a call graph.

    To trace a function and its callers, put the following at the function's start:

    g.startTracer()
    '''

    #@	@+others
    #@+node:ekr.20080531075119.2: __init__
    def __init__(self):

        self.callDict = {}
            # Keys are function names.
            # Values are the number of times the function was called by the caller.
        self.calledDict = {}
            # Keys are function names.
            # Values are the total number of times the function was called.

        self.count = 0
        self.inited = False
        self.limit = 2 # 0: no limit, otherwise, limit trace to n entries deep.
        self.stack = []
        self.trace = False
        self.verbose = False # True: print returns as well as calls.
    #@-node:ekr.20080531075119.2: __init__
    #@+node:ekr.20080531075119.3:computeName
    def computeName (self,frame):

        import inspect

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
    #@-node:ekr.20080531075119.3:computeName
    #@+node:ekr.20080531075119.4:report
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
    #@-node:ekr.20080531075119.4:report
    #@+node:ekr.20080531075119.5:stop
    def stop (self):

        sys.settrace(None)
        self.report()
    #@-node:ekr.20080531075119.5:stop
    #@+node:ekr.20080531075119.6:tracer
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
    #@-node:ekr.20080531075119.6:tracer
    #@+node:ekr.20080531075119.7:updateStats
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
    #@-node:ekr.20080531075119.7:updateStats
    #@-others

def startTracer():

    import sys
    t = g.Tracer()
    sys.settrace(t.tracer)
    return t
#@-node:ekr.20080531075119.1:class Tracer & g.startTracer
#@-node:ekr.20031218072017.3104:Debugging, Dumping, Timing, Tracing & Sherlock
#@+node:ekr.20031218072017.3116:Files & Directories...
#@+node:ekr.20080606074139.2:g.chdir
def chdir (path):

    if not g.os_path_isdir(path):
        path = g.os_path_dirname(path)

    if g.os_path_isdir(path) and g.os_path_exists(path):
        os.chdir(path)
#@-node:ekr.20080606074139.2:g.chdir
#@+node:ekr.20031218072017.3117:g.create_temp_file & test
def create_temp_file (textMode=False):
    '''Return a tuple (theFile,theFileName)

    theFile: a file object open for writing.
    theFileName: the name of the temporary file.'''

    # mktemp is deprecated, but we can't get rid of it
    # because mkstemp does not exist in Python 2.2.1.
    try:
        # fd is an handle to an open file as would be returned by os.open()
        fd,theFileName = tempfile.mkstemp(text=textMode)
        mode = g.choose(textMode,'w','wb')
        theFile = os.fdopen(fd,mode)
        # g.trace(fd,theFile)
    except AttributeError:
        # g.trace("mkstemp doesn't exist")
        theFileName = tempfile.mktemp()
        try:
            mode = g.choose(textMode,'w','wb')
            theFile = open(theFileName,mode)
        except IOError:
            theFile,theFileName = None,''
    except Exception:
        g.es('unexpected exception in g.create_temp_file',color='red')
        g.es_exception()
        theFile,theFileName = None,''

    return theFile,theFileName
#@+node:ekr.20090517020744.5873:@test g.create_temp_file
if g.unitTesting:

    import types

    theFile,theFileName = g.create_temp_file()

    assert type(theFile) == types.FileType, 'not file type'
    assert type(theFileName) in (types.StringType, types.UnicodeType), 'not string type'
#@-node:ekr.20090517020744.5873:@test g.create_temp_file
#@-node:ekr.20031218072017.3117:g.create_temp_file & test
#@+node:ekr.20031218072017.3118:g.ensure_extension
def ensure_extension (name, ext):

    theFile, old_ext = g.os_path_splitext(name)
    if not name:
        return name # don't add to an empty name.
    elif old_ext and old_ext == ext:
        return name
    else:
        return name + ext
#@-node:ekr.20031218072017.3118:g.ensure_extension
#@+node:ekr.20031218072017.1264:g.getBaseDirectory (unchanged)
# Handles the conventions applying to the "relative_path_base_directory" configuration option.

def getBaseDirectory(c):

    base = app.config.relative_path_base_directory

    if base and base == "!":
        base = app.loadDir
    elif base and base == ".":
        base = c.openDirectory

    # g.trace(base)
    if base and len(base) > 0 and g.os_path_isabs(base):
        # Set c.chdir_to_relative_path as needed.
        if not hasattr(c,'chdir_to_relative_path'):
            c.chdir_to_relative_path = c.config.getBool('chdir_to_relative_path')
        # Call os.chdir if requested.
        if c.chdir_to_relative_path:
            os.chdir(base)
        return base # base need not exist yet.
    else:
        return "" # No relative base given.
#@-node:ekr.20031218072017.1264:g.getBaseDirectory (unchanged)
#@+node:tbrown.20090219095555.61:g.handleUrlInUrlNode
def handleUrlInUrlNode(url):

    # Note: the UNL plugin has its own notion of what a good url is.

    # c = self.c
    # g.trace(url)
    #@    << check the url; return if bad >>
    #@+node:tbrown.20090219095555.62:<< check the url; return if bad >>
    #@+at 
    #@nonl
    # A valid url is (according to D.T.Hein):
    # 
    # 3 or more lowercase alphas, followed by,
    # one ':', followed by,
    # one or more of: (excludes !"#;<>[\]^`|)
    #   $%&'()*+,-./0-9:=?@A-Z_a-z{}~
    # followed by one of: (same as above, except no minus sign or comma).
    #   $%&'()*+/0-9:=?@A-Z_a-z}~
    #@-at
    #@@c

    urlPattern = "[a-z]{3,}:[\$-:=?-Z_a-z{}~]+[\$-+\/-:=?-Z_a-z}~]"

    if not url or len(url) == 0:
        g.es("no url following @url")
        return

    # Add http:// if required.
    if not re.match('^([a-z]{3,}:)',url):
        url = 'http://' + url
    if not re.match(urlPattern,url):
        g.es("invalid url:",url)
        return
    #@nonl
    #@-node:tbrown.20090219095555.62:<< check the url; return if bad >>
    #@nl
    #@    << pass the url to the web browser >>
    #@+node:tbrown.20090219095555.63:<< pass the url to the web browser >>
    #@+at 
    #@nonl
    # Most browsers should handle the following urls:
    #   ftp://ftp.uu.net/public/whatever.
    #   http://localhost/MySiteUnderDevelopment/index.html
    #   file://home/me/todolist.html
    #@-at
    #@@c

    try:
        import os
        os.chdir(g.app.loadDir)
        if g.match(url,0,"file:") and url[-4:]==".leo":
            ok,frame = g.openWithFileName(url[5:],None)
        else:
            import webbrowser
            # Mozilla throws a weird exception, then opens the file!
            try: webbrowser.open(url)
            except: pass
    except:
        g.es("exception opening",url)
        g.es_exception()
    #@-node:tbrown.20090219095555.63:<< pass the url to the web browser >>
    #@nl
#@-node:tbrown.20090219095555.61:g.handleUrlInUrlNode
#@+node:EKR.20040504154039:g.is_sentinel
def is_sentinel (line,delims):

    #@    << is_sentinel doc tests >>
    #@+node:ekr.20040719161756:<< is_sentinel doc tests >>
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
    #@-node:ekr.20040719161756:<< is_sentinel doc tests >>
    #@nl

    delim1,delim2,delim3 = delims

    line = line.lstrip()

    if delim1:
        return line.startswith(delim1+'@')
    elif delim2 and delim3:
        i = line.find(delim2+'@')
        j = line.find(delim3)
        return 0 == i < j
    else:
        g.trace("can't happen. delims: %s" % repr(delims),color="red")
        return False
#@-node:EKR.20040504154039:g.is_sentinel
#@+node:ekr.20031218072017.3119:g.makeAllNonExistentDirectories
# This is a generalization of os.makedir.

def makeAllNonExistentDirectories (theDir,c=None,force=False,verbose=True):

    """Attempt to make all non-existent directories"""

    # g.trace('theDir',theDir,c.config.create_nonexistent_directories,g.callers())

    if not force:
        if c:
            if not c.config.create_nonexistent_directories:
                return None
        elif not app.config.create_nonexistent_directories:
            return None

    if c:
        theDir = g.os_path_expandExpression(theDir,c=c)

    dir1 = theDir = g.os_path_normpath(theDir)

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
    for s in paths:
        path = g.os_path_join(path,s)
        if not g.os_path_exists(path):
            try:
                os.mkdir(path)
                if verbose and not g.app.unitTesting:
                    # g.trace('***callers***',g.callers(5))
                    g.es_print("created directory:",path,color='red')
            except Exception:
                # g.trace(g.callers())
                if verbose: g.es_print("exception creating directory:",path,color='red')
                g.es_exception()
                return None
    return dir1 # All have been created.
#@-node:ekr.20031218072017.3119:g.makeAllNonExistentDirectories
#@+node:ekr.20071114113736:g.makePathRelativeTo
def makePathRelativeTo (fullPath,basePath):

    if fullPath.startswith(basePath):
        s = fullPath[len(basePath):]
        if s.startswith(os.path.sep):
            s = s[len(os.path.sep):]
        return s
    else:
        return fullPath
#@-node:ekr.20071114113736:g.makePathRelativeTo
#@+node:ekr.20070412082527:g.openLeoOrZipFile
# This is used in several places besides g.openWithFileName.

def openLeoOrZipFile (fileName):

    try:
        isZipped = zipfile.is_zipfile(fileName)
        if isZipped:
            theFile = zipfile.ZipFile(fileName,'r')
            # g.trace('opened zip file',theFile)
        else:
            # mode = g.choose(g.isPython3,'r','rb')
            # 9/19/08: always use binary mode??
            mode = 'rb'
            theFile = open(fileName,mode)
        return theFile,isZipped
    except IOError:
        # Do not use string + here: it will fail for non-ascii strings!
        if not g.unitTesting:
            g.es_print("can not open:",fileName,color="blue")
        return None,False
#@nonl
#@-node:ekr.20070412082527:g.openLeoOrZipFile
#@+node:ekr.20090520055433.5945:g.openWithFileName & helpers
def openWithFileName(fileName,old_c,
    enableLog=True,gui=None,readAtFileNodesFlag=True):

    """Create a Leo Frame for the indicated fileName if the file exists."""

    trace = False and not g.unitTesting

    if not fileName: return False, None
    isLeo,fn,relFn = g.mungeFileName(fileName)

    # Return if the file is already open.
    c = g.findOpenFile(fn)
    if c: return True,c.frame

    # Open the file.
    if isLeo:
        c,f = g.openWithFileNameHelper(old_c,gui,fn,relFn)
    else:
        c,f = g.openWrapperLeoFile(old_c,fn,gui),None
    if not c: return False,None

    # Init the open file.
    assert c.frame and c.frame.c == c
    c.frame.log.enable(enableLog)
    g.app.writeWaitingLog()
    ok = g.handleOpenHooks(c,old_c,gui,fn,f,readAtFileNodesFlag)
    if not ok: return False,None
    g.createMenu(c,fn,relFn)
    g.finishOpen(c)
    return True,c.frame
#@+node:ekr.20090520055433.5951:createMenu
def createMenu(c,fileName,relativeFileName,):

    # New in Leo 4.4.8: create the menu as late as possible so it can use user commands.

    if not g.doHook("menu1",c=c,p=c.p,v=c.p):
        c.frame.menu.createMenuBar(c.frame)
        c.updateRecentFiles(relativeFileName or fileName)
        g.doHook("menu2",c=c,p=c.p,v=c.p)
        g.doHook("after-create-leo-frame",c=c)
#@-node:ekr.20090520055433.5951:createMenu
#@+node:ekr.20090520055433.5948:findOpenFile
def findOpenFile(fileName):

    def munge(name):
        return g.os_path_normpath(name or '').lower()

    for frame in g.app.windowList:
        c = frame.c
        if munge(fileName) == munge(c.mFileName):
            frame.bringToFront()
            c.setLog()
            c.outerUpdate()
            return c
    return None
#@-node:ekr.20090520055433.5948:findOpenFile
#@+node:ekr.20090520055433.5952:finishOpen
def finishOpen(c):

    k = c.k
    # New in Leo 4.6: provide an official way for very late initialization.
    c.frame.tree.initAfterLoad()
    c.initAfterLoad()
    c.redraw()
    # chapterController.finishCreate must be called after the first real redraw
    # because it requires a valid value for c.rootPosition().
    if c.chapterController:
        c.chapterController.finishCreate()
    if k:
        k.setDefaultInputState()
    if c.config.getBool('outline_pane_has_initial_focus'):
        c.treeWantsFocusNow()
    else:
        c.bodyWantsFocusNow()
    if k:
        k.showStateAndMode()
    c.frame.initCompleteHint()
    return True
#@-node:ekr.20090520055433.5952:finishOpen
#@+node:ekr.20090520055433.5950:handleOpenHooks
def handleOpenHooks(c,old_c,gui,fileName,theFile,readAtFileNodesFlag):

    if not g.doHook("open1",old_c=old_c,c=c,new_c=c,fileName=fileName):
        c.setLog()
        if theFile:
            app.lockLog()
            ok = c.fileCommands.open(
                theFile,fileName,
                readAtFileNodesFlag=readAtFileNodesFlag) # closes file.
            app.unlockLog()
            if not ok:
                g.app.closeLeoWindow(c.frame)
                return False
            for z in g.app.windowList: # Bug fix: 2007/12/07: don't change frame var.
                # The recent files list has been updated by c.updateRecentFiles.
                z.c.config.setRecentFiles(g.app.config.recentFiles)

    # Bug fix in 4.4.
    c.frame.openDirectory = c.os_path_finalize(g.os_path_dirname(fileName))
    g.doHook("open2",old_c=old_c,c=c,new_c=c,fileName=fileName)
    return True
#@nonl
#@-node:ekr.20090520055433.5950:handleOpenHooks
#@+node:ekr.20090520055433.5954:mungeFileName
def mungeFileName(fileName):

    '''Create a full, normalized, Unicode path name, preserving case.'''

    relFn = g.os_path_normpath(fileName)
    fn = g.os_path_finalize(fileName)

    isZipped = fn and zipfile.is_zipfile(fn)
    isLeo = isZipped or fn.endswith('.leo')

    return isLeo,fn,relFn
#@-node:ekr.20090520055433.5954:mungeFileName
#@+node:ekr.20090520055433.5946:openWithFileNameHelper
def openWithFileNameHelper(old_c,gui,fileName,relativeFileName):

    if old_c: g.preRead(old_c)
    g.doHook('open0')

    # Open the file in binary mode to allow 0x1a in bodies & headlines.
    theFile,isZipped = g.openLeoOrZipFile(fileName)
    if not theFile:
        return None,None

    # This call will take 3/4 sec. to open a file from the leoBridge.
    # This is due to imports in c.__init__
    c,frame = app.newLeoCommanderAndFrame(
        fileName=fileName,
        relativeFileName=relativeFileName,
        gui=gui)

    c.isZipped = isZipped
    return c,theFile
#@+node:ekr.20090520055433.5949:preRead
def preRead(fileName):

    '''Read the file for the first time,
    setting the setting for a later call to finishCreate.
    '''

    c = g.app.config.openSettingsFile(fileName)
    if c:
        g.app.config.updateSettings(c,localFlag=True)
#@-node:ekr.20090520055433.5949:preRead
#@-node:ekr.20090520055433.5946:openWithFileNameHelper
#@+node:ekr.20080921154026.1:openWrapperLeoFile
def openWrapperLeoFile (old_c,fileName,gui):

    '''Open a wrapper .leo file for the given file,
    and import the file into .leo file.'''

    # This code is similar to c.new, but different enough to be separate.
    if not g.os_path_exists(fileName):
        if not g.unitTesting:
            g.es_print("can not open:",fileName,color="blue")
        return None

    c,frame = g.app.newLeoCommanderAndFrame(
        fileName=None,relativeFileName=None,gui=gui)

    # Needed for plugins.
    g.doHook("new",old_c=old_c,c=c,new_c=c)

    # Use the config params to set the size and location of the window.
    frame.setInitialWindowGeometry()
    frame.deiconify()
    frame.lift()
    frame.resizePanesToRatio(frame.ratio,frame.secondary_ratio) # Resize the _new_ frame.

    if True: # Just read the file into the node.
        try:
            fileName = g.os_path_finalize(fileName)
            f = open(fileName)
            s = f.read()
            f.close()
        except IOError:
            g.es_print("can not open: ",fileName,color='red')
            return None
        p = c.rootPosition()
        if p:
            p.setHeadString('@edit %s' % fileName)
            p.setBodyString(s)
    else:  # Import the file into the new outline.
        junk,ext = g.os_path_splitext(fileName)
        p = c.p
        p = c.importCommands.createOutline(fileName,parent=p,atAuto=False,ext=ext)
        c.setCurrentPosition(p)
        c.moveOutlineLeft()
        p = c.p
        c.setCurrentPosition(p.back())
        c.deleteOutline(op_name=None)
        p = c.p
        p.expand()

    # chapterController.finishCreate must be called after the first real redraw
    # because it requires a valid value for c.rootPosition().
    if c.config.getBool('use_chapters') and c.chapterController:
        c.chapterController.finishCreate()

    frame.c.setChanged(True) # Unlike new, we the outline should be marked changed.

    if c.config.getBool('outline_pane_has_initial_focus'):
        c.treeWantsFocusNow()
    else:
        c.bodyWantsFocusNow()

    # c.redraw() # Only needed by menu commands.
    return c
#@-node:ekr.20080921154026.1:openWrapperLeoFile
#@-node:ekr.20090520055433.5945:g.openWithFileName & helpers
#@+node:ekr.20080921154026.1:openWrapperLeoFile
def openWrapperLeoFile (old_c,fileName,gui):

    '''Open a wrapper .leo file for the given file,
    and import the file into .leo file.'''

    # This code is similar to c.new, but different enough to be separate.
    if not g.os_path_exists(fileName):
        if not g.unitTesting:
            g.es_print("can not open:",fileName,color="blue")
        return None

    c,frame = g.app.newLeoCommanderAndFrame(
        fileName=None,relativeFileName=None,gui=gui)

    # Needed for plugins.
    g.doHook("new",old_c=old_c,c=c,new_c=c)

    # Use the config params to set the size and location of the window.
    frame.setInitialWindowGeometry()
    frame.deiconify()
    frame.lift()
    frame.resizePanesToRatio(frame.ratio,frame.secondary_ratio) # Resize the _new_ frame.

    if True: # Just read the file into the node.
        try:
            fileName = g.os_path_finalize(fileName)
            f = open(fileName)
            s = f.read()
            f.close()
        except IOError:
            g.es_print("can not open: ",fileName,color='red')
            return None
        p = c.rootPosition()
        if p:
            p.setHeadString('@edit %s' % fileName)
            p.setBodyString(s)
    else:  # Import the file into the new outline.
        junk,ext = g.os_path_splitext(fileName)
        p = c.p
        p = c.importCommands.createOutline(fileName,parent=p,atAuto=False,ext=ext)
        c.setCurrentPosition(p)
        c.moveOutlineLeft()
        p = c.p
        c.setCurrentPosition(p.back())
        c.deleteOutline(op_name=None)
        p = c.p
        p.expand()

    # chapterController.finishCreate must be called after the first real redraw
    # because it requires a valid value for c.rootPosition().
    if c.config.getBool('use_chapters') and c.chapterController:
        c.chapterController.finishCreate()

    frame.c.setChanged(True) # Unlike new, we the outline should be marked changed.

    if c.config.getBool('outline_pane_has_initial_focus'):
        c.treeWantsFocusNow()
    else:
        c.bodyWantsFocusNow()

    # c.redraw() # Only needed by menu commands.
    return c
#@-node:ekr.20080921154026.1:openWrapperLeoFile
#@+node:ekr.20031218072017.3120:g.readlineForceUnixNewline (Steven P. Schaefer)
#@+at 
#@nonl
# Stephen P. Schaefer 9/7/2002
# 
# The Unix readline() routine delivers "\r\n" line end strings verbatim, while 
# the windows versions force the string to use the Unix convention of using 
# only "\n".  This routine causes the Unix readline to do the same.
#@-at
#@@c

def readlineForceUnixNewline(f):

    s = f.readline()
    if len(s) >= 2 and s[-2] == "\r" and s[-1] == "\n":
        s = s[0:-2] + "\n"
    return s
#@-node:ekr.20031218072017.3120:g.readlineForceUnixNewline (Steven P. Schaefer)
#@+node:ekr.20031218072017.3124:g.sanitize_filename
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
#@-node:ekr.20031218072017.3124:g.sanitize_filename
#@+node:ekr.20060328150113:g.setGlobalOpenDir
def setGlobalOpenDir (fileName):

    if fileName:
        g.app.globalOpenDir = g.os_path_dirname(fileName)
        # g.es('current directory:',g.app.globalOpenDir)
#@-node:ekr.20060328150113:g.setGlobalOpenDir
#@+node:ekr.20031218072017.3125:g.shortFileName & shortFilename
def shortFileName (fileName):

    return g.os_path_basename(fileName)

shortFilename = shortFileName
#@-node:ekr.20031218072017.3125:g.shortFileName & shortFilename
#@+node:ekr.20050104135720:Used by tangle code & leoFileCommands
#@+node:ekr.20031218072017.1241:g.update_file_if_changed
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
        ok = g.utils_rename(c,temp_name,file_name)

    if ok:
        g.es('','%12s: %s' % (kind,file_name))
    else:
        g.es("rename failed: no file created!",color="red")
        g.es('',file_name," may be read-only or in use")
#@-node:ekr.20031218072017.1241:g.update_file_if_changed
#@+node:ekr.20050104123726.3:g.utils_remove & test
def utils_remove (fileName,verbose=True):

    try:
        os.remove(fileName)
        return True
    except Exception:
        if verbose:
            g.es("exception removing:",fileName)
            g.es_exception()
        return False
#@+node:ekr.20090517020744.5886:@test g.utils_remove
if g.unitTesting:

    import os

    exists = g.os_path_exists

    path = g.os_path_join(g.app.testDir,'xyzzy')
    if exists(path):
        os.remove(path)

    assert not exists(path)
    assert not g.utils_remove(path,verbose=False)

    f = file(path,'w')
    f.write('test')
    f.close()

    assert exists(path)
    assert g.utils_remove(path,verbose=True)
    assert not exists(path)
#@-node:ekr.20090517020744.5886:@test g.utils_remove
#@-node:ekr.20050104123726.3:g.utils_remove & test
#@+node:ekr.20031218072017.1263:g.utils_rename & test
#@<< about os.rename >>
#@+node:ekr.20050104123726.1:<< about os.rename >>
#@+at 
#@nonl
# Here is the Python 2.4 documentation for rename (same as Python 2.3)
# 
# Rename the file or directory src to dst.  If dst is a directory, OSError 
# will be raised.
# 
# On Unix, if dst exists and is a file, it will be removed silently if the 
# user
# has permission. The operation may fail on some Unix flavors if src and dst 
# are
# on different filesystems. If successful, the renaming will be an atomic
# operation (this is a POSIX requirement).
# 
# On Windows, if dst already exists, OSError will be raised even if it is a 
# file;
# there may be no way to implement an atomic rename when dst names an existing
# file.
#@-at
#@-node:ekr.20050104123726.1:<< about os.rename >>
#@nl

def utils_rename (c,src,dst,mode=None,verbose=True):

    '''Platform independent rename.'''

    head, tail = g.os_path_split(dst)
    if head and len(head) > 0:
        g.makeAllNonExistentDirectories(head,c=c)

    if g.os_path_exists(dst):
        if not g.utils_remove(dst):
            return False
    try:
        # New in Leo 4.4b1: try using shutil first.
        try:
            import shutil # shutil is new in Python 2.3
            shutil.move(src,dst)
        except ImportError:
            if sys.platform == "win32":
                os.rename(src,dst)
            else:
                try:
                    # Alas, distutils.file_util may not exist.
                    from distutils.file_util import move_file
                    move_file(src,dst)
                except ImportError:
                    # Desperation: may give: 'Invalid cross-device link'
                    os.rename(src,dst)
        if mode:
            g.utils_chmod(dst,mode,verbose)
        return True
    except Exception:
        if verbose:
            g.es('exception renaming',src,'to',dst,color='red')
            g.es_exception(full=False)
        return False
#@+node:ekr.20090517020744.5887:@test g.utils_rename
if g.unitTesting:

    import os

    exists = g.os_path_exists
    path = g.os_path_join(g.app.testDir,'xyzzy')
    path2 = g.os_path_join(g.app.testDir,'xyzzy2')

    # Create both paths.
    for p in (path,path2):
        if exists(p):
            os.remove(p)
        assert not exists(p)
        f = file(p,'w')
        f.write('test %s' % p)
        f.close()
        assert exists(p)

    assert g.utils_rename(c,path,path2,verbose=True)
    assert exists(path2)
    f = file(path2)
    s = f.read()
    f.close()
    # print('Contents of %s: %s' % (path2,s))
    assert s == 'test %s' % path
    os.remove(path2)
    assert not exists(path)
#@-node:ekr.20090517020744.5887:@test g.utils_rename
#@-node:ekr.20031218072017.1263:g.utils_rename & test
#@+node:ekr.20050104124903:g.utils_chmod
def utils_chmod (fileName,mode,verbose=True):

    if mode is None:
        return

    try:
        os.chmod(fileName,mode)
    except Exception:
        if verbose:
            g.es("exception in os.chmod",fileName)
            g.es_exception()
#@-node:ekr.20050104124903:g.utils_chmod
#@+node:ekr.20050104123726.4:g.utils_stat
def utils_stat (fileName):

    '''Return the access mode of named file, removing any setuid, setgid, and sticky bits.'''

    try:
        mode = (os.stat(fileName))[0] & (7*8*8 + 7*8 + 7) # 0777
    except Exception:
        mode = None

    return mode
#@-node:ekr.20050104123726.4:g.utils_stat
#@-node:ekr.20050104135720:Used by tangle code & leoFileCommands
#@-node:ekr.20031218072017.3116:Files & Directories...
#@+node:ekr.20031218072017.1588:Garbage Collection
lastObjectCount = 0
lastObjectsDict = {}
lastTypesDict = {}
lastFunctionsDict = {}

#@+others
#@+node:ekr.20031218072017.1589:clearAllIvars
def clearAllIvars (o):

    """Clear all ivars of o, a member of some class."""

    if o:
        o.__dict__.clear()
#@-node:ekr.20031218072017.1589:clearAllIvars
#@+node:ekr.20031218072017.1590:collectGarbage
def collectGarbage():

    try:
        if not g.app.trace_gc_inited:
            g.enable_gc_debug()

        if g.app.trace_gc_verbose or g.app.trace_gc_calls:
            g.pr('collectGarbage:')

        gc.collect()
    except Exception:
        pass

    # Only init once, regardless of what happens.
    g.app.trace_gc_inited = True
#@-node:ekr.20031218072017.1590:collectGarbage
#@+node:ekr.20060127162818:enable_gc_debug
no_gc_message = False

def enable_gc_debug(event=None):

    if gc:
        if g.app.trace_gc_verbose:
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
        g.es('can not import gc module',color='blue')
#@-node:ekr.20060127162818:enable_gc_debug
#@+node:ekr.20031218072017.1592:printGc
# Formerly called from unit tests.

def printGc(tag=None):

    if not g.app.trace_gc: return None

    tag = tag or g._callerName(n=2)

    printGcObjects(tag=tag)
    printGcRefs(tag=tag)

    if g.app.trace_gc_verbose:
        printGcVerbose(tag=tag)
#@+node:ekr.20031218072017.1593:printGcRefs
def printGcRefs (tag=''):

    refs = gc.get_referrers(app.windowList[0])
    g.pr('-' * 30,tag)

    if g.app.trace_gc_verbose:
        g.pr("refs of", app.windowList[0])
        for ref in refs:
            g.pr(type(ref))
    else:
        g.pr("%d referers" % len(refs))
#@-node:ekr.20031218072017.1593:printGcRefs
#@-node:ekr.20031218072017.1592:printGc
#@+node:ekr.20060202161935:printGcAll
def printGcAll (tag=''):

    # Suppress warning about keywords arg not supported in sort.

    tag = tag or g._callerName(n=2)
    d = {} ; objects = gc.get_objects()
    g.pr('-' * 30)
    g.pr('%s: %d objects' % (tag,len(objects)))

    for obj in objects:
        t = type(obj)
        if t == 'instance':
            try: t = obj.__class__
            except Exception: pass
        # if type(obj) == type(()):
            # g.pr(id(obj),repr(obj))
        d[t] = d.get(t,0) + 1

    if 1: # Sort by n
        items = d.items()
        try:
            # Support for keword args to sort function exists in Python 2.4.
            # Support for None as an alternative to omitting cmp exists in Python 2.3.
            items.sort(key=lambda x: x[1],reverse=True)
        except Exception: pass
        for z in items:
            g.pr('%40s %7d' % (z[0],z[1]))
    else: # Sort by type
        for t in sorted(d):
            g.pr('%40s %7d' % (t,d.get(t)))
#@-node:ekr.20060202161935:printGcAll
#@+node:ekr.20060127164729.1:printGcObjects   (printNewObjects=pno)
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

        #@        << print number of each type of object >>
        #@+node:ekr.20040703054646:<< print number of each type of object >>
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
        #@-node:ekr.20040703054646:<< print number of each type of object >>
        #@nl
        if 0:
            #@            << print added functions >>
            #@+node:ekr.20040703065638:<< print added functions >>
            # import types
            import inspect

            global lastFunctionsDict

            funcDict = {}

            # Don't print more than 50 objects.
            n = 0
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
            #@-node:ekr.20040703065638:<< print added functions >>
            #@nl

    except Exception:
        traceback.print_exc()

printNewObjects = pno = printGcObjects

#@-node:ekr.20060127164729.1:printGcObjects   (printNewObjects=pno)
#@+node:ekr.20060205043324.1:printGcSummary
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
#@-node:ekr.20060205043324.1:printGcSummary
#@+node:ekr.20060127165509:printGcVerbose
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
#@-node:ekr.20060127165509:printGcVerbose
#@-others
#@-node:ekr.20031218072017.1588:Garbage Collection
#@+node:ekr.20031218072017.3139:Hooks & plugins (leoGlobals)
#@+node:ekr.20031218072017.1315:idle time functions (leoGlobals)
#@+node:EKR.20040602125018:enableIdleTimeHook
#@+at 
#@nonl
# Enables the "idle" hook.
# After enableIdleTimeHook is called, Leo will call the "idle" hook
# approximately every g.idleTimeDelay milliseconds.
#@-at
#@@c

def enableIdleTimeHook(idleTimeDelay=100):

    if not g.app.idleTimeHook:
        # g.trace('start idle-time hook: %d msec.' % idleTimeDelay)
        # Start idle-time processing only after the first idle-time event.
        g.app.gui.setIdleTimeHook(g.idleTimeHookHandler)
        g.app.afterHandler = g.idleTimeHookHandler

    # 1/4/05: Always update these.
    g.app.idleTimeHook = True
    g.app.idleTimeDelay = idleTimeDelay # Delay in msec.
#@-node:EKR.20040602125018:enableIdleTimeHook
#@+node:EKR.20040602125018.1:disableIdleTimeHook
# Disables the "idle" hook.
def disableIdleTimeHook():

    g.app.idleTimeHook = False
#@-node:EKR.20040602125018.1:disableIdleTimeHook
#@+node:EKR.20040602125018.2:idleTimeHookHandler
# An internal routine used to dispatch the "idle" hook.
trace_count = 0

def idleTimeHookHandler(*args,**keys):

    if 0: # Do not use g.trace here!
        global trace_count ; trace_count += 1
        if 1:
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
#@nonl
#@-node:EKR.20040602125018.2:idleTimeHookHandler
#@-node:ekr.20031218072017.1315:idle time functions (leoGlobals)
#@+node:ekr.20031218072017.1596:g.doHook
#@+at 
#@nonl
# This global function calls a hook routine.  Hooks are identified by the tag 
# param.
# Returns the value returned by the hook routine, or None if the there is an 
# exception.
# 
# We look for a hook routine in three places:
# 1. c.hookFunction
# 2. app.hookFunction
# 3. leoPlugins.doPlugins()
# We set app.hookError on all exceptions.  Scripts may reset app.hookError to 
# try again.
#@-at
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
            s = "Plugins disabled: use_plugins is 0 in a leoSettings.leo file."
            g.es_print(s,color="blue")
        return None

    # Get the hook handler function.  Usually this is doPlugins.
    c = keywords.get("c")
    f = (c and c.hookFunction) or g.app.hookFunction

    if trace and (verbose or tag != 'idle'):
        g.trace('tag',tag,'f',f and f.__name__)

    if not f:
        import leo.core.leoPlugins as leoPlugins
        g.app.hookFunction = f = leoPlugins.doPlugins

    try:
        # Pass the hook to the hook handler.
        # g.pr('doHook',f.__name__,keywords.get('c'))
        return f(tag,keywords)
    except Exception:
        g.es_exception()
        g.app.hookError = True # Supress this function.
        g.app.idleTimeHook = False # Supress idle-time hook
        return None # No return value
#@-node:ekr.20031218072017.1596:g.doHook
#@+node:ekr.20031218072017.1318:g.plugin_signon
def plugin_signon(module_name,verbose=False):

    # To keep pylint happy.
    m = g.Bunch()
    m.__name__=''
    m.__version__=''

    exec("import %s ; m = %s" % (module_name,module_name))

    # g.pr('plugin_signon',module_name # ,'gui',g.app.gui)

    if verbose:
        g.es('',"...%s.py v%s: %s" % (
            m.__name__, m.__version__, g.plugin_date(m)))

        g.pr(m.__name__, m.__version__)

    app.loadedPlugins.append(module_name)
#@-node:ekr.20031218072017.1318:g.plugin_signon
#@-node:ekr.20031218072017.3139:Hooks & plugins (leoGlobals)
#@+node:ekr.20031218072017.3145:Most common functions...
# These are guaranteed always to exist for scripts.
#@+node:ekr.20031218072017.3147:g.choose
def choose(cond, a, b): # warning: evaluates all arguments

    if cond: return a
    else: return b
#@-node:ekr.20031218072017.3147:g.choose
#@+node:ekr.20080821073134.2:g.doKeywordArgs
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
#@-node:ekr.20080821073134.2:g.doKeywordArgs
#@+node:ekr.20031218072017.1474:g.enl, ecnl & ecnls
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
#@-node:ekr.20031218072017.1474:g.enl, ecnl & ecnls
#@+node:ekr.20070626132332:g.es & minitest
def es(*args,**keys):

    '''Put all non-keyword args to the log pane.
    The first, third, fifth, etc. arg translated by g.translateString.
    Supports color, comma, newline, spaces and tabName keyword arguments.
    '''

    log = app.log
    if app.killed: return

    # Compute the effective args.
    d = {'color':'black','commas':False,'newline':True,'spaces':True,'tabName':'Log'}
    d = g.doKeywordArgs(keys,d)
    color = d.get('color')
    if color == 'suppress': return # New in 4.3.
    tabName = d.get('tabName') or 'Log'
    newline = d.get('newline')
    s = g.translateArgs(args,d)

    if app.batchMode:
        if app.log:
            app.log.put(s)
    elif g.unitTesting:
        if log and not log.isNull:
            # New in Leo 4.5 b4: this is no longer needed.
            # This makes the output of unit tests match the output of scripts.
            # s = g.toEncodedString(s,'ascii')
            g.pr(s,newline=newline)
    else:
        if log and log.isNull:
            pass
        elif log:
            log.put(s,color=color,tabName=tabName)
            for ch in s:
                if ch == '\n': log.newlines += 1
                else: log.newlines = 0
            if newline:
                g.ecnl(tabName=tabName) # only valid here
        elif newline:
            app.logWaiting.append((s+'\n',color),)
        else:
            app.logWaiting.append((s,color),)
#@+node:ekr.20071024101611:mini test of es
#@@nocolor
#@@first
#@@first
#@+at
# 
# This doesn't work as an external unit test.
# To test, select all following lines and do execute-script.
# 
# s1 = 'line1 Ä, ڱ,  궯, 奠 end'
# s2 = g.toUnicode(s1,'utf-8')
# 
# for s in (s1,s2):
#     g.es(s)
#     g.es_print(s)
#@-at
#@-node:ekr.20071024101611:mini test of es
#@-node:ekr.20070626132332:g.es & minitest
#@+node:ekr.20050707064040:g.es_print
# see: http://www.diveintopython.org/xml_processing/unicode.html

def es_print(*args,**keys):

    '''Print all non-keyword args, and put them to the log pane.
    The first, third, fifth, etc. arg translated by g.translateString.
    Supports color, comma, newline, spaces and tabName keyword arguments.
    '''

    g.pr(*args,**keys)

    if not g.app.unitTesting:
        g.es(*args,**keys)
#@-node:ekr.20050707064040:g.es_print
#@+node:ekr.20050707065530:g.es_trace & test
def es_trace(*args,**keys):

    if args:
        try:
            s = args[0]
            g.trace(g.toEncodedString(s,'ascii'))
        except Exception:
            pass

    g.es(*args,**keys)
#@+node:ekr.20090517020744.5875:@test g.es_trace
#@@first

if g.unitTesting:

    if 0: # Not usually enabled.
        g.es_trace('\ntest of es_trace: Ă',color='red')
#@-node:ekr.20090517020744.5875:@test g.es_trace
#@-node:ekr.20050707065530:g.es_trace & test
#@+node:ekr.20090128083459.82:g.posList
class posList(list):
    #@    << docstring for posList >>
    #@+node:ekr.20090130114732.2:<< docstring for posList >>
    '''A subclass of list for creating and selecting lists of positions.

        aList = g.posList(c)
            # Creates a posList containing all positions in c.

        aList = g.posList(c,aList2)
            # Creates a posList from aList2.

        aList2 = aList.select(pattern,regex=False,removeClones=True)
            # Creates a posList containing all positions p in aList
            # such that p.h matches the pattern.
            # The pattern is a regular expression if regex is True.
            # if removeClones is True, all positions p2 are removed
            # if a position p is already in the list and p2.v.t == p.v.t.

        aList.dump(sort=False,verbose=False)
            # Prints all positions in aList, sorted if sort is True.
            # Prints p.h, or repr(p) if verbose is True.
    '''
    #@-node:ekr.20090130114732.2:<< docstring for posList >>
    #@nl
    def __init__ (self,c,aList=None):
        self.c = c
        list.__init__(self) # Init the base class
        if aList is None:
            for p in c.allNodes_iter():
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
            if p.v.t not in seen:
                seen[p.v.t] = p.v.t
                aList2.append(p)
        return aList2
#@-node:ekr.20090128083459.82:g.posList
#@+node:ekr.20080710101653.1:g.pr
# see: http://www.diveintopython.org/xml_processing/unicode.html

def pr(*args,**keys):

    '''Print all non-keyword args, and put them to the log pane.
    The first, third, fifth, etc. arg translated by g.translateString.
    Supports color, comma, newline, spaces and tabName keyword arguments.
    '''

    # Compute the effective args.
    d = {'commas':False,'newline':True,'spaces':True}
    d = g.doKeywordArgs(keys,d)

    # Important:  Python's print statement *can* handle unicode.
    # However, the following must appear in Python\Lib\sitecustomize.py:
    #    sys.setdefaultencoding('utf-8')
    s = g.translateArgs(args,d) # Translates everything to unicode.

    try: # We can't use any print keyword args in Python 2.x!
        # print(s) # Not quite right.
        if d.get('newline'):
            sys.stdout.write(s+'\n')
        else:
            sys.stdout.write(s)
    except Exception:
        print('unexpected Exception in g.pr')
        g.es_exception()
        g.trace(g.callers())
#@-node:ekr.20080710101653.1:g.pr
#@+node:ekr.20080220111323:g.translateArgs
def translateArgs(args,d):

    '''Return the concatenation of s and all args,

    with odd args translated.'''

    if not hasattr(g,'consoleEncoding'):
        e = sys.getdefaultencoding()
        g.consoleEncoding = isValidEncoding(e) and e or 'utf-8'
        # print 'translateArgs',g.consoleEncoding


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
#@-node:ekr.20080220111323:g.translateArgs
#@+node:ekr.20060810095921:g.translateString & tr
def translateString (s):

    '''Return the translated text of s.'''

    if g.isPython3:
        if not g.isString(s):
            s = str(s,'utf-8')
        if g.app.translateToUpperCase:
            s = s.upper()
        else:
            s = gettext.gettext(s)
        return s
    else:
        if g.app.translateToUpperCase:
            return s.upper()
        else:
            return gettext.gettext(s)

tr = translateString
#@-node:ekr.20060810095921:g.translateString & tr
#@+node:ekr.20031218072017.3150:g.windows
def windows():
    return app.windowList
#@-node:ekr.20031218072017.3150:g.windows
#@-node:ekr.20031218072017.3145:Most common functions...
#@+node:ekr.20031218072017.2145:os.path wrappers (leoGlobals.py)
#@+at 
#@nonl
# Note: all these methods return Unicode strings. It is up to the user to
# convert to an encoded string as needed, say when opening a file.
#@-at
#@+node:ekr.20031218072017.2146:os_path_abspath
def os_path_abspath(path,encoding=None):

    """Convert a path to an absolute path."""

    path = g.toUnicodeFileEncoding(path,encoding)

    path = os.path.abspath(path)

    path = g.toUnicodeFileEncoding(path,encoding)

    return path
#@-node:ekr.20031218072017.2146:os_path_abspath
#@+node:ekr.20031218072017.2147:os_path_basename
def os_path_basename(path,encoding=None):

    """Return the second half of the pair returned by split(path)."""

    path = g.toUnicodeFileEncoding(path,encoding)

    path = os.path.basename(path)

    path = g.toUnicodeFileEncoding(path,encoding)

    return path
#@-node:ekr.20031218072017.2147:os_path_basename
#@+node:ekr.20031218072017.2148:os_path_dirname
def os_path_dirname(path,encoding=None):

    """Return the first half of the pair returned by split(path)."""

    path = g.toUnicodeFileEncoding(path,encoding)

    path = os.path.dirname(path)

    path = g.toUnicodeFileEncoding(path,encoding)

    return path
#@-node:ekr.20031218072017.2148:os_path_dirname
#@+node:ekr.20031218072017.2149:os_path_exists
def os_path_exists(path,encoding=None):

    """Normalize the path and convert it to an absolute path."""

    path = g.toUnicodeFileEncoding(path,encoding)

    return os.path.exists(path)
#@-node:ekr.20031218072017.2149:os_path_exists
#@+node:ekr.20080922124033.6:os_path_expandExpression
def os_path_expandExpression (s,**keys):

    '''Expand {{anExpression}} in c's context.'''

    c = keys.get('c')
    if not c:
        g.trace('can not happen: no c',g.callers())
        return s

    if not s: return ''

    i = s.find('{{')
    j = s.find('}}')
    if -1 < i < j:
        exp = s[i+2:j].strip()
        if exp:
            try:
                import os
                import sys
                p = c.p
                d = {'c':c,'g':g,'p':p,'os':os,'sys':sys,}
                val = eval(exp,d)
                s = s[:i] + str(val) + s[j+2:]
            except Exception:
                g.trace(g.callers())
                g.es_exception(full=True, c=c, color='red')

    return s
#@-node:ekr.20080922124033.6:os_path_expandExpression
#@+node:ekr.20080921060401.13:os_path_expanduser
def os_path_expanduser(path,encoding=None):

    """wrap os.path.expanduser"""

    path = g.toUnicodeFileEncoding(path,encoding)

    result = os.path.normpath(os.path.expanduser(path))

    # g.trace('path',path,'expanduser', result)

    return result
#@-node:ekr.20080921060401.13:os_path_expanduser
#@+node:ekr.20080921060401.14:g.os_path_finalize & os_path_finalize_join
def os_path_finalize (path,**keys):

    '''
    Expand '~', then return os.path.normpath, os.path.abspath of the path.

    There is no corresponding os.path method'''

    c,encoding = keys.get('c'),keys.get('encoding')

    if c: path = g.os_path_expandExpression(path,**keys)

    path = g.os_path_expanduser(path,encoding=encoding)
    return os.path.normpath(os.path.abspath(path))

def os_path_finalize_join (*args,**keys):

    '''Do os.path.join(*args), then finalize the result.'''

    c,encoding = keys.get('c'),keys.get('encoding')

    if c: args = [g.os_path_expandExpression(path,**keys)
        for path in args if path]

    return os.path.normpath(os.path.abspath(
        g.os_path_join(*args,**keys))) # Handles expanduser
#@-node:ekr.20080921060401.14:g.os_path_finalize & os_path_finalize_join
#@+node:ekr.20031218072017.2150:os_path_getmtime
def os_path_getmtime(path,encoding=None):

    """Normalize the path and convert it to an absolute path."""

    path = g.toUnicodeFileEncoding(path,encoding)

    return os.path.getmtime(path)
#@-node:ekr.20031218072017.2150:os_path_getmtime
#@+node:ekr.20080729142651.2:os_path_getsize
def os_path_getsize (path,encoding=None):

    path = g.toUnicodeFileEncoding(path,encoding)

    return os.path.getsize(path)
#@-node:ekr.20080729142651.2:os_path_getsize
#@+node:ekr.20031218072017.2151:os_path_isabs
def os_path_isabs(path,encoding=None):

    """Normalize the path and convert it to an absolute path."""

    path = g.toUnicodeFileEncoding(path,encoding)

    return os.path.isabs(path)
#@-node:ekr.20031218072017.2151:os_path_isabs
#@+node:ekr.20031218072017.2152:os_path_isdir
def os_path_isdir(path,encoding=None):

    """Normalize the path and convert it to an absolute path."""

    path = g.toUnicodeFileEncoding(path,encoding)

    return os.path.isdir(path)
#@-node:ekr.20031218072017.2152:os_path_isdir
#@+node:ekr.20031218072017.2153:os_path_isfile
def os_path_isfile(path,encoding=None):

    """Normalize the path and convert it to an absolute path."""

    path = g.toUnicodeFileEncoding(path,encoding)

    return os.path.isfile(path)
#@-node:ekr.20031218072017.2153:os_path_isfile
#@+node:ekr.20031218072017.2154:os_path_join
def os_path_join(*args,**keys):

    c = keys.get('c')
    encoding = keys.get('encoding')

    uargs = [g.toUnicodeFileEncoding(arg,encoding) for arg in args]

    # Note:  This is exactly the same convention as used by getBaseDirectory.
    if uargs and uargs[0] == '!!':
        uargs[0] = g.app.loadDir
    elif uargs and uargs[0] == '.':
        c = keys.get('c')
        if c and c.openDirectory:
            uargs[0] = c.openDirectory
            # g.trace(c.openDirectory)

    uargs = [g.os_path_expanduser(z,encoding=encoding) for z in uargs if z]

    path = os.path.join(*uargs)

    # May not be needed on some Pythons.
    path = g.toUnicodeFileEncoding(path,encoding)
    return path
#@-node:ekr.20031218072017.2154:os_path_join
#@+node:ekr.20031218072017.2156:os_path_normcase
def os_path_normcase(path,encoding=None):

    """Normalize the path's case."""

    path = g.toUnicodeFileEncoding(path,encoding)

    path = os.path.normcase(path)

    path = g.toUnicodeFileEncoding(path,encoding)

    return path
#@-node:ekr.20031218072017.2156:os_path_normcase
#@+node:ekr.20031218072017.2157:os_path_normpath
def os_path_normpath(path,encoding=None):

    """Normalize the path."""

    path = g.toUnicodeFileEncoding(path,encoding)

    path = os.path.normpath(path)

    path = g.toUnicodeFileEncoding(path,encoding)

    return path
#@-node:ekr.20031218072017.2157:os_path_normpath
#@+node:ekr.20080605064555.2:os_path_realpath
def os_path_realpath(path,encoding=None):


    path = g.toUnicodeFileEncoding(path,encoding)

    path = os.path.realpath(path)

    path = g.toUnicodeFileEncoding(path,encoding)

    return path
#@-node:ekr.20080605064555.2:os_path_realpath
#@+node:ekr.20031218072017.2158:os_path_split
def os_path_split(path,encoding=None):

    path = g.toUnicodeFileEncoding(path,encoding)

    head,tail = os.path.split(path)

    head = g.toUnicodeFileEncoding(head,encoding)
    tail = g.toUnicodeFileEncoding(tail,encoding)

    return head,tail
#@-node:ekr.20031218072017.2158:os_path_split
#@+node:ekr.20031218072017.2159:os_path_splitext
def os_path_splitext(path,encoding=None):

    path = g.toUnicodeFileEncoding(path,encoding)

    head,tail = os.path.splitext(path)

    head = g.toUnicodeFileEncoding(head,encoding)
    tail = g.toUnicodeFileEncoding(tail,encoding)

    return head,tail
#@-node:ekr.20031218072017.2159:os_path_splitext
#@+node:ekr.20031218072017.2160:toUnicodeFileEncoding
def toUnicodeFileEncoding(path,encoding):

    if path: path = path.replace('\\', os.sep)

    if not encoding:
        if sys.platform == "win32" or sys.platform.lower().startswith('java'):
            # encoding = "mbcs" # Leo 4.2 and previous.
            encoding = 'utf-8' # New in Leo 4.3
        else:
            encoding = app.tkEncoding

    # Yes, this is correct.  All os_path_x functions return Unicode strings.
    return g.toUnicode(path,encoding)
#@-node:ekr.20031218072017.2160:toUnicodeFileEncoding
#@-node:ekr.20031218072017.2145:os.path wrappers (leoGlobals.py)
#@+node:ekr.20031218072017.3151:Scanning... (leoGlobals.py)
#@+node:ekr.20031218072017.3152:g.scanAtFileOptions (used in 3.x read code)
def scanAtFileOptions (h,err_flag=False):

    assert(g.match(h,0,"@file"))
    i = len("@file")
    atFileType = "@file"
    optionsList = []

    while g.match(h,i,'-'):
        #@        << scan another @file option >>
        #@+node:ekr.20031218072017.3153:<< scan another @file option >>
        i += 1 ; err = -1

        if g.match_word(h,i,"asis"):
            if atFileType == "@file":
                atFileType = "@silentfile"
            elif err_flag:
                g.es("using -asis option in:",h)
        elif g.match(h,i,"noref"): # Just match the prefix.
            if atFileType == "@file":
                atFileType = "@rawfile"
            elif atFileType == "@nosentinelsfile":
                atFileType = "@silentfile"
            elif err_flag:
                g.es("ignoring redundant -noref in:",h)
        elif g.match(h,i,"nosent"): # Just match the prefix.
            if atFileType == "@file":
                atFileType = "@nosentinelsfile"
            elif atFileType == "@rawfile":
                atFileType = "@silentfile"
            elif err_flag:
                g.es("ignoring redundant -nosent in:",h)
        elif g.match_word(h,i,"thin"):
            if atFileType == "@file":
                atFileType = "@thinfile"
            elif err_flag:
                g.es("using -thin option in:",h)
        else:
            if 0: # doesn't work
                for option in ("fat","new","now","old","thin","wait"):
                    if g.match_word(h,i,option):
                        optionsList.append(option)
                if len(option) == 0:
                    err = i-1
        # Scan to the next minus sign.
        while i < len(h) and h[i] not in (' ','\t','-'):
            i += 1
        if err > -1:
            z_opt = h[err:i]
            g.es("unknown option:",z_opt,"in",h)
        #@-node:ekr.20031218072017.3153:<< scan another @file option >>
        #@nl

    # Convert atFileType to a list of options.
    for fileType,option in (
        ("@silentfile","asis"),
        ("@nosentinelsfile","nosent"),
        ("@rawfile","noref"),
        ("@thinfile","thin")
    ):
        if atFileType == fileType and option not in optionsList:
            optionsList.append(option)

    # g.trace(atFileType,optionsList)

    return i,atFileType,optionsList
#@-node:ekr.20031218072017.3152:g.scanAtFileOptions (used in 3.x read code)
#@+node:ekr.20031218072017.3156:scanError
# It is dubious to bump the Tangle error count here, but it really doesn't hurt.

def scanError(s):

    '''Bump the error count in the tangle command.'''

    # New in Leo 4.4b1: just set this global.
    g.app.scanErrors +=1
    g.es('',s)
#@-node:ekr.20031218072017.3156:scanError
#@+node:ekr.20031218072017.3157:scanf
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
#@-node:ekr.20031218072017.3157:scanf
#@+node:ekr.20031218072017.3158:Scanners: calling scanError
#@+at 
#@nonl
# These scanners all call g.scanError() directly or indirectly, so they will 
# call g.es if they find an error.  g.scanError() also bumps 
# c.tangleCommands.errors, which is harmless if we aren't tangling, and useful 
# if we are.
# 
# These routines are called by the Import routines and the Tangle routines.
#@-at
#@+node:ekr.20031218072017.3159:skip_block_comment
# Scans past a block comment (an old_style C comment).

def skip_block_comment (s,i):

    assert(g.match(s,i,"/*"))
    j = i ; i += 2 ; n = len(s)

    k = s.find("*/",i)
    if k == -1:
        g.scanError("Run on block comment: " + s[j:i])
        return n
    else: return k + 2
#@-node:ekr.20031218072017.3159:skip_block_comment
#@+node:ekr.20031218072017.3160:skip_braces
#@+at 
#@nonl
# This code is called only from the import logic, so we are allowed to try 
# some tricks.  In particular, we assume all braces are matched in #if blocks.
#@-at
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
#@-node:ekr.20031218072017.3160:skip_braces
#@+node:ekr.20031218072017.3161:skip_php_braces (no longer used)
#@+at 
#@nonl
# 08-SEP-2002 DTHEIN: Added for PHP import support
# Skips from the opening to the matching . If no matching is found i is set to 
# len(s).
# 
# This code is called only from the import logic, and only for PHP imports.
#@-at
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
#@-node:ekr.20031218072017.3161:skip_php_braces (no longer used)
#@+node:ekr.20031218072017.3162:skip_parens
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
#@-node:ekr.20031218072017.3162:skip_parens
#@+node:ekr.20031218072017.3163:skip_pascal_begin_end
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
#@-node:ekr.20031218072017.3163:skip_pascal_begin_end
#@+node:ekr.20031218072017.3164:skip_pascal_block_comment
# Scans past a pascal comment delimited by (* and *).

def skip_pascal_block_comment(s,i):

    j = i
    assert(g.match(s,i,"(*"))
    i = s.find("*)",i)
    if i > -1: return i + 2
    else:
        g.scanError("Run on comment" + s[j:i])
        return len(s)
#@-node:ekr.20031218072017.3164:skip_pascal_block_comment
#@+node:ekr.20031218072017.3165:skip_pascal_string : called by tangle
def skip_pascal_string(s,i):

    j = i ; delim = s[i] ; i += 1
    assert(delim == '"' or delim == '\'')

    while i < len(s):
        if s[i] == delim:
            return i + 1
        else: i += 1

    g.scanError("Run on string: " + s[j:i])
    return i
#@-node:ekr.20031218072017.3165:skip_pascal_string : called by tangle
#@+node:ekr.20031218072017.3166:skip_heredoc_string : called by php import (Dave Hein)
#@+at 
#@nonl
# 08-SEP-2002 DTHEIN:  added function skip_heredoc_string
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
#@-at
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
#@-node:ekr.20031218072017.3166:skip_heredoc_string : called by php import (Dave Hein)
#@+node:ekr.20031218072017.3167:skip_pp_directive
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
#@-node:ekr.20031218072017.3167:skip_pp_directive
#@+node:ekr.20031218072017.3168:skip_pp_if
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
#@-node:ekr.20031218072017.3168:skip_pp_if
#@+node:ekr.20031218072017.3169:skip_pp_part
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
#@-node:ekr.20031218072017.3169:skip_pp_part
#@+node:ekr.20031218072017.3170:skip_python_string
def skip_python_string(s,i,verbose=True):

    if g.match(s,i,"'''") or g.match(s,i,'"""'):
        j = i ; delim = s[i]*3 ; i += 3
        k = s.find(delim,i)
        if k > -1: return k+3
        if verbose:
            g.scanError("Run on triple quoted string: " + s[j:i])
        return len(s)
    else:
        return g.skip_string(s,i)
#@-node:ekr.20031218072017.3170:skip_python_string
#@+node:ekr.20031218072017.2369:skip_string
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
#@-node:ekr.20031218072017.2369:skip_string
#@+node:ekr.20031218072017.3171:skip_to_semicolon
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
#@-node:ekr.20031218072017.3171:skip_to_semicolon
#@+node:ekr.20031218072017.3172:skip_typedef
def skip_typedef(s,i):

    n = len(s)
    while i < n and g.is_c_id(s[i]):
        i = g.skip_c_id(s,i)
        i = g.skip_ws_and_nl(s,i)
    if g.match(s,i,'{'):
        i = g.skip_braces(s,i)
        i = g.skip_to_semicolon(s,i)
    return i
#@-node:ekr.20031218072017.3172:skip_typedef
#@-node:ekr.20031218072017.3158:Scanners: calling scanError
#@+node:ekr.20031218072017.3173:Scanners: no error messages
#@+node:ekr.20031218072017.3174:escaped
# Returns True if s[i] is preceded by an odd number of backslashes.

def escaped(s,i):

    count = 0
    while i-1 >= 0 and s[i-1] == '\\':
        count += 1
        i -= 1
    return (count%2) == 1
#@-node:ekr.20031218072017.3174:escaped
#@+node:ekr.20031218072017.3175:find_line_start
def find_line_start(s,i):

    if i < 0:
        return 0 # New in Leo 4.4.5: add this defensive code.

    # bug fix: 11/2/02: change i to i+1 in rfind
    i = s.rfind('\n',0,i+1) # Finds the highest index in the range.
    if i == -1: return 0
    else: return i + 1
#@-node:ekr.20031218072017.3175:find_line_start
#@+node:ekr.20031218072017.3176:find_on_line
def find_on_line(s,i,pattern):

    j = s.find('\n',i)
    if j == -1: j = len(s)
    k = s.find(pattern,i,j)
    if k > -1: return k
    else: return None
#@-node:ekr.20031218072017.3176:find_on_line
#@+node:ekr.20031218072017.3177:is_c_id
def is_c_id(ch):

    return g.isWordChar(ch)

#@-node:ekr.20031218072017.3177:is_c_id
#@+node:ekr.20031218072017.3178:is_nl
def is_nl(s,i):

    return i < len(s) and (s[i] == '\n' or s[i] == '\r')
#@-node:ekr.20031218072017.3178:is_nl
#@+node:ekr.20031218072017.3179:is_special
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
#@-node:ekr.20031218072017.3179:is_special
#@+node:ekr.20031218072017.3180:is_ws & is_ws_or_nl
def is_ws(c):

    return c == '\t' or c == ' '

def is_ws_or_nl(s,i):

    return g.is_nl(s,i) or (i < len(s) and g.is_ws(s[i]))
#@-node:ekr.20031218072017.3180:is_ws & is_ws_or_nl
#@+node:ekr.20031218072017.3181:match
# Warning: this code makes no assumptions about what follows pattern.

def match(s,i,pattern):

    return s and pattern and s.find(pattern,i,i+len(pattern)) == i
#@-node:ekr.20031218072017.3181:match
#@+node:ekr.20031218072017.3182:match_c_word
def match_c_word (s,i,name):

    if name == None: return False
    n = len(name)
    if n == 0: return False
    return name == s[i:i+n] and (i+n == len(s) or not g.is_c_id(s[i+n]))
#@-node:ekr.20031218072017.3182:match_c_word
#@+node:ekr.20031218072017.3183:match_ignoring_case
def match_ignoring_case(s1,s2):

    if s1 == None or s2 == None: return False

    return s1.lower() == s2.lower()
#@-node:ekr.20031218072017.3183:match_ignoring_case
#@+node:ekr.20031218072017.3184:match_word
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
#@-node:ekr.20031218072017.3184:match_word
#@+node:ekr.20031218072017.3185:skip_blank_lines
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
#@-node:ekr.20031218072017.3185:skip_blank_lines
#@+node:ekr.20031218072017.3186:skip_c_id
def skip_c_id(s,i):

    n = len(s)
    while i < n and g.isWordChar(s[i]):
        i += 1
    return i
#@-node:ekr.20031218072017.3186:skip_c_id
#@+node:ekr.20040705195048:skip_id
def skip_id(s,i,chars=None):

    chars = chars and g.toUnicode(chars,encoding='ascii') or ''
    n = len(s)
    while i < n and (g.isWordChar(s[i]) or s[i] in chars):
        i += 1
    return i
#@nonl
#@-node:ekr.20040705195048:skip_id
#@+node:ekr.20031218072017.3187:skip_line, skip_to_start/end_of_line & tests
#@+at 
#@nonl
# These methods skip to the next newline, regardless of whether the newline 
# may be preceeded by a backslash. Consequently, they should be used only when 
# we know that we are not in a preprocessor directive or string.
#@-at
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
#@+node:ekr.20090517020744.5883:@test g.skip_line
if g.unitTesting:

    # This is a crucial unit test.

    s = 'a\n\nc'

    for i,result in (
        (-1,2), # One too few.
        (0,2),(1,2),
        (2,3),
        (3,4),
        (4,4), # One too many.
    ):
        j = g.skip_line(s,i)
        assert j == result, 'i: %d, expected %d, got %d' % (i,result,j)
#@-node:ekr.20090517020744.5883:@test g.skip_line
#@+node:ekr.20090517020744.5884:@test g.skip_to_end_of_line
if g.unitTesting:

    # This is a crucial unit test.

    s = 'a\n\nc'

    for i,result in (
        (-1,1), # One too few.
        (0,1),(1,1),
        (2,2),
        (3,4),
        (4,4), # One too many.
    ):
        j = g.skip_to_end_of_line(s,i)
        assert j == result, 'i: %d, expected %d, got %d' % (i,result,j)
#@-node:ekr.20090517020744.5884:@test g.skip_to_end_of_line
#@+node:ekr.20090517020744.5885:@test g.skip_to_start_of_line
if g.unitTesting:

    # This is a crucial unit tests.

    s1 = 'a\n\nc'
    table1 = (
        (-1,0), # One too few.
        (0,0),(1,0),
        (2,2),
        (3,3),
        (4,4), # One too many.
    )
    s2 = 'a\n'
    table2 = ((1,0),(2,2)) # A special case at end.

    for s,table in ((s1,table1),(s2,table2)):
        for i,result in table:
            j = g.skip_to_start_of_line(s,i)
            assert j == result, 'i: %d, expected %d, got %d' % (i,result,j)
#@-node:ekr.20090517020744.5885:@test g.skip_to_start_of_line
#@-node:ekr.20031218072017.3187:skip_line, skip_to_start/end_of_line & tests
#@+node:ekr.20031218072017.3188:skip_long
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
#@-node:ekr.20031218072017.3188:skip_long
#@+node:ekr.20031218072017.3189:skip_matching_python_delims
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
#@-node:ekr.20031218072017.3189:skip_matching_python_delims
#@+node:ekr.20060627080947:skip_matching_python_parens
def skip_matching_python_parens(s,i):

    '''Skip from the opening ( to the matching ).

    Return the index of the matching ')', or -1'''

    return skip_matching_python_delims(s,i,'(',')')
#@-node:ekr.20060627080947:skip_matching_python_parens
#@+node:ekr.20031218072017.3190:skip_nl
# We need this function because different systems have different end-of-line conventions.

def skip_nl (s,i):

    '''Skips a single "logical" end-of-line character.'''

    if g.match(s,i,"\r\n"): return i + 2
    elif g.match(s,i,'\n') or g.match(s,i,'\r'): return i + 1
    else: return i
#@-node:ekr.20031218072017.3190:skip_nl
#@+node:ekr.20031218072017.3191:skip_non_ws
def skip_non_ws (s,i):

    n = len(s)
    while i < n and not g.is_ws(s[i]):
        i += 1
    return i
#@-node:ekr.20031218072017.3191:skip_non_ws
#@+node:ekr.20031218072017.3192:skip_pascal_braces
# Skips from the opening { to the matching }.

def skip_pascal_braces(s,i):

    # No constructs are recognized inside Pascal block comments!
    k = s.find('}',i)
    if i == -1: return len(s)
    else: return k
#@-node:ekr.20031218072017.3192:skip_pascal_braces
#@+node:ekr.20031218072017.3193:skip_to_char
def skip_to_char(s,i,ch):

    j = s.find(ch,i)
    if j == -1:
        return len(s),s[i:]
    else:
        return j,s[i:j]
#@-node:ekr.20031218072017.3193:skip_to_char
#@+node:ekr.20031218072017.3194:skip_ws, skip_ws_and_nl
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
#@-node:ekr.20031218072017.3194:skip_ws, skip_ws_and_nl
#@-node:ekr.20031218072017.3173:Scanners: no error messages
#@+node:ekr.20031218072017.3195:splitLines & joinLines
def splitLines (s):

    '''Split s into lines, preserving the number of lines and the ending of the last line.'''

    # g.stat()

    if s:
        return s.splitlines(True) # This is a Python string function!
    else:
        return []

splitlines = splitLines

def joinLines (aList):

    return ''.join(aList)

joinlines = joinLines
#@-node:ekr.20031218072017.3195:splitLines & joinLines
#@-node:ekr.20031218072017.3151:Scanning... (leoGlobals.py)
#@+node:ekr.20040327103735.2:Script Tools (leoGlobals.py)
#@+node:ekr.20050503112513.7:g.executeFile
def executeFile(filename, options= ''):

    if not os.access(filename, os.R_OK): return

    subprocess = g.importExtension('subprocess',None,verbose=False)

    cwd = os.getcwdu()
    fdir, fname = g.os_path_split(filename)

    if subprocess: # Only exists in Python 2.4.
        #@        << define subprocess_wrapper >>
        #@+node:ekr.20050503112513.8:<< define subprocess_wrapper >>
        def subprocess_wrapper(cmdlst):

            # g.trace(cmdlst, fdir)
            # g.trace(subprocess.list2cmdline([cmdlst]))

            p = subprocess.Popen(cmdlst, cwd=fdir,
                universal_newlines=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            stdo, stde = p.communicate()
            return p.wait(), stdo, stde
        #@-node:ekr.20050503112513.8:<< define subprocess_wrapper >>
        #@nl
        rc, so, se = subprocess_wrapper('%s %s %s'%(sys.executable, fname, options))
        if rc:
            g.pr('return code', rc)
        g.pr(so, se)
    else:
        if fdir: os.chdir(fdir)
        d = {'__name__': '__main__'}
        execfile(fname, d)  #, globals()
        os.system('%s %s' % (sys.executable, fname))
        if fdir: os.chdir(cwd)
#@-node:ekr.20050503112513.7:g.executeFile
#@+node:ekr.20040321065415:g.findNode... &,findTopLevelNode
def findNodeInChildren(c,p,headline):

    """Search for a node in v's tree matching the given headline."""

    for p in p.children_iter():
        if p.h.strip() == headline.strip():
            return p.copy()
    return c.nullPosition()

def findNodeInTree(c,p,headline):

    """Search for a node in v's tree matching the given headline."""

    for p in p.subtree_iter():
        if p.h.strip() == headline.strip():
            return p.copy()
    return c.nullPosition()

def findNodeAnywhere(c,headline):

    for p in c.all_positions_with_unique_tnodes_iter():
        if p.h.strip() == headline.strip():
            return p.copy()
    return c.nullPosition()

def findTopLevelNode(c,headline):

    for p in c.rootPosition().self_and_siblings_iter():
        if p.h.strip() == headline.strip():
            return p.copy()
    return c.nullPosition()
#@-node:ekr.20040321065415:g.findNode... &,findTopLevelNode
#@+node:EKR.20040614071102.1:g.getScript & test
def getScript (c,p,useSelectedText=True,forcePythonSentinels=True,useSentinels=True):

    '''Return the expansion of the selected text of node p.
    Return the expansion of all of node p's body text if there
    is p is not the current node or if there is no text selection.'''

    # New in Leo 4.6 b2: use a pristine atFile handler
    # so there can be no conflict with c.atFileCommands.
    # at = c.atFileCommands
    import leo.core.leoAtFile as leoAtFile
    at = leoAtFile.atFile(c)

    w = c.frame.body.bodyCtrl
    p1 = p and p.copy()
    if not p:
        p = c.p
    try:
        if g.app.inBridge:
            s = p.b
        elif p1:
            s = p.b # Bug fix: Leo 8.8.4.
        elif p == c.p:
            if useSelectedText and w.hasSelection():
                s = w.getSelectedText()
            else:
                s = w.getAllText()
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

    # g.trace(type(script),repr(script))
    return script
#@+node:ekr.20090517020744.5878:@test g.getScript strips crlf
if g.unitTesting:

    script = g.getScript(c,p) # This will get the text of this node.
    assert script.find('\r\n') == -1, repr(script)
#@-node:ekr.20090517020744.5878:@test g.getScript strips crlf
#@-node:EKR.20040614071102.1:g.getScript & test
#@+node:ekr.20060624085200:g.handleScriptException
def handleScriptException (c,p,script,script1):

    g.es("exception executing script",color='blue')

    full = c.config.getBool('show_full_tracebacks_in_scripts')

    fileName, n = g.es_exception(full=full)

    if p and not script1 and fileName == "<string>":
        c.goToScriptLineNumber(p,script,n)

    #@    << dump the lines near the error >>
    #@+node:EKR.20040612215018:<< dump the lines near the error >>
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
    #@-node:EKR.20040612215018:<< dump the lines near the error >>
    #@nl
#@-node:ekr.20060624085200:g.handleScriptException
#@+node:ekr.20031218072017.2418:g.initScriptFind (set up dialog)
def initScriptFind(c,findHeadline,changeHeadline=None,firstNode=None,
    script_search=True,script_change=True):

    import leo.core.leoTest as leoTest
    import leo.core.leoGlobals as g

    # Find the scripts.
    p = c.p
    u = leoTest.testUtils(c)
    find_p = u.findNodeInTree(p,findHeadline)
    if find_p:
        find_text = find_p.b
    else:
        g.es("no Find script node",color="red")
        return
    if changeHeadline:
        change_p = u.findNodeInTree(p,changeHeadline)
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
#@-node:ekr.20031218072017.2418:g.initScriptFind (set up dialog)
#@+node:ekr.20090517020744.5888:@test pre-definition of g in scripts
if g.unitTesting:

    # print(g.listToString(dir()))

    for ivar in ('c','g','p'):
        assert ivar in dir()

    assert hasattr(g.app,'tkEncoding')
#@nonl
#@-node:ekr.20090517020744.5888:@test pre-definition of g in scripts
#@-node:ekr.20040327103735.2:Script Tools (leoGlobals.py)
#@+node:ekr.20031218072017.1498:Unicode utils...
#@+node:ekr.20090517020744.5859: Unicode tests
#@+node:ekr.20090517020744.5860:@test open non-existent non-ascii directory
#@@first

if g.unitTesting:

    file = u'Ỗ'
    path = g.os_path_join('Ỗ','Ỗ')
    # print(g.toEncodedString(file,'utf-8'))

    ok,frame = g.openWithFileName(path,c)

    assert not ok and not frame
#@-node:ekr.20090517020744.5860:@test open non-existent non-ascii directory
#@+node:ekr.20090517020744.5861:@test can't open message in g.openWithFileName
#@@first

if g.unitTesting:

    old_c = c
    filename = "testᾹ(U+1FB9: Greek Capital Letter Alpha With Macron)"
    ok,frame = g.openWithFileName(filename,old_c)
    assert(not ok)
#@nonl
#@-node:ekr.20090517020744.5861:@test can't open message in g.openWithFileName
#@+node:ekr.20090517020744.5862:@test atFile.printError
#@@first

if g.unitTesting:

    at = c.atFileCommands
    at.errors = 0

    s = u'La Pe\xf1a'
    s = u'La Peña'
    # s = u'Ă: U+0102: Latin Capital Letter A With Breve'
    at.printError('test of at.printError:',s)
#@-node:ekr.20090517020744.5862:@test atFile.printError
#@+node:ekr.20090517020744.5863:@test % operator with unicode
#@@first

if g.unitTesting:

    s = "testᾹ(U+1FB9: Greek Capital Letter Alpha With Macron)"

    s2 = 'test: %s' % s
#@-node:ekr.20090517020744.5863:@test % operator with unicode
#@+node:ekr.20090517020744.5864:@test failure to convert unicode characters to ascii
#@@first

if g.unitTesting:

    encoding = 'ascii'

    s = '炰'

    s2,ok = g.toUnicodeWithErrorCode(s,encoding)
    assert not ok, 'toUnicodeWithErrorCode returns True for %s with ascii encoding' % s

    s = u'炰'
    s3,ok = g.toEncodedStringWithErrorCode(s,encoding)
    assert not ok, 'toEncodedStringWithErrorCode returns True for %s with ascii encoding' % s
#@-node:ekr.20090517020744.5864:@test failure to convert unicode characters to ascii
#@+node:ekr.20090517020744.5865:@test of round-tripping toUnicode & toEncodedString
#@@first

if g.unitTesting:

    for s,encoding in (
        ('a',    'utf-8'),
        ('a',    'ascii'),
        ('äöü',  'utf-8'),
        ('äöü',  'mbcs'),
        ('炰',    'utf-8'),
        ('炰',    'mbcs'),
    ):
        if g.isValidEncoding(encoding):
            s2,ok = g.toUnicodeWithErrorCode(s,encoding)
            assert ok, 'toUnicodeWithErrorCode fails for %s' %s
            s3,ok = g.toEncodedStringWithErrorCode(s2,encoding)
            assert ok, 'toEncodedStringWithErrorCode fails for %s' % s2
            assert s3 == s, 'Round-trip one fails for %s' %s

            s2 = g.toUnicode(s,encoding)
            s3 = g.toEncodedString(s2,encoding)
            assert s3 == s, 'Round-trip two fails for %s' %s
#@-node:ekr.20090517020744.5865:@test of round-tripping toUnicode & toEncodedString
#@+node:ekr.20090517020744.5866:@test failure with ascii encodings
#@@first

if g.unitTesting:

    encoding = 'ascii'

    s = '炰'
    s2,ok = g.toUnicodeWithErrorCode(s,encoding)
    assert not ok, 'toUnicodeWithErrorCode returns True for %s with ascii encoding' % s

    s = u'炰'
    s3,ok = g.toEncodedStringWithErrorCode(s,encoding)
    assert not ok, 'toEncodedStringWithErrorCode returns True for %s with ascii encoding' % s
#@-node:ekr.20090517020744.5866:@test failure with ascii encodings
#@+node:ekr.20090517020744.5867:@test round trip toUnicode toEncodedString
#@@first

if g.unitTesting:

    table = [
        ('a',    'utf-8'),
        ('a',    'ascii'),
        ('äöü',  'utf-8'),
        ('äöü',  'mbcs'),
        ('炰',   'utf-8'),
    ]

    # __pychecker__ = '--no-reimport'
    import sys

    if sys.platform.startswith('win'):
        data = '炰','mbcs'
        table.append(data)

    for s,encoding in table:
        if g.isValidEncoding(encoding):
            s2,ok = g.toUnicodeWithErrorCode(s,encoding)
            assert ok, 'toUnicodeWithErrorCode fails for %s' %s
            s3,ok = g.toEncodedStringWithErrorCode(s2,encoding)
            assert ok, 'toEncodedStringWithErrorCode fails for %s' % s2
            assert s3 == s, 'Round-trip one failed for %s' %s

            s2 = g.toUnicode(s,encoding)
            s3 = g.toEncodedString(s2,encoding)
            assert s3 == s, 'Round-trip two failed for %s' %s
#@-node:ekr.20090517020744.5867:@test round trip toUnicode toEncodedString
#@-node:ekr.20090517020744.5859: Unicode tests
#@+node:ekr.20081204091750.2:g.emptyString
def emptyString():

    '''Return an empty unicode string.'''

    if isPython3:
        return ''
    else:
        return unicode('')
#@-node:ekr.20081204091750.2:g.emptyString
#@+node:ekr.20080816125725.2:g.isBytes, isChar, isString & isUnicode
# The syntax of these functions must be valid on Python2K and Python3K.

def isBytes(s):
    '''Return True if s is Python3k bytes type.'''
    if g.isPython3:
        # Generates a pylint warning, but that can't be helped.
        return type(s) == type(bytes('a','utf-8'))
    else:
        return False

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
#@-node:ekr.20080816125725.2:g.isBytes, isChar, isString & isUnicode
#@+node:ekr.20061006152327:g.isWordChar & g.isWordChar1
def isWordChar (ch):

    '''Return True if ch should be considered a letter.'''

    return ch and (ch.isalnum() or ch == '_')

def isWordChar1 (ch):

    return ch and (ch.isalpha() or ch == '_')
#@nonl
#@-node:ekr.20061006152327:g.isWordChar & g.isWordChar1
#@+node:ekr.20031218072017.1503:getpreferredencoding from 2.3a2
try:
    # Use Python's version of getpreferredencoding if it exists.
    # It is new in Python 2.3.
    import locale
    getpreferredencoding = locale.getpreferredencoding
except Exception:
    # Use code copied from locale.py in Python 2.3alpha2.
    if sys.platform in ('win32', 'darwin', 'mac'):
        #@        << define getpreferredencoding using _locale >>
        #@+node:ekr.20031218072017.1504:<< define getpreferredencoding using _locale >>
        # On Win32, this will return the ANSI code page
        # On the Mac, it should return the system encoding;
        # it might return "ascii" instead.

        def getpreferredencoding(do_setlocale = True):
            """Return the charset that the user is likely using."""
            try:
                import _locale
                return _locale._getdefaultlocale()[1]
            except Exception:
                return None
        #@-node:ekr.20031218072017.1504:<< define getpreferredencoding using _locale >>
        #@nl
    else:
        #@        << define getpreferredencoding for *nix >>
        #@+node:ekr.20031218072017.1505:<< define getpreferredencoding for *nix >>
        # Avoid pylint complaints about CODESET, LC_CTYPE and nl_langinfo.
        if (
            hasattr(locale,'CODESET') and
            hasattr(locale,'LC_CTYPE') and
            hasattr(locale,'nl_langinfo')
        ):
            codeset =  getattr(locale,'CODESET')
            lc_ctype = getattr(locale,'LC_CTYPE')
            nl_langinfo = getattr(locale,'nl_langinfo')

            def getpreferredencoding(do_setlocale=True):
                """Return the charset that the user is likely using,
                according to the system configuration."""
                try:
                    if do_setlocale:
                        oldloc = locale.setlocale(lc_ctype)
                        locale.setlocale(lc_ctype, "")
                        result = nl_langinfo(codeset)
                        locale.setlocale(lc_ctype, oldloc)
                        return result
                    else:
                        return nl_langinfo(codeset)
                except Exception:
                    return None
        else:
            # Fall back to parsing environment variables :-(
            def getpreferredencoding(do_setlocale = True):
                """Return the charset that the user is likely using,
                by looking at environment variables."""
                try:
                    return locale.getdefaultlocale()[1]
                except Exception:
                    return None

        #@-node:ekr.20031218072017.1505:<< define getpreferredencoding for *nix >>
        #@nl
#@-node:ekr.20031218072017.1503:getpreferredencoding from 2.3a2
#@+node:ekr.20031218072017.1500:isValidEncoding
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
#@nonl
#@-node:ekr.20031218072017.1500:isValidEncoding
#@+node:ekr.20031218072017.1501:reportBadChars & test
def reportBadChars (s,encoding):

    if g.isPython3:  ### To do
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
                if not g.unitTesting:
                    g.es(s2,color='red')
        elif g.isChar(s):
            for ch in s:
                try: unicode(ch,encoding,"strict")
                except Exception: errors += 1
            if errors:
                s2 = "%d errors converting %s (%s encoding) to unicode" % (
                    errors, unicode(s,encoding,'replace'),
                    encoding.encode('ascii','replace'))
                if not g.unitTesting:
                    g.es(s2,color='red')
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
                if not g.unitTesting:
                    g.es(s2,color='red')
        elif g.isChar(s):
            for ch in s:
                try: unicode(ch,encoding,"strict")
                except Exception: errors += 1
            if errors:
                s2 = "%d errors converting %s (%s encoding) to unicode" % (
                    errors, unicode(s,encoding,'replace'),
                    encoding.encode('ascii','replace'))
                if not g.unitTesting:
                    g.es(s2,color='red')
#@+node:ekr.20090517020744.5882:@test g.reportBadChars
#@@first

if g.unitTesting:

    for s,encoding in (
        ('aĂbĂ',  'ascii'),
        (u'aĂbĂ', 'ascii'),
        ('炰',    'ascii'),
        (u'炰',   'ascii'),

        ('aĂbĂ',  'utf-8'),
        (u'aĂbĂ', 'utf-8'),
        ('炰',    'utf-8'),
        (u'炰',   'utf-8'),
    ):

        g.reportBadChars(s,encoding)
#@-node:ekr.20090517020744.5882:@test g.reportBadChars
#@-node:ekr.20031218072017.1501:reportBadChars & test
#@+node:ekr.20031218072017.1502:toUnicode & toEncodedString (and tests)
#@+node:ekr.20050208093800:g.toEncodedString
def toEncodedString (s,encoding,reportErrors=False):

    if isPython3:
        if g.isString(s):
            try:
                s = s.encode(encoding,"strict")
            except UnicodeError:
                if reportErrors:
                    g.reportBadChars(s,encoding)
                s = s.encode(encoding,"replace")

    else:
        if type(s) == types.UnicodeType:
            try:
                s = s.encode(encoding,"strict")
            except UnicodeError:
                if reportErrors:
                    g.reportBadChars(s,encoding)
                s = s.encode(encoding,"replace")
    return s
#@-node:ekr.20050208093800:g.toEncodedString
#@+node:ekr.20080919065433.2:toEncodedStringWithErrorCode (for unit testing)
def toEncodedStringWithErrorCode (s,encoding,reportErrors=False):

    ok = True

    if type(s) == types.UnicodeType:

        try:
            s = s.encode(encoding,"strict")
        except UnicodeError:
            if reportErrors:
                g.reportBadChars(s,encoding)
            s = s.encode(encoding,"replace")
            ok = False

    return s,ok
#@-node:ekr.20080919065433.2:toEncodedStringWithErrorCode (for unit testing)
#@+node:ekr.20050208093800.1:g.toUnicode
def toUnicode (s,encoding,reportErrors=False):

    if isPython3:
        convert,mustConvert,nullVal = str,g.isBytes,''
    else:
        convert,nullVal = unicode,unicode('')
        def mustConvert (s):
            return type(s) != types.UnicodeType

    if not s:
        s = nullVal
    elif mustConvert(s):
        try:
            s = convert(s,encoding,'strict')
        except UnicodeError:
            s = convert(s,encoding,'replace')
            if reportErrors: g.reportBadChars(s,encoding)
    else:
        pass

    return s
#@nonl
#@-node:ekr.20050208093800.1:g.toUnicode
#@+node:ekr.20080919065433.1:toUnicodeWithErrorCode (for unit testing)
def toUnicodeWithErrorCode (s,encoding,reportErrors=False):

    ok = True

    if isPython3:
        if s is None:
            s = ''
        if g.isString(s):
            s = repr(s)
        else:
            pass # Leave s unchanged.
    else:
        if s is None:
            s = unicode('')
        if type(s) != types.UnicodeType:
            try:
                s = unicode(s,encoding,"strict")
            except UnicodeError:
                if reportErrors:
                    g.reportBadChars(s,encoding)
                s = unicode(s,encoding,"replace")
                ok = False
    return s,ok
#@-node:ekr.20080919065433.1:toUnicodeWithErrorCode (for unit testing)
#@-node:ekr.20031218072017.1502:toUnicode & toEncodedString (and tests)
#@-node:ekr.20031218072017.1498:Unicode utils...
#@+node:ekr.20070524083513:Unit testing (leoGlobals.py)
#@+node:ekr.20070619173330:g.getTestVars
def getTestVars ():

    d = g.app.unitTestDict
    c = d.get('c')
    p = d.get('p')
    return c,p and p.copy()
#@-node:ekr.20070619173330:g.getTestVars
#@-node:ekr.20070524083513:Unit testing (leoGlobals.py)
#@+node:EKR.20040612114220:Utility classes, functions & objects...
#@+node:ekr.20050315073003: Index utilities... (leoGlobals)
#@+node:ekr.20050314140957:g.convertPythonIndexToRowCol & test
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
#@+node:ekr.20090517020744.5871:@test g.convertPythonIndexToRowCol
if g.unitTesting:

    s1 = 'abc\n\np\nxy'
    table1 = (
        (-1,(0,0)), # One too small.
        (0,(0,0)),
        (1,(0,1)),
        (2,(0,2)),
        (3,(0,3)), # The newline ends a row.
        (4,(1,0)),
        (5,(2,0)),
        (6,(2,1)),
        (7,(3,0)),
        (8,(3,1)),
        (9,(3,2)), # One too many.
        (10,(3,2)), # Two too many.
    )
    s2 = 'abc\n\np\nxy\n'
    table2 = (
        (9,(3,2)),
        (10,(4,0)), # One too many.
        (11,(4,0)), # Two too many.
    )
    s3 = 'ab' # Test special case.  This was the cause of off-by-one problems.
    table3 = (
        (-1,(0,0)), # One too small.
        (0,(0,0)),
        (1,(0,1)),
        (2,(0,2)), # One too many.
        (3,(0,3)), # Two too many.
    )

    for s,table in ((s1,table1),(s2,table2)):
        for i,result in table:
            row,col = g.convertPythonIndexToRowCol(s,i)
            assert row == result[0], 'i: %d, expected row %d, got %d' % (i,result[0],row)
            assert col == result[1], 'i: %d, expected col %d, got %d' % (i,result[1],col)
#@-node:ekr.20090517020744.5871:@test g.convertPythonIndexToRowCol
#@-node:ekr.20050314140957:g.convertPythonIndexToRowCol & test
#@+node:ekr.20050315071727:g.convertRowColToPythonIndex & test
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
#@+node:ekr.20090517020744.5872:@test g.convertRowColToPythonIndex
if g.unitTesting:

    s1 = 'abc\n\np\nxy'
    s2 = 'abc\n\np\nxy\n'
    table1 = (
        (0,(-1,0)), # One too small.
        (0,(0,0)),
        (1,(0,1)),
        (2,(0,2)),
        (3,(0,3)), # The newline ends a row.
        (4,(1,0)),
        (5,(2,0)),
        (6,(2,1)),
        (7,(3,0)),
        (8,(3,1)),
        (9,(3,2)), # One too large.
    )
    table2 = (
        (9,(3,2)),
        (10,(4,0)), # One two many.
    )
    for s,table in ((s1,table1),(s2,table2)):
        for i,data in table:
            row,col = data
            result = g.convertRowColToPythonIndex(s,row,col)
            assert i == result, 'row: %d, col: %d, expected: %d, got: %s' % (row,col,i,result)
#@-node:ekr.20090517020744.5872:@test g.convertRowColToPythonIndex
#@-node:ekr.20050315071727:g.convertRowColToPythonIndex & test
#@-node:ekr.20050315073003: Index utilities... (leoGlobals)
#@+node:ekr.20031218072017.3140: List utilities...
#@+node:ekr.20031218072017.3141:appendToList
def appendToList(out, s):

    for i in s:
        out.append(i)
#@-node:ekr.20031218072017.3141:appendToList
#@+node:ekr.20031218072017.3142:flattenList
def flattenList (theList):

    result = []
    for item in theList:
        if type(item) == types.ListType:
            result.extend(g.flattenList(item))
        else:
            result.append(item)
    return result
#@-node:ekr.20031218072017.3142:flattenList
#@+node:ekr.20060221081328:maxStringListLength
def maxStringListLength(aList):

    '''Return the maximum string length in a list of strings.'''

    n = 0
    for z in aList:
        if g.isString():
            n = max(n,len(z))

    return n
#@-node:ekr.20060221081328:maxStringListLength
#@-node:ekr.20031218072017.3140: List utilities...
#@+node:ekr.20031218072017.3106:angleBrackets & virtual_event_name
# Returns < < s > >

def angleBrackets(s):

    return ( "<<" + s +
        ">>") # must be on a separate line.

virtual_event_name = angleBrackets
#@-node:ekr.20031218072017.3106:angleBrackets & virtual_event_name
#@+node:ekr.20031218072017.3097:CheckVersion
#@+node:ekr.20060921100435:CheckVersion, helper
# Simplified version by EKR: stringCompare not used.

def CheckVersion (s1,s2,condition=">=",stringCompare=None,delimiter='.',trace=False):

    # CheckVersion is called early in the startup process.
    # import leo.core.leoGlobals as g

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
#@+node:ekr.20070120123930:CheckVersionToInt
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
#@nonl
#@-node:ekr.20070120123930:CheckVersionToInt
#@+node:ekr.20090517020744.5870:@test g.checkVersion
if g.unitTesting:

    for v1,condition,v2 in (
        ('8.4.12','>','8.4.3'),
        ('1','==','1.0'),
        ('2','>','1'),
        ('1.2','>','1'),
        ('2','>','1.2.3'),
        ('1.2.3','<','2'),
        ('1','<','1.1'),
    ):
        assert g.CheckVersion(v1,v2,condition=condition,trace=False)
#@nonl
#@-node:ekr.20090517020744.5870:@test g.checkVersion
#@-node:ekr.20060921100435:CheckVersion, helper
#@+node:ekr.20060921100435.1:oldCheckVersion (Dave Hein)
#@+at
# g.CheckVersion() is a generic version checker.  Assumes a
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
#@-at
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
#@nonl
#@-node:ekr.20060921100435.1:oldCheckVersion (Dave Hein)
#@+node:ekr.20090517020744.5868:@test CheckVersionToInt
if g.unitTesting:

    assert g.CheckVersionToInt('12') == 12,'fail 1'
    assert g.CheckVersionToInt('2a5') == 2, 'fail 2'
    assert g.CheckVersionToInt('b2') == 0, 'fail 3'
#@-node:ekr.20090517020744.5868:@test CheckVersionToInt
#@-node:ekr.20031218072017.3097:CheckVersion
#@+node:ekr.20031218072017.3098:class Bunch (object)
#@+at 
#@nonl
# From The Python Cookbook:  Often we want to just collect a bunch of stuff 
# together, naming each item of the bunch; a dictionary's OK for that, but a 
# small do-nothing class is even handier, and prettier to use.
# 
# Create a Bunch whenever you want to group a few variables:
# 
#     point = Bunch(datum=y, squared=y*y, coord=x)
# 
# You can read/write the named attributes you just created, add others, del 
# some of them, etc:
#     if point.squared > threshold:
#         point.isok = True
#@-at
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
#@-node:ekr.20031218072017.3098:class Bunch (object)
#@+node:ekr.20031219074948.1:class nullObject
# From the Python cookbook, recipe 5.23

class nullObject:

    """An object that does nothing, and does it very well."""

    def __init__   (self,*args,**keys): pass
    def __call__   (self,*args,**keys): return self
    # def __len__    (self): return 0 ###
    def __repr__   (self): return "nullObject"
    def __nonzero__ (self): return 0

    def __delattr__(self,attr):     return self
    def __getattr__(self,attr):     return self
    def __setattr__(self,attr,val): return self
#@-node:ekr.20031219074948.1:class nullObject
#@+node:ekr.20031218072017.3103:g.computeWindowTitle
def computeWindowTitle (fileName):

    if fileName == None:
        return "untitled"
    else:
        path,fn = g.os_path_split(fileName)
        if path:
            title = fn + " in " + path
        else:
            title = fn
        return title
#@-node:ekr.20031218072017.3103:g.computeWindowTitle
#@+node:ekr.20090516135452.5777:g.ensureTrailingNewlines & tests
def ensureTrailingNewlines (s,n):

    s = g.removeTrailing(s,'\t\n\r ')
    return s + '\n' * n


#@+node:ekr.20090516135452.5778:@test ensureTrailingNewlines
if g.unitTesting:

    s = 'aa bc \n \n\t\n'
    s2 = 'aa bc'

    for i in range(3):
        result = g.ensureTrailingNewlines(s,i)
        val = s2 + ('\n' * i)
        assert result == val, 'expected %s, got %s' % (
            repr(val),repr(result))
#@-node:ekr.20090516135452.5778:@test ensureTrailingNewlines
#@-node:ekr.20090516135452.5777:g.ensureTrailingNewlines & tests
#@+node:ekr.20031218072017.3138:g.executeScript
def executeScript (name):

    """Execute a script whose short python file name is given.

    This is called only from the scripts_menu plugin."""

    mod_name,ext = g.os_path_splitext(name)
    theFile = None
    try:
        # This code is in effect an import or a reload.
        # This allows the user to modify scripts without leaving Leo.
        import imp
        theFile,filename,description = imp.find_module(mod_name)
        imp.load_module(mod_name,theFile,filename,description)
    except Exception:
        g.es("exception executing",name,color="red")
        g.es_exception()

    if theFile:
        theFile.close()
#@-node:ekr.20031218072017.3138:g.executeScript
#@+node:ekr.20040331083824.1:g.fileLikeObject
# Note: we could use StringIo for this.

class fileLikeObject:

    """Define a file-like object for redirecting writes to a string.

    The caller is responsible for handling newlines correctly."""

    #@    @+others
    #@+node:ekr.20050404151753: ctor
    def __init__(self,encoding='utf-8',fromString=None):

        # g.trace('g.fileLikeObject:__init__','fromString',fromString)

        # New in 4.2.1: allow the file to be inited from string s.

        self.encoding = encoding

        if fromString:
            self.list = g.splitLines(fromString) # Must preserve newlines!
        else:
            self.list = []

        self.ptr = 0

    # In CStringIO the buffer is read-only if the initial value (fromString) is non-empty.
    #@-node:ekr.20050404151753: ctor
    #@+node:ekr.20050404151753.1:clear
    def clear (self):

        self.list = []
    #@-node:ekr.20050404151753.1:clear
    #@+node:ekr.20050404151753.2:close
    def close (self):

        pass

        # The StringIo version free's the memory buffer.
    #@-node:ekr.20050404151753.2:close
    #@+node:ekr.20050404151753.3:flush
    def flush (self):

        pass
    #@-node:ekr.20050404151753.3:flush
    #@+node:ekr.20050404151753.4:get & getvalue & read
    def get (self):

        return ''.join(self.list)

    getvalue = get # for compatibility with StringIo
    read = get # for use by sax.
    #@-node:ekr.20050404151753.4:get & getvalue & read
    #@+node:ekr.20050404151753.5:readline
    def readline(self): # New for read-from-string (readOpenFile).

        if self.ptr < len(self.list):
            line = self.list[self.ptr]
            # g.trace(repr(line))
            self.ptr += 1
            return line
        else:
            return ''
    #@-node:ekr.20050404151753.5:readline
    #@+node:ekr.20050404151753.6:write
    def write (self,s):

        if s:
            if g.isBytes(s):
                s = g.toUnicode(s,self.encoding)

            self.list.append(s)
    #@-node:ekr.20050404151753.6:write
    #@-others
#@-node:ekr.20040331083824.1:g.fileLikeObject
#@+node:ekr.20031218072017.3126:g.funcToMethod
#@+at 
#@nonl
# The following is taken from page 188 of the Python Cookbook.
# 
# The following method allows you to add a function as a method of any class. 
# That
# is, it converts the function to a method of the class. The method just added 
# is
# available instantly to all existing instances of the class, and to all 
# instances
# created in the future.
# 
# The function's first argument should be self.
# 
# The newly created method has the same name as the function unless the 
# optional
# name argument is supplied, in which case that name is used as the method 
# name.
#@-at
#@@c

def funcToMethod(f,theClass,name=None):

    setattr(theClass,name or f.__name__,f)
    # g.trace(name)
#@-node:ekr.20031218072017.3126:g.funcToMethod
#@+node:ekr.20050920084036.4:g.longestCommonPrefix & g.itemsMatchingPrefixInList
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
#@-node:ekr.20050920084036.4:g.longestCommonPrefix & g.itemsMatchingPrefixInList
#@+node:ekr.20031218072017.3144:g.makeDict
# From the Python cookbook.

def makeDict(**keys):

    """Returns a Python dictionary from using the optional keyword arguments."""

    return keys
#@-node:ekr.20031218072017.3144:g.makeDict
#@+node:ekr.20060221083356:g.prettyPrintType
def prettyPrintType (obj):

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
#@-node:ekr.20060221083356:g.prettyPrintType
#@+node:ekr.20090516135452.5776:g.removeTrailing and removeTrailingWs & tests
# Warning: g.removeTrailingWs already exists.
# Do not change it!

def removeTrailing (s,chars):

    '''Remove all characters in chars from the end of s.'''

    i = len(s)-1
    while i >= 0 and s[i] in chars:
        i -= 1
    i += 1
    return s[:i]
#@+node:ekr.20090516135452.5779:@test removeTrailing
if g.unitTesting:

    s = 'aa bc \n \n\t\n'
    table = (
        ('\t\n ','aa bc'),
        ('abc\t\n ',''),
        ('c\t\n ','aa b'),
    )

    for arg,val in table:
        result = g.removeTrailing(s,arg)
        assert result == val, 'expected %s, got %s' % (val,result)
#@-node:ekr.20090516135452.5779:@test removeTrailing
#@-node:ekr.20090516135452.5776:g.removeTrailing and removeTrailingWs & tests
#@+node:ekr.20060410112600:g.stripBrackets
def stripBrackets (s):

    '''Same as s.lstrip('<').rstrip('>') except it works for Python 2.2.1.'''

    if s.startswith('<'):
        s = s[1:]
    if s.endswith('>'):
        s = s[:-1]
    return s
#@-node:ekr.20060410112600:g.stripBrackets
#@+node:ekr.20061031102333.2:g.getWord & getLine & tests
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
#@nonl
#@+node:ekr.20090517020744.5877:@test g.getLine
if g.unitTesting:

    s = 'a\ncd\n\ne'

    for i,result in (
        (-1,(0,2)), # One too few.
        (0,(0,2)),(1,(0,2)),
        (2,(2,5)),(3,(2,5)),(4,(2,5)),
        (5,(5,6)),
        (6,(6,7)),
        (7,(6,7)), # One too many.
    ):
        j,k = g.getLine(s,i)
        assert (j,k) == result, 'i: %d, expected %d,%d, got %d,%d' % (i,result[0],result[1],j,k)
#@-node:ekr.20090517020744.5877:@test g.getLine
#@+node:ekr.20090517020744.5879:@test g.getWord
if g.unitTesting:

    s = 'abc xy_z5 pdq'
    i,j = g.getWord(s,5)
    assert s[i:j] == 'xy_z5','got %s' % s[i:j]
#@-node:ekr.20090517020744.5879:@test g.getWord
#@-node:ekr.20061031102333.2:g.getWord & getLine & tests
#@+node:ekr.20041219095213:import wrappers
#@+at 
#@nonl
# 1/6/05: The problem with Tkinter is that imp.load_module is equivalent to 
# reload.
# 
# The solutions is easy: simply return sys.modules.get(moduleName) if 
# moduleName is in sys.modules!
#@-at
#@+node:ekr.20040917061619:g.cantImport & test
def cantImport (moduleName,pluginName=None,verbose=True):

    """Print a "Can't Import" message and return None."""

    s = "Can not import %s" % moduleName
    if pluginName: s = s + " from plugin %s" % pluginName

    if not g.app or not g.app.gui:
        g.pr(s)
    elif g.unitTesting:
        return
    elif g.app.gui.guiName() == 'tkinter' and moduleName in ('Tkinter','Pmw'):
        return
    else:
        g.es_print('',s,color="blue")

#@+node:ekr.20090517020744.5869:@test g.cantImport returns None
if g.unitTesting:

    assert(g.cantImport("xyzzy","during unit testing") is None)
#@-node:ekr.20090517020744.5869:@test g.cantImport returns None
#@-node:ekr.20040917061619:g.cantImport & test
#@+node:ekr.20041219095213.1:g.importModule
def importModule (moduleName,pluginName=None,verbose=False):

    '''Try to import a module as Python's import command does.

    moduleName is the module's name, without file extension.'''

    module = sys.modules.get(moduleName)
    if not module:
        try:
            theFile = None
            import imp
            try:
                data = imp.find_module(moduleName) # This can open the file.
                theFile,pathname,description = data
                module = imp.load_module(moduleName,theFile,pathname,description)
            except Exception: # Importing a module can throw exceptions other than ImportError.
                g.cantImport(moduleName,pluginName=pluginName,verbose=verbose)
        finally:
            if theFile: theFile.close()
    return module
#@-node:ekr.20041219095213.1:g.importModule
#@+node:ekr.20041219071407:g.importExtension & helpers
def importExtension (moduleName,pluginName=None,verbose=False,required=False):

    '''Try to import a module.  If that fails,
    try to import the module from Leo's extensions directory.

    moduleName is the module's name, without file extension.'''

    # g.trace(verbose,moduleName,pluginName)

    import os

    module = g.importModule(moduleName,pluginName=pluginName,verbose=False)

    extensionsDir = g.app and g.app.extensionsDir or os.path.join(os.path.dirname(__file__),'..','extensions')

    if not module:
        module = g.importFromPath(moduleName,extensionsDir,pluginName=pluginName,verbose=verbose)

        if not module and required:
            g.cantImportDialog(pluginName,moduleName)
            try: # Avoid raising SystemExit if possible.
                import os ; os._exit(1) # May not be available on all platforms.
            except Exception:
                import sys ; sys.exit(1)

    return module
#@+node:ekr.20060329083657:cantImportDialog & helpers
def cantImportDialog (pluginName,moduleName):

    '''Attempt to show a Tk dialog if an import fails.
    Yes, this is a small Tk dependency, but it can't be helped.'''

    message = '''
%s requires the %s module.
Official distributions contain this module in Leo's extensions folder,
but this module may be missing if you get Leo from cvs.
''' % (pluginName,moduleName)

    if g.app.killed:
        return

    if g.app.unitTesting:
        g.pr('g.importExtension: can not import %s' % moduleName)
        return

    # Requires minimal further imports.
    try:
        import Tkinter as Tk
        root = g.app.root or Tk.Tk()
        title = 'Can not import %s' % moduleName
        top = createDialogFrame(Tk,root,title,message)
        root.wait_window(top)
    except ImportError:
        g.pr('Can not import %s' % moduleName)
        g.pr('Can not import Tkinter')
        g.pr('Leo must now exit')
        g.pr(g.callers())
#@+node:ekr.20060329083310.1:createDialogFrame
def createDialogFrame(Tk,root,title,message):

    """Create the Tk.Toplevel widget for a leoTkinterDialog."""

    top = Tk.Toplevel(root)
    top.title(title)

    def onKey(event,top=top):
        if event.char.lower() in ('\n','\r'):
            top.destroy()
    top.bind("<Key>",onKey)

    f = Tk.Frame(top)
    f.pack(side="top",expand=1,fill="both")

    label = Tk.Label(f,text=message)
    label.pack(pady=10)

    def okButton(top=top):
        top.destroy()

    buttons = {"text":'OK',"command":okButton,"default":True}, # Singleton tuple.
    createDialogButtons(Tk,top,buttons)

    center(top)
    top.lift()
    top.focus_force()

    if not g.app.unitTesting: # Attach the icon at idle time.
        def attachIconCallback(top=top):
            g.app.gui.attachLeoIcon(top)
        top.after_idle(attachIconCallback)

    return top
#@-node:ekr.20060329083310.1:createDialogFrame
#@+node:ekr.20060329083310.2:createDialogButtons
def createDialogButtons (Tk,top,buttons):

    """Create a row of buttons.

    buttons is a list of dictionaries containing the properties of each button."""

    f = Tk.Frame(top)
    f.pack(side="top",padx=30)

    for d in buttons:
        text = d.get("text","<missing button name>")
        isDefault = d.get("default",False)
        underline = d.get("underline",0)
        command = d.get("command",None)
        bd = g.choose(isDefault,4,2)

        b = Tk.Button(f,width=6,text=text,bd=bd,underline=underline,command=command)
        b.pack(side="left",padx=5,pady=10)
#@-node:ekr.20060329083310.2:createDialogButtons
#@+node:ekr.20060329085417.1:center
def center(top):

    """Center the dialog on the screen.

    WARNING: Call this routine _after_ creating a dialog.
    (This routine inhibits the grid and pack geometry managers.)"""

    sw = top.winfo_screenwidth()
    sh = top.winfo_screenheight()
    w,h,x,y = g.get_window_info(top)

    # Set the new window coordinates, leaving w and h unchanged.
    x = (sw - w)/2
    y = (sh - h)/2
    top.geometry("%dx%d%+d%+d" % (w,h,x,y))

    return w,h,x,y
#@-node:ekr.20060329085417.1:center
#@+node:ekr.20060329085612:get_window_info
# WARNING: Call this routine _after_ creating a dialog.
# (This routine inhibits the grid and pack geometry managers.)

def get_window_info (top):

    # This is an emergency measure: this call is NOT a major Tk-dependency.
    top.update_idletasks() # Required to get proper info.

    # Get the information about top and the screen.
    geom = top.geometry() # geom = "WidthxHeight+XOffset+YOffset"
    dim,x,y = geom.split('+')
    w,h = dim.split('x')
    w,h,x,y = int(w),int(h),int(x),int(y)

    return w,h,x,y
#@-node:ekr.20060329085612:get_window_info
#@-node:ekr.20060329083657:cantImportDialog & helpers
#@-node:ekr.20041219071407:g.importExtension & helpers
#@+node:ekr.20031218072017.2278:g.importFromPath
def importFromPath (name,path,pluginName=None,verbose=False):

    fn = g.shortFileName(name)
    moduleName,ext = g.os_path_splitext(fn)
    path = g.os_path_normpath(path)
    path = g.toEncodedString(path,app and app.tkEncoding or 'ascii')

    # g.trace(verbose,name,pluginName)
    module = sys.modules.get(moduleName)
    if not module:
        try:
            theFile = None
            import imp
            try:
                data = imp.find_module(moduleName,[path]) # This can open the file.
                theFile,pathname,description = data
                module = imp.load_module(moduleName,theFile,pathname,description)
            except ImportError:
                if 0: # verbose:
                    g.es_print("exception in g.importFromPath",color='blue')
                    g.es_exception()
            except Exception:
                g.es_print("unexpected exception in g.importFromPath(%s)" %
                    (name),color='blue')
                g.es_exception()
        # Put no return statements before here!
        finally: 
            if theFile: theFile.close()

    if not module:
        g.cantImport(moduleName,pluginName=pluginName,verbose=verbose)

    return module
#@-node:ekr.20031218072017.2278:g.importFromPath
#@-node:ekr.20041219095213:import wrappers
#@+node:ekr.20040629162023:readLines class and generator
#@+node:EKR.20040612114220.3:g.readLinesGenerator
# This has been replaced by readLinesClass because
# yield is not valid in jython.

# def readLinesGenerator(s):

    # for line in g.splitLines(s):
        # # g.trace(repr(line))
        # yield line
    # yield ''
#@-node:EKR.20040612114220.3:g.readLinesGenerator
#@+node:EKR.20040612114220.4:class readLinesClass
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
#@-node:EKR.20040612114220.4:class readLinesClass
#@-node:ekr.20040629162023:readLines class and generator
#@-node:EKR.20040612114220:Utility classes, functions & objects...
#@+node:ekr.20031218072017.3197:Whitespace...
#@+node:ekr.20051014175117:g.adjustTripleString (same as removeExtraLws)
def adjustTripleString (s,tab_width):

    '''Remove leading indentation from a triple-quoted string.

    This works around the fact that Leo nodes can't represent underindented strings.
    '''

    # Compute the minimum leading whitespace of all non-blank lines.
    lines = g.splitLines(s)
    w = -1
    for s in lines:
        if s.strip():
            lws = g.get_leading_ws(s)
            w2 = g.computeWidth(lws,tab_width)
            if w < 0: w = w2
            else:     w = min(w,w2)
            # g.trace('w',w)

    if w <= 0: return s

    # Remove the leading whitespace.
    result = [g.removeLeadingWhitespace(line,w,tab_width) for line in lines]
    result = ''.join(result)

    return result
#@-node:ekr.20051014175117:g.adjustTripleString (same as removeExtraLws)
#@+node:ekr.20031218072017.3198:computeLeadingWhitespace
# Returns optimized whitespace corresponding to width with the indicated tab_width.

def computeLeadingWhitespace (width, tab_width):

    if width <= 0:
        return ""
    if tab_width > 1:
        tabs   = width / tab_width
        blanks = width % tab_width
        return ('\t' * tabs) + (' ' * blanks)
    else: # 7/3/02: negative tab width always gets converted to blanks.
        return (' ' * width)
#@-node:ekr.20031218072017.3198:computeLeadingWhitespace
#@+node:ekr.20031218072017.3199:computeWidth
# Returns the width of s, assuming s starts a line, with indicated tab_width.

def computeWidth (s, tab_width):

    w = 0
    for ch in s:
        if ch == '\t':
            w += (abs(tab_width) - (w % abs(tab_width)))
        else:
            w += 1
    return w
#@-node:ekr.20031218072017.3199:computeWidth
#@+node:ekr.20031218072017.3200:get_leading_ws
def get_leading_ws(s):

    """Returns the leading whitespace of 's'."""

    i = 0 ; n = len(s)
    while i < n and s[i] in (' ','\t'):
        i += 1
    return s[0:i]
#@-node:ekr.20031218072017.3200:get_leading_ws
#@+node:ekr.20031218072017.3201:optimizeLeadingWhitespace
# Optimize leading whitespace in s with the given tab_width.

def optimizeLeadingWhitespace (line,tab_width):

    i, width = g.skip_leading_ws_with_indent(line,0,tab_width)
    s = g.computeLeadingWhitespace(width,tab_width) + line[i:]
    return s
#@-node:ekr.20031218072017.3201:optimizeLeadingWhitespace
#@+node:ekr.20040723093558:regularizeTrailingNewlines
#@+at
# 
# The caller should call g.stripBlankLines before calling this routine if 
# desired.
# 
# This routine does _not_ simply call rstrip(): that would delete all trailing 
# whitespace-only lines, and in some cases that would change the meaning of 
# program or data.
# 
#@-at
#@@c

def regularizeTrailingNewlines(s,kind):

    """Kind is 'asis', 'zero' or 'one'."""

    pass
#@-node:ekr.20040723093558:regularizeTrailingNewlines
#@+node:ekr.20031218072017.3202:removeLeadingWhitespace
# Remove whitespace up to first_ws wide in s, given tab_width, the width of a tab.

def removeLeadingWhitespace (s,first_ws,tab_width):

    j = 0 ; ws = 0
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
#@-node:ekr.20031218072017.3202:removeLeadingWhitespace
#@+node:ekr.20050211120242.2:g.removeExtraLws & test
def removeExtraLws (s,tab_width):

    '''Remove extra indentation from one or more lines.

    Warning: used by getScript.  This is *not* the same as g.adjustTripleString.'''

    lines = g.splitLines(s)

    # Find the first non-blank line and compute w, the width of its leading whitespace.
    for s in lines:
        if s.strip():
            lws = g.get_leading_ws(s)
            w = g.computeWidth(lws,tab_width)
            # g.trace('w',w)
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
#@+node:ekr.20090517020744.5881:@test g.removeExtraLws
if g.unitTesting:

    for s,expected in (
        (' a\n b\n c', 'a\nb\nc'),
        (' \n  A\n    B\n  C\n', '\nA\n  B\nC\n'),
    ):
        result = g.removeExtraLws(s,c.tab_width)
        assert result == expected, '\ns: %s\nexpected: %s\nresult:   %s' % (
            repr(s),repr(expected),repr(result))
#@-node:ekr.20090517020744.5881:@test g.removeExtraLws
#@-node:ekr.20050211120242.2:g.removeExtraLws & test
#@+node:ekr.20031218072017.3203:removeTrailingWs & test
# Warning: string.rstrip also removes newlines!

def removeTrailingWs(s):

    j = len(s)-1
    while j >= 0 and (s[j] == ' ' or s[j] == '\t'):
        j -= 1
    return s[:j+1]
#@+node:ekr.20090516135452.5856:@test removeTrailingWs
if g.unitTesting:

    table = (
        ('a a\t','a a'),
        ('a a\t\n','a a\t\n'),
        ('a a ','a a'),
    )

    for s,val in table:
        result = g.removeTrailingWs(s)
        assert result == val, 'expected %s, got %s' % (
            repr(val),repr(result))
#@-node:ekr.20090516135452.5856:@test removeTrailingWs
#@-node:ekr.20031218072017.3203:removeTrailingWs & test
#@+node:ekr.20031218072017.3204:skip_leading_ws
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
#@-node:ekr.20031218072017.3204:skip_leading_ws
#@+node:ekr.20031218072017.3205:skip_leading_ws_with_indent
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
#@-node:ekr.20031218072017.3205:skip_leading_ws_with_indent
#@+node:ekr.20040723093558.1:stripBlankLines
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
#@-node:ekr.20040723093558.1:stripBlankLines
#@-node:ekr.20031218072017.3197:Whitespace...
#@+node:ekr.20060913091602:ZODB support
#@+node:ekr.20060913090832.1:g.init_zodb
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
#@nonl
#@-node:ekr.20060913090832.1:g.init_zodb
#@-node:ekr.20060913091602:ZODB support
#@-others
#@-node:ekr.20031218072017.3093:@thin leoGlobals.py
#@-leo
