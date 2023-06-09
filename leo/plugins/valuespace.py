#@+leo-ver=5-thin
#@+node:ville.20110403115003.10348: * @file ../plugins/valuespace.py
#@+<< docstring >>
#@+node:ville.20110403115003.10349: ** << docstring >>
"""Supports Leo scripting using per-Leo-outline namespaces.

Commands
========

This plugin supports the following commands:


vs-create-tree
--------------

Creates a tree whose root node is named 'valuespace' containing one child node
for every entry in the namespace. The headline of each child is *@@r <key>*,
where *<key>* is one of the keys of the namespace. The body text of the child
node is the value for *<key>*.

vs-dump
-------

Prints key/value pairs of the namespace.

vs-reset
--------

Clears the namespace.

vs-update
---------

Scans the entire Leo outline twice, processing *@=*, *@a* and *@r* nodes.

Pass 1
++++++

Pass 1 evaluates all *@=* and *@a* nodes in the outline as follows:

*@=* (assignment) nodes should have headlines of the the form::

    @= <var>

Pass 1 evaluates the body text and assigns the result to *<var>*.

*@a* (anchor) nodes should have headlines of one of two forms::

    @a
    @a <var>

The first form evaluates the script in the **parent** node of the *@a* node.
Such **bare** @a nodes serve as markers that the parent contains code to be
executed.

The second form evaluates the body of the **parent** of the *@a* node and
assigns the result to *<var>*.

**Important**: Both forms of *@a* nodes support the following **@x convention**
when evaluating the parent's body text. Before evaluating the body text, pass1
scans the body text looking for *@x* lines. Such lines have two forms:

1. *@x <python statement>*

Pass 1 executes *<python statement>*.

2. The second form spans multiple lines of the body text::

    @x {
    python statements
    @x }

Pass 1 executes all the python statements between the *@x {* and the *@x }*

3. Assign block of text to variable::

    @x =<var> {
    Some
    Text
    @x }

Pass 1 assigns the block of text to <var>. The type of value is SList,
a special subclass of standard 'list' that makes operating with string
lists convenient. Notably, you can do <var>.n to get the content as plain
string.

A special case of this is the "list append" notation::

    @x =<var>+ {
    Some
    Text
    @x }

This assumes that <var> is a list, and appends the content as SList to this
list. You will typically do '@x var = []' earlier in the document to make this
construct work.

<var> in all constructs above can be arbitrary expression that can be on left hand
side of assignment. E.g. you can use foo.bar, foo['bar'], foo().bar etc.

Pass 2
++++++

Pass 2 "renders" all *@r* nodes in the outline into body text. *@r* nodes should
have the form::

    @r <expression>

Pass 2 evaluates *<expression>* and places the result in the body pane.

**TODO**: discuss SList expressions.

Evaluating expressions
======================

All expression are evaluated in a context that predefines Leo's *c*, *g* and *p*
vars. In addition, *g.vs* is a dictionary whose keys are *c.hash()* and whose
values are the namespaces for each commander. This allows communication between
different namespaces, while keeping namespaces generally separate.

"""

# SList docs: http://ipython.scipy.org/moin/Cookbook/StringListProcessing
#@-<< docstring >>
# By Ville M. Vainio and Terry N. Brown.

#@+<< valuespace imports >>
#@+node:ville.20110403115003.10351: ** << valuespace imports >>
import pprint
import os
import re
import json
from io import BytesIO
from typing import Any, Sequence
try:
    import yaml
except ImportError:
    yaml = None

from leo.core import leoGlobals as g
from leo.core import leoPlugins
from leo.external.stringlist import SList  # Uses leoPlugins.TryNext.
#@-<< valuespace imports >>
# Keys are c.hash(), values are ValueSpaceControllers.
controllers: dict[str, Any] = {}

# pylint: disable=eval-used
# Eval is essential to this plugin.

#@+others
#@+node:ekr.20110408065137.14221: ** Top level
#@+node:ville.20110403115003.10353: *3* colorize_headlines_visitor
def colorize_headlines_visitor(c, p, item):
    """ Changes @thin, @auto, @shadow to bold """
    if p.h.startswith("!= "):
        f = item.font(0)
        f.setBold(True)
        item.setFont(0, f)
    raise leoPlugins.TryNext
#@+node:ville.20110403115003.10352: *3* init
def init():
    """Return True if the plugin has loaded successfully."""
    # vs_reset(None)
    global controllers
    # create global valuaspace controller for ipython
    g.visit_tree_item.add(colorize_headlines_visitor)
    g.registerHandler('after-create-leo-frame', onCreate)
    g.plugin_signon(__name__)
    return True
#@+node:ekr.20110408065137.14222: *3* onCreate
def onCreate(tag, key):

    global controllers
    c = key.get('c')
    if c:
        h = c.hash()
        vc = controllers.get(h)
        if not vc:
            controllers[h] = vc = ValueSpaceController(c)
#@+node:ville.20110403115003.10355: ** Commands
#@+node:ville.20130127115643.3695: *3* get_vs
def get_vs(c):
    """deal with singleton "ipython" controller"""
    if g.app.ipk:
        vsc = controllers.get('ipython')
        if not vsc:
            controllers['ipython'] = vsc = ValueSpaceController(c=None,
                ns=g.app.ipk.namespace)
        vsc.set_c(c)
        return vsc
    return controllers[c.hash()]
#@+node:ekr.20180328055151.1: *3* Ville's original commands
#@+node:ville.20110407210441.5691: *4* vs-create-tree
@g.command('vs-create-tree')
def vs_create_tree(event):
    """Create tree from all variables."""
    get_vs(event['c']).create_tree()

#@+node:ekr.20110408065137.14227: *4* vs-dump
@g.command('vs-dump')
def vs_dump(event):
    """Dump the valuespace for this commander."""
    get_vs(event['c']).dump()
#@+node:ekr.20110408065137.14220: *4* vs-reset
@g.command('vs-reset')
def vs_reset(event):

    get_vs(event['c']).reset()
#@+node:ville.20110403115003.10356: *4* vs-update
@g.command('vs-update')
def vs_update(event):

    get_vs(event['c']).update()
#@+node:ekr.20110408065137.14219: ** class ValueSpaceController
class ValueSpaceController:

    """A class supporting per-commander evaluation spaces
    containing @a, @r and @= nodes.
    """

    #@+others
    #@+node:ekr.20110408065137.14223: *3*  ctor
    def __init__(self, c=None, ns=None):

        self.c = c
        self.d = {} if ns is None else ns
        self.reset()
        if c:
            # This must come after self.reset()
            c.keyHandler.autoCompleter.namespaces.append(self.d)
    #@+node:ekr.20110408065137.14224: *3* create_tree
    def create_tree(self):
        """The vs-create-tree command."""
        c = self.c
        p = c.p
        tag = 'valuespace'
        # Create a 'valuespace' node if p's headline is not 'valuespace'.
        if p.h == tag:
            r = p
        else:
            r = p.insertAsLastChild()
            r.h = tag

        # Create a child of r for all items of self.d
        for k, v in self.d.items():
            if not k.startswith('__'):
                child = r.insertAsLastChild()
                child.h = '@@r ' + k
                self.render_value(child, v)  # Create child.b from child.h

        c.bodyWantsFocus()
        c.redraw()
    #@+node:ekr.20110408065137.14228: *3* dump
    def dump(self):

        c, d = self.c, self.d

        exclude = (
            '__builtins__',
            # 'c','g','p',
        )

        print('Valuespace for %s...' % c.shortFileName())
        keys = list(d.keys())
        keys = [z for z in keys if z not in exclude]
        keys.sort()
        max_s = 5
        for key in keys:
            max_s = max(max_s, len(key))
        for key in keys:
            val = d.get(key)
            pad = max(0, max_s - len(key)) * ' '
            print('%s%s = %s' % (pad, key, val))

        c.bodyWantsFocus()
    #@+node:ekr.20110408065137.14225: *3* reset
    def reset(self):

        """The vs-reset command."""

        # do not allow resetting the dict if using ipython
        if not g.app.ipk:
            self.d = {}
            self.c.vs = self.d

        self.init_ns(self.d)

    #@+node:ville.20110409221110.5755: *3* init_ns
    def init_ns(self, ns):
        """ Add 'builtin' methods to namespace """

        def slist(body):
            """ Return body as SList (string list) """
            return SList(body.split("\n"))

        ns['slist'] = slist

        # xxx todo perhaps add more?

    #@+node:ville.20130127122722.3696: *3* set_c
    def set_c(self, c):
        """ reconfigure vsc for new c

        Needed by ipython integration
        """
        self.c = c
    #@+node:ekr.20110408065137.14226: *3* update & helpers
    def update(self):

        """The vs-update command."""

        # names are reversed, xxx TODO fix later
        self.render_phase()  # Pass 1
        self.update_vs()  # Pass 2
        self.c.bodyWantsFocus()
    #@+node:ekr.20110407174428.5781: *4* render_phase (pass 1) & helpers
    def render_phase(self):
        """Update p's tree (or the entire tree) as follows:

        - Evaluate all @= nodes and assign them to variables
        - Evaluate the body of the *parent* nodes for all @a nodes.
        - Read in @vsi nodes and assign to variables

        """

        c = self.c
        self.d['c'] = c  # g.vs.c = c
        self.d['g'] = g  # g.vs.g = g
        for p in c.all_unique_positions():
            h = p.h.strip()
            if h.startswith('@= '):
                self.d['p'] = p.copy()  # g.vs.p = p.copy()
                var = h[3:].strip()
                self.let_body(var, self.untangle(p))
            elif h.startswith("@vsi "):
                fname = h[5:]
                bname, ext = os.path.splitext(fname)
                g.es("@vsi " + bname + " " + ext)
                if ext.lower() == '.json':
                    pth = c.getNodePath(p)
                    fn = os.path.join(pth, fname)
                    g.es("vsi read from  " + fn)
                    if os.path.isfile(fn):
                        cont = open(fn).read()
                        val = json.loads(cont)
                        self.let(bname, val)
                        self.render_value(p, cont)


            elif h == '@a' or h.startswith('@a '):
                tail = h[2:].strip()
                parent = p.parent()

                if tail:
                    self.let_body(tail, self.untangle(parent))
                try:
                    self.parse_body(parent)
                except Exception:
                    g.es_exception()
                    g.es("Error parsing " + parent.h)
    #@+node:ekr.20110407174428.5777: *5* let & let_body
    def let(self, var, val):

        """Enter var into self.d with the given value.
        Both var and val must be strings."""

        self.d['__vstemp'] = val
        if var.endswith('+'):
            rvar = var.rstrip('+')
            # .. obj = eval(rvar,self.d)
            exec("%s.append(__vstemp)" % rvar, self.d)
        else:
            exec(var + " = __vstemp", self.d)
        del self.d['__vstemp']

    def let_cl(self, var, body):
        """ handle @cl node """
        lend = body.find('\n')
        firstline = body[0:lend]
        rest = firstline[4:].strip()
        print("rest", rest)
        try:
            translator = eval(rest, self.d)
        except Exception:
            g.es_exception()
            g.es("Can't instantate @cl xlator: " + rest)
        translated = translator(body[lend + 1 :])
        self.let(var, translated)

    def let_body(self, var, val):
        if var.endswith(".yaml"):
            if yaml:
                sio = BytesIO(val)
                try:
                    # Both mypy and pylint complaint.
                    # pylint: disable=no-value-for-parameter
                    d = yaml.load(sio)  # type:ignore
                except Exception:
                    g.es_exception()
                    g.es("yaml error for: " + var)
                    return
                parts = os.path.splitext(var)
                self.let(parts[0], d)
            else:
                g.es("did not import yaml")
            return

        if val.startswith('@cl '):
            self.let_cl(var, val)
            return

        self.let(var, val)

    #@+node:ekr.20110407174428.5780: *5* parse_body & helpers
    def parse_body(self, p):

        body = self.untangle(p)  # body is the script in p's body.
        self.d['p'] = p.copy()
        backop: Sequence = []
        segs = re.finditer('^(@x (.*))$', body, re.MULTILINE)
        for mo in segs:
            op = mo.group(2).strip()
            # print("Oper",op)
            if op.startswith('='):
                # print("Assign", op)
                backop = ('=', op.rstrip('{').lstrip('='), mo.end(1))
            elif op == '{':
                backop = ('runblock', mo.end(1))
            elif op == '}':
                bo = backop[0]
                # print("backop",bo)
                if bo == '=':
                    self.let_body(backop[1].strip(), body[backop[2] : mo.start(1)])
                elif bo == 'runblock':
                    self.runblock(body[backop[1] : mo.start(1)])
            else:
                self.runblock(op)
    #@+node:ekr.20110407174428.5779: *6* runblock
    def runblock(self, block):

        exec(block, self.d)
    #@+node:ekr.20110407174428.5778: *6* untangle (getScript)
    def untangle(self, p):

        return g.getScript(self.c, p,
            useSelectedText=False,
            useSentinels=False)
    #@+node:ekr.20110407174428.5782: *4* update_vs (pass 2) & helper
    def update_vs(self):
        """
        Evaluate @r <expr> nodes, puting the result in their body text.
        Output @vso nodes, based on file extension
        """
        c = self.c
        for p in c.all_unique_positions():
            h = p.h.strip()
            if h.startswith('@r '):
                expr = h[3:].strip()
                try:
                    result = eval(expr, self.d)
                except Exception:
                    g.es_exception()
                    g.es("Failed to render " + h)
                    continue
                self.render_value(p, result)

            if h.startswith("@vso "):
                expr = h[5:].strip()
                bname, ext = os.path.splitext(expr)
                try:
                    result = eval(bname, self.d)
                except Exception:
                    g.es_exception()
                    g.es("@vso failed: " + h)
                    continue
                if ext.lower() == '.json':
                    cnt = json.dumps(result, indent=2)
                    pth = os.path.join(c.getNodePath(p), expr)
                    self.render_value(p, cnt)
                    g.es("Writing @vso: " + pth)
                    open(pth, "w").write(cnt)
                else:
                    g.es_error("Unknown vso extension (should be .json, ...): " + ext)
    #@+node:ekr.20110407174428.5784: *5* render_value
    def render_value(self, p, value):

        """Put the rendered value in p's body pane."""

        if isinstance(value, SList):
            p.b = value.n
        elif isinstance(value, str):
            p.b = value
        else:
            p.b = pprint.pformat(value)
    #@+node:ekr.20110407174428.5783: *3* test
    def test(self):
        self.update()

    # test()
    #@-others
#@-others
#@-leo
