#!/usr/bin/env bun
/**
 * ai-red-lines v1.0 — AI Usage Policy Compliance Checker
 *
 * Inspired by Anthropic's "red lines" stance in the 2026-02-27 Pentagon dispute:
 *   - No AI in fully autonomous weapons
 *   - No AI for mass surveillance of civilians
 *
 * Usage:
 *   bun main.ts --demo
 *   bun main.ts [directory]
 *   bun main.ts --policy policy.json [directory]
 *   bun main.ts --json --demo
 *
 *   # or with Node.js + ts-node:
 *   npx ts-node main.ts --demo
 */

import { readdir, readFile } from "node:fs/promises";
import { join, extname, basename } from "node:path";

// ── Types ─────────────────────────────────────────────────────────────────────

type Severity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";

interface PolicyRule {
  id: string;
  description: string;
  severity: Severity;
  patterns: string[];
  note?: string;
}

interface Policy {
  name: string;
  version: string;
  rules: PolicyRule[];
}

interface Finding {
  file: string;
  line: number;
  col: number;
  ruleId: string;
  ruleSeverity: Severity;
  ruleDescription: string;
  matchedText: string;
}

interface ScanResult {
  policy: { name: string; version: string };
  scannedAt: string;
  files: string[];
  findings: Finding[];
  summary: {
    filesScanned: number;
    compliantFiles: number;
    totalFindings: number;
    bySeverity: Record<Severity, number>;
    passed: boolean;
  };
}

// ── ANSI helpers ──────────────────────────────────────────────────────────────

const isColorEnabled =
  !process.env.NO_COLOR &&
  (process.stdout as NodeJS.WriteStream).isTTY !== false;

function ansi(code: string, text: string): string {
  return isColorEnabled ? `\x1b[${code}m${text}\x1b[0m` : text;
}

const bold   = (s: string) => ansi("1", s);
const red    = (s: string) => ansi("31", s);
const yellow = (s: string) => ansi("33", s);
const green  = (s: string) => ansi("32", s);
const cyan   = (s: string) => ansi("36", s);
const gray   = (s: string) => ansi("90", s);

function severityColor(sev: Severity, text: string): string {
  switch (sev) {
    case "CRITICAL": return ansi("1;31", text);
    case "HIGH":     return ansi("33", text);
    case "MEDIUM":   return ansi("36", text);
    case "LOW":      return ansi("90", text);
  }
}

// ── Default policy (Anthropic-inspired red lines) ─────────────────────────────

const DEFAULT_POLICY: Policy = {
  name: "AI Usage Policy — Red Lines",
  version: "1.0",
  rules: [
    {
      id: "NO_AUTONOMOUS_WEAPONS",
      description: "AI models must not be used for fully autonomous weapons targeting",
      severity: "CRITICAL",
      patterns: [
        "autonom\\w*[_ ]?(weapon|target|kill|lethal|strike)",
        "(weapon|target|kill|lethal|strike)[_ ]?autonom",
        "autonomous[_ ]?targeting",
        "target[_ ]?selection[\\s\\S]{0,40}(claude|gpt|gemini|llama|mistral|ai)",
      ],
      note: "Ref: Anthropic red line — 'fully autonomous weapons' (2026-02-27)",
    },
    {
      id: "NO_MASS_SURVEILLANCE",
      description: "AI models must not power mass surveillance of civilians",
      severity: "CRITICAL",
      patterns: [
        "mass[_ ]?surveill",
        "bulk[_ ]?(monitor|surveill|track|collect)[\\s\\S]{0,40}(citizen|civilian|public|population)",
        "population[_ ]?track[\\s\\S]{0,40}(ai|claude|gpt|gemini)",
        "civil(ian)?[_ ]?monitor[\\s\\S]{0,40}autonom",
      ],
      note: "Ref: Anthropic red line — 'mass surveillance of Americans' (2026-02-27)",
    },
    {
      id: "NO_HARDCODED_AI_KEYS",
      description: "AI vendor API keys must not be hardcoded in source files",
      severity: "HIGH",
      patterns: [
        "sk-ant-api0[0-9]-[A-Za-z0-9_-]{20,}",
        "sk-proj-[A-Za-z0-9_-]{20,}",
        "AIza[A-Za-z0-9_-]{35}",
        "ANTHROPIC_API_KEY\\s*=\\s*['\"][A-Za-z0-9_-]{20,}['\"]",
        "OPENAI_API_KEY\\s*=\\s*['\"][A-Za-z0-9_-]{20,}['\"]",
      ],
      note: "Hardcoded keys are a supply-chain risk (ref: 3,000 Google API keys exposed, 2026-03-01)",
    },
    {
      id: "NO_UNREVIEWED_MODEL_EXECUTION",
      description: "High-stakes automated decisions must include a human review step",
      severity: "MEDIUM",
      patterns: [
        "autoApprove\\s*[=:]\\s*true",
        "skipHumanReview\\s*[=:]\\s*true",
        "humanInLoop\\s*[=:]\\s*false",
        "requiresApproval\\s*[=:]\\s*false",
        "bypassReview\\s*=",
      ],
      note: "Ref: OpenAI / Anthropic — no 'high-stakes automated decisions without human oversight'",
    },
    {
      id: "NO_PII_WITHOUT_CONSENT_FLAG",
      description: "Processing of PII through AI APIs requires an explicit consent flag",
      severity: "MEDIUM",
      patterns: [
        "sendPII\\s*[=:]\\s*true",
        "includePII\\s*[=:]\\s*true",
        "piiConsent\\s*[=:]\\s*false",
        "stripPII\\s*[=:]\\s*false",
      ],
      note: "Best practice: never send PII to external AI APIs without explicit consent tracking",
    },
  ],
};

// ── File walking ──────────────────────────────────────────────────────────────

const SCANNABLE_EXTENSIONS = new Set([
  ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
  ".py", ".rs", ".go", ".sh", ".bash",
  ".json", ".yaml", ".yml", ".env", ".toml",
]);

async function* walkDir(dir: string): AsyncGenerator<string> {
  const entries = await readdir(dir, { withFileTypes: true });
  for (const entry of entries) {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) {
      if (entry.name.startsWith(".") || entry.name === "node_modules") continue;
      yield* walkDir(path);
    } else if (entry.isFile()) {
      const ext = extname(entry.name);
      const name = basename(entry.name);
      if (SCANNABLE_EXTENSIONS.has(ext) || name.startsWith(".env")) {
        yield path;
      }
    }
  }
}

// ── Scanning ──────────────────────────────────────────────────────────────────

function scanContent(
  filePath: string,
  content: string,
  policy: Policy,
): Finding[] {
  const findings: Finding[] = [];
  const lines = content.split("\n");

  for (const rule of policy.rules) {
    for (const patternStr of rule.patterns) {
      for (let i = 0; i < lines.length; i++) {
        const re = new RegExp(patternStr, "gi");
        const match = re.exec(lines[i]);
        if (match) {
          const snippet =
            match[0].length > 60 ? match[0].slice(0, 57) + "..." : match[0];
          findings.push({
            file: filePath,
            line: i + 1,
            col: match.index + 1,
            ruleId: rule.id,
            ruleSeverity: rule.severity,
            ruleDescription: rule.description,
            matchedText: snippet,
          });
          break; // one finding per rule per line is enough
        }
      }
    }
  }
  return findings;
}

async function scanFile(filePath: string, policy: Policy): Promise<Finding[]> {
  try {
    const content = await readFile(filePath, "utf-8");
    return scanContent(filePath, content, policy);
  } catch {
    return [];
  }
}

// ── Demo samples ──────────────────────────────────────────────────────────────

const DEMO_SAMPLES: Array<{ name: string; content: string }> = [
  {
    name: "samples/risky_app.ts",
    content: `
import Anthropic from "@anthropic-ai/sdk";

// BAD: hardcoded key
const client = new Anthropic({ apiKey: "sk-ant-api03-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" });

const config = {
  autoApprove: true,          // BAD: no human review gate
  skipHumanReview: true,      // BAD: bypasses oversight
  model: "claude-opus-4-6",
};

// BAD: autonomous targeting with AI
async function autonomousTargeting(threatData: object) {
  const response = await client.messages.create({
    model: config.model,
    messages: [{ role: "user", content: JSON.stringify(threatData) }],
  });
  return response;
}

// BAD: mass civilian surveillance
async function bulkSurveillanceEndpoint(citizenIds: string[]) {
  const response = await client.messages.create({
    model: "claude-haiku-4-5",
    messages: [{ role: "user", content: citizenIds.join(",") }],
  });
  return response;
}
`,
  },
  {
    name: "samples/safe_app.ts",
    content: `
import Anthropic from "@anthropic-ai/sdk";

// GOOD: key from environment variable
const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

const config = {
  autoApprove: false,         // GOOD: human review required
  requiresApproval: true,     // GOOD: explicit approval gate
  humanInLoop: true,          // GOOD: human oversight enabled
  model: "claude-sonnet-4-6",
};

// GOOD: content moderation with human review
async function moderateContent(text: string): Promise<string> {
  const response = await client.messages.create({
    model: config.model,
    messages: [
      { role: "user", content: \`Review this for policy violations: \${text}\` },
    ],
    max_tokens: 512,
  });
  const suggestion = response.content[0].type === "text"
    ? response.content[0].text : "";
  // Human reviewer must approve before publishing
  console.log("Awaiting human review before any action is taken.");
  return suggestion;
}

// GOOD: code review assistant (clearly safe, low-stakes use case)
async function reviewCode(diff: string): Promise<string> {
  const response = await client.messages.create({
    model: config.model,
    messages: [{ role: "user", content: \`Review this diff:\\n\${diff}\` }],
    max_tokens: 1024,
  });
  return response.content[0].type === "text" ? response.content[0].text : "";
}
`,
  },
];

// ── Report rendering ──────────────────────────────────────────────────────────

const SEP = gray("─".repeat(68));

function printReport(result: ScanResult): void {
  const { policy, findings, summary } = result;

  console.log();
  console.log(
    bold("ai-red-lines v1.0") + gray(" — AI Usage Policy Compliance Checker")
  );
  console.log(
    gray('Inspired by: Anthropic "red lines" stance (2026-02-27 Pentagon dispute)')
  );
  console.log(
    `Policy: ${cyan(policy.name)} ${gray("v" + policy.version)}  ` +
      gray(`(${DEFAULT_POLICY.rules.length} rules loaded)`)
  );
  console.log(
    `Scanning: ${cyan(result.files.length + " file(s)")}  ` +
      gray(result.scannedAt)
  );

  // Group findings by file
  const byFile = new Map<string, Finding[]>();
  for (const f of findings) {
    if (!byFile.has(f.file)) byFile.set(f.file, []);
    byFile.get(f.file)!.push(f);
  }

  for (const file of result.files) {
    console.log();
    console.log(SEP);
    console.log(" " + bold("File: " + file));
    console.log(SEP);

    const fileFings = byFile.get(file);
    if (!fileFings || fileFings.length === 0) {
      console.log(green("  ✓ No policy violations found"));
    } else {
      for (const f of fileFings) {
        const sev = `[${f.ruleSeverity.padEnd(8)}]`;
        console.log(
          "  " +
            severityColor(f.ruleSeverity, sev) +
            " " +
            bold(f.ruleId) +
            gray(` — Line ${f.line}`)
        );
        console.log(gray("    → ") + f.ruleDescription);
        console.log(gray("    → Matched: ") + yellow(`"${f.matchedText}"`));
      }
    }
  }

  // Summary
  console.log();
  console.log(SEP);
  console.log(" " + bold("Summary"));
  console.log(SEP);
  console.log(`  Files scanned:   ${summary.filesScanned}`);
  console.log(
    `  Compliant files: ${summary.compliantFiles} / ${summary.filesScanned}`
  );
  const sevLine = [
    summary.bySeverity.CRITICAL > 0
      ? red(`${summary.bySeverity.CRITICAL} CRITICAL`)
      : null,
    summary.bySeverity.HIGH > 0
      ? yellow(`${summary.bySeverity.HIGH} HIGH`)
      : null,
    summary.bySeverity.MEDIUM > 0
      ? cyan(`${summary.bySeverity.MEDIUM} MEDIUM`)
      : null,
    summary.bySeverity.LOW > 0
      ? gray(`${summary.bySeverity.LOW} LOW`)
      : null,
  ]
    .filter(Boolean)
    .join(", ");
  console.log(
    `  Total findings:  ${summary.totalFindings}` +
      (sevLine ? "  " + sevLine : "")
  );
  console.log();
  if (summary.passed) {
    console.log(
      "  Result: " + green("✓ ALL CHECKS PASSED — policy compliant")
    );
  } else {
    console.log(
      "  Result: " + red("✗ POLICY VIOLATION DETECTED — review required")
    );
  }
  console.log();
}

// ── Main ──────────────────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  const demoMode  = args.includes("--demo");
  const jsonMode  = args.includes("--json");
  const policyIdx = args.indexOf("--policy");
  const policyPath = policyIdx !== -1 ? args[policyIdx + 1] : null;
  const scanDir = args.find(
    (a) => !a.startsWith("--") && a !== policyPath
  ) ?? ".";

  // Load policy
  let policy: Policy = DEFAULT_POLICY;
  if (policyPath) {
    try {
      const raw = await readFile(policyPath, "utf-8");
      policy = JSON.parse(raw) as Policy;
    } catch (e) {
      console.error(`Error loading policy from ${policyPath}:`, e);
      process.exit(1);
    }
  }

  let scannedFiles: Array<{ name: string; findings: Finding[] }>;

  if (demoMode) {
    scannedFiles = DEMO_SAMPLES.map((s) => ({
      name: s.name,
      findings: scanContent(s.name, s.content, policy),
    }));
  } else {
    const paths: string[] = [];
    try {
      for await (const p of walkDir(scanDir)) paths.push(p);
    } catch (e) {
      console.error(`Cannot read directory "${scanDir}":`, e);
      process.exit(1);
    }
    if (paths.length === 0) {
      console.error(`No scannable files found in "${scanDir}"`);
      process.exit(1);
    }
    const results = await Promise.all(
      paths.map(async (p) => ({
        name: p,
        findings: await scanFile(p, policy),
      }))
    );
    scannedFiles = results;
  }

  // Build result
  const allFindings = scannedFiles.flatMap((f) => f.findings);
  const filesWithViolation = new Set(allFindings.map((f) => f.file));
  const bySeverity: Record<Severity, number> = {
    CRITICAL: 0,
    HIGH: 0,
    MEDIUM: 0,
    LOW: 0,
  };
  for (const f of allFindings) bySeverity[f.ruleSeverity]++;

  const result: ScanResult = {
    policy: { name: policy.name, version: policy.version },
    scannedAt: new Date().toISOString(),
    files: scannedFiles.map((f) => f.name),
    findings: allFindings,
    summary: {
      filesScanned: scannedFiles.length,
      compliantFiles: scannedFiles.length - filesWithViolation.size,
      totalFindings: allFindings.length,
      bySeverity,
      passed: bySeverity.CRITICAL === 0 && bySeverity.HIGH === 0,
    },
  };

  if (jsonMode) {
    console.log(JSON.stringify(result, null, 2));
  } else {
    printReport(result);
  }

  if (!result.summary.passed) process.exit(1);
}

main();
