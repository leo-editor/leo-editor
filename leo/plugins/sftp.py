#@+leo-ver=5-thin
#@+node:peckj.20140811080604.9496: * @file ../plugins/sftp.py
#@+<< docstring >>
#@+node:peckj.20140218144401.6036: ** << docstring >>
"""@edit-like functionality for remote files over SFTP

By Jacob M. Peck

@sftp nodes
===========

This plugin requires the python module 'paramiko' to be installed.

This plugin operates on @sftp nodes, which are defined as nodes
with headlines that start with `@sftp` and follow one of the following
patterns::

    @sftp username@host!port:path/to/remote.file
    @sftp username@host:path/to/remote.file
    @sftp host!port:path/to/remote.file
    @sftp host:path/to/remote.file

This headline tells the sftp plugin almost all it needs to know to connect to
the remote server and edit the file. If the username is omitted, it defaults to
your LeoID. If the port is omitted, it defaults to 22, the standard sftp port.

General usage
=============

Generally, you'll create an empty node with a proper @sftp headline, and then
run the minibuffer command `sftp-pull`. When you're satisfied with your edits,
you can then run the command `sftp-push` to push your changes back to the
server.

On passwords and host keys
==========================

This plugin checks host-keys before communicating with the remote server. The
first time you connect to a remote server per Leo session, you'll need to agree
to let the host-key into your trusted hosts list. This is a Leo-centric list,
and does not use your operating system's known_hosts file, in order to keep it
platform independent.

Similarly, this plugin does not (yet) use SSH key-based authentication. It will
instead prompt you for your password the first time you connect to a server per
Leo session. Future attempts will be cached, in order to cut down on typing. You
can use the `@bool sftp-cache-credentials` setting to prevent password caching.


Configuration Settings
======================

This plugin is configured with the following @settings:

@bool sftp-cache-credentials = True
-----------------------------------

Set this to False to make sftp.py prompt you for a password on each connection.


Commands
========

This plugin provides the following commands:

sftp-push
---------

Overwrites the file on the remote server with the contents of the body of the
currently selected @sftp node.

sftp-push-all
-------------

Runs an `sftp-push` on all @sftp nodes in the current outline.

sftp-pull
---------

Replaces the body of the currently selected @sftp node with the contents of the
file on the remote server.

sftp-pull-all
-------------

Runs an `sftp-pull` on all @sftp nodes in the current outline.

sftp-forget-credentials
-----------------------

Makes sftp.py forget your entered passwords. Only available if `@bool
sftp-cache-credentials = True`.

"""
#@-<< docstring >>
#@+<< imports >>
#@+node:peckj.20140218144401.6038: ** << imports >>
from leo.core import leoGlobals as g

try:
    import paramiko
except ImportError:
    paramiko = None
    if not g.unitTesting:
        print('sftp.py: can not import paramiko')

from leo.core.leoQt import QtWidgets
#
# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.
#@-<< imports >>

#@+others
#@+node:peckj.20140218144401.6039: ** init
def init():
    # if g.app.gui is None:
    #    g.app.createQtGui(__file__)
    ok = g.app.gui.guiName().startswith('qt') and paramiko is not None
    if ok:
        g.registerHandler(('new', 'open2'), onCreate)
        g.plugin_signon(__name__)
    else:
        g.es('Module \'paramiko\' not installed.  Plugin sftp.py not loaded.', color='red')

    return ok
#@+node:peckj.20140218144401.6040: ** onCreate
def onCreate(tag, keys):

    c = keys.get('c')
    if not c:
        return

    theSFTPController = SFTPController(c)
    c.theSFTPController = theSFTPController
#@+node:peckj.20140218144401.6041: ** class SFTPController
class SFTPController:

    #@+others
    #@+node:peckj.20140218144401.6042: *3* __init__(SFTPController)
    def __init__(self, c):

        self.c = c
        # Warning: hook handlers must use keywords.get('c'), NOT self.c.

        self._CACHE_CREDENTIALS = c.config.getBool('sftp-cache-credentials', True)

        # register commands
        c.k.registerCommand('sftp-push', self.sftp_push)
        c.k.registerCommand('sftp-push-all', self.sftp_push_all)
        c.k.registerCommand('sftp-pull', self.sftp_pull)
        c.k.registerCommand('sftp-pull-all', self.sftp_pull_all)
        if self._CACHE_CREDENTIALS:
            c.k.registerCommand('sftp-forget-credentials', self.sftp_forget_credentials)

    #@+node:peckj.20140218144401.6157: *3* helpers
    #@+node:peckj.20140218144401.6158: *4* log
    def log(self, s, color=None):
        if color:
            g.es('sftp.py:', s, color=color)
        else:
            g.es('sftp.py:', s)
    #@+node:peckj.20140218144401.6159: *4* get_params
    def get_params(self, headline):
        """ headline in the format:
        @sftp username@hostname!port:path/to/remote/file
        or
        @sftp username@hostname:path/to/remote/file
        or
        @sftp hostname!port:path/to/remote/file
        or
        @sftp hostname:path/to/remote/file
        """
        username = None
        port = None
        headline = headline.split(' ', 1)[1]  # strip the @sftp bit
        has_username = '@' in headline
        has_port = '!' in headline
        has_path = ':' in headline
        if not has_path:
            self.log("ERROR: need a file path!", color='red')
            return None
        remotefile = headline.split(':')[1].strip()
        if not remotefile:
            self.log("ERROR: need a file path!", color='red')
            return None
        if has_port:
            try:
                port = int(headline[headline.find('!') + 1 : headline.find(':')])
            except Exception:
                self.log("ERROR parsing port.  Falling back to port 22.", color='red')
        if has_username:
            username = headline.split('@', 1)[0]
            if not username:
                self.log("ERROR parsing username.  Falling back to leoID value.", color='red')
        hostname = headline.split(':')[0]
        if has_port:
            hostname = hostname.split('!')[0]
        if has_username:
            hostname = hostname.split('@')[1]
        if not port:
            port = 22
        if not username:
            username = g.app.leoID
        return {'port': port, 'hostname': hostname, 'username': username, 'remotefile': remotefile}
    #@+node:peckj.20140218144401.6160: *4* get_password
    def get_password(self, username, hostname):
        if self._CACHE_CREDENTIALS:
            key = '%s@%s' % (username, hostname)
            d = g.user_dict.get('sftp', {})
            pw = d.get(key, None)
            if pw is not None:
                return pw
        message = "Please enter password for user '%s' on host '%s':" % (username, hostname)
        parent = None
        title = "Enter Password"
        # Mode is valid keyword.
        password, ok = QtWidgets.QInputDialog.getText(  # type:ignore
            parent, title, message, mode=QtWidgets.QLineEdit.Password)
        password = str(password)
        if ok is False:
            return None
        if self._CACHE_CREDENTIALS:
            d[key] = password
            g.user_dict['sftp'] = d
        return password
    #@+node:peckj.20140218144401.6161: *4* confirm_hostkey
    def confirm_hostkey(self, title, message):
        answer = g.app.gui.runAskYesNoDialog(self.c, title, message)
        return answer == 'yes'
    #@+node:peckj.20140218144401.6162: *4* get_hostkey
    def get_hostkey(self, host):
        d = g.user_dict.get('sftp-hostkeys', {})
        return d.get(host, None)
    #@+node:peckj.20140218144401.6163: *4* set_hostkey
    def set_hostkey(self, host, key):
        d = g.user_dict.get('sftp-hostkeys', {})
        d[host] = key
        g.user_dict['sftp-hostkeys'] = d
    #@+node:peckj.20140218144401.6164: *4* establish_connection
    def establish_connection(self, p):
        params = self.get_params(p.h)
        host = params['hostname']
        port = params['port']
        user = params['username']
        # remotefile = params['remotefile']
        passwd = self.get_password(user, host)
        if passwd is None:
            return (None, None)
        t = paramiko.Transport((host, port))
        t.connect(username=user, password=passwd)
        hostkey = t.get_remote_server_key()
        cached_hostkey = self.get_hostkey(host)
        if cached_hostkey is None:
            store = self.confirm_hostkey(
                'Unknown host: %s' % host,
                'Add the server key for host \'%s\' to the trusted host list?' % host)
            if store:
                self.set_hostkey(host, hostkey)
            else:
                return (None, None)  # abort
        elif cached_hostkey != hostkey:
            store = self.confirm_hostkey(
                'Hostkey does not match!\n',
                f"The remote host {host!r} provided a key that does not match the stored key.\n"
                'This could indicate a man-in-the-middle attack.  Continue anyway?'
            )
            if store:
                self.set_hostkey(host, hostkey)
            else:
                return (None, None)  # abort
        sftp = paramiko.SFTPClient.from_transport(t)
        return (t, sftp)
    #@+node:peckj.20140218144401.6172: *3* commands
    #@+node:peckj.20140218144401.6173: *4* sftp_pull
    def sftp_pull(self, event=None, p=None):
        """Replaces the body of the currently selected @sftp
           node with the contents of the file on the remote server.
        """
        if p is None:
            p = self.c.p
        if p.h.startswith('@sftp'):
            self.log('Pulling node %s' % p.h, color='blue')
            try:
                t, sftp = self.establish_connection(p)
                if t is not None:
                    remotefile = self.get_params(p.h)['remotefile']
                    data = sftp.open(remotefile, 'r').read()
                    p.b = data
                    t.close()
            except Exception:
                self.log('Communications error!', color='red')
        else:
            self.log('Not an @sftp node!', color='red')
    #@+node:peckj.20140218144401.6174: *4* sftp_pull_all
    def sftp_pull_all(self, event=None):
        """Runs an `sftp-pull` on all @sftp nodes in the current outline."""
        c = self.c
        self.log('Pulling all @sftp nodes.', color='blue')
        for n in c.all_unique_nodes():
            if n.h.startswith('@sftp'):
                self.sftp_pull(p=c.vnode2position(n))
        self.log('Done pulling all @sftp nodes.', color='blue')
    #@+node:peckj.20140218144401.6175: *4* sftp_push
    def sftp_push(self, event=None, p=None):
        """Overwrites the file on the remote server with
           the contents of the body of the currently selected
           @sftp node.
        """
        if p is None:
            p = self.c.p
        if p.h.startswith('@sftp'):
            self.log('Pushing node %s' % p.h, color='blue')
            try:
                t, sftp = self.establish_connection(p)
                if t is not None:
                    remotefile = self.get_params(p.h)['remotefile']
                    data = p.b
                    sftp.open(remotefile, 'w').write(data)
                    p.b = data
                    t.close()
            except Exception:
                self.log('Communications error!', color='red')

        else:
            self.log('Not an @sftp node!', color='red')
    #@+node:peckj.20140218144401.6176: *4* sftp_push_all
    def sftp_push_all(self, event=None):
        """Runs an `sftp-push` on all @sftp nodes in the current outline."""
        c = self.c
        self.log('Pushing all @sftp nodes.', color='blue')
        for n in c.all_unique_nodes():
            if n.h.startswith('@sftp'):
                self.sftp_push(p=c.vnode2position(n))
        self.log('Done with push all command.', color='blue')
    #@+node:peckj.20140218144401.6177: *4* sftp_forget_credentials
    def sftp_forget_credentials(self, event=None):
        """Makes sftp.py forget your entered passwords."""
        g.user_dict['sftp'] = {}
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
