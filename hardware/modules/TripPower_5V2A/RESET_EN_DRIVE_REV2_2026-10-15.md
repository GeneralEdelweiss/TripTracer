# TripPower – RESET/EN-Ansteuerung Rev. 2: hochspannungsfeste VS-only-Stufe (15.10.2026)

**Konstruktiv behobene Fehler:** keine Q303-NMOS-Source-Follower-Hochseitenklemme, kein D306/D308-BAS70-Hot-Leckstrom mehr im hochohmigen RESET-Kreis, keine D307-Zenerklemme mit ungeklärtem Kleinstrom, **kein direkter elektrischer RUN_CMD→CTRL_EN-Strompfad**, und keine permanente EN-Ladung durch C309 (DNP). Eingebaut in eigenständige KiCad-10-Projektseiten. **ABER:** Kein belastbarer Funktions- oder ISO-/Fahrzeugnachweis für −40…+125°C/202V; siehe unten.

## Warum nicht einfach RESET direkt mit CTRL_EN verbinden?

TPS3760A012DYYRQ1 RESET hat zwar LOW ≤0.30V bei bis zu 5mA (VDD 2.7–65V), das wäre selbst unter dem LM74930 ENF(min) 0.41V, aber die bisherige Hysterese nutzt RESET als analogen Rückkopplungsknoten, und der bisherige RUN-Eingang wäre bei USB-only/fehlendem VIN direkt mit EN verbunden. Ein starker dauerhafter AUTO-Pullup an RESET würde darüber hinaus bei VIN=9V den 9.9kΩ-VS-Vorwiderstand belasten und die VS-Vorladung gefährden. Ein Dioden-ODER mit Schottky-Vf löst das nicht.

## Realisierter, galvanisch nicht getrennter, aber VS-only gespeister Hardwarepfad

```text
 VIN_FUSED -- 9.9k R313/314/315 --> VS_CLAMP (C302 + C308)
                                         |
                        U302 TPS3760-Q1 RESET (OD)
                              |          |
                        R339 1M         R333 1M --> VS
                              v
                           Q304 NPN READY (B1)
                              C3
 PNP Q303 BASE <-- R337 220k -+
         |                    E2---- RUN_BYPASS_NODE --- R319 0R AUTO --- GND
       R336 47k                        |
         |                             D305 BAS116Q A1/K3
       VS_CLAMP                         |
                                       RUN_SINK_C --> Q305 NPN (C3)
                                                         E2 --> GND
RUN_CMD -- R317 4.7k --> RUN_BASE --> Q305 B1; R341 100k base pulldown

VS_CLAMP --> Q303 PNP E2  [PMBTA92-Q 300V AEC-Q101]
                    C3 --> PNP_OUT --> R318 68k --> CTRL_EN --> R316 22k --> GND
                           CTRL_EN only sourced from VS, never from RUN_CMD
```

**Logik:** RESET=LOW ⇒ Q304 aus ⇒ PNP-Basis via R336 hoch auf VS ⇒ Q303 aus ⇒ R316 zieht LM74930.EN nach GND. RESET=freigegeben und (R319 bestückt für AUTO oder RUN high an Q305-Basis, wodurch beide NPNs in Serie leiten) ⇒ Q303 PNP an ⇒ EN aus VS über R318. Bei RUN HIGH und VIN=0 speist der RUN-Eingang nur die Basis von Q305 über R317; D305 blockiert Basis-Kollektor-Rückspeisung von Q305 in Q304/VS. Die RUN-Diode ist **nicht** mehr direkt mit CTRL_EN verbunden.

**Echte Portabilität / Pinouts:** Q303 Nexperia [PMBTA92-Q](https://assets.nexperia.com/documents/data-sheet/PMBTA92-Q.pdf) PNP, Q304/Q305 [PMBTA42-Q](https://assets.nexperia.com/documents/data-sheet/PMBTA42-Q.pdf) NPN, alle 300V AEC-Q101 SOT23 **B1/E2/C3**. Beide Bibliotheks-Symbole `TripPower_Sym` und die Cached-Symbole wurden auf KiCad-Bildschirm-Y geprüft und berichtigt: tatsächlicher Netlist-Nachweis `Q303.2 VS_CLAMP`, `Q303.3 PNP_OUT`, `Q304.2 RUN_BYPASS_NODE`, `Q304.3 PNP_SINK`, `Q305.2 GND`, `Q305.3 RUN_SINK_C`.

D305 ist Diodes [BAS116Q-7-F](https://www.diodes.com/datasheet/download/BAS116.pdf), automotive **dreipoliges SOT23** mit **Anode 1 → RUN_BYPASS_NODE**, **Kathode 3 → RUN_SINK_C**, NC2 unbeschaltet – der alte generische 2-Pin-SOD323-Footprint war falsch! Neues natives `TripPower_Sym:BAS116Q_A1_K3_NC2` und Standard-KiCad SOT23. Hersteller-Datenblatt spezifiziert typ. 3pA und ≤5nA @75V/25°C sowie **≤80nA @75V/150°C, kurzer Prüfimpuls**. Physische 3D-/PCB-Orientierung weiterhin visuell prüfen.

## Nominale Zahlen, keine Worst-Case-Freigabe

| Bereich | Berechnung |
|---|---|
| AUTO READY bei VS8V, ideal durchgeschalteter PNP | `VEN=8×22/(68+22)=1.956V`, über LM74930 ENR(max) 1.05V |
| Freigabeschwelle nominal | `R330=825k, R331=100k, R332=1M, R333=1M` + NPN-Q304-Basislast R3391M: ca. **7.974V** |
| Rückfall nominal | mit NPN VBE **angenommen** 0.7V: ca. **5.998V** |
| VS-Puffer bei VIN9V vor Freigabe | Beispiel mit LM74930 OFF5µA, TPS3760 max2.6µA, C308 10µA, Sense/R333 ~17µA: `VS≈8.66V` - **keine garantierte Heiß-/Kaltreserve** |
| Q303 Basis bei VS8V | `(8−0.7)/220k−0.7/47k≈18.3µA`; Q304 benötigt wegen 1M Pullup/Basisteiler nur etwa 2–3µA Basisstrom |
| Q303 maximale ohmsche Verlustleistungs-Obergrenze, VS65V | `VS²/(4×68k)≈15.5mW` bei ausschließlich diesem Speisepfad; PMBTA92-Q FR4-Referenz erlaubt bei125°C nach 500K/W nominal `(150−125)/500≈50mW` |
| R318 maximale Verlustleistung, VS65V | `VS²/68k≈62mW`; 1206 MPN mit genügend Derating / Pulsfestigkeit wählen |
| Q303 zulässige Collector-Off-Leckage zum sicheren LM74930 AUS bei 125°C | `(0.41V/22k)−0.2µA≈18.4µA`, unter Widerstandstoleranzen geringfügig weniger |

**Die Grenzen der Auslegung sind ausdrücklich offen:** 
1. Nexperia PMBTA92-Q/PMBTA42-Q nennen hFE_min bei **1mA bzw. 10mA unter 25°C/kurzem Puls**, nicht bei Q304-I_B ~2–3µA und Q303-I_C ~90µA über −40…125°C. Die Schaltung muss bei −40/25/85/125°C mit realen Transistor- und Leckmodellen plus Messung zeigen, dass sie **EN HIGH >1.05V** sicher erreicht.
2. Q303 collector leakage `ICEO/ICBO` über 125°C bei unserer Anschlussart ist **nicht** mit ≥18µA-Garantie dokumentiert. Eine qualifizierte alternative Transistor-MPN, starker pulldown / höhere Ausgangsspeisung oder integrierte Ausgabestufe wäre zur Garantie erforderlich.
3. U302 RESET high ist **kein idealer Spannungsausgang**; Q304 zieht Basisstrom durch R3331M/R3391M, was die Schmitt-Hysterese verändert. Die 7.974/5.998V gelten nur bei modelliertem VBE 0.7V ohne HFE-/Ceff-/Temperatur-/Leckeffekte; korrespondierendes [Rechenprogramm](../../../tools/check_trippower_reset_worst_case.py) gibt Szenariobänder aus, keine garantierten Trip-Punkte.
4. `D305` SOT23-K3/A1/NC2 ist gegen USB→VS-Rückspeisung so gepolt, aber Garantie gegen alle Halbleiterleck-/ESD-Wege, insbesondere wenn Q305 B high bei VIN0, erfordert Tests.
5. 202V/350ms Load-Dump- und heißer Q301 SOA/F_MAIN/Q302/OCP/C303–CAP sind **nicht freigegeben**. KiCad-ERC und Netzliste belegen nur Beschaltung, kein Fahrzeugverhalten. **Keine Platine fertigen**.

## Cost-first

Drei diskrete SOT23-BJTs `PMBTA92-Q` (1×) + `PMBTA42-Q` (2×) und fünf Standard-1206-Widerstände bilden die neue VS-only-Steuerung; BAS116Q war bereits vorgesehen, wurde nun korrekt in den unteren RUN-Sink-Pfad versetzt. Vollständiger 1/10/100-PCBA-Preis und konkrete R-MPNs noch nicht geprüft. Nexperia-Bausteine sind Automotive-Produktreihen, keine Garantie für Kleinststrom-HFE im konkreten Design. Das technisch einfachere direkte RESET→EN verworfen wegen Rückkopplungs-/Vorladestrom- und USB-Backfeed-Konflikt.

**Stand:** Ein älterer fehlerhafter NMOS/Schottky-Prototyp wurde **tatsächlich** in KiCad ersetzt. Das spezifische alte Fehlerbild ist topologisch beseitigt, aber diese REV2 bleibt **`ELECTRICAL_RELEASE_BLOCKED`** bis zu garantierten BJT-Kleinststromkennwerten oder vollständigem Labortest. Nächster geeigneter Prüfpunkt ist ± VIN9V, −40/125°C, 30V Dauerbetrieb und 56–65V VS-Klemme; bei Scheitern gezielt höher verstärkende COTS-Logik statt unkontrolliert mehr Zusatztransistoren.
