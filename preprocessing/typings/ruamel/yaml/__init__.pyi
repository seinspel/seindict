from pathlib import Path
from typing import Any, Literal

from .compat import StreamTextType

class YAML:
    def __init__(
        self, *, typ: Literal["safe", "unsafe", "base"] | None = ..., pure: bool = ...
    ) -> None: ...

    def load(self, stream: Path | StreamTextType) -> Any: ...
