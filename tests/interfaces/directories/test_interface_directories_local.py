import shutil
from unittest.mock import MagicMock, mock_open, patch

import pydantic
import pytest

from backup.interfaces.directories.local import LocalDirectoryBackupInterface


@pytest.fixture
def local_directory_backup_interface():
    """Fixture for creating a LocalDirectoryBackupInterface instance."""
    interface = LocalDirectoryBackupInterface(
        config={
            "interface": "backup.interfaces.directories.local.LocalDirectoryBackupInterface",
            "directories": [
                {
                    "src": "/path/to/source/1",
                    "dest": "/path/to/destination/1",
                    "name": "directory1",
                },
                {
                    "src": "/path/to/source/2",
                    "dest": "/path/to/destination/2",
                    "name": "directory2",
                },
            ],
        },
        storage=MagicMock(),
    )

    return interface


def test_validate(local_directory_backup_interface):
    """Test that local directories are validated correctly."""
    with patch("os.path.exists", return_value=True):
        with patch("os.access", return_value=True):
            local_directory_backup_interface.validate()


def test_validate_invalid(local_directory_backup_interface):
    """Test that an exception is raised when a local directory is invalid."""
    with patch("os.path.exists", return_value=False):
        with pytest.raises(ValueError) as exc_info:
            local_directory_backup_interface.validate()

    assert (
        str(exc_info.value)
        == "directory: /path/to/source/1 does not exist on the local machine"
    )

    with patch("os.path.exists", return_value=True):
        with patch("os.access", return_value=False):
            with pytest.raises(ValueError) as exc_info:
                local_directory_backup_interface.validate()

    assert (
        str(exc_info.value)
        == "application does not have read access to directory: /path/to/source/1"
    )


def test_archive(local_directory_backup_interface):
    """Test that a directory can be archived."""
    with patch(
        "shutil.make_archive", return_value="/path/to/archive.tar.gz"
    ) as make_archive_mock:
        result, extension = local_directory_backup_interface.archive(
            directory=local_directory_backup_interface.config.directories[0],
            src=local_directory_backup_interface.config.directories[0].src,
        )

        make_archive_mock.assert_called_once_with(
            base_name="/path/to/source/1",
            root_dir="/path/to/source/1",
            format="gztar",
        )

        assert result == "/path/to/archive.tar.gz"
        assert extension == "tar.gz"
