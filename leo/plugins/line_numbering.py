#@+leo-ver=5-thin
#@+node:vitalije.20170727201534.1: * @file ../plugins/line_numbering.py
"""
This plugin makes line numbers in gutter (if used), to represent
   real line numbers in generated file. Root of file is either a
   first of ancestor nodes with heading at-(file,clean,...), or first
   of ancestor nodes which was marked as root for line numbering  using
   command 'toggle-line-numbering-root'.

   Author: vitalije(at)kviziracija.net
"""

#@+<< imports >>
#@+node:vitalije.20170727201931.1: ** << imports >>
from contextlib import contextmanager
import re
from leo.core import leoGlobals as g
from leo.core.leoQt import QtCore, QtWidgets
#
# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.
#@-<< imports >>

LNT = 'line_number_translation'
LNR = 'line_numbering_root'
LNOFF = 'line_numbering_off'

#@+others
#@+node:vitalije.20170727203452.1: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    ok = g.app.gui.guiName() == "qt"
    if ok:
        g.registerHandler('select1', onSelect)
        g.registerHandler('start2', onSelect)
        g.plugin_signon(__name__)
    return ok
#@+node:vitalije.20170727222624.1: ** Commands
@g.command('toggle-line-numbering-root')
def toggleLineNumberingRoot(event):
    """Toggle state of current selected node to be treated as a
       root of file for line numbering purposes."""
    c = event.get('c')
    if c and c.p and c.p.v:
        v = c.p.v
        for p in c.p.self_and_parents():
            if p.isAnyAtFileNode():
                has_root = True
                break
        else:
            has_root = False
        v.u[LNR] = not v.u.get(LNR, False) and not has_root
        renumber(c)

@g.command('line-numbering-toggle')
def toggleLineNumberingOff(event):
    """Toggle line numbering plugin off or on."""
    c = event.get('c')
    c.user_dict[LNOFF] = not c.user_dict.get(LNOFF, False)
    renumber(c)
#@+node:vitalije.20170727204246.1: ** onSelect
def onSelect(tag, keys):
    c = keys.get('c')
    if not c.hash():
        return
    ok = c.config.getBool('use-gutter', default=False)
    ok = ok and not c.user_dict.get(LNOFF, False)
    if ok:
        new_p = keys.get('new_p') or c.p
        nums = NUMBERINGS.get(c.hash() + new_p.gnx, tuple())
        request_update(c)
        c.user_dict[LNT] = nums
        with number_bar_widget(c) as w:
            w.highest_line = nums[-1] if nums else 10
    else:
        c.user_dict[LNT] = tuple()
#@+node:vitalije.20170811122518.1: ** number_bar_widget
@contextmanager
def number_bar_widget(c):
    w = c.frame.top and c.frame.top.findChild(QtWidgets.QFrame, 'gutter')
    if w:
        yield w
    else:
        class DummyWidget:
            def update(self):
                pass
        yield DummyWidget()
#@+node:vitalije.20170727214320.1: ** renumber
NUMBERINGS = {}

def renumber(c):
    if c.user_dict.get(LNOFF, False):
        nums: tuple = tuple()
    else:
        p = new_p = c.p
        for p in new_p.self_and_parents():
            if p.isAnyAtFileNode() or p.v.u.get(LNR):
                root = p
                break
        else:
            p = root = new_p
        at = c.atFileCommands
        at.scanAllDirectives(new_p)
        delim_st = at.startSentinelComment
        delim_en = at.endSentinelComment
        if (p.isAtCleanNode() or p.isAtAutoNode() or p.isAtEditNode() or p.isAtNoSentFileNode()) \
            or not p.isAnyAtFileNode():
            delim_st = ''
            delim_en = ''
        nums = universal_line_numbers(root, new_p, delim_st, delim_en)
        NUMBERINGS[c.hash() + new_p.gnx] = nums
    if c.user_dict.get(LNT) != nums:
        c.user_dict[LNT] = nums
        with number_bar_widget(c) as w:
            w.highest_line = nums[-1] if nums else 10
            w.update()
    finish_update(c)
#@+node:vitalije.20170727214225.1: ** request & finish_update
REQUESTS: dict[str, bool] = {}

def request_update(c):
    h = c.hash()
    if REQUESTS.get(h):
        return
    REQUESTS[h] = True
    QtCore.QTimer.singleShot(200, lambda: renumber(c))

def finish_update(c):
    REQUESTS[c.hash()] = False
#@+node:vitalije.20170726090940.1: ** universal_line_numbers
def universal_line_numbers(root, target_p, delim_st, delim_en):
    """Returns tuple of line numbers corresponding to lines of
    target_p body, in a file generated from root."""
    c = root.v.context
    roots = c.user_dict.get('line_numbering_roots', set())
    roots.add(root.gnx)
    c.user_dict['line_numbering_roots'] = roots
    flines_data = {}
    #@+others
    #@+node:vitalije.20170726110242.1: *3* write patterns
    section_pat = re.compile(r'^(\s*)(<{2}[^>]+>>)(.*)$')

    # Important: re.M used also in others_iterator
    others_pat = re.compile(r'^(\s*)@others\b', re.M)

    doc_pattern = re.compile('^(@doc|@)(?:\\s(.*?)\n|\n)$')

    code_pattern = re.compile('^(@code|@c)$')
    #@+node:vitalije.20170726120813.1: *3* vlines
    vlinescache: dict[str, tuple] = {}
    def vlines(p):
        if p.gnx in vlinescache:
            return vlinescache[p.gnx]
        vl = vlinescache[p.gnx] = tuple(g.splitLines(p.b))
        return vl
    #@+node:vitalije.20170726124959.1: *3* is_verbatim
    verbaline = delim_st + '@'
    if delim_st:
        is_verbatim = lambda x: x.startswith(verbaline)
        inc = lambda x: x + 1
    else:
        is_verbatim = lambda x: False
        inc = lambda x: x
    #@+node:vitalije.20170726110433.1: *3* others_iterator
    def others_iterator(p):
        after = p.nodeAfterTree()
        p1 = p.threadNext()
        while p1 and p1 != after:
            if p1.isAtIgnoreNode() or section_pat.match(p1.h):
                p1.moveToNodeAfterTree()
            else:
                yield p1.copy()
                if others_pat.search(p1.b):
                    p1.moveToNodeAfterTree()
                else:
                    p1.moveToThreadNext()
    #@+node:vitalije.20170726121426.1: *3* handle_first_and_last_lines
    def handle_first_and_last_lines():
        rlines = vlines(root)
        first = last = 0
        while rlines and rlines[0].startswith('@first '):
            rlines = rlines[1:]
            first += 1
        while rlines and rlines[-1].startswith('@last '):
            rlines = rlines[:-1]
            last += 1
        vlinescache[root.gnx] = rlines
        return first, last
    #@+node:vitalije.20170726122226.1: *3* numerate_node
    def numerate_node(p, st):
        f_lines = []
        st = inc(st)
        for i, line in enumerate(vlines(p)):
            offset, size = check_line(p, line, st)
            f_lines.append(st + offset)
            st += size
        f_lines.append(st)
        flines_data[pkey(p)] = tuple(f_lines), st
        return st
    #@+node:vitalije.20170726124944.1: *3* check_line
    def check_line(p, line, st):
        # every child node ends with return
        #@+others
        #@+node:vitalije.20170726193840.1: *4* verbatim lines
        if is_verbatim(line):
            return 1, 2
        #@+node:vitalije.20170726193927.1: *4* others
        if m := others_pat.match(line):
            n = inc(st)
            for p1 in others_iterator(p):
                n = numerate_node(p1, n)
            n = inc(n)
            return (0, n - st) if delim_st else (0, n - st)
        #@+node:vitalije.20170726193858.1: *4* directives in clean
        if not delim_st and g.isDirective(line):
            return 0, 0
        #@+node:vitalije.20170726193908.1: *4* all
        if line.strip() == '@all':
            n = st + 1
            for p1 in p.subtree():
                n += 1
                if vlines(p1):
                    flines = []
                    for x in vlines(p1):
                        n += 1
                        if is_verbatim(x):
                            n += 1
                        flines.append(n)
                    flines.append(n + 1)
                else:
                    flines = [n]
                flines_data[pkey(p1)] = tuple(flines), n
            return 1, n - st
        #@+node:vitalije.20170726193920.1: *4* section reference
        if m := section_pat.match(line):
            p1 = g.findReference(m.group(2), p)
            if not p1:
                g.warning('unresolved section reference %s' % m.group(2))
                if delim_st:
                    return 0, 2
                return 0, 0
            n = inc(st)
            n = numerate_node(p1, n)
            n = inc(n)
            return (0, n - st) if delim_st else (0, n - st)
        #@+node:vitalije.20170726193933.1: *4* doc part
        if doc_pattern.match(line):
            if delim_st:
                return 0, 1
            return 0, 0
        #@+node:vitalije.20170726193941.1: *4* code part
        if code_pattern.match(line):
            if delim_st:
                return 0, 1
            return 0, 0
        #@-others
        # if we get here it is an ordinary line
        return 0, 1
    #@+node:vitalije.20170727202446.1: *3* pkey
    def pkey(p):
        # this is enough for short-term key inside this function
        # positions will never change its archivedPosition value
        return tuple(p.archivedPosition())
    #@-others
    vlinescache[root.gnx] = tuple(g.splitLines(root.b))
    first, last = handle_first_and_last_lines()
    start = 2 * first + 2 if delim_st else first + 1
    n = numerate_node(root, start)
    if target_p == root:
        k = pkey(root)
        flines, n = flines_data[k]
        tfirst = tuple(range(1, first + 1))
        n += 2 if delim_st else 1
        tlast = tuple(range(n, n + last))
        return tfirst + flines + tlast
    k = pkey(target_p)
    return flines_data.get(k, (tuple(),))[0]
#@-others
#@@language python
#@@tabwidth -4
#@-leo
