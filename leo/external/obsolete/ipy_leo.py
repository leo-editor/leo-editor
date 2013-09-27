#@+leo-ver=5-thin
#@+node:ekr.20100120092047.6087: * @file ../external/obsolete/ipy_leo.py
""" ILeo - Leo plugin for IPython

"""

# **Important**: this module has been replaced by leoIPython.py.

#@@language python
#@@tabwidth -4

#@+<< ipy_leo imports >>
#@+node:ekr.20100120092047.6088: ** << ipy_leo imports >>
if 1:
    # pylint: disable=E0611
    # E0611: No name 'ipapi' in module 'IPython'
    # E0611: No name 'genutils' in module 'IPython'
    # E0611: No name 'generics' in module 'IPython'
    # E0611: No name 'hooks' in module 'IPython'
    # E0611: No name 'ipapi' in module 'IPython'
    # E0611: No name 'macro' in module 'IPython'
    # E0611: No name 'Shell' in module 'IPython'

    import IPython.ipapi
    import IPython.genutils
    import IPython.generics
    from IPython.hooks import CommandChainDispatcher
    import re
    import UserDict
    from IPython.ipapi import TryNext 
    import IPython.macro
    import IPython.Shell
#@-<< ipy_leo imports >>

# Globals.
_leo_push_history = set()
wb = None

# EKR: these were not explicitly inited.
ip = None
_request_immediate_connect = None
    # Set below in lleo_f.

#@+others
#@+node:ekr.20100120092047.6089: ** init_ipython
def init_ipython(ipy):
    """ This will be run by _ip.load('ipy_leo') 

    Leo still needs to run update_commander() after this.

    """

    global ip
    ip = ipy
    IPython.Shell.hijack_tk() # pylint: disable=E1101
        # E1101: init_ipython: Module 'IPython' has no 'Shell' member
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
#@+node:ekr.20100120092047.6090: ** update_commander
first_launch = True

c,g = None, None

def update_commander(new_leox):
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
    print("Set Leo Commander:",c.frame.getTitle())

    # will probably be overwritten by user,
    # but handy for experimentation early on.
    ip.user_ns['c'] = c
    ip.user_ns['g'] = g
    ip.user_ns['_leo'] = new_leox

    new_leox.push = push_position_from_leo
    run_leo_startup_node()
    ip.user_ns['_prompt_title'] = 'ileo'
#@+node:ekr.20100120092047.6091: ** es
from IPython.external.simplegeneric import generic 
import pprint

def es(s):
    g.es(s, tabName = 'IPython')
    pass # pylint: disable=W0107
         # W0107: es: Unnecessary pass statement
#@+node:ekr.20100120092047.6092: ** format_for_leo
@generic
def format_for_leo(obj):
    """ Convert obj to string representiation (for editing in Leo)"""
    return pprint.pformat(obj)

# Just an example - note that this is a bad to actually do!
#@verbatim
#@format_for_leo.when_type(list)
#def format_list(obj):
#    return "\n".join(str(s) for s in obj)
#@+node:ekr.20100120092047.6093: ** valid_attribute
attribute_re = re.compile('^[a-zA-Z_][a-zA-Z0-9_]*$')

def valid_attribute(s):
    return attribute_re.match(s)    
#@+node:ekr.20100120092047.6094: ** rootnode
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
#@+node:ekr.20100120092047.6095: ** all_cells
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
#@+node:ekr.20100120092047.6096: ** eval_node
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
#@+node:ekr.20100120092047.6097: ** class LeoNode
class LeoNode(object, UserDict.DictMixin):
    """ Node in Leo outline

    Most important attributes (getters/setters available:
     .v     - evaluate node, can also be alligned 
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
    #@+node:ekr.20100120092047.6098: *3* __init__ (LeoNode)
    def __init__(self,p):
        self.p = p.copy()

    #@+node:ekr.20100120092047.6099: *3* __str__
    def __str__(self):
        return "<LeoNode %s>" % str(self.p)

    __repr__ = __str__
    #@+node:ekr.20100120092047.6101: *3* __get_h and _set_h
    def __get_h(self):
        return self.p.headString()


    def __set_h(self,val):
        c.setHeadString(self.p,val)
        LeoNode.last_edited = self
        c.redraw()

    h = property( __get_h, __set_h, doc = "Node headline string")  
    #@+node:ekr.20100120092047.6103: *3* _get_b and __set_b
    def __get_b(self):
        return self.p.bodyString()

    def __set_b(self,val):
        c.setBodyString(self.p, val)
        LeoNode.last_edited = self
        c.redraw()

    b = property(__get_b, __set_b, doc = "Nody body string")
    #@+node:ekr.20100120092047.6104: *3* __set_val
    def __set_val(self, val):        
        self.b = format_for_leo(val)

    v = property(
        # pylint: disable=W0108
        # W0108: LeoNode.<lambda>: Lambda may not be necessary
        lambda self: eval_node(self), __set_val,
        doc = "Node evaluated value")
    #@+node:ekr.20100120092047.6105: *3* __set_l
    def __set_l(self,val):
        self.b = '\n'.join(val )

    l = property(
        # pylint: disable=W0108,E1101
        # E1101: LeoNode.<lambda>: Module 'IPython' has no 'genutils' member
        # W0108: LeoNode.<lambda>: Lambda may not be necessary

        lambda self : IPython.genutils.SList(self.b.splitlines()), 
        __set_l, doc = "Node value as string list")
    #@+node:ekr.20100120092047.6106: *3* __iter__
    def __iter__(self):
        """ Iterate through nodes direct children """

        return (LeoNode(p) for p in self.p.children_iter())

    #@+node:ekr.20100120092047.6107: *3* __children
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
    #@+node:ekr.20100120092047.6108: *3* keys
    def keys(self):
        d = self.__children()
        return list(d.keys()) # 2010/02/04: per 2to3
    #@+node:ekr.20100120092047.6109: *3* __getitem__
    def __getitem__(self, key):
        """ wb.foo['Some stuff']
        Return a child node with headline 'Some stuff'

        If key is a valid python name (e.g. 'foo'),
        look for headline '@k foo' as well
        """  
        key = str(key)
        d = self.__children()
        return d[key]
    #@+node:ekr.20100120092047.6110: *3* __setitem__
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

    #@+node:ekr.20100120092047.6111: *3* __delitem__
    def __delitem__(self, key):
        """ Remove child

        Allows stuff like wb.foo.clear() to remove all children
        """
        self[key].p.doDelete()
        c.redraw()

    #@+node:ekr.20100120092047.6112: *3* ipush
    def ipush(self):
        """ Does push-to-ipython on the node """
        push_from_leo(self)

    #@+node:ekr.20100120092047.6113: *3* go
    def go(self):
        """ Set node as current node (to quickly see it in Outline) """
        #c.setCurrentPosition(self.p)

        # argh, there should be another way
        #c.redraw()
        #s = self.p.bodyString()
        #c.setBodyString(self.p,s)
        c.selectPosition(self.p)
    #@+node:ekr.20100120092047.6114: *3* append
    def append(self):
        """ Add new node as the last child, return the new node """
        p = self.p.insertAsLastChild()
        return LeoNode(p)
    #@+node:ekr.20100120092047.6115: *3* script
    def script(self):
        """ Method to get the 'tangled' contents of the node

        (parse @others, section references etc.)
        """

        return g.getScript(c,self.p,useSelectedText=False,useSentinels=False)
    #@+node:ekr.20100120092047.6116: *3* __get_uA
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
#@+node:ekr.20100120092047.6117: ** class LeoWorkbook
class LeoWorkbook:
    """ class for 'advanced' node access 

    Has attributes for all "discoverable" nodes.
    Node is discoverable if it either

    - has a valid python name (Foo, bar_12)
    - is a parent of an anchor node.
    If it has a child '@a foo', it is visible as foo.

    """
    #@+others
    #@+node:ekr.20100120092047.6118: *3* __getattr__
    def __getattr__(self, key):
        if key.startswith('_') or key == 'trait_names' or not valid_attribute(key):
            raise AttributeError
        cells = all_cells()
        p = cells.get(key, None)
        if p is None:
            return add_var(key)

        return LeoNode(p)

    #@+node:ekr.20100120092047.6119: *3* __str__
    def __str__(self):
        return "<LeoWorkbook>"

    __repr__ = __str__
    #@+node:ekr.20100120092047.6120: *3* __setattr__
    def __setattr__(self,key, val):
        raise AttributeError(
            "Direct assignment to workbook denied, try wb.%s.v = %s" % (
                key,val))

    #@+node:ekr.20100120092047.6121: *3* __iter__
    def __iter__(self):
        """ Iterate all (even non-exposed) nodes """
        cells = all_cells()
        return (LeoNode(p) for p in c.allNodes_iter())
    #@+node:ekr.20100120092047.6152: *3* current
    current = property( # pylint: disable=W1001
        # W1001:LeoWorkbook: Use of "property" on an old style class
        lambda self: LeoNode(c.currentPosition()),
        doc = "Currently selected node")
    #@+node:ekr.20100120092047.6122: *3* match_h
    def match_h(self, regex):
        cmp = re.compile(regex)
        res = PosList()
        for node in self:
            if re.match(cmp, node.h, re.IGNORECASE):
                res.append(node)
        return res

    #@+node:ekr.20100120092047.6123: *3* require
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
#@+node:ekr.20100120092047.6124: ** class PosList
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
#@+node:ekr.20100120092047.6126: ** workbook_complete
# E1101: workbook_complete: Module 'IPython' has no 'generics' member
@IPython.generics.complete_object.when_type(LeoWorkbook) # pylint: disable=E1101
def workbook_complete(obj, prev):
    # 2010/02/04: per 2to3
    return list(all_cells().keys()) + [
        s for s in prev if not s.startswith('_')]
#@+node:ekr.20100120092047.6127: ** add_var
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
#@+node:ekr.20100120092047.6128: ** add_file
def add_file(self,fname):
    p2 = c.currentPosition().insertAfter()
#@+node:ekr.20100120092047.6129: ** expose_ileo_push
push_from_leo = CommandChainDispatcher()

def expose_ileo_push(f, prio = 0):
    push_from_leo.add(f, prio)

#@+node:ekr.20100120092047.6130: ** push_ipython_script
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
#@+node:ekr.20100120092047.6131: ** eval_body
def eval_body(body):

    try:
        val = ip.ev(body)
    except:
        # just use stringlist if it's not completely legal python expression
        val = IPython.genutils.SList(body.splitlines()) # pylint: disable=E1101
            # E1101: eval_body: Module 'IPython' has no 'genutils' member
    return val 

#@+node:ekr.20100120092047.6132: ** push_plain_python
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
#@+node:ekr.20100120092047.6133: ** push_cl_node
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

#@+node:ekr.20100120092047.6134: ** push_ev_node
def push_ev_node(node):
    """ If headline starts with @ev, eval it and put result in body """
    if not node.h.startswith('@ev '):
        raise TryNext
    expr = node.h.lstrip('@ev ')
    es('ipy eval ' + expr)
    res = ip.ev(expr)
    node.v = res

#@+node:ekr.20100120092047.6136: ** push_position_from_leo
def push_position_from_leo(p):
    try:
        push_from_leo(LeoNode(p))

    # 2010/02/04: per 2to3
    except AttributeError as e:
        if e.args == ("Commands instance has no attribute 'frame'",):
            es("Error: ILeo not associated with .leo document")
            es("Press alt+shift+I to fix!")
        else:
            raise

#@+node:ekr.20100120092047.6135: ** push_mark_req
def push_mark_req(node):
    """ This should be the first one that gets called.

    It will mark the node as 'pushed', for wb.require.
    """
    _leo_push_history.add(node.h)
    raise TryNext
#@+node:ekr.20100120092047.6137: ** edit_object_in_leo
@generic
def edit_object_in_leo(obj, varname):
    """ Make it @cl node so it can be pushed back directly by alt+I """
    node = add_var(varname)
    formatted = format_for_leo(obj)
    if not formatted.startswith('@cl'):
        formatted = '@cl\n' + formatted
    node.b = formatted 
    node.go()

#@+node:ekr.20100120092047.6138: ** edit_macro
# E1101: edit_macro: Function 'edit_object_in_leo' has no 'when_type' member
# E1101: edit_macro: Module 'IPython' has no 'macro' member

@edit_object_in_leo.when_type(IPython.macro.Macro) # pylint: disable=E1101
def edit_macro(obj,varname):
    bod = '_ip.defmacro("""\\\n' + obj.value + '""")'
    node = add_var('Macro_' + varname)
    node.b = bod
    node.go()
#@+node:ekr.20100120092047.6139: ** get_history
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
#@+node:ekr.20100120092047.6140: ** lee_f
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
#@+node:ekr.20100120092047.6141: ** leoref_f
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
#@+node:ekr.20100120092047.6142: ** mb_f
def mb_f(self, arg):
    """ Execute leo minibuffer commands 

    Example:
     mb save-to-file
    """
    c.executeMinibufferCommand(arg)
#@+node:ekr.20100120092047.6143: ** mb_completer
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

#@+node:ekr.20100120092047.6144: ** ileo_pre_prompt_hook
def ileo_pre_prompt_hook(self):
    # this will fail if leo is not running yet
    try:
        c.outerUpdate()
    except (NameError, AttributeError):
        pass
    raise TryNext

#@+node:ekr.20100120092047.6145: ** show_welcome
def show_welcome():
    print("------------------")
    print("Welcome to Leo-enabled IPython session!")
    print("Try %leoref for quick reference.")

    # E1101:show_welcome: Module 'IPython' has no 'platutils' member
    # E0611:show_welcome: No name 'platutils' in module 'IPython'
    # pylint: disable=E1101,E0611
    import IPython.platutils
    IPython.platutils.set_term_title('ILeo')
    IPython.platutils.freeze_term_title()

#@+node:ekr.20100120092047.6146: ** run_leo_startup_node
def run_leo_startup_node():
    p = g.findNodeAnywhere(c,'@ipy-startup')
    if p:
        print("Running @ipy-startup nodes")
        for n in LeoNode(p):
            push_from_leo(n)

#@+node:ekr.20100120092047.6147: ** lleo_f
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

#@+node:ekr.20100120092047.6148: ** lno_f
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
#@+node:ekr.20100120092047.6149: ** lshadow_f
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
#@+node:ekr.20100120092047.6150: ** shadow_walk
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
#@+node:ekr.20100120092047.6151: ** mkbutton
def mkbutton(text, node_to_push):
    ib = c.frame.getIconBarObject()
    ib.add(text = text, command = node_to_push.ipush)

#@-others
#@-leo
