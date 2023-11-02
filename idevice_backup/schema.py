from datetime import datetime
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field, RootModel


class Snapshot(BaseModel):
    id: str
    short_id: str
    time: datetime
    tree: str
    paths: List[Path]
    hostname: str
    username: str
    uid: int
    gid: int

    def __str__(self) -> str:
        return f"{self.short_id} ({self.time})"


Snapshots = RootModel[list[Snapshot]]


class File(BaseModel):
    name: str
    file_type: str = Field(alias="type")
    path: Path
    uid: int
    gid: int
    size: int | None = None
    mode: int
    permissions: str
    mtime: datetime
    atime: datetime
    ctime: datetime

    def __str__(self) -> str:
        return f"[{self.file_type}] {self.name} ({self.path}): {self.size or '0'} bytes"

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, File)
            and self.path == other.path
            and self.size == other.size
            and self.mtime == other.mtime
        )
