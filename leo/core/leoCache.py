#@+leo-ver=4-thin
#@+node:ekr.20100208065621.5894:@thin leoCache.py
'''A module encapsulating Leo's file caching'''

#@+others
#@+node:ekr.20100208062523.5885:class cacher
class cacher:

    '''A class that encapsulates all aspects of Leo's file caching.'''

    #@    @+others
    #@+node:ekr.20100208062523.5886:ctor (casher)
    def __init__ (c=None,fileName=None):

        self.c = c
        self.fileName = fileName
        self.trace = True
        self.use_pickleshare = False
    #@-node:ekr.20100208062523.5886:ctor (casher)
    #@+node:ekr.20100208065621.5893:createGlobalDb
    def setGlobalDb(self):

        '''Create the database bound to g.app.db'''

        trace = False
        if trace: g.trace('g.enableDB',g.enableDB)

        if g.enableDB:
            dbdirname = self.homeLeoDir + "/db/global"
            self.db = leo.external.pickleshare.PickleShareDB(dbdirname, protocol='picklez')
            if trace: g.trace(self.db,dbdirname)
        else:
            self.db = {}
    #@-node:ekr.20100208065621.5893:createGlobalDb
    #@+node:ekr.20100208071151.5907:fileKey
    # was atFile._contentHashFile

    def fileKey(self,s,content):

        '''Compute the hash of s (usually a headline) and content.
        s may be unicode, content must be bytes (or plain string in Python 2.x'''

        m = hashlib.md5()

        if g.isUnicode(s):
            s = g.toEncodedString(s)

        if g.isUnicode(content):
            g.internalError('content arg must be str/bytes')
            content = g.toEncodedString(content)

        m.update(s)
        m.update(content)
        return "fcache/" + m.hexdigest()

    #@-node:ekr.20100208071151.5907:fileKey
    #@+node:ekr.20100208071151.5901:makeCacheList
    def makeCacheList(self,p):

        '''Create a recursive list describing a tree
        for use by v.createOutlineFromCacheList.
        '''

        return [
            p.h,p.b,p.gnx,
            [self.makeCacheList() for p2 in p.children()]]
    #@-node:ekr.20100208071151.5901:makeCacheList
    #@+node:ekr.20100208071151.5905:readFile
    # was atFile.readFromCache

    # Same code as atFile.readFromCache
    # Same code as code in atFile.readOneAtAutoNode

    def readFile (self,fileName,root):

        c = self.c
        s,e = g.readFileIntoString(fileName,raw=True)
        if s is None: return False,None

        key = self.fileKey(root.h,s)

        ok = g.enableDB and key in c.db
        if ok:
            # Delete the previous tree, regardless of the @<file> type.
            while root.hasChildren():
                root.firstChild().doDelete()
            # Recreate the file from the cache.
            aList = c.db[cachefile]
            root.v.createOutlineFromCacheList(c,aList,fileName=fileName)
            at.inputFile.close()
            root.clearDirty()

        return ok,key
    #@-node:ekr.20100208071151.5905:readFile
    #@+node:ekr.20100208071151.5903:writeFile
    # Was atFile.writeCachedTree

    def writeFile(self,p,cachefile):

        trace = False and not g.unitTesting
        c = self.c

        if not g.enableDB or g.app.unitTesting:
            if trace: g.trace('cache disabled')
        elif cachefile in c.db:
            if trace: g.trace('already cached',cachefile)
        else:
            if trace: g.trace('caching ',p.h)
            c.db[cachefile] = p.makeCacheList()
    #@nonl
    #@-node:ekr.20100208071151.5903:writeFile
    #@+node:ekr.20100208065621.5890:test
    def test():
        db = PickleShareDB('~/testpickleshare')
        db.clear()
        print("Should be empty:",list(db.items()))
        db['hello'] = 15
        db['aku ankka'] = [1,2,313]
        db['paths/nest/ok/keyname'] = [1,(5,46)]
        db.hset('hash', 'aku', 12)
        db.hset('hash', 'ankka', 313)
        print("12 =",db.hget('hash','aku'))
        print("313 =",db.hget('hash','ankka'))
        print("all hashed",db.hdict('hash'))
        print(list(db.keys()))
        print(list(db.keys('paths/nest/ok/k*')))
        print(dict(db)) # snapsot of whole db
        db.uncache() # frees memory, causes re-reads later

        # shorthand for accessing deeply nested files
        lnk = db.getlink('myobjects/test')
        lnk.foo = 2
        lnk.bar = lnk.foo + 5
        print(lnk.bar) # 7

    #@-node:ekr.20100208065621.5890:test
    #@+node:ekr.20100208071151.5910:createOutlineFromCacheList & helpers
    def createOutlineFromCacheList(self,parent_v,c,aList,top=True,atAll=None,fileName=None):

        """ Create outline structure from recursive aList
        built by p.makeCacheList.

        Clones will be automatically created by gnx,
        but *not* for the top-level node.
        """

        trace = False and not g.unitTesting
        ### parent_v = self

        #import pprint ; pprint.pprint(tree)
        parent_v = self
        h,b,gnx,children = aList
        if h is not None:
            v = parent_v
            v._headString = h    
            v._bodyString = b

        if top:
            c.cacheListFileName = fileName
            # Scan the body for @all directives.
            for line in g.splitLines(b):
                if line.startswith('@all'):
                    atAll = True ; break
            else:
                atAll = False
        else:
            assert atAll in (True,False,)

        for z in children:
            h,b,gnx,grandChildren = z
            isClone,child_v = self.fastAddLastChild(c,parent_v,gnx)
            if isClone:
                if child_v.b != b:
                    # 2010/02/05: Remove special case for @all.
                    c.nodeConflictList.append(g.bunch(
                        tag='(cached)',
                        fileName=c.cacheListFileName,
                        gnx=gnx,
                        b_old=child_v.b,
                        h_old=child_v.h,
                        b_new=b,
                        h_new=h,
                    ))

                    # Always issue the warning.
                    g.es_print("cached read node changed:",
                        child_v.h,color="red")

                    child_v.h,child_v.b = h,b
                    child_v.setDirty()
                    c.changed = True
                        # Tells getLeoFile to propegate dirty nodes.
            else:
                self.createOutlineFromCacheList(c,child_v,z,top=False,atAll=atAll)
    #@+node:ekr.20100208071151.5911:fastAddLastChild
    # Similar to createThinChild4
    def fastAddLastChild(self,c,parent_v,gnxString):
        '''Create new vnode as last child of the receiver.

        If the gnx exists already, create a clone instead of new vnode.
        '''

        trace = False and not g.unitTesting
        verbose = False
        # parent_v = self
        indices = g.app.nodeIndices
        gnxDict = c.fileCommands.gnxDict

        if gnxString is None: v = None
        else:                 v = gnxDict.get(gnxString)
        is_clone = v is not None

        if trace: g.trace(
            'clone','%-5s' % (is_clone),
            'parent_v',parent_v,'gnx',gnxString,'v',repr(v))

        if is_clone:
            pass
        else:
            v = vnode(context=c)
            if gnxString:
                gnx = indices.scanGnx(gnxString,0)
                v.fileIndex = gnx
            gnxDict[gnxString] = v

        child_v = v
        child_v._linkAsNthChild(parent_v,parent_v.numberOfChildren())
        child_v.setVisited() # Supress warning/deletion of unvisited nodes.

        return is_clone,child_v
    #@-node:ekr.20100208071151.5911:fastAddLastChild
    #@-node:ekr.20100208071151.5910:createOutlineFromCacheList & helpers
    #@-others
#@-node:ekr.20100208062523.5885:class cacher
#@-others
#@nonl
#@-node:ekr.20100208065621.5894:@thin leoCache.py
#@-leo
