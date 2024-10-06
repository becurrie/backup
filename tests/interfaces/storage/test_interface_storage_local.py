import os
from unittest.mock import patch

import pytest

from backup.interfaces.storage.local import LocalStorageInterface


@pytest.fixture
def local_storage_interface():
    """Fixture for creating a LocalStorageInterface instance."""
    interface = LocalStorageInterface(
        config={
            "interface": "backup.interfaces.storage.local.LocalStorageInterface",
        }
    )

    return interface


def test_create(local_storage_interface, tmp_path):
    """Test that a directory can be created in the local filesystem."""
    path = os.path.join(tmp_path, "test_directory")

    local_storage_interface.create(path)

    assert os.path.exists(path)


def test_exists_when_directory_exists(local_storage_interface, tmp_path):
    """Test that the exists method returns true when the directory exists."""
    path = os.path.join(tmp_path, "existing_directory")

    local_storage_interface.create(path)

    assert local_storage_interface.exists(path) is True


def test_exists_when_directory_does_not_exist(local_storage_interface, tmp_path):
    """Test that the exists method returns false when the directory does not exist."""
    path = os.path.join(tmp_path, "non_existent_directory")

    assert local_storage_interface.exists(path) is False


def test_upload(local_storage_interface, tmp_path):
    """Test that a file can be uploaded to the local filesystem."""
    file_path = os.path.join(tmp_path, "test_file")
    file_data = b"test data"
    file_size = len(file_data)
    file_dst = os.path.join(tmp_path, "uploaded_file")

    with open(file_path, "wb") as file:
        file.write(file_data)

    with patch("backup.settings.BACKUP_UPLOAD_CHUNK_SIZE", 25):
        with patch("backup.settings.BACKUP_UPLOAD_CONCURRENCY", 2):
            with open(file_path, "rb") as file:
                local_storage_interface.upload(file, file_size, file_dst)

    assert os.path.exists(file_dst)

    with open(file_dst, "rb") as file:
        assert file.read() == file_data


def test_upload_progress(local_storage_interface, tmp_path):
    """Test that a file can be uploaded to the local filesystem with progress."""
    file_path = os.path.join(tmp_path, "test_file")
    file_data = b"test data"
    file_size = len(file_data)
    file_dst = os.path.join(tmp_path, "uploaded_file")

    with open(file_path, "wb") as file:
        file.write(file_data)

    with patch("backup.settings.BACKUP_UPLOAD_CHUNK_SIZE", 25):
        with patch("backup.settings.BACKUP_UPLOAD_CONCURRENCY", 2):
            with open(file_path, "rb") as file:
                local_storage_interface.upload(
                    file,
                    file_size,
                    file_dst,
                    progress={
                        "total": file_size,
                        "unit": "B",
                        "unit_scale": True,
                        "desc": "Uploading",
                    },
                )

    assert os.path.exists(file_dst)

    with open(file_dst, "rb") as file:
        assert file.read() == file_data


def test_delete(local_storage_interface, tmp_path):
    """Test that a file can be deleted from the local filesystem."""
    path = os.path.join(tmp_path, "test_file")

    with open(path, "w") as file:
        file.write("test data")

    assert os.path.exists(path)

    local_storage_interface.delete(path)

    assert not os.path.exists(path)


def test_list(local_storage_interface, tmp_path):
    """Test that a list of files can be retrieved from the local filesystem."""
    file_paths = [
        os.path.join(tmp_path, "file1"),
        os.path.join(tmp_path, "file2"),
        os.path.join(tmp_path, "file3"),
    ]

    for file_path in file_paths:
        with open(file_path, "w") as file:
            file.write("test data")

    assert local_storage_interface.list(tmp_path) == list(reversed(file_paths))
