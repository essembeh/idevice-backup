from idevice_backup.utils import iter_different_files


def test_snapshots(restic):
    """
    just a test
    """
    snapshots = restic.list_snapshots()
    assert len(snapshots) > 0

    for snapshot in snapshots:
        count = 0
        print("Snapshot:", snapshot)
        for file in restic.iter_files(snapshot):
            print("  File:", file)
            count += 1
        assert count > 0


def test_updated_files(restic):
    snapshots = restic.list_snapshots()
    assert len(snapshots) >= 2

    previous_snapshot = snapshots[-2]
    current_snapshot = snapshots[-1]

    count = 0
    for previous_file, current_file in iter_different_files(
        restic.iter_files(previous_snapshot),
        restic.iter_files(current_snapshot),
        only_types=["file"],
    ):
        print("Difference:")
        print("  ", previous_file)
        print("  ", current_file)
        count += 1

    assert count == 10
