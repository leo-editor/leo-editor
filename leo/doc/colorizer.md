# About Leo's colorizer code
The JEditColorizer class adapts jEdit pattern matchers for QSyntaxHighlighter.

The line-oriented jEdit colorizer defines one or more *restarter* methods for each pattern matcher that could possibly match across line boundaries. The colorizer uses a separate restarter method for all combinations of arguments that can be passed to the jEdit pattern matchers. Restarters freeze bindings for the generic restarter methods.

Few restarters are actually needed. The Python colorizers defines restarters for continued strings, and both flavors of continued triple-quoted strings. For Python, these are separate bindings of the arguments to restart_match_span.

When a jEdit pattern matcher partially succeeds, it creates a binding for its restarter and calls setRestart. setRestart calls computeState to create a *string* representing the lambda binding of the restarter. setRestart then calls stateNameToStateNumber to convert that string to an integer state number that then gets passed to Qt's setCurrentBlockState. The string is useful for debugging; Qt only uses the corresponding number.

