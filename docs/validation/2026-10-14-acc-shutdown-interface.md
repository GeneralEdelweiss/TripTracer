# ACC shutdown interface — 2026-10-14

## Electrical implementation
The existing power chain is BAT -> D901/TVS -> LMR38020-Q1 5V -> TPS2116 source priority -> MCP1826S 3V3. ACC starts the buck through Q914/Q915; the prearmed TLC555/AND/opto holds it from BAT after ACC OFF.

The missing functional connection was ignition detection at the MCU: no GPIO previously observed ACC OFF. U201 **GPIO34 / module pad29** now receives **MCU_ACC_INV_N** from Q912's protected inverse ACC node through **R207 100k 1%, 1206**. LOW means ACC ON; HIGH means ACC OFF (including USB-only). GPIO21/pad25 remains MCU_HOLD_REQ; GPIO33/pad28 remains USB_ACTIVE_N. GPIO34 is exposed on the selected MINI-1-N8 and is not a strapping pin. USB remains GPIO19/20. No new IC, footprint or PCB change.

## Why the series resistor matters
Directly joining a bidirectional MCU pin to the shared 555 trigger could defeat the hardware deadline if firmware drove it LOW. R207 isolates that fault. With R919=22k and R502=100k (both 1%), the maximum equivalent pull-up is 18.213k. With R207 minimum99k and the GPIO hard-shorted to GND, the unloaded trigger divider is **0.8446 x V3V3**. At V3V3=3V, allowing an additional **1uA assumed leakage envelope** lowers this to **2.518V / 0.8395 x V3V3**, still above the 555 trigger high region used in the timer sensitivity study. This calculation does not qualify all leakage/temperature limits at 3.3V; those remain a hardware gate.

At ACC ON, Q912 sinks at most another 3.6/99k = **36.4uA** if GPIO34 is accidentally driven HIGH. With input configured correctly, the module's 25C input leakage limit50nA produces at most **5.05mV** across R207. R207 dissipation in a GPIO rail fault is below0.14mW. Neither R207 endpoint connects to raw ACC/BAT. For valid sensing, **disable GPIO34 internal pull-up and pull-down**; their typical45k resistance would otherwise load the100k sense path. GPIO34 is not an RTC GPIO; button wake allocation remains separate.

Manufacturer sources: [Espressif module datasheet v1.7](https://www.espressif.com/sites/default/files/documentation/esp32-s3-mini-1_mini-1u_datasheet_en.pdf), tables3-1,4-1,6-3; [Panasonic ERJP08F1003V](https://industrial.panasonic.com/ww/products/pt/small-and-high-power-chip-resistors/models/ERJP08F1003V). Existing project resistor symbol: passive pad1/2; existing Tripmaster:R_1206_3216 footprint reused. Candidate MPN, procurement/temperature derating not independently released.

## Required operating sequence
1. With ACC ON, the VIN-powered startup stage supplies5V independently of MCU boot. Firmware configures GPIO34 as input without pulls, reads GPIO33 for USB source status, and asserts GPIO21 HOLD early while ACC is still present.
2. ACC OFF raises GPIO34; the already active timer/opto holds the buck from BAT. Firmware stops new logging, finishes FRAM/SD/file closure, then releases GPIO21.
3. Stuck HIGH on HOLD is terminated by the hardware timer, subject to the documented RC/temperature qualification. A GPIO34 output-low fault must not retrigger the timer; R207 provides the calculated separation above.
4. USB-only has ACC sense HIGH and USB_ACTIVE_N LOW; service firmware must not interpret that combination as a pending vehicle shutdown. USB can keep the MCU alive after vehicle HOLD expires; hardware status does not guarantee total power-off with USB attached.

Firmware is not implemented by this schematic change. Loss of BAT before boot/HOLD assertion can still reset the system. No guaranteed3s hold, surge/thermal, USB inrush, ISO or vehicle approval is claimed.

## Checks
Native Actions exports the complete root netlist and now requires the exact six-node ACC trigger plus the isolated two-node MCU sense network, preventing accidental bypass or added timer loading. The power BOM includes R207 even though it is on the MCU sheet: **expected55 active power components**. Actions also exports the full hierarchical schematic PDF and retains evidence14days. Existing ERC/DRC failures remain enforced.

Native run and results: pending for the implementation commit.
