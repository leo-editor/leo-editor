#@+leo-ver=5-thin
#@+node:ekr.20120419093256.10048: * @file ../plugins/free_layout.py
#@+<< free_layout docstring >>
#@+node:ekr.20110319161401.14467: ** << free_layout docstring >>
"""
Free layout
===========

Adds flexible panel layout through context menus on the handles between panels.

Uses NestedSplitter, a more intelligent QSplitter, from leo.plugins.nested_splitter

Requires Qt.

Commands (bindable with @settings-->@keys-->@shortcuts):

free-layout-load
    Open context menu for loading a different layout,
    convenient keyboard shortcut target.
free-layout-restore
    Use the layout this outline had when it was opened.
free-layout-zoom
    Zoom or unzoom the current pane

"""
#@-<< free_layout docstring >>
# Written by Terry Brown.
#@+<< free_layout imports >>
#@+node:tbrown.20110203111907.5520: ** << free_layout imports >>
from __future__ import annotations
import json
from typing import Any, Optional, Union, TYPE_CHECKING
from leo.core import leoGlobals as g
#
# Qt imports. May fail from the bridge.
try:  # #1973
    from leo.core.leoQt import QtWidgets
    from leo.core.leoQt import MouseButton
    from leo.plugins.nested_splitter import NestedSplitter  # NestedSplitterChoice
except Exception:
    QtWidgets = None
    MouseButton = None  # type:ignore
    NestedSplitter = None  # type:ignore

# Do not call g.assertUi('qt') here. It's too early in the load process.
#@-<< free_layout imports >>
#@+<< free_layout annotations >>
#@+node:ekr.20220828125201.1: ** << free_layout annotations >>
if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent
    from leo.core.leoNodes import Position

    QSplitter = QtWidgets.QSplitter
    QWidget = QtWidgets.QWidget

Wrapper = Any
#@-<< free_layout annotations >>
#@+others
#@+node:tbrown.20110203111907.5521: ** free_layout:init
def init() -> bool:
    """Return True if the free_layout plugin can be loaded."""
    return bool(NestedSplitter and g.app.gui.guiName() == "qt")
#@+node:ekr.20110318080425.14389: ** class FreeLayoutController
class FreeLayoutController:

    #@+<< FreeLayoutController docstring >>
    #@+node:ekr.20201013042712.1: *3* << FreeLayoutController docstring >>
    """Glue between Leo and the NestedSplitter gui widget.  All Leo aware
    code should be in here, none in NestedSplitter.

    *ALSO* implements the provider interface for NestedSplitter, in
    ns_provides, ns_provide, ns_context, ns_do_context, which
    NestedSplitter uses as callbacks to populate splitter-handle context-menu
    and the empty pane Action button menu:

    see nested_splitter.py-->class%20NestedSplitter%20(QSplitter)-->register_provider

    ns_provides
      tell NestedSplitter which Action button items we can provide
    ns_provide
      provide the advertised service when an Action button item we
      advertised is selected
    ns_context
      tell NestedSplitter which splitter-handle context-menu items
      we can provide
    ns_do_context
      provide the advertised service when a splitter-handle context-menu
      item we advertised is selected
    """
    #@-<< FreeLayoutController docstring >>
    #@+<< define default_layout >>
    #@+node:ekr.20201013042741.1: *3* << define default_layout >>
    default_layout = {
        'content': [
            {
                'content': [
                    '_leo_pane:outlineFrame',
                    '_leo_pane:logFrame',
                ],
                'orientation': 1,
                'sizes': [509, 275],
            },
            '_leo_pane:bodyFrame',
        ],
        'orientation': 2,
        'sizes': [216, 216],
    }
    #@-<< define default_layout >>

    #@+others
    #@+node:ekr.20110318080425.14390: *3*  flc.ctor
    def __init__(self, c: Cmdr) -> None:
        """Ctor for FreeLayoutController class."""
        self.c = c
        g.registerHandler('after-create-leo-frame', self.init)
        # Plugins must be loaded first to provide their widgets in panels etc.
        g.registerHandler('after-create-leo-frame2', self.loadLayouts)
    #@+node:tbrown.20110203111907.5522: *3*  flc.init
    def init(self, tag: str, keys: Any) -> None:
        """Attach to an outline and

        - add tags to widgets to indicate that they're essential
          (tree, body, log-window-tabs) and

        - tag the log-window-tabs widget as the place to put widgets
          from free-layout panes which are closed

        - register this FreeLayoutController as a provider of menu items
          for NestedSplitter
        """
        c = self.c
        if not NestedSplitter:
            return
        if c != keys.get('c'):
            return
        # Careful: we could be unit testing.
        splitter = self.get_top_splitter()  # A NestedSplitter.
        if not splitter:
            return
        # by default NestedSplitter's context menus are disabled, needed
        # once to globally enable them
        NestedSplitter.enabled = True
        # when NestedSplitter disposes of children, it will either close
        # them, or move them to another designated widget.  Here we set
        # up two designated widgets
        logTabWidget = splitter.findChild(QtWidgets.QWidget, "logTabWidget")
        splitter.root.holders['_is_from_tab'] = logTabWidget
        splitter.root.holders['_is_permanent'] = 'TOP'
        # allow body and tree widgets to be "removed" to tabs on the log tab panel
        bodyWidget = splitter.findChild(QtWidgets.QFrame, "bodyFrame")
        bodyWidget._is_from_tab = "Body"
        treeWidget = splitter.findChild(QtWidgets.QFrame, "outlineFrame")
        treeWidget._is_from_tab = "Tree"
        # also the other tabs will have _is_from_tab set on them by the
        # offer_tabs menu callback above
        # if the log tab panel is removed, move it back to the top splitter
        logWidget = splitter.findChild(QtWidgets.QFrame, "logFrame")
        logWidget._is_permanent = True
        # tag core Leo components (see ns_provides)
        splitter.findChild(
            QtWidgets.QWidget, "outlineFrame")._ns_id = '_leo_pane:outlineFrame'
        splitter.findChild(QtWidgets.QWidget, "logFrame")._ns_id = '_leo_pane:logFrame'
        splitter.findChild(QtWidgets.QWidget, "bodyFrame")._ns_id = '_leo_pane:bodyFrame'
        splitter.register_provider(self)
        splitter.splitterClicked_connect(self.splitter_clicked)
    #@+node:tbrown.20120119080604.22982: *3* flc.embed
    def embed(self) -> None:
        """called from ns_do_context - embed layout in outline's
        @settings, an alternative to the Load/Save named layout system
        """
        # Careful: we could be unit testing.
        top_splitter = self.get_top_splitter()
        if not top_splitter:
            return
        c = self.c
        layout = top_splitter.get_saveable_layout()
        nd = g.findNodeAnywhere(c, "@data free-layout-layout")
        if not nd:
            settings: Position
            settings = g.findNodeAnywhere(c, "@settings")
            if not settings:
                settings = c.rootPosition().insertAfter()
                settings.h = "@settings"
            nd = settings.insertAsNthChild(0)
        nd.h = "@data free-layout-layout"
        nd.b = json.dumps(layout, indent=4)
        nd = nd.parent()
        if not nd or nd.h != "@settings":
            g.es("WARNING: @data free-layout-layout node is not under an active @settings node")
        c.redraw()
    #@+node:ekr.20160424035257.1: *3* flc.get_main_splitter
    def get_main_splitter(self, w: Wrapper = None) -> Optional[Wrapper]:
        """
        Return the splitter the main splitter, or None. The main splitter is a
        NestedSplitter that contains the body pane.

        Yes, the user could delete the secondary splitter but if so, there is
        not much we can do here.
        """
        top = self.get_top_splitter()
        if top:
            w = top.find_child(QtWidgets.QWidget, "bodyFrame")
            while w:
                if isinstance(w, NestedSplitter):
                    return w
                w = w.parent()
        return None
    #@+node:ekr.20160424035254.1: *3* flc.get_secondary_splitter
    def get_secondary_splitter(self) -> Optional[Wrapper]:
        """
        Return the secondary splitter, if it exists. The secondary splitter
        contains the outline pane.

        Yes, the user could delete the outline pane, but if so, there is not
        much we can do here.
        """
        top = self.get_top_splitter()
        if top:
            w = top.find_child(QtWidgets.QWidget, 'outlineFrame')
            while w:
                if isinstance(w, NestedSplitter):
                    return w
                w = w.parent()
        return None
    #@+node:tbrown.20110621120042.22914: *3* flc.get_top_splitter
    def get_top_splitter(self) -> Optional[Wrapper]:
        """Return the top splitter of c.frame.top."""
        # Careful: we could be unit testing.
        f = self.c.frame
        if hasattr(f, 'top') and f.top:
            child = f.top.findChild(NestedSplitter)
            return child and child.top()
        return None
    #@+node:ekr.20120419095424.9927: *3* flc.loadLayouts (sets wrap=True)
    def loadLayouts(self, tag: str, keys: Any, reloading: bool = False) -> None:
        """loadLayouts - Load the outline's layout

        :Parameters:
        - `tag`: from hook event
        - `keys`: from hook event
        - `reloading`: True if this is not the initial load, see below

        When called from the `after-create-leo-frame2` hook this defaults
        to False.  When called from the `restore-layout` command, this is set
        True, and the layout the outline had *when first loaded* is restored.
        Useful if you want to temporarily switch to a different layout and then
        back, without having to remember the original layouts name.
        """
        trace = 'layouts' in g.app.debug
        c = self.c
        if not (g.app and g.app.db):
            return  # Can happen when running from the Leo bridge.
        if c != keys.get('c'):
            return
        d = g.app.db.get('ns_layouts') or {}
        if trace:
            g.trace(tag)
            g.printObj(keys, tag="keys")
        layout = c.config.getData("free-layout-layout")
        if layout:
            layout = json.loads('\n'.join(layout))
        name = c.db.get('_ns_layout')
        if name:
            if reloading:
                name = c.free_layout.original_layout
                c.db['_ns_layout'] = name
            else:
                c.free_layout.original_layout = name
            if layout:
                g.es("NOTE: embedded layout in @settings/@data free-layout-layout "
                     "overrides saved layout " + name)
            else:
                layout = d.get(name)
        # EKR: Create commands that will load each layout.
        if d:
            for name in sorted(d.keys()):

                def func(event: LeoKeyEvent) -> None:
                    layout = d.get(name)
                    if layout:
                        c.free_layout.get_top_splitter().load_layout(c, layout)
                    else:
                        g.trace('no layout', name)

                name_s = name.strip().lower().replace(' ', '-')
                commandName = f"free-layout-load-{name_s}"
                c.k.registerCommand(commandName, func)
        # Careful: we could be unit testing or in the Leo bridge.
        if layout:
            splitter = c.free_layout.get_top_splitter()
            if splitter:
                splitter.load_layout(c, layout)
    #@+node:tbrown.20110628083641.11730: *3* flc.ns_context
    def ns_context(self) -> list[tuple[str, str]]:
        ans: list[Any] = [
            ('Embed layout', '_fl_embed_layout'),
            ('Save layout', '_fl_save_layout'),
        ]
        d = g.app.db.get('ns_layouts', {})
        if d:
            ans.append({'Load layout': [(k, '_fl_load_layout:' + k) for k in d]})
            ans.append({'Delete layout': [(k, '_fl_delete_layout:' + k) for k in d]})
            ans.append(('Forget layout', '_fl_forget_layout:'))
            ans.append(('Restore initial layout', '_fl_restore_layout:'))
        ans.append(('Restore default layout', '_fl_restore_default:'))
        ans.append(('Help for this menu', '_fl_help:'))
        return ans
    #@+node:tbrown.20110628083641.11732: *3* flc.ns_do_context
    def ns_do_context(self, id_: QWidget, splitter: QSplitter, index: int) -> bool:

        c = self.c
        if id_.startswith('_fl_embed_layout'):
            self.embed()
            return True
        if id_.startswith('_fl_restore_default'):
            self.get_top_splitter().load_layout(c, layout=self.default_layout)
        if id_.startswith('_fl_help'):
            self.c.putHelpFor(__doc__)
            # g.handleUrl("https://leo-editor.github.io/leo-editor/")
            return True
        if id_ == '_fl_save_layout':
            if self.c.config.getData("free-layout-layout"):
                g.es("WARNING: embedded layout in")
                g.es("@settings/@data free-layout-layout")
                g.es("will override saved layout")
            layout = self.get_top_splitter().get_saveable_layout()
            name = g.app.gui.runAskOkCancelStringDialog(self.c,
                title="Save layout",
                message="Name for layout?",
            )
            if name:
                self.c.db['_ns_layout'] = name
                d = g.app.db.get('ns_layouts', {})
                d[name] = layout
                # make sure g.app.db's __set_item__ is hit so it knows to save
                g.app.db['ns_layouts'] = d
            return True
        if id_.startswith('_fl_load_layout:'):
            if self.c.config.getData("free-layout-layout"):
                g.es("WARNING: embedded layout in")
                g.es("@settings/@data free-layout-layout")
                g.es("will override saved layout")
            name = id_.split(':', 1)[1]
            self.c.db['_ns_layout'] = name
            layout = g.app.db['ns_layouts'][name]
            self.get_top_splitter().load_layout(c, layout)
            return True
        if id_.startswith('_fl_delete_layout:'):
            name = id_.split(':', 1)[1]
            if ('yes' == g.app.gui.runAskYesNoCancelDialog(c,
                "Really delete Layout?",
                f"Really permanently delete the layout '{name}'?")
            ):
                d = g.app.db.get('ns_layouts', {})
                del d[name]
                # make sure g.app.db's __set_item__ is hit so it knows to save
                g.app.db['ns_layouts'] = d
                if '_ns_layout' in self.c.db:
                    del self.c.db['_ns_layout']
            return True
        if id_.startswith('_fl_forget_layout:'):
            if '_ns_layout' in self.c.db:
                del self.c.db['_ns_layout']
            return True
        if id_.startswith('_fl_restore_layout:'):
            self.loadLayouts("reload", {'c': self.c}, reloading=True)
            return True
        return False
    #@+node:tbrown.20110628083641.11724: *3* flc.ns_provide
    def ns_provide(self, id_: str) -> Union[str, Wrapper, None]:
        if id_.startswith('_leo_tab:'):
            id_ = id_.split(':', 1)[1]
            top = self.get_top_splitter()
            logTabWidget = top.find_child(QtWidgets.QWidget, "logTabWidget")
            for n in range(logTabWidget.count()):
                if logTabWidget.tabText(n) == id_:
                    w = logTabWidget.widget(n)
                    w.setHidden(False)
                    w._is_from_tab = logTabWidget.tabText(n)
                    w.setMinimumSize(20, 20)
                    return w
            # didn't find it, maybe it's already in a splitter
            return 'USE_EXISTING'
        if id_.startswith('_leo_pane:'):
            id_ = id_.split(':', 1)[1]
            w = self.get_top_splitter().find_child(QtWidgets.QWidget, id_)
            if w:
                w.setHidden(False)  # may be from Tab holder
                w.setMinimumSize(20, 20)
            return w
        return None
    #@+node:tbrown.20110627201141.11745: *3* flc.ns_provides
    def ns_provides(self) -> list[tuple[str, str]]:
        ans: list[tuple[str, str]] = []
        # list of things in tab widget
        logTabWidget = self.get_top_splitter(
            ).find_child(QtWidgets.QWidget, "logTabWidget")
        for n in range(logTabWidget.count()):
            text = str(logTabWidget.tabText(n))
            if text in ('Body', 'Tree'):
                continue  # handled below
            if text == 'Log':
                # if Leo can't find Log in tab pane, it creates another
                continue
            ans.append((text, '_leo_tab:' + text))
        ans.append(('Tree', '_leo_pane:outlineFrame'))
        ans.append(('Body', '_leo_pane:bodyFrame'))
        ans.append(('Tab pane', '_leo_pane:logFrame'))
        return ans
    #@+node:tbnorth.20160510122413.1: *3* flc.splitter_clicked
    def splitter_clicked(self,
        splitter: Wrapper,
        handle: Wrapper,
        event: LeoKeyEvent,
        release: str,
        double: bool,
    ) -> None:
        """
        splitter_clicked - middle click release will zoom adjacent
        body / tree panes

        :param NestedSplitter splitter: splitter containing clicked handle
        :param NestedSplitterHandle handle: clicked handle
        :param QMouseEvent event: mouse event for click
        :param bool release: was it a Press or Release event
        :param bool double: was it a double click event
        """
        if not release or event.button() != MouseButton.MiddleButton:
            return
        if splitter.root.zoomed:  # unzoom if *any* handle clicked
            splitter.zoom_toggle()
            return
        before = splitter.widget(splitter.indexOf(handle) - 1)
        after = splitter.widget(splitter.indexOf(handle))
        for pane in before, after:
            if pane.objectName() == 'bodyFrame':
                pane.setFocus()
                splitter.zoom_toggle()
                return
            if pane.objectName() == 'outlineFrame':
                pane.setFocus()
                splitter.zoom_toggle(local=True)
                return
    #@-others
#@+node:ekr.20160416065221.1: ** commands: free_layout.py
#@+node:tbrown.20140524112944.32658: *3* @g.command free-layout-context-menu
@g.command('free-layout-context-menu')
def free_layout_context_menu(event: LeoKeyEvent) -> None:
    """
    Open free layout's context menu, using the first divider of the top
    splitter for context.
    """
    c = event.get('c')
    splitter = c.free_layout.get_top_splitter()
    handle = splitter.handle(1)
    handle.splitter_menu(handle.rect().topLeft())
#@+node:tbrown.20130403081644.25265: *3* @g.command free-layout-restore
@g.command('free-layout-restore')
def free_layout_restore(event: LeoKeyEvent) -> None:
    """
    Restore layout outline had when it was loaded.
    """
    c = event.get('c')
    c.free_layout.loadLayouts('reload', {'c': c}, reloading=True)
#@+node:tbrown.20131111194858.29876: *3* @g.command free-layout-load
@g.command('free-layout-load')
def free_layout_load(event: LeoKeyEvent) -> None:
    """Load layout from menu."""
    c = event.get('c')
    if not c:
        return
    d = g.app.db.get('ns_layouts', {})
    menu = QtWidgets.QMenu(c.frame.top)
    for k in d:
        menu.addAction(k)
    pos = c.frame.top.window().frameGeometry().center()
    action = menu.exec(pos)
    if action is None:
        return
    name = str(action.text())
    c.db['_ns_layout'] = name
    # layout = g.app.db['ns_layouts'][name]
    layouts = g.app.db.get('ns_layouts', {})
    layout = layouts.get(name)
    if layout:
        c.free_layout.get_top_splitter().load_layout(c, layout)
#@+node:tbrown.20140522153032.32658: *3* @g.command free-layout-zoom
@g.command('free-layout-zoom')
def free_layout_zoom(event: LeoKeyEvent) -> None:
    """(un)zoom the current pane."""
    c = event.get('c')
    c.free_layout.get_top_splitter().zoom_toggle()
#@+node:ekr.20160327060009.1: *3* free_layout:register_provider
def register_provider(c: Cmdr, provider_instance: Any) -> None:
    """Register the provider instance with the top splitter."""
    # Careful: c.free_layout may not exist during unit testing.
    if c and hasattr(c, 'free_layout'):
        splitter = c.free_layout.get_top_splitter()
        if splitter:
            splitter.register_provider(provider_instance)
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
