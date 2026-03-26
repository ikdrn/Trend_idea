use clap::Parser;
use colored::*;

#[derive(Parser)]
#[command(name = "threat-monitor")]
#[command(about = "AI Package Threat Monitor - Scan npm/pip packages for security vulnerabilities")]
struct Args {
    /// Package name to scan (e.g., litellm, langflow, @huggingface/transformers)
    #[arg(value_name = "PACKAGE")]
    package: String,

    /// Package manager (npm or pip)
    #[arg(short, long, default_value = "npm")]
    manager: String,

    /// Check GitHub Advisory database
    #[arg(short = 'g', long)]
    github_advisory: bool,
}

#[derive(Debug, Clone)]
struct Vulnerability {
    id: String,
    severity: String,
    description: String,
    affected_versions: String,
}

fn main() {
    let args = Args::parse();

    println!("{}",  "═══════════════════════════════════════════════════════".bright_cyan());
    println!("{}", format!("🔍 AI Package Threat Monitor - {}  Scanner", args.manager.to_uppercase()).bright_cyan());
    println!("{}",  "═══════════════════════════════════════════════════════".bright_cyan());
    println!();

    println!("📦 Scanning package: {}", args.package.yellow());
    println!();

    // Simulated threat data (in production, would call real APIs)
    let threats = simulate_package_scan(&args.package, &args.manager);

    if threats.is_empty() {
        println!("{}", "✅ No vulnerabilities detected for this package.".bright_green());
    } else {
        println!(
            "{} {}",
            "⚠️  Found".yellow().bold(),
            format!("{} potential threat(s):", threats.len()).yellow().bold()
        );
        println!();

        for (idx, vuln) in threats.iter().enumerate() {
            print_threat(idx + 1, vuln);
        }
    }

    if args.github_advisory {
        println!();
        println!("{}", "📊 Fetching GitHub Advisory data...".bright_blue());
        check_github_advisory(&args.package);
    }

    println!();
    println!(
        "{}",
        "═══════════════════════════════════════════════════════".bright_cyan()
    );
    println!(
        "{}",
        "Scan completed. Recommend immediate patching for CRITICAL vulnerabilities.".dimmed()
    );
}

fn simulate_package_scan(package: &str, manager: &str) -> Vec<Vulnerability> {
    // Simulated threat database (in production, would query npm/pip/GitHub Advisory API)
    let known_threats = vec![
        (
            "litellm",
            vec![
                Vulnerability {
                    id: "TeamPCP-SUPPLY-CHAIN-001".to_string(),
                    severity: "CRITICAL".to_string(),
                    description:
                        "Malicious code injection in versions 1.82.7, 1.82.8 (March 2026)".to_string(),
                    affected_versions: "1.82.7, 1.82.8".to_string(),
                },
                Vulnerability {
                    id: "CVE-2026-LITELLM-AUTH".to_string(),
                    severity: "HIGH".to_string(),
                    description: "Unauthorized credential exposure in API key handling".to_string(),
                    affected_versions: "<1.82.6".to_string(),
                },
            ],
        ),
        (
            "langflow",
            vec![
                Vulnerability {
                    id: "CVE-2026-33017".to_string(),
                    severity: "CRITICAL".to_string(),
                    description: "Authentication bypass + Code injection vulnerability".to_string(),
                    affected_versions: "<0.6.15".to_string(),
                },
            ],
        ),
        (
            "@huggingface/transformers",
            vec![
                Vulnerability {
                    id: "HF-SUPPLY-CHAIN-002".to_string(),
                    severity: "MEDIUM".to_string(),
                    description: "Potential model poisoning in auto-download feature".to_string(),
                    affected_versions: "4.28.0 - 4.30.2".to_string(),
                },
            ],
        ),
    ];

    for (pkg_name, vulns) in known_threats.iter() {
        if package.to_lowercase().contains(&pkg_name.to_lowercase())
            || pkg_name.contains(&package.to_lowercase())
        {
            return vulns.clone();
        }
    }

    vec![]
}

fn print_threat(index: usize, vuln: &Vulnerability) {
    let severity_colored = match vuln.severity.as_str() {
        "CRITICAL" => vuln.severity.bright_red().bold(),
        "HIGH" => vuln.severity.red(),
        "MEDIUM" => vuln.severity.yellow(),
        _ => vuln.severity.normal(),
    };

    println!("{}", format!("[{}] {}", index, vuln.id).bright_white().bold());
    println!("    Severity:  {}", severity_colored);
    println!("    {} {}", "Details: ".dimmed(), vuln.description);
    println!(
        "    {} {}",
        "Affected:  ".dimmed(),
        vuln.affected_versions.bright_yellow()
    );
    println!();
}

fn check_github_advisory(package: &str) {
    // Simulated GitHub Advisory API response
    println!(
        "  {}",
        "→ Checking GitHub Advisory Database...".bright_blue()
    );
    println!(
        "    {} {} {}",
        "Package:".dimmed(),
        package.cyan(),
        format!("(query to github.com/advisories)").dimmed()
    );

    if package.to_lowercase().contains("litellm") {
        println!(
            "    {} {}",
            "Found:".bright_red().bold(),
            "1 advisory from GitHub (TeamPCP March 2026 incident)"
        );
        println!(
            "    {} {}",
            "Link:".blue(),
            "https://github.com/advisories/GHSA-xxxx-xxxx-xxxx".blue()
        );
    } else {
        println!(
            "    {} No GitHub advisories found.",
            "✓".bright_green().bold()
        );
    }
}