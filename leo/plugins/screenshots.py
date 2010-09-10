#@+leo-ver=5-thin
#@+node:ekr.20100908110845.5505: * @thin screenshots.py
#@+<< docstring >>
#@+node:ekr.20100908115707.5554: ** << docstring >>
"""screenshots.py: a plugin to take screen shots using Inkscape
============================================================

Inkscape, http://inkscape.org/, is an Open
Source vector graphics editor, with
capabilities similar to Illustrator,
CorelDraw, or Xara X, using the SVG (Scalable
Vector Graphics) file format. See
http://www.w3.org/Graphics/SVG/.

Leo scripts can control Inkscape using the
c.inkscapeCommands.run method (run for
short), a method of the LeoInkscapeCommands
class defined in leoRst.py.

The primary input to the run method is the
**screeshot file**. This must be a bitmap.
Typically the screenshot file will be a PNG
format file, though other kinds of bitmap
files should work. The user, or perhaps
another script, must generate the screenshot
file before calling run().

The run method works in three stages:

1. Convert the screenshot (bitmap) file to
   the **working file**. The working file is
   a SVG (vector graphic) file. Besides the
   image from the original screenshot, the
   working file may contain text **callouts**
   (text ballons) and **markers** (black
   circles containing numbers). You specify
   callouts and markers using arguments to
   the run method.

2. (Optional) Edit the working file using
   Inkscape. Inkscape will appear on the
   screen. You can edit and position callouts
   and markers, then save the working file.

3. (Optional) Use Inkscape behind the scenes
   to render a final PNG image from the
   working file.  If PIL is installed, this
   step adjusts the image in various subtle
   ways.

Prerequisites
-------------

Inkscape
  The SVG editor, from http://www.inkscape.org/

PIL
  The Python Imaging Library,
  http://www.pythonware.com/products/pil/

  Optional but highly recommended. If present,
  PIL will improve the quality of the generated
  images.

Settings
--------

@string inkscape-bin

This setting tells Leo the location of the Inkscape executable.

Usage
-----

The run method has the following signature::

    def run (self,fn,
        callouts=[],markers=[],edit_flag=True,
        png_fn=None,svg_fn=None,template_fn=None)

        fn  The name of the bitmap screenshot file.
  callouts  A possibly empty list of strings.
   markers  A possibly empty list of numbers.
 edit_flag  If True, run calls Inkscape so you can
            edit the working file interactively.
    png_fn  The name of final png image file.
            No image is generated if this argument is None.
    svg_fn  The name of working svg file.
            If no name is given, ``working_file.svg`` is used.
 template_fn The name of the **template svg file**.
            This file contains images to be used for
            callouts and markers.  If no name is given,
            inkscape-template.svg is used.

For example, the following places three text
balloon callouts and three black circle
numeric markers on a screenshot::

    fn = "some_screen_shot.png"
    png_fn = "final_screen_shot.png"
    callouts = (
        "This goes here",
        "These are those, but slightly longer",
        "Then you pull this")
    markers = (2,4,17)

    c.inkscapeCommands.run(fn,
        callouts=callouts,markers=markers,
        png_fn=png_fn)

"""
#@-<< docstring >>

__version__ = '0.1'

#@+<< imports >>
#@+node:ekr.20100908110845.5604: ** << imports >>
import leo.core.leoGlobals as g

import copy
import os

# Warnings are given later.
try:
    from PIL import Image, ImageChops
    got_pil = True
except ImportError:
    got_pil = False

try:
    from PyQt4.QtGui import QImage
    got_qt = True
except ImportError:
    got_qt = False

import subprocess
import tempfile

import xml.etree.ElementTree as etree
#@-<< imports >>

#@+others
#@+node:ekr.20100908110845.5606: ** init
def init ():

    ok = got_qt

    if ok:
        g.plugin_signon(__name__)

    return ok
#@+node:ekr.20100908110845.5580: ** Commands
#@+node:ekr.20100908110845.5581: *3* g.command(apropos-screen-shots)
# @pagewidth 45

@g.command('apropos-screen-shots')
def apropos_screen_shots(event):

    c = event.get('c')
    if not c: return

    #@+<< define s >>
    #@+node:ekr.20100908110845.5582: *4* << define s >>
    s = """\

    Using Inkscape to take screen shots
    ===================================

    Inkscape, http://inkscape.org/, is an Open
    Source vector graphics editor, with
    capabilities similar to Illustrator,
    CorelDraw, or Xara X, using the SVG (Scalable
    Vector Graphics) file format. See
    http://www.w3.org/Graphics/SVG/.

    Leo scripts can control Inkscape using the
    c.inkscapeCommands.run method (run for
    short), a method of the LeoInkscapeCommands
    class defined in leoRst.py.

    The primary input to the run method is the
    **screeshot file**. This must be a bitmap.
    Typically the screenshot file will be a PNG
    format file, though other kinds of bitmap
    files should work. The user, or perhaps
    another script, must generate the screenshot
    file before calling run().

    The run method works in three stages:

    1. Convert the screenshot (bitmap) file to
       the **working file**. The working file is
       a SVG (vector graphic) file. Besides the
       image from the original screenshot, the
       working file may contain text **callouts**
       (text ballons) and **markers** (black
       circles containing numbers). You specify
       callouts and markers using arguments to
       the run method.

    2. (Optional) Edit the working file using
       Inkscape. Inkscape will appear on the
       screen. You can edit and position callouts
       and markers, then save the working file.

    3. (Optional) Use Inkscape behind the scenes
       to render a final PNG image from the
       working file.  If PIL is installed, this
       step adjusts the image in various subtle
       ways.

    Prerequisites
    -------------

    Inkscape
      The SVG editor, from http://www.inkscape.org/

    PIL
      The Python Imaging Library,
      http://www.pythonware.com/products/pil/

      Optional but highly recommended. If present,
      PIL will improve the quality of the generated
      images.

    Settings
    --------

    @string inkscape-bin

    This setting tells Leo the location of the Inkscape executable.

    Usage
    -----

    The run method has the following signature::

        def run (self,fn,
            callouts=[],markers=[],edit_flag=True,
            png_fn=None,svg_fn=None,template_fn=None)

            fn  The name of the bitmap screenshot file.
      callouts  A possibly empty list of strings.
       markers  A possibly empty list of numbers.
     edit_flag  If True, run calls Inkscape so you can
                edit the working file interactively.
        png_fn  The name of final png image file.
                No image is generated if this argument is None.
        svg_fn  The name of working svg file.
                If no name is given, ``working_file.svg`` is used.
    template_fn The name of the **template svg file**.
                This file contains images to be used for
                callouts and markers.  If no name is given,
                inkscape-template.svg is used.

    For example, the following places three text
    balloon callouts and three black circle
    numeric markers on a screenshot::

        fn = "some_screen_shot.png"
        png_fn = "final_screen_shot.png"
        callouts = (
            "This goes here",
            "These are those, but slightly longer",
            "Then you pull this")
        markers = (2,4,17)

        c.inkscapeCommands.run(fn,
            callouts=callouts,markers=markers,
            png_fn=png_fn)

    """
    #@-<< define s >>

    g.es(g.adjustTripleString(s.rstrip(),c.tab_width))
#@+node:ekr.20100908110845.5583: *3* g.command(take_screen_shot)
@g.command('take-screen-shot')
def take_screen_shot_command (event):

    c = event.get('c')
    if not c: return

    ScreenShotController(c).screen_shot_command()
#@+node:ekr.20100908110845.5531: ** class ScreenShotController
class ScreenShotController(object):

    '''A class to take screen shots and control Inkscape.

    apropos-screenshots contains a more complete description.'''

    #@+others
    #@+node:ekr.20100908110845.5532: *3*  ctor
    def __init__(self,c):

        self.c = c

        # Non-changing settings.
        self.inkscape_bin = r'c:\Program Files (x86)\Inkscape\inkscape.exe' ### testing.

        # c.config.getString('inkscape-bin') or \

        assert g.os_path_exists(self.inkscape_bin)

        # Dimension cache.
        self.dimCache = {}
        self.is_reads,self.is_cache = 0,0

        # Internal constants.
        # element IDs which should exist in the SVG template
        self.ids = [
            "co_bc_1",        # 1 digit black circle
            "co_bc_2",        # 2 digit black circle
            "co_bc_text_1",   # text holder for 1 digit black circle
            "co_bc_text_2",   # text holder for 2 digit black circle
            "co_frame",       # frame for speech balloon callout
            "co_g_bc_1",      # group for 1 digit black circle
            "co_g_bc_2",      # group for 2 digit black circle
            "co_g_co",        # group for speech balloon callout
            "co_shot",        # image for screen shot
            "co_text_holder", # text holder for speech balloon callout
        ]

        self.xlink = "{http://www.w3.org/1999/xlink}"
        # self.namespace = {'svg': "http://www.w3.org/2000/svg"}
    #@+node:ekr.20100908110845.5533: *3*  lxml replacements
    #@+node:ekr.20100908110845.5534: *4* getElementsWithAttrib
    def getElementsWithAttrib (self,e,attr_name,aList=None):

        if aList is None: aList = []

        val = e.attrib.get(attr_name)
        if val: aList.append(e)

        for child in e.getchildren():
            self.getElementsWithAttrib(child,attr_name,aList)

        return aList
    #@+node:ekr.20100908110845.5535: *4* getElementsWithAttribList (not used)
    def getElementsWithAttribList (self,e,attr_names,aList=None):

        if aList is None: aList = []

        for z in attr_names:
            if not e.attrib.get(z):
                break
        else:
            aList.append(e)

        for child in e.getchildren():
            self.getElementsWithAttribList(child,attr_names,aList)

        return aList
    #@+node:ekr.20100908110845.5536: *4* getIds
    def getIds (self,e,d=None):

        '''Return a dict d. Keys are ids, values are elements.'''

        aList = self.getElementsWithAttrib(e,'id')
        return dict([(e.attrib.get('id'),e) for e in aList])

        # if d is None: d = {}
        # i = e.attrib.get('id')
        # if i: d[i] = e
        # for child in e.getchildren():
            # self.getIds(child,d)
        # return d
    #@+node:ekr.20100908110845.5537: *4* getParents
    def getParents (self,e,d=None):

        if d is None:
            d = {}
            d[e] = None

        for child in e.getchildren():
            d[child] = e
            self.getParents(child,d)

        return d
    #@+node:ekr.20100908110845.5538: *3*  utilities
    #@+node:ekr.20100908110845.5539: *4* error & warning
    def error (self,*args):

        if not g.app.unitTesting:
            g.es_print('Error:',*args,color='red')

    def warning (self,*args):

        if not g.app.unitTesting:
            g.es_print('Warning:',*args,color='blue')
    #@+node:ekr.20100908110845.5540: *4* finalize
    def finalize (self,fn):

        '''Return the absolute path to fn in the screenshot folder.'''

        s = g.os_path_finalize_join(g.app.loadDir,
            '..','doc','html','screen-shots',fn)

        return s.replace('\\','/')
    #@+node:ekr.20100908115707.5555: *3* screen_shot_command & helpers
    def screen_shot_command (self):

        c = self.c ; p = c.p

        if self.inSlideShow(p):

            self.give_pil_warning()

            # Take the screenshot and update the tree.
            fn = self.take_screen_shot(p)

            # Call Inkscape to post-process the slide.
            self.post_process(fn,p)
            c.selectPosition(p)
            c.redraw()
    #@+node:ekr.20100908110845.5592: *4* inSlideShow
    def inSlideShow (self,p):

        for p2 in p.parents():
            if p2.h.startswith('@slideshow'):
                return True
        else:
            return False
    #@+node:ekr.20100908110845.5543: *4* give_pil_warning
    pil_message_given = False

    def give_pil_warning(self):

        if self.pil_message_given:
            return # Warning already given.

        if got_pil:
            return # The best situation

        self.pil_message_given = True

        if got_qt:
            self.warning('PIL not found: images may have transparent borders')
        else:
            self.warning('PIL and Qt both not found: images may be less clear')
    #@+node:ekr.20100909121239.6117: *4* take_screen_shot & helpers
    def take_screen_shot(self,p):

        directive_path = self.get_directive_path(p)
        path = self.get_path(p)
        root,h = self.find_at_screenshot_tree_node(p)

        if 1:
            self.make_screen_shot(path,root,h)
            g.es('created %s' % path)
            self.make_image_node(p,path)
            self.add_image_directive(p,directive_path)

        return path
    #@+node:ekr.20100908110845.5594: *5* add_image_directive
    def add_image_directive (self,p,path):

        '''Add ".. image:: <path>" to p.b if it is not already there.'''

        path = path.replace('\\','/')
        s = '.. image:: %s' % path

        if p.b.find(s) == -1:
            p.b = p.b.rstrip() + '\n\n%s\n\n' % (s)
    #@+node:ekr.20100909121239.5742: *5* find_at_screenshot_tree_node
    def find_at_screenshot_tree_node (self,p):

        '''
        Find the @screenshot-tree node in a direct child of p.
        Set h to whatever follows @screenshot-tree in the headline.
        '''

        tag = '@screenshot-tree'

        for root in p.children():
            if g.match_word(root.h,0,tag):
                h = root.h[len(tag):].strip()
                break
        else:
            root,h = None,''

        return root,h
    #@+node:ekr.20100909121239.5669: *5* get_directive_path
    def get_directive_path (self,p):

        '''Compute the path for use in an .. image:: directive.'''

        fn = '%s.png' % (p.gnx.replace('.','-'))

        return self.finalize(fn)
    #@+node:ekr.20100909121239.5723: *5* get_path
    def get_path (self,p):

        '''Compute the path for @image nodes.'''

        fn = '%s.png' % (p.gnx.replace('.','-'))

        return self.finalize(fn)
    #@+node:ekr.20100908110845.5599: *5* make_image_node
    def make_image_node (self,p,path):

        '''Create an @image node as the first child of p.'''

        c = self.c
        h = '@image %s' % path

        # Create the node if it doesn't exist.
        for child in p.children():
            if child.h == h:
                # print('already exists: %s' % h)
                break
        else:
            c.selectPosition(p)
            p2 = p.insertAsNthChild(0)
            p2.h = h

        p.expand()
        c.redraw_now(p=p)
    #@+node:ekr.20100908110845.5600: *5* make_screen_shot & helpers
    def make_screen_shot (self,path,root,h):

        c = self.c

        old_size = c.frame.top.size()

        self.resize_leo_window()
        if root: self.hoist_and_select(root,h)

        self.make_screen_shot_helper(path)

        if root: c.dehoist()
        c.frame.top.resize(old_size)
    #@+node:ekr.20100908110845.5601: *6* hoist_and_select
    def hoist_and_select(self,root,h):

        '''root is an @screenshot-tree node.
        Hoist root.firstChild() and select h in root's tree.'''

        c = self.c

        if root.hasChildren(): root = root.firstChild()

        c.selectPosition(root)
        c.hoist()

        if not h: return
        # Select the requested node.
        p = g.findNodeInTree(c,root,h)
        if p:
            assert h == p.h
            assert c.positionExists(p,root=root)
            c.selectPosition(p)
        else:
            g.trace('*** not found ***',h)
    #@+node:ekr.20100908110845.5602: *6* make_screen_shot_helper
    def make_screen_shot_helper (self,path):

        try:
            import PyQt4.QtGui
            app = g.app.gui.qtApp
            pix = PyQt4.QtGui.QPixmap
        except ImportError:
            self.error('take-screenshot requires PyQt4')
            return

        w = pix.grabWindow(app.activeWindow().winId())

        # This generates an incorrect Qt error.
        # The file is, in fact, saved correctly.
        w.save(path,'png')

        g.trace('wrote',path)
    #@+node:ekr.20100908110845.5603: *6* resize_leo_window
    def resize_leo_window(self):

        '''Resize the Leo window to the standard size and
        make both panes the same size.'''

        c = self.c ; w = c.frame.top

        w.resize(1000,800)
        c.k.simulateCommand('equal-sized-panes')
        c.redraw()
        w.repaint() # Essential
    #@+node:ekr.20100908110845.5544: *4* post_process & helpers
    def post_process (self,fn,p):

        '''Post-process the slide fn.'''

        c = self.c

        template_fn = self.get_template_fn()
        if not template_fn: return

        png_fn = fn # Use output file is the same as the input file.
        svg_fn = self.finalize('screenshot_working_file.svg')

        callouts = self.get_callouts(p)
        markers = self.get_markers(p)
        template = self.make_svg(fn,svg_fn,template_fn,callouts,markers)
        if not template: return

        if callouts or markers:
            self.edit_svg(svg_fn)
        else:
            self.warning('No callouts or markers')

        self.make_png(svg_fn,png_fn)
    #@+node:ekr.20100908110845.5596: *5* get_callouts & helper
    def get_callouts (self,p):
        '''Return the list of callouts from the
        direct children that are @callout nodes.'''

        aList = []
        for child in p.children():
            # g.trace(child.h)
            if child.h.startswith('@callout'):
                callout = self.get_callout(child)
                if callout: aList.append(callout)
        g.trace(aList)
        return aList

    #@+node:ekr.20100909121239.6096: *6* get_callout
    def get_callout (self,p):

        '''Return the text of the callout at p.'''

        if p.b.strip():
            return p.b
        else:
            s = p.h ; assert s.startswith('@callout')
            i = g.skip_id(s,0,chars='@')
                # Match @callout or @callouts, etc.
            s = s[i:].strip()
            return s
    #@+node:ekr.20100908110845.5597: *5* get_markers & helper
    def get_markers (self,p):

        '''Return the list of callouts from the
        direct children that are @callout nodes.'''

        aList = []
        for child in p.children():
            if child.h.startswith('@marker'):
                callout = self.get_marker(child)
                if callout: aList.extend(callout)
        # g.trace(aList)
        return aList
    #@+node:ekr.20100909121239.6097: *6* get_marker
    def get_marker (self,p):

        '''Return a list of markers at p.'''

        s = p.h ; assert s.startswith('@marker')
        i = g.skip_id(s,0,chars='@')
            # Match @marker or @markers, etc.
        s = s[i:].strip()
        return [z.strip() for z in s.split(',')]
    #@+node:ekr.20100908110845.5542: *5* get_template_fn
    def get_template_fn (self,template_fn=None):

        c = self.c

        if template_fn:
            fn = template_fn
        else:
            # fn = c.config.getString('inkscape-template') or 'inkscape-template.png'
            fn = g.os_path_finalize_join(g.app.loadDir,
                '..','doc','inkscape-template.svg')

        if g.os_path_exists(fn):
            return fn
        else:
            self.error('template file not found:',fn)
            return None
    #@+node:ekr.20100908110845.5545: *5* step 1: make_svg & make_dom
    def make_svg(self,fn,output_fn,template_fn,callouts,markers):

        outfile = open(output_fn,'w')

        template = self.make_dom(fn,template_fn,callouts,markers)

        if template:
            template.write(outfile)

        outfile.close()

        return template
    #@+node:ekr.20100908110845.5546: *6* make_dom & helpers
    def make_dom(self,fn,template_fn,callouts,markers):

        trace = True and not g.unitTesting
        template = self.get_template(template_fn)
        if not template: return None
        root = template.getroot()
        ids_d = self.getIds(root)
        parents_d = self.getParents(root)

        # make a dict of the groups we're going to manipulate
        part = dict([(z,ids_d.get(z))
            for z in ('co_g_co', 'co_g_bc_1', 'co_g_bc_2')])

        # note where we should place modified copies
        part_parent = parents_d.get(part.get('co_g_co'))

        # remove them from the document
        for i in part.values():
            parents_d = self.getParents(root)
            parent = parents_d.get(i)
            parent.remove(i)

        for n,callout in enumerate(callouts):
            if trace: g.trace('callout %s: %s' % (n,callout))
            z = copy.deepcopy(part['co_g_co'])
            ids_d = self.getIds(z)
            text = ids_d.get('co_text_holder')
            text.text = callout
            # need distinct IDs on frames/text for sizing
            frame = ids_d.get('co_frame')
            self.clear_id(z) # let inkscape pick new IDs for other elements

            # A) it's the flowRoot, not the flowPara, which carries the size info
            # B) Inkscape trashes the IDs on flowParas on load!
            parents_d = self.getParents(z)
            parent = parents_d.get(text)
            parent.set('id', 'co_text_%d'%n)
            frame.set('id', 'co_frame_%d'%n)

            # offset so user can see them all
            self.move_element(z, 20*n, 20*n)
            part_parent.append(z)

        for n,number in enumerate(markers):
            if trace: g.trace('number %s: %s' % (n,number))
            if len(str(number)) == 2:
                use_g,use_t = 'co_g_bc_2', 'co_bc_text_2'
            else:
                use_g,use_t = 'co_g_bc_1', 'co_bc_text_1'

            z = copy.deepcopy(part[use_g])
            ids_d = self.getIds(z)
            bc_text = ids_d.get(use_t) 
            bc_text.text = str(number)
            self.move_element(z, 20*n, 20*n)
            part_parent.append(z)

        # point to the right screen shot
        ids_d = self.getIds(template.getroot())
        img_element = ids_d.get('co_shot')
        img_element.set(self.xlink+'href',fn)

        # adjust screen shot dimensions
        if got_pil:
            img = Image.open(fn)
            img_element.set('width', str(img.size[0]))
            img_element.set('height', str(img.size[1]))

        # if self.opt.no_resize:
            # return template

        # write temp file to get size info
        fh, fp = tempfile.mkstemp()
        os.close(fh)
        template.write(fp)

        # could reload file at this point to reflect offsets etc.
        # but don't need to because of relative position mode in paths

        # resize things to fit text
        for n,callout in enumerate(callouts):
            self.resize_curve_box(fp, template, n)

        os.unlink(fp)
        return template
    #@+node:ekr.20100908110845.5547: *7* clear_id
    def clear_id(self,x):

        """recursively clear @id on element x and descendants"""

        if 'id' in x.keys():
            del x.attrib['id']

        ids_d = self.getIds(x)
        objects = set(list(ids_d.values()))
        for z in objects:
            del z.attrib['id']

        return x
    #@+node:ekr.20100908110845.5548: *7* get_template
    def get_template(self,template_fn):

        """Load and check the template SVG and return DOM"""

        infile = open(template_fn)
        template = etree.parse(infile)
        ids_d = self.getIds(template.getroot())

        # check all IDs we expect are present
        ids = list(ids_d.keys())
        if set(self.ids) <= set(ids):
            return template
        else:
            self.error('template did not include all required IDs:',template_fn)
            return None
    #@+node:ekr.20100908110845.5549: *7* move_element
    def move_element(self,element,x,y):

        if not element.get('transform'):
            element.set('transform', "translate(%f,%f)" % (x,y))
        else:
            ox,oy = element.get('transform').split(',')
            ox = ox.split('(')[1]
            oy = oy.split(')')[0]

            element.set('transform', "translate(%f,%f)" %
                (float(ox)+x, float(oy)+y))
    #@+node:ekr.20100908110845.5550: *7* resize_curve_box & helper
    def resize_curve_box(self,fn,template,n):

        d = self.getIds(template.getroot())
        text = d.get('co_text_%d' % (n))
        frame = d.get('co_frame_%d' % (n))
        text_id = text.get('id')
        frame_id = frame.get('id')

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

        # g.trace('\n'.join([repr(i) for i in pnts])_
        # g.trace(self.get_dim(fn, text_id, 'width'), self.get_dim(fn, text_id, 'height'))
        # g.trace(self.get_dim(fn, frame_id, 'width'), self.get_dim(fn, frame_id, 'height'))

        # kludge for now
        h0 = 12  # index of vertical component going down right side
        h1 = -4  # index of vertical component coming up left side
        min_ = 0  # must leave this many
        present = 5  # components present initially
        h = pnts[h0][2]  # height of one component
        th = self.get_dim(fn, text_id, 'height')  # text height
        # g.trace('  ', present, h, present*h, th)
        while present > min_ and present * h + 15 > th:
            # g.trace('  ', present, h, present*h, th)
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
    #@+node:ekr.20100908110845.5551: *8* get_dim
    def get_dim(self, fn, Id, what):
        """return dimension of element in fn with @id Id, what is
        x, y, width, or height
        """

        hsh = fn+Id+what
        if hsh in self.dimCache:
            self.is_cache += 1
            return self.dimCache[hsh]

        cmd = [self.inkscape_bin, '--without-gui', '--query-all', fn]

        proc = subprocess.Popen(cmd,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE)

        # make new pipe for stderr to supress chatter from inkscape
        stdout, stderr = proc.communicate()
        s = str(stdout).strip()

        # Necessary for Python 3k.
        if s.startswith("b'"): s = s[2:]
        if s.endswith("'"): s = s[:-1]
        aList = s.replace('\\r','').replace('\\n','\n').split('\n')
        for line in aList:
            if not line.strip(): continue
            id_,x,y,w,h = line.split(',')
            for part in ('x',x), ('y',y), ('width',w), ('height',h):
                hsh2 = fn+id_+part[0]
                self.dimCache[hsh2] = float(part[1])
        self.is_reads += 1

        return self.dimCache[hsh]
    #@+node:ekr.20100908110845.5552: *5* step 2: edit_svg & enable_filters
    def edit_svg(self,svg_fn):

        cmd = [self.inkscape_bin,"--with-gui",svg_fn]
        self.enable_filters(svg_fn, False)
        proc = subprocess.Popen(cmd, stderr=subprocess.PIPE)
        proc.communicate()
        # self.enable_filters(svg_fn, True)
    #@+node:ekr.20100908110845.5553: *6* enable_filters
    def enable_filters(self,svgfile,enable):
        """Disable/enable filters in SVG at the XML level

        The drop-shadow filter on several objects kills editing performance
        in inkscape, so this turns them on/off in the XML.  There's a GUI
        operation to turn them off in inkscape, but it's a pain to have to
        keep using it.

        Disabling copys the real @style to @__style and changes
        "filter:url" to "_filter:url" in the active @style, while
        enabling just copys @__style to @style and deletes @__style.
        """

        doc = etree.parse(svgfile)
        root = doc.getroot()

        if enable:
            # copy @__style to @style and deletes @__style.
            aList = self.getElementsWithAttrib(root,'__style')
            for i in aList:
                i.set("style", i.get("__style"))
                del i.attrib['__style']
        else:
            aList3 = self.getElementsWithAttrib(root,'style')
            aList = [z for z in aList3
                if z.attrib.get('style').find('filter:url(') > -1]
            # copy the real @style to @__style and
            # changes "filter:url" to "_filter:url" in the active @style
            for i in aList:
                i.set("__style", i.get("style"))
                i.set("style", i.get("style").replace(
                    'filter:url(', '_filter:url('))

        doc.write(open(svgfile, 'w'))
    #@+node:ekr.20100908110845.5554: *5* step 3: make_png & trim
    def make_png(self,svg_fn,png_fn):

        '''Create png_fn from svg_fn.'''

        # png_fn = self.finalize('output.png')
        # png_fn = os.path.splitext(png_fn)[0] + ".co.png"

        cmd = [
            self.inkscape_bin,
            "--without-gui",
            "--export-png="+png_fn,
            "--export-area-drawing",
            "--export-area-snap",
            svg_fn,
        ]

        proc = subprocess.Popen(cmd, stderr=subprocess.PIPE)
        proc.communicate()

        if got_pil: # trim transparent border
            try:
                img = Image.open(png_fn)
                img = self.trim(img, (255,255,255,0))
                img.save(png_fn)
            except IOError:
                g.trace('Can not open %s' % png_fn)

        # os.system(png_fn)
    #@+node:ekr.20100908110845.5555: *6* trim
    def trim(self, im, border):
         bg = Image.new(im.mode, im.size, border)
         diff = ImageChops.difference(im, bg)
         bbox = diff.getbbox()
         if bbox:
             return im.crop(bbox)
         else:
             # found no content
             raise ValueError("cannot trim; image was empty")
    #@+node:ekr.20100909193826.5600: *4* select_at_image_node
    def select_at_image_node (self,p):

        c = self.c
        for child in p.children():
            if child.h.startswith('@image'):
                c.selectPosition(child)
                c.redraw_now(child)
                break
        else:
            c.selectPosition(p)
            c.redraw_now(p)
    #@-others

#@-others
#@-leo
