#!/usr/bin/env python
#@+leo-ver=4-thin
#@+node:ekr.20100207111939.5895:@thin ../external/pickleshare.py
#@@first
#@@language python
#@@tabwidth -4
#@<< docstring >>
#@+node:ekr.20091204141748.6178:<< docstring >>
""" PickleShare - a small 'shelve' like datastore with concurrency support

Like shelve, a PickleShareDB object acts like a normal dictionary. Unlike 
shelve, many processes can access the database simultaneously. Changing a 
value in database is immediately visible to other processes accessing the 
same database.

Concurrency is possible because the values are stored in separate files. Hence
the "database" is a directory where *all* files are governed by PickleShare.

Example usage::

    from pickleshare import *
    db = PickleShareDB('~/testpickleshare')
    db.clear()
    print("Should be empty:",db.items())
    db['hello'] = 15
    db['aku ankka'] = [1,2,313]
    db['paths/are/ok/key'] = [1,(5,46)]
    print(db.keys())
    del db['aku ankka']

This module is certainly not ZODB, but can be used for low-load 
(non-mission-critical) situations where tiny code size trumps the 
advanced features of a "real" object database.

Installation guide: easy_install pickleshare

Author: Ville M. Vainio <vivainio@gmail.com>
License: MIT open source license.

"""
#@-node:ekr.20091204141748.6178:<< docstring >>
#@nl
#@<< imports >>
#@+node:ekr.20091204132346.6078:<< imports >> (pickleshare.py)
try:
    import leo.core.leoGlobals as g
except ImportError:
    pass

try:
    from leo.external.path import path as Path
except ImportError:
    import path as Path

import glob
import os
import stat
import sys
import time
import warnings

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
#@-node:ekr.20091204132346.6078:<< imports >> (pickleshare.py)
#@nl
#@+others
#@+node:ekr.20091204132346.6079:gethashfile
def gethashfile(key):

    return ("%02x" % abs(hash(key) % 256))[-2:]

#@-node:ekr.20091204132346.6079:gethashfile
#@+node:ekr.20091204132346.6080:class PickleShareDB (pickleshare.py)
_sentinel = object()

class PickleShareDB:

    """ The main 'connection' object for PickleShare database """

    #@    @+others
    #@+node:ekr.20100208103105.6187: Birth & special methods
    #@+node:ekr.20091204132346.6081: __init__
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

        trace = False and g.unitTesting
        self.root = Path(root).expanduser().abspath()
        if trace: g.trace('PickleShareDB',self.root)

        if not self.root.isdir():
            if trace: g.trace('makedirs',self.root)
            self.root.makedirs()

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
    #@-node:ekr.20091204132346.6081: __init__
    #@+node:ekr.20091216103214.6305:__contains__
    def __contains__(self, key):

        trace = False and g.unitTesting

        if trace: g.trace('(old PickleShareDB)',key)

        return self.has_key(key)
    #@-node:ekr.20091216103214.6305:__contains__
    #@+node:ekr.20091204132346.6088:__delitem__ 
    def __delitem__(self,key):

        """ del db["key"] """

        trace = False and g.unitTesting

        fil = self.root / key

        if trace: g.trace('(old PickleShareDB)',key,g.shortFileName(fil))

        self.cache.pop(fil,None)

        try:
            fil.remove()
        except OSError:
            # notfound and permission denied are ok - we
            # lost, the other process wins the conflict
            pass
    #@-node:ekr.20091204132346.6088:__delitem__ 
    #@+node:ekr.20091204132346.6082:__getitem__ 
    def __getitem__(self,key):

        """ db['key'] reading """

        trace = False and g.unitTesting

        fil = self.root / key
        try:
            mtime = (fil.stat()[stat.ST_MTIME])
        except OSError:
            raise KeyError(key)

        if fil in self.cache and mtime == self.cache[fil][1]:
            obj = self.cache[fil][0]
            if trace: g.trace('(old PickleShareDB: in cache)',
                g.shortFileName(fil),obj)
            return obj
        try:
            # The cached item has expired, need to read
            obj = self.loader(fil.open("rb"))
        except:
            raise KeyError(key)

        self.cache[fil] = (obj,mtime)
        if trace: g.trace('(old PickleShareDB: set cache)',
            g.shortFileName(fil),obj)
        return obj
    #@-node:ekr.20091204132346.6082:__getitem__ 
    #@+node:ekr.20091216103214.6303:__iter__
    def __iter__(self):

        trace = False and g.unitTesting

        if trace: g.trace('(old PickleShareDB)',list(self.keys()))

        for k in list(self.keys()):
            yield k
    #@-node:ekr.20091216103214.6303:__iter__
    #@+node:ekr.20091204132346.6094:__repr__
    def __repr__(self):

        return "PickleShareDB('%s')" % self.root



    #@-node:ekr.20091204132346.6094:__repr__
    #@+node:ekr.20091204132346.6083:__setitem
    def __setitem__(self,key,value):

        """ db['key'] = 5 """

        trace = False and g.unitTesting
        fil = self.root / key
        if trace: g.trace('(old PickleShareDB)',
            key,g.shortFileName(fil),g.callers(2)) # value can be big
        parent = fil.parent
        if parent and not parent.isdir():
            parent.makedirs()
        pickled = self.dumper(value,fil.open('wb'))

        try:
            self.cache[fil] = (value,fil.mtime)
        except OSError as e:
            if e.errno != 2:
                raise

    #@-node:ekr.20091204132346.6083:__setitem
    #@+node:ekr.20091204132346.6089:_normalized
    def _normalized(self, p):
        """ Make a key suitable for user's eyes """

        return str(self.root.relpathto(p)).replace('\\','/')
    #@-node:ekr.20091204132346.6089:_normalized
    #@-node:ekr.20100208103105.6187: Birth & special methods
    #@+node:ekr.20100208103105.6189:Methods that call special methods
    #@+node:ekr.20100208103105.5950:clear
    def clear (self):

        for z in self.keys():
            self.__delitem__(z)
    #@-node:ekr.20100208103105.5950:clear
    #@+node:ekr.20091224075120.6536:get
    def get(self, key, default=None):

        trace = False and g.unitTesting
        if trace: g.trace('(old PickleShareDB)')

        try:
            return self[key]
        except KeyError:
            return default
    #@-node:ekr.20091224075120.6536:get
    #@+node:ekr.20091216103214.6304:has_key
    def has_key(self, key):

        trace = False and g.unitTesting
        if trace: g.trace('(old PickleShareDB)',key)

        try:
            value = self[key]
        except KeyError:
            return False

        return True
    #@-node:ekr.20091216103214.6304:has_key
    #@+node:ekr.20091216103214.6306:items
    # def iteritems(self):
        # for k in self:
            # yield (k, self[k])

    def items(self):
        return [z for z in self]
    #@-node:ekr.20091216103214.6306:items
    #@+node:ekr.20091204132346.6090:keys
    # def iterkeys(self):
        # return self.__iter__()

    def keys(self, globpat = None):
        """ All keys in DB, or all keys matching a glob"""

        trace = False and g.unitTesting

        if globpat is None:
            files = self.root.walkfiles()
        else:
            files = [Path(p) for p in glob.glob(self.root/globpat)]

        result = [self._normalized(p) for p in files if p.isfile()]

        if trace: g.trace('(old PickleShareDB)',len(result))

        return result

    #@-node:ekr.20091204132346.6090:keys
    #@-node:ekr.20100208103105.6189:Methods that call special methods
    #@+node:ekr.20100208103105.6188:Other methods
    #@+node:ekr.20091204132346.6093:getlink
    def getlink(self,folder):
        """ Get a convenient link for accessing items  """

        trace = True and not g.unitTesting

        if trace: g.trace(folder,g.callers(5))

        return PickleShareLink(self, folder)

    #@-node:ekr.20091204132346.6093:getlink
    #@+node:ekr.20091204132346.6087:hcompress
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
            p = self.root / f
            if p.basename() == 'xx':
                continue
            p.remove()

    #@-node:ekr.20091204132346.6087:hcompress
    #@+node:ekr.20091204132346.6086:hdict
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
    #@-node:ekr.20091204132346.6086:hdict
    #@+node:ekr.20091204132346.6085:hget
    def hget(self, hashroot, key, default = _sentinel, fast_only = True):
        """ hashed get """

        trace = True and not g.unitTesting
        if trace: g.trace(g.callers(5))

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
    #@-node:ekr.20091204132346.6085:hget
    #@+node:ekr.20091204132346.6084:hset
    def hset(self, hashroot, key, value):
        """ hashed set """

        trace = True and not g.unitTesting
        if trace: g.trace(g.callers(5))

        hroot = self.root / hashroot
        if not hroot.isdir():
            hroot.makedirs()
        hfile = hroot / gethashfile(key)
        d = self.get(hfile, {})
        d.update( {key : value})
        self[hfile] = d                



    #@-node:ekr.20091204132346.6084:hset
    #@+node:ekr.20091204132346.6091:uncache
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

    #@-node:ekr.20091204132346.6091:uncache
    #@+node:ekr.20091204132346.6092:waitget
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
    #@-node:ekr.20091204132346.6092:waitget
    #@-node:ekr.20100208103105.6188:Other methods
    #@-others
#@-node:ekr.20091204132346.6080:class PickleShareDB (pickleshare.py)
#@+node:ekr.20091204132346.6095:class PickleShareLink (not used)
class PickleShareLink:
    """ A shortdand for accessing nested PickleShare data conveniently.

    Created through PickleShareDB.getlink(), example::

        lnk = db.getlink('myobjects/test')
        lnk.foo = 2
        lnk.bar = lnk.foo + 5

    """
    #@    @+others
    #@+node:ekr.20091204132346.6096:__init__
    def __init__(self, db, keydir ):    
        self.__dict__.update(locals())

    #@-node:ekr.20091204132346.6096:__init__
    #@+node:ekr.20091204132346.6097:__getattr__
    def __getattr__(self,key):
        return self.__dict__['db'][self.__dict__['keydir']+'/' + key]
    #@-node:ekr.20091204132346.6097:__getattr__
    #@+node:ekr.20091204132346.6098:__setattr__
    def __setattr__(self,key,val):
        self.db[self.keydir+'/' + key] = val
    #@-node:ekr.20091204132346.6098:__setattr__
    #@+node:ekr.20091204132346.6099:__repr__
    def __repr__(self):
        db = self.__dict__['db']
        keys = db.keys( self.__dict__['keydir'] +"/*")
        return "<PickleShareLink '%s': %s>" % (
            self.__dict__['keydir'],
            ";".join([Path(k).basename() for k in keys]))


    #@-node:ekr.20091204132346.6099:__repr__
    #@-others
#@-node:ekr.20091204132346.6095:class PickleShareLink (not used)
#@+node:ekr.20091204132346.6100:test
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

#@-node:ekr.20091204132346.6100:test
#@+node:ekr.20091204132346.6101:stress
def stress():
    db = PickleShareDB('~/fsdbtest')
    import time,sys
    for i in range(1000):
        for j in range(1000):
            if i % 15 == 0 and i < 200:
                if str(j) in db:
                    del db[str(j)]
                continue

            if j%33 == 0:
                time.sleep(0.02)

            db[str(j)] = db.get(str(j), []) + [(i,j,"proc %d" % os.getpid())]
            db.hset('hash',j, db.hget('hash',j,15) + 1 )

        # print i,
        print(i)
        sys.stdout.flush()
        if i % 10 == 0:
            db.uncache()

#@-node:ekr.20091204132346.6101:stress
#@+node:ekr.20091204132346.6102:main
def main():
    import textwrap
    usage = textwrap.dedent("""\
    pickleshare - manage PickleShare databases 

    Usage:

        pickleshare dump /path/to/db > dump.txt
        pickleshare load /path/to/db < dump.txt
        pickleshare test /path/to/db
    """)
    DB = PickleShareDB
    import sys
    if len(sys.argv) < 2:
        print(usage)
        return

    cmd = sys.argv[1]
    args = sys.argv[2:]
    if cmd == 'dump':
        if not args: args= ['.']
        db = DB(args[0])
        import pprint
        pprint.pprint(db.items())
    elif cmd == 'load':
        cont = sys.stdin.read()
        db = DB(args[0])
        data = eval(cont)
        db.clear()
        for k,v in db.items():
            db[k] = v
    elif cmd == 'testwait':
        db = DB(args[0])
        db.clear()
        print(db.waitget('250'))
    elif cmd == 'test':
        test()
        stress()
#@-node:ekr.20091204132346.6102:main
#@-others
if __name__== "__main__":
    main()


#@-node:ekr.20100207111939.5895:@thin ../external/pickleshare.py
#@-leo
