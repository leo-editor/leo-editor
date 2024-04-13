#@+leo-ver=5-thin
#@+node:tbrown.20080613095157.2: * @file ../plugins/active_path.py
#@+<< docstring >>
#@+node:tbrown.20080613095157.3: ** << docstring >> (active_path)
r"""Synchronizes \@path nodes with folders.

If a node is named '\@path *<path_to_folder>*', the content (file and folder
names) of the folder and the children of that node will synchronized whenever
you double-click the node.

For files not previously seen in a folder a new node will appear on top of the
children list (with a mark).

Folders appear in the list as /foldername/. If you double click on the folder
node, it will have children added to it based on the contents of the folder on
disk. These folders have the '@path' directive as the first line of their body
text.

When files are deleted from the folder and the list is updated by double
clicking the files will appear in the list as *filename* (or */foldername/*).

You can describe files and directories in the body of the nodes.

You can organize files and directories with organizer nodes, an organizer node
name cannot contain with '/'.

Files and folders can be created by entering a node with the required name as
its headline (must start and/or end with "/" for a folder) and then double
clicking on the node.

\@auto nodes can be set up for existing files can be loaded by double clicking
on the node. If you prefer \@shadow or something else use the
"active_path_attype" setting, without the "@".

There are commands on the Plugins active_path submenu:

- show path - show the current path
- set absolute path - changes a node "/dirname/" to "@path
  /absolute/path/to/dirname".
- purge vanished (recursive) - remove *entries*
- update recursive - recursive load of directories, use with caution on large
  file systems
- pick dir - select a folder interactively to make a new top level @path node
- mark-content - mark outline content in the @path tree, as opposed to
  filesystem content. Useful if you want to delete the @path tree to check for
  content not on the filesystem first

If you want to use an input other than double clicking a node set
active_path_event to a value like 'hypercclick1' or 'headrclick1'.

There are @settings for ignoring directory entries and automatically loading
files. ``re.search`` is used, rather than ``re.match``, so patterns need only
match part of the filename, not the whole filename.

The body of the @setting ``@data active_path_ignore`` is a list of regex
patterns, one per line. Directory entries matching any pattern in the list will
be ignored. The names of directories used for matching will have forward slashes
around them ('/dirname/'), so patterns can use this to distinguish between
directories and files.

The body of the @setting ``@data active_path_autoload`` is a list of regex
patterns, one per line. File entries matching any pattern in the list will be
loaded automatically. This works only with files, not directories (but you can
load directories recursively anyway).

Autoloading can be toggled with `active-path-toggle-autoload`, autoloading
defaults to initially on unless @bool active-path-do-autoload = False.

Set ``@bool active_path_load_docstring = True`` to have active_path load the
docstring of .py files automatically. These nodes start with the special
string::

    @language rest # AUTOLOADED DOCSTRING

which must be left intact if you want active path to be able to double-click
load the file later.

\@float active_path_timeout_seconds (default 10.) controls the maximum time
active_path will spend on a recursive operation.

\@int active_path_max_size (default 1000000) controls the maximum size file
active_path will open without query.

Per Folder file/folder inclusion and exclusion by adding flags to the body of an
active path folder (either ``@`` or ``/*/``), can include multiple ``inc=`` and
``exc=`` flags:

- ``excdirs`` - excludes all directories
- ``excfiles`` - excludes all files
- ``inc=`` - a single item or comma separated list of strings to include in the
  list of files/folders
- ``exc=`` - a single item or comma separated list of strings to exclude in the
  list of files/folders
- ``re`` - search using regular expressions (otherwise a case-sensitive 'in'
  comparison)

active_path is a rewrite of the at_directory plugin to use \@path directives
(which influence \@auto and other \@file type directives), and to handle
sub-folders more automatically.

"""
#@-<< docstring >>
#@+<< imports >>
#@+node:ekr.20140612210500.17669: ** << imports >>
import ast  # for docstring loading
import os
import re
import shutil
import time  # for recursion bailout
from leo.core import leoGlobals as g
from leo.core import leoPlugins  # uses leoPlugins.TryNext

#@-<< imports >>
testing = False
#@+others
#@+node:tbrown.20091128094521.15048: ** init (active_path.py)
def init():
    """Return True if the plugin has loaded successfully."""
    g.registerHandler('after-create-leo-frame', attachToCommander)
    g.act_on_node.add(active_path_act_on_node, priority=90)
    g.plugin_signon(__name__)
    if g.app.gui.guiName() == "qt":
        g.tree_popup_handlers.append(popup_entry)
    return True
#@+node:tbrown.20091128094521.15047: ** attachToCommander
# defer binding event until c exists
def attachToCommander(t, k):

    c = k.get('c')
    event = c.config.getString('active-path-event') or "headdclick1"
    g.registerHandler(event, lambda t, k: onSelect(t, k))

    # not using a proper class, so
    c.__active_path = {'ignore': [], 'autoload': [],
        'do_autoload': c.config.getBool('active-path-do-autoload', default=True)}

    if c.config.getData('active_path_ignore'):
        c.__active_path['ignore'] = [re.compile(i, re.IGNORECASE)
            for i in c.config.getData('active_path_ignore')]

    if c.config.getData('active_path_autoload'):
        c.__active_path['autoload'] = [re.compile(i, re.IGNORECASE)
            for i in c.config.getData('active_path_autoload')]

    if c.config.getBool('active-path-load-docstring'):
        c.__active_path['load_docstring'] = True
    else:
        c.__active_path['load_docstring'] = False

    if c.config.getFloat('active-path-timeout-seconds'):
        c.__active_path['timeout'] = c.config.getFloat('active-path-timeout-seconds')
    else:
        c.__active_path['timeout'] = 10.

    if c.config.getInt('active-path-max-size'):
        c.__active_path['max_size'] = c.config.getInt('active-path-max-size')
    else:
        c.__active_path['max_size'] = 1000000

    c.__active_path['DS_SENTINEL'] = "@language rest # AUTOLOADED DOCSTRING"
#@+node:tbrown.20091128094521.15042: ** popup_entry (active_path)
def popup_entry(c, p, menu):
    """Populate the Path submenu of the popup."""
    pathmenu = menu.addMenu("Path")
    d = g.global_commands_dict
    for key in d:
        if key.startswith('active-path'):
            a = pathmenu.addAction(key)
            command = d.get(key)

            def active_path_wrapper(aBool, command=command, c=c):
                event = {'c': c}
                command(event)

            a.triggered.connect(active_path_wrapper)
#@+node:tbrown.20091128094521.15037: ** isDirNode
def isDirNode(p):

    return (
        p.h.startswith('@path ') or
        #  '/foo/' form *assumes* @path in body
        (not p.h.strip().startswith('@') and p.h.strip().endswith('/')) or
        p.h.strip().startswith('/')
        )
#@+node:tbrown.20091128094521.15039: ** isFileNode
def isFileNode(p):
    """really isEligibleToBecomeAFileNode"""
    return (
        not p.h.strip().startswith('@') and not p.hasChildren() and
        not isDirNode(p) and isDirNode(p.parent()) and
        (not p.b.strip() or
        # p.b.startswith(c.__active_path['DS_SENTINEL']
        p.b.startswith("@language rest # AUTOLOADED DOCSTRING")  # no c!
      ))
#@+node:jlunz.20150611151435.1: ** inAny
def inAny(item, group, regEx=False):
    """ Helper function to check if word from list is in a string """
    if regEx:
        return any(re.search(word, item) for word in group)
    return any(word in item for word in group)
#@+node:jlunz.20150611151003.1: ** checkIncExc
def checkIncExc(item, inc, exc, regEx):
    """ Primary logic to check if an item is in either the include or exclude list """
    if inc and not exc:
        return inAny(item, inc, regEx)
    if exc and not inc:
        return not inAny(item, exc, regEx)
    return True
#@+node:tbrown.20091129085043.9329: ** inReList
def inReList(txt, lst):
    for pat in lst:
        if pat.search(txt):
            return True
    return False
#@+node:tbrown.20091128094521.15040: ** subDir
def subDir(d, p):

    if p.h.strip().startswith('@path'):
        p = p.h.split(None, 1)
        if len(p) != 2:
            return None
        p = p[1]

    elif p.b.strip().startswith('@path'):
        p = p.b.split('\n', 1)[0].split(None, 1)
        if len(p) != 2:
            return None
        p = p[1]

    else:
        p = p.h.strip(' /')

    return os.path.join(d, p)
#@+node:tbrown.20080613095157.4: ** onSelect
def onSelect(tag, keywords):
    """Determine if a file or directory node was clicked, and the path"""
    c = keywords.get('c') or keywords.get('new_c')
    if not c:
        return None
    p = keywords.get("p")
    p.expand()
    pos = p.copy()
    path = getPath(c, p)
    if path and sync_node_to_folder(c, pos, path):
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
    if not isDirNode(p):  # add file name
        h = p.h.split(None, 1)
        if h[0].startswith('@') and len(h) == 2:
            path = os.path.join(path, h[1])
        else:
            path = os.path.join(path, p.h.strip())
    return path
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
        if not isDirNode(n) and not n.h.startswith('@'):
            for i in flattenOrganizers(n):
                yield i
#@+node:tbrown.20080613095157.6: ** sync_node_to_folder
def sync_node_to_folder(c, parent, d, updateOnly=False, recurse=False):
    """Decide whether we're opening or creating a file or a folder"""

    if (
        not updateOnly and
        not recurse and
        isDirNode(parent) and not parent.h.strip().startswith('@path') and
        not parent.b.strip().startswith('@path')
    ):
        createDir(c, parent, d)
        return True  # even if it didn't happen, else get stuck in edit mode w/o focus

    if os.path.isdir(d):
        if (isDirNode(parent) and
            (not updateOnly or recurse or parent.hasChildren())
        ):
            # no '/' or @path implies organizer
            openDir(c, parent, d)
            return True

    if updateOnly:
        return False

    if os.path.isfile(d) and isFileNode(parent):
        openFile(c, parent, d)
        return True

    if isFileNode(parent):
        createFile(c, parent, d)
        return True  # even if it didn't happen, else get stuck in edit mode w/o focus

    return False
#@+node:tbrown.20080613095157.7: ** createDir
def createDir(c, parent, d):
    """Ask if we should create a new folder"""
    newd = parent.h.strip(' /')
    ok = g.app.gui.runAskYesNoDialog(c, 'Create folder?',
        'Create folder ' + newd + '?')
    if ok == 'no':
        return False
    parent.h = '/' + newd + '/'
    if parent.b.strip():
        parent.b = '@path ' + newd + '\n' + parent.b
    else:
        parent.b = '@path ' + newd

    os.mkdir(os.path.join(d, newd))
    return True
#@+node:tbrown.20080613095157.8: ** createFile
def createFile(c, parent, d):
    """Ask if we should create a new file"""
    directory = os.path.dirname(d)
    if not os.path.isdir(directory):
        g.error('Create parent directories first')
        return False

    d = os.path.basename(d)
    atType = c.config.getString('active-path-attype') or 'auto'
    ok = g.app.gui.runAskYesNoDialog(c, 'Create / load file?',
        'Create file @' + atType + ' ' + d + '?')
    if ok == 'no':
        return False
    parent.h = '@' + atType + ' ' + d
    c.bodyWantsFocus()
    return True
#@+node:tbrown.20080613095157.9: ** openFile
def openFile(c, parent, d, autoload=False):
    """Open an existing file"""

    path = getPath(c, parent)

    if not os.path.isfile(path):
        return

    oversize = os.stat(path).st_size > c.__active_path['max_size']

    if not autoload:
        junk, ext = g.os_path_splitext(path)
        extensions = c.config.getData('active_path_bin_open') or []  # #2103
        binary_open = ext in extensions
        if not binary_open:
            try:
                start = open(path).read(100)
                for i in start:
                    if ord(i) == 0:
                        binary_open = True
                        break
            except Exception:
                binary_open = True

        if binary_open:
            g.es('Treating file as binary')
            g.handleUrl('file://' + path, c=c)
            # if not query(c, "File may be binary, continue?"):
            #     return
            return

        if oversize:
            if not query(c, "File size greater than %d bytes, continue?" %
              c.__active_path['max_size']):
                return

    if autoload and oversize:
        return

    atType = c.config.getString('active-path-attype') or 'auto'
    parent.h = '@' + atType + ' ' + parent.h
    c.selectPosition(parent)
    if atType == 'asis':
        parent.b = open(d).read()
    else:
        c.refreshFromDisk()
    c.bodyWantsFocus()
#@+node:tbrown.20080613095157.10: ** openDir
def openDir(c, parent, d):
    """
    Expand / refresh an existing folder

    Note: With the addition of per folder inclusion/exclusion a check is done
    against both the current list of nodes and against the files/folders as
    they exist on the system. This check must be done in both places to keep
    the node list in sync with the file system while respecting the inc/exc
    lists - John Lunzer
    """

    # compare folder content to children
    try:
        path, dirs, files = next(os.walk(d))
    except StopIteration:
        # directory deleted?
        c.setHeadString(parent, '*' + parent.h.strip('*') + '*')
        return

    # parent.expand()  # why?

    oldlist = set()
    toRemove = set()
    newlist = []

    bodySplit = parent.b.splitlines()

    excdirs = False
    excfiles = False
    regEx = False
    if re.search('^excdirs', parent.b, flags=re.MULTILINE):
        excdirs = True
    if re.search('^excfiles', parent.b, flags=re.MULTILINE):
        excfiles = True
    if re.search('^re', parent.b, flags=re.MULTILINE):
        regEx = True

    inc = [line.replace('inc=', '') for line in bodySplit if line.startswith('inc=')]
    exc = [line.replace('exc=', '') for line in bodySplit if line.startswith('exc=')]

    # flatten lists if using comma separations
    inc = [item for line in inc for item in line.strip(' ').split(',')]
    exc = [item for line in exc for item in line.strip(' ').split(',')]

    # get children info
    for p in flattenOrganizers(parent):
        entry = p.h.strip('/*')
        if entry.startswith('@'):  # remove only the @part
            directive = entry.split(None, 1)
            if len(directive) > 1:
                entry = entry[len(directive[0]) :].strip()
        # find existing inc/exc nodes to remove
        # using p.h allows for example exc=/ to remove all directories
        if (
            not checkIncExc(p.h, inc, exc, regEx)
            or (excdirs and entry in dirs)
            or (excfiles and entry in files)
        ):
            toRemove.add(p.h)  #must not strip '/', so nodes can be removed
        else:
            oldlist.add(entry)

    # remove existing found inc/exc nodes
    for headline in toRemove:
        found = g.findNodeInChildren(c, parent, headline)
        if found:
            found.doDelete()

    # dirs trimmed by toRemove to remove redundant checks
    for d2 in set(dirs) - set([h.strip('/') for h in toRemove]):
        if d2 in oldlist:
            oldlist.discard(d2)
        else:
            if checkIncExc(d2,
                           [i.strip('/') for i in inc],
                           [e.strip('/') for e in exc],
                           regEx) and not excdirs:
                newlist.append('/' + d2 + '/')

    # files trimmed by toRemove, retains original functionality of plugin
    for f in set(files) - toRemove:
        if f in oldlist:
            oldlist.discard(f)
        else:
            if checkIncExc(f, inc, exc, regEx) and not excfiles:
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
        c.setChanged()
        p.h = name
        if name.startswith('/'):
            # sufficient test of dirness as we created newlist
            p.b = '@path ' + name.strip('/')
        elif (c.__active_path['do_autoload'] and
              inReList(name, c.__active_path['autoload'])):
            openFile(c, p, os.path.join(d, p.h), autoload=True)
        elif (c.__active_path['do_autoload'] and
              c.__active_path['load_docstring'] and
              name.lower().endswith(".py")):
            # do_autoload suppresses doc string loading because turning
            # autoload off is supposed to address situations where autoloading
            # causes problems, so don't still do some form of autoloading
            p.b = c.__active_path['DS_SENTINEL'] + "\n\n" + loadDocstring(os.path.join(d, p.h))
        p.setMarked()
        p.contract()

    if ignored:
        g.es('Ignored %d files in directory' % ignored)

    # warn / mark for orphan oldlist
    for p in flattenOrganizers(parent):
        h = p.h.strip('/*')  # strip / and *
        if (h not in oldlist or
            (p.hasChildren() and not isDirNode(p))
        ):  # clears bogus '*' marks
            nh = p.h.strip('*')  # strip only *
        else:
            nh = '*' + p.h.strip('*') + '*'
            if isDirNode(p):
                for orphan in p.subtree():
                    c.setHeadString(orphan, '*' + orphan.h.strip('*') + '*')
        if p.h != nh:  # don't dirty node unless we must
            p.h = nh

    c.selectPosition(parent)
#@+node:tbrown.20100304090709.31081: ** loadDocstring
def loadDocstring(file_path):
    try:
        src = open(file_path).read()
        src = src.replace('\r\n', '\n').replace('\r', '\n') + '\n'
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
        title='Really?',
        message=s)

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
#@+node:ville.20090223183051.1: ** cmd_ActOnNode (active_path.py)
@g.command('active-path-act-on-node')
def cmd_ActOnNode(event, p=None):
    """ act_on_node handler for active_path.py
    """
    c = event.get('c')
    # implementation mostly copied from onSelect
    if p is None:
        p = c.currentPosition()
    pos = p.copy()
    path = getPath(c, p)
    if path:
        sync_node_to_folder(c, pos, path)
        c.redraw()
        return True
    raise leoPlugins.TryNext

active_path_act_on_node = cmd_ActOnNode
#@+node:tbrown.20111207143354.19381: ** cmd_MakeDir (active_path.py)
@g.command('active-path-make-dir')
def cmd_MakeDir(event):
    c = event.get('c')
    txt = g.app.gui.runAskOkCancelStringDialog(
        c, 'Directory name', 'Directory name')
    if txt:
        nd = c.p.insertAsNthChild(0)
        nd.h = '/' + txt.strip('/') + '/'
        nd.b = '@path %s\n' % txt
        c.selectPosition(nd)
        c.redraw()
    g.es("Path will be created if a file is saved on it")
#@+node:tbrown.20080616153649.2: ** cmd_ShowCurrentPath (active_path.py)
@g.command('active-path-show-current-path')
def cmd_ShowCurrentPath(event):
    """Just show the path to the current file/directory node in the log pane."""
    c = event.get('c')
    g.es(getPath(c, c.p))
#@+node:tbrown.20100401100336.13608: ** cmd_LoadRecursive (active_path.py)
@g.command('active-path-load-recursive')
def cmd_LoadRecursive(event):
    """Recursive update, with expansions."""
    g.trace(event, g.callers())
    c = event.get('c')
    for s in run_recursive(c):
        path = getPath(c, s)
        if path:
            sync_node_to_folder(c, s, path, updateOnly=True, recurse=True)
#@+node:tbrown.20080619080950.16: ** cmd_UpdateRecursive (active_path.py)
@g.command('active-path-update-recursive')
def cmd_UpdateRecursive(event):
    """Recursive update, no new expansions."""
    c = event.get('c')
    for s in run_recursive(c):
        path = getPath(c, s)
        if path:
            sync_node_to_folder(c, s, path, updateOnly=True)
#@+node:tbrown.20091214212801.13475: ** cmd_SetNodeToAbsolutePathRecursive (active_path.py)
@g.command('active-path-set-node-to-absolute-path-recursive')
def cmd_SetNodeToAbsolutePathRecursive(event):
    """Change "/dirname/" to "@path /absolute/path/to/dirname", recursively"""
    c = event.get('c')
    for s in run_recursive(c):
        cmd_SetNodeToAbsolutePath(event, p=s)
#@+node:tbrown.20080616153649.5: ** cmd_SetNodeToAbsolutePath (active_path.py)
@g.command('active-path-set-node-to-absolute-path')
def cmd_SetNodeToAbsolutePath(event, p=None):
    """Change "/dirname/" to "@path /absolute/path/to/dirname"."""
    c = event.get('c')
    if not p:
        p = c.p
    path = getPath(c, p)
    d = p.h.split(None, 1)
    if len(d) > 1 and d[0].startswith('@'):
        type_ = d[0] + " "
    elif isDirNode(p):
        type_ = "@path "
        p.b = '# path Created from node "%s"\n\n' % p.h + p.b
    else:
        type_ = "@auto "
    p.h = type_ + path
#@+node:tbrown.20080618141617.879: ** cmd_PurgeVanishedFiles (active_path.py)
def cond(p):
    return p.h.startswith('*') and p.h.endswith('*')

def condunl(p):
    return (
        isFileNode(p) and not p.b.strip() or
        isDirNode(p) and not p.hasChildren())

def dtor(p):
    # g.es(p.h)
    p.doDelete()

@g.command('active-path-purge-vanished-files-here')
def cmd_PurgeVanishedFilesHere(event):
    """Remove files no longer present, i.e. "*filename*" entries."""
    c = event.get('c')
    p = c.p.getParent()
    n = deleteChildren(p, cond, dtor=dtor)
    g.es('Deleted %d nodes' % n)
    c.redraw(p)

@g.command('active-path-purge-vanished-files-recursive')
def cmd_PurgeVanishedFilesRecursive(event):
    """Remove files no longer present, i.e. "*filename*" entries."""
    c = event.get('c')
    p = c.p
    n = deleteDescendents(p, cond, dtor=dtor)
    g.es('Deleted at least %d nodes' % n)
    c.redraw(p)

@g.command('active-path-purge-unloaded-files-here')
def cmd_PurgeUnloadedFilesHere(event):
    """Remove files never loaded, i.e. no kind of @file node."""
    c = event.get('c')
    p = c.p.getParent()
    n = deleteChildren(p, condunl, dtor=dtor)
    g.es('Deleted %d nodes' % n)
    c.redraw(p)

@g.command('active-path-purge-unloaded-files-recursive')
def cmd_PurgeUnloadedFilesRecursive(event):
    """Remove files never loaded, i.e. no kind of @file node."""
    c = event.get('c')
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

#@+node:tbrown.20140308075026.27803: ** cmd_PickDir (active_path.py)
@g.command('active-path-pick-dir')
def cmd_PickDir(event):
    """cmd_PickDir - Show user a folder picker to create
    """
    c = event.get('c')
    p = c.p
    aList = g.get_directives_dict_list(p)
    path = c.scanAtPathDirectives(aList)
    if p.h.startswith('@'):  # see if it's a @<file> node of some sort
        nodepath = p.h.split(None, 1)[-1]
        nodepath = g.os_path_join(path, nodepath)
        if not g.os_path_isdir(nodepath):  # remove filename
            nodepath = g.os_path_dirname(nodepath)
        if g.os_path_isdir(nodepath):  # append if it's a directory
            path = nodepath
    ocwd = os.getcwd()
    try:
        os.chdir(path)
    except OSError:
        g.es("Couldn't find path %s" % path)
    dir_ = g.app.gui.runOpenDirectoryDialog("Pick a folder", "Pick a folder")
    os.chdir(ocwd)
    if not dir_:
        g.es("No folder selected")
        return
    nd = c.p.insertAfter()
    nd.h = "@path %s" % dir_
    c.redraw()
#@+node:tbnorth.20160122134156.1: ** cmd_MarkContent (active_path.py)
@g.command('active-path-mark-content')
def cmd_MarkContent(event):
    """cmd_MarkContent - mark nodes in @path sub-tree with non-filesystem content

    i.e. not organizer nodes (no body), subdirs (body starts with @path)
    vanished file placeholders, or @<file> nodes.
    """
    c = event.get('c')
    p = c.p

    while not p.h.startswith("@path "):
        p.moveToParent()
        if not p:
            g.es("Not in a @path tree")
            return
    c.unmarkAll()
    def find_content(nd, count):
        # pylint: disable=len-as-condition
        if nd.isAnyAtFileNode():
            return
        content = True
        if len(nd.b.strip()) == 0:
            content = False
        elif len(nd.b.strip().split('\n')) == 1 and nd.b.startswith('@path '):
            content = False
        if content:
            nd.setMarked()
            count[0] += 1
        for child in nd.children():
            find_content(child, count)
    count = [0]
    find_content(p, count)
    g.es("%d content nodes marked" % count[0])
    if count[0]:
        c.redraw()
#@+node:tbnorth.20160224113800.1: ** cmd_ToggleAutoLoad (active_path.py)
@g.command('active-path-toggle-autoload')
def cmd_ToggleAutoLoad(event):
    """cmd_ToggleAutoLoad - toggle autoloading behavior
    """
    c = event.get('c')
    c.__active_path['do_autoload'] = not c.__active_path['do_autoload']
    g.es("Autoload: %s" % c.__active_path['do_autoload'])

#@+node:tbrown.20080619080950.14: ** testing
#@+node:tbrown.20080619080950.15: *3* makeTestHierachy
files = """
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
def makeTestHierachy(c):

    shutil.rmtree('active_directory_test')
    for i in files.strip().split():
        f = 'active_directory_test/' + i
        if f.endswith('/'):
            os.makedirs(os.path.normpath(f))
        else:
            open(os.path.normpath(f), 'w')

def deleteTestHierachy(c):

    for i in files.strip().split():
        f = 'active_directory_test/' + i
        if 'c/' in f and f.endswith('/'):
            shutil.rmtree(os.path.normpath(f))
        elif '2' in f:
            try:
                os.remove(os.path.normpath(f))
            except Exception:
                pass  # already gone

if testing:
    cmd_MakeTestHierachy = makeTestHierachy
    cmd_DeleteFromTestHierachy = deleteTestHierachy
#@-others
#@@language python
#@@tabwidth -4
#@-leo
