# Arch Linux BTRFS Installation Script

This repository contains a Python script designed to automate the installation of Arch Linux on a BTRFS filesystem.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [Disclaimer](#disclaimer)
- [License](#license)

## Features
- **Automated Installation**: Simplify the Arch Linux installation process with a single script.
- **BTRFS Filesystem**: Specifically tailored for installations on a BTRFS filesystem.
- **Partitioning**: Automated disk partitioning to ensure optimal setup.
- **Base System Installation**: Installs the necessary base system for Arch Linux.

## Prerequisites
- A system compatible with Arch Linux.
- An active internet connection during installation.
- A USB drive or CD with the Arch Linux ISO.

## Installation
1. Clone this repository:
   ```bash
   curl -LO https://bit.ly/arch_btrfs_install
   git clone https://github.com/ArchLinux-Development/Arch_BTRFS_Install_Script.git
   ```
2. Navigate to the cloned directory: If Cloned otherwise SKIP
   ```bash
   cd Arch_BTRFS_Install_Script
   ```

## Usage
1. Make the script executable:
   ```bash
   chmod +x arch_btrfs_install.py
   ```
2. Run the script:
   ```bash
   python ./arch_btrfs_install.py
   ```

## Contributing
We welcome contributions! If you find a bug or have a feature request, please open an issue. If you'd like to contribute code, please fork the repository and submit a pull request.

## Disclaimer
This script is still in development and may contain bugs. Always backup your data before proceeding with the installation and use at your own risk.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

This is a basic structure for the README. You can further enhance it by adding screenshots, more detailed explanations, or any other information you deem necessary.
