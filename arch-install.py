# Standard library imports
import os
import subprocess
import re
import sys
import curses
import logging
from pathlib import Path

# Local application/library-specific imports
from libs import disk_operations, file_system_options
from libs import system_config
from libs import utils

# Setting up logging
logging.basicConfig(filename='menu.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def display_intro():
    """Display the introduction to the script."""
    os.system('clear')
    print("=" * 80)
    print(" " * 15 + "Arch BTRFS Installation Script By Eliminater74")
    print(" " * 25 + "Year: 2023")
    print("=" * 80)
    
    print("\nWelcome to the Arch Linux BTRFS Installation Helper!")
    print("This advanced script is designed to simplify the process of installing Arch Linux with BTRFS as the filesystem.")
    print("With a focus on user-friendliness and customization, it provides a seamless experience even for beginners.")
    
    display_features()
    display_guidelines()
    
    print("\nDisclaimer: Use this script at your own risk. Always ensure backups before making system changes.")
    input("\nPress Enter to proceed to the main menu...")

def display_features():
    """Display the features of the script."""
    features = [
        "Interactive drive selection from connected devices.",
        "LUKS encryption for enhanced security.",
        "Btrfs filesystem setup with optional compression.",
        "Creation and management of Btrfs subvolumes.",
        "Automatic mounting of the filesystem.",
        "Installation of essential and custom packages.",
        "Time zone and localization configuration.",
        "Network setup for both wired and Wi-Fi connections.",
        "Desktop environment installation options.",
        "zRAM setup for improved performance.",
        "Service management and activation.",
        "Pacman repository configuration.",
        "Integration of Chaotic-AUR and CachyOS Repository.",
        "Kernel selection based on user preference.",
        "User and root password management."
    ]
    print("\nKey Features:")
    for feature in features:
        print(f"- {feature}")

def display_guidelines():
    """Display the guidelines for using the script."""
    guidelines = [
        "Navigate using the numbers provided in the menu.",
        "Follow on-screen prompts carefully.",
        "Ensure a stable internet connection when required.",
        "Recommended to run from a Live Arch Linux environment.",
        "Backup crucial data before making changes to drives or partitions."
    ]
    print("\nInstructions:")
    for idx, guideline in enumerate(guidelines, 1):
        print(f"{idx}. {guideline}")


class Menu:
    def __init__(self):
        self.menu_items = [
            ("Install Filesystem", file_system_options.install_filesystem_menu),
            ("Install essential packages", system_config.install_essential_packages),
            ("Configure fstab", disk_operations.configure_fstab),
            ("Chroot into system", utils.chroot_into_system),
            ("Set time zone", system_config.set_time_zone),
            ("Localization", system_config.localization),
            ("Network configuration", system_config.network_configuration),
            ("Set hostname", system_config.set_hostname),
            ("Set root password", system_config.set_root_password),
            ("Create a new user", system_config.create_user),
            ("Kernel Selector", system_config.kernel_selector),
            ("Install additional packages", system_config.install_additional_packages),
            ("Install custom packages", system_config.install_custom_packages),
            ("Desktop Environment Installation", system_config.install_desktop_environment),
            ("Display Services Menu", utils.display_services_menu),
            ("Setup Chaotic-AUR", system_config.setup_chaotic_aur),
            ("Setup CachyOS Repository", system_config.setup_cachyos_repo),
            ("Quit", exit)
        ]
        self.current_row = 0

    def display(self, stdscr):
        """Display the main menu and handle user interactions."""
        curses.curs_set(0)
        stdscr.nodelay(1)
        stdscr.timeout(100)
        
        # Initialize color pairs
        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Selected menu item
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)   # Header/Footer
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Informational text
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)    # Top border
        curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Right border
        curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)   # Bottom border
        curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Left border

        title = "Arch BTRFS Installation Script"

        while True:
            stdscr.clear()
            
            # Draw multi-color border
            stdscr.hline(0, 0, curses.ACS_HLINE, curses.COLS - 1, curses.color_pair(4))  # Adjusted the length
            stdscr.vline(0, curses.COLS - 2, curses.ACS_VLINE, curses.LINES, curses.color_pair(5))
            stdscr.hline(curses.LINES - 1, 0, curses.ACS_HLINE, curses.COLS - 1, curses.color_pair(6))  # Adjusted the length
            stdscr.vline(0, 0, curses.ACS_VLINE, curses.LINES, curses.color_pair(7))

            # Adjusted corner drawing
            stdscr.addch(0, 0, curses.ACS_ULCORNER, curses.color_pair(4))
            stdscr.addch(0, curses.COLS - 2, curses.ACS_URCORNER, curses.color_pair(5))
            stdscr.addch(curses.LINES - 1, curses.COLS - 2, curses.ACS_LRCORNER, curses.color_pair(6))
            stdscr.addch(curses.LINES - 1, 0, curses.ACS_LLCORNER, curses.color_pair(7))

            # Draw centered title
            stdscr.addstr(0, (curses.COLS - len(title)) // 2, title, curses.color_pair(2))
            
            h, w = stdscr.getmaxyx()
            for idx, (item_name, _) in enumerate(self.menu_items):
                x = w // 2 - len(item_name) // 2
                y = h // 2 - len(self.menu_items) // 2 + idx
                if idx == self.current_row:
                    stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
                    stdscr.addstr(y, x, "--> " + item_name)
                    stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
                else:
                    stdscr.addstr(y, x, item_name)

            key = stdscr.getch()

            if key == curses.KEY_UP and self.current_row > 0:
                self.current_row -= 1
            elif key == curses.KEY_DOWN and self.current_row < len(self.menu_items) - 1:
                self.current_row += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:  # Enter key
                _, selected_function = self.menu_items[self.current_row]
                try:
                    if selected_function:
                        selected_function(stdscr)
                except Exception as e:
                    logging.error(f"Error occurred while executing function: {str(e)}")
                    # Display a user-friendly error message
                    error_message = f"An error occurred: {str(e)}"
                    stdscr.addstr(h // 2, w // 2 - len(error_message) // 2, error_message, curses.color_pair(1))
                    stdscr.refresh()
                    stdscr.getch()
                if self.current_row == len(self.menu_items) - 1:
                    break

            stdscr.refresh()

        stdscr.getch()

# To start the menu
if __name__ == "__main__":
    display_intro()
    menu = Menu()
    curses.wrapper(menu.display)
