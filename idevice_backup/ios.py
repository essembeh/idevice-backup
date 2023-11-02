import shlex
import subprocess
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator

from colorama import Fore, Style


def get_ios_device_name() -> str | None:
    process = subprocess.run(
        ["ideviceinfo", "-k", "DeviceName"],
        text=True,
        check=False,
        capture_output=True,
    )
    if process.returncode == 0 and process.stdout is not None:
        return process.stdout.strip()


@contextmanager
def mount_ios_device() -> Generator[Path, None, None]:
    device = get_ios_device_name()
    assert device is not None, "No idevice found"
    with TemporaryDirectory(prefix=f"{device.replace(' ', '_')}_") as tmp:
        subprocess.run(["ifuse", tmp], check=True)
        try:
            yield Path(tmp)
        finally:
            umount_command = ["fusermount", "-u", tmp]
            umount = subprocess.run(umount_command, check=False)
            if umount.returncode != 0:
                print(
                    f"Warning, could not umount: {Fore.YELLOW}{shlex.join(umount_command)}{Style.RESET_ALL}"
                )
