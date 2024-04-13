#@+leo-ver=5-thin
#@+node:vitalije.20180804172140.1: * @file ../plugins/md_docer.py
"""This plugin adds few commands for those who use Leo for writing
   markdown documentation with code samples taken from real source
   files.

   md-write-files command scans outline for nodes whose headline is
                  like `md:<filename>`, and for each node it generates
                  output file adding extension .md.
                  The output is written relative to the @path in effect
                  for the given md node.

                  headlines of descendant nodes are written as headlines
                  of the appropriate level.

                  Any line which startswith `LEO:<some gnx>` will be
                  replaced with the lines of node with given gnx indented
                  as much as LEO:<gnx> line was indented.

    md-copy-leo-gnx command puts in clipboard marker of the currently selected
                  node. This marker can be pasted in the documentation where
                  source code example should be.

    md-sync-transformations command updates body of all @transform-node nodes.

        transformations can be defined in nodes with headline like:
            @transformer <name>
        body (and possibly subtree), should be script which has predefined
        symbols c, g, v, out where v is source vnode whose body is being
        transformed and out is file like object where transformer script
        can write its output. This synchronization is done before save
        automatically.

    Author: vitalije(at)kviziracija.net
"""
import io
import re
from leo.core import leoGlobals as g
pat = re.compile(r'^(\s*)LEOGNX:(.+)$')
def init():
    """Return True if the plugin has loaded successfully."""
    g.registerHandler('save1', beforeSave)
    g.plugin_signon(__name__)
    return True
#@+others
#@+node:vitalije.20180804174131.1: ** md_write_files
@g.command('md-write-files')
def md_write_files(event):
    """writes all md nodes. A md node is node whose headline
       starts with 'md:' followed by file name."""
    c = event.get('c')
    #@+others
    #@+node:vitalije.20180804180150.1: *3* hl
    def hl(v, lev):
        return '#' * (lev + 1) + ' ' + v.h + '\n'
    #@+node:vitalije.20180804180104.1: *3* mdlines
    def mdlines(v, lev=0):
        if lev > 0 and not v.b.startswith('#'):
            yield hl(v, lev)
            yield ''
        for line in v.b.splitlines(False):
            if m := pat.match(line):
                v1 = c.fileCommands.gnxDict.get(m.group(2))
                if not v1:
                    g.es('gnx not found:[%s]' % m.group(2))
                else:
                    for x in v1.b.splitlines(False):
                        yield m.group(1) + x
                continue
            yield line
        yield ''
        for v1 in v.children:
            for line in mdlines(v1, lev + 1):
                yield line
        yield ''
    #@+node:vitalije.20180804180749.1: *3* process
    def process(v, fname):
        with open(fname, 'w', encoding='utf-8') as out:
            out.write('\n'.join(mdlines(v, 0)))
        g.es(fname, 'ok')
    #@-others
    seen = set()
    p = c.rootPosition()
    while p:
        v = p.v
        if v.gnx in seen:
            p.moveToNodeAfterTree()
        else:
            seen.add(v.gnx)
            if v.isAtIgnoreNode():
                p.moveToNodeAfterTree()
                continue
            h = v.h
            if h.startswith('md:'):
                pth = c.getNodePath(p)
                fname = g.finalize_join(pth, h[3:].strip())
                if not fname.endswith('.md'):
                    fname = fname + '.md'
                process(v, fname)
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
#@+node:vitalije.20180804180928.1: ** md_copy_leo_gnx
@g.command('md-copy-leo-gnx')
def md_copy_leo_gnx(event):
    """Puts on clipboard `LEOGNX:<gnx of currently selected node>`."""
    c = event.get('c')
    g.app.gui.replaceClipboardWith('LEOGNX:' + c.p.gnx)
#@+node:vitalije.20180805114033.1: ** beforeSave
def beforeSave(tag, key):
    sync_transformations(key)
#@+node:vitalije.20180805114039.1: ** sync_transformations
@g.command('md-sync-transformations')
def sync_transformations(event):
    c = event.get('c')
    gnxDict = c.fileCommands.gnxDict
    trscripts = {}
    trtargets = {}
    #@+others
    #@+node:vitalije.20180805121201.1: *3* collect_data (md_docer.py)
    def collect_data():
        p = c.rootPosition()
        seen = set()
        while p:
            v = p.v
            if v.gnx in seen:
                p.moveToNodeAfterTree()
                continue
            seen.add(v.gnx)
            h = v.h
            if h.startswith('@transformer '):
                name = h.partition(' ')[2].strip()
                trscripts[name] = g.getScript(c, p.copy(),
                    useSentinels=False, forcePythonSentinels=True)
                p.moveToNodeAfterTree()
            elif h.startswith('@transform-node '):
                name = h.partition(' ')[2].strip()
                name, sep, rest = name.partition('(')
                if not sep:
                    g.warning('wrong syntax expected "("', nodeLink=p)
                    p.moveToThreadNext()
                    continue
                srcgnx, sep, rest = rest.partition(')')
                if not sep:
                    g.warning('wrong syntax expected ")"', nodeLink=p)
                    p.moveToThreadNext()
                    continue
                srcgnx = srcgnx.strip()
                if not srcgnx in c.fileCommands.gnxDict:
                    g.warning('unknown gnx', srcgnx, nodeLink=p)
                    p.moveToThreadNext()
                    continue
                trtargets[v.gnx] = (name, srcgnx)
                p.moveToThreadNext()
            else:
                p.moveToThreadNext()
    #@-others
    collect_data()
    count = 0
    for dst, args in trtargets.items():
        name, src = args
        code = trscripts.get(name, 'out.write("not found transformer code")')
        out = io.StringIO()
        try:
            exec(code, dict(v=gnxDict[src], out=out, g=g, c=c))
            gnxDict[dst].b = out.getvalue()
            count += 1
        except Exception:
            g.es_exception()
    if count:
        g.es('%d node(s) transformed' % count)
#@-others
#@-leo
