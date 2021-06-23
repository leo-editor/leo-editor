from leo.core import leoserver as leoserver
from typing import Any

wsHost: str
wsPort: int
tag: str
timeout: float
times_d: Any
tot_response_time: float
n_known_response_times: int
n_unknown_response_times: int
n_async_responses: int

async def client_main_loop(timeout) -> None: ...
def main() -> None: ...
