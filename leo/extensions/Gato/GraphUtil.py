################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#
#	file:   Graph.py
#	author: Alexander Schliep (schliep@molgen.mpg.de)
#
#       Copyright (C) 1998-2005, Alexander Schliep, Winfried Hochstaettler and 
#       Copyright 1998-2001 ZAIK/ZPR, Universitaet zu Koeln
#                                   
#       Contact: schliep@molgen.mpg.de, wh@zpr.uni-koeln.de             
#
#       Information: http://gato.sf.net
#
#       This library is free software; you can redistribute it and/or
#       modify it under the terms of the GNU Library General Public
#       License as published by the Free Software Foundation; either
#       version 2 of the License, or (at your option) any later version.
#
#       This library is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#       Library General Public License for more details.
#
#       You should have received a copy of the GNU Library General Public
#       License along with this library; if not, write to the Free
#       Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#
#
#       This file is version $Revision: 1.1 $ 
#                       from $Date: 2007/10/04 14:36:39 $
#             last change by $Author: edream $.
#
################################################################################

import types
import StringIO
from string import split
import string
from GatoGlobals import *
from Graph import Graph
from DataStructures import Point2D, VertexLabeling, EdgeLabeling, EdgeWeight, VertexWeight, Queue
import logging
log = logging.getLogger("GraphUtil.py")


################################################################################
#
# Syntactic Sugar
#
################################################################################
def Vertices(G):
    """ Returns the vertices of G. Hide method call """
    return G.vertices
    
def Edges(G):
    """ Returns the edges of G. Hide method call """
    return G.Edges()
    
    
    ################################################################################
    #
    # Basic algorithms
    #
    ################################################################################
    
def BFS(G,root,direction='forward'):
    """ Calculate BFS distances and predecessor without showing animations. 
        If G is directed, direction does matter:
    
        - 'forward'  BFS will use outgoing edges
        - 'backward' BFS will use incoming edges
    
        It uses gInfinity (from GatoGlobals.py) as infinite distance.
        returns (dist,pred) """
    
    Q = Queue()
    d = {}
    pred = {}
    
    for v in G.vertices:
        d[v] = gInfinity
    d[root] = 0
    pred[root] = root
    
    Q.Append(root)
    
    while Q.IsNotEmpty():
        v = Q.Top()
        if G.QDirected() == 1 and direction == 'backward':
            nbh = G.InNeighbors(v)
        else:
            nbh = G.Neighborhood(v)
            
        for w in nbh:
            if d[w] == gInfinity:
                d[w] = d[v] + 1
                pred[w] = v
                Q.Append(w)
                
    return (d,pred)
    
    
def ConnectedComponents(G):
    """ Compute the connected components of the undirected graph G.
        Returns a list of lists of vertices. """
    
    
    result = []
    visited = {}
    for v in G.vertices:
        visited[v] = None
        
    for root in G.vertices:
        if visited[root] is not None:
            continue
        else: # Found a new component
            component = [root]
            visited[root] = 1
            
            Q = Queue()
            Q.Append(root)
            
            while Q.IsNotEmpty():
                v = Q.Top()
                nbh = G.Neighborhood(v)
                for w in nbh:
                    if visited[w] == None:
                        visited[w] = 1
                        Q.Append(w)
                        component.append(w)
                        
            result.append(component)
            
    return result
    
    
    
    ################################################################################
    #
    # GraphInformer
    #
    ################################################################################
    
    
class GraphInformer:
    """ Provides information about edges and vertices of a graph.
        Used as argument for GraphDisplay.RegisterGraphInformer() """
    
    def __init__(self,G):
        self.G = G
        self.info = ""
        
    def DefaultInfo(self):
        """ Provide an default text which is shown when no edge/vertex
            info is displayed """  
        return self.info
        
    def VertexInfo(self,v):
        """ Provide an info text for vertex v """
        t = self.G.GetEmbedding(v)
        return "Vertex %d at position (%d,%d)" % (v, int(t.x), int(t.y))
        
    def EdgeInfo(self,tail,head):
        """ Provide an info text for edge (tail,head)  """        
        return "Edge (%d,%d)" % (tail, head) 
        
    def SetDefaultInfo(self, info=""):
        self.info = info
        
        
class WeightedGraphInformer(GraphInformer):
    """ Provides information about weighted edges and vertices of a graph.
        Used as argument for GraphDisplay.RegisterGraphInformer() """
    
    def __init__(self,G,weightDesc="weight"):
        """ G is the graph we want to supply information about and weightDesc
            a textual interpretation of the weight """
        GraphInformer.__init__(self,G)
        self.weightDesc = weightDesc
        
    def EdgeInfo(self,tail,head):
        """ Provide an info text for weighted edge (tail,head)  """  
        # How to handle undirected graph
        if self.G.QDirected() == 0:
            try:
                w = self.G.GetEdgeWeight(0,tail, head)
            except KeyError:
                w = self.G.GetEdgeWeight(0, head, tail)
        else:
            w = self.G.GetEdgeWeight(0, tail, head)
        if self.G.edgeWeights[0].QInteger():
            return "Edge (%d,%d) %s: %d" % (tail, head, self.weightDesc, w) 
        else:
            return "Edge (%d,%d) %s: %f" % (tail, head, self.weightDesc, w) 
            
            
class MSTGraphInformer(WeightedGraphInformer):
    def __init__(self,G,T):
        WeightedGraphInformer.__init__(self,G)
        self.T = T
        
    def DefaultInfo(self):
        """ Provide an default text which is shown when no edge/vertex
            info is displayed """  
        return "Tree has %d vertices and weight %5.2f" % (self.T.Order(),self.T.Weight())
        
        
class FlowGraphInformer(GraphInformer):
    def __init__(self,G,flow):
        GraphInformer.__init__(self,G)
        self.flow   = flow
        self.cap    = flow.cap
        self.res    = flow.res
        self.excess = flow.excess
        
    def EdgeInfo(self,v,w):
        return "Edge (%d,%d) - flow: %d of %d" % (v,w, self.flow[(v,w)], self.cap[(v,w)])
        
    def VertexInfo(self,v):
        tmp = self.excess[v]
        if tmp == gInfinity:
            str1 = "Infinity"
        elif tmp == -gInfinity:
            str1 = "-Infinity"
        else:
            str1 = "%d"%tmp
            
        return "Vertex %d - excess: %s" % (v, str1)
        
class ResidualGraphInformer(FlowGraphInformer):

    def EdgeInfo(self,v,w):
        return "Edge (%d,%d) - residual capacity: %d" % (v, w, self.res[(v,w)])
        
        ################################################################################
        #
        # FILE I/O
        #
        ################################################################################
        
def OpenCATBoxGraph(_file):
    """ Reads in a graph from file fileName. File-format is supposed
        to be from old CATBOX++ (*.cat) """
    G = Graph()
    E = VertexLabeling()
    W = EdgeWeight(G)
    L = VertexLabeling()
    
    # get file from name or file object
    graphFile=None
    if type(_file) in types.StringTypes:
        graphFile = open(_file, 'r')
    elif type(_file)==types.FileType or issubclass(_file.__class__,StringIO.StringIO):
        graphFile=_file
    else:
        raise Exception("got wrong argument")
        
    lineNr = 1
    
    firstVertexLineNr = -1    
    lastVertexLineNr  = -1
    firstEdgeLineNr   = -1
    lastEdgeLineNr    = -1
    intWeights        = 0
    
    while 1:
    
        line = graphFile.readline()
        
        if not line:
            break
            
        if lineNr == 2: # Read directed and euclidian
            splitLine = split(line[:-1],';')	    
            G.directed = eval(split(splitLine[0],':')[1])
            G.simple = eval(split(splitLine[1],':')[1])
            G.euclidian = eval(split(splitLine[2],':')[1])
            intWeights = eval(split(splitLine[3],':')[1])
            nrOfEdgeWeights = eval(split(splitLine[4],':')[1])
            nrOfVertexWeights = eval(split(splitLine[5],':')[1])
            for i in xrange(nrOfEdgeWeights):
                G.edgeWeights[i] = EdgeWeight(G)
            for i in xrange(nrOfVertexWeights):
                G.vertexWeights[i] = VertexWeight(G)
                
                
        if lineNr == 5: # Read nr of vertices
            nrOfVertices = eval(split(line[:-2],':')[1]) # Strip of "\n" and ; 
            firstVertexLineNr = lineNr + 1
            lastVertexLineNr  = lineNr + nrOfVertices
            
        if  firstVertexLineNr <= lineNr and lineNr <= lastVertexLineNr: 
            splitLine = split(line[:-1],';')
            v = G.AddVertex()
            x = eval(split(splitLine[1],':')[1])
            y = eval(split(splitLine[2],':')[1])
            for i in xrange(nrOfVertexWeights):
                w = eval(split(splitLine[3+i],':')[1])
                G.vertexWeights[i][v] = w
                
            E[v] = Point2D(x,y)
            
        if lineNr == lastVertexLineNr + 1: # Read Nr of edges
            nrOfEdges = eval(split(line[:-2],':')[1]) # Strip of "\n" and ; 
            firstEdgeLineNr = lineNr + 1
            lastEdgeLineNr  = lineNr + nrOfEdges
            
        if firstEdgeLineNr <= lineNr and lineNr <= lastEdgeLineNr: 
            splitLine = split(line[:-1],';')
            h = eval(split(splitLine[0],':')[1])
            t = eval(split(splitLine[1],':')[1])
            G.AddEdge(t,h)
            for i in xrange(nrOfEdgeWeights):
                G.edgeWeights[i][(t,h)] = eval(split(splitLine[3+i],':')[1])
                
        lineNr = lineNr + 1
        
    graphFile.close()
    
    for v in G.vertices:
        L[v] = v
        
    G.embedding = E
    G.labeling  = L
    if intWeights:
        G.Integerize('all')
        for i in xrange(nrOfVertexWeights):
            G.vertexWeights[i].Integerize()
            
    return G
    
def SaveCATBoxGraph(G, _file):
    """ Save graph to file fileName in file-format from old CATBOX++ (*.cat) """
    
    # get file from name or file object
    file=None
    if type(_file) in types.StringTypes:
        file = open(_file, 'w')
    elif type(_file)==types.FileType or issubclass(_file.__class__,StringIO.StringIO):
        file=_file
    else:
        raise Exception("got wrong argument")
        
    nrOfVertexWeights = len(G.vertexWeights.keys())
    nrOfEdgeWeights = len(G.edgeWeights.keys())
    integerEdgeWeights = G.edgeWeights[0].QInteger()
    
    file.write("graph:\n")
    file.write("dir:%d; simp:%d; eucl:%d; int:%d; ew:%d; vw:%d;\n" %
               (G.QDirected(), G.simple, G.QEuclidian(), integerEdgeWeights,
               nrOfEdgeWeights, nrOfVertexWeights))
    file.write("scroller:\n")
    file.write("vdim:1000; hdim:1000; vlinc:10; hlinc:10; vpinc:50; hpinc:50;\n")
    file.write("vertices:" + `G.Order()` + ";\n")
    
    # Force continous numbering of vertices
    count = 1
    save = {}
    for v in G.vertices:
        save[v] = count
        count = count + 1
        file.write("n:%d; x:%d; y:%d;" % (save[v], G.embedding[v].x, G.embedding[v].y))
        for i in xrange(nrOfVertexWeights):
            if integerEdgeWeights: # XXX
                file.write(" w:%d;" % int(round(G.vertexWeights[i][v])))
            else:
                file.write(" w:%d;" % G.vertexWeights[i][v])	    
        file.write("\n")
        
    file.write("edges:" + `G.Size()` + ";\n")
    for tail in G.vertices:
        for head in G.OutNeighbors(tail):
            file.write("h:%d; t:%d; e:2;" % (save[head], save[tail]))
            
            for i in xrange(nrOfEdgeWeights):
                if integerEdgeWeights:
                    file.write(" w:%d;" % int(round(G.edgeWeights[i][(tail,head)])))
                else:
                    file.write(" w:%f;" % G.edgeWeights[i][(tail,head)])
                    
            file.write("\n")
            
            #### GML
            
def ParseGML(file):

    retval = []
    
    while 1:
    
        line = file.readline() 
        
        if not line:
            return retval
            
        token = filter(lambda x: x != '', split(line[:-1],"[\t ]*"))
        
        if len(token) == 1 and token[0] == ']':
            return retval
            
        elif len(token) == 2:
        
            if token[1] == '[':
                retval.append((token[0], ParseGML(file)))
            else:
                retval.append((token[0], token[1]))
                
        else:
            log.error("Serious format error line %s:" % line)
            
            
def PairListToDictionary(l):
    d = {}
    for i in xrange(len(l)):
        d[l[i][0]] = l[i][1]
    return d
    
    
    
def OpenGMLGraph(fileName):
    """ Reads in a graph from file fileName. File-format is supposed
        to be GML (*.gml) """
    G = Graph()
    G.directed = 0
    E = VertexLabeling()
    W = EdgeWeight(G)
    L = VertexLabeling()
    VLabel = VertexLabeling()
    ELabel = EdgeLabeling()
    
    file = open(fileName, 'r')
    g = ParseGML(file)
    file.close()
    
    if g[0][0] != 'graph':
        log.error("Serious format error in %s. first key is not graph" % fileName)
        return
    else:
        l = g[0][1]
        for i in xrange(len(l)):
        
            key   = l[i][0]
            value = l[i][1]
            
            if key == 'node':
            
                d = PairListToDictionary(value)
                v = G.AddVertex()
                
                try:
                    VLabel[v] = eval(d['label'])
                    P = PairListToDictionary(d['graphics'])
                    E[v] = Point2D(eval(P['x']), eval(P['y']))
                    
                except:
                    d = None 
                    P = None
                    
            elif key == 'edge':
            
                d = PairListToDictionary(value)
                
                try:
                    s = eval(d['source'])
                    t = eval(d['target'])
                    G.AddEdge(s,t)
                    ELabel[(s,t)] = eval(d['label'])
                    W[(s,t)] = 0
                except:
                    d = None 
                    
            elif key == 'directed':
                G.directed = 1 
                
    for v in G.vertices:
        L[v] = v
        
    G.embedding = E
    G.labeling  = L
    G.nrEdgeWeights = 1
    G.edgeWeights[0] = W
    G.vertexAnnotation = VLabel
    G.edgeAnnotation = ELabel
    
    return G
    
    
    
def OpenDotGraph(fileName):
    """ Reads in a graph from file fileName. File-format is supposed
        to be dot (*.dot) used in """
    G = Graph()
    G.directed = 1
    E = VertexLabeling()
    W = EdgeWeight(G)
    L = VertexLabeling()
    VLabel = VertexLabeling()
    ELabel = EdgeLabeling()
    
    import re
    file = open(fileName, 'r')
    lines = file.readlines()
    file.close()
    
    dot2graph = {}
    
    for l in lines[3:]:
        items = string.split(l)
        if len(items) < 2:
            break
        if items[1] != '->':
            v = G.AddVertex()
            dot_v = int(items[0])
            L[v] = "%d" % dot_v
            dot2graph[dot_v] = v
            m = re.search('label=("[^"]+")', l)
            VLabel[v] = m.group(1)[1:-1]
            m = re.search('pos="(\d+),(\d+)"', l)
            x = int(m.group(1))
            y = int(m.group(2))
            E[v] = Point2D(x,y)
        else:
            m = re.search('(\d+) -> (\d+)', l)
            v = dot2graph[int(m.group(1))]
            w = dot2graph[int(m.group(2))]
            m = re.search('label=("[^"]+")', l)
            #print l
            #print v,w,m.group(1)
            G.AddEdge(v,w)
            weight = float(m.group(1)[1:-1])
            W[(v,w)] = weight
            ELabel[(v,w)] = "%0.2f" % weight
            
    G.embedding = E
    G.labeling  = L
    G.nrEdgeWeights = 1
    G.edgeWeights[0] = W
    G.vertexAnnotation = VLabel
    G.edgeAnnotation = ELabel
    return G
