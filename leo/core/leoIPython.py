# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20120401063816.10072: * @file leoIPython.py
#@@first
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
#@+<< imports >>
#@+node:ekr.20130930062914.15990: ** << imports >> (leoIpython.py)
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
    #@+node:ekr.20130930062914.15994: *3* ctor
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
        if g.app.debug:
            self.namespace['kernelApp'] = kernelApp
            self.namespace['app_counter'] = 0
            # Example: a variable that will be seen by the user in the shell, and
            # that the GUI modifies (the 'Counter++' button increments it)
    #@+node:ekr.20160308090432.1: *3* put_log
    def put_log(self, s, raw=False):
        '''Put s to the IPython kernel log.'''
        if g.app.debug:
            if not raw:
                s = 'leoIpython.py: %s' % s
            if self.kernelApp:
                self.kernelApp.log.info(s)
            else:
                print(s)
    #@+node:ekr.20130930062914.15992: *3* pylab_kernel
    def pylab_kernel(self, gui):
        '''Launch an IPython kernel with pylab support for the gui.'''
        trace = False
            # Forces Leo's --debug option.
        self.kernelApp = kernelApp = IPKernelApp.instance()
            # IPKernalApp is a singleton class.
            # Return the singleton instance, creating it if necessary.
        if kernelApp:
            # pylab is needed for Qt event loop integration.
            args = ['python', '--pylab=%s' % (gui)]
            if trace or g.app.debug: args.append('--debug')
                # Produces a verbose IPython log.
                #'--log-level=10'
                # '--pdb', # User-level debugging
            try:
                kernelApp.initialize(args)
            except Exception:
                sys.stdout = sys.__stdout__
                print('kernelApp.initialize failed!')
                raise
        else:
            g.trace('IPKernelApp.instance failed!')
        return kernelApp
    #@+node:ekr.20130930062914.15995: *3* print_namespace
    def print_namespace(self, event=None):
        print("\n***Variables in User namespace***")
        for k, v in self.namespace.iteritems():
            if k not in self._init_keys and not k.startswith('_'):
                print('%s -> %r' % (k, v))
        sys.stdout.flush()
    #@+node:ekr.20130930062914.15996: *3* new_qt_console (to do: ensure connection)
    def new_qt_console(self, event=None):
        '''Start a new qtconsole connected to our kernel.'''
        trace = False or g.app.debug
            # For now, always trace when using Python 2.
        ipk = g.app.ipk
        console = None
        if ipk:
            if not ipk.namespace.get('_leo'):
                ipk.namespace['_leo'] = LeoNameSpace()
            try:
                if trace and not g.isPython3:
                    self.put_log('new_qt_console: connecting...')
                console = connect_qtconsole(
                    self.kernelApp.connection_file,
                    profile=self.kernelApp.profile)
                if console:
                    self.consoles.append(console)
                else:
                    self.put_log('new_qt_console: no console!')
            except OSError as e:
                # Print statements do not work here.
                self.put_log('new_qt_console: failed to connect to console')
                self.put_log(e, raw=True)
            except Exception as e:
                self.put_log('new_qt_console: unexpected exception')
                self.put_log(e)
        return console
    #@+node:ekr.20130930062914.15997: *3* count
    def count(self, event=None):
        self.namespace['app_counter'] += 1
    #@+node:ekr.20130930062914.15998: *3* cleanup_consoles
    def cleanup_consoles(self, event=None):
        for c in self.consoles:
            c.kill()
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
