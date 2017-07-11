#@+leo-ver=5-thin
#@+node:ekr.20170428084207.434: * @file ../external/npyscreen/stdfmemail.py
#@+others
#@+node:ekr.20170428084207.435: ** Declarations
import curses
import weakref
import npyscreen
# import email
import mimetypes
import os.path

#@+node:ekr.20170428084207.436: ** class EmailTreeLine
class EmailTreeLine(npyscreen.TreeLine):
    #@+others
    #@+node:ekr.20170428084207.437: *3* display_value
    def display_value(self, vl):
        return vl
        if vl:
            return vl.getContent().get_content_type()
        else:
            return ""

    #@-others
#@+node:ekr.20170428084207.438: ** class EmailTree
class EmailTree(npyscreen.MultiLineTreeNew):
    _contained_widgets = EmailTreeLine
    #@+others
    #@+node:ekr.20170428084207.439: *3* display_value
    def display_value(self, vl):
        return vl.getContent().get_content_type()
        #return vl.get_content_type()

    #@+node:ekr.20170428084207.440: *3* EmailTree.h_select
    def h_select(self, ch):
        if self.values[self.cursor_line].hasChildren():
            self.cursor_line += 1
            return False

        try:
            value = [weakref.proxy(self.values[self.cursor_line]),]
        except TypeError:
            # Actually, this is inefficient, since with the NPSTree class (default) we will always be here - since by default we will
            # try to create a weakref to a weakref, and that will fail with a type-error.  BUT we are only doing it on a keypress, so
            # it shouldn't create a huge performance hit, and is future-proof. Code replicated in h_select_exit
            value = [self.values[self.cursor_line],]
        self.parent.when_select_part(value)
        self.editing = False
        self.how_exited=npyscreen.wgwidget.EXITED_UP
        self.hidden  = True

    #@+node:ekr.20170428084207.441: *3* h_select_exit
    def h_select_exit(self, ch):
        self.h_select(ch)

    #@+node:ekr.20170428084207.442: *3* set_up_handlers
    def set_up_handlers(self):
        '''EmailTree.set_up_handlers.'''
        super(EmailTree, self).set_up_handlers()
        self.handlers.update({
            ord('s'):   self.h_save_message_part,
        })

    #@+node:ekr.20170428084207.443: *3* h_save_message_part
    def h_save_message_part(self, ch):
        self.parent.saveMessagePart()
        npyscreen.notify_wait("Message part saved to your downloads folder: \n %s" % self.parent.DOWNLOAD_DIR)


    #@-others
#@+node:ekr.20170428084207.444: ** class EmailPager
class EmailPager(npyscreen.Pager):
    #@+others
    #@+node:ekr.20170428084207.445: *3* set_up_handlers
    def set_up_handlers(self):
        '''EmailPager.set_up_handlers.'''
        super(EmailPager, self).set_up_handlers()
        self.handlers.update({
            curses.KEY_LEFT:    self.h_exit_tree,
            ord('s'):           self.h_save_message_part,
            ord('x'):           self.h_exit_tree,
            ord('q'):           self.h_exit_tree,
            curses.ascii.ESC:   self.h_exit_tree,
        })

    #@+node:ekr.20170428084207.446: *3* EmailPager.h_exit_tree
    def h_exit_tree(self, ch):
        self.editing    = False
        self.how_exited = True
        self.parent.when_show_tree(ch)

    #@+node:ekr.20170428084207.447: *3* h_save_message_part
    def h_save_message_part(self, ch):
        self.parent.saveMessagePart()
        npyscreen.notify_wait("Message part saved to your downloads folder: \n %s" % self.parent.DOWNLOAD_DIR)


    #@-others
#@+node:ekr.20170428084207.448: ** class EmailViewFm
class EmailViewFm(npyscreen.SplitFormWithMenus):
    BLANK_COLUMNS_RIGHT= 1
    SHORT_HEADER_LIST = ('from', 'to', 'cc', 'bcc' 'date', 'subject', 'reply-to')
    DOWNLOAD_DIR = os.path.expanduser("~/Downloads")

    #@+others
    #@+node:ekr.20170428084207.449: *3* setEmail
    def setEmail(self, this_email):
        #Clear everything
        self.this_email          = this_email
        self.wSubject.value      = ""
        self.wFrom.value         = ""
        self.wDate.value         = ""
        self.wEmailBody.values   = []
        self.wStatusLine.value   = ""
        self.wEmailBody.hidden   = True
        self.wEmailBody.start_display_at = 0
        self.wMessageTree.hidden = False
        self.wMessageTree.cursor_line = 0

        self.updateEmailTree()

        self.wSubject.value     = this_email['subject']
        self.wFrom.value        = this_email['from']
        self.wDate.value        = this_email['date']


    #@+node:ekr.20170428084207.450: *3* setValue
    def setValue(self, this_email):
        return self.setEmail(this_email)


    #@+node:ekr.20170428084207.451: *3* updateEmailTree
    def updateEmailTree(self):
        self._parse_email_tree(self.this_email)
        self.wMessageTree.values = self._this_email_tree


    #@+node:ekr.20170428084207.452: *3* set_up_handlers
    def set_up_handlers(self):
        '''EmailViewFm.set_up_handlers.'''
        super(EmailViewFm, self).set_up_handlers()
        self.handlers.update({})

    #@+node:ekr.20170428084207.453: *3* create
    def create(self):
        self.m1 = self.add_menu(name="Read Email")
        self.m1.addItemsFromList([
            ('View Short Headers',              self.viewShortHeaders),
            ('View Full Headers',               self.viewAllHeaders),
            ('View Message Tree',              self.viewMessageTree),
            ('Save this Message Part',          self.saveMessagePart),
            ('View Message Source',             self.viewMessageSource),
        ])
        self.nextrely = 1
        self.wSubject = self.add(npyscreen.TitleText, begin_entry_at=10, editable=False,
                                        use_two_lines=False, name = "Subject:")
        self.wFrom    = self.add(npyscreen.TitleText, begin_entry_at=10,
                                        editable=False, name = "From:", ) #max_width=-8)
        self.wDate    = self.add(npyscreen.TitleText, begin_entry_at=10,
                                        editable=False, name = "Date:")

        self.draw_line_at   = self.nextrely
        self.nextrely      += 1
        _body_rely          = self.nextrely
        self.wEmailBody     = self.add(EmailPager, max_height=-1, scroll_exit=True, hidden=True)
        self.nextrely       = _body_rely
        self.wMessageTree   = self.add(EmailTree, max_height=-1, scroll_exit=True, hidden=False)
        self.nextrely      += 1
        self.wStatusLine    = self.add(npyscreen.FixedText,
            editable=False,
            use_max_space=True,
            color='STANDOUT',
            value="Status Line-Status Line-Status Line-Status Line-Status Line-Status Line-Status Line-")


    #@+node:ekr.20170428084207.454: *3* _parse_email_tree
    def _parse_email_tree(self, this_email):
        "Create an NPSTree representation of the email."
        self._this_email_tree = npyscreen.NPSTreeData(content=this_email, ignoreRoot=False)
        if this_email.is_multipart():
            for part in this_email.get_payload():
                self._tree_add_children(self._this_email_tree, part)

    #@+node:ekr.20170428084207.455: *3* _tree_add_children
    def _tree_add_children(self, tree_node, this_message_part):
        use_part = this_message_part
        this_child = tree_node.newChild(content=use_part)
        try:
            if use_part.is_multipart():
                for part in use_part.get_payload():
                    self._tree_add_children(this_child, part)
        except AttributeError:
            # Dealing with a string only, not a message.
            pass

    #@+node:ekr.20170428084207.456: *3* when_select_part
    def when_select_part(self, vl):
        self.wEmailBody.hidden = False
        self.wEmailBody.setValuesWrap(vl[0].getContent().get_payload(decode=True).decode(errors='replace').split("\n"))
        self.wEmailBody.start_display_at = 0
        self.wMessageTree.hidden = True

    #@+node:ekr.20170428084207.457: *3* when_show_tree
    def when_show_tree(self, vl):
        if self.wMessageTree.hidden:
            self.wEmailBody.hidden = True
            if self.wEmailBody.editing:
                self.wEmailBody.h_exit_tree(vl)
            self.wMessageTree.hidden = False
            self.wStatusLine.value = ""
            self.display()

    #@+node:ekr.20170428084207.458: *3* viewShortHeaders
    def viewShortHeaders(self,):
        s_header_list = []
        for headers in self.SHORT_HEADER_LIST:
            these_headers = self.this_email.get_all(headers)
            if these_headers:
                for h in these_headers:
                    s_header_list.append(str(headers).capitalize() + ": " + h.strip())
        npyscreen.notify_confirm(s_header_list, wide=True, wrap=False)

    #@+node:ekr.20170428084207.459: *3* saveMessagePart
    def saveMessagePart(self, vl=None):
        if vl == None:
            vl = self.wMessageTree.values[self.wMessageTree.cursor_line].getContent()
        if vl.is_multipart():
            for v in vl.get_payload():
                self.saveMessagePart(v)
        else:
            self._savePartToFile(vl)

    #@+node:ekr.20170428084207.460: *3* _savePartToFile
    def _savePartToFile(self, messagePart):
        fn = messagePart.get_filename()
        counter = 0
        if not fn:
            ext = mimetypes.guess_extension(messagePart.get_content_type()) # Bug in python returns .ksh for text/plain.  Wait for python fix?
            if not ext:
                # generic extension?
                ext = '.bin'
            fn = 'emailpart%s' % (ext)
        fn = os.path.basename(fn) # Sanitize Filename.
        attempted_filename = fn
        while os.path.exists(os.path.join(self.DOWNLOAD_DIR, attempted_filename)):
            counter += 1
            attempted_filename = "%s%s%s" % (os.path.splitext(fn)[0], counter, os.path.splitext(fn)[1])
        fn = attempted_filename
        fqfn = os.path.join(self.DOWNLOAD_DIR, fn)
        if messagePart.get_content_maintype() == "text":
            with open(fqfn, 'w') as f:
                f.write(messagePart.get_payload(decode=True))
        else:
            with open(fqfn, 'wb') as f:
                f.write(messagePart.get_payload(decode=True))


    #@+node:ekr.20170428084207.461: *3* viewAllHeaders
    def viewAllHeaders(self,):
        s_header_list = []
        for headers in list(self.this_email.keys()):
            these_headers = self.this_email.get_all(headers)
            if these_headers:
                for h in these_headers:
                    s_header_list.append(str(headers).capitalize() + ": " + h.strip())
        npyscreen.notify_confirm(s_header_list, wide=True, wrap=True)


    #@+node:ekr.20170428084207.462: *3* viewMessageTree
    def viewMessageTree(self,):
        self.wEmailBody.h_exit_tree(None)
        self.wEmailBody.hidden = True

    #@+node:ekr.20170428084207.463: *3* viewMessageSource
    def viewMessageSource(self,):
        npyscreen.notify_confirm(self.this_email.as_string(), wide=True)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
