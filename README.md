Leo https://leo-editor.github.io/leo-editor/ 6.8.4 is now available on [GitHub](https://github.com/leo-editor/leo-editor/releases) and [pypi](https://pypi.org/project/leo/).

Leo is an [IDE, outliner and PIM](https://leo-editor.github.io/leo-editor/preface.html).

**The highlights of Leo 6.8.4**

- Improve the Rust importer.
- Allow rest comments to be colored differently from @language rest.
- Support `@language typst`.
- Several other improvements to syntax coloring.
- Add the `show-buttons-and-at-commands` command.
- Add the `find-source-for-command` command.
- Add the `beautify-script` command.
- The `execute-script` command beautifies `c.p`'s tree if
  `@bool beautify-python-code-on-write = True`.
- Remove the join-leo-irc command.
- Scripts (including `@command` and `@button` scripts) may now return a value.
- Replace `c.scanAllDirectives` with 7 seven new Commands getters.
- Deprecate `c.scanAllDirectives` and 17 other directives-related functions.
- Call `g.deprecated` in all deprecated functions to issue a deprecation warning.
- Several significant code cleanups.
- The usual minor bug fixes.

**Breaking change**

- Syntax coloring for @language rest may require a new setting in myLeoSettings.leo.
  See the `What's new in Leo 6.8.4` for details.

**Links**

- [Install Leo](https://leo-editor.github.io/leo-editor/installing.html)
- [6.8.4 Issues](https://github.com/leo-editor/leo-editor/issues?q=is%3Aissue+milestone%3A6.8.4+)
- [6.8.4 Pull Requests](https://github.com/leo-editor/leo-editor/pulls?q=is%3Apr+milestone%3A6.8.4)
- [Documentation](https://leo-editor.github.io/leo-editor/leo_toc.html)
- [Tutorials](https://leo-editor.github.io/leo-editor/tutorial.html)
- [Video tutorials](https://leo-editor.github.io/leo-editor/screencasts.html)
- [Forum](https://groups.google.com/group/leo-editor)
- [Leo on GitHub](https://github.com/leo-editor/leo-editor)
- [LeoVue](https://github.com/kaleguy/leovue#leo-vue)
- [What people are saying about Leo](https://leo-editor.github.io/leo-editor/testimonials.html)
- [More links](https://leo-editor.github.io/leo-editor/leoLinks.html)
