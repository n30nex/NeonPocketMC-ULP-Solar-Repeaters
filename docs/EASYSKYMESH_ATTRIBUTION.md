# EasySkyMesh / IoTThinks attribution

NeonPocketMC ULP Solar Repeaters are built directly on the power-saving work by **IoTThinks**:

- Project and end-user releases: [IoTThinks/EasySkyMesh](https://github.com/IoTThinks/EasySkyMesh)
- Reference release: [PowerSaving17.1](https://github.com/IoTThinks/EasySkyMesh/releases/tag/PowerSaving17.1)
- Power-saving source fork: [IoTThinks/MeshCore, PowerSaving-v17](https://github.com/IoTThinks/MeshCore/tree/PowerSaving-v17)
- Power-saving documentation: [EasySkyMesh PowerSaving wiki](https://github.com/IoTThinks/EasySkyMesh/wiki/PowerSaving)
- Source commit used here: `a3b9ad91a5bf04e7e00713595469dc868de53628`

The imported implementation includes the principal EasySkyMesh power-saving mechanisms:

1. ESP32 light sleep with LoRa interrupt/timer wake and nRF52 event sleep.
2. SX1262/LR1110 receive duty cycling with configurable RX/sleep timing and power levels.
3. Continuous-RX fallback and bounded re-arm attempts on radio duty-cycle errors.
4. Noise-floor recalibration and timekeeping corrections needed around sleep cycles.
5. GPS duty scheduling for builds where GPS is present and explicitly enabled.
6. USB-awareness fixes from the post-release PowerSaving-v17 branch.

NeonPocketMC additions include the RCC6 and RC52 hardware ports, their optional NV3001B TFT profiles, indexed framebuffer integration, a default balanced ULP policy for new installations, the `ulp` convenience command, guided configuration, build/release automation, and NeonPocket documentation/branding.

IoTThinks and the EasySkyMesh contributors are not responsible for NeonPocketMC builds or support. This file is intended to make their substantial technical contribution clear and easy to find.

The source is distributed under the repository's MIT license with upstream copyright notices retained.
