from argparse import ArgumentParser, Namespace

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


def run(args: Namespace, restic: Restic):
    """
    Handler for subcommand
    """
    with mount_ios_device() as mnt:
        device = get_ios_device_name()
        print(
            f"Mount 📱 {Style.BRIGHT}{Fore.YELLOW}{device}{Style.RESET_ALL} to {label(mnt)}"
        )
        return spawn_shell(mnt, device)
