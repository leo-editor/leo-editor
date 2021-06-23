from leo.core import leoBridge as leoBridge
from typing import Any

cwd: Any
g_trace: bool
trace_argv: bool
trace_main: bool
trace_time: bool

def main() -> None: ...
def runUnitTests(c, g) -> None: ...
def scanOptions(): ...
