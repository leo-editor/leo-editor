# -*- coding: utf-8 -*-
# Copyright (C) 2016, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

"""
Module to integrate GUI event loops in the Pyzo interpreter.

This specifies classes that all have the same interface. Each class
wraps one GUI toolkit.

Support for PyQt4, WxPython, FLTK, GTK, TK.

"""

import sys
import time

from pyzokernel import printDirect


# Warning message.
mainloopWarning = """
Note: The GUI event loop is already running in the pyzo kernel. Be aware
that the function to enter the main loop does not block.
""".strip()+"\n"

# Qt has its own message
mainloopWarning_qt = """
Note on using QApplication.exec_():
The GUI event loop is already running in the pyzo kernel, and exec_()
does not block. In most cases your app should run fine without the need
for modifications. For clarity, this is what the pyzo kernel does:
- Prevent deletion of objects in the local scope of functions leading to exec_()
- Prevent system exit right after the exec_() call
""".lstrip()


# Print the main loop warning at most once
_printed_warning = False
def print_mainloop_warning(msg=None):
    global _printed_warning
    if not _printed_warning:
        _printed_warning = True
        msg = msg or mainloopWarning
        printDirect(msg)


class App_base:
    """ Defines the interface.
    """
    
    def process_events(self):
        pass
    
    def _keyboard_interrupt(self, signum=None, frame=None):
        interpreter = sys._pyzoInterpreter
        interpreter.write("\nKeyboardInterrupt\n")
        interpreter._resetbuffer()
        if interpreter.more:
            interpreter.more = 0
            interpreter.newPrompt = True
    
    def run(self, repl_callback, sleeptime=0.01):
        """ Very simple mainloop. Subclasses can overload this to use
        the native event loop. Attempt to process GUI events at least
        every sleeptime seconds.
        """
        
        if hasattr(time, 'perf_counter'):
            perf_counter= time.perf_counter
        else:
            perf_counter = time.time
        
        _sleeptime = sleeptime
        
        # The toplevel while-loop is just to catch Keyboard interrupts
        # and then proceed. The inner while-loop is the actual event loop.
        while True:
            try:
                
                while True:
                    time.sleep(_sleeptime)
                    repl_callback()
                    self.process_events()
            
            except KeyboardInterrupt:
                self._keyboard_interrupt()
            except TypeError:
                # For some reason, when wx is integrated, keyboard interrupts
                # result in a TypeError.
                # I tried to find the source, but did not find it. If anyone
                # has an idea, please e-mail me!
                if '_wx' in self.__class__.__name__.lower():
                    self._keyboard_interrupt()
    
    def quit(self):
        raise SystemExit()


class App_asyncio(App_base):
    """ Based on asyncio (standard Python) event loop.
    
    We do not run the event loop and a timer to keep the REPL active, because
    asyncio does allow creating new loops while one is running. So we stick to
    a simple and non-intrusive mechanism to regularly process events from
    whatever event loop is current at any given moment.
    
    """
    
    def __init__(self):
        import asyncio
        self.app = asyncio.get_event_loop()
        self.app._in_event_loop = 'Pyzo'
        self._warned_about_process_events = False
        self._blocking = False
        
        # Hijack 
        
        # Prevent entering forever, not giving control back to repl
        self.app._original_run_forever = self.app.run_forever
        self.app.run_forever = self.stub_run_forever
        # The run_until_complete() calls run_forever and then checks that future completed
        self.app._original_run_until_complete = self.app.run_until_complete
        self.app.run_until_complete = self.stub_run_until_complete
        # Prevent the loop from being destroyed
        self.app._original_close = self.app.close
        self.app.close = self.stub_close
        # Stop is fine, since we don't "run" the loop, but just keep it active
    
    def stub_run_until_complete(self, *args):
        self._blocking = True
        return self.app._original_run_until_complete(*args)
    
    def stub_run_forever(self):
        if self._blocking:
            self._blocking = False
            self.app._original_run_forever()
    
    def stub_close(self):
        pass
    
    def process_events(self):
        loop = self.app
        if loop.is_closed():
            pass  # not much we can do
        elif loop.is_running():
            if not self._warned_about_process_events:
                print('Warning: cannot process events synchronously in asyncio')
                self._warned_about_process_events = True
        else:
            # First calling stop and then run_forever() process all pending events.
            # We do this multiple times to work around the limited frequence that this
            # method gets called, but we need to use a private attribute for that :/
            for i in range(20):
                loop.stop()
                loop._original_run_forever()
                if len(getattr(loop, '_ready', ())) == 0:
                    break
    
    def quit(self):
        loop = self.app
        try:
            if not loop.is_closed():
                loop.close()
        finally:
            raise SystemExit()
        

class App_tk(App_base):
    """ Tries to import tkinter and returns a withdrawn tkinter root
    window.  If tkinter is already imported or not available, this
    returns None.
    Modifies tkinter's mainloop with a dummy so when a module calls
    mainloop, it does not block.
    """
    def __init__(self):
        
        # Try importing
        import sys
        if sys.version[0] == '3':
            import tkinter
        else:
            import Tkinter as tkinter
        
        # Replace mainloop. Note that a root object obtained with
        # tkinter.Tk() has a mainloop method, which will simply call
        # tkinter.mainloop().
        def dummy_mainloop(*args,**kwargs):
            print_mainloop_warning()
        tkinter.Misc.mainloop = dummy_mainloop
        tkinter.mainloop = dummy_mainloop
                
        # Create tk "main window" that has a Tcl interpreter.
        # Withdraw so it's not shown. This object can be used to
        # process events for any other windows.
        r = tkinter.Tk()
        r.withdraw()
        
        # Store the app instance to process events
        self.app = r
        
        # Notify that we integrated the event loop
        self.app._in_event_loop = 'Pyzo'
        tkinter._in_event_loop = 'Pyzo'
    
    def process_events(self):
        self.app.update()



class App_fltk(App_base):
    """ Hijack fltk 1.
    This one is easy. Just call fl.wait(0.0) now and then.
    Note that both tk and fltk try to bind to PyOS_InputHook. Fltk
    will warn about not being able to and Tk does not, so we should
    just hijack (import) fltk first. The hook that they try to fetch
    is not required in pyzo, because the pyzo interpreter will keep
    all GUI backends updated when idle.
    """
    def __init__(self):
        # Try importing
        import fltk as fl
        import types
        
        # Replace mainloop with a dummy
        def dummyrun(*args,**kwargs):
            print_mainloop_warning()
        fl.Fl.run = types.MethodType(dummyrun, fl.Fl)
        
        # Store the app instance to process events
        self.app =  fl.Fl
        
        # Notify that we integrated the event loop
        self.app._in_event_loop = 'Pyzo'
        fl._in_event_loop = 'Pyzo'
    
    def process_events(self):
        self.app.wait(0)



class App_fltk2(App_base):
    """ Hijack fltk 2.
    """
    def __init__(self):
        # Try importing
        import fltk2 as fl
        
        # Replace mainloop with a dummy
        def dummyrun(*args,**kwargs):
            print_mainloop_warning()
        fl.run = dummyrun
        
        # Return the app instance to process events
        self.app = fl
        
        # Notify that we integrated the event loop
        self.app._in_event_loop = 'Pyzo'
    
    def process_events(self):
        # is this right?
        self.app.wait(0)


class App_tornado(App_base):
    """ Hijack Tornado event loop.
    
    Tornado does have a function to process events, but it does not
    work when the event loop is already running. Therefore we don't
    enter the real Tornado event loop, but just poll it regularly.
    """
    
    def __init__(self):
        # Try importing
        import tornado.ioloop
        
        # Get the "app" instance
        self.app = tornado.ioloop.IOLoop.instance()
        
        # Replace mainloop with a dummy
        def dummy_start():
            print_mainloop_warning()
            sys._pyzoInterpreter.ignore_sys_exit = True
            self.app.add_callback(reset_sys_exit)
        def dummy_stop():
            pass
        def reset_sys_exit():
            sys._pyzoInterpreter.ignore_sys_exit = False
        def run_sync(func, timeout=None):
            self.app.start = self.app._original_start
            try:
                self.app._original_run_sync(func, timeout)
            finally:
                self.app.start = self.app._dummy_start
        #
        self.app._original_start = self.app.start
        self.app._dummy_start = dummy_start
        self.app.start = self.app._dummy_start
        #
        self.app._original_stop = self.app.stop
        self.app._dummy_stop = dummy_stop
        self.app.stop = self.app._dummy_stop
        #
        self.app._original_run_sync = self.app.run_sync
        self.app.run_sync = run_sync
        
        # Notify that we integrated the event loop
        self.app._in_event_loop = 'Pyzo'
        
        self._warned_about_process_events = False
    
    def process_events(self):
        if not self._warned_about_process_events:
            print('Warning: cannot process events synchronously in Tornado')
            self._warned_about_process_events = True
        #self.app.run_sync(lambda x=None: None)
    
    def run(self, repl_callback, sleeptime=None):
        from tornado.ioloop import PeriodicCallback
        # Create timer
        self._timer = PeriodicCallback(repl_callback, 0.05*1000)
        self._timer.start()
        # Enter mainloop
        self.app._original_start()
        while True:
            try:
                self.app._original_start()
            except KeyboardInterrupt:
                self._keyboard_interrupt()
                self.app._original_stop()
                continue
            break
    
    def quit(self):
        self.app._original_stop()
        # raise SystemExit()


class App_qt(App_base):
    """ Common functionality for pyqt and pyside
    """
    
    
    def __init__(self):
        import types
        
        # Try importing qt
        QtGui, QtCore = self.importCoreAndGui()
        self._QtGui, self._QtCore = QtGui, QtCore
        
        # Store the real application class
        if not hasattr(QtGui, 'real_QApplication'):
            QtGui.real_QApplication = QtGui.QApplication
        
        
        class QApplication_hijacked(QtGui.QApplication):
            """ QApplication_hijacked(*args, **kwargs)
            
            Hijacked QApplication class. This class has a __new__()
            method that always returns the global application
            instance, i.e. QtGui.qApp.
            
            The QtGui.qApp instance is an instance of the original
            QtGui.QApplication, but with its __init__() and exec_()
            methods replaced.
            
            You can subclass this class; the global application instance
            will be given the methods and attributes so it will behave
            like the subclass.
            """
            def __new__(cls, *args, **kwargs):
                
                # Get the singleton application instance
                theApp = QApplication_hijacked.instance()
                
                # Instantiate an original QApplication instance if we need to
                if theApp is None:
                    theApp = QtGui.real_QApplication(*args, **kwargs)
                    QtGui.qApp = theApp
                
                # Add attributes of cls to the instance to make it
                # behave as if it were an instance of that class
                for key in dir(cls):
                    # Skip all magic methods except __init__
                    if key.startswith('__') and key != '__init__':
                        continue
                    # Skip attributes that we already have
                    val = getattr(cls, key)
                    if hasattr(theApp.__class__, key):
                        if hash(val) == hash(getattr(theApp.__class__, key)):
                            continue
                    # Make method?
                    if hasattr(val, '__call__'):
                        if hasattr(val, 'im_func'):
                            val = val.im_func # Python 2.x
                        val = types.MethodType(val, theApp.__class__)
                    # Set attribute on app instance (not the class!)
                    try:
                        setattr(theApp, key, val)
                    except Exception:
                        pass # tough luck
                
                # Call init function (in case the user overloaded it)
                theApp.__init__(*args, **kwargs)
                
                # Return global app object (modified to the users needs)
                return theApp
            
            def __init__(self, *args, **kwargs):
                pass
            
            def exec_(self, *args, **kwargs):
                """ This function does nothing, except printing a
                warning message. The point is that a Qt App can crash
                quite hard if an object goes out of scope, and the error
                is not obvious.
                """
                print_mainloop_warning(mainloopWarning_qt)
                
                # Store local namespaces (scopes) of any functions that
                # precede this call. It might have a widget or application
                # object that should not be deleted ...
                import inspect, __main__
                for caller in inspect.stack()[1:]:
                    frame, name = caller[0], caller[3]
                    if name.startswith('<'):  # most probably "<module>"
                        break
                    else:
                        __main__.__dict__[name+'_locals'] = frame.f_locals
                
                # Tell interpreter to ignore any system exits
                sys._pyzoInterpreter.ignore_sys_exit = True
                
                # But re-enable it as soon as *this event* is processed
                def reEnableSysExit():
                    sys._pyzoInterpreter.ignore_sys_exit = False
                self._reEnableSysExitTimer = timer = QtCore.QTimer()
                timer.singleShot(0, reEnableSysExit)
            
            def quit(self, *args, **kwargs):
                """ Do not quit if Qt app quits. """
                pass
        
        
        # Instantiate application object
        self.app = QApplication_hijacked([''])
        
        # Keep it alive even if all windows are closed
        self.app.setQuitOnLastWindowClosed(False)
        
        # Replace app class
        QtGui.QApplication = QApplication_hijacked
        
        # Notify that we integrated the event loop
        self.app._in_event_loop = 'Pyzo'
        QtGui._in_event_loop = 'Pyzo'
        
        # Use sys.excepthook to catch keyboard interrupts that occur
        # in event handlers. We also want to call the curren hook
        self._original_excepthook = sys.excepthook
        sys.excepthook = self._excepthook
    
    
    def _excepthook(self, type, value, traceback):
        if issubclass(type, KeyboardInterrupt):
            self._keyboard_interrupt()
        elif self._original_excepthook is not None:
            return self._original_excepthook(type, value, traceback)
    
    
    def process_events(self):
        self.app.flush()
        self.app.processEvents()
    
    
    def run(self, repl_callback, sleeptime=None):
        # Create timer
        timer = self._timer = self._QtCore.QTimer()
        timer.setSingleShot(False)
        timer.setInterval(0.05*1000)  # ms
        timer.timeout.connect(repl_callback)
        timer.start()
        
        # Enter Qt mainloop
        #self._QtGui.real_QApplication.exec_(self.app)
        self._QtGui.real_QApplication.exec_()
    
    
    def quit(self):
        # A nicer way to quit
        self._QtGui.real_QApplication.quit()



class App_pyqt5(App_qt):
    """ Hijack the PyQt5 mainloop.
    """
    
    def importCoreAndGui(self):
        # Try importing qt
        import PyQt5  # noqa
        from PyQt5 import QtGui, QtCore, QtWidgets  # noqa
        return QtWidgets, QtCore  # QApp sits on QtWidgets


class App_pyqt4(App_qt):
    """ Hijack the PyQt4 mainloop.
    """
    
    def importCoreAndGui(self):
        # Try importing qt
        import PyQt4  # noqa
        from PyQt4 import QtGui, QtCore
        return QtGui, QtCore
    
class App_pyside2(App_qt):
    """ Hijack the PySide2 mainloop.
    """
    
    def importCoreAndGui(self):
        # Try importing qt
        import PySide2  # noqa
        from PySide2 import QtGui, QtCore, QtWidgets  # noqa
        return QtWidgets, QtCore  # QApp sits on QtWidgets
    
class App_pyside(App_qt):
    """ Hijack the PySide mainloop.
    """
    
    def importCoreAndGui(self):
        # Try importing qt
        import PySide  # noqa
        from PySide import QtGui, QtCore
        return QtGui, QtCore



class App_wx(App_base):
    """ Hijack the wxWidgets mainloop.
    """
    
    def __init__(self):
        
        # Try importing
        try:
            import wx
        except ImportError:
            # For very old versions of WX
            import wxPython as wx
        
        # Create dummy mainloop to replace original mainloop
        def dummy_mainloop(*args, **kw):
            print_mainloop_warning()
        
        # Depending on version, replace mainloop
        ver = wx.__version__
        orig_mainloop = None
        if ver[:3] >= '2.5':
            if hasattr(wx, '_core_'): core = getattr(wx, '_core_')
            elif hasattr(wx, '_core'): core = getattr(wx, '_core')
            else: raise ImportError
            orig_mainloop = core.PyApp_MainLoop
            core.PyApp_MainLoop = dummy_mainloop
        elif ver[:3] == '2.4':
            orig_mainloop = wx.wxc.wxPyApp_MainLoop
            wx.wxc.wxPyApp_MainLoop = dummy_mainloop
        else:
            # Unable to find either wxPython version 2.4 or >= 2.5."
            raise ImportError
        
        self._orig_mainloop = orig_mainloop
        # Store package wx
        self.wx = wx
        
        # Get and store the app instance to process events
        app = wx.GetApp()
        if app is None:
            app = wx.App(False)
        self.app = app
        
        # Notify that we integrated the event loop
        self.app._in_event_loop = 'Pyzo'
        wx._in_event_loop = 'Pyzo'
    
    def process_events(self):
        wx = self.wx
        
        # This bit is really needed
        old = wx.EventLoop.GetActive()
        eventLoop = wx.EventLoop()
        wx.EventLoop.SetActive(eventLoop)
        while eventLoop.Pending():
            eventLoop.Dispatch()
        
        # Process and reset
        self.app.ProcessIdle() # otherwise frames do not close
        wx.EventLoop.SetActive(old)



class App_gtk(App_base):
    """ Modifies pyGTK's mainloop with a dummy so user code does not
    block IPython.  processing events is done using the module'
    main_iteration function.
    """
    def __init__(self):
        # Try importing gtk
        import gtk
        
        # Replace mainloop with a dummy
        def dummy_mainloop(*args, **kwargs):
            print_mainloop_warning()
        gtk.mainloop = dummy_mainloop
        gtk.main = dummy_mainloop
        
        # Replace main_quit with a dummy too
        def dummy_quit(*args, **kwargs):
            pass
        gtk.main_quit = dummy_quit
        gtk.mainquit = dummy_quit
        
        # Make sure main_iteration exists even on older versions
        if not hasattr(gtk, 'main_iteration'):
            gtk.main_iteration = gtk.mainiteration
        
        # Store 'app object'
        self.app = gtk
        
        # Notify that we integrated the event loop
        self.app._in_event_loop = 'Pyzo'
    
    def process_events(self):
        gtk = self.app
        while gtk.events_pending():
            gtk.main_iteration(False)

