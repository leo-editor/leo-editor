#@+leo-ver=5-thin
#@+node:ekr.20190805022257.1: * @file pyzo_file_browser.py
'''
Experimental plugin that adds pyzo's file browser dock to Leo.
'''
#@+<< pyzo_file_browser imports >>
#@+node:ekr.20190805031511.1: ** << pyzo_file_browser imports >>
import leo.core.leoGlobals as g

###
    # This ends Leo, with "Still warming up...
    # from leo.external.pyzo.tools.pyzoFileBrowser import PyzoFileBrowser
    # print(PyzoFileBrowser)

##### From pyzo/tools/pyzoFileBrowser.__init__.py

import os.path as op
assert op

### import pyzo
### from pyzo.util import zon as ssdf
### from pyzo.util.qt import QtCore, QtGui, QtWidgets  # noqa

from leo.core.leoQt import QtCore, QtWidgets # QtGui, 

# from pyzo.util._locale import translate

# from .browser import Browser
# from .utils import cleanpath, isdir

##### From pyzo/tools/pyzoFileBrowser/browser.py

# import sys
# import os.path as op

# import pyzo
# from pyzo import translate
# from pyzo.util import zon as ssdf

# from . import QtCore, QtGui, QtWidgets
# from . import proxies
# from .tree import Tree
# from .utils import cleanpath, isdir

#@-<< pyzo_file_browser imports >>

#@+others
#@+node:ekr.20190805032828.1: ** top-level functions
#@+node:ekr.20190805022358.1: *3* init (pyzo_file_browser.py)
init_warning_given = False

def init():
    '''Return True if the pyzo_file_browser plugin can be loaded.'''
    
    def oops(message):
        global init_warning_given
        if not init_warning_given:
            init_warning_given = True
            print('%s %s' % (__name__, message))
        return False

    if g.app.gui.guiName() != "qt":
        return oops('requires Qt gui')
    # if not pyzo:
        # return oops('requires pyzo')
    if not g.app.dock:
        return oops('is incompatible with --no-dock')
    g.plugin_signon(__name__)
    g.registerHandler('after-create-leo-frame', onCreate)
    return True
#@+node:ekr.20190805022841.1: *3* onCreate (pyzo_file_browser.py)
def onCreate(tag, keys):
    '''TO DO'''
    c = keys.get('c')
    if c:
        mw = c.frame.top
        g.trace(mw)
        assert mw
        dock = mw.createDockWidget(
            closeable=True,
            moveable=True,
            height=100,
            name='file browser'
        )
        mw.leo_docks.append(dock)
        # w = self.createBodyPane(parent=None)
        w = PyzoFileBrowser(parent=None)
        dock.setWidget(w)
        area = QtCore.Qt.RightDockWidgetArea
        mw.addDockWidget(area, dock)
#@+node:ekr.20190805031430.1: ** class PyzoFileBrowser(QWidget)
class PyzoFileBrowser(QtWidgets.QWidget):
    """ The main tool widget. An instance of this class contains one or
    more Browser instances. If there are more, they can be selected
    using a tab bar.
    """

    #@+others
    #@+node:ekr.20190805031430.2: *3* PyzoFileBrowser.__init__
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)

        # Get config
        
        ###
            # toolId =  self.__class__.__name__.lower() + '2'  # This is v2 of the file browser
            # if toolId not in pyzo.config.tools:
                # pyzo.config.tools[toolId] = ssdf.new()
            # self.config = pyzo.config.tools[toolId]

        # Ensure three main attributes in config
        ###
            # for name in ['expandedDirs', 'starredDirs']:
                # if name not in self.config:
                    # self.config[name] = []

        # Ensure path in config
        ###
            # # if leo_g: leo_g.pr('PyzoFileBrowser.__init__', self.config.__class__)
            # if 'path' not in self.config or not isdir(self.config.path):
                # self.config.path = op.expanduser('~')

        # Check expandedDirs and starredDirs.
        # Make path objects and remove invalid dirs. Also normalize case,
        # should not be necessary, but maybe the config was manually edited.
        ###
            # expandedDirs, starredDirs = [], []
            # for d in self.config.starredDirs:
                # if 'path' in d and 'name' in d and 'addToPythonpath' in d:
                    # if isdir(d.path):
                        # d.path = op.normcase(cleanpath(d.path))
                        # starredDirs.append(d)
            # for p in set([str(p) for p in self.config.expandedDirs]):
                # if isdir(p):
                    # p = op.normcase(cleanpath(p))
                    # # Add if it is a subdir of a starred dir
                    # for d in starredDirs:
                        # if p.startswith(d.path):
                            # expandedDirs.append(p)
                            # break
            # self.config.expandedDirs, self.config.starredDirs = expandedDirs, starredDirs

        # Create browser(s).
        ###
            # self._browsers = []
            # for i in [0]:
                # self._browsers.append(Browser(self, self.config) )

        # Layout
        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)
        ### layout.addWidget(self._browsers[0])
        layout.setSpacing(0)
        layout.setContentsMargins(4,4,4,4)
    #@+node:ekr.20190805031430.3: *3* PyzoFileBrowser.path
    def path(self):
        """ Get the current path shown by the file browser.
        """
        browser = self._browsers[0]
        return browser._tree.path()
    #@+node:ekr.20190805031430.4: *3* PyzoFileBrowser.setPath
    def setPath(self, path):
        """ Set the shown path.
        """
        browser = self._browsers[0]
        browser._tree.setPath(path)
    #@+node:ekr.20190805031430.5: *3* PyzoFileBrowser.getAddToPythonPath
    def getAddToPythonPath(self):
        """
        Returns the path to be added to the Python path when starting a shell
        If a project is selected, which has the addToPath checkbox selected,
        returns the path of the project. Otherwise, returns None
        """
        # Select browser
        browser = self._browsers[0]
        # Select active project
        d = browser.currentProject()
        if d and d.addToPythonpath:
            return d.path
        return None
    #@+node:ekr.20190805031430.6: *3* PyzoFileBrowser.getDefaultSavePath
    def getDefaultSavePath(self):
        """
        Returns the path to be used as default when saving a new file in pyzo.
        Or None if the no path could be determined
        """
        # Select current browser
        browser = self._browsers[0]
        # Select its path
        path = browser._tree.path()
        # Return
        if op.isabs(path) and op.isdir(path):
            return path
        return None
    #@+node:ekr.20190805031430.7: *3* PyzoFileBrowser.closeEvent
    def closeEvent(self, event):
        # Close all browsers so they can clean up the file system proxies
        for browser in self._browsers:
            browser.close()
        return QtWidgets.QWidget.closeEvent(self, event)
    #@-others
#@-others
#@-leo
