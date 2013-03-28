#@+leo-ver=5-thin
#@+node:tbrown.20080613095157.2: * @file active_path.py
#@+<< docstring >>
#@+node:tbrown.20080613095157.3: ** << docstring >>
'''Synchronizes \@path nodes with folders.

If a node is named '\@path *<path_to_folder>*', the content (file and folder names)
of the folder and the children of that node will synchronized whenever you double-click
the node's status-iconbox.

For files not previously seen in a folder a new node will appear on top of the
children list (with a mark).

Folders appear in the list as /foldername/. If you double click on the icon-box
of the folder node, it will have children added to it based on the contents of
the folder on disk. These folders have the '@path' directive as the first line
of their body text.

When files are deleted from the folder and the list is updated by double
clicking the files will appear in the list as *filename* (or */foldername/*).

You can describe files and directories in the body of the nodes.

You can organize files and directories with organizer nodes, an organizer node
name cannot contain with '/'.

Files and folders can be created by entering a node with the required name as
its headline (must start and/or end with "/" for a folder) and then double
clicking on the node's status-iconbox.

\@auto nodes can be set up for existing files can be loaded by
double clicking on the node's status-iconbox. If you prefer
\@shadow or something else use the "active_path_attype" setting,
without the "@".

There are commands on the Plugins active_path submenu:

- show path - show the current path
- set absolute path - changes a node "/dirname/" to "@path /absolute/path/to/dirname".
- purge vanished (recursive) - remove *entries*
- update recursive - recursive load of directories, use with caution on large
  file systems

If you want to use an input other than double clicking a node's status-iconbox
set active_path_event to a value like 'iconrclick1' or 'iconclick1'.

There are @settings for ignoring directory entries and automatically loading files.  ``re.search`` is used, rather than ``re.match``, so patterns need only match part of the filename, not the whole filename.

The body of the @setting ``@data active_path_ignore`` is a list of regex
patterns, one per line.  Directory entries matching any pattern in the list will be ignored.  The names of directories used for matching will have forward slashes around them ('/dirname/'), so patterns can use this to distinguish between directories and files.

The body of the @setting ``@data active_path_autoload`` is a list of regex
patterns, one per line.  File entries matching any pattern in the list will be loaded automatically.  This works only with files, not directories (but you can load directories recursively anyway).

Set ``@bool active_path_load_docstring = True`` to have active_path load the docstring
of .py files automatically.  These nodes start with the special string::

    @language rest # AUTOLOADED DOCSTRING

which must be left intact if you want active path to be able to double-click load
the file later.

\@float active_path_timeout_seconds (default 10.) controls the maximum
time active_path will spend on a recursive operation.

\@int active_path_max_size (default 1000000) controls the maximum
size file active_path will open without query.

active_path is a rewrite of the at_directory plugin to use \@path directives
(which influence \@auto and other \@file type directives), and to handle
sub-folders more automatically.

'''
#@-<< docstring >>

#@@language python
#@@tabwidth -4

import leo.core.leoGlobals as g

import leo.core.leoPlugins as leoPlugins
    # uses leoPlugins.TryNext

import os
import re
import ast # for docstring loading
import time # for recursion bailout

from leo.plugins.plugins_menu import PlugIn

testing = False

__version__ = "0.2"

#@+<< version history >>
#@+node:ekr.20090120065737.1: ** << version history >>
#@@nocolor-node
#@+at
# 
# 0.2 EKR: replaced begin/endUpdate with c.redraw(p)
#@-<< version history >>

#@+others
#@+node:tbrown.20091128094521.15048: ** init
if g.app.gui.guiName() == "qt":
    # for the right click context menu
    from PyQt4 import QtCore

def init():
    g.registerHandler('after-create-leo-frame', attachToCommander)
    g.act_on_node.add(active_path_act_on_node, priority = 90)

    g.plugin_signon(__name__)

    if g.app.gui.guiName() == "qt":
        g.tree_popup_handlers.append(popup_entry)

    return True
#@+node:tbrown.20091128094521.15047: ** attachToCommander
# defer binding event until c exists
def attachToCommander(t,k):
    c = k.get('c')
    event = c.config.getString('active_path_event') or "icondclick1"
    g.registerHandler(event, lambda t,k: onSelect(t,k))

    # not using a proper class, so
    c.__active_path = {'ignore': [], 'autoload': []}

    if c.config.getData('active_path_ignore'):
        c.__active_path['ignore'] = [re.compile(i, re.IGNORECASE)
            for i in c.config.getData('active_path_ignore')]

    if c.config.getData('active_path_autoload'):
        c.__active_path['autoload'] = [re.compile(i, re.IGNORECASE)
            for i in c.config.getData('active_path_autoload')]

    if c.config.getBool('active_path_load_docstring'):
        c.__active_path['load_docstring'] = True
    else:
        c.__active_path['load_docstring'] = False

    if c.config.getFloat('active_path_timeout_seconds'):
        c.__active_path['timeout'] = c.config.getFloat('active_path_timeout_seconds')
    else:
        c.__active_path['timeout'] = 10.

    if c.config.getInt('active_path_max_size'):
        c.__active_path['max_size'] = c.config.getInt('active_path_max_size')
    else:
        c.__active_path['max_size'] = 1000000

    c.__active_path['DS_SENTINEL'] = "@language rest # AUTOLOADED DOCSTRING"
#@+node:tbrown.20091128094521.15042: ** popup_entry
def mkCmd(cmd, c):

    def f():
        return cmd(c)

    return f

def popup_entry(c,p,menu):

    pathmenu = menu.addMenu("Path")

    for i in globals():
        if i.startswith('cmd_'):

            a = pathmenu.addAction(PlugIn.niceMenuName(i))
            CMD = globals()[i]
            a.connect(a, QtCore.SIGNAL("triggered()"), mkCmd(CMD,c))
#@+node:tbrown.20091128094521.15037: ** isDirNode
def isDirNode(p):

    return (
        p.h.startswith('@path ') or 
        #  '/foo/' form *assumes* @path in body
        (not p.h.strip().startswith('@') and p.h.strip().endswith('/'))
        or p.h.strip().startswith('/')
        )
#@+node:tbrown.20091128094521.15039: ** isFileNode
def isFileNode(p):
    """really isEligibleToBecomeAFileNode"""
    return (not p.h.strip().startswith('@') and not p.hasChildren() and
      not isDirNode(p) and isDirNode(p.parent())
      and (not p.b.strip() or # p.b.startswith(c.__active_path['DS_SENTINEL']
      p.b.startswith("@language rest # AUTOLOADED DOCSTRING")  # no c!
      ))
#@+node:tbrown.20091129085043.9329: ** inReList
def inReList(txt, lst):

    for pat in lst:
        if pat.search(txt):
            return True

    return False
#@+node:tbrown.20091128094521.15040: ** subDir
def subDir(d, p):

    if p.h.strip().startswith('@path'):
        p = p.h.split(None,1)
        if len(p) != 2:
            return None
        p = p[1]

    elif p.b.strip().startswith('@path'):
        p = p.b.split('\n',1)[0].split(None,1)
        if len(p) != 2:
            return None
        p = p[1]

    else:
        p = p.h.strip(' /')

    return os.path.join(d,p)
#@+node:tbrown.20080613095157.4: ** onSelect
def onSelect (tag,keywords):
    """Determine if a file or directory status-iconbox was clicked, and the path"""
    c = keywords.get('c') or keywords.get('new_c')
    if not c: return
    p = keywords.get("p")

    p.expand()

    pos = p.copy()

    path = getPath(c, p)

    if path:
        if sync_node_to_folder(c,pos,path):
            c.requestRedrawFlag = True
            c.redraw()
            return True

    return None
#@+node:tbrown.20080616153649.4: ** getPath
def getPath(c, p):

    for n in p.self_and_parents():
        if n.h.startswith('@path'):
            break
    else:
        return None  # must have a full fledged @path in parents

    aList = g.get_directives_dict_list(p)
    path = c.scanAtPathDirectives(aList)
    if (not isDirNode(p)):  # add file name
        h = p.h.split(None, 1)
        if h[0].startswith('@') and len(h) == 2:
            path = os.path.join(path, h[1])
        else:
            path = os.path.join(path, p.h.strip())
    return path
#@+node:tbrown.20090219133655.230: ** getPathOld
def getPathOld(p):
    # NOT USED, my version which does its own @path scanning
    p = p.copy()

    path = []

    while p:
        h = p.h

        if g.match_word(h,0,"@path"):  # top of the tree
            path.insert(0,os.path.expanduser(h[6:].strip()))
            d = os.path.join(*path)
            return d

        elif h.startswith('@'):  # some other directive, run away
            break

        elif isDirNode(p):  # a directory
            path.insert(0,h.strip('/*'))

        elif not p.hasChildren():  # a leaf node, assume a file
            path.insert(0,h.strip('*'))

        p = p.parent()

    return None
#@+node:tbrown.20080613095157.5: ** flattenOrganizers
def flattenOrganizers(p):
    """Children of p, some of which may be in organizer nodes

    In the following example nodeA's children are nodes B, F, and G::

      /nodeA/
         nodeB
         /nodeC/
            nodeD
            nodeE
         oldStuff
            nodeF
            nodeG    
    """    
    for n in p.children():
        yield n
        if (not isDirNode(n)
            and not n.h.startswith('@')):
            for i in flattenOrganizers(n):
                yield i
#@+node:tbrown.20080613095157.6: ** sync_node_to_folder
def sync_node_to_folder(c,parent,d,updateOnly=False, recurse=False):
    """Decide whether we're opening or creating a file or a folder"""

    if (not updateOnly
      and not recurse
      and isDirNode(parent) and not parent.h.strip().startswith('@path')
      and not parent.b.strip().startswith('@path')):
        createDir(c,parent,d)
        return True  # even if it didn't happen, else get stuck in edit mode w/o focus

    if os.path.isdir(d):
        if (isDirNode(parent)
            and (not updateOnly or recurse or parent.hasChildren())):
            # no '/' or @path implies organizer
            openDir(c,parent,d)
            return True

    if updateOnly: return False

    if os.path.isfile(d) and isFileNode(parent):
        openFile(c,parent,d)
        return True

    if isFileNode(parent):
        createFile(c,parent,d)
        return True  # even if it didn't happen, else get stuck in edit mode w/o focus

    return False
#@+node:tbrown.20080613095157.7: ** createDir
def createDir(c,parent,d):
    """Ask if we should create a new folder"""
    newd = parent.h.strip(' /')
    ok = g.app.gui.runAskYesNoDialog(c, 'Create folder?',
        'Create folder '+newd+'?')
    if ok == 'no':
        return False
    parent.h = '/'+newd+'/'
    if parent.b.strip():
        parent.b = '@path '+newd+'\n'+parent.b
    else:
        parent.b = '@path '+newd

    os.mkdir(os.path.join(d, newd))
    return True
#@+node:tbrown.20080613095157.8: ** createFile
def createFile(c,parent,d):
    """Ask if we should create a new file"""
    directory = os.path.dirname(d)
    if not os.path.isdir(directory):
        g.error('Create parent directories first')
        return False

    d = os.path.basename(d)
    atType = c.config.getString('active_path_attype') or 'auto'
    ok = g.app.gui.runAskYesNoDialog(c, 'Create / load file?',
        'Create file @'+atType+' '+d+'?')
    if ok == 'no':
        return False
    c.setHeadString(parent, '@'+atType+' '+d)
    c.bodyWantsFocus()
    return True
#@+node:tbrown.20080613095157.9: ** openFile
def openFile(c,parent,d, autoload=False):
    """Open an existing file"""
    # hdr = os.path.basename(d)
    # parent.h = '@auto '+hdr
    # parent.b = file(d).read()

    path = getPath(c, parent)

    if not os.path.isfile(path):
        return

    if not autoload:
        binary_open = g.os_path_splitext(path)[-1].lower() in (
            c.config.getData('active_path_bin_open') or '')
            
        if not binary_open:
            start = open(path).read(100)
            for i in start:
                if ord(i) == 0:
                    binary_open = True
                    break
                    
        if binary_open:
            g.es('Treating file as binary')
            g.handleUrl('file://' + path,c=c)
            # if not query(c, "File may be binary, continue?"):
            #     return
            return

        if os.stat(path).st_size > c.__active_path['max_size']:
            if not query(c, "File size greater than %d bytes, continue?" %
              c.__active_path['max_size']):
                return

    c.importCommands.createOutline(d,parent=parent,atAuto=True)
    atType = c.config.getString('active_path_attype') or 'auto'
    parent.h = '@' + atType + ' ' + parent.h

    c.bodyWantsFocus()
#@+node:tbrown.20080613095157.10: ** openDir
def openDir(c,parent,d):
    """Expand / refresh an existing folder"""

    # compare folder content to children
    try:
        path, dirs, files = next(os.walk(d))
    except StopIteration:
        # directory deleted?
        c.setHeadString(parent,'*'+parent.h.strip('*')+'*')
        return

    # parent.expand()  # why?

    oldlist = set()
    newlist = []

    # get children info
    for p in flattenOrganizers(parent):
        entry = p.h.strip('/*')
        if entry.startswith('@'):  # remove only the @part
            directive = entry.split(None,1)
            if len(directive) > 1:
                entry = entry[len(directive[0]):].strip()
        oldlist.add(entry)

    for d2 in dirs:
        if d2 in oldlist:
            oldlist.discard(d2)
        else:
            newlist.append('/'+d2+'/')
    for f in files:
        if f in oldlist:
            oldlist.discard(f)
        else:
            newlist.append(f)

    # insert newlist
    newlist.sort()
    ignored = 0
    newlist.reverse()  # un-reversed by the following loop
    for name in newlist:

        if inReList(name, c.__active_path['ignore']):
            ignored += 1
            continue

        p = parent.insertAsNthChild(0)
        c.setChanged(True)
        c.setHeadString(p,name)
        if name.startswith('/'): 
            # sufficient test of dirness as we created newlist
            c.setBodyString(p, '@path '+name.strip('/'))
        elif inReList(name, c.__active_path['autoload']):
            openFile(c, p, os.path.join(d, p.h), autoload=True)
        elif (c.__active_path['load_docstring'] and
            name.lower().endswith(".py")):
            p.b = c.__active_path['DS_SENTINEL']+"\n\n"+loadDocstring(os.path.join(d, p.h))
        p.setMarked()
        p.contract()

    if ignored:
        g.es('Ignored %d files in directory' % ignored)

    # warn / mark for orphan oldlist
    for p in flattenOrganizers(parent):
        h = p.h.strip('/*')  # strip / and *
        if (h not in oldlist 
            or (p.hasChildren() and not isDirNode(p))):  # clears bogus '*' marks
            nh = p.h.strip('*')  # strip only *
        else:
            nh = '*'+p.h.strip('*')+'*'
            if isDirNode(p):
                for orphan in p.subtree():
                    c.setHeadString(orphan, '*'+orphan.h.strip('*')+'*')
        if p.h != nh:  # don't dirty node unless we must
            c.setHeadString(p,nh)
#@+node:tbrown.20100304090709.31081: ** loadDocstring
def loadDocstring(file_path):
    try:
        src = open(file_path).read()
        src = src.replace('\r\n', '\n').replace('\r','\n')+'\n'
    except IOError:
        doc_string = "**COULD NOT OPEN / READ FILE**"
        return doc_string

    try:
        ast_info = ast.parse(src)
        doc_string = ast.get_docstring(ast_info)
    except SyntaxError:
        doc_string = "**SYNTAX ERROR IN MODULE SOURCE**"

    if not doc_string:
        doc_string = "**NO DOCSTRING**"

    return doc_string
#@+node:tbrown.20100401100336.24943: ** query
def query(c, s):
    """Return yes/no answer from user for question s"""

    ok = g.app.gui.runAskYesNoCancelDialog(c,
        title = 'Really?',
        message = s)

    return ok == 'yes'
#@+node:tbrown.20090225191501.1: ** run_recursive
def run_recursive(c):
    """Recursive descent."""

    c.__active_path['start_time'] = time.time()
    p = c.p
    
    aList = [z.copy() for z in c.p.self_and_subtree()]
    for p2 in reversed(aList):
        if time.time() - c.__active_path['start_time'] >= c.__active_path['timeout']:
            g.es('Recursive processing aborts after %f seconds' %
                c.__active_path['timeout'])
            break
        yield p2

    c.redraw(p)
#@+node:ville.20090223183051.1: ** act on node
def cmd_ActOnNode(c, p=None, event=None):
    """ act_on_node handler for active_path.py
    """

    # implementation mostly copied from onSelect
    if p is None:
        p = c.currentPosition()

    pos = p.copy()
    path = getPath(c, p)

    if path:
        sync_node_to_folder(c,pos,path)
        c.requestRedrawFlag = True
        c.redraw()
        return True

    else:
        raise leoPlugins.TryNext

active_path_act_on_node = cmd_ActOnNode
#@+node:tbrown.20111207143354.19381: ** cmd_MakeDir
def cmd_MakeDir(c):
    
    txt = g.app.gui.runAskOkCancelStringDialog(
        c, 'Directory name' ,'Directory name')
    if txt:
        nd = c.p.insertAsNthChild(0)
        nd.h = '/'+txt.strip('/')+'/'
        nd.b = '@path %s\n' % txt
        c.selectPosition(nd)
        c.redraw()
    g.es("Path will be created if a file is saved on it")
#@+node:tbrown.20080616153649.2: ** cmd_ShowCurrentPath
def cmd_ShowCurrentPath(c):
    """Just show the path to the current file/directory node in the log pane."""
    g.es(getPath(c, c.p))
#@+node:tbrown.20100401100336.13608: ** cmd_LoadRecursive
def cmd_LoadRecursive(c):
    """Recursive update, with expansions."""

    for s in run_recursive(c):
        path = getPath(c, s)
        if path:
            sync_node_to_folder(c,s,path,updateOnly=True,recurse=True)
#@+node:tbrown.20080619080950.16: ** cmd_UpdateRecursive
def cmd_UpdateRecursive(c):
    """Recursive update, no new expansions."""

    for s in run_recursive(c):
        path = getPath(c, s)
        if path:
            sync_node_to_folder(c,s,path,updateOnly=True)
#@+node:tbrown.20091214212801.13475: ** cmd_SetNodeToAbsolutePathRecursive
def cmd_SetNodeToAbsolutePathRecursive(c):
    """Change "/dirname/" to "@path /absolute/path/to/dirname", recursively"""

    for s in run_recursive(c):
        cmd_SetNodeToAbsolutePath(c, p=s)
#@+node:tbrown.20080616153649.5: ** cmd_SetNodeToAbsolutePath
def cmd_SetNodeToAbsolutePath(c, p=None):
    """Change "/dirname/" to "@path /absolute/path/to/dirname"."""

    if not p:
        p = c.p

    path = getPath(c, p)
    d = p.h.split(None, 1)
    if len(d) > 1 and d[0].startswith('@'):
        type_  = d[0]+" "
    elif isDirNode(p):
        type_ = "@path "
        p.b = '# path Created from node "%s"\n\n' % p.h + p.b
    else:
        type_ = "@auto "
    p.h = type_+path
#@+node:tbrown.20080618141617.879: ** cmd_PurgeVanishedFiles
def cond(p):
    return p.h.startswith('*') and p.h.endswith('*')

def condunl(p):
    return (isFileNode(p) and not p.b.strip()
            or
            isDirNode(p) and not p.hasChildren())

def dtor(p):
    # g.es(p.h)
    p.doDelete()

def cmd_PurgeVanishedFilesHere(c):
    """Remove files no longer present, i.e. "*filename*" entries."""
    p = c.p.getParent()
    n = deleteChildren(p, cond, dtor=dtor)
    g.es('Deleted %d nodes' % n)
    c.redraw(p)

def cmd_PurgeVanishedFilesRecursive(c):
    """Remove files no longer present, i.e. "*filename*" entries."""
    p = c.p
    n = deleteDescendents(p, cond, dtor=dtor)
    g.es('Deleted at least %d nodes' % n)
    c.redraw(p)

def cmd_PurgeUnloadedFilesHere(c):
    """Remove files never loaded, i.e. no kind of @file node."""
    p = c.p.getParent()
    n = deleteChildren(p, condunl, dtor=dtor)
    g.es('Deleted %d nodes' % n)
    c.redraw(p)

def cmd_PurgeUnloadedFilesRecursive(c):
    """Remove files never loaded, i.e. no kind of @file node."""
    p = c.p
    n = deleteDescendents(p, condunl, dtor=dtor)
    g.es('Deleted at least %d nodes' % n)
    c.redraw(p)

def deleteChildren(p, cond, dtor=None):

    cull = [child.copy() for child in p.children() if cond(child)]

    if cull:
        cull.reverse()
        for child in cull:
            if dtor:
                dtor(child)
            else:
                child.doDelete()
        return len(cull)

    return 0

def deleteDescendents(p, cond, dtor=None, descendAnyway=False, _culls=0):

    childs = [child.copy() for child in p.children()]
    childs.reverse()
    for child in childs:
        if descendAnyway or not cond(child):
            _culls += deleteDescendents(child, cond, dtor=dtor,
                                        descendAnyway=descendAnyway)
        if cond(child):
            _culls += 1
            if dtor:
                dtor(child)
            else:
                child.doDelete()
    return _culls

#@+node:tbrown.20080619080950.14: ** testing
#@+node:tbrown.20080619080950.15: *3* makeTestHierachy
files="""
a/
a/a/
a/a/1
a/a/2
a/a/3
a/b/
a/c/
a/c/1
a/c/2
a/c/3
b/
c/
1
2
3
"""
import os, shutil
def makeTestHierachy(c):

    shutil.rmtree('active_directory_test')
    for i in files.strip().split():
        f = 'active_directory_test/'+i
        if f.endswith('/'):
            os.makedirs(os.path.normpath(f))
        else:
            file(os.path.normpath(f),'w')

def deleteTestHierachy(c):

    for i in files.strip().split():
        f = 'active_directory_test/'+i
        if 'c/' in f and f.endswith('/'):
            shutil.rmtree(os.path.normpath(f))
        elif '2' in f:
            try: os.remove(os.path.normpath(f))
            except: pass  # already gone

if testing:
    cmd_MakeTestHierachy = makeTestHierachy
    cmd_DeleteFromTestHierachy = deleteTestHierachy
#@-others
#@-leo
