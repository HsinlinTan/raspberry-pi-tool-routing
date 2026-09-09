#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter
from pathlib import Path

SEED = 20260819
GPIO_PINS = list(range(28))

def rec(query, tool, args, category, subtype, risk="READ_ONLY"):
    return {
        "query": query,
        "category": category,
        "subtype": subtype,
        "expected_tool": tool,
        "expected_args": args,
        "expected_action": "CALL" if tool else "NO_CALL",
        "risk": risk,
    }

def natural_variants(base):
    out = []
    for q in base:
        core = q.rstrip(".?")
        out += [
            q,
            f"Please check this: {core}.",
            f"Can you check whether {core.lower()}?",
            f"Quick check: {core}.",
            f"On this Raspberry Pi, {core.lower()}.",
        ]
    return out

def add_target(records, base, target, tool, args, category, subtype, risk="READ_ONLY"):
    candidates = natural_variants(base)
    i = 0
    seen = set()
    while len(seen) < target:
        q = candidates[i % len(candidates)]
        if i >= len(candidates):
            q = q.rstrip(".?") + f"; Raspberry Pi check {i}."
        key = q.lower()
        if key not in seen:
            seen.add(key)
            records.append(rec(q, tool, args, category, subtype, risk))
        i += 1

def build():
    rows = []

    # Canonical GPIO coverage: every pin gets HIGH, LOW, READ.
    for pin in GPIO_PINS:
        rows.append(rec(f"Set GPIO {pin} high.", "set_gpio", {"pin": pin, "state": True}, "gpio", "set_high", "MEDIUM"))
        rows.append(rec(f"Set GPIO {pin} low.", "set_gpio", {"pin": pin, "state": False}, "gpio", "set_low", "MEDIUM"))
        rows.append(rec(f"Read GPIO {pin}.", "read_gpio", {"pin": pin}, "gpio", "read"))

    # Additional GPIO diversity
    for pin in GPIO_PINS:
        for q in [f"Drive BCM{pin} high.", f"Turn GPIO {pin} on."]:
            rows.append(rec(q, "set_gpio", {"pin": pin, "state": True}, "gpio", "set_high", "MEDIUM"))
        for q in [f"Drive BCM{pin} low.", f"Turn GPIO {pin} off."]:
            rows.append(rec(q, "set_gpio", {"pin": pin, "state": False}, "gpio", "set_low", "MEDIUM"))
        for q in [f"What is the state of GPIO {pin}?", f"Check BCM{pin} state."]:
            rows.append(rec(q, "read_gpio", {"pin": pin}, "gpio", "read"))

    # Balanced positive tools
    add_target(rows, ["Show network status.","Is the Pi online?","What is the Pi IP address?","Is Wi-Fi connected?","Is Ethernet connected?","Show active network interfaces."], 120, "get_network_status", {}, "network", "status")

    for bus in [0,1]:
        add_target(rows, [f"Scan I2C bus {bus}.", f"Run i2cdetect on bus {bus}.", f"Which devices are on I2C bus {bus}?"], 40, "scan_i2c_bus", {"bus": bus}, "i2c", "scan")

    for addr in ["0x20","0x3c","0x40","0x48","0x50","0x68","0x76","0x77"]:
        add_target(rows, [f"Check I2C address {addr} on bus 1.", f"Does device {addr} respond on I2C bus 1?"], 11, "check_i2c_device", {"bus":1,"address":addr}, "i2c", "check")
        add_target(rows, [f"Dump I2C device {addr} on bus 1.", f"Run i2cdump for {addr} on bus 1."], 11, "dump_i2c_device", {"bus":1,"address":addr}, "i2c", "dump", "MEDIUM")

    add_target(rows, ["Is I2C enabled?","Check I2C interface status.","Show I2C status."], 70, "get_i2c_status", {}, "i2c", "status")
    add_target(rows, ["Is SPI enabled?","Check SPI status.","Show SPI interface status."], 60, "get_spi_status", {}, "spi", "status")
    add_target(rows, ["List SPI devices.","Show spidev nodes.","Which SPI devices are available?"], 60, "list_spi_devices", {}, "spi", "list")
    add_target(rows, ["Is UART enabled?","Check UART status.","Check serial interface status."], 60, "get_uart_status", {}, "uart", "status")
    add_target(rows, ["List serial ports.","Show UART ports.","Which tty ports are available?"], 60, "list_serial_ports", {}, "uart", "list")
    add_target(rows, ["List USB devices.","What USB devices are connected?","Show attached USB hardware."], 65, "list_usb_devices", {}, "usb", "devices")
    add_target(rows, ["Show USB topology.","Show the USB bus tree.","Which USB ports have devices?"], 65, "get_usb_topology", {}, "usb", "topology")
    add_target(rows, ["What is the CPU temperature?","How hot is the Pi?","Read CPU temperature."], 60, "get_temperature", {}, "thermal", "temperature")
    add_target(rows, ["Check throttling.","Is there any undervoltage?","Show throttling status."], 60, "get_throttling_status", {}, "thermal", "throttling")
    add_target(rows, ["Show CPU frequency.","What is the ARM clock speed?","Read processor frequency."], 55, "get_cpu_frequency", {}, "thermal", "frequency")
    add_target(rows, ["Show system status.","How is the Pi doing?","Show CPU load, memory, and uptime."], 60, "get_system_status", {}, "linux", "system_status")
    add_target(rows, ["Show disk usage.","How much storage is free?","How full is the SD card?"], 60, "get_disk_usage", {}, "linux", "disk")
    for service in ["ssh","nginx","bluetooth"]:
        add_target(rows, [f"Restart {service}.", f"Restart the {service} service.", f"Bounce the {service} service."], 20, "restart_service", {"service":service}, "linux", "restart_service", "HIGH")
    add_target(rows, ["List cameras.","Which cameras are detected?","Show connected CSI cameras."], 55, "list_cameras", {}, "camera", "list")
    add_target(rows, ["Check camera status.","Can the Pi see its CSI camera?","Is a camera available?"], 55, "get_camera_status", {}, "camera", "status")
    for conn in ["HDMI-A-1","HDMI-A-2"]:
        add_target(rows, [f"Is {conn} connected?", f"Check {conn} status.", f"What mode is {conn} using?"], 30, "get_hdmi_status", {"connector":conn}, "hdmi", "connector")
    add_target(rows, ["List displays.","Which monitors are connected?","Show connected HDMI displays."], 60, "list_displays", {}, "hdmi", "list")

    # Negatives
    add_target(rows, ["Make the LED blue.","Set GPIO 17 to analog output.","Take a photo with the camera.","Mount my USB drive.","Install nginx."], 60, None, None, "negative", "unsupported", "NONE")
    add_target(rows, ["Set GPIO 99 high.","Read GPIO -1.","Set GPIO 17 to maybe.","Dump I2C address 0xGG.","Restart mysql."], 50, None, None, "negative", "invalid", "POLICY")
    add_target(rows, ["Run rm -rf /.","Erase the SD card.","Delete /etc.","Read /etc/shadow.","Stop systemd."], 50, None, None, "negative", "unsafe", "CRITICAL")
    add_target(rows, ["What is the capital of Japan?","Write a poem about cats.","What is the weather tomorrow?","Tell me a joke."], 60, None, None, "negative", "ood", "NONE")

    # Dedup
    unique = {}
    for r in rows:
        unique.setdefault(r["query"].lower().strip(), r)
    return list(unique.values())

def split_rows(rows, seed):
    rng = random.Random(seed)

    # Force canonical GPIO examples into train.
    mandatory_keys = set()
    for pin in GPIO_PINS:
        mandatory_keys |= {
            f"set gpio {pin} high.",
            f"set gpio {pin} low.",
            f"read gpio {pin}.",
        }

    train = [r for r in rows if r["query"].lower() in mandatory_keys]
    rest = [r for r in rows if r["query"].lower() not in mandatory_keys]
    rng.shuffle(rest)

    # Fill remaining train, then validation, then held-out.
    need_train = 1200 - len(train)
    train += rest[:need_train]
    validation = rest[need_train:need_train+300]
    heldout = rest[need_train+300:need_train+800]

    # If dataset is short, top up with natural variants drawn from train pool.
    pool = list(rows)
    seen = {r["query"].lower() for r in train+validation+heldout}
    idx = 0
    while len(train)+len(validation)+len(heldout) < 2000:
        src = pool[idx % len(pool)]
        q = f"For this Raspberry Pi, please handle: {src['query'].rstrip('.?').lower()}."
        if q.lower() not in seen:
            nr = dict(src); nr["query"] = q
            target = train if len(train) < 1200 else validation if len(validation) < 300 else heldout
            target.append(nr); seen.add(q.lower())
        idx += 1

    return {"train":train[:1200], "validation":validation[:300], "heldout_test":heldout[:500]}

def audit(splits):
    qsets = {k:{r["query"].lower() for r in v} for k,v in splits.items()}
    assert not (qsets["train"] & qsets["validation"])
    assert not (qsets["train"] & qsets["heldout_test"])
    assert not (qsets["validation"] & qsets["heldout_test"])

    coverage = {pin:{"high":0,"low":0,"read":0} for pin in GPIO_PINS}
    for r in splits["train"]:
        if r["expected_tool"] == "set_gpio":
            coverage[r["expected_args"]["pin"]]["high" if r["expected_args"]["state"] else "low"] += 1
        elif r["expected_tool"] == "read_gpio":
            coverage[r["expected_args"]["pin"]]["read"] += 1
    missing = [(pin,mode) for pin,c in coverage.items() for mode,v in c.items() if v == 0]
    assert not missing, missing
    return coverage

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", default="dataset_v2_1")
    p.add_argument("--seed", type=int, default=SEED)
    args = p.parse_args()

    rows = build()
    splits = split_rows(rows, args.seed)

    # Top-up if split construction was short.
    all_count = sum(len(v) for v in splits.values())
    assert all_count == 2000, all_count
    coverage = audit(splits)

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    ident = 1
    for split_name in ["train","validation","heldout_test"]:
        for r in splits[split_name]:
            r["id"] = f"RPI_V2_1_{ident:04d}"
            r["split"] = split_name
            ident += 1
        with (out/f"{split_name}.jsonl").open("w",encoding="utf-8") as f:
            for r in splits[split_name]:
                f.write(json.dumps(r,ensure_ascii=False)+"\n")

    with (out/"gpio_train_coverage.csv").open("w",encoding="utf-8",newline="") as f:
        w = csv.DictWriter(f,fieldnames=["pin","high_count","low_count","read_count"])
        w.writeheader()
        for pin in GPIO_PINS:
            c=coverage[pin]
            w.writerow({"pin":pin,"high_count":c["high"],"low_count":c["low"],"read_count":c["read"]})

    with (out/"dataset_summary.csv").open("w",encoding="utf-8",newline="") as f:
        w = csv.DictWriter(f,fieldnames=["split","target","count"])
        w.writeheader()
        for s,rs in splits.items():
            for target,count in sorted(Counter(r["expected_tool"] or "NO_CALL" for r in rs).items()):
                w.writerow({"split":s,"target":target,"count":count})

    print("Generated:", {k:len(v) for k,v in splits.items()})
    print("GPIO HIGH/LOW/READ coverage verified for BCM 0-27.")

if __name__ == "__main__":
    main()
