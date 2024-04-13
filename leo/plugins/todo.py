#@+leo-ver=5-thin
#@+node:tbrown.20090119215428.2: * @file ../plugins/todo.py
#@+<< todo docstring >>
#@+node:tbrown.20090119215428.3: ** << todo docstring >>
""" Provides to-do list and simple task management.

This plugin adds time required, progress and priority settings for nodes. With
the @project tag a branch can display progress and time required with dynamic
hierarchical updates.

The Task Tab
============

The plugin creates a "Task" Tab in the log pane.  It looks like this:

    .. image:: ../Icons/cleo/LeoTaskTab.png

Along the top are icons that you can associate with nodes.
Just click on the icon: it will appear on the presently selected node.

Next are a set of fields that allow you to associate **due dates** and
**completion times** with nodes. The @setting @data todo_due_date_offsets lists
date offsets, +n -n days from now, or <n >n to subtract / add n days to existing
date.

Clicking on the Button named "Menu" reveals submenus.

For full details, see http://leo.zwiki.org/Tododoc

Icons
=====

The plugin uses icons in the leo/Icons/cleo folder. These icons are generated
from the file cleo_icons.svg in the same directory. You may replace the PNG
images with any others you wish.

@Settings
=========

Most setting documented elsewhere (http://leo.zwiki.org/Tododoc).

todo_compact_interface
  Hide one line of the interface to preserve original height
todo_icon_location
  "beforeHeadline", "afterHeadline" might also work
todo_due_date_offsets
  A list of offsets like "+7" or "<3" or ">5", for 7 days from now,
  3 days earlier, or 5 days later
todo_calendar_n
  Number of months to display at once in calendar pop up, default 3
todo_calendar_cols
  Number of columns to use when displaying multiple months in
  in calendar pop up, default 3 - extra rows are used as needed to
  display `todo_calendar_n` months.


"""


#@-<< todo docstring >>
# TNB: derived from cleo.py.

#@+<< todo imports & annotations >>
#@+node:tbrown.20090119215428.4: ** << todo imports & annotations >>
from __future__ import annotations
from collections.abc import Callable
import os
import re
import datetime
import time
from typing import Any, Iterable, Optional, Union
from typing import TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.core.leoQt import Qt, QtCore, QtGui, QtWidgets, uic
from leo.core.leoQt import Checked, Unchecked

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent as Event
    from leo.core.leoNodes import Position, VNode
    Icon = Any  # QtGui.QIcon
    Menu = Any
    Priority = Union[int, str]

# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.
#@-<< todo imports & annotations >>

NO_TIME = datetime.date(3000, 1, 1)

#@+others
#@+node:tbrown.20090119215428.6: ** init (todo.py)
def init() -> bool:
    """Return True if the plugin has loaded successfully."""
    name = g.app.gui.guiName()
    if name != "qt":
        if name not in ('browser', 'curses', 'nullGui'):
            print('todo.py plugin not loading because gui is not Qt')
        return False
    g.registerHandler('after-create-leo-frame', onCreate)
    # can't use before-create-leo-frame because Qt dock's not ready
    g.plugin_signon(__name__)
    g.tree_popup_handlers.append(popup_entry)
    return True
#@+node:tbrown.20090119215428.7: ** onCreate
def onCreate(tag: str, key: dict) -> None:

    c = key.get('c')
    todoController(c)
#@+node:tbrown.20090630144958.5318: ** popup_entry (todo.py)
def popup_entry(c: Cmdr, p: Position, menu: Menu) -> None:

    if getattr(c, 'cleo', None):  # #2856.
        c.cleo.addPopupMenu(c, p, menu)
#@+node:tbrown.20090119215428.8: ** class todoQtUI(QWidget)
if g.app.gui.guiName() == "qt":

    class todoQtUI(QtWidgets.QWidget):  # type:ignore
        #@+others
        #@+node:ekr.20111118104929.10204: *3* ctor (todo.py)
        def __init__(self, owner: Any, logTab: bool = True) -> None:

            self.owner = owner
            super().__init__()
            uiPath = g.os_path_join(g.app.leoDir, 'plugins', 'ToDo.ui')
            #
            # change dir to get themed icons, needed for uic resources
            # These are icons for todo UI, not the tree.
            theme = g.app.config.getString('color-theme')
            if theme:
                testPath = g.os_path_join(
                    g.app.homeLeoDir, 'themes', theme, 'Icons', 'cleo')
                if g.os_path_exists(testPath):
                    iconPath = g.os_path_dirname(testPath)
                else:
                    testPath = g.os_path_join(
                        g.app.loadDir, '..', 'themes', theme, 'Icons', 'cleo')
                    if g.os_path_exists(testPath):
                        iconPath = g.os_path_dirname(testPath)
                    else:
                        iconPath = g.os_path_join(g.app.leoDir, 'Icons')
            else:
                iconPath = g.os_path_join(g.app.leoDir, 'Icons')
            os.chdir(iconPath)
            form_class, base_class = uic.loadUiType(uiPath)
            if logTab:
                self.owner.c.frame.log.createTab('Task', widget=self)
            self.UI = form_class()
            self.UI.setupUi(self)
            u = self.UI
            o = self.owner
            self.menu = QtWidgets.QMenu()
            self.populateMenu(self.menu, o)
            u.butMenu.setMenu(self.menu)

            u.butHelp.clicked.connect(lambda checked: o.showHelp())
            u.butClrProg.clicked.connect(lambda checked: o.progress_clear())
            u.butClrTime.clicked.connect(lambda checked: o.clear_time_req())
            u.butPriClr.clicked.connect(lambda checked: o.priority_clear())
            # if live update is too slow change valueChanged(*) to editingFinished()
            u.spinTime.valueChanged.connect(
                lambda v: o.set_time_req(val=u.spinTime.value()))
            u.spinProg.valueChanged.connect(
                lambda v: o.set_progress(val=u.spinProg.value()))

            u.dueDateEdit.dateChanged.connect(
                lambda v: o.set_due_date(val=u.dueDateEdit.date()))
            u.dueTimeEdit.timeChanged.connect(
                lambda v: o.set_due_time(val=u.dueTimeEdit.time()))

            u.nxtwkDateEdit.dateChanged.connect(
                lambda v: o.set_due_date(val=u.nxtwkDateEdit.date(), field='nextworkdate'))
            u.nxtwkTimeEdit.timeChanged.connect(
                lambda v: o.set_due_time(val=u.nxtwkTimeEdit.time(), field='nextworktime'))

            u.dueDateToggle.stateChanged.connect(
                lambda v: o.set_due_date(val=u.dueDateEdit.date(), mode='check'))
            u.dueTimeToggle.stateChanged.connect(
                lambda v: o.set_due_time(val=u.dueTimeEdit.time(), mode='check'))
            u.nxtwkDateToggle.stateChanged.connect(
                lambda v: o.set_due_date(val=u.nxtwkDateEdit.date(), mode='check', field='nextworkdate'))
            u.nxtwkTimeToggle.stateChanged.connect(
                lambda v: o.set_due_time(val=u.nxtwkTimeEdit.time(), mode='check', field='nextworktime'))

            for but in ["butPri1", "butPri6", "butPriChk", "butPri2",
                "butPri4", "butPri5", "butPri8", "butPri9", "butPri0",
                "butPriToDo", "butPriXgry", "butPriBang", "butPriX",
                "butPriQuery", "butPriBullet", "butPri7",
                "butPri3"
            ]:
                w = getattr(u, but)
                # w.property() seems to give QVariant in python 2.x and int in 3.x!?
                try:
                    pri = int(w.property('priority'))
                except(TypeError, ValueError):
                    try:
                        pri, ok = w.property('priority').toInt()
                    except(TypeError, ValueError):
                        pri = -1

                def setter(pri: int = pri) -> None:
                    o.setPri(pri)

                w.clicked.connect(lambda checked, setter=setter: setter())

            offsets = self.owner.c.config.getData('todo_due_date_offsets')
            if not offsets:
                offsets = (
                    '+7 +0 +1 +2 +3 +4 +5 +6 +10 +14 +21 +28 +42 +60 +90 +120 +150 '
                    '>7 <7 <14 >14 <28 >28'
                ).split()
            self.date_offset_default = int(offsets[0].strip('>').replace('<', '-'))
            offsets = sorted(set(offsets), key=lambda x: (x[0], int(x[1:].strip('>').replace('<', '-'))))
            u.dueDateOffset.addItems(offsets)
            u.dueDateOffset.setCurrentIndex(self.date_offset_default)

            self.UI.dueDateOffset.activated.connect(
                lambda v: o.set_date_offset(field='duedate'))

            u.nxtwkDateOffset.addItems(offsets)
            u.nxtwkDateOffset.setCurrentIndex(self.date_offset_default)

            self.UI.nxtwkDateOffset.activated.connect(
                lambda v: o.set_date_offset(field='nextworkdate'))

            self.setDueDate = self.make_func(self.UI.dueDateEdit,
                self.UI.dueDateToggle, 'setDate',
                datetime.date.today() + datetime.timedelta(self.date_offset_default))

            self.setDueTime = self.make_func(self.UI.dueTimeEdit,
                self.UI.dueTimeToggle, 'setTime',
                datetime.datetime.now().time())

            self.setNextWorkDate = self.make_func(self.UI.nxtwkDateEdit,
                self.UI.nxtwkDateToggle, 'setDate',
                datetime.date.today() + datetime.timedelta(self.date_offset_default))

            self.setNextWorkTime = self.make_func(self.UI.nxtwkTimeEdit,
                self.UI.nxtwkTimeToggle, 'setTime',
                datetime.datetime.now().time())

            self.UI.butDetails.clicked.connect(
                lambda checked: self.UI.frmDetails.setVisible(not self.UI.frmDetails.isVisible()))

            if self.owner.c.config.getBool("todo-compact-interface"):
                self.UI.frmDetails.setVisible(False)

            self.UI.butNext.clicked.connect(
                lambda checked: self.owner.c.selectVisNext())
            self.UI.butNextTodo.clicked.connect(
                lambda checked: self.owner.find_todo())
            self.UI.butApplyDueOffset.clicked.connect(
                lambda checked: o.set_date_offset(field='duedate'))
            self.UI.butApplyOffset.clicked.connect(
                lambda checked: o.set_date_offset(field='nextworkdate'))

            n = g.app.config.getInt("todo-calendar-n")
            cols = g.app.config.getInt("todo-calendar-cols")
            if n or cols:
                self.UI.dueDateEdit.calendarWidget().build(n or 3, cols or 3)
                self.UI.nxtwkDateEdit.calendarWidget().build(n or 3, cols or 3)
        #@+node:ekr.20111118104929.10203: *3* make_func
        def make_func(self, edit: Any, toggle: Any, method: Any, default: Any) -> Callable:

            def func(
                value: Any,
                edit: Any = edit,
                toggle: Any = toggle,
                method: Any = method,
                default: Any = default,
                self: Any = self,
            ) -> None:

                edit.blockSignals(True)
                toggle.blockSignals(True)
                if value:
                    getattr(edit, method)(value)
                    # edit.setEnabled(True)
                    toggle.setChecked(True)
                else:
                    getattr(edit, method)(default)
                    toggle.setChecked(False)
                edit.blockSignals(False)
                toggle.blockSignals(False)

            return func
        #@+node:ekr.20111118104929.10205: *3* populateMenu
        @staticmethod
        def populateMenu(menu: Menu, o: Any) -> None:
            menu.addAction('Find next ToDo', o.find_todo)
            m = menu.addMenu("Priority")
            m.addAction('Priority Sort', o.priSort)
            m.addAction('Due Date Sort', o.dueSort)
            m.addAction('Next Work Date Sort', lambda: o.dueSort(field='nextwork'))
            m.addAction('Clear Descendant Due Dates', o.dueClear)
            m.addAction('Mark children todo', o.childrenTodo)
            m.addAction('Show distribution', o.showDist)
            m.addAction('Redistribute', o.reclassify)
            m = menu.addMenu("Time")
            m.addAction('Show times', lambda: o.show_times(show=True))
            m.addAction('Hide times', lambda: o.show_times(show=False))
            m.addAction('Re-calc. derived times', o.local_recalc)
            m.addAction('Clear derived times', o.local_clear)
            m = menu.addMenu("Misc.")
            m.addAction('Hide all Todo icons', lambda: o.loadAllIcons(clear=True))
            m.addAction('Show all Todo icons', o.loadAllIcons)
            m.addAction('Delete Todo from node', o.clear_all)
            m.addAction('Delete Todo from subtree', lambda: o.clear_all(recurse=True))
            m.addAction('Delete Todo from all', lambda: o.clear_all(all=True))
        #@+node:ekr.20111118104929.10207: *3* setProgress
        def setProgress(self, prgr: Any) -> None:
            self.UI.spinProg.blockSignals(True)
            self.UI.spinProg.setValue(prgr)
            self.UI.spinProg.blockSignals(False)
        #@+node:ekr.20111118104929.10208: *3* setTime
        def setTime(self, timeReq: Any) -> None:
            self.UI.spinTime.blockSignals(True)
            self.UI.spinTime.setValue(timeReq)
            self.UI.spinTime.blockSignals(False)
        #@-others

#@+node:tbrown.20090119215428.9: ** class todoController
class todoController:
    """A per-commander class that manages tasks."""

    #@+<< todoController data >>
    #@+node:tbrown.20090119215428.10: *3* << todoController data >>
    priorities: dict[int, dict[str, str]] = {
      1: {'long': 'Urgent', 'short': '1', 'icon': 'pri1.png'},
      2: {'long': 'Very High', 'short': '2', 'icon': 'pri2.png'},
      3: {'long': 'High', 'short': '3', 'icon': 'pri3.png'},
      4: {'long': 'Medium', 'short': '4', 'icon': 'pri4.png'},
      5: {'long': 'Low', 'short': '5', 'icon': 'pri5.png'},
      6: {'long': 'Very Low', 'short': '6', 'icon': 'pri6.png'},
      7: {'long': 'Sometime', 'short': '7', 'icon': 'pri7.png'},
      8: {'long': 'Level 8', 'short': '8', 'icon': 'pri8.png'},
      9: {'long': 'Level 9', 'short': '9', 'icon': 'pri9.png'},
     10: {'long': 'Level 0', 'short': '0', 'icon': 'pri0.png'},
     19: {'long': 'To do', 'short': 'o', 'icon': 'chkboxblk.png'},
     20: {'long': 'Bang', 'short': '!', 'icon': 'bngblk.png'},
     21: {'long': 'Cross', 'short': 'X', 'icon': 'xblk.png'},
     22: {'long': '(cross)', 'short': 'x', 'icon': 'xgry.png'},
     23: {'long': 'Query', 'short': '?', 'icon': 'qryblk.png'},
     24: {'long': 'Bullet', 'short': '-', 'icon': 'bullet.png'},
    100: {'long': 'Done', 'short': 'D', 'icon': 'chkblk.png'},
    }

    todo_priorities = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 19

    _date_fields = ['created', 'date', 'duedate', 'nextworkdate', 'prisetdate']
    _time_fields = ['duetime', 'nextworktime', 'time']
    _datetime_fields = _date_fields + _time_fields
    #@-<< todoController data >>

    #@+others
    #@+node:tbrown.20090119215428.11: *3* __init__ & helpers (todoController)
    def __init__(self, c: Cmdr) -> None:
        """ctor for todoController class."""
        self.c = c
        c.cleo = self
        self.donePriority = 100
        self.menuicons: dict[Priority, Icon] = {}  # menu icon cache
        self.recentIcons: list[Icon] = []
        self.redrawLevels = 0
        self._widget_to_style = None  # see updateStyle()
        self.reloadSettings()
        self.handlers = [
           ("close-frame", self.close),
           ('select3', self.updateUI),
           ('save2', self.loadAllIcons),
           ('idle', self.updateStyle),
        ]
        # chdir so the Icons can be located, needed for uic resources
        owd = os.getcwd()
        os.chdir(g.os_path_join(g.app.loadDir, '..', 'plugins'))
        self.ui = todoQtUI(self)
        os.chdir(owd)
        for i in self.handlers:
            g.registerHandler(i[0], i[1])
        self.loadAllIcons()
        # correct spinTime suffix:
        self.ui.UI.spinTime.setSuffix(" " + self.time_name)
        # #1591: patch labels if necessary.
        self.patch_1591()
    #@+node:tbrown.20090119215428.12: *4* reloadSettings (todoController)
    def reloadSettings(self) -> None:
        c = self.c
        c.registerReloadSettings(self)
        self.time_name = c.config.getString('todo-time-name') or 'days'
        self.icon_location = c.config.getString('todo-icon-location') or 'beforeHeadline'
        self.prog_location = c.config.getString('todo-prog-location') or 'beforeHeadline'
        self.icon_order = c.config.getString('todo-icon-order') or 'pri-first'
    #@+node:ekr.20201111052557.1: *4* todo_c.patch_1591
    def patch_1591(self) -> None:
        """
        A workaround for #1591.

        Add labels and tooltips for all buttons.
        """
        # Patch the buttons only if the pyqt version is greater than 5.12.
        from leo.core.leoQt import qt_version
        size = QtCore.QSize(16, 16)
        qt_version = [int(z) for z in qt_version.split('.')]  # type:ignore
        if qt_version[1] <= 12:  # type:ignore
            return
        ui = self.ui.UI

        for i in range(10):
            button = getattr(ui, f"butPri{i}")
            path = g.finalize_join(g.app.loadDir, '..', 'Icons', "cleo", f"pri{i}.png")
            button.setIcon(QtGui.QIcon(path))
            button.setIconSize(size)
            button.setToolTip(f"Priority {i}")

        table = (
                # Alternate priorities...
                ('butPriChk', 'chkblk.png', 'Check Mark'),
                ('butPriToDo', 'chkboxblk.png', 'Box Mark'),
                ('butPriX', 'xblk.png', 'Black X'),
                ('butPriXgry', 'xgry.png', 'Gray X'),
                ('butPriBang', 'bngblk.png', 'Exclamation Point'),
                ('butPriQuery', 'qryblk.png', 'Question Mark'),
                ('butPriBullet', 'bullet.png', 'Bullet'),
                ('butPriClr', 'edit-clear.png', 'Clear Priority'),
                # Other labels...
                ('butDetails', 'document-save.png', 'Toggle Details'),
                ('butNext', 'down.png', 'Next Node'),
                ('butNextTodo', 'bottom.png', 'Next To Do'),
                ('butClrTime', 'edit-clear.png', 'Clear Required Time'),
                ('butClrProg', 'edit-clear.png', 'Clear Progress')
            )

        for attr, icon, tooltip in table:
            button = getattr(ui, attr)
            path = g.finalize_join(g.app.loadDir, '..', 'Icons', "cleo", icon)
            button.setIcon(QtGui.QIcon(path))
            button.setIconSize(size)
            button.setToolTip(tooltip)
    #@+node:tbrown.20090522142657.7894: *3* __del__
    def __del__(self) -> None:
        for i in self.handlers:
            g.unregisterHandler(i[0], i[1])
    #@+node:tbnorth.20170925093004.1: *3* _date
    def _date(self, d: str) -> Optional[datetime.date]:
        """_date - convert a string to a date

        :param str d: date to convert
        :return: datetime.date
        """
        if not d.strip():
            return None  # Was ''
        return datetime.datetime.strptime(d.split('T')[0], "%Y-%m-%d").date()

    def _time(self, d: str) -> Optional[datetime.time]:
        """_time - convert a string to a time

        :param str d: time to convert
        :return: datetime.time
        """
        if not d.strip():
            return None  # Was ''
        return datetime.datetime.strptime(d, "%H:%M:%S.%f").time()
    #@+node:tbrown.20090630144958.5319: *3* addPopupMenu
    def addPopupMenu(self, c: Cmdr, p: Position, menu: Menu) -> None:

        def rnd(x: float) -> str:
            return re.sub('.0$', '', '%.1f' % x)

        taskmenu = menu.addMenu("Task")
        submenu = taskmenu.addMenu("Status")
        iconlist = [(menu, i) for i in self.recentIcons]
        iconlist.extend([(submenu, i) for i in self.priorities])
        for m, i in iconlist:
            icon = self.menuicon(i)
            a = m.addAction(icon, self.priorities[i]["long"])
            a.setIconVisibleInMenu(True)

            def icon_cb(checked: Any, pri: int = i) -> None:
                self.setPri(pri)

            a.triggered.connect(icon_cb)
        submenu = taskmenu.addMenu("Progress")
        for i in range(11):
            icon = self.menuicon(10 * i, progress=True)
            a = submenu.addAction(icon, "%d%%" % (i * 10))
            a.setIconVisibleInMenu(True)

            def progress_cb(checked: bool, prog: int = i) -> None:
                self.set_progress(val=10 * prog)

            a.triggered.connect(progress_cb)
        prog = self.getat(p.v, 'progress')
        if isinstance(prog, int):
            a = taskmenu.addAction("(%d%% complete)" % prog)
            a.setIconVisibleInMenu(True)
            a.enabled = False
        time_ = self.getat(p.v, 'time_req')
        if isinstance(time_, float):
            if isinstance(prog, int):
                f = prog / 100.
                a = taskmenu.addAction("(%s+%s=%s %s)" % (
                    rnd(f * time_),
                    rnd((1. - f) * time_),
                    rnd(time_),
                    self.time_name))
            else:
                a = taskmenu.addAction("(%s %s)" % (rnd(time_), self.time_name))
            a.enabled = False
        todoQtUI.populateMenu(taskmenu, self)
    #@+node:tbrown.20090630144958.5320: *3* menuicon
    def menuicon(self, pri: int, progress: bool = False) -> Icon:
        """return icon from cache, placing it there if needed"""
        key: Priority = f"prog-{pri}" if progress else pri
        # mypy doesn't know (and can't be told) that priorities[key]["icon"] is a string.
        fn: str = 'prg%03d.png' % pri if progress else self.priorities[key]["icon"]  # type:ignore
        if key not in self.menuicons:
            # use getImageImage because it's theme aware
            fn = g.os_path_join('cleo', fn)
            self.menuicons[key] = QtGui.QIcon(g.app.gui.getImageImage(fn))
        return self.menuicons[key]
    #@+node:tbrown.20090119215428.13: *3* redrawer
    # mypy complains about missing 'self' arg.
    # pylint: disable=no-self-argument
    def redrawer(fn: Callable) -> Callable:  # type:ignore
        """decorator for methods which create the need for a redraw"""

        def todo_redrawer_callback(self: Any, *args: Any, **kargs: Any) -> Any:

            self.redrawLevels += 1
            try:
                ans = fn(self, *args, **kargs)
            finally:
                self.redrawLevels -= 1
                if self.redrawLevels == 0:
                    self.updateUI()
            return ans

        return todo_redrawer_callback
    #@+node:tbrown.20090119215428.14: *3* projectChanger
    # mypy complaints there is no 'self' argument.
    def projectChanger(fn: Callable) -> Callable:  # type:ignore
        """decorator for methods which change projects"""

        # pylint: disable=no-self-argument
        def project_changer_callback(self, *args: Any, **kargs: Any) -> Any:  # type:ignore
            ans = fn(self, *args, **kargs)
            self.update_project()
            return ans

        return project_changer_callback
    #@+node:tbrown.20090119215428.15: *3* loadAllIcons
    @redrawer
    def loadAllIcons(self, tag: str = None, k: int = None, clear: bool = None) -> None:
        """Load icons to represent cleo state"""
        for p in self.c.all_positions():
            self.loadIcons(p, clear=clear)
    #@+node:tbrown.20090119215428.16: *3* loadIcons (todo.py)
    @redrawer
    def loadIcons(self, p: Position, clear: bool = False) -> None:

        c = self.c
        com = c.editCommands
        allIcons = com.getIconList(p.v)
        icons = [i for i in allIcons if 'cleoIcon' not in i]
        if self.icon_order == 'pri-first':
            iterations = ['priority', 'progress', 'duedate']
        else:
            iterations = ['progress', 'priority', 'duedate']
        if clear:
            iterations = []
        today = datetime.date.today()
        for which in iterations:
            if which == 'priority':
                pri = self.getat(p.v, 'priority')
                if pri:
                    pri = int(pri)
                if pri in self.priorities:
                    com.appendImageDictToList(icons, g.os_path_join('cleo', self.priorities[pri]['icon']),
                        2, on='vnode', cleoIcon='1', where=self.icon_location)
                        # Icon location defaults to 'beforeIcon' unless cleo_icon_location global defined.
                        # Example: @strings[beforeIcon,beforeHeadline] cleo_icon_location = beforeHeadline
            elif which == 'progress':
                prog = self.getat(p.v, 'progress')
                # pylint: disable=literal-comparison
                if prog != '':
                    prog = int(prog or 0)
                    use = prog // 10 * 10
                    use = 'prg%03d.png' % use
                    com.appendImageDictToList(icons, g.os_path_join('cleo', use),
                        2, on='vnode', cleoIcon='1', where=self.prog_location)
            elif which == 'duedate':
                duedate = self.getat(p.v, 'duedate')
                nextworkdate = self.getat(p.v, 'nextworkdate')
                icondate = min(duedate or NO_TIME, nextworkdate or NO_TIME)
                if icondate != NO_TIME:
                    if icondate < today:
                        icon = "date_past.png"
                    elif icondate == today:
                        icon = "date_today.png"
                    else:
                        icon = "date_future.png"
                    # Append the icon to the icons list.
                    com.appendImageDictToList(icons,
                        g.os_path_join('cleo', icon),
                        2,
                        on='vnode',
                        cleoIcon='1',
                        where=self.prog_location)
        # Set the p.v.u for the icons.
        com.setIconList(p, icons)
        p.v.updateIcon()  # #2870.
    #@+node:tbrown.20090119215428.17: *3* close
    def close(self, tag: str, key: Any) -> None:
        "unregister handlers on closing commander"

        if self.c != key['c']:
            return  # not our problem
        for i in self.handlers:
            g.unregisterHandler(i[0], i[1])
    #@+node:tbrown.20090119215428.18: *3* showHelp
    def showHelp(self) -> None:
        g.es('Check the Plugins menu Todo entry')
    #@+node:tbrown.20090119215428.19: *3* attributes...
    #@+at
    # annotate was the previous name of this plugin, which is why the default values
    # for several keyword args is 'annotate'.
    #@+node:tbrown.20090119215428.20: *4* delUD
    def delUD(self, node: VNode, udict: str = "annotate") -> None:
        """ Remove our dict from the node"""
        if (hasattr(node, "unknownAttributes") and
            udict in node.unknownAttributes
        ):
            del node.unknownAttributes[udict]
    #@+node:tbrown.20090119215428.21: *4* hasUD
    def hasUD(self, node: VNode, udict: str = "annotate") -> bool:
        """ Return True if the node has an UD."""
        return (
            hasattr(node, "unknownAttributes")
            and udict in node.unknownAttributes
            and isinstance(node.unknownAttributes.get(udict), dict)
        )
    #@+node:tbrown.20090119215428.22: *4* getat
    def getat(self, node: VNode, attrib: str) -> Any:  # Hard to annotate.
        "new attribute getter"
        if (hasattr(node, 'unknownAttributes') and
            "annotate" in node.unknownAttributes and
            isinstance(node.unknownAttributes["annotate"], dict) and
            attrib in node.unknownAttributes["annotate"]
        ):
            x: Any = node.unknownAttributes["annotate"][attrib]
            if attrib in self._date_fields and isinstance(x, str):
                x = self._date(x)
            if attrib in self._time_fields and isinstance(x, str):
                x = self._time(x)
            return x
        return 9999 if attrib == "priority" else ''
    #@+node:tbrown.20090119215428.23: *4* testDefault
    def testDefault(self, attrib: str, val: Any) -> bool:
        "return true if val is default val for attrib"
        # pylint: disable=consider-using-ternary
        return attrib == "priority" and val == 9999 or val == ""
    #@+node:tbrown.20090119215428.24: *4* setat
    def setat(self, node: VNode, attrib: Any, val: Any) -> None:
        "new attribute setter"

        if attrib in self._datetime_fields and isinstance(val,
            (datetime.date, datetime.time, datetime.datetime)):
            val = val.isoformat()

        if 'annotate' in node.u and 'src_unl' in node.u['annotate']:

            if (not hasattr(node, '_cached_src_vnode') or
                not node._cached_src_vnode
            ):
                src_unl = node.u['annotate']['src_unl']
                c1 = self.c
                p1 = c1.vnode2position(node)
                c2, p2 = self.unl_to_pos(src_unl, p1)
                if p2 is None:
                    g.es("Failed to access '%s' for attribute update." % src_unl)
                else:
                    node._cached_src_c = c2
                    node._cached_src_vnode = p2.v

            # if the above succeeded in getting the required attributes
            if (hasattr(node, '_cached_src_vnode') and
                node._cached_src_vnode
            ):
                node._cached_src_c.cleo.setat(node._cached_src_vnode, attrib, val)
                op = node._cached_src_c.vnode2position(node._cached_src_vnode)
                node._cached_src_c.cleo.loadIcons(op)
                node._cached_src_c.cleo.updateUI(k={'c': node._cached_src_c})
                node._cached_src_c.setChanged()

        isDefault = self.testDefault(attrib, val)

        if (not hasattr(node, 'unknownAttributes') or
            "annotate" not in node.unknownAttributes or
            not isinstance(node.unknownAttributes["annotate"], dict)
        ):
            # dictionary doesn't exist
            if isDefault:
                return  # don't create dict. for default value
            if not hasattr(node, 'unknownAttributes'):  # node has no unknownAttributes
                node.unknownAttributes = {}
                node.unknownAttributes["annotate"] = {}
            elif ("annotate" not in node.unknownAttributes or
                 not isinstance(node.unknownAttributes["annotate"], dict)
            ):
                node.unknownAttributes["annotate"] = {}
            # node.unknownAttributes["annotate"]['created'] = datetime.datetime.now()
            node.unknownAttributes["annotate"][attrib] = val
            return

        # dictionary exists
        if (attrib not in node.unknownAttributes["annotate"] or
            node.unknownAttributes["annotate"][attrib] != val
        ):
            self.c.setChanged()
            node.setDirty()

        node.unknownAttributes["annotate"][attrib] = val

        if isDefault:  # check if all default, if so drop dict.
            self.dropEmpty(node, dictOk=True)
    #@+node:tbrown.20090119215428.25: *4* dropEmpty
    def dropEmpty(self, node: VNode, dictOk: bool = False) -> bool:

        if (dictOk or
            hasattr(node, 'unknownAttributes') and
            "annotate" in node.unknownAttributes and
            isinstance(node.unknownAttributes["annotate"], dict)
        ):
            isDefault = True
            for ky, vl in node.unknownAttributes["annotate"].items():
                if not self.testDefault(ky, vl):
                    isDefault = False
                    break
            if isDefault:  # no non-defaults seen, drop the whole cleo dictionary
                del node.unknownAttributes["annotate"]
                self.c.setChanged()
                return True
        return False
    #@+node:tbrown.20090119215428.26: *4* safe_del
    def safe_del(self, d: dict[str, Any], k: Any) -> None:
        "delete a key from a dict. if present"
        if k in d:
            del d[k]
    #@+node:tbrown.20090119215428.27: *3* drawing...
    #@+node:tbrown.20090119215428.29: *4* clear_all
    @redrawer
    def clear_all(self, recurse: bool = False, all: bool = False) -> None:

        what: Iterable
        if all:
            what = self.c.all_positions()
        elif recurse:
            what = self.c.currentPosition().self_and_subtree()
        else:
            what = iter([self.c.currentPosition()])

        for p in what:
            self.delUD(p.v)
            self.loadIcons(p)
            self.show_times(p)

    #@+node:tbrown.20090119215428.30: *3* Progress/time/project...
    #@+node:tbrown.20090119215428.31: *4* progress_clear
    @redrawer
    @projectChanger
    def progress_clear(self, v: VNode = None) -> None:

        self.setat(self.c.currentPosition().v, 'progress', '')
    #@+node:tbrown.20090119215428.32: *4* set_progress
    @redrawer
    @projectChanger
    def set_progress(self, p: Position = None, val: Any = None) -> None:  # Hard to annotate.
        if p is None:
            p = self.c.currentPosition()
        v = p.v

        if val is None:
            return

        self.setat(v, 'progress', val)
    #@+node:tbrown.20090119215428.33: *4* set_time_req
    @redrawer
    @projectChanger
    def set_time_req(self, p: Position = None, val: Any = None) -> None:  # Hard to annotate.
        if p is None:
            p = self.c.currentPosition()
        v = p.v
        if val is None:
            return
        self.setat(v, 'time_req', val)
        if self.getat(v, 'progress') == '':
            self.setat(v, 'progress', 0)
    #@+node:tbrown.20090119215428.34: *4* show_times
    @redrawer
    def show_times(self, p: Position = None, show: bool = False) -> None:

        def rnd(x: float) -> str:
            return re.sub('.0$', '', '%.1f' % x)

        if p is None:
            p = self.c.currentPosition()

        for nd in p.self_and_subtree():
            nd.h = re.sub(' <[^>]*>$', '', nd.headString())
            tr = self.getat(nd.v, 'time_req')
            pr = self.getat(nd.v, 'progress')
            try:
                pr = float(pr)
            except Exception:
                pr = ''
            if tr != '' or pr != '':
                ans = ' <'
                if tr != '':
                    if pr == '' or pr == 0 or pr == 100:
                        ans += rnd(tr) + ' ' + self.time_name
                    else:
                        ans += '%s+%s=%s %s' % (
                            rnd(pr / 100. * tr),
                            rnd((1 - pr / 100.) * tr),
                            rnd(tr), self.time_name
                        )
                    if pr != '':
                        ans += ', '
                if pr != '':
                    ans += rnd(pr) + '%'  # pr may be non-integer if set by recalc_time
                ans += '>'

                if show:
                    nd.h = nd.h + ans
                self.loadIcons(nd)  # update progress icon
    #@+node:tbrown.20090119215428.35: *4* recalc_time
    def recalc_time(self, p: Position = None, clear: bool = False) -> tuple[str, str]:

        if p is None:
            p = self.c.currentPosition()
        v = p.v
        time_totl: str = None
        time_done: str = None

        # get values from children, if any
        for cn in p.children():
            ans = self.recalc_time(cn.copy(), clear)
            if time_totl is None:
                time_totl = ans[0]
            else:
                if ans[0] is not None:
                    time_totl += ans[0]

            if time_done is None:
                time_done = ans[1]
            else:
                if ans[1] is not None:
                    time_done += ans[1]

        if time_totl is not None:  # some value returned

            if clear:  # then we should just clear our values
                self.setat(v, 'progress', '')
                self.setat(v, 'time_req', '')
                return (time_totl, time_done)

            if time_done is not None:  # some work done
                # can't round derived progress without getting bad results form show_times
                if time_totl == 0:
                    pr = 0.
                else:
                    pr = float(time_done) / float(time_totl) * 100.
                self.setat(v, 'progress', pr)
            else:
                self.setat(v, 'progress', 0)
            self.setat(v, 'time_req', time_totl)
        else:  # no values from children, use own
            tr = self.getat(v, 'time_req')
            pr = self.getat(v, 'progress')
            if tr != '':
                time_totl = tr
                if pr != '':
                    time_done = float(pr) / 100. * tr
                else:
                    self.setat(v, 'progress', 0)

        return (time_totl, time_done)
    #@+node:tbrown.20090119215428.36: *4* clear_time_req
    @redrawer
    @projectChanger
    def clear_time_req(self, p: Position = None) -> None:

        if p is None:
            p = self.c.currentPosition()
        v = p.v
        self.setat(v, 'time_req', '')
    #@+node:tbrown.20090119215428.37: *4* update_project
    @redrawer
    def update_project(self, p: Position = None) -> None:
        """Find highest parent with '@project' in headline and run recalc_time
        and maybe show_times (if headline has '@project time')"""

        if p is None:
            p = self.c.currentPosition()
        project = None

        for nd in p.self_and_parents():
            if nd.headString().find('@project') > -1:
                project = nd.copy()

        if project:
            self.recalc_time(project)
            if project.headString().find('@project time') > -1:
                self.show_times(project, show=True)
            else:
                self.show_times(p, show=True)
        else:
            self.show_times(p, show=False)
    #@+node:tbrown.20090119215428.38: *4* local_recalc
    @redrawer
    def local_recalc(self, p: Position = None) -> None:
        self.recalc_time(p)
    #@+node:tbrown.20090119215428.39: *4* local_clear
    @redrawer
    def local_clear(self, p: Position = None) -> None:
        self.recalc_time(p, clear=True)
    #@+node:tbrown.20110213091328.16233: *4* set_due_date
    def set_due_date(self,
        p: Position = None,
        val: Any = None,  # Hard to annotate.
        mode: str = 'adjust',
        field: str = 'duedate',
    ) -> None:
        "mode: `adjust` for change in time, `check` for checkbox toggle"
        if p is None:
            p = self.c.currentPosition()
        v = p.v

        if field == 'duedate':
            toggle = self.ui.UI.dueDateToggle
        else:
            toggle = self.ui.UI.nxtwkDateToggle

        if mode == 'check':
            if toggle.checkState() == Unchecked:
                self.setat(v, field, "")
            else:
                self.setat(v, field, val.toPyDate())
        else:
            toggle.setCheckState(Checked)
            self.setat(v, field, val.toPyDate())

        self.updateUI()  # if change was made to date with offset selector
        self.loadIcons(p)
    #@+node:tbrown.20110213091328.16235: *4* set_due_time
    def set_due_time(self,
        p: Position = None,
        val: Any = None,  # Hard to annotate.
        mode: str = 'adjust',
        field: str = 'duetime',
    ) -> None:
        "mode: `adjust` for change in time, `check` for checkbox toggle"
        if p is None:
            p = self.c.currentPosition()
        v = p.v

        if field == 'duetime':
            toggle = self.ui.UI.dueTimeToggle
        else:
            toggle = self.ui.UI.nxtwkTimeToggle

        if mode == 'check':
            if toggle.checkState() == Unchecked:
                self.setat(v, field, "")
            else:
                self.setat(v, field, val.toPyTime())
        else:
            toggle.setCheckState(Checked)
            self.setat(v, field, val.toPyTime())
        self.loadIcons(p)

    #@+node:tbrown.20121204084515.60965: *4* set_date_offset
    def set_date_offset(self, field: str = 'nextworkdate') -> None:
        """set_nxtwk_date_offset - update date by selected offset

        offset sytax::

            +5 five days after today
            -5 five days before today
            >5 move current date 5 days later
            <5 move current date 5 days earlier

        """

        if field == 'nextworkdate':
            offset = str(self.ui.UI.nxtwkDateOffset.currentText())
        else:
            offset = str(self.ui.UI.dueDateOffset.currentText())

        mult = 1  # to handle '<' as a negative relative offset

        date = QtCore.QDate.currentDate()

        if '<' in offset or '>' in offset:
            date = self.ui.UI.nxtwkDateEdit.date()

        if offset.startswith('<'):
            mult = -1

        self.set_due_date(val=date.addDays(mult * int(offset.strip('<>'))), field=field)
        p = self.c.currentPosition()
        self.loadIcons(p)
    #@+node:tbrown.20090119215428.40: *3* ToDo icon related...
    #@+node:tbrown.20090119215428.41: *4* childrenTodo
    @redrawer
    def childrenTodo(self, p: Position = None) -> None:
        if p is None:
            p = self.c.currentPosition()
        for p in p.children():
            if self.getat(p.v, 'priority') != 9999:
                continue
            self.setat(p.v, 'priority', 19)
            self.loadIcons(p)
    #@+node:tbrown.20130207095125.20463: *4* dueClear
    @redrawer
    def dueClear(self, p: Position = None) -> None:
        """clear due date on descendants, useful for creating a master todo
        item with sub items which previously had their own dates"""
        if p is None:
            p = self.c.currentPosition()
        for p in p.subtree():
            self.setat(p.v, 'duedate', '')
    #@+node:tbrown.20130207103126.28498: *4* needs_doing
    def needs_doing(self, v: VNode = None, pri: Any = None, due: Any = None) -> bool:  # Hard to annotate.
        """needs_doing - Return true if the node is a todo node that needs doing

        :Parameters:
        - `v`: vnode
        """

        if v is not None:
            pri = self.getat(v, 'priority')
            due = self.getat(v, 'duedate')

        return (pri in self.todo_priorities) or (due and pri == 9999)
    #@+node:tbrown.20090119215428.42: *4* find_todo
    @redrawer
    def find_todo(self, p: Position = None, stage: int = 0) -> bool:
        """Recursively find the next todo"""

        # search is like XPath 'following' axis, all nodes after p in document order.
        # returning True should always propogate all the way back up to the top
        # stages: 0 - user selected start node,
        #         1 - search siblings, parents siblings,
        #         2 - searching children
        if p is None:
            p = self.c.currentPosition()

        # see if this node is a todo
        if stage != 0 and self.needs_doing(p.v):
            if p.getParent():
                self.c.selectPosition(p.getParent())
                self.c.expandNode()
            self.c.selectPosition(p)
            return True

        for nd in p.children():
            if self.find_todo(nd, stage=2):
                return True

        if stage < 2 and p.getNext():
            if self.find_todo(p.getNext(), stage=1):
                return True

        if stage < 2 and p.getParent() and p.getParent().getNext():
            if self.find_todo(p.getParent().getNext(), stage=1):
                return True

        if stage == 0:
            g.es("None found")

        return False
    #@+node:tbrown.20090119215428.43: *4* prikey
    def prikey(self, v: VNode) -> int:
        """key function for sorting by priority"""
        # getat returns 9999 for nodes without priority, so you'll only get -1
        # if a[1] is not a node.  Or even an object.

        try:
            pa = int(self.getat(v, 'priority'))
        except ValueError:
            pa = -1

        return pa if pa != 24 else 0
    #@+node:tbrown.20110213153425.16373: *4* duekey
    def duekey(self, v: VNode, field: str = 'due') -> tuple[bool, datetime.date, datetime.time, int]:
        """key function for sorting by due date/time"""
        # pylint: disable=boolean-datetime
        priority = self.getat(v, 'priority')
        done = priority not in self.todo_priorities
        date_ = self.getat(v, field + 'date') or datetime.date(3000, 1, 1)
        time_ = self.getat(v, field + 'time') or datetime.time(23, 59, 59)
        return done, date_, time_, priority
    #@+node:tbrown.20110213153425.16377: *4* dueSort
    @redrawer
    def dueSort(self, p: Position = None, field: str = 'due') -> None:
        if p is None:
            p = self.c.currentPosition()
        self.c.selectPosition(p)
        self.c.sortSiblings(key=lambda x: self.duekey(x, field=field))
    #@+node:tbrown.20090119215428.44: *4* priority_clear
    @redrawer
    def priority_clear(self, v: VNode = None) -> None:

        if v is None:
            v = self.c.currentPosition().v
        self.setat(v, 'priority', 9999)
        self.loadIcons(self.c.currentPosition())
    #@+node:tbrown.20090119215428.45: *4* priSort
    @redrawer
    def priSort(self, p: Position = None) -> None:
        if p is None:
            p = self.c.currentPosition()
        self.c.selectPosition(p)
        self.c.sortSiblings(key=self.prikey)
    #@+node:tbrown.20090119215428.46: *4* reclassify
    @redrawer
    def reclassify(self, p: Position = None) -> None:
        """change priority codes"""

        if p is None:
            p = self.c.currentPosition()
        g.es('\n Current distribution:')
        self.showDist()
        dat: dict = {}
        for end in 'from', 'to':
            if Qt:
                x0, ok = QtWidgets.QInputDialog.getText(
                    None, 'Reclassify priority', '%s priorities (1-9,19)' % end)
                if not ok:
                    x0 = None
                else:
                    x0 = str(x0)
            else:
                x0 = g.app.gui.runAskOkCancelStringDialog(
                    self.c, 'Reclassify priority', '%s priorities (1-7,19)' % end.upper())
            try:
                while re.search(r'\d+-\d+', x0):
                    what = re.search(r'\d+-\d+', x0).group(0)
                    rng = [int(n) for n in what.split('-')]
                    repl = []
                    if rng[0] > rng[1]:
                        for n in range(rng[0], rng[1] - 1, -1):
                            repl.append(str(n))
                    else:
                        for n in range(rng[0], rng[1] + 1):
                            repl.append(str(n))
                    x0 = x0.replace(what, ','.join(repl))

                x0 = [int(i) for i in x0.replace(',', ' ').split()]
                    # if int(i) in self.todo_priorities]
            except Exception:
                g.es('Not understood, no action')
                return
            if not x0:
                g.es('No action')
                return
            dat[end] = x0

        if len(dat['from']) != len(dat['to']):
            g.es('Unequal list lengths, no action')
            return

        cnt = 0
        for p in p.subtree():
            pri = int(self.getat(p.v, 'priority'))
            if pri in dat['from']:
                self.setat(p.v, 'priority', dat['to'][dat['from'].index(pri)])
                self.loadIcons(p)
                cnt += 1
        g.es('\n%d priorities reclassified, new distribution:' % cnt)
        self.showDist()
    #@+node:tbrown.20090119215428.47: *4* setPri
    @redrawer
    def setPri(self, pri: Any) -> None:

        if pri in self.recentIcons:
            self.recentIcons.remove(pri)
        self.recentIcons.insert(0, pri)
        self.recentIcons = self.recentIcons[:3]

        p = self.c.currentPosition()
        self.setat(p.v, 'priority', pri)
        self.setat(p.v, 'prisetdate', str(datetime.date.today()))
        self.loadIcons(p)
    #@+node:tbrown.20090119215428.48: *4* showDist
    def showDist(self, p: Position = None) -> None:
        """show distribution of priority levels in subtree"""
        if p is None:
            p = self.c.currentPosition()
        pris: dict = {}
        for p in p.subtree():
            pri = int(self.getat(p.v, 'priority'))
            if pri not in pris:
                pris[pri] = 1
            else:
                pris[pri] += 1
        pris_list = sorted([(k, v) for k, v in pris.items()])
        for item in pris_list:
            if item[0] in self.priorities:
                g.es('%s\t%d\t%s\t(%s)' % (self.priorities[item[0]]['short'], item[1],
                    self.priorities[item[0]]['long'], item[0]))
    #@+node:tbrown.20150605111428.1: *3* updateStyle
    def updateStyle(self, tag: str = None, k: int = None) -> None:
        """
        updateStyle - calling widget.setStyleSheet("/* */") is a trick to get Qt to
        update appearance on a widget styled depending on changes in attributes.
        It's faster than applying the whole stylesheet at top level or applying the
        whole stylesheet to the widget, which also breaks style cascading. But it's
        still too slow to do as the user up/down-arrows through nodes, so we just do
        it on idle instead.

        However, the idle event isn't only called when Leo is truely idle, it's just
        called at a set frequency. So by checking that time (0.2 sec) as passed
        since the need to restyle the node was noted, we avoid updating every
        idle-time seconds as the user scrolls through the outline with the arrow
        keys, which causes hiccups in scrolling speed.
        """

        if self._widget_to_style:
            # pylint: disable = unpacking-non-sequence
            # this would be neat, but hasPendingEvents() always returns True
            # (google it), so check time has passed instead
            # if QtWidgets.QApplication.instance().hasPendingEvents():
            #     return  # not truely idle
            w, old_time = self._widget_to_style
            if time.time() - old_time > 0.2:
                w.setStyleSheet("/* */")
                self._widget_to_style = None
    #@+node:tbrown.20090119215428.49: *3* updateUI
    def updateUI(self, tag: str = None, k: dict = None) -> None:

        if k and k['c'] != self.c:
            return  # wrong number

        v = self.c.currentPosition().v

        # check work date < due date and do stylesheet re-evaluation stuff
        nwd = self.getat(v, 'nextworkdate')
        due = self.getat(v, 'duedate')
        if hasattr(self.ui.UI, "frmDates"):
            w = self.ui.UI.frmDates
            if nwd and due and str(nwd) > str(due):
                w.setProperty('style_class', 'tododate_error')
            else:
                w.setProperty('style_class', '')
            # update style on this widget on idle, see updateStyle()
            self._widget_to_style = (w, time.time())

        self.ui.setProgress(int(self.getat(v, 'progress') or 0))
        self.ui.setTime(float(self.getat(v, 'time_req') or 0))

        self.ui.setDueDate(self.getat(v, 'duedate'))
        # default is "", which is understood by setDueDate()
        self.ui.setDueTime(self.getat(v, 'duetime'))
        # ditto

        self.ui.setDueDate(self.getat(v, 'duedate'))
        self.ui.setDueTime(self.getat(v, 'duetime'))
        self.ui.setNextWorkDate(self.getat(v, 'nextworkdate'))
        self.ui.setNextWorkTime(self.getat(v, 'nextworktime'))
        created = self.getat(v, 'created')
        if created and isinstance(created, datetime.datetime) and created.year >= 1900:
            self.ui.UI.createdTxt.setText(created.strftime("%d %b %y"))
            self.ui.UI.createdTxt.setToolTip(created.strftime("Created %H:%M %d %b %Y"))
        else:
            # .strftime doesn't work here! This has has happened...
            try:
                gdate = self.c.p.v.gnx.split('.')[1][:12]
                created = datetime.datetime.strptime(gdate, '%Y%m%d%H%M')
                if created.year < 1900:
                    created = None
            except Exception:
                created = None
            if created:
                self.ui.UI.createdTxt.setText(created.strftime("Created %d %b %Y"))
                self.ui.UI.createdTxt.setToolTip(created.strftime("gnx created %H:%M %d %b %Y"))
            else:
                self.ui.UI.createdTxt.setText("")

        # Update the label.
        h = self.c and self.c.p and self.c.p.h
        due = self.getat(v, 'duedate')
        ago = (datetime.date.today() - created.date()).days if created else 0
        if due:
            days = (due - datetime.date.today()).days
            txt = f"{h}\nCreated {ago} days ago, due in {days}"
        else:
            txt = f"{h}\nCreated {ago} days ago"
        self.ui.UI.txtDetails.setText(txt)
        prisetdate = self.getat(v, 'prisetdate')
        self.ui.UI.txtDetails.setToolTip("Priority set %s" %
            (str(prisetdate).strip() or '?')
        )
    #@+node:tbrown.20121129095833.39490: *3* unl_to_pos (todo.py)
    def unl_to_pos(self, unl: Any, for_p: Any) -> tuple[Cmdr, Position]:
        """"unl may be an outline (like c) or an UNL (string)

        return c, p where c is an outline and p is a node to copy data to
        in that outline

        for_p is the p to be copied - needed to check for invalid recursive
        copy / move
        """

        # COPIED FROM quickMove.py

        # unl is an UNL indicating where to insert
        full_path = unl
        path, unl = full_path.split('#', 1)
        c2 = g.openWithFileName(path, old_c=self.c)
        self.c.bringToFront(c2=self.c)
        maxp = g.findAnyUnl(unl, c2)
        if maxp:
            if (for_p == maxp or for_p.isAncestorOf(maxp)):
                g.es("Invalid move")
                return None, None
            nd = maxp
        else:
            g.es("Could not find '%s'" % full_path)
            self.c.bringToFront(c2=self.c)
            return None, None
        return c2, nd
    #@-others
#@+node:tbrown.20170928065405.1: ** command fix datetime
@g.command('todo-fix-datetime')
def todo_fix_datetime(event: Event) -> None:

    c = event['c']
    if not hasattr(c, 'cleo'):  # 2856.
        return
    changed = 0
    for nd in c.all_unique_nodes():
        for key in c.cleo._datetime_fields:
            x = c.cleo.getat(nd, key)
            if not isinstance(x, str):
                c.cleo.setat(nd, key, x)
                changed += 1
                g.es("%r -> %r" % (x, c.cleo.getat(nd, key)))
    g.es("Changed %d attribs." % changed)

#@+node:tbrown.20100701093750.13800: ** command inc/dec priority
@g.command('todo-dec-pri')
def todo_dec_pri(event: Event, direction: int = 1) -> None:

    c = event['c']
    if not hasattr(c, 'cleo'):  # 2856.
        return
    p = c.p
    pri = int(c.cleo.getat(p.v, 'priority'))

    if pri not in c.cleo.priorities:
        pri = 1
    else:
        ordered = sorted(c.cleo.priorities.keys())
        pri = ordered[(ordered.index(pri) + direction) % len(ordered)]

    pri = c.cleo.setPri(pri)
    c.redraw()
    # c.doCommandByName("todo-inc-pri")

@g.command('todo-inc-pri')
def todo_inc_pri(event: Event) -> None:
    todo_dec_pri(event, direction=-1)

for cmd, method in [
    ("todo-children-todo", "childrenTodo"),
    ("todo-find-todo", "find_todo"),
]:

    def f(event: Event, method: str = method) -> None:
        getattr(event.c.cleo, method)()
        event.c.redraw()

    g.command(cmd)(f)
#@-others
#@@language python
#@@tabwidth -4
#@-leo
