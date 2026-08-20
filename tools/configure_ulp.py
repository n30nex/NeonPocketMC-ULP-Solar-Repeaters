#!/usr/bin/env python3
"""Friendly USB setup wizard for NeonPocketMC ULP Solar Repeaters."""

from __future__ import annotations

import argparse
import getpass
import re
import sys
import time


BAUD = 115200
PRESETS = (
    ("USA / Canada", "910.525", "62.5", 7, 5),
    ("EU / UK", "869.618", "62.5", 8, 8),
    ("Australia", "915.800", "250", 10, 5),
    ("Australia narrow", "916.575", "62.5", 7, 8),
    ("New Zealand", "917.375", "250", 11, 5),
    ("New Zealand narrow", "917.375", "62.5", 7, 5),
    ("Brazil", "923.125", "62.5", 8, 8),
    ("EU 433 MHz", "433.650", "62.5", 8, 8),
)
PROFILES = (
    ("balanced", "Recommended: strong savings with pre-1.16 compatibility"),
    ("conservative", "More receive time; lower savings"),
    ("max", "Maximum duty cycling; may miss pre-1.16 nodes"),
    ("off", "Continuous receive and no MCU sleep"),
)


class SetupError(RuntimeError):
    pass


def ask_number(label: str, minimum: int, maximum: int, default: int) -> int:
    while True:
        raw = input(f"{label} [{default}]: ").strip()
        if not raw:
            return default
        if raw.isdigit() and minimum <= int(raw) <= maximum:
            return int(raw)
        print(f"Enter a number from {minimum} to {maximum}.")


def ask_text(label: str, default: str, maximum: int) -> str:
    while True:
        value = input(f"{label} [{default}]: ").strip() or default
        if value and len(value.encode("utf-8")) <= maximum and not any(c in value for c in "[]\\:,?*"):
            return value
        print(f"Use 1-{maximum} bytes and avoid []\\:,?*.")


def choose_port(requested: str | None) -> str:
    if requested:
        return requested
    try:
        from serial.tools import list_ports
    except ImportError as exc:
        raise SetupError("PySerial is missing. Use the supplied Windows or Linux launcher.") from exc
    ports = sorted(list_ports.comports(), key=lambda item: item.device.lower())
    if not ports:
        raise SetupError("No serial device found. Connect the repeater with a USB data cable.")
    if len(ports) == 1:
        print(f"Found {ports[0].device}: {ports[0].description}")
        return ports[0].device
    print("Connected serial devices:")
    for index, port in enumerate(ports, 1):
        print(f"  {index}. {port.device} — {port.description}")
    return ports[ask_number("Choose the repeater", 1, len(ports), 1) - 1].device


class Device:
    def __init__(self, port: str):
        try:
            import serial
            self.serial = serial.Serial()
            self.serial.port = port
            self.serial.baudrate = BAUD
            self.serial.timeout = 0.08
            self.serial.write_timeout = 2
            self.serial.dtr = False
            self.serial.rts = False
            self.serial.open()
        except Exception as exc:
            raise SetupError(f"Could not open {port}: {exc}") from exc
        time.sleep(1.0)
        self.serial.reset_input_buffer()

    def close(self) -> None:
        if self.serial.is_open:
            self.serial.close()

    def command(self, command: str, secret: bool = False, timeout: float = 4.0) -> str:
        label = command.split(" ", 1)[0] + " ********" if secret else command
        print(f"  {label:<48}", end="", flush=True)
        self.serial.reset_input_buffer()
        self.serial.write((command + "\r").encode())
        self.serial.flush()
        data = bytearray()
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            chunk = self.serial.read(max(1, self.serial.in_waiting))
            if chunk:
                data.extend(chunk)
                replies = re.findall(r"(?:^|[\r\n])\s*->\s*([^\r\n]+)", data.decode(errors="replace"))
                if replies:
                    reply = replies[-1].strip()
                    if reply.lower().startswith(("err", "error", "unknown", "??")):
                        print("FAILED")
                        raise SetupError(f"Device rejected '{label}': {reply}")
                    print("OK")
                    return reply
            time.sleep(0.03)
        print("NO REPLY")
        raise SetupError(f"Device did not answer '{label}'.")


def self_test() -> None:
    assert len(PRESETS) >= 8
    assert [p[0] for p in PROFILES] == ["balanced", "conservative", "max", "off"]
    print("ULP configurator self-test passed")


def run(port: str | None) -> None:
    print("\nNeonPocketMC ULP Solar Repeater setup\n")
    device = Device(choose_port(port))
    try:
        version = device.command("ver")
        board = device.command("board")
        if "neonpocket-ulp" not in version.lower():
            raise SetupError(f"Refusing this device: '{version}' is not NeonPocket ULP firmware.")
        print(f"\nVerified {board}\n")

        name = ask_text("Repeater name", "NeonPocket ULP", 31)
        print("\nRadio preset:")
        for index, preset in enumerate(PRESETS, 1):
            print(f"  {index}. {preset[0]}")
        preset = PRESETS[ask_number("Choose your region", 1, len(PRESETS), 1) - 1]
        tx = ask_number("Transmit power in dBm", 2, 22, 20)

        print("\nPower profile:")
        for index, profile in enumerate(PROFILES, 1):
            print(f"  {index}. {profile[0]} — {profile[1]}")
        profile = PROFILES[ask_number("Choose a profile", 1, len(PROFILES), 1) - 1][0]

        while True:
            password = getpass.getpass("New admin password (8-15 characters): ")
            if 8 <= len(password) <= 15 and password == getpass.getpass("Confirm password: "):
                break
            print("Passwords must match and be 8-15 characters.")

        print("\nApplying settings:")
        device.command(f"set name {name}")
        device.command(f"set radio {preset[1]},{preset[2]},{preset[3]},{preset[4]}")
        device.command(f"set tx {tx}")
        device.command(f"ulp {profile}")
        device.command(f"password {password}", secret=True)
        device.command("advert")
        print("\nSetup complete. Restart once, keep the antenna attached, then deploy.")
    finally:
        device.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", help="Serial port, for example COM21 or /dev/ttyACM0")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        if args.self_test:
            self_test()
        else:
            run(args.port)
        return 0
    except (SetupError, KeyboardInterrupt) as exc:
        print(f"\nStopped: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
