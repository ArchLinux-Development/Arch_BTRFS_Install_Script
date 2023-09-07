# Standard library imports
import os
import subprocess
import re
import sys
import curses
import logging
from pathlib import Path
from libs.bootloader import bootloader_menu

from libs.utils import is_strong_password, run_command


def install_filesystem_menu(stdscr):
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    menu_options = [
        "Choose Drive",
        "Format Partitions",
        "Create Subvolumes",
        "Mount File System",
        "Install Bootloader",
        "Exit"
    ]

    current_option = 0
    drive = None

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        for idx, option in enumerate(menu_options):
            x = w // 2 - len(option) // 2
            y = h // 2 - len(menu_options) // 2 + idx

            if idx == current_option:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, option)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, option)

        key = stdscr.getch()

        if key == curses.KEY_UP and current_option > 0:
            current_option -= 1
        elif key == curses.KEY_DOWN and current_option < len(menu_options) - 1:
            current_option += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_option == 0:
                drive = choose_drive_curses(stdscr)
            elif current_option == 1:
                format_partitions_curses(stdscr, drive)
            elif current_option == 2:
                create_subvolumes_curses(stdscr, drive)
            elif current_option == 3:
                mount_file_system_curses(stdscr, drive)
            elif current_option == 4:  # Corrected the index for "Install Bootloader"
                bootloader_menu(stdscr)
            elif current_option == 5:  # Corrected the index for "Exit"
                break

        stdscr.refresh()


def choose_drive_curses(stdscr):
    drives = get_connected_drives()
    current_option = 0

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # Title
        title = "Choose a Drive"
        stdscr.addstr(0, (w - len(title)) // 2, title, curses.A_BOLD)

        # If no drives are detected
        if not drives:
            stdscr.addstr(2, 0, "No drives detected!")
            stdscr.getch()
            return None

        # Display drives
        for idx, drive in enumerate(drives):
            x = 5
            y = 2 + idx

            if idx == current_option:
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(y, x, drive)
                stdscr.attroff(curses.A_REVERSE)
            else:
                stdscr.addstr(y, x, drive)

        # Add an option to return to the submenu
        return_option = "Return to submenu"
        if current_option == len(drives):
            stdscr.attron(curses.A_REVERSE)
            stdscr.addstr(2 + len(drives), 5, return_option)
            stdscr.attroff(curses.A_REVERSE)
        else:
            stdscr.addstr(2 + len(drives), 5, return_option)

        key = stdscr.getch()

        if key == curses.KEY_UP and current_option > 0:
            current_option -= 1
        elif key == curses.KEY_DOWN and current_option < len(drives):
            current_option += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_option == len(drives):
                install_filesystem_menu(stdscr)  # Return to the main menu
                return
            else:
                return drives[current_option]

        stdscr.refresh()

def get_connected_drives():
    result = run_command("lsblk -dpno NAME,SIZE,MODEL")
    lines = result.stdout.split("\n")
    drives = []
    for line in lines:
        if line:
            drives.append(line.strip())
    return drives

def setup_luks_encryption_curses(stdscr, drive):
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Enter a passphrase for LUKS encryption: ")
        curses.echo()
        passphrase = stdscr.getstr(1, 0).decode('utf-8')
        curses.noecho()

        if not is_strong_password(passphrase):
            stdscr.addstr(2, 0, "Weak passphrase! Ensure it's at least 8 characters long, contains lowercase, uppercase, numbers, and special characters.")
            stdscr.getch()
            continue

        stdscr.addstr(2, 0, "Confirm passphrase: ")
        curses.echo()
        confirm_passphrase = stdscr.getstr(3, 0).decode('utf-8')
        curses.noecho()

        if passphrase != confirm_passphrase:
            stdscr.addstr(4, 0, "Passphrases do not match!")
            stdscr.getch()
            continue
        break

def format_partitions_curses(stdscr, drive):
    if not drive:
        stdscr.addstr(0, 0, "No drive selected!")
        stdscr.getch()
        return

    stdscr.addstr(1, 0, f"WARNING: You are about to format the drive {drive}.")
    stdscr.addstr(2, 0, "All data on this drive will be permanently lost!")
    stdscr.addstr(3, 0, "Are you sure you want to proceed? (y/n): ")
    confirmation = stdscr.getch()

    if confirmation != ord('y'):
        stdscr.addstr(4, 0, "Operation cancelled.")
        stdscr.getch()
        return

    stdscr.addstr(5, 0, "Do you want to enable LUKS encryption? (y/n): ")
    encrypt_choice = stdscr.getch()
    if encrypt_choice == ord('y'):
        drive = setup_luks_encryption_curses(stdscr, drive)

    stdscr.addstr(6, 0, "Do you want to enable Btrfs compression? (y/n): ")
    choice = stdscr.getch()
    if choice == ord('y'):
        run_command(f"mkfs.btrfs -f --compress=zstd {drive}2")
    else:
        run_command(f"mkfs.btrfs -f {drive}2")

    stdscr.addstr(7, 0, "Partitions formatted successfully!")
    stdscr.getch()

def create_subvolumes_curses(stdscr, drive):
    # Unmount /mnt before creating subvolumes
    run_command("umount /mnt")

    # Mount the drive to /mnt
    run_command(f"mount {drive} /mnt")

    # Define the subvolumes
    subvolumes = [
        SubvolumeModification(Path('@'), Path('/')),
        SubvolumeModification(Path('@home'), Path('/home')),
        SubvolumeModification(Path('@log'), Path('/var/log')),
        SubvolumeModification(Path('@pkg'), Path('/var/cache/pacman/pkg')),
        SubvolumeModification(Path('@.snapshots'), Path('/.snapshots'))
    ]

    # Create the specified subvolumes
    for idx, subvol in enumerate(subvolumes):
        run_command(f"btrfs subvolume create /mnt{subvol.name}")
        stdscr.addstr(idx, 0, f"Created subvolume: {subvol.name}")

    # Unmount after creating subvolumes
    run_command("umount /mnt")
    stdscr.addstr(len(subvolumes), 0, "Subvolumes created successfully!")
    stdscr.getch()

def mount_file_system_curses(stdscr, drive):
    # Unmount /mnt before mounting the new system
    run_command("umount /mnt")

    run_command(f"mount -o compress=zstd,subvol=@ {drive} /mnt")
    stdscr.addstr(0, 0, "Mounted root filesystem.")


    stdscr.addstr(6, 0, "Filesystem mounted successfully!")
    stdscr.getch()

    # Encrypt the partition
    run_command(f"echo -n {passphrase} | cryptsetup luksFormat {drive} -")

    # Open the encrypted partition
    run_command(f"echo -n {passphrase} | cryptsetup open {drive} cryptroot -")

    return "/dev/mapper/cryptroot"  # Return the path to the opened encrypted partition


# Define the SubvolumeModification class outside of the function for clarity
class SubvolumeModification:
    def __init__(self, name, mount_point):
        self.name = name
        self.mount_point = mount_point


def configure_fstab():
    run_command("genfstab -U /mnt >> /mnt/etc/fstab")