#@+leo-ver=5-thin
#@+node:vitalije.20170704194046.1: * @file ../external/sax2db.py
from __future__ import print_function
import sys
import leo.core.leoGlobals as g
import re
import pprint
if not g.isPython3:
    reload(sys)
    sys.setdefaultencoding('utf-8')
from .leosax import get_leo_data
import sqlite3
import pickle
#@+others
#@+node:vitalije.20170706071146.1: ** SQL
#@+node:vitalije.20170704195230.1: *3* sqls
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
#@+node:vitalije.20170704195351.1: *3* resetdb
def resetdb(conn):
    conn.execute(sqls('drop-vnodes'))
    conn.execute(sqls('create-vnodes'))
    conn.execute(sqls('create-extra-infos'))
    #conn.execute(sqls('drop-settings'))
    #conn.execute(sqls('create-settings'))
#@+node:vitalije.20170706070756.1: ** Settings...
#@+node:vitalije.20170706070938.1: *3* __ kinds of settings
simple_settings = g.u('bool color directory int ints '
    'float path ratio string strings data enabledplugins').split()
super_simple_settings = g.u('directory path string').split()
condition_settings = g.u('ifenv ifhostname ifplatform').split()
complex_settings = g.u('buttons commands '
    'font menus mode menuat openwith outlinedata popup shortcuts').split()
#@+node:vitalije.20170706070818.1: *3* descend & descend_f
def descend(node, conds, acc):
    descend_f(settings_harvester, node, conds, acc)

def descend_f(f, node, conds, acc):
    for child in node.children:
        f(child, conds, acc)
#@+node:vitalije.20170706070953.1: *3* isComplexSetting
def isComplexSetting(node):
    kind, name, val = parseHeadline(node.h)
    return kind in complex_settings
#@+node:vitalije.20170706070955.1: *3* isCondition
def isCondition(node):
    kind, name, val = parseHeadline(node.h)
    return kind in condition_settings
#@+node:vitalije.20170706070951.1: *3* isSimpleSetting
def isSimpleSetting(node):
    kind, name, val = parseHeadline(node.h)
    return kind in simple_settings
#@+node:vitalije.20170705141951.1: *3* parseHeadline
def parseHeadline(s):
    """
    Parse a headline of the form @kind:name=val
    Return (kind,name,val).
    Leo 4.11.1: Ignore everything after @data name.
    """
    kind = name = val = None
    if g.match(s, 0, g.u('@')):
        i = g.skip_id(s, 1, chars=g.u('-'))
        i = g.skip_ws(s, i)
        kind = s[1: i].strip()
        if kind:
            # name is everything up to '='
            if kind == g.u('data'):
                # i = g.skip_ws(s,i)
                j = s.find(g.u(' '), i)
                if j == -1:
                    name = s[i:].strip()
                else:
                    name = s[i: j].strip()
            else:
                j = s.find(g.u('='), i)
                if j == -1:
                    name = s[i:].strip()
                else:
                    name = s[i: j].strip()
                    # val is everything after the '='
                    val = s[j + 1:].strip()
    # g.trace("%50s %10s %s" %(name,kind,val))
    return kind, name, val
#@+node:vitalije.20170706124002.1: *3* harvest_one_setting
def harvest_one_setting(gnx, kind, name, value, conds, acc):
    cond = g.u('|#|').join((x.h for x in conds[1:]))
    acc.append((gnx, kind, name, value, cond))
#@+node:vitalije.20170706213544.1: *3* get_data
def subtree(node):
    for child in node.children:
        yield child
        for x in subtree(child):
            yield x
def blines(node):
    return g.splitLines(''.join(node.b))
def get_data(node):
    data = blines(node)
    for x in subtree(node):
        if x.b and not x.h.startswith('@'):
            data.extend(blines(x))
            if not x.b[-1].endswith('\n'):
                data.append(g.u('\n'))
    return data
    
#@+node:vitalije.20170707152323.1: *3* get_menus_list
def get_menu_items(node):
    aList = []
    for child in node.children:
        for tag in ('@menu', '@item'):
            if child.h.startswith(tag):
                name = child.h[len(tag)+1:].strip()
                if tag == '@menu':
                    aList.append(('%s %s'%(tag, name), get_menu_items(child), None))
                else:
                    b = g.splitLines(''.join(child.b))
                    aList.append((tag, name, b[0] if b else ''))
                break
    return aList
    
def get_menus_list(node):
    aList = []
    tag = '@menu'
    taglen = len(tag) + 1
    for child in node.children:
        if child.h.startswith(tag):
            menuName = child.h[taglen:].strip()
            aList.append(('%s %s'%(tag, menuName), get_menu_items(child), None))
    with open('/tmp/menus', 'w') as out:
        out.write(pprint.pformat(aList))
    return aList
#@+node:vitalije.20170707131941.1: *3* get_enabled_plugins
def get_enabled_plugins(node):
    s = node.b
    aList = []
    for s in g.splitLines(s):
        i = s.find('#')
        if i > -1: s = s[: i] + '\n' # 2011/09/29: must add newline back in.
        if s.strip(): aList.append(s.lstrip())
    return ''.join(aList)
    
#@+node:vitalije.20170707132425.1: *3* get_font
def get_font(node, values):
    '''Handle an @font node. Such nodes affect syntax coloring *only*.'''
    d = parseFont(node)
    # Set individual settings.
    for key in ('family', 'size', 'slant', 'weight'):
        data = d.get(key)
        if data is not None:
            name, val = data
            values.append((key, name, val))
#@+node:vitalije.20170707132535.1: *4* parseFont & helper
def parseFont(node):
    d = {
        'comments': [],
        'family': None,
        'size': None,
        'slant': None,
        'weight': None,
    }
    lines = node.b
    for line in lines:
        parseFontLine(line, d)
    comments = d.get('comments')
    d['comments'] = '\n'.join(comments)
    return d
#@+node:vitalije.20170707132535.2: *5* parseFontLine
def parseFontLine(line, d):
    s = line.strip()
    if not s: return
    if g.match(s, 0, '#'):
        s = s[1:].strip()
        comments = d.get('comments')
        comments.append(s)
        d['comments'] = comments
    else:
        # name is everything up to '='
        i = s.find('=')
        if i == -1:
            name = s; val = None
        else:
            name = s[: i].strip()
            val = s[i + 1:].strip()
            val = val.lstrip('"').rstrip('"')
            val = val.lstrip("'").rstrip("'")
        if name.endswith(('_family', '_size', '_slant', '_weight')):
            d[name.rsplit('_', 1)[1]] = name, val
#@+node:vitalije.20170707140753.1: *3* get_ints
get_ints_items_pattern = re.compile('\\[\\d+(,\\d+)*\\]')
get_ints_name_pattern = re.compile('[a-zA-Z_\\-]+')

def get_ints(name, val):
    '''We expect either:
    @ints [val1,val2,...]aName=val
    @ints aName[val1,val2,...]=val'''
    m = get_ints_items_pattern.search(name)
    if m:
        kind = 'ints' + m.group(0)
        
        if ',%s,'%val not in m.group(0).replace('[', ',').replace(']',','):
            g.pr("%s is not in %s in %s" % (val, kind, name))
            return
    else:
        valueError('ints', name, val)
        return
    try:
        value = int(val)
    except ValueError:
        valueError('int', name, val)
        return
    return kind, name, value
    
#@+node:vitalije.20170707160403.1: *3* get_strings
get_strings_pattern = re.compile('\\[([^\\]]+)\\]')
def get_strings(name, value):
    m = get_strings_pattern.search(name)
    if m:
        items = [x.strip() for x in m.group(1).split(',')]
        nm = name.replace(m.group(0), '').strip()
        if value not in items:
            raise ValueError('%s value %s not in valid values [%s]'%(nm, value, items))
        return 'strings[%s]'%(','.join(items)), nm, value
    raise ValueError("%s is not a valid strings for %s" % (value, name))
#@+node:vitalije.20170706123951.1: *3* harvest_one_simple_setting
def harvest_one_simple_setting(node, conds, acc):
    kind, name, value = parseHeadline(node.h)
    #@+others
    #@+node:vitalije.20170707155128.1: *4* if supersimple
    if kind in super_simple_settings:
        pass
    #@+node:vitalije.20170706213248.1: *4* elif bool
    elif kind == 'bool':
        if value in ('True', 'true', '1'):
            value = True
        elif value in ('False', 'false', '0'):
            value = False
        elif value in ('None', '', 'none'):
            value = None
        else:
            valueError(kind, name, value)
            return
    #@+node:vitalije.20170706213427.1: *4* elif color
    elif kind == 'color':
        value = value.lstrip('"').rstrip('"')
        value = value.lstrip("'").rstrip("'")
    #@+node:vitalije.20170706214722.1: *4* elif data
    elif kind == 'data':
        value = get_data(node)
    #@+node:vitalije.20170707132224.1: *4* elif enabled_plugins
    elif kind == 'enabled_plugins':
        value = get_enabled_plugins(node)
    #@+node:vitalije.20170707132301.1: *4* elif float
    elif kind == 'float':
        try:
            value = float(value)
        except ValueError:
            valueError(kind, name, value)
            return
    #@+node:vitalije.20170707140655.1: *4* elif int
    elif kind == 'int':
        try:
            value = int(value)
        except ValueError:
            valueError(kind, name, value)
            return
    #@+node:vitalije.20170707143252.1: *4* elif ints
    elif kind == 'ints':
        try:
            (kind, name, value) = get_ints(name, value)
        except ValueError:
            # error reported in get_ints
            return
    #@+node:vitalije.20170707154737.1: *4* elif ratio
    elif kind == 'ratio':
        try:
            value = float(value)
            if value < 0 or value > 1.0:
                raise ValueError
        except ValueError:
            valueError(kind, name, value)
            return
    #@+node:vitalije.20170707160350.1: *4* elif strings
    elif kind == 'strings':
        try:
            kind, name, value = get_strings(name, value)
        except ValueError as e:
            g.pr(e.message)
            return
    #@-others
    else:
        raise ValueError('unhandled kind %s'%node.h)
    harvest_one_setting(node.gnx, kind, name, value, conds, acc)
#@+node:vitalije.20170706123955.1: *3* harvest_one_complex_setting
def harvest_one_complex_setting(node, conds, acc):
    kind, name, value = parseHeadline(node.h)
    values = []
    #@+others
    #@+node:vitalije.20170707140157.1: *4* if font
    if kind == 'font':
        get_font(node, values)
    #@+node:vitalije.20170707151859.1: *4* elif menus
    elif kind == 'menus':
        menusList = get_menus_list(node)
        if menusList:
            values.append(('menus', 'menus', menusList))
        else:
            valueError('menus', name, value or node.h)
    #@+node:vitalije.20170707161612.1: *4* elif buttons
    elif kind == 'buttons':
        raise ValueError('buttons')
    #@+node:vitalije.20170707161622.1: *4* elif commands
    elif kind == 'commands':
        raise ValueError('commands')
    #@+node:vitalije.20170707161716.1: *4* elif mode
    elif kind == 'mode':
        raise ValueError('mode')
    #@+node:vitalije.20170707161742.1: *4* elif menuat
    elif kind == 'menuat':
        raise ValueError('menuat')
    #@+node:vitalije.20170707161803.1: *4* elif openwith
    elif kind == 'openwith':
        raise ValueError('openwith')
    #@+node:vitalije.20170707161900.1: *4* elif outlinedata
    elif kind == 'openwith':
        raise ValueError('openwith')
    #@+node:vitalije.20170707162334.1: *4* elif popup
    elif kind == 'popup':
        raise ValueError('popup')
    #@+node:vitalije.20170707161820.1: *4* elif shortcuts
    elif kind == 'shortcuts':
        raise ValueError('shortcuts')
    #@-others
    for (kind, name, value) in values:
        harvest_one_setting(node.gnx, kind, name, value, conds, acc)

#@+node:vitalije.20170706071117.1: *3* settings_harvester
def settings_harvester(node, conds, acc):
    if conds:
        if isSimpleSetting(node):
            harvest_one_simple_setting(node, conds, acc)
        elif isCondition(node):
            descend(node, conds + [node], acc)
        elif isComplexSetting(node):
            harvest_one_complex_setting(node, conds, acc)
        elif node.h.startswith('@ignore'):
            pass
        else:
            descend(node, conds, acc)
    elif node.h.startswith('@ignore'):
        pass
    elif node.h.startswith(g.u('@settings')):
        descend(node, [True], acc)
    else:
        descend(node, conds, acc)
#@+node:vitalije.20170706214907.1: *3* valueError
def valueError(kind, name, value):
    """Give an error: val is not valid for kind."""
    g.pr("%s is not a valid %s for %s" % (value, kind, name))
#@+node:vitalije.20170704202637.1: ** vnode_data
def vnode_data(vns, seq):
    for gnx in seq:
        v = vns[gnx]
        yield (gnx, v[0], v[1], v[2], g.u(' ').join(v[3]), v[4], 0, v[5])
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
#@-others

def main(src, dest):
    print('src', src)
    print('dest', dest)
    root = get_leo_data(g.readFileIntoEncodedString(src))
    root.gnx = 'hidden-root-vnode-gnx'
    vns, seq = walk_tree(root)
    data = vnode_data(vns, seq[1:]) # skip hidden root
    with sqlite3.connect(dest) as conn:
        resetdb(conn)
        conn.executemany(sqls('insert-vnode'), data)
        conn.commit()
    acc = []
    settings_harvester(root, [], acc)
    for gnx, kind, name, value, cond in acc:
        if kind == g.u('data'):
            value = repr(value)[:30]
        
        print(cond or "always", kind, name, pprint.pformat(value))
            
if __name__ == '__main__':
    src = g.os_path_finalize_join(g.os_path_dirname(__file__),
         '../config/myLeoSettings.leo')
    if len(sys.argv) > 1:
        src = sys.argv[1]
    dest = src[:-3] + 'db'
    main(src, dest)
    print('ok')
#@-leo
