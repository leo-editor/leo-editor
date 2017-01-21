import leo.core.leoGlobals as g
from leo.core.leoQt import QtCore, QtGui, QtWidgets, QtConst

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

        for arg in 'c', 'p', 'show_head', 'show_control', 'mode':
            if arg in kwargs:
                del kwargs[arg]

        QtWidgets.QWidget.__init__(self, *args, **kwargs)

        self._build_layout(mode=mode, show_head=show_head, show_control=show_control)
        self._register_handlers()

        self.track   = self.cb_track.isChecked()
        self.update  = self.cb_update.isChecked()
        self.edit    = self.cb_edit.isChecked()
        self.split   = self.cb_split.isChecked()
        self.recurse = self.cb_recurse.isChecked()

        self.new_position(p)
    def _add_checkbox(self, text, state_changed, checked=True, enabled=True):
        """
        _add_checkbox - helper to add a checkbox

        :param str text: Text for label
        :param function state_changed: callback for state_changed signal
        :param bool checked: initially checked?
        :param bool enabled: initially enabled?
        :return: QCheckBox
        """
        cbox = QtWidgets.QCheckBox(text, self)
        self.control_layout.addWidget(cbox)
        cbox.setChecked(checked)
        cbox.setEnabled(enabled)
        cbox.stateChanged.connect(state_changed)
        return cbox

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

    def _register_handlers(self):
        """_register_handlers - attach to Leo signals
        """
        DBG("\nregister handlers")
        g.registerHandler('select1', self._before_select)
        g.registerHandler('select2', self._after_select)

    def _build_layout(self, mode='edit', show_head=True, show_control=True):
        """build_layout - build layout
        """
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        # header
        self.header_layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.header_layout)
        self.header = QtWidgets.QLineEdit(self)
        self.header_layout.addWidget(self.header)

        # controls
        self.control_layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.control_layout)
        # checkboxes
        self.cb_track = self._add_checkbox("Track", self.change_track)
        self.cb_update = self._add_checkbox("Update", self.change_update)
        self.cb_edit = self._add_checkbox("Edit", self.change_edit)
        self.cb_split = self._add_checkbox("Split", self.change_split, checked=False)
        self.cb_recurse = self._add_checkbox("Recurse", self.change_recurse)
        # render now
        self.btn_render = QtWidgets.QPushButton("Render", self)
        self.control_layout.addWidget(self.btn_render)
        self.btn_render.clicked.connect(self.render)
        # menu
        self.control_menu_button = QtWidgets.QPushButton(u"More\u2026", self)
        self.control_layout.addWidget(self.control_menu_button)
        # padding
        self.control_layout.addItem(
            QtWidgets.QSpacerItem(0, 0, hPolicy=QtWidgets.QSizePolicy.Expanding))

        # content
        self.splitter = QtWidgets.QSplitter(self)
        self.layout.addWidget(self.splitter)
        self.editor = QtWidgets.QTextEdit(self)
        self.splitter.addWidget(self.editor)

        self.show()

        # debug
        self.header.setText("test")

    def change_edit(self, state):
        self.edit = bool(state)
    def change_recurse(self, state):
        self.recurse = bool(state)
    def change_split(self, state):
        self.split = bool(state)
        # always edit if split
        self.cb_edit.setEnabled(not state)
        if state:
            self.cb_edit.setChecked(True)
    def change_track(self, state):
        self.track = bool(state)
    def change_update(self, state):
        self.update = bool(state)
    def close(self):
        """close - clean up
        """
        do_close = QtWidgets.QWidget.close(self)
        if do_close:
            DBG("unregister handlers\n")
            g.unregisterHandler('select1', self._before_select)
            g.unregisterHandler('select2', self._after_select)
        return do_close
    def new_position(self, p):
        """new_position - update editor and view for new Leo position

        :param position p: the new position
        """

        if self.edit or self.split:
            self.new_position_edit(p)
        if not self.edit or self.split:
            self.new_position_view(p)
    def new_position_edit(self, p):
        """new_position_edit - update editor for new position

        :param position p: the new position
        """

        pass
    def new_position_view(self, p):
        """new_position_view - update viewer for new position

        :param position p: the new position
        """

        pass
    def render(self, checked):
        pass


