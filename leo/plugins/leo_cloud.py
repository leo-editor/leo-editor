#@+leo-ver=5-thin
#@+node:ekr.20170925083314.1: * @file ../plugins/leo_cloud.py
#@+<< docstring >>
#@+node:ekr.20210518113636.1: ** << docstring >>
"""
leo_cloud.py - synchronize Leo subtrees with remote central server

Terry N. Brown, terrynbrown@gmail.com, Fri Sep 22 10:34:10 2017

This plugin allows subtrees within a .leo file to be stored in the cloud. It
should be possible to support various cloud platforms, currently git and systems
like DropBox are supported (i.e. you can use GitLab or GitHub or your own remote
git server).

A leo_cloud subtree has a top node with a headline that starts with
'@leo_cloud'. The rest of the headline is ignored. The body of this top node is
used to describe the cloud service, e.g.:

type: Git
remote: git@gitlab.com:tnbrown/leo_cloud_storage.git
local: ~/.leo/leo_cloud/gitlab_leo_cloud_storage
ID: shortcuts
read_on_load: ask
write_on_save: ask

The first three lines can be repeated with different IDs to store
different subtrees at the same remote cloud location.

read_on_load: / write_on_save: can be yes, no, ask, or background (read_on_load
only). If it's not one of those three, there's a warning dialog. `background`
performs a check against the cloud in the background, and then behaves like
`ask` if a difference is detected.

There's also a file system backend, which would look like this:

type: FileSystem
root: ~/DropBox/leo_cloud
ID: my_notes
read_on_load: ask
write_on_save: ask

If you set up the FileSystem backend it into a folder that is sync'ed
externally, as shown above, it can serve as a cloud adapter for services like
DropBox, Google Drive, OneDrive, etc. etc.

In addition to the Git and FileSystem cloud types it should be possible to add
many others - AWS, WebDAV, sFTP, whatever.

FYI: https://gitlab.com/ gives you free private repos.

The plugin stores headline, body, and uA (unknown attributes). The caveat is
that it must be JSON serializable, this is to avoid pickle flavor issues. I
don't think this will cause problems except for legacy datetime objects from the
todo.py plugin and set()s in the tags plugin. I think both can be fixed easily -
a custom JSON writer can write datetime as iso string time and sets as lists,
and the tags plugin can coerce lists to sets. I think the todo.py plugin already
reads iso string time values.

My intended use was a common synchronized todo list across machines, which this
achieves.

An unintended bonus is that you can use it to sync. your settings across
machines easily too. Like this:

@settings
  @keys
    @leo_cloud
      @shortcuts

"just works", so now your shortcuts etc. can be stored on a central
server.
"""
#@-<< docstring >>
#@+<< imports >>
#@+node:ekr.20210518113710.1: ** << imports >>
import json
import os
import re
import shlex
import subprocess
import tempfile
import threading
from typing import Any
from copy import deepcopy
from datetime import date, datetime
from hashlib import sha1
from leo.core import leoGlobals as g
from leo.core.leoNodes import vnode
from leo.core.leoQt import QtCore  # see QTimer in LeoCloud.__init__
#
# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.
#@-<< imports >>

# for 'key: value' lines in body text
KWARG_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_]*): (.*)")

#@+others
#@+node:ekr.20201012111338.3: ** init (leo_cloud.py)
def init():
    g.registerHandler(('new', 'open2'), onCreate)
    g.registerHandler(('save1'), onSave)
    g.plugin_signon(__name__)
    return True

#@+node:ekr.20201012111338.4: ** onCreate (leo_cloud.py)
def onCreate(tag, keys):

    c = keys.get('c')
    if not c:
        return

    c._leo_cloud = LeoCloud(c)

#@+node:ekr.20201012111338.5: ** onSave (leo_cloud.py)
def onSave(tag, keys):

    c = keys.get('c')
    if not c:
        return None
    if getattr(c, '_leo_cloud'):
        c._leo_cloud.save_clouds()
    return None  # explicitly not stopping save1 hook

#@+node:ekr.20201012111338.6: ** lc_read_current (leo_cloud.py)
@g.command("lc-read-current")
def lc_read_current(event):
    """write current Leo Cloud subtree to cloud"""
    c = event.get('c')
    if not c or not hasattr(c, '_leo_cloud'):
        return
    c._leo_cloud.read_current()

#@+node:ekr.20201012111338.7: ** lc_write_current (leo_cloud.py)
@g.command("lc-write-current")
def lc_write_current(event):
    """write current Leo Cloud subtree to cloud"""
    c = event.get('c')
    if not c or not hasattr(c, '_leo_cloud'):
        return
    c._leo_cloud.write_current()

#@+node:ekr.20201012111338.8: ** class LeoCloudIOBase
class LeoCloudIOBase:
    """Leo Cloud IO layer Base Class

    LeoCloudIO layer sits between LeoCloud plugin and backends,
    which might be leo_cloud_server.py or Google Drive etc. etc.
    """
    #@+others
    #@+node:ekr.20201012111338.9: *3* LeoCloudIOBase.__init__
    def __init__(self, c, p, kwargs):
        """
        Args:
            c (context): Leo outline
            p (position): @leo_cloud position
            kwargs (dict): key word args from p.b
        """
        self.v = p.v
        self.c = c
        self.lc_id = kwargs['ID']

    #@+node:ekr.20201012111338.10: *3* LeoCloudIOBase.get_subtree
    def get_subtree(self, lc_id):
        """get_subtree - get a Leo subtree from the cloud

        Args:
            lc_id (str(?)): resource to get

        :returns: vnode build from lc_id
        """
        # pylint: disable=no-member
        # self.get_data
        return self.c._leo_cloud.from_dict(self.get_data(lc_id))

    #@+node:ekr.20201012111338.11: *3* LeoCloudIOBase.put_subtree
    def put_subtree(self, lc_id, v):
        """put - put a subtree into the Leo Cloud

        Args:
            lc_id (str(?)): place to put it
            v (vnode): subtree to put
        """
        # pylint: disable=no-member
        # self.put_data
        self.put_data(lc_id, LeoCloud.to_dict(v))


    #@-others
#@+node:ekr.20201012111338.12: ** class LeoCloudIOFileSystem(LeoCloudIOBase)
class LeoCloudIOFileSystem(LeoCloudIOBase):
    """Leo Cloud IO layer that just loads / saves local files.

    i.e it's just for development / testing
    """
    #@+others
    #@+node:ekr.20201012111338.13: *3* LeoCloudIOFileSystem(LeoCloudIOBase).__init__
    def __init__(self, c, p, kwargs):
        """
        Args:
            basepath (str): root folder for data
        """
        LeoCloudIOBase.__init__(self, c, p, kwargs)
        self.basepath = os.path.expanduser(kwargs['root'])
        if not os.path.exists(self.basepath):
            os.makedirs((self.basepath))

    #@+node:ekr.20201012111338.14: *3* LeoCloudIOFileSystem(LeoCloudIOBase).get_data
    def get_data(self, lc_id):
        """get_data - get a Leo Cloud resource

        Args:
            lc_id (str(?)): resource to get

        Returns:
            object loaded from JSON
        """
        filepath = os.path.join(self.basepath, lc_id + '.json')
        with open(filepath) as data:
            return json.load(data)

    #@+node:ekr.20201012111338.15: *3* LeoCloudIOFileSystem(LeoCloudIOBase).put_data
    def put_data(self, lc_id, data):
        """put - store data in the Leo Cloud

        Args:
            lc_id (str(?)): place to put it
            data (obj): data to store
        """
        filepath = os.path.join(self.basepath, lc_id + '.json')
        with open(filepath, 'w') as out:
            return out.write(LeoCloud.to_json(data))


    #@-others
#@+node:ekr.20201012111338.16: ** class LeoCloudIOGit(LeoCloudIOBase)
class LeoCloudIOGit(LeoCloudIOBase):
    """Leo Cloud IO layer that just loads / saves local files.

    i.e it's just for development / testing
    """
    #@+others
    #@+node:ekr.20201012111338.17: *3* LeoCloudIOGit(LeoCloudIOBase).__init__
    def __init__(self, c, p, kwargs):
        """
        Args:
            basepath (str): root folder for data
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
            self._run_git('git clone "%s" "%s"' % (self.remote, self.local))
        self._run_git('git -C "%s" pull' % self.local)

    #@+node:ekr.20201012111338.18: *3* LeoCloudIOGit(LeoCloudIOBase)._run_git
    def _run_git(self, text):
        """_run_git - run a git command

        Args:
            text (str): command to run
        """
        subprocess.Popen(shlex.split(text)).wait()

    #@+node:ekr.20201012111338.19: *3* LeoCloudIOGit(LeoCloudIOBase).get_data
    def get_data(self, lc_id):
        """get_data - get a Leo Cloud resource

        Args:
            lc_id (str(?)): resource to get

        :returns: object loaded from JSON
        """
        filepath = os.path.join(self.local, lc_id + '.json')
        with open(filepath) as data:
            return json.load(data)

    #@+node:ekr.20201012111338.20: *3* LeoCloudIOGit(LeoCloudIOBase).put_data
    def put_data(self, lc_id, data):
        """put - store data in the Leo Cloud

        Args:
            lc_id (str(?)): place to put it
            data (obj): data to store
        """
        filepath = os.path.join(self.local, lc_id + '.json')
        with open(filepath, 'w') as out:
            out.write(LeoCloud.to_json(data))
        self._run_git('git -C "%s" add "%s"' % (self.local, lc_id + '.json'))
        self._run_git('git -C "%s" commit -mupdates' % self.local)
        self._run_git('git -C "%s" push' % self.local)


    #@-others
#@+node:ekr.20201012111338.21: ** class LeoCloud
class LeoCloud:
    #@+others
    #@+node:ekr.20201012111338.22: *3* LeoCloud.__init__
    def __init__(self, c):
        """
        Args:
            c (context): Leo context    """
        self.c = c
        self.bg_finished = False  # used for background thread
        self.bg_results = []  # results from background thread

        # we're here via open2 hook, but too soon to load from cloud,
        # so defer
        QtCore.QTimer.singleShot(0, self.load_clouds)

    #@+node:ekr.20201012111338.23: *3* LeoCloud.bg_check
    def bg_check(self, to_check):
        """
        bg_check - run from load_clouds() to look for changes in
        cloud in background.

        WARNING: no gui impacting calls allowed here (g.es() etc.)

        Args:
            to_check (list): list of (vnode, kwargs, hash) tuples to check

        This (background) thread can't handle any changes found, because it
        would have to interact with the user and GUI code can only be called
        from the main thread.  We don't want to use QThread, to allow this to
        work without Qt.  So we just collect results and set
        self.bg_finished = True, which the main thread watches using g.IdleTime()

        """
        for v, kwargs, local_hash in to_check:
            c = v.context
            p = c.vnode2position(v)
            lc_io = getattr(v, '_leo_cloud_io', None) or self.io_from_node(p)
            subtree = lc_io.get_subtree(lc_io.lc_id)
            remote_hash = self.recursive_hash(subtree, [], include_current=False)
            self.bg_results.append((v, local_hash == remote_hash))
            if False and local_hash != remote_hash:
                # disabled dev. / debug code
                # record difference for inspection
                tmpdir = tempfile.mkdtemp()
                with open(os.path.join(tmpdir, 'leo_cloug_local.json'), 'w') as out:
                    out.write(self.to_json(self.to_dict(v)))
                with open(os.path.join(tmpdir, 'leo_cloug_remote.json'), 'w') as out:
                    out.write(self.to_json(self.to_dict(subtree)))

        self.bg_finished = True
    #@+node:ekr.20201012111338.24: *3* LeoCloud.bg_post_process
    def bg_post_process(self, timer):
        """
        bg_post_process - check to see if background checking is finished,
        handle any changed cloud trees found

        Args:
            timer (leo-idle-timer): Leo idle timer
        """
        if not self.bg_finished:
            return
        timer.stop()
        from_background = set()
        for v, unchanged in self.bg_results:
            kwargs = self.kw_from_node(v)
            if unchanged:
                g.es("Cloud tree '%s' unchanged" % kwargs['ID'])
            else:
                from_background.add((kwargs['remote'], kwargs['ID']))
                g.es("Cloud tree '%s' DOES NOT MATCH" % kwargs['ID'])
        if from_background:
            self.load_clouds(from_background=from_background)

    #@+node:ekr.20201012111338.25: *3* LeoCloud.find_at_leo_cloud
    def find_at_leo_cloud(self, p):
        """find_at_leo_cloud - find @leo_cloud node

        Args:
            p (position): start from here, work up

        Returns:
            position or None
        """
        while not p.h.startswith("@leo_cloud") and p.parent():
            p = p.parent()
        if not p.h.startswith("@leo_cloud"):
            g.es("No @leo_cloud node found", color='red')
            return None
        return p
    #@+node:ekr.20201012111338.26: *3* LeoCloud._find_clouds_recursive
    def _find_clouds_recursive(self, v, found):
        """see find_clouds()"""
        if v.h.startswith('@ignore'):
            return
        if v.h.startswith('@leo_cloud'):
            found.add(v)
            return
        for child in v.children:
            self._find_clouds_recursive(child, found)

    #@+node:ekr.20201012111338.27: *3* LeoCloud.find_clouds
    def find_clouds(self):
        """find_clouds - return a list of @leo_cloud nodes

        respects @ignore in headlines, doesn't recurse into @leo_cloud nodes
        """
        found: set = set()
        self._find_clouds_recursive(self.c.hiddenRootNode, found)
        valid = []
        for lc in found:
            if 'ID' in self.kw_from_node(lc):
                valid.append(lc)
            else:
                g.es('%s - no ID: line' % lc.h, color='red')
        return valid

    #@+node:ekr.20201012111338.28: *3* LeoCloud._from_dict_recursive
    def _from_dict_recursive(self, top, d):
        """see from_dict()"""
        top.h = d['h']
        top.b = d['b']
        top.u = d['u']
        top.children[:] = []
        for child in d['children']:
            top.children.append(self._from_dict_recursive(vnode(self.c), child))
        return top

    #@+node:ekr.20201012111338.29: *3* LeoCloud.from_dict
    def from_dict(self, d):
        """from_dict - make a Leo subtree from a dict

        Args:
            d (dict): input dict

        Returns:
            vnode
        """
        return self._from_dict_recursive(vnode(self.c), d)

    #@+node:ekr.20201012111338.30: *3* LeoCloud.io_from_node
    def io_from_node(self, p):
        """io_from_node - create LeoCloudIO instance from body text

        Args:
            p (position): node containing text

        Returns:
            LeoCloudIO instance
        """
        kwargs = self.kw_from_node(p)
        # pylint: disable=eval-used
        lc_io_class = eval("LeoCloudIO%s" % kwargs['type'])
        return lc_io_class(self.c, p, kwargs)

    #@+node:ekr.20201012111338.31: *3* LeoCloud.kw_from_node
    def kw_from_node(self, p):
        """kw_from_node - read keywords from body text

        Args:
            p (position): node containing text

        Returns:
            dict
        """
        kwargs: dict[str, Any] = {'remote': None}
        # some methods assume 'remote' exists, but it's absent in LeoCloudIOFileSystem
        for line in p.b.split('\n'):
            kwarg = KWARG_RE.match(line)
            if kwarg:
                kwargs[kwarg.group(1)] = kwarg.group(2)
        return kwargs

    #@+node:ekr.20201012111338.32: *3* LeoCloud.load_clouds
    def load_clouds(self, from_background=None):
        """
        load_clouds - Handle loading from cloud on startup and after
        background checking for changes.

        Args:
            from_background (set): set of (remote, ID) str tuples if we're
            called after a background check process finds changes.
        """
        if from_background is None:
            from_background = set()
        skipped = []
        background = []  # things to check in background
        for lc_v in self.find_clouds():
            kwargs = self.kw_from_node(lc_v)
            if from_background and \
                (kwargs['remote'], kwargs['ID']) not in from_background:
                # only process nodes from the background checking
                continue
            read = False
            read_on_load = kwargs.get('read_on_load', '').lower()
            if from_background:
                # was 'background', changes found, so now treat as 'ask'
                read_on_load = 'ask'
            if read_on_load == 'yes':
                read = True
            elif read_on_load == 'ask':
                try:
                    last_read = datetime.strptime(
                        lc_v.u['_leo_cloud']['last_read'], "%Y-%m-%dT%H:%M:%S.%f")
                except KeyError:
                    last_read = None
                message = "Read cloud data '%s', overwriting local nodes?" % kwargs['ID']
                if last_read:
                    delta = datetime.now() - last_read
                    message = "%s\n%s, %sh:%sm:%ss ago" % (
                        message, last_read.strftime("%a %b %d %H:%M"),
                        24 * delta.days + int(delta.seconds / 3600),
                        int(delta.seconds / 60) % 60,
                        delta.seconds % 60)
                read = g.app.gui.runAskYesNoCancelDialog(self.c, "Read cloud data?",
                    message=message)
                read = str(read).lower() == 'yes'
            if read:
                self.read_current(p=self.c.vnode2position(lc_v))
            elif read_on_load == 'background':
                # second time round, with from_background data, this will
                # have been changed to 'ask' (above), so no infinite loop
                background.append((lc_v, kwargs,
                    self.recursive_hash(lc_v, [], include_current=False)))
            elif read_on_load == 'no':
                g.es("NOTE: not reading '%s' from cloud" % kwargs['ID'])
            elif read_on_load != 'ask':
                skipped.append(kwargs['ID'])
        if skipped:
            g.app.gui.runAskOkDialog(self.c, "Unloaded cloud data",
                message="There is unloaded (possibly stale) cloud data, use\nread_on_load: yes|no|ask\n"
                  "in @leo_cloud nodes to avoid this message.\nUnloaded data:\n%s" % ', '.join(skipped))

        if background:
            # send to background thread for checking
            names = ', '.join([i[1]['ID'] for i in background])
            g.es("Checking cloud trees in background:\n%s" % names)
            thread = threading.Thread(target=self.bg_check, args=(background,))
            thread.start()
            # start watching for results
            g.IdleTime(self.bg_post_process).start()
    #@+node:ekr.20201012111338.33: *3* LeoCloud.read_current
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
        # but... (a) top node is ending up dirty anyway, and (b) this is ok
        # because we want the user to understand why the outline's changed,
        # so just ignore top node dirtiness in self.subtree_changed()
        self.c.setChanged()
        p.v.u.setdefault('_leo_cloud', {})['last_read'] = datetime.now().isoformat()


    #@+node:ekr.20201012111338.34: *3* LeoCloud.recursive_hash
    @staticmethod
    def recursive_hash(nd, tree, include_current=True):
        """
        recursive_hash - recursively hash a tree

        Args:
            nd (vnode): node to hash
            tree (list): recursive list of hashes
            include_current (bool): include h/b/u of current node in hash?

        Returns:
            str: sha1 hash of tree

        Calling with include_current=False ignores the h/b/u of the top node

        To hash a dict, need a string representation
        that sorts keys, i.e. json.dumps(s, sort_keys=True)

        Trailing newlines are ignored in body text.
        """
        childs: list = []
        hashes: list = [LeoCloud.recursive_hash(child, childs) for child in nd.children]
        if include_current:
            hashes.extend([nd.h + nd.b.rstrip('\n') + json.dumps(LeoCloud._ua_clean(nd.u), sort_keys=True)])
        whole_hash = sha1(''.join(hashes).encode('utf-8')).hexdigest()
        tree.append([whole_hash, childs])
        return whole_hash
    #@+node:ekr.20201012111338.35: *3* LeoCloud.save_clouds
    def save_clouds(self):
        """check for clouds to save when outline is saved"""
        skipped = []
        no = []
        unchanged = []
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
                no.append(kwargs['ID'])
            elif write_on_save == 'unchanged':
                unchanged.append(kwargs['ID'])
            elif write_on_save != 'ask':
                skipped.append(kwargs['ID'])
        if skipped:
            g.app.gui.runAskOkDialog(self.c, "Unsaved cloud data",
                message="There is unsaved cloud data, use\nwrite_on_save: yes|no|ask\n"
                  "in @leo_cloud nodes to avoid this message.\nUnsaved data:\n%s" % ', '.join(skipped))
        if unchanged:
            g.es("Unchanged cloud data: %s" % ', '.join(unchanged))
        if no:
            g.es("Cloud data never saved: %s" % ', '.join(no))

    #@+node:ekr.20201012111338.36: *3* LeoCloud.subtree_changed
    def subtree_changed(self, p):
        """subtree_changed - check if subtree is changed

        Args:
            p (position): top of subtree

        Returns:
            bool
        """
        if isinstance(p, vnode):
            p = self.c.vnode2position(p)
        for nd in p.subtree_iter():
            if nd.isDirty():
                break
        else:
            return False
        return True

    #@+node:ekr.20201012111338.37: *3* LeoCloud._to_json_serial
    @staticmethod
    def _to_json_serial(obj):
        """JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, set):
            return list(obj)
        raise TypeError("Type %s not serializable" % type(obj))

    #@+node:ekr.20201012111338.38: *3* LeoCloud.to_json
    @staticmethod
    def to_json(data):
        """to_json - convert dict to appropriate JSON

        Args:
            data (dict): data to convert

        Returns:
            str: json
        """
        return json.dumps(
            data,
            sort_keys=True,  # prevent unnecessary diffs
            indent=0,  # make json readable on cloud web pages
            default=LeoCloud._to_json_serial
        )

    #@+node:ekr.20201012111338.39: *3* LeoCloud._to_dict_recursive
    @staticmethod
    def _to_dict_recursive(v, d):
        """_to_dict_recursive - recursively make dictionary representation of v

        Args:
            v (vnode): subtree to convert
            d (dict): dict for results

        Returns:
            dict of subtree
        """
        d['b'] = v.b
        d['h'] = v.h
        d['u'] = v.u
        d['children'] = []
        for child in v.children:
            d['children'].append(LeoCloud._to_dict_recursive(child, dict()))
        return d

    #@+node:ekr.20201012111338.40: *3* LeoCloud.to_dict
    @staticmethod
    def to_dict(v):
        """to_dict - make dictionary representation of v

        Args:
            v (vnode): subtree to convert

        Returns:
            dict of subtree
        """
        return LeoCloud._to_dict_recursive(v, dict())

    #@+node:ekr.20201012111338.41: *3* LeoCloud._ua_clean
    @staticmethod
    def _ua_clean(d):
        """_ua_clean - strip todo icons from dict

        Args:
            d (dict): dict to clean

        Returns:
            cleaned dict

        recursive_hash() to compare trees stumbles on todo icons which are
        derived information from the todo attribute and include *local*
        paths to icon images
        """

        d = deepcopy(d)
        if 'icons' in d:
            d['icons'] = [i for i in d['icons'] if not i.get('cleoIcon')]
        return d

    #@+node:ekr.20201012111338.42: *3* LeoCloud.write_current
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
        # writing counts as reading, last read time msg. confusing otherwise
        p.v.u.setdefault('_leo_cloud', {})['last_read'] = datetime.now().isoformat()





    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
