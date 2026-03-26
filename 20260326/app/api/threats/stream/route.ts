export async function GET() {
  const threats = [
    {
      id: 'threat-001',
      title: 'Trivy Supply Chain Attack (CanisterWorm)',
      severity: 'critical',
      cvss: 9.8,
      source: 'The Hacker News',
      timestamp: new Date(Date.now() - 60000).toISOString(),
    },
    {
      id: 'threat-002',
      title: 'Chrome 0-Day RCE Vulnerability',
      severity: 'critical',
      cvss: 9.6,
      source: 'Hacker News Weekly Recap',
      timestamp: new Date(Date.now() - 120000).toISOString(),
    },
    {
      id: 'threat-003',
      title: 'Router Botnet Campaign (149 incidents)',
      severity: 'high',
      cvss: 8.5,
      source: 'Krebs on Security',
      timestamp: new Date(Date.now() - 180000).toISOString(),
    },
    {
      id: 'threat-004',
      title: 'macOS DNS Configuration Bypass',
      severity: 'medium',
      cvss: 6.2,
      source: 'Apple Security',
      timestamp: new Date(Date.now() - 240000).toISOString(),
    },
    {
      id: 'threat-005',
      title: 'North Korean npm Package RAT Campaign',
      severity: 'high',
      cvss: 8.1,
      source: 'npm Security Advisory',
      timestamp: new Date(Date.now() - 300000).toISOString(),
    },
  ];

  return Response.json(threats);
}
