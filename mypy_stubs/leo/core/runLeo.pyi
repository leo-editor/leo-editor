from leo.core import leoApp as leoApp
from typing import Any

path: Any
msg: str

def profile_leo() -> None: ...
prof = profile_leo

def run(fileName: Any | None = ..., pymacs: Any | None = ..., *args, **keywords) -> None: ...
def run_console(*args, **keywords) -> None: ...
