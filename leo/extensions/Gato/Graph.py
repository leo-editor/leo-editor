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

from GatoGlobals import *
from DataStructures import Point2D, VertexLabeling, EdgeLabeling, EdgeWeight
#from math import log

import logging
log = logging.getLogger("Graph.py")

################################################################################
#
# Graph
#
################################################################################
class Graph:
    """ Provides a mathematical graph object consisting of vertices 
        and (directed) edges connecting those vertices. Graphs have
    
        - a labeling for vertices allowing to specify names
    
        - an embedding of vertices into 2D-space
    
        - one or more sets of edge weights  
    
        Vertices are specified via id (integer number) and edges via
        (tail,head)-tuples 
    
        NOTE: ids are supposed to be consecutive and ranging from 0
        to G.Order() - 1 !!! Use the labeling to *display* other numbers
        for vertices.
    
        At least one set of edge weights is assumed to exist and accessible
        as self.edgeWeights[0]; self.euclidian and Euclidify refer to this
        self.edgeWeights[0]
    
    """
    
    def __init__(self):
        self.simple           = 1
        self.euclidian        = 1
        self.directed         = 0
        self.vertices         = [] 
        self.adjLists         = {}
        self.invAdjLists      = {}   # Inverse Adjazenzlisten
        self.highVertexID     = 0    # INTERNAL
        self.embedding        = VertexLabeling() # 2D-Positions
        self.labeling         = VertexLabeling() # Names of vertices
        self.edgeWeights      = {}   # Dictionary of edge labellings
        self.edgeWeights[0]   = EdgeWeight(self)
        self.vertexWeights    = {}   # None by default
        self.size             = 0
        self.edgeWidth        = None
        self.vertexAnnotation = None
        self.edgeAnnotation   = None
        self.properties       = {}
        
    def AddVertex(self):
        """ Add an isolated vertex. Returns the id of the new vertex """
        id = self.GetNextVertexID()	
        self.vertices.append(id)
        self.adjLists[id]    = []
        self.invAdjLists[id] = []
        return id
        
    def DeleteVertex(self, v):
        """ Delete the vertex v and its incident edges """
        outVertices = self.OutNeighbors(v)[:] # Need a copy here
        inVertices = self.InNeighbors(v)[:]
        for w in outVertices:
            self.DeleteEdge(v,w)
        for w in inVertices:
            if w != v: # We have already deleted loops
                self.DeleteEdge(w,v)
        self.vertices.remove(v)
        #self.adjLists[v] = None
        #self.invAdjLists[v] = None 
        # XXX Should clean up all other stuff too ...
        
        
    def QVertex(self, v):
        """ Check whether v is a vertex """
        return v in self.vertices
        
    def AddEdge(self,tail,head):
        """ Add an edge (tail,head). Returns nothing
            Raises GraphNotSimpleError if
            - trying to add a loop
            - trying to add an edge multiply 
        
            In case of directed graphs (tail,head) and (head,tail)
            are distinct edges """
        
        if self.simple == 1 and tail == head: # Loop
            raise GraphNotSimpleError, '(%d,%d) is a loop' % (tail,head)
        if self.directed == 0 and tail in self.adjLists[head]: 
            raise GraphNotSimpleError, '(%d,%d) is already an undirected edge' % (head,tail)
        if head in self.adjLists[tail]: # Multiple edge
            raise GraphNotSimpleError, '(%d,%d) is already an directed edge' % (tail,head)
            
        self.adjLists[tail].append(head)
        self.invAdjLists[head].append(tail)
        self.size = self.size + 1
        
        
    def DeleteEdge(self,tail,head):
        """ Deletes edge (tail,head). Does *not* handle undirected graphs
            implicitely. Raises NoSuchEdgeError upon error. """
        
        try:
            self.adjLists[tail].remove(head)
            self.invAdjLists[head].remove(tail)
            self.size = self.size - 1
        except KeyError:
            raise NoSuchEdgeError, "(%d,%d) is not an edge." % (tail,head)
            
            
    def Edge(self,tail,head):
        """  Handles undirected graphs by return correct ordered
             vertices as (tail,head). Raises NoSuchEdgeError upon error. """
        
        if tail not in self.vertices or head not in self.vertices:
            raise NoSuchEdgeError, "(%d,%d) is not an edge." % (tail,head)
            
        if head in self.adjLists[tail]:
            return (tail,head)
        elif self.directed == 0 and tail in self.adjLists[head]:
            return (head,tail)
        else:
            raise NoSuchEdgeError, "(%d,%d) is not an edge." % (tail,head)
            
            
    def QEdge(self,tail,head):
        """ Returns 1 if (tail,head) is an edge in G. If G is undirected
            order of vertices does not matter """
        if self.directed == 1:	
            return head in self.adjLists[tail]
        else: 
            return (head in self.adjLists[tail]) or (tail in self.adjLists[head])


    def QEdgeWidth(self):
        """ Returns 1 if individual edge widths are defined, 0 else """
        return self.edgeWidth != None
        

    def EdgeWidth(self, tail, head):
        return self.edgeWidth[(tail,head)]
    
            
    def Neighborhood(self,v):
        """ Returns the vertices which are connected to v. Does handle
            undirected graphs (i.e., returns vertices w s.t. either 
            (v,w) or (w,v) is an edge) """
        
        if self.directed:
            return self.OutNeighbors(v)
        else:
            return self.InOutNeighbors(v)
            
            
    def InNeighbors(self,v):
        """ Returns vertices w for which (w,v) is an edge """
        return self.invAdjLists[v]
        
        
    def OutNeighbors(self,v):
        """ Returns vertices w for which (v,w) is an edge """
        return self.adjLists[v]
        
        
    def InOutNeighbors(self,v):
        """ Returns vertices w for which (v,w) or (w,v) is an edge """	
        return self.InNeighbors(v) + self.OutNeighbors(v)
        
        
    def InEdges(self,v):
        """ Returns edges (*,v) """	
        f = lambda x, vertex = v : (x,vertex)
        return map(f, self.invAdjLists[v])
        
        
    def OutEdges(self,v):
        """ Returns edges (v,*) """	
        f = lambda x, vertex = v : (vertex,x)
        return map(f ,self.adjLists[v])
        
        
    def IncidentEdges(self,v):
        """ Returns edges (v,*) and (*,v) """	
        return self.InEdges(v) + self.OutEdges(v)
        
        
    def Edges(self):
        """ Returns all edges """		
        tmp = []
        for v in self.vertices:
            tmp = tmp + self.OutEdges(v)
        return tmp
        
    def Vertices(self):
        """ Returns all edges """		
        return self.vertices
        
    def printMy(self):
        """ Debugging only """
        for v in self.vertices:
            print v, " -- ", self.adjLists[v]
            
            
    def GetNextVertexID(self):
        """ *Internal* returns next free vertex id """
        self.highVertexID = self.highVertexID + 1
        return self.highVertexID
        
        
    def Order(self):
        """ Returns order i.e., the number of vertices """
        return len(self.vertices)
        
        
    def Size(self):
        """ Returns size i.e., the number of edge """
        return self.size 
        
        
    def Degree(self, v):
        """ Returns the degree of the vertex v, which is
            - the number of incident edges in the undirect case
            - the number of outgoing edges in the directed case """
        
        if self.directed:
            return len(self.adjLists[v])
        else:
            return len(self.adjLists[v]) + len(self.invAdjLists[v])
            
    def InDegree(self, v):
        """ Returns the number of incoming edges for direct graphs """
        if self.directed:
            return len(self.invAdjLists[v])
        else:
            return None # Proper error to raise?
            
            
    def OutDegree(self, v):
        """ Returns the number of incoming edges for direct graphs """
        if self.directed:
            return len(self.adjLists[v])
        else:
            return None # Proper error to raise?
            
            
    def QEuclidian(self):
        """ Returns 1 if the graph is euclidian, 0 else """
        return self.euclidian
        
        
    def QDirected(self):
        """ Returns 1 if the graph is directed, 0 else """
        return self.directed
        
        
    def CalculateWidthFromWeight(self, scale, weightID = 0):
        """ Calculate width of edges (self.edgeWidth will be used by 
            GraphDisplay if not none) from the specified set of edge
            weights. 
        
            Default: weightID = 0 is used """
        
        self.edgeWidth = EdgeLabeling()
        edges = self.Edges()
        maxWeight = max(self.edgeWeights[weightID].label.values())
        for e in edges:
            self.edgeWidth[e] = scale * (1 + 35 * self.edgeWeights[weightID][e] / maxWeight) 
            
    def NrOfEdgeWeights(self):
        return len(self.edgeWeights.keys())

    def SetEdgeWeight(self,i,v,w,value):
        self.edgeWeights[i][(v,w)] = value

    def GetEdgeWeight(self,i,v,w):
        return self.edgeWeights[i][(v,w)]

    def NrOfVertexWeights(self):
        return len(self.vertexWeights.keys())

    def SetVertexWeight(self,i,v,value):
        self.vertexWeights[i][v] = value

    def GetVertexWeight(self,i,v):
        return self.vertexWeights[i][v]

    def GetLabeling(self,v):
        return self.labeling[v]
    
    def SetLabeling(self,v, value):
        self.labeling[v] = value

    def GetEmbedding(self,v):
        return self.embedding[v]
    
    def SetEmbedding(self,v, x, y):
        self.embedding[v] = Point2D(x,y)
                  
    def Euclidify(self):
        """ Replace edge weights with weightID = 0 with Euclidean distance 
            between incident vertices """
        
        for v in self.vertices:
            for w in self.adjLists[v]:
                d = ((self.embedding[v].x - self.embedding[w].x)**2 + 
                     (self.embedding[v].y - self.embedding[w].y)**2)**(.5)
                
                if self.edgeWeights[0].QInteger():
                    self.edgeWeights[0][(v,w)] = int(round(d))
                else:
                    self.edgeWeights[0][(v,w)] = d
                    
        self.euclidian = 1
        
        
    def Integerize(self, weightID = 0):
        """ Integerize: Make all edge weights integers """
        
        if weightID == 'all':
            for w in self.edgeWeights.keys():
                self.edgeWeights[w].Integerize()
        else:
            self.edgeWeights[weightID].Integerize()
            
            
    def Undirect(self):
        """ If (u,v) and (v,u) are edges in the directed graph, remove one of them.
            to make graph undirected (no multiple edges allowed). Which one gets
            deleted depends on ordering in adjacency lists. """
        if not self.directed:
            return
            
        for v in self.vertices:
            for w in self.adjLists[v]:
                if v in self.adjLists[w]:
                    self.DeleteEdge(w,v)
                    
        self.directed = 0
        
    def SetProperty(self, name, val):
        """ Set the value of property 'name' to 'val' """
        self.properties[name] = val
        
    def Property(self,name):
        """ Return the value of property 'name'. If the property
           'name' has not been set 'Unknown' is returned """
        try:
            return self.properties[name]
        except:
            return None
            
    def About(self):
        """ Return string containing HTML code providing information
            about the graph """
        return "<HTML><BODY> <H3>No information available</H3></BODY></HTML>"
        
        
        ################################################################################
        #
        # Induced Subgraph
        #
        ################################################################################
        
class SubGraph(Graph):
    """ Provides a subgraph, i.e., a subset of the vertices and edges 
        of a specified graph
    
        Vertices are specified via ids from its supergraph and edges via
        (tail,head)-tuples 
    
        It also keeps track of the subgraphs total weight (= sum of edge 
        weights) for weights with weightID == 0
    """
    
    
    def __init__(self,G):
        Graph.__init__(self)
        self.superGraph    = G
        
        self.embedding     = self.superGraph.embedding
        self.labeling      = self.superGraph.labeling
        self.edgeWeights   = self.superGraph.edgeWeights
        
        self.directed = self.superGraph.directed
        
        self.totalWeight   = 0
        
        
    def AddVertex(self,v):
        """ Add a vertex from the supergraph to the subgraph.
            Returns NoSuchVertexError if v does not exist in
            supergraph """
        try:
            self.vertices.append(v)
            #f = lambda x, vertexList=self.vertices: x in vertexList
            #self.adjLists[v]    = filter(f, self.superGraph.adjLists[v])
            #self.invAdjLists[v] = filter(f, self.superGraph.invAdjLists[v])
            self.adjLists[v]    = []
            self.invAdjLists[v] = []
        except:
            raise NoSuchVertexError, "%d is not a vertex in the supergraph" % v
            
    def AddEdge(self,tail,head):
        """ Add an edge from the supergraph to the subgraph.
            Will also add tail and/or head if there are not
            already in subgraph """
        try:
            if not tail in self.vertices:
                self.AddVertex(tail)
            if not head in self.vertices:
                self.AddVertex(head)
            (tail,head) = self.superGraph.Edge(tail,head) 
            
            self.adjLists[tail].append(head)
            self.invAdjLists[head].append(tail)
            self.size = self.size + 1
            try:
                w = self.superGraph.edgeWeights[0][(tail,head)]
            except KeyError:
                w = 0.0 # XXX we dont have w weight for the edge. Make totalWeight configurable/subclass
            self.totalWeight += w
            
        except (KeyError, NoSuchVertexError, NoSuchEdgeError):
            raise NoSuchEdgeError, "(%d,%d) is not an edge in the supergraph." % (tail,head)
            
    def AddSubGraph(self,G):
        """ Add subgraph G to self. Will do nothing if self and G 
            have distinct supergraphs """
        if self.superGraph != G.superGraph:
            log.error("AddSubGraph: distinct superGraphs")
            return
        for v in G.vertices:
            self.AddVertex(v)
        for e in G.Edges():
            self.AddEdge(e[0],e[1])
            
            
    def DeleteEdge(self,tail,head):
        """ Delete edge from subgraph. Raises NoSuchEdgeError
            upon error """
        if tail in self.vertices and head in self.vertices:
            superEdge = self.superGraph.Edge(tail,head)
            self.totalWeight =  self.totalWeight - self.superGraph.edgeWeights[0][superEdge]
            self.adjLists[tail].remove(head)
            self.invAdjLists[head].remove(tail)
            self.size = self.size - 1
        else:
            raise NoSuchEdgeError, "(%d,%d) is not an edge." % (tail,head)
            
    def Clear(self):
        """ Delete all vertices and edges from the subgraph. """
        self.vertices         = [] 
        self.adjLists         = {}
        self.invAdjLists      = {}   # Inverse Adjazenzlisten
        self.size = 0
        self.totalWeight   = 0
        
        
    def GetNextVertexID(self):
        """ *Internal* safeguard """
        log.error("Induced Subgraph -> GetNextVertexID should never have been called")
        
    def Weight(self):
        """ Returns the total weight (= sum of edge weights) of subgraph """
        return self.totalWeight
        
        
    def QEuclidian(self):
        """ Returns 1 if the super graph is euclidian, 0 else """
        return self.superGraph.euclidian
        
        
    def QDirected(self):
        """ Returns 1 if the super graph is directed, 0 else"""
        return self.superGraph.directed
        
    def QEdge(self,tail,head):
        """ Returns 1 if (tail,head) is an edge in G """
        if not tail in self.vertices or not head in self.vertices:
            return 0
        if self.directed == 1:	
            return head in self.adjLists[tail]
        else: 
            return head in self.adjLists[tail] or tail in self.adjLists[head]
            
            
