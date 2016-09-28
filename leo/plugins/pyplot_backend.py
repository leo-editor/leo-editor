#@+leo-ver=5-thin
#@+node:ekr.20160928073518.1: * @file pyplot_backend.py
'''
    A helper for the viewrendered plugin.
    This is *NOT* a real plugin.
'''
DEBUG = False
#@+<< pyplot_backend imports >>
#@+node:ekr.20160928074801.1: ** << pyplot_backend imports >>
import leo.core.leoGlobals as g
from leo.core.leoQt import isQt5, QtCore
import_ok = True
if isQt5:
    assert False, '===== pyplot_backend.py: MUST USE QT4'
    try:
        import matplotlib.backends.backend_qt5agg as backend
    except ImportError:
        import_ok = False
else:
    try:
        import matplotlib.backends.backend_qt4agg as backend
    except ImportError:
        import_ok = False
if import_ok:
    try:
        FigureCanvasAgg         = backend.FigureCanvasAgg
        FigureCanvasQT          = backend.FigureCanvasQT
        FigureCanvasQTAgg       = backend.FigureCanvasQTAgg
        FigureCanvasQTAggBase   = backend.FigureCanvasQTAggBase
        FigureManagerQT         = backend.FigureManagerQT
        _FigureCanvasQTAggBase  = backend._FigureCanvasQTAggBase
        from matplotlib.figure import Figure
        # from .backend_qt5agg import FigureCanvasQTAggBase as _FigureCanvasQTAggBase
        # from .backend_agg import FigureCanvasAgg
        # from .backend_qt4 import QtCore
        # from .backend_qt4 import FigureManagerQT
        # from .backend_qt4 import FigureCanvasQT
        # from .backend_qt4 import NavigationToolbar2QT
    except ImportError:
        import_ok = False
#@-<< pyplot_backend imports >>
#@+others
#@+node:ekr.20160928073605.1: ** init
def init():
    '''Return True if the plugin has loaded successfully.'''
    g.trace('pyplot_backend.py is not a plugin.')
    return False
#@+node:ekr.20160928082006.1: ** Leo backend
# pylint: disable=function-redefined
#@+node:ekr.20160928074615.2: *3* new_figure_manager
def new_figure_manager(num, *args, **kwargs):
    """
    Create a new figure manager instance
    """
    if DEBUG:
        g.trace('(VR)', g.callers())
        # g.trace('(VR): kwargs', kwargs)
        
    FigureClass = kwargs.pop('FigureClass', Figure)
    thisFig = FigureClass(*args, **kwargs)
    return new_figure_manager_given_figure(num, thisFig)
#@+node:ekr.20160928074615.3: *3* new_figure_manager_given_figure
def new_figure_manager_given_figure(num, figure):
    """
    Create a new figure manager instance for the given figure.
    """
    if DEBUG:
        g.trace('(VR)', num, figure)
    canvas = FigureCanvasQTAgg(figure)
    return FigureManagerQT(canvas, num)
#@+node:ekr.20160928080012.1: *3* FigureCanvasQTAggBase
if import_ok:
    class FigureCanvasQTAggBase(_FigureCanvasQTAggBase):
        def __init__(self, figure):
            # pylint: disable=super-init-not-called
            if DEBUG: g.trace('(VR: FigureCanvasQTAggBase)', figure)
            self._agg_draw_pending = False
else:
    
    class FigureCanvasQTAggBase:
        def __init__(self, figure):
            g.trace('(VR: DUMMY FigureCanvasQTAggBase)', g.callers())
            self._agg_draw_pending = False
#@+node:ekr.20160928074615.4: *3* FigureCanvasQTAgg
if import_ok:

    class FigureCanvasQTAgg(FigureCanvasQTAggBase, FigureCanvasQT, FigureCanvasAgg):
        """
        The canvas the figure renders into.  Calls the draw and print fig
        methods, creates the renderers, etc...
        """
        def __init__(self, figure):
            if DEBUG: g.trace('(VR: FigureCanvasQTAgg)', figure)
            FigureCanvasQT.__init__(self, figure)
            FigureCanvasQTAggBase.__init__(self, figure)
            FigureCanvasAgg.__init__(self, figure)
            self._drawRect = None
            self.blitbox = None
            self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)
            
else:
    class FigureCanvasQTAgg:
        def __init__(self, figure):
            if DEBUG: g.trace('(VR: DUMMY FigureCanvasQTAgg)', figure, g.callers())
#@-others
#@@language python
#@-leo
