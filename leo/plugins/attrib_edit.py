#@+leo-ver=4-thin
#@+node:tbrown.20091026203923.1334:@thin /mnt/usr1/usr1/home/tbrown/.gnome-desktop/Package/leo/bzr/leo.repo/attrib_edit/leo/plugins/attrib_edit.py
#@<< docstring >>
#@+node:tbrown.20091009210724.10972:<< docstring >>
'''

attrib_edit.py - Edit attributes in v.u
=======================================

This plugin creates a frame for editing attributes similar to::

    Name:   Fred Blogs
    Home:   555-555-5555
    Work:   555-555-5556

``attrib_edit`` is also intended to provide attribute editing for
other plugins, see below.

These attributes are stored in the "unknownAttributes" (uA) data for
each node, accessed via ``v.u``.

When creating attributes on a node (using the ``attrib-edit-create`` command described below)
you should specify a path for
the attribute, e.g.::

    "addressbook First"

to store the attribute in v.u['addressbook']['_edit']['First']

As a convenience, entering a path like::

    "todo metadata created|creator|revised"

would create::

    v.u.['todo']['metadata']['_edit']['created']
    v.u.['todo']['metadata']['_edit']['creator']
    v.u.['todo']['metadata']['_edit']['revised']

The plugin defines the following commands, available either in the
plugin's sub-menu in the Plugins menu, or as ``Alt-X attrib-edit-*``.

attrib-edit-create
    Create a new attribute on the current node

attrib-edit-create-readonly
    Create a new readonly attribute on the current node,
    not really useful

attrib-edit-manage
    Select which attributes, from all attributes seen so
    far in this outline, to include on the current node.

attrib-edit-scan
    Scan the entire outline for attributes so ``attrib-edit-manage``
    has the complete list.

Technical details
+++++++++++++++++

See the source for complete documentation for use with other
plugins, here are some points of interest:

- in addition to ``v.u['addressbook']['_edit']['first']`` paths
  like ``v.u['addressbook']['_edit']['_int']['age']`` may be used
  to identify type, although currently there's no difference in
  the edit widget.

- in future the plugin may allow other plugins to register
  to provide attribute path information, instead of just
  scanning for ['_edit'] entries in v.u.

- currently there's no sorting of the attributes, which is
  a problem for some applications.  It's unclear where the
  desired order would be stored, without even more repetition
  in v.u.  When other plugins can register to manipulate the
  attribute list each plugin could address this, with unordered
  presentation in the absence of the client plugin.

- There's code to have the editor appear in a tab instead
  of its own area under the body editor, but (a) this is
  always being buried by output in the log window, and
  (b) there's a bug which leaves some (harmless) ghost 
  widgets in the background.  Enable by @setting
  ``attrib_edit_placement`` to 'tab'.

'''
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

    def __init__(self, c, v, name, value, path, type_):
        """v - node whose attribute we edit
        name - name of edited attribute
        value - initial value of edited attribute
        path - dictionary key path to attribute in v.u
        type_ - attribute type
        """
        self.c = c
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
            # self._widget.focusOutEvent = self.lostFocus
            # see lostFocus()
        return self._widget

    def updateValue(self, newValue):
        """copy value from widget to v.u"""
        self.setValue(self.v.u, self.path, self.type_(newValue))
        self.v.setDirty()

    def lostFocus(self, event):
        """Can link this in in widget(), but it stops tabbing through
        the attributes"""
        self.c.redraw()

    @staticmethod
    def setValue(a, path, value):
        """copy value into dict a on path,
        e.g. a['one']['more']['level'] = value
        """
        for i in path[:-1]:
            a = a.setdefault(i, {})
        a[path[-1]] = value
#@-node:tbrown.20091010211613.5257:class editWatcher
#@+node:tbrown.20091028131637.1353:class ListDialog
class ListDialog(QtGui.QDialog):

    #@    @+others
    #@+node:tbrown.20091028131637.1354:__init__
    def __init__(self, parent, title, text, entries):

        self.entries = entries

        QtGui.QDialog.__init__(self, parent)

        vbox = QtGui.QVBoxLayout()


        sa = QtGui.QScrollArea()
        salo = QtGui.QVBoxLayout()
        frame = QtGui.QFrame()
        frame.setLayout(salo)

        self.buttons = []

        for entry in entries:
            hbox = QtGui.QHBoxLayout()
            cb = QtGui.QCheckBox(entry[0])
            self.buttons.append(cb)
            if entry[1]:
                cb.setCheckState(Qt.Checked)
            hbox.addWidget(cb)
            salo.addLayout(hbox)

        sa.setWidget(frame)
        vbox.addWidget(sa)

        hbox = QtGui.QHBoxLayout()

        ok = QtGui.QPushButton("Ok")
        cancel = QtGui.QPushButton("Cancel")

        QtCore.QObject.connect(ok, QtCore.SIGNAL('clicked(bool)'), self.writeBack)
        QtCore.QObject.connect(cancel, QtCore.SIGNAL('clicked(bool)'), self.reject)

        hbox.addWidget(ok)
        hbox.addWidget(cancel)
        vbox.addLayout(hbox)

        self.setLayout(vbox)


    #@-node:tbrown.20091028131637.1354:__init__
    #@+node:tbrown.20091028131637.1359:writeBack
    def writeBack(self, event=None):

        for n,i in enumerate(self.buttons):
            self.entries[n][1] = (i.checkState() == Qt.Checked)

        self.accept()
    #@-node:tbrown.20091028131637.1359:writeBack
    #@-others
#@-node:tbrown.20091028131637.1353:class ListDialog
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

        self.attrPaths = set()  # set of *tuples* to paths

        self.handlers = [
           ('select3', self.updateEditor),
        ]

        for i in self.handlers:
            leoPlugins.registerHandler(i[0], i[1])

        # 'body' or 'tab' mode
        self.guiMode = c.config.getString('attrib_edit_placement') or 'body'

        if self.guiMode == 'body':
            self.holder = QtGui.QSplitter(QtCore.Qt.Vertical)
            self.holder.setMinimumWidth(300)
            os = c.frame.top.leo_body_frame.parent()
            self.holder.addWidget(c.frame.top.leo_body_frame)
            os.addWidget(self.holder)
            self.parent = self.holder
        elif self.guiMode == 'tab':
            self.parent = QtGui.QFrame()
            self.holder = QtGui.QHBoxLayout()
            self.parent.setLayout(self.holder)
            c.frame.log.createTab('Attribs', widget = self.parent)
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
                x = w.takeAt(0)

        pnl = QtGui.QFrame()
        self.form = QtGui.QFormLayout()
        self.form.setVerticalSpacing(0)
        pnl.setLayout(self.form)
        pnl.setAutoFillBackground(True)
        w.addWidget(pnl)
    #@-node:tbrown.20091009210724.11210:initForm
    #@+node:tbrown.20091009210724.11047:updateEditor
    def updateEditor(self,tag,k):
        """update edit panel when new node selected"""

        if k['c'] != self.c: return  # not our problem

        self.updateEditorInt()
    #@-node:tbrown.20091009210724.11047:updateEditor
    #@+node:tbrown.20091028100922.1493:updateEditorInt
    def updateEditorInt(self):

        c = self.c

        self.initForm()

        for attr in self.getAttribs():
            name, value, path, type_, readonly = attr
            if readonly:
                self.form.addRow(QtGui.QLabel(name), QtGui.QLabel(str(value)))

            else:
                editor = editWatcher(c, c.currentPosition().v, name, value, path, type_)
                self.editors.append(editor)

                self.form.addRow(QtGui.QLabel(name), editor.widget())
    #@-node:tbrown.20091028100922.1493:updateEditorInt
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
                                ans.append((ekt, d[k][ek][ekt], tuple(path+['_edit',ek,ekt]),
                                    type_, k != '_edit'))
                        else:
                            ans.append((ek, d[k][ek], tuple(path+['_edit',ek]), str, k != '_edit'))
    #@-node:tbrown.20091011151836.14789:recSearch
    #@+node:tbrown.20091009210724.11211:getAttribs
    def getAttribs(self, d = None):
        """Return a list of tuples describing editable uAs.

        (name, value, path, type, readonly)


        e.g.

        ('created', '2009-09-23', ('stickynotes','_edit','created'), str, False),
        ('cars', 2, ('inventory','_edit','_int','cars'), int, False)

        Changes should be written back to
        v.uA['stickynotes']['_edit']['created'] and
        v.uA['inventory']['_edit']['_int']['cars'] respectively
        """

        ans = []
        if not d:
            d = self.c.currentPosition().v.u
        self.recSearch(d, [], ans)

        for ns in ans:
            self.attrPaths.add(ns[2])

        return ans
    #@-node:tbrown.20091009210724.11211:getAttribs
    #@+node:tbrown.20091029101116.1413:addAttrib
    def addAttrib(self, attrib):
        editWatcher.setValue(self.c.currentPosition().v.u, attrib, '')
    #@nonl
    #@-node:tbrown.20091029101116.1413:addAttrib
    #@+node:tbrown.20091029101116.1414:delAttrib
    def delAttrib(self, attrib):

        a = self.c.currentPosition().v.u
        for i in attrib[:-1]:
            try:
                a = a[i]
            except KeyError:
                return
        try:
            del a[attrib[-1]]
        except KeyError:
            pass
    #@-node:tbrown.20091029101116.1414:delAttrib
    #@+node:tbrown.20091029101116.1424:scanAttribs
    def scanAttribs(self):
        """scan all of c for attrbutes"""
        for v in self.c.all_unique_nodes():
            self.getAttribs(v.u)  # updates internal list of attribs
        g.es("%d attributes found" % len(self.attrPaths))
    #@nonl
    #@-node:tbrown.20091029101116.1424:scanAttribs
    #@+node:tbrown.20091011151836.14788:createAttrib
    def createAttrib(self, event=None, readonly=False):

        path,ok = QtGui.QInputDialog.getText(self.parent, "Enter attribute path",
            "Enter path to attribute (space separated words)")

        ns = str(path).split()  # not the QString
        if not ok or not ns:
            g.es("Cancelled")
            return

        type_ = {True: '_view', False: '_edit'}[readonly]

        if '|' in ns[-1]:
            nslist = [ ns[:-1] + [i.strip()] for i in ns[-1].split('|') ]
        else:
            nslist = [ns]

        for ns in nslist:

            if type_ not in ns:
                ns.insert(-1, type_)

            self.attrPaths.add(tuple(ns))

            self.addAttrib(ns)

        self.c.currentPosition().v.setDirty()
        self.c.redraw()

        self.updateEditorInt()
    #@-node:tbrown.20091011151836.14788:createAttrib
    #@+node:tbrown.20091028131637.1358:manageAttrib
    def manageAttrib(self):

        attribs = [i[2] for i in self.getAttribs()]

        dat = [ ['.'.join([j for j in i if j not in ('_edit','_view')]), (i in attribs), i]
               for i in self.attrPaths]

        if not dat:
            g.es('No attributes seen (yet)')
            return

        dat.sort(key=lambda x: x[0])

        res = ListDialog(self.parent, "Enter attribute path",
            "Enter path to attribute (space separated words)", 
            dat)

        res.exec_()

        if res.result() == QtGui.QDialog.Rejected:
            return

        # check for deletions
        for i in dat:
            if i[2] in attribs and not i[1]:
                res = QtGui.QMessageBox(QtGui.QMessageBox.Question,
                    "Really delete attributes?","Really delete attributes?",
                    QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel, self.parent)
                if res.exec_() == QtGui.QMessageBox.Cancel:
                    return
                break

        # apply changes
        for i in dat:
            if i[2] in attribs and not i[1]:
                self.delAttrib(i[2])
            elif i[2] not in attribs and i[1]:
                self.addAttrib(i[2])

        self.updateEditorInt()

    #@-node:tbrown.20091028131637.1358:manageAttrib
    #@-others
#@-node:tbrown.20091009210724.10979:class attrib_edit_Controller
#@+node:tbrown.20091029101116.1415:cmd_Manage
def cmd_Manage(c):
   c.attribEditor.manageAttrib()
#@-node:tbrown.20091029101116.1415:cmd_Manage
#@+node:tbrown.20091029101116.1419:cmd_Create
def cmd_Create(c):
   c.attribEditor.createAttrib()
#@-node:tbrown.20091029101116.1419:cmd_Create
#@+node:tbrown.20091029101116.1421:cmd_CreateReadonly
def cmd_CreateReadonly(c):
   c.attribEditor.createAttrib(readonly=True)
#@-node:tbrown.20091029101116.1421:cmd_CreateReadonly
#@+node:tbrown.20091029101116.1426:cmd_Scan
def cmd_Scan(c):
   c.attribEditor.scanAttribs()
#@-node:tbrown.20091029101116.1426:cmd_Scan
#@-others
#@nonl
#@-node:tbrown.20091026203923.1334:@thin /mnt/usr1/usr1/home/tbrown/.gnome-desktop/Package/leo/bzr/leo.repo/attrib_edit/leo/plugins/attrib_edit.py
#@-leo
