import logging
import os

import pydantic
import pytest
import yaml

from backup import settings
from backup.config.logger import initialize_logger


@pytest.fixture
def logging_test_config(tmp_path):
    """Fixture to create a temporary logging configuration."""
    settings.LOG_LEVEL = "DEBUG"
    settings.LOG_FILE_NAME = "test.log"
    settings.LOG_FILE_DIR = os.path.join(tmp_path, "logs")


def test_initialize_logger_file(logging_test_config, tmp_path):
    """Test initializing the logger."""
    initialize_logger()

    logger = logging.getLogger(__name__)

    assert os.path.exists(logger.root.handlers[1].baseFilename)
    assert logger.root.level == logging.DEBUG
