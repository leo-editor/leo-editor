# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20050301083306: * @thin mod_read_dir_outline.py
#@@first

#@+<< docstring >>
#@+node:ekr.20050301084207: ** << docstring >>
'''This plugin allows Leo to read a complete directory's outline into a Leo's
Outline. Directories are converted into headlines and files names are listed
into the bodies.

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

#@+<< imports >>
#@+node:ekr.20050301083306.2: ** << imports >>
import leo.core.leoGlobals as g

tkFileDialog = g.importExtension('tkFileDialog',pluginName=__name__,verbose=True)

import os
#@-<< imports >>

__version__ = '1.6'
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
#     - Use g.importExtension to import Tkinter
#     - Changed true/false to True/False.
#     - Used g.os_path functions to support Unicode properly.
#     - Added '@first # -*- coding: utf-8 -*-' to suppress deprecation warning.
# 1.5 EKR:
#     - use g.importExtension to import tkFileDialog.
#     - Redraw the screen only once (in readDir instead of importDir).
# 
# 1.6 EKR:
#     - Changed 'new_c' logic to 'c' logic.
#     - Added init function.
#@-<< version history >>

language = 'english' # Anything except 'french' uses english.

#@+others
#@+node:ekr.20050301083306.4: ** init
def init ():

    if tkFileDialog is None: return False

    if g.app.gui is None:
        g.app.createTkGui(__file__)

    ok = g.app.gui.guiName() == "tkinter"

    if ok:
        g.app.pluginsController.registerHandler(("new2","open2"), onCreate)
        g.plugin_signon(__name__)

    return ok
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

        dirName = tkFileDialog.askdirectory(
            title=titledialog,initialdir=startdir,mustexist="true")

        if dirName and len(dirName) > 0:
            g.es(dirName)
            compteur, compteurglobal = self.importDir(dirName,compteur=0,compteurglobal=0)
            c.selectVnode(c.currentVnode())
            c.frame.tree.redraw_now()
            self.esfm("\n")
            if language == 'french':
                g.es(str(compteurglobal)+" fichiers traités.")
            else:
                g.es(str(compteurglobal)+" files outlined.")
    #@+node:ekr.20050301083306.9: *3* esfm
    def esfm (self,chaine,**keys):

        """ Pour imprimer une chaîne de caractères sans retour à la ligne """

        if 1: # No longer needed so much now that we don't redraw as much.

            color = keys.get('color')

            if g.app.log:
                g.app.log.put(chaine,color=color)
            else:
                g.app.logWaiting.append((chaine,color),)
                g.pr(chaine,newline=False)
    #@+node:ekr.20050301083306.10: *3* importDir
    def importDir (self,dir,compteur,compteurglobal):

        """ La routine récursive de lecture des fichiers """

        if not g.os_path_exists(dir):
            if language == 'french':
                g.es("Ce répertoire n'existe pas: %s" + dir)
            else:
                g.es("No such Directory: %s" + dir)
            return compteur, compteurglobal # EKR

        head,tail = g.os_path_split(dir)
        c = self.c ; v = c.currentVnode()
        try:
            #ici, on liste le contenu du répertoire
            body=""
            #@+<< listdir >>
            #@+node:ekr.20050301083306.11: *4* << listdir >>
            try:
                fichiers = os.listdir(dir)
                dossiers = []
                for f in fichiers:
                    if compteur == 25:
                        self.esfm("\n")
                        compteur = 0
                    # mettre ici le code de création des noeuds
                    path = g.os_path_join(dir,f)
                    # est-ce un fichier ?
                    if g.os_path_isfile(path):
                        body += (f+"\n")
                    else:
                        # c'est alors un répertoire
                        dossiers.append(path)

                    self.esfm(".")
                    compteur += 1
                    compteurglobal += 1
            except Exception:
                if language == 'french':
                    g.es("erreur dans listage fichiers...")
                else:
                    g.es("os.listdir error...")
                g.es_exception()
            #@-<< listdir >>
            retour = c.importCommands.createHeadline(v,body,tail)
            #sélectionne le noeud nouvellement créé
            c.selectVnode(retour)
            if len(dossiers) > 0:
                for d in dossiers:
                    compteur,compteurglobal = self.importDir(d,compteur,compteurglobal)
            c.setChanged(True)
            #sélectionne le noeud parent
            c.selectVnode(v)
        except:
            if language == 'french':
                g.es("erreur d'insertion de noeud...")
            else:
                g.es("error while creating vnode...")
            g.es_exception()

        return compteur, compteurglobal
    #@-others
#@-others
#@-leo
