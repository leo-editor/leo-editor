#@+leo-ver=5-thin
#@+node:ekr.20100208065621.5894: * @file leoCache.py
'''A module encapsulating Leo's file caching'''

#@+<< imports >>
#@+node:ekr.20100208223942.10436: ** << imports >> (leoCache)
import sys
isPython3 = sys.version_info >= (3,0,0)

import leo.core.leoGlobals as g
import leo.core.leoNodes as leoNodes

if isPython3:
    import pickle
else:
    import cPickle as pickle

import glob
import fnmatch
import hashlib
import os
import stat
# import time
import zlib

# try:
    # import marshal
# except ImportError:
    # marshal = None
#@-<< imports >>

# Abbreviations used throughout.
abspath     = g.os_path_abspath
basename    = g.os_path_basename
expanduser  = g.os_path_expanduser
isdir       = g.os_path_isdir
isfile      = g.os_path_isfile
join        = g.os_path_join
normcase    = g.os_path_normcase
split       = g.os_path_split

#@+others
#@+node:ekr.20100208062523.5885: ** class cacher
class cacher:

    '''A class that encapsulates all aspects of Leo's file caching.'''

    #@+others
    #@+node:ekr.20100208082353.5919: *3*  Birth (cacher)
    #@+node:ekr.20100208062523.5886: *4*  ctor (cacher)
    def __init__ (self,c=None):

        trace = False and not g.unitTesting
        if trace: g.trace('cacher','c',c)

        self.c = c

        # set by initFileDB and initGlobalDB...
        self.db = {}
            # 2011/07/30
            # When caching is enabled will be a PickleShareDB instance.
        self.dbdirname = None # A string.
        self.inited = False

    #@+node:ekr.20100208082353.5918: *4* initFileDB
    def initFileDB (self,fn):

        trace = False and not g.unitTesting
        if trace: g.trace('inited',self.inited,repr(fn))

        if not fn: return

        pth, bname = split(fn)

        if pth and bname: ### and g.enableDB:
            fn = fn.lower()
            fn = g.toEncodedString(fn) # Required for Python 3.x.

            # Important: this creates a top-level directory of the form x_y.
            # x is a short file name, included for convenience.
            # y is a key computed by the *full* path name fn.
            # Thus, there will a separate top-level directory for every path.
            self.dbdirname = dbdirname = join(g.app.homeLeoDir,'db',
                '%s_%s' % (bname,hashlib.md5(fn).hexdigest()))

            self.db = PickleShareDB(dbdirname)
            # Fixes bug 670108.
            self.c.db = self.db
            self.inited = True

            if trace: g.trace('self.c.db',self.db)
    #@+node:ekr.20100208082353.5920: *4* initGlobalDb
    def initGlobalDB (self):

        trace = False and not g.unitTesting

        # New in Leo 4.10.1.
        # We always create the global db, even if caching is disabled.
        try:
            dbdirname = g.app.homeLeoDir + "/db/global"
            self.db = db = PickleShareDB(dbdirname)
            if trace: g.trace(db,dbdirname)
            self.inited = True
            return db
        except Exception:
            return {} # Use a plain dict as a dummy.
    #@+node:ekr.20100210163813.5747: *4* save (cacher)
    def save (self,fn,changeName):

        if changeName or not self.inited:
            self.initFileDB(fn)
    #@+node:ekr.20100209160132.5759: *3* clear/AllCache(s) (cacher)
    def clearCache (self):
        if self.db:
            # 2011/07/30: Be careful about calling db.clear.
            try:
                self.db.clear(verbose=True)
            except TypeError:
                self.db.clear() # self.db is a Python dict.
            except Exception:
                g.trace('unexpected exception')
                g.es_exception()
                self.db = {}

    def clearAllCaches (self):

        # Clear the cachers *only* for all open windows.
        # This is much safer than tryting to Kill all db's.
        for frame in g.windows():
            c = frame.c
            if c.cacher:
                c.cacher.clearCache()
    #@+node:ekr.20100208071151.5907: *3* fileKey
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
    #@+node:ekr.20100208082353.5925: *3* Reading
    #@+node:ekr.20100208071151.5910: *4* cacher.createOutlineFromCacheList & helpers
    def createOutlineFromCacheList(self,parent_v,aList,fileName,top=True):

        """ Create outline structure from recursive aList
        built by makeCacheList."""

        trace = False and not g.unitTesting
        verbose = False
        c = self.c
        if not c:
            g.internalError('no c')

        if top:
            if trace and verbose: g.trace(fileName)
            c.cacheListFileName = fileName

        h,b,gnx,children = aList
        if h is not None:
            v = parent_v
            v._headString = h    
            v._bodyString = b

        for z in children:
            h,b,gnx,grandChildren = z
            isClone,child_v = self.fastAddLastChild(parent_v,gnx)

            if isClone:
                self.reportChangedClone(child_v,b,h,gnx)
            else:
                self.createOutlineFromCacheList(
                    child_v,z,fileName,top=False)
    #@+node:ekr.20100208071151.5911: *5* casher.fastAddLastChild
    # Similar to createThinChild4
    def fastAddLastChild(self,parent_v,gnxString):
        '''Create new vnode as last child of the receiver.

        If the gnx exists already, create a clone instead of new vnode.
        '''

        trace = False and not g.unitTesting
        c = self.c
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
            else:
                g.trace('**** no gnx for',v)
        child_v = v
        child_v._linkAsNthChild(parent_v,parent_v.numberOfChildren())
        child_v.setVisited() # Supress warning/deletion of unvisited nodes.
        return is_clone,child_v
    #@+node:ekr.20100705083838.5740: *5* casher.reportChangedClone
    def reportChangedClone (self,child_v,b,h,gnx):

        trace = False and not g.unitTesting
        c = self.c
        fileName=c.cacheListFileName
        old,new = child_v.b,b

        same = (
            old == new or
            new.endswith('\n') and old == new[:-1] or
            old.endswith('\n') and new == old[:-1])

        # if trace and not same:
        if trace and (not same or h == 'writeException'):
            g.trace('same %s old %s new %s %s %s' % (
                same,len(old),len(new),h,fileName))

        # This would make it impossible to clear nodes!
        # if not new: return same

        if same: return

        c.nodeConflictList.append(g.bunch(
            tag='(cached)',
            fileName=fileName,
            gnx=gnx,
            b_old=child_v.b,
            h_old=child_v.h,
            b_new=b,
            h_new=h,
        ))

        # Always issue the warning.
        g.error("cached read node changed:",child_v.h)

        child_v.h,child_v.b = h,b
        child_v.setDirty()
        c.changed = True # Tell getLeoFile to propegate dirty nodes.
    #@+node:ekr.20100208082353.5923: *4* getCachedGlobalFileRatios
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
    #@+node:ekr.20100208082353.5924: *4* getCachedStringPosition
    def getCachedStringPosition(self):

        trace = False and not g.unitTesting
        c = self.c

        if not c:
            return g.internalError('no commander')

        globals_tag = g.choose(g.isPython3,'leo3k.globals','leo2k.globals')
        # globals_tag = g.toEncodedString(globals_tag,'ascii')

        key = self.fileKey(c.mFileName,globals_tag)
        str_pos = self.db.get('current_position_%s' % key)

        if trace: g.trace(str_pos,key)
        return str_pos
    #@+node:ekr.20100208082353.5922: *4* getCachedWindowPositionDict
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
    #@+node:ekr.20100208071151.5905: *4* readFile (cacher)
    def readFile (self,fileName,root):

        trace = False and not g.unitTesting
        verbose = True
        if not g.enableDB:
            if trace: g.trace('g.enableDB is False')
            return '',False,None
        s,e = g.readFileIntoString(fileName,raw=True,silent=True)
        if s is None:
            if trace: g.trace('empty file contents',fileName)
            return s,False,None
        assert not g.isUnicode(s)
        if trace and verbose:
            for i,line in enumerate(g.splitLines(s)):
                print('%3d %s' % (i,repr(line)))

        # There will be a bug if s is not already an encoded string.
        key = self.fileKey(root.h,s,requireEncodedString=True)
        ok = self.db and key in self.db
        if trace: g.trace('in cache',ok,fileName,key)
        if ok:
            # Delete the previous tree, regardless of the @<file> type.
            while root.hasChildren():
                root.firstChild().doDelete()
            # Recreate the file from the cache.
            aList = self.db.get(key)
            self.createOutlineFromCacheList(root.v,aList,fileName=fileName)
        return s,ok,key
    #@+node:ekr.20100208082353.5927: *3* Writing
    #@+node:ekr.20100208071151.5901: *4* makeCacheList
    def makeCacheList(self,p):

        '''Create a recursive list describing a tree
        for use by createOutlineFromCacheList.
        '''

        # This is called after at.copyAllTempBodyStringsToVnodes,
        # so p.b *is* the body text.

        return [
            p.h,p.b,p.gnx,
            [self.makeCacheList(p2) for p2 in p.children()]]
    #@+node:ekr.20100208082353.5929: *4* setCachedGlobalsElement
    def setCachedGlobalsElement(self,fn):

        trace = False and not g.unitTesting
        c = self.c

        if not c:
            return g.internalError('no commander')

        globals_tag = g.choose(g.isPython3,'leo3k.globals','leo2k.globals')
        key = self.fileKey(fn,globals_tag)

        if trace: g.trace(c.mFileName,key,g.callers(5))

        self.db['body_outline_ratio_%s' % key] = str(c.frame.ratio)
        self.db['body_secondary_ratio_%s' % key] = str(c.frame.secondary_ratio)
        if trace: g.trace('ratios: %1.2f %1.2f' % (
            c.frame.ratio,c.frame.secondary_ratio))

        width,height,left,top = c.frame.get_window_info()

        self.db['window_position_%s' % key] = (
            str(top),str(left),str(height),str(width))
        if trace:
            g.trace('top',top,'left',left,'height',height,'width',width)
    #@+node:ekr.20100208082353.5928: *4* setCachedStringPosition
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
    #@+node:ekr.20100208071151.5903: *4* writeFile (cacher)
    # Was atFile.writeCachedTree

    def writeFile(self,p,fileKey):

        trace = False and not g.unitTesting

        # Bug fix: 2010/05/26: check g.enableDB before giving internal error.
        if not g.enableDB:
            if trace: g.trace('cache disabled')
        elif not fileKey:
            g.trace(g.callers(5))
            g.internalError('empty fileKey')
        elif self.db.get(fileKey):
            if trace: g.trace('already cached',fileKey)
        else:
            if trace: g.trace('caching ',p.h,fileKey)
            self.db[fileKey] = self.makeCacheList(p)
    #@+node:ekr.20100208065621.5890: *3* test (cacher)
    def test(self):

        if g.app.gui.guiName() == 'nullGui':
            # Null gui's don't normally set the g.app.gui.db.
            g.app.setGlobalDb() 

        # Fixes bug 670108.
        assert g.app.db is not None
            # a PickleShareDB instance.

        # Make sure g.guessExternalEditor works.
        junk = g.app.db.get("LEO_EDITOR")

        self.initFileDB('~/testpickleshare')
        db = self.db
        db.clear()
        assert not list(db.items())
        db['hello'] = 15
        db['aku ankka'] = [1,2,313]
        db['paths/nest/ok/keyname'] = [1,(5,46)]
        db.uncache() # frees memory, causes re-reads later
        if 0: print(db.keys())
        db.clear()
        return True
    #@-others
#@+node:ekr.20100208223942.5967: ** class PickleShareDB
_sentinel = object()

class PickleShareDB:

    """ The main 'connection' object for PickleShare database """

    #@+others
    #@+node:ekr.20100208223942.5968: *3*  Birth & special methods
    #@+node:ekr.20100208223942.5969: *4*  __init__ (PickleShareDb)
    def __init__(self,root):

        """
        Init the PickleShareDB class.
        root: The directory that contains the data. Created if it doesn't exist.
        """

        trace = False and not g.unitTesting

        self.root = abspath(expanduser(root))

        if trace: g.trace('PickleShareDB',self.root)

        if not isdir(self.root) and not g.unitTesting:
            self._makedirs(self.root)

        self.cache = {}
            # Keys are normalized file names.
            # Values are tuples (obj, orig_mod_time)

        def loadz(fileobj):
            if fileobj:
                val = pickle.loads(
                    zlib.decompress(fileobj.read()))
                return val
            else:
                return None

        def dumpz(val, fileobj):
            if fileobj:
                compressed = zlib.compress(pickle.dumps(
                    val, pickle.HIGHEST_PROTOCOL))
                fileobj.write(compressed)

        self.loader = loadz
        self.dumper = dumpz
    #@+node:ekr.20100208223942.5970: *4* __contains__
    def __contains__(self, key):

        trace = False and g.unitTesting

        if trace: g.trace('(PickleShareDB)',key)

        return self.has_key(key)
    #@+node:ekr.20100208223942.5971: *4* __delitem__
    def __delitem__(self,key):

        """ del db["key"] """

        trace = False and not g.unitTesting

        fn = join(self.root,key)

        if trace: g.trace('(PickleShareDB)',
            g.shortFileName(fn))

        self.cache.pop(fn,None)

        try:
            os.remove(fn)
        except OSError:
            # notfound and permission denied are ok - we
            # lost, the other process wins the conflict
            pass
    #@+node:ekr.20100208223942.5972: *4* __getitem__
    def __getitem__(self,key):

        """ db['key'] reading """

        trace = False and not g.unitTesting

        fn = join(self.root,key)
        try:
            mtime = (os.stat(fn)[stat.ST_MTIME])
        except OSError:
            if trace: g.trace('***OSError',fn,key)
            raise KeyError(key)

        if fn in self.cache and mtime == self.cache[fn][1]:
            obj = self.cache[fn][0]
            if trace: g.trace('(PickleShareDB: in cache)',key)
            return obj
        try:
            # The cached item has expired, need to read
            obj = self.loader(self._openFile(fn,'rb'))
        except Exception:
            if trace: g.trace('***Exception',key)
            raise KeyError(key)

        self.cache[fn] = (obj,mtime)
        if trace: g.trace('(PickleShareDB: set cache)',key)
        return obj
    #@+node:ekr.20100208223942.5973: *4* __iter__
    def __iter__(self):

        trace = False and g.unitTesting

        if trace: g.trace('(PickleShareDB)',list(self.keys()))

        for k in list(self.keys()):
            yield k
    #@+node:ekr.20100208223942.5974: *4* __repr__
    def __repr__(self):

        return "PickleShareDB('%s')" % self.root



    #@+node:ekr.20100208223942.5975: *4* __setitem__
    def __setitem__(self,key,value):

        """ db['key'] = 5 """

        trace = False and not g.unitTesting
        fn = join(self.root,key)

        if trace: g.trace('(PickleShareDB)',key)
        parent,junk = split(fn)

        if parent and not isdir(parent):
            self._makedirs(parent)

        self.dumper(value,self._openFile(fn,'wb'))

        try:
            mtime = os.path.getmtime(fn)
            self.cache[fn] = (value,mtime)
        except OSError as e:
            if trace: g.trace('***OSError')
            if e.errno != 2:
                raise
    #@+node:ekr.20100208223942.10452: *3* _makedirs
    def _makedirs(self,fn,mode=0o777):

        trace = False and not g.unitTesting
        if trace: g.trace(self.root)

        os.makedirs(fn,mode)

    #@+node:ekr.20100208223942.10458: *3* _openFile
    def _openFile(self,fn, mode='r'):

        """ Open this file.  Return a file object.

        Do not print an error message.
        It is not an error for this to fail. 
        """

        try:
            return open(fn, mode)
        except Exception:
            return None
    #@+node:ekr.20100208223942.10454: *3* _walkfiles & helpers
    def _walkfiles(self,s, pattern=None):

        """ D.walkfiles() -> iterator over files in D, recursively.

        The optional argument, pattern, limits the results to files
        with names that match the pattern.  For example,
        mydir.walkfiles('*.tmp') yields only files with the .tmp
        extension.
        """

        for child in self._listdir(s):
            if isfile(child):
                if pattern is None or self._fn_match(child,pattern):
                    yield child
            elif isdir(child):
                for f in self._walkfiles(child,pattern):
                    yield f

    #@+node:ekr.20100208223942.10456: *4* _listdir
    def _listdir(self,s, pattern=None):

        """ D.listdir() -> List of items in this directory.

        Use D.files() or D.dirs() instead if you want a listing
        of just files or just subdirectories.

        The elements of the list are path objects.

        With the optional 'pattern' argument, this only lists
        items whose names match the given pattern.
        """

        names = os.listdir(s)

        if pattern is not None:
            names = fnmatch.filter(names, pattern)

        return [join(s,child) for child in names]

    #@+node:ekr.20100208223942.10464: *4* _fn_match
    def _fn_match(self,s, pattern):
        """ Return True if self.name matches the given pattern.

        pattern - A filename pattern with wildcards, for example '*.py'.
        """

        return fnmatch.fnmatch(basename(s), pattern)

    #@+node:ekr.20100208223942.5978: *3* clear
    def clear (self,verbose=False):

        # Deletes all files in the fcache subdirectory.
        # It would be more thorough to delete everything
        # below the root directory, but it's not necessary.

        if verbose:
            g.red('clearing cache at directory...\n')
            g.es_print(self.root)

        for z in self.keys():
            self.__delitem__(z)
    #@+node:ekr.20100208223942.5979: *3* get
    def get(self, key, default=None):

        trace = False and g.unitTesting
        if trace: g.trace('(PickleShareDB)')

        try:
            return self[key]
        except KeyError:
            return default
    #@+node:ekr.20100208223942.5980: *3* has_key
    def has_key(self, key):

        trace = False and g.unitTesting
        if trace: g.trace('(PickleShareDB)',key)
        try:
            self[key]
        except KeyError:
            return False
        return True
    #@+node:ekr.20100208223942.5981: *3* items
    def items(self):
        return [z for z in self]
    #@+node:ekr.20100208223942.5982: *3* keys & helpers
    # Called by clear, and during unit testing.

    def keys(self, globpat = None):

        """Return all keys in DB, or all keys matching a glob"""

        trace = False and not g.unitTesting

        if globpat is None:
            files = self._walkfiles(self.root)
        else:
            files = [z for z in glob.glob(join(self.root,globpat))]

        result = [self._normalized(p) for p in files if isfile(p)]

        if trace: g.trace('(PickleShareDB)',len(result),result)

        return result
    #@+node:ekr.20100208223942.5976: *4* _normalized
    def _normalized(self, p):
        """ Make a key suitable for user's eyes """

        # os.path.relpath doesn't work here.

        return self._relpathto(self.root,p).replace('\\','/')

    #@+node:ekr.20100208223942.10460: *4* _relpathto
    # Used only by _normalized.

    def _relpathto(self,src, dst):

        """ Return a relative path from self to dst.

        If there is no relative path from self to dst, for example if
        they reside on different drives in Windows, then this returns
        dst.abspath().
        """

        origin = abspath(src)
        dst = abspath(dst)
        orig_list = self._splitall(normcase(origin))
        # Don't normcase dst!  We want to preserve the case.
        dest_list = self._splitall(dst)

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
            return os.curdir
        else:
            return join(*segments)
    #@+node:ekr.20100208223942.10462: *4* _splitall
    # Used by relpathto.

    def _splitall(self,s):
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
            loc,child = split(prev)
            if loc == prev:
                break
            parts.append(child)
        parts.append(loc)
        parts.reverse()
        return parts

    #@+node:ekr.20100208223942.5989: *3* uncache
    def uncache(self,*items):
        """ Removes all, or specified items from cache

        Use this after reading a large amount of large objects
        to free up memory, when you won't be needing the objects
        for a while.

        """

        trace = False and not g.unitTesting
        if trace: g.trace()

        if not items:
            self.cache = {}
        for it in items:
            self.cache.pop(it,None)

    #@-others
#@-others
#@-leo
