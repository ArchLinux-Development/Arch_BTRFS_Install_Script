# Standard library imports
import os
import subprocess
import re
import sys
import curses
import logging
from pathlib import Path

# Local application/library-specific imports
from libs import bootloader
from libs import disk_operations
from libs import system_config
from libs import utils

def display_intro():
    os.system('clear')
    print("=" * 80)
    print(" " * 15 + "Arch BTRFS Installation Script By Eliminater74")
    print(" " * 25 + "Year: 2023")
    print("=" * 80)
    
    print("\nWelcome to the Arch Linux BTRFS Installation Helper!")
    print("This advanced script is designed to simplify the process of installing Arch Linux with BTRFS as the filesystem.")
    print("With a focus on user-friendliness and customization, it provides a seamless experience even for beginners.")
    
    print("\nKey Features:")
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
    for feature in features:
        print(f"- {feature}")
    
    print("\nInstructions:")
    guidelines = [
        "Navigate using the numbers provided in the menu.",
        "Follow on-screen prompts carefully.",
        "Ensure a stable internet connection when required.",
        "Recommended to run from a Live Arch Linux environment.",
        "Backup crucial data before making changes to drives or partitions."
    ]
    for idx, guideline in enumerate(guidelines, 1):
        print(f"{idx}. {guideline}")
    
    print("\nDisclaimer: Use this script at your own risk. Always ensure backups before making system changes.")
    input("\nPress Enter to proceed to the main menu...")


import curses

def display_menu(stdscr):
    menu_items = {
        "Install Filesystem": disk_operations.install_filesystem_menu,
        "Install essential packages": system_config.install_essential_packages,
        "Configure fstab": disk_operations.configure_fstab,
        "Chroot into system": utils.chroot_into_system,
        "Set time zone": system_config.set_time_zone,
        "Localization": system_config.localization,
        "Network configuration": system_config.network_configuration,
        "Set hostname": system_config.set_hostname,
        "Set root password": system_config.set_root_password,
        "Create a new user": system_config.create_user,
        "Kernel Selector": system_config.kernel_selector,
        "Install additional packages": system_config.install_additional_packages,
        "Install custom packages": system_config.install_custom_packages,
        "Desktop Environment Installation": system_config.install_desktop_environment,
        "Display Services Menu": utils.display_services_menu,
        "Setup zRAM": utils.setup_zram,
        #"Configure pacman repositories": system_config.configure_pacman_repositories,
        "Setup Chaotic-AUR": system_config.setup_chaotic_aur,
        "Setup CachyOS Repository": system_config.setup_cachyos_repo,
        #"Install Bootloader": system_config.install_bootloader,
        #"Finish Installation": utils.finish_installation,
        "Quit": exit
    }

    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    current_row = 0

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        for idx, item in enumerate(menu_items.keys()):
            x = w // 2 - len(item) // 2
            y = h // 2 - len(menu_items) // 2 + idx
            if idx == current_row:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, item)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, item)

        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu_items) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:  # Enter key
            selected_function = menu_items.get(list(menu_items.keys())[current_row])
            if selected_function:
                selected_function(stdscr)
            elif current_row == len(menu_items) - 1:
                break

        stdscr.refresh()

    stdscr.getch()

# Assuming the other required functions and imports are present in your code.



# To start the menu
if __name__ == "__main__":
    display_intro()  # Uncomment this if you have a display_intro function
    curses.wrapper(display_menu)
