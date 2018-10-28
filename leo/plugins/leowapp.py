# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20181028052650.1: * @file leowapp.py
#@@first
#@+<< docstring >>
#@+node:ekr.20181028052650.2: ** << docstring >>
#@@language rest
#@@wrap
'''Leo as a web app: contains python and javascript sides.

StartLeo with the --gui=browser command-line option. This will show a
"chooser page" in your default browser, showing one link for every open
.leo file.

You can use the browser's refresh button to update the top-level view in
the browser after you have opened or closed files.

The web page contains::

    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js">
    <script src="<a fixed script, defined in this file"></script>
    <style src="leowapp_default.css">
    <style src="leowapp_user.css">

Settings
--------

``@string leowapp_ip = 127.0.0.1``
    address to bind to, see notes below
    
    IP address 127.0.0.1 is accessible by all users logged into your local
    machine. That means while Leo and mod_http is running anyone logged
    into your machine will be able to browse all your leo outlines.

    If you want all other network accessible machines to have access
    to your mod_http instance, then use @string leowapp_ip = 0.0.0.0.

``@int  leowapp_port = 8100``
    The port.
    
``@data leowapp_stylesheet``
    The default .css for this page.
    
``@data leowapp_user_stylesheet``
    Additional .css for this page.
'''
#@-<< docstring >>
#@+<< imports >>
#@+node:ekr.20181028052650.3: ** << imports >>
# pylint: disable=deprecated-method
    # parse_qs
import leo.core.leoGlobals as g
import asynchat
import asyncore
import cgi
import json
if g.isPython3:
    import http.server
    SimpleHTTPRequestHandler = http.server.SimpleHTTPRequestHandler
else:
    import SimpleHTTPServer
    SimpleHTTPRequestHandler = SimpleHTTPServer.SimpleHTTPRequestHandler
if g.isPython3:
    import io
    StringIO = io.StringIO
    BytesIO = io.BytesIO
else:
    import io
    import StringIO # Python 2.x
    StringIO = StringIO.StringIO
    BytesIO = io.BytesIO
if g.isPython3:
    # pylint: disable=no-name-in-module
    import urllib.parse as urlparse
else:
    import urlparse
import os
import select
import shutil
import socket
import time
from xml.sax.saxutils import quoteattr
#@-<< imports >>
#@+<< data >>
#@+node:ekr.20181028052650.4: ** << data >>
browser_encoding = 'utf-8'
    # To do: Can we query the browser for this?
    # This encoding must match the character encoding used in your browser.
    # If it does not, non-ascii characters will look very strange.

sockets_to_close = []
#@-<< data >>
#@+<< leowapp_js >>
#@+node:ekr.20181028071923.1: ** << leowapp_js >>
#@@language javascript

leowapp_js = """\
$(document).ready(function(){
    // Toggle (hide) all but top-level *nodes*.
    // Headlines are *always* visible.
    $("div.node").hide()
    $(".outlinepane").children("div.node").show();
    // Attach borders to *headlines*.
    $("div.headline").addClass('unborderclass')
    $(".outlinepane").children("div.node").children("div.headline:first").removeClass('unborderclass');
    $(".outlinepane").children("div.node").children("div.headline:first").addClass('borderclass');
    // Set h attributes for css
    // $("headline").attr("icon_url", "http://leoeditor.com/box" + $("headline").attr("icon") + ".GIF")
        // Works, but I haven't found how to use it.
    $("div.headline").click(function(e){
        e.stopImmediatePropagation()
            // Google: jquery click event called twice.
        // Toggle the expansion state.
        $(e.target).parent().children("div.node").toggle()
        // Set the body text.
        $(".body-code").text($(e.target).attr("b"));
        // Set the border
        $("div.headline").removeClass('borderclass');
        $("div.headline").addClass('unborderclass');
        $(e.target).removeClass('unborderclass');
        $(e.target).addClass('borderclass');
        // console.clear();
        // console.log($(e.target));
        // console.log($(e.target).children("div.node").length);
        // console.log($(e.target).children("div.node").children("div.headline").length);
        //console.log($(e.target).attr("b").length);
        //console.log($(e.target).children(":first"));
        //console.log($(e.target).children(":first").is(":visible"));
    });
});
"""
#@-<< leowapp_js >>
#@+others
#@+node:ekr.20181028052650.11: ** class config
class config(object):

    leowapp_timeout = 0
    leowapp_ip = '127.0.0.1'
    leowapp_port = 8100
    ### We must have two ports

#@+node:ekr.20181028052650.12: ** class delayedSocketStream
class delayedSocketStream(asyncore.dispatcher_with_send):
    #@+others
    #@+node:ekr.20181028052650.13: *3* __init__
    def __init__(self, sock):
        # pylint: disable=super-init-not-called
        self._map = asyncore.socket_map
        self.socket = sock
        self.socket.setblocking(0)
        self.closed = 1 # compatibility with SocketServer
        self.buffer = []
    #@+node:ekr.20181028052650.14: *3* write
    def write(self, data):
        self.buffer.append(data)
    #@+node:ekr.20181028052650.15: *3* initiate_sending
    def initiate_sending(self):
        # Create a bytes string.
        aList = [g.toEncodedString(z) for z in self.buffer]
        self.out_buffer = b''.join(aList)
        del self.buffer
        self.set_socket(self.socket, None)
        self.socket.setblocking(0)
        self.connected = 1
        try:
            self.addr = self.socket.getpeername()
        except socket.error:
            # The addr isn't crucial
            pass
    #@+node:ekr.20181028052650.16: *3* handle_read
    def handle_read(self):
        g.trace()
        ### pass
    #@+node:ekr.20181028052650.17: *3* writable
    def writable(self):
        result = (not self.connected) or len(self.out_buffer)
        if not result:
            sockets_to_close.append(self)
        return result
    #@-others
#@+node:ekr.20181028052650.40: ** class ExecHandler
class ExecHandler(object):
    """
    Quasi-RPC GET based interface
    """
    #@+others
    #@+node:ekr.20181028052650.41: *3* __init__
    def __init__(self, request_handler):
        self.request_handler = request_handler
    #@+node:ekr.20181028052650.42: *3* get_response
    def get_response(self):
        """Return the file like 'f' that leo_interface.send_head makes"""
        # self.request_handler.path.startswith('/_/exec/')

        if not g.app.config.getBool("http-allow-remote-exec"):
            return None  # fail deliberately
            
        c = g.app and g.app.log and g.app.log.c
        if c and config.enable is None:
            if c.config.isLocalSetting('http-allow-remote-exec', 'bool'):
                g.issueSecurityWarning('@bool http-allow-remote-exec')
                config.enable = False
            else:
                config.enable = True

        parsed_url = urlparse.urlparse(self.request_handler.path)
        query = urlparse.parse_qs(parsed_url.query)

        enc = query.get("enc", ["str"])[0]

        if parsed_url.path.startswith('/_/exec/commanders/'):
            ans = [i.fileName() for i in g.app.commanders()]
            if enc != 'json':
                ans = '\n'.join(ans)
        else:
            ans = self.proc_cmds()

        f = StringIO()
        f.mime_type = query.get("mime_type", ["text/plain"])[0]
        enc = query.get("enc", ["str"])[0]
        if enc == 'json':
            f.write(json.dumps(ans))
        elif enc == 'repr':
            f.write(repr(ans))
        else:
            f.write(str(ans))
        return f

    #@+node:ekr.20181028052650.43: *3* proc_cmds (mod_http.py)
    def proc_cmds(self):

        parsed_url = urlparse.urlparse(self.request_handler.path)
        query = urlparse.parse_qs(parsed_url.query)
        # work out which commander to use, zero index int, full path name, or file name
        c_idx = query.get('c', [0])[0]
        if c_idx is not 0:
            try:
                c_idx = int(c_idx)
            except ValueError:
                paths = [i.fileName() for i in g.app.commanders()]
                if c_idx in paths:
                    c_idx = paths.index(c_idx)
                else:
                    paths = [os.path.basename(i) for i in paths]
                    c_idx = paths.index(c_idx)
        ans = None
        c = g.app.commanders()[c_idx]
        if c and c.evalController:
            for cmd in query['cmd']:
                ans = c.evalController.eval_text(cmd)
        return ans  # the last answer, if multiple commands run
    #@-others
#@+node:ekr.20181028052650.18: ** class leo_interface
class leo_interface(object):
    # pylint: disable=no-member
        # .path, .send_error, .send_response and .end_headers
        # appear to be undefined.
    #@+others
    #@+node:ekr.20181028052650.19: *3* send_head & helpers
    def send_head(self):
        """Common code for GET and HEAD commands.

         This sends the response code and MIME headers.

         Return value is either a file object (which has to be copied
         to the outputfile by the caller unless the command was HEAD,
         and must be closed by the caller under all circumstances), or
         None, in which case the caller has nothing further to do.

         """
        try:
            # self.path is provided by the RequestHandler class.
            path = self.split_leo_path(self.path)
            if path[0] == '_':
                f = self.leo_actions.get_response()
            ###
                # elif len(path) == 1 and path[0] == 'favicon.ico':
                    # f = self.leo_actions.get_favicon()
            elif path == '/':
                f = self.write_leo_windowlist()
            else:
                try:
                    window, root = self.find_window_and_root(path)
                    if window is None:
                        self.send_error(404, "File not found")
                        return None
                    if root is None:
                        self.send_error(404, "No root node")
                        return None
                    f = StringIO()
                    self.write_leo_tree(f, window, root)
                except nodeNotFound:
                    self.send_error(404, "Node not found")
                    return None
                except noLeoNodePath:
                    g.es("No Leo node path:", path)
                    # Is there something better we can do here?
                    self.send_error(404, "Node not found")
                    return None
            if f is None:
                return
            length = f.tell()
            f.seek(0)
            self.send_response(200)
            self.send_header("Content-type", getattr(f, "mime_type", "text/html"))
            self.send_header("Content-Length", str(length))
            self.end_headers()
            return f
        except Exception:
            import traceback
            traceback.print_exc()
            raise
    #@+node:ekr.20181028052650.20: *4* find_window_and_root
    def find_window_and_root(self, path):
        """
        given a path of the form:
            [<short filename>,<number1>,<number2>...<numbern>]
            identify the leo node which is in that file, and,
            from top to bottom, is the <number1> child of the topmost
            node, the <number2> child of that node, and so on.

            Return None if that node can not be identified that way.
        """
        for w in g.app.windowList:
            if w.shortFileName() == path[0]:
                return w, w.c.rootPosition()
        return None, None
    #@+node:ekr.20181028052650.21: *4* split_leo_path
    def split_leo_path(self, path):
        '''Split self.path.'''
        if path == '/':
            return '/'
        if path.startswith("/"):
            path = path[1:]
        return path.split('/')
    #@+node:ekr.20181028052650.22: *4* write_leo_tree & helpers
    def write_leo_tree(self, f, window, root):
        '''Wriite the entire html file to f.'''
        root = root.copy()
        self.write_head(f, root.h, window)
        f.write('<body>')
        f.write('<div class="container">')
        f.write('<div class="outlinepane">')
        f.write('<h1>%s</h1>' % window.shortFileName())
        for sib in root.self_and_siblings():
            self.write_node_and_subtree(f, sib)
        f.write('</div>')
        f.write('</div>')
        self.write_body_pane(f, root)
        f.write('</body></html>')
    #@+node:ekr.20181028052650.23: *5* write_body_pane
    def write_body_pane(self, f, p):

        f.write('<div class="bodypane">')
        f.write('<pre class="body-text">')
        f.write('<code class="body-code">%s</code>' % escape(p.b))
            # This isn't correct when put in a triple string.
            # We might be able to use g.adjustTripleString, but this works.
        f.write('</pre></div>')
    #@+node:ekr.20181028052650.24: *5* write_head
    def write_head(self, f, headString, window):

        f.write("""\
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html>
    <head>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
        <style>%s</style>
        <style>%s</style>
        <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js"></script>
        <script>%s</script>
        <title>%s</title>
    </head>
    """ % (
        getData('leowapp_stylesheet'),
        getData('leowapp_user_stylesheet'),
        leowapp_js,
        (escape(window.shortFileName() + ":" + headString)))
    )

    #@+node:ekr.20181028052650.25: *5* write_node_and_subtree
    def write_node_and_subtree(self, f, p):

        # This organization, with <headline> elements in <node> elements,
        # allows proper highlighting of nodes.
        f.write('<div class="node" id=n:%s>' % (
            quoteattr(p.gnx),
        ))
        f.write('<div class="headline" id=h:%s expand="%s" icon="%02d" b=%s>%s</div>' % (
            quoteattr(p.gnx),
            '+' if p.hasChildren() else '-',
            p.computeIcon(),
            quoteattr(p.b),
            escape(p.h),
        ))
        for child in p.children():
            self.write_node_and_subtree(f, child)
        f.write('</div>')
    #@+node:ekr.20181028052650.26: *4* write_leo_windowlist
    def write_leo_windowlist(self):
        f = StringIO()
        f.write('''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html>
    <head>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
        <style>%s</style>
        <style>%s</style>
        <title>ROOT for LEO HTTP plugin</title>
    </head>
    <body>
        <h1>Windowlist</h1>
        <hr />
        <ul>
    ''' % (
        getData('leowapp_stylesheet'),
        getData('leowapp_user_stylesheet'),
    ))
        a = g.app # get the singleton application instance.
        windows = a.windowList # get the list of all open frames.
        for w in windows:
            shortfilename = w.shortFileName()
            f.write('<li><a href="%s">"file name: %s"</a></li>' % (
                shortfilename, shortfilename))
        f.write('</ul><hr /></body></html>')
        return f
    #@+node:ekr.20181028052650.27: *3* node_reference & helpers
    def node_reference(self, vnode):
        """
        Given a position p, return the name of the node.

        This is called from leo.core.leoRst.
        """
        # 1. Find the root
        root = vnode
        parent = root.parent()
        while parent:
            root = parent
            parent = root.parent()
        while root.v._back:
            root.moveToBack()
        # 2. Return the window
        window = [w for w in g.app.windowList if w.c.rootVnode().v == root.v][0]
        result = self.create_leo_h_reference(window, vnode)
        return result
    #@+node:ekr.20181028052650.28: *4* add_leo_links
    def add_leo_links(self, window, node, f):
        """
        Given a node 'node', add links to:
            The next sibling, if any.
            the next node.
            the parent.
            The children, if any.
        """
        # Collecting the navigational links.
        if node:
            nodename = node.h
            threadNext = node.threadNext()
            sibling = node.next()
            parent = node.parent()
            f.write("<p>\n")
            children = []
            firstChild = node.firstChild()
            if firstChild:
                child = firstChild
                while child:
                    children.append(child)
                    child = child.next()
            if threadNext is not None:
                self.create_leo_reference(window, threadNext, "next", f)
            f.write("<br />")
            if sibling is not None:
                self.create_leo_reference(window, sibling, "next Sibling", f)
            f.write("<br />")
            if parent is None:
                self.create_href("/", "Top level", f)
            else:
                self.create_leo_reference(window, parent, "Up", f)
            f.write("<br />")
            f.write("\n</p>\n")
        else:
            # top level
            child = window.c.rootPosition()
            children = [child]
            next = child.next()
            while next:
                child = next
                children.append(child)
                next = child.next()
            nodename = window.shortFileName()
        if children:
            f.write("\n<h2>")
            f.write("Children of ")
            f.write(escape(nodename))
            f.write("</h2>\n")
            f.write("<ol>\n")
            for child in children:
                f.write("<li>\n")
                self.create_leo_reference(window, child, child.h, f)
                f.write("</li>\n")
            f.write("</ol>\n")
    #@+node:ekr.20181028052650.29: *4* create_href
    def create_href(self, href, text, f):
        f.write('<a href="%s">' % href)
        f.write(escape(text))
        f.write("</a>\n")
    #@+node:ekr.20181028052650.30: *4* create_leo_h_reference
    def create_leo_h_reference(self, window, node):
        parts = [window.shortFileName()] + self.get_leo_nameparts(node)
        href = '/' + '/'.join(parts)
        return href
    #@+node:ekr.20181028052650.31: *4* create_leo_reference
    def create_leo_reference(self, window, node, text, f):
        """
        Create a reference to 'node' in 'window', displaying 'text'
        """
        href = self.create_leo_h_reference(window, node)
        self.create_href(href, text, f)
    #@+node:ekr.20181028052650.32: *4* write_path
    def write_path(self, node, f):
        result = []
        while node:
            result.append(node.h)
            node = node.parent()
        result.reverse()
        if result:
            result2 = result[: -1]
            if result2:
                result2 = ' / '.join(result2)
                f.write("<p>\n")
                f.write("<br />\n")
                f.write(escape(result2))
                f.write("<br />\n")
                f.write("</p>\n")
            f.write("<h2>")
            f.write(escape(result[-1]))
            f.write("</h2>\n")
    #@-others
#@+node:ekr.20181028052650.33: ** class LeoActions
class LeoActions(object):
    """
    A place to collect other URL based actions like saving bookmarks from
    the browser. Conceptually this stuff could go in class leo_interface
    but putting it here for separation for now.
    """
    #@+others
    #@+node:ekr.20181028052650.34: *3* __init__(LeoActions)
    def __init__(self, request_handler):
        self.request_handler = request_handler
        self.bookmark_unl = g.app.commanders()[0].config.getString('http-bookmark-unl')
        self.exec_handler = ExecHandler(request_handler)
    #@+node:ekr.20181028052650.35: *3* add_bookmark
    def add_bookmark(self):
        """Return the file like 'f' that leo_interface.send_head makes

        """
        parsed_url = urlparse.urlparse(self.request_handler.path)
        query = urlparse.parse_qs(parsed_url.query)
        # print(parsed_url.query)
        # print(query)
        name = query.get('name', ['NO TITLE'])[0]
        url = query['url'][0]
        one_tab_links = []
        if 'www.one-tab.com' in url.lower():
            one_tab_links = query.get('ln', [''])[0]
            one_tab_links = json.loads(one_tab_links)
        c = None # outline for bookmarks
        previous = None # previous bookmark for adding selections
        parent = None # parent node for new bookmarks
        using_root = False
        path = self.bookmark_unl
        if path:
            parsed = urlparse.urlparse(path)
            leo_path = os.path.expanduser(parsed.path)
            c = g.openWithFileName(leo_path, old_c=None)
            if c:
                g.es_print("Opened '%s' for bookmarks" % path)
                if parsed.fragment:
                    g.recursiveUNLSearch(parsed.fragment.split("-->"), c)
                parent = c.currentPosition()
                if parent.hasChildren():
                    previous = parent.getFirstChild()
            else:
                g.es_print("Failed to open '%s' for bookmarks" % self.bookmark_unl)
        if c is None:
            using_root = True
            c = g.app.commanders()[0]
            parent = c.rootPosition()
            previous = c.rootPosition()
        f = StringIO()
        if previous and url == previous.b.split('\n', 1)[0]:
            # another marking of the same page, just add selection
            self.add_bookmark_selection(
                previous, query.get('selection', [''])[0])
            c.selectPosition(previous) # required for body text redraw
            c.redraw()
            f.write("""
    <body onload="setTimeout('window.close();', 350);" style='font-family:mono'>
    <p>Selection added</p></body>"""         )
            return f
        if '_form' in query:
            # got extra details, save to new node
            f.write("""
    <body onload="setTimeout('window.close();', 350);" style='font-family:mono'>
    <p>Bookmark saved</p></body>"""         )
            if using_root:
                nd = parent.insertAfter()
                nd.moveToRoot(c.rootPosition())
            else:
                nd = parent.insertAsNthChild(0)
            if g.pluginIsLoaded('leo.plugins.bookmarks'):
                nd.h = name
            else:
                nd.h = '@url ' + name
            selection = query.get('selection', [''])[0]
            if selection:
                selection = '\n\n"""\n' + selection + '\n"""'
            tags = query.get('tags', [''])[0]
            if one_tab_links:
                if tags:
                    tags += ', OneTabList'
                else:
                    tags = 'OneTabList'
                self.get_one_tab(one_tab_links, nd)
            nd.b = "%s\n\nTags: %s\n\n%s\n\nCollected: %s%s\n\n%s" % (
                url,
                tags,
                query.get('_name', [''])[0],
                time.strftime("%c"),
                selection,
                query.get('description', [''])[0],
            )
            c.setChanged(True)
            c.selectPosition(nd) # required for body text redraw
            c.redraw()
            return f
        # send form to collect extra details
        f.write("""
    <html>
    <head>
        <style>
            body {font-family:mono; font-size: 80%%;}
            th {text-align:right}
        </style>
        <style>%s</style>
    <title>Leo Add Bookmark</title>
    </head>
    <body onload='document.getElementById("tags").focus();'>
        <form method='GET' action='/_/add/bkmk/'>
            <input type='hidden' name='_form' value='1'/>
            <input type='hidden' name='_name' value=%s/>
            <input type='hidden' name='selection' value=%s/>
            <input type='hidden' name='ln' value=%s/>
            <table>
            <tr><th>Tags:</th><td><input id='tags' name='tags' size='60'/>(comma sep.)</td></tr>
            <tr><th>Title:</th><td><input name='name' value=%s size='60'/></td></tr>
            <tr><th>URL:</th><td><input name='url' value=%s size='60'/></td></tr>
            <tr><th>Notes:</th><td><textarea name='description' cols='60' rows='6'></textarea></td></tr>
            </table>
            <input type='submit' value='Save'/><br/>
        </form>
    </body>
    </html>""" % (
            getData('user_bookmark_stylesheet'),  # EKR: Add config.css to style.
            quoteattr(name),
            quoteattr(query.get('selection', [''])[0]),
            quoteattr(json.dumps(one_tab_links)),
            quoteattr(name),
            quoteattr(url)))
        return f
    #@+node:ekr.20181028052650.36: *3* get_one_tab
    def get_one_tab(self, links, nd):
        """get_one_tab - Add child bookmarks from OneTab chrome extension

        :Parameters:
        - `links`: list of {'txt':, 'url':} dicts
        - `nd`: node under which to put child nodes
        """
        for link in links:
            if 'url' in link and 'www.one-tab.com' not in link['url'].lower():
                nnd = nd.insertAsLastChild()
                nnd.h = link['txt']
                nnd.b = "%s\n\nTags: %s\n\n%s\n\nCollected: %s%s\n\n%s" % (
                    link['url'],
                    'OneTabTab',
                    link['txt'],
                    time.strftime("%c"),
                    '',
                    '',
                )
    #@+node:ekr.20181028052650.37: *3* add_bookmark_selection
    def add_bookmark_selection(self, node, text):
        '''Insert the selected text into the bookmark node,
        after any earlier selections but before the users comments.

            http://example.com/

            Tags: tags, are here

            Full title of the page

            Collected: timestamp

            """
            The first saved selection
            """

            """
            The second saved selection
            """

            Users comments

        i.e. just above the "Users comments" line.
        '''
        b = node.b.split('\n')
        insert = ['', '"""', text, '"""']
        collected = None
        tri_quotes = []
        for n, i in enumerate(b):
            if collected is None and i.startswith('Collected: '):
                collected = n
            if i == '"""':
                tri_quotes.append(n)
        if collected is None:
            # not a regularly formatted text, just append
            b.extend(insert)
        elif len(tri_quotes) >= 2:
            # insert after the last balanced pair of tri quotes
            x = tri_quotes[len(tri_quotes) - len(tri_quotes) % 2 - 1] + 1
            b[x: x] = insert
        else:
            # found Collected but no tri quotes
            b[collected + 1: collected + 1] = insert
        node.b = '\n'.join(b)
        node.setDirty()
    #@+node:ekr.20181028052650.38: *3* get_favicon
    def get_favicon(self):
        path = g.os_path_join(g.computeLeoDir(), 'Icons', 'LeoApp16.ico')
        try:
            f = StringIO()
            f2 = open(path)
            s = f2.read()
            f.write(s)
            return f
        except Exception:
            return None
    #@+node:ekr.20181028052650.39: *3* get_response
    def get_response(self):
        """Return the file like 'f' that leo_interface.send_head makes"""
        if self.request_handler.path.startswith('/_/add/bkmk/'):
            return self.add_bookmark()
        if self.request_handler.path.startswith('/_/exec/'):
            return self.exec_handler.get_response()
        f = StringIO()
        f.write("Unknown URL in LeoActions.get_response()")
        return f
    #@-others
#@+node:ekr.20181028052650.44: ** class nodeNotFound
class nodeNotFound(Exception):
    pass
#@+node:ekr.20181028052650.45: ** class noLeoNodePath
class noLeoNodePath(Exception):
    """
    Raised if the path can not be converted a filename and a series of numbers.
    Most likely a reference to a picture.
    """
    pass
#@+node:ekr.20181028052650.46: ** class RequestHandler
class RequestHandler(
    leo_interface,
    asynchat.async_chat,
    SimpleHTTPRequestHandler
):
    # pylint: disable=too-many-ancestors
    # pylint: disable=super-init-not-called
    #@+others
    #@+node:ekr.20181028052650.47: *3* __init__
    def __init__(self, conn, addr, server):
        
        self.leo_actions = LeoActions(self)
        asynchat.async_chat.__init__(self, conn)
        self.client_address = addr
        self.connection = conn
        self.server = server
        self.wfile = delayedSocketStream(self.socket)
        # Sets the terminator. When it is received, this means that the
        # http request is complete, control will be passed to self.found_terminator
        self.term = g.toEncodedString('\r\n\r\n')
        self.set_terminator(self.term)
        self.buffer = BytesIO()
        ### Set self.use_encoding and self.encoding.
        ### This is used by asyn_chat.
        self.use_encoding = True
        self.encoding = 'utf-8'
    #@+node:ekr.20181028052650.48: *3* copyfile
    def copyfile(self, source, outputfile):
        """Copy all data between two file objects.

        The SOURCE argument is a file object open for reading
        (or anything with a read() method) and the DESTINATION
        argument is a file object open for writing (or
        anything with a write() method).

        The only reason for overriding this would be to change
        the block size or perhaps to replace newlines by CRLF
        -- note however that this the default server uses this
        to copy binary data as well.
         """
        shutil.copyfileobj(source, outputfile, length=255)
    #@+node:ekr.20181028052650.49: *3* log_message
    def log_message(self, format, *args):
        """Log an arbitrary message.

         This is used by all other logging functions.  Override
         it if you have specific logging wishes.

         The first argument, FORMAT, is a format string for the
         message to be logged.  If the format string contains
         any % escapes requiring parameters, they should be
         specified as subsequent arguments (it's just like
         printf!).

         The client host and current date/time are prefixed to
         every message.

         """
        message = "%s - - [%s] %s\n" % (
            self.address_string(),
            self.log_date_time_string(),
            format % args)
        g.es(message)
    #@+node:ekr.20181028052650.50: *3* collect_incoming_data
    def collect_incoming_data(self, data):
        """Collects the data arriving on the connexion"""
        self.buffer.write(data)
    #@+node:ekr.20181028052650.51: *3* prepare_POST
    def prepare_POST(self):
        """Prepare to read the request body"""
        bytesToRead = int(self.headers.getheader('content-length'))
        # set terminator to length (will read bytesToRead bytes)
        self.set_terminator(bytesToRead)
        self.buffer = StringIO()
        # control will be passed to a new found_terminator
        self.found_terminator = self.handle_post_data
    #@+node:ekr.20181028052650.52: *3* handle_post_data
    def handle_post_data(self):
        """Called when a POST request body has been read"""
        self.rfile = StringIO(self.buffer.getvalue())
        self.do_POST()
        self.finish()
    #@+node:ekr.20181028052650.53: *3* do_GET
    def do_GET(self):
        """Begins serving a GET request"""
        # nothing more to do before handle_data()
        self.handle_data()
    #@+node:ekr.20181028052650.54: *3* do_POST
    def do_POST(self):
        """Begins serving a POST request. The request data must be readable
         on a file-like object called self.rfile"""
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        length = int(self.headers.getheader('content-length'))
        if ctype == 'multipart/form-data':
            query = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            qs = self.rfile.read(length)
            query = cgi.parse_qs(qs, keep_blank_values=1)
        else:
            query = '' # Unknown content-type
        # some browsers send 2 more bytes...
        [ready_to_read, x, y] = select.select([self.connection], [], [], 0)
        if ready_to_read:
            self.rfile.read(2)
        self.QUERY.update(self.query(query))
        self.handle_data()
    #@+node:ekr.20181028052650.55: *3* query
    def query(self, parsedQuery):
        """Returns the QUERY dictionary, similar to the result of cgi.parse_qs
         except that :
         - if the key ends with [], returns the value (a Python list)
         - if not, returns a string, empty if the list is empty, or with the
         first value in the list"""
        res = {}
        for item in parsedQuery.keys():
            value = parsedQuery[item] # a Python list
            if item.endswith("[]"):
                res[item[: -2]] = value
            else:
                res[item] = value[0] if value else ''
        return res
    #@+node:ekr.20181028052650.56: *3* handle_data
    def handle_data(self):
        """Class to override"""
        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile)
    #@+node:ekr.20181028052650.57: *3* handle_read_event (NEW)
    def handle_read_event(self):
        '''Over-ride SimpleHTTPRequestHandler.handle_read_event.'''
        asynchat.async_chat.handle_read_event(self)
    #@+node:ekr.20181028052650.58: *3* handle_request_line (aka found_terminator)
    def handle_request_line(self):
        """Called when the http request line and headers have been received"""
        # prepare attributes needed in parse_request()
        self.rfile = BytesIO(self.buffer.getvalue())
        self.raw_requestline = self.rfile.readline()
        self.parse_request()
        # if there is a Query String, decodes it in a QUERY dictionary
        self.path_without_qs, self.qs = self.path, ''
        if self.path.find('?') >= 0:
            self.qs = self.path[self.path.find('?') + 1:]
            self.path_without_qs = self.path[: self.path.find('?')]
        self.QUERY = self.query(cgi.parse_qs(self.qs, 1))
        if self.command in ['GET', 'HEAD']:
            # if method is GET or HEAD, call do_GET or do_HEAD and finish
            method = "do_" + self.command
            if hasattr(self, method):
                f = getattr(self, method)
                f()
                self.finish()
        elif self.command == "POST":
            # if method is POST, call prepare_POST, don't finish before
            self.prepare_POST()
        else:
            self.send_error(501, "Unsupported method (%s)" % self.command)
    #@+node:ekr.20181028052650.59: *3* found_terminator
    def found_terminator(self):
        # pylint: disable=method-hidden
        # Control may be passed to another found_terminator.
        self.handle_request_line()
    #@+node:ekr.20181028052650.60: *3* finish
    def finish(self):
        """Reset terminator (required after POST method), then close"""
        self.set_terminator(self.term)
        self.wfile.initiate_sending()
        # self.close()
    #@-others
#@+node:ekr.20181028052650.61: ** class Server
class Server(asyncore.dispatcher):
    """Copied from http_server in medusa"""
    #@+others
    #@+node:ekr.20181028052650.62: *3* __init__
    def __init__(self, ip, port, handler):
        self.ip = ip
        self.port = port
        self.handler = handler
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((ip, port))
        # lower this to 5 if your OS complains
        self.listen(1024)
    #@+node:ekr.20181028052650.63: *3* handle_accept
    def handle_accept(self):
        try:
            # pylint: disable=unpacking-non-sequence
            # The following except statements catch this.
            conn, addr = self.accept()
        except socket.error:
            self.log_info('warning: server accept() threw an exception', 'warning')
            return
        except TypeError:
            self.log_info('warning: server accept() threw EWOULDBLOCK', 'warning')
            return
        # creates an instance of the handler class to handle the request/response
        # on the incoming connexion
        self.handler(conn, addr, self)
    #@-others
#@+node:ekr.20181028052650.64: ** functions
#@+node:ekr.20181028052650.65: *3* a_read (asynchore override)
def a_read(obj):
    try:
        obj.handle_read_event()
    except asyncore.ExitNow:
        raise
    except Exception:
        obj.handle_error()
#@+node:ekr.20181028052650.66: *3* escape
def escape(s):
    s = s.replace('&', "&amp;")
    s = s.replace('<', "&lt;")
    s = s.replace('>', "&gt;")
    # is there a more elegant way to do this?
    # Replaces blanks with &nbsp; id they are in
    # the beginning of the line.
    lines = s.split('\n')
    result = []
    blank = chr(32)
    for line in lines:
        if line.startswith(blank):
            resultchars = []
            startline = True
            for char in line:
                if char == blank:
                    if startline:
                        resultchars.append('&nbsp;')
                    else:
                        resultchars.append(' ')
                else:
                    startline = False
                    resultchars.append(char)
            result.append(''.join(resultchars))
        else:
            result.append(line)
    s = '\n'.join(result)
    s = s.replace('\n', '<br />')
    s = s.replace(chr(9), '&nbsp;&nbsp;&nbsp;&nbsp;')
    # 8/9/2007
    # s = g.toEncodedString(s,encoding=browser_encoding,reportErrors=False)
    # StringIO.write(self, s)
    return s
#@+node:ekr.20181028052650.67: *3* loop (asynchore override)
def loop(timeout=5.0, use_poll=0, map=None):
    """
    Override the loop function of asynchore.
    We poll only until there is not read or
    write request pending.
    """
    return poll(timeout)
#@+node:ekr.20181028052650.68: *3* node_reference
def node_reference(vnode):
    """
    Use by the rst3 plugin.
    """
    return leo_interface().node_reference(vnode)
#@+node:ekr.20181028052650.69: *3* poll
def poll(timeout=0.0):
    global sockets_to_close
    map = asyncore.socket_map
    if not map:
        return False
    while 1:
        r = []; w = []; e = []
        for fd, obj in map.items():
            if obj.readable():
                r.append(fd)
            if obj.writable():
                w.append(fd)
        if not sockets_to_close: # Set by writeable()
            break
        for s in sockets_to_close:
            s.close()
        sockets_to_close = []
    if [] == r == w == e:
        time.sleep(timeout)
    else:
        #@+<< try r, w, e = select.select >>
        #@+node:ekr.20181028052650.70: *4* << try r, w, e = select.select >>
        try:
            r, w, e = select.select(r, w, e, timeout)
        except select.error: # as err:
            # if err[0] != EINTR:
                # raise
            # else:
                # return False
            return False # EKR: EINTR is undefined.
        #@-<< try r, w, e = select.select >>
    for fd in r:
        #@+<< asyncore.read(map.get(fd)) >>
        #@+node:ekr.20181028052650.71: *4* << asyncore.read(map.get(fd)) >>
        obj = map.get(fd)
        if obj is not None:
            asyncore.read(obj)
        #@-<< asyncore.read(map.get(fd)) >>
    for fd in w:
        #@+<< asyncore.write(map.get(fd)) >>
        #@+node:ekr.20181028052650.72: *4* << asyncore.write(map.get(fd)) >>
        obj = map.get(fd)
        if obj is not None:
            asyncore.write(obj)
        #@-<< asyncore.write(map.get(fd)) >>
    return len(r) > 0 or len(w) > 0
#@+node:ekr.20181028052650.10: *3* getData
def getData(setting):
    '''Return the given @data node.'''
    aList = g.app.config.getData(
        setting,
        strip_comments=False,
        strip_data=False,
    )
    s = ''.join(aList or [])
    return s
#@+node:ekr.20181028052650.5: ** init & helpers (leowapp.py)
def init():
    '''Return True if the plugin has loaded successfully.'''
    getGlobalConfiguration() ###
    try:
        Server(config.leowapp_ip, config.leowapp_port, RequestHandler)
    except socket.error as e:
        g.es("mod_http server initialization failed (%s:%s): %s" % (
            config.leowapp_ip, config.leowapp_port, e))
        return False
    asyncore.read = a_read
    g.registerHandler("idle", plugin_wrapper)
    g.es("leowapp serving at %s:%s" % (
        config.leowapp_ip,
        config.leowapp_port), color="purple")
    g.plugin_signon(__name__)
    return True
#@+node:ekr.20181028052650.6: *3* getGlobalConfiguration
def getGlobalConfiguration():
    """read config."""
    # timeout.
    newtimeout = g.app.config.getInt("leowapp-timeout")
    if newtimeout is not None:
        config.leowapp_timeout = newtimeout / 1000.0
    # ip.
    newip = g.app.config.getString("leowapp-ip")
    if newip:
        config.leowapp_ip = newip
    # port.
    newport = g.app.config.getInt("leowapp-port")
    if newport:
        config.leowapp_port = newport
#@+node:ekr.20181028052650.7: *3* plugin_wrapper
def plugin_wrapper(tag, keywords):
    if g.app.killed:
        return
    # first = True
    while loop(config.leowapp_timeout):
        pass
#@+node:ekr.20181028052650.8: *3* onFileOpen (not used)
def onFileOpen(tag, keywords):
    c = keywords.get("new_c")
    g.trace('c',repr(c))
    ### wasactive = config.leowapp_active
    getConfiguration(c)
    Server('', config.leowapp_port, RequestHandler)
    asyncore.read = a_read
    g.registerHandler("idle", plugin_wrapper)
    g.es("http serving enabled on port %s, " % (
        config.leowapp_port),
        color="purple")
#@+node:ekr.20181028052650.9: *3* getConfiguration (not used)
def getConfiguration(c):
    """Called when the user opens a new file."""
    # timeout.
    newtimeout = c.config.getInt("leowapp-timeout")
    if newtimeout is not None:
        config.leowapp_timeout = newtimeout / 1000.0
    # port.
    newport = c.config.getInt("leowapp-port")
    if newport:
        config.leowapp_port = newport
#@-others
#@@language python
#@@tabwidth -4
#@-leo
