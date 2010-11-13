#@+leo-ver=5-thin
#@+node:ekr.20071004090250: * @file graphed.py
#@+<< docstring >>
#@+node:ekr.20071004090250.1: ** << docstring >>
""" Edits graphs visually.

Graph commands are in the Outline/Graph submenu.
See http://leo.zwiki.org/GraphEd for documentation.

Graph editor component based on the Gred graph editor from the
Gato Graph Animation Toolbox at http://gato.sourceforge.net/

"""
#@-<< docstring >>

# By Terry Brown terry_n_brown@yahoo.com

#@@language python
#@@tabwidth -4
#@@nowrap

__version__ = "0.4"

#@+<< imports >>
#@+node:ekr.20071004090250.2: ** << imports >>
import leo.core.leoGlobals as g

# This plugin works in reduced mode without Gato.

import sys

gato_path = g.os_path_join(g.app.loadDir,'..','extensions','Gato')

if gato_path not in sys.path:
    sys.path.append(gato_path)

try:
    from Gato import Gred, Graph
    Gato_ok = True
except:
    Gato_ok = False
    Gred = None
    Graph = None
#@-<< imports >>
#@+<< version history >>
#@+node:ekr.20071004090250.3: ** << version history >>
#@@killcolor

#@+at Use and distribute under the same terms as leo itself.
# 
# 0.0 - initial version
# 
# 0.1 EKR:
# - reassigned all gnx's (by cutting and pasting the
# entire @thin node) to avoid conflict with cleo (!!)
# 
# - Add leo/extensions/Gato to sys.path before importing from Gato.
# 0.2 TNB:
#   - moved leo <-> graph stuff into separate class, much tidier not
#     mixing that with Gato stuff
#   - put x,y uAs on tnodes rather than vnodes because low level graph
#     class is a graph of tnodes (gnxs)
#   - implemented dot export functions
# 0.3 TNB:
#   - cleo background colors used in editor and graphviz export
#   - gNode class used to make API more friendly
#   - ask user if they want headings split into lines on spaces
#   - @graph headString text to indicate container node
# 0.4 EKR: changed p.link to p._link, and p.unlink to p._unlink
#@-<< version history >>

#@+others
#@+node:ekr.20071004090250.9: ** init
def init():

    # Important: Gato uses Tk
    # Using Gato with the Qt gui will hang Leo.
    ok = Gato_ok and g.app.gui.guiName() == 'tkinter'

    if ok:
        g.registerHandler('after-create-leo-frame', onCreate)
        g.plugin_signon(__name__)

    return ok
#@+node:ekr.20071004090250.10: ** onCreate
def onCreate (tag,key):
    GraphEd(key['c'])
#@+node:tbrown.20071007201356: ** class gNode
class gNode(object):
    """Simple graph node.  Acts as a dictionary, although not by descent, as
     it needs to be hashable.

     Special attributes (not in dict):
       - x x-coord of node in graph
       - y y-coord of node in graph
       - title label for node in graph, headString for leo node
       - body bodText for leo node
     """
    #@+others
    #@+node:tbrown.20071007213346: *3* __init__
    def __init__(self, *args, **kwds):
        self._dict = {}
        self.x = self.y = 10
        self.body = self.label = ""
        self.attr = {}
    #@+node:tbrown.20071007213346.1: *3* readtnode
    def readtnode(self, tn, splitLabels = True, vnode = None):
        if splitLabels:
            self.title = tn.h.replace(' ', '\n')
        else:
            self.title = tn.h
        self.body = tn.b
        self.x = getattr(tn,'unknownAttributes',{}).get('graphed',{}).get('x',0)
        self.y = getattr(tn,'unknownAttributes',{}).get('graphed',{}).get('y',0)
        self.attr.update(getattr(tn,'unknownAttributes',{}))
        self.vnode = vnode
    #@+node:tbrown.20071007220740: *3* writetnode
    def writetnode(self, nd, vnode = None):
        nd.setHeadString(self.title.replace('\n', ' '))
        nd.setTnodeText(self.body)
        if self.attr:
            if not hasattr(nd,'unknownAttributes'): nd.unknownAttributes = {}
            nd.unknownAttributes.update(self.attr)
        if hasattr(self, 'vnode'):
            if self.vnode != None and vnode != None:
                if not hasattr(vnode,'unknownAttributes'):
                    vnode.unknownAttributes = {}
                vnode.unknownAttributes.update(
                    getattr(self.vnode, 'unknownAttributes', {}))
        if (hasattr(self, 'x') and hasattr(self, 'y')
            and self.x != 0 or self.y != 0):
            if not hasattr(nd,'unknownAttributes'): nd.unknownAttributes = {}
            nd.unknownAttributes.setdefault('graphed',{}).update(
                {'x': self.x, 'y': self.y})
    #@-others
#@+node:tbrown.20071004135224.1: ** class tGraph
class tGraph:
    """Minimalist graph-of-tnodes wrapper"""
    #@+others
    #@+node:tbrown.20071004135224.2: *3* __init__
    def __init__(self):
        self._nodes = set()
        self._edges = set()
        self._gnxStr2tnode = {}
    #@+node:tbrown.20071004135224.3: *3* nodes
    def nodes(self):
        """Return set of nodes"""
        return self._nodes
    #@+node:tbrown.20071004135224.4: *3* edges
    def edges(self):
        """Return set of (node0, node1) tuples"""
        return self._edges
    #@+node:tbrown.20071004135224.5: *3* addNode
    def addNode(self, n):
        """Add n as a node"""
        self._nodes.add(n)
    #@+node:tbrown.20071004135224.6: *3* addDirectedEdge
    def addDirectedEdge(self, n0, n1):
        """Add an edge from n0 and n1 as a node"""
        self._edges.add((n0, n1))
    #@+node:tbrown.20071004141737: *3* addGraphFromPosition
    def addGraphFromPosition(self, p, splitLabels = True):
        """
        *Add* nodes and edges from the position and its descendants.

        Need to add all the nodes before trying to resolve edges from @links
        """

        self.splitLabels = splitLabels
        if '@graph' in p.h:
            for p1 in p.children():
                self._addNodesLinks(p1)
            for p1 in p.children():
                self._addLinks(p1)
        else:
            self._addNodesLinks(p)
            self._addLinks(p)
    #@+node:tbrown.20071004152905: *3* createTreeFromGraph
    def createTreeFromGraph(self, p):
        """Build tree representing graph after p, assuming our nodes are gNodes"""

        todo = set(self.nodes())

        root = p.insertAfter()
        if '@graph' in p.h:
            root.setHeadString(p.h)
        else:
            root.setHeadString('@graph ' + p.h)
        root.expand()
        pos = root.copy()

        node2tnode = {}  # for gnx lookups for making @links

        inOut = {}  # count in and out for each node
        for n0, n1 in self.edges():
            if n0 in inOut:  # out edge
                inOut[n0] = (inOut[n0][0], inOut[n0][1]+1)
            else:
                inOut[n0] = (0,1)
            if n1 in inOut:  # in edge
                inOut[n1] = (inOut[n1][0]+1, inOut[n1][1])
            else:
                inOut[n1] = (1,0)

        def nextStart(todo):
            """find the node with the fewest in edges and most
             out edges, writing these node first may give a more
             human readable tree representation of the graph"""
            maxOut = -1
            minIn = 9999
            maxIdx = None
            for i in todo:
                In = inOut[i][0]
                out = inOut[i][1]
                if In < minIn:
                    maxOut = out
                    minIn = In
                    maxIdx = i
                if In == minIn and out > maxOut:
                    maxOut = out
                    minIn = In
                    maxIdx = i
            return maxIdx

        def makeTree(pos, node0):

            nd = pos.insertAsLastChild()
            nd.expand()
            nd.setDirty()
            self._setIndex(nd)
            node2tnode[node0] = str(nd.v.fileIndex)
            node0.writetnode(nd.v, vnode = nd.v)
            #X if hasattr(node0, 'vnode'):
            #X     if node0.vnode != None:
            #X         if not hasattr(nd.v, 'unknownAttributes'):
            #X             nd.v.unknownAttributes = {}
            #X         nd.v.unknownAttributes.update(
            #X             node0.vnode.get('unknownAttributes', {}))

            desc = [i[1] for i in self.edges() if i[0] == node0]
            while desc:
                node1 = nextStart(desc)
                desc.remove(node1)

                if node1 in todo:
                    todo.remove(node1)
                    makeTree(nd, node1)
                else:
                    lnk = nd.insertAsLastChild()
                    lnk.setHeadString(
                        self._formatLink(node2tnode[node1], node1.title))

        while todo:
            next = nextStart(todo)
            todo.remove(next)
            makeTree(pos, next)

        ans = pos

        # if only one top level node, remove the holder node
        if pos.numberOfChildren() == 1:
            ch = pos.children().next()
            ch._linkAfter(pos)
            ans = ch
            pos._unlink()

        return ans
    #@+node:tbrown.20071004141737.1: *3* _addNodesLinks
    def _addNodesLinks(self, p):
        """Add nodes and simple descendent links from p"""

        gn = gNode()
        gn.readtnode(p.v, splitLabels = self.splitLabels, vnode = p.v)
        self.addNode(gn)
        self._gnxStr2tnode[str(p.v.fileIndex)] = gn

        for nd0 in p.children():
            if nd0.h.startswith('@link'): continue
            gn1 = self._addNodesLinks(nd0)
            self.addDirectedEdge(gn, gn1)

        return gn
    #@+node:tbrown.20071004141737.2: *3* _addLinks
    def _addLinks(self, p):
        """Collect the @links from p, now we know the nodes are in
        self._gnxStr2tnode"""

        s0 = str(p.v.fileIndex)
        for nd0 in p.children():
            if nd0.h.startswith('@link'):
                s1 = self._indexStrFromStr(nd0.h)
                try:
                    fnd = self._gnxStr2tnode[s0]
                    tnd = self._gnxStr2tnode[s1]
                    self.addDirectedEdge(fnd, tnd)
                except:  # @link node went stale
                    g.es('Broken %s' % nd0.h)
                    raise
            else:
                self._addLinks(nd0)
    #@+node:tbrown.20071004141911: *3* _setIndex
    def _setIndex(self, p):
        """fresh tnodes may not have .fileIndex, this adds it"""
        try:
            theId,time,n = p.v.fileIndex
        except TypeError:
            p.v.fileIndex = g.app.nodeIndices.getNewIndex()
    #@+node:tbrown.20071004141931: *3* _indexStrFromStr
    def _indexStrFromStr(self, s):
        """isolate the '(...)' part of s"""
        return s[s.find('(') : s.find(')')+1]
    #@+node:tbrown.20071004155803: *3* _formatLink
    def _formatLink(self, tid, hs):
        """format @link headString,
        strips '(' and ')' so _indexStrFromStr works"""
        return '@link %s %s' % (hs.replace('(','[').replace(')',']'),str(tid))
    #@-others
#@+node:tbrown.20071004225829: ** class tGraphUtil
class tGraphUtil(tGraph):
    """Misc. utility functions on a tGraph"""

    #@+others
    #@+node:tbrown.20071004225829.1: *3* dotStrFromPosition
    def dotStrFromPosition(self,p, includeXY = True):
        """return complete Graphviz dot format graph text"""
        self.addGraphFromPosition(p)
        node = {}  # gnx to node number map
        nodes = []
        for n,i in enumerate(self.nodes()):
            node[i]=n
            xy = ""
            if includeXY:
                xy += ' pos="%d,%d"' % (i.x, i.y)
            color = ''
            try:
                color = i.vnode.unknownAttributes['annotate']['bg']
                if color:

                    color = ' style="filled" fillcolor="%s"' % color
            except:
                color = ''
            nodes.append('n%s [label="%s"%s%s]' % (
                n, i.title.replace('\n', '\\n'), xy, color))
        edges = []
        for f,t in self.edges():
            edges.append('n%d -> n%d' % (node[f],node[t]))

        return 'digraph G {\n%s\n\n%s\n}' % ('\n'.join(nodes), '\n'.join(edges))
    #@-others
#@+node:ekr.20071004090250.11: ** class GraphEd
class GraphEd:

    '''A per-commander class that recolors outlines.'''

    #@+others
    #@+node:ekr.20071004090250.12: *3* __init__
    def __init__ (self,c):

        self.dictName = 'graphed'  # for uA dictionary

        self.c = c
        table = []
        if Gato_ok: table.append(("Edit node as graph",None,self.editGraph))
        table += (
                 # BROKEN ("Edit whole tree as graph",None,self.editWholeTree),
                 ("Copy link to clipboard",None,self.copyLink),
                 ("Follow link",None,self.followLink),
                 ("Export to Graphviz dot format",None,self.dotFile),
                 ("Make Graphviz dot node",None,self.dotNode),
                 # CAN'T ("Layout using Graphviz dot",None,self.undone), # FIXME
                 )
        c.frame.menu.createNewMenu('Graph', 'Outline')
        c.frame.menu.createMenuItemsFromTable('Graph', table)
    #@+node:ekr.20071004090250.13: *3* close
    def close(self, tag, key):
        "unregister handlers on closing commander"

        if self.c != key['c']: return  # not our problem

        # for i in self.handlers:
        #     pass # FIXME no handlers?

    #@+node:ekr.20071004090250.14: *3* setIndex
    def setIndex(self, p):
        try:
            theId,time,n = p.v.fileIndex
        except TypeError:
            p.v.fileIndex = g.app.nodeIndices.getNewIndex()
    #@+node:ekr.20071004090250.15: *3* indexStrFromStr
    def indexStrFromStr(self, s):
        """isolate the '(...)' part of s"""
        return s[s.find('(') : s.find(')')+1]
    #@+node:ekr.20071004090250.16: *3* attributes...
    #@+node:ekr.20071004090250.17: *4* getat
    def getat(self, node, attrib):

        if (not hasattr(node,'unknownAttributes') or
            not node.unknownAttributes.has_key(self.dictName) or
            not type(node.unknownAttributes[self.dictName]) == type({}) or
            not node.unknownAttributes[self.dictName].has_key(attrib)):

            return None

        return node.unknownAttributes[self.dictName][attrib]
    #@+node:ekr.20071004090250.18: *4* setat
    def setat(self, node, attrib, val):
        "new attrbiute setter"

        #X isDefault = self.testDefault(attrib, val)

        if (not hasattr(node,'unknownAttributes') or
            not node.unknownAttributes.has_key(self.dictName) or
            type(node.unknownAttributes[self.dictName]) != type({})):
            # dictionary doesn't exist

            #X if isDefault:
            #X     return  # don't create dict. for default value

            if not hasattr(node,'unknownAttributes'):  # node has no unknownAttributes
                node.unknownAttributes = {}
                node.unknownAttributes[self.dictName] = {}
            else:  # our private dictionary isn't present
                if (not node.unknownAttributes.has_key(self.dictName) or
                    type(node.unknownAttributes[self.dictName]) != type({})):
                    node.unknownAttributes[self.dictName] = {}

            node.unknownAttributes[self.dictName][attrib] = val

            return

        # dictionary exists

        node.unknownAttributes[self.dictName][attrib] = val

        #X if isDefault:  # check if all default, if so drop dict.
        #X     self.dropEmpty(node, dictOk = True)
    #@+node:ekr.20071004090250.25: *3* safe_del
    def safe_del(self, d, k):
        "delete a key from a dict. if present"
        if d.has_key(k): del d[k]
    #@+node:ekr.20071004090250.26: *3* editGraph
    def editGraph(self, event=None, pos = None):

        c = self.c

        if pos == None:
            p = c.p
        else:
            p = pos

        self.p = p

        tgraph = tGraph()
        splitL = g.app.gui.runAskYesNoDialog(self.c,
            'Split labels with spaces?',
            'Split labels with spaces?'
        )

        tgraph.addGraphFromPosition(p, splitLabels = (splitL == 'yes'))

        #X # make sure fileIndex is set on everything
        #X for p2 in p.self_and_subtree():
        #X     self.setIndex(p2)

        self.graph = Graph()
        # graph.simple = 0  # only blocks self loops?
        self.graph.directed = 1

        self.tnode2gnode = {}
        self.gnode2attribs = {}


        self.loadGraph(self.graph, tgraph)
        # self.loadGraphLinks(self.graph, p)

        editor = Gred.SAGraphEditor(g.app.root)
        self.editor = editor
        editor.dirty = 0
        editor.cVertexDefault = '#e8e8ff'
        editor.cEdgeDefault = '#a0a0a0'
        editor.cLabelDefault = 'black'
        editor.leoQuit = self.exiting
        editor.master.protocol("WM_DELETE_WINDOW", self.exiting)

        editor.ShowGraph(self.graph, "test")
        for vert in self.graph.Vertices():
            if hasattr(self.gnode2attribs[vert], 'vnode'):
                nd = self.gnode2attribs[vert].vnode
                if hasattr(nd, 'unknownAttributes'):
                    if 'annotate' in nd.unknownAttributes:
                        if 'bg' in nd.unknownAttributes['annotate']:
                            editor.SetVertexColor(vert,
                                nd.unknownAttributes['annotate']['bg'])

        # layout = Embedder.BFSTreeEmbedder()
        # layout.Embed(self.editor)
        # self.editor.grab_set()
        # self.editor.focus_force()
        # g.app.root.wait_window(self.editor)
    #@+node:ekr.20071004090250.27: *3* editWholeTree
    #@+at
    # 
    # This doesn't work
    # 
    # def editWholeTree(self, event=None):
    #     c = self.c
    #     g.pr(c.rootPosition().h)
    #     self.editGraph(pos = c.rootPosition())
    #@+node:ekr.20071004090250.28: *3* loadGraph
    def loadGraph(self, graph, tgraph):

        for nd in tgraph.nodes():
            vid = graph.AddVertex()
            self.tnode2gnode[nd] = vid
            self.gnode2attribs[vid] = nd
            graph.SetLabeling(vid, nd.title)
            graph.SetEmbedding(vid, nd.x, nd.y)
        for nd0, nd1 in tgraph.edges():
            graph.AddEdge(self.tnode2gnode[nd0],
                          self.tnode2gnode[nd1])
    #@+node:ekr.20071004090250.30: *3* exiting
    def exiting(self):
        ans = g.app.gui.runAskYesNoCancelDialog(
            self.c, 'Load changes?',
            'Load changes from graph editor?')
        if ans == 'yes':
            self.saveGraph(self.p, self.graph)
        if ans in ('yes', 'no'):
            self.editor.destroy()
            self.editor.master.withdraw()  # ???
        # if ans == cancel do nothing
    #@+node:ekr.20071004090250.31: *3* saveGraph
    def saveGraph(self, p, graph):

        def label(i):
            """change undefined (numeric) labels from ints to strs"""
            return str(graph.GetLabeling(i))

        c = self.c
        tgraph = tGraph()
        gnode2nottnode = {}
        for node in graph.Vertices():
            tn = gNode()
            gnode2nottnode[node] = tn
            tn.title = label(node)
            x = graph.GetEmbedding(node)
            tn.x, tn.y = x.x,x.y
            if node in self.gnode2attribs:
                tn.body = self.gnode2attribs[node].body
                tn.vnode = self.gnode2attribs[node].vnode
                tn.attr.update(self.gnode2attribs[node].attr)

            tgraph.addNode(tn)

        for node0, node1 in graph.Edges():
            tgraph.addDirectedEdge(gnode2nottnode[node0],gnode2nottnode[node1])

        newp = tgraph.createTreeFromGraph(p)

        c.setHeadString(p, 'OLD: ' + p.h)
        p.setDirty()
        c.selectPosition(p)
        c.contractNode()

        c.selectPosition(newp)
        c.setChanged(True)
        c.redraw()
    #@+node:ekr.20071004090250.32: *3* copyLink
    def copyLink(self, event = None):
        c = self.c
        p = c.p
        self.setIndex(p)
        nn = p.insertAfter()
        nn.setHeadString(self.formatLink(p.v.fileIndex, p.h))
        c.selectPosition(nn)
        c.cutOutline()
        c.selectPosition(p)
        g.es('Link copied to clipboard')
    #@+node:ekr.20071004090250.33: *3* followLink
    def followLink(self, event = None):
        c = self.c
        s = c.p.h
        s = self.indexStrFromStr(s)
        for p in c.all_positions():
            if self.indexStrFromStr(str(p.v.fileIndex)) == s:
                c.selectPosition(p)
                break
        g.es('Not found')
    #@+node:ekr.20071004090250.34: *3* formatLink
    def formatLink(self, tid, hs):
        return '@link %s %s' % (hs.replace('(','[').replace(')',']'),str(tid))
    #@+node:tbrown.20071004225829.2: *3* dotNode
    def dotNode(self, event=None):
        c = self.c
        p = c.p
        t = p.h
        tg = tGraphUtil()
        dot = tg.dotStrFromPosition(p)
        p = p.insertAfter()
        c.setHeadString(p, 'DOT FORMAT: ' + t)
        c.setBodyString(p, dot)
        c.selectPosition(p)
    #@+node:tbrown.20071005092239: *3* dotFile
    def dotFile(self, event=None):
        c = self.c
        p = c.p
        t = p.h
        tg = tGraphUtil()
        dot = tg.dotStrFromPosition(p)
        fn = g.app.gui.runSaveFileDialog(
            '',
            'Save dot file to' ,
            [('Dot', '*.dot'), ('All', '*.*')],
            '.dot'
            )
        if not fn.lower().endswith('.dot'):
            fn += '.dot'
        file(fn, 'w').write(dot)
        g.es('Wrote %s' % fn)
    #@+node:ekr.20071004090250.35: *3* undone
    def undone(self, event = None):
        g.app.gui.runAskOkDialog(self.c, 'Not implemented',
            "Sorry, that's not implemented yet.")
    #@-others
#@-others
#@-leo
