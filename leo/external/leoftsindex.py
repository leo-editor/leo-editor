"""
Stand alone GUI free index builder for Leo's full text search system::

  python leoftsindex.py <file1> <file2> <file3>...

If the file name starts with @ it's a assumed to be a simple
text file listing files to be indexed.

If <file> does not contain '#' it's assumed to be a .leo file
to index, and is indexed.

If <file> does contain '#' it's assumed to be a .leo file
containing a list of .leo files to index, with the list in
the node indicated by the UNL after the #, e.g.::

   path/to/myfile.leo#Lists-->List of outlines

In the latter case, if the node identified by the UNL has children,
the list of files to scan is built from the first line of the body
of each child node of the identified node (works well with bookmarks.py).
If the node identified by the UNL does not have children, the
node's body is assumed to be a simple text listing of paths to .leo files).

.. note::
    
    It may be necessary to quote the "file" on the command line,
    as the '#' may be interpreted as a comment delimiter::
        
        python leoftsindex.py "workbook.leo#Links"


"""

import sys
# add folder containing 'leo' folder to path
# sys.path.append("/home/tbrown/Package/leo/bzr/leo.repo/trunk")
import leo.core.leoBridge as leoBridge
import leo.plugins.leofts as leofts

controller = leoBridge.controller(
    gui='nullGui',
    loadPlugins=False,  # True: attempt to load plugins.
    readSettings=False, # True: read standard settings files.
    silent=False,       # True: don't print signon messages.
    verbose=False
)
g = controller.globals()

# list of "files" to process
files = sys.argv[1:]

# set up leofts
leofts.set_leo(g)
g._gnxcache = leofts.GnxCache()
fts = leofts.get_fts()

fn2c = {}  # cache to avoid loading same outline twice
done = set()  # outlines scanned, to avoid repetition repetition

todo = list(files)

while todo:

    item = todo.pop(0)
    
    print ("INDEX: %s"%item)
    
    if '#' in item:
        fn, node = item.split('#', 1)
    else:
        fn, node = item, None
        
    if node:
        c = fn2c.setdefault(fn, controller.openLeoFile(fn))
        found, dummy, p = g.recursiveUNLSearch(node.split('-->'), c)
        if not found:
            print("Could not find '%s'"%item)
            break
        if not p:
            p = c.p
        if p.hasChildren():
            # use file named in first node of each child
            files = [chl.b.strip().split('\n', 1)[0].strip() for chl in p.children()]
        else:
            # use all files listed in body
            files = [i.strip() for i in p.b.strip().split('\n')]

    elif fn.startswith('@'):
        todo.extend(open(fn[1:]).read().strip().split('\n'))
        files = []

    else:
        files = [fn]
        
    for fn in files:
    
        # file names may still have '#' if taken from a node list
        real_name = fn.split('#', 1)[0]
        if real_name in done:
            continue
        done.add(real_name)
        
        if len(files) != 1:
            print (" FILE: %s"%real_name)
    
        c = fn2c.setdefault(real_name, controller.openLeoFile(fn))
        fts.drop_document(real_name)
        fts.index_nodes(c)
