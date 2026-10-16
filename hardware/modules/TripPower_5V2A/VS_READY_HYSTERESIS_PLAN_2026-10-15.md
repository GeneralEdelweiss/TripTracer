# VS_READY-Hysterese – Entwurfsziel & Garantierbarkeit (15.10.2026)

## Entscheidung vorweg

**Für den aktuellen Standalone-TripPower ist in 9–30 V noch KEINE garantierte Start-Untergrenze belegbar.** 30 V ist nicht automatisch freigegeben: Hersteller spezifiziert die Ladungspumpen-CAP-Ladestromversorgung unter anderen Bedingungen als die unzureichend beschriebene Versorgung des Controllers während des Kaltstarts. In der vorherigen **passiven AUTO-EN-RC-Modellrechnung** war bei VIN 9 V / ungünstig parametrierten Ceff und 5 mA *angenommenem* zusätzlichem Pumpen-Eingangsstrom `VS_min=5.15V` (und bei 12V `6.93V`, 13.8V `7.90V`, 24V `12.60V`, 30V `14.95V`). Das sind **keine garantierten Herstellergrenzen** und **nicht** der Startverlauf der neuen Hysterese.

## Vorschlag: 8.0 V VS_READY einschalten, 6.0 V VS_READY ausschalten, 250ms stabile Vorladung

1. **VS_READY=FALSE solange VS < 8.0 V.** LM74930 EN auf Low halten; Ladungspumpe bei EN Low aus. Nach dem **Überschreiten von 8.0V** für nominell **250ms stabil** VS_READY freigeben und nur dann `RUN_REQUEST ∧ VS_READY` an `CTRL_EN` weiterleiten. 250ms ist eine experimentelle Vorladung, keine garantierte Hersteller-Zeit; besser als sofort bei 8V.
2. **Bei VS < 6.0V sofort wieder sperren** (nur interne Komparator-/Treiberausbreitung, keine absichtlich lange Verzögerung); 2.0V Schmitt-Hysterese. UV-Schaltpunkt **6.0V** basiert auf der **VS≥6V**-Prüfbedingung des TI-`I(CAP)`-Minimums, nicht auf einem absolut harten 6V-`LM74930`-Betriebslimit. `VITN`-Toleranz und Hysterese-Toleranz der realen MPN in der 6V-Reserve berücksichtigen.
3. **R318/R316/R319 AUTO (100k/100k/0R) und externes RUN_CMD über R317+D305** dürfen `VS_READY` NICHT umgehen. Die bestehende passive 10µF-C309 an CTRL_EN wäre beim schnellen Rückfall problematisch und ist nach Einführung einer echten Freigabeschaltung auf **DNP/Entfernen oder wenige nF** zur Funktion zu prüfen. Die zwei Steuerungsmodi bleiben erhalten; keine Relais-/MCU-USB-Backfeed.
4. Der Überwacher muss direkt aus der geschützten `VS_CLAMP`-Versorgung startfähig sein (auch beim ersten OFF), **2.7–65V Betriebsbereich**, sehr geringer Iq, Sensor kann 56V nominell (Zener-Toleranz/Surge prüfen), fail-safe Ausgang der `CTRL_EN` auch mit externem 3.3/5V-RUN low halten kann; output sink bei RUN=5V über 4.7k etwa **1.0mA** plus AUTO-Teiler ~0.3mA bei 56V plus C309-Entladeimpulse (deshalb C309 DNP). Zusätzliche Schmitt-Logik muss selbst **vor Q301** versorgt werden; keine Rückspeisung aus dem 5V-Buck.

## 9V Spannungsbudget beim ersten Start

`R313–R315 = 9900Ω`, Auto-EN-Teiler R318/R316=200kΩ in Serie, D302 `SOURCE_A→VS` kann **erst nach** erfolgreichem Gate-Start helfen; großer `C308 10µF/100V` plus `C302 1µF` nominal an VS.

Rechnerische, nicht garantierte statische OFF-Sensitivität mit **5µA LM74930 OFF + 10µA Panasonic C308 Leckstromgrenze am Nennprüfpunkt + 2.6µA Supervisor-IDD max + 0.1µA Sense** (andere Leck-/Temperatur-/Ceff-Fälle offen) und R318+R316=200kΩ:

`VS_infinity = [VIN−9900Ω×17.7µA] / [1+9900Ω/200kΩ]`.

- Bei VIN=9V: `VS_infinity≈8.409V`. 8V Rising **nominal** erreichbar; nur **0.409V** OFF-Spannungsreserve (ohne Supervisor-Spannungstoleranz, Zenerleck, R-Toleranz, C308-Aging).
- Bei VIN=12V: VS_infinity≈11.267V; bei 24V≈22.701V, bei 30V≈28.418V. Dies sind Modellgrößen, keine nachgewiesenen eingeschalteten Versorgungen.
- Zeitkonstante `R_eq≈(9.9k || 200k)≈9.43kΩ`, mit nominell 11µF `τ≈104ms`. Bei VIN9V ist die Schwelle 8V erst nach nominell ca. 315ms erreichbar; weitere 250ms Haltezeit erhöhen VS auf ca.8.37V. Reale Leckströme und ESR/Ceff verändert diese Zeiten.
- Mit **Ceff=8.5µF** (angenommener unterer Prototyp-Grenzfall), Pumpen-Schaltintervall **3.03ms nur als Rechenmodell** und statisch angenommener zusätzlicher Pumpeneingangsaufnahme **5mA** + 0.78mA IQ wird bei 9V aus VS≈8.37V eine Unterschreitung von 6V **knapp vermieden**. Bei einem größeren, **nicht vom TI-Datenblatt begrenzten** transienten VS-Strom fällt VS trotzdem unter 6V. Folglich **selbst mit 8/6/250ms KEINE 9V-Startgarantie**.

## Beschaffbare COTS-Option für VS_READY

**TI [TPS3760-Q1](https://www.ti.com/product/TPS3760-Q1) (AEC-Q100, 2.7–65V, Iq typ 1µA; je nach Variante max 2.0/2.6µA, OD-Ausgang kann 5mA bis 0.3V sinken)** ist elektrisch interessante Supervisor-Familie; die Zener-/VS-Overshoot-Marge muss nachgewiesen werden.

- Nach **TI-Datenblatt Rev.B (03/2026) Table 4-1** tatsächlich aufgeführte automotive Variante **`TPS3760A012DYYRQ1`**, 0.8V **ADJUSTABLE über externen SENSE-Teiler**, **UV open-drain low, 2% interne Hysterese**, SOT-23-THIN-14; [Mouser Europa Cut Tape](https://eu.mouser.com/en/ProductDetail/Texas-Instruments/TPS3760A012DYYRQ1) als Lieferquelle ca. **2.30EUR/1, 1.71EUR/10, 1.40EUR/100 netto/St.** zum Suchzeitpunkt, Bestand schwankt ~570–1,279 Stück. Die **2% auf 0.8V sind KEINE 2V-VS-Hysterese**. Um das **8V-EIN/6V-AUS**-Ziel mit dieser tatsächlich lieferbaren MPN zu erreichen, ist ein **zusätzlicher, elektrisch auszuarbeitender Schmitt-Rückkopplungs- und RUN-Gate-Pfad** erforderlich. Nicht ohne konkrete Widerstandsnetz-Berechnung / Fehlermodelle / Pin-Netz-Prüfung in KiCad eintragen.
- TI-Artikel beschreibt zwar auch feste 0.5–2.5V Hystereseoptionen für 2.9–8V Schwellen, aber **eine genau passende und tatsächlich lieferbare 6.0V UV/2.0V-Hysterese MPN wurde NICHT belegt**; Bestellnummer darf **nicht** aus dem Suffix erfunden werden. In Table 4-1 aufgeführte andere feste Varianten (6.3V/5%) erfüllen unsere 2V Hysterese nicht. [TI Gerätevariantenliste Rev.B](https://www.ti.com/lit/ds/symlink/tps3760-q1.pdf).
- Alternative `TPS3762-Q1` AEC-Q100 2.7–65V mit 0.8V sense + 2/5/10%-Hysterese, aber höherer Iq max 8.1µA/komplizierterem Selbsttest und Hysterese nicht unmittelbar 2V bei 8/6. Nicht blind als austauschbar.
- TI reset release via CTR: typische/Anwendungswert **10nF ≈ 12.8ms**, linear extrapoliert **~200nF ≈ 256ms**, erst mit konkretem 100V/25V X7R/NPO `Ceff(temperature/DC)` und TI Delay-Streuungen auslegen. Reset assertion / UV darf **keine** 250ms Verzögerung bekommen.

## Übergangsentscheidung

**Kein zusätzlicher Supervisor und keine fingierte Festschwellen-MPN wird jetzt in die tatsächliche KiCad-Netlist übernommen.** Aktive Schaltung mit C308/C309 bleibt *nur* reversibler Prototyp der Vorrevision. **Nächste Konstruktionseinheit:** entweder tatsächlich beschaffbare automotive Supervisor-Variante mit direkt spezifizierter 6V-Falling+2V-Hysterese auswählen oder präzise diskrete positive Rückkopplung **getrennt von CTRL_EN/RUN_CMD** auslegen; C309 auf DNP, die 250ms Freigabeverzögerung aus CTR/konkreter Timerfunktion, beide Steuermodi in AND-Verknüpfung; danach erst natives KiCad ERC/Netlist, 9/10/12/13.8/24/30V analytisch und dynamisch (auch hot-plug und schnelle Wiederholung), 202V/350ms/VS65V Grenze, Q301 SOA und externe F_MAIN-Faultabstimmung.

**Garantierbarkeit** entsteht erst nach spezifizierter vollständiger Last-/Kälte-/Heiß-/Bauteilstreuungsrechnung, simulierter Versorgung mit echten Strom-/Ceff-Modellen UND Labortests. Ziel bleibt **9–30V VIN am Modul bei benannten Lasten**, nicht einfach 12V im Auto.
