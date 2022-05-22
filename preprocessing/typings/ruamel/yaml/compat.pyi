import io
from typing import BinaryIO, IO, Text, TypeAlias

StreamType: TypeAlias = BinaryIO | IO[str] | io.StringIO
StreamTextType: TypeAlias = Text | StreamType
