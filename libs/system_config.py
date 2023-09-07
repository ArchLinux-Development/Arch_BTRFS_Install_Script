# Standard library imports
import os
import subprocess
import re
import sys
import curses
import logging
from pathlib import Path

from libs.utils import get_wifi_interface, is_strong_password, run_command, scan_wifi


def kernel_selector(stdscr):
    kernels = [
        "linux (Standard Arch Kernel)",
        "linux-lts (Long Term Support Kernel)",
        "linux-zen (Tuned for desktop performance)",
        "linux-hardened (Security-focused kernel)",
        "Return to main menu"
    ]
    current_row = 0

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # Draw title
        title = "Kernel Selector"
        stdscr.addstr(1, (w - len(title)) // 2, title)
        stdscr.addstr(2, (w - 25) // 2, "-" * 25)

        # Draw menu items
        for idx, item in enumerate(kernels):
            x = w // 4
            y = h // 4 + idx
            if idx == current_row:
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(y, x, item)
                stdscr.attroff(curses.A_REVERSE)
            else:
                stdscr.addstr(y, x, item)

        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(kernels) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:  # Enter key
            if current_row == 0:
                run_command("pacman -S linux linux-headers")
                stdscr.addstr(h - 2, (w - len("Standard Arch Kernel installed.")) // 2, "Standard Arch Kernel installed.")
            elif current_row == 1:
                run_command("pacman -S linux-lts linux-lts-headers")
                stdscr.addstr(h - 2, (w - len("Long Term Support Kernel installed.")) // 2, "Long Term Support Kernel installed.")
            elif current_row == 2:
                run_command("pacman -S linux-zen linux-zen-headers")
                stdscr.addstr(h - 2, (w - len("Zen Kernel installed.")) // 2, "Zen Kernel installed.")
            elif current_row == 3:
                run_command("pacman -S linux-hardened linux-hardened-headers")
                stdscr.addstr(h - 2, (w - len("Hardened Kernel installed.")) // 2, "Hardened Kernel installed.")
            elif current_row == 4:
                return
            stdscr.refresh()
            stdscr.getch()  # Wait for user input before returning to the menu

        stdscr.refresh()

def create_user():
    while True:
        username = input("Enter the desired username: ")

        # Check if the username already exists
        result = run_command(f"id {username}")
        if result.returncode == 0:
            print(f"The username {username} already exists. Please choose a different username.")
            continue

        # Set password for the new user
        while True:
            password = input(f"Enter password for {username}: ")
            confirm_password = input(f"Confirm password for {username}: ")

            if password != confirm_password:
                print("Passwords do not match. Please try again.")
                continue

            if not is_strong_password(password):
                print("Password is too weak. Please choose a stronger password.")
                print("A strong password contains at least 8 characters, a mix of upper and lower case letters, numbers, and special characters.")
                continue

            # Create the user and set the password
            run_command(f"useradd -m {username}")
            result = run_command(f'echo "{username}:{password}" | chpasswd')
            if result.returncode == 0:
                print(f"User {username} created successfully!")
                break
            else:
                print(f"Error setting password for {username}. Please try again.")
                continue

        break


def set_hostname():
    while True:
        hostname = input("Enter the desired hostname for your system: ")

        # Check if the hostname is valid
        if not is_valid_hostname(hostname):
            print("Invalid hostname. Please enter a valid hostname.")
            continue

        # Set the hostname
        result = run_command(f'echo "{hostname}" > /etc/hostname')
        if result.returncode == 0:
            print(f"Hostname set to {hostname} successfully!")
            break
        else:
            print(f"Error setting hostname to {hostname}. Please try again.")
            continue

def is_valid_hostname(hostname):
    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        hostname = hostname[:-1]  # strip exactly one dot from the right, if present
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


def set_root_password():
    while True:
        password = input("Enter the root password: ")
        confirm_password = input("Confirm the root password: ")

        if password != confirm_password:
            print("Passwords do not match. Please try again.")
            continue

        if not is_strong_password(password):
            print("Password is too weak. Please choose a stronger password.")
            print("A strong password contains at least 8 characters, a mix of upper and lower case letters, numbers, and special characters.")
            continue

        # Set the root password
        result = run_command(f'echo "root:{password}" | chpasswd')
        if result.returncode == 0:
            print("Root password set successfully!")
            break
        else:
            print("Error setting root password. Please try again.")


def install_microcode():
    # Detect the CPU vendor
    cpu_vendor = run_command("grep -m 1 'vendor_id' /proc/cpuinfo").stdout

    if "Intel" in cpu_vendor:
        print("Intel CPU detected. Installing intel-ucode...")
        run_command("pacman -S intel-ucode")
    elif "AMD" in cpu_vendor:
        print("AMD CPU detected. Installing amd-ucode...")
        run_command("pacman -S amd-ucode")
    else:
        print("Unknown CPU vendor. Skipping microcode installation.")


def install_desktop_environment(stdscr):
    environments = [
        "Install KDE Plasma",
        "Install GNOME",
        "Return to main menu"
    ]
    current_row = 0

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # Draw title
        title = "Desktop Environment Installation Menu"
        stdscr.addstr(1, (w - len(title)) // 2, title)

        # Draw menu items
        for idx, item in enumerate(environments):
            x = w // 4
            y = h // 4 + idx
            if idx == current_row:
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(y, x, item)
                stdscr.attroff(curses.A_REVERSE)
            else:
                stdscr.addstr(y, x, item)

        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(environments) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:  # Enter key
            if current_row == 0:
                install_kde_plasma()
                install_xorg_option(stdscr)
            elif current_row == 1:
                install_gnome()
                install_xorg_option(stdscr)
            elif current_row == 2:
                return

        stdscr.refresh()

def install_kde_plasma():
    run_command("pacman -S plasma-meta plasma-wayland-session kde-utilities kde-system dolphin-plugins sddm sddm-kcm kde-graphics ksysguard")

def install_gnome():
    run_command("pacman -S gnome gnome-extra gdm")

def install_xorg_option(stdscr):
    h, w = stdscr.getmaxyx()
    stdscr.clear()
    msg = "Do you want to install Xorg-related packages? (y/n): "
    stdscr.addstr(h // 2, (w - len(msg)) // 2, msg)
    stdscr.refresh()
    choice = stdscr.getch()
    if choice == ord('y'):
        run_command("pacman -S xorg-server xorg-apps")


def setup_chaotic_aur():
    print("Setting up Chaotic-AUR inside chroot environment...")
    if not is_inside_chroot():
        print("You are not inside the chroot environment. Please chroot into the system first.")
        return
    run_command(
        "pacman-key --recv-key 3056513887B78AEB --keyserver keyserver.ubuntu.com")
    run_command("pacman-key --lsign-key 3056513887B78AEB")
    run_command("pacman -U 'https://cdn-mirror.chaotic.cx/chaotic-aur/chaotic-keyring.pkg.tar.zst' 'https://cdn-mirror.chaotic.cx/chaotic-aur/chaotic-mirrorlist.pkg.tar.zst'")
    run_command(
        'echo -e "\n[chaotic-aur]\nInclude = /etc/pacman.d/chaotic-mirrorlist" >> /etc/pacman.conf')
    print("Chaotic-AUR setup complete!")


def setup_cachyos_repo():
    print("Setting up CachyOS repository inside chroot environment...")
    if not is_inside_chroot():
        print("You are not inside the chroot environment. Please chroot into the system first.")
        return
    run_command(
        "pacman-key --recv-keys F3B607488DB35A47 --keyserver keyserver.ubuntu.com")
    run_command("pacman-key --lsign-key F3B607488DB35A47")
    run_command("pacman -U 'https://mirror.cachyos.org/repo/x86_64/cachyos/cachyos-keyring-3-1-any.pkg.tar.zst' 'https://mirror.cachyos.org/repo/x86_64/cachyos/cachyos-mirrorlist-17-1-any.pkg.tar.zst' 'https://mirror.cachyos.org/repo/x86_64/cachyos/cachyos-v3-mirrorlist-17-1-any.pkg.tar.zst' 'https://mirror.cachyos.org/repo/x86_64/cachyos/cachyos-v4-mirrorlist-5-1-any.pkg.tar.zst' 'https://mirror.cachyos.org/repo/x86_64/cachyos/pacman-6.0.2-13-x86_64.pkg.tar.zst'")

    cpu_compatibility = run_command(
        "/lib/ld-linux-x86-64.so.2 --help | grep supported | grep x86-64-v4")
    if "supported, searched" in cpu_compatibility.stdout:
        run_command(
            'echo -e "\n[cachyos-v4]\nInclude = /etc/pacman.d/cachyos-v4-mirrorlist" >> /etc/pacman.conf')

    cpu_compatibility_v3 = run_command(
        "/lib/ld-linux-x86-64.so.2 --help | grep supported | grep x86-64-v3")
    if "supported, searched" in cpu_compatibility_v3.stdout:
        run_command(
            'echo -e "\n[cachyos-v3]\nInclude = /etc/pacman.d/cachyos-v3-mirrorlist" >> /etc/pacman.conf')
        run_command(
            'echo -e "\n[cachyos-core-v3]\nInclude = /etc/pacman.d/cachyos-v3-mirrorlist" >> /etc/pacman.conf')
        run_command(
            'echo -e "\n[cachyos-extra-v3]\nInclude = /etc/pacman.d/cachyos-v3-mirrorlist" >> /etc/pacman.conf')

    run_command(
        'echo -e "\n[cachyos]\nInclude = /etc/pacman.d/cachyos-mirrorlist" >> /etc/pacman.conf')
    print("CachyOS repository setup complete!")


def install_essential_packages():
    run_command("pacstrap /mnt base linux linux-firmware")


def install_additional_packages(stdscr):
    packages = [
        "btrfs-progs", "grub", "grub-btrfs", "rsync", "efibootmgr", 
        "snapper", "reflector", "snap-pac", "zram-generator", "sudo", 
        "micro", "git", "neofetch", "zsh", "man-db", "man-pages", 
        "texinfo", "samba", "chromium", "nano"
    ]
    selected_packages = packages.copy()  # All packages are selected by default

    curses.curs_set(0)
    stdscr.nodelay(0)
    stdscr.timeout(100)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    current_row = 0

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        for idx, package in enumerate(packages):
            x = w//2 - len(package)//2
            y = h//2 - len(packages)//2 + idx
            if idx == current_row:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, package)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, package)

            # Display an 'X' next to the package if it's selected
            if package in selected_packages:
                stdscr.addstr(y, x - 3, "[X]")
            else:
                stdscr.addstr(y, x - 3, "[ ]")

        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(packages)-1:
            current_row += 1
        elif key == ord(' '):  # Space bar to select/deselect a package
            if packages[current_row] in selected_packages:
                selected_packages.remove(packages[current_row])
            else:
                selected_packages.append(packages[current_row])
        elif key == ord('q'):  # Press 'q' to quit and install selected packages
            break

    # Install the selected packages
    if selected_packages:
        cmd = "pacman -S " + " ".join(selected_packages)
        run_command(cmd)


def install_custom_packages():
    packages = input(
        "Enter a space-separated list of additional packages you want to install: ")
    run_command(f"pacman -S {packages}")


def configure_pacman_repos():
    print("Available repositories:")
    print("1) multilib")
    print("2) multilib-testing")
    print("3) testing")
    choices = input(
        "Use space to select multiple repositories. Enter your choice (e.g. 1 3): ").split()
    for choice in choices:
        if choice == "1":
            run_command(
                "sed -i '/\[multilib\]/,/Include/s/^#//' /etc/pacman.conf")
        elif choice == "2":
            run_command(
                "sed -i '/\[multilib-testing\]/,/Include/s/^#//' /etc/pacman.conf")
        elif choice == "3":
            run_command(
                "sed -i '/\[testing\]/,/Include/s/^#//' /etc/pacman.conf")


def set_time_zone():
    # Get the current time zone
    current_timezone = run_command("timedatectl show --property=Timezone --value").stdout.strip()
    
    # Set the time zone based on the current setting
    run_command(f"ln -sf /usr/share/zoneinfo/{current_timezone} /etc/localtime")
    run_command("hwclock --systohc")


def localization():
    run_command('echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen')
    run_command("locale-gen")
    run_command('echo "LANG=en_US.UTF-8" > /etc/locale.conf')


def wifi_menu(stdscr):
    ssids = scan_wifi()
    if not ssids:
        stdscr.addstr(0, 0, "No Wi-Fi networks found or error in scanning.")
        stdscr.getch()
        return

    current_row = 0

    curses.curs_set(0)
    stdscr.keypad(1)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # Draw title
        title = "Available Wi-Fi Networks"
        stdscr.attron(curses.color_pair(2))
        stdscr.addstr(1, (w - len(title)) // 2, title)
        stdscr.attroff(curses.color_pair(2))

        # Draw SSIDs
        for idx, ssid in enumerate(ssids):
            x = w // 4
            y = h // 4 + idx
            if idx == current_row:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, ssid)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, ssid)

        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(ssids) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            selected_ssid = ssids[current_row]
            wifi_interface = get_wifi_interface()  # Automatically get Wi-Fi interface name
            password = stdscr.getstr(h - 2, w // 4, "Enter password for {}: ".format(selected_ssid)).decode('utf-8')
            result = run_command(f"iwctl station {wifi_interface} connect {selected_ssid} --passphrase {password}")
            
            if result.returncode != 0:
                stdscr.addstr(h - 3, w // 4, "Failed to connect to the Wi-Fi network. Please check the password and try again.")
            else:
                stdscr.addstr(h - 3, w // 4, f"Connected to {selected_ssid} successfully!")
            stdscr.getch()
            break


def network_configuration(stdscr):
    menu_items = ["Wired", "Wi-Fi", "Check current connection", "Return to main menu"]
    current_row = 0

    curses.curs_set(0)
    stdscr.keypad(1)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # Draw title
        title = "Network Configuration"
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

        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu_items) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_row == 0:
                stdscr.addstr(h - 2, w // 4, "Please ensure your ethernet cable is connected.")
                stdscr.getch()
            elif current_row == 1:
                wifi_menu(stdscr)
            elif current_row == 2:
                result = run_command("curl -Is http://www.google.com | head -n 1")
                if result and "HTTP/1.1 200 OK" in result.stdout:
                    stdscr.addstr(h - 2, w // 4, "You are connected to the internet.")
                else:
                    stdscr.addstr(h - 2, w // 4, "You are not connected to the internet. Please check your connection.")
                stdscr.getch()
            elif current_row == 3:
                return


