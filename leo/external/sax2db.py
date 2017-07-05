#@+leo-ver=5-thin
#@+node:vitalije.20170704194046.1: * @file ../external/sax2db.py
from __future__ import print_function
import sys
from .leosax import get_leo_data
import leo.core.leoGlobals as g
import sqlite3
import pickle
#@+others
#@+node:vitalije.20170704195230.1: ** sqls
def sqls(k=None):
    _sqls = {
        'drop-vnodes': 'drop table if exists vnodes',
        'drop-settings': 'drop table if exists settings',
        'create-vnodes': '''create table vnodes(gnx primary key,
                                    head,
                                    body,
                                    children,
                                    parents,
                                    iconVal,
                                    statusBits,
                                    ua)''',
        'create-extra-infos': 
            '''create table if not exists extra_infos(name primary key, value)''',
        'create-settings': '''create table settings(name primary key,
                                    value, level, source)''',
        'insert-vnode': 'replace into vnodes values(?,?,?,?,?,?,?,?)',
        'insert-setting': 'replace into settings values(?,?,?,?)'
    }
    if k is None:
        return _sqls
    return _sqls.get(k)
#@+node:vitalije.20170704195351.1: ** resetdb
def resetdb(conn):
    conn.execute(sqls('drop-vnodes'))
    conn.execute(sqls('create-vnodes'))
    conn.execute(sqls('create-extra-infos'))
    #conn.execute(sqls('drop-settings'))
    #conn.execute(sqls('create-settings'))
#@+node:vitalije.20170704202015.1: ** walk_tree
def walk_tree(node, vns=None, seq=None):
    if vns is None:
        vns = {}
    if seq is None:
        seq = []
    if not node.gnx in seq:
        seq.append(node.gnx)
    pgnx = node.parent.gnx
    v = vns.get(node.gnx, 
        (
            node.h,
            g.u('').join(node.b),
            g.u(' ').join(n.gnx for n in node.children),
            [],
            1 if node.b else 0,
            pickle.dumps(node.u)
        ))
    v[3].append(pgnx)
    vns[node.gnx] = v
    for n in node.children:
        walk_tree(n, vns, seq)
    return vns, seq
#@+node:vitalije.20170704202637.1: ** vnode_data
def vnode_data(vns, seq):
    for gnx in seq:
        v = vns[gnx]
        yield (gnx, v[0], v[1], v[2], g.u(' ').join(v[3]), v[4], 0, v[5])
#@-others
def main(src, dest):
    print('src', src)
    print('dest', dest)
    root = get_leo_data(src)
    root.gnx = 'hidden-root-vnode-gnx'
    vns, seq = walk_tree(root)
    data = vnode_data(vns, seq[1:]) # skip hidden root
    with sqlite3.connect(dest) as conn:
        resetdb(conn)
        conn.executemany(sqls('insert-vnode'), data)
        conn.commit()

if __name__ == '__main__':
    src = g.os_path_finalize_join(g.os_path_dirname(__file__),
         '../config/myLeoSettings.leo')
    if len(sys.argv) > 1:
        src = sys.argv[1]
    dest = src[:-3] + 'db'
    main(src, dest)
    print('ok')
#@-leo
