#@+leo-ver=5-thin
#@+node:tbrown.20171028115144.6: * @file ../plugins/editpane/editpane.py
"""Support for the edit-pane-test-open command and window."""
#@+<<editpane imports>>
#@+node:tbrown.20171028115438.1: ** << editpane imports >>
from collections import defaultdict
from importlib import import_module
import os
from leo.core.leoQt import QtWidgets
from leo.core.leoQt import QAction, ContextMenuPolicy, Orientation, Policy
from leo.core.leoQt import WidgetAttribute  # 2347
from leo.core import leoGlobals as g
from leo.core import signal_manager
from leo.plugins.editpane.clicky_splitter import ClickySplitter
#@-<<editpane imports>>
#@+others
#@+node:tbrown.20171028115438.2: ** DBG
def DBG(text):
    """DBG - temporary debugging function

    :param str text: text to print
    """
    print(f"LEP: {text}")
#@+node:tbrown.20171028115438.3: ** edit_pane_test_open
def edit_pane_test_open(event):
    """Make a command for opening the editpane in free_layout.

    This is just for testing / demoing, and will be removed eventually.
    """
    c = event['c']

    if not hasattr(c, '__edit_pane_test'):
        c.__edit_pane_test = True


        class MinimalDemoProvider:

            def ns_provides(self):
                return [("Demo editor", "__demo_provider_minimal_slider")]

            def ns_provide(self, id_):
                if id_ == "__demo_provider_minimal_slider":
                    w = LeoEditPane(c=c, mode='split')
                    return w
                return None

            def ns_provider_id(self):
                return "__demo_provider_minimal"

        c.free_layout.get_top_splitter().register_provider(MinimalDemoProvider())

    s = c.free_layout.get_top_splitter()
    s.open_window("__demo_provider_minimal_slider")
#@+node:tbrown.20180207103918.1: ** edit_pane_csv
def edit_pane_csv(event):
    from leo.plugins.nested_splitter import NestedSplitter
    c = event['c']
    w = c.frame.body.widget
    while not isinstance(w, NestedSplitter):
        w = w.parent()
    w.insert(-1, LeoEditPane(c=c, show_control=False, lep_type='EDITOR-CSV'))
#@+node:tbrown.20171028115438.4: ** class LeoEditPane
class LeoEditPane(QtWidgets.QWidget):
    """
    Leo node body editor / viewer
    """
    #@+others
    #@+node:tbrown.20171028115438.5: *3* __init__
    def __init__(self,
        c=None, p=None, mode='edit', show_head=True, show_control=True,
        update=True, recurse=False, lep_type=None, *args, **kwargs):
        """LeoEditPane.__init__ - bind to outline

        :param outline c: outline to bind to
        :param position p: initial position
        :param str mode: 'edit' | 'view' | 'split'
        :param bool show_head: show header
        :param bool show_control: show controls
        :param bool update: update view pane when text changes
        :param bool recurse: render view pane recursively
        :param str or [str] lep_type: 'EDITOR' or ['EDITOR', 'HTML']
        :param list *args: pass through
        :param dict **kwargs: pass through
        """
        DBG("__init__ LEP")
        super().__init__(*args, **kwargs)
        self.setAttribute(WidgetAttribute.WA_DeleteOnClose)  # #2347.

        lep_type = lep_type or ['EDITOR', 'TEXT']
        if isinstance(lep_type, str):
            lep_type = [lep_type]
        if len(lep_type) < 2:
            lep_type.append('TEXT')

        self.modules = []  # modules we collect widgets from
        self.widget_classes = []  # collected widgets
        self.widget_for = defaultdict(lambda: [])  # widget by class.lep_type

        self.c = c
        p = p or self.c.p
        self.mode = mode

        self.gnx = p.gnx

        self.load_modules()

        self._build_layout(
            show_head=show_head,
            show_control=show_control,
            update=update,
            recurse=recurse,
        )

        self.track = self.cb_track.isChecked()
        self.update_flag = self.cb_update.isChecked()
        self.recurse = self.cb_recurse.isChecked()
        self.goto = self.cb_goto.isChecked()

        for type_ in lep_type:
            self.set_widget(lep_type=type_)

        self.set_mode(self.mode)

        self.handlers = [
            ('select1', self._before_select),
            ('select2', self._after_select),
            # ('bodykey2', self._after_body_key),
        ]
        self._register_handlers()
    #@+node:tbrown.20171028115438.6: *3* _add_checkbox
    def _add_checkbox(self, text, state_changed, tooltip, checked=True,
        enabled=True, button_label=True):
        """
        _add_checkbox - helper to add a checkbox

        :param str text: Text for label
        :param function state_changed: callback for state_changed signal
        :param bool checked: initially checked?
        :param bool enabled: initially enabled?
        :param bool button_label: label should be a button for single shot use
        :return: QCheckBox
        """
        cbox = QtWidgets.QCheckBox('' if button_label else text, self)
        self.control.layout().addWidget(cbox)
        btn = None
        if button_label:
            btn = QtWidgets.QPushButton(text, self)
            self.control.layout().addWidget(btn)

            def cb(checked, cbox=cbox, state_changed=state_changed):
                state_changed(cbox.isChecked(), one_shot=True)

            btn.clicked.connect(cb)
            btn.setToolTip(tooltip)
        cbox.setChecked(checked)
        cbox.setEnabled(enabled)
        cbox.stateChanged.connect(state_changed)
        cbox.setToolTip(tooltip)
        self.control.layout().addItem(QtWidgets.QSpacerItem(20, 0))
        return cbox
    #@+node:tbrown.20171028115438.7: *3* _add_frame
    def _add_frame(self):
        """_add_frame - add a widget with a layout as a hiding target.

        i.e. a container we can hide / show easily"""
        w = QtWidgets.QWidget(self)
        self.layout().addWidget(w)
        w.setSizePolicy(Policy.Expanding, Policy.Maximum)
        w.setLayout(QtWidgets.QHBoxLayout())
        w.layout().setContentsMargins(0, 0, 0, 0)
        w.layout().setSpacing(0)
        return w
    #@+node:tbrown.20171028115438.8: *3* _after_body_key
    def _after_body_key(self, v):
        """_after_body_key - after Leo selects another node

        FIXME: although class EditCommandsClass-->insert &
        delete...-->selfInsertCommand() implies that bodykey2 should fire
        after all keys, it doesn't seem to fire after \n, backspace, delete
        etc., so the viewer gets out of date for those keys. The simplest
        fix would be a new bodychanged2 hook.

        :param str tag: handler name ("bodykey2")
        :param dict keywords: c, p, etc.
        :return: None
        """
        p = self.c.vnode2position(v)
        DBG("after body key")
        self.update_position(p)
    #@+node:tbrown.20171028115438.9: *3* _after_select
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
    #@+node:tbrown.20171028115438.10: *3* _before_select
    def _before_select(self, tag, keywords):
        """_before_select - before Leo selects another node

        :param str tag: handler name ("select1")
        :param dict keywords: c, new_p, old_p
        :return: None
        """

        c = keywords['c']
        if c != self.c:
            return None

        # currently nothing to do here, focusOut in widget takes care
        # of any text updates

        # BUT keyboard driven position change might need some action here
        # BUT then again, textChanged in widget is probably sufficient

        DBG("before select")

        return None
    #@+node:tbrown.20171028115438.11: *3* _find_gnx_node
    def _find_gnx_node(self, gnx):
        """Return the first position having the given gnx."""
        if self.c.p.gnx == gnx:
            return self.c.p
        for p in self.c.all_unique_positions():
            if p.v.gnx == gnx:
                return p
        g.es("Edit/View pane couldn't find node")
        return None
    #@+node:tbrown.20171028115438.12: *3* _register_handlers (editpane.py)
    def _register_handlers(self):
        """_register_handlers - attach to Leo signals
        """
        DBG("\nregister handlers")
        for hook, handler in self.handlers:
            g.registerHandler(hook, handler)

        signal_manager.connect(self.c, 'body_changed', self._after_body_key)
    #@+node:tbrown.20171028115438.13: *3* _build_layout
    def _build_layout(
        self, show_head=True, show_control=True, update=True, recurse=False):
        """build_layout - build layout
        """
        DBG("build layout")
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        # header
        self.header = self._add_frame()
        self.toggle_ctrl = QtWidgets.QPushButton("-", self)
        self.header.layout().addWidget(self.toggle_ctrl)
        self.line_edit = QtWidgets.QLineEdit(self)
        self.header.layout().addWidget(self.line_edit)
        self.header.layout().addStretch(1)
        self.btn_close = QtWidgets.QPushButton("X", self)
        self.btn_close.clicked.connect(lambda checked: self.close())
        self.header.layout().addWidget(self.btn_close)

        # controls
        self.control = self._add_frame()
        # checkboxes
        txt = ",\ncheck to do this always"
        self.cb_track = self._add_checkbox("Track", self.change_track,
            "Track the node selected in the tree" + txt)
        self.cb_goto = self._add_checkbox("Goto", self.change_goto,
            "Make the tree go to this node" + txt)
        self.cb_update = self._add_checkbox("Update", self.change_update,
            "Update view to match changed node" + txt)
        self.cb_recurse = self._add_checkbox("Recurse", self.change_recurse,
            "Recursive view" + txt, checked=recurse)
        # mode menu
        btn = self.btn_mode = QtWidgets.QPushButton("Mode", self)
        self.control.layout().addWidget(btn)
        btn.setContextMenuPolicy(ContextMenuPolicy.CustomContextMenu)
        btn.customContextMenuRequested.connect(  # right click
            lambda pnt: self.mode_menu())
        btn.clicked.connect(  # or left click
            lambda checked: self.mode_menu())

        # misc. menu
        btn = self.control_menu_button = QtWidgets.QPushButton("More\u25BE", self)
        self.control.layout().addWidget(btn)
        btn.setContextMenuPolicy(ContextMenuPolicy.CustomContextMenu)
        btn.customContextMenuRequested.connect(  # right click
            lambda pnt: self.misc_menu())
        btn.clicked.connect(  # or left click
            lambda checked: self.misc_menu())

        # padding
        self.control.layout().addItem(QtWidgets.QSpacerItem(0, 0, hPolicy=Policy.Expanding))

        # content
        self.splitter = ClickySplitter(self)
        self.splitter.setOrientation(Orientation.Vertical)
        self.layout().addWidget(self.splitter)
        self.edit_frame = self._add_frame()
        self.splitter.addWidget(self.edit_frame)
        self.view_frame = self._add_frame()
        self.splitter.addWidget(self.view_frame)

        self.control_visible = show_control
        self.header_visible = show_head
        self.show()

        # debug
        self.line_edit.setText("test")

        # toggle control visibility
        self.toggle_ctrl.clicked.connect(
            lambda checked: self.control.setVisible(not self.control.isVisible()))
    #@+node:tbrown.20171028115438.14: *3* header_visible
    @property
    def header_visible(self):
        return self.header.isVisible()
    #@+node:tbrown.20171028115438.15: *3* header_visible
    @header_visible.setter
    def header_visible(self, state):
        self.header.setVisible(state)
    #@+node:tbrown.20171028115438.16: *3* control_visible
    @property
    def control_visible(self):
        return self.control.isVisible()
    #@+node:tbrown.20171028115438.17: *3* control_visible
    @control_visible.setter
    def control_visible(self, state):
        self.control.setVisible(state)
    #@+node:tbrown.20171028115438.18: *3* change_goto
    def change_goto(self, state, one_shot=False):
        self.goto = one_shot or bool(state)
        self.state_changed()
        self.goto = bool(state)
    #@+node:tbrown.20171028115438.19: *3* change_recurse
    def change_recurse(self, state, one_shot=False):
        self.recurse = one_shot or bool(state)
        self.state_changed()
        self.recurse = bool(state)
    #@+node:tbrown.20171028115438.20: *3* change_track
    def change_track(self, state, one_shot=False):
        self.track = one_shot or bool(state)
        if self.track:
            p = self.c.p
            self.new_position(p)
        self.track = bool(state)
    #@+node:tbrown.20171028115438.21: *3* change_update
    def change_update(self, state, one_shot=False):
        self.update_flag = one_shot or bool(state)
        if self.update_flag:
            p = self.get_position()
            if p is not None:
                self.new_position(p)
        self.update_flag = bool(state)
    #@+node:tbrown.20171028115438.22: *3* close
    def close(self):
        """close - clean up
        """
        do_close = QtWidgets.QWidget.close(self)
        if do_close:
            signal_manager.disconnect_all(self)
            DBG("unregister handlers\n")
            for hook, handler in self.handlers:
                g.unregisterHandler(hook, handler)
        return do_close
    #@+node:tbrown.20171028115438.23: *3* edit_widget_focus
    def edit_widget_focus(self):
        """edit_widget_focus - edit widget got focus"""
        if self.goto:
            self.goto_node()
        self.update_position(self.get_position())
    #@+node:tbrown.20171028115438.24: *3* get_position
    def get_position(self):
        """get_position - get current position"""
        return self._find_gnx_node(self.gnx)
    #@+node:tbrown.20171028115438.25: *3* goto_node
    def goto_node(self):
        """goto_node - goto node being edited / viewed"""
        p = self.get_position()
        if p and p != self.c.p:
            self.c.selectPosition(p)
    #@+node:tbrown.20171028115438.26: *3* load_modules
    def load_modules(self):
        """load_modules - load modules to find widgets
        """
        module_dir = os.path.dirname(__file__)
        names = [os.path.splitext(i) for i in os.listdir(module_dir)
                 if os.path.isfile(os.path.join(module_dir, i))]
        # FIXME: sort 'plain' to start of list for devel.
        names.sort(key=lambda x: (not x[0].startswith('plain'), x[0]))
        modules = []
        for name in [i[0] for i in names if i[1].lower() == '.py']:
            try:
                modules.append(import_module('leo.plugins.editpane.' + name))
                DBG(f"Loaded module: {name}")
            except ImportError as e:
                DBG(
                    f"{e.__class__.__name__}: "
                    f"Module not loaded (unmet dependencies?): {name}")
        for module in modules:
            for key in dir(module):
                value = getattr(module, key)
                if hasattr(value, 'lep_type') and value not in self.widget_classes:
                    if module not in self.modules:
                        self.modules.append(module)
                    self.widget_classes.append(value)
                    self.widget_for[value.lep_type].append(value)
    #@+node:tbrown.20171028115438.27: *3* misc_menu
    def misc_menu(self):
        """build menu on Action button"""
        # info needed to separate edit and view widgets in self.widget_classes
        name_test_current = [
            ("Editor", lambda x: x.lep_type == 'EDITOR', self.edit_widget.__class__),
            ("Viewer", lambda x: x.lep_type != 'EDITOR', self.view_widget.__class__),
        ]

        menu = QtWidgets.QMenu()
        for name, is_one, current in name_test_current:
            # list Editor widgets, then Viewer widgets
            for widget_class in [i for i in self.widget_classes if is_one(i)]:

                def cb(checked, widget_class=widget_class):
                    self.set_widget(widget_class=widget_class)

                act = QAction(f"{name}: {widget_class.lep_name}", self)
                act.setCheckable(True)
                act.setChecked(widget_class == current)
                act.triggered.connect(cb)
                menu.addAction(act)

        button = self.control_menu_button
        point = button.position().toPoint()  # Qt6 documentation is wrong.
        global_point = button.mapToGlobal(point)
        menu.exec(global_point)
    #@+node:tbrown.20171028115438.28: *3* mode_menu
    def mode_menu(self):
        """build menu on Action button"""
        menu = QtWidgets.QMenu()
        for mode in 'edit', 'view', 'split':
            act = QAction(mode.title(), self)

            def cb(checked, self=self, mode=mode):
                self.set_mode(mode)

            act.triggered.connect(cb)
            act.setCheckable(True)
            act.setChecked(mode == self.mode)
            menu.addAction(act)

        button = self.btn_mode
        point = button.position().toPoint()  # Qt6 documentation is wrong.
        global_point = button.mapToGlobal(point)
        menu.exec(global_point)

    #@+node:tbrown.20171028115438.29: *3* new_position
    def new_position(self, p):
        """new_position - update editor and view for new Leo position

        :param position p: the new position
        """
        if self.track:
            self.gnx = p.gnx
        else:
            p = self.get_position()

        self.new_position_edit(p)
        self.new_position_view(p)
    #@+node:tbrown.20171028115438.30: *3* new_position_edit
    def new_position_edit(self, p):
        """new_position_edit - update editor for new position

        WARNING: unlike new_position() this uses p without regard
                 for self.track

        :param position p: the new position
        """

        DBG("new edit position")
        if self.mode != 'view':
            self.edit_widget.new_text(p.b)
    #@+node:tbrown.20171028115438.31: *3* new_position_view
    def new_position_view(self, p):
        """new_position_view - update viewer for new position

        WARNING: unlike new_position() this uses p without regard
                 for self.track

        :param position p: the new position
        """
        DBG("new view position")
        if self.mode != 'edit':
            if self.recurse:
                text = g.getScript(self.c, p, useSelectedText=False, useSentinels=False)
            else:
                text = p.b
            self.view_widget.new_text(text)
    #@+node:tbrown.20171028115438.32: *3* text_changed
    def text_changed(self, new_text):
        """text_changed - node text changed by this LEP's editor"""

        # Update p.b
        p = self.get_position()
        signal_manager.lock(self)
        p.b = new_text  # triggers 'body_changed' signal from c
        self.update_position_view(p)  # as we're ignoring signals
        signal_manager.unlock(self)
    #@+node:tbrown.20171028115438.33: *3* update_position
    def update_position(self, p):
        """update_position - update editor and view for current Leo position

        :param position p: the new position
        """
        if self.track:
            our_p = self.c.p
            assert self.gnx == our_p.gnx
        else:
            our_p = self.get_position()

        if p.gnx == our_p.gnx:
            self.update_position_edit(p)
            if self.update_flag:
                self.update_position_view(p)
    #@+node:tbrown.20171028115438.34: *3* update_position_edit
    def update_position_edit(self, p):
        """update_position_edit - update editor for current position

        WARNING: unlike update_position() this uses p without regard
                 for self.track

        :param position p: the position to update to
        """

        DBG("update edit position")
        if self.mode != 'view':
            self.edit_widget.update_text(p.b)
    #@+node:tbrown.20171028115438.35: *3* update_position_view
    def update_position_view(self, p):
        """update_position_view - update viewer for current position

        WARNING: unlike update_position() this uses p without regard
                 for self.track

        :param position p: the position to update to
        """

        DBG("update view position")
        if self.update_flag and self.mode != 'edit':
            if self.recurse:
                text = g.getScript(self.c, p, useSelectedText=False, useSentinels=False)
            else:
                text = p.b
            self.view_widget.update_text(text)
    #@+node:tbrown.20171028115438.36: *3* render
    def render(self, checked):
        pass
    #@+node:tbrown.20171028115438.37: *3* set_widget
    def set_widget(self, widget_class=None, lep_type='TEXT'):
        """set_widget - set edit or view widget

        :param QWidget widget: widget to use
        """

        if widget_class is None:
            widget_class = [i for i in self.widget_classes if i.lep_type == lep_type][0]
        if hasattr(
            widget_class, 'lep_type') and widget_class.lep_type.startswith('EDITOR'):
            frame = self.edit_frame
            attr = 'edit_widget'
            update = self.new_position_edit
        else:
            frame = self.view_frame
            attr = 'view_widget'
            update = self.new_position_view
        widget = widget_class(c=self.c, lep=self)

        setattr(self, attr, widget)
        for i in reversed(range(frame.layout().count())):
            frame.layout().itemAt(i).widget().setParent(None)
        frame.layout().addWidget(widget)
        update(self.get_position())
    #@+node:tbrown.20171028115438.38: *3* set_mode
    def set_mode(self, mode):
        """set_mode - change mode edit / view / split

        :param str mode: mode to change to

        """
        self.mode = mode
        self.btn_mode.setText(f"{mode.title()}\u25BE")
        self.state_changed()
    #@+node:tbrown.20171028115438.39: *3* state_changed
    def state_changed(self):
        """state_changed - control state has changed
        """
        if self.goto and self.get_position() != self.c.p:
            self.goto_node()

        if self.mode == 'edit':
            self.edit_frame.show()
            self.view_frame.hide()
        elif self.mode == 'view':
            self.edit_frame.hide()
            self.view_frame.show()
        else:
            self.edit_frame.show()
            self.view_frame.show()

        self.update_position(self.c.p)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
