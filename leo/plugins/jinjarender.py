#@+leo-ver=5-thin
#@+node:ville.20110409151021.5699: * @file ../plugins/jinjarender.py
#@+<< docstring >>
#@+node:ville.20110409151021.5700: ** << docstring >>
""" Render @jinja nodes.

- sudo apt-get install python-jinja2

Create headline like this:

@jinja ~/foo.txt

Select the node and do alt-x act-on-node

Conceptually, acts like @nosent - tree is parsed,
template is expanded and content is written to the file.

Requires "valuespace" plugin. Fetches vars from valuespace.

"""
#@-<< docstring >>

# By Ville M. Vainio.

#@+<< imports >>
#@+node:ville.20110409151021.5702: ** << imports >>
try:
    from jinja2 import Template
except ImportError:
    Template = None  # type:ignore

from leo.core import leoGlobals as g
from leo.core import leoPlugins  # Uses leoPlugins.TryNext
#@-<< imports >>

#@+others
#@+node:ville.20110409151021.5703: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    ok = bool(Template)
    if ok:
        g.plugin_signon(__name__)
        jinja_install()
    return ok
#@+node:ville.20110409151021.5705: ** install & act-on-node
#@+node:ekr.20120525090541.10863: *3* untangle
def untangle(c, p):

    return g.getScript(c, p,
        useSelectedText=False,
        useSentinels=False)

#@+node:ekr.20120525090541.10864: *3* jinja_render
def jinja_render(template, fname, d):
    tmpl = Template(template)
    out = tmpl.render(d)
    open(fname, "w").write(out)

#@+node:ekr.20120525090541.10865: *3* jinja_act_on_node
def jinja_act_on_node(c, p, event):
    h = p.h
    if not h.startswith('@jinja '):
        raise leoPlugins.TryNext
    tail = h[7:].strip()
    pth = c.getNodePath(p)
    fullpath = g.finalize_join(pth, tail)
    g.es("Rendering " + fullpath)
    body = untangle(c, p)
    jinja_render(body, fullpath, c.vs)

#@+node:ekr.20120525090541.10866: *3* jinja_install
def jinja_install():
    g.act_on_node.add(jinja_act_on_node, 50)

#@+node:ekr.20120525090541.10867: *3* class JinjaCl
class JinjaCl:
    #@+others
    #@+node:ekr.20120525090541.10868: *4* __init__
    def __init__(self, c):
        self.c = c
    #@+node:ekr.20120525090541.10869: *4* __call__
    def __call__(self, body):
        """ Render body through jinja

        To be used from @cl nodes
        """
        tmpl = Template(body)
        out = tmpl.render(self.c.vs)
        return out

    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
