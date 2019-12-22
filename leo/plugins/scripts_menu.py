#@+leo-ver=5-thin
#@+node:EKR.20040517080555.36: * @file scripts_menu.py
"""Creates a Scripts menu for LeoPy.leo."""

# The new Execute Script command seems much safer and more convenient.

#@@language python
#@@tabwidth -4

import leo.core.leoGlobals as g
import glob
import os

__version__ = "1.5"

#@+others
#@+node:ekr.20111104210837.9694: **  init
def init():
    '''Return True if the plugin has loaded successfully.'''
    # Ok for unit testing: creates menu.
    g.registerHandler("create-optional-menus",create_scripts_menu)
    g.plugin_signon(__name__)
    return True
#@+node:EKR.20040517080555.37: ** create_scripts_menu & helpers
def create_scripts_menu (tag,keywords):
    """
    Populate a new Scripts menu with all .py files
    in leo/scripts and subdirectories.
    """
    c = keywords.get("c")
    if not c:
        return
    # finalize = g.os_path_finalize
    join = g.os_path_finalize_join
    path = join(g.app.loadDir,"..","scripts")
    if not os.path.exists(path):
        return
    # Get all files and directories.
    entries = glob.glob(join(path, "*"))
    # Get all top-level modules.
    top_mods = glob.glob(join(path, "*.py"))
    top_mods = [z for z in top_mods
        if not z.endswith('__init__.py')]
    # Get all inner modules.
    dirs = [f for f in entries if os.path.isdir(f)]
    inner_mods = [glob.glob(join(z, "*.py")) for z in dirs]
    inner_mods = [z for z in inner_mods if z]
    # g.printObj(top_mods, tag='top_mods')
    # g.printObj(inner_mods, tag='inner_mods')
    if not top_mods and not inner_mods:
        return
    # Create the top-level scripts menu.
    scriptsMenu = c.frame.menu.createNewMenu("&Scripts")
    create_top_level_scripts(c, scriptsMenu, top_mods)
    for directory in dirs:
        files = glob.glob(join(directory, "*.py"))
        if files:
            create_inner_scripts(c, directory, files)
#@+node:EKR.20040517080555.40: *3* create_inner_scripts
def create_inner_scripts(c, directory, files):
    """Create a submenu of the Scripts menu."""
    name = os.path.join("scripts", g.shortFileName(directory))
    menu = c.frame.menu.createNewMenu(name,"&Scripts")
    
    # Populate the submenu.
    table = []
    for filename in files:
        if filename.endswith('__init__.py'):
            continue
        prefix = g.os_path_finalize_join(g.app.loadDir, "..", "..")
        name = filename[len(prefix)+1:-3]
        name = name.replace('\\','.').replace('/','.')
        g.trace(name)
        
        def inner_script_callback(event=None, name=name):
            g.import_module(name)

        table.append((name, None, inner_script_callback))
    c.frame.menu.createMenuEntries(menu, table, dynamicMenu=True)
#@+node:EKR.20040517080555.39: *3* create_top_level_scripts
def create_top_level_scripts(c, scriptsMenu, top_scripts):
 
    table = []
    for script in sorted(top_scripts):
        name = g.shortFileName(script)[:-3]

        def script_callback(event=None, name=name):
            g.import_module(f"leo.scripts.{name}")

        table.append((name, None, script_callback))
    c.frame.menu.createMenuEntries(
        scriptsMenu, table, dynamicMenu=True)
#@-others
#@-leo
