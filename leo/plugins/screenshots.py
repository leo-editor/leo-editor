#@+leo-ver=5-thin
#@+node:ekr.20101121031443.5330: * @file ../plugins/screenshots.py
#@+<< docstring >>
#@+node:ekr.20100908115707.5554: ** << docstring >>
#@@pagewidth 80
r""" Creates stand-alone slideshows containing screenshots.

This plugin defines the following commands:
    
- **help-for-screenshots**: print this message to Leo's log pane.
- **take-local-screen-shot**: take a screenshot of Leo's main window.
- **take-global-screen-shot**: take a screenshot of the entire screen.
- **slide-show-info**: print the settings in effect.
- **make-slide** and **make-slide-show**, collectively called **slide
  commands**, create collections of slides from **@slideshow** trees containing
  **@slide** nodes.
  
Slides may link to screenshots. The slide commands can generate screenshots from
**@screenshot-tree** nodes, but this feature has proven to be clumsy and
inflexible. It is usually more convenient to use screenshots taken with a
program such as Wink. The **meld-slides** command creates references to
externally-generated screenshots within @slide nodes.

\@slide nodes may contain **@url nodes**:
- @url nodes allow you to see various files (slides, initial screenshots,
  working files and final screenshots).
- @url nodes guide the meld script and the commands defined by this plugin By
  inserting or deleting these @url nodes you (or your scripts) can customize how
  the commands (and meld) work. In effect, the @url nodes become per-slide
  settings.

**Prerequisites**

Inkscape (Required)
  An SVG editor: http://www.inkscape.org/
  Allows the user to edit screenshots.
  Required to create final output (PNG) files.

PIL, aka pillow (Optional but highly recommended)
  pip install pillow
  https://python-pillow.org/

Wink (Optional)
  A program that creates slideshows and slides.
  http://www.debugmode.com/wink/

**Summary**

@slideshow <slideshow-name>
  Creates the folder:
  <sphinx_path>/slides/<slideshow-name>

@slide <ignored text>
  Creates slide-<slide-number>.html
  (in the sphinx _build directory).
  **Note**: the plugin skips any @slide nodes
  with empty body text.

@screenshot
  Specifies the contents of the screenshot.

**Options** are child nodes of @slideshow or
\@slide nodes that control the make-slide and
make-slide-show commands. See the Options section
below.

The make-slide and make-slide-show commands
create the following @url nodes as children
of each @slide node:

@url built slide
  Contains the absolute path to the final slide in
  the _build/html subfolder of the slideshow
  folder. If present, this @url node completely
  disables rebuilding the slide.

@url screenshot
  Contains the absolute path to the original
  screenshot file. If present, this @url node
  inhibits taking the screenshot.

@url working file
  Contains the absolute path to the working file.
  If present, this @url node disables taking the
  screenshot, creating the working file. The final
  output file will be regenerated if the working
  file is newer than the final output file.

@url final output file
  Contains the absolute path to the final output
  file.

Thus, to completely recreate an @slide node, you
must delete any of the following nodes that appear
as its children::

    @url screenshot
    @url working file
    @url built slide

**Making slides**

For each slide, the make-slide and make-slide-show
commands do the following:

1. Create a slide.

  If the @slide node contains an @screenshot tree,
  the plugin appends an ``.. image::`` directive
  referring to the screenshot to the body text of
  the @slide node. The plugin also creates a child
  @image node referring to the screenshot.

2. (Optional) Create a screenshot.

  The plugin creates a screenshot for an @slide
  node only if the @slide node contains an
  @screenshot node as a direct child.

  **Important**: this step has largely been
  superseded by the ``@button meld`` script in
  LeoDocs.leo.

  Taking a screenshot involves the following steps:

  A. Create the **target outline**: screenshot-setup.leo.

    The target outline contains consists of all
    the children (and their descendants) of the
    @screenshot node.

  B. Create the **screenshot**, a bitmap (PNG) file.

    The slide commands take a screen shot of the
    target outline. The @pause option opens the
    target outline but does *not* take the
    screenshot. The user must take the screenshot
    manually. For more details, see the the
    options section below.

  C. Convert the screenshot file to a **work file**.

    The work file is an SVG (Scalable Vector
    Graphics) file: http://www.w3.org/Graphics/SVG/.

  D. (Optional) Edit the work file.

    If the @slide node has a child @edit node, the
    plugin opens Inkscape so that the user can
    edit the work file.

  E. Render the **final output file**.

    The plugin calls Inkscape non-interactively to
    render the final output file (a PNG image)
    from the work file. If the Python Imaging
    Library (PIL) is available, this step will use
    PIL to improve the quality of the final output
    file.

3. Build the slide using Sphinx.

  After making all files, the plugins runs Sphinx
  by running 'make html' in the slideshow folder.
  This command creates the final .html files in the
  _build/html subfolder of the slideshow folder.

4. Create url nodes.

  Depending on options, and already-existing @url
  nodes, the make-slide and make-slide-show
  commands may create one or more of the following
  \@url nodes::

    @url built slide
    @url screenshot
    @url working file
    @url final output file

**Options and settings**

You specify options in the headlines of nodes.
**Global options** appear as direct children of
\@slideshow nodes and apply to all @slide nodes
unless overridden by a local option. **Local
options** appear as direct children of an @slide
node and apply to only to that @slide node.

**Global options nodes**

The following nodes may appear *either* as a
direct child of the @slideshow node or as the
direct child of an @slide node.

@sphinx_path = <path>
  This directory contains the slides directory,
  and the following files: 'conf.py',
  'Leo4-80-border.jpg', 'Makefile' and 'make.bat'.

@screenshot_height = <int>
  The height in pixels of screenshots.

@screenshot_width = <int>
  The height in pixels of screenshots.

@template_fn = <path>
  The absolute path to inkscape-template.svg

@title = <any text>
  The title to use for one slide or the entire
  slideshow.

@title_pattern = <pattern>
  The pattern used to generate patterns for one
  slide or the entire slideshow. The title is
  computed as follows::

    d = {
        'slideshow_name':slideshow_name,
        'slide_name':    slide_name,
        'slide_number':  sc.slide_number,
    }
    title = (pattern % (d)).title()

  If neither an @title or @title_pattern option
  node applies, the title is the headline of the
  \@slide node. If this is empty, the default
  pattern is::

    '%(slideshow_name)s:%(slide_number)s'

\@verbose = True/False
  True (or true or 1):  generate informational message.
  False (or false or 0): suppress informational messages.

\@wink_path = <path>
  This path contains screenshots created by wink.
  This is used only by the meld-slides command.

**Local options nodes**

The following nodes are valid only as the direct
child of an @slide node.

@callout <any text>
  Generates a text callout in the working .svg file.
  An @slide node may have several @callout children.

@edit = True/False
  If True (or true or 1) the plugin enters
  Inkscape interactively after taking a
  screenshot.

@markers = <list of integers>
  Generates 'numbered balls' in the working .svg file.

@pause = True/False
  If True (or true or 1) the user must take the
  screenshot manually. Otherwise, the plugin takes
  the screenshot automatically.

  If the slide node contains an @pause node as one
  of its directive children, the slide commands
  open the target node, but do *not* take a screen
  shot.

  The user may adjust the screen as desired, for
  example by selecting menus or showing dialogs.
  The *user* must then take the screen shot
  manually. **Important**: the screenshot need not
  be of Leo--it could be a screenshot of anything
  on the screen.

  As soon as the user closes the target
  outline, the slide commands look for the screen
  shot on the clipboard. If found, the slide
  commands save the screenshot to the screenshot
  file.

@screenshot
  The root of a tree that becomes the entire
  contents of screenshot. No screenshot is taken
  if this node does not exist.

@select <headline>
  Causes the given headline in the @screenshot
  outline to be selected before taking the screenshot.

**Settings**

@string screenshot-bin = <path to inkscape.exe>
  The full path to the Inkscape program.

**File names**

Suppose the @slide node is the n'th @slide node in
the @slideshow tree whose sanitized name is
'name'. The following files will be created in
(relative to) the slideshow directory::

    slide-n.html.txt:   the slide's rST source.
    screenshot-n.png:   the original screenshot.
    screenshot-n.svg:   the working file.
    slide-n.png:        the final output file.
    _build/html/slide-n.html: the final slide.

"""
#@@pagewidth 50
#@-<< docstring >>
#@+<< imports >>
#@+node:ekr.20100908110845.5604: ** << imports >>
import copy
import glob
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import xml.etree.ElementTree as etree

from leo.core import leoGlobals as g
from leo.core.leoQt import QtCore

# Third-party imports: Warnings will be given later.
try:
    from PIL import Image  # pylint: disable=import-error
except Exception:
    Image = None
try:
    from PIL import ImageChops  # pylint: disable=import-error
except ImportError:
    ImageChops = None

# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.
#@-<< imports >>

screenshot_number = 0

# To do: create _static folder.

#@+others
#@+node:ekr.20100914090933.5771: ** Top level
#@+node:ekr.20100908110845.5606: *3*  init (screenshots.py)
def init():
    """Return True if the plugin has loaded successfully."""
    g.plugin_signon(__name__)
    return True
#@+node:ekr.20100908110845.5581: *3* g.command(apropos-slides)
@g.command('help-for-screenshots')
def help_for_screen_shots(event):
    # Just print the module's docstring.
    g.es(__doc__)
#@+node:ekr.20100908110845.5583: *3* g.command(make-slide)
@g.command('make-slide')
def make_slide_command(event):
    c = event.get('c')
    if c:
        sc = ScreenShotController(c)
        sc.make_slide_command(c.p)
        g.note('make-slide finished')
#@+node:ekr.20100911044508.5634: *3* g.command(make-slide-show)
@g.command('make-slide-show')
def make_slide_show_command(event=None):
    c = event.get('c')
    if c:
        sc = ScreenShotController(c)
        sc.make_slide_show_command(c.p)
        g.note('make-slide-show finished')
#@+node:ekr.20101113193341.5459: *3* g.command(meld-slides)
@g.command('meld-slides')
def meld_slides_command(event):
    """Meld Wink slides into an @slideshow folder.

    Copy screenshot files from the wink_dir to slideshow_dir, numbering
    the destination files to reflect "holes" created by @no-screenshot
    nodes.

    This script carefully checks that the number of screenshot files
    matches the number of screenshots referenced by the @slide nodes.
    No copying takes place if the numbers are not as expected.
    """
    c = event.get('c')
    if c:
        sc = ScreenShotController(c)
        sc.meld_slides_command(c.p)
#@+node:ekr.20101004082701.5733: *3* g.command(slide-show-info)
@g.command('slide-show-info')
def slide_show_info_command(event):
    c = event.get('c')
    if c:
        sc = ScreenShotController(c)
        sc.slide_show_info_command(c.p)
#@+node:ekr.20100914090933.5770: *3* g.command(take-local/global-screen-shot)
@g.command('take-screen-shot')
@g.command('take-local-screen-shot')
def start_local_screenshot(event):
    """Wait 5 seconds, then take a screen shot of Leo's main window."""
    start_screenshot('local', take_local_screenshot)

@g.command('take-global-screen-shot')
def start_global_screen_shot(event):
    """Wait 5 seconds, then take a screen shot of the entire screen."""
    start_screenshot('global', take_global_screenshot)

def start_screenshot(kind, callback):
    """Call the callback after 5 seconds."""
    global screenshot_number
    screenshot_number += 1
    print(f"I'll take a {kind} screenshot number {screenshot_number} in 5 seconds")
    QtCore.QTimer.singleShot(5000, callback)

def take_global_screenshot():
    screenshot_helper(0)

def take_local_screenshot():
    app = g.app.gui.qtApp
    screenshot_helper(app.activeWindow().winId())  # Only Leo's main window.

def screenshot_helper(window_id):
    """Take a screenshot of the given window."""
    global screenshot_number
    app = g.app.gui.qtApp
    screen = app.primaryScreen()
    if screen is not None:
        # Save to the home directory.
        file_name = os.path.normpath(os.path.expanduser(
            f"~/.leo/screenshot-{screenshot_number}.png"))
        pixmap = screen.grabWindow(window_id)
        pixmap.save(file_name, 'png')
        print(f"Screenshot saved in {file_name}")
#@+node:ekr.20100908110845.5531: ** class ScreenShotController
class ScreenShotController:
    """A class to take screen shots and control Inkscape.

    help-for-screenshots contains a more complete description."""
    #@+others
    #@+node:ekr.20100908110845.5532: *3*  ctor & helpers
    def __init__(self, c):
        self.c = c
        # Defaults.
        self.default_screenshot_height = 700
        self.default_screenshot_width = 900
        # Used with a dict whose keys are 'slideshow_name','slide_name','slide_number'
        self.default_slide_pattern = '%(slideshow_name)s:%(slide_number)s'
        self.default_verbose_flag = True
        # Options that may be set in @settings nodes.
        self.inkscape_bin = self.get_inkscape_bin()  # The path to the Inkscape executable.
        # Options that may be set in children of
        # *either* the @slideshow node or any @slide node.
        self.screenshot_height = None
        self.screenshot_width = None
        self.slide_pattern = None
        self.sphinx_path = None
        self.template_fn = None
        self.title = None
        self.title_pattern = None
        self.verbose = True
        self.wink_path = None
        # Options that may be set only in children of @slide nodes.
        self.callouts = []
        self.edit_flag = False
        self.markers = []
        self.output_fn = None
        self.pause_flag = None
        self.screenshot_tree = None
        self.select_node = None
        # Computed data...
        self.at_image_fn = None
        self.directive_fn = None
        self.screenshot_fn = None
        self.screenshot_tree = None
        self.slide_base_name = None
        self.slide_fn = None
        self.slideshow_node = None
        self.slide_node = None
        self.slide_number = 1
        self.slideshow_path = None
        self.working_fn = None
        # Dimension cache.
        self.dimCache = {}
        self.is_reads, self.is_cache = 0, 0
        # Internal constants.
        # element IDs which should exist in the SVG template
        self.ids = [
            "co_bc_1",  # 1 digit black circle
            "co_bc_2",  # 2 digit black circle
            "co_bc_text_1",  # text holder for 1 digit black circle
            "co_bc_text_2",  # text holder for 2 digit black circle
            "co_frame",  # frame for speech balloon callout
            "co_g_bc_1",  # group for 1 digit black circle
            "co_g_bc_2",  # group for 2 digit black circle
            "co_g_co",  # group for speech balloon callout
            "co_shot",  # image for screen shot
            "co_text_holder",  # text holder for speech balloon callout
        ]
        self.xlink = "{http://www.w3.org/1999/xlink}"
        # self.namespace = {'svg': "http://www.w3.org/2000/svg"}
    #@+node:ekr.20100913085058.5657: *4* get_inkscape_bin
    def get_inkscape_bin(self):
        c = self.c
        bin = c.config.getString('screenshot-bin').strip('"').strip("'")
        if bin:
            if g.os_path_exists(bin):
                self.inkscape_bin = bin
            else:
                g.warning('Invalid @string screenshot-bin:', bin)
        if not bin:
            g.warning('Inkscape not found. No editing is possible.')
        return bin
    #@+node:ekr.20101004082701.5731: *3* commands
    #@+node:ekr.20101004082701.5732: *4* sc.slide-show-info_command
    def slide_show_info_command(self, p):
        sc = self
        ok = sc.init(p)
        if not ok:
            g.error('sc.init failed')
            return
        table = (
            ('\npaths...', ''),
            ('at_image_fn      ', sc.at_image_fn),
            ('directive_fn     ', sc.directive_fn),
            ('output_fn        ', sc.output_fn),
            ('screenshot_fn    ', sc.screenshot_fn),
            ('sphinx_path      ', sc.sphinx_path),
            ('slide_fn         ', sc.slide_fn),
            ('slideshow_path   ', sc.slideshow_path),
            ('template_fn      ', sc.template_fn),
            ('working_fn       ', sc.working_fn),
            ('\nnodes...', ''),
            ('screenshot_tree  ', sc.screenshot_tree and sc.screenshot_tree.h or 'None'),
            ('select_node      ', sc.select_node),  # A string, not a node!
            ('slide_node       ', sc.slide_node.h),
            ('\nother args...', ''),
            ('edit_flag        ', sc.edit_flag),
            ('pause_flag       ', sc.pause_flag),
            ('screenshot_height', sc.screenshot_height),
            ('screenshot_width ', sc.screenshot_width),
            ('slide_base_name  ', sc.slide_base_name),
        )
        for tag, s in table:
            g.es_print(tag, s)
    #@+node:ekr.20100911044508.5635: *4* sc.make_slide_show_command & helper
    def make_slide_show_command(self, p):
        """Create slides for all slide nodes (direct children)
        of the @slideshow node p."""
        sc = self
        if not sc.inkscape_bin:
            return  # The ctor has given the warning.
        if not sc.match(p, '@slideshow'):
            g.error('Not an @slideshow node:', p.h)
            return
        after = p.nodeAfterTree()
        p = p.firstChild()
        while p and p != after:
            if g.app.commandInterruptFlag:
                return
            if sc.match(p, '@slide'):
                sc.run(p)
                p.moveToNodeAfterTree()
            elif sc.match(p, '@ignore'):
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
        sc.build()
        sc.c.redraw()
    #@+node:ekr.20100913085058.5629: *4* sc.make_slide_command
    def make_slide_command(self, p):
        sc = self
        if not sc.inkscape_bin:
            return  # The ctor has given the warning.
        if not sc.find_slideshow_node(p):
            g.error('Not in slide show:', p.h)
            return
        slide_node = sc.find_slide_node(p)
        sc.remove_built_slide_node(slide_node)
        sc.run(p)
        sc.build()
        sc.c.redraw()
        # Only the make-slide command gives this error.
        # The make-slide-show commands allows dummy nodes.
        if sc.slide_node and not sc.slide_node.b.strip():
            g.error('No body for slide')
    #@+node:ekr.20101113193341.5460: *4* sc.meld_slides_command
    def meld_slides_command(self, p):
        sc = self
        if not sc.inkscape_bin:
            return  # The ctor has given the warning.
        if not sc.find_slideshow_node(p):
            g.error('Not in slide show:', p.h)
            return
        sc.meld(p)
    #@+node:ekr.20101008112639.5628: *4* sc.build
    def build(self):
        """Do a complete sphinx build."""
        sc = self
        os.chdir(sc.slideshow_path)
        os.system('make clean')
        os.system('make html')
        # cmd = ['make','html']
        # proc = subprocess.Popen(cmd)
        # proc.communicate() # Wait
    #@+node:ekr.20100915074635.5651: *3* init
    def init(self, p):
        """Initialize from node p."""
        sc = self
        # Compute essential nodes & values.
        sc.slideshow_node = sc.find_slideshow_node(p)
        if not sc.slideshow_node:
            return False
        sc.slide_node = p = sc.find_slide_node(p)
        if not p:
            return False
        sc.slide_number = n = sc.get_slide_number(p)
        if n < 0:
            return False
        # Do nothing if p.b is empty.  This is a good flag.
        if not p.b.strip():
            return False
        # Set the verbose flag.
        sc.verbose = sc.get_verbose_flag()
        # Compute essential paths.
        sc.sphinx_path = sc.get_sphinx_path()
        if not sc.sphinx_path:
            return False
        sc.slideshow_path = sc.get_slideshow_path()
        sc.slide_base_name = sc.get_slide_base_name()
        sc.working_fn = sc.get_working_fn()
        if not sc.working_fn:
            return False
        sc.screenshot_fn = sc.get_screenshot_fn()
        if not sc.screenshot_fn:
            return False
        # Find optional nodes, all relative to the slide node.
        sc.callouts = sc.get_callouts(p)
        sc.markers = sc.get_markers(p)
        sc.screenshot_tree = sc.find_at_screenshot_node(p)
        sc.select_node = sc.find_select_node(p)
        # Compute paths and file names.
        sc.output_fn = sc.get_output_fn(p)
        sc.template_fn = sc.get_template_fn(p)
        sc.wink_path = sc.get_wink_path()
        # Compute these after computing sc.sphinx_path and sc.screenshot_fn...
        sc.at_image_fn = sc.get_at_image_fn()
        sc.directive_fn = sc.get_directive_fn()
        sc.slide_fn = sc.get_slide_fn()
        # Compute simple ivars.
        sc.screenshot_height = sc.get_screenshot_height()
        sc.screenshot_width = sc.get_screenshot_width()
        # Only an explicit pause now pauses.
        sc.edit_flag = sc.get_edit_flag(p)
        sc.pause_flag = sc.get_pause_flag(p)
        return True
    #@+node:ekr.20100908110845.5533: *3* lxml replacements
    #@+node:ekr.20100908110845.5534: *4* getElementsWithAttrib
    def getElementsWithAttrib(self, e, attr_name, aList=None):
        sc = self
        if aList is None:
            aList = []
        val = e.attrib.get(attr_name)
        if val:
            aList.append(e)
        for child in e.getchildren():
            sc.getElementsWithAttrib(child, attr_name, aList)
        return aList
    #@+node:ekr.20100908110845.5535: *4* getElementsWithAttribList (not used)
    def getElementsWithAttribList(self, e, attr_names, aList=None):
        sc = self
        if aList is None:
            aList = []
        for z in attr_names:
            if not e.attrib.get(z):
                break
        else:
            aList.append(e)
        for child in e.getchildren():
            sc.getElementsWithAttribList(child, attr_names, aList)
        return aList
    #@+node:ekr.20100908110845.5536: *4* getIds
    def getIds(self, e, d=None):
        """Return a dict d. Keys are ids, values are elements."""
        sc = self
        aList = sc.getElementsWithAttrib(e, 'id')
        return dict([(e.attrib.get('id'), e2) for e2 in aList])
    #@+node:ekr.20100908110845.5537: *4* getParents
    def getParents(self, e, d=None):
        sc = self
        if d is None:
            d = {}
            d[e] = None
        for child in e.getchildren():
            d[child] = e
            sc.getParents(child, d)
        return d
    #@+node:ekr.20100911044508.5630: *3* options & paths
    #@+node:ekr.20101004082701.5734: *4* Finding nodes
    #@+node:ekr.20101008112639.5629: *5* find_node
    def find_node(self, p, h):
        """Return the node in p's direct children whose headline matches h."""
        for p2 in p.children():
            if g.match_word(p2.h, 0, h):
                return p2
        return None
    #@+node:ekr.20100909121239.5742: *5* find_at_screenshot_node
    def find_at_screenshot_node(self, p):
        """Return the @screenshot node in a direct child of p."""
        return self.find_node(p, '@screenshot')
    #@+node:ekr.20100913085058.5660: *5* find_select_node
    def find_select_node(self, p):
        """
        Find the @select node in a direct child of p.
        Return whatever follows @select in the headline.
        """
        sc = self
        tag = '@select'
        p2 = sc.find_node(p, tag)
        return p2.h[len(tag) :].strip() if p2 else ''
    #@+node:ekr.20100915074635.5652: *5* find_slide_node
    def find_slide_node(self, p):
        """Return the @slide node at or near p."""
        sc = self
        p1 = p.copy()
        if sc.match(p, '@slide'):
            return p
        # Look up the tree.
        for parent in p.self_and_parents():
            if sc.match(parent, '@slide'):
                return parent
            if sc.match(parent, '@slideshow'):
                break
        # Look down the tree.
        p = p.firstChild()
        while p:
            if sc.match(p, '@slide'):
                return p
            if sc.match(p, '@slideshow'):
                break
            else:
                p.moveToThreadNext()
        g.trace('No @slide node found:', p1.h)
        return None
    #@+node:ekr.20100913085058.5654: *5* find_slideshow_node
    def find_slideshow_node(self, p):
        """Return the nearest ancestor @slideshow node."""
        # sc = self
        for p2 in p.self_and_parents():
            if g.match_word(p2.h, 0, '@slideshow'):
                return p2
        return None
    #@+node:ekr.20101004082701.5735: *4* Path utils
    #@+node:ekr.20100908110845.5540: *5* finalize
    def finalize(self, fn):
        """Return the absolute path to fn in the slideshow folder."""
        sc = self
        return sc.fix(g.finalize_join(sc.slideshow_path, fn))
    #@+node:ekr.20100911044508.5632: *5* fix
    def fix(self, fn):
        """Fix the case of a file name,
        especially on Windows the case of drive letters.

        This method is safe to call at any time:
        it changes only case and slashes.
        """
        return os.path.normcase(fn).replace('\\', '/')
    #@+node:ekr.20100913085058.5658: *5* sanitize
    def sanitize(self, fn):
        return g.sanitize_filename(fn.lower()).replace('.', '-').replace('_', '-')
    #@+node:ekr.20101004082701.5736: *4* Computed paths
    # These methods compute final paths.
    #@+node:ekr.20100911044508.5631: *5* get_at_image_fn
    def get_at_image_fn(self):
        """Return sc.output_fn name **relative to g.app.loadDir**.

        @image directives are relative to g.app.loadDir.
        """
        sc = self
        base = sc.fix(g.finalize(g.app.loadDir))
        fn = sc.fix(sc.output_fn)
        fn = os.path.relpath(fn, base)
        fn = sc.fix(fn)
        return fn
    #@+node:ekr.20100909121239.5669: *5* get_directive_fn
    def get_directive_fn(self):
        """Compute the path for use in an .. image:: directive."""
        sc = self
        return g.shortFileName(sc.output_fn)
    #@+node:ekr.20100911044508.5627: *5* get_output_fn
    def get_output_fn(self, p):
        """
        Return the full, absolute, output file name.

        An empty filename disables output.

        The default is 'slide-%03d.png' % (sc.slide_number)
        """
        # Look for any @output nodes in p's children.
        sc = self
        tag = '@output'
        for child in p.children():
            h = child.h
            if g.match_word(h, 0, tag):
                fn = h[len(tag) :].strip()
                if fn:
                    fn = sc.finalize(fn)
                else:
                    fn = None
        fn = 'slide-%03d.png' % (sc.slide_number)
        fn = sc.finalize(fn)
        return fn
    #@+node:ekr.20100911044508.5628: *5* get_screenshot_fn
    def get_screenshot_fn(self):
        """Return the full, absolute, screenshot file name."""
        sc = self
        # fn = '%s-%03d.png' % (sc.slide_base_name,sc.slide_number)
        fn = 'screenshot-%03d.png' % (sc.slide_number)
        fn = sc.finalize(fn)
        return fn
    #@+node:ekr.20101004082701.5738: *5* get_slide_base_name
    def get_slide_base_name(self):
        sc = self
        junk, name = g.os_path_split(sc.slideshow_path)
        return name
    #@+node:ekr.20101004082701.5740: *5* get_slide_fn
    def get_slide_fn(self):
        """Return the absolute path to 'slide-%03d.html.txt' % (sc.slide_number)."""
        sc = self
        # fn = '%s-%03d.html.txt' % (sc.slide_base_name,sc.slide_number)
        fn = 'slide-%03d.html.txt' % (sc.slide_number)
        fn = sc.finalize(fn)
        return fn
    #@+node:ekr.20100919075719.5641: *5* get_slideshow_path
    def get_slideshow_path(self):
        """
        Return the path to the folder to be used for slides and screenshots.
        This is sphinx_path/slides/<sanitized-p.h>
        """
        sc = self
        p = sc.slideshow_node
        h = p.h
        tag = '@slideshow'
        assert g.match_word(h, 0, tag)
        h = h[len(tag) :].strip()
        if h:
            theDir = sc.sanitize(h)
            path = sc.fix(g.finalize_join(sc.sphinx_path, 'slides', theDir))
            return path
        g.error('@slideshow node has no name')
        return None
    #@+node:ekr.20100911044508.5633: *5* get_sphinx_path
    def get_sphinx_path(self):
        """Return the full, absolute, path to the sphinx directory.

        By default this will be the leo/doc/html directory.

        If a relative path is given, it will resolved
        relative to the directory containing the .leo file.

        This path will contain the slides directory, and the following files:
        'conf.py','Leo4-80-border.jpg','Makefile','make.bat',
        """
        sc = self
        c = sc.c
        sphinx_path = sc.get_option('sphinx_path')
        if sphinx_path:
            if g.os_path_isabs(sphinx_path):
                path = sphinx_path
            else:
                # The path is relative to the .leo file
                leo_fn = c.fileName()
                if not leo_fn:
                    g.error('relative sphinx path given but outline not named')
                    return None
                leo_fn = g.finalize_join(g.app.loadDir, leo_fn)
                base, junk = g.os_path_split(leo_fn)
                path = g.finalize_join(base, sphinx_path)
        else:
            # The default is the leo/doc/html directory.
            path = g.finalize_join(g.app.loadDir, '..', 'doc', 'html')
        path = sc.fix(path)
        return path
    #@+node:ekr.20100908110845.5542: *5* get_template_fn
    def get_template_fn(self, p):
        """Return the full, absolute, template file name."""
        sc = self
        # c = sc.c
        template_fn = sc.get_option('template_fn')
        if template_fn:
            fn = sc.fix(g.finalize(template_fn))
        else:
            fn = sc.fix(g.finalize_join(g.app.loadDir, '..', 'doc', 'inkscape-template.svg'))
        if g.os_path_exists(fn):
            return fn
        g.error('template file not found:', fn)
        return None
    #@+node:ekr.20100911044508.5626: *5* get_working_fn
    def get_working_fn(self):
        """Return the full, absolute, name of the working file."""
        sc = self
        # fn = '%s-%03d.svg' % (sc.slide_base_name,sc.slide_number)
        fn = 'screenshot-%03d.svg' % (sc.slide_number)
        fn = sc.finalize(fn)
        return fn
    #@+node:ekr.20101113193341.5461: *5* get_wink_path
    def get_wink_path(self):
        """Return the full, absolute, path to the directory containing wink
        screenshots. If a relative path is given, it will resolved relative to
        the directory containing the .leo file.
        """
        sc = self
        c = sc.c
        tag = '@wink_path'
        for p in sc.slideshow_node.children():
            if sc.match(p, tag):
                path = p.h[len(tag) :].strip()
                if path.startswith('='):
                    path = path[1:].strip()
                break
        else:
            return None
        if g.os_path_isabs(path):
            return path
        # The path is relative to the .leo file
        leo_fn = c.fileName()
        if not leo_fn:
            g.error('relative wink path given but outline not named')
            return None
        leo_fn = g.finalize_join(g.app.loadDir, leo_fn)
        base, junk = g.os_path_split(leo_fn)
        path = g.finalize_join(base, path)
        path = sc.fix(path)
        g.trace(path)
        return path
    #@+node:ekr.20101004082701.5737: *4* Options
    # These methods examine the children/descendants of a node for options nodes.
    #@+node:ekr.20100908110845.5596: *5* get_callouts & helper
    def get_callouts(self, p):
        """Return the list of callouts from the
        direct children that are @callout nodes."""
        sc = self
        aList = []
        for child in p.children():
            if g.match_word(child.h, 0, '@callout'):
                callout = sc.get_callout(child)
                if callout:
                    aList.append(callout)
        return aList
    #@+node:ekr.20100909121239.6096: *6* get_callout
    def get_callout(self, p):
        """Return the text of the callout at p."""
        if p.b.strip():
            return p.b
        s = p.h
        assert g.match_word(s, 0, '@callout')
        i = g.skip_id(s, 0, chars='@')  # Match @callout or @callouts, etc.
        s = s[i:].strip()
        return s
    #@+node:ekr.20100911044508.5620: *5* get_edit_flag
    def get_edit_flag(self, p):
        """Return True if any of p's children is an @edit node."""
        sc = self
        return bool(sc.find_node(p, '@edit'))
    #@+node:ekr.20100908110845.5597: *5* get_markers & helper
    def get_markers(self, p):
        """Return the list of markers from all @marker nodes."""
        sc = self
        aList = []
        for child in p.children():
            if (
                g.match_word(child.h, 0, '@marker') or
                g.match_word(child.h, 0, '@markers')
            ):
                callout = sc.get_marker(child)
                if callout:
                    aList.extend(callout)
        return aList
    #@+node:ekr.20100909121239.6097: *6* get_marker
    def get_marker(self, p):
        """Return a list of markers at p."""
        s = p.h
        assert g.match_word(s, 0, '@markers') or g.match_word(s, 0, 'marker')
        i = g.skip_id(s, 0, chars='@')
        s = s[i:].strip()
        return [z.strip() for z in s.split(',')]
    #@+node:ekr.20101006060338.5703: *5* get_option
    def get_option(self, option):
        """Get a local or global option.
        Global options are children of the @slideshow node.
        Local options are children of the p, the @slide node."""
        sc = self
        assert hasattr(sc, option)
        tag = '@' + option
        isPath = tag.endswith('_fn') or tag.endswith('_path')
        for p in (sc.slideshow_node, sc.slide_node):
            for child in p.children():
                h = child.h
                if g.match_word(h, 0, tag):
                    val = h[len(tag) :].strip()
                    if val.startswith('='):
                        val = val[1:].strip()
                    if val:
                        if isPath:
                            val = sc.finalize(val)
                        elif val in ('1', 'True', 'true'):
                            val = True
                        elif val in ('0', 'False', 'false'):
                            val = False
                        elif val.isdigit():
                            val = int(val)
                        elif not val:
                            g.warning('ignoring setting', child.h)
                        return val
                    g.warning('ignoring setting:', child.h)
                    return None
        return None
    #@+node:ekr.20100913085058.5630: *5* get_pause_flag
    def get_pause_flag(self, p):
        # Look for an @pause nodes in p's children.
        for child in p.children():
            if g.match_word(child.h, 0, '@pause'):
                return True
        return False
    #@+node:ekr.20100913085058.5628: *5* get_protect_flag
    def get_protect_flag(self, p):
        # Look for any @protect or @ignore nodes in p's children.
        for child in p.children():
            if g.match_word(p.h, 0, '@ignore') or g.match_word(p.h, 0, '@protect'):
                return True
        return False
    #@+node:ekr.20101006060338.5704: *5* get_screenshot_height/width
    def get_screenshot_height(self):
        sc = self
        h = sc.get_option('screenshot_height')
        return sc.default_screenshot_height if h is None else h

    def get_screenshot_width(self):
        sc = self
        w = sc.get_option('screenshot_width')
        return sc.default_screenshot_width if w is None else w
    #@+node:ekr.20101009162803.5632: *5* get_slide_title
    def get_slide_title(self):
        sc = self
        slideshow_name = sc.slideshow_node.h[len('@slideshow') :].strip()
        slide_name = sc.slide_node.h[len('@slide') :].strip()
        d = {
            'slideshow_name': slideshow_name,
            'slide_name': slide_name,
            'slide_number': sc.slide_number,
        }
        for tag in ('title', 'title_pattern'):
            s = sc.get_option(tag)
            if s:
                if tag == '@title':
                    return s
                try:
                    return s % d
                except Exception:
                    g.warning('bad %s' % repr(self.c.p.h))
        if slide_name and not slide_name.strip().startswith('(('):
            return slide_name
        s = sc.default_slide_pattern % d
        return s
    #@+node:ekr.20101006060338.5706: *5* get_verbose_flag
    def get_verbose_flag(self):
        sc = self
        val = sc.get_option('verbose')
        return sc.default_verbose_flag if val is None else val
    #@+node:ekr.20100911044508.5618: *3* utilities
    #@+node:ekr.20100911044508.5637: *4* clear_cache
    def clear_cache(self):
        """Clear the dimension cache."""
        sc = self
        sc.dimCache = {}
        sc.is_reads, sc.is_cache = 0, 0
    #@+node:ekr.20101005193146.5687: *4* copy_files & helper
    #@+at We would like to do sphinx "make" operations only in the top-level sphinx
    # folder (leo/doc/html) so that only a single _build directory tree would exist.
    #
    # Alas, that doesn't work.  To get links correct, the build must be done in
    # the individual slide folders.  So we *must* copy all the files.
    #@@c

    def copy_files(self):
        sc = self
        sc.make_toc()
        table = (
            'conf.py',
            # 'leo_toc.html.txt', # created by make_toc above.
            'Leo4-80-border.jpg',
            'Makefile',
            'make.bat',
        )
        slide_path, junk = g.os_path_split(sc.slide_fn)
        for fn in table:
            path = g.finalize_join(slide_path, fn)
            if not g.os_path_exists(path):
                sc.copy_file(sc.sphinx_path, slide_path, fn)
    #@+node:ekr.20101005193146.5688: *5* copy_file
    def copy_file(self, src_path, dst_path, fn):
        src_fn = g.finalize_join(src_path, fn)
        dst_fn = g.finalize_join(dst_path, fn)
        junk, dst_dir = g.os_path_split(dst_path)
        g.note('creating', g.os_path_join('slides', dst_dir, fn))
        shutil.copyfile(src_fn, dst_fn)
    #@+node:ekr.20100913085058.5653: *4* get_slide_number
    def get_slide_number(self, p):
        sc = self
        assert sc.slideshow_node
        assert p == sc.slide_node
        n = 1  # Slides numbers start at one.
        p1 = p.copy()
        p = sc.slideshow_node.firstChild()
        while p:
            if p == p1:
                return n
            if g.match_word(p.h, 0, '@slide'):
                n += 1
                # Skip the entire tree, including
                # any inner @screenshot trees.
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
        g.trace('Can not happen. Not found:', p.h)
        return -666
    #@+node:ekr.20100908110845.5543: *4* give_pil_warning
    pil_message_given = False

    def give_pil_warning(self):
        """Give a singleton warning that PIL could not be loaded."""
        sc = self
        if sc.pil_message_given:
            return  # Warning already given.
        if Image and ImageChops:
            return  # The best situation
        sc.pil_message_given = True
        g.warning('PIL not found: images may have transparent borders')
        print('pip install pillow')
    #@+node:ekr.20100908110845.5592: *4* in_slide_show
    def in_slide_show(self, p):
        """Return True if p is a descendant of an @slideshow node."""
        sc = self
        return bool(sc.find_slideshow_node(p))
    #@+node:ekr.20101004201006.5685: *4* make_all_directories
    def make_all_directories(self):
        sc = self
        # Don't create path for at_image_fn or directive_fn
        # They are relative paths!
        static_dir = g.finalize_join(
            sc.slideshow_path, '_static')
        table = (
            # ('at_image_fn   ',sc.at_image_fn),
            ('output_fn     ', sc.output_fn),
            ('screenshot_fn ', sc.screenshot_fn),
            ('sphinx_path   ', sc.sphinx_path),
            ('slide_fn      ', sc.slide_fn),
            ('slideshow_path', sc.slideshow_path),
            ('template_fn   ', sc.template_fn),
            ('working_fn    ', sc.working_fn),
            ('_static       ', static_dir),
        )
        for tag, path in table:
            if tag.strip().endswith('fn'):
                path, junk = g.os_path_split(path)
            if not g.os_path_exists(path):
                g.trace(tag, path)
                g.makeAllNonExistentDirectories(path)
    #@+node:ekr.20101008112639.5625: *4* make_at_url_node_for_built_slide
    def make_at_url_node_for_built_slide(self):
        """Create an @url node for built slide."""
        sc = self
        c = sc.c
        p = sc.slide_node
        h = '@url built slide'
        if not sc.find_node(p, h):
            c.selectPosition(p)
            junk, fn = g.os_path_split(sc.slide_fn)
            if fn.endswith('.txt'):
                fn = fn[:-4]
            p2 = p.insertAsLastChild()
            p2.h = h
            p2.b = g.finalize_join(
                sc.slideshow_path, '_build', 'html', fn)
    #@+node:ekr.20101008112639.5631: *4* make_at_url_node_for_output_file
    def make_at_url_node_for_output_file(self):
        """Create an @url node for the final output file."""
        sc = self
        c = sc.c
        p = sc.slide_node
        h = '@url final output file'
        if not sc.find_node(p, h):
            c.selectPosition(p)
            p2 = p.insertAsLastChild()
            p2.h = h
            p2.b = sc.output_fn
    #@+node:ekr.20101008112639.5627: *4* make_at_url_node_for_screenshot
    def make_at_url_node_for_screenshot(self):
        """Create an @url node for the screenshot file."""
        sc = self
        c = sc.c
        p = sc.slide_node
        h = '@url screenshot'
        if not sc.find_node(p, h):
            c.selectPosition(p)
            p2 = p.insertAsLastChild()
            p2.h = h
            p2.b = sc.screenshot_fn
    #@+node:ekr.20101008112639.5624: *4* make_at_url_node_for_working_file
    def make_at_url_node_for_working_file(self):
        """Create an @url node for the working file."""
        sc = self
        c = sc.c
        p = sc.slide_node
        h = '@url working file'
        if not sc.find_node(p, h):
            c.selectPosition(p)
            p2 = p.insertAsLastChild()
            p2.h = h
            p2.b = sc.working_fn
    #@+node:ekr.20100908110845.5599: *4* make_image_node (not used)
    # def make_image_node (self):
        # """Create an @image node as the first child of sc.slide_node."""
        # sc = self ; c = sc.c ; p = sc.slide_node
        # h = '@image %s' % sc.at_image_fn
        # # Create the node if it doesn't exist.
        # for child in p.children():
            # if child.h == h:
                # # print('already exists: %s' % h)
                # break
        # else:
            # c.selectPosition(p)
            # p2 = p.insertAsNthChild(0)
            # p2.h = h
    #@+node:ekr.20101006060338.5698: *4* make_toc
    def make_toc(self):
        sc = self
        #@+<< define toc_body >>
        #@+node:ekr.20101006060338.5699: *5* << define toc_body >>
        h = sc.slideshow_node.h[len('@slideshow') :].strip()
        title = sc.underline(h.title())
        s = '''\
        %s

        Contents:

        .. toctree::
           :maxdepth: 1
           :glob:

           slide-*
        ''' % (title)  #,sc.slide_base_name)
        # Indices and tables
        # ==================
        # * :ref:`genindex`
        # * :ref:`search`
        toc_body = textwrap.dedent(s)
        #@-<< define toc_body >>
        fn = sc.finalize('leo_toc.html.txt')
        if g.os_path_exists(fn):
            return
        try:
            f = open(fn, 'w')
            f.write(toc_body)
            f.close()
            if sc.verbose:
                g.note('wrote:', g.shortFileName(fn))
        except Exception:
            g.error('writing', fn)
            g.es_exception()
    #@+node:ekr.20101113193341.5446: *4* match
    def match(self, p, pattern):
        """Return True if p.h matches the pattern."""
        return g.match_word(p.h, 0, pattern)
    #@+node:ekr.20100911044508.5636: *4* open_inkscape_with_list (not used)
    # def open_inkscape_with_list (self,aList):
        # """Open inkscape with a list of file."""
        # sc = self
        # cmd = [sc.inkscape_bin,"--with-gui"]
        # cmd.extend(aList)
        # proc = subprocess.Popen(cmd, stderr=subprocess.PIPE)
        # proc.communicate() # Wait for Inkscape to terminate.
    #@+node:ekr.20101021065622.5633: *4* remove_built_slide_node
    def remove_built_slide_node(self, p):
        sc = self
        c = sc.c
        changed = 0
        for child in p.children():
            if g.match_word(child.h, 0, '@url built slide'):
                child.doDelete()
                changed += 1
        if changed:
            c.redraw()
    #@+node:ekr.20100909193826.5600: *4* select_at_image_node (not used)
    # def select_at_image_node (self,p):
        # """Select the @image node in one of p's direct children."""
        # sc = self ; c = sc.c
        # for child in p.children():
            # if g.match_word(child.h,0,'@image'):
                # c.selectPosition(child)
                # c.redraw(child)
                # break
        # else:
            # c.selectPosition(p)
            # c.redraw(p)
    #@+node:ekr.20101005193146.5690: *4* underline
    def underline(self, s):
        """Return s overlined and underlined with '=' characters."""
        # Write longer underlines for non-ascii characters.
        n = max(4, len(g.toEncodedString(s, encoding='utf-8', reportErrors=False)))
        ch = '='
        return '%s\n%s\n%s\n\n' % (ch * n, s, ch * n)
        # return '%s\n%s\n' % (s,ch*n)
    #@+node:ekr.20100911044508.5616: *3* sc.run & helpers
    def run(self, p):
        """
        Create a slide from node p.
        Call Inkscape to edit the slide if requested.
        """
        sc = self
        # c = sc.c
        if not sc.init(p):
            return
        # Make directories and copy the sphinx build files into them.
        sc.make_all_directories()
        sc.copy_files()
        # "@url built slide" inhibits everything.
        if sc.find_node(sc.slide_node, '@url built slide'):
            g.blue('exists: @url built slide in %s' % (p.h))
            return
        sc.make_slide()
        # "@url final output file" inhibits everything except the build.
        if sc.find_node(sc.slide_node, '@url final output file'):
            sc.make_at_url_node_for_built_slide()
            g.blue('exists: @url final output file %s' % (p.h))
            return
        # Do only a build if there is no @screenshot tree.
        if not sc.screenshot_tree:
            sc.make_at_url_node_for_built_slide()
            return  # Don't take any screenshot!
        # '@url screenshot' inhibits taking the screenshot.
        if not sc.find_node(sc.slide_node, '@url screenshot'):
            if sc.take_screen_shot():
                sc.make_at_url_node_for_screenshot()
            else:
                g.error('can not make screen shot:', p.h)
                sc.make_at_url_node_for_built_slide()
                return
        # "@url working file" inhibits making a new working file.
        if sc.find_node(sc.slide_node, '@url working file'):
            # Make a new output file *only* if the working file is newer.
            if (
                g.os_path_exists(sc.working_fn) and
                sc.output_fn and
                os.path.getmtime(sc.working_fn) >
                os.path.getmtime(sc.output_fn)
            ):
                sc.make_output_file()
            else:
                # Make sure this has been made.
                sc.make_at_url_node_for_output_file()
        else:
            # Make the working file and output file
            sc.make_working_file()
            if sc.edit_flag:
                sc.edit_working_file()
            sc.make_output_file()
        # Build slide after creating the output file ;-)
        sc.make_at_url_node_for_built_slide()
    #@+node:ekr.20100908110845.5552: *4* edit_working_file & helper
    def edit_working_file(self):
        """Invoke Inkscape on the working file."""
        sc = self
        g.red('Opening Inkscape...\n')
        sc.c.outerUpdate()
        sc.enable_filters(sc.working_fn, False)
        cmd = [sc.inkscape_bin, "--with-gui", sc.working_fn]
        proc = subprocess.Popen(cmd, stderr=subprocess.PIPE)
        proc.communicate()  # Wait for Inkscape to terminate.
        sc.enable_filters(sc.working_fn, True)
    #@+node:ekr.20100908110845.5553: *5* enable_filters
    def enable_filters(self, svgfile, enable):
        """Disable/enable filters in SVG at the XML level

        The drop-shadow filter on several objects kills editing performance
        in inkscape, so this turns them on/off in the XML.  There's a GUI
        operation to turn them off in inkscape, but it's a pain to have to
        keep using it.

        Disabling copys the real @style to @__style and changes
        "filter:url" to "_filter:url" in the active @style, while
        enabling just copys @__style to @style and deletes @__style.
        """
        sc = self
        doc = etree.parse(svgfile)
        root = doc.getroot()
        if enable:
            # copy @__style to @style and deletes @__style.
            aList = sc.getElementsWithAttrib(root, '__style')
            for i in aList:
                i.set("style", i.get("__style"))
                del i.attrib['__style']
        else:
            aList3 = sc.getElementsWithAttrib(root, 'style')
            aList = [z for z in aList3
                if z.attrib.get('style').find('filter:url(') > -1]
            # copy the real @style to @__style and
            # changes "filter:url" to "_filter:url" in the active @style
            for i in aList:
                i.set("__style", i.get("style"))
                i.set("style", i.get("style").replace(
                    'filter:url(', '_filter:url('))
        doc.write(open(svgfile, 'w'))
    #@+node:ekr.20100908110845.5554: *4* make_output_file & helper
    def make_output_file(self):
        """Create the output file from the working file."""
        sc = self
        if not sc.output_fn:
            if sc.verbose:
                g.note('no output file')
            return
        cmd = (
            sc.inkscape_bin,
            "--without-gui",
            "--export-png=" + sc.output_fn,
            "--export-area-drawing",
            "--export-area-snap",
            sc.working_fn)
        proc = subprocess.Popen(cmd, stderr=subprocess.PIPE)
        proc.communicate()  # Wait for Inkscape to terminate.
        if sc.verbose:
            g.note('wrote:  %s' % g.shortFileName(sc.output_fn))
        if Image:  # trim transparent border
            try:
                img = Image.open(sc.output_fn)
                img = sc.trim(img, (255, 255, 255, 0))
                img.save(sc.output_fn)
            except IOError:
                g.trace('can not open %s' % sc.output_fn)
        sc.make_at_url_node_for_output_file()
    #@+node:ekr.20100908110845.5555: *5* trim
    def trim(self, im, border):
        if Image and ImageChops:
            bg = Image.new(im.mode, im.size, border)
            diff = ImageChops.difference(im, bg)
            bbox = diff.getbbox()
            if bbox:
                return im.crop(bbox)
            # found no content
            raise ValueError("cannot trim; image was empty")
        return None
    #@+node:ekr.20101004082701.5739: *4* make_slide & helpers
    #  Don't call rstCommands.writeToDocutils--we are using sphinx!

    def make_slide(self):
        """Write sc.slide_node.b to <sc.slide_fn>, a .html.txt file."""
        sc = self
        fn = sc.slide_fn
        s = sc.make_slide_contents()
        try:
            f = open(fn, 'w')
            f.write(s)
            f.close()
            if sc.verbose:
                g.note('wrote: ', g.shortFileName(fn))
        except Exception:
            g.error('writing:', fn)
            g.es_exception()
    #@+node:ekr.20101005193146.5689: *5* make_slide_contents
    def make_slide_contents(self):
        sc = self
        # n = sc.slide_number
        h = sc.get_slide_title()
        body = sc.slide_node.b
        # 2010/11/21: Don't use h.title(): it can produce bad results.
        # title = sc.underline(h.title())
        title = sc.underline(h)
        return '%s\n%s' % (title, body)
    #@+node:ekr.20101006060338.5702: *4* make_working_file & helpers
    def make_working_file(self):
        sc = self
        sc.give_pil_warning()
        # Create the working file from the template.
        template = sc.make_dom()
        if template:
            sc.make_working_file_from_template(template)
            sc.make_at_url_node_for_working_file()
        else:
            g.error('can not make template from:', sc.template_fn)
        return bool(template)
    #@+node:ekr.20100908110845.5546: *5* make_dom & helpers
    def make_dom(self):
        """Create the template dom object."""
        sc = self
        template = sc.get_template()
        if not template:
            return None
        root = template.getroot()
        ids_d = sc.getIds(root)
        parents_d = sc.getParents(root)
        # make a dict of the groups we're going to manipulate
        part = dict([(z, ids_d.get(z))
            for z in ('co_g_co', 'co_g_bc_1', 'co_g_bc_2')])
        # note where we should place modified copies
        part_parent = parents_d.get(part.get('co_g_co'))
        # remove them from the document
        for i in part.values():
            parents_d = sc.getParents(root)
            parent = parents_d.get(i)
            parent.remove(i)
        for n, callout in enumerate(sc.callouts):
            z = copy.deepcopy(part['co_g_co'])
            ids_d = sc.getIds(z)
            text = ids_d.get('co_text_holder')
            text.text = callout
            # need distinct IDs on frames/text for sizing
            frame = ids_d.get('co_frame')
            sc.clear_id(z)  # let inkscape pick new IDs for other elements
            # A) it's the flowRoot, not the flowPara, which carries the size info
            # B) Inkscape trashes the IDs on flowParas on load!
            parents_d = sc.getParents(z)
            parent = parents_d.get(text)
            parent.set('id', 'co_text_%d' % n)
            frame.set('id', 'co_frame_%d' % n)
            # offset so user can see them all
            sc.move_element(z, 20 * n, 20 * n)
            part_parent.append(z)
        for n, number in enumerate(sc.markers):
            if len(str(number)) == 2:
                use_g, use_t = 'co_g_bc_2', 'co_bc_text_2'
            else:
                use_g, use_t = 'co_g_bc_1', 'co_bc_text_1'
            z = copy.deepcopy(part[use_g])
            ids_d = sc.getIds(z)
            bc_text = ids_d.get(use_t)
            bc_text.text = str(number)
            sc.move_element(z, 20 * n, 20 * n)
            part_parent.append(z)
        # point to the right screen shot
        ids_d = sc.getIds(template.getroot())
        img_element = ids_d.get('co_shot')
        img_element.set(sc.xlink + 'href', sc.screenshot_fn)
        # adjust screen shot dimensions
        if Image:
            img = Image.open(sc.screenshot_fn)
            img_element.set('width', str(img.size[0]))
            img_element.set('height', str(img.size[1]))
        # write temp file to get size info
        fh, fp = tempfile.mkstemp()
        os.close(fh)
        template.write(fp)
        # could reload file at this point to reflect offsets etc.
        # but don't need to because of relative position mode in paths
        # resize things to fit text
        for n, callout in enumerate(sc.callouts):
            sc.resize_curve_box(fp, template, n)
        os.unlink(fp)
        return template
    #@+node:ekr.20100908110845.5547: *6* clear_id
    def clear_id(self, x):
        """Recursively clear @id on element x and descendants."""
        sc = self
        if 'id' in x.keys():
            del x.attrib['id']
        ids_d = sc.getIds(x)
        objects = set(list(ids_d.values()))
        for z in objects:
            del z.attrib['id']
        return x
    #@+node:ekr.20100908110845.5548: *6* get_template
    def get_template(self):
        """Load and check the template SVG and return DOM"""
        sc = self
        infile = open(sc.template_fn)
        template = etree.parse(infile)
        ids_d = sc.getIds(template.getroot())
        # check all IDs we expect are present
        ids = list(ids_d.keys())
        if set(sc.ids) <= set(ids):
            return template
        g.error('template did not include all required IDs:', sc.template_fn)
        return None
    #@+node:ekr.20100908110845.5549: *6* move_element
    def move_element(self, element, x, y):
        if not element.get('transform'):
            element.set('transform', "translate(%f,%f)" % (x, y))
        else:
            ox, oy = element.get('transform').split(',')
            ox = ox.split('(')[1]
            oy = oy.split(')')[0]
            element.set('transform', "translate(%f,%f)" %
                (float(ox) + x, float(oy) + y))
    #@+node:ekr.20100908110845.5550: *6* resize_curve_box & helper
    def resize_curve_box(self, fn, template, n):
        sc = self
        d = sc.getIds(template.getroot())
        text = d.get('co_text_%d' % (n))
        frame = d.get('co_frame_%d' % (n))
        text_id = text.get('id')
        # frame_id = frame.get('id')
        pnts = frame.get('d').split()
        i = 0
        while i < len(pnts):
            if ',' not in pnts[i]:
                type_ = pnts[i]
                del pnts[i]
            else:
                pnts[i] = [float(j) for j in pnts[i].split(',')]
                pnts[i].insert(0, type_)
                if type_ == 'm':
                    type_ = 'l'
                i += 1
        # kludge for now
        h0 = 12  # index of vertical component going down right side
        h1 = -4  # index of vertical component coming up left side
        min_ = 0  # must leave this many
        present = 5  # components present initially
        h = pnts[h0][2]  # height of one component
        th = sc.get_dim(fn, text_id, 'height')  # text height
        if not th:
            g.trace('no th')
        while present > min_ and present * h + 15 > th:
            del pnts[h0]
            del pnts[h1]
            present -= 1
        last = ''
        d = []
        for p in pnts:
            if last != p[0]:
                last = p[0]
                if last == 'm':
                    last = 'l'
                d.append(p[0])
            d.append("%s,%s" % (p[1], p[2]))
        d.append('z')
        frame.set('d', ' '.join(d))
    #@+node:ekr.20100908110845.5551: *7* get_dim
    def get_dim(self, fn, Id, what):
        """return dimension of element in fn with @id Id, what is
        x, y, width, or height
        """
        sc = self
        hsh = fn + Id + what
        if hsh in sc.dimCache:
            sc.is_cache += 1
            return sc.dimCache[hsh]
        cmd = [sc.inkscape_bin, '--without-gui', '--query-all', fn]
        proc = subprocess.Popen(cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        # make new pipe for stderr to supress chatter from inkscape.
        stdout, stderr = proc.communicate()  # Wait for Inkscape to terminate.
        s = str(stdout).strip()
        # Necessary for Python 3k.
        if s.startswith("b'"):
            s = s[2:]
        if s.endswith("'"):
            s = s[:-1]
        aList = s.replace('\\r', '').replace('\\n', '\n').split('\n')
        for line in aList:
            if not line.strip():
                continue
            id_, x, y, w, h = line.split(',')
            for part in ('x', x), ('y', y), ('width', w), ('height', h):
                hsh2 = fn + id_ + part[0]
                sc.dimCache[hsh2] = float(part[1])
        sc.is_reads += 1
        assert sc.dimCache.get(hsh)
        return sc.dimCache.get(hsh)
    #@+node:ekr.20100908110845.5545: *5* make_working_file_from_template
    def make_working_file_from_template(self, template):
        """Create the working file from the template."""
        sc = self
        fn = sc.working_fn
        outfile = open(fn, 'w')
        template.write(outfile)
        if sc.verbose:
            g.note('wrote: ', g.shortFileName(fn))
        outfile.close()
    #@+node:ekr.20100909121239.6117: *4* take_screen_shot & helpers
    def take_screen_shot(self):
        """Take the screen shot, create an @image node,
        and add an .. image:: directive to p."""
        sc = self
        # p = sc.slide_node
        # Always create 'screenshot-setup.leo'
        fn = sc.create_setup_leo_file()
        # Always open fn in a separate process.
        ok = sc.setup_screen_shot(fn)
        if ok:
            if sc.verbose:
                g.note('wrote:  %s' % g.shortFileName(sc.screenshot_fn))
                # g.note('slide node:  %s' % p.h)
            sc.add_image_directive()
        return ok
    #@+node:ekr.20100914090933.5643: *5* create_setup_leo_file
    def create_setup_leo_file(self):
        """
        Create an ouline containing all children of sc.screenshot_tree.
        Do not copy @slide nodes or @slideshow nodes.
        """
        sc = self
        fn = sc.finalize('screenshot-setup.leo')
        c = g.app.newCommander(fn)

        def isSlide(p):
            return g.match_word(p.h, 0, '@slide') or g.match_word(p.h, 0, '@slideshow')

        c.frame.createFirstTreeNode()
        root = c.rootPosition()
        # Remember the expanded nodes.
        expanded = [z.copy() for z in sc.screenshot_tree.subtree() if z.isExpanded()]
        if sc.screenshot_tree:
            # Copy all descendants of the @screenshot node.
            children = [z.copy() for z in sc.screenshot_tree.children() if not isSlide(z)]
            if not children:
                return g.error('empty @screenshot tree')
        else:
            return g.error('can not happen. no screenshot tree')
        child1 = children[0]
        child1.copyTreeFromSelfTo(root)
        last = root
        for child in children[1:]:
            child2 = last.insertAfter()
            child.copyTreeFromSelfTo(child2)
            last = child2
        # Set the expanded bits in the new file.
        for z in c.all_unique_positions():
            for z2 in expanded:
                if z2.h == z.h:
                    z.expand()
        # Save the file silently.
        c.fileCommands.save(fn)
        # pylint: disable=no-member
            # c.close does exist.
        c.close()
        return fn
    #@+node:ekr.20100913085058.5659: *5* setup_screen_shot & helpers
    def setup_screen_shot(self, fn):
        """Take the screen shot after adjusting the window and outline."""
        sc = self
        # Important: we must *not* have the clipboard open here!
        # Doing so can hang if the user does a clipboard operation
        # in a subprocess.
        if 0:
            cb = g.app.gui.qtApp.clipboard()
            if cb:
                cb.clear(cb.Clipboard)  # Does not work anyway.
        ok = sc.open_screenshot_app(fn)
        if ok and sc.pause_flag:
            ok = sc.save_clipboard_to_screenshot_file()
        return ok
    #@+node:ekr.20100913085058.5656: *6* open_screenshot_app
    def open_screenshot_app(self, leo_fn):
        """Open the screenshot app.
        Return True if the app exists and can be opened."""
        verbose = False
        sc = self
        c = sc.c
        launch = g.finalize_join(g.app.loadDir, '..', '..', 'launchLeo.py')
        python = sys.executable
        h, w = sc.screenshot_height, sc.screenshot_width
        cmd = [python, launch, '--window-size=%sx%s' % (h, w)]
        if sc.select_node:
            cmd.append('--select="%s"' % (sc.select_node))
        if sc.pause_flag:
            g.red('Pausing:', g.shortFileName(sc.screenshot_fn))
            g.note('Please take the screenshot by hand')
            c.outerUpdate()
        else:
            cmd.append('--screen-shot="%s"' % sc.screenshot_fn)
        cmd.append('--file="%s"' % (leo_fn))
        if verbose:
            proc = subprocess.Popen(cmd)
        else:
            # Eat the output.
            proc = subprocess.Popen(cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        proc.communicate()  # Wait for Leo to terminate.
        return True
    #@+node:ekr.20100913085058.5655: *6* save_clipboard_to_screenshot_file
    def save_clipboard_to_screenshot_file(self):
        """Save the clipboard to screenshot_fn.
        Return True if all went well."""
        sc = self
        cb = g.app.gui.qtApp.clipboard()
        if not cb:
            g.error('no clipboard')
            return False
        image = cb.image()
        if image:
            image.save(sc.screenshot_fn)
            return True
        g.error('no image on clipboard')
        return False
    #@+node:ekr.20101113193341.5447: *3* sc.meld & helpers
    def meld(self, p):
        sc = self
        if not sc.init(p):
            return
        if not sc.wink_path:
            g.error('No @wink_path node')
            return
        print('=' * 20)
        aList = sc.get_wink_screenshots()
        if not aList:
            return
        if not sc.check_meld(aList):
            return
        # Pass 1: copy files for @slide nodes w/o @no-screenshot nodes.
        sc.copy_screenshots(aList)
        # Pass 2: adjust children of @slide nodes.
        sc.adjust_slideshow()
        print('meld done')
    #@+node:ekr.20101113193341.5448: *4* adjust_slideshow & helper
    def adjust_slideshow(self):
        """Adjust all @slide nodes in the slideshow."""
        # Traverse the tree as in the screenshot plugin.
        # That is, ignore @ignore trees and nested @slide nodes.
        # This ensures that the slide number, n, is correct.
        sc = self
        p = sc.slideshow_node
        after = p.nodeAfterTree()
        p = p.firstChild()
        n = 1
        while p and p != after:
            if sc.match(p, '@slide'):
                sc.adjust_slide_node(p, n)
                n += 1
                p.moveToNodeAfterTree()
            elif sc.match(p, '@ignore'):
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
    #@+node:ekr.20101113193341.5449: *5* adjust_slide_node & helpers
    def adjust_slide_node(self, p, slide_number):
        """Adjust p, an @slide node."""
        sc = self
        # Delete the first "@url built slide" node.
        sc.delete_at_url_built_slide_node(p)
        # Do nothing more if there is an @no-screenshot node.
        if sc.has_at_no_screenshot_node(p):
            return
        # Add or update the "@url final output file" node.
        sc.add_at_url_final_output_file(p, slide_number)
        # Add the .. image:: directive.
        sc.add_image_directive(p, slide_number)
    #@+node:ekr.20101113193341.5450: *6* add_at_url_final_output_file
    def add_at_url_final_output_file(self, p, slide_number):
        """Create or update the "@url final output file" node."""
        sc = self
        tag = '@url final output file'
        for child in p.children():
            if sc.match(child, tag):
                p2 = child
                break
        else:
            p2 = p.insertAsLastChild()
            p2.h = tag
        p2.b = sc.finalize(
            'slide-%03d.png' % (slide_number))
        return p2
    #@+node:ekr.20101113193341.5451: *6* add_image_directive
    def add_image_directive(self, p=None, slide_number=None):
        """Add an image directive in p if it is not there."""
        sc = self
        if not p:
            p = sc.slide_node
        if slide_number:
            s = '.. image:: slide-%03d.png' % (slide_number)
        else:
            s = '.. image:: %s' % sc.directive_fn.replace('\\', '/')
        if p.b.find(s) == -1:
            p.b = p.b.rstrip() + '\n\n%s\n\n' % (s)
    #@+node:ekr.20101113193341.5452: *6* delete_at_url_built_slide_node
    def delete_at_url_built_slide_node(self, p):
        """Delete any "@url built slide" node in p's children."""
        sc = self
        tag = '@url built slide'
        for child in p.children():
            if sc.match(child, tag):
                child.doDelete()
                break
    #@+node:ekr.20101113193341.5453: *4* check_meld & helpers
    def check_meld(self, aList):
        """
        Check that len(aList) matches the number of @slide nodes in the
        slideshow. Don't count @slide nodes containing an @no-screenshot node.
        """
        sc = self
        p = sc.slideshow_node
        n1 = len(aList)
        n2, n3 = sc.count_slide_nodes()
        if not sc.check_dir(sc.wink_path):
            return False
        if not sc.check_dir(sc.slideshow_path):
            return False
        if not sc.match(p, '@slideshow'):
            return g.error('not a @slideshow node: %s', p.h)
        if n1 != (n2 - n3):
            return g.error(
                '%s wink slides\n'
                '%s @slide nodes\n'
                '%s @no_screenshot nodes' % (
                    n1, n2, n3))
        return True
    #@+node:ekr.20101113193341.5454: *5* check_dir
    def check_dir(self, theDir):
        if not g.os_path_exists(theDir):
            return g.error('not found: %s' % (theDir))
        if not g.os_path_isdir(theDir):
            return g.error('not a directory: %s' % (theDir))
        return True
    #@+node:ekr.20101113193341.5455: *5* count_slide_nodes
    def count_slide_nodes(self):
        """Return n1,n2

        n1 is the total number of @slide nodes in the @slideshow tree.
        n2 is number of @slide nodes containing an @no-slideshow child.
        """
        sc = self
        p = sc.slideshow_node
        after = p.nodeAfterTree()
        p = p.firstChild()
        n1, n2 = 0, 0
        while p and p != after:
            if sc.match(p, '@slide'):
                n1 += 1
                if sc.has_at_no_screenshot_node(p):
                    n2 += 1
                p.moveToNodeAfterTree()
            elif sc.match(p, '@ignore'):
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
        g.trace(n1, n2)
        return n1, n2
    #@+node:ekr.20101113193341.5456: *4* copy_screenshots & helper
    def copy_screenshots(self, aList):
        """Copy files from the wink_path to slideshow_path,
        numbering the destination files to reflect "holes"
        created by @no-screenshot nodes."""
        # Traverse the tree as in the screenshot plugin.
        # That is, ignore @ignore trees and nested @slide nodes.
        # This ensures that the slide number, n, is correct.
        sc = self
        p = sc.slideshow_node
        after = p.nodeAfterTree()
        p = p.firstChild()
        wink_n = 0  # Wink screenshot numbers start at 0.
        slide_n = 1  # Slide numbers start at 1.
        while p and p != after:
            if sc.match(p, '@slide'):
                if not sc.has_at_no_screenshot_node(p):
                    sc.copy_screenshot(aList, slide_n, wink_n)
                    wink_n += 1
                slide_n += 1
                p.moveToNodeAfterTree()
            elif sc.match(p, '@ignore'):
                p.moveToNodeAfterTree()
            else:
                p.moveToThreadNext()
    #@+node:ekr.20101113193341.5457: *5* copy_screenshot
    def copy_screenshot(self, aList, slide_n, wink_n):
        sc = self
        if wink_n >= len(aList):
            g.trace('can not happen: len(aList): %s, n: %s' % (
                len(aList), wink_n))
            return
        fn_src = aList[wink_n]
        fn_dst = sc.finalize('slide-%03d.png' % (slide_n))
        shutil.copyfile(fn_src, fn_dst)
    #@+node:ekr.20101113193341.5458: *4* get_wink_screenshots
    def get_wink_screenshots(self):
        """Return the properly sorted list of wink screenshots."""
        sc = self
        aList = glob.glob(sc.wink_path + '/*.png')

        def key(s):
            path, ext = g.os_path_splitext(s)
            junk, n = g.os_path_split(path)
            n = n.strip()
            if n.isdigit():
                return int(n)
            # 2010/11/23: allow file names of the form xnnn.png.
            if n and n[-1].isdigit():
                i = len(n) - 1
                while i >= 0 and n[i:].isdigit():
                    i -= 1
                return int(n[i + 1 :])
            g.error('wink screenshot file names must end with a number: %s' % (s))
            raise KeyError

        aList.sort(key=key)  # Essential.
        return aList
    #@+node:ekr.20101113193341.5445: *4* has_at_no_screenshot_node
    def has_at_no_screenshot_node(self, p):
        sc = self
        for p in p.children():
            if sc.match(p, '@no-screenshot'):
                return True
        return False
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
