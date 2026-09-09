from __future__ import annotations
import glob, json, os, shutil, socket, subprocess
from pathlib import Path

def _run(cmd, timeout=10):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout).strip())
    return r.stdout.strip()

def execute_tool(tool, args):
    args = args or {}
    if tool == "get_temperature":
        raw = Path("/sys/class/thermal/thermal_zone0/temp").read_text().strip()
        return {"temperature_c": float(raw)/1000.0}
    if tool == "get_system_status":
        load = os.getloadavg()
        return {"loadavg_1m":load[0],"loadavg_5m":load[1],"loadavg_15m":load[2]}
    if tool == "get_disk_usage":
        u = shutil.disk_usage("/")
        return {"total_gb":u.total/2**30,"used_gb":u.used/2**30,"free_gb":u.free/2**30}
    if tool == "get_cpu_frequency":
        p = Path("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq")
        return {"frequency_mhz": float(p.read_text().strip())/1000.0}
    if tool == "get_i2c_status":
        return {"devices": sorted(glob.glob("/dev/i2c-*")), "enabled": bool(glob.glob("/dev/i2c-*"))}
    if tool == "scan_i2c_bus":
        return {"bus":args["bus"],"raw":_run(["i2cdetect","-y",str(args["bus"])])}
    if tool == "check_i2c_device":
        return {"bus":args["bus"],"address":args["address"],"raw":_run(["i2cget","-y",str(args["bus"]),args["address"]])}
    if tool == "dump_i2c_device":
        return {"bus":args["bus"],"address":args["address"],"raw":_run(["i2cdump","-y",str(args["bus"]),args["address"]])}
    if tool == "get_spi_status" or tool == "list_spi_devices":
        devs = sorted(glob.glob("/dev/spidev*"))
        return {"enabled":bool(devs),"devices":devs}
    if tool == "get_uart_status" or tool == "list_serial_ports":
        ports = sorted(glob.glob("/dev/ttyAMA*")+glob.glob("/dev/ttyS*")+glob.glob("/dev/ttyUSB*"))
        return {"enabled":bool(ports),"ports":ports}
    if tool == "list_usb_devices":
        return {"raw":_run(["lsusb"])}
    if tool == "get_usb_topology":
        return {"raw":_run(["lsusb","-t"])}
    if tool == "get_network_status":
        return {"hostname":socket.gethostname(),"raw":_run(["ip","-brief","addr"])}
    if tool == "list_displays":
        return {"displays":sorted(glob.glob("/sys/class/drm/*/status"))}
    if tool == "get_hdmi_status":
        matches = glob.glob(f"/sys/class/drm/*-{args['connector']}/status")
        return {"connector":args["connector"],"status":Path(matches[0]).read_text().strip() if matches else "unknown"}
    if tool == "list_cameras":
        return {"raw":_run(["rpicam-hello","--list-cameras"]) if shutil.which("rpicam-hello") else "rpicam-hello unavailable"}
    if tool == "get_camera_status":
        return {"available": bool(shutil.which("rpicam-hello"))}
    if tool == "get_throttling_status":
        if shutil.which("vcgencmd"):
            return {"raw":_run(["vcgencmd","get_throttled"])}
        return {"available":False}
    if tool == "read_gpio":
        return {"pin":args["pin"],"raw":_run(["pinctrl","get",str(args["pin"])])}
    if tool == "set_gpio":
        state = "op dh" if args["state"] else "op dl"
        return {"pin":args["pin"],"state":args["state"],"raw":_run(["pinctrl","set",str(args["pin"])]+state.split())}
    if tool == "restart_service":
        return {"service":args["service"],"raw":_run(["systemctl","restart",args["service"]])}
    raise ValueError(f"Unsupported executor: {tool}")
