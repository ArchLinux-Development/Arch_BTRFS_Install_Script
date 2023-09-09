import os
import subprocess


def has_uefi() -> bool:
    """Checks if the system supports UEFI."""
    return os.path.isdir('/sys/firmware/efi')


def _graphics_devices() -> list:
    """Lists all graphics devices using the lspci command."""
    lspci_output = subprocess.check_output(['lspci']).decode('utf-8')
    return [line for line in lspci_output.splitlines() if 'VGA' in line or '3D' in line]

def has_nvidia_graphics() -> bool:
    """Checks if the system has an NVIDIA graphics card."""
    return any('NVIDIA' in device for device in _graphics_devices())

def has_amd_graphics() -> bool:
    """Checks if the system has an AMD graphics card."""
    return any('AMD' in device for device in _graphics_devices())

def has_intel_graphics() -> bool:
    """Checks if the system has an Intel graphics card."""
    return any('Intel' in device for device in _graphics_devices())


def cpu_vendor() -> str:
    """Retrieves the CPU vendor information."""
    with open('/proc/cpuinfo', 'r') as f:
        for line in f:
            if line.startswith('vendor_id'):
                return line.split(':')[1].strip()
    return ''

def cpu_model() -> str:
    """Retrieves the CPU model information."""
    with open('/proc/cpuinfo', 'r') as f:
        for line in f:
            if line.startswith('model name'):
                return line.split(':')[1].strip()
    return ''


def mem_available() -> str:
    """Retrieves the available memory information."""
    with open('/proc/meminfo', 'r') as f:
        for line in f:
            if line.startswith('MemAvailable'):
                return line.split(':')[1].strip()
    return ''

def mem_free() -> str:
    """Retrieves the free memory information."""
    with open('/proc/meminfo', 'r') as f:
        for line in f:
            if line.startswith('MemFree'):
                return line.split(':')[1].strip()
    return ''

def mem_total() -> str:
    """Retrieves the total memory information."""
    with open('/proc/meminfo', 'r') as f:
        for line in f:
            if line.startswith('MemTotal'):
                return line.split(':')[1].strip()
    return ''


def virtualization() -> str:
    """Detects the type of virtualization, if any."""
    try:
        return subprocess.check_output(['systemd-detect-virt']).decode('utf-8').strip()
    except subprocess.CalledProcessError:
        return 'None'

def is_vm() -> bool:
    """Determines if the system is running inside a virtual machine."""
    virt_type = virtualization()
    return virt_type != 'None' and virt_type != 'none'


def requires_sof_fw() -> bool:
    """Checks if SOF (Sound Open Firmware) modules are loaded."""
    with open('/proc/modules', 'r') as f:
        for line in f:
            if 'snd_sof' in line:
                return True
    return False

def requires_alsa_fw() -> bool:
    """Checks if ALSA (Advanced Linux Sound Architecture) modules are loaded."""
    with open('/proc/modules', 'r') as f:
        for line in f:
            if 'snd_hda_intel' in line:
                return True
    return False


def has_wifi() -> bool:
    """Checks if any of the system's network interfaces support wireless connectivity."""
    try:
        interfaces = subprocess.check_output(['iwconfig'], stderr=subprocess.STDOUT).decode('utf-8')
        return 'no wireless extensions' not in interfaces
    except subprocess.CalledProcessError:
        return False
    

def sys_vendor() -> str:
    """Retrieves the system's vendor information."""
    with open('/sys/devices/virtual/dmi/id/sys_vendor', 'r') as f:
        return f.read().strip()

def product_name() -> str:
    """Retrieves the system's product name."""
    with open('/sys/devices/virtual/dmi/id/product_name', 'r') as f:
        return f.read().strip()


def loaded_modules() -> list:
    """Retrieves a list of all loaded kernel modules."""
    with open('/proc/modules', 'r') as f:
        return [line.split(' ')[0] for line in f.readlines()]
    
    