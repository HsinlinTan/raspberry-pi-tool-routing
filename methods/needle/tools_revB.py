"""
NeedleGuard Phase 1B - Schema Revision B

Short, discriminative tool descriptions for Needle 2.

RevA showed that long descriptions improved some tool-selection results but
greatly increased latency and argument errors. RevB therefore keeps only the
minimum vocabulary needed to distinguish neighboring tools.

Tool names, argument types, return values, and benchmark tool groups are kept
compatible with Benchmark v1.
"""

from typing import Literal

import needle


# ---------------------------------------------------------------------------
# Shared argument types
# ---------------------------------------------------------------------------

GPIOPin = Literal[
    0, 1, 2, 3, 4, 5, 6, 7,
    8, 9, 10, 11, 12, 13, 14, 15,
    16, 17, 18, 19, 20, 21, 22, 23,
    24, 25, 26, 27,
]

I2CBus = Literal[0, 1]

HDMIConnector = Literal[
    "HDMI-A-1",
    "HDMI-A-2",
]

AllowedService = Literal[
    "ssh",
    "nginx",
    "bluetooth",
]


# ---------------------------------------------------------------------------
# GPIO
# ---------------------------------------------------------------------------

@needle.tool
def set_gpio(pin: GPIOPin, state: bool):
    """Set BCM GPIO pin state. HIGH/on=True; LOW/off=False."""
    return {
        "pin": pin,
        "state": state,
    }


@needle.tool
def read_gpio(pin: GPIOPin):
    """Read HIGH/LOW state of one BCM GPIO pin."""
    return {
        "pin": pin,
        "state": False,
    }


# ---------------------------------------------------------------------------
# I2C
# ---------------------------------------------------------------------------

@needle.tool
def scan_i2c_bus(bus: I2CBus):
    """Scan an entire I2C bus for devices; i2cdetect-style scan."""
    return {
        "bus": bus,
        "devices": [],
    }


@needle.tool
def check_i2c_device(bus: I2CBus, address: str):
    """Check whether one specific I2C address responds."""
    return {
        "bus": bus,
        "address": address,
        "present": False,
    }


@needle.tool
def dump_i2c_device(bus: I2CBus, address: str):
    """Dump registers from one I2C device; i2cdump-style read."""
    return {
        "bus": bus,
        "address": address,
        "registers": {},
    }


@needle.tool
def get_i2c_status():
    """Check whether the I2C interface is enabled/available."""
    return {
        "enabled": True,
    }


# ---------------------------------------------------------------------------
# SPI
# ---------------------------------------------------------------------------

@needle.tool
def get_spi_status():
    """Check whether the SPI interface is enabled/available."""
    return {
        "enabled": True,
    }


@needle.tool
def list_spi_devices():
    """List SPI/spidev device nodes."""
    return {
        "devices": [],
    }


# ---------------------------------------------------------------------------
# UART / serial
# ---------------------------------------------------------------------------

@needle.tool
def get_uart_status():
    """Check whether UART/serial interface is enabled/available."""
    return {
        "enabled": True,
    }


@needle.tool
def list_serial_ports():
    """List UART/serial ports such as ttyAMA, ttyS, or ttyUSB."""
    return {
        "ports": [],
    }


# ---------------------------------------------------------------------------
# USB
# ---------------------------------------------------------------------------

@needle.tool
def list_usb_devices():
    """List WHAT USB devices are connected."""
    return {
        "devices": [],
    }


@needle.tool
def get_usb_topology():
    """Show WHERE USB devices connect: buses, hubs, ports, and tree."""
    return {
        "tree": [],
    }


# ---------------------------------------------------------------------------
# HDMI / display
# ---------------------------------------------------------------------------

@needle.tool
def get_hdmi_status(connector: HDMIConnector):
    """Read status/mode of HDMI-A-1 or HDMI-A-2 connector."""
    return {
        "connector": connector,
        "connected": False,
        "mode": None,
    }


@needle.tool
def list_displays():
    """List connected HDMI displays/monitors."""
    return {
        "displays": [],
    }


# ---------------------------------------------------------------------------
# Camera
# ---------------------------------------------------------------------------

@needle.tool
def list_cameras():
    """List detected Raspberry Pi CSI/libcamera cameras."""
    return {
        "cameras": [],
    }


@needle.tool
def get_camera_status():
    """Check whether a Raspberry Pi CSI/libcamera camera is available."""
    return {
        "available": False,
    }


# ---------------------------------------------------------------------------
# Thermal / CPU
# ---------------------------------------------------------------------------

@needle.tool
def get_temperature():
    """Read Raspberry Pi CPU/SoC temperature; Pi temp or how hot the Pi is."""
    return {
        "temperature_c": 50.0,
    }


@needle.tool
def get_throttling_status():
    """Read throttling, undervoltage, frequency-cap, and thermal-limit status."""
    return {
        "currently_throttled": False,
        "undervoltage": False,
        "frequency_capped": False,
        "thermal_limit": False,
    }


@needle.tool
def get_cpu_frequency():
    """Read Raspberry Pi CPU/ARM clock frequency in MHz."""
    return {
        "frequency_mhz": 1500,
    }


# ---------------------------------------------------------------------------
# Linux / system
# ---------------------------------------------------------------------------

@needle.tool
def get_network_status():
    """Read NETWORK status: Wi-Fi, Ethernet, online state, interface, and IP."""
    return {
        "connected": True,
        "interface": "eth0",
        "ip": "192.168.1.100",
    }


@needle.tool
def get_system_status():
    """Read GENERAL system health: CPU load, memory use, and uptime."""
    return {
        "cpu_percent": 20,
        "memory_percent": 35,
        "uptime_seconds": 3600,
    }


@needle.tool
def get_disk_usage():
    """Read DISK/SD-card storage usage and free space."""
    return {
        "used_percent": 50,
        "free_gb": 10.0,
    }


@needle.tool
def restart_service(service: AllowedService):
    """Restart allowlisted service: ssh, nginx, or bluetooth."""
    return {
        "success": True,
        "service": service,
    }


# ---------------------------------------------------------------------------
# Benchmark tool groups
# ---------------------------------------------------------------------------

CORE5_TOOLS = [
    get_network_status,
    get_system_status,
    get_disk_usage,
    restart_service,
    get_temperature,
]


LEVEL10_TOOLS = CORE5_TOOLS + [
    get_throttling_status,
    get_cpu_frequency,
    list_usb_devices,
    get_usb_topology,
    get_camera_status,
]


FULL_TOOLS = [
    # GPIO
    set_gpio,
    read_gpio,

    # I2C
    scan_i2c_bus,
    check_i2c_device,
    dump_i2c_device,
    get_i2c_status,

    # SPI
    get_spi_status,
    list_spi_devices,

    # UART
    get_uart_status,
    list_serial_ports,

    # USB
    list_usb_devices,
    get_usb_topology,

    # HDMI / display
    get_hdmi_status,
    list_displays,

    # Camera
    list_cameras,
    get_camera_status,

    # Thermal / CPU
    get_temperature,
    get_throttling_status,
    get_cpu_frequency,

    # Linux / system
    get_network_status,
    get_system_status,
    get_disk_usage,
    restart_service,
]
