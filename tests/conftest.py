from pathlib import Path

import pytest

from idevice_backup.restic import DEFAULT_PASSWORD, Restic


@pytest.fixture
def restic() -> Restic:
    repository = Path(__file__).parent.parent / "samples" / "repo1.restic"
    assert repository.is_dir()
    return Restic(repository, DEFAULT_PASSWORD)
