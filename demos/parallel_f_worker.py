#!/usr/bin/env python3
"""
parallel_f_worker.py
The "native" / hot-path worker for the Parallel_f + KickLang wrapper contract.

This is the separate process / compiled binary stand-in that the thin shim calls via subprocess (or would call via ctypes/pybind in real C++).

It implements the aggregation logic (forecast horizon rollup + risk + coherence derivation) that was previously inlined.

Contract:
- Invoked as: python3 parallel_f_worker.py --node <node_id> --payload '<json>'
- Or via JSON on stdin in future extensions.
- Outputs a single JSON object to stdout (the "native_result" part before shim wrapping).
- On error: non-zero exit + error text on stderr.

This separation demonstrates the real FFI / IPC boundary the spec calls for.
Used by the demo for "real" subprocess path + benchmarking.
"""

import argparse
import json
import math
import random
import sys
import time
from typing import Dict, Any

def aggregate_forecasts(tas_inputs: list) -> Dict[str, Any]:
    """Core 'parallel' / vectorized work (the expensive kernel)."""
    if not tas_inputs:
        tas_inputs = [
            {"id": "TAS-JAA-001", "h0": 0.94, "h1": 0.82, "risk": 0.06},
            {"id": "TAS-PAR-002", "h0": 0.89, "h1": 0.78, "risk": 0.11},
        ]

    start = time.time()

    aggregated: Dict[str, float] = {"H0": 0.0, "H1": 0.0, "H2": 0.0, "H3": 0.0}
    total_risk = 0.0
    count = max(1, len(tas_inputs))

    for t in tas_inputs:
        h0 = float(t.get("h0", 0.8))
        h1 = float(t.get("h1", 0.7))
        risk = float(t.get("risk", 0.1))

        # Simulated "native optimization" lift (better locality, SIMD, etc.)
        lift = 0.015 + (random.random() * 0.01 - 0.005)
        aggregated["H0"] += min(0.98, h0 + lift)
        aggregated["H1"] += min(0.90, h1 + lift * 0.8)
        aggregated["H2"] += min(0.80, (h0 + h1) / 2 - 0.05)
        aggregated["H3"] += min(0.65, (h0 + h1) / 2 - 0.12)
        total_risk += risk

    for h in aggregated:
        aggregated[h] = round(aggregated[h] / count, 3)

    avg_risk = round(total_risk / count, 3)
    kernel_time = (time.time() - start) * 1000

    coherence_flux = "low" if avg_risk < 0.12 else "medium"
    coherence_drift = round(max(0.0, avg_risk - 0.05), 3)
    coherence_valence = round(0.22 - (avg_risk * 1.2), 2)

    return {
        "aggregated_horizons": aggregated,
        "average_risk": avg_risk,
        "parallel_degree": min(8, max(2, len(tas_inputs) * 2)),
        "suggested_tas": [
            {"id": "TAS-PAR-003", "desc": "Benchmark real Parallel_f impl vs Python baseline for forecast aggregation", "horizon": "H1"},
            {"id": "COH-EMIT-001", "desc": "Emit aggregated coherence signals to CoherenceMonitorBridge for this cycle", "horizon": "H0"},
        ],
        "internal_metrics": {
            "kernel_time_ms": round(kernel_time, 2),
            "reduction_efficiency": round(0.87 + random.random() * 0.08, 2),
        },
        "_coherence_internal": {
            "flux": coherence_flux,
            "drift": coherence_drift,
            "valence": coherence_valence,
            "notes": f"Native aggregation over {len(tas_inputs)} TAS inputs; risk rollup {avg_risk}"
        }
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--node", required=True, help="Node ID (e.g. parallel-forecast-aggregator)")
    parser.add_argument("--payload", required=True, help="JSON payload string")
    args = parser.parse_args()

    try:
        payload = json.loads(args.payload)
    except Exception as e:
        print(f"ERROR: bad payload JSON: {e}", file=sys.stderr)
        sys.exit(2)

    tas_inputs = payload.get("tas_forecasts", [])
    result = aggregate_forecasts(tas_inputs)

    # The worker outputs the raw native result (shim will wrap with full contract)
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0)

if __name__ == "__main__":
    main()
