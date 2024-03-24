#@+leo-ver=5-thin
#@+node:tbrown.20091029123555.5319: * @file ../plugins/attrib_edit.py
#@+<< docstring >>
#@+node:tbrown.20091009210724.10972: ** << docstring >>
r""" Edits user attributes in a Qt frame.

This plugin creates a frame for editing attributes similar to::

    Name:   Fred Blogs
    Home:   555-555-5555
    Work:   555-555-5556

``attrib_edit`` is also intended to provide attribute editing for
other plugins, see below.

The editor panel appears in the Log pane in its own tab.  If the free_layout
system is active you can move it into its own pane (e.g. below the body text)
by right clicking the pane dividers.

The attributes can be stored in different ways, three modes are implemented
currently:

v.u mode
  These attributes are stored in the "unknownAttributes" (uA) data for
  each node, accessed via v.u.

Field:
  Attributes are lines starting (no whitespace) with "AttributeName:" in
  the body text.

@Child
  Attributes are the head strings of child nodes when the head string
  starts with '@AttributeName' where the first letter (second character)
  must be capitalized.

The plugin defines the following commands, available either in the
plugin's sub-menu in the Plugins menu, or as ``Alt-X attrib-edit-*``.

attrib-edit-modes
    Select which attribute setting / getting modes to use.  More than one mode
    can be used at the same time.

    You can also control which modes are active by listing them
    with the @data attrib_edit_active_modes setting.  For example::

        Field:
        @Child
        # v.u mode

    would cause only the "Field:" and "@Child" modes to be active be default.

attrib-edit-manage
    Select which attributes, from all attributes seen so
    far in this outline, to include on the current node.

attrib-edit-scan
    Scan the entire outline for attributes so ``attrib-edit-manage``
    has the complete list.

attrib-edit-create
    Create a new attribute on the current node.  If Field: or \@Child modes
    are active, they simply remind you how to create an attribute in the log pane.
    If the "v.u mode" mode is active, you're prompted for a path for the attribute.
    For example::

        addressbook First

    to store the attribute in v.u['addressbook']['_edit']['First']

    As a convenience, entering a path like::

        todo metadata created|creator|revised

    would create::

        v.u.['todo']['metadata']['_edit']['created']
        v.u.['todo']['metadata']['_edit']['creator']
        v.u.['todo']['metadata']['_edit']['revised']


**Technical details**

See the source for complete documentation for use with other
plugins. Here are some points of interest:

- In addition to ``v.u['addressbook']['_edit']['first']``, paths
  like ``v.u['addressbook']['_edit']['_int']['age']`` may be used
  to identify type, although currently there's no difference in
  the edit widget.

- In the future the plugin may allow other plugins to register
  to provide attribute path information, instead of just
  scanning for ['_edit'] entries in v.u.

- Currently there's no sorting of the attributes in "v.u mode", which is
  a problem for some applications.  It's unclear where the
  desired order would be stored, without even more repetition
  in v.u.  When other plugins can register to manipulate the
  attribute list each plugin could address this, with unordered
  presentation in the absence of the client plugin.

"""
#@-<< docstring >>
# Written by TNB.
from typing import Any
from leo.core import leoGlobals as g
from leo.core.leoQt import QtCore, QtWidgets
from leo.core.leoQt import DialogCode, Orientation

# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.

QWidget = QtWidgets.QWidget

#@+others
#@+node:tbrown.20091009210724.10975: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    if g.app.gui.guiName() != "qt":
        print('attrib_edit.py plugin not loading because gui is not Qt')
        return False
    g.registerHandler('after-create-leo-frame', onCreate)
    g.plugin_signon(__name__)
    return True
#@+node:tbrown.20091009210724.10976: ** onCreate
def onCreate(tag, key):

    c = key.get('c')

    attrib_edit_Controller(c)
#@+node:tbrown.20091103080354.1400: ** class AttributeGetter
class AttributeGetter:

    implementations: list[Any] = []

    typeMap = {
        '_int': int,
        '_float': float,
        '_bool': bool,
    }

    @classmethod
    def register(cls, subclass):
        cls.implementations.append(subclass)

    def __init__(self, c):
        self.c = c

    def name(self):
        return "ABSTRACT VIRTUAL BASE CLASS"

    def getAttribs(self, v):
        raise NotImplementedError
    def setAttrib(self, v, path, value):
        raise NotImplementedError
    def delAttrib(self, v, path):
        raise NotImplementedError

    def helpCreate(self):
        """either a string telling user how to add an attribute, or
        True if the Getter needs to help the user create an attribute"""
        return "ABSTRACT VIRTUAL BASE CLASS"

    def longDescrip(self, path):
        """give the long description of the attribute on path 'path'.

        ASSUMES: path determines name

        E.g. attribute named 'count' might be described as 'address.people.count'
        """
        raise NotImplementedError
#@+node:tbrown.20091103080354.1402: ** class AttributeGetterUA
class AttributeGetterUA(AttributeGetter):
    #@+others
    #@+node:tbrown.20091103080354.1409: *3* recSearch
    def recSearch(self, d, path, ans):
        """recursive search of tree of dicts for values whose
        key path is like [*][*][*]['_edit'][*] or
        [*][*][*]['_edit']['_int'][*]

        Modifies list ans
        """
        for k in d:
            if isinstance(d[k], dict):
                if k not in ('_edit', '_view'):
                    self.recSearch(d[k], path + [k], ans)
                else:
                    # k == '_edit' or '_view'
                    for ek in d[k]:
                        if ek in self.typeMap:
                            # ek is '_int' or similar
                            type_ = self.typeMap[ek]
                            for ekt in d[k][ek]:
                                ans.append((self,
                                    ekt, d[k][ek][ekt], tuple(path + ['_edit', ek, ekt]),
                                    type_, k != '_edit'))
                        else:
                            ans.append((self,
                                ek, d[k][ek], tuple(path + ['_edit', ek]), str, k != '_edit'))
    #@+node:tbrown.20091103080354.1410: *3* getAttribs
    def getAttribs(self, v):
        """Return a list of tuples describing editable uAs.

        (class, name, value, path, type, readonly)


        e.g.

        (AttributeGetterUA, 'created', '2009-09-23', ('stickynotes','_edit','created'), str, False),
        (AttributeGetterUA, 'cars', 2, ('inventory','_edit','_int','cars'), int, False)

        Changes should be written back to
        v.uA['stickynotes']['_edit']['created'] and
        v.uA['inventory']['_edit']['_int']['cars'] respectively
        """

        ans: list[tuple] = []
        d = v.u

        self.recSearch(d, [], ans)

        return ans
    #@+node:tbrown.20091103080354.1430: *3* setAttrib
    def setAttrib(self, v, path, value):
        """copy value into dict a on path,
        e.g. a['one']['more']['level'] = value
        """

        a = v.u

        for i in path[:-1]:
            a = a.setdefault(i, {})
        a[path[-1]] = value
    #@+node:tbrown.20091103080354.1438: *3* delAttrib
    def delAttrib(self, v, path):
        a = v.u
        for i in path[:-1]:
            try:
                a = a[i]
            except KeyError:
                return
        try:
            del a[path[-1]]
        except KeyError:
            pass
    #@+node:tbrown.20091103080354.1411: *3* name
    def name(self):
        return "v.u mode"
    #@+node:tbrown.20091103080354.1431: *3* helpCreate
    def helpCreate(self):
        """does the Getter need to help the user create an attribute?"""
        return True
    #@+node:tbrown.20091103080354.1432: *3* createAttrib
    def createAttrib(self, v, gui_parent=None):

        path, ok = QtWidgets.QInputDialog.getText(gui_parent,
            "Enter attribute path",
            "Enter path to attribute (space separated words)")

        ns = str(path).split()
        if not ok or not ns:
            g.es("Cancelled")
            return

        # FIXME type_ = {True: '_view', False: '_edit'}[readonly]
        type_ = '_edit'

        if '|' in ns[-1]:
            nslist = [ns[:-1] + [i.strip()] for i in ns[-1].split('|')]
        else:
            nslist = [ns]

        for ns in nslist:

            if type_ not in ns:
                ns.insert(-1, type_)

            self.setAttrib(v, ns, '')

            # FIXME self.attrPaths.add(tuple(ns))
    #@+node:tbrown.20091103080354.1433: *3* longDescrip
    def longDescrip(self, path):

        return '.'.join([j for j in path if j not in ('_edit', '_view')])
    #@-others

AttributeGetter.register(AttributeGetterUA)
#@+node:tbrown.20091103080354.1420: ** class AttributeGetterAt
class AttributeGetterAt(AttributeGetter):
    #@+others
    #@+node:tbrown.20091103080354.1422: *3* getAttribs
    def getAttribs(self, v):
        """Return a list of tuples describing editable uAs.

        (class, name, value, path, type, readonly)


        e.g.

        (AttributeGetterUA, 'created', '2009-09-23', ('stickynotes','_edit','created'), str, False),
        (AttributeGetterUA, 'cars', 2, ('inventory','_edit','_int','cars'), int, False)

        Changes should be written back to
        v.uA['stickynotes']['_edit']['created'] and
        v.uA['inventory']['_edit']['_int']['cars'] respectively
        """

        ans = []

        for n in v.children:
            if n.h and n.h[0] == '@' and ('A' <= n.h[1] <= 'Z'):
                words = n.h[1:].split(None, 1)
                if not words:
                    continue
                if len(words) == 1:
                    words.append('')
                ans.append((self, words[0], words[1], words[0], str, False))
        return ans
    #@+node:tbrown.20091103080354.6237: *3* setAttrib
    def setAttrib(self, v, path, value):


        for n in v.children:
            if n.h[0] == '@' and ('A' <= n.h[1] <= 'Z'):
                words = n.h[1:].split(None, 1)
                if len(words) == 1:
                    words.append('')
                if words[0] == path:
                    n.h = "@%s %s" % (path, value)
                    break
        else:
            p = self.c.vnode2position(v)
            n = p.insertAsLastChild()
            n.h = "@%s %s" % (path, value)
    #@+node:tbrown.20091103080354.6244: *3* delAttrib
    def delAttrib(self, v, path):

        for n in v.children:
            if n.h[0] == '@' and ('A' <= n.h[1] <= 'Z'):
                words = n.h[1:].split(None, 1)
                if not words:
                    continue
                if words[0] == path:
                    p = self.c.vnode2position(n)
                    p.doDelete()
                    break
    #@+node:tbrown.20091103080354.1423: *3* name
    def name(self):
        return "@Child"
    #@+node:tbrown.20091103080354.1443: *3* helpCreate
    def helpCreate(self):
        return "Add a child named '@AttributeName'"
    #@+node:tbrown.20091103080354.1435: *3* longName
    def longDescrip(self, path):

        return path
    #@-others

AttributeGetter.register(AttributeGetterAt)
#@+node:tbrown.20091103080354.1427: ** class AttributeGetterColon
class AttributeGetterColon(AttributeGetter):
    #@+others
    #@+node:tbrown.20091103080354.1428: *3* getAttribs
    def getAttribs(self, v):

        ans = []
        parts = v.b.split('\n', 100)

        for i in parts[:99]:
            if not i or i[0].isspace():
                continue
            words = i.split(None, 1)
            if words and words[0] and words[0][-1] == ':':
                if len(words) == 1:
                    words.append('')
                ans.append((self, words[0][:-1], words[1], words[0][:-1], str, False))

        return ans
    #@+node:tbrown.20091103080354.6246: *3* setAttrib
    def setAttrib(self, v, path, value):

        parts = v.b.split('\n', 100)

        for n, i in enumerate(parts[:99]):
            words = i.split(None, 1)
            if words and words[0] and words[0][-1] == ':' and words[0][:-1] == path:
                parts[n] = "%s: %s" % (path, value)
                v.b = '\n'.join(parts)
                break
        else:
            v.b = "%s: %s\n%s" % (path, value, v.b)
    #@+node:tbrown.20091103080354.6248: *3* delAttrib
    def delAttrib(self, v, path):

        parts = v.b.split('\n', 100)

        for n, i in enumerate(parts[:99]):
            words = i.split(None, 1)
            if words and words[0] and words[0][-1] == ':' and words[0][:-1] == path:
                del parts[n]
                v.b = '\n'.join(parts)
                break
    #@+node:tbrown.20091103080354.1429: *3* name
    def name(self):
        return "Field:"
    #@+node:tbrown.20091103080354.1441: *3* helpCreate
    def helpCreate(self):
        return "Add 'AttributeName:' to the text"
    #@+node:tbrown.20091103080354.1437: *3* longName
    def longDescrip(self, path):

        return path
    #@-others

AttributeGetter.register(AttributeGetterColon)
#@+node:tbrown.20091028131637.1353: ** class ListDialog
class ListDialog(QtWidgets.QDialog):  # type:ignore

    #@+others
    #@+node:tbrown.20091028131637.1354: *3* __init__ (attrib_edit.py)
    def __init__(self, parent, title, text, entries):

        self.entries = entries
        super().__init__(parent)
        vbox = QtWidgets.QVBoxLayout()
        sa = QtWidgets.QScrollArea()
        salo = QtWidgets.QVBoxLayout()
        frame = QtWidgets.QFrame()
        frame.setLayout(salo)
        self.buttons = []
        for entry in entries:
            hbox = QtWidgets.QHBoxLayout()
            cb = QtWidgets.QCheckBox(entry[0])
            self.buttons.append(cb)
            if entry[1]:
                cb.setChecked(True)
            hbox.addWidget(cb)
            salo.addLayout(hbox)
        sa.setWidget(frame)
        vbox.addWidget(sa)
        hbox = QtWidgets.QHBoxLayout()
        ok = QtWidgets.QPushButton("Ok")
        cancel = QtWidgets.QPushButton("Cancel")
        ok.clicked.connect(self.writeBack)
        # QtCore.QObject.connect(ok, QtCore.SIGNAL('clicked(bool)'), self.writeBack)
        # QtCore.QObject.connect(cancel, QtCore.SIGNAL('clicked(bool)'), self.reject)
        cancel.clicked.connect(self.reject)
        hbox.addWidget(ok)
        hbox.addWidget(cancel)
        vbox.addLayout(hbox)
        self.setLayout(vbox)
    #@+node:tbrown.20091028131637.1359: *3* writeBack
    def writeBack(self, event=None):

        for n, i in enumerate(self.buttons):
            self.entries[n][1] = (i.isChecked())
        self.accept()
    #@-others
#@+node:tbrown.20091010211613.5257: ** class editWatcher
class editWatcher:
    """class to supply widget for editing attribute and handle
    its textChanged signal"""

    def __init__(self, c, v, class_, name, value, path, type_):
        """v - node whose attribute we edit
        name - name of edited attribute
        value - initial value of edited attribute
        path - dictionary key path to attribute in v.u
        type_ - attribute type
        """
        self.c = c
        self.v = v
        self.class_ = class_
        self.name = name
        self.value = value
        self.path = path
        self.type_ = type_
        self._widget = None

    def widget(self):
        """return widget for editing this attribute"""
        if not self._widget:
            self._widget = w = QtWidgets.QLineEdit(str(self.value))
            w.textChanged.connect(self.updateValue)
            self._widget.focusOutEvent = self.lostFocus
            # see lostFocus()
        return self._widget

    def updateValue(self, newValue):
        """copy value from widget to v.u"""
        self.class_.setAttrib(self.v, self.path, self.type_(newValue))
        self.v.setDirty()

    def lostFocus(self, event):
        """Can activate this in in widget(), but it stops tabbing through
        the attributes - unless we can check that none of our siblings
        has focus..."""
        sibs = self._widget.parent().findChildren(QtWidgets.QLineEdit)
        for i in sibs:
            if i.hasFocus():
                break
        else:
            self.c.redraw()
#@+node:tbrown.20091009210724.10979: ** class attrib_edit_Controller
class attrib_edit_Controller:

    """A per-commander class that manages attribute editing."""

    #@+others
    #@+node:tbrown.20091009210724.10981: *3* __init__ & reloadSettings (attrib_edit_Controller)
    def __init__(self, c):

        self.c = c
        c.attribEditor = self
        self.pname = "_attrib_edit_frame"  # used to tag out panel
        self.reloadSettings()
        self.attrPaths = set()  # set of tuples (getter-class, path)
        self.handlers = [
           ('select3', self.updateEditor),
        ]
        for i in self.handlers:
            g.registerHandler(i[0], i[1])
        # 'body' or 'tab' mode
        # self.guiMode = c.config.getString('attrib-edit-placement') or 'tab'
        self.guiMode = 'tab'
        # body mode in not compatible with nested_splitter, causes hard crash
        self.holder: Any
        if self.guiMode == 'body':
            self.holder = QtWidgets.QSplitter(Orientation.Vertical)
            self.holder.setMinimumWidth(300)
            parent = c.frame.top.leo_body_frame.parent()
            self.holder.addWidget(c.frame.top.leo_body_frame)
            parent.addWidget(self.holder)
            self.parent = self.holder
        elif self.guiMode == 'tab':
            self.parent = QtWidgets.QFrame()
            self.holder = QtWidgets.QHBoxLayout()
            self.parent.setLayout(self.holder)
            c.frame.log.createTab('Attribs', widget=self.parent)

    def reloadSettings(self):
        c = self.c
        c.registerReloadSettings(self)
        active = c.config.getData('attrib_edit_active_modes') or []
        self.getsetters = []
        for i in AttributeGetter.implementations:
            s = i(c)
            self.getsetters.append([s, (s.name() in active)])
        if not active:
            self.getsetters[0][1] = True  # turn on the first one
    #@+node:tbrown.20091009210724.10983: *3* __del__
    def __del__(self):
        for i in self.handlers:
            g.unregisterHandler(i[0], i[1])
    #@+node:tbrown.20091009210724.11210: *3* initForm
    def initForm(self):
        """set up self.form, the blank form layout before adding edit widgets"""
        self.editors = []

        w = self.holder

        for i in w.parent().findChildren(QtCore.QObject):
            if i.objectName() == self.pname:
                i.hide()
                i.deleteLater()

        pnl = QtWidgets.QFrame()
        pnl.setObjectName(self.pname)
        self.form = QtWidgets.QFormLayout()
        self.form.setVerticalSpacing(0)
        pnl.setLayout(self.form)
        pnl.setAutoFillBackground(True)
        w.addWidget(pnl)
    #@+node:tbrown.20091009210724.11047: *3* updateEditor
    def updateEditor(self, tag, k):
        """update edit panel when new node selected"""

        if k['c'] != self.c:
            return  # not our problem

        self.updateEditorInt()
    #@+node:tbrown.20091028100922.1493: *3* updateEditorInt
    def updateEditorInt(self):

        c = self.c

        self.initForm()
        for attr in self.getAttribs():
            class_, name, value, path, type_, readonly = attr
            if readonly:
                self.form.addRow(QtWidgets.QLabel(name), QtWidgets.QLabel(str(value)))

            else:
                editor = editWatcher(c, c.currentPosition().v, class_, name, value, path, type_)
                self.editors.append(editor)

                self.form.addRow(QtWidgets.QLabel(name), editor.widget())
    #@+node:tbrown.20091103080354.1405: *3* recSearch (not used)
    # def JUNKrecSearch(self, d, path, ans):
        # """recursive search of tree of dicts for values whose
        # key path is like [*][*][*]['_edit'][*] or
        # [*][*][*]['_edit']['_int'][*]

        # Modifies list ans
        # """
        # for k in d:
            # if isinstance(d[k], dict):
                # if k not in ('_edit', '_view'):
                    # self.recSearch(d[k], path+[k], ans)
                # else:
                    # # k == '_edit' or '_view'
                    # for ek in d[k]:
                        # if ek in self.typeMap:
                            # # ek is '_int' or similar
                            # type_ = self.typeMap[ek]
                            # for ekt in d[k][ek]:
                                # ans.append((ekt, d[k][ek][ekt], tuple(path+['_edit',ek,ekt]),
                                    # type_, k != '_edit'))
                        # else:
                            # ans.append((ek, d[k][ek], tuple(path+['_edit',ek]), str, k != '_edit'))
    #@+node:tbrown.20091103080354.1406: *3* getAttribs
    def getAttribs(self, v=None):
        """Return a list of tuples describing editable uAs.

        (class, name, value, path, type, readonly)


        e.g.

        (class, 'created', '2009-09-23', ('stickynotes','_edit','created'), str, False),
        (class, 'cars', 2, ('inventory','_edit','_int','cars'), int, False)

        Changes should be written back to
        v.uA['stickynotes']['_edit']['created'] and
        v.uA['inventory']['_edit']['_int']['cars'] respectively
        """

        ans = []
        if not v:
            v = self.c.currentPosition().v

        for getter, isOn in self.getsetters:

            if not isOn:
                continue

            ans.extend(getter.getAttribs(v))


        for ns in ans:
            self.attrPaths.add((ns[0], ns[1], ns[3]))  # class, name, path

        return ans
    #@+node:tbrown.20091029101116.1413: *3* addAttrib
    def addAttrib(self, attrib):

        attrib[0].setAttrib(self.c.currentPosition().v, attrib[2], '')
    #@+node:tbrown.20091029101116.1414: *3* delAttrib
    def delAttrib(self, attrib):

        attrib[0].delAttrib(self.c.currentPosition().v, attrib[2])
    #@+node:tbrown.20091029101116.1424: *3* scanAttribs
    def scanAttribs(self):
        """scan all of c for attrbutes"""
        for v in self.c.all_unique_nodes():
            self.getAttribs(v)  # updates internal list of attribs
        g.es("%d attributes found" % len(self.attrPaths))
    #@+node:tbrown.20091011151836.14788: *3* createAttrib
    def createAttrib(self, event=None, readonly=False):

        ans = []

        for getter, isOn in self.getsetters:
            if not isOn:
                continue

            if getter.helpCreate() is True:
                ans.append(getter)
            else:
                g.es("For '%s' attributes:\n  %s" % (getter.name(), getter.helpCreate()))

        if len(ans) > 1:
            g.error('Eror: more than one attribute type (%s) active' %
            ', '.join([i.name() for i in ans]))
        elif ans:
            ans[0].createAttrib(self.c.currentPosition().v, gui_parent=self.parent)
            self.updateEditorInt()
            self.c.currentPosition().v.setDirty()
            self.c.redraw()
    #@+node:tbrown.20091028131637.1358: *3* manageAttrib
    def manageAttrib(self):

        attribs = [(i[0], i[1], i[3]) for i in self.getAttribs()]
        dat = []
        for attr in self.attrPaths:
            txt = attr[0].longDescrip(attr[2])
            active = attr in attribs
            dat.append([txt, active, attr])
        if not dat:
            g.es('No attributes seen (yet)')
            return
        dat.sort(key=lambda x: x[0])

        res: QWidget
        res = ListDialog(self.parent, "Enter attribute path",
            "Enter path to attribute (space separated words)", dat)
        res.exec()
        if res.result() == DialogCode.Rejected:
            return

        # check for deletions
        for i in dat:
            if i[2] in attribs and not i[1]:
                res = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Question,
                    "Really delete attributes?", "Really delete attributes?",
                    QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel, self.parent)
                if res.exec() == QtWidgets.QMessageBox.Cancel:
                    return
                break

        # apply changes
        for i in dat:
            if i[2] in attribs and not i[1]:
                self.delAttrib(i[2])
            elif i[2] not in attribs and i[1]:
                self.addAttrib(i[2])

        self.updateEditorInt()
        self.c.redraw()

    #@+node:tbrown.20091103080354.1415: *3* manageModes
    def manageModes(self):

        modes = [[i[0].name(), i[1]] for i in self.getsetters]

        res = ListDialog(self.parent, "Enter attribute path",
            "Enter path to attribute (space separated words)",
            modes)

        res.exec()
        if res.result() == DialogCode.Rejected:
            return

        for n, i in enumerate(modes):
            self.getsetters[n][1] = i[1]

        self.updateEditorInt()
    #@-others
#@+node:tbrown.20091029101116.1415: ** cmd_Modes (attrib_edit_Controller)
@g.command('attrib-edit-modes')
def cmd_Modes(event):
    c = event.get('c')
    c.attribEditor.manageModes()
#@+node:tbrown.20091103080354.1413: ** cmd_Manage (attrib_edit_Controller)
@g.command('attrib-edit-manage')
def cmd_Manage(event):
    c = event.get('c')
    c.attribEditor.manageAttrib()
#@+node:tbrown.20091029101116.1419: ** cmd_Create (attrib_edit_Controller)
@g.command('attrib-edit-create')
def cmd_Create(event):
    c = event.get('c')
    c.attribEditor.createAttrib()
#@+node:tbrown.20091029101116.1421: ** cmd_CreateReadonly (attrib_edit_Controller)
def Xcmd_CreateReadonly(c):
    c.attribEditor.createAttrib(readonly=True)
#@+node:tbrown.20091029101116.1426: ** cmd_Scan (attrib_edit_Controller)
@g.command('attrib-edit-scan')
def cmd_Scan(event):
    c = event.get('c')
    c.attribEditor.scanAttribs()
#@-others
#@@language python
#@@tabwidth -4
#@-leo
