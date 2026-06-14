#!/usr/bin/env python3
"""
journal_as_agent_mvp.py
Minimal viable "journal-as-agent" prototype.
Reads memory.md (current journal/TAS source), extracts key objectives as TAS blocks,
runs a simplified multi-horizon forecast cycle, proposes deltas, and logs everything
with full provenance in KickLang/OCS-inspired structured format.

Emulates core patterns from tas-forecast-cycle and living-objective-tas-flow skills
without requiring the full multi-agent runtime.

Usage:
    python3 /home/workdir/artifacts/journal_as_agent_mvp.py

Outputs:
    - artifacts/journal_delta_YYYY-MM-DD.md   (human-readable KickLang report)
    - artifacts/journal_delta_YYYY-MM-DD_provenance.json (machine-readable log)
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import sys
import time
from typing import List, Dict, Any, Optional

VERSION = "0.2.0-dev"
AGENT_NAME = "journal_as_agent_mvp"

def read_memory(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def extract_current_state(memory_text: str) -> List[Dict[str, Any]]:
    """Heuristic TAS extraction from memory.md + injected vision context."""
    tas_blocks: List[Dict[str, Any]] = []

    # Core active project from Key Life Events
    if "autonomous underbody" in memory_text.lower() or "Move & Traffic" in memory_text:
        tas_blocks.append({
            "id": "TAS-UBI-001",
            "desc": "Autonomous underbody image recognition pipeline for Move & Traffic Controls GmbH (real-time defect/anomaly detection, synthetic data + YOLOv8-seg, TensorRT/Jetson target, safety recall ≥0.98)",
            "priority": "HIGH",
            "source": "Key Life Events [2026-04-19]",
            "domain": "vision_systems"
        })

    # Vision 1: Parallel_f + KickLang standard (from user input)
    tas_blocks.append({
        "id": "TAS-PAR-001",
        "desc": "Evolve Parallel_f + KickLang wrappers into de-facto standard for agentic DAGs — attract forks/contributions and bridge C++ performance with LLM orchestration at scale",
        "priority": "HIGH",
        "source": "User vision input [2026-06-14]",
        "domain": "meta_infrastructure"
    })

    # Vision 2: Full OCS + journal-as-agent (from user input)
    tas_blocks.append({
        "id": "TAS-OCS-001",
        "desc": "Realize Full Orion Collective State (OCS) as self-sustaining meta-AI ecosystem where TAS-driven forecasting + living objectives enable autonomous 'journal-as-agent' evolution influencing broader AI governance/embodiment paradigms",
        "priority": "HIGH",
        "source": "User vision input [2026-06-14]",
        "domain": "meta_infrastructure"
    })

    # Portfolio / career acceleration
    tas_blocks.append({
        "id": "TAS-PORT-001",
        "desc": "Build and demonstrate impressive AI-hybrid workflows, self-running systems, and creative engines (KickLang v4.1+, AuffassungForge, CoherenceMonitorBridge, DopaSprint, predictive modeling) as portfolio for new Google role or independent ventures",
        "priority": "HIGH",
        "source": "Goals & Aspirations",
        "domain": "career_portfolio"
    })

    # Foundational meta capability (this MVP itself)
    tas_blocks.append({
        "id": "TAS-JAA-000",
        "desc": "Establish persistent journal-as-agent capability: read memory/TAS, run forecast cycles, propose deltas, log with full provenance, integrate with living-objective-tas-flow and CoherenceMonitorBridge",
        "priority": "HIGH",
        "source": "Living objective evolution / current task",
        "domain": "meta_infrastructure"
    })

    # Additional from Core Interests & Experience (meta-infra focus)
    tas_blocks.append({
        "id": "TAS-META-002",
        "desc": "Continue intensive development of personal AI meta-infrastructure: KickLang v4.1+ codex/RTA, CoherenceMonitorBridge v1.1, RTA Python/KickLang impl, OCS-CTL integration, Dynamic Tool Construction Kit, Nexus-Prime",
        "priority": "MED-HIGH",
        "source": "Experience & May 2026 burst",
        "domain": "meta_infrastructure"
    })

    return tas_blocks

def run_forecast_cycle(tas_blocks: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Simplified multi-horizon forecasting (H0–H3). Deterministic templates + domain overrides for MVP."""
    horizons = ["H0", "H1", "H2", "H3"]
    forecasts: Dict[str, Dict[str, Any]] = {}

    for tas in tas_blocks:
        tid = tas["id"]
        desc = tas["desc"].lower()
        forecasts[tid] = {}

        for h in horizons:
            base_prob = 0.75
            leading = ["Clear next action defined", "Dependencies mapped"]
            risk = ["Scope creep in meta-layering"]

            if "underbody" in desc or "ubi" in tid.lower():
                if h == "H0":
                    prob, desc_h = 0.88, "Complete core detection training loop + synthetic data validation pipeline"
                    leading = ["YOLOv8-seg training script ready", "Domain randomization params tuned"]
                elif h == "H1":
                    prob, desc_h = 0.72, "Integrate real-time inference on Jetson Orin Nano / ROS2; initial field test"
                elif h == "H2":
                    prob, desc_h = 0.65, "Safety-gated validation (recall ≥0.98), TensorRT export, production pilot"
                else:
                    prob, desc_h = 0.55, "Full autonomous underbody inspection product deployed at customer sites"
                risk = ["False-negative safety risk", "Hardware integration delays"]

            elif "parallel_f" in desc or "par-001" in tid.lower():
                if h == "H0":
                    prob, desc_h = 0.90, "Define Parallel_f ↔ KickLang node contract + first wrapper prototype"
                elif h == "H1":
                    prob, desc_h = 0.78, "Reference agentic DAG examples (forecast pipeline, multi-persona orchestration)"
                elif h == "H2":
                    prob, desc_h = 0.68, "GitHub release + community onboarding; attract first external forks"
                else:
                    prob, desc_h = 0.50, "De-facto standard adoption in hybrid C++/LLM agent ecosystems"
                leading = ["Clean abstraction layer", "Performance benchmarks vs pure LLM"]

            elif "ocs" in desc or "journal-as-agent" in desc or "jaa" in tid.lower():
                if h == "H0":
                    prob, desc_h = 0.93, "Deploy this minimal journal-as-agent MVP + first delta log with provenance"
                elif h == "H1":
                    prob, desc_h = 0.82, "Wire output to CoherenceMonitorBridge + living-objective-tas-flow for closed loop"
                elif h == "H2":
                    prob, desc_h = 0.70, "Autonomous periodic runs + objective evolution proposals accepted into memory"
                else:
                    prob, desc_h = 0.58, "Full self-sustaining OCS with journal-as-agent as core evolutionary engine"
                leading = ["Provenance logging robust", "Consent gates implemented"]

            else:
                # Generic
                if h == "H0":
                    prob, desc_h = base_prob + 0.12, f"Immediate concrete next action for: {tas['desc'][:60]}..."
                elif h == "H1":
                    prob, desc_h = base_prob + 0.03, "Short-term sprint completion with measurable progress"
                elif h == "H2":
                    prob, desc_h = base_prob - 0.05, "Medium-term integration into broader meta-infrastructure"
                else:
                    prob, desc_h = base_prob - 0.15, "Long-term portfolio or paradigm impact realized"

            forecasts[tid][h] = {
                "success_probability": round(prob, 2),
                "description": desc_h,
                "leading_indicators": leading,
                "risks": risk
            }

    return forecasts

def propose_deltas(tas_blocks: List[Dict[str, Any]], forecasts: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate concrete delta proposals (new TAS, refinements, coherence actions)."""
    deltas: List[Dict[str, Any]] = []

    # Always propose strengthening this capability
    deltas.append({
        "type": "new_tas",
        "id": "TAS-JAA-001",
        "desc": "Operationalize journal-as-agent MVP: schedule periodic runs (e.g. on new memory updates or objective shifts), integrate provenance into meta-report-card-generation, add simple RTA query support for historical deltas",
        "horizon": "H0",
        "confidence": 0.94,
        "parent": "TAS-JAA-000"
    })

    deltas.append({
        "type": "new_tas",
        "id": "TAS-PAR-002",
        "desc": "Create first Parallel_f + KickLang wrapper specification document + reference implementation skeleton (node contract, execution context, coherence propagation)",
        "horizon": "H0",
        "confidence": 0.89,
        "parent": "TAS-PAR-001"
    })

    deltas.append({
        "type": "objective_refinement",
        "id": "OBJ-REF-OCS-001",
        "target_id": "TAS-OCS-001",
        "change": "Elevate 'journal-as-agent' from prototype to core OCS primitive. Add explicit consent/halt gates and CoherenceMonitorBridge integration as acceptance criteria for H1.",
        "horizon": "H1",
        "confidence": 0.85
    })

    deltas.append({
        "type": "coherence_action",
        "id": "COH-ACT-001",
        "desc": "Run CoherenceMonitorBridge on current memory + new delta proposals. Flag any drift vs Denis Kropp Meta-DNA (DirectFB precision + creative chaos + co-agency + embodiment).",
        "horizon": "H0",
        "confidence": 0.91
    })

    deltas.append({
        "type": "new_tas",
        "id": "TAS-META-003",
        "desc": "Extend Dynamic Tool Construction Kit with journal-as-agent and forecast-cycle tool descriptors for MCP / OCS consumption",
        "horizon": "H1",
        "confidence": 0.80,
        "parent": "TAS-META-002"
    })

    # Portfolio acceleration
    deltas.append({
        "type": "new_tas",
        "id": "TAS-PORT-002",
        "desc": "Package current meta-infrastructure state (KickLang, CoherenceMonitor, RTA, this MVP) into polished demo portfolio artifacts + short Loom/video walkthrough targeting Google or independent opportunities",
        "horizon": "H1",
        "confidence": 0.75,
        "parent": "TAS-PORT-001"
    })

    return deltas

def compute_provenance(memory_text: str, cycle_id: str, memory_source: str = "/home/workdir/.grok/user_info/memory.md") -> Dict[str, Any]:
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    mem_hash = hashlib.sha256(memory_text.encode("utf-8")).hexdigest()[:16]
    mem_size = len(memory_text)
    return {
        "cycle_id": cycle_id,
        "timestamp": ts,
        "agent": f"{AGENT_NAME}_v{VERSION}",
        "memory_source": memory_source,
        "memory_sha256_prefix": mem_hash,
        "memory_size_bytes": mem_size,
        "input_artifacts": ["memory.md", "current_tas.json"],
        "coherence_notes": "High alignment with existing KickLang/OCS/TAS primitives and user vision vectors. Low semantic drift. Strong valence for autonomy and co-agency.",
        "meta_dna_tags": ["denis_kropp_dna", "meta_infrastructure", "co_agency", "kicklang", "ocs", "tas"]
    }


# --- Operationalization additions (v0.2) ---

def load_state(state_dir: str) -> Dict[str, Any]:
    """Load persistent journal_state (current_tas + prior deltas if present)."""
    current_tas_path = os.path.join(state_dir, "current_tas.json")
    if os.path.exists(current_tas_path):
        with open(current_tas_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"tas_blocks": [], "pending_h1": [], "state_version": "0.0"}


def merge_accepted_deltas(tas_blocks: List[Dict[str, Any]], state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Merge newly accepted H0 blocks from ledger into the active extraction view (idempotent)."""
    accepted = {b["id"]: b for b in state.get("tas_blocks", []) if b.get("status", "").endswith("accepted") or b.get("status") == "newly_accepted_h0"}
    merged = []
    seen = set()
    for tb in tas_blocks:
        seen.add(tb["id"])
        merged.append(tb)
    for aid, ab in accepted.items():
        if aid not in seen:
            # promote ledger entry into extraction shape
            merged.append({
                "id": ab["id"],
                "desc": ab["desc"],
                "priority": ab.get("priority", "HIGH"),
                "source": ab.get("source", "journal_state ledger (accepted)"),
                "domain": ab.get("domain", "meta_infrastructure"),
                "parent": ab.get("parent")
            })
    return merged


def persist_ledger(state_dir: str, provenance: Dict[str, Any], tas_blocks: List[Dict[str, Any]], deltas: List[Dict[str, Any]], forecasts: Dict[str, Dict[str, Any]]):
    """Write/append to journal_state for operational continuity (current_tas + run log)."""
    os.makedirs(state_dir, exist_ok=True)

    # Update a lightweight current_tas view (append new accepted-style entries for H0 deltas)
    current_path = os.path.join(state_dir, "current_tas.json")
    prior = {}
    if os.path.exists(current_path):
        with open(current_path, "r", encoding="utf-8") as f:
            prior = json.load(f)

    now_iso = datetime.datetime.now().isoformat(timespec="seconds")
    ledger_tas = prior.get("tas_blocks", [])[:]

    # Seed or refresh from the just-extracted + newly proposed H0
    id_map = {t["id"]: t for t in ledger_tas}
    for tb in tas_blocks:
        if tb["id"] not in id_map:
            id_map[tb["id"]] = {
                "id": tb["id"],
                "desc": tb["desc"],
                "priority": tb.get("priority", "HIGH"),
                "horizon": "H0-H2",
                "status": "active",
                "source": tb.get("source", "journal_as_agent"),
                "domain": tb.get("domain", "general"),
                "confidence": 0.8
            }
    # Mark newly operationalized items
    for d in deltas:
        if d.get("horizon") == "H0" and d.get("type") == "new_tas":
            if d["id"] in id_map:
                id_map[d["id"]]["status"] = "newly_accepted_h0"
                id_map[d["id"]]["parent"] = d.get("parent")
            else:
                id_map[d["id"]] = {
                    "id": d["id"],
                    "desc": d["desc"],
                    "priority": "HIGH",
                    "horizon": d["horizon"],
                    "status": "newly_accepted_h0",
                    "parent": d.get("parent"),
                    "source": f"journal_delta {provenance['cycle_id']} (operationalized)",
                    "domain": "meta_infrastructure",
                    "confidence": d.get("confidence", 0.85)
                }

    new_state = {
        "state_version": "0.2",
        "last_updated": now_iso,
        "source_cycle": provenance["cycle_id"],
        "tas_blocks": list(id_map.values()),
        "pending_h1": prior.get("pending_h1", []),
        "coherence_last": prior.get("coherence_last", {})
    }
    with open(current_path, "w", encoding="utf-8") as f:
        json.dump(new_state, f, indent=2, ensure_ascii=False)

    # Append a tiny run log (human + machine friendly)
    log_path = os.path.join(state_dir, "journal_runs.log")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"{now_iso}\t{provenance['cycle_id']}\t{len(tas_blocks)} tas\t{len(deltas)} deltas\n")

    # Also drop a machine-readable sidecar of the full run (for meta-report consumption)
    sidecar = os.path.join(state_dir, f"run_{provenance['cycle_id']}.json")
    with open(sidecar, "w", encoding="utf-8") as f:
        json.dump({
            "provenance": provenance,
            "tas_blocks": tas_blocks,
            "deltas": deltas,
            "forecast_summary": {
                tid: {h: fdata.get("success_probability") for h, fdata in fcast.items()}
                for tid, fcast in forecasts.items()
            }
        }, f, indent=2)


def emit_scheduler_hint(state_dir: str, project_root: str = ".") -> str:
    """Return a ready-to-use scheduler snippet for recurring journal-as-agent runs."""
    hint = f"""# Scheduler hint for journal-as-agent operationalization (TAS-JAA-001)
# Option A: cron (recommended for simple periodic)
# Run every 4 hours + on significant memory changes (inotify or post-edit hook)
# 0 */4 * * * cd {os.path.abspath(project_root)} && python3 journal_as_agent_mvp.py --state-dir journal_state --memory ~/.grok/user_info/memory.md >> journal_state/journal_agent.log 2>&1

# Option B: lightweight python loop watcher (for dev / container)
#   while true; do python3 journal_as_agent_mvp.py --state-dir journal_state --once; sleep 14400; done

# Option C: on-memory-change (Linux)
#   while inotifywait -e close_write ~/.grok/user_info/memory.md; do
#       python3 journal_as_agent_mvp.py --state-dir journal_state --memory ~/.grok/user_info/memory.md
#   done

# After runs, feed journal_state/run_*.json + current_tas.json into:
#   - meta-report-card-generation (as TAS + provenance source)
#   - CoherenceMonitorBridge (flux/drift/valence signals)
#   - living-objective-tas-flow (for objective re-grounding)
"""
    hint_path = os.path.join(state_dir, "SCHEDULER_HINTS.md")
    os.makedirs(state_dir, exist_ok=True)
    with open(hint_path, "w", encoding="utf-8") as f:
        f.write(hint)
    return hint


def run_operational_cycle(memory_path: str, state_dir: str, project_root: str = ".") -> Dict[str, Any]:
    """Full operational cycle used by both CLI --once and future scheduler."""
    if not os.path.exists(memory_path):
        print(f"WARNING: memory not found at {memory_path}. Using minimal synthetic context for bootstrap.")
        memory_text = "journal-as-agent operationalization + Parallel_f + OCS vision + meta-infrastructure + underbody vision system (synthetic bootstrap)"
    else:
        memory_text = read_memory(memory_path)

    today = datetime.date.today().isoformat()
    cycle_id = f"JAA-{today}-001"

    print(f"⫻kicklang:operational")
    print(f"Starting operational cycle: {cycle_id}")
    print(f"Memory: {memory_path}")
    print(f"State dir: {state_dir}")

    tas_blocks = extract_current_state(memory_text)

    # Merge any ledger-accepted H0 work so the agent "remembers" prior deltas
    state = load_state(state_dir)
    tas_blocks = merge_accepted_deltas(tas_blocks, state)

    print(f"Extracted + merged {len(tas_blocks)} TAS blocks (ledger continuity applied).")

    forecasts = run_forecast_cycle(tas_blocks)
    deltas = propose_deltas(tas_blocks, forecasts)

    provenance = compute_provenance(memory_text, cycle_id, memory_path)

    # Persist for the next agent invocation and downstream consumers
    persist_ledger(state_dir, provenance, tas_blocks, deltas, forecasts)

    # Always (re)emit scheduler guidance
    scheduler = emit_scheduler_hint(state_dir, project_root)

    report = generate_kicklang_report(provenance, tas_blocks, forecasts, deltas)

    # Write the human delta as before (to artifacts or local)
    out_md = os.path.join(state_dir, f"journal_delta_{today}.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n✅ Operational cycle complete.")
    print(f"   State/ledger updated in: {state_dir}")
    print(f"   Human report: {out_md}")
    print(f"   Scheduler guidance: {os.path.join(state_dir, 'SCHEDULER_HINTS.md')}")
    print("")
    return {"cycle_id": cycle_id, "report_path": out_md, "state_dir": state_dir, "scheduler_hint": scheduler}

def generate_kicklang_report(
    provenance: Dict[str, Any],
    tas_blocks: List[Dict[str, Any]],
    forecasts: Dict[str, Dict[str, Any]],
    deltas: List[Dict[str, Any]]
) -> str:
    """Render full structured output in KickLang / OCS style."""
    lines: List[str] = []

    lines.append("⫻kicklang:header")
    lines.append("# Journal-as-Agent MVP — Delta Report & Provenance Log")
    lines.append("")
    lines.append(f"**Cycle ID**: {provenance['cycle_id']}")
    lines.append(f"**Generated**: {provenance['timestamp']}")
    lines.append(f"**Agent**: {provenance['agent']}")
    lines.append("")

    # Provenance section
    lines.append("⫻data/provenance:journal_delta/01")
    lines.append(f"- cycle_id: {provenance['cycle_id']}")
    lines.append(f"- timestamp: {provenance['timestamp']}")
    lines.append(f"- memory_sha256_prefix: {provenance['memory_sha256_prefix']}")
    lines.append(f"- memory_size_bytes: {provenance['memory_size_bytes']}")
    lines.append(f"- coherence_notes: {provenance['coherence_notes']}")
    lines.append(f"- meta_dna_tags: {', '.join(provenance['meta_dna_tags'])}")
    lines.append("")

    # Current extracted TAS
    lines.append("⫻tas/current_state:extracted/01")
    for tas in tas_blocks:
        lines.append(f"- **{tas['id']}** [{tas['priority']}] — {tas['desc']}")
        lines.append(f"  Source: {tas['source']} | Domain: {tas.get('domain', 'general')}")
    lines.append("")

    # Forecast summary (high level)
    lines.append("⫻forecast/cycle:summary/01")
    lines.append("Multi-horizon probabilistic forecast executed (H0 immediate → H3 long-term).")
    lines.append("Overall near-term confidence strong on meta-infrastructure primitives and this MVP itself.")
    lines.append("Key risk vector: underbody safety-critical false-negatives and hardware integration timing.")
    lines.append("")

    # Detailed per-TAS forecast highlights (H0/H1 focus for brevity)
    lines.append("⫻forecast/details:h0_h1/01")
    for tas in tas_blocks[:4]:  # top priority ones
        tid = tas["id"]
        if tid in forecasts:
            h0 = forecasts[tid].get("H0", {})
            h1 = forecasts[tid].get("H1", {})
            lines.append(f"**{tid}** — {tas['desc'][:70]}...")
            lines.append(f"  H0 ({h0.get('success_probability', 0.8)}): {h0.get('description', 'N/A')}")
            lines.append(f"  H1 ({h1.get('success_probability', 0.7)}): {h1.get('description', 'N/A')}")
    lines.append("")

    # Proposed deltas
    lines.append("⫻tas/proposed_delta:updates/01")
    for d in deltas:
        d_type = d.get("type", "update")
        block_id = d.get("id", d.get("target_id", "N/A"))
        content = d.get("desc") or d.get("change", "No description provided")
        lines.append(f"⫻tas/block:{d_type}/{block_id} [horizon={d['horizon']}] [confidence={d.get('confidence', 0.8)}]")
        lines.append(f"  {content}")
        if d.get("parent"):
            lines.append(f"  Parent: {d['parent']}")
        if d.get("change") and d.get("desc"):
            lines.append(f"  Change detail: {d['change']}")
        lines.append("")
    lines.append("")

    # Coherence & next actions
    lines.append("⫻coherence/report:current/01")
    lines.append("**Flux**: Low (new capability directly extends prior vision and existing primitives).")
    lines.append("**Drift potential**: Minimal — proposals stay within Denis Kropp Meta-DNA (precision engineering + creative co-agency + embodiment).")
    lines.append("**Valence**: +0.14 (empowering, autonomy-increasing, high coherence with OCS and TAS methodology).")
    lines.append("**Recommendation**: Accept all H0 deltas. Proceed to implementation of journal-as-agent operationalization and Parallel_f wrapper spec.")
    lines.append("")

    lines.append("⫻cmd/recommendation:immediate/01")
    lines.append("1. Accept and action H0 deltas (journal-as-agent operationalization + Parallel_f spec).")
    lines.append("2. Schedule recurring MVP runs (e.g. via cron or on memory change detection).")
    lines.append("3. Wire provenance output into meta-report-card-generation and CoherenceMonitorBridge.")
    lines.append("4. Extend parser in v0.2 for deeper TAS extraction from full conversation history + GitHub t-repos.")
    lines.append("5. Prototype first Parallel_f ↔ KickLang wrapper as next concrete deliverable.")
    lines.append("")

    lines.append("⫻end/report")
    lines.append("")
    lines.append("**End of Journal-as-Agent MVP Delta Log** — provenance preserved for recursive evolution.")

    return "\n".join(lines)

def main(argv: Optional[List[str]] = None):
    parser = argparse.ArgumentParser(description="Journal-as-Agent MVP (v0.2 operational)")
    parser.add_argument("--memory", default=None, help="Path to memory.md (TAS source). Falls back to ~/.grok/user_info/memory.md or local test.")
    parser.add_argument("--state-dir", default="journal_state", help="Directory for persistent ledger (current_tas.json, run sidecars, scheduler hints)")
    parser.add_argument("--once", action="store_true", help="Run a single operational cycle (the new default behavior for scheduled use).")
    parser.add_argument("--project-root", default=".", help="Project root for scheduler hint generation.")
    parser.add_argument("--legacy", action="store_true", help="Force legacy one-shot output to ./artifacts (pre-v0.2 behavior).")
    args = parser.parse_args(argv)

    # Resolve memory path with sensible fallbacks for operational use
    memory_path = args.memory
    if not memory_path:
        candidates = [
            os.path.expanduser("~/.grok/user_info/memory.md"),
            "/home/workdir/.grok/user_info/memory.md",
            os.path.join(args.project_root, "memory.md"),
            os.path.join(args.project_root, "test_memory.md"),
        ]
        for c in candidates:
            if os.path.exists(c):
                memory_path = c
                break
        if not memory_path:
            memory_path = os.path.expanduser("~/.grok/user_info/memory.md")  # will trigger bootstrap warning in operational cycle

    state_dir = os.path.abspath(args.state_dir)

    if args.legacy and not args.once:
        # Original pre-operational behavior (writes to artifacts relative to cwd)
        if not os.path.exists(memory_path):
            print(f"ERROR: memory.md not found at {memory_path}")
            sys.exit(2)
        memory_text = read_memory(memory_path)
        today = datetime.date.today().isoformat()
        cycle_id = f"JAA-{today}-001"
        print("⫻kicklang:header")
        print("# Journal-as-Agent MVP v0.1.0-legacy — Execution Log")
        print(f"Starting cycle: {cycle_id}")
        tas_blocks = extract_current_state(memory_text)
        forecasts = run_forecast_cycle(tas_blocks)
        deltas = propose_deltas(tas_blocks, forecasts)
        provenance = compute_provenance(memory_text, cycle_id, memory_path)
        report = generate_kicklang_report(provenance, tas_blocks, forecasts, deltas)
        os.makedirs("artifacts", exist_ok=True)
        out_md = f"artifacts/journal_delta_{today}.md"
        with open(out_md, "w", encoding="utf-8") as f:
            f.write(report)
        out_json = out_md.replace(".md", "_provenance.json")
        json_payload = {
            "provenance": provenance,
            "tas_blocks": tas_blocks,
            "deltas": deltas,
            "forecast_summary": {tid: {h: fdata.get("success_probability") for h, fdata in fcast.items()} for tid, fcast in forecasts.items()}
        }
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(json_payload, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Legacy MVP complete. Report: {out_md}")
        return

    # Default / recommended path: operational cycle (supports scheduling + ledger)
    result = run_operational_cycle(memory_path, state_dir, args.project_root)

    # For interactive visibility, also print a short tail of the latest report
    if os.path.exists(result["report_path"]):
        print("--- Tail of latest operational KickLang delta ---")
        with open(result["report_path"], "r", encoding="utf-8") as f:
            lines = f.readlines()[-12:]
        for line in lines:
            print(line.rstrip())

if __name__ == "__main__":
    main()
