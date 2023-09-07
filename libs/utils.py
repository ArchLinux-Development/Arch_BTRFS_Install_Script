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


def handle_error(screen, message):
    """
    Display an error message using curses and log the error.
    """
    # Log the error
    logging.error(message)
    
    # Display the error message using curses
    screen.addstr(0, 0, "ERROR: " + message, curses.color_pair(2))
    screen.refresh()
    curses.napms(2000)  # Display the error for 2 seconds
    screen.clear()

# Used for network configuration
def run_command(command):
    return subprocess.run(command, shell=True, capture_output=True, text=True)


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


def is_inside_chroot():
    return os.stat("/") != os.stat("/proc/1/root/.")


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


def scan_wifi():
    try:
        result = subprocess.check_output(['iwlist', 'wlan0', 'scan'])
        result = result.decode('utf-8')
        ssids = [line.split(':')[1].strip() for line in result.split('\n') if "ESSID" in line]
        return ssids
    except:
        return []
    
def enable_services():
    run_command("systemctl enable NetworkManager")
    print("NetworkManager service enabled.")
    result = run_command("pacman -Qq | grep -q 'plasma-meta'")
    if result.returncode == 0:
        run_command("systemctl enable sddm")
        print("sddm service enabled for KDE.")


def setup_zram():
    ram_size = int(run_command(
        "grep MemTotal /proc/meminfo | awk '{print $2}'").stdout)
    zram_size = ram_size // 2
    run_command(f'echo "zram0" > /etc/modules-load.d/zram.conf')
    run_command(f'echo "options zram num_devices=1" > /etc/modprobe.d/zram.conf')
    run_command(
        f'echo \'KERNEL=="zram0", ATTR{{disksize}}="{zram_size}K",TAG+="systemd"\' > /etc/udev/rules.d/99-zram.rules')
    

def chroot_into_system():
    virt_check()  # Check for virtualization and install guest tools
    install_microcode()  # Check and install the appropriate microcode
    run_command("arch-chroot /mnt")

