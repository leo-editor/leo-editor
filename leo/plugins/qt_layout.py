#@+leo-ver=5-thin
#@+node:tom.20240923194438.1: * @file ../plugins/qt_layout.py
"""The basic machinery to support applying layouts of the main Leo panels."""

#@+<< qt_layout: imports >>
#@+node:tom.20240923194438.2: ** << qt_layout: imports >>
from __future__ import annotations

from collections import OrderedDict
from typing import Any, Dict, TYPE_CHECKING

from leo.core.leoQt import QtWidgets, Orientation, QtCore
from leo.core import leoGlobals as g

QWidget = QtWidgets.QWidget
if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent
    # from typing import TypeAlias  # Requires Python 3.12+
    Args = Any
    KWargs = Any
#@-<< qt_layout: imports >>

#@+others
#@+node:tom.20241009141008.1: ** Declarations
VR3_OBJ_NAME = 'viewrendered3_pane'
VR_OBJ_NAME = 'viewrendered_pane'
VRX_PLACEHOLDER_NAME = 'viewrenderedx_pane'

VR_MODULE_NAME = 'viewrendered.py'
VR3_MODULE_NAME = 'viewrendered3.py'
#@+node:ekr.20241008174359.1: ** Top-level functions
#@+node:ekr.20241008141246.1: *3* function: init
def init() -> bool:
    """Return True if this plugin should be enabled."""
    # qt_layout is not a true plugin.
    return True
#@+node:ekr.20241008141353.1: *3* function: show_vr3_pane
def show_vr3_pane(c, w):
    w.setUpdatesEnabled(True)
    c.doCommandByName('vr3-show')
#@+node:tom.20241009141223.1: *3* function: is_module_loaded
def is_module_loaded(module_name):
    """Return True if the plugins controller has loaded the module.
    """
    controller = g.app.pluginsController
    return controller.isLoaded(module_name)
#@+node:ekr.20241008174351.1: ** Layout commands
#@+node:tom.20240928171510.1: *3* command: 'layout-big-tree'
@g.command('layout-big-tree')
def big_tree(event: LeoKeyEvent) -> None:
    """Create Leo's big-tree layout:
        ┌──────────────────┐
        │  outline         │
        ├──────────┬───────┤
        │  body    │  log  │
        ├──────────┴───────┤
        │  VR              │
        └──────────────────┘
    """
    c = event.get('c')
    cache = c.frame.top.layout_cache
    cache.restoreFromLayout()

    has_vr3 = is_module_loaded(VR3_MODULE_NAME)

    ms = cache.find_widget('main_splitter')
    ss = cache.find_widget('secondary_splitter')
    of = cache.find_widget('outlineFrame')
    lf = cache.find_widget('logFrame')
    bf = cache.find_widget('bodyFrame')

    if has_vr3:
        vr = cache.find_widget('viewrendered3_pane')
        if vr is None:
            import leo.plugins.viewrendered3 as vr3_mod
            h = c.hash()
            vr3_mod.controllers[h] = vr = vr3_mod.ViewRenderedController3(c)
    else:
        vr = cache.find_widget('viewrendered_pane')

    # Clear out splitters so we can add widgets back in the right order
    for widget in (ss, of, lf, bf, vr):  # Don't remove ms!
        if widget is not None:
            widget.setParent(None)

    # Move widgets to target splitters
    of.setParent(ms)
    ss.setParent(ms)
    if vr is not None:
        vr.setParent(ms)
    bf.setParent(ss)
    lf.setParent(ss)

    # set Orientations
    ms.setOrientation(Orientation.Vertical)
    ss.setOrientation(Orientation.Horizontal)

    # Re-parenting a widget to None hides it, so show it now
    widgets = [ss, of, lf, bf]
    if vr is not None:
        widgets.append(vr)
    for widget in widgets:
        widget.show()

    # Set splitter sizes
    ms.setSizes([100_000] * len(ms.sizes()))
    ss.setSizes([100_000] * len(ss.sizes()))

    if vr is not None:
        if has_vr3:
            # Avoid flash each time VR pane is re-opened.
            QtCore.QTimer.singleShot(60, lambda: show_vr3_pane(c, vr))
        else:
            c.doCommandByName('vr-show')
#@+node:ekr.20241008174424.1: *3* command: 'layout-fallback-layout'
@g.command('layout-fallback-layout')
def fallback_layout(event: LeoKeyEvent) -> None:
    """Apply a workable layout in case the layout setting is invalid."""
    c = event.get('c')
    dw = c.frame.top
    cache = dw.layout_cache
    cache.restoreFromLayout(FALLBACK_LAYOUT)
#@+node:ekr.20241008174427.1: *3* command: 'layout-horizontal-thirds'
@g.command('layout-horizontal-thirds')
def horizontal_thirds(event: LeoKeyEvent) -> None:
    """Create Leo's horizontal-thirds layout:
        ┌───────────┬───────┐
        │  outline  │  log  │
        ├───────────┴───────┤
        │  body             │
        ├───────────────────┤
        │  VR               │
        └───────────────────┘
    """
    c = event.get('c')
    dw = c.frame.top
    cache = dw.layout_cache
    cache.restoreFromLayout(HORIZONTAL_THIRDS_LAYOUT)
#@+node:ekr.20241008180407.1: *3* command: 'layout-quadrant'
@g.command('layout-quadrant')
@g.command('layout-legacy')
def quadrants(event: LeoKeyEvent) -> None:
    """Create Leo's quadrant layout:
        ┌───────────────┬───────────┐
        │   outline     │   log     │
        ├───────────────┼───────────┤
        │   body        │     vr    │
        └───────────────┴───────────┘
    """
    c = event.get('c')
    dw = c.frame.top
    cache = dw.layout_cache
    cache.restoreFromLayout(QUADRANT_LAYOUT)
#@+node:ekr.20241008174427.2: *3* command: 'layout-render-focused'
@g.command('layout-render-focused')
def render_focused(event: LeoKeyEvent) -> None:
    """Create Leo's render-focused layout:
        ┌───────────┬─────┐
        │ outline   │     │
        ├───────────┤     │
        │ body      │ VR  │
        ├───────────┤     │
        │ log       │     │
        └───────────┴─────┘
    """
    c = event.get('c')
    dw = c.frame.top
    cache = dw.layout_cache
    cache.restoreFromLayout(RENDERED_FOCUSED_LAYOUT)
#@+node:tom.20240930101515.1: *3* command: 'layout-restore-default'
@g.command('layout-restore-default')
@g.command('layout-restore-to-setting')
def restoreDefaultLayout(event: LeoKeyEvent) -> None:
    """Restore the default layout specified in @settings, if known."""
    c = event.get('c')
    if not c:
        return
    event = g.app.gui.create_key_event(c)

    found_layout = False
    layout = default_layout = c.config.getString('qt-layout-name')
    if not layout:
        layout = 'layout-fallback-layout'
    elif default_layout.startswith('layout-'):
        if default_layout in c.commandsDict:
            found_layout = True
    else:
        layout = 'layout-' + default_layout
        if layout in c.commandsDict:
            found_layout = True
        elif default_layout in c.commandsDict:
            layout = default_layout
            found_layout = True
        else:
            g.es(f'Cannot find command {layout} or {default_layout}')
    if found_layout:
        c.commandsDict[layout](event)

#@+node:tom.20241005163724.1: *3* command: 'layout-swap-log-panel'
@g.command('layout-swap-log-panel')
def swapLogPanel(event: LeoKeyEvent) -> None:
    """Move Log frame between main and secondary splitters.

    If the Log frame is contained in a different splitter, possibly with
    some other widget, the entire splitter will be swapped between the main
    and secondary splitters.

    The effect of this command depends on the existing layout. For example,
    if the legacy layout is in effect, this command changes the layout
    from:
        ┌───────────┬──────┐
        │ outline   │ log  │
        ├───────────┼──────┤
        │ body      │ VR   │
        └───────────┴──────┘
    to:
        ┌──────────────────┐
        │  outline         │
        ├──────────┬───────┤
        │  body    │  VR   │
        ├──────────┴───────┤
        │  Log             │
        └──────────────────┘
    """
    c = event.get('c')
    if not c:
        return
    gui = g.app.gui

    ms = gui.find_widget_by_name(c, 'main_splitter')
    ss = gui.find_widget_by_name(c, 'secondary_splitter')
    lf = gui.find_widget_by_name(c, 'logFrame')

    lf_parent = lf.parent()
    lf_parent_container = lf_parent.parent()
    widget = None

    if lf_parent in (ss, ms):
        # Move just the lf
        target = ms if lf_parent is ss else ss
        widget = lf
    elif lf_parent_container in (ms, ss):
        # Move lf's entire container
        target = ms if lf_parent_container is ss else ss
        widget = lf_parent
    else:
        g.es("Don't know what widget or container to swap")

    if widget is not None:
        target.addWidget(widget)
        g.app.gui.equalize_splitter(target)
#@+node:ekr.20241008175137.1: *3* command: 'layout-vertical-thirds'
@g.command('layout-vertical-thirds')
def vertical_thirds(event: LeoKeyEvent) -> None:
    """Create Leo's vertical-thirds layout:
        ┌───────────┬────────┬──────┐
        │  outline  │        │      │
        ├───────────┤  body  │  VR  │
        │  log      │        │      │
        └───────────┴────────┴──────┘
    """
    c = event.get('c')
    dw = c.frame.top
    cache = dw.layout_cache
    cache.restoreFromLayout(VERTICAL_THIRDS_LAYOUT)

#@+node:ekr.20241008175303.1: *3* command: 'layout-vertical-thirds2'
@g.command('layout-vertical-thirds2')
def vertical_thirds2(event: LeoKeyEvent) -> None:
    """Create Leo's vertical-thirds2 layout:
        ┌───────────┬───────┬───────┐
        │           │  log  │       │
        │  outline  ├───────┤  VR   │
        │           │  body │       │
        └───────────┴───────┴───────┘
    """
    c = event.get('c')
    dw = c.frame.top
    cache = dw.layout_cache
    cache.restoreFromLayout(VERTICAL_THIRDS2_LAYOUT)
#@+node:ekr.20241008174638.1: ** Layouts
#@+node:tom.20240923194438.3: *3* FALLBACK_LAYOUT
FALLBACK_LAYOUT = {
    'SPLITTERS': OrderedDict(
        (('outlineFrame', 'secondary_splitter'),
        ('logFrame', 'secondary_splitter'),
        ('secondary_splitter', 'main_splitter'),
        ('bodyFrame', 'main_splitter'))
    ),
    'ORIENTATIONS': {
        'main_splitter': Orientation.Horizontal,
        'secondary_splitter': Orientation.Vertical,
    }
}
#@+node:tom.20240928170706.1: *3* HORIZONTAL_THIRDS_LAYOUT
HORIZONTAL_THIRDS_LAYOUT = {
    'SPLITTERS': OrderedDict(
            (('outlineFrame', 'secondary_splitter'),
            ('logFrame', 'secondary_splitter'),
            ('secondary_splitter', 'main_splitter'),
            ('bodyFrame', 'main_splitter'),
            ('viewrenderedx_pane', 'main_splitter'))
        ),
    'ORIENTATIONS': {
        'secondary_splitter': Orientation.Horizontal,
        'main_splitter': Orientation.Vertical
    }
}
#@+node:tom.20240930164155.1: *3* QUADRANT_LAYOUT
QUADRANT_LAYOUT = {
    'SPLITTERS': OrderedDict(
        (
            ('bodyFrame', 'secondary_splitter'),
            ('viewrenderedx_pane', 'secondary_splitter'),
            ('outlineFrame', 'outline-log-splitter'),
            ('logFrame', 'outline-log-splitter'),
            ('outline-log-splitter', 'main_splitter'),
            ('secondary_splitter', 'main_splitter'),
        )
    ),
    'ORIENTATIONS': {
        'outline-log-splitter': Orientation.Horizontal,
        'secondary_splitter': Orientation.Horizontal,
        'main_splitter': Orientation.Vertical,
    }
}
#@+node:tom.20240929101820.1: *3* RENDERED_FOCUSED_LAYOUT
RENDERED_FOCUSED_LAYOUT = {
    'SPLITTERS': OrderedDict(
            (('outlineFrame', 'secondary_splitter'),
            ('bodyFrame', 'secondary_splitter'),
            ('logFrame', 'secondary_splitter'),
            ('viewrenderedx_pane', 'body-vr-splitter'),
            ('secondary_splitter', 'main_splitter'),
            ('body-vr-splitter', 'main_splitter'))
        ),
    'ORIENTATIONS': {
        'body-vr-splitter': Orientation.Horizontal,
        'secondary_splitter': Orientation.Vertical,
        'main_splitter': Orientation.Horizontal
    }
}

#@+node:tom.20240929115043.1: *3* VERTICAL_THIRDS2_LAYOUT
VERTICAL_THIRDS2_LAYOUT = {
    'SPLITTERS': OrderedDict(
        (('logFrame', 'secondary_splitter'),
        ('bodyFrame', 'secondary_splitter'),
        ('outlineFrame', 'main_splitter'),
        ('viewrenderedx_pane', 'vr-splitter'),
        ('secondary_splitter', 'main_splitter'),
        ('vr-splitter', 'main_splitter')
        )
    ),
    'ORIENTATIONS': {
        'vr-splitter': Orientation.Vertical,
        'secondary_splitter': Orientation.Vertical,
        'main_splitter': Orientation.Horizontal
    }
}
#@+node:tom.20240929104728.1: *3* VERTICAL_THIRDS_LAYOUT
VERTICAL_THIRDS_LAYOUT = {
    'SPLITTERS': OrderedDict(
            (('outlineFrame', 'secondary_splitter'),
            ('logFrame', 'secondary_splitter'),
            ('secondary_splitter', 'main_splitter'),
            ('bodyFrame', 'main_splitter'),
            ('viewrenderedx_pane', 'main_splitter'))
        ),
    'ORIENTATIONS': {
        'secondary_splitter': Orientation.Vertical,
        'main_splitter': Orientation.Horizontal
    }
}
#@+node:tom.20240930095459.1: ** class LayoutCacheWidget
class LayoutCacheWidget(QWidget):
    """
    Manage layout such as the following:

        FALLBACK_LAYOUT = {
            'SPLITTERS':OrderedDict(
                (('outlineFrame', 'secondary_splitter'),
                ('logFrame', 'secondary_splitter'),
                ('secondary_splitter', 'main_splitter'),
                ('bodyFrame', 'main_splitter'))
            ),
            'ORIENTATIONS':{
            'main_splitter':Orientation.Horizontal,
            'secondary_splitter':Orientation.Vertical}
        }
    """

    def __init__(self, c: Cmdr, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.c = c
        self.setObjectName('leo-layout-cache')
        # maps splitter objectNames to their splitter object.
        self.created_splitter_dict: Dict[str, Any] = {}

    #@+others
    #@+node:tom.20240923194438.5: *3* LayoutCacheWidget.find_splitter_by_name
    def find_splitter_by_name(self, name):
        foundit = False
        splitter = None
        splitter = self.find_widget(name)
        if splitter is not None:
            foundit = True
        if not foundit:
            splitter = self.created_splitter_dict.get(name, None)
            if splitter is not None:
                foundit = True
        if not foundit:
            for kid in self.children():
                if kid.objectName() == name:
                    foundit = True
                    splitter = kid
                    break
        return splitter
    #@+node:ekr.20241008180818.1: *3* LayoutCacheWidget.find_widget
    def find_widget(self, name):
        return g.app.gui.find_widget_by_name(self.c, name)
    #@+node:tom.20240923194438.4: *3* LayoutCacheWidget.find_widget_in_children
    def find_widget_in_children(self, name):
        w = None
        for kid in self.children():
            if kid.objectName() == name:
                w = kid
        return w

    #@+node:tom.20240923194438.6: *3* LayoutCacheWidget.restoreFromLayout
    def restoreFromLayout(self, layout=None):
        if layout is None:
            layout = FALLBACK_LAYOUT
        #@+<< initialize data structures >>
        #@+node:tom.20240923194438.7: *4* << initialize data structures >>
        ORIENTATIONS = layout['ORIENTATIONS']

        has_vr3 = is_module_loaded(VR3_MODULE_NAME)
        if has_vr3:
            if (vr3 := self.find_widget('viewrendered3_pane')) is None:
                import leo.plugins.viewrendered3 as vr3_mod
                vr3 = vr3_mod.getVr3({'c': self.c})
            vr3.setParent(self)

        # A layout might want to use VR3 if it is present, else VR.
        # This is indicated by using the name VRX_PLACEHOLDER_NAME in the layout.
        # In building the SPLITTER dict we replace the placeholder
        # by VR3_OBJ_NAME if it exists, otherwise VR_OBJ_NAME.
        SPLITTERS = dict()
        for k, v in layout['SPLITTERS'].items():
            if k == VRX_PLACEHOLDER_NAME:
                k = VR3_OBJ_NAME if has_vr3 else VR_OBJ_NAME
            SPLITTERS[k] = v

        # Make unknown splitters.
        # If a splitter name is not known or does not exist, create one
        # and add it to self.created_splitter_dict.
        for _, name in SPLITTERS.items():
            splitter = self.find_splitter_by_name(name)
            if splitter is None:
                splitter = QtWidgets.QSplitter(self)
                splitter.setObjectName(name)
                self.created_splitter_dict[name] = splitter

        SPLITTER_DICT: Dict[str, Any] = OrderedDict()
        for name in ORIENTATIONS:
            splitter = self.find_splitter_by_name(name)
            if splitter is not None and SPLITTER_DICT.get(name, None) is None:
                SPLITTER_DICT[name] = splitter

        #@-<< initialize data structures >>
        #@+<< rehome body editor >>
        #@+node:tom.20240923194438.8: *4* << rehome body editor >>
        # In case the editor has been moved to e.g. a QTabWidget,
        # Move it back to its standard place.

        bsw = self.find_widget('bodyStackedWidget')
        editor = self.find_widget('bodyPage2')
        if bsw.indexOf(editor) == -1:
            bsw.insertWidget(0, editor)
        bsw.setCurrentIndex(0)
        #@-<< rehome body editor >>
        #@+<< clean up splitters >>
        #@+node:tom.20240923194438.9: *4* << clean up splitters >>
        # Remove extra (no longer wanted) widgets to the cache.
        # Then insert the required widgets into their home splitters

        # ESSENTIALS: {'outlineFrame':'secondary_splitter',...}
        # SPLITTERS: {'main_splitter':ms, ...}

        # Cache widgets we don't want
        desired_widget_names = list(SPLITTERS.keys())
        cache_list = []
        for splitter in SPLITTER_DICT.values():
            for i in range(splitter.count()):
                widget = splitter.widget(i)
                try:
                    objname = widget.objectName()
                # Probably can't happen but just in case
                except Exception:
                    objname = ''
                    continue
                if objname and objname not in desired_widget_names:
                    cache_list.append(widget)

        for widget in cache_list:
            if widget not in self.children():
                widget.setParent(self)

        for splitter in self.created_splitter_dict.values():
            if splitter not in self.children():
                splitter.setParent(self)
        #@-<< clean up splitters >>
        #@+<< set default orientations >>
        #@+node:tom.20240923194438.11: *4* << set default orientations >>
        # SPLITTER_DICT: {'main_splitter':ms, ...}
        # DEFAULT_ORIENTATIONS:
        # {'main_splitter':Orientation.Horizontal...}

        for splitter_name, splitter in SPLITTER_DICT.items():
            orientation = ORIENTATIONS[splitter_name]
            splitter.setOrientation(orientation)
        #@-<< set default orientations >>
        #@+<< move widgets to targets >>
        #@+node:tom.20240923194438.10: *4* << move widgets to targets >>
        # Move all desired widgets into their home splitters
        # SPLITTERS is an OrderedDict so the widgets will
        # be inserted in the right order.

        splitter_index: Dict = {}
        for name, target in SPLITTERS.items():
            widget = self.find_widget(name)
            if widget is None:
                widget = self.created_splitter_dict.get(name, None)
            dest = SPLITTER_DICT.get(target, None)
            if widget is not None and dest is not None:
                i = splitter_index[dest] = splitter_index.get(dest, -1) + 1
                if dest is not None:
                    dest.insertWidget(i, widget)
        #@-<< move widgets to targets >>
        #@+<< resize splitters >>
        #@+node:tom.20240923194438.12: *4* << resize splitters >>
        for splt in SPLITTER_DICT.values():
            g.app.gui.equalize_splitter(splt)
        #@-<< resize splitters >>
        editor.show()
    #@-others

#@-others

#@-leo
