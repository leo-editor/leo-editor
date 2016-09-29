#@+leo-ver=5-thin
#@+node:ekr.20160928073518.1: * @file pyplot_backend.py
'''
    A helper for the viewrendered plugin.
    This is *NOT* a real plugin.
'''
#@+<< pyplot_backend imports >>
#@+node:ekr.20160928074801.1: ** << pyplot_backend imports >>
import leo.core.leoGlobals as g
import leo.plugins.viewrendered as vr
from leo.core.leoQt import isQt5, QtCore, QtWidgets, QtGui
import os
import six

import_ok = True
if isQt5:
    assert False, '===== pyplot_backend.py: MUST USE QT4'
    try:
        import matplotlib.backends.backend_qt5agg as backend
    except ImportError:
        import_ok = False
else:
    try:
        import matplotlib
        from matplotlib._pylab_helpers import Gcf
        import matplotlib.backends.backend_qt4agg as backend
        import matplotlib.backends.backend_qt5 as backend_qt5
        import matplotlib.backend_bases as backend_bases
    except ImportError:
        g.es_exception()
        import_ok = False
if import_ok:
    try:
        FigureManagerBase       = backend_bases.FigureManagerBase
        
        # These work
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
# pylint: disable=function-redefined`
#@+node:ekr.20160928074615.2: *3* new_figure_manager
def new_figure_manager(num, *args, **kwargs):
    """
    Create a new figure manager instance
    """
    # g.trace('(VR)', g.callers())
    # g.trace('(VR): kwargs', kwargs) 
    FigureClass = kwargs.pop('FigureClass', Figure)
    thisFig = FigureClass(*args, **kwargs)
    return new_figure_manager_given_figure(num, thisFig)
#@+node:ekr.20160928074615.3: *3* new_figure_manager_given_figure
def new_figure_manager_given_figure(num, figure):
    """
    Create a new figure manager instance for the given figure.
    """
    canvas = FigureCanvasQTAgg(figure)
    # g.trace('(VR) %s\ncanvas: %s\nfigure: %s' % (num, canvas.__class__, figure.__class__))
    return LeoFigureManagerQT(canvas, num)
#@+node:ekr.20160928080012.1: *3* class FigureCanvasQTAggBase (not used)
if 0:
    if import_ok:

        class FigureCanvasQTAggBase(_FigureCanvasQTAggBase):
            def __init__(self, figure):
                # pylint: disable=super-init-not-called
                g.trace('(VR: FigureCanvasQTAggBase)', figure)
                g.trace('(VR: _FigureCanvasQTAggBase:', _FigureCanvasQTAggBase)
                    # backend_qt5agg.FigureCanvasQTAggBase (an object)
                self._agg_draw_pending = False
    else:
        
        class FigureCanvasQTAggBase:
            def __init__(self, figure):
                g.trace('(VR: DUMMY FigureCanvasQTAggBase)', g.callers())
                self._agg_draw_pending = False
#@+node:ekr.20160928074615.4: *3* class FigureCanvasQTAgg
if import_ok:

    class FigureCanvasQTAgg(FigureCanvasQTAggBase, FigureCanvasQT, FigureCanvasAgg):
        """
        The canvas the figure renders into.  Calls the draw and print fig
        methods, creates the renderers, etc...
        """
        def __init__(self, figure):
            # g.trace('(VR: FigureCanvasQTAgg)', figure)
            FigureCanvasQT.__init__(self, figure)
            FigureCanvasQTAggBase.__init__(self, figure)
            FigureCanvasAgg.__init__(self, figure)
            self._drawRect = None
            self.blitbox = None
            self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)

else:
    class FigureCanvasQTAgg:
        def __init__(self, figure):
            g.trace('(VR: DUMMY FigureCanvasQTAgg)', figure, g.callers())
#@+node:ekr.20160929045732.1: *3* class MainWindow (not used)
# From backend_qt5.py

if 0:

    class MainWindow(QtWidgets.QMainWindow):
        closing = QtCore.Signal()
    
        def closeEvent(self, event):
            self.closing.emit()
            QtWidgets.QMainWindow.closeEvent(self, event)
#@+node:ekr.20160929050151.1: *3* class LeoFigureManagerQT (backend_qt5.FigureManager)
# From backend_qt5.py

class LeoFigureManagerQT(backend_qt5.FigureManager):
    """
    Public attributes

    canvas      : The FigureCanvas instance
    num         : The Figure number
    toolbar     : The qt.QToolBar
    window      : The qt.QMainWindow
    """

    #@+others
    #@+node:ekr.20160929050151.2: *4* __init__ (LeoFigureManagerQt)
    def __init__(self, canvas, num):
        '''Ctor for the LeoFigureManagerQt class.'''
        # g.trace('LeoFigureManagerQT', g.app.log and g.app.log.c)
        self.use_vr = True
        self.c = c = g.app.log.c
        FigureManagerBase.__init__(self, canvas, num)
        self.canvas = canvas
        if self.use_vr:
            self.vr_controller = vc = vr.controllers.get(c.hash())
            # g.trace('vr_controller', self.vr_controller)
            self.splitter = c.free_layout.get_top_splitter()
            self.frame = w = QtGui.QFrame()
            w.setLayout(QtWidgets.QVBoxLayout())
            w.layout().addWidget(self.canvas)
            vc.embed_widget(w)
            
        if self.use_vr:
            class DummyWindow:
                def __init__(self, c):
                    self.c = c
                    self._destroying = None
                def windowTitle(self):
                    return self.c.p.h
            self.window = DummyWindow(c)
        else:
            self.window = MainWindow()
            self.window.closing.connect(canvas.close_event)
            self.window.closing.connect(self._widgetclosed)
        
            self.window.setWindowTitle("Figure %d" % num)
            image = os.path.join(matplotlib.rcParams['datapath'],
                                 'images', 'matplotlib.png')
            self.window.setWindowIcon(QtGui.QIcon(image))

        # Give the keyboard focus to the figure instead of the
        # manager; StrongFocus accepts both tab and click to focus and
        # will enable the canvas to process event w/o clicking.
        # ClickFocus only takes the focus is the window has been
        # clicked
        # on. http://qt-project.org/doc/qt-4.8/qt.html#FocusPolicy-enum or
        # http://doc.qt.digia.com/qt/qt.html#FocusPolicy-enum
        self.canvas.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.canvas.setFocus()
        
        if self.use_vr:
            self.canvas._destroying = False
        else:
            self.window._destroying = False
        
        if self.use_vr:
            self.toolbar = self._get_toolbar(self.canvas, self.frame)
            if self.toolbar is not None:
                layout = self.frame.layout()
                layout.addWidget(self.toolbar)
                # add text label to status bar
                self.statusbar_label = QtWidgets.QLabel()
                layout.addWidget(self.statusbar_label)
                self.toolbar.message.connect(self._show_message)
        else:
            self.toolbar = self._get_toolbar(self.canvas, self.window)
            if self.toolbar is not None:
                self.window.addToolBar(self.toolbar)
                self.toolbar.message.connect(self._show_message)
                tbs_height = self.toolbar.sizeHint().height()
            else:
                tbs_height = 0
                
            # add text label to status bar
            self.statusbar_label = QtWidgets.QLabel()
            self.window.statusBar().addWidget(self.statusbar_label)
            
        if self.use_vr:
            pass
        else:

            # resize the main window so it will display the canvas with the
            # requested size:
            cs = canvas.sizeHint()
            sbs = self.window.statusBar().sizeHint()
            self._status_and_tool_height = tbs_height + sbs.height()
            height = cs.height() + self._status_and_tool_height
            self.window.resize(cs.width(), height)
        
            self.window.setCentralWidget(self.canvas)
            
        if self.use_vr:
            self.canvas.draw_idle()
        else:
            if matplotlib.is_interactive():
                self.window.show()
                self.canvas.draw_idle()

        def notify_axes_change(fig):
            # This will be called whenever the current axes is changed
            if self.toolbar is not None:
                self.toolbar.update()
        self.canvas.figure.add_axobserver(notify_axes_change)

    #@+node:ekr.20160929083114.1: *4* destroy
    def destroy(self, *args):
        pass
    #@+node:ekr.20160929082310.1: *4* unused
    if 0:
        #@+others
        #@+node:ekr.20160929050151.3: *5* _show_message
        @QtCore.Slot()
        def _show_message(self, s):
            self.statusbar_label.setText(s)

        #@+node:ekr.20160929050151.4: *5* full_screen_toggle
        def full_screen_toggle(self):
            if self.window.isFullScreen():
                self.window.showNormal()
            else:
                self.window.showFullScreen()

        #@+node:ekr.20160929050151.5: *5* _widgetclosed
        def _widgetclosed(self):
            if self.window._destroying:
                return
            self.window._destroying = True
            try:
                Gcf.destroy(self.num)
            except AttributeError:
                pass
                # It seems that when the python session is killed,
                # Gcf can get destroyed before the Gcf.destroy
                # line is run, leading to a useless AttributeError.

        #@+node:ekr.20160929050151.6: *5* _get_toolbar
        def _get_toolbar(self, canvas, parent):
            # must be inited after the window, drawingArea and figure
            # attrs are set
            if 1: ### EKR
                return backend_qt5.NavigationToolbar2QT(canvas, parent, False)
            else:
                if matplotlib.rcParams['toolbar'] == 'toolbar2':
                    toolbar = NavigationToolbar2QT(canvas, parent, False)
                else:
                    toolbar = None
                return toolbar
        #@+node:ekr.20160929050151.7: *5* resize
        def resize(self, width, height):
            'set the canvas size in pixels'
            self.window.resize(width, height + self._status_and_tool_height)

        #@+node:ekr.20160929050151.8: *5* show
        def show(self):
            self.window.show()

        #@+node:ekr.20160929050151.9: *5* destroy
        def destroy(self, *args):
            # check for qApp first, as PySide deletes it in its atexit handler
            if QtWidgets.QApplication.instance() is None:
                return
            if self.window._destroying:
                return
            self.window._destroying = True
            self.window.destroyed.connect(self._widgetclosed)

            if self.toolbar:
                self.toolbar.destroy()
            if DEBUG:
                print("destroy figure manager")
            self.window.close()

        #@+node:ekr.20160929050151.10: *5* get_window_title
        def get_window_title(self):
            return six.text_type(self.window.windowTitle())
        #@+node:ekr.20160929050151.11: *5* set_window_title
        def set_window_title(self, title):
            self.window.setWindowTitle(title)
        #@-others
    #@-others
#@-others
#@@language python
#@-leo
