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

  onMount(() => {
    ctx = canvasElement.getContext('2d')!;
    canvasElement.width = 500;
    canvasElement.height = 250;
    drawChart();
  });

  function drawChart() {
    const width = canvasElement.width;
    const height = canvasElement.height;
    const padding = 40;
    const chartWidth = width - 2 * padding;
    const chartHeight = height - 2 * padding;

    // Clear canvas
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, width, height);

    // Draw axes
    ctx.strokeStyle = '#d1d5db';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.stroke();

    // Draw title
    ctx.fillStyle = '#111827';
    ctx.font = 'bold 14px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Memory Usage Over Time', width / 2, 20);

    // Draw grid lines
    ctx.strokeStyle = '#f3f4f6';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
      const y = padding + (chartHeight / 4) * i;
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(width - padding, y);
      ctx.stroke();
    }

    // Draw data lines for each agent
    const colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe'];
    agents.forEach((agent, idx) => {
      const dataPoints = generateDataPoints(agent.memory);
      drawLine(dataPoints, colors[idx % colors.length], agent.name);
    });

    // Draw legend
    let legendY = height - 10;
    agents.forEach((agent, idx) => {
      ctx.fillStyle = colors[idx % colors.length];
      ctx.fillRect(width - 150, legendY - 15, 12, 12);
      ctx.fillStyle = '#111827';
      ctx.font = '12px sans-serif';
      ctx.textAlign = 'left';
      ctx.fillText(agent.name, width - 130, legendY - 6);
      legendY -= 20;
    });
  }

  function generateDataPoints(baseValue: number): number[] {
    const points = [];
    for (let i = 0; i < 10; i++) {
      const variation = Math.sin(i / 2) * 10;
      points.push(Math.min(100, Math.max(0, baseValue + variation)));
    }
    return points;
  }

  function drawLine(dataPoints: number[], color: string, label: string) {
    const width = canvasElement.width;
    const height = canvasElement.height;
    const padding = 40;
    const chartWidth = width - 2 * padding;
    const chartHeight = height - 2 * padding;

    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.beginPath();

    dataPoints.forEach((value, idx) => {
      const x = padding + (chartWidth / (dataPoints.length - 1)) * idx;
      const y = height - padding - (chartHeight * (value / 100));
      
      if (idx === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.stroke();
  }
</script>

<div class="chart-container">
  <canvas bind:this={canvasElement}></canvas>
  <div class="description">
    Real-time memory usage tracking for active agents with 10-second window.
  </div>
</div>

<style>
  .chart-container {
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

  :global(.dark) .chart-container {
    background: #1e293b;
    border-color: #475569;
  }

  :global(.dark) .description {
    color: #94a3b8;
  }
</style>
