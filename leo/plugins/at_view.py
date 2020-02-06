#@+leo-ver=5-thin
#@+node:ktenney.20041211072654.1: * @file at_view.py
#@+<< docstring >>
#@+node:ekr.20150411161126.1: ** << docstring >> (at_view.py)
r''' Adds support for \@clip, \@view and \@strip nodes.

- Selecting a headline containing \@clip appends the contents of the clipboard to
  the end of the body pane.

- The double-click-icon-box command on a node whose headline contains \@view
  *<path-to-file>* places the contents of the file in the body pane.

- The double-click-icon-box command on a node whose headline contains \@strip
  *<path-to-file>* places the contents of the file in the body pane, with all
  sentinels removed.

This plugin also accumulates the effect of all \@path nodes.
'''
#@-<< docstring >>
__version__ = "0.9"
import leo.core.leoGlobals as g
path           = g.import_module('path')
win32clipboard = g.import_module('win32clipboard')

#@+others
#@+node:ekr.20111104210837.9693: ** init
def init():
    '''Return True if the plugin has loaded successfully.'''
    ok = path and win32clipboard
        # Ok for unit testing.
    if ok:
        g.registerHandler("after-create-leo-frame",onCreate)
    elif not g.app.unitTesting:
        s = 'at_view plugin not loaded: win32Clipboard not present.'
        g.es_print(s)
    return ok
#@+node:ktenney.20041211072654.6: ** onCreate (at_view.py)
def onCreate(tag, keywords):

    c = keywords.get("c")
    if not c: return
    myView = View(c)

    # Register the handlers...
    g.registerHandler("icondclick2", myView.icondclick2)
    g.registerHandler("idle", myView.idle)
    g.plugin_signon(__name__)
#@+node:ktenney.20041211072654.7: ** class View
class View:

    '''A class to support @view, @strip and @clip nodes.'''

    #@+others
    #@+node:ktenney.20041211072654.8: *3* __init__
    def __init__ (self,c):

        self.c = c

    #@+node:ktenney.20041211072654.9: *3* icondclick2 (at_view.py)
    def icondclick2 (self, tag, keywords):

        self.current = self.c.p
        hs = self.current.h

        if hs.startswith('@view'):
            self.view()

        if hs.startswith('@strip'):
            self.strip()
    #@+node:ktenney.20041211203715: *3* idle
    def idle(self, tag, keywords):

        try:
            self.current = self.c.p
        except AttributeError:
            # c has been destroyed.
            return

        s = self.current.h
        if s.startswith("@clip"):
            self.clip()
    #@+node:ktenney.20041211072654.10: *3* view
    def view(self):
        '''
        Place the contents of a file in the body pane

        the file is either in the current headstring,
        or found by ascending the tree
        '''
        # get a path object for this position
        currentPath = self.getCurrentPath()
        if currentPath.exists():
            g.es('currentPath: %s' % currentPath.abspath())
            if currentPath.isfile():
                self.processFile(currentPath, self.current)

            if currentPath.isdir():
                self.processDirectory(currentPath, self.current)
        else:
            g.warning('path does not exist: %s' % (str(currentPath)))
    #@+node:ktenney.20041212102137: *3* clip
    def clip(self):

        '''Watch the clipboard, and copy new items to the body.'''

        if not win32clipboard:
            return

        c = self.c
        divider = '\n' + ('_-' * 34) + '\n'
        win32clipboard.OpenClipboard()
        clipboard = ""
        if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_TEXT):
            clipboard = win32clipboard.GetClipboardData()
        else:
            banner = '*' * 8
            clipboard = banner + 'Image data was copied to the clipboard' + banner

        win32clipboard.CloseClipboard()

        body = self.current.b.split(divider)
        if not body[0] == clipboard:
            g.es('clipboard now holds %s' % clipboard)
            body.insert(0, clipboard)
            c.setBodyText(self.current,divider.join(body))
    #@+node:ktenney.20041211072654.15: *3* strip
    def strip(self):

        '''Display a file with all sentinel lines removed'''

        # get a path object for this position
        c = self.c
        currentPath = self.getCurrentPath()
        if currentPath.exists():
            path = currentPath.abspath()
            s = 'currentPath: %s' % path
            g.es_print(s)
            filelines = path.lines()
            # Add an @ignore directive.
            lines = ['@ignore\n']
            verbatim = False
            for line in filelines:
                if verbatim:
                    lines.append(line)
                    verbatim = False
                elif line.strip().startswith('#@verbatim'):
                    verbatim = True
                elif not line.strip().startswith('#@'):
                    lines.append(line)
            c.setBodyText(self.current,''.join(lines))
        else:
            g.warning('path does not exist: %s' % (str(currentPath)))
    #@+node:ktenney.20041211072654.11: *3* getCurrentPath
    def getCurrentPath(self):

        """ traverse the current tree and build a path
            using all @path statements found
        """
        pathFragments = []

        # we are currently in a @view node; get the file or directory name
        pathFragments.append(self.getPathFragment(self.current))

        for p in self.current.parents():
            pathFragments.append(self.getPathFragment(p))

        if pathFragments:
            currentPath = path.path(pathFragments.pop())
            while pathFragments:
                # pop takes the last appended, which is at the top of the tree
                # build a path from the fragments
                currentPath = currentPath / path.path(pathFragments.pop())

        return currentPath.normpath()
    #@+node:ktenney.20041211072654.12: *3* getPathFragment
    def getPathFragment (self,p):

        """
        Return the path fragment if this node is a @path or @view or any @file node.
        """
        head = p.h
        for s in ('@path','@view','@strip','@file','@thin','@nosent','@asis'):
            if head.startswith(s):
                fragment = head [head.find(' '):].strip()
                return fragment
        return ''
    #@+node:ktenney.20041211072654.13: *3* processFile
    def processFile(self, path, node):

        """parameters are a path object and a node.
           the path is a file, place it's contents into the node
        """

        g.trace(node)

        self.c.setBodyText(node,''.join(path.lines()))
    #@+node:ktenney.20041211072654.14: *3* processDirectory
    def processDirectory(self, path, node):

        """
        create child nodes for each member of the directory

        @path is a path object for a directory
        @node is the node to work with
        """

        c = self.c

        # delete all nodes before creating, to avoid duplicates
        while node.firstChild():
            node.firstChild().doDelete(node)

        for file in path.files():
            child = node.insertAsLastChild()
            c.setHeadString(child,'@view %s' % file.name)

        for file in path.dirs():
            child = node.insertAsLastChild()
            c.setHeadString(child,'@view %s' % file.name)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 80
#@-leo
