echo off
cd c:\Repos\leo-editor
python -m unittest ^
    leo.unittests.core.test_leoAtFile.TestFastAtRead.test_doc_parts ^
    leo.unittests.core.test_leoAtFile.TestFastAtRead.test_html_doc_part ^
    leo.unittests.core.test_leoAtFile.TestFastAtRead.test_verbatim ^
    leo.unittests.core.test_leoAst.TestOrange.test_verbatim ^
    %*
