#@+leo-ver=5-thin
#@+node:ekr.20100906164425.5874: * @thin leoInkscape.py
#@@language python
#@@tabwidth -4

#@+<< docstring >>
#@+node:ekr.20100906164425.5875: ** << docstring >>
"""

InkCall - screen shot call out utility using Inkscape
=====================================================

InkCall can be used from the command line or from a python script.  It
works in three stages:

    - generate SVG from template, screen shot filename, list of text (speech
      balloon) callouts, and list of numeric (black circle) markers

    - Invoke Inkscape interactively on the SVG so the user can position the
      markers and drag out the balloon tails as required

    - Invoke Inkscape non-interactively to render a .png from the edited SVG

Prerequisites
-------------

Inkscape
  The SVG editor, from http://www.inkscape.org/
lxml
  | The Python module for XML DOM manipulation, from ``easy_install lxml``
  | *Important:* You may have to add a version number,as in ``easy_install lxml==2.2.4``
  | See http://codespeak.net/lxml/installation.html for details.
PIL (recommended, not essential)
  The Python Imaging Library (http://www.pythonware.com/products/pil/) can be
  used to fix screenshot size in the SVG to avoid rescaling, see `Details`_.

Usage
-----

The user is responsible for generating the initial screen shot, a bitmap image,
probably PNG format, although others should work. **InkCall will derive file
names from the file name of the screenshot** for all its operations, unless
alternative file names are supplied.  Derived names are::

    myshot.png -> myshot.svg -> myshot.co.png

Step 1 - generate SVG
+++++++++++++++++++++

To place three text balloon callouts and three black circle numeric
markers on a screenshot::

    from inkcall import InkCall

    inkcall = InkCall()

    filename = "some_screen_shot.png"  # will create some_screen_shot.svg

    callouts = [
        "This goes here",
        "These are those, but slightly longer",
        "Then you pull this, but this text needs to be longer for testing",
    ]
    numbers = [2,4,17]

    inkcall.make_svg(filename, callouts, numbers)

Step 2 - edit SVG
+++++++++++++++++

You can edit the SVG in Inkscape directly, or invoke it like this::

    inkcall.edit_svg(filename)

The above will disable filters in the SVG file (by tweaking the @style
attribute) before editing and re-enable them afterward. Drop shadow rendering
on multiple balloons really kills performance, and while you can disable filter
display in Inkscape, it's easier if you don't need to.


Step 3 - render PNG
+++++++++++++++++++

Make the final output with::

    inkcall.make_png(filename)  # will create some_screen_shot.co.png


Configuring InkCall
+++++++++++++++++++

InkCall supports the following options::

    Usage: inkcall.py [options] <screenshotimage>

    Options:
      -h, --help           show this help message and exit
      --template=TEMPLATE  filename for SVG template [default: template.svg]
      --svg=SVG            filename for SVG working file [default:
                           <screenshotimage>.svg]
      --png=PNG            filename for OUTPUT PNG file [default:
                           <screenshotimage>.co.png]
      --callout=CALLOUT    add a callout text to the list
      --number=NUMBER      add a callout number to the list
      --no-resize          don't resize balloons etc. to fit text
      --inkscape=INKSCAPE  Inkscape executeable, with path, if needed
      --no-svg             Don't do SVG creation step
      --no-edit            Don't do SVG edit creation step
      --no-png             Don't do final PNG render step

For use from within python, only some of these make sense for manipulation; ``template``,
``svg``, ``png``, ``no_resize``, and ``inkscape``.  For example::

    inkcall = InkCall({
        'template': "/path/to/mytemplate.svg",
        'svg': "temp.svg",
        'no_resize': True,
        'inkscape': "c:\\Program Files (x86)\\Inkscape\\inkscape.exe",
    })

To do
-----

    - [done] Tweak screenshot image size to avoid rescaling, using PIL
    - Add new callouts to an existing SVG
    - Improve resizing of balloons
    - Special callout template for single line callouts?

Details
-------

InkCall does some tricky things behind the scenes.  If the Python Imaging Library (PIL)
is available, it sets the image size in the SVG based on the true image size, to get
pixel perfect rendering of the screenshot (as long as it's aligned on pixel boundaries
in the template).  Without PIL the screenshot may be rescaled, although if you know
all your screenshots will be the same size, you can set up the template appropriately.  
PIL is also used to remove transparent borders from images.

InkCall also writes a temporary version of the SVG and invokes Inkscape non-interactively
to get the rendered (wrapped) dimension of the text.  It then edits the balloon path to
make the balloon fit the text (somewhat crudely at present).

As mentioned above, it also temporarily hides the filter references so drop shadow
rendering doesn't slow down balloon editing.  It does this by munging and unmunging
the @style attribute.

"""
#@-<< docstring >>
#@+<< imports >>
#@+node:ekr.20100906164425.5876: ** << imports >>
import leo.core.leoGlobals as g

try:
    from PIL import Image, ImageChops
    got_pil = True
except ImportError:
    got_pil = False

# try:
    # from lxml import etree
# except ImportError:
    # etree = None

import xml.etree.ElementTree as eltree
import optparse
import os
import subprocess
# import sys
from copy import deepcopy
import tempfile
#@-<< imports >>

class LeoInkscapeCommands(object):

    '''A class to control Inkscape.'''

    #@+others
    #@+node:ekr.20100906164425.5882: **  ctor (LeoInkscapeCommands)
    def __init__(self,c):

        self.c = c

        # Non-changing settings.
        self.inkscape_bin = c.config.getString('inkscape-bin') or \
            r'c:\Program Files (x86)\Inkscape\inkscape.exe' ### testing.

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
        self.NS = {'svg': "http://www.w3.org/2000/svg"}

    #@+node:ekr.20100906164425.5883: ** lxml replacements
    #@+node:ekr.20100906164425.5890: *3* dumpMismatch
    def dumpMismatch(self,caller,aList,aList2):

        print('\n\n',caller)

        print('****aList...')
        for z in aList: print(z)

        print('\n\n****aList2')
        for z in aList2: print(z)
    #@+node:ekr.20100906164425.5884: *3* getElementsWithAttrib
    def getElementsWithAttrib (self,e,attr_name,aList=None):

        if aList is None: aList = []

        val = e.attrib.get(attr_name)
        if val: aList.append(e)

        for child in e.getchildren():
            self.getElementsWithAttrib(child,attr_name,aList)

        return aList
    #@+node:ekr.20100906164425.5885: *3* getElementsWithAttribList (not used)
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
    #@+node:ekr.20100906164425.5886: *3* getIds
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
    #@+node:ekr.20100906164425.5887: *3* getParents
    def getParents (self,e,d=None):

        if d is None:
            d = {}
            d[e] = None

        for child in e.getchildren():
            d[child] = e
            self.getParents(child,d)

        return d
    #@+node:ekr.20100906165118.5911: ** Utilities
    #@+node:ekr.20100906165118.5910: *3* error & warning
    def error (self,*args):

        g.es_print(*args,color='red')

    def warning (self,*args):

        g.es_print(*args,color='blue')
    #@+node:ekr.20100906165118.5912: *3* finalize
    def finalize (self,fn):

        return g.os_path_abspath(g.os_path_finalize(fn))
    #@+node:ekr.20100906165118.5878: *3* give_pil_warning
    pil_message_given = False

    def give_pil_warning(self):

        if not self.pil_message_given:
            self.pil_message_given = True
            if not g.unitTesting:
                g.es_print('PIL not found: ' +
                    'images will be less clear than they could be',
                    color='red')
    #@+node:ekr.20100906165118.5877: ** run & helpers
    def run (self,
        fn, # Required: the name of the screenshot file (.png) file.
        callouts, # A possibly empty list of callouts.
        numbers, # A possibly empty list of callouts.
        edit_flag = True, # True: call inkscape to edit the working file.
        png_fn=None, # Optional: Name of output png file.
        svg_fn=None, # Optional: Name of working svg file.
        template_fn=None, # Optional: Name of template svg file.
    ):

        c = self.c
        self.errors = 0

        if not got_pil:
            self.give_pil_warning()

        fn = self.get_screenshot_fn(fn)
        if not fn: return

        template_fn = self.get_template_fn(template_fn)
        if not template_fn: return

        png_fn = self.finalize(png_fn)
        svg_fn = self.finalize(svg_fn and svg_fn.strip() or 'working_file.svg')

        if 0: # Testing only
            fn = "some_screen_shot.png"
            callouts = [
                "This goes here",
                "These are those, but slightly longer",
                "Then you pull this, but this text needs to be longer for testing",
            ]
            numbers = [2,4,17]

        self.make_svg(fn,svg_fn,template_fn,callouts,numbers)

        if edit_flag:
            self.edit_svg(svg_fn)

        if png_fn:
            self.make_png(svg_fn,png_fn)
    #@+node:ekr.20100906165118.5913: *3* get_screenshot_fn
    def get_screenshot_fn (self,fn):

        fn = fn.strip()

        if fn:
            fn = self.finalize(fn)
            if g.os_path_exists(fn):
                return fn
            else:
                self.error('screenshot file not found:',fn)
                return None
        else:
            self.error('missing screenshot_fn arg')
            return None
    #@+node:ekr.20100906165118.5914: *3* get_template_fn
    def get_template_fn (self,template_fn):

        if template_fn:
            fn = template_fn
        else:
            fn = c.config.getString('inkscape-template') or 'inkscape-template'

        fn = self.finalize(fn)
        if g.os_path_exists(fn):
            return fn
        else:
            self.error('template file not found:',fn)
            return None
    #@+node:ekr.20100906164425.5891: ** step 1: make_svg & make_dom
    def make_svg(self,fn,output_fn,template_fn,callouts,numbers):

        # if self.opt.svg:
            # outfile = open(self.opt.svg, 'w')
        # elif not outfile:
            # outfile = open(os.path.splitext(filename)[0] + ".svg", 'w')

        outfile = open(output_fn,'w')

        self.make_dom(fn,template_fn,callouts,numbers).write(outfile)
    #@+node:ekr.20100906164425.5892: *3* make_dom & helpers
    def make_dom(self,fn,template_fn,callouts, numbers):

        trace = True
        template = self.get_template(template_fn)
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
            if trace: print('make_dom',n,callout)
            z = deepcopy(part['co_g_co'])
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

        for n,number in enumerate(numbers):
            if len(str(number)) == 2:
                use_g,use_t = 'co_g_bc_2', 'co_bc_text_2'
            else:
                use_g,use_t = 'co_g_bc_1', 'co_bc_text_1'

            z = deepcopy(part[use_g])
            ids_d = self.getIds(z)
            bc_text = ids_d.get(use_t) 
            bc_text.text = str(number)
            self.move_element(z, 20*n, 20*n)
            parent.append(z)

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
    #@+node:ekr.20100906164425.5893: *4* clear_id
    def clear_id(self,x):

        """recursively clear @id on element x and descendants"""

        if 'id' in x.keys():
            del x.attrib['id']

        ids_d = self.getIds(x)
        objects = set(list(ids_d.values()))
        for z in objects:
            del z.attrib['id']

        return x
    #@+node:ekr.20100906164425.5894: *4* get_template (revise)
    def get_template(self,template_fn):

        """Load and check the template SVG and return DOM"""

        infile = open(template_fn)
        template = eltree.parse(infile)
        ids_d = self.getIds(template.getroot())

        # check all IDs we expect are present
        ids = list(ids_d.keys())
        if not set(self.ids) <= set(ids):
            raise Exception(
                "inkcall: template did not include all required IDs")

        return template
    #@+node:ekr.20100906164425.5895: *4* move_element
    def move_element(self,element,x,y):

        if not element.get('transform'):
            element.set('transform', "translate(%f,%f)" % (x,y))
        else:
            ox,oy = element.get('transform').split(',')
            ox = ox.split('(')[1]
            oy = oy.split(')')[0]

            element.set('transform', "translate(%f,%f)" %
                (float(ox)+x, float(oy)+y))
    #@+node:ekr.20100906164425.5896: *4* resize_curve_box & helper
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

        # print '\n'.join([repr(i) for i in pnts])

        # print self.get_dim(fn, text_id, 'width'), self.get_dim(fn, text_id, 'height')
        # print self.get_dim(fn, frame_id, 'width'), self.get_dim(fn, frame_id, 'height')

        # kludge for now
        h0 = 12  # index of vertical component going down right side
        h1 = -4  # index of vertical component coming up left side
        min_ = 0  # must leave this many
        present = 5  # components present initially
        h = pnts[h0][2]  # height of one component
        th = self.get_dim(fn, text_id, 'height')  # text height
        # print '  ', present, h, present*h, th
        while present > min_ and present * h + 15 > th:
            # print '  ', present, h, present*h, th
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
        # print
        # print frame.get('d')
    #@+node:ekr.20100906164425.5897: *5* get_dim
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
            # print(repr(line))
            id_,x,y,w,h = line.split(',')
            for part in ('x',x), ('y',y), ('width',w), ('height',h):
                hsh2 = fn+id_+part[0]
                self.dimCache[hsh2] = float(part[1])
        self.is_reads += 1

        return self.dimCache[hsh]
    #@+node:ekr.20100906164425.5898: ** step 2: edit_svg & enable_filters
    def edit_svg(self,svg_fn):

        cmd = [self.inkscape_bin,"--with-gui",svg_fn]
        self.enable_filters(svg_fn, False)
        proc = subprocess.Popen(cmd, stderr=subprocess.PIPE)
        proc.communicate()
        self.enable_filters(svg_fn, True)
    #@+node:ekr.20100906164425.5899: *3* enable_filters
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

        doc = eltree.parse(svgfile)
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
    #@+node:ekr.20100906164425.5900: ** step 3: make_png & trim
    def make_png(self,svg_fn,png_fn):

        '''Create png_fn from svg_fn.'''

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
                print('Can not open %s' % png_fn)
    #@+node:ekr.20100906164425.5901: *3* trim
    def trim(self, im, border):
         bg = Image.new(im.mode, im.size, border)
         diff = ImageChops.difference(im, bg)
         bbox = diff.getbbox()
         if bbox:
             return im.crop(bbox)
         else:
             # found no content
             raise ValueError("cannot trim; image was empty")
    #@-others

#@-leo
