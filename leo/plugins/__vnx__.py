#@+leo-ver=4-thin
#@+node:ekr.20050915064008:@thin __vnx__.py
'''A plugin to piggyback vnx's (vnode gnx's) in t.uA's

This will move into Leo's core in Leo 4.4.
'''

#@<< imports >>
#@+node:ekr.20050915064008.1:<< imports >>
import leoGlobals as g

import leoFileCommands
# import leoNodes
import leoPlugins
#@nonl
#@-node:ekr.20050915064008.1:<< imports >>
#@nl

__version__ = '0.0.1'

#@+others
#@+node:ekr.20050915064008.2:init
def init ():
    
    # Not ok for unit testing yet.
    return not g.app.unitTesting
#@nonl
#@-node:ekr.20050915064008.2:init
#@+node:ekr.20050915084416:reference code
if 0:
    #@    @+others
    #@+node:ekr.20050915084416.1:to do
    #@@nocolor
    #@+at
    # 
    # Q: Shouldn't we just bite the bullet and change the file format.
    #     - Use DOM
    #     - write "vx" attributes in vnodes.
    # A: We could do this, but writing vnx attributes in 
    # descendentUnknownAttribute field is not painful.
    # 
    # - (done) assign gnx to all vnodes. (done)
    # - (done) create new helper method for getLeoFile:  
    # restoreDescendantAttributes
    #@-at
    #@nonl
    #@-node:ekr.20050915084416.1:to do
    #@+node:ekr.20050915084416.2:from leoFileCommands
    #@+node:ekr.20050915084416.3:reading
    #@+node:ekr.20050915090544:getLeoFile & helper
    # The caller should enclose this in begin/endUpdate.
    
    def getLeoFile (self,fileName,readAtFileNodesFlag=True,silent=False):
    
        c = self.c
        c.setChanged(False) # 10/1/03: May be set when reading @file nodes.
        #@    << warn on read-only files >>
        #@+node:ekr.20050915090544.1:<< warn on read-only files >>
        # os.access may not exist on all platforms.
        
        try:
            self.read_only = not os.access(fileName,os.W_OK)
        except AttributeError:
            self.read_only = False
        except UnicodeError:
            self.read_only = False
                
        if self.read_only:
            g.es("read only: " + fileName,color="red")
        #@nonl
        #@-node:ekr.20050915090544.1:<< warn on read-only files >>
        #@nl
        self.mFileName = c.mFileName
        self.tnodesDict = {}
        self.descendentExpandedList = []
        self.descendentMarksList = []
        self.descendentUnknownAttributesDictList = []
        ok = True
        c.loading = True # disable c.changed
        try:
            #@        << scan all the xml elements >>
            #@+node:ekr.20050915090544.2:<< scan all the xml elements >>
            self.getXmlVersionTag()
            self.getXmlStylesheetTag()
            
            self.getTag("<leo_file>") # Must match exactly.
            self.getLeoHeader()
            self.getGlobals()
            self.getPrefs()
            self.getFindPanelSettings()
            
            # Causes window to appear.
            c.frame.resizePanesToRatio(c.frame.ratio,c.frame.secondary_ratio)
            if not silent:
                g.es("reading: " + fileName)
            
            self.getVnodes()
            self.getTnodes()
            self.getCloneWindows()
            self.getTag("</leo_file>")
            #@nonl
            #@-node:ekr.20050915090544.2:<< scan all the xml elements >>
            #@nl
        except BadLeoFile, message:
            if not silent:
                #@            << raise an alert >>
                #@+node:ekr.20050915090544.3:<< raise an alert >>
                # All other exceptions are Leo bugs.
                
                g.es_exception()
                g.alert(self.mFileName + " is not a valid Leo file: " + str(message))
                #@nonl
                #@-node:ekr.20050915090544.3:<< raise an alert >>
                #@nl
            ok = False
        c.frame.tree.redraw_now(scroll=False)
        # g.trace(readAtFileNodesFlag,c.mFileName)
        if ok and readAtFileNodesFlag:
            c.atFileCommands.readAll(c.rootVnode(),partialFlag=False)
        # g.trace(c.currentPosition())
        
        # New in 4.3.1: do this after reading derived files.
        if not self.usingClipboard:
            #@        << set current and top positions >>
            #@+node:ekr.20050915090544.5:<< set current and top positions >>
            current = self.convertStackToPosition(self.currentVnodeStack)
            if current:
                # g.trace('using convertStackToPosition',current)
                c.setCurrentPosition(current)
            else:
                # g.trace(self.currentVnodeStack)
                c.setCurrentPosition(c.rootPosition())
                
            # At present this is useless: the drawing code doesn't set the top position properly.
            if 0:
                top = self.convertStackToPosition(self.topVnodeStack)
                if top:
                    c.setTopPosition(top)
            #@nonl
            #@-node:ekr.20050915090544.5:<< set current and top positions >>
            #@nl
        self.restoreDescendantAttributes() # New in 4.4: this is now a helper.
        self.descendentUnknownAttributesDictList = []
        self.descendentExpandedList = []
        self.descendentMarksList = []
        self.tnodesDict = {}
        if not c.currentPosition():
            c.setCurrentPosition(c.rootPosition())
        c.selectVnode(c.currentPosition()) # load body pane
        c.loading = False # reenable c.changed
        c.setChanged(c.changed) # Refresh the changed marker.
        return ok, self.ratio
    #@nonl
    #@+node:ekr.20050915090544.4:restoreDescendantAttributes (new in 4.4)
    def restoreDescendantAttributes (self):
        
        for resultDict in self.descendentUnknownAttributesDictList:
            d = resultDict
            if d.has_key('vnxs'):
                gnxs = d.get('vnxs')
                del d ['vnxs']
                ### To do: handle vnxs.
                
            for gnx in d.keys():
                tref = self.canonicalTnodeIndex(gnx)
                t = self.tnodesDict.get(tref)
                if t: t.unknownAttributes = resultDict[gnx]
                # else: g.trace("can not find tnode: gnx = %s" % gnx,color="red")
                    
        marks = {} ; expanded = {}
        for gnx in self.descendentExpandedList:
            t = self.tnodesDict.get(gnx)
            if t: expanded[t]=t
            # else: g.trace("can not find tnode: gnx = %s" % gnx,color="red")
            
        for gnx in self.descendentMarksList:
            t = self.tnodesDict.get(gnx)
            if t: marks[t]=t
            # else: g.trace("can not find tnode: gnx = %s" % gnx,color="red")
        
        if marks or expanded:
            # g.trace("marks",len(marks),"expanded",len(expanded))
            for p in c.all_positions_iter():
                if marks.get(p.v.t):
                    p.v.initMarkedBit()
                        # This was the problem: was p.setMark.
                        # There was a big performance bug in the mark hook in the Node Navigator plugin.
                if expanded.get(p.v.t):
                    p.expand()
    #@nonl
    #@-node:ekr.20050915090544.4:restoreDescendantAttributes (new in 4.4)
    #@-node:ekr.20050915090544:getLeoFile & helper
    #@+node:ekr.20050915084416.4:createVnode (changed for 4.2) sets skip
    def createVnode (self,parent,back,tref,headline,attrDict):
        
        # g.trace(parent,headline)
        v = None ; c = self.c
        # Shared tnodes are placed in the file even if empty.
        if tref == -1:
            t = leoNodes.tnode()
        else:
            tref = self.canonicalTnodeIndex(tref)
            t = self.tnodesDict.get(tref)
            if not t:
                t = self.newTnode(tref)
        if back: # create v after back.
            v = back.insertAfter(t)
        elif parent: # create v as the parent's first child.
            v = parent.insertAsNthChild(0,t)
        else: # create a root vnode
            v = leoNodes.vnode(c,t)
            v.moveToRoot()
    
        if v not in v.t.vnodeList:
            v.t.vnodeList.append(v) # New in 4.2.
    
        skip = len(v.t.vnodeList) > 1
        v.initHeadString(headline,encoding=self.leo_file_encoding)
        #@    << handle unknown vnode attributes >>
        #@+node:ekr.20050915084416.5:<< handle unknown vnode attributes >>
        keys = attrDict.keys()
        if keys:
            v.unknownAttributes = attrDict
        
            if 0: # For debugging.
                s = "unknown attributes for " + v.headString()
                g.es_print(s,color="blue")
                for key in keys:
                    s = "%s = %s" % (key,attrDict.get(key))
                    g.es_print(s)
        #@nonl
        #@-node:ekr.20050915084416.5:<< handle unknown vnode attributes >>
        #@nl
        # g.trace(skip,tref,v,v.t,len(v.t.vnodeList))
        return v,skip
    #@nonl
    #@-node:ekr.20050915084416.4:createVnode (changed for 4.2) sets skip
    #@-node:ekr.20050915084416.3:reading
    #@+node:ekr.20050915084416.6:writing
    #@+node:ekr.20050915084628:assign/compactFileIndices (changed for 4.4)
    def assignFileIndices (self):
        
        """Assign a file index to all tnodes"""
        
        c = self.c ; nodeIndices = g.app.nodeIndices
    
        nodeIndices.setTimestamp() # This call is fairly expensive.
    
        # Assign missing gnx's, converting ints to gnx's.
        # Always assign an (immutable) index, even if the tnode is empty.
        for p in c.allNodes_iter():
            try: # Will fail for None or any pre 4.1 file index.
                theId,time,n = p.v.t.fileIndex
            except TypeError:
                # Don't convert to string until the actual write.
                p.v.t.fileIndex = nodeIndices.getNewIndex()
                
            # New in 4.4.
            if not hasattr(p.v.gnx):
                p.v.gnx = nodeIndices.getNewIndex()
    
        if 0: # debugging:
            for p in c.allNodes_iter():
                g.trace('v',p.v.gnx)
                g.trace('t',p.v.t.fileIndex)
    
    # Indices are now immutable, so there is no longer any difference between these two routines.
    compactFileIndices = assignFileIndices
    #@nonl
    #@-node:ekr.20050915084628:assign/compactFileIndices (changed for 4.4)
    #@+node:ekr.20050915084416.7:putUnknownAttributes
    def putUnknownAttributes (self,torv):
        
        """Put pickleable values for all keys in torv.unknownAttributes dictionary."""
        
        attrDict = torv.unknownAttributes
        if type(attrDict) != type({}):
            g.es("ignoring non-dictionary unknownAttributes for",torv,color="blue")
            return
    
        for key in attrDict.keys():
            val = attrDict[key]
            self.putUa(torv,key,val)
    #@nonl
    #@+node:ekr.20050915084416.8:putUa (new in 4.3) (changed for 4.3)
    def putUa (self,torv,key,val):
        
        '''Put attribute whose name is key and value is val to the output stream.'''
        
        # New in 4.3: leave string attributes starting with 'str_' alone.
        if key.startswith('str_'):
            if type(val) == type(''):
                attr = ' %s="%s"' % (key,self.xmlEscape(val))
                self.put(attr)
            else:
                g.es("ignoring non-string attribute %s in %s" % (
                    key,torv),color="blue")
            return
        try:
            try:
                # Protocol argument is new in Python 2.3
                # Use protocol 1 for compatibility with bin.
                s = pickle.dumps(val,protocol=1)
            except TypeError:
                s = pickle.dumps(val,bin=True)
            attr = ' %s="%s"' % (key,binascii.hexlify(s))
            self.put(attr)
    
        except pickle.PicklingError:
            # New in 4.2 beta 1: keep going after error.
            g.es("ignoring non-pickleable attribute %s in %s" % (
                key,torv),color="blue")
    #@nonl
    #@-node:ekr.20050915084416.8:putUa (new in 4.3) (changed for 4.3)
    #@-node:ekr.20050915084416.7:putUnknownAttributes
    #@+node:ekr.20050915084416.9:putDescendentAttributes (writes marks and expanded attributes)
    def putDescendentAttributes (self,p):
        
        nodeIndices = g.app.nodeIndices
    
        # Create a list of all tnodes whose vnodes are marked or expanded
        marks = [] ; expanded = []
        for p in p.subtree_iter():
            if p.isMarked() and not p in marks:
                marks.append(p.copy())
            if p.hasChildren() and p.isExpanded() and not p in expanded:
                expanded.append(p.copy())
    
        for theList,tag in ((marks,"marks="),(expanded,"expanded=")):
            if theList:
                sList = []
                for p in theList:
                    gnx = p.v.t.fileIndex
                    sList.append("%s," % nodeIndices.toString(gnx))
                s = string.join(sList,'')
                # g.trace(tag,[str(p.headString()) for p in theList])
                self.put('\n' + tag)
                self.put_in_dquotes(s)
    #@nonl
    #@-node:ekr.20050915084416.9:putDescendentAttributes (writes marks and expanded attributes)
    #@+node:ekr.20050915084416.10:putDescendentUnknownAttributes (changed for 4.4)
    # For 4.4 we 'piggyback' all v.gnx fields in resultDict['vnxs']
    
    def putDescendentUnknownAttributes (self,p):
    
        # Create a list of all tnodes having a valid unknownAttributes dict.
        # New in 4.4: create a dictionary: keys are tnodes, values are lists of vnx's.
        tnodes = [] ; vnxs = {}
        for p2 in p.subtree_iter():
            v = p2.v
            t = v.t
            if hasattr(t,"unknownAttributes"):
                if t not in tnodes :
                    tnodes.append((p,t),)
                    
            # New in 4.4.
            theList = vnxs.get(t,[])
            theList.append(v.gnx)
            vnxs[t] = theList
            
        
        # Create a list of pairs (t,d) where d contains only pickleable entries.
        data = []
        for p,t in tnodes:
            if type(t.unknownAttributes) != type({}):
                 g.es("ignoring non-dictionary unknownAttributes for",p,color="blue")
            else:
                # Create a new dict containing only entries that can be pickled.
                d = dict(t.unknownAttributes) # Copy the dict.
                for key in d.keys():
                    try: pickle.dumps(d[key],bin=True)
                    except pickle.PicklingError:
                        del d[key]
                        g.es("ignoring bad unknownAttributes key %s in %s" % (
                            key,p),color="blue")
                data.append((t,d),)
                
        # Create resultDict, an enclosing dict to hold all the data.
        resultDict = {}
        nodeIndices = g.app.nodeIndices
        for t,d in data:
            gnx = nodeIndices.toString(t.fileIndex)
            resultDict[gnx]=d
        
        if 0:
            print "resultDict"
            for key in resultDict:
                print ; print key,resultDict[key]
            
        # Pickle and hexlify resultDict.
        if resultDict:
            try:
                tag = "descendentTnodeUnknownAttributes"
                s = pickle.dumps(resultDict,bin=True)
                field = ' %s="%s"' % (tag,binascii.hexlify(s))
                self.put(field)
            except pickle.PicklingError:
                g.trace("can't happen",color="red")
    #@nonl
    #@-node:ekr.20050915084416.10:putDescendentUnknownAttributes (changed for 4.4)
    #@+node:ekr.20050915084416.11:putVnode (3.x and 4.x) (Added vx attribute for 4.4)
    def putVnode (self,p):
    
        """Write a <v> element corresponding to a vnode."""
    
        fc = self ; c = fc.c ; v = p.v
        isThin = p.isAtThinFileNode()
        # Must check all parents.
        isIgnore = False
        for p2 in p.self_and_parents_iter():
            if p2.isAtIgnoreNode():
                isIgnore = True ; break
        isOrphan = p.isOrphan()
        forceWrite = isIgnore or not isThin or (isThin and isOrphan)
    
        fc.put("<v")
        #@    << put vx attribute >>
        #@+node:ekr.20050915092747:<< put vx attribute >>
        vnx = g.app.nodeIndices.toString(v.gnx)
        fc.put(" vx=") ; fc.put_in_dquotes(vnx)
        #@nonl
        #@-node:ekr.20050915092747:<< put vx attribute >>
        #@afterref
 # New in 4.4.
        #@    << Put tnode index >>
        #@+node:ekr.20050915084416.12:<< Put tnode index >>
        if v.t.fileIndex:
            gnx = g.app.nodeIndices.toString(v.t.fileIndex)
            fc.put(" t=") ; fc.put_in_dquotes(gnx)
        
            # g.trace(v.t)
            if forceWrite or self.usingClipboard:
                v.t.setWriteBit() # 4.2: Indicate we wrote the body text.
        else:
            g.trace(v.t.fileIndex,v)
            g.es("error writing file(bad v.t.fileIndex)!")
            g.es("try using the Save To command")
        #@nonl
        #@-node:ekr.20050915084416.12:<< Put tnode index >>
        #@nl
        #@    << Put attribute bits >>
        #@+node:ekr.20050915084416.13:<< Put attribute bits >>
        attr = ""
        if p.v.isExpanded(): attr += "E"
        if p.v.isMarked():   attr += "M"
        if p.v.isOrphan():   attr += "O"
        
        if 1: # No longer a bottleneck now that we use p.equal rather than p.__cmp__
            # Almost 30% of the entire writing time came from here!!!
            if p.equal(self.topPosition):   attr += "T" # was a bottleneck
            if c.isCurrentPosition(p):      attr += "V" # was a bottleneck
        
        if attr: fc.put(' a="%s"' % attr)
        #@nonl
        #@-node:ekr.20050915084416.13:<< Put attribute bits >>
        #@nl
        #@    << Put tnodeList and unKnownAttributes >>
        #@+node:ekr.20050915084416.14:<< Put tnodeList and unKnownAttributes >>
        # Write the tnodeList only for @file nodes.
        # New in 4.2: tnode list is in tnode.
        
        if 0: # Debugging.
            if v.isAnyAtFileNode():
                if hasattr(v.t,"tnodeList"):
                    g.trace(v.headString(),len(v.t.tnodeList))
                else:
                    g.trace(v.headString(),"no tnodeList")
        
        if hasattr(v.t,"tnodeList") and len(v.t.tnodeList) > 0 and v.isAnyAtFileNode():
            if isThin:
                if g.app.unitTesting:
                    g.app.unitTestDict["warning"] = True
                g.es("deleting tnode list for %s" % p.headString(),color="blue")
                # This is safe: cloning can't change the type of this node!
                delattr(v.t,"tnodeList")
            else:
                fc.putTnodeList(v) # New in 4.0
        
        if hasattr(v,"unknownAttributes"): # New in 4.0
            self.putUnknownAttributes(v)
            
        if p.hasChildren() and not forceWrite and not self.usingClipboard:
            # We put the entire tree when using the clipboard, so no need for this.
            self.putDescendentUnknownAttributes(p)
            self.putDescendentAttributes(p)
        #@nonl
        #@-node:ekr.20050915084416.14:<< Put tnodeList and unKnownAttributes >>
        #@nl
        fc.put(">")
        #@    << Write the head text >>
        #@+node:ekr.20050915084416.16:<< Write the head text >>
        headString = p.v.headString()
        
        if headString:
            fc.put("<vh>")
            fc.putEscapedString(headString)
            fc.put("</vh>")
        #@nonl
        #@-node:ekr.20050915084416.16:<< Write the head text >>
        #@nl
        
        if not self.usingClipboard:
            #@        << issue informational messages >>
            #@+node:ekr.20050915084416.15:<< issue informational messages >>
            if p.isAtThinFileNode and p.isOrphan():
                g.es("Writing erroneous: %s" % p.headString(),color="blue")
                p.clearOrphan()
            
            if 0: # For testing.
                if p.isAtIgnoreNode():
                     for p2 in p.self_and_subtree_iter():
                            if p2.isAtThinFileNode():
                                g.es("Writing @ignore'd: %s" % p2.headString(),color="blue")
            #@nonl
            #@-node:ekr.20050915084416.15:<< issue informational messages >>
            #@nl
    
       # New in 4.2: don't write child nodes of @file-thin trees (except when writing to clipboard)
        if p.hasChildren():
            if forceWrite or self.usingClipboard:
                fc.put_nl()
                # This optimization eliminates all "recursive" copies.
                p.moveToFirstChild()
                while 1:
                    fc.putVnode(p)
                    if p.hasNext(): p.moveToNext()
                    else:           break
                p.moveToParent()
    
        fc.put("</v>") ; fc.put_nl()
    #@nonl
    #@-node:ekr.20050915084416.11:putVnode (3.x and 4.x) (Added vx attribute for 4.4)
    #@-node:ekr.20050915084416.6:writing
    #@-node:ekr.20050915084416.2:from leoFileCommands
    #@-others
#@nonl
#@-node:ekr.20050915084416:reference code
#@-others
#@nonl
#@-node:ekr.20050915064008:@thin __vnx__.py
#@-leo
