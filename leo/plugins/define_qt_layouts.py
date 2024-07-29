#@+leo-ver=5-thin
#@+node:ekr.20240729034257.1: * @file ../plugins/define_qt_layouts.py
"""
define_qt_layouts.py: define several qt layouts.
"""

from leo.core import leoGlobals as g
from leo.core.leoQt import Orientation  ### QtWidgets

g.assertUi('qt')

def init():
    """Return True if the plugin has loaded successfully."""
    if g.unitTesting:
        return False
    g.registerHandler('after-create-layout-dict', update_layout)
    return True

def update_layout(tags, event):
    """Update dw.layout_dict with a new layout."""
    # Note: c.frame.top does not exist yet.
    c = event.get('c')
    dw = event.get('dw')
    layout_dict = event.get('layout_dict')
    assert c and dw and layout_dict
    #@+<< create horizontal-thirds layout >>
    #@+node:ekr.20240729040239.1: ** << create horizontal-thirds layout >>
    def create_horizontal_thirds_layout(dw=dw):

        """Create the "horizontal-thirds" layout:
            ┌────────────────┬──────────────┐
            │   outline      │      log     │
            ├────────────────┴──────────────┤
            │   body                        │
            ├───────────────────────────────┤
            │   vr                          │
            └───────────────────────────────┘
        https://gist.github.com/gatesphere/82c9f67ca7b65d09e85208e0b2f7eca1#file-horizontal-thirds
        """
        main_splitter, secondary_splitter = dw.createMainLayout(dw.centralwidget)
        dw.main_splitter, dw.secondary_splitter = main_splitter, secondary_splitter
        dw.createOutlinePane(secondary_splitter)
        dw.createLogPane(secondary_splitter)
        dw.createBodyPane(main_splitter)
        dw.vr_parent_frame = main_splitter
        return main_splitter, secondary_splitter
    #@-<< create horizontal-thirds layout >>
    #@+<< create render-focused layout >>
    #@+node:ekr.20240729045515.1: ** << create render-focused layout >>
    def create_render_focused_layout(dw=dw):
        """Create the "render-focused" layout:

            ┌────────────────┬──────────┐
            │    outline     │          │
            ├────────────────┤          │
            │     body       │    vr    │
            ├────────────────┤          │
            │     log        │          │
            └────────────────┴──────────┘
        
        https://gist.github.com/gatesphere/82c9f67ca7b65d09e85208e0b2f7eca1#file-render-focused
        """
        parent = dw.centralwidget
        #### main_splitter, secondary_splitter = dw.createMainLayout(dw.centralwidget)
        
        main_splitter = dw.createMainSplitter(parent)
        secondary_splitter = dw.createSecondarySplitter(main_splitter)

        dw.verticalLayout = dw.createVLayout(parent, 'mainVLayout', margin=3)
        dw.set_widget_size_policy(secondary_splitter)
        dw.verticalLayout.addWidget(main_splitter)

        dw.main_splitter, dw.secondary_splitter = main_splitter, secondary_splitter
        main_splitter.setOrientation(Orientation.Horizontal)
        secondary_splitter.setOrientation(Orientation.Vertical)
        dw.createOutlinePane(main_splitter)
        dw.createLogPane(main_splitter)
        dw.createBodyPane(main_splitter)
        dw.vr_parent_frame = secondary_splitter

        return main_splitter, secondary_splitter
    #@-<< create render-focused layout >>
    #@+<< create vertical-thirds layout >>
    #@+node:ekr.20240729042637.1: ** << create vertical-thirds layout >>
    def create_vertical_thirds_layout(c=c, dw=dw):

        """Define the "vertical-thirds" layout:
            
            ┌────────────┬─────────┬────────────┐
            │            │         │            │
            │   outline  │         │            │
            │            │  body   │     VR     │
            ├────────────┤         │            │
            │   log      │         │            │
            └────────────┴─────────┴────────────┘
            
        This only *looks* the same as the "legacy" layout after 'toggle-split-direction'.

        https://gist.github.com/gatesphere/82c9f67ca7b65d09e85208e0b2f7eca1#file-vertical-thirds
        """
        g.trace('not ready: using legacy layout')
        return dw.create_legacy_layout()

        # main_splitter = dw.main_splitter
        # secondary_splitter = dw.secondary_splitter

        # dw.createOutlinePane(main_splitter)
        # dw.createLogPane(main_splitter)
        # dw.createBodyPane(secondary_splitter)
        # dw.vr_parent_frame = secondary_splitter
    #@-<< create vertical-thirds layout >>
    table = (
        ('horizontal-thirds', create_horizontal_thirds_layout),
        ('render-focused', create_render_focused_layout),
        ('vertical-thirds',  create_vertical_thirds_layout),
    )
    for key, creator in table:
        assert key not in layout_dict
        layout_dict[key] = creator
#@-leo
