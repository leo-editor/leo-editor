#@+leo-ver=4-thin
#@+node:ekr.20100208065621.5894:@thin leoCache.py
'''A module encapsulating Leo's file caching'''

import leo.core.leoGlobals as g
import leo.external.pickleshare as pickleshare

if 1: # For path.
    import sys,fnmatch,glob,shutil,codecs

import hashlib
import os

#@<< defines (for path only) >>
#@+node:ekr.20100208103105.6114:<< defines (for path only) >>
if g.isPython3:
    _base = str
else:
    _base = unicode

# Universal newline support
_textmode = 'r'
if not g.isPython3:
    if hasattr(file, 'newlines'):
        _textmode = 'U'
#@-node:ekr.20100208103105.6114:<< defines (for path only) >>
#@nl

#@+others
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
        self.trace = False
        self.use_pickleshare = True
    #@-node:ekr.20100208062523.5886: ctor (cacher)
    #@+node:ekr.20100208082353.5918:initFileDB
    def initFileDB (self,fn):

        self.fn = fn

        pth, bname = os.path.split(fn)

        if pth and bname and g.enableDB:
            fn = fn.lower()
            fn = g.toEncodedString(fn) # Required for Python 3.x.

            # dbdirname = '%s/db/%s_%s' % (
                # g.app.homeLeoDir,bname,hashlib.md5(fn).hexdigest())

            dbdirname = g.os_path_join(g.app.homeLeoDir,'db',
                '%s_%s' % (bname,hashlib.md5(fn).hexdigest()))

            # Use compressed pickles (handy for @thin caches)
            self.db = pickleshare.PickleShareDB(
                dbdirname,protocol='picklez')
    #@-node:ekr.20100208082353.5918:initFileDB
    #@+node:ekr.20100208082353.5920:initGlobalDb
    def initGlobalDB (self):

        if g.enableDB:
            dbdirname = self.homeLeoDir + "/db/global"
            self.db = pickleshare.PickleShareDB(dbdirname, protocol='picklez')
            if trace: g.trace(self.db,dbdirname)
        else:
            self.db = {}
    #@-node:ekr.20100208082353.5920:initGlobalDb
    #@+node:ekr.20100208065621.5893:createGlobalDb
    def setGlobalDb(self):

        '''Create the database bound to g.app.db'''

        trace = False
        if trace: g.trace('g.enableDB',g.enableDB)

        if g.enableDB:
            dbdirname = self.homeLeoDir + "/db/global"
            self.db = pickleshare.PickleShareDB(dbdirname, protocol='picklez')
            if trace: g.trace(self.db,dbdirname)
        else:
            self.db = {}
    #@-node:ekr.20100208065621.5893:createGlobalDb
    #@-node:ekr.20100208082353.5919: Birth
    #@+node:ekr.20100208071151.5910:createOutlineFromCacheList & helpers
    def createOutlineFromCacheList(self,parent_v,c,aList,top=True,atAll=None,fileName=None):

        """ Create outline structure from recursive aList
        built by makeCacheList.

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
    #@+node:ekr.20100208082353.5925:Reading
    #@+node:ekr.20100208082353.5924:getCachedStringPosition
    def getCachedStringPosition(self):

        c = self.c

        if not c:
            return g.internalError('no commander')

        globals_tag = g.choose(g.isPython3,'leo3k.globals','leo2k.globals')
        key = self.fileKey(c.mFileName,globals_tag)
        str_pos = self.db.get('current_position_%s' % key)

        if trace: g.trace(str_pos,key)
        return str_pos
    #@-node:ekr.20100208082353.5924:getCachedStringPosition
    #@+node:ekr.20100208082353.5923:getCachedGlobalFileRatios
    def getCachedGlobalFileRatios (self):

        trace = False and not g.unitTesting
        c = self.c

        if not c:
            return g.internalError('no commander')

        globals_tag = g.choose(g.isPython3,'leo3k.globals','leo2k.globals')
        key = self.fileKey(c.mFileName,globals_tag)

        ratio  = float(self.db.get('body_outline_ratio_%s' % (key),'0.5'))
        ratio2 = float(self.db.get('body_secondary_ratio_%s' % (key),'0.5'))

        if trace:
            g.trace('key',key,'%1.2f %1.2f' % (ratio,ratio2))

        return ratio,ratio2
    #@-node:ekr.20100208082353.5923:getCachedGlobalFileRatios
    #@+node:ekr.20100208082353.5922:getCachedWindowPositionDict
    def getCachedWindowPositionDict (self):

        c = self.c

        if not c:
            g.internalError('no commander')
            return {}


        globals_tag = g.choose(g.isPython3,'leo3k.globals','leo2k.globals')
        key = self.fileKey(c.mFileName,globals_tag)
        data = self.db.get('window_position_%s' % (key))

        if data:
            top,left,height,width = data
            top,left,height,width = int(top),int(left),int(height),int(width)
            d = {'top':top,'left':left,'height':height,'width':width}
        else:
            d = {}
    #@-node:ekr.20100208082353.5922:getCachedWindowPositionDict
    #@+node:ekr.20100208071151.5905:readFile
    # was atFile.readFromCache
    # Same code as atFile.readFromCache
    # Same code as code in atFile.readOneAtAutoNode

    def readFile (self,fileName,root):

        c = self.c

        if not g.enableDB:
            return False,None

        s,e = g.readFileIntoString(fileName,raw=True)
        if s is None: return False,None

        key = self.fileKey(root.h,s)
        ok = key in self.db
        if ok:
            # Delete the previous tree, regardless of the @<file> type.
            while root.hasChildren():
                root.firstChild().doDelete()
            # Recreate the file from the cache.
            aList = self.db[cachefile]
            root.v.createOutlineFromCacheList(c,aList,fileName=fileName)
            at.inputFile.close()
            root.clearDirty()

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
            [self.makeCacheList() for p2 in p.children()]]
    #@-node:ekr.20100208071151.5901:makeCacheList
    #@+node:ekr.20100208082353.5929:setCachedGlobalsElement
    def setCachedGlobalsElement(self):

        trace = False and not g.unitTesting
        c = self.c

        if not c:
            return g.internalError('no commander')

        globals_tag = g.choose(g.isPython3,'leo3k.globals','leo2k.globals')
        key = self.fileKey(c.mFileName,globals_tag)
        if trace: g.trace(len(list(self.db.keys())),c.mFileName,key)

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
        key = self.fileKey(c.mFileName,globals_tag)
        self.db['current_position_%s' % key] = str_pos

        if trace: g.trace(str_pos,key)
    #@-node:ekr.20100208082353.5928:setCachedStringPosition
    #@+node:ekr.20100208071151.5903:writeFile
    # Was atFile.writeCachedTree

    def writeFile(self,p,fileKey):

        trace = False and not g.unitTesting
        c = self.c

        if not g.enableDB:
            if trace: g.trace('cache disabled')
        elif fileKey in self.db:
            if trace: g.trace('already cached',fileKey)
        else:
            if trace: g.trace('caching ',p.h)
            self.db[fileKey] = self.makeCacheList(p)
    #@nonl
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
#@+node:ekr.20100208103105.6115:class path
class path(_base):
    """
    Represents a filesystem path. Example::

        from path import path
        d = path('/home/guido/bin')
        for f in d.files('*.py'):
            f.chmod(0755)

    For documentation on individual methods,
    consult their counterparts in os.path.
    """

    #@    @+others
    #@+node:ekr.20100208103105.6116:Special methods
    def __repr__(self):
        return 'path(%s)' % _base.__repr__(self)

    # Adding a path and a string yields a path.
    def __add__(self, more):
        return path(_base(self) + more)

    def __radd__(self, other):
        return path(other + _base(self))

    # The / operator joins paths.
    def __div__(self, rel):
        """ fp.__div__(rel) == fp / rel == fp.joinpath(rel)

        Join two path components, adding a separator character if
        needed.
        """
        # 2010/02/04 EKR: fix for Python 3.x.
        if rel is None: rel = ''
        return path(os.path.join(self, rel))

    # Make the / operator work even when true division is enabled.
    __truediv__ = __div__
    #@-node:ekr.20100208103105.6116:Special methods
    #@+node:ekr.20100208103105.6117:getcwd
    def getcwd():
        """ Return the current working directory as a path object. """
        return path(os.getcwd())

    getcwd = staticmethod(getcwd)
    #@-node:ekr.20100208103105.6117:getcwd
    #@+node:ekr.20100208103105.6118:path strings...
    #@+node:ekr.20100208103105.6119:abspath

    # --- Operations on path strings.

    def abspath(self):       return path(os.path.abspath(self))
    #@-node:ekr.20100208103105.6119:abspath
    #@+node:ekr.20100208103105.6120:normcase
    def normcase(self):
        return path(os.path.normcase(self))
    #@-node:ekr.20100208103105.6120:normcase
    #@+node:ekr.20100208103105.6121:normpath
    def normpath(self):
        return path(os.path.normpath(self))
    #@-node:ekr.20100208103105.6121:normpath
    #@+node:ekr.20100208103105.6122:realpath
    def realpath(self):
        return path(os.path.realpath(self))
    #@-node:ekr.20100208103105.6122:realpath
    #@+node:ekr.20100208103105.6123:expanduser
    def expanduser(self):
        return path(os.path.expanduser(self))
    #@-node:ekr.20100208103105.6123:expanduser
    #@+node:ekr.20100208103105.6124:expandvars
    def expandvars(self):
        return path(os.path.expandvars(self))
    #@-node:ekr.20100208103105.6124:expandvars
    #@+node:ekr.20100208103105.6125:dirname
    def dirname(self):
        return path(os.path.dirname(self))
    #@-node:ekr.20100208103105.6125:dirname
    #@+node:ekr.20100208103105.6126:expand
    basename = os.path.basename

    def expand(self):
        """ Clean up a filename by calling expandvars(),
        expanduser(), and normpath() on it.

        This is commonly everything needed to clean up a filename
        read from a configuration file, for example.
        """
        return self.expandvars().expanduser().normpath()
    #@-node:ekr.20100208103105.6126:expand
    #@+node:ekr.20100208103105.6127:_get_namebase
    def _get_namebase(self):

        base, ext = os.path.splitext(self.name)
        return base

    #@-node:ekr.20100208103105.6127:_get_namebase
    #@+node:ekr.20100208103105.6128:_get_ext
    def _get_ext(self):
        f, ext = os.path.splitext(_base(self))
        return ext

    #@-node:ekr.20100208103105.6128:_get_ext
    #@+node:ekr.20100208103105.6129:_get_drive
    def _get_drive(self):
        drive, r = os.path.splitdrive(self)
        return path(drive)
    #@-node:ekr.20100208103105.6129:_get_drive
    #@+node:ekr.20100208103105.6130:splitpath
    parent = property(
        dirname, None, None,
        """ This path's parent directory, as a new path object.

        For example, path('/usr/local/lib/libpython.so').parent == path('/usr/local/lib')
        """)

    name = property(
        basename, None, None,
        """ The name of this file or directory without the full path.

        For example, path('/usr/local/lib/libpython.so').name == 'libpython.so'
        """)

    namebase = property(
        _get_namebase, None, None,
        """ The same as path.name, but with one file extension stripped off.

        For example, path('/home/guido/python.tar.gz').name     == 'python.tar.gz',
        but          path('/home/guido/python.tar.gz').namebase == 'python.tar'
        """)

    ext = property(
        _get_ext, None, None,
        """ The file extension, for example '.py'. """)

    drive = property(
        _get_drive, None, None,
        """ The drive specifier, for example 'C:'.
        This is always empty on systems that don't use drive specifiers.
        """)

    def splitpath(self):
        """ p.splitpath() -> Return (p.parent, p.name). """
        parent, child = os.path.split(self)
        return path(parent), child

    #@-node:ekr.20100208103105.6130:splitpath
    #@+node:ekr.20100208103105.6131:splitdrive
    def splitdrive(self):
        """ p.splitdrive() -> Return (p.drive, <the rest of p>).

        Split the drive specifier from this path.  If there is
        no drive specifier, p.drive is empty, so the return value
        is simply (path(''), p).  This is always the case on Unix.
        """
        drive, rel = os.path.splitdrive(self)
        return path(drive), rel

    #@-node:ekr.20100208103105.6131:splitdrive
    #@+node:ekr.20100208103105.6132:splitext
    def splitext(self):
        """ p.splitext() -> Return (p.stripext(), p.ext).

        Split the filename extension from this path and return
        the two parts.  Either part may be empty.

        The extension is everything from '.' to the end of the
        last path segment.  This has the property that if
        (a, b) == p.splitext(), then a + b == p.
        """
        filename, ext = os.path.splitext(self)
        return path(filename), ext

    #@-node:ekr.20100208103105.6132:splitext
    #@+node:ekr.20100208103105.6133:stripext
    def stripext(self):
        """ p.stripext() -> Remove one file extension from the path.

        For example, path('/home/guido/python.tar.gz').stripext()
        returns path('/home/guido/python.tar').
        """
        return self.splitext()[0]

    #@-node:ekr.20100208103105.6133:stripext
    #@+node:ekr.20100208103105.6134:splitunc
    if hasattr(os.path, 'splitunc'):
        def splitunc(self):
            unc, rest = os.path.splitunc(self)
            return path(unc), rest

        def _get_uncshare(self):
            unc, r = os.path.splitunc(self)
            return path(unc)

        uncshare = property(
            _get_uncshare, None, None,
            """ The UNC mount point for this path.
            This is empty for paths on local drives. """)

    #@-node:ekr.20100208103105.6134:splitunc
    #@+node:ekr.20100208103105.6135:joinpath
    def joinpath(self, *args):
        """ Join two or more path components, adding a separator
        character (os.sep) if needed.  Returns a new path
        object.
        """
        return path(os.path.join(self, *args))

    #@-node:ekr.20100208103105.6135:joinpath
    #@+node:ekr.20100208103105.6136:splitall
    def splitall(self):
        """ Return a list of the path components in this path.

        The first item in the list will be a path.  Its value will be
        either os.curdir, os.pardir, empty, or the root directory of
        this path (for example, '/' or 'C:\\').  The other items in
        the list will be strings.

        path.path.joinpath(*result) will yield the original path.
        """
        parts = []
        loc = self
        while loc != os.curdir and loc != os.pardir:
            prev = loc
            loc, child = prev.splitpath()
            if loc == prev:
                break
            parts.append(child)
        parts.append(loc)
        parts.reverse()
        return parts

    #@-node:ekr.20100208103105.6136:splitall
    #@+node:ekr.20100208103105.6137:relpath
    def relpath(self):
        """ Return this path as a relative path,
        based from the current working directory.
        """
        cwd = path(os.getcwd())
        return cwd.relpathto(self)

    #@-node:ekr.20100208103105.6137:relpath
    #@+node:ekr.20100208103105.6138:relpathto
    def relpathto(self, dest):
        """ Return a relative path from self to dest.

        If there is no relative path from self to dest, for example if
        they reside on different drives in Windows, then this returns
        dest.abspath().
        """
        origin = self.abspath()
        dest = path(dest).abspath()

        orig_list = origin.normcase().splitall()
        # Don't normcase dest!  We want to preserve the case.
        dest_list = dest.splitall()

        if orig_list[0] != os.path.normcase(dest_list[0]):
            # Can't get here from there.
            return dest

        # Find the location where the two paths start to differ.
        i = 0
        for start_seg, dest_seg in zip(orig_list, dest_list):
            if start_seg != os.path.normcase(dest_seg):
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
            return path(os.curdir)
        else:
            return path(os.path.join(*segments))


    #@-node:ekr.20100208103105.6138:relpathto
    #@-node:ekr.20100208103105.6118:path strings...
    #@+node:ekr.20100208103105.6139:Listing, searching, walking, matching
    #@+node:ekr.20100208103105.6140:listdir
    def listdir(self, pattern=None):
        """ D.listdir() -> List of items in this directory.

        Use D.files() or D.dirs() instead if you want a listing
        of just files or just subdirectories.

        The elements of the list are path objects.

        With the optional 'pattern' argument, this only lists
        items whose names match the given pattern.
        """
        names = os.listdir(self)
        if pattern is not None:
            names = fnmatch.filter(names, pattern)
        return [self / child for child in names]

    #@-node:ekr.20100208103105.6140:listdir
    #@+node:ekr.20100208103105.6141:dirs
    def dirs(self, pattern=None):
        """ D.dirs() -> List of this directory's subdirectories.

        The elements of the list are path objects.
        This does not walk recursively into subdirectories
        (but see path.walkdirs).

        With the optional 'pattern' argument, this only lists
        directories whose names match the given pattern.  For
        example, d.dirs('build-*').
        """
        return [p for p in self.listdir(pattern) if p.isdir()]

    #@-node:ekr.20100208103105.6141:dirs
    #@+node:ekr.20100208103105.6142:files
    def files(self, pattern=None):
        """ D.files() -> List of the files in this directory.

        The elements of the list are path objects.
        This does not walk into subdirectories (see path.walkfiles).

        With the optional 'pattern' argument, this only lists files
        whose names match the given pattern.  For example,
        d.files('*.pyc').
        """

        return [p for p in self.listdir(pattern) if p.isfile()]

    #@-node:ekr.20100208103105.6142:files
    #@+node:ekr.20100208103105.6143:walk
    def walk(self, pattern=None):
        """ D.walk() -> iterator over files and subdirs, recursively.

        The iterator yields path objects naming each child item of
        this directory and its descendants.  This requires that
        D.isdir().

        This performs a depth-first traversal of the directory tree.
        Each directory is returned just before all its children.
        """
        for child in self.listdir():
            if pattern is None or child.fnmatch(pattern):
                yield child
            if child.isdir():
                for item in child.walk(pattern):
                    yield item

    #@-node:ekr.20100208103105.6143:walk
    #@+node:ekr.20100208103105.6144:walkdirs
    def walkdirs(self, pattern=None):
        """ D.walkdirs() -> iterator over subdirs, recursively.

        With the optional 'pattern' argument, this yields only
        directories whose names match the given pattern.  For
        example, mydir.walkdirs('*test') yields only directories
        with names ending in 'test'.
        """
        for child in self.dirs():
            if pattern is None or child.fnmatch(pattern):
                yield child
            for subsubdir in child.walkdirs(pattern):
                yield subsubdir

    #@-node:ekr.20100208103105.6144:walkdirs
    #@+node:ekr.20100208103105.6145:walkfiles
    def walkfiles(self, pattern=None):
        """ D.walkfiles() -> iterator over files in D, recursively.

        The optional argument, pattern, limits the results to files
        with names that match the pattern.  For example,
        mydir.walkfiles('*.tmp') yields only files with the .tmp
        extension.
        """
        for child in self.listdir():
            if child.isfile():
                if pattern is None or child.fnmatch(pattern):
                    yield child
            elif child.isdir():
                for f in child.walkfiles(pattern):
                    yield f

    #@-node:ekr.20100208103105.6145:walkfiles
    #@+node:ekr.20100208103105.6146:fnmatch
    def fnmatch(self, pattern):
        """ Return True if self.name matches the given pattern.

        pattern - A filename pattern with wildcards,
            for example '*.py'.
        """
        return fnmatch.fnmatch(self.name, pattern)

    #@-node:ekr.20100208103105.6146:fnmatch
    #@+node:ekr.20100208103105.6147:glob
    def glob(self, pattern):
        """ Return a list of path objects that match the pattern.

        pattern - a path relative to this directory, with wildcards.

        For example, path('/users').glob('*/bin/*') returns a list
        of all the files users have in their bin directories.
        """
        return map(path, glob.glob(_base(self / pattern)))


    #@-node:ekr.20100208103105.6147:glob
    #@-node:ekr.20100208103105.6139:Listing, searching, walking, matching
    #@+node:ekr.20100208103105.6148:Reading or writing and entire file
    #@+node:ekr.20100208103105.6149:open
    def open(self, mode='r'):
        """ Open this file.  Return a file object. """
        # 2010/02/04 EKR: catch exception so Leo doesn't crash on startup.
        try:
            return open(self, mode)
        except Exception:
            print('can not open',self)
            return None
    #@-node:ekr.20100208103105.6149:open
    #@+node:ekr.20100208103105.6150:bytes
    def bytes(self):
        """ Open this file, read all bytes, return them as a string. """
        f = self.open('rb')
        try:
            return f.read()
        finally:
            f.close()

    #@-node:ekr.20100208103105.6150:bytes
    #@+node:ekr.20100208103105.6151:write_bytes
    def write_bytes(self, bytes, append=False):
        """ Open this file and write the given bytes to it.

        Default behavior is to overwrite any existing file.
        Call this with write_bytes(bytes, append=True) to append instead.
        """
        if append:
            mode = 'ab'
        else:
            mode = 'wb'
        f = self.open(mode)
        try:
            f.write(bytes)
        finally:
            f.close()

    #@-node:ekr.20100208103105.6151:write_bytes
    #@+node:ekr.20100208103105.6152:text
    def text(self, encoding=None, errors='strict'):
        """ Open this file, read it in, return the content as a string.

        This uses 'U' mode in Python 2.3 and later, so '\r\n' and '\r'
        are automatically translated to '\n'.

        Optional arguments:

        encoding - The Unicode encoding (or character set) of
            the file.  If present, the content of the file is
            decoded and returned as a unicode object; otherwise
            it is returned as an 8-bit str.
        errors - How to handle Unicode errors; see help(str.decode)
            for the options.  Default is 'strict'.
        """
        if encoding is None:
            # 8-bit
            f = self.open(_textmode)
            try:
                return f.read()
            finally:
                f.close()
        else:
            # Unicode
            f = codecs.open(self, 'r', encoding, errors)
            # (Note - Can't use 'U' mode here, since codecs.open
            # doesn't support 'U' mode, even in Python 2.3.)
            try:
                t = f.read()
            finally:
                f.close()

            if g.isPython3:
                f = str
            else:
                f = unicode

            return (
                t.replace(f('\r\n'), f('\n')).
                replace(f('\r\x85'), f('\n')).
                replace(f('\r'), f('\n')).
                replace(f('\x85'), f('\n')).
                replace(f('\u2028'), f('\n'))
            )
    #@-node:ekr.20100208103105.6152:text
    #@+node:ekr.20100208103105.6153:write_text
    def write_text(self, text, encoding=None, errors='strict', linesep=os.linesep, append=False):
        """ Write the given text to this file.

        The default behavior is to overwrite any existing file;
        to append instead, use the 'append=True' keyword argument.

        There are two differences between path.write_text() and
        path.write_bytes(): newline handling and Unicode handling.
        See below.

        Parameters:

          - text - str/unicode - The text to be written.

          - encoding - str - The Unicode encoding that will be used.
            This is ignored if 'text' isn't a Unicode string.

          - errors - str - How to handle Unicode encoding errors.
            Default is 'strict'.  See help(unicode.encode) for the
            options.  This is ignored if 'text' isn't a Unicode
            string.

          - linesep - keyword argument - str/unicode - The sequence of
            characters to be used to mark end-of-line.  The default is
            os.linesep.  You can also specify None; this means to
            leave all newlines as they are in 'text'.

          - append - keyword argument - bool - Specifies what to do if
            the file already exists (True: append to the end of it;
            False: overwrite it.)  The default is False.


        --- Newline handling.

        write_text() converts all standard end-of-line sequences
        ('\n', '\r', and '\r\n') to your platform's default end-of-line
        sequence (see os.linesep; on Windows, for example, the
        end-of-line marker is '\r\n').

        If you don't like your platform's default, you can override it
        using the 'linesep=' keyword argument.  If you specifically want
        write_text() to preserve the newlines as-is, use 'linesep=None'.

        This applies to Unicode text the same as to 8-bit text, except
        there are three additional standard Unicode end-of-line sequences:
        u'\x85', u'\r\x85', and u'\u2028'.

        (This is slightly different from when you open a file for
        writing with fopen(filename, "w") in C or file(filename, 'w')
        in Python.)


        --- Unicode

        If 'text' isn't Unicode, then apart from newline handling, the
        bytes are written verbatim to the file.  The 'encoding' and
        'errors' arguments are not used and must be omitted.

        If 'text' is Unicode, it is first converted to bytes using the
        specified 'encoding' (or the default encoding if 'encoding'
        isn't specified).  The 'errors' argument applies only to this
        conversion.

        """
        if isinstance(text, unicode):
            if linesep is not None:
                # Convert all standard end-of-line sequences to
                # ordinary newline characters.
                text = (
                    text.replace(f('\r\n'), f('\n')).
                    replace(f('\r\x85'), f('\n')).
                    replace(f('\r'), f('\n')).
                    replace(f('\x85'), f('\n')).
                    replace(f('\u2028'), f('\n'))
                )
                text = text.replace(f('\n'),linesep)
            if encoding is None:
                encoding = sys.getdefaultencoding()
            bytes = text.encode(encoding, errors)
        else:
            # It is an error to specify an encoding if 'text' is
            # an 8-bit string.
            assert encoding is None

            if linesep is not None:
                text = (text.replace('\r\n', '\n')
                            .replace('\r', '\n'))
                bytes = text.replace('\n', linesep)

        self.write_bytes(bytes, append)

    #@-node:ekr.20100208103105.6153:write_text
    #@+node:ekr.20100208103105.6154:lines
    def lines(self, encoding=None, errors='strict', retain=True):
        """ Open this file, read all lines, return them in a list.

        Optional arguments:
            encoding - The Unicode encoding (or character set) of
                the file.  The default is None, meaning the content
                of the file is read as 8-bit characters and returned
                as a list of (non-Unicode) str objects.
            errors - How to handle Unicode errors; see help(str.decode)
                for the options.  Default is 'strict'
            retain - If true, retain newline characters; but all newline
                character combinations ('\r', '\n', '\r\n') are
                translated to '\n'.  If false, newline characters are
                stripped off.  Default is True.

        This uses 'U' mode in Python 2.3 and later.
        """
        if encoding is None and retain:
            f = self.open(_textmode)
            try:
                return f.readlines()
            finally:
                f.close()
        else:
            return self.text(encoding, errors).splitlines(retain)

    #@-node:ekr.20100208103105.6154:lines
    #@+node:ekr.20100208103105.6155:write_lines
    def write_lines(self, lines, encoding=None, errors='strict',
                    linesep=os.linesep, append=False):
        """ Write the given lines of text to this file.

        By default this overwrites any existing file at this path.

        This puts a platform-specific newline sequence on every line.
        See 'linesep' below.

        lines - A list of strings.

        encoding - A Unicode encoding to use.  This applies only if
            'lines' contains any Unicode strings.

        errors - How to handle errors in Unicode encoding.  This
            also applies only to Unicode strings.

        linesep - The desired line-ending.  This line-ending is
            applied to every line.  If a line already has any
            standard line ending ('\r', '\n', '\r\n', u'\x85',
            u'\r\x85', u'\u2028'), that will be stripped off and
            this will be used instead.  The default is os.linesep,
            which is platform-dependent ('\r\n' on Windows, '\n' on
            Unix, etc.)  Specify None to write the lines as-is,
            like file.writelines().

        Use the keyword argument append=True to append lines to the
        file.  The default is to overwrite the file.  Warning:
        When you use this with Unicode data, if the encoding of the
        existing data in the file is different from the encoding
        you specify with the encoding= parameter, the result is
        mixed-encoding data, which can really confuse someone trying
        to read the file later.
        """
        if append:
            mode = 'ab'
        else:
            mode = 'wb'
        f = self.open(mode)
        try:
            for line in lines:
                isUnicode = isinstance(line, unicode)
                if linesep is not None:
                    # Strip off any existing line-end and add the
                    # specified linesep string.
                    if g.isPython3:
                        f = str
                    else:
                        f = unicode
                    if isUnicode:
                        if line[-2:] in (
                            f('\r\n'), f('\x0d\x85')
                        ):
                            line = line[:-2]
                        elif line[-1:] in (
                            f('\r'), f('\n'),f('\x85'), f('\u2028')
                        ):
                            line = line[:-1]
                    else:
                        if line[-2:] == '\r\n':
                            line = line[:-2]
                        elif line[-1:] in ('\r', '\n'):
                            line = line[:-1]
                    line += linesep
                if isUnicode:
                    if encoding is None:
                        encoding = sys.getdefaultencoding()
                    line = line.encode(encoding, errors)
                f.write(line)
        finally:
            f.close()


    #@-node:ekr.20100208103105.6155:write_lines
    #@-node:ekr.20100208103105.6148:Reading or writing and entire file
    #@+node:ekr.20100208103105.6156:Querying the file system
    #@+node:ekr.20100208103105.6157:access
    # --- Methods for querying the filesystem.

    exists = os.path.exists
    isabs = os.path.isabs
    isdir = os.path.isdir
    isfile = os.path.isfile
    islink = os.path.islink
    ismount = os.path.ismount

    if hasattr(os.path, 'samefile'):
        samefile = os.path.samefile

    getatime = os.path.getatime
    atime = property(
        getatime, None, None,
        """ Last access time of the file. """)

    getmtime = os.path.getmtime
    mtime = property(
        getmtime, None, None,
        """ Last-modified time of the file. """)

    if hasattr(os.path, 'getctime'):
        getctime = os.path.getctime
        ctime = property(
            getctime, None, None,
            """ Creation time of the file. """)

    getsize = os.path.getsize
    size = property(
        getsize, None, None,
        """ Size of the file, in bytes. """)

    if hasattr(os, 'access'):
        def access(self, mode):
            """ Return true if current user has access to this path.

            mode - One of the constants os.F_OK, os.R_OK, os.W_OK, os.X_OK
            """
            return os.access(self, mode)

    #@-node:ekr.20100208103105.6157:access
    #@+node:ekr.20100208103105.6158:stat
    def stat(self):
        """ Perform a stat() system call on this path. """
        return os.stat(self)

    #@-node:ekr.20100208103105.6158:stat
    #@+node:ekr.20100208103105.6159:lstat
    def lstat(self):
        """ Like path.stat(), but do not follow symbolic links. """
        return os.lstat(self)

    #@-node:ekr.20100208103105.6159:lstat
    #@+node:ekr.20100208103105.6160:statvfs
    if hasattr(os, 'statvfs'):
        def statvfs(self):
            """ Perform a statvfs() system call on this path. """
            return os.statvfs(self)

    #@-node:ekr.20100208103105.6160:statvfs
    #@+node:ekr.20100208103105.6161:pathconf
    if hasattr(os, 'pathconf'):
        def pathconf(self, name):
            return os.pathconf(self, name)


    #@-node:ekr.20100208103105.6161:pathconf
    #@-node:ekr.20100208103105.6156:Querying the file system
    #@+node:ekr.20100208103105.6162:Modifying files and directories
    #@+node:ekr.20100208103105.6163:utime
    # --- Modifying operations on files and directories

    def utime(self, times):
        """ Set the access and modified times of this file. """
        os.utime(self, times)

    #@-node:ekr.20100208103105.6163:utime
    #@+node:ekr.20100208103105.6164:chmod
    def chmod(self, mode):
        os.chmod(self, mode)

    #@-node:ekr.20100208103105.6164:chmod
    #@+node:ekr.20100208103105.6165:chown
    if hasattr(os, 'chown'):
        def chown(self, uid, gid):
            os.chown(self, uid, gid)

    #@-node:ekr.20100208103105.6165:chown
    #@+node:ekr.20100208103105.6166:rename
    def rename(self, new):
        os.rename(self, new)

    #@-node:ekr.20100208103105.6166:rename
    #@+node:ekr.20100208103105.6167:renames
    def renames(self, new):
        os.renames(self, new)


    #@-node:ekr.20100208103105.6167:renames
    #@-node:ekr.20100208103105.6162:Modifying files and directories
    #@+node:ekr.20100208103105.6168:Create/delete directories
    #@+node:ekr.20100208103105.6169:mkdir
    # --- Create/delete operations on directories

    def mkdir(self, mode=0o777):
        os.mkdir(self, mode)

    #@-node:ekr.20100208103105.6169:mkdir
    #@+node:ekr.20100208103105.6170:makedirs
    def makedirs(self, mode=0o777):
        os.makedirs(self, mode)

    #@-node:ekr.20100208103105.6170:makedirs
    #@+node:ekr.20100208103105.6171:rmdir
    def rmdir(self):
        os.rmdir(self)

    #@-node:ekr.20100208103105.6171:rmdir
    #@+node:ekr.20100208103105.6172:removedirs
    def removedirs(self):
        os.removedirs(self)


    #@-node:ekr.20100208103105.6172:removedirs
    #@-node:ekr.20100208103105.6168:Create/delete directories
    #@+node:ekr.20100208103105.6173:Modifying files
    #@+node:ekr.20100208103105.6174:touch
    # --- Modifying operations on files

    def touch(self):
        """ Set the access/modified times of this file to the current time.
        Create the file if it does not exist.
        """
        fd = os.open(self, os.O_WRONLY | os.O_CREAT, 0o666)
        os.close(fd)
        os.utime(self, None)

    #@-node:ekr.20100208103105.6174:touch
    #@+node:ekr.20100208103105.6175:remove
    def remove(self):
        os.remove(self)

    #@-node:ekr.20100208103105.6175:remove
    #@+node:ekr.20100208103105.6176:unlink
    def unlink(self):
        os.unlink(self)


    #@-node:ekr.20100208103105.6176:unlink
    #@-node:ekr.20100208103105.6173:Modifying files
    #@+node:ekr.20100208103105.6177:Links...
    #@+node:ekr.20100208103105.6178:link
    # --- Links

    if hasattr(os, 'link'):
        def link(self, newpath):
            """ Create a hard link at 'newpath', pointing to this file. """
            os.link(self, newpath)

    #@-node:ekr.20100208103105.6178:link
    #@+node:ekr.20100208103105.6179:symlink
    if hasattr(os, 'symlink'):
        def symlink(self, newlink):
            """ Create a symbolic link at 'newlink', pointing here. """
            os.symlink(self, newlink)

    #@-node:ekr.20100208103105.6179:symlink
    #@+node:ekr.20100208103105.6180:readlink
    if hasattr(os, 'readlink'):
        def readlink(self):
            """ Return the path to which this symbolic link points.

            The result may be an absolute or a relative path.
            """
            return path(os.readlink(self))

        def readlinkabs(self):
            """ Return the path to which this symbolic link points.

            The result is always an absolute path.
            """
            p = self.readlink()
            if p.isabs():
                return p
            else:
                return (self.parent / p).abspath()


    #@-node:ekr.20100208103105.6180:readlink
    #@-node:ekr.20100208103105.6177:Links...
    #@+node:ekr.20100208103105.6181:High-level operations from shutil
    #@+node:ekr.20100208103105.6182:chroot
    # --- High-level functions from shutil

    copyfile = shutil.copyfile
    copymode = shutil.copymode
    copystat = shutil.copystat
    copy = shutil.copy
    copy2 = shutil.copy2
    copytree = shutil.copytree
    if hasattr(shutil, 'move'):
        move = shutil.move
    rmtree = shutil.rmtree


    # --- Special stuff from os

    if hasattr(os, 'chroot'):
        def chroot(self):
            os.chroot(self)

    #@-node:ekr.20100208103105.6182:chroot
    #@+node:ekr.20100208103105.6183:startfile
    if hasattr(os, 'startfile'):
        def startfile(self):
            os.startfile(self)

    #@-node:ekr.20100208103105.6183:startfile
    #@-node:ekr.20100208103105.6181:High-level operations from shutil
    #@-others
#@-node:ekr.20100208103105.6115:class path
#@+node:ekr.20100208103105.5992:class PickleShareDB
_sentinel = object()

class PickleShareDB:
    """ The main 'connection' object for PickleShare database """
    #@    @+others
    #@+node:ekr.20100208103105.5993: __init__
    def __init__(self,root, protocol = 'pickle'):
        """ Initialize a PickleShare object that will manage the specied directory

        root: The directory that contains the data. Created if it doesn't exist.

        protocol: one of 

            * 'pickle' (universal, default) 
            * 'picklez' (compressed pickle)         
            * 'marshal' (fast, limited type support)
            * 'json' : brief, human-readable, very limited type support

        Protol 'json' requires installation of simplejson module
        """
        ### self.root = Path(root).expanduser().abspath()
        self.root = g.os_path_expanduser(g.os_path_abspath(root))

        ### if not self.root.isdir():
        if not g.os_path_isdir(self.root):
            ### self.root.makedirs()
            os.makedirs(self.root,mode=0o777)

        # cache has { 'key' : (obj, orig_mod_time) }
        self.cache = {}

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
    #@-node:ekr.20100208103105.5993: __init__
    #@+node:ekr.20100208103105.5994:__contains__
    def __contains__(self, key):

        return self.has_key(key)
    #@-node:ekr.20100208103105.5994:__contains__
    #@+node:ekr.20100208103105.5995:__delitem__
    def __delitem__(self,key):

        """ del db["key"] """

        ### fil = self.root / key
        fil = g.os_path_join(self.root,key)
        # g.trace('(PickleShareDB)',key) # ,g.shortFileName(fil))
        self.cache.pop(fil,None)
        try:
            fil.remove()
        except OSError:
            # notfound and permission denied are ok - we
            # lost, the other process wins the conflict
            pass
    #@-node:ekr.20100208103105.5995:__delitem__
    #@+node:ekr.20100208103105.5996:__getitem__
    def __getitem__(self,key):

        """ db['key'] reading """

        ### fil = self.root / key
        fil = g.os_path_join(self.root,key)
        # g.trace('(PickleShareDB)',key) #,g.shortFileName(fil))
        try:
            mtime = (fil.stat()[stat.ST_MTIME])
        except OSError:
            raise KeyError(key)

        if fil in self.cache and mtime == self.cache[fil][1]:
            return self.cache[fil][0]
        try:
            # The cached item has expired, need to read
            obj = self.loader(fil.open("rb"))
        except:
            raise KeyError(key)

        self.cache[fil] = (obj,mtime)
        return obj
    #@-node:ekr.20100208103105.5996:__getitem__
    #@+node:ekr.20100208103105.5997:__iter__
    def __iter__(self):

        for k in list(self.keys()):
            yield k
    #@-node:ekr.20100208103105.5997:__iter__
    #@+node:ekr.20100208103105.5998:__repr__
    def __repr__(self):

        return "PickleShareDB('%s')" % self.root



    #@-node:ekr.20100208103105.5998:__repr__
    #@+node:ekr.20100208103105.5999:__setitem__
    def __setitem__(self,key,value):

        """ db['key'] = 5 """

        fil = self.root / key
        parent = fil.parent
        ### if parent and not parent.isdir():
            ### parent.makedirs()

        if parent and not g.os_path_isdir(parent):
            os.makedirs(parent,mode=0o777)

        pickled = self.dumper(value,fil.open('wb'))
        # g.trace('(PickleShareDB)',key) # ,g.shortFileName(fil))
        try:
            self.cache[fil] = (value,fil.mtime)
        except OSError as e:
            if e.errno != 2:
                raise

    #@-node:ekr.20100208103105.5999:__setitem__
    #@+node:ekr.20100208103105.6000:_normalized
    def _normalized(self, p):
        """ Make a key suitable for user's eyes """
        return str(self.root.relpathto(p)).replace('\\','/')

    #@-node:ekr.20100208103105.6000:_normalized
    #@+node:ekr.20100208103105.6001:get
    def get(self, key, default=''): # EKR: default was None.
        try:
            return self[key]
        except KeyError:
            return default
    #@nonl
    #@-node:ekr.20100208103105.6001:get
    #@+node:ekr.20100208103105.6002:getlink
    def getlink(self,folder):
        """ Get a convenient link for accessing items  """
        return PickleShareLink(self, folder)

    #@-node:ekr.20100208103105.6002:getlink
    #@+node:ekr.20100208103105.6003:has_key
    def has_key(self, key):

        try:
            value = self[key]
        except KeyError:
            return False

        return True
    #@-node:ekr.20100208103105.6003:has_key
    #@+node:ekr.20100208103105.6004:hcompress
    def hcompress(self, hashroot):
        """ Compress category 'hashroot', so hset is fast again

        hget will fail if fast_only is True for compressed items (that were
        hset before hcompress).

        """
        hfiles = self.keys(hashroot + "/*")
        all = {}
        for f in hfiles:
            # print("using",f)
            all.update(self[f])
            self.uncache(f)

        self[hashroot + '/xx'] = all
        for f in hfiles:
            p = self.root / f
            if p.basename() == 'xx':
                continue
            p.remove()



    #@-node:ekr.20100208103105.6004:hcompress
    #@+node:ekr.20100208103105.6005:hdict
    def hdict(self, hashroot):
        """ Get all data contained in hashed category 'hashroot' as dict """
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
    #@-node:ekr.20100208103105.6005:hdict
    #@+node:ekr.20100208103105.6006:hget
    def hget(self, hashroot, key, default = _sentinel, fast_only = True):
        """ hashed get """
        hroot = self.root / hashroot
        hfile = hroot / gethashfile(key)
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
    #@nonl
    #@-node:ekr.20100208103105.6006:hget
    #@+node:ekr.20100208103105.6007:hset
    def hset(self, hashroot, key, value):
        """ hashed set """
        hroot = self.root / hashroot

        ### if not hroot.isdir():
            ### hroot.makedirs()
        if not g.os_path_isdir(hroot):
            os.makedirs(hroot,mode=0o777)

        hfile = hroot / gethashfile(key)
        d = self.get(hfile, {})
        d.update( {key : value})
        self[hfile] = d                



    #@-node:ekr.20100208103105.6007:hset
    #@+node:ekr.20100208103105.6008:iteritems & iterkeys
    def iteritems(self):
        for k in self:
            yield (k, self[k])

    def iterkeys(self):
        return self.__iter__()
    #@-node:ekr.20100208103105.6008:iteritems & iterkeys
    #@+node:ekr.20100208103105.6009:keys
    def keys(self, globpat = None):
        """ All keys in DB, or all keys matching a glob"""

        if globpat is None:
            ### files = self.root.walkfiles()
            files = self.walkfiles(self.root)
        else:
            ### files = [Path(p) for p in glob.glob(self.root/globpat)]
            files = glob.glob(g.os_path_join(self.root,globpat))

        return [self._normalized(p) for p in files if p.isfile()]

    #@-node:ekr.20100208103105.6009:keys
    #@+node:ekr.20100208103105.6010:uncache
    def uncache(self,*items):
        """ Removes all, or specified items from cache

        Use this after reading a large amount of large objects
        to free up memory, when you won't be needing the objects
        for a while.

        """
        if not items:
            self.cache = {}
        for it in items:
            self.cache.pop(it,None)

    #@-node:ekr.20100208103105.6010:uncache
    #@+node:ekr.20100208103105.6011:waitget
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
    #@-node:ekr.20100208103105.6011:waitget
    #@-others
#@-node:ekr.20100208103105.5992:class PickleShareDB
#@+node:ekr.20100208103105.6017:class PickleShareLink
class PickleShareLink:
    """ A shortdand for accessing nested PickleShare data conveniently.

    Created through PickleShareDB.getlink(), example::

        lnk = db.getlink('myobjects/test')
        lnk.foo = 2
        lnk.bar = lnk.foo + 5

    """
    #@    @+others
    #@+node:ekr.20100208103105.6018:__init__
    def __init__(self, db, keydir ):

        self.__dict__.update(locals())
    #@-node:ekr.20100208103105.6018:__init__
    #@+node:ekr.20100208103105.6019:__getattr__
    def __getattr__(self,key):

        return self.__dict__['db'][self.__dict__['keydir']+'/' + key]
    #@-node:ekr.20100208103105.6019:__getattr__
    #@+node:ekr.20100208103105.6020:__setattr__
    def __setattr__(self,key,val):
        self.db[self.keydir+'/' + key] = val
    #@-node:ekr.20100208103105.6020:__setattr__
    #@+node:ekr.20100208103105.6021:__repr__
    def __repr__(self):
        db = self.__dict__['db']
        keys = db.keys( self.__dict__['keydir'] +"/*")
        return "<PickleShareLink '%s': %s>" % (
            self.__dict__['keydir'],
            ";".join([Path(k).basename() for k in keys]))


    #@-node:ekr.20100208103105.6021:__repr__
    #@-others
#@-node:ekr.20100208103105.6017:class PickleShareLink
#@+node:ekr.20100208103105.6029:path methods referenced by pickleShare
if 0:
    #@    @+others
    #@+node:ekr.20100208103105.6030:(done) makedirs
    def makedirs(self, mode=0o777):
        os.makedirs(self, mode)

    #@-node:ekr.20100208103105.6030:(done) makedirs
    #@+node:ekr.20100208103105.6031:(done) expanduser
    def expanduser(self):
        return path(os.path.expanduser(self))
    #@-node:ekr.20100208103105.6031:(done) expanduser
    #@+node:ekr.20100208103105.6032:abspath

    # --- Operations on path strings.

    def abspath(self):       return path(os.path.abspath(self))
    #@-node:ekr.20100208103105.6032:abspath
    #@+node:ekr.20100208103105.6033:__div__
    # The / operator joins paths.
    def __div__(self, rel):
        """ fp.__div__(rel) == fp / rel == fp.joinpath(rel)

        Join two path components, adding a separator character if
        needed.
        """
        # 2010/02/04 EKR: fix for Python 3.x.
        if rel is None: rel = ''
        return path(os.path.join(self, rel))
    #@nonl
    #@-node:ekr.20100208103105.6033:__div__
    #@+node:ekr.20100208103105.6034:walkfiles
    def walkfiles(self, pattern=None):
        """ D.walkfiles() -> iterator over files in D, recursively.

        The optional argument, pattern, limits the results to files
        with names that match the pattern.  For example,
        mydir.walkfiles('*.tmp') yields only files with the .tmp
        extension.
        """
        for child in self.listdir():
            if child.isfile():
                if pattern is None or child.fnmatch(pattern):
                    yield child
            elif child.isdir():
                for f in child.walkfiles(pattern):
                    yield f

    #@-node:ekr.20100208103105.6034:walkfiles
    #@+node:ekr.20100208103105.6035:splitpath
    # parent = property(
        # dirname, None, None,
        # """ This path's parent directory, as a new path object.

        # For example, path('/usr/local/lib/libpython.so').parent == path('/usr/local/lib')
        # """)

    # name = property(
        # basename, None, None,
        # """ The name of this file or directory without the full path.

        # For example, path('/usr/local/lib/libpython.so').name == 'libpython.so'
        # """)

    # namebase = property(
        # _get_namebase, None, None,
        # """ The same as path.name, but with one file extension stripped off.

        # For example, path('/home/guido/python.tar.gz').name     == 'python.tar.gz',
        # but          path('/home/guido/python.tar.gz').namebase == 'python.tar'
        # """)

    # ext = property(
        # _get_ext, None, None,
        # """ The file extension, for example '.py'. """)

    # drive = property(
        # _get_drive, None, None,
        # """ The drive specifier, for example 'C:'.
        # This is always empty on systems that don't use drive specifiers.
        # """)

    # def splitpath(src):
        # """ p.splitpath() -> Return (p.parent, p.name). """
        # parent, child = os.path.split(src)
        # return path(parent), child
    #@-node:ekr.20100208103105.6035:splitpath
    #@-others


#@-node:ekr.20100208103105.6029:path methods referenced by pickleShare
#@-others
#@nonl
#@-node:ekr.20100208065621.5894:@thin leoCache.py
#@-leo
