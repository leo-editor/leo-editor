#@+leo-ver=5-thin
#@+node:ekr.20100208065621.5894: * @file leoCache.py
'''A module encapsulating Leo's file caching'''
#@+<< imports >>
#@+node:ekr.20100208223942.10436: ** << imports >> (leoCache)
import sys
isPython3 = sys.version_info >= (3, 0, 0)
import leo.core.leoGlobals as g
import leo.core.leoNodes as leoNodes
if isPython3:
    import pickle
else:
    import cPickle as pickle
# import glob
import fnmatch
import hashlib
import os
import stat
# import time
import zlib
import sqlite3
# try:
    # import marshal
# except ImportError:
    # marshal = None
#@-<< imports >>
# Abbreviations used throughout.
abspath = g.os_path_abspath
basename = g.os_path_basename
expanduser = g.os_path_expanduser
isdir = g.os_path_isdir
isfile = g.os_path_isfile
join = g.os_path_join
normcase = g.os_path_normcase
split = g.os_path_split
SQLITE = True
#@+others
#@+node:ekr.20100208062523.5885: ** class Cacher
class Cacher(object):
    '''A class that encapsulates all aspects of Leo's file caching.'''
    #@+others
    #@+node:ekr.20100208082353.5919: *3* cacher.Birth
    #@+node:ekr.20100208062523.5886: *4* cacher.ctor
    def __init__(self, c=None):
        trace = False and not g.unitTesting
        if trace: g.trace('(Cacher)', c and c.shortFileName() or '<no c>')
        self.c = c
        # set by initFileDB and initGlobalDB...
        self.db = {}
            # When caching is enabled will be a PickleShareDB instance.
        self.dbdirname = None # A string.
        self.globals_tag = 'leo.globals'
            # 'leo3k.globals' if g.isPython3 else 'leo2k.globals'
        self.inited = False
    #@+node:ekr.20100208082353.5918: *4* cacher.initFileDB
    def initFileDB(self, fn):
        trace = False and not g.unitTesting
        if trace: g.trace('inited', self.inited, repr(fn))
        if not fn: return
        pth, bname = split(fn)
        if pth and bname:
            fn = fn.lower()
            fn = g.toEncodedString(fn) # Required for Python 3.x.
            # Important: this creates a top-level directory of the form x_y.
            # x is a short file name, included for convenience.
            # y is a key computed by the *full* path name fn.
            # Thus, there will a separate top-level directory for every path.
            self.dbdirname = dbdirname = join(g.app.homeLeoDir, 'db',
                '%s_%s' % (bname, hashlib.md5(fn).hexdigest()))
            self.db = SqlitePickleShare(dbdirname) if SQLITE else PickleShareDB(dbdirname)
            # Fixes bug 670108.
            self.c.db = self.db
            self.inited = True
            if trace: g.trace('self.c.db', self.db)
    #@+node:ekr.20100208082353.5920: *4* cacher.initGlobalDb
    def initGlobalDB(self):
        trace = False and not g.unitTesting
        # New in Leo 4.10.1.
        # We always create the global db, even if caching is disabled.
        try:
            dbdirname = g.app.homeLeoDir + "/db/global"
            db = SqlitePickleShare(dbdirname) if SQLITE else PickleShareDB(dbdirname)
            self.db = db
            if trace: g.trace(db, dbdirname)
            self.inited = True
            return db
        except Exception:
            return {} # Use a plain dict as a dummy.
    #@+node:ekr.20100210163813.5747: *4* cacher.save
    def save(self, fn, changeName):
        if SQLITE:
            self.commit(True)
        if changeName or not self.inited:
            self.initFileDB(fn)
    #@+node:ekr.20100209160132.5759: *3* cacher.clearCache & clearAllCaches
    def clearCache(self):
        '''Clear the cache for the open window.'''
        if self.db:
            # Be careful about calling db.clear.
            try:
                self.db.clear(verbose=True)
            except TypeError:
                self.db.clear() # self.db is a Python dict.
            except Exception:
                g.trace('unexpected exception')
                g.es_exception()
                self.db = {}

    def clearAllCaches(self):
        '''
        Clear the Cachers *only* for all open windows. This is much safer than
        killing all db's.
        '''
        for frame in g.windows():
            c = frame.c
            if c.cacher:
                c.cacher.clearCache()
        g.es('done', color='blue')
    #@+node:ekr.20100208071151.5907: *3* cacher.fileKey
    def fileKey(self, fileName, content, requireEncodedString=False):
        '''
        Compute the hash of fileName and content. fileName may be unicode,
        content must be bytes (or plain string in Python 2.x).
        '''
        trace = False and not g.unitTesting
        m = hashlib.md5()
        if g.isUnicode(fileName):
            fileName = g.toEncodedString(fileName)
        if g.isUnicode(content):
            if requireEncodedString:
                g.internalError('content arg must be str/bytes')
            content = g.toEncodedString(content)
        # New in Leo 5.6: Use the git branch name in the key.
        branch = g.gitBranchName()
        # g.trace(type(branch), repr(branch))
        branch = g.toEncodedString(branch)
            # Fix #475.
        m.update(branch)
        m.update(fileName)
        m.update(content)
        if trace: g.trace(m.hexdigest())
        return "fcache/" + m.hexdigest()
    #@+node:ekr.20100208082353.5925: *3* cacher.Reading
    #@+node:ekr.20100208071151.5910: *4* cacher.createOutlineFromCacheList & helpers
    def createOutlineFromCacheList(self, parent_v, aList, fileName, top=True):
        '''
        Create outline structure from recursive aList built by makeCacheList.
        '''
        trace = False and not g.unitTesting # and fileName.endswith('leoFileCommands.py')
        c = self.c
        if not c:
            g.internalError('no c')
            return
        if top:
            if trace: g.trace(g.shortFileName(fileName))
            c.cacheListFileName = fileName
        if not aList:
            if trace: g.trace('no list')
            return
        h, b, gnx, children = aList
        if h is not None:
            v = parent_v
            # Does this destroy the ability to handle the rare case?
            v._headString = g.toUnicode(h)
            v._bodyString = g.toUnicode(b)
        for child_tuple in children:
            h, b, gnx, grandChildren = child_tuple
            if trace:
                g.trace('%30s %3s %s' % (gnx, len(grandChildren), h.strip()))
            isClone, child_v = self.fastAddLastChild(fileName, gnx, parent_v)
            if isClone:
                self.checkForChangedNodes(child_tuple, fileName, parent_v)
            else:
                self.createOutlineFromCacheList(child_v, child_tuple, fileName, top=False)
    #@+node:ekr.20170622112151.1: *5* cacher.checkForChangedNodes
    # update_warning_given = False

    def checkForChangedNodes(self, child_tuple, fileName, parent_v):
        '''
        Update the outline described by child_tuple, including all descendants.
        '''
        trace = False and not g.unitTesting
        h, junk_b, gnx, grand_children = child_tuple
        child_v = self.c.fileCommands.gnxDict.get(gnx)
        if child_v:
            self.reportIfNodeChanged(child_tuple, child_v, fileName, parent_v)
            for grand_child in grand_children:
                self.checkForChangedNodes(grand_child, fileName, child_v)
            gnxes_in_cache = set(x[2] for x in grand_children)
            for_removal = [(i, v)
                for i, v in enumerate(child_v.children) 
                if v.gnx not in gnxes_in_cache]
            for i, v in reversed(for_removal):
                v._cutLink(i, child_v)
            #
            # sort children in the order from cache
            for i, grand_child in enumerate(grand_children):
                gnx = grand_child[2]
                child_v.children[i] = self.c.fileCommands.gnxDict.get(gnx)

        else:
            # If the outline is out of sync, there may be write errors later,
            # but the user should be handle them easily enough.
            isClone, child_v = self.fastAddLastChild(fileName, gnx, parent_v)
            self.createOutlineFromCacheList(child_v, child_tuple, fileName, top=False)
            if trace: g.trace('vnode does not exist: %25s %s' % (gnx, h))
            # if not self.update_warning_given: # not needed.
                # self.update_warning_given = True
                # g.internalError('no vnode', child_tuple)
    #@+node:ekr.20100208071151.5911: *5* cacher.fastAddLastChild (sets tempRoots)
    # Similar to createThinChild4

    def fastAddLastChild(self, fileName, gnxString, parent_v):
        '''
        Create new VNode as last child of the receiver.
        If the gnx exists already, create a clone instead of new VNode.
        '''
        trace = 'gnx' in g.app.debug
        c = self.c
        gnxString = g.toUnicode(gnxString)
        gnxDict = c.fileCommands.gnxDict
        if gnxString is None: v = None
        else: v = gnxDict.get(gnxString)
        is_clone = v is not None
        if trace: g.trace(
            'clone', '%-5s' % (is_clone),
            'parent_v', parent_v, 'gnx', gnxString, 'v', repr(v))
        if is_clone:
            # new-read: update tempRoots.
            if not hasattr(v, 'tempRoots'):
                v.tempRoots = set()
            v.tempRoots.add(fileName)
        else:
            if gnxString:
                assert g.isUnicode(gnxString)
                v = leoNodes.VNode(context=c, gnx=gnxString)
                if 'gnx' in g.app.debug:
                    g.trace(c.shortFileName(), gnxString, v)
            else:
                v = leoNodes.VNode(context=c)
                # This is not an error: it can happen with @auto nodes.
                # g.trace('**** no gnx for',v,parent_v)
            # Indicate that this node came from an external file.
            v.tempRoots = set()
            v.tempRoots.add(fileName)
        child_v = v
        child_v._linkAsNthChild(parent_v, parent_v.numberOfChildren())
        child_v.setVisited() # Supress warning/deletion of unvisited nodes.
        return is_clone, child_v
    #@+node:ekr.20100705083838.5740: *5* cacher.reportIfNodeChanged
    def reportIfNodeChanged(self, child_tuple, child_v, fileName, parent_v):
        '''
        Schedule a recovered node if child_v is substantially different from an
        earlier version.

        Issue a (rare) warning if two different files are involved.
        '''
        trace = False and not g.unitTesting
        always_warn = True # True always warn about changed nodes.
        c = self.c
        h, b, gnx, grandChildren = child_tuple
        old_b, new_b = child_v.b, b
        old_h, new_h = child_v.h, h
        # Leo 5.6: test headlines.
        same_head = old_h == new_h
        same_body = (
            old_b == new_b or
            new_b.endswith('\n') and old_b == new_b[: -1] or
            old_b.endswith('\n') and new_b == old_b[: -1]
        )
        if same_head and same_body:
            return
        old_roots = list(getattr(child_v, 'tempRoots', set()))
        same_file = (
            len(old_roots) == 0 or
            len(old_roots) == 1 and old_roots[0] == fileName
        )
        must_warn = not same_file
        if not hasattr(child_v, 'tempRoots'):
            child_v.tempRoots = set()
        child_v.tempRoots.add(fileName)
        if trace:
            # g.trace('same h: %s, same b: %s same fn: %s' % (
                # same_head, same_body, same_file))
            g.trace('fileName', fileName)
            g.trace('tempRoots', old_roots)
        if must_warn:
            # This is the so-called "rare" case:
            # The node differs  in two different external files.
            self.warning('out-of-sync node: %s' % h)
            g.es_print('using node in %s' % fileName)
        if always_warn or must_warn:
            if c.make_node_conflicts_node:
                g.es_print('creating recovered node:', h)
            c.nodeConflictList.append(g.bunch(
                tag='(cached)',
                fileName=fileName,
                gnx=gnx,
                b_old=child_v.b,
                h_old=child_v.h,
                b_new=b,
                h_new=h,
                root_v=parent_v,
            ))
        # Always update the node.
        child_v.h, child_v.b = h, b
        child_v.setDirty()
        c.changed = True # Tell getLeoFile to propegate dirty nodes.
    #@+node:ekr.20100208082353.5923: *4* cacher.getCachedGlobalFileRatios
    def getCachedGlobalFileRatios(self):
        trace = False and not g.unitTesting
        c = self.c
        if not c:
            return g.internalError('no commander')
        key = self.fileKey(c.mFileName, self.globals_tag)
        try:
            ratio = float(self.db.get('body_outline_ratio_%s' % (key), '0.5'))
        except TypeError:
            ratio = 0.5
        try:
            ratio2 = float(self.db.get('body_secondary_ratio_%s' % (key), '0.5'))
        except TypeError:
            ratio2 = 0.5
        if trace:
            g.trace('  %s %1.2f %1.2f' % (c.shortFileName(), ratio, ratio2))
        return ratio, ratio2
    #@+node:ekr.20100208082353.5924: *4* cacher.getCachedStringPosition
    def getCachedStringPosition(self):
        trace = False and not g.unitTesting
        c = self.c
        if not c:
            return g.internalError('no commander')
        key = self.fileKey(c.mFileName, self.globals_tag)
        str_pos = self.db.get('current_position_%s' % key)
        if trace: g.trace(c.shortFileName(), str_pos)
        return str_pos
    #@+node:ekr.20100208082353.5922: *4* cacher.getCachedWindowPositionDict
    def getCachedWindowPositionDict(self, fn):
        '''Return a dict containing window positions.'''
        trace = False and not g.unitTesting
        c = self.c
        if not c:
            g.internalError('no commander')
            return {}
        key = self.fileKey(c.mFileName, self.globals_tag)
        if trace: g.trace(self.db.__class__.__name__)
        data = self.db.get('window_position_%s' % (key))
        # pylint: disable=unpacking-non-sequence
        if data:
            top, left, height, width = data
            top, left, height, width = int(top), int(left), int(height), int(width)
            d = {'top': top, 'left': left, 'height': height, 'width': width}
        else:
            d = {}
        if trace: g.trace(c.shortFileName(), key[-10:], d)
        return d
    #@+node:ekr.20100208071151.5905: *4* cacher.readFile
    def readFile(self, fileName, root):
        '''
        Read the file from the cache if possible.
        Return (s,ok,key)
        '''
        trace = False and not g.unitTesting
        showHits = False
        showLines = False
        showList = False
        sfn = g.shortFileName(fileName)
        if not g.enableDB:
            if trace: g.trace('g.enableDB is False', fileName)
            return '', False, None
        if trace: g.trace('=====', root.v.gnx, 'children', root.numberOfChildren(), fileName)
        s = g.readFileIntoEncodedString(fileName, silent=True)
        if s is None:
            if trace: g.trace('empty file contents', fileName)
            return s, False, None
        assert not g.isUnicode(s)
        if trace and showLines:
            for i, line in enumerate(g.splitLines(s)):
                print('%3d %s' % (i, repr(line)))
        # There will be a bug if s is not already an encoded string.
        key = self.fileKey(fileName, s, requireEncodedString=True)
            # Fix bug #385: use the full fileName, not root.h.
        ok = self.db and key in self.db
        if ok:
            if trace and showHits: g.trace('cache hit', key[-6:], sfn)
            # Delete the previous tree, regardless of the @<file> type.
            while root.hasChildren():
                root.firstChild().doDelete()
            # Recreate the file from the cache.
            aList = self.db.get(key)
            if trace and showList:
                g.printList(list(g.flatten_list(aList)))
            self.createOutlineFromCacheList(root.v, aList, fileName=fileName)
        elif trace:
            g.trace('cache miss', key[-6:], sfn)
        return s, ok, key
    #@+node:ekr.20100208082353.5927: *3* cacher.Writing
    #@+node:ekr.20100208071151.5901: *4* cacher.makeCacheList
    def makeCacheList(self, p):
        '''Create a recursive list describing a tree
        for use by createOutlineFromCacheList.
        '''
        # This is called after at.readPostPass, so p.b *is* the body text.
        return [
            p.h, p.b, p.gnx,
            [self.makeCacheList(p2) for p2 in p.children()]]
    #@+node:ekr.20100208082353.5929: *4* cacher.setCachedGlobalsElement
    def setCachedGlobalsElement(self, fn):
        trace = False and not g.unitTesting
        c = self.c
        if not c:
            return g.internalError('no commander')
        key = self.fileKey(c.mFileName, self.globals_tag)
        self.db['body_outline_ratio_%s' % key] = str(c.frame.ratio)
        self.db['body_secondary_ratio_%s' % key] = str(c.frame.secondary_ratio)
        if trace: g.trace('ratios: %1.2f %1.2f' % (
            c.frame.ratio, c.frame.secondary_ratio))
        width, height, left, top = c.frame.get_window_info()
        self.db['window_position_%s' % key] = (
            str(top), str(left), str(height), str(width))
        if trace:
            g.trace(c.shortFileName(),
                    'top', top, 'left', left,
                    'height', height, 'width', width)
    #@+node:ekr.20100208082353.5928: *4* cacher.setCachedStringPosition
    def setCachedStringPosition(self, str_pos):
        trace = False and not g.unitTesting
        c = self.c
        if not c:
            return g.internalError('no commander')
        key = self.fileKey(c.mFileName, self.globals_tag)
        self.db['current_position_%s' % key] = str_pos
        if trace: g.trace(c.shortFileName(), str_pos)
    #@+node:ekr.20100208071151.5903: *4* cacher.writeFile
    def writeFile(self, p, fileKey):
        '''Update the cache after reading the file.'''
        trace = False and not g.unitTesting
        # Check g.enableDB before giving internal error.
        if not g.enableDB:
            if trace: g.trace('cache disabled')
        elif not fileKey:
            g.trace(g.callers(5))
            g.internalError('empty fileKey')
        elif self.db.get(fileKey):
            if trace: g.trace('already cached', fileKey)
        else:
            if trace: g.trace('caching ', p.h, fileKey)
            self.db[fileKey] = self.makeCacheList(p)
    #@+node:ekr.20100208065621.5890: *3* cacher.test
    def test(self):
        
        # pylint: disable=no-member
        if g.app.gui.guiName() == 'nullGui':
            # Null gui's don't normally set the g.app.gui.db.
            g.app.setGlobalDb()
        # Fixes bug 670108.
        assert g.app.db is not None
            # a PickleShareDB instance.
        # Make sure g.guessExternalEditor works.
        g.app.db.get("LEO_EDITOR")
        self.initFileDB('~/testpickleshare')
        db = self.db
        db.clear()
        assert not list(db.items())
        db['hello'] = 15
        db['aku ankka'] = [1, 2, 313]
        db['paths/nest/ok/keyname'] = [1, (5, 46)]
        db.uncache() # frees memory, causes re-reads later
        if 0: print(db.keys())
        db.clear()
        return True
    #@+node:ekr.20170624135447.1: *3* cacher.warning
    def warning(self, s):
        '''Print a warning message in red.'''
        g.es_print('Warning: %s' % s.lstrip(), color='red')
    #@-others
    def commit(self, close=True):
        # in some cases while unit testing self.db is python dict
        if SQLITE and hasattr(self.db, 'conn'):
            # pylint: disable=no-member
            self.db.conn.commit()
            if close:
                self.db.conn.close()
                self.inited = False
#@+node:ekr.20100208223942.5967: ** class PickleShareDB
_sentinel = object()

class PickleShareDB(object):
    """ The main 'connection' object for PickleShare database """
    #@+others
    #@+node:ekr.20100208223942.5968: *3*  Birth & special methods
    #@+node:ekr.20100208223942.5969: *4*  __init__ (PickleShareDB)
    def __init__(self, root):
        """
        Init the PickleShareDB class.
        root: The directory that contains the data. Created if it doesn't exist.
        """
        trace = False and not g.unitTesting
        self.root = abspath(expanduser(root))
        if trace: g.trace('(PickleShareDB)', self.root)
        if not isdir(self.root) and not g.unitTesting:
            self._makedirs(self.root)
        self.cache = {}
            # Keys are normalized file names.
            # Values are tuples (obj, orig_mod_time)

        def loadz(fileobj):
            if fileobj:
                try:
                    val = pickle.loads(
                        zlib.decompress(fileobj.read()))
                except ValueError:
                    g.es("Unpickling error - Python 3 data accessed from Python 2?")
                    return None
                return val
            else:
                return None

        def dumpz(val, fileobj):
            if fileobj:
                try:
                    # use Python 2's highest protocol, 2, if possible
                    data = pickle.dumps(val, 2)
                except Exception:
                    # but use best available if that doesn't work (unlikely)
                    data = pickle.dumps(val, pickle.HIGHEST_PROTOCOL)
                compressed = zlib.compress(data)
                fileobj.write(compressed)

        self.loader = loadz
        self.dumper = dumpz
    #@+node:ekr.20100208223942.5970: *4* __contains__(PickleShareDB)
    def __contains__(self, key):
        trace = False and g.unitTesting
        if trace: g.trace('(PickleShareDB)', key)
        return self.has_key(key) # NOQA
    #@+node:ekr.20100208223942.5971: *4* __delitem__
    def __delitem__(self, key):
        """ del db["key"] """
        trace = False and not g.unitTesting
        fn = join(self.root, key)
        if trace: g.trace('(PickleShareDB)',
            g.shortFileName(fn))
        self.cache.pop(fn, None)
        try:
            os.remove(fn)
        except OSError:
            # notfound and permission denied are ok - we
            # lost, the other process wins the conflict
            pass
    #@+node:ekr.20100208223942.5972: *4* __getitem__
    def __getitem__(self, key):
        """ db['key'] reading """
        trace = False and not g.unitTesting
        fn = join(self.root, key)
        try:
            mtime = (os.stat(fn)[stat.ST_MTIME])
        except OSError:
            if trace: g.trace('***OSError', fn, key)
            raise KeyError(key)
        if fn in self.cache and mtime == self.cache[fn][1]:
            obj = self.cache[fn][0]
            if trace: g.trace('(PickleShareDB: in cache)', key)
            return obj
        try:
            # The cached item has expired, need to read
            obj = self.loader(self._openFile(fn, 'rb'))
        except Exception:
            if trace: g.trace('***Exception', key)
            raise KeyError(key)
        self.cache[fn] = (obj, mtime)
        if trace: g.trace('(PickleShareDB: set cache)', key)
        return obj
    #@+node:ekr.20100208223942.5973: *4* __iter__
    def __iter__(self):
        trace = False and g.unitTesting
        if trace: g.trace('(PickleShareDB)', list(self.keys()))
        for k in list(self.keys()):
            yield k
    #@+node:ekr.20100208223942.5974: *4* __repr__
    def __repr__(self):
        return "PickleShareDB('%s')" % self.root
    #@+node:ekr.20100208223942.5975: *4* __setitem__
    def __setitem__(self, key, value):
        """ db['key'] = 5 """
        trace = False and not g.unitTesting
        fn = join(self.root, key)
        if trace: g.trace('(PickleShareDB)', key)
        parent, junk = split(fn)
        if parent and not isdir(parent):
            self._makedirs(parent)
        self.dumper(value, self._openFile(fn, 'wb'))
        try:
            mtime = os.path.getmtime(fn)
            self.cache[fn] = (value, mtime)
        except OSError as e:
            if trace: g.trace('***OSError')
            if e.errno != 2:
                raise
    #@+node:ekr.20100208223942.10452: *3* _makedirs
    def _makedirs(self, fn, mode=0o777):
        trace = False and not g.unitTesting
        if trace: g.trace(self.root)
        os.makedirs(fn, mode)
    #@+node:ekr.20100208223942.10458: *3* _openFile
    def _openFile(self, fn, mode='r'):
        """ Open this file.  Return a file object.

        Do not print an error message.
        It is not an error for this to fail.
        """
        try:
            return open(fn, mode)
        except Exception:
            return None
    #@+node:ekr.20100208223942.10454: *3* _walkfiles & helpers
    def _walkfiles(self, s, pattern=None):
        """ D.walkfiles() -> iterator over files in D, recursively.

        The optional argument, pattern, limits the results to files
        with names that match the pattern.  For example,
        mydir.walkfiles('*.tmp') yields only files with the .tmp
        extension.
        """
        for child in self._listdir(s):
            if isfile(child):
                if pattern is None or self._fn_match(child, pattern):
                    yield child
            elif isdir(child):
                for f in self._walkfiles(child, pattern):
                    yield f
    #@+node:ekr.20100208223942.10456: *4* _listdir
    def _listdir(self, s, pattern=None):
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
        return [join(s, child) for child in names]
    #@+node:ekr.20100208223942.10464: *4* _fn_match
    def _fn_match(self, s, pattern):
        """ Return True if self.name matches the given pattern.

        pattern - A filename pattern with wildcards, for example '*.py'.
        """
        return fnmatch.fnmatch(basename(s), pattern)
    #@+node:ekr.20100208223942.5978: *3* clear (PickleShareDB)
    def clear(self, verbose=False):
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
        trace = False and not g.unitTesting
        try:
            val = self[key]
            if trace: g.trace('(PickleShareDB) SUCCESS', key)
            return val
        except KeyError:
            if trace: g.trace('(PickleShareDB) ERROR',  key)
            return default
    #@+node:ekr.20100208223942.5980: *3* has_key (PickleShareDB)
    def has_key(self, key):
        trace = False and g.unitTesting
        if trace: g.trace('(PickleShareDB)', key)
        try:
            self[key]
        except KeyError:
            return False
        return True
    #@+node:ekr.20100208223942.5981: *3* items
    def items(self):
        return [z for z in self]
    #@+node:ekr.20100208223942.5982: *3* keys & helpers (PickleShareDB)
    # Called by clear, and during unit testing.

    def keys(self, globpat=None):
        """Return all keys in DB, or all keys matching a glob"""
        trace = False and not g.unitTesting
        if globpat is None:
            files = self._walkfiles(self.root)
        else:
            # Do not call g.glob_glob here.
            files = [z for z in join(self.root, globpat)]
        result = [self._normalized(p) for p in files if isfile(p)]
        if trace: g.trace('(PickleShareDB)', len(result), result)
        return result
    #@+node:ekr.20100208223942.5976: *4* _normalized
    def _normalized(self, p):
        """ Make a key suitable for user's eyes """
        # os.path.relpath doesn't work here.
        return self._relpathto(self.root, p).replace('\\', '/')
    #@+node:ekr.20100208223942.10460: *4* _relpathto
    # Used only by _normalized.

    def _relpathto(self, src, dst):
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
        if segments:
            return join(*segments)
        else:
            # If they happen to be identical, use os.curdir.
            return os.curdir
    #@+node:ekr.20100208223942.10462: *4* _splitall
    # Used by relpathto.

    def _splitall(self, s):
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
            loc, child = split(prev)
            if loc == prev:
                break
            parts.append(child)
        parts.append(loc)
        parts.reverse()
        return parts
    #@+node:ekr.20100208223942.5989: *3* uncache
    def uncache(self, *items):
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
            self.cache.pop(it, None)
    #@-others
#@+node:vitalije.20170716201700.1: ** class SqlitePickleShare
_sentinel = object()

class SqlitePickleShare(object):
    """ The main 'connection' object for SqlitePickleShare database """
    #@+others
    #@+node:vitalije.20170716201700.2: *3*  Birth & special methods
    def init_dbtables(self, conn):
        sql = 'create table if not exists cachevalues(key text primary key, data blob);'
        conn.execute(sql)
    #@+node:vitalije.20170716201700.3: *4*  __init__ (SqlitePickleShare)
    def __init__(self, root):
        """
        Init the SqlitePickleShare class.
        root: The directory that contains the data. Created if it doesn't exist.
        """
        trace = False and not g.unitTesting
        self.root = abspath(expanduser(root))
        if trace: g.trace('(SqlitePickleShare)', self.root)
        if not isdir(self.root) and not g.unitTesting:
            self._makedirs(self.root)
        dbfile = ':memory:' if g.unitTesting else join(root, 'cache.sqlite')
        self.conn = sqlite3.connect(dbfile, isolation_level=None)
        self.init_dbtables(self.conn)
        self.cache = {}
            # Keys are normalized file names.
            # Values are tuples (obj, orig_mod_time)

        def loadz(data):
            if data:
                try:
                    val = pickle.loads(zlib.decompress(data))
                except (ValueError, TypeError):
                    g.es("Unpickling error - Python 3 data accessed from Python 2?")
                    return None
                return val
            else:
                return None

        def dumpz(val):
            try:
                # use Python 2's highest protocol, 2, if possible
                data = pickle.dumps(val, protocol=2)
            except Exception:
                # but use best available if that doesn't work (unlikely)
                data = pickle.dumps(val, pickle.HIGHEST_PROTOCOL)
            return sqlite3.Binary(zlib.compress(data))

        self.loader = loadz
        self.dumper = dumpz
        if g.isPython3:
            self.reset_protocol_in_values()
    #@+node:vitalije.20170716201700.4: *4* __contains__(SqlitePickleShare)
    def __contains__(self, key):
        trace = False and g.unitTesting
        if trace: g.trace('(PickleShareDB)', key)
        return self.has_key(key) # NOQA
    #@+node:vitalije.20170716201700.5: *4* __delitem__
    def __delitem__(self, key):
        """ del db["key"] """
        try:
            self.conn.execute('''delete from cachevalues
                where key=?''', (key,))
        except sqlite3.OperationalError:
            pass

    #@+node:vitalije.20170716201700.6: *4* __getitem__
    def __getitem__(self, key):
        """ db['key'] reading """
        try:
            obj = None
            for row in self.conn.execute('''select data from cachevalues
                where key=?''', (key,)):
                obj = self.loader(row[0])
                break
            else:
                raise KeyError(key)
        except sqlite3.Error:
            raise KeyError(key)
        return obj
    #@+node:vitalije.20170716201700.7: *4* __iter__
    def __iter__(self):
        trace = False and g.unitTesting
        if trace: g.trace('(SqlitePickleShare)', list(self.keys()))
        for k in list(self.keys()):
            yield k
    #@+node:vitalije.20170716201700.8: *4* __repr__
    def __repr__(self):
        return "SqlitePickleShare('%s')" % self.root
    #@+node:vitalije.20170716201700.9: *4* __setitem__
    def __setitem__(self, key, value):
        """ db['key'] = 5 """
        #trace = False and not g.unitTesting
        try:
            data = self.dumper(value)
            self.conn.execute('''replace into cachevalues(key, data)
                values(?,?);''', (key, data))
        except sqlite3.OperationalError as e:
            g.es_exception(e)

    #@+node:vitalije.20170716201700.10: *3* _makedirs
    def _makedirs(self, fn, mode=0o777):
        trace = False and not g.unitTesting
        if trace: g.trace(self.root)
        os.makedirs(fn, mode)
    #@+node:vitalije.20170716201700.11: *3* _openFile
    def _openFile(self, fn, mode='r'):
        """ Open this file.  Return a file object.

        Do not print an error message.
        It is not an error for this to fail.
        """
        try:
            return open(fn, mode)
        except Exception:
            return None
    #@+node:vitalije.20170716201700.12: *3* _walkfiles & helpers
    def _walkfiles(self, s, pattern=None):
        """ D.walkfiles() -> iterator over files in D, recursively.

        The optional argument, pattern, limits the results to files
        with names that match the pattern.  For example,
        mydir.walkfiles('*.tmp') yields only files with the .tmp
        extension.
        """
        
    #@+node:vitalije.20170716201700.13: *4* _listdir
    def _listdir(self, s, pattern=None):
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
        return [join(s, child) for child in names]
    #@+node:vitalije.20170716201700.14: *4* _fn_match
    def _fn_match(self, s, pattern):
        """ Return True if self.name matches the given pattern.

        pattern - A filename pattern with wildcards, for example '*.py'.
        """
        return fnmatch.fnmatch(basename(s), pattern)
    #@+node:vitalije.20170716201700.15: *3* clear (SqlitePickleShare)
    def clear(self, verbose=False):
        # Deletes all files in the fcache subdirectory.
        # It would be more thorough to delete everything
        # below the root directory, but it's not necessary.
        if verbose:
            g.red('clearing cache at directory...\n')
            g.es_print(self.root)
        self.conn.execute('delete from cachevalues;')
    #@+node:vitalije.20170716201700.16: *3* get
    def get(self, key, default=None):
        trace = False and not g.unitTesting
        if not self.has_key(key):return default
        try:
            val = self[key]
            if trace: g.trace('(SqlitePickleShare) SUCCESS', key)
            return val
        except KeyError:
            if trace: g.trace('(SqlitePickleShare) ERROR',  key)
            return default
    #@+node:vitalije.20170716201700.17: *3* has_key (PickleShareDB)
    def has_key(self, key):
        sql = 'select 1 from cachevalues where key=?;'
        for row in self.conn.execute(sql, (key,)):
            return True
        return False
    #@+node:vitalije.20170716201700.18: *3* items
    def items(self):
        sql = 'select key,data from cachevalues;'
        for key,data in self.conn.execute(sql):
            yield key, data
    #@+node:vitalije.20170716201700.19: *3* keys
    # Called by clear, and during unit testing.

    def keys(self, globpat=None):
        """Return all keys in DB, or all keys matching a glob"""
        if globpat is None:
            sql = 'select key from cachevalues;'
            args = tuple()
        else:
            sql = "select key from cachevalues where key glob ?;"
            # pylint: disable=trailing-comma-tuple
            args = globpat,
        for key in self.conn.execute(sql, args):
            yield key
    #@+node:vitalije.20170818091008.1: *3* reset_protocol_in_values
    def reset_protocol_in_values(self):
        PROTOCOLKEY = '__cache_pickle_protocol__'
        if self.get(PROTOCOLKEY, 3) == 2: return
        #@+others
        #@+node:vitalije.20170818115606.1: *4* viewrendered special case
        import json
        row = self.get('viewrendered_default_layouts') or (None, None)
        row = json.loads(json.dumps(row[0])), json.loads(json.dumps(row[1]))
        self['viewrendered_default_layouts'] = row
        #@+node:vitalije.20170818115617.1: *4* do_block
        def do_block(cur):
            itms = tuple((self.dumper(self.loader(v)), k) for k, v in cur)
            if itms:
                self.conn.executemany('update cachevalues set data=? where key=?', itms)
                self.conn.commit()
                return itms[-1][1]
            return None
        #@-others

        self.conn.isolation_level = 'DEFERRED'

        sql0 = '''select key, data from cachevalues order by key limit 50'''
        sql1 = '''select key, data from cachevalues where key > ? order by key limit 50'''


        block = self.conn.execute(sql0)
        lk = do_block(block)
        while lk:
            lk = do_block(self.conn.execute(sql1, (lk,)))
        self[PROTOCOLKEY] = 2
        self.conn.commit()

        self.conn.isolation_level = None
    #@+node:vitalije.20170716201700.23: *3* uncache
    def uncache(self, *items):
        """not used in SqlitePickleShare"""
        pass
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
