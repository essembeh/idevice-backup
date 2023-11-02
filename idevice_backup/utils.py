from pathlib import Path
from typing import Iterable, Iterator

import arrow
from colorama import Fore, Style

from .restic import Restic
from .schema import File, Snapshot


def label(item):
    """
    return a str with colors of the given object
    """
    if isinstance(item, Restic):
        return f"🔐 {label(item.repository)}"
    if isinstance(item, Path):
        if not item.exists():
            return str(item)
        if item.is_dir():
            return f"{Fore.BLUE}{Style.BRIGHT}{item}/{Style.RESET_ALL}"
        return f"{Style.BRIGHT}{Fore.BLUE}{item.parent}/{Fore.MAGENTA}{item.name}{Style.RESET_ALL}"
    if isinstance(item, File):
        if item.file_type == "dir":
            return f"{Fore.BLUE}{Style.BRIGHT}{item.path}/{Style.RESET_ALL}"
        color = Fore.MAGENTA
        if item.file_type == "symlink":
            color = Fore.CYAN
        elif "x" in item.permissions:
            color = Fore.GREEN
        return f"{Style.BRIGHT}{Fore.BLUE}{item.path.parent}/{color}{item.path.name}{Style.RESET_ALL}"
    if isinstance(item, Snapshot):
        return (
            f"📦 [{Fore.YELLOW}{item.hostname}{Style.RESET_ALL}] "
            + f"{Style.BRIGHT}{Fore.CYAN}{item.short_id}{Style.RESET_ALL} "
            + f"{Style.DIM}({arrow.get(item.time).humanize()}){Style.RESET_ALL}"
        )

    return str(item) if item is not None else ""


def iter_different_files(
    previous_files: Iterator[File],
    current_files: Iterator[File],
    only_types: Iterable[str] | None = None,
) -> Iterator[tuple[File | None, File | None]]:
    cache = {f.path: f for f in previous_files}
    for file in current_files:
        if only_types is not None and file.file_type not in only_types:
            continue
        if file.path not in cache:
            # new file
            yield (None, file)
        elif file != (old_file := cache[file.path]):
            # updated file
            yield (old_file, file)
        else:
            # samefile
            pass


def find_previous_snapshot(
    selected: Snapshot, others: list[Snapshot]
) -> Snapshot | None:
    out = None
    for candidate in others:
        if candidate.hostname != selected.hostname:
            continue
        if candidate.id == selected.id:
            continue
        if candidate.time < selected.time:
            if out is None or candidate.time < out.time:
                out = candidate
    return out


def select_snapshot(snap_id: str, snapshots: Iterable[Snapshot]) -> Snapshot:
    for snapshot in snapshots:
        if snap_id == snapshot.id or snap_id == snapshot.short_id:
            return snapshot
    raise ValueError(f"Cannot find snapshot wich id {snap_id}")


def sizeof(num: float, suffix: str = ""):
    """
    simply display a human readable size
    """
    for unit in ("", "K", "M", "G"):
        if abs(num) < 1024:
            if isinstance(num, float):
                return f"{num:0.1f}{unit}{suffix}"
            return f"{num}{unit}{suffix}"
        num /= 1024.0
    raise ValueError()
