# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20180121041003.1: * @file leoTips.py
#@@first
'''Save and show tips to the user.'''
import random
import leo.core.leoGlobals as g
assert g
tips = []
#@+others
#@+node:ekr.20180121041252.1: ** class TipManager
class TipManager(object):
    '''A class to manage user tips.'''
    #@+others
    #@+node:ekr.20180121041822.1: *3* tipm.__init__
    def __init__(self, c):
        '''ctor for TipManager class.'''
        self.key = 'shown-tips'
        self.tips = [UserTip(i) for i in range(4)]
    #@+node:ekr.20180121041748.1: *3* tipm.get_next_tip
    def get_next_tip(self):
        
        db = g.app.db
        # Compute list of unseen tips.
        seen = db.get(self.key, [])
        unseen = [i for i in range(len(self.tips)) if i not in seen]
        if not unseen:
            g.trace('===== reinit tips')
            db [self.key] = []
            unseen = list(range(len(self.tips)))
            seen = []
        # Choose a tip at random from the unseen tips.
        i = random.choice(unseen)
        assert i not in seen, (i, seen)
        seen.append(i)
        db [self.key] = seen
        g.trace('returns', i)
        return self.tips[i]
    #@-others
#@+node:ekr.20180121041301.1: ** class UserTip
class UserTip(object):
    '''A User Tip.'''
    
    def __init__(self, n):
        self.n = n
        
    def __repr__(self):
        return 'This is user tip %s' % self.n
    __str__ = __repr__
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
