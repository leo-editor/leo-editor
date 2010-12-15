#@+leo-ver=5-thin
#@+node:tbrown.20060828111141: * @file cleo.py
#@+<< docstring >>
#@+node:tbrown.20060903211930: ** << docstring >>
''' Creates coloured Leo outlines.

``cleo`` is a Tk plugin, the Qt version is called ``todo``.

Cleo adds time required, progress and priority settings for nodes.
It also allows you to colour nodes.  With the @project tag a
branch can display progress and time required with dynamic updates.

Right click on a node's icon box to display the cleo menu.

For full documentation see:

  - http://leo.zwiki.org/Cleo 
  - http://leo.zwiki.org/cleodoc.html

'''
#@-<< docstring >>

#@@language python
#@@tabwidth -4

#@+<< imports >>
#@+node:tbrown.20060903121429.2: ** << imports >>
import leo.core.leoGlobals as g

Tk = g.importExtension('Tkinter',pluginName=__name__,verbose=True)
#@-<< imports >>
__version__ = "0.25.2"
#@+<< version history >>
#@+node:tbrown.20060903121429.3: ** << version history >>
#@@killcolor

#@+at Use and distribute under the same terms as leo itself.
# 
# Original code by Mark Ng <z3r0.00@gmail.com>
# 
# 0.5  Priority arrows and Archetype-based colouring of headline texts.
# 0.6  Arbitary headline colouring.
# 0.7  Colouring for node types. Added "Others" type option
# 0.8  Added "Clear Priority" option
# 0.8.1  Fixed popup location
# 0.8.2  Fixed unposting
# 0.9  Automatically colour @file and @ignore nodes
# 0.10 EKR:
# - Repackaged for leoPlugins.leo.
#     - Define g.  Eliminate from x import *.
# - Made code work with 4.3 code base:
#     - Override tree.setUnselectedHeadlineColors instead of tree.setUnselectedLabelState
# - Create per-commander instances of cleoController in onCreate.
# - Converted some c/java style to python style.
# - Replaced string.find(s,...) by s.find(...) & removed import string.
# - show_menu now returns 'break':  fixes the 'popup menu is not unposting bug)
# 0.11 EKR:
# - hasUD and getUD now make sure that the dict is actually a dict.
# 0.12 EKR:
# - Changed 'new_c' logic to 'c' logic.
# 0.13 EKR:
# - Installed patch roughly following code at http://sourceforge.net/forum/message.php?msg_id=3517080
# - custom_colours now returns None for default.
# - Added override of setDisabledHeadlineColors so that color changes in headlines happen immediately.
# - Removed checkmark menu item because there is no easy way to clear it.
# 0.14 EKR: Installed further patch to clear checkmark.
# 0.15 TNB:
# - Use dictionary of lists of canvas objects to allow removal
# - Removed code for painting over things
# - Try to track which commander/frame/tree is being used when more than
#   one Leo window open.  Not quite working, redraws are missed if you change
#   Leo windows by right clicking on the icon box, but all changes occur and
#   appear when a left click on the tree occurs.
# - Added rich_ries patch to darken colour of selected auto-colored headlines
# 0.16 TNB:
# - finally seem to have resolved all issues with multiple Leo windows
# - handlers now unregister when window closes
# 0.17 TNB:
# - don't write cleo.TkPickleVars into .leo file (but handle legacies)
# - don't write empty / all default value dictionaries into .leo file
# - added menu option to strip empty / all default value dictionaries from .leo file
# 0.17.1 TNB:
# - added DanR's custom colour selection idea and progress bars
# 0.18 TNB:
# - added time required and recursive time/progress calc.
#   thanks again to DanR for pointers.
# 0.19 TNB:
# - added @project nodes for automatic display updates
# - added Show time to show times on nodes
# - added Find next todo
# 0.20 EKR: applied patch by mstarzyk.
# 0.21 EKR: protect access to c.frame.tree.canvas.  It may not exist during dynamic unit tests.
# 0.22 EKR: fixed crasher in custom_colours.
# 0.23 EKR: added 'c' arg to p.isVisible (v.isVisible no longer exists).
# 0.24 EKR: removed bugs section.
# 0.25 TNB:
# - added priority sort, tag all children 'todo'
# - switched to leo icons for priority display
# 0.25.1 bobjack
# - make leo play nice with rclick and standard tree popup on linux
#     - post menu with g.app.postPopupMenu
#     - destroy menu with g.app.killPopupMenu
# 0.25.2 TNB: highlight all nodes with altered background colors, minor bug fixes
#@-<< version history >>

ok = Tk is not None

#@+others
#@+node:tbrown.20060903121429.11: ** class TkPickleVar(Tk.Variable)
if ok: # Don't define this if import Tkinter failed.

    class TkPickleVar (Tk.Variable):
        "Required as target for Tk menu functions to write back into"

        def __setstate__(self,state):
            Tk.Variable.__init__(self)
            Tk.Variable.set(self,state)

        def __getstate__(self):
            p = Tk.Variable.get(self)
            # Beware of returning False!
            return p
#@+node:tbrown.20060903121429.12: ** init
def init():

    ok = Tk and g.app.gui.guiName() == "tkinter"

    if ok:
        g.registerHandler(('open2','new'), onCreate)
        g.plugin_signon(__name__)

    return ok
#@+node:tbrown.20060903121429.13: ** onCreate
def onCreate (tag,key):

    c = key.get('c')

    cleoController(c)
#@+node:tbrown.20060903121429.14: ** class cleoController
class cleoController:

    '''A per-commander class that recolors outlines.'''

    #@+others
    #@+node:tbrown.20080304230028: *3* priority table
    priorities = {
      1: {'long': 'Urgent',    'short': '1', 'icon': 'pri1.png'},
      2: {'long': 'Very High', 'short': '2', 'icon': 'pri2.png'},
      3: {'long': 'High',      'short': '3', 'icon': 'pri3.png'},
      4: {'long': 'Medium',    'short': '4', 'icon': 'pri4.png'},
      5: {'long': 'Low',       'short': '5', 'icon': 'pri5.png'},
      6: {'long': 'Very Low',  'short': '6', 'icon': 'pri6.png'},
      7: {'long': 'Sometime',  'short': '7', 'icon': 'pri7.png'},
      8: {'long': 'Level 8',   'short': '8', 'icon': 'pri8.png'},
      9: {'long': 'Level 9',   'short': '9', 'icon': 'pri9.png'},
     10: {'long': 'Level 0',   'short': '0', 'icon': 'pri0.png'},
     19: {'long': 'To do',     'short': 'o', 'icon': 'chkboxblk.png'},
     20: {'long': 'Bang',      'short': '!', 'icon': 'bngblk.png'},
     21: {'long': 'Cross',     'short': 'X', 'icon': 'xblk.png'},
     22: {'long': '(cross)',   'short': 'x', 'icon': 'xgry.png'},
     23: {'long': 'Query',     'short': '?', 'icon': 'qryblk.png'},
     24: {'long': 'Bullet',    'short': '-', 'icon': 'bullet.png'},
    100: {'long': 'Done',      'short': 'D', 'icon': 'chkblk.png'},
    }

    todo_priorities = 1,2,3,4,5,6,7,8,9,10,19
    #@+node:tbrown.20060903121429.15: *3* birth
    def __init__ (self,c):

        self.c = c
        c.cleo = self
        self.menu = None
        self.donePriority = 100
        self.smiley = None

        self.marks = []   # list of marks made on canvas

        #@+<< set / read default values >>
        #@+node:tbrown.20060913151952: *4* << set / read default values >>
        self.progWidth = 18
        if c.config.getInt('cleo_prog_width'):
            self.progWidth = c.config.getInt('cleo_prog_width')

        self.time_init = 1.0
        if c.config.getFloat('cleo_time_init'):
            self.time_init = c.config.getFloat('cleo_time_init')

        self.scaleProg = 1
        if c.config.getInt('cleo_prog_scale'):
            self.progWidth = c.config.getInt('cleo_prog_scale')

        self.extraProg = 4
        if c.config.getFloat('cleo_prog_extra'):
            self.progWidth = c.config.getFloat('cleo_prog_extra')

        self.time_name = 'days'
        if c.config.getString('cleo_time_name'):
            self.time_name = c.config.getString('cleo_time_name')

        self.colorIgnore = c.config.getBool('cleo_color_ignore',default=True)

        self.icon_location = 'beforeIcon'
        if c.config.getString('cleo_icon_location'):
            self.icon_location = c.config.getString('cleo_icon_location')
        #@-<< set / read default values >>

        # image ids should be a property of the node
        # use {marking,image id} as the kv pair.
        self.images = {}

        #@+<< define colors >>
        #@+node:tbrown.20060903121429.16: *4* << define colors >>

        # see docstring for related @settings

        self.colours = [
            'Black',
            'Brown', 'Purple', 'Red', 'Pink',
            'Yellow', 'Orange', 'Khaki', 'Gold',
            'DarkGreen', 'Green', 'OliveDrab2',
            'Blue', 'Lightblue', 'SteelBlue2',
            'White',
        ]

        self.archetype_colours = {
            'Data' : 'Purple',
            'Thing' : 'Green3',
            'Logic' : 'Blue',
            'Interface': 'DarkOrange',
            'Moment-Interval' : 'Red',
        }

        self.node_colours = {
            'file' : 'lightgreen',
            'Major Branch' : 'SandyBrown',
            'Feature' : 'peachpuff',
            'Comments': 'lightblue',
            'Sel. File' : 'PaleGreen4',
            'Sel. Major Branch' : 'tan4',
            'Sel. Feature' : 'PeachPuff4',
            'Sel. Comments': 'LightBlue4',
        }

        self.file_nodes = ["@file", "@thin", "@nosent", "@asis", "@root"]
        if g.app.config.exists(self.c, 'cleo_color_file_node_list', 'data'):
            self.file_nodes = self.c.config.getData('cleo_color_file_node_list')

        self.priority_colours = {
            1 : 'red',
            2 : 'orange',
            3 : 'yellow',
            4 : 'green',
            5 : 'background-colour'
        }

        for pri in self.priority_colours.iterkeys():
            if self.c.config.getColor('cleo_color_pri_'+str(pri)):
                self.priority_colours[pri] = self.c.config.getColor('cleo_color_pri_'+str(pri))

        self.red, self.green = ('red', 'green')
        for i in ('red', 'green'):
            if self.c.config.getColor('cleo_color_prog_'+i):
                self.__dict__[i] = self.c.config.getColor('cleo_color_prog_'+i)

        if c.frame and c.frame.tree and c.frame.tree.canvas:
            self.background_colour = c.frame.tree.canvas.cget('background')
        else:
            self.background_color = 'black'
        #@-<< define colors >>

        self.install_drawing_overrides()

        self.handlers = [
            ("draw-outline-text-box",self.draw),
            ("redraw-entire-outline",self.clear_canvas),
            ("iconrclick1",self.show_menu),
            ("close-frame",self.close),
        ]
        for i in self.handlers:
            g.registerHandler(i[0], i[1])

        self.loadAllIcons()
    #@+node:tbrown.20060903121429.17: *4* install_drawing_overrides
    def install_drawing_overrides (self):

        # g.pr("Cleo plugin: installing overrides for",self.c.shortFileName())

        tree = self.c.frame.tree # NOT tkGui.leoTkinterTree

        g.funcToMethod(self.setUnselectedHeadlineColors,tree)
        g.funcToMethod(self.setDisabledHeadlineColors,tree)
    #@+node:tbrown.20080303214305: *3* loadAllIcons
    def loadAllIcons(self):
        """Load icons to represent cleo state"""

        for p in self.c.all_positions():
            self.loadIcons(p)
    #@+node:tbrown.20080303232514: *3* loadIcons
    def loadIcons(self, p):
        com = self.c.editCommands
        allIcons = com.getIconList(p)
        icons = [i for i in allIcons if 'cleoIcon' not in i]
        pri = self.getat(p.v, 'priority')
        if pri: pri = int(pri)
        if pri in self.priorities:
            cleo_icon_path = self.c.config.getString('cleo_icon_path')
            if not cleo_icon_path:
                cleo_icon_path = 'cleo'  # relative to leo Icons dir
            iconDir = g.os_path_abspath(
              g.os_path_normpath(
                g.os_path_join(g.app.loadDir,"..","Icons")))
            com.appendImageDictToList(icons, iconDir,
                g.os_path_join(cleo_icon_path,self.priorities[pri]['icon']),
                2, on='vnode', cleoIcon='1', where=self.icon_location)
                # Icon location defaults to 'beforeIcon' unless cleo_icon_location global defined.
                # Example: @strings[beforeIcon,beforeHeadline] cleo_icon_location = beforeHeadline
                # Note: 'beforeBox' and 'afterHeadline' collide with other elements on the line.
            com.setIconList(p, icons)
        else:
            if len(allIcons) != len(icons):  # something to remove
                com.setIconList(p, icons)

    #@+node:tbrown.20060903121429.18: *3* close
    def close(self, tag, key):
        "unregister handlers on closing commander"

        if self.c != key['c']: return  # not our problem

        for i in self.handlers:
            g.unregisterHandler(i[0], i[1])
    #@+node:tbrown.20060903121429.19: *3* attributes...
    #@+at
    # These methods should really be part of vnode in accordance with the principles
    # of encapsulation and information hiding.
    # 
    # annotate was the previous name of this plugin, which is why the default values
    # for several keyword args is 'annotate'.
    #@+node:tbrown.20060903121429.20: *4* delUD
    def delUD (self,node,udict="annotate"):

        ''' Remove our dict from the node'''

        if hasattr(node,"unknownAttributes" ) and \
               node.unknownAttributes.has_key(udict):

            del node.unknownAttributes[udict]
    #@+node:tbrown.20060903121429.21: *4* hasUD
    def hasUD (self,node,udict="annotate"):

        ''' Return True if the node has an UD.'''

        # g.trace(node) # EKR: node had better not be a position!

        return (
            hasattr(node,"unknownAttributes") and
            node.unknownAttributes.has_key(udict) and
            type(node.unknownAttributes.get(udict)) == type({}) # EKR
        )
    #@+node:tbrown.20060903121429.22: *4* getUD
    #@+at no longer required, use getat()
    # 
    # def getUD (self,node,udict="annotate"):
    #     ''' Create or retrive the user dict'''
    # 
    #     if not hasattr(node,'unknownAttributes'):
    #         node.unknownAttributes = {}
    #     # Create a subdictionary for the private use of my plugin.
    #     d = node.unknownAttributes.get(udict)
    # 
    #     if d is None or type(d) != type({}): # EKR
    #         node.unknownAttributes[udict] = d = {}
    #     # read legacy files that wrote TkPickleVars to the file
    #     for ky,vl in d.iteritems():
    #         if type(vl) == self.typePickle:
    #             # g.es("cleo: converting old TkPickleVar attribute")
    #             d[ky] = vl.get()
    #     return d
    #@+node:tbrown.20060903174527: *4* getat
    def getat(self, node, attrib):
        "new attrbiute getter"

        if (not hasattr(node,'unknownAttributes') or
            not node.unknownAttributes.has_key("annotate") or
            not type(node.unknownAttributes["annotate"]) == type({}) or
            not node.unknownAttributes["annotate"].has_key(attrib)):

            if attrib == "priority":
                return 9999
            else:
                return ""

        x = node.unknownAttributes["annotate"][attrib]
        if isinstance(x, TkPickleVar):
            node.unknownAttributes["annotate"][attrib] = x.get()
            return x.get()
        else:
            return x
    #@+node:tbrown.20060903204409: *4* testDefault
    def testDefault(self, attrib, val):
        "return true if val is default val for attrib"

        # if type(val) == self.typePickle: val = val.get()
        # not needed as only dropEmpty would call with such a thing, and it checks first

        return attrib == "priority" and val == 9999 or val == ""
    #@+node:tbrown.20060903200946: *4* setat
    def setat(self, node, attrib, val):
        "new attrbiute setter"

        isDefault = self.testDefault(attrib, val)

        if (not hasattr(node,'unknownAttributes') or
            not node.unknownAttributes.has_key("annotate") or
            type(node.unknownAttributes["annotate"]) != type({})):
            # dictionary doesn't exist

            if isDefault:
                return  # don't create dict. for default value

            if not hasattr(node,'unknownAttributes'):  # node has no unknownAttributes
                node.unknownAttributes = {}
                node.unknownAttributes["annotate"] = {}
            else:  # our private dictionary isn't present
                if (not node.unknownAttributes.has_key("annotate") or
                    type(node.unknownAttributes["annotate"]) != type({})):
                    node.unknownAttributes["annotate"] = {}

            node.unknownAttributes["annotate"][attrib] = val

            return

        # dictionary exists

        node.unknownAttributes["annotate"][attrib] = val

        if isDefault:  # check if all default, if so drop dict.
            self.dropEmpty(node, dictOk = True)
    #@+node:tbrown.20060903204409.1: *4* dropEmptyAll
    def dropEmptyAll(self):
        "search whole tree for empty nodes"

        cnt = 0
        for p in self.c.all_positions(): 
            if self.dropEmpty(p.v): cnt += 1

        g.es("cleo: dropped %d empty dictionaries" % cnt)
    #@+node:tbrown.20060903204409.2: *4* dropEmpty
    def dropEmpty(self, node, dictOk = False):

        if (dictOk or
            hasattr(node,'unknownAttributes') and
            node.unknownAttributes.has_key("annotate") and
            type(node.unknownAttributes["annotate"]) == type({})):

            isDefault = True
            for ky, vl in node.unknownAttributes["annotate"].iteritems():
                if isinstance(vl, TkPickleVar):
                    node.unknownAttributes["annotate"][ky] = vl = vl.get()
                if not self.testDefault(ky, vl):
                    isDefault = False
                    break

            if isDefault:  # no non-defaults seen, drop the whole cleo dictionary
                del node.unknownAttributes["annotate"]
                self.c.setChanged(True)
                return True

        return False
    #@+node:tbrown.20060903121429.23: *3* safe_del
    def safe_del(self, d, k):
        "delete a key from a dict. if present"
        if d.has_key(k): del d[k]
    #@+node:tbrown.20060903121429.24: *3* colours...
    #@+node:tbrown.20060903121429.25: *4* remove_colours
    def remove_colours(self,v):

        self.setat(v, 'fg', '')
        self.setat(v, 'bg', '')
        self.safe_del(self.pickles, 'fg')
        self.safe_del(self.pickles, 'bg')
        self.c.redraw()
    #@+node:tbrown.20071008150126: *4* subtree_colours
    def subtree_colours(self,p):

        fg = self.getat(p.v, 'fg')
        bg = self.getat(p.v, 'bg')
        for n in p.subtree():
            self.setat(n.v, 'fg', fg)
            self.setat(n.v, 'bg', bg)
        self.c.redraw()
    #@+node:tbrown.20060912130940: *4* add_colour
    def add_colour(self):

        import tkColorChooser

        myColor = '#008000'
        myColor = tkColorChooser.askcolor(myColor)
        if myColor[0] == None:
            g.es("No colour selected")
            return

        myColor = "#%02x%02x%02x" % myColor[0]

        if not self.colours.count(myColor):
            self.colours.insert(0, myColor)
            g.es("Added %s to the colour list" % (myColor))
        else:
            g.es("%s already on the colour list" % (myColor))
    #@+node:tbrown.20060903121429.26: *4* custom_colours
    # use return values to set the colours so no need to muck around when loading up files.

    def custom_colours(self,v,node_is_selected):

        ''' Returns the vnodes custom colours if it has them '''

        fg, bg = None, None

        # XXX This is ugly and inefficient !!
        #@+<< auto headline colours >>
        #@+node:tbrown.20060903121429.27: *5* << auto headline colours >>
        # set bg of @file type of nodes
        h = v and v.h or ''

        for f in self.file_nodes:
            if h.startswith(f):
                bg = self.node_colours['file']

        # set bg of @ignore type of nodes
        if self.colorIgnore:
            if h.find("@ignore") == 0:
                bg = self.node_colours['Comments']
        #@-<< auto headline colours >>
        #@+<< node colours >>
        #@+node:tbrown.20060903121429.28: *5* << node colours >>
        # Node-based colouring --- bg only
        n = self.getat(v, 'node') # d.get('node')
        if n:
            bg = self.node_colours.get(n, bg)
        #@-<< node colours >>
        #@+<< archetype colours >>
        #@+node:tbrown.20060903121429.29: *5* << archetype colours >>
        # Archetype-based colouring --- fg only
        a = self.getat(v, 'archetype') # d.get('archetype')
        if a:
            fg = self.archetype_colours.get(a, fg)
        #@-<< archetype colours >>
        #@+<< arbitary colours >>
        #@+node:tbrown.20060903121429.30: *5* << arbitary colours >>
        # User defined colours overrides all
        fgv = self.getat(v, 'fg') # d.get('fg')
        if fgv:
            f = fgv
            if f:
                fg = f

        bgv = self.getat(v, 'bg') # d.get('bg')
        if bgv:
            b = bgv
            if b:
                bg = b
        #@-<< arbitary colours >>

        #g.pr("> (%s,%s) %s" % (fg,bg,v.h))

        return fg,bg
    #@+node:tbrown.20060903121429.31: *3* drawing...
    #@+node:tbrown.20060903121429.32: *4* redraw
    def redraw(self):
        "redraw after menu used"

        g.trace(g.callers())

        # IMPORTANT ASSUMPTION: called only after menu used

        # read updates from menu choice

        # Tk seems to use menu label when '' is used as value?
        # note, keys not present if coming via clear_all
        if self.pickles.has_key('node'):
            if self.pickles['node'].get() == 'CLEO_BLANK': self.pickles['node'].set('')
        if self.pickles.has_key('archetype'):
            if self.pickles['archetype'].get() == 'CLEO_BLANK': self.pickles['archetype'].set('')

        for ky, vl in self.pickles.iteritems():
            self.setat(self.pickleV, ky, vl.get())

        self.loadIcons(self.pickleP)

        self.clear_marks(self.c.frame.tree.canvas)
        self.update_project(self.pickleP)
        c = self.c
        c.setChanged(True)
        c.redraw_now()
    #@+node:tbrown.20060903121429.33: *4* clear_all
    def clear_all(self,v):

        self.delUD(v)
        self.pickles = {}
        self.redraw()
    #@+node:tbrown.20060903121429.34: *4* clear_canvas
    def clear_canvas(self,tag,key):
        "Remove all marks placed on canvas previously"

        if key.get("c") != self.c: return  # not out problem

        self.clear_marks(self.c.frame.tree.canvas)
    #@+node:tbrown.20060903121429.35: *4* clear_marks
    def clear_marks(self, canvas):
        "Remove all marks placed on canvas previously"

        for mark in self.marks:
            canvas.delete(mark)

        self.marks = []
    #@+node:tbrown.20060903121429.36: *4* draw box area
    #@+node:tbrown.20060903121429.37: *5* draw
    def draw (self,tag,key):

        ''' Redraws all the indicators for the markups of v '''

        if self.c != key['c']: return  # not our problem
        # point of order, Summary of Hooks doesn't list 'c' for 'draw-outline-text-box'

        v = key['p'].v

        if not self.hasUD(v):
            # colour='white'
            # self.draw_arrow(v,colour)
            # self.draw_tick(v)
            return None

        # priority = self.getat(v, 'priority')
        # colour = self.priority_colours.get(priority,False)
        # if colour:
        #     self.draw_arrow(v,colour)
        # if priority==self.donePriority:
        #     self.draw_tick(v)

        progress = self.getat(v, 'progress')
        if self.scaleProg != 0 and progress != '': 
            progWidth = self.progWidth
            if self.scaleProg == 2 and self.getat(v, 'time_req') != '':
                progWidth += self.getat(v, 'time_req') * self.extraProg
            self.draw_prog(v, float(progress)/100., progWidth)

        # Archetype are not drawn here
        return None
    #@+node:tbrown.20060903121429.39: *5* draw_box <1 'hours', 100%>
    def draw_box (self,v,color,canvas):

        c = self.c
        if v.isVisible(c):
            x, y = v.iconx, v.icony
            self.marks.append(
                canvas.create_rectangle(x,y,x+10,y+10,fill=color)
                )
    #@+node:tbrown.20060903121429.40: *5* draw_arrow
    # If too long can obscure +/- box

    def draw_arrow (self,v,colour='darkgreen'):

        c = self.c
        tree = c.frame.tree

        canvas = tree.canvas
        clear = colour == 'background-colour'

        if not clear:
            self.marks.append(canvas.create_line(v.iconx-10,v.icony+8,v.iconx+5,v.icony+8,
                arrow = "last", fill = colour, width = 4))
    #@+node:tbrown.20060903121429.41: *5* draw_tick
    def draw_tick (self,v,colour='salmon'):

        canvas = self.c.frame.tree.canvas

        # canvas.create_line(v.iconx+13-5,v.icony+8,v.iconx+13,v.icony+13,fill=colour,width=2)
        # canvas.create_line(v.iconx+13,v.icony+13,v.iconx+13+12,v.icony-2,fill=colour,width=2)

        # Define the 3 points of a check mark to allow quick adjustment.
        XpointA = v.iconx-15 + 3
        YpointA = v.icony + 8-2
        XpointB = v.iconx-7
        YpointB = v.icony + 13
        XpointC = v.iconx + 5
        YpointC = v.icony-2
        # draw the check-mark

        self.marks.append(
            canvas.create_line(XpointA,YpointA,XpointB,YpointB,fill=colour,width=2)
        )
        self.marks.append(
            canvas.create_line(XpointB,YpointB,XpointC,YpointC,fill=colour,width=2)
        )
    #@+node:tbrown.20060912215129: *5* draw_prog
    def draw_prog (self, v, prop, progWidth):

        canvas = self.c.frame.tree.canvas

        XpointA = v.iconx+1
        YpointA = v.icony-1

        XpointB = v.iconx+1+int(prop * progWidth)
        YpointB = v.icony-1

        XpointC = v.iconx+1+progWidth
        YpointC = v.icony-1

        self.marks.append(
            canvas.create_line(XpointA,YpointA,XpointB,YpointB,fill=self.green,width=2)
        )
        self.marks.append(
            canvas.create_line(XpointB,YpointB,XpointC,YpointC,fill=self.red,width=2)
        )
    #@+node:tbrown.20060903121429.42: *5* draw_invertedT
    def draw_invertedT (self,v,color,canvas):

        '''Draw the symbol for data.'''

        c = self.c
        if v.isVisible(c):

            x, y = v.iconx, v.icony ; bottom = y+13

            # Draw horizontal line.
            self.marks.append(   
                canvas.create_line(x,bottom,x+10,bottom,fill=color,width=2)
            )

            # Draw vertical line.
            self.marks.append(
                canvas.create_line(x+5,bottom-5,x+5,bottom,fill=color,width=2)
            )
    #@+node:tbrown.20060903121429.43: *5* draw_topT
    def draw_topT (self,v,color,canvas):

        '''Draw the symbol for interfaces.'''

        c = self.c
        if v.isVisible(c):

            x, y = v.iconx, v.icony ; topl = y 

            # Draw the horizontal line.
            self.marks.append(
                canvas.create_line(x,topl,x+10,topl,fill=color,width=2)
            )

            # Draw the vertical line.
            self.marks.append(
                canvas.create_line(x+5,topl,x+5,topl+15,fill=color,width=2)
            )
    #@+node:tbrown.20060903121429.44: *4* overrides of leoTkinterTree methods
    #@+node:tbrown.20060903121429.45: *5* setUnselectedHeadlineColors
    def setUnselectedHeadlineColors (self,p):

        # unlike handlers, override commands don't need to check self.c against other c
        c = self.c

        if hasattr(p,'edit_widget'):  #temporary cvs transitional code
            w = p.edit_widget()
        else:
            w = c.edit_widget(p)

        fg, bg = self.custom_colours(p.v,node_is_selected=False)

        fg = fg or c.config.getColor("headline_text_unselected_foreground_color") or 'black'
        bg = bg or c.config.getColor("headline_text_unselected_background_color") or 'white'

        try:
            w.configure(state="disabled",highlightthickness=0,fg=fg,bg=bg)
        except:
            g.es_exception()
    #@+node:tbrown.20060903121429.46: *5* setDisabledHeadlineColors
    def setDisabledHeadlineColors (self,p):

        c = self.c

        if hasattr(p,'edit_widget'):  #temporary cvs transitional code
            w = p.edit_widget()
        else:
            w = c.edit_widget(p)

        fg, bg = self.custom_colours(p.v,node_is_selected=True)

        fg = fg or c.config.getColor("headline_text_selected_foreground_color") or 'black'
        bg2 = c.config.getColor("headline_text_selected_background_color")
        bg = bg or bg2 or 'gray80'

        try:
            if bg != bg2:
                hl = c.config.getColor("headline_text_selected_highlight_color") or 'black'
                w.configure(state="disabled", highlightthickness=1, highlightbackground=hl, fg=fg, bg=bg)
            else:
                w.configure(state="disabled", highlightthickness=0, fg=fg, bg=bg)
        except:
            g.es_exception()
    #@+node:tbrown.20060903121429.47: *3* menus...
    #@+node:tbrown.20060903121429.48: *4* prep_pickle
    def prep_pickle(self, v, pkl, default = None):
        "prepare a TkPickleVar in self.pickles for a menu write back"

        self.pickles[pkl] = TkPickleVar()
        self.pickles[pkl].set(self.getat(v, pkl))
    #@+node:tbrown.20060903121429.49: *4* archetype_menu
    def archetype_menu(self,parent,p):

        self.prep_pickle(p.v, "archetype")

        menu = Tk.Menu(parent,tearoff=0,takefocus=1)

        for label,value in (
            ('Data/Description','Data'),
            ('Thing/Place','Thing'),
            ('Logic/Function','Logic'),
            ('Interface/Role','Interface'),
            ('Moment-Interval/Event Handler','Moment-Interval'),
            ('Other','CLEO_BLANK'),  # Tk seems to use menu label if '' used for value?
        ):
            menu.add_radiobutton(label=label,
                underline=0,command=self.redraw,
                variable=self.pickles['archetype'],value=value)

        parent.add_cascade(label='Code Archetypes',underline=6,menu=menu)

        return menu
    #@+node:tbrown.20060903121429.50: *4* colours_menu
    def colours_menu(self,parent, p):

        c = self.c
        self.prep_pickle(p.v, 'fg')
        self.prep_pickle(p.v, 'bg')

        for var in (self.pickles['fg'].get(), self.pickles['bg'].get()):
            if var and var != '' and var != 'Other' and not self.colours.count(var):
                self.colours.insert(0, var)
                g.es("Added %s to the colour list" % (var))

        for label,var in (('Foreground',self.pickles['fg']),('Background',self.pickles['bg'])):
            menu = Tk.Menu(parent,tearoff=0,takefocus=1)
            for color in self.colours:
                menu.add_radiobutton(label=color,
                    variable=var, value=color,
                    command=self.redraw)
            parent.add_cascade(label=label,underline=0,menu=menu)

        def cleoColorsMenuCallback():
            self.remove_colours(p.v)
        def cleoColorsMenuSubtree():
            self.subtree_colours(p)

        c.add_command(parent,label='Remove Colouring', underline=0,
            command=cleoColorsMenuCallback)

        c.add_command(parent,label='Colour subtree', underline=0,
            command=cleoColorsMenuSubtree)

        def cleoAddColorsMenuCallback():
            self.add_colour()

        c.add_command(parent,label='New Colour', underline=0,
            command=cleoAddColorsMenuCallback)
    #@+node:tbrown.20060903121429.51: *4* node menu
    def nodes_menu(self,parent,p):

        self.prep_pickle(p.v, 'node')

        menu = Tk.Menu(parent,tearoff=0,takefocus=1)

        for label,value in (
            ('@file','file'),
            ('Major Branch','Major Branch'),
            ('Feature/Concern','Feature'),
            ('Comments/@ignore','Comments'),
            ('Other','CLEO_BLANK'),  # Tk seems to use menu label if '' used for value?
        ):
            menu.add_radiobutton(label=label,underline=0,
                command=self.redraw,variable=self.pickles['node'],value=value)

        parent.add_cascade(label='Node types',underline=0,menu=menu)
    #@+node:tbrown.20061020145804: *4* left_priority_menu
    def left_priority_menu(self, menu, p):
        self.prep_pickle(p.v, 'priority', default=9999)
        for pri in self.priorities:
            value,label = pri, self.priorities[pri]['short']
            s = '%s' % (label)
            menu.add_radiobutton(
                label=s,variable=self.pickles['priority'],value=value,
                command=self.redraw,underline=0)
    #@+node:tbrown.20060903121429.52: *4* priority_menu
    def prikey(self, v):
        """key function for sorting by priority"""
        # getat returns 9999 for nodes without priority, so you'll only get -1
        # if a[1] is not a node.  Or even an object.

        try:
            pa = int(self.getat(v, 'priority'))
        except ValueError:
            pa = -1

        return pa

    def priSort(self):
        self.c.selectPosition(self.pickleP)
        self.c.sortSiblings(key=self.prikey)

    def childrenTodo(self):
        for p in self.pickleP.children():
            if self.getat(p.v, 'priority') != 9999: continue
            self.setat(p.v, 'priority', 19)
            self.loadIcons(p)
        self.c.redraw()

    def showDist(self):
        """show distribution of priority levels in subtree"""
        pris = {}
        for p in self.pickleP.subtree():
            pri = int(self.getat(p.v, 'priority'))
            if pri not in pris:
                pris[pri] = 1
            else:
                pris[pri] += 1
        pris = sorted([(k,v) for k,v in pris.iteritems()]) 
        for pri in pris:
            if pri[0] in self.priorities:
                g.es('%s\t%d\t%s' % (self.priorities[pri[0]]['short'], pri[1],
                    self.priorities[pri[0]]['long']))

    def reclassify(self):
        """change priority codes"""

        g.es('\n Current distribution:')
        self.showDist()
        dat = {}
        for end in 'from', 'to':
            x0 = g.app.gui.runAskOkCancelStringDialog(
                self.c,'Reclassify priority' ,'%s priorities (1-7,19)' % end.upper())
            try:
                x0 = [int(i) for i in x0.replace(',',' ').split()
                      if int(i) in self.todo_priorities]
            except:
                g.es('Not understood, no action')
                return
            if not x0:
                g.es('No action')
                return
            dat[end] = x0

        if len(dat['from']) != len(dat['to']):
            g.es('Unequal list lengths, no action')
            return

        cnt = 0
        for p in self.pickleP.subtree():
            pri = int(self.getat(p.v, 'priority'))
            if pri in dat['from']:
                self.setat(p.v, 'priority', dat['to'][dat['from'].index(pri)])
                self.loadIcons(p)
                cnt += 1
        g.es('\n%d priorities reclassified, new distribution:' % cnt)
        self.showDist()
        if cnt:
            self.c.redraw_now()

    def priority_menu(self,parent,p):

        # done already in left_priority menu
        # self.prep_pickle(p.v, 'priority', default=9999)

        c = self.c
        menu = Tk.Menu(parent,tearoff=0,takefocus=1)

        parent.add_cascade(label='Priority', menu=menu,underline=1)

        # Instead of just redraw, set changed too.
        for pri in self.priorities:
            value,label = pri, self.priorities[pri]['long']
            s = '%d %s' % (value,label)
            menu.add_radiobutton(
                label=s,variable=self.pickles['priority'],value=value,
                command=self.redraw,underline=0)

        menu.add_separator()

        c.add_command(menu,label='Sort',
            command=self.priSort, underline=0)
        c.add_command(menu,label='Children -> To do',
            command=self.childrenTodo, underline=0)
        c.add_command(menu,label='Show distribution',
            command=self.showDist, underline=0)
        c.add_command(menu,label='Reclassify',
            command=self.reclassify, underline=0)

        menu.add_separator()

        c.add_command(menu,label='Clear',
            command=lambda p=p:self.priority_clear(p.v),underline=0)

        return menu
    #@+node:tbrown.20060912220630: *4* progress_menu
    def progress_menu(self,parent,p):

        self.prep_pickle(p.v, 'progress')

        menu = Tk.Menu(parent,tearoff=0,takefocus=1)

        parent.add_cascade(label='Progress', menu=menu,underline=1)

        # Instead of just redraw, set changed too.
        for value in range(0,11):
            s = '%d%%' % (value*10)
            menu.add_radiobutton(
                label=s,variable=self.pickles['progress'],value=value*10,
                command=self.redraw,underline=0)

        menu.add_separator()

        c = self.c

        c.add_command(menu,label='Clear',
            command=lambda p=p:self.progress_clear(p.v),underline=0)

        def toggle_scaling():
            self.scaleProg = (self.scaleProg+1) % 3
            self.redraw()

        c.add_command(menu,label='Toggle progress scaling',
            underline=0,command=toggle_scaling)

        return menu
    #@+node:tbrown.20060913212017: *4* time_menu
    def time_menu(self,parent,p):

        c = self.c ; v = p.v

        menu = Tk.Menu(parent,tearoff=0,takefocus=1)

        lab = 'Time'
        if self.getat(v, 'time_req') != '':
            lab += ' ('+str(self.getat(v, 'time_req'))+')'
        parent.add_cascade(label=lab, menu=menu,underline=1)

        lab = 'Set time required'
        if self.getat(v, 'time_req') != '':
            lab += ' ('+str(self.getat(v, 'time_req'))+')'
        c.add_command(menu,label=lab,
            underline=0,command=lambda:self.set_time_req(p))
        c.add_command(menu,label='Clear time required',
            underline=0,command=lambda:self.clear_time_req(p))

        c.add_command(menu,label='Show times',
            underline=0,command=lambda:self.show_times(p, show=True))
        c.add_command(menu,label='Hide times',
            underline=0,command=lambda:self.show_times(p, show=False))

        def local_recalc():
            self.recalc_time(p)
            self.pickles['progress'].set(self.getat(v, 'progress'))
            self.redraw()

        c.add_command(menu,label='Re-calc. time required',
            underline=0,command=local_recalc)

        def local_clear():
            self.recalc_time(p, clear=True)
            self.pickles['progress'].set(self.getat(v, 'progress'))
            self.redraw()

        c.add_command(menu,label='Clear derived times',
            underline=0,command=local_clear)

        return menu
    #@+node:tbrown.20060903121429.53: *4* show_menu
    def show_menu (self,tag,k):

        g.app.gui.killPopupMenu()

        if k['c'] != self.c: return  # not our problem

        p = k['p']
        self.c.selectPosition(p)
        v = k['p'].v ## EKR

        self.pickles = {}  # clear dict. of TkPickleVars
        self.pickleV = v
        self.pickleP = p.copy()

        # Create the menu.
        menu = Tk.Menu(None,tearoff=0,takefocus=0)

        self.left_priority_menu(menu, p)

        c = self.c

        c.add_command(menu,label='T',
            underline=0,command=lambda:self.set_time_req(p))

        c.add_command(menu,label='Find next todo', columnbreak=1,
            underline=0,command=lambda:self.find_todo(p))
        self.priority_menu(menu,p)
        self.progress_menu(menu,p)
        self.time_menu(menu,p)
        self.archetype_menu(menu, p)
        self.nodes_menu(menu,p)

        menu.add_separator()

        self.colours_menu(menu,p)
        # fonts_menu(menu,p)
        menu.add_separator()
        c.add_command(menu,label='Clear All for node',
            underline=0,command=lambda:self.clear_all(v))
        c.add_command(menu,label='Flush empty cleo attribs.',
            underline=0,command=self.dropEmptyAll)

        # Show the menu.
        event = k['event']
        g.app.gui.postPopupMenu(self.c, menu, event.x_root,event.y_root)

        return 'break' # EKR: Prevent other right clicks.
    #@+node:tbrown.20060903121429.54: *3* priority_clear
    def priority_clear(self,v):

        self.setat(v, 'priority', 9999)
        self.safe_del(self.pickles, 'priority')
        self.redraw()
    #@+node:tbrown.20060912221139: *3* progress_clear
    def progress_clear(self,v):

        self.setat(v, 'progress', '')
        self.safe_del(self.pickles, 'progress')
        self.redraw()
    #@+node:tbrown.20060913153851: *3* set_time_req
    def set_time_req(self,p):
        v = p.v
        tkSimpleDialog = g.importExtension('tkSimpleDialog',pluginName=__name__)
        initialvalue = str(self.time_init)
        if self.getat(v, 'time_req') != '':
            initialvalue = self.getat(v, 'time_req')
        prompt = '%s required' % self.time_name
        tr = tkSimpleDialog.askfloat(prompt, prompt, parent = self.c.frame.tree.canvas,
                                     initialvalue = str(initialvalue))

        if tr == None: return

        self.setat(v, 'time_req', tr)

        if self.getat(v, 'progress') == '':
            self.setat(v, 'progress', 0)
            self.pickles['progress'].set(0)

        self.redraw()
    #@+node:tbrown.20060913204451: *3* show_times
    def show_times(self, p, show=False):

        import re

        def rnd(x): return re.sub('.0$', '', '%.1f' % x)

        for nd in p.self_and_subtree():
            if hasattr(nd, 'setHeadStringOrHeadline'):  # temp. cvs transition code
                nd.setHeadStringOrHeadline(re.sub(' <[^>]*>$', '', nd.h))
            else:
                self.c.setHeadString(nd, re.sub(' <[^>]*>$', '', nd.h))
                # nd.setHeadString(re.sub(' <[^>]*>$', '', nd.h))
            if show:
                tr = self.getat(nd.v, 'time_req')
                pr = self.getat(nd.v, 'progress')
                try: pr = float(pr)
                except: pr = ''
                if tr != '' or pr != '':
                    ans = ' <'
                    if tr != '':
                        if pr == '' or pr == 0 or pr == 100:
                            ans += rnd(tr) + ' ' + self.time_name
                        else:
                            ans += '%s+%s=%s %s' % (rnd(pr/100.*tr), rnd((1-pr/100.)*tr), rnd(tr), self.time_name)
                        if pr != '': ans += ', '
                    if pr != '':
                        ans += rnd(pr) + '%'  # pr may be non-integer if set by recalc_time
                    ans += '>'
                    if hasattr(nd, 'setHeadStringOrHeadline'):  # temp. cvs transition code
                        nd.setHeadStringOrHeadline(nd.h+ans)
                    else:
                        self.c.setHeadString(nd, nd.h+ans)
    #@+node:tbrown.20060913133338: *3* recalc_time
    def recalc_time(self, p, clear=False):
        v = p.v
        time_totl = None
        time_done = None

        # get values from children, if any
        for cn in p.children():
            ans = self.recalc_time(cn.copy(), clear)
            if time_totl == None:
                time_totl = ans[0]
            else:
                if ans[0] != None: time_totl += ans[0]

            if time_done == None:
                time_done = ans[1]
            else:
                if ans[1] != None: time_done += ans[1]

        if time_totl != None:  # some value returned

            if clear:  # then we should just clear our values
                self.setat(v, 'progress', '')
                self.setat(v, 'time_req', '')
                return (time_totl, time_done)

            if time_done != None:  # some work done
                # can't round derived progress without getting bad results form show_times
                pr = float(time_done) / float(time_totl) * 100.
                self.setat(v, 'progress', pr)
            else:
                self.setat(v, 'progress', 0)
            self.setat(v, 'time_req', time_totl)
        else:  # no values from children, use own
            tr = self.getat(v, 'time_req')
            pr = self.getat(v, 'progress')
            if tr != '':
                time_totl = tr
                if pr != '':
                    time_done = float(pr) / 100. * tr
                else:
                    self.setat(v, 'progress', 0)

        # if time_totl != None:
        #     self.setat(v, 'time_req', time_totl)
        #     if time_done != None:
        #         self.setat(v, 'progress', int(float(time_done) / float(time_totl) * 100.))
        #     else:
        #         self.setat(v, 'progress', 0)

        # import sys
        # s0, s1 = (time_totl, time_done)
        # if not s0: s0 = 0
        # if not s1: s1 = 0
        # sys.stderr.write('%s %g %g\n' % (p.h, float(s0), float(s1)))
        return (time_totl, time_done)
    #@+node:tbrown.20060913104504.1: *3* clear_time_req
    def clear_time_req(self,p):

        v = p.v
        self.setat(v, 'time_req', '')
        self.safe_del(self.pickles, 'time_req')
        self.redraw()
    #@+node:tbrown.20060914134553.376: *3* update_project
    def update_project(self, p):
        """Find highest parent with '@project' in headline and run recalc_time
        and maybe show_times (if headline has '@project time')"""

        project = None

        for nd in p.self_and_parents():
            if nd.h.find('@project') > -1:
                project = nd.copy()

        if project:
            self.recalc_time(project)
            if project.h.find('@project time') > -1:
                self.show_times(project, show=True)
    #@+node:tbrown.20060919160306: *3* find_todo
    def find_todo(self, p, stage = 0):
        """Recursively find the next todo"""

        # search is like XPath 'following' axis, all nodes after p in document order.
        # returning True should always propogate all the way back up to the top
        # stages: 0 - user selected start node, 1 - searching siblings, parents siblings, 2 - searching children

        if not p: return True  # not required - safety net

        # see if this node is a todo
        if stage != 0 and self.getat(p.v, 'priority') in self.todo_priorities:
            if p.getParent(): 
                self.c.selectPosition(p.getParent())
                self.c.expandNode()
            self.c.selectPosition(p)
            self.c.redraw()
            return True

        for nd in p.children():
            if self.find_todo(nd, stage = 2): return True

        if stage < 2 and p.getNext():
            if self.find_todo(p.getNext(), stage = 1): return True

        if stage < 2 and p.getParent() and p.getParent().getNext():
            if self.find_todo(p.getParent().getNext(), stage = 1): return True

        if stage == 0: g.es("None found")

        return False
    #@-others
#@-others
#@-leo
