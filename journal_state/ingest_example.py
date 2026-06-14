#!/usr/bin/env python3
"""Tiny runnable example showing how meta-report-card-generation or CoherenceMonitor could consume journal provenance."""
import json
import glob
import os
from datetime import datetime

STATE_DIR = os.path.join(os.path.dirname(__file__), "..", "journal_state")

def load_latest_journal_run():
    runs = sorted(glob.glob(os.path.join(STATE_DIR, "run_JAA-*.json")))
    if not runs:
        return None
    with open(runs[-1], "r", encoding="utf-8") as f:
        return json.load(f)

def load_current_tas():
    path = os.path.join(STATE_DIR, "current_tas.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_consumer_payload():
    run = load_latest_journal_run() or {}
    ledger = load_current_tas()
    prov = run.get("provenance", {})
    return {
        "card_title": f"Journal-as-Agent Delta — {prov.get('cycle_id', 'unknown')}",
        "generated": prov.get("timestamp") or datetime.now().isoformat(),
        "primary_projects": ["t451 / Journal-as-Agent MVP", "meta-infrastructure (KickLang/OCS/TAS)"],
        "tas_extracted": ledger.get("tas_blocks", []),
        "deltas_proposed": run.get("deltas", []),
        "forecast_summary": run.get("forecast_summary", {}),
        "coherence": ledger.get("coherence_last", {}),
        "provenance_sha_prefix": prov.get("memory_sha256_prefix"),
        "sources": ["journal_delta", "current_tas ledger", "run sidecar"],
        "immediate_h0_next": [d for d in run.get("deltas", []) if d.get("horizon") == "H0"]
    }

if __name__ == "__main__":
    payload = build_consumer_payload()
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print("\n# Ready for meta-report-card-generation or CoherenceMonitorBridge ingestion.")
