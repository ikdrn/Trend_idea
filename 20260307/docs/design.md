# vulntriage — Design Document

**Date**: 2026-03-07
**System**: Multi-Agent CVE Triage CLI
**Language**: Rust (rustc 1.93.1)
**Entry point**: `cargo run` (inside `src/vulntriage/`)

---

## Background & Motivation

Two dominant trends collided on 2026-03-07:

| Trend | Signal |
|-------|--------|
| Multi-agent AI orchestration | Windsurf Wave 13 parallel agents, Cursor 2.0 (8 agents), openai/symphony (Elixir), Apple Xcode 26.3 agentic coding |
| Security bulletin overload | Android 129 CVEs, Cisco CVSS 10.0 (CVE-2026-20127), Microsoft 59 CVEs |

The insight: security teams face the same "orchestration" problem that AI coding tools are solving — how do you coordinate multiple specialized workers across a large, parallelizable workload?
`vulntriage` simulates that answer using Rust threads + channels.

---

## Architecture

```
main()
  |
  +--[thread]--> Analyzer Agent
  |                  |
  |              mpsc::channel<AnalyzedCve>
  |                  |
  +--[thread]--> Scorer Agent
  |                  |
  |              mpsc::channel<ScoredCve>
  |                  |
  +-----------> Reporter Agent (main thread)
```

### Pipeline stages

#### 1. Analyzer Agent (`agent_analyzer`)
- Input: `Vec<Cve>` — raw CVE records
- Enriches each record with an `attack_surface` label derived from `attack_vector` × `auth_required`
- Sends `AnalyzedCve` to the next stage via `mpsc::Sender`

#### 2. Scorer Agent (`agent_scorer`)
- Input: `mpsc::Receiver<AnalyzedCve>`
- Computes a composite `risk_score` (0–100):

```
risk_score = min(100,
    floor(cvss * 8)               // CVSS weight: 0..80
  + (15 if exploited in wild)     // exploitation bonus
  + floor(affected_systems / 20000).clamp(0, 5)  // scale bonus
)
```

- Sorts by CVSS descending for consistent output ordering
- Sends `ScoredCve` to Reporter

#### 3. Reporter Agent (`agent_reporter`)
- Input: `mpsc::Receiver<ScoredCve>` (drained after Scorer thread joins)
- Classifies into tiers:
  - CRITICAL: `risk_score >= 90`
  - HIGH: `risk_score in [70, 90)`
  - MEDIUM: `risk_score < 70`
- Emits a structured plain-text report with actionable labels

---

## Data Model

```rust
struct Cve {
    id: &'static str,
    cvss: f32,
    exploited: bool,
    attack_vector: &'static str,   // "Network" | "Local"
    auth_required: &'static str,   // "None" | "Low" | "High"
    component: &'static str,
    affected_systems: u32,
    description: &'static str,
}

struct AnalyzedCve { cve: Cve, attack_surface: String }
struct ScoredCve   { analyzed: AnalyzedCve, risk_score: u32 }
```

---

## Sample CVE Dataset (2026-03-07)

| CVE ID | CVSS | Exploited | Source |
|--------|------|-----------|--------|
| CVE-2026-20127 | 10.0 | Yes | Cisco SD-WAN (CISA ED 26-03) |
| CVE-2026-0006 | 9.8 | No | Android System RCE |
| CVE-2026-21385 | 7.8 | Yes | Qualcomm / Android |
| CVE-2026-0037 | 7.0 | No | Android pKVM |
| CVE-2026-0031 | 6.5 | No | Android pKVM |

---

## Concurrency Model

- `std::thread::spawn` for Analyzer and Scorer — no external async runtime needed
- `std::sync::mpsc` channels for typed message passing between agents
- Reporter runs on the main thread after both worker threads join, eliminating the need for additional synchronization
- No `unsafe` code, no `Arc<Mutex<>>` — the pipeline topology naturally avoids data races

---

## Extension Points

| Feature | How to add |
|---------|------------|
| Real CVE feed | Replace `sample_cves()` with an NVD API call (`ureq` crate) |
| JSON output | Add a `--json` flag; serialize `ScoredCve` with `serde_json` |
| More agents | Add a "Remediation Advisor" stage between Scorer and Reporter |
| Parallel Analyzers | Use `rayon` crate for data-parallel analysis across large CVE sets |
| Custom thresholds | Accept `--critical` / `--high` score cutoffs as CLI args via `clap` |

---

## Rust Language Choice Rationale

- `nearai/ironclaw` (Rust, 4.3k★) is trending on GitHub today — security-focused Rust tooling is mainstream
- Ownership model prevents common security bugs (use-after-free, data races) by construction
- `std::sync::mpsc` provides typed, zero-copy message passing that maps cleanly to the "agent" metaphor
- Zero external dependencies: entire project compiles with `cargo build` and no network access
