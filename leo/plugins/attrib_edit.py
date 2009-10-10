#@+leo-ver=4-thin
#@+node:tbrown.20091009210724.10971:@thin attrib_edit.py
#@<< docstring >>
#@+node:tbrown.20091009210724.10972:<< docstring >>
'''attrib_edit.py  -- Edit certain attributes in v.uA
'''
#@nonl
#@-node:tbrown.20091009210724.10972:<< docstring >>
#@nl

#@@language python
#@@tabwidth -4

#@<< imports >>
#@+node:tbrown.20091009210724.10973:<< imports >>
import leo.core.leoGlobals as g
import re
if g.app.gui.guiName() == "qt":
    import leo.core.leoPlugins as leoPlugins
    import os

    from PyQt4 import QtCore, QtGui
    Qt = QtCore.Qt
#@-node:tbrown.20091009210724.10973:<< imports >>
#@nl
__version__ = "0.1"
#@<< version history >>
#@+node:tbrown.20091009210724.10974:<< version history >>
#@@killcolor

#@+at 
#@nonl
# Use and distribute under the same terms as leo itself.
# 
# 0.1 TNB
#   - initial version
#@-at
#@nonl
#@-node:tbrown.20091009210724.10974:<< version history >>
#@nl

#@+others
#@+node:tbrown.20091009210724.10975:init
def init():

    if g.app.gui.guiName() != "qt":
        print 'attrib_edit.py plugin not loading because gui is not Qt'
        return False

    leoPlugins.registerHandler('after-create-leo-frame',onCreate)
    g.plugin_signon(__name__)
    return True

#@-node:tbrown.20091009210724.10975:init
#@+node:tbrown.20091009210724.10976:onCreate
def onCreate (tag,key):

    c = key.get('c')

    attrib_edit_Controller(c)
#@-node:tbrown.20091009210724.10976:onCreate
#@+node:tbrown.20091009210724.10979:class attrib_edit_Controller
class attrib_edit_Controller:

    '''A per-commander class that manages attribute editing.'''

    #@    @+others
    #@+node:tbrown.20091009210724.10981:__init__
    def __init__ (self, c):

        self.c = c

        self.handlers = [
           ('select3', self.updateEditor),
        ]

        for i in self.handlers:
            leoPlugins.registerHandler(i[0], i[1])

        c.frame.top.attr_splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        os = c.frame.top.leo_body_frame.parent()
        c.frame.top.attr_splitter.addWidget(c.frame.top.leo_body_frame)
        os.addWidget(c.frame.top.attr_splitter)
    #@-node:tbrown.20091009210724.10981:__init__
    #@+node:tbrown.20091009210724.10983:__del__
    def __del__(self):
        for i in self.handlers:
            leoPlugins.unregisterHandler(i[0], i[1])
    #@-node:tbrown.20091009210724.10983:__del__
    #@+node:tbrown.20091009210724.11210:initForm
    def initForm(self):
        w = self.c.frame.top.attr_splitter

        # seems this gets called 3 times during init, resulting in too many editor panels
        # so delete all but the 0th (the body editor)
        # print w.count()  # enable this line to see, only seems to be off at init
        for i in range(w.count()-1, 0, -1):
            w.widget(i).hide()
            w.widget(i).deleteLater()
        pnl = QtGui.QFrame()
        self.form = QtGui.QFormLayout()
        pnl.setLayout(self.form)
        w.addWidget(pnl)
    #@nonl
    #@-node:tbrown.20091009210724.11210:initForm
    #@+node:tbrown.20091009210724.11047:updateEditor
    def updateEditor(self,tag,k):

        c = self.c

        if k['c'] != self.c: return  # not our problem

        self.initForm()

        for attr in self.getAttribs():
            if len(attr) == 2:
                name, value = attr
                self.form.addRow(QtGui.QLabel(name), QtGui.QLabel(str(value)))
            else:
                name, value, path, type_ = attr
                self.form.addRow(QtGui.QLabel(name), QtGui.QLineEdit(str(value)))
    #@-node:tbrown.20091009210724.11047:updateEditor
    #@+node:tbrown.20091009210724.11211:getAttribs
    def getAttribs(self):
        """Return a list of tuples describing editable uAs.

        (name, value, [path, type])

        If only name and value are present then it's a read only attribute
        for display only.

        e.g.

        ('created', '2009-09-23', ['stickynotes','_edit','created'], str),
        ('cars', 2, ['inventory','_edit','_int','cars'], int)

        Changes should be written back to
        v.uA['stickynotes']['_edit']['created'] and
        v.uA['inventory']['_edit']['_int']['cars'] respectively
        """

        import time
        return [
          ('time', time.time()),
          ('cars', 0, ['_test','_edit','_int','cars'], int),
          ('phone', '', ['_test','_edit','phone'], str),
        ]
    #@-node:tbrown.20091009210724.11211:getAttribs
    #@-others
#@-node:tbrown.20091009210724.10979:class attrib_edit_Controller
#@-others
#@nonl
#@-node:tbrown.20091009210724.10971:@thin attrib_edit.py
#@-leo
