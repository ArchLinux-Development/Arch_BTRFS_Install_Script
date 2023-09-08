# Standard library imports
import os
import subprocess
import re
import sys
import curses
import logging
from pathlib import Path

# Initialize logging
logging.basicConfig(filename='bootloader.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def install_bootloader(stdscr, bootloader_choice):
    """
    Install and configure the specified bootloader.

    Parameters:
    - stdscr: the curses window object
    - bootloader_choice: the chosen bootloader (e.g., 'GRUB', 'rEFInd', 'systemd-boot')
    """
    try:
        if bootloader_choice == 'GRUB':
            # Install GRUB package
            subprocess.run(['pacman', '-S', 'grub', '--noconfirm'])
            # Install GRUB for EFI systems
            subprocess.run(['grub-install', '--target=x86_64-efi', '--efi-directory=/boot', '--bootloader-id=GRUB'])
            # Generate GRUB configuration file
            subprocess.run(['grub-mkconfig', '-o', '/boot/grub/grub.cfg'])
        elif bootloader_choice == 'rEFInd':
            # Install rEFInd package
            subprocess.run(['pacman', '-S', 'refind-efi', '--noconfirm'])
            # Install rEFInd bootloader
            subprocess.run(['refind-install'])
        elif bootloader_choice == 'systemd-boot':
            # Install and configure systemd-boot
            subprocess.run(['bootctl', '--path=/boot', 'install'])
    except Exception as e:
        logging.error(f"Error occurred while installing {bootloader_choice}: {str(e)}")
        # Display error message if bootloader installation fails
        stdscr.addstr(0, 0, f"Error installing {bootloader_choice}: {str(e)}")
        stdscr.getch()


def handle_input(stdscr, bootloaders, selected_idx):
    """
    Handle user input for the bootloader menu.

    Parameters:
    - stdscr: the curses window object
    - bootloaders: list of available bootloader options
    - selected_idx: index of the currently selected bootloader option

    Returns:
    - Tuple containing the updated selected index and a flag indicating if an option was selected
    """
    key = stdscr.getch()
    # Navigate the menu options
    if key == curses.KEY_UP and selected_idx > 0:
        selected_idx -= 1
    elif key == curses.KEY_DOWN and selected_idx < len(bootloaders) - 1:
        selected_idx += 1
    elif key == curses.KEY_ENTER or key in [10, 13]:
        return selected_idx, True
    return selected_idx, False


def render_menu(stdscr, bootloaders, selected_idx):
    """
    Render the bootloader options menu.

    Parameters:
    - stdscr: the curses window object
    - bootloaders: list of available bootloader options
    - selected_idx: index of the currently selected bootloader option
    """
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

    for idx, bootloader in enumerate(bootloaders):
        y = h // 2 - len(bootloaders) // 2 + idx
        x = w // 2 - len(bootloader) // 2
        # Highlight the currently selected bootloader option
        if idx == selected_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, bootloader)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, bootloader)
    stdscr.refresh()

# ... [rest of the functions]

def bootloader_menu(stdscr):
    """
    Display an interactive menu for the user to choose a bootloader.

    Parameters:
    - stdscr: the curses window object
    """
    # Initialize color pairs
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Selected menu item
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)   # Header/Footer
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)    # Top border
    curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Right border
    curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)   # Bottom border
    curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Left border

    bootloaders = ['GRUB', 'rEFInd', 'systemd-boot', 'Exit']  # Available bootloader options
    selected_idx = 0
    option_selected = False

    while not option_selected:
        render_menu(stdscr, bootloaders, selected_idx)
        selected_idx, option_selected = handle_input(stdscr, bootloaders, selected_idx)

    # Exit the menu or install the selected bootloader
    if bootloaders[selected_idx] != 'Exit':
        install_bootloader(stdscr, bootloaders[selected_idx])
