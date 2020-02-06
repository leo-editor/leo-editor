#@+leo-ver=5-thin
#@+node:ekr.20110110105526.5463: * @file ftp.py
'''Uploading of file by ftp.'''

# 0.1 05.01.2011 by Ivanov Dmitriy.
#@+<< ftp imports >>
#@+node:ekr.20161223150819.1: ** << ftp imports >>
import leo.core.leoGlobals as g
import leo.core.leoPlugins as leoPlugins
from leo.core.leoQt import isQt5,QtGui,QtWidgets
if 1:
     # pylint: disable=no-name-in-module,no-member
    QAction = QtWidgets.QAction if isQt5 else QtGui.QAction
import json
import os
from ftplib import FTP
#@-<< ftp imports >>
#@+others
#@+node:ekr.20110110105526.5467: ** init
def init ():
    '''Return True if the plugin has loaded successfully.'''
    if g.app.gui.guiName() != "qt":
        print('ftp.py plugin not loading because gui is not Qt')
        return False
    leoPlugins.registerHandler("after-create-leo-frame", onCreate)
    g.plugin_signon(__name__)
    return True
#@+node:ekr.20110110105526.5468: ** onCreate
def onCreate (tag, keys):
    c = keys.get('c')
    if c:
        # Check whether the node @data ftp exists in the file being opened.
        # If so, create a button and register.
        p = g.findTopLevelNode(c, '@data ftp')
        if p:
            pluginController(c)
#@+node:ekr.20110110105526.5469: ** class pluginController
class pluginController:

    #@+others
    #@+node:ekr.20110110105526.5470: *3* __init__(pluginController, ftp.py)
    def __init__ (self,c):
        self.c = c
        # c.k.registerCommand('upload',self.upload)
        # script = "c.k.simulateCommand('upload')"
        # g.app.gui.makeScriptButton(c,script=script,buttonText='Upload')
        ib_w = self.c.frame.iconBar.w
        action = QAction('Upload', ib_w)
        self.c.frame.iconBar.add(qaction = action, command = self.upload)


    #@+node:ekr.20110110105526.5471: *3* upload
    def upload (self,event=None):
        c = self.c ; p = c.p

        g.es("upload started")
        p = g.findTopLevelNode(c, '@data ftp')
        if p:
            files = json.loads(p.b)

            # credentials - array of (host, pass) of server,
            # to while the files must be uploaded I suggest that the locations must be the same.
            credentials = files[0]

            for element in credentials:

                g.es(element[0])
                ftp = FTP(element[0])
                ftp.login(element[1], element[2])
                #@+<<upload all the modified files>>
                #@+node:ekr.20110110105526.5472: *4* <<upload all the modified files>>
                #@@c
                for i in range(1, len(files)):

                    file = files[i]

                    n = len(file)
                    if n < 3:
                        file.append(-1)

                    time = os.path.getmtime(file[0])
                    if time != file[2]:
                        files[i][2] = time
                        g.es(files[i][0])
                        FH = open(files[i][0],"rb")
                        ftp.storbinary('STOR ' + files[i][1], FH)
                        FH.close()
                #@-<<upload all the modified files>>

                ftp.quit()
                p.b = json.dumps(files)

            g.es("Upload complete")
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
