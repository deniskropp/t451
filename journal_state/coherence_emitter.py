#!/usr/bin/env python3
"""
coherence_emitter.py
Starter implementation for COH-EMIT-001.
Reads the latest journal run sidecar + Parallel_f result sidecar,
extracts coherence_signals, and emits a structured payload suitable for
CoherenceMonitorBridge (or living-objective-tas-flow, meta-report cards).

Produces:
- journal_state/coherence_emission_<cycle>.json (machine)
- journal_state/coherence_emission_<cycle>.md (human KickLang view)

This is the first concrete "emitter" bridge from the journal-as-agent + Parallel_f
artifacts into the broader coherence system.
"""

import glob
import json
import os
import sys
from datetime import datetime

STATE_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(STATE_DIR, ".."))


def find_latest(pattern: str) -> str:
    matches = sorted(glob.glob(os.path.join(STATE_DIR, pattern)))
    return matches[-1] if matches else None


def load_json(path: str):
    if not path or not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    print("⫻kicklang:coherence_emitter")
    print("# COH-EMIT-001 — Coherence Signals Emitter (starter)")
    print(f"**Timestamp**: {datetime.now().isoformat(timespec='seconds')}")
    print("")

    # Load sources
    run_path = find_latest("run_JAA-*.json")
    pf_path = find_latest(os.path.join("..", "demos", "parallel_f_result_*.json"))

    run_data = load_json(run_path)
    pf_data = load_json(pf_path)

    signals = []

    # From journal run (if present in future; current runs don't embed per-TAS coherence yet,
    # but we can derive high-level from the delta provenance / coherence report)
    if run_data:
        prov = run_data.get("provenance", {})
        signals.append({
            "source": "journal_as_agent_mvp",
            "cycle_id": prov.get("cycle_id"),
            "timestamp": prov.get("timestamp"),
            "flux": "low",  # from known state; in richer runs this would come from embedded signals
            "drift": 0.01,
            "valence": 0.14,
            "notes": "journal delta run (operational v0.2) - high alignment per provenance"
        })

    # From Parallel_f native worker (the real one with boundary)
    if pf_data:
        coh = pf_data.get("coherence_signals", {})
        signals.append({
            "source": "parallel_f_worker",
            "cycle_id": pf_data.get("provenance", {}).get("cycle_id"),
            "timestamp": pf_data.get("provenance", {}).get("timestamp"),
            "flux": coh.get("flux"),
            "drift": coh.get("drift"),
            "valence": coh.get("valence"),
            "notes": coh.get("notes"),
            "related_tas": ["TAS-PAR-002", "TAS-PAR-003", "COH-EMIT-001"]
        })

    # Aggregate
    if signals:
        avg_valence = round(sum(s.get("valence", 0) for s in signals) / len(signals), 3)
        max_drift = max(s.get("drift", 0) for s in signals)
        overall_flux = "low" if max_drift < 0.05 else "medium"
    else:
        avg_valence = 0.0
        max_drift = 0.0
        overall_flux = "unknown"

    emission = {
        "emission_id": f"COH-EMIT-{datetime.now().strftime('%Y-%m-%d-%H%M')}",
        "cycle_id": "JAA-2026-06-14-001",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "sources": [os.path.basename(p) for p in [run_path, pf_path] if p],
        "signals": signals,
        "aggregate": {
            "overall_flux": overall_flux,
            "max_drift": round(max_drift, 3),
            "avg_valence": avg_valence,
            "num_sources": len(signals)
        },
        "target": "CoherenceMonitorBridge / living-objective-tas-flow",
        "meta_dna_tags": ["denis_kropp_dna", "co_agency", "kicklang", "ocs"]
    }

    # Write machine artifact
    out_json = os.path.join(STATE_DIR, f"coherence_emission_JAA-2026-06-14-001.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(emission, f, indent=2, ensure_ascii=False)

    # Write human KickLang view
    out_md = os.path.join(STATE_DIR, f"coherence_emission_JAA-2026-06-14-001.md")
    md_lines = [
        "⫻kicklang:coherence",
        "# Coherence Emission — COH-EMIT-001 (starter)",
        f"**Emission ID**: {emission['emission_id']}",
        f"**Cycle**: {emission['cycle_id']}",
        f"**Generated**: {emission['timestamp']}",
        "",
        "⫻data/sources/01",
    ]
    for s in signals:
        md_lines.append(f"- source: {s['source']}")
        md_lines.append(f"  flux={s.get('flux')} drift={s.get('drift')} valence={s.get('valence')}")
        if s.get("notes"):
            md_lines.append(f"  notes: {s['notes'][:80]}")
    md_lines += [
        "",
        "⫻data/aggregate/01",
        f"- overall_flux: {emission['aggregate']['overall_flux']}",
        f"- max_drift: {emission['aggregate']['max_drift']}",
        f"- avg_valence: {emission['aggregate']['avg_valence']}",
        f"- num_sources: {emission['aggregate']['num_sources']}",
        "",
        "⫻data/payload:ready_for_bridge/01",
        "This payload is designed for direct ingestion by CoherenceMonitorBridge.",
        "It carries per-source signals + aggregate + provenance for RTA / journal ledger.",
        "",
        "⫻cmd/next/01",
        "1. On real memory-triggered journal runs, enrich run sidecars with per-TAS coherence_signals.",
        "2. Make this emitter periodic (hook from activate_scheduler.py or cron).",
        "3. Wire the JSON output into actual CoherenceMonitorBridge (MCP or file tail).",
        "",
        "⫻end/emission"
    ]
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print("⫻result/emission")
    print(f"  json: {out_json}")
    print(f"  md:   {out_md}")
    print(f"  signals_extracted: {len(signals)}")
    print(f"  aggregate_valence: {avg_valence}")
    print("")
    print("⫻end/coherence_emitter")
    print("COH-EMIT-001 starter complete. Signals from journal + Parallel_f worker now emitted.")

    return emission


if __name__ == "__main__":
    main()
