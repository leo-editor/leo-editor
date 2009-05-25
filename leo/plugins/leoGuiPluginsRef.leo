<?xml version="1.0" encoding="utf-8"?>
<?xml-stylesheet ekr_test?>
<leo_file>
<leo_header file_format="2" tnodes="0" max_tnode_index="0" clone_windows="0"/>
<globals body_outline_ratio="0.5">
	<global_window_position top="72" left="119" height="936" width="1118"/>
	<global_log_window_position top="0" left="0" height="0" width="0"/>
</globals>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="ekr.20081121105001.1076" str_leo_pos="3,1,5,9"><vh>Startup</vh>
<v t="ekr.20081121105001.1077"><vh>@chapters</vh></v>
<v t="ekr.20081121105001.1078"><vh>@settings</vh>
<v t="ekr.20081121105001.1079"><vh>@page http plugin</vh>
<v t="ekr.20081121105001.1080"><vh>@bool http_active = False</vh></v>
<v t="ekr.20081121105001.1081"><vh>@int  port = 8080</vh></v>
<v t="ekr.20081121105001.1082"><vh>@string rst_http_attributename = rst_http_attribute</vh></v>
</v>
</v>
<v t="ekr.20081121105001.1083"><vh>buttons</vh>
<v t="ekr.20081121105001.1084"><vh>@@button settings.leo</vh></v>
<v t="ekr.20081121105001.1085"><vh>@@button scripts.leo</vh></v>
<v t="ekr.20081121105001.1086"><vh>@@button Beautify</vh></v>
<v t="ekr.20081121105001.1087"><vh>@@button Spell</vh></v>
<v t="ekr.20081121105001.1088"><vh>@@button Save</vh></v>
</v>
<v t="ekr.20081121105001.1089"><vh>regex: replace w.bind by c.bind(w...)</vh></v>
<v t="ekr.20081121105001.1090"><vh>@@button change leo imports</vh></v>
</v>
<v t="ekr.20081121105001.1108"><vh>Notes</vh>
<v t="ekr.20081121105001.147"
marks="ekr.20081121105001.264,"
expanded="ekr.20081121105001.572,"><vh>@thin qtNotes.txt</vh></v>
</v>
<v t="ekr.20081121105001.1110"><vh>Other guis</vh>
<v t="ekr.20081121105001.12"><vh>@thin cursesGui.py</vh></v>
<v t="ekr.20081121105001.80"><vh>@thin ironPythonGui.py</vh></v>
<v t="ekr.20081121105001.595"><vh>@thin swing_gui.py</vh></v>
<v t="ekr.20081121110412.2"><vh>@thin tkGui.py</vh></v>
<v t="ekr.20090126093408.1"><vh>@thin wxGui.py</vh></v>
</v>
<v t="ekr.20081121105001.1092" a="E"><vh>Qt gui</vh>
<v t="ekr.20081121105001.1093"><vh>QDesigner files</vh>
<v t="ekr.20081121105001.1094"><vh>@auto ../test/qtui_generate.py</vh></v>
<v t="ekr.20081121105001.1095"><vh>@auto qt_main.py</vh></v>
<v t="ekr.20081121105001.1096"><vh>@auto qt_main.ui</vh></v>
<v t="ekr.20081121105001.1097"><vh>@auto qt_quicksearch.py</vh></v>
<v t="ekr.20081121105001.1098"><vh>@auto qt_quicksearch.ui</vh></v>
</v>
<v t="ekr.20090124174652.7" a="E"
expanded="ekr.20090124174652.9,ekr.20090124174652.52,ekr.20090124174652.85,ekr.20090124174652.63,"><vh>@thin baseNativeTree.py</vh></v>
<v t="ekr.20081121105001.188" a="E"
marks="ekr.20081121105001.264,"
expanded="ekr.20081121105001.194,ekr.20090124174652.102,ekr.20081121105001.473,ekr.20081121105001.509,ekr.20081121105001.521,ekr.20081121105001.572,"><vh>@thin qtGui.py</vh></v>
<v t="leohag.20081204085551.1"><vh>@thin scrolledmessage.py</vh></v>
</v>
<v t="ekr.20081121105001.148"><vh> qt To do</vh>
<v t="ekr.20090430102239.1"><vh>Before b2</vh>
<v t="ekr.20090430102239.2"><vh>Arrow keys do not work in headlines</vh></v>
<v t="ekr.20090409055330.10"><vh>Make sure change-all honors node-only and suboutline-only settings</vh>
<v t="ekr.20081121105001.235"><vh>class leoQtFindTab (findTab)</vh>
<v t="ekr.20081121105001.236"><vh> Birth: called from leoFind ctor</vh>
<v t="ekr.20081121105001.237"><vh>initGui</vh></v>
<v t="ekr.20081121105001.238"><vh>init (qtFindTab) &amp; helpers</vh>
<v t="ekr.20081121105001.239"><vh>createIvars</vh></v>
<v t="ekr.20081121105001.240"><vh>initIvars</vh></v>
<v t="ekr.20081121105001.241"><vh>initTextWidgets</vh></v>
<v t="ekr.20081121105001.242"><vh>initCheckBoxes</vh></v>
<v t="ekr.20081121105001.243"><vh>initRadioButtons</vh></v>
</v>
</v>
<v t="ekr.20081121105001.244"><vh>class svar</vh>
<v t="ekr.20090427112929.10"><vh>svar.ctor</vh></v>
<v t="ekr.20090427112929.12"><vh>get</vh></v>
<v t="ekr.20090427112929.13"><vh>init</vh></v>
<v t="ekr.20090427112929.17"><vh>set</vh></v>
<v t="ekr.20090427112929.18"><vh>setRadioScope</vh></v>
<v t="ekr.20090427112929.15"><vh>setWidget</vh></v>
</v>
<v t="ekr.20081121105001.245"><vh>Support for minibufferFind class (qtFindTab)</vh>
<v t="ekr.20081121105001.246"><vh>getOption</vh></v>
<v t="ekr.20081121105001.247"><vh>setOption</vh></v>
<v t="ekr.20081121105001.248"><vh>toggleOption</vh></v>
</v>
</v>
</v>
<v t="ekr.20090430102239.3"><vh>Fix page up/down problem</vh>
<v t="ekr.20090430102239.4"><vh>masterKeyHandler &amp; helpers</vh>
<v t="ekr.20090430102239.5"><vh>&lt;&lt; define vars &gt;&gt;</vh></v>
<v t="ekr.20090430102239.6"><vh>&lt;&lt; handle mode bindings &gt;&gt;</vh></v>
<v t="ekr.20090430102239.7"><vh>&lt;&lt; handle special cases for plain keys &gt;&gt;</vh></v>
<v t="ekr.20090430102239.8"><vh>&lt;&lt; handle per-pane bindings &gt;&gt;</vh></v>
<v t="ekr.20090430102239.9"><vh>callStateFunction</vh></v>
<v t="ekr.20090430102239.10"><vh>handleMiniBindings</vh></v>
<v t="ekr.20090430102239.11"><vh>k.handleUnboudKeys</vh></v>
</v>
<v t="ekr.20090430102239.12"><vh>scrollOutlineUp/Down/Line/Page</vh></v>
</v>
<v t="ekr.20090421121914.11"><vh>Urgent: fix the tkinter problem in Terry's code</vh></v>
<v t="ekr.20081215162017.5"><vh>Support multiple body editors</vh>
<v t="ekr.20090318091009.13"><vh>Prototype code</vh></v>
<v t="ekr.20081121105001.572" a="E"><vh> class leoQTextEditWidget</vh>
<v t="ekr.20081121105001.573"><vh>Birth</vh>
<v t="ekr.20081121105001.574"><vh>ctor</vh></v>
<v t="ekr.20081121105001.575"><vh>setFontFromConfig</vh></v>
<v t="ekr.20081121105001.576"><vh>setColorFromConfig</vh></v>
<v t="ekr.20081121105001.577"><vh>setConfig</vh></v>
<v t="ekr.20090303095630.10"><vh>setScrollBarOrientation (QTextEdit)</vh></v>
</v>
<v t="ekr.20081121105001.578"><vh>Widget-specific overrides (QTextEdit)</vh>
<v t="ekr.20090205153624.11"><vh>delete (avoid call to setAllText)</vh></v>
<v t="ekr.20081121105001.579"><vh>flashCharacter (leoQTextEditWidget)</vh></v>
<v t="ekr.20081121105001.580"><vh>getAllText (leoQTextEditWidget)</vh></v>
<v t="ekr.20081121105001.581"><vh>getInsertPoint</vh></v>
<v t="ekr.20081121105001.582"><vh>getSelectionRange</vh></v>
<v t="ekr.20081121105001.583"><vh>getYScrollPosition</vh></v>
<v t="ekr.20081121105001.584"><vh>hasSelection</vh></v>
<v t="ekr.20090205153624.12"><vh>insert (avoid call to setAllText)</vh></v>
<v t="ekr.20081121105001.585"><vh>see</vh></v>
<v t="ekr.20081121105001.586"><vh>seeInsertPoint</vh></v>
<v t="ekr.20081121105001.587"><vh>setAllText (leoQTextEditWidget)</vh></v>
<v t="ekr.20081121105001.588"><vh>setInsertPoint</vh></v>
<v t="ekr.20081121105001.589"><vh>setSelectionRangeHelper &amp; helper</vh>
<v t="ekr.20081121105001.590"><vh>lengthHelper</vh></v>
</v>
<v t="ekr.20081121105001.591"><vh>setYScrollPosition</vh></v>
<v t="ville.20090321082712.1"><vh> PythonIndex</vh>
<v t="ville.20090321082712.2"><vh>toPythonIndex</vh></v>
<v t="ville.20090321082712.3"><vh>toPythonIndexToRowCol</vh></v>
</v>
<v t="ville.20090324170325.63"><vh>get</vh></v>
</v>
</v>
<v t="ekr.20081121110412.143"><vh>Editors (tkBody)</vh>
<v t="ekr.20081121110412.144"><vh>createEditorFrame</vh></v>
<v t="ekr.20081121110412.145"><vh>packEditorLabelWidget</vh></v>
<v t="ekr.20081121110412.146"><vh>setEditorColors</vh></v>
</v>
<v t="ekr.20081121110412.133"><vh>tkBody.createTextWidget</vh></v>
<v t="ekr.20081121105001.205"><vh>class leoQtBody (leoBody)</vh>
<v t="ekr.20081121105001.206"><vh> Birth</vh>
<v t="ekr.20081121105001.207"><vh> ctor (qtBody)</vh></v>
<v t="ekr.20081121105001.208"><vh>createBindings (qtBody)</vh></v>
<v t="ekr.20081121105001.209"><vh>get_name</vh></v>
</v>
<v t="ekr.20081121105001.210"><vh>Do-nothings</vh></v>
<v t="ekr.20081121105001.211"><vh>High-level interface to self.widget</vh></v>
<v t="ekr.20081121105001.212"><vh>Editors (qtBody)</vh>
<v t="ekr.20081121105001.214"><vh>packEditorLabelWidget</vh></v>
<v t="ekr.20081121105001.215"><vh>entries</vh>
<v t="ekr.20081121105001.216"><vh>addEditor &amp; helpers (qtBody)</vh>
<v t="ekr.20081121105001.213"><vh>createEditorFrame</vh></v>
<v t="ekr.20081121105001.217"><vh>createEditorWidget</vh></v>
<v t="ekr.20090318091009.14"><vh>createTextWidget (not used)</vh></v>
</v>
<v t="ekr.20081121105001.218"><vh>assignPositionToEditor</vh></v>
<v t="ekr.20081121105001.219"><vh>cycleEditorFocus</vh></v>
<v t="ekr.20081121105001.220"><vh>deleteEditor</vh></v>
<v t="ekr.20081121105001.221"><vh>findEditorForChapter (leoBody)</vh></v>
<v t="ekr.20081121105001.222"><vh>select/unselectLabel</vh></v>
<v t="ekr.20081121105001.223"><vh>selectEditor &amp; helpers</vh>
<v t="ekr.20081121105001.224"><vh>selectEditorHelper</vh>
<v t="ekr.20081121105001.225"><vh>&lt;&lt; restore the selection, insertion point and the scrollbar &gt;&gt;</vh></v>
</v>
</v>
<v t="ekr.20081121105001.226"><vh>updateEditors</vh></v>
</v>
<v t="ekr.20081121105001.227"><vh>utils</vh>
<v t="ekr.20081121105001.228"><vh>computeLabel</vh></v>
<v t="ekr.20081121105001.229"><vh>createChapterIvar</vh></v>
<v t="ekr.20081121105001.230"><vh>ensurePositionExists</vh></v>
<v t="ekr.20081121105001.231"><vh>inactivateActiveEditor</vh></v>
<v t="ekr.20081121105001.232"><vh>recolorWidget</vh></v>
<v t="ekr.20081121105001.233"><vh>switchToChapter (leoBody)</vh></v>
<v t="ekr.20081121105001.234"><vh>updateInjectedIvars</vh></v>
</v>
</v>
<v t="ekr.20090406071640.13"><vh>Event handlers called from eventFilter</vh></v>
</v>
<v t="ekr.20081121105001.249"><vh>class leoQtFrame</vh>
<v t="ekr.20081121105001.250"><vh> Birth &amp; Death (qtFrame)</vh>
<v t="ekr.20081121105001.251"><vh>__init__ (qtFrame)</vh>
<v t="ekr.20081121105001.252"><vh>&lt;&lt; set the leoQtFrame ivars &gt;&gt; (removed frame.bodyCtrl ivar)</vh></v>
</v>
<v t="ekr.20081121105001.253"><vh>__repr__ (qtFrame)</vh></v>
<v t="ekr.20081121105001.254"><vh>qtFrame.finishCreate &amp; helpers</vh>
<v t="ekr.20081121105001.255"><vh>createSplitterComponents (qtFrame)</vh></v>
</v>
<v t="ekr.20081121105001.256"><vh>initCompleteHint</vh></v>
<v t="ekr.20081121105001.257"><vh>Destroying the qtFrame</vh>
<v t="ekr.20081121105001.258"><vh>destroyAllObjects</vh>
<v t="ekr.20081121105001.259"><vh>&lt;&lt; clear all vnodes and tnodes in the tree&gt;&gt;</vh></v>
</v>
<v t="ekr.20081121105001.260"><vh>destroySelf (qtFrame)</vh></v>
</v>
</v>
<v t="ekr.20081121105001.261"><vh>class qtStatusLineClass (qtFrame)</vh>
<v t="ekr.20081121105001.262"><vh>ctor</vh></v>
<v t="ekr.20081121105001.263"><vh> do-nothings</vh></v>
<v t="ekr.20081121105001.264" a="M"><vh>clear, get &amp; put/1</vh></v>
<v t="ekr.20081121105001.265"><vh>update</vh></v>
</v>
<v t="ekr.20081121105001.266"><vh>class qtIconBarClass</vh>
<v t="ekr.20081121105001.267"><vh> ctor</vh></v>
<v t="ekr.20081121105001.268"><vh> do-nothings</vh></v>
<v t="ekr.20081121105001.269"><vh>add</vh></v>
<v t="ekr.20081121105001.270"><vh>addRowIfNeeded</vh></v>
<v t="ekr.20081121105001.271"><vh>addWidget</vh></v>
<v t="ekr.20081121105001.272"><vh>clear</vh></v>
<v t="ekr.20081121105001.273"><vh>deleteButton</vh></v>
<v t="ekr.20081121105001.274"><vh>setCommandForButton</vh></v>
</v>
<v t="ekr.20081121105001.275"><vh>Minibuffer methods</vh>
<v t="ekr.20081121105001.276"><vh>showMinibuffer</vh></v>
<v t="ekr.20081121105001.277"><vh>hideMinibuffer</vh></v>
<v t="ekr.20081121105001.278"><vh>f.setMinibufferBindings</vh></v>
</v>
<v t="ekr.20081121105001.279"><vh>Configuration (qtFrame)</vh>
<v t="ekr.20081121105001.280"><vh>configureBar (qtFrame)</vh></v>
<v t="ekr.20081121105001.281"><vh>configureBarsFromConfig (qtFrame)</vh></v>
<v t="ekr.20081121105001.282"><vh>reconfigureFromConfig (qtFrame)</vh></v>
<v t="ekr.20081121105001.283"><vh>setInitialWindowGeometry (qtFrame)</vh></v>
<v t="ekr.20081121105001.284"><vh>setTabWidth (qtFrame)</vh></v>
<v t="ekr.20081121105001.285"><vh>setWrap (qtFrame)</vh></v>
<v t="ekr.20081121105001.286"><vh>reconfigurePanes (use config bar_width) (qtFrame)</vh></v>
<v t="ekr.20081121105001.287"><vh>resizePanesToRatio (qtFrame)</vh></v>
<v t="leohag.20081208130321.12"><vh>divideLeoSplitter</vh></v>
<v t="leohag.20081208130321.13"><vh>divideAnySplitter</vh></v>
</v>
<v t="ekr.20081121105001.288"><vh>Event handlers (qtFrame)</vh>
<v t="ekr.20081121105001.289"><vh>frame.OnCloseLeoEvent</vh></v>
<v t="ekr.20081121105001.290"><vh>frame.OnControlKeyUp/Down</vh></v>
<v t="ekr.20081121105001.291"><vh>OnActivateBody (qtFrame)</vh></v>
<v t="ekr.20081121105001.292"><vh>OnActivateLeoEvent, OnDeactivateLeoEvent</vh></v>
<v t="ekr.20081121105001.293"><vh>OnActivateTree</vh></v>
<v t="ekr.20081121105001.294"><vh>OnBodyClick, OnBodyRClick (Events)</vh></v>
<v t="ekr.20081121105001.295"><vh>OnBodyDoubleClick (Events)</vh></v>
</v>
<v t="ekr.20081121105001.296"><vh>Gui-dependent commands</vh>
<v t="ekr.20081121105001.297"><vh>Minibuffer commands... (qtFrame)</vh>
<v t="ekr.20081121105001.298"><vh>contractPane</vh></v>
<v t="ekr.20081121105001.299"><vh>expandPane</vh></v>
<v t="ekr.20081121105001.300"><vh>fullyExpandPane</vh></v>
<v t="ekr.20081121105001.301"><vh>hidePane</vh></v>
<v t="ekr.20081121105001.302"><vh>expand/contract/hide...Pane</vh></v>
<v t="ekr.20081121105001.303"><vh>fullyExpand/hide...Pane</vh></v>
</v>
<v t="ekr.20081121105001.304"><vh>Window Menu...</vh>
<v t="ekr.20081121105001.305"><vh>toggleActivePane (qtFrame)</vh></v>
<v t="ekr.20081121105001.306"><vh>cascade</vh></v>
<v t="ekr.20081121105001.307"><vh>equalSizedPanes</vh></v>
<v t="ekr.20081121105001.308"><vh>hideLogWindow</vh></v>
<v t="ekr.20081121105001.309"><vh>minimizeAll</vh></v>
<v t="ekr.20081121105001.310"><vh>toggleSplitDirection (qtFrame)</vh>
<v t="ekr.20081121105001.311"><vh>toggleQtSplitDirection</vh></v>
</v>
<v t="ekr.20081121105001.312"><vh>resizeToScreen</vh></v>
</v>
<v t="ekr.20081121105001.313"><vh>Help Menu...</vh>
<v t="ekr.20081121105001.314"><vh>leoHelp</vh>
<v t="ekr.20081121105001.315"><vh>showProgressBar</vh>
<v t="ekr.20081121105001.316"><vh>&lt;&lt; create the scale widget &gt;&gt;</vh></v>
</v>
</v>
</v>
</v>
<v t="ekr.20081121105001.317"><vh>Qt bindings... (qtFrame)</vh></v>
</v>
<v t="ekr.20081121105001.212"></v>
<v t="ekr.20081121105001.214"></v>
<v t="ekr.20081121105001.216"></v>
<v t="ekr.20081121105001.222"></v>
</v>
<v t="ekr.20090426075320.10"><vh>mark command reverts headline</vh></v>
<v t="ekr.20081215074704.16"><vh>Mark finds doesn't work in Qt gui plugin</vh></v>
<v t="ekr.20090304084841.15"><vh>Complete open-with menu</vh></v>
<v t="ekr.20090223065019.11"><vh>Make Leo's page-up/page-down commands funtional</vh></v>
<v t="ekr.20090318091009.12"><vh>Script errors mess up syntax coloring</vh></v>
</v>
<v t="ekr.20090430102239.13"><vh>Before 4.6 final</vh>
<v t="ekr.20090429101847.10"><vh>Support canvas widgets in all panes</vh></v>
<v t="ekr.20090128083504.1"><vh>Fix rclick</vh></v>
</v>
<v t="ekr.20090304084841.11"><vh>Later</vh>
<v t="ekr.20081215074704.21"><vh>Add drag and drop</vh></v>
<v t="ekr.20090418064921.12"><vh>Qt, vim bindings</vh></v>
<v t="ekr.20081215162017.4"><vh>Allow coloring of script buttons</vh>
<v t="ekr.20090406111739.12"><vh>setWidgetColor (qtGui)</vh></v>
<v t="ekr.20090406111739.13"><vh>setStyleSetting (qtGui)</vh></v>
<v t="ekr.20081121105001.266"></v>
</v>
<v t="ekr.20081124094918.1"><vh>Fix problems with scim</vh></v>
<v t="ekr.20090406111739.10"><vh>Let gui handle hard part of next/prev-line commands</vh></v>
<v t="ekr.20090401110027.1"><vh>Make sure qt plugin supports user icons</vh></v>
</v>
<v t="ekr.20090522102224.3882"><vh>To do First</vh>
<v t="ekr.20090430102239.2"></v>
<v t="ekr.20090426075320.10"></v>
<v t="ekr.20081215074704.16"></v>
</v>
</v>
<v t="ekr.20081121105001.490"><vh>runScrolledMessageDialog</vh>
<v t="leohag.20081205043707.12"><vh>&lt;&lt; no c error&gt;&gt;</vh></v>
<v t="leohag.20081205043707.14"><vh>&lt;&lt; load scrolledmessage plugin &gt;&gt;</vh></v>
<v t="leohag.20081205043707.11"><vh>&lt;&lt; no dialog error &gt;&gt;</vh></v>
<v t="leohag.20081205043707.13"><vh>&lt;&lt; emergency fallback &gt;&gt;</vh></v>
</v>
</vnodes>
<tnodes>
<t tx="ekr.20081121105001.148"></t>
<t tx="ekr.20081121105001.205">class leoQtBody (leoFrame.leoBody):

    """A class that represents the body pane of a Qt window."""

    @others
</t>
<t tx="ekr.20081121105001.206"></t>
<t tx="ekr.20081121105001.207">def __init__ (self,frame,parentFrame):

    trace = False and not g.unitTesting

    # Call the base class constructor.
    leoFrame.leoBody.__init__(self,frame,parentFrame)

    c = self.c
    assert c.frame == frame and frame.c == c

    self.useScintilla = c.config.getBool('qt-use-scintilla')
    self.selectedBackgroundColor = c.config.getString('selected-background-color')
    self.unselectedBackgroundColor = c.config.getString('unselected-background-color')

    # Set the actual gui widget.
    if self.useScintilla:
        self.widget = w = leoQScintillaWidget(
            c.frame.top.textEdit,
            name='body',c=c)
        self.bodyCtrl = w # The widget as seen from Leo's core.
        self.colorizer = leoColor.nullColorizer(c)
    else:
        top = c.frame.top
        sw = top.ui.stackedWidget
        qtWidget = top.ui.richTextEdit # A QTextEdit.
        sw.setCurrentIndex(1)
        self.widget = w = leoQTextEditWidget(
            qtWidget,name = 'body',c=c)
        self.bodyCtrl = w # The widget as seen from Leo's core.

        # Hook up the QSyntaxHighlighter
        self.colorizer = leoQtColorizer(c,w.widget)
        w.acceptRichText = False

    # Config stuff.
    self.trace_onBodyChanged = c.config.getBool('trace_onBodyChanged')
    wrap = c.config.getBool('body_pane_wraps')
    # g.trace('wrap',wrap,self.widget.widget)
    if self.useScintilla:
        pass
    else:
        self.widget.widget.setWordWrapMode(g.choose(wrap,
            QtGui.QTextOption.WordWrap,
            QtGui.QTextOption.NoWrap))
    wrap = g.choose(wrap,"word","none")
    self.wrapState = wrap

    # For multiple body editors.
    self.editor_name = None
    self.editor_v = None
    self.numberOfEditors = 1
    self.totalNumberOfEditors = 1

    if trace: print('qtBody.__init__ %s' % self.widget)
</t>
<t tx="ekr.20081121105001.208">def createBindings (self,w=None):

    '''(qtBody) Create gui-dependent bindings.
    These are *not* made in nullBody instances.'''

    # frame = self.frame ; c = self.c ; k = c.k
    # if not w: w = self.widget

    # c.bind(w,'&lt;Key&gt;', k.masterKeyHandler)

    # def onFocusOut(event,c=c):
        # # This interferes with inserting new nodes.
            # # c.k.setDefaultInputState()
        # self.setEditorColors(
            # bg=c.k.unselected_body_bg_color,
            # fg=c.k.unselected_body_fg_color)
        # # This is required, for example, when typing Alt-Shift-anyArrow in insert mode.
        # # But we suppress coloring in the widget.
        # oldState = k.unboundKeyAction
        # k.unboundKeyAction = k.defaultUnboundKeyAction
        # c.k.showStateAndMode(w=g.app.gui.get_focus(c))
        # k.unboundKeyAction = oldState

    # def onFocusIn(event,c=c):
        # # g.trace('callback')
        # c.k.setDefaultInputState()
        # c.k.showStateAndMode()  # TNB - fix color when window manager returns focus to Leo

    # c.bind(w,'&lt;FocusOut&gt;', onFocusOut)
    # c.bind(w,'&lt;FocusIn&gt;', onFocusIn)

    # table = [
        # ('&lt;Button-1&gt;',  frame.OnBodyClick,          k.masterClickHandler),
        # ('&lt;Button-3&gt;',  frame.OnBodyRClick,         k.masterClick3Handler),
        # ('&lt;Double-1&gt;',  frame.OnBodyDoubleClick,    k.masterDoubleClickHandler),
        # ('&lt;Double-3&gt;',  None,                       k.masterDoubleClick3Handler),
        # ('&lt;Button-2&gt;',  frame.OnPaste,              k.masterClickHandler),
    # ]

    # table2 = (
        # ('&lt;Button-2&gt;',  frame.OnPaste,              k.masterClickHandler),
    # )

    # if c.config.getBool('allow_middle_button_paste'):
        # table.extend(table2)

    # for kind,func,handler in table:
        # def bodyClickCallback(event,handler=handler,func=func):
            # return handler(event,func)

        # c.bind(w,kind,bodyClickCallback)
</t>
<t tx="ekr.20081121105001.209">def getName (self):

    return 'body-widget'
</t>
<t tx="ekr.20081121105001.210">
# Configuration will be handled by style sheets.
def cget(self,*args,**keys):        return None
def configure (self,*args,**keys):  pass
def setEditorColors (self,bg,fg):   pass

def oops (self):
    g.trace('qtBody',g.callers(3))
</t>
<t tx="ekr.20081121105001.211">def appendText (self,s):
    return self.widget.appendText(s)

def bind (self,kind,*args,**keys):
    return self.widget.bind(kind,*args,**keys)

def deleteTextSelection (self):
    return self.widget.deleteTextSelection()

def flashCharacter(self,i,bg='white',fg='red',flashes=3,delay=75):
    return self.widget(i,bg,fg,flashes,delay)

def get(self,i,j=None):
    return self.widget.get(i,j)

def getAllText (self):
    return self.widget.getAllText()

def getFocus (self):
    return self.widget.getFocus()

def getInsertPoint(self):
    return self.widget.getInsertPoint()

def getSelectedText (self):
    return self.widget.getSelectedText()

def getSelectionRange (self,sort=True):
    return self.widget.getSelectionRange(sort)

def getYScrollPosition (self):
    return self.widget.getYScrollPosition()

def insert(self,i,s):
    return self.widget.insert(i,s)

def scrollLines (self,n):
    return self.widget.scrollLines(n)

def see(self,index):
    return self.widget.see(index)

def seeInsertPoint(self):
    return self.widget.seeInsertPoint()

def setAllText (self,s):
    return self.widget.setAllText(s)

def setBackgroundColor (self,color):
    return self.widget.setBackgroundColor(color)

def setFocus (self):
    return self.widget.setFocus()

def setForegroundColor (self,color):
    return self.widget.setForegroundColor(color)

def setInsertPoint (self,pos):
    return self.widget.setInsertPoint(pos)

def setSelectionRange (self,sel):
    i,j = sel
    return self.widget.setSelectionRange(i,j)

def setYScrollPosition (self,i):
    return self.widget.setYScrollPosition(i)
</t>
<t tx="ekr.20081121105001.212"></t>
<t tx="ekr.20081121105001.213">def createEditorFrame (self):

    f = self.c.frame
    inner_f = f.top.ui.leo_body_inner_frame
    body = leoQtBody(f,None)
    w = body.widget.widget

    inner_f.layout().addWidget(w,0,1)
    w.setFocus()

    return inner_f,body.widget
</t>
<t tx="ekr.20081121105001.214">def packEditorLabelWidget (self,w):

    '''Create a Tk label widget.'''

    # if not hasattr(w,'leo_label') or not w.leo_label:
        # # g.trace('w.leo_frame',id(w.leo_frame))
        # w.pack_forget()
        # w.leo_label = Tk.Label(w.leo_frame)
        # w.leo_label.pack(side='top')
        # w.pack(expand=1,fill='both')</t>
<t tx="ekr.20081121105001.215">if 1:
    @others</t>
<t tx="ekr.20081121105001.216"># An override of leoFrame.addEditor.

def addEditor (self,event=None):

    '''Add another editor to the body pane.'''

    g.es_print('add-editor not supported yet',color='red')
    return

    trace = True and not g.unitTesting

    bodyCtrl = self.c.frame.body.bodyCtrl # A leoQTextEditWidget
    self.editorWidgets['1'] = bodyCtrl
    c = self.c ; p = c.currentPosition()
    self.totalNumberOfEditors += 1
    self.numberOfEditors += 1

    if self.numberOfEditors == 2:
        # Inject the ivars into the first editor.
        # The name of the last editor need not be '1'
        d = self.editorWidgets ; keys = d.keys()
        if len(keys) == 1:
            w_old = d.get(keys[0])
            if trace: g.trace('w_old',w_old)
            self.updateInjectedIvars(w_old,p)
            self.selectLabel(w_old) # Immediately create the label in the old editor.
        else:
            g.trace('can not happen: unexpected editorWidgets',d)

    name = '%d' % self.totalNumberOfEditors

    f,w = self.createEditorFrame()
    self.createEditorWidget(f,name,p,w)
    self.editorWidgets[name] = w

    # for pane in panes:
        # self.pb.configurepane(pane,size=minSize)

    # self.pb.updatelayout()
    if trace: g.trace('w',w)
    c.frame.body.bodyCtrl = w

    self.updateInjectedIvars(w,p)
    self.selectLabel(w)
    self.selectEditor(w)
    self.updateEditors()
    c.bodyWantsFocusNow()
</t>
<t tx="ekr.20081121105001.217">def createEditorWidget (self,f,name,p,w):

    trace = False and not g.unitTesting
    c = self.c

    if trace: g.trace(p.h,w)
    #### w = self.createTextWidget(f,name,p,w)
    self.updateInjectedIvars(w,p)
    w.delete(0,'end')
    w.insert('end',p.bodyString())
    w.see(0)
    ##self.setFontFromConfig(w=w)
    ##self.setColorFromConfig(w=w)
    self.createBindings(w=w)
    c.k.completeAllBindingsForWidget(w)
    self.recolorWidget(p,w)

    #### return w
</t>
<t tx="ekr.20081121105001.218">def assignPositionToEditor (self,p):

    '''Called *only* from tree.select to select the present body editor.'''

    c = self.c ; cc = c.chapterController ; w = c.frame.body.bodyCtrl

    # self.updateInjectedIvars(w,p)
    # self.selectLabel(w)

    # g.trace('===',id(w),w.leo_chapter.name,w.leo_p.h)
</t>
<t tx="ekr.20081121105001.219">def cycleEditorFocus (self,event=None):

    '''Cycle keyboard focus between the body text editors.'''

    # c = self.c ; d = self.editorWidgets ; w = c.frame.body.bodyCtrl
    # values = d.values()
    # if len(values) &gt; 1:
        # i = values.index(w) + 1
        # if i == len(values): i = 0
        # w2 = d.values()[i]
        # assert(w!=w2)
        # self.selectEditor(w2)
        # c.frame.body.bodyCtrl = w2
        # # g.pr('***',g.app.gui.widget_name(w2),id(w2))

    # return 'break'
</t>
<t tx="ekr.20081121105001.220">def deleteEditor (self,event=None):

    '''Delete the presently selected body text editor.'''

    # c = self.c ; w = c.frame.body.bodyCtrl ; d = self.editorWidgets

    # if len(d.keys()) == 1: return

    # name = w.leo_name

    # del d [name] 
    # self.pb.delete(name)
    # panes = self.pb.panes()
    # minSize = float(1.0/float(len(panes)))

    # for pane in panes:
        # self.pb.configurepane(pane,size=minSize)

    # # Select another editor.
    # w = d.values()[0]
    # # c.frame.body.bodyCtrl = w # Don't do this now?
    # self.numberOfEditors -= 1
    # self.selectEditor(w)
</t>
<t tx="ekr.20081121105001.221">def findEditorForChapter (self,chapter,p):

    '''Return an editor to be assigned to chapter.'''

    return self.c.frame.body.bodyCtrl

    # c = self.c ; d = self.editorWidgets ; values = d.values()

    # # First, try to match both the chapter and position.
    # if p:
        # for w in values:
            # if (
                # hasattr(w,'leo_chapter') and w.leo_chapter == chapter and
                # hasattr(w,'leo_p') and w.leo_p and w.leo_p == p
            # ):
                # # g.trace('***',id(w),'match chapter and p',p.h)
                # return w

    # # Next, try to match just the chapter.
    # for w in values:
        # if hasattr(w,'leo_chapter') and w.leo_chapter == chapter:
            # # g.trace('***',id(w),'match only chapter',p.h)
            # return w

    # # As a last resort, return the present editor widget.
    # # g.trace('***',id(self.bodyCtrl),'no match',p.h)
    # return c.frame.body.bodyCtrl
</t>
<t tx="ekr.20081121105001.222">def unselectLabel (self,w):

    pass

    # self.createChapterIvar(w)
    # self.packEditorLabelWidget(w)
    # s = self.computeLabel(w)
    # if hasattr(w,'leo_label') and w.leo_label:
        # w.leo_label.configure(text=s,bg='LightSteelBlue1')

def selectLabel (self,w):

    pass

    # if self.numberOfEditors &gt; 1:
        # self.createChapterIvar(w)
        # self.packEditorLabelWidget(w)
        # s = self.computeLabel(w)
        # # g.trace(s,g.callers())
        # if hasattr(w,'leo_label') and w.leo_label:
            # w.leo_label.configure(text=s,bg='white')
    # elif hasattr(w,'leo_label') and w.leo_label:
        # w.leo_label.pack_forget()
        # w.leo_label = None
</t>
<t tx="ekr.20081121105001.223">selectEditorLockout = False

def selectEditor(self,w):

    '''Select editor w and node w.leo_p.'''

    return self.c.frame.body.bodyCtrl

    #  Called by body.onClick and whenever w must be selected.
    # trace = False
    # c = self.c
    # if not w: return self.c.frame.body.bodyCtrl
    # if self.selectEditorLockout: return

    # if w and w == self.c.frame.body.bodyCtrl:
        # if w.leo_p and w.leo_p != c.currentPosition():
            # c.selectPosition(w.leo_p)
            # c.bodyWantsFocusNow()
        # return

    # try:
        # val = None
        # self.selectEditorLockout = True
        # val = self.selectEditorHelper(w)
    # finally:
        # self.selectEditorLockout = False

    # return val # Don't put a return in a finally clause.
</t>
<t tx="ekr.20081121105001.224">def selectEditorHelper (self,w):

    c = self.c ; cc = c.chapterController ; d = self.editorWidgets

    trace = False

    if not w.leo_p:
        g.trace('no w.leo_p') 
        return 'break'

    if trace:
        g.trace('==1',id(w),
            hasattr(w,'leo_chapter') and w.leo_chapter and w.leo_chapter.name,
            hasattr(w,'leo_p') and w.leo_p and w.leo_p.h)

    self.inactivateActiveEditor(w)

    # The actual switch.
    c.frame.body.bodyCtrl = w
    w.leo_active = True

    self.switchToChapter(w)
    self.selectLabel(w)

    if not self.ensurePositionExists(w):
        g.trace('***** no position editor!')
        return 'break'

    if trace:
        g.trace('==2',id(w),
            hasattr(w,'leo_chapter') and w.leo_chapter and w.leo_chapter.name,
            hasattr(w,'leo_p') and w.leo_p and w.leo_p.h)

    # g.trace('expanding ancestors of ',w.leo_p.h,g.callers())
    c.expandAllAncestors(w.leo_p)
    c.selectPosition(w.leo_p) # Calls assignPositionToEditor.
    c.redraw()

    c.recolor_now()
    &lt;&lt; restore the selection, insertion point and the scrollbar &gt;&gt;
    c.bodyWantsFocusNow()
    return 'break'
</t>
<t tx="ekr.20081121105001.225"># g.trace('active:',id(w),'scroll',w.leo_scrollBarSpot,'ins',w.leo_insertSpot)

if w.leo_insertSpot:
    w.setInsertPoint(w.leo_insertSpot)
else:
    w.setInsertPoint(0)

if w.leo_scrollBarSpot is not None:
    first,last = w.leo_scrollBarSpot
    w.yview('moveto',first)
else:
    w.seeInsertPoint()

if w.leo_selection:
    try:
        start,end = w.leo_selection
        w.setSelectionRange(start,end)
    except Exception:
        pass
</t>
<t tx="ekr.20081121105001.226"># Called from addEditor and assignPositionToEditor

def updateEditors (self):

    pass

    # c = self.c ; p = c.currentPosition()
    # d = self.editorWidgets
    # if len(d.keys()) &lt; 2: return # There is only the main widget.

    # for key in d:
        # w = d.get(key)
        # v = w.leo_v
        # if v and v == p.v and w != c.frame.body.bodyCtrl:
            # w.delete(0,'end')
            # w.insert('end',p.bodyString())
            # # g.trace('update',w,v)
            # self.recolorWidget(p,w)

    # c.bodyWantsFocus()
</t>
<t tx="ekr.20081121105001.227"></t>
<t tx="ekr.20081121105001.228">def computeLabel (self,w):

    s = w.leo_label_s

    if hasattr(w,'leo_chapter') and w.leo_chapter:
        s = '%s: %s' % (w.leo_chapter.name,s)

    return s
</t>
<t tx="ekr.20081121105001.229">def createChapterIvar (self,w):

    c = self.c ; cc = c.chapterController

    if not hasattr(w,'leo_chapter') or not w.leo_chapter:
        if cc and self.use_chapters:
            w.leo_chapter = cc.getSelectedChapter()
        else:
            w.leo_chapter = None
</t>
<t tx="ekr.20081121105001.230">def ensurePositionExists(self,w):

    '''Return True if w.leo_p exists or can be reconstituted.'''

    c = self.c

    if c.positionExists(w.leo_p):
        return True
    else:
        g.trace('***** does not exist',w.leo_name)
        for p2 in c.all_positions_with_unique_vnodes_iter():
            if p2.v and p2.v == w.leo_v:
                w.leo_p = p2.copy()
                return True
        else:
             # This *can* happen when selecting a deleted node.
            w.leo_p = c.currentPosition()
            return False
</t>
<t tx="ekr.20081121105001.231">def inactivateActiveEditor(self,w):

    '''Inactivate the previously active editor.'''

    d = self.editorWidgets

    # Don't capture ivars here! assignPositionToEditor keeps them up-to-date. (??)
    for key in d:
        w2 = d.get(key)
        if w2 != w and w2.leo_active:
            w2.leo_active = False
            self.unselectLabel(w2)
            w2.leo_scrollBarSpot = w2.yview()
            w2.leo_insertSpot = w2.getInsertPoint()
            w2.leo_selection = w2.getSelectionRange()
            # g.trace('inactive:',id(w2),'scroll',w2.leo_scrollBarSpot,'ins',w2.leo_insertSpot)
            # g.trace('inactivate',id(w2))
            return
</t>
<t tx="ekr.20081121105001.232">def recolorWidget (self,p,w):

    c = self.c ; old_w = c.frame.body.bodyCtrl

    # g.trace('w',id(w),p.h,len(w.getAllText()))

    # Save.
    c.frame.body.bodyCtrl = w
    try:
        # c.recolor_now(interruptable=False) # Force a complete recoloring.
        c.frame.body.colorizer.colorize(p,incremental=False,interruptable=False)
    finally:
        # Restore.
        c.frame.body.bodyCtrl = old_w
</t>
<t tx="ekr.20081121105001.233">def switchToChapter (self,w):

    '''select w.leo_chapter.'''

    c = self.c ; cc = c.chapterController

    if hasattr(w,'leo_chapter') and w.leo_chapter:
        chapter = w.leo_chapter
        name = chapter and chapter.name
        oldChapter = cc.getSelectedChapter()
        if chapter != oldChapter:
            # g.trace('===','old',oldChapter.name,'new',name,w.leo_p)
            cc.selectChapterByName(name)
            c.bodyWantsFocusNow()
</t>
<t tx="ekr.20081121105001.234"># Called from addEditor and assignPositionToEditor.

def updateInjectedIvars (self,w,p):

    c = self.c ; cc = c.chapterController

    if cc and self.use_chapters:
        w.leo_chapter = cc.getSelectedChapter()
    else:
        w.leo_chapter = None

    w.leo_p = p.copy()
    w.leo_v = w.leo_p.v
    w.leo_label_s = p.h

    # g.trace('   ===', id(w),w.leo_chapter and w.leo_chapter.name,p.h)
</t>
<t tx="ekr.20081121105001.235">class leoQtFindTab (leoFind.findTab):

    '''A subclass of the findTab class containing all Qt Gui code.'''

    if 0: # We can use the base-class ctor.
        def __init__ (self,c,parentFrame):
            leoFind.findTab.__init__(self,c,parentFrame)
                # Init the base class.
                # Calls initGui, createFrame, createBindings &amp; init(c), in that order.

    # Define these to suppress oops messages.
    def createBindings (self): pass
    def createFindTab (self,c,parentFrame): pass
    def createFrame (self,parentFrame): pass

    @others
</t>
<t tx="ekr.20081121105001.236"># leoFind.__init__ calls initGui, createFrame, createBindings &amp; init, in that order.
</t>
<t tx="ekr.20081121105001.237">def initGui (self):

    owner = self

    self.svarDict = {}
        # Keys are ivar names, values are svar objects.

    for ivar in self.intKeys:
        self.svarDict[ivar] = self.svar(owner,ivar)

    # Add a hack for 'entire_outline' radio button.
    ivar = 'entire_outline'
    self.svarDict[ivar] = self.svar(owner,ivar)

    for ivar in self.newStringKeys:
        # "radio-find-type", "radio-search-scope"
        self.svarDict[ivar] = self.svar(owner,ivar)
</t>
<t tx="ekr.20081121105001.238">def init (self,c):

    '''Init the widgets of the 'Find' tab.'''

    # g.trace('leoQtFindTab.init')

    self.createIvars()
    self.initIvars()
    self.initTextWidgets()
    self.initCheckBoxes()
    self.initRadioButtons()
</t>
<t tx="ekr.20081121105001.239">def createIvars (self):

    c = self.c ; w = c.frame.top.ui # A Window ui object.

    # Bind boxes to Window objects.
    self.widgetsDict = {} # Keys are ivars, values are Qt widgets.
    data = (
        ('find_ctrl',       findTextWrapper(w.findPattern,'find-widget',c)),
        ('change_ctrl',     findTextWrapper(w.findChange,'change-widget',c)),
        ('whole_word',      w.checkBoxWholeWord),
        ('ignore_case',     w.checkBoxIgnoreCase),
        ('wrap',            w.checkBoxWrapAround),
        ('reverse',         w.checkBoxReverse),
        ('pattern_match',   w.checkBoxRegexp),
        ('mark_finds',      w.checkBoxMarkFinds),
        ('entire_outline',  w.checkBoxEntireOutline),
        ('suboutline_only', w.checkBoxSubroutineOnly),  
        ('node_only',       w.checkBoxNodeOnly),
        ('search_headline', w.checkBoxSearchHeadline),
        ('search_body',     w.checkBoxSearchBody),
        ('mark_changes',    w.checkBoxMarkChanges),
        ('batch', None),
    )
    for ivar,widget in data:
        setattr(self,ivar,widget)
        self.widgetsDict[ivar] = widget
        # g.trace(ivar,widget)
</t>
<t tx="ekr.20081121105001.240">def initIvars(self):

    c = self.c

    # Separate c.ivars are much more convenient than a svarDict.
    for ivar in self.intKeys:
        # Get ivars from @settings.
        val = c.config.getBool(ivar)
        setattr(self,ivar,val)
        val = g.choose(val,1,0)
        svar = self.svarDict.get(ivar)
        if svar:
            svar.set(val)

        # g.trace(ivar,val)
</t>
<t tx="ekr.20081121105001.241">def initTextWidgets(self):

    '''Init the find/change text areas.'''

    c = self.c

    table = (
        (self.find_ctrl,    "find_text",    '&lt;find pattern here&gt;'),
        (self.change_ctrl,  "change_text",  ''),
    )

    for w,setting,defaultText in table:
        # w is a textWrapper object
        w.setAllText(c.config.getString(setting) or defaultText)
</t>
<t tx="ekr.20081121105001.242">def initCheckBoxes (self):

    for ivar,key in (
        ("pattern_match","pattern-search"),
    ):
        svar = self.svarDict[ivar].get()
        if svar:
            self.svarDict["radio-find-type"].set(key)
            w = self.widgetsDict.get(key)
            if w: w.setChecked(True)
            break
    else:
        self.svarDict["radio-find-type"].set("plain-search")

    aList = (
        'ignore_case','mark_changes','mark_finds',
        'pattern_match','reverse','search_body','search_headline',
        'whole_word','wrap',
        'node_only','suboutline_only','entire_outline',
    )

    for ivar in aList:
        svar = self.svarDict.get(ivar)
        if svar:
            # w is a QCheckBox or a QRadioButton.
            w = self.widgetsDict.get(ivar)
            if w:
                val = svar.get()
                svar.setWidget(w)
                svar.set(val)
                if isinstance(w,QtGui.QCheckBox):
                    def checkBoxCallback(val,svar=svar):
                        svar.set(val)
                    w.connect(w,
                        QtCore.SIGNAL("stateChanged(int)"),
                        checkBoxCallback)
                else:
                    def radioButtonCallback(val,svar=svar):
                        svar.set(val)
                    w.connect(w,
                        QtCore.SIGNAL("clicked(bool)"),
                        radioButtonCallback)
            else: g.trace('*** no w',ivar)
        else: g.trace('*** no svar',ivar)
</t>
<t tx="ekr.20081121105001.243">def initRadioButtons (self):

    scopeSvar = self.svarDict.get('radio-search-scope')

    table = (
        ("suboutline_only","suboutline-only"),
        ("node_only","node-only"))

    for ivar,key in table:
        svar = self.svarDict.get(ivar)
        if svar:
            val = svar.get()
            if val:
                scopeSvar.init(key)
                break
    else:
        scopeSvar.init('entire-outline')
        self.svarDict.get('entire_outline').init(True)

    w = self.widgetsDict.get(key)
    if w: w.setChecked(True)

    # g.trace(scopeSvar.get())
</t>
<t tx="ekr.20081121105001.244">class svar:
    '''A class like Tk's IntVar and StringVar classes.'''

    @others

</t>
<t tx="ekr.20081121105001.245"># This is the same as the Tk code because we simulate Tk svars.</t>
<t tx="ekr.20081121105001.246">def getOption (self,ivar):

    var = self.svarDict.get(ivar)

    if var:
        val = var.get()
        # g.trace('ivar %s = %s' % (ivar,val))
        return val
    else:
        # g.trace('bad ivar name: %s' % ivar)
        return None
</t>
<t tx="ekr.20081121105001.247">def setOption (self,ivar,val):

    if ivar in self.intKeys:
        if val is not None:
            svar = self.svarDict.get(ivar)
            svar.set(val)
            # g.trace('ivar %s = %s' % (ivar,val))

    elif not g.app.unitTesting:
        g.trace('oops: bad find ivar %s' % ivar)
</t>
<t tx="ekr.20081121105001.248">def toggleOption (self,ivar):

    if ivar in self.intKeys:
        var = self.svarDict.get(ivar)
        val = not var.get()
        var.set(val)
        # g.trace('%s = %s' % (ivar,val),var)
    else:
        g.trace('oops: bad find ivar %s' % ivar)
</t>
<t tx="ekr.20081121105001.249">class leoQtFrame (leoFrame.leoFrame):

    """A class that represents a Leo window rendered in qt."""

    @others
</t>
<t tx="ekr.20081121105001.250"></t>
<t tx="ekr.20081121105001.251">def __init__(self,title,gui):

    # Init the base class.
    leoFrame.leoFrame.__init__(self,gui)

    self.title = title
    self.initComplete = False # Set by initCompleteHint().
    leoQtFrame.instances += 1

    self.c = None # Set in finishCreate.
    self.iconBarClass = self.qtIconBarClass
    self.statusLineClass = self.qtStatusLineClass
    self.iconBar = None

    self.trace_status_line = None # Set in finishCreate.

    &lt;&lt; set the leoQtFrame ivars &gt;&gt;

    self.minibufferVisible = True
</t>
<t tx="ekr.20081121105001.252"># "Official ivars created in createLeoFrame and its allies.
self.bar1 = None
self.bar2 = None
self.body = None
self.f1 = self.f2 = None
self.findPanel = None # Inited when first opened.
self.iconBarComponentName = 'iconBar'
self.iconFrame = None 
self.log = None
self.canvas = None
self.outerFrame = None
self.statusFrame = None
self.statusLineComponentName = 'statusLine'
self.statusText = None 
self.statusLabel = None 
self.top = None # This will be a class Window object.
self.tree = None
# self.treeBar = None # Replaced by injected frame.canvas.leo_treeBar.

# Used by event handlers...
self.controlKeyIsDown = False # For control-drags
self.draggedItem = None
self.isActive = True
self.redrawCount = 0
self.wantedWidget = None
self.wantedCallbackScheduled = False
self.scrollWay = None
</t>
<t tx="ekr.20081121105001.253">def __repr__ (self):

    return "&lt;leoQtFrame: %s&gt;" % self.title
</t>
<t tx="ekr.20081121105001.254">def finishCreate (self,c):

    f = self ; f.c = c

    # g.trace('***qtFrame')

    self.bigTree           = c.config.getBool('big_outline_pane')
    self.trace_status_line = c.config.getBool('trace_status_line')
    self.use_chapters      = c.config.getBool('use_chapters')
    self.use_chapter_tabs  = c.config.getBool('use_chapter_tabs')

    # xx todo
    f.top = DynamicWindow(c)
    g.app.gui.attachLeoIcon(f.top)
    f.top.setWindowTitle(self.title)
    f.top.show()

    # This must be done after creating the commander.
    f.splitVerticalFlag,f.ratio,f.secondary_ratio = f.initialRatios()
    # # f.createOuterFrames()
    f.createIconBar() # A base class method.
    # # f.createLeoSplitters(f.outerFrame)
    f.createSplitterComponents()
    f.createStatusLine() # A base class method.
    f.createFirstTreeNode() # Call the base-class method.
    f.menu = leoQtMenu(f)
    c.setLog()
    g.app.windowList.append(f)
    c.initVersion()
    c.signOnWithVersion()
    f.miniBufferWidget = leoQtMinibuffer(c)
    c.bodyWantsFocusNow()
</t>
<t tx="ekr.20081121105001.255">def createSplitterComponents (self):

    f = self ; c = f.c

    f.tree  = leoQtTree(c,f)
    f.log   = leoQtLog(f,None)
    f.body  = leoQtBody(f,None)

    if f.use_chapters:
        c.chapterController = cc = leoChapters.chapterController(c)

    # # Create the canvas, tree, log and body.
    # if f.use_chapters:
        # c.chapterController = cc = leoChapters.chapterController(c)

    # # split1.pane1 is the secondary splitter.

    # if self.bigTree: # Put outline in the main splitter.
        # if self.use_chapters and self.use_chapter_tabs:
            # cc.tt = leoQtTreeTab(c,f.split1Pane2,cc)
        # f.canvas = f.createCanvas(f.split1Pane1)
        # f.tree  = leoQtTree(c,f,f.canvas)
        # f.log   = leoQtLog(f,f.split2Pane2)
        # f.body  = leoQtBody(f,f.split2Pane1)
    # else:
        # if self.use_chapters and self.use_chapter_tabs:
            # cc.tt = leoQtTreeTab(c,f.split2Pane1,cc)
        # f.canvas = f.createCanvas(f.split2Pane1)
        # f.tree   = leoQtTree(c,f,f.canvas)
        # f.log    = leoQtLog(f,f.split2Pane2)
        # f.body   = leoQtBody(f,f.split1Pane2)

    # # Yes, this an "official" ivar: this is a kludge.
    # # f.bodyCtrl = f.body.bodyCtrl

    # # Configure.
    # f.setTabWidth(c.tab_width)
    # f.reconfigurePanes()
    # f.body.setFontFromConfig()
    # f.body.setColorFromConfig()
</t>
<t tx="ekr.20081121105001.256">def initCompleteHint (self):

    '''A kludge: called to enable text changed events.'''

    self.initComplete = True
    # g.trace(self.c)
</t>
<t tx="ekr.20081121105001.257"></t>
<t tx="ekr.20081121105001.258">def destroyAllObjects (self):

    """Clear all links to objects in a Leo window."""

    frame = self ; c = self.c

    # g.printGcAll()

    # Do this first.
    &lt;&lt; clear all vnodes and tnodes in the tree &gt;&gt;

    if 1:
        # Destroy all ivars in subcommanders.
        g.clearAllIvars(c.atFileCommands)
        if c.chapterController: # New in Leo 4.4.3 b1.
            g.clearAllIvars(c.chapterController)
        g.clearAllIvars(c.fileCommands)
        g.clearAllIvars(c.keyHandler) # New in Leo 4.4.3 b1.
        g.clearAllIvars(c.importCommands)
        g.clearAllIvars(c.tangleCommands)
        g.clearAllIvars(c.undoer)
        g.clearAllIvars(c)
    if 0: # No need.
        tree = frame.tree ; body = self.body
        g.clearAllIvars(body.colorizer)
        g.clearAllIvars(body)
        g.clearAllIvars(tree)

</t>
<t tx="ekr.20081121105001.259"># Using a dict here is essential for adequate speed.
vList = [] ; tDict = {}

for p in c.all_positions_with_unique_vnodes_iter():
    vList.append(p.v)
    if p.v.t:
        key = id(p.v.t)
        if key not in tDict:
            tDict[key] = p.v.t

for key in tDict:
    g.clearAllIvars(tDict[key])

for v in vList:
    g.clearAllIvars(v)

vList = [] ; tDict = {} # Remove these references immediately.
</t>
<t tx="ekr.20081121105001.260">def destroySelf (self):

    # Remember these: we are about to destroy all of our ivars!
    c,top = self.c,self.top 

    # Indicate that the commander is no longer valid.
    c.exists = False

    if 0: # We can't do this unless we unhook the event filter.
        # Destroys all the objects of the commander.
        self.destroyAllObjects()

    c.exists = False # Make sure this one ivar has not been destroyed.

    # g.trace('qtFrame',c,g.callers(4))
    top.close()

</t>
<t tx="ekr.20081121105001.261">class qtStatusLineClass:

    '''A class representing the status line.'''

    @others
</t>
<t tx="ekr.20081121105001.262">def __init__ (self,c,parentFrame):

    self.c = c
    self.statusBar = c.frame.top.statusBar
    self.lastFcol= 0
    self.lastRow = 0
    self.lastCol = 0

    # Create the text widgets.
    self.textWidget1 = w1 = QtGui.QLineEdit(self.statusBar)
    self.textWidget2 = w2 = QtGui.QLineEdit(self.statusBar)
    w1.setObjectName('status1')
    w2.setObjectName('status2')
    self.statusBar.addWidget(w1,True)
    self.statusBar.addWidget(w2,True)
    self.put('')
    self.update()
    c.frame.top.setStyleSheets()
</t>
<t tx="ekr.20081121105001.263">def disable (self,background=None): pass
def enable(self,background="white"):pass
def getFrame (self):                return None
def isEnabled(self):                return True
def onActivate (self,event=None):   pass
def pack (self):                    pass
def setBindings (self):             pass
def unpack (self):                  pass

hide = unpack
show = pack

</t>
<t tx="ekr.20081121105001.264">def clear (self):
    self.put('')

def get (self):
    return self.textWidget2.text()

def put(self,s,color=None):
    self.put_helper(s,self.textWidget2)

def put1(self,s,color=None):
    self.put_helper(s,self.textWidget1)

def put_helper(self,s,w):
    # w.setEnabled(True)
    if sys.platform.startswith('linux'):
        # Work around an apparent Qt bug.
        s = g.toEncodedString(s,'ascii',reportErrors=False)
    w.setText(s)
    # w.setEnabled(False)
</t>
<t tx="ekr.20081121105001.265">def update (self):
    if g.app.killed: return

    c = self.c ; body = c.frame.body

    # QTextEdit
    te = body.widget.widget
    cr = te.textCursor()
    bl = cr.block()

    col = cr.columnNumber()
    row = bl.blockNumber() + 1
    line = bl.text()

    if col &gt; 0:
        s2 = line[0:col]        
        col = g.computeWidth (s2,c.tab_width)
    fcol = col + c.currentPosition().textOffset()
    self.put1(
        "line: %d, col: %d, fcol: %d" % (row,col,fcol))
    self.lastRow = row
    self.lastCol = col
    self.lastFcol = fcol
</t>
<t tx="ekr.20081121105001.266">class qtIconBarClass:

    '''A class representing the singleton Icon bar'''

    @others
</t>
<t tx="ekr.20081121105001.267">def __init__ (self,c,parentFrame):

    self.c = c
    self.parentFrame = parentFrame
    self.w = c.frame.top.iconBar # A QToolBar.
    self.actions = []

    # Options
    self.buttonColor = c.config.getString('qt-button-color')

    # g.app.iconWidgetCount = 0
</t>
<t tx="ekr.20081121105001.268">def addRow(self,height=None):   pass
def getFrame (self):            return None
def getNewFrame (self):         return None
def pack (self):                pass
def unpack (self):              pass

hide = unpack
show = pack
</t>
<t tx="ekr.20081121105001.269">def add(self,*args,**keys):

    '''Add a button to the icon bar.'''

    c = self.c
    command = keys.get('command')
    text = keys.get('text')
    # able to specify low-level QAction directly (QPushButton not forced)
    qaction = keys.get('qaction')

    if not text and not qaction:
        g.es('bad toolbar item')


    # imagefile = keys.get('imagefile')
    # image = keys.get('image')

    class leoIconBarButton (QtGui.QWidgetAction):
        def __init__ (self,parent,text,toolbar):
            QtGui.QWidgetAction.__init__(self,parent)
            self.button = None # set below
            self.text = text
            self.toolbar = toolbar
        def createWidget (self,parent):
            self.button = b = QtGui.QPushButton(self.text,parent)
            g.app.gui.setWidgetColor(b,
                widgetKind='QPushButton',
                selector='background-color',
                colorName = self.toolbar.buttonColor)
            return b

    if qaction is None:
        action = leoIconBarButton(parent=self.w,text=text,toolbar=self)
    else:
        action = qaction

    self.w.addAction(action)

    self.actions.append(action)
    b = self.w.widgetForAction(action)

    b.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

    def delete_callback(action=action,):
        self.w.removeAction(action)

    b.leo_removeAction = rb = QtGui.QAction('Remove Button' ,b)

    b.addAction(rb)
    rb.connect(rb, QtCore.SIGNAL("triggered()"), delete_callback)

    if command:
        def button_callback(c=c,command=command):
            g.trace('command',command.__name__)
            val = command()
            if c.exists:
                c.bodyWantsFocus()
                c.outerUpdate()
            return val

        self.w.connect(b,
            QtCore.SIGNAL("clicked()"),
            button_callback)

    return action
</t>
<t tx="ekr.20081121105001.270">def addRowIfNeeded (self):

    '''Add a new icon row if there are too many widgets.'''

    # n = g.app.iconWidgetCount

    # if n &gt;= self.widgets_per_row:
        # g.app.iconWidgetCount = 0
        # self.addRow()

    # g.app.iconWidgetCount += 1
</t>
<t tx="ekr.20081121105001.271">def addWidget (self,w):

    self.w.addWidget(w)
</t>
<t tx="ekr.20081121105001.272">def clear(self):

    """Destroy all the widgets in the icon bar"""

    self.w.clear()
    self.actions = []

    g.app.iconWidgetCount = 0
</t>
<t tx="ekr.20081121105001.273">def deleteButton (self,w):
    """ w is button """

    #g.trace(w, '##')    

    self.w.removeAction(w)

    self.c.bodyWantsFocus()
    self.c.outerUpdate()
</t>
<t tx="ekr.20081121105001.274">def setCommandForButton(self,button,command):

    if command:
        # button is a leoIconBarButton.
        QtCore.QObject.connect(button.button,
            QtCore.SIGNAL("clicked()"),command)
</t>
<t tx="ekr.20081121105001.275"></t>
<t tx="ekr.20081121105001.276">def showMinibuffer (self):

    '''Make the minibuffer visible.'''

    # frame = self

    # if not frame.minibufferVisible:
        # frame.minibufferFrame.pack(side='bottom',fill='x')
        # frame.minibufferVisible = True
</t>
<t tx="ekr.20081121105001.277">def hideMinibuffer (self):

    '''Hide the minibuffer.'''

    # frame = self

    # if frame.minibufferVisible:
        # frame.minibufferFrame.pack_forget()
        # frame.minibufferVisible = False
</t>
<t tx="ekr.20081121105001.278">def setMinibufferBindings (self):

    '''Create bindings for the minibuffer..'''

    pass
</t>
<t tx="ekr.20081121105001.279"></t>
<t tx="ekr.20081121105001.280">def configureBar (self,bar,verticalFlag):

    c = self.c

    # Get configuration settings.
    w = c.config.getInt("split_bar_width")
    if not w or w &lt; 1: w = 7
    relief = c.config.get("split_bar_relief","relief")
    if not relief: relief = "flat"
    color = c.config.getColor("split_bar_color")
    if not color: color = "LightSteelBlue2"

    try:
        if verticalFlag:
            # Panes arranged vertically; horizontal splitter bar
            bar.configure(relief=relief,height=w,bg=color,cursor="sb_v_double_arrow")
        else:
            # Panes arranged horizontally; vertical splitter bar
            bar.configure(relief=relief,width=w,bg=color,cursor="sb_h_double_arrow")
    except: # Could be a user error. Use all defaults
        g.es("exception in user configuration for splitbar")
        g.es_exception()
        if verticalFlag:
            # Panes arranged vertically; horizontal splitter bar
            bar.configure(height=7,cursor="sb_v_double_arrow")
        else:
            # Panes arranged horizontally; vertical splitter bar
            bar.configure(width=7,cursor="sb_h_double_arrow")
</t>
<t tx="ekr.20081121105001.281">def configureBarsFromConfig (self):

    c = self.c

    w = c.config.getInt("split_bar_width")
    if not w or w &lt; 1: w = 7

    relief = c.config.get("split_bar_relief","relief")
    if not relief or relief == "": relief = "flat"

    color = c.config.getColor("split_bar_color")
    if not color or color == "": color = "LightSteelBlue2"

    if self.splitVerticalFlag:
        bar1,bar2=self.bar1,self.bar2
    else:
        bar1,bar2=self.bar2,self.bar1

    try:
        bar1.configure(relief=relief,height=w,bg=color)
        bar2.configure(relief=relief,width=w,bg=color)
    except: # Could be a user error.
        g.es("exception in user configuration for splitbar")
        g.es_exception()
</t>
<t tx="ekr.20081121105001.282">def reconfigureFromConfig (self):

    frame = self ; c = frame.c

    frame.tree.setFontFromConfig()
    frame.configureBarsFromConfig()

    frame.body.setFontFromConfig()
    frame.body.setColorFromConfig()

    frame.setTabWidth(c.tab_width)
    frame.log.setFontFromConfig()
    frame.log.setColorFromConfig()

    c.redraw()
</t>
<t tx="ekr.20081121105001.283">def setInitialWindowGeometry(self):

    """Set the position and size of the frame to config params."""

    c = self.c

    h = c.config.getInt("initial_window_height") or 500
    w = c.config.getInt("initial_window_width") or 600
    x = c.config.getInt("initial_window_left") or 10
    y = c.config.getInt("initial_window_top") or 10

    if h and w and x and y:
        self.setTopGeometry(w,h,x,y)
</t>
<t tx="ekr.20081121105001.284">def setTabWidth (self, w):

    return

    # try: # This can fail when called from scripts
        # # Use the present font for computations.
        # font = self.body.bodyCtrl.cget("font") # 2007/10/27
        # root = g.app.root # 4/3/03: must specify root so idle window will work properly.
        # font = tkFont.Font(root=root,font=font)
        # tabw = font.measure(" " * abs(w)) # 7/2/02
        # self.body.bodyCtrl.configure(tabs=tabw)
        # self.tab_width = w
        # # g.trace(w,tabw)
    # except:
        # g.es_exception()
</t>
<t tx="ekr.20081121105001.285">def setWrap (self,p):

    c = self.c
    theDict = c.scanAllDirectives(p)
    if not theDict: return

    return

    # wrap = theDict.get("wrap")
    # if self.body.wrapState == wrap: return

    # self.body.wrapState = wrap
    # w = self.body.bodyCtrl

    # # g.trace(wrap)
    # if wrap:
        # w.configure(wrap="word") # 2007/10/25
        # w.leo_bodyXBar.pack_forget() # 2007/10/31
    # else:
        # w.configure(wrap="none")
        # # Bug fix: 3/10/05: We must unpack the text area to make the scrollbar visible.
        # w.pack_forget()  # 2007/10/25
        # w.leo_bodyXBar.pack(side="bottom", fill="x") # 2007/10/31
        # w.pack(expand=1,fill="both")  # 2007/10/25
</t>
<t tx="ekr.20081121105001.286">def reconfigurePanes (self):

    return

    # c = self.c

    # border = c.config.getInt('additional_body_text_border')
    # if border == None: border = 0

    # # The body pane needs a _much_ bigger border when tiling horizontally.
    # border = g.choose(self.splitVerticalFlag,2+border,6+border)
    # self.body.bodyCtrl.configure(bd=border) # 2007/10/25

    # # The log pane needs a slightly bigger border when tiling vertically.
    # border = g.choose(self.splitVerticalFlag,4,2) 
    # self.log.configureBorder(border)
</t>
<t tx="ekr.20081121105001.287">def resizePanesToRatio(self,ratio,ratio2):

    #g.trace(ratio,ratio2,g.callers())

    self.divideLeoSplitter(self.splitVerticalFlag,ratio)
    self.divideLeoSplitter(not self.splitVerticalFlag,ratio2)
</t>
<t tx="ekr.20081121105001.288"></t>
<t tx="ekr.20081121105001.289"># Called from quit logic and when user closes the window.
# Returns True if the close happened.

def OnCloseLeoEvent(self):

    f = self ; c = f.c

    if c.inCommand:
        # g.trace('requesting window close')
        c.requestCloseWindow = True
    else:
        g.app.closeLeoWindow(self)
</t>
<t tx="ekr.20081121105001.290">def OnControlKeyDown (self,event=None):

    self.controlKeyIsDown = True

def OnControlKeyUp (self,event=None):

    self.controlKeyIsDown = False
</t>
<t tx="ekr.20081121105001.291">def OnActivateBody (self,event=None):

    # try:
        # frame = self ; c = frame.c
        # c.setLog()
        # w = c.get_focus()
        # if w != c.frame.body.bodyCtrl:
            # frame.tree.OnDeactivate()
        # c.bodyWantsFocusNow()
    # except:
        # g.es_event_exception("activate body")

    return 'break'
</t>
<t tx="ekr.20081121105001.292">def OnActivateLeoEvent(self,event=None):

    '''Handle a click anywhere in the Leo window.'''

    self.c.setLog()

def OnDeactivateLeoEvent(self,event=None):

    pass # This causes problems on the Mac.
</t>
<t tx="ekr.20081121105001.293">def OnActivateTree (self,event=None):

    try:
        frame = self ; c = frame.c
        c.setLog()

        if 0: # Do NOT do this here!
            # OnActivateTree can get called when the tree gets DE-activated!!
            c.bodyWantsFocus()

    except:
        g.es_event_exception("activate tree")
</t>
<t tx="ekr.20081121105001.294">def OnBodyClick (self,event=None):

    try:
        c = self.c ; p = c.currentPosition()
        if not g.doHook("bodyclick1",c=c,p=p,v=p,event=event):
            self.OnActivateBody(event=event)
            c.k.showStateAndMode(w=c.frame.body.bodyCtrl)
        g.doHook("bodyclick2",c=c,p=p,v=p,event=event)
    except:
        g.es_event_exception("bodyclick")

def OnBodyRClick(self,event=None):

    try:
        c = self.c ; p = c.currentPosition()
        if not g.doHook("bodyrclick1",c=c,p=p,v=p,event=event):
            c.k.showStateAndMode(w=c.frame.body.bodyCtrl)
        g.doHook("bodyrclick2",c=c,p=p,v=p,event=event)
    except:
        g.es_event_exception("iconrclick")
</t>
<t tx="ekr.20081121105001.295">def OnBodyDoubleClick (self,event=None):

    try:
        c = self.c ; p = c.currentPosition()
        if event and not g.doHook("bodydclick1",c=c,p=p,v=p,event=event):
            c.editCommands.extendToWord(event) # Handles unicode properly.
            c.k.showStateAndMode(w=c.frame.body.bodyCtrl)
        g.doHook("bodydclick2",c=c,p=p,v=p,event=event)
    except:
        g.es_event_exception("bodydclick")

    return "break" # Restore this to handle proper double-click logic.
</t>
<t tx="ekr.20081121105001.296"></t>
<t tx="ekr.20081121105001.297"></t>
<t tx="ekr.20081121105001.298">def contractPane (self,event=None):

    '''Contract the selected pane.'''

    # f = self ; c = f.c
    # w = c.get_requested_focus()
    # wname = c.widget_name(w)

    # # g.trace(wname)
    # if not w: return

    # if wname.startswith('body'):
        # f.contractBodyPane()
    # elif wname.startswith('log'):
        # f.contractLogPane()
    # elif wname.startswith('head') or wname.startswith('canvas'):
        # f.contractOutlinePane()
</t>
<t tx="ekr.20081121105001.299">def expandPane (self,event=None):

    '''Expand the selected pane.'''

    # f = self ; c = f.c

    # w = c.get_requested_focus()
    # wname = c.widget_name(w)

    # # g.trace(wname)
    # if not w: return

    # if wname.startswith('body'):
        # f.expandBodyPane()
    # elif wname.startswith('log'):
        # f.expandLogPane()
    # elif wname.startswith('head') or wname.startswith('canvas'):
        # f.expandOutlinePane()
</t>
<t tx="ekr.20081121105001.300">def fullyExpandPane (self,event=None):

    '''Fully expand the selected pane.'''

    # f = self ; c = f.c

    # w = c.get_requested_focus()
    # wname = c.widget_name(w)

    # # g.trace(wname)
    # if not w: return

    # if wname.startswith('body'):
        # f.fullyExpandBodyPane()
    # elif wname.startswith('log'):
        # f.fullyExpandLogPane()
    # elif wname.startswith('head') or wname.startswith('canvas'):
        # f.fullyExpandOutlinePane()
</t>
<t tx="ekr.20081121105001.301">def hidePane (self,event=None):

    '''Completely contract the selected pane.'''

    # f = self ; c = f.c

    # w = c.get_requested_focus()
    # wname = c.widget_name(w)

    # g.trace(wname)
    # if not w: return

    # if wname.startswith('body'):
        # f.hideBodyPane()
        # c.treeWantsFocusNow()
    # elif wname.startswith('log'):
        # f.hideLogPane()
        # c.bodyWantsFocusNow()
    # elif wname.startswith('head') or wname.startswith('canvas'):
        # f.hideOutlinePane()
        # c.bodyWantsFocusNow()
</t>
<t tx="ekr.20081121105001.302">@ The first arg to divideLeoSplitter means the following:

    f.splitVerticalFlag: use the primary   (tree/body) ratio.
not f.splitVerticalFlag: use the secondary (tree/log) ratio.
@c

def contractBodyPane (self,event=None):
    '''Contract the body pane.'''
    f = self ; r = min(1.0,f.ratio+0.1)
    f.divideLeoSplitter(f.splitVerticalFlag,r)

def contractLogPane (self,event=None):
    '''Contract the log pane.'''
    f = self ; r = min(1.0,f.ratio+0.1)
    f.divideLeoSplitter(not f.splitVerticalFlag,r)

def contractOutlinePane (self,event=None):
    '''Contract the outline pane.'''
    f = self ; r = max(0.0,f.ratio-0.1)
    f.divideLeoSplitter(f.splitVerticalFlag,r)

def expandBodyPane (self,event=None):
    '''Expand the body pane.'''
    self.contractOutlinePane()

def expandLogPane(self,event=None):
    '''Expand the log pane.'''
    f = self ; r = max(0.0,f.ratio-0.1)
    f.divideLeoSplitter(not f.splitVerticalFlag,r)

def expandOutlinePane (self,event=None):
    '''Expand the outline pane.'''
    self.contractBodyPane()
</t>
<t tx="ekr.20081121105001.303">def fullyExpandBodyPane (self,event=None):
    '''Fully expand the body pane.'''
    f = self
    f.divideLeoSplitter(f.splitVerticalFlag,0.0)

def fullyExpandLogPane (self,event=None):
    '''Fully expand the log pane.'''
    f = self
    f.divideLeoSplitter(not f.splitVerticalFlag,0.0)

def fullyExpandOutlinePane (self,event=None):
    '''Fully expand the outline pane.'''
    f = self
    f.divideLeoSplitter(f.splitVerticalFlag,1.0)

def hideBodyPane (self,event=None):
    '''Completely contract the body pane.'''
    f = self
    f.divideLeoSplitter(f.splitVerticalFlag,1.0)

def hideLogPane (self,event=None):
    '''Completely contract the log pane.'''
    f = self
    f.divideLeoSplitter(not f.splitVerticalFlag,1.0)

def hideOutlinePane (self,event=None):
    '''Completely contract the outline pane.'''
    f = self
    f.divideLeoSplitter(f.splitVerticalFlag,0.0)
</t>
<t tx="ekr.20081121105001.304"></t>
<t tx="ekr.20081121105001.305">def toggleActivePane (self,event=None):

    '''Toggle the focus between the outline and body panes.'''

    frame = self ; c = frame.c

    if c.get_focus() == frame.body.bodyCtrl: # 2007/10/25
        c.treeWantsFocusNow()
    else:
        c.endEditing()
        c.bodyWantsFocusNow()
</t>
<t tx="ekr.20081121105001.306">def cascade (self,event=None):

    '''Cascade all Leo windows.'''

    # x,y,delta = 10,10,10
    # for frame in g.app.windowList:
        # top = frame.top

        # # Compute w,h
        # top.update_idletasks() # Required to get proper info.
        # geom = top.geometry() # geom = "WidthxHeight+XOffset+YOffset"
        # dim,junkx,junky = geom.split('+')
        # w,h = dim.split('x')
        # w,h = int(w),int(h)

        # # Set new x,y and old w,h
        # frame.setTopGeometry(w,h,x,y,adjustSize=False)

        # # Compute the new offsets.
        # x += 30 ; y += 30
        # if x &gt; 200:
            # x = 10 + delta ; y = 40 + delta
            # delta += 10
</t>
<t tx="ekr.20081121105001.307">def equalSizedPanes (self,event=None):

    '''Make the outline and body panes have the same size.'''

    frame = self
    frame.resizePanesToRatio(0.5,frame.secondary_ratio)
</t>
<t tx="ekr.20081121105001.308">def hideLogWindow (self,event=None):

    frame = self

    frame.divideLeoSplitter2(0.99, not frame.splitVerticalFlag)
</t>
<t tx="ekr.20081121105001.309">def minimizeAll (self,event=None):

    '''Minimize all Leo's windows.'''

    self.minimize(g.app.pythonFrame)
    for frame in g.app.windowList:
        self.minimize(frame)
        self.minimize(frame.findPanel)

def minimize(self,frame):

    pass

    # if frame and frame.top.state() == "normal":
        # frame.top.iconify()
</t>
<t tx="ekr.20081121105001.310"># The key invariant: self.splitVerticalFlag tells the alignment of the main splitter.

def toggleSplitDirection (self,event=None):

    '''Toggle the split direction in the present Leo window.'''

    frame = self ; top = frame.top

    for w in (top.splitter,top.splitter_2):
        w.setOrientation(
            g.choose(w.orientation() == QtCore.Qt.Horizontal,
                QtCore.Qt.Vertical,QtCore.Qt.Horizontal))</t>
<t tx="ekr.20081121105001.311">def toggleQtSplitDirection (self,verticalFlag):

    # Abbreviations.
    frame = self
    # bar1 = self.bar1 ; bar2 = self.bar2
    # split1Pane1,split1Pane2 = self.split1Pane1,self.split1Pane2
    # split2Pane1,split2Pane2 = self.split2Pane1,self.split2Pane2
    # # Reconfigure the bars.
    # bar1.place_forget()
    # bar2.place_forget()
    # self.configureBar(bar1,verticalFlag)
    # self.configureBar(bar2,not verticalFlag)
    # # Make the initial placements again.
    # self.placeSplitter(bar1,split1Pane1,split1Pane2,verticalFlag)
    # self.placeSplitter(bar2,split2Pane1,split2Pane2,not verticalFlag)
    # # Adjust the log and body panes to give more room around the bars.
    # self.reconfigurePanes()
    # # Redraw with an appropriate ratio.
    # vflag,ratio,secondary_ratio = frame.initialRatios()
    # self.resizePanesToRatio(ratio,secondary_ratio)
</t>
<t tx="ekr.20081121105001.312">def resizeToScreen (self,event=None):

    '''Resize the Leo window so it fill the entire screen.'''

    top = self.top

    # w = top.winfo_screenwidth()
    # h = top.winfo_screenheight()

    # if sys.platform.startswith('win'):
        # top.state('zoomed')
    # elif sys.platform == 'darwin':
        # # Must leave room to get at very small resizing area.
        # geom = "%dx%d%+d%+d" % (w-20,h-55,10,25)
        # top.geometry(geom)
    # else:
        # # Fill almost the entire screen.
        # # Works on Windows. YMMV for other platforms.
        # geom = "%dx%d%+d%+d" % (w-8,h-46,0,0)
        # top.geometry(geom)
</t>
<t tx="ekr.20081121105001.313"></t>
<t tx="ekr.20081121105001.314">def leoHelp (self,event=None):

    '''Open Leo's offline tutorial.'''

    frame = self ; c = frame.c

    theFile = g.os_path_join(g.app.loadDir,"..","doc","sbooks.chm")

    if g.os_path_exists(theFile):
        os.startfile(theFile)
    else:
        answer = g.app.gui.runAskYesNoDialog(c,
            "Download Tutorial?",
            "Download tutorial (sbooks.chm) from SourceForge?")

        if answer == "yes":
            try:
                if 0: # Download directly.  (showProgressBar needs a lot of work)
                    url = "http://umn.dl.sourceforge.net/sourceforge/leo/sbooks.chm"
                    import urllib
                    self.scale = None
                    urllib.urlretrieve(url,theFile,self.showProgressBar)
                    if self.scale:
                        self.scale.destroy()
                        self.scale = None
                else:
                    url = "http://prdownloads.sourceforge.net/leo/sbooks.chm?download"
                    import webbrowser
                    os.chdir(g.app.loadDir)
                    webbrowser.open_new(url)
            except:
                g.es("exception downloading","sbooks.chm")
                g.es_exception()
</t>
<t tx="ekr.20081121105001.315">def showProgressBar (self,count,size,total):

    # g.trace("count,size,total:",count,size,total)
    if self.scale == None:
        pass
        &lt;&lt; create the scale widget &gt;&gt;
    # self.scale.set(count*size)
    # self.scale.update_idletasks()
</t>
<t tx="ekr.20081121105001.316"># top = qt.Toplevel()
# top.title("Download progress")
# self.scale = scale = qt.Scale(top,state="normal",orient="horizontal",from_=0,to=total)
# scale.pack()
# top.lift()
</t>
<t tx="ekr.20081121105001.317">def bringToFront (self):
    self.top.showNormal()
def deiconify (self):
    self.top.showNormal()
def getFocus(self):
    return g.app.gui.get_focus() 
def get_window_info(self):
    rect = self.top.geometry()
    topLeft = rect.topLeft()
    x,y = topLeft.x(),topLeft.y()
    w,h = rect.width(),rect.height()
    return w,h,x,y
def iconify(self):
    g.trace()
    self.top.showMinimized()
def lift (self):
    self.top.activateWindow()
def update (self):
    pass
def getTitle (self):
    return g.app.gui.toUnicode(self.top.windowTitle())

def setTitle (self,s):
    self.top.setWindowTitle(s)
def setTopGeometry(self,w,h,x,y,adjustSize=True):
    self.top.setGeometry(QtCore.QRect(x,y,w,h))
</t>
<t tx="ekr.20081121105001.490">def runScrolledMessageDialog (self, title='Message', label= '', msg='', c=None, **kw):

    if g.unitTesting: return None

    def send(title=title, label=label, msg=msg, c=c, kw=kw):
        return g.doHook('scrolledMessage', title=title, label=label, msg=msg, c=c, **kw)

    if not c or not c.exists:
        &lt;&lt; no c error&gt;&gt;
    else:        
        retval = send()
        if retval: return retval
        &lt;&lt; load scrolledmessage plugin &gt;&gt;
        retval = send()
        if retval: return retval
        &lt;&lt; no dialog error &gt;&gt;

    &lt;&lt; emergency fallback &gt;&gt;
</t>
<t tx="ekr.20081121105001.572">class leoQTextEditWidget (leoQtBaseTextWidget):

    @others
</t>
<t tx="ekr.20081121105001.573"></t>
<t tx="ekr.20081121105001.574">def __init__ (self,widget,name,c=None):

    # widget is a QTextEdit.
    # g.trace('leoQTextEditWidget',widget)

    # Init the base class.
    leoQtBaseTextWidget.__init__(self,widget,name,c=c)

    self.baseClassName='leoQTextEditWidget'

    widget.setUndoRedoEnabled(False)

    self.setConfig()
    self.setFontFromConfig()
    self.setColorFromConfig()
    # self.setScrollBarOrientation()</t>
<t tx="ekr.20081121105001.575">def setFontFromConfig (self,w=None):

    '''Set the font in the widget w (a body editor).'''

    c = self.c
    if not w: w = self.widget

    font = c.config.getFontFromParams(
        "body_text_font_family", "body_text_font_size",
        "body_text_font_slant",  "body_text_font_weight",
        c.config.defaultBodyFontSize)

    self.fontRef = font # ESSENTIAL: retain a link to font.
    # w.configure(font=font)

    # g.trace("BODY",body.cget("font"),font.cget("family"),font.cget("weight"))
</t>
<t tx="ekr.20081121105001.576">def setColorFromConfig (self,w=None):

    '''Set the font in the widget w (a body editor).'''

    c = self.c
    if w is None: w = self.widget

    bg = c.config.getColor("body_text_background_color") or 'white'
    try:
        pass ### w.configure(bg=bg)
    except:
        g.es("exception setting body text background color")
        g.es_exception()

    fg = c.config.getColor("body_text_foreground_color") or 'black'
    try:
        pass ### w.configure(fg=fg)
    except:
        g.es("exception setting body textforeground color")
        g.es_exception()

    bg = c.config.getColor("body_insertion_cursor_color")
    if bg:
        try:
            pass ### w.configure(insertbackground=bg)
        except:
            g.es("exception setting body pane cursor color")
            g.es_exception()

    sel_bg = c.config.getColor('body_text_selection_background_color') or 'Gray80'
    try:
        pass ### w.configure(selectbackground=sel_bg)
    except Exception:
        g.es("exception setting body pane text selection background color")
        g.es_exception()

    sel_fg = c.config.getColor('body_text_selection_foreground_color') or 'white'
    try:
        pass ### w.configure(selectforeground=sel_fg)
    except Exception:
        g.es("exception setting body pane text selection foreground color")
        g.es_exception()

    # if sys.platform != "win32": # Maybe a Windows bug.
        # fg = c.config.getColor("body_cursor_foreground_color")
        # bg = c.config.getColor("body_cursor_background_color")
        # if fg and bg:
            # cursor="xterm" + " " + fg + " " + bg
            # try:
                # pass ### w.configure(cursor=cursor)
            # except:
                # import traceback ; traceback.print_exc()
</t>
<t tx="ekr.20081121105001.577">def setConfig (self):

    c = self.c ; w = self.widget

    n = c.config.getInt('qt-rich-text-zoom-in')

    w.setWordWrapMode(QtGui.QTextOption.NoWrap)

    # w.zoomIn(1)
    # w.updateMicroFocus()
    if n not in (None,0):
        # This only works when there is no style sheet.
        # g.trace('zoom-in',n)
        w.zoomIn(n)
        w.updateMicroFocus()

    # tab stop in pixels - no config for this (yet)        
    w.setTabStopWidth(24)


</t>
<t tx="ekr.20081121105001.578"></t>
<t tx="ekr.20081121105001.579">def flashCharacter(self,i,bg='white',fg='red',flashes=3,delay=75):

    # numbered color names don't work in Ubuntu 8.10, so...
    if bg[-1].isdigit() and bg[0] != '#':
        bg = bg[:-1]
    if fg[-1].isdigit() and fg[0] != '#':
        fg = fg[:-1]

    # This might causes problems during unit tests.
    # The selection point isn't restored in time.
    if g.app.unitTesting: return

    w = self.widget # A QTextEdit.
    e = QtGui.QTextCursor

    def after(func):
        QtCore.QTimer.singleShot(delay,func)

    def addFlashCallback(self=self,w=w):
        n,i = self.flashCount,self.flashIndex

        cursor = w.textCursor() # Must be the widget's cursor.
        cursor.setPosition(i)
        cursor.movePosition(e.Right,e.KeepAnchor,1)

        extra = w.ExtraSelection()
        extra.cursor = cursor
        if self.flashBg: extra.format.setBackground(QtGui.QColor(self.flashBg))
        if self.flashFg: extra.format.setForeground(QtGui.QColor(self.flashFg))
        self.extraSelList = [extra] # keep the reference.
        w.setExtraSelections(self.extraSelList)

        self.flashCount -= 1
        after(removeFlashCallback)

    def removeFlashCallback(self=self,w=w):
        w.setExtraSelections([])
        if self.flashCount &gt; 0:
            after(addFlashCallback)
        else:
            w.setFocus()

    # g.trace(flashes,fg,bg)
    self.flashCount = flashes
    self.flashIndex = i
    self.flashBg = g.choose(bg.lower()=='same',None,bg)
    self.flashFg = g.choose(fg.lower()=='same',None,fg)

    addFlashCallback()
</t>
<t tx="ekr.20081121105001.580">def getAllText(self):

    #g.trace("getAllText", g.callers(5))
    w = self.widget
    s = unicode(w.toPlainText())

    # Doesn't work: gets only the line containing the cursor.
    # s = unicode(w.textCursor().block().text())

    # g.trace(repr(s))
    return s</t>
<t tx="ekr.20081121105001.581">def getInsertPoint(self):

    return self.widget.textCursor().position()
</t>
<t tx="ekr.20081121105001.582">def getSelectionRange(self,sort=True):

    w = self.widget
    tc = w.textCursor()
    i,j = tc.selectionStart(),tc.selectionEnd()
    # g.trace(i,j,g.callers(4))
    return i,j</t>
<t tx="ekr.20081121105001.583">def getYScrollPosition(self):

    w = self.widget
    sb = w.verticalScrollBar()
    i = sb.sliderPosition()

    # Return a tuple, only the first of which is used.
    return i,i 
</t>
<t tx="ekr.20081121105001.584">def hasSelection(self):

    return self.widget.textCursor().hasSelection()
</t>
<t tx="ekr.20081121105001.585">def see(self,i):

    self.widget.ensureCursorVisible()</t>
<t tx="ekr.20081121105001.586">def seeInsertPoint (self):

    self.widget.ensureCursorVisible()
</t>
<t tx="ekr.20081121105001.587">def setAllText(self,s,insert=None):

    '''Set the text of the widget.

    If insert is None, the insert point, selection range and scrollbars are initied.
    Otherwise, the scrollbars are preserved.'''

    trace = False and not g.unitTesting
    c,w = self.c,self.widget
    colorizer = c.frame.body.colorizer
    highlighter = colorizer.highlighter
    colorer = highlighter.colorer

    # Set a hook for the colorer.
    colorer.initFlag = True

    sb = w.verticalScrollBar()
    if insert is None: i,pos = 0,0
    else: i,pos = insert,sb.sliderPosition()

    if trace: t1 = g.getTime()
    try:
        self.changingText = True
        w.setPlainText(s)
    finally:
        self.chaningText = False
    if trace: g.trace(g.timeSince(t1))

    self.setSelectionRange(i,i,insert=i)
    sb.setSliderPosition(pos)</t>
<t tx="ekr.20081121105001.588">def setInsertPoint(self,i):

    w = self.widget

    s = w.toPlainText()
    i = max(0,min(i,len(s)))
    cursor = w.textCursor()

    # block = cursor.block()
    # i = max(0,min(i,block.length()))

    cursor.setPosition(i)
    w.setTextCursor(cursor)
</t>
<t tx="ekr.20081121105001.589">def setSelectionRangeHelper(self,i,j,insert):

    w = self.widget
    # g.trace('i',i,'j',j,'insert',insert,g.callers(4))
    e = QtGui.QTextCursor
    if i &gt; j: i,j = j,i
    n = self.lengthHelper()
    i = max(0,min(i,n))
    j = max(0,min(j,n))
    k = max(0,min(j-i,n))
    cursor = w.textCursor()
    if i == j:
        cursor.setPosition(i)
    elif insert in (j,None):
        cursor.setPosition(i)
        cursor.movePosition(e.Right,e.KeepAnchor,k)
    else:
        cursor.setPosition(j)
        cursor.movePosition(e.Left,e.KeepAnchor,k)

    w.setTextCursor(cursor)
</t>
<t tx="ekr.20081121105001.590">def lengthHelper(self):

    '''Return the length of the text.'''

    w = self.widget
    cursor = w.textCursor()
    cursor.movePosition(QtGui.QTextCursor.End)
    n = cursor.position()
    return n

</t>
<t tx="ekr.20081121105001.591">def setYScrollPosition(self,pos):

    # g.trace('pos',pos)

    w = self.widget
    sb = w.verticalScrollBar()
    if pos is None: pos = 0
    elif type(pos) == types.TupleType:
        pos = pos[0]
    sb.setSliderPosition(pos)
</t>
<t tx="ekr.20081121105001.1076"></t>
<t tx="ekr.20081121105001.1077"></t>
<t tx="ekr.20081121105001.1078">@nocolor</t>
<t tx="ekr.20081121105001.1079"> 
        
        
        </t>
<t tx="ekr.20081121105001.1080"></t>
<t tx="ekr.20081121105001.1081"></t>
<t tx="ekr.20081121105001.1082"></t>
<t tx="ekr.20081121105001.1083"></t>
<t tx="ekr.20081121105001.1084">c.openLeoSettings()</t>
<t tx="ekr.20081121105001.1085">name = "scripts.leo"
fileName = g.os_path_join(g.app.loadDir,"..","scripts",name)
ok,frame = g.openWithFileName(fileName,c)
if not ok:
    g.es("not found: %s" % name)</t>
<t tx="ekr.20081121105001.1086">c.prettyPrintPythonNode()</t>
<t tx="ekr.20081121105001.1087">c.spellCommands.openSpellTab()</t>
<t tx="ekr.20081121105001.1088">c.save()</t>
<t tx="ekr.20081121105001.1089">([a-zA-Z_.]+)\.bind\((.*)\)(.*)$
c.bind(\1,\2)\3

[a-zA-Z_.]+

(\w)+(\.\w+)*

abc.xyz.pdq

# Bind w.bind with more than two args (none found)

w.bind\(.*,.*,.*$

[-w]\.bind\(</t>
<t tx="ekr.20081121105001.1090">change = True # True: actually make the changes.
trace = True

print '-' * 40

tag = 'import leo' ; n = len('import ')

for p in p.self_and_subtree_iter():
    result = []
    for s in g.splitlines(p.bodyString()):
        i = s.find(tag,0)
        if i &gt; -1:
            # Do nothing if we have already done the translation.
            i2 = s.find('&lt;&lt;') ; i3 = s.find('import leo.core')
            if i2 == -1 and i3 == -1:
                i += n
                j = g.skip_c_id(s,i)
                word = s[i:j]
                rest = s[j:]
                if rest.strip().startswith('as'):
                    s = s[:i] + 'leo.core.' + word + rest
                else:
                    s = s[:i] + 'leo.core.' + word + ' as ' + word + rest
                if trace:
                    print p.headString()
                    j,k=g.getLine(s,i) ; print s[j:k]
        result.append(s)
    result = ''.join(result)

    if change and result != p.bodyString():
        c.setBodyString(p,result)

</t>
<t tx="ekr.20081121105001.1092"></t>
<t tx="ekr.20081121105001.1093"></t>
<t tx="ekr.20081121105001.1108"></t>
<t tx="ekr.20081121105001.1110"></t>
<t tx="ekr.20081121110412.133">def createTextWidget (self,parentFrame,p,name):

    c = self.c

    parentFrame.configure(bg='LightSteelBlue1')

    wrap = c.config.getBool('body_pane_wraps')
    wrap = g.choose(wrap,"word","none")

    # Setgrid=1 cause severe problems with the font panel.
    body = w = leoTkTextWidget (parentFrame,name='body-pane',
        bd=2,bg="white",relief="flat",setgrid=0,wrap=wrap)

    bodyBar = Tk.Scrollbar(parentFrame,name='bodyBar')

    def yscrollCallback(x,y,bodyBar=bodyBar,w=w):
        # g.trace(x,y,g.callers())
        if hasattr(w,'leo_scrollBarSpot'):
            w.leo_scrollBarSpot = (x,y)
        return bodyBar.set(x,y)

    body['yscrollcommand'] = yscrollCallback # bodyBar.set

    bodyBar['command'] =  body.yview
    bodyBar.pack(side="right", fill="y")

    # Always create the horizontal bar.
    bodyXBar = Tk.Scrollbar(
        parentFrame,name='bodyXBar',orient="horizontal")
    body['xscrollcommand'] = bodyXBar.set
    bodyXBar['command'] = body.xview

    if wrap == "none":
        # g.trace(parentFrame)
        bodyXBar.pack(side="bottom", fill="x")

    body.pack(expand=1,fill="both")

    self.wrapState = wrap

    if 0: # Causes the cursor not to blink.
        body.configure(insertofftime=0)

    # Inject ivars
    if name == '1':
        w.leo_p = w.leo_v = None # Will be set when the second editor is created.
    else:
        w.leo_p = p.copy()
        w.leo_v = w.leo_p.v

    w.leo_active = True
    # New in Leo 4.4.4 final: inject the scrollbar items into the text widget.
    w.leo_bodyBar = bodyBar # 2007/10/31
    w.leo_bodyXBar = bodyXBar # 2007/10/31
    w.leo_chapter = None
    w.leo_frame = parentFrame
    w.leo_name = name
    w.leo_label = None
    w.leo_label_s = None
    w.leo_scrollBarSpot = None
    w.leo_insertSpot = None
    w.leo_selection = None

    return w
</t>
<t tx="ekr.20081121110412.143"></t>
<t tx="ekr.20081121110412.144">def createEditorFrame (self,pane):

    f = Tk.Frame(pane)
    f.pack(side='top',expand=1,fill='both')
    return f
</t>
<t tx="ekr.20081121110412.145">def packEditorLabelWidget (self,w):

    '''Create a Tk label widget.'''

    if not hasattr(w,'leo_label') or not w.leo_label:
        # g.trace('w.leo_frame',id(w.leo_frame))
        w.pack_forget()
        w.leo_label = Tk.Label(w.leo_frame)
        w.leo_label.pack(side='top')
        w.pack(expand=1,fill='both')</t>
<t tx="ekr.20081121110412.146">def setEditorColors (self,bg,fg):

    c = self.c ; d = self.editorWidgets

    for key in d:
        w2 = d.get(key)
        # g.trace(id(w2),bg,fg)
        try:
            w2.configure(bg=bg,fg=fg)
        except Exception:
            g.es_exception()
</t>
<t tx="ekr.20081124094918.1">@nocolor-node

http://groups.google.com/group/leo-editor/browse_thread/thread/59c1e5d6acaf4de0

I've some more information about the problems with accent previously
reported:
- I can confirm that they are caused by the interaction scim+leo (with
and without the qt plugin). If scim is not started leo works fine. If
scim is running the problems appear and are slightly different with
and without the qt plugin. The workaround is obvious: don't use leo
and scim at the same time :-)
- accents are not working in the qt plugin when scintilla is used. If
qt-use-scintilla=False I can write this:

àáä (the same for the rest of vowels)

but if qt-use-scintilla=True when I enter the same sequence in the
keyboard I get:

`aaa (the same for the rest of vowels)

- the problem with the ñ character (reported previously too) is only
present in the qt plugin (both with and without scintilla)
</t>
<t tx="ekr.20081215074704.16">http://groups.google.com/group/leo-editor/browse_thread/thread/b2af78fbb36d3590</t>
<t tx="ekr.20081215074704.21"></t>
<t tx="ekr.20081215162017.4">@nocolor-node

Use @string qt-button-color = lightSteelBlue

The following does *not* work in @data qt-gui-plugin-style-sheet::

    QPushButton {
        background-color: red;
    }
</t>
<t tx="ekr.20081215162017.5"></t>
<t tx="ekr.20090128083504.1">@nocolor-node

rClick


After the qt-plugin merge (rev 1251 ), the image plugin no longer works. I
couldn't find any mention of gsimage in the diff.

 # Erase image if it was previously displayed
             a = g.app ; c = keywords.get("c")

-            if a.gsimage:
+            if getattr(a, 'gsimage', None):
                 try:
                     c.frame.body.bodyCtrl.delete(a.gsimage)
                 except:
</t>
<t tx="ekr.20090205153624.11">def delete(self,i,j=None):

    trace = False and not g.unitTesting
    c,w = self.c,self.widget
    colorer = c.frame.body.colorizer.highlighter.colorer
    n = colorer.recolorCount

    i = self.toGuiIndex(i)
    if j is None: j = i+1
    j = self.toGuiIndex(j)

    # Set a hook for the colorer.
    colorer.initFlag = True

    sb = w.verticalScrollBar()
    pos = sb.sliderPosition()
    cursor = w.textCursor()
    cursor.setPosition(i)
    moveCount = abs(j-i)
    cursor.movePosition(cursor.Right,cursor.KeepAnchor,moveCount)
    cursor.removeSelectedText()
    sb.setSliderPosition(pos)

    if trace:
        g.trace('%s calls to recolor' % (
            colorer.recolorCount-n))
</t>
<t tx="ekr.20090205153624.12">def insert(self,i,s):

    trace = False and not g.unitTesting
    c,w = self.c,self.widget
    colorer = c.frame.body.colorizer.highlighter.colorer
    n = colorer.recolorCount

    # Set a hook for the colorer.
    colorer.initFlag = True

    i = self.toGuiIndex(i)

    sb = w.verticalScrollBar()
    pos = sb.sliderPosition()
    cursor = w.textCursor()
    cursor.setPosition(i)
    cursor.insertText(s) # This cause an incremental call to recolor.
    sb.setSliderPosition(pos)

    if trace:
        g.trace('%s calls to recolor' % (
            colorer.recolorCount-n))
</t>
<t tx="ekr.20090223065019.11"># This will be needed for vim.

if 0:
    tree = c.frame.tree
    hs,vs = tree.getScroll()
    print hs,vs
    tree.setVScroll(bs+10)

if 1:
    w = c.frame.body.bodyCtrl.widget
    hScroll = w.horizontalScrollBar()
    vScroll = w.verticalScrollBar()
    hPos = hScroll.sliderPosition()
    vPos = vScroll.sliderPosition()
    print hPos,vPos
    vScroll.setValue(vPos+10)</t>
<t tx="ekr.20090303095630.10"># def setScrollBarOrientation (self):

    # c = self.c
    # orientation = c.config.getString(jk13ab02xy04)
</t>
<t tx="ekr.20090304084841.11"></t>
<t tx="ekr.20090304084841.15"></t>
<t tx="ekr.20090318091009.12"></t>
<t tx="ekr.20090318091009.13">@color

import leo.plugins.qtGui as qtGui

f = c.frame
inner_f = f.top.ui.leo_body_inner_frame
body = qtGui.leoQtBody(f,None) # body is a leoQtFrame
w = body.widget.widget
    # body.widget is a leoQTextEditWidget
    # body.widget.widget is a QTextEdit

inner_f.layout().addWidget(w,0,1)</t>
<t tx="ekr.20090318091009.14">def createTextWidget (self,parentFrame,name,p,w):

    c = self.c

    # # parentFrame.configure(bg='LightSteelBlue1')

    # # wrap = c.config.getBool('body_pane_wraps')
    # # wrap = g.choose(wrap,"word","none")

    # Setgrid=1 cause severe problems with the font panel.
    #### w = leoQTextEditWidget (widget,name,c)


    # # bodyBar = Tk.Scrollbar(parentFrame,name='bodyBar')

    # # def yscrollCallback(x,y,bodyBar=bodyBar,w=w):
        # # # g.trace(x,y,g.callers())
        # # if hasattr(w,'leo_scrollBarSpot'):
            # # w.leo_scrollBarSpot = (x,y)
        # # return bodyBar.set(x,y)

    # # body['yscrollcommand'] = yscrollCallback # bodyBar.set

    # # bodyBar['command'] =  body.yview
    # # bodyBar.pack(side="right", fill="y")

    # # # Always create the horizontal bar.
    # # bodyXBar = Tk.Scrollbar(
        # # parentFrame,name='bodyXBar',orient="horizontal")
    # # body['xscrollcommand'] = bodyXBar.set
    # # bodyXBar['command'] = body.xview

    # # if wrap == "none":
        # # # g.trace(parentFrame)
        # # bodyXBar.pack(side="bottom", fill="x")

    # # body.pack(expand=1,fill="both")

    # # self.wrapState = wrap

    # # if 0: # Causes the cursor not to blink.
        # # body.configure(insertofftime=0)

    # Inject ivars
    if name == '1':
        w.leo_p = w.leo_v = None # Will be set when the second editor is created.
    else:
        w.leo_p = p.copy()
        w.leo_v = w.leo_p.v

    w.leo_active = True
    # New in Leo 4.4.4 final: inject the scrollbar items into the text widget.
    w.leo_bodyBar = None #### bodyBar # 2007/10/31
    w.leo_bodyXBar = None #### bodyXBar # 2007/10/31
    w.leo_chapter = None
    w.leo_frame = parentFrame
    w.leo_name = name
    w.leo_label = None
    w.leo_label_s = None
    w.leo_scrollBarSpot = None
    w.leo_insertSpot = None
    w.leo_selection = None

    #### return w
</t>
<t tx="ekr.20090401110027.1"></t>
<t tx="ekr.20090406071640.13">def onFocusIn (self):
    self.onFocusHelper(self.selectedBackgroundColor)

def onFocusOut (self):
    self.onFocusHelper(self.unselectedBackgroundColor)

badFocusColors = []

def onFocusHelper(self,name):

    if not name: return

    if QtGui.QColor(name).isValid():
        s = 'QTextEdit#richTextEdit { background-color: %s; }' % name
        self.widget.widget.setStyleSheet(s)
    elif name not in self.badFocusColors:
        self.badFocusColors.append(name)
        g.es_print('invalid body background color: %s' % (name),color='blue')
</t>
<t tx="ekr.20090406111739.10">@nocolor-node

http://groups.google.com/group/leo-editor/browse_thread/thread/ef04b185f74f4926

This is a little difficult to describe in words, but trying it out
should, I hope make the issue clear enough.

(1) Start by setting body_pane_wraps to true.

(2) Create a very long line of e.g. 500 characters, which is wrapped
around on the body pane. (E.g. paste in a paragraph from a Word
document). This text will then be wrapped onscreen into roughly 8
lines of 70 characters.

(3) The up and down arrows do not behave as expected.

I'd expect that in this scenario, pressing the down arrow key should
go to go to the next line down as it currently appears *onscreen* --
so in this example, I'd expect to have to press the down arrow several
times to get to the end of the paragraph.  This is the way that Emacs
works when it is in word wrap mode, and is of course is the way that
all word processors work. However, Leo does not play this way, and
takes you right to the end of the line (i.e. to the last of the 500
characters) when you press the down key once. This makes editing plain
text (e.g. using Leo as an outliner) rather more tricky than it ought
to be. Would it be possible to change the effect of Previous-Line and
Next-Line when in word wrap mode, so that they behave as other text
editors and word processors do?

============================

This is a long-standing problem.  It's tricky to fix in a straightforward
way.

However, I just realized that there might be a clever way: the commands
could let the gui handle the hard part of the command (the actual move) and
then the commands could detect the resulting row/col numbers as they must.

I've been putting this off, I'll see if this more clever way will work soon. </t>
<t tx="ekr.20090406111739.12">badWidgetColors = []

def setWidgetColor (self,w,widgetKind,selector,colorName):

    if not colorName: return

    if QtGui.QColor(colorName).isValid():
        g.app.gui.setStyleSetting(w,widgetKind,selector,colorName)
    elif colorName not in self.badWidgetColors:
        self.badWidgetColors.append(colorName)
        g.es_print('bad widget color %s for %s' % (
            colorName,widgetKind),color='blue')
</t>
<t tx="ekr.20090406111739.13">def setStyleSetting(self,w,widgetKind,selector,val):

    '''Set the styleSheet for w to
       "%s { %s: %s; }  % (widgetKind,selector,val)"
    '''

    s = '%s { %s: %s; }' % (widgetKind,selector,val)

    try:
        w.setStyleSheet(s)
    except Exception:
        g.es_print('bad style sheet: %s' % s)
        g.es_exception()
</t>
<t tx="ekr.20090409055330.10">@nocolor-node

http://groups.google.com/group/leo-editor/browse_thread/thread/430287018f9d773d

The following problem hits rev 1633, qt plugin (untested with tk plugin). The
command Find --&gt; Change All *always* acts on *every node*. It ignores the
checkboxes selection made by the user. Even if you select the "Node Only"
checkbox the changes are aplied to the whole tree (headline text and body text).</t>
<t tx="ekr.20090418064921.12">http://groups.google.com/group/leo-editor/browse_thread/thread/7285ac185355efb1</t>
<t tx="ekr.20090421121914.11"></t>
<t tx="ekr.20090426075320.10"></t>
<t tx="ekr.20090427112929.10">def __init__(self,owner,ivar):

    self.ivar = ivar
    self.owner = owner
    self.radioButtons = ['node_only','suboutline_only','entire_outline']
    self.trace = False
    self.val = None
    self.w = None

def __repr__(self):
    return '&lt;svar %s&gt;' % self.ivar</t>
<t tx="ekr.20090427112929.12">def get (self):
    if self.w:
        val = self.w.isChecked()
        if self.trace: g.trace('qt svar %15s = %s' % (self.ivar,val))
    else:
        val = self.val
    return val</t>
<t tx="ekr.20090427112929.13">def init (self,val):

    '''Init the svar, but do *not* init radio buttons.
    (This is called from initRadioButtons).'''

    if val in (0,1):
        self.val = bool(val)
    else:
        self.val = val # Don't contain the scope values!

    if self.w:
        self.w.setChecked(bool(val))

    if self.trace: g.trace('qt svar %15s = %s' % (self.ivar,val))
</t>
<t tx="ekr.20090427112929.15">def setWidget(self,w):

    self.w = w
</t>
<t tx="ekr.20090427112929.17">def set (self,val):

    '''Init the svar and update the radio buttons.'''

    self.init(val)

    if self.ivar in self.radioButtons:
        self.owner.initRadioButtons()
    elif self.ivar == 'radio-search-scope':
        self.setRadioScope(val)


</t>
<t tx="ekr.20090427112929.18">def setRadioScope (self,val):

    '''Update the svars corresponding to the scope value.'''

    table = (
        ("suboutline_only","suboutline-only"),
        ("node_only","node-only"),
        ("entire_outline","entire-outline"))

    for ivar,val2 in table:
        if val == val2:
            svar = self.owner.svarDict.get(ivar)
            val = svar.get()
            svar.init(True)
</t>
<t tx="ekr.20090429101847.10">http://groups.google.com/group/leo-editor/browse_thread/thread/9ac06147e75fc042</t>
<t tx="ekr.20090430102239.1"></t>
<t tx="ekr.20090430102239.2">Especially shift-arrow keys.</t>
<t tx="ekr.20090430102239.3">@

At present, the qt gui sends PgUp and PgDn directly to the widget.

That is, the plugin does not handle scrolling properly.

This will become an issue for vim bindings.</t>
<t tx="ekr.20090430102239.4">master_key_count = 0

def masterKeyHandler (self,event,stroke=None):

    '''This is the handler for almost all key bindings.'''

    &lt;&lt; define vars &gt;&gt;
    trace = False and not g.app.unitTesting # or self.trace_masterKeyHandler)
    traceGC = self.trace_masterKeyHandlerGC and not g.app.unitTesting
    verbose = True

    if keysym in special_keys:
        if trace and verbose: g.trace('keysym',keysym)
        return None
    if traceGC: g.printNewObjects('masterKey 1')
    if trace:
        g.trace('stroke:',repr(stroke),'keysym:',
            repr(event.keysym),'ch:',repr(event.char),'state',state)
        # g.trace('callers',g.callers(5))
            # 'state.kind:',k.state.kind),'\n',g.callers())
        # if (self.master_key_count % 100) == 0: g.printGcSummary()

    # if stroke == 'Return': g.pdb()

    # Handle keyboard-quit first.
    if k.abortAllModesKey and stroke == k.abortAllModesKey:
        # g.trace('special case')
        if c.macroCommands.recordingMacro:
            c.macroCommands.endKbdMacro()
            return 'break'
        else:
            return k.masterCommand(event,k.keyboardQuit,stroke,'keyboard-quit')

    if k.inState():
        # This will return unless k.autoCompleterStateHandler
        # (called from k.callStateFunction) returns 'do-standard-keys'
        &lt;&lt; handle mode bindings &gt;&gt;

    if traceGC: g.printNewObjects('masterKey 2')

    if stroke and isPlain:
        &lt;&lt; handle special cases for plain keys &gt;&gt;

    &lt;&lt; handle per-pane bindings &gt;&gt;

    if traceGC: g.printNewObjects('masterKey 5')

    return k.handleUnboundKeys(event,char,keysym,stroke)
</t>
<t tx="ekr.20090430102239.5">k = self ; c = k.c ; gui = g.app.gui

if event:
    # This is a leoGui base class event.
    event = gui.leoKeyEvent(event,c,stroke=stroke)

w = event.widget
char = event.char
keysym = event.keysym
if stroke and not keysym:
    event.keysym = keysym = stroke

w_name = c.widget_name(w)
state = k.state.kind

special_keys = (
    'Alt_L','Alt_R',
    'Caps_Lock','Control_L','Control_R',
    'Meta_L','Meta_R', # Meta support.
    'Num_Lock',
    'Shift_L','Shift_R',
    'Win_L','Win_R',
)

self.master_key_count += 1

isPlain =  k.isPlainKey(stroke)</t>
<t tx="ekr.20090430102239.6"># First, honor minibuffer bindings for all except user modes.

if state in ('getArg','getFileName','full-command','auto-complete'):
    if k.handleMiniBindings(event,state,stroke):
        return 'break'

# Second, honor general modes.
if state == 'getArg':
    return k.getArg(event,stroke=stroke)
elif state == 'getFileName':
    return k.getFileName(event)
elif state in ('full-command','auto-complete'):
    # Do the default state action.
    if trace: g.trace('calling state function',k.state.kind) # k.state.handler)
    val = k.callStateFunction(event) # Calls end-command.
    if val != 'do-standard-keys': return 'break'

# Third, pass keys to user modes.
else:
    d =  k.masterBindingsDict.get(state)
    if d:
        b = d.get(stroke)
        if b:
            if trace: g.trace('calling generalModeHandler',stroke)
            k.generalModeHandler (event,
                commandName=b.commandName,func=b.func,
                modeName=state,nextMode=b.nextMode)
            return 'break'
        else:
            # New in Leo 4.5: unbound keys end mode.
            if trace: g.trace('unbound key ends mode',stroke,state)
            k.endMode(event)
    else:
        # New in 4.4b4.
        handler = k.getStateHandler()
        if handler:
            handler(event)
        else:
            g.trace('No state handler for %s' % state)
        return 'break'
</t>
<t tx="ekr.20090430102239.7"># g.trace('plain key','state',k.unboundKeyAction,'stroke',stroke)

# Important: only keys bound somewhere have a stroke.
# All unbound plain keys will be handled by handleUnboundKeys.

if k.unboundKeyAction in ('insert','overwrite'):

    for key in (k.unboundKeyAction,'body','log','text','all'):
        # Ignore bindings for all plain keys in insert/overwrite mode *except* auto-complete.
        d = k.masterBindingsDict.get(key,{})
        if d:
            b = d.get(stroke)
            if b and b.commandName == 'auto-complete':
                if trace: g.trace('%s: auto-complete key in %s mode' % (stroke,k.unboundKeyAction))
                k.masterCommand(event,b.func,b.stroke,b.commandName)
                return 'break'

    if trace: g.trace('unbound key: %s in %s mode' % (stroke,k.unboundKeyAction))
    k.masterCommand(event,func=None,stroke=stroke,commandName=None)
    return 'break'

# Bound   plain keys in command mode are by the per-pane logic.
# Unbound plain keys in command mode are ignored by handleUnboundKeys.

# This code ignores all command-state keys if we are not in a text widget.
elif k.unboundKeyAction == 'command':
    if not g.app.gui.isTextWidget(w):
        c.onCanvasKey(event)
        return 'break'</t>
<t tx="ekr.20090430102239.8">keyStatesTuple = ('command','insert','overwrite')

# g.trace('w_name',w_name,'stroke',stroke,'w',w,'isTextWidget(w)',g.app.gui.isTextWidget(w))

for key,name in (
    # Order here is similar to bindtags order.
    ('command',None),
    ('insert',None),
    ('overwrite',None),
    ('button',None),
    ('body','body'),
    ('text','head'), # Important: text bindings in head before tree bindings.
    ('tree','head'),
    ('tree','canvas'),
    ('log', 'log'),
    ('text','log'),
    ('text',None),
    ('all',None),
):
    if (
        # key in keyStatesTuple and isPlain and k.unboundKeyAction == key or
        name and w_name.startswith(name) or
        key in ('text','all') and g.app.gui.isTextWidget(w) or
        key in ('button','all')
    ):
        d = k.masterBindingsDict.get(key,{})
        # g.trace('key',key,'name',name,'stroke',stroke,'stroke in d.keys',stroke in d)
        # g.trace(key,'keys',g.listToString(d.keys(),sort=True)) # [:5])
        if d:
            b = d.get(stroke)
            if b:
                if trace: g.trace('%s found %s = %s' % (key,repr(b.stroke),b.commandName))
                if traceGC: g.printNewObjects('masterKey 3')
                return k.masterCommand(event,b.func,b.stroke,b.commandName)
</t>
<t tx="ekr.20090430102239.9">def callStateFunction (self,event):

    k = self ; val = None ; ch = g.app.gui.eventChar(event)

    # g.trace(k.state.kind,'ch',ch,'ignore-non-ascii',k.ignore_unbound_non_ascii_keys)

    if k.state.kind:
        if (
            k.ignore_unbound_non_ascii_keys and
            ch and ch not in ('\b','\n','\r','\t') and
            (ord(ch) &lt; 32 or ord(ch) &gt; 128)
        ):
            # g.trace('non-ascii',ord(ch))
            pass
        elif k.state.handler:
            val = k.state.handler(event)
            if val != 'continue':
                k.endCommand(event,k.commandName)
        else:
            g.es_print('no state function for',k.state.kind,color='red')

    return val
</t>
<t tx="ekr.20090430102239.10">def handleMiniBindings (self,event,state,stroke):

    k = self ; c = k.c
    trace = False or (self.trace_masterKeyHandler and not g.app.unitTesting)

    # Special case for bindings handled in k.getArg:
    if state in ('getArg','full-command'):
        if stroke in ('BackSpace','Return','Tab','Escape'):
            return False

    if not state.startswith('auto-'):
        # New in Leo 4.5: ignore plain key binding in the minibuffer.
        if not stroke or k.isPlainKey(stroke):
            if trace: g.trace('plain key',stroke)
            return False
        # New in Leo 4.5: The minibuffer inherits 'text' and 'all' bindings
        # for all single-line editing commands.
        for pane in ('mini','all','text'):
            d = k.masterBindingsDict.get(pane)
            if d:
                b = d.get(stroke)
                if b:
                    if b.commandName == 'replace-string' and state == 'getArg':
                        if trace: g.trace('%s binding for replace-string' % (pane),stroke)
                        return False # Let getArg handle it.
                    elif b.commandName not in k.singleLineCommandList:
                        if trace: g.trace('%s binding terminates minibuffer' % (pane),b.commandName,stroke)
                        k.keyboardQuit(event,hideTabs=True)
                    else:
                        if trace: g.trace(repr(stroke),'mini binding',b.commandName)
                        c.minibufferWantsFocusNow() # New in Leo 4.5.
                    # Pass this on for macro recording.
                    k.masterCommand(event,b.func,stroke,b.commandName)
                    # Careful: the command could exit.
                    if c.exists and not k.silentMode:
                        c.minibufferWantsFocus()
                    return True

    return False
</t>
<t tx="ekr.20090430102239.11">def handleUnboundKeys (self,event,char,keysym,stroke):

    k = self ; c = k.c ; trace = False
    modesTuple = ('insert','overwrite')

    if trace:
        # if stroke: g.trace('***unexpected stroke***')
        g.trace('keysym:',repr(event.keysym),'ch:',repr(event.char))
            # 'state.kind:',k.state.kind),'\n',g.callers())
        # if (self.master_key_count % 100) == 0: g.printGcSummary()

    if k.unboundKeyAction == 'command':
        # Ignore all unbound characters in command mode.
        w = g.app.gui.get_focus(c)
        if w and g.app.gui.widget_name(w).lower().startswith('canvas'):
            c.onCanvasKey(event)
        return 'break'

    elif stroke and k.isPlainKey(stroke) and k.unboundKeyAction in modesTuple:
        # insert/overwrite normal character.  &lt;Return&gt; is *not* a normal character.
        if trace: g.trace('plain key in insert mode',repr(stroke))
        return k.masterCommand(event,func=None,stroke=stroke,commandName=None)

    elif k.ignore_unbound_non_ascii_keys and len(char) &gt; 1:
        # (stroke.find('Alt+') &gt; -1 or stroke.find('Ctrl+') &gt; -1)):
        if trace: g.trace('ignoring unbound non-ascii key')
        return 'break'

    elif keysym.find('Escape') != -1:
        # Never insert escape characters.
        return 'break'

    else:
        if trace: g.trace(repr(stroke),'no func')
        return k.masterCommand(event,func=None,stroke=stroke,commandName=None)
</t>
<t tx="ekr.20090430102239.12">def scrollOutlineDownLine (self,event=None):
    '''Scroll the outline pane down one line.'''
    a,b = self.c.frame.canvas.leo_treeBar.get()
    if b &lt; 1.0:
        self.c.frame.tree.canvas.yview_scroll(1,"unit")

def scrollOutlineDownPage (self,event=None):
    '''Scroll the outline pane down one page.'''
    a,b = self.c.frame.canvas.leo_treeBar.get()
    if b &lt; 1.0:
        self.c.frame.tree.canvas.yview_scroll(1,"page")

def scrollOutlineUpLine (self,event=None):
    '''Scroll the outline pane up one line.'''
    a,b = self.c.frame.canvas.leo_treeBar.get()
    if a &gt; 0.0:
        self.c.frame.tree.canvas.yview_scroll(-1,"unit")

def scrollOutlineUpPage (self,event=None):
    '''Scroll the outline pane up one page.'''
    a,b = self.c.frame.canvas.leo_treeBar.get()
    if a &gt; 0.0:
        self.c.frame.tree.canvas.yview_scroll(-1,"page")
</t>
<t tx="ekr.20090430102239.13"></t>
<t tx="ekr.20090522102224.3882"></t>
<t tx="leohag.20081205043707.11">g.es_print_error('The handler for the "scrolledMessage" hook appears to be missing or not working.\n\t%s'%g.callers())</t>
<t tx="leohag.20081205043707.12">g.es_print_error('%s\n%s\n\t%s' % (
    "The qt plugin requires calls to g.app.gui.scrolledMessageDialog to include 'c'",
    "as a keyword argument",
    g.callers()
))</t>
<t tx="leohag.20081205043707.13">
b = QtGui.QMessageBox
d = b(None) # c.frame.top)
d.setWindowFlags(QtCore.Qt.Dialog) # That is, not a fixed size dialog.

d.setWindowTitle(title)
if msg: d.setText(msg)
d.setIcon(b.Information)
yes = d.addButton('Ok',b.YesRole)
d.exec_()</t>
<t tx="leohag.20081205043707.14">import leo.core.leoPlugins as leoPlugins
sm = leoPlugins.getPluginModule('scrolledmessage')

if not sm:
    sm = leoPlugins.loadOnePlugin('scrolledmessage',verbose=True)
    if sm:
        g.es('scrolledmessage plugin loaded.', color='blue')
        sm.onCreate('tag',{'c':c})
</t>
<t tx="leohag.20081208130321.12"># Divides the main or secondary splitter, using the key invariant.
def divideLeoSplitter (self, verticalFlag, frac):

    if self.splitVerticalFlag == verticalFlag:
        self.divideLeoSplitter1(frac,verticalFlag)
        self.ratio = frac # Ratio of body pane to tree pane.
    else:
        self.divideLeoSplitter2(frac,verticalFlag)
        self.secondary_ratio = frac # Ratio of tree pane to log pane.

# Divides the main splitter.
def divideLeoSplitter1 (self, frac, verticalFlag): 
    self.divideAnySplitter(frac, self.top.splitter_2 )

# Divides the secondary splitter.
def divideLeoSplitter2 (self, frac, verticalFlag): 
    self.divideAnySplitter (frac, self.top.ui.splitter)

</t>
<t tx="leohag.20081208130321.13"># This is the general-purpose placer for splitters.
# It is the only general-purpose splitter code in Leo.

def divideAnySplitter (self, frac, splitter ):#verticalFlag, bar, pane1, pane2):

    sizes = splitter.sizes()

    if len(sizes)!=2:
        g.trace('there must be two and only two widgets in the splitter')

    if frac &gt; 1 or frac &lt; 0:
        g.trace('split ratio [%s] out of range 0 &lt;= frac &lt;= 1'%frac)

    s1, s2 = sizes
    s = s1+s2
    s1 = int(s * frac + 0.5)
    s2 = s - s1 

    splitter.setSizes([s1,s2])

@
    # if self.bigTree:
        # pane1,pane2 = pane2,pane1

    if verticalFlag:
        # Panes arranged vertically; horizontal splitter bar
        bar.place(rely=frac)
        pane1.place(relheight=frac)
        pane2.place(relheight=1-frac)
    else:
        # Panes arranged horizontally; vertical splitter bar
        bar.place(relx=frac)
        pane1.place(relwidth=frac)
        pane2.place(relwidth=1-frac)
</t>
<t tx="ville.20090321082712.1"></t>
<t tx="ville.20090321082712.2">def toPythonIndex (self,index):

    w = self
    te = self.widget

    if type(index) == type(99):
        return index
    elif index == '1.0':
        return 0
    elif index == 'end':
        return w.getLastPosition()
    else:
        # g.trace(repr(index))
        #s = w.getAllText()
        doc = te.document()
        data = index.split('.')
        if len(data) == 2:
            row,col = data
            row,col = int(row),int(col)
            bl = doc.findBlockByNumber(row-1)
            return bl.position() + col


            #i = g.convertRowColToPythonIndex(s,row-1,col)

            # g.trace(index,row,col,i,g.callers(6))
            #return i
        else:
            g.trace('bad string index: %s' % index)
            return 0

toGuiIndex = toPythonIndex
</t>
<t tx="ville.20090321082712.3">def toPythonIndexRowCol(self,index):
    #print "use idx",index

    if index == '1.0':
        return 0, 0, 0
    if index == 'end':
        index = w.getLastPosition()

    w = self 
    te = self.widget
    #print te
    doc = te.document()
    i = w.toPythonIndex(index)
    bl = doc.findBlock(i)
    row = bl.blockNumber()
    col = i - bl.position()

    #s = w.getAllText()
    #i = w.toPythonIndex(index)
    #row,col = g.convertPythonIndexToRowCol(s,i)
    #print "idx",i,row,col
    return i,row,col
</t>
<t tx="ville.20090324170325.63">def get(self,i,j=None):
    i = self.toGuiIndex(i)
    if j is None: 
        j = i+1
    else:
        j = self.toGuiIndex(j)
    te = self.widget
    doc = te.document()
    bl = doc.findBlock(i)
    #row = bl.blockNumber()
    #col = index - bl.position()

    # common case, e.g. one character    
    if bl.contains(j):
        s = unicode(bl.text())
        offset = i - bl.position()

        ret = s[ offset : offset + (j-i)]
        #print "fastget",ret
        return ret

    # the next implementation is much slower, but will have to do        

    #g.trace('Slow get()', g.callers(5))
    s = self.getAllText()
    i = self.toGuiIndex(i)

    j = self.toGuiIndex(j)
    return s[i:j]
</t>
</tnodes>
</leo_file>
