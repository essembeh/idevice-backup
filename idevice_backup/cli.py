"""
command line interface
"""
import os
import traceback
from argparse import ArgumentParser, Namespace
from pathlib import Path

from colorama import Fore, Style
from lazy_object_proxy import Proxy

from . import __version__
from .commands import backup, extract, init, mount
from .ios import get_ios_device_name
from .restic import DEFAULT_PASSWORD, RESTIC_PASSWORD, RESTIC_REPOSITORY, Restic


def get_restic_repository(args: Namespace) -> Restic:
    device = get_ios_device_name()
    repository = None
    if args.repository is not None:
        repository = args.repository
    elif RESTIC_REPOSITORY in os.environ:
        repository = os.getenv(RESTIC_REPOSITORY)
    elif device is not None:
        repository = Path.home() / ".config" / "idevice-backup" / device
    else:
        raise ValueError(
            "Cannot find repository, use --repository to specify one, one connect an iOS device"
        )

    password = None
    if args.password is not None:
        password = args.password
    elif RESTIC_PASSWORD in os.environ:
        password = os.getenv(RESTIC_PASSWORD)
    else:
        password = DEFAULT_PASSWORD

    assert repository is not None
    assert password is not None and len(password) > 0

    return Restic(repository, password, verbose=args.verbose)


def run():
    """
    entry point
    """
    parser = ArgumentParser()
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="print more details"
    )
    parser.add_argument("-r", "--repository", help="restic repository")
    parser.add_argument(
        "-p",
        "--password",
        help=f"restic repository password, default is '{DEFAULT_PASSWORD}'",
    )

    subparsers = parser.add_subparsers()

    init.configure(subparsers.add_parser("init", help="init repository"))
    backup.configure(subparsers.add_parser("backup", help="backup connected idevice"))
    mount.configure(subparsers.add_parser("mount", help="mount connected idevice"))
    extract.configure(
        subparsers.add_parser("extract", help="extract last snapshot photos")
    )

    args = parser.parse_args()
    handler = args.handler
    restic = Proxy(lambda: get_restic_repository(args))
    try:
        out = handler(args, restic)
        exit(out if isinstance(out, int) else 0)
    except SystemExit:
        pass
    except KeyboardInterrupt:
        print("")
        exit(130)
    except BaseException as error:
        print(f"{Fore.RED}ERROR: {error}{Style.RESET_ALL}")
        if args.verbose:
            traceback.print_exception(error)
        exit(1)
