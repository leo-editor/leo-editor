<?xml version="1.0" encoding="utf-8"?>
<!-- Created by Leo: http://leoeditor.com/leo_toc.html -->
<leo_file xmlns:leo="http://leoeditor.com/namespaces/leo-python-editor/1.1" >
<leo_header file_format="2"/>
<globals/>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="ekr.20041121151002"><vh>@settings</vh>
<v t="ekr.20161011095551.1"><vh>@bool allow-section-references-in-at-auto = True</vh></v>
<v t="ekr.20161129030232.1"><vh>@bool run-pyflakes-on-write = True</vh></v>
<v t="ekr.20070503064257"><vh>@bool use-chapters = True</vh></v>
<v t="ekr.20111123042627.6654"><vh>@@enabled-plugins</vh></v>
</v>
<v t="ekr.20190113120618.1"><vh>Read me</vh></v>
<v t="ekr.20190113120734.1"><vh>@asis at-asis-test.py</vh>
<v t="ekr.20190113120734.2"><vh>spam</vh></v>
<v t="ekr.20190113120734.3"><vh>eggs</vh></v>
</v>
<v t="ekr.20200205065723.1"><vh>@asis external_files/at-asis-test2.txt</vh>
<v t="ekr.20200205065723.2"><vh>spam</vh></v>
<v t="ekr.20200205065723.3"><vh>@@eggs</vh></v>
</v>
<v t="ekr.20190113123439.5"><vh>@auto at-auto-line-number-test.py</vh></v>
<v t="ekr.20190113123439.7"><vh>@auto at-auto-md-line-number-test.md</vh></v>
<v t="ekr.20190113123439.11"><vh>@auto at-auto-section-ref-test.py</vh></v>
<v t="ekr.20190113121550.1"><vh>@auto at-auto-test.py</vh></v>
<v t="ekr.20190113123439.16"><vh>@auto at-auto-unit-test.py</vh></v>
<v t="ekr.20190113123635.2"><vh>@auto-org at-auto-org-line-number-test.org</vh></v>
<v t="ekr.20190113123635.5"><vh>@auto-otl at-auto-otl-line-number-test.otl</vh></v>
<v t="ekr.20190113123822.1"><vh>@clean at-clean-line-number-test.c</vh>
<v t="ekr.20190113123822.2"><vh>spam</vh></v>
<v t="ekr.20190113123822.3"><vh>eggs</vh></v>
</v>
<v t="ekr.20190113123853.1"><vh>@clean at-clean-line-number-test.py</vh>
<v t="ekr.20190113123853.2"><vh>spam</vh></v>
<v t="ekr.20190113123853.3"><vh>eggs</vh></v>
</v>
<v t="ekr.20191207060251.1"><vh>@clean at-clean-write-test.py</vh>
<v t="ekr.20191207060251.2"><vh>spam</vh></v>
<v t="ekr.20191207060251.3"><vh>eggs</vh></v>
</v>
<v t="ekr.20160403123754.1"><vh>@file at-file-line-number-test.c</vh></v>
<v t="ekr.20080904102243.2"><vh>@file at-file-line-number-test.py</vh></v>
<v t="ekr.20111021115306.3697"><vh>@file tex-error.tex</vh></v>
<v t="ekr.20130912092638.4150"><vh>@file utf-16-test.txt</vh></v>
<v t="ekr.20190113124135.1"><vh>@nosent at-nosent-line-number-test.py</vh>
<v t="ekr.20190113124135.2"><vh>spam</vh></v>
<v t="ekr.20190113124135.3"><vh>eggs</vh></v>
</v>
<v t="ekr.20100731163237.5782"><vh>@thin at-thin-html-test.html</vh></v>
<v t="ekr.20090704085350.5022"><vh>@thin at-thin-test.py</vh></v>
</vnodes>
<tnodes>
<t tx="ekr.20041121151002"># Many of these are required for unit tests.
# Do not change them without running all unit tests.</t>
<t tx="ekr.20070503064257"></t>
<t tx="ekr.20111123042627.6654"># Leo loads plugins in the order they appear here.

# **Important**: to change these defaults, put
# an @enabled-plugins node in myLeoSettings.leo.

# Highly-recommended plugins:
plugins_menu.py
free_layout.py # needs to be early
viewrendered.py

# Recommended plugins:
mod_scripting.py

# Testing:
todo.py  # #1691.
</t>
<t tx="ekr.20161011095551.1">True: (Experimental): The @auto write code expands section references.
False: (Legacy):      The @auto write code ignores section references.
</t>
<t tx="ekr.20161129030232.1"></t>
<t tx="ekr.20190113120618.1"># This file searves as manual test of Leo's file-reading code.</t>
<t tx="ekr.20190113120734.1">@language python
@others
</t>
<t tx="ekr.20190113120734.2">def spam():
    pass</t>
<t tx="ekr.20190113120734.3">def eggs():
    pass</t>
<t tx="ekr.20190113123822.1">@language c
@tabwidth -4
// before @others // line 1
@others
// last line: line 6
</t>
<t tx="ekr.20190113123822.2">def spam(): // line 2
    pass
</t>
<t tx="ekr.20190113123822.3">def eggs(): // line 4
    pass
</t>
<t tx="ekr.20190113123853.1">@language python
@tabwidth -4
# Before @others: line 1
@others
# Last line: line 6
</t>
<t tx="ekr.20190113123853.2">def spam(): # line 2
    pass
</t>
<t tx="ekr.20190113123853.3">def eggs(): # line 4
    pass
</t>
<t tx="ekr.20190113124135.1">@language python
@tabwidth -4
# before @others: line 1
@others
# last line: line 6</t>
<t tx="ekr.20190113124135.2">def spam(): # line 2
    pass
</t>
<t tx="ekr.20190113124135.3">def eggs(): # line 4
    pass</t>
<t tx="ekr.20191207060251.1">@language python
@tabwidth -4
@others
</t>
<t tx="ekr.20191207060251.2">def spam():
    pass
</t>
<t tx="ekr.20191207060251.3">def eggs():
    pass
</t>
<t tx="ekr.20200205065723.1">@language python
@others
</t>
<t tx="ekr.20200205065723.2">def spam():
    pass</t>
<t tx="ekr.20200205065723.3">def eggs():
    pass
</t>
</tnodes>
</leo_file>
