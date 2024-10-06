import os
from unittest.mock import MagicMock, patch

import pytest
from azure.core.exceptions import ResourceNotFoundError

from backup.interfaces.vault.azure import AzureKeyVaultInterface


@pytest.fixture
def azure_key_vault_interface():
    """Fixture for creating an AzureKeyVaultInterface instance."""
    interface = AzureKeyVaultInterface(
        config={
            "interface": "backup.interfaces.vault.azure.AzureKeyVaultInterface",
            "url": "https://test.vault.azure.net/",
            "secrets": {
                "ENV_VAR_1": "secret-name-1",
                "ENV_VAR_2": "secret-name-2",
            },
        }
    )
    interface.client = MagicMock()

    return interface


def test_get_client(azure_key_vault_interface):
    """Test that a client can be retrieved from the azure key vault."""
    with patch(
        "backup.interfaces.vault.azure.DefaultAzureCredential"
    ) as mock_credential:
        with patch("backup.interfaces.vault.azure.SecretClient") as mock_secret_client:
            client = azure_key_vault_interface.get_client()

    mock_credential.assert_called_once()
    mock_secret_client.assert_called_once_with(
        vault_url="https://test.vault.azure.net/",
        credential=mock_credential.return_value,
    )

    assert client == mock_secret_client.return_value


def test_load(azure_key_vault_interface):
    """Test that secrets can be loaded from the azure key vault."""
    mock_environment = {}

    with patch("os.environ", mock_environment):
        azure_key_vault_interface.get_secret = MagicMock()
        azure_key_vault_interface.get_secret.return_value = "secret-value"
        azure_key_vault_interface.load()

    assert azure_key_vault_interface.get_secret.call_count == 2
    assert mock_environment == {
        "ENV_VAR_1": "secret-value",
        "ENV_VAR_2": "secret-value",
    }


def test_get_secret(azure_key_vault_interface):
    """Test that a secret can be retrieved from the azure key vault."""
    with patch.object(
        azure_key_vault_interface.client, "get_secret"
    ) as mock_get_secret:
        mock_get_secret.return_value.value = "secret-value"
        secret_value = azure_key_vault_interface.get_secret("secret-name")

    mock_get_secret.assert_called_once_with("secret-name")
    assert secret_value == "secret-value"
