from typing import Any

at_s: str
ref1_s: str
ref2_s: str

class TipManager:
    key: str
    def get_next_tip(self): ...

class UserTip:
    n: Any
    tags: Any
    title: Any
    text: Any
    def __init__(self, n: int = ..., tags: Any | None = ..., text: str = ..., title: str = ...) -> None: ...

def make_tips(c): ...
def make_tip_nodes(c) -> None: ...

tips: Any
