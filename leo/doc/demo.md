# Leo's demo.py plugin

The demo.py plugin helps presenters run dynamic demos from Leo files.

- [Leo's demo.py plugin](../doc/demo.md#leos-demopy-plugin)
- [Overview](../doc/demo.md#overview)
- [Graphics classes](../doc/demo.md#graphics-classes)
- [Using demo scripts](../doc/demo.md#using-demo-scripts)
    - [Script trees and lists](../doc/demo.md#script-trees-and-lists)
    - [Predefined symbols](../doc/demo.md#predefined-symbols)
    - [Positioning graphics](../doc/demo.md#positioning-graphics)
    - [Deleting graphics](../doc/demo.md#deleting-graphics)
    - [Details](../doc/demo.md#details)
- [Example scripts](../doc/demo.md#example-scripts)
    - [Top-level script](../doc/demo.md#top-level-script)
    - [Simulate typing](../doc/demo.md#simulate-typing)
    - [Add graphics](../doc/demo.md#add-graphics)
    - [Change the demo namespace](../doc/demo.md#change-the-demo-namespace)
    - [Switch focus](../doc/demo.md#switch-focus)
- [Helper methods](../doc/demo.md#helper-methods)
    - [Ivars](../doc/demo.md#ivars)
    - [Menus](../doc/demo.md#menus)
    - [Magnification and styling](../doc/demo.md#magnification-and-styling)
    - [Setup and teardown](../doc/demo.md#setup-and-teardown)
    - [Window Position](../doc/demo.md#window-position)
    - [Typing](../doc/demo.md#typing)
- [History](../doc/demo.md#history)

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

# Graphics classes

The demo.py file defines 5 classes that create graphics.  All classes add the created widget to demo.widgets, ensuring that the widget remains visible.

**arguments**: All classes have defaults, shown below, that subclasses may change.  Unless noted, position=None centers the widget in the middle of the body pane.

The valid arguments for the `pane` argument are `None, 'body', 'log', 'tree`. `None` is same as `body`. 

**Callout**: Add a QLabel containing text.

```python
Callout(text, font=None, pane=None, position=None, stylesheet=None)
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
demo.start(script_tree, delim='###')
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

- Chaining from one script to another using demo.next() in the demo script is valid and harmless.  Yes, this creates a recursive call to demo.next(), but this would be a problem only if a presentation had hundreds of demo scripts.

- The demo-next command *must* be bound in the top-level script, as shown in the example in scripts.leo. The demo-end and demo-prev commands may be bound in myLeoSettings.leo as usual.

# Example scripts

The demo plugin does not change focus in any way, nor does it interfere with Leo's key handling. As a results, *demo scripts work just like normal Leo scripts*.

## Top-level script

Here is a recommended top-level node for the top-level script, in an `@button MyDemo @key=Ctrl-9` node. scripts.leo contains the actual script.

```python

# << imports >>
from leo.core.leoQt import QtGui
import leo.plugins.demo as demo_module
import imp
imp.reload(demo_module)

# << class MyDemo >>
class MyDemo (demo_module.Demo):
    
    def setup(self, p=None):
        c = self.c
        self.end_on_exception = True # Good for debugging.
        self.delta = 0
        p = g.findNodeAnywhere(c, 'Demo Area')
        self.root = p.copy() if p else None
        if p:
            c.selectPosition(p)
            c.redraw()
        self.set_youtube_position()

    def setup_script(self):
        self.delete_widgets()
        
    def teardown(self):
        c = self.c
        self.delete_all_widgets()
        if hasattr(self, 'delta') and self.delta > 0:
            self.set_text_delta(-self.delta)
        if self.root and c.positionExists(self.root, trace=False):
            c.selectPosition(self.root)
            c.redraw()
# Don't use @others here.
try:
    if getattr(g.app, 'demo', None):
        g.app.demo.next()
    else:
        g.cls()
        c.frame.log.clearTab('Log')
        g.es_print('Starting MyDemo')
        c.k.demoNextKey = c.k.strokeFromSetting('Ctrl-9')
            # Tell k.masterKeyHandler to process Ctrl-9 immediately.
            # Binding demo-next in a setting does *not* work.
        demo = MyDemo(c, trace=False)
        p = g.findNodeAnywhere(c, '@button Demo @key=Ctrl-9')
        demo.start(script_tree=g.findNodeInTree(c, p, 'demo-script'))
except Exception:
    g.app.demo = None
    raise
```

And here is an example script_string:

```python
script_string = '''\
demo.bind('greeting', 'Hello World')
w = Image('C:/leo.repo/leo-editor/leo/Icons/SplashScreen.ico')
demo.retain(w)
Callout('Callout 1 centered')
Title('This is title 1')
###
Callout('Callout 2 (700, 200)', position=[700, 200])
Title('This is title 2')
###
demo.delete_retained_widgets()
Text(greeting,
    font=QtGui.QFont('Verdana', 18),
    position=(200, 40),
    size=(100, 200))
###
Callout('Callout 3 (200, 300)', position=[200, 300])
Title('This is title 3')
###
Callout('Callout 4 (center, 200)', position=['center', 200])
Title('This is a much much longer title 4')
###
Callout('Callout 5 (700, center)', position=[700, 'center'])
Title('Short 5')
###
demo.next()
'''
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

## Add graphics

Add an image:

```python
Image(g.os_path_finalize_join(
    g.app.loadDir, '..', 'Icons', 'SplashScreen.ico'))
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

```
Callout('Hello World')
```

Add a subtitle, centered just above the minibuffer:

```
Title('It was the best of times...')
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
demo.init_namespace() initializes demo.namespace at the start of the demo. Subclasses may override init.namespace for complete control of the scripting environment:
```
import leo.plugins.demo as demo_module
Demo = demo_module.Demo
class MyDemo(Demo):
    def init_namespace(self):
        super(Demo, self).init_namespace()
        self.namespace.update({
            'MyCallout': MyCallout,
            'MyImage': MyImage,
        })
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

**demo.n1** and **demo.n2** These ivars control the speed of the simulated typing.

Demo scripts may change n1 or n2 at any time. If both are given, each character is followed by a wait of between n1 and n2 seconds. If n2 is None, the wait is exactly n1. The default values are 0.02 and 0.175 seconds.

**demo.namespace**: The environment in which scripts execute.

**demo.speed**: A multiplier applied to n1 and n2.

This ivar is initially 1.0.  The demo.wait method multiplies both the n1 nd n2 ivars by the speed factor before waiting.

**demo.retained_widgets**: A list of widgets *not* deleted by demo.delete_widgets()

**demo.user_dict**:  Python dictionary that demo scripts may freely use.

**demo.widgets**: A list of references to allocated widgets.

Standard graphics classes add themselves to this list automatically.

## Menus

**demo.open_menu(menu_name)**: Opens the menu whose name is given.

Don't worry about case or non-alpha characters in menu_name. This method shows all parent menus, so demo.open_menu('cursorback') suffices to show the `Cmds\:Cursor/Selection\:Cursor Back...` menu.

**demo.dismiss_menubar()**: Close the menu opened with demo.open_menu.

## Magnification and styling

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

## Setup and teardown

Subclasses of Demo may override any of the following:

**demo.init_namespace**: Creates demo.namespace with default symbols.

**demo.setup(p=None)**: Called before executing the first demo script.

**demo.setup_script()**: Called before executing each demo script.

**demo.teardown()**: Called just before ending the demonstration.

**demo.teardown_script():** Called after executing each demo script.

## Window position

**demo.set_window_size(width, height)** Set the size of Leo's main window, in pixels.

**demo.set_window_position(x, y):** Move the top-left corner of Leo's main window to x, y, in pixels.

**demo.set_youtube_position()**: Resize and position Leo's main window for YouTube.

## Typing

**demo.body_keys(s, undo=False)**: Simulates typing the string s in the body pane.

**demo.head_keys(s, undo=False)**: Simulates typing the string s in the body pane.

**demo.keys(s, undo=False)**: Simulates typing the string s in the present widget.

**demo.key(setting)**: Types a single key in the present widget. This method does not support undo.

These methods call `c.undoer.setUndoTypingParams(...)` only if the `undo` keyword argument is True.  Methods without an `undo` argument do not support undo .

```python
   demo.key('Alt-X') # Activate the minibuffer
   demo.key('Ctrl-F') # Execute Leo's Find command
```

# History

Edward K. Ream wrote and debugged this plugin from January 29 to February 10, 2017. The [demo-it](https://github.com/howardabrams/demo-it/blob/master/demo-it.org) inspired this plugin. Or perhaps the screencast plugin inspired demo-it.

