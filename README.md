Leo https://leo-editor.github.io/leo-editor/ 6.7.4 is now available on [GitHub](https://github.com/leo-editor/leo-editor/releases) and [pypi](https://pypi.org/project/leo/).

Leo is an [IDE, outliner and PIM](https://leo-editor.github.io/leo-editor/preface.html).

**The highlights of Leo 6.7.4**

**Warning: breaking changes to Leo's api**

p.get_UNL returns gnx-based unls. Previously it returned path-based gnxs.
See the first comment of PR #3424 for full details.

**gnx-based unls**

- PR #3215 and #3424: gnx-based unls (clickable links).
  These links will break only if the original node is deleted.
  
**New settings**
  
- @string unl-status-kind = gnx
- @bool full-unl-paths = True
- @data unl-path-prefixes
  
**Other improvements**
  
- PR #3330: Improve importers for C, C++, and cython.
- PR #3345: Improve importer architecture.
- PR #3363 & #3379: Improve c.recursiveImport.
- PR #3376: Improve python importer.

**Large code changes**

- PR #3365: Simplify mypy annotations (128 files).
- PR #3367: Import Callable from collections.abc instead of typing (50 files).

**Retire three plugins**

- PR #3215: Retire the settings_finder, backlink, and quickMove plugins.

- 50+ issues and 70+ pull requests.

**Links**

- [Download Leo](https://leo-editor.github.io/leo-editor/download.html)
- [Install Leo](https://leo-editor.github.io/leo-editor/installing.html)
- [6.7.4 Issues](https://github.com/leo-editor/leo-editor/issues?q=is%3Aissue+milestone%3A6.7.4+)
- [6.7.4 Pull Requests](https://github.com/leo-editor/leo-editor/pulls?q=is%3Apr+milestone%3A6.7.4)
- [Documentation](https://leo-editor.github.io/leo-editor/leo_toc.html)
- [Tutorials](https://leo-editor.github.io/leo-editor/tutorial.html)
- [Video tutorials](https://leo-editor.github.io/leo-editor/screencasts.html)
- [Forum](http://groups.google.com/group/leo-editor)
- [Download](http://sourceforge.net/projects/leo/files/)
- [Leo on GitHub](https://github.com/leo-editor/leo-editor)
- [LeoVue](https://github.com/kaleguy/leovue#leo-vue)
- [What people are saying about Leo](https://leo-editor.github.io/leo-editor/testimonials.html)
- [A web page that displays .leo files](https://leo-editor.github.io/leo-editor/load-leo.html)
- [More links](https://leo-editor.github.io/leo-editor/leoLinks.html)
