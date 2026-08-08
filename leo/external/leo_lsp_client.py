#!/usr/bin/env python
"""
LSP client for issue #4871.

https://github.com/leo-editor/leo-editor/issues/4871

A *generic* LSP client (any conforming server, not a jedi-shaped API)
that drives Leo's body-pane completions and diagnostics, reusing the
existing jedi position-mapping logic in
leoKeys.py::AutoCompleterClass.get_jedi_completions.

Offers both a blocking API (start/request/completions -- for tests and
headless scripts) and a non-blocking one (start_async/request_async/
completions_async -- what leoKeys.py's GUI-facing code uses, since a
cold server's initial indexing can take seconds and must not freeze
Leo's event loop). See LspClient's class docstring.

Messages are built and parsed as typed `lsprotocol` objects, not raw
dicts: `lsprotocol.types.METHOD_TO_TYPES[method]` gives the
(RequestType, ResponseType, ParamsType, ...) for any LSP method, and
`lsprotocol.converters.get_converter()` handles snake_case-attrs <->
camelCase-JSON conversion in both directions. Callers pass/receive typed
params/results (e.g. types.CompletionParams, types.Diagnostic) --
`lsprotocol` is a mandatory dependency (see requirements.txt), not an
optional one, precisely so this client never has to fall back to
untyped dicts.

Remaining known gaps, not yet addressed:

- No per-@language server selection (`@data language-servers`):
  the caller passes the server command explicitly, so today's wiring
  in leoKeys.py is Python/`ty`-only in practice.
- Diagnostics only reach the body pane as a side effect of a completion
  request (get_lsp_completions calls show_lsp_diagnostics after every
  request, and LspClient.on_diagnostics pushes updates that arrive
  later for the same file). Nothing calls sync_document from a plain
  body edit that isn't also a completion trigger, so squigglies can
  lag behind typing that never invokes autocomplete.
- A crashed server is detected and replaced on next use (get_client),
  but there's no backoff -- a server that crashes on every request
  will be respawned every time, once per keystroke.

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
from collections.abc import Callable
import json
import os
import subprocess
import threading
import time
from pathlib import Path
from typing import Any
from lsprotocol import converters, types

_converter = converters.get_converter()


def path_to_uri(path: str) -> str:
    """Return a standards-compliant absolute file URI on every platform."""
    return Path(path).resolve().as_uri()


class LspClient:
    """A client for one LSP server subprocess.

    Offers both a blocking API (start/request/completions -- handy for
    tests and headless scripts) and a non-blocking one (start_async/
    request_async/completions_async -- what GUI callers must use, since
    cold-start indexing can take seconds and must not freeze the event
    loop; see #4871).

    request/request_async/notify are generic over any LSP method:
    `types.METHOD_TO_TYPES[method]` supplies the envelope classes
    (*Request/*Notification carry method+jsonrpc automatically), so
    adding a new LSP feature (hover, definition, rename, ...) needs no
    new plumbing here -- just call request_async(types.TEXT_DOCUMENT_HOVER,
    types.HoverParams(...), callback) from leoKeys.py.
    """

    def __init__(self, command: list[str], root_path: str) -> None:
        self.command = command
        self.root_path = root_path
        self.proc: subprocess.Popen | None = None
        self.diagnostics: dict[str, list[types.Diagnostic]] = {}  # uri -> latest diagnostics.
        # Called (from the reader thread -- see class docstring) as
        # on_diagnostics(uri, diagnostics) whenever the server pushes new
        # diagnostics. None means "nobody's listening".
        self.on_diagnostics: Callable[[str, list[types.Diagnostic]], None] | None = None
        self._id = 0
        self._lock = threading.Lock()
        self._write_lock = threading.Lock()  # Guards proc.stdin: writers may be on any thread.
        self._pending: dict[int, dict] = {}  # For the blocking request() API.
        self._callbacks: dict[int, Callable[[dict | None], None]] = {}  # For request_async().
        self._doc_versions: dict[str, int] = {}
        self._started = False
        self._start_lock = threading.Lock()
        self._start_thread: threading.Thread | None = None
        self._start_error: Exception | None = None
        self._ready = threading.Event()
        self._alive = True  # False once the server process/pipe is known dead.

    @property
    def is_ready(self) -> bool:
        """True once the initialize/initialized handshake has succeeded."""
        return self._ready.is_set() and self._start_error is None

    @property
    def is_alive(self) -> bool:
        """False once the reader thread has seen EOF on the server's stdout."""
        return self._alive

    @property
    def start_error(self) -> Exception | None:
        """The exception that failed the handshake, or None if it hasn't (yet) failed.

        None while a cold start is still in progress -- check is_ready
        first to tell "still starting" apart from "will never be ready"
        (e.g. the configured command doesn't exist). See get_client.
        """
        return self._start_error if self._ready.is_set() else None

    def start(self, timeout: float = 10.0) -> None:
        """Spawn the server and perform the initialize/initialized handshake.

        Blocks until the handshake completes (or raises TimeoutError).
        GUI callers must use start_async() instead -- see class docstring.
        """
        if self._started:
            return
        self._started = True
        try:
            # Popen itself (e.g. the configured command isn't on PATH) must
            # fail into the same _start_error/_ready bookkeeping as a
            # handshake failure below -- it used to be outside this
            # try/finally, so a bad command silently left is_ready False
            # forever with start_error still None, indistinguishable from
            # "still cold-starting" (#4871 follow-up).
            self.proc = subprocess.Popen(
                self.command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                cwd=self.root_path,  # See root_uri/workspace_folders note below.
            )
            threading.Thread(target=self._read_loop, daemon=True).start()
            self.request(
                types.INITIALIZE,
                types.InitializeParams(
                    process_id=os.getpid(),
                    root_uri=path_to_uri(self.root_path),
                    # `ty server` (confirmed by testing, and by its own
                    # startup log line) ignores the deprecated root_uri
                    # for workspace discovery and needs workspace_folders
                    # instead -- without it, it silently falls back to its
                    # own process cwd, which is *not* root_path unless
                    # cwd= above also pins it there as a backstop for
                    # servers that only look at cwd. With neither set
                    # correctly, diagnostics silently never fire (no
                    # error -- publishDiagnostics just always reports zero
                    # diagnostics for every document).
                    workspace_folders=[
                        types.WorkspaceFolder(
                            uri=path_to_uri(self.root_path),
                            name=os.path.basename(self.root_path) or self.root_path,
                        ),
                    ],
                    capabilities=types.ClientCapabilities(
                        text_document=types.TextDocumentClientCapabilities(
                            completion=types.CompletionClientCapabilities(
                                completion_item=types.ClientCompletionItemOptions(
                                    snippet_support=False
                                ),
                            ),
                            hover=types.HoverClientCapabilities(
                                content_format=[types.MarkupKind.PlainText, types.MarkupKind.Markdown],
                            ),
                            publish_diagnostics=types.PublishDiagnosticsClientCapabilities(),
                        ),
                    ),
                ),
                timeout=timeout,
            )
            self.notify(types.INITIALIZED, types.InitializedParams())
        except Exception as e:
            self._start_error = e
            raise
        finally:
            self._ready.set()

    def start_async(self) -> None:
        """Non-blocking start(): runs the handshake on a background thread.

        Safe to call repeatedly / concurrently -- only the first call
        actually spawns anything. Check is_ready before sending requests;
        an unready client is expected for the first keystroke or two after
        Leo starts and self-heals once the handshake finishes.
        """
        with self._start_lock:
            if self._started or self._start_thread is not None:
                return

            def run() -> None:
                try:
                    self.start()
                except Exception:
                    pass  # self._start_error / is_ready already reflects this.

            self._start_thread = threading.Thread(target=run, daemon=True)
            self._start_thread.start()

    def _read_loop(self) -> None:
        """Runs in a daemon thread: demux responses (by id) from notifications.

        Exits (and flips is_alive to False) on EOF -- i.e. when the server
        process dies or closes its stdout. Callers find out via is_alive,
        not an exception, since this thread has no caller to raise to.
        """
        stdout = self.proc.stdout
        buf = b''
        try:
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
                        callback = self._callbacks.pop(msg['id'], None)
                        if callback is None:
                            self._pending[msg['id']] = msg
                    # Call outside the lock: callback may itself call back
                    # into this client (e.g. sync_document), which must not
                    # deadlock on self._lock.
                    if callback is not None:
                        callback(msg)
                elif msg.get('method') == types.TEXT_DOCUMENT_PUBLISH_DIAGNOSTICS:
                    diagnostics = self._structure_diagnostics(msg.get('params', {}))
                    if diagnostics is not None:
                        uri, items = diagnostics
                        self.diagnostics[uri] = items
                        if self.on_diagnostics is not None:
                            self.on_diagnostics(uri, items)
        finally:
            self._alive = False

    def _structure_diagnostics(self, raw_params: dict) -> tuple[str, list[types.Diagnostic]] | None:
        """Structure a raw publishDiagnostics params dict, or None if malformed."""
        try:
            params = _converter.structure(raw_params, types.PublishDiagnosticsParams)
        except Exception:
            return None
        return params.uri, list(params.diagnostics)

    def _send(self, payload: dict) -> None:
        data = json.dumps(payload).encode('utf-8')
        header = f"Content-Length: {len(data)}\r\n\r\n".encode('ascii')
        # request_async's caller (often the GUI thread) and a completion
        # callback running on the reader thread (see get_lsp_completions'
        # restore-real-source step) can both write concurrently.
        with self._write_lock:
            self.proc.stdin.write(header + data)
            self.proc.stdin.flush()

    def _next_id(self) -> int:
        with self._lock:
            self._id += 1
            return self._id

    def _build_request(self, method: str, params: Any, msg_id: int) -> Any:
        request_cls = types.METHOD_TO_TYPES[method][0]
        return (
            request_cls(id=msg_id, params=params) if params is not None else request_cls(id=msg_id)
        )

    @staticmethod
    def _structure_result(msg: dict, response_cls: Any) -> Any:
        """Return msg's typed `.result`, falling back to the raw dict/list
        value on a structuring failure.

        A server is free to advertise capabilities or return fields
        lsprotocol's generated converter doesn't fully handle (seen in
        practice: `ty server`'s `notebookDocumentSync` capability, in a
        part of InitializeResult Leo never reads) without that being a
        real protocol error for *our* purposes -- we only ever consume a
        handful of fields, so degrade to "here's the raw value" instead
        of discarding a response that otherwise arrived successfully.
        """
        if response_cls is None:
            return msg.get('result')
        try:
            return _converter.structure(msg, response_cls).result
        except Exception:
            return msg.get('result')

    def request(self, method: str, params: Any = None, timeout: float = 10.0) -> Any:
        """Send a request and block until the matching response arrives.

        Returns the response's typed `.result` where that structures
        cleanly (see _structure_result), the raw result otherwise, or
        raises TimeoutError / the server's reported error.
        """
        msg_id = self._next_id()
        self._send(_converter.unstructure(self._build_request(method, params, msg_id)))
        deadline = time.time() + timeout
        while time.time() < deadline:
            with self._lock:
                if msg_id in self._pending:
                    msg = self._pending.pop(msg_id)
                    break
            time.sleep(0.01)
        else:
            raise TimeoutError(f"leo_lsp_client: no response to {method!r}")
        if 'error' in msg:
            raise RuntimeError(f"leo_lsp_client: {method} failed: {msg['error']}")
        return self._structure_result(msg, types.METHOD_TO_TYPES[method][1])

    def request_async(
        self,
        method: str,
        params: Any,
        callback: Callable[[Any], None],
        timeout: float = 5.0,
    ) -> None:
        """Send a typed request without blocking.

        `params` is the lsprotocol params object appropriate for `method`
        (e.g. types.CompletionParams for 'textDocument/completion'), or
        None for params-less requests. callback(result) fires exactly
        once, later, with the response's typed `.result` (see
        _structure_result) -- or None on error/timeout. It never runs on
        the calling thread. Callers must not touch GUI widgets from
        callback -- hop to the GUI thread first (see leoKeys._LspBridge
        for the pattern this codebase uses).
        """
        msg_id = self._next_id()
        response_cls = types.METHOD_TO_TYPES[method][1]

        def deliver(raw_msg: dict | None) -> None:
            if raw_msg is None or 'error' in raw_msg:
                callback(None)
                return
            callback(self._structure_result(raw_msg, response_cls))

        with self._lock:
            self._callbacks[msg_id] = deliver
        self._send(_converter.unstructure(self._build_request(method, params, msg_id)))

        def on_timeout() -> None:
            with self._lock:
                cb = self._callbacks.pop(msg_id, None)
            if cb is not None:
                cb(None)

        timer = threading.Timer(timeout, on_timeout)
        timer.daemon = True
        timer.start()

    def notify(self, method: str, params: Any = None) -> None:
        notification_cls = types.METHOD_TO_TYPES[method][0]
        notification = notification_cls(params=params) if params is not None else notification_cls()
        self._send(_converter.unstructure(notification))

    def sync_document(self, uri: str, text: str, language_id: str = 'python') -> None:
        """didOpen the first time a uri is seen, full-text didChange after.

        May be called from more than one thread for the same uri (the GUI
        thread starting a new request while an earlier request's async
        callback is still restoring the previous document) -- the version
        counter is locked so those calls can't race each other.
        """
        with self._lock:
            version = self._doc_versions.get(uri)
            if version is None:
                self._doc_versions[uri] = version = 1
                is_open = False
            else:
                version += 1
                self._doc_versions[uri] = version
                is_open = True
        if not is_open:
            self.notify(
                types.TEXT_DOCUMENT_DID_OPEN,
                types.DidOpenTextDocumentParams(
                    text_document=types.TextDocumentItem(
                        uri=uri, language_id=language_id, version=1, text=text
                    ),
                ),
            )
        else:
            self.notify(
                types.TEXT_DOCUMENT_DID_CHANGE,
                types.DidChangeTextDocumentParams(
                    text_document=types.VersionedTextDocumentIdentifier(uri=uri, version=version),
                    content_changes=[types.TextDocumentContentChangeWholeDocument(text=text)],
                ),
            )

    @staticmethod
    def _completion_items(
        result: types.CompletionList | list[types.CompletionItem] | None,
    ) -> list[types.CompletionItem]:
        if result is None:
            return []
        items = result.items if isinstance(result, types.CompletionList) else result
        return list(items or [])

    def completions(
        self, uri: str, line: int, character: int, timeout: float = 5.0
    ) -> list[types.CompletionItem]:
        """Return typed CompletionItems at the given 0-based position.

        Blocks. GUI callers must use completions_async instead.
        """
        try:
            result = self.request(
                types.TEXT_DOCUMENT_COMPLETION,
                types.CompletionParams(
                    text_document=types.TextDocumentIdentifier(uri=uri),
                    position=types.Position(line=line, character=character),
                    context=types.CompletionContext(
                        trigger_kind=types.CompletionTriggerKind.Invoked
                    ),
                ),
                timeout=timeout,
            )
        except (TimeoutError, RuntimeError):
            return []
        return self._completion_items(result)

    def completions_async(
        self,
        uri: str,
        line: int,
        character: int,
        callback: Callable[[list[types.CompletionItem]], None],
        timeout: float = 5.0,
    ) -> None:
        """Non-blocking counterpart to completions().

        callback(items) fires later with a (possibly empty) list of typed
        CompletionItems; empty on error or timeout. See request_async for
        the threading contract.
        """
        self.request_async(
            types.TEXT_DOCUMENT_COMPLETION,
            types.CompletionParams(
                text_document=types.TextDocumentIdentifier(uri=uri),
                position=types.Position(line=line, character=character),
                context=types.CompletionContext(trigger_kind=types.CompletionTriggerKind.Invoked),
            ),
            lambda result: callback(self._completion_items(result)),
            timeout=timeout,
        )

    def hover(self, uri: str, line: int, character: int, timeout: float = 2.0) -> str:
        """Return plain hover text at the given 0-based position.

        Blocks, with a short default timeout: the Qt tooltip event that
        drives this (see qt_text.py's LeoQTextBrowser.eventFilter) needs
        an immediate string to display, so there's no async variant.
        """
        try:
            result = self.request(
                types.TEXT_DOCUMENT_HOVER,
                types.HoverParams(
                    text_document=types.TextDocumentIdentifier(uri=uri),
                    position=types.Position(line=line, character=character),
                ),
                timeout=timeout,
            )
        except (TimeoutError, RuntimeError):
            return ''
        if result is None:
            return ''
        # result.contents is typed (MarkupContent | str |
        # MarkedStringWithLanguage | Sequence[...]) when it structures
        # cleanly; _structure_result falls back to the raw dict/list
        # otherwise (see its docstring), so handle both shapes.
        contents = result.contents if isinstance(result, types.Hover) else result.get('contents', '')
        text = self._hover_text(contents)
        # LSP markdown commonly wraps type signatures in a fenced code block.
        lines = text.splitlines()
        if lines and lines[0].startswith('```'):
            lines = lines[1:]
        if lines and lines[-1] == '```':
            lines = lines[:-1]
        return '\n'.join(lines).strip()

    @staticmethod
    def _hover_text(contents: Any) -> str:
        """Flatten a Hover.contents value (typed or raw-dict fallback) to plain text."""
        if isinstance(contents, str):
            return contents
        if isinstance(contents, (types.MarkupContent, types.MarkedStringWithLanguage)):
            return contents.value
        if isinstance(contents, dict):
            return contents.get('value', '')
        if isinstance(contents, (list, tuple)):
            parts = [LspClient._hover_text(z) for z in contents]
            return '\n\n'.join(z for z in parts if z)
        return ''

    def shutdown(self) -> None:
        self._alive = False
        if not self._started or self.proc is None:
            return
        try:
            self.request(types.SHUTDOWN, timeout=2)
            self.notify(types.EXIT)
        except Exception:
            pass
        try:
            self.proc.terminate()
        except Exception:
            pass


# One client per (command, root_path), kept alive for the process lifetime
# (or until it's found dead -- see get_client) and terminated for good by
# shutdown_all(), which leoApp.finishQuit calls so `ty server` and friends
# don't outlive the Leo process (#4871).
_clients: dict[str, LspClient] = {}


def get_client(command: list[str], root_path: str) -> LspClient:
    """Return the (lazily started) LspClient for this server command + root.

    Starts the handshake asynchronously: a cold server can take a few
    seconds to index a project, and callers on the GUI thread must not
    block on that. Check client.is_ready before sending requests -- an
    unready client is expected right after Leo starts or right after a
    crashed server is replaced, and self-heals within a keystroke or two.

    A client whose reader thread has seen EOF (is_alive False -- the
    server crashed or was killed) is discarded and replaced on the next
    call, rather than staying permanently wedged returning nothing.
    """
    key = f"{' '.join(command)}::{root_path}"
    client = _clients.get(key)
    if client is not None and not client.is_alive:
        client.shutdown()
        del _clients[key]
        client = None
    if client is None:
        client = LspClient(command, root_path)
        client.start_async()
        _clients[key] = client
    return client


def shutdown_all() -> None:
    """Terminate every LSP server process spawned this session.

    leoApp.finishQuit calls this explicitly: leo_lsp_client has no other
    connection to app shutdown, and without it every `ty server` (or
    whatever @string lsp-command names) spawned during the session would
    outlive the Leo process.
    """
    for client in list(_clients.values()):
        client.shutdown()
    _clients.clear()
