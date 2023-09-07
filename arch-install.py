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


def display_menu(stdscr):
    menu_items = [
        "Install Filesystem", "Install essential packages", "Configure fstab",
        "Chroot into system", "Set time zone", "Localization", "Network configuration",
        "Set hostname", "Set root password", "Create a new user", "Kernel Selector",
        "Install additional packages", "Install custom packages", "Desktop Environment Installation",
        "Enable necessary services", "Setup zRAM", "Configure pacman repositories",
        "Setup Chaotic-AUR", "Setup CachyOS Repository", "Quit"
    ]
    current_row = 0

    curses.curs_set(0)
    stdscr.keypad(1)  # Enable special keys
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)

    while True:
        try:
            stdscr.clear()
            h, w = stdscr.getmaxyx()

            # Draw title
            title = "Arch Linux Installation Menu"
            stdscr.attron(curses.color_pair(2))
            stdscr.addstr(1, (w - len(title)) // 2, title)
            stdscr.attroff(curses.color_pair(2))

            # Draw menu items
            for idx, item in enumerate(menu_items):
                x = w // 4
                y = h // 4 + idx
                if idx == current_row:
                    stdscr.attron(curses.color_pair(1))
                    stdscr.addstr(y, x, item)
                    stdscr.attroff(curses.color_pair(1))
                else:
                    stdscr.addstr(y, x, item)

            # Draw footer
            footer = "Use arrow keys to navigate, Enter to select, and 'q' to quit."
            stdscr.addstr(h - 2, (w - len(footer)) // 2, footer)

            key = stdscr.getch()

            if key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(menu_items) - 1:
                current_row += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:  # Enter key
                if current_row == 0:
                    disk_operations.install_filesystem_menu(stdscr)
                elif current_row == 1:
                    system_config.install_essential_packages()
                elif current_row == 2:
                    disk_operations.configure_fstab()
                elif current_row == 3:
                    utils.chroot_into_system()
                elif current_row == 4:
                    system_config.set_time_zone()
                elif current_row == 5:
                    system_config.localization()
                elif current_row == 6:
                    system_config.network_configuration(stdscr)
                elif current_row == 7:
                    system_config.set_hostname()
                elif current_row == 8:
                    system_config.set_root_password()
                elif current_row == 9:
                    system_config.create_user()
                elif current_row == 10:
                    system_config.kernel_selector(stdscr)
                elif current_row == 11:
                    system_config.install_additional_packages(stdscr)
                elif current_row == 12:
                    system_config.install_custom_packages()
                elif current_row == 13:
                    system_config.install_desktop_environment(stdscr)
                elif current_row == 14:
                    system_config.enable_necessary_services()
                elif current_row == 15:
                    utils.setup_zram()
                elif current_row == 16:
                    system_config.configure_pacman_repositories()
                elif current_row == 17:
                    system_config.setup_chaotic_aur()
                elif current_row == 18:
                    system_config.setup_cachyos_repo()
                elif current_row == len(menu_items) - 1:
                    break
            elif key == ord('q'):
                break

        except OSError as e:
            utils.handle_error(stdscr, f"OS error: {str(e)}")
        except ValueError as e:
            utils.handle_error(stdscr, f"Value error: {str(e)}")

        stdscr.refresh()  # Refresh the screen

    stdscr.keypad(0)  # Disable special keys
    curses.endwin()


# To start the menu
if __name__ == "__main__":
    display_intro()  # Uncomment this if you have a display_intro function
    curses.wrapper(display_menu)
