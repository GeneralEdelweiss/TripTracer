# TripPower Weg B – Round8 CI-Echtlauf, 16.10.2026

**Repo** `GeneralEdelweiss/TripTracer`; **Branch ausschließlich** `design/trippower-b`.

**Unabhängig über GitHub REST Jobs + tatsächlichen Job-Log + Artifact-API verifizierter Lauf**:

- **Lauf-URL:** https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38858861567
- **Run-ID:** `38858861567`.
- **Job-ID:** `116836339876`, Status **completed / success** (kein hypothetisches PASS).
- **Test-Commit:** `ad2f3323f87042be43914825a9c774d6c99ce6e9`. Die Vorlage `WEG_B_ROUND8_ACD_INDEPENDENT_REV6_SAFETY_REVIEW_2026-10-16.md`, CSV und Modelltests waren zu diesem Zeitpunkt enthalten.
- **Sichtbar im tatsächlichen Log:** sieben Python-Unit-Testgruppen mit **10+3+9+12+10+12+11 = 67 bestandenen Tests** und allen `OK`. Die **11 neuen A/C/D-Regressionsprüfungen** enthalten tatsächliche A-R-Werte, TPS26631 Factory-OV vs gezeichneter OV, 10V-UVLO-Swap-Falle, C-26600-Margin/Restart, D-LTC alle drei Input-Leakages, Fuse-Placement und strikte PASS/FAIL/OFFEN-CSV-Validierung.
- Ebenfalls `success` im selben Run: Native `kicad-cli sch erc` und tatsächlicher `kicad-cli sch export netlist` mit adversarial netlist check. **Achtung: Dies ist die GEERBTE REV5-B-Hierarchie, nicht der neue A-REV6-KiCad-Prototyp.** Das A-REV6-Projekt wird separat durch A auf dessen eigener Branch-CI geprüft. Der B-Run lädt nicht den anderen A-Branch nach und kann ihn deshalb nicht als eigene ERC-Prüfung deklarieren.
- Logs/Artefakt via GitHub API nachgewiesen: `trippower-b-independent-audit` **Artifact-ID 12028141770**, https://github.com/GeneralEdelweiss/TripTracer/actions/runs/38858861567/artifacts/12028141770. Dateien: `b-rev6-ACD-cross-audit-tests.txt`, `b-rev6-ACD-cross-audit.json` plus Altmodell-/KiCad-REV5-Berichte.
- **Regression der eigenen Reviewer-Mathematik:** ältere `rev6_practical_safety_model.py` hat fälschlicherweise `falling_max<=32` als Wiederanlaufgarantie gewertet; das wurde auf `falling_min>32` korrigiert und per Unit Tests fixiert. Ein Zwischenlauf `38858140434` war wegen Python-Dictionary-Syntax im neuen Modell **fehlgeschlagen**; korrigiert über Commit `25a05c2...` und in obigem vollständigen erfolgreichen Echtlauf erneut geprüft.

**Grenze dieser Evidenz:** Unit- und Source-Snapshot-Tests sind keine freigegebene Board-Revision. **Kein Labor PASS für 58V/350ms, 36V/400ms, OVP-Restart an realen 32V, HOT 5V2A/+60°C, safeOFF/+85°C, RAW0.5A, USB-/Backup-Backfeed, F_MAIN Kabelkoordination, KiCad-REV6-A als eigenen B-Netzlistenexport oder KiCad PCB DRC.** Keine reale Einzel-Fault-Injection, keine Fahrzeug- und keine Fertigungsfreigabe.

Nach Commit dieser Evidence-Datei muss, falls der HEAD neue Actions auslöst, für `HEAD` dessen eigene neue Run-URL/Conclusion erneut geprüft werden; oben ist nur die konkret geprüfte und erfolgreich gelaufene Test-SHA belegt.
