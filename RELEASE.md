# Releasing ULP Solar Repeaters

ULP candidates are built by `.github/workflows/ulp-build.yml` on pull requests
and pushes to `main`. A tag does not start this workflow.

1. Set the same candidate version in `variants/neonpocket_ulp/platformio.ini`
   and `scripts/package_ulp_build.py`, and update the README release links.
2. Merge only after the required checks pass. Wait for the exact merged commit's
   unit tests, ten firmware builds, bundle, and `required-firmware` check.
3. Download that run's `NeonPocketMC-ULP-all-<commit>` artifact. Verify every
   entry in its aggregate `SHA256SUMS.txt` before preparing release assets.
4. Publish the ten build pairs, configurator ZIP, exact source ZIP, and license.
   If the release assets are flattened, generate a matching flat SHA-256 manifest
   from those verified files. Never substitute locally compiled firmware.
5. Create a new `v1.0.0-rc.N` tag at the verified merged commit and publish a
   prerelease with the exact commit and Actions run in its notes. Keep existing
   tags and assets unchanged.
6. Refresh the NeonPocketMC suite catalog/submodule, flasher profiles/catalog,
   and Canadaverse product page to the same release. Verify every changed public
   download, its checksum, and the deployed source before declaring it live.

## v1.0.0-rc.4

- Fix the Python configurator's `ver` timeout on nRF52 USB CDC by asserting DTR
  while keeping RTS disabled.
- Wait for complete reply lines so USB packet splits cannot truncate firmware
  identity or accept a partial error as success.
- Document the existing shell launcher for macOS, including Apple Silicon and
  Python 3.11, and the `/dev/cu.usbmodem...` port selection.
- Include seven synthetic serial regression tests in the existing CI gate.

The corrected configurator also works with rc.2 and rc.3 firmware. Reflashing
is unnecessary for this host-side fix. New rc.4 firmware keeps the MeshCore
1.17.1 baseline and existing power-saving behavior; the firmware version changes
so its identity matches the release package.

Use normal application images for ESP32 updates at `0x10000`, or the exact
board's application UF2 for nRF52. Recovery binaries are only for the documented
recovery path. Preserve identity and settings. Physical verification on the
reported Apple Silicon Mac/RAK setup remains outstanding.
