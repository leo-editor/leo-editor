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
   non-server backends like Google Drive / Drop Box / git / WebDAV.
   Probably worth a layer to handle this for people with out access to a
   server.

 - goal would be for an older Raspberry Pi to be sufficient server
   wise, so recursive hash speed there might be an issue (Phase 2)

"""

import os
import sys
from collections import namedtuple, defaultdict

import leo.core.leoGlobals as g
from leo.core.leoNodes import vnode

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

@g.command("lc-write-current")
def lc_write_current(event):
    """write current Leo Cloud subtree to cloud"""
    c = event.get('c')
    if not c or not hasattr(c, '_leo_cloud'):
        return

class LeoCloudIOABC:
    """Leo Cloud IO layer "Abstract" Base Class

    LeoCloudIO layer sits between LeoCloud plugin and backends,
    which might be leo_cloud_server.py or Google Drive etc. etc.
    """
    pass

class LeoCloudIOFileSystem(LeoCloudIOABC):
    """Leo Cloud IO layer that just loads / saves local files.

    i.e it's just for development / testing
    """
    def __init__(self, basepath):
        """
        :param str basepath: root folder for data
        """
        self.basepath = basepath
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

    def get_subtree(self, lc_id):
        """get_subtree - get a Leo subtree from the cloud

        :param str(?) lc_id: resource to get
        :returns: vnode build from lc_id
        """
        return LeoCloud.from_dict(self.get_data(lc_id))

    def put_data(self, lc_id, data):
        """put - store data in the Leo Cloud

        :param str(?) lc_id: place to put it
        :param obj data: data to store
        """
        filepath = os.path.join(self.basepath, lc_id+'.json')
        with open(filepath, 'w') as out:
            return json.dump(LeoCloud.to_json(data), out)

    def put_subtree(self, lc_id, v):
        """put - put a subtree into the Leo Cloud

        :param str(?) lc_id: place to put it
        :param vnode v: subtree to put
        """
        self.put_data(LeoCloud.to_json(v), lc_id)


class LeoCloud:
    def __init__(self, c):
        """
        :param context c: Leo context
        """
        self.c = c

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

    @staticmethod
    def to_json(v):
        """to_json - make JSON representation of v

        :param vnode v: subtree to convert
        :return: JSON for subtree
        :rtype: str
        """
        return json.dumps(LeoCloud.to_dict(v))



