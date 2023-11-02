import os
import shlex
import subprocess
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Iterable, Iterator

from colorama import Fore, Style
from tqdm import tqdm

from .ios import get_ios_device_name
from .schema import File, Snapshot, Snapshots

RESTIC_REPOSITORY = "RESTIC_REPOSITORY"
RESTIC_PASSWORD = "RESTIC_PASSWORD"
DEFAULT_PASSWORD = "backup"


@dataclass
class Restic:
    repository: str | Path
    password: str
    binary: str = os.getenv("RESTIC_BIN", "restic")
    verbose: bool = False

    @cached_property
    def environ(self) -> dict[str, str]:
        out = dict(os.environ)
        if self.repository is not None:
            if isinstance(self.repository, Path):
                out[RESTIC_REPOSITORY] = str(self.repository.absolute())
            else:
                out[RESTIC_REPOSITORY] = str(self.repository)
        if self.password is not None:
            out[RESTIC_PASSWORD] = str(self.password)
        return out

    def _execute(
        self,
        args: Iterable[str],
        capture_output: bool = True,
        json: bool = True,
        cwd: Path | None = None,
    ) -> str:
        command = [self.binary]
        if json:
            command.append("--json")
        command += list(args)
        if self.verbose:
            print(f"Execute: {Fore.YELLOW}{shlex.join(command)}{Style.RESET_ALL}")
        process = subprocess.run(
            command,
            text=True,
            env=self.environ,
            capture_output=capture_output,
            check=False,
            cwd=cwd,
        )
        if process.returncode != 0:
            if self.verbose and capture_output:
                print(Style.DIM, process.stdout, Style.RESET_ALL, sep="")
                print(Style.DIM, Fore.RED, process.stderr, Style.RESET_ALL, sep="")
            raise ChildProcessError(
                f"{shlex.join(command)} returned {process.returncode}"
            )
        return process.stdout

    def init(self):
        self._execute(["init"], json=False, capture_output=False)

    def mount(self, mnt: Path):
        command = ["mount", str(mnt)]
        if (device := get_ios_device_name()) is not None:
            command += ["--host", device]
        self._execute(command, json=False, capture_output=False)

    def list_snapshots(self) -> list[Snapshot]:
        return Snapshots.model_validate_json(self._execute(["snapshots"])).root

    def iter_files(self, snapshot: Snapshot | None) -> Iterator[File]:
        if snapshot is not None:
            stdout = self._execute(["ls", snapshot.id])
            snapshot0 = None
            for line in stdout.splitlines():
                if snapshot0 is None:
                    snapshot0 = Snapshot.model_validate_json(line)
                else:
                    yield File.model_validate_json(line)

    def backup(
        self, root_folder: Path, include: Iterable[Path], host: str | None = None
    ):
        args = ["backup"]
        if host is not None:
            args += ["--host", host]
        args += [str(x.relative_to(root_folder)) for x in include]
        self._execute(args, cwd=root_folder, json=False, capture_output=False)

    def restore_files(
        self,
        snapshot: Snapshot,
        files: list[File],
        output_folder: Path,
        overwrite: bool = False,
    ) -> list[Path]:
        assert len(files) > 0
        args = ["restore", snapshot.id, "--target", str(output_folder)]
        out = []
        for file in tqdm(files, unit="file"):
            new_file = output_folder / str(file.path).removeprefix("/")
            if new_file.exists() and not overwrite:
                raise FileExistsError(f"File already exists: {new_file}")
            self._execute(args + ["--include", str(file.path)], json=False)
            if not new_file.exists():
                raise FileNotFoundError(f"Cannot find restored file: {new_file}")
            out.append(new_file)

        return out

    def restore_multiple_files(
        self,
        snapshot: Snapshot,
        files: list[File],
        output_folder: Path,
        overwrite: bool = False,
    ) -> list[Path]:
        assert len(files) > 0
        args = ["restore", snapshot.id, "--target", str(output_folder)]
        out = []
        for file in files:
            new_file = output_folder / str(file.path).removeprefix("/")
            if new_file.exists() and not overwrite:
                raise FileExistsError(f"File already exists: {new_file}")
            args += ["--include", str(file.path)]
            out.append(new_file)
        self._execute(args, json=False, capture_output=False)
        for new_file in out:
            if not new_file.exists():
                raise FileNotFoundError(f"Cannot find restored file: {new_file}")

        return out
