from argparse import ArgumentParser, Namespace

from ..restic import Restic
from ..utils import label


def configure(parser: ArgumentParser):
    """
    Configure parser for subcommand
    """
    parser.set_defaults(handler=run)


def run(args: Namespace, restic: Restic):  # pylint: disable=unused-argument
    """
    Handler for subcommand
    """
    print(f"Initialize Restic repository: {label(restic)}")
    restic.init()
