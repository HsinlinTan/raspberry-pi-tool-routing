from __future__ import annotations

READ_ONLY = {
    "read_gpio","scan_i2c_bus","check_i2c_device","get_i2c_status",
    "get_spi_status","list_spi_devices","get_uart_status","list_serial_ports",
    "list_usb_devices","get_usb_topology","get_hdmi_status","list_displays",
    "list_cameras","get_camera_status","get_temperature","get_throttling_status",
    "get_cpu_frequency","get_network_status","get_system_status","get_disk_usage",
}
MEDIUM = {"set_gpio","dump_i2c_device"}
HIGH = {"restart_service"}

def classify_risk(tool):
    if tool is None: return "NONE"
    if tool in READ_ONLY: return "READ_ONLY"
    if tool in MEDIUM: return "MEDIUM"
    if tool in HIGH: return "HIGH"
    return "UNKNOWN"

def policy_decision(tool, arguments, execute=False):
    risk = classify_risk(tool)
    if tool is None:
        return {"action":"NO_ACTION","risk":risk,"reason":"No tool proposed."}
    if risk == "READ_ONLY":
        return {"action":"ALLOW","risk":risk,"reason":"Read-only tool."}
    if execute:
        return {"action":"ALLOW","risk":risk,"reason":"Explicit execution requested."}
    return {"action":"REJECT","risk":risk,"reason":"Write/high-risk operations are dry-run by default."}
