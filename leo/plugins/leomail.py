#@+leo-ver=5-thin
#@+node:ville.20110125222411.10536: * @file leomail.py
#@+<< docstring >>
#@+node:ville.20110125222411.10537: ** << docstring >>
''' Sync local mailbox files over to Leo


'''
#@-<< docstring >>

__version__ = '0.0'
#@+<< version history >>
#@+node:ville.20110125222411.10538: ** << version history >>
#@@killcolor
#@+at
# 
# Put notes about each version here.
#@-<< version history >>

#@+<< imports >>
#@+node:ville.20110125222411.10539: ** << imports >>
import leo.core.leoGlobals as g

import sys

isPython3 = sys.version_info >= (3,0,0)

if isPython3:
    from html.parser import HTMLParser
else:
    from HTMLParser import HTMLParser

#@-<< imports >>

#@+others
#@+node:ville.20110125222411.10540: ** init
def init ():
    ok = True

    if ok:
        g.plugin_signon(__name__)

    return ok
#@+node:ville.20110125222411.10546: ** mail_refresh
import mailbox

#@+<< stripping >>
#@+node:ville.20110125222411.10547: *3* << stripping >>

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()
#@-<< stripping >>

def emit_message(c, p, message):
    for part in message.walk():
        ty = part.get_content_maintype()
        pl = part.get_payload(decode = True)
        p2 = p.insertAfter()
        
        bo = strip_tags(pl)
        p2.h = '%s [%s]' % (message['subject'], message['from'])
        p2.b = bo
    

@g.command('mail-refresh')
def mail_refresh(event):
    c = event['c']
    p = c.p
    assert p.h.startswith('@mbox')
    
    aList = g.get_directives_dict_list(p)
    path = c.scanAtPathDirectives(aList)
    
    mb = path + "/" + p.h.split(None,1)[1]
    
    folder = mailbox.mbox(mb)
    g.es(folder)
    
    r = p.insertAsLastChild()
    for message in folder:        
        emit_message(c,r, message)
    
    c.redraw()
#@-others
#@-leo
