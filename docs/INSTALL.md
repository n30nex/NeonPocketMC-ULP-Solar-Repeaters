# Install and deploy

## Before flashing

1. Confirm the exact board model and radio variant.
2. Attach a correctly tuned LoRa antenna before transmitting.
3. Back up any identity/settings that must survive.
4. Use the normal application image for updates.
5. Keep the battery/solar system disconnected while bench wiring is uncertain.

## Image selection

Every public filename contains the hardware name. RCC6 and RC52 additionally contain `Headless` or `TFT`.

- `app.bin`: normal ESP32 update at `0x10000`.
- `full-recovery.bin`: ESP32 recovery at `0x0`; use only for a non-booting unit.
- `.uf2`: normal nRF52 application update through the UF2 bootloader.
- `.hex`: advanced nRF52 recovery/programmer input.

Do not interchange V3/V4, RAK4631/RAK3401, Xiao ESP32-S3/Xiao nRF52840,
RCC6/RC52, or screen/headless images.

## First setup

Keep USB connected after the reboot and run the packaged configurator. It verifies the NeonPocket ULP version and then writes the node name, radio preset, TX power, power profile, and a replacement admin password.

The configurator also asks whether the saved map location should be included in adverts. ULP repeater builds use USB CLI only; they do not start a setup Wi-Fi access point or host a WebUI.

The firmware's compile-time admin password is `password` only for first access. Replace it during onboarding before deployment.

## USB configurator troubleshooting

If the port opens but `ver` gets no reply on a RAK or another nRF52 board, check
the configurator's `Device` setup: older copies explicitly set
`self.serial.dtr = False`. The firmware's TinyUSB serial stack requires DTR to
send replies, even though it can still receive commands. Use the corrected
`tools/configure_ulp.py`, which sets DTR to `True` and leaves RTS `False`.
This is a host configurator fix; it does not require reflashing the repeater or
resetting its saved settings. It applies to the rc.2 and rc.3 firmware.

On macOS, including Apple Silicon with Python 3.11, run
`sh configure-ulp-linux.sh` from the extracted configurator folder. Choose the
repeater's `/dev/cu.usbmodem...` device, or pass its exact name with `--port`.
Close any other terminal or browser tab holding the port. The firmware accepts
115200 baud with carriage-return command endings.

The corrected parser also waits for a complete reply line, so USB packet splits
cannot truncate the firmware version or turn a partial error into success.
To check the connection without applying settings again, stop with Ctrl-C after
the wizard prints `Verified` and prompts for the repeater name.

## Solar deployment

Use an external solar/MPPT charger that is suitable for the exact battery chemistry and panel open-circuit voltage. A connector fitting mechanically does not prove polarity, voltage, charge current, or regulation compatibility.

After configuration:

1. Restart and confirm the repeater advert/name from a second MeshCore radio.
2. Confirm RX and TX at the deployment preset.
3. Compare `ulp conservative`, `balanced`, and `off` at the real site.
4. Measure idle and traffic current after the display timeout.
5. Weatherproof the antenna feed, enclosure, cable entries, and battery separately.
