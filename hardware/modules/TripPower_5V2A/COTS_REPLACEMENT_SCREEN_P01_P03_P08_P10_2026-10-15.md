> **AKTUELLER TRIPPOWER-VERTRAG (Korrektur vom 15.10.2026): 200 V / 350 ms**, nicht 202 V. Maßgeblich ist [`REV5_DESIGN_BASELINE.json`](REV5_DESIGN_BASELINE.json); in älteren REV2–REV4-Dokumenten stehen historische 202-V-TI-Referenzrechnungen, die NICHT die jetzige Vorgabe darstellen. 9–30 V, 5 V/2 A, RAW-AUX 1 A bleiben Entwicklungsziele. SOA/Puls- und PCB-Freigaben weiterhin BLOCKED. REV5-TPS38 ist aktiver Stand.

# TripPower – COTS-Ersatzprüfung über P02 hinaus (15.10.2026)

> **Ergebnis: TPS38-Q1 bleibt einzige primär empfohlene IC-Architekturänderung; für den 5V-Buck und RAW-AUX wurden reale Serien-ICs/Module identifiziert, aber wegen Spannungsspielraum bzw. fehlender AEC-/Lieferbarkeit noch nicht freigegeben.** Keine Änderung der aktiven REV4-KiCad-Schaltpläne/BOM. Diese Seite ergänzt [P02 COTS TPS38](P02_COTS_TPS38_DUAL_ENABLE_2026-10-15.md) und das verbindliche [REV4-Entscheidungsregister](REV4_DECISION_REGISTER_AND_FAB_STOP.md). Sie soll unnötige erneute Markt- und Architekturwechsel vermeiden.

## Anforderungen: keine stillschweigende Vereinfachung

**VIN_FUSED 9–30V direkt am Modul**, 5V/2A dauerhaft, RAW-Zusatzausgang bis1A, AUTO/RUN 3,3/5V, −40 bis +125°C Ziel, off <100µA Entwurfsziel, **202V/350ms unsuppressed load dump** als separates Schutzgate, extern austauschbare F_MAIN upstream. Ein 65V- oder 36V-IC **darf niemals roh am 202V-Eingang stehen**; der hochspannungsfeste LM74930/FET-Pfad bleibt erforderlich. COTS ersetzt niemals SOA, PCB-DRC, thermische Freigabe.

## A. RESET/EN P02 – weiterhin beste konkrete Änderung

- **TI TPS38A010122DSKRQ1**; [TI Produkt](https://www.ti.com/product/TPS38-Q1), [Mouser DE](https://www.mouser.de/en/ProductDetail/Texas-Instruments/TPS38A010122DSKRQ1); zwei UV-Open-Drain-Outputs, 2,7–65V Versorgung, AEC-Q100, −40…+125°C. Low **VOL≤0,300V**, LM74930 verlangt **EN_OFF≤0,410V**; garantiert bei expliziten Hersteller-Testbedingungen. PNP/NPN-Hot-Off/hFE-Risiko entfällt. Mouser DE Snapshot 4.274 Lager/3,25€ pro1/2,03€ pro100 ohne MwSt./Versand.
- **Noch vor REV5-KiCad**: gemeinsame Open-Drain-Ausgänge beeinflussen externe Schmitt-Rückkopplung beim RUN=LOW; VIN0 mit RUN=HIGH und partiell geladenes CTR sind neue Eckfälle. Die TI-Familie besitzt **interne Hysterese-Optionen bis 2,5V**, aber für exakt unsere Wunsch-Schwellen ist eine *tatsächlich öffentlich bestellbare* Dual-Channel-AEC-MPN noch **nicht** belegt. Keine erfundene Variante bestellen.
- Bevorzugter nächster Entwurf: **einmal** TPS38-Dual-UV-Schaltung mit isolierter Hysterese-/RUN-State-Matrix aufsetzen und verifizieren, dann als REV5 wechseln. Kein weiterer diskreter Q303–Q305-Teiletausch aus Routine.

## B. Fertigmodul statt LMR38020 Buck P08

### B1: **TPSM33620S5QRDNRQ1** – AEC-Q100, 5V/2A, *3–36V IN*: wertvoll, aber **aktuell nicht drop-in-geeignet**

- [TI TPSM33620-Q1](https://www.ti.com/product/TPSM33620-Q1), [DigiKey DE 5V-Fixvariante](https://www.digikey.de/en/products/detail/texas-instruments/TPSM33620S5QRDNRQ1/27687227): integrierte MOSFETs, **AEC-qualifizierte Drossel**, Bootstrap und Regler; 11-Pin 4,5×3,5mm HotRod-QFN mit nassbenetzbaren Flanken, Automotive −40…+125°C Umgebung, 2A, integrierter 5V-Fixwert; definierte OCP/TSD/Spread-Spectrum, integrierte Kompensation und TI-Referenz/EVM. Bei fester 5V-Version nur wenige externe Passivteile.
- DigiKey DE Recherche 15.10.2026 ca **4.170** vorrätig, **2,05€ netto/Stk1, 1,8426€/Stk100**; Preis/Bestand sind Händler-Snapshot, kein Checkout-Angebot.
- **Blockierende Grenzüberschneidung:** Unser LM74930-OVP schaltet **nominal bei ~35,9V** ab. Das Buck-Modul erlaubt **maximal 36V Betrieb**, TI warnt vor *absolutem Maximum 40V* bei transientem VIN-Ringing. Ein nominaler **0,1V**-Abstand zwischen Abschaltschwelle und maximaler Betriebs-VIN ist **keine Robustheitsreserve**! Schon OVP-Toleranzen, OVP-Reaktionszeit, MOSFET-Turnoff und Kabel-/PCB-Induktivität können darüber liegen.
- **Nur bedingte Option:** Erst **OVP-Abschaltschwelle unter die Modulgrenze verlegen** und mit Worst-Case-Margen nachweisen, dass 30V Dauerbetrieb bei allen Toleranzen gewährleistet bleibt und am Modul-Eingang auch bei 202V-Puls niemals 36V Betriebsgrenze bzw. 40V Absolutgrenze erreicht wird. Hierzu müsste die LM74930-OVP-Dimensionierung bewusst neu eingefroren und der Stress dynamisch getestet werden. Das ist **mehr** als ein bloßer MPN-Tausch und schafft ein neues kritisches Proof Gate.
- **Urteil:** *guter späterer Kostensenkungs-/EMV-Kandidat*, **nicht** vor der ersten robusten PCB-Fertigung statt LMR38020 umstellen.

### B2: **TPSM65620SVCGR** – 3–65V, 2A, integrierte Induktivität, aber Katalogprodukt / derzeit kein Lager

- [TI TPSM65620](https://www.ti.com/product/TPSM65620), [exakte OPN TI](https://www.ti.com/product/TPSM65620/part-details/TPSM65620SVCGR), [DigiKey DE](https://www.digikey.de/de/products/detail/texas-instruments/TPSM65620SVCGR/29281629): 19-Pin 5,8×5,2mm eQFN-Modul, MOSFETs/Drossel/Capacitors integriert, **VIN 3–65V**, 2A, −40…+150°C **Junction**, interner OCP/TSD/Softstart. Deutlich größerer VIN-Bereich als TPSM33620.
- Hersteller-Einstufung ausdrücklich **„Catalog“**, nicht AEC-Q100 Automotive. **DigiKey Deutschland Lager 0**; 15.10.2026 je nach regionalem Schnappschuss ca 4,58–6,26€ netto bei1, 4,07–4,21€ netto bei100 und avisierter Eingang **Februar 2027**. Absolute Dati-/Preisangaben vor Beschaffung neu prüfen.
- **Urteil:** Für den Prototyp **nicht** empfohlen, solange AEC-Q-Spezifikation und unmittelbare Beschaffbarkeit fehlen. Auch ein 65-V-Modul muss gegen die 202-V-Fronttransienten nachgewiesen geschützt werden.

### B3: Bestehender **LMR38020SQDDARQ1** bleibt gesperrte, aber plausibel dimensionierte REV4-Basis

- [TI LMR38020-Q1](https://www.ti.com/product/LMR38020-Q1), 4,2–80V, 2A, Automotive AEC-Q100; hat bereits integrierte Leistungsschalter, Strombegrenzung, thermischen Schutz und interne Kompensation. Die externe 15-µH-Drossel mit realer Isat und DC-Bias/PCB-Kühlung ist noch zu verifizieren. Keine vorläufige Neuqualifikation durch den 36-V-Modulwechsel erzwingen.
- **Urteil: Beibehalten.** 80V-Wandler hinter 202V-abtrennender Schutzstufe mit nominellem OVP ~35,9V bietet deutlich mehr Spannungsspielraum als 36V-Modul. Eine Serien-/2A-Thermik-Garantie ist das nicht.

## C. Zusätzlich elektronische RAW-Ausgangsabsicherung P05/P10

### C1: **TPS1H200AQDGNRQ1**, AEC-Q100 Single-Channel-High-Side mit integrierter FET

- [TI TPS1H200A-Q1](https://www.ti.com/product/TPS1H200A-Q1), [konkrete aktive OPN](https://www.ti.com/product/TPS1H200A-Q1/part-details/TPS1H200AQDGNRQ1): **3,4–40V** Eingang, Max Last2A, **einstellbare Stromgrenze 0,25–5A**, spezifiziert ±15% ab500mA, abschaltend/latch/auto-retry parametrierbar, −40…125°C, integrierte FET (200mΩ typ) und TSD. Bei RAW=1A nominell 0,2W Leitverluste typ. und ca **0,2V** Spannungsabfall, kein Null-Verlust.
- Kann **hinter LM74930** die RAW-Buchse bei Kurzschluss unabhängig abschalten und so den 5V-Zweig gegen einen RAW-Fehler besser isolieren; beseitigt aber nicht die **gemeinsame Hauptsicherung** und ersetzt nicht deren Kabelschutz.
- **RISIKO:** max40V am Zweig gegen LM74930 OVP35,9V nominal lässt nur etwa4,1V statische Reserve, **ohne** reale OVP-Eck-/Schaltüberschwinger. Vor Festlegung **maximale RAW-Spannung** während 202V-Eingangspuls messen/belegen. Außerdem muss `VIN_PROTECTED_UNFUSED` bei einem zwischengeschalteten High-Side ggf. korrekt als RAW_`SWITCHED_CURRENT_LIMITED` umbenannt und die Schnittstellenanforderung aktualisiert werden.
- **Urteil:** Option, **wenn echte unabhängige RAW-1A-Kurzschlussisolation** wichtiger ist als Stückkosten, PCB-Fläche und zusätzliche Fehlerpfade; **nicht** blind zu REV4 hinzufügen.

### C2: **TPS1HTC30-Q1**, 6–60V / 30mΩ typ, starke Automotive-High-Side-Alternative

- [TI TPS1HTC30-Q1](https://www.ti.com/product/TPS1HTC30-Q1): 6–60V (C-Variante bis70V), bis6A, thermischer Schutz, einstellbare Strombegrenzung **erst ab2A** (bis16A), −40…125°C, 14-Pin-HTSSOP.
- Damit **besserer Betriebsspannungsspielraum** als TPS1H200A, aber **keine sinnvolle 1A-Stromgrenze**, größere Baugruppe und Mehrkosten für eine nominale1A-RAW-Leitung; RAW-Leiterbahnen müssten auch den mindestens2A-Fehlerstrom sicher führen.
- **Urteil:** Für 1A-AUX derzeit nicht der passende Aufwand/Nutzen.

## D. Integrierter Ersatz für gesamten 202V-Hauptschutz P01/P03/P04/P05

- [TI LM74930-Q1](https://www.ti.com/product/LM74930-Q1) ist bereits ein **integrierter Automotive-Ideal-Diode-/Surge-Stopper mit OVP, UVLO, elektronischem OCP/SCP und getrennten Back-to-Back-MOSFET-Gates**. [LM74930Q1EVM](https://www.ti.com/tool/LM74930Q1EVM) ist die direkte Herstellerreferenz für ~200V Load-Dump.
- Die evaluierten 40V/60V/65V internen MOSFET-High-Side-Switches und 36V/65V Buckmodule **können nicht** als direkter Ersatz für den Eingang mit **202V/350ms** dienen. Ein integrierter Automotive 9–30V/2A/RAW1A/202V/350ms-FET-eFuse mit **nachgewiesener** gleicher Schutzfunktion und thermischem Impulsverhalten wurde in diesem Marktcheck **nicht** identifiziert.
- Externe Q301/Q302-FET-SOA, **56V-Zener**/R313–315-Pulsbelastbarkeit und F_MAIN bleiben eigene Pflichtnachweise. Nicht wegen eines unbewiesenen „neuen 200V-IC“ wieder komplett umbauen.

## E. Klare priorisierte Entscheidung gegen Entwicklungsschleifen

| Blocker | Maßnahme | Status |
| --- | --- | --- |
| **P02** diskrete EN-Pegel | TPS38-Q1 dual OD als kontrollierte **REV5-Schaltungsvariante** durchrechnen, danach einmal KiCad-/ERC-Netlist integrieren. | **UMSETZUNGSKANDIDAT** |
| **P08** integrierte 5V/2A-Stufe | TPSM33620S5QRDNRQ1 ist der ernsthafte COTS-„fertig Modul“-Kandidat; 36V-Proof-Gap gegenüber OV35,9V **verhindert jetzt** einen Drop-in-Swap. TPSM65620 ist nicht Automotive und nicht lieferbar. | **BEIBEHALTEN: LMR38020-Q1** |
| **P05/P10** isolierter RAW-1A-Kurzschluss | TPS1H200A-Q1 als spätere Option, wenn unabhängige Fehlerisolation verlangt wird und 40V-Spitzengate bewiesen ist. | **OPTIONAL, keine REV4-Änderung** |
| **P01/P03/P04** VS-Start/200V-SOA/puls-rated RVS | Im vorhandenen LM74930 Hersteller-Referenzdesign bleiben; kein gleichwertiger 202V-Integrated-FET-Ersatz belegt. | **COTS-ARCHITEKTUR BEREITS GEWÄHLT** |
| **P06** Effektivkapazität C308/C312 | Serien-MLCC-Herstellerkurven, keine IC-Abkürzung für effektives C(T,V,Alterung). | **DATEN/MESSUNG** |
| **P09** PCB/F_MAIN | Footprints, Stromschleifen, Leiterbahnen, wärmeleitende Kupferflächen und DRC; keine IC-Abkürzung. | **LAYOUT/TEST** |

**Änderungskontrolle:** Aktive [REV4_DESIGN_BASELINE.json](REV4_DESIGN_BASELINE.json) bleibt **unverändert**. Kein KiCad/MPN-Wechsel, kein fab-release und keine neue „garantierte VIN-Grenze“ aus diesem Dokument. Ein möglicher späterer Buck-Modulwechsel erfordert eine *neue* Worst-Case-OVP-/Gate-/Front-FMEA und 202V-Abschaltprüfung; TPS38 ersetzt allein die **diskrete** Enable-Stufe.
