# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20181028052650.1: * @file leowapp.py
#@@first
#@+<< docstring >>
#@+node:ekr.20181028052650.2: ** << docstring >>
#@@language rest
#@@wrap
'''Leo as a web app: contains python and javascript sides.

**Now**: enable the leowapp.py plugin.
**Later**: StartLeo with the --gui=browser command-line option.

Open localhost:8100 in your browser. Refresh the web page after opening or closing files.

Settings
--------

``@string leowapp_ip = 127.0.0.1``
    
    IP address 127.0.0.1 gives anyone logged into your machine access to
    all your Leo outlines.
    
    IP address 0.0.0.0 gives all network accessible machines access to
    your Leo outlines.
    
``@int  leowapp_port = 8100``
    The port.
    
``@data leowapp_stylesheet``
    The default .css for this page.
    
``@data leowapp_user_stylesheet``
    Additional .css for this page.
    
HTML
----

The web page contains::

    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js">
    <script src="<a fixed script, defined in this file"></script>
    <style src="leowapp_default.css">
    <style src="leowapp_user.css">
'''
#@-<< docstring >>
#@+<< imports >>
#@+node:ekr.20181028052650.3: ** << imports >>
# pylint: disable=deprecated-method
    # parse_qs

import leo.core.leoGlobals as g
if g.isPython3:
    import asynchat
    import asyncore
    import cgi
    from http.server import SimpleHTTPRequestHandler
    from io import BytesIO, StringIO
    import select
    import shutil
    import socket
    import time
    from xml.sax.saxutils import quoteattr
    from xml.sax.saxutils import escape as esc
else:
    print('leowapp.py requires Python 3')
#@-<< imports >>
#@+<< leowapp_js >>
#@+node:ekr.20181028071923.1: ** << leowapp_js >>
#@@language javascript

leowapp_js = """\

socket= new WebSocket('127.0.0.1:8001/');
    // https://stackoverflow.com/questions/1736382/how-to-use-sockets-in-javascript-html

// require(http)
    // ReferenceError: require is not defined
    //https://stackoverflow.com/questions/19059580

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
        //
        // Toggle the expansion state.
        $(e.target).parent().children("div.node").toggle()
        //
        // Set the body text.
        $(".body-code").text($(e.target).attr("b"));
        //
        // Set the border
        $("div.headline").removeClass('borderclass');
        $("div.headline").addClass('unborderclass');
        $(e.target).removeClass('unborderclass');
        $(e.target).addClass('borderclass');
        //
        // POST to the python server.
        var x = new XMLHttpRequest();
        x.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                // document.getElementById("demo").innerHTML = this.responseText;
                window.alert(this.responseText);
           }
        };
        x.open("GET", "clicked.txt", true);
        // POST isn't handled properly in the Python.
        // x.open("POST", "clicked.py", true);
        x.send();
        
        //
            //window.alert($(e.target));
            //console.clear();
            //console.log($(e.target));
            // console.log($(e.target).children("div.node").length);
            // console.log($(e.target).children("div.node").children("div.headline").length);
            //console.log($(e.target).attr("b").length);
            //console.log($(e.target).children(":first"));
            //console.log($(e.target).children(":first").is(":visible"));
    });
});
"""
#@-<< leowapp_js >>
browser_encoding = 'utf-8'
  ### To do: query browser: var x = document.characterSet; 
sockets_to_close = []
#@+others
#@+node:ekr.20181028154356.1: ** class Config
class Config (object):
    
    ip = g.app.config.getString("leowapp-ip") or '127.0.0.1'
    port = g.app.config.getInt("leowapp-port") or 8100
    timeout = g.app.config.getInt("leowapp-timeout") or 0
    
    def __init__(self):
        if self.timeout > 0:
            self.timeout = self.timeout / 1000.0

# Create a singleton instance.
# The initial values probably should not be changed. 
config = Config()
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
        global sockets_to_close
        result = (not self.connected) or len(self.out_buffer)
        if not result:
            sockets_to_close.append(self)
        return result
    #@-others
#@+node:ekr.20181028052650.18: ** class LeoInterface
class LeoInterface(object):
    # pylint: disable=no-member
        # .path, .send_error, .send_response and .end_headers
        # appear to be undefined.
    #@+others
    #@+node:ekr.20181028081759.1: *3* leo_i.get_favicon (not used)
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
    #@+node:ekr.20181028052650.19: *3* leo_i.send_head & helpers
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
            if len(path) == 1 and path[0] == 'favicon.ico':
                return None
                # f = self.get_favicon()
            g.trace(path)
            if path == '/':
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
    #@+node:ekr.20181028052650.20: *4* leo_i.find_window_and_root
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
    #@+node:ekr.20181028052650.21: *4* leo_i.split_leo_path
    def split_leo_path(self, path):
        '''Split self.path.'''
        if path == '/':
            return '/'
        if path.startswith("/"):
            path = path[1:]
        return path.split('/')
    #@+node:ekr.20181028052650.22: *4* leo_i.write_leo_tree & helpers
    def write_leo_tree(self, f, window, root):
        '''Write the entire html file to f.'''
        root = root.copy()
        # Write the prolog.
        f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"')
        f.write('"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">')
        f.write('<html>')
        self.write_head(f, root.h, window)
        f.write('<body>')
        f.write('<div class="container">')
        f.write('<div class="outlinepane">')
        f.write('<h1>%s</h1>' % window.shortFileName())
        for sib in root.self_and_siblings():
            self.write_node_and_subtree(f, sib)
        f.write('</div>') # End of outlinepane
        self.write_body_pane(f)
        self.write_log_pane(f)
        self.write_minibuffer_pane(f)
        f.write('</div>')  # End of containerpane.
        f.write('</body></html>')
    #@+node:ekr.20181028052650.23: *5* leo_i.write_body_pane
    def write_body_pane(self, f):
        '''
        Write (just once) a *template* for the body pane.
        
        There is no need to write the actual text because the javascript sets
        the body-code element when the user changes nodes::
            
             $(".body-code").text($(e.target).attr("b"));
        '''
        # Don't use a triple string here: it would insert whitespace.
        table = (
            '<div class="bodypane">',
            '<pre>',
            '<code class="body-code"></code>',
            '</pre>',
            '</div>',
        )
        for z in table:
            f.write(z)
    #@+node:ekr.20181028052650.24: *5* leo_i.write_head
    def write_head(self, f, headString, window):

        f.write("""\
    <head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
    <style>%(default-stylesheet)s</style>
    <style>%(user-stylesheet)s</style>
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js"></script>
    <script>%(leowapp_js)s</script>
    <title>%(title)s</title>
    </head>
    """ % {
        'default-stylesheet': get_data('leowapp-stylesheet'),
        'user-stylesheet': get_data('leowapp-user-_stylesheet'),
        'leowapp_js': leowapp_js,
        'title': escape(window.shortFileName())
    })
    #@+node:ekr.20181028131729.1: *5* leo_i.write_log_pane
    def write_log_pane(self, f):
        '''
        Write the html for the log pane.
        '''
        # Don't use a triple string here: it would insert whitespace.
        table = (
            '<div class="logpane">',
            '<pre>',
            '<code class="log-code"></code>',
            '</pre>',
            '</div>',
        )
        for z in table:
            f.write(z)
    #@+node:ekr.20181028133546.1: *5* leo_i.write_minibuffer_pane
    def write_minibuffer_pane(self, f):
        '''
        Write the html for the log pane.
        '''
        # Don't use a triple string here: it would insert whitespace.
        table = (
            '<div class="minibufferpane">',
            '<pre>',
            '<code class="minibuffer-code"></code>',
            '</pre>',
            '</div>',
        )
        for z in table:
            f.write(z)
    #@+node:ekr.20181028052650.25: *5* leo_i.write_node_and_subtree
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
    #@+node:ekr.20181028052650.26: *4* leo_i.write_leo_windowlist
    def write_leo_windowlist(self):
        f = StringIO()
        f.write('''\
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html>
    <head>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
        <style>%(default-stylesheet)s</style>
        <style>%(user-stylesheet)s</style>
        <title>LeoWapp</title>
    </head>
    <body>
        <h1>Windowlist</h1>
        <hr />
        <ul>
    ''' % {
        'default-stylesheet': get_data('leowapp-stylesheet'),
        'user-stylesheet': get_data('leowapp-user-stylesheet'),
    })
        for w in g.app.windowList:
            f.write('<li><a href="%(sfn)s">"%(sfn)s"</a></li>' % {
                'sfn': w.shortFileName(),
            })
        f.write('</ul><hr /></body></html>')
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
    LeoInterface,
    asynchat.async_chat,
    SimpleHTTPRequestHandler
):
    # pylint: disable=too-many-ancestors
    # pylint: disable=super-init-not-called
    #@+others
    #@+node:ekr.20181028052650.47: *3* req.__init__
    def __init__(self, conn, addr, server):
        
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
        # async_chat uses the use_encoding and encoding ivars.
        self.use_encoding = True
        self.encoding = 'utf-8'
    #@+node:ekr.20181028052650.48: *3* req.copyfile
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
    #@+node:ekr.20181028052650.49: *3* req.log_message
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
    #@+node:ekr.20181028052650.50: *3* req.collect_incoming_data
    def collect_incoming_data(self, data):
        """Collects the data arriving on the connexion"""
        self.buffer.write(data)
    #@+node:ekr.20181028052650.51: *3* req.prepare_POST
    def prepare_POST(self):
        """Prepare to read the request body"""
        try:
            bytesToRead = int(self.headers.getheader('content-length'))
        except Exception:
            g.trace(self.headers)
            g.es_exception()
            return
        # set terminator to length (will read bytesToRead bytes)
        self.set_terminator(bytesToRead)
        self.buffer = StringIO()
        # control will be passed to a new found_terminator
        self.found_terminator = self.handle_post_data
    #@+node:ekr.20181028052650.52: *3* req.handle_post_data
    def handle_post_data(self):
        """Called when a POST request body has been read"""
        self.rfile = StringIO(self.buffer.getvalue())
        self.do_POST()
        self.finish()
    #@+node:ekr.20181028052650.53: *3* req.do_GET
    def do_GET(self):
        """Begins serving a GET request"""
        # nothing more to do before handle_data()
        self.handle_data()
    #@+node:ekr.20181028052650.54: *3* req.do_POST
    def do_POST(self):
        """
        Begins serving a POST request.
        
        The request data must be readable on a file-like object called
        self.rfile
        """
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
    #@+node:ekr.20181028052650.55: *3* req.query
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
    #@+node:ekr.20181028052650.56: *3* req.handle_data
    def handle_data(self):
        """Class to override"""
        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile)
    #@+node:ekr.20181028052650.57: *3* req.handle_read_event (NEW)
    def handle_read_event(self):
        '''Over-ride SimpleHTTPRequestHandler.handle_read_event.'''
        asynchat.async_chat.handle_read_event(self)
    #@+node:ekr.20181028052650.58: *3* req.handle_request_line (aka found_terminator)
    def handle_request_line(self):
        """Called when the http request line and headers have been received"""
        # prepare attributes needed in parse_request()
        self.rfile = BytesIO(self.buffer.getvalue())
        self.raw_requestline = self.rfile.readline()
        self.parse_request()
        #
        # if there is a Query String, decode it in a QUERY dictionary
        self.path_without_qs, self.qs = self.path, ''
        if self.path.find('?') >= 0:
            self.qs = self.path[self.path.find('?') + 1:]
            self.path_without_qs = self.path[: self.path.find('?')]
        self.QUERY = self.query(cgi.parse_qs(self.qs, 1))
        if self.QUERY: g.trace(self.QUERY) ###
        if self.command in ('GET', 'HEAD'):
            f = getattr(self, "do_" + self.command, None)
            f()
            self.finish()
        elif self.command == "POST":
            self.prepare_POST()
        else:
            self.send_error(501, "Unsupported method (%s)" % self.command)
    #@+node:ekr.20181028052650.59: *3* req.found_terminator
    def found_terminator(self):
        # pylint: disable=method-hidden
        # Control may be passed to another found_terminator.
        self.handle_request_line()
    #@+node:ekr.20181028052650.60: *3* req.finish
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
#@+node:ekr.20181028052650.64: ** top-level functions
#@+node:ekr.20181028052650.66: *3* escape
def escape(s):
    '''
    Do the standard xml escapes, replacing tabs by four spaces.
    
    There is no need to convert leading blanks to &nbsp; because the body
    and log panes use <pre> elements.
    '''
    return esc(s, {
         '\n': '<br />',
         '\t': '&nbsp;&nbsp;&nbsp;&nbsp;',
    })
#@+node:ekr.20181028052650.10: *3* get_data
def get_data(setting):
    '''Return the given @data node.'''
    aList = g.app.config.getData(
        setting,
        strip_comments=False,
        strip_data=False,
    )
    s = ''.join(aList or [])
    return s
#@+node:ekr.20181028052650.5: *3* init (leowapp.py)
def init():
    '''Return True if the plugin has loaded successfully.'''
    #
    # LeoWapp should require Python 3, for safety and convenience.
    if not g.isPython3:
        return False
    
    try:
        Server(config.ip, config.port, RequestHandler)
    except socket.error as e:
        g.es("leowapp server initialization failed (%s:%s): %s" % (config.ip, config.port, e))
        return False
    #
    # Monkey patch a method.
    asyncore.read = a_read
    
    def plugin_wrapper(tag, keywords):
        global config
        while not g.app.killed and loop(config.timeout):
            pass

    g.registerHandler("idle", plugin_wrapper)
    g.es("leowapp serving at %s:%s" % (config.ip, config.port), color="purple")
    g.plugin_signon(__name__)
    return True
#@+node:ekr.20181028161536.1: ** overrides
#@+node:ekr.20181028052650.65: *3* a_read (asynchore override)
def a_read(obj):
    try:
        obj.handle_read_event()
    except asyncore.ExitNow:
        raise
    except Exception:
        obj.handle_error()
#@+node:ekr.20181028052650.67: *3* loop (asynchore override) & poll
def loop(timeout=5.0, use_poll=0, map=None):
    """
    Override the loop function of asynchore.
    We poll only until there is not read or
    write request pending.
    """
    return poll(timeout)
#@+node:ekr.20181028052650.69: *4* poll
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
        #@+node:ekr.20181028052650.70: *5* << try r, w, e = select.select >>
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
        #@+node:ekr.20181028052650.71: *5* << asyncore.read(map.get(fd)) >>
        obj = map.get(fd)
        if obj is not None:
            asyncore.read(obj)
        #@-<< asyncore.read(map.get(fd)) >>
    for fd in w:
        #@+<< asyncore.write(map.get(fd)) >>
        #@+node:ekr.20181028052650.72: *5* << asyncore.write(map.get(fd)) >>
        obj = map.get(fd)
        if obj is not None:
            asyncore.write(obj)
        #@-<< asyncore.write(map.get(fd)) >>
    return len(r) > 0 or len(w) > 0
#@-others
#@@language python
#@@tabwidth -4
#@-leo
