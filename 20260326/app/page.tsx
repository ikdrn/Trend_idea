'use client';

import { useEffect, useState } from 'react';
import styles from './page.module.css';

interface Threat {
  id: string;
  title: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  cvss: number;
  source: string;
  timestamp: string;
}

interface AgentTask {
  id: string;
  name: string;
  status: 'running' | 'completed' | 'failed';
  progress: number;
  timestamp: string;
}

export default function Dashboard() {
  const [threats, setThreats] = useState<Threat[]>([]);
  const [agents, setAgents] = useState<AgentTask[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [threatRes, agentRes] = await Promise.all([
          fetch('/api/threats/stream'),
          fetch('/api/agents/stream'),
        ]);

        if (threatRes.ok) {
          const threatData = await threatRes.json();
          setThreats(threatData);
        }
        if (agentRes.ok) {
          const agentData = await agentRes.json();
          setAgents(agentData);
        }
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();

    // Simulate real-time updates
    const threatInterval = setInterval(fetchData, 5000);
    return () => clearInterval(threatInterval);
  }, []);

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      critical: '#ff4444',
      high: '#ff8800',
      medium: '#ffbb33',
      low: '#00cc00',
    };
    return colors[severity] || '#999';
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      running: '#00bbff',
      completed: '#00cc00',
      failed: '#ff4444',
    };
    return colors[status] || '#999';
  };

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1>🛡️ SecurityPulse Dashboard</h1>
        <p>Real-time threat & AI agent monitoring</p>
      </header>

      <div style={styles.content}>
        {/* Threats Section */}
        <section style={styles.section}>
          <h2>🚨 Security Threats</h2>
          {loading ? (
            <p>Loading threat data...</p>
          ) : threats.length === 0 ? (
            <p>No threats detected</p>
          ) : (
            <div style={styles.grid}>
              {threats.map((threat) => (
                <div key={threat.id} style={styles.card}>
                  <div
                    style={{
                      ...styles.severityBadge,
                      backgroundColor: getSeverityColor(threat.severity),
                    }}
                  >
                    {threat.severity.toUpperCase()}
                  </div>
                  <h3>{threat.title}</h3>
                  <div style={styles.details}>
                    <p>
                      <strong>CVSS Score:</strong> {threat.cvss}
                    </p>
                    <p>
                      <strong>Source:</strong> {threat.source}
                    </p>
                    <p style={{ fontSize: '0.9em', color: '#666' }}>
                      {new Date(threat.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Agents Section */}
        <section style={styles.section}>
          <h2>🤖 AI Agent Tasks</h2>
          {loading ? (
            <p>Loading agent data...</p>
          ) : agents.length === 0 ? (
            <p>No agents running</p>
          ) : (
            <div style={styles.taskList}>
              {agents.map((agent) => (
                <div key={agent.id} style={styles.taskItem}>
                  <div style={styles.taskHeader}>
                    <h4>{agent.name}</h4>
                    <span
                      style={{
                        ...styles.statusBadge,
                        backgroundColor: getStatusColor(agent.status),
                      }}
                    >
                      {agent.status.toUpperCase()}
                    </span>
                  </div>
                  <div style={styles.progressBar}>
                    <div
                      style={{
                        ...styles.progressFill,
                        width: `${agent.progress}%`,
                      }}
                    />
                  </div>
                  <p style={{ fontSize: '0.85em', color: '#666', margin: '5px 0 0 0' }}>
                    {new Date(agent.timestamp).toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>

      <footer style={styles.footer}>
        <p>Last updated: {new Date().toLocaleString()}</p>
      </footer>
    </div>
  );
}

const moduleStyles = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#0f1419',
    color: '#fff',
    padding: '20px',
    fontFamily: 'system-ui, -apple-system, sans-serif',
  },
  header: {
    textAlign: 'center' as const,
    marginBottom: '40px',
    borderBottom: '2px solid #333',
    paddingBottom: '20px',
  },
  content: {
    maxWidth: '1200px',
    margin: '0 auto',
  },
  section: {
    marginBottom: '40px',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
    gap: '20px',
  },
  card: {
    backgroundColor: '#1a1f26',
    border: '1px solid #333',
    borderRadius: '8px',
    padding: '20px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
  },
  severityBadge: {
    display: 'inline-block',
    padding: '4px 12px',
    borderRadius: '4px',
    fontSize: '0.75em',
    fontWeight: 'bold',
    marginBottom: '10px',
    color: '#fff',
  },
  details: {
    marginTop: '12px',
    fontSize: '0.9em',
  },
  taskList: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '15px',
  },
  taskItem: {
    backgroundColor: '#1a1f26',
    border: '1px solid #333',
    borderRadius: '8px',
    padding: '15px',
  },
  taskHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '10px',
  },
  statusBadge: {
    padding: '4px 12px',
    borderRadius: '4px',
    fontSize: '0.75em',
    fontWeight: 'bold',
    color: '#fff',
  },
  progressBar: {
    width: '100%',
    height: '8px',
    backgroundColor: '#333',
    borderRadius: '4px',
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#00bbff',
    transition: 'width 0.3s ease',
  },
  footer: {
    textAlign: 'center' as const,
    marginTop: '60px',
    paddingTop: '20px',
    borderTop: '2px solid #333',
    color: '#888',
    fontSize: '0.9em',
  },
};

export { moduleStyles as styles };
