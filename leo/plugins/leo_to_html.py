#@+leo-ver=4-thin
#@+node:danr7.20060902215215.1:@thin leo_to_html.py
#@@language python
#@@tabwidth -4

#@<< docstring >>
#@+node:danr7.20060902215215.2:<< docstring >>
'''leo_to_html converts a leo outline to an html web page.

Introduction
~~~~~~~~~~~~

This plugin takes an outline stored in LEO and converts it to html which is then
either saved in a file or shown in a browser. It is based on the original
leoToHTML 1.0 plugin by Dan Rahmel which had bullet list code by Mike Crowe.

The outline can be represented as a bullet list, a numbered list or using html
<h?> type headings. Optionally, the body text may be included in the output.

If desired, only the current node will be included in the output rather than
the entire outline.

An xhtml header may be included in the output, in which case the code will be
valid XHTML 1.0 Strict.

The plugin is fully scriptable as all its functionality is available through a
Leo_to_HTML object which can be imported and used in scripts.


Menu items
~~~~~~~~~~

If this plugin loads properly, the following menu items should appear in
your File > Export... menu in Leo.

	Save Outline as HTML  (equivalent to export-html)
	Save Node as HTML     (equivalent to export-html-node)
	Show Outline as HTML  (equivalent to show-html)
	Show Node as HTML     (equivalent to show-html-node)


Commands
~~~~~~~~

Several commands will also be made available

    + 'export-html' will export to a file according to current settings.
    + 'export-html-*' will export to a file using bullet type '*' which can be 'number', 'bullet' or 'head'.

The following commands will start a browser showing the html.

    +'show-html' will show the outline according to current settings.
    +'show-html-*' will show the outline using bullet type '*' which can be 'number', 'bullet' or 'head'.

The following commands are the same as above except only the current node is converted.

    +'export-html-node'
    +'export-html-node-*'
    +'show-html-node'
    +'show-html-node-*


Properties
~~~~~~~~~

There are several settings that can appear in the leo_to_html.ini properties
file in leo's plugins folder or be set via the Plugins > leo_to_html >
Properties... menu. These are:

exportpath:
    The path to the folder where you want to store the generate html file.

    Default: c:\

flagjustheadlines:
    Default: 'Yes' to include only headlines in the output.

flagignorefiles:
    Default: 'Yes' to ignore @file nodes.

use_xhtml:
    Yes to include xhtml doctype declarations and make the file valid XHTML 1.0 Strict.
    Otherwise only a simple <html> tag is used although the output will be xhtml
    compliant otherwise.

    Default: Yes

bullet_type:
    If this is 'bullet' then the output will be in the form of a bulleted list.
    If this is 'number' then the output will be in the form of a numbered list.
    If this is 'heading' then the output will use <h?> style headers.

    Anything else will result in <h?> type tags being used where '?' will be a
    digit starting at 1 and increasing up to a maximum of six depending on depth
    of nesting.

    Default: number

browser_command:
    Set this to the command needed to launch a browser on your system.

    Default:  c:\Program Files\Internet Explorer\IEXPLORE.EXE

'''
#@-node:danr7.20060902215215.2:<< docstring >>
#@nl
#@<< version history >>
#@+node:danr7.20060902215215.3:<< version history >>
#@@killcolor
#@+at
# 
# 1.00 - Finished testing with 4 different options & outlines
# 0.91 - Got initial headline export code working. Resolved bug in INI file 
# checking
# 0.90 - Created initial plug-in framework
# 1.1 ekr: Added init method.
# 2.0 plumloco:
#     - made gui independent
#     - made output xhtml compliant
#     - added ini options
#         - use_xhtml: 'Yes' to included xhtml headers in output.
#         - bullet_type: 'number', 'bullet', or 'head'.
#         - browser_command: the command needed to launch a browser.
#     - removed bullet/headlines dialog in favour of bullet_type ini option.
#     - added option to show output in a browser instead of saving to a file
#     - added extra menu items to save/show current node only
#     - added export-html-*-* commands
#     - added show-html-*-* commands
#     - added Leo_to_HTML object so all the plugins functionality can be 
# scripted.
# 2.1 plumloco:
#     - fixed bug in export of single nodes
#     - fixed to use tempdir to get a temp dir
#     - improved (and spellchecked :) docstring.
#     - added abspath module level method
# 
# 
# 
# 
#@-at
#@-node:danr7.20060902215215.3:<< version history >>
#@nl
#@<< imports >>
#@+node:danr7.20060902215215.4:<< imports >>
import leoGlobals as g
import leoPlugins
import ConfigParser
import re
import tempfile

#@-node:danr7.20060902215215.4:<< imports >>
#@nl


__version__ = '2.1'


pluginController = None


#@+others
#@+node:bob.20080107154936:module level functions
#@+node:bob.20080107154936.1:init

def init ():
    leoPlugins.registerHandler("create-optional-menus",createExportMenus)
    leoPlugins.registerHandler('after-create-leo-frame', onCreate)
    g.plugin_signon(__name__)
    # I think this should be ok for unit testing.
    return True

#@-node:bob.20080107154936.1:init
#@+node:bob.20080107154936.2:safe
def safe(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

#@-node:bob.20080107154936.2:safe
#@+node:bob.20080110210953:abspath
def abspath(*args):
    return g.os_path_abspath(g.os_path_join(*args))
#@nonl
#@-node:bob.20080110210953:abspath
#@+node:bob.20080107154936.3:onCreate
def onCreate (tag, keys):

    c = keys.get('c')
    if not c: return

    thePluginController = pluginController(c)
#@nonl
#@-node:bob.20080107154936.3:onCreate
#@+node:bob.20080107154936.4:createExportMenus
def createExportMenus (tag,keywords):

    c = keywords.get("c")

    for item, cmd in (
        ('Show Node as HTML', 'show-html-node'),
        ('Show Outline as HTML', 'show-html'),
        ('Save Node as HTML', 'export-html-node'),
        ('Save Outline as HTML', 'export-html'),
    ):
        c.frame.menu.insert('Export...', 3,
            label = item,
            command = lambda c = c, cmd=cmd: c.k.simulateCommand(cmd)
        )
#@-node:bob.20080107154936.4:createExportMenus
#@-node:bob.20080107154936:module level functions
#@+node:bob.20080107154757:class pluginController
class pluginController:

    #@    @+others
    #@+node:bob.20080107154757.1:__init__
    def __init__ (self,c):

        self.c = c
        # Warning: hook handlers must use keywords.get('c'), NOT self.c.

        for command in (
            'export-html',
            'export-html-bullet',
            'export-html-number',
            'export-html-head',

            'export-html-node',
            'export-html-node-bullet',
            'export-html-node-number',
            'export-html-node-head',

            'show-html',
            'show-html-bullet',
            'show-html-number',
            'show-html-head',

            'show-html-node',
            'show-html-node-bullet',
            'show-html-node-number',
            'show-html-node-head'
        ):
            method = getattr(self, command.replace('-','_'))
            c.k.registerCommand(command, shortcut=None, func=method)
    #@-node:bob.20080107154757.1:__init__
    #@+node:bob.20080107154757.3:export_html
    # EXPORT ALL

    def export_html(self, event=None, bullet=None, show=False, node=False):
        html = Leo_to_HTML(self.c)
        html.main(bullet=bullet, show=show, node=node)

    def export_html_bullet(self, event=None):
        self.export_html(bullet='bullet')

    def export_html_number(self, event=None):
        self.export_html(bullet='number')

    def export_html_head(self, event=None):
        self.export_html(bullet='head')

    # EXPORT NODE


    def export_html_node(self,event=None, bullet=None,):
        self.export_html(bullet=bullet, node=True)

    def export_html_node_bullet(self, event=None):
        self.export_html_node(bullet='bullet')

    def export_html_node_number(self, event=None):
        self.export_html_node(bullet='number')

    def export_html_node_head(self, event=None):
        self.export_html_node(bullet='head')


    # SHOW ALL


    def show_html(self, event=None, bullet=None):
        self.export_html(bullet=bullet, show=True)

    def show_html_bullet(self, event=None):
        self.show_html(bullet='bullet')

    def show_html_number(self, event=None):
        self.show_html(bullet='number')

    def show_html_head(self, event=None):
        self.show_html(bullet='head')


    ## SHOW NODE

    def show_html_node(self, event=None, bullet=None):
        self.export_html(bullet=bullet, show=True, node=True)

    def show_html_node_bullet(self, event=None):
        self.show_html_node(bullet='bullet')

    def show_html_node_number(self, event=None):
        self.show_html_node(bullet='number')

    def show_html_node_head(self, event=None):
        self.show_html_node(bullet='head')
    #@-node:bob.20080107154757.3:export_html
    #@-others
#@nonl
#@-node:bob.20080107154757:class pluginController
#@+node:bob.20080107154746:class Leo_to_HTML
class Leo_to_HTML(object):

    #@    @+others
    #@+node:bob.20080107154746.1:__init__

    def __init__(self, c):

        self.c = c
        self.basedir = ''
        self.path = ''
        self.reportColor = 'turquoise4'
        self.errorColor = 'red'
        self.fileColor = 'turquoise4'
        self.msgPrefix = 'leo_to_html: '

    #@-node:bob.20080107154746.1:__init__
    #@+node:bob.20080107154746.2:do_xhtml
    def do_xhtml(self, node=False):
        """Convert the tree to xhtml.

        Return the result as a string in self.xhtml.

        Only the code to represent the tree is generated, not the
        wraper code to turn it into a file.
        """

        self.xhtml = xhtml = []

        if node:
            root = self.c.currentPosition()
        else:
            root = self.c.rootPosition()

        if self.bullet_type != 'head':
            xhtml.append(self.openLevelString)

        if node:

            if self.bullet_type == 'head':
                self.doItemHeadlineTags(root)
            else:
                self.doItemBulletList(root)

        else:

            for pp in root.following_siblings_iter():

                if self.bullet_type == 'head':
                    self.doItemHeadlineTags(pp)
                else:
                    self.doItemBulletList(pp)

        if self.bullet_type != 'head':
            xhtml.append(self.closeLevelString)

        self.xhtml = '\n'.join(xhtml)


    #@+node:bob.20080107160008:doItemHeadlineTags
    def doItemHeadlineTags(self, p, level=1):
        """" Recursivley proccess an outline node into an xhtml list."""

        xhtml = self.xhtml

        self.doHeadline(p, level)
        self.doBodyElement(p, level)

        if p.hasChildren() and self.showSubtree(p):

            for item in p.children_iter():
                self.doItemHeadlineTags(item, level +1)




    #@-node:bob.20080107160008:doItemHeadlineTags
    #@+node:bob.20080107165629:doItemBulletList
    def doItemBulletList(self, p):
        """" Recursivley proccess an outline node into an xhtml list."""

        xhtml = self.xhtml

        xhtml.append(self.openItemString)

        self.doHeadline(p)
        self.doBodyElement(p)

        if p.hasChildren():

            xhtml.append(self.openLevelString)
            for item in p.children_iter():
                self.doItemBulletList(item)
            xhtml.append(self.closeLevelString)

        xhtml.append(self.closeItemString)
    #@-node:bob.20080107165629:doItemBulletList
    #@+node:bob.20080107154746.5:doHeadline
    def doHeadline(self, p, level=None):
        """Append wrapped headstring to ouput stream."""

        headline = safe(p.headString()).replace(' ', '&nbsp;')

        if level is None:
            self.xhtml.append(headline)
            return

        h = '%s' % min(level, 6)
        self.xhtml.append( self.openHeadlineString % h + headline + self.closeHeadlineString % h)
    #@-node:bob.20080107154746.5:doHeadline
    #@+node:bob.20080107154746.6:doBodyElement
    def doBodyElement(self, pp, level=None):
        """Append wrapped body string to output stream."""

        if not self.include_body: return

        self.xhtml.append(
            self.openBodyString \
            + '<pre>' + safe(pp.bodyString()) + '</pre>' \
            + self.closeBodyString
        )

    #@-node:bob.20080107154746.6:doBodyElement
    #@+node:bob.20080107175336:showSubtree
    def showSubtree(self, p):

        """Return True if subtree should be shown.

        subtree should be shown if it is not an @file node or if it
        is an @file node and flags say it should be shown.

        """

        s = p.headString()
        if not self.flagIgnoreFiles or s[:len('@file')] != '@file':
           return True 
    #@-node:bob.20080107175336:showSubtree
    #@-node:bob.20080107154746.2:do_xhtml
    #@+node:bob.20080107154746.9:main
    def main(self, bullet=None, show=False, node=False):
        """Generate the html and write the files.

        If 'bullet' is not recognized then the value of bullet_type from
        the the properties file will be used.

        If 'show' is True then the file will be saved to a temp dir and shown
        in a browser.

        """

        self.silent = show

        self.announce_start()

        self.loadConfig()

        if bullet in ('bullet', 'number', 'head'):
            self.bullet_type = bullet

        self.setup()

        if self.use_xhtml:
            self.template = self.getXHTMLTemplate()
        else:
            self.template = self.getPlainTemplate()

        self.do_xhtml(node)
        self.applyTemplate()

        if show:
            self.show()

        else:
            self.writeall()

        self.announce_end()


    #@-node:bob.20080107154746.9:main
    #@+node:bob.20080109063110.7:announce
    def announce(self, msg, prefix=None, color=None, silent=None):

        if silent is None:
            silent = self.silent

        if silent:
            return

        g.es('%s%s' % (prefix or self.msgPrefix, msg), color=color or self.reportColor)

    def announce_start(self, msg='running ...', prefix=None, color=None):
           self.announce(msg, prefix, color) 

    def announce_end(self, msg='done', prefix=None, color=None):
            self.announce(msg, prefix, color)

    def announce_fail(self, msg='failed', prefix=None, color=None):
        self.announce(msg, prefix, color= color or self.errorColor, silent=False) 
    #@-node:bob.20080109063110.7:announce
    #@+node:bob.20080107154746.11:loadConfig
    def loadConfig(self):

        def config(s):
            s = configParser.get("Main", s)
            #g.trace(s)
            if not s:
                s = ''
            return s.strip()

        def flag(s):
             ss = config(s)
             if ss:
                 return ss.lower()[0] in ('y', 't', '1')

        g.trace(g.app.loadDir,"..","plugins","leo_to_html.ini")
        fileName = abspath(g.app.loadDir,"..","plugins","leo_to_html.ini")
        configParser = ConfigParser.ConfigParser()
        configParser.read(fileName)

        self.flagIgnoreFiles =  flag("flagIgnoreFiles")
        self.include_body = not flag("flagJustHeadlines")

        self.basedir = config("exportPath") # "/"

        self.browser_command = config("browser_command")
        self.use_xhtml =  flag("use_xhtml")

        self.bullet_type = config( "bullet_type").lower()
        if self.bullet_type not in ('bullet', 'number', 'head'):
            self.bulletType = 'number'






    #@-node:bob.20080107154746.11:loadConfig
    #@+node:bob.20080109063110.8:setup
    def setup(self):

        self.openItemString = '<li>'
        self.closeItemString = '</li>'

        self.openBodyString = '<div>'
        self.closeBodyString = '</div>'


        self.openHeadlineString = ''
        self.closeHeadlineString = ''


        if self.bullet_type == 'head':

            self.openHeadlineString = '<h%s>'
            self.closeHeadlineString = '</h%s>'

            self.openBodyString = '<blockquote>'
            self.closeBodyString = '</blockquote>'


        else:

            if self.bullet_type == 'number':
                self.openLevelString = '<ol>'
                self.closeLevelString = '</ol>'

            else:

                self.openLevelString = '<ul>'
                self.closeLevelString = '</ul>'

            self.openBlockquoteString = '<div>'
            self.closeBlockquoteString = '</div>'


        myFileName = self.c.frame.shortFileName()    # Get current outline filename
        if not myFileName:
            myFileName = 'untitiled'

        self.title = myFileName

        if myFileName[-4:].lower() == '.leo':
            myFileName = myFileName[:-4]            # Remove .leo suffix

        self.myFileName = myFileName + '.html'
    #@-node:bob.20080109063110.8:setup
    #@+node:bob.20080107154746.10:applyTemplate
    def applyTemplate(self, template=None):

        xhtml = self.xhtml

        if template is None:
            template = self.template

        self.xhtml = template%(
            self.title,
            xhtml
        )
    #@-node:bob.20080107154746.10:applyTemplate
    #@+node:bob.20080109063110.9:show

    def show(self):

        filepath = abspath(self.basedir, self.path, self.myFileName)

        filename = 'leo_show_' + re.sub('[/\\:]', '_', filepath)

        filepath = abspath(tempfile.gettempdir(), filename)

        self.write(filepath, self.xhtml, basedir='', path='')



        try:
            import subprocess
        except:
            subprocess = None
            self.announce_fail('Show failed - cant import subprocess')

        if subprocess:
            try:
                subprocess.Popen([self.browser_command,  "file://%s" % filepath])
            except:
                self.announce_fail('Show failed - cant open browser')
    #@-node:bob.20080109063110.9:show
    #@+node:bob.20080107171331:writeall
    def writeall(self):
        """Write all the files"""

        self.write(self.myFileName, self.xhtml)
    #@-node:bob.20080107171331:writeall
    #@+node:bob.20080107154746.13:write
    def write(self, name, data, basedir=None, path=None):
        """Write a single file.

        The `name` can be a file name or a ralative path which will be
        added to basedir and path to create a full path for the file to be
        written.

        If basedir is None self.basedir will be used and if path is none
        self.path will be used.

        """

        if basedir is None:
            basedir = self.basedir

        if path is None:
            path = self.path

        filepath = abspath(basedir, path , name)

        try:
            f = open(filepath, 'wb')
            ok = True
        except IOError:
            ok = False

        if ok:
            try:
                try:
                    f.write(data.encode('utf-8'))
                finally:
                    f.close()
            except IOError:
                ok = False


        if ok:
            self.announce('ouput file - %s' % filepath, color=self.fileColor)
            return True

        self.announce_fail('failed writing to %s' % filepath)
        return False
    #@-node:bob.20080107154746.13:write
    #@+node:bob.20080107175154:getXHTMLTemplate
    def getXHTMLTemplate(self):
        """Returns a string containing a template for the outline page.

        The string should have positions in order, for:
            title and body text.

        """

        return """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
    <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
    <title>
        %s
    </title>
    </head>
    <body>
    %s
    </body></html>
    """

    #@-node:bob.20080107175154:getXHTMLTemplate
    #@+node:bob.20080107175336.1:getPlainTemplate
    def getPlainTemplate(self):
        """Returns a string containing a template for the outline page.

        The string should have positions in order, for:
            title and body text.

        """

        return """<html>
    <head>
    <title>
        %s
    </title>
    </head>
    <body>
    %s
    </body></html>
    """
    #@-node:bob.20080107175336.1:getPlainTemplate
    #@-others
#@-node:bob.20080107154746:class Leo_to_HTML
#@-others
#@nonl
#@-node:danr7.20060902215215.1:@thin leo_to_html.py
#@-leo
