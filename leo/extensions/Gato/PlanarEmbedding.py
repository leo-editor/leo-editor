################################################################################
#
#       This file is part of Gato (Graph Algorithm Toolbox) 
#
#	file:   PlanarEmbedding.py
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
#                    THE "DE FRAYSSEIX,PACH,POLLACK(FPP)"                     #
#                             AND THE "SCHNYDER"                              #
#                   PLANAR STRAIGHT-LINE EMBEDDING ALGORITHM                  #
#                                                                             #
###############################################################################
#                                                                             #
# References:                                                                 #
#                                                                             #
# [FPP90] H. de Fraysseix, J.Pach, and R.Pollack .                            #
#         "How to draw a planar graph on a grid."                             #
#         Combinatorian, 10:41-51,1990                                        #
# [Sch90] W.Schnyder.                                                         #
#         "Embedding planar graphs on the grid."                              #
#         In 1st Annual ACM-SIAM Symposium on Discrete Algorithms,            #
#         pages 138-14, San Francisco, 1990                                   #
#                                                                             #
###############################################################################



#=============================================================================#
from PlanarityTest import *
from copy import deepcopy
from DataStructures import Stack
from tkMessageBox import showinfo
#=============================================================================#



#=============================================================================#
class pe_Point:

    def __init__(self,xpos,ypos):
        self.x=xpos
        self.y=ypos
        #=============================================================================#
        
        
        
        #=============================================================================#
class pe_Node:

    def __init__(self,x,y):
        self.xpos=x
        self.ypos=y
        self.canOrder=None
        self.t1,self.t2,self.t3=None,None,None 
        self.p1,self.p2,self.p3=None,None,None 
        self.r1,self.r2,self.r3=None,None,None 
        self.xsch,self.ysch=None,None
        self.xfpp,self.yfpp=None,None
        self.adjacentEdges=[]
        self.adjacentNodes=[]
        self.M=[]
        self.oppositeNodes=[]
        self.outface=None
        
        self.path1=[]
        self.path2=[]
        self.path3=[]   
        
    def addEdge(self,e,v):
        self.adjacentEdges.append(e)
        self.adjacentNodes.append(v)
        #=============================================================================#
        
        
        
        #=============================================================================#
class pe_Edge: # directed from p1->p2

    def __init__(self,index_p1,index_p2,ep1,ep2,tf):
        self.p1=index_p1
        self.p2=index_p2
        self.label=None # normal labelling: 1,-1,2,-2,3,-3
        self.original=tf
        self.outface=None
        #=============================================================================#
        
        
        
        #=============================================================================#
class pe_Graph:

    #-------------------------------------------------------------------------
    def printGraph(self):
    
        for i in range(0,len(self.nodes)):
            n=self.nodes[i]
            print "--------Node:",i,"--------------"
            print "xpos=",n.xpos,"ypos=",n.ypos
            print "canOrder=",n.canOrder
            print "t1=",n.t1,"t2=",n.t2,"t3=",n.t3
            print "p1=",n.p1,"p2=",n.p2,"p3=",n.p3
            print "r1=",n.r1,"r2=",n.r2,"r3=",n.r3
            print "xsch=",n.xsch,"ysch=",n.ysch
            print "xfpp=",n.xfpp,"yfpp=",n.yfpp
            print "outface=",n.outface
            
        print
        for i in range(0,len(self.edges)):
            e=self.edges[i]
            print "-------Edge:",i,"---------------"
            print "p1=",e.p1,"p2=",e.p2
            print "label=",e.label
            print "original=",e.original,"outface=",e.outface
            
        print
        for i in range(0,len(self.nodes)):
            n=self.nodes[i]
            
            print "---------------------------"
            print i,":"
            
            print "adjacentEdges:",
            for j in range(0,len(n.adjacentEdges)):
                print n.adjacentEdges[j],
            print
            
            print "adjacentNodes:",
            for j in range(0,len(n.adjacentNodes)):
                print n.adjacentNodes[j],
            print
            
            print "M:",
            for j in range(0,len(n.M)):
                print n.M[j],
            print
            
            print "oppositeNodes:",
            for j in range(0,len(n.oppositeNodes)):
                print n.oppositeNodes[j],
            print
            
            print "path1:",
            for j in range(0,len(n.path1)):
                print n.path1[j],
            print
            
            print "path2:",
            for j in range(0,len(n.path2)):
                print n.path2[j],
            print
            
            print "path3:",
            for j in range(0,len(n.path3)):
                print n.path3[j],
            print
            #-------------------------------------------------------------------------
            
            
            #-------------------------------------------------------------------------
    def __init__(self):
        self.nodes=[]
        self.edges=[]
        
        self.orderK,self.orderIndexVk=None,None
        self.FPPk=None
        self.labelK=None
        self.indexV1,self.indexV2,self.indexV3=-1,-1,-1
        #-------------------------------------------------------------------------
        
        
        #-------------------------------------------------------------------------
    def checkIndex(self,index, p1):
        if index<0:
            tempNode1=pe_Node(p1.x,p1.y)
            self.nodes.append(tempNode1)
            return (len(self.nodes)-1)
        return index
        #-------------------------------------------------------------------------
        
        
        #-------------------------------------------------------------------------
    def storeEdge(self,indexP1,indexP2,p1,p2,tf):
        ep1=pe_Point(self.nodes[indexP1].xpos,self.nodes[indexP1].ypos)
        ep2=pe_Point(self.nodes[indexP2].xpos,self.nodes[indexP2].ypos)
        self.edges.append(pe_Edge(indexP1,indexP2,ep1,ep2,tf))
        #-------------------------------------------------------------------------
        
        
        
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # TRIANGULATION
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Algorithm:
        # For each vertex v
        #     for v's each pair of consecutive neighbours u & w
        #             add the edge in
        #             add u into w's incident list in ccw order
        #             add w into u's incident list in ccw order
        #             repeat this procedure
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        
        #-------------------------------------------------------------------------
    def isEdge(self,u,w):
        # check if w is in u's adjacentEdges
        if w in u.adjacentNodes: return 1
        return 0
        #-------------------------------------------------------------------------
        
        
        #-------------------------------------------------------------------------
    def adjacentVertex(self,v,e):
        return v.adjacentNodes[e]
        #-------------------------------------------------------------------------
        
        
        #-------------------------------------------------------------------------
    def consider(self):
        for indexV in range(0,len(self.nodes)):
            v=self.nodes[indexV]
            
            if len(v.adjacentEdges)<2: continue
            
            for j in range(0,len(v.adjacentEdges)):
                # get two consective neighbours of v
                indexU=self.adjacentVertex(v,j)
                u=self.nodes[indexU]
                k=j+1
                if k==len(v.adjacentEdges): k=0
                indexW=self.adjacentVertex(v,k)
                w=self.nodes[indexW]
                
                # check if (u, w) is an edge
                if not(self.isEdge(u,indexW)):
                    pointu=pe_Point(u.xpos,u.ypos)
                    pointw=pe_Point(w.xpos,w.ypos)
                    self.storeEdge(indexU,indexW,pointu, pointw,0)
                    
                    tempi1=indexV
                    tempe1=len(self.edges)-1
                    
                    # add u to w's adjacentEdges (with ordering)
                    # add u after v in w's adjacentEdges
                    indexVinW=w.adjacentNodes.index(tempi1)+1
                    w.adjacentEdges.insert(indexVinW,tempe1)
                    w.adjacentNodes.insert(indexVinW,indexU)
                    
                    # add w to u's incitentList (with ordering)
                    # add w before v in u's adjacentEdges
                    indexVinU=u.adjacentNodes.index(tempi1)
                    u.adjacentEdges.insert(indexVinU,tempe1)
                    u.adjacentNodes.insert(indexVinU,indexW)
                    
                    # Don't forget to set original=0
                    self.edges[-1].original=0
                    
                    return 1
        return 0
        #-------------------------------------------------------------------------
        
        
        #-------------------------------------------------------------------------
    def triangulate(self):
        finish=1
        while finish:
            finish=self.consider()
            #-------------------------------------------------------------------------
            
            #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            
            
            
            #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            # CANONICAL ORDERING
            #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            # Algorithm:
            # Pick up a face as outface
            # Assign its vertices with canonical ordering 1,2, and n
            #
            # For k from n-1 to 3 
            #     remove Vk+1 from graph
            #     find all Vk+1's neighbours in the new graph Gk
            #     update the vertices on the outface
            #     assign Vk to one of these neighbours on Ck that
            #                                              is not V1
            #                                              is not V2
            #                                              is not incident to a chord
            #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            
            #-------------------------------------------------------------------------
    def ordering(self):
        self.orderK=len(self.nodes)
        
        # Now, remove Vn from the graph, and let Vn-1 be the vertex 
        # that is on the outerface and not incident to a chord.
        k=len(self.nodes)
        while k>3:
            self.orderIndexVk=self.order()
            k=k-1
            #-------------------------------------------------------------------------
            
            
            #-------------------------------------------------------------------------
    def initOrder(self):
        # NOTE: initially, all the canOrder are 0
        for i in range(0,len(self.nodes)):
            self.nodes[i].canOrder=0
            
            # Base: find v1, v2, and vn, which define a outerface
        if self.indexV1<0:
            self.indexV1=0
            v1=self.nodes[self.indexV1]
            
            self.indexV2=v1.adjacentNodes[0]
            v2=self.nodes[self.indexV2]
            
            self.indexVn=v1.adjacentNodes[1]
            vk=self.nodes[self.indexVn]
        else:
            v1=self.nodes[self.indexV1]
            v2=self.nodes[self.indexV2]
            vk=self.nodes[self.indexVn]
            
        v1.canOrder=1
        v2.canOrder=2
        vk.canOrder=len(self.nodes)
        
        # initialize all the outface to 0
        for j in range(0,len(self.nodes)): 
            self.nodes[j].outface=0
            
        self.orderK=len(self.nodes)
        self.orderIndexVk=self.indexVn
        return self.indexVn
        #-------------------------------------------------------------------------
        
        
        #-------------------------------------------------------------------------
        # Now, remove Vn from the graph, and let Vn-1 be the vertex 
        # that is on the outerface and not incident to a chord
    def order(self):
        if self.orderK>3:
            v1=self.nodes[self.indexV1]
            v2=self.nodes[self.indexV2]
            vk=self.nodes[self.orderIndexVk]
            # "remove" Vk from the graph
            # find the neighbours of Vk, that have canOrder number < k
            # define they are on the outface
            for i in range(0,len(vk.adjacentNodes)):
                neighbour=self.nodes[vk.adjacentNodes[i]]
                
                if neighbour.canOrder<self.orderK:
                    neighbour.outface=1
                    
                    # find the node that is not v1, v2, and not incident to any chord,
                    # let it be Vk-1
            found=0
            j=0
            while not(found) and j<len(self.nodes):
                candidate=self.nodes[j]
                if (candidate.outface and candidate!=v1 and
                    candidate!=v2 and candidate.canOrder<self.orderK):
                    # if it only has 2 neighbours on the outface,
                    # we set it to be Vk-1
                    count=0
                    for i in range(0,len(candidate.adjacentNodes)):
                        checkIndex=candidate.adjacentNodes[i]
                        checkNode=self.nodes[checkIndex]
                        if (checkNode.outface and
                            (checkNode.canOrder<self.orderK)):
                            count=count+1
                    if count==2:
                        found=1
                        vk=candidate
                        candidate.canOrder=self.orderK-1
                        
                        self.orderK=self.orderK-1
                        self.orderIndexVk=j
                        return j
                j=j+1
        return -1
        #-------------------------------------------------------------------------
        
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        
        
        
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # EDGE LABELLING 
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Algorithm:
        # In triangle V1, V2, V3 (canonical order)
        #     label V3->V1 with 1
        #     label V3->V2 with 2
        #
        # For k from 3 to n-1   
        #     add Vk+1 to graph Gk
        #     find all Vk+1's neighbours in Gk in order
        #     label the left most edge from top to bottom with 1
        #     label the right most edge from top to bottom with 2
        #     label the rest from bottom to top with 3
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        
        #-------------------------------------------------------------------------
    def labelling(self):
        self.initLabel()
        #steps
        for k in range(3,len(self.nodes)):
            self.labelK=k
            self.labelStep()
            # looking for v4, v5, ..., vn
            #-------------------------------------------------------------------------
            
            
            #-------------------------------------------------------------------------
            # label  label if the edge is indexP1 -> indexP2
            #       -label if the edge is indexP2 -> indexP1
    def labelEdge(self,indexP1,indexP2,label):
        e=self.edges[0]
        
        if e.p1==indexP1 and e.p2==indexP2:
            self.edges[0].label=label
            return
        if e.p1==indexP2 and e.p2==indexP1:
            self.edges[0].label=-label 
            return
            
        for i in range(1,len(self.edges)):
            e=self.edges[i]
            if e.p1==indexP1 and e.p2==indexP2:
                e.label=label
                return
            if e.p1==indexP2 and e.p2==indexP1:
                e.label=-label
                return
                #-------------------------------------------------------------------------
                
                
                #-------------------------------------------------------------------------
    def findIndexOfVk(self,k):
        indexVk=-1
        i=0
        
        while indexVk<0:
            if self.nodes[i].canOrder==k:
                return i
            i=i+1
        return -1
        #-------------------------------------------------------------------------
        
        
        #-------------------------------------------------------------------------
    def initLabel(self):
        for j in range(0,len(self.edges)):
            self.edges[j].label=0
            
        self.indexV3=self.findIndexOfVk(3)
        
        # find v1, v2, v3
        v1=self.nodes[self.indexV1]
        v2=self.nodes[self.indexV2]
        v3=self.nodes[self.indexV3]
        
        # labelling should be done at the same time as FPP is running
        # (because we need the outface information)
        # but we are doing this separately, for the sak of clearness
        
        # label V3 -> V1 by 1
        self.labelEdge(self.indexV3,self.indexV1,1)
        
        # label V3 -> V2 by 2
        self.labelEdge(self.indexV3,self.indexV2,2)
        
        self.labelK = 3
        #-------------------------------------------------------------------------
        
        
        #-------------------------------------------------------------------------
    def labelStep(self):
        k=self.labelK
        n=len(self.nodes)
        
        if k<n:
            indexVkplus1=self.findIndexOfVk(k+1)
            vkplus1=self.nodes[indexVkplus1]
            
            # labelling should be done at the same time as FPP is running
            # (because we need the outface information)
            # case 1: vk+1 is "to the right" of vk
            # case 2: vk+1 is "to the left" of vk
            # case 3: vk+1 "covers" vk
            # all make the first element in Vk+1's oppositeNodes label 1, 
            #   	   last                                        2,
            #  		   rest        	   			       3.
            # oppositeNodes is done in FPP
            
            first=vkplus1.oppositeNodes[0]
            self.labelEdge(indexVkplus1,first,1)
            
            last=vkplus1.oppositeNodes[-1]
            self.labelEdge(indexVkplus1,last,2)
            
            if len(vkplus1.oppositeNodes)>2:
                for l in range(1,len(vkplus1.oppositeNodes)-1):
                    self.labelEdge(indexVkplus1,vkplus1.oppositeNodes[l],-3)
                    
            self.labelK=self.labelK+1
        return self.labelK
        #-------------------------------------------------------------------------
        
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        
        
        
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # FPP
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Algorithm:
        # 3. Initialize x,y coordinates and M for V1,V2, and V3
        #                               v1.M={v1,v2,v3}
        #                               v2.M={v2}
        #                               v3.M={v2,v3}
        # 4. In the canonical order, for each vertex
        #       1. find the vertices on the outface in order
        #       2. shift vertices in the subset M of Wp+1 and Wq
        #       3. calculate the x,y coordinates of Vk+1
        #       4. updating M for all the outface vertices
        #                               wi.M=wi.M+{vk+1}  for i<=p
        #                               vk+1.M=wp+1.M+{vk+1}
        #                               wj.M=wj.M  for j>=q
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        
        #-------------------------------------------------------------------------
    def FPP(self):
        self.initFPP()
        
        # steps
        for k in range(3,len(self.nodes)):
            self.FPPk=k
            self.FPPstep()
            #-------------------------------------------------------------------------
            
            
            #-------------------------------------------------------------------------
    def initFPP(self):
        self.indexV3=self.findIndexOfVk(3)
        
        # initialize all the outface to 0
        for j in range(0,len(self.nodes)):
            self.nodes[j].outface=0
            self.nodes[j].xfpp=0
            self.nodes[j].yfpp=0
            self.nodes[j].M=[]
            self.nodes[j].oppositeNodes=[]
            
            # find v1, v2, v3
        v1=self.nodes[self.indexV1]
        v2=self.nodes[self.indexV2]
        v3=self.nodes[self.indexV3] 
        
        # basic
        v1.xfpp=0; v1.yfpp=0
        v2.xfpp=2; v2.yfpp=0
        v3.xfpp=1; v3.yfpp=1
        
        # v1.M={v1,v2,v3} v2.M={v2} v3.M={v2,v3}
        v1.M.append(self.indexV1)
        v1.M.append(self.indexV2)
        v1.M.append(self.indexV3)
        
        v2.M.append(self.indexV2)
        
        v3.M.append(self.indexV2)
        v3.M.append(self.indexV3) 
        
        self.nodes[self.indexV1].outface=1
        self.nodes[self.indexV2].outface=1
        self.nodes[self.indexV3].outface=1
        
        self.FPPk=3
        #-------------------------------------------------------------------------
        
        
        #-------------------------------------------------------------------------
    def FPPstep(self):
        k=self.FPPk
        n=len(self.nodes)
        
        if k<n:
            indexVkplus1=self.findIndexOfVk(k+1)
            vkplus1=self.nodes[indexVkplus1]
            
            # find the vertices on the outerface of Gk,
            # and in order of p, p+1, ..., q
            # find the neighbours of v(k+1) with CanOrder <= k,
            # and sort them according to their xfpp
            for i in range(0,len(vkplus1.adjacentNodes)):
                neighbour=self.nodes[vkplus1.adjacentNodes[i]]
                if neighbour.canOrder<=k:
                    insertPlace=-1
                    j=0
                    while insertPlace<0 and j<len(vkplus1.oppositeNodes):
                        if (neighbour.xfpp <
                            self.nodes[vkplus1.oppositeNodes[j]].xfpp):
                            insertPlace=j
                        j=j+1
                        
                    if insertPlace==-1:
                        vkplus1.oppositeNodes.append(
                            self.nodes.index(neighbour))
                    else:
                        vkplus1.oppositeNodes.insert(insertPlace,
                                                 self.nodes.index(neighbour))
                        
                        # find the vertices on the outface
            self.nodes[indexVkplus1].outface=1
            if len(vkplus1.oppositeNodes)>2:
                for i in range(1,len(vkplus1.oppositeNodes)-1):
                    temp=vkplus1.oppositeNodes[i]
                    self.nodes[temp].outface=0
                    
                    # shift all vertices in w(p+1).M right by 1 unit
            indexWpplus1=vkplus1.oppositeNodes[1]
            w=self.nodes[indexWpplus1]
            for i in range(0,len(w.M)):
                temp=w.M[i]
                self.nodes[temp].xfpp=self.nodes[temp].xfpp+1
                
                # shift all vertices in w(q).M right by 1 unit
            Wq=self.nodes[vkplus1.oppositeNodes[-1]]
            for i in range(0,len(Wq.M)): 
                self.nodes[Wq.M[i]].xfpp=self.nodes[Wq.M[i]].xfpp+1
                
                # add in v(k+1)
                
            Wp=self.nodes[vkplus1.oppositeNodes[0]]
            x1=Wp.xfpp
            y1=Wp.yfpp
            x2=Wq.xfpp
            y2=Wq.yfpp
            
            vkplus1.xfpp=(x1+x2+y2-y1)/2
            vkplus1.yfpp=(x2-x1+y2+y1)/2
            
            # update M
            # wi.M = wi.M + v(k+1)  for i<=p
            for i in range(0,n):
                wi=self.nodes[i]
                if wi.outface  and  wi.xfpp<w.xfpp and i!=indexVkplus1:
                    wi.M.append(indexVkplus1)
                    
                    # v(k+1).M = w(p+1).M + v(k+1)
            vkplus1.M.append(indexVkplus1)
            for i in range(0,len(w.M)):
                vkplus1.M.append(w.M[i])
                
                
            self.FPPk=self.FPPk+1
            
        return self.FPPk
        #-------------------------------------------------------------------------
        
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        
        
        
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # SCHNYDER
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Algorithm:
        # 4. Calculate for each interior vertex v
        #              pathi : vertices on the i-path from v to v1, v2, or vn
        #              pn : number of vertices on the i-path starting at v
        #              ti : number of vertices in the subtree of Ti rooted at v
        #              ri : number of vertices in region Ri(v) for v
        # 5. Calculate barycentric representation for each v: vi'=ri - pi-1
        #                                            v->(v1',v2',v3')/(n-1)
        #    A barycentric representation of a graph G is 
        #    an injective function v->(v1,v2,v3) that satisfies:
        #      a.) v1+v2+v3=1 for all v
        #      b.) for each edge (x,y) and each vertex z not x or y,
        #          there is some k (k=1,2 or 3) such that xk < zk and yk < zk   
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        
        #-------------------------------------------------------------------------
    def calculateP(self,path123):
        for i in range(0,len(self.nodes)):
            v=self.nodes[i] 
            finalNode=0
            
            if (v.canOrder!=1 and v.canOrder!=2 and 
                v.canOrder!=len(self.nodes)):
                # v is an interior vertex
                if path123==1:
                    v.p1=1
                    v.path1.append(i)
                    finalNode=1
                if path123==2:
                    v.p2=1
                    v.path2.append(i)
                    finalNode=2
                if path123==3:
                    v.p3=1
                    v.path3.append(i)
                    finalNode=len(self.nodes)
                    
                vNext=v
                while vNext.canOrder!=finalNode:
                    j=0
                    found=0
                    while (not(found) and j<len(vNext.adjacentEdges)):
                        curEdge=self.edges[vNext.adjacentEdges[j]]
                        curLabel=curEdge.label
                        # HIER IST IRGENDWO EIN FEHLER !!!!!!
                        if ( ((curLabel==path123) and 
                              (curEdge.p1==self.nodes.index(vNext))) or 
                             ((curLabel==-path123) and
                              (curEdge.p2==self.nodes.index(vNext))) ):
                            found=1
                            vNextIndex=vNext.adjacentNodes[j]
                            vNext=self.nodes[vNextIndex]
                            
                            if path123==1:
                                v.p1=v.p1+1
                                v.path1.append(vNextIndex)
                            if path123==2:
                                v.p2=v.p2+1
                                v.path2.append(vNextIndex)
                            if path123==3:
                                v.p3=v.p3+1
                                v.path3.append(vNextIndex)
                        j=j+1
                        #-------------------------------------------------------------------------
                        
                        
                        #-------------------------------------------------------------------------
    def traverse(self,label,v,count):
        for j in range(0,len(v.adjacentEdges)):
            curEdge=self.edges[v.adjacentEdges[j]]
            curLabel=curEdge.label
            if ( ((curLabel==-label) and 
                  (curEdge.p1==self.nodes.index(v))) or
                 ((curLabel==label) and
                  (curEdge.p2==self.nodes.index(v))) ):
                vNextIndex=v.adjacentNodes[j]
                vNext=self.nodes[vNextIndex]
                count=count+1
                count=self.traverse(label,vNext,count)
        return count
        #-------------------------------------------------------------------------
        
        
        #-------------------------------------------------------------------------
    def Schnyder(self):
        # we need to compute p1, p2, p3 and t1, t2, t3 and
        # r1, r2, r3 for each vertex
    
        # Initialize the data
        for i in range(0,len(self.nodes)):
            tempnn1=self.nodes[i]
            tempnn1.p1=0
            tempnn1.p2=0
            tempnn1.p3=0
            tempnn1.t1=0
            tempnn1.t2=0
            tempnn1.t3=0
            tempnn1.r1=0
            tempnn1.r2=0
            tempnn1.r3=0
            tempnn1.xsch=0
            tempnn1.ysch=0
            tempnn1.path1=[]
            tempnn1.path2=[]
            tempnn1.path3=[]
            
            # find those for v1, v2, and vn
        v1=self.nodes[self.indexV1]
        v2=self.nodes[self.indexV2]
        vn=self.nodes[self.indexVn]
        v1.t1=0; v1.t2=1; v1.t3=1;
        v2.t1=1; v2.t2=0; v2.t3=1;
        vn.t1=1; vn.t2=1; vn.t3=0;
        v1.p1=0; vn.p1=1;
        v2.p2=0; vn.p2=1;
        
        v1.xsch=len(self.nodes)-1; v1.ysch=0;
        v2.xsch=0; v2.ysch=len(self.nodes)-1;
        vn.xsch=0; vn.ysch = 0;
        
        
        # can we get p1/p2/p3 while doing ordering or labelling???
        # Not really!!! We cannot get p3 easily
        
        # calculate p1, p2, p3 by going through path1, path2, path3
        self.calculateP(1)
        self.calculateP(2)
        self.calculateP(3)
        
        # calculate t1, t2, t3
        # exterior vertices are done in ordering
        # for each interior vertex v
        for i in range(0,len(self.nodes)):
            v=self.nodes[i]
            
            if (v.canOrder!=1 and v.canOrder!=2 and
                v.canOrder!=len(self.nodes)):
                # v is an interior vertex
                v.t1=self.traverse(1,v,1) # Itself is in the subtree
                v.t2=self.traverse(2,v,1) # Itself is in the subtree
                v.t3=self.traverse(3,v,1) # Itself is in the subtree
                
                # calculate r1, r2, r3
                # we need 3 vectors in each vertex to store the path 1,2,3
                # v.ri = ti of all vertices on P(i+1)+ti of all vertices on P(i-1)-ti
        for i in range(0,len(self.nodes)):
            v=self.nodes[i]
            
            if (v.canOrder!=1 and v.canOrder!=2 and
                v.canOrder!=len(self.nodes)):
                # v is an interior vertex
                v.r1=0; v.r2=0; v.r3=0;
                
                # r1
                for j in range(0,len(v.path2)):
                    onPath=self.nodes[v.path2[j]]
                    v.r1=v.r1+onPath.t1
                for j in range(0,len(v.path3)):
                    onPath=self.nodes[v.path3[j]]
                    v.r1=v.r1+onPath.t1
                v.r1=v.r1-v.t1
                
                # r2
                for j in range(0,len(v.path1)):
                    onPath=self.nodes[v.path1[j]]
                    v.r2=v.r2+onPath.t2
                for j in range(0,len(v.path3)):
                    onPath=self.nodes[v.path3[j]]
                    v.r2=v.r2+onPath.t2
                v.r2=v.r2-v.t2
                
                # r3
                for j in range(0,len(v.path1)):
                    onPath=self.nodes[v.path1[j]]
                    v.r3=v.r3+onPath.t3
                for j in range(0,len(v.path2)):
                    onPath=self.nodes[v.path2[j]]
                    v.r3=v.r3+onPath.t3
                v.r3=v.r3-v.t3
                
                
                # The coordinates of each vertex is (v'1, v'2), 
                # where v'i = ri - p(i-1)
                # exterior vertices are done in ordering
                # for each interior vertex v
        for i in range(0,len(self.nodes)):
            v=self.nodes[i]
            
            if (v.canOrder!=1 and v.canOrder!=2 and
                v.canOrder!=len(self.nodes)):
                # v is an interior vertex
                v.xsch=(v.r1-v.p3)
                v.ysch=(v.r2-v.p1)
                #-------------------------------------------------------------------------
                
                #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                
                
                #=============================================================================#
                # LOAD GRAPH
                
def load_graph(InGraph):

    if InGraph.Order()<3:
        return 0
        
    ccwOrderedEdges=planarity_test(InGraph)
    if not(ccwOrderedEdges):
        showinfo("Planarity Test", "Graph is NOT PLANAR!")
        return 0
        
    graph1=pe_Graph()
    
    i=0
    NodeIndex={}
    for v in InGraph.vertices:
        NodeIndex[v]=i
        i=i+1
        
    for i in range(0,InGraph.Order()):
        graph1.nodes.append(pe_Node(i,i))
        
    EdgeIndex={}
    for i in range(0,len(ccwOrderedEdges)):
        n1=NodeIndex[ccwOrderedEdges[i][0]]
        n2=NodeIndex[ccwOrderedEdges[i][1]]
        ccwOrderedEdges[i]=(n1,n2)
        EdgeIndex[(n1,n2)]=None
        
    i=0
    for e in ccwOrderedEdges:
        if EdgeIndex[e]==None:
            EdgeIndex[e]=i
            EdgeIndex[(e[1],e[0])]=i
            i=i+1
            p1=pe_Point(e[0],e[0])
            p2=pe_Point(e[1],e[1])
            tempe1=pe_Edge(e[0],e[1],p1,p2,1)
            graph1.edges.append(tempe1)
            
        graph1.nodes[e[0]].addEdge(EdgeIndex[e],e[1])
        
    return graph1
    #=============================================================================#
    
    
    
    #=============================================================================#
def FPP_PlanarCoords(G): # (2n-4)*(n-2) GRID
# Algorithm: 
# 1. Triangulate orginal graph
# 2. Canonical order all vertices
# 3. Initialize x,y coordinates and M for V1,V2, and V3
#                               v1.M={v1,v2,v3}
#                               v2.M={v2}
#                               v3.M={v2,v3}
# 4. In the canonical order, for each vertex
#       1. find the vertices on the outface in order
#       2. shift vertices in the subset M of Wp+1 and Wq
#       3. calculate the x,y coordinates of Vk+1
#       4. updating M for all the outface vertices
#                               wi.M=wi.M+{vk+1}  for i<=p
#                               vk+1.M=wp+1.M+{vk+1}
#                               wj.M=wj.M  for j>=q

    #-------------------------------------------------------------------------
    # LOAD GRAPH
    graph=load_graph(G)
    if graph==0: return 0
    #-------------------------------------------------------------------------
    
    
    #-------------------------------------------------------------------------
    # 1.TRIANGULATION
    graph.triangulate()
    #-------------------------------------------------------------------------
    
    
    #-------------------------------------------------------------------------
    # 2.CANONICAL ORDERING
    graph.initOrder()
    graph.ordering()
    #-------------------------------------------------------------------------
    
    
    #-------------------------------------------------------------------------
    # 3+4. FPP 
    graph.FPP()
    #-------------------------------------------------------------------------
    
    
    #-------------------------------------------------------------------------
    # COORDINATES
    G.xCoord={}
    G.yCoord={}
    n=len(graph.nodes)
    for i in range(0,n):
        G.xCoord[G.vertices[i]]=graph.nodes[i].xfpp*float(900/(2*n-4))+50
        G.yCoord[G.vertices[i]]=1000-(graph.nodes[i].yfpp*float(900/(n-2))+50)
    return 1
    #-------------------------------------------------------------------------
    
    #=============================================================================#
    
    
    
    #=============================================================================#
def Schnyder_PlanarCoords(G): # (n-1)*(n-1) GRID
# Algorithm: 
# 1. Triangulate orginal graph
# 2. Canonical order all vertices
# 3. Normal label interior edges of G to i->Ti (i=1,2,3)
# 4. Calculate for each interior vertex v
#              pathi : vertices on the i-path from v to v1, v2, or vn
#              pn : number of vertices on the i-path starting at v
#              ti : number of vertices in the subtree of Ti rooted at v
#              ri : number of vertices in region Ri(v) for v
# 5. Calculate barycentric representation for each v: vi'=ri - pi-1
#                                            v->(v1',v2',v3')/(n-1)
#    A barycentric representation of a graph G is 
#    an injective function v->(v1,v2,v3) that satisfies:
#      a.) v1+v2+v3=1 for all v
#      b.) for each edge (x,y) and each vertex z not x or y,
#          there is some k (k=1,2 or 3) such that xk < zk and yk < zk       

    #-------------------------------------------------------------------------
    # LOAD GRAPH
    graph=load_graph(G)
    if graph==0: return 0
    #-------------------------------------------------------------------------
    
    
    #-------------------------------------------------------------------------
    # 1.TRIANGULATION
    graph.triangulate()
    #-------------------------------------------------------------------------
    
    
    #-------------------------------------------------------------------------
    # 2.CANONICAL ORDERING
    graph.initOrder()
    graph.ordering()
    #-------------------------------------------------------------------------
    
    
    #-------------------------------------------------------------------------
    # 3. EDGE LABELLING 
    graph.FPP() # outfaces
    graph.labelling()
    #-------------------------------------------------------------------------
    
    
    #-------------------------------------------------------------------------
    # 4+5. Schnyder
    graph.Schnyder()
    #-------------------------------------------------------------------------
    
    
    #-------------------------------------------------------------------------
    # COORDINATES
    G.xCoord={}
    G.yCoord={}
    n=len(graph.nodes)
    for i in range(0,n):
        G.xCoord[G.vertices[i]]=graph.nodes[i].xsch*float(900/(n-1))+50
        G.yCoord[G.vertices[i]]=1000-(graph.nodes[i].ysch*float(900/(n-1))+50)
    return 1
    #-------------------------------------------------------------------------
    
    #=============================================================================#
