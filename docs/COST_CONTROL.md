# TripTracer V1 – laufende Gesamtkostenkontrolle

**Stand: 13.10.2026 · Status: KEINE belastbare Gesamt-BOM oder Fertigungspreiskalkulation.** Ziel ist der **günstigste nachweislich taugliche** Rallye-Tripmaster, nicht ein möglichst teures Automotive-Elektronikprojekt. Kein verbindliches Gerätebudget oder Verkaufspreis vom Nutzer festgelegt; **keine künstliche Budgetobergrenze** annehmen.

## Systemstatus der Kalkulation

- Bestehendes `hardware/kicad/TripTracer_V1_BOM_DRAFT.csv` umfasst derzeit **21 vorläufige Positionen** und unvollständige Hardware; die Felder `Einzelpreis_1/10/50/100` sind noch leer. **Eine gesamte V1-Stückkostensumme ist dadurch derzeit nicht seriös berechenbar.**
- Die historische, überdimensionierte LTC4380-/TPS26631-/250-V-FET-Eingangsschutz-Variante ergibt bei einer Teil-BOM **21,92 €/Gerät** im Einzelbezug; **nicht als neues Kosten-/Sicherheitsminimum übernehmen**. Die detaillierte, uneinheitlich verifizierte Preisschätzung ist in [SOLID_STATE_POWER_ARCHITECTURE.md](SOLID_STATE_POWER_ARCHITECTURE.md) archiviert.
- LM74800-Q1-Eingangsschutz-Forschung deutet auf ca. **9,13–10,13 €/Gerät für eine vereinfachte Teil-Surge-Schutz-BOM** hin (Einzelmengen, netto, teilweise Schätzmaterial, **ohne** elektronische Strombegrenzung/Auto-Retry, unabhängige Abschaltung, ACC/HOLD, USB, Fertigung). **Das ist kein vollständiger Vergleich der Gesamtsystemkosten**. Kein Kosten- oder Funktionsvorteil behaupten, ehe beide Varianten denselben Schutzumfang und Prüfnachweis liefern.

## Pflichtstruktur je Baugruppe

| Prüffeld | Immer ausweisen |
|---|---|
| Pflichtfunktion / Prämisse | Exakt welche HW-/PWR-Anforderung und welchen Fehlerfall erfüllt das Teil? |
| Preisgünstige Basisoption | Vollständige, norm-/lastgerecht dimensionierte funktionale Option, ggf. Automotive-Referenzdesign |
| Teurere Alternative | Konkreter zusätzlicher Nutzen, was entfällt, welche Zusatzbauteile sind zwingend? |
| Gesamte Bauteilkosten | MPN, Menge, Quelle/Datum, **2/10/100 Stück**, Steuer-/Versand-/Bestückungsstatus |
| PCB-/Fertigungsfolgen | Mehrfläche, nötige Kupferfläche, thermische Anbindung, 2/4 Lagen, JLC Basic/Extended, zweite Seite, manuelle Arbeit |
| *Inkrementelle* Mehrkosten | €/Gerät und Gesamtkosten für jeweilige Stückzahl, gegenüber der **gleichen Funktionsspezifikation** |
| Technische Entscheidung | günstigere nachweislich ausreichende Variante bevorzugen; teurere nur mit konkretem Nutzen |
| Unsicherheit | Endpreise/Verfügbarkeit, Automotive-/SOA-/EMV-/ERC-/DRC-Prüfung explizit „offen“ |

**Keine künstliche Redundanz:** Zwei in Serie geschaltete teure Controller sind nicht allein durch das Wort „Sicherheit“ gerechtfertigt. Zuerst gemeinsame Fehlerfälle, unabhängige Abschaltanforderungen und bereits integrierte Schutzfunktionen betrachten. Die Pflichtfunktionen Kurzschluss-/Leitungsschutz, Kfz-Transienten, Verpolung, sichere SD-Abmeldung, USB-Entkopplung bleiben erhalten; der preisgünstigste Weg zu **nachweisbar** sicheren Funktionen gewinnt.

## Kostenrisiken für die Gesamtrechnung, derzeit priorisiert

| Baugruppe / Kostenthema | Nachweisbarer Stand / Risiko | Kostenkontrolle vor Festlegung |
|---|---|---|
| **Eingangsschutz, ACC-HOLD** | In bisheriger Designstudie **21,92 € Teil-BOM** für Doppelcontroller, neue alternative Teil-BOM **9,13–10,13 €** unvollständig | vollständige Funktionsvergleichs-BOM mit realen Lieferartikeln, SOA und Test-A-Ziel; zweiten Controller nur bei unverzichtbarer Funktion |
| **6 FILN-Leuchttaster** | Projektanforderungen nennen ca. **3,20 USD je Taster**, FILN-Versand **28 € pro Bestellung** als bisherigen Ansatz | Alternative mit vergleichbarer Haptik/Lebensdauer, Versandbündelung; Kosten der Taster **plus** Auslösekabel/Ring-LED berücksichtigen |
| **Riverdi-Display + Beleuchtung** | Hochwertiges 3,5-Zoll-Display, Boost-/LED-Treiber und Einbau; noch kein finaler Gesamtpreis | komplettes Modul inkl. Versand und Backlight-Treiber bepreisen; keine Displayänderung ohne Bewertung des Nutzerwerts |
| **GNSS/Antennenpfad** | MAX-M10N, aktive GNSS-Antenne und HF-Steckverbindung | Gesamtmodul-/Antennen- und Assemblierungspreis inkl. Steck-/Koaxteile erheben |
| **Platine 2 vs. 4 Lagen** | 2 Lagen bevorzugt, 4 erlaubt bei technischer Notwendigkeit | JLCPCB *konkretes* Angebot für 5 PCB/2 PCBA vergleichen, nicht pauschalen Kostenfaktor erfinden |
| **JLCPCB Basic/Extended** | BOM unvollständig, Kategorien noch nicht verifiziert | auch Bestückung/Feeder-/Extended-/Mindestmengen- und Non-Stock-Kosten einrechnen |
| **Mechanik/Service** | 3D-Gehäuse, M8-Kabel/Stecker, USB, Taster, Halter, Dichtung | Gehäuse-/Befestigungs-/Kabellängen und Versand/Steuern nicht außerhalb der „Teilekosten“ vergessen |
| **Lieferantenvielfalt** | LCSC/JLCPCB, DigiKey, Mouser, FILN möglich | Mindestbestellwerte, getrennte Fracht, Zoll/MwSt. und Nachbestellrisiken berücksichtigen |

## Entscheidungsschwellwert ohne erfundenes Euro-Budget

Jede neue Baugruppe startet mit **„Welchen Schutz oder welche Funktion brauchen wir wirklich?“**. Wenn die bevorzugte Lösung **wesentlich teurer** ist als eine ebenfalls spezifikationskonforme Alternative, vor Auswahl **Mehrpreis pro Gerät und technisches Alleinstellungsmerkmal** ausweisen; gegebenenfalls zurückstellen. Ein vermeintlicher Sicherheitsgewinn muss mit Datenblatt, Fehlerbaum und erforderlichem Test nachweisbar sein.

### Nächste konkrete Arbeitsschritte

1. Gesamte V1-Hierarchie aus KiCad in eine **vollständige vorläufige BOM** überführen, nicht bei den 21 Legacy-BOM-Positionen stehenbleiben.
2. **Einkaufskosten pro Stück und per 2/10/100 Geräte**, getrennt nach verifizierten Händlerpreisen, Schätzpreisen und unbekannten Preisen, vollständig gegenrechnen. Fehlende Preise **nicht als 0 €** verrechnen.
3. Preislich dominierende Baugruppen (Displays, Taster samt Versand, GNSS, Versorgung, PCBA, Gehäuse) nach Gesamteinfluss priorisieren und Angebote/Austauschbarkeit prüfen.
4. Vor KiCad-Auslegung neuer Eingangsschutz-Topologie die vollständig funktional **vergleichbare**, kostenoptimierte BOM auslegen; Sicherheits-/Ruhestrom-/SOA-Gates weiterführen.
5. Laufende Zwischenstände und Änderungen nach jeder Baugruppe hier dokumentieren; Änderungen an `main` erst nach Review/Merge.

**Keine Freigabe vor:** ERC/DRC, Pin-/Package-Kontrolle, Fahrzeugstörprofil, SOA/thermisches Derating, realer USB-Bordnetz-Rückspeiseschutz, SD-Flush, Mess- und Fertigungskostenbewertung.
