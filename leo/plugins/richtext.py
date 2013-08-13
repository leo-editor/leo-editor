#@+leo-ver=5-thin
#@+node:tbrown.20130813134319.11942: * @file richtext.py
#@@language python
#@@tabwidth -4
#@+<< docstring >>
#@+node:tbrown.20130813134319.14333: ** << docstring >> (todo.py)
"""Rich text editing"""
#@-<< docstring >>
#@+<< imports >>
#@+node:tbrown.20130813134319.14335: ** << imports >>
import leo.core.leoGlobals as g
import sys
py3 = sys.version_info.major == 3

from PyQt4 import QtGui, QtWebKit, QtCore, Qt, QtXml
from PyQt4.QtCore import Qt as QtConst
from collections import OrderedDict
import time

if py3:
    from urllib.parse import unquote
else:
    from urllib import unquote
#@-<< imports >>
#@+others
#@+node:tbrown.20130813134319.14337: ** init
def init():

    name = g.app.gui.guiName()
    if name != "qt":
        if name != 'nullGui':
            print('richtext.py plugin not loading because gui is not Qt')
        return False

    g.registerHandler('after-create-leo-frame',onCreate)
    g.plugin_signon(__name__)
    return True
#@+node:tbrown.20130813134319.5691: ** class CKEEditor
class CKEEditor(QtGui.QWidget):
    #@+others
    #@+node:tbrown.20130813134319.7225: *3* __init__
    def __init__(self, *args, **kwargs):
        
        self.c = kwargs['c']
        
        del kwargs['c']
        QtGui.QWidget.__init__(self, *args, **kwargs)
        
        # read autosave preference
        if not hasattr(self.c, '_ckeeditor_autosave'):
            auto = self.c.config.getBool("richtext_cke_autosave") or False
            self.c._ckeeditor_autosave = auto
            if auto:
                g.es("NOTE: automatic saving of rich text edits")

        # load HTML template
        template_path = g.os_path_join(
            g.computeLeoDir(),
            'plugins', 'cke_template.html',
        )
        self.template = open(template_path).read()
        
        # load config
        self.config = self.c.config.getData("richtext_cke_config")
        if self.config:
            self.config = '\n'.join(self.config).strip()

        # precompute path containing ckeditor folder
        self.leo_external_path = "file://" + g.os_path_join(
            g.computeLeoDir(),
            'external'
        ) + "/"

        # make widget containing QWebView    
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0,0,0,0)
        # enable inspector
        QtWebKit.QWebSettings.globalSettings().setAttribute(
            QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)

        self.webview = QtWebKit.QWebView()
        self.layout().addWidget(self.webview)
        
        g.registerHandler('select3', self.select_node)
        g.registerHandler('unselect1', self.unselect_node)

        # load current node
        self.select_node('', {'c': self.c, 'new_p': self.c.p})
    #@+node:tbrown.20130813134319.7226: *3* select_node
    def select_node(self, tag, kwargs):
        c = kwargs['c']
        if c != self.c:
            return

        p = kwargs['new_p']
        data = self.template
        if p.b.startswith('<'):  # already rich text, probably
            content = p.b
            self.was_rich = True
        else:
            content = "<pre>%s</pre>" % p.b
            self.was_rich = p.b.strip() == ''
        data = data.replace('[CONTENT]', content)

        # replace textarea with CKEditor, with or without config.
        if self.config:
            data = data.replace('[CONFIG]', ', '+self.config)
        else:
            data = data.replace('[CONFIG]', '')
        self.webview.setHtml(data, QtCore.QUrl(self.leo_external_path))
    #@+node:tbrown.20130813134319.7228: *3* unselect_node
    def unselect_node(self, tag, kwargs):
        
        c = kwargs['c']
        if c != self.c:
            return

        # read initial content and request and wait for final content    
        frame = self.webview.page().mainFrame()
        ele = frame.findFirstElement("#initial")
        text = str(ele.toPlainText()).strip()
        if text == '[empty]':
            return  # no edit
        frame.evaluateJavaScript('save_final();')
        ele = frame.findFirstElement("#final")
        for attempt in range(10):  # wait for up to 1 second
            new_text = str(ele.toPlainText()).strip()
            if new_text == '[empty]':
                time.sleep(0.1)
                continue
            break
        if new_text == '[empty]':
            print("Didn't get new text")
            return
            
        text = unquote(str(text))
        new_text = unquote(str(new_text))
        
        if new_text != text:

            if self.c._ckeeditor_autosave:
                ans = 'yes'
            else:
                text = "Save edits?"
                if not self.was_rich:
                    text += " *converting plain text to rich*"
                ans = g.app.gui.runAskYesNoCancelDialog(
                    self.c,
                    "Save edits?",
                    text
                )
            if ans == 'yes':
                kwargs['old_p'].b = new_text
                c.redraw()  # but node has content marker still doesn't appear?
            elif ans == 'cancel':
                return 'STOP'
            else:
                pass  # discard edits
    #@+node:tbrown.20130813134319.7229: *3* close
    def close(self):
        if self.c:
            # save changes?
            self.unselect_node('', {'c': self.c, 'old_p': self.c.p})
        self.c = None
        g.unregisterHandler('select3', self.select_node)
        g.unregisterHandler('unselect1', self.unselect_node)
        return QtGui.QWidget.close(self)
    #@-others
#@+node:tbrown.20130813134319.5694: ** class CKEPaneProvider
class CKEPaneProvider:
    ns_id = '_add_cke_pane'
    def __init__(self, c):
        self.c = c
        # Careful: we may be unit testing.
        if hasattr(c, 'free_layout'):
            splitter = c.free_layout.get_top_splitter()
            if splitter:
                splitter.register_provider(self)
    def ns_provides(self):
        return[('Rich text CKE editor', self.ns_id)]
    def ns_provide(self, id_):
        if id_ == self.ns_id:
            w = CKEEditor(c=self.c)
            return w
    def ns_provider_id(self):
        # used by register_provider() to unregister previously registered
        # providers of the same service
        return self.ns_id
#@+node:tbrown.20130813134319.14339: ** onCreate
def onCreate (tag,key):

    c = key.get('c')

    CKEPaneProvider(c)
#@+node:tbrown.20130813134319.5692: ** @g.command('cke-text-open')
@g.command('cke-text-open')
def cmd_OpenEditor(kwargs):
    c = kwargs['c'] if isinstance(kwargs, dict) else kwargs
    splitter = c.free_layout.get_top_splitter()
    rte = splitter.find_child(CKEEditor, '')
    if rte:
        g.es("CKE Editor appears to be open already")
        return
    body = splitter.find_child(QtGui.QWidget, 'bodyFrame')
    w = CKEEditor(c=c)
    splitter = body.parent()
    splitter.replace_widget(body, w)
#@+node:tbrown.20130813134319.5693: ** @g.command('cke-text-close')
@g.command('cke-text-close')
def cmd_CloseEditor(kwargs):
    c = kwargs['c'] if isinstance(kwargs, dict) else kwargs
    splitter = c.free_layout.get_top_splitter()
    rte = splitter.find_child(CKEEditor, '')
    if not rte:
        g.es("No editor open")
    else:
        body = splitter.get_provided('_leo_pane:bodyFrame')
        splitter = rte.parent()
        splitter.replace_widget(rte, body)
#@+node:tbrown.20130813134319.7233: ** @g.command('cke-text-switch')
@g.command('cke-text-switch')
def cmd_SwitchEditor(kwargs):
    c = kwargs['c'] if isinstance(kwargs, dict) else kwargs
    splitter = c.free_layout.get_top_splitter()
    rte = splitter.find_child(CKEEditor, '')
    if not rte:
        cmd_OpenEditor(kwargs)
    else:
        cmd_CloseEditor(kwargs)
#@+node:tbrown.20130813134319.7231: ** @g.command('cke-text-toggle-autosave')
@g.command('cke-text-toggle-autosave')
def cmd_ToggleAutosave(kwargs):
    c = kwargs['c'] if isinstance(kwargs, dict) else kwargs
    c._ckeeditor_autosave = not c._ckeeditor_autosave
    g.es("Rich text autosave " + 
         ("ENABLED" if c._ckeeditor_autosave else "disabled"))
#@-others
#@-leo
