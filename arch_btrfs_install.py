import os
import subprocess
import re


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


def run_command(cmd):
    return subprocess.run(cmd, shell=True, text=True, capture_output=True)


def clear_screen():
    os.system('clear')


def is_inside_chroot():
    return os.stat("/") != os.stat("/proc/1/root/.")


def choose_drive():
    while True:
        clear_screen()  # Clear the screen before displaying the menu
        drives = get_connected_drives()
        if not drives:
            print("No drives detected!")
            return None

        print("Available drives:")
        for idx, drive in enumerate(drives, 1):
            print(f"{idx}. {drive}")

        print(f"{len(drives) + 1}. Return to main menu")

        choice = input("Enter the number of the drive you want to install to or return to the main menu: ")
        if choice.isdigit() and 1 <= int(choice) <= len(drives):
            return drives[int(choice) - 1]
        elif choice == str(len(drives) + 1):
            return None
        else:
            print("Invalid choice. Please select a valid drive number or return to the main menu.")
            input("Press any key to continue...")


def get_connected_drives():
    result = run_command("lsblk -dpno NAME,SIZE,MODEL")
    lines = result.stdout.split("\n")
    drives = []
    for line in lines:
        if line:
            drives.append(line.strip())
    return drives


def setup_luks_encryption(drive):
    while True:
        passphrase = input("Enter a passphrase for LUKS encryption: ")
        if not is_strong_password(passphrase):
            print("Weak passphrase! Ensure it's at least 8 characters long, contains lowercase, uppercase, numbers, and special characters.")
            continue
        confirm_passphrase = input("Confirm passphrase: ")

        if passphrase != confirm_passphrase:
            print("Passphrases do not match!")
            continue
        break

    # Encrypt the partition
    run_command(f"echo -n {passphrase} | cryptsetup luksFormat {drive} -")

    # Open the encrypted partition
    run_command(f"echo -n {passphrase} | cryptsetup open {drive} cryptroot -")

    return "/dev/mapper/cryptroot"  # Return the path to the opened encrypted partition

def format_partitions(drive):
    if not drive:
        print("No drive selected!")
        return

    print(f"\nWARNING: You are about to format the drive {drive}.")
    print("All data on this drive will be permanently lost!")
    confirmation = input("Are you sure you want to proceed? (y/n): ")

    if confirmation.lower() != 'y':
        print("Operation cancelled.")
        return

    encrypt_choice = input("Do you want to enable LUKS encryption? (y/n): ")
    if encrypt_choice.lower() == "y":
        drive = setup_luks_encryption(drive)

    choice = input("Do you want to enable Btrfs compression? (y/n): ")
    if choice.lower() == "y":
        run_command(f"mkfs.btrfs -f --compress=zstd {drive}")
    else:
        run_command(f"mkfs.btrfs -f {drive}")


def create_subvolumes(drive):
    run_command(f"mount {drive} /mnt")
    run_command("btrfs subvolume create /mnt/@")
    run_command("btrfs subvolume create /mnt/@home")
    run_command("umount /mnt")


def mount_file_system(drive):
    run_command(f"mount -o compress=zstd,subvol=@ {drive} /mnt")
    run_command("mkdir /mnt/home")
    run_command(f"mount -o compress=zstd,subvol=@home {drive} /mnt/home")


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


def network_configuration():
    while True:
        clear_screen()  # Clear the screen before displaying the menu
        print("Network Configuration")
        print("-" * 25)
        print("Choose a network connection method:")
        print("1) Wired")
        print("2) Wi-Fi")
        print("3) Check current connection")
        print("4) Return to main menu")
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            # Assuming the wired connection will be managed by NetworkManager or dhcpcd
            print("Please ensure your ethernet cable is connected.")
            input("Press Enter to continue...")
            
        elif choice == "2":
            ssid = input("Enter the SSID of the Wi-Fi network: ")
            password = input("Enter the password for the Wi-Fi network: ")
            # Connect to the Wi-Fi network using iwctl
            run_command(f"iwctl station wlan0 connect {ssid} --passphrase {password}")
            
        elif choice == "3":
            result = run_command("ping -c 1 google.com")
            if result.returncode == 0:
                print("You are connected to the internet.")
            else:
                print("You are not connected to the internet. Please check your connection.")
                
        elif choice == "4":
            return
        else:
            print("Invalid choice!")


def install_additional_packages():
    run_command("pacman -S btrfs-progs grub grub-btrfs rsync efibootmgr snapper reflector snap-pac zram-generator sudo micro git neofetch zsh man-db man-pages texinfo samba chromium nano")


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

def install_desktop_environment():
    while True:
        clear_screen()
        print("Desktop Environment Installation Menu")
        print("1) Install KDE Plasma")
        print("2) Install GNOME")
        print("3) Return to main menu")
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            install_kde_plasma()
            install_xorg_option()
        elif choice == "2":
            install_gnome()
            install_xorg_option()
        elif choice == "3":
            return
        else:
            print("Invalid choice!")
        input("Press any key to return to the Desktop Environment Installation Menu...")

def install_kde_plasma():
    run_command("pacman -S plasma-meta plasma-wayland-session kde-utilities kde-system dolphin-plugins sddm sddm-kcm kde-graphics ksysguard")

def install_gnome():
    run_command("pacman -S gnome gnome-extra gdm")

def install_xorg_option():
    choice = input("Do you want to install Xorg-related packages? (y/n): ")
    if choice.lower() == "y":
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


def kernel_selector():
    while True:
        clear_screen()
        print("Kernel Selector")
        print("-" * 25)
        print("Choose a kernel:")
        print("1) linux (Standard Arch Kernel)")
        print("2) linux-lts (Long Term Support Kernel)")
        print("3) linux-zen (Tuned for desktop performance)")
        print("4) linux-hardened (Security-focused kernel)")
        print("5) Return to main menu")
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            run_command("pacman -S linux linux-headers")
            print("Standard Arch Kernel installed.")
            
        elif choice == "2":
            run_command("pacman -S linux-lts linux-lts-headers")
            print("Long Term Support Kernel installed.")
            
        elif choice == "3":
            run_command("pacman -S linux-zen linux-zen-headers")
            print("Zen Kernel installed.")
            
        elif choice == "4":
            run_command("pacman -S linux-hardened linux-hardened-headers")
            print("Hardened Kernel installed.")
            
        elif choice == "5":
            return
        else:
            print("Invalid choice!")
        input("Press any key to return to the kernel selector...")


def main():
    while True:
        clear_screen()
        print("Arch Linux Installation Menu")
        print("1) Choose drive")
        print("2) Format partitions")
        print("3) Create Btrfs subvolumes")
        print("4) Mount file system")
        print("5) Install essential packages")
        print("6) Configure fstab")
        print("7) Chroot into system")
        print("8) Set time zone")
        print("9) Localization")
        print("10) Set hostname")
        print("11) Network configuration")
        print("12) Kernel Selector")
        print("13) Set root password")
        print("14) Create a new user")
        print("15) Desktop Environment Installation")
        print("16) Install additional packages")
        print("17) Install custom packages")
        print("18) Enable necessary services")
        print("19) Setup zRAM")
        print("20) Configure pacman repositories")
        print("21) Setup Chaotic-AUR")
        print("22) Setup CachyOS Repository")
        print("23) Quit")
        choice = input("Enter your choice: ")

        if choice == "1":
            drive = choose_drive()
        elif choice == "2":
            format_partitions(drive)
        elif choice == "3":
            create_subvolumes(drive)
        elif choice == "4":
            mount_file_system(drive)
        elif choice == "5":
            install_essential_packages()
        elif choice == "6":
            configure_fstab()
        elif choice == "7":
            chroot_into_system()
        elif choice == "8":
            set_time_zone()
        elif choice == "9":
            localization()
        elif choice == "10":
            set_hostname()
        elif choice == "11":
            network_configuration()
        elif choice == "12":
            kernel_selector()
        elif choice == "13":
            set_root_password()
        elif choice == "14":
            create_user()
        elif choice == "15":
            install_desktop_environment()
        elif choice == "16":
            install_additional_packages()
        elif choice == "17":
            install_custom_packages()
        elif choice == "18":
            enable_services()
        elif choice == "19":
            setup_zram()
        elif choice == "20":
            configure_pacman_repos()
        elif choice == "21":
            setup_chaotic_aur()
        elif choice == "22":
            setup_cachyos_repo()
        elif choice == "23":
            print("Exiting...")
            break
        else:
            print("Invalid choice!")
        input("Press any key to return to the main menu...")



if __name__ == "__main__":
    display_intro()
    main()
