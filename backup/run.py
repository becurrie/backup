import logging

from backup import settings
from backup.utils import get_class


def run_backup(config):
    """Run the backup process using the provided configuration.

    Args:
        config: The configuration object to use for the backup process.

    """
    logger = logging.getLogger(__name__)
    logger.info("starting backup process")
    logger.info("using backup configuration: '%s'", config.name)

    storage_cls = get_class(cls=config.storage.interface)
    storage_instance = storage_cls(config=config.storage)

    configs, instances = [], []

    for interface in config.interfaces:
        if interface.enabled:
            configs.append(interface)
        else:
            logger.info("interface: '%s' is disabled, skipping this interface...")

    for config in configs:
        cls = get_class(cls=config.interface)
        instances.append(cls(config=config, storage=storage_instance))

    for instance in instances:
        try:
            instance.validate()
            instance.backup()
        except Exception as exc:
            if settings.BACKUP_GRACEFUL_ERRORS:
                logger.error(
                    "%s occurred while running interface: '%s', skipping this interface..."
                    % (type(exc), instance.config.interface),
                    exc_info=True,
                )
            else:
                raise
