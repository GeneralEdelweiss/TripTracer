> **ÜBERHOLT DURCH WORST CASE:** [RESET_Q303_WORST_CASE_2026-10-15.md](RESET_Q303_WORST_CASE_2026-10-15.md): RESET/Q303 bei 125°C funktional nicht freigegeben. Die früheren optimistischen Rechenwerte sind nur hypothetisch. Physisches D306/D308 BAS70 A1/K2 korrigiert. R318 (nicht Q303) dissipiert ~109mW bei VS56V/EN7V.\n\n> **WICHTIGE KORREKTUR VON HERSTELLER-PINNUMMERN (Worst-Case-Review 15.10.2026):** Vishay [BAS70-02V Datenblatt, S.1](https://www.vishay.com/docs/85652/bas70-02v.pdf) zeigt **physisches Pad 1 = ANODE, Pad 2 = KATHODE**, nicht umgekehrt wie in der alten Standardbibliothek `TripTracer_V1:PWR_DIODE`. D306/D308 nutzen deshalb nun eigenes portables `TripPower_Sym:BAS70_02V_A1_K2`; D306 pin2 K=RESET, pin1 A=GATE, D308 pin2 K=RESET, pin1 A=CTRL_EN. **Die alte Zeile unten mit „K1/A2“ ist überholt.** Schottky-Sperrleckage bei 125°C, EN<0.41V und Source-Follower-EIN sind weiterhin **nicht nachgewiesen**. Die bisherige 109mW-Zahl ist die R318-Verlustleistung im hypothetischen VS56V/EN7V-Fall, **nicht direkt Q303**. Widerstand R318 selbst (Bauform 1206 bei 125°C) muss geprüft werden. Keine Fertigungsfreigabe.

# TripPower U302 RESET → LM74930 EN: hardwareseitige AUTO/RUN-Verriegelung (15.10.2026)

**Status: ECHTER KICAD-10-PROTOTYP, KEINE ELEKTRISCHE/HARDWARE/202V-FREIGABE.** Der Benutzer will alle Einschaltwünsche über eine einheitliche Freigabesperre nach TPS3760A012DYYRQ1 überwachen. Nach [TI TPS3760-Q1 Rev.B](https://www.ti.com/lit/ds/symlink/tps3760-q1.pdf), Abschnitt 6.5: U302.6 RESET ist **Open Drain, aktiv LOW**, V_OL ≤0.3V bei 5mA, Leckstrom High-Z bis 300nA, Versorgung 2.7–65V und bei VDD<1.4V Ausgang **undefiniert**. [TI LM74930-Q1](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf) benötigt **EN>1.05V zum sicheren EIN** und **EN<0.41V zum sicheren AUS**, I_EN ≤0.2µA. Ein normaler Diode-ODER ohne Verriegelung ist nicht zulässig.

## Funktion, keine bloß beschriftete Leitung

```text
VS_CLAMP → U302 TPS3760 SENSE mit R330/R331/R332/R333
                        │
       RESET_OD_N (LOW = nicht bereit / CTR wartet)
                        │
            ┌───────────┴───────────────────────────┐
            ↓                                       ↓
  D306 Schottky-K:RESET                      D308 Schottky-K:RESET
       A:EN_GATE_DRIVE                        A:CTRL_EN (zweite Sperrklemme)
            │                                       │
 VS_CLAMP─R334 470k─┤                       Q303 Source────────CTRL_EN─R316 5.6k─GND
               ├─R335 1M─GND                     ↑
               └─D307 10V Zener─GND              │
                         │  Q303 Gate            Q303 Drain
                         └───────────Q303 G          │
                                  R319 0R AUTO ──────┤
           VS_CLAMP─R318 22k─AUTO_EN_LINK       EN_REQUEST_RAW
           RUN_CMD─R317 4.7k─D305─EN_REQUEST_RAW ┘
```

**Konkreter Schaltplan:** `01_Protection_LM74930.kicad_sch`: R319.2 und D305.K (=Pin1) vom alten `CTRL_EN` auf neues `EN_REQUEST_RAW` verlegt. Die Eingänge AUTO und RUN können **EN nicht mehr direkt** betätigen. `R318=22k` statt 100k, `R316=5.6k` statt 100k für höhere Störfestigkeit gegen MOSFET-Hot-Leckstrom. `C309` früher 10µF/50V an `CTRL_EN` ist in KiCad **DNP**, damit Aus über den Supervisor nicht um 10µF verzögert wird. `R313–R315` bleiben für 202V/350ms unverändert 9.9kΩ.

`03_VS_READY_TPS3760.kicad_sch` erhält den 100V-NMOS-**Q303** als echte **D→S-Pass-Stufe** zwischen `EN_REQUEST_RAW` und `CTRL_EN`, Source an CTRL_EN, Drain an EN_REQUEST_RAW. **MOSFET-Bodydiode verkehrt herum** für Einspeisung EN_REQUEST_RAW→CTRL_EN, damit der FET ausgeschaltet sperrt. Q303 Gate von VS über R334470k / R3351M, durch D307 10V-Zener vor +65V VS geschützt. D306 zieht Gate an Reset LOW (~0.3V plus Schottky-VF) auf AUS. D308 zusätzliche aktive-low Klemme von EN→RESET bei HOT-Off-Leckstrom. Wenn RESET High-Z, liegt Gate gegen GND modellhaft VS×1M/(1M+470k)≈0.68 VS bis die 10V-Zener greift und EN kann zugeführtem AUTO/RUN folgen. **RESET bleibt auf eigenem positiven Hysterese-Feedback R332/R333 und wird nicht direkt mit EN kurzgeschlossen.**

### Bestückbare Bauteilkandidaten – 15.10.2026, DigiKey DE Momentaufnahme, netto vor USt/Versand

| Ref | MPN | Parameter | Stückpreis/Stk. | Bestand | Status |
|---|---|---|---|---|---|
| Q303 | [onsemi BVSS123LT1G](https://www.digikey.de/de/products/detail/onsemi/BVSS123LT1G/3062042) | AEC-Q101 100V SOT-23, G1/S2/D3, VGS±20V, RDS≤6Ω @10V, **IDSS bei100V/125°C max60µA** | ca. 0.38 EUR | Momentaufnahme 1,300–18,000 je Listung | **Prototyp** |
| D306+D308 | [Vishay BAS70-02V-HG3-08](https://www.digikey.de/de/products/detail/vishay-general-semiconductor-diodes-division/BAS70-02V-HG3-08/16683593) | Automotive-Schottky 70V SOD-523, K1/A2 in KiCad | ca. 0.41 EUR ×2 | ca. 48,000 | **Prototyp; Reverse-Leak und Vf bei −40/125°C offen** |
| D307 | [onsemi SZMMSZ5240BT1G](https://www.digikey.de/de/products/detail/onsemi/SZMMSZ5240BT1G/5969222) | AEC-Q101 10V ±5% 500mW Zener SOD-123 K1/A2 | ca. 0.29 EUR | ca. 59,900 | **Prototyp; VZ bei ~30–110µA Zenerstrom unqualifiziert** |
| R334/R335 | 470k / 1M, 1%, 1206 | Gate-Teiler, automotive genaue MPN noch offen | unbekannt | offen | **BOM-Gate** |

Die drei D/Q-Halbleiter erhöhen die 1-Stück-Materialkosten indikativ um **ca. 1.49 EUR netto** zuzüglich R334/R335 (andere Bauteile sind Wertänderungen). Achtung: BAS70-HG3 ist **SOD-523**, deutlich kleiner als 1206 und nicht so bequem von Hand zu löten. Nicht mit nicht lieferbarem BAS70Q oder BSS123Q verwechseln.

## Rechen-Vorbemessung und offene echte Grenzen

- **AUTO EIN nach gültigem Reset**: bei VS≈8V und eingeschaltetem Q303, ohmsches Ideal `V_CTRL_EN≈8V×5.6/(22+5.6)=1.623V`. Gegen LM74930 guaranteed V_ENR≤1.05V **0.573V nominelle Reserve**, aber Q303 ist Source-Follower: Gate≈5.44V bei 8V ohne Zenerleck und V_GS hängt vom tatsächlich geforderten Strom/Temp ab. Kein garantiertes min EN ohne eigene Hot-/Cold-I(VGS)-Kurven/SPICE/Messung. 
- **RUN_CMD**: 3.3V am Eingang, D305 BAS116Q und R3174.7k, mit **angenommenen** Vf_D305=0.8V und vernachlässigbarem Q303-Ron: `V_EN=(3.3−0.8)×5.6/(4.7+5.6)=1.359V`; 0.309V über 1.05V. Externe RUN-Toleranzen, Vf beim Extremtemperatur-/Mikrostrom und Rückspeisen noch offen.
- **AUS durch RESET LOW**: Q303 öffnet (GATE via Schottky D306 niederohmig an RESET); R316 zieht `CTRL_EN` nach Masse, zusätzlich D308 vom EN-Ausgang zum RESET. Onsemi BVSS123LT1G spezifiziert `I_DSS≤60µA` bei **VGS=0V**, `VDS=100V`, `TJ=125°C`. Unter der **Modellannahme VGS≤0** ergäbe das `V_EN≤60µA×5.6k=0.336V`, +1% R316 und 200nA EN-Leck <0.341V vs LM74930 ENF_min0.41V. Bei RESET LOW hat Gate real ca. Schottky-Vf, nicht garantiert 0; außerdem ist die maximale D308-Klemmspannung bei extremen Temperaturen nicht nachgewiesen. **Somit ist AUS bei jedem Eckfall noch NICHT freigegeben.**
- **Gate stress**: Bei VS8 ergibt R334470k/R3351M ideal `V_GATE≈5.44V`. Zener D307 begrenzt oberhalb ~10V, aber das 10V-Spezifikations-Teststromniveau ist **weit höher** als unsere ~30–110µA. `VGS<20V` bei VS≤65V **mit echtem Zener-I(V),T** nachweisen; idealisierte 10V-Festklemmung ist keine Bauteilfreigabe. Reverse-Leckstrom von D306/D308 kann außerdem das 1M/1.91M RESET-Hysteresenetz beeinflussen.
- **202V/350ms**: VS nominell per 56V Zener geschützt (real pulsbias OFFEN). Für Q303 bei VS56V und angenommen 5–8V Source liegt `P≈(56−V_EN)×(56−V_EN)/22k = 105–118mW` während des 350ms Pulses; BVSS123LT1G Dauerleistung bei TA125°C über 1.8mW/°C Derating nur ca. **45mW**. **Spezifischer zusätzlicher Sperrpunkt: heißer 350ms Puls Q303 transienter Zθ(t) – ohne Nachweis keine Freigabe.** Bei VIN30 normal ähnlich `P≈23–30mW` als grobe Modellrechnung.
- **9V Startbudget**: bislang R313–315 9.9k und C308 nominal 10µF, durch Wegfall des früheren 200k AUTO→GND Ruhestroms *prinzipiell* höhere Vorladungs-VS; neue Gate- und Hysterese-/Zener-/Leckströme rechnen. Dass VS8V garantiert erreicht und C302/C308 beim C303-Gateladen >6V bleiben, ist weiter **offen**.
- **DNP C309 und erster RAMP**: externes RUN kann früh HIGH sein, der Q303-Gate-Spannungsteiler kann bei VIN→0 einen unbestimmten RESET-Zustand erleben (<1.4V U302). Gate muss unter dem MOSFET-Mindest-Vth bleiben oder ein zusätzlicher definierter Reset-/Gate-Clamp nötig sein; MCU-USB→Fahrzeug darf nicht rückspeisen.
- **Pinplan**: Q303 auf SOT23 **1G 2S 3D** nach [onsemi](https://www.onsemi.com/pdf/datasheet/bss123lt1-d.pdf). D306/D308/BAS70-02V-HG3-08 und D307/Zener jeweils **pad1 cathode, pad2 anode**; bei D306 cathode RESET / anode GATE, D308 cathode RESET / anode CTRL_EN, D307 cathode GATE / anode GND. Footprints KiCad-SOT23/SOD523/SOD123, Bauteil-3D-Pakete und PCB-Pin-Orientierung später prüfen.

## Verbindliche Funktionsmatrix

| U302 RESET | AUTO R319 | RUN_CMD | Q303 | CTRL_EN |
|---|---|---|---|---|
| LOW (VS noch nicht bereit / CTR-Delay / Einbruch) | 0/1 | 0/1 | AUS (Sperrpfad D306+D308) | LOW (unter 0.41V **erst zu validieren**) |
| Open Drain High-Z (=VS_READY) | nicht bestückt / LOW | LOW | Gate frei, aber **keine angeforderte Spannung** | LOW via R316 |
| Open Drain High-Z (=VS_READY) | bestückt | egal | freigegeben, EN_REQUEST_RAW aus VS über R318 | HIGH (>1.05V **erst zu validieren**) |
| Open Drain High-Z (=VS_READY) | nicht bestückt | HIGH 3.3/5V | freigegeben, EN_REQUEST_RAW aus R317+D305 | HIGH (>1.05V **erst zu validieren**) |

Damit ist `EN = VS_READY && (AUTO || RUN_CMD)` **elektrisch als Zwischenentwurf realisiert**, aber die zugehörige vollständige *sichere* Grenzspannungs- und Bauteil-Freigabe bleibt offen. Die Reset-Freigabeverzögerung wird durch `U302.CTR/C311` gebildet, nicht C309. `CTS` ist offen für schnellstmögliche Assertion. Alle relevanten Modelle: 9/10/12/13.8/24/30, Hot Restart, −40/25/85/125°C, 202V/350ms, Verpolung, Kabelanbindung und externe austauschbare `F_MAIN`.
