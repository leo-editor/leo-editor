#@+leo-ver=5-thin
#@+node:ekr.20240729034257.1: * @file ../plugins/define_qt_layouts.py
"""
define_qt_layouts.py: define several qt layouts.
"""

from leo.core import leoGlobals as g
# from leo.core.leoQt import Orientation, QtWidgets

g.assertUi('qt')

def init():
    """Return True if the plugin has loaded successfully."""
    if g.unitTesting:
        return False
    g.registerHandler('after-create-layout-dict', update_layout)
    return True

def update_layout(tag, args):
    """Update dw.layout_dict with a new layout."""
    # Note: c.frame.top does not exist yet.
    dw = args.get('dw')
    layout_dict = args.get('layout_dict')
    #@+others  # Define layouts.
    #@+node:ekr.20240729040239.1: ** function: create_all_vertical_layout
    def create_all_vertical_layout(dw=dw):
        """Create a completely vertical layout:
            ┌───────────┐
            │  outline  │
            ├───────────┤
            │  body     │
            ├───────────┤
            │  log      │
            ├───────────┤
            │  VR       │
            └───────────┘
        """
        main_splitter, secondary_splitter = dw.createMainLayout(dw.centralwidget)
        dw.createOutlinePane(main_splitter)
        dw.createBodyPane(main_splitter)
        dw.createLogPane(main_splitter)
        dw.vr_parent_frame = main_splitter
        return main_splitter, secondary_splitter
    #@-others
    table = (
        ('all-vertical', create_all_vertical_layout),
    )
    for key, creator in table:
        if key in layout_dict:
            g.es_print(f"Overriding {key} layout")
        layout_dict[key] = creator
#@-leo
