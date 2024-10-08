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

CACHENAME = 'leo-layout-cache'
FALLBACK_LAYOUT_NAME = 'layout-fallback-layout'

#@+others
#@+node:ekr.20241008141246.1: ** function: init
def init() -> bool:
    """Return True if this plugin should be enabled."""
    return True
#@+node:ekr.20241008141353.1: ** function: show_vr_pane
def show_vr_pane(c, w):
    w.setUpdatesEnabled(True)
    c.doCommandByName('vr-show')
#@+node:tom.20240923194438.3: ** FALLBACK_LAYOUT
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

@g.command(FALLBACK_LAYOUT_NAME)
def fallback_layout(event: LeoKeyEvent) -> None:
    """Apply a workable layout in case the layout setting is invalid."""
    c = event.get('c')
    dw = c.frame.top
    cache = dw.layout_cache
    cache.restoreFromLayout(FALLBACK_LAYOUT)
#@+node:tom.20240930101515.1: ** restoreDefaultLayout
@g.command('layout-restore-default')
def restoreDefaultLayout(event: LeoKeyEvent) -> None:
    """Restore the default layout specified in @settings, if known."""
    c = event.get('c')
    if not c:
        return
    event = g.app.gui.create_key_event(c)

    found_layout = False
    layout = default_layout = c.config.getString('qt-layout-name')
    if not layout:
        layout = FALLBACK_LAYOUT_NAME
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

#@+node:tom.20240928165801.1: ** Built-in Layouts
# Define commands to create some standard layouts
#@+others
#@+node:tom.20240928195823.1: *3* legacy
# Recreate the layout called "legacy" in the Dynamic Window code.
LEGACY_LAYOUT = {
    'SPLITTERS': OrderedDict(
            (('outlineFrame', 'secondary_splitter'),
            ('logFrame', 'secondary_splitter'),
            ('bodyFrame', 'body-vr-splitter'),
            ('viewrendered_pane', 'body-vr-splitter'),
            ('secondary_splitter', 'main_splitter'),
            ('body-vr-splitter', 'main_splitter'))
        ),
    'ORIENTATIONS': {
        'body-vr-splitter': Orientation.Horizontal,
        'secondary_splitter': Orientation.Horizontal,
        'main_splitter': Orientation.Vertical
    }
}

@g.command('layout-legacy')
def layout_legacy(event: LeoKeyEvent) -> None:
    """Create Leo's legacy layout."""
    c = event.get('c')
    dw = c.frame.top
    cache = dw.layout_cache
    cache.restoreFromLayout(LEGACY_LAYOUT)

    # Find or create VR widget
    vr = cache.find_widget('viewrendered_pane')
    if not vr:
        import leo.plugins.viewrendered as v
        vr = v.getVr(c=c)

    bvs = cache.find_widget('body-vr-splitter')
    bvs.addWidget(vr)
    c.doCommandByName('vr-show')
#@+node:tom.20240928170706.1: *3* horizontal-thirds
HORIZONTAL_THIRDS_LAYOUT = {
    'SPLITTERS': OrderedDict(
            (('outlineFrame', 'secondary_splitter'),
            ('logFrame', 'secondary_splitter'),
            ('secondary_splitter', 'main_splitter'),
            ('bodyFrame', 'main_splitter'),
            ('viewrendered3_pane', 'main_splitter'))
        ),
    'ORIENTATIONS': {
        'secondary_splitter': Orientation.Horizontal,
        'main_splitter': Orientation.Vertical
    }
}


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
    import leo.plugins.viewrendered3 as v3
    v3.getVr3({'c': c})
    cache.restoreFromLayout(HORIZONTAL_THIRDS_LAYOUT)
#@+node:tom.20240928171510.1: *3* big-tree
@g.command('layout-big-tree')
def big_tree(event: LeoKeyEvent) -> None:
    """Apply the "big-tree" layout.

    Main splitter: tree, secondary_splitter, VR
    Secondary splitter: body, log.

    Orientations:
        main splitter: vertical
        secondary splitter: horizontal
    """
    c = event.get('c')
    cache = c.frame.top.layout_cache
    cache.restoreFromLayout()

    ms = cache.find_widget('main_splitter')
    ss = cache.find_widget('secondary_splitter')
    of = cache.find_widget('outlineFrame')
    lf = cache.find_widget('logFrame')
    bf = cache.find_widget('bodyFrame')

    # Find or create VR widget
    vr = cache.find_widget('viewrendered_pane')
    if vr is None:
        import leo.plugins.viewrendered as v
        vr = v.getVr()
#@+at
#     # For VR3 instead
#     vr = cache.find_widget('viewrendered3_pane')
#     if not vr:
#         import leo.plugins.viewrendered3 as v
#         try:
#         vr = v.getVr3({'c':c})
#@@c
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
    if vr is not None:
        c.doCommandByName('vr-show')

    # Set splitter sizes
    ms.setSizes([100_000] * len(ms.sizes()))
    ss.setSizes([100_000] * len(ss.sizes()))

    # Avoid flash each time VR pane is re-opened.
    QtCore.QTimer.singleShot(60, lambda: show_vr_pane(c, vr))

#@+node:tom.20240929101820.1: *3* render-focused
RENDERED_FOCUSED_LAYOUT = {
    'SPLITTERS': OrderedDict(
            (('outlineFrame', 'secondary_splitter'),
            ('bodyFrame', 'secondary_splitter'),
            ('logFrame', 'secondary_splitter'),
            ('viewrendered_pane', 'body-vr-splitter'),
            ('secondary_splitter', 'main_splitter'),
            ('body-vr-splitter', 'main_splitter'))
        ),
    'ORIENTATIONS': {
        'body-vr-splitter': Orientation.Horizontal,
        'secondary_splitter': Orientation.Vertical,
        'main_splitter': Orientation.Horizontal
    }
}

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

    # # Find or create VR widget
    # vr = cache.find_widget('viewrendered_pane')
    # if not vr:
        # import leo.plugins.viewrendered as v
        # vr = v.getVr(c=c)

    # bvs = cache.find_widget('body-vr-splitter')
    # bvs.addWidget(vr)

    # QtCore.QTimer.singleShot(60, lambda: show_vr_pane(c, vr))
#@+node:tom.20240929104728.1: *3* vertical-thirds
VERTICAL_THIRDS_LAYOUT = {
    'SPLITTERS': OrderedDict(
            (('outlineFrame', 'secondary_splitter'),
            ('logFrame', 'secondary_splitter'),
            ('secondary_splitter', 'main_splitter'),
            ('bodyFrame', 'main_splitter'),
            ('viewrendered_pane', 'main_splitter'))
        ),
    'ORIENTATIONS': {
        'secondary_splitter': Orientation.Vertical,
        'main_splitter': Orientation.Horizontal
    }
}

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

    # # Find or create VR widget
    # vr = cache.find_widget('viewrendered_pane')
    # if not vr:
        # import leo.plugins.viewrendered as v
        # vr = v.getVr(c=c)

    # ms = cache.find_widget('main_splitter')
    # ms.addWidget(vr)
    # QtCore.QTimer.singleShot(60, lambda: show_vr_pane(c, vr))
#@+node:tom.20240929115043.1: *3* vertical-thirds2
VERTICAL_THIRDS2_LAYOUT = {
    'SPLITTERS': OrderedDict(
        (('logFrame', 'secondary_splitter'),
        ('bodyFrame', 'secondary_splitter'),
        ('outlineFrame', 'main_splitter'),
        ('viewrendered_pane', 'vr-splitter'),
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

    # # Find or create VR widget
    # vr = cache.find_widget('viewrendered_pane')
    # if not vr:
        # import leo.plugins.viewrendered as v
        # vr = v.getVr(c=c)

    # ms = cache.find_widget('vr-splitter')
    # ms.addWidget(vr)
    # QtCore.QTimer.singleShot(60, lambda: show_vr_pane(c, vr))
#@-others
#@+node:tom.20240930164141.1: ** Other Layouts
#@+node:tom.20240930164155.1: *3* Quadrant
QUADRANT_LAYOUT = {
    'SPLITTERS': OrderedDict(
        (
            ('bodyFrame', 'secondary_splitter'),
            ('viewrendered_pane', 'secondary_splitter'),
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

@g.command('layout-quadrant')
def quadrants(event: LeoKeyEvent) -> None:
    """Create a "quadrant layout:
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
#@+node:tom.20241005163724.1: *3* Swap Log Pane Location
@g.command('layout-swap-log-panel')
def swapLogPanel(event: LeoKeyEvent) -> None:
    """Move Log frame between main and secondary splitters.

       If the Log frame is contained in a different splitter,
       possibly with some other widget, the entire splitter
       will be swapped between the main and secondary splitters.
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
        self.setObjectName(CACHENAME)
        # maps splitter objectNames to their splitter object.
        self.created_splitter_dict: Dict[str, Any] = {}

    #@+others
    #@+node:tom.20240923194438.4: *3* find_widget()
    def find_widget_in_children(self, name):
        w = None
        for kid in self.children():
            if kid.objectName() == name:
                w = kid
        return w

    def xfind_widget(self, name):
        w = None
        # Weird - g.app.gui.find_widget_by_name() may not find object in ourself
        w = self.created_splitter_dict.get(name)

        w1 = self.find_widget_in_children(name)
        if w1 is not None and w is not None:
            w = w1

        w2 = g.app.gui.find_widget_by_name(self.c, name)
        if w2 is not None and w is None:
            w = w2
        return w

    def find_widget(self, name):
        return g.app.gui.find_widget_by_name(self.c, name)
    #@+node:tom.20240923194438.5: *3* find_splitter_by_name()
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
    #@+node:tom.20240923194438.6: *3* restoreFromLayout
    def restoreFromLayout(self, layout=None):
        if layout is None:
            layout = FALLBACK_LAYOUT
        #@+<< initialize data structures >>
        #@+node:tom.20240923194438.7: *4* << initialize data structures >>
        SPLITTERS = layout['SPLITTERS']
        ORIENTATIONS = layout['ORIENTATIONS']

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
            # Redundant, already checked in self.find_splitter_by_name()
            # if splitter is None:
                # splitter = self.created_splitter_dict[name]
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
