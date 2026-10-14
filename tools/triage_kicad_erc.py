#!/usr/bin/env python3
"""Produce actionable KiCad 10 ERC triage without suppressing violations.

Usage: python3 tools/triage_kicad_erc.py reports/erc.json reports/erc-triage.md
"""
import collections
import json
import pathlib
import sys

def triage(report):
    sheets=report.get("sheets",[])
    aggregate=collections.Counter()
    entries=[]
    for sh in sheets:
        path=sh.get("path","?")
        per=collections.Counter()
        for v in sh.get("violations",[]):
            key=(v.get("type","unknown"),v.get("severity","unknown"))
            aggregate[key]+=1
            per[key]+=1
        entries.append((path,per))
    lines=["# KiCad 10 ERC – vollständige Fehlerübersicht","",
           "Automatisch aus dem unveränderten KiCad-ERC-JSON erzeugt. **Keine ERC-Freigabe.**",
           "",f"KiCad-Version: {report.get('kicad_version','?')}","",
           "## Fehlertypen","",
           "| Typ | Severity | Anzahl |","|---|---|---:|"]
    for (kind,severity),count in sorted(aggregate.items(),key=lambda kv:(-kv[1],kv[0])):
        lines.append(f"| `{kind}` | {severity} | {count} |")
    lines += ["","## Fehler je Hierarchieseite","","| Seite | Fehler/Warnungen | Schwerpunkt |","|---|---:|---|"]
    for path, per in sorted(entries,key=lambda row:-sum(row[1].values())):
        total=sum(per.values())
        if not total: continue
        biggest=", ".join(f"{k[0]}: {v}" for k,v in per.most_common(3))
        lines.append(f"| `{path}` | {total} | {biggest} |")
    lines += ["","## Nächster Korrekturdurchlauf","",
              "1. Stromversorgungs- und Anschlussfehler in der aktiven Versorgung vor kosmetischen Grid-Warnungen beheben.",
              "2. Grid-Warnungen über tatsächliche Endpunkt-/Pin-Koordinaten auf KiCad-Verbindungsgitter korrigieren, nicht ignorieren.",
              "3. Unverbundene Designseiten nur nach elektrisch vollständiger Migration aktivieren; keine künstlichen PWR_FLAGs.",
              "4. Nach jedem Änderungsschritt projektweiten KiCad-ERC erneut ausführen und die vollständigen JSON-Artefakte behalten.",""]
    return "\n".join(lines),aggregate

def main():
    if len(sys.argv)!=3:
        raise SystemExit("Usage: triage_kicad_erc.py erc.json triage.md")
    source=pathlib.Path(sys.argv[1]);dest=pathlib.Path(sys.argv[2])
    md,counts=triage(json.loads(source.read_text(encoding="utf-8")))
    dest.write_text(md,encoding="utf-8")
    print(f"Triaged {sum(counts.values())} ERC violations -> {dest}")
if __name__=="__main__":
    main()
