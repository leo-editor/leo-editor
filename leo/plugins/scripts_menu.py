#@+leo-ver=4-thin
#@+node:EKR.20040517080555.36:@thin scripts_menu.py
"""Create a Scripts menu for LeoPy.leo"""

# The new Execute Script command seems much safer and more convenient.

#@@language python
#@@tabwidth -4

#@<< imports >>
#@+node:ekr.20050111115429:<< imports >>

import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins

import glob
import os
#@nonl
#@-node:ekr.20050111115429:<< imports >>
#@nl

__version__ = "1.4"

#@+others
#@+node:EKR.20040517080555.37:createScriptsMenu
def createScriptsMenu (tag,keywords):

    c = keywords.get("c")
    path = os.path.join(g.app.loadDir,"..","scripts")

    if os.path.exists(path):

        # Create lists of scripts and subdirectories.
        entries = glob.glob(os.path.join(path,"*"))
        top_scripts = glob.glob(os.path.join(path,"*.py"))
        dirs = [f for f in entries if os.path.isdir(f)]
        #@        << Return if no scripts exist anywhere >>
        #@+node:EKR.20040517080555.38:<< Return if no scripts exist anywhere >>
        if not top_scripts:
            found = False
            for dir in dirs:
                scripts = glob.glob(os.path.join(dir,"*.py"))
                if scripts:
                    found = True ; break
            if not found:
                return
        #@-node:EKR.20040517080555.38:<< Return if no scripts exist anywhere >>
        #@nl

        scriptsMenu = c.frame.menu.createNewMenu("&Scripts")
        table = []
        #@        << Create top-level entries for every script in top_scripts >>
        #@+node:EKR.20040517080555.39:<< Create top-level entries for every script in top_scripts >>
        table = []
        top_scripts.sort()
        for script in top_scripts:
            name = g.shortFileName(script)
            def doScript(event=None,name=name):
                g.executeScript(name)
            table.append((name,None,doScript),)

        c.frame.menu.createMenuEntries(scriptsMenu, table,dynamicMenu=True)
        #@-node:EKR.20040517080555.39:<< Create top-level entries for every script in top_scripts >>
        #@nl
        for dir in dirs:
            files = glob.glob(os.path.join(dir,"*.py"))
            if files:
                #@                << Create a submenu for dir containing each file in files >>
                #@+node:EKR.20040517080555.40:<< Create a submenu for dir containing each file in files >>
                # Create the submenu.
                name = os.path.join("scripts",g.shortFileName(dir))
                menu = c.frame.menu.createNewMenu(name,"&Scripts")

                # Populate the submenu.
                table = []
                for file in files:
                    name = g.shortFileName(file)
                    def doScript(event=None,name=name):
                        g.executeScript(name)
                    table.append((name,None,doScript),)

                c.frame.menu.createMenuEntries(menu, table,dynamicMenu=True)
                #@nonl
                #@-node:EKR.20040517080555.40:<< Create a submenu for dir containing each file in files >>
                #@nl
#@nonl
#@-node:EKR.20040517080555.37:createScriptsMenu
#@-others

if 1: # Ok for unit testing: creates menu.
    leoPlugins.registerHandler("create-optional-menus",createScriptsMenu)
    g.plugin_signon(__name__)
#@nonl
#@-node:EKR.20040517080555.36:@thin scripts_menu.py
#@-leo
