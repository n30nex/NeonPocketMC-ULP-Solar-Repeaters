#!/usr/bin/env python3
"""Static release contract for NeonPocketMC ULP Solar Repeaters."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX = {
    "neonpocket_ulp_heltec_v3",
    "neonpocket_ulp_heltec_v4",
    "neonpocket_ulp_rak4631",
    "neonpocket_ulp_rak3401_1w",
    "neonpocket_ulp_xiao_esp32s3",
    "neonpocket_ulp_rcc6_headless",
    "neonpocket_ulp_rcc6_tft",
    "neonpocket_ulp_rc52_headless",
    "neonpocket_ulp_rc52_tft",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> int:
    ini = (ROOT / "variants/neonpocket_ulp/platformio.ini").read_text(encoding="utf-8")
    actual = {
        line[len("[env:"):-1]
        for line in ini.splitlines()
        if line.startswith("[env:neonpocket_ulp_") and line.endswith("]")
    }
    require(actual == MATRIX, f"ULP matrix mismatch: expected {sorted(MATRIX)}, got {sorted(actual)}")
    require(ini.count("-D NEONPOCKET_ULP_SOLAR=1") == 1, "common ULP guard must be defined once")
    require("NV3001B_USE_INDEXED_FRAMEBUFFER=1" in ini, "TFT profiles must use indexed framebuffer")

    mesh = (ROOT / "examples/simple_repeater/MyMesh.cpp").read_text(encoding="utf-8")
    cli = (ROOT / "src/helpers/CommonCLI.cpp").read_text(encoding="utf-8")
    require("_prefs.powersaving_enabled = 1;" in mesh, "MCU saving must default on")
    require("_prefs.rxps.enabled = 1;" in mesh, "radio RX saving must default on")
    for command in ("ulp status", "ulp balanced", "ulp conservative", "ulp max", "ulp off"):
        require(f'"{command}"' in cli, f"missing CLI command {command}")

    for path in (
        "boards/heltec_rc52.json",
        "boards/heltec_rcc6.json",
        "variants/heltec_rc52/target.cpp",
        "variants/heltec_rcc6/target.cpp",
        "docs/EASYSKYMESH_ATTRIBUTION.md",
        "tools/configure_ulp.py",
    ):
        require((ROOT / path).is_file(), f"missing required file: {path}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for text in ("IoTThinks", "PowerSaving-v17", "power saving is ON by default", "external MPPT"):
        require(text.lower() in readme.lower(), f"README missing: {text}")
    print("Verified 9-profile NeonPocketMC ULP release contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
