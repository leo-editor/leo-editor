# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20050301083306: * @file mod_read_dir_outline.py
#@@first

#@+<< docstring >>
#@+node:ekr.20050301084207: ** << docstring >>
''' Allows Leo to read a complete directory tree into a Leo outline. Converts
directories into headlines and puts the list of file names into bodies.

Ce plug-in permet de traduire l'arborescence d'un répertoire en une arborescence
Leo : Chaque dossier est converti en noeud dans Leo ; son nom est placé dans
l'entête du noeud et chaque nom de fichier qu'il contient est listé dans son
contenu.

Feedback on this plugin can be sent to::

    Frédéric Momméja
    <frederic [point] mommeja [at] laposte [point] net>

'''
#@-<< docstring >>

#@@language python
#@@tabwidth -4

import leo.core.leoGlobals as g
import os

__version__ = '2.0'
#@+<< version history >>
#@+node:ekr.20050301083306.3: ** << version history >>
#@@killcolor

#@+at
# 
# 1.3 Original version by Frédéric Momméja
# 
# 1.4 EKR:  Changes for 4.3 code base and new plugins style.
# 
#     - Created typical init and onCreate functions.
#     - Created language global.
#     - Changed true/false to True/False.
#     - Used g.os_path functions to support Unicode properly.
#     - Added '@first # -*- coding: utf-8 -*-' to suppress deprecation warning.
# 1.5 EKR:
#     - use g.importExtension to import tkFileDialog.
#     - Redraw the screen only once (in readDir instead of importDir).
# 1.6 EKR:
#     - Changed 'new_c' logic to 'c' logic.
#     - Added init function.
# 2.0 EKR: now gui independent.
#@-<< version history >>

language = 'english' # Anything except 'french' uses english.

#@+others
#@+node:ekr.20050301083306.4: ** init
def init ():

    # This plugin is now gui independent.
    g.registerHandler(("new2","menu2"), onCreate)
    g.plugin_signon(__name__)

    return True
#@+node:ekr.20050301083306.5: ** onCreate
def onCreate (tag, keywords):

    c = keywords.get('c')
    cc = controller(c)

    menu = c.frame.menu.getMenu('Outline')

    if language == 'french':
        mess1 = "Lit un Répertoire..."
    else:
        mess1 = "Read a Directory..."

    table = (
        ("-", None, None),
        (mess1, "Shift+Ctrl+Alt+D",cc.readDir))

    c.frame.menu.createMenuEntries(menu,table,dynamicMenu=True)
#@+node:ekr.20050301083306.6: ** class controller
class controller:

    #@+others
    #@+node:ekr.20050301083306.7: *3* ctor
    def __init__ (self,c):

        self.c = c
    #@+node:ekr.20050301083306.8: *3* readDir
    def readDir (self,event=None):

        # fr - Modifier pour adapter à votre environnement
        # en - Change it to select the starting browsing directory
        c = self.c ; startdir = "/home/"

        if language == 'french':
            titledialog = "Choisir le répertoire..."
        else:
            titledialog = "Please, select a directory..."

        dirName = g.app.gui.runOpenDirectoryDialog(
            title=titledialog,
            startdir=startdir,
        )

        if dirName:
            g.es(dirName)
            compteurglobal = self.importDir(dirName,compteurglobal=0)
            c.selectPosition(c.p)
            c.redraw_now()
            if language == 'french':
                g.es(str(compteurglobal)+" fichiers traités.")
            else:
                g.es(str(compteurglobal)+" files outlined.")
    #@+node:ekr.20050301083306.10: *3* importDir
    def importDir (self,dir,compteurglobal):

        """ La routine récursive de lecture des fichiers """

        if not g.os_path_exists(dir):
            if language == 'french':
                g.es("Ce répertoire n'existe pas: %s" + dir)
            else:
                g.es("No such Directory: %s" + dir)
            return compteurglobal

        head,tail = g.os_path_split(dir)
        c = self.c ; current = c.p
        try:
            #ici, on liste le contenu du répertoire
            body=""
            #@+<< listdir >>
            #@+node:ekr.20050301083306.11: *4* << listdir >>
            try:
                fichiers = os.listdir(dir)
                dossiers = []
                for f in fichiers:
                    # mettre ici le code de création des noeuds
                    path = g.os_path_join(dir,f)
                    # est-ce un fichier ?
                    if g.os_path_isfile(path):
                        body += (f+"\n")
                    else:
                        # c'est alors un répertoire
                        dossiers.append(path)
                    compteurglobal += 1
            except Exception:
                if language == 'french':
                    g.es("erreur dans listage fichiers...")
                else:
                    g.es("os.listdir error...")
                g.es_exception()
            #@-<< listdir >>
            p = c.importCommands.createHeadline(current,body,tail)
            c.selectPosition(p)
            if len(dossiers) > 0:
                for d in dossiers:
                    compteurglobal = self.importDir(d,compteurglobal)
            c.setChanged(True)
            #sélectionne le noeud parent
            c.selectPosition(current)
        except:
            if language == 'french':
                g.es("erreur d'insertion de noeud...")
            else:
                g.es("error while creating node...")
            g.es_exception()

        return compteurglobal
    #@-others
#@-others
#@-leo
