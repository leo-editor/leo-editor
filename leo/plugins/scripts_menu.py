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
#@+node:ekr.20111104210837.9694: ** init
def init():

    # Ok for unit testing: creates menu.
    g.registerHandler("create-optional-menus",createScriptsMenu)
    g.plugin_signon(__name__)
    return True
#@+node:EKR.20040517080555.37: ** createScriptsMenu
def createScriptsMenu (tag,keywords):

    c = keywords.get("c")
    path = os.path.join(g.app.loadDir,"..","scripts")

    if os.path.exists(path):

        # Create lists of scripts and subdirectories.
        entries = glob.glob(os.path.join(path,"*"))
        top_scripts = glob.glob(os.path.join(path,"*.py"))
        dirs = [f for f in entries if os.path.isdir(f)]
        #@+<< Return if no scripts exist anywhere >>
        #@+node:EKR.20040517080555.38: *3* << Return if no scripts exist anywhere >>
        if not top_scripts:
            found = False
            for dir in dirs:
                scripts = glob.glob(os.path.join(dir,"*.py"))
                if scripts:
                    found = True ; break
            if not found:
                return
        #@-<< Return if no scripts exist anywhere >>

        scriptsMenu = c.frame.menu.createNewMenu("&Scripts")
        table = []
        #@+<< Create top-level entries for every script in top_scripts >>
        #@+node:EKR.20040517080555.39: *3* << Create top-level entries for every script in top_scripts >>
        table = []
        top_scripts.sort()
        for script in top_scripts:
            name = g.shortFileName(script)
            def doScript(event=None,name=name):
                g.executeScript(name)
            table.append((name,None,doScript),)

        c.frame.menu.createMenuEntries(scriptsMenu, table,dynamicMenu=True)
        #@-<< Create top-level entries for every script in top_scripts >>
        for dir in dirs:
            files = glob.glob(os.path.join(dir,"*.py"))
            if files:
                #@+<< Create a submenu for dir containing each file in files >>
                #@+node:EKR.20040517080555.40: *3* << Create a submenu for dir containing each file in files >>
                # Create the submenu.
                name = os.path.join("scripts",g.shortFileName(dir))
                menu = c.frame.menu.createNewMenu(name,"&Scripts")

                # Populate the submenu.
                table = []
                for file in files:
                    name = g.shortFileName(file)
                    # EKR: use doScript1 to keep pylint happy.
                    def doScript1(event=None,name=name):
                        g.executeScript(name)
                    table.append((name,None,doScript1),)

                c.frame.menu.createMenuEntries(menu, table,dynamicMenu=True)
                #@-<< Create a submenu for dir containing each file in files >>
#@-others
#@-leo
