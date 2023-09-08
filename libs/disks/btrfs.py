import os
import logging
from pathlib import Path
from libs.utils import run_command

# Initialize logging
logging.basicConfig(filename='btrfs.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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

class SubvolumeModification:
    """Class to represent a Btrfs subvolume modification."""
    def __init__(self, name, mount_point):
        self.name = name
        self.mount_point = mount_point

def format_btrfs(stdscr, drive):
    """Format a drive with the Btrfs filesystem."""
    stdscr.addstr(6, 0, "Do you want to enable Btrfs compression? (y/n): ")
    choice = stdscr.getch()
    try:
        if choice == ord('y'):
            run_command(f"mkfs.btrfs -f --compress=zstd {drive}2")
        else:
            run_command(f"mkfs.btrfs -f {drive}2")
        stdscr.addstr(7, 0, "Partitions formatted successfully!")
    except Exception as e:
        logging.error(f"Error formatting drive: {str(e)}")
        stdscr.addstr(7, 0, f"Error formatting drive: {str(e)}")
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

def setup_zram(self, stdscr):
    """Setup ZRAM for swap on Btrfs filesystem."""
    # Determine the amount of RAM in the system
    total_memory = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
    zram_size = int(total_memory * 0.5)  # Using 50% of RAM for ZRAM

    # Load the zram module
    os.system("modprobe zram")

    # Create a zram device
    os.system(f"echo {zram_size} > /sys/block/zram0/disksize")

    # Format the zram device as swap
    os.system("mkswap /dev/zram0")

    # Enable the swap
    os.system("swapon /dev/zram0")

    # Add the zram swap to fstab to ensure it's available after reboot
    with open("/etc/fstab", "a") as fstab:
        fstab.write("/dev/zram0 none swap defaults 0 0\n")

    stdscr.addstr(0, 0, "ZRAM swap setup completed!")
    stdscr.getch()
