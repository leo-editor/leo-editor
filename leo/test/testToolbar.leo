<?xml version="1.0" encoding="utf-8"?>
<?xml-stylesheet ekr_test?>
<leo_file>
<leo_header file_format="2" tnodes="0" max_tnode_index="0" clone_windows="0"/>
<globals body_outline_ratio="0.5">
	<global_window_position top="51" left="243" height="634" width="1161"/>
	<global_log_window_position top="0" left="0" height="0" width="0"/>
</globals>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="bobjack.20080424195922.3" str_leo_pos="1,0"><vh>Startup</vh>
<v t="bobjack.20080424195922.2" str_leo_pos="1"><vh>@chapters</vh></v>
</v>
<v t="bobjack.20080424195922.90" a="E"><vh>Buttons</vh>
<v t="bobjack.20080427085237.1"><vh>@button Fav Button</vh></v>
<v t="bobjack.20080427084403.1"><vh>@button Say Hello!</vh></v>
<v t="bobjack.20080427183647.2"><vh>@button show-menu-tables</vh></v>
<v t="bobjack.20080424195922.94"><vh>@button Do Unit Tests</vh></v>
</v>
<v t="bobjack.20080427091720.1"><vh>@popup test-button-menu</vh>
<v t="bobjack.20080427091720.2"><vh>@item toolbar-delete-button</vh></v>
</v>
<v t="bobjack.20080424195922.89" a="E"><vh>Unit Tests</vh>
<v t="bobjack.20080424195922.87" a="E"><vh>Test Plugin Controller</vh>
<v t="bobjack.20080424224706.1"><vh>@test module has required functions</vh></v>
<v t="bobjack.20080424195922.88"><vh>@test ivars exist and have correct type</vh></v>
<v t="bobjack.20080424224706.2"><vh>@test Controller Methods</vh>
<v t="bobjack.20080424224706.8"><vh>@test createCommandCallbacks</vh></v>
<v t="bobjack.20080424224706.22"><vh>@test getCommandList</vh></v>
<v t="bobjack.20080424224706.15"><vh>@test onClose</vh></v>
<v t="bobjack.20080424224706.16"><vh>@test onCreate</vh></v>
<v t="bobjack.20080424224706.23"><vh>@test registerCommands</vh></v>
</v>
</v>
</v>
</vnodes>
<tnodes>
<t tx="bobjack.20080424195922.2"></t>
<t tx="bobjack.20080424195922.3"></t>
<t tx="bobjack.20080424195922.87"></t>
<t tx="bobjack.20080424195922.88">import toolbar
plugin = toolbar

testController = tc = plugin.pluginController(c)

liveController = lc = plugin.controllers.get('c')

ivars = plugin.requiredIvars

for ivar, kind in ivars:
    
    if lc:
        assert hasattr(lc, ivar), \
            "Live controller does not have attribute: %s" % ivar
    
    assert hasattr(tc, ivar), \
        "Test controller does not have attribute: %s" % ivar
    
    if not kind:
        continue
        
    if lc:
        val = getattr(lc, ivar)
        assert isinstance(val, kind), \
            "Live Controller has ivar of wrong type\n\tGot type: %s\n\tExpected: %s" %(
                type(val), kind)
    
       
    val = getattr(tc, ivar)
    assert isinstance(val, kind), \
        "Test Controller has ivar of wrong type\n\tGot type: %s\n\tExpected: %s" %(
            type(val), kind)</t>
<t tx="bobjack.20080424195922.89"></t>
<t tx="bobjack.20080424195922.90">@
The following buttons are provided:

    show-toolbar-tables:

        This button pretty prints the rclick menu tables in
        c.context_menus to the log panel.

    show-button-events:

        After clicking this button, all clicks to the radio and
        check button menu items will be reported in the log
        panel.


    show-button-data:

        This button prints the status of the radio groups and check
        buttons that are used in the menus.

    do-unit-tests:

        This button runs all the unit tests for the toolbar
        plugin.  There are not many of them yet but that will
        change over time.

</t>
<t tx="bobjack.20080424195922.94">@
@btn fg = red
@btn bg = white
@btn tooltip = Run All Unit Tests
@btn menu = test-button-menu
@c

import leoTest
leoTest.doTests(c,all=True)
</t>
<t tx="bobjack.20080424224706.1">import toolbar
plugin = toolbar

for name in (
    'init',
    'onPreCreate',
    'onCreate',
    'onClose',
    'pluginController',
):
    assert hasattr(plugin, name), \
        "%s is missing"
</t>
<t tx="bobjack.20080424224706.2">from toolbar import pluginController

controller = pluginController(c)

headlines = [p.headString() for p in p.children_iter()]

for h in headlines:
    if h.startswith('@test'):
        h = h[5:].strip()
        
        assert hasattr(controller, h), \
            "Controller has no method %s" % h
            
# test for unknown methods


</t>
<t tx="bobjack.20080424224706.8"></t>
<t tx="bobjack.20080424224706.15"></t>
<t tx="bobjack.20080424224706.16"></t>
<t tx="bobjack.20080424224706.22"></t>
<t tx="bobjack.20080424224706.23"></t>
<t tx="bobjack.20080427084403.1">@
@btn bg = lightgreen
@btn fg = blue
@btn tooltip = Say: Hello!
@btn menu = test-button-menu
@c
g.es('Hello!')</t>
<t tx="bobjack.20080427085237.1">@
@btn icon = Tango\16x16\emblems\emblem-favorite.png
@btn bg=
@btn tooltip = Say: I Love Leo
@btn menu = test-button-menu
@c

g.es('I LOVE LEO')</t>
<t tx="bobjack.20080427091720.1"></t>
<t tx="bobjack.20080427091720.2">Remove Button

icon = Tango\16x16\actions\stop.png</t>
<t tx="bobjack.20080427183647.2">from pprint import pformat

g.es_print(pformat(c.context_menus))</t>
</tnodes>
</leo_file>
