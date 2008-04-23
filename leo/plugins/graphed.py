#@+leo-ver=4-thin
#@+node:ekr.20071004090250:@thin graphed.py
#@<< docstring >>
#@+node:ekr.20071004090250.1:<< docstring >>
"""
graphed.py  -- Edit graphs visually

Graph commands are in the Outline/Graph submenu.
See http://leo.zwiki.org/GraphEd for documentation.

Graph editor component based on the Gred graph editor from the
Gato Graph Animation Toolbox at http://gato.sourceforge.net/

Leo plugin by Terry Brown terry_n_brown@yahoo.com
"""
#@-node:ekr.20071004090250.1:<< docstring >>
#@nl

#@@language python
#@@tabwidth -4
#@@nowrap

__version__ = "0.4"

#@<< imports >>
#@+node:ekr.20071004090250.2:<< imports >>
import leoGlobals as g
import leoPlugins
import leoTkinterTree

Tk = g.importExtension('Tkinter',pluginName=__name__,verbose=True)

import sys

gato_path = g.os_path_join(g.app.loadDir,'..','extensions','Gato')

if gato_path not in sys.path:
    sys.path.append(gato_path)

try:
    from Gato import Gred, Embedder, Graph, GraphEditor, DataStructures
    Gato_ok = True
except:
    Gato_ok = False
#@-node:ekr.20071004090250.2:<< imports >>
#@nl
#@<< version history >>
#@+node:ekr.20071004090250.3:<< version history >>
#@@killcolor

#@+at 
#@nonl
# Use and distribute under the same terms as leo itself.
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
#@-at
#@-node:ekr.20071004090250.3:<< version history >>
#@nl

#@+others
#@+node:ekr.20071004090250.9:init
def init():

    if not Gato_ok:
        g.es('graphed: Gato import failed, functions reduced',color='red')

    leoPlugins.registerHandler('after-create-leo-frame', onCreate)
    g.plugin_signon(__name__)

    return True
#@-node:ekr.20071004090250.9:init
#@+node:ekr.20071004090250.10:onCreate
def onCreate (tag,key):
    GraphEd(key['c'])
#@-node:ekr.20071004090250.10:onCreate
#@+node:tbrown.20071007201356:class gNode
class gNode(object):
    """Simple graph node.  Acts as a dictionary, although not by descent, as
     it needs to be hashable.

     Special attributes (not in dict):
       - x x-coord of node in graph
       - y y-coord of node in graph
       - title label for node in graph, headString for leo node
       - body bodText for leo node
     """
    #@    @+others
    #@+node:tbrown.20071007213346:__init__
    def __init__(self, *args, **kwds):
        self._dict = {}
        self.x = self.y = 10
        self.body = self.label = ""
        self.attr = {}
    #@-node:tbrown.20071007213346:__init__
    #@+node:tbrown.20071007213346.1:readtnode
    def readtnode(self, tn, splitLabels = True, vnode = None):
        if splitLabels:
            self.title = tn.headString.replace(' ', '\n')
        else:
            self.title = tn.headString
        self.body = tn.bodyString
        self.x = getattr(tn,'unknownAttributes',{}).get('graphed',{}).get('x',0)
        self.y = getattr(tn,'unknownAttributes',{}).get('graphed',{}).get('y',0)
        self.attr.update(getattr(tn,'unknownAttributes',{}))
        self.vnode = vnode
    #@-node:tbrown.20071007213346.1:readtnode
    #@+node:tbrown.20071007220740:writetnode
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
    #@-node:tbrown.20071007220740:writetnode
    #@-others
#@-node:tbrown.20071007201356:class gNode
#@+node:tbrown.20071004135224.1:class tGraph
class tGraph:
    """Minimalist graph-of-tnodes wrapper"""
    #@    @+others
    #@+node:tbrown.20071004135224.2:__init__
    def __init__(self):
        self._nodes = set()
        self._edges = set()
        self._gnxStr2tnode = {}
    #@-node:tbrown.20071004135224.2:__init__
    #@+node:tbrown.20071004135224.3:nodes
    def nodes(self):
        """Return set of nodes"""
        return self._nodes
    #@-node:tbrown.20071004135224.3:nodes
    #@+node:tbrown.20071004135224.4:edges
    def edges(self):
        """Return set of (node0, node1) tuples"""
        return self._edges
    #@-node:tbrown.20071004135224.4:edges
    #@+node:tbrown.20071004135224.5:addNode
    def addNode(self, n):
        """Add n as a node"""
        self._nodes.add(n)
    #@-node:tbrown.20071004135224.5:addNode
    #@+node:tbrown.20071004135224.6:addDirectedEdge
    def addDirectedEdge(self, n0, n1):
        """Add an edge from n0 and n1 as a node"""
        self._edges.add((n0, n1))
    #@-node:tbrown.20071004135224.6:addDirectedEdge
    #@+node:tbrown.20071004141737:addGraphFromPosition
    def addGraphFromPosition(self, p, splitLabels = True):
        """
        *Add* nodes and edges from the position and its descendants.

        Need to add all the nodes before trying to resolve edges from @links
        """

        self.splitLabels = splitLabels
        if '@graph' in p.headString():
            for p1 in p.children_iter():
                self._addNodesLinks(p1)
            for p1 in p.children_iter():
                self._addLinks(p1)
        else:
            self._addNodesLinks(p)
            self._addLinks(p)
    #@-node:tbrown.20071004141737:addGraphFromPosition
    #@+node:tbrown.20071004152905:createTreeFromGraph
    def createTreeFromGraph(self, p):
        """Build tree representing graph after p, assuming our nodes are gNodes"""

        todo = set(self.nodes())

        root = p.insertAfter()
        if '@graph' in p.headString():
            root.setHeadString(p.headString())
        else:
            root.setHeadString('@graph ' + p.headString())
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

            # This does not work, all nodes become clones and things
            # get parsed more than once.
            #
            # t = None
            # if hasattr(node0, 'vnode'):
            #     t = node0.vnode.t

            nd = pos.insertAsLastChild()
            nd.expand()
            nd.setDirty()
            self._setIndex(nd)
            node2tnode[node0] = str(nd.v.t.fileIndex)
            node0.writetnode(nd.v.t, vnode = nd.v)
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
            ch = pos.children_iter().next()
            ch._linkAfter(pos)
            ans = ch
            pos._unlink()

        return ans
    #@-node:tbrown.20071004152905:createTreeFromGraph
    #@+node:tbrown.20071004141737.1:_addNodesLinks
    def _addNodesLinks(self, p):
        """Add nodes and simple descendent links from p"""

        gn = gNode()
        gn.readtnode(p.v.t, splitLabels = self.splitLabels, vnode = p.v)
        self.addNode(gn)
        self._gnxStr2tnode[str(p.v.t.fileIndex)] = gn

        for nd0 in p.children_iter():
            if nd0.headString().startswith('@link'): continue
            gn1 = self._addNodesLinks(nd0)
            self.addDirectedEdge(gn, gn1)

        return gn
    #@-node:tbrown.20071004141737.1:_addNodesLinks
    #@+node:tbrown.20071004141737.2:_addLinks
    def _addLinks(self, p):
        """Collect the @links from p, now we know the nodes are in
        self._gnxStr2tnode"""

        s0 = str(p.v.t.fileIndex)
        for nd0 in p.children_iter():
            if nd0.headString().startswith('@link'):
                s1 = self._indexStrFromStr(nd0.headString())
                try:
                    fnd = self._gnxStr2tnode[s0]
                    tnd = self._gnxStr2tnode[s1]
                    self.addDirectedEdge(fnd, tnd)
                except:  # @link node went stale
                    g.es('Broken %s' % nd0.headString())
                    raise
            else:
                self._addLinks(nd0)
    #@-node:tbrown.20071004141737.2:_addLinks
    #@+node:tbrown.20071004141911:_setIndex
    def _setIndex(self, p):
        """fresh tnodes may not have .fileIndex, this adds it"""
        try:
            theId,time,n = p.v.t.fileIndex
        except TypeError:
            p.v.t.fileIndex = g.app.nodeIndices.getNewIndex()
    #@-node:tbrown.20071004141911:_setIndex
    #@+node:tbrown.20071004141931:_indexStrFromStr
    def _indexStrFromStr(self, s):
        """isolate the '(...)' part of s"""
        return s[s.find('(') : s.find(')')+1]
    #@-node:tbrown.20071004141931:_indexStrFromStr
    #@+node:tbrown.20071004155803:_formatLink
    def _formatLink(self, tid, hs):
        """format @link headString,
        strips '(' and ')' so _indexStrFromStr works"""
        return '@link %s %s' % (hs.replace('(','[').replace(')',']'),str(tid))
    #@-node:tbrown.20071004155803:_formatLink
    #@-others
#@-node:tbrown.20071004135224.1:class tGraph
#@+node:tbrown.20071004225829:class tGraphUtil
class tGraphUtil(tGraph):
    """Misc. utility functions on a tGraph"""

    #@    @+others
    #@+node:tbrown.20071004225829.1:dotStrFromPosition
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
    #@-node:tbrown.20071004225829.1:dotStrFromPosition
    #@-others
#@-node:tbrown.20071004225829:class tGraphUtil
#@+node:ekr.20071004090250.11:class GraphEd
class GraphEd:

    '''A per-commander class that recolors outlines.'''

    #@    @+others
    #@+node:ekr.20071004090250.12:__init__
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
    #@-node:ekr.20071004090250.12:__init__
    #@+node:ekr.20071004090250.13:close
    def close(self, tag, key):
        "unregister handlers on closing commander"

        if self.c != key['c']: return  # not our problem

        for i in self.handlers:
            pass # FIXME no handlers?

    #@-node:ekr.20071004090250.13:close
    #@+node:ekr.20071004090250.14:setIndex
    def setIndex(self, p):
        try:
            theId,time,n = p.v.t.fileIndex
        except TypeError:
            p.v.t.fileIndex = g.app.nodeIndices.getNewIndex()
    #@-node:ekr.20071004090250.14:setIndex
    #@+node:ekr.20071004090250.15:indexStrFromStr
    def indexStrFromStr(self, s):
        """isolate the '(...)' part of s"""
        return s[s.find('(') : s.find(')')+1]
    #@-node:ekr.20071004090250.15:indexStrFromStr
    #@+node:ekr.20071004090250.16:attributes...
    #@+node:ekr.20071004090250.17:getat
    def getat(self, node, attrib):

        if (not hasattr(node,'unknownAttributes') or
            not node.unknownAttributes.has_key(self.dictName) or
            not type(node.unknownAttributes[self.dictName]) == type({}) or
            not node.unknownAttributes[self.dictName].has_key(attrib)):

            return None

        return node.unknownAttributes[self.dictName][attrib]
    #@nonl
    #@-node:ekr.20071004090250.17:getat
    #@+node:ekr.20071004090250.18:setat
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
    #@-node:ekr.20071004090250.18:setat
    #@+node:ekr.20071004090250.19:probably junk
    #@+at
    # 
    # These probably aren't needed for this app, but maybe we'll need to
    # offer an option to strip our uAs
    #@-at
    #@+node:ekr.20071004090250.20:delUD
    def delUD (self,node,udict=None):

        ''' Remove our dict from the node'''

        if udict == None: udict = self.dictName
        if (hasattr(node,"unknownAttributes" ) and 
            node.unknownAttributes.has_key(udict)):

            del node.unknownAttributes[udict]
    #@-node:ekr.20071004090250.20:delUD
    #@+node:ekr.20071004090250.21:hasUD
    def hasUD (self,node,udict=None):

        ''' Return True if the node has an UD.'''

        if udict == None: udict = self.dictName
        return (
            hasattr(node,"unknownAttributes") and
            node.unknownAttributes.has_key(udict) and
            type(node.unknownAttributes.get(udict)) == type({}) # EKR
        )
    #@-node:ekr.20071004090250.21:hasUD
    #@+node:ekr.20071004090250.22:testDefault
    def testDefault(self, attrib, val):
        "return true if val is default val for attrib"

        # if type(val) == self.typePickle: val = val.get()
        # not needed as only dropEmpty would call with such a thing, and it checks first

        return attrib == "priority" and val == 9999 or val == ""
    #@nonl
    #@-node:ekr.20071004090250.22:testDefault
    #@+node:ekr.20071004090250.23:dropEmptyAll
    def dropEmptyAll(self):
        "search whole tree for empty nodes"

        cnt = 0
        for p in self.c.allNodes_iter(): 
            if self.dropEmpty(p.v): cnt += 1

        g.es("cleo: dropped %d empty dictionaries" % cnt)
    #@-node:ekr.20071004090250.23:dropEmptyAll
    #@+node:ekr.20071004090250.24:dropEmpty
    def dropEmpty(self, node, dictOk = False):

        if (dictOk or
            hasattr(node,'unknownAttributes') and
            node.unknownAttributes.has_key(self.dictName) and
            type(node.unknownAttributes[self.dictName]) == type({})):

            isDefault = True
            for ky, vl in node.unknownAttributes[self.dictName].iteritems():
                if type(vl) == self.typePickle:
                    node.unknownAttributes[self.dictName][ky] = vl = vl.get()
                if not self.testDefault(ky, vl):
                    isDefault = False
                    break

            if isDefault:  # no non-defaults seen, drop the whole cleo dictionary
                del node.unknownAttributes[self.dictName]
                self.c.setChanged(True)
                return True

        return False
    #@nonl
    #@-node:ekr.20071004090250.24:dropEmpty
    #@-node:ekr.20071004090250.19:probably junk
    #@-node:ekr.20071004090250.16:attributes...
    #@+node:ekr.20071004090250.25:safe_del
    def safe_del(self, d, k):
        "delete a key from a dict. if present"
        if d.has_key(k): del d[k]
    #@nonl
    #@-node:ekr.20071004090250.25:safe_del
    #@+node:ekr.20071004090250.26:editGraph
    def editGraph(self, event=None, pos = None):

        c = self.c

        if pos == None:
            p = c.currentPosition()
        else:
            p = pos

        self.p = p

        tgraph = tGraph()
        splitL = g.app.gui.runAskYesNoDialog(self.c,
            'Split labels with spaces?') 
        tgraph.addGraphFromPosition(p, splitLabels = (splitL == 'yes'))

        #X # make sure fileIndex is set on everything
        #X for p2 in p.self_and_subtree_iter():
        #X     self.setIndex(p2)

        self.graph = Graph.Graph()
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
    #@-node:ekr.20071004090250.26:editGraph
    #@+node:ekr.20071004090250.27:editWholeTree
    #@+at
    # 
    # This doesn't work
    # 
    # def editWholeTree(self, event=None):
    #     c = self.c
    #     print c.rootPosition().headString()
    #     self.editGraph(pos = c.rootPosition())
    #@-at
    #@-node:ekr.20071004090250.27:editWholeTree
    #@+node:ekr.20071004090250.28:loadGraph
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
    #@-node:ekr.20071004090250.28:loadGraph
    #@+node:ekr.20071004090250.30:exiting
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
    #@-node:ekr.20071004090250.30:exiting
    #@+node:ekr.20071004090250.31:saveGraph
    def saveGraph(self, p, graph):

        def label(i):
             """change undefined (numeric) labels from ints to strs"""
             return str(graph.GetLabeling(i))

        c = self.c
        c.beginUpdate()
        try:

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

            c.setHeadString(p, 'OLD: ' + p.headString())
            p.setDirty()
            c.selectPosition(p)
            c.contractNode()

            c.selectPosition(newp)

        finally:
            c.setChanged(True)
            c.endUpdate()
    #@-node:ekr.20071004090250.31:saveGraph
    #@+node:ekr.20071004090250.32:copyLink
    def copyLink(self, event = None):
        c = self.c
        p = c.currentPosition()
        self.setIndex(p)
        nn = p.insertAfter()
        nn.setHeadString(self.formatLink(p.v.t.fileIndex, p.headString()))
        c.selectPosition(nn)
        c.cutOutline()
        c.selectPosition(p)
        g.es('Link copied to clipboard')
    #@-node:ekr.20071004090250.32:copyLink
    #@+node:ekr.20071004090250.33:followLink
    def followLink(self, event = None):
        c = self.c
        s = c.currentPosition().headString()
        s = self.indexStrFromStr(s)
        for p in c.allNodes_iter():
            if self.indexStrFromStr(str(p.v.t.fileIndex)) == s:
                c.selectPosition(p)
                break
        g.es('Not found')
    #@-node:ekr.20071004090250.33:followLink
    #@+node:ekr.20071004090250.34:formatLink
    def formatLink(self, tid, hs):
        return '@link %s %s' % (hs.replace('(','[').replace(')',']'),str(tid))
    #@-node:ekr.20071004090250.34:formatLink
    #@+node:tbrown.20071004225829.2:dotNode
    def dotNode(self, event=None):
        c = self.c
        p = c.currentPosition()
        t = p.headString()
        tg = tGraphUtil()
        dot = tg.dotStrFromPosition(p)
        p = p.insertAfter()
        c.setHeadString(p, 'DOT FORMAT: ' + t)
        c.setBodyString(p, dot)
        c.selectPosition(p)
    #@-node:tbrown.20071004225829.2:dotNode
    #@+node:tbrown.20071005092239:dotFile
    def dotFile(self, event=None):
        c = self.c
        p = c.currentPosition()
        t = p.headString()
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
    #@-node:tbrown.20071005092239:dotFile
    #@+node:ekr.20071004090250.35:undone
    def undone(self, event = None):
        g.app.gui.runAskOkDialog(self.c, 'Not implemented',
            "Sorry, that's not implemented yet.")
    #@-node:ekr.20071004090250.35:undone
    #@-others
#@nonl
#@-node:ekr.20071004090250.11:class GraphEd
#@-others
#@-node:ekr.20071004090250:@thin graphed.py
#@-leo
