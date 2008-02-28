################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#       You can find more information at 
#       http://gato.sf.net
#
#	file:   AnimatedDataStructures.py
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
from DataStructures import VertexLabeling, Queue, Stack, PriorityQueue
from Graph import SubGraph
import copy


class Animator:
    """ *Debugging* Text only Animator providing animation functions which
        only print to console """
    
    def SetVertexColor(self,v, color):
        print "set color of",v," to ",color
        
    def SetEdgeColor(self, tail, head, color):
        print "set color of edge (",tail,",", head ,") to ",color
        
        
class AnimatedNeighborhood:
    """ Visualizes visiting of neighbors by calling the Neighborhood
        method of graph for v and allowing to iterate over it, while 
        coloring (v,w) cTraversedEdge unless (v,w) is colored with
        one of the colors in leaveColors.
    
        #Neighborhood = lambda v,a=A,g=G: AnimatedNeighborhood(a,g,v,['red'])
        #
        #for w in Neighborhood(v):
        #    doSomething
        will color all edges cTraversedEdge unless the edge has been colored
        'red' at some point
    
        if a blinkColor is specified the edge will blink
        """
    
    def __init__(self,theAnimator,G,v,leaveColors = [],blinkColor=None):	
        """ theAnimator will usually be the GraphDisplay(Frame/Toplevel) """
        self.Animator    = theAnimator
        self.nbh         = G.Neighborhood(v)
        self.v           = v
        self.leaveColors = leaveColors
        self.blinkColor  = blinkColor
        self.lastEdge    = None
        self.lastColor   = None
        self.travColor   = "yellow"
        self.Animator.SetVertexFrameWidth(self.v,8)
        
    def __getitem__(self, i):
        try:
            if (self.Animator.GetEdgeColor(self.lastEdge[0],self.lastEdge[1]) == self.travColor):
                if (self.lastColor not in self.leaveColors):
                    self.Animator.SetEdgeColor(self.lastEdge[0],self.lastEdge[1],cTraversedEdge)
                else:
                    self.Animator.SetEdgeColor(self.lastEdge[0],self.lastEdge[1],self.lastColor)
        except:
            None
        if i < len(self.nbh):
            self.lastEdge  = (self.v,self.nbh[i])
            self.lastColor = self.Animator.GetEdgeColor(self.v,self.nbh[i])
            self.Animator.SetEdgeColor(self.v,self.nbh[i],self.travColor)
            if self.blinkColor != None:
                self.Animator.BlinkEdge(self.v,self.nbh[i],self.blinkColor)
            return self.nbh[i]
        else:
            self.Animator.SetVertexFrameWidth(self.v,self.Animator.gVertexFrameWidth)
            raise IndexError
            
    def __len__(self):
        return len(self.nbh)
        
        
class BlinkingNeighborhood:
    """ Visualizes visiting blinking (v,w) for all w when iterating over
        the Neighborhood
    
        #Neighborhood = lambda v,a=A,g=G: BlinkingNeighborhood(a,g,v,c)
        #
        #for w in Neighborhood(v):
        #    doSomething
        will blink all edges"""
    
    def __init__(self,theAnimator,G,v,c):	
        """ theAnimator will usually be the GraphDisplay(Frame/Toplevel) """
        self.Animator = theAnimator
        self.nbh = G.Neighborhood(v)
        self.v = v
        self.color = c
        
    def __getitem__(self, i):
        if i < len(self.nbh):
            self.Animator.BlinkEdge(self.v,self.nbh[i],self.color)
            return self.nbh[i]
        else:
            raise IndexError
            
    def __len__(self):
        return len(self.nbh)
        
class BlinkingTrackLastNeighborhood(BlinkingNeighborhood):
    """ Visualizes visiting blinking (v,w) for all w when iterating over
        the Neighborhood. It also temporarily keeps the the last blinked
        edge grey
    
        #Neighborhood = lambda v,a=A,g=G: BlinkingTrackLastNeighborhood(a,g,v,c,track)
        #
        #for w in Neighborhood(v):
        #    doSomething
        will blink all edges with color c, the last blinked is tracked with color 
        track """
    old = None
    
    
    def __init__(self,theAnimator,G,v,c,track="grey"):
        BlinkingNeighborhood.__init__(self,theAnimator,G,v,c)
        self.trackColor = track
        
    def __getitem__(self, i):
        if BlinkingTrackLastNeighborhood.old != None and i < len(self.nbh): 
            old = BlinkingTrackLastNeighborhood.old
            self.Animator.SetEdgeColor(old[0],old[1],old[2])
            
        BlinkingTrackLastNeighborhood.old = (self.v,self.nbh[i],
                                             self.Animator.GetEdgeColor(self.v,self.nbh[i]))
        retVal = BlinkingNeighborhood.__getitem__(self,i)
        self.Animator.SetEdgeColor(self.v,self.nbh[i],self.trackColor)
        
        return retVal
        
        
class BlinkingContainerWrapper:
    """ Visualizes iterating over a list of vertices and/or edges by
        blinking.
    
        #List = lambda l, a=A: BlinkingContainerWrapper(a,l,color)
        #
        #for w in List:
        #    doSomething
        """
    
    def __init__(self, theAnimator, l,  color=cOnQueue):	
        self.Animator = theAnimator
        self.list = copy.copy(l)
        self.color = color
        
    def __getitem__(self, i):
        if i < len(self.list):
            item = self.list[i]
            if type(item) == type(2): # vertex
                self.Animator.BlinkVertex(item,self.color)
            else:
                self.Animator.BlinkEdge(item[0],item[1],self.color)
            return item
        else:
            raise IndexError
            
    def __len__(self):
        return len(self.list)
        
        
class ContainerWrapper(BlinkingContainerWrapper):
    """ Visualizes iterating over a list of vertices and/or edges by
        coloring. If color has changed in the meantime the original
        color will not be set again.
    
        #List = lambda l, a=A: ContainerWrapper(a,l,color)
        #
        #for w in List:
        #    doSomething
        """
    
    def __init__(self, theAnimator, l, color=cOnQueue):
        BlinkingContainerWrapper.__init__(self,theAnimator,l,color)	
        self.lastitem  = None
        self.lastcolor = None
        
    def __getitem__(self, i):
        if i < len(self.list):
            item = self.list[i]
            if type(item) == type(2): # vertex
                dummy = self.Animator.GetVertexColor(item)
                if (self.lastitem != None) and (self.Animator.GetVertexColor(self.lastitem) == self.color):
                    self.Animator.SetVertexColor(self.lastitem,self.lastcolor)
                self.Animator.SetVertexColor(item,self.color)
                self.lastcolor = dummy
            else:
                dummy = self.Animator.GetEdgeColor(item[0],item[1])
                if (self.lastitem != None) and (self.Animator.GetEdgeColor(self.lastitem[0],self.lastitem[1]) == self.color):
                    self.Animator.SetEdgeColor(self.lastitem[0],self.lastitem[1],self.lastcolor)
                self.Animator.SetEdgeColor(item[0],item[1],self.color)
                self.lastcolor = dummy
            self.lastitem = item
            return item
        else:
            raise IndexError
            
class VisibleVertexLabeling(VertexLabeling):
    def __init__(self, theAnimator):
        VertexLabeling.__init__(self)
        self.A = theAnimator
        
    def __setitem__(self, v, val):
        VertexLabeling.__setitem__(self, v, val)
        if val == gInfinity:
            val = "Infinity"
        elif val == -gInfinity:
            val = "-Infinity"
        self.A.SetVertexAnnotation(v,val)
        
        
class AnimatedVertexLabeling(VertexLabeling):
    """ Visualizes changes of values of the VertexLabeling
        by changing vertex colors appropriately.
    
        E.g.,
        #d = AnimatedVertexLabeling(A) 
        #d[v] = 0
        will color v cInitial.
    
        The coloring used for d[v] = val 
        - cInitial if val = 0,None,gInfinity
        - "blue" else """
    
    def __init__(self, theAnimator, initial=0, color="blue"):
        """ theAnimator will usually be the GraphDisplay(Frame/Toplevel) 
            initial is the value to cause coloring in cInitial """
        VertexLabeling.__init__(self)
        self.Animator = theAnimator
        self.initial=initial
        self.color = color
        
    def __setitem__(self, v, val):
        VertexLabeling.__setitem__(self, v, val)
        if val == self.initial or val == None or val == gInfinity:
            self.Animator.SetVertexColor(v,cInitial)
        else:
            self.Animator.SetVertexColor(v,self.color)
            
            
class AnimatedSignIndicator:
    """ Visualizes sign of vertex or edge:
        weight > 0 : green
               = 0 : grey
               < 0 : red """
    
    def __init__(self,theAnimator):
        self.Animator = theAnimator
        self.weight   = {}
        
    def __setitem__(self, i, val):
        self.weight[i] = val
        if type(i) == type(2): # vertex
            if val>0:
                self.Animator.SetVertexColor(i,"green")
            elif val<0:
                self.Animator.SetVertexColor(i,"red")
            else:
                self.Animator.SetVertexColor(i,"grey")
        else:
            if val>0:
                self.Animator.SetEdgeColor(i,"green")
            elif val<0:
                self.Animator.SetEdgeColor(i,"red")
            else:
                self.Animator.SetEdgeColor(i,"grey")
                
    def __getitem__(self, i):
        return self.weight[i]
        
        
        
class AnimatedPotential:
    """ Visualizes the potential from 0 (green) to
         max (brown) of a vertex. """
    def __init__(self,max,theAnimator1,theAnimator2=None):
        self.pot      = {}
        self.max      = max
        self.colors   = ['#00FF00','#11EE00','#22DD00','#33CC00','#44BB00',
                         '#55AA00','#669900','#778800','#887700','#996600',
                         '#AA5500','#BB4400','#CC3300']
        self.Animator1 = theAnimator1
        if theAnimator2 == None:
            self.Animator2 = theAnimator1
        else:
            self.Animator2 = theAnimator2 
            
    def __setitem__(self,v,val):
        self.pot[v] = val
        if val == gInfinity:
            self.Animator2.SetVertexAnnotation(v,"Inf")
        elif val == -gInfinity:
            self.Animator2.SetVertexAnnotation(v,"-Inf")
        else:
            self.Animator2.SetVertexAnnotation(v,"%d"%val)
        if val > self.max:
            val = self.max
        self.Animator1.SetVertexColor(v,self.colors[(val*(len(self.colors)-1))/self.max])
        
    def __getitem__(self,v):
        return self.pot[v]
        
        
        
class BlinkingVertexLabeling(VertexLabeling):
    """ Visualizes changes of values of the VertexLabeling
        by blinking vertices """
    
    def __init__(self, theAnimator):
        """ theAnimator will usually be the GraphDisplay(Frame/Toplevel) """
        VertexLabeling.__init__(self)
        self.Animator = theAnimator
        
    def __setitem__(self, v, val):
        VertexLabeling.__setitem__(self, v, val)
        if val == 0:
            self.Animator.BlinkVertex(v)
        else:
            self.Animator.BlinkVertex(v)
            
            
class AnimatedVertexQueue(Queue):
    """ Visualizes status of vertices in relation to the Queue by
        coloring them
    
        - cOnQueue if they are in the queue
        - cRemovedFromQueue if they have been on the queue and were
          removed """
    
    def __init__(self, theAnimator, colorOn=cOnQueue, colorOff=cRemovedFromQueue):
        """ theAnimator will usually be the GraphDisplay(Frame/Toplevel) """
        Queue.__init__(self)
        self.Animator = theAnimator
        self.ColorOn = colorOn
        self.ColorOff = colorOff
        self.lastRemoved = None
        
    def Append(self,v):
        Queue.Append(self,v)
        self.Animator.SetVertexColor(v, self.ColorOn)
        
    def Top(self):
        v = Queue.Top(self)
        self.Animator.SetVertexColor(v, self.ColorOff)
        if self.lastRemoved is not None:
            self.Animator.SetVertexFrameWidth(self.lastRemoved,self.Animator.gVertexFrameWidth)
        self.Animator.SetVertexFrameWidth(v,6)
        self.lastRemoved = v 
        return v
        
    def Clear(self):
        for v in self.contents:
            self.Animator.SetVertexColor(v, self.ColorOff)
        Queue.Clear(self) 
        if self.lastRemoved is not None:
            self.Animator.SetVertexFrameWidth(self.lastRemoved,self.Animator.gVertexFrameWidth)
            self.lastRemoved = None
            
class AnimatedVertexPriorityQueue(PriorityQueue):    
    """ Visualizes status of vertices in relation to the PriorityQueue by
        coloring them
    
        - cOnQueue if they are in the queue
        - cRemovedFromQueue if they have been on the queue and were
          removed """
    
    def __init__(self, theAnimator, colorOn=cOnQueue, colorOff=cRemovedFromQueue):
        """ theAnimator will usually be the GraphDisplay(Frame/Toplevel) """
        PriorityQueue.__init__(self)
        self.Animator = theAnimator
        self.ColorOn = colorOn
        self.ColorOff = colorOff
        self.lastRemoved = None
        
    def Insert(self,value,sortKey):
        PriorityQueue.Insert(self,value,sortKey)
        self.Animator.SetVertexColor(value, self.ColorOn)
        
    def DecreaseKey(self,value,newSortKey):
        PriorityQueue.DecreaseKey(self,value,newSortKey)
        self.Animator.BlinkVertex(value)
        
    def DeleteMin(self):
        v = PriorityQueue.DeleteMin(self)
        self.Animator.SetVertexColor(v, self.ColorOff)
        if self.lastRemoved is not None:
            self.Animator.SetVertexFrameWidth(self.lastRemoved,self.Animator.gVertexFrameWidth)
        self.Animator.SetVertexFrameWidth(v,6)
        self.lastRemoved = v 
        return v
        
        
class AnimatedVertexStack(Stack):
    """ Visualizes status of vertices in relation to the Stack by
        coloring them
    
        - cOnQueue if they are in the queue
        - cRemovedFromQueue if they have been on the queue and were
          removed """
    
    def __init__(self, theAnimator, colorOn=cOnQueue, colorOff=cRemovedFromQueue):
        """ theAnimator will usually be the GraphDisplay(Frame/Toplevel) """
        Stack.__init__(self)
        self.Animator = theAnimator
        self.ColorOn = colorOn
        self.ColorOff = colorOff
        self.lastRemoved = None
        
    def Push(self,v):
        Stack.Push(self,v)
        self.Animator.SetVertexColor(v, self.ColorOn)
        
    def Pop(self):
        v = Stack.Pop(self)
        self.Animator.SetVertexColor(v, self.ColorOff)
        if self.lastRemoved is not None:
            self.Animator.SetVertexFrameWidth(self.lastRemoved,self.Animator.gVertexFrameWidth)
        self.Animator.SetVertexFrameWidth(v,6)
        self.lastRemoved = v 
        return v
        
    def Clear(self):
        for v in self.contents:
            self.Animator.SetVertexColor(v, self.ColorOff)
        Stack.Clear(self)
        if self.lastRemoved is not None:
            self.Animator.SetVertexFrameWidth(self.lastRemoved,self.Animator.gVertexFrameWidth)
            self.lastRemoved = None
            
            
            ##class AnimatedPriorityQueue(PriorityQueue):
            ##    def __init__(self, theAnimator, color=cVisited):
            ##	""" theAnimator will usually be the GraphDisplay(Frame/Toplevel) """
            ##	self.Animator = theAnimator
            ##        self.color = color        
            ##        PriorityQueue.__init__(self)
            
            ##    def Insert(self,value,sortKey):
            ##        # XXX For compat. to AnimatedVertexSet (yuk)
            ##        PriorityQueue.Insert(self,value,sortKey)
            
            ##    def DeleteMin(self):
            ##        """ Return and delete minimal value with minimal sortKey from queue. """
            ##	v = PriorityQueue.DeleteMin(self)
            ## 	self.Animator.SetVertexColor(v,self.color)
            ##        return v
            
            
            
            
class AnimatedVertexSet:
    """ Visualizes status of vertices in relation to the Set by
        coloring them
    
        - cVisited  if they have been in the set and were
          removed """
    
    def __init__(self, theAnimator, vertexSet=None, color=cVisited):
        """ theAnimator will usually be the GraphDisplay(Frame/Toplevel) """
        if vertexSet == None:
            self.vertices = []
        else:
            self.vertices = vertexSet
        self.Animator = theAnimator
        self.color = color
        
    def Set(self, vertexSet):
        """ Sets the set equal to a copy of vertexSet """
        self.vertices = vertexSet[:]
        
    def Remove(self, v):
        self.Animator.SetVertexColor(v,self.color)
        self.vertices.remove(v)
        
    def Add(self,v):
        """ Add a single vertex v """
        self.vertices.append(v)
        
    def IsNotEmpty(self):
        return len(self.vertices) > 0
        
    def IsEmpty(self):
        return len(self.vertices) == 0
        
    def Contains(self,v):
        return v in self.vertices
        
        
class AnimatedEdgeSet:
    """ Visualizes status of edges in relation to the Set by
        coloring them
    
        - 'blue' if they are added to the set
        - cVisited  if they have been in the set and were
          removed """
    
    def __init__(self, theAnimator,edgeSet=None):
        """ theAnimator will usually be the GraphDisplay(Frame/Toplevel) """
        if edgeSet == None:
            self.edges = []
        else:
            self.edges = edgeSet	    
        self.Animator = theAnimator
        
    def __len__(self):
        return len(self.edges)
        
    def __getitem__(self,key):
        return self.edges[key]
        
    def Set(self, edgeSet):
        """ Sets the set equal to a copy of edgeSet """
        self.edges = edgeSet[:]
        
    def AddEdge(self, e):
        self.Animator.SetEdgeColor(e[0],e[1],"blue")
        self.edges.append(e)
        
    def Remove(self, e):
        self.Animator.BlinkEdge(e[0],e[1],cVisited)
        self.Animator.SetEdgeColor(e[0],e[1],cVisited)
        self.edges.remove(e) 
        
    def IsNotEmpty(self):
        return len(self.edges) > 0
        
    def Contains(self,e):
        return e in self.edges
        
        
class AnimatedSubGraph(SubGraph):
    """ Visualizes status of vertices and edges in relation to the SubGraph by
        coloring them
        - color (default is 'blue') if they are added to the SubGraph """
    
    def __init__(self, G, theAnimator, color="blue"):
        """ color is used to color vertices and edges in the subgraph.
            theAnimator will usually be the GraphDisplay(Frame/Toplevel) """
        SubGraph.__init__(self, G)
        self.Animator = theAnimator
        self.Color = color
        
    def AddVertex(self,v):
        try:
            SubGraph.AddVertex(self,v)
            self.Animator.SetVertexColor(v,self.Color)
            self.Animator.DefaultInfo()
        except NoSuchVertexError:
            return
            
    def AddEdge(self,edge,head=None):
         # Poor mans function overload
        if head == None and len(edge) == 2:
            t = edge[0]
            h = edge[1]
        else:
            t = edge
            h = head
        try:
            SubGraph.AddEdge(self,t,h)
            self.Animator.SetEdgeColor(t,h,self.Color)
            # Raise edges above other
            tt, hh = self.superGraph.Edge(t,h)
            self.Animator.RaiseEdge(tt,hh)
            self.Animator.DefaultInfo()
        except NoSuchVertexError, NoSuchEdgeError:
            return

    def RaiseEdges(self):
        for (t,h) in self.Edges():
            tt, hh = self.superGraph.Edge(t,h)
            self.Animator.RaiseEdge(tt,hh)
            
            
    def DeleteEdge(self,edge,head=None):
        if head == None and len(edge) == 2:
            t = edge[0]
            h = edge[1]
        else:
            t = edge
            h = head
        try:
            SubGraph.DeleteEdge(self,t,h)
            self.Animator.SetEdgeColor(t,h,"black")
        except NoSuchVertexError, NoSuchEdgeError:
            return
            
    def Clear(self, color="grey"):
        """ Delete all vertices and edges from the animated subgraph. 
            and color them with 'color' (grey is default) """
        
        # GraphDisplay functions save several update()'s
        self.Animator.SetAllVerticesColor(color,self)
        self.Animator.SetAllEdgesColor(color,self)
        
        self.vertices         = [] 
        self.adjLists         = {}
        self.invAdjLists      = {}   # Inverse Adjazenzlisten
        self.size = 0
        self.totalWeight   = 0
        
        
    def AddEdgeByVertices(self,tail,head):
        try:
            SubGraph.AddEdge(self,tail,head)
            self.Animator.SetEdgeColor(tail,head,self.Color)
            self.Animator.DefaultInfo()
        except NoSuchVertexError, NoSuchEdgeError:
            return
            
            
            
class AnimatedPredecessor(VertexLabeling):
    """ Animates a predecessor array by 
    
        - coloring edges (pred[v],v) 'red' 
        - coloring edges (pred[v],v) 'grey' if the value of
          pred[v] is changed """
    
    def __init__(self, theAnimator, leaveColors = None, predColor='red'):
        VertexLabeling.__init__(self)
        self.Animator = theAnimator
        self.leaveColors = leaveColors
        self.predColor = predColor
        
    def __setitem__(self, v, val):
        try:
            oldVal = VertexLabeling.__getitem__(self, v)
            if oldVal != None:
                if self.leaveColors == None or not (self.Animator.GetEdgeColor(oldVal,v) in self.leaveColors):
                    self.Animator.SetEdgeColor(oldVal,v,"grey")
        except:
            pass 
        if val != None:
            try:
                if self.leaveColors == None or not (self.Animator.GetEdgeColor(val,v) in self.leaveColors):
                    self.Animator.SetEdgeColor(val,v,self.predColor)
            except:
                pass
        VertexLabeling.__setitem__(self, v, val)
        
        
    def SetPredColor(self, color):
        """ NOTE: This does not recolor assigned (pred[v],v) edges """
        self.predColor = color
        
    def AppendLeaveColor(self,color):
        if self.leaveColors == None:
            self.leaveColors = [color]
        else:
            self.leaveColors.append(color)
            
class ComponentMaker:
    """ Subsequent calls of method NewComponent() will return differently
        colored subgraphs of G """
    def __init__(self,g,a):
        self.G = g
        self.A = a
        self.colors = ['#FF0000','#00FF00','#0000FF',
                       '#009999','#990099','#999900',
                       '#996666','#669966','#666699',
                       '#0066CC','#6600CC','#66CC00',
                       '#00CC66','#CC0066','#CC6600']
        self.lastColor = 0
        
    def NewComponent(self):
        comp = AnimatedSubGraph(self.G, self.A, self.colors[self.lastColor])
        self.lastColor = self.lastColor + 1
        if self.lastColor == len(self.colors):
            self.lastColor = 0
        return comp
        
    def LastComponentColor(self):
        if self.lastColor > 0:
            return self.colors[self.lastColor -1]
        return None
        
        ################################################################################
        #
        # Functions
        #
        ################################################################################
        
def showPathByPredecessorArray(source,sink,pred,A,color="red"):
    """ Visualizes a path from source to sink in a graph G
        displayed in A. The path is specified in terms of the
        predecessor array pred and will be colored with color
        (default is 'red') """
    
    v = sink
    
    seen = [v] # avoid getting stuck in cycles
    
    while (pred[v] != None) and (pred[v] != v):
        A.SetVertexColor(v,color)
        A.SetEdgeColor(pred[v],v,color)
        v = pred[v]
        if v in seen:
            return
        else:
            seen.append(v)
            
    A.SetVertexColor(v,color)
    
    ################################################################################
    #
    # Wrapper
    #
    ################################################################################
    
class FlowWrapper:
    """ This class visualizes the flow in a directed graph G
        with animator GA and it's residual network R with
        animator RA.
    
        flow = FlowWrapper(G,A,R,RA,G.edgeWeights[0],R.edgeWeights[0])
    
        or
    
        flow = FlowWrapper(G,A,R,RA,G.edgeWeights[0],R.edgeWeights[0],G.vertexWeights[0])
    """
    def __init__(self,  G, GA, R, RA, flow, res, excess=None):
        self.zeroEdgeColor = "black"
        self.G      = G
        self.GA     = GA
        self.R      = R
        self.RA     = RA
        self.flow   = flow
        self.cap    = copy.deepcopy(res)
        self.res    = res
        self.excess = excess
        if self.excess == None:        ## if no startup excess set all to zero
            self.excess = {}
            for v in self.G.vertices:
                self.excess[v] = 0
        for e in self.G.Edges():
            self.flow[e] = 0 
            
    def __setitem__(self, e, val):
        if (self.excess[e[0]] != gInfinity) and (self.excess[e[0]] != -gInfinity):
            self.excess[e[0]] = self.excess[e[0]] + self.flow[e] - val
        if (self.excess[e[1]] != gInfinity) and (self.excess[e[1]] != -gInfinity):
            self.excess[e[1]] = self.excess[e[1]] - self.flow[e] + val  
        if self.excess[e[0]] > 0:
            self.RA.SetVertexColor(e[0],"green")
        elif self.excess[e[0]] < 0:
            self.RA.SetVertexColor(e[0],"red")
        else:
            self.RA.SetVertexColor(e[0],"gray")
        if self.excess[e[1]] > 0:
            self.RA.SetVertexColor(e[1],"green")
        elif self.excess[e[1]] < 0:
            self.RA.SetVertexColor(e[1],"red")
        else:
            self.RA.SetVertexColor(e[1],"gray")
        self.flow[e] = val
        if val == self.cap[e]:     
            self.GA.SetEdgeColor(e[0],e[1],"blue")
            self.GA.SetEdgeAnnotation(e[0],e[1],"%d/%d" % (val,self.cap[e]),"black")
            try:
                self.RA.DeleteEdge(e[0],e[1])
            except:
                None
            if not self.R.QEdge(e[1],e[0]):
                self.RA.AddEdge(e[1],e[0])
        elif val == 0: 
            self.GA.SetEdgeColor(e[0],e[1],self.zeroEdgeColor)
            self.GA.SetEdgeAnnotation(e[0],e[1],"%d/%d" % (val, self.cap[e]),"gray")
            try:
                self.RA.DeleteEdge(e[1],e[0])
            except:
                None
            if not self.R.QEdge(e[0],e[1]):
                self.RA.AddEdge(e[0],e[1])
        else:                      
            self.GA.SetEdgeColor(e[0],e[1],"#9999FF")
            self.GA.SetEdgeAnnotation(e[0],e[1],"%d/%d" % (val,self.cap[e]),"black")
            if not self.R.QEdge(e[1],e[0]):
                self.RA.AddEdge(e[1],e[0])
            if not self.R.QEdge(e[0],e[1]):
                self.RA.AddEdge(e[0],e[1])
        if self.G.QEdge(e[0],e[1]):
            self.res[(e[1],e[0])]  = val
            self.res[(e[0],e[1])]  = self.cap[(e[0],e[1])] - val
        else:
            self.res[(e[0],e[1])]  = val
            self.res[(e[1],e[0])]  = self.cap[(e[1],e[0])] - val
        return
        
    def __getitem__(self, e):
        return self.flow[e]
        
        
class ReducedCostsWrapper:
    """ Visualizes the reduced costs of the edge
        >0 green
        =0 grey
        <0 red 
    """
    def __init__(self, A, cost, pot):
        self.cost = cost
        self.pot = pot
        self.A = A
        
    def __setitem__(self, e, val):
        self.cost[e] = val
        rc = self.cost[e] + self.pot[e[0]] - self.pot[e[1]]
        try:
            if rc > 0:
                self.A.SetEdgeColor(e[0],e[1],"red")
            elif rc == 0:
                self.A.SetEdgeColor(e[0],e[1],"grey")
            else:
                self.A.SetEdgeColor(e[0],e[1],"green")
        except:
            None
            
    def __getitem__(self, e):
        return self.cost[e]
