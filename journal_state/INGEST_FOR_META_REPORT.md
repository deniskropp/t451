⫻data/wiring:provenance/01
# Wiring Journal-as-Agent Provenance → meta-report-card-generation + CoherenceMonitorBridge

The operational journal agent (v0.2+) now emits two primary artifacts for downstream consumers every cycle:

1. `journal_state/current_tas.json` — living ledger of accepted + active TAS blocks (with status, parentage, confidence, horizon).
2. `journal_state/run_JAA-YYYY-MM-DD-001.json` — full machine-readable bundle (provenance + tas_blocks + deltas + forecast_summary). This is the direct analogue of the original `_provenance.json` but now co-located with state for easy discovery.

## Minimal ingestion example (Python)

```python
# ingest_journal_for_meta_report.py (example consumer)
import json, glob, os
from datetime import datetime

def load_latest_journal_run(state_dir="journal_state"):
    runs = sorted(glob.glob(os.path.join(state_dir, "run_JAA-*.json")))
    if not runs:
        return None
    with open(runs[-1]) as f:
        return json.load(f)

def load_current_tas(state_dir="journal_state"):
    path = os.path.join(state_dir, "current_tas.json")
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)

def build_meta_report_payload(state_dir="journal_state"):
    run = load_latest_journal_run(state_dir) or {}
    ledger = load_current_tas(state_dir)
    prov = run.get("provenance", {})
    return {
        "card_title": f"Journal-as-Agent Delta — {prov.get('cycle_id')}",
        "generated": prov.get("timestamp") or datetime.now().isoformat(),
        "primary_projects": ["t451 / Journal-as-Agent MVP", "meta-infrastructure (KickLang, OCS, TAS)"],
        "tas_extracted": ledger.get("tas_blocks", []),
        "deltas_proposed": run.get("deltas", []),
        "forecast_summary": run.get("forecast_summary", {}),
        "coherence": ledger.get("coherence_last", {}),
        "provenance_sha": prov.get("memory_sha256_prefix"),
        "sources": ["journal_delta", "current_tas ledger", "run sidecar"],
        "next_action_hints": [d for d in run.get("deltas", []) if d.get("horizon") == "H0"]
    }

if __name__ == "__main__":
    payload = build_meta_report_payload()
    print(json.dumps(payload, indent=2))
```

## Integration points (when full skills are active)

- **meta-report-card-generation**: Feed the payload above (or the raw run_*.json + current_tas.json) as the `⫻data/tas` and `⫻data/state` sections. The card should celebrate the operationalization milestone and surface the new TAS-JAA-001 / TAS-PAR-002 as in-progress.
- **CoherenceMonitorBridge**: On every journal run, the sidecar + any `coherence_signals` from Parallel_f wrappers should be emitted as time-series (flux/drift/valence). The gate report (coherence_gate_*.md) is the human trace of the same signal.
- **living-objective-tas-flow**: The `current_tas.json` + acceptance records become the persistent substrate. On objective shift detection the flow should re-TAS from the ledger + latest delta.
- **tas-forecast-cycle**: Future journal runs can be driven *by* a full tas-forecast-cycle instead of the MVP heuristic, then the journal simply formats and persists the authoritative forecast output + proposes operational deltas on top.

## Filesystem contract (for MCP / external tools)

- All run sidecars and the current_tas ledger live under `journal_state/`.
- A consumer can `list_dir` or glob `run_JAA-*.json` + read the latest + the ledger.
- When the real memory.md updates (or a GitHub t-repo push lands), a watcher/cron triggers a new `--once` run; the sidecars accumulate history.

This wiring is intentionally filesystem + JSON first (no heavy service mesh) so it works in the current local OCS node (Berlin Node, Jetson targets, etc.) and can later be upgraded to full MCP tool exposure.

⫻end/wiring
