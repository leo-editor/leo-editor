#@+leo-ver=5-thin
#@+node:tom.20240923194438.1: * @file ../plugins/qt_layout.py
"""The basic machinery to support applying layouts of the main Leo panels."""
from __future__ import annotations
#@+<< imports >>
#@+node:tom.20240923194438.2: ** << imports >>
from collections import OrderedDict
from typing import Any, TYPE_CHECKING

from leo.core.leoQt import QtWidgets, Orientation, QtCore
# from leo.core.leoCommands import Commands as Cmdr
from leo.core import leoGlobals as g

QWidget = QtWidgets.QWidget
if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent
    # from typing import TypeAlias  # Requires Python 3.12+
    Args = Any
    KWargs = Any
#@-<< imports >>

CACHENAME = 'leo-layout-cache'

def show_vr_pane(c, w):
    w.setUpdatesEnabled(True)
    c.doCommandByName('vr-show')


#@+<< FALLBACK_LAYOUT >>
#@+node:tom.20240923194438.3: ** << FALLBACK_LAYOUT >>
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

@g.command('layout-fallback-layout')
def fallback_layout(event: LeoKeyEvent) -> None:
    """Apply a workable layout in case the layout setting is invalid."""
    c = event.get('c')
    dw = c.frame.top
    cache = dw.layout_cache
    cache.restoreFromLayout(FALLBACK_LAYOUT)
#@-<< FALLBACK_LAYOUT >>
#@+<< Built-in Layouts >>
#@+node:tom.20240928165801.1: ** << Built-in Layouts >>
# Define commands to create some standard layouts
#@+others
#@+node:tom.20240928195823.1: *3* legacy
# Recreate the layout called "legacy" in the Dynamic Window code.
LEGACY_LAYOUT = {
    'SPLITTERS':OrderedDict(
            (('outlineFrame', 'secondary_splitter'),
            ('logFrame', 'secondary_splitter'),
            ('bodyFrame', 'body-vr-splitter'),
            ('viewrendered_pane', 'body-vr-splitter'),
            ('secondary_splitter', 'main_splitter'),
            ('body-vr-splitter', 'main_splitter'))
        ),
    'ORIENTATIONS':{
        'body-vr-splitter':Orientation.Horizontal,
        'secondary_splitter':Orientation.Horizontal,
        'main_splitter':Orientation.Vertical
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
        vr = v.getVr()

    bvs = cache.find_widget('body-vr-splitter')
    bvs.addWidget(vr)
    c.doCommandByName('vr-show')
#@+node:tom.20240928170706.1: *3* horizontal-thirds
@g.command('layout-horizontal-thirds')
def horizontal_thirds(event: LeoKeyEvent) -> None:
    """Restore Leo's horizontal-thirds layout"""

    c = event.get('c')
    cache = c.frame.top.layout_cache
    cache.restoreFromLayout()

    ms = cache.find_widget('main_splitter')
    ss = cache.find_widget('secondary_splitter')
    lf = cache.find_widget('logFrame')
    bf = cache.find_widget('bodyFrame')
    of = cache.find_widget('outlineFrame')

    vr = cache.find_widget('viewrendered_pane')
    if vr is None:
        import leo.plugins.viewrendered as v
        vr = v.getVr()

    ms.setOrientation(Orientation.Vertical)
    ss.setOrientation(Orientation.Horizontal)

    ss.addWidget(of)
    ss.addWidget(lf)
    ms.addWidget(ss)
    ms.addWidget(bf)
    ms.addWidget(vr)

    # c.doCommandByName('vr-show')
    g.app.gui.equalize_splitter(ss)
    g.app.gui.equalize_splitter(ms)

    # Avoid flash each time VR pane is re-opened.
    QtCore.QTimer.singleShot(60, lambda: show_vr_pane(c, vr))

#@+node:tom.20240928171510.1: *3* big-tree
@g.command ('layout-big-tree')
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
    if not vr:
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
        widget.setParent(None)

    # Move widgets to target splitters
    of.setParent(ms)
    ss.setParent(ms)
    vr.setParent(ms)
    bf.setParent(ss)
    lf.setParent(ss)

    # set Orientations
    ms.setOrientation(Orientation.Vertical)
    ss.setOrientation(Orientation.Horizontal)

    # Re-parenting a widget to None hides it, so show it now
    for widget in (ss, of, lf, bf, vr):
        widget.show()
    c.doCommandByName('vr-show')

    # Set splitter sizes
    ms.setSizes([100_000] * len(ms.sizes()))
    ss.setSizes([100_000] * len(ss.sizes()))

    # Avoid flash each time VR pane is re-opened.
    QtCore.QTimer.singleShot(60, lambda: show_vr_pane(c, vr))

#@+node:tom.20240929101820.1: *3* render-focused
RENDERED_FOCUSED_LAYOUT = {
    'SPLITTERS':OrderedDict(
            (('outlineFrame', 'secondary_splitter'),
            ('bodyFrame', 'secondary_splitter'),
            ('logFrame', 'secondary_splitter'),
            ('viewrendered_pane', 'body-vr-splitter'),
            ('secondary_splitter', 'main_splitter'),
            ('body-vr-splitter', 'main_splitter'))
        ),
    'ORIENTATIONS':{
        'body-vr-splitter':Orientation.Horizontal,
        'secondary_splitter':Orientation.Vertical,
        'main_splitter':Orientation.Horizontal
    }
}

@g.command('layout-render-focused')
def render_focused(event: LeoKeyEvent) -> None:
    """Create Leo's render-focused layout::
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

    # Find or create VR widget
    vr = cache.find_widget('viewrendered_pane')
    if not vr:
        import leo.plugins.viewrendered as v
        vr = v.getVr()

    bvs = cache.find_widget('body-vr-splitter')
    bvs.addWidget(vr)

    QtCore.QTimer.singleShot(60, lambda: show_vr_pane(c, vr))
#@+node:tom.20240929104728.1: *3* vertical-thirds
VERTICAL_THIRDS_LAYOUT = {
    'SPLITTERS':OrderedDict(
            (('outlineFrame', 'secondary_splitter'),
            ('logFrame', 'secondary_splitter'),
            ('secondary_splitter', 'main_splitter'),
            ('bodyFrame', 'main_splitter'),
            ('viewrendered_pane', 'main_splitter'))
        ),
    'ORIENTATIONS':{
        'secondary_splitter':Orientation.Vertical,
        'main_splitter':Orientation.Horizontal
    }
}


@g.command('layout-vertical-thirds')
def vertical_thirds(event: LeoKeyEvent) -> None:
    """Create Leo's vertical-thirds layout::
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

    # Find or create VR widget
    vr = cache.find_widget('viewrendered_pane')
    if not vr:
        import leo.plugins.viewrendered as v
        vr = v.getVr()

    ms = cache.find_widget('main_splitter')
    ms.addWidget(vr)
    QtCore.QTimer.singleShot(60, lambda: show_vr_pane(c, vr))
#@+node:tom.20240929115043.1: *3* vertical-thirds2
VERTICAL_THIRDS2_LAYOUT = {
    'SPLITTERS':OrderedDict(
            (('logFrame', 'secondary_splitter'),
            ('bodyFrame', 'secondary_splitter'),
            ('outlineFrame', 'main_splitter'),
            ('viewrendered_pane', 'vr-splitter'),
            ('secondary_splitter', 'main_splitter'),
            ('vr-splitter', 'main_splitter')
            )
        ),
    'ORIENTATIONS':{
        'vr-splitter':Orientation.Vertical,
        'secondary_splitter':Orientation.Vertical,
        'main_splitter':Orientation.Horizontal
    }
}


@g.command('layout-vertical-thirds2')
def vertical_thirds2(event: LeoKeyEvent) -> None:
    """Create Leo's vertical-thirds2 layout::
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

    # Find or create VR widget
    vr = cache.find_widget('viewrendered_pane')
    if not vr:
        import leo.plugins.viewrendered as v
        vr = v.getVr()

    ms = cache.find_widget('vr-splitter')
    ms.addWidget(vr)
    QtCore.QTimer.singleShot(60, lambda: show_vr_pane(c, vr))
#@-others
#@-<< Built-in Layouts >>

class LayoutCacheWidget(QWidget):

    def __init__(self, c: Cmdr, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.c = c
        self.setObjectName(CACHENAME)
        self.created_splitter_dict = {}

    #@+<< find_widget() >>
    #@+node:tom.20240923194438.4: ** << find_widget() >>
    def find_widget_in_children(self, name, debug=False):
        log = [f'==== find_widget_in_children for: {name}']
        w = None
        for kid in self.children():
            if kid.objectName() == name:
                log.append(f'======== found it: {kid}')
                w = kid
        if debug:
            g.es('\n'.join(log))
        return w

    def find_widget(self, name, debug=False):
        log = ['\n']
        log.append('Running find_widget()')
        w = None
        # Weird - g.app.gui.find_widget_by_name() may not find object in ourself
        w = self.created_splitter_dict.get(name)
        log.append(f'---- self.created_splitter_dict.get(name) returned: {w}')

        w1 = self.find_widget_in_children(name, debug)
        log.append(f'---- self.find_widget_in_children(name) returned: {w1}')
        if w1 is not None and w is not None:
            w = w1

        w2 = g.app.gui.find_widget_by_name(self.c, name)
        log.append(f'----g.app.gui.find_widget_by_name(self.c, name) returned: {w2}')
        if (w1 is not None and w2 is not None) and w1 != w2:
            log.append(f'---- Inconsistent splitter objects: w1 != w2: {w1}, {w2}')
        elif w2 is not None and w is None:
            w = w2


        # if (w := self.created_splitter_dict.get(name)) is not None:
            # log.append(f'---- self.created_splitter_dict.get(name) returned: {w}')
        # elif (w := self.find_widget_in_children(name, debug)) is not None:
            # log.append(f'---- self.find_widget_in_children(name) returned: {w}')
        # elif (w := g.app.gui.find_widget_by_name(self.c, name)) is not None:
            # log.append(f'     g.app.gui.find_widget_by_name(self.c, name) returned: {w}')
        if debug:
            print('\n'.join(log))
        return w

    #@-<< find_widget() >>
    #@+<< find_splitter_by_name() >>
    #@+node:tom.20240923194438.5: ** << find_splitter_by_name() >>
    def find_splitter_by_name(self, name):
        foundit = False
        splitter = None
        splitter = self.find_widget(name)
        if splitter:
            foundit = True
        if not foundit:
            splitter = self.created_splitter_dict.get(name)
            if splitter:
                foundit = True
        if not foundit:
            for kid in self.children():
                if kid.objectName() == name:
                    foundit = True
                    splitter = kid
                    break
        return splitter
    #@-<< find_splitter_by_name() >>

    def restoreFromLayout(self, layout=FALLBACK_LAYOUT):
        #@+<< restoreFromLayout >>
        #@+node:tom.20240923194438.6: ** << restoreFromLayout >>
        #@+<< initialize data structures >>
        #@+node:tom.20240923194438.7: *3* << initialize data structures >>
        SPLITTERS = layout['SPLITTERS']
        ORIENTATIONS = layout['ORIENTATIONS']

        # Make unknown splitters
        for _, name in SPLITTERS.items():
            splitter = self.find_splitter_by_name(name)
            # g.es(f'self.find_splitter_by_name({name}) returned {splitter}')
            # g.es('    splitter is None:', splitter is None)
            if splitter is None:
                splitter = QtWidgets.QSplitter(self)
                splitter.setObjectName(name)
                self.created_splitter_dict[name] = splitter
                # g.es(f'Created splitter {splitter.objectName()=}  {splitter=}  {splitter.parent().objectName()=}')

        SPLITTER_DICT = OrderedDict()
        for name in ORIENTATIONS:
            splitter = self.find_splitter_by_name(name)
            if splitter is None:
                splitter = self.created_splitter_dict[name]
            SPLITTER_DICT[name] = splitter
        #@-<< initialize data structures >>
        #@+<< rehome body editor >>
        #@+node:tom.20240923194438.8: *3* << rehome body editor >>
        # In case the editor has been moved to e.g. a QTabWidget,
        # Move it back to its standard place.

        bsw = self.find_widget('bodyStackedWidget')
        editor = self.find_widget('bodyPage2')
        if bsw.indexOf(editor) == -1:
            bsw.insertWidget(0, editor)
        bsw.setCurrentIndex(0)
        #@-<< rehome body editor >>
        #@+<< clean up splitters >>
        #@+node:tom.20240923194438.9: *3* << clean up splitters >>
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
            # if widget.objectName() == 'layout_quad_splitter':
                # g.es('.... reparented from cache_list:', widget.objectName(), widget)

        for splitter in self.created_splitter_dict.values():
            if splitter not in self.children():
                splitter.setParent(self)
                # g.es('.... reparented from created_splitter_dict.values():',splitter.objectName(), splitter) 

        #@-<< clean up splitters >>
        #@+<< move widgets to targets >>
        #@+node:tom.20240923194438.10: *3* << move widgets to targets >>
        # Move all desired widgets into their home splitters
        # SPLITTERS is an OrderedDict so the widgets will
        # be inserted in the right order.
        for i, (name, target) in enumerate(SPLITTERS.items()):
            widget = self.find_widget(name)
            if not widget:
                widget = self.created_splitter_dict[name]
            dest = SPLITTER_DICT[target]
            dest.insertWidget(i, widget)
        #@-<< move widgets to targets >>
        #@+<< set default orientations >>
        #@+node:tom.20240923194438.11: *3* << set default orientations >>
        # SPLITTER_DICT: {'main_splitter':ms, ...}
        # DEFAULT_ORIENTATIONS:
        # {'main_splitter':Orientation.Horizontal...}

        for splitter_name, splitter in SPLITTER_DICT.items():
            orientation = ORIENTATIONS[splitter_name]
            splitter.setOrientation(orientation)
        #@-<< set default orientations >>
        #@+<< resize splitters >>
        #@+node:tom.20240923194438.12: *3* << resize splitters >>
        for splt in SPLITTER_DICT.values():
            g.app.gui.equalize_splitter(splt)
        #@-<< resize splitters >>
        editor.show()
        #@-<< restoreFromLayout >>


#@-leo
