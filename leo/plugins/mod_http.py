#@+leo-ver=5-thin
#@+node:EKR.20040517080250.1: * @file mod_http.py
#@+<< docstring >>
#@+node:ekr.20050111111238: ** << docstring >>
''' A minimal http plugin for LEO, based on AsyncHttpServer.py.

Use this plugin is as follows:

1. Start Leo with the plugin enabled. You will see a purple message that says
   something like::

    "http serving enabled on port 8080, version 0.91"

2. Start a web browser, and enter the following url: http://localhost:8080/

You will see a a "top" level page containing one link for every open .leo file.
Start clicking :-)

You can use the browser's refresh button to update the top-level view in the
browser after you have opened or closed files.

To enable this plugin put this into your file::

    @settings
        @bool http_active = True
        @int  http_port = 8080
        @string rst_http_attributename = 'rst_http_attribute'

**Note**: the browser_encoding constant (defined in the top node of this file)
must match the character encoding used in the browser. If it does not, non-ascii
characters will look strange.

Can also be used for bookmarking directly from the browser to Leo. To do this,
add a bookmark to the browser with the following URL / Location::
    
    javascript:w=window;if(w.content){w=w.content}; d=w.document; w.open('http://localhost:8130/_/add/bkmk/?&name=' + escape(d.title) + '&selection=' + escape(window.getSelection()) + '&url=' + escape(w.location.href),%22_blank%22,%22toolbar=no, location=no, directories=no, status=no, menubar=no, scrollbars=no, resizable=yes, copyhistory=no, width=800, height=300, status=no%22);void(0)
    
and edit the port (8130 in the example above) to match the port you're using for
mod_http.

Bookmarks are created as the first node in the outline which has been opened
longest. You can set the ``@string`` ``http_bookmark_unl`` to specify an
alternative location, e.g.::
    
    @string http_bookmark_unl = /home/tbrown/.bookmarks.leo#@bookmarks-->Incoming

to place them in the `Incoming` node in the `@bookmarks` node in the
`.bookmarks.leo` outline.
    
The headline is preceeded with '@url ' *unless* the ``bookmarks`` plugin is
loaded. If the ``bookmarks`` plugin is loaded the bookmark will have to be moved
to a ``@bookmarks`` tree to be useful.

The browser may or may not be able to close the bookmark form window for you,
depending on settings - set ``dom.allow_scripts_to_close_windows`` to true in
``about:config`` in Firefox.

'''
#@-<< docstring >>

#@@language python
#@@tabwidth -4

# Adapted and extended from the Python Cookbook:
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/259148

__version__ = "0.99"

# This encoding must match the character encoding used in your browser.
# If it does not, non-ascii characters will look very strange.
browser_encoding = 'utf-8' # A hack.  Can we query the browser for this?

#@+<< imports >>
#@+node:EKR.20040517080250.3: ** << imports >>
import leo.core.leoGlobals as g

import asynchat
import asyncore
import cgi

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
#@+<< version history >>
#@+node:ekr.20050328104558: ** << version history >>
#@@killcolor
#@+at
# 
# 0.93 EKR:
#     - Added 'version history' section.
#     - Removed vestigial sections.
#     - Changed docstring to mention @string rst_http_attributename = 'rst_http_attribute'
# 0.93 EKR: Added init function.
# But http was in the Plugins menu because the rst3 plugin imports it.
# The fix was to the plugins manager, not this plugin or rst3.
# 0.94 BWM
# 0.95 EKR: Changed headline from applyConfiguration to getConfiguration to match name of method.
# 0.96 EKR: suppress all pychecker warnings.
# 0.97 EKR:
# - Call g.signon in init so users can see that the plugin is enabled.
# - Removed the old @page line from the docstring.
# 0.98 EKR: Handle unicode characters properly.
# 0.99 Lauri Ojansivu <lauri.ojansivu@gmail.com>: Many change for better html generation.
#@-<< version history >>

sockets_to_close = []

#@+<< config >>
#@+node:bwmulder.20050326191345: ** << config >>
class config:
    http_active = False
    http_timeout = 0
    http_port = 8080
    rst2_http_attributename = 'rst_http_attribute'
#@-<< config >>
#@+others
#@+node:ekr.20110522152535.18250: ** top-level
#@+node:ekr.20060830091349: *3* init
def init ():

    if 0:
        g.registerHandler("open2", onFileOpen)
    else:
        getGlobalConfiguration()
        if config.http_active:
            
            try:
                s=Server('',config.http_port,RequestHandler)
            except socket.error:
                g.es("mod_http port already in use")
                return False
                    
            asyncore.read = a_read
            g.registerHandler("idle", plugin_wrapper)
    
            g.es("http serving enabled on port %s, version %s" % (
                config.http_port, __version__), color="purple")
        
    g.plugin_signon(__name__)

    return True
#@+node:bwmulder.20050326191345.1: *3* onFileOpen
def onFileOpen(tag, keywords):
    c = keywords.get("new_c")
    
    # g.trace('c',repr(c))

    wasactive = config.http_active
    getConfiguration(c)

    if config.http_active and not wasactive: # Ok for unit testing:

        s=Server('',config.http_port,RequestHandler)
        asyncore.read = a_read
        g.registerHandler("idle", plugin_wrapper)

        g.es("http serving enabled on port %s, version %s" % (
            config.http_port, __version__), color="purple")
#@+node:ekr.20110522152535.18252: *3* escape
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
#@+node:bwmulder.20050322132919: ** rst_related
#@+node:bwmulder.20050322134325: *3* reconstruct_html_from_attrs
def reconstruct_html_from_attrs(attrs, how_much_to_ignore=0):
    """
    Given an attribute, reconstruct the html for this node.
    """
    result = []
    stack = attrs
    while stack:
        result.append(stack[0])
        stack = stack[2]
    result.reverse()
    result = result[how_much_to_ignore:]
    result.extend(attrs[3:])
    stack = attrs
    for i in range(how_much_to_ignore):
        stack = stack[2]
    while stack:
        result.append(stack[1])
        stack = stack[2]
    return result
#@+node:bwmulder.20050322132919.2: *3* get_http_attribute
def get_http_attribute(p):
    vnode = p.v
    if hasattr(vnode, 'unknownAttributes'):
        return vnode.unknownAttributes.get(config.rst2_http_attributename, None)
    return None

#@+node:bwmulder.20050322133050: *3* set_http_attribute
def set_http_attribute(p, value):
    vnode = p.v
    if hasattr(vnode, 'unknownAttributes'):
        vnode.unknownAttributes[config.rst2_http_attributename] = value
    else:
        vnode.unknownAttributes = {config.rst2_http_attributename: value}

#@+node:bwmulder.20050322135114: *3* node_reference
def node_reference(vnode):
    """
    Use by the rst2 plugin.
    """
    return leo_interface().node_reference(vnode)
#@+node:EKR.20040517080250.4: ** class delayedSocketStream
class delayedSocketStream(asyncore.dispatcher_with_send):
    #@+others
    #@+node:EKR.20040517080250.5: *3* __init__
    def __init__(self,sock):
        self._map = asyncore.socket_map
        self.socket=sock
        self.socket.setblocking(0)
        self.closed=1   # compatibility with SocketServer
        self.buffer = []
    #@+node:EKR.20040517080250.6: *3* write
    def write(self,data):
        
        self.buffer.append(data)
    #@+node:EKR.20040517080250.7: *3* initiate_sending
    def initiate_sending(self):
        
        ### Create a bytes string.
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
    #@+node:EKR.20040517080250.8: *3* handle_read
    def handle_read(self):
        pass
    #@+node:EKR.20040517080250.9: *3* writable
    def writable(self):

        result = (not self.connected) or len(self.out_buffer)
        if not result:
            sockets_to_close.append(self)
        return result
    #@-others
#@+node:EKR.20040517080250.10: ** class nodeNotFound
class nodeNotFound(Exception):
    pass
#@+node:bwmulder.20061014153544: ** class noLeoNodePath
class noLeoNodePath(Exception):
    """
    Raised if the path can not be converted a filename and a series of numbers.
    Most likely a reference to a picture.
    """
    pass
#@+node:EKR.20040517080250.20: ** class leo_interface
class leo_interface(object):
    #@+others
    #@+node:EKR.20040517080250.21: *3* add_leo_links
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
                self.create_leo_reference(window, threadNext,  "next", f)
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
            child = window.c.rootVnode()
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
    #@+node:EKR.20040517080250.22: *3* create_href
    def create_href(self, href, text, f):

        f.write('<a href="%s">' % href)
        f.write(escape(text))
        f.write("</a>\n")

    #@+node:bwmulder.20050319134815: *3* create_leo_h_reference
    def create_leo_h_reference(self, window, node):
        parts = [window.shortFileName()] + self.get_leo_nameparts(node)
        href = '/' + '/'.join(parts)
        return href
    #@+node:EKR.20040517080250.23: *3* create_leo_reference
    def create_leo_reference(self, window, node, text, f):
        """
        Create a reference to 'node' in 'window', displaying 'text'
        """
        href = self.create_leo_h_reference(window, node)
        self.create_href(href, text, f)
    #@+node:EKR.20040517080250.24: *3* format_leo_node
    def format_leo_node(self, window, node):
        """
        Given a node 'node', return the contents of that node as html text.

        Include some navigational references too
        """

        if node:
            headString = node.h
            bodyString = node.b
            format_info = get_http_attribute(node)
        else:
            headString, bodyString = "Top level", ""
            format_info = None
        f = StringIO()
        f.write("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" 
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"> 
    <html> 
    <head> 
    <meta http-equiv="content-type" content="text/html; charset=UTF-8" /> 
    <title>""")
        f.write(escape(window.shortFileName() + ":" + headString))
        f.write("</title>\n</head>\n<body>\n")
        # write navigation
        self.add_leo_links(window, node, f)
        # write path
        self.write_path(node, f)
        f.write("<hr />\n") # horizontal rule
        # f.write('<span style="font-family: monospace;">')
        if format_info:
            f.write("<p>\n")
            html_lines = reconstruct_html_from_attrs(format_info, 3)
            for line in html_lines:
                f.write(line)
            f.write("\n</p>\n")
        else:
            if (bodyString):
                f.write("<p>\n")
            f.write(escape(bodyString))
            if (bodyString):
                f.write("\n</p>\n")
        # f.write("</span>\n")
        f.write("\n</body>\n</html>\n")
        return f
    #@+node:EKR.20040517080250.25: *3* get_leo_nameparts
    def get_leo_nameparts(self, node):
        """
        Given a 'node', construct a list of sibling numbers to get to that node.
        """
        result = []
        if node:
            cnode = node
            parent = cnode.parent()
            while parent:
                i = 0
                child = parent.firstChild()
                while child != cnode:
                    child = child.next()
                    i += 1
                result.append(str(i))
                cnode = parent
                parent = cnode.parent()
            i = 0
            previous = cnode.back()
            while previous:
                i += 1
                previous = previous.back()
            result.append(str(i))
            result.reverse()
        return result
    #@+node:EKR.20040517080250.26: *3* get_leo_node
    def get_leo_node(self, path):
        """
        given a path of the form:
            [<short filename>,<number1>,<number2>...<numbern>]
            identify the leo node which is in that file, and,
            from top to bottom, is the <number1> child of the topmost
            node, the <number2> child of that node, and so on.

            Return None if that node can not be identified that way.
        """
        # Identify the window
        for w in g.app.windowList:
            if w.shortFileName() == path[0]:
                break
        else:
            return None, None

        node = w.c.rootVnode()

        if len(path) >= 2:
            for i in range(int(path[1])):
                node = node.next()
                if node is None:
                    raise nodeNotFound
            # go to the i'th child for each path element.
            for i in path[2:]:
                try:
                    int(i)
                except ValueError:
                    # No Leo path
                    raise noLeoNodePath
                node = node.nthChild(int(i))
                if node is None:
                    raise nodeNotFound
        else:
            node = None
        return w, node
    #@+node:EKR.20040517080250.27: *3* get_leo_windowlist
    def get_leo_windowlist(self):

        f = StringIO()
        f.write("<title>ROOT for LEO HTTP plugin</title>\n")
        f.write("<h2>Windowlist</h2>\n")
        f.write("<hr />\n") # horizontal rule
        f.write("<ul>\n")
        a = g.app # get the singleton application instance.
        windows = a.windowList # get the list of all open frames.
        for w in windows:
            f.write("<li>")
            shortfilename = w.shortFileName()
            f.write('<a href="%s">' % shortfilename)
            f.write("file name: %s" % shortfilename)
            f.write("</a>\n")
            f.write("</li>")
        f.write("</ul>\n")
        f.write("<hr />\n")
        return f
    #@+node:bwmulder.20050319135316: *3* node_reference
    def node_reference(self, vnode):
        """
        Given a position p, return the name of the node.
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
    #@+node:bwmulder.20050322224921: *3* send_head
    def send_head(self):
        """Common code for GET and HEAD commands.

         This sends the response code and MIME headers.

         Return value is either a file object (which has to be copied
         to the outputfile by the caller unless the command was HEAD,
         and must be closed by the caller under all circumstances), or
         None, in which case the caller has nothing further to do.

         """
        try:
            path = self.split_leo_path(self.path)
            
            if path[0] == '_':
                f = self.leo_actions.get_response()
            elif len(path) == 1 and path[0] == 'favicon.ico':
                f = self.leo_actions.get_favicon()
            elif path == '/':
                f = self.get_leo_windowlist()
            else:
                try:
                    window, node = self.get_leo_node(path)
                    if window is None:
                        self.send_error(404, "File not found")
                        return None
                    f = self.format_leo_node(window, node)
                except nodeNotFound:
                    self.send_error(404, "Node not found")
                    return None
                except noLeoNodePath:
                    g.es("No Leo node path:", path)
                    # Is there something better we can do here?
                    self.send_error(404, "Node not found")
                    return None
            length = f.tell()
            f.seek(0)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-Length", str(length))
            self.end_headers()
            return f
        except:
            import traceback
            traceback.print_exc()
            raise

    #@+node:EKR.20040517080250.30: *3* split_leo_path
    def split_leo_path(self, path):
        """
        A leo node is represented by a string of the form:
            <number1>_<number2>...<numbern>,
        where <number> is the number of sibling of the node.
        """
        if path == '/':
            return '/'
        if path.startswith("/"):
            path = path[1:]
        return path.split('/')
    #@+node:EKR.20040517080250.28: *3* write_path
    def write_path(self, node, f):

        result = []
        while node:
            result.append(node.h)
            node = node.parent()
        result.reverse()
        if result:
            result2 = result[:-1]
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
#@+node:EKR.20040517080250.13: ** class RequestHandler
class RequestHandler(
    leo_interface,
    asynchat.async_chat,
    SimpleHTTPRequestHandler
):
    #@+others
    #@+node:EKR.20040517080250.14: *3* __init__
    def __init__(self,conn,addr,server):
        
        self.leo_actions = LeoActions(self)
        
        asynchat.async_chat.__init__(self,conn)

        self.client_address=addr
        self.connection=conn
        self.server=server
        
        self.wfile = delayedSocketStream(self.socket)
        
        # Sets the terminator. When it is received, this means that the
        # http request is complete, control will be passed to self.found_terminator
        self.term = g.toEncodedString('\r\n\r\n')
        self.set_terminator(self.term)

        self.buffer = BytesIO() ###
        
        ### Set self.use_encoding and self.encoding.
        ### This is used by asyn_chat.
        self.use_encoding = True
        self.encoding = 'utf-8'
    #@+node:EKR.20040517080250.15: *3* copyfile
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
    #@+node:EKR.20040517080250.16: *3* log_message
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
            format%args)
        g.es(message)
    #@+node:EKR.20040517080250.17: *3* collect_incoming_data
    def collect_incoming_data(self,data):

        """Collects the data arriving on the connexion"""
        
        self.buffer.write(data)
    #@+node:EKR.20040517080250.18: *3* prepare_POST
    def prepare_POST(self):
        
        """Prepare to read the request body"""

        bytesToRead = int(self.headers.getheader('content-length'))
        
        # set terminator to length (will read bytesToRead bytes)
        self.set_terminator(bytesToRead)
        self.buffer=StringIO()

        # control will be passed to a new found_terminator
        self.found_terminator=self.handle_post_data
    #@+node:EKR.20040517080250.19: *3* handle_post_data
    def handle_post_data(self):
        """Called when a POST request body has been read"""

        self.rfile=StringIO(self.buffer.getvalue())
        self.do_POST()
        self.finish()
    #@+node:EKR.20040517080250.31: *3* do_GET
    def do_GET(self):
        """Begins serving a GET request"""

        # nothing more to do before handle_data()
        self.handle_data()
    #@+node:EKR.20040517080250.32: *3* do_POST
    def do_POST(self):
        
        """Begins serving a POST request. The request data must be readable
         on a file-like object called self.rfile"""

        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        length = int(self.headers.getheader('content-length'))
        if ctype == 'multipart/form-data':
            query=cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            qs=self.rfile.read(length)
            query=cgi.parse_qs(qs, keep_blank_values=1)
        else:
            query = ''                   # Unknown content-type
        # some browsers send 2 more bytes...
        [ready_to_read,x,y]=select.select([self.connection],[],[],0)
        if ready_to_read:
            self.rfile.read(2)

        self.QUERY.update(self.query(query))
        self.handle_data()
    #@+node:EKR.20040517080250.33: *3* query
    def query(self,parsedQuery):
        
        """Returns the QUERY dictionary, similar to the result of cgi.parse_qs
         except that :
         - if the key ends with [], returns the value (a Python list)
         - if not, returns a string, empty if the list is empty, or with the
         first value in the list"""

        res={}
        for item in parsedQuery.keys():
            value=parsedQuery[item] # a Python list
            if item.endswith("[]"):
                res[item[:-2]]=value
            else:
                if len(value)==0:
                    res[item]=''
                else:
                    res[item]=value[0]
        return res
    #@+node:EKR.20040517080250.34: *3* handle_data
    def handle_data(self):
        """Class to override"""

        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile)
    #@+node:ekr.20110522152535.18254: *3* handle_read_event (NEW)
    def handle_read_event (self):
        
        '''Over-ride SimpleHTTPRequestHandler.handle_read_event.'''

        asynchat.async_chat.handle_read_event(self)
    #@+node:EKR.20040517080250.35: *3* handle_request_line (aka found_terminator)
    def handle_request_line(self):
        """Called when the http request line and headers have been received"""

        # prepare attributes needed in parse_request()
        self.rfile=BytesIO(self.buffer.getvalue())
        self.raw_requestline=self.rfile.readline()
        self.parse_request()

        # if there is a Query String, decodes it in a QUERY dictionary
        self.path_without_qs,self.qs=self.path,''
        if self.path.find('?')>=0:
            self.qs=self.path[self.path.find('?')+1:]
            self.path_without_qs=self.path[:self.path.find('?')]
        self.QUERY=self.query(cgi.parse_qs(self.qs,1))

        if self.command in ['GET','HEAD']:
            # if method is GET or HEAD, call do_GET or do_HEAD and finish
            method="do_"+self.command
            if hasattr(self,method):
                f = getattr(self,method)
                f()
                self.finish()
        elif self.command=="POST":
            # if method is POST, call prepare_POST, don't finish before
            self.prepare_POST()
        else:
            self.send_error(501, "Unsupported method (%s)" %self.command)
    #@+node:ekr.20110522152535.18256: *3* found_terminator
    def found_terminator (self):
        
        self.handle_request_line()
    #@+node:EKR.20040517080250.36: *3* finish
    def finish(self):

        """Reset terminator (required after POST method), then close"""

        self.set_terminator (self.term)
        self.wfile.initiate_sending()
        # self.close()
    #@-others
#@+node:EKR.20040517080250.37: ** class Server
class Server(asyncore.dispatcher):
    """Copied from http_server in medusa"""
    #@+others
    #@+node:EKR.20040517080250.38: *3* __init__
    def __init__ (self, ip, port, handler):

        self.ip = ip
        self.port = port
        self.handler=handler

        asyncore.dispatcher.__init__ (self)
        self.create_socket (socket.AF_INET, socket.SOCK_STREAM)

        self.set_reuse_addr()
        self.bind ((ip, port))

        # lower this to 5 if your OS complains
        self.listen (1024)
    #@+node:EKR.20040517080250.39: *3* handle_accept
    def handle_accept (self):
        
        try:
            conn, addr = self.accept()
        except socket.error:
            self.log_info ('warning: server accept() threw an exception', 'warning')
            return
        except TypeError:
            self.log_info ('warning: server accept() threw EWOULDBLOCK', 'warning')
            return

        # creates an instance of the handler class to handle the request/response
        # on the incoming connexion
        self.handler(conn,addr,self)
    #@-others
#@+node:tbrown.20110930093028.34530: ** class LeoActions
class LeoActions:
    """A place to collect other URL based actions like saving
    bookmarks from the browser.  Conceptually this stuff could
    go in class leo_interface but putting it here for separation
    for now."""
    
    #@+others
    #@+node:tbrown.20110930220448.18077: *3* __init__
    def __init__(self, request_handler):
        
        self.request_handler = request_handler
        self.bookmark_unl = g.app.commanders()[0].config.getString('http_bookmark_unl')
    #@+node:tbrown.20110930220448.18075: *3* add_bookmark
    def add_bookmark(self):
        """Return the file like 'f' that leo_interface.send_head makes

        """
        
        parsed_url = urlparse.urlparse(self.request_handler.path)
        query = urlparse.parse_qs(parsed_url.query)
        
        # print(parsed_url.query)
        # print(query)
        
        name = query.get('name', ['NO TITLE'])[0]
        url = query['url'][0]
        
        c = None  # outline for bookmarks
        previous = None  # previous bookmark for adding selections
        parent = None  # parent node for new bookmarks
        using_root = False
        
        path = self.bookmark_unl
        
        # g.trace(path)

        if path:
            # EKR
            i = path.find('#')
            if i > -1:
                path = path[:i].strip()
                unl = path[i+1:].strip()
            else:
                path = path
                unl = ''
            
            parsed = urlparse.urlparse(path) # self.bookmark_unl) # EKR
            leo_path = os.path.expanduser(parsed.path)
            
            c = g.openWithFileName(leo_path,old_c=None)

            if c:
                g.es_print("Opened '%s' for bookmarks"% path) # self.bookmark_unl)

                parsed = urlparse.urlparse(unl) # self.bookmark_unl) # EKR
                if parsed.fragment:
                    g.recursiveUNLSearch(parsed.fragment.split("-->"),c)
                parent = c.currentPosition()
                if parent.hasChildren():
                    previous = parent.getFirstChild()
            else:
                g.es_print("Failed to open '%s' for bookmarks"%self.bookmark_unl)

        if c is None:
            using_root = True
            c = g.app.commanders()[0]
            parent = c.rootPosition()
            previous = c.rootPosition()
        
        f = StringIO()
        
        if previous and url == previous.b.split('\n',1)[0]:
            # another marking of the same page, just add selection
            self.add_bookmark_selection(
                previous, query.get('selection', [''])[0])

            c.selectPosition(previous)  # required for body text redraw
            c.redraw()

            f.write("""
    <body onload="setTimeout('window.close();', 350);" style='font-family:mono'>
    <p>Selection added</p></body>""")

            return f
        
        if '_form' in query:
            # got extra details, save to new node
            
            f.write("""
    <body onload="setTimeout('window.close();', 350);" style='font-family:mono'>
    <p>Bookmark saved</p></body>""")
            
            if using_root:
                nd = parent.insertAfter()
                nd.moveToRoot(c.rootPosition())
            else:
                nd = parent.insertAsNthChild(0)
            if g.pluginIsLoaded('leo.plugins.bookmarks'):
                nd.h = name
            else:
                nd.h = '@url '+name
            
            selection = query.get('selection', [''])[0]
            if selection:
                selection = '\n\n"""\n'+selection+'\n"""'
            
            nd.b = "%s\n\nTags: %s\n\n%s\n\nCollected: %s%s\n\n%s" % (
                url, 
                query.get('tags', [''])[0],
                query.get('_name', [''])[0],
                time.strftime("%c"),
                selection,
                query.get('description', [''])[0],
            )
            c.setChanged(True)
            c.selectPosition(nd)  # required for body text redraw
            c.redraw()

            return f
            
        # send form to collect extra details
        
        f.write("""
    <html><head><style>
    body {font-family:mono; font-size: 80%%;}
    th {text-align:right}
    </style><title>Leo Add Bookmark</title>
    </head><body onload='document.getElementById("tags").focus();'>
    <form method='GET' action='/_/add/bkmk/'>
    <input type='hidden' name='_form' value='1'/>
    <input type='hidden' name='_name' value=%s/>
    <input type='hidden' name='selection' value=%s/>
    <table>
    <tr><th>Tags:</th><td><input id='tags' name='tags' size='60'/>(comma sep.)</td></tr>
    <tr><th>Title:</th><td><input name='name' value=%s size='60'/></td></tr>
    <tr><th>URL:</th><td><input name='url' value=%s size='60'/></td></tr>
    <tr><th>Notes:</th><td><textarea name='description' cols='60' rows='6'></textarea></td></tr>
    </table>
    <input type='submit' value='Save'/><br/>
    </form>
    </body></html>""" % (quoteattr(name), 
                  quoteattr(query.get('selection', [''])[0]), 
                  quoteattr(name), 
                  quoteattr(url)))

        return f
    #@+node:tbrown.20111002082827.18325: *3* add_bookmark_selection
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
        
        # g.trace(node.h)
        
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
            x = tri_quotes[len(tri_quotes)-len(tri_quotes)%2-1]+1
            b[x:x] = insert

        else:
            # found Collected but no tri quotes
            b[collected+1:collected+1] = insert

        node.b = '\n'.join(b)
        node.setDirty()
    #@+node:tbrown.20111005093154.17683: *3* get_favicon
    def get_favicon(self):
        
        path = g.os_path_join(g.computeLeoDir(),'Icons','LeoApp16.ico')
            
        # g.trace(g.os_path_exists(path),path)
        
        try:
            f = StringIO()
            # f.write(open(path).read())
            f2 = open(path)
            s = f.read()
            f.write(s)
            return f
        except Exception:
            return None

    #@+node:tbrown.20110930220448.18076: *3* get_response
    def get_response(self):
        """Return the file like 'f' that leo_interface.send_head makes"""

        if self.request_handler.path.startswith('/_/add/bkmk/'):
            return self.add_bookmark()
            
        f = StringIO()
        f.write("Unknown URL in LeoActions.get_response()")
        return f
    #@-others
    
#@+node:EKR.20040517080250.40: ** poll
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
        #@+node:EKR.20040517080250.41: *3* << try r, w, e = select.select >>
        try:
            r, w, e = select.select(r, w, e, timeout)
        except select.error as err:
            # if err[0] != EINTR:
                # raise
            # else:
                # return False
            return False # EKR: EINTR is undefined.
        #@-<< try r, w, e = select.select >>
    for fd in r:
        #@+<< asyncore.read(map.get(fd)) >>
        #@+node:EKR.20040517080250.42: *3* << asyncore.read(map.get(fd)) >>
        obj = map.get(fd)
        if obj is not None:
            asyncore.read(obj)
        #@-<< asyncore.read(map.get(fd)) >>
    for fd in w:
        #@+<< asyncore.write(map.get(fd)) >>
        #@+node:EKR.20040517080250.43: *3* << asyncore.write(map.get(fd)) >>
        obj = map.get(fd)
        if obj is not None:
            asyncore.write(obj)
        #@-<< asyncore.write(map.get(fd)) >>
    return len(r) > 0 or len(w) > 0
#@+node:EKR.20040517080250.44: ** loop
def loop(timeout=5.0, use_poll=0, map=None):
    """
    Override the loop function of asynchore.
    We poll only until there is not read or
    write request pending.
    """
    return poll(timeout)
#@+node:EKR.20040517080250.45: ** plugin_wrapper
def plugin_wrapper(tag, keywords):

    if g.app.killed: return

    first = True
    while loop(config.http_timeout):
        pass
#@+node:EKR.20040517080250.46: ** asynchore_overrides
#@+node:EKR.20040517080250.47: *3* a_read
def a_read(obj):

    try:
        obj.handle_read_event()
    except asyncore.ExitNow:
        raise
    except:
        # g.trace('error')
        obj.handle_error()
#@+node:EKR.20040517080250.48: ** getConfiguration
def getConfiguration(c):

    """Called when the user opens a new file."""

    # timeout.
    newtimeout = c.config.getInt("http_timeout")
    if newtimeout is not None:
        config.http_timeout = newtimeout  / 1000.0
    
    # port.
    newport = c.config.getInt("http_port") 
    if newport:
        config.http_port = newport

    # active.
    newactive = c.config.getBool("http_active")
    if newactive is not None:
        config.http_active = newactive

    # attribute name.
    new_rst2_http_attributename = c.config.getString("rst2_http_attributename")
    if new_rst2_http_attributename:
        config.rst2_http_attributename = new_rst2_http_attributename
#@+node:tbrown.20111005140148.18223: ** getGlobalConfiguration
def getGlobalConfiguration():

    """read config."""

    # timeout.
    newtimeout = g.app.config.getInt("http_timeout")
    if newtimeout is not None:
        config.http_timeout = newtimeout  / 1000.0
    
    # port.
    newport = g.app.config.getInt("http_port") 
    if newport:
        config.http_port = newport

    # active.
    newactive = g.app.config.getBool("http_active")
    if newactive is not None:
        config.http_active = newactive

    # attribute name.
    new_rst2_http_attributename = g.app.config.getString("rst2_http_attributename")
    if new_rst2_http_attributename:
        config.rst2_http_attributename = new_rst2_http_attributename
#@-others
#@-leo
