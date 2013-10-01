# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20120401063816.10072: * @file leoIPython.py
#@@first

'''
Support for the --ipython command-line option and the IPython bridge:
http://leoeditor.com/IPythonBridge.html

This code will run on IPython 1.0 and higher, as well as the IPython 0.x
versions that define the IPKernelApp class.

'''

# This module replaces leo.external.ipy_leo and leo.plugins.internal_ipkernel.

#@@language python
#@@tabwidth -4

#@+<< imports >>
#@+node:ekr.20130930062914.15990: ** << imports >>
import sys
import leo.core.leoGlobals as g
import_trace = False and not g.unitTesting
try:
    from IPython.lib.kernel import connect_qtconsole
    if import_trace: print('ok: IPython.lib.kernel import connect_qtconsole')
except ImportError:
    connect_qtconsole = None
    print('leoIPython.py: can not import connect_qtconsole')
try:
    # First, try the IPython 0.x import.
    from IPython.zmq.ipkernel import IPKernelApp
    if import_trace: print('ok: from IPython.zmq.ipkernel import IPKernelApp')
except ImportError:
    # Next, try the IPython 1.x import.
    try:
        from IPython.kernel.zmq.kernelapp import IPKernelApp
        if import_trace: print('ok: from IPython.kernel.zmq.ipkernel import IPKernelApp')
    except ImportError:
        IPKernelApp = None
        print('leoIPython.py: can not import IPKernelApp')
#@-<< imports >>
#@+others
#@+node:ekr.20130930062914.15993: ** class InternalIPKernel
class InternalIPKernel(object):
    #@+others
    #@+node:ekr.20130930062914.15994: *3* ctor
    # Was init_ipkernel

    def __init__(self, backend='qt'):
        # Start IPython kernel with GUI event loop and pylab support
        self.ipkernel = self.pylab_kernel(backend)
        # To create and track active qt consoles
        self.consoles = []
        
        # This application will also act on the shell user namespace
        self.namespace = self.ipkernel.shell.user_ns
        # Keys present at startup so we don't print the entire pylab/numpy
        # namespace when the user clicks the 'namespace' button
        self._init_keys = set(self.namespace.keys())

        # Example: a variable that will be seen by the user in the shell, and
        # that the GUI modifies (the 'Counter++' button increments it):
        self.namespace['app_counter'] = 0
        #self.namespace['ipkernel'] = self.ipkernel  # dbg
    #@+node:ekr.20130930062914.15992: *3* pylab_kernel
    def pylab_kernel(self,gui):
        """Launch and return an IPython kernel with pylab support for the desired gui
        """
        trace = True
        tag = 'leoIPython.py'
        kernel = IPKernelApp.instance()
        if kernel:
            # pylab is really needed, for Qt event loop integration.
            try:
                kernel.initialize(['python','--pylab=%s' % (gui)])
                    #'--log-level=10'
                if trace: print('%s: kernel: %s' % (tag,kernel))
            except Exception:
                print('%s: kernel.initialize failed!' % tag)
                raise
        else:
            print('%s IPKernelApp.instance failed' % (tag))
        return kernel
    #@+node:ekr.20130930062914.15995: *3* print_namespace
    def print_namespace(self,event=None):
        print("\n***Variables in User namespace***")
        for k, v in self.namespace.iteritems():
            if k not in self._init_keys and not k.startswith('_'):
                print('%s -> %r' % (k, v))
        sys.stdout.flush()
    #@+node:ekr.20130930062914.15996: *3* new_qt_console
    def new_qt_console(self,event=None):
        """start a new qtconsole connected to our kernel"""
        ipk = g.app.ipk
        console = None
        if ipk:
            if not ipk.namespace.get('_leo'):
                ipk.namespace['_leo'] = LeoNameSpace()
            console = connect_qtconsole(
                self.ipkernel.connection_file,
                profile=self.ipkernel.profile)
            if console:
                self.consoles.append(console)
        return console
    #@+node:ekr.20130930062914.15997: *3* count
    def count(self,event=None):
        self.namespace['app_counter'] += 1

    #@+node:ekr.20130930062914.15998: *3* cleanup_consoles
    def cleanup_consoles(self,event=None):
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

    def __init__ (self):
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

    def __set_c(self,c):
        '''Designate the commander to be returned by the getter.'''
        self.update()
        if c in self.commanders_list:
            self.commander = c
        else:
            g.trace(g.callers())
            raise ValueError(c)

    c = property(
        __get_c, __set_c,
        doc = "LeoNameSpace c property")
    #@+node:edward.20130930125732.11822: *3* LeoNS.commanders property
    def __get_commanders(self):
        '''Return the designated commander, or the only open commander.'''
        self.update()
        return self.commanders_list

    commanders = property(
        __get_commanders, None,
        doc = "LeoNameSpace commanders property (read-only)")
    #@+node:ekr.20130930062914.16009: *3* LeoNS.find_c
    def find_c(self,path):
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
    def update (self):
        '''Update the list of available commanders.'''
        self.commanders_list = [frame.c for frame in g.app.windowList]
    #@-others
    
#@+node:ekr.20130930062914.16010: ** exec_helper
def exec_helper(self,event):
    '''This helper is required because an unqualified "exec"
    may not appear in a nested function.
    
    '''
    c = event and event.get('c')
    ipk = g.app.ipk
    ns = ipk.namespace # The actual IPython namespace.
    ipkernel = ipk.ipkernel # IPKernelApp
    shell = ipkernel.shell # ZMQInteractiveShell
    if c and ns is not None:
        try:
            script = g.getScript(c,c.p)
            if 1:
                code = compile(script,c.p.h,'exec')
                shell.run_code(code) # Run using IPython.
            else:
                exec(script,ns) # Run in Leo in the IPython namespace.
        except Exception:
            g.es_exception()
        finally:
            sys.stdout.flush()
            # sys.stderr.flush()
#@-others
#@-leo
