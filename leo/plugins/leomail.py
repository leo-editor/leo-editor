#@+leo-ver=5-thin
#@+node:ville.20110125222411.10536: * @file ../plugins/leomail.py
#@+<< docstring >>
#@+node:ekr.20170228181049.1: ** << docstring >>
"""
Sync local mailbox files over to Leo.

Creates mail-refresh command, which can only be applied to @mbox nodes of the form:

    @mbox <path to .mbox file>

The command parses the .mbox file and creates a separate node for each thread.

Replies to the original messages become children of that message.
"""
#@-<< docstring >>
#@+<< imports >>
#@+node:ville.20110125222411.10539: ** << imports >>
from html.parser import HTMLParser
import mailbox
from leo.core import leoGlobals as g
#@-<< imports >>

#@+others
#@+node:ville.20110125222411.10540: ** init
def init():
    g.plugin_signon(__name__)
    return True
#@+node:ville.20110125222411.10546: ** mail_refresh & helpers
@g.command('mail-refresh')
def mail_refresh(event):
    c = event['c']
    p = c.p
    if p.h.startswith('@mbox'):
        aList = g.get_directives_dict_list(p)
        path = c.scanAtPathDirectives(aList)
        h = p.h[5:].strip()
        mb = g.finalize_join(path, h)
        if g.os_path_exists(mb):
            n = 0
            root = p.copy()
            parent = None
            for message in mailbox.mbox(mb):
                n += 1
                parent = emit_message(c, parent, root, message)
            c.redraw()
            g.es_print('created %s messages in %s threads' % (
                n, root.numberOfChildren()))
        else:
            g.trace('not found', mb)
    else:
        g.es_print('Please select an @mbox node.')
#@+node:ekr.20170228150606.1: *3* class MLStripper
class MLStripper(HTMLParser):

    # pylint: disable=abstract-method

    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []

    def handle_data(self, data):
        self.fed.append(data)

    def get_data(self):
        return ''.join(self.fed)
#@+node:ekr.20170228150717.1: *3* emit_message
def emit_message(c, parent, root, message):
    """Create all the children of p."""
    for part in message.walk():
        part.get_content_maintype()
        payload = part.get_payload()
        subject = g.toUnicode(message.get('subject'))
        from_ = g.toUnicode(message.get('from'))
        if parent and subject.lower().startswith('re:'):
            p = parent.insertAsLastChild()
        else:
            p = parent = root.insertAsLastChild()
        payload = g.toUnicode(payload)
        p.h = '%s [%s]' % (subject, from_)
        p.b = g.toUnicode(strip_tags(payload))
        return parent
#@+node:ekr.20170228150636.1: *3* strip_tags
def strip_tags(obj):
    stripper = MLStripper()
    if isinstance(obj, list):
        # Python 3: obj may be an email.message object.
        # https://docs.python.org/2/library/email.message.html
        # False: don't include headers.
        s = ''.join([z.as_string(False) for z in obj])
    else:
        s = obj
    stripper.feed(s)
    return stripper.get_data()
#@-others

#@-leo
