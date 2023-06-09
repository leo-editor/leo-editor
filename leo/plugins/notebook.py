#@+leo-ver=5-thin
#@+node:ville.20120604212857.4215: * @file ../plugins/notebook.py
""" QML Notebook

Edit several nodes at once, in a pannable "notebook" view.

Use <Alt-x>nb-<tab> to see the list of commands.
"""
from typing import Any
from leo.core import leoGlobals as g
from leo.core.leoQt import QtCore, QtDeclarative, QtGui
#
# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.

controllers: dict[str, Any] = {}  # keys are c.hash(), values are NavControllers

#@+others
#@+node:ville.20120604212857.4219: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    ok = g.app.gui.guiName() == "qt"
    if ok:
        g.registerHandler('after-create-leo-frame', onCreate)
        g.plugin_signon(__name__)
    return ok
#@+node:ville.20120604212857.4231: ** onCreate
def onCreate(tag, keys):
    """notebook.py onCreate"""
    global controllers
    c = keys.get('c')
    if c:
        h = c.hash()
        nb = controllers.get(h)
        if not nb:
            controllers[h] = NbController(c)
#@+node:ville.20120604212857.4227: ** class ModelWrapper
class ModelWrapper:
    #@+others
    #@+node:ville.20120604212857.4228: *3* __init__
    def __init__(self, fieldlist):
        """Ctor for ModelWrapper class."""
        self.rolenames = rn = {}
        self.roleids = ri = {}
        for n, f in enumerate(fieldlist):
            rid = n + 100
            rn[rid] = f
            ri[f] = rid
        self.model = mo = QtGui.QStandardItemModel()
        try:
            mo.setRoleNames(rn)
        except AttributeError:
            pass
    #@+node:ville.20120604212857.4229: *3* mkitem
    def mkitem(self, d):
        """ dict with field->value """
        si = QtGui.QStandardItem()
        for k, v in d.items():
            rid = self.roleids[k]
            si.setData(v, rid)
        return si
    #@-others
#@+node:ville.20120604212857.4237: ** class NbController
class NbController:
    #@+others
    #@+node:ville.20120604212857.4241: *3* __init__
    def __init__(self, c):
        """Ctor for NbController class."""
        self.c = c
        self.gnxcache = {}
        self.mw = ModelWrapper(["h", "b", "gnx", "level", "style"])
        try:
            # pylint: disable=import-error, no-name-in-module
            from PyQt5.QtQuick import QQuickView
            self.view = view = QQuickView()
        except Exception:  #1746.
            self.view = view = QtDeclarative.QDeclarativeView()
        ctx = view.rootContext()

        @g.command("nb-all")
        def nb_all_f(event):
            self.add_all_nodes()
            self.view.show()

        @g.command("nb-subtree")
        def nb_subtree_f(event):
            p = self.c.p
            self.add_subtree(p)
            self.view.show()

        ctx.setContextProperty("nodesModel", self.mw.model)
        path = g.os_path_join(g.computeLeoDir(), 'plugins', 'qmlnb', 'qml', 'leonbmain.qml')
        view.setSource(QtCore.QUrl(path))
        mode = view.SizeRootObjectToView
        view.setResizeMode(mode)
        # Display the user interface and allow the user to interact with it.
        view.hide()
        view.setGeometry(100, 100, 800, 600)
        c.dummy = view
    #@+node:ville.20120604212857.4239: *3* add_all_nodes
    def add_all_nodes(self):
        self.mw.model.clear()
        for p in self.c.all_positions():
            self.addNode(p)
    #@+node:ville.20120604212857.4240: *3* add_subtree
    def add_subtree(self, pos):
        self.mw.model.clear()
        for p in pos.self_and_subtree():
            self.addNode(p)

    #@+node:ville.20120604212857.4238: *3* addNode
    def addNode(self, p, styling=None):
        if styling is None:
            styling = {}
        v = p.v
        d = {
            "h": v.h,
            "b": v.b,
            "gnx": v.gnx,
            "level": p.level(),
        }
        d.update(styling)
        self.gnxcache[v.gnx] = v
        si = self.mw.mkitem(d)
        self.mw.model.appendRow(si)
    #@-others
#@-others
#@-leo
