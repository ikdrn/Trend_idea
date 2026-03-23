<script lang="ts">
  interface Agent {
    id: string;
    name: string;
    status: 'running' | 'idle' | 'completed' | 'error';
    memory: number;
    tokensUsed: number;
  }

  export let agent: Agent;
  export let statusColor: (status: string) => string;

  const statusLabel = {
    running: 'Running',
    idle: 'Idle',
    completed: 'Completed',
    error: 'Error'
  };
</script>

<div class="card" style="border-left: 4px solid {statusColor(agent.status)}">
  <div class="header">
    <h3>{agent.name}</h3>
    <span class="status" style="background-color: {statusColor(agent.status)}">
      {statusLabel[agent.status]}
    </span>
  </div>
  <div class="content">
    <div class="metric">
      <span class="label">Memory:</span>
      <span class="value">{agent.memory}%</span>
    </div>
    <div class="metric">
      <span class="label">Tokens:</span>
      <span class="value">{agent.tokensUsed}</span>
    </div>
  </div>
</div>

<style>
  .card {
    background: white;
    border-radius: 0.75rem;
    padding: 1.5rem;
    transition: transform 0.2s, box-shadow 0.2s;
  }

  .card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.1);
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  h3 {
    font-size: 1rem;
    font-weight: 600;
    margin: 0;
  }

  .status {
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    font-weight: 600;
  }

  .content {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .metric {
    display: flex;
    justify-content: space-between;
    font-size: 0.9rem;
  }

  .label {
    color: #6b7280;
    font-weight: 500;
  }

  .value {
    color: #111827;
    font-weight: 700;
  }

  :global(.dark) .card {
    background: #334155;
  }

  :global(.dark) .label {
    color: #94a3b8;
  }

  :global(.dark) .value {
    color: #f1f5f9;
  }
</style>
