# Vehicle harness, 9V HOLD and thermal envelope — 2026-10-14

Development candidate, not a wiring/fault/vehicle approval. No PCB edit.

## Implemented changes
- F901 **Littelfuse0997003.WXN,3A/58V** on BAT and F902 **0997002.WXN,2A/58V** on ACC are drawn as **external, replaceable** source-side fuses on01G. They are explicitly excluded from the PCB, have no PCB footprint and retain the existing M8/pigtail nets. They can represent a suitable existing fused takeoff; no device-side inline holder is prescribed.
- R911/R915 **30.1k ->24.9k1%**, candidate PanasonicERJP08F2492V, existing1206 footprints.
- R914 **330ohm ->154ohm1%**, candidate YAGEORC1206FR-07154RL, existing1206 footprint. No added PCB component or IC.

## The actual headroom defect
The earlier calculation allowed diode drop but omitted harness/fuse/contact loss. At a **vehicle source** of9V (not9V already at the M8),10W buck output, assumed80% efficiency,1.5V diode allowance,10mA additional BAT bias and0.35ohm total warm BAT/GND resistance, the constant-power solution is:
- current **1.8325A**, protected buck input **6.8586V**;
- diode **2.7488W**, whole harness **1.1754W**;
- old30.1k HOLD model **1.2898V**, below the1.4V enable requirement;
- new24.9k HOLD **1.5128V** with the same device-drop/leakage/resistor assumptions. The separate conservative VIN6.8V model gives1.4962V.

This solves a specific missing-loss calculation and changes the hardware accordingly. It is not a measured cold-start guarantee. The diode1.5V allowance,80% efficiency, bias budget, transistor/opto drops and leakage must be verified. The 288-corner solver distinguishes vehicle-source voltage from device-terminal voltage and uses the high-voltage stable constant-power root; it does not model control-loop dynamics.

## Opto drive
TI's SN74LVC1G08-Q1 specifies VOH >=2.3V at3V and24mA, over its stated temperature range. R914154ohm+/-1% gives at least **5.143mA** with an **assumed VF <=1.5V**, and at most **23.613mA** even with a shorted LED at3.6V. Resistor worst-case shorted-LED power is85mW, below the0.25W candidate rating at70C.

The opto manufacturer specifies VF max1.4V at10mA and25C, and CTR min50% at5mA/VCE5V and25C. The1.5V cold allowance and operation above5mA are **not full-temperature CTR guarantees**. The change brings the LED drive above the published test current under the declared allowance; hot/cold CTR, loaded output voltage and real HOLD still require qualification. At USB-only the unarmed timer keeps this LED off.

Sources: [TI SCES556H Aug2026, sections5.3/5.5](https://www.ti.com/lit/ds/symlink/sn74lvc1g08-q1.pdf), [Wuerth140356145000 rev001.004, p2](https://www.we-online.com/components/products/datasheet/140356145000.pdf), [Panasonic24.9k](https://industrial.panasonic.com/tw/products/pt/small-and-high-power-chip-resistors/models/ERJP08F2492V). Existing nonpolar1206 symbol/land patterns are reused; no new component geometry is invented.

## External wiring and fuse coordination
Candidate harness: **0.5mm2 copper, maximum2m each direction**, rated insulation, mechanical support and suitable crimps. With the stated copper resistance/temperature assumptions its70C wire loop is0.16751ohm, leaving0.18249ohm of the0.35ohm budget for the fuse, holder, M8 and other contacts. The assembled loop must be measured. Verify at least5A wire ampacity at70C under the actual bundling/installation; this is a requirement, not an assertion about any unspecified0.5mm2 cable.

The3A fuse's typical60/80C derating values interpolate to2.1A at70C, above the1.833A modeled current. This is typical application guidance, not a guaranteed no-trip rating. Source-side locations hotter than70C require review; do not silently increase fuse current without rechecking the whole path.

The manufacturer's maximum opening times at2x/3.5x/6x nominal give BAT3A illustrative constant-current integrals180/55.125/32.4A2s and ACC2A80/24.5/14.4A2s. A stated-material adiabatic copper study from70 to105C gives1364.5A2s for0.5mm2; that only screens these sampled fuse points. At135% the opening time can reach600s: steady ampacity matters. **Above6x, maximum total clearing I2t remains needed**; the catalog's typical melting I2t is not a guaranteed upper bound. M8 contacts, holders, crimps and PCB traces are not certified by the wire calculation.

58V and1kA interrupt ratings receive credit only if actual terminal voltage and prospective fault current are within them. TestA202V is outside this fuse/clamp envelope. Both source circuits need protection close to the source; these fuses are **line protection, not guaranteed semiconductor protection**.

[MINI997 manufacturer data](https://www.littelfuse.com/assetdocs/littelfuse-datasheet-997-mini58v?assetguid=f4bf5724-5a40-4a44-8f08-c52ae959a5ef). If a new holder is needed, [Littelfuse0FHM0001ZXJ-RED](https://www.littelfuse.com/de/products/fuses-overcurrent-protection/fuse-holders-fuse-blocks-accessories/fuse-holders/in-line-fuse-holders/mini-fhm/0fhm0001zxj-red) is currently specified58VDC. Old32V holder listings/installed parts must not automatically receive that rating.

## D901 thermal consequence
S5MC's quoted10K/W is **junction-to-terminal**, not junction-to-air. At the2.749W modeled dissipation and70C ambient, a125C design junction target would require about **20.0K/W actual junction-to-air**. That has not been established for the PCB. The3A/5A package label alone is not a heat proof.

For illustration, with assumed VF1.15V, thetaJA45K/W gives a thermal-only5V current ceiling about1.26A at the9V source;60K/W gives0.95A. These are sensitivities, not a new reduced product requirement. The2A target remains; measured thermal behavior or a qualified lower-loss/better-cooled implementation must satisfy it before release. No PCB layout or full-load approval was made.

## Sourcing and cost
14Oct2026 web observations, not a checked-out German landed quote:
- TVS5800: TI shows no confirmed stock; Mouser lists non-stocked/MOQ3000/18weeks, with an error banner and an old crawl. DigiKey's earlier listing also had no stock. **No confirmed near-term small-quantity source**. No ordinary60V TVS was silently substituted because its rated clamp can exceed80V.
- F902: [Mouser DE](https://www.mouser.de/de/ProductDetail/Littelfuse/0997002.WXN?qs=sGAEpiMZZMsIz3CjQ1xegWrlMY7vL59hm7srGIGCOPc%3D) listed15949, EUR0.886/0.668/0.501 at1/10/100; VAT/shipping treatment unconfirmed.
- F901: [DigiKey](https://www.digikey.com/en/products/detail/littelfuse-inc/0997003-WXN/701055) listed3471, USD1.04/0.792/0.6063 at1/10/100.
- R914: [DigiKey](https://www.digikey.com/en/products/detail/yageo/RC1206FR-07154RL/728563) listed5000, USD0.10/0.047/0.0247. PanasonicERJ-8ENF1540V is another catalog alternative, not yet priced as a complete order.
- New58V FHM holders are an optional cost increase: a retrieved Mouser listing showed USD10.33 each at1pc, USD7.55 at10,5.40 at100. A qualified existing fused source avoids buying two new holders. Reichelt options were considered, but no validated lower-cost58V MINI holder was confirmed; generic32V holders are not credited as58V.

All stock is to recheck. No order; complete2/10/100-device landed price, shipping/minimum order, JLC categories and final cable/M8 procurement remain **NICHT BELASTBAR**.

## Validation
New Actions coverage:288 source/diode/harness/load/efficiency corners, opto-current bounds, thermal/fuse sensitivity and actual offboard source-graph checks. Native netlist checks also verify offboard fuse terminals when included by the exporter; if omitted, the log explicitly distinguishes that from source checking. The BOM tags PCB versus vehicle-external installation.

Native run/results pending for this commit.
