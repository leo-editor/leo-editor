# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20120401063816.10072: * @file leoIPython.py
#@@first

'''Unified support code for ILeo: the Leo-IPython bridge.

This module replaces both ipython.py and leo/external/ipy_leo.

Users no longer need to activate a plugin. This code will be active
provided that some version of IPyton is found on the Python path.

This module supports all versions of the IPython api:
    - legacy api: IPython to 0.11.
    - new api:    IPython 0.12 and up.
'''

#@@language python
#@@tabwidth -4

print('***** leoIPyhon.py')

#@+<< imports >>
#@+node:ekr.20120401063816.10141: ** << imports >> (leoIPython.py)
import leo.core.leoGlobals as g

import re
import sys
import UserDict

# From ipy_leo.py...

if 1:
    import IPython
    from IPython.core.hooks import CommandChainDispatcher
else:
    # Old imports
    import IPython.ipapi
    import IPython.genutils
    import IPython.generics
    from IPython.hooks import CommandChainDispatcher
    from IPython.ipapi import TryNext 
    import IPython.macro
    import IPython.Shell

# From ipython.py
if 0:
    import_ok = True
else:
    try:
        # import IPython.ipapi
        import IPython.frontend.terminal.ipapp as ipapp
        import IPython.core.interactiveshell as ishell
        import_ok = True
    except ImportError:
        g.es_print('ipython plugin: can not import frontend.terminal.ipapp',color='red')
        import_ok = False
    except SyntaxError:
        g.es_print('ipython plugin: syntax error importing frontend.terminal.ipapp',color='red')
        import_ok = False
        
try:
    import leo.external.ipy_leo as ipy_leo
except ImportError:
    g.es_print('can not import leo.external.ipy_leo',color='red')
    import_ok = False
    
try:
    st = ipy_leo._request_immediate_connect
except AttributeError:
    g.es_print('not found: ipy_leo._request_immediate_connect',color='red')
    import_ok = False
#@-<< imports >>
#@+<< globals >>
#@+node:ekr.20120401063816.10207: ** << globals >> (leoIPyton.py)
# From ipy_leo.py

if 0: # Now defined in IPythonManager class.
    _leo_push_history = set()
    wb = None
    
    # EKR: these were not explicitly inited.
    ip = None
    _request_immediate_connect = None
        # Set below in lleo_f.
    first_launch = True
    c = None
    g = None

# From ipython.py

# IPython IPApi instance. One can exist through the whole leo session.
# gIP = None
#@-<< globals >>
#@+<< docstring >>
#@+node:ekr.20120401063816.10229: ** << docstring >>
''' Creates a two-way communication (bridge) between Leo
scripts and IPython running in the console from which Leo was launched.

Using this bridge, scripts running in Leo can affect IPython, and vice versa.
In particular, scripts running in IPython can alter Leo outlines!

For full details, see Leo Users Guide:
http://webpages.charter.net/edreamleo/IPythonBridge.html

'''
#@-<< docstring >>
#@+<< to do >>
#@+node:ekr.20120401063816.10231: ** << to do >>
#@@nocolor
#@+at
# 
# new
# ===
# 
# Init GlobalIPythonManager in LoadManager class.
# 
# 
# old
# ===
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
#@+<< version history >>
#@+node:ekr.20120401063816.10230: ** << version history >>
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

#@+others
#@+node:ekr.20120401063816.10233: ** Unused
# Module-level functions from ipython.py.


if 0:
    #@+others
    #@+node:ekr.20120401063816.10234: *3* init
    def init ():

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
    #@+node:ekr.20120401063816.10235: *3* onCreate
    def onCreate (tag, keys):

        c = keys.get('c')

        if not c:
            return

        # Inject the controller into the commander.
        c.ipythonController = IpythonController(c)

        # try:
            # from leo.external import ipy_leo
        # except ImportError:
            # return

        # try:
            # st = ipy_leo._request_immediate_connect
        # except AttributeError:
            # return

        st = ipy_leo._request_immediate_connect
        if st:
            c.ipythonController.startIPython()

    #@-others
#@+node:ekr.20120401063816.10142: ** Functions (old)
# These were in ipy_leo.

if 0:
    #@+others
    #@+node:ekr.20120401063816.10154: *3* add_file
    def add_file(self,fname):
        p2 = c.currentPosition().insertAfter()
    #@+node:ekr.20120401063816.10153: *3* add_var
    def add_var(varname):
        r = rootnode()
        try:
            if r is None:
                p2 = g.findNodeAnywhere(c,varname)
            else:
                p2 = g.findNodeInChildren(c, r.p, varname)
            if p2:
                return LeoNode(p2)

            if r is not None:
                p2 = r.p.insertAsLastChild()

            else:
                p2 =  c.currentPosition().insertAfter()

            c.setHeadString(p2,varname)
            return LeoNode(p2)
        finally:
            c.redraw()
    #@+node:ekr.20120401063816.10150: *3* all_cells
    def all_cells():
        global _rootnode
        d = {}
        r = rootnode() 
        if r is not None:
            nodes = r.p.children_iter()
        else:
            nodes = c.allNodes_iter()

        for p in nodes:
            h = p.headString()
            if h.strip() == '@ipy-root':
                # update root node (found it for the first time)
                _rootnode = LeoNode(p)            
                # the next recursive call will use the children of new root
                return all_cells()

            if h.startswith('@a '):
                d[h.lstrip('@a ').strip()] = p.parent().copy()
            elif not valid_attribute(h):
                continue 
            d[h] = p.copy()
        return d    
    #@+node:ekr.20120401063816.10166: *3* edit_macro
    ##### @edit_object_in_leo.when_type(IPython.macro.Macro)
    def edit_macro(obj,varname):
        bod = '_ip.defmacro("""\\\n' + obj.value + '""")'
        node = add_var('Macro_' + varname)
        node.b = bod
        node.go()

    #@+node:ekr.20120401063816.10165: *3* edit_object_in_leo
    ##### @generic
    def edit_object_in_leo(obj, varname):
        """ Make it @cl node so it can be pushed back directly by alt+I """
        node = add_var(varname)
        formatted = format_for_leo(obj)
        if not formatted.startswith('@cl'):
            formatted = '@cl\n' + formatted
        node.b = formatted 
        node.go()

    #@+node:ekr.20120401063816.10146: *3* es
    from IPython.external.simplegeneric import generic 
    import pprint

    def es(s):    
        g.es(s, tabName = 'IPython')
        pass
    #@+node:ekr.20120401063816.10155: *3* eval_body
    def eval_body(body):
        try:
            val = ip.ev(body)
        except:
            # just use stringlist if it's not completely legal python expression
            val = IPython.genutils.SList(body.splitlines())
        return val 

    #@+node:ekr.20120401063816.10151: *3* eval_node
    def eval_node(n):
        body = n.b    
        if not body.startswith('@cl'):
            # plain python repr node, just eval it
            return ip.ev(n.b)
        # @cl nodes deserve special treatment:
        # first eval the first line (minus cl),
        # then use it to call the rest of body.
        first, rest = body.split('\n',1)
        tup = first.split(None, 1)
        # @cl alone SPECIAL USE-> dump var to user_ns
        if len(tup) == 1:
            val = ip.ev(rest)
            ip.user_ns[n.h] = val
            es("%s = %s" % (n.h, repr(val)[:20]  )) 
            return val

        cl, hd = tup 

        xformer = ip.ev(hd.strip())
        es('Transform w/ %s' % repr(xformer))
        return xformer(rest, n)
    #@+node:ekr.20120401063816.10147: *3* format_for_leo
    @generic
    def format_for_leo(obj):
        """ Convert obj to string representiation (for editing in Leo)"""
        return pprint.pformat(obj)

    # Just an example - note that this is a bad to actually do!
    #@verbatim
    #@format_for_leo.when_type(list)
    #def format_list(obj):
    #    return "\n".join(str(s) for s in obj)
    #@+node:ekr.20120401063816.10167: *3* get_history
    def get_history(hstart = 0):
        res = []
        ohist = ip.IP.output_hist 

        for idx in range(hstart, len(ip.IP.input_hist)):
            val = ohist.get(idx,None)
            has_output = True
            inp = ip.IP.input_hist_raw[idx]
            if inp.strip():
                res.append('In [%d]: %s' % (idx, inp))
            if val:
                res.append(pprint.pformat(val))
                res.append('\n')    
        return ''.join(res)
    #@+node:ekr.20120401063816.10172: *3* ileo_pre_prompt_hook
    def ileo_pre_prompt_hook(self):
        # this will fail if leo is not running yet
        try:
            c.outerUpdate()
        except (NameError, AttributeError):
            pass
        raise TryNext

    #@+node:ekr.20120401063816.10168: *3* lee_f
    def lee_f(self,s):
        """ Open file(s)/objects in Leo

        - %lee hist -> open full session history in leo
        - Takes an object. l = [1,2,"hello"]; %lee l.
          Alt+I in leo pushes the object back
        - Takes an mglob pattern, e.g. '%lee *.cpp' or %lee 'rec:*.cpp'
        - Takes input history indices:  %lee 4 6-8 10 12-47
        """
        import os

        try:
            if s == 'hist':
                wb.ipython_history.b = get_history()
                wb.ipython_history.go()
                return

            if s and s[0].isdigit():
                # numbers; push input slices to leo
                lines = self.extract_input_slices(s.strip().split(), True)
                v = add_var('stored_ipython_input')
                v.b = '\n'.join(lines)
                return

            # try editing the object directly
            obj = ip.user_ns.get(s, None)
            if obj is not None:
                edit_object_in_leo(obj,s)
                return

            # if it's not object, it's a file name / mglob pattern
            from IPython.external import mglob

            files = (os.path.abspath(f) for f in mglob.expand(s))
            for fname in files:
                p = g.findNodeAnywhere(c,'@auto ' + fname)
                if not p:
                    p = c.currentPosition().insertAfter()

                p.setHeadString('@auto ' + fname)
                if os.path.isfile(fname):
                    c.setBodyString(p,open(fname).read())
                c.selectPosition(p)
            print("Editing file(s), \
                press ctrl+shift+w in Leo to write @auto nodes")
        finally:
            c.redraw()
    #@+node:ekr.20120401063816.10169: *3* leoref_f
    def leoref_f(self,s):
        """ Quick reference for ILeo """
        import textwrap
        print(textwrap.dedent("""\
        %lee file/object - open file / object in leo
        %lleo Launch leo (use if you started ipython first!)
        wb.foo.v  - eval node foo (i.e. headstring is 'foo' or '@ipy foo')
        wb.foo.v = 12 - assign to body of node foo
        wb.foo.b - read or write the body of node foo
        wb.foo.l - body of node foo as string list

        for el in wb.foo:
          print el.v

        """
        ))
    #@+node:ekr.20120401063816.10175: *3* lleo_f
    def lleo_f(selg,  args):
        """ Launch leo from within IPython

        This command will return immediately when Leo has been
        launched, leaving a Leo session that is connected 
        with current IPython session (once you press alt+I in leo)

        Usage::
          lleo foo.leo
          lleo 
        """

        import shlex, sys,os
        argv = shlex.split(args)

        # when run without args, leo will open ipython_notebook for 
        # quick note taking / experimentation

        if not argv:
            argv = [os.path.join(ip.options.ipythondir,'ipython_notebook.leo')]

        sys.argv = ['leo'] + argv
        # if this var exists and is true, leo will "launch" (connect)
        # ipython immediately when it's started
        global _request_immediate_connect
        _request_immediate_connect = True
        import leo.core.runLeo
        leo.core.runLeo.run()

    #@+node:ekr.20120401063816.10176: *3* lno_f
    def lno_f(self, arg):
        """ %lno [note text]

        Gather quick notes to leo notebook

        """

        import time
        try:
            scr = wb.Scratch
        except AttributeError:
            print("No leo yet, attempt launch of notebook...")
            lleo_f(self,'')
            scr = wb.Scratch

        child = scr.get(arg, None)
        if child is None:
            scr[arg] = time.asctime()
            child = scr[arg]

        child.go()
    #@+node:ekr.20120401063816.10177: *3* lshadow_f
    def lshadow_f(self, arg):
        """ lshadow [path] 

        Create shadow nodes for path (default .)

        """
        if not arg.split():
            arg = '.'

        p = c.currentPosition().insertAfter()
        c.setCurrentPosition(p)
        shadow_walk(arg)
        c.redraw()
    #@+node:ekr.20120401063816.10171: *3* mb_completer
    def mb_completer(self,event):
        """ Custom completer for minibuffer """
        cmd_param = event.line.split()
        if event.line.endswith(' '):
            cmd_param.append('')
        if len(cmd_param) > 2:
            return ip.IP.Completer.file_matches(event.symbol)

        # 2010/02/04: per 2to3
        cmds = list(c.commandsDict.keys())
        cmds.sort()
        return cmds

    #@+node:ekr.20120401063816.10170: *3* mb_f
    def mb_f(self, arg):
        """ Execute leo minibuffer commands 

        Example:
         mb save-to-file
        """
        c.executeMinibufferCommand(arg)
    #@+node:ekr.20120401063816.10179: *3* mkbutton
    def mkbutton(text, node_to_push):
        ib = c.frame.getIconBarObject()
        ib.add(text = text, command = node_to_push.ipush)

    #@+node:ekr.20120401063816.10156: *3* push... (ipy_leo)
    #@+node:ekr.20120401063816.10157: *4* expose_ileo_push
    def expose_ileo_push(f, prio = 0):

        push_from_leo.add(f, prio)
    #@+node:ekr.20120401063816.10158: *4* push_cl_node
    def push_cl_node(node):
        """ If node starts with @cl, eval it

        The result is put as last child of @ipy-results node, if it exists
        """
        if not node.b.startswith('@cl'):
            raise TryNext

        p2 = g.findNodeAnywhere(c,'@ipy-results')
        val = node.v
        if p2:
            es("=> @ipy-results")
            LeoNode(p2).v = val
        es(val)

    #@+node:ekr.20120401063816.10159: *4* push_ev_node
    def push_ev_node(node):
        """ If headline starts with @ev, eval it and put result in body """
        if not node.h.startswith('@ev '):
            raise TryNext
        expr = node.h.lstrip('@ev ')
        es('ipy eval ' + expr)
        res = ip.ev(expr)
        node.v = res

    #@+node:ekr.20120401063816.10160: *4* push_from_leo
    push_from_leo = CommandChainDispatcher()
    #@+node:ekr.20120401063816.10161: *4* push_ipython_script
    def push_ipython_script(node):
        """ Execute the node body in IPython,
        as if it was entered in interactive prompt """
        try:
            ohist = ip.IP.output_hist 
            hstart = len(ip.IP.input_hist)
            script = node.script()

            # The current node _p needs to handle
            # wb.require() and recursive ipushes.
            old_p = ip.user_ns.get('_p',None)
            ip.user_ns['_p'] = node
            ip.runlines(script)
            ip.user_ns['_p'] = old_p
            if old_p is None:
                del ip.user_ns['_p']

            has_output = False
            for idx in range(hstart,len(ip.IP.input_hist)):
                val = ohist.get(idx,None)
                if val is None:
                    continue
                has_output = True
                inp = ip.IP.input_hist[idx]
                if inp.strip():
                    es('In: %s' % (inp[:40], ))

                es('<%d> %s' % (idx, pprint.pformat(ohist[idx],width = 40)))

            if not has_output:
                es('ipy run: %s (%d LL)' %( node.h,len(script)))
        finally:
            c.redraw()
    #@+node:ekr.20120401063816.10162: *4* push_mark_req
    def push_mark_req(node):
        """ This should be the first one that gets called.

        It will mark the node as 'pushed', for wb.require.
        """
        _leo_push_history.add(node.h)
        raise TryNext
    #@+node:ekr.20120401063816.10163: *4* push_plain_python
    def push_plain_python(node):
        if not node.h.endswith('P'):
            raise TryNext
        script = node.script()
        lines = script.count('\n')
        try:
            # exec script in ip.user_ns
            # 2010/02/04: per 2to3
            exec(script,ip.user_ns)
        except:
            print(" -- Exception in script:\n"+script + "\n --")
            raise
        es('ipy plain: %s (%d LL)' % (node.h,lines))
    #@+node:ekr.20120401063816.10164: *4* push_position_from_leo ***
    def push_position_from_leo(p):
        
        try:
            # push_from_leo(LeoNode(p))
            n = LeoNode(p)
            n.ipush()

        except AttributeError as e:
            if e.args == ("Commands instance has no attribute 'frame'",):
                es("Error: ILeo not associated with .leo document")
                es("Press alt+shift+I to fix!")
            else:
                raise
            
    #@+node:ekr.20120401063816.10149: *3* rootnode
    _rootnode = None

    def rootnode():
        """ Get ileo root node (@ipy-root) 

        if node has become invalid or has not been set, return None

        Note that the root is the *first* @ipy-root item found    
        """
        global _rootnode
        if _rootnode is None:
            return None
        if c.positionExists(_rootnode.p):
            return _rootnode
        _rootnode = None
        return None  
    #@+node:ekr.20120401063816.10174: *3* run_leo_startup_node
    def run_leo_startup_node():
        p = g.findNodeAnywhere(c,'@ipy-startup')
        if p:
            print("Running @ipy-startup nodes")
            for n in LeoNode(p):
                push_from_leo(n)

    #@+node:ekr.20120401063816.10178: *3* shadow_walk
    def shadow_walk(directory, parent=None, isroot=True):
        """ source: http://leo.zwiki.org/CreateShadows

        """

        from os import listdir
        from os.path import join, abspath, basename, normpath, isfile
        from fnmatch import fnmatch

        RELATIVE_PATHS = False

        patterns_to_ignore = [
            '*.pyc', '*.leo', '*.gif', '*.png', '*.jpg', '*.json']

        match = lambda s: any(fnmatch(s, p) for p in patterns_to_ignore)

        is_ignorable = lambda s: any([ s.startswith('.'), match(s) ])

        p = c.currentPosition()

        if not RELATIVE_PATHS: directory = abspath(directory)
        if isroot:
            body = "@path %s" % normpath(directory)
            c.setHeadString(p, body)
        for name in listdir(directory):
            if is_ignorable(name):
                continue
            path = join(directory, name)
            if isfile(path):
                g.es('file:', path)
                headline = '@shadow %s' % basename(path)
                if parent:
                    node = parent
                else:
                    node = p
                child = node.insertAsLastChild()
                child.initHeadString(headline)
            else:
                g.es('dir:', path)
                headline = basename(path)
                body = "@path %s" % normpath(path)
                if parent:
                    node = parent
                else:
                    node = p
                child = node.insertAsLastChild()
                child.initHeadString(headline)
                child.initBodyString(body)
                shadow_walk(path, parent=child, isroot=False)
    #@+node:ekr.20120401063816.10173: *3* show_welcome
    def show_welcome():
        print("------------------")
        print("Welcome to Leo-enabled IPython session!")
        print("Try %leoref for quick reference.")
        # import IPython.platutils
        # IPython.platutils.set_term_title('ILeo')
        # IPython.platutils.freeze_term_title()

    #@+node:ekr.20120401063816.10148: *3* valid_attribute
    attribute_re = re.compile('^[a-zA-Z_][a-zA-Z0-9_]*$')

    def valid_attribute(s):
        return attribute_re.match(s)    
    #@+node:ekr.20120401063816.10152: *3* workbook_complete
    ### @IPython.generics.complete_object.when_type(LeoWorkbook)
    def workbook_complete(obj, prev):
        # 2010/02/04: per 2to3
        return list(all_cells().keys()) + [
            s for s in prev if not s.startswith('_')]
    #@-others
#@+node:ekr.20120401144849.10109: ** Functions
# These are supposed to have "self" as the first argument.
#@+node:ekr.20120401144849.10085: *3* ileo_pre_prompt_hook
def ileo_pre_prompt_hook(self):

    # this will fail if leo is not running yet
    try:
        c.outerUpdate()
    except (NameError, AttributeError):
        pass
    raise TryNext
#@+node:ekr.20120401144849.10086: *3* lee_f
def lee_f(self,s):
    
    """ Open file(s)/objects in Leo

    - %lee hist -> open full session history in leo
    - Takes an object. l = [1,2,"hello"]; %lee l.
      Alt+I in leo pushes the object back
    - Takes an mglob pattern, e.g. '%lee *.cpp' or %lee 'rec:*.cpp'
    - Takes input history indices:  %lee 4 6-8 10 12-47
    """
    import os

    try:
        if s == 'hist':
            wb.ipython_history.b = get_history()
            wb.ipython_history.go()
            return

        if s and s[0].isdigit():
            # numbers; push input slices to leo
            lines = self.extract_input_slices(s.strip().split(), True)
            v = add_var('stored_ipython_input')
            v.b = '\n'.join(lines)
            return

        # try editing the object directly
        obj = ip.user_ns.get(s, None)
        if obj is not None:
            edit_object_in_leo(obj,s)
            return

        # if it's not object, it's a file name / mglob pattern
        from IPython.external import mglob

        files = (os.path.abspath(f) for f in mglob.expand(s))
        for fname in files:
            p = g.findNodeAnywhere(c,'@auto ' + fname)
            if not p:
                p = c.currentPosition().insertAfter()

            p.setHeadString('@auto ' + fname)
            if os.path.isfile(fname):
                c.setBodyString(p,open(fname).read())
            c.selectPosition(p)
        print("Editing file(s), \
            press ctrl+shift+w in Leo to write @auto nodes")
    finally:
        c.redraw()
#@+node:ekr.20120401144849.10087: *3* leoref_f
def leoref_f(self,s):
    """ Quick reference for ILeo """
    import textwrap
    print(textwrap.dedent("""\
    %lee file/object - open file / object in leo
    %lleo Launch leo (use if you started ipython first!)
    wb.foo.v  - eval node foo (i.e. headstring is 'foo' or '@ipy foo')
    wb.foo.v = 12 - assign to body of node foo
    wb.foo.b - read or write the body of node foo
    wb.foo.l - body of node foo as string list

    for el in wb.foo:
      print el.v

    """
    ))
#@+node:ekr.20120401144849.10088: *3* lleo_f
def lleo_f(selg,  args):
    """ Launch leo from within IPython

    This command will return immediately when Leo has been
    launched, leaving a Leo session that is connected 
    with current IPython session (once you press alt+I in leo)

    Usage::
      lleo foo.leo
      lleo 
    """

    import shlex, sys,os
    argv = shlex.split(args)

    # when run without args, leo will open ipython_notebook for 
    # quick note taking / experimentation

    if not argv:
        argv = [os.path.join(ip.options.ipythondir,'ipython_notebook.leo')]

    sys.argv = ['leo'] + argv
    # if this var exists and is true, leo will "launch" (connect)
    # ipython immediately when it's started
    global _request_immediate_connect
    _request_immediate_connect = True
    import leo.core.runLeo
    leo.core.runLeo.run()

#@+node:ekr.20120401144849.10089: *3* lno_f
def lno_f(self, arg):
    """ %lno [note text]

    Gather quick notes to leo notebook

    """

    import time
    try:
        scr = wb.Scratch
    except AttributeError:
        print("No leo yet, attempt launch of notebook...")
        lleo_f(self,'')
        scr = wb.Scratch

    child = scr.get(arg, None)
    if child is None:
        scr[arg] = time.asctime()
        child = scr[arg]

    child.go()
#@+node:ekr.20120401144849.10090: *3* lshadow_f
def lshadow_f(self, arg):
    """ lshadow [path] 

    Create shadow nodes for path (default .)

    """
    if not arg.split():
        arg = '.'

    p = c.currentPosition().insertAfter()
    c.setCurrentPosition(p)
    shadow_walk(arg)
    c.redraw()
#@+node:ekr.20120401144849.10038: ** class ILeoCommands
class ILeoCommands:
    
    def __init__ (self,c):
        
        self._rootnode = None
        self.attribute_re = re.compile('^[a-zA-Z_][a-zA-Z0-9_]*$')
        self.c = c
#@+node:ekr.20120401144849.10075: *3* add_file
def add_file(self,fname):
    p2 = c.currentPosition().insertAfter()
#@+node:ekr.20120401144849.10076: *3* add_var
def add_var(varname):
    r = rootnode()
    try:
        if r is None:
            p2 = g.findNodeAnywhere(c,varname)
        else:
            p2 = g.findNodeInChildren(c, r.p, varname)
        if p2:
            return LeoNode(p2)

        if r is not None:
            p2 = r.p.insertAsLastChild()

        else:
            p2 =  c.currentPosition().insertAfter()

        c.setHeadString(p2,varname)
        return LeoNode(p2)
    finally:
        c.redraw()
#@+node:ekr.20120401144849.10077: *3* all_cells
def all_cells():
    global _rootnode
    d = {}
    r = rootnode() 
    if r is not None:
        nodes = r.p.children_iter()
    else:
        nodes = c.allNodes_iter()

    for p in nodes:
        h = p.headString()
        if h.strip() == '@ipy-root':
            # update root node (found it for the first time)
            _rootnode = LeoNode(p)            
            # the next recursive call will use the children of new root
            return all_cells()

        if h.startswith('@a '):
            d[h.lstrip('@a ').strip()] = p.parent().copy()
        elif not valid_attribute(h):
            continue 
        d[h] = p.copy()
    return d    
#@+node:ekr.20120401144849.10078: *3* edit_macro
##### @edit_object_in_leo.when_type(IPython.macro.Macro)
def edit_macro(obj,varname):
    bod = '_ip.defmacro("""\\\n' + obj.value + '""")'
    node = add_var('Macro_' + varname)
    node.b = bod
    node.go()

#@+node:ekr.20120401144849.10079: *3* edit_object_in_leo
##### @generic
def edit_object_in_leo(obj, varname):
    """ Make it @cl node so it can be pushed back directly by alt+I """
    node = add_var(varname)
    formatted = format_for_leo(obj)
    if not formatted.startswith('@cl'):
        formatted = '@cl\n' + formatted
    node.b = formatted 
    node.go()

#@+node:ekr.20120401144849.10080: *3* es
from IPython.external.simplegeneric import generic 
import pprint

def es(s):    
    g.es(s, tabName = 'IPython')
    pass
#@+node:ekr.20120401144849.10081: *3* eval_body
def eval_body(body):
    try:
        val = ip.ev(body)
    except:
        # just use stringlist if it's not completely legal python expression
        val = IPython.genutils.SList(body.splitlines())
    return val 

#@+node:ekr.20120401144849.10082: *3* eval_node
def eval_node(n):
    body = n.b    
    if not body.startswith('@cl'):
        # plain python repr node, just eval it
        return ip.ev(n.b)
    # @cl nodes deserve special treatment:
    # first eval the first line (minus cl),
    # then use it to call the rest of body.
    first, rest = body.split('\n',1)
    tup = first.split(None, 1)
    # @cl alone SPECIAL USE-> dump var to user_ns
    if len(tup) == 1:
        val = ip.ev(rest)
        ip.user_ns[n.h] = val
        es("%s = %s" % (n.h, repr(val)[:20]  )) 
        return val

    cl, hd = tup 

    xformer = ip.ev(hd.strip())
    es('Transform w/ %s' % repr(xformer))
    return xformer(rest, n)
#@+node:ekr.20120401144849.10083: *3* format_for_leo
@generic
def format_for_leo(obj):
    """ Convert obj to string representiation (for editing in Leo)"""
    return pprint.pformat(obj)

# Just an example - note that this is a bad to actually do!
#@verbatim
#@format_for_leo.when_type(list)
#def format_list(obj):
#    return "\n".join(str(s) for s in obj)
#@+node:ekr.20120401144849.10084: *3* get_history
def get_history(hstart = 0):
    res = []
    ohist = ip.IP.output_hist 

    for idx in range(hstart, len(ip.IP.input_hist)):
        val = ohist.get(idx,None)
        has_output = True
        inp = ip.IP.input_hist_raw[idx]
        if inp.strip():
            res.append('In [%d]: %s' % (idx, inp))
        if val:
            res.append(pprint.pformat(val))
            res.append('\n')    
    return ''.join(res)
#@+node:ekr.20120401144849.10091: *3* mb_completer
def mb_completer(self,event):
    """ Custom completer for minibuffer """
    cmd_param = event.line.split()
    if event.line.endswith(' '):
        cmd_param.append('')
    if len(cmd_param) > 2:
        return ip.IP.Completer.file_matches(event.symbol)

    # 2010/02/04: per 2to3
    cmds = list(c.commandsDict.keys())
    cmds.sort()
    return cmds

#@+node:ekr.20120401144849.10092: *3* mb_f
def mb_f(self, arg):
    """ Execute leo minibuffer commands 

    Example:
     mb save-to-file
    """
    c.executeMinibufferCommand(arg)
#@+node:ekr.20120401144849.10093: *3* mkbutton
def mkbutton(self,text, node_to_push):
    
    ib = c.frame.getIconBarObject()
    ib.add(text=text,command=node_to_push.ipush)

#@+node:ekr.20120401144849.10094: *3* push...
#@+node:ekr.20120401144849.10095: *4* expose_ileo_push
def expose_ileo_push(self,f,priority=0):

    self.push_from_leo.add(f,priority)
#@+node:ekr.20120401144849.10096: *4* push_cl_node
def push_cl_node(self,node):

    """ If node starts with @cl, eval it

    The result is put as last child of @ipy-results node, if it exists
    """

    if not node.b.startswith('@cl'):
        raise TryNext

    p2 = g.findNodeAnywhere(c,'@ipy-results')
    val = node.v
    if p2:
        es("=> @ipy-results")
        LeoNode(p2).v = val
    self.es(val)

#@+node:ekr.20120401144849.10097: *4* push_ev_node
def push_ev_node(self,node):
    
    """ If headline starts with @ev, eval it and put result in body """

    if not node.h.startswith('@ev '):
        raise TryNext
    expr = node.h.lstrip('@ev ')
    self.es('ipy eval ' + expr)
    res = ip.ev(expr)
    node.v = res

#@+node:ekr.20120401144849.10098: *4* push_from_leo
#push_from_leo = CommandChainDispatcher()

def push_from_leo(self,args):
    
    CommandChainDispatcher(args)
#@+node:ekr.20120401144849.10099: *4* push_ipython_script
def push_ipython_script(self,node):
    """ Execute the node body in IPython,
    as if it was entered in interactive prompt """
    try:
        ohist = ip.IP.output_hist 
        hstart = len(ip.IP.input_hist)
        script = node.script()

        # The current node _p needs to handle
        # wb.require() and recursive ipushes.
        old_p = ip.user_ns.get('_p',None)
        ip.user_ns['_p'] = node
        ip.runlines(script)
        ip.user_ns['_p'] = old_p
        if old_p is None:
            del ip.user_ns['_p']

        has_output = False
        for idx in range(hstart,len(ip.IP.input_hist)):
            val = ohist.get(idx,None)
            if val is None:
                continue
            has_output = True
            inp = ip.IP.input_hist[idx]
            if inp.strip():
                es('In: %s' % (inp[:40], ))

            self.es('<%d> %s' % (idx, pprint.pformat(ohist[idx],width = 40)))

        if not has_output:
            self.es('ipy run: %s (%d LL)' %( node.h,len(script)))
    finally:
        c.redraw()
#@+node:ekr.20120401144849.10100: *4* push_mark_req
def push_mark_req(self,node):
    """ This should be the first one that gets called.

    It will mark the node as 'pushed', for wb.require.
    """
    _leo_push_history.add(node.h)
    raise TryNext
#@+node:ekr.20120401144849.10101: *4* push_plain_python
def push_plain_python(self,node):
    if not node.h.endswith('P'):
        raise TryNext
    script = node.script()
    lines = script.count('\n')
    try:
        # exec script in ip.user_ns
        # 2010/02/04: per 2to3
        exec(script,ip.user_ns)
    except:
        print(" -- Exception in script:\n"+script + "\n --")
        raise
    es('ipy plain: %s (%d LL)' % (node.h,lines))
#@+node:ekr.20120401144849.10102: *4* push_position_from_leo ***
def push_position_from_leo(self,p):
    
    try:
        # push_from_leo(LeoNode(p))
        n = LeoNode(p)
        n.ipush()

    except AttributeError as e:
        if e.args == ("Commands instance has no attribute 'frame'",):
            es("Error: ILeo not associated with .leo document")
            es("Press alt+shift+I to fix!")
        else:
            raise
        
#@+node:ekr.20120401144849.10103: *3* rootnode
def rootnode(self):
    """ Get ileo root node (@ipy-root) 

    if node has become invalid or has not been set, return None

    Note that the root is the *first* @ipy-root item found    
    """

    if self._rootnode is None:
        return None
    if c.positionExists(_rootnode.p):
        return self._rootnode
    self._rootnode = None
    return None  
#@+node:ekr.20120401144849.10104: *3* run_leo_startup_node
def run_leo_startup_node(self):
    
    c = self.c
    p = g.findNodeAnywhere(c,'@ipy-startup')
    if p:
        print("Running @ipy-startup nodes")
        for n in LeoNode(p):
            push_from_leo(n)

#@+node:ekr.20120401144849.10105: *3* shadow_walk
def shadow_walk(self,directory, parent=None, isroot=True):
    """ source: http://leo.zwiki.org/CreateShadows

    """

    from os import listdir
    from os.path import join, abspath, basename, normpath, isfile
    from fnmatch import fnmatch

    RELATIVE_PATHS = False

    patterns_to_ignore = [
        '*.pyc', '*.leo', '*.gif', '*.png', '*.jpg', '*.json']

    match = lambda s: any(fnmatch(s, p) for p in patterns_to_ignore)

    is_ignorable = lambda s: any([ s.startswith('.'), match(s) ])

    p = c.currentPosition()

    if not RELATIVE_PATHS: directory = abspath(directory)
    if isroot:
        body = "@path %s" % normpath(directory)
        c.setHeadString(p, body)
    for name in listdir(directory):
        if is_ignorable(name):
            continue
        path = join(directory, name)
        if isfile(path):
            g.es('file:', path)
            headline = '@shadow %s' % basename(path)
            if parent:
                node = parent
            else:
                node = p
            child = node.insertAsLastChild()
            child.initHeadString(headline)
        else:
            g.es('dir:', path)
            headline = basename(path)
            body = "@path %s" % normpath(path)
            if parent:
                node = parent
            else:
                node = p
            child = node.insertAsLastChild()
            child.initHeadString(headline)
            child.initBodyString(body)
            shadow_walk(path, parent=child, isroot=False)
#@+node:ekr.20120401144849.10106: *3* show_welcome
def show_welcome(self):
    print("------------------")
    print("Welcome to Leo-enabled IPython session!")
    print("Try %leoref for quick reference.")
    # import IPython.platutils
    # IPython.platutils.set_term_title('ILeo')
    # IPython.platutils.freeze_term_title()

#@+node:ekr.20120401144849.10107: *3* valid_attribute
def valid_attribute(self,s):
    return self.attribute_re.match(s)    
#@+node:ekr.20120401144849.10108: *3* workbook_complete
### @IPython.generics.complete_object.when_type(LeoWorkbook)
def workbook_complete(self,obj, prev):
    # 2010/02/04: per 2to3
    return list(all_cells().keys()) + [
        s for s in prev if not s.startswith('_')]
#@+node:ekr.20120401082519.10036: ** class GlobalIPythonManager
class GlobalIPythonManager:
    
    '''A class to manage global IPython data'''
    
    #@+others
    #@+node:ekr.20120401082519.10037: *3* gipm.ctor
    def __init__ (self):
        
        self.first_launch = True
        self.ip = None
        self.push_history = set()
        self.request_immediate_connect = None
        self.wb = None
    #@+node:ekr.20120401063816.10144: *3* gipm.init_ipython 
    def init_ipython(ipy):
        
        """ This will be run by _ip.load('ipy_leo') 

        Leo still needs to run update_commander() after this.

        """
        
        global ip
        ip = ipy
        
        #### IPython.Shell.hijack_tk()
        ip.set_hook('complete_command', mb_completer, str_key = '%mb')
        ip.expose_magic('mb',mb_f)
        ip.expose_magic('lee',lee_f)
        ip.expose_magic('leoref',leoref_f)
        ip.expose_magic('lleo',lleo_f)    
        ip.expose_magic('lshadow', lshadow_f)
        ip.expose_magic('lno', lno_f)    
        # Note that no other push command should EVER have lower than 0
        expose_ileo_push(push_mark_req, -1)
        expose_ileo_push(push_cl_node,100)
        # this should be the LAST one that will be executed,
        # and it will never raise TryNext.
        expose_ileo_push(push_ipython_script, 1000)
        expose_ileo_push(push_plain_python, 100)
        expose_ileo_push(push_ev_node, 100)
        ip.set_hook('pre_prompt_hook', ileo_pre_prompt_hook)     
        global wb
        wb = LeoWorkbook()
        ip.user_ns['wb'] = wb
    #@+node:ekr.20120401063816.10145: *3* gipm.update_commander
    # first_launch = True

    # c,g = None, None

    def update_commander(new_leox,new_ip=None):
        """ Set the Leo commander to use

        This will be run every time Leo does ipython-launch; basically,
        when the user switches the document he is focusing on, he should do
        ipython-launch to tell ILeo what document the commands apply to.

        """

        global first_launch
        if first_launch:
            show_welcome()
            first_launch = False

        global c,g
        c,g = new_leox.c, new_leox.g
        print("Set Leo Commander: %s" % c.frame.getTitle())
        
        global ip
        if not ip:
            if new_ip:
                # g.trace('***** setting ip',new_ip)
                ip = new_ip
            else:
                g.trace('***** no ip')
                return

        # will probably be overwritten by user,
        # but handy for experimentation early on.
        ip.user_ns['c'] = c
        ip.user_ns['g'] = g
        ip.user_ns['_leo'] = new_leox

        new_leox.push = push_position_from_leo
        run_leo_startup_node()
        ip.user_ns['_prompt_title'] = 'ileo'
    #@-others
#@+node:ekr.20120401063816.10236: ** class IpythonController
class IpythonController:

    '''A per-commander controller that manages the
    singleton IPython ipshell instance.'''

    #@+others
    #@+node:ekr.20120401063816.10237: *3* Birth
    #@+node:ekr.20120401063816.10238: *4* ctor
    def __init__ (self,c):

        self.c = c
        self.createCommands()
    #@+node:ekr.20120401063816.10239: *4* createCommands
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
    #@+node:ekr.20120401063816.10240: *3* Commands
    #@+node:ekr.20120401063816.10241: *4* startIPython (not used)
    def startIPython(self,event=None):

        '''The start-ipython command'''

        c = self.c
        
        g.es_print('Can not start IPython from Leo yet')
        return
        
        # global gIP

        # try:
            # from leo.external import ipy_leo
        # except ImportError:
            # self.error("Error importing ipy_leo")
            # return

        # if gIP:
        ip = ishell.instance()
        if ip:
            # Just inject a new commander for current document.
            # if we are already running.
            leox = leoInterface(c,g) # inject leox into the namespace.
            ipy_leo.update_commander(leox)
        else:
            g.es_print('use --ipython option to start IPython.')
            
            
        if 0: ### Old code

            try:
                leox = leoInterface(c,g)
                    # Inject leox into the IPython namespace.
        
                args = c.config.getString('ipython_argv')
                if args is None:
                    ### argv = ['leo.py']
                    argv =  ['ipython']
                else:
                    # force str instead of unicode
                    argv = [str(s) for s in args.split()]
        
                if g.app.gui.guiName() == 'qt':
                    # qt ui takes care of the coloring (using scintilla)
                    if '-colors' not in argv:
                        argv.extend(['-colors','NoColor'])
        
                sys.argv = argv
        
                self.message('Creating IPython shell.')
                
                # New code
                # sys.argv =  ['ipython']
                ipapp.launch_new_instance()
                
                if 0: # Old code
                
                    ses = api.make_session()
                    gIP = ses.IP.getapi()
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
    #@+node:ekr.20120401063816.10242: *4* pushToIPythonCommand
    def pushToIPythonCommand(self,event=None):

        '''The push-to-ipython command.

        IPython must be started, but need not be inited.'''

        self.pushToIPython(script=None)
    #@+node:ekr.20120401063816.10243: *3* Utils...
    #@+node:ekr.20120401063816.10244: *4* error & message
    def error (self,s):

        g.es_print(s,color='red')

    def message (self,s):

        g.es_print(s,color='blue')
    #@+node:ekr.20120401063816.10245: *4* pushToIPython
    def pushToIPython (self,script=None):
        ''' Push the node to IPython'''
        
        ip = ishell.InteractiveShell.instance()
        if ip:
            if script:
                ip.runlines(script)
            else:
                c = self.c ; p = c.p
                if not ip.user_ns.get('_leo'):
                    leox = leoInterface(c,g)
                    # ipy_leo.init_ipython(ip)
                    ipy_leo.update_commander(leox,new_ip=ip)
                    # g.trace('_leo',ip.user_ns.get('_leo'))
                    assert ip.user_ns.get('_leo')
                c.inCommand = False
                    # Disable the command lockout logic
                push = ip.user_ns['_leo'].push
                    # This is really push_position_from_leo.
                push(p)
        else:
            g.trace('can not happen: IPython not running')
            # self.startIPython(script)
    #@+node:ekr.20120401063816.10246: *4* started
    def started (self):
        
        ### return gIP
        return ishell.InteractiveShell.instance()
    #@-others
#@+node:ekr.20120401063816.10247: ** class LeoInterface
class LeoInterface:

    '''A class to allow full access to Leo from Ipython.

    An instance of this class called leox is typically injected
    into IPython's user_ns namespace by the init-ipython-command.'''

    def __init__(self,c,g,tag='@ipython-results'):
        self.c = c
        self.g = g
#@+node:ekr.20120401063816.10189: ** class LeoNode
class LeoNode(object, UserDict.DictMixin):
    """ Node in Leo outline

    Most important attributes (getters/setters available:
     .v     - evaluate node, can also be aligned 
     .b, .h - body string, headline string
     .l     - value as string list

    Also supports iteration, 

    setitem / getitem (indexing):  
     wb.foo['key'] = 12
     assert wb.foo['key'].v == 12

    Note the asymmetry on setitem and getitem! Also other
    dict methods are available. 

    .ipush() - run push-to-ipython

    Minibuffer command access (tab completion works):

     mb save-to-file

    """
    #@+others
    #@+node:ekr.20120401063816.10190: *3* __init__ (LeoNode)
    def __init__(self,p):
        self.p = p.copy()

    #@+node:ekr.20120401063816.10191: *3* __str__
    def __str__(self):
        return "<LeoNode %s>" % str(self.p.h)

    __repr__ = __str__
    #@+node:ekr.20120401063816.10192: *3* __get_h and _set_h
    def __get_h(self):
        return self.p.headString()


    def __set_h(self,val):
        c.setHeadString(self.p,val)
        LeoNode.last_edited = self
        c.redraw()

    h = property( __get_h, __set_h, doc = "Node headline string")  
    #@+node:ekr.20120401063816.10193: *3* _get_b and __set_b
    def __get_b(self):
        return self.p.bodyString()

    def __set_b(self,val):
        c.setBodyString(self.p, val)
        LeoNode.last_edited = self
        c.redraw()

    b = property(__get_b, __set_b, doc = "Nody body string")
    #@+node:ekr.20120401063816.10194: *3* __set_val
    def __set_val(self, val):        
        self.b = format_for_leo(val)

    v = property(lambda self: eval_node(self), __set_val,
        doc = "Node evaluated value")
    #@+node:ekr.20120401063816.10195: *3* __set_l
    def __set_l(self,val):
        self.b = '\n'.join(val )

    l = property(lambda self : IPython.genutils.SList(self.b.splitlines()), 
                 __set_l, doc = "Node value as string list")
    #@+node:ekr.20120401063816.10196: *3* __iter__
    def __iter__(self):
        """ Iterate through nodes direct children """

        return (LeoNode(p) for p in self.p.children_iter())

    #@+node:ekr.20120401063816.10197: *3* __children
    def __children(self):
        d = {}
        for child in self:
            head = child.h
            tup = head.split(None,1)
            if len(tup) > 1 and tup[0] == '@k':
                d[tup[1]] = child
                continue

            if not valid_attribute(head):
                d[head] = child
                continue
        return d
    #@+node:ekr.20120401063816.10198: *3* keys
    def keys(self):
        d = self.__children()
        return list(d.keys()) # 2010/02/04: per 2to3
    #@+node:ekr.20120401063816.10199: *3* __getitem__
    def __getitem__(self, key):
        """ wb.foo['Some stuff']
        Return a child node with headline 'Some stuff'

        If key is a valid python name (e.g. 'foo'),
        look for headline '@k foo' as well
        """  
        key = str(key)
        d = self.__children()
        return d[key]
    #@+node:ekr.20120401063816.10200: *3* __setitem__
    def __setitem__(self, key, val):
        """ You can do wb.foo['My Stuff'] = 12 to create children 

        Create 'My Stuff' as a child of foo (if it does not exist), and 
        do .v = 12 assignment.

        Exception:

        wb.foo['bar'] = 12

        will create a child with headline '@k bar',
        because bar is a valid python name and we don't want to crowd
        the WorkBook namespace with (possibly numerous) entries.
        """
        key = str(key)
        d = self.__children()
        if key in d:
            d[key].v = val
            return

        if not valid_attribute(key):
            head = key
        else:
            head = '@k ' + key
        p = c.createLastChildNode(self.p, head, '')
        LeoNode(p).v = val

    #@+node:ekr.20120401063816.10201: *3* __delitem__
    def __delitem__(self, key):
        """ Remove child

        Allows stuff like wb.foo.clear() to remove all children
        """
        self[key].p.doDelete()
        c.redraw()

    #@+node:ekr.20120401063816.10202: *3* ipush (LeoNode)
    def ipush(self):
        """ Does push-to-ipython on the node """
        # push_from_leo(self)
        
        print('LeoNode.ipush',self)
        
        # CommandChainDispatcher([self])
    #@+node:ekr.20120401063816.10203: *3* go
    def go(self):
        """ Set node as current node (to quickly see it in Outline) """
        #c.setCurrentPosition(self.p)

        # argh, there should be another way
        #c.redraw()
        #s = self.p.bodyString()
        #c.setBodyString(self.p,s)
        c.selectPosition(self.p)
    #@+node:ekr.20120401063816.10204: *3* append
    def append(self):
        """ Add new node as the last child, return the new node """
        p = self.p.insertAsLastChild()
        return LeoNode(p)
    #@+node:ekr.20120401063816.10205: *3* script
    def script(self):
        """ Method to get the 'tangled' contents of the node

        (parse @others, %s references etc.)
        """ % g.angleBrackets(' section ')

        return g.getScript(c,self.p,useSelectedText=False,useSentinels=False)

    #@+node:ekr.20120401063816.10206: *3* __get_uA
    def __get_uA(self):
        p = self.p

        # Create the uA if necessary.

        # EKR: change p.v.t to p.v here.
        if not hasattr(p.v,'unknownAttributes'):
            p.v.unknownAttributes = {}        

        d = p.v.unknownAttributes.setdefault('ipython', {})
        return d        

    #@-others
    uA = property(__get_uA,
        doc = "Access persistent unknownAttributes of node")
#@+node:ekr.20120401063816.10181: ** class LeoWorkbook
class LeoWorkbook:
    """ class for 'advanced' node access 

    Has attributes for all "discoverable" nodes.
    Node is discoverable if it either

    - has a valid python name (Foo, bar_12)
    - is a parent of an anchor node.
    If it has a child '@a foo', it is visible as foo.

    """
    #@+others
    #@+node:ekr.20120401063816.10182: *3* __getattr__
    def __getattr__(self, key):
        if key.startswith('_') or key == 'trait_names' or not valid_attribute(key):
            raise AttributeError
        cells = all_cells()
        p = cells.get(key, None)
        if p is None:
            return add_var(key)

        return LeoNode(p)

    #@+node:ekr.20120401063816.10183: *3* __str__
    def __str__(self):
        return "<LeoWorkbook>"

    __repr__ = __str__
    #@+node:ekr.20120401063816.10184: *3* __setattr__
    def __setattr__(self,key, val):
        raise AttributeError(
            "Direct assignment to workbook denied, try wb.%s.v = %s" % (
                key,val))

    #@+node:ekr.20120401063816.10185: *3* __iter__
    def __iter__(self):
        """ Iterate all (even non-exposed) nodes """
        cells = all_cells()
        return (LeoNode(p) for p in c.allNodes_iter())

    #@+node:ekr.20120401063816.10186: *3* current
    current = property(
        lambda self: LeoNode(c.currentPosition()),
        doc = "Currently selected node")
    #@+node:ekr.20120401063816.10187: *3* match_h
    def match_h(self, regex):
        cmp = re.compile(regex)
        res = PosList()
        for node in self:
            if re.match(cmp, node.h, re.IGNORECASE):
                res.append(node)
        return res

    #@+node:ekr.20120401063816.10188: *3* require
    def require(self, req):
        """ Used to control node push dependencies 

        Call this as first statement in nodes.
        If node has not been pushed, it will be pushed before proceeding

        E.g. wb.require('foo') will do wb.foo.ipush()
        if it hasn't been done already.
        """

        if req not in _leo_push_history:
            es('Require: ' + req)
            getattr(self,req).ipush()
    #@-others
#@+node:ekr.20120401063816.10180: ** class PosList
class PosList(list):

    def select(self, pat):
        res = PosList()
        for n in self:
            #print "po",p
            for chi_p in n.p.children_iter():
                #print "chi",chi_p
                if re.match(pat, chi_p.headString()):
                    res.append(LeoNode(chi_p))
        return res
#@-others
#@-leo
