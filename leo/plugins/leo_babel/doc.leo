<?xml version="1.0" encoding="utf-8"?>
<!-- Created by Leo: https://leo-editor.github.io/leo-editor/leo_toc.html -->
<leo_file xmlns:leo="https://leo-editor.github.io/leo-editor/namespaces/leo-python-editor/1.1" >
<leo_header file_format="2"/>
<globals/>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="bob.20170311143430.3"><vh>@file doc/doc.txt</vh></v>
<v t="bob.20170927112530.1"><vh>md to other formats</vh>
<v t="bob.20171229154149.1"><vh>Manual</vh>
<v t="bob.20170707161137.1"><vh>Make Leo-Babel.pdf</vh>
<v t="bob.20170707161147.1"><vh>Script</vh></v>
</v>
<v t="bob.20170818105700.1"><vh>Make Leo-Babel.rst</vh>
<v t="bob.20170818105700.2"><vh>Script</vh></v>
</v>
<v t="bob.20170818104927.1"><vh>Make Leo-Babel.html</vh>
<v t="bob.20170818104927.2"><vh>Script</vh></v>
</v>
</v>
<v t="bob.20171229154159.1"><vh>Maintenance</vh>
<v t="bob.20171229154159.2"><vh>Make maintenance.pdf</vh>
<v t="bob.20171229154159.3"><vh>Script</vh></v>
</v>
<v t="bob.20171229154159.5"><vh>Make maintenance.html</vh>
<v t="bob.20171229154159.6"><vh>Script</vh></v>
</v>
</v>
</v>
<v t="bob.20171229153743.1"><vh>@auto-md doc/maintenance.md</vh></v>
<v t="bob.20170508125533.2"><vh>@auto-md doc/Leo-Babel.md</vh></v>
</vnodes>
<tnodes>
<t tx="bob.20170707161137.1">@language python

babel_node_creation = False</t>
<t tx="bob.20170707161147.1">@language shell

echo pandoc -N --toc doc/Leo-Babel.md -o doc/Leo-Babel.pdf
pandoc -N --toc doc/Leo-Babel.md -o doc/Leo-Babel.pdf
</t>
<t tx="bob.20170818104927.1">@language python

babel_node_creation = False</t>
<t tx="bob.20170818104927.2">@language shell

echo pandoc -N doc/Leo-Babel.md -o doc/Leo-Babel.html
pandoc -N doc/Leo-Babel.md -o doc/Leo-Babel.html
</t>
<t tx="bob.20170818105700.1">@doc

-N number sections.  But there is no way to get numbered sections in markdown output or rst output.

-s Make a standalone document with proper header and footer.
    The .rst must NOT be generated with this option.  Leo-Editor can't deal with a standalone document.

--toc Table of contents
@code
@language python

babel_node_creation = False</t>
<t tx="bob.20170818105700.2">@language shell

echo pandoc -f markdown -t markdown -s --toc -o doc/Leo-Babel.tmp.md doc/Leo-Babel.md
pandoc -f markdown -t markdown -s --toc -o doc/Leo-Babel.tmp.md doc/Leo-Babel.md
echo pandoc -f markdown -t rst -o doc/Leo-Babel.rst doc/Leo-Babel.tmp.md
pandoc -f markdown -t rst  -o doc/Leo-Babel.rst doc/Leo-Babel.tmp.md
echo rm doc/Leo-Babel.tmp.md
rm doc/Leo-Babel.tmp.md
</t>
<t tx="bob.20170927112530.1"></t>
<t tx="bob.20171229154149.1"></t>
<t tx="bob.20171229154159.1"></t>
<t tx="bob.20171229154159.2">@language python

babel_node_creation = False</t>
<t tx="bob.20171229154159.3">@language shell

echo pandoc -N --toc doc/maintenance.md -o doc/maintenance.pdf
pandoc -N --toc doc/maintenance.md -o doc/maintenance.pdf
</t>
<t tx="bob.20171229154159.5">@language python

babel_node_creation = False</t>
<t tx="bob.20171229154159.6">@language shell

echo pandoc -N doc/maintenance.md -o doc/maintenance.html
pandoc -N doc/maintenance.md -o doc/maintenance.html
</t>
</tnodes>
</leo_file>
