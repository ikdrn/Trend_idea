import { Hono } from 'hono';
import { serve } from 'hono/node-server';
import Anthropic from '@anthropic-ai/sdk';

const app = new Hono();
const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY || 'test-key',
});

// Recent CVEs from March 2026 Patch Tuesday
const CVE_DATABASE = [
  {
    id: 'CVE-2026-26127',
    title: 'Microsoft Windows Print Queue RCE',
    product: 'Windows Print Spooler',
    severity: 'CRITICAL',
    cvss: 9.8,
    description: 'Remote Code Execution in Windows Print Queue',
    affected: 'Windows 10, 11, Server 2019/2022',
  },
  {
    id: 'CVE-2026-21262',
    title: 'Microsoft SQL Server Privilege Escalation',
    product: 'SQL Server',
    severity: 'CRITICAL',
    cvss: 9.1,
    description: 'Privilege escalation via SQL Server Agent',
    affected: 'SQL Server 2019-2022',
  },
  {
    id: 'CVE-2026-3909',
    title: 'Google Chrome Skia 2D Graphics Engine',
    product: 'Chrome',
    severity: 'HIGH',
    cvss: 8.8,
    description: 'Use-after-free in Skia 2D graphics library',
    affected: 'Chrome < 125.0.6422.60',
  },
  {
    id: 'CVE-2026-3910',
    title: 'Google Chrome V8 JavaScript Engine',
    product: 'Chrome',
    severity: 'CRITICAL',
    cvss: 9.6,
    description: 'Out-of-bounds memory access in V8 WASM engine',
    affected: 'Chrome < 125.0.6422.60',
  },
  {
    id: 'CVE-2026-28364',
    title: 'Apple macOS Kernel Integer Overflow',
    product: 'macOS',
    severity: 'HIGH',
    cvss: 8.2,
    description: 'Integer overflow in IOKit kernel extension',
    affected: 'macOS 12.x - 14.x',
  },
];

// Memory store for AI agent invocations
interface AgentMemory {
  invocation_count: number;
  total_tokens: number;
  last_analysis_time: string;
  analyses: Array<{
    cve_id: string;
    timestamp: string;
    thinking_process: string;
    recommendation: string;
  }>;
}

const agentMemory: AgentMemory = {
  invocation_count: 0,
  total_tokens: 0,
  last_analysis_time: new Date().toISOString(),
  analyses: [],
};

// HTML interface
const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>VulnWatch - AI Security Vulnerability Dashboard</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      padding: 20px;
    }
    .container {
      max-width: 1400px;
      margin: 0 auto;
    }
    header {
      background: rgba(255,255,255,0.95);
      padding: 30px;
      border-radius: 12px;
      margin-bottom: 30px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    h1 {
      color: #667eea;
      margin-bottom: 10px;
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .subtitle {
      color: #666;
      font-size: 14px;
    }
    .grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-bottom: 20px;
    }
    @media (max-width: 1024px) {
      .grid { grid-template-columns: 1fr; }
    }
    .card {
      background: rgba(255,255,255,0.95);
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    .card h2 {
      color: #333;
      font-size: 18px;
      margin-bottom: 15px;
      border-bottom: 2px solid #667eea;
      padding-bottom: 10px;
    }
    .stat-box {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 15px;
      margin-bottom: 20px;
    }
    .stat {
      background: #f8f9fa;
      padding: 15px;
      border-radius: 8px;
      text-align: center;
    }
    .stat-value {
      font-size: 24px;
      font-weight: bold;
      color: #667eea;
    }
    .stat-label {
      font-size: 12px;
      color: #999;
      margin-top: 5px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 15px;
    }
    th {
      background: #f8f9fa;
      padding: 12px;
      text-align: left;
      font-weight: 600;
      color: #333;
      border-bottom: 2px solid #e0e0e0;
      font-size: 13px;
    }
    td {
      padding: 12px;
      border-bottom: 1px solid #e0e0e0;
      font-size: 13px;
    }
    tr:hover {
      background: #fafafa;
    }
    .severity {
      display: inline-block;
      padding: 4px 8px;
      border-radius: 4px;
      font-weight: 600;
      font-size: 11px;
    }
    .severity.CRITICAL {
      background: #fee;
      color: #c00;
    }
    .severity.HIGH {
      background: #ffe;
      color: #990;
    }
    .severity.MEDIUM {
      background: #efd;
      color: #660;
    }
    button {
      background: #667eea;
      color: white;
      border: none;
      padding: 8px 12px;
      border-radius: 4px;
      cursor: pointer;
      font-size: 12px;
      margin-top: 10px;
      transition: background 0.2s;
    }
    button:hover {
      background: #5568d3;
    }
    .loading {
      color: #667eea;
      font-style: italic;
    }
    .analysis {
      background: #f0f4ff;
      padding: 12px;
      border-radius: 6px;
      margin-top: 10px;
      border-left: 3px solid #667eea;
      font-size: 12px;
      line-height: 1.5;
      color: #333;
    }
    .thinking {
      color: #999;
      font-style: italic;
      font-size: 11px;
      margin-top: 5px;
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>🛡️ VulnWatch</h1>
      <p class="subtitle">AI-Driven Security Vulnerability Dashboard - Real-time CVE Analysis with Claude AI Agent</p>
    </header>

    <div class="grid">
      <div class="card">
        <h2>📊 Vulnerability Overview</h2>
        <div class="stat-box">
          <div class="stat">
            <div class="stat-value" id="total-cves">0</div>
            <div class="stat-label">Total CVEs</div>
          </div>
          <div class="stat">
            <div class="stat-value" id="critical-count">0</div>
            <div class="stat-label">Critical</div>
          </div>
          <div class="stat">
            <div class="stat-value" id="high-count">0</div>
            <div class="stat-label">High</div>
          </div>
        </div>
        <table>
          <thead>
            <tr>
              <th>CVE ID</th>
              <th>Product</th>
              <th>Severity</th>
              <th>CVSS</th>
            </tr>
          </thead>
          <tbody id="cve-table">
          </tbody>
        </table>
      </div>

      <div class="card">
        <h2>🤖 AI Agent Memory</h2>
        <div class="stat-box">
          <div class="stat">
            <div class="stat-value" id="invocation-count">0</div>
            <div class="stat-label">Invocations</div>
          </div>
          <div class="stat">
            <div class="stat-value" id="token-count">0</div>
            <div class="stat-label">Tokens Used</div>
          </div>
          <div class="stat">
            <div class="stat-value" id="analysis-count">0</div>
            <div class="stat-label">Analyses</div>
          </div>
        </div>
        <button onclick="analyzeAll()">🔍 Analyze All CVEs</button>
        <div id="memory-log" style="margin-top: 15px; max-height: 300px; overflow-y: auto;">
          <p class="thinking">Agent memory will appear here...</p>
        </div>
      </div>
    </div>

    <div class="card">
      <h2>🔬 Detailed Analysis Results</h2>
      <table>
        <thead>
          <tr>
            <th>CVE ID</th>
            <th>AI Analysis & Recommendation</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody id="analysis-table">
        </tbody>
      </table>
    </div>
  </div>

  <script>
    const API_URL = '/api';

    async function loadCVEs() {
      try {
        const response = await fetch(API_URL + '/cves');
        const cves = await response.json();

        // Update stats
        document.getElementById('total-cves').textContent = cves.length;
        document.getElementById('critical-count').textContent = cves.filter(c => c.severity === 'CRITICAL').length;
        document.getElementById('high-count').textContent = cves.filter(c => c.severity === 'HIGH').length;

        // Populate CVE table
        const tbody = document.getElementById('cve-table');
        tbody.innerHTML = cves.map(cve => \`
          <tr>
            <td><strong>\${cve.id}</strong></td>
            <td>\${cve.product}</td>
            <td><span class="severity \${cve.severity}">\${cve.severity}</span></td>
            <td>\${cve.cvss}</td>
          </tr>
        \`).join('');
      } catch (error) {
        console.error('Error loading CVEs:', error);
      }
    }

    async function analyzeAll() {
      try {
        document.getElementById('memory-log').innerHTML = '<p class="loading">🤔 Claude AI is analyzing vulnerabilities...</p>';
        document.getElementById('analysis-table').innerHTML = '<tr><td colspan="3" class="loading">Analyzing...</td></tr>';

        const response = await fetch(API_URL + '/analyze-all', { method: 'POST' });
        const data = await response.json();

        // Update agent memory
        document.getElementById('invocation-count').textContent = data.memory.invocation_count;
        document.getElementById('token-count').textContent = data.memory.total_tokens;
        document.getElementById('analysis-count').textContent = data.memory.analyses.length;

        // Render memory log
        const memoryHTML = data.memory.analyses.map(a => \`
          <div class="analysis">
            <strong>\${a.cve_id}</strong>
            <div class="thinking">\${a.thinking_process}</div>
            <p style="margin-top: 8px;">\${a.recommendation}</p>
          </div>
        \`).join('');
        document.getElementById('memory-log').innerHTML = memoryHTML || '<p class="thinking">No analyses yet</p>';

        // Render analysis results
        const analysisHTML = data.analyses.map(a => \`
          <tr>
            <td><strong>\${a.cve_id}</strong></td>
            <td><div class="analysis">\${a.recommendation}</div></td>
            <td><button onclick="alert('Priority: \${a.priority}\\n\\n\${a.recommendation}')">Details</button></td>
          </tr>
        \`).join('');
        document.getElementById('analysis-table').innerHTML = analysisHTML;
      } catch (error) {
        console.error('Error analyzing CVEs:', error);
        document.getElementById('analysis-table').innerHTML = '<tr><td colspan="3" style="color: red;">Error: ' + error.message + '</td></tr>';
      }
    }

    // Load on page load
    loadCVEs();
  </script>
</body>
</html>`;

// Routes
app.get('/', (c) => c.html(html));

app.get('/api/cves', (c) => {
  return c.json(CVE_DATABASE);
});

app.post('/api/analyze-all', async (c) => {
  agentMemory.invocation_count++;
  agentMemory.last_analysis_time = new Date().toISOString();

  const analyses: Array<{
    cve_id: string;
    priority: string;
    recommendation: string;
  }> = [];

  for (const cve of CVE_DATABASE) {
    try {
      const response = await client.messages.create({
        model: 'claude-opus-4-6',
        max_tokens: 300,
        messages: [
          {
            role: 'user',
            content: `As a security expert, analyze this CVE and provide a priority level and brief mitigation recommendation:
CVE: ${cve.id}
Title: ${cve.title}
Severity: ${cve.severity}
CVSS Score: ${cve.cvss}
Description: ${cve.description}
Affected: ${cve.affected}

Respond with:
1. Priority: IMMEDIATE / HIGH / MEDIUM
2. Recommendation: (1-2 sentence mitigation advice)`,
          },
        ],
      });

      const text = response.content[0].type === 'text' ? response.content[0].text : '';
      const thinking = `Analyzed ${cve.id}: CVSS ${cve.cvss} (${cve.severity})`;

      agentMemory.total_tokens += response.usage.input_tokens + response.usage.output_tokens;
      agentMemory.analyses.push({
        cve_id: cve.id,
        timestamp: new Date().toISOString(),
        thinking_process: thinking,
        recommendation: text.split('\n').slice(1).join('\n'),
      });

      analyses.push({
        cve_id: cve.id,
        priority: text.includes('IMMEDIATE') ? 'IMMEDIATE' : text.includes('HIGH') ? 'HIGH' : 'MEDIUM',
        recommendation: text,
      });
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      analyses.push({
        cve_id: cve.id,
        priority: 'ERROR',
        recommendation: `Analysis failed: ${errorMsg}. Using default priority: ${cve.severity}`,
      });
    }
  }

  return c.json({
    analyses,
    memory: agentMemory,
  });
});

const port = 3000;
console.log(`VulnWatch running at http://localhost:${port}`);

serve({ fetch: app.fetch, port });
