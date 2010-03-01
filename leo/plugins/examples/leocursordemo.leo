<?xml version="1.0" encoding="utf-8"?>
<?xml-stylesheet ekr_test?>
<leo_file>
<leo_header file_format="2" tnodes="0" max_tnode_index="0" clone_windows="0"/>
<globals body_outline_ratio="0.5" body_secondary_ratio="0.5">
	<global_window_position top="50" left="50" height="500" width="700"/>
	<global_log_window_position top="0" left="0" height="0" width="0"/>
</globals>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="tbrown.20100205200824.5417"><vh>@chapters</vh></v>
<v t="tbrown.20100206093837.1344"><vh>What's this?</vh></v>
<v t="tbrown.20100205200824.5416" a="E"><vh>Data</vh>
<v t="tbrown.20100205200824.5418"><vh>Meta</vh></v>
<v t="tbrown.20100205200824.5419" a="E"><vh>Events</vh>
<v t="tbrown.20100205200824.5420"><vh>Event 1</vh></v>
<v t="tbrown.20100205200824.5422" a="E"><vh>Event 2</vh>
<v t="tbrown.20100206093837.1337"><vh>Review 1</vh></v>
<v t="tbrown.20100206093837.1339"><vh>Review 2</vh></v>
</v>
</v>
</v>
<v t="tbrown.20100205200824.5423"><vh>Simple Demo</vh></v>
<v t="tbrown.20100206093837.1341"><vh>Genshi Demo</vh></v>
<v t="tbrown.20100206093837.1342"><vh>Genshi template</vh></v>
<v t="tbrown.20100206093837.1343"><vh>leocursordemo.html</vh></v>
</vnodes>
<tnodes>
<t tx="tbrown.20100205200824.5416"></t>
<t tx="tbrown.20100205200824.5417"></t>
<t tx="tbrown.20100205200824.5418"></t>
<t tx="tbrown.20100205200824.5419"></t>
<t tx="tbrown.20100205200824.5420">Some rambling about the event
date:2010-4-1 (no space, doesn't match)
date: 2010/3/6
time: 12:00 (matches, but not used, disappears in output)
More rambling
</t>
<t tx="tbrown.20100205200824.5422">date: 2999/3/6
Second one
</t>
<t tx="tbrown.20100205200824.5423">import traceback  # leo's run-script hides detail on tracebacks
import sys

from leo.plugins import leocursor

reload(leocursor)  # for development

try:

    lc = leocursor.LeoCursor(g.findTopLevelNode(c, 'Data').v)
    lc._setAttribManagers([leocursor.AM_Colon()])

    print("%d events with %d reviews" %
      (len(lc("Events/Event.*")),len(lc("Events/Event.*/Rev.*"))))

    print "Event dates:", lc("Events/Event.*/@date")

    print("%s to %s" %
      (lc("Events/0")[0]._H,lc("Events/-1")[0]._H))
    print("%s to %s" %
      (lc("Events/.*")[0]._H,lc("Events/.*")[-1]._H))
    print("%s to %s" %
      (lc.Events[0]._H,lc.Events[-1]._H))

    for event in lc._R.Events:
        print("\n%s (%s)" % (event._H, event._date))
        print('"%s"' % event._B.strip())
        for review in event('Review.*'):
            print('   Review: '+review._H+('*'*int(review('@stars')[0])))


except:
    # print the full traceback leo's run-script hides
    traceback.print_tb(sys.exc_info()[2])
    raise
</t>
<t tx="tbrown.20100206093837.1337">stars: 3</t>
<t tx="tbrown.20100206093837.1339">stars: 12</t>
<t tx="tbrown.20100206093837.1341">from genshi import XML, HTML
from genshi.template import MarkupTemplate

from leo.plugins import leocursor

reload(leocursor)  # for development

lc = leocursor.LeoCursor(g.findTopLevelNode(c, 'Data').v)
lc._setAttribManagers([leocursor.AM_Colon()])

tmpl = MarkupTemplate(g.findTopLevelNode(c, 'Genshi template').b)

g.findTopLevelNode(c, 'leocursordemo.html').b = ('@language html\n'+
    tmpl.generate(lc=lc).render('xhtml', doctype='html')
)

</t>
<t tx="tbrown.20100206093837.1342">&lt;html xmlns:py="http://genshi.edgewall.org/"&gt;
  &lt;body&gt;
    &lt;h1&gt;Events&lt;/h1&gt;

    &lt;div&gt;${len(lc("Events/Event.*"))} events,
       ${len(lc("Events/Event.*/Rev.*"))} reviews&lt;/div&gt;
       
    &lt;div py:for="event in lc._R.Events" class="event"&gt;

      &lt;h2&gt;${event._H} (${event._date})&lt;/h2&gt;
      &lt;p&gt;${event._B}&lt;/p&gt;
      
      &lt;div py:if="event('Review.*')" class='reviews'&gt;
        &lt;h3&gt;Reviews&lt;/h3&gt;
        
        &lt;div py:for="rev in event('Review.*')"&gt;
          &lt;b&gt;${rev._H}:&lt;/b&gt;${'*' * int(rev._stars)}
        &lt;/div&gt;
      &lt;/div&gt;
    &lt;/div&gt;
  &lt;/body&gt;
&lt;/html&gt;
</t>
<t tx="tbrown.20100206093837.1343">@language html
&lt;!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd"&gt;
&lt;html&gt;
  &lt;body&gt;
    &lt;h1&gt;Events&lt;/h1&gt;
    &lt;div&gt;2 events,
       2 reviews&lt;/div&gt;
    &lt;div class="event"&gt;
      &lt;h2&gt;Event 1 (2010/3/6)&lt;/h2&gt;
      &lt;p&gt;Some rambling about the event
date:2010-4-1 (no space, doesn't match)
More rambling
&lt;/p&gt;
    &lt;/div&gt;&lt;div class="event"&gt;
      &lt;h2&gt;Event 2 (2999/3/6)&lt;/h2&gt;
      &lt;p&gt;Second one
&lt;/p&gt;
      &lt;div class="reviews"&gt;
        &lt;h3&gt;Reviews&lt;/h3&gt;
        &lt;div&gt;
          &lt;b&gt;Review 1:&lt;/b&gt;***
        &lt;/div&gt;&lt;div&gt;
          &lt;b&gt;Review 2:&lt;/b&gt;************
        &lt;/div&gt;
      &lt;/div&gt;
    &lt;/div&gt;
  &lt;/body&gt;
&lt;/html&gt;</t>
<t tx="tbrown.20100206093837.1344">@nocolor

Simple Demo and Genshi Demo are scripts you can run to demonstrate the
LeoCursor class in .../plugins/leocursor.py.

The cursor is used by "non-Leo" code (Simple Demo and Genshi Demo) to
access the structured data in the Data node.

Simple Demo simply prints its output on stdout.

The Genshi Demo requires the genshi html templating language module,
but it doesn't really do anything the Simple Demo doesn't, it's just
there to test LeoCursor in an intended application (i.e. Genshi templates).

The output from the Genshi Demo is placed in the "leocursordemo.html"
node, so you can view it there even if you don't have Genshi installed.
</t>
</tnodes>
</leo_file>
