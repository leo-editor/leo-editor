#@+leo-ver=5-thin
#@+node:ekr.20130927071752.11380: * @file internal_ipkernel.py
'''Support for Leo's --ipython option.'''

# This module is no longer used.

#@@language python
#@@tabwidth -4

if 0: # No longer used.

    #@+<< imports >>
    #@+node:ekr.20130408094309.8746: ** << imports >>
    import sys

    import_trace = False
    try:
        from IPython.lib.kernel import connect_qtconsole
        if import_trace: print('ok: IPython.lib.kernel import connect_qtconsole')
    except ImportError:
        connect_qtconsole = None
        print('internal_ipkernel.py: can not import connect_qtconsole')
    try:
        # First, try the IPython 0.x import.
        from IPython.zmq.ipkernel import IPKernelApp
        if import_trace: print('ok: from IPython.zmq.ipkernel import IPKernelApp')
    except ImportError:
        # Next, try the IPython 1.x import.
        try:
            from IPython.kernel.zmq.kernelapp import IPKernelApp
            if import_trace: print('ok: from IPython.zmq.ipkernel import IPKernelApp')
        except ImportError:
            IPKernelApp = None
            print('internal_ipkernel.py: can not import IPKernelApp')
    #@-<< imports >>
    
    #@+others
    #@+node:ekr.20130408094309.8748: ** init
    def init():
        
        return True # Required for Leo's unit tests.
    #@+node:ekr.20130408094309.8749: ** pylab_kernel
    def pylab_kernel(gui):
        """Launch and return an IPython kernel with pylab support for the desired gui
        """
        trace = False
        tag = 'internal_ipkernel.py'
        kernel = IPKernelApp.instance()
        if kernel:
            # pylab is really needed, for Qt event loop integration.
            try:
                kernel.initialize(
                    ['python',
                    '--pylab=%s' % gui,
                    #'--log-level=10'
                ])
                if trace: print('%s: kernel: %s' % (tag,kernel))
            except Exception:
                print('%s: kernel.initialize failed!' % tag)
                raise
        else:
            print('%s IPKernelApp.instance failed' % (tag))
        return kernel
    #@+node:ekr.20130408094309.8750: ** class InternalIPKernel
    class InternalIPKernel(object):
        #@+others
        #@+node:ekr.20130408094309.8751: *3* init_ipkernel

        def init_ipkernel(self, backend):
            # Start IPython kernel with GUI event loop and pylab support
            self.ipkernel = pylab_kernel(backend)
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

        #@+node:ekr.20130408094309.8752: *3* print_namespace
        def print_namespace(self, evt=None):
            print("\n***Variables in User namespace***")
            for k, v in self.namespace.iteritems():
                if k not in self._init_keys and not k.startswith('_'):
                    print('%s -> %r' % (k, v))
            sys.stdout.flush()

        #@+node:ekr.20130408094309.8753: *3* new_qt_console
        def new_qt_console(self, evt=None):
            """start a new qtconsole connected to our kernel"""
            return connect_qtconsole(self.ipkernel.connection_file, profile=self.ipkernel.profile)

        #@+node:ekr.20130408094309.8754: *3* count
        def count(self, evt=None):
            self.namespace['app_counter'] += 1

        #@+node:ekr.20130408094309.8755: *3* cleanup_consoles
        def cleanup_consoles(self, evt=None):
            for c in self.consoles:
                c.kill()
        #@-others
    #@+node:ekr.20130930062914.15971: ** class LeoInterface
    class LeoInterface:

        '''A class to allow full access to Leo from Ipython.

        An instance of this class called leox is typically injected
        into IPython's user_ns namespace by the init-ipython-command.'''

        # pylint: disable=R0923
        # R0923:LeoInterface: Interface not implemented

        def __init__(self,c,g,tag='@ipython-results'):
            self.c = c
            self.g = g
    #@-others
#@-leo
