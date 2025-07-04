#@+leo-ver=5-thin
#@+node:ekr.20140907123524.18774: * @file ../plugins/qt_frame.py
"""Leo's qt frame classes."""
#@+<< qt_frame imports >>
#@+node:ekr.20110605121601.18003: ** << qt_frame imports >>
from __future__ import annotations
from collections import defaultdict
from collections.abc import Callable
import os
import platform
import string
import sys
import time
import urllib
from typing import Any, Optional, Union, TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.core import leoColor
from leo.core import leoColorizer
from leo.core import leoFrame
from leo.core import leoGui
from leo.core import leoMenu
from leo.commands import gotoCommands
from leo.core.leoAPI import StringTextWrapper
from leo.core.leoQt import QtCore, QtGui, QtWidgets
from leo.core.leoQt import QAction, Qsci
from leo.core.leoQt import AlignLeft
from leo.core.leoQt import ContextMenuPolicy, DropAction, FocusReason, KeyboardModifier
from leo.core.leoQt import MoveOperation, Orientation, MouseButton
from leo.core.leoQt import Policy, ScrollBarPolicy, SelectionBehavior, SelectionMode, SizeAdjustPolicy
from leo.core.leoQt import Shadow, Shape, Style
from leo.core.leoQt import TextInteractionFlag, ToolBarArea, Type, Weight, WindowState, WrapMode
from leo.plugins import qt_events
from leo.plugins import qt_text
from leo.plugins.qt_tree import LeoQtTree
from leo.plugins.mod_scripting import build_rclick_tree
from leo.plugins.qt_layout import LayoutCacheWidget
#@-<< qt_frame imports >>
#@+<< qt_frame annotations >>
#@+node:ekr.20220415080427.1: ** << qt_frame annotations >>
if TYPE_CHECKING:  # pragma: no cover
    from typing import TypeAlias  # Requires Python 3.12+
    from leo.core.leoColorizer import BaseColorizer
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoGui
    from leo.core.leoGui import LeoKeyEvent
    from leo.core.leoNodes import Position
    from leo.plugins.leoFrame import LeoLog
    from leo.plugins.mod_scripting import ScriptingController
    from leo.plugins.qt_text import QScintillaWrapper, QTextEditWrapper
    Args = Any
    KWargs = Any
    QBoxLayout = QtWidgets.QBoxLayout
    QComboBox = QtWidgets.QComboBox
    QCursor = QtGui.QCursor
    QEvent: TypeAlias = QtCore.QEvent
    QFocusEvent: TypeAlias = QtGui.QFocusEvent
    QFrame = QtWidgets.QFrame
    QGridLayout = QtWidgets.QGridLayout
    QLayout = QtWidgets.QWidget
    QMenu = QtWidgets.QMenu
    QMenuBar = QtWidgets.QMenuBar
    QMouseEvent: TypeAlias = QtGui.QMouseEvent
    QObject = QtCore.QObject
    QPoint = QtCore.QPoint
    QPushButton = QtWidgets.QPushButton
    QRect = QtGui.QRect
    QSplitter = QtWidgets.QSplitter
    QTabWidget = QtWidgets.QTabWidget
    QTextBlock = QtGui.QTextBlock
    QTextCursor = QtGui.QTextCursor
    QWidget = QtWidgets.QWidget
    RClick = tuple  # Union[tuple, namedtuple('RClick', 'position,children')]
    RClicks = list[RClick]

    # LeoFrame defines TextAPI as:
    # TextAPI = Union[QScintillaWrapper, QTextEditWrapper, StringTextWrapper]
    QtWrapper = Union[QScintillaWrapper, QTextEditWrapper]
#@-<< qt_frame annotations >>
#@+<< qt_frame decorators >>
#@+node:ekr.20210228142208.1: ** << qt_frame decorators >>
def body_cmd(name: str) -> Callable:
    """Command decorator for the LeoQtBody class."""
    return g.new_cmd_decorator(name, ['c', 'frame', 'body'])

def frame_cmd(name: str) -> Callable:
    """Command decorator for the LeoQtFrame class."""
    return g.new_cmd_decorator(name, ['c', 'frame',])

def log_cmd(name: str) -> Callable:
    """Command decorator for the LeoQtLog class."""
    return g.new_cmd_decorator(name, ['c', 'frame', 'log'])
#@-<< qt_frame decorators >>
#@+others
#@+node:ekr.20110605121601.18137: ** class  DynamicWindow (QMainWindow)
class DynamicWindow(QtWidgets.QMainWindow):
    """
    A class representing all parts of the main Qt window.

    c.frame.top is a DynamicWindow.
    c.frame.top.leo_master is a LeoTabbedTopLevel, a subclass of QTabWidget.
    c.frame.top.parent() is a QStackedWidget()

    All leoQtX classes use the ivars of this Window class to
    support operations requested by Leo's core.
    """
    #@+others
    #@+node:ekr.20240730052903.1: *3*  dw: Birth
    #@+node:ekr.20110605121601.18138: *4* dw.ctor
    def __init__(self, c: Cmdr, parent: QWidget = None) -> None:
        """Ctor for the DynamicWindow class.  The main window is c.frame.top"""
            # Called from LeoQtFrame.finishCreate.
            # parent is a LeoTabbedTopLevel.
        super().__init__(parent)
        self.leo_c = c
        self.leo_body_frame: QWidget = None
        self.leo_master: LeoTabbedTopLevel = None  # Set in construct.
        self.leo_menubar: QWidget = None  # Set in createMenuBar.
        self.leo_statusBar: QtWidgets.QStatusBar = None
        self.layout_name: str = None
        self.old_layout_name: str = None
        self.verticalLayout: QBoxLayout = None
        self.vr_parent_frame: QWidget = None
        c._style_deltas = defaultdict(lambda: 0)  # for adjusting styles dynamically
        self.layout_cache = LayoutCacheWidget(c, self)
        self.reloadSettings()

        # Delay until DW initialization has ended and c.commandsDict
        # has been populated
        def run_layout():
            c.doCommandByName('layout-restore-to-setting')
        QtCore.QTimer.singleShot(300, run_layout)
    #@+node:ekr.20240726074809.1: *4* dw.recreateMainWindow
    def recreateMainWindow(self):
        """
        Recreate the main window by reloading the outline.
        """
        w = getattr(self, 'centralwidget', None)
        if w and self.layout_name != self.old_layout_name:
            c = self.leo_c
            print('')
            print('@string qt-layout-name has changed: restarting Leo')
            c.restartLeo()

    #@+node:ekr.20240730052919.1: *4* dw.reloadSettings
    def reloadSettings(self) -> None:
        c = self.leo_c
        c.registerReloadSettings(self)
        self.old_layout_name = self.layout_name
        self.layout_name = c.config.getString('qt-layout-name')
        self.show_iconbar = c.config.getBool('show-iconbar', default=True)
        self.toolbar_orientation = c.config.getString('qt-toolbar-location') or ''
        self.useScintilla = c.config.getBool('qt-use-scintilla')
        self.use_gutter = c.config.getBool('use-gutter', default=False)
        self.recreateMainWindow()
        if getattr(self, 'iconBar', None):
            if self.show_iconbar:
                self.iconBar.show()
            else:
                self.iconBar.hide()
    #@+node:ekr.20110605121601.18139: *3* dw.construct & helpers
    def construct(self, master: LeoTabbedTopLevel = None) -> None:
        """ Factor 'heavy duty' code out from the DynamicWindow ctor """
        c = self.leo_c
        self.leo_master = master
        # Create all widgets.
        self.setMainWindowOptions()
        self.createCentralWidget()
        main_splitter, secondary_splitter = self.create_layout()
        self.createMiniBuffer(self.centralwidget)
        self.createMenuBar()
        self.createStatusBar(self)
        self.createIconBar()
        # Set official ivars...
        self.leo_menubar = self.menuBar()
        self.leo_statusBar = QtWidgets.QStatusBar()
        self.setStatusBar(self.leo_statusBar)
        # Final inits...
        if not self.show_iconbar:
            # #266 A setting to hide the icon bar.
            self.iconBar.hide()
        if hasattr(c, 'styleSheetManager'):
            c.styleSheetManager.set_style_sheets(top=self, all=True)
        # Connect signals last.
        QtCore.QMetaObject.connectSlotsByName(self)
    #@+node:ekr.20240726062809.1: *4* dw.create_layout & helpers
    def create_layout(self) -> tuple[QWidget, QWidget]:
        """
        Create the layout given by @string qt_layout_name.

        Return the tuple (main_splitter, Optional[secondary_splitter])
        """
        c = self.leo_c

        import leo.plugins.viewrendered as vrm
        cache = self.layout_cache
        ms, ss = self.createMainLayout(self.centralwidget)
        self.createBodyPane(cache)
        self.createOutlinePane(ss)
        self.createLogPane(ss)
        # self.vr_parent_frame = ms
        _ = vrm.getVr(c=c, parent=ms)

        return ms, ss
    #@+node:ekr.20240725073848.1: *4* dw.insert_vr_frame
    def insert_vr_frame(self, vr_frame: QtWidgets.QFrame) -> None:
        """Insert the given frame into the dw.vr_parent_frame."""
        c = self.leo_c
        dw = self
        gui = g.app.gui
        parent = dw.vr_parent_frame
        if not isinstance(parent, QtWidgets.QSplitter):
            g.trace('dw.vr_parent_frame must be a QSplitter!')
            return
        # Add the vr frame.
        vr_frame.show()
        parent.addWidget(vr_frame)
        # Resize splitters if they exist.
        main_splitter = gui.find_widget_by_name(c, 'main_splitter')
        secondary_splitter = gui.find_widget_by_name(c, 'secondary_splitter')
        gui.equalize_splitter(main_splitter)
        gui.equalize_splitter(secondary_splitter)
        gui.equalize_splitter(parent)
    #@+node:ekr.20110605121601.18165: *3* dw: create log tabs
    #@+node:ekr.20110605121601.18167: *4* dw.createSpellTab
    def createSpellTab(self, parent: QWidget) -> None:
        # dw = self
        vLayout = self.createVLayout(parent, 'spellVLayout', margin=2)
        spellFrame = self.createFrame(parent, 'spellFrame')
        vLayout2 = self.createVLayout(spellFrame, 'spellVLayout')
        grid = self.createGrid(None, 'spellGrid', spacing=2)
        table = (
            ('Add', 'Add', 2, 1),
            ('Find', 'Find', 2, 0),
            ('Change', 'Change', 3, 0),
            ('FindChange', 'Change,Find', 3, 1),
            ('Ignore', 'Ignore', 4, 0),
            ('Hide', 'Hide', 4, 1),
        )
        for (ivar, label, row, col) in table:
            name = f"spell_{label}_button"
            button = self.createButton(spellFrame, name, label)
            grid.addWidget(button, row, col)
            func = getattr(self, f"do_leo_spell_btn_{ivar}")
            button.clicked.connect(func)
            # This name is significant.
            setattr(self, f"leo_spell_btn_{ivar}", button)
        self.leo_spell_btn_Hide.setCheckable(False)
        spacerItem = QtWidgets.QSpacerItem(20, 40, Policy.Minimum, Policy.Expanding)
        grid.addItem(spacerItem, 5, 0, 1, 1)
        listBox = QtWidgets.QListWidget(spellFrame)
        self.set_widget_size_policy(listBox, kind1=Policy.MinimumExpanding, kind2=Policy.Expanding)
        listBox.setMinimumSize(QtCore.QSize(0, 0))
        listBox.setMaximumSize(QtCore.QSize(150, 150))
        listBox.setObjectName("leo_spell_listBox")
        grid.addWidget(listBox, 1, 0, 1, 2)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, Policy.Expanding, Policy.Minimum)
        grid.addItem(spacerItem1, 2, 2, 1, 1)
        lab = self.createLabel(spellFrame, 'spellLabel', 'spellLabel')
        grid.addWidget(lab, 0, 0, 1, 2)
        vLayout2.addLayout(grid)
        vLayout.addWidget(spellFrame)
        listBox.itemDoubleClicked.connect(self.do_leo_spell_btn_FindChange)
        # Official ivars.
        self.spellFrame = spellFrame
        self.spellGrid = grid
        self.leo_spell_widget = parent  # 2013/09/20: To allow bindings to be set.
        self.leo_spell_listBox = listBox  # Must exist
        self.leo_spell_label = lab  # Must exist (!!)
    #@+node:ekr.20110605121601.18166: *4* dw.createFindTab & helpers
    def createFindTab(self, parent: QWidget, tab_widget: QWidget) -> None:
        """Create a Find Tab in the given parent."""
        c, dw = self.leo_c, self
        fc = c.findCommands
        assert not fc.ftm
        fc.ftm = ftm = FindTabManager(c)
        grid = self.create_find_grid(parent)
        row = 0  # The index for the present row.
        row = dw.create_find_header(grid, parent, row)
        row = dw.create_find_findbox(grid, parent, row)
        row = dw.create_find_replacebox(grid, parent, row)
        max_row2 = 1
        max_row2 = dw.create_find_checkboxes(grid, parent, max_row2, row)
        row = dw.create_find_buttons(grid, parent, max_row2, row)
        row = dw.create_help_row(grid, parent, row)
        dw.override_events()
        # Last row: Widgets that take all additional vertical space.
        w = QtWidgets.QWidget()
        grid.addWidget(w, row, 0)
        grid.addWidget(w, row, 1)
        grid.addWidget(w, row, 2)
        grid.setRowStretch(row, 100)
        # Official ivars (in addition to checkbox ivars).
        self.leo_find_widget = tab_widget  # A scrollArea.
        ftm.init_widgets()
    #@+node:ekr.20131118152731.16847: *5* dw.create_find_grid
    def create_find_grid(self, parent: QWidget) -> QGridLayout:
        grid = self.createGrid(parent, 'findGrid', margin=10, spacing=10)
        grid.setColumnStretch(0, 100)
        grid.setColumnStretch(1, 100)
        grid.setColumnStretch(2, 10)
        grid.setColumnMinimumWidth(1, 75)
        grid.setColumnMinimumWidth(2, 175)
        return grid
    #@+node:ekr.20131118152731.16849: *5* dw.create_find_header
    def create_find_header(self, grid: QGridLayout, parent: QWidget, row: int) -> int:
        if False:
            dw = self
            lab1 = dw.createLabel(parent, 'findHeading', 'Find/Change Settings...')
            grid.addWidget(lab1, row, 0, 1, 2, AlignLeft)  # AlignHCenter
            row += 1
        return row
    #@+node:ekr.20131118152731.16848: *5* dw.create_find_findbox
    def create_find_findbox(self, grid: QGridLayout, parent: QWidget, row: int) -> int:
        """Create the Find: label and text area."""
        c, dw = self.leo_c, self
        fc = c.findCommands
        ftm = fc.ftm
        assert ftm.find_findbox is None
        ftm.find_findbox = w = dw.createLineEdit(
            parent, 'findPattern', disabled=fc.expert_mode)
        lab2 = self.createLabel(parent, 'findLabel', 'Find:')
        grid.addWidget(lab2, row, 0)
        grid.addWidget(w, row, 1, 1, 2)
        row += 1
        return row
    #@+node:ekr.20131118152731.16850: *5* dw.create_find_replacebox
    def create_find_replacebox(self, grid: QGridLayout, parent: QWidget, row: int) -> int:
        """Create the Replace: label and text area."""
        c, dw = self.leo_c, self
        fc = c.findCommands
        ftm = fc.ftm
        assert ftm.find_replacebox is None
        ftm.find_replacebox = w = dw.createLineEdit(
            parent, 'findChange', disabled=fc.expert_mode)
        lab3 = dw.createLabel(parent, 'changeLabel', 'Replace:')
        grid.addWidget(lab3, row, 0)
        grid.addWidget(w, row, 1, 1, 2)
        row += 1
        return row
    #@+node:ekr.20131118152731.16851: *5* dw.create_find_checkboxes
    def create_find_checkboxes(self, grid: QGridLayout, parent: QWidget, max_row2: int, row: int) -> int:
        """Create check boxes and radio buttons."""
        c, dw = self.leo_c, self
        fc = c.findCommands
        ftm = fc.ftm

        def mungeName(kind: str, label: str) -> str:
            # The returned value is the name of an ivar.
            kind = 'check_box_' if kind == 'box' else 'radio_button_'
            name = label.replace(' ', '_').replace('&', '').lower()
            return f"{kind}{name}"

        # Rows for check boxes, radio buttons & execution buttons...

        d = {
            'box': dw.createCheckBox,
            'rb': dw.createRadioButton,
        }
        table = (
            # Note: the Ampersands create Alt bindings when the log pane is enable.
            # The QShortcut class is the workaround.
            # First row.
            ('box', 'whole &Word', 0, 0),
            ('rb', '&Entire outline', 0, 1),
            # Second row.
            ('box', '&Ignore case', 1, 0),
            ('rb', '&Suboutline only', 1, 1),
            # Third row.
            ('box', 'rege&Xp', 2, 0),
            ('rb', '&Node only', 2, 1),
            # Fourth row.
            ('box', 'mark &Finds', 3, 0),
            ('rb', 'fi&Le only', 3, 1),
            # Fifth row.
            ('box', 'mark &Changes', 4, 0),
            ('box', 'search &Headline', 4, 1),
            # Sixth Row
            ('box', 'search &Body', 5, 1),

            # ('box', 'rege&Xp', 2, 0),
            # ('rb', '&Node only', 2, 1),
            # # Fourth row.
            # ('box', 'mark &Finds', 3, 0),
            # ('box', 'search &Headline', 3, 1),
            # # Fifth row.
            # ('box', 'mark &Changes', 4, 0),
            # ('box', 'search &Body', 4, 1),
            # ('rb', 'File &Only', 5, 1),

            # Sixth row.
            # ('box', 'wrap &Around', 5, 0),
            # a,b,c,e,f,h,i,n,rs,w
        )
        for kind, label, row2, col in table:
            max_row2 = max(max_row2, row2)
            name = mungeName(kind, label)
            func = d.get(kind)
            assert func
            # Fix the greedy checkbox bug:
            label = label.replace('&', '')
            w = func(parent, name, label)
            grid.addWidget(w, row + row2, col)
            # The the checkbox ivars in dw and ftm classes.
            assert getattr(ftm, name) is None
            setattr(ftm, name, w)
        return max_row2
    #@+node:ekr.20131118152731.16853: *5* dw.create_help_row
    def create_help_row(self, grid: QGridLayout, parent: QWidget, row: int) -> int:
        # Help row.
        if False:
            w = self.createLabel(parent,
                'findHelp', 'For help: <alt-x>help-for-find-commands<return>')
            grid.addWidget(w, row, 0, 1, 3)
            row += 1
        return row
    #@+node:ekr.20131118152731.16852: *5* dw.create_find_buttons
    def create_find_buttons(self, grid: QGridLayout, parent: QWidget, max_row2: int, row: int) -> int:
        """
        Per #1342, this method now creates labels, not real buttons.
        """
        dw, k = self, self.leo_c.k

        # Create Buttons in column 2 (Leo 4.11.1.)
        table = (
            (0, 2, 'find-next'),  # 'findButton',
            (1, 2, 'find-prev'),  # 'findPreviousButton',
            (2, 2, 'find-all'),  # 'findAllButton',
            (3, 2, 'replace'),  # 'changeButton',
            (4, 2, 'replace-then-find'),  # 'changeThenFindButton',
            (5, 2, 'replace-all'),  # 'changeAllButton',
        )
        for row2, col, cmd_name in table:
            stroke = k.getStrokeForCommandName(cmd_name)
            if stroke:
                label = f"{cmd_name}:  {k.prettyPrintKey(stroke)}"
            else:
                label = cmd_name
            # #1342: Create a label, not a button.
            w = dw.createLabel(parent, cmd_name, label)
            w.setObjectName('find-label')
            grid.addWidget(w, row + row2, col)
        row += max_row2
        row += 2
        return row
    #@+node:ekr.20150618072619.1: *5* dw.create_find_status
    if 0:

        def create_find_status(self, grid: QGridLayout, parent: QWidget, row: int) -> None:
            """Create the status line."""
            dw = self
            status_label = dw.createLabel(parent, 'status-label', 'Status')
            status_line = dw.createLineEdit(parent, 'find-status', disabled=True)
            grid.addWidget(status_label, row, 0)
            grid.addWidget(status_line, row, 1, 1, 2)
            # Official ivars.
            dw.find_status_label = status_label
            dw.find_status_edit = status_line
    #@+node:ekr.20131118172620.16891: *5* dw.override_events
    def override_events(self) -> None:
        # dw = self
        c = self.leo_c
        fc = c.findCommands
        ftm = fc.ftm
        # Define class EventWrapper.
        #@+others
        #@+node:ekr.20131118172620.16892: *6* class EventWrapper
        class EventWrapper:

            def __init__(self, c: Cmdr, w: QWidget, next_w: QWidget, func: Callable) -> None:
                self.c = c
                self.d = self.create_d()  # Keys: stroke.s; values: command-names.
                self.w = w
                self.next_w = next_w
                self.eventFilter = qt_events.LeoQtEventFilter(c, w, 'EventWrapper')
                self.func = func
                self.oldEvent: Callable = w.event
                w.event = self.wrapper  # type:ignore # cannot assign to a method.
            #@+others
            #@+node:ekr.20131120054058.16281: *7* EventWrapper.create_d
            def create_d(self) -> dict[str, str]:
                """Create self.d dictionary."""
                c = self.c
                d = {}
                table = (
                    'toggle-find-ignore-case-option',
                    'toggle-find-in-body-option',
                    'toggle-find-in-headline-option',
                    'toggle-find-mark-changes-option',
                    'toggle-find-mark-finds-option',
                    'toggle-find-regex-option',
                    'toggle-find-word-option',
                    'toggle-find-wrap-around-option',
                    # New in Leo 5.2: Support these in the Find Dialog.
                    'find-all',
                    'find-next',
                    'find-prev',
                    'hide-find-tab',
                    'replace',
                    'replace-all',
                    'replace-then-find',
                    'set-find-everywhere',
                    'set-find-node-only',
                    'set-find-suboutline-only',
                    # #2041 & # 2094 (Leo 6.4): Support Alt-x.
                    'full-command',
                    'keyboard-quit',  # Might as well :-)
                )
                for cmd_name in table:
                    stroke = c.k.getStrokeForCommandName(cmd_name)
                    if stroke:
                        d[stroke.s] = cmd_name
                return d
            #@+node:ekr.20131118172620.16893: *7* EventWrapper.wrapper
            def wrapper(self, event: LeoKeyEvent) -> bool:

                type_ = event.type()
                # Must intercept KeyPress for events that generate FocusOut!
                if type_ == Type.KeyPress:
                    return self.keyPress(event)
                if type_ == Type.KeyRelease:
                    return self.keyRelease(event)  # type:ignore[arg-type]
                return self.oldEvent(event)
            #@+node:ekr.20131118172620.16894: *7* EventWrapper.keyPress
            def keyPress(self, event: LeoKeyEvent) -> bool:

                s = event.text()
                out = s and s in '\t\r\n'
                if out:
                    # Move focus to next widget.
                    if s == '\t':
                        if self.next_w:
                            self.next_w.setFocus(FocusReason.TabFocusReason)
                        else:
                            # Do the normal processing.
                            return self.oldEvent(event)
                    elif self.func:
                        self.func()
                    return True
                binding, ch, lossage = self.eventFilter.toBinding(event)
                # #2094: Use code similar to the end of LeoQtEventFilter.eventFilter.
                #        The ctor converts <Alt-X> to <Alt-x> !!
                #        That is, we must use the stroke, not the binding.
                key_event = leoGui.LeoKeyEvent(
                    c=self.c, char=ch, event=event, binding=binding, w=self.w)
                if key_event.stroke:
                    cmd_name = self.d.get(key_event.stroke)
                    if cmd_name:
                        self.c.doCommandByName(cmd_name)
                        return True
                # Do the normal processing.
                return self.oldEvent(event)
            #@+node:ekr.20131118172620.16895: *7* EventWrapper.keyRelease
            def keyRelease(self, event: QEvent) -> bool:
                return self.oldEvent(event)
            #@-others
        #@-others
        EventWrapper(c, w=ftm.find_findbox, next_w=ftm.find_replacebox, func=fc.find_next)
        EventWrapper(c, w=ftm.find_replacebox, next_w=ftm.find_next_button, func=fc.find_next)
        # Finally, checkBoxMarkChanges goes back to ftm.find_findBox.
        EventWrapper(c, w=ftm.check_box_mark_changes, next_w=ftm.find_findbox, func=None)
    #@+node:ekr.20110605121601.18152: *3* dw: create widgets
    #@+node:ekr.20110605121601.18153: *4* dw.createButton
    def createButton(self, parent: QWidget, name: str, label: str) -> QWidget:
        w = QtWidgets.QPushButton(parent)
        w.setObjectName(name)
        w.setText(self.tr(label))
        return w
    #@+node:ekr.20110605121601.18154: *4* dw.createCheckBox
    def createCheckBox(self, parent: QWidget, name: str, label: str) -> QWidget:
        w = QtWidgets.QCheckBox(parent)
        self.setName(w, name)
        w.setText(self.tr(label))
        return w
    #@+node:ekr.20110605121601.18155: *4* dw.createFrame
    def createFrame(
        self,
        parent: QWidget,
        name: str,
        hPolicy: Policy = None,
        vPolicy: Policy = None,
        lineWidth: int = 1,
        shadow: Shadow = None,
        shape: Shape = None,
    ) -> QWidget:
        """Create a Qt Frame."""
        if shadow is None:
            shadow = Shadow.Plain
        if shape is None:
            shape = Shape.NoFrame
        #
        w = QtWidgets.QFrame(parent)
        self.set_widget_size_policy(w, kind1=hPolicy, kind2=vPolicy)
        w.setFrameShape(shape)
        w.setFrameShadow(shadow)
        w.setLineWidth(lineWidth)
        self.setName(w, name)
        return w
    #@+node:ekr.20110605121601.18156: *4* dw.createGrid
    def createGrid(self,
        parent: QWidget, name: str, margin: int = 0, spacing: int = 0,
    ) -> QtWidgets.QGridLayout:
        w = QtWidgets.QGridLayout(parent)
        w.setContentsMargins(QtCore.QMargins(margin, margin, margin, margin))
        w.setSpacing(spacing)
        self.setName(w, name)
        return w
    #@+node:ekr.20110605121601.18157: *4* dw.createHLayout & createVLayout
    def createHLayout(self, parent: QWidget, name: str, margin: int = 0, spacing: int = 0) -> QBoxLayout:
        hLayout = QtWidgets.QHBoxLayout(parent)
        hLayout.setSpacing(spacing)
        hLayout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        self.setName(hLayout, name)
        return hLayout

    def createVLayout(self, parent: QWidget, name: str, margin: int = 0, spacing: int = 0) -> QBoxLayout:
        vLayout = QtWidgets.QVBoxLayout(parent)
        vLayout.setSpacing(spacing)
        vLayout.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        self.setName(vLayout, name)
        return vLayout
    #@+node:ekr.20110605121601.18158: *4* dw.createLabel
    def createLabel(self, parent: QWidget, name: str, label: str) -> QWidget:
        w = QtWidgets.QLabel(parent)
        self.setName(w, name)
        w.setText(self.tr(label))
        return w
    #@+node:ekr.20110605121601.18159: *4* dw.createLineEdit
    def createLineEdit(self, parent: QWidget, name: str, disabled: bool = True) -> QWidget:

        w = QtWidgets.QLineEdit(parent)
        w.setObjectName(name)
        w.leo_disabled = disabled  # Inject the ivar.
        return w
    #@+node:ekr.20110605121601.18160: *4* dw.createRadioButton
    def createRadioButton(self, parent: QWidget, name: str, label: str) -> QWidget:  # QtWidgets.QRadioButton:
        w = QtWidgets.QRadioButton(parent)
        self.setName(w, name)
        w.setText(self.tr(label))
        return w
    #@+node:ekr.20110605121601.18161: *4* dw.createStackedWidget
    def createStackedWidget(
        self,
        parent: QWidget,
        name: str,
        lineWidth: int = 1,
        hPolicy: Policy = None,
        vPolicy: Policy = None,
    ) -> QWidget:  # QtWidgets.QStackedWidget
        w = QtWidgets.QStackedWidget(parent)
        self.set_widget_size_policy(w, kind1=hPolicy, kind2=vPolicy)
        w.setAcceptDrops(True)
        w.setLineWidth(1)
        self.setName(w, name)
        return w
    #@+node:ekr.20110605121601.18162: *4* dw.createTabWidget
    def createTabWidget(self,
        parent: QWidget, name: str, hPolicy: Policy = None, vPolicy: Policy = None,
    ) -> QWidget:
        w = QtWidgets.QTabWidget(parent)
        # tb = w.tabBar()
        # tb.setTabsClosable(True)
        self.set_widget_size_policy(w, kind1=hPolicy, kind2=vPolicy)
        self.setName(w, name)
        return w
    #@+node:ekr.20110605121601.18163: *4* dw.createText (creates QTextBrowser)
    def createText(
        self,
        parent: QWidget,
        name: str,
        lineWidth: int = 0,
        shadow: Shadow = None,
        shape: Shape = None,
    ) -> QWidget:
        # Create a text widget.
        c = self.leo_c
        w: QWidget
        if name == 'richTextEdit' and self.useScintilla and Qsci:
            # Do this in finishCreate, when c.frame.body exists.
            w = Qsci.QsciScintilla(parent)
            self.scintilla_widget = w
        else:
            if shadow is None:
                shadow = Shadow.Plain
            if shape is None:
                shape = Shape.NoFrame
            w = qt_text.LeoQTextBrowser(parent, c, None)
            w.setFrameShape(shape)
            w.setFrameShadow(shadow)
            w.setLineWidth(lineWidth)
            self.setName(w, name)
        return w
    #@+node:ekr.20110605121601.18164: *4* dw.createTreeWidget
    def createTreeWidget(self, parent: QWidget, name: str) -> QWidget:
        c = self.leo_c
        w = LeoQTreeWidget(c, parent)
        self.set_widget_size_policy(w)
        # 12/01/07: add new config setting.
        multiple_selection = c.config.getBool('qt-tree-multiple-selection', default=True)
        if multiple_selection:
            w.setSelectionMode(SelectionMode.ExtendedSelection)
            w.setSelectionBehavior(SelectionBehavior.SelectRows)
        else:
            w.setSelectionMode(SelectionMode.SingleSelection)
            w.setSelectionBehavior(SelectionBehavior.SelectItems)
        w.setContextMenuPolicy(ContextMenuPolicy.CustomContextMenu)
        w.setHeaderHidden(False)
        self.setName(w, name)
        return w
    #@+node:ekr.20240730053128.1: *3* dw: events
    #@+node:ekr.20110605121601.18140: *4* dw.closeEvent
    def closeEvent(self, event: QEvent) -> None:
        """Handle a close event in the Leo window."""
        c = self.leo_c
        if not c.exists:
            # Fixes double-prompt bug on Linux.
            event.accept()
            return
        if c.inCommand:
            c.requestCloseWindow = True
            return
        ok = g.app.closeLeoWindow(c.frame)
        if ok:
            event.accept()
        else:
            event.ignore()
    #@+node:ekr.20110605121601.18172: *4* dw.do_leo_spell_btn_*
    def doSpellBtn(self, btn: str) -> None:
        """Execute btn, a button handler."""
        # Make *sure* this never crashes.
        try:
            tab = self.leo_c.spellCommands.handler.tab
            button = getattr(tab, btn)
            button()
        except Exception:
            g.es_exception()

    def do_leo_spell_btn_Add(self) -> None:
        self.doSpellBtn('onAddButton')

    def do_leo_spell_btn_Change(self) -> None:
        self.doSpellBtn('onChangeButton')

    def do_leo_spell_btn_Find(self) -> None:
        self.doSpellBtn('onFindButton')

    def do_leo_spell_btn_FindChange(self) -> None:
        self.doSpellBtn('onChangeThenFindButton')

    def do_leo_spell_btn_Hide(self) -> None:
        self.doSpellBtn('onHideButton')

    def do_leo_spell_btn_Ignore(self) -> None:
        self.doSpellBtn('onIgnoreButton')
    #@+node:ekr.20110605121601.18173: *4* dw.select
    def select(self, c: Cmdr) -> None:
        """Select the window or tab for c."""
        # Called from the save commands.
        self.leo_master.select(c)
    #@+node:ekr.20110605121601.18142: *3* dw: top-level methods
    #@+node:ekr.20190118150859.10: *4* dw.addNewEditor
    def addNewEditor(self, name: str) -> tuple[QWidget, QTextEditWrapper]:
        """Create a new body editor."""
        c, p = self.leo_c, self.leo_c.p
        body = c.frame.body
        assert isinstance(body, LeoQtBody), repr(body)
        # Step 1: create the editor.
        parent_frame = c.frame.top.leo_body_inner_frame
        widget = qt_text.LeoQTextBrowser(parent_frame, c, self)
        widget.setObjectName('richTextEdit')  # Will be changed later.
        wrapper = qt_text.QTextEditWrapper(widget, name='body', c=c)
        self.packLabel(widget)
        # Step 2: inject ivars, set bindings, etc.
        inner_frame = c.frame.top.leo_body_inner_frame  # Inject ivars *here*.
        body.injectIvars(inner_frame, name, p, wrapper)
        body.updateInjectedIvars(widget, p)
        wrapper.setAllText(p.b)
        wrapper.see(0)
        c.k.completeAllBindingsForWidget(wrapper)
        if isinstance(widget, QtWidgets.QTextEdit):
            colorizer = leoColorizer.make_colorizer(c, widget)
            colorizer.highlighter.setDocument(widget.document())
        else:
            # Scintilla only.
            body.recolorWidget(p, wrapper)
        return parent_frame, wrapper
    #@+node:ekr.20110605121601.18143: *4* dw.createBodyPane
    def createBodyPane(self, parent: QWidget) -> QWidget:
        """
        Create the *pane* for the body, not the actual QTextBrowser.
        """
        c = self.leo_c
        # Create widgets.
        bodyFrame = self.createFrame(parent, 'bodyFrame')
        innerFrame = self.createFrame(bodyFrame, 'innerBodyFrame')
        sw = self.createStackedWidget(innerFrame, 'bodyStackedWidget',
             hPolicy=Policy.Expanding, vPolicy=Policy.Expanding)
        page2 = QtWidgets.QWidget()
        self.setName(page2, 'bodyPage2')
        body = self.createText(page2, 'richTextEdit')  # A LeoQTextBrowser
        # Pack.
        vLayout = self.createVLayout(page2, 'bodyVLayout', spacing=0)
        grid = self.createGrid(bodyFrame, 'bodyGrid')
        innerGrid = self.createGrid(innerFrame, 'bodyInnerGrid')
        if self.use_gutter:
            lineWidget = qt_text.LeoLineTextWidget(c, body)
            vLayout.addWidget(lineWidget)
        else:
            vLayout.addWidget(body)
        sw.addWidget(page2)
        innerGrid.addWidget(sw, 0, 0, 1, 1)
        grid.addWidget(innerFrame, 0, 0, 1, 1)
        # Official ivars
        self.text_page = page2
        self.stackedWidget = sw  # used by LeoQtBody
        self.richTextEdit = body
        self.leo_body_frame = bodyFrame
        self.leo_body_inner_frame = innerFrame
        return bodyFrame
    #@+node:ekr.20110605121601.18144: *4* dw.createCentralWidget
    def createCentralWidget(self) -> QWidget:
        """Create the central widget."""
        dw = self
        w = QtWidgets.QWidget(dw)
        w.setObjectName("centralwidget")
        dw.setCentralWidget(w)
        # Official ivars.
        self.centralwidget = w
        return w
    #@+node:ekr.20240730054632.1: *4* dw.createIconBar & helper
    def createIconBar(self) -> None:
        """Create the icon bar."""
        c = self.leo_c
        self.iconBar: QtWidgets.QToolBar = self.addToolBar("IconBar")
        self.iconBar.setObjectName('icon-bar')  # Required for QMainWindow.saveState().
        self.set_icon_bar_orientation(c)

    #@+node:ekr.20140915062551.19519: *5* dw.set_icon_bar_orientation
    def set_icon_bar_orientation(self, c: Cmdr) -> None:
        """Set the orientation of the icon bar based on settings."""
        d = {
            'bottom': ToolBarArea.BottomToolBarArea,
            'left': ToolBarArea.LeftToolBarArea,
            'right': ToolBarArea.RightToolBarArea,
            'top': ToolBarArea.TopToolBarArea,
        }
        where_s = self.toolbar_orientation
        if not where_s:
            where_s = 'top'
        where = d.get(where_s.lower())
        if where:
            self.addToolBar(where, self.iconBar)
    #@+node:ekr.20110605121601.18145: *4* dw.createLogPane & helpers
    def createLogPane(self, parent: QWidget) -> None:
        """Create all parts of Leo's log pane."""
        c = self.leo_c
        #
        # Create the log frame.
        logFrame = self.createFrame(parent, 'logFrame', vPolicy=Policy.Minimum)
        innerFrame = self.createFrame(logFrame, 'logInnerFrame',
            hPolicy=Policy.Preferred, vPolicy=Policy.Expanding)
        tabWidget = self.createTabWidget(innerFrame, 'logTabWidget')
        #
        # Pack.
        innerGrid = self.createGrid(innerFrame, 'logInnerGrid')
        innerGrid.addWidget(tabWidget, 0, 0, 1, 1)
        outerGrid = self.createGrid(logFrame, 'logGrid')
        outerGrid.addWidget(innerFrame, 0, 0, 1, 1)
        #
        # Create the Find tab, embedded in a QScrollArea.
        findScrollArea = QtWidgets.QScrollArea()
        findScrollArea.setObjectName('findScrollArea')
        # Find tab.
        findTab = QtWidgets.QWidget()
        findTab.setObjectName('findTab')
        #
        # #516 and #1507: Create a Find tab unless we are using a dialog.
        #
        # Careful: @bool minibuffer-ding-mode overrides @bool use-find-dialog.
        use_minibuffer = c.config.getBool('minibuffer-find-mode', default=False)
        use_dialog = c.config.getBool('use-find-dialog', default=False)
        if use_minibuffer or not use_dialog:
            tabWidget.addTab(findScrollArea, 'Find')
        # Complete the Find tab in LeoFind.finishCreate.
        self.findScrollArea = findScrollArea
        self.findTab = findTab
        #
        # Spell tab.
        spellTab = QtWidgets.QWidget()
        spellTab.setObjectName('spellTab')
        tabWidget.addTab(spellTab, 'Spell')
        self.createSpellTab(spellTab)
        tabWidget.setCurrentIndex(1)
        #
        # Official ivars
        self.tabWidget = tabWidget  # Used by LeoQtLog.
    #@+node:ekr.20131118172620.16858: *5* dw.finishCreateLogPane
    def finishCreateLogPane(self) -> None:
        """It's useful to create this late, because c.config is now valid."""
        assert self.findTab
        self.createFindTab(self.findTab, self.findScrollArea)
        self.findScrollArea.setWidget(self.findTab)
    #@+node:ekr.20110605121601.18146: *4* dw.createMainLayout
    def createMainLayout(self, parent: QWidget) -> tuple[QWidget, QWidget]:
        """Create the layout for Leo's main window."""
        # c = self.leo_c
        main_splitter = self.createMainSplitter(parent)
        secondary_splitter = self.createSecondarySplitter(main_splitter)

        #  Add the main splitter to the vertical layout!
        self.verticalLayout = self.createVLayout(parent, 'mainVLayout', margin=3)
        self.set_widget_size_policy(secondary_splitter)
        self.verticalLayout.addWidget(main_splitter)

        return main_splitter, secondary_splitter
    #@+node:ekr.20240729064156.1: *4* dw.createMainSplitter
    def createMainSplitter(self, parent: QWidget) -> QtWidgets.QSplitter:

        main_splitter = QtWidgets.QSplitter(parent)
        main_splitter.setObjectName('main_splitter')
        main_splitter.setOrientation(Orientation.Vertical)
        return main_splitter
    #@+node:ekr.20240729064421.1: *4* dw.createSecondarySplitter
    def createSecondarySplitter(self, parent: QWidget) -> QtWidgets.QSplitter:

        secondary_splitter = QtWidgets.QSplitter(parent)
        secondary_splitter.setObjectName('secondary_splitter')
        return secondary_splitter
    #@+node:ekr.20110605121601.18148: *4* dw.createMiniBuffer (class VisLineEdit)
    def createMiniBuffer(self, parent: QWidget) -> QWidget:
        """Create the widgets for Leo's minibuffer area."""
        # Create widgets.
        frame = self.createFrame(parent, 'minibufferFrame',
            hPolicy=Policy.MinimumExpanding, vPolicy=Policy.Fixed)
        frame.setMinimumSize(QtCore.QSize(100, 0))
        label = self.createLabel(frame, 'minibufferLabel', 'Minibuffer:')


        class VisLineEdit(QtWidgets.QLineEdit):
            """In case user has hidden minibuffer with gui-minibuffer-hide"""

            def focusInEvent(self, event: QFocusEvent) -> None:
                self.parent().show()
                super().focusInEvent(event)  # Call the base class method.

            def focusOutEvent(self, event: QFocusEvent) -> None:
                self.store_selection()
                super().focusOutEvent(event)

            def restore_selection(self) -> None:
                w = self
                i, j, ins = self._sel_and_insert
                if i == j:
                    w.setCursorPosition(i)
                else:
                    length = j - i
                    # Set selection is a QLineEditMethod
                    if ins < j:
                        w.setSelection(j, -length)
                    else:
                        w.setSelection(i, length)

            def store_selection(self) -> None:
                w = self
                ins = w.cursorPosition()
                if w.hasSelectedText():
                    i = w.selectionStart()
                    s = w.selectedText()
                    j = i + len(s)
                else:
                    i = j = ins
                w._sel_and_insert = (i, j, ins)

        lineEdit = VisLineEdit(frame)
        lineEdit._sel_and_insert = (0, 0, 0)
        lineEdit.setObjectName('lineEdit')  # name important.
        # Pack.
        hLayout = self.createHLayout(frame, 'minibufferHLayout', spacing=4)
        hLayout.setContentsMargins(3, 2, 2, 0)
        hLayout.addWidget(label)
        hLayout.addWidget(lineEdit)
        self.verticalLayout.addWidget(frame)
        # Transfers focus request from label to lineEdit.
        label.setBuddy(lineEdit)
        #
        # Official ivars.
        self.lineEdit = lineEdit
        self.leo_minibuffer_frame = frame
        # self.leo_minibuffer_layout = layout
        return frame
    #@+node:ekr.20110605121601.18147: *4* dw.createMenuBar
    def createMenuBar(self) -> None:
        """Create Leo's menu bar."""
        dw = self
        w = QtWidgets.QMenuBar(dw)
        w.setNativeMenuBar(platform.system() == 'Darwin')
        w.setGeometry(QtCore.QRect(0, 0, 957, 22))
        w.setObjectName("menubar")
        dw.setMenuBar(w)
        # Official ivars.
        self.leo_menubar = w
    #@+node:ekr.20110605121601.18149: *4* dw.createOutlinePane
    def createOutlinePane(self, parent: QWidget) -> QWidget:
        """Create the widgets and ivars for Leo's outline."""
        # Create widgets.
        treeFrame = self.createFrame(parent, 'outlineFrame', vPolicy=Policy.Expanding)
        innerFrame = self.createFrame(treeFrame, 'outlineInnerFrame', hPolicy=Policy.Preferred)
        treeWidget = self.createTreeWidget(innerFrame, 'treeWidget')
        grid = self.createGrid(treeFrame, 'outlineGrid')
        grid.addWidget(innerFrame, 0, 0, 1, 1)
        innerGrid = self.createGrid(innerFrame, 'outlineInnerGrid')
        innerGrid.addWidget(treeWidget, 0, 0, 1, 1)
        # Official ivars...
        self.treeWidget = treeWidget
        return treeFrame
    #@+node:ekr.20110605121601.18150: *4* dw.createStatusBar
    def createStatusBar(self, parent: QWidget) -> None:
        """Create the widgets and ivars for Leo's status area."""
        w = QtWidgets.QStatusBar(parent)
        w.setObjectName("statusbar")
        parent.setStatusBar(w)
        # Official ivars.
        self.leo_statusBar = w
    #@+node:ekr.20240726174902.1: *4* dw.createVRPanes (new)
    def createVRPanes(self) -> list[QtWidgets.QFrame]:
        """
        Create the VR and/or the VR3 panes if either plugin is enabled.

        Return a list containing the panes.

        The caller is responsible for placing the panes in the properly place.
        """
        panes: list[QtWidgets.QFrame] = []

        return panes

    #@+node:ekr.20110605121601.18212: *4* dw.packLabel
    def packLabel(self, w: QWidget, n: int = None) -> None:
        """
        Pack w into the body frame's QVGridLayout.

        The type of w does not affect the following code. In fact, w is a
        QTextBrowser possibly packed inside a LeoLineTextWidget.
        """
        c = self.leo_c
        #
        # Reuse the grid layout in the body frame.
        grid = self.leo_body_frame.layout()
        # Pack the label and the text widget.
        label = QtWidgets.QLineEdit(None)
        label.setObjectName('editorLabel')
        label.setText(c.p.h)
        if n is None:
            n = c.frame.body.numberOfEditors
        n = max(0, n - 1)
        # mypy error: grid is a QGridLayout, not a QLayout.
        grid.addWidget(label, 0, n)  # type:ignore
        grid.addWidget(w, 1, n)  # type:ignore
        grid.setRowStretch(0, 0)  # Don't grow the label vertically.
        grid.setRowStretch(1, 1)  # Give row 1 as much as vertical room as possible.
        # Inject the ivar.
        w.leo_label = label
    #@+node:ekr.20110605121601.18151: *4* dw.setMainWindowOptions
    def setMainWindowOptions(self) -> None:
        """Set default options for Leo's main window."""
        dw = self
        dw.setObjectName("MainWindow")
        dw.resize(691, 635)
    #@+node:ekr.20110605121601.18168: *3* dw: utils
    #@+node:ekr.20110605121601.18178: *4* dw.set_geometry
    # Mypy complaint because this overrides QMainWindow.setGeometry.

    def setGeometry(self, rect: QRect) -> None:  # type:ignore
        """Set the window geometry, but only once when using the qt gui."""
        m = self.leo_master
        assert self.leo_master
        # Only set the geometry once, even for new files.
        if not hasattr(m, 'leo_geom_inited'):
            m.leo_geom_inited = True
            self.leo_master.setGeometry(rect)
            super().setGeometry(rect)
    #@+node:ekr.20110605121601.18170: *4* dw.set_widget_size_policy
    def set_widget_size_policy(self, widget: QWidget, kind1: Policy = None, kind2: Policy = None) -> None:
        if kind1 is None:
            kind1 = Policy.Ignored
        if kind2 is None:
            kind2 = Policy.Ignored
        sizePolicy = QtWidgets.QSizePolicy(kind1, kind2)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(widget.sizePolicy().hasHeightForWidth())
        widget.setSizePolicy(sizePolicy)
    #@+node:ekr.20110605121601.18177: *4* dw.setLeoWindowIcon
    def setLeoWindowIcon(self) -> None:
        """ Set icon visible in title bar and task bar """
        # self.setWindowIcon(QtGui.QIcon(g.app.leoDir + "/Icons/leoapp32.png"))
        g.app.gui.attachLeoIcon(self)
    #@+node:ekr.20110605121601.18169: *4* dw.setName
    def setName(self, widget: QObject, name: str) -> None:
        if name:
            widget.setObjectName(name)
    #@+node:ekr.20110605121601.18174: *4* dw.setSplitDirection
    def setSplitDirection(self,
        main_splitter: QWidget,
        secondary_splitter: QWidget,
        orientation: str,
    ) -> None:
        """
        Set the orientations of the splitters in the Leo main window.

        Only the legacy layout should use this method!

        """
        # c = self.leo_c
        vert = orientation and orientation.lower().startswith('v')
        h, v = Orientation.Horizontal, Orientation.Vertical
        orientation1 = v if vert else h
        orientation2 = h if vert else v
        main_splitter.setOrientation(orientation1)
        if secondary_splitter:
            secondary_splitter.setOrientation(orientation2)
    #@+node:ekr.20130804061744.12425: *4* dw.setWindowTitle
    if 0:  # Override for debugging only.

        def setWindowTitle(self, s: str) -> None:
            g.trace('***(DynamicWindow)', s, self.parent())
            # Call the base class method.
            QtWidgets.QMainWindow.setWindowTitle(self, s)
    #@+node:ekr.20110605121601.18171: *4* dw.tr (no longer used)
    # def tr(self, s: str) -> str:
        # return QtWidgets.QApplication.translate('MainWindow', s, None)

    #@-others
#@+node:ekr.20131117054619.16698: ** class FindTabManager (qt_frame.py)
class FindTabManager:
    """A helper class for the LeoFind class."""
    #@+others
    #@+node:ekr.20131117120458.16794: *3*  ftm.ctor
    def __init__(self, c: Cmdr) -> None:
        """Ctor for the FindTabManager class."""
        self.c = c
        self.entry_focus = None  # The widget that had focus before find-pane entered.
        # Find/change text boxes.
        self.find_findbox: QWidget = None
        self.find_replacebox: QWidget = None
        # Check boxes.
        self.check_box_ignore_case = None
        self.check_box_mark_changes = None
        self.check_box_mark_finds = None
        self.check_box_regexp = None
        self.check_box_search_body = None
        self.check_box_search_headline = None
        self.check_box_whole_word = None
        # self.check_box_wrap_around = None
        # Radio buttons
        self.radio_button_file_only = None
        self.radio_button_entire_outline = None
        self.radio_button_node_only = None
        self.radio_button_suboutline_only = None
        # Push buttons
        self.find_next_button = None
        self.find_prev_button = None
        self.find_all_button = None
        self.help_for_find_commands_button = None
        self.replace_button = None
        self.replace_then_find_button = None
        self.replace_all_button = None
    #@+node:ekr.20131119185305.16478: *3* ftm.clear_focus & init_focus & set_entry_focus
    def clear_focus(self) -> None:
        self.entry_focus = None
        self.find_findbox.clearFocus()

    def init_focus(self) -> None:
        self.set_entry_focus()
        w = self.find_findbox
        w.setFocus()
        s = w.text()
        w.setSelection(0, len(s))

    def set_entry_focus(self) -> None:
        # Remember the widget that had focus, changing headline widgets
        # to the tree pane widget.  Headline widgets can disappear!
        c = self.c
        w = g.app.gui.get_focus(raw=True)
        if w != c.frame.body.wrapper.widget:
            w = c.frame.tree.treeWidget
        self.entry_focus = w
    #@+node:ekr.20210110143917.1: *3* ftm.get_settings
    def get_settings(self) -> g.Bunch:
        """
        Return a g.bunch representing all widget values.

        Similar to LeoFind.default_settings, but only for find-tab values.
        """
        return g.Bunch(
            # Find/change strings...
            find_text=self.find_findbox.text(),
            change_text=self.find_replacebox.text(),
            # Find options...
            file_only=self.radio_button_file_only.isChecked(),
            ignore_case=self.check_box_ignore_case.isChecked(),
            mark_changes=self.check_box_mark_changes.isChecked(),
            mark_finds=self.check_box_mark_finds.isChecked(),
            node_only=self.radio_button_node_only.isChecked(),
            pattern_match=self.check_box_regexp.isChecked(),
            # reverse = False,
            search_body=self.check_box_search_body.isChecked(),
            search_headline=self.check_box_search_headline.isChecked(),
            suboutline_only=self.radio_button_suboutline_only.isChecked(),
            whole_word=self.check_box_whole_word.isChecked(),
            # wrapping = self.check_box_wrap_around.isChecked(),
        )
    #@+node:ekr.20131117120458.16789: *3* ftm.init_widgets (creates callbacks)
    def init_widgets(self) -> None:
        """
        Init widgets and ivars from c.config settings.
        Create callbacks that always keep the LeoFind ivars up to date.
        """
        c = self.c
        find = c.findCommands
        # Find/change text boxes.
        table1 = (
            ('find_findbox', 'find_text', '<find pattern here>'),
            ('find_replacebox', 'change_text', ''),
        )
        for ivar, setting_name, default in table1:
            s = c.config.getString(setting_name) or default
            w = getattr(self, ivar)
            w.insert(s)
            if find.minibuffer_mode:
                w.clearFocus()
            else:
                w.setSelection(0, len(s))
        # Check boxes.
        table2 = (
            ('ignore_case', self.check_box_ignore_case),
            ('mark_changes', self.check_box_mark_changes),
            ('mark_finds', self.check_box_mark_finds),
            ('pattern_match', self.check_box_regexp),
            ('search_body', self.check_box_search_body),
            ('search_headline', self.check_box_search_headline),
            ('whole_word', self.check_box_whole_word),
            # ('wrap', self.check_box_wrap_around),
        )
        for setting_name, w in table2:
            val = c.config.getBool(setting_name, default=False)
            # The setting name is also the name of the LeoFind ivar.
            assert hasattr(find, setting_name), setting_name
            setattr(find, setting_name, val)
            if val:
                w.toggle()

            def check_box_callback(n: int, setting_name: str = setting_name, w: str = w) -> None:
                # The focus has already change when this gets called.
                # focus_w = QtWidgets.QApplication.focusWidget()
                val = w.isChecked()
                assert hasattr(find, setting_name), setting_name
                setattr(find, setting_name, val)
                # Too kludgy: we must use an accurate setting.
                # It would be good to have an "about to change" signal.
                # Put focus in minibuffer if minibuffer find is in effect.
                c.bodyWantsFocusNow()

            w.stateChanged.connect(check_box_callback)
        # Radio buttons
        table3 = (
            ('node_only', 'node_only', self.radio_button_node_only),
            ('entire_outline', None, self.radio_button_entire_outline),
            ('suboutline_only', 'suboutline_only', self.radio_button_suboutline_only),
            ('file_only', 'file_only', self.radio_button_file_only)
        )
        for setting_name, ivar, w in table3:
            val = c.config.getBool(setting_name, default=False)
            # The setting name is also the name of the LeoFind ivar.
            if ivar is not None:
                assert hasattr(find, setting_name), setting_name
                setattr(find, setting_name, val)
                w.toggle()

            def radio_button_callback(
                n: int, ivar: str = ivar, setting_name: str = setting_name, w: str = w
            ) -> None:
                val = w.isChecked()
                if ivar:
                    assert hasattr(find, ivar), ivar
                    setattr(find, ivar, val)

            w.toggled.connect(radio_button_callback)
        # Ensure one radio button is set.
        if not find.node_only and not find.suboutline_only and not find.file_only:
            w = self.radio_button_entire_outline
            w.toggle()
    #@+node:ekr.20210923060904.1: *3* ftm.set_widgets_from_dict
    def set_widgets_from_dict(self, d: g.Bunch) -> None:
        """Set all settings from d."""
        # Similar to ftm.init_widgets, which has already been called.
        c = self.c
        find = c.findCommands
        # Set find text.
        find_text = d.get('find_text')
        self.set_find_text(find_text)
        find.find_text = find_text
        # Set change text.
        change_text = d.get('change_text')
        self.set_change_text(change_text)
        find.change_text = change_text
        # Check boxes...
        table1 = (
            ('ignore_case', self.check_box_ignore_case),
            ('mark_changes', self.check_box_mark_changes),
            ('mark_finds', self.check_box_mark_finds),
            ('pattern_match', self.check_box_regexp),
            ('search_body', self.check_box_search_body),
            ('search_headline', self.check_box_search_headline),
            ('whole_word', self.check_box_whole_word),
        )
        for setting_name, w in table1:
            val = d.get(setting_name, False)
            # The setting name is also the name of the LeoFind ivar.
            assert hasattr(find, setting_name), setting_name
            setattr(find, setting_name, val)
            w.setChecked(val)
        # Radio buttons...
        table2 = (
            ('node_only', 'node_only', self.radio_button_node_only),
            ('entire_outline', None, self.radio_button_entire_outline),
            ('suboutline_only', 'suboutline_only', self.radio_button_suboutline_only),
            ('file_only', 'file_only', self.radio_button_file_only),
        )
        for setting_name, ivar, w in table2:
            val = d.get(setting_name, False)
            # The setting name is also the name of the LeoFind ivar.
            if ivar is not None:
                assert hasattr(find, setting_name), setting_name
                setattr(find, setting_name, val)
                w.setChecked(val)
        # Ensure one radio button is set.
        if not find.node_only and not find.suboutline_only and not find.file_only:
            w = self.radio_button_entire_outline
            w.setChecked(True)
    #@+node:ekr.20210312120503.1: *3* ftm.set_body_and_headline_checkbox
    def set_body_and_headline_checkbox(self) -> None:
        """Return the search-body and search-headline checkboxes to their defaults."""
        # #1840: headline-only one-shot
        c = self.c
        find = c.findCommands
        if not find:
            return
        table = (
            ('search_body', self.check_box_search_body),
            ('search_headline', self.check_box_search_headline),
        )
        for setting_name, w in table:
            val = c.config.getBool(setting_name, default=False)
            if val != w.isChecked():
                w.toggle()
        if find.minibuffer_mode:
            find.show_find_options_in_status_area()
    #@+node:ekr.20150619082825.1: *3* ftm.set_ignore_case
    def set_ignore_case(self, aBool: bool) -> None:
        """Set the ignore-case checkbox to the given value."""
        c = self.c
        c.findCommands.ignore_case = aBool
        w = self.check_box_ignore_case
        w.setChecked(aBool)
    #@+node:ekr.20131117120458.16792: *3* ftm.set_radio_button
    def set_radio_button(self, name: str) -> None:
        """Set the value of the radio buttons"""
        c = self.c
        find = c.findCommands
        d = {
            # Name is not an ivar. Set by find.setFindScope... commands.
            'file-only': self.radio_button_file_only,
            'node-only': self.radio_button_node_only,
            'entire-outline': self.radio_button_entire_outline,
            'suboutline-only': self.radio_button_suboutline_only,
        }
        w = d.get(name)
        # Most of the work will be done in the radio button callback.
        if not w.isChecked():
            w.toggle()
        if find.minibuffer_mode:
            find.show_find_options_in_status_area()
    #@+node:ekr.20131117164142.16853: *3* ftm.text getters/setters
    def get_find_text(self) -> str:
        s = self.find_findbox.text()
        if s and s[-1] in ('\r', '\n'):
            s = s[:-1]
        return s

    def get_change_text(self) -> str:
        s = self.find_replacebox.text()
        if s and s[-1] in ('\r', '\n'):
            s = s[:-1]
        return s

    getChangeText = get_change_text

    def set_find_text(self, s: str) -> None:
        w = self.find_findbox
        s = g.checkUnicode(s or '')
        w.clear()
        w.insert(s)

    def set_change_text(self, s: str) -> None:
        w = self.find_replacebox
        s = g.checkUnicode(s or '')
        w.clear()
        w.insert(s)
    #@+node:ekr.20131117120458.16791: *3* ftm.toggle_checkbox
    #@@nobeautify

    def toggle_checkbox(self, checkbox_name: str) -> None:
        """Toggle the value of the checkbox whose name is given."""
        c = self.c
        find = c.findCommands
        if not find:
            return
        d = {
            'ignore_case':     self.check_box_ignore_case,
            'mark_changes':    self.check_box_mark_changes,
            'mark_finds':      self.check_box_mark_finds,
            'pattern_match':   self.check_box_regexp,
            'search_body':     self.check_box_search_body,
            'search_headline': self.check_box_search_headline,
            'whole_word':      self.check_box_whole_word,
            # 'wrap':            self.check_box_wrap_around,
        }
        w = d.get(checkbox_name)
        assert w
        assert hasattr(find, checkbox_name), checkbox_name
        w.toggle() # The checkbox callback toggles the ivar.
        if find.minibuffer_mode:
            find.show_find_options_in_status_area()
    #@-others
#@+node:ekr.20131115120119.17376: ** class LeoBaseTabWidget(QTabWidget)
class LeoBaseTabWidget(QtWidgets.QTabWidget):
    """Base class for all QTabWidgets in Leo."""
    #@+others
    #@+node:ekr.20131115120119.17390: *3* qt_base_tab.__init__
    def __init__(self, *args: Args, **kwargs: KWargs) -> None:
        #
        # Called from frameFactory.createMaster.
        #
        self.factory = kwargs.get('factory')
        if self.factory:
            del kwargs['factory']
        super().__init__(*args, **kwargs)
        self.detached: list[tuple[str, QWidget]] = []
        self.setMovable(True)

        def tabContextMenu(point: QPoint) -> None:
            index = self.tabBar().tabAt(point)
            if index < 0:  # or (self.count() < 1 and not self.detached):
                return
            menu = QtWidgets.QMenu()
            # #310: Create new file on right-click in file tab in UI.
            a = menu.addAction("New Outline")
            a.triggered.connect(lambda checked: self.new_outline(index))
            if self.count() > 1:
                a = menu.addAction("Detach")
                a.triggered.connect(lambda checked: self.detach(index))
                # #2914: These no longer make sense.
                    # a = menu.addAction("Horizontal tile")
                    # a.triggered.connect(lambda checked: self.tile(index, orientation='H'))
                    # a = menu.addAction("Vertical tile")
                    # a.triggered.connect(lambda checked: self.tile(index, orientation='V'))
            if self.detached:
                a = menu.addAction("Re-attach All")
                a.triggered.connect(lambda checked: self.reattach_all())

            global_point = self.mapToGlobal(point)
            menu.exec(global_point)

        self.setContextMenuPolicy(ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(tabContextMenu)
    #@+node:ekr.20180123082452.1: *3* qt_base_tab.new_outline
    def new_outline(self, index: int) -> None:
        """Open a new outline tab."""
        w = self.widget(index)
        c = w.leo_c
        c.new()
    #@+node:ekr.20131115120119.17391: *3* qt_base_tab.detach
    def detach(self, index: int) -> QWidget:  # A QIcon.
        """detach tab (from tab's context menu)"""
        w = self.widget(index)
        name = self.tabText(index)
        self.detached.append((name, w))
        self.factory.detachTab(w)
        icon = g.app.gui.getImageFinder("application-x-leo-outline.png")
        icon = QtGui.QIcon(icon)
        if icon:
            w.window().setWindowIcon(icon)
        c = w.leo_c
        if c.styleSheetManager:
            c.styleSheetManager.set_style_sheets(w=w)
        if platform.system() == 'Windows':
            # Windows (XP and 7) put the windows title bar off screen.
            w.move(20, 20)
        return w
    #@+node:ekr.20131115120119.17393: *3* qt_base_tab.reattach_all
    def reattach_all(self) -> None:
        """reattach all detached tabs"""
        for name, w in self.detached:
            self.addTab(w, name)
            self.factory.leoFrames[w] = w.leo_c.frame
        self.detached = []
    #@+node:ekr.20131115120119.17394: *3* qt_base_tab.delete
    def delete(self, w: QWidget) -> None:
        """called by TabbedFrameFactory to tell us a detached tab
        has been deleted"""
        self.detached = [i for i in self.detached if i[1] != w]
    #@+node:ekr.20131115120119.17395: *3* qt_base_tab.setChanged
    def setChanged(self, c: Cmdr, changed: bool) -> None:
        """Set the changed indicator in c's tab."""
        # Find the tab corresponding to c.
        dw = c.frame.top  # A DynamicWindow
        i = self.indexOf(dw)
        if i < 0:
            return
        s = self.tabText(i)
        if len(s) > 2:
            if changed:
                if not s.startswith('* '):
                    title = "* " + s
                    self.setTabText(i, title)
            else:
                if s.startswith('* '):
                    title = s[2:]
                    self.setTabText(i, title)
    #@+node:ekr.20131115120119.17396: *3* qt_base_tab.setTabName
    def setTabName(self, c: Cmdr, fileName: str) -> None:
        """Set the tab name for c's tab to fileName."""
        # Find the tab corresponding to c.
        dw = c.frame.top  # A DynamicWindow
        i = self.indexOf(dw)
        if i > -1:
            self.setTabText(i, g.shortFileName(fileName))
    #@+node:ekr.20131115120119.17397: *3* qt_base_tab.closeEvent
    def closeEvent(self, event: QEvent) -> None:
        """Handle a close event."""
        g.app.gui.close_event(event)
    #@+node:ekr.20131115120119.17398: *3* qt_base_tab.select (leoTabbedTopLevel)
    def select(self, c: Cmdr) -> None:
        """Select the tab for c."""
        dw = c.frame.top  # A DynamicWindow
        i = self.indexOf(dw)
        self.setCurrentIndex(i)
        # Fix bug 844953: tell Unity which menu to use.
            # c.enableMenuBar()
    #@-others
#@+node:ekr.20110605121601.18180: ** class LeoQtBody(leoFrame.LeoBody)
class LeoQtBody(leoFrame.LeoBody):
    """A class that represents the body pane of a Qt window."""
    #@+others
    #@+node:ekr.20110605121601.18182: *3* LeoQtBody.ctor & helpers
    def __init__(self, frame: LeoQtFrame, parentFrame: QWidget) -> None:
        """Ctor for LeoQtBody class."""
        # Call the base class constructor.
        super().__init__(frame, parentFrame)
        c = self.c
        assert c.frame == frame and frame.c == c
        self.colorizer: BaseColorizer = None
        self.wrapper: QtWrapper = None
        self.widget: QWidget = None
        self.reloadSettings()
        self.set_widget()  # Sets self.widget and self.wrapper.
        self.setWrap(c.p)
    #@+node:ekr.20110605121601.18185: *4* LeoQtBody.get_name
    def getName(self) -> str:
        return 'body-widget'
    #@+node:ekr.20140901062324.18562: *4* LeoQtBody.reloadSettings
    def reloadSettings(self) -> None:
        c = self.c
        self.useScintilla = c.config.getBool('qt-use-scintilla')
        self.use_chapters = c.config.getBool('use-chapters')
        self.use_gutter = c.config.getBool('use-gutter', default=False)
    #@+node:ekr.20160309074124.1: *4* LeoQtBody.set_invisibles
    def set_invisibles(self, c: Cmdr) -> None:
        """Set the show-invisibles bit in the document."""
        d = c.frame.body.wrapper.widget.document()
        option = QtGui.QTextOption()
        if c.frame.body.colorizer.showInvisibles:
            option.setFlags(option.Flag.ShowTabsAndSpaces)
        d.setDefaultTextOption(option)
    #@+node:ekr.20140901062324.18563: *4* LeoQtBody.set_widget
    def set_widget(self) -> None:
        """Set the actual gui widget."""
        c = self.c
        top = c.frame.top
        sw = getattr(top, 'stackedWidget', None)
        if sw:
            sw.setCurrentIndex(1)
        if self.useScintilla and not Qsci:
            g.trace('Can not import Qsci: ignoring @bool qt-use-scintilla')
        if self.useScintilla and Qsci:
            # A Qsci.QsciSintilla object.
            # dw.createText sets self.scintilla_widget
            self.widget = c.frame.top.scintilla_widget
            self.wrapper = qt_text.QScintillaWrapper(self.widget, name='body', c=c)
            self.colorizer = leoColorizer.QScintillaColorizer(c, self.widget)
        else:
            self.widget = top.richTextEdit  # A LeoQTextBrowser
            self.wrapper = qt_text.QTextEditWrapper(self.widget, name='body', c=c)
            self.widget.setAcceptRichText(False)
            self.colorizer = leoColorizer.make_colorizer(c, self.widget)
    #@+node:ekr.20110605121601.18183: *4* LeoQtBody.forceWrap and setWrap
    def forceWrap(self, p: Position) -> None:
        """Set **only** the wrap bits in the body."""
        if not p or self.useScintilla:
            return
        c = self.c
        w = c.frame.body.wrapper.widget
        wrap = WrapMode.WrapAtWordBoundaryOrAnywhere
        w.setWordWrapMode(wrap)

    def setWrap(self, p: Position) -> None:
        """Set **only** the wrap bits in the body."""
        if not p or self.useScintilla:
            return
        c = self.c
        w = c.frame.body.wrapper.widget
        wrap = c.getWrap(p)
        policy = ScrollBarPolicy.ScrollBarAlwaysOff if wrap else ScrollBarPolicy.ScrollBarAsNeeded
        w.setHorizontalScrollBarPolicy(policy)
        wrap_setting = WrapMode.WrapAtWordBoundaryOrAnywhere if wrap else WrapMode.NoWrap
        w.setWordWrapMode(wrap_setting)
    #@+node:ekr.20110605121601.18223: *3* LeoQtBody.Event handlers
    #@+node:ekr.20110930174206.15472: *4* LeoQtBody.onFocusIn
    def onFocusIn(self, obj: QObject) -> None:
        """Handle a focus-in event in the body pane."""
        if obj.objectName() == 'richTextEdit':
            self.onFocusColorHelper('focus-in', obj)
            if hasattr(obj, 'leo_copy_button') and obj.leo_copy_button:
                obj.setReadOnly(True)
            else:
                obj.setReadOnly(False)
            obj.setFocus()  # Weird, but apparently necessary.
    #@+node:ekr.20110930174206.15473: *4* LeoQtBody.onFocusOut
    def onFocusOut(self, obj: QObject) -> None:
        """Handle a focus-out event in the body pane."""
        # Apparently benign.
        if obj.objectName() == 'richTextEdit':
            self.onFocusColorHelper('focus-out', obj)
            if hasattr(obj, 'setReadOnly'):
                obj.setReadOnly(True)
    #@+node:ekr.20110605121601.18224: *4* LeoQtBody.qtBody.onFocusColorHelper (revised)
    def onFocusColorHelper(self, kind: str, obj: QObject) -> None:
        """Handle changes of style when focus changes."""
        c, vc = self.c, self.c.vimCommands
        if vc and c.vim_mode:
            try:
                assert kind in ('focus-in', 'focus-out')
                w = c.frame.body.wrapper.widget
                vc.set_border(w=w, activeFlag=kind == 'focus-in')
            except Exception:
                # g.es_exception()
                pass
    #@-others
#@+node:ekr.20110605121601.18245: ** class LeoQtFrame (LeoFrame)
class LeoQtFrame(leoFrame.LeoFrame):
    """A class that represents a Leo window rendered in qt."""
    #@+others
    #@+node:ekr.20110605121601.18246: *3*  LeoQtFrame.Birth & Death
    #@+node:ekr.20110605121601.18253: *4* Destroying the LeoQtFrame
    #@+node:ekr.20110605121601.18256: *5* LeoQtFrame.destroySelf
    def destroySelf(self) -> None:
        # Remember these: we are about to destroy all of our ivars!
        c, top = self.c, self.top
        if hasattr(g.app.gui, 'frameFactory'):
            g.app.gui.frameFactory.deleteFrame(top)
        # Indicate that the commander is no longer valid.
        c.exists = False
        top.close()
    #@+node:ekr.20110605121601.18247: *4* LeoQtFrame.__init__ & reloadSettings
    def __init__(self, c: Cmdr, title: str, gui: LeoGui) -> None:
        super().__init__(c, gui)
        assert self.c == c
        leoFrame.LeoFrame.instances += 1  # Increment the class var.

        # Official ivars for objects.
        self.bar1: LeoQtFrame = None
        self.bar2: LeoQtFrame = None
        self.body: LeoQtBody = None
        self.iconBar: QtIconBarClass = None
        self.iconFrame: QtIconBarClass = None
        self.log: LeoQtLog = None
        self.statusLine: QtStatusLineClass = None
        self.tree: LeoQtTree = None
        self.top: DynamicWindow = None

        # Status ivars...
        self.title = title
        self.initComplete = False  # Set by initCompleteHint().
        self.minibufferVisible = True
        self.controlKeyIsDown = False  # For control-drags
        self.redrawCount = 0

        # Init settings.
        self.reloadSettings()

    def reloadSettings(self) -> None:
        c = self.c
        self.cursorStay = c.config.getBool("cursor-stay-on-paste", default=True)
        self.use_chapters = c.config.getBool('use-chapters')
        self.use_chapter_tabs = c.config.getBool('use-chapter-tabs')
    #@+node:ekr.20110605121601.18249: *4* LeoQtFrame.__repr__
    def __repr__(self) -> str:
        return f"<LeoQtFrame: {self.title}>"
    #@+node:ekr.20250328195727.1: *4* LeoQtFrame.getIconBar
    def getIconBar(self) -> QtIconBarClass:
        return self.iconBar

    getIconBarObject = getIconBar
    #@+node:ekr.20110605121601.18250: *4* LeoQtFrame.finishCreate & helpers
    def finishCreate(self) -> None:
        """Finish creating the outline's frame."""
        # Called from app.newCommander, Commands.__init__
        t1 = time.process_time()
        c = self.c
        assert c
        frameFactory = g.app.gui.frameFactory
        if not frameFactory.masterFrame:
            frameFactory.createMaster()
        self.top = frameFactory.createFrame(leoFrame=self)
        self.iconBar = QtIconBarClass(c, None)
        self.createSplitterComponents()
        self.statusLine = QtStatusLineClass(c, None)
        self.createFirstTreeNode()  # Call the base-class method.
        self.menu = LeoQtMenu(c, self, label='top-level-menu')
        g.app.windowList.append(self)
        t2 = time.process_time()
        self.setQtStyle()  # Slow, but only the first time it is called.
        t3 = time.process_time()
        self.miniBufferWidget = qt_text.QMinibufferWrapper(c)
        c.bodyWantsFocus()
        t4 = time.process_time()
        if 'speed' in g.app.debug:
            print('qtFrame.finishCreate')
            print(
                f"    1: {t2-t1:5.2f}\n"  # 0.20 sec: before.
                f"    2: {t3-t2:5.2f}\n"  # 0.19 sec: setQtStyle (only once)
                f"    3: {t4-t3:5.2f}\n"  # 0.00 sec: after.
                f"total: {t4-t1:5.2f}"
            )
    #@+node:ekr.20110605121601.18251: *5* LeoQtFrame.createSplitterComponents
    def createSplitterComponents(self) -> None:

        c = self.c
        self.tree = LeoQtTree(c, self)
        self.log = LeoQtLog(self, None)
        self.body = LeoQtBody(self, None)
        self.splitVerticalFlag, ratio, secondary_ratio = self.initialRatios()
        self.resizePanesToRatio(ratio, secondary_ratio)
    #@+node:ekr.20190412044556.1: *5* LeoQtFrame.setQtStyle
    def setQtStyle(self) -> None:
        """
        Set the default Qt style.  Based on pyzo code.

        Copyright (C) 2013-2018, the Pyzo development team

        Pyzo is distributed under the terms of the (new) BSD License.
        The full license can be found in 'license.txt'.
        """
        # Fix #1936: very slow new command. Only do this once!
        if g.app.initStyleFlag:
            return
        g.app.initStyleFlag = True
        c = self.c
        trace = 'themes' in g.app.debug
        # Get the requested style name.
        stylename = c.config.getString('qt-style-name') or ''
        if trace:
            g.trace(repr(stylename))
        if not stylename:
            return
        # Return if the style does not exist.
        styles = [z.lower() for z in QtWidgets.QStyleFactory.keys()]
        if stylename.lower() not in styles:
            g.es_print(f"ignoring unknown Qt style name: {stylename!r}")
            g.printObj(styles)
            return
        # Change the style and palette.
        app = g.app.gui.qtApp
        qstyle = app.setStyle(stylename)
        if not qstyle:
            g.es_print(f"failed to set Qt style name: {stylename!r}")

    #@+node:ekr.20110605121601.18252: *4* LeoQtFrame.initCompleteHint
    def initCompleteHint(self) -> None:
        """A kludge: called to enable text changed events."""
        self.initComplete = True
    #@+node:ekr.20110605121601.18274: *3* LeoQtFrame.Configuration
    #@+node:ekr.20240510092709.1: *4* LeoQtFrame.compute_ratio & compute_secondary_ratio
    #@+node:ekr.20240510093119.1: *5* LeoQtFrame.compute_ratio
    def compute_ratio(self) -> float:
        """
        Return ratio of the main Qt splitter or 0.5.
        """
        c = self.c
        gui = g.app.gui
        w = gui.find_widget_by_name(c, 'main_splitter')
        if not w:
            return 0.5
        aList = w.sizes()
        if len(aList) == 2:
            n1, n2 = aList
            # Don't divide by zero.
            ratio = 0.5 if n1 + n2 == 0 else float(n1) / float(n1 + n2)
            return ratio
        return 0.5
    #@+node:ekr.20240510093122.1: *5* LeoQtFrame.compute_secondary_ratio
    def compute_secondary_ratio(self) -> float:
        """
        Return the ratio of the Qt secondary splitter or 0.5.
        """
        c = self.c
        gui = g.app.gui
        w = gui.find_widget_by_name(c, 'secondary_splitter')
        if w is None:
            return 0.5
        aList = w.sizes()
        if len(aList) == 2:
            n1, n2 = aList
            return float(n1) / float(n1 + n2) if n2 > 0 else 0.5
        return 0.5
    #@+node:ekr.20110605121601.18275: *4* LeoQtFrame.configureBar
    def configureBar(self, bar: QMenuBar, verticalFlag: bool) -> None:  # pylint: disable=disallowed-name
        c = self.c
        # Get configuration settings.
        w = c.config.getInt("split-bar-width")
        if not w or w < 1:
            w = 7
        relief = c.config.get("split_bar_relief", "relief")
        if not relief:
            relief = "flat"
        color = c.config.getColor("split-bar-color")
        if not color:
            color = "LightSteelBlue2"
        try:
            if verticalFlag:
                # Panes arranged vertically; horizontal splitter bar
                bar.configure(
                    relief=relief, height=w, bg=color, cursor="sb_v_double_arrow")
            else:
                # Panes arranged horizontally; vertical splitter bar
                bar.configure(
                    relief=relief, width=w, bg=color, cursor="sb_h_double_arrow")
        except Exception:
            # Could be a user error. Use all defaults
            g.es("exception in user configuration for splitbar")
            g.es_exception()
            if verticalFlag:
                # Panes arranged vertically; horizontal splitter bar
                bar.configure(height=7, cursor="sb_v_double_arrow")
            else:
                # Panes arranged horizontally; vertical splitter bar
                bar.configure(width=7, cursor="sb_h_double_arrow")
    #@+node:ekr.20110605121601.18276: *4* LeoQtFrame.configureBarsFromConfig
    def configureBarsFromConfig(self) -> None:
        c = self.c
        w = c.config.getInt("split-bar-width")
        if not w or w < 1:
            w = 7
        relief = c.config.get("split_bar_relief", "relief")
        if not relief or relief == "":
            relief = "flat"
        color = c.config.getColor("split-bar-color")
        if not color or color == "":
            color = "LightSteelBlue2"
        if self.splitVerticalFlag:
            bar1, bar2 = self.bar1, self.bar2
        else:
            bar1, bar2 = self.bar2, self.bar1
        try:
            bar1.configure(relief=relief, height=w, bg=color)
            bar2.configure(relief=relief, width=w, bg=color)
        except Exception:
            # Could be a user error.
            g.es("exception in user configuration for splitbar")
            g.es_exception()
    #@+node:ekr.20110605121601.18277: *4* LeoQtFrame.reconfigureFromConfig
    def reconfigureFromConfig(self) -> None:
        """Init the configuration of the Qt frame from settings."""
        c, frame = self.c, self
        frame.configureBarsFromConfig()
        frame.setTabWidth(c.tab_width)
        c.redraw()
    #@+node:ekr.20110605121601.18278: *4* LeoQtFrame.setInitialWindowGeometry
    def setInitialWindowGeometry(self) -> None:
        """Set the position and size of the frame to config params."""
        c = self.c
        h = c.config.getInt("initial-window-height") or 500
        w = c.config.getInt("initial-window-width") or 600
        x = c.config.getInt("initial-window-left") or 50  # #1190: was 10
        y = c.config.getInt("initial-window-top") or 50  # #1190: was 10
        if h and w and x and y:
            if 'size' in g.app.debug:
                g.trace(w, h, x, y)
            self.setTopGeometry(w, h, x, y)
    #@+node:ekr.20110605121601.18279: *4* LeoQtFrame.setTabWidth
    def setTabWidth(self, w: int) -> None:
        # A do-nothing because tab width is set automatically.
        # It *is* called from Leo's core.
        pass
    #@+node:ekr.20110605121601.18280: *4* LeoQtFrame.forceWrap & setWrap
    def forceWrap(self, p: Position = None) -> None:
        self.c.frame.body.forceWrap(p)

    def setWrap(self, p: Position = None) -> None:
        self.c.frame.body.setWrap(p)
    #@+node:ekr.20110605121601.18281: *4* LeoQtFrame.reconfigurePanes
    def reconfigurePanes(self) -> None:
        c, f = self.c, self
        if f.splitVerticalFlag:
            r = c.config.getRatio("initial-vertical-ratio")
            if r is None or r < 0.0 or r > 1.0:
                r = 0.5
            r2 = c.config.getRatio("initial-vertical-secondary-ratio")
            if r2 is None or r2 < 0.0 or r2 > 1.0:
                r2 = 0.8
        else:
            r = c.config.getRatio("initial-horizontal-ratio")
            if r is None or r < 0.0 or r > 1.0:
                r = 0.3
            r2 = c.config.getRatio("initial-horizontal-secondary-ratio")
            if r2 is None or r2 < 0.0 or r2 > 1.0:
                r2 = 0.8
        f.resizePanesToRatio(r, r2)
    #@+node:ekr.20110605121601.18282: *4* LeoQtFrame.resizePanesToRatio
    def resizePanesToRatio(self, ratio: float, ratio2: float) -> None:
        """Resize splitter1 and splitter2 using the given ratios."""
        self.divideLeoSplitter1(ratio)
        self.divideLeoSplitter2(ratio2)
    #@+node:ekr.20110605121601.18283: *4* LeoQtFrame.divideLeoSplitter1/2
    def divideLeoSplitter1(self, frac: float) -> None:
        """Divide the main splitter."""
        gui = g.app.gui
        c = self.c
        w = gui.find_widget_by_name(c, 'main_splitter')
        if w:
            self.divideAnySplitter(frac, w)

    def divideLeoSplitter2(self, frac: float) -> None:
        """Divide the secondary splitter."""
        gui = g.app.gui
        c = self.c
        w = gui.find_widget_by_name(c, 'secondary_splitter')
        if w:
            self.divideAnySplitter(frac, w)
    #@+node:ekr.20110605121601.18284: *4* LeoQtFrame.divideAnySplitter
    # This is the general-purpose placer for splitters.
    # It is the only general-purpose splitter code in Leo.

    def divideAnySplitter(self, frac: float, splitter: QSplitter) -> None:
        """Set the splitter sizes."""
        sizes = splitter.sizes()
        if len(sizes) != 2:
            # This is not an error: QSplitters may contain more than 2 widgets.
            return
        if frac > 1 or frac < 0:
            # g.trace(f"split ratio [{frac}] out of range 0 <= frac <= 1")
            frac = 0.5
        s1, s2 = sizes
        s = s1 + s2
        s1 = int(s * frac + 0.5)
        s2 = s - s1
        splitter.setSizes([s1, s2])
    #@+node:ekr.20110605121601.18285: *3* LeoQtFrame.Event handlers
    #@+node:ekr.20110605121601.18286: *4* LeoQtFrame.OnCloseLeoEvent
    # Called from quit logic and when user closes the window.
    # Returns True if the close happened.

    def OnCloseLeoEvent(self) -> None:
        f = self
        c = f.c
        if c.inCommand:
            c.requestCloseWindow = True
        else:
            g.app.closeLeoWindow(self)
    #@+node:ekr.20110605121601.18287: *4* LeoQtFrame.OnControlKeyUp/Down
    def OnControlKeyDown(self, event: QEvent = None) -> None:
        self.controlKeyIsDown = True

    def OnControlKeyUp(self, event: QEvent = None) -> None:
        self.controlKeyIsDown = False
    #@+node:ekr.20110605121601.18290: *4* LeoQtFrame.OnActivateTree
    def OnActivateTree(self, event: QEvent = None) -> None:
        pass
    #@+node:ekr.20110605121601.18293: *3* LeoQtFrame.Gui-dependent commands
    #@+node:ekr.20110605121601.18301: *4* LeoQtFrame.Window Menu...
    #@+node:ekr.20110605121601.18302: *5* LeoQtFrame.toggleActivePane
    @frame_cmd('toggle-active-pane')
    def toggleActivePane(self, event: LeoKeyEvent = None) -> None:
        """Toggle the focus between the outline and body panes."""
        frame = self
        c = frame.c
        w = c.get_focus()
        w_name = g.app.gui.widget_name(w)
        if w_name in ('canvas', 'tree', 'treeWidget'):
            c.endEditing()
            c.bodyWantsFocus()
        else:
            c.treeWantsFocus()
    #@+node:ekr.20110605121601.18304: *5* LeoQtFrame.equalSizedPanes
    @frame_cmd('equal-sized-panes')
    def equalSizedPanes(self, event: LeoKeyEvent = None) -> None:
        """Make the outline and body panes have the same size."""
        self.resizePanesToRatio(0.5, self.compute_secondary_ratio())
    #@+node:ekr.20250422154709.1: *5* LeoQtFrame.contract/expandMainSplitter
    @frame_cmd('contract-main-splitter')
    def contractMainSplitter(self, event: LeoKeyEvent = None) -> None:
        """
        Contract the main splitter's first widget, expanding the main splitter's second widget.
        """
        self.resize_main_splitter(-40)

    @frame_cmd('expand-main-splitter')
    def expandMainSplitter(self, event: LeoKeyEvent = None) -> None:
        """
        Expand the main splitter's first widget, contracting the main splitter's second widget.
        """
        self.resize_main_splitter(40)

    def resize_main_splitter(self, delta: int) -> None:
        """Resize the first two widgets of the main splitter."""
        c = self.c
        splitter = g.app.gui.find_widget_by_name(c, 'main_splitter')
        if not splitter:
            return
        sizes = splitter.sizes()
        if len(sizes) < 2:
            return
        sizes[0] += delta
        sizes[1] -= delta
        if sizes[0] >= 0 and sizes[1] >= 0:
            splitter.setSizes(sizes)
    #@+node:ekr.20110605121601.18305: *5* LeoQtFrame.hideLogWindow
    def hideLogWindow(self, event: LeoKeyEvent = None) -> None:
        """Hide the log pane."""
        self.divideLeoSplitter2(0.99)
    #@+node:ekr.20110605121601.18306: *5* LeoQtFrame.minimizeAll
    @frame_cmd('minimize-all')
    def minimizeAll(self, event: LeoKeyEvent = None) -> None:
        """Minimize all Leo's windows."""
        for frame in g.app.windowList:
            self.minimize(frame)

    def minimize(self, frame: LeoQtFrame) -> None:
        # This unit test will fail when run externally.
        if frame and frame.top:
            w = frame.top.leo_master or frame.top
            if g.unitTesting:
                assert hasattr(w, 'setWindowState'), w
            else:
                w.setWindowState(WindowState.WindowMinimized)
    #@+node:ekr.20110605121601.18307: *5* LeoQtFrame.toggleSplitDirection
    @frame_cmd('toggle-split-direction')
    def toggleSplitDirection(self, event: LeoKeyEvent = None) -> None:
        """
        Toggle the split direction in the present Leo window.
        """
        c = self.c
        gui = g.app.gui
        splitter = gui.find_widget_by_name(c, 'main_splitter')
        splitter2 = gui.find_widget_by_name(c, 'secondary_splitter')
        for w in (splitter, splitter2):
            if w.orientation() == Orientation.Vertical:
                w.setOrientation(Orientation.Horizontal)
            else:
                w.setOrientation(Orientation.Vertical)
    #@+node:ekr.20110605121601.18308: *5* LeoQtFrame.resizeToScreen
    @frame_cmd('resize-to-screen')
    def resizeToScreen(self, event: LeoKeyEvent = None) -> None:
        """Resize the Leo window so it fill the entire screen."""
        frame = self
        # This unit test will fail when run externally.
        if frame and frame.top:
            # frame.top.leo_master is a LeoTabbedTopLevel.
            # frame.top is a DynamicWindow.
            w = frame.top.leo_master or frame.top
            if g.unitTesting:
                assert hasattr(w, 'setWindowState'), w
            else:
                w.setWindowState(WindowState.WindowMaximized)
    #@+node:ekr.20110605121601.18311: *3* LeoQtFrame.Qt bindings...
    #@+node:ekr.20190611053431.1: *4* LeoQtFrame.bringToFront
    def bringToFront(self) -> None:
        if 'size' in g.app.debug:
            g.trace()
        self.lift()
    #@+node:ekr.20190611053431.2: *4* LeoQtFrame.deiconify
    def deiconify(self) -> None:
        """Undo --minimized"""
        if 'size' in g.app.debug:
            g.trace(
                'top:', bool(self.top),
                'isMinimized:', self.top and self.top.isMinimized())
        if self.top and self.top.isMinimized():  # Bug fix: 400739.
            self.lift()
    #@+node:ekr.20190611053431.4: *4* LeoQtFrame.get_window_info
    def get_window_info(self) -> tuple[int, int, int, int]:
        """Return the geometry of the top window."""
        f: QWidget
        if getattr(self.top, 'leo_master', None):
            f = self.top.leo_master
        else:
            f = self.top
        rect = f.geometry()
        topLeft = rect.topLeft()
        x, y = topLeft.x(), topLeft.y()
        w, h = rect.width(), rect.height()
        if 'size' in g.app.debug:
            g.trace('\n', w, h, x, y)
        return w, h, x, y
    #@+node:ekr.20190611053431.3: *4* LeoQtFrame.getFocus
    def getFocus(self) -> None:
        return g.app.gui.get_focus(self.c)  # Bug fix: 2009/6/30.
    #@+node:ekr.20190611053431.7: *4* LeoQtFrame.getTitle
    def getTitle(self) -> str:
        # Fix https://bugs.launchpad.net/leo-editor/+bug/1194209
        # For qt, leo_master (a LeoTabbedTopLevel) contains the QMainWindow.
        w = self.top.leo_master
        return w.windowTitle()
    #@+node:ekr.20190611053431.5: *4* LeoQtFrame.iconify
    def iconify(self) -> None:
        if 'size' in g.app.debug:
            g.trace(bool(self.top))
        if self.top:
            self.top.showMinimized()
    #@+node:ekr.20190611053431.6: *4* LeoQtFrame.lift
    def lift(self) -> None:
        if 'size' in g.app.debug:
            g.trace(bool(self.top), self.top and self.top.isMinimized())
        if not self.top:
            return
        if self.top.isMinimized():  # Bug 379141
            self.top.showNormal()
        self.top.activateWindow()
        self.top.raise_()
    #@+node:ekr.20190611053431.8: *4* LeoQtFrame.setTitle
    def setTitle(self, s: str) -> None:
        if self.top:
            # Fix https://bugs.launchpad.net/leo-editor/+bug/1194209
            # When using tabs, leo_master (a LeoTabbedTopLevel) contains the QMainWindow.
            w = self.top.leo_master
            w.setWindowTitle(s)
    #@+node:ekr.20190611053431.9: *4* LeoQtFrame.setTopGeometry
    def setTopGeometry(self, w: int, h: int, x: int, y: int) -> None:
        # self.top is a DynamicWindow.
        if self.top:
            if 'size' in g.app.debug:
                g.trace(w, h, x, y, self.c.shortFileName(), g.callers())
            self.top.setGeometry(QtCore.QRect(x, y, w, h))
    #@+node:ekr.20190611053431.10: *4* LeoQtFrame.update
    def update(self, *args: Args, **keys: KWargs) -> None:
        if 'size' in g.app.debug:
            g.trace(bool(self.top))
        self.top.update()
    #@-others
#@+node:ekr.20110605121601.18312: ** class LeoQtLog (LeoLog)
class LeoQtLog(leoFrame.LeoLog):
    """A class that represents the log pane of a Qt window."""
    #@+others
    #@+node:ekr.20110605121601.18313: *3* LeoQtLog.Birth
    #@+node:ekr.20110605121601.18314: *4* LeoQtLog.__init__ & reloadSettings
    def __init__(self, frame: LeoQtFrame, parentFrame: LeoQtFrame) -> None:
        """Ctor for LeoQtLog class."""
        super().__init__(frame, parentFrame)  # Calls createControl.
        # Set in finishCreate.
        # Important: depending on the log *tab*,
        # logCtrl may be either a wrapper or a widget.
        assert self.logCtrl is None, self.logCtrl
        self.c = c = frame.c  # Also set in the base constructor, but we need it here.
        self.contentsDict: dict[str, QWidget] = {}  # Keys are tab names.
        self.eventFilters: list = []  # Apparently needed to make filters work!
        self.logCtrl: QWidget = None  # A union.
        self.logDict: dict[str, QWidget] = {}  # Keys are tab names.
        self.logWidget: LeoLog = None  # Set in finishCreate.
        self.menu: qt_text.LeoQTextBrowser = None  # A Qt menu that pops up on right clicks in the hull or in tabs.
        self.tabWidget: QTabWidget = c.frame.top.tabWidget  # A QTabWidget that holds all the tabs.
        tw = self.tabWidget

        # Bug 917814: Switching Log Pane tabs is done incompletely.
        tw.currentChanged.connect(self.onCurrentChanged)
        if 0:  # Not needed to make onActivateEvent work.
            # Works only for .tabWidget, *not* the individual tabs!
            theFilter = qt_events.LeoQtEventFilter(c, w=tw, tag='tabWidget')
            tw.installEventFilter(theFilter)
        # Partial fix for bug 1251755: Log-pane refinements
        tw.setMovable(True)
        self.reloadSettings()

    def reloadSettings(self) -> None:
        c = self.c
        self.wrap = bool(c.config.getBool('log-pane-wraps'))
    #@+node:ekr.20110605121601.18315: *4* LeoQtLog.finishCreate
    def finishCreate(self) -> None:
        """Finish creating the LeoQtLog class."""
        c, log, w = self.c, self, self.tabWidget

        # Create the log tab as the leftmost tab.
        log.createTab('Log')
        self.logWidget = self.contentsDict.get('Log')
        logWidget = self.logWidget
        logWidget.setWordWrapMode(WrapMode.WordWrap if self.wrap else WrapMode.NoWrap)
        w.insertTab(0, logWidget, 'Log')  # Required.

        # set up links in log handling
        logWidget.setTextInteractionFlags(
            TextInteractionFlag.LinksAccessibleByMouse
            | TextInteractionFlag.TextEditable
            | TextInteractionFlag.TextSelectableByMouse
        )
        logWidget.setOpenLinks(False)
        logWidget.setOpenExternalLinks(False)
        logWidget.anchorClicked.connect(self.linkClicked)

        # Show the spell tab.
        c.spellCommands.openSpellTab()

        # 794: Clicking Find Tab should do exactly what pushing Ctrl-F does

        def tab_callback(index: int) -> None:
            name = w.tabText(index)
            if name == 'Find':
                c.findCommands.startSearch(event=None)

        w.currentChanged.connect(tab_callback)
        # #1286.
        w.customContextMenuRequested.connect(self.onContextMenu)
    #@+node:ekr.20110605121601.18316: *4* LeoQtLog.getName
    def getName(self) -> str:
        return 'log'  # Required for proper pane bindings.
    #@+node:ekr.20150717102728.1: *3* LeoQtLog: clear-log & dump-log
    @log_cmd('clear-log')
    @log_cmd('log-clear')
    def clearLog(self, event: LeoKeyEvent = None) -> None:
        """Clear the log pane."""
        # self.logCtrl may be either a wrapper or a widget.
        w = self.logCtrl.widget
        if w:
            w.clear()

    @log_cmd('dump-log')
    @log_cmd('log-dump')
    def dumpLog(self, event: LeoKeyEvent = None) -> None:
        """Clear the log pane."""
        # self.logCtrl may be either a wrapper or a widget.
        w = self.logCtrl.widget
        if not w:
            return

        fn = self.c.shortFileName()
        printable = string.ascii_letters + string.digits + string.punctuation + ' '

        def dump(s: str) -> str:
            return ''.join(c if c in printable else r'\x{0:02x}'.format(ord(c)) for c in s)

        g.printObj([dump(z) for z in w.toPlainText().split('\n')], tag=f"{fn}: w.toPlainText")
        g.printObj([f"{dump(z)}<br />" for z in w.toHtml().split('<br />')], tag=f"{fn}: w.toHtml")


    #@+node:ekr.20110605121601.18333: *3* LeoQtLog.color tab stuff
    def createColorPicker(self, tabName: str) -> None:
        g.warning('color picker not ready for qt')
    #@+node:ekr.20110605121601.18334: *3* LeoQtLog.font tab stuff
    #@+node:ekr.20110605121601.18335: *4* LeoQtLog.createFontPicker
    def createFontPicker(self, tabName: str) -> None:
        # log = self
        font, ok = QtWidgets.QFontDialog.getFont()
        if not (font and ok):
            return
        style = font.style()
        style_s: str = ''
        table1 = (
            (Style.StyleNormal, 'normal'),  # #2330.
            (Style.StyleItalic, 'italic'),
            (Style.StyleOblique, 'oblique'))
        for val, name in table1:
            if style == val:
                style_s = name
                break
        weight: int = font.weight()
        weight_s: str = ''
        table2 = (
            (Weight.Light, 'light'),  # #2330.
            (Weight.Normal, 'normal'),
            (Weight.DemiBold, 'demibold'),
            (Weight.Bold, 'bold'),
            (Weight.Black, 'black'))
        for val2, name2 in table2:
            if weight == val2:
                weight_s = name2
                break
        table3 = (
            ('family', str(font.family())),
            ('size  ', font.pointSize()),
            ('style ', style_s),
            ('weight', weight_s),
        )
        for key3, val3 in table3:
            if val3:
                g.es(key3, val3, tabName='Fonts')
    #@+node:ekr.20110605121601.18339: *4* LeoQtLog.hideFontTab
    def hideFontTab(self, event: LeoKeyEvent = None) -> None:
        c = self.c
        c.frame.log.selectTab('Log')
        c.bodyWantsFocus()
    #@+node:ekr.20111120124732.10184: *3* LeoQtLog.isLogWidget
    def isLogWidget(self, w: LeoQtFrame) -> bool:
        val = w == self or w in list(self.contentsDict.values())
        return val
    #@+node:tbnorth.20171220123648.1: *3* LeoQtLog.linkClicked
    def linkClicked(self, link: str) -> None:
        """linkClicked - link clicked in log

        :param QUrl link: link that was clicked
        """
        s = g.toUnicode(link.toString())
        url = urllib.parse.unquote(s)
        g.handleUrl(url, c=self.c)
    #@+node:ekr.20120304214900.9940: *3* LeoQtLog.onCurrentChanged
    def onCurrentChanged(self, idx: int) -> None:

        tabw = self.tabWidget
        w = tabw.widget(idx)

        # #917814: Switching Log Pane tabs is done incompletely
        obj = getattr(w, 'leo_log_wrapper', None)

        # #1161: Don't change logs unless the wrapper is correct.
        if obj and isinstance(obj, qt_text.QTextEditWrapper):
            self.logCtrl = obj
    #@+node:ekr.20200304132424.1: *3* LeoQtLog.onContextMenu
    def onContextMenu(self, point: QPoint) -> None:
        """LeoQtLog: Callback for customContextMenuRequested events."""
        # #1286.
        c, w = self.c, self
        g.app.gui.onContextMenu(c, w, point)
    #@+node:ekr.20110605121601.18321: *3* LeoQtLog.put and helpers
    #@+node:ekr.20110605121601.18322: *4* LeoQtLog.put & helper
    def put(self,
        s: str,
        color: str = None,
        tabName: str = 'Log',
        from_redirect: bool = False,
        nodeLink: str = None,
    ) -> None:
        """
        Put s to the Qt Log widget, converting to html.
        All output to the log stream eventually comes here.

        The from_redirect keyword argument is no longer used.
        """
        c = self.c
        if g.app.quitting or not c or not c.exists:
            return
        #
        # *Note*: For reasons that I don't fully understand,
        #         all lines sent to the log must now end in a newline.
        #
        s = s.rstrip() + '\n'
        color = self.resolve_color(color)
        self.selectTab(tabName or 'Log')
        # Must be done after the call to selectTab.
        wrapper = self.logCtrl
        if not isinstance(wrapper, qt_text.QTextEditWrapper):
            g.trace('BAD wrapper', wrapper.__class__.__name__)
            return
        w = wrapper.widget
        if not isinstance(w, QtWidgets.QTextEdit):
            g.trace('BAD widget', w.__class__.__name__)
            return
        sb = w.horizontalScrollBar()
        s = self.to_html(color, s)
        if nodeLink:
            link = urllib.parse.quote(nodeLink)
            s = f'<a href="{link}" title="{link}">{s}</a>'
        w.moveCursor(MoveOperation.End)
        w.insertHtml(s)
        sb.setSliderPosition(0)  # Force the slider to the initial position.
        w.repaint()  # Slow, but essential.
    #@+node:ekr.20220411085334.1: *5* LeoQtLog.to_html
    def to_html(self, color: str, s: str) -> str:
        """Convert s to html."""
        s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        # #884: Always convert leading blanks and tabs to &nbsp.
        n = len(s) - len(s.lstrip())
        if n > 0 and s.strip():
            s = '&nbsp;' * (n) + s[n:]
        if not self.wrap:
            # Convert all other blanks to &nbsp;
            s = s.replace(' ', '&nbsp;')
        s = s.replace('\n', '<br>')  # The caller is responsible for newlines!
        s = f'<font color="{color}">{s}</font>'
        return s
    #@+node:ekr.20110605121601.18323: *4* LeoQtLog.putnl
    def putnl(self, tabName: str = 'Log') -> None:
        """Put a newline to the Qt log."""
        #
        # This is not called normally.
        if g.app.quitting:
            return
        if tabName:
            self.selectTab(tabName)
        wrapper = self.logCtrl
        if not isinstance(wrapper, qt_text.QTextEditWrapper):
            g.trace('BAD wrapper', wrapper.__class__.__name__)
            return
        w = wrapper.widget
        if not isinstance(w, QtWidgets.QTextEdit):
            g.trace('BAD widget', w.__class__.__name__)
            return
        sb = w.horizontalScrollBar()
        pos = sb.sliderPosition()
        # Not needed!
            # contents = w.toHtml()
            # w.setHtml(contents + '\n')
        w.moveCursor(MoveOperation.End)
        sb.setSliderPosition(pos)
        w.repaint()  # Slow, but essential.
    #@+node:ekr.20220411085427.1: *4* LeoQtLog.resolve_color
    def resolve_color(self, color: str) -> str:
        """Resolve the given color name to an actual color name."""
        c = self.c
        # Note: g.actualColor does all color translation.
        if color:
            color = leoColor.getColor(color)
        if not color:
            # #788: First, fall back to 'log_black_color', not 'black.
            color = c.config.getColor('log-black-color')
            if not color:
                # Should never be necessary.
                color = 'black'
        return color
    #@+node:ekr.20150205181818.5: *4* LeoQtLog.scrollToEnd
    def scrollToEnd(self, tabName: str = 'Log') -> None:
        """Scroll the log to the end."""
        if g.app.quitting:
            return
        if tabName:
            self.selectTab(tabName)
        w = self.logCtrl.widget
        if not w:
            return
        sb = w.horizontalScrollBar()
        pos = sb.sliderPosition()
        w.moveCursor(MoveOperation.End)
        sb.setSliderPosition(pos)
        w.repaint()  # Slow, but essential.
    #@+node:ekr.20110605121601.18324: *3* LeoQtLog.Tab
    #@+node:ekr.20110605121601.18325: *4* LeoQtLog.clearTab
    def clearTab(self, tabName: str, wrap: str = 'none') -> None:
        w = self.logDict.get(tabName)
        if w:
            w.clear()  # w is a QTextBrowser.
    #@+node:ekr.20110605121601.18326: *4* LeoQtLog.createTab
    def createTab(self,
        tabName: str, createText: bool = True, widget: QWidget = None, wrap: str = 'none',
    ) -> QWidget:  # Widget or LeoQTextBrowser.
        """
        Create a new tab in tab widget
        if widget is None, Create a QTextBrowser,
        suitable for log functionality.
        """
        c = self.c
        contents: Any
        if widget is None:
            # widget is subclass of QTextBrowser.
            widget = qt_text.LeoQTextBrowser(parent=None, c=c, wrapper=self)
            # contents is a wrapper.
            contents = qt_text.QTextEditWrapper(widget=widget, name='log', c=c)
            # Inject an ivar into the QTextBrowser that points to the wrapper.
            widget.leo_log_wrapper = contents
            widget.setWordWrapMode(WrapMode.WordWrap if self.wrap else WrapMode.NoWrap)
            widget.setReadOnly(False)  # Allow edits.
            self.logDict[tabName] = widget
            if tabName == 'Log':
                self.logCtrl = contents
                widget.setObjectName('log-widget')
            # Set binding on all log pane widgets.
            g.app.gui.setFilter(c, widget, self, tag='log')
            self.contentsDict[tabName] = widget
            self.tabWidget.addTab(widget, tabName)
        else:
            # #1161: Don't set the wrapper unless it has the correct type.
            contents = widget  # Unlike text widgets, contents is the actual widget.
            if isinstance(contents, qt_text.QTextEditWrapper):
                widget.leo_log_wrapper = widget  # The leo_log_wrapper is the widget itself.
            else:
                widget.leo_log_wrapper = None  # Tell the truth.
            g.app.gui.setFilter(c, widget, contents, 'tabWidget')
            self.contentsDict[tabName] = contents
            self.tabWidget.addTab(contents, tabName)
        return contents
    #@+node:ekr.20110605121601.18328: *4* LeoQtLog.deleteTab
    def deleteTab(self, tabName: str) -> None:
        """
        Delete the tab if it exists.  Otherwise do *nothing*.
        """
        c = self.c
        w = self.tabWidget
        i = self.findTabIndex(tabName)
        if i is None:
            return
        w.removeTab(i)
        self.selectTab('Log')
        c.invalidateFocus()
        c.bodyWantsFocus()
    #@+node:ekr.20190603062456.1: *4* LeoQtLog.findTabIndex
    def findTabIndex(self, tabName: str) -> Optional[int]:
        """Return the tab index for tabName, or None."""
        w = self.tabWidget
        for i in range(w.count()):
            if tabName == w.tabText(i):
                return i
        return None
    #@+node:ekr.20110605121601.18329: *4* LeoQtLog.hideTab
    def hideTab(self, tabName: str) -> None:
        self.selectTab('Log')
    #@+node:ekr.20111122080923.10185: *4* LeoQtLog.orderedTabNames
    def orderedTabNames(self, LeoLog: str = None) -> list[str]:  # Unused: LeoLog
        """Return a list of tab names in the order in which they appear in the QTabbedWidget."""
        w = self.tabWidget
        return [w.tabText(i) for i in range(w.count())]
    #@+node:ekr.20221022062949.1: *4* LeoQtLog.renameTab
    def renameTab(self, oldTabName: str, tabName: str) -> None:
        """Rename the text tab"""
        w = self.tabWidget
        i = self.findTabIndex(oldTabName)
        if i is None:
            self.createTab(tabName)
        else:
            # Update the dict.
            self.logDict[tabName] = self.logDict[oldTabName]
            del self.logDict[oldTabName]
            # Update the tab's name.
            w.setTabText(i, tabName)
            self.tabName = tabName
    #@+node:ekr.20110605121601.18330: *4* LeoQtLog.numberOfVisibleTabs
    def numberOfVisibleTabs(self) -> int:
        # **Note**: the base-class version of this uses frameDict.
        return len([val for val in self.contentsDict.values() if val is not None])
    #@+node:ekr.20110605121601.18331: *4* LeoQtLog.selectTab & helpers
    def selectTab(self, tabName: str, wrap: str = 'none') -> None:
        """Create the tab if necessary and make it active."""
        i = self.findTabIndex(tabName)
        if i is None:
            self.createTab(tabName, wrap=wrap)
            self.finishCreateTab(tabName)
        self.finishSelectTab(tabName)
    #@+node:ekr.20190603064815.1: *5* LeoQtLog.finishCreateTab
    def finishCreateTab(self, tabName: str) -> None:
        """Finish creating the given tab. Do not set focus!"""
        c = self.c
        i = self.findTabIndex(tabName)
        if i is None:
            g.trace('Can not happen', tabName)
            self.tabName: str = None
            return
        # #1161.
        if tabName == 'Log':
            wrapper: QWidget = None
            widget: QWidget = self.contentsDict.get('Log')
            if widget:
                wrapper = getattr(widget, 'leo_log_wrapper', None)
                if wrapper and isinstance(wrapper, qt_text.QTextEditWrapper):
                    self.logCtrl = wrapper
            if not wrapper:
                g.trace('NO LOG WRAPPER')
        if tabName == 'Find':
            # Do *not* set focus here!
            # #1254861: Ctrl-f doesn't ensure find input field visible.
            if c.config.getBool('auto-scroll-find-tab', default=True):
                # This is the cause of unwanted scrolling.
                findbox = c.findCommands.ftm.find_findbox
                if hasattr(widget, 'ensureWidgetVisible'):
                    widget.ensureWidgetVisible(findbox)
                else:
                    findbox.setFocus()
        if tabName == 'Spell':
            # Set a flag for the spell system.
            widget = self.tabWidget.widget(i)
            self.frameDict['Spell'] = widget
    #@+node:ekr.20190603064816.1: *5* LeoQtLog.finishSelectTab
    def finishSelectTab(self, tabName: str) -> None:
        """Select the proper tab."""
        w = self.tabWidget
        # Special case for Spell tab.
        if tabName == 'Spell':
            return
        i = self.findTabIndex(tabName)
        if i is None:
            g.trace('can not happen', tabName)
            self.tabName = None
            return
        w.setCurrentIndex(i)
        self.tabName = tabName
    #@-others
#@+node:ekr.20110605121601.18340: ** class LeoQtMenu (LeoMenu)
class LeoQtMenu(leoMenu.LeoMenu):

    #@+others
    #@+node:ekr.20110605121601.18341: *3* LeoQtMenu.__init__
    def __init__(self, c: Cmdr, frame: LeoQtFrame, label: str) -> None:
        """ctor for LeoQtMenu class."""
        assert frame
        assert frame.c
        super().__init__(frame)
        self.leo_menu_label = label.replace('&', '').lower()
        self.frame = frame
        self.c = c
        self.menuBar: QMenuBar = c.frame.top.menuBar()
        assert self.menuBar is not None
        # Inject this dict into the commander.
        if not hasattr(c, 'menuAccels'):
            setattr(c, 'menuAccels', {})
        if 0:
            self.font = c.config.getFontFromParams(
                'menu_text_font_family', 'menu_text_font_size',
                'menu_text_font_slant', 'menu_text_font_weight',
                c.config.defaultMenuFontSize)
    #@+node:ekr.20120306130648.9848: *3* LeoQtMenu.__repr__
    def __repr__(self) -> str:
        return f"<LeoQtMenu: {self.leo_menu_label}>"

    __str__ = __repr__
    #@+node:ekr.20110605121601.18342: *3* LeoQtMenu.Tkinter menu bindings
    # See the Tk docs for what these routines are to do
    #@+node:ekr.20110605121601.18343: *4* LeoQtMenu.Methods with Tk spellings
    #@+node:ekr.20110605121601.18344: *5* LeoQtMenu.add_cascade
    def add_cascade(self,
        parent: LeoQtFrame, label: str, menu: QMenu, underline: int,
    ) -> None:
        """Wrapper for the Tkinter add_cascade menu method.

        Adds a submenu to the parent menu, or the menubar."""
        # menu and parent are a QtMenuWrappers, subclasses of  QMenu.
        n = underline
        if -1 < n < len(label):
            label = label[:n] + '&' + label[n:]
        menu.setTitle(label)
        if parent:
            parent.addMenu(menu)  # QMenu.addMenu.
        else:
            self.menuBar.addMenu(menu)
        label = label.replace('&', '').lower()
        menu.leo_menu_label = label

    #@+node:ekr.20110605121601.18345: *5* LeoQtMenu.add_command (Called by createMenuEntries)
    def add_command(self,
        menu: QMenu,
        accelerator: str = '',
        command: Callable = None,
        commandName: str = None,
        label: str = None,
        underline: int = 0,
    ) -> None:
        """Wrapper for the Tkinter add_command menu method."""
        if not label:
            return
        if -1 < underline < len(label):
            label = label[:underline] + '&' + label[underline:]
        if accelerator:
            label = f"{label}\t{accelerator}"
        action = menu.addAction(label)
        # Inject the command name into the action so that it can be enabled/disabled dynamically.
        action.leo_command_name = commandName or ''
        if command:

            def qt_add_command_callback(checked: int, label: str = label, command: Callable = command) -> None:
                return command()

            action.triggered.connect(qt_add_command_callback)
    #@+node:ekr.20110605121601.18346: *5* LeoQtMenu.add_separator
    def add_separator(self, menu: QMenu) -> None:
        """Wrapper for the Tkinter add_separator menu method."""
        if menu:
            action = menu.addSeparator()
            action.leo_menu_label = '*seperator*'
    #@+node:ekr.20110605121601.18347: *5* LeoQtMenu.delete
    def delete(self, menu: QtMenuWrapper, realItemName: str = '<no name>') -> None:
        """Wrapper for the Tkinter delete menu method."""
        # if menu:
            # return menu.delete(realItemName)
    #@+node:ekr.20110605121601.18348: *5* LeoQtMenu.delete_range
    def delete_range(self, menu: QtMenuWrapper, n1: int, n2: int) -> None:
        """Wrapper for the Tkinter delete menu method."""
        # Menu is a subclass of QMenu and LeoQtMenu.
        for z in menu.actions()[n1:n2]:
            menu.removeAction(z)
    #@+node:ekr.20110605121601.18349: *5* LeoQtMenu.destroy
    def destroy(self, menu: QMenu) -> None:
        """Wrapper for the Tkinter destroy menu method."""
        # Fixed bug https://bugs.launchpad.net/leo-editor/+bug/1193870
        if menu:
            menu.menuBar.removeAction(menu.menuAction())
    #@+node:ekr.20110605121601.18350: *5* LeoQtMenu.index
    def index(self, label: str) -> int:
        """Return the index of the menu with the given label."""
        return 0
    #@+node:ekr.20110605121601.18351: *5* LeoQtMenu.insert
    def insert(self,
        menuName: str, position: int, label: str, command: Callable, underline: int = None,
    ) -> None:

        menu = self.getMenu(menuName)
        if menu and label:
            n = underline or 0
            if -1 > n > len(label):
                label = label[:n] + '&' + label[n:]
            action = menu.addAction(label)
            if command:

                def insert_callback(checked: str, label: str = label, command: Callable = command) -> None:
                    command()

                action.triggered.connect(insert_callback)
    #@+node:ekr.20110605121601.18352: *5* LeoQtMenu.insert_cascade
    def insert_cascade(self,
        parent: LeoQtFrame,
        index: int,
        label: str,
        menu: QMenu,
        underline: int,  # Not used
    ) -> QMenu:
        """Wrapper for the Tkinter insert_cascade menu method."""
        menu.setTitle(label)
        label.replace('&', '').lower()
        menu.leo_menu_label = label
        if parent:
            parent.addMenu(menu)
        else:
            self.menuBar.addMenu(menu)
        action = menu.menuAction()
        if action:
            action.leo_menu_label = label
        else:
            g.trace('no action for menu', label)
        return menu
    #@+node:ekr.20110605121601.18353: *5* LeoQtMenu.new_menu
    def new_menu(self, parent: QWidget, tearoff: int = 0, label: str = '') -> QtMenuWrapper:  # label is for debugging.
        """Wrapper for the Tkinter new_menu menu method."""
        c, leoFrame = self.c, self.frame
        # Parent can be None, in which case it will be added to the menuBar.
        menu = QtMenuWrapper(c, leoFrame, parent, label)
        return menu
    #@+node:ekr.20110605121601.18354: *4* LeoQtMenu.Methods with other spellings
    #@+node:ekr.20110605121601.18355: *5* LeoQtMenu.clearAccel
    def clearAccel(self, menu: QMenu, name: str) -> None:
        pass
        # if not menu:
            # return
        # realName = self.getRealMenuName(name)
        # realName = realName.replace("&","")
        # menu.entryconfig(realName,accelerator='')
    #@+node:ekr.20110605121601.18356: *5* LeoQtMenu.createMenuBar
    def createMenuBar(self, frame: LeoQtFrame) -> None:
        """
        (LeoQtMenu) Create all top-level menus.
        The menuBar itself has already been created.
        """
        self.createMenusFromTables()  # This is LeoMenu.createMenusFromTables.
    #@+node:ekr.20110605121601.18357: *5* LeoQtMenu.createOpenWithMenu
    def createOpenWithMenu(self, parent: QWidget, label: str, index: int, amp_index: int) -> QtMenuWrapper:
        """
        Create the File:Open With submenu.

        This is called from LeoMenu.createOpenWithMenuFromTable.
        """
        # Use the existing Open With menu if possible.
        menu = self.getMenu('openwith')
        if not menu:
            menu = self.new_menu(parent, tearoff=False, label=label)
            menu.insert_cascade(parent, index, label, menu, underline=amp_index)
        return menu
    #@+node:ekr.20110605121601.18358: *5* LeoQtMenu.disable/enableMenu (not used)
    def disableMenu(self, menu: QMenu, name: str) -> None:
        self.enableMenu(menu, name, False)

    def enableMenu(self, menu: QMenu, name: str, val: bool) -> None:
        """Enable or disable the item in the menu with the given name."""
        if menu and name:
            for action in menu.actions():
                s = g.checkUnicode(action.text()).replace('&', '')
                if s.startswith(name):
                    action.setEnabled(val)
                    break
    #@+node:ekr.20110605121601.18359: *5* LeoQtMenu.getMenuLabel
    def getMenuLabel(self, menu: QMenu, name: str) -> None:
        """Return the index of the menu item whose name (or offset) is given.
        Return None if there is no such menu item."""
        # At present, it is valid to always return None.
    #@+node:ekr.20110605121601.18360: *5* LeoQtMenu.setMenuLabel
    def setMenuLabel(self, menu: QMenu, name: str, label: str, underline: int = -1) -> None:

        def munge(s: str) -> str:
            return (s or '').replace('&', '')

        # menu is a QtMenuWrapper.
        if not menu:
            return

        realName = munge(self.getRealMenuName(name))
        realLabel = self.getRealMenuName(label)
        for action in menu.actions():
            s = munge(action.text())
            s = s.split('\t')[0]
            if s == realName:
                action.setText(realLabel)
                break
    #@+node:ekr.20110605121601.18361: *3* LeoQtMenu.activateMenu & helper
    def activateMenu(self, menuName: str) -> None:
        """Activate the menu with the given name"""
        # Menu is a QtMenuWrapper, a subclass of both QMenu and LeoQtMenu.
        menu = self.getMenu(menuName)
        if menu:
            self.activateAllParentMenus(menu)
        else:
            g.trace(f"No such menu: {menuName}")
    #@+node:ekr.20120922041923.10607: *4* LeoQtMenu.activateAllParentMenus
    def activateAllParentMenus(self, menu: QObject) -> None:
        """menu is a QtMenuWrapper.  Activate it and all parent menus."""
        parent = menu.parent()
        action = menu.menuAction()
        if action:
            if parent and isinstance(parent, QtWidgets.QMenuBar):
                parent.setActiveAction(action)
            elif parent:
                self.activateAllParentMenus(parent)
                parent.setActiveAction(action)
            else:
                g.trace(f"can not happen: no parent for {menu}")
        else:
            g.trace(f"can not happen: no action for {menu}")
    #@+node:ekr.20120922041923.10613: *3* LeoQtMenu.deactivateMenuBar
    # def deactivateMenuBar (self):
        # """Activate the menu with the given name"""
        # menubar = self.c.frame.top.leo_menubar
        # menubar.setActiveAction(None)
        # menubar.repaint()
    #@-others
#@+node:ekr.20110605121601.18363: ** class LeoQTreeWidget (QTreeWidget)
class LeoQTreeWidget(QtWidgets.QTreeWidget):

    def __init__(self, c: Cmdr, parent: QWidget) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        enable_drag = c.config.getBool('enable-tree-dragging')
        self.setDragEnabled(bool(enable_drag))
        self.c = c
        self.was_alt_drag = False
        self.was_control_drag = False
        # #2463.
        header = self.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(header.ResizeMode.ResizeToContents)

    def __repr__(self) -> str:
        return f"LeoQTreeWidget: {id(self)}"

    __str__ = __repr__


    def dragMoveEvent(self, ev: QEvent) -> None:  # Called during drags.
        pass

    #@+others
    #@+node:ekr.20111022222228.16980: *3* LeoQTreeWidget: Event handlers
    #@+node:ekr.20110605121601.18364: *4* LeoQTreeWidget.dragEnterEvent & helper
    def dragEnterEvent(self, ev: QEvent) -> None:
        """Export c.p's tree as a Leo mime-data."""
        c = self.c
        if not ev:
            g.trace('no event!')
            return
        md = ev.mimeData()
        if not md:
            g.trace('No mimeData!')
            return
        c.endEditing()
        # Fix bug 135: cross-file drag and drop is broken.
        # This handler may be called several times for the same drag.
        # Only the first should should set g.app.drag_source.
        if g.app.dragging:
            pass
        else:
            g.app.dragging = True
            g.app.drag_source = c, c.p
            self.setText(md)
        # Always accept the drag, even if we are already dragging.
        ev.accept()
    #@+node:ekr.20110605121601.18384: *5* LeoQTreeWidget.setText
    def setText(self, md: QWidget) -> None:
        c = self.c
        fn = self.fileName()
        s = c.fileCommands.outline_to_clipboard_string()
        md.setText(f"{fn},{s}")
    #@+node:ekr.20110605121601.18365: *4* LeoQTreeWidget.dropEvent & helpers
    def dropEvent(self, ev: QEvent) -> None:
        """Handle a drop event in the QTreeWidget."""
        if not ev:
            return
        md = ev.mimeData()
        if not md:
            g.trace('no mimeData!')
            return
        try:
            mods = ev.modifiers()
            self.was_alt_drag = bool(mods & KeyboardModifier.AltModifier)
            self.was_control_drag = bool(mods & KeyboardModifier.ControlModifier)
        except Exception:  # Defensive.
            g.es_exception()
            g.app.dragging = False
            return
        c, tree = self.c, self.c.frame.tree
        p = None
        point = ev.position().toPoint()
        item = self.itemAt(point)
        if item:
            itemHash = tree.itemHash(item)
            p = tree.item2positionDict.get(itemHash)
        if not p:
            # #59: Drop at last node.
            p = c.rootPosition()
            while p.hasNext():
                p.moveToNext()
        formats = set(str(f) for f in md.formats())
        ev.setDropAction(DropAction.IgnoreAction)
        ev.accept()
        hookres = g.doHook("outlinedrop", c=c, p=p, dropevent=ev, formats=formats)
        if hookres:
            # A plugin handled the drop.
            pass
        else:
            if md.hasUrls():
                self.urlDrop(md, p)
            else:
                self.nodeDrop(md, p)
        g.app.dragging = False
    #@+node:ekr.20110605121601.18366: *5* LeoQTreeWidget.nodeDrop & helpers
    def nodeDrop(self, md: QWidget, p: Position) -> None:
        """
        Handle a drop event when not md.urls().
        This will happen when we drop an outline node.
        We get the copied text from md.text().
        """
        c = self.c
        fn, s = self.parseText(md)
        if not s or not fn:
            return
        if fn == self.fileName():
            if p and p == c.p:
                pass
            elif g.os_path_exists(fn):
                self.intraFileDrop(fn, c.p, p)
        else:
            self.interFileDrop(fn, p, s)
    #@+node:ekr.20110605121601.18367: *6* LeoQTreeWidget.interFileDrop
    def interFileDrop(self, fn: str, p: Position, s: str) -> None:
        """Paste the mime data after (or as the first child of) p."""
        c = self.c
        u = c.undoer
        undoType = 'Drag Outline'
        isLeo = g.match(s, 0, g.app.prolog_prefix_string)
        if not isLeo:
            return
        c.selectPosition(p)
        # Paste the node after the presently selected node.
        pasted = c.fileCommands.getLeoOutlineFromClipboard(s)
        if not pasted:
            return
        if c.config.getBool('inter-outline-drag-moves'):
            src_c, src_p = g.app.drag_source
            if src_p.hasVisNext(src_c):
                nxt = src_p.getVisNext(src_c).v
            elif src_p.hasVisBack(src_c):
                nxt = src_p.getVisBack(src_c).v
            else:
                nxt = None
            if nxt is not None:
                src_p.doDelete()
                src_c.selectPosition(src_c.vnode2position(nxt))
                src_c.setChanged()
                src_c.redraw()
            else:
                g.es("Can't move last node out of outline")
        undoData = u.beforeInsertNode(p, pasteAsClone=False, copiedBunchList=[])
        c.checkOutline()
        c.selectPosition(pasted)
        pasted.setDirty()  # 2011/02/27: Fix bug 690467.
        c.setChanged()
        back = pasted.back()
        if back and back.isExpanded():
            pasted.moveToNthChildOf(back, 0)
        # c.setRootPosition(c.findRootPosition(pasted))
        u.afterInsertNode(pasted, undoType, undoData)
        c.redraw(pasted)
        c.recolor()
    #@+node:ekr.20110605121601.18368: *6* LeoQTreeWidget.intraFileDrop
    def intraFileDrop(self, fn: str, p1: Position, p2: Position) -> None:
        """Move p1 after (or as the first child of) p2."""
        as_child = self.was_alt_drag
        cloneDrag = self.was_control_drag
        c = self.c
        u = c.undoer
        c.selectPosition(p1)
        if as_child or p2.hasChildren() and p2.isExpanded():
            # Attempt to move p1 to the first child of p2.
            # parent = p2

            def move(p1: Position, p2: Position) -> Position:
                if cloneDrag:
                    p1 = p1.clone()
                p1.moveToNthChildOf(p2, 0)
                p1.setDirty()
                return p1

        else:
            # Attempt to move p1 after p2.
            # parent = p2.parent()

            def move(p1: Position, p2: Position) -> Position:
                if cloneDrag:
                    p1 = p1.clone()
                p1.moveAfter(p2)
                p1.setDirty()
                return p1

        ok = (
            # 2011/10/03: Major bug fix.
            c.checkDrag(p1, p2) and
            c.checkMoveWithParentWithWarning(p1, p2, True))
        if ok:
            undoData = u.beforeMoveNode(p1)
            p1.setDirty()
            p1 = move(p1, p2)
            if cloneDrag:
                # Set dirty bits for ancestors of *all* cloned nodes.
                for z in p1.self_and_subtree():
                    z.setDirty()
            c.setChanged()
            u.afterMoveNode(p1, 'Drag', undoData)
            if (not as_child or
                p2.isExpanded() or
                c.config.getBool("drag-alt-drag-expands") is not False
            ):
                c.redraw(p1)
            else:
                c.redraw(p2)
    #@+node:ekr.20110605121601.18383: *6* LeoQTreeWidget.parseText
    def parseText(self, md: QWidget) -> tuple[str, str]:
        """Parse md.text() into (fn,s)"""
        fn = ''
        s = md.text()
        if s:
            i = s.find(',')
            if i == -1:
                pass
            else:
                fn = s[:i]
                s = s[i + 1 :]
        return fn, s
    #@+node:ekr.20110605121601.18369: *5* LeoQTreeWidget.urlDrop & helpers
    def urlDrop(self, md: QWidget, p: Position) -> None:
        """Handle a drop when md.urls()."""
        c, u, undoType = self.c, self.c.undoer, 'Drag Urls'
        urls = md.urls()
        if not urls:
            return
        u.beforeChangeGroup(c.p, undoType)
        changed = False
        for url in urls:
            scheme = url.scheme()
            path = url.path()
            if scheme == 'file':
                changed |= self.doFileUrl(p, path)
            elif scheme in ('http', 'https'):  # 'ftp','mailto',
                changed |= self.doHttpUrl(p, path)
        # Call this only once, at end.
        u.afterChangeGroup(c.p, undoType)
        if changed:
            c.setChanged()
            c.redraw()
        else:
            g.es("Command did not find any affected Urls")

    #@+node:ekr.20110605121601.18370: *6* LeoQTreeWidget.doFileUrl & helper
    def doFileUrl(self, p: Position, path: str) -> bool:
        """Read the file with the given path and put it in the outline."""
        e = sys.getfilesystemencoding()
        fn = g.toUnicode(path, encoding=e)
        if sys.platform.lower().startswith('win') and fn.startswith('/'):
            fn = fn[1:]
        if os.path.isdir(fn):
            # Just insert an @path directory.
            self.doPathUrlHelper(fn, p)
            return True
        if g.os_path_exists(fn):
            try:
                f = open(fn, 'rb')
            except IOError:
                f = None
            if f:
                b = f.read()
                s = g.toUnicode(b)
                f.close()
                return self.doFileUrlHelper(fn, p, s)
        nodeLink = p.get_UNL()
        g.es_print(f"not found: {fn}", nodeLink=nodeLink)
        return False
    #@+node:ekr.20110605121601.18371: *7* LeoQTreeWidget.doFileUrlHelper & helper
    def doFileUrlHelper(self, fn: str, p: Position, s: str) -> bool:
        """
        Insert s in an @file, @auto or @edit node after p.
        If fn is a .leo file, insert a node containing its top-level nodes as children.
        """
        c = self.c
        if self.isLeoFile(fn, s) and not self.was_control_drag:
            g.openWithFileName(fn, old_c=c)
            return False  # Don't set the changed marker in the original file.
        u, undoType = c.undoer, 'Drag File'
        undoData = u.beforeInsertNode(p, pasteAsClone=False, copiedBunchList=[])
        if p.hasChildren() and p.isExpanded():
            p2 = p.insertAsNthChild(0)
            parent = p
        elif p.h.startswith('@path '):
            # #60: create relative paths & urls when dragging files.
            p2 = p.insertAsNthChild(0)
            p.expand()
            parent = p
        else:
            p2 = p.insertAfter()
            parent = p.parent()
        # #60: create relative paths & urls when dragging files.
        path = c.getPath(parent)
        if path:
            fn = os.path.relpath(fn, path)
        self.createAtFileNode(fn, p2, s)
        u.afterInsertNode(p2, undoType, undoData)
        c.selectPosition(p2)
        return True  # The original .leo file has changed.
    #@+node:ekr.20110605121601.18372: *8* LeoQTreeWidget.createAtFileNode & helpers (QTreeWidget)
    def createAtFileNode(self, fn: str, p: Position, s: str) -> None:
        """
        Set p's headline, body text and possibly descendants
        based on the file's name fn and contents s.

        If the file is an thin file, create an @file tree.
        Otherwise, create an @auto tree.
        If all else fails, create an @edit node.

        Give a warning if a node with the same headline already exists.
        """
        c = self.c
        c.init_error_dialogs()
        if self.isLeoFile(fn, s):
            self.createLeoFileTree(fn, p)
        elif self.isThinFile(fn, s):
            self.createAtFileTree(fn, p, s)
        elif self.isAutoFile(fn):
            self.createAtAutoTree(fn, p)
        elif self.isBinaryFile(fn):
            self.createUrlForBinaryFile(fn, p)
        else:
            self.createAtEditNode(fn, p)
        self.warnIfNodeExists(p)
        c.raise_error_dialogs(kind='read')
    #@+node:ekr.20110605121601.18373: *9* LeoQTreeWidget.createAtAutoTree
    def createAtAutoTree(self, fn: str, p: Position) -> None:
        """
        Make p an @auto node and create the tree using s, the file's contents.
        """
        c = self.c
        at = c.atFileCommands
        fn2 = fn.replace('\\', '/')
        p.h = f"@auto {fn2}"
        at.readOneAtAutoNode(p)
        # No error recovery should be needed here.
        p.clearDirty()  # Don't automatically rewrite this node.
    #@+node:ekr.20110605121601.18374: *9* LeoQTreeWidget.createAtEditNode
    def createAtEditNode(self, fn: str, p: Position) -> None:
        c = self.c
        at = c.atFileCommands
        # Use the full @edit logic, so dragging will be
        # exactly the same as reading.
        at.readOneAtEditNode(p)
        fn2 = fn.replace('\\', '/')
        p.h = f"@edit {fn2}"
        p.clearDirty()  # Don't automatically rewrite this node.
    #@+node:ekr.20110605121601.18375: *9* LeoQTreeWidget.createAtFileTree
    def createAtFileTree(self, fn: str, p: Position, s: str) -> None:
        """Make p an @file node and create the tree using s, the file's contents."""
        c = self.c
        at = c.atFileCommands
        fn2 = fn.replace('\\', '/')
        p.h = f"@file {fn2}"
        # Read the file into p.
        ok = at.read(root=p.copy(), fromString=s)
        if not ok:
            g.error('Error reading', fn)
            p.b = ''  # Safe: will not cause a write later.
            p.clearDirty()  # Don't automatically rewrite this node.
    #@+node:ekr.20141007223054.18004: *9* LeoQTreeWidget.createLeoFileTree
    def createLeoFileTree(self, fn: str, p: Position) -> None:
        """Copy all nodes from fn, a .leo file, to the children of p."""
        c = self.c
        fn2 = fn.replace('\\', '/')
        p.h = f"From {g.shortFileName(fn2)}"
        c.selectPosition(p)
        # Create a dummy first child of p.
        dummy_p = p.insertAsNthChild(0)
        c.selectPosition(dummy_p)
        c2 = g.openWithFileName(fn, old_c=c, gui=g.app.nullGui)
        for p2 in c2.rootPosition().self_and_siblings():
            c2.selectPosition(p2)
            s = c2.fileCommands.outline_to_clipboard_string()
            # Paste the outline after the selected node.
            c.fileCommands.getLeoOutlineFromClipboard(s)
        dummy_p.doDelete()
        c.selectPosition(p)
        p.v.contract()
        c2.close()
        g.app.forgetOpenFile(c2.fileName())  # Necessary.
    #@+node:ekr.20120309075544.9882: *9* LeoQTreeWidget.createUrlForBinaryFile
    def createUrlForBinaryFile(self, fn: str, p: Position) -> None:
        # Fix bug 1028986: create relative urls when dragging binary files to Leo.
        c = self.c
        base_fn = g.os_path_normcase(g.os_path_abspath(c.mFileName))
        abs_fn = g.os_path_normcase(g.os_path_abspath(fn))
        prefix = os.path.commonprefix([abs_fn, base_fn])
        if prefix and len(prefix) > 3:  # Don't just strip off c:\.
            p.h = abs_fn[len(prefix) :].strip()
        else:
            fn2 = fn.replace('\\', '/')
            p.h = f"@url file://{fn2}"
    #@+node:ekr.20110605121601.18377: *9* LeoQTreeWidget.isAutoFile (LeoQTreeWidget)
    def isAutoFile(self, fn: str) -> bool:
        """Return true if fn (a file name) can be parsed with an @auto parser."""
        d = g.app.classDispatchDict
        junk, ext = g.os_path_splitext(fn)
        return bool(d.get(ext))
    #@+node:ekr.20120309075544.9881: *9* LeoQTreeWidget.isBinaryFile
    def isBinaryFile(self, fn: str) -> bool:
        # The default for unknown files is True. Not great, but safe.
        junk, ext = g.os_path_splitext(fn)
        ext = ext.lower()
        if not ext:
            val = False
        elif ext.startswith('~'):
            val = False
        elif ext in ('.css', '.htm', '.html', '.leo', '.txt'):
            val = False
        # elif ext in ('.bmp','gif','ico',):
            # val = True
        else:
            keys = (z.lower() for z in g.app.extension_dict)
            val = ext not in keys
        return val
    #@+node:ekr.20141007223054.18003: *9* LeoQTreeWidget.isLeoFile
    def isLeoFile(self, fn: str, s: str) -> bool:
        """Return true if fn (a file name) represents an entire .leo file."""
        return fn.endswith('.leo') and s.startswith(g.app.prolog_prefix_string)
    #@+node:ekr.20110605121601.18376: *9* LeoQTreeWidget.isThinFile
    def isThinFile(self, fn: str, s: str) -> bool:
        """
        Return true if the file whose contents is s
        was created from an @thin or @file tree.
        """
        c = self.c
        at = c.atFileCommands
        # Skip lines before the @+leo line.
        i = s.find('@+leo')
        if i == -1:
            return False
        # Like at.isFileLike.
        j, k = g.getLine(s, i)
        line = s[j:k]
        valid, new_df, start, end, isThin = at.parseLeoSentinel(line)
        return valid and new_df and isThin
    #@+node:ekr.20110605121601.18378: *9* LeoQTreeWidget.warnIfNodeExists
    def warnIfNodeExists(self, p: Position) -> None:
        c = self.c
        h = p.h
        for p2 in c.all_unique_positions():
            if p2.h == h and p2 != p:
                g.warning('Warning: duplicate node:', h)
                break
    #@+node:ekr.20110605121601.18379: *7* LeoQTreeWidget.doPathUrlHelper
    def doPathUrlHelper(self, fn: str, p: Position) -> None:
        """Insert fn as an @path node after p."""
        c = self.c
        u, undoType = c.undoer, 'Drag Directory'
        undoData = u.beforeInsertNode(p, pasteAsClone=False, copiedBunchList=[])
        if p.hasChildren() and p.isExpanded():
            p2 = p.insertAsNthChild(0)
        else:
            p2 = p.insertAfter()
        p2.h = '@path ' + fn
        u.afterInsertNode(p2, undoType, undoData)
        c.selectPosition(p2)
    #@+node:ekr.20110605121601.18380: *6* LeoQTreeWidget.doHttpUrl
    def doHttpUrl(self, p: Position, path: str) -> bool:
        """Insert the path in an @url node after p."""
        c = self.c
        u = c.undoer
        undoType = 'Drag Url'
        s = path.strip()
        if not s:
            return False
        undoData = u.beforeInsertNode(p, pasteAsClone=False, copiedBunchList=[])
        if p.hasChildren() and p.isExpanded():
            p2 = p.insertAsNthChild(0)
        else:
            p2 = p.insertAfter()
        p2.h = '@url'
        p2.b = s
        p2.clearDirty()  # Don't automatically rewrite this node.
        u.afterInsertNode(p2, undoType, undoData)
        return True
    #@+node:ekr.20110605121601.18381: *3* LeoQTreeWidget: utils
    #@+node:ekr.20110605121601.18382: *4* LeoQTreeWidget.dump
    def dump(self, ev: LeoKeyEvent, p: Position, tag: str) -> None:
        if ev:
            md = ev.mimeData()
            s = g.checkUnicode(md.text(), encoding='utf-8')
            g.trace('md.text:', repr(s) if len(s) < 100 else len(s))
            for url in md.urls() or []:
                g.trace('     url:', url)
                g.trace('  url.fn:', url.toLocalFile())
                g.trace('url.text:', url.toString())
        else:
            g.trace('', tag, '** no event!')
    #@+node:ekr.20141007223054.18002: *4* LeoQTreeWidget.fileName
    def fileName(self) -> str:
        """Return the commander's filename."""
        return self.c.fileName() or '<unsaved file>'
    #@-others
#@+node:ekr.20110605121601.18385: ** class LeoQtSpellTab
class LeoQtSpellTab:
    #@+others
    #@+node:ekr.20110605121601.18386: *3* LeoQtSpellTab.__init__
    def __init__(self, c: Cmdr, handler: Callable, tabName: str) -> None:
        """Ctor for LeoQtSpellTab class."""
        self.c = c
        top = c.frame.top
        self.handler = handler
        # hack:
        handler.workCtrl = StringTextWrapper(c, 'spell-workctrl')
        self.tabName = tabName
        if hasattr(top, 'leo_spell_label'):
            self.wordLabel = top.leo_spell_label
            self.listBox = top.leo_spell_listBox
            self.fillbox([])
        else:
            self.handler.loaded = False
    #@+node:ekr.20110605121601.18389: *3* Event handlers
    #@+node:ekr.20110605121601.18390: *4* onAddButton
    def onAddButton(self) -> None:
        """Handle a click in the Add button in the Check Spelling dialog."""
        self.handler.add()
    #@+node:ekr.20110605121601.18391: *4* onChangeButton & onChangeThenFindButton
    def onChangeButton(self, event: QEvent = None) -> None:
        """Handle a click in the Change button in the Spell tab."""
        state = self.updateButtons()
        if state:
            self.handler.change()
        self.updateButtons()

    def onChangeThenFindButton(self, event: QEvent = None) -> None:
        """Handle a click in the "Change, Find" button in the Spell tab."""
        state = self.updateButtons()
        if state:
            self.handler.change()
            if self.handler.change():
                self.handler.find()
            self.updateButtons()
    #@+node:ekr.20110605121601.18392: *4* onFindButton
    def onFindButton(self) -> None:
        """Handle a click in the Find button in the Spell tab."""
        c = self.c
        self.handler.find()
        self.updateButtons()
        c.invalidateFocus()
        c.bodyWantsFocus()
    #@+node:ekr.20110605121601.18393: *4* onHideButton
    def onHideButton(self) -> None:
        """Handle a click in the Hide button in the Spell tab."""
        self.handler.hide()
    #@+node:ekr.20110605121601.18394: *4* onIgnoreButton
    def onIgnoreButton(self, event: QEvent = None) -> None:
        """Handle a click in the Ignore button in the Check Spelling dialog."""
        self.handler.ignore()
    #@+node:ekr.20110605121601.18395: *4* onMap
    def onMap(self, event: QEvent = None) -> None:
        """Respond to a Tk <Map> event."""
        self.update(show=False, fill=False)
    #@+node:ekr.20110605121601.18396: *4* onSelectListBox
    def onSelectListBox(self, event: QEvent = None) -> None:
        """Respond to a click in the selection listBox."""
        c = self.c
        self.updateButtons()
        c.bodyWantsFocus()
    #@+node:ekr.20110605121601.18397: *3* Helpers
    #@+node:ekr.20110605121601.18398: *4* bringToFront (LeoQtSpellTab)
    def bringToFront(self) -> None:
        self.c.frame.log.selectTab('Spell')
    #@+node:ekr.20110605121601.18399: *4* fillbox (LeoQtSpellTab)
    def fillbox(self, alts: list[str], word: str = None) -> None:
        """Update the suggestions listBox in the Check Spelling dialog."""
        self.suggestions = alts
        if not word:
            word = ""
        self.wordLabel.setText("Suggestions for: " + word)
        self.listBox.clear()
        if self.suggestions:
            self.listBox.addItems(self.suggestions)
            self.listBox.setCurrentRow(0)
    #@+node:ekr.20110605121601.18400: *4* getSuggestion (LeoQtSpellTab)
    def getSuggestion(self) -> str:
        """Return the selected suggestion from the listBox."""
        idx = self.listBox.currentRow()
        value = self.suggestions[idx]
        return value
    #@+node:ekr.20141113094129.13: *4* setFocus (LeoQtSpellTab)
    def setFocus(self) -> None:
        """Actually put focus in the tab."""
        # Not a great idea: there is no indication of focus.
        c = self.c
        if c.frame and c.frame.top and hasattr(c.frame.top, 'spellFrame'):
            w = self.c.frame.top.spellFrame
            c.widgetWantsFocus(w)
    #@+node:ekr.20110605121601.18401: *4* update (LeoQtSpellTab)
    def update(self, show: bool = True, fill: bool = False) -> None:
        """Update the Spell Check dialog."""
        c = self.c
        if fill:
            self.fillbox([])
        self.updateButtons()
        if show:
            self.bringToFront()
            c.bodyWantsFocus()
    #@+node:ekr.20110605121601.18402: *4* updateButtons (spellTab)
    def updateButtons(self) -> bool:
        """Enable or disable buttons in the Check Spelling dialog."""
        c = self.c
        top, w = c.frame.top, c.frame.body.wrapper
        state = bool(self.suggestions and w.hasSelection())
        top.leo_spell_btn_Change.setDisabled(not state)
        top.leo_spell_btn_FindChange.setDisabled(not state)
        return state
    #@-others
#@+node:ekr.20110605121601.18438: ** class LeoQtTreeTab
class LeoQtTreeTab:
    """
    A class representing a so-called tree-tab.

    Actually, it represents a combo box
    """
    #@+others
    #@+node:ekr.20110605121601.18439: *3*  Birth & death
    #@+node:ekr.20110605121601.18440: *4*  ctor (LeoQtTreeTab)
    def __init__(self, c: Cmdr, iconBar: LeoQtLog) -> None:
        """Ctor for LeoQtTreeTab class."""

        self.c = c
        self.cc = c.chapterController
        assert self.cc
        self.iconBar = iconBar
        self.lockout = False  # True: do not redraw.
        self.tabNames: list[str] = []  # The list of tab names. Changes when tabs are renamed.
        self.w: QComboBox = None
        # self.reloadSettings()
        self.createControl()
    #@+node:ekr.20110605121601.18441: *4* tt.createControl (defines class LeoQComboBox)
    def createControl(self) -> None:


        class LeoQComboBox(QtWidgets.QComboBox):
            """Create a subclass in order to handle focusInEvents."""

            def __init__(self, tt: LeoQtTreeTab) -> None:
                self.leo_tt = tt
                super().__init__()
                # Fix #458: Chapters drop-down list is not automatically resized.
                self.setSizeAdjustPolicy(SizeAdjustPolicy.AdjustToContents)

            def focusInEvent(self, event: QFocusEvent) -> None:
                self.leo_tt.setNames()
                QtWidgets.QComboBox.focusInEvent(self, event)  # Call the base class

        tt = self
        frame = QtWidgets.QLabel('Chapters: ')
        ibw = tt.iconBar.w  # "ibw": iconbar widget (a QToolbar)
        tt.w = LeoQComboBox(tt)
        w = tt.w
        tt.setNames()

        # Should the "Chapters" group be installed at the left of the toolbar?
        insert_left = self.c.config.getBool('chapter-dropdown-left', False)
        left = None
        if insert_left:
            actions = ibw.actions()
            if actions:
                left = actions[0]
        if left:
            ibw.insertWidget(left, frame)
            ibw.insertWidget(left, w)
        else:
            ibw.addWidget(frame)
            ibw.addWidget(w)

        def onIndexChanged(s: str, tt: LeoQtTreeTab = tt) -> None:
            if isinstance(s, int):
                s = '' if s == -1 else tt.w.currentText()
            else:  # s is the tab name.
                pass
            if s and not tt.cc.selectChapterLockout:
                tt.selectTab(s)

        # A change: the argument could now be an int instead of a string.
        w.currentIndexChanged.connect(onIndexChanged)
    #@+node:ekr.20110605121601.18443: *3* tt.createTab
    def createTab(self, tabName: str, select: bool = True) -> None:
        """LeoQtTreeTab."""
        tt = self
        # Avoid a glitch during initing.
        if tabName != 'main' and tabName not in tt.tabNames:
            tt.tabNames.append(tabName)
            tt.setNames()
    #@+node:ekr.20110605121601.18444: *3* tt.destroyTab
    def destroyTab(self, tabName: str) -> None:
        """LeoQtTreeTab."""
        tt = self
        if tabName in tt.tabNames:
            tt.tabNames.remove(tabName)
            tt.setNames()
    #@+node:ekr.20110605121601.18445: *3* tt.selectTab
    def selectTab(self, tabName: str) -> None:
        """LeoQtTreeTab."""
        tt, c, cc = self, self.c, self.cc
        exists = tabName in self.tabNames
        c.treeWantsFocusNow()  # Fix #969. Somehow this is important.
        if not exists:
            tt.createTab(tabName)  # Calls tt.setNames()
        if tt.lockout:
            return
        cc.selectChapterByName(tabName)
        c.redraw()
        c.outerUpdate()
    #@+node:ekr.20110605121601.18446: *3* tt.setTabLabel
    def setTabLabel(self, tabName: str) -> None:
        """LeoQtTreeTab."""
        w = self.w
        i = w.findText(tabName)
        if i > -1:
            w.setCurrentIndex(i)
    #@+node:ekr.20110605121601.18447: *3* tt.setNames
    def setNames(self) -> None:
        """LeoQtTreeTab: Recreate the list of items."""
        w = self.w
        names = self.cc.setAllChapterNames()
        w.clear()
        w.insertItems(0, names)
    #@-others
#@+node:ekr.20110605121601.18448: ** class LeoTabbedTopLevel (LeoBaseTabWidget)
class LeoTabbedTopLevel(LeoBaseTabWidget):
    """ Toplevel frame for tabbed ui """

    def __init__(self, *args: Args, **kwargs: KWargs) -> None:
        super().__init__(*args, **kwargs)
        ## middle click close on tabs -- JMP 20140505
        self.setMovable(False)
        tb = QtTabBarWrapper(self)
        self.setTabBar(tb)
#@+node:ekr.20110605121601.18262: ** class QtIconBarClass
class QtIconBarClass:
    """A class representing the singleton Icon bar"""
    #@+others
    #@+node:ekr.20110605121601.18263: *3*  QtIconBar.ctor & reloadSettings
    def __init__(self, c: Cmdr, parentFrame: LeoQtFrame) -> None:
        """Ctor for QtIconBarClass."""
        # Copy ivars
        self.c = c
        self.parentFrame = parentFrame
        # Status ivars.
        self.actions: list[QAction] = []
        self.chapterController = None
        self.toolbar = self
        self.w = c.frame.top.iconBar  # A QToolBar.
        self.reloadSettings()

    def reloadSettings(self) -> None:
        c = self.c
        c.registerReloadSettings(self)
        self.buttonColor = c.config.getString('qt-button-color')
        self.toolbar_orientation = c.config.getString('qt-toolbar-location')
    #@+node:ekr.20110605121601.18264: *3*  QtIconBar.do-nothings
    # These *are* called from Leo's core.

    def addRow(self, height: int = None) -> None:
        pass

    def getNewFrame(self) -> None:
        return None

    def hide(self) -> None:
        pass

    def show(self) -> None:
        pass
    #@+node:ekr.20110605121601.18265: *3* QtIconBar.add
    def add(self, *args: Args, **keys: KWargs) -> QAction:
        """Add a button to the icon bar."""
        c = self.c
        if not self.w:
            return None
        command: Callable = keys.get('command')
        text: str = keys.get('text')
        # able to specify low-level QAction directly (QPushButton not forced)
        qaction: QAction = keys.get('qaction')
        if not text and not qaction:
            g.es('bad toolbar item')
        kind: str = keys.get('kind') or 'generic-button'
        # imagefile = keys.get('imagefile')
        # image = keys.get('image')


        class leoIconBarButton(QtWidgets.QWidgetAction):

            def __init__(self, parent: QWidget, text: str, toolbar: QtIconBarClass) -> None:
                super().__init__(parent)
                self.button: QtWidgets.QPushButton = None
                self.text_val = text  # self.text is a method!
                self.toolbar = toolbar

            def createWidget(self, parent: QWidget) -> QtWidgets.QPushButton:
                self.button = QtWidgets.QPushButton(self.text_val, parent)
                self.button.setProperty('button_kind', kind)  # for styling
                return self.button

        action: Any
        if qaction is None:
            action = leoIconBarButton(parent=self.w, text=text, toolbar=self)
            button_name = text
        else:
            action = qaction
            button_name = action.text()
        self.w.addAction(action)
        self.actions.append(action)
        b = self.w.widgetForAction(action)
        # Set the button's object name so we can use the stylesheet to color it.
        if not button_name:
            button_name = 'unnamed'
        button_name = button_name + '-button'
        b.setObjectName(button_name)
        b.setContextMenuPolicy(ContextMenuPolicy.ActionsContextMenu)

        def delete_callback(checked: str, action: str = action) -> None:
            self.w.removeAction(action)

        b.leo_removeAction = rb = QAction('Remove Button', b)
        b.addAction(rb)
        rb.triggered.connect(delete_callback)
        if command:

            def button_callback(event: QEvent, c: Cmdr = c, command: Callable = command) -> None:
                val = command()
                if c.exists:
                    # c.bodyWantsFocus()
                    c.outerUpdate()
                return val

            b.clicked.connect(button_callback)

        return action
    #@+node:ekr.20110605121601.18266: *3* QtIconBar.addRowIfNeeded (not used)
    def addRowIfNeeded(self) -> None:
        """Add a new icon row if there are too many widgets."""
        # n = g.app.iconWidgetCount
        # if n >= self.widgets_per_row:
            # g.app.iconWidgetCount = 0
            # self.addRow()
        # g.app.iconWidgetCount += 1
    #@+node:ekr.20110605121601.18267: *3* QtIconBar.addWidget
    def addWidget(self, w: LeoQtFrame) -> None:
        self.w.addWidget(w)
    #@+node:ekr.20110605121601.18268: *3* QtIconBar.clear
    def clear(self) -> None:
        """Destroy all the widgets in the icon bar"""
        self.w.clear()
        self.actions = []
        g.app.iconWidgetCount = 0
    #@+node:ekr.20110605121601.18269: *3* QtIconBar.createChaptersIcon
    def createChaptersIcon(self) -> "LeoQtTreeTab":

        c = self.c
        f = c.frame
        if f.use_chapters and f.use_chapter_tabs:
            return LeoQtTreeTab(c, f.iconBar)
        return None
    #@+node:ekr.20110605121601.18270: *3* QtIconBar.deleteButton
    def deleteButton(self, w: LeoQtFrame) -> None:
        """ w is button """
        self.w.removeAction(w)
        self.c.bodyWantsFocus()
        self.c.outerUpdate()
    #@+node:ekr.20141031053508.14: *3* QtIconBar.goto_command
    def goto_command(self, controller: ScriptingController, gnx: str) -> None:
        """
        Select the node corresponding to the given gnx.
        controller is a ScriptingController instance.
        """
        # Fix bug 74: command_p may be in another outline.
        c = self.c
        c2, p = controller.open_gnx(c, gnx)
        if p:
            assert c2.positionExists(p)
            if c == c2:
                c2.selectPosition(p)
            else:
                g.app.selectLeoWindow(c2)
                # Fix #367: Process events before selecting.
                g.app.gui.qtApp.processEvents()
                c2.selectPosition(p)
        else:
            g.trace('not found', gnx)
    #@+node:ekr.20110605121601.18271: *3* QtIconBar.setCommandForButton (@rclick nodes) & helper
    # qtFrame.QtIconBarClass.setCommandForButton

    def setCommandForButton(self,
        button: QPushButton,
        command: Callable,
        command_p: Position,
        controller: ScriptingController,
        gnx: str,
        script: str,
    ) -> None:
        """
        Set the "Goto Script" rlick item of an @button button.
        Called from mod_scripting.py plugin.

        button is a leoIconBarButton.
        command is a callback, defined in mod_scripting.py.
        command_p exists only if the @button node exists in the local .leo file.
        gnx is the gnx of the @button node.
        script is a static script for common @button nodes.
        """
        if not command:
            return
        b = button.button
        b.clicked.connect(command)

        def goto_callback(
            checked: str,
            controller: ScriptingController = controller,
            gnx: str = gnx,
        ) -> None:
            self.goto_command(controller, gnx)

        b.goto_script = gts = QAction('Goto Script', b)
        b.addAction(gts)
        gts.triggered.connect(goto_callback)
        rclicks = build_rclick_tree(command_p, top_level=True)
        self.add_rclick_menu(b, rclicks, controller, script=script)
    #@+node:ekr.20141031053508.15: *4* add_rclick_menu (QtIconBarClass)
    def add_rclick_menu(
        self,
        action_container: QWidget,
        rclicks: RClicks,
        controller: ScriptingController,
        top_level: bool = True,
        button: QWidget = None,
        script: str = None,
    ) -> None:
        c = controller.c
        top_offset = -2  # insert before the remove button and goto script items
        if top_level:
            button = action_container
        for rc in rclicks:
            headline = rc.position.h[8:].strip()
            act = QAction(headline, action_container)
            if '---' in headline and headline.strip().strip('-') == '':
                act.setSeparator(True)
            elif rc.position.b.strip():

                def cb(checked: str, p: Position = rc.position, button: QWidget = button) -> None:
                    controller.executeScriptFromButton(
                        b=button,
                        buttonText=p.h[8:].strip(),
                        p=p,
                        script=script,
                    )
                    if c.exists:
                        c.outerUpdate()

                act.triggered.connect(cb)
            else:  # recurse submenu
                sub_menu = QtWidgets.QMenu(action_container)
                act.setMenu(sub_menu)
                self.add_rclick_menu(sub_menu, rc.children, controller,
                    top_level=False, button=button)
            if top_level:
                # insert act before Remove Button
                action_container.insertAction(
                    action_container.actions()[top_offset], act)
            else:
                action_container.addAction(act)
        if top_level and rclicks:
            act = QAction('---', action_container)
            act.setSeparator(True)
            action_container.insertAction(
                action_container.actions()[top_offset], act)
            action_container.setText(
                action_container.text() +
                (c.config.getString('mod-scripting-subtext') or '')
            )
    #@-others
#@+node:ekr.20110605121601.18458: ** class QtMenuWrapper (LeoQtMenu,QMenu)
# mypy complains about the font ivar and incompatible destroy methods(!)

class QtMenuWrapper(LeoQtMenu, QtWidgets.QMenu):  # type:ignore
    #@+others
    #@+node:ekr.20110605121601.18459: *3* ctor and __repr__(QtMenuWrapper)
    def __init__(self, c: Cmdr, frame: LeoQtFrame, parent: QWidget, label: str) -> None:
        """ctor for QtMenuWrapper class."""
        assert c
        assert frame
        if parent is None:
            parent = c.frame.top.menuBar()
        #
        # For reasons unknown, the calls must be in this order.
        # Presumably, the order of base classes also matters(!)
        LeoQtMenu.__init__(self, c, frame, label)
        QtWidgets.QMenu.__init__(self, parent)
        label = label.replace('&', '').lower()
        self.leo_menu_label = label
        action = self.menuAction()
        if action:
            action.leo_menu_label = label
        self.aboutToShow.connect(self.onAboutToShow)

    def __repr__(self) -> str:
        return f"<QtMenuWrapper {self.leo_menu_label}>"
    #@+node:ekr.20110605121601.18460: *3* onAboutToShow & helpers (QtMenuWrapper)
    def onAboutToShow(self, *args: Args, **keys: KWargs) -> None:

        name = self.leo_menu_label
        if not name:
            return
        for action in self.actions():
            commandName = hasattr(action, 'leo_command_name') and action.leo_command_name
            if commandName:
                self.leo_update_shortcut(action, commandName)
                self.leo_enable_menu_item(action, commandName)
                self.leo_update_menu_label(action, commandName)
    #@+node:ekr.20120120095156.10261: *4* leo_enable_menu_item
    def leo_enable_menu_item(self, action: QAction, commandName: str) -> None:
        func = self.c.frame.menu.enable_dict.get(commandName)
        if action and func:
            val = func()
            action.setEnabled(bool(val))
    #@+node:ekr.20120124115444.10190: *4* leo_update_menu_label
    def leo_update_menu_label(self, action: QAction, commandName: str) -> None:
        c = self.c
        if action and commandName == 'mark':
            action.setText('UnMark' if c.p.isMarked() else 'Mark')
            # Set the proper shortcut.
            self.leo_update_shortcut(action, commandName)
    #@+node:ekr.20120120095156.10260: *4* leo_update_shortcut
    def leo_update_shortcut(self, action: QAction, commandName: str) -> None:

        c, k = self.c, self.c.k
        if action:
            s = action.text()
            parts = s.split('\t')
            if len(parts) >= 2:
                s = parts[0]
            key, aList = c.config.getShortcut(commandName)
            if aList:
                result = []
                for bi in aList:
                    # Don't show mode-related bindings.
                    if not bi.isModeBinding():
                        accel = k.prettyPrintKey(bi.stroke)
                        result.append(accel)
                        # Break here if we want to show only one accelerator.
                action.setText(f"{s}\t{', '.join(result)}")
            else:
                action.setText(s)
        else:
            g.trace(f"can not happen: no action for {commandName}")
    #@-others
#@+node:ekr.20110605121601.18461: ** class QtSearchWidget
class QtSearchWidget:
    """A dummy widget class to pass to Leo's core find code."""

    def __init__(self) -> None:
        self.insertPoint = 0
        self.selection = 0, 0
        self.wrapper = self
        self.body = self
        self.text = None
#@+node:ekr.20110605121601.18257: ** class QtStatusLineClass
class QtStatusLineClass:
    """A class representing the status line."""
    #@+others
    #@+node:ekr.20110605121601.18258: *3* QtStatusLineClass.ctor
    def __init__(self, c: Cmdr, parentFrame: LeoQtFrame) -> None:
        """Ctor for LeoQtFrame class."""
        self.c = c
        self.statusBar = c.frame.top.leo_statusBar
        self.lastFcol = 0
        self.lastRow = 0
        self.lastCol = 0

        # #3901:  A new ivar that toggles between representations of UNLs.
        #         False: Use default, based on settings.
        #         True: Use the alternate representation.
        self.toggle_unl_view = False

        # Create the text widgets.
        self.textWidget1 = w1 = QtWidgets.QLineEdit(self.statusBar)
        self.textWidget2 = w2 = QtWidgets.QLineEdit(self.statusBar)
        w1.setObjectName('status1')
        w2.setObjectName('status2')
        w1.setReadOnly(True)
        w2.setReadOnly(True)
        splitter = QtWidgets.QSplitter()
        self.statusBar.addWidget(splitter, True)
        sizes = c.config.getString('status-line-split-sizes') or '1 2'
        int_sizes = [int(i) for i in sizes.replace(',', ' ').split()]
        for n, i in enumerate(int_sizes):
            w = [w1, w2][n]
            policy = w.sizePolicy()
            policy.setHorizontalStretch(i)
            policy.setHorizontalPolicy(Policy.Minimum)
            w.setSizePolicy(policy)
        splitter.addWidget(w1)
        splitter.addWidget(w2)
        self.put('')
        self.update()
    #@+node:ekr.20110605121601.18260: *3* QtStatusLineClass.clear, get & put/1 & helper
    def clear(self) -> None:
        self.put('')

    def get(self) -> str:
        return self.textWidget2.text()

    def put(self, s: str, bg: str = None, fg: str = None) -> None:
        """Put the UNL area."""
        self.put_helper(s, self.textWidget2, bg, fg)

    def put1(self, s: str, bg: str = None, fg: str = None) -> None:
        """Put the status area"""
        self.put_helper(s, self.textWidget1, bg, fg)
    #@+node:ekr.20240505051258.1: *4* QtStatusLineClass.put_helper
    # Keys are widgets, values are stylesheets.
    styleSheetCache: dict[QWidget, str] = {}

    def put_helper(self, s: str, w: QWidget, bg: str = None, fg: str = None) -> None:
        """Put string s in the indicated widget, with proper colors."""
        c = self.c
        bg = bg or c.config.getColor('status-bg') or 'white'
        fg = fg or c.config.getColor('status-fg') or 'black'
        if True:
            # Work around #804. w is a QLineEdit.
            w.setStyleSheet(f"background: {bg}; color: {fg};")
        else:
            # Rather than put(msg, explicit_color, explicit_color) we should use
            # put(msg, status) where status is None, 'info', or 'fail'.
            # Just as a quick hack to avoid dealing with propagating those changes
            # back upstream, infer status like this:
            if (
                fg == c.config.getColor('find-found-fg') and
                bg == c.config.getColor('find-found-bg')
            ):
                status = 'info'
            elif (
                fg == c.config.getColor('find-not-found-fg') and
                bg == c.config.getColor('find-not-found-bg')
            ):
                status = 'fail'
            else:
                status = None
            d = self.styleSheetCache
            if status != d.get(w, '__undefined__'):
                d[w] = status
                c.styleSheetManager.mng.remove_sclass(w, ['info', 'fail'])
                c.styleSheetManager.mng.add_sclass(w, status)
                c.styleSheetManager.mng.update_view(w)  # force appearance update
        w.setText(s)
    #@+node:ekr.20240505052656.1: *3* QtStatusLineClass.computeStatusUnl
    def computeStatusUnl(self, p: Position) -> str:
        """Compute the UNL part of the status line."""
        c = self.c
        kind = c.config.getString('unl-status-kind') or ''
        legacy = kind.lower() == 'legacy'
        if self.toggle_unl_view:
            # Show the UNL the opposite as indicated by settings.
            method = p.get_UNL if legacy else p.get_legacy_UNL
        else:
            # Show the UNL per the settings.
            method = p.get_legacy_UNL if legacy else p.get_UNL
        s = method()
        return s
    #@+node:ekr.20240505050902.1: *3* QtStatsuLineClass.toggleUnlView
    def toggleUnlView(self):
        """Toggle view of UNLs."""
        c = self.c
        # Toggle the switch.
        self.toggle_unl_view = not self.toggle_unl_view
        # Redraw.
        s = self.computeStatusUnl(c.p)
        self.put(s)
        self.update()
    #@+node:chris.20180320072817.1: *3* QtStatusLineClass.update & helpers
    def update(self) -> None:
        if g.app.killed:
            return
        c, body = self.c, self.c.frame.body
        if not c.p:
            return
        te = body.widget
        if not isinstance(te, QtWidgets.QTextEdit):
            return
        cursor = te.textCursor()
        block = cursor.block()
        row = block.blockNumber() + 1
        col, fcol = self.compute_columns(block, cursor)
        words = len(c.p.b.split(None))
        self.put_status_line(col, fcol, row, words)
        self.lastRow = row
        self.lastCol = col
        self.lastFcol = fcol
    #@+node:ekr.20190118082646.1: *4* qstatus.compute_columns
    def compute_columns(self, block: QTextBlock, cursor: QTextCursor) -> tuple[int, int]:

        c = self.c
        line = block.text()
        col = cursor.columnNumber()
        offset = c.p.textOffset()
        fcol_offset = 0
        s2 = line[0:col]
        col = g.computeWidth(s2, c.tab_width)
        #
        # #195: fcol when using @first directive is inaccurate
        i = line.find('<<')
        j = line.find('>>')
        if -1 < i < j or g.match_word(line.strip(), 0, '@others'):
            offset = None
        else:
            for tag in ('@first ', '@last '):
                if line.startswith(tag):
                    fcol_offset = len(tag)
                    break
        #
        # fcol is '' if there is no ancestor @<file> node.
        fcol = None if offset is None else max(0, col + offset - fcol_offset)
        return col, fcol
    #@+node:chris.20180320072817.2: *4* qstatus.file_line (not used)
    def file_line(self) -> Optional[int]:
        """
        Return the line of the first line of c.p in its external file.
        Return None if c.p is not part of an external file.
        """
        c, p = self.c, self.c.p
        if p:
            goto = gotoCommands.GoToCommands(c)
            return goto.find_node_start(p)
        return None
    #@+node:ekr.20190118082047.1: *4* qstatus.put_status_line
    def put_status_line(self, col: int, fcol: int, row: int, words: int) -> None:

        if 1:
            fcol_part = '' if fcol is None else f" fcol: {fcol}"
            # For now, it seems to0 difficult to get alignment *exactly* right.
            self.put1(f"line: {row:d} col: {col:d} {fcol_part} words: {words}")
        else:
            # #283 is not ready yet, and probably will never be.
            fline = self.file_line()
            fline = '' if fline is None else fline + row
            self.put1(
                f"fline: {fline:2} line: {row:2d} col: {col:2} fcol: {fcol:2}")
    #@+node:ekr.20220911120019.1: *3* QtStatusLineClass: do-nothings
    def disable(self, background: str = None) -> None:
        pass

    def enable(self, background: str = "white") -> None:
        pass

    def isEnabled(self) -> bool:
        return False

    def setFocus(self) -> None:
        pass
    #@-others
#@+node:peckj.20140505102552.10377: ** class QtTabBarWrapper (QTabBar)
class QtTabBarWrapper(QtWidgets.QTabBar):
    #@+others
    #@+node:peckj.20140516114832.10108: *3* __init__
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setMovable(True)
    #@+node:peckj.20140516114832.10109: *3* mouseReleaseEvent (QtTabBarWrapper)
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        # middle click close on tabs -- JMP 20140505
        # closes Launchpad bug: https://bugs.launchpad.net/leo-editor/+bug/1183528
        if event.button() == MouseButton.MiddleButton:
            self.tabCloseRequested.emit(self.tabAt(event.pos()))
        QtWidgets.QTabBar.mouseReleaseEvent(self, event)
    #@-others
#@+node:ekr.20110605121601.18464: ** class TabbedFrameFactory
class TabbedFrameFactory:
    """
    'Toplevel' frame builder for tabbed toplevel interface

    This causes Leo to maintain only one toplevel window,
    with multiple tabs for documents
    """
    #@+others
    #@+node:ekr.20110605121601.18465: *3* TabbedFrameFactory.__init__
    def __init__(self) -> None:
        # Will be created when first frame appears.
        # Workaround a problem setting the window title when tabs are shown.
        self.alwaysShowTabs = True
        self.leoFrames: dict[QWidget, QWidget] = {}
        self.masterFrame: LeoTabbedTopLevel = None
        self.createTabCommands()
    #@+node:ekr.20110605121601.18466: *3* TabbedFrameFactory.createFrame
    def createFrame(self, leoFrame: QWidget) -> QWidget:

        c = leoFrame.c
        tabw = self.masterFrame
        dw = DynamicWindow(c, tabw)
        self.leoFrames[dw] = leoFrame
        # Shorten the title.
        title = os.path.basename(c.mFileName) if c.mFileName else leoFrame.title
        tip = leoFrame.title
        dw.setWindowTitle(tip)
        idx = tabw.addTab(dw, title)
        if tip:
            tabw.setTabToolTip(idx, tip)
        dw.construct(master=tabw)
        tabw.setCurrentIndex(idx)
        g.app.gui.setFilter(c, dw, dw, tag='tabbed-frame')
        #
        # Work around the problem with missing dirty indicator
        # by always showing the tab.
        tabw.tabBar().setVisible(self.alwaysShowTabs or tabw.count() > 1)
        tabw.setTabsClosable(c.config.getBool('outline-tabs-show-close', True))
        if not g.unitTesting:
            # #1327: Must always do this.
            # 2021/09/12: but not for new unit tests!
            dw.show()
            tabw.show()
        return dw
    #@+node:ekr.20110605121601.18468: *3* TabbedFrameFactory.createMaster
    def createMaster(self) -> None:

        window = self.masterFrame = LeoTabbedTopLevel(factory=self)
        tabbar = window.tabBar()
        g.app.gui.attachLeoIcon(window)
        try:
            tabbar.setTabsClosable(True)
            tabbar.tabCloseRequested.connect(self.slotCloseRequest)
        except AttributeError:
            pass  # Qt 4.4 does not support setTabsClosable
        window.currentChanged.connect(self.slotCurrentChanged)
        if 'size' in g.app.debug:
            g.trace(
                f"minimized: {g.app.start_minimized}, "
                f"maximized: {g.app.start_maximized}, "
                f"fullscreen: {g.app.start_fullscreen}")
        #
        # #1189: We *can* (and should) minimize here, to eliminate flash.
        if g.app.start_minimized:
            window.showMinimized()
    #@+node:ekr.20110605121601.18472: *3* TabbedFrameFactory.createTabCommands
    def detachTab(self, wdg: DynamicWindow) -> None:
        """ Detach specified tab as individual toplevel window """
        del self.leoFrames[wdg]
        wdg.setParent(None)
        wdg.show()

    def createTabCommands(self) -> None:
        #@+<< Commands for tabs >>
        #@+node:ekr.20110605121601.18473: *4* << Commands for tabs >>
        @g.command('tab-detach')
        def tab_detach(event: LeoKeyEvent) -> None:
            """ Detach current tab from tab bar """
            if len(self.leoFrames) < 2:
                g.es_print_error("Can't detach last tab")
                return
            c = event['c']
            f = c.frame
            tabwidget = g.app.gui.frameFactory.masterFrame
            tabwidget.detach(tabwidget.indexOf(f.top))
            f.top.setWindowTitle(f.title + ' [D]')

        # this is actually not tab-specific, move elsewhere?

        @g.command('close-others')
        def close_others(event: LeoKeyEvent) -> None:
            """Close all windows except the present window."""
            myc = event['c']
            for c in g.app.commanders():
                if c is not myc:
                    c.close()

        def tab_cycle(offset: int) -> None:

            tabw = self.masterFrame
            cur = tabw.currentIndex()
            count = tabw.count()
            # g.es("cur: %s, count: %s, offset: %s" % (cur,count,offset))
            cur += offset
            if cur < 0:
                cur = count - 1
            elif cur >= count:
                cur = 0
            tabw.setCurrentIndex(cur)
            self.focusCurrentBody()

        @g.command('tab-cycle-next')
        def tab_cycle_next(event: LeoKeyEvent) -> None:
            """ Cycle to next tab """
            tab_cycle(1)

        @g.command('tab-cycle-previous')
        def tab_cycle_previous(event: LeoKeyEvent) -> None:
            """ Cycle to next tab """
            tab_cycle(-1)
        #@-<< Commands for tabs >>
    #@+node:ekr.20110605121601.18467: *3* TabbedFrameFactory.deleteFrame
    def deleteFrame(self, wdg: DynamicWindow) -> None:

        if not wdg:
            return
        if wdg not in self.leoFrames:
            # probably detached tab
            self.masterFrame.delete(wdg)
            return
        tabw = self.masterFrame
        idx = tabw.indexOf(wdg)
        tabw.removeTab(idx)
        del self.leoFrames[wdg]
        wdg2 = tabw.currentWidget()
        if wdg2:
            g.app.selectLeoWindow(wdg2.leo_c)
        tabw.tabBar().setVisible(self.alwaysShowTabs or tabw.count() > 1)
    #@+node:ekr.20110605121601.18471: *3* TabbedFrameFactory.focusCurrentBody
    def focusCurrentBody(self) -> None:
        """ Focus body control of current tab """
        tabw = self.masterFrame
        w = tabw.currentWidget()
        w.setFocus()
        f = self.leoFrames[w]
        c = f.c
        c.bodyWantsFocusNow()
        # Fix bug 690260: correct the log.
        g.app.log = f.log
    #@+node:ekr.20110605121601.18469: *3* TabbedFrameFactory.setTabForCommander
    def setTabForCommander(self, c: Cmdr) -> None:
        tabw = self.masterFrame  # a QTabWidget
        for dw in self.leoFrames:  # A dict whose keys are DynamicWindows.
            if dw.leo_c == c:
                for i in range(tabw.count()):
                    if tabw.widget(i) == dw:
                        tabw.setCurrentIndex(i)
                        break
                break
    #@+node:ekr.20110605121601.18470: *3* TabbedFrameFactory.signal handlers
    def slotCloseRequest(self, idx: int) -> None:

        tabw = self.masterFrame
        w = tabw.widget(idx)
        f = self.leoFrames[w]
        c = f.c
        # 2012/03/04: Don't set the frame here.
        # Wait until the next slotCurrentChanged event.
        # This keeps the log and the QTabbedWidget in sync.
        c.close(new_c=None)

    def slotCurrentChanged(self, idx: int) -> None:
        # Two events are generated, one for the tab losing focus,
        # and another event for the tab gaining focus.
        tabw = self.masterFrame
        w = tabw.widget(idx)
        f = self.leoFrames.get(w)
        if not f:
            return
        c = f.c
        title = c.computeWindowTitle()
        tabw.setWindowTitle(title)
        # Don't do this: it would break --minimize.
            # g.app.selectLeoWindow(f.c)
        # Fix bug 690260: correct the log.
        g.app.log = f.log
        # Redraw the tab.
        c = f.c
        if c:
            c.redraw()
    #@-others
#@+node:ekr.20200303082457.1: ** top-level commands (qt_frame.py)
#@+node:ekr.20241027140721.1: *3* contract-*-pane commands
#@+node:ekr.20200303082511.6: *4* 'contract-body-pane'
@g.command('contract-body-pane')
def contractBodyPane(event: LeoKeyEvent) -> None:
    """Contract the body pane. Expand the outline/log splitter."""
    c = event.get('c')
    if c:
        c.frame.top.layout_cache.contract_body()
#@+node:ekr.20200303084048.1: *4* 'contract-log-pane'
@g.command('contract-log-pane')
def contractLogPane(event: LeoKeyEvent) -> None:
    """Contract the log pane. Expand the outline pane."""
    c = event.get('c')
    if c:
        c.frame.top.layout_cache.contract_log()
#@+node:ekr.20200303084225.1: *4* 'contract-outline-pane'
@g.command('contract-outline-pane')
def contractOutlinePane(event: LeoKeyEvent) -> None:
    """Contract the outline pane. Expand the body pane."""
    c = event.get('c')
    if c:
        c.frame.top.layout_cache.contract_outline()
#@+node:ekr.20241027140603.1: *4* 'contract-vr-pane'
@g.command('contract-vr-pane')
def contractVRPane(event: LeoKeyEvent) -> None:
    """Contract the outline pane. Expand the body pane."""
    c = event.get('c')
    if c:
        c.frame.top.layout_cache.contract_vr()
#@+node:ekr.20241027140620.1: *4* 'contract-vr3-pane'
@g.command('contract-vr3-pane')
def contractVR3Pane(event: LeoKeyEvent) -> None:
    """Contract the outline pane. Expand the body pane."""
    c = event.get('c')
    if c:
        c.frame.top.layout_cache.contract_vr3()
#@+node:ekr.20241027140739.1: *3* expand-*-pane commands
#@+node:ekr.20241027124820.1: *4* 'expand-body-pane
@g.command('expand-body-pane')
def expandBodyPane(event: LeoKeyEvent) -> None:
    """Expand the log pane. Contract the outline pane."""
    c = event.get('c')
    if c:
        c.frame.top.layout_cache.expand_body()
#@+node:ekr.20200303084226.1: *4* 'expand-log-pane'
@g.command('expand-log-pane')
def expandLogPane(event: LeoKeyEvent) -> None:
    """Expand the log pane. Contract the outline pane."""
    c = event.get('c')
    if c:
        c.frame.top.layout_cache.expand_log()
#@+node:ekr.20241027124753.1: *4* 'expand-outline-pane'
@g.command('expand-outline-pane')
def expandOutlinePane(event: LeoKeyEvent) -> None:
    """Expand the log pane. Contract the outline pane."""
    c = event.get('c')
    if c:
        c.frame.top.layout_cache.expand_outline()
#@+node:ekr.20241027140647.1: *4* 'expand-vr-pane'
@g.command('expand-vr-pane')
def expandVRPane(event: LeoKeyEvent) -> None:
    """Expand the log pane. Contract the outline pane."""
    c = event.get('c')
    if c:
        c.frame.top.layout_cache.expand_vr()
#@+node:ekr.20241027140706.1: *4* 'expand-vr3-pane'
@g.command('expand-vr3-pane')
def expandVR3Pane(event: LeoKeyEvent) -> None:
    """Expand the log pane. Contract the outline pane."""
    c = event.get('c')
    if c:
        c.frame.top.layout_cache.expand_vr3()
#@+node:ekr.20241027140819.1: *3* hide-* commands
#@+node:ekr.20200303084610.1: *4* 'hide-body-pane'
@g.command('hide-body-pane')
def hideBodyPane(event: LeoKeyEvent) -> None:
    """Hide the body pane. Fully expand the outline/log splitter."""
    c = event.get('c')
    if not c:
        return
    c.frame.divideLeoSplitter1(1.0)
#@+node:ekr.20231102130853.1: *4* 'hide-icon-bar'
@g.command('hide-icon-bar')
def hideIconBar(event: LeoKeyEvent) -> None:
    c = event.get('c')
    if c:
        dw = c.frame.top
        dw.iconBar.hide()
#@+node:ekr.20200303084625.1: *4* 'hide-log-pane'
@g.command('hide-log-pane')
def hideLogPane(event: LeoKeyEvent) -> None:
    """Hide the log pane. Fully expand the outline pane."""
    c = event.get('c')
    if not c:
        return
    c.frame.divideLeoSplitter2(1.0)
#@+node:ekr.20231102131048.1: *4* 'hide-minibuffer'
@g.command('hide-minibuffer')
def hideMinibuffer(event: LeoKeyEvent) -> None:
    c = event.get('c')
    if c:
        dw = c.frame.top
        dw.leo_minibuffer_frame.hide()
#@+node:ekr.20200303082511.7: *4* 'hide-outline-pane'
@g.command('hide-outline-pane')
def hideOutlinePane(event: LeoKeyEvent) -> None:
    """Hide the outline/log splitter. Fully expand the body pane."""
    c = event.get('c')
    if not c:
        return
    c.frame.divideLeoSplitter1(0.0)

#@+node:ekr.20231102130902.1: *4* 'hide-status-bar'
@g.command('hide-status-bar')
def hideStatusBar(event: LeoKeyEvent) -> None:
    c = event.get('c')
    if c:
        dw = c.frame.top
        dw.statusBar.hide()
#@+node:ekr.20241027140853.1: *3* show-* commands
#@+node:ekr.20241027140945.1: *4* 'show-icon-bar'
@g.command('show-icon-bar')
def showIconBar(event: LeoKeyEvent) -> None:
    c = event.get('c')
    if c:
        dw = c.frame.top
        dw.iconBar.show()
#@+node:ekr.20241027141052.1: *4* 'show-minibuffer'
@g.command('show-minibuffer')
def showMinibuffer(event: LeoKeyEvent) -> None:
    c = event.get('c')
    if c:
        dw = c.frame.top
        dw.leo_minibuffer_frame.show()
#@+node:ekr.20240518150051.1: *4* 'show-qt-widgets'
@g.command('print-qt-widgets')
@g.command('show-qt-widgets')
def showQtWidgets(event: LeoKeyEvent) -> None:
    """Print the hierarchy of qt widgets."""
    c = event.get('c')
    total = 0
    if not c:
        return

    def w_name(w):
        name = w.objectName() or 'no name'
        return f"{ w.__class__.__name__}({name})"

    def dump(w, level=0):
        nonlocal total
        total += 1
        ws = level * '.'
        print(f"{total:3} {level:3}: {ws}{w_name(w)}")

    def dump_children(w, level=0):
        if 1:  # Specify wanted classes...
            wanted = (
                'DynamicWindow', 'Frame', 'Layout',
                'Splitter', 'Stacked', 'Text', 'Widget',
            )
            children = [z for z in w.children()
                if any(z2 in z.__class__.__name__ for z2 in wanted)]
        else:  # Specifiy unwanted classes...
            ignore = ('action', 'animation', 'menu')
            children = [z for z in w.children()
                if not any(z2 in z.__class__.__name__.lower() for z2 in ignore)]
        if children:
            for i, child in enumerate(children):
                dump(child, level + 1)
                dump_children(child, level + 1)

    def full_dump(w, level=0):
        print('')
        print('Full dump of c.frame.top:\n')
        print('  i   level')
        dump(w)
        dump_children(w)

    full_dump(c.frame.top)
#@+node:ekr.20241027141138.1: *4* 'show-status-bar'
@g.command('show-status-bar')
def showStatusBar(event: LeoKeyEvent) -> None:
    c = event.get('c')
    if c:
        dw = c.frame.top
        dw.statusBar.show()
#@+node:ekr.20241027140920.1: *3* toggle-* commands
#@+node:ekr.20241027141012.1: *4* 'toggle-icon-bar'
@g.command('toggle-icon-bar')
def toggleIconBar(event: LeoKeyEvent) -> None:
    c = event.get('c')
    if c:
        dw = c.frame.top
        w = dw.iconBar
        if w.isVisible():
            w.hide()
        else:
            w.show()
#@+node:ekr.20241027141108.1: *4* 'toggle-minibuffer'
@g.command('toggle-minibuffer')
def toggleMinibuffer(event: LeoKeyEvent) -> None:
    c = event.get('c')
    if c:
        dw = c.frame.top
        w = dw.leo_minibuffer_frame
        if w.isVisible():
            w.hide()
        else:
            w.show()
#@+node:ekr.20241027141155.1: *4* 'toggle-status-bar'
@g.command('toggle-status-bar')
def toggleStatusBar(event: LeoKeyEvent) -> None:
    c = event.get('c')
    if c:
        dw = c.frame.top
        w = dw.statusBar
        if w.isVisible():
            w.hide()
        else:
            w.show()
#@+node:ekr.20240505045118.1: *4* 'toggle-unl-view'
@g.command('toggle-unl-view')
def toggleUnlView(event: LeoKeyEvent) -> None:
    c = event.get('c')
    if c and c.frame.statusLine:
        # This is not a convenience method.
        c.frame.statusLine.toggleUnlView()
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
