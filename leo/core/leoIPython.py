# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20120401063816.10072: * @file leoIPython.py
#@@first
#@+<< leoIpython docstring >>
#@+node:ekr.20180326102140.1: ** << leoIpython docstring >>
'''
Support for the --ipython command-line option and the IPython bridge:
http://leoeditor.com/IPythonBridge.html

This code will run on IPython 1.0 and higher, as well as the IPython
0.x versions that define the IPKernelApp class.

This module replaces leo.external.ipy_leo and
leo.plugins.internal_ipkernel.

The ``--ipython`` command-line argument creates g.app.ipk, a
*singleton* IPython shell, shared by all IPython consoles.

The startup code injects a single object, _leo, into the IPython namespace.
This object, a LeoNameSpace instance, simplifies dealing with multiple open
Leo commanders.
'''
#@-<< leoIpython docstring >>
#@+<< imports >>
#@+node:ekr.20130930062914.15990: ** << imports >> (leoIpython.py)
from __future__ import print_function
import sys
import leo.core.leoGlobals as g
# Switches...
import_trace = True and not g.unitTesting

def import_fail(s):
    if import_trace:
        print('===== leoIpython.py: can not import %s' % s)

try:
    from ipykernel.connect import connect_qtconsole
except ImportError:
    connect_qtconsole = None
    import_fail('connect_qtconsole')
try:
    # https://github.com/ipython/ipykernel/tree/master/ipykernel
    # from IPython.core.interactiveshell import ExecutionResult
    from ipykernel.kernelapp import IPKernelApp
except ImportError:
    IPKernelApp = None
    import_fail('IPKernelApp')

g.app.ipython_inited = IPKernelApp is not None
#@-<< imports >>
#@+others
#@+node:ekr.20130930062914.15993: ** class InternalIPKernel
class InternalIPKernel(object):
    '''
    An interface class between Leo's core and IPython.
    Called from LeoQtGui.runWithIpythonKernel()
    '''
    #@+others
    #@+node:ekr.20130930062914.15994: *3* ileo.__init__
    def __init__(self, backend='qt'):
        '''Ctor for InternalIPKernal class.'''
        # g.trace('(InternalIPKernel)', g.callers())
        # Part 1: create the ivars.
        self.consoles = []
            # List of Qt consoles.
        self.kernelApp = None
            # The IPKernelApp instance, a subclass of
            # BaseIPythonApplication, InteractiveShellApp, ConnectionFileMixin
        self.namespace = None
            # Inited below.
        self._init_keys = None
            # Keys present at startup so we don't print the entire pylab/numpy
            # namespace when the user clicks the 'namespace' button
        # Part 2: Init the kernel and init the ivars.
        kernelApp = self.pylab_kernel(backend)
        assert kernelApp == self.kernelApp
            # Sets self.kernelApp.
            # Start IPython kernel with GUI event loop and pylab support
        self.namespace = kernelApp.shell.user_ns
            # Import the shell namespace.
        self._init_keys = set(self.namespace.keys())
        if 'ipython' in g.app.debug:
            self.namespace['kernelApp'] = kernelApp
            self.namespace['app_counter'] = 0
            # Example: a variable that will be seen by the user in the shell, and
            # that the GUI modifies (the 'Counter++' button increments it)
    #@+node:ekr.20130930062914.15998: *3* ileo.cleanup_consoles
    def cleanup_consoles(self, event=None):
        '''Kill all ipython consoles.  Called from app.finishQuit.'''
        for console in self.consoles:
            console.kill()
    #@+node:ekr.20130930062914.15997: *3* ileo.count
    def count(self, event=None):
        self.namespace['app_counter'] += 1
    #@+node:ekr.20130930062914.15996: *3* ileo.new_qt_console
    def new_qt_console(self, event=None):
        '''
        Start a new qtconsole connected to our kernel.
        
        Called from qt_gui.runWithIpythonKernel.
        '''
        trace = 'ipython' in g.app.debug
        console = None
        if not self.namespace.get('_leo'):
            self.namespace['_leo'] = LeoNameSpace()
        if trace:
            self.put_log('new_qt_console: connecting...')
            self.put_log(self.kernelApp.connection_file, raw=True)
        try:
            # Fix #213: leo --ipython fails to connect with python3.5 and jupyter
            # https://github.com/leo-editor/leo-editor/issues/213
            # The connection file has the form kernel-nnn.json.
            # Using the defaults lets connect_qtconsole find the .json file.
            console = connect_qtconsole()
                # ipykernel.connect.connect_qtconsole
            if trace: g.trace(console)
            if console:
                self.consoles.append(console)
            else:
                self.put_warning('new_qt_console: no console!')
        except OSError as e:
            # Print statements do not work here.
            self.put_warning('new_qt_console: failed to connect to console')
            self.put_warning(e, raw=True)
        except Exception as e:
            self.put_warning('new_qt_console: unexpected exception')
            self.put_warning(e)
        return console
    #@+node:ekr.20160331083020.1: *3* ileo.pdb
    def pdb(self, message=''):
        """Fall into pdb."""
        import pdb
            # Required: we have just defined pdb as a function!
        pdb = pdb.Pdb(stdout=sys.__stdout__)
        if message:
            self.put_stdout(message)
        pdb.set_trace()
            # This works, but there are no IPython sources.
    #@+node:ekr.20130930062914.15995: *3* ileo.print_namespace
    def print_namespace(self, event=None):
        print("\n***Variables in User namespace***")
        for k, v in self.namespace.items():
            if k not in self._init_keys and not k.startswith('_'):
                print('%s -> %r' % (k, v))
        sys.stdout.flush()
    #@+node:ekr.20160308090432.1: *3* ileo.put_log
    def put_log(self, s, raw=False):
        '''Put a message to the IPython kernel log.'''
        if not raw:
            s = '[leoIpython.py] %s' % s
        if self.kernelApp:
            self.kernelApp.log.info(s)
        else:
            self.put_stdout(s)
    #@+node:ekr.20160331084025.1: *3* ileo.put_stdout
    def put_stdout(self, s):
        '''Put s to sys.__stdout__.'''
        sys.__stdout__.write(s.rstrip()+'\n')
        sys.__stdout__.flush()
    #@+node:ekr.20160308101536.1: *3* ileo.put_warning
    def put_warning(self, s, raw=False):
        '''
        Put an warning message to the IPython kernel log.
        This will be seen, regardless of Leo's --debug option.
        '''
        if not raw:
            s = '[leoIpython.py] %s' % s
        if self.kernelApp:
            self.kernelApp.log.warning(s)
        else:
            self.put_stdout(s)
    #@+node:ekr.20130930062914.15992: *3* ileo.pylab_kernel
    def pylab_kernel(self, gui):
        '''Launch an IPython kernel with pylab support for the gui.'''
        trace = False and not g.unitTesting
            # Increased logging.
        self.kernelApp = kernelApp = IPKernelApp.instance()
            # IPKernalApp is a singleton class.
            # Return the singleton instance, creating it if necessary.
        if kernelApp:
            # --pylab is no longer needed to create a qt console.
            # --pylab=qt now generates:
                # RuntimeError: Cannot activate multiple GUI eventloops
                # GUI event loop or pylab initialization failed
            args = ['python', '--pylab']
                # Fails
                # args = ['python', '--pylab=%s' % (gui)]
            if trace:
                args.append('--log-level=20')
                    # Higher is *quieter*
                # args.append('--debug')
                # Produces a verbose IPython log.
                #'--log-level=10'
                # '--pdb', # User-level debugging
            try:
                # self.pdb()
                kernelApp.initialize(args)
            except Exception:
                sys.stdout = sys.__stdout__
                print('kernelApp.initialize failed!')
                raise
        else:
            g.trace('IPKernelApp.instance failed!')
        return kernelApp
    #@+node:ekr.20160329053849.1: *3* ileo.run_script
    def run_script(self, file_name, script):
        '''
        Helper for the ipython-exec command.
        Run the script in the qt console.
        '''
        # https://ipython.org/ipython-doc/dev/interactive/qtconsole.html
        # https://github.com/ipython/ipython/blob/master/IPython/core/interactiveshell.py
        shell = self.kernelApp.shell # ZMQInteractiveShell
        old_show = getattr(shell, '_showtraceback', None)
        code = compile(script, file_name, 'exec')
        # g.trace(old_show.__name__)
        #@+<< define show_traceback >>
        #@+node:ekr.20160402124159.1: *4* << define show_traceback >>
        def show_traceback(etype, evalue, stb, shell=shell):
            '''Monkey-patched replacement for ZMQInteractiveShell._showtraceback.'''
            # stb is an internal representation of the traceback...
            # was: print(self.InteractiveTB.stb2text(stb), file=io.stdout)
            print(shell.InteractiveTB.stb2text(stb), file=sys.stderr)
            sys.stderr.flush()
        #@-<< define show_traceback >>
        shell._showtraceback = show_traceback
        shell.run_code(code)
        if old_show:
            shell._showtraceback = old_show
    #@+node:ekr.20171115090205.1: *3* ileo.test
    def test(self):
        
        from ipykernel.connect import connect_qtconsole
        from ipykernel.kernelapp import IPKernelApp
        
        kernelApp = IPKernelApp.instance()
        args = ['python', '--pylab=qt', '--log-level=20']
        kernelApp.initialize(args)
        connect_qtconsole()
    #@-others
#@+node:ekr.20130930062914.16002: ** class LeoNameSpace
class LeoNameSpace(object):
    '''An interface class passed to IPython that provides easy
    access to "g" and all commanders.

    A convenience property, "c" provides access to the first
    commander in g.app.windowList.
    '''

    def __init__(self):
        '''LeoNameSpace ctor.'''
        self.commander = None
            # The commander returned by the c property.
        self.commanders_list = []
            # The list of commanders returned by the commanders property.
        self.g = g
        self.update()
    #@+others
    #@+node:ekr.20130930062914.16006: *3* LeoNS.c property
    def __get_c(self):
        '''Return the designated commander, or the only open commander.'''
        self.update()
        if self.commander and self.commander in self.commanders_list:
            return self.commander
        elif len(self.commanders_list) == 1:
            return self.commanders_list[0]
        else:
            return None

    def __set_c(self, c):
        '''Designate the commander to be returned by the getter.'''
        self.update()
        if c in self.commanders_list:
            self.commander = c
        else:
            g.trace(g.callers())
            raise ValueError(c)

    c = property(
        __get_c, __set_c,
        doc="LeoNameSpace c property")
    #@+node:edward.20130930125732.11822: *3* LeoNS.commanders property
    def __get_commanders(self):
        '''Return the designated commander, or the only open commander.'''
        self.update()
        return self.commanders_list

    commanders = property(
        __get_commanders, None,
        doc="LeoNameSpace commanders property (read-only)")
    #@+node:ekr.20130930062914.16009: *3* LeoNS.find_c
    def find_c(self, path):
        '''Return the commander associated with path, or None.'''
        g = self.g
        self.update()
        path = g.os_path_normcase(path)
        short_path = g.shortFileName(path)
        for c in self.commanders_list:
            fn = g.os_path_normcase(c.fileName())
            short_fn = g.shortFileName(fn)
            if fn == path or short_fn == short_path:
                return c
    #@+node:ekr.20130930062914.16003: *3* LeoNS.update
    def update(self):
        '''Update the list of available commanders.'''
        self.commanders_list = [frame.c for frame in g.app.windowList]
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
