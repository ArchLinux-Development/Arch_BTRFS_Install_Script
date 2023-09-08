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

# Initialize logging
logging.basicConfig(filename='disk_operations.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class SubvolumeModification:
    """Class to represent a Btrfs subvolume modification."""
    def __init__(self, name, mount_point):
        self.name = name
        self.mount_point = mount_point

def confirm_formatting(stdscr, drive):
    """Prompt the user to confirm formatting a drive."""
    stdscr.addstr(1, 0, f"WARNING: You are about to format the drive {drive}.")
    stdscr.addstr(2, 0, "All data on this drive will be permanently lost!")
    stdscr.addstr(3, 0, "Are you sure you want to proceed? (y/n): ")
    confirmation = stdscr.getch()
    if confirmation != ord('y'):
        stdscr.addstr(4, 0, "Operation cancelled.")
        stdscr.getch()
        return False
    return True

def setup_encryption_choice(stdscr):
    """Prompt the user to choose whether to enable LUKS encryption."""
    stdscr.addstr(5, 0, "Do you want to enable LUKS encryption? (y/n): ")
    encrypt_choice = stdscr.getch()
    return encrypt_choice == ord('y')

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

def format_partitions_curses(stdscr, drive):
    if not drive:
        stdscr.addstr(0, 0, "No drive selected!")
        stdscr.getch()
        return

    if not confirm_formatting(stdscr, drive):
        return

    if setup_encryption_choice(stdscr):
        drive = setup_luks_encryption_curses(stdscr, drive)

    format_btrfs(stdscr, drive)

class FileSystemMenu:
    def __init__(self):
        self.menu_options = [
            ("Choose Drive", self.choose_drive),
            ("Format Partitions", self.format_partitions),
            ("Create Subvolumes", self.create_subvolumes),
            ("Mount File System", self.mount_file_system),
            ("Setup ZRAM", self.setup_zram),
            ("Install Bootloader", self.bootloader),
            ("Exit", self.exit_menu)
        ]
        self.current_option = 0
        self.drive = None

    def choose_drive(self, stdscr):
        self.drive = choose_drive_curses(stdscr)

    def format_partitions(self, stdscr):
        format_partitions_curses(stdscr, self.drive)

    def create_subvolumes(self, stdscr):
        create_subvolumes_curses(stdscr, self.drive)

    def mount_file_system(self, stdscr):
        mount_file_system_curses(stdscr, self.drive)

    def setup_zram(self, stdscr):
        setup_zram(self, stdscr)

    def bootloader(self, stdscr):
        bootloader_menu(stdscr)

    def exit_menu(self, stdscr):
        exit(0)

    def display(self, stdscr):
        # Initialize color pairs
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Selected menu item
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)   # Header/Footer
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)    # Top border
        curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Right border
        curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)   # Bottom border
        curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Left border

        while True:
            stdscr.clear()
            
            # Draw multi-color border
            stdscr.hline(0, 0, curses.ACS_HLINE, curses.COLS - 1, curses.color_pair(4))
            stdscr.vline(0, curses.COLS - 2, curses.ACS_VLINE, curses.LINES, curses.color_pair(5))
            stdscr.hline(curses.LINES - 1, 0, curses.ACS_HLINE, curses.COLS - 1, curses.color_pair(6))
            stdscr.vline(0, 0, curses.ACS_VLINE, curses.LINES, curses.color_pair(7))
            stdscr.addch(0, 0, curses.ACS_ULCORNER, curses.color_pair(4))
            stdscr.addch(0, curses.COLS - 2, curses.ACS_URCORNER, curses.color_pair(5))
            stdscr.addch(curses.LINES - 1, curses.COLS - 2, curses.ACS_LRCORNER, curses.color_pair(6))
            stdscr.addch(curses.LINES - 1, 0, curses.ACS_LLCORNER, curses.color_pair(7))
            
            h, w = stdscr.getmaxyx()
            for idx, (option, _) in enumerate(self.menu_options):
                x = w // 2 - len(option) // 2
                y = h // 2 - len(self.menu_options) // 2 + idx
                if idx == self.current_option:
                    stdscr.attron(curses.color_pair(1))
                    stdscr.addstr(y, x, option)
                    stdscr.attroff(curses.color_pair(1))
                else:
                    stdscr.addstr(y, x, option)

            key = stdscr.getch()
            if key == curses.KEY_UP and self.current_option > 0:
                self.current_option -= 1
            elif key == curses.KEY_DOWN and self.current_option < len(self.menu_options) - 1:
                self.current_option += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                _, selected_function = self.menu_options[self.current_option]
                selected_function(stdscr)

            stdscr.refresh()

# To start the menu
def install_filesystem_menu(stdscr):
    menu = FileSystemMenu()
    menu.display(stdscr)


def choose_drive_curses(stdscr):
    # Initialize color pairs
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Selected menu item
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)   # Header/Footer
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)    # Top border
    curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Right border
    curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)   # Bottom border
    curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Left border

    drives = get_connected_drives()
    current_option = 0

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # Draw multi-color border
        stdscr.hline(0, 0, curses.ACS_HLINE, curses.COLS - 1, curses.color_pair(4))
        stdscr.vline(0, curses.COLS - 2, curses.ACS_VLINE, curses.LINES, curses.color_pair(5))
        stdscr.hline(curses.LINES - 1, 0, curses.ACS_HLINE, curses.COLS - 1, curses.color_pair(6))
        stdscr.vline(0, 0, curses.ACS_VLINE, curses.LINES, curses.color_pair(7))
        stdscr.addch(0, 0, curses.ACS_ULCORNER, curses.color_pair(4))
        stdscr.addch(0, curses.COLS - 2, curses.ACS_URCORNER, curses.color_pair(5))
        stdscr.addch(curses.LINES - 1, curses.COLS - 2, curses.ACS_LRCORNER, curses.color_pair(6))
        stdscr.addch(curses.LINES - 1, 0, curses.ACS_LLCORNER, curses.color_pair(7))

        # Title
        title = "Choose a Drive"
        stdscr.addstr(0, (w - len(title)) // 2, title, curses.A_BOLD)

        # If no drives are detected
        if not drives:
            stdscr.addstr(2, (w - len("No drives detected!")) // 2, "No drives detected!")
            stdscr.getch()
            return None

        # Calculate the starting x-coordinate to center the drives
        max_drive_length = max([len(drive) for drive in drives])
        x_start = (w - max_drive_length) // 2

        # Display drives
        for idx, drive in enumerate(drives):
            y = 2 + idx

            if idx == current_option:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x_start, drive)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x_start, drive)

        # Add an option to return to the submenu
        return_option = "Return to submenu"
        x_return = (w - len(return_option)) // 2
        if current_option == len(drives):
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(2 + len(drives), x_return, return_option)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(2 + len(drives), x_return, return_option)

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
    """Generate the fstab file."""
    run_command("genfstab -U /mnt >> /mnt/etc/fstab")

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
