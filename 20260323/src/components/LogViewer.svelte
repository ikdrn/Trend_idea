<script lang="ts">
  import { onMount } from 'svelte';

  export let logs: string[] = [];
  let logContainer: HTMLDivElement;

  $: if (logContainer) {
    logContainer.scrollTop = logContainer.scrollHeight;
  }

  function formatTimestamp(log: string): string {
    const match = log.match(/\[(\d{2}:\d{2}:\d{2})\]/);
    return match ? match[1] : '';
  }

  function formatMessage(log: string): string {
    return log.replace(/\[\d{2}:\d{2}:\d{2}\]\s*/, '');
  }

  function getLogLevel(log: string): string {
    if (log.includes('error') || log.includes('Error')) return 'error';
    if (log.includes('warning') || log.includes('Warning')) return 'warning';
    if (log.includes('started') || log.includes('Started')) return 'info';
    return 'log';
  }
</script>

<div class="log-viewer">
  <div class="log-container" bind:this={logContainer}>
    {#each logs as log (log)}
      <div class="log-entry" class:error={getLogLevel(log) === 'error'} class:warning={getLogLevel(log) === 'warning'} class:info={getLogLevel(log) === 'info'}>
        <span class="timestamp">{formatTimestamp(log)}</span>
        <span class="message">{formatMessage(log)}</span>
      </div>
    {/each}
  </div>
</div>

<style>
  .log-viewer {
    background: #1f2937;
    border-radius: 0.5rem;
    padding: 1rem;
    font-family: 'Courier New', monospace;
  }

  .log-container {
    height: 250px;
    overflow-y: auto;
    background: #111827;
    padding: 1rem;
    border-radius: 0.25rem;
  }

  .log-entry {
    color: #d1d5db;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
    display: flex;
    gap: 1rem;
  }

  .log-entry.info {
    color: #60a5fa;
  }

  .log-entry.warning {
    color: #fbbf24;
  }

  .log-entry.error {
    color: #f87171;
  }

  .timestamp {
    color: #9ca3af;
    flex-shrink: 0;
    font-weight: 600;
  }

  .message {
    flex: 1;
  }

  :global(.dark) .log-viewer {
    background: #0f172a;
  }

  :global(.dark) .log-container {
    background: #1e293b;
  }

  ::-webkit-scrollbar {
    width: 6px;
  }

  ::-webkit-scrollbar-track {
    background: #374151;
  }

  ::-webkit-scrollbar-thumb {
    background: #6b7280;
    border-radius: 3px;
  }

  ::-webkit-scrollbar-thumb:hover {
    background: #9ca3af;
  }
</style>
