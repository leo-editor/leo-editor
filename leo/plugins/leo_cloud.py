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

def init ():

    # g.registerHandler(('new','open2'),onCreate)
    g.plugin_signon(__name__)

def onCreate (tag, keys):

    c = keys.get('c')
    if not c:
        return

    c._leo_cloud = LeoCloud(c)

@g.command("lc-read-current")
def lc_read_current(event):
    """write current Leo Cloud subtree to cloud"""
@g.command("lc-write-current")
def lc_write_current(event):
    """write current Leo Cloud subtree to cloud"""
class LeoCloudIOABC:
    """Leo Cloud IO layer "Abstract" Base Class
    
    LeoCloudIO layer sits between LeoCloud plugin and backends,
    which might be leo_cloud_server.py or Google Drive etc. etc.    
    """
    pass

class LeoCloudIOFileSystem(LeoCloudIOABC):
    """Leo Cloud IO layer that just loads / saves local files"""
    def get(self, lc_id):
        """get - get a Leo Cloud resource

        :param str(?) lc_id: resource to get
        """
        filepath = os.path.join(self.basepath, lc_id+'.json')
        with open(filepath) as data:
            return json.load(data)

    def put(self, vnode, lc_id):
        """put - put a subtree into the Leo Cloud

        :param Vnode vnode: subtree to put
        :param str(?) lc_id: place to put it
        """
        filepath = os.path.join(self.basepath, lc_id+'.json')
        with open(filepath, 'w') as data:
            return json.dump(LeoCloud.to_json(vnode), data)



class LeoCloud:
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
            d['children'].append(_to_dict_recursive(child, dict()))
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


