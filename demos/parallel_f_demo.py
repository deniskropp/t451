#!/usr/bin/env python3
"""
parallel_f_demo.py
Reference end-to-end implementation of the Parallel_f + KickLang wrapper contract (v0.1).

This is the smallest viable "native hot path" demo:
- Simulates a high-performance C++/native Parallel_f worker (the "heavy" part).
- Provides the thin Python shim that KickLang / journal-as-agent talks to.
- Exercises the full node contract: payload in, context, result + metrics + coherence_signals + next_tas_hints + halt discipline.
- Tied to a live TAS: accelerates a sub-step of TAS-PAR-001 / TAS-JAA-001 (multi-horizon forecast aggregation + coherence rollup for the journal-as-agent cycle itself).

Run:
    python3 demos/parallel_f_demo.py

It produces:
- Console trace in KickLang/OCS style
- Full contract JSON result
- A small sidecar (demos/parallel_f_result_*.json) that can be consumed by the journal ledger or meta-report tools.

This demonstrates the bridge: fast native-style execution (here simulated) feeding directly into the living meta-infrastructure (coherence, TAS evolution, journal-as-agent).
"""

import json
import os
import random
import subprocess
import sys
import time
from datetime import datetime
from typing import Dict, Any, List

WORKER_PATH = os.path.join(os.path.dirname(__file__), "parallel_f_worker.py")


def pure_python_aggregate(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Baseline pure-Python version of the aggregation (for benchmarking the overhead of the wrapper boundary)."""
    tas_inputs = payload.get("tas_forecasts", []) or [
        {"id": "TAS-JAA-001", "h0": 0.94, "h1": 0.82, "risk": 0.06},
        {"id": "TAS-PAR-002", "h0": 0.89, "h1": 0.78, "risk": 0.11},
        {"id": "TAS-OCS-001", "h0": 0.93, "h1": 0.82, "risk": 0.07},
        {"id": "TAS-PAR-001", "h0": 0.90, "h1": 0.78, "risk": 0.10},
    ]
    start = time.time()
    aggregated: Dict[str, float] = {"H0": 0.0, "H1": 0.0, "H2": 0.0, "H3": 0.0}
    total_risk = 0.0
    count = max(1, len(tas_inputs))
    for t in tas_inputs:
        h0 = float(t.get("h0", 0.8))
        h1 = float(t.get("h1", 0.7))
        risk = float(t.get("risk", 0.1))
        lift = 0.015 + (random.random() * 0.01 - 0.005)
        aggregated["H0"] += min(0.98, h0 + lift)
        aggregated["H1"] += min(0.90, h1 + lift * 0.8)
        aggregated["H2"] += min(0.80, (h0 + h1) / 2 - 0.05)
        aggregated["H3"] += min(0.65, (h0 + h1) / 2 - 0.12)
        total_risk += risk
    for h in aggregated:
        aggregated[h] = round(aggregated[h] / count, 3)
    avg_risk = round(total_risk / count, 3)
    dur = (time.time() - start) * 1000
    return {
        "aggregated_horizons": aggregated,
        "average_risk": avg_risk,
        "parallel_degree": min(8, max(2, len(tas_inputs) * 2)),
        "suggested_tas": [
            {"id": "TAS-PAR-003", "desc": "Benchmark real Parallel_f impl vs Python baseline for forecast aggregation", "horizon": "H1"},
            {"id": "COH-EMIT-001", "desc": "Emit aggregated coherence signals to CoherenceMonitorBridge for this cycle", "horizon": "H0"},
        ],
        "internal_metrics": {"kernel_time_ms": round(dur * 0.6, 2), "reduction_efficiency": round(0.87 + random.random() * 0.08, 2)},
        "_coherence_internal": {
            "flux": "low" if avg_risk < 0.12 else "medium",
            "drift": round(max(0.0, avg_risk - 0.05), 3),
            "valence": round(0.22 - (avg_risk * 1.2), 2),
            "notes": f"Pure Python baseline over {len(tas_inputs)} inputs"
        }
    }


# --- The thin shim (now using real subprocess boundary to parallel_f_worker.py) ---

def invoke_parallel_f_node(node_id: str, payload: Dict[str, Any], context: Dict[str, Any], use_subprocess: bool = True) -> Dict[str, Any]:
    """
    Thin adapter / FFI boundary.
    KickLang (or journal-as-agent, or any OCS participant) calls this.
    Now exercises the *real* contract boundary: calls the separate parallel_f_worker.py via subprocess
    (exactly as the spec example: ["parallel_f_worker", "--node", ..., "--payload", json]).
    """
    start = time.time()

    # Enforce contract basics (KickGuard-style)
    if not context.get("consent", True):
        return {
            "success": False,
            "halt_reasons": ["consent flag false in context"],
            "coherence_signals": {"flux": "high", "drift": 0.4, "valence": -0.8, "notes": "consent violation"},
            "metrics": {"duration_ms": 0},
        }

    try:
        if use_subprocess:
            # The production-style boundary
            cmd = [sys.executable, WORKER_PATH, "--node", node_id, "--payload", json.dumps(payload)]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=context.get("timeout_s", 30))
            if proc.returncode != 0:
                raise RuntimeError(f"worker failed (code {proc.returncode}): {proc.stderr[:200]}")
            native = json.loads(proc.stdout)
            boundary = "subprocess"
        else:
            # Pure python fallback (for benchmark baseline)
            native = pure_python_aggregate(payload)
            boundary = "in-process"
    except Exception as e:
        return {
            "success": False,
            "halt_reasons": [f"parallel_f worker failure: {str(e)[:120]}"],
            "coherence_signals": {"flux": "high", "drift": 0.25, "valence": -0.4, "notes": "worker exception"},
            "metrics": {"duration_ms": round((time.time() - start) * 1000, 1)},
        }

    duration_ms = round((time.time() - start) * 1000, 1)

    coherence = native.get("_coherence_internal", {
        "flux": "low", "drift": 0.01, "valence": 0.2, "notes": ""
    })

    return {
        "success": True,
        "result": {
            "aggregated_horizons": native["aggregated_horizons"],
            "average_risk": native["average_risk"],
            "suggested_next": native.get("suggested_tas", []),
        },
        "metrics": {
            "duration_ms": duration_ms,
            "parallel_degree": native.get("parallel_degree", 4),
            "kernel_time_ms": native.get("internal_metrics", {}).get("kernel_time_ms", duration_ms * 0.6),
        },
        "coherence_signals": {
            "flux": coherence["flux"],
            "drift": coherence["drift"],
            "valence": coherence["valence"],
            "notes": f"{coherence['notes']} (via {boundary})",
        },
        "next_tas_hints": native.get("suggested_tas", []),
        "halt_reasons": [],
        "provenance": {
            "node_id": node_id,
            "cycle_id": context.get("cycle_id"),
            "tas_ids": context.get("tas_ids", []),
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "boundary": boundary,
        }
    }


# --- Demo driver: exercise the contract against the current JAA operational context ---

def run_demo():
    print("⫻kicklang:demo")
    print("# Parallel_f + KickLang Wrapper — End-to-End Reference Demo (v0.1)")
    print(f"**Timestamp**: {datetime.now().isoformat(timespec='seconds')}")
    print("**Tied TAS**: TAS-PAR-001 / TAS-PAR-002 + TAS-JAA-001 (operationalization acceleration)")
    print("")

    node_id = "parallel-forecast-aggregator"
    payload = {
        "node_id": node_id,
        "tas_forecasts": [
            {"id": "TAS-JAA-001", "h0": 0.94, "h1": 0.82, "risk": 0.06},
            {"id": "TAS-PAR-002", "h0": 0.89, "h1": 0.78, "risk": 0.11},
            {"id": "TAS-OCS-001", "h0": 0.93, "h1": 0.82, "risk": 0.07},
            {"id": "TAS-PAR-001", "h0": 0.90, "h1": 0.78, "risk": 0.10},
        ],
        "aggregation_mode": "horizon_risk_rollup",
    }

    context = {
        "cycle_id": "JAA-2026-06-14-001",
        "tas_ids": ["TAS-PAR-002", "TAS-JAA-001"],
        "meta_dna_tags": ["denis_kropp_dna", "meta_infrastructure", "kicklang", "co_agency"],
        "consent": True,
        "coherence_threshold": 0.08,
        "timeout_s": 30,
    }

    print("⫻flow/parallel_f:invoke")
    print(f"  node_id: {node_id}")
    print(f"  payload.tas_count: {len(payload['tas_forecasts'])}")
    print(f"  context.cycle_id: {context['cycle_id']}")
    print("  ... invoking shim → subprocess parallel_f_worker (real boundary) ...")
    print("")

    # --- Benchmark: pure Python baseline vs real subprocess wrapper boundary ---
    print("⫻benchmark:wrapper_overhead/01")
    t0 = time.time()
    pure = pure_python_aggregate(payload)
    pure_ms = (time.time() - t0) * 1000

    t1 = time.time()
    result = invoke_parallel_f_node(node_id, payload, context, use_subprocess=True)
    wrapped_ms = (time.time() - t1) * 1000

    overhead = round(wrapped_ms - pure_ms, 2)
    print(f"  pure_python: {pure_ms:.2f} ms")
    print(f"  subprocess_worker: {wrapped_ms:.2f} ms")
    print(f"  boundary_overhead: {overhead:.2f} ms (IPC + json + process spawn)")
    print("")

    # Attach benchmark data to the contract result for consumers (journal ledger, meta-report)
    result["benchmark"] = {
        "pure_python_ms": round(pure_ms, 2),
        "subprocess_ms": round(wrapped_ms, 2),
        "overhead_ms": overhead,
        "note": "Demonstrates the measurable cost/benefit of crossing the Parallel_f native boundary."
    }

    # Pretty console output (KickLang flavored)
    print("⫻result/contract")
    print(f"  success: {result['success']}")
    print(f"  metrics.duration_ms: {result['metrics']['duration_ms']}")
    print(f"  metrics.parallel_degree: {result['metrics']['parallel_degree']}")
    print(f"  coherence_signals: flux={result['coherence_signals']['flux']} drift={result['coherence_signals']['drift']} valence={result['coherence_signals']['valence']}")
    print("")

    print("⫻data/aggregated:horizons/01")
    for h, p in result["result"]["aggregated_horizons"].items():
        print(f"  {h}: {p}")
    print(f"  average_risk: {result['result']['average_risk']}")
    print("")

    if result.get("next_tas_hints"):
        print("⫻tas/hints:from_parallel_f/01")
        for hint in result["next_tas_hints"]:
            print(f"  - {hint['id']} [{hint.get('horizon','H?')}] — {hint['desc'][:70]}...")
        print("")

    # Machine consumable sidecar (now includes benchmark + subprocess boundary proof)
    out_dir = os.path.dirname(__file__)
    sidecar_name = f"parallel_f_result_{context['cycle_id']}.json"
    sidecar_path = os.path.join(out_dir, sidecar_name)
    with open(sidecar_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("⫻data/provenance:sidecar/01")
    print(f"  written: {sidecar_path}")
    print(f"  size: {os.path.getsize(sidecar_path)} bytes")
    print("")

    print("⫻coherence:from_native/01")
    print(f"  The native worker (separate process) emitted coherence_signals directly usable by CoherenceMonitorBridge.")
    print(f"  Benchmark data included for TAS-PAR-003 style follow-up work.")
    print("")

    print("⫻end/demo")
    print("**Parallel_f contract demo (v0.2 boundary) complete.** Subprocess worker + benchmark now satisfies the spec's FFI example more faithfully.")
    print("Ready to be wired into real KickLang flows or called from the operational journal agent.")

    return result, sidecar_path


if __name__ == "__main__":
    run_demo()
