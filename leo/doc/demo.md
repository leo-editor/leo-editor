# Leo's demo.py plugin

The demo.py plugin helps presenters run dynamic demos from Leo files.

- [Leo's demo.py plugin](../doc/demo.md#leos-demopy-plugin)
- [Overview](../doc/demo.md#overview)
- [A simpler work flow](../doc/demo.md#a-simpler-work-flow)
- [Graphics classes & helpers](../doc/demo.md#graphics-classes--helpers)
- [Using demo scripts](../doc/demo.md#using-demo-scripts)
    - [Script trees and lists](../doc/demo.md#script-trees-and-lists)
    - [Predefined symbols](../doc/demo.md#predefined-symbols)
    - [Positioning graphics](../doc/demo.md#positioning-graphics)
    - [Deleting graphics](../doc/demo.md#deleting-graphics)
    - [Details](../doc/demo.md#details)
- [Example scripts](../doc/demo.md#example-scripts)
    - [Top-level script](../doc/demo.md#top-level-script)
    - [Simulate typing](../doc/demo.md#simulate-typing)
    - [Change the demo namespace](../doc/demo.md#change-the-demo-namespace)
    - [Add graphics](../doc/demo.md#add-graphics)
    - [Switch focus](../doc/demo.md#switch-focus)
- [Helper methods](../doc/demo.md#helper-methods)
    - [Ivars](../doc/demo.md#ivars)
    - [Menus](../doc/demo.md#menus)
    - [Magnification and styling](../doc/demo.md#magnification-and-styling)
    - [Simulated typing](../doc/demo.md#simulated-typing)
    - [Startup, setup and teardown](../doc/demo.md#startup-setup-and-teardown)
    - [Window position and ratios](../doc/demo.md#window-position-and-ratios)
- [Summary](../doc/demo.md#summary)
- [History and change log](../doc/demo.md#history-and-change-log)

# Overview

A **presentation** consists of one or more **slides**, created by **demo scripts**.
Demo scripts free the presenter from having to type correctly or remember sequences of desired actions. The demo plugin does not interfere with focus or key-handling, so demo scripts can freely call all of Leo's regular scripting API. Demo scripts can:

- Simulate typing in headlines, body text, the minibuffer, or anywhere else.
- Show **graphics**, including scaled images, callouts and text areas.
- Open any Leo menu, selecting particular menu items.
- Scale font sizes.

For example, this demo script executes the insert-node command:

```python
    demo.key('Alt-x')
    demo.keys('insert-node\n')
```

**Creating the demo**: To start a demo, presenters run a **top-level script**. These scripts instantiate the Demo class and call **demo.start**. As discussed later, demo.start creates demo scripts from its arguments.

**Controlling the presentation**: The **demo-next** command executes the next demo script. The **demo-prev** command executes the previous demo. The presentation ends after executing the last demo script. The **demo-end** command ends the demo early. Presentations can be made fully automated by having demo scripts move from slide to slide with appropriate delays between each.

**Adding graphic to slides**: Demo scripts may use predefined **graphics classes** to show callouts, subtitles or images. These graphics persist from slide to slide until deleted. Subclasses of Demo may easily subclass the predefined classes.

# A simpler work flow
The workflow just described demo works well for interactive demos. An easier work flow suffices for non-interactive demos. Two \@button nodes in LeoDocs.leo illustrate the difference in these two approaches:

\@button IntroSlides uses the interactive work flow. It defines a subclass of the Demo class, including setup and teardown methods when entering and leaving a slide.  And it defines a "slides tree" that contains the actual slides.

@button demo creates a non-interactive demo. It uses the base Demo class, and defines a single script to be run from start to finish. The <\< utils >\> section defines some simple utilities:  highlight, unhighlight, update, wait. Everything else (@others) defines a sequence of actions.

The top-level node (its headline is top-level) is:

```python
ssm = c.styleSheetManager
d = demo.Demo(c)
d.delete_widgets()
\@others # slides
update()
c.bodyWantsFocusNow()
```

A single node suffices to demonstrate three panes:

```python
for pane in ('body', 'tree', 'log'):
    highlight(pane)
    d.Callout('%s %s' % (pane.capitalize(), pane), pane=pane)
    wait()
    unhighlight(pane)
```

highlight(pane) is the "setup" action, wait() denotes the end of the slide, and unhighlight(pane) is the "teardown" action.

Now here is the important part:  **@others organizes the slides**.  No need for any fancy conventions about where slides start and end.  Just use Leo's natural tree structure, including empty organizer nodes if you like.

**Summary**

The wait() utility waits for a fixed length of time, which can be set by a keyword arg.  It could also call Python's input() function to wait for a keystroke.

The non-interactive pattern is simpler than the interactive pattern. The interactive pattern is more flexible. It allows the presenter to move backward and forward through slides, something that is not possible with the new, simpler pattern.  Otoh, the new pattern is a good way to prototype interactive demos.

# Graphics classes & helpers

The demo.py file defines 5 classes that create graphics.  All classes add the created widget to demo.widgets, ensuring that the widget remains visible.

**arguments**: All classes have defaults, shown below, that subclasses may change.  Unless noted, position=None centers the widget in the middle of the body pane.

The valid arguments for the `pane` argument are `None, 'body', 'log', 'tree`. `None` is same as `body`. 

**Callout**: Add a QLabel containing text.

```python
Callout(text, font=None, pane=None, position=None, stylesheet=None)
```

**Head**: Add a label to a headline, given only its headline(!).

```python
Head(arrow, label, headline, offset=None)
```

**Image**: Add a QLabel containing an image.

```python
Image(fn, pane=None, position=None, size=None)
```

**Text**: Add a QTextEdit.

```python
Text(text, font=None, pane=None, position=None, size=None, stylesheet=None)
```

**Title**: Add a QLabel containing text, centered horizontally, positioned near the bottom of the body pane.

```python
Title(text, font=None, pane=None, position=None, stylesheet=None)
```

# Using demo scripts

## Script trees and lists

A **script tree**, a tree of **script nodes**, specifies the script.

```python
demo.start(script_tree, auto_run=False delim='###')
```

Script nodes may contain multiple demo scripts, separated by a **script delimiter**:

```python
Callout('Callout 1')
Title('Title 1')
###
Callout('Callout 2')
Title('This is a much much longer title')
```

The Demo startup code converts the script tree to a linear **script list**, composed of the body text of all nodes in script tree, ignoring:

- Nodes whose body text contains nothing but whitespace or python comments.
- `@ignore` nodes.
- All nodes in an `@ignore-tree` tree.

## Predefined symbols

Demo scripts execute in the **demo.namespace** environment. This is a python dict containing:

- c, g and p as usual,
- The names of all predefined graphics classes: Callout, Image, Label, Text and Title,
- The name **demo**, bound to the Demo instance.

At startup, **demo.init_namespace()** creates demo.namespace. Subclasses may override this method.

**demo.bind(name, object)** adds one binding to demo.namespace. The following are equivalent:

```python
demo.bind('name', object)
demo.namespace.update({'name', object})
```

The demo.namespace environment *persists* until the end of the demo, so demo scripts can share information:

```python
demo.bind('greeting', hello world')
###
Callout(greeting)
```

## Positioning graphics

By default, graphics are centered horizontally and vertically in the body pane.  The **position** keyword arg positions a graphic explicitly.

```python
Callout('Callout 1')
Callout('Callout 1', position='center') # same as above.
Callout('Callout 2 ', position=[700, 200])
Text('Hello world', position=['center', 200])
Title('This is a subtitle', position=[700, 'center'])
```

## Deleting graphics

By default, **demo.widgets** contains references to all allocated widgets. Without these references, Python's garbage collector would destroy the widgets.

**demo.delete_widgets()** destroys all the widgets in that list by calling w.deleteLater and clears demo.widgets.

```python
Callout('Callout 1')
###
delete_widgets()
Callout('Callout 2')
```

**demo.retain(w)** adds widget w to **demo.retained_widgets**.

**demo.delete_retained()** deletes all retained widgets, removes retained items from demo.widgets and clears demo.retained_widgets.

```python

w = Callout('Callout 42')
demo.retain(w)
###
...
###
demo.delete_retained()
```

**demo.delete_one_widget(w)** calls w.deleteLater() and removes w from demo.widgets and demo.retained_widgets.

```python
w = Image(g.os_path_finalize_join(
    g.app.loadDir, '..', 'Icons', 'SplashScreen.ico'))
demo.user_dict ['splash'] = w
###
...
###
w = demo.user_dict['splash']
del demo.user_dict['splash']
demo.delete_one_widget(w)
```

## Details

- Demo scripts can not be undone/redone in a single step, unless each demo script makes *itself* undoable.

- The demo-next command executes demo scripts *in the present outline*. Demo scripts may create new outlines, thereby changing the meaning of c. It is up to each demo script to handle such complications.

- Leo's undo command is limited to the presently selected outline. If a demo script opens another outline, there is no *automatic* way of selecting the previous outline.

- The demo-next command *must* be bound in the top-level script, as shown in the example in scripts.leo. The demo-end and demo-prev commands may be bound in myLeoSettings.leo as usual.

# Example scripts

The demo plugin does not change focus in any way, nor does it interfere with Leo's key handling. As a results, *demo scripts work just like normal Leo scripts*.

## Top-level script

Here is a recommended top-level node for the top-level script, in an `@button MyDemo @key=Ctrl-9` node. scripts.leo contains the actual script.



```python

'''Create intro slides for screen shots.'''
if c.isChanged():
    c.save()

# << imports >>
from leo.core.leoQt import QtGui
import leo.plugins.demo as demo_module

# Do NOT use @others here.

# << class IntroSlides >>
class IntroSlides (demo_module.Demo):

    def setup(self, p=None):
        c = self.c
        self.end_on_exception = True # Good for debugging.
        self.delta = 0
        self.ratios = self.get_ratios()
        self.set_text_delta(self.delta)
        if hasattr(self, 'hoist_node'):
            c.selectPosition(self.hoist_node)
            for child in self.hoist_node.children():
                if child.h. startswith('@@'):
                    child.h = child.h[1:]
                    child.clearDirty()
            c.hoist()
        self.set_top_geometry((400, 200, 700, 400),)
            # x, y, width, height, like QRect.
        c.redraw()

    def setup_script(self):
        self.delete_widgets()

    def teardown(self):
        c = self.c
        self.delete_all_widgets()
        if self.delta > 0:
            self.set_text_delta(-self.delta)
        if self.hoist_node:
            for child in self.hoist_node.children():
                if child.h. startswith('@'):
                    child.h = '@' + child.h
            c.dehoist()
            # c.selectPosition(self.hoist_node)
        p = g.findTopLevelNode(c, "Slide 1: Leo's main window")
        if p:
            c.selectPosition(p)
        ratio1, ratio2 = self.ratios
        self.set_ratios(ratio1, ratio2)
        c.contractAllHeadlines()
        c.clearChanged()
        c.redraw()

    def teardown_script(self):
        if self.auto_run:
            self.wait(0.5)

# << main >>
def main(c, demo, script_name, auto_run=False, hoist_node=None):
    g.cls()
    k = c.k
    class_name = demo.__class__.__name__
    g.es_print('Starting', class_name)
    k.demoNextKey = k.strokeFromSetting('Ctrl-9')
        # Tell k.masterKeyHandler to process Ctrl-9 immediately.
        # Binding demo-next in a setting does *not* work.
    h = '@button %s @key=Ctrl-9' % class_name
    p = g.findNodeAnywhere(c, h)
    assert p, h
    script_tree = g.findNodeInTree(c, p, script_name)
    assert script_tree, repr(script_name)
    demo.hoist_node = hoist_node and g.findNodeInTree(c, p, hoist_node)
    demo.start(script_tree, auto_run=auto_run)

# The top-level of the top-level script...

# The *same* command/key binding calls both demo-start and demo.next.
if getattr(g.app, 'demo', None):
    g.app.demo.next()
else:
    demo = IntroSlides(c)
    main(c, demo,
        auto_run=False,
        hoist_node = "Leo's Main Window",
        script_name='intro-slides-script')
```


Here are two example script_string. The first creates two screenshots, with lots of callouts.



```python
demo.set_top_size(height=400, width=700)
demo.set_ratios(0.5, 0.5)
geom = demo.pane_geometry('body')
table = (
    ('body', 'The Body Pane'),
    ('tree', 'The Outline Pane'),
    ('log',  'The Log Pane'),
)
for pane, h in table:
    Callout(h, pane=pane)
###
demo.set_top_size(height=500, width=800)
table = (
    (False, 0, '<-- @file node', '@file leoApp.py'),
)
for arrow, offset, label, headline in table:
    Head(arrow, label, headline, offset=offset)
w = Image(fn=demo.get_icon_fn('box01.png'), position=(20, 30), magnification=2)
Callout('<-- An Icon', position=(20+w.width(), w.y()-3))
###
demo.next()
```


The second example script_string adds and demotes nodes:


```python
# Create, move, promote, demote, hoist.
demo.retain(Title('Leo is a full featured outliner.'))
demo.wait(1.0)
###
demo.insert_node('a new node', keys=True, speed=10.0)
###
c.moveOutlineRight()
###
# demo.end() # Test of early exit.
###
demo.insert_node('another headline')
###
demo.insert_node('yet another node')
###
p = g.findNodeInTree(c, demo.root, 'a new node')
assert p, 'a new node'
c.selectPosition(p)
demo.wait(0.25)
###
c.demote()
demo.wait(1.0)
###
demo.delete_retained_widgets()
```

## Simulate typing

Simulate typing in the minibuffer:

```python
demo.key('Alt+x')
demo.keys('insert-node')
demo.wait(2)
demo.key('\n')
```

Simulate typing in a headline:

```python
c.insertHeadline()
c.redraw()
c.editHeadline()
demo.head_keys('My Headline')
demo.wait(1)
c.endEditing()
```

Begin editing a headline and select all headline text:

```python
c.editHeadline()
wrapper = c.edit_widget(p)
wrapper.setSelectionRange(0, len(p.h))
```

## Change the demo namespace

**demo.bind(name, object)** adds an entry to this dictionary.

```python
demo.bind('greeting', 'Hello World')
```

This is equivalent to:

```python
demo.namespace.update({'greeting': 'Hello World'})
```

**demo.init_namespace()**: Initializes demo.namespace at the start of the demo. Subclasses may override init.namespace for complete control of the scripting environment:

```python
import leo.plugins.demo as demo_module
Demo = demo_module.Demo
class MyDemo(Demo):
    def init_namespace(self):
        Demo.init_namespace(self)
        self.namespace.update({
            'MyCallout': MyCallout,
            'MyImage': MyImage,
        })
```

## Add graphics

Add an image:

```python
Image(fn=demo.get_icon_fn('box01.png'),
      position=(20, 30),
      magnification=2)
```

Add a text area:

```python
Text('This is a text area',
     font=QtGui.QFont('Verdana', 14),
     position=(20, 40),
     size=(100, 200),
)
```

Add a callout, centered in the body area:

```python
Callout('Hello World')
```

Add a callout for a headline:

```python
Head(arrow=False, '<-- @file node', headline='@file leoApp.py', offset=None)
```

Add a subtitle, centered just above the minibuffer:

```
Title('It was the best of times...')
```

## Switch focus

```python
# Put focus to the tree.
c.treeWantsFocusNow()
# Put focus to the minibuffer.
c.minibufferWantsFocusNow()
# Put focus to the body.
c.bodyWantsFocusNow()
# Put focus in the log pane.
c.logWantsFocusNow()
```

# Helper methods

The following sections describe all public ivars and helper methods of the Demo class.

## Ivars

The following discusses only those ivars that demo scripts might change.

**demo.auto_run**: A copy of the auto_run argument to demo.startup.

Overridden demo.teardown methods might insert additional delays if auto_run is True.

**demo.n1** and **demo.n2**: These ivars control the speed of the simulated typing.

Demo scripts may change n1 or n2 at any time. If both are given, each character is followed by a wait of between n1 and n2 seconds. If n2 is None, the wait is exactly n1. The default values are 0.02 and 0.175 seconds.

**demo.namespace**: The environment in which scripts execute.

**demo.speed**: A multiplier applied to n1 and n2.

This ivar is initially 1.0.  The demo.wait method multiplies both the n1 and n2 ivars by the speed factor before waiting.

**demo.retained_widgets**: A list of widgets *not* deleted by demo.delete_widgets()

**demo.user_dict**:  Python dictionary that demo scripts may freely use.

**demo.widgets**: A list of references to allocated widgets.

Standard graphics classes add themselves to this list automatically.

## Menus

**demo.open_menu(menu_name)**: Opens the menu whose name is given.

Don't worry about case or non-alpha characters in menu_name. This method shows all parent menus, so demo.open_menu('cursorback') suffices to show the `Cmds\:Cursor/Selection\:Cursor Back...` menu.

**demo.dismiss_menubar()**: Close the menu opened with demo.open_menu.

## Magnification and styling

**Important**: Images may now be scaled using the magnification arg:

```python
Image(fn=demo.get_icon_fn('box01.png'), position=(20, 30), magnification=2)
```

**demo.set_text_delta(self, delta, w=None)**: Updates the style sheet for the given widget w (default is the body pane). Delta increases the text size by the given number of points.

Presenters may alter the appearance of captions by using changing the
following stylesheet::

```css
    QPlainTextEdit#democaption {
        background-color: yellow;
        font-family: DejaVu Sans Mono;
        font-size: 18pt;
        font-weight: normal; /* normal,bold,100,..,900 */
        font-style: normal; /* normal,italic,oblique */
    }
```

You will find this stylesheet in the node @data
``qt-gui-plugin-style-sheet`` in leoSettings.leo or myLeoSettings.leo.

## Simulated typing

**demo.body_keys(s, undo=False)**: Simulates typing the string s in the body pane.

**demo.head_keys(s, undo=False)**: Simulates typing the string s in the body pane.

**demo.keys(s, undo=False)**: Simulates typing the string s in the present widget.

**demo.key(setting)**: Types a single key in the present widget. This method does not support undo.

These methods call `c.undoer.setUndoTypingParams(...)` only if the `undo` keyword argument is True.  Methods without an `undo` argument do not support undo .

```python
   demo.key('Alt-X') # Activate the minibuffer
   demo.key('Ctrl-F') # Execute Leo's Find command
```

## Startup, setup and teardown

**demo.start(script_tree, auto_run=False, delim='###')**: Start the demo, saving the geometry (size and position) of the top-level Leo window. **demo.end** restores this geometry.

- **script_tree**:  The root of a tree of script nodes.
- **auto_run**:     True: run all script nodes, one after the other.

**demo.get_ratios()**: Returns a tuple of frame ratios.

**demo.set_ratios(ratio1, ratio2)**: Set the body/outline ratio to ratio1 and the tree/log ratio to ratio2.

Subclasses of Demo may override any of the following:

**demo.init_namespace**: Creates demo.namespace with default symbols.

**demo.setup(p=None)**: Called before executing the first demo script.

**demo.setup_script()**: Called before executing each demo script.

**demo.teardown()**: Called just before ending the demonstration.

**demo.teardown_script():** Called after executing each demo script.

## Window position and ratios

**demo.headline_geometry(p)**: Return the x, y, height, width coordinates of p, for use by demo.set_geometry.

**demo.get_ratios()**: Returns a tuple (ratio1, ratio2), where ratio1 is the body/outline ratio and ratio2 is the tree/log ratio. Each ratio is a float between 0 and 1.0.

**demo.get_top_geometry()**: Return the geometry of Leo's main window.

**demo.set_ratios(ratio1, ratio2)**: Restores the body/outline and tree/log ratios.

**demo.set_top_geometry(geometry)**: Restore the geometry of Leo's main window.

**demo.set_window_size(width, height)**: Set the size of Leo's main window, in pixels.

**demo.set_window_position(x, y)**: Move the top-left corner of Leo's main window to x, y, in pixels.

**demo.set_youtube_position()**: Resize and position Leo's main window for YouTube.

# Summary

**Demos are programs in disguise**

The [top-level script](../doc/demo.md#top-level-script) is no toy. Although simple, ​the various setup/teardown methods help devs maintain momentum and energy.​ This is important, especially when planning many experiments.

The **setup** method defines the 'delta' ivar, incremented when changing font magnification in Leo's body pane. The **teardown** method restores the original font magnification. The Demo class catches all exceptions, so it can call teardown in all cases.

The **setup_script** method calls demo.delete_widgets(), freeing individual demo scripts from having to do so. See below for a practical use for **teardown_script**.

**Demos are reproducible**

Demo scripts can use *all* parts of Leo's API to "run" Leo automatically. For example, this is one way to create a new node:

```python
p = c.insertHeadline()
p.h = 'a headline'
p.b = 'some body text'
```

Presenters don't have to do anything by hand.

**Demos can be descriptive**

Demo scripts have full access to nodes in the slides. Using methods such as demo.headline_geometry, it's easy to write scripts that descriptive, rather than dependent on size and position of individual slides.

**Demos can be fully automated**

During development, it's fine to move from one slide to the next using `Ctrl-9` (demo-next) But just before creating a video or slide show, devs can define this **teardown_script**:

```python
def teardown_script(self):
    self.wait(self.inter_slide_wait)
    self.next()
```

Instant automation!  Do you see how cool this is?

# History and change log

Edward K. Ream wrote, debugged and documented this plugin from January 29 to February 14, 2017. The [demo-it](https://github.com/howardabrams/demo-it/blob/master/demo-it.org) inspired this plugin. Or perhaps the screencast plugin inspired demo-it.

**2017/02/11**: Added auto-run feature. Fixed bugs re widget visibility.

- Added the auto_run option to demo.start and the auto_run ivar.
- demo.start calls qtApp.processEvents() before each script.
- demo.delete_* call w.hide() before calling w.deleteLater().
- demo.wait() calls the new demo.repaint() method.
- demo.repaint_pane() calls w.viewport().repaint().

**2017/02/13**: Added new helpers & removed all calls to super.

- Added magnification keyword arg to Image.
- Added demo.get_ratios() and demo.set_ratios(ratio1, ratio2).
- Added demo.headline_geometry(p)
- Added Head helper.
- Added all Graphics classes and helpers to demo.namespace.
