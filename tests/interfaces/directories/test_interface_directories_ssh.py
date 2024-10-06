import shutil
from unittest.mock import MagicMock, mock_open, patch

import pydantic
import pytest

from backup.interfaces.directories.ssh import SSHDirectoryBackupInterface


@pytest.fixture
def ssh_directory_backup_interface():
    """Fixture for creating a SSHDirectoryBackupInterface instance."""
    with patch("paramiko.SSHClient.connect"):
        interface = SSHDirectoryBackupInterface(
            config={
                "interface": "backup.interfaces.directories.ssh.SSHDirectoryBackupInterface",
                "directories": [
                    {
                        "src": "/path/to/source/1",
                        "dest": "/path/to/destination/1",
                        "name": "directory1",
                        "exclude": [
                            "/path/to/source/1/exclude1",
                        ],
                    },
                ],
                "ssh_host": "host",
                "ssh_port": 22,
                "ssh_username": "user",
                "ssh_password": "password",
                "ssh_private_key": "/path/to/private/key",
            },
            storage=MagicMock(),
        )

    return interface


def test_validate(ssh_directory_backup_interface):
    """Test that remote directories are validated correctly."""
    mock_stdout = MagicMock()
    mock_stdout.channel.recv_exit_status.return_value = 0

    with patch(
        "paramiko.SSHClient.exec_command",
        return_value=(MagicMock(), mock_stdout, MagicMock()),
    ):
        ssh_directory_backup_interface.validate()


def test_validate_invalid(ssh_directory_backup_interface):
    """Test that an exception is raised when a remote directory is invalid."""
    mock_stdout_does_not_exist = MagicMock()
    mock_stdout_does_not_exist.channel.recv_exit_status.side_effect = [1]

    mock_stdout_permission_denied = MagicMock()
    mock_stdout_permission_denied.channel.recv_exit_status.side_effect = [0, 1]

    def mock_exec_command(command):
        if "does_not_exist" in command:
            return None, mock_stdout_does_not_exist, None
        if "permission_denied" in command:
            return None, mock_stdout_permission_denied, None

    ssh_directory_backup_interface.client.exec_command = mock_exec_command

    with pytest.raises(ValueError) as exc_info:
        ssh_directory_backup_interface.config.directories[0].src = "does_not_exist"
        ssh_directory_backup_interface.validate()

    assert (
        str(exc_info.value)
        == "directory: 'does_not_exist' does not exist on the remote machine"
    )

    with pytest.raises(ValueError) as exc_info:
        ssh_directory_backup_interface.config.directories[0].src = "permission_denied"
        ssh_directory_backup_interface.validate()

    assert (
        str(exc_info.value)
        == "application does not have read access to directory: 'permission_denied'"
    )


def test_archive(ssh_directory_backup_interface):
    """Test that a remote directory can be archived."""
    mock_stdout = MagicMock()
    mock_stdout.channel.recv_exit_status.return_value = 0

    with patch(
        "paramiko.SSHClient.exec_command",
        return_value=(MagicMock(), mock_stdout, MagicMock()),
    ):
        with patch("shutil.make_archive", return_value="/path/to/archive.tar.gz"):
            result, extension = ssh_directory_backup_interface.archive(
                directory=ssh_directory_backup_interface.config.directories[0],
                src=ssh_directory_backup_interface.config.directories[0].src,
            )

    assert result == "/tmp/directory1.tar.gz"
    assert extension == "tar.gz"
