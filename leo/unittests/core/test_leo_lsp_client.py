"""Tests for leo.external.leo_lsp_client."""

from pathlib import Path

from leo.external import leo_lsp_client


def test_path_to_uri_uses_canonical_file_uri() -> None:
    path = Path.cwd() / 'leo' / 'core' / 'leoKeys.py'
    uri = leo_lsp_client.path_to_uri(str(path))

    assert uri == path.resolve().as_uri()
    assert '\\' not in uri
