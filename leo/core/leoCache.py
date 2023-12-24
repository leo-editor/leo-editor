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
#@+node:ekr.20180627052459.1: ** class CommanderWrapper (c.db)
class CommanderWrapper:
    """
    A class that creates distinct keys for all commanders, allowing
    commanders to share g.app.db without collisions.
    
    Instances of this class are c.db.
    """

    def __init__(self, c: Cmdr) -> None:
        self.c = c
        self.db = g.app.db
        self.key = c.mFileName
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
#@+node:ekr.20180627041556.1: ** class GlobalCacher (g.app.db)
class GlobalCacher:
    """
    A class creating a singleton global database, g.app.db.
    
    This DB resides in ~/.leo/db.
    
    New in Leo 6.7.7: All instances of c.db may use g.app.db because the
    CommanderWrapper class creates distinct keys for each commander.
    """

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
            self.db.clear()  # SqlitePickleShare.clear.
        except TypeError:
            self.db = {}  # self.db was a dict.
        except Exception:
            g.trace('unexpected exception')
            g.es_exception()
            self.db = {}
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
#@+node:vitalije.20170716201700.1: ** class SqlitePickleShare
_sentinel = object()


class SqlitePickleShare:
    """
    The main 'connection' object for SqlitePickleShare database.
    
    Opening this DB may fail. If so the GlobalCacher class uses a plain
    Python dict instead.
    """
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
        """
        Deletes all files in the fcache subdirectory.
        
        It would be more thorough to delete everything
        below the root directory, but it's not necessary.
        """
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
    #@+node:vitalije.20170716201700.17: *3* has_key (SqlitePickleShare)
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
