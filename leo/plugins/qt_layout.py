#@+leo-ver=5-thin
#@+node:tom.20240923194438.1: * @file ../plugins/qt_layout.py
"""The basic machinery to support applying layouts of the main Leo panels."""

#@+<< qt_layout: imports & annotations >>
#@+node:tom.20240923194438.2: ** << qt_layout: imports & annotations >>
from __future__ import annotations

import textwrap
from collections import OrderedDict
from typing import Any, Dict, TYPE_CHECKING, Optional

from leo.core.leoQt import QtWidgets, Orientation, QtCore
from leo.core import leoGlobals as g

QSplitter = QtWidgets.QSplitter
QWidget = QtWidgets.QWidget

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent
    # from typing import TypeAlias  # Requires Python 3.12+
    Args = Any
    KWargs = Any
#@-<< qt_layout: imports & annotations >>
#@+<< qt_layout: declarations >>
#@+node:tom.20241009141008.1: ** << qt_layout: declarations >>
VR3_OBJ_NAME = 'viewrendered3_pane'
VR_OBJ_NAME = 'viewrendered_pane'
VRX_PLACEHOLDER_NAME = 'viewrenderedx_pane'

VR_MODULE_NAME = 'viewrendered.py'
VR3_MODULE_NAME = 'viewrendered3.py'

# Will contain {layout_name: layout_docstring}
LAYOUT_REGISTRY = {}
#@-<< qt_layout: declarations >>

#@+others
#@+node:ekr.20241008174359.1: ** Top-level functions: qt_layout.py
#@+node:ekr.20241008141246.1: *3* function: init (qt_layout.py)
def init() -> bool:
    """
    qt_layout is not a true plugin, but return True just in case.
    """
    return True
#@+node:ekr.20241008141353.1: *3* function: show_vr3_pane (qt_layout.py)
def show_vr3_pane(c: Cmdr, w: QWidget) -> None:
    w.setUpdatesEnabled(True)
    c.doCommandByName('vr3-show')
#@+node:tom.20241009141223.1: *3* function: is_module_loaded (qt_layout.py)
def is_module_loaded(module_name: str) -> bool:
    """Return True if the plugins controller has loaded the module.
    """
    controller = g.app.pluginsController
    return controller.isLoaded(module_name)
#@+node:tom.20241015161609.1: *3* decorator:  register_layout (qt_layout.py)
def register_layout(name: str):  # type: ignore
    def decorator(func):
        # Register the function's name and docstring in the dictionary
        LAYOUT_REGISTRY[name] = func.__doc__
        return func  # Ensure the original function is returned
    return decorator
#@+node:ekr.20241008174351.1: ** Layout commands
#@+at
# Read Me or Suffer
#
# The help-for-layouts and show-layout commands use these docstrings,
# so the following constraints apply to the following docstrings:
#
# 1. All docstrings must start with a newline.
# 2. Use a *single* ':', followed by a blank line
#    to denote the start of a layout diagram or
#    any other verbatim text.
# 3. All verbatim text must end with a blank line unless
#    the verbatim text ends the docstring.
#@@c
#@+node:tom.20240928171510.1: *3* command: 'layout-big-tree'
@g.command('layout-big-tree')
@register_layout('layout-big-tree')
def big_tree(event: LeoKeyEvent) -> None:
    """
    Create Leo's big-tree layout:

        ┌──────────────────┐
        │  outline         │
        ├──────────┬───────┤
        │  body    │  log  │
        ├──────────┴───────┤
        │  VR/VR3          │
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
#@+node:ekr.20241008174427.1: *3* command: 'layout-horizontal-thirds'
@g.command('layout-horizontal-thirds')
@register_layout('layout-horizontal-thirds')
def horizontal_thirds(event: LeoKeyEvent) -> None:
    """
    Create Leo's horizontal-thirds layout:

        ┌───────────┬───────┐
        │  outline  │  log  │
        ├───────────┴───────┤
        │  body             │
        ├───────────────────┤
        │  VR/VR3           │
        └───────────────────┘
    """
    c = event.get('c')
    dw = c.frame.top
    cache = dw.layout_cache
    cache.restoreFromLayout(HORIZONTAL_THIRDS_LAYOUT)
#@+node:ekr.20241008180407.1: *3* command: 'layout-legacy'
@g.command('layout-legacy')
@register_layout('layout-legacy')
def quadrants(event: LeoKeyEvent) -> None:
    """
    Create Leo's legacy layout:

        ┌───────────────┬───────────┐
        │   outline     │   log     │
        ├───────────────┼───────────┤
        │   body        │  VR/VR3   │
        └───────────────┴───────────┘
    """
    c = event.get('c')
    dw = c.frame.top
    cache = dw.layout_cache
    cache.restoreFromLayout(LEGACY_LAYOUT)
#@+node:ekr.20241008174427.2: *3* command: 'layout-render-focused'
@g.command('layout-render-focused')
@register_layout('layout-render-focused')
def render_focused(event: LeoKeyEvent) -> None:
    """
    Create Leo's render-focused layout:

        ┌───────────┬─────┐
        │ outline   │     │
        ├───────────┤     │
        │ body      │ VR/ │
        ├───────────┤ VR3 │
        │ log       │     │
        └───────────┴─────┘
    """
    c = event.get('c')
    dw = c.frame.top
    cache = dw.layout_cache
    cache.restoreFromLayout(RENDERED_FOCUSED_LAYOUT)
#@+node:tom.20240930101515.1: *3* command: 'layout-restore-to-setting'
@g.command('layout-restore-to-setting')
@register_layout('layout-restore-to-setting')
def restoreDefaultLayout(event: LeoKeyEvent) -> None:
    """
    Select the layout specified by the `@string qt-layout-name` setting in effect
    for this outline. Use the **legacy** layout if the user's setting is erroneous.
    """
    c = event.get('c')
    if not c:
        return
    event = g.app.gui.create_key_event(c)
    layout = c.config.getString('qt-layout-name') or 'legacy'
    if not layout.startswith('layout-'):
        layout = 'layout-' + layout.strip()
    if layout not in c.commandsDict:
        g.es_print(f"Unknown layout: {layout}; Using 'legacy' layout", color='red')
        layout = 'layout-legacy'
    c.commandsDict[layout](event)
#@+node:tom.20241005163724.1: *3* command: 'layout-swap-log-panel'
@g.command('layout-swap-log-panel')
@register_layout('layout-swap-log-panel')
def swapLogPanel(event: LeoKeyEvent) -> None:
    """
    Move the Log frame between main and secondary splitters.
    
    **Do not use this layout as the initial layout.**

    The effect of this command depends on the existing layout. For example,
    if the legacy layout is in effect, this command changes the layout
    from:

        ┌───────────┬──────┐
        │ outline   │ log  │
        ├───────────┼──────┤
        │ body      │VR/VR3│
        └───────────┴──────┘

    to:

        ┌──────────────────┐
        │  outline         │
        ├──────────┬───────┤
        │  body    │ VR/VR3│
        ├──────────┴───────┤
        │  log             │
        └──────────────────┘
    """
    c = event.get('c')
    if not c:
        return
    gui = g.app.gui

    ms = gui.find_widget_by_name(c, 'main_splitter')  # type: ignore
    ss = gui.find_widget_by_name(c, 'secondary_splitter')  # type: ignore
    lf = gui.find_widget_by_name(c, 'logFrame')  # type: ignore

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
        gui.equalize_splitter(target)  # type: ignore
#@+node:ekr.20241008175137.1: *3* command: 'layout-vertical-thirds'
@g.command('layout-vertical-thirds')
@register_layout('layout-vertical-thirds')
def vertical_thirds(event: LeoKeyEvent) -> None:
    """
    Create Leo's vertical-thirds layout:

        ┌───────────┬────────┬────────┐
        │  outline  │        │        │
        ├───────────┤  body  │ VR/VR3 │
        │  log      │        │        │
        └───────────┴────────┴────────┘
    """
    c = event.get('c')
    dw = c.frame.top
    cache = dw.layout_cache
    cache.restoreFromLayout(VERTICAL_THIRDS_LAYOUT)

#@+node:ekr.20241008175303.1: *3* command: 'layout-vertical-thirds2'
@g.command('layout-vertical-thirds2')
@register_layout('layout-vertical-thirds2')
def vertical_thirds2(event: LeoKeyEvent) -> None:
    """
    Create Leo's vertical-thirds2 layout:

        ┌───────────┬───────┬─────────┐
        │           │  log  │         │
        │  outline  ├───────┤ VR/VR3  │
        │           │  body │         │
        └───────────┴───────┴─────────┘
    """
    c = event.get('c')
    dw = c.frame.top
    cache = dw.layout_cache
    cache.restoreFromLayout(VERTICAL_THIRDS2_LAYOUT)
#@+node:tom.20241022170042.1: *3* command: 'show-layouts'
@g.command('layout-show-layouts')
@g.command('show-layouts')
def showLayouts(event) -> None:
    """Show all layout diagrams in the Log Frame's `layouts` tab."""
    c = event.get('c')
    if not c:
        return

    dw = c.frame.top
    cache = dw.layout_cache
    layouts = cache.layout_registry
    listing = []
    for name, docstr in layouts.items():
        # This trick is *not* a bug in Leo!
        doc_s = textwrap.dedent(docstr.rstrip()).strip()
        listing.append(f'{name}\n' + '=' * len(name) + f'\n\n{doc_s}\n\n')
    listing_s = ''.join(listing)
    g.es(listing_s, tabName='layouts')
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
            (VRX_PLACEHOLDER_NAME, 'main_splitter'))
        ),
    'ORIENTATIONS': {
        'secondary_splitter': Orientation.Horizontal,
        'main_splitter': Orientation.Vertical
    }
}
#@+node:tom.20240930164155.1: *3* LEGACY_LAYOUT
LEGACY_LAYOUT = {
    'SPLITTERS': OrderedDict(
        (
            ('bodyFrame', 'secondary_splitter'),
            (VRX_PLACEHOLDER_NAME, 'secondary_splitter'),
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
            (VRX_PLACEHOLDER_NAME, 'body-vr-splitter'),
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
        (VRX_PLACEHOLDER_NAME, 'vr-splitter'),
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
            (VRX_PLACEHOLDER_NAME, 'main_splitter'))
        ),
    'ORIENTATIONS': {
        'secondary_splitter': Orientation.Vertical,
        'main_splitter': Orientation.Horizontal
    }
}
#@+node:tom.20240930095459.1: ** class LayoutCacheWidget
class LayoutCacheWidget(QWidget):
    """
    Manage layouts, which may be defined by methods or by
    a layout data structure such as the following:0

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

    def __init__(self, c: Cmdr, parent: Optional[QWidget]) -> None:
        super().__init__(parent)
        self.c = c
        self.setObjectName('leo-layout-cache')

        # maps splitter objectNames to their splitter object.
        self.created_splitter_dict: Dict[str, QWidget] = {}
        self.layout_registry = LAYOUT_REGISTRY

    #@+others
    #@+node:ekr.20241027142532.1: *3* LayoutCasheWidget: contract_*
    #@+node:ekr.20241027124630.1: *4* LCW.contract_body
    def contract_body(self):
        """Contract the body pane"""
        self.contract_pane(self.c.frame.body.widget)
    #@+node:ekr.20241027125414.1: *4* LCW.contract_log
    def contract_log(self):
        """Contract the log pane"""
        self.contract_pane(self.c.frame.log.logWidget)
    #@+node:ekr.20241027125415.1: *4* LCW.contract_outline
    def contract_outline(self):
        """Contract the outline pane"""
        self.contract_pane(self.c.frame.tree.treeWidget)
    #@+node:ekr.20241027141341.1: *4* LCW.contract_vr
    def contract_vr(self):
        """Contract the VR pane if VR is running"""
        c = self.c
        if is_module_loaded(VR_MODULE_NAME):
            vr = getattr(c, 'vr', None)
            self.expand_pane(vr)
        else:
            g.es_print('VR is not running', color='blue')
    #@+node:ekr.20241027141411.1: *4* LCW.contract_vr3
    def contract_vr3(self):
        """Contract the VR3 pane if VR3 is running"""
        c = self.c
        if is_module_loaded(VR3_MODULE_NAME):
            from leo.plugins.viewrendered3 import controllers
            vr3 = controllers.get(c.hash())
            self.contract_pane(vr3)
        else:
            g.es_print('VR3 is not running', color='blue')
    #@+node:ekr.20241027142605.1: *3* LayoutCacheWidget: expand_*
    #@+node:ekr.20241027124500.1: *4* LCW.expand_body
    def expand_body(self):
        """Expand the body pane"""
        self.expand_pane(self.c.frame.body.widget)
    #@+node:ekr.20241027125500.1: *4* LCW.expand_log
    def expand_log(self):
        """Expand the log pane"""
        self.expand_pane(self.c.frame.log.logWidget)
    #@+node:ekr.20241027124703.1: *4* LCW.expand_outline
    def expand_outline(self):
        """Expand the outline pane."""
        self.expand_pane(self.c.frame.tree.treeWidget)
    #@+node:ekr.20241027141425.1: *4* LCW.expand_vr
    def expand_vr(self):
        """Expand the VR pane if VR is running"""
        c = self.c
        if is_module_loaded(VR_MODULE_NAME):
            vr = getattr(c, 'vr', None)
            self.expand_pane(vr)
        else:
            g.es_print('VR is not running', color='blue')
    #@+node:ekr.20241027141446.1: *4* LCW.expand_vr3
    def expand_vr3(self):
        """Expand the VR3 pane if VR3 is running"""
        c = self.c
        if is_module_loaded(VR3_MODULE_NAME):
            from leo.plugins.viewrendered3 import controllers
            vr3 = controllers.get(c.hash())
            self.expand_pane(vr3)
        else:
            g.es_print('VR3 is not running', color='blue')
    #@+node:ekr.20241027162525.1: *3* LayoutCacheWidget: utils
    #@+node:ekr.20241027161121.1: *4* LCW.contract_pane
    def contract_pane(self, widget: Any) -> None:
        """Contract the pane containing the given widget."""
        self.resize_pane(widget, delta=-40)

    #@+node:ekr.20241028045021.1: *4* LCW.expand_pane
    def expand_pane(self, widget: Any) -> None:
        """Expand the pane containing the given widget."""
        self.resize_pane(widget, delta=40)
    #@+node:tom.20240923194438.5: *4* LCW.find_splitter_by_name
    def find_splitter_by_name(self, name: str) -> Optional[QSplitter]:
        """Return the splitter with the given objectName."""

        def is_splitter(obj: Any) -> bool:
            return obj is not None and isinstance(obj, QSplitter)

        splitter = self.find_widget(name)
        if is_splitter(splitter):
            return splitter  # type:ignore  # We've just checked the type.
        splitter = self.created_splitter_dict.get(name, None)
        if is_splitter(splitter):
            return splitter  # type:ignore  # We've just checked the type.
        for child in self.children():
            if child.objectName() == name and is_splitter(child):
                return child  # type:ignore  # We've just checked the type.
        return None
    #@+node:ekr.20241008180818.1: *4* LCW.find_widget
    def find_widget(self, name: str) -> QWidget:
        """Return a widget given it objectName."""
        return g.app.gui.find_widget_by_name(self.c, name)
    #@+node:tom.20240923194438.4: *4* LCW.find_widget_in_children
    def find_widget_in_children(self, name: str) -> Optional[QWidget]:
        """Return a child widget with the given objectName.
        """
        w: QWidget = None
        for kid in self.children():
            if kid.objectName() == name:
                w = kid  # type: ignore [assignment]
        return w
    #@+node:ekr.20241027181931.1: *4* LCW.resize_widget
    def resize_pane(self, widget: QWidget, delta: int) -> None:
        """Resize the pane containing the given widget."""
        c = self.c
        splitter, direct_child = g.app.gui.find_parent_splitter(widget)
        if not splitter:
            g.trace(f"Oops! no splitter for name: {widget.objectName()!r}")
            return
        try:
            index = splitter.indexOf(direct_child)
            sizes = splitter.sizes()
            widget_size = sizes[index]
        except Exception:
            g.trace(f"Oops! {widget} not in: {splitter!r}")
            g.es_exception()
            return
        if index == -1:
            g.trace(f"Oops! direct child: {direct_child!r} not in {splitter}")
            return
        if widget_size == 0:
            # The pane is invisible.
            return
        if len(sizes) < 2:
            # There are no other widgets in the splitter.
            return
        # Look for another *visible* widget.
        for other_index, size in enumerate(sizes):
            if other_index != index and size > 0:
                break
        else:
            # There is no other visible pane.
            return
        sizes[index] += delta
        sizes[other_index] -= delta
        splitter.setSizes(sizes)
    #@+node:tom.20240923194438.6: *4* LCW.restoreFromLayout
    def restoreFromLayout(self, layout: Dict = None) -> None:
        if layout is None:
            layout = FALLBACK_LAYOUT
        #@+<< initialize data structures >>
        #@+node:tom.20240923194438.7: *5* << initialize data structures >> restoreFromLayout
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
            splitter: QWidget = self.find_splitter_by_name(name)
            if splitter is None:
                splitter = QSplitter(self)
                splitter.setObjectName(name)
                self.created_splitter_dict[name] = splitter

        SPLITTER_DICT: Dict[str, Any] = OrderedDict()
        for name in ORIENTATIONS:
            splitter = self.find_splitter_by_name(name)
            if splitter is not None and SPLITTER_DICT.get(name, None) is None:
                SPLITTER_DICT[name] = splitter

        #@-<< initialize data structures >>
        #@+<< rehome body editor >>
        #@+node:tom.20240923194438.8: *5* << rehome body editor >> restoreFromLayout
        # In case the editor has been moved to e.g. a QTabWidget,
        # Move it back to its standard place.

        bsw: QWidget = self.find_widget('bodyStackedWidget')
        editor: QWidget = self.find_widget('bodyPage2')
        if bsw.indexOf(editor) == -1:
            bsw.insertWidget(0, editor)
        bsw.setCurrentIndex(0)
        #@-<< rehome body editor >>
        #@+<< clean up splitters >>
        #@+node:tom.20240923194438.9: *5* << clean up splitters >> restoreFromLayout
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
        #@+node:tom.20240923194438.11: *5* << set default orientations >> restoreFromLayout
        # SPLITTER_DICT: {'main_splitter':ms, ...}
        # DEFAULT_ORIENTATIONS:
        # {'main_splitter':Orientation.Horizontal...}

        for splitter_name, splitter in SPLITTER_DICT.items():
            orientation = ORIENTATIONS[splitter_name]
            splitter.setOrientation(orientation)
        #@-<< set default orientations >>
        #@+<< move widgets to targets >>
        #@+node:tom.20240923194438.10: *5* << move widgets to targets >> restoreFromLayout
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
        #@+node:tom.20240923194438.12: *5* << resize splitters >> restoreFromLayout
        for splt in SPLITTER_DICT.values():
            g.app.gui.equalize_splitter(splt)  # type: ignore[attr-defined]
        #@-<< resize splitters >>
        editor.show()
    #@-others

#@-others

#@-leo
