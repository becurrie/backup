from unittest.mock import MagicMock, patch

import pytest
from azure.core.exceptions import ResourceNotFoundError

from backup.interfaces.storage.azure import AzureBlobStorageInterface


@pytest.fixture
def azure_blob_storage_interface():
    """Fixture for creating an AzureBlobStorageInterface instance."""
    interface = AzureBlobStorageInterface(
        config={
            "interface": "backup.interfaces.storage.azure.AzureBlobStorageInterface",
            "storage_account": "test_account",
            "storage_container": "test_container",
            "storage_key": "test_key",
        }
    )
    interface.client = MagicMock()

    return interface


def test_create(azure_blob_storage_interface):
    """Test that a directory can be created in the azure blob storage container."""
    path = "test_directory"
    mock_blob_client = azure_blob_storage_interface.client.get_blob_client.return_value

    azure_blob_storage_interface.create(path)

    azure_blob_storage_interface.client.get_blob_client.assert_called_once_with(path)
    mock_blob_client.upload_blob.assert_called_once_with(b"", overwrite=False)


def test_exists_when_blob_exists(azure_blob_storage_interface):
    """Test that the exists method returns true when the blob exists."""
    path = "existing_blob"
    mock_blob_client = azure_blob_storage_interface.client.get_blob_client.return_value
    mock_blob_client.get_blob_properties.return_value = MagicMock()

    result = azure_blob_storage_interface.exists(path)

    assert result is True
    azure_blob_storage_interface.client.get_blob_client.assert_called_once_with(path)
    mock_blob_client.get_blob_properties.assert_called_once()


def test_exists_when_blob_does_not_exist(azure_blob_storage_interface):
    """Test that the exists method returns false when the blob does not exist."""
    path = "non_existent_blob"
    mock_blob_client = azure_blob_storage_interface.client.get_blob_client.return_value
    mock_blob_client.get_blob_properties.side_effect = ResourceNotFoundError

    result = azure_blob_storage_interface.exists(path)

    assert result is False
    azure_blob_storage_interface.client.get_blob_client.assert_called_once_with(path)
    mock_blob_client.get_blob_properties.assert_called_once()


def test_upload(azure_blob_storage_interface):
    """Test that a file can be uploaded to the azure blob storage container."""
    file = MagicMock()
    file_size = 100
    dst = "uploaded_file"
    mock_blob_client = azure_blob_storage_interface.client.get_blob_client.return_value

    with patch("backup.settings.BACKUP_UPLOAD_CHUNK_SIZE", 25):
        with patch("backup.settings.BACKUP_UPLOAD_CONCURRENCY", 2):
            azure_blob_storage_interface.upload(file, file_size, dst)

    azure_blob_storage_interface.client.get_blob_client.assert_called_once_with(dst)
    assert mock_blob_client.commit_block_list.call_count == 1
    assert mock_blob_client.stage_block.call_count == 4


def test_upload_progress(azure_blob_storage_interface):
    """Test that a file can be uploaded to the azure blob storage container with a progress bar."""
    file = MagicMock()
    file_size = 100
    dst = "uploaded_file"
    mock_blob_client = azure_blob_storage_interface.client.get_blob_client.return_value

    with patch("backup.interfaces.storage.azure.tqdm") as mock_tqdm:
        with patch("backup.settings.BACKUP_UPLOAD_CHUNK_SIZE", 25):
            with patch("backup.settings.BACKUP_UPLOAD_CONCURRENCY", 2):
                azure_blob_storage_interface.upload(
                    file,
                    file_size,
                    dst,
                    progress={
                        "total": file_size,
                        "unit": "B",
                        "unit_scale": True,
                        "desc": "Uploading",
                    },
                )

    azure_blob_storage_interface.client.get_blob_client.assert_called_once_with(dst)
    assert mock_blob_client.commit_block_list.call_count == 1
    assert mock_blob_client.stage_block.call_count == 4
    mock_tqdm.assert_called_once_with(
        total=file_size,
        unit="B",
        unit_scale=True,
        desc="Uploading",
    )


def test_delete(azure_blob_storage_interface):
    """Test that a blob can be deleted from the azure blob storage container."""
    path = "delete_blob"
    mock_blob_client = azure_blob_storage_interface.client.get_blob_client.return_value

    azure_blob_storage_interface.delete(path)

    azure_blob_storage_interface.client.get_blob_client.assert_called_once_with(path)
    mock_blob_client.delete_blob.assert_called_once()


def test_list(azure_blob_storage_interface):
    """Test that a list of blobs can be retrieved from the azure blob storage container."""
    path = "path_to_list"
    path_mocks = []

    for name in [
        "path_to_list/blob1",
        "path_to_list/blob2",
        "path_to_list/blob3",
    ]:
        path_mock = MagicMock(spec_set=["name"])
        path_mock.name = name
        path_mocks.append(path_mock)

    azure_blob_storage_interface.client.list_blobs.return_value = path_mocks

    result = azure_blob_storage_interface.list(path)

    assert result == ["path_to_list/blob3", "path_to_list/blob2", "path_to_list/blob1"]
    azure_blob_storage_interface.client.list_blobs.assert_called_once_with(
        name_starts_with=path
    )
