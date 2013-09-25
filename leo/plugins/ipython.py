# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20080201143145: * @file ipython.py
#@@first

#@+<< docstring >>
#@+node:ekr.20080201151802: ** << docstring >>
''' Creates a two-way communication (bridge) between Leo
scripts and IPython running in the console from which Leo was launched.

Using this bridge, scripts running in Leo can affect IPython, and vice versa.
In particular, scripts running in IPython can alter Leo outlines!

For full details, see Leo Users Guide:
http://leoeditor.com//IPythonBridge.html

'''
#@-<< docstring >>

# **Important**: this plugin has been replaced by leoIPython.py.

__version__ = '0.9'
#@+<< version history >>
#@+node:ekr.20080201143145.2: ** << version history >>
#@@killcolor
#@+at
# 
# v 0.1: Ideas by Ville M. Vainio, code by EKR.
# 
# v 0.2 EKR: Use g.getScript to synthesize scripts.
# 
# v 0.3 EKR:
# - Moved all code from scripts to this plugin.
# - Added leoInterface and leoInterfaceResults classes.
# - Added createNode function for use by the interface classes.
# - Created minibuffer commands.
# - c.ipythonController is now an official ivar.
# - Docstring now references Chapter 21 of Leo's Users Guide.
# 
# v 0.4 EKR:
# - Disable the command lockout logic for the start-ipython command.
# - (In leoSettings.leo): add shortcuts for ipython commands.
# 
# v 0.5 VMV & EKR:  Added leoInterfaceResults.__getattr__.
# 
# v 0.6 EKR:
# - Inject leox into the user_ns in start-ipython.
#   As a result, there is no need for init_ipython and it has been removed.
# 
# v 0.7 EKR:
# - changed execute-ipython-script to push-to-ipython.
# - Disabled trace of script in push-to-ipython.
# 
# v 0.8 VMV and EKR:
# - This version is based on mods made by VMV.
# - EKR: set sys.argv = [] in startIPython before calling any IPython api.
#   This prevents IPython from trying to load the .leo file.
# 
# v 0.9 EKR: tell where the commands are coming from.
#@-<< version history >>
#@+<< to do >>
#@+node:ekr.20080203092534: ** << to do >>
#@@nocolor
#@+at
# 
# - Read the docs re saving and restoring the IPython namespace.
# 
# - Is it possible to start IPShellEmbed automatically?
# 
#     Calling IPShellEmbed.ipshell() blocks, so it can't be done
#     outside the event loop.  It might be possible to do this in
#     an idle-time handler.
# 
#     If it is possible several more settings would be possible.
#@-<< to do >>
#@+<< imports >>
#@+node:ekr.20080201143145.3: ** << imports >>
import leo.core.leoGlobals as g

import sys

try:
    import IPython.ipapi
    import_ok = True
except ImportError:
    g.error('ipython plugin: can not import IPython.ipapi')
    import_ok = False
except SyntaxError:
    g.error('ipython plugin: syntax error importing IPython.ipapi')
    import_ok = False
    
#@-<< imports >>

# Globals

# IPython IPApi instance. Global, because only one can exist through the whole leo session
gIP = None

#@+others
#@+node:ekr.20080201144219: ** Module-level functions
#@+node:ekr.20080201143145.4: *3* init
def init ():
    
    print('**Important**: Use Leo\'s --ipython option instead of the ipython.py plugin.')

    if not import_ok: return False

    # This plugin depends on the properties of the gui's event loop.
    # It may work for other gui's, but this is not guaranteed.

    if g.app.gui and g.app.gui.guiName() == 'qt' and not g.app.useIpython:
        g.pr('ipython.py plugin disabled ("leo --ipython" enables it)')
        return False

    # Call onCreate after the commander and the key handler exist.
    g.registerHandler('after-create-leo-frame',onCreate)
    g.plugin_signon(__name__)

    return True
#@+node:ekr.20080201143145.5: *3* onCreate
def onCreate (tag, keys):

    c = keys.get('c')

    if not c:
        return

    # Inject the controller into the commander.
    c.ipythonController = ipythonController(c)

    try:
        from leo.external import ipy_leo
    except ImportError:
        return
    try:
        st = ipy_leo._request_immediate_connect
    except AttributeError:
        return

    if st:
        c.ipythonController.startIPython()

#@+node:ekr.20080201143145.6: ** class ipythonController
class ipythonController:

    '''A per-commander controller that manages the
    singleton IPython ipshell instance.'''

    #@+others
    #@+node:ekr.20080204110426: *3* Birth
    #@+node:ekr.20080201143145.7: *4* ctor
    def __init__ (self,c):

        self.c = c
        self.createCommands()
    #@+node:ekr.20080204080848: *4* createCommands
    def createCommands(self):

        '''Create all of the ipython plugin's minibuffer commands.'''

        c = self.c ; k = c.k

        table = (
            ('start-ipython',   self.startIPython),
            ('push-to-ipython', self.pushToIPythonCommand),
        )

        shortcut = None

        if not g.app.unitTesting:
            g.es('ipython plugin...',color='purple')

        for commandName,func in table:
            k.registerCommand (commandName,shortcut,func,pane='all',verbose=True)
    #@+node:ekr.20080201151802.1: *3* Commands
    #@+node:ekr.20080201143319.10: *4* startIPython (rewrite)
    def startIPython(self,event=None):

        '''The start-ipython command'''

        c = self.c
        global gIP

        try:
            from leo.external import ipy_leo
        except ImportError:
            self.error("Error importing ipy_leo")
            return

        if gIP:
            # Just inject a new commander for current document.
            # if we are already running.
            leox = leoInterface(c,g) # inject leox into the namespace.
            ipy_leo.update_commander(leox)
            return

        try:
            api = IPython.ipapi
            leox = leoInterface(c,g)
                # Inject leox into the IPython namespace.

            existing_ip = api.get()
            if existing_ip is None:
                args = c.config.getString('ipython_argv')
                if args is None:
                    argv = ['leo.py']
                else:
                    # force str instead of unicode
                    argv = [str(s) for s in args.split()] 
                if g.app.gui.guiName() == 'qt':
                    # qt ui takes care of the coloring (using scintilla)
                    if '-colors' not in argv:
                        argv.extend(['-colors','NoColor'])
                sys.argv = argv

                self.message('Creating IPython shell.')
                ses = api.make_session()
                gIP = ses.IP.getapi()

                #if g.app.gui.guiName() == 'qt' and not g.app.useIpython:
                if 0:
                    # disable this code for now - --ipython is the one recommended way of using qt + ipython
                    g.es('IPython launch failed. Start Leo with argument "--ipython" on command line!')
                    return
                    #try:
                    #    import ipy_qt.qtipywidget
                    #except:
                    #    g.es('IPython launch failed. Start Leo with argument "--ipython" on command line!')
                    #    raise


                    import textwrap
                    self.qtwidget = ipy_qt.qtipywidget.IPythonWidget()
                    self.qtwidget.set_ipython_session(gIP)
                    self.qtwidget.show()
                    self.qtwidget.viewport.append(textwrap.dedent("""\
                    Qt IPython widget (for Leo). Commands entered on box below.
                    If you want the classic IPython text console, start leo with 'launchLeo.py --gui=qt --ipython'
                    """))

            else:
                # To reuse an old IPython session, you need to launch Leo from IPython by doing:
                #
                # import IPython.Shell
                # IPython.Shell.hijack_tk()
                # %run leo.py  (in leo/leo/src)              
                #
                # Obviously you still need to run launch-ipython (Alt-Shift-I) to make 
                # the document visible for ILeo

                self.message('Reusing existing IPython shell')
                gIP = existing_ip                

            ipy_leo_m = gIP.load('leo.external.ipy_leo')
            ipy_leo_m.update_commander(leox)
            c.inCommand = False # Disable the command lockout logic, just as for scripts.
            # start mainloop only if it's not running already
            if existing_ip is None and g.app.gui.guiName() != 'qt':
                # Does not return until IPython closes!
                ses.mainloop()

        except Exception:
            self.error('exception creating IPython shell')
            g.es_exception()
    #@+node:ekr.20080204111314: *4* pushToIPythonCommand
    def pushToIPythonCommand(self,event=None):

        '''The push-to-ipython command.

        IPython must be started, but need not be inited.'''

        self.pushToIPython(script=None)
    #@+node:ekr.20080201151802.2: *3* Utils...
    #@+node:ekr.20080204075924: *4* error & message
    def error (self,s):

        g.es_print(s)

    def message (self,s):

        g.blue(s)
    #@+node:ekr.20080201150746.2: *4* pushToIPython
    def pushToIPython (self,script=None):
        ''' Push the node to IPython'''
        if not gIP:
            self.startIPython() # Does not return
        else:
            if script:
                gIP.runlines(script)
                return
            c = self.c ; p = c.p
            push = gIP.user_ns['_leo'].push
            c.inCommand = False # Disable the command lockout logic
            push(p)
            return
    #@+node:ekr.20080204083034: *4* started
    def started (self):
        return gIP
    #@-others
#@+node:ekr.20080204103804.3: ** class leoInterface
class leoInterface:

    '''A class to allow full access to Leo from Ipython.

    An instance of this class called leox is typically injected
    into IPython's user_ns namespace by the init-ipython-command.'''

    def __init__(self,c,g,tag='@ipython-results'):
        self.c, self.g = c,g
#@-others
#@-leo
