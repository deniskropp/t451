# GEMINI.md — Project Context & Operational Guidelines

This workspace represents the core runtime, state ledger, and demonstration substrate for the **Orion Collective State (OCS)** meta-infrastructure. It hosts the operational **Journal-as-Agent (JAA)** MVP and the high-performance **Parallel_f ↔ KickLang** native-agent wrapper integration.

---

## 1. Project & Directory Overview

This is a **hybrid agentic-code and metadata project** designed to realize a self-sustaining, self-referential agent loop. High-level agent planning, probabilistic forecasting, and coherence-monitoring are coupled with native, high-performance execution patterns.

### Core Paradigms & Meta-DNA
All code and documents in this repository are engineered to align with the core **Denis Kropp Meta-DNA**:
1. **Precision Engineering:** Strong architectural contracts, explicit interfaces, measurable metrics, and mathematical rigor (reminiscent of the DirectFB system architecture).
2. **Creative Co-Agency:** Dynamic collaboration between the human developer and self-governing AI agents, where agent-proposed deltas are recorded in accepted logs.
3. **Embodiment:** Fast native-style code execution (e.g., C++/native via Parallel_f) acting as the execution body that grounds high-level LLM-orchestrated intentions.
4. **Closed-Loop Self-Reference:** The system proposes updates to its own objective state, which are merged, scheduled, and re-executed dynamically.

---

## 2. Key Subsystems & Architecture

```
                       +----------------------------------+
                       |   Human Inputs & Living Memory   |
                       |       (~/.grok/memory.md)        |
                       +----------------+-----------------+
                                        |
                                        v
                       +----------------------------------+
                       |    journal_as_agent_mvp.py       | <---+
                       | (TAS Extraction & Forecasts)     |     |
                       +----------------+-----------------+     | Polling /
                                        |                       | Watcher
                                        v                       | Trigger
                       +----------------------------------+     |
                       |          journal_state/          |     |
                       | (Ledgers, Run Sidecars, MD Logs) | ----+
                       +----------------+-----------------+
                                        |
                                        v
                       +----------------------------------+
                       |     coherence_emitter.py         |
                       |  (Aggregates Coherence Signals)  |
                       +----------------+-----------------+
                                        |
                                        v
                       +----------------------------------+
                       |     CoherenceMonitorBridge       |
                       |  (Validates alignment & valence) |
                       +----------------------------------+
```

### A. Journal-as-Agent (JAA) Loop
The main daemon loop extracts **TAS (Task-Action-System)** blocks from memory, executes a multi-horizon probabilistic forecast (H0 to H3), proposes delta adjustments, and records full provenance.
- **Main Driver:** `journal_as_agent_mvp.py`
- **Scheduler & Watcher:** `journal_state/activate_scheduler.py`
- **State Storage:** `journal_state/current_tas.json` & `journal_state/current_tas.md`

### B. Parallel_f ↔ KickLang Wrapper Contract
Bridges the compiled, high-performance native-concurrency DAG framework (`Parallel_f`) with the expressive LLM orchestration layer (`KickLang`).
- **Specification:** `parallel_f_kicklang_wrapper_spec.md`
- **Demonstration Host (FFI/IPC Shim):** `demos/parallel_f_demo.py`
- **Native Process Stand-in:** `demos/parallel_f_worker.py`

### C. Coherence Emission & Monitoring
Monitors the drift, flux, and valence of agent executions, transforming runtime execution sidecars into structured coherence signals ready for `CoherenceMonitorBridge` ingestion.
- **Emission Engine:** `journal_state/coherence_emitter.py`
- **Output Artifacts:** `journal_state/coherence_emission_JAA-*.json` and `.md`

---

## 3. Directory Structure & Key Files

- `/` (Root Directory)
  - `journal_as_agent_mvp.py`: core agent script (v0.2.0-dev) executing the forecasting pipeline, ledger merge, and provenance computations.
  - `journal_delta_2026-06-14.md` / `journal_delta_2026-06-14_provenance.json`: reference human/machine output logs of a full delta run.
  - `parallel_f_kicklang_wrapper_spec.md`: standard specification for high-performance Parallel_f node integrations.
- `demos/` (Parallel_f Sandbox)
  - `parallel_f_demo.py`: execution shim simulating FFI/IPC, benchmark metrics, and coherence extraction.
  - `parallel_f_worker.py`: standalone worker subprocess called by the shim for "native" vectorized aggregation calculations.
  - `parallel_f_result_JAA-*.json`: sidecar output recording runtime metrics and worker outcomes.
- `journal_state/` (The Persistent Substrate & State Ledger)
  - `current_tas.json` / `current_tas.md`: the authoritative, serialized ledger of currently accepted and active tasks (TAS blocks).
  - `activate_scheduler.py`: process scheduler and polling directories file-watcher.
  - `coherence_emitter.py`: script parsing run logs + demo results to generate downstream-compatible coherence emissions.
  - `coherence_gate_JAA-*.md` / `delta_acceptance_2026-06-14.md`: quality validation and human-in-the-loop approval records.
  - `execution_closure_JAA-*.md`: finality validation reports for operational cycle completion.
  - `meta_report_card_JAA_operationalization_2026-06-14.md`: meta-evaluation summarizing the technical and creative success of cycles.
  - `SCHEDULER_HINTS.md`: reference setup instructions for setting up cron-jobs or watchers.
  - `ingest_example.py` / `INGEST_FOR_META_REPORT.md`: guidelines and helper tools for feeding results into meta report generators.
  - `journal_agent.log` / `journal_runs.log`: runtime execution logging files.

---

## 4. Building, Running & Scheduling Operations

### Execution Commands

#### 1. Execute Journal-as-Agent MVP (One-Shot)
Runs the TAS extraction and forecast cycle, producing new delta suggestions:
```bash
python3 journal_as_agent_mvp.py --once
```

To execute with custom state directory or explicit memory source paths:
```bash
python3 journal_as_agent_mvp.py --state-dir journal_state --memory ~/.grok/user_info/memory.md
```

#### 2. Run the Polling Scheduler / File Watcher
Launches a long-lived watcher polling the target memory file and extra directories (`demos/`, `journal_state/`), automatically triggering the JAA loop on save:
```bash
python3 journal_state/activate_scheduler.py --watch --interval 30
```

To run a simple fixed-interval loop (e.g., every 4 hours):
```bash
python3 journal_state/activate_scheduler.py --loop --interval 14400
```

#### 3. Run and Benchmark the Parallel_f Wrapper Demo
Executes the subprocess-boundary native worker and compares execution metrics against an in-process pure Python baseline:
```bash
python3 demos/parallel_f_demo.py
```

#### 4. Run the Coherence Emission Pipeline
Parses the latest JAA execution logs and Parallel_f sidecars, aggregating signals into a formatted report and JSON emission payload:
```bash
python3 journal_state/coherence_emitter.py
```

---

## 5. Development & Contribution Conventions

### A. Code Quality & Integration Standards
- **Strong Contracts First:** All FFI or IPC boundaries (e.g., Python calling Parallel_f binaries) must strictly respect the identity/execution/coherence interface spec in `parallel_f_kicklang_wrapper_spec.md`.
- **Halt on Coherence Violations:** If execution safety parameters or coherence valence thresholds are violated, the worker must return an explicit list of `halt_reasons` and exit cleanly with success=false.
- **Type Safety & CLI Ergonomics:** Prefer explicit parameter configurations using `argparse`, structured typing, and descriptive logging. Never swallow errors.
- **Idempotency:** Re-running the agent or the scheduler on the same memory/state substrate must be idempotent and merge newly accepted blocks without duplicating legacy ledgers.

### B. KickLang Markup Standard
For Markdown-based communications, ledger tables, and reports, the project uses custom **KickLang tag envelopes** to encode structured machine-readable blocks.

Key tags include:
- `⫻kicklang:header` / `⫻kicklang:meta-report` — structural headers defining the document type.
- `⫻data/provenance:journal_delta/01` — cryptographic tracking block (hash of memory, agent version, cycle identifier).
- `⫻tas/current_state:extracted/01` — lists extracted active TAS blocks.
- `⫻tas/ledger:current/01` — the accepted ledger of active, validated tasks.
- `⫻tas/block:new_tas/TAS-XXX` — concrete block describing a new task proposal.
- `⫻forecast/cycle:summary/01` — multi-horizon summary results.
- `⫻coherence/report:current/01` — flux, drift potential, and valence score rollups.
- `⫻cmd/recommendation:immediate/01` — execution guidance and immediate action points.
- `⫻end/report` / `⫻end/spec` — envelope closures indicating clean parsing termination points.

Whenever modifying or creating reports under `journal_state/`, guarantee that all KickLang wrappers remain pristine, balanced, and machine-parsable.
