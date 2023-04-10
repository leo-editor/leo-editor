#@+leo-ver=5-thin
#@+node:danr7.20060902215215.1: * @file ../plugins/leo_to_html.py
#@+<< docstring >>
#@+node:danr7.20060902215215.2: ** << docstring >>
r"""
Converts a leo outline to an html web page.

This plugin takes an outline stored in Leo and converts it to html which is then
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

**Menu items and @settings**

If this plugin loads properly, the following menu items should appear in
your File > Export... menu in Leo::

    Save Outline as HTML  (equivalent to export-html)
    Save Node as HTML     (equivalent to export-html-node)
    Show Outline as HTML  (equivalent to show-html)
    Show Node as HTML     (equivalent to show-html-node)

*Unless* the following appears in an @setting tree::

    @bool leo_to_html_no_menus = True

in which case the menus will **not** be created. This is so that the user can
use @menu and @item to decide which commands will appear in the menu and where.

**Commands**

Several commands will also be made available

export-html
  will export to a file according to current settings.
export-html-*
  will export to a file using bullet type '*' which can be
  **number**, **bullet** or **head**.

The following commands will start a browser showing the html.

show-html
  will show the outline according to current settings.

show-html-*
  will show the outline using bullet type '*' which can be
  **number**, **bullet** or **head**.

The following commands are the same as above except only the current node is converted::

    export-html-node
    export-html-node-*
    show-html-node
    show-html-node-*

**Properties**

.. note::

    As of Mar. 2014 regular Leo @string settings starting with
    `leo_to_html_` are checked first, before the ``.ini`` file.
    E.g. ``@string leo_to_html_flagjustheadlines = No`` has the
    same effect as ``flagjustheadlines = No`` in the ``.ini``, and
    takes precedence.

There are several settings that can appear in the leo_to_html.ini properties
file in leo's plugins folder or be set via the Plugins > leo_to_html >
Properties... menu. These are:

exportpath:
    The path to the folder where you want to store the generated html file.
    Default: c:\\

flagjustheadlines:
    Default: 'Yes' to include only headlines in the output.

flagignorefiles:
    Default: 'Yes' to ignore @file nodes.

use_xhtml:
    Yes to include xhtml doctype declarations and make the file valid XHTML 1.0 Strict.
    Otherwise only a simple <html> tag is used although the output will be xhtml
    compliant otherwise. Default: Yes

bullet_type:
    If this is 'bullet' then the output will be in the form of a bulleted list.
    If this is 'number' then the output will be in the form of a numbered list.
    If this is 'heading' then the output will use <h?> style headers.

    Anything else will result in <h?> type tags being used where '?' will be a
    digit starting at 1 and increasing up to a maximum of six depending on depth
    of nesting. Default: number

browser_command:
    Set this to the command needed to launch a browser on your system or leave it blank
    to use your systems default browser.

    If this is an empty string or the browser can not be launched using this command then
    python's `webbrowser` module will be tried. Using a bad command here will slow down the
    launch of the default browser, better to leave it blank.
    Default: empty string

**Configuration**

At present, the file leo/plugins/leo_to_html.ini contains configuration
settings. In particular, the default export path, "c:\" must be changed for \*nix
systems.

"""
#@-<< docstring >>

# Edited by plumloco, bobjack, and EKR.

#@+<< imports >>
#@+node:danr7.20060902215215.4: ** << imports >>
import configparser as ConfigParser
import os
import subprocess
import tempfile
from typing import List
import webbrowser
from leo.core import leoGlobals as g
#@-<< imports >>

#@+others
#@+node:bob.20080107154936: ** module level functions
#@+node:bob.20080107154936.1: *3* init
def init():
    """Return True if the plugin has loaded successfully."""
    g.registerHandler("create-optional-menus", createExportMenus)
    g.registerHandler('after-create-leo-frame', onCreate)
    g.plugin_signon(__name__)
    # I think this should be ok for unit testing.
    return True

#@+node:bob.20080107154936.2: *3* safe
def safe(s):
    """Convert special characters to html entities."""
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

#@+node:bob.20080110210953: *3* abspath
def abspath(*args):
    """Join the arguments and convert to an absolute file path."""
    return g.finalize_join(*args)
#@+node:bob.20080107154936.3: *3* onCreate
def onCreate(tag, keys):

    """
    Handle 'after-create-leo-frame' hooks by creating a plugin
    controller for the commander issuing the hook.
    """
    c = keys.get('c')
    if c:
        pluginController(c)
#@+node:bob.20080107154936.4: *3* createExportMenus
def createExportMenus(tag, keywords):

    """Create menu items in File -> Export menu.

    Menu's will not be created if the following appears in an @setting tree::

        @bool leo_to_html_no_menus = True

    This is so that the user can use @menu to decide which commands will
    appear in the menu and where.

    """
    # pylint: disable=undefined-variable
    # c *is* defined.
    c = keywords.get("c")
    if c.config.getBool('leo-to-html-no-menus'):
        return
    for item, cmd in (
        ('Show Node as HTML', 'show-html-node'),
        ('Show Outline as HTML', 'show-html'),
        ('Save Node as HTML', 'export-html-node'),
        ('Save Outline as HTML', 'export-html'),
    ):
        c.frame.menu.insert('Export...', 3,
            label=item,
            command=lambda c=c, cmd=cmd: c.k.simulateCommand(cmd)
        )
#@+node:bob.20080107154757: ** class pluginController
class pluginController:
    """A per commander plugin controller to create and handle
    minibuffer commands that control the plugins functions.
    """

    #@+others
    #@+node:bob.20080107154757.1: *3* __init__(pluginController, leo_to_html.py)
    def __init__(self, c):
        """
        Initialize pluginController by registering minibuffer commands.
        """
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
            method = getattr(self, command.replace('-', '_'))
            c.k.registerCommand(command, method)
    #@+node:bob.20080107154757.3: *3* export_html
    # EXPORT ALL

    def export_html(self, event=None, bullet=None, show=False, node=False):
        """Save outline as an HTML file according to current settings."""
        html = Leo_to_HTML(self.c)
        html.main(bullet=bullet, show=show, node=node)

    def export_html_bullet(self, event=None):
        """Save outline as HTML file with bullets as unordered lists."""
        self.export_html(bullet='bullet')

    def export_html_number(self, event=None):
        """Save outline as HTML file with bullets as ordered lists."""
        self.export_html(bullet='number')

    def export_html_head(self, event=None):
        """Save outline as HTML file with bullets as headings."""
        self.export_html(bullet='head')

    # EXPORT NODE


    def export_html_node(self, event=None, bullet=None,):
        """Save current node as an HTML file according to current settings."""
        self.export_html(bullet=bullet, node=True)

    def export_html_node_bullet(self, event=None):
        """Save current node as an HTML file with bullets as unordered lists."""
        self.export_html_node(bullet='bullet')

    def export_html_node_number(self, event=None):
        """Save current node as an HTML file with bullets as ordered lists."""
        self.export_html_node(bullet='number')

    def export_html_node_head(self, event=None):
        """Save current node as an HTML file with bullets as headings."""
        self.export_html_node(bullet='head')


    # SHOW ALL


    def show_html(self, event=None, bullet=None):
        """Start browser and show the outline as HTML according to current settings."""
        self.export_html(bullet=bullet, show=True)

    def show_html_bullet(self, event=None):
        """Start browser and show the outline as HTML with bullets as unordered lists."""
        self.show_html(bullet='bullet')

    def show_html_number(self, event=None):
        """Start browser and show the outline as HTML with bullets as ordered lists."""
        self.show_html(bullet='number')

    def show_html_head(self, event=None):
        """Start browser and show the outline as HTML with bullets as headings."""
        self.show_html(bullet='head')


    ## SHOW NODE

    def show_html_node(self, event=None, bullet=None):
        """Start browser and show the current node as HTML according to current settings."""
        self.export_html(bullet=bullet, show=True, node=True)

    def show_html_node_bullet(self, event=None):
        """Start browser and show the current node as HTML with bullets as unordered lists."""
        self.show_html_node(bullet='bullet')

    def show_html_node_number(self, event=None):
        """Start browser and show the current node as HTML with bullets as ordered lists."""
        self.show_html_node(bullet='number')

    def show_html_node_head(self, event=None):
        """Start browser and show the current node as HTML with bullets as headings."""
        self.show_html_node(bullet='head')
    #@-others
#@+node:bob.20080107154746: ** class Leo_to_HTML
class Leo_to_HTML:

    """
    This class provides all the functionality of the leo_to_html plugin.

    See the docstring for the leo_to_html module for details.
    """

    #@+others
    #@+node:bob.20080107154746.1: *3* __init__

    def __init__(self, c=None):

        """Constructor."""

        self.c = c
        self.basedir = ''
        self.path = ''
        self.reportColor = 'turquoise4'
        self.errorColor = 'red'
        self.fileColor = 'turquoise4'
        self.msgPrefix = 'leo_to_html: '

    #@+node:bob.20080107154746.2: *3* do_xhtml
    def do_xhtml(self, node=False):
        """Convert the tree to xhtml.

        Return the result as a string in self.xhtml.

        Only the code to represent the tree is generated, not the
        wrapper code to turn it into a file.
        """

        xhtml: List[str] = []

        if node:
            root = self.c.p
        else:
            root = self.c.rootPosition()

        if self.bullet_type != 'head':
            xhtml.append(self.openLevelString)

        if self.bullet_type == 'head':
            self.doItemHeadlineTags(root)
        else:
            self.doItemBulletList(root)

        if not node:

            for pp in root.following_siblings():

                if self.bullet_type == 'head':
                    self.doItemHeadlineTags(pp)
                else:
                    self.doItemBulletList(pp)

        if self.bullet_type != 'head':
            xhtml.append(self.closeLevelString)

        self.xhtml = '\n'.join(xhtml)
    #@+node:bob.20080107160008: *4* doItemHeadlineTags
    def doItemHeadlineTags(self, p, level=1):
        """" Recursively process an outline node into an xhtml list."""
        self.doHeadline(p, level)
        self.doBodyElement(p, level)
        if p.hasChildren() and self.showSubtree(p):
            for item in p.children():
                self.doItemHeadlineTags(item, level + 1)
    #@+node:bob.20080107165629: *4* doItemBulletList
    def doItemBulletList(self, p):
        """" Recursively process an outline node into an xhtml list."""

        xhtml = self.xhtml

        xhtml.append(self.openItemString)

        self.doHeadline(p)
        self.doBodyElement(p)

        if p.hasChildren():

            xhtml.append(self.openLevelString)
            for item in p.children():
                self.doItemBulletList(item)
            xhtml.append(self.closeLevelString)

        xhtml.append(self.closeItemString)
    #@+node:bob.20080107154746.5: *4* doHeadline
    def doHeadline(self, p, level=None):
        """Append wrapped headline string to output stream."""

        headline = safe(p.h).replace(' ', '&nbsp;')

        if level is None:
            self.xhtml.append(headline)
            return

        h = '%s' % min(level, 6)
        self.xhtml.append(self.openHeadlineString % h + headline + self.closeHeadlineString % h)
    #@+node:bob.20080107154746.6: *4* doBodyElement
    def doBodyElement(self, pp, level=None):
        """Append wrapped body string to output stream."""

        if not self.include_body:
            return

        self.xhtml.append(
            self.openBodyString +
            '<pre>' + safe(pp.b) + '</pre>' +
            self.closeBodyString
        )

    #@+node:bob.20080107175336: *4* showSubtree
    def showSubtree(self, p):
        """
        Return True if subtree should be shown.

        subtree should be shown if it is not an @file node or if it
        is an @file node and flags say it should be shown.

        """
        s = p.h
        if not self.flagIgnoreFiles or s[: len('@file')] != '@file':
            return True
        return False
    #@+node:bob.20080107154746.9: *3* main
    def main(self, bullet=None, show=False, node=False):
        """
        Generate the html and write the files.

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
        self.do_xhtml(node)
        self.applyTemplate()
        if show:
            self.show()
        else:
            self.writeall()
        self.announce_end()
    #@+node:bob.20080109063110.7: *3* announce
    def announce(self, msg, prefix=None, color=None, silent=None):
        """Print a message if flags allow."""

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
        self.announce(msg, prefix, color=color or self.errorColor, silent=False)
    #@+node:bob.20080107154746.11: *3* loadConfig
    def loadConfig(self):
        """Load configuration from a .ini file."""

        def config(s):

            ss = self.c.config.getString("leo_to_html_%s" % s)
            if ss is None:
                s = configParser.get("Main", s)
            else:
                s = ss
            if not s:
                s = ''
            return s.strip()

        def flag(s):
            ss = config(s)
            if ss:
                return ss.lower()[0] in ('y', 't', '1')
            return None

        fileName = abspath(g.app.loadDir, "..", "plugins", "leo_to_html.ini")
        configParser = ConfigParser.ConfigParser()
        configParser.read(fileName)

        self.flagIgnoreFiles = flag("flagIgnoreFiles")
        self.include_body = not flag("flagJustHeadlines")

        self.basedir = config("exportPath")  # "/"

        self.browser_command = config("browser_command").strip()

        self.use_xhtml = flag("use_xhtml")
        if self.use_xhtml:
            self.template = self.getXHTMLTemplate()
        else:
            self.template = self.getPlainTemplate()

        self.bullet_type = config("bullet_type").lower()
        if self.bullet_type not in ('bullet', 'number', 'head'):
            self.bulletType = 'number'

    #@+node:bob.20080109063110.8: *3* setup
    def setup(self):
        """Set various parameters."""

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


        myFileName = self.c.frame.shortFileName()  # Get current outline filename
        if not myFileName:
            myFileName = 'untitled'

        self.title = myFileName

        if myFileName[-4:].lower() == '.leo':
            myFileName = myFileName[:-4]  # Remove .leo suffix

        self.myFileName = myFileName + '.html'
    #@+node:bob.20080107154746.10: *3* applyTemplate
    def applyTemplate(self, template=None):

        """
        Fit self.xhtml and self.title into an (x)html template.

        Place the result in self.xhtml.

        The template string in self.template should have too %s place
        holders.  The first for the title the second for the body.

        """

        xhtml = self.xhtml

        if template is None:
            template = self.template

        self.xhtml = template % (
            self.title,
            xhtml
        )
    #@+node:bob.20080109063110.9: *3* show
    def show(self):

        """
        Convert the outline to xhtml and display the results in a browser.

        If browser_command is set, this command will be used to launch the browser.
        If it is not set, or if the command fails, the default browser will be used.
        Setting browser_command to a bad command will slow down browser launch.

        """
        tempdir = g.finalize_join(tempfile.gettempdir(), 'leo_show')
        if not g.os_path_exists(tempdir):
            os.mkdir(tempdir)
        filename = g.sanitize_filename(self.myFileName)
        filepath = g.finalize_join(tempdir, filename + '.html')
        self.write(filepath, self.xhtml, basedir='', path='')
        url = "file://%s" % filepath
        msg = ''
        if self.browser_command:
            g.trace(self.browser_command)
            try:
                subprocess.Popen([self.browser_command, url])
                return
            except Exception:
                msg = 'can\'t open browser using \n    %s\n' % self.browser_command + \
                'Using default browser instead.'
        if msg:
            self.announce_fail(msg)
        webbrowser.open(url)
    #@+node:bob.20080107171331: *3* writeall
    def writeall(self):
        """Write all the files"""

        self.write(self.myFileName, self.xhtml)
    #@+node:bob.20080107154746.13: *3* write
    def write(self, name, data, basedir=None, path=None):
        """Write a single file.

        The `name` can be a file name or a relative path which will be
        added to basedir and path to create a full path for the file to be
        written.

        If basedir is None self.basedir will be used and if path is none
        self.path will be used.

        """
        if basedir is None:
            basedir = self.basedir
        if path is None:
            path = self.path
        filepath = abspath(basedir, path, name)
        try:
            f = open(filepath, 'wb')
        except Exception:
            g.error('can not open: %s' % (filepath))
            # g.es_exception()
            return False
        try:
            try:
                f.write(data.encode('utf-8'))
                self.announce('output file: %s' % (filepath),
                    color=self.fileColor)
                ok = True
            except Exception:
                g.error('write failed: %s' % (filepath))
                g.es_exception()
                ok = False
        finally:
            f.close()

        return ok
    #@+node:bob.20080107175154: *3* getXHTMLTemplate
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

    #@+node:bob.20080107175336.1: *3* getPlainTemplate
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
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
