#@+leo-ver=5-thin
#@+node:ekr.20120401063816.10072: * @file leoIPython.py
#@+<< leoIpython docstring >>
#@+node:ekr.20180326102140.1: ** << leoIpython docstring >>
"""
Support for the --ipython command-line option and the IPython bridge:
https://leo-editor.github.io/leo-editor/IPythonBridge.html

This code will run on IPython 1.0 and higher, as well as the IPython
0.x versions that define the IPKernelApp class.

This module replaces leo.external.ipy_leo and
leo.plugins.internal_ipkernel.

The ``--ipython`` command-line argument creates g.app.ipk, a
*singleton* IPython shell, shared by all IPython consoles.

The startup code injects a single object, _leo, into the IPython namespace.
This object, a LeoNameSpace instance, simplifies dealing with multiple open
Leo commanders.
"""
#@-<< leoIpython docstring >>
#@+<< leoIPython imports >>
#@+node:ekr.20130930062914.15990: ** << leoIPython imports >>
from __future__ import annotations
import sys
from typing import Any, Optional, TYPE_CHECKING
from leo.core import leoGlobals as g

def import_fail(s: str) -> None:
    if not g.unitTesting:
        print(f"leoIpython.py: can not import {s}")

try:
    from ipykernel.connect import connect_qtconsole
except ImportError:
    connect_qtconsole = None
    import_fail('connect_qtconsole')
try:
    from ipykernel.kernelapp import IPKernelApp
except ImportError:
    IPKernelApp = None  # type:ignore
    import_fail('IPKernelApp')

g.app.ipython_inited = IPKernelApp is not None
#@-<< leoIPython imports >>
#@+<< leoIPython annotations >>
#@+node:ekr.20220901090431.1: ** << leoIPython annotations >>
if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent
#@-<< leoIPython annotations >>
#@+others
#@+node:ekr.20190927110149.1: ** @g.command("ipython-new")
@g.command("ipython-new")
def qtshell_f(event: LeoKeyEvent) -> None:
    """ Launch new ipython shell window, associated with the same ipython kernel """
    ipk = getattr(g.app, 'ipk', None)
    if not ipk:
        g.es_print('ipython commands require --ipython')
        return
    g.app.ipk.new_qt_console(event=event)
#@+node:ekr.20190927110150.1: ** @g.command("ipython-exec")
@g.command("ipython-exec")
def ipython_exec(event: LeoKeyEvent) -> None:
    """ Execute script in current node in ipython namespace """
    ipk = getattr(g.app, 'ipk', None)
    if not ipk:
        g.es_print('ipython commands require --ipython')
        return
    c = event and event.get('c')
    if not c:
        g.es_print('no c')
        return
    script = g.getScript(c, c.p, useSentinels=False)
    if not script.strip():
        g.es_print('no script')
        return
    g.app.ipk.run_script(file_name=c.p.h, script=script)
#@+node:ekr.20130930062914.15993: ** class InternalIPKernel
class InternalIPKernel:
    """
    An interface class between Leo's core and IPython.
    Called from LeoQtGui.runWithIpythonKernel()
    """
    #@+others
    #@+node:ekr.20130930062914.15994: *3* ileo.__init__
    def __init__(self, backend: str = 'qt') -> None:
        """Ctor for InternalIPKernal class."""
        # Part 1: create the ivars.
        self.consoles: list[Any] = []  # List of Qt consoles.
        self.kernelApp: InternalIPKernel = None  # The IPKernelApp instance.
        # Keys present at startup so we don't print the entire pylab/numpy
        # namespace when the user clicks the 'namespace' button
        self._init_keys: set[str] = None
        # Start IPython kernel with GUI event loop and pylab support.
        kernelApp = self.pylab_kernel(backend)  # Sets self.kernelApp.
        assert kernelApp == self.kernelApp
        self.namespace: dict[str, Any] = kernelApp.shell.user_ns  # Import the shell namespace.
        self._init_keys = set(self.namespace.keys())
        if 'ipython' in g.app.debug:
            self.namespace['kernelApp'] = kernelApp
            self.namespace['app_counter'] = 0
    #@+node:ekr.20130930062914.15998: *3* ileo.cleanup_consoles
    def cleanup_consoles(self, event: LeoKeyEvent = None) -> None:
        """Kill all ipython consoles.  Called from app.finishQuit."""
        trace = 'ipython' in g.app.debug
        for console in self.consoles:
            # console is a process returned by the Python subprocess module.
            if trace:
                g.trace('kill', console)
            # #1677: neither console.kill nor console.kill works!
            # console.terminate()
            console.kill()
    #@+node:ekr.20130930062914.15997: *3* ileo.count
    def count(self, event: LeoKeyEvent = None) -> None:
        self.namespace['app_counter'] += 1
    #@+node:ekr.20130930062914.15996: *3* ileo.new_qt_console
    def new_qt_console(self, event: LeoKeyEvent = None) -> Any:
        """
        Start a new qtconsole connected to our kernel.

        Called from qt_gui.runWithIpythonKernel.
        """
        trace = 'ipython' in g.app.debug
        console = None
        if not self.namespace.get('_leo'):
            self.namespace['_leo'] = LeoNameSpace()
        if trace:
            self.put_log('new_qt_console: connecting...')
            self.put_log(self.kernelApp.connection_file, raw=True)
        try:
            # #213: leo --ipython fails to connect with python3.5 and jupyter.
            # The connection file has the form kernel-nnn.json.
            # Using the defaults lets connect_qtconsole find the .json file.
            console = connect_qtconsole()  # ipykernel.connect.connect_qtconsole
            if console:
                if trace:
                    g.trace('console:', console)
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
    def pdb(self, message: str = '') -> None:
        """Fall into pdb."""
        if message:
            self.put_stdout(message)
        # pylint: disable=forgotten-debug-statement
        # This works, but there are no IPython sources.
        breakpoint()  # New in Python 3.7.
    #@+node:ekr.20130930062914.15995: *3* ileo.print_namespace
    def print_namespace(self, event: LeoKeyEvent = None) -> None:
        print("\n***Variables in User namespace***")
        for k, v in self.namespace.items():
            if k not in self._init_keys and not k.startswith('_'):
                print(f"{k} -> {v!r}")
        sys.stdout.flush()
    #@+node:ekr.20160308090432.1: *3* ileo.put_log
    def put_log(self, s: str, raw: bool = False) -> None:
        """Put a message to the IPython kernel log."""
        if not raw:
            s = f"[leoIpython.py] {s}"
        if self.kernelApp:
            self.kernelApp.log.info(s)
        else:
            self.put_stdout(s)
    #@+node:ekr.20160331084025.1: *3* ileo.put_stdout
    def put_stdout(self, s: str) -> None:
        """Put s to sys.__stdout__."""
        sys.__stdout__.write(s.rstrip() + '\n')
        sys.__stdout__.flush()
    #@+node:ekr.20160308101536.1: *3* ileo.put_warning
    def put_warning(self, message: Any, raw: bool = False) -> None:
        """
        Put an warning message to the IPython kernel log.
        This will be seen, regardless of Leo's --debug option.
        """
        if not raw:
            message = f"[leoIpython.py] {message}"
        if self.kernelApp:
            self.kernelApp.log.warning(message)
        else:
            self.put_stdout(message)
    #@+node:ekr.20130930062914.15992: *3* ileo.pylab_kernel
    def pylab_kernel(self, gui: Any) -> Any:  # 'gui' arg not used.
        """Launch an IPython kernel with pylab support for the gui."""
        trace = False and not g.unitTesting  # Increased logging.
        # IPKernalApp is a singleton class.
        # Return the singleton instance, creating it if necessary.
        self.kernelApp = kernelApp = IPKernelApp.instance()
        if not kernelApp:
            g.trace('IPKernelApp.instance failed!')
            return None

        # --pylab is no longer needed to create a qt console.
        # --pylab=qt now generates:
            # RuntimeError: Cannot activate multiple GUI eventloops
            # GUI event loop or pylab initialization failed

        # Fails: args = ['python', '--pylab=%s' % (gui)]
        args = ['python', '--pylab']
        if trace:
            args.append('--log-level=20')  # Higher is *quieter*
            # args.append('--debug')
            # Produces a verbose IPython log.
            # '--log-level=10'
            # '--pdb', # User-level debugging
        try:
            # self.pdb()
            kernelApp.initialize(args)
        except Exception:
            sys.stdout = sys.__stdout__
            print('kernelApp.initialize failed!')
            raise
        return kernelApp
    #@+node:ekr.20190927100624.1: *3* ileo.run
    def run(self) -> None:
        """Start the IPython kernel.  This does not return."""
        self.new_qt_console(event=None)
        self.kernelApp.start()  # This does not return.
    #@+node:ekr.20160329053849.1: *3* ileo.run_script
    def run_script(self, file_name: str, script: str) -> None:
        """
        Helper for the ipython-exec command.
        Run the script in the qt console.
        """
        # https://ipython.org/ipython-doc/dev/interactive/qtconsole.html
        # https://github.com/ipython/ipython/blob/master/IPython/core/interactiveshell.py
        # A ZMQInteractiveShell, defined in ipkernel.zmqshell.py,
        # a subclass of InteractiveShell, defined in ipython.core.interactiveshell.py.
        shell = self.kernelApp.shell
        try:
            code = compile(script, file_name, 'exec')
            exec(code, shell.user_global_ns, shell.user_ns)
        except Exception:
            g.es_exception()
    #@+node:ekr.20171115090205.1: *3* ileo.test
    def test(self) -> None:

        from ipykernel.connect import connect_qtconsole
        from ipykernel.kernelapp import IPKernelApp

        kernelApp = IPKernelApp.instance()
        args = ['python', '--pylab=qt', '--log-level=20']
        kernelApp.initialize(args)
        connect_qtconsole()
    #@-others
#@+node:ekr.20130930062914.16002: ** class LeoNameSpace
class LeoNameSpace:
    """
    An interface class passed to IPython that provides easy
    access to "g" and all commanders.

    A convenience property, "c" provides access to the first
    commander in g.app.windowList.
    """

    def __init__(self) -> None:
        """LeoNameSpace ctor."""
        self.commander: Cmdr = None  # The commander returned by the c property.
        self.commanders_list: list[Cmdr] = []  # The list of commanders returned by the commanders property.
        self.g = g
        self.update()
    #@+others
    #@+node:ekr.20130930062914.16006: *3* LeoNS.c property
    def __get_c(self) -> Optional[Cmdr]:
        """Return the designated commander, or the only open commander."""
        self.update()
        if self.commander and self.commander in self.commanders_list:
            return self.commander
        if len(self.commanders_list) == 1:
            return self.commanders_list[0]
        return None

    def __set_c(self, c: Cmdr) -> None:
        """Designate the commander to be returned by the getter."""
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
    def __get_commanders(self) -> list[Cmdr]:
        """Return the designated commander, or the only open commander."""
        self.update()
        return self.commanders_list

    commanders = property(
        __get_commanders, None,
        doc="LeoNameSpace commanders property (read-only)")
    #@+node:ekr.20130930062914.16009: *3* LeoNS.find_c
    def find_c(self, path: str) -> Optional[Cmdr]:
        """Return the commander associated with path, or None."""
        g = self.g
        self.update()
        path = g.os_path_normcase(path)
        short_path = g.shortFileName(path)
        for c in self.commanders_list:
            fn = g.os_path_normcase(c.fileName())
            short_fn = g.shortFileName(fn)
            if fn == path or short_fn == short_path:
                return c
        return None
    #@+node:ekr.20130930062914.16003: *3* LeoNS.update
    def update(self) -> None:
        """Update the list of available commanders."""
        self.commanders_list = [frame.c for frame in g.app.windowList]
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
