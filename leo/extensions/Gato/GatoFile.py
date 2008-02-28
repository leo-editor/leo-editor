#!/usr/bin/env python2.3
################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#
#	file:   GatoFile.py
#	author: Achim Gaedke (achim.gaedke@zpr.uni-koeln.de)
#
#       Copyright (C) 1998-2005, Alexander Schliep, Winfried Hochstaettler and 
#       Copyright 1998-2001 ZAIK/ZPR, Universitaet zu Koeln
#                                   
#       Contact: schliep@molgen.mpg.de, wh@zpr.uni-koeln.de             
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
#       This file is version $Revision: 1.1 $ 
#                       from $Date: 2007/10/04 14:36:39 $
#             last change by $Author: edream $.
#
################################################################################
import sys
import os
import types
import codecs
import StringIO
import urllib2
import xml.dom.minidom
import Gato
import Graph
import GraphUtil
import Tkinter
import TreeWidget
import TextTreeWidget
import ScrolledText

# code handling:
# the data object model module is unicode
# xml*Element functions return iso-8859-1 strings
# tkinter does not like python unicode, it gets iso-8859-1 strings
# file data are encoded to iso-8859-1

# xmlDecode(unicode) returns iso char string
(_isoEncoder,_isoDecoder,_isoStreamReader,_isoStreamWriter)=codecs.lookup("iso-8859-1")
xmlDecode=lambda x:_isoEncoder(x)[0]
# xmlEnocde(iso_char_string) returns unicode
xmlEncode=lambda x:_isoDecoder(x)[0]
# object that encodes stream data from unicode to iso-8859-1
xmlEncodedStream=_isoStreamWriter

class FileException(Exception):
    """
    is the subclass for all file and xml related things that can go wrong in this module
    """
    def __init__(self, reason):
        """
        takes the reason or explanation as argument
        """
        self.reason=reason
        
class GatoStorageCache:
    """
    singleton list for all accessed/used/cached storage locations
    """
    pass
    
class GatoStorageLocation:
    """
    bundle of common functions for file load/save/selection
    These functions act on the level of graphs and algorithms.
    they propagate the open and save calls to the different file implementations
    """
    
    def __init__(self,fileName=None):
        """
        opens the file and prepares the access
        """
        self.fileName=fileName
        
    def chooseLocation(self,accessMode="rw"):
        """
        opens a suitable dialog to choose a possible location for reading/writing gato data
        """
        
    def __repr__(self):
        """
        a short representation of the instance
        """
        return "<%s: %s>"%(self.__class__.__name__,self.fileName)
        
    def __str__(self):
        """
        should display the name in human understandable manner
        """
        return self.fileName
        
    def readGraph(self,whichGraph=None):
        """
        returns a Graph object
        """
        pass
        
    def readAlgortihm(self, whichAlgorithm=None):
        """
        returns an Algorithm object
        """
        pass
        
    def writeGraph(self, Graph, whichGraph=None):
        """
        puts a graph to the collection of graphs
        """
        pass
        
    def writeAlgorithm(self, Algorithm, whichAlgorithm=None):
        """
        puts a graph to the collection of algorithms
        """
        pass
        
class GatoStorageLocationTest:
    """
    some tests for GatoStorageLocation
    """
    def __init__(self):
        l=GatoStorageLocation("bla")
        print "human readable: %s, python representation %s"%(l,repr(l))
        
        
class GatoDirBranch(TreeWidget.DirBranch):
    """
    """
    def updateChildList(self):
        """
        create/update child list suitable for gato
        """
        oldChildren=self.children
        self.children=[]
        entries=[]
        try:
            entries=os.listdir(self.path)
        except OSError:
            pass
        entries.sort()
        oldEntries=map(lambda c:c.name,oldChildren)
        for entry in entries:
            if entry in oldEntries:
                self.children.append(oldChildren[oldEntries.index(entry)])
            else:
                entrypath=os.path.join(self.path,entry)
                if os.path.isdir(entrypath):
                    self.children.append(GatoDirBranch(parent=self,name=entry))
                elif os.path.isfile(entrypath):
                    # select suitable leaf
                    if entry[-5:]==".gato":
                        self.children.append(GatoFileBranch(parent=self,name=entry))
                    elif entry[-4:]==".xml":
                        self.children.append(xmlGatoFileBranch(parent=self,name=entry))
                    elif entry[-4:]==".alg" and os.path.isfile(entrypath[:-4]+".pro"):
                        self.children.append(algLeaf(parent=self,name=entry))
                    elif entry[-4:]==".cat":
                        self.children.append(catLeaf(parent=self,name=entry))
                        
class GatoFileBranch(TreeWidget.xmlFileBranch):
    """
    ToDo: supports xml files with gato root section
    """
    pass
    
class xmlGatoFileBranch(TreeWidget.xmlFileBranch):
    """
    ToDo supports xml files with gato sections inside
    """
    pass
    
class algLeaf(TreeWidget.Leaf):
    """
    old algortithm file
    """
    def __init__(self,parent=None,name=None):
        TreeWidget.Leaf.__init__(self,parent=parent, name=name)
        self.selectable=1
        
class catLeaf(TreeWidget.Leaf):
    """
    old graph file
    """
    def __init__(self,parent=None,name=None):
        TreeWidget.Leaf.__init__(self,parent=parent, name=name)
        self.selectable=1
        
class GatoTree(TreeWidget.scrolledTree):
    """
    """
    def __init__(self,master):
        TreeWidget.scrolledTree.__init__(self,master)
        self.root=GatoDirBranch(parent=self,name="/",anchor=(1,1))
        self.root.display()
        # show current work directory
        current=os.getcwd()
        currentList=[]
        while current!=self.root.name:
            (current,piece)=os.path.split(current)
            currentList.insert(0,piece)
            # expand all branches on the way
        thisNode=self.root
        thisNode.expand()
        for piece in currentList:
            thisNode=filter(lambda x:x.name==piece,thisNode.children)[0]
            thisNode.expand()
            
        (Nx0,Ny0,Nx1,Ny1)=thisNode.getBoundingBox()
        (Cx0,Cy0,Cx1,Cy1)=self.bbox(Tkinter.ALL)
        self.yview(Tkinter.MOVETO,float(Ny0)/float(Cy1-Cy0))
        
        
class WorkInProgress(Tkinter.Tk):
    """
    my development and test class
    """
    
    def __init__(self):
        Tkinter.Tk.__init__(self)
        self.tree=GatoTree(self)
        self.tree.pack(expand=1,fill=Tkinter.BOTH)
        
    def run(self):
        self.mainloop()
        
        
class xmlAlgorithmElement:

    algorithmElementName="algorithm"
    sourceElementName="text"
    prologElementName="prolog"
    aboutElementName="about"
    
    def __init__(self,dom):
        # test for right tag
        if dom.tagName!=self.algorithmElementName:
            raise FileException("Wrong element name: %s, %s expected"
                                %(dom.tagName,self.algorithmElementName))
        self.domElement=dom
        
    def setAlgorithmFromALGFile(self,fileName):
        """
        writes algorithm data to xml sections
        """
        algorithm=Gato.Algorithm()
        algorithm.Open(fileName)
        self.setAlgorithm(algorithm.source)
        self.setAbout(algorithm.About())
        PrologFileName=fileName[:-4]+'.pro'
        if os.access(PrologFileName,os.R_OK):
            self.setProlog(file(PrologFileName).read())
        else:
            print "Warning: could not read prolog file %s"%PrologFileName
            
    def setProlog(self,text):
        """
        creates/repaces the prolog section
        """
        #create new one
        newProlog=None
        if self.domElement.ownerDocument:
            newProlog=self.domElement.ownerDocument.createElement(self.prologElementName)
            newProlog.appendChild(self.domElement.ownerDocument.createCDATASection(
                xmlEncode(text)
                ))
        else:
            newProlog=xml.dom.Element(self.prologElementName)
            newProlog.appendChild(xml.dom.CDATASection(xmlEncode(text)))
        existingProlog=self.domElement.getElementsByTagName(self.prologElementName)
        if len(existingProlog)>0:
            # replace existing prolog
            self.domElement.repaceChild(newProlog,existingProlog[0])
        else:
            self.domElement.appendChild(newProlog)
            
    def setAlgorithm(self,text):
        """
        creates/repaces the algorithm section
        """
        #create new one
        newAlgorithm=None
        if self.domElement.ownerDocument:
            newAlgorithm=self.domElement.ownerDocument.createElement(self.sourceElementName)
            newAlgorithm.appendChild(self.domElement.ownerDocument.createCDATASection(
                xmlEncode(text)
                ))
        else:
            newAlgorithm=xml.dom.Element(self.sourceElementName)
            newAlgorithm.appendChild(xml.dom.CDATASection(xmlEncode(text)))
        existingAlgorithm=self.domElement.getElementsByTagName(self.sourceElementName)
        if len(existingAlgorithm)>0:
            # replace existing algorithm
            self.domElement.repaceChild(newAlgorithm,existingAlgorithm[0])
        else:
            self.domElement.appendChild(newAlgorithm)
            
    def setAbout(self,text):
        """
        ToDo
        """
        pass
        
    def getTextFromElement(self,tagName):
        "returns the text of specified tag"
        requestedElements=self.domElement.getElementsByTagName(tagName)
        if len(requestedElements)!=1:
            return None
        requestedElement=requestedElements[0]
        text=""
        for e in requestedElement.childNodes:
            if (e.nodeType==xml.dom.minidom.Node.TEXT_NODE or
                e.nodeType==xml.dom.minidom.Node.CDATA_SECTION_NODE):
                text+=e.data
        return xmlDecode(text)
        
    def getText(self):
        t=self.getTextFromElement(self.sourceElementName)
        if t:
            return t
        else:
            return ""
            
    def getAboutAsString(self):
        requestedElements=filter(lambda e:e.nodeType==xml.dom.Node.ELEMENT_NODE and \
                                 e.tagName==self.aboutElementName,
                                 self.domElement.childNodes)
        if len(requestedElements)<1:
            return None
        else:
            return requestedElements[0].toxml()
            
    def getTextAsFile(self):
        """
        creates a StringIO Object from file
        """
        return StringIO.StringIO(self.getText())
        
    def getProlog(self):
        "returns the prolog"
        p=self.getTextFromElement(self.prologElementName)
        if p:
            return p
        else:
            return ""
            
    def getPrologAsFile(self):
        return StringIO.StringIO(self.getProlog())
        
    def getName(self):
        return xmlDecode(self.domElement.getAttribute("name"))
        
    def setName(self,name):
        self.domElement.setAttribute("name",xmlEncode(name))
        
class xmlGraphElement:

    graphElementName="graph"
    
    def __init__(self,graph,name=None):
        """
        called with a dom element: grants access to Graph
        called with a graph and a name string: creates the dom structure from graph
        """
        # test for right tag
        if issubclass(graph.__class__,xml.dom.minidom.Element):
            # we were called with a dom element as argument
            if graph.tagName!=self.graphElementName:
                raise FileException("Wrong element name: %s, %s expected"
                                    %(graph.tagName,self.graphElementName))
            self.domElement=graph
        elif issubclass(graph.__class__,Graph.Graph) and type(name) in types.StringTypes:
            # initialise dom element
            self.domElement=xml.dom.minidom.Element(xmlGraphElement.graphElementName)
            self.setName(name)
            self.setGraph(graph)
        else:
            raise FileException("wrong arguments provided")
            
    def getAboutAsString(self):
        requestedElements=filter(lambda e:e.nodeType==xml.dom.Node.ELEMENT_NODE and e.tagName=="about",
                                 self.domElement.childNodes)
        if len(requestedElements)<1:
            return None
        else:
            return requestedElements[0].toxml()
            
    def getGraph(self):
        """
        returns the Graph object constructed  from this dom element
        """
        return GraphUtil.OpenCATBoxGraph(self.getGraphAsStringIO())
        
    def getGraphAsStringIO(self):
        text=StringIO.StringIO()
        for e in self.domElement.childNodes:
            if (e.nodeType==xml.dom.minidom.Node.TEXT_NODE or
                e.nodeType==xml.dom.minidom.Node.CDATA_SECTION_NODE):
                text.write(xmlDecode(e.data))
        text.seek(0)
        return text
        
    def setGraph(self,graph):
        # we were called with a Graph and a name as arguments
        data=StringIO.StringIO()
        GraphUtil.SaveCATBoxGraph(graph,data)
        #remove all other text nodes
        textNodes=filter(lambda e:e.nodeType==xml.dom.minidom.Node.TEXT_NODE or
                         e.nodeType==xml.dom.minidom.Node.CDATA_SECTION_NODE,
                         self.domElement.childNodes)
        map(self.domElement.removeChild,textNodes)
        # create necessary dom elements
        # maybe xml.dom.minidom.Text is ok, too
        newCDATASection=None
        if self.domElement.ownerDocument:
            newCDATASection=self.domElement.ownerDocument.createCDATASection(
                xmlEncode(data.getvalue())
                )
        else:
            newCDATASection=xml.dom.minidom.CDATASection(xmlEncode(data.getvalue()))
        self.domElement.appendChild(newCDATASection)
        
    def setGraphFromCATFile(self,GraphFile):
        """
        creates a graph object from .cat file and sets it
        this detour assures an actual graph format
        """
        self.setGraph(GraphUtil.OpenCATBoxGraph(GraphFile))
        
    def getName(self):
        return xmlDecode(self.domElement.getAttribute("name"))
        
    def setName(self,name):
        self.domElement.setAttribute("name",xmlEncode(name))
        
class xmlGatoElement:
    """
    is an access and modification interface to the gato dom structure 
    """
    
    gatoElementName="gato"
    
    def __init__(self,_domElement):
        """
        creates the access and modification interface
        """
        # test for right tag
        if _domElement.tagName!=self.gatoElementName:
            raise FileException("Wrong element name: %s, %s expected"
                            %(_domElement.tagName,self.gatoElementName))
        self.domElement=_domElement
        
    def createGraphElement(self,name=None):
        """
        creates a new graph Element
        """
        newDOMElement=None
        if self.domElement.ownerDocument:
            newDOMElement=self.domElement.ownerDocument.createElement(
                xmlGraphElement.graphElementName)
        else:
            newDOMElement=xml.dom.Element(xmlGraphElement.graphElementName)
        newElement=xmlGraphElement(newDOMElement)
        if name is not None:
            newElement.setName(name)
        return newElement
        
    def createAlgorithmElement(self,name=None):
        """
        creates a new algorithm element
        """
        newDOMElement=None
        if self.domElement.ownerDocument:
            newDOMElement=self.domElement.ownerDocument.createElement(
                xmlAlgorithmElement.algorithmElementName)
        else:
            newDOMElement=xml.dom.Element(xmlAlgorithmElement.algorithmElementName)
        newElement=xmlAlgorithmElement(newDOMElement)
        if name is not None:
            newElement.setName(name)
        return newElement
        
    def setName(self,name):
        """
        sets the name attribute for this element
        """
        self.domElement.setAttribute("name",xmlEncode(name))
        
    def getName(self,name):
        """
        gets the name of this element, if unset an empty string
        """
        return xmlDecode(self.domElement.getAttribute("name"))
        
    def getAboutAsString(self):
        requestedElements=filter(lambda e:e.nodeType==xml.dom.Node.ELEMENT_NODE and e.tagName=="about",
                                 self.domElement.childNodes)
        if len(requestedElements)<1:
            return None
        else:
            return requestedElements[0].toxml()
            
    def getGraphElements(self):
        """
        returns all direct child elements with graph's tagName
        """
        return filter(lambda x:(x.nodeType==xml.dom.minidom.Node.ELEMENT_NODE and
                                x.tagName==xmlGraphElement.graphElementName),
                      self.domElement.childNodes)
        
    def getAlgorithmElements(self):
        """
        returns all direct child elements with algorithm's tagName
        """
        return filter(lambda x:(x.nodeType==xml.dom.minidom.Node.ELEMENT_NODE and
                                x.tagName==xmlAlgorithmElement.algorithmElementName),
                      self.domElement.childNodes)
        
    def getGraphNames(self):
        """
        extracts all graph names
        """
        # return a list of name attribute values from graph elements
        return map(lambda x:xmlDecode(x.getAttribute("name")),
                   self.getGraphElements())
        
    def getAlgorithmNames(self):
        """
        extracts all algorithm names
        """
        # return a list of name attribute values from graph elements
        return map(lambda x:xmlDecode(x.getAttribute("name")),
                   self.getAlgorithmElements())
        
    def getGraphByName(self,name):
        """
        gets a xmlGraphElement by its name
        """
        graphs=filter(lambda x:x.getAttribute("name")==name,
                      self.getGraphElements())
        return xmlGraphElement(graphs[0])
        
    def getAlgorithmByName(self,name):
        """
        gets a xmlAlgorithmElement by its name
        """
        graphs=filter(lambda x:x.getAttribute("name")==name,
                      self.getAlgorithmElements())
        return xmlAlgorithmElement(graphs[0])
        
    def getDefaultSelection(self):
        """
        searches for the default selection, e.g.
        only one graph and one algorithm
        """
        defaultSelection={}
        graphs=self.getGraphNames()
        algorithms=self.getAlgorithmNames()
        if len(graphs)<2 and len(algorithms)<2:
            if len(graphs)==1:
                defaultSelection["graph"]=self.getGraphByName(graphs[0])
            if len(algorithms)==1:
                defaultSelection["algorithm"]=self.getAlgorithmByName(algorithms[0])
            return defaultSelection
            
        if self.domElement.hasAttribute("defaultGraph"):
            defaultSelection["graph"]=self.getGraphByName(
                self.domElement.getAttribute("defaultGraph"))
            
        if self.domElement.hasAttribute("defaultAlgorithm"):
            defaultSelection["algorithm"]=self.getAlgorithmByName(
                self.domElement.getAttribute("defaultAlgorithm"))
            
        return defaultSelection
        
    def updateGraphByName(self,graph,name=None):
        """
        appends or replaces a graph, if name not given, the graphs name is taken
        """
        newGraph=None
        newName=None
        if issubclass(graph.__class__,Graph.Graph):
            newGraph=xmlGraphElement(graph,name)
        elif issubclass(graph.__class__,xmlGraphElement):
            newGraph=graph
            if name:
                graph.setName(name)
            else:
                name=graph.getName()
        else:
            raise FileException("argument mismatch!")
            
        graphs=filter(lambda x:x.getAttribute("name")==name,
                      self.getGraphElements())
        if len(graphs):
            # replace graph, more exactly the first one
            self.domElement.replaceChild(newGraph.domElement,graphs[0])
        else:
            # append graph
            self.domElement.appendChild(newGraph.domElement)
            
    def updateAlgorithmByName(self,algorithm,name=None):
        """
        appends or replaces an algorithm
        """
        newAlgorithm=None
        newName=None
        if issubclass(algorithm.__class__,Gato.Algorithm):
            newAlgorithm=xmlAlgorithmElement(algorithm,name)
        elif issubclass(algorithm.__class__,xmlAlgorithmElement):
            newAlgorithm=algorithm
            if name:
                algorithm.setName(name)
            else:
                name=algorithm.getName()
        else:
            raise FileException("argument mismatch!")
            
        algorithms=filter(lambda x:x.getAttribute("name")==name,
                          self.getAlgorithmElements())
        if len(algorithms):
            # replace graph, more exactly the first one
            self.domElement.replaceChild(newAlgorithm.domElement,graphs[0])
        else:
            # append graph
            self.domElement.appendChild(newAlgorithm.domElement)
            
    def removeGraphByName(self,name):
        """
        removes the named graph
        """
        graphs=filter(lambda x:x.getAttribute("name")==name,
                      self.getGraphElements())
        map(self.domElement.removeChild,graphs)
        
    def removeAlgorithmByName(self,name):
        """
        removes the named algorithm
        """
        algorithms=filter(lambda x:x.getAttribute("name")==name,
                          self.getAlgorithmElements())
        map(self.domElement.removeChild,algorithms)
        
class ElementDisplay(Tkinter.Frame):
    """
    displays the selected element
    """
    def __init__(self,master,**config):
        """
        """
        config.update({"width":500, "height":500})
        Tkinter.Frame.__init__(self,master,bg="white",cnf=config)
        self.pack_propagate(0) # keep everything in a rigid frame
        self.displayedWidget=None
        self.displayedNode=None
        
    def clearDisplay(self):
        """
        cleanup and display nothing
        """
        # cleanup radically
        for child in self.children.values():
            child.pack_forget()
            child.destroy()
        self.displayedNode=None
        
    def setDisplay(self,node):
        """
        display node...
        """
        if node is None:
            self.clearDisplay()
            return
        else:
            if self.displayedNode is not None and self.displayedNode==node:
                return #nothing to do
        self.clearDisplay()
        displayedWidget=None
        if node.tagName==xmlGraphElement.graphElementName:
            html_data=xmlGraphElement(node).getAboutAsString()
            displayedWidget=AboutWidget(self,html_data)
            self.displayedNode=node
        elif node.tagName==xmlAlgorithmElement.algorithmElementName:
            displayedWidget=AlgorithmInfoWidget(self,xmlAlgorithmElement(node))
            self.displayedNode=node
        elif node.tagName==xmlGatoElement.gatoElementName:
            html_data=xmlGatoElement(node).getAboutAsString()
            displayedWidget=AboutWidget(self,html_data)
            self.displayedNode=node
        else:
            print "toDo: ",node
            
        if displayedWidget:
            displayedWidget.pack(expand=1,fill=Tkinter.BOTH)
            
            
class AlgorithmInfoWidget(Tkinter.Frame):
    """
    creates an algorithm widget
    """
    
    def __init__(self,master,algorithmElement):
        """
        create it
        """
        Tkinter.Frame.__init__(self,master,highlightthickness=0)
        html_data=algorithmElement.getAboutAsString()
        self.About=AboutWidget(self,html_data)
        self.About.pack(side=Tkinter.TOP,expand=1,fill=Tkinter.BOTH)
        text_data=algorithmElement.getText()
        self.Text=ScrolledText.ScrolledText(self,
                                            background='white', 
                                            wrap='word',
                                            font="Times 10")
        self.Text.insert(Tkinter.END, text_data)
        self.Text.pack(side=Tkinter.TOP,expand=1,fill=Tkinter.BOTH)
        self.Text['state'] = Tkinter.DISABLED 
        
class AboutWidget(ScrolledText.ScrolledText):
    """
    displays html text
    copied and modified from GatoDialogs.py
    Basic class which provides a scrollable area for viewing HTML text
    """
    
    def __init__(self, master, htmlcode):
        ScrolledText.ScrolledText.__init__(self, master,
                                           background='white', 
                                           wrap='word',
                                           font="Times 10",
                                           )
        self.inserthtml(htmlcode)
        
    def Update(self,htmlcode):
        self.inserthtml(htmlcode)
        
    def inserthtml(self, htmlcode):
        if htmlcode is None:
            htmlcode="""<html><body>
            No information avaliable !
            </body></html>
            """
        import formatter
        import GatoDialogs
        self['state'] = Tkinter.NORMAL
        self.delete('0.0', Tkinter.END)
        
        writer = GatoDialogs.HTMLWriter(self, self)
        format = formatter.AbstractFormatter(writer)
        parser = GatoDialogs.MyHTMLParser(format, self)
        parser.feed(htmlcode)
        parser.close()
        
        self['state'] = Tkinter.DISABLED
        
class GatoFileButtonBar(Tkinter.Frame):
    """
    holds the buttons for the node selection dialog
    """
    def __init__(self, master, reporter, cnf={}, **config):
    
        cnf.update(config)
        Tkinter.Frame.__init__(self,master,cnf=cnf)
        self.reporter=reporter
        self.okButton=Tkinter.Button(self,text="Ok",command=lambda e=None :self.reporter("quit"))
        self.okButton.grid(row=0,column=0,sticky=Tkinter.E+Tkinter.W)
        self.cancelButton=Tkinter.Button(self,text="Cancel",command=lambda e=None:self.reporter("cancel"))
        self.cancelButton.grid(row=0,column=1,sticky=Tkinter.E+Tkinter.W)
        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)
        
        
class GatoFileStructureWidget(TextTreeWidget.dom_structure_widget):
    """
    customized for .gato files
    """
    
    def __init__(self,master,dom,report_function,**conf):
        """
        report function coordinates the element display
        """
        TextTreeWidget.dom_structure_widget.__init__(self,master,dom,self.report_func,width=30,cnf=conf)
        self.chosenNodes={}
        self.report_to=report_function
        
    def report_func(self,event,*opts):
        """
        reports nodes that are marked aka chosen
        """
        if event=="chosenNode":
            # double click on node, or hit <Return>
            if len(opts)<1 or opts[0] is None:
                return
            node=opts[0]
            # is this a gato element?
            if node.tagName==xmlGatoElement.gatoElementName:
                if self.report_to and not self.report_to(event,node):
                    return
                self.chosenNode(node,xmlGatoElement.gatoElementName)
                # is it a valid graph or algorithm object?
            if self.isGatoMemberElement(node)!=1:
                # nothing to do...
                return
            if node.tagName==xmlAlgorithmElement.algorithmElementName:
                if self.report_to and not self.report_to(event,node):
                    return
                self.chosenNode(node,xmlAlgorithmElement.algorithmElementName)
            elif node.tagName==xmlGraphElement.graphElementName:
                if self.report_to and not self.report_to(event,node):
                    return
                self.chosenNode(node,xmlGraphElement.graphElementName)
        elif event=="selectedNode":
            # selected Node
            if len(opts)<1 or opts[0] is None:
                return
            node=opts[0]
            if self.report_to:
                self.report_to(event, node)
        else:
            print event, opts
            
    def chosenNode(self,node,register):
        """
        mark and save chosen node
        """
        last=self.chosenNodes.get(register)
        if last:
            self.setNodeColor(last,"black")
        if last==node:
            # erase selection
            self.chosenNodes[register]=None
        else:
            # new selection
            self.chosenNodes[register]=node
            self.setNodeColor(node,"red")
            
    def nameNode(self,node):
        """
        chose proper names for node
        """
        if node.nodeType==xml.dom.Node.ELEMENT_NODE:
            myName=xmlDecode(node.tagName)
            if myName==xmlGatoElement.gatoElementName:
                if node.hasAttribute("name"):
                    return "gato: %s"%xmlDecode(node.getAttribute("name"))
                else:
                    return "gato"
            elif myName==xmlGraphElement.graphElementName:
                return "graph: %s"%xmlDecode(node.getAttribute("name"))
            elif myName==xmlAlgorithmElement.algorithmElementName:
                return "algorithm: %s"%xmlDecode(node.getAttribute("name"))
            else:
                return TextTreeWidget.dom_structure_widget.nameNode(self,node)
        else:
            return TextTreeWidget.dom_structure_widget.nameNode(self,node)
            
    def isGatoMemberElement(self,node):
        """
        if this is a subtag of gato, return actual depth
        returns 0, if not in a gato element, or is a gato element itself
        """
        parent=node.parentNode
        if parent:
            if parent.nodeType==xml.dom.Node.DOCUMENT_NODE:
                return 0
            elif parent.nodeType==xml.dom.Node.ELEMENT_NODE and parent.tagName=="gato":
                return 1
            else:
                depth=self.isGatoMemberElement(parent)
                if depth:
                    return depth+1
                else:
                    return 0
        else:
            raise FileException("could not determine, if node is member of gato section")
            
    def isVisible(self,node):
        """
        filter out subsections of graph and algorithm in gato sections
        """
        isMember=self.isGatoMemberElement(node)
        if isMember==0:
            return TextTreeWidget.dom_structure_widget.isVisible(self,node)
        elif isMember>1:
            # hide everything deeper than 1
            return 0
        else:
            # hide everything except graph and algorithm
            if (node.nodeType==xml.dom.Node.ELEMENT_NODE and
                node.tagName in [xmlGraphElement.graphElementName,
                                 xmlAlgorithmElement.algorithmElementName]):
                return 1
            else:
                return 0
                
class GatoDOMDialog(Tkinter.Toplevel):
    """
    contains the xml structure and the display of selected element and some buttons
    opt_choose contains the elements, that may be chosen
    mand_choose contains the elements, that must be choosen
    """
    def __init__(self, master, dom, opt_choose=("algorithm","graph"), mand_choose=(), **config):
        """
        create it
        """
        self.dom=dom
        self.opt_choose=opt_choose
        self.mand_choose=mand_choose
        self.result={} # None in case of canceled dialog, (graphNode, algoNode) in case of selection
        Tkinter.Toplevel.__init__(self,master, cnf=config)
        # the structure widget...
        self.struct_widget=GatoFileStructureWidget(self, self.dom, self.reportFromStructure, font="Times 12")
        self.struct_widget.grid(row=0, column=0, sticky=Tkinter.NSEW)
        # and the element display....
        self.display_widget=ElementDisplay(self,width=400)
        self.display_widget.grid(row=0, column=1, sticky=Tkinter.NSEW)
        # the button bar...
        self.buttons=GatoFileButtonBar(self,self.reportFromButtons)
        self.buttons.grid(row=1, column=0, columnspan=2, sticky=Tkinter.EW)
        self.protocol("WM_DELETE_WINDOW", lambda e=None: self.reportFromButtons("cancel"))
        
    def reportFromStructure(self,event,node):
        """
        coordinates element display
        """
        if event=="selectedNode":
            self.display_widget.setDisplay(node)
        elif event=="chosenNode":
            # should be selected?
            if node and node.nodeType==xml.dom.Node.ELEMENT_NODE and \
               (node.tagName in self.opt_choose or node.tagName in self.mand_choose):
                return 1
                
    def reportFromButtons(self,event):
        """
        gets interesting events from button bar
        """
        if event=="quit":
            # graph
            graph=self.struct_widget.chosenNodes.get(xmlGraphElement.graphElementName)
            if graph:
                self.result[xmlGraphElement.graphElementName]=xmlGraphElement(graph)
            else:
                if xmlGraphElement.graphElementName in self.mand_choose:
                    return
                    # algorithm
            algorithm=self.struct_widget.chosenNodes.get(xmlAlgorithmElement.algorithmElementName)
            if algorithm:
                self.result[xmlAlgorithmElement.algorithmElementName]=xmlAlgorithmElement(algorithm)
            else:
                if xmlAlgorithmElement.algorithmElementName in self.mand_choose:
                    return
                    # gato section
            gato=self.struct_widget.chosenNodes.get(xmlGatoElement.gatoElementName)
            if gato:
                self.result[xmlGatoElement.gatoElementName]=xmlGatoElement(gato)
            else:
                if xmlGatoElement.gatoElementName in self.mand_choose:
                    return
            self.destroy()
            self.quit()
        elif event=="cancel":
            self.result=None
            self.destroy()
            self.quit()
        else:
            raise Exception("unknown event %s"%event)
            
    def run(self):
        """
        runs this dialog
        """
        self.mainloop()
        return self.result
        
class GatoFile:
    """
    encapsulates the dom creation from file
    """
    
    validModes=['r', # expect valid gato file and read this file
                'w', # create new file or overwrite existing file
                ]
    
    def __init__(self,myFile=None, mode='r'):
        """
        open a file and read the dom from it, or provide an empty gato document
        """
        if myFile:
            if mode not in self.validModes:
                raise FileException("mode %c not supported"%mode)
            self.mode=mode
            import types
            
            # test if name or file is given
            if self.mode=='r':
                self.file=None
                self.name=None
                if type(myFile) in types.StringTypes:
                    if os.access(myFile,os.R_OK):
                        self.file=file(myFile,"r")
                        self.name=myFile
                    else:
                        urlRequest=urllib2.Request(myFile)
                        self.file=urllib2.urlopen(urlRequest,"r")
                elif type(myFile)==types.FileType:
                    self.file=myFile
                    
                try:
                    # pull dom out of file
                    self.dom = xml.dom.minidom.parse(self.file)
                except xml.dom.DOMException, e:
                    print e
                    raise FileException(str(e))
                    
            elif self.mode=='w':
                if type(myFile) in types.StringTypes:
                    if os.access(myFile,os.W_OK):
                        self.file=file(myFile,"w")
                        self.name=myFile
                    else:
                        urlRequest=urllib2.Request(myFile)
                        self.file=urllib2.urlopen(urlRequest,"w")
                else:
                    self.file=myFile
                    
                    # create empty document
                self.dom = xml.dom.minidom.Document()
                
        else: #myFile=None
            # without file, but create empty doc, too
            self.dom = xml.dom.minidom.Document()
            # self.dom.appendChild(self.dom.createElement(xmlGatoElement.gatoElementName))
            
    def write(self,_file=None):
        """
        writes the (modified) dom to the file
        """
        # ???? write to right place????
        _thisFile=None
        if _file is not None:
            if type(_file) in types.StringTypes:
                _thisFile=encodedStream(file(_file,"w"))
            elif type(_file)==types.FileType:
                _thisFile=_file
        else:
            _thisFile=self.file
            
        encoding="iso-8859-1"
        _thisFile.write("<?xml version=\"1.0\" encoding=\"%s\" ?>\n"%encoding)
        if self.dom.hasChildNodes():
            for n in self.dom.childNodes:
                n.writexml(xmlEncodedStream(_thisFile))
                
    def getDefaultSelection(self):
        """
        returns the default selected elements
        """
        if (not self.dom.documentElement) or \
               self.dom.documentElement.tagName!=xmlGatoElement.gatoElementName:
            return None
        else:
            return xmlGatoElement(self.dom.documentElement).getDefaultSelection()
            
    def getGatoElements(self):
        """
        returns an xmlGatoElement instance
        """
        return self.dom.getElementsByTagName(xmlGatoElement.gatoElementName)
        
    def appendGatoElement(self,newElement):
        """
        append the element without checking unique name
        """
        if self.dom.hasChildNodes():
            # replace doc root gato node with a more general section
            if self.dom.documentElement.tagName==xmlGatoElement.gatoElementName:
                tmpGatoElement=self.dom.documentElement
                self.dom.replaceChild(self.dom.createElement("xml"),tmpGatoElement)
                self.dom.documentElement.appendChild(tmpGatoElement)
                # append to document element
            self.dom.documentElement.appendChild(newElement.domElement)
        else:
            # start with a gato node as root element
            self.dom.appendChild(newElement.domElement)
            
    def createGatoElement(self,name=None):
        """
        creates a new (opt. unnamed)  Gato element
        """
        newElement=xmlGatoElement(self.dom.createElement(xmlGatoElement.gatoElementName))
        if name is not None:
            newElement.setName(name)
        return newElement
        
    def displaySelectionDialog(self,master):
        """
        runs the dom structure
        """
        w=GatoDOMDialog(master,self.dom)
        return w.run()
        
    def displayGraphSelectionDialog(self,master):
        w=GatoDOMDialog(master,self.dom,to_choose=(('graph',)))
        s=w.run()
        if s:
            return s["graph"]
        else:
            return None
            
    def displayAlgorithmSelectionDialog(self,master):
        w=GatoDOMDialog(master, self.dom,to_choose=(('algorithm',)))
        s=w.run()
        if s:
            return s["algorithm"]
        else:
            return None
            
if __name__=='__main__':
    # some test progs
    WorkInProgress().run()
    
    # old ones
    # f=GatoFile('DFS.gato') # parse an XML file by name
    # f.displayGraphSelectionDialog(Tkinter.Tk())
    
    
