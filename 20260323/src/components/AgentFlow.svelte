<script lang="ts">
  import { onMount } from 'svelte';

  interface Agent {
    id: string;
    name: string;
    status: 'running' | 'idle' | 'completed' | 'error';
    memory: number;
    tokensUsed: number;
  }

  export let agents: Agent[];
  let canvasElement: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D;

  const statusColors = {
    running: '#10b981',
    idle: '#8b5cf6',
    completed: '#3b82f6',
    error: '#ef4444'
  };

  onMount(() => {
    ctx = canvasElement.getContext('2d')!;
    canvasElement.width = 600;
    canvasElement.height = 300;
    drawFlow();
  });

  function drawFlow() {
    const width = canvasElement.width;
    const height = canvasElement.height;

    // Clear canvas
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, width, height);

    // Draw title
    ctx.fillStyle = '#111827';
    ctx.font = 'bold 14px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Agent Interaction Flow', width / 2, 20);

    // Arrange agents in positions
    const positions = agents.map((_, idx) => ({
      x: 100 + (idx % 2) * 200,
      y: 80 + Math.floor(idx / 2) * 100
    }));

    // Draw connections
    ctx.strokeStyle = '#d1d5db';
    ctx.lineWidth = 2;
    for (let i = 0; i < positions.length - 1; i++) {
      const from = positions[i];
      const to = positions[i + 1];
      ctx.beginPath();
      ctx.moveTo(from.x + 40, from.y + 30);
      ctx.lineTo(to.x - 40, to.y - 30);
      ctx.stroke();

      // Draw arrow
      const angle = Math.atan2(to.y - from.y, to.x - from.x);
      const arrowX = to.x - 40;
      const arrowY = to.y - 30;
      ctx.fillStyle = '#d1d5db';
      ctx.beginPath();
      ctx.moveTo(arrowX, arrowY);
      ctx.lineTo(arrowX - 8 * Math.cos(angle - Math.PI / 6), arrowY - 8 * Math.sin(angle - Math.PI / 6));
      ctx.lineTo(arrowX - 8 * Math.cos(angle + Math.PI / 6), arrowY - 8 * Math.sin(angle + Math.PI / 6));
      ctx.closePath();
      ctx.fill();
    }

    // Draw agent nodes
    agents.forEach((agent, idx) => {
      const pos = positions[idx];
      const color = statusColors[agent.status];

      // Circle background
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, 30, 0, Math.PI * 2);
      ctx.fill();

      // Status icon
      ctx.fillStyle = 'white';
      ctx.font = 'bold 20px sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      const icon = agent.status === 'running' ? '▶' : agent.status === 'idle' ? '⏸' : '✓';
      ctx.fillText(icon, pos.x, pos.y);

      // Label
      ctx.fillStyle = '#111827';
      ctx.font = '11px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(agent.name.split('-')[0], pos.x, pos.y + 50);
    });
  }
</script>

<div class="flow-container">
  <canvas bind:this={canvasElement}></canvas>
  <div class="description">
    Sequential agent interaction pipeline showing data flow and execution status.
  </div>
</div>

<style>
  .flow-container {
    width: 100%;
    background: #fafbfc;
    border-radius: 0.5rem;
    padding: 1rem;
    border: 1px solid #e5e7eb;
  }

  canvas {
    width: 100%;
    height: auto;
  }

  .description {
    margin-top: 1rem;
    font-size: 0.85rem;
    color: #6b7280;
    text-align: center;
  }

  :global(.dark) .flow-container {
    background: #1e293b;
    border-color: #475569;
  }

  :global(.dark) .description {
    color: #94a3b8;
  }
</style>
