# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20180121041003.1: * @file leoTips.py
#@@first
'''Save and show tips to the user.'''
import random
import leo.core.leoGlobals as g
assert g
tips = []
    # The global tips array, created by make_tips script.
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
    
    def __init__(self, n, tags=None, text='', title=''):
        self.n = n
        self.tags = tags or []
        self.title = title
        self.text = text.strip()
        
    def __repr__(self):
        return 'This is user tip %s' % self.n
    __str__ = __repr__
#@+node:ekr.20180121045646.1: ** make_tips
def make_tips():
    '''A script to make entries in the global tips array.'''
    import requests
    base_url = 'https://api.github.com/repos/leo-editor/leo-editor/issues?labels=Tip&state='
    
    def get_tips(data):
        """get_tips - get tips from GitHub issues
        :param dict data: GitHub API issues list
        :return: list of Tips
        """
        tips = []
        for issue in data:
            if '\n' in issue['body']:
                tip, tags = issue['body'].strip().rsplit('\n', 1)
            else:
                tip, tags = issue['body'].strip(), ''
            if tags.lower().startswith('tags:'):
                tags = [i.strip().strip('.') for i in tags[5:].split(',')]
            else:
                tags = []
                tip = "%s\n%s" % (tip, tags)
            if isinstance(tip, (tuple, list)):
                tip = (z for z in tip if z and z.strip())
            tips.append(
                UserTip(
                    n=issue['number'],
                    tags=tags,
                    text=tip.strip().strip('[]').strip(),
                    title=issue['title'],
                ))
        return tips
    
    g.cls()
    for kind in 'open', 'closed':
        URL = base_url+kind
        data = requests.get(URL).json()
        for tip in get_tips(data):
            print('%s %s tip #%s %s...' % (('-'*10), kind, tip.n, tip.title))
            print('')
            print("TAGS: %s" % tip.tags or "**NO TAGS**")
            print('')
            # print(tip.text.strip().strip('[]').strip())
            print(tip.text)
            print('')
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
