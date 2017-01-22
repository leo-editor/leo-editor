import leo.core.leoGlobals as g
from leo.core.leoQt import QtCore, QtGui, QtWidgets, QtConst

from leo.core.editpane import plaintextview

if g.isPython3:
    from importlib import reload
def DBG(text):
    """DBG - temporary debugging function

    :param str text: text to print
    """
    print("LEP: \033[33m%s\033[39m" % text)
class LeoEditPane(QtWidgets.QWidget):
    """
    Leo node body editor / viewer
    """
    def __init__(self, *args, **kwargs):
        """__init__ - bind to outline

        :param outline c: outline to bind to
        """
        self.c = kwargs['c']
        p = kwargs.get('p', self.c.p)
        mode = kwargs.get('mode', 'edit')
        show_head = kwargs.get('show_head', True)
        show_control = kwargs.get('show_control', True)
        recurse = kwargs.get('recurse', False)
        split = kwargs.get('split', False)
        for arg in 'c', 'p', 'show_head', 'show_control', 'mode', 'recurse', 'split':
            if arg in kwargs:
                del kwargs[arg]

        QtWidgets.QWidget.__init__(self, *args, **kwargs)

        self.gnx = p.gnx

        self._build_layout(
            mode=mode,
            show_head=show_head,
            show_control=show_control,
            recurse=recurse,
        )

        self.handlers = [
            ('select1', self._before_select),
            ('select2', self._after_select),
            ('bodykey2', self._after_body_key),
        ]
        self._register_handlers()

        self.track   = self.cb_track.isChecked()
        self.update  = self.cb_update.isChecked()
        self.edit    = self.cb_edit.isChecked()
        self.split   = self.cb_split.isChecked()
        self.recurse = self.cb_recurse.isChecked()

        reload(plaintextview)
        self.edit_widget = None
        self.view_widget = plaintextview.LEP_PlainTextView(lep=self, c=self.c)
        self.view_frame.layout().addWidget(self.view_widget)

        self.new_position(p)
    def _add_checkbox(self, text, state_changed, tooltip, checked=True, enabled=True):
        """
        _add_checkbox - helper to add a checkbox

        :param str text: Text for label
        :param function state_changed: callback for state_changed signal
        :param bool checked: initially checked?
        :param bool enabled: initially enabled?
        :return: QCheckBox
        """
        cbox = QtWidgets.QCheckBox(text, self)
        self.control.layout().addWidget(cbox)
        cbox.setChecked(checked)
        cbox.setEnabled(enabled)
        cbox.stateChanged.connect(state_changed)
        cbox.setToolTip(tooltip)
        self.control.layout().addItem(QtWidgets.QSpacerItem(20, 0))
        return cbox

    def _add_frame(self):
        """_add_frame - add a widget with a layout as a hiding target"""
        w = QtWidgets.QWidget(self)
        self.layout().addWidget(w)
        w.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        w.setLayout(QtWidgets.QHBoxLayout())
        w.layout().setContentsMargins(0, 0, 0, 0)
        w.layout().setSpacing(0)
        return w
    def _after_body_key(self, tag, keywords):
        """_after_select - after Leo selects another node

        :param str tag: handler name ("bodykey2")
        :param dict keywords: c, p, etc.
        :return: None
        """

        c = keywords['c']
        if c != self.c:
            return None

        if self.update:
            self.new_position(keywords['p'])

        return None
    def _after_select(self, tag, keywords):
        """_after_select - after Leo selects another node

        :param str tag: handler name ("select2")
        :param dict keywords: c, new_p, old_p
        :return: None
        """

        c = keywords['c']
        if c != self.c:
            return None

        DBG("after select")

        if self.track:
            self.new_position(keywords['new_p'])

        return None
    def _before_select(self, tag, keywords):
        """_before_select - before Leo selects another node

        :param str tag: handler name ("select1")
        :param dict keywords: c, new_p, old_p
        :return: None
        """

        c = keywords['c']
        if c != self.c:
            return None

        DBG("before select")

        return None

    def _find_gnx_node(self, gnx):
        '''Return the first position having the given gnx.'''
        for p in self.c.all_unique_positions():
            if p.v.gnx == gnx:
                return p
        g.es("Edit/View pane couldn't find node")
        return None
    def _register_handlers(self):
        """_register_handlers - attach to Leo signals
        """
        DBG("\nregister handlers")
        for hook, handler in self.handlers:
            g.registerHandler(hook, handler)

    def _build_layout(self, mode='edit', show_head=True, show_control=True, split=False, recurse=False):
        """build_layout - build layout
        """
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        # header
        self.header = self._add_frame()
        self.line_edit = QtWidgets.QLineEdit(self)
        self.header.layout().addWidget(self.line_edit)

        # controls
        self.control = self._add_frame()
        # checkboxes
        self.cb_track = self._add_checkbox("Track", self.change_track,
            "Track the node selected in the tree")
        self.cb_edit = self._add_checkbox("Edit", self.change_edit,
            "Toggle edit / view mode")
        self.cb_split = self._add_checkbox("Split", self.change_split, 
            "Split edit and view", checked=split)
        self.cb_update = self._add_checkbox("Update", self.change_update,
            "Update view to match changed node")
        self.cb_recurse = self._add_checkbox("Recurse", self.change_recurse, 
            "Recursive view", checked=recurse)
        # render now
        self.btn_render = QtWidgets.QPushButton("Render", self)
        self.control.layout().addWidget(self.btn_render)
        self.btn_render.clicked.connect(self.render)
        # menu
        self.control_menu_button = QtWidgets.QPushButton(u"More\u2026", self)
        self.control.layout().addWidget(self.control_menu_button)
        # padding
        self.control.layout().addItem(
            QtWidgets.QSpacerItem(0, 0, hPolicy=QtWidgets.QSizePolicy.Expanding))

        # content
        self.splitter = QtWidgets.QSplitter(self)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.layout().addWidget(self.splitter)
        self.edit_frame = self._add_frame()
        self.splitter.addWidget(self.edit_frame)
        self.view_frame = self._add_frame()
        self.splitter.addWidget(self.view_frame)

        if mode not in ('edit', 'split'):
            self.edit_frame.hide()
            self.cb_edit.setChecked(False)
        else:  # avoid hiding both parts
            if mode not in ('view', 'split'):
                self.view_frame.hide()
                self.cb_edit.setChecked(False)

        self.show()

        # debug
        self.line_edit.setText("test")

    def change_edit(self, state):
        self.edit = bool(state)
    def change_recurse(self, state):
        self.recurse = bool(state)
        self.state_changed()
    def change_split(self, state):
        self.split = bool(state)
        # always edit if split
        self.cb_edit.setEnabled(not state)
        if state:
            self.cb_edit.setChecked(True)
    def change_track(self, state):
        self.track = bool(state)
        if self.track:
            p = self.c.p
            self.new_position(p)
    def change_update(self, state):
        self.update = bool(state)
        if self.update:
            p = self._find_gnx_node(self.gnx)
            if p is not None:
                self.new_position(p)
    def close(self):
        """close - clean up
        """
        do_close = QtWidgets.QWidget.close(self)
        if do_close:
            DBG("unregister handlers\n")
            for hook, handler in self.handlers:
                g.unregisterHandler(hook, handler)
        return do_close
    def new_position(self, p):
        """new_position - update editor and view for new Leo position

        ALSO CALLED for updates, when not really a new position

        :param position p: the new position
        """
        if self.track:
            self.gnx = p.gnx
        else:
            p = self._find_gnx_node(self.gnx)

        if self.edit or self.split:
            self.new_position_edit(p)
        if not self.edit or self.split:
            self.new_position_view(p)
    def new_position_edit(self, p):
        """new_position_edit - update editor for new position

        :param position p: the new position
        """

        DBG("new edit position")
    def new_position_view(self, p):
        """new_position_view - update viewer for new position

        :param position p: the new position
        """

        DBG("new view position")
        self.view_widget.new_position(p)

    def render(self, checked):
        pass


    def state_changed(self):
        """state_changed - control state has changed
        """

        self.new_position(self.c.p)
