#@+leo-ver=4-thin
#@+node:tbrown.20090119215428.2:@thin todo.py
#@<< docstring >>
#@+node:tbrown.20090119215428.3:<< docstring >>
'''todo.py  -- ToDo and simple task management for leo

(todo is the Qt version of the Tk cleo plugin)

todo adds time required, progress and priority settings for nodes.
With the @project tag a branch can display progress and time
required with dynamic hierachical updates.

For full documentation see:

  - http://leo.zwiki.org/ToDo 
  - http://leo.zwiki.org/tododoc.html
'''
#@nonl
#@-node:tbrown.20090119215428.3:<< docstring >>
#@nl

#@@language python
#@@tabwidth -4

#@<< imports >>
#@+node:tbrown.20090119215428.4:<< imports >>
import leo.core.leoGlobals as g

if g.app.gui.guiName() == "qt":
    import leo.core.leoPlugins as leoPlugins
    import os

    from PyQt4 import QtCore, QtGui, uic
    Qt = QtCore.Qt
#@-node:tbrown.20090119215428.4:<< imports >>
#@nl
__version__ = "0.30"
#@<< version history >>
#@+node:tbrown.20090119215428.5:<< version history >>
#@@killcolor

#@+at 
#@nonl
# Use and distribute under the same terms as leo itself.
# 
# 0.30 TNB
#   - fork from cleo.py to todo.py
#   - Qt interface in a tab
#@-at
#@-node:tbrown.20090119215428.5:<< version history >>
#@nl

#@+others
#@+node:tbrown.20090119215428.6:init
def init():

    if g.app.gui.guiName() != "qt":
        print 'todo.py plugin not loading because gui is not Qt'
        return False

    leoPlugins.registerHandler('after-create-leo-frame',onCreate)
    # can't use before-create-leo-frame because Qt dock's not ready
    g.plugin_signon(__name__)

    return True

#@-node:tbrown.20090119215428.6:init
#@+node:tbrown.20090119215428.7:onCreate
def onCreate (tag,key):

    c = key.get('c')

    todoController(c)
#@-node:tbrown.20090119215428.7:onCreate
#@+node:tbrown.20090119215428.8:class todoQtUI
if g.app.gui.guiName() == "qt":
    class cleoQtUI(QtGui.QWidget):

        def __init__(self, owner):

            self.owner = owner

            QtGui.QWidget.__init__(self)
            uiPath = g.os_path_join(g.app.leoDir, 'plugins', 'ToDo.ui')
            form_class, base_class = uic.loadUiType(uiPath)
            self.owner.c.frame.log.createTab('Task', widget = self) 
            self.UI = form_class()
            self.UI.setupUi(self)

            u = self.UI
            o = self.owner

            self.menu = QtGui.QMenu()
            self.menu.addAction('Find next ToDo', o.find_todo)
            m = self.menu.addMenu("Priority")
            m.addAction('Sort', o.priSort)
            m.addAction('Mark children todo', o.childrenTodo)
            m.addAction('Show distribution', o.showDist)
            m.addAction('Redistribute', o.reclassify)
            m = self.menu.addMenu("Time")
            m.addAction('Show times', lambda:o.show_times(show=True))
            m.addAction('Hide times', lambda:o.show_times(show=False))
            m.addAction('Re-calc. derived times', o.local_recalc)
            m.addAction('Clear derived times', o.local_clear)
            m = self.menu.addMenu("Misc.")
            m.addAction('Clear all todo icons', lambda:o.loadAllIcons(clear=True))
            m.addAction('Show all todo icons', o.loadAllIcons)
            m.addAction('Clear todo from node', o.clear_all)
            m.addAction('Clear todo from subtree', lambda:o.clear_all(recurse=True))
            m.addAction('Clear todo from all', lambda:o.clear_all(all=True))
            u.butMenu.setMenu(self.menu)

            self.connect(u.butHelp, QtCore.SIGNAL("clicked()"), o.showHelp)

            self.connect(u.butClrProg, QtCore.SIGNAL("clicked()"),
                o.progress_clear)
            self.connect(u.butClrTime, QtCore.SIGNAL("clicked()"),
                o.clear_time_req)
            self.connect(u.butPriClr, QtCore.SIGNAL("clicked()"),
                o.priority_clear)

            # if live update is too slow change valueChanged(*) to editingFinished()
            self.connect(u.spinTime, QtCore.SIGNAL("valueChanged(double)"),
                lambda v: o.set_time_req(val=u.spinTime.value()))
            self.connect(u.spinProg, QtCore.SIGNAL("valueChanged(int)"),
                lambda v: o.set_progress(val=u.spinProg.value()))

            for but in ["butPri1", "butPri6", "butPriChk", "butPri2",
                "butPri4", "butPri5", "butPri8", "butPri9", "butPri0",
                "butPriToDo", "butPriXgry", "butPriBang", "butPriX",
                "butPriQuery", "butPriBullet", "butPri7", 
                "butPri3"]:

                w = getattr(u, but)
                pri, ok = w.property('priority').toInt()
                def setter(pri=pri): o.setPri(pri)
                self.connect(w, QtCore.SIGNAL("clicked()"), setter)

        def setProgress(self, prgr):
            self.UI.spinProg.blockSignals(True)
            self.UI.spinProg.setValue(prgr)
            self.UI.spinProg.blockSignals(False)
        def setTime(self, timeReq):
            self.UI.spinTime.blockSignals(True)
            self.UI.spinTime.setValue(timeReq)
            self.UI.spinTime.blockSignals(False)
#@-node:tbrown.20090119215428.8:class todoQtUI
#@+node:tbrown.20090119215428.9:class todoController
class todoController:

    '''A per-commander class that manages tasks.'''

    #@    @+others
    #@+node:tbrown.20090119215428.10:priority table
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
    #@-node:tbrown.20090119215428.10:priority table
    #@+node:tbrown.20090119215428.11:birth
    def __init__ (self,c):

        self.c = c
        c.cleo = self
        self.donePriority = 100
        #X self.smiley = None
        self.redrawLevels = 0

        #@    << set / read default values >>
        #@+node:tbrown.20090119215428.12:<< set / read default values >>
        self.time_name = 'days'
        if c.config.getString('todo_time_name'):
            self.time_name = c.config.getString('todo_time_name')

        self.icon_location = 'beforeIcon'
        if c.config.getString('todo_icon_location'):
            self.icon_location = c.config.getString('todo_icon_location')

        self.prog_location = 'beforeHeadline'
        if c.config.getString('todo_prog_location'):
            self.prog_location = c.config.getString('todo_prog_location')

        self.icon_order = 'pri-first'
        if c.config.getString('todo_icon_order'):
            self.icon_order = c.config.getString('todo_icon_order')
        #@-node:tbrown.20090119215428.12:<< set / read default values >>
        #@nl

        self.handlers = [("close-frame",self.close)]

        # chdir so the Icons can be located
        owd = os.getcwd()
        os.chdir(os.path.split(__file__)[0])
        self.ui = cleoQtUI(self)
        os.chdir(owd)
        leoPlugins.registerHandler('select3', self.updateUI)
        leoPlugins.registerHandler('save2', self.loadAllIcons)

        for i in self.handlers:
            leoPlugins.registerHandler(i[0], i[1])

        self.loadAllIcons()
    #@-node:tbrown.20090119215428.11:birth
    #@+node:tbrown.20090119215428.13:redrawer
    def redrawer(fn):
        """decorator for methods which create the need for a redraw"""
        def new(self, *args, **kargs):
            self.redrawLevels += 1
            try:
                ans = fn(self,*args, **kargs)
            finally:
                self.redrawLevels -= 1

                if self.redrawLevels == 0:
                    self.redraw()

            return ans
        return new
    #@-node:tbrown.20090119215428.13:redrawer
    #@+node:tbrown.20090119215428.14:projectChanger
    def projectChanger(fn):
        """decorator for methods which change projects"""
        def new(self, *args, **kargs):
            ans = fn(self,*args, **kargs)
            self.update_project()
            return ans
        return new
    #@nonl
    #@-node:tbrown.20090119215428.14:projectChanger
    #@+node:tbrown.20090119215428.15:loadAllIcons
    @redrawer
    def loadAllIcons(self, tag=None, k=None, clear=None):
        """Load icons to represent cleo state"""

        for p in self.c.allNodes_iter():
            self.loadIcons(p, clear=clear)
    #@-node:tbrown.20090119215428.15:loadAllIcons
    #@+node:tbrown.20090119215428.16:loadIcons
    @redrawer
    def loadIcons(self, p, clear=False):

        com = self.c.editCommands
        allIcons = com.getIconList(p)
        icons = [i for i in allIcons if 'cleoIcon' not in i]

        if clear:
            iterations = []
        else:
            iterations = [True, False]

        for which in iterations:

            if which == (self.icon_order == 'pri-first'):
                pri = self.getat(p.v, 'priority')
                if pri: pri = int(pri)
                if pri in self.priorities:
                    iconDir = g.os_path_abspath(
                      g.os_path_normpath(
                        g.os_path_join(g.app.loadDir,"..","Icons")))
                    com.appendImageDictToList(icons, iconDir,
                        g.os_path_join('cleo',self.priorities[pri]['icon']),
                        2, on='vnode', cleoIcon='1', where=self.icon_location)
                        # Icon location defaults to 'beforeIcon' unless cleo_icon_location global defined.
                        # Example: @strings[beforeIcon,beforeHeadline] cleo_icon_location = beforeHeadline
                    com.setIconList(p, icons)
            else:

                prog = self.getat(p.v, 'progress')
                if prog is not '':
                    prog = int(prog)
                    use = prog//10*10
                    use = 'prg%03d.png' % use

                    iconDir = g.os_path_abspath(
                      g.os_path_normpath(
                        g.os_path_join(g.app.loadDir,"..","Icons")))

                    com.appendImageDictToList(icons, iconDir,
                        g.os_path_join('cleo',use),
                        2, on='vnode', cleoIcon='1', where=self.prog_location)
                    com.setIconList(p, icons)

        if len(allIcons) != len(icons):  # something to add / remove
            com.setIconList(p, icons)

    #@-node:tbrown.20090119215428.16:loadIcons
    #@+node:tbrown.20090119215428.17:close
    def close(self, tag, key):
        "unregister handlers on closing commander"

        if self.c != key['c']: return  # not our problem

        for i in self.handlers:
            leoPlugins.unregisterHandler(i[0], i[1])
    #@-node:tbrown.20090119215428.17:close
    #@+node:tbrown.20090119215428.18:showHelp
    def showHelp(self):
        g.es('Check the Plugins menu todo entry')
    #@nonl
    #@-node:tbrown.20090119215428.18:showHelp
    #@+node:tbrown.20090119215428.19:attributes...
    #@+at
    # annotate was the previous name of this plugin, which is why the default 
    # values
    # for several keyword args is 'annotate'.
    #@-at
    #@nonl
    #@+node:tbrown.20090119215428.20:delUD
    def delUD (self,node,udict="annotate"):

        ''' Remove our dict from the node'''

        if (hasattr(node,"unknownAttributes" )
            and node.unknownAttributes.has_key(udict)):

            del node.unknownAttributes[udict]
    #@-node:tbrown.20090119215428.20:delUD
    #@+node:tbrown.20090119215428.21:hasUD
    def hasUD (self,node,udict="annotate"):

        ''' Return True if the node has an UD.'''

        return (
            hasattr(node,"unknownAttributes") and
            node.unknownAttributes.has_key(udict) and
            type(node.unknownAttributes.get(udict)) == type({}) # EKR
        )
    #@nonl
    #@-node:tbrown.20090119215428.21:hasUD
    #@+node:tbrown.20090119215428.22:getat
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
        return x
    #@nonl
    #@-node:tbrown.20090119215428.22:getat
    #@+node:tbrown.20090119215428.23:testDefault
    def testDefault(self, attrib, val):
        "return true if val is default val for attrib"

        return attrib == "priority" and val == 9999 or val == ""
    #@nonl
    #@-node:tbrown.20090119215428.23:testDefault
    #@+node:tbrown.20090119215428.24:setat
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
    #@-node:tbrown.20090119215428.24:setat
    #@+node:tbrown.20090119215428.25:dropEmpty
    def dropEmpty(self, node, dictOk = False):

        if (dictOk or
            hasattr(node,'unknownAttributes') and
            node.unknownAttributes.has_key("annotate") and
            type(node.unknownAttributes["annotate"]) == type({})):

            isDefault = True
            for ky, vl in node.unknownAttributes["annotate"].iteritems():

                if not self.testDefault(ky, vl):
                    isDefault = False
                    break

            if isDefault:  # no non-defaults seen, drop the whole cleo dictionary
                del node.unknownAttributes["annotate"]
                self.c.setChanged(True)
                return True

        return False
    #@-node:tbrown.20090119215428.25:dropEmpty
    #@+node:tbrown.20090119215428.26:safe_del
    def safe_del(self, d, k):
        "delete a key from a dict. if present"
        if d.has_key(k): del d[k]
    #@nonl
    #@-node:tbrown.20090119215428.26:safe_del
    #@-node:tbrown.20090119215428.19:attributes...
    #@+node:tbrown.20090119215428.27:drawing...
    #@+node:tbrown.20090119215428.28:redraw
    def redraw(self):

        self.updateUI()
        self.c.redraw_now()
    #@-node:tbrown.20090119215428.28:redraw
    #@+node:tbrown.20090119215428.29:clear_all
    @redrawer
    def clear_all(self, recurse=False, all=False):

        if all:
            what = self.c.allNodes_iter
        elif recurse:
            what = self.c.currentPosition().self_and_subtree_iter
        else:
            what = iter([self.c.currentPosition()])

        for p in what():
            self.delUD(p.v)
            self.loadIcons(p)
            self.show_times(p)

    #@-node:tbrown.20090119215428.29:clear_all
    #@-node:tbrown.20090119215428.27:drawing...
    #@+node:tbrown.20090119215428.30:Progress/time/project...
    #@+node:tbrown.20090119215428.31:progress_clear
    @redrawer
    @projectChanger
    def progress_clear(self,v=None):

        self.setat(self.c.currentPosition().v, 'progress', '')
    #@-node:tbrown.20090119215428.31:progress_clear
    #@+node:tbrown.20090119215428.32:set_progress
    @redrawer
    @projectChanger
    def set_progress(self,p=None, val=None):
        if p is None:
            p = self.c.currentPosition()
        v = p.v

        if val == None: return

        self.setat(v, 'progress', val)
    #@-node:tbrown.20090119215428.32:set_progress
    #@+node:tbrown.20090119215428.33:set_time_req
    @redrawer
    @projectChanger
    def set_time_req(self,p=None, val=None):
        if p is None:
            p = self.c.currentPosition()
        v = p.v

        if val == None: return

        self.setat(v, 'time_req', val)

        if self.getat(v, 'progress') == '':
            self.setat(v, 'progress', 0)
    #@-node:tbrown.20090119215428.33:set_time_req
    #@+node:tbrown.20090119215428.34:show_times
    @redrawer
    def show_times(self, p=None, show=False):

        import re

        def rnd(x): return re.sub('.0$', '', '%.1f' % x)

        if p is None:
            p = self.c.currentPosition()

        for nd in p.self_and_subtree_iter():
            self.c.setHeadString(nd, re.sub(' <[^>]*>$', '', nd.headString()))

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

                if show:
                    self.c.setHeadString(nd, nd.headString()+ans)
                self.loadIcons(nd)  # update progress icon

    #@-node:tbrown.20090119215428.34:show_times
    #@+node:tbrown.20090119215428.35:recalc_time
    def recalc_time(self, p=None, clear=False):

        if p is None:
            p = self.c.currentPosition()

        v = p.v
        time_totl = None
        time_done = None

        # get values from children, if any
        for cn in p.children_iter():
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

        return (time_totl, time_done)
    #@-node:tbrown.20090119215428.35:recalc_time
    #@+node:tbrown.20090119215428.36:clear_time_req
    @redrawer
    @projectChanger
    def clear_time_req(self, p=None):

        if p is None:
            p = self.c.currentPosition()
        v = p.v
        self.setat(v, 'time_req', '')
    #@-node:tbrown.20090119215428.36:clear_time_req
    #@+node:tbrown.20090119215428.37:update_project
    @redrawer
    def update_project(self, p=None):
        """Find highest parent with '@project' in headline and run recalc_time
        and maybe show_times (if headline has '@project time')"""

        if p is None:
            p = self.c.currentPosition()
        project = None

        for nd in p.self_and_parents_iter():
            if nd.headString().find('@project') > -1:
                project = nd.copy()

        if project:
            self.recalc_time(project)
            if project.headString().find('@project time') > -1:
                self.show_times(project, show=True)
            else:
                self.show_times(p, show=True)
        else:
            self.show_times(p, show=False)
    #@-node:tbrown.20090119215428.37:update_project
    #@+node:tbrown.20090119215428.38:local_recalc
    @redrawer
    def local_recalc(self, p=None):
        self.recalc_time(p)
    #@-node:tbrown.20090119215428.38:local_recalc
    #@+node:tbrown.20090119215428.39:local_clear
    @redrawer
    def local_clear(self, p=None):
        self.recalc_time(p, clear=True)
    #@-node:tbrown.20090119215428.39:local_clear
    #@-node:tbrown.20090119215428.30:Progress/time/project...
    #@+node:tbrown.20090119215428.40:ToDo icon related...
    #@+node:tbrown.20090119215428.41:childrenTodo
    @redrawer
    def childrenTodo(self, p=None):
        if p is None:
            p = self.c.currentPosition()
        for p in p.children_iter():
            if self.getat(p.v, 'priority') != 9999: continue
            self.setat(p.v, 'priority', 19)
            self.loadIcons(p)
    #@nonl
    #@-node:tbrown.20090119215428.41:childrenTodo
    #@+node:tbrown.20090119215428.42:find_todo
    @redrawer
    def find_todo(self, p=None, stage = 0):
        """Recursively find the next todo"""

        # search is like XPath 'following' axis, all nodes after p in document order.
        # returning True should always propogate all the way back up to the top
        # stages: 0 - user selected start node, 1 - searching siblings, parents siblings, 2 - searching children

        if p is None:
            p = self.c.currentPosition()

        # see if this node is a todo
        if stage != 0 and self.getat(p.v, 'priority') in self.todo_priorities:
            if p.getParent(): 
                self.c.selectPosition(p.getParent())
                self.c.expandNode()
            self.c.selectPosition(p)
            return True

        for nd in p.children_iter():
            if self.find_todo(nd, stage = 2): return True

        if stage < 2 and p.getNext():
            if self.find_todo(p.getNext(), stage = 1): return True

        if stage < 2 and p.getParent() and p.getParent().getNext():
            if self.find_todo(p.getParent().getNext(), stage = 1): return True

        if stage == 0: g.es("None found")

        return False
    #@-node:tbrown.20090119215428.42:find_todo
    #@+node:tbrown.20090119215428.43:pricmp
    def pricmp(self, a, b):
        """cmp function for sorting by priority, a and b are (headstring,v)"""
        # getat returns 9999 for nodes without priority, so you'll only get -1
        # if a[1] is not a node.  Or even an object.

        try:
            pa = int(self.getat(a[1], 'priority'))
        except:
            pa = -1
        try:
            pb = int(self.getat(b[1], 'priority'))
        except:
            pb = -1

        return cmp(pa,pb)
    #@nonl
    #@-node:tbrown.20090119215428.43:pricmp
    #@+node:tbrown.20090119215428.44:priority_clear
    @redrawer
    def priority_clear(self,v=None):

        if v is None:
            v = self.c.currentPosition().v
        self.setat(v, 'priority', 9999)
        self.loadIcons(self.c.currentPosition())
    #@-node:tbrown.20090119215428.44:priority_clear
    #@+node:tbrown.20090119215428.45:priSort
    @redrawer
    def priSort(self, p=None):
        if p is None:
            p = self.c.currentPosition()
        self.c.selectPosition(p)
        self.c.sortSiblings(cmp=self.pricmp)
    #@nonl
    #@-node:tbrown.20090119215428.45:priSort
    #@+node:tbrown.20090119215428.46:reclassify
    @redrawer
    def reclassify(self, p=None):
        """change priority codes"""

        if p is None:
            p = self.c.currentPosition()
        g.es('\n Current distribution:')
        self.showDist()
        dat = {}
        for end in 'from', 'to':
            if Qt:
                x0,ok = QtGui.QInputDialog.getText(None, 'Reclassify priority' ,'%s priorities (1-9,19)'%end)
                if not ok:
                    x0 = None
                else:
                    x0 = str(x0)
            else:
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
        for p in p.subtree_iter():
            pri = int(self.getat(p.v, 'priority'))
            if pri in dat['from']:
                self.setat(p.v, 'priority', dat['to'][dat['from'].index(pri)])
                self.loadIcons(p)
                cnt += 1
        g.es('\n%d priorities reclassified, new distribution:' % cnt)
        self.showDist()
    #@nonl
    #@-node:tbrown.20090119215428.46:reclassify
    #@+node:tbrown.20090119215428.47:setPri
    @redrawer
    def setPri(self,pri):
        p = self.c.currentPosition()
        self.setat(p.v, 'priority', pri)
        self.loadIcons(p)
    #@-node:tbrown.20090119215428.47:setPri
    #@+node:tbrown.20090119215428.48:showDist
    def showDist(self, p=None):
        """show distribution of priority levels in subtree"""
        if p is None:
            p = self.c.currentPosition()
        pris = {}
        for p in p.subtree_iter():
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
    #@nonl
    #@-node:tbrown.20090119215428.48:showDist
    #@-node:tbrown.20090119215428.40:ToDo icon related...
    #@+node:tbrown.20090119215428.49:updateUI
    def updateUI(self,tag=None,k=None):

        if k and k['c'] != self.c:
            return  # wrong number

        v = self.c.currentPosition().v
        self.ui.setProgress(int(self.getat(v, 'progress') or 0 ))
        self.ui.setTime(float(self.getat(v, 'time_req') or 0 ))
    #@-node:tbrown.20090119215428.49:updateUI
    #@-others
#@-node:tbrown.20090119215428.9:class todoController
#@-others
#@nonl
#@-node:tbrown.20090119215428.2:@thin todo.py
#@-leo
