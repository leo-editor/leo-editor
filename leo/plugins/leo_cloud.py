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

import json
import os
import re
import shlex
import subprocess
import sys
from collections import namedtuple, defaultdict

import leo.core.leoGlobals as g
from leo.core.leoNodes import vnode

# for 'key: value' lines in body text
KWARG_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_]*): (.*)")

def init ():
    g.registerHandler(('new','open2'),onCreate)
    g.plugin_signon(__name__)
    return True

def onCreate (tag, keys):

    c = keys.get('c')
    if not c:
        return

    c._leo_cloud = LeoCloud(c)

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
        return self.c._leo_cloud.from_dict(self.get_data(lc_id))

    def put_subtree(self, lc_id, v):
        """put - put a subtree into the Leo Cloud

        :param str(?) lc_id: place to put it
        :param vnode v: subtree to put
        """
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
            return json.dump(data, out)


class LeoCloudIOGit(LeoCloudIOBase):
    """Leo Cloud IO layer that just loads / saves local files.

    i.e it's just for development / testing
    """
    def __init__(self, c, p, kwargs):
        """
        :param str basepath: root folder for data
        """
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
            json.dump(data, out)
        self._run_git('git -C "%s" add "%s"' % (self.local, lc_id+'.json'))
        self._run_git('git -C "%s" commit -mupdates' % self.local)
        self._run_git('git -C "%s" push' % self.local)


class LeoCloud:
    def __init__(self, c):
        """
        :param context c: Leo context
        """
        self.c = c

    def find_at_leo_cloud(self, p):
        """find_at_leo_cloud - find @leo_cloud node

        :param position p: start from here, work up
        :return: position or None
        """
        while not p.h.startswith("@leo_cloud ") and p.parent():
            p = p.parent()
        if not p.h.startswith("@leo_cloud"):
            g.es("No @leo_cloud node found", color='red')
            return
        return p

    def _from_dict_recursive(self, top, d):
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
        kwargs = {}
        for line in p.b.split('\n'):
            kwarg = KWARG_RE.match(line)
            if kwarg:
                kwargs[kwarg.group(1)] = kwarg.group(2)
        lc_io_class = eval("LeoCloudIO%s" % kwargs['type'])
        return lc_io_class(self.c, p, kwargs)

    def read_current(self):
        """read_current - read current tree from cloud
        """
        p = self.find_at_leo_cloud(self.c.p)
        if not p:
            return
        lc_io = getattr(p.v, '_leo_cloud_io', None) or self.io_from_node(p)
        v = lc_io.get_subtree(lc_io.lc_id)
        p.deleteAllChildren()
        for child_n, child in enumerate(v.children):
            # child._cutLink(child_n, v)
            child._addLink(child_n, p.v)
        # p.v.children = v.children
        self.c.redraw(p=p)
        g.es("Loaded %s" % lc_io.lc_id)

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

    def write_current(self):
        """write_current - write current tree to cloud
        """
        p = self.find_at_leo_cloud(self.c.p)
        if not p:
            return
        g.es("Storing to cloud...")  # some io's as slow to init. - reassure user
        lc_io = getattr(p.v, '_leo_cloud_io', None) or self.io_from_node(p)
        lc_io.put_subtree(lc_io.lc_id, p.v)
        g.es("Stored %s" % lc_io.lc_id)



