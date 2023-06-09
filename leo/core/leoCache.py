#@+leo-ver=5-thin
#@+node:ekr.20100208065621.5894: * @file leoCache.py
"""A module encapsulating Leo's file caching"""
#@+<< leoCache imports & annotations >>
#@+node:ekr.20100208223942.10436: ** << leoCache imports & annotations >>
from __future__ import annotations
import fnmatch
import os
import pickle
import sqlite3
import stat
from typing import Any, Generator, Optional, Sequence, TYPE_CHECKING
import zlib
from leo.core import leoGlobals as g

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr

#@-<< leoCache imports & annotations >>

# pylint: disable=raise-missing-from

# Abbreviations used throughout.
abspath = g.os_path_abspath
basename = g.os_path_basename
expanduser = g.os_path_expanduser
isdir = g.os_path_isdir
isfile = g.os_path_isfile
join = g.os_path_join
normcase = g.os_path_normcase
split = g.os_path_split
#@+others
#@+node:ekr.20100208062523.5885: ** class CommanderCacher
class CommanderCacher:
    """A class to manage per-commander caches."""

    def __init__(self) -> None:
        self.db: Any
        try:
            path = join(g.app.homeLeoDir, 'db', 'global_data')
            self.db = SqlitePickleShare(path)
        except Exception:
            self.db = {}  # type:ignore
    #@+others
    #@+node:ekr.20100209160132.5759: *3* cacher.clear
    def clear(self) -> None:
        """Clear the cache for all commanders."""
        # Careful: self.db may be a Python dict.
        try:
            self.db.clear()
        except Exception:
            g.trace('unexpected exception')
            g.es_exception()
            self.db = {}  # type:ignore
    #@+node:ekr.20180627062431.1: *3* cacher.close
    def close(self) -> None:
        # Careful: self.db may be a dict.
        if hasattr(self.db, 'conn'):
            # pylint: disable=no-member
            self.db.conn.commit()
            self.db.conn.close()
    #@+node:ekr.20180627042809.1: *3* cacher.commit
    def commit(self) -> None:
        # Careful: self.db may be a dict.
        if hasattr(self.db, 'conn'):
            # pylint: disable=no-member
            self.db.conn.commit()
    #@+node:ekr.20180611054447.1: *3* cacher.dump
    def dump(self) -> None:
        """Dump the indicated cache if --trace-cache is in effect."""
        dump_cache(g.app.commander_db, tag='Commander Cache')
    #@+node:ekr.20180627053508.1: *3* cacher.get_wrapper
    def get_wrapper(self, c: Cmdr, fn: str = None) -> "CommanderWrapper":
        """Return a new wrapper for c."""
        return CommanderWrapper(c, fn=fn)
    #@+node:ekr.20100208065621.5890: *3* cacher.test
    def test(self) -> bool:

        # pylint: disable=no-member
        if g.app.gui.guiName() == 'nullGui':
            # Null gui's don't normally set the g.app.gui.db.
            g.app.setGlobalDb()
        # Fixes bug 670108.
        assert g.app.db is not None  # a PickleShareDB instance.
        # Make sure g.guessExternalEditor works.
        g.app.db.get("LEO_EDITOR")
        # self.initFileDB('~/testpickleshare')
        db = self.db
        db.clear()
        assert not list(db.items())
        db['hello'] = 15
        db['aku ankka'] = [1, 2, 313]
        db['paths/nest/ok/keyname'] = [1, (5, 46)]
        db.uncache()  # frees memory, causes re-reads later
        # print(db.keys())
        db.clear()
        return True
    #@+node:ekr.20100210163813.5747: *3* cacher.save
    def save(self, c: Cmdr, fn: str) -> None:
        """
        Save the per-commander cache.

        Change the cache prefix if changeName is True.

        save and save-as set changeName to True, save-to does not.
        """
        self.commit()
        if fn:
            # 1484: Change only the key!
            if isinstance(c.db, CommanderWrapper):
                c.db.key = fn
                self.commit()
            else:
                g.trace('can not happen', c.db.__class__.__name__)
    #@-others
#@+node:ekr.20180627052459.1: ** class CommanderWrapper
class CommanderWrapper:
    """A class to distinguish keys from separate commanders."""

    def __init__(self, c: Cmdr, fn: str = None) -> None:
        self.c = c
        self.db = g.app.db
        self.key = fn or c.mFileName
        self.user_keys: set[str] = set()

    def get(self, key: str, default: Any = None) -> Any:
        value = self.db.get(f"{self.key}:::{key}")
        return default if value is None else value

    def keys(self) -> list[str]:
        return sorted(list(self.user_keys))

    def __contains__(self, key: Any) -> bool:
        return f"{self.key}:::{key}" in self.db

    def __delitem__(self, key: Any) -> None:
        if key in self.user_keys:
            self.user_keys.remove(key)
        del self.db[f"{self.key}:::{key}"]

    def __getitem__(self, key: str) -> Any:
        return self.db[f"{self.key}:::{key}"]  # May (properly) raise KeyError

    def __setitem__(self, key: str, value: Any) -> None:
        self.user_keys.add(key)
        self.db[f"{self.key}:::{key}"] = value
#@+node:ekr.20180627041556.1: ** class GlobalCacher
class GlobalCacher:
    """A singleton global cacher, g.app.db"""

    def __init__(self) -> None:
        """Ctor for the GlobalCacher class."""
        trace = 'cache' in g.app.debug
        self.db: Any
        try:
            path = join(g.app.homeLeoDir, 'db', 'g_app_db')
            if trace:
                print('path for g.app.db:', repr(path))
            self.db = SqlitePickleShare(path)
            if trace and self.db is not None:
                self.dump(tag='Startup')
        except Exception:
            if trace:
                g.es_exception()
            # Use a plain dict as a dummy.
            self.db = {}  # type:ignore
    #@+others
    #@+node:ekr.20180627045750.1: *3* g_cacher.clear
    def clear(self) -> None:
        """Clear the global cache."""
        # Careful: self.db may be a Python dict.
        if 'cache' in g.app.debug:
            g.trace('clear g.app.db')
        try:
            self.db.clear()
        except TypeError:
            self.db.clear()
        except Exception:
            g.trace('unexpected exception')
            g.es_exception()
            self.db = {}  # type:ignore
    #@+node:ekr.20180627042948.1: *3* g_cacher.commit_and_close()
    def commit_and_close(self) -> None:
        # Careful: self.db may be a dict.
        if hasattr(self.db, 'conn'):
            # pylint: disable=no-member
            if 'cache' in g.app.debug:
                self.dump(tag='Shutdown')
            self.db.conn.commit()
            self.db.conn.close()
    #@+node:ekr.20180627045953.1: *3* g_cacher.dump
    def dump(self, tag: str = '') -> None:
        """Dump the indicated cache if --trace-cache is in effect."""
        tag0 = 'Global Cache'
        tag2 = f"{tag0}: {tag}" if tag else tag0
        dump_cache(self.db, tag2)  # Careful: g.app.db may not be set yet.
    #@-others
#@+node:ekr.20100208223942.5967: ** class PickleShareDB
_sentinel = object()


class PickleShareDB:
    """ The main 'connection' object for PickleShare database """
    #@+others
    #@+node:ekr.20100208223942.5968: *3*  Birth & special methods
    #@+node:ekr.20100208223942.5969: *4*  __init__ (PickleShareDB)
    def __init__(self, root: str) -> None:
        """
        Init the PickleShareDB class.
        root: The directory that contains the data. Created if it doesn't exist.
        """
        self.root: str = abspath(expanduser(root))
        if not isdir(self.root) and not g.unitTesting:
            self._makedirs(self.root)
        # Keys are normalized file names.
        # Values are tuples (obj, orig_mod_time)
        self.cache: dict[str, Any] = {}

        def loadz(fileobj: Any) -> None:
            if fileobj:
                # Retain this code for maximum compatibility.
                try:
                    val = pickle.loads(
                        zlib.decompress(fileobj.read()))
                except ValueError:
                    g.es("Unpickling error - Python 3 data accessed from Python 2?")
                    return None
                return val
            return None

        def dumpz(val: Any, fileobj: Any) -> None:
            if fileobj:
                try:
                    # Use Python 2's highest protocol, 2, if possible
                    data = pickle.dumps(val, 2)
                except Exception:
                    # Use best available if that doesn't work (unlikely)
                    data = pickle.dumps(val, pickle.HIGHEST_PROTOCOL)
                compressed = zlib.compress(data)
                fileobj.write(compressed)

        self.loader = loadz
        self.dumper = dumpz
    #@+node:ekr.20100208223942.5970: *4* __contains__(PickleShareDB)
    def __contains__(self, key: Any) -> bool:

        return self.has_key(key)  # NOQA
    #@+node:ekr.20100208223942.5971: *4* __delitem__
    def __delitem__(self, key: str) -> None:
        """ del db["key"] """
        fn = join(self.root, key)
        self.cache.pop(fn, None)
        try:
            os.remove(fn)
        except OSError:
            # notfound and permission denied are ok - we
            # lost, the other process wins the conflict
            pass
    #@+node:ekr.20100208223942.5972: *4* __getitem__ (PickleShareDB)
    def __getitem__(self, key: str) -> Any:
        """ db['key'] reading """
        fn = join(self.root, key)
        try:
            mtime = (os.stat(fn)[stat.ST_MTIME])
        except OSError:
            raise KeyError(key)
        if fn in self.cache and mtime == self.cache[fn][1]:
            obj = self.cache[fn][0]
            return obj
        try:
            # The cached item has expired, need to read
            obj = self.loader(self._openFile(fn, 'rb'))
        except Exception:
            raise KeyError(key)
        self.cache[fn] = (obj, mtime)
        return obj
    #@+node:ekr.20100208223942.5973: *4* __iter__
    def __iter__(self) -> Generator:

        for k in list(self.keys()):
            yield k
    #@+node:ekr.20100208223942.5974: *4* __repr__
    def __repr__(self) -> str:
        return f"PickleShareDB('{self.root}')"
    #@+node:ekr.20100208223942.5975: *4* __setitem__ (PickleShareDB)
    def __setitem__(self, key: str, value: Any) -> None:
        """ db['key'] = 5 """
        fn = join(self.root, key)
        parent, junk = split(fn)
        if parent and not isdir(parent):
            self._makedirs(parent)
        self.dumper(value, self._openFile(fn, 'wb'))
        try:
            mtime = os.path.getmtime(fn)
            self.cache[fn] = (value, mtime)
        except OSError as e:
            if e.errno != 2:
                raise
    #@+node:ekr.20100208223942.10452: *3* _makedirs
    def _makedirs(self, fn: str, mode: int = 0o777) -> None:

        os.makedirs(fn, mode)
    #@+node:ekr.20100208223942.10458: *3* _openFile (PickleShareDB)
    def _openFile(self, fn: str, mode: str = 'r') -> Optional[Any]:
        """ Open this file.  Return a file object.

        Do not print an error message.
        It is not an error for this to fail.
        """
        try:
            return open(fn, mode)
        except Exception:
            return None
    #@+node:ekr.20100208223942.10454: *3* _walkfiles & helpers
    def _walkfiles(self, s: str, pattern: str = None) -> Generator:
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
    def _listdir(self, s: str, pattern: str = None) -> list[str]:
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
    def _fn_match(self, s: str, pattern: str) -> bool:
        """ Return True if self.name matches the given pattern.

        pattern - A filename pattern with wildcards, for example '*.py'.
        """
        return fnmatch.fnmatch(basename(s), pattern)
    #@+node:ekr.20100208223942.5978: *3* clear (PickleShareDB)
    def clear(self) -> None:
        # Deletes all files in the fcache subdirectory.
        # It would be more thorough to delete everything
        # below the root directory, but it's not necessary.
        for z in self.keys():
            self.__delitem__(z)
    #@+node:ekr.20100208223942.5979: *3* get
    def get(self, key: str, default: Any = None) -> Any:

        try:
            val = self[key]
            return val
        except KeyError:
            return default
    #@+node:ekr.20100208223942.5980: *3* has_key (PickleShareDB)
    def has_key(self, key: str) -> bool:

        try:
            self[key]
        except KeyError:
            return False
        return True
    #@+node:ekr.20100208223942.5981: *3* items
    def items(self) -> list[Any]:
        return [z for z in self]
    #@+node:ekr.20100208223942.5982: *3* keys & helpers (PickleShareDB)
    # Called by clear, and during unit testing.

    def keys(self, globpat: str = None) -> list[str]:
        """Return all keys in DB, or all keys matching a glob"""
        files: list[str]
        if globpat is None:
            files = self._walkfiles(self.root)  # type:ignore
        else:
            # Do not call g.glob_glob here.
            files = [z for z in join(self.root, globpat)]
        result = [self._normalized(s) for s in files if isfile(s)]
        return result
    #@+node:ekr.20100208223942.5976: *4* _normalized
    def _normalized(self, filename: str) -> str:
        """ Make a key suitable for user's eyes """
        # os.path.relpath doesn't work here.
        return self._relpathto(self.root, filename).replace('\\', '/')
    #@+node:ekr.20100208223942.10460: *4* _relpathto
    # Used only by _normalized.

    def _relpathto(self, src: str, dst: str) -> str:
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
        # If they happen to be identical, use os.curdir.
        return os.curdir
    #@+node:ekr.20100208223942.10462: *4* _splitall
    # Used by relpathto.

    def _splitall(self, s: str) -> list[str]:
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
    def uncache(self, *items: Any) -> None:
        """ Removes all, or specified items from cache

        Use this after reading a large amount of large objects
        to free up memory, when you won't be needing the objects
        for a while.

        """
        if not items:
            self.cache = {}
        for it in items:
            self.cache.pop(it, None)
    #@-others
#@+node:vitalije.20170716201700.1: ** class SqlitePickleShare
_sentinel = object()


class SqlitePickleShare:
    """ The main 'connection' object for SqlitePickleShare database """
    #@+others
    #@+node:vitalije.20170716201700.2: *3*  Birth & special methods
    def init_dbtables(self, conn: Any) -> None:
        sql = 'create table if not exists cachevalues(key text primary key, data blob);'
        conn.execute(sql)
    #@+node:vitalije.20170716201700.3: *4*  __init__ (SqlitePickleShare)
    def __init__(self, root: str) -> None:
        """
        Init the SqlitePickleShare class.
        root: The directory that contains the data. Created if it doesn't exist.
        """
        self.root: str = abspath(expanduser(root))
        if not isdir(self.root) and not g.unitTesting:
            self._makedirs(self.root)
        dbfile = ':memory:' if g.unitTesting else join(root, 'cache.sqlite')
        self.conn = sqlite3.connect(dbfile, isolation_level=None)
        self.init_dbtables(self.conn)
        # Keys are normalized file names.
        # Values are tuples (obj, orig_mod_time)
        self.cache: dict[str, Any] = {}

        def loadz(data: Any) -> Optional[Any]:
            if data:
                # Retain this code for maximum compatibility.
                try:
                    val = pickle.loads(zlib.decompress(data))
                except(ValueError, TypeError):
                    g.es("Unpickling error - Python 3 data accessed from Python 2?")
                    return None
                return val
            return None

        def dumpz(val: Any) -> Any:
            try:
                # Use Python 2's highest protocol, 2, if possible
                data = pickle.dumps(val, protocol=2)
            except Exception:
                # Use best available if that doesn't work (unlikely)
                data = pickle.dumps(val, pickle.HIGHEST_PROTOCOL)
            return sqlite3.Binary(zlib.compress(data))

        self.loader = loadz
        self.dumper = dumpz
        self.reset_protocol_in_values()
    #@+node:vitalije.20170716201700.4: *4* __contains__(SqlitePickleShare)
    def __contains__(self, key: str) -> bool:

        return self.has_key(key)  # NOQA
    #@+node:vitalije.20170716201700.5: *4* __delitem__
    def __delitem__(self, key: str) -> None:
        """ del db["key"] """
        try:
            self.conn.execute(
                '''delete from cachevalues
                where key=?''', (key,))
        except sqlite3.OperationalError:
            pass
    #@+node:vitalije.20170716201700.6: *4* __getitem__
    def __getitem__(self, key: str) -> None:
        """ db['key'] reading """
        try:
            obj = None
            for row in self.conn.execute(
                '''select data from cachevalues
                where key=?''', (key,)):
                obj = self.loader(row[0])
                break
            else:
                raise KeyError(key)
        except sqlite3.Error:
            raise KeyError(key)
        return obj
    #@+node:vitalije.20170716201700.7: *4* __iter__
    def __iter__(self) -> Generator:

        for k in list(self.keys()):
            yield k
    #@+node:vitalije.20170716201700.8: *4* __repr__
    def __repr__(self) -> str:
        return f"SqlitePickleShare('{self.root}')"
    #@+node:vitalije.20170716201700.9: *4* __setitem__
    def __setitem__(self, key: str, value: Any) -> None:
        """ db['key'] = 5 """
        try:
            data = self.dumper(value)
            self.conn.execute(
                '''replace into cachevalues(key, data) values(?,?);''',
                (key, data))
        except sqlite3.OperationalError:
            g.es_exception()
    #@+node:vitalije.20170716201700.10: *3* _makedirs
    def _makedirs(self, fn: str, mode: int = 0o777) -> None:

        os.makedirs(fn, mode)
    #@+node:vitalije.20170716201700.11: *3* _openFile (SqlitePickleShare)
    def _openFile(self, fn: str, mode: str = 'r') -> Optional[Any]:
        """ Open this file.  Return a file object.

        Do not print an error message.
        It is not an error for this to fail.
        """
        try:
            return open(fn, mode)
        except Exception:
            return None
    #@+node:vitalije.20170716201700.12: *3* _walkfiles & helpers
    def _walkfiles(self, s: str, pattern: str = None) -> None:
        """ D.walkfiles() -> iterator over files in D, recursively.

        The optional argument, pattern, limits the results to files
        with names that match the pattern.  For example,
        mydir.walkfiles('*.tmp') yields only files with the .tmp
        extension.
        """
    #@+node:vitalije.20170716201700.13: *4* _listdir
    def _listdir(self, s: str, pattern: str = None) -> list[str]:
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
    def _fn_match(self, s: str, pattern: Any) -> bool:
        """ Return True if self.name matches the given pattern.

        pattern - A filename pattern with wildcards, for example '*.py'.
        """
        return fnmatch.fnmatch(basename(s), pattern)
    #@+node:vitalije.20170716201700.15: *3* clear (SqlitePickleShare)
    def clear(self) -> None:
        # Deletes all files in the fcache subdirectory.
        # It would be more thorough to delete everything
        # below the root directory, but it's not necessary.
        self.conn.execute('delete from cachevalues;')
    #@+node:vitalije.20170716201700.16: *3* get  (SqlitePickleShare)
    def get(self, key: str, default: Any = None) -> Any:

        if not self.has_key(key):  # noqa
            return default
        try:
            val = self[key]
            return val
        except Exception:  # #1444: Was KeyError.
            return default
    #@+node:vitalije.20170716201700.17: *3* has_key (SqlightPickleShare)
    def has_key(self, key: str) -> bool:
        sql = 'select 1 from cachevalues where key=?;'
        for _row in self.conn.execute(sql, (key,)):
            return True
        return False
    #@+node:vitalije.20170716201700.18: *3* items
    def items(self) -> Generator:
        sql = 'select key,data from cachevalues;'
        for key, data in self.conn.execute(sql):
            yield key, data
    #@+node:vitalije.20170716201700.19: *3* keys
    # Called by clear, and during unit testing.

    def keys(self, globpat: str = None) -> Generator:
        """Return all keys in DB, or all keys matching a glob"""
        if globpat is None:
            sql = 'select key from cachevalues;'
            args: Sequence[Any] = tuple()
        else:
            sql = "select key from cachevalues where key glob ?;"
            # pylint: disable=trailing-comma-tuple
            args = globpat,
        for key in self.conn.execute(sql, args):
            yield key
    #@+node:vitalije.20170818091008.1: *3* reset_protocol_in_values
    def reset_protocol_in_values(self) -> None:
        PROTOCOLKEY = '__cache_pickle_protocol__'
        if self.get(PROTOCOLKEY, 3) == 2:
            return
        #@+others
        #@+node:vitalije.20170818115606.1: *4* viewrendered special case
        import json
        row = self.get('viewrendered_default_layouts') or (None, None)
        row = json.loads(json.dumps(row[0])), json.loads(json.dumps(row[1]))
        self['viewrendered_default_layouts'] = row
        #@+node:vitalije.20170818115617.1: *4* do_block
        def do_block(cur: Any) -> Any:
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
    def uncache(self, *items: Any) -> None:
        """not used in SqlitePickleShare"""
        pass
    #@-others
#@+node:ekr.20180627050237.1: ** function: dump_cache
def dump_cache(db: Any, tag: str) -> None:
    """Dump the given cache."""
    print(f'\n===== {tag} =====\n')
    if db is None:
        print('db is None!')
        return
    # Create a dict, sorted by file prefixes.
    d: dict[str, Any] = {}
    for key in db.keys():
        key = key[0]
        val = db.get(key)
        data = key.split(':::')
        if len(data) == 2:
            fn, key2 = data
        else:
            fn, key2 = 'None', key
        aList = d.get(fn, [])
        aList.append((key2, val),)
        d[fn] = aList
    # Print the dict.
    files = 0
    for key in sorted(d.keys()):
        if key != 'None':
            dump_list('File: ' + key, d.get(key))
            files += 1
    if d.get('None'):
        heading = f"All others ({tag})" if files else None
        dump_list(heading, d.get('None'))

def dump_list(heading: Any, aList: list) -> None:
    if heading:
        print(f'\n{heading}...\n')
    for aTuple in aList:
        key, val = aTuple
        if isinstance(val, str):
            if key.startswith('windowState'):
                print(key)
            elif key.endswith(('leo_expanded', 'leo_marked')):
                if val:
                    print(f"{key:30}:")
                    g.printObj(val.split(','))
                else:
                    print(f"{key:30}: []")
            else:
                print(f"{key:30}: {val}")
        elif isinstance(val, (int, float)):
            print(f"{key:30}: {val}")
        else:
            print(f"{key:30}:")
            g.printObj(val)
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
