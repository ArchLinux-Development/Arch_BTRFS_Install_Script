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
    try:
        if bootloader_choice == 'GRUB':
            # Install and configure GRUB
            subprocess.run(['pacman', '-S', 'grub', '--noconfirm'])
            subprocess.run(['grub-install', '--target=x86_64-efi', '--efi-directory=/boot', '--bootloader-id=GRUB'])
            subprocess.run(['grub-mkconfig', '-o', '/boot/grub/grub.cfg'])
        elif bootloader_choice == 'rEFInd':
            # Install and configure rEFInd
            subprocess.run(['pacman', '-S', 'refind-efi', '--noconfirm'])
            subprocess.run(['refind-install'])
        elif bootloader_choice == 'systemd-boot':
            # Install and configure systemd-boot
            subprocess.run(['bootctl', '--path=/boot', 'install'])
    except Exception as e:
        stdscr.addstr(0, 0, f"Error installing {bootloader_choice}: {str(e)}")
        stdscr.getch()
        return

def bootloader_menu(stdscr):
    bootloaders = ['GRUB', 'rEFInd', 'systemd-boot', 'Exit']  # Added 'Exit' option
    selected_idx = 0

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        for idx, bootloader in enumerate(bootloaders):
            y = h // 2 - len(bootloaders) // 2 + idx
            x = w // 2 - len(bootloader) // 2
            if idx == selected_idx:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, bootloader)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, bootloader)

        key = stdscr.getch()
        if key == curses.KEY_UP and selected_idx > 0:
            selected_idx -= 1
        elif key == curses.KEY_DOWN and selected_idx < len(bootloaders) - 1:
            selected_idx += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if bootloaders[selected_idx] == 'Exit':  # Handle 'Exit' option
                break
            else:
                install_bootloader(stdscr, bootloaders[selected_idx])

        stdscr.refresh()
