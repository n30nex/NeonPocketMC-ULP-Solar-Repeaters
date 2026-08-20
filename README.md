<p align="center">
  <img src="https://raw.githubusercontent.com/n30nex/NeonPocketMC/main/branding/neonpocketmc-mark.png" width="180" alt="NeonPocketMC logo">
</p>

# NeonPocketMC ULP Solar Repeaters

Experimental, low-power MeshCore repeaters for solar and battery deployments.

This firmware is built from [IoTThinks' PowerSaving-v17 MeshCore fork](https://github.com/IoTThinks/MeshCore/tree/PowerSaving-v17), with the power-saving work fully attributed in [docs/EASYSKYMESH_ATTRIBUTION.md](docs/EASYSKYMESH_ATTRIBUTION.md). It tracks MeshCore 1.17.1 and adds NeonPocketMC hardware profiles, default-on setup, a simpler `ulp` command, TFT support for RCC6/RC52, packaging, and a guided USB configurator.

> **Experimental.** RX duty cycling saves power by intentionally spending part of each interval asleep. A ULP repeater can miss packets that a continuously listening repeater would receive. Test coverage and current draw at the actual deployment site before relying on it.

## Builds

| Release build | Hardware | Display |
|---|---|---|
| Heltec V3 | WiFi LoRa 32 V3 / SX1262 | Built-in OLED |
| Heltec V4 | WiFi LoRa 32 V4 / SX1262 | Built-in OLED |
| RAK4631 | WisBlock Core RAK4631 / SX1262 | Optional SSD1306 |
| RAK3401 1W | RAK3401 + RAK13302/SKY66122 | Optional SSD1306 |
| Xiao ESP32-S3 | Seeed Xiao ESP32-S3 + supported SX1262 wiring | Headless |
| Xiao nRF52840 | Seeed Xiao nRF52840 + supported SX1262 wiring | Headless / null display |
| RCC6 Headless | Heltec RadioCore RCC6-L62 | TFT held off |
| RCC6 TFT | RCC6-L62 + NV3001B 220×128 | Indexed framebuffer; auto-off |
| RC52 Headless | Heltec RadioCore RC52-L62 | TFT held off |
| RC52 TFT | RC52-L62 + NV3001B 220×128 | Indexed framebuffer; auto-off |

**Hardware warning:** these boards do not all accept an unregulated solar panel. Use a protected battery and an external MPPT/solar charge controller matched to the panel and cell. Never connect a raw panel directly to VBAT or USB.

## Default power behavior

For a new installation, **power saving is ON by default**:

- MCU light sleep is enabled after the existing two-minute startup window on ESP32 and whenever idle on nRF52.
- SX1262 radio RX duty cycling starts in the balanced profile: level 5, preamble 16.
- GPS duty scheduling is automatic when a supported GPS is explicitly enabled; this firmware does not turn GPS on by default.
- TFT/OLED builds turn the display off after inactivity; LoRa continues operating.
- If radio duty-cycle arming fails, the IoTThinks implementation falls back to continuous receive and limits retries rather than leaving the radio deaf.

Saved preferences always win after an upgrade. A previously configured device is not silently forced back to balanced mode.

## Easy setup

1. Flash the build matching the exact board.
2. Keep USB and the antenna connected.
3. Download the release's `NeonPocketMC-ULP-Configurator.zip`.
4. Windows: double-click `configure-ulp-windows.bat`.
5. Linux: run `sh configure-ulp-linux.sh`.
6. Pick the serial device, region, name, transmit power, admin password, and ULP profile.

The wizard verifies that it is talking to NeonPocket ULP firmware before changing anything.

### Simple manual CLI

Open the USB serial port at 115200 baud and end each command with Enter/CR:

```text
ulp
ulp on
ulp conservative
ulp max
ulp off
```

- `ulp` or `ulp status`: show MCU and radio state.
- `ulp on` / `ulp balanced`: recommended balanced profile.
- `ulp conservative`: more receive time, smaller savings.
- `ulp max`: highest duty cycling; may not hear older pre-1.16 transmitters.
- `ulp off`: continuous radio RX and no MCU sleep.

Advanced EasySkyMesh-compatible controls remain available through `get radio.rxps`, `set radio.rxps ...`, and `powersaving ...`.

## Installation

### ESP32 boards: V3, V4, Xiao ESP32-S3, RCC6

- Normal update: flash the `*-app.bin` at address `0x10000`.
- Recovery only: flash `*-full-recovery.bin` at `0x0`.
- The full image includes the bootloader, partition table, and app. It does not deliberately erase the separate MeshCore filesystem, but normal app-only flashing is the identity-preserving path.
- Never flash an image for another board.

### nRF52 boards: RAK4631, RAK3401 1W, RC52

- Enter the board's UF2 bootloader and copy the exact `.uf2` for that board.
- This is an application image; do not erase or replace the SoftDevice/bootloader.
- `.hex` is provided for advanced recovery tools.

See [docs/INSTALL.md](docs/INSTALL.md) for board-specific notes and [docs/POWER_SAVING.md](docs/POWER_SAVING.md) for the tradeoffs.

## Source and reproducibility

- NeonPocket ULP base: IoTThinks/MeshCore `PowerSaving-v17` commit `a3b9ad91a5bf04e7e00713595469dc868de53628`.
- MeshCore upstream base: 1.17.1 commit `d92964352441e53b93e8667b802e04f6e072b39e`.
- EasySkyMesh reference release: [`PowerSaving17.1`](https://github.com/IoTThinks/EasySkyMesh/releases/tag/PowerSaving17.1).
- All ten release environments are built by GitHub Actions and shipped with SHA-256 manifests.

This community project is not an official Heltec, RAKwireless, Seeed Studio, MeshCore, or EasySkyMesh release.

## License

MIT, retaining all upstream notices. See [license.txt](license.txt) and [docs/EASYSKYMESH_ATTRIBUTION.md](docs/EASYSKYMESH_ATTRIBUTION.md).
