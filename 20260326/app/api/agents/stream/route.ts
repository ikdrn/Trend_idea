export async function GET() {
  const agents = [
    {
      id: 'agent-001',
      name: 'Threat Intelligence Aggregator',
      status: 'running',
      progress: 75,
      timestamp: new Date(Date.now() - 30000).toISOString(),
    },
    {
      id: 'agent-002',
      name: 'npm Package Vulnerability Scanner',
      status: 'completed',
      progress: 100,
      timestamp: new Date(Date.now() - 60000).toISOString(),
    },
    {
      id: 'agent-003',
      name: 'CVE Correlation Analyzer',
      status: 'running',
      progress: 45,
      timestamp: new Date(Date.now() - 20000).toISOString(),
    },
    {
      id: 'agent-004',
      name: 'Automated Response Executor',
      status: 'completed',
      progress: 100,
      timestamp: new Date(Date.now() - 120000).toISOString(),
    },
    {
      id: 'agent-005',
      name: 'Supply Chain Risk Assessor',
      status: 'running',
      progress: 60,
      timestamp: new Date(Date.now() - 15000).toISOString(),
    },
  ];

  return Response.json(agents);
}
