#@+leo-ver=5-thin
#@+node:ekr.20090622063842.5264: * @file projectwizard.py
''' Creates a wizard that creates @auto nodes.

Opens a file dialog and recursively creates @auto & @path nodes from the path
where the selected file is (the selected file itself doesn't matter.)

'''
# Written by VMV.

import leo.core.leoGlobals as g

# Fail gracefully if the gui is not qt.
g.assertUi('qt')
from leo.core.leoQt import QtCore

#@+others
#@+node:ville.20090614224528.8139: ** init
def init ():
    '''Return True if the plugin has loaded successfully.'''
    ok = g.app.gui.guiName() == "qt"
    if ok:
        g.plugin_signon(__name__)
    install_contextmenu_handlers()
    return ok
#@+node:ville.20090614224528.8141: ** auto_walk() and g.command('projectwizard')
def auto_walk(c, directory, parent=None, isroot=True):
    """ source: http://leo.zwiki.org/CreateShadows

    (create @auto files instead)

    """

    from os import listdir
    from os.path import join, abspath, basename, normpath, isfile
    from fnmatch import fnmatch
    import os

    RELATIVE_PATHS = False

    patterns_to_ignore = ['*.pyc', '*.leo', '*.gif', '*.png', '*.jpg', '*.json']
    patterns_to_import = ['*.py','*.c', '*.cpp']
    match = lambda s: any(fnmatch(s, p) for p in patterns_to_ignore)

    is_ignorable = lambda s: any([ s.startswith('.'), match(s) ])

    p = c.currentPosition()

    if not RELATIVE_PATHS: directory = abspath(directory)
    if isroot:
        body = "@path %s" % normpath(directory)
        c.setHeadString(p, body)
    for name in listdir(directory):


        if is_ignorable(name):
            continue

        path = join(directory, name)

        if isfile(path) and not any(fnmatch(name, p) for p in patterns_to_import):           
            continue

        if isfile(path):
            g.es('file:', path)
            headline = '@auto %s' % basename(path)
            if parent:
                node = parent
            else:
                node = p
            child = node.insertAsLastChild()
            child.initHeadString(headline)
        else:
            g.es('dir:', path)
            headline = basename(path)
            body = "@path %s" % normpath(path)
            if parent:
                node = parent
            else:
                node = p
            child = node.insertAsLastChild()
            child.initHeadString(headline)
            child.initBodyString(body)
            auto_walk(c,path, parent=child, isroot=False)

@g.command('project-wizard')
def project_wizard(event):
    """ Launch project wizard """
    import os
    c = event['c']
    table = [("All files","*"),
        ("Python files","*.py"),]

    fname = g.app.gui.runOpenFileDialog(
        title = "Open",filetypes = table,defaultextension = ".leo")

    pth = os.path.dirname(os.path.abspath(fname))

    g.es(pth)
    tgt = c.currentPosition().insertAsLastChild()
    c.selectPosition(tgt)
    auto_walk(c, pth, tgt)
    g.es('Import ok. Do read-at-auto-nodes to parse')
    c.redraw()


#project_wizard()    
#@+node:ville.20090910010217.5230: ** context menu import
def rclick_path_importfile(c,p,menu):
    if not p.h.startswith('@path'):
        return

    def importfiles_rclick_cb():
        aList = g.get_directives_dict_list(p)
        path = c.scanAtPathDirectives(aList)

        table = [("All files","*"),
            ("Python files","*.py"),]
        fnames = g.app.gui.runOpenFileDialog(
            title = "Import files",filetypes = table, 
            defaultextension = '.notused',
            multiple=True)

        print("import files from",path)

    action = menu.addAction("Import files")
    action.connect(action, QtCore.SIGNAL("triggered()"), importfiles_rclick_cb)        

def install_contextmenu_handlers():
    """ Install all the wanted handlers (menu creators) """
    hnd = [rclick_path_importfile]
    g.tree_popup_handlers.extend(hnd)
#@-others
#@-leo
