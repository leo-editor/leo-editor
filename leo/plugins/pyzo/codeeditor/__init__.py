# -*- coding: utf-8 -*-
# flake8: noqa
""" CodeEditor
A full featured code editor component based on QPlainTextEdit.
"""
try:
    import leo.core.leoGlobals as leo_g
    # leo_g.pr('IMPORT pyzo.codeeditor')
except Exception:
    leo_g = None
from .manager import Manager
from .base import CodeEditorBase

from .extensions.appearance import (
    HighlightMatchingBracket,
    HighlightMatchingOccurrences,
    HighlightCurrentLine,
    FullUnderlines,
    IndentationGuides,
    CodeFolding,
    LongLineIndicator,
    ShowWhitespace,
    ShowLineEndings,
    Wrap,
    LineNumbers,
    SyntaxHighlighting,
    BreakPoints,
)
from .extensions.behaviour import (
    Indentation,
    HomeKey,
    EndKey,
    NumpadPeriodKey,
    AutoIndent,
    PythonAutoIndent,
    SmartCopyAndPaste,
    MoveLinesUpDown,
    ScrollWithUpDownKeys,
    AutoCloseQuotesAndBrackets,
)
from .extensions.autocompletion import AutoCompletion
from .extensions.calltip import Calltip

# Order of superclasses: first the extensions, then CodeEditorBase
# The first superclass is the first extension that gets to handle each key and
# the first to receive paint events.

class CodeEditor( # tag:CodeEditor
    HighlightCurrentLine,
    HighlightMatchingOccurrences,
    HighlightMatchingBracket,
    FullUnderlines,
    IndentationGuides,
    CodeFolding,
    LongLineIndicator,
    ShowWhitespace,
    ShowLineEndings,
    Wrap,
    BreakPoints,
    LineNumbers,

    AutoCompletion, #Escape: first remove autocompletion,
    Calltip,               #then calltip

    Indentation,
    MoveLinesUpDown,
    ScrollWithUpDownKeys,
    HomeKey,
    EndKey,
    NumpadPeriodKey,

    AutoIndent,
    PythonAutoIndent,
    AutoCloseQuotesAndBrackets,
    SyntaxHighlighting,

    SmartCopyAndPaste, # overrides cut(), copy(), paste()

    CodeEditorBase, #CodeEditorBase must be the last one in the list

    ):
    """
    CodeEditor with all the extensions
    """
    pass
