#!/usr/bin/env python
"""
Spike / proof-of-concept LSP client for issue #4871.

https://github.com/leo-editor/leo-editor/issues/4871

Goal of the spike: prove that a *generic* LSP client (any conforming
server, not a jedi-shaped API) can drive Leo's body-pane completions,
reusing the existing jedi position-mapping logic in
leoKeys.py::AutoCompleterClass.get_jedi_completions.

This is deliberately minimal and NOT production code:

- Synchronous request/response (blocks the caller while waiting for
  the server). The real implementation described in #4871 would need
  an async round trip with a callback, since cold-start indexing can
  be slow.
- No process crash/restart handling.
- No per-@language server selection (`@data language-servers`):
  the caller passes the server command explicitly.
- Diagnostics are collected but nothing in Leo consumes them yet;
  they're exposed on LspClient.diagnostics for a future body-pane
  squiggly-underline feature to read.

Protocol notes discovered while spiking against `ty server` (Astral's
Python language server, `pip install ty`):

- Completion requests need an *absolute* `file://` URI. A relative
  path is treated as an opaque URI and diagnostics/completions for it
  silently fail.
- `ty` only returns completions -- member or otherwise -- when there is
  no text after the cursor on that physical line. `self.` at true
  end-of-line returns members; the identical position with real code
  continuing after the cursor on the same line (e.g. mid-edit of an
  existing statement) returns nothing, even one character further in.
  Worked around with a "phantom EOL": `get_lsp_completions` sends a copy
  of the source with just the cursor's line truncated at the cursor, so
  the server always sees end-of-line there (confirmed this restores
  mid-line completions). The untruncated source is unaffected -- the
  truncated copy exists only for that one completion request.
  `ty` *does* do server-side prefix filtering once positioned correctly
  (`self.f` at end-of-line returns only names starting with `f`), so no
  client-side re-implementation of that part was needed.
"""

from __future__ import annotations
import json
import os
import subprocess
import threading
import time
from typing import Any


class LspClient:
    """A blocking client for one LSP server subprocess."""

    def __init__(self, command: list[str], root_path: str) -> None:
        self.command = command
        self.root_path = root_path
        self.proc: subprocess.Popen | None = None
        self.diagnostics: dict[str, list[dict]] = {}  # uri -> latest diagnostics.
        self._id = 0
        self._lock = threading.Lock()
        self._pending: dict[int, dict] = {}
        self._doc_versions: dict[str, int] = {}
        self._started = False

    def start(self, timeout: float = 10.0) -> None:
        """Spawn the server and perform the initialize/initialized handshake."""
        if self._started:
            return
        self._started = True
        self.proc = subprocess.Popen(
            self.command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        threading.Thread(target=self._read_loop, daemon=True).start()
        self.request(
            'initialize',
            {
                'processId': os.getpid(),
                'rootUri': 'file://' + self.root_path,
                'capabilities': {
                    'textDocument': {
                        'completion': {'completionItem': {'snippetSupport': False}},
                        'publishDiagnostics': {},
                    },
                },
            },
            timeout=timeout,
        )
        self.notify('initialized', {})

    def _read_loop(self) -> None:
        """Runs in a daemon thread: demux responses (by id) from notifications."""
        stdout = self.proc.stdout
        buf = b''
        while True:
            chunk = stdout.read(1)
            if not chunk:
                break
            buf += chunk
            if not buf.endswith(b'\r\n\r\n'):
                continue
            length = 0
            for header in buf.decode('ascii', errors='replace').split('\r\n'):
                if header.lower().startswith('content-length'):
                    length = int(header.split(':', 1)[1].strip())
            buf = b''
            body = stdout.read(length)
            try:
                msg = json.loads(body)
            except ValueError:
                continue
            if 'id' in msg and ('result' in msg or 'error' in msg):
                with self._lock:
                    self._pending[msg['id']] = msg
            elif msg.get('method') == 'textDocument/publishDiagnostics':
                params = msg.get('params', {})
                self.diagnostics[params.get('uri', '')] = params.get('diagnostics', [])

    def _send(self, payload: dict) -> None:
        data = json.dumps(payload).encode('utf-8')
        header = f"Content-Length: {len(data)}\r\n\r\n".encode('ascii')
        self.proc.stdin.write(header + data)
        self.proc.stdin.flush()

    def request(self, method: str, params: Any, timeout: float = 10.0) -> dict:
        """Send a request and block until the matching response arrives."""
        with self._lock:
            self._id += 1
            msg_id = self._id
        self._send({'jsonrpc': '2.0', 'id': msg_id, 'method': method, 'params': params})
        deadline = time.time() + timeout
        while time.time() < deadline:
            with self._lock:
                if msg_id in self._pending:
                    return self._pending.pop(msg_id)
            time.sleep(0.01)
        raise TimeoutError(f"leo_lsp_client: no response to {method!r}")

    def notify(self, method: str, params: Any) -> None:
        self._send({'jsonrpc': '2.0', 'method': method, 'params': params})

    def sync_document(self, uri: str, text: str, language_id: str = 'python') -> None:
        """didOpen the first time a uri is seen, full-text didChange after."""
        version = self._doc_versions.get(uri)
        if version is None:
            self._doc_versions[uri] = 1
            self.notify(
                'textDocument/didOpen',
                {
                    'textDocument': {
                        'uri': uri,
                        'languageId': language_id,
                        'version': 1,
                        'text': text,
                    },
                },
            )
        else:
            version += 1
            self._doc_versions[uri] = version
            self.notify(
                'textDocument/didChange',
                {
                    'textDocument': {'uri': uri, 'version': version},
                    'contentChanges': [{'text': text}],
                },
            )

    def completions(self, uri: str, line: int, character: int, timeout: float = 5.0) -> list[dict]:
        """Return raw LSP CompletionItem dicts at the given 0-based position."""
        try:
            response = self.request(
                'textDocument/completion',
                {
                    'textDocument': {'uri': uri},
                    'position': {'line': line, 'character': character},
                    'context': {'triggerKind': 1},
                },
                timeout=timeout,
            )
        except TimeoutError:
            return []
        if 'error' in response:
            return []
        result = response.get('result')
        if result is None:
            return []
        items = result.get('items', []) if isinstance(result, dict) else result
        return items or []

    def shutdown(self) -> None:
        if not self._started or self.proc is None:
            return
        try:
            self.request('shutdown', None, timeout=2)
            self.notify('exit', None)
        except Exception:
            pass
        try:
            self.proc.terminate()
        except Exception:
            pass


# One client per (command, root_path), kept alive for the process lifetime.
# Matches the "spawn once per session" note in #4871; there's no eviction,
# which is fine for a spike but would need addressing for real use
# (closing Leo should shut these down; a long session with many
# different @file roots would otherwise accumulate server processes).
_clients: dict[str, LspClient] = {}


def get_client(command: list[str], root_path: str) -> LspClient:
    """Return the (lazily started) LspClient for this server command + root."""
    key = f"{' '.join(command)}::{root_path}"
    client = _clients.get(key)
    if client is None:
        client = LspClient(command, root_path)
        client.start()
        _clients[key] = client
    return client
