/// vulntriage — Multi-Agent CVE Triage System
///
/// Simulates a 3-agent pipeline (Analyzer / Scorer / Reporter) running in parallel
/// to triage CVEs from the March 7, 2026 security bulletins.
///
/// Language choice: Rust is trending on GitHub (nearai/ironclaw) and its ownership
/// model makes it ideal for safe, concurrent security tooling.
use std::sync::mpsc;
use std::thread;
use std::time::Instant;

// ── Data model ────────────────────────────────────────────────────────────────

#[derive(Debug, Clone)]
struct Cve {
    id: &'static str,
    cvss: f32,
    /// true = actively exploited in the wild
    exploited: bool,
    attack_vector: &'static str,
    /// "None" | "Low" | "High"
    auth_required: &'static str,
    component: &'static str,
    affected_systems: u32,
    description: &'static str,
}

#[derive(Debug, Clone)]
struct AnalyzedCve {
    cve: Cve,
    attack_surface: String,
}

#[derive(Debug, Clone)]
struct ScoredCve {
    analyzed: AnalyzedCve,
    risk_score: u32,
}

// ── Sample CVE data (from 2026-03-07 security bulletins) ─────────────────────

fn sample_cves() -> Vec<Cve> {
    vec![
        Cve {
            id: "CVE-2026-20127",
            cvss: 10.0,
            exploited: true,
            attack_vector: "Network",
            auth_required: "None",
            component: "Cisco SD-WAN Controller/Manager",
            affected_systems: 45_000,
            description: "Auth bypass — unauthenticated admin access (CISA ED 26-03)",
        },
        Cve {
            id: "CVE-2026-0006",
            cvss: 9.8,
            exploited: false,
            attack_vector: "Network",
            auth_required: "None",
            component: "Android System",
            affected_systems: 92_000,
            description: "RCE without user interaction or privileges",
        },
        Cve {
            id: "CVE-2026-21385",
            cvss: 7.8,
            exploited: true,
            attack_vector: "Local",
            auth_required: "None",
            component: "Qualcomm / Android",
            affected_systems: 31_000,
            description: "Under limited targeted exploitation (Qualcomm component)",
        },
        Cve {
            id: "CVE-2026-0037",
            cvss: 7.0,
            exploited: false,
            attack_vector: "Local",
            auth_required: "Low",
            component: "Android pKVM",
            affected_systems: 18_000,
            description: "Privilege escalation in Protected Kernel-Based VM subsystem",
        },
        Cve {
            id: "CVE-2026-0031",
            cvss: 6.5,
            exploited: false,
            attack_vector: "Local",
            auth_required: "Low",
            component: "Android pKVM",
            affected_systems: 18_000,
            description: "Privilege escalation in Protected Kernel-Based VM subsystem",
        },
    ]
}

// ── Agent: Analyzer ───────────────────────────────────────────────────────────
// Parses raw CVE data and enriches it with an "attack surface" label.

fn agent_analyzer(cves: Vec<Cve>, tx: mpsc::Sender<AnalyzedCve>) {
    for cve in cves {
        let surface = match (cve.attack_vector, cve.auth_required) {
            ("Network", "None") => "Internet-exposed, no auth required",
            ("Network", _) => "Internet-exposed, credentials needed",
            ("Local", "None") => "Local access, no privileges needed",
            ("Local", _) => "Local access, user-level privileges",
            _ => "Unknown surface",
        }
        .to_string();

        println!(
            "[Analyzer]  {} | Vector: {:<7} | Auth: {:<4} | Component: {} | Surface: {}",
            cve.id, cve.attack_vector, cve.auth_required, cve.component, surface
        );

        tx.send(AnalyzedCve {
            cve,
            attack_surface: surface,
        })
        .unwrap();
    }
}

// ── Agent: Scorer ─────────────────────────────────────────────────────────────
// Calculates a composite risk score:
//   base  = CVSS * 8          (0..80)
//   bonus = 15 if exploited   (actively exploited in the wild)
//   bonus += scale factor from affected system count (0..5)

fn agent_scorer(rx: mpsc::Receiver<AnalyzedCve>, tx: mpsc::Sender<ScoredCve>) {
    let mut buffer: Vec<AnalyzedCve> = rx.iter().collect();

    // Sort by CVSS descending before scoring to produce a stable order
    buffer.sort_by(|a, b| {
        b.cve
            .cvss
            .partial_cmp(&a.cve.cvss)
            .unwrap_or(std::cmp::Ordering::Equal)
    });

    for analyzed in buffer {
        let base = (analyzed.cve.cvss * 8.0) as u32;
        let exploit_bonus: u32 = if analyzed.cve.exploited { 15 } else { 0 };
        let scale_bonus = (analyzed.cve.affected_systems / 20_000).min(5) as u32;
        let risk_score = (base + exploit_bonus + scale_bonus).min(100);

        println!(
            "[Scorer]    {} | CVSS:{:4.1} | Exploited:{} | Affected:{:6} | RiskScore:{:3} | {}",
            analyzed.cve.id,
            analyzed.cve.cvss,
            if analyzed.cve.exploited { "YES" } else { "NO " },
            analyzed.cve.affected_systems,
            risk_score,
            analyzed.attack_surface
        );

        tx.send(ScoredCve {
            analyzed,
            risk_score,
        })
        .unwrap();
    }
}

// ── Agent: Reporter ───────────────────────────────────────────────────────────
// Sorts scored CVEs and emits a prioritised triage report.

fn agent_reporter(rx: mpsc::Receiver<ScoredCve>, date: &str) {
    let mut scored: Vec<ScoredCve> = rx.iter().collect();
    scored.sort_by(|a, b| b.risk_score.cmp(&a.risk_score));

    let (critical, rest): (Vec<_>, Vec<_>) = scored.iter().partition(|s| s.risk_score >= 90);
    let (high, medium): (Vec<&&ScoredCve>, Vec<&&ScoredCve>) = rest.iter().partition(|s| s.risk_score >= 70);

    println!();
    println!("=== [Reporter] Triage Report {} ===", date);
    println!();

    println!("CRITICAL (RiskScore >= 90):");
    if critical.is_empty() {
        println!("  (none)");
    }
    for s in &critical {
        println!(
            "  [!!!] {} | CVSS={:4.1} | {} — {}",
            s.analyzed.cve.id,
            s.analyzed.cve.cvss,
            s.analyzed.cve.component,
            s.analyzed.cve.description
        );
    }

    println!();
    println!("HIGH (RiskScore 70-89):");
    if high.is_empty() {
        println!("  (none)");
    }
    for s in &high {
        println!(
            "  [!]   {} | CVSS={:4.1} | {} — {}",
            s.analyzed.cve.id,
            s.analyzed.cve.cvss,
            s.analyzed.cve.component,
            s.analyzed.cve.description
        );
    }

    println!();
    println!("MEDIUM (RiskScore < 70):");
    if medium.is_empty() {
        println!("  (none)");
    }
    for s in &medium {
        println!(
            "  [ ]   {} | CVSS={:4.1} | {} — {}",
            s.analyzed.cve.id,
            s.analyzed.cve.cvss,
            s.analyzed.cve.component,
            s.analyzed.cve.description
        );
    }

    println!();
    println!(
        "Summary: {} CVEs | CRITICAL: {} | HIGH: {} | MEDIUM: {}",
        scored.len(),
        critical.len(),
        high.len(),
        medium.len()
    );
}

// ── Main ──────────────────────────────────────────────────────────────────────

fn main() {
    let start = Instant::now();
    let date = "2026-03-07";

    println!("=== VulnTriage — Multi-Agent CVE Triage System ===");
    println!("Date: {}", date);
    println!();

    let cves = sample_cves();

    // Channel: Analyzer -> Scorer
    let (tx_analyzed, rx_analyzed) = mpsc::channel::<AnalyzedCve>();
    // Channel: Scorer   -> Reporter
    let (tx_scored, rx_scored) = mpsc::channel::<ScoredCve>();

    // Spawn Analyzer agent thread
    let analyzer_handle = thread::spawn(move || {
        agent_analyzer(cves, tx_analyzed);
    });

    // Spawn Scorer agent thread
    let scorer_handle = thread::spawn(move || {
        agent_scorer(rx_analyzed, tx_scored);
    });

    // Reporter runs on main thread after both pipeline stages complete
    analyzer_handle.join().unwrap();
    scorer_handle.join().unwrap();

    agent_reporter(rx_scored, date);

    let elapsed = start.elapsed();
    println!(
        "Triage completed in {}ms (3 agents, parallel pipeline)",
        elapsed.as_millis()
    );
}
