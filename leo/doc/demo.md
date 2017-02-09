# Leo's demo.py plugin

The demo.py plugin helps presenters run dynamic demos from Leo files.

- [Leo's demo.py plugin](../doc/demo.md#leos-demopy-plugin)
- [Overview](../doc/demo.md#overview)
- [Using demo scripts](../doc/demo.md#using-demo-scripts)
    - [Creating demo lists (to do)](../doc/demo.md#creating-demo-lists-to-do)
    - [Predefined symbols](../doc/demo.md#predefined-symbols)
    - [Positioning graphics elements](../doc/demo.md#positioning-graphics-elements)
    - [Deleting graphics elements](../doc/demo.md#deleting-graphics-elements)
    - [Details](../doc/demo.md#details)
- [Example scripts](../doc/demo.md#example-scripts)
    - [Top-level script](../doc/demo.md#top-level-script)
    - [Simulate typing](../doc/demo.md#simulate-typing)
    - [Add graphics elements](../doc/demo.md#add-graphics-elements)
    - [Change the demo namespace](../doc/demo.md#change-the-demo-namespace)
    - [Switch focus](../doc/demo.md#switch-focus)
- [Helper methods](../doc/demo.md#helper-methods)
    - [Ivars](../doc/demo.md#ivars)
    - [Images](../doc/demo.md#images)
    - [Menus](../doc/demo.md#menus)
    - [Magnification and styling](../doc/demo.md#magnification-and-styling)
    - [Setup and teardown](../doc/demo.md#setup-and-teardown)
    - [Typing](../doc/demo.md#typing)
- [History](../doc/demo.md#history)

# Overview

A **presentation** consists of one or more **slides**, created by **demo scripts**.
Demo scripts free the presenter from having to type correctly or remember sequences of desired actions. The demo plugin does not interfere with focus or key-handling, so demo scripts can freely call all of Leo's regular scripting API. Demo scripts can:

- Simulate typing in headlines, body text, the minibuffer, or anywhere else.
- Show graphic elements, including scaled images.
- Open any Leo menu, selecting particular menu items.
- Scale font sizes.

For example, this demo script executes the insert-node command:

```python
    demo.key('Alt-x')
    demo.keys('insert-node\n')
```

**Creating the demo**: To start a demo, presenters run a **top-level script**. These scripts instantiate the Demo class and call **demo.start**. As discussed later, demo.start creates demo scripts from its arguments.

**Controlling the presentation**: The **demo-next** command executes the next demo script.  The presentation ends after executing the last demo script. The **demo-end** command ends the demo early. Presentations can be made fully automated by having demo scripts move from slide to slide with appropriate delays between each.

**Adding graphic to slides**: Demo scripts may use predefined **graphics classes** to show callouts, subtitles or images or other graphics elements. These graphics elements persist from slide to slide until deleted. Subclasses of Demo may easily subclass the predefined classes.

# Using demo scripts


## Creating demo lists (to do)
```def start(self, p=None, script_list=None, script_string=None, delim='###'):
    '''
    Start a demo whose scripts are given by:
    script_string is not None:  a single string, with given delim.
    script_list is not None:    a list of strings,
    p is not None:              The body texts of a tree of nodes.
    '''
```

Within the script tree, **@ignore** and **@ignore-tree** work as expected. The demo-script command ignores any nodes whose headline starts with `@ignore`, and ignores entire trees whose root node's headline starts with `@ignore-tree`.

## Predefined symbols
Demo scripts execute in the **demo.namespace** environment. This is a python dict containing:

- c, g and p as usual,
- The names of all predefined graphics classes: Callout, Image, Label, Text and Title,
- The name **demo**, bound to the Demo instance.

At startup, **demo.init_namespace()** creates demo.namespace. Subclasses may override this method. **demo.bind(name, object)** adds one binding to demo.namespace. The following are equivalent:

```python
demo.bind('name', object)
demo.namespace.update({'name', object})
```

demo.namespace *persists* until the end of the demo, so demo scripts can share information.  For example:

```python
demo.bind('greeting', hello world')
###
Callout(greeting)
```

## Positioning graphics elements
By default, graphics elements are centered horizontally and vertically in the body pane.  The **position** keyword arg positions a graphic explicitly.

```python
Callout('Callout 2 (700, 200)', position=[700, 200])
Text('Hello world', position=['center', 200])
Title('This is a subtitle', position=[700, 'center'])
```

## Deleting graphics elements
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

# Example scripts
The demo plugin does not change focus in any way, nor does it interfere with Leo's key handling. As a results, *demo scripts work just like normal Leo scripts*.

## Top-level script
Here is a recommended top-level node for the top-level script, in an `@button MyDemo @key=Ctrl-9` node. scripts.leo contains the actual script.

```python

import leo.plugins.demo as demo_module

class MyDemo (demo_module.Demo):
    def setup_script(self):
        self.delete_widgets()
        
# The *same* command/key binding calls both demo-start and demo.next.
try:
    if getattr(g.app, 'demo', None):
        g.app.demo.next()
    else:
        g.cls()
        print('starting MyDemo')
        demo = MyDemo(c, trace=False)
        demo.start(script_string=script_string)
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

Select all headline text:

```python
'''Begin editing a headline and select all its text.'''
c.editHeadline()
wrapper = c.edit_widget(p)
wrapper.setSelectionRange(0, len(p.h))
```

## Add graphics elements
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

The valid values for `pane` arguments are the strings, "body", "log" or "tree".

Helper methods call `c.undoer.setUndoTypingParams(...)` only if the `undo` keyword argument is True.  Methods without an `undo` argument do not support undo .

## Ivars

**demo.namespace**: The environment in which scripts execute.

**demo.n1** and **demo.n2** These ivars control the speed of the simulated typing.

Demo scripts may change n1 or n2 at any time. If both are given, each character is followed by a wait of between n1 and n2 seconds. If n2 is None, the wait is exactly n1. The default values are 0.02 and 0.175 seconds.

**demo.speed**: A multiplier applied to n1 and n2.

This ivar is initially 1.0.  The demo.wait method multiplies both the n1 nd n2 ivars by the speed factor before waiting.

**demo.user_dict**:  Python dictionary that demo scripts may freely use.

**demo.widgets**: A list of references to allocated widgets.

Standard graphics classes add their elements to this list automatically.

## Images

**demo.caption(s, pane)**

Creates a caption with text s in the indicated pane. A **caption** is a text area that overlays part of Leo's screen. By default, captions have a distinctive yellow background. The appearance of captions can be changed using Qt stylesheets. See below.

**demo.image(pane,fn,center=None,height=None,width=None)**

Overlays an image in a pane.

- `pane`: Valid values are 'body', 'log' or 'tree'.
- `fn`: The path to the image file, relative to the leo/Icons directory for relative paths.
- `height`: Scales the image so it has the given height.
- `width`: Scales the image i so it has the given width.
- `center`: If True, centers the image horizontally in the given pane.

## Menus

**demo.open_menu(menu_name)**

Opens the menu whose name is given, ignoring case and any non-alpha characters in menu_name. This method shows all parent menus, so demo.open_menu('cursorback') suffices to show the `Cmds\:Cursor/Selection\:Cursor Back...` menu.

**demo.dismiss_menubar()**

Close the menu opened with demo.open_menu.

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

**demo.setup_script(): Called before executing each demo script.

**demo.teardown()**: Called just before ending the demonstration.

**demo.teardown_script():** Called after executing each demo script.

## Typing

**demo.body_keys(s, undo=False)**: Simulates typing the string s in the body pane.

**demo.head_keys(s, undo=False)**: Simulates typing the string s in the body pane.

**demo.keys(s, undo=False)**: Simulates typing the string s in the present widget.

**demo.key(setting)**: Types a single key in the present widget.

This method does not support undo.
```python
   demo.key('Alt-X') # Activate the minibuffer
   demo.key('Ctrl-F') # Execute Leo's Find command
```

# History

Edward K. Ream wrote this plugin on January 29 to February 9, 2017, using Leo's screencast plugin as a starting point. 

The [demo-it](https://github.com/howardabrams/demo-it/blob/master/demo-it.org) inspired this plugin. Or perhaps the screencast plugin inspired demo-it.

