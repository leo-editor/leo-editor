#@+leo-ver=4-thin
#@+node:ekr.20100208065621.5894:@thin leoCache.py
'''A module encapsulating Leo's file caching'''

#@<< imports >>
#@+node:ekr.20100208223942.10436:<< imports >>
import leo.core.leoGlobals as g
import leo.core.leoNodes as leoNodes

import glob
import fnmatch
import hashlib
import os
import stat
import sys
import time

isPython3 = sys.version_info >= (3,0,0)

try:
    import marshal
except ImportError:
    marshal = None

if isPython3:
    import pickle
else:
    import cPickle as pickle

try:
    import simplejson
except ImportError:
    simplejson = None

try:
    import zlib
except ImportError:
    zlib = None
#@nonl
#@-node:ekr.20100208223942.10436:<< imports >>
#@nl

#@+others
#@+node:ekr.20100208223942.10450:Top-level functions
abspath     = g.os_path_abspath
basename    = g.os_path_basename
expanduser  = g.os_path_expanduser
isdir       = g.os_path_isdir
isfile      = g.os_path_isfile
join        = g.os_path_join
normcase    = g.os_path_normcase
split       = g.os_path_split
#@nonl
#@+node:ekr.20100208223942.6140:gethashfile
def gethashfile(key):

    return ("%02x" % abs(hash(key) % 256))[-2:]
#@-node:ekr.20100208223942.6140:gethashfile
#@+node:ekr.20100208223942.10456:listdir
def listdir(s, pattern=None):
    """ D.listdir() -> List of items in this directory.

    Use D.files() or D.dirs() instead if you want a listing
    of just files or just subdirectories.

    The elements of the list are path objects.

    With the optional 'pattern' argument, this only lists
    items whose names match the given pattern.
    """
    # self -> self
    names = os.listdir(s)
    if pattern is not None:
        names = fnmatch.filter(names, pattern)
    ### return [self / child for child in names]
    return [join(s,child) for child in names]

#@-node:ekr.20100208223942.10456:listdir
#@+node:ekr.20100208223942.10452:makedirs
def makedirs(self, mode=0o777):

    os.makedirs(self, mode)

#@-node:ekr.20100208223942.10452:makedirs
#@+node:ekr.20100208223942.10464:fn_match
def fn_match(s, pattern):
    """ Return True if self.name matches the given pattern.

    pattern - A filename pattern with wildcards,
        for example '*.py'.
    """

    # self -> s

    ### return fnmatch.fnmatch(self.name, pattern)

    return fnmatch.fnmatch(basename(s), pattern)

#@-node:ekr.20100208223942.10464:fn_match
#@+node:ekr.20100208223942.10458:openFile
def openFile(fn, mode='r'):
    """ Open this file.  Return a file object.

    Do not print an error message.
    It is not an error for this to fail. 
    """
    # Catch exception so Leo doesn't crash on startup.
    try:
        return open(fn, mode)
    except Exception:
        return None
#@-node:ekr.20100208223942.10458:openFile
#@+node:ekr.20100208223942.10460:relpathto
def relpathto(src, dst):
    """ Return a relative path from self to dst.

    If there is no relative path from self to dst, for example if
    they reside on different drives in Windows, then this returns
    dst.abspath().
    """

    # self --> src
    ### origin = src.abspath()
    origin = abspath(src)
    ### dst = path(dst).abspath()
    dst = abspath(dst)

    ### orig_list = origin.normcase().splitall()
    orig_list = splitall(normcase(origin))
    # Don't normcase dst!  We want to preserve the case.
    dest_list = splitall(dst) ### dst.splitall()

    if orig_list[0] != normcase(dest_list[0]):
        # Can't get here from there.
        return dst

    # Find the location where the two paths start to differ.
    i = 0
    for start_seg, dest_seg in zip(orig_list, dest_list):
        if start_seg != normcase(dest_seg):
            break
        i += 1

    # Now i is the point where the two paths diverge.
    # Need a certain number of "os.pardir"s to work up
    # from the origin to the point of divergence.
    segments = [os.pardir] * (len(orig_list) - i)
    # Need to add the diverging part of dest_list.
    segments += dest_list[i:]
    if len(segments) == 0:
        # If they happen to be identical, use os.curdir.
        ### return path(os.curdir)
        return os.curdir
    else:
        ### return path(join(*segments))
        return join(*segments)


#@-node:ekr.20100208223942.10460:relpathto
#@+node:ekr.20100208223942.10462:splitall
def splitall(s):
    """ Return a list of the path components in this path.

    The first item in the list will be a path.  Its value will be
    either os.curdir, os.pardir, empty, or the root directory of
    this path (for example, '/' or 'C:\\').  The other items in
    the list will be strings.

    path.path.joinpath(*result) will yield the original path.
    """
    parts = []
    loc = s
    while loc != os.curdir and loc != os.pardir:
        prev = loc
        ### loc, child = prev.splitpath()
        loc,child = split(prev)
        if loc == prev:
            break
        parts.append(child)
    parts.append(loc)
    parts.reverse()
    return parts

#@-node:ekr.20100208223942.10462:splitall
#@+node:ekr.20100208223942.10454:walkfiles
def walkfiles(s, pattern=None):

    """ D.walkfiles() -> iterator over files in D, recursively.

    The optional argument, pattern, limits the results to files
    with names that match the pattern.  For example,
    mydir.walkfiles('*.tmp') yields only files with the .tmp
    extension.
    """

    ### self -> s

    ### for child in self.listdir():
    for child in listdir(s):
        ### if child.isfile():
        if isfile(child):
            ### if pattern is None or child.fnmatch(pattern):
            if pattern is None or fn_match(child,pattern):
                yield child
        ### elif child.isdir():
        elif isdir(child):
            ### for f in child.walkfiles(pattern):
            for f in walkfiles(child,pattern):
                yield f

#@-node:ekr.20100208223942.10454:walkfiles
#@-node:ekr.20100208223942.10450:Top-level functions
#@+node:ekr.20100208062523.5885:class cacher
class cacher:

    '''A class that encapsulates all aspects of Leo's file caching.'''

    #@    @+others
    #@+node:ekr.20100208082353.5919: Birth
    #@+node:ekr.20100208062523.5886: ctor (cacher)
    def __init__ (self,c=None):

        self.c = c
        self.db = {} # set by initFileDB and initGlobalDB
        self.fn = None # set by initFile.
        self.trace = True
        self.use_pickleshare = True
    #@-node:ekr.20100208062523.5886: ctor (cacher)
    #@+node:ekr.20100208082353.5918:initFileDB
    def initFileDB (self,fn):

        self.fn = fn

        pth, bname = split(fn)

        if pth and bname and g.enableDB:
            fn = fn.lower()
            fn = g.toEncodedString(fn) # Required for Python 3.x.

            dbdirname = join(g.app.homeLeoDir,'db',
                '%s_%s' % (bname,hashlib.md5(fn).hexdigest()))

            # Use compressed pickles (handy for @thin caches)
            self.db = PickleShareDB(dbdirname,protocol='picklez')
    #@-node:ekr.20100208082353.5918:initFileDB
    #@+node:ekr.20100208082353.5920:initGlobalDb
    def initGlobalDB (self):

        trace = False and not g.unitTesting

        if g.enableDB:
            dbdirname = g.app.homeLeoDir + "/db/global"
            self.db = PickleShareDB(dbdirname, protocol='picklez')
            if trace: g.trace(self.db,dbdirname)
        else:
            self.db = {}
    #@-node:ekr.20100208082353.5920:initGlobalDb
    #@+node:ekr.20100208065621.5893:setGlobalDb
    def setGlobalDb(self):

        '''Create the database bound to g.app.db'''

        trace = False and not g.unitTesting

        if trace: g.trace('g.enableDB',g.enableDB)

        if g.enableDB:
            dbdirname = g.app.homeLeoDir + "/db/global"
            self.db = PickleShareDB(dbdirname, protocol='picklez')
            if trace: g.trace(self.db,dbdirname)
        else:
            self.db = {}
    #@-node:ekr.20100208065621.5893:setGlobalDb
    #@-node:ekr.20100208082353.5919: Birth
    #@+node:ekr.20100208071151.5907:fileKey
    # was atFile._contentHashFile

    def fileKey(self,s,content,requireEncodedString=False):

        '''Compute the hash of s (usually a headline) and content.
        s may be unicode, content must be bytes (or plain string in Python 2.x'''

        m = hashlib.md5()

        if g.isUnicode(s):
            s = g.toEncodedString(s)

        if g.isUnicode(content):
            if requireEncodedString:
                g.internalError('content arg must be str/bytes')
            content = g.toEncodedString(content)

        m.update(s)
        m.update(content)
        return "fcache/" + m.hexdigest()
    #@-node:ekr.20100208071151.5907:fileKey
    #@+node:ekr.20100208082353.5925:Reading
    #@+node:ekr.20100208071151.5910:createOutlineFromCacheList & helpers
    def createOutlineFromCacheList(self,parent_v,aList,top=True,atAll=None,fileName=None):

        """ Create outline structure from recursive aList
        built by makeCacheList.

        Clones will be automatically created by gnx,
        but *not* for the top-level node.
        """

        trace = False and not g.unitTesting
        ### parent_v = self

        if trace: g.trace(parent_v,g.callers(5))

        c = self.c
        if not c:
            g.internalError('no c')

        #import pprint ; pprint.pprint(tree)
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
            isClone,child_v = self.fastAddLastChild(parent_v,gnx)
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
                self.createOutlineFromCacheList(child_v,z,top=False,atAll=atAll)
    #@+node:ekr.20100208071151.5911:fastAddLastChild
    # Similar to createThinChild4
    def fastAddLastChild(self,parent_v,gnxString):
        '''Create new vnode as last child of the receiver.

        If the gnx exists already, create a clone instead of new vnode.
        '''

        trace = False and not g.unitTesting
        verbose = False
        c = self.c
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
            v = leoNodes.vnode(context=c)
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
    #@+node:ekr.20100208082353.5923:getCachedGlobalFileRatios
    def getCachedGlobalFileRatios (self):

        trace = False and not g.unitTesting
        c = self.c

        if not c:
            return g.internalError('no commander')

        globals_tag = g.choose(g.isPython3,'leo3k.globals','leo2k.globals')
        # globals_tag = g.toEncodedString(globals_tag,'ascii')

        key = self.fileKey(c.mFileName,globals_tag)

        ratio  = float(self.db.get('body_outline_ratio_%s' % (key),'0.5'))
        ratio2 = float(self.db.get('body_secondary_ratio_%s' % (key),'0.5'))

        if trace:
            g.trace('key',key,'%1.2f %1.2f' % (ratio,ratio2))

        return ratio,ratio2
    #@-node:ekr.20100208082353.5923:getCachedGlobalFileRatios
    #@+node:ekr.20100208082353.5924:getCachedStringPosition
    def getCachedStringPosition(self):

        c = self.c

        trace = False and not g.unitTesting

        if not c:
            return g.internalError('no commander')

        globals_tag = g.choose(g.isPython3,'leo3k.globals','leo2k.globals')
        # globals_tag = g.toEncodedString(globals_tag,'ascii')

        key = self.fileKey(c.mFileName,globals_tag)
        str_pos = self.db.get('current_position_%s' % key)

        if trace: g.trace(str_pos,key)
        return str_pos
    #@-node:ekr.20100208082353.5924:getCachedStringPosition
    #@+node:ekr.20100208082353.5922:getCachedWindowPositionDict
    def getCachedWindowPositionDict (self,fn):

        trace = False and not g.unitTesting
        c = self.c

        if not c:
            g.internalError('no commander')
            return {}

        globals_tag = g.choose(g.isPython3,'leo3k.globals','leo2k.globals')
        key = self.fileKey(fn,globals_tag)
        data = self.db.get('window_position_%s' % (key))

        if data:
            top,left,height,width = data
            top,left,height,width = int(top),int(left),int(height),int(width)
            d = {'top':top,'left':left,'height':height,'width':width}
        else:
            d = {}

        if trace: g.trace(fn,key,data)
        return d
    #@-node:ekr.20100208082353.5922:getCachedWindowPositionDict
    #@+node:ekr.20100208071151.5905:readFile
    # was atFile.readFromCache
    # Same code as atFile.readFromCache
    # Same code as code in atFile.readOneAtAutoNode

    def readFile (self,fileName,root):

        trace = False and not g.unitTesting
        c = self.c

        if not g.enableDB:
            if trace: g.trace('g.enableDB is False')
            return False,None

        s,e = g.readFileIntoString(fileName,raw=True)
        if s is None:
            if trace: g.trace('empty file contents',fileName)
            return False,None
        assert not g.isUnicode(s)

        # There will be a bug if s is not already an encoded string.
        key = self.fileKey(root.h,s,requireEncodedString=True)
        ok = key in self.db
        if trace: g.trace('in cache',ok,fileName,key)
        if ok:
            # Delete the previous tree, regardless of the @<file> type.
            while root.hasChildren():
                root.firstChild().doDelete()
            # Recreate the file from the cache.
            aList = self.db[key]
            self.createOutlineFromCacheList(root.v,aList,fileName=fileName)

        return ok,key
    #@-node:ekr.20100208071151.5905:readFile
    #@-node:ekr.20100208082353.5925:Reading
    #@+node:ekr.20100208082353.5927:Writing
    #@+node:ekr.20100208071151.5901:makeCacheList
    def makeCacheList(self,p):

        '''Create a recursive list describing a tree
        for use by createOutlineFromCacheList.
        '''

        return [
            p.h,p.b,p.gnx,
            [self.makeCacheList(p2) for p2 in p.children()]]
    #@-node:ekr.20100208071151.5901:makeCacheList
    #@+node:ekr.20100208082353.5929:setCachedGlobalsElement
    def setCachedGlobalsElement(self,fn):

        trace = False and not g.unitTesting
        c = self.c

        if not c:
            return g.internalError('no commander')

        globals_tag = g.choose(g.isPython3,'leo3k.globals','leo2k.globals')
        key = self.fileKey(fn,globals_tag)

        if trace: g.trace(c.mFileName,key)

        self.db['body_outline_ratio_%s' % key] = str(c.frame.ratio)
        self.db['body_secondary_ratio_%s' % key] = str(c.frame.secondary_ratio)
        if trace: g.trace('ratios: %1.2f %1.2f' % (
            c.frame.ratio,c.frame.secondary_ratio))

        width,height,left,top = c.frame.get_window_info()

        self.db['window_position_%s' % key] = (
            str(top),str(left),str(height),str(width))
        if trace:
            g.trace('top',top,'left',left,'height',height,'width',width)
    #@-node:ekr.20100208082353.5929:setCachedGlobalsElement
    #@+node:ekr.20100208082353.5928:setCachedStringPosition
    def setCachedStringPosition(self,str_pos):

        trace = False and not g.unitTesting
        c = self.c

        if not c:
            return g.internalError('no commander')

        globals_tag = g.choose(g.isPython3,'leo3k.globals','leo2k.globals')
        # globals_tag = g.toEncodedString(globals_tag,'ascii')

        key = self.fileKey(c.mFileName,globals_tag)
        self.db['current_position_%s' % key] = str_pos

        if trace: g.trace(str_pos,key)
    #@-node:ekr.20100208082353.5928:setCachedStringPosition
    #@+node:ekr.20100208071151.5903:writeFile
    # Was atFile.writeCachedTree

    def writeFile(self,p,fileKey):

        trace = False and not g.unitTesting
        c = self.c

        if not fileKey:
            g.internalError('empty fileKey')
        elif not g.enableDB:
            if trace: g.trace('cache disabled')
        elif fileKey in self.db:
            if trace: g.trace('already cached',fileKey)
        else:
            if trace: g.trace('caching ',p.h,fileKey)
            self.db[fileKey] = self.makeCacheList(p)
    #@-node:ekr.20100208071151.5903:writeFile
    #@-node:ekr.20100208082353.5927:Writing
    #@+node:ekr.20100208065621.5890:test (cacher)
    def test(self):

        # db = pickleshare.PickleShareDB('~/testpickleshare')
        self.initFileDB('~/testpickleshare')
        db = self.db
        db.clear()
        # print("Should be empty:",list(db.items()))
        assert not list(db.items())
        db['hello'] = 15
        db['aku ankka'] = [1,2,313]
        db['paths/nest/ok/keyname'] = [1,(5,46)]
        db.hset('hash', 'aku', 12)
        db.hset('hash', 'ankka', 313)
        if not g.unitTesting:
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
        # print(lnk.bar) # 7
        db.clear()
        # print('passed')
        return True
    #@-node:ekr.20100208065621.5890:test (cacher)
    #@-others
#@-node:ekr.20100208062523.5885:class cacher
#@+node:ekr.20100208223942.5967:class PickleShareDB (internal)
_sentinel = object()

class PickleShareDB:

    """ The main 'connection' object for PickleShare database """

    #@    @+others
    #@+node:ekr.20100208223942.5968: Birth & special methods
    #@+node:ekr.20100208223942.5969: __init__
    def __init__(self,root,protocol='pickle'):

        """ Initialize a PickleShare object that will manage the specied directory

        root: The directory that contains the data. Created if it doesn't exist.

        protocol: one of:
            * 'pickle' (universal, default) 
            * 'picklez' (compressed pickle)         
            * 'marshal' (fast, limited type support)
            * 'json' : brief, human-readable, very limited type support

        Protol 'json' requires installation of simplejson module
        """

        trace = False and not g.unitTesting

        ### self.root = Path(root).expanduser().abspath()
        self.root = abspath(expanduser(root))

        if trace: g.trace('PickleShareDB',self.root)

        ### if not self.root.isdir():
        if not isdir(self.root):
            if trace: g.trace('makedirs',self.root)
            ### self.root.makedirs()
            os.makedirs(self.root,mode=0o777)

        self.cache = {}
            # Keys are normalized file names.
            # Values are tuples (obj, orig_mod_time)

        if protocol == 'pickle':
            self.loader = pickle.load
            self.dumper = pickle.dump
        elif protocol == 'marshal':
            if marshal:
                self.loader = marshal.load
                self.dumper = marshal.dump
        elif protocol == 'json':
            if simplejson:
                self.loader = simplejson.load
                self.dumper = simplejson.dump
        elif protocol == 'picklez':
            if zlib:
                def loadz(fileobj):
                    # 2010/02/04 EKR: guard against null fileobj.
                    if fileobj:
                        val = pickle.loads(zlib.decompress(fileobj.read()))
                        return val
                    else:
                        return None

                def dumpz(val, fileobj):
                    # 2010/02/04 EKR: guard against null fileobj.
                    if fileobj:
                        compressed = zlib.compress(pickle.dumps(val, pickle.HIGHEST_PROTOCOL))
                        fileobj.write(compressed)

                self.loader = loadz
                self.dumper = dumpz
    #@-node:ekr.20100208223942.5969: __init__
    #@+node:ekr.20100208223942.5970:__contains__
    def __contains__(self, key):

        trace = False and g.unitTesting

        if trace: g.trace('(old PickleShareDB)',key)

        return self.has_key(key)
    #@-node:ekr.20100208223942.5970:__contains__
    #@+node:ekr.20100208223942.5971:__delitem__ 
    def __delitem__(self,key):

        """ del db["key"] """

        trace = False and g.unitTesting

        ### fil = self.root / key
        fil = join(self.root,key)

        if trace: g.trace('(old PickleShareDB)',key,g.shortFileName(fil))

        self.cache.pop(fil,None)

        try:
            ### fil.remove()
            os.remove(fil)
        except OSError:
            # notfound and permission denied are ok - we
            # lost, the other process wins the conflict
            pass
    #@-node:ekr.20100208223942.5971:__delitem__ 
    #@+node:ekr.20100208223942.5972:__getitem__ 
    def __getitem__(self,key):

        """ db['key'] reading """

        trace = False and not g.unitTesting

        ### fil = self.root / key
        fil = join(self.root,key)
        try:
            ### mtime = (fil.stat()[stat.ST_MTIME])
            mtime = (os.stat(fil)[stat.ST_MTIME])
        except OSError:
            if trace: g.trace('***OSError',fil,key)
            raise KeyError(key)

        if fil in self.cache and mtime == self.cache[fil][1]:
            obj = self.cache[fil][0]
            if trace: g.trace('(PickleShareDB: in cache)',key)
            return obj
        try:
            # The cached item has expired, need to read
            ### obj = self.loader(fil.open("rb"))
            obj = self.loader(openFile(fil,'rb'))
        except Exception:
            if trace: g.trace('***Exception',key)
            raise KeyError(key)

        self.cache[fil] = (obj,mtime)
        if trace: g.trace('(PickleShareDB: set cache)',key)
        return obj
    #@-node:ekr.20100208223942.5972:__getitem__ 
    #@+node:ekr.20100208223942.5973:__iter__
    def __iter__(self):

        trace = False and g.unitTesting

        if trace: g.trace('(old PickleShareDB)',list(self.keys()))

        for k in list(self.keys()):
            yield k
    #@-node:ekr.20100208223942.5973:__iter__
    #@+node:ekr.20100208223942.5974:__repr__
    def __repr__(self):

        return "PickleShareDB('%s')" % self.root



    #@-node:ekr.20100208223942.5974:__repr__
    #@+node:ekr.20100208223942.5975:__setitem__
    def __setitem__(self,key,value):

        """ db['key'] = 5 """

        trace = False and not g.unitTesting
        ### fil = self.root / key
        fil = join(self.root,key)

        if trace: g.trace('(PickleShareDB)',key)
        ### parent = fil.parent
        parent,junk = split(fil)

        ### if parent and not parent.isdir():
        if parent and not isdir(parent):
            ### parent.makedirs()
            makedirs(parent)

        ### pickled = self.dumper(value,fil.open('wb'))
        f = openFile(fil,'wb')
        pickled = self.dumper(value,f)

        try:
            ### self.cache[fil] = (value,fil.mtime)
            mtime = os.path.getmtime(fil)
            self.cache[fil] = (value,mtime)
        except OSError as e:
            if trace: g.trace('***OSError')
            if e.errno != 2:
                raise
    #@-node:ekr.20100208223942.5975:__setitem__
    #@+node:ekr.20100208223942.5976:_normalized
    def _normalized(self, p):
        """ Make a key suitable for user's eyes """

        # return str(self.root.relpathto(p)).replace('\\','/')
        return relpathto(self.root,p).replace('\\','/')
    #@-node:ekr.20100208223942.5976:_normalized
    #@-node:ekr.20100208223942.5968: Birth & special methods
    #@+node:ekr.20100208223942.5977:Methods that call special methods
    #@+node:ekr.20100208223942.5978:clear
    def clear (self):

        for z in self.keys():
            self.__delitem__(z)
    #@-node:ekr.20100208223942.5978:clear
    #@+node:ekr.20100208223942.5979:get
    def get(self, key, default=None):

        trace = False and g.unitTesting
        if trace: g.trace('(old PickleShareDB)')

        try:
            return self[key]
        except KeyError:
            return default
    #@-node:ekr.20100208223942.5979:get
    #@+node:ekr.20100208223942.5980:has_key
    def has_key(self, key):

        trace = False and g.unitTesting
        if trace: g.trace('(PickleShareDB)',key)

        try:
            value = self[key]
        except KeyError:
            return False

        return True
    #@-node:ekr.20100208223942.5980:has_key
    #@+node:ekr.20100208223942.5981:items
    # def iteritems(self):
        # for k in self:
            # yield (k, self[k])

    def items(self):
        return [z for z in self]
    #@-node:ekr.20100208223942.5981:items
    #@+node:ekr.20100208223942.5982:keys (modified)
    # def iterkeys(self):
        # return self.__iter__()

    def keys(self, globpat = None):
        """ All keys in DB, or all keys matching a glob"""

        trace = False and g.unitTesting

        if globpat is None:
            ### files = self.root.walkfiles()
            files = walkfiles(self.root)
        else:
            ### files = [Path(p) for p in glob.glob(self.root/globpat)]
            files = [z for z in glob.glob(join(self.root,globpat))]

        ### result = [self._normalized(p) for p in files if p.isfile()]
        result = [self._normalized(p) for p in files if isfile(p)]

        if trace: g.trace('(old PickleShareDB)',len(result))

        return result

    #@-node:ekr.20100208223942.5982:keys (modified)
    #@-node:ekr.20100208223942.5977:Methods that call special methods
    #@+node:ekr.20100208223942.5983:Other methods
    #@+node:ekr.20100208223942.5984:getlink
    def getlink(self,folder):
        """ Get a convenient link for accessing items  """

        trace = True and not g.unitTesting

        if trace: g.trace(folder,g.callers(5))

        return PickleShareLink(self, folder)

    #@-node:ekr.20100208223942.5984:getlink
    #@+node:ekr.20100208223942.5985:hcompress
    def hcompress(self, hashroot):
        """ Compress category 'hashroot', so hset is fast again

        hget will fail if fast_only is True for compressed items (that were
        hset before hcompress).

        """

        trace = True and not g.unitTesting
        if trace: g.trace(g.callers(5))

        hfiles = self.keys(hashroot + "/*")
        all = {}
        for f in hfiles:
            # print("using",f)
            all.update(self[f])
            self.uncache(f)

        self[hashroot + '/xx'] = all
        for f in hfiles:
            ### p = self.root / f
            p = join(self.root,f)
            ### if p.basename() == 'xx':
            if basename(p) == 'xx':
                continue
            ### p.remove()
            os.remove(p)

    #@-node:ekr.20100208223942.5985:hcompress
    #@+node:ekr.20100208223942.5986:hdict
    def hdict(self, hashroot):
        """ Get all data contained in hashed category 'hashroot' as dict """

        trace = True and not g.unitTesting
        if trace: g.trace(g.callers(5))

        hfiles = self.keys(hashroot + "/*")
        hfiles.sort()
        last = len(hfiles) and hfiles[-1] or ''
        if last.endswith('xx'):
            # print("using xx")
            hfiles = [last] + hfiles[:-1]

        all = {}

        for f in hfiles:
            # print("using",f)
            try:
                all.update(self[f])
            except KeyError:
                print("Corrupt",f,"deleted - hset is not threadsafe!")
                del self[f]

            self.uncache(f)

        return all
    #@-node:ekr.20100208223942.5986:hdict
    #@+node:ekr.20100208223942.5987:hget
    def hget(self, hashroot, key, default = _sentinel, fast_only = True):
        """ hashed get """

        trace = True and not g.unitTesting
        if trace: g.trace(g.callers(5))

        ### hroot = self.root / hashroot
        hroot = join(self.root,hashroot)
        ### hfile = hroot / gethashfile(key)
        hfile = join(hroot,gethashfile(key))
        d = self.get(hfile, _sentinel )
        g.trace("got dict",d,"from",g.shortFileName(hfile))
        if d is _sentinel:
            if fast_only:
                if default is _sentinel:
                    raise KeyError(key)
                return default
            # slow mode ok, works even after hcompress()
            d = self.hdict(hashroot)

        return d.get(key, default)
    #@-node:ekr.20100208223942.5987:hget
    #@+node:ekr.20100208223942.5988:hset
    def hset(self, hashroot, key, value):
        """ hashed set """

        trace = True and not g.unitTesting
        if trace: g.trace(g.callers(5))

        # hroot = self.root / hashroot
        hroot = join(self.root,hashroot)
        ### if not hroot.isdir():
        if not isdir(hroot):
            ### hroot.makedirs()
            makedirs(hroot)
        ### hfile = hroot / gethashfile(key)
        hfile = join(hroot,gethashfile(key))
        d = self.get(hfile, {})
        d.update( {key : value})
        self[hfile] = d                



    #@-node:ekr.20100208223942.5988:hset
    #@+node:ekr.20100208223942.5989:uncache
    def uncache(self,*items):
        """ Removes all, or specified items from cache

        Use this after reading a large amount of large objects
        to free up memory, when you won't be needing the objects
        for a while.

        """

        trace = True and not g.unitTesting
        if trace: g.trace()

        if not items:
            self.cache = {}
        for it in items:
            self.cache.pop(it,None)

    #@-node:ekr.20100208223942.5989:uncache
    #@+node:ekr.20100208223942.5990:waitget
    def waitget(self,key, maxwaittime = 60 ):
        """ Wait (poll) for a key to get a value

        Will wait for `maxwaittime` seconds before raising a KeyError.
        The call exits normally if the `key` field in db gets a value
        within the timeout period.

        Use this for synchronizing different processes or for ensuring
        that an unfortunately timed "db['key'] = newvalue" operation 
        in another process (which causes all 'get' operation to cause a 
        KeyError for the duration of pickling) won't screw up your program 
        logic. 
        """

        trace = True
        if trace: g.trace() # key, g.callers(5)
        wtimes = [0.2] * 3 + [0.5] * 2 + [1]
        tries = 0
        waited = 0
        while 1:
            try:
                val = self[key]
                return val
            except KeyError:
                pass

            if waited > maxwaittime:
                raise KeyError(key)

            time.sleep(wtimes[tries])
            waited+=wtimes[tries]
            if tries < len(wtimes) -1:
                tries+=1
    #@-node:ekr.20100208223942.5990:waitget
    #@-node:ekr.20100208223942.5983:Other methods
    #@-others
#@-node:ekr.20100208223942.5967:class PickleShareDB (internal)
#@+node:ekr.20100208223942.5996:class PickleShareLink (internal)
class PickleShareLink:
    """ A shortdand for accessing nested PickleShare data conveniently.

    Created through PickleShareDB.getlink(), example::

        lnk = db.getlink('myobjects/test')
        lnk.foo = 2
        lnk.bar = lnk.foo + 5

    """
    #@    @+others
    #@+node:ekr.20100208223942.5997:__init__
    def __init__(self, db, keydir ):    
        self.__dict__.update(locals())

    #@-node:ekr.20100208223942.5997:__init__
    #@+node:ekr.20100208223942.5998:__getattr__
    def __getattr__(self,key):
        return self.__dict__['db'][self.__dict__['keydir']+'/' + key]
    #@-node:ekr.20100208223942.5998:__getattr__
    #@+node:ekr.20100208223942.5999:__setattr__
    def __setattr__(self,key,val):
        self.db[self.keydir+'/' + key] = val
    #@-node:ekr.20100208223942.5999:__setattr__
    #@+node:ekr.20100208223942.6000:__repr__
    def __repr__(self):
        db = self.__dict__['db']
        keys = db.keys( self.__dict__['keydir'] +"/*")
        return "<PickleShareLink '%s': %s>" % (
            self.__dict__['keydir'],
            ### ";".join([Path(k).basename() for k in keys]))
             ";".join([g.os_path_basename(k) for k in keys]))
    #@-node:ekr.20100208223942.6000:__repr__
    #@-others
#@-node:ekr.20100208223942.5996:class PickleShareLink (internal)
#@-others

# if not use_external:
    # Path = path
#@nonl
#@-node:ekr.20100208065621.5894:@thin leoCache.py
#@-leo
