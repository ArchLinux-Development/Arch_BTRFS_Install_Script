# Standard library imports
import os
import shutil
import subprocess
import re
import sys
import curses
import logging
from pathlib import Path


# Initialize logging
logging.basicConfig(level=logging.INFO)

def run_command(command, log_file="install_log.txt"):
    """
    Executes a shell command and logs its output to a specified log file.
    
    Parameters:
    - command: The shell command to execute.
    - log_file: The file to which the command's output will be logged.
    
    Returns:
    - result: The result object containing stdout, stderr, and returncode.
    """
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
        
        # Log the command's output to the specified file
        with open(log_file, "a") as f:
            f.write(result.stdout)
            f.write(result.stderr)
        
        # If there's an error in the command execution, raise an exception
        if result.returncode != 0:
            raise Exception(f"Error executing: {command}\n{result.stderr}")
        
        return result
    except Exception as e:
        print(str(e))
        exit(1)


def clear():
    """Clears the terminal screen."""
    try:
        subprocess.run(['clear'])
    except Exception as e:
        print(f"Error clearing screen: {str(e)}")

def handle_error(screen, message):
    """
    Logs and displays an error message using the curses library.
    
    Parameters:
    - screen: The curses window object.
    - message: The error message to display.
    """
    # Log the error
    logging.error(message)
    
    # Display the error message using curses
    screen.addstr(0, 0, "ERROR: " + message, curses.color_pair(2))
    screen.refresh()
    curses.napms(2000)  # Display the error for 2 seconds
    screen.clear()

def is_strong_password(password):
    """
    Checks if a password meets certain strength criteria.
    
    Parameters:
    - password: The password string to check.
    
    Returns:
    - True if the password is strong, False otherwise.
    """
    # A strong password has at least 8 characters, contains both uppercase and lowercase characters, and has at least one digit.
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isupper() for char in password):
        return False
    if not any(char.islower() for char in password):
        return False
    return True

def is_inside_chroot():
    """
    Checks if the current environment is inside a chroot.
    
    Returns:
    - True if inside a chroot, False otherwise.
    """
    try:
        with open("/proc/1/sched", "r") as f:
            data = f.readline()
        return "[chroot]" in data
    except Exception as e:
        logging.error(f"Error checking chroot status: {str(e)}")
        return False

def virt_check():
    """
    Detects the virtualization platform and sets up the appropriate guest tools.
    """
    try:
        result = subprocess.run(['systemd-detect-virt'], text=True, capture_output=True)
        virtualization_type = result.stdout.strip()
        
        if virtualization_type == "vmware":
            subprocess.run(['pacman', '-S', 'open-vm-tools', '--noconfirm'])
        elif virtualization_type == "virtualbox":
            subprocess.run(['pacman', '-S', 'virtualbox-guest-utils', '--noconfirm'])
        # ... [Any other virtualization checks and setups]
    except Exception as e:
        logging.error(f"Error detecting virtualization platform: {str(e)}")


def get_wifi_interface():
    # Get the name of the Wi-Fi interface (e.g., wlan0, wlp3s0)
    result = run_command("iw dev | awk '$1==\"Interface\" {print $2}'")
    interface = result.stdout.strip()
    if not interface:
        return "wlan0"  # Default to wlan0 if not found
    return interface

def scan_wifi():
    """
    Scans for available Wi-Fi networks.
    
    Returns:
    - List of available Wi-Fi networks.
    """
    # Dynamically get the Wi-Fi interface name
    wifi_interface = get_wifi_interface()

    try:
        # Check if 'iw' command is available
        if shutil.which("iw") is None:
            raise Exception("'iw' command not found. Please install it to scan for Wi-Fi networks.")

        result = subprocess.run(['iw', 'dev', wifi_interface, 'scan'], text=True, capture_output=True)
        networks = re.findall(r"SSID: (.+)", result.stdout)
        return networks
    except Exception as e:
        logging.error(f"Error scanning for Wi-Fi networks: {str(e)}")
        return [f"Error: {str(e)}"]


def enable_services():
    """
    Enables certain system services based on installed packages.
    """
    try:
        # Check for installed packages and enable corresponding services
        if Path("/usr/bin/NetworkManager").exists():
            subprocess.run(['systemctl', 'enable', 'NetworkManager'])
        if Path("/usr/bin/sshd").exists():
            subprocess.run(['systemctl', 'enable', 'sshd'])
        # ... [Any other service checks and setups]
    except Exception as e:
        logging.error(f"Error enabling services: {str(e)}")
        

def chroot_into_system(script_path=None):
    """
    Checks for virtualization, installs the appropriate microcode, and then chroots into the system.
    
    Parameters:
    - script_path: Path to a script that will be executed inside the chroot environment.
    """
    try:
        virt_check()
        # Install appropriate microcode based on CPU vendor
        cpu_info = subprocess.run(['cat', '/proc/cpuinfo'], text=True, capture_output=True).stdout
        if "GenuineIntel" in cpu_info:
            subprocess.run(['pacman', '-S', 'intel-ucode', '--noconfirm'])
        elif "AuthenticAMD" in cpu_info:
            subprocess.run(['pacman', '-S', 'amd-ucode', '--noconfirm'])
        
        # Chroot into the system and optionally run a script
        if script_path:
            subprocess.run(['arch-chroot', '/mnt', 'bash', script_path])
        else:
            subprocess.run(['arch-chroot', '/mnt'])
    except Exception as e:
        logging.error(f"Error during chroot operation: {str(e)}")


def update_systemd_services(to_enable, to_disable):
    """
    Enables and disables the specified systemd services.
    
    Parameters:
    - to_enable: List of services to enable.
    - to_disable: List of services to disable.
    """
    for service in to_enable:
        subprocess.run(["systemctl", "enable", service], check=True)
    for service in to_disable:
        subprocess.run(["systemctl", "disable", service], check=True)

def get_systemd_services():
    command = "systemctl list-unit-files --type=service"
    result = subprocess.run(command, text=True, capture_output=True, shell=True)
    lines = result.stdout.splitlines()
    services = []
    for line in lines[1:-1]:  # Skip the header and footer lines
        parts = line.split(None, 1)
        if len(parts) == 2:
            service, status = parts
            services.append((service, status == "enabled"))
    return services

def toggle_service_status(services, index):
    service, status = services[index]
    services[index] = (service, not status)

def display_services_menu(stdscr):
    services = get_systemd_services()
    current_row = 0

    # Create a dictionary to store the original statuses of the services
    original_statuses = {service: status for service, status in services}

    # Get the height and width of the window
    height, width = stdscr.getmaxyx()

    while True:
        stdscr.clear()

        # Display the services and their status
        for i, (service, status) in enumerate(services):
            # Check if we're about to write outside the window boundaries
            if i >= height - 1:
                break

            if i == current_row:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(i, 0, f"  {service} {'[X]' if status else '[ ]'}")
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(i, 0, f"  {service} {'[X]' if status else '[ ]'}")

        # Capture user input
        key = stdscr.getch()

        # Navigate the menu
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(services) - 1:
            current_row += 1
        elif key == ord('e'):
            service_to_toggle = services[current_row][0]
            toggle_service_status(service_to_toggle)
            services = get_systemd_services()  # Refresh the list after toggling
        elif key == ord('q'):
            break

    # Reset the terminal settings
    curses.endwin()

    # Determine which services to enable and disable
    to_enable = []
    to_disable = []
    for service, status in services:
        if status and not original_statuses[service]:
            to_enable.append(service)
        elif not status and original_statuses[service]:
            to_disable.append(service)

    # Apply changes
    update_systemd_services(to_enable, to_disable)

