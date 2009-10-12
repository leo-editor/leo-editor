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
#@+node:tbrown.20091010211613.5257:class editWatcher
class editWatcher(object):
    """class to supply widget for editing attribute and handle
    its textChanged signal"""

    def __init__(self, v, name, value, path, type_):
        """v - node whose attribute we edit
        name - name of edited attribute
        value - initial value of edited attribute
        path - dictionary key path to attribute in v.u
        type_ - attribute type
        """
        self.v = v
        self.name = name
        self.value = value
        self.path = path
        self.type_ = type_
        self._widget = None

    def widget(self):
        """return widget for editing this attribute"""
        if not self._widget:
            self._widget = QtGui.QLineEdit(str(self.value))
            QtCore.QObject.connect(self._widget, 
                QtCore.SIGNAL("textChanged(QString)"), self.updateValue)
        return self._widget

    def updateValue(self, newValue):
        """copy value from widget to v.u"""
        self.setValue(self.v.u, self.path, self.type_(newValue))

    @staticmethod
    def setValue(a, path, value):
        """copy value into dict a on path,
        e.g. a['one']['more']['level'] = value
        """
        for i in path[:-1]:
            a = a.setdefault(i, {})
        a[path[-1]] = value
        print path,value
#@-node:tbrown.20091010211613.5257:class editWatcher
#@+node:tbrown.20091009210724.10979:class attrib_edit_Controller
class attrib_edit_Controller:

    '''A per-commander class that manages attribute editing.'''

    typeMap = {
        '_int': int,
        '_float': float,
        '_bool': bool,
    }

    #@    @+others
    #@+node:tbrown.20091009210724.10981:__init__
    def __init__ (self, c):

        self.c = c
        c.attribEditor = self

        self.handlers = [
           ('select3', self.updateEditor),
        ]

        for i in self.handlers:
            leoPlugins.registerHandler(i[0], i[1])

        # self.guiMode = 'tab'
        self.guiMode = 'body'

        if self.guiMode == 'body':
            self.holder = QtGui.QSplitter(QtCore.Qt.Vertical)
            os = c.frame.top.leo_body_frame.parent()
            self.holder.addWidget(c.frame.top.leo_body_frame)
            os.addWidget(self.holder)
        elif self.guiMode == 'tab':
            frame = QtGui.QFrame()
            self.holder = QtGui.QHBoxLayout()
            frame.setLayout(self.holder)
            c.frame.log.createTab('Attribs', widget = frame)
    #@-node:tbrown.20091009210724.10981:__init__
    #@+node:tbrown.20091009210724.10983:__del__
    def __del__(self):
        for i in self.handlers:
            leoPlugins.unregisterHandler(i[0], i[1])
    #@-node:tbrown.20091009210724.10983:__del__
    #@+node:tbrown.20091009210724.11210:initForm
    def initForm(self):
        """set up self.form, the blank form layout before adding edit widgets"""
        self.editors = []

        w = self.holder

        if self.guiMode == 'body':
            # seems this gets called 3 times during init,
            # resulting in too many attrib editors
            # so delete all but the 0th (the body editor)
            # print w.count()  # enable this line to see, only seems to be off at init
            for i in range(w.count()-1, 0, -1):
                w.widget(i).hide()
                w.widget(i).deleteLater()

        elif self.guiMode == 'tab':
            while w.count():
                w.takeAt(0)

        pnl = QtGui.QFrame()
        self.form = QtGui.QFormLayout()
        pnl.setLayout(self.form)
        pnl.setAutoFillBackground(True)
        w.addWidget(pnl)
    #@-node:tbrown.20091009210724.11210:initForm
    #@+node:tbrown.20091009210724.11047:updateEditor
    def updateEditor(self,tag,k):
        """update edit panel when new node selected"""
        c = self.c

        if k['c'] != self.c: return  # not our problem

        self.initForm()

        for attr in self.getAttribs():
            if len(attr) == 2:  # read only attribute
                name, value = attr
                self.form.addRow(QtGui.QLabel(name), QtGui.QLabel(str(value)))
            else:               # editable attribute
                name, value, path, type_ = attr
                editor = editWatcher(c.currentPosition().v, name, value, path, type_)
                self.editors.append(editor)

                self.form.addRow(QtGui.QLabel(name), editor.widget())
    #@-node:tbrown.20091009210724.11047:updateEditor
    #@+node:tbrown.20091011151836.14789:recSearch
    def recSearch(self, d, path, ans):
        """recursive search of tree of dicts for values whose
        key path is like [*][*][*]['_edit'][*] or
        [*][*][*]['_edit']['_int'][*]

        Modifies list ans
        """
        for k in d:
            if isinstance(d[k], dict):
                if k not in ('_edit', '_view'):
                    self.recSearch(d[k], path+[k], ans)
                else:
                    # k == '_edit' or '_view'
                    for ek in d[k]:
                        if ek in self.typeMap:
                            # ek is '_int' or similar
                            type_ = self.typeMap[ek]
                            for ekt in d[k][ek]:
                                if k == '_edit':
                                    ans.append((ekt, d[k][ek][ekt], path+['_edit',ek,ekt], type_))
                                else:
                                    ans.append((ekt, d[k][ek][ekt]))
                        else:
                            if k == '_edit':
                                ans.append((ek, d[k][ek], path+['_edit',ek], str))
                            else:
                                ans.append((ek, d[k][ek]))
    #@-node:tbrown.20091011151836.14789:recSearch
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

        ans = []
        d = self.c.currentPosition().v.u
        self.recSearch(d, [], ans)

        return ans
    #@-node:tbrown.20091009210724.11211:getAttribs
    #@+node:tbrown.20091011151836.14787:getNamespace
    def getNamespace(self, event=None):
        # JUNK
       stateName = 'get-input'
       k = self.c.k
       state = k.getState(stateName)

       if state == 0:
           k.setLabelBlue('Namespace (space separated words): ',protect=True)
           k.getArg(event,stateName,1,self.getNamespace)
       else:
           k.clearState()
           self.namespace = k.arg
    #@-node:tbrown.20091011151836.14787:getNamespace
    #@+node:tbrown.20091011151836.14788:createAttrib
    def createAttrib(self, event=None):
       stateName = 'get-input'
       k = self.c.k
       state = k.getState(stateName)

       if state == 0:
           k.setLabelBlue('Namespace (space separated words): ',protect=True)
           k.getArg(event,stateName,1,self.createAttrib)
       else:
           k.clearState()
           ns = k.arg.split()
           if '_edit' not in ns:
               ns.insert(-1, '_edit')
           editWatcher.setValue(self.c.currentPosition().v.u, ns, '')
    #@-node:tbrown.20091011151836.14788:createAttrib
    #@+node:tbrown.20091011151836.5259:command attrib-create
    @staticmethod
    @g.command('attrib-create')
    def attrib_create(event):
        event['c'].attribEditor.createAttrib()
    #@nonl
    #@-node:tbrown.20091011151836.5259:command attrib-create
    #@-others
#@-node:tbrown.20091009210724.10979:class attrib_edit_Controller
#@-others
#@nonl
#@-node:tbrown.20091009210724.10971:@thin attrib_edit.py
#@-leo
