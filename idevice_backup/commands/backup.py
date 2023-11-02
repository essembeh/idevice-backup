from argparse import ArgumentParser, Namespace
from pathlib import Path

from colorama import Fore, Style

from ..ios import get_ios_device_name, mount_ios_device
from ..restic import Restic
from ..utils import label


def configure(parser: ArgumentParser):
    """
    Configure parser for subcommand
    """
    parser.set_defaults(handler=run)
    parser.add_argument(
        "-a", "--all", action="store_true", help="backup all files, not only photos"
    )


def run(args: Namespace, restic: Restic):
    """
    Handler for subcommand
    """
    with mount_ios_device() as mnt:
        if args.all:
            folders = list(mnt.iterdir())
        else:
            folders = [mnt / "DCIM", mnt / "PhotoData" / "Mutations"]
        device = get_ios_device_name()
        print(f"Restic repository: {label(restic)}")
        print(f"Backup from {Fore.YELLOW}{device}{Style.RESET_ALL}:")
        for item in folders:
            print(f"  {label(item)}")
        print("")
        restic.backup(mnt, filter(Path.exists, folders), host=device)
