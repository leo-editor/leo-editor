################################################################################
#
#       This file is part of Gato (Graph Algorithm Toolbox) 
#
#	file:   PlanarityTest.py
#	author: Ramazan Buzdemir (buzdemir@zpr.uni-koeln.de)
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


###############################################################################
###############################################################################
###############################################################################
#                                                                             #
#                            AN IMPLEMENTATION OF                             #
#                           THE HOPCROFT AND TARJAN                           #
#                    PLANARITY TEST AND EMBEDDING ALGORITHM                   #
#                                                                             #
###############################################################################
#                                                                             #
# References:                                                                 #
#                                                                             #
# [Meh84] K.Mehlhorn.                                                         #
#         "Data Structures and Efficient Algorithms."                         #
#         Springer Verlag, 1984.                                              #
# [MM94]  K.Mehlhorn and P.Mutzel.                                            #
#         "On the embedding phase of the Hopcroft and Tarjan planarity        #
#          testing algorithm."                                                #
#         Technical report no. 117/94, mpi, Saarbruecken, 1994                #
#                                                                             #
###############################################################################



#=============================================================================#
from copy import deepcopy
from DataStructures import Stack
from tkMessageBox import showinfo
#=============================================================================#



#=============================================================================#
class List:
    def __init__(self,el=[]):
        elc=deepcopy(el)
        self.elements=elc
        
        # a) Access Operations
    def length(self):
        return len(self.elements)
        
    def empty(self):
        if self.length()==0:
            return 1
        else:
            return 0
            
    def head(self):
        return self.elements[0]
        
    def tail(self):
        return self.elements[-1]
        
        # b)Update Operations
    def push(self,x):
        self.elements.insert(0,x)
        return x
        
    def Push(self,x):
        self.elements.append(x)
        return x
        
    def append(self,x):
        self.Push(x)
        
    def pop(self):
        x=self.elements[0]
        self.elements=self.elements[1:]
        return x
        
    def Pop(self):
        x=self.elements[-1]
        self.elements=self.elements[:-1]
        return x
        
    def clear(self):
        self.elements=[]
        
    def conc(self,A):
        self.elements=self.elements+A.elements
        A.elements=[]
        #=============================================================================#
        
        
        
        #=============================================================================#
class pt_graph:

    def __init__(self):
        self.V        = []
        self.E        = []
        self.adjEdges = {}
        
        # a) Access operations
    def source(self,e):
        return e[0]
        
    def target(self,e):
        return e[1]
        
    def number_of_nodes(self):
        return len(self.V)
        
    def number_of_edges(self):
        return len(self.E)
        
    def all_nodes(self):
        return self.V
        
    def all_edges(self):
        return self.E
        
    def adj_edges(self,v):
        return self.adjEdges[v]
        
    def adj_nodes(self,v):
        nodelist=[]
        for e in self.adj_edges(v):
            nodelist.append(e[1])
        return nodelist
        
    def first_node(self):
        return self.V[0]
        
    def last_node(self):
        return self.V[-1]
        
    def first_edge(self):
        return self.E[0]
        
    def last_edge(self):
        return self.E[-1]
        
    def first_adj_edge(self,v):
        if len(self.adj_edges(v))>0:
            return self.adj_edges(v)[0]
        else:
            return None
            
    def last_adj_edge(self,v):
        if len(self.adj_edges(v))>0:
            return self.adj_edges(v)[-1]
        else:
            return None
            
            # b) Update operations
    def new_node(self,v):
        self.V.append(v)
        self.adjEdges[v]=[]
        return v
        
    def new_edge(self,v,w):
        if v==w: # Loop
            raise GraphNotSimpleError
        if (v,w) in self.E: # Multiple edge
            raise GraphNotSimpleError
        self.E.append((v,w))
        self.adjEdges[v].append((v,w))
        return (v,w)
        
    def del_node(self,v):
        try:
            for k in self.V:
                for e in self.adj_edges(k):
                    if source(e)==v or target(e)==v:
                        self.adjEdges[k].remove(e)
            self.V.remove(v)
            for e in self.E:
                if source(e)==v or target(e)==v:
                    self.E.remove(e)
        except KeyError:
            raise NoSuchVertexError
            
    def del_edge(self,e):
        try:
            self.E.remove(e)
            self.adjEdges[source(e)].remove((source(e),target(e)))
        except KeyError:
            raise NoSuchEdgeError
            
    def del_nodes(self,node_list): # deletes all nodes in list L from self
        L=deepcopy(node_list)
        for l in L:
            self.del_node(l)
            
    def del_edges(self,edge_list): # deletes all edges in list L from self
        L=deepcopy(edge_list)
        for l in L:
            self.del_edge(l)
            
    def del_all_nodes(self): # deletes all nodes from self
        self.del_nodes(self.all_nodes())
        
    def del_all_edges(self): # deletes all edges from self
        self.del_edges(self.all_edges())
        
    def sort_edges(self, cost):
        def up(x,y):
            if x[1]<y[1]: return -1
            if x[1]==y[1]: return 0
            return 1
        sorted_list=cost.items()
        sorted_list.sort(up)
        self.del_all_edges()
        for i in sorted_list:
            self.new_edge(source(i[0]),target(i[0]))
            
def source(e):
    return e[0]
    
def target(e):
    return e[1]
    
def reversal(e):
    return (e[1],e[0])
    #=============================================================================#
    
    
    
    #=============================================================================#
class block:
# The constructor takes an edge and a list of attachments and creates 
# a block having the edge as the only segment in its left side.
#
# |flip| interchanges the two sides of a block.
#
# |head_of_Latt| and |head_of_Ratt| return the first elements 
# on |Latt| and |Ratt| respectively 
# and |Latt_empty| and |Ratt_empty| check these lists for emptyness.
#
# |left_interlace| checks whether the block interlaces with the left 
# side of the topmost block of stack |S|. 
# |right_interlace| does the same for the right side.
#
# |combine| combines the block with another block |Bprime| by simply 
# concatenating all lists.
#
# |clean| removes the attachment |w| from the block |B| (it is 
# guaranteed to be the first attachment of |B|). 
# If the block becomes empty then it records the placement of all 
# segments in the block in the array |alpha| and returns true.
# Otherwise it returns false.
#
# |add_to_Att| first makes sure that the right side has no attachment 
# above |w0| (by flipping); when |add_to_Att| is called at least one 
# side has no attachment above |w0|.
# |add_to_Att| then adds the lists |Ratt| and |Latt| to the output list 
# |Att| and records the placement of all segments in the block in |alpha|.

    def __init__(self,e,A):
        self.Latt=List(); self.Ratt=List() # list of attachments "ints"
        self.Lseg=List(); self.Rseg=List() # list of segments represented by
                                           # their defining "edges"
        self.Lseg.append(e)
        self.Latt.conc(A)  # the other two lists are empty
        
    def flip(self):
        ha=List() # "ints"
        he=List() # "edges"
        
        # we first interchange |Latt| and |Ratt| and then |Lseg| and |Rseg|
        ha.conc(self.Ratt); self.Ratt.conc(self.Latt); self.Latt.conc(ha);
        he.conc(self.Rseg); self.Rseg.conc(self.Lseg); self.Lseg.conc(he);
        
    def head_of_Latt(self):
        return self.Latt.head()
        
    def empty_Latt(self):
        return self.Latt.empty()
        
    def head_of_Ratt(self):
        return self.Ratt.head()
        
    def empty_Ratt(self):
        return self.Ratt.empty()
        
    def left_interlace(self,S):
        # check for interlacing with the left side of the 
        # topmost block of |S|
        if (S.IsNotEmpty() and not((S.contents[-1]).empty_Latt()) and
            self.Latt.tail()<(S.contents[-1]).head_of_Latt()):
            return 1
        else:
            return 0
            
    def  right_interlace(self,S):
        # check for interlacing with the right side of the 
        # topmost block of |S|
        if (S.IsNotEmpty() and not((S.contents[-1]).empty_Ratt()) and
            self.Latt.tail()<(S.contents[-1]).head_of_Ratt()):
            return 1
        else:
            return 0
            
    def combine(self,Bprime):
        # add block Bprime to the rear of |this| block
        self.Latt.conc(Bprime.Latt)
        self.Ratt.conc(Bprime.Ratt)
        self.Lseg.conc(Bprime.Lseg)
        self.Rseg.conc(Bprime.Rseg)
        del Bprime
        
    def clean(self,dfsnum_w,alpha,dfsnum):
        # remove all attachments to |w|; there may be several
        while not(self.Latt.empty()) and self.Latt.head()==dfsnum_w:
            self.Latt.pop()
        while not(self.Ratt.empty()) and self.Ratt.head()==dfsnum_w:
            self.Ratt.pop()
        if not(self.Latt.empty()) or not(self.Ratt.empty()):
            return 0
            
            # |Latt| and |Ratt| are empty;
            #  we record the placement of the subsegments in |alpha|.
        for e in self.Lseg.elements:
            alpha[e]=left
        for e in self.Rseg.elements:
            alpha[e]=right 
        return 1
        
    def add_to_Att(self,Att,dfsnum_w0,alpha,dfsnum):
        # add the block to the rear of |Att|. Flip if necessary
        if not(self.Ratt.empty()) and self.head_of_Ratt()>dfsnum_w0:
            self.flip()
        Att.conc(self.Latt)
        Att.conc(self.Ratt) 
        # This needs some explanation. 
        # Note that |Ratt| is either empty or {w0}.
        # Also if |Ratt| is non-empty then all subsequent
        # sets are contained in {w0}. 
        # So we indeed compute an ordered set of attachments.
        for e in self.Lseg.elements:
            alpha[e]=left
        for e in self.Rseg.elements:
            alpha[e]=right
            #=============================================================================#
            
            
            
            #=============================================================================#
            # GLOBALS:
left=1
right=2
G=pt_graph()

reached={}
dfsnum={}
parent={}
dfs_count=0
lowpt={}
Del=[]
lowpt1={}
lowpt2={}
alpha={}
Att=List()
cur_nr=0
sort_num={}
tree_edge_into={}
#=============================================================================#



#=============================================================================#
def planarity_test(Gin):
# planarity_test decides whether the InputGraph is planar.
# it also order the adjecentLists in counterclockwise.

###    SaveGmlGraph(Gin,"/home/ramazan/Leda/Graphs/rama.gml")

    n=Gin.Order() # number of nodes
    if n<3: return 1
    if not(Gin.QDirected()) and Gin.Size()>3*n-6: return 0 # number of edges
    if Gin.QDirected() and Gin.Size()>6*n-12: return 0
    
    #--------------------------------------------------------------
    # make G a copy of Gin and make G bidirected
    
    global G,cur_nr
    G=pt_graph()
    
    for v in Gin.vertices:
        G.new_node(v)
    for e in Gin.Edges():
        G.new_edge(source(e),target(e))
        
    cur_nr=0
    nr={}
    cost={}
    n=G.number_of_nodes()
    for v in G.all_nodes():
        nr[v]=cur_nr
        cur_nr=cur_nr+1
    for e in G.all_edges():
        if nr[source(e)] < nr[target(e)]:
            cost[e]=n*nr[source(e)] + nr[target(e)]
        else:
            cost[e]=n*nr[target(e)] + nr[source(e)]
    G.sort_edges(cost)
    
    L=List(G.all_edges())
    while not(L.empty()):
        e=L.pop()
        if (not(L.empty()) and source(e)==target(L.head())
            and source(L.head())==target(e)):
            L.pop()
        else:
            G.new_edge(target(e),source(e))
            #--------------------------------------------------------------
            
            
            #--------------------------------------------------------------    
            # make G biconnected
    Make_biconnected_graph()
    #--------------------------------------------------------------
    
    
    #--------------------------------------------------------------
    # make H a copy of G
    #
    # We need the biconnected version of G (G will be further modified
    # during the planarity test) in order to construct the planar embedding.
    # So we store it as a graph H.
    H=deepcopy(G)
    #--------------------------------------------------------------
    
    
    #--------------------------------------------------------------    
    # test planarity
    
    global dfsnum,parent,alpha,Att
    
    dfsnum={}
    parent={}
    for v in G.all_nodes():
        parent[v]=None      
        
    reorder()
    
    alpha={}
    for e in G.all_edges():
        alpha[e]=0
    Att=List()
    alpha[G.first_adj_edge(G.first_node())] = left
    
    if not(strongly_planar(G.first_adj_edge(G.first_node()),Att)):
        return 0
        #--------------------------------------------------------------
        
        
        #--------------------------------------------------------------
        # construct embedding
        
    global sort_num,tree_edge_into
    
    T=List()
    A=List()
    
    cur_nr=0
    sort_num={}
    tree_edge_into={}
    
    embedding(G.first_adj_edge(G.first_node()),left,T,A)
    
    # |T| contains all edges incident to the first node except the
    # cycle edge into it. 
    # That edge comprises |A|.
    T.conc(A)
    
    for e in T.elements:
        sort_num[e]=cur_nr 
        cur_nr=cur_nr+1 
        
    H.sort_edges(sort_num)  
    #--------------------------------------------------------------
    
    return H.all_edges() # ccwOrderedEges
    
    #=============================================================================#
    
    
    #=============================================================================#
def pt_DFS(v):

    global G,reached
    
    S=Stack()
    
    if reached[v]==0:
        reached[v]=1
        S.Push(v)
        
    while S.IsNotEmpty():
        v=S.Pop()
        for w in G.adj_nodes(v):
            if reached[w]==0:
                reached[w]=1
                S.Push(w)
                #=============================================================================#
                
                
                #=============================================================================#
def Make_biconnected_graph():
# We first make it connected by linking all roots of a DFS-forest.
# Assume now that G is connected.
# Let a be any articulation point and let u and v be neighbors
# of a belonging to different biconnected components.
# Then there are embeddings of the two components with the edges
# {u,a} and {v,a} on the boundary of the unbounded face.
# Hence we may add the edge {u,v} without destroying planarity.
# Proceeding in this way we make G biconnected.

    global G,reached,dfsnum,parent,dfs_count,lowpt
    
    #-------------------------------------------------------------- 
    # We first make G connected by linking all roots of the DFS-forest.
    reached={}
    for v in G.all_nodes():
        reached[v]=0
    u=G.first_node()
    
    for v in G.all_nodes():
        if  not(reached[v]):
            # explore the connected component with root v
            pt_DFS(v)
            if u!=v:
                # link v's component to the first component
                G.new_edge(u,v)
                G.new_edge(v,u)
                #-------------------------------------------------------------- 
                
                
                #-------------------------------------------------------------- 
                # We next make G biconnected.
    for v in G.all_nodes():
        reached[v]=0
    dfsnum={}
    parent={}
    for v in G.all_nodes():
        parent[v]=None
    dfs_count=0
    lowpt={}
    dfs_in_make_biconnected_graph(G.first_node())
    #--------------------------------------------------------------
    
    
    #=============================================================================#
    
    
    
    #=============================================================================#
def dfs_in_make_biconnected_graph(v):
# This procedure determines articulation points and adds appropriate
# edges whenever it discovers one.

    global G,reached,dfsnum,parent,dfs_count,lowpt
    
    dfsnum[v]=dfs_count
    dfs_count=dfs_count+1
    lowpt[v]=dfsnum[v]
    reached[v]=1
    
    if not(G.first_adj_edge(v)): return # no children
    
    u=target(G.first_adj_edge(v)) # first child
    
    for e in G.adj_edges(v):
        w=target(e)
        if not(reached[w]):
            # e is a tree edge
            parent[w]=v
            dfs_in_make_biconnected_graph(w)
            if lowpt[w]==dfsnum[v]:
                # v is an articulation point. We now add an edge.
                # If w is the first child and v has a parent then we 
                # connect w and parent[v], if w is a first child and v 
                # has no parent then we do nothing.
                # If w is not the first child then we connect w to the
                # first child.
                # The net effect of all of this is to link all children
                # of an articulation point to the first child and the
                # first child to the parent (if it exists).
                if w==u and parent[v]:
                    G.new_edge(w,parent[v])
                    G.new_edge(parent[v],w)
                if w!=u:
                    G.new_edge(u,w)
                    G.new_edge(w,u)
                    
            lowpt[v]=min(lowpt[v],lowpt[w])
            
        else:
            lowpt[v]=min(lowpt[v],dfsnum[w]) # non tree edge
            #=============================================================================#
            
            
            
            #=============================================================================#
def reorder():
# The procedure reorder first performs DFS to compute dfsnum, parent
# lowpt1 and lowpt2, and the list Del of all forward edges and all
# reversals of tree edges.
# It then deletes the edges in Del and finally reorders the edges.

    global G,dfsnum,parent,reached,dfs_count,Del,lowpt1,lowpt2
    
    reached={}
    for v in G.all_nodes():
        reached[v]=0
    dfs_count = 0
    Del=[]
    lowpt1={}
    lowpt2={}
    
    dfs_in_reorder(G.first_node())
    
    #--------------------------------------------------------------       
    # remove forward and reversals of tree edges
    for e in Del:
        G.del_edge(e)
        #--------------------------------------------------------------
        
        
        #--------------------------------------------------------------     
        # we now reorder adjacency lists 
    cost={}
    for e in G.all_edges():
        v = source(e)
        w = target(e)
        if dfsnum[w]<dfsnum[v]:
            cost[e]=2*dfsnum[w]
        elif lowpt2[w]>=dfsnum[v]:
            cost[e]=2*lowpt1[w]
        else:
            cost[e]=2*lowpt1[w]+1
    G.sort_edges(cost)
    #--------------------------------------------------------------
    
    
    #=============================================================================#
    
    
    
    #=============================================================================#
def dfs_in_reorder(v):

    global G,dfsnum,parent,reached,dfs_count,Del,lowpt1,lowpt2
    
    #--------------------------------------------------------------    
    dfsnum[v]=dfs_count
    dfs_count=dfs_count+1
    lowpt1[v]=lowpt2[v]=dfsnum[v]
    reached[v]=1
    for e in G.adj_edges(v):
        w = target(e);
        if not(reached[w]):
            # e is a tree edge
            parent[w]=v
            dfs_in_reorder(w)
            lowpt1[v]=min(lowpt1[v],lowpt1[w])
        else:
            lowpt1[v]=min(lowpt1[v],dfsnum[w]) # no effect for forward edges
            if dfsnum[w]>=dfsnum[v] or w==parent[v]: 
               # forward edge or reversal of tree edge
                Del.append(e) 
                #--------------------------------------------------------------
                
                
                #--------------------------------------------------------------
                # we know |lowpt1[v]| at this point and now make a second pass over all
                # adjacent edges of |v| to compute |lowpt2|
    for e in G.adj_edges(v):
        w = target(e)
        if parent[w]==v:
            # tree edge
            if lowpt1[w]!=lowpt1[v]:
                lowpt2[v]=min(lowpt2[v],lowpt1[w])
            lowpt2[v]=min(lowpt2[v],lowpt2[w])
        else:
            # all other edges 
            if lowpt1[v]!=dfsnum[w]:
                lowpt2[v]=min(lowpt2[v],dfsnum[w])
                #--------------------------------------------------------------
                
                
                #=============================================================================#
                
                
                
                #=============================================================================#
def strongly_planar(e0,Att):
# We now come to the heart of the planarity test: procedure strongly_planar.
# It takes a tree edge e0=(x,y) and tests whether the segment S(e0) is 
# strongly planar. 
# If successful it returns (in Att) the ordered list of attachments of S(e0) 
# (excluding x); high DFS-numbers are at the front of the list.
# In alpha it records the placement of the subsegments.
#
# strongly_planar operates in three phases.
# It first constructs the cycle C(e0) underlying the segment S(e0). 
# It then constructs the interlacing graph for the segments emanating >from the
# spine of the cycle.
# If this graph is non-bipartite then the segment S(e0) is non-planar.
# If it is bipartite then the segment is planar.
# In this case the third phase checks whether the segment is strongly planar 
# and, if so, computes its list of attachments.

    global G,alpha,dfsnum,parent
    
    #--------------------------------------------------------------
    # DETERMINE THE CYCLE C(e0)
    # We determine the cycle "C(e0)" by following first edges until a back 
    # edge is encountered. 
    # |wk| will be the last node on the tree path and |w0|
    # is the destination of the back edge.
    x=source(e0)
    y=target(e0)
    e=G.first_adj_edge(y)
    wk=y
    
    while dfsnum[target(e)]>dfsnum[wk]:  # e is a tree edge
        wk=target(e)
        e=G.first_adj_edge(wk)
    w0=target(e)
    #--------------------------------------------------------------
    
    
    #--------------------------------------------------------------
    # PROCESS ALL EDGES LEAVING THE SPINE
    # The second phase of |strongly_planar| constructs the connected 
    # components of the interlacing graph of the segments emananating 
    # from the the spine of the cycle "C(e0)". 
    # We call a connected component a "block". 
    # For each block we store the segments comprising its left and 
    # right side (lists |Lseg| and |Rseg| contain the edges defining 
    # these segments) and the ordered list of attachments of the segments
    # in the block; 
    # lists |Latt| and |Ratt| contain the DFS-numbers of the attachments; 
    # high DFS-numbers are at the front of the list. 
    #
    # We process the edges leaving the spine of "S(e0)" starting at 
    # node |wk| and working backwards. 
    # The interlacing graph of the segments emanating from
    # the cycle is represented as a stack |S| of blocks.
    w=wk
    S=Stack()
    
    while w!=x:
        count=0
        for e in G.adj_edges(w):
            count=count+1
            
            if count!=1: # no action for first edge
                # TEST RECURSIVELY
                # Let "e" be any edge leaving the spine. 
                # We need to test whether "S(e)" is strongly planar 
                # and if so compute its list |A| of attachments.
                # If "e" is a tree edge we call our procedure recursively 
                # and if "e" is a back edge then "S(e)" is certainly strongly 
                # planar and |target(e)| is the only attachment.
                # If we detect non-planarity we return false and free
                # the storage allocated for the blocks of stack |S|.
                A=List()
                if dfsnum[w]<dfsnum[target(e)]: 
                    # tree edge
                    if not(strongly_planar(e,A)):
                        while S.IsNotEmpty(): S.Pop()
                        return 0                    
                else:
                    A.append(dfsnum[target(e)]) # a back edge
                    
                    # UPDATE STACK |S| OF ATTACHMENTS
                    # The list |A| contains the ordered list of attachments 
                    # of segment "S(e)". 
                    # We create an new block consisting only of segment "S(e)" 
                    # (in its L-part) and then combine this block with the 
                    # topmost block of stack |S| as long as there is interlacing. 
                    # We check for interlacing with the L-part. 
                    # If there is interlacing then we flip the two sides of the 
                    # topmost block. 
                    # If there is still interlacing with the left side then the 
                    # interlacing graph is non-bipartite and we declare the graph 
                    # non-planar (and also free the storage allocated for the
                    # blocks).
                    # Otherwise we check for interlacing with the R-part. 
                    # If there is interlacing then we combine |B| with the topmost
                    # block and repeat the process with the new topmost block.
                    # If there is no interlacing then we push block |B| onto |S|.
                B=block(e,A)
                
                while 1:
                    if B.left_interlace(S): (S.contents[-1]).flip()
                    if B.left_interlace(S): 
                        del B
                        while S.IsNotEmpty(): S.Pop() 
                        return 0
                    if B.right_interlace(S): B.combine(S.Pop())
                    else: break
                S.Push(B)
                
                # PREPARE FOR NEXT ITERATION
                # We have now processed all edges emanating from vertex |w|. 
                # Before starting to process edges emanating from vertex
                # |parent[w]| we remove |parent[w]| from the list of attachments
                # of the topmost 
                # block of stack |S|. 
                # If this block becomes empty then we pop it from the stack and 
                # record the placement for all segments in the block in array
                # |alpha|.
        while (S.IsNotEmpty() and
               (S.contents[-1]).clean(dfsnum[parent[w]],alpha,dfsnum)):
            S.Pop()
            
        w=parent[w]
        #--------------------------------------------------------------
        
        
        #--------------------------------------------------------------
        # TEST STRONG PLANARITY AND COMPUTE Att
        # We test the strong planarity of the segment "S(e0)". 
        # We know at this point that the interlacing graph is bipartite. 
        # Also for each of its connected components the corresponding block 
        # on stack |S| contains the list of attachments below |x|. 
        # Let |B| be the topmost block of |S|. 
        # If both sides of |B| have an attachment above |w0| then 
        # "S(e0)" is not strongly planar. 
        # We free the storage allocated for the blocks and return false.
        # Otherwise (cf. procedure |add_to_Att|) we first make sure that 
        # the right side of |B| attaches only to |w0| (if at all) and then 
        # add the two sides of |B| to the output list |Att|.
        # We also record the placements of the subsegments in |alpha|.
    Att.clear()
    
    while S.IsNotEmpty():
        B = S.Pop()
        
        if (not(B.empty_Latt()) and not(B.empty_Ratt()) and
            B.head_of_Latt()>dfsnum[w0] and B.head_of_Ratt()>dfsnum[w0]):
            del B
            while S.IsNotEmpty(): S.Pop()
            return 0
        B.add_to_Att(Att,dfsnum[w0],alpha,dfsnum)
        del B
        
        # Let's not forget that "w0" is an attachment
        # of "S(e0)" except if w0 = x.
    if w0!=x: Att.append(dfsnum[w0])
    
    return 1
    #--------------------------------------------------------------
    
    
    #=============================================================================#
    
    
    
    #=============================================================================#
def embedding(e0,t,T,A):
# embed: determine the cycle "C(e0)" 
#
# We start by determining the spine cycle.
# This is precisley as in |strongly_planar|. 
# We also record for the vertices w_r+1, ...,w_k, and w_0 the 
# incoming cycle edge either in |tree_edge_into| or in the local
# variable |back_edge_into_w0|.

    global G,dfsnum,cur_nr,sort_num,tree_edge_into,parent
    
    x=source(e0)
    y=target(e0)
    tree_edge_into[y]=e0
    e=G.first_adj_edge(y)
    wk=y
    
    while (dfsnum[target(e)]>dfsnum[wk]):  # e is a tree edge
        wk=target(e)
        tree_edge_into[wk]=e
        e=G.first_adj_edge(wk)
        
    w0=target(e)
    back_edge_into_w0=e
    
    
    # process the subsegments
    w=wk
    Al=List()
    Ar=List()
    Tprime=List()
    Aprime=List()
    
    T.clear()  
    T.append(e)    # |e=(wk,w0)| at this point
    
    while w!=x:
        count=0
        for e in G.adj_edges(w):
            count=count+1
            if count!=1: # no action for first edge
                # embed recursively
                if dfsnum[w]<dfsnum[target(e)]:
                    # tree edge
                    if t==alpha[e]:
                        tprime=left
                    else:
                        tprime=right
                    embedding(e,tprime,Tprime,Aprime)
                else: 	
                    # back edge
                    Tprime.append(e)
                    Aprime.append(reversal(e))
                    
                    # update lists |T|, |Al|, and |Ar|
                if t==alpha[e]:
                    Tprime.conc(T)
                    T.conc(Tprime) # T = Tprime conc T
                    Al.conc(Aprime) # Al = Al conc Aprime
                else:	
                    T.conc(Tprime) # T = T conc Tprime
                    Aprime.conc(Ar)
                    Ar.conc(Aprime) # Ar = Aprime conc Ar
                    
                    # compute |w|'s adjacency list and prepare for next iteration
        T.append(reversal(tree_edge_into[w])) # (w_j-1,w_j)
        for e in T.elements:
            sort_num[e]=cur_nr
            cur_nr=cur_nr+1
            
            # |w|'s adjacency list is now computed; we clear |T| and 
            # prepare for the next iteration by moving all darts incident
            # to |parent[w]| from |Al| and |Ar| to |T|.
            # These darts are at the rear end of |Al| and at the front end
            # of |Ar|.
        T.clear()
        
        while not(Al.empty()) and source(Al.tail())==parent[w]: 
        # |parent[w]| is in |G|, |Al.tail| in |H|
            T.push(Al.Pop()) # Pop removes from the rear
            
        T.append(tree_edge_into[w]) # push would be equivalent
        
        while not(Ar.empty()) and source(Ar.head())==parent[w]: 
            T.append(Ar.pop()); # pop removes from the front
            
        w=parent[w]
        
        # prepare the output
    A.clear()
    A.conc(Ar)
    A.append(reversal(back_edge_into_w0))
    A.conc(Al)
    #=============================================================================#
    
    
    
    
    
    
    
    
    
    
    
    
    ###############################################################################
    # DEBUG                                                                       #
    ###############################################################################
    
    #=============================================================================#
def PrintGraph(G):
    print "============================================================"
    print "V : "
    for v in G.all_nodes():
        print "[%i]" %(v-1)
    print
    
    print "E : "
    for e in G.all_edges():
        print "[%i]---->[%i]" %((source(e)-1),(target(e)-1))
    print
    
    for v in G.all_nodes():
        print "[%i] : " %(v-1)
        for e in G.adj_edges(v):
            print "    [%i]---->[%i]" %((source(e)-1),(target(e)-1))
    print
    #=============================================================================#
    
    #=============================================================================#
def SaveGmlGraph(G, fileName):    
    file = open(fileName, 'w')
    
    file.write("graph [ \n")
    file.write("  directed 1 \n \n")
    
    for v in G.vertices:
        file.write("  node [ id ")
        n=str(v)
        file.write(n)
        file.write(" ] \n")
        
    file.write("\n")
    
    for e in G.Edges():
        file.write("  edge [ \n")
        
        file.write("    source ")
        k=str(e[0])
        file.write(k)
        file.write("\n")
        
        file.write("    target ")
        k=str(e[1])
        file.write(k)
        file.write("\n")
        
        file.write("  ] \n")
        
    file.write("] \n")
    #=============================================================================#
