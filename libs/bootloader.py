# Standard library imports
import os
import subprocess
import re
import sys
import curses
import logging
from pathlib import Path

# Initialize logging
logging.basicConfig(level=logging.INFO)

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
        # Display error message if bootloader installation fails
        stdscr.addstr(0, 0, f"Error installing {bootloader_choice}: {str(e)}")
        stdscr.getch()
        return

def bootloader_menu(stdscr):
    """
    Display an interactive menu for the user to choose a bootloader.

    Parameters:
    - stdscr: the curses window object
    """
    bootloaders = ['GRUB', 'rEFInd', 'systemd-boot', 'Exit']  # Available bootloader options
    selected_idx = 0

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
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

        key = stdscr.getch()
        # Navigate the menu options
        if key == curses.KEY_UP and selected_idx > 0:
            selected_idx -= 1
        elif key == curses.KEY_DOWN and selected_idx < len(bootloaders) - 1:
            selected_idx += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            # Exit the menu or install the selected bootloader
            if bootloaders[selected_idx] == 'Exit':
                break
            else:
                install_bootloader(stdscr, bootloaders[selected_idx])

        stdscr.refresh()
