# Arch BTRFS Install Script

This script provides a streamlined method to install Arch Linux with a BTRFS filesystem. It's designed to simplify the installation process, making it more user-friendly and efficient.

## Table of Contents

- [Arch BTRFS Install Script](#arch-btrfs-install-script)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Prerequisites](#prerequisites)
  - [Usage](#usage)
  - [Optional Repositories](#optional-repositories)
  - [BTRFS LUKS Encryption](#btrfs-luks-encryption)
  - [Recommendations](#recommendations)
  - [Contributing](#contributing)
  - [License](#license)

## Features

- **BTRFS Filesystem**: The script uses the BTRFS filesystem, which offers advanced features like snapshots, compression, and subvolumes.
  
- **UEFI and Legacy Boot**: Whether your system uses UEFI or Legacy boot modes, this script has got you covered.

- **Optional Repositories**: Extend your package selection with additional repositories like CachyOS and Chaotic AUR.

- **BTRFS LUKS Encryption**: The script provides an option for users to set up LUKS encryption on their BTRFS filesystem, ensuring data security.

## Prerequisites

Before you begin, ensure you have:

- A bootable Arch Linux USB or CD.
- An active internet connection during the installation.
- Basic knowledge of Linux command-line operations.

## Usage

1. Boot into your Arch Linux live environment.
2. Download the script:

```bash
curl -LO https://bit.ly/arch_btrfs_install
```

3. Make the script executable:

```bash
chmod +x arch_btrfs_install.py
```

4. Execute the script:

```bash
./arch_btrfs_install.py
```

## Optional Repositories

Expand your Arch Linux experience with these optional repositories:

- **[CachyOS](https://cachyos.org)**: An optimized version of Arch Linux that incorporates the Cachy scheduler.
  
- **[Chaotic AUR](https://aur.chaotic.cx)**: An unofficial user repository offering a plethora of packages not present in the official repositories.

## BTRFS LUKS Encryption

For users who prioritize data security, the script offers an option to set up LUKS encryption on the BTRFS filesystem. This ensures that your data remains encrypted and can only be accessed with the correct passphrase.

## Recommendations

- **Backup**: Always back up any crucial data before initiating the installation process.
  
- **Documentation**: For a smoother installation experience, familiarize yourself with the [Arch Linux installation guide](https://wiki.archlinux.org/title/Installation_guide) and the [features of BTRFS](https://btrfs.wiki.kernel.org/index.php/Main_Page).
  
- **Snapshots**: After the installation, consider exploring BTRFS's snapshot capabilities and set up a regular snapshot schedule.

## Contributing

We value your input! Contributions, issues, and feature requests are always welcome. Check the [issues page](https://github.com/ArchLinux-Development/Arch_BTRFS_Install_Script/issues) for current issues or to create a new one.

## License

This project is licensed under [MIT](https://github.com/ArchLinux-Development/Arch_BTRFS_Install_Script/blob/main/LICENSE).
