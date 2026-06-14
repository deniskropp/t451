⭾kicklang:header
# Parallel_f Native C++ Bridge Design Exploration v0.1

**Parent TAS**: TAS-PAR-001 / TAS-PAR-002 (H1 realization path)  
**Related**: parallel_f_kicklang_wrapper_spec.md (Python shim side)  
**Cycle**: JAA-2026-06-14 post-merge with t451  
**Goal**: Define concrete native C++ side of the bridge so high-performance Parallel_f DAG nodes can be first-class participants in KickLang-orchestrated agentic flows while preserving full coherence, provenance, halt discipline, and OCS payload contracts.

⭾data/motivation/01
- KickLang + OCS = living cognitive orchestration layer (TAS extraction, multi-horizon forecasting, journal-as-agent autonomy, CoherenceMonitorBridge, consent/halt gates).
- Parallel_f (user-defined high-performance C++/native DAG runtime) = execution body providing true parallelism, low-latency, memory efficiency, and CPU/GPU affinity.
- The bridge must allow **native hot paths** (vision post-processing, RTA graph traversals, heavy simulation, forecast inner loops) without forcing everything through Python.
- Heritage leverage: 25+ years DirectFB low-level C++ mastery (framebuffers, embedded systems, performance-critical graphics) directly applicable to memory pools, zero-copy patterns, explicit parallelism, and robust error/halt contracts.
- Long-term: de-facto standard for hybrid C++ + LLM agentic systems (portfolio vision).

⭾data/architecture:options/01
**Option A — Pure pybind11 / pybind11 + nanobind (recommended for tight integration)**
- Pros: Zero-copy where possible, natural C++ classes exposed to Python, excellent performance, modern C++.
- Cons: Requires building extension module; GIL considerations for long-running native work (release GIL during compute).
- Best for: Embedded hybrid pattern.

**Option B — Subprocess + JSON-over-stdio (already sketched in spec shim)**
- Pros: Strong isolation, language agnostic worker, easy debugging, crash containment.
- Cons: Serialization overhead, process spawn cost (mitigate with long-lived worker pool or Unix sockets).
- Good fallback or for untrusted nodes.

**Option C — gRPC / Cap'n Proto / FlatBuffers over Unix socket or TCP**
- Pros: Excellent schema evolution, cross-language, streaming possible, mature tooling.
- Cons: More boilerplate, dependency surface.
- Suitable for distributed or multi-process Parallel_f clusters.

**Recommended Hybrid**:
1. Core Parallel_f library built as shared object (.so) with pybind11 bindings for the "embedded hybrid" case.
2. Optional standalone `parallel_f_worker` binary (same library + CLI) for the "fire-and-observe" / isolation case.
3. Thin Python shim (already in spec) dispatches to either the bound module or the subprocess worker based on node policy.

⭾data/cpp:core_abstractions/01
```cpp
// parallel_f_node.hpp
#pragma once
#include <string>
#include <vector>
#include <optional>
#include <nlohmann/json.hpp>   // or rapidjson / protobuf

namespace parallel_f {

using json = nlohmann::json;

struct Context {
    std::string cycle_id;
    std::vector<std::string> tas_ids;
    std::vector<std::string> meta_dna_tags;
    bool consent{true};
    double coherence_threshold{0.05};
    std::optional<int> timeout_ms;
    // provenance sidecar reference
    std::optional<std::string> previous_delta_hash;
};

struct CoherenceSignals {
    std::string flux{"low"};      // low | medium | high
    double drift{0.0};
    double valence{0.0};          // -1.0 ... +1.0
    std::string notes;
};

struct Result {
    bool success{true};
    json result_payload;                    // domain-specific output
    json metrics;                           // duration_ms, cpu, parallel_degree, memory_peak, etc.
    CoherenceSignals coherence_signals;
    std::vector<std::string> next_tas_hints;
    std::vector<std::string> halt_reasons;
};

class ParallelFNode {
public:
    virtual ~ParallelFNode() = default;

    virtual std::string node_id() const = 0;
    virtual std::string version() const = 0;
    virtual std::string kind() const { return "parallel_f"; }

    // Core contract — must be implemented by every native node
    virtual Result execute(const json& payload, const Context& context) = 0;

    // Optional: batch / streaming variants for high-throughput paths
    virtual std::vector<Result> execute_batch(const std::vector<json>& payloads,
                                              const Context& context);
};

} // namespace parallel_f
```

Every concrete node (e.g. `UnderbodyYoloSegTrainerNode`, `RTAGraphTraversalNode`) inherits and implements `execute()`.

Inside `execute()` the implementation **must**:
- Respect `context.consent` and `context.coherence_threshold`.
- Populate `coherence_signals` on every return path (success or halt).
- Never swallow errors — populate `halt_reasons` and set `success = false`.
- Emit measurable metrics (use `std::chrono`, `getrusage`, or platform equivalents).
- Optionally suggest follow-on TAS via `next_tas_hints`.

⭾data/performance:patterns/01
Leverage DirectFB-era expertise:
- Memory pools / arena allocators instead of repeated `new`/`malloc` in hot loops.
- Explicit thread pools or task systems (std::jthread + work stealing, or integrate existing Parallel_f scheduler).
- Zero-copy where payload allows (std::span, views, or move semantics).
- NUMA / CPU affinity pinning for vision or simulation nodes.
- SIMD / vectorization hints (or offload to GPU via CUDA / Vulkan compute if relevant).
- Profiling hooks (easy integration with perf, VTune, or custom counters emitted in metrics).

⭾data/coherence:cpp_emission/01
CoherenceSignals must be produced natively and passed back through the shim to CoherenceMonitorBridge.

Example inside a node:
```cpp
CoherenceSignals sig;
sig.flux = (duration > threshold) ? "medium" : "low";
sig.drift = calculate_drift_from_previous(...);
sig.valence = success ? 0.25 : -0.4;
sig.notes = "node completed; " + std::to_string(parallel_degree) + " workers used";
result.coherence_signals = sig;
```

The Python shim simply forwards these signals; the journal-as-agent and CoherenceMonitorBridge consume them for living-objective updates and drift detection.

⭾data/halt:safety/01
Native side is the last line of defense:
- Timeouts → populate halt_reasons + return early.
- Resource exhaustion (memory, file descriptors) → halt.
- Semantic violations (e.g. recall_target not met in vision node) → halt with clear reason.
- Any exception in C++ must be caught at the boundary and turned into a structured halt result (never let it propagate to Python crash).

⭾data/example:node/01
Concrete example skeleton for a hot path (e.g. RTA traversal or vision aggregation):

```cpp
class RTATraversalNode : public ParallelFNode {
public:
    std::string node_id() const override { return "rta-graph-traversal-v1"; }
    std::string version() const override { return "0.1.0"; }

    Result execute(const json& payload, const Context& context) override {
        auto start = std::chrono::steady_clock::now();

        // ... actual high-performance RTA traversal using payload graph data ...
        // Use memory pools, parallel workers, etc.

        auto end = std::chrono::steady_clock::now();
        auto duration_ms = std::chrono::duration<double, std::milli>(end - start).count();

        Result r;
        r.success = true;
        r.result_payload = {{"traversed_nodes", 12345}, {"max_depth", 42}};
        r.metrics = {
            {"duration_ms", duration_ms},
            {"parallel_degree", 8},
            {"memory_peak_mb", 256}
        };
        r.coherence_signals = {
            .flux = "low",
            .drift = 0.01,
            .valence = 0.3,
            .notes = "RTA traversal completed within contract"
        };
        r.next_tas_hints = {"TAS-RTA-002", "TAS-JAA-delta-review"};
        return r;
    }
};
```

Registration can be via a factory or plugin system so new native nodes can be discovered without recompiling the shim.

⭾data/roadmap:cpp_implementation/01
H1 (current):
- Finalize this design doc.
- Implement one reference native node (e.g. simple vectorized aggregator or stub RTA) + pybind11 bindings.
- Extend the Python shim to support both pybind and subprocess modes.
- Benchmark vs pure-Python baseline on a realistic TAS (forecast cycle or underbody post-processing).

H2:
- Full Parallel_f core library with multiple production nodes.
- Integration with existing user C++ codebase (DirectFB-era patterns, Verilog FIFO lessons, Repast4Py insights where applicable).
- Packaging (CMake, Conan/vcpkg) and first GitHub release of the bridge.

H3:
- Community examples + adoption as bridge pattern for other hybrid agent systems.

⭾coherence:design/01
This native C++ bridge design directly advances the merged t451 vision while remaining inside Denis Kropp Meta-DNA:
- **Precision Engineering**: Explicit contracts, measurable metrics, strong halt discipline, provenance flow.
- **Creative Co-Agency**: Native execution as the "body" that grounds high-level KickLang/LLM intention; journal-as-agent receives next_tas_hints from native results.
- **Embodiment**: Real C++ performance and parallelism instead of simulated Python.
- **Self-Reference**: Coherence signals and next hints feed directly back into the journal-as-agent loop.

⭾end/design

**Next concrete action**: Prototype the first native node + pybind11 bindings + updated shim that can call it, then run an end-to-end benchmark inside the t451 / journal_as_agent_mvp framework.