<script lang="ts">
  import AgentCard from './components/AgentCard.svelte';
  import MemoryChart from './components/MemoryChart.svelte';
  import AgentFlow from './components/AgentFlow.svelte';
  import LogViewer from './components/LogViewer.svelte';

  interface Agent {
    id: string;
    name: string;
    status: 'running' | 'idle' | 'completed' | 'error';
    memory: number;
    tokensUsed: number;
  }

  let agents: Agent[] = [
    { id: '1', name: 'TradingAgent-1', status: 'running', memory: 65, tokensUsed: 1250 },
    { id: '2', name: 'AnalysisAgent-2', status: 'running', memory: 42, tokensUsed: 890 },
    { id: '3', name: 'PenTestAgent-3', status: 'idle', memory: 28, tokensUsed: 450 },
    { id: '4', name: 'OptimizeAgent-4', status: 'completed', memory: 0, tokensUsed: 2100 }
  ];

  let logs = [
    '[12:34:56] TradingAgent-1: Market analysis started',
    '[12:34:58] AnalysisAgent-2: Processing financial data',
    '[12:35:02] TradingAgent-1: Generated 3 trading signals',
    '[12:35:05] AnalysisAgent-2: Confidence score: 0.87',
    '[12:35:10] PenTestAgent-3: Waiting for input',
    '[12:35:15] OptimizeAgent-4: Completed optimization cycle'
  ];

  let darkMode = true;

  $: statusColor = (status: string) => {
    switch(status) {
      case 'running': return '#10b981';
      case 'idle': return '#8b5cf6';
      case 'completed': return '#3b82f6';
      case 'error': return '#ef4444';
      default: return '#6b7280';
    }
  };
</script>

<main class:dark={darkMode}>
  <header>
    <h1>🤖 AgentMonitor</h1>
    <button on:click={() => darkMode = !darkMode} class="theme-toggle">
      {darkMode ? '☀️' : '🌙'}
    </button>
  </header>

  <div class="container">
    <section class="agents-grid">
      <h2>Active Agents</h2>
      <div class="grid">
        {#each agents as agent (agent.id)}
          <AgentCard {agent} {statusColor} />
        {/each}
      </div>
    </section>

    <section class="metrics">
      <h2>Performance Metrics</h2>
      <div class="metrics-grid">
        <MemoryChart {agents} />
      </div>
    </section>

    <section class="flow">
      <h2>Agent Interaction Flow</h2>
      <AgentFlow {agents} />
    </section>

    <section class="logs">
      <h2>Real-time Logs</h2>
      <LogViewer {logs} />
    </section>
  </div>
</main>

<style>
  :global(*) {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  :global(body) {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    transition: background-color 0.3s, color 0.3s;
  }

  main {
    background-color: #f9fafb;
    color: #111827;
    min-height: 100vh;
    padding-bottom: 2rem;
  }

  main.dark {
    background-color: #0f172a;
    color: #f1f5f9;
  }

  header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
  }

  header h1 {
    font-size: 2rem;
    font-weight: 700;
  }

  .theme-toggle {
    background: rgba(255,255,255,0.2);
    border: none;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    cursor: pointer;
    font-size: 1.2rem;
    transition: background 0.3s;
  }

  .theme-toggle:hover {
    background: rgba(255,255,255,0.3);
  }

  .container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem;
  }

  section {
    margin-bottom: 3rem;
  }

  h2 {
    font-size: 1.5rem;
    margin-bottom: 1rem;
    font-weight: 600;
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
  }

  .agents-grid, .metrics {
    background: white;
    padding: 2rem;
    border-radius: 1rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  }

  main.dark .agents-grid,
  main.dark .metrics,
  main.dark section {
    background: #1e293b;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
  }

  .metrics-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 2rem;
  }

  .flow, .logs {
    background: white;
    padding: 2rem;
    border-radius: 1rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  }

  @media (max-width: 768px) {
    header {
      flex-direction: column;
      gap: 1rem;
      text-align: center;
    }

    header h1 {
      font-size: 1.5rem;
    }

    .container {
      padding: 1rem;
    }

    .grid {
      grid-template-columns: 1fr;
    }
  }
</style>
