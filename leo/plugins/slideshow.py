#@+leo-ver=5-thin
#@+node:ekr.20060831165821: * @file slideshow.py
#@+<< docstring >>
#@+node:ekr.20060831165845.1: ** << docstring >>
''' Supports slideshows in Leo outlines.

This plugin defines four new commands:

- next-slide-show:  move to the start of the next slide show,
  or the first slide show if no slide show has been seen yet.
- prev-slide-show:  move to the start of the previous slide show,
  or the first slide show if no slide show has been seen yet.
- next-slide: move to the next slide of a present slide show.
- prev-slide: move to the previous slide of the present slide show.

Slides shows consist of a root @slideshow node with descendant @slide nodes.
@slide nodes may be organized via non-@slide nodes that do not appear in the slideshow.

All these commands ignore @ignore trees.

'''
#@-<< docstring >>

__version__ = '0.4'

#@+at
# To do:
# - Add sound/script support for slides.
# - Save/restore changes to slides when entering/leaving a slide.
#@@c

#@+<< version history >>
#@+node:ekr.20060831165845.2: ** << version history >>
#@@killcolor
#@+at
# 
# 0.01 EKR: Initial version.
# 0.02 EKR: Improved docstring and added todo notes.
# 0.03 EKR: Simplified createCommands.
# 0.1  EKR: A big step forward.
# The next/prev-slide-show commands allow easy management of multiple slideshows.
# 0.2  EKR: next/pref-slide-show commands work properly when
# a) c.currentPosition changes and
# b) @slideshow nodes inserted or deleted.
# 0.3 EKR:
# - next-slide and prev-slide now work more intuitively when current position changes.
# 0.4 EKR: Support @ignore nodes in all commands.
#@-<< version history >>
#@+<< imports >>
#@+node:ekr.20060831165845.3: ** << imports >>
import leo.core.leoGlobals as g

#@-<< imports >>

#@+others
#@+node:ekr.20060831165845.4: ** init
def init ():
    '''Return True if the plugin has loaded successfully.'''
    g.registerHandler(('open2','new2'),onCreate)
    g.plugin_signon(__name__)
    return True
#@+node:ekr.20060831165845.5: ** onCreate
def onCreate (tag, keys):

    c = keys.get('c')
    if not c: return

    slideshowController(c)
#@+node:ekr.20060831165845.6: ** class slideshowController
class slideshowController:

    #@+others
    #@+node:ekr.20060831165845.7: *3* __init__
    def __init__ (self,c):

        self.c = c
        self.firstSlideShow = None
        self.slideShowRoot = None
        self.slide = None
        self.createCommands()
    #@+node:ekr.20060831171016: *3* createCommands
    def createCommands (self):

        c = self.c ; k = c.k

        for name,func in (
            ('next-slide-command',      self.nextSlide),
            ('next-slide-show-command', self.nextSlideShow),
            ('prev-slide-command',      self.prevSlide),
            ('prev-slide-show-command', self.prevSlideShow),
        ):
            k.registerCommand (name,shortcut=None,func=func,pane='all',verbose=False)
    #@+node:ekr.20060901182318: *3* findFirstSlideShow
    def findFirstSlideShow (self):

        c = self.c
        for p in c.all_positions():
            h = p.h.strip()
            if h.startswith('@slideshow'):
                self.firstSlideShow = p.copy()
                return p
            elif g.match_word(h,0,'@ignore'):
                p = p.nodeAfterTree()

        self.firstSlideShow = None
        return None
    #@+node:ekr.20060904110319: *3* ignored
    def ignored (self,p):

        for p2 in p.self_and_parents():
            if g.match_word(p2.h,0,'@ignore') or g.match_word(p2.h,0,'@noslide'):
                return True
        return False
    #@+node:ekr.20060831171016.5: *3* nextSlide
    def nextSlide (self,event=None):

        c = self.c ; p = c.p
        if p == self.slide:
            p = self.slide.threadNext()
            oldSlide = self.slide
        else:
            oldSlide = None
        while p:
            h = p.h.strip()
            if self.ignored(p):
                p = p.threadNext()
            elif h.startswith('@slideshow'):
                self.select(p)
                return g.es('At %s of slide show' % 'end' if oldSlide else 'start')
            elif g.match_word(h,0,'@ignore') or g.match_word(h,0,'@noslide'):
                p = p.nodeAfterTree()
            else:
                return self.select(p)
            # elif h.startswith('@slide'):
                # return self.select(p)
            # else: p = p.threadNext()
        return g.es('At end of slide show' if self.slideShowRoot else 'Not in any slide show')
    #@+node:ekr.20060901142848: *3* nextSlideShow
    def nextSlideShow (self,event=None):

        c = self.c
        self.findFirstSlideShow()
        if not self.firstSlideShow:
            return g.es('No slide show found') 
        elif not self.slideShowRoot:
            return self.select(self.firstSlideShow)
        p = c.p
        h = p.h.strip()
        if h.startswith('@slideshow'):
            p = p.threadNext()
        while p:
            h = p.h.strip()
            if self.ignored(p):
                p = p.threadNext()
            elif h.startswith('@slideshow'):
                return self.select(p)
            elif g.match_word(h,0,'@ignore'):
                p = p.nodeAfterTree()
            else:
                p = p.threadNext()
        self.select(self.slideShowRoot)
        g.es('At start of last slide show')
    #@+node:ekr.20060831171016.4: *3* prevSlide
    def prevSlide (self,event=None):

        c = self.c ; p = c.p
        if self.ignored(p):
            p = p.threadBack()
        else:
            if self.slide and self.slide == self.slideShowRoot:
                return g.es('At start of slide show')
            if p == self.slide:
                p = self.slide.threadBack()
        while p:
            h = p.h.strip()
            if self.ignored(p):
                p = p.threadBack()
            elif h.startswith('@slideshow'):
                self.select(p)
                return g.es('At start of slide show')
            else:
                return self.select(p)
            # elif h.startswith('@slide'):
                # return self.select(p)
            # else: p = p.threadBack()
        p = self.findFirstSlideShow()
        if p:
            self.select(p)
            return g.es('At start of first slide show')
        else:
            return g.es('No slide show found')
    #@+node:ekr.20060901142848.1: *3* prevSlideShow
    def prevSlideShow (self,event=None):

        c = self.c
        self.findFirstSlideShow()
        if not self.firstSlideShow:
            return g.es('No slide show found') 
        elif not self.slideShowRoot:
            return self.select(self.firstSlideShow)
        p = c.p
        h = p.h.strip()
        if h.startswith('@slideshow'):
            p = p.threadBack()
        while p:
            h = p.h.strip()
            if self.ignored(p):
                p = p.threadBack()
            elif h.startswith('@slideshow'):
                return self.select(p)
            else:
                p = p.threadBack()
        self.select(self.firstSlideShow)
        g.es('At start of first slide show')
    #@+node:ekr.20060901145257: *3* select
    def select (self,p):
        '''Make p the present slide, and set self.slide and maybe self.slideShowRoot.'''
        c = self.c ; h = p.h.strip()
        w = c.frame.body.wrapper
        g.es('%s' % h)
        #c.expandAllAncestors(p)
        #c.selectPosition(p)
        c.redraw_now(p)
        w.see('1.0')
        if h.startswith('@slideshow'):
            self.slideShowRoot = p.copy()

        self.slide = p.copy()
    #@-others
#@-others
#@-leo
