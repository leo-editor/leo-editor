# Leo's demo.py plugin

The demo.py plugin helps presenters run dynamic demos from Leo files.

- [Overview](../doc/demo.md#overview)
- [Demo scripts](../doc/demo.md#demo-scripts)
- [Example scripts](../doc/demo.md#example-scripts)
- [Helper methods](../doc/demo.md#helper-methods)
    - [Images](../doc/demo.md#images)
    - [Menus](../doc/demo.md#menus)
    - [Starting and ending](../doc/demo.md#starting-and-ending)
    - [Typing](../doc/demo.md#typing)
- [Magnification and styling](../doc/demo.md#magnification-and-styling)
- [Details](../doc/demo.md#details)
- [Acknowledgements](../doc/demo.md#acknowledgements)

# Overview

A **script tree**, a tree of **demo scripts**, controls the demo. Demo scripts free the presenter from having to type correctly or remember sequences of desired actions. 

The **demo-next** command executes the next demo script.  The plugin ends the presentation just after executing the last demo script. The **demo-end** command ends the demo early.

To start a demo, presenters run a **top-level script**. Top-level scripts instantiate the Demo class, and then call one of three demo.start_* methods.

This plugin boasts significant advantages compared with Leo's screencast plugin:

- The demo plugin does not interfere with focus or key-handling. As a result, the full power of Leo scripting is available to demo scripts. Few helper methods are needed.

- Demo scripts are mostly descriptive. Subclasses of demo.Demo can define methods that hide implementation and configuration details.

- Demo scripts can insert fixed delays, callouts and subtitles. As a result, demo scripts can be fully automated. There is little need for post-production editing.

# Demo scripts

These methods can:

- Simulate typing in headlines, body text, the minibuffer, or anywhere else.
- Overlay a scaled image on the screen.
- Open any Leo menu, selecting particular menu items.
- Help init graphics classes.
- Scale font sizes.

For example, this demo script executes the insert-node command:

```python
    demo.key('Alt-x')
    demo.keys('insert-node\n')
```

Within the script tree, **@ignore** and **@ignore-tree** work as expected. The demo-script command ignores any nodes whose headline starts with `@ignore`, and ignores entire trees whose root node's headline starts with `@ignore-tree`.

**Note**: The demo-next command executes demo scripts *in the present outline*. Demo scripts may create new outlines, thereby changing the meaning of c. It is up to each demo script to handle such complications.

## ** Creating demo scripts from trees and strings
def start(self, p=None, script_list=None, script_string=None, delim='###'):
    '''
    Start a demo whose scripts are given by:
    script_string is not None:  a single string, with given delim.
    script_list is not None:    a list of strings,
    p is not None:              The body texts of a tree of nodes.
    '''

## Predefined symbols and demo.init_namespace
Demo scripts execute in the **demo.namespace** environment. This is a python dict containing:

- c, g and p as usual,
- the names of all graphics classes: Callout, Image, Label, Text and Title,
- and the name **demo**, bound to the Demo instance.

demo.namespace is cleared when a demo starts. It *persists* until the end of the demo.



As a result, demo scripts can share information.  For example:

```
demo.bind('greeting', hello world')
###
print(greeting)
```



Demo scripts also have access to the predefined **demo** variable, bound to the Demo instance. This allows demo scripts to use all the **helper methods** in the Demo class.

Subclasses may override **demo.init_namespace()** or add to the initial namespace with:


**demo.namespace** is a persistent python dictionsary  

```python
demo.namespace.update({
    'name1': object1,
    'name2': object2,
    })
```

# Example scripts
Demo scripts may freely use all of Leo's scripting API. The demo plugin does not interfere in any way.

## Show typing in the minibuffer
```python
demo.key('Alt+x')
demo.keys('insert-node')
demo.wait(2)
demo.key('\n')
```

## Show typing in a headline
```python
c.insertHeadline()
c.redraw()
c.editHeadline()
demo.head_keys('My Headline')
demo.wait(1)
c.endEditing()

# wrapper = c.edit_widget(p)
# wrapper.setSelectionRange(0, len(p.h))
```

## Show an image
```python
Image(g.os_path_finalize_join(
    g.app.loadDir, '..', 'Icons', 'SplashScreen.ico'))
```

## Show a text area
```python
Text('This is a text area',
    font=QtGui.QFont('Verdana', 14),
    position=(20, 40),
    size=(100, 200),
)

## Show a text callout
```python
# By default, callouts are centered in the body pane.
Callout('Callout 1 centered')

# Callouts may be positioned in various ways...
Callout('Callout 2 (700, 200)', position=[700, 200])

Callout('Callout 4 (center, 200)', position=['center', 200])

Callout('Callout 5 (700, center)', position=[700, 'center'])
```

## Show a text Title
```python
# By default Titles are centered at the bottom of the body pane.
# Titles may be positioned just as Callouts are.
Title('This is title 1')
```

## Deleting widgets
By default, all allocated widgets appear in the **demo.widgets** list.

Calling **demo.delete_widgets** deletes all widgets and removes them from the screen.

Widgets can be retained until some later slide using **demo.retain(w):

```python

w = Callout('Callout 42')
demo.retain(w)
###
...
###
demo.delete_retained()
```

Finally, demo scripts can handle deleting of a single widget, as shown:

```python
w = Image(g.os_path_finalize_join(
    g.app.loadDir, '..', 'Icons', 'SplashScreen.ico'))
demo.retain(w)
demo.user_dict ['splash'] = w
###
demo.delete_one_widget(demo.user_dict.get('splash'))

## Altering the demo namespace
**demo.bind(name, object)** adds an entry to this dictionary.
```python
demo.bind('greeting', 'Hello World')
```
This is equivaent to:
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

## Select all headline text
```python
'''Begin editing a headline and select all its text.'''
c.editHeadline()
wrapper = c.edit_widget(p)
wrapper.setSelectionRange(0, len(p.h))
```

# Helper methods

The following sections describe all public ivars and helper methods of the Demo class.

The valid values for `pane` arguments are the strings, "body", "log" or "tree".

Helper methods call `c.undoer.setUndoTypingParams(...)` only if the `undo` keyword argument is True.  Methods without an `undo` argument do not support undo .

## Ivars

**demo.user_dict**

This ivar is a Python dictionary that demo scripts may freely use.

**demo.n1** and **demo.n2**

These ivars determine the speed of the simulated typing provided by the following methods. Demo scripts may change either at any time. If both are given, each character is followed by a wait of between n1 and n2 seconds. If n2 is None, the wait is exactly n1. The default values are 0.02 and 0.175 seconds, respectively.

**demo.speed**

This ivar is initially 1.0.  The demo.wait method multiplies both the n1 nd n2 ivars by the speed factor before waiting.  So using demo.speed factor is the easy way to adjust simulated typing speed.

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

## Starting and ending

**demo.setup(p)**

May be overridden in subclasses. Called before executing the first demo script.

**demo.start(p)**

Starts a demo. p is the root of demo script tree. 

**demo.end()**

Ends the demo and calls the teardown script. The demo automatically ends after executing the last demo script.

**demo.teardown()**

May be overridden in subclasses. Called when the demo ends.

## Typing

**demo.body_keys(s, undo=False)**

Simulates typing the string s in the body pane.

**demo.head_keys(s, undo=False)**

Simulates typing the string s in the body pane.

**demo.keys(s, undo=False)**

Simulates typing the string s in the present widget.

**demo.key(setting)**

Types a single key in the present widget. This method does not support undo. Examples:
```python
   demo.key('Alt-X') # Activate the minibuffer
   demo.key('Ctrl-F') # Execute Leo's Find command
```

# Magnification and styling

**demo.set_text_delta(self, delta, w=None)**

Updates the style sheet for the given widget w (default is the body pane). Delta increases the text size by the given number of points.

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

# Details

- Demo scripts can not be undone/redone in a single step, unless each demo script makes *itself* undoable.

- Leo's undo command is limited to the presently selected outline. If a demo script opens another outline, there is no *automatic* way of selecting the previous outline.

- Chaining from one script to another using demo.next() cause a recursion. This would be a problem only if a presentation had hundreds of demo scripts.

# Acknowledgements

Edward K. Ream wrote this plugin on January 29-31, 2017, using Leo's screencast plugin as a starting point. 

The [demo-it](https://github.com/howardabrams/demo-it/blob/master/demo-it.org) inspired this plugin. Or perhaps the screencast plugin inspired demo-it.

