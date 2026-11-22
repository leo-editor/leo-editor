Leo https://leo-editor.github.io/leo-editor/ 6.9.0 is now available on [GitHub](https://github.com/leo-editor/leo-editor/releases) and [pypi](https://pypi.org/project/leo/).

Leo is an [outline-oriented text editor](https://leo-editor.github.io/leo-editor/preface.html).

**The highlights of Leo 6.9.0**

- Remove an long-standing confusion about what backspaces mean in find strings::

  - Non-regex finds treat backspaces as normal characters.
  - Regex finds treat backspaces as escape characters.

- Add the ``promote-to-at-others``, ``promote-section-def`` and ``ty`` commands.

- Improve the ``next-line`` and ``prev-line`` commands.

- Improve the Rust importer.

Codebase changes

- Convert all of Leo's codebase to a new, much simpler undo API.
  This is a **breaking change** for any undoable script or plugin.

- Complete the transition from Python-based checkers (black, pyflakes, pylint)
  to Rust-based checkers (ruff format, ruff lint, ty).
  These changes affected annotations and suppressions throughout Leo's code base.

- Drop support for Python 3.10. Add support for Python 3.14.

- The usual bug fixes.

**Links**

- [Install Leo](https://leo-editor.github.io/leo-editor/installing.html)
- [6.9.0 Issues](https://github.com/leo-editor/leo-editor/issues?q=is%3Aissue+milestone%3A6.9.0+)
- [6.9.0 Pull Requests](https://github.com/leo-editor/leo-editor/pulls?q=is%3Apr+milestone%3A6.9.0)
- [Documentation](https://leo-editor.github.io/leo-editor/leo_toc.html)
- [Tutorials](https://leo-editor.github.io/leo-editor/tutorial.html)
- [Video tutorials](https://leo-editor.github.io/leo-editor/screencasts.html)
- [Forum](https://groups.google.com/group/leo-editor)
- [Leo on GitHub](https://github.com/leo-editor/leo-editor)
- [LeoVue](https://github.com/kaleguy/leovue#leo-vue)
- [What people are saying about Leo](https://leo-editor.github.io/leo-editor/testimonials.html)
- [More links](https://leo-editor.github.io/leo-editor/leoLinks.html)
