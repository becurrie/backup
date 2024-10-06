import logging
import os
import platform
import shutil
import tarfile
from typing import List

from backup.config.models import DirectoryBackupInterfaceConfig, DirectoryConfig
from backup.decorators import log_execution
from backup.interfaces.interface import BackupInterface
from backup.utils import format_object, get_backup_name


class LocalDirectoryBackupInterface(BackupInterface):
    """Concrete implementation of a backup interface for backing up directories
    located on the local machine.

    This class provides methods for backing up directories located on the local machine.
    It manages the process of creating an archive of the specified directories and uploading
    the archive to the configured storage interface.

    No additional setup is required to get local directory backups working.

    Settings:

    - directories (List[DirectoryConfig]): A list of directories to back up.
        This is a list of directories to back up on the local machine. Each directory
        must have a source path on the local machine and a destination path for the backup.

    """

    config_cls = DirectoryBackupInterfaceConfig

    def _validate_directories(self):
        """Validate the directories to be backed up.

        This method checks that the directories to be backed up exist on the
        local machine that the backup process is running on, and that the application
        has the necessary permissions to read the directories.

        Raises:
            ValueError: If any specified directories are missing or inaccessible.

        """
        logger = logging.getLogger(__name__)
        logger.info("validating local source directories")

        for directory in self.config.directories:
            if not os.path.exists(directory.src):
                raise ValueError(
                    "directory: %s does not exist on the local machine" % directory.src,
                )
            if not os.access(directory.src, os.R_OK):
                raise ValueError(
                    "application does not have read access to directory: %s"
                    % directory.src
                )

    def validate(self):
        """Validate the local directory backup interface.

        Raises:
            ValueError: If any specified directories are missing or inaccessible.

        """
        self._validate_directories()

    @log_execution(
        __name__,
        prefix="created archive of local directory",
    )
    def archive(self, directory, src):
        """Create an archive file of the specified local directory.

        This method creates an archive of the specified local directory, which
        can then be uploaded to the configured storage interface.

        Args:
            directory: The directory configuration to archive.
            src (str): The path to the directory to archive.

        Returns:
            Tuple[str, str]: A tuple containing the path to the archive file and
                the extension of the archive file.

        """
        logger = logging.getLogger(__name__)
        logger.info("creating archive of local directory: '%s'", src)

        file = shutil.make_archive(
            base_name=src,
            root_dir=src,
            format="gztar",
        )

        return file, ".".join(file.rsplit(".")[1:])

    def backup(self):
        """Backup the specified local directories.

        This method acts as the entry point for the local directory backup interface,
        and is responsible for backing up the specified directories to the configured
        storage interface.

        For local directory backups, the directories are first compressed into a zip
        archive, and then uploaded to the storage interface, where they are stored
        as individual files.

        When the backup is complete, the temporary zip archive is removed from the
        local machine to free up disk space.

        """
        logger = logging.getLogger(__name__)
        logger.debug("backing up local directories")

        for directory in self.config.directories:
            logger.info("backing up directory: '%s'", directory.src)
            logger.debug("directory configuration: %s" % format_object(directory))

            src, dst, name = (
                directory.src,
                directory.dest,
                directory.name,
            )
            archive, extension = self.archive(
                directory,
                src,
            )

            dst_name = get_backup_name(name)
            dst = os.path.join(dst, name)
            dst_backup = os.path.join(dst, dst_name + ".%s" % extension)

            if not self.storage.exists(path=dst):
                self.storage.create(path=dst)

            with open(archive, "rb") as file_obj:
                file_obj_size = os.path.getsize(archive)
                file_obj_progress = {
                    "total": file_obj_size,
                    "unit": "B",
                    "unit_scale": True,
                    "desc": "Uploading from local directory",
                }
                self.storage.upload(
                    file=file_obj,
                    file_size=file_obj_size,
                    dst=dst_backup,
                    progress=file_obj_progress,
                )

            logger.info("removing temporary archive of local directory: '%s'", archive)

            os.remove(archive)

            if directory.retention:
                self.storage.retention(
                    path=dst,
                    config=directory.retention,
                )
