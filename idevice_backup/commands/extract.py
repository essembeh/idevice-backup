from argparse import ArgumentParser, Namespace
from pathlib import Path

from idevice_backup.mime import is_image, is_video

from ..restic import Restic
from ..utils import (
    find_previous_snapshot,
    iter_different_files,
    label,
    select_snapshot,
    sizeof,
)


def configure(parser: ArgumentParser):
    """
    Configure parser for subcommand
    """
    parser.set_defaults(handler=run)
    parser.add_argument(
        "-l", "--list", action="store_true", help="list snapshots and do nothing"
    )
    parser.add_argument(
        "-i",
        "--ignore-mtime",
        action="store_true",
        help="ignore ctime to detect new files",
    )
    parser.add_argument("-o", "--output", type=Path, help="folder to extract new files")
    parser.add_argument(
        "-s", "--snapshot", dest="current", help="snapshot, default is latest"
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="extract all files, not only images and videos",
    )


def run(args: Namespace, restic: Restic):
    """
    Handler for subcommand
    """

    print(f"Restic repository: {label(restic)}")
    snapshots = restic.list_snapshots()
    print("Found snapshots:")
    for snapshot in snapshots:
        print(f"  {label(snapshot)}")

    if not args.list:
        current_snapshot = (
            select_snapshot(args.current, snapshots)
            if args.current is not None
            else sorted(snapshots, key=lambda s: s.time)[-1]
        )
        assert current_snapshot is not None, "Cannot find any snapshot"

        previous_snapshot = find_previous_snapshot(current_snapshot, snapshots)
        print(
            f"\nFind new files between {label(previous_snapshot) or 'N/A'} and {label(current_snapshot)}",
        )

        new_files = []
        new_files_size = 0
        for _, current_file in iter_different_files(
            restic.iter_files(previous_snapshot),
            restic.iter_files(current_snapshot),
            only_types=["file"],
            ignore_mtime=args.ignore_mtime,
        ):
            if current_file is None:
                # deleted file
                continue
            if args.all or is_image(current_file.path) or is_video(current_file.path):
                new_files.append(current_file)
                new_files_size += current_file.size or 0
                print("   ", label(current_file))
        print(f"{len(new_files)} new file(s), {sizeof(new_files_size, suffix='B')}")

        if len(new_files) > 0 and args.output is not None:
            target_folder = (
                args.output
                / f"{current_snapshot.hostname} ({current_snapshot.time.isoformat(sep=' ', timespec='seconds')})"
            )
            target_folder.mkdir(parents=True, exist_ok=True)
            print(f"\nExtract {len(new_files)} file(s) to {label(target_folder)}")
            restic.restore_multiple_files(current_snapshot, new_files, target_folder)
