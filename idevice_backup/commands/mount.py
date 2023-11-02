from argparse import ArgumentParser, Namespace
from pathlib import Path
from tempfile import TemporaryDirectory

from colorama import Fore, Style

from ..ios import get_ios_device_name, mount_ios_device
from ..restic import Restic
from ..shell import spawn_shell
from ..utils import label


def configure(parser: ArgumentParser):
    """
    Configure parser for subcommand
    """
    parser.set_defaults(handler=run)
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-d",
        "--device",
        dest="source",
        action="store_const",
        const="device",
        default="device",
        help="mount ios device",
    )
    group.add_argument(
        "-r",
        "--restic",
        dest="source",
        action="store_const",
        const="repo",
        default="device",
        help="mount restic repository",
    )


def run(args: Namespace, restic: Restic):
    """
    Handler for subcommand
    """
    if args.source == "device":
        with mount_ios_device() as mnt:
            device = get_ios_device_name()
            print(
                f"Mount 📱 {Style.BRIGHT}{Fore.YELLOW}{device}{Style.RESET_ALL} to {label(mnt)}"
            )
            return spawn_shell(mnt, device)
    elif args.source == "repo":
        with TemporaryDirectory() as mnt:
            mnt = Path(mnt)
            print(f"Mount {label(restic)} to {label(mnt)}")
            try:
                restic.mount(mnt)
            except KeyboardInterrupt:
                pass
            print(f"Umount {label(mnt)}")
