"""
leo_cloud.py - synchronize Leo subtrees with remote central server

Terry N. Brown, terrynbrown@gmail.com, Fri Sep 22 10:34:10 2017

(this is the Leo plugin half, see also leo_cloud_server.py)

Sub-trees include head and body content *and* v.u

## Phase 1

On load, on save, and on demand, synchronize @leo_cloud subtrees with
remote server by complete download / upload

## Phase 2

Maybe more granular and regular synchronization.

 - experiments show recursive hash of 7000 node subtree, covering
   v.h, v.b, and v.u, can be done in 0.02 seconds on a 4GHz CPU.

## General notes

 - todo.py used to put datetime.datetime objects in v.u, the tags.py
   plugin puts set() objects in v.u.  Neither are JSON serializable.
   Plan is to serialize to text (ISO date and JSON list), and not
   fix on the way back in - tags.py can coerce the things it expects
   to be sets to be sets.

 - for Phase 1 functionality at least it might be possible to use
   non-server back ends like Google Drive / Drop Box / git / WebDAV.
   Probably worth a layer to handle this for people with out access to a
   server.

 - goal would be for an older Raspberry Pi to be sufficient server
   wise, so recursive hash speed there might be an issue (Phase 2)

"""

# pylint: disable=unused-import
import json
import os
import re
import shlex
import subprocess
from datetime import date, datetime
from hashlib import sha1

import leo.core.leoGlobals as g
from leo.core.leoNodes import vnode

from leo.core.leoQt import QtCore  # see QTimer in LeoCloud.__init__

# for 'key: value' lines in body text
KWARG_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_]*): (.*)")

def init ():
    g.registerHandler(('new','open2'), onCreate)
    g.registerHandler(('save1'), onSave)
    g.plugin_signon(__name__)
    return True

def onCreate (tag, keys):

    c = keys.get('c')
    if not c:
        return

    c._leo_cloud = LeoCloud(c)

def onSave(tag, keys):

    c = keys.get('c')
    if not c:
        return

    if getattr(c, '_leo_cloud'):
        c._leo_cloud.save_clouds()

    return None  # explicitly not stopping save1 hook

@g.command("lc-read-current")
def lc_read_current(event):
    """write current Leo Cloud subtree to cloud"""
    c = event.get('c')
    if not c or not hasattr(c, '_leo_cloud'):
        return
    c._leo_cloud.read_current()

@g.command("lc-write-current")
def lc_write_current(event):
    """write current Leo Cloud subtree to cloud"""
    c = event.get('c')
    if not c or not hasattr(c, '_leo_cloud'):
        return
    c._leo_cloud.write_current()

class LeoCloudIOBase:
    """Leo Cloud IO layer Base Class

    LeoCloudIO layer sits between LeoCloud plugin and backends,
    which might be leo_cloud_server.py or Google Drive etc. etc.
    """
    def __init__(self, c, p, kwargs):
        """
        :param context c: Leo outline
        :param position p: @leo_cloud position
        :param dict kwargs: key word args from p.b
        """
        self.v = p.v
        self.c = c
        self.lc_id = kwargs['ID']

    def get_subtree(self, lc_id):
        """get_subtree - get a Leo subtree from the cloud

        :param str(?) lc_id: resource to get
        :returns: vnode build from lc_id
        """
        # pylint: disable=no-member
        # self.get_data
        return self.c._leo_cloud.from_dict(self.get_data(lc_id))

    def put_subtree(self, lc_id, v):
        """put - put a subtree into the Leo Cloud

        :param str(?) lc_id: place to put it
        :param vnode v: subtree to put
        """
        # pylint: disable=no-member
        # self.put_data
        self.put_data(lc_id, LeoCloud.to_dict(v))


class LeoCloudIOFileSystem(LeoCloudIOBase):
    """Leo Cloud IO layer that just loads / saves local files.

    i.e it's just for development / testing
    """
    def __init__(self, c, p, kwargs):
        """
        :param str basepath: root folder for data
        """
        LeoCloudIOBase.__init__(self, c, p, kwargs)
        self.basepath = kwargs['root']
        if not os.path.exists(self.basepath):
            os.makedirs((self.basepath))

    def get_data(self, lc_id):
        """get_data - get a Leo Cloud resource

        :param str(?) lc_id: resource to get
        :returns: object loaded from JSON
        """
        filepath = os.path.join(self.basepath, lc_id+'.json')
        with open(filepath) as data:
            return json.load(data)

    def put_data(self, lc_id, data):
        """put - store data in the Leo Cloud

        :param str(?) lc_id: place to put it
        :param obj data: data to store
        """
        filepath = os.path.join(self.basepath, lc_id+'.json')
        with open(filepath, 'w') as out:
            return out.write(LeoCloud.to_json(data))


class LeoCloudIOGit(LeoCloudIOBase):
    """Leo Cloud IO layer that just loads / saves local files.

    i.e it's just for development / testing
    """
    def __init__(self, c, p, kwargs):
        """
        :param str basepath: root folder for data
        """
        # if p.v._leo_cloud_io was used, we'd probably also need to pull
        # in get_data(), so don't bother with p.v._leo_cloud_io
        # p.v._leo_cloud_io = self
        LeoCloudIOBase.__init__(self, c, p, kwargs)
        self.remote = kwargs['remote']
        self.local = os.path.expanduser(kwargs['local'])
        if not os.path.exists(self.local):
            os.makedirs((self.local))
        if not os.listdir(self.local):
            self._run_git('git clone "%s" "%s"'% (self.remote, self.local))
        self._run_git('git -C "%s" pull' % self.local)

    def _run_git(self, text):
        """_run_git - run a git command

        :param str text: command to run
        """
        subprocess.Popen(shlex.split(text)).wait()

    def get_data(self, lc_id):
        """get_data - get a Leo Cloud resource

        :param str(?) lc_id: resource to get
        :returns: object loaded from JSON
        """
        filepath = os.path.join(self.local, lc_id+'.json')
        with open(filepath) as data:
            return json.load(data)

    def put_data(self, lc_id, data):
        """put - store data in the Leo Cloud

        :param str(?) lc_id: place to put it
        :param obj data: data to store
        """
        filepath = os.path.join(self.local, lc_id+'.json')
        with open(filepath, 'w') as out:
            out.write(LeoCloud.to_json(data))
        self._run_git('git -C "%s" add "%s"' % (self.local, lc_id+'.json'))
        self._run_git('git -C "%s" commit -mupdates' % self.local)
        self._run_git('git -C "%s" push' % self.local)


class LeoCloud:
    def __init__(self, c):
        """
        :param context c: Leo context
        """
        self.c = c

        # we're here via open2 hook, but too soon to load from cloud,
        # so defer
        QtCore.QTimer.singleShot(0, self.load_clouds)

    def find_at_leo_cloud(self, p):
        """find_at_leo_cloud - find @leo_cloud node

        :param position p: start from here, work up
        :return: position or None
        """
        while not p.h.startswith("@leo_cloud") and p.parent():
            p = p.parent()
        if not p.h.startswith("@leo_cloud"):
            g.es("No @leo_cloud node found", color='red')
            return
        return p

    def _find_clouds_recursive(self, v, found):
        """see find_clouds()"""
        if v.h.startswith('@ignore'):
            return
        if v.h.startswith('@leo_cloud'):
            found.add(v)
            return
        else:
            for child in v.children:
                self._find_clouds_recursive(child, found)

    def find_clouds(self):
        """find_clouds - return a list of @leo_cloud nodes

        respects @ignore in headlines, doesn't recurse into @leo_cloud nodes
        """
        found = set()
        self._find_clouds_recursive(self.c.hiddenRootNode, found)
        valid = []
        for lc in found:
            if 'ID' in self.kw_from_node(lc):
                valid.append(lc)
            else:
                g.es('%s - no ID: line' % lc.h, color='red')
        return valid

    def _from_dict_recursive(self, top, d):
        """see from_dict()"""
        top.h = d['h']
        top.b = d['b']
        top.u = d['u']
        top.children[:] = []
        for child in d['children']:
            top.children.append(self._from_dict_recursive(vnode(self.c), child))
        return top

    def from_dict(self, d):
        """from_dict - make a Leo subtree from a dict

        :param dict d: input dict
        :return: vnode
        """
        return self._from_dict_recursive(vnode(self.c), d)

    def io_from_node(self, p):
        """io_from_node - create LeoCloudIO instance from body text

        :param position p: node containing text
        :return: LeoCloudIO instance
        """
        kwargs = self.kw_from_node(p)
        # pylint: disable=eval-used
        lc_io_class = eval("LeoCloudIO%s" % kwargs['type'])
        return lc_io_class(self.c, p, kwargs)

    def kw_from_node(self, p):
        """kw_from_node - read keywords from body text

        :param position p: node containing text
        :return: dict
        """
        kwargs = {}
        for line in p.b.split('\n'):
            kwarg = KWARG_RE.match(line)
            if kwarg:
                kwargs[kwarg.group(1)] = kwarg.group(2)
        return kwargs

    def load_clouds(self):
        """check for clouds to load on startup"""
        skipped = []
        for lc_v in self.find_clouds():
            kwargs = self.kw_from_node(lc_v)
            read = False
            read_on_load = kwargs.get('read_on_load', '').lower()
            if read_on_load == 'yes':
                read = True
            elif read_on_load == 'ask':
                read = g.app.gui.runAskYesNoCancelDialog(self.c, "Read cloud data?",
                    message="Read cloud data '%s', overwriting local nodes?" % kwargs['ID'])
                read = str(read).lower() == 'yes'
            if read:
                self.read_current(p=self.c.vnode2position(lc_v))
            elif read_on_load == 'no':
                g.es("NOTE: not reading '%s' from cloud" % kwargs['ID'])
            elif read_on_load != 'ask':
                skipped.append(kwargs['ID'])
        if skipped:
            g.app.gui.runAskOkDialog(self.c, "Unloaded cloud data",
                message="There is unloaded (possibly stale) could data, use\nread_on_load: yes|no|ask\n"
                  "in @leo_cloud nodes to avoid this message.\nUnloaded data:\n%s" % ', '.join(skipped))

    def read_current(self, p=None):
        """read_current - read current tree from cloud
        """
        if p is None:
            p = self.find_at_leo_cloud(self.c.p)
        if not p:
            return
        old_p = self.c.p.copy()
        g.es("Reading from cloud...")  # some io's as slow to init. - reassure user
        # io's can cache themselves on the vnode, but should think hard
        # about whether they want to
        lc_io = getattr(p.v, '_leo_cloud_io', None) or self.io_from_node(p)

        v = lc_io.get_subtree(lc_io.lc_id)
        p.deleteAllChildren()
        for child_n, child in enumerate(v.children):
            child._addLink(child_n, p.v)
        if hasattr(self.c, 'cleo'):
            self.c.cleo.loadAllIcons()
        self.c.redraw(p=old_p if self.c.positionExists(old_p) else p)
        g.es("Read %s" % lc_io.lc_id)
        # set c changed but don't dirty tree, which would cause
        # write to cloud prompt on save
        self.c.setChanged(changedFlag=True)

    @staticmethod
    def recursive_hash(nd, tree, include_current=True):
        """
        recursive_hash - recursively hash a tree

        :param vnode nd: node to hahs
        :param list tree: recursive list of hashes
        :param bool include_current: include h/b/u of current node in hash?
        :return: sha1 hash of tree
        :rtype: str

        Calling with include_current=False ignores the h/b/u of the top node
        """
        childs = []
        hashes = [LeoCloud.recursive_hash3(child, childs) for child in nd.children]
        if include_current:
            hashes.extend([nd.h + nd.b + str(nd.u)])
            # FIXME: random sorting on nd.u, use JSON/sorted keys
        whole_hash = sha1(''.join(hashes).encode('utf-8')).hexdigest()
        tree.append([whole_hash, childs])
        return whole_hash

    def save_clouds(self):
        """check for clouds to save when outline is saved"""
        skipped = []
        for lc_v in self.find_clouds():
            kwargs = self.kw_from_node(lc_v)
            write = False
            write_on_save = kwargs.get('write_on_save', '').lower()
            if not self.subtree_changed(lc_v):
                write_on_save = 'unchanged'
            if write_on_save == 'yes':
                write = True
            elif write_on_save == 'ask':
                write = g.app.gui.runAskYesNoCancelDialog(self.c, "Write cloud data?",
                    message="Write cloud data '%s', overwriting remote version?" % kwargs['ID'])
                write = str(write).lower() == 'yes'
            if write:
                self.write_current(p=self.c.vnode2position(lc_v))
            elif write_on_save == 'no':
                g.es("NOTE: not writing '%s' to cloud" % kwargs['ID'])
            elif write_on_save == 'unchanged':
                g.es("NOTE: not writing unchanged '%s' to cloud" % kwargs['ID'])
            elif write_on_save != 'ask':
                skipped.append(kwargs['ID'])
        if skipped:
            g.app.gui.runAskOkDialog(self.c, "Unsaved cloud data",
                message="There is unsaved could data, use\nwrite_on_save: yes|no|ask\n"
                  "in @leo_cloud nodes to avoid this message.\nUnsaved data:\n%s" % ', '.join(skipped))

    def subtree_changed(self, p):
        """subtree_changed - check if subtree is changed

        :param position p: top of subtree
        :return: bool
        """
        if isinstance(p, vnode):
            p = self.c.vnode2position(p)
        for nd in p.self_and_subtree_iter():
            if nd.isDirty():
                break
        else:
            return False
        return True

    @staticmethod
    def _to_json_serial(obj):
        """JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, set):
            return list(obj)
        raise TypeError ("Type %s not serializable" % type(obj))

    @staticmethod
    def to_json(data):
        """to_json - convert dict to appropriate JSON

        :param dict data: data to convert
        :return: json
        :rtype: str
        """
        return json.dumps(
            data,
            sort_keys=True,  # prevent unnecessary diffs
            indent=0,        # make json readable on cloud web pages
            default=LeoCloud._to_json_serial
        )

    @staticmethod
    def _to_dict_recursive(v, d):
        """_to_dict_recursive - recursively make dictionary representation of v

        :param vnode v: subtree to convert
        :param dict d: dict for results
        :return: dict of subtree
        """
        d['b'] = v.b
        d['h'] = v.h
        d['u'] = v.u
        d['children'] = []
        for child in v.children:
            d['children'].append(LeoCloud._to_dict_recursive(child, dict()))
        return d

    @staticmethod
    def to_dict(v):
        """to_dict - make dictionary representation of v

        :param vnode v: subtree to convert
        :return: dict of subtree
        """
        return LeoCloud._to_dict_recursive(v, dict())

    def write_current(self, p=None):
        """write_current - write current tree to cloud
        """
        if p is None:
            p = self.find_at_leo_cloud(self.c.p)
        if not p:
            return
        g.es("Storing to cloud...")  # some io's as slow to init. - reassure user
        lc_io = getattr(p.v, '_leo_cloud_io', None) or self.io_from_node(p)
        lc_io.put_subtree(lc_io.lc_id, p.v)
        g.es("Stored %s" % lc_io.lc_id)

"""Notes / code for recursive hashes

from hashlib import sha1, md5
import json
import timeit

# using c.all_unique_nodes()

def hashy():
    n = 0
    for nd in c.all_unique_nodes():
        sha1(
            nd.h.encode('utf-8') +
            nd.b.encode('utf-8') +
            str(nd.u).encode('utf-8')
        ).hexdigest()
        n += 1
    # g.es(n)
n = 10
g.es(timeit.timeit(hashy, number=n) / n)

# not storing

def recursive_hash(nd):
    hashes = [recursive_hash(child) for child in nd.children]
    hashes.extend([nd.h + nd.b + str(nd.u)])
    return sha1(''.join(hashes).encode('utf-8')).hexdigest()

def test_recurse():
    return recursive_hash(c.hiddenRootNode)

g.es(timeit.timeit(test_recurse, number=n) / n)

# using dicts

def recursive_hash2(nd, tree):
    childs = {}
    hashes = [recursive_hash2(child, childs) for child in nd.children]
    hashes.extend([nd.h + nd.b + str(nd.u)])
    whole_hash = sha1(''.join(hashes).encode('utf-8')).hexdigest()
    tree[whole_hash] = childs
    return whole_hash

def test_recurse2():
    return recursive_hash2(c.hiddenRootNode, {})

g.es(timeit.timeit(test_recurse2, number=n) / n)

# using lists

def recursive_hash3(nd, tree):
    childs = []
    hashes = [recursive_hash3(child, childs) for child in nd.children]
    hashes.extend([nd.h + nd.b + str(nd.u)])
    whole_hash = sha1(''.join(hashes).encode('utf-8')).hexdigest()
    tree.append([whole_hash, childs])
    return whole_hash

def test_recurse3():
    return recursive_hash3(c.hiddenRootNode, [])

g.es(timeit.timeit(test_recurse2, number=n) / n)

# comparison

g.es(test_recurse())
g.es(test_recurse2())
g.es(test_recurse3())

# save

all = []
recursive_hash3(c.hiddenRootNode, all)
with open("/tmp/json_hashes.json", 'w') as out:
    json.dump(all, out)
"""


