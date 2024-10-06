
# Backup Interfaces

A simple backup application that uses an interface-based approach to perform backups against your resources
using simple, and straight-forward configuration files to define and manage your backup processes.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Requirements](#requirements)
- [Setup and Installation](#setup-and-installation)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Install Dependencies](#2-install-dependencies)
- [Configuration Files](#configuration-files)
  - [Examples](#examples)
    - [Local Directory Backup](#local-directory-backup)
    - [Remote SSH Directory Backup](#remote-ssh-directory-backup)

## Project Overview

The **Backup Interfaces App** is designed to run scheduled backups against your resources, using a simple and
straight-forward configuration file to define and manage your backup process/policy.

The application uses an interface-based approach to define and manage your backup processes, allowing you to easily
extend or modify the backup processes to suit your evolving needs.

## Features
- **Granular Configurations**: Define your backup policy using a simple and straight-forward configuration file.
- **Environment Configuration**: Use environment variables to manage your secrets and sensitive data directly in your configuration files.
- **Secrets Management**: Vault management interfaces to retrieve and load your secrets directly into your configuration files.
- **Interface-based Backups**: Pick and choose the interfaces you want to use to back up your resources.

## Requirements

- Python 3.9+

## Setup and Installation

To use the backup-interfaces app, you can install the package from PyPI:

```bash
pip install backup-interfaces
```

If you're looking to contribute to the project or run the app locally,
you can follow the steps below:

### 1. Clone the Repository

```bash
git clone git@github.com:becurrie/backup-interfaces.git
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## Configuration Files

The backup-interfaces package uses a configuration file to define and manage your backup processes. 
The configuration file is a simple YAML file that defines your backup policy, this includes any
secrets, vaults, storage, and backup interfaces you want to use.

### Examples

#### Local Directory Backup

Here's an example of a relatively simple configuration file that uses a local directory 
interface to back up a directory that exists on the local machine running the backup application,
and stores those backups on the local machine as well.

```yaml

name: my-local-backup-configuration
enabled: true

storage:
  interface: interfaces.storage.local.LocalStorageInterface

interfaces:
  - interface: interfaces.directories.local.LocalDirectoryBackupInterface
    enabled: true
    directories:
      - src: /path/to/source
        dest: backups
        name: source
        retention:
        count: 5
    
 ```

#### Remote SSH Directory Backup

Here's an example of a more complex configuration file that uses an azure key vault to store/retrieve secrets,
an azure blob storage interface to store the backups, and an ssh directory interface to back up a directory
that exists on a remote ssh host.

```yaml

name: my-ssh-backup-configuration
enabled: true

vaults:
  - interface: interfaces.vault.azure.AzureKeyVaultInterface
    secrets:
      AZURE_STORAGE_KEY: my-storage-key
    url: https://my-key-vault.vault.azure.net/

storage:
  interface: interfaces.storage.azure.AzureBlobStorageInterface
  storage_account: my-storage-account
  storage_container: my-storage-container
  storage_key: ${AZURE_STORAGE_KEY}

interfaces:
  - interface: interfaces.directories.ssh.SSHDirectoryBackupInterface
    enabled: true
    directories:
      - src: /path/to/source
        dest: backups
        name: source
        retention:
          count: 5
    ssh_host: my-ssh-host.com
    ssh_user: my-ssh-user
    ssh_private_key: /path/to/private-key
    ssh_port: 22

```

## Running the Application

In Progress...

## Deployment / Usage

In Progress...


