# P02 – COTS-Auswahl: garantierte Automotive-Enable-Pegel für LM74930 (15.10.2026)

**Entscheidung: KONKRETER BEVORZUGTER KANDIDAT gefunden – TPS38A010122DSKRQ1 von TI. NOCH NICHT ins aktive REV4-KiCad eingebaut; NOCH KEINE garantierte 9-V-/Fahrzeug-/Fertigungsfunktion.** Die vorliegende Recherche erfüllt den P02-COTS-FIRST-Vergleich und ist die maßgebliche Untersuchung zum Ersatz der µA-BJT-Kette, nicht eine Aufforderung zur wiederholten Suche nach neuen Schaltungen.

## 1. Herstellergrenzen, echte Bestellnummer und Einkauf

1. [TI TPS38-Q1 Datenblatt (SNVSBI8E), Figure 5-1 (Seite 3)](https://www.ti.com/lit/ds/symlink/tps38-q1.pdf): Aus **TPS38A010122DSKRQ1** entschlüsselt:
   - Topologie `A`: **CH1 UV open-drain active-LOW, CH2 UV open-drain active-LOW**;
   - `01`/`01`: **beide Schwellwerte 0,8 V** (per äußeren Teiler, keine internen HV-Teiler);
   - `2`/`2`: **je 2% interne Hysterese**;
   - `DSK` **WSON-10, 2,5×2,5 mm**, `Q1` AEC-Q100 Automotive –40…+125 °C.
2. [TI TPS38-Q1 Datenblatt §7.3, §7.5 (Seiten 6–8)](https://www.ti.com/lit/ds/symlink/tps38-q1.pdf): VDD und RESET/SENSE im Betrieb **max 65 V**; SENSE 0,8-V-Eingang max **100 nA** unter den im Datenblatt spezifizierten Bedingungen; VDD IDD max **2,6 µA**; je RESET OD Leck max **300 nA bei 5,5V bzw. 65V**; RESET **VOL max 300 mV bei 5 mA Sinkstrom, VDD 2,7–65 V, −40…+125 °C**. POR max VDD 1,4 V für VOL 300 mV bei 15 µA. Diese OUTPUT-GRENZWERTE ersetzen die ungeregelten Q303/Q304/Q305 hFE-/Leckageannahmen.
3. [TI LM74930-Q1 Datenblatt §6.3, §6.5](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf): `EN` LOW sicher bei **≤0,41V**, HIGH sicher bei **≥1,05V**; `IEN` max **200nA**; `EN` zulässiger Eingang 0–65V, `VS` Betriebsbereich 4–65V. **TPS38 V_OL ≤0,300V < LM74930 EN_LOW 0,410V**, Differenz ≥110mV bei spezifizierter Sinklast und Versorgung; kein Transistor-Beta-Mindestwert mehr erforderlich.
4. [Mouser Deutschland TPS38A010122DSKRQ1](https://www.mouser.de/en/ProductDetail/Texas-Instruments/TPS38A010122DSKRQ1): Recherche-Snapshot rund **4.274 lagernd, 3,25 EUR bei 1 Stück, 2,45 EUR bei10, 2,03 EUR bei100**, Preise in EUR / vor Versand & Steuerabklärung. [TI Part-Detail](https://www.ti.com/product/TPS38-Q1/part-details/TPS38A010122DSKRQ1) gelistet als **ACTIVE**, direkter TI-Shop derzeit **out of stock**. Lieferbarkeit vor BOM-Freeze prüfen; geforderte Kleinstückzahlen bei Mouser vorhanden.
5. [Mouser TPS3760A012DYYRQ1](https://eu.mouser.com/en/ProductDetail/Texas-Instruments/TPS3760A012DYYRQ1) existierender REV4-U302: ca **2,30 EUR/1, 1,71 EUR/10, 1,40 EUR/100** als Snapshot. Delta Einzel-IC ungefähr **+0,95 EUR**; dafür entfallen diskrete PNP/NPN/Diode/Basis- und Treiberwiderstände sowie deren Temperatur-Qualifikation. Endgültige Stücklisten-/PCBA-Vollkosten prüfen.

### Verglichene Optionen

| Option | Beurteilung |
|---|---|
| **Aktiver REV4** TPS3760A012DYYRQ1 OD + Q303 PNP/Q304+Q305 NPN | Niedrige Bauteilkosten, jedoch **keine** Hersteller-Garantie für 10–50µA BJT-IC und Q303 I_CEO @+125°C → P02 derzeit BLOCKED |
| **Bevorzugt: TPS38A010122DSKRQ1** mit CH1 VS_READY, CH2 RUN_CMD und gemeinsamem OD `EN` | **Ein** AEC-Q100 65V-IC; zwei garantierte LOW-Ausgänge und definierte Ausgangsleckage; erspart 3 HV-BJT; bestellbar. WSON10 und Rückkopplungs-Verkopplung zur Hysterese sind **vor KiCad-Freeze** nachzuweisen. |
| 2× **TPS3760A012DYYRQ1** mit Open-Drain-AND | Gleicher garantierter OD-Pegel, weniger Änderung pro Kanal, aber 2× SOT23-14, mehr Bauteile/PCBA-Fläche und ca. 4,60 EUR pro2 IC. Gut dokumentierter Plan B für reproduzierbare Kanaltrennung. |
| Nur TPS3760 „PP-Ausführung“ | **Nicht ohne tatsächlich veröffentlichte/lieferbare passende Nummer!** Im TPS3760-Q1 Datenblatt Rev.B Table4-1 gibt es veröffentlichte PP-Low UV-Variante **BF05 mit 31V-Threshold**, für 9V ungeeignet. Ebenso PP-High H279 ist OV und nicht unser 8V-VS-UV; aus Katalogbezeichnung PP nicht einfach Bestellcode erfinden. |
| TPS3762-Q1 | 65V und Automotive, aber veröffentlicht nur OD-Low, ~4µA und BIST/ASIL-D-Sonderfunktion; kein Vorteil für zwei Kanäle RUN + VS gegenüber TPS38A. |

## 2. Topologievorschlag für spätere REV5 – OHNE KiCad-Umbau

**Einfaches wired-AND aus zwei Open-Drain-Ausgängen** (beide RESET1/RESET2 low sobald *ihr* Kanal einen Fehler sieht):

- TPS38 `VDD=VS_CLAMP`, `GND` wie U302; `SENSE1` kontrolliert `VS_CLAMP` mit **R_TOP≈715k/R_BOTTOM=100k**, plus bislang bewährte **R_FB≈1M** vom gemeinsamen Ausgang `CTRL_EN` nach `SENSE1`; CH1 `CTR1=330nF` wie alter C311. `CTS1` nur bei Bedarf entprellen.
- `RESET1` + `RESET2` sind **Open-Drain**, dürfen konzeptionell als gemeinsames `CTRL_EN` geschaltet werden, mit **nur einem Pull-Up von VS auf CTRL_EN**, vorläufig `R_PU=1M` (bestehendes R333). `CTRL_EN` direkt an **LM74930 EN**. Entfernt Q303/Q304/Q305, den 22k EN-Pulldown und die BAS116 RUN-Reihendiode; funktioniert im Latch-Modus **nicht** mit automatisch identischer alter RESET-Hysterese ohne erneute Netto-Rechnung.
- `SENSE2` überwacht bei RUN-Bestückung `RUN_CMD` (3,3V oder5V nominal) über z.B. **100k Serien-R + 1M Pulldown**, die RUN-Schwelle ist dann `0.8V*(1+100k/1M)≈0.88V` (ideal beim *Fall*, bei Wiederfreigabe ~0,898V). 3,3V liefert nominell ~3,0V an SENSE2. Am offenen RUN bleibt SENSE2 durch 1M nahe0V; max100nA Sense-Bias entspräche 0,1V – weit unter 0,792V. **RUN_CMD HIGH bei VIN0** ist dennoch ein *separater Rückspeise-/Ioff-Gate*: VDD<VDDmin → Hersteller max SENSE-I nicht zwangsläufig spezifiziert, trotz zulässigem SENSE-V-Grenzwert.
- Bei AUTO-Bestückung **RUN-Serien-R und Pull-Down DNP**, `SENSE2` über einen einzigen 0-Ω-Jumper direkt an `VS_CLAMP`, keine zusätzliche Precharge-Last; der RUN-Kanal ist damit bei VS≥4V immer READY. Bestückungsvarianten in BOM unterscheiden.
- Externe Feedback-Hysterese aus CH1 benötigt neue Berechnung, da bei RUN=LOW der **gemeinsame** RESET-Knoten low ist, auch wenn VS_READY intern schon high wäre. Das kann die Spannungsfreigabeschwelle abhängig vom RUN-Zustand verschieben. Vor dem Routing statisches und transientenzeitliches Verhalten für AUTO, RUN, langsame Ramps und RUN-high bei VIN0 kontrollieren; sonst statt bloß parallelgeschalteten RESET-Ausgängen getrennte Kanal-Logik oder doppelte TPS3760 verwenden.
- Alle Leiterbahnen am CTRL_EN bis65V und die 56V-Zener-Spitzen prüfen; **TI VDD/RESET max65V im Betrieb**, absolute70V nicht als erlaubten Dauerbetrieb benutzen. WSON-10 Pinout/zentralen Pad/Pin1 / fertigungsgerechtes Design gegen TI DSK-Tabelle und KiCad10 DRC prüfen.

### Vorläufige reproduzierbare HIGH-/LOW-Pegelrechnung

Für `R_TOP=715k, R_BOTTOM=100k, R_FB=1M, R_PULLUP=1M`, 1%-R-Spanne, TPS38 0,792–0,808V sense, 2%-Hysterese ±1,5% rel., ±100nA Sense-Bias, Output **max 300nA je OD** + LM74930 EN **max200nA**, statisch ideal und vor Layout/Thermik:

- Für beide Kanäle READY und `VS_CLAMP≈7,510V` ergibt sich das **rechnerische EN-HIGH-Szenarioband ~3,89–4,40V**; dies liegt selbst am unteren Modellrand erheblich über dem spezifizierten LM74930 **1,05V EIN**. Es ist **kein gesamt-System-/transientes Geräte-Garantie**, sondern Herstellerschwellen plus Widerstandsannahmen.
- Ist mindestens eine RESET-Ausgangsstufe aktiv LOW und ihre Gesamtsinklast **unter5mA**, garantiert TI den Ausgang nach spezifizierten VDD/Temperatur-Bedingungen **VOL≤0,300V**, somit LM74930 EN **unter0,410V AUS**. Mit 1M Pullup von VS selbst bei65V nur ~65µA, plus Feedback-Widerstand-Ströme: deutlich kleiner5mA (vollständig zu berechnen).
- Einfache Modell-Toleranzhülle für externe Rückkopplung von VS_READY ungefähr **6,75–7,51V ON** und **4,83–5,42V OFF**, falls RESET1/RESET2 tatsächlich gemeinsame OD-Logik wie angenommen; diese Hülle berücksichtigt noch keine Effekte aus Reset-Kondensator/partiell geladener C, 125°C-Isolation oder dynamischem VS. Sie **ersetzt** nicht die alte REV4-7,234/5,438V-Rechnung.

## 3. Klare noch offene Sachfragen – vor Schematic-Commit

1. **Rückkopplung:** gemeinsame OD-Ausgänge beeinflussen Feedback und damit die Freigabeschwelle, wenn RUN aus ist. VS- und RUN-Transitions-Matrix modellieren und vorzugsweise geeignete TI-EVM-Ausgangs-Wired-AND-Freigabe bestätigen.
2. **VS-Startup ist unabhängig vom Enable-Pegelnachweis weiterhin OPEN:** Versorgung beider Kanäle2,6µA max, VS-RVS=9,9k + MLCCs21µF; dynamisches LM74930 `I_VS(t)` beim Pumpen bleibt ohne garantiertes Max.
3. **Power-off USB/RUN:** RUN_CMD=5V/3,3V bei VIN_FUSED=0 darf nach Vertrag keine relevante VS-Rückspeisung erzeugen. Hersteller-Leck bei **VDD unter2,7V** nicht überversprechen; Schutzwert/Trennpfad vor finalem Design belegen.
4. **CTR-Zeit/Reset-Release:** 330nF nominal420ms mit TPS3760/38 min/max RCTR; min/max Ceff aus Hersteller, Teilentladung, RUN-Clean timing, Timingkoppelung von SENSE1/2 prüfen.
5. **Package/BOM:** DSK10 WSON-2,5mm keine Drop-in-Kompatibilität mit bestehendem U302 DYY14; Footprint geometrisch prüfen, Handlötbarkeit schlechter. Kosten und tatsächliche Kaufbarkeit Händler bei Freeze aktualisieren.
6. **202V-Zener/SOA/F_MAIN** sind vollständig separat BLOCKED; keine Schutzfreigabe aus „65V-IC“-Eigenschaft ableiten.

## 4. Konkreter nächster Entscheid

**Empfehle TPS38A010122DSKRQ1 als bevorzugte REV5-Entwicklungsvariante**. Der Ersatz der diskreten µA-BJT-Stufe durch in TI-Datenblatt spezifizierte Open-Drain-Ausgänge ist in Bezug auf garantierte EN-Pegel klar sinnvoller als eine erneute Widerstandsanpassung der drei Transistoren. Vor *aktiver* Änderung: Reset-Ausgangsverknüpfung, Run-Off-/VIN0-Ereignisse und Software-nahe AUTO/RUN-Bestückung rechnerisch und nach Datenblatt verifizieren. **REV4 ist unverändert die aktive Baseline; kein neuer Fertigungsauftrag.**
