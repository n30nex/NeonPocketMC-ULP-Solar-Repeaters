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

Do not interchange V3/V4, RAK4631/RAK3401, RCC6/RC52, or screen/headless images.

## First setup

Keep USB connected after the reboot and run the packaged configurator. It verifies the NeonPocket ULP version and then writes the node name, radio preset, TX power, power profile, and a replacement admin password.

The firmware's compile-time admin password is `password` only for first access. Replace it during onboarding before deployment.

## Solar deployment

Use an external solar/MPPT charger that is suitable for the exact battery chemistry and panel open-circuit voltage. A connector fitting mechanically does not prove polarity, voltage, charge current, or regulation compatibility.

After configuration:

1. Restart and confirm the repeater advert/name from a second MeshCore radio.
2. Confirm RX and TX at the deployment preset.
3. Compare `ulp conservative`, `balanced`, and `off` at the real site.
4. Measure idle and traffic current after the display timeout.
5. Weatherproof the antenna feed, enclosure, cable entries, and battery separately.
