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


# Initialize logging
logging.basicConfig(level=logging.INFO)

def run_command(command, log_file="install_log.txt"):
    result = subprocess.run(command, text=True, capture_output=True, shell=True)
    with open(log_file, "a") as f:
        f.write(result.stdout)
        f.write(result.stderr)
    if result.returncode != 0:
        print(f"Error executing: {command}")
        print(result.stderr)
        exit(1)


def clear():
    """Clear the terminal screen using subprocess."""
    subprocess.run(['clear'])


def install_filesystem_menu(stdscr):
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    menu_options = [
        "Choose Drive",
        "Format Partitions",
        "Create Subvolumes",
        "Mount File System",
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
            elif current_option == 4:
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


def is_inside_chroot():
    return os.stat("/") != os.stat("/proc/1/root/.")


def install_essential_packages():
    run_command("pacstrap /mnt base linux linux-firmware")


def configure_fstab():
    run_command("genfstab -U /mnt >> /mnt/etc/fstab")


def chroot_into_system():
    virt_check()  # Check for virtualization and install guest tools
    install_microcode()  # Check and install the appropriate microcode
    run_command("arch-chroot /mnt")


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


# Used for network configuration
def run_command(command):
    return subprocess.run(command, shell=True, capture_output=True, text=True)


def scan_wifi():
    try:
        result = subprocess.check_output(['iwlist', 'wlan0', 'scan'])
        result = result.decode('utf-8')
        ssids = [line.split(':')[1].strip() for line in result.split('\n') if "ESSID" in line]
        return ssids
    except:
        return []

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
            # Here you can handle the selected SSID, e.g., prompt for password and connect
            password = stdscr.getstr(h - 2, w // 4, "Enter password for {}: ".format(selected_ssid)).decode('utf-8')
            run_command(f"iwctl station wlan0 connect {selected_ssid} --passphrase {password}")
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
                result = run_command("ping -c 1 google.com")
                if result.returncode == 0:
                    stdscr.addstr(h - 2, w // 4, "You are connected to the internet.")
                else:
                    stdscr.addstr(h - 2, w // 4, "You are not connected to the internet. Please check your connection.")
                stdscr.getch()
            elif current_row == 3:
                return


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


def setup_zram():
    ram_size = int(run_command(
        "grep MemTotal /proc/meminfo | awk '{print $2}'").stdout)
    zram_size = ram_size // 2
    run_command(f'echo "zram0" > /etc/modules-load.d/zram.conf')
    run_command(f'echo "options zram num_devices=1" > /etc/modprobe.d/zram.conf')
    run_command(
        f'echo \'KERNEL=="zram0", ATTR{{disksize}}="{zram_size}K",TAG+="systemd"\' > /etc/udev/rules.d/99-zram.rules')


def enable_services():
    run_command("systemctl enable NetworkManager")
    print("NetworkManager service enabled.")
    result = run_command("pacman -Qq | grep -q 'plasma-meta'")
    if result.returncode == 0:
        run_command("systemctl enable sddm")
        print("sddm service enabled for KDE.")


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


def virt_check():
    hypervisor = run_command("systemd-detect-virt").stdout.strip()

    if hypervisor == "kvm":
        print("KVM has been detected, setting up guest tools.")
        run_command("pacstrap /mnt qemu-guest-agent")
        run_command("systemctl enable qemu-guest-agent --root=/mnt")
        
    elif hypervisor == "vmware":
        print("VMWare Workstation/ESXi has been detected, setting up guest tools.")
        run_command("pacstrap /mnt open-vm-tools")
        run_command("systemctl enable vmtoolsd --root=/mnt")
        run_command("systemctl enable vmware-vmblock-fuse --root=/mnt")
        
    elif hypervisor == "oracle":
        print("VirtualBox has been detected, setting up guest tools.")
        run_command("pacstrap /mnt virtualbox-guest-utils")
        run_command("systemctl enable vboxservice --root=/mnt")
        
    elif hypervisor == "microsoft":
        print("Hyper-V has been detected, setting up guest tools.")
        run_command("pacstrap /mnt hyperv")
        run_command("systemctl enable hv_fcopy_daemon --root=/mnt")
        run_command("systemctl enable hv_kvp_daemon --root=/mnt")
        run_command("systemctl enable hv_vss_daemon --root=/mnt")

    else:
        print(f"Unknown or no virtualization detected: {hypervisor}")


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

def is_strong_password(password):
    # Check password length
    if len(password) < 8:
        return False

    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False

    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False

    # Check for at least one number
    if not re.search(r'[0-9]', password):
        return False

    # Check for at least one special character
    special_characters = re.compile('[@_!#$%^&*()<>?/\\|}{~:]')
    if not special_characters.search(password):
        return False

    return True


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
                install_filesystem_menu(stdscr)
            elif current_row == 1:
                install_essential_packages()
            elif current_row == 2:
                configure_fstab()
            elif current_row == 3:
                chroot_into_system()
            elif current_row == 4:
                set_time_zone()
            elif current_row == 5:
                localization()
            elif current_row == 6:
                network_configuration(stdscr)
            elif current_row == 7:
                set_hostname()
            elif current_row == 8:
                set_root_password()
            elif current_row == 9:
                create_user()
            elif current_row == 10:
                kernel_selector(stdscr)
            elif current_row == 11:
                install_additional_packages(stdscr)
            elif current_row == 12:
                install_custom_packages()
            elif current_row == 13:
                install_desktop_environment(stdscr)
            elif current_row == 14:
                enable_necessary_services()
            elif current_row == 15:
                setup_zram()
            elif current_row == 16:
                configure_pacman_repositories()
            elif current_row == 17:
                setup_chaotic_aur()
            elif current_row == 18:
                setup_cachyos_repo()
            elif current_row == len(menu_items) - 1:
                break
        elif key == ord('q'):
            break

        stdscr.refresh()  # Refresh the screen

    stdscr.keypad(0)  # Disable special keys
    curses.endwin()

# To start the menu
if __name__ == "__main__":
    display_intro()  # Uncomment this if you have a display_intro function
    curses.wrapper(display_menu)
