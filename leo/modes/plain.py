# Leo colorizer control file for plain mode.
# This file is in the public domain.

# Properties for plain mode.
properties = {}

# Attributes dict for plain_main ruleset.
plain_main_attributes_dict = {
    "default": "null",
    "digit_re": "",
    "escape": "\\",
    "highlight_digits": "false",
    "ignore_case": "true",
    "no_word_sep": "",
}

# Dictionary of attributes dictionaries for plain mode.
attributesDictDict = {
    "plain_main": plain_main_attributes_dict,
}

# Keywords dict for plain_main ruleset.
plain_main_keywords_dict = {}

# Dictionary of keywords dictionaries for plain mode.
keywordsDictDict = {
    "plain_main": plain_main_keywords_dict,
}

# Rules for plain_main ruleset.

# Rules dict for plain_main ruleset.
if 1:
    def plain_rule0(colorer, s, i):
        # print('plain_rule0',s[i:i+10])
        return colorer.match_eol_span(s, i, kind="null")

    # Simulate a dict that returns [plain_rule0] by default.
    class RulesDict:
        def __init__(self):
            self.d = {}
        def get(self, ch, default_val):
            return self.d.get(ch) or [plain_rule0]
        def __setitem__(self, key, item):
            self.d[key] = item

    rulesDict1 = RulesDict()

else:
    rulesDict1 = {}

# x.rulesDictDict for plain mode.
rulesDictDict = {
    "plain_main": rulesDict1,
}

# Import dict for plain mode.
importDict = {}
