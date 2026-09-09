from __future__ import annotations
import re

def _pin(q):
    m = re.search(r"\b(?:gpio|bcm|pin)\s*[-#:]?\s*(\d{1,2})\b", q, re.I)
    return int(m.group(1)) if m else None

def _bus(q):
    m = re.search(r"\bbus\s*(\d+)\b", q, re.I)
    return int(m.group(1)) if m else None

def _addr(q):
    m = re.search(r"\b0x([0-9a-fA-F]{2})\b", q)
    return f"0x{m.group(1).lower()}" if m else None

def route(query):
    q = query.strip()
    pin = _pin(q)

    # GPIO
    if pin is not None and 0 <= pin <= 27:
        if re.search(r"\b(read|check|status|state|level|is)\b", q, re.I) and not re.search(r"\b(set|turn|drive|enable|disable|pull|switch)\b", q, re.I):
            return "read_gpio", {"pin":pin}, "explicit GPIO read"
        if re.search(r"\b(high|on|true|enable|enabled)\b", q, re.I):
            return "set_gpio", {"pin":pin,"state":True}, "explicit GPIO write"
        if re.search(r"\b(low|off|false|disable|disabled)\b", q, re.I):
            return "set_gpio", {"pin":pin,"state":False}, "explicit GPIO write"

    # I2C
    bus, addr = _bus(q), _addr(q)
    if re.search(r"\bi2c\b", q, re.I):
        if re.search(r"\bdump|i2cdump\b", q, re.I) and bus is not None and addr:
            return "dump_i2c_device", {"bus":bus,"address":addr}, "explicit I2C dump"
        if re.search(r"\bcheck|respond|device|address\b", q, re.I) and bus is not None and addr:
            return "check_i2c_device", {"bus":bus,"address":addr}, "explicit I2C device check"
        if re.search(r"\bscan|detect|i2cdetect\b", q, re.I) and bus is not None:
            return "scan_i2c_bus", {"bus":bus}, "explicit I2C scan"
        if re.search(r"\bstatus|enabled|available\b", q, re.I):
            return "get_i2c_status", {}, "I2C status"

    # SPI/UART/USB
    if re.search(r"\bspi\b", q, re.I):
        if re.search(r"\blist|devices|spidev|nodes\b", q, re.I): return "list_spi_devices", {}, "SPI list"
        return "get_spi_status", {}, "SPI status"
    if re.search(r"\b(uart|serial)\b", q, re.I):
        if re.search(r"\blist|ports|tty\b", q, re.I): return "list_serial_ports", {}, "serial list"
        return "get_uart_status", {}, "UART status"
    if re.search(r"\busb\b", q, re.I):
        if re.search(r"\b(topology|tree|ports?|hubs?)\b", q, re.I): return "get_usb_topology", {}, "USB topology"
        return "list_usb_devices", {}, "USB devices"

    # HDMI / camera
    m = re.search(r"\bHDMI-A-[12]\b", q, re.I)
    if m:
        return "get_hdmi_status", {"connector":m.group(0).upper()}, "HDMI connector"
    if re.search(r"\b(display|monitor)s?\b", q, re.I): return "list_displays", {}, "display list"
    if re.search(r"\bcamera", q, re.I):
        if re.search(r"\blist|which|detected|connected\b", q, re.I): return "list_cameras", {}, "camera list"
        return "get_camera_status", {}, "camera status"

    # Thermal/system/network/disk
    if re.search(r"\b(temperature|how hot|cpu temp|soc temp)\b", q, re.I): return "get_temperature", {}, "temperature"
    if re.search(r"\b(throttl|undervoltage|under-voltage|frequency cap|thermal limit)\b", q, re.I): return "get_throttling_status", {}, "throttling"
    if re.search(r"\b(cpu|arm|processor).*(frequency|clock)|\bfrequency\b", q, re.I): return "get_cpu_frequency", {}, "CPU frequency"
    if re.search(r"\b(network|wifi|wi-fi|ethernet|internet|ip address|interfaces?)\b", q, re.I): return "get_network_status", {}, "network"
    if re.search(r"\b(disk|storage|sd card|free space)\b", q, re.I): return "get_disk_usage", {}, "disk"
    if re.search(r"\b(system status|system health|cpu load|memory|uptime|how is the pi)\b", q, re.I): return "get_system_status", {}, "system"

    # Services
    sm = re.search(r"\b(?:restart|bounce)\s+(?:the\s+)?(ssh|nginx|bluetooth)(?:\s+service)?\b", q, re.I)
    if sm: return "restart_service", {"service":sm.group(1).lower()}, "service restart"

    return None, None, "no deterministic match"
