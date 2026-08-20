# Power-saving behavior

## Balanced is the default

New NeonPocketMC ULP installations use:

```text
MCU sleep: on
Radio RXPS: on
Level: 5
Preamble: 16
```

This is a compromise, not a guarantee. RX duty cycling lowers average receive power by sleeping between listen windows. That necessarily increases the chance of missing a packet, particularly around interference, weak signal, short/older preambles, or incompatible transmitters.

## Profiles

| Command | MCU | Radio | Use |
|---|---|---|---|
| `ulp conservative` | Sleep | Level 1 / preamble 16 | Favor reception |
| `ulp on` or `ulp balanced` | Sleep | Level 5 / preamble 16 | Default |
| `ulp max` | Sleep | Level 10 / preamble 32 | Favor battery; compatibility warning |
| `ulp off` | Awake | Continuous receive | Baseline/troubleshooting |

The radio driver immediately returns to continuous RX when duty-cycle arming fails. Three consecutive arm failures pause further attempts until configuration changes, avoiding an endless retry loop.

## Board caveats

- A display consumes extra power while lit. RCC6/RC52 TFT profiles use a single indexed framebuffer and power the panel down after inactivity.
- On RAK3401, the GPS/shared 3V3 rail cannot be freely shut down without also disturbing required hardware; the board profile preserves that rail.
- Current draw depends heavily on the regulator, attached sensors, FEM/LNA, display, USB state, radio preset, traffic, and solar controller.
- IoTThinks' published measurements are useful reference data, but they are not NeonPocket certification results and are not repeated as guarantees here.

Measure at the battery under the intended traffic pattern. Size the battery and panel from measured worst-season energy, not a headline current figure.
