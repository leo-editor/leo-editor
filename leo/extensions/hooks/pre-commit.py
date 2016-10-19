#!/usr/bin/env python

# Move this file to leo-editor/.git/hooks/pre-commit.
# The file must be named pre-commit, NOT pre-commit.py

# pylint: disable=invalid-name

# print('===== pre-commit ====')
import leo.core.leoVersion as v
v.create_commit_timestamp_json(after=True)
